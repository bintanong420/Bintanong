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


# Ask mode drafts (plan of action, Steps 3-5; owner 4 Nov 2026). Each draft is the greedy prerequisite chain from one
# failed course, already run through check_plan; it is a draft for adviser review, never an approval or an offering.
Quote = Annotated[str, Field(min_length=1, max_length=1200)]
Semester = Literal['first_semester', 'second_semester', 'summer']
Variant = Literal['A', 'B', 'C']  # A regular offerings only; B with special-class requests; C with summer too


class RouteClause(Record):
    """A printed Handbook clause quoted verbatim from the reviewed release chunks."""
    kind: Literal['regular_class', 'special_class', 'off_semester', 'summer']
    topic: Text
    page: int = Field(ge=1)
    text: Quote
    conditions: tuple[Text, ...] = Field(default=(), max_length=4)

    @model_validator(mode='after')
    def _quoted(self):
        if any(c not in self.text for c in self.conditions):
            raise ValueError('a condition is quoted from its own clause')
        return self


class RecoveryRoutes(Contract):
    SCHEMA_VERSION = 'bintanong-recovery-routes-v1'
    routes_id: Text
    synthetic: bool
    clauses: tuple[RouteClause, ...] = Field(min_length=4, max_length=4)
    source_chunk_ids: tuple[Text, ...] = Field(min_length=1)
    review_refs: tuple[Text, ...] = Field(min_length=1)

    @model_validator(mode='after')
    def _each_route_once(self):
        if sorted(c.kind for c in self.clauses) != ['off_semester', 'regular_class', 'special_class', 'summer']:
            raise ValueError('one clause per recovery route')
        return self

    def clause(self, kind: str) -> RouteClause:
        return next(c for c in self.clauses if c.kind == kind)


class TermRef(Record):
    year: int = Field(ge=1, le=5)  # for summer: the year it follows
    semester: Semester


class PlacedCourse(Record):
    course_id: CourseId
    mode: Mode


class DraftTerm(Record):
    term: TermRef
    moved: tuple[PlacedCourse, ...] = Field(max_length=MAX_COURSES)  # the failed course and the courses it delays
    kept: tuple[CourseId, ...] = Field(max_length=MAX_COURSES)  # the student's other prescribed courses of the term
    verdict: TermVerdict


class Draft(Record):
    variant: Variant
    terms: tuple[DraftTerm, ...] = Field(min_length=1, max_length=MAX_TERMS)
    requests: int = Field(ge=0)  # courses that need an offering or approval the checker cannot confirm
    beyond_curriculum: bool  # the last delayed course falls after the curriculum's last prescribed term


class DroppedDraft(Record):
    variant: Variant
    reason: Literal['same_as', 'blocked', 'not_placed', 'no_summer_policy', 'too_long']
    same_as: Variant | None = None
    course_id: CourseId | None = None
    missing: tuple[CourseId, ...] = ()
    term: TermRef | None = None


class RecoveryResult(Contract):
    SCHEMA_VERSION = 'bintanong-recovery-result-v1'
    synthetic: bool
    curriculum_id: CourseId
    failed_course_id: CourseId
    failed_term: TermRef  # the failed course's prescribed term
    start_term: TermRef  # the first term the drafts plan
    term_stated: bool  # True when the student named the term; otherwise the start is assumed and the reply says so
    next_offering: TermRef | None  # the failed course's next regular offering from the start term
    regular_asked: bool = False  # the student said "regular": the reply explains it means the prescribed sequence
    clauses: tuple[RouteClause, ...] = Field(min_length=4, max_length=4)
    drafts: tuple[Draft, ...] = Field(max_length=3)
    dropped: tuple[DroppedDraft, ...] = Field(max_length=3)
    policy_id: Text | None

    @model_validator(mode='after')
    def _variants(self):
        variants = [d.variant for d in self.drafts] + [d.variant for d in self.dropped]
        if sorted(variants) != ['A', 'B', 'C']:
            raise ValueError('each variant is drafted or dropped once')
        return self
