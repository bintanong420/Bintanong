"""Earliest-term questions use LLM routing and checked rules before the host renders a reply."""
import asyncio
import json

import pytest

from backend.bintanong_contracts.symbolic import Capability, CapabilityRegistry
from backend.bintanong_generation.generator import Generator
from backend.bintanong_api.presentation import student_text
from backend.bintanong_orchestration.adapters import SymbolicAdapter
from backend.bintanong_orchestration.contracts import ReleasePin
from backend.bintanong_orchestration.orchestrator import Orchestrator
from backend.bintanong_orchestration.ports import ReleaseResources, SyntheticReleaseProvider
from backend.bintanong_routing.contracts import RequestContext
from test_planning_check import curriculum, CURRICULA, SOURCE
from test_planning_chat import catalog
from test_routing_contracts import proposal
from test_routing_router import FakeTransport, style_proposal
from test_generation_research import NoModel


@pytest.fixture(autouse=True, params=['0', '1'])
def compile_mode(request, monkeypatch):
    monkeypatch.setenv('BINTANONG_ROUTER_COMPILE', request.param)


def run_earliest(curriculum, language='en', *, term=True):
    key, runtime, c = curriculum
    code = CURRICULA[key]['Z']
    text = (f'When is the earliest I can take {code}?' if language == 'en' else
            f'Kailan ko pinakamaagang puwedeng kunin ang {code}?')
    if term:
        text += ' Starting 2nd year 2nd sem.'
    start = text.index(code)
    value = proposal(text=text, language=language, intent='earliest_course_term',
        mentions=[dict(kind='course', text=code, start=start, end=start+len(code))],
        operations=[dict(name='earliest_course_term', target=0)])
    registry = CapabilityRegistry({'earliest_course_term': Capability('synthetic_earliest_term',
        ('curriculum_id', 'course_id', 'year_level', 'semester'))})
    pin = ReleasePin.parse(dict(release_id=runtime.release_id, synthetic=True,
        rule_bundle_version=runtime.rule_bundle_version,
        sources=[dict(version_id=SOURCE.version_id, byte_sha256=SOURCE.byte_sha256)]))
    entries = tuple(e.model_copy(update=dict(source_ref=SOURCE.version_id)) for e in catalog(key))
    resources = ReleaseResources(pin, entries, registry, None, SymbolicAdapter(runtime),
        course_labels=tuple((e.entity_id, e.aliases[0]) for e in entries))
    context = RequestContext.parse(dict(session_id='sess-a', request_id='req-a', program_id='program-synthetic',
        curriculum_id=key, facts=[dict(fact_id='fact-x', session_id='sess-a', program_id='program-synthetic',
            curriculum_id=key, course_id=c('X'), state='failed')]))
    style = style_proposal(language, english=['When is the earliest'] if language == 'en' else [],
        filipino=[] if language == 'en' else ['Kailan ko'])
    async def run():
        result = await Orchestrator(FakeTransport(json.dumps(value), json.dumps(value),
            style_outputs=[json.dumps(style)]), releases=SyntheticReleaseProvider(resources)).run(text, context)
        return result, await Generator(NoModel()).generate(text, result)
    return asyncio.run(run())


@pytest.mark.parametrize('language', ['en', 'taglish'])
def test_earliest_question_reaches_a_cited_host_answer(curriculum, language):
    key, _, c = curriculum
    result, answer = run_earliest(curriculum, language)
    assert result.status == 'ready' and answer.status == 'answered'
    text = student_text(answer)
    assert CURRICULA[key]['Z'] in text
    assert 'fourth year, second semester' in text
    assert 'adviser' in text and 'assum' in text.lower()
    assert answer.citations and all(card.kind == 'rule' for card in answer.citations)
    assert answer.earliest_term.inputs == result.understanding.predicate_request.inputs


def test_earliest_question_without_a_start_term_asks_for_it(curriculum):
    result, answer = run_earliest(curriculum, term=False)
    assert result.status == 'clarify' and result.missing_facts == ('earliest_start_term',)
    assert answer.status == 'clarification_needed'
    assert 'year and semester' in student_text(answer) and '?' in student_text(answer)


def test_many_rule_spans_keep_all_proof_within_the_card_budget(curriculum):
    from backend.bintanong_generation.evidence import prepare
    result, _ = run_earliest(curriculum)
    data = result.model_dump(mode='json')
    template = data['evidence']['earliest_term']['rule_spans'][0]
    spans = [{**template, 'text':f'Fictional prerequisite proof {i}.'} for i in range(40)]
    data['evidence']['earliest_term']['rule_spans'] = spans
    from backend.bintanong_orchestration.contracts import IntegrationResult
    pack = prepare(IntegrationResult.parse(data))
    assert len(pack.cards) == 1
    assert len(pack.cards[0].citations) == 40
    assert all(s['text'] in pack.cards[0].text for s in spans)


def test_result_checked_with_other_facts_cannot_answer_my_request(curriculum, monkeypatch):
    original = SymbolicAdapter.earliest_term
    async def wrong_facts(adapter, course_id, context, start_term):
        altered = context.model_copy(update=dict(facts=tuple(f.model_copy(update=dict(state='passed'))
                                                             for f in context.facts)))
        return await original(adapter, course_id, altered, start_term)
    monkeypatch.setattr(SymbolicAdapter, 'earliest_term', wrong_facts)
    result, answer = run_earliest(curriculum)
    assert result.status == 'invalid_output' and answer.status != 'answered'
