"""Actual-role disposable verification of scoped V1 storage and immutable references."""
import copy
from concurrent.futures import ThreadPoolExecutor
import json
import time
import unittest

from backend.bintanong_contracts.source import Chunk,bind_chunk,check_chunk_binding
from backend.bintanong_contracts.governance import SourceDocumentVersion
from backend.bintanong_storage.client import StorageError,PermissionDeniedError
from backend.bintanong_storage.loader import BatchKnowledgeLoader
from backend.bintanong_storage.source_acquisition import SourceAcquisitionLoader
from backend.bintanong_storage.source_verification import SourceVerificationLoader
from tests.storage_database import DatabaseStorageClient,sql_literal,FIXTURE
import tests.test_storage_selected_review_database as selected_database
from tests.test_storage_source_acquisition_verification import subsequent_check
from tests.test_storage_source_verification import observation_for,observed_record


class SourceVerificationDatabaseTests(unittest.TestCase):
    def setUp(self):
        selected_database.SelectedReviewDatabaseTests.prepare(self)
        partial=self.client.select('document_versions',role='admin')[0]['source_register']
        self.current=SourceAcquisitionLoader(self.client).verify(partial,subsequent_check(partial)).model_dump(mode='json')
        self.loader.record(self.receipt)
        self.loader.bind_release('release-selected',self.receipt['review_scope_id'])
        self.observation=observation_for(self.current)
        self.observer=SourceVerificationLoader(self.client)

    def rpc(self,current=...,observation=...):
        return self.client.rpc('observe_source_verification',dict(
            p_expected_register=self.current if current is ... else current,
            p_observation=self.observation if observation is ... else observation),role='admin')

    def snapshot(self,observations=True):
        tables=['document_versions','chunks','source_spans','chunk_embeddings','source_partial_reviews',
            'selected_release_reviews','knowledge_releases','release_document_versions','active_release']
        if observations:tables.append('source_verification_observations')
        return {t:self.client.select(t,role='admin') for t in tables}

    def reset(self):
        # Only for independent synthetic first-application scenarios in this DB.
        self.db.execute("update public.document_versions set verification_state='pending',source_register="+
            sql_literal(json.dumps(self.current))+"::jsonb where version_id="+sql_literal(self.current['version_id'])+";")

    def test_persist_exact_replay_preserves_evidence_receipts_rows_and_no_update(self):
        before=self.snapshot(observations=False)
        result=self.observer.observe(self.current,self.observation)
        self.assertEqual(result,SourceDocumentVersion.parse(observed_record(self.current,self.observation)))
        after=self.snapshot()
        version=after['document_versions'][0]
        self.assertEqual(version['source_register'],result.model_dump(mode='json'))
        self.assertEqual(version['verification_state'],'observed')
        self.assertEqual(after['source_verification_observations'][0]['receipt'],self.observation)
        for t in before:
            if t!='document_versions':self.assertEqual(before[t],after[t])
        self.assertEqual({k:v for k,v in before['document_versions'][0].items() if k not in ('source_register','verification_state')},
                         {k:v for k,v in version.items() if k not in ('source_register','verification_state')})
        self.db.execute("create function public.no_v1_update() returns trigger language plpgsql as $$ begin raise exception 'unexpected V1 update'; end $$; create trigger no_v1_update before update on public.document_versions for each row execute function public.no_v1_update();")
        self.assertEqual(self.observer.observe(self.current,self.observation),result)
        self.assertEqual(self.snapshot(),after)

    def test_direct_rpc_closed_shapes_nulls_bad_roles_scopes_labels_and_timing(self):
        cases=[(None,self.observation),([],self.observation),(self.current,None),(self.current,[]),
            (self.current,dict(self.observation,extra=True))]
        for key in self.observation:
            cases.append((self.current,{k:v for k,v in self.observation.items() if k!=key}))
            for value in (None,False,0,{},[]):cases.append((self.current,dict(self.observation,**{key:value})))
        for key,value in (('receipt_format','other'),('observation_scope','whole_source'),
                ('review_scope_id','8'*64),('partial_review_evidence_id','foreign-c1'),
                ('reviewer_label','someone else'),('compiler_label',' '),('timestamp_meaning','')):
            cases.append((self.current,dict(self.observation,**{key:value})))
        for key,value in (('kind','issuing_office_confirmation'),('recorded_by','researcher'),('recorded_by','system'),
                ('authorization_ref','forbidden'),('evidence_id',' '),('evidence_id','synthetic-partial-review'),
                ('recorded_at','2026-02-30T00:00:00Z'),('recorded_at','2026-10-16T10:30:00Z'),
                ('recorded_at','2026-10-16T12:00:00+23:99')):
            case=copy.deepcopy(self.observation);case['evidence'][key]=value;cases.append((self.current,case))
        for key in self.observation['evidence']:
            case=copy.deepcopy(self.observation);del case['evidence'][key];cases.append((self.current,case))
        before=self.snapshot()
        for current,observation in cases:
            with self.subTest(current=current,observation=observation),self.assertRaises(StorageError):self.rpc(current,observation)
        self.assertEqual(self.snapshot(),before)

    def test_direct_lifecycle_source_identity_and_specific_c1_reference_fail(self):
        cases=[]
        for field,value in (('filename','changed.pdf'),('version_id','ver-missing'),('byte_sha256','8'*64)):
            cases.append(dict(self.current,**{field:value}))
        for field,value in (('acquisition_state','observed'),('verification_state','verified'),
                ('content_review_state','pending'),('approval_state','requested')):
            case=copy.deepcopy(self.current);case[field]['state']=value;cases.append(case)
        case=copy.deepcopy(self.current);case['content_review_state']['evidence_ref']='foreign';cases.append(case)
        before=self.snapshot()
        for current in cases:
            with self.subTest(current=current),self.assertRaises(StorageError):self.rpc(current)
        self.assertEqual(self.snapshot(),before)

    def test_compilation_time_parity_equal_decision_and_offset_normalization(self):
        for moment in ('2026-10-16T11:00:00Z','2026-10-16T19:00:00+08:00',
                '2026-10-16T13:00:00+00:99','2026-10-17T11:59:00.123456789+23:59'):
            case=copy.deepcopy(self.observation);case['evidence']['recorded_at']=moment
            # Distinct seeded databases are unnecessary; exact same timestamp is
            # a replay only when all fields agree. Restore initial register and
            # use a distinct evidence ID for each synthetic independent check.
            case['evidence']['evidence_id']+='-'+moment
            with self.subTest(moment=moment):
                result=self.observer.observe(self.current,case)
                self.assertEqual(result.evidence[-1].recorded_at,moment)
                self.assertEqual(self.rpc(observation=case),result.model_dump(mode='json'))
            self.reset()

    def test_replay_and_first_application_detect_relational_and_snapshot_drift(self):
        for replay in (False,True):
            if replay:self.rpc()
            original=self.client.select('document_versions',role='admin')[0]
            self.db.execute("update public.document_versions set issuer='{}'::jsonb;")
            with self.subTest(replay=replay),self.assertRaises(StorageError):self.rpc()
            self.db.execute('update public.document_versions set issuer='+sql_literal(json.dumps(original['issuer']))+'::jsonb;')
            self.db.execute("update public.source_spans set text='drift';")
            before=self.snapshot()
            with self.subTest(replay=replay),self.assertRaises(StorageError):self.rpc()
            self.assertEqual(self.snapshot(),before)
            self.db.execute('update public.source_spans set text='+sql_literal(self.partial['chunks'][0]['spans'][0]['text'])+';')

    def test_same_concurrent_calls_converge_different_receipts_conflict(self):
        def call(observation):
            try:return self.rpc(observation=observation)
            except StorageError:return None
        with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(call,[self.observation,self.observation]))
        self.assertTrue(all(r is not None for r in results))
        other=copy.deepcopy(self.observation);other['evidence']['evidence_id']='different-observation'
        before=self.snapshot()
        with self.assertRaises(StorageError):self.rpc(observation=other)
        with self.assertRaises(StorageError):self.rpc(dict(self.current,filename='stale.pdf'))
        self.assertEqual(self.snapshot(),before)

    def test_concurrent_different_observations_have_one_winner(self):
        other=copy.deepcopy(self.observation);other['evidence']['evidence_id']='competing-observation'
        def call(observation):
            try:return self.rpc(observation=observation)
            except StorageError:return None
        with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(call,[self.observation,other]))
        self.assertEqual(sum(r is not None for r in results),1)
        self.assertEqual(len(self.client.select('source_verification_observations',role='admin')),1)
        self.assertIn(self.client.select('document_versions',role='admin')[0]['source_register'],results)

    def test_missing_legacy_and_ever_published_source_rejected(self):
        self.db.execute('update public.document_versions set source_register=null;')
        with self.assertRaises(StorageError):self.rpc()
        self.reset()
        self.db.execute(FIXTURE.replace("repeat('a',64)","repeat('e',64)")+"commit;")
        self.manager.activate_release('release-test1')
        self.manager.activate_release('release-test2')
        current=dict(self.current,version_id='ver-test1')
        observation=dict(self.observation,version_id='ver-test1')
        with self.assertRaisesRegex(StorageError,'Published'):self.rpc(current,observation)

    def test_ordinary_rebinding_changes_only_chunk_review_metadata(self):
        from tests.test_contracts_source import chunk_dict,span_dict
        raw=chunk_dict(chunk_type='policy',document_id=self.current['document_id'],
            version_id=self.current['version_id'],edition_id=self.current['edition_id'],
            byte_sha256=self.current['byte_sha256'],source_label=self.current['filename'],
            spans=[span_dict(byte_sha256=self.current['byte_sha256'],version_id=self.current['version_id'])])
        old=bind_chunk(Chunk.parse(raw),SourceDocumentVersion.parse(self.current))
        current=self.observer.observe(self.current,self.observation)
        with self.assertRaises(ValueError):check_chunk_binding(old,current)
        bound=bind_chunk(old,current);check_chunk_binding(bound,current)
        stored_before=self.snapshot()
        changed=dict(self.chunk,source_verification='observed',content_review='partially_reviewed')
        BatchKnowledgeLoader(self.client).load_chunks([changed])
        stored_after=self.snapshot()
        for table in stored_before:
            if table!='chunks':self.assertEqual(stored_before[table],stored_after[table])
        before,after=stored_before['chunks'][0],stored_after['chunks'][0]
        self.assertEqual({k:v for k,v in before.items() if k!='source_verification'},
                         {k:v for k,v in after.items() if k!='source_verification'})
        self.assertEqual(after['source_verification'],'observed')
        self.assertEqual(self.loader.bind_release('release-selected','9'*64),dict(release_id='release-selected',review_scope_id='9'*64))
        with self.assertRaises(StorageError):self.manager.activate_release('release-selected')

    def test_roles_public_and_accidental_grants_cannot_use_or_mutate_receipts(self):
        self.rpc()
        for role in ('anon','authenticated'):
            reader=DatabaseStorageClient(self.db,runtime_role=role)
            with self.subTest(role=role),self.assertRaises(PermissionDeniedError):
                reader.rpc('observe_source_verification',dict(p_expected_register=self.current,p_observation=self.observation))
            with self.assertRaisesRegex(AssertionError,'permission denied'):reader.select('source_verification_observations')
            self.assertEqual(reader.select('document_versions'),[])
        self.db.execute('grant all on public.source_verification_observations to anon,authenticated; create policy accidental_v1_allow on public.source_verification_observations for all to anon,authenticated using(true) with check(true);')
        for role in ('anon','authenticated'):
            reader=DatabaseStorageClient(self.db,runtime_role=role)
            self.assertEqual(reader.select('source_verification_observations'),[])
            for verb in ('update public.source_verification_observations set receipt=receipt',
                    'delete from public.source_verification_observations','truncate public.source_verification_observations'):
                output=self.db._command(self.db.name,'begin;set local role '+role+';'+verb+';rollback;')
                self.assertTrue(output.returncode,output.stdout)
        for verb in ('update public.source_verification_observations set receipt=receipt',
                'delete from public.source_verification_observations','truncate public.source_verification_observations'):
            with self.assertRaisesRegex(AssertionError,'immutable'):self.db.execute(verb+';')
        attrs=self.db.json("select jsonb_build_object('definer',prosecdef,'public',exists(select 1 from aclexplode(proacl) a where a.grantee=0 and a.privilege_type='EXECUTE')) from pg_proc where proname='observe_source_verification';")
        self.assertEqual(attrs,dict(definer=False,public=False))

    def test_publication_lock_serialization_and_transaction_rollback(self):
        before=self.snapshot()
        query='begin;set local role service_role;select public.observe_source_verification('+sql_literal(json.dumps(self.current))+'::jsonb,'+sql_literal(json.dumps(self.observation))+"::jsonb);select 1/0;commit;"
        with self.assertRaises(AssertionError):self.db.execute(query)
        self.assertEqual(self.snapshot(),before)
        with ThreadPoolExecutor(max_workers=1) as pool:
            held=pool.submit(self.db.execute,'begin;select bintanong_private.publication_lock();select pg_sleep(1);commit;')
            deadline=time.monotonic()+5
            while time.monotonic()<deadline:
                if self.db.json("select to_jsonb(exists(select 1 from pg_locks where locktype='advisory' and granted and database=(select oid from pg_database where datname=current_database())));"):break
            else:self.fail('publication lock not acquired')
            started=time.monotonic();self.rpc();elapsed=time.monotonic()-started;held.result()
            self.assertGreater(elapsed,.1)
