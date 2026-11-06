"""Gated benchmark runs: one question through the unchanged answer path, with what kNN ranked beside the answer.

Mounted only when the trusted launcher configures it; never on the student site. Each run gets its own session, so
nothing carries between questions. The all-chunk ranking is display and scoring data and never reaches the answer.
"""
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
import re
import secrets
import threading
from typing import Literal

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, ConfigDict, Field

from backend.bintanong_api.chat import ChatTurns, PreparedTurn
from backend.bintanong_api.presentation import student_text
from backend.bintanong_api.session import ApiError, Session
from backend.bintanong_api.stream import _title
from backend.bintanong_private_context.sessions import SessionStore
from backend.bintanong_retrieval.observation import observe_retrievals
from backend.bintanong_retrieval.types import RetrievalRequest
from backend.bintanong_routing.contracts import prepare_query

RUN_SCHEMA = 'bintanong-evaluation-run-v1'
MIN_TOKEN_LENGTH = 12
_NO_KEY = dict(key_id=None, key_status='human_judged', relevant_chunk_ids=[], expected_facts=[],
               expected_route=None, expected_outcome=None, source_note=None)


class RunBody(BaseModel):
    model_config = ConfigDict(extra='forbid')
    question: str = Field(max_length=16000)


class JudgmentBody(BaseModel):
    model_config = ConfigDict(extra='forbid')
    chunk_marks: dict[str, bool]
    answer_mark: Literal['correct', 'partial', 'wrong'] | None
    note: str = Field(default='', max_length=2000)


def route_label(routed):
    if routed is None:
        return None
    return routed.decision.route or routed.decision.control


def _row(rank, item, emitted):
    chunk = item['chunk']
    return dict(rank=rank, chunk_id=chunk['chunk_id'], similarity=item['similarity'],
                text=chunk.get('source_text') or chunk['text'], source_label=chunk.get('source_label'),
                pages=sorted({span['page'] for span in item.get('spans', []) if span.get('page') is not None}),
                section_path=list(chunk.get('section_path') or ()), sent_to_writer=chunk['chunk_id'] in emitted,
                attached_count=len(item.get('neighbors') or ()))


def _rows(items, emitted):
    return [_row(rank, item, emitted) for rank, item in enumerate(items, 1)]


class _RouteCapture:
    """Passes everything to the real pipeline and keeps the routing result for the record."""
    def __init__(self, pipeline):
        self._pipeline, self.routed = pipeline, None

    async def run(self, text, context, *, routed_sink, progress):
        def sink(routed):
            self.routed = routed
            routed_sink(routed)
        return await self._pipeline.run(text, context, routed_sink=sink, progress=progress)


