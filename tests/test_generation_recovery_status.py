"""Track A reply lines (owner 4 Nov 2026), English and Taglish: removal of a stated 4.0/INC with the D6 discrepancy,
overload only for a graduating student in their last semester without a stated delinquency, the prerequisite waiver
and the twelve-unit summer only for a graduating student, cited cross-enrollment/substitution/leave, and the D7
advance-course restriction with a Dean referral. Synthetic curricula and clauses (test_planning_recovery_status)."""
import pytest

from backend.bintanong_generation.plan_check_reply import plan_check_lines
from backend.bintanong_generation.recovery_reply import recovery_lines
from backend.bintanong_planning.contracts import RecoveryRoutes
from test_planning_recovery import ROUTES, curriculum  # noqa: F401  (fixture)
from test_planning_recovery_status import FULL, _plan, recover

BANNED = ('Supported prerequisite check', 'conditions satisfied', 'Based on the supplied evidence')


def text_of(curriculum, language='en', **kw):
    _, _, c = curriculum
    names = {c(n): n for n in ('X', 'Y', 'Z', 'W', 'BASE')}
    lines = recovery_lines(recover(curriculum, **kw), language, lambda course: names.get(course, course))
    joined = '\n'.join(lines)
    assert not any(b in joined for b in BANNED)
    return joined


@pytest.mark.parametrize('grade,verb', [('4.0', 'remove'), ('INC', 'complete')])
def test_an_open_grade_offers_removal_with_the_discrepancy_before_enrollment_and_forfeiture(curriculum, grade, verb):
    text = text_of(curriculum, grade=grade)
    assert (f'You said you got {grade} in X, so you can {verb} it instead of retaking it, within the succeeding term. '
            'Student Handbook p. 2: "Fictional removal_period clause') in text
    assert 'Note: the same section also states "within one year" (3.3, 3.7).' in text
    assert 'need X, so the removal must be done before enrollment. Student Handbook p. 2' in text
    assert 'Heads-up: re-enrolling X gives up the removal. Student Handbook p. 2' in text
    assert text.index('within the succeeding term') < text.index('Ways to take X again')


def test_taglish_removal_keeps_the_english_source_terms(curriculum):
    text = text_of(curriculum, 'taglish', grade='4.0')
    assert 'Sabi mo 4.0 ang grade mo sa X, kaya puwede mo itong i-remove imbes na i-retake, sa loob ng succeeding term.' in text
    assert 'Note: sinasabi rin ng parehong section ang "within one year" (3.3, 3.7).' in text
    assert 'kaya dapat matapos ang removal bago mag-enroll.' in text


@pytest.mark.parametrize('grade', ['5.0', None])
def test_a_five_gets_no_removal_route(curriculum, grade):
    text = text_of(curriculum, grade=grade)
    assert 'removal' not in text.lower() and 'within one year' not in text


def test_without_the_held_clauses_removal_refers_to_the_dean_and_quotes_nothing_it_lacks(curriculum):
    kept = RecoveryRoutes.parse({**FULL.model_dump(mode='json'), 'clauses': [
        c for c in FULL.model_dump(mode='json')['clauses']
        if c['kind'] not in ('removal_before_enrollment', 'removal_forfeit')]})
    text = text_of(curriculum, grade='4.0', routes=kept)
    assert 'ask your Dean about finishing the removal before enrollment' in text
    assert 'Before you re-enroll X, ask your Dean how that affects removing the grade' in text
    assert 'removal_forfeit clause' not in text and 'removal_before_enrollment clause' not in text


@pytest.mark.parametrize('flags,shown', [
    (dict(graduating=True, last_semester=True), True),
    (dict(graduating=True), False),
    (dict(last_semester=True), False),
    (dict(graduating=True, last_semester=True, standing='probation'), False),
    (dict(graduating=True, last_semester=True, standing='scholastic_delinquency'), False)])
def test_overload_is_only_for_a_graduating_last_semester_without_a_stated_delinquency(curriculum, flags, shown):
    text = text_of(curriculum, **flags)
    assert ('Fictional overload clause' in text) is shown
    if shown:
        assert "It's a request, not automatic: ask your Dean and the Registrar first." in text


@pytest.mark.parametrize('graduating', [True, False])
def test_waiver_and_twelve_unit_summer_only_for_a_graduating_student(curriculum, graduating):
    text = text_of(curriculum, graduating=graduating)
    assert ('Fictional prerequisite_waiver clause' in text) is graduating
    assert ('the summer load can go up to twelve (12) units' in text) is graduating
    if graduating:
        assert 'not part of the drafts below' in text
        assert 'Dahil sabi mo graduating ka' in text_of(curriculum, 'taglish', graduating=True)


def test_not_offered_cites_cross_enrollment_and_substitution_with_its_limit(curriculum):
    text = text_of(curriculum, not_offered=True)
    assert 'If X is not offered, you can ask about cross-enrollment. Student Handbook p. 2' in text
    assert 'Fictional substitution clause' in text and 'Fictional substitution_limit clause' in text
    assert 'Fictional leave_of_absence clause' not in text


def test_stopping_cites_leave_of_absence(curriculum):
    assert 'apply for a leave of absence. Student Handbook p. 2: "Fictional leave_of_absence clause' in text_of(
        curriculum, stopping=True)
    assert 'mag-apply ng leave of absence' in text_of(curriculum, 'taglish', stopping=True)


@pytest.mark.parametrize('standing', ['warning', 'probation', 'scholastic_delinquency'])
def test_a_stated_standing_quotes_the_advance_course_restriction_with_a_dean_referral(curriculum, standing):
    text = text_of(curriculum, standing=standing)
    assert 'Fictional advance_courses clause' in text
    assert "I don't work out your academic standing" in text and 'please ask your Dean before you enroll' in text


def test_no_status_adds_no_track_a_line(curriculum):
    text = text_of(curriculum)
    assert not any(f'Fictional {k} clause' in text for k in ('overload', 'prerequisite_waiver', 'cross_enrollment',
                                                             'leave_of_absence', 'advance_courses'))


def test_plan_check_reply_gives_the_reenroll_heads_up(curriculum):
    request, result, c = _plan(curriculum, 'INC')
    lines = plan_check_lines(request, result, 'en', lambda course: 'X' if course == c('X') else course, routes=FULL)
    assert any(l.endswith('Works with a heads-up') for l in lines)
    assert '  Heads-up: you said you have INC in X, and this plan re-enrolls it.' in lines
    assert any('re-enrolling X gives up the removal. Student Handbook p. 2' in l for l in lines)
    lines = plan_check_lines(request, result, 'taglish', lambda course: 'X', routes=ROUTES)
    assert any('itanong sa Dean kung ano ang epekto ng pag-re-enroll ng X' in l for l in lines)
