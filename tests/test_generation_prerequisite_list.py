"""Owner, 24 Oct 2026 (step 2b): with no passed/failed course stated, a prerequisite check lists the reviewed
prerequisites and asks which ones the student passed, instead of "eligibility cannot be established".
Synthetic ledgers only."""
import asyncio

import pytest

from backend.bintanong_generation.generator import Generator
from backend.bintanong_generation.render import requirement_text
from backend.bintanong_contracts.symbolic import RequirementView
from test_generation_research import NoModel
from test_orchestration_research_evidence import research_integration
from test_symbolic_runtime import expression_ledger, facts, request, runtime


def node(kind, course=None, *items):
    return RequirementView(kind=kind, course_id=course, items=items)


@pytest.mark.parametrize('kind', ['all_of', 'any_of'])
def test_runtime_returns_the_reviewed_requirement_tree(kind):
    result = runtime(expression_ledger(kind)).check(request(), facts())
    assert result.requirement == node(kind, None, node('course', 'course-1'), node('course', 'course-3'))


def test_no_stated_fact_lists_the_prerequisites_and_asks_which_were_passed():
    answer = asyncio.run(Generator(NoModel()).generate('A1', research_integration()))  # fixture style: Taglish
    assert answer.status == 'clarification_needed'
    assert 'Prerequisites ng course-2: course-1.' in answer.text
    assert 'Sabihin mo kung alin dito ang na-pass mo na' in answer.text
    assert 'Hindi pa ma-establish ang eligibility' not in answer.text


def test_a_stated_fact_keeps_the_eligibility_check():
    answer = asyncio.run(Generator(NoModel()).generate('A1', research_integration(facts=(('course-1', 'failed'),))))
    assert answer.decision.outcome == 'ineligible' and 'Prerequisites ng' not in answer.text


@pytest.mark.parametrize('language,expected', [
    ('en', 'A and (one of: B, C (or take it at the same time))'),
    ('fil', 'A at (isa sa: B, C (o kunin nang sabay))'),
    ('taglish', 'A and (one of: B, C (or i-take nang sabay))'),
])
def test_requirement_wording_keeps_all_of_any_of_and_co_requisites(language, expected):
    tree = node('all_of', None, node('course', 'A'),
                node('any_of', None, node('course', 'B'), node('co_requisite', 'C')))
    assert requirement_text(tree, language) == expected


def any_of_pack(missing, unknown=()):
    from dataclasses import replace
    from backend.bintanong_generation.evidence import prepare
    pack = prepare(research_integration())
    tree = node('any_of', None, node('course', 'course-1'), node('co_requisite', 'course-3'))
    decision = pack.decision.model_copy(update=dict(missing_facts=missing, unknown_conditions=unknown))
    return replace(pack, requirement=tree, decision=decision, missing_facts=missing)


def test_a_fact_about_one_alternative_keeps_the_eligibility_check():
    from backend.bintanong_generation.render import render_text
    # "I failed course-1": the any-of result is still unknown, with no violated condition left to show it.
    text = render_text(any_of_pack(('completion_unknown:course-3',), ('enrollment_unknown:course-3',)),
                       (), 'clarification_needed')
    assert 'Prerequisites ng' not in text


def test_every_alternative_still_unknown_is_listed():
    from backend.bintanong_generation.render import render_text
    text = render_text(any_of_pack(('completion_unknown:course-1', 'completion_unknown:course-3'),
                                   ('enrollment_unknown:course-3',)), (), 'clarification_needed')
    assert 'Prerequisites ng course-2: one of: course-1, course-3 (or i-take nang sabay).' in text
