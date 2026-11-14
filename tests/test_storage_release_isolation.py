import concurrent.futures
import unittest
from backend.bintanong_storage.client import PermissionDeniedError, StorageError
from backend.bintanong_storage.release import ReleaseManager
from tests.storage_database import StorageDatabase, DatabaseStorageClient, FIXTURE


class TestStorageReleaseIsolation(unittest.TestCase):
    def setUp(self):
        self.db = StorageDatabase()
        self.addCleanup(self.db.close)
        self.db.execute(FIXTURE + 'commit;')
        self.client = DatabaseStorageClient(self.db)
        self.manager = ReleaseManager(self.client)

    def test_release_isolation_and_atomic_transition(self):
        self.assertEqual(self.client.select('chunks'), [])
        for release_id, chunk_id, rollback in [('release-test1', 'a'*64, False),
                                               ('release-test2', 'b'*64, False),
                                               ('release-test1', 'a'*64, True)]:
            operation = self.manager.rollback_release if rollback else self.manager.activate_release
            operation(release_id)
            self.assertEqual([c['chunk_id'] for c in self.client.select('chunks')], [chunk_id])
            self.assertEqual(self.manager.get_active_release()['release_id'], release_id)
            self.assertEqual(len(self.manager.list_releases(role='runtime')), 1)

    def test_draft_creation_is_atomic_and_records_expected_counts(self):
        for chunk_ids, document_ids in [(['missing'], ['ver-test1']), ([], ['ver-test1']),
                                       (['a'*64], []), (['a'*64, 'a'*64], ['ver-test1'])]:
            with self.subTest(chunks=chunk_ids), self.assertRaises(StorageError):
                self.manager.create_release('new-release', 'v3', 'Synthetic', 'set-test', chunk_ids, document_ids)
            self.assertEqual(self.client.select('knowledge_releases', filters={'release_id': 'eq.new-release'}, role='admin'), [])
        self.manager.create_release('new-release', 'v3', 'Synthetic', 'set-test', ['a'*64], ['ver-test1'], ['rule-test'])
        row = self.client.select('knowledge_releases', filters={'release_id': 'eq.new-release'}, role='admin')[0]
        self.assertEqual((row['expected_chunk_count'], row['expected_document_version_count'], row['expected_rule_count']), (1, 1, 1))
        self.manager.activate_release('new-release')
        self.assertEqual(self.manager.get_active_release()['release_id'], 'new-release')

    def test_runtime_cannot_execute_any_admin_rpc(self):
        calls = [
            ('activate_knowledge_release', {'p_release_id': 'release-test1'}),
            ('rollback_knowledge_release', {'p_target_release_id': 'release-test1'}),
            ('create_knowledge_release', {'p_release_id': 'x', 'p_release_version': 'x', 'p_description': 'x',
             'p_embedding_set_id': 'set-test', 'p_chunk_ids': ['a'*64], 'p_document_version_ids': ['ver-test1'], 'p_rule_ids': []}),
            ('load_chunk_batch', {'p_chunks': [], 'p_spans': []}),
            ('load_embedding_set', {'p_record': {}}),
            ('load_embedding_batch', {'p_records': [], 'p_embedding_set_id': 'set-test'}),
            ('load_knowledge_batch', {'p_embedding_set': {}, 'p_chunks': [], 'p_spans': [], 'p_embeddings': []}),
        ]
        for function, params in calls:
            with self.subTest(function=function), self.assertRaises(PermissionDeniedError):
                self.client.rpc(function, params, role='runtime')

    def test_concurrent_activation_keeps_one_active_release_and_pointer(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as workers:
            list(workers.map(self.manager.activate_release, ['release-test1', 'release-test2']))
        active = self.manager.get_active_release()['release_id']
        states = self.manager.list_releases()
        self.assertEqual([r['release_id'] for r in states if r['status'] == 'active'], [active])
        self.assertEqual(sum(r['status'] == 'superseded' for r in states), 1)
        self.assertEqual(len(self.client.select('chunks')), 1)


if __name__ == '__main__':
    unittest.main()
