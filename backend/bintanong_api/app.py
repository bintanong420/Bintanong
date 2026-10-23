"""Student-facing HTTP API (master 16.1). Session and origin rules live in `session.py`."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from fastapi import Depends, FastAPI, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse

from backend.bintanong_api.chat import ChatRequest, ChatTurns, CurriculumOption
from backend.bintanong_api.main import health_live, health_ready
from backend.bintanong_api.session import SESSION_COOKIE, ApiError, Session, check_origin, require_session
from backend.bintanong_api.sources import SourceRegistry, source_view
from backend.bintanong_api.stream import STREAM_HEADERS, chat_stream
from backend.bintanong_api.uploads import upload_router
from backend.bintanong_private_context.sessions import SessionStore
from backend.bintanong_private_context.uploads import MAX_UPLOAD_BYTES

__all__ = ['ApiServices', 'ApiSettings', 'create_app', 'require_session']


@dataclass(frozen=True)
class ApiSettings:
    allowed_origins: tuple[str, ...]
    max_upload_bytes: int = MAX_UPLOAD_BYTES


@dataclass(frozen=True)
class ApiServices:
    sessions: SessionStore
    curricula: tuple[CurriculumOption, ...] = ()
    pipeline: object = None  # run(text, context, *, routed_sink, progress) -> CandidateAnswer
    extract_rows: object = None  # (raw bytes, program_id, curriculum_id) -> ExtractionResult; parses; blocking
    course_labels: Mapping[str, str] = field(default_factory=dict)  # course id -> printed code
    sources: SourceRegistry = field(default_factory=SourceRegistry)


def create_app(services: ApiServices, settings: ApiSettings) -> FastAPI:
    app = FastAPI(title='Bintanong API', version='0.0.0', dependencies=[Depends(check_origin)])
    app.state.services, app.state.settings = services, settings
    turns = ChatTurns(services.sessions, services.pipeline, services.curricula)
    app.include_router(upload_router(services, turns, settings.max_upload_bytes))
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

    @app.post('/chat')
    def chat(request: ChatRequest, session: Session = Depends(require_session)) -> StreamingResponse:
        turn = turns.prepare(request)
        return StreamingResponse(chat_stream(turns, session, turn, services.sources),
                                 media_type='text/event-stream',
                                 headers=STREAM_HEADERS)

    @app.get('/sources/{source_id}')
    def source(source_id: str) -> dict:
        card = services.sources.get(source_id)
        if card is None:
            raise ApiError(404, 'unknown_source')
        return source_view(card)

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
