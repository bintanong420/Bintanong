"""LLM-routed explicit plans reach the checked host reply; synthetic curricula only."""
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
from test_planning_check import curriculum, CURRICULA, POLICY, SOURCE
from test_planning_chat import catalog
from test_routing_contracts import proposal
from test_routing_router import FakeTransport, style_proposal
from test_generation_research import NoModel


@pytest.fixture(autouse=True, params=['0', '1'])
def compile_mode(request, monkeypatch):
    monkeypatch.setenv('BINTANONG_ROUTER_COMPILE', request.param)


def run_plan(curriculum, plan_text, *, facts=(), audience='undergraduate', language='en'):
    key, runtime, c = curriculum
    prefix = 'Check my plan: ' if language == 'en' else 'Paki-check ang plan ko: '
    text = prefix + plan_text
    start = len(prefix)
    value = proposal(text=text, language=language, audience=audience, intent='check_study_plan',
        mentions=[dict(kind='term', text=plan_text, start=start, end=len(text))],
        operations=[dict(name='check_study_plan', target=0)])
    registry = CapabilityRegistry({'check_study_plan': Capability('synthetic_plan_check',
        ('curriculum_id', 'plan_sha256'))})
    pin = ReleasePin.parse(dict(release_id=runtime.release_id, synthetic=True, rule_bundle_version=runtime.rule_bundle_version,
        sources=[dict(version_id=SOURCE.version_id, byte_sha256=SOURCE.byte_sha256)]))
    entries = tuple(e.model_copy(update=dict(source_ref=SOURCE.version_id)) for e in catalog(key))
    labels = tuple((e.entity_id, e.aliases[0]) for e in entries)
    resources = ReleaseResources(pin, entries, registry, None, SymbolicAdapter(runtime, recovery=(POLICY, None)),
        course_labels=labels)
    context = RequestContext.parse(dict(session_id='sess-a', request_id='req-a', program_id='program-synthetic',
        curriculum_id=key, facts=tuple(dict(fact_id=f'fact-{i}', session_id='sess-a', program_id='program-synthetic',
            curriculum_id=key, course_id=course, state=state) for i,(course,state) in enumerate(facts))))
    async def run():
        result = await Orchestrator(FakeTransport(json.dumps(value), json.dumps(value),
            style_outputs=[json.dumps(style_proposal(language, english=['Check my plan'] if language == 'en' else [],
                filipino=[] if language == 'en' else ['ang plan ko']))]),
            releases=SyntheticReleaseProvider(resources)).run(text, context)
        answer = await Generator(NoModel()).generate(text, result)
        return result, answer
    return asyncio.run(run())


@pytest.mark.parametrize('language', ['en', 'taglish'])
def test_typed_plan_is_checked_then_rendered_without_a_generation_model(curriculum, language):
    key, _, c = curriculum
    codes = CURRICULA[key]
    result, answer = run_plan(curriculum,
        f"2nd year 2nd sem: {codes['X']} special class; summer: {codes['D1']}",
        facts=((c('BASE'), 'passed'),), language=language)
    assert result.status == 'ready' and answer.status == 'answered'
    assert result.plan_check is not None
    assert result.plan_check.checked_request.facts[0].course_id == c('BASE')
    text = student_text(answer)
    assert codes['X'] in text and codes['D1'] in text
    assert ('Works, needs confirmation' if language == 'en' else 'Works, may kailangan pang i-confirm') in text
    assert 'adviser' in text
    assert answer.part_ledger.status == 'all_declared_parts_mapped'
    assert answer.citations and all(card.kind == 'rule' for card in answer.citations)
    assert answer.plan_check == result.plan_check


def test_failed_prerequisite_blocks_a_typed_plan(curriculum):
    key, _, c = curriculum
    _, answer = run_plan(curriculum, f"2nd year 2nd sem: {CURRICULA[key]['D1']}",
        facts=((c('X'), 'failed'),))
    assert answer.status == 'answered' and 'Blocked' in student_text(answer)
    assert CURRICULA[key]['X'] in student_text(answer)


@pytest.mark.parametrize('body,missing', [('2nd sem: {X}', 'plan_term'),
    ('{X}', 'plan_terms'), ('2nd year 2nd sem: QQ 999', 'plan_courses'),
    ('2nd year 2nd sem: {X} automatic approval', 'plan_courses'),
    ('3rd year 1st sem: {X}; 2nd year 2nd sem: {D1}', 'plan_order')])
def test_plan_gaps_ask_a_specific_question(curriculum, body, missing):
    key, _, _ = curriculum
    result, answer = run_plan(curriculum, body.format(**CURRICULA[key]))
    assert result.status == 'clarify' and result.missing_facts == (missing,)
    assert answer.status == 'clarification_needed' and '?' in student_text(answer)
    assert 'temporarily unavailable' not in student_text(answer)


def test_plan_never_escapes_the_audience_guard(curriculum):
    key, _, _ = curriculum
    result, answer = run_plan(curriculum, f"2nd year 2nd sem: {CURRICULA[key]['X']}", audience='excluded')
    assert result.plan_check is None and answer.status == 'out_of_scope'


def test_plan_sidecar_cannot_disagree_with_its_evidence(curriculum):
    key, _, c = curriculum
    result, _ = run_plan(curriculum, f"2nd year 2nd sem: {CURRICULA[key]['X']}",
                         facts=((c('BASE'), 'passed'),))
    from backend.bintanong_orchestration.contracts import IntegrationResult
    data = result.model_dump(mode='json')
    data.pop('plan_check')
    with pytest.raises(ValueError, match='plan_check_evidence_mismatch'):
        IntegrationResult.parse(data)


def test_a_valid_result_for_another_plan_never_answers_the_question(curriculum, monkeypatch):
    key, _, c = curriculum
    original = SymbolicAdapter.check_typed_plan
    async def wrong_plan(adapter, request, context):
        from backend.bintanong_planning.contracts import PlanCheckRequest
        data = request.model_dump(mode='json')
        data['terms'][0]['courses'] = [dict(course_id=c('FILL'), mode='prescribed')]
        return await original(adapter, PlanCheckRequest.parse(data), context)
    monkeypatch.setattr(SymbolicAdapter, 'check_typed_plan', wrong_plan)
    result, answer = run_plan(curriculum, f"2nd year 2nd sem: {CURRICULA[key]['X']}",
                             facts=((c('BASE'), 'passed'),))
    assert result.status == 'invalid_output' and result.plan_check is None
    assert answer.status != 'answered' and 'Works' not in student_text(answer)
