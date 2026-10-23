"""Master 23: the router sees previous-turn ids only when a session has them; single-turn input is unchanged."""
import asyncio
import json

from backend.bintanong_routing.contracts import RequestContext
from backend.bintanong_routing.prompt import SYSTEM_PROMPT, build_messages, output_schema
from backend.bintanong_routing.router import Router
from test_routing_contracts import context
from test_routing_router import FakeTransport, style_proposal
from test_routing_validation import catalog, registry

FOLLOW_UP = 'What are its prerequisites?'
PREVIOUS = dict(program_id='program-a', curriculum_id='curriculum-a', course_id='course-a', subject_id=None)


def ctx(conversation=None):
    return RequestContext.parse(context(conversation=conversation))


def wire(**updates):
    its = dict(text='its', occurrence=0)
    value = dict(schema_version='bintanong-interpretation-wire-v4', language='en', audience='undergraduate',
                 control=None, part_count=1,
                 parts=[dict(part_id='r1', quote=its, evidence_need='structured', operation_indices=[0])],
                 intent='prerequisite_check', mentions=[dict(kind='course', quote=its)], claims=[],
                 operations=[dict(name='check_prerequisite_eligibility', target=its)], route='Symbolic',
                 ambiguities=[], previous_course_quote=its)
    value.update(updates)
    return json.dumps(value)


def route(conversation, output):
    transport = FakeTransport(output, style_outputs=[json.dumps(style_proposal('en', english=['prerequisites']))])
    result = asyncio.run(Router(transport, catalog=catalog(), registry=registry(), documents_available=True,
                                synthetic=True).route(FOLLOW_UP, ctx(conversation)))
    return result, transport.calls[0]


def test_single_turn_messages_and_schema_carry_no_follow_up_material():
    messages = build_messages('A1', ctx(), catalog(), registry())
    assert messages[0]['content'].startswith(SYSTEM_PROMPT) and 'previous' not in messages[0]['content'].split(
        'JSON schema:')[0][len(SYSTEM_PROMPT):]
    assert 'previous_turn' not in json.loads(messages[1]['content'])
    assert 'previous_course_quote' not in json.dumps(output_schema())


def test_stored_course_is_shown_by_its_printed_label_with_the_reference_field():
    messages = build_messages(FOLLOW_UP, ctx(PREVIOUS), catalog(), registry())
    assert json.loads(messages[1]['content'])['previous_turn'] == {'course': 'A1'}
    assert 'previous_course_quote' in messages[0]['content']
    assert 'previous_course_quote' in json.dumps(output_schema(follow_up=True))


def test_stored_course_outside_the_catalog_scope_is_not_shown():
    messages = build_messages(FOLLOW_UP, ctx(dict(PREVIOUS, course_id='course-z')), catalog(), registry())
    assert 'previous_turn' not in json.loads(messages[1]['content'])


def test_model_marked_reference_resolves_to_the_stored_course():
    result, (messages, schema) = route(PREVIOUS, wire())
    assert result.diagnostic == 'validated'
    assert {i.name: i.value for i in result.decision.predicate_request.inputs}['course_id'] == 'course-a'
    assert 'previous_course_quote' in json.dumps(schema)


def test_reference_without_stored_course_never_routes():
    result, _ = route(None, wire())
    assert result.decision.route is None
