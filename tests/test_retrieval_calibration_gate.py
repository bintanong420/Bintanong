"""Research retrieval must not promote incomplete reviewed-field reports to answer-ready."""
import asyncio
from copy import deepcopy

import pytest

from backend.bintanong_orchestration.adapters import RetrievalAdapter
from backend.bintanong_retrieval.types import RetrievalRequest
from test_orchestration_integration import documents


class FakeResearchRetrieval:
    def __init__(self, payload):
        self.payload = payload

    def retrieve(self, request, **intent):
        return deepcopy(self.payload)


def payload():
    passage = documents().model_dump(mode='json')['passages'][0]
    chunk = passage['chunk_id']
    claim = dict(claim='printed office', status='reviewed_fields_available',
                 source_review=dict(finding='visible_fields'),
                 source_fields=[dict(chunk_id=chunk,
                                     field=dict(name='office', value='Office A',
                                                source_blank=False, span_indexes=[0]))])
    return dict(schema_version='bintanong-retrieval-debug-v2',
                release_id='release-synth-1', status='uncalibrated',
                gaps=['development_calibration_pending'], evidence=[passage],
                evidence_policy=dict(assessment=dict(
                    status='reviewed_fields_available', subject_id='fictional_office',
                    claims=[claim])))


def retrieve(raw, **intent):
    defaults = dict(subject_id='fictional_office', requested_claims=('printed office',))
    defaults.update(intent)
    return asyncio.run(RetrievalAdapter(FakeResearchRetrieval(raw), research=True).retrieve(
        RetrievalRequest('Where?', 'release-synth-1'), **defaults))


def test_complete_reviewed_fields_lift_only_calibration_marker():
    result = retrieve(payload())
    assert result.status == 'ok' and not result.gaps
    assert len(result.record_coverage) == 1


@pytest.mark.parametrize('mutation', [
    'other_gap', 'empty_evidence', 'wrong_subject', 'wrong_claim', 'unreviewed',
    'field_outside_emission', 'blank_field', 'missing_fields', 'additional_claim',
])
def test_reviewed_field_presence_is_not_unconditional_answer_permission(mutation):
    raw = payload()
    report = raw['evidence_policy']['assessment']
    claim = report['claims'][0]
    if mutation == 'other_gap':
        raw['gaps'].append('incomplete_procedure')
    elif mutation == 'empty_evidence':
        raw['evidence'] = []
    elif mutation == 'wrong_subject':
        report['subject_id'] = 'other'
    elif mutation == 'wrong_claim':
        claim['claim'] = 'different claim'
    elif mutation == 'unreviewed':
        claim['source_review']['finding'] = 'unresolved'
    elif mutation == 'field_outside_emission':
        claim['source_fields'][0]['chunk_id'] = 'f'*64
    elif mutation == 'blank_field':
        claim['source_fields'][0]['field']['source_blank'] = True
    elif mutation == 'missing_fields':
        claim['source_fields'] = []
    elif mutation == 'additional_claim':
        report['claims'].append(dict(claim, claim='unrequested claim'))
    result = retrieve(raw)
    assert result.status == 'uncalibrated'
    assert 'development_calibration_pending' in result.gaps


@pytest.mark.parametrize('intent', [
    {}, {'requested_claims':('printed office','second question')},
    {'requested_claims':('incorrect question',)},
    {'subject_id':'unmatched_topic'},
])
def test_unbound_or_mismatched_request_remains_held(intent):
    # No topic/claims supplied must not acquire reviewed-field authorization.
    opts = dict(subject_id='fictional_office', requested_claims=('printed office',))
    opts.update(intent)
    if not intent:
        opts = dict(subject_id=None, requested_claims=None)
    result = retrieve(payload(), **opts)
    assert result.status == 'uncalibrated'


def test_synthetic_retrieval_cannot_use_research_only_promotion():
    raw = payload()
    result = asyncio.run(RetrievalAdapter(FakeResearchRetrieval(raw), research=False).retrieve(
        RetrievalRequest('Where?', 'release-synth-1'),
        subject_id='fictional_office', requested_claims=('printed office',)))
    assert result.status == 'uncalibrated'
