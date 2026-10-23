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
