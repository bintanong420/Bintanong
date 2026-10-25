"""Translate existing module outputs without upgrading their authorization/status."""
import asyncio
import threading

from ..bintanong_contracts.runtime import PredicateRequest
from ..bintanong_contracts.symbolic import SymbolicResult
from ..bintanong_retrieval.types import RetrievalRequest
from ..bintanong_routing.contracts import RequestContext
from ..bintanong_symbolic.course_facts import CourseFactsResult
from ..bintanong_symbolic.runtime import (DependencyResult, ResearchDependencyResult,
                                         ResearchSymbolicResult, StudentFacts)
from .contracts import DocumentResult


class AdapterFailure(RuntimeError):
    """Fixed operational code only; never include upstream exception text."""


def _consume(task):
    if not task.cancelled():
        task.exception()


class _BoundedWorker:
    """Cancellation ends the wait, not the thread; hold admission until completion."""
    def __init__(self):
        self._admission = threading.Lock()

    async def run(self, call):
        if not self._admission.acquire(blocking=False):
            raise AdapterFailure('busy')

        def invoke():
            try:
                return call()
            finally:
                self._admission.release()

        task = asyncio.create_task(asyncio.to_thread(invoke))
        try:
            return await asyncio.shield(task)
        except asyncio.CancelledError:
            task.add_done_callback(_consume)
            raise


class RetrievalAdapter:
    def __init__(self, engine, *, research=False):
        # research: owner-authorized real-data development mode (AGENTS.md, 21 Oct 2026).
        self.engine, self.research = engine, research is True
        self._worker = _BoundedWorker()

    async def retrieve(self, request: RetrievalRequest, **intent) -> DocumentResult:
        # Research topic intent (subject_id/requested_claims) is forwarded only when supplied.
        raw = await self._worker.run(lambda: self.engine.retrieve(request, **intent))
        if raw.get('schema_version') not in (None, 'bintanong-retrieval-debug-v1',
                                             'bintanong-retrieval-debug-v2'):
            raise ValueError('invalid_retrieval_schema')
        passages = []
        for p in raw['evidence']:
            citations = [dict(c, locator=dict(table_index=None, cell_ids=[], item_ids=[],
                ref=None, section_path=[]) | c['locator']) for c in p['citations']]
            passages.append(dict(chunk_id=p['chunk_id'], version_id=p['version_id'],
                text=p['text'], citations=citations))
        status, gaps = raw['status'], list(raw['gaps'])
        assessment = (raw.get('evidence_policy') or {}).get('assessment') or {}
        if self.research and status == 'uncalibrated' and assessment.get('status') == 'reviewed_fields_available':
            # Reviewed fields found; only the calibration marker is lifted, real gaps stay.
            status, gaps = 'ok', [g for g in gaps if g != 'development_calibration_pending']
        return DocumentResult.parse(dict(release_id=raw['release_id'], status=status,
            gaps=gaps, passages=passages))


# Fixed input names per operation (the routing validator binds exactly these).
SIGNATURES = {'check_prerequisite_eligibility': ('curriculum_id', 'course_id'),
              'list_missing_prerequisites': ('curriculum_id', 'course_id'),
              'list_affected_courses': ('curriculum_id', 'course_id'),
              'course_facts': ('curriculum_id', 'course_id'),
              'list_term_courses': ('curriculum_id', 'year_level', 'semester')}


class SymbolicAdapter:
    def __init__(self, runtime, *, research=False):
        # research: owner-authorized real-rule mode; results keep their research labels.
        self.research = research is True
        if self.research and runtime.synthetic is not False:
            raise ValueError('research_runtime_required')
        if not self.research and runtime.synthetic is not True:
            raise ValueError('synthetic_runtime_required')
        self.runtime = runtime
        self.release_id = runtime.release_id
        self.rule_bundle_version = runtime.rule_bundle_version
        self._worker = _BoundedWorker()

    async def execute(self, request: PredicateRequest, context: RequestContext
                      ) -> SymbolicResult | DependencyResult:
        request = PredicateRequest.parse(request.model_dump(mode='json'))
        context = RequestContext.parse(context.model_dump(mode='json'))
        operation = request.predicate
        if operation not in SIGNATURES:
            raise ValueError('unsupported_operation')
        args = {i.name:i.value for i in request.inputs}
        if set(args) != set(SIGNATURES[operation]):
            raise ValueError('invalid_signature')
        if args['curriculum_id'] != context.curriculum_id or context.program_id is None:
            raise ValueError('request_scope_mismatch')
        if operation in ('course_facts', 'list_term_courses'):  # reviewed printed facts; no rule executed
            result = await self._worker.run(lambda: self.runtime.look_up(request))
            if type(result) is not CourseFactsResult or result.synthetic is self.research:
                raise ValueError('course_facts_result_kind_mismatch')
            return CourseFactsResult.parse(result.model_dump(mode='json'))
        # The context contains user assertions, never verified university grades.
        facts = StudentFacts(**{state:tuple(f.course_id for f in context.facts if f.state == state)
            for state in ('passed', 'failed', 'enrolled', 'not_enrolled')})
        if operation == 'list_affected_courses':
            result = await self._worker.run(lambda: self.runtime.list_affected_courses(request))
            kind = ResearchDependencyResult if self.research else DependencyResult
            if type(result) is not kind or result.synthetic is self.research:
                raise ValueError('dependency_result_kind_mismatch')
            return kind.parse(result.model_dump(mode='json'))
        result = await self._worker.run(lambda: self.runtime.check(request, facts))
        kind = ResearchSymbolicResult if self.research else SymbolicResult
        if type(result) is not kind or result.decision.synthetic is self.research:
            raise ValueError('symbolic_result_kind_mismatch')
        return kind.parse(result.model_dump(mode='json'))


class MultiCurriculumSymbolicAdapter:
    """Several reviewed curricula in one research release; each check runs on the runtime of the
    curriculum named by the request, which keeps that curriculum's own release identity."""
    research = True

    def __init__(self, adapters, *, release_id, rule_bundle_version):
        if not adapters or any(not a.research for a in adapters.values()):
            raise ValueError('research_runtime_required')
        self.adapters = dict(adapters)
        self.release_id, self.rule_bundle_version = release_id, rule_bundle_version

    async def execute(self, request: PredicateRequest, context: RequestContext
                      ) -> SymbolicResult | DependencyResult:
        curriculum = next((i.value for i in request.inputs if i.name == 'curriculum_id'), None)
        if curriculum not in self.adapters:
            raise ValueError('curriculum_not_in_release')
        return await self.adapters[curriculum].execute(request, context)
