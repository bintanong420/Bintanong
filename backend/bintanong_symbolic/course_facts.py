"""Deterministic lookups of reviewed printed course facts (title, units, year level, semester).

Values are returned as printed; nothing is computed or defaulted. A curriculum whose courses do not
all carry a reviewed placement cannot be listed by term (unknown, never a partial list).
"""
from __future__ import annotations

from dataclasses import dataclass

YEARS = {'FIRST YEAR': 1, 'SECOND YEAR': 2, 'THIRD YEAR': 3, 'FOURTH YEAR': 4, 'FIFTH YEAR': 5}
TERMS = {'FIRST SEMESTER': 'first_semester', 'SECOND SEMESTER': 'second_semester', 'SUMMER': 'summer'}
UNIT_FIELDS = ('units.printed', 'units.total', 'units.lecture', 'units.lab', 'units.rle')


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
    return code['page'], -bbox[1], bbox[0]


def list_term_courses(ledger, *, year: int, term: str) -> TermListing:
    courses = ledger['courses']
    placed = [_facts(c) for c in courses if _reviewed(c)]
    if len(placed) != len(courses) or any(f.year is None or f.term is None for f in placed):
        return TermListing('not_reviewed', ())
    chosen = sorted((c for c in courses if (YEARS.get(c['facts']['year_level']['value']),
                     TERMS.get(c['facts']['semester']['value'])) == (year, term)), key=_printed_order)
    return TermListing('complete', tuple(_facts(c) for c in chosen))
