"""Academic recovery Step 2, "Check my plan": each proposed term is checked in order against reviewed prerequisite
rules on the start-of-term state, earlier terms count only as request-local assumed passes, and the unit load is
compared with the reviewed load policy (D5: the semester's prescribed total is a ceiling shown as a major warning,
never a block). Synthetic curricula only; the same tests run on a second curriculum with unfamiliar codes.

Shape (logical names; each curriculum prints its own codes):
  1:1  BASE (3), AUX (3)                      no prerequisites
  1:2  PAIR_A (3) co-requisite PAIR_B; PAIR_B (3)
  2:1  X (3) needs BASE; FILL (3)
  2:2  D1 (3) needs X; D2 (3) needs X; Y (3) needs X and AUX; LINK (3) blank cell (no prerequisite)
  3:1  T0 (3) needs LINK; T1..T6 (3 each)     prescribed total 21
  3:2  Z (3) needs D1; GAP (no printed units)
"""
import pytest

from backend.bintanong_planning.checker import check_plan
from backend.bintanong_planning.contracts import PlanCheckRequest, PlanCheckResult
from backend.bintanong_planning.policies import LoadPolicy
from backend.bintanong_symbolic.authoring import build_curriculum_ledger
from backend.bintanong_symbolic.runtime import CurriculumRuntime
from test_symbolic_course_facts import SOURCE, fact

FIRST, SECOND = 'FIRST SEMESTER', 'SECOND SEMESTER'
Y1, Y2, Y3 = 'FIRST YEAR', 'SECOND YEAR', 'THIRD YEAR'
SHAPE = [('BASE', Y1, FIRST, 3, None), ('AUX', Y1, FIRST, 3, None),
         ('PAIR_A', Y1, SECOND, 3, ('co_requisite', 'PAIR_B')), ('PAIR_B', Y1, SECOND, 3, None),
         ('X', Y2, FIRST, 3, ('course', 'BASE')), ('FILL', Y2, FIRST, 3, None),
         ('D1', Y2, SECOND, 3, ('course', 'X')), ('D2', Y2, SECOND, 3, ('course', 'X')),
         ('Y', Y2, SECOND, 3, ('all_of', 'X', 'AUX')), ('LINK', Y2, SECOND, 3, 'blank'),
         ('T0', Y3, FIRST, 3, ('course', 'LINK')), *((f'T{i}', Y3, FIRST, 3, None) for i in range(1, 7)),
         ('Z', Y3, SECOND, 3, ('course', 'D1')), ('GAP', Y3, SECOND, None, None)]

CURRICULA = {
    'curriculum-synthetic-1': {name: f'SYN {100 + i}' for i, (name, *_) in enumerate(SHAPE)},
    'curriculum-unfamiliar-9': {name: f'QZV-{chr(65 + i)}{i}/L' for i, (name, *_) in enumerate(SHAPE)},
}

# Synthetic fixture policy only: the real PalSU record is supplied after the owner reviews the printed clauses.
POLICY = LoadPolicy.parse({
    'schema_version': LoadPolicy.SCHEMA_VERSION, 'policy_id': 'policy-synthetic-load', 'synthetic': True,
    'regular_ceiling': 'prescribed_semester_total', 'summer_normal_units': 9,
    'clauses': [{'topic': 'synthetic_semester_load', 'page': 1, 'text': 'Fictional maximum load clause.'},
                {'topic': 'synthetic_summer_load', 'page': 1, 'text': 'Fictional summer load clause.'}],
    'review_refs': ['review-synthetic-policy']})


def cid(code):
    return 'course-' + ''.join(ch for ch in code.lower() if ch.isalnum())


