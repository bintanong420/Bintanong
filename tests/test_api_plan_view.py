"""Plan view (owner, 4 Nov 2026): the recovery drafts as a comparison and per-term timeline, built only from the
host's checked recovery result (never from model text). Synthetic curriculum (test_planning_recovery)."""
import pytest

from backend.bintanong_api.presentation import plan_view
from backend.bintanong_api.stream import answer_parts
from backend.bintanong_planning.contracts import DroppedDraft
from test_generation_recovery_reply import RECOVERY_TEXT, clarify_with_failure, run


@pytest.fixture(scope='module')
def answered():
    return run(RECOVERY_TEXT, clarify_with_failure(RECOVERY_TEXT))


def test_the_answer_carries_the_recovery_its_text_renders(answered):
    integration, answer = answered
    assert answer.recovery == integration.recovery


def test_each_draft_maps_its_checked_terms_with_printed_codes(answered):
    integration, answer = answered
    view = plan_view(answer, integration.course_labels)
    assert [d['label'] for d in view['drafts']] == [f'Draft {d.variant}' for d in integration.recovery.drafts]
    a = next(d for d in view['drafts'] if d['variant'] == 'A')
    # The unchanged prescribed term is left out, as in the reply text.
    assert [t['label'] for t in a['terms']] == ['3rd yr · 1st sem', '3rd yr · 2nd sem', '4th yr · 1st sem']
    first = a['terms'][0]
    assert first['courses'] == [
        {'code': 'SYN 302', 'mode': 'retake', 'needsConfirmation': False},
        {'code': 'SYN 308', 'mode': 'prescribed', 'needsConfirmation': False},
        {'code': 'SYN 309', 'mode': 'prescribed', 'needsConfirmation': False}]
    assert first['load'] == {'status': 'within', 'units': 9.0, 'ceiling': 9.0} and first['notes'] == []
    assert a['terms'][1]['load'] == {'status': 'above', 'units': 12.0, 'ceiling': 6.0}
    assert a['terms'][1]['notes'] == ['12 units, lampas sa 6 na nakalista sa term na ito']  # a Taglish question
    english = plan_view(answer.model_copy(update=dict(language='en')), integration.course_labels)
    assert english['drafts'][0]['terms'][1]['notes'] == ['12 units, above the 6 listed for this term']
    assert a['summary'] == {'rejoinAfter': '4th yr · 1st sem', 'specialClassRequests': 0, 'summerCourses': 0,
                            'requests': 0, 'majorWarnings': 2, 'beyondCurriculum': False}
    assert 'course-' not in str(view)  # internal identities never reach the student


def test_requested_courses_need_confirmation_and_summer_reads_as_summer(answered):
    integration, answer = answered
    c = next(d for d in plan_view(answer, integration.course_labels)['drafts'] if d['variant'] == 'C')
    assert [t['label'] for t in c['terms']] == ['2nd yr · 2nd sem', '2nd yr · Summer', '3rd yr · 1st sem']
    assert c['terms'][0]['courses'][0] == {'code': 'SYN 302', 'mode': 'special_class_request',
                                           'needsConfirmation': True}
    assert [x['mode'] for x in c['terms'][1]['courses']] == ['summer', 'summer']
    assert all(x['needsConfirmation'] for x in c['terms'][1]['courses'])
    assert c['summary'] == {'rejoinAfter': '3rd yr · 1st sem', 'specialClassRequests': 1, 'summerCourses': 2,
                            'requests': 3, 'majorWarnings': 0, 'beyondCurriculum': False}


def test_fastest_rejoins_earliest_then_fewest_requests(answered):
    integration, answer = answered
    assert plan_view(answer, integration.course_labels)['fastest'] == 'C'  # back after 3rd yr 1st sem
    recovery = answer.recovery
    c = next(d for d in recovery.drafts if d.variant == 'C')
    tied = c.model_copy(update=dict(variant='B', requests=c.requests + 1))  # same rejoin term, more requests
    other = recovery.model_copy(update=dict(drafts=(tied, c, *(d for d in recovery.drafts if d.variant == 'A'))))
    assert plan_view(answer.model_copy(update=dict(recovery=other)), {})['fastest'] == 'C'


