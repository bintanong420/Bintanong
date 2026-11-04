"""One release pin, one validated LLM route, explicit independent evidence branches."""
import asyncio
from dataclasses import replace
import math
import hashlib
import re
import json
from time import perf_counter

from ..bintanong_contracts.symbolic import SymbolicResult
from ..bintanong_retrieval.types import RetrievalRequest
from ..bintanong_routing.contracts import RequestContext, ScopedFact, prepare_query
from ..bintanong_routing.router import Router
from ..bintanong_routing.validation import effective_facts, facts_for_term
from ..bintanong_routing.combined import CombinedRouter
from ..bintanong_routing.topic_selection import ABSENCE, ABSENCE_TOPICS, SHIFT, SHIFT_TOPICS
from ..bintanong_symbolic.course_facts import CourseFactsResult
from ..bintanong_symbolic.runtime import DependencyResult, ResearchDependencyResult, ResearchSymbolicResult
from .adapters import AdapterFailure
from .term_assessment import TermAssessmentResult
from .contracts import DocumentResult, IntegrationResult, StageEvent, RequestUnderstanding
from .integration import assemble
from .ports import HeldReleaseProvider, ReleaseResources, ReleaseUnavailable

_ROUTING_FAILURES = {
    'model_timeout':'timeout',
    'model_connection_error':'tool_error', 'model_http_error':'tool_error',
    'invalid_model_output':'invalid_output', 'invalid_style_output':'invalid_output',
    # Persistent reference errors: the question could not be interpreted; ask, not 'outage'.
    'invalid_reference':'clarify',
    # The model asked to clarify but named nothing: unavailable information (owner E3, 24 Oct 2026).
    'empty_clarification':'no_evidence',
    # A structured fact with no operation to run ("How many units is CC 5?"): unavailable information, not an
    # outage (owner step 2d, 24 Oct 2026).
    'unsupported_requirement':'no_evidence',
    'invalid_grounding':'invalid_output', 'invalid_server_response':'invalid_output',
    'truncated_output':'invalid_output', 'server_response_too_large':'invalid_output',
    'context_overflow':'invalid_output',
}



# Owner 2 Nov 2026 (#10, CC-first): the held overdue-fine note fetches both printed fine records; the generation
# host reply (fee_precedence.py) then answers the Charter fee first and discloses the Handbook figure.
FEE_PRECEDENCE = {'H101/C79 overdue fine applicability and precedence unresolved':
                  (('charter_returns', 'printed returns fields'), ('handbook_library', 'printed library fields'))}


def _topic_intents(proposed):
    """Each chosen document topic with its facts and its parts' words, in part order (owner step 2e: every topic is
    retrieved). The words are the topic's query only when there are several topics (live: the whole two-topic
    message found nothing for its special-class fee part); a single topic keeps the whole message."""
    parts = [p for p in proposed.parts if p.evidence_need == 'document' and p.subject_id]
    if not parts:
        return [(None, dict(subject_id=None, requested_claims=None))]
    claims, texts = {}, {}
    for p in parts:
        for claim in p.requested_claims:
            for subject, wanted in FEE_PRECEDENCE.get(claim, ((p.subject_id, claim),)):
                claims.setdefault(subject, {})[wanted] = None
                texts.setdefault(subject, {})[p.text] = None
        # Owner 2 Nov 2026 (#3): an absence question gets the attendance rule and the sickness certificate together.
        # Owner 3 Nov 2026 (H8): a shifting question gets the 4.1 rule and the FAQ 8 steps together.
        for topics, cue in ((ABSENCE_TOPICS, ABSENCE), (SHIFT_TOPICS, SHIFT)):
            if p.subject_id not in topics or not cue.search(p.text):
                continue
            for subject, wanted in topics.items():
                claims.setdefault(subject, {})[wanted] = None
                texts.setdefault(subject, {})[p.text] = None
    return [(' '.join(texts[s]) if len(claims) > 1 else None, dict(subject_id=s, requested_claims=tuple(claims[s])))
            for s in claims]


def merge_documents(results):
    """One result for several topics: the first one that is not 'ok' (any topic without evidence leaves the
    message unanswered, as integration requires), otherwise every distinct passage and gap in order."""
    failed = next((r for r in results if r.status != 'ok'), None)
    if failed is not None:
        return failed
    passages = {p.chunk_id: p for r in results for p in r.passages}
    gaps = dict.fromkeys(g for r in results for g in r.gaps)
    coverage = {}
    for result in results:
        for item in result.record_coverage:
            key = (item.subject_id, item.claim)
            previous = coverage.get(key)
            if previous is None:
                coverage[key] = item
            elif previous.source_ordered or item.source_ordered:
                if previous != item:
                    raise ValueError('incompatible_procedure_order')
            else:
                coverage[key] = previous.model_copy(update=dict(
                    chunk_ids=tuple(dict.fromkeys(previous.chunk_ids + item.chunk_ids))))
    value = results[0].model_dump(mode='json')
    value.update(passages=[p.model_dump(mode='json') for p in passages.values()], gaps=list(gaps),
        record_coverage=[item.model_dump(mode='json') for item in coverage.values()])
    return DocumentResult.parse(value)