def build(curriculum_id):
    codes = CURRICULA[curriculum_id]
    scope = {'program_id': 'program-synthetic', 'curriculum_id': curriculum_id}
    spans = fact('rule')['source_spans']

    def rule(value):
        if value is None:
            return {'kind': 'verified_none', 'source_spans': spans}
        if value == 'blank':
            return {'kind': 'unresolved', 'reason': 'Printed prerequisite cell is blank', 'source_spans': spans}
        if value[0] in ('course', 'co_requisite'):
            return {'kind': value[0], 'course_id': cid(codes[value[1]]), 'source_spans': spans}
        return {'kind': value[0], 'items': [rule(('course', n)) for n in value[1:]], 'source_spans': spans}
    courses = []
    for top, (name, year, term, units, prerequisite) in enumerate(SHAPE):
        facts = {'course_code': fact(codes[name], 700 - top * 10), 'course_title': fact('Fictional ' + name),
                 'year_level': fact(year), 'semester': fact(term)}
        if units is not None:
            facts['units.total'] = fact(units)
        courses.append({'course_id': cid(codes[name]), **scope, 'source_version_id': SOURCE.version_id,
                        'facts': facts, 'prerequisites': rule(prerequisite), 'review_state': 'draft', 'review_refs': []})
    digests = {c['course_id']: c['content_sha256'] for c in build_curriculum_ledger(scope, [SOURCE], courses)['courses']}
    for c in courses:
        c['review_state'], c['review_refs'] = 'reviewed', ['review-1']
    reviews = [{'review_id': 'review-1', 'source_version_id': SOURCE.version_id, 'course_digests': digests,
                'reviewer_label': 'Synthetic researcher'}]
    return CurriculumRuntime(build_curriculum_ledger(scope, [SOURCE], courses, reviews=reviews))


@pytest.fixture(params=sorted(CURRICULA), scope='module')
def curriculum(request):
    curriculum_id = request.param
    codes = CURRICULA[curriculum_id]
    return curriculum_id, build(curriculum_id), (lambda name: cid(codes[name]))


def regular(year, semester, *courses):
    return {'kind': 'regular', 'year_level': year, 'semester': semester,
            'courses': [{'course_id': c, 'mode': m} for c, m in courses]}


def summer(*courses):
    return {'kind': 'summer', 'year_level': None, 'semester': None,
            'courses': [{'course_id': c, 'mode': 'summer'} for c in courses]}


def plan(curriculum_id, facts, *terms):
    return PlanCheckRequest.parse({'schema_version': PlanCheckRequest.SCHEMA_VERSION, 'curriculum_id': curriculum_id,
                                   'facts': [{'course_id': c, 'state': s} for c, s in facts], 'terms': list(terms)})


def test_a_later_term_works_only_through_the_earlier_terms_assumed_pass(curriculum):
    curriculum_id, runtime, c = curriculum
    facts = [(c('BASE'), 'passed'), (c('X'), 'failed')]
    result = check_plan(plan(curriculum_id, facts, regular(2, 'second_semester', (c('X'), 'retake')),
                             regular(3, 'first_semester', (c('D1'), 'prescribed'))), runtime, POLICY)
    assert type(result) is PlanCheckResult
    assert [t.outcome for t in result.terms] == ['works', 'works']
    alone = check_plan(plan(curriculum_id, facts, regular(3, 'first_semester', (c('D1'), 'prescribed'))), runtime, POLICY)
    assert alone.terms[0].outcome == 'blocked'
    (reason,) = alone.terms[0].reasons
    assert (reason.kind, reason.course_id, reason.missing) == ('unmet_prerequisite', c('D1'), (c('X'),))


def test_a_course_never_taken_blocks_and_a_course_not_stated_is_unknown(curriculum):
    curriculum_id, runtime, c = curriculum
    term = regular(2, 'first_semester', (c('X'), 'prescribed'))
    blocked = check_plan(plan(curriculum_id, [(c('BASE'), 'not_taken')], term), runtime, POLICY)
    assert blocked.terms[0].outcome == 'blocked' and blocked.terms[0].reasons[0].missing == (c('BASE'),)
    unknown = check_plan(plan(curriculum_id, [], term), runtime, POLICY)
    assert unknown.terms[0].outcome == 'unknown'
    assert unknown.terms[0].reasons[0].kind == 'prerequisite_unknown'
    assert unknown.terms[0].reasons[0].missing == (c('BASE'),)


def test_a_blocked_course_is_not_assumed_passed_later(curriculum):
    curriculum_id, runtime, c = curriculum
    facts = [(c('X'), 'failed')]
    result = check_plan(plan(curriculum_id, facts, regular(2, 'second_semester', (c('D1'), 'prescribed')),
                             regular(3, 'second_semester', (c('Z'), 'prescribed'))), runtime, POLICY)
    assert [t.outcome for t in result.terms] == ['blocked', 'blocked']
    assert result.terms[1].reasons[0].missing == (c('D1'),)


