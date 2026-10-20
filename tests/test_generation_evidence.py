import importlib
import hashlib

import pytest

from backend.bintanong_orchestration.contracts import IntegrationResult, RequestUnderstanding
from backend.bintanong_orchestration.integration import assemble
from test_orchestration_integration import pin,documents,symbolic


def api():
    return importlib.import_module('backend.bintanong_generation.evidence')


def integrated(route='Hybrid',outcome='eligible',*,text='Fictional check; fictional policy?',**updates):
    evidence = assemble(pin(),route,documents=documents() if route!='Symbolic' else None,
                        symbolic=symbolic(outcome) if route!='RAG' else None)
    data = dict(schema_version=IntegrationResult.SCHEMA_VERSION,request_id='req-a',route=route,
        response_style='en',status=evidence.status,evidence=evidence,events=())
    data.update(updates)
    operation = None if evidence.symbolic is None else dict(
        predicate=evidence.symbolic.decision.predicate,
        inputs=[i.model_dump(mode='json') for i in evidence.symbolic.inputs])
    parts = []
    if route != 'RAG':
        quote = text.split('; ')[0] if route == 'Hybrid' else text
        parts.append(dict(part_id='r1',text=quote,start=0,end=len(quote),
                          evidence_need='structured',operation_indices=[0]))
    if route != 'Symbolic':
        quote = text.split('; ')[1] if route == 'Hybrid' else text
        start = text.index(quote)
        parts.append(dict(part_id='r2' if parts else 'r1',text=quote,start=start,end=start+len(quote),
                          evidence_need='document',operation_indices=[]))
    data['understanding'] = RequestUnderstanding.parse(dict(schema_version='bintanong-request-understanding-v1',
        request_id=data['request_id'],release_id=evidence.pin.release_id,
        question_sha256=hashlib.sha256(text.encode()).hexdigest(),route=route,parts=parts,
        operations=[] if operation is None else [dict(name=operation['predicate'],target=0)],
        predicate_request=operation))
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
    control=IntegrationResult(understanding=None,schema_version=IntegrationResult.SCHEMA_VERSION,
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


def test_resolved_target_curriculum_and_edition_survive_without_fact_refs():
    first=integrated('Symbolic')
    value=first.model_dump(mode='json')
    value['evidence']['symbolic']['inputs'][0]['value']='FICTIONAL-202'
    value['understanding']['predicate_request']['inputs'][0]['value']='FICTIONAL-202'
    second=IntegrationResult.parse(value)
    a,b=api().prepare(first),api().prepare(second)
    assert a.model_payload()!=b.model_payload()
    context=a.model_payload()['structured_context']
    assert context['inputs']=={'course':'FICTIONAL-101'}
    assert context['scope']['edition_ids']==['edition-synth-handbook-1']
    assert context['rule_bundle_version']=='bundle-synth-1'
    assert 'fact-synth' not in str(context) and 'fact_ref' not in str(context)


def test_private_namespace_in_control_missing_facts_is_rejected():
    control=IntegrationResult(understanding=None,schema_version=IntegrationResult.SCHEMA_VERSION,
        request_id='req-a',route=None,response_style='en',status='clarify',evidence=None,
        missing_facts=('sess-other-1',),events=())
    with pytest.raises(ValueError,match='private_missing_fact_reference'):
        api().prepare(control)
