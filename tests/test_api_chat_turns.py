"""Phase 11 chat turns (master 16.1, 23.3): last user message only, session context in and out, one turn
at a time, no capture from a cancelled or failed turn."""
import asyncio
import re

import pytest

from backend.bintanong_api.chat import ChatRequest, ChatTurns, CurriculumOption
from backend.bintanong_api.session import ApiError, Session
from backend.bintanong_private_context.conversation import capture
from backend.bintanong_private_context.sessions import SessionStore
from test_routing_contracts import context
from test_routing_validation import validate

CURRICULA = (CurriculumOption('program-a', 'curriculum-a', 'Program A', 'Curriculum A'),)


class Pipeline:
    """Stand-in for the answer pipeline: records what it was given and reports a routing result."""

    def __init__(self, routed=None, error=None, gate=None):
        self.calls, self.routed, self.error, self.gate = [], routed, error, gate

    async def run(self, text, ctx, *, routed_sink, progress):
        self.calls.append((text, ctx))
        if self.gate is not None:
            await self.gate.wait()
        if self.routed is not None:
            routed_sink(self.routed)
        if self.error is not None:
            raise self.error
        return f'answer to {text}'


def session(store):
    issued = store.issue()
    return Session(issued.credential, store.resolve(issued.credential))


def request(*texts, message_id='msg-1', trigger='submit-message', **scope):
    messages = [dict(id=f'm{i}', role='user' if i % 2 == 0 else 'assistant', parts=[dict(type='text', text=t)])
                for i, t in enumerate(texts)]
    messages[-1]['id'] = message_id
    return ChatRequest.model_validate(dict(id='chat-1', messages=messages, trigger=trigger, **scope))


def answer(turns, s, req):
    return asyncio.run(turns.answer(s, req))


def test_only_the_last_user_message_reaches_the_pipeline():
    store, pipeline = SessionStore(), Pipeline()
    s = session(store)
    assert answer(ChatTurns(store, pipeline, CURRICULA), s, request('first', 'reply', 'second')) == 'answer to second'
    assert [text for text, _ in pipeline.calls] == ['second']


def test_context_carries_the_session_a_fresh_request_id_and_the_chosen_scope():
    store, pipeline = SessionStore(), Pipeline()
    s = session(store)
    answer(ChatTurns(store, pipeline, CURRICULA), s,
           request('Can I take A1?', programId='program-a', curriculumId='curriculum-a'))
    ctx = pipeline.calls[0][1]
    assert ctx.session_id == s.view.session_id
    assert re.fullmatch(r'req-[a-z0-9-]+', ctx.request_id)
    assert (ctx.program_id, ctx.curriculum_id) == ('program-a', 'curriculum-a')


def test_validated_turn_becomes_the_session_conversation_and_reaches_the_next_turn():
    store = SessionStore()
    s = session(store)
    turns = ChatTurns(store, Pipeline(routed=validate()), CURRICULA)
    answer(turns, s, request('A1', programId='program-a', curriculumId='curriculum-a'))
    assert store.resolve(s.credential).conversation == capture(validate())
    follow = Pipeline()
    answer(ChatTurns(store, follow, CURRICULA), session_of(store, s), request('What are its prerequisites?',
                                                                             message_id='msg-2'))
    assert follow.calls[0][1].conversation == capture(validate())


def session_of(store, s):
    return Session(s.credential, store.resolve(s.credential))


def test_clarification_turn_keeps_the_earlier_context_for_the_reply():
    store = SessionStore()
    s = session(store)
    answer(ChatTurns(store, Pipeline(routed=validate()), CURRICULA), s, request('A1'))
    unvalidated = validate(ctx=context(program_id=None, curriculum_id=None))
    answer(ChatTurns(store, Pipeline(routed=unvalidated), CURRICULA), session_of(store, s),
           request('Which one?', message_id='msg-2'))
    assert store.resolve(s.credential).conversation == capture(validate())


@pytest.mark.parametrize('scope, code', [
    (dict(programId='program-a', curriculumId='curriculum-z'), 'unknown_curriculum'),
    (dict(programId='program-a'), 'incomplete_scope'),
    (dict(curriculumId='curriculum-a'), 'incomplete_scope'),
])
def test_scope_must_be_a_listed_curriculum(scope, code):
    store, pipeline = SessionStore(), Pipeline()
    with pytest.raises(ApiError) as raised:
        answer(ChatTurns(store, pipeline, CURRICULA), session(store), request('A1', **scope))
    assert (raised.value.status, raised.value.code) == (422, code)
    assert pipeline.calls == []


@pytest.mark.parametrize('texts', [('first', 'assistant last'), ('   ',)])
def test_request_without_a_last_user_text_is_refused(texts):
    store = SessionStore()
    with pytest.raises(ApiError) as raised:
        answer(ChatTurns(store, Pipeline(), CURRICULA), session(store), request(*texts))
    assert raised.value.code == 'empty_message'