def test_a_co_requisite_counts_only_when_taken_the_same_term(curriculum):
    curriculum_id, runtime, c = curriculum
    together = check_plan(plan(curriculum_id, [], regular(1, 'second_semester', (c('PAIR_A'), 'prescribed'),
                                                          (c('PAIR_B'), 'prescribed'))), runtime, POLICY)
    assert together.terms[0].outcome == 'works'
    alone = regular(1, 'second_semester', (c('PAIR_A'), 'prescribed'))
    apart = check_plan(plan(curriculum_id, [(c('PAIR_B'), 'not_taken')], alone), runtime, POLICY)
    assert apart.terms[0].outcome == 'blocked' and apart.terms[0].reasons[0].missing == (c('PAIR_B'),)
    unstated = check_plan(plan(curriculum_id, [], alone), runtime, POLICY)  # PAIR_B may already be passed
    assert unstated.terms[0].outcome == 'unknown' and unstated.terms[0].reasons[0].missing == (c('PAIR_B'),)


def test_units_above_the_prescribed_semester_total_warn_and_never_block(curriculum):
    curriculum_id, runtime, c = curriculum
    facts = [(c('LINK'), 'passed'), (c('X'), 'passed'), (c('AUX'), 'passed')]
    full = [(c(f'T{i}'), 'prescribed') for i in range(7)]
    result = check_plan(plan(curriculum_id, facts, regular(3, 'first_semester', *full, (c('Y'), 'special_class_request'))),
                        runtime, POLICY)
    term = result.terms[0]
    assert term.outcome == 'works_with_warning' and not term.reasons
    assert (term.load.status, term.load.units, term.load.ceiling) == ('above', 24, 21)
    (warning,) = term.warnings
    assert (warning.kind, warning.severity, warning.units, warning.ceiling) == ('load_above_prescribed', 'major', 24, 21)
    assert warning.clause.topic == 'synthetic_semester_load'
    at_ceiling = check_plan(plan(curriculum_id, facts, regular(3, 'first_semester', *full)), runtime, POLICY)
    assert at_ceiling.terms[0].outcome == 'works' and at_ceiling.terms[0].load.status == 'within'


def test_summer_above_the_normal_load_warns(curriculum):
    curriculum_id, runtime, c = curriculum
    facts = [(c('BASE'), 'passed'), (c('AUX'), 'passed'), (c('X'), 'passed')]
    nine = check_plan(plan(curriculum_id, facts, summer(c('D1'), c('D2'), c('Y'))), runtime, POLICY)
    assert nine.terms[0].outcome == 'works' and nine.terms[0].load.units == 9
    twelve = check_plan(plan(curriculum_id, facts, summer(c('D1'), c('D2'), c('Y'), c('LINK'))), runtime, POLICY)
    assert twelve.terms[0].outcome == 'works_with_warning'
    assert (twelve.terms[0].warnings[0].kind, twelve.terms[0].load.units, twelve.terms[0].load.ceiling) == (
        'summer_above_normal', 12, 9)


def test_without_a_reviewed_policy_only_the_load_part_is_unknown(curriculum):
    curriculum_id, runtime, c = curriculum
    result = check_plan(plan(curriculum_id, [(c('BASE'), 'passed')], regular(2, 'first_semester', (c('X'), 'prescribed'))),
                        runtime, None)
    term = result.terms[0]
    assert term.outcome == 'unknown' and not term.reasons
    assert (term.load.status, term.load.reason) == ('unknown', 'load policy not reviewed')
    assert term.load.units == 3  # units are still the printed ones; only the ceiling is unavailable


def test_missing_printed_units_leave_the_load_unknown(curriculum):
    curriculum_id, runtime, c = curriculum
    result = check_plan(plan(curriculum_id, [(c('D1'), 'passed')], regular(3, 'second_semester', (c('Z'), 'prescribed'),
                                                                           (c('GAP'), 'prescribed'))), runtime, POLICY)
    term = result.terms[0]
    assert term.outcome == 'unknown' and term.load.status == 'unknown'
    assert term.reasons[0].kind == 'units_missing' and term.reasons[0].course_id == c('GAP')


def test_special_class_off_semester_and_summer_courses_are_requested_not_confirmed(curriculum):
    curriculum_id, runtime, c = curriculum
    facts = [(c('BASE'), 'passed'), (c('X'), 'failed')]
    result = check_plan(plan(curriculum_id, facts,
                             regular(2, 'second_semester', (c('X'), 'special_class_request'),
                                     (c('LINK'), 'off_semester_request')),
                             summer(c('D1'))), runtime, POLICY)
    first, second = result.terms
    assert [(u.course_id, u.kind, u.text) for u in first.unconfirmed] == [
        (c('X'), 'special_class_request', 'requested, not confirmed'),
        (c('LINK'), 'off_semester_request', 'requested, not confirmed')]
    assert [(u.course_id, u.kind) for u in second.unconfirmed] == [(c('D1'), 'summer')]
    assert first.outcome == 'works'  # an unconfirmed request is a condition, not a verdict


