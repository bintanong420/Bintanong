"""Memory/eligibility plan, Task 1: a message that only states a result is acknowledged as a scoped fact.
Synthetic course labels only."""
import asyncio

import pytest

from backend.bintanong_api.presentation import student_text
from backend.bintanong_orchestration.contracts import IntegrationResult
from test_generation_loop import Fake, api

NOTED = {'en': 'Noted: you passed A 1. I will use this in this chat for your selected curriculum.',
         'taglish': 'Noted: passed mo na ang A 1. Gagamitin ko ito sa chat na ito para sa napili mong curriculum.'}


@pytest.mark.parametrize('language', ['en', 'taglish'])
def test_a_stated_result_is_acknowledged_without_a_missing_information_line(language):
    source = IntegrationResult(understanding=None, schema_version=IntegrationResult.SCHEMA_VERSION, request_id='req-a',
                               route=None, response_style=language, status='clarify', evidence=None,
                               missing_facts=('noted_passed:course-a',), events=(), course_labels={'course-a': 'A 1'})
    answer = asyncio.run(api().Generator(Fake(), explanation_profile='legacy').generate('I passed A1', source))
    shown = student_text(answer)
    assert shown == NOTED[language]
    assert 'noted_' not in answer.text and 'course-a' not in answer.text


def test_several_noted_results_keep_their_own_states():
    source = IntegrationResult(understanding=None, schema_version=IntegrationResult.SCHEMA_VERSION, request_id='req-a',
                               route=None, response_style='en', status='clarify', evidence=None,
                               missing_facts=('noted_passed:course-a', 'noted_not_taken:course-b'), events=(),
                               course_labels={'course-a': 'A 1', 'course-b': 'B 1'})
    answer = asyncio.run(api().Generator(Fake(), explanation_profile='legacy').generate('A1 B1', source))
    assert student_text(answer) == ('Noted: you passed A 1, and you have not taken B 1 yet. '
                                    'I will use this in this chat for your selected curriculum.')
