import asyncio
import importlib
import threading

import pytest

from backend.bintanong_retrieval.types import RetrievalRequest
from backend.bintanong_routing.contracts import RequestContext
from backend.bintanong_symbolic.runtime import CurriculumRuntime
from test_symbolic_authoring import fixture, run as ledger
from test_symbolic_runtime import request
from test_retrieval_engine import Client, Encoder
from backend.bintanong_retrieval.engine import RetrievalEngine


def api():
    return importlib.import_module('backend.bintanong_orchestration.adapters')


def context(session='a', state=None):
    return RequestContext.parse(dict(session_id='sess-'+session, request_id='req-'+session,
        program_id='program-synthetic', curriculum_id='curriculum-synthetic-1',
        facts=[] if state is None else [dict(fact_id='fact-'+session,session_id='sess-'+session,
            program_id='program-synthetic', curriculum_id='curriculum-synthetic-1',
            course_id='course-1', state=state)]))


def test_runtime_exposes_immutable_release_binding_without_private_fields():
    runtime = CurriculumRuntime(ledger(fixture()))
    assert runtime.synthetic is True
    assert runtime.release_id.startswith('release-synthetic-')
    assert runtime.rule_bundle_version
    with pytest.raises(AttributeError):
        runtime.release_id = 'release-other'


def test_existing_retrieval_uncalibrated_status_and_gaps_survive_translation():
    async def scenario():
        client = Client()
        row = client.payload['items'][0]
        row['chunk'].update(chunk_id='a'*64, version_id='ver-synthetic')
        row['version']['version_id'] = 'ver-synthetic'
        row['spans'][0]['version_id'] = 'ver-synthetic'
        adapter = api().RetrievalAdapter(RetrievalEngine(client, Encoder()))
        result = await adapter.retrieve(RetrievalRequest('Fictional policy?', 'release-test'))
        assert result.status == 'uncalibrated'
        assert result.passages and result.passages[0].citations
        assert 'development_calibration_pending' in result.gaps
    asyncio.run(scenario())


@pytest.mark.parametrize('operation', ['check_prerequisite_eligibility',
    'list_missing_prerequisites', 'list_affected_courses'])
def test_real_synthetic_janus_dispatches_each_fixed_operation(operation):
    async def scenario():
        runtime = CurriculumRuntime(ledger(fixture()))
        adapter = api().SymbolicAdapter(runtime)
        result = await adapter.execute(request(predicate=operation), context(state='passed'))
        assert adapter.release_id == runtime.release_id
        assert adapter.rule_bundle_version == runtime.rule_bundle_version
        if operation == 'list_affected_courses':
            assert result.status == 'complete' and result.course_ids == ()
            # course-2 is not a prerequisite of another course in this synthetic bundle.
        else:
            assert result.decision.outcome == 'eligible' and result.decision.synthetic
            assert result.decision.predicate == operation
        assert not hasattr(adapter, 'facts')
    asyncio.run(scenario())


def test_concurrent_students_use_request_local_facts_and_never_a_grade_default():
    async def scenario():
        # Separate workers avoid intentional per-runtime admission rejection.
        adapters = [api().SymbolicAdapter(CurriculumRuntime(ledger(fixture()))) for _ in range(2)]
        a = await adapters[0].execute(request(), context('a', 'failed'))
        b = await adapters[1].execute(request(), context('b'))
        assert a.decision.outcome == 'ineligible'
        assert b.decision.outcome == 'unknown' and b.decision.missing_facts
    asyncio.run(scenario())


def test_wrong_curriculum_and_unregistered_operation_do_not_reach_runtime():
    async def scenario():
        adapter = api().SymbolicAdapter(CurriculumRuntime(ledger(fixture())))
        with pytest.raises(ValueError, match='scope'):
            await adapter.execute(request(curriculum='different'), context())
        with pytest.raises(ValueError, match='operation'):
            await adapter.execute(request(predicate='arbitrary_goal'), context())
    asyncio.run(scenario())


def test_cancelling_wait_retains_worker_admission_until_thread_finishes():
    async def scenario():
        started, finish = threading.Event(), threading.Event()
        class SlowEngine:
            def retrieve(self, req):
                started.set()
                assert finish.wait(3)
                return dict(release_id=req.release_id, status='insufficient_evidence',
                            evidence=[], gaps=['no_complete_relevant_evidence'])
        adapter = api().RetrievalAdapter(SlowEngine())
        req = RetrievalRequest('Fictional?', 'release-test')
        task = asyncio.create_task(adapter.retrieve(req))
        try:
            assert await asyncio.to_thread(started.wait, 2)
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
            with pytest.raises(api().AdapterFailure, match='busy'):
                await adapter.retrieve(req)
        finally:
            finish.set()
        # Async loop shutdown joins the bounded outstanding thread.
    asyncio.run(scenario())


def test_non_synthetic_runtime_is_refused_before_any_execution():
    class RealRuntime:
        synthetic = False
    with pytest.raises(ValueError, match='synthetic'):
        api().SymbolicAdapter(RealRuntime())


def test_course_fact_operations_answer_from_reviewed_facts_within_the_request_scope():
    from test_symbolic_course_facts import ledger as facts_ledger, runtime_request
    async def scenario():
        adapter = api().SymbolicAdapter(CurriculumRuntime(facts_ledger()))
        ctx = context()
        listing = await adapter.execute(runtime_request('list_term_courses', year_level='1', semester='any'), ctx)
        assert listing.status == 'complete' and [c.code for c in listing.courses] == ['SYN 101', 'SYN 102', 'SYN 103']
        one = await adapter.execute(runtime_request('course_facts', course_id='course-syn101'), ctx)
        assert one.courses[0].units == (('units.printed', '3'),)
        other = ctx.model_copy(update={'curriculum_id': 'curriculum-other'})
        with pytest.raises(ValueError, match='scope'):
            await adapter.execute(runtime_request('course_facts', course_id='course-syn101'), other)
    asyncio.run(scenario())
