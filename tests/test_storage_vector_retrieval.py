import unittest
from backend.bintanong_storage.release import ReleaseManager
from backend.bintanong_storage.retrieval import KnowledgeRetriever
from tests.storage_database import StorageDatabase, DatabaseStorageClient, FIXTURE


class TestStorageVectorRetrieval(unittest.TestCase):
    def setUp(self):
        self.db = StorageDatabase()
        self.addCleanup(self.db.close)
        self.db.execute(FIXTURE + 'commit;')
        self.client = DatabaseStorageClient(self.db)
        self.manager = ReleaseManager(self.client)
        self.retriever = KnowledgeRetriever(self.client)
        self.query = [1.0] + [0.0]*1023

    def test_exact_cosine_search_ranking_and_release_isolation(self):
        self.assertEqual(self.retriever.search(self.query), [])
        self.manager.create_release('both', 'both', 'Synthetic', 'set-test', ['a'*64, 'b'*64], ['ver-test1', 'ver-test2'])
        self.manager.activate_release('both')
        rows = self.retriever.search(self.query)
        self.assertEqual([r.chunk_id for r in rows], ['a'*64, 'b'*64])
        self.assertAlmostEqual(rows[0].similarity, 1.0, places=6)
        self.assertAlmostEqual(rows[1].similarity, 0.0, places=6)
        self.assertEqual(rows[0].source_text, self.client.select('chunks', filters={'chunk_id': 'eq.'+'a'*64})[0]['source_text'])
        self.manager.activate_release('release-test2')
        self.assertEqual([r.chunk_id for r in self.retriever.search(self.query)], ['b'*64])
        self.manager.rollback_release('both')
        self.assertEqual(len(self.retriever.search(self.query)), 2)

    def test_threshold_count_and_dimension(self):
        self.manager.create_release('both', 'both', 'Synthetic', 'set-test', ['a'*64, 'b'*64], ['ver-test1', 'ver-test2'])
        self.manager.activate_release('both')
        self.assertEqual([r.chunk_id for r in self.retriever.search(self.query, match_threshold=0.5)], ['a'*64])
        self.assertEqual(len(self.retriever.search(self.query, match_count=1)), 1)
        with self.assertRaises(ValueError):
            self.retriever.search([1.0])


if __name__ == '__main__':
    unittest.main()
