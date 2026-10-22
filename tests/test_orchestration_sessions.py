import asyncio
import json

import pytest

from backend.bintanong_routing.contracts import RequestContext
from test_orchestration_pipeline import api, ports, resources, ctx, transport
from test_routing_contracts import proposal
from test_routing_router import FakeTransport


def test_concurrent_sessions_keep_facts_in_their_own_evidence_branch():
    async def scenario():
        release = resources()
        provider = ports().SyntheticReleaseProvider(release)
        results = await asyncio.gather(*(
            api().Orchestrator(transport(), releases=provider).run('A1', ctx(name, state))
            for name,state in [('a','passed'),('b','failed'),('c',None)]))
        assert [r.status for r in results] == ['ready','ready','unknown']
        assert [r.evidence.symbolic.decision.outcome for r in results] == [
            'eligible','ineligible','unknown']
        for req, context in release.symbolic.calls:
            assert all(f.session_id == context.session_id for f in context.facts)
    asyncio.run(scenario())


def test_followup_reuses_only_explicitly_supplied_context_and_does_not_persist_it():
    async def scenario():
        provider = ports().SyntheticReleaseProvider(resources())
        first = await api().Orchestrator(transport(), releases=provider).run('A1', ctx('a','failed'))
        followup = ctx('a','failed').model_copy(update={'request_id':'req-followup'})
        second = await api().Orchestrator(transport(), releases=provider).run('A1', followup)
        forgotten = await api().Orchestrator(transport(), releases=provider).run('A1', ctx('a',None))
        assert first.evidence.symbolic.decision.outcome == second.evidence.symbolic.decision.outcome == 'ineligible'
        assert forgotten.status == 'unknown'  # no hidden transcript/session store
        assert followup.request_id == 'req-followup' and len(followup.facts) == 1
    asyncio.run(scenario())


def test_new_assertion_is_request_local_and_hypotheticals_never_enter_runtime():
    async def scenario():
        for mode,expected in [('asserted','ready'),('hypothetical','clarify'),('reported','clarify')]:
            release = resources()
            value = proposal(claims=[dict(entity=0,state='failed',mode=mode,text='A1',start=0,end=2)])
            context = ctx('a',None)
            result = await api().Orchestrator(FakeTransport(json.dumps(value)), releases=
                ports().SyntheticReleaseProvider(release)).run('A1', context)
            assert result.status == expected
            assert context.facts == ()
            if mode == 'asserted':
                assert release.symbolic.calls[0][1].facts[0].state == 'failed'
                assert result.evidence.symbolic.decision.outcome == 'ineligible'
            else:
                assert not release.symbolic.calls
    asyncio.run(scenario())


def test_foreign_session_or_curriculum_cannot_be_reused_as_followup_context():
    for update in [dict(session_id='sess-b'),dict(curriculum_id='curriculum-b')]:
        with pytest.raises(ValueError):
            ctx().model_copy(update=update)


def test_missing_target_is_clarified_without_borrowing_the_previous_answer():
    async def scenario():
        release = resources()
        provider = ports().SyntheticReleaseProvider(release)
        await api().Orchestrator(transport(), releases=provider).run('A1', ctx())
        value = proposal(route=None,control='clarify',mentions=[],operations=[],claims=[],
            ambiguities=['Which course?'])
        # Synthetic style protocol evidence, not a language quality assertion.
        style = json.dumps(dict(schema_version='bintanong-response-style-v1',style=dict(
            english_fragments=['And'],filipino_fragments=[],preferred_response_style='english_only')))
        result = await api().Orchestrator(FakeTransport(json.dumps(value),style_outputs=[style]),
            releases=provider).run('And that one?',ctx())
        assert result.status == 'clarify' and len(release.symbolic.calls) == 1
    asyncio.run(scenario())
