"""Evaluation sees what kNN ranked; the answer path and its evidence stay exactly as they were."""
import asyncio

from backend.bintanong_orchestration.adapters import _BoundedWorker
from backend.bintanong_retrieval.observation import observe_retrievals
from backend.bintanong_retrieval.types import RetrievalRequest
from tests.test_retrieval_claim_filter import fixture

REQUEST = RetrievalRequest('synthetic printed amount', 'release-test')
INTENT = dict(subject_id='fees', requested_claims=('printed amount',))


def ids(rows):
    return [row['chunk']['chunk_id'] for row in rows]


class SpyStorage:
    def __init__(self, storage):
        self.storage, self.params = storage, None

    def __getattr__(self, name):
        return getattr(self.storage, name)

    def rpc(self, name, params, *, role):
        self.params = params
        return self.storage.rpc(name, params, role=role)


def test_observer_records_ranked_candidates_and_what_was_sent_on():
    engine, _ = fixture()
    with observe_retrievals() as seen:
        engine.retrieve(REQUEST, **INTENT)
    assert seen[0]['query'] == REQUEST.query and seen[0]['subject_id'] == 'fees'
    assert seen[0]['requested_claims'] == ['printed amount']
    assert sorted(ids(seen[0]['candidates'])) == ['a', 'b']
    assert seen[0]['emitted_chunk_ids'] == ['a', 'b']


def test_observer_still_sees_a_search_the_policy_then_refuses():
    engine, _ = fixture()
    with observe_retrievals() as seen:
        out = engine.retrieve(REQUEST)
    assert out['status'] == 'needs_subject'
    assert sorted(ids(seen[0]['candidates'])) == ['a', 'b', 'other'] and seen[0]['emitted_chunk_ids'] == []


def test_each_search_in_a_turn_is_recorded_separately():
    engine, _ = fixture()
    with observe_retrievals() as seen:
        engine.retrieve(REQUEST, **INTENT)
        engine.retrieve(RetrievalRequest('second words', 'release-test'), **INTENT)
    assert [entry['query'] for entry in seen] == [REQUEST.query, 'second words']


def test_observation_crosses_the_adapter_worker_thread():
    engine, _ = fixture()

    async def scenario():
        with observe_retrievals() as seen:
            await _BoundedWorker().run(lambda: engine.retrieve(REQUEST, **INTENT))
        return seen
    assert len(asyncio.run(scenario())) == 1


def test_observation_stops_with_its_context():
    engine, _ = fixture()
    with observe_retrievals() as seen:
        pass
    engine.retrieve(REQUEST, **INTENT)
    assert seen == []


def test_observing_does_not_change_the_response():
    engine, _ = fixture()
    plain = engine.retrieve(REQUEST, **INTENT)
    with observe_retrievals():
        assert engine.retrieve(REQUEST, **INTENT) == plain


def test_all_chunk_search_drops_only_the_topic_filter():
    engine, _ = fixture()
    engine.client = spy = SpyStorage(engine.client)
    request = RetrievalRequest('q', 'release-test', scope=('audience:undergraduate',), document_version_ids=('version',))
    engine.search_all_chunks(request)
    assert 'p_chunk_ids' not in spy.params and spy.params['p_scope'] == ['audience:undergraduate']
    assert spy.params['p_top_k'] == 3 and spy.params['p_min_similarity'] == .25 and spy.params['p_version_ids'] == ['version']


def test_all_chunk_search_reaches_chunks_outside_the_narrowed_topic():
    engine, _ = fixture()
    assert sorted(ids(engine.search_all_chunks(REQUEST))) == ['a', 'b', 'other']


def test_all_chunk_search_accepts_a_wider_pool_for_key_drafting():
    engine, _ = fixture()
    engine.client = spy = SpyStorage(engine.client)
    engine.search_all_chunks(REQUEST, top_k=8)
    assert spy.params['p_top_k'] == 8


def test_all_chunk_search_is_not_recorded_as_a_system_search():
    engine, _ = fixture()
    with observe_retrievals() as seen:
        engine.search_all_chunks(REQUEST)
    assert seen == []


def test_all_chunk_search_cannot_change_a_later_answer():
    engine, _ = fixture()
    before = engine.retrieve(REQUEST, **INTENT)
    engine.search_all_chunks(REQUEST)
    assert engine.retrieve(REQUEST, **INTENT) == before


def test_all_chunk_search_reports_a_failed_read():
    engine, _ = fixture()
    engine.client.rpc = lambda *args, **kwargs: dict(status='release_changed')
    try:
        engine.search_all_chunks(REQUEST)
    except ValueError as failure:
        assert str(failure) == 'release_changed'
    else:
        raise AssertionError('a failed read must not look like an empty result')
