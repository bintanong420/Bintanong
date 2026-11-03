"""Prerequisite checks for every reviewed course of one term (memory/eligibility plan, Task 4).

The host lists the term's reviewed courses, then runs the registered prerequisite check on each with the same
release and the same student facts; no new rule is executed and nothing is ranked or recommended. A term with no
reviewed rows is reported as not covered by the source, never as a term without courses. Earlier explicit failures
are checked separately as possible retakes. Prerequisite results say nothing about offerings, slots or approval.
"""
from __future__ import annotations

import json
from typing import Literal

from pydantic import Field

from ..bintanong_contracts.base import Contract, Record
from ..bintanong_contracts.runtime import BoundInput, PredicateRequest
from ..bintanong_contracts.source import SourceSpan
from ..bintanong_contracts.symbolic import DecisionScope

OPERATION = 'assess_term_prerequisites'
MAX_SPANS = 24  # generation evidence stays within its card limit


class TermCourseCheck(Record):
    course_id: str = Field(min_length=1, max_length=128)
    code: str = Field(min_length=1)
    title: str | None
    page: int = Field(ge=1)  # the printed code's page and source version (provenance of the listing)
    version_id: str = Field(min_length=1)
    group: Literal['met', 'blocked', 'needs_info', 'already_passed']
    retake: bool = False
    outcome: Literal['eligible', 'ineligible', 'unknown', 'unsupported', 'error']
    violated: tuple[str, ...] = ()
    missing: tuple[str, ...] = ()
    unresolved_reason: str | None = None


class TermAssessmentResult(Contract):
    SCHEMA_VERSION = 'bintanong-term-assessment-v1'
    synthetic: bool
    predicate: Literal['assess_term_prerequisites']
    inputs: tuple[BoundInput, ...]
    status: Literal['complete', 'partial', 'not_covered', 'not_reviewed', 'not_found', 'unsupported']
    courses: tuple[TermCourseCheck, ...] = ()
    covered_terms: tuple[str, ...] = ()  # 'year:term' with reviewed rows in this edition
    scope: DecisionScope | None = None
    rule_ids: tuple[str, ...] = ()
    rule_spans: tuple[SourceSpan, ...] = ()


def _request(predicate, curriculum, **inputs):
    return PredicateRequest.parse({'predicate': predicate, 'inputs': [
        {'name': 'curriculum_id', 'value': curriculum, 'fact_ref': None},
        *({'name': name, 'value': value, 'fact_ref': None} for name, value in inputs.items())]})


def assess_term(runtime, request, facts, retakes=None) -> TermAssessmentResult:
    """runtime: a CurriculumRuntime; facts: projected StudentFacts; retakes: course ids the student explicitly
    failed (defaults to every noncompletion fact)."""
    request = PredicateRequest.parse(request.model_dump(mode='json'))
    if request.predicate != OPERATION:
        raise ValueError('unsupported_operation')
    args = {i.name: i.value for i in request.inputs}
    curriculum, year, semester = args['curriculum_id'], args['year_level'], args['semester']
    listing = runtime.look_up(_request('list_term_courses', curriculum, year_level=year, semester=semester))

    def result(status, **values):
        return TermAssessmentResult(schema_version=TermAssessmentResult.SCHEMA_VERSION, synthetic=listing.synthetic,
                                    predicate=OPERATION, inputs=request.inputs, status=status, **values)
    if listing.status != 'complete':
        return result(listing.status)
    covered = sorted({f'{c.year}:{c.term}' for y in range(1, 6) for c in runtime.look_up(
        _request('list_term_courses', curriculum, year_level=str(y), semester='any')).courses})
    if not listing.courses:
        return result('not_covered', covered_terms=tuple(covered), scope=listing.scope)
    passed, spans, rule_ids, failures = set(facts.passed), {}, {}, []

    def check(course, retake):
        checked = runtime.check(_request('check_prerequisite_eligibility', curriculum, course_id=course.course_id), facts)
        decision = checked.decision
        outcome = decision.outcome
        if outcome in ('unsupported', 'error'):
            failures.append(course.course_id)
        group = {'eligible': 'met', 'ineligible': 'blocked'}.get(outcome, 'needs_info')
        if not retake and course.course_id in passed:
            group = 'already_passed'
        for span in checked.rule_spans:
            spans.setdefault(json.dumps(span.model_dump(mode='json'), sort_keys=True), span)
        rule_ids.update(dict.fromkeys(checked.rule_ids))
        requirement = checked.requirement
        return TermCourseCheck(course_id=course.course_id, code=course.code, title=course.title, page=course.page,
                               version_id=course.version_id, group=group,
                               retake=retake, outcome=outcome, violated=decision.violated_conditions,
                               missing=tuple(c for c in decision.missing_facts + decision.unknown_conditions
                                             if c.startswith(('completion_unknown:', 'enrollment_unknown:'))),
                               unresolved_reason=(requirement.reason if requirement is not None
                                                  and requirement.kind == 'unresolved' else None))
    courses = [check(c, False) for c in listing.courses]
    listed = {c.course_id for c in listing.courses}
    for course_id in dict.fromkeys(facts.failed if retakes is None else retakes):
        if course_id in listed:
            continue
        found = runtime.look_up(_request('course_facts', curriculum, course_id=course_id))
        if found.status == 'complete':
            courses.append(check(found.courses[0], True))
    return result('partial' if failures else 'complete', courses=tuple(courses), covered_terms=tuple(covered),
                  scope=listing.scope, rule_ids=tuple(rule_ids), rule_spans=tuple(spans.values())[:MAX_SPANS])
