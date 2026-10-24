"""FastAPI -> Vercel AI SDK UI message stream, protocol v1 (master 16.3; chunk shapes of `ai` 7.0.150).

No draft text is streamed (master 16.2): transient `data-status` progress (`waiting` while queued for the model),
then one validated student text,
its sources, a `data-answer` summary and `finish`. Failures after the stream starts become an `error` chunk.
A client disconnect closes this generator, which cancels the turn, so nothing is captured from it.
"""
from __future__ import annotations

import asyncio
import contextlib
import json
import secrets

from backend.bintanong_api.chat import ChatTurns, PreparedTurn
from backend.bintanong_api.presentation import student_text
from backend.bintanong_api.session import ApiError, Session

STREAM_HEADERS = {'x-vercel-ai-ui-message-stream': 'v1', 'cache-control': 'no-cache', 'x-accel-buffering': 'no'}
DONE = b'data: [DONE]\n\n'
_SOURCE = 'Institutional source'


def encode(part: dict) -> bytes:
    return b'data: ' + json.dumps(part, ensure_ascii=False, separators=(',', ':')).encode('utf-8') + b'\n\n'


def _title(card) -> str:
    cite = card.citations[0] if card.citations else None
    return _SOURCE if cite is None else f'{cite.filename or _SOURCE}, p.{cite.page}'


def answer_parts(answer, message_id: str) -> list[dict]:
    text_id = f'{message_id}-text'
    parts = [{'type': 'text-start', 'id': text_id},
             {'type': 'text-delta', 'id': text_id, 'delta': student_text(answer)},
             {'type': 'text-end', 'id': text_id}]
    parts += [{'type': 'source-document', 'sourceId': card.evidence_id, 'mediaType': 'text/plain',
               'title': _title(card)} for card in answer.citations]
    # A Prolog decision always rests on facts the student supplied, so it is shown as conditional (master 16.2).
    parts.append({'type': 'data-answer', 'data': {'status': answer.status,
                                                  'conditional': answer.decision is not None}})
    parts.append({'type': 'finish', 'finishReason': 'stop'})
    return parts


async def chat_stream(turns: ChatTurns, session: Session, turn: PreparedTurn, sources=None, reservation=None):
    message_id = f'msg-{secrets.token_hex(8)}'
    yield encode({'type': 'start', 'messageId': message_id})
    queue: asyncio.Queue = asyncio.Queue()

    def progress(stage: str) -> None:
        queue.put_nowait({'type': 'data-status', 'data': {'stage': stage}, 'transient': True})

    async def admitted_turn():
        if reservation is None:
            return await turns.run(session, turn, progress=progress)
        async with reservation.running(progress):
            return await turns.run(session, turn, progress=progress)

    task = asyncio.create_task(admitted_turn())
    try:
        while not task.done() or not queue.empty():
            if not queue.empty():
                yield encode(queue.get_nowait())
                continue
            getter = asyncio.ensure_future(queue.get())
            await asyncio.wait({task, getter}, return_when=asyncio.FIRST_COMPLETED)
            if getter.done():
                yield encode(getter.result())
            else:
                getter.cancel()
        try:
            answer = task.result()
        except ApiError as error:
            yield encode({'type': 'error', 'errorText': error.code})
            yield DONE
            return
        if sources is not None:
            sources.remember(answer.citations)
        for part in answer_parts(answer, message_id):
            yield encode(part)
        yield DONE
    finally:
        if not task.done():
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task
