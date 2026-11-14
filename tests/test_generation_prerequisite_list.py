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


def test_no_stated_fact_asks_about_the_single_prerequisite_directly():
    # Memory/eligibility plan (owner, 3 Nov 2026): one prerequisite is asked about by name; several are still listed
    # with "tell me which of these you passed" (step 2b, see the multi-course rendering tests below).
    answer = asyncio.run(Generator(NoModel()).generate('A1', research_integration()))  # fixture style: Taglish
    assert answer.status == 'clarification_needed'
    assert 'course-2 needs course-1. Naipasa mo na ba ang course-1? Sabihin mo lang at iche-check ko.' in answer.text
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
    assert 'Naipasa mo na ba ang course-3, o kinukuha mo ito ngayong term?' in text
    assert 'Naipasa mo na ba ang course-1?' not in text


BLANK = 'Printed prerequisite cell is blank; no explicit no-prerequisite statement; coverage unknown'
STANDING = 'Printed condition "3rd yr. Standing" is a year-level standing, not a course; unknown unless reviewed'


def unresolved_pack(reason, language, tree=None):
    from dataclasses import replace
    from backend.bintanong_generation.evidence import prepare
    pack = prepare(research_integration())
    decision = pack.decision.model_copy(update=dict(missing_facts=(), unknown_conditions=('rule_unresolved',)))
    tree = tree or RequirementView(kind='unresolved', reason=reason)
    return replace(pack, requirement=tree, decision=decision, missing_facts=(), language=language)


@pytest.mark.parametrize('reason,language,expected', [
    (BLANK, 'en', "The prospectus for this curriculum doesn't list a prerequisite for course-2. "
                  "Your program adviser or college can confirm if you need to be sure."),
    (BLANK, 'taglish', 'Walang nakalistang prerequisite ang course-2 sa prospectus ng curriculum na ito. '
                       'Pwede i-confirm sa program adviser o college kung gusto mong makasigurado.'),
    (STANDING, 'en', 'The prospectus prints "3rd yr. Standing" for course-2, but it isn\'t verified in the system '
                     'yet. Please confirm with your program adviser and the college.'),
    (STANDING, 'taglish', '"3rd yr. Standing" ang naka-print para sa course-2 sa prospectus, pero hindi pa verified '
                          'sa system. Paki-confirm sa program adviser at college.'),
    ('Fictional other reason', 'en', "Sorry, I can't confirm the prerequisite of course-2 yet. "
                                     "Please check with your program adviser or college."),
    ('Fictional other reason', 'taglish', 'Sorry, hindi ko pa ma-confirm ang prerequisite ng course-2. '
                                          'Paki-check sa program adviser o college.'),
])
def test_an_unresolved_rule_says_what_the_prospectus_shows(reason, language, expected):
    # Owner, 2 Nov 2026: say what is printed instead of a bare "please clarify"; a blank stays unknown, never "none".
    from backend.bintanong_generation.render import render_text
    text = render_text(unresolved_pack(reason, language), (), 'clarification_needed')
    assert expected in text.splitlines()
    for generic in ('Please clarify', 'Paki-clarify', 'Conditions', 'cannot be established', 'ma-establish',
                    'no prerequisite', 'walang prerequisite'):
        assert generic not in text


def test_a_partly_unresolved_rule_keeps_its_existing_reply():
    from backend.bintanong_generation.render import render_text
    tree = node('all_of', None, node('course', 'course-1'), RequirementView(kind='unresolved', reason=BLANK))
    text = render_text(unresolved_pack(BLANK, 'en', tree), (), 'clarification_needed')
    assert "doesn't list" not in text


def test_every_alternative_still_unknown_is_listed():
    from backend.bintanong_generation.render import render_text
    text = render_text(any_of_pack(('completion_unknown:course-1', 'completion_unknown:course-3'),
                                   ('enrollment_unknown:course-3',)), (), 'clarification_needed')
    assert 'course-2 needs alinman sa course-1 o course-3 (naipasa na o kinukuha nang sabay).' in text


def test_several_prerequisites_with_no_stated_fact_are_still_listed():
    from dataclasses import replace
    from backend.bintanong_generation.evidence import prepare
    from backend.bintanong_generation.render import render_text
    pack = prepare(research_integration())
    missing = ('completion_unknown:course-1', 'completion_unknown:course-3')
    decision = pack.decision.model_copy(update=dict(missing_facts=missing))
    pack = replace(pack, requirement=node('all_of', None, node('course', 'course-1'), node('course', 'course-3')),
                   decision=decision, missing_facts=missing)
    text = render_text(pack, (), 'clarification_needed')
    assert 'course-2 needs parehong course-1 at course-3.' in text
    assert 'Sabihin mo lang at iche-check ko' in text
