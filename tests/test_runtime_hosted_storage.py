"""Hosted research-release reads under the local pin's release id (fake client, no network)."""
import pytest

from backend.bintanong_runtime.hosted_storage import HostedReleaseStorage

PIN, HOSTED, REF = 'release-pin', 'release-hosted', 'research-owner-20261021'
CHUNKS = [dict(chunk_id='a' * 64, content_hash='1' * 64), dict(chunk_id='b' * 64, content_hash='2' * 64)]


class FakeClient:
    def __init__(self, release=None, chunks=CHUNKS):
        self.release = dict(release_id=HOSTED, status='active', release_kind='research',
                            research_authorization_ref=REF, embedding_set_id='set-1') | (release or {})
        self.chunks, self.calls = [dict(c) for c in chunks], []

    def select(self, table, columns='*', filters=None, role='runtime'):
        self.calls.append(('select', table, filters, role))
        if table == 'knowledge_releases':
            return [self.release] if filters in (None, {'release_id': 'eq.' + self.release['release_id']}) else []
        if table == 'chunks':
            return self.chunks
        if table == 'embedding_sets':
            return [dict(embedding_set_id='set-1')]
        raise AssertionError(table)

    def rpc(self, name, params, role='runtime'):
        self.calls.append(('rpc', name, params, role))
        return dict(status='ok', release_id=params['p_release_id'], items=[])


def storage(client=None, chunks=CHUNKS):
    return HostedReleaseStorage(client or FakeClient(), pin_release_id=PIN, hosted_release_id=HOSTED,
                                authorization_ref=REF, chunks=chunks)


def test_pin_release_lookups_and_search_go_to_the_hosted_release():
    client = FakeClient(); s = storage(client)
    assert s.select('knowledge_releases', filters={'release_id': 'eq.' + PIN}, role='runtime')[0]['embedding_set_id'] == 'set-1'
    assert ('select', 'knowledge_releases', {'release_id': 'eq.' + HOSTED}, 'runtime') in client.calls
    response = s.rpc('retrieve_context', dict(p_release_id=PIN, p_top_k=3), role='runtime')
    assert client.calls[-1][2]['p_release_id'] == HOSTED and response['release_id'] == PIN


def test_other_release_ids_are_not_translated():
    client = FakeClient(); s = storage(client)
    assert s.select('knowledge_releases', filters={'release_id': 'eq.other'}, role='runtime') == []
    assert s.rpc('retrieve_context', dict(p_release_id='other'), role='runtime')['status'] == 'release_changed'
    assert not any(c[0] == 'rpc' for c in client.calls)


def test_only_runtime_reads_are_allowed():
    s = storage()
    with pytest.raises(ValueError, match='runtime_reads_only'):
        s.select('chunks', filters=None, role='admin')
    with pytest.raises(ValueError, match='runtime_reads_only'):
        s.rpc('retrieve_context', dict(p_release_id=PIN), role='admin')


@pytest.mark.parametrize('change', [dict(status='superseded'), dict(release_kind='institutional'),
                                    dict(research_authorization_ref='research-owner-20261022')])
def test_refuses_a_hosted_release_that_is_not_the_active_owner_research_release(change):
    with pytest.raises(ValueError, match='hosted_release_not_active_research'):
        storage(FakeClient(release=change))


def test_refuses_when_hosted_chunks_differ_from_the_reviewed_package():
    changed = [CHUNKS[0], dict(CHUNKS[1], content_hash='3' * 64)]
    for hosted in (changed, CHUNKS[:1], CHUNKS + [dict(chunk_id='c' * 64, content_hash='4' * 64)]):
        with pytest.raises(ValueError, match='hosted_release_differs'):
            storage(FakeClient(chunks=hosted))


def test_research_builder_uses_hosted_storage_when_given(monkeypatch):
    from backend.bintanong_runtime import research
    seen = {}
    monkeypatch.setattr(research, 'RetrievalEngine', lambda storage, *a, **k: seen.setdefault('storage', storage))
    monkeypatch.setattr(research, 'HostedReleaseStorage', lambda client, **k: ('hosted', client, k))
    assert research.retrieval_storage('pin', dict(manifest={}, chunks=[], versions={}, vectors={}),
        hosted=dict(client='C', release_id='H'), authorization_ref=REF) == (
        'hosted', 'C', dict(pin_release_id='pin', hosted_release_id='H', authorization_ref=REF, chunks=[]))
