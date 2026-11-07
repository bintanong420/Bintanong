"""Exact student wire metadata for the installed frontend, without private/internal locators."""
import pytest

from backend.bintanong_api.stream import answer_parts, encode
from backend.bintanong_api.answer_presentation import AnswerPresentationV2
from backend.bintanong_contracts.runtime import BoundInput
from test_api_presentation import answer_for


def summary(answer, labels=None):
    parts = answer_parts(answer, 'msg-test', course_labels=labels or {})
    return next(part for part in parts if part['type'] == 'data-answer')


@pytest.mark.parametrize('status,language,conditional,missing,expected', [
    ('answered', 'en', True, (),
     b'data: {"type":"data-answer","data":{"status":"answered","conditional":true,"language":"en","missingFields":[],'
     b'"notice":"Not official university guidance."}}\n\n'),
    ('insufficient_evidence', 'taglish', False, ('internal-unavailable-field',),
     b'data: {"type":"data-answer","data":{"status":"insufficient_evidence","conditional":false,"language":"taglish","missingFields":[],'
     b'"notice":"Hindi official university guidance."}}\n\n'),
])
def test_answer_and_insufficient_metadata_golden(status, language, conditional, missing, expected):
    answer = answer_for('Symbolic').model_copy(update={
        'status': status, 'language': language, 'missing_facts': missing,
    })
    if not conditional:
        answer = answer.model_copy(update={'decision': None})
    actual = summary(answer)
    presentation = actual['data'].pop('presentation', None)
    assert encode(actual) == expected
    if status == 'answered':
        view = AnswerPresentationV2.model_validate(presentation)
        assert view.coverageState == 'complete'
        assert all(set(part.sourceIds) <= {card.evidence_id for card in answer.citations} for part in view.parts)
    else:
        assert presentation is None


@pytest.mark.parametrize('missing,fields', [(('transfer_direction',), ['transfer_direction']),
                                            (('program_choice:program-a', 'program_choice:program-b'), ['program'])])
def test_direction_and_program_choices_reach_the_clarification_dialog(missing, fields):
    # Owner GUI 3 Nov 2026 (H2): the direction question showed "No specific clarification question was provided."
    answer = answer_for('Symbolic').model_copy(update={'status': 'clarification_needed', 'missing_facts': missing,
                                                       'decision': None})
    assert summary(answer)['data']['missingFields'] == fields


def test_clarification_golden_carries_only_printed_unknown_course_and_scoped_choices():
    answer = answer_for('Symbolic')
    context = answer.structured_context.model_copy(update={'inputs': (
        BoundInput(name='program_id', value='program-a', fact_ref=None),
        BoundInput(name='curriculum_id', value='curriculum-a', fact_ref=None),
    )})
    answer = answer.model_copy(update={
        'status': 'clarification_needed', 'language': 'taglish', 'structured_context': context,
        'missing_facts': ('program_id', 'completion_unknown:course-pre', 'completion_unknown:course-pre',
                          'enrollment_unknown:course-other', 'not_completed:course-failed', 'internal-hash'),
    })
    data = summary(answer, {'course-pre': 'A 1/L', 'course-other': 'B 2/L', 'course-failed': 'C 3/L'})
    assert encode(data) == (
        b'data: {"type":"data-answer","data":{"status":"clarification_needed","conditional":true,'
        b'"language":"taglish","missingFields":["program","course_status"],'
        b'"notice":"Hindi official university guidance.","clarification":'
        b'{"courses":[{"code":"A 1/L","kind":"completion"},{"code":"B 2/L","kind":"enrollment"}],'
        b'"scope":{"programId":"program-a","curriculumId":"curriculum-a"}}}}\n\n')
    assert 'not_completed' not in str(data) and 'internal-hash' not in str(data)


def test_unresolved_course_identity_never_becomes_a_printed_choice():
    answer = answer_for('Symbolic').model_copy(update={
        'status': 'clarification_needed', 'missing_facts': ('completion_unknown:course-pre',),
    })
    assert summary(answer)['data']['clarification']['courses'] == []


@pytest.mark.parametrize('language,notice', [('en', 'Not official university guidance.'),
    ('taglish', 'Hindi official university guidance.'), ('fil', 'Hindi opisyal na gabay ng unibersidad.')])
def test_answer_metadata_carries_the_guidance_notice_in_the_reply_language(language, notice):
    assert summary(answer_for('RAG').model_copy(update=dict(language=language)))['data']['notice'] == notice
