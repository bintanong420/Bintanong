import json
from pathlib import Path
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

    def test_synthetic_development_rankings_and_citation_references(self):
        from evaluation.retrieval import calibrate_threshold
        cases=json.loads(Path('evaluation/retrieval-dev-synthetic.json').read_text(encoding='utf-8'))
        observations={}
        for case in cases:
            vector=[0.0]*1024
            vector[case['vector_axis']]=1.0
            snapshot=self.search(query_embedding=vector,p_scope=case['scope'],
                p_entity_hints=case['entity_hints'],p_version_ids=case['document_version_ids'],p_min_similarity=0.0)
            self.assertEqual(snapshot['status'],'ok')
            observations[case['case_id']]=[dict(chunk_id=r['chunk']['chunk_id'],similarity=r['similarity']) for r in snapshot['items']]
            for row in snapshot['items']:
                self.assertEqual(row['spans'][0]['version_id'],row['version']['version_id'])
                self.assertTrue(row['spans'][0]['locator'])
        reports={str(k):calibrate_threshold(cases,observations,k) for k in (3,5,8)}
        for report in reports.values():
            self.assertEqual(report['selected_report']['overall']['recall_at_k'],1.0)
            self.assertEqual(report['selected_report']['unsupported_detection_rate'],1.0)
            self.assertFalse(report['selected_report']['institutional_gate_eligible'])
        # Exercise the complete runtime pipeline with an explicitly synthetic encoder.
        from dataclasses import replace
        from backend.bintanong_embedding.adapter import EmbeddingConfig
        from backend.bintanong_retrieval.engine import RetrievalEngine
        from backend.bintanong_retrieval.types import RetrievalRequest, RetrievalSettings
        class SyntheticEncoder:
            config=replace(EmbeddingConfig(),**IDENTITY)
            def encode(self, query):
                axis=next(case['vector_axis'] for case in cases if case['query']==query)
                return tuple(1.0 if i==axis else 0.0 for i in range(1024))
            def count_context_tokens(self,text):
                return len(text)  # Explicit fixture counter, not a measured model tokenizer.
        for k in (3,5,8):
            engine=RetrievalEngine(self.client,SyntheticEncoder(),RetrievalSettings(top_k=k,context_budget=4096,
                min_similarity=reports[str(k)]['threshold']))
            for case in cases:
                result=engine.retrieve(RetrievalRequest(case['query'],'release-both',tuple(case['scope']),
                    tuple(case['entity_hints']),tuple(case['document_version_ids'])))
                self.assertEqual(result['status'],case['expected_status'],case['case_id'])
                self.assertEqual({row['chunk_id'] for row in result['evidence']},set(case['gold_chunk_ids']))
        (self.db.evidence/'retrieval-observations.json').write_text(json.dumps(observations,indent=2),encoding='utf-8')
        (self.db.evidence/'retrieval-evaluation.json').write_text(json.dumps(reports,indent=2),encoding='utf-8')
        print('Synthetic development evidence:',self.db.evidence)


if __name__ == '__main__':
    unittest.main()
