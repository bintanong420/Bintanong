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
    from backend.bintanong_routing.prompt import output_schema
    schema = output_schema()
    branches = schema['oneOf']
    assert len(branches) == 2
    assert branches[0]['properties']['control'] == {'type':'null'}
    assert branches[1]['properties']['route'] == {'type':'null'}
