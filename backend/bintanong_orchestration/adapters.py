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
from .term_assessment import TermAssessmentResult, assess_term


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
        coverage = []
        if self.research and status == 'ok' and assessment.get('status') == 'reviewed_fields_available':
            for claim in assessment.get('claims', []):
                if (claim.get('status') != 'reviewed_fields_available'
                        or (claim.get('source_review') or {}).get('finding') != 'visible_fields'):
                    continue
                records = tuple(dict.fromkeys(f['chunk_id'] for f in claim.get('source_fields', [])
                    if ('procedure_order' not in claim['source_review']
                        or f.get('field', {}).get('name') == 'client_step')
                    and f['field'].get('source_blank') is False))
                ordered = 'procedure_order' in claim['source_review']
                if ordered:
                    by_reading = {f['reading_id']: f['chunk_id'] for f in claim['source_fields']
                        if f.get('field', {}).get('name') == 'client_step'
                        and f['field'].get('source_blank') is False}
                    order = claim['source_review']['procedure_order']
                    if set(order) != set(by_reading) or len(order) != len(by_reading):
                        raise ValueError('invalid_procedure_order')
                    records = tuple(by_reading[reading] for reading in order)
                if records or ordered:
                    required = tuple(dict.fromkeys((*records, *claim.get('required_chunk_ids', []))))
                    coverage.append(dict(subject_id=assessment['subject_id'], claim=claim['claim'],
                        chunk_ids=list(required), source_ordered=ordered,
                        **({'quoted_field':dict(chunk_id=claim['source_fields'][0]['chunk_id'],
                            field_name=claim['source_fields'][0]['field']['name'],
                            text=claim['source_fields'][0]['field']['value'],
                            span_ids=[claim['source_fields'][0]['chunk_id']+':'+str(i)
                                for i in claim['source_fields'][0]['field']['span_indexes']])}
                            if claim['source_review'].get('answer_mode') == 'quoted_field' else {}),
                        **({'sequence_chunk_ids': list(records)} if ordered and required!=records else {})))
        return DocumentResult.parse(dict(release_id=raw['release_id'], status=status,
            gaps=gaps, passages=passages, record_coverage=coverage))


# Fixed input names per operation (the routing validator binds exactly these).
SIGNATURES = {'earliest_course_term': ('curriculum_id', 'course_id', 'year_level', 'semester'),
              'check_study_plan': ('curriculum_id', 'plan_sha256'),
              'check_prerequisite_eligibility': ('curriculum_id', 'course_id'),
              'list_missing_prerequisites': ('curriculum_id', 'course_id'),
              'list_affected_courses': ('curriculum_id', 'course_id'),
              'course_facts': ('curriculum_id', 'course_id'),
              'list_term_courses': ('curriculum_id', 'year_level', 'semester'),
              'assess_term_prerequisites': ('curriculum_id', 'year_level', 'semester')}


# Only the facts a rule can use (memory/eligibility plan, Task 1): a stated pass completes; a failure, "not yet
# passed" or "never taken" is noncompletion; "took it" with no result supplies neither. The stated state itself
# stays on the session fact, so an answer never calls an unattempted course a failure.
_RULE_STATE = {'passed': 'passed', 'failed': 'failed', 'not_passed': 'failed', 'not_taken': 'failed',
               'enrolled': 'enrolled', 'not_enrolled': 'not_enrolled'}


def student_facts(facts) -> StudentFacts:
    projected = {state: [] for state in ('passed', 'failed', 'enrolled', 'not_enrolled')}
    for fact in facts:
        rule_state = _RULE_STATE.get(fact.state)
        if rule_state is not None and fact.course_id not in projected[rule_state]:
            projected[rule_state].append(fact.course_id)
    return StudentFacts(**{state: tuple(ids) for state, ids in projected.items()})


