"""Deterministic lookups of reviewed printed course facts (title, units, year level, semester).

Values are returned as printed; nothing is computed or defaulted. A curriculum whose courses do not
all carry a reviewed placement cannot be listed by term (unknown, never a partial list).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from pydantic import Field, model_validator

from ..bintanong_contracts.base import Contract, Record
from ..bintanong_contracts.runtime import BoundInput
from ..bintanong_contracts.symbolic import DecisionScope

YEARS = {'FIRST YEAR': 1, 'SECOND YEAR': 2, 'THIRD YEAR': 3, 'FOURTH YEAR': 4, 'FIFTH YEAR': 5}
TERMS = {'FIRST SEMESTER': 'first_semester', 'SECOND SEMESTER': 'second_semester', 'SUMMER': 'summer'}
TERM_ORDER = tuple(TERMS.values())
UNIT_FIELDS = ('units.printed', 'units.total', 'units.lecture', 'units.lab', 'units.rle')
Term = Literal['first_semester', 'second_semester', 'summer']


@dataclass(frozen=True)
class CourseFacts:
    course_id: str
    code: str
    title: str | None
    units: dict
    year: int | None
    term: str | None
    source_spans: tuple


@dataclass(frozen=True)
class TermListing:
    status: str  # complete | not_reviewed
    courses: tuple


class PrintedCourse(Record):
    course_id: str = Field(min_length=1, max_length=128)
    code: str = Field(min_length=1)
    title: str | None
    units: tuple[tuple[str, str], ...]  # (fact field, printed value); empty when units are not printed
    year: int = Field(ge=1, le=5)
    term: Term
    page: int = Field(ge=1)
    version_id: str = Field(min_length=1)


class CourseFactsResult(Contract):
    SCHEMA_VERSION = 'bintanong-course-facts-result-v1'
    synthetic: bool
    predicate: Literal['course_facts', 'list_term_courses']
    inputs: tuple[BoundInput, ...]
    status: Literal['complete', 'not_reviewed', 'not_found', 'unsupported']
    courses: tuple[PrintedCourse, ...]
    scope: DecisionScope | None

    @model_validator(mode='after')
    def _boundaries(self):
        if (self.status == 'complete') != (self.scope is not None):
            raise ValueError('only a complete lookup carries its release scope')
        if self.status != 'complete' and self.courses:
            raise ValueError('only a complete lookup lists printed facts')
        if self.predicate == 'course_facts' and self.status == 'complete' and len(self.courses) != 1:
            raise ValueError('a course lookup names exactly one course')
        return self


def _reviewed(course) -> bool:
    return course['review_state'] == 'reviewed' and bool(course['review_refs'])


def _facts(course) -> CourseFacts:
    facts = course['facts']
    value = lambda name: facts[name]['value'] if name in facts else None
    return CourseFacts(course_id=course['course_id'], code=value('course_code'), title=value('course_title'),
                       units={f: facts[f]['value'] for f in UNIT_FIELDS if f in facts},
                       year=YEARS.get(value('year_level')), term=TERMS.get(value('semester')),
                       source_spans=tuple(s for f in facts.values() for s in f['source_spans']))


def course_facts(ledger, course_id) -> CourseFacts | None:
    course = next((c for c in ledger['courses'] if c['course_id'] == course_id), None)
    return _facts(course) if course is not None and _reviewed(course) else None


def _printed_order(course):
    code = course['facts']['course_code']['source_spans'][0]
    bbox = code['bbox'] or [0, 0, 0, 0]
    return TERM_ORDER.index(TERMS[course['facts']['semester']['value']]), code['page'], -bbox[1], bbox[0]


def list_term_courses(ledger, *, year: int, term: str) -> TermListing:
    """term is one of TERM_ORDER, or 'any' for every term of the year (term order, then printed order)."""
    courses = ledger['courses']
    placed = [_facts(c) for c in courses if _reviewed(c)]
    if len(placed) != len(courses) or any(f.year is None or f.term is None for f in placed):
        return TermListing('not_reviewed', ())
    chosen = sorted((c for c in courses if YEARS.get(c['facts']['year_level']['value']) == year
                     and term in ('any', TERMS.get(c['facts']['semester']['value']))), key=_printed_order)
    return TermListing('complete', tuple(_facts(c) for c in chosen))


def printed_course(ledger, facts: CourseFacts) -> dict:
    """Contract data for one reviewed course, cited by its printed code's page and source version."""
    course = next(c for c in ledger['courses'] if c['course_id'] == facts.course_id)
    code = course['facts']['course_code']['source_spans'][0]
    return dict(course_id=facts.course_id, code=facts.code, title=facts.title,
                units=tuple((f, str(v)) for f, v in facts.units.items()), year=facts.year, term=facts.term,
                page=code['page'], version_id=code['version_id'])
