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


def test_turn_with_a_check_keeps_the_course_it_asked_about_not_the_other_one_mentioned():
    # "Can I take B1? I passed A1." -> a later "it" means B1, the course asked about (owner, 23 Oct 2026).
    value = proposal(text='A1 B1', mentions=[dict(kind='course', text='A1', start=0, end=2),
                                             dict(kind='course', text='B1', start=3, end=5)],
                     operations=[dict(name='check_prerequisite_eligibility', target=1)])
    assert capture(validate('A1 B1', value)).course_id == 'course-b'


def test_turn_without_a_check_naming_two_courses_keeps_no_course_so_its_cannot_pick_one():
    value = proposal(text='A1 B1 policy', mentions=[dict(kind='course', text='A1', start=0, end=2),
                                                    dict(kind='course', text='B1', start=3, end=5)],
                     operations=[], route='RAG')
    assert capture(validate('A1 B1 policy', value)).course_id is None


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


def test_follow_up_context_keeps_the_previous_turn_without_forcing_its_scope():
    store = SessionStore()
    a = store.issue()
    store.set_conversation(a.credential, previous())
    ctx = follow_up_context(store.resolve(a.credential), request_id='req-2')
    assert isinstance(ctx, RequestContext)
    assert (ctx.program_id, ctx.curriculum_id, ctx.conversation) == (None, None, previous())
    explicit = follow_up_context(store.resolve(a.credential), request_id='req-3', program_id='program-b')
    assert (explicit.program_id, explicit.curriculum_id) == ('program-b', None)


def test_carried_scope_fills_in_when_the_follow_up_names_none():
    unscoped = context(program_id=None, curriculum_id=None, conversation=previous().model_dump(mode='json'))
    value = proposal(text=FOLLOW_UP, mentions=[dict(kind='course', **ITS)], context_reference=ITS)
    result = validate(FOLLOW_UP, value, unscoped)
    assert result.diagnostic == 'validated' and result.curriculum_id == 'curriculum-a'


def other_program_catalog():
    from backend.bintanong_routing.contracts import CatalogEntry
    def item(kind, entity, alias, program, curriculum):
        return CatalogEntry.parse(dict(kind=kind, entity_id=entity, program_id=program, curriculum_id=curriculum,
            aliases=[alias], source_ref='ver-a', review_ref='review-a', reviewed=True))
    return (entry(), item('program', 'program-b', 'Program B', 'program-b', None),
            item('curriculum', 'curriculum-b', 'Edition B', 'program-b', 'curriculum-b'),
            item('course', 'course-z', 'Z1', 'program-b', 'curriculum-b'))


def test_unrelated_new_question_about_another_program_is_not_blocked_by_the_previous_turn():
    text = 'Program B Z1'
    value = proposal(text=text, mentions=[dict(kind='program', text='Program B', start=0, end=9),
                                          dict(kind='course', text='Z1', start=10, end=12)],
                     operations=[dict(name='check_prerequisite_eligibility', target=1)])
    unscoped = context(program_id=None, curriculum_id=None, conversation=previous().model_dump(mode='json'))
    result = validate(text, value, unscoped, catalog=other_program_catalog())
    assert result.diagnostic == 'validated' and result.curriculum_id == 'curriculum-b'
    assert {i.name: i.value for i in result.decision.predicate_request.inputs}['course_id'] == 'course-z'


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


def test_unrelated_document_question_does_not_inherit_the_previous_course_scope():
    value = proposal(text='policy', mentions=[], operations=[], route='RAG')
    unscoped = context(program_id=None, curriculum_id=None, conversation=previous().model_dump(mode='json'))
    result = validate('policy', value, unscoped)
    assert result.diagnostic == 'validated' and (result.program_id, result.curriculum_id) == (None, None)


def test_a_named_course_marked_as_a_back_reference_resolves_to_the_named_course():
    # Live F5: "What about CC 4?" had "CC 4" marked as the reference and was answered for CC 5.
    text = 'What about B1?'
    b1 = dict(text='B1', start=11, end=13)
    value = proposal(text=text, mentions=[dict(kind='course', **b1)], context_reference=b1)
    result = validate(text, value, context(conversation=previous().model_dump(mode='json')))
    assert result.diagnostic == 'validated'
    assert {i.name: i.value for i in result.decision.predicate_request.inputs}['course_id'] == 'course-b'