class EvaluationService:
    def __init__(self, *, pipeline, releases, curricula, course_labels, roster, normalize_question, keys_document,
                 log_path, code_commit, token):
        self._pipeline, self._releases, self._curricula = pipeline, releases, curricula
        self._labels, self._roster, self._normalize = course_labels, roster, normalize_question
        self._log_path, self._commit, self._token = Path(log_path), code_commit, token
        self._by_question = {normalize_question(row['question']): row for row in roster}
        self._curriculum_labels = {(c.program_id, c.curriculum_id): f'{c.program_name} {c.curriculum_name}' for c in curricula}
        self._keys = {case_id: key for key in keys_document['keys'] for case_id in key['case_ids']}
        self._lock = threading.Lock()
        self._records = []
        if self._log_path.exists():
            self._records = [json.loads(line) for line in self._log_path.read_text(encoding='utf-8').splitlines() if line.strip()]

    def _append(self, record):
        with self._lock:
            with self._log_path.open('a', encoding='utf-8') as log:
                log.write(json.dumps(record, ensure_ascii=False) + '\n')
            self._records.append(record)

    def _key(self, case_id):
        return None if case_id is None else self._keys.get(case_id, _NO_KEY)

    def cases(self):
        return dict(code_commit=self._commit, cases=[dict(row, key=self._key(row['case_id']),
            curriculum_label=self._curriculum_labels.get((row['program_id'], row['curriculum_id'])))
            for row in self._roster])

    def runs(self):
        judgments = {r['run_id']: r for r in self._records if r['record_type'] == 'judgment'}
        return dict(runs=[dict(r, key=self._key(r['case_id']), judgment=judgments.get(r['run_id']))
                          for r in self._records if r['record_type'] == 'run'])

    def judge(self, run_id, body: JudgmentBody):
        if not any(r['record_type'] == 'run' and r['run_id'] == run_id for r in self._records):
            raise ApiError(404, 'unknown_run')
        record = dict(record_type='judgment', run_id=run_id, chunk_marks=body.chunk_marks,
                      answer_mark=body.answer_mark, note=body.note)
        self._append(record)
        return record

    async def run_question(self, question):
        try:
            text = prepare_query(question)
        except ValueError:
            raise ApiError(422, 'invalid_message') from None
        case = self._by_question.get(self._normalize(question))
        program_id, curriculum_id = (case['program_id'], case['curriculum_id']) if case is not None else (None, None)
        if program_id is not None and (program_id, curriculum_id) not in self._curriculum_labels:
            raise ApiError(409, 'case_curriculum_unavailable')
        record = dict(record_type='run', schema_version=RUN_SCHEMA, run_id='run-' + secrets.token_hex(8),
                      code_commit=self._commit, release_id=None, question=question,
                      case_id=case['case_id'] if case is not None else None, program_id=program_id,
                      curriculum_id=curriculum_id, outcome='completed', error=None,
                      route_label=None, topics=[], answer=None, searches=[])
        capture, seen, failure = _RouteCapture(self._pipeline), [], None
        store = SessionStore()  # one question, one session: nothing carries to the next run
        issued = store.issue()
        session = Session(issued.credential, store.resolve(issued.credential))
        turns = ChatTurns(store, capture, self._curricula, course_labels=self._labels)
        try:
            with observe_retrievals() as seen:
                result = await turns.run(session, PreparedTurn(question, 'msg-evaluation', program_id, curriculum_id, False))
        except ApiError as error:
            failure = error.code
        else:
            record['answer'] = dict(status=getattr(result, 'status', 'answered'), language=getattr(result, 'language', None),
                                    text=result if isinstance(result, str) else student_text(result),
                                    reason=getattr(result, 'reason', None),
                                    sources=[_title(card) for card in getattr(result, 'citations', ())])
            if record['answer']['status'] == 'temporarily_unavailable':
                failure = record['answer']['reason'] or 'temporarily_unavailable'
        routed = capture.routed
        record['route_label'] = route_label(routed)
        if routed is not None and routed.proposed is not None:
            record['topics'] = [dict(subject_id=part.subject_id, claims=list(part.requested_claims))
                                for part in routed.proposed.parts if part.subject_id]
        if failure is None:
            try:
                record['searches'], record['release_id'] = await self._searches(seen, routed, text)
            except Exception:
                failure = 'all_chunk_search_failed'
        if failure is not None:
            record.update(outcome='infrastructure_error', error=failure, searches=[])
        self._append(record)
        return dict(record, key=self._key(record['case_id']), judgment=None)

    async def _searches(self, seen, routed, fallback_query):
        resources = await self._releases.pin()
        engine = resources.retrieval.engine
        versions = tuple(dict.fromkeys(document.version_id for document in resources.pin.documents))
        turn_emitted = {identity for entry in seen for identity in entry['emitted_chunk_ids']}
        planned = seen or [dict(query=routed.query.normalized_text if routed is not None else fallback_query,
                                subject_id=None, requested_claims=None, candidates=[], emitted_chunk_ids=[])]
        searches = []
        for entry in planned:
            request = RetrievalRequest(entry['query'], resources.pin.release_id, scope=tuple(resources.document_scope),
                                       document_version_ids=versions)
            everything = await asyncio.to_thread(engine.search_all_chunks, request)
            searches.append(dict(query=entry['query'], subject_id=entry['subject_id'],
                                 requested_claims=entry['requested_claims'],
                                 topic_bound=_rows(entry['candidates'], set(entry['emitted_chunk_ids'])),
                                 all_chunks=_rows(everything, turn_emitted)))
        return searches, resources.pin.release_id

    def _require_token(self, request: Request):
        supplied = request.headers.get('x-bintanong-evaluator', '')
        if not secrets.compare_digest(supplied.encode(), self._token.encode()):
            raise ApiError(404, 'route_unavailable')

    def router(self, admission):
        router = APIRouter(prefix='/evaluation', dependencies=[Depends(self._require_token)])

        @router.get('/cases')
        def cases():
            return self.cases()

        @router.get('/runs')
        def runs():
            return self.runs()

        @router.post('/run')
        async def run(body: RunBody):
            reservation = admission.reserve(account_id='evaluator')
            try:
                async with reservation.running(lambda _stage: None):
                    return await self.run_question(body.question)
            finally:
                reservation.release()

        @router.post('/runs/{run_id}/judgment')
        def judgment(run_id: str, body: JudgmentBody):
            return self.judge(run_id, body)
        return router


def _inside_git(path):
    return any((parent / '.git').exists() for parent in path.parents)


def evaluation_from_env(pipeline, releases, curricula, course_labels, *, environ=None):
    """None unless the launcher sets a passcode; a half-configured launcher refuses to start."""
    environ = os.environ if environ is None else environ
    token = environ.get('BINTANONG_EVALUATION_TOKEN')
    if not token:
        return None
    if len(token) < MIN_TOKEN_LENGTH:
        raise ValueError('evaluation_token_too_short')
    log, keys, commit = (environ.get('BINTANONG_EVALUATION_' + name) for name in ('LOG', 'KEYS', 'COMMIT'))
    if not (log and keys and commit):
        raise ValueError('evaluation_configuration_incomplete')
    if re.fullmatch(r'[0-9a-f]{7,40}', commit) is None:
        raise ValueError('evaluation_commit_invalid')
    log_path = Path(log).resolve()
    if _inside_git(log_path):
        raise ValueError('evaluation_log_inside_git')
    from evaluation.system_metrics import load_roster, normalize_question  # dev checkout only; the student path skips it
    roster = load_roster()
    keys_document = json.loads(Path(keys).read_text(encoding='utf-8'))
    known, covered = {row['case_id'] for row in roster}, set()
    for key in keys_document['keys']:
        for case_id in key['case_ids']:
            if case_id not in known:
                raise ValueError('evaluation_key_unknown_case')
            if case_id in covered:
                raise ValueError('evaluation_key_duplicate_case')
            covered.add(case_id)
    return EvaluationService(pipeline=pipeline, releases=releases, curricula=curricula, course_labels=course_labels,
                             roster=roster, normalize_question=normalize_question, keys_document=keys_document,
                             log_path=log_path, code_commit=commit, token=token)
