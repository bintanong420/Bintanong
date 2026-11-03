"""Owner/thesis leader, 4 Nov 2026: a message that is only a program name is a clarification naming it, never an
outage. Live, the router called its one part unknown and the student read "The check is temporarily unavailable"."""
import asyncio
import json

import pytest

from backend.bintanong_orchestration.contracts import IntegrationResult
from test_generation_loop import Fake, api as generation
from test_routing_router import FakeTransport, run, style_proposal
from test_routing_contracts import proposal
from routing_wire_fixtures import wire_fixture

TEXT = 'Program A'


def bare_name(**updates):
    value = proposal(text=TEXT, mentions=[dict(kind='program', text=TEXT, start=0, end=9)], operations=[],
                     route='RAG', parts=[dict(part_id='r1', text=TEXT, start=0, end=9, evidence_need='unknown',
                                              operation_indices=[])])
    value.update(updates)
    return json.dumps(value)


def test_a_bare_program_name_asks_what_the_student_wants_to_know():
    style = json.dumps(style_proposal('en', english=[TEXT]))
    result = run(FakeTransport(bare_name(language='en'), style_outputs=[style]), text=TEXT)
    assert result.decision.control == 'clarify' and result.decision.route is None
    assert result.decision.missing_facts == ('program_topic:program-a',)
    assert result.diagnostic == 'bare_program_name'


def test_zero_parts_with_an_unknown_placeholder_reaches_bare_program_clarification():
    # Recorded cx-bare-bscs/cx-bare-cs wire shape, with a synthetic program.
    value = wire_fixture(json.loads(bare_name(language='en')), TEXT)
    value['part_count'] = 0
    result = run(FakeTransport(json.dumps(value), json.dumps(value), style_outputs=[
        json.dumps(style_proposal('en', english=[TEXT]))]), text=TEXT)
    assert result.diagnostic == 'bare_program_name'
    assert result.decision.missing_facts == ('program_topic:program-a',)
    assert result.attempts == 1


@pytest.mark.parametrize('language,expected', [
    ('en', 'Got it: Program A. What would you like to know about it, such as subjects for a term or a prerequisite?'),
    ('taglish', 'Sige: Program A. Ano ang gusto mong malaman tungkol dito, halimbawa subjects sa isang sem o '
                'prerequisite?')])
def test_the_clarification_names_the_program_in_the_students_language(language, expected):
    source = IntegrationResult(understanding=None, schema_version=IntegrationResult.SCHEMA_VERSION, request_id='req-a',
                               route=None, response_style=language, status='clarify', evidence=None,
                               missing_facts=('program_topic:program-a',), events=(),
                               course_labels={'program-a': 'Program A'})
    answer = asyncio.run(generation().Generator(Fake(), explanation_profile='legacy').generate(TEXT, source))
    assert answer.status == 'clarification_needed'
    assert expected in answer.text.splitlines() and 'program_topic' not in answer.text


def test_a_program_name_with_a_real_question_is_not_a_bare_name():
    text = 'Program A prerequisites of A1'
    value = proposal(text=text, mentions=[dict(kind='program', text='Program A', start=0, end=9),
                                           dict(kind='course', text='A1', start=27, end=29)],
                     operations=[dict(name='check_prerequisite_eligibility', target=1)])
    assert run(FakeTransport(json.dumps(value)), text=text).decision.route == 'Symbolic'
