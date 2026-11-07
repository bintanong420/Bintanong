"""Opt-in composition of ordinary, independently validated evidence paths."""
import asyncio
import hashlib
from dataclasses import replace
from time import perf_counter

from ..bintanong_retrieval.types import RetrievalRequest
from ..bintanong_routing.contracts import Interpretation, prepare_query
from ..bintanong_routing.validation import validate_interpretation
from .compound import plan_two_eligibility_checks, execute_two_eligibility_checks, CompoundNotSupported
from .contracts import (DocumentResult, DocumentTopicOutcome, ExecutionPlan, ExecutionStep,
                        IntegrationResult, RequestUnderstanding, StageEvent)
from .integration import assemble
from .adapters import AdapterFailure


async def compose_compound(text, context, routed, resources, *, timeout_seconds, events):
    from .orchestrator import _topic_intents, merge_documents, referenced_labels
    plan = plan_two_eligibility_checks(text, context, routed, resources,
                                      allow_document=True, allow_research=True)
    proposed = routed.proposed
    document_routes = {}
    for part in proposed.parts:
        if part.evidence_need != 'document':
            continue
        data = proposed.model_dump(mode='json')
        data.update(route='RAG', operations=[], parts=[part.model_dump(mode='json')])
        validated = validate_interpretation(text, context, Interpretation.parse(data),
            catalog=resources.catalog, registry=resources.registry,
            documents_available=resources.retrieval is not None, synthetic=resources.pin.synthetic)
        if validated.diagnostic != 'validated' or validated.decision.route != 'RAG' or resources.retrieval is None:
            raise CompoundNotSupported('compound_document_failed_validation')
        document_routes[part.part_id] = validated
    started = perf_counter()
    result = await execute_two_eligibility_checks(plan, resources,
        timeout_seconds=min(timeout_seconds, 120), allow_research=True)
    stages = list(events)
    stages.append(StageEvent(stage='symbolic', duration_ms=(perf_counter()-started)*1000,
        route=proposed.route, release_id=plan.release_id,
        outcome='ready' if result.status == 'complete' else 'unknown'))
    checks = {p.part_id: p for p in result.parts}
    children, steps = [], []
    digest = hashlib.sha256(text.encode()).hexdigest()
    for part in proposed.parts:
        request, operations, evidence, status = None, (), None, 'no_evidence'
        if part.evidence_need == 'structured':
            checked = checks[part.part_id]
            request = checked.request
            operations = (proposed.operations[part.operation_indices[0]],)
            evidence, status = checked.evidence, checked.status
            child_part = part.model_copy(update={'operation_indices': (0,)})
        else:
            validated = document_routes[part.part_id]
            scope = (f'program:{plan.program_id}', f'curriculum:{plan.curriculum_id}')
            retrieval = RetrievalRequest(prepare_query(part.text), plan.release_id,
                scope=scope+resources.document_scope,
                document_version_ids=tuple(dict.fromkeys(d.version_id for d in resources.pin.documents)))
            documents = []
            started = perf_counter()
            try:
                for words, intent, part_ids in (_topic_intents(validated.proposed, context.conversation, bind_parts=True)
                        if resources.topics else [(None, {}, ())]):
                    query = retrieval if words is None else replace(retrieval, query=prepare_query(words))
                    async with asyncio.timeout(timeout_seconds):
                        actual = await resources.retrieval.retrieve(query, **intent)
                    if type(actual) is not DocumentResult:
                        raise ValueError('typed_document_result_required')
                    actual = DocumentResult.parse(actual.model_dump(mode='json'))
                    if part_ids:
                        outcome = DocumentTopicOutcome(part_ids=part_ids, subject_id=intent['subject_id'],
                            requested_claims=intent['requested_claims'], release_id=actual.release_id,
                            status=actual.status, passages=actual.passages, gaps=actual.gaps,
                            record_coverage=actual.record_coverage)
                        actual = actual.model_copy(update={'topic_outcomes': (outcome,)})
                    documents.append(actual)
                evidence = assemble(resources.pin, 'RAG', documents=merge_documents(documents))
                status = evidence.status
            except TimeoutError:
                status = 'timeout'
            except AdapterFailure:
                status = 'busy'
            except (ValueError, TypeError, KeyError, AttributeError):
                status = 'invalid_output'
            except Exception:
                status = 'tool_error'
            stages.append(StageEvent(stage='retrieval', duration_ms=(perf_counter()-started)*1000,
                route='Hybrid', release_id=plan.release_id, outcome=status))
            child_part = part
        if status in ('release_mismatch', 'conflict'):
            raise CompoundNotSupported('compound_shared_evidence_held')
        route = 'Symbolic' if request else 'RAG'
        understanding = RequestUnderstanding(schema_version=RequestUnderstanding.SCHEMA_VERSION,
            request_id=context.request_id, release_id=plan.release_id, question_sha256=digest,
            route=route, parts=(child_part,), operations=operations, predicate_request=request)
        children.append(IntegrationResult(schema_version=IntegrationResult.SCHEMA_VERSION,
            request_id=context.request_id, route=route, response_style=routed.response_style,
            status=status, evidence=evidence, understanding=understanding,
            missing_facts=evidence.missing_facts if evidence else (), events=(),
            course_labels=referenced_labels(resources.course_labels,
                evidence.model_dump(mode='json') if evidence else None)))
        steps.append(ExecutionStep(part_id=part.part_id, evidence_need=part.evidence_need, request=request))
    execution = ExecutionPlan(schema_version=ExecutionPlan.SCHEMA_VERSION,
        release_id=plan.release_id, program_id=plan.program_id, curriculum_id=plan.curriculum_id,
        steps=tuple(steps))
    understanding = RequestUnderstanding(schema_version=RequestUnderstanding.SCHEMA_VERSION,
        request_id=context.request_id, release_id=plan.release_id, question_sha256=digest,
        route=proposed.route, parts=proposed.parts, operations=proposed.operations, predicate_request=None)
    return IntegrationResult(schema_version=IntegrationResult.SCHEMA_VERSION,
        request_id=context.request_id, route=proposed.route, response_style=routed.response_style,
        status='ready' if any(c.status == 'ready' for c in children) else 'unknown', evidence=None,
        understanding=understanding, events=tuple(stages), execution_plan=execution,
        execution_parts=tuple(children))
