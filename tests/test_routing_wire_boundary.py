"""Literal wire packets at real router boundaries, independent of fixture migration."""
import asyncio
import json

from jsonschema import Draft202012Validator

from backend.bintanong_routing.contracts import RequestContext
from test_routing_wire import TEXT, packet
from test_routing_validation import entry, registry


STYLE = dict(schema_version='bintanong-response-style-v1', style=dict(
    english_fragments=['Can I take'], filipino_fragments=[], preferred_response_style='english_only'))


class Model:
    def __init__(self, *outputs):
        self.outputs, self.calls = outputs, []

    async def infer(self, messages, schema):
        index = len(self.calls)
        self.calls.append((messages, schema))
        value = self.outputs[min(index, len(self.outputs)-1)]
        return value if isinstance(value, str) else json.dumps(value)


def route(model, *, combined=False):
    from backend.bintanong_routing.router import Router
    from backend.bintanong_routing.combined import CombinedRouter
    router = (CombinedRouter if combined else Router)(model,
        catalog=(entry(), entry(entity='course-b', alias='B2')), registry=registry(),
        documents_available=True, synthetic=True)
    return asyncio.run(router.route(TEXT, RequestContext(session_id='sess-wire',
        request_id='req-wire', program_id='program-a', curriculum_id='curriculum-a')))


def test_selected_router_normalizes_literal_wire_before_existing_dispatch_checks():
    model = Model(packet(), STYLE)
    result = route(model)
    assert result.diagnostic == 'validated' and result.decision.route == 'Hybrid'
    assert result.proposed.schema_version == 'bintanong-interpretation-v2'
    assert result.proposed.operations[0].target == 1
    assert result.claims[0].state == 'failed' and result.claims[0].course_id == 'course-a'
    assert {i.name:i.value for i in result.decision.predicate_request.inputs}['course_id'] == 'course-b'
    assert len(model.calls) == 2 and result.offset_corrections == 0


def test_wire_schema_does_not_request_offsets_or_numeric_course_references():
    from backend.bintanong_routing.prompt import output_schema
    schema = output_schema()
    assert Draft202012Validator(schema).is_valid(packet())
    definitions = schema['$defs']
    assert set(definitions['QuoteReference']['properties']) == {'text', 'occurrence'}
    assert definitions['WireOperation']['properties']['target'] == {'$ref':'#/$defs/QuoteReference'}
    assert definitions['WireClaim']['properties']['entity'] == {'$ref':'#/$defs/QuoteReference'}
    assert 'start' not in json.dumps(schema) and 'end' not in definitions['QuoteReference']['properties']


def test_invalid_quote_spends_only_existing_shared_repair():
    bad = packet()
    bad['operations'][0]['target']['text'] = 'invented'
    model = Model(bad, packet(), STYLE)
    result = route(model)
    assert result.decision.route == 'Hybrid' and result.repair_attempts == 1
    assert len(model.calls) == 3


def test_style_cannot_obtain_an_extra_repair_after_wire_repair():
    model = Model('invalid', packet(), 'invalid style')
    result = route(model)
    assert result.diagnostic == 'invalid_style_output' and len(model.calls) == 3


def test_explicit_combined_experiment_uses_same_wire_normalizer_in_one_call():
    model = Model(dict(schema_version='bintanong-routing-style-v3',
        interpretation=packet(), style=STYLE['style']))
    result = route(model, combined=True)
    assert result.decision.route == 'Hybrid' and len(model.calls) == 1
    assert result.proposed.operations[0].target == 1


def test_legacy_model_packet_is_rejected_without_silent_fallback():
    from test_routing_contracts import proposal
    model = Model(proposal())
    result = route(model)
    assert result.diagnostic == 'invalid_model_output' and len(model.calls) == 2


def test_mode_and_scope_guards_remain_active_after_wire_normalization():
    value = packet()
    value['claims'][0]['mode'] = 'hypothetical'
    result = route(Model(value, STYLE))
    assert result.diagnostic == 'nonasserted_facts' and not result.decision.dispatchable
