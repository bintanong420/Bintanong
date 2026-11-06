"""Candidate-only bounded FM-05 executor for two independent eligibility checks."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Literal
from pydantic import Field, model_validator

from ..bintanong_contracts.base import Contract, Record
from ..bintanong_contracts.runtime import PredicateRequest
from ..bintanong_contracts.symbolic import SymbolicResult
from ..bintanong_routing.contracts import Interpretation, RequestContext, ScopedFact
from ..bintanong_routing.validation import (
    RoutingResult, effective_facts, facts_for_term, validate_interpretation,
)
from .adapters import AdapterFailure
from .contracts import CandidateEvidence
from .integration import assemble
from .ports import ReleaseResources


class CompoundNotSupported(ValueError):
    """Reject unsupported shapes rather than dropping requested work."""


@dataclass(frozen=True)
class PlannedCheck:
    part_id: str
    predicate_request: PredicateRequest


@dataclass(frozen=True)
class CompoundPlan:
    release_id: str
    program_id: str
    curriculum_id: str
    checks: tuple[PlannedCheck, PlannedCheck]
    scoped: RequestContext


def plan_two_eligibility_checks(text: str, context: RequestContext, routed: RoutingResult,
                                resources: ReleaseResources) -> CompoundPlan:
    """Revalidate each model-proposed part using P12's existing single-operation guard."""
    if (type(routed) is not RoutingResult or routed.diagnostic != 'compound_request'
            or routed.decision.dispatchable or routed.decision.control != 'clarify'
            or routed.proposed is None):
        raise CompoundNotSupported('not_a_guarded_compound_request')
    p = Interpretation.parse(routed.proposed.model_dump(mode='json'))
    if (p.route != 'Symbolic' or p.control is not None or p.ambiguities
            or len(p.operations) != 2 or len(p.parts) != 2
            or any(op.name != 'check_prerequisite_eligibility' for op in p.operations)
            or any(part.evidence_need != 'structured' or len(part.operation_indices) != 1
                   for part in p.parts)
            or {part.operation_indices[0] for part in p.parts} != {0, 1}
            or resources.pin.synthetic is not True or resources.symbolic is None):
        raise CompoundNotSupported('compound_shape_not_supported')
    context = RequestContext.parse(context.model_dump(mode='json'))
    valid = []
    for idx in range(2):
        part = next(part for part in p.parts if part.operation_indices == (idx,))
        narrowed = p.model_dump(mode='json')
        narrowed['operations'] = [p.operations[idx].model_dump(mode='json')]
        narrowed['parts'] = [dict(part.model_dump(mode='json'), operation_indices=[0])]
        checked = validate_interpretation(
            text, context, Interpretation.parse(narrowed), catalog=resources.catalog,
            registry=resources.registry, documents_available=False, synthetic=True)
        if (checked.diagnostic != 'validated' or checked.decision.route != 'Symbolic'
                or checked.decision.predicate_request is None
                or checked.decision.predicate_request.predicate != 'check_prerequisite_eligibility'
                or not checked.program_id or not checked.curriculum_id):
            raise CompoundNotSupported('compound_subcheck_failed_validation')
        valid.append((part.part_id, checked))
    programs = {r.program_id for _, r in valid}
    curricula = {r.curriculum_id for _, r in valid}
    if len(programs) != 1 or len(curricula) != 1:
        raise CompoundNotSupported('compound_curriculum_mismatch')
    program, curriculum = next(iter(programs)), next(iter(curricula))
    targets = [next((i.value for i in r.decision.predicate_request.inputs
                     if i.name == 'course_id'), None) for _, r in valid]
    if None in targets or len(set(targets)) != 2:
        raise CompoundNotSupported('duplicate_or_unresolved_compound_targets')
    if (routed.program_id, routed.curriculum_id) != (program, curriculum):
        raise CompoundNotSupported('compound_scope_binding_mismatch')
    basis = tuple(f for f in context.facts
                  if (f.program_id, f.curriculum_id) == (program, curriculum))
    grounded = tuple(ScopedFact(**{k: getattr(f, k) for k in ScopedFact.model_fields})
                     for f in facts_for_term(effective_facts(basis, routed.claims), text))
    scoped = RequestContext(session_id=context.session_id, request_id=context.request_id,
                            program_id=program, curriculum_id=curriculum, facts=grounded)
    checks = tuple(PlannedCheck(pid, r.decision.predicate_request) for pid, r in valid)
    return CompoundPlan(resources.pin.release_id, program, curriculum, checks, scoped)


