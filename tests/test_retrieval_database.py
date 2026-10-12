import unittest

from backend.bintanong_storage.release import ReleaseManager
from tests.storage_database import StorageDatabase, DatabaseStorageClient, FIXTURE


IDENTITY = dict(model_id='synthetic-model', model_revision='2'*64, dimension=1024,
                normalization='l2', prompt_fingerprint='3'*64,
                preprocessing_fingerprint='4'*64, tokenizer_fingerprint='5'*64)


class RetrievalDatabaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = StorageDatabase()
        cls.addClassCleanup(cls.db.close)
        cls.db.execute(FIXTURE + """
            update public.chunks set scope=array['program:TEST'],
              type_fields='{"entity_hints":["TEST1"],"required_neighbor_chunk_ids":[]}' where chunk_id=repeat('a',64);
            commit;
        """)
        cls.client = DatabaseStorageClient(cls.db)
        cls.manager = ReleaseManager(cls.client)
        cls.manager.create_release('release-both', 'both', 'Synthetic', 'set-test',
                                   ['a'*64,'b'*64], ['ver-test1','ver-test2'])
        cls.manager.activate_release('release-both')

    def search(self, **overrides):
        params = dict(p_release_id='release-both', p_config=IDENTITY,
                      query_embedding=[1.0]+[0.0]*1023, p_top_k=3, p_min_similarity=0.0,
                      p_scope=[], p_entity_hints=[], p_version_ids=[])
        params.update(overrides)
        return self.client.rpc('retrieve_context', params)

    def test_snapshot_rank_sources_and_exact_filters(self):
        result = self.search()
        self.assertEqual(result['status'], 'ok')
        self.assertEqual([x['chunk']['chunk_id'] for x in result['items']], ['a'*64, 'b'*64])
        first = result['items'][0]
        self.assertEqual(first['spans'][0]['version_id'], first['chunk']['version_id'])
        self.assertEqual(first['version']['byte_sha256'], first['chunk']['byte_sha256'])
        self.assertEqual(first['spans'][0]['page'], 1)
        self.assertEqual(self.search(p_scope=['program:OTHER'])['items'][0]['chunk']['chunk_id'], 'b'*64)
        self.assertEqual(self.search(p_entity_hints=['UNKNOWN'])['items'], [])
        self.assertEqual(len(self.search(p_entity_hints=['TEST1'])['items']), 1)
        self.assertEqual(self.search(p_version_ids=['not-active'])['items'], [])

    def test_configuration_mismatch_and_invalid_parameters(self):
        bad = dict(IDENTITY, prompt_fingerprint='0'*64)
        self.assertEqual(self.search(p_config=bad)['status'], 'configuration_mismatch')
        for params in ({'p_top_k':100}, {'p_min_similarity':2}, {'query_embedding':[0.0]*1024}):
            with self.assertRaises(Exception):
                self.search(**params)

    def test_stale_and_draft_pins_are_closed_under_both_runtime_roles(self):
        self.assertEqual(self.search(p_release_id='release-test1')['status'], 'release_changed')
        self.manager.activate_release('release-test2')
        try:
            self.assertEqual(self.search()['status'], 'release_changed')
            self.assertEqual(self.search()['items'], [])
            sql = """begin; set local role authenticated;
                select public.retrieve_context('release-both', '{}'::jsonb,
                  ('[' || '1,' || repeat('0,',1022) || '0]')::extensions.vector);
                commit;"""
            self.assertEqual(self.db.json(sql)['status'], 'release_changed')
        finally:
            self.manager.rollback_release('release-both')

    def test_function_is_stable_invoker_with_explicit_runtime_privileges(self):
        attrs = self.db.json("""select jsonb_build_object('definer',prosecdef,'volatility',provolatile,
            'anon',has_function_privilege('anon',oid,'execute'),
            'authenticated',has_function_privilege('authenticated',oid,'execute'))
            from pg_proc where proname='retrieve_context';""")
        self.assertEqual(attrs, dict(definer=False, volatility='s', anon=True, authenticated=True))


if __name__ == '__main__':
    unittest.main()