@pytest.mark.parametrize('language,fastest,notice', [
    ('en', 'Fastest', 'This is a draft, not an approval. Show it to your program adviser.'),
    ('taglish', 'Pinakamabilis', 'Draft lang ito, hindi approval. Ipakita sa program adviser.')])
def test_host_labels_follow_the_reply_language(answered, language, fastest, notice):
    integration, answer = answered
    view = plan_view(answer.model_copy(update=dict(language=language)), integration.course_labels)
    assert (view['fastestLabel'], view['notice']) == (fastest, notice)


def test_absent_without_a_recovery_or_a_draft(answered):
    integration, answer = answered
    assert plan_view(answer.model_copy(update=dict(recovery=None)), {}) is None
    empty = answer.recovery.model_copy(update=dict(drafts=(), dropped=tuple(
        DroppedDraft(variant=v, reason='too_long') for v in 'ABC')))
    assert plan_view(answer.model_copy(update=dict(recovery=empty)), {}) is None


def test_built_from_checked_recovery_never_model_text_and_validated(answered):
    from backend.bintanong_generation.evidence import prepare
    from backend.bintanong_generation.render import shown_recovery
    from backend.bintanong_generation.validation import validate_final
    from backend.bintanong_planning.contracts import PlanReason
    integration, answer = answered
    pack = prepare(integration)
    baseline = plan_view(answer, integration.course_labels)
    mutated_text = answer.model_copy(update=dict(
        text='Draft Z: take FAKE 999 (0 units)',
        decision_explanation='Completely different model prose'))
    assert plan_view(mutated_text, integration.course_labels) == baseline
    # Forged or mismatched recovery on CandidateAnswer must be rejected by validate_final.
    with pytest.raises(ValueError, match='final_identity_or_decision_mismatch'):
        validate_final(answer.model_copy(update=dict(recovery=None)), pack, answer.claims)
    # Withheld when status is not answered or failed_course_id mismatches target.
    assert shown_recovery(pack, 'clarification_needed') is None
    import dataclasses
    mismatched_pack = dataclasses.replace(
        pack, recovery=integration.recovery.model_copy(update=dict(failed_course_id='course-other')))
    assert shown_recovery(mismatched_pack, 'answered') is None
    # units_missing must not emit prereq_unknown note (only load_unknown when load is unknown).
    from backend.bintanong_planning.contracts import LoadCheck
    first_draft = answer.recovery.drafts[0]
    first_term = first_draft.terms[0]
    verdict_with_units_missing = first_term.verdict.model_copy(update=dict(
        outcome='unknown',
        load=LoadCheck(status='unknown', units=None, ceiling=None, reason='Units blank in source'),
        reasons=(*first_term.verdict.reasons, PlanReason(
            kind='units_missing', course_id='course-syn-302', detail='Units blank in source'))))
    term_with_units_missing = first_term.model_copy(update=dict(verdict=verdict_with_units_missing))
    draft_with_units_missing = first_draft.model_copy(update=dict(
        terms=(term_with_units_missing, *first_draft.terms[1:])))
    rec_with_units_missing = answer.recovery.model_copy(update=dict(
        drafts=(draft_with_units_missing, *answer.recovery.drafts[1:])))
    view = plan_view(answer.model_copy(update=dict(recovery=rec_with_units_missing)), integration.course_labels)
    assert view['drafts'][0]['terms'][0]['notes'] == ['Hindi na-check ang unit load: Units blank in source']


def test_the_stream_sends_the_plan_view_only_when_enabled(answered):
    integration, answer = answered

    def data(**options):
        parts = answer_parts(answer, 'msg-test', course_labels=integration.course_labels, **options)
        return next(p for p in parts if p['type'] == 'data-answer')['data']
    # The installed frontend parses data-answer strictly, so the key stays off until it accepts it.
    assert 'planView' not in data()
    assert data(plan_view=True)['planView'] == plan_view(answer, integration.course_labels)
