"""Synthetic course-fact lookups (titles, printed units, year/semester); no institutional facts."""
from __future__ import annotations

import importlib

from backend.bintanong_symbolic.authoring import build_curriculum_ledger
from backend.bintanong_tools.document_ingest.register import mint_pending_register
from contracts_fixtures import span


def lookups():
    return importlib.import_module('backend.bintanong_symbolic.course_facts')


SOURCE = mint_pending_register([{'filename': 'fictional.pdf', 'sha256': 'b' * 64,
                                 'acquisition_locator': 'shelf:fictional'}], synthetic=True)[0]
SCOPE = {'program_id': 'program-synthetic', 'curriculum_id': 'curriculum-synthetic-1'}
# code, title, printed units, year, semester, printed top (rows lower on the page print later)
ROWS = [('SYN 102', 'Fictional Second Row', '2/1', 'FIRST YEAR', 'FIRST SEMESTER', 600),
        ('SYN 101', 'Fictional First Row', '3', 'FIRST YEAR', 'FIRST SEMESTER', 700),
        ('SYN 103', 'Fictional Later Term', '3', 'FIRST YEAR', 'SECOND SEMESTER', 700),
        ('SYN 201', 'Fictional Second Year', '3', 'SECOND YEAR', 'FIRST SEMESTER', 300)]


def fact(value, top=500):
    s = span(SOURCE.byte_sha256, text=str(value))
    s['version_id'], s['bbox'] = SOURCE.version_id, [100, top, 140, top - 10]
    s['bbox_origin'], s['page_size'] = 'BOTTOMLEFT', [612, 792]
    return {'value': value, 'source_spans': [s]}


def ledger(rows=ROWS, *, drop=(), draft=()):
    courses, reviews = [], {}
    for code, title, units, year, term, top in rows:
        facts = {'course_code': fact(code, top), 'course_title': fact(title, top), 'units.printed': fact(units, top),
                 'year_level': fact(year), 'semester': fact(term)}
        for name in drop if code == 'SYN 101' else ():
            del facts[name]
        courses.append({'course_id': 'course-' + code.replace(' ', '').lower(), **SCOPE,
                        'source_version_id': SOURCE.version_id, 'facts': facts,
                        'prerequisites': {'kind': 'verified_none', 'source_spans': fact('None')['source_spans']},
                        'review_state': 'draft', 'review_refs': []})
    digests = {c['course_id']: c['content_sha256'] for c in build_curriculum_ledger(SCOPE, [SOURCE], courses)['courses']}
    for c in courses:
        if c['facts']['course_code']['value'] not in draft:
            c['review_state'], c['review_refs'] = 'reviewed', ['review-1']
    reviews = [{'review_id': 'review-1', 'source_version_id': SOURCE.version_id, 'course_digests': digests,
                'reviewer_label': 'Synthetic researcher'}]
    return build_curriculum_ledger(SCOPE, [SOURCE], courses, reviews=reviews)


def test_term_listing_names_every_reviewed_course_of_the_term_in_printed_order():
    listing = lookups().list_term_courses(ledger(), year=1, term='first_semester')
    assert listing.status == 'complete'
    assert [c.code for c in listing.courses] == ['SYN 101', 'SYN 102']
    assert [(c.title, c.units) for c in listing.courses] == [('Fictional First Row', {'units.printed': '3'}),
                                                             ('Fictional Second Row', {'units.printed': '2/1'})]
    assert all(c.source_spans for c in listing.courses)


def test_term_without_printed_courses_is_complete_and_empty_only_with_full_coverage():
    listing = lookups().list_term_courses(ledger(), year=2, term='summer')
    assert listing.status == 'complete' and listing.courses == ()


def test_course_without_reviewed_placement_makes_every_listing_unknown():
    for broken in (ledger(drop=('semester',)), ledger(draft=('SYN 101',))):
        listing = lookups().list_term_courses(broken, year=1, term='second_semester')
        assert listing.status == 'not_reviewed' and listing.courses == ()


def test_course_facts_return_printed_values_for_a_reviewed_course_only():
    facts = lookups().course_facts(ledger(), 'course-syn102')
    assert (facts.code, facts.title, facts.units, facts.year, facts.term) == (
        'SYN 102', 'Fictional Second Row', {'units.printed': '2/1'}, 1, 'first_semester')
    assert lookups().course_facts(ledger(draft=('SYN 102',)), 'course-syn102') is None
    assert lookups().course_facts(ledger(), 'course-missing') is None


def test_missing_printed_units_stay_missing_not_zero():
    facts = lookups().course_facts(ledger(drop=('units.printed',)), 'course-syn101')
    assert facts.units == {}
