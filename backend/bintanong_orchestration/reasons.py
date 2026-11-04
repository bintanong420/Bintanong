"""Why a turn was not answered, as a stable machine-readable code (audit A03, 4 Nov 2026).

The public answer status stays as it was; the reason says which boundary stopped the turn, so a dialogue the host
could not follow is never reported as information missing from the reviewed sources. Every routing diagnostic is
mapped here explicitly (tests/test_orchestration_reasons.py checks the inventory).
"""
from __future__ import annotations

from typing import Literal

ReasonCode = Literal[
    'dialogue_unresolved',     # the host could not follow the conversation (repair, "I already said it")
    'clarification_pending',   # a named missing fact was asked for (program, course, result, term)
    'route_interpretation',    # the router reply could not be read into a supported request
    'capability_unavailable',  # the request needs an operation, language or path this build does not offer
    'retrieval_coverage',      # retrieval or answer coverage found nothing that answers the question
    'source_incomplete',       # the reviewed source is unreviewed, clipped or has an unresolved rule
    'source_conflict',         # the reviewed evidence conflicts
    'unsupported_scope',       # outside undergraduate academic affairs
    'validation_failure',      # a candidate answer or adapter result failed host validation
    'system_error',            # model/tool outage, timeout or internal failure
]

_PENDING, _ROUTE, _CAPABILITY = 'clarification_pending', 'route_interpretation', 'capability_unavailable'
_SYSTEM = 'system_error'

# Router and validation diagnostics -> reason ('validated' and a greeting have none).
ROUTING_REASONS: dict[str, ReasonCode | None] = {
    'validated': None,
    # dialogue
    'empty_clarification': 'dialogue_unresolved',
    'dialogue_reference_missing': 'dialogue_unresolved', 'dialogue_ambiguous': 'dialogue_unresolved',
    # a specific missing fact is asked for
    'scope_conflict': _PENDING, 'unresolved_entity': _PENDING, 'compound_request': _PENDING,
    'bare_program_name': _PENDING, 'facts_noted': _PENDING, 'missing_scope': _PENDING, 'missing_term': _PENDING,
    'course_not_in_curriculum': _PENDING, 'conflicting_facts': _PENDING, 'missing_plan_information': _PENDING,
    'missing_earliest_start_term': _PENDING, 'program_switch_ambiguous': _PENDING,
    'transfer_direction_unstated': _PENDING,
    # the router reply could not be read
    'audience_unknown': _ROUTE, 'model_ambiguity': _ROUTE, 'inconsistent_proposal': _ROUTE,
    'unknown_requirement': _ROUTE, 'inconsistent_requirements': _ROUTE, 'part_operation_target_mismatch': _ROUTE,
    'invalid_model_output': _ROUTE, 'invalid_style_output': _ROUTE, 'invalid_reference': _ROUTE,
    'invalid_grounding': _ROUTE, 'topic_selection_unavailable': _ROUTE,
    # not offered by this build
    'unsupported_language': _CAPABILITY, 'unsupported_requirement': _CAPABILITY,
    'unsupported_operation': _CAPABILITY, 'institutional_execution_held': _CAPABILITY,
    'unsupported_signature': _CAPABILITY, 'documents_unavailable': _CAPABILITY,
    # scope
    'unsupported_scope': 'unsupported_scope', 'excluded_program_named': 'unsupported_scope',
    # model transport
    'model_timeout': _SYSTEM, 'model_connection_error': _SYSTEM, 'model_http_error': _SYSTEM,
    'invalid_server_response': _SYSTEM, 'truncated_output': _SYSTEM, 'server_response_too_large': _SYSTEM,
    'context_overflow': _SYSTEM,
}

# The model's own control (diagnostic 'model_control') -> reason.
CONTROL_REASONS: dict[str, ReasonCode | None] = {
    'clarify': _PENDING, 'greeting': None, 'unsupported_scope': 'unsupported_scope',
    'evidence_unavailable': 'retrieval_coverage'}

# Stage failures and integration statuses -> reason.
STATUS_REASONS: dict[str, ReasonCode | None] = {
    'ready': None, 'greeting': None,
    'held': _CAPABILITY, 'unsupported': _CAPABILITY,
    'timeout': _SYSTEM, 'busy': _SYSTEM, 'tool_error': _SYSTEM, 'error': _SYSTEM,
    'invalid_output': 'validation_failure', 'release_mismatch': 'validation_failure',
    'conflict': 'source_conflict', 'clarify': _PENDING, 'unknown': _PENDING,
    'no_evidence': 'retrieval_coverage', 'uncalibrated': 'retrieval_coverage',
    'unsupported_scope': 'unsupported_scope', 'evidence_unavailable': 'retrieval_coverage',
}


# Generator outcomes (CandidateAnswer.validation) that decide the reason themselves.
GENERATION_REASONS: dict[str, ReasonCode] = {
    'repair_exhausted': 'validation_failure', 'decision_withheld': 'validation_failure',
    'question_uncovered': 'retrieval_coverage', 'parts_unresolved': 'retrieval_coverage',
    'timeout': _SYSTEM, 'tool_error': _SYSTEM, 'unsupported_answer_scope': _CAPABILITY}


def answer_reason(pack, status: str, validation: str, ledger=None) -> ReasonCode | None:
    """The final reason of a candidate answer; an answered turn or a greeting has none."""
    if status in ('answered', 'greeting'):
        return None
    if validation == 'parts_unresolved' and ledger is not None and any(
            e.status == 'unavailable' and e.reason == 'source_gap' for e in ledger.entries):
        return 'source_incomplete'
    return (GENERATION_REASONS.get(validation) or pack.reason or STATUS_REASONS.get(pack.status)
            or 'validation_failure')


def routing_reason(diagnostic: str, control: str | None) -> ReasonCode | None:
    if diagnostic == 'model_control':
        return CONTROL_REASONS.get(control, _ROUTE)
    return ROUTING_REASONS.get(diagnostic, _ROUTE)


def evidence_reason(status: str, evidence=None) -> ReasonCode | None:
    """An integration status, refined by the evidence: a reviewed-source defect is not a retrieval miss."""
    if evidence is not None and status in ('no_evidence', 'unknown'):
        symbolic = evidence.symbolic
        unreviewed = any(getattr(r, 'status', None) == 'not_reviewed'
                         for r in (evidence.course_facts, evidence.term_assessment))
        if unreviewed:
            return 'source_incomplete'
        if symbolic is not None and status == 'unknown' and 'rule_unresolved' in symbolic.decision.unknown_conditions:
            return 'source_incomplete'
    return STATUS_REASONS.get(status, _SYSTEM)
