"""Phase 11 master 16.3: FastAPI -> AI SDK UI message stream (protocol v1, chunk shapes of `ai` 7.0.150).

No draft text is streamed: transient progress first, then one validated student text, its sources, and finish.
"""
import asyncio
import json

import pytest
from fastapi.testclient import TestClient

from backend.bintanong_api.app import ApiServices, ApiSettings, create_app
from backend.bintanong_api.chat import ChatRequest, ChatTurns, CurriculumOption
from backend.bintanong_api.presentation import student_text
from backend.bintanong_api.session import Session
from backend.bintanong_api.stream import DONE, STREAM_HEADERS, answer_parts, chat_stream, encode
from backend.bintanong_private_context.sessions import SessionStore
from test_api_presentation import answer_for
from test_routing_validation import validate

ORIGIN = 'https://bintanong.example'
CURRICULA = (CurriculumOption('program-a', 'curriculum-a', 'Program A', 'Curriculum A'),)
# Required fields per chunk type in ai 7.0.150 (src/ui-message-stream/ui-message-chunks.ts).
REQUIRED = {'start': set(), 'text-start': {'id'}, 'text-delta': {'id', 'delta'}, 'text-end': {'id'},
            'source-document': {'sourceId', 'mediaType', 'title'}, 'error': {'errorText'}, 'finish': set()}


def assert_protocol(part):
    kind = part['type']
    required = {'data'} if kind.startswith('data-') else REQUIRED[kind]
    assert required <= part.keys(), part
    assert all(isinstance(part[k], str) for k in required - {'data'}), part


class Pipeline:
    def __init__(self, answer=None, error=None, gate=None, routed=None):
        self.answer, self.error, self.gate, self.routed = answer, error, gate, routed

    async def run(self, text, ctx, *, routed_sink, progress):
        progress('understanding')
        if self.gate is not None:
            await self.gate.wait()
        if self.routed is not None:
            routed_sink(self.routed)
        progress('writing')
        if self.error is not None:
            raise self.error
        return self.answer


def body(text='A1 policy', message_id='msg-1', **extra):
    return dict(id='chat-1', trigger='submit-message',
                messages=[dict(id=message_id, role='user', parts=[dict(type='text', text=text)])], **extra)


def parse(raw: bytes):
    events = [e for e in raw.decode('utf-8').split('\n\n') if e]
    assert all(e.startswith('data: ') for e in events), events
    assert events[-1] == 'data: [DONE]'
    return [json.loads(e[len('data: '):]) for e in events[:-1]]


def app_with(pipeline, store=None):
    store = SessionStore() if store is None else store
    return create_app(ApiServices(sessions=store, curricula=CURRICULA, pipeline=pipeline),
                      ApiSettings(allowed_origins=(ORIGIN,))), store


def client(app):
    return TestClient(app, base_url='https://testserver', headers={'Origin': ORIGIN})


def test_encoding_is_one_compact_sse_data_line_per_chunk():
    assert encode({'type': 'text-delta', 'id': 't', 'delta': 'Pañuelo'}) == \
        'data: {"type":"text-delta","id":"t","delta":"Pañuelo"}\n\n'.encode('utf-8')
    assert DONE == b'data: [DONE]\n\n'
    assert STREAM_HEADERS['x-vercel-ai-ui-message-stream'] == 'v1'


def test_answer_parts_carry_the_student_text_sources_and_finish():
    answer = answer_for('Hybrid')
    parts = answer_parts(answer, 'msg-a')
    for part in parts:
        assert_protocol(part)
    kinds = [p['type'] for p in parts]
    assert kinds[:3] == ['text-start', 'text-delta', 'text-end']
    assert parts[1]['delta'] == student_text(answer)
    sources = [p for p in parts if p['type'] == 'source-document']
    assert [s['sourceId'] for s in sources] == [c.evidence_id for c in answer.citations]
    assert all('ev-' not in s['title'] for s in sources)
    summary = next(p for p in parts if p['type'] == 'data-answer')
    assert summary['data'] == {'status': 'answered', 'conditional': True,
                               'language': 'taglish', 'missingFields': []}
    assert kinds[-1] == 'finish' and parts[-1]['finishReason'] == 'stop'


def test_chat_streams_progress_then_the_validated_answer():
    answer = answer_for('RAG')
    app, _ = app_with(Pipeline(answer))
    response = client(app).post('/chat', json=body())
    assert response.status_code == 200
    assert response.headers['x-vercel-ai-ui-message-stream'] == 'v1'
    assert response.headers['content-type'].startswith('text/event-stream')
    assert response.headers['set-cookie'].startswith('__Host-bintanong_session=')
    parts = parse(response.content)
    for part in parts:
        assert_protocol(part)
    kinds = [p['type'] for p in parts]
    assert kinds[0] == 'start'
    status = [p for p in parts if p['type'] == 'data-status']
    assert [p['data']['stage'] for p in status] == ['understanding', 'writing']
    assert all(p['transient'] is True for p in status)
    assert kinds.index('data-status') < kinds.index('text-start')
    assert next(p['delta'] for p in parts if p['type'] == 'text-delta') == student_text(answer)
    assert answer.text not in response.text  # the researcher text never reaches the student


