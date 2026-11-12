from __future__ import annotations

import json
import secrets
import threading
from contextlib import asynccontextmanager
from urllib.parse import urlsplit

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response

from ..prospectus_review_gui.app import _host_ok
from ..prospectus_review_gui.render import PageError, PageRenderer
from .files import contained, read_json
from .prepare import load_packet


def create_app(session, token: str, *, port: int, ui_origin: str, workspace=None, prepare_python=None,
               model_dir=None, knowledge=None) -> FastAPI:
    origin = urlsplit(ui_origin)
    if (origin.scheme != 'http' or origin.hostname not in {'127.0.0.1', 'localhost'}
            or not origin.port or origin.path or origin.query or origin.fragment or origin.username):
        raise ValueError('review UI needs an explicit loopback origin')
    if not isinstance(token, str) or len(token) < 16:
        raise ValueError('review access token must contain at least 16 characters')
    renderers = {}
    prospectus_sessions = {}
    renderer_lock = threading.RLock()

    @asynccontextmanager
    async def lifespan(app):
        yield
        for renderer in renderers.values():
            renderer.close()
        for review in prospectus_sessions.values():
            review.close()

    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)

    @app.middleware('http')
    async def guard(request: Request, call_next):
        request_origin = request.headers.get('origin')
        if not _host_ok(request.headers.get('host', ''), port) or (
                request_origin is not None and request_origin != ui_origin):
            return JSONResponse({'error': 'Only the declared local review interface is allowed.'}, status_code=403)
        if request.method == 'OPTIONS':
            if request_origin != ui_origin:
                return JSONResponse({'error': 'Invalid review origin.'}, status_code=403)
            response = Response(status_code=204)
        elif not secrets.compare_digest(request.headers.get('x-review-token', '').encode(), token.encode()):
            return JSONResponse({'error': 'A local review token is required.'}, status_code=403)
        else:
            response = await call_next(request)
        response.headers.update({'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff',
            'Referrer-Policy': 'no-referrer', 'Access-Control-Allow-Origin': ui_origin,
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, X-Review-Token', 'Vary': 'Origin'})
        return response

    from .intake import Refusal

    @app.exception_handler(Refusal)
    async def refused(request, exc):
        return JSONResponse({'error': str(exc), 'code': exc.code}, status_code=exc.status)

    @app.exception_handler(ValueError)
    async def invalid(request, exc):
        status = 409 if 'revision' in str(exc) or 'digest' in str(exc) or 'identity' in str(exc) else 422
        return JSONResponse({'error': str(exc)}, status_code=status)

    @app.get('/api/state')
    def state():
        return session.state()

    @app.get('/api/history')
    def history():
        return session.history()

    async def read_command(request: Request):
        if request.headers.get('content-type', '').split(';')[0].strip() != 'application/json':
            return JSONResponse({'error': 'Use application/json.'}, status_code=415)
        data = bytearray()
        async for chunk in request.stream():
            data.extend(chunk)
            if len(data) > 1024 * 1024:
                return JSONResponse({'error': 'Review request exceeds 1 MiB.'}, status_code=413)
        try:
            return json.loads(data)
        except (ValueError, UnicodeError):
            return JSONResponse({'error': 'Malformed review JSON.'}, status_code=422)

    @app.post('/api/decision')
    async def decide(request: Request):
        command = await read_command(request)
        if isinstance(command, Response):
            return command
        from starlette.concurrency import run_in_threadpool
        return await run_in_threadpool(session.save, command)

    @app.post('/api/export')
    def export():
        return session.export()

    def document(identity):
        packet = load_packet(session.root)
        return next((d for d in packet['documents'] if d['id'] == identity), None)

    def prospectus(identity):
        doc = document(identity)
        if doc is None or doc['kind'] != 'prospectus':
            raise ValueError('document is not a prospectus in this packet')
        with renderer_lock:
            if identity not in prospectus_sessions:
                from ..prospectus_review_gui.session import open_session
                source = contained(session.root, doc['source'])
                candidate = contained(session.root, doc['candidate_bundle'] + '/conversion/prospectus_candidates.json')
                prospectus_sessions[identity] = open_session(candidate,
                    {'pdf_sha256': doc['sha256'], 'pdf_path': source}, session.reviewer,
                    session.root / 'review/prospectus' / identity, pdf_path=source,
                    docling_json=contained(session.root, doc['candidate_bundle'] + '/conversion/raw_docling.json'))
            return prospectus_sessions[identity]

    @app.get('/api/prospectus/{identity}/queue')
    def prospectus_queue(identity: str, mode: str = 'attention'):
        if mode not in {'attention', 'print'}:
            raise ValueError('invalid prospectus queue mode')
        review = prospectus(identity)
        return {'questions': [q.to_dict() for q in review.queue(mode)], 'state': review.state()}

    @app.get('/api/prospectus/{identity}/question')
    def prospectus_question(identity: str, qid: str):
        try:
            return prospectus(identity).question_view(qid)
        except KeyError:
            return JSONResponse({'error': 'Unknown prospectus question.'}, status_code=404)

    @app.post('/api/prospectus/{identity}/answer')
    async def prospectus_answer(identity: str, request: Request):
        from ..prospectus_review_gui.app import _answer_from
        from starlette.concurrency import run_in_threadpool
        parsed = await read_command(request)
        if isinstance(parsed, Response):
            return parsed
        qid, answer, errors = _answer_from(parsed)
        if errors:
            return JSONResponse({'error': '; '.join(errors)}, status_code=422)
        try:
            result = await run_in_threadpool(prospectus(identity).answer, qid, answer)
        except KeyError:
            return JSONResponse({'error': 'Unknown prospectus question.'}, status_code=404)
        return JSONResponse(result, status_code=422 if result['errors'] else 200)

    @app.post('/api/prospectus/{identity}/export')
    def prospectus_export(identity: str):
        review = prospectus(identity)
        result = review.materialise()
        return {'candidate_only': True, 'result': result, 'candidate': read_json(review.corrected_path),
                'ledger_jsonl': review.ledger_path.read_text(encoding='utf-8') if review.ledger_path.exists() else ''}

    @app.get('/api/source/{identity}')
    def source(identity: str):
        doc = document(identity)
        if doc is None:
            return JSONResponse({'error': 'Source not in this packet.'}, status_code=404)
        return Response(contained(session.root, doc['source']).read_bytes(), media_type='application/pdf')

    def png(key, path, number, scale):
        try:
            with renderer_lock:
                if key not in renderers:
                    renderers[key] = PageRenderer(path)
                renderer = renderers[key]
                data = renderer.png(number, scale)
                size = renderer.size(number)
                return Response(data, media_type='image/png', headers={
                    'X-Page-Width': str(size[0]), 'X-Page-Height': str(size[1]),
                    'X-Page-Count': str(renderer.page_count), 'X-Page-Rotation': str(renderer.rotation(number)),
                    'Access-Control-Expose-Headers': 'X-Page-Width, X-Page-Height, X-Page-Count, X-Page-Rotation'})
        except PageError as exc:
            return JSONResponse({'error': str(exc)}, status_code=422)

    @app.get('/api/page/{identity}/{number}')
    def page(identity: str, number: int, scale: float = 1.5):
        doc = document(identity)
        if doc is None:
            return JSONResponse({'error': 'Source not in this packet.'}, status_code=404)
        return png(identity, contained(session.root, doc['source']), number, scale)

    from . import intake

    @app.get('/api/intake/build-plan')
    def build_plan():
        return intake.build_plan(session)

    @app.post('/api/intake/build-metadata')
    async def build_metadata(request: Request):
        form = await read_command(request)
        if isinstance(form, Response):
            return form
        from starlette.concurrency import run_in_threadpool
        return await run_in_threadpool(intake.save_build_metadata, session, form)

    if workspace is not None:

        @app.post('/api/intake/upload')
        async def upload(request: Request, kind: str, title: str, edition: str, office: str = '', audience: str = ''):
            # raw PDF body with metadata in the query: no multipart dependency, and nothing reaches a command line
            if request.headers.get('content-type', '').split(';')[0].strip() != 'application/pdf':
                return JSONResponse({'error': 'Upload the PDF as application/pdf.'}, status_code=415)
            data = bytearray()
            async for chunk in request.stream():
                data.extend(chunk)
                if len(data) > intake.MAX_UPLOAD:
                    return JSONResponse({'error': 'Upload exceeds 128 MiB.'}, status_code=413)
            from starlette.concurrency import run_in_threadpool
            return await run_in_threadpool(intake.create_upload, workspace, bytes(data), kind=kind, title=title,
                                           edition=edition, office=office, audience=audience)

        @app.get('/api/intake/uploads')
        def uploads():
            return {'uploads': intake.list_uploads(workspace)}

        @app.post('/api/intake/prepare')
        async def start_prepare(request: Request):
            command = await read_command(request)
            if isinstance(command, Response):
                return command
            if (not isinstance(command, dict) or set(command) != {'upload_id', 'assist'}
                    or not isinstance(command['assist'], bool)):
                raise ValueError('prepare needs upload_id and a true/false assist choice')
            if prepare_python is None:
                raise ValueError('this review session has no Docling interpreter configured')
            return intake.start_prepare(workspace, command['upload_id'], python=prepare_python,
                                        assist=command['assist'])

        @app.get('/api/intake/prepare/{upload_id}')
        def prepare_status(upload_id: str):
            return intake.prepare_status(workspace, upload_id)

        @app.post('/api/intake/build')
        async def start_build(request: Request):
            command = await read_command(request)
            if isinstance(command, Response):
                return command
            if not isinstance(command, dict) or set(command) != {'upload_id'}:
                raise intake.Refusal('Build needs upload_id only.', 'bad_request')
            return intake.start_build(workspace, command['upload_id'], python=prepare_python, model_dir=model_dir)

        @app.get('/api/intake/build/{upload_id}')
        def build_status(upload_id: str):
            return intake.build_status(workspace, upload_id)

        @app.get('/api/intake/packet/{upload_id}/items')
        def packet_items(upload_id: str):
            return intake.packet_items(workspace, upload_id)

        from .knowledge_browse import KnowledgeBrowser
        browser = knowledge if knowledge is not None else KnowledgeBrowser(workspace)

        @app.get('/api/knowledge/sources')
        def knowledge_sources():
            return browser.sources()

        @app.get('/api/knowledge/chunks')
        def knowledge_chunks(source: str, q: str = '', offset: int = 0, limit: int = 25, document: str = ''):
            return browser.chunks(source, q, offset, limit, document)

        @app.get('/api/knowledge/documents')
        def knowledge_documents(source: str):
            return browser.documents(source)

        @app.get('/api/knowledge/page')
        def knowledge_page(sha256: str, page: int, scale: float = 1.5):
            path = browser.sources_index.pdf(sha256)  # scan and hash happen here, outside the render lock
            if path is None:
                return JSONResponse({'error': 'source PDF not available locally', 'code': 'source_not_local'},
                                    status_code=404)
            return png('sha256:' + sha256, path, page, scale)

    if isinstance(session, intake.SessionSlot):

        @app.get('/api/intake/current')
        def current():
            return {'upload_id': session.upload_id}

        @app.post('/api/intake/open')
        async def open_upload(request: Request):
            command = await read_command(request)
            if isinstance(command, Response):
                return command
            if not isinstance(command, dict) or set(command) != {'upload_id'}:
                raise ValueError('open needs upload_id only')
            from starlette.concurrency import run_in_threadpool
            return await run_in_threadpool(session.open, command['upload_id'])

    return app
