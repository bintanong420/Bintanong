"""Trusted per-subject context size; synthetic evidence and exact fixture counter."""
from dataclasses import replace

import pytest

from backend.bintanong_retrieval.engine import RetrievalEngine
from backend.bintanong_retrieval.evidence_policy import SourceAwareEvidencePolicy
from backend.bintanong_retrieval.types import RetrievalRequest, RetrievalSettings
from tests.test_retrieval_engine import Client, Encoder
from tests.test_retrieval_evidence_policy import policy_fixture


def make_engine(overrides=None):
    inputs, rows = policy_fixture()
    client, encoder = Client(), Encoder()
    # The counter models a complete group occupying3000 tokens, independently of text
    # lengths. Real tokenizer/source-group measurements live in ignored evidence.
    encoder.count_context_tokens = lambda text: 3000
    client.payload['items'] = rows[:1]
    engine = RetrievalEngine(client, encoder, RetrievalSettings(context_budget=2048),
        evidence_policy=SourceAwareEvidencePolicy(**inputs), subject_context_budgets=overrides)
    return engine, client, rows


def test_only_the_configured_subject_can_emit_its_complete_larger_context():
    overrides = {'fees':4096}
    engine, client, rows = make_engine(overrides)
    overrides['fees'] = 1
    request = RetrievalRequest('synthetic question', 'release-test')
    out = engine.retrieve(request, subject_id='fees', requested_claims=('printed amount',))
    assert out['status'] == 'uncalibrated'
    assert [e['chunk_id'] for e in out['evidence']] == ['a','b']
    assert out['context_tokens'] == 3000
    assert out['configuration']['context_budget'] == 4096
    assert out['configuration']['fingerprint'] == replace(engine.settings,context_budget=4096).fingerprint
    assert engine.settings.context_budget == 2048
    client.payload['items'] = rows[2:]
    other = engine.retrieve(request, subject_id='other', requested_claims=('unknown',))
    assert other['status'] == 'insufficient_evidence'
    assert other['evidence'] == []
    assert other['configuration']['context_budget'] == 2048
    assert any(g.startswith('context_budget:') for g in other['gaps'])
    client.payload['items'] = rows[:1]
    again = engine.retrieve(request, subject_id='fees', requested_claims=('printed amount',))
    assert [e['chunk_id'] for e in again['evidence']] == ['a','b']


def test_default_budget_still_refuses_an_oversized_group_atomically():
    engine, _, _ = make_engine()
    result = engine.retrieve(RetrievalRequest('synthetic', 'release-test'),
        subject_id='fees', requested_claims=('printed amount',))
    assert result['status'] == 'insufficient_evidence'
    assert result['evidence'] == []
    assert result['configuration']['context_budget'] == 2048


@pytest.mark.parametrize('overrides', [[], {'unknown':4096}, {'':4096}, {'fees':True},
    {'fees':0}, {'fees':32769}, {'fees':4096.0}])
def test_invalid_or_unbound_overrides_reject_before_execution(overrides):
    with pytest.raises(ValueError):
        make_engine(overrides)


def test_an_override_requires_a_prepared_evidence_policy():
    with pytest.raises(ValueError):
        RetrievalEngine(Client(), Encoder(), subject_context_budgets={'fees':4096})
