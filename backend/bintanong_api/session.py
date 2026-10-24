"""Cookie session boundary over the memory-only SessionStore, plus the origin check for unsafe methods.

The browser holds only an opaque credential in a `__Host-` cookie; the store keeps its digest. Unsafe
methods must come from a configured origin (OWASP CSRF guidance; SameSite is defence in depth only).
"""
from __future__ import annotations

from dataclasses import dataclass

from fastapi import Request

from backend.bintanong_private_context.sessions import SessionLimitError, SessionStore, SessionView

SESSION_COOKIE = '__Host-bintanong_session'
_SAFE_METHODS = frozenset({'GET', 'HEAD', 'OPTIONS'})


class ApiError(Exception):
    def __init__(self, status: int, code: str):
        super().__init__(code)
        self.status, self.code = status, code


@dataclass(frozen=True)
class Session:
    credential: str
    view: SessionView


def check_origin(request: Request) -> None:
    if request.method in _SAFE_METHODS:
        return
    if request.headers.get('sec-fetch-site') == 'cross-site':
        raise ApiError(403, 'origin_not_allowed')
    if request.headers.get('origin') not in request.app.state.settings.allowed_origins:
        raise ApiError(403, 'origin_not_allowed')


def require_session(request: Request) -> Session:
    """The caller's live session, or a fresh one when the cookie is missing, unknown or expired."""
    store: SessionStore = request.app.state.services.sessions
    credential = request.cookies.get(SESSION_COOKIE)
    view = store.resolve(credential)
    if view is None:
        try:
            issued = store.issue()
        except SessionLimitError:
            raise ApiError(503, 'session_limit') from None
        credential, view = issued.credential, store.resolve(issued.credential)
        request.state.issued_credential = credential
    return Session(credential, view)
