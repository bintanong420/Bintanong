"""Student-facing HTTP API (master 16.1): cookie session boundary over the memory-only SessionStore.

The browser holds only an opaque credential in a `__Host-` cookie; the store keeps its digest. Unsafe
methods must come from a configured origin (OWASP CSRF guidance; SameSite is defence in depth only).
"""
from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, FastAPI, Request, Response
from fastapi.responses import JSONResponse

from backend.bintanong_api.main import health_live, health_ready
from backend.bintanong_private_context.sessions import SessionLimitError, SessionStore, SessionView

SESSION_COOKIE = '__Host-bintanong_session'
_SAFE_METHODS = frozenset({'GET', 'HEAD', 'OPTIONS'})


@dataclass(frozen=True)
class ApiSettings:
    allowed_origins: tuple[str, ...]


@dataclass(frozen=True)
class ApiServices:
    sessions: SessionStore


@dataclass(frozen=True)
class Session:
    credential: str
    view: SessionView


class ApiError(Exception):
    def __init__(self, status: int, code: str):
        super().__init__(code)
        self.status, self.code = status, code


def check_origin(request: Request) -> None:
    if request.method in _SAFE_METHODS:
        return
    settings: ApiSettings = request.app.state.settings
    if request.headers.get('sec-fetch-site') == 'cross-site':
        raise ApiError(403, 'origin_not_allowed')
    if request.headers.get('origin') not in settings.allowed_origins:
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


def create_app(services: ApiServices, settings: ApiSettings) -> FastAPI:
    app = FastAPI(title='Bintanong API', version='0.0.0', dependencies=[Depends(check_origin)])
    app.state.services, app.state.settings = services, settings
    app.add_api_route('/health/live', health_live, methods=['GET'])
    app.add_api_route('/health/ready', health_ready, methods=['GET'])

    @app.exception_handler(ApiError)
    async def api_error(_request: Request, error: ApiError):
        return JSONResponse({'error': error.code}, status_code=error.status)

    @app.middleware('http')
    async def attach_session_cookie(request: Request, call_next):
        response = await call_next(request)
        credential = getattr(request.state, 'issued_credential', None)
        if credential is not None:
            response.set_cookie(SESSION_COOKIE, credential, httponly=True, secure=True, samesite='strict',
                                path='/')
        return response

    @app.delete('/session', status_code=204)
    def delete_session(request: Request) -> Response:
        services.sessions.delete(request.cookies.get(SESSION_COOKIE))
        response = Response(status_code=204)
        response.delete_cookie(SESSION_COOKIE, httponly=True, secure=True, samesite='strict', path='/')
        return response

    return app