class CompoundPartResult(Record):
    part_id: str = Field(pattern=r'^r[1-8]$')
    request: PredicateRequest
    status: Literal['ready', 'unknown', 'unsupported', 'error', 'conflict',
                    'release_mismatch', 'no_evidence', 'timeout', 'busy',
                    'invalid_output', 'tool_error']
    evidence: CandidateEvidence | None

    @model_validator(mode='after')
    def _bound(self):
        if self.evidence is not None:
            if (self.evidence.route != 'Symbolic' or self.evidence.status != self.status
                    or self.evidence.symbolic is None
                    or self.evidence.symbolic.decision.predicate != self.request.predicate
                    or self.evidence.symbolic.inputs != self.request.inputs):
                raise ValueError('compound_part_result_mismatch')
        elif self.status not in ('timeout', 'busy', 'invalid_output', 'tool_error'):
            raise ValueError('missing_compound_evidence')
        return self


class CompoundResearchResult(Contract):
    SCHEMA_VERSION = 'bintanong-compound-research-result-v1'
    candidate_only: Literal[True] = True
    institutional_use_allowed: Literal[False] = False
    activation_allowed: Literal[False] = False
    release_id: str = Field(pattern=r'^release-[a-z0-9-]+$')
    program_id: str
    curriculum_id: str
    status: Literal['complete', 'partial', 'withheld']
    parts: tuple[CompoundPartResult, CompoundPartResult]

    @model_validator(mode='after')
    def _coherent(self):
        if len({p.part_id for p in self.parts}) != 2:
            raise ValueError('duplicate_compound_part')
        for p in self.parts:
            values = {i.name: i.value for i in p.request.inputs}
            if (values.get('curriculum_id') != self.curriculum_id
                    or (p.evidence is not None and p.evidence.pin.release_id != self.release_id)):
                raise ValueError('compound_scope_or_release_mismatch')
        successes = sum(p.status == 'ready' for p in self.parts)
        expected = 'complete' if successes == 2 else 'partial' if successes else 'withheld'
        if self.status != expected:
            raise ValueError('compound_summary_mismatch')
        return self


async def execute_two_eligibility_checks(plan: CompoundPlan, resources: ReleaseResources,
                                         *, timeout_seconds: float = 30) -> CompoundResearchResult:
    """Run sequentially to respect the per-runtime worker-admission lock."""
    if (not 0 < timeout_seconds <= 120 or resources.pin.synthetic is not True
            or plan.release_id != resources.pin.release_id or resources.symbolic is None):
        raise CompoundNotSupported('invalid_compound_execution_scope')
    results = []
    for part in plan.checks:
        try:
            resources.registry.goal(part.predicate_request)
            async with asyncio.timeout(timeout_seconds):
                actual = await resources.symbolic.execute(part.predicate_request, plan.scoped)
            if type(actual) is not SymbolicResult:
                raise ValueError('wrong_symbolic_result_kind')
            if (actual.decision.predicate != part.predicate_request.predicate
                    or actual.inputs != part.predicate_request.inputs):
                raise ValueError('wrong_symbolic_result_binding')
            resources.registry.check_result(actual)
            evidence = assemble(resources.pin, 'Symbolic', symbolic=actual)
            results.append(CompoundPartResult(part_id=part.part_id, request=part.predicate_request,
                                              status=evidence.status, evidence=evidence))
        except TimeoutError:
            results.append(CompoundPartResult(part_id=part.part_id, request=part.predicate_request,
                                              status='timeout', evidence=None))
        except AdapterFailure:
            results.append(CompoundPartResult(part_id=part.part_id, request=part.predicate_request,
                                              status='busy', evidence=None))
        except (ValueError, TypeError, KeyError, AttributeError):
            results.append(CompoundPartResult(part_id=part.part_id, request=part.predicate_request,
                                              status='invalid_output', evidence=None))
        except Exception:
            results.append(CompoundPartResult(part_id=part.part_id, request=part.predicate_request,
                                              status='tool_error', evidence=None))
    count = sum(p.status == 'ready' for p in results)
    return CompoundResearchResult(schema_version=CompoundResearchResult.SCHEMA_VERSION,
        release_id=plan.release_id, program_id=plan.program_id, curriculum_id=plan.curriculum_id,
        status='complete' if count == 2 else 'partial' if count else 'withheld', parts=tuple(results))


async def run_bounded_compound(text: str, context: RequestContext, transport, releases,
                               *, timeout_seconds: float = 30) -> CompoundResearchResult:
    """Developer-only routed entrypoint; no student-facing generator activation."""
    from ..bintanong_routing.router import Router
    resources = await releases.pin()
    if not isinstance(resources, ReleaseResources) or resources.pin.synthetic is not True:
        raise CompoundNotSupported('synthetic_release_required')
    router = Router(transport, catalog=resources.catalog, registry=resources.registry,
                    documents_available=resources.retrieval is not None, synthetic=True,
                    **(dict(topics=resources.topics) if resources.topics else {}))
    context = RequestContext.parse(context.model_dump(mode='json'))
    routed = await router.route(text, context)
    checked = plan_two_eligibility_checks(text, context, routed, resources)
    return await execute_two_eligibility_checks(checked, resources,
                                                timeout_seconds=timeout_seconds)
