"""One chat turn (master 16.1, 23.3), independent of the HTTP transport.

The client message list supplies only the current utterance. Bounded server-owned exchanges are kept
ephemerally, separate from accepted academic facts. Facts, dialogue and legacy follow-up context commit
together only after a completed turn; a cancelled or failed turn leaves nothing.
"""
from __future__ import annotations

import secrets
from dataclasses import dataclass, replace
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from backend.bintanong_api.session import ApiError, Session
from backend.bintanong_private_context.conversation import capture, capture_request, follow_up_context
from backend.bintanong_private_context.memory import (accepted_facts, bind_reply, merge_facts, pending_from,
                                                     turn_ref)
from backend.bintanong_private_context.sessions import SessionStore
from backend.bintanong_private_context.dialogue import (DialogueEntity, DialogueExchange, UnresolvedDialogue,
                                                       bounded_text)
from backend.bintanong_routing.contracts import DialogueDocument, prepare_query

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
    def __init__(self, sessions: SessionStore, pipeline, curricula: tuple[CurriculumOption, ...],
                 course_labels=None):
        self._sessions, self._pipeline = sessions, pipeline
        self._labels = dict(course_labels or {})  # course id -> printed code, for asking a waiting check again
        self._scopes = {(c.program_id, c.curriculum_id) for c in curricula}

    def prepare(self, request: ChatRequest) -> PreparedTurn:
        """Checks that need no session state, so they can be refused before a stream starts."""
        message = request.messages[-1]
        text = ' '.join(p.text for p in message.parts if p.type == 'text' and p.text).strip()
        if message.role != 'user' or not text:
            raise ApiError(422, 'empty_message')
        try:
            prepare_query(text)  # the router's own length and character rules, checked before the stream starts
        except ValueError:
            raise ApiError(422, 'invalid_message') from None
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
            self._sessions.begin_turn(session.credential, turn.message_id, regenerate=turn.regenerate,
                                      account_id=session.account_id)
        except ValueError as refused:
            raise ApiError(409, str(refused)) from None
        except KeyError:  # deleted or expired after its cookie was resolved
            raise ApiError(409, 'session_ended') from None
        # Fresh state under the turn (memory/eligibility plan, Task 2): a short reply answers the check waiting on
        # it in the same scope, and that check is asked again with the stated result.
        routed, completed = [], False
        try:
            view = self._sessions.resolve(session.credential, account_id=session.account_id)
            if view is None:
                raise ApiError(409, 'session_ended')
            bound = bind_reply(turn.text, view.pending_check, (turn.program_id, turn.curriculum_id),
                               session_id=view.session_id)
            if bound is not None and bound.fact is not None:
                view = replace(view, facts=merge_facts(view.facts, (bound.fact,)))
            context = follow_up_context(view, request_id=f'req-{secrets.token_hex(8)}',
                                        program_id=turn.program_id, curriculum_id=turn.curriculum_id)
            try:
                result = await self._pipeline.run(turn.text, context,
                                                  routed_sink=routed.append, progress=progress)
            except Exception:
                raise ApiError(503, 'answer_unavailable') from None
            route = routed[0] if routed else None
            stated = tuple(f for f in accepted_facts(route, turn.message_id) if f.session_id == view.session_id)
            if bound is not None and bound.fact is not None:
                stated = (bound.fact.model_copy(update=dict(ref=turn_ref(turn.message_id))),) + stated
            conversation = capture(route) if route is not None else None
            from .presentation import student_text
            user_text, user_cut = bounded_text(turn.text)
            assistant_text, assistant_cut = bounded_text(result if isinstance(result, str) else student_text(result))
            entities = tuple(dict.fromkeys((e.kind, e.value) for e in route.query.entities
                if e.kind in ('course', 'program', 'curriculum', 'topic'))) if route is not None else ()
            known = tuple(DialogueEntity(kind=kind, entity_id=value) for kind, value in entities[:32])
            status = getattr(result, 'status', 'answered')
            missing = tuple(getattr(result, 'missing_facts', ()))
            request = route.decision.predicate_request if route is not None else None
            unresolved = UnresolvedDialogue(originating_message_id=turn.message_id,
                requested_operation=request.predicate if request is not None else None,
                missing_slots=missing[:32], candidates=known) if status == 'clarification_needed' else None
            if (unresolved is not None and view.dialogue.unresolved is not None and route is not None
                    and route.dialogue_act is not None and route.dialogue_act.act not in ('new_topic', 'switch_topic')):
                unresolved = unresolved.model_copy(update={
                    'originating_message_id': view.dialogue.unresolved.originating_message_id})
            exchange = DialogueExchange(message_id=turn.message_id, user_text=user_text,
                program_id=route.program_id if route is not None else turn.program_id,
                curriculum_id=route.curriculum_id if route is not None else turn.curriculum_id,
                assistant_text=assistant_text, answer_status=status, entities=known,
                context=capture_request(route) if route is not None else None,
                documents=tuple(DialogueDocument(subject_id=p.subject_id, claims=p.requested_claims, detail=p.detail)
                    for p in route.proposed.parts if p.subject_id) if route and route.proposed else (),
                source_refs=tuple(c.evidence_id for c in getattr(result, 'citations', ()))[:32],
                text_truncated=user_cut or assistant_cut)
            try:
                self._sessions.commit_turn_result(session.credential, turn.message_id,
                    expected_revision=view.dialogue.revision, exchange=exchange, facts=stated,
                    pending_check=pending_from(route, result, self._labels),
                    conversation=conversation if conversation is not None else view.conversation,
                    unresolved=unresolved, account_id=session.account_id)
            except (ValueError, KeyError):
                raise ApiError(409, 'conversation_changed') from None
            completed = True
        finally:
            if not completed:  # a failed or cancelled turn commits nothing
                self._sessions.end_turn(session.credential, turn.message_id, completed=False,
                                        account_id=session.account_id)
        return result
