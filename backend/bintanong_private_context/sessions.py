"""In-process session store keyed by an opaque server-issued credential (master 15.1-15.2, owner D3).

Memory only: nothing is written to disk, Supabase or logs, so a restart forgets every session.
Only a SHA-256 digest of each credential is kept; the browser-visible session id is not a credential.
"""
from __future__ import annotations

import hashlib
import re
import secrets
import threading
import time
from dataclasses import dataclass, field

from ..bintanong_routing.contracts import ConversationContext, RequestContext, ScopedFact
from .grades import ExtractionResult, confirm_rows

IDLE_SECONDS = 30 * 60
MAX_SESSIONS = 1000
# A session never holds more facts than one request may carry.
MAX_FACTS = next(m.max_length for m in RequestContext.model_fields['facts'].metadata if hasattr(m, 'max_length'))
_CREDENTIAL = re.compile(r'^[A-Za-z0-9_-]{43}$')  # secrets.token_urlsafe(32)


class SessionLimitError(RuntimeError):
    """Every live session holds student state; the caller should answer 503 rather than evict someone."""


@dataclass(frozen=True)
class IssuedSession:
    credential: str
    session_id: str


@dataclass(frozen=True)
class SessionView:
    session_id: str
    facts: tuple[ScopedFact, ...]
    pending: ExtractionResult | None
    conversation: ConversationContext | None
    pending_upload_id: str | None = None


@dataclass
class _Session:
    session_id: str
    last_seen: float
    facts: tuple[ScopedFact, ...] = ()
    pending: ExtractionResult | None = None
    confirmations: int = 0
    conversation: ConversationContext | None = None
    turn_in_flight: bool = False
    answered_message: str | None = None
    pending_upload_id: str | None = None
    upload_facts: dict[str, tuple[str, ...]] = field(default_factory=dict)  # upload id -> fact ids it confirmed


def _digest(credential: object) -> str | None:
    if not isinstance(credential, str) or not _CREDENTIAL.fullmatch(credential):
        return None
    return hashlib.sha256(credential.encode('ascii')).hexdigest()


class SessionStore:
    def __init__(self, *, idle_seconds: float = IDLE_SECONDS, clock=time.monotonic,
                 max_sessions: int = MAX_SESSIONS):
        self._idle = idle_seconds
        self._clock = clock
        self._max = max_sessions
        self._sessions: dict[str, _Session] = {}
        self._lock = threading.Lock()

    def __len__(self) -> int:
        with self._lock:
            return len(self._sessions)

    def issue(self) -> IssuedSession:
        credential = secrets.token_urlsafe(32)
        session_id = f'sess-{secrets.token_hex(16)}'
        with self._lock:
            self._purge_expired()
            if len(self._sessions) >= self._max and not self._evict_one_empty():
                raise SessionLimitError('session_limit')
            self._sessions[_digest(credential)] = _Session(session_id, self._clock())
        return IssuedSession(credential, session_id)

    def resolve(self, credential: object) -> SessionView | None:
        with self._lock:
            session = self._live(credential)
            return None if session is None else SessionView(session.session_id, session.facts, session.pending,
                                                                 session.conversation, session.pending_upload_id)

    def set_facts(self, credential: object, facts: tuple[ScopedFact, ...]) -> None:
        with self._lock:
            session = self._owned(credential)
            if any(f.session_id != session.session_id for f in facts):
                raise ValueError('foreign_session_fact')
            session.facts = tuple(facts)

    def set_conversation(self, credential: object, conversation: ConversationContext | None) -> None:
        with self._lock:
            self._owned(credential).conversation = conversation

    def set_pending(self, credential: object, extraction: ExtractionResult | None) -> str | None:
        """Replaces any earlier pending rows; returns the new upload id."""
        with self._lock:
            session = self._owned(credential)
            session.pending = extraction
            session.pending_upload_id = None if extraction is None else f'upl-{secrets.token_hex(8)}'
            return session.pending_upload_id

    def confirm_pending(self, credential: object, decisions: dict[str, tuple[str, str]], *,
                        upload_id: str | None = None) -> tuple[ScopedFact, ...]:
        """Student's row choices become facts; a new statement for a course replaces the earlier one."""
        with self._lock:
            session = self._owned(credential)
            if session.pending is None:
                raise ValueError('no_pending_extraction')
            if upload_id is not None and upload_id != session.pending_upload_id:
                raise ValueError('unknown_upload')
            session.confirmations += 1
            new = confirm_rows(session.pending, decisions, session_id=session.session_id,
                               batch=session.confirmations)
            replaced = {f.course_id for f in new}
            merged = tuple(f for f in session.facts if f.course_id not in replaced) + new
            if len(merged) > MAX_FACTS:
                raise ValueError('too_many_facts')
            session.facts = merged
            session.upload_facts[session.pending_upload_id] = tuple(f.fact_id for f in new)
            session.pending = session.pending_upload_id = None
            return session.facts

    def delete_upload(self, credential: object, upload_id: str) -> bool:
        """Removes the upload's pending rows and the facts it confirmed that are still current."""
        with self._lock:
            session = self._live(credential)
            if session is None:
                return False
            found = upload_id == session.pending_upload_id
            if found:
                session.pending = session.pending_upload_id = None
            confirmed = session.upload_facts.pop(upload_id, None)
            if confirmed is not None:
                session.facts = tuple(f for f in session.facts if f.fact_id not in confirmed)
            return found or confirmed is not None

    def begin_turn(self, credential: object, message_id: str, *, regenerate: bool = False) -> None:
        """One chat turn at a time per session; a completed message is not answered twice."""
        with self._lock:
            session = self._owned(credential)
            if session.turn_in_flight:
                raise ValueError('chat_in_progress')
            if not regenerate and message_id == session.answered_message:
                raise ValueError('already_answered')
            session.turn_in_flight = True

    def end_turn(self, credential: object, message_id: str, *, completed: bool) -> None:
        """A session deleted or expired during the turn stays gone."""
        with self._lock:
            session = self._live(credential)
            if session is None:
                return
            session.turn_in_flight = False
            if completed:
                session.answered_message = message_id

    def delete(self, credential: object) -> bool:
        key = _digest(credential)
        with self._lock:
            return key is not None and self._sessions.pop(key, None) is not None

    def wipe(self) -> None:
        with self._lock:
            self._sessions.clear()

    def _owned(self, credential: object) -> _Session:
        session = self._live(credential)
        if session is None:
            raise KeyError('unknown_session')
        return session

    def _live(self, credential: object) -> _Session | None:
        key = _digest(credential)
        session = self._sessions.get(key) if key else None
        if session is None:
            return None
        now = self._clock()
        if now - session.last_seen > self._idle:
            del self._sessions[key]
            return None
        session.last_seen = now
        return session

    def _evict_one_empty(self) -> bool:
        """Owner, 24 Oct 2026: cookie-less requests must not lock students out, so the least recently used
        session that holds nothing the student stated (and no running turn) makes room."""
        empty = [(s.last_seen, k) for k, s in self._sessions.items()
                 if not (s.facts or s.pending or s.conversation or s.turn_in_flight)]
        if not empty:
            return False
        del self._sessions[min(empty)[1]]
        return True

    def _purge_expired(self) -> None:
        now = self._clock()
        for key in [k for k, s in self._sessions.items() if now - s.last_seen > self._idle]:
            del self._sessions[key]
