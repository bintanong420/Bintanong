import copy

import pytest

from test_storage_selected_release_review import selected_fixture
from backend.bintanong_contracts.reviewed_policy_context import context_chunker_version
from backend.bintanong_api.hosted_snapshot import load_document_snapshot, bind_document_policy


class Database:
    def __init__(self):
        source, _, receipt, text = selected_fixture()
        reviewed = receipt['chunks'][0]
        self.calls = []
        self.tables = {
            'knowledge_releases': [dict(release_id='hosted', status='active', release_kind='research',
                research_authorization_ref='research-fictional', embedding_set_id='embedding',
                review_scope_id=receipt['review_scope_id'], expected_chunk_count=1, expected_document_version_count=1)],
            'release_chunks': [dict(chunk_id=reviewed['chunk_id'])],
            'release_document_versions': [dict(version_id=source['version_id'])],
            'selected_release_reviews': [dict(receipt=receipt)],
            'embedding_sets': [dict(embedding_set_id='embedding', dimension=1024)],
            'document_versions': [source],
            'chunks': [dict(chunk_id=reviewed['chunk_id'], content_hash=reviewed['content_hash'],
                type_fields=reviewed['type_fields'], version_id=source['version_id'], byte_sha256=source['byte_sha256'],
                document_id=source['document_id'], edition_id=source['edition_id'], text=text,
                chunk_type='policy', chunker_version=context_chunker_version(reviewed['type_fields']['context_format']),
                source_text='Synthetic visible field', scope=['audience:undergraduate'], section_path=[])],
            'source_spans': reviewed['spans'],
        }

    def select(self, table, *, filters=None, role):
        assert role == 'runtime'
        self.calls.append((table, filters))
        return copy.deepcopy(self.tables[table])


def load(db):
    return load_document_snapshot(db, release_id='hosted', authorization_ref='research-fictional')


def test_snapshot_uses_shared_reviewed_rows_without_downloading_vectors_or_reading_local_packages():
    db = Database(); snapshot = load(db)
    assert snapshot['manifest']['embedding_set_id'] == 'embedding'
    assert len(snapshot['chunks']) == 1 and len(snapshot['versions']) == 1
    assert snapshot['chunks'][0]['spans'][0]['page'] == 1
    assert not any(table == 'chunk_embeddings' for table, _ in db.calls)
    assert not any(table in ('selected_release_reviews', 'source_partial_reviews') for table, _ in db.calls)


@pytest.mark.parametrize('change', ['hash', 'span', 'scope', 'membership', 'retired', 'version'])
def test_hosted_snapshot_refuses_changed_content_scope_spans_or_release(change):
    db = Database()
    if change == 'hash': db.tables['chunks'][0]['content_hash'] = '0' * 64
    if change == 'span': db.tables['source_spans'][0]['text'] = 'Changed'
    if change == 'scope': db.tables['chunks'][0]['scope'] = ['audience:graduate']
    if change == 'membership': db.tables['release_chunks'] = []
    if change == 'retired': db.tables['knowledge_releases'][0]['status'] = 'retired'
    if change == 'version': db.tables['document_versions'][0]['byte_sha256'] = '0' * 64
    with pytest.raises(ValueError): load(db)


def test_missing_source_claim_index_is_explicit_not_reconstructed_from_unreviewed_guesses():
    snapshot = load(Database())
    with pytest.raises(ValueError, match='source_claim_index_unavailable'):
        bind_document_policy(snapshot, None)
    assert 'catalogue' not in snapshot and 'register' not in snapshot


def test_recovered_prior_assignments_and_reviews_bind_to_the_shared_verified_snapshot():
    snapshot = load(Database()); chunk = snapshot['chunks'][0]
    policy = dict(assignments=[dict(reading_id=chunk['type_fields']['reading_id'], subject_id='synthetic', basis_ref='synthetic-owner-record')], reviews=[])
    bound = bind_document_policy(snapshot, policy)
    assert bound['catalogue']['assignments'][0]['subject_id'] == 'synthetic'
    assert bound['register']['reviews'] == []
    assert 'catalogue' not in snapshot
