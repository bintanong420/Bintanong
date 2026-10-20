"""Literal synthetic protocol regressions; no institutional claims or model calls."""
from copy import deepcopy
import importlib

import pytest

TEXT = 'Can I take B2 after failing A1? Where is form T?'


def quote(text, occurrence=0):
    return dict(text=text, occurrence=occurrence)


def packet():
    return dict(schema_version='bintanong-interpretation-wire-v2', language='en', part_count=2,
        audience='undergraduate', intent='eligibility and form location',
        mentions=[dict(kind='course', quote=quote('A1')),
                  dict(kind='course', quote=quote('B2'))],
        claims=[dict(quote=quote('failing A1'), entity=quote('A1'), state='failed', mode='asserted')],
        operations=[dict(name='check_prerequisite_eligibility', target=quote('B2'))],
        parts=[dict(part_id='r1', quote=quote('Can I take B2 after failing A1?'),
                    evidence_need='structured', operation_indices=[0]),
               dict(part_id='r2', quote=quote('Where is form T?'),
                    evidence_need='document', operation_indices=[])],
        route='Hybrid', control=None, ambiguities=[], reason='Two requested tasks.')


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
    lambda p: p['operations'][0].update(target=quote('B2', 1)),
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
