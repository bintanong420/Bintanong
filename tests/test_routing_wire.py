"""Literal synthetic protocol regressions; no institutional claims or model calls."""
from copy import deepcopy
import importlib

import pytest

TEXT = 'Can I take B2 after failing A1? Where is form T?'


def quote(text, occurrence=0):
    return dict(text=text, occurrence=occurrence)


def packet():
    return dict(schema_version='bintanong-interpretation-wire-v4', language='en', part_count=2,
        audience='undergraduate', intent='eligibility and form location',
        mentions=[dict(kind='course', quote=quote('A1')),
                  dict(kind='course', quote=quote('B2'))],
        claims=[dict(quote=quote('failing A1'), entity=quote('A1'), state='failed', mode='asserted')],
        operations=[dict(name='check_prerequisite_eligibility', target=quote('B2'))],
        parts=[dict(part_id='r1', quote=quote('Can I take B2 after failing A1?'),
                    evidence_need='structured', operation_indices=[0]),
               dict(part_id='r2', quote=quote('Where is form T?'),
                    evidence_need='document', operation_indices=[])],
        route='Hybrid', control=None, ambiguities=[])


def normalize(value=None, text=TEXT):
    api = importlib.import_module('backend.bintanong_routing.wire')
    return api.normalize_interpretation(text, api.WireInterpretation.parse(packet() if value is None else value))


def test_quoted_target_and_condition_resolve_after_mention_reordering():
    result = normalize()
    assert result.schema_version == 'bintanong-interpretation-v2'
    assert result.operations[0].target == 1
    assert result.claims[0].entity == 0 and result.claims[0].mode == 'asserted'
    assert (result.mentions[1].text, result.mentions[1].start, result.mentions[1].end) == ('B2', 11, 13)
    assert (result.claims[0].start, result.claims[0].end) == (20, 30)
    assert (result.parts[1].start, result.parts[1].end) == (32, 48)
    value = packet()
    value['mentions'].reverse()
    reordered = normalize(value)
    assert reordered.operations[0].target == 0 and reordered.claims[0].entity == 1


def test_repeated_and_overlapping_text_use_declared_occurrence():
    value = packet()
    value.update(mentions=[], claims=[], operations=[], route='RAG', part_count=1,
        parts=[dict(part_id='r1', quote=quote('AA', 2), evidence_need='document', operation_indices=[])])
    result = normalize(value, 'AAAA')
    assert (result.parts[0].start, result.parts[0].end) == (2, 4)


@pytest.mark.parametrize('mutation', [
    lambda p: p['operations'][0].update(target=quote('C3')),
    lambda p: p['mentions'].append(deepcopy(p['mentions'][0])),
    lambda p: p['mentions'][1].update(kind='program'),
    lambda p: p['claims'][0].update(entity=quote('B2')),
    lambda p: p['parts'][0].update(quote=quote('failing A1')),
])
def test_invented_missing_duplicate_noncourse_or_uncontained_reference_rejects(mutation):
    value = packet()
    mutation(value)
    with pytest.raises(ValueError):
        normalize(value)


@pytest.mark.parametrize('occurrence', [True, '0', -1, 8192])
def test_occurrence_is_a_strict_bounded_integer(occurrence):
    value = packet()
    value['operations'][0]['target']['occurrence'] = occurrence
    with pytest.raises(ValueError):
        normalize(value)


@pytest.mark.parametrize('mode', ['hypothetical', 'reported'])
def test_nonasserted_mode_survives_and_existing_dispatch_guard_still_clarifies(mode):
    from backend.bintanong_routing.contracts import RequestContext
    from backend.bintanong_routing.validation import validate_interpretation
    from test_routing_validation import entry, registry
    value = packet()
    value['claims'][0]['mode'] = mode
    interpretation = normalize(value)
    context = RequestContext(session_id='sess-wire', request_id='req-wire',
        program_id='program-a', curriculum_id='curriculum-a')
    result = validate_interpretation(TEXT, context, interpretation,
        catalog=(entry(), entry(entity='course-b', alias='B2')),
        registry=registry(), documents_available=True, synthetic=True)
    assert interpretation.claims[0].mode == mode
    assert result.diagnostic == 'nonasserted_facts' and not result.decision.dispatchable


def test_missing_occurrence_and_legacy_index_or_offset_fields_are_not_accepted():
    for field, extra in [('target', 1), ('target', dict(text='B2', start=11, end=13))]:
        value = packet()
        value['operations'][0][field] = extra
        with pytest.raises(ValueError):
            normalize(value)


def test_wrong_occurrence_of_a_quote_that_appears_once_is_corrected():
    # Seen with real output (24 Oct 2026): "Nurs MC 1" declared as occurrence 1 after "Nursing" in the text.
    value = packet()
    for item in (value['mentions'][0]['quote'], value['claims'][0]['entity'], value['claims'][0]['quote'], value['parts'][0]['quote']):
        item['occurrence'] = 1
    result = normalize(value)
    assert (result.mentions[0].text, result.mentions[0].start) == ('A1', 28)
    assert result.claims[0].entity == 0 and (result.parts[0].start, result.parts[0].end) == (0, 31)


def test_two_declared_occurrences_of_a_quote_that_appears_once_reject():
    value = packet()
    value['mentions'].append(dict(kind='course', quote=quote('A1', 1)))
    with pytest.raises(ValueError):
        normalize(value)


def test_course_quote_the_model_forgot_to_list_becomes_a_course_mention():
    # Seen with real output (run 9, 23 Oct 2026): a program sentence was listed, CC5/CC4 were not.
    value = packet()
    value['mentions'] = [dict(kind='program', quote=quote('Where is form T?'))]
    result = normalize(value)
    assert [(m.kind, m.text) for m in result.mentions] == [('program', 'Where is form T?'), ('course', 'A1'), ('course', 'B2')]
    assert result.claims[0].entity == 1 and result.operations[0].target == 2


def test_miscounted_course_quote_reuses_the_listed_mention_at_that_place():
    value = packet()
    value['operations'][0]['target'] = quote('B2', 1)
    result = normalize(value)
    assert len(result.mentions) == 2 and result.operations[0].target == 1


def test_course_quote_on_a_listed_noncourse_mention_still_rejects():
    value = packet()
    value['mentions'][1]['kind'] = 'program'
    with pytest.raises(ValueError, match='invalid_course_quote_reference'):
        normalize(value)


def test_model_writes_intent_but_no_reason():
    # Latency (owner, 23 Oct 2026): nothing reads reason, so the model no longer decodes it.
    # intent stays: without it the 4B model dropped a failed-course claim (run 14 precheck).
    schema = importlib.import_module('backend.bintanong_routing.prompt').output_schema()
    assert schema['properties']['schema_version']['const'] == 'bintanong-interpretation-wire-v4'
    assert 'intent' in schema['properties'] and 'reason' not in schema['properties']


def test_wire_packet_with_reason_is_rejected():
    value = packet()
    value['reason'] = 'free text'
    with pytest.raises(Exception):
        normalize(value)


def test_host_supplies_reason_and_keeps_model_intent():
    result = normalize()
    assert result.intent == 'eligibility and form location'
    assert result.reason == 'interpreter proposed route Hybrid'
    value = packet()
    value.update(route=None, control='clarify')
    assert normalize(value).reason == 'interpreter proposed control clarify'
