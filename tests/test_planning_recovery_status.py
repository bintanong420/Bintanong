"""Track A routes (owner 4 Nov 2026): the optional Handbook clauses and the student's stated status reach the planner.

Removal of a stated 4.0/INC (not 5.0) names the courses of the next regular semester that need the failed course; a
plan that re-enrolls a course with an open 4.0/INC gets a heads-up. Nothing here computes standing, graduation or a
grade: every status field is the student's own statement. Synthetic curricula and clauses only (test_planning_recovery).
"""
import pytest

from backend.bintanong_planning.checker import check_plan
from backend.bintanong_planning.contracts import (CITED_ROUTES, PlanCheckRequest, RecoveryRoutes, StudentStatus,
                                                  plan_request_digest)
from backend.bintanong_planning.recovery import palsu_recovery_sources, plan_recovery
from test_planning_check import POLICY, cid
from test_planning_recovery import ROUTES, _affected_request, curriculum  # noqa: F401  (fixture)

FULL = RecoveryRoutes.parse({**ROUTES.model_dump(mode='json'), 'clauses': [
    *ROUTES.model_dump(mode='json')['clauses'],
    *({'kind': k, 'topic': 'synthetic_' + k, 'page': 2, 'text': f'Fictional {k} clause, condition {k}.',
       'conditions': [f'condition {k}']} for k in CITED_ROUTES)]})


def recover(curriculum, grade=None, routes=FULL, **flags):
    curriculum_id, runtime, c = curriculum
    affected = runtime.list_affected_courses(_affected_request(curriculum_id, c('X'))).course_ids
    stated = StudentStatus.parse(dict(flags, grades=[] if grade is None else [{'course_id': c('X'), 'grade': grade}]))
    return plan_recovery(runtime, curriculum_id, c('X'), affected, [(c('X'), 'failed')], None, POLICY, routes,
                         student_status=stated)


def test_optional_clauses_are_each_allowed_once_and_the_four_routes_stay_required():
    assert len(FULL.clauses) == 4 + len(CITED_ROUTES)
    data = FULL.model_dump(mode='json')
    with pytest.raises(ValueError):
        RecoveryRoutes.parse({**data, 'clauses': data['clauses'] + [data['clauses'][-1]]})
    with pytest.raises(ValueError):
        RecoveryRoutes.parse({**data, 'clauses': [c for c in data['clauses'] if c['kind'] != 'summer']})


def test_a_stated_grade_is_one_per_course():
    with pytest.raises(ValueError):
        StudentStatus.parse({'grades': [{'course_id': 'a', 'grade': '4.0'}, {'course_id': 'a', 'grade': 'INC'}]})


@pytest.mark.parametrize('grade', ['4.0', 'INC'])
def test_an_open_grade_names_the_next_semester_courses_that_need_it(curriculum, grade):
    _, _, c = curriculum
    result = recover(curriculum, grade)
    assert result.failed_grade == grade
    # The drafts start in second year, second semester, where Y and Z need X.
    assert set(result.removal_needed_by) == {c('Y'), c('Z')}


@pytest.mark.parametrize('grade', ['5.0', None])
def test_a_five_or_no_stated_grade_has_no_removal(curriculum, grade):
    result = recover(curriculum, grade)
    assert result.failed_grade == grade and result.removal_needed_by == ()


def test_without_a_status_the_result_dump_is_unchanged(curriculum):
    curriculum_id, runtime, c = curriculum
    affected = runtime.list_affected_courses(_affected_request(curriculum_id, c('X'))).course_ids
    result = plan_recovery(runtime, curriculum_id, c('X'), affected, [(c('X'), 'failed')], None, POLICY, ROUTES)
    dumped = result.model_dump(mode='json')
    assert 'status' not in dumped and 'removal_needed_by' not in dumped


def _plan(curriculum, grade):
    curriculum_id, runtime, c = curriculum
    data = dict(schema_version=PlanCheckRequest.SCHEMA_VERSION, curriculum_id=curriculum_id,
                facts=[dict(course_id=c('BASE'), state='passed'), dict(course_id=c('X'), state='failed')],
                terms=[dict(kind='regular', year_level=3, semester='first_semester',
                            courses=[dict(course_id=c('X'), mode='retake')])])
    if grade is not None:
        data['status'] = dict(grades=[dict(course_id=c('X'), grade=grade)])
    request = PlanCheckRequest.parse(data)
    return request, check_plan(request, runtime, POLICY), c


@pytest.mark.parametrize('grade', ['4.0', 'INC'])
def test_a_plan_that_reenrolls_an_open_grade_gets_a_heads_up(curriculum, grade):
    _, result, c = _plan(curriculum, grade)
    verdict = result.terms[0]
    assert verdict.open_removals == (c('X'),) and verdict.outcome == 'works_with_warning'


def test_a_reenrolled_five_is_not_a_removal_heads_up_and_no_status_keeps_the_digest(curriculum):
    _, result, _ = _plan(curriculum, '5.0')
    assert result.terms[0].open_removals == () and result.terms[0].outcome == 'works'
    request, plain, _ = _plan(curriculum, None)
    assert 'status' not in request.model_dump(mode='json')
    assert 'open_removals' not in plain.terms[0].model_dump(mode='json')
    assert plain.request_sha256 == plan_request_digest(request, plain.policy_id, plain.policy_sha256)


def test_the_reviewed_palsu_routes_carry_the_track_a_clauses_from_unheld_chunks():
    _, routes = palsu_recovery_sources()
    pages = {c.kind: c.page for c in routes.clauses}
    assert pages == {'regular_class': 37, 'special_class': 37, 'off_semester': 37, 'summer': 35,
                     'removal_period': 47, 'removal_one_year': 47, 'overload': 62, 'prerequisite_waiver': 31,
                     'cross_enrollment': 34, 'substitution': 44, 'substitution_limit': 44, 'leave_of_absence': 38,
                     'advance_courses': 40}
    assert 'within a period of one term' in routes.clause('removal_period').text
    assert 'within one year' in routes.clause('removal_one_year').text
    assert 'not to exceed 28 units' in routes.clause('overload').text
    assert routes.clause('advance_courses').text.startswith('2. RESTRICTION ON ADVANCE COURSES.')
    # 3.2, 3.5 and 3.6 (p. 47) and the p. 36 overload clause sit only in chunks with an unresolved source limit.
    assert 'removal_before_enrollment' not in pages and 'removal_forfeit' not in pages
