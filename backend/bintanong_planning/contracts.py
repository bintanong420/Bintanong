"""Typed contracts for "Check my plan" (academic recovery plan of action, Step 2).

A plan is the student's own proposal: ordered terms, each with courses and how each would be taken. A check result
is a verdict per term; it never states an offering, an approval, a grade or academic standing. Course ids are the
reviewed ledger's ids; nothing here names a program or a course.
"""
from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field, model_validator

from ..bintanong_contracts.base import Contract, Record
from ..bintanong_contracts.source import SourceSpan
from ..bintanong_contracts.symbolic import DecisionScope
from ..bintanong_routing.contracts import State

CourseId = Annotated[str, Field(min_length=1, max_length=128)]
Text = Annotated[str, Field(min_length=1, max_length=400)]
Units = Annotated[float, Field(ge=0, allow_inf_nan=False)]
Mode = Literal['prescribed', 'retake', 'special_class_request', 'off_semester_request', 'summer']
# Modes that depend on an offering or approval the checker cannot confirm.
REQUESTED_MODES = ('special_class_request', 'off_semester_request', 'summer')
MAX_TERMS = 12
MAX_COURSES = 16


class StatedFact(Record):
    """A course result as the student stated it (same states as the session facts)."""
    course_id: CourseId
    state: State


class PlanCourse(Record):
    course_id: CourseId
    mode: Mode


class PlanTerm(Record):
    kind: Literal['regular', 'summer']
    year_level: int | None = Field(ge=1, le=5)  # the prescribed term a regular term stands for
    semester: Literal['first_semester', 'second_semester'] | None
    courses: tuple[PlanCourse, ...] = Field(min_length=1, max_length=MAX_COURSES)

    @model_validator(mode='after')
    def _shape(self):
        if (self.kind == 'regular') != (self.year_level is not None and self.semester is not None):
            raise ValueError('a regular term names its prescribed year and semester; a summer term names neither')
        if self.kind == 'summer' and (self.year_level is not None or self.semester is not None):
            raise ValueError('a summer term names no prescribed semester')
        if any((c.mode == 'summer') != (self.kind == 'summer') for c in self.courses):
            raise ValueError('summer mode is used exactly for summer-term courses')
        if len({c.course_id for c in self.courses}) != len(self.courses):
            raise ValueError('a course appears once per term')
        return self


class PlanCheckRequest(Contract):
    SCHEMA_VERSION = 'bintanong-plan-check-request-v1'
    curriculum_id: CourseId
    facts: tuple[StatedFact, ...] = Field(default=(), max_length=256)
    terms: tuple[PlanTerm, ...] = Field(min_length=1, max_length=MAX_TERMS)


class PlanReason(Record):
    kind: Literal['unmet_prerequisite', 'prerequisite_unknown', 'units_missing', 'not_in_curriculum', 'rule_error']
    course_id: CourseId
    missing: tuple[CourseId, ...] = ()  # the courses whose completion (or same-term enrollment) is lacking/unknown
    detail: Text | None = None


class PolicyClauseRef(Record):
    topic: Text
    page: int = Field(ge=1)
    text: Text


class PlanWarning(Record):
    kind: Literal['load_above_prescribed', 'summer_above_normal']
    severity: Literal['major']
    units: Units
    ceiling: Units
    clause: PolicyClauseRef


class UnconfirmedCondition(Record):
    course_id: CourseId
    kind: Literal['special_class_request', 'off_semester_request', 'summer']
    text: Literal['requested, not confirmed']


class AssumedPass(Record):
    """A course counted as passed for later terms of this request only; never a stated or stored result."""
    course_id: CourseId
    from_term: int = Field(ge=0)


class LoadCheck(Record):
    status: Literal['within', 'above', 'unknown']
    units: Units | None
    ceiling: Units | None
    reason: Text | None = None

    @model_validator(mode='after')
    def _known(self):
        if self.status != 'unknown' and (self.units is None or self.ceiling is None):
            raise ValueError('a decided load names its units and ceiling')
        if (self.status == 'unknown') != (self.reason is not None):
            raise ValueError('only an unknown load carries a reason')
        return self


class TermVerdict(Record):
    index: int = Field(ge=0)
    outcome: Literal['works', 'works_with_warning', 'blocked', 'unknown']
    reasons: tuple[PlanReason, ...] = ()
    warnings: tuple[PlanWarning, ...] = ()
    unconfirmed: tuple[UnconfirmedCondition, ...] = ()
    load: LoadCheck
    assumed: tuple[AssumedPass, ...] = ()  # earlier-term assumed passes in effect when this term was checked

    @model_validator(mode='after')
    def _consistent(self):
        blocked = any(r.kind == 'unmet_prerequisite' for r in self.reasons)
        unknown = bool(self.reasons) and not blocked or self.load.status == 'unknown'
        expected = ('blocked' if blocked else 'unknown' if unknown
                    else 'works_with_warning' if self.warnings else 'works')
        if self.outcome != expected:
            raise ValueError('term outcome must follow its reasons, load and warnings')
        return self


class PlanCheckResult(Contract):
    SCHEMA_VERSION = 'bintanong-plan-check-result-v1'
    synthetic: bool
    curriculum_id: CourseId
    terms: tuple[TermVerdict, ...] = Field(min_length=1, max_length=MAX_TERMS)
    policy_id: Text | None
    scope: DecisionScope | None = None
    rule_ids: tuple[Text, ...] = ()
    rule_spans: tuple[SourceSpan, ...] = ()
