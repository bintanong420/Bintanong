"""Counted literal protocol and real router transport boundaries; no inference."""
from copy import deepcopy
import json

import pytest

from backend.bintanong_routing.wire import WireInterpretation, normalize_interpretation
from test_routing_wire import TEXT, packet as previous_packet
from test_routing_wire_boundary import Model, STYLE, route


ORDER = ('schema_version', 'language', 'audience', 'control', 'part_count', 'parts',
         'intent', 'mentions', 'claims', 'operations', 'route', 'ambiguities')


def packet():
    value = previous_packet()
    value.update(schema_version='bintanong-interpretation-wire-v4', part_count=2)
    return value


def normalize(value):
    return normalize_interpretation(TEXT, WireInterpretation.parse(value))


def test_counted_wire_preserves_scoped_target_grade_and_distinct_parts():
    result = normalize(packet())
    assert result.schema_version == 'bintanong-interpretation-v2'
    assert result.mentions[result.operations[0].target].text == 'B2'
    assert result.mentions[result.claims[0].entity].text == 'A1'
    assert result.claims[0].state == 'failed' and result.claims[0].mode == 'asserted'
    assert [p.evidence_need for p in result.parts] == ['structured', 'document']
    assert 'part_count' not in result.model_dump()


def test_count_disagreement_rejects_without_rewriting_declared_parts():
    normalize(packet())
    value = packet()
    value['parts'].pop()
    original = deepcopy(value)
    with pytest.raises(ValueError, match='part_count_mismatch'):
        normalize(value)
    assert value == original


@pytest.mark.parametrize('change', ['missing', 'boolean', 'legacy'])
def test_only_new_wire_with_required_strict_count_is_accepted(change):
    normalize(packet())
    value = packet()
    if change == 'missing':
        value.pop('part_count')
    elif change == 'boolean':
        value['part_count'] = True
    else:
        value['schema_version'] = 'bintanong-interpretation-wire-v1'
    with pytest.raises(ValueError):
        normalize(value)


def test_zero_count_terminal_control_preserves_empty_work():
    value = packet()
    value.update(part_count=0, parts=[], mentions=[], claims=[], operations=[],
                 route=None, control='greeting')
    result = normalize(value)
    assert result.control == 'greeting' and not result.parts and not result.operations


def test_count_repair_cannot_buy_an_additional_style_repair():
    bad = packet()
    bad['part_count'] = 1
    model = Model(bad, packet(), 'invalid style')
    result = route(model)
    assert result.diagnostic == 'invalid_style_output'
    assert result.repair_attempts == 1 and len(model.calls) == 3


@pytest.mark.parametrize('combined', [False, True], ids=['separate', 'combined'])
def test_task_first_schema_and_display_reach_actual_router_transport(combined):
    value = packet()
    model = (Model(dict(schema_version='bintanong-routing-style-v4',
                        interpretation=value, style=STYLE['style']))
             if combined else Model(value, STYLE))
    result = route(model, combined=combined)
    assert result.diagnostic == 'validated' and result.decision.route == 'Hybrid'
    assert len(model.calls) == (1 if combined else 2) and result.repair_attempts == 0
    messages, schema = model.calls[0]
    decoder = schema['$defs']['WireInterpretation'] if combined else schema
    assert tuple(decoder['properties']) == ORDER
    assert all(tuple(branch['properties']) == ORDER for branch in decoder['oneOf'])
    displayed = json.loads(messages[0]['content'].rsplit('JSON schema:\n', 1)[1])
    displayed = displayed['$defs']['WireInterpretation'] if combined else displayed
    assert tuple(displayed['properties']) == ORDER
    assert 'reviewed_aliases' not in json.loads(messages[1]['content'])
    example = json.loads(messages[0]['content'].split('BEGIN FICTIONAL EXAMPLE\n', 1)[1]
                         .split('\nEND FICTIONAL EXAMPLE', 1)[0])['interpretation']
    assert tuple(example) == ORDER and example['part_count'] == len(example['parts']) == 3