def test_the_session_facts_are_unchanged_after_a_check(curriculum):
    curriculum_id, runtime, c = curriculum
    request = plan(curriculum_id, [(c('BASE'), 'passed'), (c('X'), 'failed')],
                   regular(2, 'second_semester', (c('X'), 'retake')), summer(c('D1')))
    before = request.model_dump(mode='json')
    check_plan(request, runtime, POLICY)
    assert request.model_dump(mode='json') == before
    assert [(f.course_id, f.state) for f in request.facts] == [(c('BASE'), 'passed'), (c('X'), 'failed')]


def test_the_owner_plan_shape_on_synthetic_codes(curriculum):
    """Owner plan §6 shape: fail X; special X now; X's dependants in summer; the next dependant in the following term
    on top of a full prescribed load -> a major warning, never a block."""
    curriculum_id, runtime, c = curriculum
    facts = [(c(n), 'passed') for n in ('BASE', 'AUX', 'FILL', 'PAIR_A', 'PAIR_B')] + [(c('X'), 'failed')]
    result = check_plan(plan(curriculum_id, facts,
                             regular(2, 'second_semester', (c('LINK'), 'prescribed'), (c('X'), 'special_class_request')),
                             summer(c('D1'), c('D2')),
                             regular(3, 'first_semester', *((c(f'T{i}'), 'prescribed') for i in range(7)),
                                     (c('Y'), 'special_class_request'))), runtime, POLICY)
    assert [t.outcome for t in result.terms] == ['works', 'works', 'works_with_warning']
    assert result.terms[2].warnings[0].units == 24 and result.terms[2].warnings[0].ceiling == 21
    assert [u.course_id for t in result.terms for u in t.unconfirmed] == [c('X'), c('D1'), c('D2'), c('Y')]


def test_a_plan_outside_the_runtime_curriculum_is_refused():
    runtime = build('curriculum-synthetic-1')
    with pytest.raises(ValueError, match='curriculum_mismatch'):
        check_plan(plan('curriculum-unfamiliar-9', [], summer('course-x')), runtime, POLICY)


@pytest.mark.parametrize('term', [
    {'kind': 'summer', 'year_level': 2, 'semester': 'first_semester', 'courses': [{'course_id': 'course-a', 'mode': 'summer'}]},
    {'kind': 'regular', 'year_level': None, 'semester': None, 'courses': [{'course_id': 'course-a', 'mode': 'prescribed'}]},
    {'kind': 'regular', 'year_level': 2, 'semester': 'first_semester', 'courses': [{'course_id': 'course-a', 'mode': 'summer'}]},
    {'kind': 'summer', 'year_level': None, 'semester': None, 'courses': [{'course_id': 'course-a', 'mode': 'retake'}]},
    {'kind': 'regular', 'year_level': 2, 'semester': 'first_semester',
     'courses': [{'course_id': 'course-a', 'mode': 'prescribed'}, {'course_id': 'course-a', 'mode': 'retake'}]},
    {'kind': 'regular', 'year_level': 2, 'semester': 'first_semester', 'courses': []},
])
def test_malformed_terms_are_rejected(term):
    with pytest.raises(ValueError):
        PlanCheckRequest.parse({'schema_version': PlanCheckRequest.SCHEMA_VERSION,
                                'curriculum_id': 'curriculum-synthetic-1', 'facts': [], 'terms': [term]})


def test_a_load_policy_needs_review_and_a_positive_summer_load():
    data = POLICY.model_dump(mode='json')
    for change in ({'review_refs': []}, {'summer_normal_units': 0}, {'clauses': []}):
        with pytest.raises(ValueError):
            LoadPolicy.parse({**data, **change})


def test_the_reviewed_palsu_load_policy_record_loads():
    # Owner 4 Nov 2026 (Track A, "go"): the semester ceiling (D5) and the nine-unit summer load, printed on Handbook
    # p. 35; the record quotes both clauses verbatim and is not synthetic.
    from pathlib import Path
    from backend.bintanong_planning.policies import load_policy
    policy = load_policy(Path(__file__).resolve().parents[1] / 'knowledge' / 'rules' / 'palsu-load-policy-v1.json')
    assert not policy.synthetic and policy.summer_normal_units == 9
    assert policy.regular_ceiling == 'prescribed_semester_total'
    assert 'nine (9) units' in policy.clause('summer').text and 'prescribed for the semester' in policy.clause('regular').text
