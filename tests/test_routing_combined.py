"""One inference, two independently grounded decisions; no weakened dispatch guard."""
import asyncio
from copy import deepcopy
import importlib
import json

import pytest
from jsonschema import Draft202012Validator

from backend.bintanong_contracts.schema_display import compact_for_prompt
from backend.bintanong_routing.contracts import RequestContext
from backend.bintanong_routing.prompt import output_schema as routing_schema
from backend.bintanong_routing.style import style_output_schema
from backend.bintanong_routing.transport import RuntimeFailure
from test_routing_contracts import context, proposal
from test_routing_router import FakeTransport, style_proposal
from test_routing_validation import catalog, registry
from routing_wire_fixtures import wire_fixture


def api():
    return importlib.import_module('backend.bintanong_routing.combined')


def packet(response_style='taglish', **interpretation):
    return dict(schema_version='bintanong-routing-style-v2',
        interpretation=wire_fixture(proposal(**interpretation), interpretation.get('text', 'A1')),
        style=style_proposal(response_style)['style'])


def run(transport, **options):
    config=dict(catalog=catalog(),registry=registry(),documents_available=True,synthetic=True)
    config.update(options)
    return asyncio.run(api().CombinedRouter(transport,**config).route('A1',RequestContext.parse(context())))


@pytest.mark.parametrize('language',['en','fil','taglish'])
def test_one_call_preserves_proposal_and_separately_grounded_style(language):
    transport=FakeTransport(json.dumps(packet(language,language='unknown')))
    result=run(transport)
    assert result.decision.route=='Symbolic' and result.response_style==language
    assert result.proposed.language=='unknown'
    assert result.style_evidence.language==language
    assert result.inference_calls==result.attempts==len(transport.calls)==1
    assert result.style_attempts==result.repair_attempts==0


def test_format_repair_is_one_shared_call_and_reanchors_original_question():
    transport=FakeTransport('bad json',json.dumps(packet()))
    result=run(transport)
    assert result.decision.route=='Symbolic' and result.inference_calls==2
    assert result.style_attempts==0 and result.repair_attempts==1
    assert 'original_text' in transport.calls[1][0][-1]['content']
    assert 'not a new student question' in transport.calls[1][0][-1]['content']


@pytest.mark.parametrize('raw',['bad','{"schema_version":"a","schema_version":"b"}',
    json.dumps(dict(packet(),extra='forbidden')),
    json.dumps(dict(packet(),schema_version='wrong')),
    json.dumps(dict(packet(),style=dict(style_proposal()['style'],extra='forbidden')))])
def test_two_invalid_packets_fail_closed_without_separate_or_rag_fallback(raw):
    transport=FakeTransport(raw,raw)
    result=run(transport)
    assert result.diagnostic=='invalid_model_output' and result.decision.route is None
    assert result.decision.control=='evidence_unavailable' and result.inference_calls==2


@pytest.mark.parametrize('change',['style','mention'])
def test_invalid_wire_and_style_grounding_preserve_format_repair_limits(change):
    value=packet()
    if change=='style':value['style']['english_fragments']=['invented']
    else:value['interpretation']['mentions'][0]['quote']['text']='B1'
    transport=FakeTransport(json.dumps(value),json.dumps(value))
    result=run(transport)
    assert result.diagnostic==('invalid_grounding' if change=='style' else 'invalid_model_output')
    assert not result.decision.dispatchable
    assert result.inference_calls==len(transport.calls)==(1 if change=='style' else 2)


def test_timeout_does_not_spend_a_repair_or_enter_separate_path():
    transport=FakeTransport(RuntimeFailure('model_timeout'))
    assert run(transport).diagnostic=='model_timeout'
    assert len(transport.calls)==1


def test_missing_capability_preserves_unknown_and_requested_operation():
    from backend.bintanong_contracts.symbolic import EMPTY_REGISTRY
    result=run(FakeTransport(json.dumps(packet())),registry=EMPTY_REGISTRY)
    assert result.decision.control=='evidence_unavailable'
    assert result.proposed.operations and not result.claims
    assert result.decision.route is None


def test_ambiguous_semantics_hold_without_an_additional_model_call():
    transport=FakeTransport(json.dumps(packet(ambiguities=['Which curriculum?'])))
    assert run(transport).decision.control=='clarify'
    assert len(transport.calls)==1


def test_full_nested_schema_retains_original_acceptance_and_style_constraints():
    original_routing=routing_schema();original_style=style_output_schema()
    before=deepcopy((original_routing,original_style))
    full=api().output_schema();short=compact_for_prompt(full)
    Draft202012Validator.check_schema(full);Draft202012Validator.check_schema(short)
    validators=[Draft202012Validator(v) for v in (full,short)]
    route_validator=Draft202012Validator(original_routing)
    for audience in ('undergraduate','excluded','unrelated','unknown'):
        for route in (None,'RAG','Symbolic','Hybrid'):
            for control in (None,'clarify','greeting','unsupported_scope','evidence_unavailable'):
                for operations in ([],[dict(name='check_prerequisite_eligibility',target=0)]):
                    value=packet(audience=audience,route=route,control=control,operations=operations)
                    expected=route_validator.is_valid(value['interpretation'])
                    assert all(v.is_valid(value)==expected for v in validators)
    bad=packet();bad['style']['preferred_response_style']='english_only'
    assert all(not v.is_valid(bad) for v in validators)
    assert (original_routing,original_style)==before


def test_combined_prompt_keeps_original_data_and_scopes_both_task_instructions():
    module=api()
    messages=module.build_messages('A1',RequestContext.parse(context()),catalog(),registry())
    system=messages[0]['content']
    assert 'interpretation' in system and 'style' in system and 'Prolog' in system
    assert 'English' in system and 'Filipino' in system and 'Taglish' in system
    assert json.loads(system.split('JSON schema:\n',1)[1])==compact_for_prompt(module.output_schema())
    data=json.loads(messages[1]['content'])
    assert data['original_text']=='A1' and data['reviewed_aliases']
    assert 'session_id' not in data['context'] and 'request_id' not in data['context']
    assert module.PROMPT_SHA256 and module.PROMPT_VERSION


def test_evaluation_identifies_actual_combined_packet_and_physical_calls():
    from backend.bintanong_routing.evaluation import evaluate_cases
    from test_routing_evaluation import case, metadata
    module=api()
    router=module.CombinedRouter(FakeTransport(json.dumps(packet('en'))),
        catalog=catalog(),registry=registry(),documents_available=True,synthetic=True)
    report=asyncio.run(evaluate_cases(router,[case()],metadata()))
    assert report['routing_profile']=='combined'
    assert report['prompt_sha256']==module.PROMPT_SHA256
    assert report['schema_sha256']==module.digest(module.output_schema())
    assert report['inference_calls']==report['routing_calls']==1 and report['style_calls']==0
    assert report['records'][0]['style_evidence'] and report['style_correct']==1
