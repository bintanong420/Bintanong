"""Execution-domain boundaries for Bintanong's reviewed academic operations.

A policy document is not a Prolog program. Symbolic operations are limited to
reviewed curriculum/catalog capabilities; documentary policies use RAG unless
the student's request independently needs a supported curriculum operation.

This is a host-owned allowlist, not a model-provided or source-derived predicate.
It cannot establish semantic intent on its own; live model evaluation still must
measure whether a question was assigned the correct part/operation.
"""
from __future__ import annotations

from typing import Literal

Domain = Literal['curriculum_catalog', 'curriculum_constraints']

# Printed, reviewed curriculum data: no student-specific constraint decision.
CURRICULUM_CATALOG_OPERATIONS = frozenset({
    'list_course_prerequisites', 'course_facts', 'list_term_courses',
})

# Bounded operations that evaluate a curriculum/dependency/plan condition.
CURRICULUM_CONSTRAINT_OPERATIONS = frozenset({
    'check_prerequisite_eligibility', 'list_missing_prerequisites',
    'list_affected_courses', 'assess_term_prerequisites', 'check_study_plan',
    'earliest_course_term',
})

# Keep ordering stable for existing prompt, evaluation and registry consumers.
OPERATIONS = ('check_prerequisite_eligibility', 'list_course_prerequisites',
              'list_missing_prerequisites', 'list_affected_courses', 'course_facts',
              'list_term_courses', 'assess_term_prerequisites', 'check_study_plan',
              'earliest_course_term')

if (set(OPERATIONS) != CURRICULUM_CATALOG_OPERATIONS | CURRICULUM_CONSTRAINT_OPERATIONS
        or CURRICULUM_CATALOG_OPERATIONS & CURRICULUM_CONSTRAINT_OPERATIONS):
    raise RuntimeError('invalid_curriculum_operation_partition')


def operation_domain(name: str) -> Domain | None:
    """Unknown names are not valid symbolic capabilities, regardless of registry injection."""
    if name in CURRICULUM_CATALOG_OPERATIONS:
        return 'curriculum_catalog'
    if name in CURRICULUM_CONSTRAINT_OPERATIONS:
        return 'curriculum_constraints'
    return None


def route_for_evidence_needs(needs) -> Literal['RAG', 'Symbolic', 'Hybrid'] | None:
    """Route by the requested parts' evidence requirements, not by policy keywords.

    An unknown part is not silently turned into RAG or discarded: return None so
    the caller can ask for clarification. This function never executes either
    evidence subsystem.
    """
    kinds = frozenset(needs)
    if not kinds or not kinds <= {'document', 'structured'}:
        return None
    if kinds == {'document'}:
        return 'RAG'
    if kinds == {'structured'}:
        return 'Symbolic'
    return 'Hybrid'
