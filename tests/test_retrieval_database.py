import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import time
import unittest

from backend.bintanong_storage.release import ReleaseManager
from tests.storage_database import StorageDatabase, DatabaseStorageClient, FIXTURE
from backend.bintanong_contracts.source import compute_content_hash


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

    def test_chunk_filter_limits_ranking_without_changing_omitted_filter(self):
        for role in ('anon', 'authenticated'):
            with self.subTest(role=role):
                client = DatabaseStorageClient(self.db, runtime_role=role)
                original = self.client
                self.client = client
                try:
                    baseline = self.search()
                    self.assertEqual(self.search(p_chunk_ids=[]), baseline)
                    result = self.search(p_chunk_ids=['b'*64])
                    self.assertEqual([r['chunk']['chunk_id'] for r in result['items']], ['b'*64])
                    self.assertEqual(self.search(p_chunk_ids=['not-in-release'])['items'], [])
                    self.assertEqual(self.search(p_chunk_ids=['a'*64], p_scope=['program:OTHER'])['items'], [])
                    self.assertEqual(self.search(p_chunk_ids=['a'*64], p_version_ids=['ver-test2'])['items'], [])
                    self.assertEqual(self.search(p_chunk_ids=['b'*64], p_min_similarity=.25)['items'], [])
                    self.assertEqual(self.search(p_chunk_ids=['b'*64],
                        p_release_id='release-test1')['status'], 'release_changed')
                finally:
                    self.client = original

    def test_chunk_filter_rejects_malformed_or_oversized_lists(self):
        from backend.bintanong_storage.client import StorageError
        for value in (None, {}, 'a', [1], [''], [' '], ['\t'], ['\n'], ['a'*257], ['a']*129):
            with self.subTest(value=value), self.assertRaisesRegex(StorageError, 'retrieval filters'):
                self.search(p_chunk_ids=value)

    def test_chunk_filter_supports_complete_topics_larger_than_32_chunks(self):
        for count in (33, 128):
            chunk_ids = ['a'*64] + ['not-a-member-'+str(i) for i in range(count-1)]
            with self.subTest(count=count):
                result = self.search(p_chunk_ids=chunk_ids)
                self.assertEqual([r['chunk']['chunk_id'] for r in result['items']], ['a'*64])
        from backend.bintanong_storage.client import StorageError
        for name in ('p_scope', 'p_entity_hints', 'p_version_ids'):
            with self.subTest(filter=name), self.assertRaisesRegex(StorageError, 'retrieval filters'):
                self.search(**{name:['a']*33})

    def test_topic_filter_precedes_top_k_and_retains_below_floor_neighbor(self):
        import math
        from tests.storage_database import sql_literal
        db = StorageDatabase()
        self.addCleanup(db.close)
        db.execute(FIXTURE + """
            update public.chunks set type_fields=jsonb_build_object(
                'required_neighbor_chunk_ids', jsonb_build_array(repeat('c',64))) where chunk_id=repeat('a',64);
            insert into public.chunks select (jsonb_populate_record(null::public.chunks,
                to_jsonb(c) || jsonb_build_object('chunk_id', repeat('c',64), 'type_fields', '{}'::jsonb))).*
                from public.chunks c where c.chunk_id=repeat('a',64);
            insert into public.chunks select (jsonb_populate_record(null::public.chunks,
                to_jsonb(c) || jsonb_build_object('chunk_id', repeat(k,64)))).*
                from public.chunks c cross join (values ('d'),('e')) ids(k) where c.chunk_id=repeat('b',64);
            insert into public.source_spans(span_id,chunk_id,version_id,byte_sha256,text,page,locator)
                select gen_random_uuid(),c.chunk_id,c.version_id,c.byte_sha256,c.text,1,
                    '{"kind":"section","section_path":["Synthetic"]}'::jsonb
                from public.chunks c where c.chunk_id in (repeat('c',64),repeat('d',64),repeat('e',64));
            insert into public.chunk_embeddings(chunk_id,embedding_set_id,chunk_content_hash,embedding)
                select c.chunk_id,'set-test',c.content_hash,
                    ('[' || '1,' || repeat('0,',1022) || '0]')::extensions.vector
                from public.chunks c where c.chunk_id in (repeat('c',64),repeat('d',64),repeat('e',64));
            update public.chunk_embeddings set embedding=
                ('[' || '1,' || repeat('0,',1022) || '0]')::extensions.vector;
            update public.chunk_embeddings set embedding=
                ('[' || '0,1,' || repeat('0,',1021) || '0]')::extensions.vector where chunk_id=repeat('c',64);
            update public.embedding_sets set total_chunks=5 where embedding_set_id='set-test';
            commit;
        """)
        vector = [.4, math.sqrt(.84)] + [0.0]*1022
        db.execute('update public.chunk_embeddings set embedding='+sql_literal(json.dumps(vector))+
                   "::extensions.vector where chunk_id=repeat('a',64);")
        manager = ReleaseManager(DatabaseStorageClient(db))
        manager.create_release('release-topic', 'topic', 'Synthetic', 'set-test',
            [c*64 for c in 'abcde'], ['ver-test1', 'ver-test2'])
        manager.activate_release('release-topic')
        params = dict(p_release_id='release-topic', p_config=IDENTITY,
            query_embedding=[1.0]+[0.0]*1023, p_top_k=3, p_min_similarity=.25)
        for role in ('anon', 'authenticated'):
            client = DatabaseStorageClient(db, runtime_role=role)
            baseline = client.rpc('retrieve_context', params)
            self.assertEqual([r['chunk']['chunk_id'] for r in baseline['items']], [c*64 for c in 'bde'])
            result = client.rpc('retrieve_context', params | {'p_chunk_ids':['a'*64, 'c'*64]})
            self.assertEqual([r['chunk']['chunk_id'] for r in result['items']], ['a'*64])
            self.assertEqual([r['chunk']['chunk_id'] for r in result['items'][0]['neighbors']], ['c'*64])

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

    def test_statement_snapshot_remains_consistent_during_publication(self):
        from tests.storage_database import sql_literal
        vector=sql_literal(json.dumps([1.0]+[0.0]*1023))+'::extensions.vector'
        sql=f"""begin; set local role anon;
            with delay as materialized (select pg_sleep(2))
            select public.retrieve_context('release-both',{sql_literal(json.dumps(IDENTITY))}::jsonb,
                {vector},3,0.0) from delay; commit;"""
        with ThreadPoolExecutor(max_workers=1) as executor:
            pending=executor.submit(self.db.json,sql)
            # Read-only activity check establishes that the retrieval statement's
            # snapshot precedes publication, rather than relying on a fixed sleep.
            deadline=time.monotonic()+5
            while time.monotonic()<deadline:
                sleeping=self.db.json("""select to_json(exists(select 1 from pg_stat_activity
                    where datname=current_database() and wait_event='PgSleep'
                      and query like '%retrieve_context%'));""")
                if sleeping:
                    break
                time.sleep(0.02)
            self.assertTrue(sleeping,'retrieval snapshot did not enter controlled wait')
            try:
                self.manager.activate_release('release-test2')
                snapshot=pending.result(timeout=30)
                self.assertEqual(snapshot['status'],'ok')
                self.assertEqual(snapshot['release_id'],'release-both')
                self.assertEqual(len(snapshot['items']),2)
                self.assertEqual(self.search()['status'],'release_changed')
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


