"""One release pin, one validated LLM route, explicit independent evidence branches."""
import asyncio
import math
import hashlib
from time import perf_counter

from ..bintanong_contracts.symbolic import SymbolicResult
from ..bintanong_retrieval.types import RetrievalRequest
from ..bintanong_routing.contracts import RequestContext, ScopedFact, prepare_query
from ..bintanong_routing.router import Router
from ..bintanong_routing.combined import CombinedRouter
from ..bintanong_symbolic.runtime import DependencyResult, ResearchDependencyResult, ResearchSymbolicResult
from .adapters import AdapterFailure
from .contracts import DocumentResult, IntegrationResult, StageEvent, RequestUnderstanding
from .integration import assemble
from .ports import HeldReleaseProvider, ReleaseResources, ReleaseUnavailable

_ROUTING_FAILURES = {
    'model_timeout':'timeout',
    'model_connection_error':'tool_error', 'model_http_error':'tool_error',
    'invalid_model_output':'invalid_output', 'invalid_style_output':'invalid_output',
    # Persistent reference errors: the question could not be interpreted; ask, not 'outage'.
    'invalid_reference':'clarify',
    'invalid_grounding':'invalid_output', 'invalid_server_response':'invalid_output',
    'truncated_output':'invalid_output', 'server_response_too_large':'invalid_output',
    'context_overflow':'invalid_output',
}



def _topic_intent(proposed):
    """First chosen document topic and its facts; other topics stay unretrieved (known limit)."""
    parts = [p for p in proposed.parts if p.evidence_need == 'document' and p.subject_id]
    if not parts:
        return dict(subject_id=None, requested_claims=None)
    subject = parts[0].subject_id
    claims = dict.fromkeys(c for p in parts if p.subject_id == subject for c in p.requested_claims)
    return dict(subject_id=subject, requested_claims=tuple(claims))

