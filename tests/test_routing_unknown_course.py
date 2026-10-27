"""Owner, 24 Oct 2026 (step 2c): a course name or code that matches no reviewed course in the student's curriculum
("Can I take CS 999?") says the course was not found and asks for the printed code, not a bare "please clarify".
Synthetic catalog only."""
import asyncio

import pytest

from backend.bintanong_orchestration.contracts import IntegrationResult
from test_generation_loop import Fake, api
from test_routing_validation import catalog, entry, proposal, validate


def unknown_course(text='Z9'):
    return validate(text, proposal(text=text, mentions=[dict(kind='course', text=text, start=0, end=len(text))]))


def test_course_matching_no_reviewed_course_asks_for_the_printed_code():
    result = unknown_course()
    assert result.diagnostic == 'unresolved_entity' and result.decision.control == 'clarify'
    assert result.decision.missing_facts == ('course_id',)


def test_course_matching_two_reviewed_courses_keeps_the_plain_clarification():
    result = validate(catalog=(*catalog(), entry(entity='course-duplicate')))
    assert result.diagnostic == 'unresolved_entity' and result.decision.missing_facts == ()


NOT_FOUND = {'en': 'could not find that course', 'fil': 'Hindi ko nakita ang kursong iyan',
             'taglish': 'Hindi ko nakita yung course na iyan'}
PRINTED = {'en': 'as printed in your prospectus', 'fil': 'nakasulat sa prospectus mo',
           'taglish': 'naka-print sa prospectus mo'}


@pytest.mark.parametrize('language', ['en', 'fil', 'taglish'])
def test_not_found_course_reply_names_the_problem_in_the_students_language(language):
    source = IntegrationResult(understanding=None, schema_version=IntegrationResult.SCHEMA_VERSION, request_id='req-a',
                               route=None, response_style=language, status='clarify', evidence=None,
                               missing_facts=('course_id',), events=())
    answer = asyncio.run(api().Generator(Fake(), explanation_profile='legacy').generate('Z9', source))
    assert answer.status == 'clarification_needed'
    assert NOT_FOUND['taglish' if language=='fil' else language] in answer.text and PRINTED['taglish' if language=='fil' else language] in answer.text
    assert 'course_id' not in answer.text
