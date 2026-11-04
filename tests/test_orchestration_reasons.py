"""Audit A03 (4 Nov 2026): a turn the host could not follow is a dialogue failure, never "not in the reviewed sources".
Every routing diagnostic has an explicit reason code. Synthetic fixtures only."""
import asyncio
import json
import re
from pathlib import Path

import pytest

from backend.bintanong_generation.generator import Generator
from backend.bintanong_orchestration.reasons import ROUTING_REASONS, STATUS_REASONS, evidence_reason, routing_reason
from backend.bintanong_routing.contracts import RequestContext
from test_generation_research import NoModel
from test_orchestration_pipeline import api, ports, resources, ctx
from test_private_context_conversation import previous
from test_routing_contracts import proposal
from test_routing_router import FakeTransport

ROOT = Path(__file__).resolve().parents[1] / 'backend' / 'bintanong_routing'
SOURCE_GAP = ("not in Bintanong's reviewed sources", 'Wala pa ito sa reviewed sources', 'university office')


def emitted_diagnostics():
    """Every diagnostic literal the router, combined router and validation can produce, plus model transport codes."""
    found = set()
    for name in ('validation.py', 'router.py', 'combined.py', 'transport.py'):
        text = (ROOT / name).read_text(encoding='utf-8')
        found |= set(re.findall(r"\b(?:result|failure)\('([a-z_]+)'", text))
        found |= set(re.findall(r"diagnostic='([a-z_]+)'", text))
        found |= set(re.findall(r"RuntimeFailure\('([a-z_]+)'", text))
    return found


def test_every_routing_diagnostic_has_an_explicit_reason():
    diagnostics = emitted_diagnostics()
    assert {'empty_clarification', 'missing_scope', 'invalid_model_output', 'model_timeout'} <= diagnostics
    assert diagnostics - {'model_control'} <= set(ROUTING_REASONS)


@pytest.mark.parametrize('diagnostic,control,expected', [
    ('empty_clarification', 'evidence_unavailable', 'dialogue_unresolved'),
    ('model_control', 'clarify', 'clarification_pending'),
    ('model_control', 'unsupported_scope', 'unsupported_scope'),
    ('model_control', 'greeting', None),
    ('unsupported_operation', 'evidence_unavailable', 'capability_unavailable'),
    ('invalid_grounding', 'evidence_unavailable', 'route_interpretation'),
    ('model_timeout', 'evidence_unavailable', 'system_error'),
    ('validated', None, None),
])
def test_routing_reasons(diagnostic, control, expected):
    assert routing_reason(diagnostic, control) == expected


def test_stage_statuses_have_reasons():
    assert evidence_reason('no_evidence') == 'retrieval_coverage'
    assert evidence_reason('conflict') == 'source_conflict'
    assert evidence_reason('timeout') == 'system_error' and evidence_reason('held') == 'capability_unavailable'
    assert STATUS_REASONS['ready'] is None


def empty_clarify():
    return proposal(text='A1', route=None, control='clarify', mentions=[], operations=[], claims=[])


def repair(conversation=None):
    context = ctx()
    if conversation is not None:
        context = RequestContext.parse(dict(context.model_dump(mode='json'),
                                            conversation=conversation.model_dump(mode='json')))

    async def scenario():
        provider = ports().SyntheticReleaseProvider(resources())
        integration = await api().Orchestrator(FakeTransport(json.dumps(empty_clarify())),
                                               releases=provider).run('A1', context)
        return integration, await Generator(NoModel()).generate('A1', integration)
    return asyncio.run(scenario())


def test_a_repair_with_no_previous_context_says_it_lost_track():
    integration, answer = repair()
    assert integration.status == 'clarify' and integration.reason == 'dialogue_unresolved'
    assert answer.status == 'clarification_needed' and answer.reason == 'dialogue_unresolved'
    # fixture style: Taglish
    assert 'Sorry, na-lost track ako — anong subject o topic ang tinatanong mo?' in answer.text.splitlines()
    assert not any(gap in answer.text for gap in SOURCE_GAP)


def test_a_repair_names_the_previous_course_back():
    integration, answer = repair(previous())
    assert integration.missing_facts == ('previous_course:course-a',)
    assert answer.text.splitlines()[1].startswith('Tungkol sa ')
    assert 'iyan ba ang ibig mong sabihin?' in answer.text
    assert not any(gap in answer.text for gap in SOURCE_GAP)


def test_english_repair_wording():
    from backend.bintanong_generation.dialogue_reply import dialogue_text
    assert dialogue_text((), 'en') == 'Sorry, I lost track — which subject or topic are you asking about?'
    assert dialogue_text(('previous_course:course-a',), 'en', {'course-a': 'IT 14/L'}.get) == (
        "You asked about IT 14/L earlier — is that the one you mean? Tell me what you'd like to know about it, "
        "and I'll check.")
    assert dialogue_text(('previous_topic:handbook_graduation',), 'en').startswith(
        'You asked about the graduation topic earlier')


def test_an_answered_turn_has_no_reason():
    from test_orchestration_research_evidence import research_integration
    answer = asyncio.run(Generator(NoModel()).generate('A1', research_integration((('course-1', 'passed'),))))
    assert answer.status == 'answered' and answer.reason is None


@pytest.mark.parametrize('gap',['context_budget:chunk','missing_required_neighbor:chunk','requested_claim_not_established'])
def test_retrieval_gaps_do_not_claim_the_original_source_is_defective(gap):
    from types import SimpleNamespace
    evidence=SimpleNamespace(documents=SimpleNamespace(gaps=(gap,)), symbolic=None,
                             course_facts=None,term_assessment=None)
    assert evidence_reason('no_evidence',evidence)=='retrieval_coverage'