class RequiredNeighborDatabaseTests(unittest.TestCase):
    def test_transitive_neighbors_recovered_only_when_authorized(self):
        from backend.bintanong_retrieval.context import build_context
        db=StorageDatabase()
        self.addCleanup(db.close)
        # Two additional same-version clauses with synthetic printed provenance.
        sql=FIXTURE+"""
            update public.chunks set scope=array['program:TEST'], type_fields=jsonb_build_object(
                'entity_hints',jsonb_build_array('MAIN'), 'required_neighbor_chunk_ids',jsonb_build_array(repeat('c',64)))
                where chunk_id=repeat('a',64);
        """
        for char,text,required,scope in [('c','Required exception',['d'*64],['program:TEST']),('d','Exception condition',[],['program:TEST'])]:
            from tests.storage_database import sql_literal
            sql+=f"""
                insert into public.chunks(chunk_id,chunk_type,document_id,version_id,edition_id,byte_sha256,
                  text,source_text,content_hash,source_verification,content_review,scope,type_fields)
                values ({sql_literal(char*64)},'policy','doc-test','ver-test1','edition-test',repeat('0',64),
                  {sql_literal(text)},{sql_literal(text)},{sql_literal(compute_content_hash(text,text))},'verified','reviewed',
                  array['program:TEST'],{sql_literal(json.dumps({'required_neighbor_chunk_ids':required}))}::jsonb);
                insert into public.source_spans(chunk_id,version_id,byte_sha256,text,page,locator)
                values ({sql_literal(char*64)},'ver-test1',repeat('0',64),{sql_literal(text)},2,
                  {sql_literal(json.dumps({'kind':'section','section_path':[text]}))}::jsonb);
                insert into public.chunk_embeddings(chunk_id,embedding_set_id,chunk_content_hash,embedding)
                values ({sql_literal(char*64)},'set-test',{sql_literal(compute_content_hash(text,text))},
                  ('[' || '0,1,' || repeat('0,',1021) || '0]')::extensions.vector);
            """
        db.execute(sql+"update public.embedding_sets set total_chunks=4 where embedding_set_id='set-test'; commit;")
        client=DatabaseStorageClient(db)
        manager=ReleaseManager(client)
        manager.create_release('release-chain','chain','Synthetic','set-test',['a'*64,'c'*64,'d'*64],['ver-test1'])
        manager.activate_release('release-chain')
        params=dict(p_release_id='release-chain',p_config=IDENTITY,query_embedding=[1.0]+[0.0]*1023,
                    p_top_k=3,p_min_similarity=0.5,p_scope=['program:TEST'],p_entity_hints=['MAIN'],p_version_ids=[])
        snapshot=client.rpc('retrieve_context',params)
        self.assertEqual({r['chunk']['chunk_id'] for r in snapshot['items'][0]['neighbors']},{'c'*64,'d'*64})
        result=build_context(snapshot['items'],4096,len)
        self.assertEqual(len(result['evidence']),3)
        self.assertEqual(result['gaps'],[])
        params['p_scope']=['program:OTHER']
        self.assertEqual(client.rpc('retrieve_context',params)['items'],[])


if __name__ == '__main__':
    unittest.main()
