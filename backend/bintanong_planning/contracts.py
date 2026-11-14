"""Typed contracts for "Check my plan" (academic recovery plan of action, Step 2).

A plan is the student's own proposal: ordered terms, each with courses and how each would be taken. A check result
is a verdict per term; it never states an offering, an approval, a grade or academic standing. Course ids are the
reviewed ledger's ids; nothing here names a program or a course.
"""
from __future__ import annotations

import hashlib
import json

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


Grade = Literal['4.0', 'INC', '5.0']
OPEN_GRADES = ('4.0', 'INC')  # grades the Handbook lets a student remove or complete (pp. 46-47); 5.0 is not one
Standing = Literal['warning', 'probation', 'scholastic_delinquency']


class StatedGrade(Record):
    """A grade the student said they got; never a verified university record."""
    course_id: CourseId
    grade: Grade


class StudentStatus(Record):
    """What the student said about themselves, as the router read it this turn (Track A, owner 4 Nov 2026).

    Every field is the student's own statement: Bintanong never computes academic standing, graduation status or a
    grade. The router fills it; without it every flag is off and no status-dependent route is mentioned.
    """
    graduating: bool = False  # "graduating ako" / "I'm graduating"
    last_semester: bool = False  # "last sem ko na" / "this is my last semester"
    standing: Standing | None = None  # a stated warning, probation or scholastic delinquency
    stopping: bool = False  # the student says they will stop or take a break from studies
    not_offered: bool = False  # the student says the course is not offered
    grades: tuple[StatedGrade, ...] = Field(default=(), max_length=64)

    @model_validator(mode='after')
    def _one_grade_per_course(self):
        if len({g.course_id for g in self.grades}) != len(self.grades):
            raise ValueError('one stated grade per course')
        return self

    def grade(self, course_id: str) -> str | None:
        return next((g.grade for g in self.grades if g.course_id == course_id), None)


class PlanCheckRequest(Contract):
    SCHEMA_VERSION = 'bintanong-plan-check-request-v1'
    curriculum_id: CourseId
    facts: tuple[StatedFact, ...] = Field(default=(), max_length=256)
    terms: tuple[PlanTerm, ...] = Field(min_length=1, max_length=MAX_TERMS)
    # Omitted from the dump when absent, so the digest of a request without a stated status is unchanged.
    status: StudentStatus | None = Field(default=None, exclude_if=lambda value: value is None)


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
    # Courses this term re-enrolls while the student stated an open 4.0/INC in them (Track A 4): a heads-up.
    open_removals: tuple[CourseId, ...] = Field(default=(), max_length=MAX_COURSES, exclude_if=lambda value: not value)

    @model_validator(mode='after')
    def _consistent(self):
        blocked = any(r.kind == 'unmet_prerequisite' for r in self.reasons)
        unknown = bool(self.reasons) and not blocked  # a load of unknown status is its own line (ARP-04)
        expected = ('blocked' if blocked else 'unknown' if unknown
                    else 'works_with_warning' if self.warnings or self.open_removals else 'works')
        if self.outcome != expected:
            raise ValueError('term outcome must follow its reasons, load and warnings')
        return self


def plan_request_digest(request: PlanCheckRequest, policy_id, policy_sha256) -> str:
    request = PlanCheckRequest.parse(request.model_dump(mode='json'))
    data = dict(request=request.model_dump(mode='json'), policy_id=policy_id, policy_sha256=policy_sha256)
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False, allow_nan=False).encode('utf-8')).hexdigest()


class PlanCheckResult(Contract):
    SCHEMA_VERSION = 'bintanong-plan-check-result-v2'
    synthetic: bool
    curriculum_id: CourseId
    terms: tuple[TermVerdict, ...] = Field(min_length=1, max_length=MAX_TERMS)
    checked_request: PlanCheckRequest
    request_sha256: str = Field(pattern=r'^[0-9a-f]{64}$')
    policy_id: Text | None
    policy_sha256: str | None = Field(pattern=r'^[0-9a-f]{64}$')
    scope: DecisionScope | None = None
    rule_ids: tuple[Text, ...] = ()
    rule_spans: tuple[SourceSpan, ...] = ()

    @model_validator(mode='after')
    def _request_bound(self):
        if (self.curriculum_id != self.checked_request.curriculum_id
                or len(self.terms) != len(self.checked_request.terms)
                or tuple(t.index for t in self.terms) != tuple(range(len(self.terms)))
                or (self.policy_id is None) != (self.policy_sha256 is None)
                or self.request_sha256 != plan_request_digest(self.checked_request, self.policy_id,
                                                              self.policy_sha256)):
            raise ValueError('plan_result_request_binding_mismatch')
        return self


