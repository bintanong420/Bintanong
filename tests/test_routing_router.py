import asyncio
import importlib
import json

import pytest

from backend.bintanong_routing.contracts import RequestContext
from test_routing_contracts import context, proposal
from test_routing_validation import catalog, registry


def api():
    return importlib.import_module('backend.bintanong_routing.router')


class FakeTransport:
    def __init__(self, *outputs):
        self.outputs = list(outputs)
        self.calls = []
    async def infer(self, messages, schema):
        self.calls.append((messages, schema))
        value = self.outputs.pop(0)
        if isinstance(value, Exception):
            raise value
        return value


def run(transport, **options):
    defaults = dict(catalog=catalog(), registry=registry(), documents_available=True, synthetic=True)
    defaults.update(options)
    return asyncio.run(api().Router(transport, **defaults).route('A1', RequestContext.parse(context())))


@pytest.mark.parametrize('language', ['en','fil','taglish'])
def test_model_selected_language_style_is_preserved(language):
    transport = FakeTransport(json.dumps(proposal(language=language)))
    result = run(transport)
    assert result.response_style == language and result.decision.route == 'Symbolic'
    assert result.attempts == 1
    system = transport.calls[0][0][0]['content']
    assert 'LLM' in system and 'Taglish' in system and 'Prolog' in system
    assert 'A1' in transport.calls[0][0][1]['content']
    assert transport.calls[0][1]['properties']['schema_version']['const'] == 'bintanong-interpretation-v1'


def test_invalid_json_repairs_once_and_retains_complete_repair_messages():
    transport = FakeTransport('bad json', json.dumps(proposal()))
    result = run(transport)
    assert result.attempts == 2 and result.decision.route == 'Symbolic'
    messages = transport.calls[1][0]
    assert len(messages) == 4 and messages[2]['content'] == 'bad json'


def test_repair_explicitly_reanchors_the_original_student_request():
    transport = FakeTransport('bad json', json.dumps(proposal()))
    run(transport)
    repair = transport.calls[1][0][-1]['content']
    assert 'original_text' in repair and 'A1' in repair
    assert 'not a new student question' in repair


def test_second_invalid_output_is_unavailable_not_rag():
    transport = FakeTransport('bad', 'still bad')
    result = run(transport)
    assert result.decision.control == 'evidence_unavailable' and result.decision.route is None
    assert result.diagnostic == 'invalid_model_output' and result.attempts == 2


def test_semantic_hold_does_not_repair_or_fall_back():
    transport = FakeTransport(json.dumps(proposal(ambiguities=['uncertain'])))
    result = run(transport)
    assert result.decision.control == 'clarify' and len(transport.calls) == 1


def test_false_grounding_is_unavailable_without_a_semantic_repair():
    value = proposal(mentions=[dict(kind='course', text='B1', start=0, end=2)])
    transport = FakeTransport(json.dumps(value))
    result = run(transport)
    assert result.diagnostic == 'invalid_grounding' and not result.decision.dispatchable
    assert len(transport.calls) == 1


def test_timeout_stops_without_format_repair():
    from backend.bintanong_routing.transport import RuntimeFailure
    transport = FakeTransport(RuntimeFailure('model_timeout'))
    result = run(transport)
    assert result.diagnostic == 'model_timeout' and result.attempts == 1


def test_duplicate_json_keys_are_not_silently_overwritten():
    transport = FakeTransport('{"language":"en","language":"fil"}', 'invalid')
    assert run(transport).diagnostic == 'invalid_model_output'


def test_decoder_schema_expresses_mutually_exclusive_route_and_control():
    jsonschema = pytest.importorskip('jsonschema')
    from backend.bintanong_routing.prompt import output_schema
    validator = jsonschema.Draft202012Validator(output_schema())
    assert validator.is_valid(proposal())
    assert not validator.is_valid(proposal(control='greeting'))
    assert not validator.is_valid(proposal(route=None))


