"""Units as printed (owner decision, 4 Nov 2026): most reviewed ledgers carry only `units.printed`. A plain number is
the total; "a/b" is lecture units / lab units, total a+b (LEC_LAB_SUM_READING); anything else stays unknown. The
printed value itself is never changed. Synthetic curriculum only."""
import pytest

from backend.bintanong_planning import checker
from backend.bintanong_planning.checker import check_plan, printed_total
from backend.bintanong_symbolic.authoring import build_curriculum_ledger
from backend.bintanong_symbolic.runtime import CurriculumRuntime
from test_planning_check import POLICY, cid, plan, regular
from test_symbolic_course_facts import SOURCE, fact


@pytest.mark.parametrize('printed,on,off', [
    ('3', 3.0, 3.0), (' 3 ', 3.0, 3.0), ('1.5', 1.5, 1.5), ('2/1', 3.0, None), ('3/0', 3.0, None),
    ('None', None, None), ('2 /2', None, None), ('', None, None), ('3 (lab)', None, None), (None, None, None)])
def test_printed_units_reading(printed, on, off):
    assert printed_total(printed, lec_lab_sum=True) == on
    assert printed_total(printed, lec_lab_sum=False) == off


def test_the_owner_reading_is_on_by_default():
    assert checker.LEC_LAB_SUM_READING is True and printed_total('2/1') == 3.0


def _runtime():
    scope = {'program_id': 'program-synthetic', 'curriculum_id': 'curriculum-units-1'}
    spans = fact('rule')['source_spans']
    courses = []
    for top, (code, printed, term) in enumerate((('UNT 1', '3', 'FIRST SEMESTER'), ('UNT 2', '2/1', 'FIRST SEMESTER'),
                                                 ('UNT 3', 'None', 'SECOND SEMESTER'))):
        courses.append({'course_id': cid(code), **scope, 'source_version_id': SOURCE.version_id,
                        'facts': {'course_code': fact(code, 700 - top * 10), 'course_title': fact('Fictional ' + code),
                                  'year_level': fact('FIRST YEAR'), 'semester': fact(term),
                                  'units.printed': fact(printed)},
                        'prerequisites': {'kind': 'verified_none', 'source_spans': spans},
                        'review_state': 'draft', 'review_refs': []})
    digests = {c['course_id']: c['content_sha256'] for c in build_curriculum_ledger(scope, [SOURCE], courses)['courses']}
    for c in courses:
        c['review_state'], c['review_refs'] = 'reviewed', ['review-1']
    reviews = [{'review_id': 'review-1', 'source_version_id': SOURCE.version_id, 'course_digests': digests,
                'reviewer_label': 'Synthetic researcher'}]
    return CurriculumRuntime(build_curriculum_ledger(scope, [SOURCE], courses, reviews=reviews))


def test_a_plan_reads_loads_from_printed_units():
    runtime = _runtime()
    two = check_plan(plan('curriculum-units-1', [], regular(1, 'first_semester', (cid('UNT 1'), 'prescribed'),
                                                             (cid('UNT 2'), 'prescribed'))), runtime, POLICY)
    assert (two.terms[0].load.status, two.terms[0].load.units) == ('within', 6)
    three = check_plan(plan('curriculum-units-1', [], regular(1, 'first_semester', (cid('UNT 1'), 'prescribed'),
                                                               (cid('UNT 3'), 'prescribed'))), runtime, POLICY)
    assert (three.terms[0].load.status, three.terms[0].load.reason) == ('unknown', 'units not printed as totals')
    assert three.terms[0].outcome == 'works'