def referenced_labels(labels, *mentions):
    """Printed-code labels for the courses this answer mentions; a release of several curricula
    holds far more labels than one answer may carry."""
    text = json.dumps(mentions, sort_keys=True, default=str)
    return {cid: code for cid, code in labels
            if re.search(re.escape(cid) + r'(?![0-9A-Za-z_-])', text)}


def choice_labels(details, missing):
    """Printed details for the courses or programs a "which one" clarification lists."""
    chosen = {field.split(':', 1)[1] for field in missing if field.startswith(('course_choice:', 'program_choice:', 'program_topic:'))}
    return {cid: label for cid, label in details if cid in chosen}


class Orchestrator:
    def __init__(self, transport, *, releases=None, stage_timeout=120.0,
                 routing_profile='separate', topic_selection=False):
        if (type(stage_timeout) not in (int,float) or not math.isfinite(stage_timeout)
                or not 0 < stage_timeout <= 300):
            raise ValueError('stage_timeout_must_be_finite_positive_at_most_300')
        if routing_profile not in ('separate','combined'):
            raise ValueError('invalid_routing_profile')
        if type(topic_selection) is not bool:
            raise ValueError('invalid_topic_selection')
        self.transport = transport
        self.releases = HeldReleaseProvider() if releases is None else releases
        self.stage_timeout = float(stage_timeout)
        self.routing_profile = routing_profile
        self.topic_selection = topic_selection  # opt-in Router candidate narrowing for large menus

    async def run(self, text: str, context: RequestContext, *, routed_sink=None) -> IntegrationResult:
        """routed_sink, when given, receives the routing result so the owning host can capture
        session-only conversation context (master 23); nothing is kept here."""
        prepare_query(text)
        context = RequestContext.parse(context.model_dump(mode='json'))
        events, resources, route, style = [], None, None, 'unknown'
        understanding, assumed, recovery, routed = None, (), None, None

        def finish(status, evidence=None, missing=()):
            ready = status == 'ready'
            drafts = recovery if ready else None
            return IntegrationResult(schema_version=IntegrationResult.SCHEMA_VERSION,
                request_id=context.request_id, route=route, response_style=style,
                status=status, evidence=evidence, understanding=understanding,
                missing_facts=tuple(missing), events=tuple(events), assumed_facts=assumed,
                recovery=drafts, unavailable_parts=routed.unavailable_parts if ready and routed is not None else (),
                course_labels=referenced_labels(resources.course_labels if resources else (),
                    evidence.model_dump(mode='json') if evidence is not None else None,
                    understanding.model_dump(mode='json') if understanding is not None else None,
                    drafts.model_dump(mode='json') if drafts is not None else None,
                    tuple(missing)) | choice_labels(resources.course_details if resources else (), tuple(missing)))

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
                elif isinstance(value, CourseFactsResult):
                    observed = {'complete':'ready','not_reviewed':'no_evidence','not_found':'no_evidence',
                                'unsupported':'unsupported'}[value.status]
                elif isinstance(value, TermAssessmentResult):
                    observed = {'complete':'ready','partial':'unknown','not_covered':'no_evidence',
                                'not_reviewed':'no_evidence','not_found':'no_evidence',
                                'unsupported':'unsupported'}[value.status]
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
                                    value.course_labels, value.course_details)  # choice labels (live #12, 3 Nov)

        resources, failure = await stage('release', pin_release)
        if failure:
            return finish(failure)
        router_class = CombinedRouter if self.routing_profile=='combined' else Router
        router = router_class(self.transport, catalog=resources.catalog, registry=resources.registry,
            documents_available=resources.retrieval is not None, synthetic=True,
            topic_selection=self.topic_selection,
            **(dict(topics=resources.topics) if resources.topics else {}))
        scoped = None

        async def route_request():
            nonlocal scoped, route, style, understanding, assumed
            value = await router.route(text, context)
            route, style = value.decision.route, value.response_style
            # A failed result can carry style (for its clarification) but never its rejected parts.
            if (value.style_evidence is not None and value.proposed is not None
                    and value.diagnostic not in _ROUTING_FAILURES):
                understanding = RequestUnderstanding(
                    schema_version=RequestUnderstanding.SCHEMA_VERSION,
                    request_id=context.request_id, release_id=resources.pin.release_id,
                    question_sha256=hashlib.sha256(text.encode('utf-8')).hexdigest(),
                    route=route, parts=value.proposed.parts, operations=value.proposed.operations,
                    predicate_request=value.decision.predicate_request)
            if route is not None:
                # Bound the merged assertion set within the guarded routing stage.
                # Nothing is persisted, and overflow cannot escape as an exception.
                assumed = tuple(f'{c.state}:{c.course_id}' for c in value.claims if c.mode == 'hypothetical')
                program = value.program_id or context.program_id
                curriculum = value.curriculum_id or context.curriculum_id
                context_facts = tuple(f for f in context.facts
                                      if (f.program_id, f.curriculum_id) == (program, curriculum))
                # A what-if premise replaces the record for its course in this check only; nothing is persisted here.
                facts = tuple(f if type(f) is ScopedFact else
                              ScopedFact(**{name:getattr(f,name) for name in ScopedFact.model_fields})
                              for f in facts_for_term(effective_facts(context_facts, value.claims), text))
                scoped = RequestContext(session_id=context.session_id, request_id=context.request_id,
                    program_id=program, curriculum_id=curriculum, facts=facts)
            return value

        routed, failure = await stage('routing', route_request)
        if failure:
            return finish(failure)
        if routed_sink is not None:
            routed_sink(routed)
        route, style = routed.decision.route, routed.response_style
        if routed.decision.control is not None:
            return finish(routed.decision.control, missing=routed.decision.missing_facts)
        if ((route in ('RAG','Hybrid') and resources.retrieval is None) or
                (route in ('Symbolic','Hybrid') and resources.symbolic is None)):
            return finish('held')
        async def retrieve():
            scope = tuple(f'{kind}:{value}' for kind,value in
                (('program',scoped.program_id),('curriculum',scoped.curriculum_id)) if value)
            request = RetrievalRequest(
                routed.query.normalized_text, resources.pin.release_id, scope=scope+resources.document_scope,
                # Only document versions hold chunks; curriculum sources are for Prolog.
                document_version_ids=tuple(dict.fromkeys(d.version_id for d in resources.pin.documents)))
            results = []
            for words, intent in (_topic_intents(routed.proposed) if resources.topics else [(None, {})]):
                topic_request = request if words is None else replace(request, query=prepare_query(words))
                value = await resources.retrieval.retrieve(topic_request, **intent)
                if type(value) is not DocumentResult:
                    raise ValueError('typed_document_result_required')
                results.append(DocumentResult.parse(value.model_dump(mode='json')))
            return merge_documents(results)

        async def reason():
            request = routed.decision.predicate_request
            resources.registry.goal(request)
            value = await resources.symbolic.execute(request, scoped)
            if request.predicate == 'assess_term_prerequisites':  # each course of the term, same release and facts
                if (type(value) is not TermAssessmentResult or value.inputs != request.inputs
                        or value.synthetic is research_pin):
                    raise ValueError('operation_result_mismatch')
                return TermAssessmentResult.parse(value.model_dump(mode='json'))
            if request.predicate in ('course_facts', 'list_term_courses'):  # printed facts; no rule executed
                if (type(value) is not CourseFactsResult or value.inputs != request.inputs
                        or value.predicate != request.predicate or value.synthetic is research_pin):
                    raise ValueError('operation_result_mismatch')
                return CourseFactsResult.parse(value.model_dump(mode='json'))
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

        documents, symbolic, dependencies, course_facts, term_assessment = None, None, None, None, None
        research_pin = not resources.pin.synthetic
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
            recovery = await self._recovery(text, routed.decision.predicate_request, scoped, resources, result,
                                            follow_up=context if routed.compiled else None)
        elif isinstance(result, CourseFactsResult):
            course_facts = result
        elif isinstance(result, TermAssessmentResult):
            term_assessment = result
        else:
            symbolic = result

        async def integrate():
            return assemble(resources.pin, route, documents=documents,
                            symbolic=symbolic, dependencies=dependencies, course_facts=course_facts,
                            term_assessment=term_assessment)

        evidence, failure = await stage('integration', integrate)
        return finish(failure) if failure else finish(evidence.status, evidence, evidence.missing_facts)

    async def _recovery(self, text, request, scoped, resources, dependencies, *, follow_up=None):
        """Ask mode (owner 4 Nov 2026): recovery routes and greedy drafts when the dependency question also asks
        what to take or how to recover. A draft failure keeps the plain dependency answer; it never fails the turn."""
        from ..bintanong_routing.recovery_cue import asks_recovery, recovery_follow_up
        from ..bintanong_routing.terms import parse_term
        recover = getattr(resources.symbolic, 'recover', None)
        if (recover is None or not (asks_recovery(text) or (follow_up is not None and recovery_follow_up(text, follow_up)))
                or dependencies.status not in ('complete', 'partial')):
            return None
        try:
            async with asyncio.timeout(self.stage_timeout):
                value = await recover(request, scoped, dependencies.course_ids, parse_term(text),
                                      regular_asked=bool(re.search(r'\bregular\b', text, re.I)))
        except (ValueError, TypeError, KeyError, AttributeError, AdapterFailure, TimeoutError):
            return None
        return None if value is None or value.synthetic is not resources.pin.synthetic else value
