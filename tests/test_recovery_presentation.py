"""The recovery view is concise without concealing checks or changing legacy text."""
import pytest

from backend.bintanong_api.answer_presentation import build_answer_presentation, AnswerPresentationV2
from backend.bintanong_api.stream import answer_parts
from test_generation_recovery_reply import answered


def test_recovery_shows_one_draft_with_its_warnings_and_keeps_the_rest_accessible(answered):
    integration, answer, _ = answered
    before = answer.text
    view = build_answer_presentation(answer, integration.course_labels)
    assert view is not None
    AnswerPresentationV2.model_validate(view)
    blocks = view['parts'][0]['blocks']
    visible = '\n'.join(b['text'] for b in blocks if b['type'] != 'details')
    details = [b for b in blocks if b['type'] == 'details']
    assert visible.count('### Plan ') == 1
    assert '####' not in visible and 'preferred: just in time' not in visible
    assert '2nd year, 2nd sem' in visible
    assert 'second year, second semester' not in visible
    assert 'Heads-up:' in visible
    assert 'Assuming' in visible
    assert len(details) == 3
    assert all(b['title'] for b in details)
    assert sum(b['text'].count('### Plan ') for b in details) == len(answer.recovery.drafts) - 1
    assert 'Fictional special_class clause.' in details[-1]['text']
    assert len(visible.split()) < len(answer.text.split()) * .7
    assert answer.text == before
    assert not build_answer_presentation(answer)  # no printed labels: keep the safe legacy view
    assert all('course-' not in b['text'] for b in blocks)


def test_incomplete_primary_term_remains_visible(answered):
    integration, answer, _ = answered
    first = answer.recovery.drafts[0]
    term = first.terms[0]
    from backend.bintanong_planning.contracts import PlanReason
    term = term.model_copy(update={'verdict': term.verdict.model_copy(update={
        'outcome': 'unknown', 'reasons': (PlanReason(kind='prerequisite_unknown',
                                                    course_id=first.terms[0].moved[0].course_id),)})})
    first = first.model_copy(update={'terms': (term, *first.terms[1:])})
    recovery = answer.recovery.model_copy(update={'drafts': (first, *answer.recovery.drafts[1:])})
    view = build_answer_presentation(answer.model_copy(update={'recovery': recovery}), integration.course_labels)
    assert 'Hindi ko ma-check nang buo ang term na ito.' in view['parts'][0]['blocks'][0]['text']


def test_recovery_view_is_opt_in_and_retains_the_full_copy_text(answered):
    integration, answer, _ = answered
    legacy = answer_parts(answer, 'msg-test', integration.course_labels)
    modern = answer_parts(answer, 'msg-test', integration.course_labels, presentation_version=2)
    metadata = lambda parts: next(p['data'] for p in parts if p['type'] == 'data-answer')
    assert 'presentation' not in metadata(legacy)
    assert metadata(modern)['presentation']['parts'][0]['conditional']
    assert next(p['delta'] for p in legacy if p['type'] == 'text-delta') == next(
        p['delta'] for p in modern if p['type'] == 'text-delta')


def test_fastest_is_a_projection_among_generated_drafts_not_a_feasibility_guarantee(answered):
    from backend.bintanong_generation.recovery_reply import recovery_lines
    _, answer, _ = answered
    recovery = answer.recovery.model_copy(update={'fastest_asked': True})
    line = recovery_lines(recovery, 'en', lambda c: c)[0]
    assert 'Earliest projected return among these drafts' in line
    assert 'approval' in line


@pytest.mark.parametrize('block', [dict(type='details', text='Hidden'),
                                       dict(type='limitation', text='Warning', title='Hide')])
def test_only_labelled_details_blocks_can_collapse(block):
    from backend.bintanong_api.answer_presentation import PresentationBlock
    with pytest.raises(ValueError):
        PresentationBlock.model_validate(block)
