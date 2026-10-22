import asyncio
import importlib
import json
import hashlib

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
    defaults = dict(text='A1 policy',route=route, operations=[] if route=='RAG' else proposal()['operations'])
    defaults.update(kw)
    return FakeTransport(json.dumps(proposal(**defaults)))


@pytest.mark.parametrize('route', ['RAG', 'Symbolic', 'Hybrid'])
def test_route_uses_existing_router_and_returns_one_common_evidence_package(route):
    async def scenario():
        release = resources()
        result = await api().Orchestrator(transport(route),
            releases=ports().SyntheticReleaseProvider(release)).run('A1 policy', ctx())
        assert result.status == 'ready' and result.evidence.route == route
        assert result.response_style == 'taglish'
        assert len(release.retrieval.calls) == (route != 'Symbolic')
        assert len(release.symbolic.calls) == (route != 'RAG')
        assert result.evidence.pin == release.pin
        assert result.understanding.request_id==ctx().request_id
        assert result.understanding.release_id==release.pin.release_id
        assert result.understanding.question_sha256==hashlib.sha256(b'A1 policy').hexdigest()
        assert len(result.understanding.parts)==(2 if route=='Hybrid' else 1)
        assert result.candidate_only and not result.institutional_use_allowed
        assert [e.stage for e in result.events][:2] == ['release','routing']
    asyncio.run(scenario())


def test_retrieval_is_limited_to_document_versions_when_many_curricula_are_pinned():
    # A release serving many curricula pins one source per prospectus; only the document
    # versions hold retrievable chunks, and a request accepts at most 32 version ids.
    async def scenario():
        base = resources()
        data = base.pin.model_dump(mode='json')
        data['sources'] += [dict(version_id=f'ver-synth-prospectus-{i}', byte_sha256=f'{i:064x}')
                            for i in range(40)]
        release = ports().ReleaseResources(type(base.pin).parse(data), base.catalog, base.registry,
                                           base.retrieval, base.symbolic)
        result = await api().Orchestrator(transport('RAG'),
            releases=ports().SyntheticReleaseProvider(release)).run('A1 policy', ctx())
        assert result.status == 'ready'
        assert release.retrieval.calls[0].document_version_ids == ('ver-synth-handbook-1',)
    asyncio.run(scenario())


def test_default_provider_holds_without_model_or_evidence_calls():
    async def scenario():
        model = transport()
        result = await api().Orchestrator(model).run('A1 policy', ctx())
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
        result = await api().Orchestrator(transport('Hybrid'), releases=provider).run('A1 policy', ctx())
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
            ports().SyntheticReleaseProvider(resources(WaitDocuments(), WaitSymbolic()))).run('A1 policy', ctx())
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
            resources(sym=Broken())), stage_timeout=0.05).run('A1 policy', ctx())
        assert result.status == expected and result.evidence is None and result.route == 'Hybrid'
        assert len(model.calls) == 2  # original routing and style only
        assert 'PRIVATE' not in json.dumps([e.model_dump(mode='json') for e in result.events])
    asyncio.run(scenario())


def test_router_control_never_dispatches_evidence():
    async def scenario():
        release = resources()
        result = await api().Orchestrator(transport(None, control='greeting', operations=[]),
            releases=ports().SyntheticReleaseProvider(release)).run('A1 policy', ctx())
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
        task = asyncio.create_task(pipeline.run('A1 policy', ctx()))
        await asyncio.wait_for(entered.wait(),timeout=1)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert cancelled == {'documents','symbolic'}
    asyncio.run(scenario())


def test_telemetry_has_only_fixed_stage_outcomes_and_evidence_ids():
    async def scenario():
        result = await api().Orchestrator(transport('Hybrid'), releases=
            ports().SyntheticReleaseProvider(resources())).run('A1 policy', ctx())
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
            ports().SyntheticReleaseProvider(resources(sym=Wrong()))).run('A1 policy', ctx())
        assert result.status == 'invalid_output' and result.evidence is None
    asyncio.run(scenario())


@pytest.mark.parametrize('state,status', [('passed','ready'), (None,'unknown')])
def test_telemetry_records_pinned_release_route_and_actual_integration_outcome(state,status):
    async def scenario():
        result = await api().Orchestrator(transport(),releases=
            ports().SyntheticReleaseProvider(resources())).run('A1 policy',ctx(state=state))
        assert result.events[0].release_id == 'release-synth-1'
        assert result.events[1].route == 'Symbolic'
        assert result.events[-1].outcome == status
    asyncio.run(scenario())


def test_valid_underscore_rule_identifier_survives_telemetry():
    async def scenario():
        class Underscore(Symbolic):
            async def execute(self, request, context):
                result = await super().execute(request, context)
                return result.model_copy(update={'rule_ids':('rule-course_a',)})
        result = await api().Orchestrator(transport(),releases=ports().SyntheticReleaseProvider(
            resources(sym=Underscore()))).run('A1 policy',ctx())
        assert result.status == 'ready'
        assert 'rule-course_a' in result.events[2].evidence_ids
    asyncio.run(scenario())


def test_unloggable_rule_identifier_returns_bounded_invalid_output_without_raw_text():
    async def scenario():
        class Unsafe(Symbolic):
            async def execute(self, request, context):
                result = await super().execute(request, context)
                return result.model_copy(update={'rule_ids':('PRIVATE grade 5.00',)})
        result = await api().Orchestrator(transport(),releases=ports().SyntheticReleaseProvider(
            resources(sym=Unsafe()))).run('A1 policy',ctx())
        assert result.status == 'invalid_output' and result.evidence is None
        assert 'PRIVATE' not in json.dumps([e.model_dump(mode='json') for e in result.events])
    asyncio.run(scenario())


def test_maximum_context_plus_new_assertion_has_a_bounded_failure():
    async def scenario():
        base = ctx().model_dump(mode='json')
        base['facts'] = [dict(base['facts'][0],fact_id=f'fact-existing-{n}') for n in range(256)]
        value = proposal(claims=[dict(entity=0,state='passed',mode='asserted',text='A1',start=0,end=2)])
        release = resources()
        result = await api().Orchestrator(FakeTransport(json.dumps(value)),releases=
            ports().SyntheticReleaseProvider(release)).run('A1 policy',RequestContext.parse(base))
        assert result.status == 'invalid_output' and not release.symbolic.calls
        assert result.events[-1].outcome == 'invalid_output'
    asyncio.run(scenario())


@pytest.mark.parametrize('outputs,status', [
    (['timeout'],'timeout'), (['bad','still bad'],'invalid_output'),
    (['connection'],'tool_error')])
def test_router_operational_failures_keep_distinct_status_and_telemetry(outputs,status):
    from backend.bintanong_routing.transport import RuntimeFailure
    async def scenario():
        values = [RuntimeFailure({'timeout':'model_timeout','connection':'model_connection_error'}[v])
                  if v in ('timeout','connection') else v for v in outputs]
        release = resources()
        result = await api().Orchestrator(FakeTransport(*values),releases=
            ports().SyntheticReleaseProvider(release)).run('A1 policy',ctx())
        assert result.status == status and result.events[-1].outcome == status
        assert not release.symbolic.calls and not release.retrieval.calls
    asyncio.run(scenario())
