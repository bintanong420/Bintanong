import asyncio
import importlib
import json

import pytest

from backend.bintanong_contracts.runtime import BoundInput
from backend.bintanong_contracts.symbolic import Capability, CapabilityRegistry
from backend.bintanong_routing.contracts import RequestContext
from test_routing_contracts import context, proposal
from test_routing_router import FakeTransport
from test_routing_validation import catalog, registry
from test_orchestration_integration import pin, documents, symbolic


def api():
    return importlib.import_module('backend.bintanong_orchestration.orchestrator')


def ports():
    return importlib.import_module('backend.bintanong_orchestration.ports')


class Documents:
    def __init__(self, result=None):
        self.result = documents() if result is None else result
        self.calls = []

    async def retrieve(self, request):
        self.calls.append(request)
        return self.result


class Symbolic:
    release_id = 'release-synth-1'
    rule_bundle_version = 'bundle-synth-1'

    def __init__(self):
        self.calls = []

    async def execute(self, request, ctx):
        self.calls.append((request, ctx))
        await asyncio.sleep(0)
        outcome = 'ineligible' if any(f.state == 'failed' for f in ctx.facts) else (
            'eligible' if any(f.state == 'passed' for f in ctx.facts) else 'unknown')
        value = symbolic(outcome).model_dump(mode='json')
        value['decision']['predicate'] = request.predicate
        value.update(capability='synthetic_prerequisite_check',
                     inputs=[i.model_dump(mode='json') for i in request.inputs])
        from backend.bintanong_contracts.symbolic import SymbolicResult
        return SymbolicResult.parse(value)


def resources(doc=None, sym=None):
    # Existing catalog source refs are bound to this fictional source version.
    aliases = tuple(c.model_copy(update={'source_ref':'ver-synth-handbook-1'}) for c in catalog())
    return ports().ReleaseResources(pin(), aliases, registry(),
        Documents() if doc is None else doc, Symbolic() if sym is None else sym)


def ctx(session='a', state='passed'):
    return RequestContext.parse(context(session_id='sess-'+session, request_id='req-'+session,
        facts=[] if state is None else [dict(fact_id='fact-'+session, session_id='sess-'+session,
            program_id='program-a', curriculum_id='curriculum-a',course_id='course-pre',state=state)]))


def transport(route='Symbolic', **kw):
    defaults = dict(route=route, operations=[] if route=='RAG' else proposal()['operations'])
    defaults.update(kw)
    return FakeTransport(json.dumps(proposal(**defaults)))


@pytest.mark.parametrize('route', ['RAG', 'Symbolic', 'Hybrid'])
def test_route_uses_existing_router_and_returns_one_common_evidence_package(route):
    async def scenario():
        release = resources()
        result = await api().Orchestrator(transport(route),
            releases=ports().SyntheticReleaseProvider(release)).run('A1', ctx())
        assert result.status == 'ready' and result.evidence.route == route
        assert result.response_style == 'taglish'
        assert len(release.retrieval.calls) == (route != 'Symbolic')
        assert len(release.symbolic.calls) == (route != 'RAG')
        assert result.evidence.pin == release.pin
        assert result.candidate_only and not result.institutional_use_allowed
        assert [e.stage for e in result.events][:2] == ['release','routing']
    asyncio.run(scenario())


def test_default_provider_holds_without_model_or_evidence_calls():
    async def scenario():
        model = transport()
        result = await api().Orchestrator(model).run('A1', ctx())
        assert result.status == 'held' and not model.calls and result.evidence is None
    asyncio.run(scenario())


def test_pin_once_even_if_provider_changes_between_branches():
    async def scenario():
        class Provider:
            calls = 0
            async def pin(self):
                self.calls += 1
                assert self.calls == 1
                return resources()
        provider = Provider()
        result = await api().Orchestrator(transport('Hybrid'), releases=provider).run('A1', ctx())
        assert result.status == 'ready' and provider.calls == 1
    asyncio.run(scenario())


