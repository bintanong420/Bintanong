"""One chat turn (master 16.1, 23.3), independent of the HTTP transport.

The AI SDK client posts its whole message list, but only the last user message is used: the session's
structured conversation context carries follow-ups, never a transcript (master 23.2). A routing result
becomes the next turn's context only when the turn finishes; a cancelled or failed turn leaves nothing.
"""
from __future__ import annotations

import secrets
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from backend.bintanong_api.session import ApiError, Session
from backend.bintanong_private_context.conversation import capture, follow_up_context
from backend.bintanong_private_context.sessions import SessionStore

MAX_MESSAGES = 500


@dataclass(frozen=True)
class CurriculumOption:
    program_id: str
    curriculum_id: str
    program_name: str
    curriculum_name: str


class _Part(BaseModel):
    model_config = ConfigDict(extra='ignore')
    type: str
    text: str | None = None


class _Message(BaseModel):
    model_config = ConfigDict(extra='ignore')
    id: str = Field(min_length=1, max_length=128)
    role: Literal['system', 'user', 'assistant']
    parts: list[_Part]


class ChatRequest(BaseModel):
    """The AI SDK `DefaultChatTransport` body plus the student's chosen curriculum."""
    model_config = ConfigDict(extra='ignore')
    id: str | None = None
    messages: list[_Message] = Field(min_length=1, max_length=MAX_MESSAGES)
    trigger: Literal['submit-message', 'regenerate-message'] = 'submit-message'
    messageId: str | None = None
    programId: str | None = None
    curriculumId: str | None = None


@dataclass(frozen=True)
class PreparedTurn:
    text: str
    message_id: str
    program_id: str | None
    curriculum_id: str | None
    regenerate: bool


def _ignore(_stage: str) -> None:
    pass


class ChatTurns:
    def __init__(self, sessions: SessionStore, pipeline, curricula: tuple[CurriculumOption, ...]):
        self._sessions, self._pipeline = sessions, pipeline
        self._scopes = {(c.program_id, c.curriculum_id) for c in curricula}

    def prepare(self, request: ChatRequest) -> PreparedTurn:
        """Checks that need no session state, so they can be refused before a stream starts."""
        message = request.messages[-1]
        text = ' '.join(p.text for p in message.parts if p.type == 'text' and p.text).strip()
        if message.role != 'user' or not text:
            raise ApiError(422, 'empty_message')
        scope = self.checked_scope(request.programId, request.curriculumId, required=False)
        return PreparedTurn(text, message.id, *scope, regenerate=request.trigger == 'regenerate-message')

    def checked_scope(self, program_id: str | None, curriculum_id: str | None, *,
                      required: bool) -> tuple[str | None, str | None]:
        """A program and curriculum come together and must be listed (`GET /curricula`)."""
        if (program_id is None) != (curriculum_id is None) or (required and program_id is None):
            raise ApiError(422, 'incomplete_scope')
        if program_id is not None and (program_id, curriculum_id) not in self._scopes:
            raise ApiError(422, 'unknown_curriculum')
        return program_id, curriculum_id

    async def answer(self, session: Session, request: ChatRequest, progress=_ignore):
        return await self.run(session, self.prepare(request), progress)

    async def run(self, session: Session, turn: PreparedTurn, progress=_ignore):
        try:
            self._sessions.begin_turn(session.credential, turn.message_id, regenerate=turn.regenerate)
        except ValueError as refused:
            raise ApiError(409, str(refused)) from None
        context = follow_up_context(session.view, request_id=f'req-{secrets.token_hex(8)}',
                                    program_id=turn.program_id, curriculum_id=turn.curriculum_id)
        routed, completed = [], False
        try:
            try:
                result = await self._pipeline.run(turn.text, context, routed_sink=routed.append,
                                                  progress=progress)
            except Exception:
                raise ApiError(503, 'answer_unavailable') from None
            completed = True
        finally:
            self._sessions.end_turn(session.credential, turn.message_id, completed=completed)
        conversation = capture(routed[0]) if routed else None
        if conversation is not None:
            try:
                self._sessions.set_conversation(session.credential, conversation)
            except KeyError:  # deleted or expired during the turn; it stays gone
                pass
        return result
