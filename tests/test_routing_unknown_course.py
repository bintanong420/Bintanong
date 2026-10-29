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


def test_course_matching_two_reviewed_courses_names_both_choices():
    # Owner, 29 Oct 2026 ("Ask which one"): a shared abbreviation or repeated printed code lists its candidates.
    result = validate(catalog=(*catalog(), entry(entity='course-duplicate')))
    assert result.diagnostic == 'unresolved_entity' and result.decision.control == 'clarify'
    assert result.decision.missing_facts == ('course_choice:course-a', 'course_choice:course-duplicate')


CHOICE = {'en': 'Which course do you mean: A 1 or A 1 (other)?', 'taglish': 'Aling course ang ibig mong sabihin: A 1 or A 1 (other)?'}


@pytest.mark.parametrize('language', ['en', 'taglish'])
def test_choice_reply_names_each_candidate_by_its_printed_label(language):
    source = IntegrationResult(understanding=None, schema_version=IntegrationResult.SCHEMA_VERSION, request_id='req-a',
                               route=None, response_style=language, status='clarify', evidence=None,
                               missing_facts=('course_choice:course-a', 'course_choice:course-duplicate'), events=(),
                               course_labels={'course-a': 'A 1', 'course-duplicate': 'A 1 (other)'})
    answer = asyncio.run(api().Generator(Fake(), explanation_profile='legacy').generate('A1', source))
    assert answer.status == 'clarification_needed' and CHOICE[language] in answer.text
    assert 'course_choice' not in answer.text and 'course-a' not in answer.text


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
