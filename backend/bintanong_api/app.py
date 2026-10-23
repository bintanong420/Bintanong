"""Student-facing HTTP API (master 16.1). Session and origin rules live in `session.py`."""
from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, FastAPI, Request, Response
from fastapi.responses import JSONResponse

from backend.bintanong_api.chat import CurriculumOption
from backend.bintanong_api.main import health_live, health_ready
from backend.bintanong_api.session import SESSION_COOKIE, ApiError, check_origin, require_session
from backend.bintanong_private_context.sessions import SessionStore

__all__ = ['ApiServices', 'ApiSettings', 'create_app', 'require_session']


@dataclass(frozen=True)
class ApiSettings:
    allowed_origins: tuple[str, ...]


@dataclass(frozen=True)
class ApiServices:
    sessions: SessionStore
    curricula: tuple[CurriculumOption, ...] = ()


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

    @app.get('/curricula')
    def curricula() -> dict:
        return {'curricula': [dict(programId=c.program_id, curriculumId=c.curriculum_id,
                                   programName=c.program_name, curriculumName=c.curriculum_name)
                              for c in services.curricula]}

    @app.delete('/session', status_code=204)
    def delete_session(request: Request) -> Response:
        services.sessions.delete(request.cookies.get(SESSION_COOKIE))
        response = Response(status_code=204)
        response.delete_cookie(SESSION_COOKIE, httponly=True, secure=True, samesite='strict', path='/')
        return response

    return app
