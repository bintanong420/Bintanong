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
from dataclasses import dataclass

from ..bintanong_routing.contracts import ScopedFact

IDLE_SECONDS = 30 * 60
MAX_SESSIONS = 1000
_CREDENTIAL = re.compile(r'^[A-Za-z0-9_-]{43}$')  # secrets.token_urlsafe(32)


class SessionLimitError(RuntimeError):
    """Too many live sessions; the caller should answer 503 rather than evict someone."""


@dataclass(frozen=True)
class IssuedSession:
    credential: str
    session_id: str


@dataclass(frozen=True)
class SessionView:
    session_id: str
    facts: tuple[ScopedFact, ...]


@dataclass
class _Session:
    session_id: str
    last_seen: float
    facts: tuple[ScopedFact, ...] = ()


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
            if len(self._sessions) >= self._max:
                raise SessionLimitError('session_limit')
            self._sessions[_digest(credential)] = _Session(session_id, self._clock())
        return IssuedSession(credential, session_id)

    def resolve(self, credential: object) -> SessionView | None:
        with self._lock:
            session = self._live(credential)
            return None if session is None else SessionView(session.session_id, session.facts)

    def set_facts(self, credential: object, facts: tuple[ScopedFact, ...]) -> None:
        with self._lock:
            session = self._live(credential)
            if session is None:
                raise KeyError('unknown_session')
            if any(f.session_id != session.session_id for f in facts):
                raise ValueError('foreign_session_fact')
            session.facts = tuple(facts)

    def delete(self, credential: object) -> bool:
        key = _digest(credential)
        with self._lock:
            return key is not None and self._sessions.pop(key, None) is not None

    def wipe(self) -> None:
        with self._lock:
            self._sessions.clear()

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

    def _purge_expired(self) -> None:
        now = self._clock()
        for key in [k for k, s in self._sessions.items() if now - s.last_seen > self._idle]:
            del self._sessions[key]
