import importlib

import pytest

from backend.bintanong_orchestration.contracts import IntegrationResult
from backend.bintanong_orchestration.integration import assemble
from test_orchestration_integration import pin,documents,symbolic


def api():
    return importlib.import_module('backend.bintanong_generation.evidence')


def integrated(route='Hybrid',outcome='eligible',**updates):
    evidence = assemble(pin(),route,documents=documents() if route!='Symbolic' else None,
                        symbolic=symbolic(outcome) if route!='RAG' else None)
    data = dict(schema_version=IntegrationResult.SCHEMA_VERSION,request_id='req-a',route=route,
        response_style='en',status=evidence.status,evidence=evidence,events=())
    data.update(updates)
    return IntegrationResult(**data)


@pytest.mark.parametrize('route',['RAG','Symbolic','Hybrid'])
def test_allowed_cards_preserve_complete_text_and_real_locators(route):
    result = integrated(route)
    prepared = api().prepare(result)
    assert prepared.cards and all(c.citations for c in prepared.cards)
    assert prepared.release_id == result.evidence.pin.release_id
    assert all(c.evidence_id.startswith('ev-') and len(c.evidence_id)==67 for c in prepared.cards)
    assert api().prepare(result).cards == prepared.cards
    if route!='RAG':
        assert prepared.decision == result.evidence.symbolic.decision
    payload = str(prepared.model_payload())
    assert 'req-a' not in payload and 'fact-synth' not in payload and 'sess-' not in payload


def test_caller_cannot_relabel_uncalibrated_or_mismatched_release_as_ready():
    value = integrated('RAG').model_dump(mode='json')
    value['evidence']['documents']['status']='uncalibrated'
    bad = IntegrationResult.parse(value)
    with pytest.raises(ValueError,match='integration_policy'):
        api().prepare(bad)
    value['evidence']['documents']['status']='ok'
    value['evidence']['documents']['release_id']='release-wrong'
    with pytest.raises(ValueError,match='integration_policy'):
        api().prepare(IntegrationResult.parse(value))


def test_unknown_and_no_evidence_controls_remain_nonready():
    unknown = api().prepare(integrated(outcome='unknown'))
    assert unknown.status == 'unknown' and unknown.decision.outcome == 'unknown'
    control=IntegrationResult(schema_version=IntegrationResult.SCHEMA_VERSION,
        request_id='req-a',route=None,response_style='fil',status='unsupported_scope',
        evidence=None,events=())
    result=api().prepare(control)
    assert result.cards == () and result.status == 'unsupported_scope'


def test_strict_draft_rejects_unknown_fields_and_duplicate_claims():
    contracts=importlib.import_module('backend.bintanong_generation.contracts')
    card=api().prepare(integrated()).cards[0]
    payload=dict(schema_version='bintanong-answer-draft-v1',language='en',
        release_id='release-synth-1',decision_outcome='eligible',claims=[
            dict(claim_id='c1',text='Fictional policy.',evidence_ids=[card.evidence_id])])
    assert contracts.AnswerDraft.parse(payload).claims[0].claim_id == 'c1'
    with pytest.raises(ValueError):
        contracts.AnswerDraft.parse(dict(payload,approved=True))
    with pytest.raises(ValueError):
        contracts.AnswerDraft.parse(dict(payload,claims=payload['claims']*2))