class SymbolicAdapter:
    def __init__(self, runtime, *, research=False, recovery=None):
        # research: owner-authorized real-rule mode; results keep their research labels.
        # recovery: (LoadPolicy | None, RecoveryRoutes) for Ask mode drafts, or None (no drafts are offered).
        self.research = research is True
        if self.research and runtime.synthetic is not False:
            raise ValueError('research_runtime_required')
        if not self.research and runtime.synthetic is not True:
            raise ValueError('synthetic_runtime_required')
        if recovery is not None and any(part is not None and part.synthetic is self.research for part in recovery):
            raise ValueError('recovery_sources_must_match_runtime')
        self.runtime, self.recovery = runtime, recovery
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
        facts = student_facts(context.facts)
        if operation == 'assess_term_prerequisites':  # each reviewed course of the term, same release and facts
            retakes = tuple(dict.fromkeys(f.course_id for f in context.facts if f.state == 'failed'))
            result = await self._worker.run(lambda: assess_term(self.runtime, request, facts, retakes))
            if type(result) is not TermAssessmentResult or result.synthetic is self.research:
                raise ValueError('term_result_kind_mismatch')
            return TermAssessmentResult.parse(result.model_dump(mode='json'))
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

    def recovery_routes(self, curriculum_id):
        return None if self.recovery is None else self.recovery[1]

    async def check_typed_plan(self, text_plan, context: RequestContext):
        """Check an already-structured PlanCheckRequest using owning-session facts, never model-supplied grades."""
        from ..bintanong_planning.contracts import PlanCheckRequest
        from ..bintanong_planning.checker import check_plan
        request = PlanCheckRequest.parse(text_plan.model_dump(mode='json'))
        context = RequestContext.parse(context.model_dump(mode='json'))
        if request.curriculum_id != context.curriculum_id or context.program_id is None:
            raise ValueError('request_scope_mismatch')
        facts = tuple(dict(course_id=f.course_id, state=f.state) for f in context.facts)
        if request.facts and tuple(f.model_dump(mode='json') for f in request.facts) != facts:
            raise ValueError('plan_facts_must_match_context')
        request = PlanCheckRequest.parse({**request.model_dump(mode='json'), 'facts': facts})
        policy = None if self.recovery is None else self.recovery[0]
        return await self._worker.run(lambda: check_plan(request, self.runtime, policy))

    async def earliest_term(self, course_id, context: RequestContext, start_term):
        from ..bintanong_planning.chat import earliest_term
        context = RequestContext.parse(context.model_dump(mode='json'))
        if context.curriculum_id is None or context.program_id is None:
            raise ValueError('request_scope_mismatch')
        facts = tuple((f.course_id, f.state) for f in context.facts if f.state not in ('enrolled', 'not_enrolled'))
        return await self._worker.run(lambda: earliest_term(self.runtime, context.curriculum_id, course_id, facts,
                                                           start_term))

    async def recover(self, request: PredicateRequest, context: RequestContext, affected, stated_term,
                      *, regular_asked=False):
        """Ask mode: recovery drafts for the failed course of a dependency listing, or None without sources."""
        if self.recovery is None or request.predicate != 'list_affected_courses':
            return None
        args = {i.name: i.value for i in request.inputs}
        if args.get('curriculum_id') != context.curriculum_id:
            raise ValueError('request_scope_mismatch')
        from ..bintanong_planning.recovery import plan_recovery
        policy, routes = self.recovery
        # completion results only: an enrollment statement is about the current term, not the drafted ones
        facts = tuple((f.course_id, f.state) for f in context.facts if f.state not in ('enrolled', 'not_enrolled'))
        return await self._worker.run(lambda: plan_recovery(
            self.runtime, args['curriculum_id'], args['course_id'], tuple(affected), facts, stated_term, policy, routes,
            regular_asked=regular_asked, student_status=student_status))


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

    def recovery_routes(self, curriculum_id):
        if curriculum_id not in self.adapters:
            raise ValueError('curriculum_not_in_release')
        return self.adapters[curriculum_id].recovery_routes(curriculum_id)

    async def check_typed_plan(self, text_plan, context):
        if text_plan.curriculum_id not in self.adapters:
            raise ValueError('curriculum_not_in_release')
        return await self.adapters[text_plan.curriculum_id].check_typed_plan(text_plan, context)

    async def earliest_term(self, course_id, context, start_term):
        if context.curriculum_id not in self.adapters:
            raise ValueError('curriculum_not_in_release')
        return await self.adapters[context.curriculum_id].earliest_term(course_id, context, start_term)

    async def recover(self, request, context, affected, stated_term, *, regular_asked=False, student_status=None):
        curriculum = next((i.value for i in request.inputs if i.name == 'curriculum_id'), None)
        if curriculum not in self.adapters:
            raise ValueError('curriculum_not_in_release')
        return await self.adapters[curriculum].recover(request, context, affected, stated_term,
                                                       regular_asked=regular_asked, student_status=student_status)
