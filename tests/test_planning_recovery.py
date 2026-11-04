"""Ask mode drafts (plan of action, Step 5; owner 4 Nov 2026): the greedy prerequisite chain from one failed course,
four variants run through check_plan with the load policy, unlock-weight ordering in a summer that cannot hold every
course, stated vs assumed start term, and dropped variants with their reasons. Synthetic curricula only; the same tests
run on a curriculum with unfamiliar codes.

Shape (logical names):
  1:1 BASE   1:2 AUX
  2:1 X needs BASE; F1                2:2 Y needs X; Z needs X; P1
  3:1 W needs Y; Q1 needs AUX; Q2     3:2 R1; R2
  4:1 S1                              4:2 S2          every course 3 units
"""
import pytest

from backend.bintanong_planning.contracts import RecoveryResult
from backend.bintanong_planning.policies import LoadPolicy
from backend.bintanong_planning.recovery import palsu_recovery_sources, plan_recovery
from backend.bintanong_planning.contracts import RecoveryRoutes
from backend.bintanong_symbolic.authoring import build_curriculum_ledger
from backend.bintanong_symbolic.runtime import CurriculumRuntime
from test_planning_check import POLICY, cid
from test_symbolic_course_facts import SOURCE, fact

Y1, Y2, Y3, Y4 = 'FIRST YEAR', 'SECOND YEAR', 'THIRD YEAR', 'FOURTH YEAR'
FIRST, SECOND = 'FIRST SEMESTER', 'SECOND SEMESTER'
SHAPE = [('BASE', Y1, FIRST, None), ('AUX', Y1, SECOND, None),
         ('X', Y2, FIRST, 'BASE'), ('F1', Y2, FIRST, None),
         ('Y', Y2, SECOND, 'X'), ('Z', Y2, SECOND, 'X'), ('P1', Y2, SECOND, None),
         ('W', Y3, FIRST, 'Y'), ('Q1', Y3, FIRST, 'AUX'), ('Q2', Y3, FIRST, None),
         ('R1', Y3, SECOND, None), ('R2', Y3, SECOND, None), ('S1', Y4, FIRST, None), ('S2', Y4, SECOND, None)]
CURRICULA = {'curriculum-synthetic-1': {n: f'SYN {300 + i}' for i, (n, *_) in enumerate(SHAPE)},
             'curriculum-unfamiliar-9': {n: f'QZV-{chr(65 + i)}{i}/L' for i, (n, *_) in enumerate(SHAPE)}}
ROUTES = RecoveryRoutes.parse({
    'schema_version': RecoveryRoutes.SCHEMA_VERSION, 'routes_id': 'routes-synthetic', 'synthetic': True,
    'clauses': [{'kind': k, 'topic': 'synthetic_' + k, 'page': 1, 'text': f'Fictional {k} clause.', 'conditions': []}
                for k in ('regular_class', 'special_class', 'off_semester', 'summer')],
    'source_chunk_ids': ['chunk-synthetic'], 'review_refs': ['review-synthetic']})


def build(curriculum_id):
    codes = CURRICULA[curriculum_id]
    scope = {'program_id': 'program-synthetic', 'curriculum_id': curriculum_id}
    spans = fact('rule')['source_spans']
    courses = []
    for top, (name, year, term, needs) in enumerate(SHAPE):
        rule = ({'kind': 'verified_none', 'source_spans': spans} if needs is None else
                {'kind': 'course', 'course_id': cid(codes[needs]), 'source_spans': spans})
        courses.append({'course_id': cid(codes[name]), **scope, 'source_version_id': SOURCE.version_id,
                        'facts': {'course_code': fact(codes[name], 700 - top * 10), 'course_title': fact('Fictional ' + name),
                                  'year_level': fact(year), 'semester': fact(term), 'units.total': fact(3)},
                        'prerequisites': rule, 'review_state': 'draft', 'review_refs': []})
    digests = {c['course_id']: c['content_sha256'] for c in build_curriculum_ledger(scope, [SOURCE], courses)['courses']}
    for c in courses:
        c['review_state'], c['review_refs'] = 'reviewed', ['review-1']
    reviews = [{'review_id': 'review-1', 'source_version_id': SOURCE.version_id, 'course_digests': digests,
                'reviewer_label': 'Synthetic researcher'}]
    return CurriculumRuntime(build_curriculum_ledger(scope, [SOURCE], courses, reviews=reviews))


@pytest.fixture(params=sorted(CURRICULA), scope='module')
def curriculum(request):
    codes = CURRICULA[request.param]
    return request.param, build(request.param), (lambda name: cid(codes[name]))


def recover(curriculum, facts=(('X', 'failed'),), term=None, policy=POLICY):
    curriculum_id, runtime, c = curriculum
    affected = runtime.list_affected_courses(_affected_request(curriculum_id, c('X'))).course_ids
    return plan_recovery(runtime, curriculum_id, c('X'), affected, [(c(n), s) for n, s in facts], term, policy, ROUTES)


def _affected_request(curriculum_id, course):
    from backend.bintanong_planning.checker import _request
    return _request('list_affected_courses', curriculum_id, course_id=course)


def moved(draft, c, names):
    """{term: [(name, mode)]} for the courses the draft moves."""
    back = {c(n): n for n in names}
    return {(t.term.year, t.term.semester): [(back[p.course_id], p.mode) for p in t.moved] for t in draft.terms if t.moved}


NAMES = [n for n, *_ in SHAPE]


