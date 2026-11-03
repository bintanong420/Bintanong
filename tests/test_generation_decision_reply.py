"""Memory/eligibility plan, Task 3: the checked Prolog result is the evidence; the host states the conclusion first,
Bintu explains it, and a draft that reverses or invents anything never reaches the student. Synthetic ledger only
(course-2 requires course-1)."""
import asyncio
import json
from dataclasses import replace

import pytest

from backend.bintanong_api.presentation import student_text
from backend.bintanong_generation.evidence import prepare
from backend.bintanong_generation.generator import Generator
from backend.bintanong_generation.render import render_text
from backend.bintanong_routing.transport import RuntimeFailure
from test_generation_research import NoModel
from test_orchestration_research_evidence import research_integration


class Model:
    def __init__(self, *outputs):
        self.outputs, self.calls = list(outputs), []

    async def infer(self, messages, schema):
        self.calls.append((messages, schema))
        value = self.outputs.pop(0)
        if isinstance(value, Exception):
            raise value
        return value


def explained(text, language='taglish'):
    return json.dumps(dict(schema_version='bintanong-decision-explanation-v1', language=language, explanation=text))


def first_line(answer):
    return student_text(answer).splitlines()[0]


@pytest.mark.parametrize('facts,status,first', [
    ((('course-1', 'passed'),), 'answered',
     'Oo. Pasok ka sa prerequisite ng course-2, base sa sinabi mong naipasa mo ang course-1.'),
    ((('course-1', 'failed'),), 'answered',
     'Hindi pa. Kailangan mo munang maipasa ang course-1 bago mo makuha ang course-2.'),
    ((), 'clarification_needed', 'course-1 ang prerequisite ng course-2. Naipasa mo na ba ang course-1?'),
])
def test_the_scoped_conclusion_comes_first_even_without_the_model(facts, status, first):
    answer = asyncio.run(Generator(NoModel()).generate('A1', research_integration(facts=facts)))
    assert answer.status == status and first_line(answer) == first
    assert answer.decision_explanation is None
    assert 'Conditions' not in student_text(answer) and 'supported prerequisite check' not in answer.text


@pytest.mark.parametrize('facts,expected', [
    ((('course-1', 'passed'),), ['Yes. You meet the prerequisite for course-2, based on your report that you passed course-1.',
                                 'Rule: course-2 requires course-1.']),
    ((('course-1', 'failed'),), ['Not yet. You need to pass course-1 before you can take course-2.',
                                 'Rule: course-2 requires course-1.']),
    ((), ['course-2 requires course-1. Have you passed course-1?']),
])
def test_english_conclusions_keep_the_rule_and_ask_only_for_the_missing_result(facts, expected):
    pack = replace(prepare(research_integration(facts=facts)), language='en')
    status = 'answered' if facts else 'clarification_needed'
    shown = [line for line in render_text(pack, (), status).splitlines()[1:] if line != 'Based on the supplied evidence:' and not line.startswith('Check scope')]
    assert shown[:len(expected)] == expected


def test_bintu_explains_from_the_checked_evidence_after_prolog():
    model = Model(explained('course-1 ang nag-iisang prerequisite ng course-2, at sinabi mong naipasa mo na ito.'))
    answer = asyncio.run(Generator(model).generate('A1', research_integration(facts=(('course-1', 'passed'),))))
    assert answer.status == 'answered'
    assert answer.decision_explanation == 'course-1 ang nag-iisang prerequisite ng course-2, at sinabi mong naipasa mo na ito.'
    lines = student_text(answer).splitlines()
    assert lines[0].startswith('Oo. Pasok ka') and lines[1] == answer.decision_explanation
    messages, schema = model.calls[0]
    evidence = json.loads(messages[1]['content'])['evidence']
    assert evidence['outcome'] == 'eligible' and evidence['target'] == 'course-2'
    assert evidence['rule'] == {'kind': 'course', 'course': 'course-1'}
    assert evidence['satisfied'] == ['passed:course-1'] and evidence['reply_language'] == 'taglish'
    assert schema['properties']['schema_version']['const'] == 'bintanong-decision-explanation-v1'