class Orchestrator:
    def __init__(self, transport, *, releases=None, stage_timeout=120.0,
                 routing_profile='separate'):
        if (type(stage_timeout) not in (int,float) or not math.isfinite(stage_timeout)
                or not 0 < stage_timeout <= 300):
            raise ValueError('stage_timeout_must_be_finite_positive_at_most_300')
        if routing_profile not in ('separate','combined'):
            raise ValueError('invalid_routing_profile')
        self.transport = transport
        self.releases = HeldReleaseProvider() if releases is None else releases
        self.stage_timeout = float(stage_timeout)
        self.routing_profile = routing_profile

    async def run(self, text: str, context: RequestContext) -> IntegrationResult:
        prepare_query(text)
        context = RequestContext.parse(context.model_dump(mode='json'))
        events, resources, route, style = [], None, None, 'unknown'
        understanding = None

        def finish(status, evidence=None, missing=()):
            return IntegrationResult(schema_version=IntegrationResult.SCHEMA_VERSION,
                request_id=context.request_id, route=route, response_style=style,
                status=status, evidence=evidence, understanding=understanding,
                missing_facts=tuple(missing), events=tuple(events),
                course_labels=dict(resources.course_labels) if resources else {})

        async def stage(name, call):
            start, value, outcome = perf_counter(), None, 'ok'
            try:
                async with asyncio.timeout(self.stage_timeout):
                    value = await call()
            except ReleaseUnavailable:
                outcome = 'held'
            except TimeoutError:
                outcome = 'timeout'
            except AdapterFailure:
                outcome = 'busy'
            except (ValueError, TypeError, KeyError, AttributeError):
                outcome = 'invalid_output'
            except Exception:
                # Details may contain a private query or upstream response body.
                outcome = 'tool_error'
            ids, retries, event_route = (), 0, route
            release_id = resources.pin.release_id if resources else None
            observed = outcome
            if outcome == 'ok':
                if name == 'release':
                    release_id = value.pin.release_id
                elif name == 'routing':
                    retries = value.repair_attempts
                    event_route = value.decision.route
                    if value.decision.control is not None:
                        observed = 'control'
                    if value.decision.control == 'evidence_unavailable' and value.diagnostic in _ROUTING_FAILURES:
                        outcome = observed = _ROUTING_FAILURES[value.diagnostic]
                elif isinstance(value, DocumentResult):
                    ids = tuple(p.chunk_id for p in value.passages)
                    observed = value.status
                elif isinstance(value, (SymbolicResult, DependencyResult)):
                    ids = value.rule_ids
                    observed = value.decision.outcome if isinstance(value, SymbolicResult) else (
                        {'complete':'ready','partial':'unknown','unsupported':'unsupported','error':'error'}[value.status])
                elif name == 'integration':
                    observed = value.status
            metadata = dict(stage=name, duration_ms=(perf_counter()-start)*1000,
                route=event_route, release_id=release_id)
            try:
                event = StageEvent(**metadata, outcome=observed, retry_count=retries, evidence_ids=ids)
            except ValueError:
                # Invalid adapter metadata cannot leak through a validation error
                # or crash the request. Keep only safe, host-owned stage metadata.
                outcome, value = 'invalid_output', None
                event = StageEvent(**metadata, outcome=outcome)
            events.append(event)
            return value, None if outcome == 'ok' else outcome

        async def pin_release():
            value = await self.releases.pin()
            if not isinstance(value, ReleaseResources):
                raise ValueError('release_resources_required')
            # Recheck metadata at this request boundary; the provider is trusted.
            return ReleaseResources(value.pin, value.catalog, value.registry,
                                    value.retrieval, value.symbolic, value.topics, value.document_scope,
                                    value.course_labels)

        resources, failure = await stage('release', pin_release)
        if failure:
            return finish(failure)
        router_class = CombinedRouter if self.routing_profile=='combined' else Router
        router = router_class(self.transport, catalog=resources.catalog, registry=resources.registry,
            documents_available=resources.retrieval is not None, synthetic=True,
            **(dict(topics=resources.topics) if resources.topics else {}))
        scoped = None

        async def route_request():
            nonlocal scoped, route, style, understanding
            value = await router.route(text, context)
            route, style = value.decision.route, value.response_style
            if value.style_evidence is not None and value.proposed is not None:
                understanding = RequestUnderstanding(
                    schema_version=RequestUnderstanding.SCHEMA_VERSION,
                    request_id=context.request_id, release_id=resources.pin.release_id,
                    question_sha256=hashlib.sha256(text.encode('utf-8')).hexdigest(),
                    route=route, parts=value.proposed.parts, operations=value.proposed.operations,
                    predicate_request=value.decision.predicate_request)
            if route is not None:
                # Bound the merged assertion set within the guarded routing stage.
                # Nothing is persisted, and overflow cannot escape as an exception.
                facts = (*context.facts, *(ScopedFact(**{name:getattr(c,name) for name in ScopedFact.model_fields})
                    for c in value.claims if c.mode == 'asserted'))
                scoped = RequestContext(session_id=context.session_id, request_id=context.request_id,
                    program_id=value.program_id or context.program_id,
                    curriculum_id=value.curriculum_id or context.curriculum_id, facts=facts)
            return value

        routed, failure = await stage('routing', route_request)
        if failure:
            return finish(failure)
        route, style = routed.decision.route, routed.response_style
        if routed.decision.control is not None:
            return finish(routed.decision.control, missing=routed.decision.missing_facts)
        if ((route in ('RAG','Hybrid') and resources.retrieval is None) or
                (route in ('Symbolic','Hybrid') and resources.symbolic is None)):
            return finish('held')
        async def retrieve():
            scope = tuple(f'{kind}:{value}' for kind,value in
                (('program',scoped.program_id),('curriculum',scoped.curriculum_id)) if value)
            value = await resources.retrieval.retrieve(RetrievalRequest(
                routed.query.normalized_text, resources.pin.release_id, scope=scope+resources.document_scope,
                document_version_ids=tuple(s.version_id for s in resources.pin.sources)),
                **(_topic_intent(routed.proposed) if resources.topics else {}))
            if type(value) is not DocumentResult:
                raise ValueError('typed_document_result_required')
            return DocumentResult.parse(value.model_dump(mode='json'))

        async def reason():
            request = routed.decision.predicate_request
            resources.registry.goal(request)
            value = await resources.symbolic.execute(request, scoped)
            # A research pin expects labelled real-rule results; a synthetic pin, synthetic ones.
            research = not resources.pin.synthetic
            result_kind, dependency_kind = ((ResearchSymbolicResult, ResearchDependencyResult) if research
                                            else (SymbolicResult, DependencyResult))
            if type(value) not in (result_kind, dependency_kind) or value.inputs != request.inputs:
                raise ValueError('operation_input_mismatch')
            if type(value) is result_kind:
                if value.decision.predicate != request.predicate or value.decision.synthetic is research:
                    raise ValueError('operation_result_mismatch')
                resources.registry.check_result(value)
                return result_kind.parse(value.model_dump(mode='json'))
            if request.predicate != 'list_affected_courses' or value.synthetic is research:
                raise ValueError('dependency_operation_mismatch')
            return dependency_kind.parse(value.model_dump(mode='json'))

        documents, symbolic, dependencies = None, None, None
        if route == 'Hybrid':
            (documents, doc_failure), (result, sym_failure) = await asyncio.gather(
                stage('retrieval', retrieve), stage('symbolic', reason))
            failure = sym_failure or doc_failure
        elif route == 'RAG':
            documents, failure = await stage('retrieval', retrieve)
            result = None
        else:
            result, failure = await stage('symbolic', reason)
        if failure:
            return finish(failure)
        if isinstance(result, DependencyResult):
            dependencies = result
        else:
            symbolic = result

        async def integrate():
            return assemble(resources.pin, route, documents=documents,
                            symbolic=symbolic, dependencies=dependencies)

        evidence, failure = await stage('integration', integrate)
        return finish(failure) if failure else finish(evidence.status, evidence, evidence.missing_facts)