def test_failure_after_the_stream_starts_is_an_error_chunk_without_text():
    app, _ = app_with(Pipeline(error=RuntimeError('secret detail')))
    response = client(app).post('/chat', json=body())
    parts = parse(response.content)
    assert [p['type'] for p in parts if p['type'] != 'data-status'] == ['start', 'error']
    assert parts[-1]['errorText'] == 'answer_unavailable'
    assert 'secret detail' not in response.text


def test_invalid_request_is_refused_before_streaming():
    app, store = app_with(Pipeline(answer_for('RAG')))
    response = client(app).post('/chat', json=body(programId='program-a', curriculumId='curriculum-z'))
    assert response.status_code == 422
    assert response.json() == {'error': 'unknown_curriculum'}


def test_malformed_body_is_a_plain_422():
    app, _ = app_with(Pipeline(answer_for('RAG')))
    response = client(app).post('/chat', json={'messages': []})
    assert response.status_code == 422


def test_chat_requires_an_allowed_origin():
    app, store = app_with(Pipeline(answer_for('RAG')))
    response = TestClient(app, base_url='https://testserver').post('/chat', json=body())
    assert response.status_code == 403 and len(store) == 0


def test_repeating_an_answered_message_streams_already_answered():
    app, _ = app_with(Pipeline(answer_for('RAG')))
    c = client(app)
    parse(c.post('/chat', json=body()).content)
    parts = parse(c.post('/chat', json=body()).content)
    assert parts[-1] == {'type': 'error', 'errorText': 'already_answered'}


def test_follow_up_over_http_uses_the_stored_conversation():
    seen = []

    class Recording(Pipeline):
        async def run(self, text, ctx, *, routed_sink, progress):
            seen.append(ctx.conversation)
            return await super().run(text, ctx, routed_sink=routed_sink, progress=progress)

    app, _ = app_with(Recording(answer_for('RAG'), routed=validate()))
    c = client(app)
    parse(c.post('/chat', json=body('A1', programId='program-a', curriculumId='curriculum-a')).content)
    parse(c.post('/chat', json=body('What are its prerequisites?', message_id='msg-2')).content)
    assert seen[0] is None and seen[1].course_id == 'course-a'


def test_disconnect_cancels_the_turn_and_keeps_nothing():
    store = SessionStore()
    issued = store.issue()
    session = Session(issued.credential, store.resolve(issued.credential))
    answer = answer_for('RAG')

    async def scenario():
        gate = asyncio.Event()
        turns = ChatTurns(store, Pipeline(answer, gate=gate, routed=validate()), CURRICULA)
        request = ChatRequest.model_validate(body())
        stream = chat_stream(turns, session, turns.prepare(request))
        first = await stream.__anext__()
        assert json.loads(first[len(b'data: '):])['type'] == 'start'
        await stream.__anext__()  # 'understanding' progress: the pipeline is now waiting
        loop = asyncio.get_running_loop()
        started = loop.time()
        await asyncio.wait_for(stream.aclose(), 5)  # what Starlette does when the client goes away
        assert loop.time() - started < 1, 'the turn was not cancelled; it ran until the timeout'

    asyncio.run(scenario())
    assert store.resolve(issued.credential).conversation is None
    store.begin_turn(issued.credential, 'msg-1')  # not stuck in flight, and not marked answered


def test_answers_past_the_model_capacity_wait_in_a_short_queue_then_get_busy():
    # Owner, 24 Oct 2026: Gemma serves one request at a time; a short queue with a waiting status, then busy.
    import threading
    import time
    started, release = threading.Event(), threading.Event()
    answer = answer_for('RAG')  # built outside the event loop (it runs one itself)

    class OneSlotModel:
        def __init__(self):
            self.running = self.peak = self.calls = 0

        async def run(self, text, ctx, *, routed_sink, progress):
            self.calls += 1
            self.running += 1
            self.peak = max(self.peak, self.running)
            started.set()
            await asyncio.to_thread(release.wait, 10)
            self.running -= 1
            return answer
    model = OneSlotModel()
    app = create_app(ApiServices(sessions=SessionStore(), curricula=CURRICULA, pipeline=model),
                     ApiSettings(allowed_origins=(ORIGIN,), max_running_answers=1, max_waiting_answers=1))
    results = {}

    def ask(name, c):
        results[name] = c.post('/chat', json=body())
    # One client = one event loop, as under uvicorn. Its cookie jar fills only when a response ends, so each
    # concurrent request below arrives without a cookie and gets its own session.
    with client(app) as c:
        running = threading.Thread(target=ask, args=('running', c))
        running.start()
        assert started.wait(10)
        waiting = threading.Thread(target=ask, args=('waiting', c))
        waiting.start()
        deadline = time.monotonic() + 10
        while app.state.admission.admitted < 2 and time.monotonic() < deadline:
            time.sleep(0.01)
        busy = c.post('/chat', json=body())
        release.set()
        running.join(10)
        waiting.join(10)
        c.cookies.clear()
        afterwards = c.post('/chat', json=body(message_id='msg-2'))
    assert (busy.status_code, busy.json()) == (503, {'error': 'answers_busy'})
    stages = [p['data']['stage'] for p in parse(results['waiting'].content) if p['type'] == 'data-status']
    assert stages[0] == 'waiting'
    for response in (results['running'], results['waiting'], afterwards):
        assert response.status_code == 200 and any(p['type'] == 'text-delta' for p in parse(response.content))
    assert model.peak == 1 and model.calls == 3