# Ask mode drafts (plan of action, Steps 3-5; owner 4 Nov 2026). Each draft is the greedy prerequisite chain from one
# failed course, already run through check_plan; it is a draft for adviser review, never an approval or an offering.
Quote = Annotated[str, Field(min_length=1, max_length=1200)]
Semester = Literal['first_semester', 'second_semester', 'summer']
Variant = Literal['A', 'B', 'C', 'D']  # A regular; B special; C earliest summer; D just in time


CORE_ROUTES = ('off_semester', 'regular_class', 'special_class', 'summer')
# Optional clauses (Track A, owner 4 Nov 2026), each quoted only when the student's stated status makes it relevant.
CITED_ROUTES = ('removal_period', 'removal_one_year', 'removal_before_enrollment', 'removal_forfeit', 'overload',
                'prerequisite_waiver', 'cross_enrollment', 'substitution', 'substitution_limit', 'leave_of_absence',
                'advance_courses')
MAX_CLAUSES = len(CORE_ROUTES) + len(CITED_ROUTES)


class RouteClause(Record):
    """A printed Handbook clause quoted verbatim from the reviewed release chunks."""
    kind: Literal['regular_class', 'special_class', 'off_semester', 'summer', 'removal_period', 'removal_one_year',
                  'removal_before_enrollment', 'removal_forfeit', 'overload', 'prerequisite_waiver',
                  'cross_enrollment', 'substitution', 'substitution_limit', 'leave_of_absence', 'advance_courses']
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
    clauses: tuple[RouteClause, ...] = Field(min_length=4, max_length=MAX_CLAUSES)
    source_chunk_ids: tuple[Text, ...] = Field(min_length=1)
    review_refs: tuple[Text, ...] = Field(min_length=1)

    @model_validator(mode='after')
    def _each_route_once(self):
        _check_clause_kinds(self.clauses)
        return self

    def clause(self, kind: str) -> RouteClause:
        return next(c for c in self.clauses if c.kind == kind)


def _check_clause_kinds(clauses):
    kinds = [c.kind for c in clauses]
    if len(set(kinds)) != len(kinds) or not set(CORE_ROUTES) <= set(kinds):
        raise ValueError('one clause per recovery route')


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
    # The first term from which every delayed course is back in its own prescribed term (None: after year five).
    rejoin_term: TermRef | None = None


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
    fastest_asked: bool = Field(default=False, exclude_if=lambda value: not value)  # "fastest" / "pinakamabilis"
    clauses: tuple[RouteClause, ...] = Field(min_length=4, max_length=MAX_CLAUSES)
    drafts: tuple[Draft, ...] = Field(max_length=4)
    dropped: tuple[DroppedDraft, ...] = Field(max_length=4)
    policy_id: Text | None
    # The student's own statements (Track A); omitted from the dump when absent.
    status: StudentStatus | None = Field(default=None, exclude_if=lambda value: value is None)
    # Courses prescribed in the first regular semester of the drafts that need the failed course; filled only for a
    # stated 4.0/INC (removal before enrollment, Handbook 3.5).
    removal_needed_by: tuple[CourseId, ...] = Field(default=(), max_length=MAX_COURSES * 2,
                                                    exclude_if=lambda value: not value)

    @model_validator(mode='after')
    def _variants(self):
        variants = [d.variant for d in self.drafts] + [d.variant for d in self.dropped]
        if sorted(variants) != ['A', 'B', 'C', 'D']:
            raise ValueError('each variant is drafted or dropped once')
        _check_clause_kinds(self.clauses)
        if self.removal_needed_by and self.failed_grade not in OPEN_GRADES:
            raise ValueError('removal applies only to a stated 4.0 or INC')
        return self

    @property
    def failed_grade(self) -> str | None:
        return None if self.status is None else self.status.grade(self.failed_course_id)