def test_second_turn_while_one_runs_is_refused():
    store = SessionStore()
    s = session(store)

    async def scenario():
        gate = asyncio.Event()
        turns = ChatTurns(store, Pipeline(gate=gate), CURRICULA)
        first = asyncio.create_task(turns.answer(s, request('A1')))
        await asyncio.sleep(0)
        with pytest.raises(ApiError) as raised:
            await turns.answer(s, request('A1 again', message_id='msg-2'))
        gate.set()
        await first
        return raised.value

    error = asyncio.run(scenario())
    assert (error.status, error.code) == (409, 'chat_in_progress')


def test_answered_message_is_not_rerun_but_regenerate_is_allowed():
    store, pipeline = SessionStore(), Pipeline()
    s = session(store)
    turns = ChatTurns(store, pipeline, CURRICULA)
    answer(turns, s, request('A1'))
    with pytest.raises(ApiError) as raised:
        answer(turns, s, request('A1'))
    assert (raised.value.status, raised.value.code) == (409, 'already_answered')
    answer(turns, s, request('A1', trigger='regenerate-message'))
    assert len(pipeline.calls) == 2


def test_cancelled_turn_captures_nothing_and_can_be_retried():
    store = SessionStore()
    s = session(store)

    async def scenario():
        gate = asyncio.Event()
        task = asyncio.create_task(ChatTurns(store, Pipeline(routed=validate(), gate=gate), CURRICULA)
                                   .answer(s, request('A1')))
        await asyncio.sleep(0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(scenario())
    assert store.resolve(s.credential).conversation is None
    assert answer(ChatTurns(store, Pipeline(), CURRICULA), s, request('A1')) == 'answer to A1'


def test_pipeline_failure_is_a_typed_error_without_capture():
    store = SessionStore()
    s = session(store)
    turns = ChatTurns(store, Pipeline(routed=validate(), error=RuntimeError('model down')), CURRICULA)
    with pytest.raises(ApiError) as raised:
        answer(turns, s, request('A1'))
    assert (raised.value.status, raised.value.code) == (503, 'answer_unavailable')
    assert 'model down' not in str(raised.value)
    assert store.resolve(s.credential).conversation is None
    assert answer(ChatTurns(store, Pipeline(), CURRICULA), s, request('A1')) == 'answer to A1'


def test_session_deleted_during_the_turn_stays_deleted():
    store = SessionStore()
    s = session(store)

    class DeletingPipeline(Pipeline):
        async def run(self, text, ctx, *, routed_sink, progress):
            store.delete(s.credential)
            return await super().run(text, ctx, routed_sink=routed_sink, progress=progress)

    answer(ChatTurns(store, DeletingPipeline(routed=validate()), CURRICULA), s, request('A1'))
    assert len(store) == 0


def test_session_deleted_before_the_turn_starts_is_a_typed_error():
    store = SessionStore()
    s = session(store)
    store.delete(s.credential)  # e.g. DELETE /session raced the chat request after its cookie was resolved
    pipeline = Pipeline()
    with pytest.raises(ApiError) as raised:
        answer(ChatTurns(store, pipeline, CURRICULA), s, request('A1'))
    assert (raised.value.status, raised.value.code) == (409, 'session_ended')
    assert pipeline.calls == [] and len(store) == 0


@pytest.mark.parametrize('text', ['x' * 8193, chr(0x20ac) * 6000, 'CC 5' + chr(0x200b) + '?'],
                         ids=['chars', 'utf8-bytes', 'format-char'])
def test_message_the_router_would_refuse_is_a_422_before_any_answer_work(text):
    # Security review S4: these used to fail late, inside the stream, as answer_unavailable.
    turns = ChatTurns(SessionStore(), Pipeline(), CURRICULA)
    with pytest.raises(ApiError) as raised:
        turns.prepare(request(text))
    assert (raised.value.status, raised.value.code) == (422, 'invalid_message')


# Memory/eligibility plan, Task 2: stated results and the waiting check carry across turns of one chat only.
from types import SimpleNamespace

from test_routing_contracts import proposal

LABELS = {'course-a': 'A 1', 'course-b': 'B 1'}
SCOPE = dict(programId='program-a', curriculumId='curriculum-a')


class Answering(Pipeline):
    def __init__(self, routed=None, result=None, **options):
        super().__init__(routed=routed, **options)
        self.result = result

    async def run(self, text, ctx, *, routed_sink, progress):
        await super().run(text, ctx, routed_sink=routed_sink, progress=progress)
        return self.result


def checked(session_id, text='Natake ko na yung A1. Can I take B1?', state='passed', curriculum='curriculum-a'):
    """The routing result of a check on B1 whose text states a result for A1."""
    start, target = text.index('A1'), text.rindex('B1')
    value = proposal(text=text, mentions=[dict(kind='course', text='A1', start=start, end=start + 2),
                                          dict(kind='course', text='B1', start=target, end=target + 2)],
                     claims=[dict(entity=0, state=state, mode='asserted', text=text, start=0, end=len(text))],
                     operations=[dict(name='check_prerequisite_eligibility', target=1)])
    value['parts'] = [dict(part_id='r1', text=text, start=0, end=len(text), evidence_need='structured',
                           operation_indices=[0])]
    return validate(text, value, context(session_id=session_id, curriculum_id=curriculum))


def waiting_on(course='course-a'):
    return SimpleNamespace(decision=SimpleNamespace(outcome='unknown', missing_facts=(f'completion_unknown:{course}',),
                                                    unknown_conditions=()))


def turn(store, s, pipeline, text, message_id, **scope):
    return answer(ChatTurns(store, pipeline, CURRICULA, course_labels=LABELS), session_of(store, s),
                  request(text, message_id=message_id, **(scope or SCOPE)))


def test_a_bare_reply_reruns_the_waiting_check_and_the_result_is_remembered_for_later_turns():
    store = SessionStore()
    s = session(store)
    turn(store, s, Answering(checked(s.view.session_id), waiting_on()), 'Natake ko na yung A1. Can I take B1?', 'msg-1')
    view = store.resolve(s.credential)
    assert [(f.course_id, f.state, f.source) for f in view.facts] == [('course-a', 'taken_unknown', 'user_statement')]
    assert (view.pending_check.course_id, view.pending_check.target_course_id) == ('course-a', 'course-b')

    reply = Answering()
    turn(store, s, reply, 'Oo, pasado.', 'msg-2')
    text, ctx = reply.calls[0]
    assert text == 'Pwede ko na bang i-take ang B 1?'
    assert [(f.course_id, f.state) for f in ctx.facts] == [('course-a', 'passed')]
    view = store.resolve(s.credential)
    assert [(f.course_id, f.state) for f in view.facts] == [('course-a', 'passed')] and view.pending_check is None

    turn(store, s, Answering(), 'Where is the registrar?', 'msg-3')   # an unrelated question in between
    later = Answering()
    turn(store, s, later, 'Pasok ba ako sa prerequisites ng B1?', 'msg-4')
    assert later.calls[0][0] == 'Pasok ba ako sa prerequisites ng B1?'
    assert [(f.course_id, f.state) for f in later.calls[0][1].facts] == [('course-a', 'passed')]


def test_a_fresh_chat_remembers_nothing():
    store = SessionStore()
    s = session(store)
    turn(store, s, Answering(checked(s.view.session_id), waiting_on()), 'Natake ko na yung A1. Can I take B1?', 'msg-1')
    fresh = session(store)
    pipeline = Answering()
    turn(store, fresh, pipeline, 'Oo, pasado.', 'msg-1')
    assert pipeline.calls[0][0] == 'Oo, pasado.' and pipeline.calls[0][1].facts == ()


def test_a_curriculum_switch_before_the_reply_carries_no_fact_and_no_question():
    store = SessionStore()
    s = session(store)
    turns = (CurriculumOption('program-a', 'curriculum-a', 'A', 'A'), CurriculumOption('program-a', 'curriculum-z', 'A', 'Z'))
    answer(ChatTurns(store, Answering(checked(s.view.session_id), waiting_on()), turns, course_labels=LABELS), s,
           request('Natake ko na yung A1. Can I take B1?', **SCOPE))
    switched = Answering()
    answer(ChatTurns(store, switched, turns, course_labels=LABELS), session_of(store, s),
           request('Oo, pasado.', message_id='msg-2', programId='program-a', curriculumId='curriculum-z'))
    text, ctx = switched.calls[0]
    assert text == 'Oo, pasado.' and ctx.facts == ()
    assert [(f.curriculum_id, f.state) for f in store.resolve(s.credential).facts] == [('curriculum-a', 'taken_unknown')]


def test_a_failed_reply_turn_commits_no_partial_memory():
    store = SessionStore()
    s = session(store)
    turn(store, s, Answering(checked(s.view.session_id), waiting_on()), 'Natake ko na yung A1. Can I take B1?', 'msg-1')
    with pytest.raises(ApiError):
        turn(store, s, Answering(error=RuntimeError('model down')), 'Oo, pasado.', 'msg-2')
    view = store.resolve(s.credential)
    assert [f.state for f in view.facts] == ['taken_unknown'] and view.pending_check is not None


def test_a_correction_replaces_the_earlier_self_report_and_regeneration_does_not_duplicate_it():
    store = SessionStore()
    s = session(store)
    sid = s.view.session_id
    turn(store, s, Answering(checked(sid, 'I passed A1. Can I take B1?')), 'I passed A1. Can I take B1?', 'msg-1')
    corrected = checked(sid, 'Sorry, I failed A1. Can I take B1?', state='failed')
    turn(store, s, Answering(corrected), 'Sorry, I failed A1. Can I take B1?', 'msg-2')
    answer(ChatTurns(store, Answering(corrected), CURRICULA, course_labels=LABELS), session_of(store, s),
           request('Sorry, I failed A1. Can I take B1?', message_id='msg-2', trigger='regenerate-message', **SCOPE))
    assert [(f.course_id, f.state) for f in store.resolve(s.credential).facts] == [('course-a', 'failed')]
