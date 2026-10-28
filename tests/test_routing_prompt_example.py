"""Shipped example coherence and dispatch guards; never model-accuracy evidence."""
import asyncio
from copy import deepcopy
import json

from jsonschema import Draft202012Validator
import pytest

from backend.bintanong_contracts.symbolic import EMPTY_REGISTRY
from backend.bintanong_routing import prompt
from backend.bintanong_routing.contracts import RequestContext
from backend.bintanong_routing.router import Router
from backend.bintanong_routing.wire import WireInterpretation, normalize_interpretation
from test_routing_validation import entry, registry
from test_routing_wire_boundary import Model


def example():
    context = RequestContext(session_id='sess-example', request_id='req-example',
        program_id='program-a', curriculum_id='curriculum-a')
    messages = prompt.build_messages('Hello', context, (), EMPTY_REGISTRY)
    marker = 'BEGIN FICTIONAL EXAMPLE\n'
    assert marker in messages[0]['content'], 'Model-visible worked example missing'
    value = json.loads(messages[0]['content'].split(marker, 1)[1].split(
        '\nEND FICTIONAL EXAMPLE', 1)[0])
    return value, context


def test_shipped_example_has_grounded_distinct_parts_and_coherent_target_condition():
    value, _ = example()
    packet = value['interpretation']
    Draft202012Validator(prompt.output_schema()).validate(packet)
    normalized = normalize_interpretation(value['original_text'], WireInterpretation.parse(packet))
    assert [p.text for p in normalized.parts] == [
        'After failing M4, can I take N8', 'where do I submit ticket R', 'what is the fee?']
    assert [p.evidence_need for p in normalized.parts] == ['structured', 'document', 'document']
    assert [p.operation_indices for p in normalized.parts] == [(0,), (), ()]
    assert normalized.mentions[normalized.operations[0].target].text == 'N8'
    claim = normalized.claims[0]
    assert normalized.mentions[claim.entity].text == 'M4'
    assert (claim.text, claim.state, claim.mode) == ('failing M4', 'failed', 'asserted')
    assert all(a.end <= b.start for a, b in zip(normalized.parts, normalized.parts[1:]))


def route_example(mode='asserted'):
    value, context = example()
    packet = deepcopy(value['interpretation'])
    packet['claims'][0]['mode'] = mode
    style = dict(schema_version='bintanong-response-style-v2', style=dict(
        english_fragments=['can I take N8'], filipino_fragments=[], preferred_response_style='english_only'))
    model = Model(packet, style)
    router = Router(model, catalog=(entry(alias='M4'), entry(entity='course-b', alias='N8')),
        registry=registry(), documents_available=True, synthetic=True)
    return asyncio.run(router.route(value['original_text'], context)), model


def test_shipped_example_dispatches_scoped_target_and_request_local_failure():
    result, model = route_example()
    assert result.diagnostic == 'validated' and result.decision.route == 'Hybrid'
    assert {i.name: i.value for i in result.decision.predicate_request.inputs} == {
        'curriculum_id': 'curriculum-a', 'course_id': 'course-b'}
    assert [(c.course_id, c.state, c.mode) for c in result.claims] == [('course-a', 'failed', 'asserted')]
    assert len(model.calls) == 2 and result.repair_attempts == 0


@pytest.mark.parametrize('mode', ['hypothetical', 'reported'])
def test_nonasserted_variant_of_shipped_example_stays_guarded(mode):
    result, model = route_example(mode)
    assert result.claims[0].mode == mode
    assert result.diagnostic == 'nonasserted_facts' and not result.decision.dispatchable
    assert len(model.calls) == 2 and result.repair_attempts == 0


def test_router_prompt_maps_not_yet_passed_and_not_taken_to_a_failed_claim():
    # Gate run 1 (28 Oct 2026): "... kahit hindi ko pa naipapasa ang Y?" kept the check but dropped the statement in
    # all 7 curricula (English "if I failed Y" passed). failed means not completed for the engine.
    from backend.bintanong_routing import prompt
    text = prompt.SYSTEM_PROMPT
    assert 'not yet passed' in text and 'not taken' in text and 'state failed' in text
    assert prompt.PROMPT_VERSION == 'bintanong-router-p11-v25'


def test_router_prompt_treats_meeting_a_printed_rule_as_a_specific_detail():
    # Gate 28 Oct 2026: getting off probation / honors residence asked one printed rule but were labelled whole, so a
    # multi-record Handbook topic needed every record and abstained. Steps stay whole; examples are fictional.
    from backend.bintanong_routing import prompt
    text = prompt.TOPIC_INSTRUCTION
    assert 'meet a condition' in text and 'printed rule' in text and 'not a list of steps' in text
    assert 'fictional waitlist' in text
    assert prompt.PROMPT_VERSION == 'bintanong-router-p11-v25'