def test_hybrid_waits_for_both_independent_branches():
    async def scenario():
        entered = asyncio.Event()
        class WaitDocuments(Documents):
            async def retrieve(self, request):
                entered.set()
                return await super().retrieve(request)
        class WaitSymbolic(Symbolic):
            async def execute(self, request, context):
                await entered.wait()
                return await super().execute(request, context)
        result = await api().Orchestrator(transport('Hybrid'), releases=
            ports().SyntheticReleaseProvider(resources(WaitDocuments(), WaitSymbolic()))).run('A1', ctx())
        assert result.status == 'ready'
    asyncio.run(scenario())


@pytest.mark.parametrize('problem,expected', [('timeout','timeout'), ('raise','tool_error'),
    ('bad','invalid_output')])
def test_hybrid_failure_never_returns_a_document_only_fallback(problem, expected):
    async def scenario():
        class Broken(Symbolic):
            async def execute(self, request, context):
                if problem == 'timeout':
                    await asyncio.Event().wait()
                if problem == 'raise':
                    raise RuntimeError('PRIVATE grade 5.00 student name')
                return 'unvalidated'
        model = transport('Hybrid')
        result = await api().Orchestrator(model, releases=ports().SyntheticReleaseProvider(
            resources(sym=Broken())), stage_timeout=0.05).run('A1', ctx())
        assert result.status == expected and result.evidence is None and result.route == 'Hybrid'
        assert len(model.calls) == 2  # original routing and style only
        assert 'PRIVATE' not in json.dumps([e.model_dump(mode='json') for e in result.events])
    asyncio.run(scenario())


def test_router_control_never_dispatches_evidence():
    async def scenario():
        release = resources()
        result = await api().Orchestrator(transport(None, control='greeting', operations=[]),
            releases=ports().SyntheticReleaseProvider(release)).run('A1', ctx())
        assert result.status == 'greeting' and result.evidence is None
        assert not release.symbolic.calls and not release.retrieval.calls
    asyncio.run(scenario())


def test_external_cancellation_cancels_both_async_branches():
    async def scenario():
        entered = asyncio.Event()
        cancelled = set()
        class WaitDoc(Documents):
            async def retrieve(self, request):
                try:
                    entered.set()
                    await asyncio.Event().wait()
                finally:
                    cancelled.add('documents')
        class WaitSym(Symbolic):
            async def execute(self, request, context):
                try:
                    await asyncio.Event().wait()
                finally:
                    cancelled.add('symbolic')
        pipeline = api().Orchestrator(transport('Hybrid'), releases=
            ports().SyntheticReleaseProvider(resources(WaitDoc(), WaitSym())))
        task = asyncio.create_task(pipeline.run('A1', ctx()))
        await entered.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert cancelled == {'documents','symbolic'}
    asyncio.run(scenario())


def test_telemetry_has_only_fixed_stage_outcomes_and_evidence_ids():
    async def scenario():
        result = await api().Orchestrator(transport('Hybrid'), releases=
            ports().SyntheticReleaseProvider(resources())).run('A1', ctx())
        for event in result.events:
            assert set(event.model_dump()) == {'stage','duration_ms','route','release_id',
                'outcome','retry_count','evidence_ids'}
            assert event.duration_ms >= 0
            assert 'sess-' not in event.model_dump_json() and 'fact-' not in event.model_dump_json()
        assert any(e.evidence_ids for e in result.events)
    asyncio.run(scenario())


def test_wrong_operation_identity_is_not_accepted_as_a_valid_symbolic_result():
    async def scenario():
        class Wrong(Symbolic):
            async def execute(self, req, context):
                value = await super().execute(req, context)
                return value.model_copy(update={'inputs':(BoundInput(
                    name='course_id', value='another', fact_ref=None), *value.inputs[:1])})
        result = await api().Orchestrator(transport(), releases=
            ports().SyntheticReleaseProvider(resources(sym=Wrong()))).run('A1', ctx())
        assert result.status == 'invalid_output' and result.evidence is None
    asyncio.run(scenario())


@pytest.mark.parametrize('state,status', [('passed','ready'), (None,'unknown')])
def test_telemetry_records_pinned_release_route_and_actual_integration_outcome(state,status):
    async def scenario():
        result = await api().Orchestrator(transport(),releases=
            ports().SyntheticReleaseProvider(resources())).run('A1',ctx(state=state))
        assert result.events[0].release_id == 'release-synth-1'
        assert result.events[1].route == 'Symbolic'
        assert result.events[-1].outcome == status
    asyncio.run(scenario())
