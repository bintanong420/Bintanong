"""Exact student wire metadata for the installed frontend, without private/internal locators."""
import pytest

from backend.bintanong_api.stream import answer_parts, encode
from backend.bintanong_contracts.runtime import BoundInput
from test_api_presentation import answer_for


def summary(answer, labels=None):
    parts = answer_parts(answer, 'msg-test', course_labels=labels or {})
    return next(part for part in parts if part['type'] == 'data-answer')


@pytest.mark.parametrize('status,language,conditional,missing,expected', [
    ('answered', 'en', True, (),
     b'data: {"type":"data-answer","data":{"status":"answered","conditional":true,"language":"en","missingFields":[]}}\n\n'),
    ('insufficient_evidence', 'taglish', False, ('internal-unavailable-field',),
     b'data: {"type":"data-answer","data":{"status":"insufficient_evidence","conditional":false,"language":"taglish","missingFields":[]}}\n\n'),
])
def test_answer_and_insufficient_metadata_golden(status, language, conditional, missing, expected):
    answer = answer_for('Symbolic').model_copy(update={
        'status': status, 'language': language, 'missing_facts': missing,
    })
    if not conditional:
        answer = answer.model_copy(update={'decision': None})
    assert encode(summary(answer)) == expected


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
        b'"language":"taglish","missingFields":["program","course_status"],"clarification":'
        b'{"courses":[{"code":"A 1/L","kind":"completion"},{"code":"B 2/L","kind":"enrollment"}],'
        b'"scope":{"programId":"program-a","curriculumId":"curriculum-a"}}}}\n\n')
    assert 'not_completed' not in str(data) and 'internal-hash' not in str(data)


def test_unresolved_course_identity_never_becomes_a_printed_choice():
    answer = answer_for('Symbolic').model_copy(update={
        'status': 'clarification_needed', 'missing_facts': ('completion_unknown:course-pre',),
    })
    assert summary(answer)['data']['clarification']['courses'] == []