def test_four_variants_follow_the_greedy_chain_in_the_stated_order(curriculum):
    _, _, c = curriculum
    result = recover(curriculum)
    assert type(result) is RecoveryResult and not result.dropped
    assert (result.start_term.year, result.start_term.semester, result.term_stated) == (2, 'second_semester', False)
    assert (result.next_offering.year, result.next_offering.semester) == (3, 'first_semester')
    c_, a, fastest, b = result.drafts  # preferred first, then fewest requests, then earliest last course
    assert [d.variant for d in result.drafts] == ['D', 'A', 'C', 'B'] and [d.requests for d in result.drafts] == [2, 0, 3, 3]
    assert moved(a, c, NAMES) == {(3, 'first_semester'): [('X', 'retake')],
                                  (3, 'second_semester'): [('Y', 'prescribed'), ('Z', 'prescribed')],
                                  (4, 'first_semester'): [('W', 'prescribed')]}
    # Z unlocks nothing: a special class for it would not bring the student back any sooner, so it is not requested.
    assert moved(b, c, NAMES) == {(2, 'second_semester'): [('X', 'special_class_request')],
                                  (3, 'first_semester'): [('Y', 'special_class_request')],
                                  (3, 'second_semester'): [('Z', 'prescribed'), ('W', 'special_class_request')]}
    assert moved(c_, c, NAMES) == {(2, 'second_semester'): [('X', 'special_class_request')],
                                   (2, 'summer'): [('Y', 'summer')],
                                   (3, 'first_semester'): [('W', 'prescribed')],
                                   (3, 'second_semester'): [('Z', 'prescribed')]}


def test_the_other_prescribed_courses_stay_and_over_the_prescribed_total_is_a_warning_not_a_block(curriculum):
    _, _, c = curriculum
    a = next(d for d in recover(curriculum).drafts if d.variant == 'A')
    by_term = {(t.term.year, t.term.semester): t for t in a.terms}
    assert set(by_term[(3, 'second_semester')].kept) == {c('R1'), c('R2')}
    third = by_term[(3, 'second_semester')].verdict
    assert third.outcome == 'works_with_warning' and (third.load.units, third.load.ceiling) == (12, 6)
    assert by_term[(3, 'first_semester')].verdict.outcome == 'works'


def test_summer_stays_within_the_summer_load_and_its_requests_are_unconfirmed(curriculum):
    result = recover(curriculum)
    c_ = next(d for d in result.drafts if d.variant == 'D')
    summer = next(t for t in c_.terms if t.term.semester == 'summer')
    assert summer.verdict.outcome == 'works' and summer.verdict.load.units <= POLICY.summer_normal_units
    assert [u.kind for u in summer.verdict.unconfirmed] == ['summer']


def test_a_small_summer_still_takes_the_course_needed_by_the_next_term(curriculum):
    _, _, c = curriculum
    small = LoadPolicy.parse(dict(POLICY.model_dump(mode='json'), summer_normal_units=3))
    c_ = next(d for d in recover(curriculum, policy=small).drafts if d.variant == 'D')
    assert moved(c_, c, NAMES)[(2, 'summer')] == [('Y', 'summer')]  # Y is needed by W in 3:1; Z by nothing
    assert moved(c_, c, NAMES)[(3, 'second_semester')] == [('Z', 'prescribed')]


def test_a_stated_later_term_is_the_start_and_identical_variants_are_dropped(curriculum):
    result = recover(curriculum, term=(3, 'first_semester'))
    assert (result.start_term.year, result.start_term.semester, result.term_stated) == (3, 'first_semester', True)
    _, _, c = curriculum
    assert [d.variant for d in result.drafts] == ['D', 'C']
    assert [(d.variant, d.reason, d.same_as) for d in result.dropped] == [('A', 'same_as', 'D'), ('B', 'same_as', 'D')]
    assert moved(result.drafts[0], c, NAMES)[(4, 'first_semester')] == [('W', 'prescribed')]
    assert moved(result.drafts[1], c, NAMES)[(3, 'summer')] == [('W', 'summer')]


def test_a_stated_term_equal_to_the_failed_course_term_starts_the_term_after(curriculum):
    result = recover(curriculum, term=(2, 'first_semester'))
    assert (result.start_term.year, result.start_term.semester, result.term_stated) == (2, 'second_semester', True)


def test_a_variant_that_cannot_work_is_dropped_with_its_reason(curriculum):
    _, _, c = curriculum
    result = recover(curriculum, facts=(('X', 'failed'), ('AUX', 'failed')))
    assert not result.drafts
    assert {(d.reason, d.course_id, d.missing) for d in result.dropped} == {('blocked', c('Q1'), (c('AUX'),))}


def test_without_a_load_policy_summer_is_not_drafted_and_loads_are_unknown(curriculum):
    result = recover(curriculum, policy=None)
    assert [(d.variant, d.reason) for d in result.dropped] == [('D', 'no_summer_policy'), ('C', 'no_summer_policy')]
    assert all(t.verdict.load.status == 'unknown' for d in result.drafts for t in d.terms)


def test_the_reviewed_palsu_recovery_routes_quote_the_load_policy_summer_clause():
    policy, routes = palsu_recovery_sources()
    assert not routes.synthetic and routes.clause('summer').text == policy.clause('summer').text
    special = routes.clause('special_class')
    assert special.page == 37 and 'a maximum of fifteen (15) students' in special.conditions
    assert 'at least 35 students for lecture and 25 students for laboratory' in routes.clause('off_semester').text
