"""Reviewed claim evidence cannot be crowded out by other rows in its own topic."""
import copy
import pytest

from backend.bintanong_retrieval.candidate_claims import prepare_candidate_claim_reviews
from backend.bintanong_retrieval.candidate_subject import prepare_candidate_subject_catalogue
from backend.bintanong_retrieval.engine import RetrievalEngine
from backend.bintanong_retrieval.evidence_policy import SourceAwareEvidencePolicy
from backend.bintanong_retrieval.query import configuration_identity
from backend.bintanong_retrieval.types import RetrievalRequest,RetrievalSettings
from backend.bintanong_runtime.package_storage import PackageStorage
from tests.test_retrieval_engine import Encoder
from tests.test_retrieval_evidence_policy import policy_fixture


def fixture(conflict=None):
    inputs, rows = policy_fixture()
    if conflict == 'edition':
        row = rows[2]
        row['chunk'].update(version_id='version-other',byte_sha256='9'*64)
        row['version'].update(version_id='version-other',byte_sha256='9'*64)
        row['spans'][0].update(version_id='version-other',byte_sha256='9'*64)
    elif conflict == 'curriculum':
        for row in rows:
            row['chunk']['scope'].append('curriculum:second' if row is rows[2] else 'curriculum:first')
    inputs['chunks'] = [copy.deepcopy(r['chunk']) | {'spans':copy.deepcopy(r['spans'])} for r in rows]
    assignments = copy.deepcopy(inputs['catalogue']['assignments'])
    for assignment in assignments:
        assignment['subject_id'] = 'fees'
    catalogue = prepare_candidate_subject_catalogue(inputs['chunks'],assignments)
    reviews = copy.deepcopy(inputs['claim_reviews']['reviews'])
    for review in reviews:
        review['reviewed_chunk_ids'] = ['a','b','other']
    inputs.update(catalogue=catalogue,
        claim_reviews=prepare_candidate_claim_reviews(catalogue,inputs['chunks'],reviews))
    encoder = Encoder()
    encoder.count_context_tokens = lambda text:3000 if 'Synthetic amount other' in text else 1000
    vectors = {c['chunk_id']:[1.0]+[0.0]*1023 for c in inputs['chunks']}
    storage = PackageStorage(release_id='release-test',
        manifest=dict(embedding_set_id='set',**configuration_identity(encoder.config)),
        chunks=inputs['chunks'],versions={r['chunk']['version_id']:r['version'] for r in rows},vectors=vectors)
    policy = SourceAwareEvidencePolicy(**inputs)
    engine = RetrievalEngine(storage,encoder,RetrievalSettings(top_k=3,min_similarity=.25,context_budget=2048),
        evidence_policy=policy)
    return engine, policy


def test_same_subject_extra_row_cannot_exhaust_a_reviewed_claim_context():
    engine, _ = fixture()
    out = engine.retrieve(RetrievalRequest('synthetic printed amount','release-test'),
        subject_id='fees',requested_claims=('printed amount',))
    assert out['status'] == 'uncalibrated', out['gaps']
    assert [c['chunk_id'] for c in out['evidence']] == ['a','b']
    assert out['gaps'] == ['development_calibration_pending']
    assert out['evidence_policy']['assessment']['status'] == 'reviewed_fields_available'


def test_unknown_negative_or_mixed_claims_retain_the_full_subject_snapshot():
    _, policy = fixture()
    for claims in ((),('unknown',),('payment permission',),('printed amount','unknown')):
        assert policy._chunk_ids('fees',claims) == ['a','b','other']


def test_claim_filter_keeps_the_required_exception_and_empty_unknown_subject():
    _, policy = fixture()
    assert policy._chunk_ids('fees',('printed amount',)) == ['a','b']
    assert policy._chunk_ids('absent',('printed amount',)) == []


@pytest.mark.parametrize('conflict,status',[('edition','conflicting_sources'),('curriculum','needs_scope')])
def test_claim_selection_cannot_hide_an_alternative_edition_or_curriculum(conflict,status):
    engine, _ = fixture(conflict)
    result = engine.retrieve(RetrievalRequest('synthetic printed amount','release-test'),
        subject_id='fees',requested_claims=('printed amount',))
    assert result['status'] == status
    assert result['evidence'] == []


def test_explicit_curriculum_scope_still_filters_the_alternative_before_assembly():
    engine, _ = fixture('curriculum')
    result = engine.retrieve(RetrievalRequest('synthetic printed amount','release-test',
        scope=('audience:undergraduate','curriculum:first')),
        subject_id='fees',requested_claims=('printed amount',))
    assert result['status'] == 'uncalibrated'
    assert [c['chunk_id'] for c in result['evidence']] == ['a','b']
