"""Owner27Oct: three input families,two reply targets;grounded fragments remain literal."""
import asyncio
import json

import pytest

from backend.bintanong_routing.style import StyleProposal, style_output_schema
from test_routing_router import FakeTransport, run
from test_routing_contracts import proposal
from test_generation_evidence import integrated
from test_generation_loop import Fake as GenerationTransport
from backend.bintanong_generation.generator import Generator


def new_style(english=(), filipino=(), target='taglish'):
    return dict(schema_version='bintanong-response-style-v2', style=dict(
        english_fragments=list(english), filipino_fragments=list(filipino), preferred_response_style=target))


@pytest.mark.parametrize('text,english,filipino,target', [
    ('How do I apply?', ('How do I',), (), 'english_only'),
    ('Paano ako makakakuha?', (), ('Paano ako',), 'taglish'),
    ('Paano mag-request?', ('request',), ('Paano',), 'taglish'),
])
def test_new_style_evidence_preserves_input_fragments_and_uses_only_current_reply_targets(text, english, filipino, target):
    style = StyleProposal.parse(new_style(english, filipino, target)).style
    style.ground(text)
    assert style.language == ('en' if target=='english_only' else 'taglish')
    assert style.english_fragments == english and style.filipino_fragments == filipino


def test_new_model_schema_retires_exclusive_filipino_without_requiring_fabricated_english():
    import jsonschema
    validator=jsonschema.Draft202012Validator(style_output_schema())
    assert validator.is_valid(new_style(filipino=('Paano',)))
    assert not validator.is_valid(new_style(filipino=('Paano',), target='filipino'))
    assert not validator.is_valid(new_style())
    assert not validator.is_valid(new_style(english=('Hello',), target='taglish'))
    assert validator.is_valid(new_style(target='unknown'))


def test_legacy_style_wire_cannot_enter_the_new_inference_boundary():
    old = new_style(filipino=('Paano',))
    old['schema_version']='bintanong-response-style-v1'
    with pytest.raises(ValueError): StyleProposal.parse(old)


def test_new_generation_model_schema_offers_no_exclusive_filipino_target():
    from backend.bintanong_generation.prompt import output_schema
    from backend.bintanong_generation.contracts import AnswerDraft
    assert output_schema(AnswerDraft)['properties']['language']['enum']==['en','taglish','unknown']


def test_router_preserves_tagalog_only_input_but_requests_taglish_reply():
    value=proposal(text='A1 paano?', language='fil')
    transport=FakeTransport(json.dumps(value), style_outputs=[json.dumps(new_style(filipino=('paano',)))])
    result=run(transport, text='A1 paano?')
    assert result.decision.route=='Symbolic' and result.response_style=='taglish'
    assert result.proposed.language=='fil'  # proposed input interpretation remains observable
    assert result.style_evidence.english_fragments==()


def test_combined_router_uses_tagalog_only_evidence_without_english_fragments():
    from backend.bintanong_routing.combined import CombinedRouter
    from backend.bintanong_routing.contracts import RequestContext
    from test_routing_contracts import context
    from test_routing_validation import catalog, registry
    from routing_wire_fixtures import wire_fixture
    text='A1 paano?'
    packet=dict(schema_version='bintanong-routing-style-v4',
        interpretation=wire_fixture(proposal(text=text,language='fil'),text),
        style=new_style(filipino=('paano',))['style'])
    transport=FakeTransport(json.dumps(packet))
    router=CombinedRouter(transport,catalog=catalog(),registry=registry(),documents_available=True,synthetic=True)
    result=asyncio.run(router.route(text,RequestContext.parse(context())))
    assert result.decision.route=='Symbolic' and result.response_style=='taglish'
    assert result.proposed.language=='fil' and result.style_evidence.english_fragments==()
    assert result.inference_calls==1


@pytest.mark.parametrize('status', ['greeting', 'clarify', 'unknown', 'unsupported_scope', 'error'])
def test_generation_control_boundary_maps_legacy_filipino_target_before_host_rendering(status):
    from backend.bintanong_orchestration.contracts import IntegrationResult
    integration=IntegrationResult(schema_version=IntegrationResult.SCHEMA_VERSION,
        request_id='req-policy',route=None,response_style='fil',status=status,evidence=None,understanding=None,events=())
    before=integration.model_dump(mode='json')
    answer=asyncio.run(Generator(GenerationTransport()).generate('Paano?',integration))
    assert answer.language=='taglish'
    assert integration.model_dump(mode='json')==before


def test_symbolic_host_answer_uses_taglish_without_changing_canonical_decision():
    integration=integrated('Symbolic',response_style='fil',text='Fictional check?')
    answer=asyncio.run(Generator(GenerationTransport()).generate('Fictional check?',integration))
    assert answer.language=='taglish' and answer.status=='answered'
    assert answer.decision==integration.evidence.symbolic.decision
    assert 'satisfied ang conditions' in answer.text


def test_prepared_evidence_normalizes_before_any_generation_or_review_identity():
    from backend.bintanong_generation.evidence import prepare
    integration=integrated('RAG',response_style='fil')
    pack=prepare(integration)
    assert pack.language=='taglish' and pack.model_payload()['language']=='taglish'
    assert integration.response_style=='fil'


def test_document_generation_request_and_review_share_the_normalized_reply_language():
    from test_generation_part_slots import PartModel
    integration=integrated('RAG',response_style='fil',text='Fictional policy?')
    model=PartModel(slots={'r1':('answered',['May fictional policy sa source.'])})
    answer=asyncio.run(Generator(model).generate('Fictional policy?',integration))
    assert answer.language=='taglish' and answer.status=='answered'
    assert len(model.calls)==2
    assert model.calls[0][1]['properties']['language']['const']=='taglish'
    assert all('"language": "fil"' not in m[1]['content'] for m,_ in model.calls)


def test_current_evaluation_reports_policy_expectation_without_rewriting_case_input():
    from backend.bintanong_routing.evaluation import evaluate_cases
    from backend.bintanong_routing.router import Router
    from test_routing_evaluation import case, metadata
    from test_routing_validation import catalog, registry
    authored=case(language='fil',expected_style='fil')
    before=json.dumps(authored,sort_keys=True)
    transport=FakeTransport(json.dumps(proposal(language='fil')),
        style_outputs=[json.dumps(new_style(filipino=('A1',)))])
    router=Router(transport,catalog=catalog(),registry=registry(),documents_available=True,synthetic=True)
    report=asyncio.run(evaluate_cases(router,[authored],metadata()))
    assert report['style_correct']==1
    assert report['reply_policy_version']=='english-taglish-20261027-v1'
    assert report['records'][0]['expected_reply_style']=='taglish'
    assert json.dumps(authored,sort_keys=True)==before


def test_generation_observations_keep_authored_input_family_separate_from_reply_target():
    from backend.bintanong_generation.evaluation import load_cases, observe
    from test_generation_evaluation import case
    from test_generation_pipeline import EchoEvidence
    authored=case(input_language='fil')
    report=asyncio.run(observe(load_cases([authored]),
        Generator(EchoEvidence(),explanation_profile='legacy'),evaluation_kind='mock'))
    assert report['observations'][0]['input_language']=='fil'
    assert report['observations'][0]['expected_reply_language']=='en'
    assert report['reply_policy_version']=='english-taglish-20261027-v1'