def test_a_checked_unknown_also_gets_the_explanation_and_still_asks_first():
    model = Model(explained('Kailangan muna ang course-1 bago ang course-2.'))
    answer = asyncio.run(Generator(model).generate('A1', research_integration()))
    assert answer.status == 'clarification_needed'
    assert first_line(answer) == 'course-1 ang prerequisite ng course-2. Naipasa mo na ba ang course-1?'
    assert answer.decision_explanation == 'Kailangan muna ang course-1 bago ang course-2.'


@pytest.mark.parametrize('facts,draft', [
    ((('course-1', 'passed'),), 'Hindi ka pa pwede kumuha ng course-2.'),        # reverses eligible
    ((('course-1', 'failed'),), 'Pwede mo nang i-take ang course-2.'),             # reverses ineligible
    ((('course-1', 'passed'),), 'Kailangan mo rin ang CS 99 bago ang course-2.'),  # invents a prerequisite
    ((('course-1', 'passed'),), 'Naka-enroll ka na sa course-2 at approved na ito.'),  # promises enrollment
    ((), 'Pwede mo nang kunin ang course-2.'),                                     # a verdict where none exists
])
def test_a_draft_that_reverses_invents_or_promises_never_reaches_the_student(facts, draft):
    answer = asyncio.run(Generator(Model(explained(draft))).generate('A1', research_integration(facts=facts)))
    assert answer.decision_explanation is None and draft not in answer.text
    assert first_line(answer).startswith(('Oo.', 'Hindi pa.', 'course-1 ang prerequisite'))


@pytest.mark.parametrize('failure', [RuntimeFailure('model_timeout'), RuntimeFailure('model_connection_error'),
                                     'not json', explained('x' * 700)])
def test_a_failed_or_invalid_explanation_falls_back_to_the_host_conclusion(failure):
    answer = asyncio.run(Generator(Model(failure)).generate('A1', research_integration(facts=(('course-1', 'passed'),))))
    assert answer.status == 'answered' and answer.decision_explanation is None
    assert first_line(answer).startswith('Oo. Pasok ka')


WHAT_IF = 'If I failed P1, can I take A1?'


def what_if():
    """A what-if premise about course-1 (alias P1) for the check on course-2 (alias A1)."""
    from test_routing_contracts import proposal
    value = proposal(text=WHAT_IF, mentions=[dict(kind='course', text='P1', start=12, end=14),
                                             dict(kind='course', text='A1', start=27, end=29)],
                     claims=[dict(entity=0, state='failed', mode='hypothetical', text='If I failed P1', start=0, end=14)],
                     operations=[dict(name='check_prerequisite_eligibility', target=1)])
    return research_integration(text=WHAT_IF, value=value, aliases=(('course-1', 'P1'),))


def test_a_what_if_answer_says_it_is_conditional_and_unsaved():
    integration = what_if()
    assert integration.assumed_facts == ('failed:course-1',)
    answer = asyncio.run(Generator(NoModel()).generate(WHAT_IF, integration))
    lines = student_text(answer).splitlines()
    assert lines[0] == 'Hindi pa. Kailangan mo munang maipasa ang course-1 bago mo makuha ang course-2.'
    assert lines[1] == ('Assumption lang ito base sa tanong mo: failed ka sa course-1. '
                        'Hindi ito sine-save bilang record mo.')


def test_a_what_if_premise_is_never_remembered():
    from types import SimpleNamespace
    from backend.bintanong_private_context.memory import accepted_facts
    claim = SimpleNamespace(mode='hypothetical', session_id='sess-a', program_id='program-a', curriculum_id='c',
                            course_id='course-1', state='failed', period=None)
    assert accepted_facts(SimpleNamespace(claims=(claim,)), 'msg-1') == ()


@pytest.mark.parametrize('facts,draft', [
    # Live draft, 3 Nov 2026 (Lawrence case): "before you can take" is the condition, not a verdict.
    ((('course-1', 'failed'),), 'The rule requires that you must have passed course-1 before you can take course-2.'),
    ((('course-1', 'failed'),), 'Kailangan mo munang maipasa ang course-1 bago mo ma-take ang course-2.'),
    ((('course-1', 'failed'),), 'You need course-1 first so that you can take course-2.'),
])
def test_a_condition_clause_is_not_read_as_a_verdict(facts, draft):
    from backend.bintanong_generation.decision_reply import explanation_errors
    pack = prepare(research_integration(facts=facts))
    assert explanation_errors(pack, draft) == ()
