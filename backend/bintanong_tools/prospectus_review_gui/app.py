"""The loopback-only HTTP face of a ReviewSession (decisions D7 and D8).

Every request must carry a Host of 127.0.0.1 or localhost on the app's port (DNS rebinding). Every request that is
not a GET or HEAD must carry the per-launch token in `X-Review-Token` and, when the browser sends an Origin, the
app's own origin: another web page open in the reviewer's browser cannot write decisions. Every response carries a
strict Content-Security-Policy; the page has no inline script or style and loads nothing from outside.
"""

from __future__ import annotations

import math
import secrets
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response

from ..prospectus_extractor.fixer_cli import FixerError
from ..prospectus_extractor.ledger import LedgerError
from .answers import Answer
from .questions import MODES
from .render import PageError
from .session import ReviewSession

STATIC = Path(__file__).parent / "static"
STATIC_TYPES = {".css": "text/css; charset=utf-8", ".js": "text/javascript; charset=utf-8"}
CSP = ("default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; "
       "frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
LOOPBACK = ("127.0.0.1", "localhost")
TOKEN_PLACEHOLDER = "__REVIEW_TOKEN__"
PAGE_STATUS = {"missing_pdf": 404, "bad_pdf": 404, "bad_page": 404, "bad_scale": 422}


def new_token() -> str:
    return secrets.token_urlsafe(32)


def _host_ok(value: str, port: int | None) -> bool:
    name, _sep, given = value.rpartition(":") if value.count(":") == 1 else (value, "", "")
    return name.lower() in LOOPBACK and (port is None or given == str(port))


def _origin_ok(value: str, port: int | None) -> bool:
    try:
        parts = urlsplit(value)
        return parts.scheme == "http" and (parts.hostname or "") in LOOPBACK and (port is None or parts.port == port) \
            and not parts.path.strip("/")
    except ValueError:
        return False


def _same(a: str, b: str) -> bool:
    return secrets.compare_digest(a.encode("utf-8", "replace"), b.encode("utf-8", "replace"))


def _error(status: int, message: str) -> JSONResponse:
    return JSONResponse({"error": message}, status_code=status)


def _answer_from(body: Any) -> tuple[str | None, Answer | None, list[str]]:
    """(qid, Answer, errors) from the posted JSON; types are checked here, values by answer_to_entries."""
    if not isinstance(body, dict):
        return None, None, ["the answer must be a JSON object"]
    qid, choice = body.get("qid"), body.get("choice")
    edits, proposals = body.get("edits", {}), body.get("proposals", [])
    reason, note = body.get("reason", ""), body.get("note", "")
    errors = []
    if not isinstance(qid, str) or not qid:
        errors.append("qid must be text")
    if not isinstance(choice, str):
        errors.append("choice must be yes, no or other")
    if not isinstance(edits, dict) or not all(isinstance(k, str) for k in edits):
        errors.append("edits must map field names to typed text")
    if not isinstance(proposals, list) or not all(isinstance(p, str) for p in proposals):
        errors.append("proposals must be a list of letters")
    if not isinstance(reason, str) or not isinstance(note, str):
        errors.append("reason and note must be text")
    if errors:
        return None, None, errors
    return qid, Answer(choice=choice, edits=edits, proposals=proposals, reason=reason, note=note), []


def create_app(session: ReviewSession, token: str, port: int | None = None) -> FastAPI:
    """The app for one session. `port` is the bound port the Host and Origin checks expect (None accepts any port,
    for a caller that cannot know it yet)."""
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    app.state.token = token

    @app.middleware("http")
    async def guard(request: Request, call_next):
        if not _host_ok(request.headers.get("host", ""), port):
            response = _error(403, "this review tool only answers on 127.0.0.1 or localhost")
        elif request.method not in ("GET", "HEAD") and (
                ("origin" in request.headers and not _origin_ok(request.headers["origin"], port))
                or not _same(request.headers.get("x-review-token", ""), token)):
            response = _error(403, "this request did not come from the review page")
        else:
            response = await call_next(request)
        response.headers["Content-Security-Policy"] = CSP
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers.setdefault("Cache-Control", "no-store")
        return response

    @app.get("/")
    def page() -> HTMLResponse:
        return HTMLResponse((STATIC / "index.html").read_text(encoding="utf-8").replace(TOKEN_PLACEHOLDER, token))

    @app.get("/favicon.ico")
    def favicon() -> Response:
        return Response(status_code=204)   # no icon; answering stops the browser logging a 404 on every load

    @app.get("/static/{name}")
    def static(name: str) -> Response:
        path = STATIC / name
        if Path(name).name != name or path.suffix not in STATIC_TYPES or not path.is_file():
            return _error(404, "not found")
        return Response(path.read_bytes(), media_type=STATIC_TYPES[path.suffix])

    @app.get("/api/state")
    def state() -> dict:
        return session.state()

    @app.get("/api/queue")
    def queue(mode: str = "attention"):
        if mode not in MODES:
            return _error(422, f"mode must be one of {', '.join(MODES)}")
        questions = session.questions()
        return {"mode": mode, "queue": [q.to_dict() for q in session.queue(mode)],
                "all": [{"qid": q.qid, "kind": q.kind, "section": q.section, "decided": q.decided, "prompt": q.prompt,
                         "position": q.position} for q in questions]}

    @app.get("/api/question/{qid}")
    def question(qid: str):
        try:
            return session.question_view(qid)
        except KeyError:
            return _error(404, f"no question {qid}")

    @app.get("/api/page/{number}.png")
    def page_png(number: int, scale: str = "1.5"):
        try:
            value = float(scale)
        except ValueError:
            return _error(422, "scale must be a number")
        if not math.isfinite(value):
            return _error(422, "scale must be a number")
        try:
            data = session.page_png(number, value)
        except PageError as exc:
            return _error(PAGE_STATUS.get(exc.code, 404), str(exc))
        return Response(data, media_type="image/png", headers={"Cache-Control": "private, max-age=300"})

    @app.get("/api/twin")
    def twin() -> dict:
        return session.twin()

    @app.post("/api/answer")
    async def answer(request: Request):
        try:
            body = await request.json()
        except ValueError:
            return JSONResponse({"errors": ["the answer is not JSON"]}, status_code=422)
        qid, parsed, errors = _answer_from(body)
        if errors:
            return JSONResponse({"errors": errors}, status_code=422)
        try:
            result = await _in_thread(session.answer, qid, parsed)
        except KeyError:
            return JSONResponse({"errors": [f"no question {qid}"]}, status_code=404)
        if result["errors"]:
            return JSONResponse(result, status_code=422)
        queue = session.queue()
        return {**result, "state": session.state(), "next": queue[0].qid if queue else None}

    @app.post("/api/materialise")
    def materialise():
        try:
            return session.materialise()
        except (FixerError, LedgerError, OSError) as exc:
            print(f"error: {exc}", file=sys.stderr)   # the full message (with its path) stays on this machine's terminal
            return _error(500, "the corrected candidate could not be written; see the terminal")

    return app


async def _in_thread(func, *args):
    """Run a blocking session call off the event loop (the session serialises writers itself)."""
    from starlette.concurrency import run_in_threadpool

    return await run_in_threadpool(func, *args)
