"""Private grade uploads over HTTP (master 15.1, 16.1).

Raw body -> capped read -> type sniffed from the leading bytes -> parsing and extraction in the bounded parser
job -> pending rows.
Only the student's explicit row choices become session facts. Responses carry printed codes and marks only, and
errors are fixed codes, so no grade or file text leaves through an error.
"""
from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from backend.bintanong_api.chat import ChatTurns
from backend.bintanong_api.session import ApiError, Session, require_session
from backend.bintanong_private_context.uploads import UploadRejected, read_capped, sniff_type

_CONFIRM_ERRORS = {'no_pending_extraction': (404, 'unknown_upload'), 'unknown_upload': (404, 'unknown_upload'),
                   'unknown_row': (422, 'unknown_row'), 'course_not_in_row': (422, 'course_not_in_row'),
                   'too_many_facts': (422, 'too_many_facts')}


class _Decision(BaseModel):
    rowId: str = Field(min_length=1, max_length=64)
    courseId: str = Field(min_length=1, max_length=128)
    state: Literal['passed', 'failed', 'enrolled', 'not_enrolled']


class ConfirmRequest(BaseModel):
    decisions: list[_Decision] = Field(min_length=1, max_length=256)


def upload_router(services, turns: ChatTurns, max_upload_bytes: int, max_parallel: int) -> APIRouter:
    router = APIRouter()
    sessions, labels = services.sessions, services.course_labels
    active = [0]  # uploads in progress; changed only on the event loop, so no lock is needed

    @router.post('/uploads')
    async def create_upload(request: Request, programId: str | None = None, curriculumId: str | None = None,
                            session: Session = Depends(require_session)) -> dict:
        program_id, curriculum_id = turns.checked_scope(programId, curriculumId, required=True)
        if active[0] >= max_parallel:
            raise ApiError(503, 'uploads_busy')
        active[0] += 1
        try:
            data = await read_capped(request.stream(), max_upload_bytes)
            sniff_type(data)
            result = await run_in_threadpool(services.extract_rows, data, program_id, curriculum_id)
        except UploadRejected as rejected:
            raise ApiError(413 if rejected.reason == 'too_large' else 422, rejected.reason) from None
        finally:
            active[0] -= 1
        upload_id = sessions.set_pending(session.credential, result, account_id=session.account_id)
        return {'uploadId': upload_id, 'unmatchedLines': result.unmatched_lines,
                'rows': [{'rowId': r.row_id, 'printedCode': r.code_text, 'marks': list(r.marks),
                          'courses': [{'courseId': c, 'label': labels.get(c, r.code_text)} for c in r.candidates]}
                         for r in result.rows]}

    @router.post('/uploads/{upload_id}/confirm')
    def confirm_upload(upload_id: str, body: ConfirmRequest, session: Session = Depends(require_session)) -> dict:
        decisions = {d.rowId: (d.courseId, d.state) for d in body.decisions}
        try:
            facts = sessions.confirm_pending(session.credential, decisions, upload_id=upload_id,
                                               account_id=session.account_id)
        except ValueError as refused:
            raise ApiError(*_CONFIRM_ERRORS.get(str(refused), (422, 'invalid_decision'))) from None
        return {'facts': [{'courseId': f.course_id, 'label': labels.get(f.course_id, f.course_id), 'state': f.state}
                          for f in facts]}

    @router.delete('/uploads/{upload_id}', status_code=204)
    def delete_upload(upload_id: str, session: Session = Depends(require_session)) -> Response:
        if not sessions.delete_upload(session.credential, upload_id, account_id=session.account_id):
            raise ApiError(404, 'unknown_upload')
        return Response(status_code=204)

    return router
