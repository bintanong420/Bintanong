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


def test_a_year_without_a_semester_lists_every_term_in_term_then_printed_order():
    listing = lookups().list_term_courses(ledger(), year=1, term='any')
    assert [c.code for c in listing.courses] == ['SYN 101', 'SYN 102', 'SYN 103']


def runtime_request(predicate, **inputs):
    from backend.bintanong_contracts.runtime import PredicateRequest
    return PredicateRequest.parse({'predicate': predicate, 'inputs': [
        {'name': k, 'value': v, 'fact_ref': None} for k, v in {'curriculum_id': SCOPE['curriculum_id'], **inputs}.items()]})


def look_up(request, value=None):
    from backend.bintanong_symbolic.runtime import CurriculumRuntime
    return CurriculumRuntime(ledger() if value is None else value).look_up(request)


def test_runtime_lists_a_term_with_printed_facts_and_release_scope():
    result = look_up(runtime_request('list_term_courses', year_level='1', semester='first_semester'))
    assert result.status == 'complete' and result.scope is not None and result.synthetic is True
    assert [(c.code, c.units, c.year, c.term, c.page) for c in result.courses] == [
        ('SYN 101', (('units.printed', '3'),), 1, 'first_semester', 1),
        ('SYN 102', (('units.printed', '2/1'),), 1, 'first_semester', 1)]


def test_runtime_course_lookup_distinguishes_unreviewed_from_unknown_courses():
    assert look_up(runtime_request('course_facts', course_id='course-syn102')).courses[0].title == 'Fictional Second Row'
    unreviewed = look_up(runtime_request('course_facts', course_id='course-syn102'), ledger(draft=('SYN 102',)))
    assert unreviewed.status == 'not_reviewed' and unreviewed.courses == ()
    assert look_up(runtime_request('course_facts', course_id='course-missing')).status == 'not_found'


def test_runtime_listing_without_full_review_returns_no_courses():
    result = look_up(runtime_request('list_term_courses', year_level='1', semester='any'), ledger(draft=('SYN 103',)))
    assert result.status == 'not_reviewed' and result.courses == () and result.scope is None


def test_runtime_lookup_of_another_curriculum_is_not_found():
    request = runtime_request('course_facts', course_id='course-syn101')
    other = request.model_copy(update={'inputs': (request.inputs[0].model_copy(update={'value': 'curriculum-other'}),
                                                  request.inputs[1])})
    assert look_up(other).status == 'not_found'


def test_runtime_course_without_reviewed_placement_is_not_reviewed():
    result = look_up(runtime_request('course_facts', course_id='course-syn101'), ledger(drop=('semester',)))
    assert result.status == 'not_reviewed' and result.courses == ()