@pytest.mark.parametrize('control', ['greeting', 'unsupported_scope'])
@pytest.mark.parametrize('field', ['operations', 'claims'])
def test_terminal_control_schema_and_contract_forbid_student_actions(control, field):
    jsonschema = pytest.importorskip('jsonschema')
    from backend.bintanong_routing.contracts import Interpretation
    from backend.bintanong_routing.prompt import output_schema
    value = proposal(route=None, control=control, operations=[])
    validator = jsonschema.Draft202012Validator(output_schema())
    assert validator.is_valid(value)
    assert Interpretation.parse(value).control == control
    if field == 'operations':
        value[field] = [dict(name='check_prerequisite_eligibility', target=0)]
    else:
        value[field] = [dict(text='A1', start=0, end=2, entity=0, state='passed', mode='asserted')]
    assert not validator.is_valid(value)
    with pytest.raises(ValueError, match='terminal_control_has_actions'):
        Interpretation.parse(value)


def test_compound_clarification_keeps_the_requested_operations():
    jsonschema = pytest.importorskip('jsonschema')
    from backend.bintanong_routing.contracts import Interpretation
    from backend.bintanong_routing.prompt import output_schema
    value = proposal(route=None, control='clarify', operations=[
        dict(name='check_prerequisite_eligibility', target=0),
        dict(name='list_affected_courses', target=0)])
    assert jsonschema.Draft202012Validator(output_schema()).is_valid(value)
    assert len(Interpretation.parse(value).operations) == 2


@pytest.mark.parametrize('apostrophe', ["'", '’'])
def test_english_contractions_do_not_fail_grounding(apostrophe):
    text = f'I didn{apostrophe}t pass A1.'
    value = proposal(language='en', mentions=[dict(kind='course',text='A1',start=14,end=16)], claims=[])
    transport = FakeTransport(json.dumps(value))
    router = api().Router(transport, catalog=catalog(), registry=registry(), synthetic=True)
    result = asyncio.run(router.route(text, RequestContext.parse(context())))
    assert result.diagnostic == 'validated' and result.decision.route == 'Symbolic'
    assert result.query.normalized_text == text


def test_unique_literal_quotes_anchor_bad_model_offsets_without_changing_meaning():
    value = proposal(language='en', mentions=[dict(kind='course',text='A1',start=0,end=2),
        dict(kind='course',text='B1',start=16,end=19)],
        claims=[dict(text='I failed A1.',start=0,end=10,entity=0,state='failed',mode='asserted')],
        operations=[dict(name='check_prerequisite_eligibility',target=1)])
    text = 'I failed A1. Check if I can take B1.'
    transport = FakeTransport(json.dumps(value))
    router = api().Router(transport,catalog=catalog(),registry=registry(),synthetic=True)
    result = asyncio.run(router.route(text,RequestContext.parse(context())))
    assert result.decision.route == 'Symbolic' and result.offset_corrections == 3
    assert result.claims[0].state == 'failed' and result.claims[0].text == 'I failed A1.'
    assert result.proposed.mentions[0].start == text.index('A1')
    assert len(transport.calls) == 1


def test_ambiguous_repeated_quote_cannot_repair_invalid_model_offsets():
    value = proposal(mentions=[dict(kind='course',text='A1',start=1,end=3)])
    router = api().Router(FakeTransport(json.dumps(value)),catalog=catalog(),registry=registry(),synthetic=True)
    result = asyncio.run(router.route('A1 A1',RequestContext.parse(context())))
    assert result.diagnostic == 'invalid_grounding' and not result.decision.dispatchable


def test_private_ownership_and_scenario_identifiers_never_enter_model_input():
    transport = FakeTransport(json.dumps(proposal()))
    ctx = context(session_id='sess-private-owner',request_id='req-gold-symbolic-label',
        facts=[dict(fact_id='fact-private-record',session_id='sess-private-owner',
            program_id='program-a',curriculum_id='curriculum-a',course_id='course-a',state='passed')])
    router = api().Router(transport,catalog=catalog(),registry=registry(),synthetic=True)
    result = asyncio.run(router.route('A1',RequestContext.parse(ctx)))
    sent = json.dumps(transport.calls[0][0])
    for private in ['sess-private-owner','req-gold-symbolic-label','fact-private-record']:
        assert private not in sent
    assert result.query.session_fact_refs == ('fact-private-record',)
    data = json.loads(transport.calls[0][0][1]['content'])
    assert data['context']['facts'] == [{'course_id':'course-a','state':'passed'}]
