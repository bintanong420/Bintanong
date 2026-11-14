"""Disposable actual-role tests of selected undergraduate release coverage."""
import copy
import json
from concurrent.futures import ThreadPoolExecutor
import time
import unittest

from backend.bintanong_storage.client import StorageError, PermissionDeniedError
from backend.bintanong_storage.loader import BatchKnowledgeLoader, CONFIG_FIELDS
from backend.bintanong_storage.release import ReleaseManager
from backend.bintanong_storage.selected_release_review import SelectedReleaseReviewLoader
from backend.bintanong_storage.source_registration import SourceRegistrationLoader
from backend.bintanong_storage.source_acquisition import SourceAcquisitionLoader
from backend.bintanong_storage.source_partial_review import SourcePartialReviewLoader
from tests.storage_database import StorageDatabase, DatabaseStorageClient, sql_literal, FIXTURE
from tests.test_storage_source_registration import pending_version, document_record
from tests.test_storage_source_acquisition import byte_check
from tests.test_storage_selected_release_review import selected_fixture, add_record_group, add_flow_group
from backend.bintanong_contracts.reviewed_policy_context import serialize_reviewed_fields
from backend.bintanong_contracts.source import compute_content_hash


class SelectedReviewDatabaseTests(unittest.TestCase):
    def setUp(self):
        self.prepare()

    def prepare(self,mutate=None):
        self.db = StorageDatabase(); self.addCleanup(self.db.close)
        self.client = DatabaseStorageClient(self.db)
        initial = pending_version()
        SourceRegistrationLoader(self.client).load_versions([initial],[document_record()])
        source = SourceAcquisitionLoader(self.client).observe(initial,byte_check(initial)).model_dump(mode='json')
        _, self.partial, self.receipt, self.text = selected_fixture()
        if mutate:
            mutate(self.partial)
            for chunk in self.partial['chunks']:
                fields = chunk['type_fields']
                text = serialize_reviewed_fields(fields['field_associations'],fields['source_limits'],fields.get('service_group'))
                chunk['content_hash'] = compute_content_hash(chunk['spans'][0]['text'],text)
            self.text = serialize_reviewed_fields(self.partial['chunks'][0]['type_fields']['field_associations'],
                self.partial['chunks'][0]['type_fields']['source_limits'],self.partial['chunks'][0]['type_fields'].get('service_group'))
            self.receipt['chunks'] = copy.deepcopy(self.partial['chunks'])
        snap = self.partial['chunks'][0]
        self.chunk = dict(chunk_id=snap['chunk_id'], chunk_type='policy',
            chunker_version='palsu-reviewed-policy-context-chunker-v1',
            document_id=source['document_id'], version_id=source['version_id'],
            edition_id=source['edition_id'], byte_sha256=source['byte_sha256'],
            source_verification='pending', content_review='pending', text=self.text,
            source_text=snap['spans'][0]['text'],content_hash=snap['content_hash'],
            type_fields=snap['type_fields'],spans=snap['spans'],scope=['audience:undergraduate'])
        records = []
        for chunk in self.partial['chunks']:
            fields = chunk['type_fields']
            records.append(dict(self.chunk,chunk_id=chunk['chunk_id'],spans=chunk['spans'],type_fields=fields,
                source_text=chunk['spans'][0]['text'],content_hash=chunk['content_hash'],
                text=serialize_reviewed_fields(fields['field_associations'],fields['source_limits'],fields.get('service_group'))))
        BatchKnowledgeLoader(self.client).load_chunks(records)
        SourcePartialReviewLoader(self.client).record(source,self.partial)
        self.db.execute("update public.chunks set content_review='partially_reviewed';")
        self.db.execute("""
          insert into public.embedding_sets(embedding_set_id,model_id,model_revision,dimension,normalization,
            prompt_fingerprint,preprocessing_fingerprint,tokenizer_fingerprint,total_chunks)
          values ('set-selected','synthetic-model',repeat('2',64),1024,'l2',repeat('3',64),repeat('4',64),repeat('5',64),1);
          insert into public.chunk_embeddings(chunk_id,embedding_set_id,chunk_content_hash,embedding)
          select chunk_id,'set-selected',content_hash,('[' || '1,' || repeat('0,',1022) || '0]')::extensions.vector from public.chunks;
          update public.embedding_sets set total_chunks=(select count(*) from public.chunks) where embedding_set_id='set-selected';
        """)
        self.loader = SelectedReleaseReviewLoader(self.client)
        self.manager = ReleaseManager(self.client)
        self.manager.create_release('release-selected','selected-test','Synthetic undergraduate selection',
            'set-selected',[c['chunk_id'] for c in self.partial['chunks']],[initial['version_id']])

    def record(self,receipt=...):
        return self.client.rpc('record_selected_release_review', {'p_receipt':self.receipt if receipt is ... else receipt},role='admin')

    def bind(self):
        return self.loader.bind_release('release-selected','9'*64)

    def authority(self):
        # Explicitly synthetic authority for the publication mechanics test only.
        self.db.execute("update public.document_versions set verification_state='verified',approval_state='approved';"
                        "update public.chunks set source_verification='verified';")

    def test_receipt_binding_replay_and_current_source_states_are_unchanged(self):
        before = self.client.select('document_versions',role='admin')
        self.assertEqual(self.loader.record(self.receipt),self.receipt)
        saved = self.client.select('selected_release_reviews',role='admin')
        self.assertEqual(self.record(),self.receipt)
        expected = dict(release_id='release-selected',review_scope_id='9'*64)
        self.assertEqual(self.bind(),expected); self.assertEqual(self.bind(),expected)
        self.assertEqual(self.client.select('selected_release_reviews',role='admin'),saved)
        self.assertEqual(self.client.select('document_versions',role='admin'),before)

    def test_direct_closed_shape_and_decision_coverage_fail_atomically(self):
        cases = [None, [], {}, dict(self.receipt, supported_scope='staff'),dict(self.receipt,extra=True)]
        for key in self.receipt:
            for value in (None,False,0,[],{}): cases.append(dict(self.receipt,**{key:value}))
        for key in self.receipt['decision']:
            case = copy.deepcopy(self.receipt); case['decision'][key] = ''; cases.append(case)
        for field,value in (('recorded_at','2026-10-16T09:00:00Z'),('decision_document','../private.md')):
            case = copy.deepcopy(self.receipt); case['decision'][field] = value; cases.append(case)
        for case in cases:
            with self.subTest(case=case),self.assertRaises(StorageError): self.record(case)
        self.assertEqual(self.client.select('selected_release_reviews',role='admin'),[])
        self.record()
        changed = copy.deepcopy(self.receipt); changed['decision']['owner_response'] = 'Changed scope'
        with self.assertRaises(StorageError): self.record(changed)

    def test_partial_receipt_chunk_field_span_event_and_neighbor_changes_reject(self):
        for field,value in (('content_hash','0'*64),('chunk_id','b'*64),('spans',[])):
            case = copy.deepcopy(self.receipt); case['chunks'][0][field] = value
            with self.subTest(field=field),self.assertRaises(StorageError): self.record(case)
        for field,value in (('required_neighbor_chunk_ids',['b'*64]),('applicability_basis_ref','other')):
            case = copy.deepcopy(self.receipt); case['chunks'][0]['type_fields'][field] = value
            with self.subTest(field=field),self.assertRaises(StorageError): self.record(case)
        case = copy.deepcopy(self.receipt); case['chunks'][0]['type_fields']['field_associations'][0]['event_sha256'] = '0'*64
        with self.assertRaises(StorageError): self.record(case)
        case = copy.deepcopy(self.receipt); case['sources'][0]['partial_review_evidence_id'] = 'absent'
        with self.assertRaises(StorageError): self.record(case)

    def test_hash_retaining_text_drift_rejects_first_replay_binding_and_publication(self):
        def drift(): self.db.execute("update public.chunks set text='Changed unreviewed text';")
        def restore(): self.db.execute('update public.chunks set text='+sql_literal(self.text)+';')
        drift()
        with self.assertRaises(StorageError): self.record()
        restore(); self.record(); drift()
        with self.assertRaises(StorageError): self.record()
        with self.assertRaises(StorageError): self.bind()
        restore(); self.bind(); self.authority(); drift()
        with self.assertRaises(StorageError): self.manager.activate_release('release-selected')
        self.assertEqual(self.client.select('active_release',role='admin'),[])

    def test_no_authority_no_binding_and_pending_review_remain_blocked(self):
        self.record(); self.bind()
        with self.assertRaises(StorageError): self.manager.activate_release('release-selected')
        self.authority()
        self.db.execute("update public.chunks set content_review='pending';")
        with self.assertRaises(StorageError): self.manager.activate_release('release-selected')
        self.db.execute("update public.chunks set content_review='partially_reviewed'; update public.knowledge_releases set review_scope_id=null;")
        with self.assertRaises(StorageError): self.manager.activate_release('release-selected')

    def test_exact_membership_publication_roles_privacy_immutability_and_rollback(self):
        self.record(); self.bind(); self.authority()
        for role in ('anon','authenticated'):
            self.assertEqual(DatabaseStorageClient(self.db,runtime_role=role).select('chunks'),[])
        # Negative scope fixture only; it is never a selected or active policy.
        self.db.execute("""insert into public.chunks(chunk_id,chunk_type,document_id,version_id,edition_id,
            byte_sha256,text,content_hash,scope) select repeat('b',64),chunk_type,document_id,version_id,edition_id,
            byte_sha256,'Excluded staff procedure',bintanong_private.content_hash(null,'Excluded staff procedure'),
            array['audience:staff'] from public.chunks limit 1;""")
        self.manager.activate_release('release-selected')
        for role in ('anon','authenticated'):
            runtime = DatabaseStorageClient(self.db,runtime_role=role)
            self.assertEqual([c['chunk_id'] for c in runtime.select('chunks')],['a'*64])
            self.assertEqual(len(runtime.select('source_spans')),1)
            configuration = self.client.select('embedding_sets',role='admin')[0]
            response = runtime.rpc('retrieve_context',dict(query_embedding=[1.0]+[0.0]*1023,
                p_release_id='release-selected',p_config={k:configuration[k] for k in CONFIG_FIELDS},
                p_top_k=3,p_min_similarity=.25,p_scope=['audience:undergraduate'],
                p_entity_hints=[],p_version_ids=[]))
            self.assertEqual(response['status'],'ok')
            self.assertEqual([item['chunk']['chunk_id'] for item in response['items']],['a'*64])
            with self.assertRaisesRegex(AssertionError,'permission denied'): runtime.select('selected_release_reviews')
            with self.assertRaises(PermissionDeniedError): runtime.rpc('record_selected_release_review',{'p_receipt':self.receipt})
            with self.assertRaises(PermissionDeniedError): runtime.rpc('bind_selected_release_review',dict(p_release_id='release-selected',p_review_scope_id='9'*64))
        for sql in ("update public.selected_release_reviews set receipt='{}';",
                "delete from public.selected_release_reviews;", "truncate public.selected_release_reviews;",
                "update public.knowledge_releases set review_scope_id=null;",
                "delete from public.release_chunks where release_id='release-selected';"):
            with self.subTest(sql=sql),self.assertRaises(AssertionError): self.db.execute(sql)
        fixture = FIXTURE.replace("repeat('a',64)","repeat('c',64)").replace("repeat('b',64)","repeat('d',64)")
        self.db.execute(fixture+'commit;')
        self.manager.activate_release('release-test1')
        self.manager.rollback_release('release-selected')
        self.assertEqual([c['chunk_id'] for c in self.client.select('chunks')],['a'*64])

    def test_membership_changes_after_binding_and_different_binding_reject(self):
        self.record(); self.bind(); self.authority()
        other = copy.deepcopy(self.receipt); other['review_scope_id'] = '8'*64
        self.record(other)
        with self.assertRaises(StorageError): self.loader.bind_release('release-selected','8'*64)
        self.db.execute("delete from public.release_chunks where release_id='release-selected'; update public.knowledge_releases set expected_chunk_count=1;")
        with self.assertRaises(StorageError): self.manager.activate_release('release-selected')
        with self.assertRaises(StorageError): self.bind()

    def test_actual_grants_invoker_functions_and_accidental_runtime_grants(self):
        self.record()
        for role in ('anon','authenticated'):
            for privilege in ('SELECT','INSERT','UPDATE','DELETE','TRUNCATE'):
                self.assertFalse(self.db.json('select to_jsonb(has_table_privilege('+sql_literal(role)+
                    ",'public.selected_release_reviews',"+sql_literal(privilege)+'));'))
            self.db.execute('grant select on public.selected_release_reviews to '+role+';')
            self.assertEqual(DatabaseStorageClient(self.db,runtime_role=role).select('selected_release_reviews'),[])
        attrs = self.db.json("""select jsonb_agg(jsonb_build_object('definer',prosecdef,'public',
            exists(select 1 from aclexplode(proacl) a where a.grantee=0 and a.privilege_type='EXECUTE')))
            from pg_proc where proname in ('record_selected_release_review','bind_selected_release_review');""")
        self.assertEqual(attrs,[dict(definer=False,public=False)]*2)
        for privilege in ('UPDATE','DELETE','TRUNCATE'):
            self.assertFalse(self.db.json("select to_jsonb(has_table_privilege('service_role','public.selected_release_reviews',"+sql_literal(privilege)+'));'))

    def test_span_metadata_source_and_extended_membership_drift_are_rechecked(self):
        self.record(); self.bind(); self.authority()
        changes = [("update public.source_spans set page=2;","update public.source_spans set page=1;"),
            ("update public.chunks set type_fields=type_fields||'{\"unexpected\":true}'::jsonb;",
             "update public.chunks set type_fields=type_fields-'unexpected';")]
        for change,restore in changes:
            self.db.execute(change)
            with self.subTest(change=change),self.assertRaises(StorageError): self.manager.activate_release('release-selected')
            with self.assertRaises(StorageError): self.record()
            self.db.execute(restore)
        self.db.execute("""insert into public.chunks(chunk_id,chunk_type,document_id,version_id,edition_id,
            byte_sha256,text,content_hash) select repeat('b',64),chunk_type,document_id,version_id,edition_id,
            byte_sha256,'Unreviewed extension',bintanong_private.content_hash(null,'Unreviewed extension')
            from public.chunks limit 1;
            insert into public.release_chunks values ('release-selected',repeat('b',64));
            update public.knowledge_releases set expected_chunk_count=2;
        """)
        with self.assertRaises(StorageError): self.manager.activate_release('release-selected')

    def test_concurrent_record_replay_and_lock_serialization(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _:self.record(),range(2)))
        self.assertEqual(results,[self.receipt,self.receipt])
        with ThreadPoolExecutor(max_workers=2) as pool:
            marker = 91736403
            hold = pool.submit(self.db.execute,"begin; select pg_advisory_xact_lock(420,4); select pg_advisory_xact_lock("+str(marker)+"); select pg_sleep(0.8); update public.chunks set text='Concurrent drift'; commit;")
            deadline = time.monotonic()+10
            while not self.db.json("select to_jsonb(exists(select 1 from pg_locks where locktype='advisory' and objid="+str(marker)+" and granted));"):
                if time.monotonic()>deadline: self.fail('Writer did not acquire marker')
                time.sleep(0.02)
            with self.assertRaises(StorageError): self.bind()
            hold.result()

    def test_direct_rpc_rejects_incomplete_group_already_present_in_c1(self):
        self.prepare(lambda r:r['chunks'][0]['type_fields'].update(service_group=dict(
            logical_step_id='synthetic-procedure',part_order=0,part_count=2)))
        with self.assertRaises(StorageError): self.record()

    def test_direct_rpc_rejects_unprinted_value_already_present_in_c1(self):
        self.prepare(lambda r:r['chunks'][0]['type_fields']['field_associations'][0].update(
            value='A different unreviewed undergraduate condition'))
        with self.assertRaises(StorageError): self.record()

    def test_complete_record_group_preserves_original_gap_hash_and_can_publish(self):
        self.prepare(add_record_group)
        self.loader.record(self.receipt); self.bind(); self.authority()
        self.manager.activate_release('release-selected')
        self.assertEqual(len(self.client.select('chunks')),2)

    def test_complete_flow_group_records_and_can_publish(self):
        self.prepare(add_flow_group)
        self.loader.record(self.receipt); self.bind(); self.authority()
        self.manager.activate_release('release-selected')
        self.assertEqual(len(self.client.select('chunks')),2)

    def test_flow_manifest_differing_from_its_review_event_is_rejected_by_sql(self):
        def mutate(partial):
            add_flow_group(partial)
            for chunk in partial['chunks']:
                chunk['type_fields']['service_group']['flow_manifest']['nodes'][1]['region']=[0,20,10,31]
        self.prepare(mutate)
        with self.assertRaises(StorageError): self.record()

    def test_flow_group_with_differing_member_manifests_is_rejected_by_sql(self):
        def mutate(partial):
            add_flow_group(partial)
            partial['chunks'][1]['type_fields']['service_group']['flow_manifest']['physical_page']=2
        self.prepare(mutate)
        with self.assertRaises(StorageError): self.record()

    def test_missing_projected_original_gap_in_c1_is_rejected_by_sql(self):
        def mutate(partial):
            add_record_group(partial)
            partial['chunks'][1]['type_fields']['source_limits'] = []
        self.prepare(mutate)
        with self.assertRaises(StorageError): self.record()
