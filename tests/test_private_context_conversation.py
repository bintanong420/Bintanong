"""Phase 10 / master 23: session-only conversation context and host-checked follow-up references."""
import pytest

from backend.bintanong_private_context.conversation import capture, follow_up_context
from backend.bintanong_private_context.sessions import SessionStore
from backend.bintanong_routing.contracts import ConversationContext, RequestContext
from test_routing_contracts import context, proposal
from test_routing_validation import entry, validate

FOLLOW_UP = 'What are its prerequisites?'
ITS = dict(text='its', start=9, end=12)


def previous(course='course-a', **updates):
    value = dict(program_id='program-a', curriculum_id='curriculum-a', course_id=course, subject_id=None)
    value.update(updates)
    return ConversationContext.parse(value)


def follow_up(conversation, value=None, **options):
    value = value or proposal(text=FOLLOW_UP, mentions=[dict(kind='course', **ITS)], context_reference=ITS)
    return validate(FOLLOW_UP, value, context(conversation=conversation and conversation.model_dump(mode='json')),
                    **options)


def test_validated_single_course_answer_is_captured_as_ids_only():
    assert capture(validate()) == previous()


def test_turn_with_two_courses_keeps_no_course_so_its_cannot_pick_one():
    value = proposal(text='A1 B1', mentions=[dict(kind='course', text='A1', start=0, end=2),
                                             dict(kind='course', text='B1', start=3, end=5)])
    assert capture(validate('A1 B1', value)).course_id is None


def test_unvalidated_turn_is_not_captured():
    assert capture(validate(ctx=context(program_id=None, curriculum_id=None))) is None  # missing scope


def test_document_answer_keeps_its_subject():
    value = proposal(text='policy', mentions=[], operations=[], route='RAG',
                     parts=[dict(part_id='r1', text='policy', start=0, end=6, evidence_need='document',
                                 operation_indices=[], subject_id='subject_a', requested_claims=['fee'])])
    assert capture(validate('policy', value)).subject_id == 'subject_a'


def test_its_resolves_to_the_stored_course_through_the_host():
    result = follow_up(previous())
    assert result.diagnostic == 'validated'
    assert {i.name: i.value for i in result.decision.predicate_request.inputs}['course_id'] == 'course-a'


def test_reference_without_a_stored_course_clarifies():
    assert follow_up(None).diagnostic == 'unresolved_entity'
    assert follow_up(previous(course=None)).diagnostic == 'unresolved_entity'


def test_stored_course_outside_the_current_curriculum_clarifies():
    result = follow_up(previous(), catalog=(entry(), entry(entity='course-z', alias='Z1', curriculum='curriculum-b')))
    assert result.diagnostic == 'validated'
    other = follow_up(previous(course='course-z'),
                      catalog=(entry(), entry(entity='course-z', alias='Z1', curriculum='curriculum-b')))
    assert other.diagnostic == 'unresolved_entity'


def test_reference_quote_must_be_in_the_message():
    value = proposal(text=FOLLOW_UP, mentions=[dict(kind='course', **ITS)],
                     context_reference=dict(text='that', start=9, end=13))
    with pytest.raises(ValueError):
        follow_up(previous(), value)


def test_follow_up_context_carries_scope_and_only_matching_facts():
    store = SessionStore()
    a = store.issue()
    store.set_conversation(a.credential, previous())
    ctx = follow_up_context(store.resolve(a.credential), request_id='req-2')
    assert isinstance(ctx, RequestContext)
    assert (ctx.program_id, ctx.curriculum_id, ctx.conversation) == ('program-a', 'curriculum-a', previous())
    explicit = follow_up_context(store.resolve(a.credential), request_id='req-3', program_id='program-b')
    assert (explicit.program_id, explicit.curriculum_id) == ('program-b', None)


def test_conversation_context_is_isolated_and_deleted_with_its_session():
    store = SessionStore()
    a, b = store.issue(), store.issue()
    store.set_conversation(a.credential, previous())
    assert store.resolve(b.credential).conversation is None
    assert store.resolve(a.credential).conversation == previous()
    store.delete(a.credential)
    assert store.resolve(a.credential) is None


def test_orchestrator_hands_the_routed_result_to_the_host_for_capture():
    import asyncio
    from test_orchestration_pipeline import api, ports, resources, ctx, transport
    routed = []
    provider = ports().SyntheticReleaseProvider(resources())
    result = asyncio.run(api().Orchestrator(transport(), releases=provider).run('A1', ctx('a', 'passed'),
                                                                               routed_sink=routed.append))
    assert result.status == 'ready' and len(routed) == 1
    assert capture(routed[0]) == previous()


def test_orchestrator_without_a_sink_behaves_as_before():
    import asyncio
    from test_orchestration_pipeline import api, ports, resources, ctx, transport
    provider = ports().SyntheticReleaseProvider(resources())
    assert asyncio.run(api().Orchestrator(transport(), releases=provider).run('A1', ctx('a', 'passed'))).status == 'ready'
