"""Read-only package stand-in mirrors retrieve_context semantics without a database."""
import math

import pytest

from backend.bintanong_runtime.package_storage import PackageStorage

SET_ID = 'set-synthetic'
MANIFEST = dict(embedding_set_id=SET_ID, model_id='m', model_revision='r', dimension=2,
                normalization='l2', prompt_fingerprint='p', preprocessing_fingerprint='q',
                tokenizer_fingerprint='t')


def chunk(cid, scope=('audience:undergraduate',), neighbors=()):
    return dict(chunk_id=cid, version_id='ver-' + cid, scope=list(scope), text='Fictional ' + cid,
                type_fields=dict(required_neighbor_chunk_ids=list(neighbors)),
                spans=[dict(text='Fictional ' + cid, page=1)])


def unit(angle):
    return [math.cos(angle), math.sin(angle)]


def store(*, same_version=True, **extra):
    chunks = [chunk('a', neighbors=('c',)), chunk('b'), chunk('c'), chunk('z', scope=('audience:graduate',))]
    if same_version:
        chunks[2]['version_id'] = 'ver-a'
    vectors = {'a': unit(0.1), 'b': unit(0.5), 'c': unit(1.5), 'z': unit(0.0)}
    versions = {'ver-' + c['chunk_id']: dict(version_id='ver-' + c['chunk_id']) for c in chunks}
    return PackageStorage(release_id='release-research', manifest=MANIFEST, chunks=chunks,
                          versions=versions, vectors=vectors, **extra)


def search(storage, **overrides):
    params = dict(p_release_id='release-research', p_config={}, query_embedding=unit(0.0),
                  p_top_k=2, p_min_similarity=0.5, p_scope=['audience:undergraduate'],
                  p_entity_hints=[], p_version_ids=[]) | overrides
    return storage.rpc('retrieve_context', params, role='runtime')


def test_release_and_embedding_set_lookups_answer_only_for_the_pinned_package():
    s = store()
    assert s.select('knowledge_releases', filters={'release_id': 'eq.release-research'},
                    role='runtime') == [dict(embedding_set_id=SET_ID)]
    assert s.select('knowledge_releases', filters={'release_id': 'eq.other'}, role='runtime') == []
    sets = s.select('embedding_sets', filters={'embedding_set_id': 'eq.' + SET_ID}, role='runtime')
    assert sets == [{k: v for k, v in MANIFEST.items() if k != 'embedding_set_id'}]


def test_search_ranks_by_cosine_applies_threshold_scope_top_k_and_neighbors():
    raw = search(store())
    assert raw['status'] == 'ok' and raw['release_id'] == 'release-research'
    assert raw['embedding_set_id'] == SET_ID
    # z is closest but outside the requested scope; c is below the threshold.
    assert [i['chunk']['chunk_id'] for i in raw['items']] == ['a', 'b']
    first = raw['items'][0]
    assert first['similarity'] == pytest.approx(math.cos(0.1))
    assert [n['chunk']['chunk_id'] for n in first['neighbors']] == ['c']
    assert first['spans'][0]['chunk_id'] == 'a' and first['version'] == dict(version_id='ver-a')
    assert 'spans' not in first['chunk']


def test_returned_rows_cannot_mutate_the_package():
    s = store()
    search(s)['items'][0]['chunk']['text'] = 'changed'
    assert search(s)['items'][0]['chunk']['text'] == 'Fictional a'


def test_chunk_filter_applies_before_ranking_and_keeps_only_eligible_neighbors():
    s = store(same_version=True)
    assert search(s, p_chunk_ids=[]) == search(s)
    assert [r['chunk']['chunk_id'] for r in search(s, p_chunk_ids=['b'])['items']] == ['b']
    assert search(s, p_chunk_ids=['z'])['items'] == []  # Scope still applies.
    assert search(s, p_chunk_ids=['c'])['items'] == []  # Threshold still applies.
    assert search(s, p_chunk_ids=['missing'])['items'] == []
    assert search(s, p_chunk_ids=['a'])['items'][0]['neighbors'] == []
    assert [n['chunk']['chunk_id'] for n in
            search(s, p_chunk_ids=['a', 'c'])['items'][0]['neighbors']] == ['c']


def test_required_context_expands_transitively_through_cycles_below_the_score_threshold():
    chunks = [chunk('a', neighbors=('b',)), chunk('b', neighbors=('c',)), chunk('c', neighbors=('a',))]
    for row in chunks:
        row['version_id'] = 'ver-group'
    s = PackageStorage(release_id='release-research', manifest=MANIFEST, chunks=chunks,
        versions={'ver-group':dict(version_id='ver-group')},
        vectors={'a':unit(0.0), 'b':unit(1.5), 'c':unit(2.0)})
    result = search(s, p_top_k=3, p_chunk_ids=['a', 'b', 'c'])
    assert [r['chunk']['chunk_id'] for r in result['items']] == ['a']
    assert [r['chunk']['chunk_id'] for r in result['items'][0]['neighbors']] == ['b', 'c']


def test_context_closure_cannot_cross_source_versions():
    result = search(store(same_version=False))
    assert result['items'][0]['neighbors'] == []


def test_version_filter_limits_ranked_roots_before_context_expansion():
    result = search(store(same_version=False), p_version_ids=['ver-b'])
    assert [row['chunk']['chunk_id'] for row in result['items']] == ['b']


def test_context_closure_still_enforces_audience_without_a_chunk_filter():
    chunks = [chunk('a', neighbors=('z',)), chunk('z', scope=('audience:graduate',))]
    for row in chunks:
        row['version_id'] = 'ver-group'
    s = PackageStorage(release_id='release-research', manifest=MANIFEST, chunks=chunks,
        versions={'ver-group':dict(version_id='ver-group')}, vectors={'a':unit(0), 'z':unit(0)})
    assert search(s)['items'][0]['neighbors'] == []


@pytest.mark.parametrize('value', [None, {}, 'a', [1], [''], [' '], ['\t'], ['\n'], ['a'*257], ['a']*129])
def test_chunk_filter_rejects_invalid_lists(value):
    with pytest.raises(ValueError, match='retrieval filters'):
        search(store(), p_chunk_ids=value)


@pytest.mark.parametrize('count', [33, 128])
def test_chunk_filter_supports_complete_topics_larger_than_32_chunks(count):
    chunk_ids = ['b'] + ['not-a-member-'+str(i) for i in range(count-1)]
    assert [r['chunk']['chunk_id'] for r in search(store(), p_chunk_ids=chunk_ids)['items']] == ['b']


@pytest.mark.parametrize('call', [
    lambda s: s.select('knowledge_releases', filters={'release_id': 'eq.release-research'}, role='admin'),
    lambda s: s.rpc('retrieve_context', {}, role='admin'),
    lambda s: s.rpc('activate_release', {}, role='runtime'),
    lambda s: s.select('chunks', filters={}, role='runtime')])
def test_only_runtime_reads_of_known_operations_are_served(call):
    with pytest.raises(ValueError):
        call(store())


def test_other_release_search_is_not_served():
    assert search(store(), p_release_id='other')['status'] == 'release_changed'


def test_package_rejects_missing_vectors_or_versions():
    with pytest.raises(ValueError):
        PackageStorage(release_id='r', manifest=MANIFEST, chunks=[chunk('a')], versions={}, vectors={'a': unit(0)})
    with pytest.raises(ValueError):
        PackageStorage(release_id='r', manifest=MANIFEST, chunks=[chunk('a')],
                       versions={'ver-a': {}}, vectors={})
