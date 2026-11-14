"""Synthetic scoped C1 receipts, never institutional source approvals."""
import copy
import importlib
import importlib.util
import json
from concurrent.futures import ThreadPoolExecutor
import time
import unittest

from backend.bintanong_contracts.governance import SourceDocumentVersion
from backend.bintanong_storage.client import StorageError
from tests.test_storage_source_acquisition import byte_check, observed_record
from tests.test_storage_source_registration import pending_version
from tests.test_storage_source_registration import document_record
from tests.storage_database import StorageDatabase, DatabaseStorageClient, sql_literal, FIXTURE
from backend.bintanong_storage.source_registration import SourceRegistrationLoader
from backend.bintanong_storage.source_acquisition import SourceAcquisitionLoader
from backend.bintanong_storage.source_partial_review import SourcePartialReviewLoader
from backend.bintanong_storage.loader import BatchKnowledgeLoader


def current_source():
    pending = pending_version()
    return observed_record(pending, byte_check(pending))


def receipt_for(current=None):
    current = current or current_source()
    event = dict(event_sha256='7'*64, representation='original_file_bytes',
        source_sha256=current['byte_sha256'], owner_event_sha256='8'*64,
        actual_owner_label='owner (chat confirmation)', recorded_at='2026-10-13T08:00:00Z',
        timestamp_meaning='Recording time only; not school verification')
    span = dict(chunk_id='a'*64, span_order=0, version_id=current['version_id'],
        byte_sha256=current['byte_sha256'], page=1, printed_page_label=None,
        locator=dict(kind='section', section_path=['Synthetic']), text='Synthetic visible field',
        bbox=None, bbox_origin=None, page_size=None, extraction={})
    fields = dict(reading_id='synthetic-reading', context_format='reviewed-policy-fields-v1',
        applicability_basis_ref='C:/synthetic/audit-evidence/confirmation.json',
        required_neighbor_chunk_ids=[], source_limits=[dict(issue='synthetic visible cutoff')],
        field_associations=[dict(name='condition', value='Synthetic visible field', source_blank=False,
            event_sha256=event['event_sha256'], span_indexes=[0])])
    from backend.bintanong_contracts.source import compute_content_hash
    return dict(receipt_format='selected-source-partial-review-v1',
        version_id=current['version_id'], source_sha256=current['byte_sha256'],
        acquisition_locators=list(current['acquisition_locators']),
        evidence=dict(evidence_id='synthetic-partial-review', kind='content_review_record',
            recorded_by='reviewer', recorded_at='2026-10-16T10:00:00Z', authorization_ref=None),
        reviewer_label=event['actual_owner_label'], compiler_label='Synthetic compiler',
        review_scope='selected_fields', source_events=[event], chunks=[dict(chunk_id='a'*64,
            content_hash=compute_content_hash(span['text'], span['text']), type_fields=fields, spans=[span])])


def partial_record(current, receipt):
    result = copy.deepcopy(current)
    result['evidence'].append(copy.deepcopy(receipt['evidence']))
    result['content_review_state'] = dict(state='partially_reviewed', evidence_ref=receipt['evidence']['evidence_id'])
    return result


def loader_class(test):
    name = 'backend.bintanong_storage.source_partial_review'
    test.assertIsNotNone(importlib.util.find_spec(name), 'Scoped C1 loader is not implemented')
    return importlib.import_module(name).SourcePartialReviewLoader


class RecordingClient:
    def __init__(self):
        self.calls, self.response, self.error = [], None, None

    def rpc(self, name, params, role):
        self.calls.append((name, copy.deepcopy(params), role))
        if self.error:
            raise self.error
        return self.response if self.response is not None else partial_record(
            params['p_expected_register'], params['p_receipt'])


class PartialReviewLoaderTests(unittest.TestCase):
    def setUp(self):
        self.current, self.client = current_source(), RecordingClient()
        self.receipt = receipt_for(self.current)

    def test_exact_admin_request_retains_input_history_owner_provenance_and_compilation(self):
        before = copy.deepcopy((self.current,self.receipt))
        for current in (self.current, SourceDocumentVersion.parse(self.current)):
            result = loader_class(self)(self.client).record(current,self.receipt)
            self.assertEqual(result, SourceDocumentVersion.parse(partial_record(self.current,self.receipt)))
            self.assertEqual(self.client.calls[-1], ('record_source_partial_review',dict(
                p_expected_register=self.current,p_receipt=self.receipt),'admin'))
        self.assertEqual((self.current,self.receipt), before)

    def test_closed_envelopes_and_nested_objects_reject_before_rpc(self):
        cases = [None,[],{},dict(self.receipt,extra=True),dict(self.receipt,review_scope='whole_source'),
            dict(self.receipt,receipt_format='other'),dict(self.receipt,version_id='ver-other'),
            dict(self.receipt,source_sha256='9'*64),dict(self.receipt,acquisition_locators=[])]
        for key in self.receipt:
            cases.append({k:v for k,v in self.receipt.items() if k != key})
        for key in ('reviewer_label','compiler_label'):
            cases.append(dict(self.receipt,**{key:' '}))
        for field,value in (('kind','printed_text_span'),('recorded_by','researcher'),
                ('authorization_ref','forbidden'),('recorded_at','2026-02-30T00:00:00Z'),
                ('recorded_at','2026-10-12T00:00:00Z'),('evidence_id',' ')):
            case = copy.deepcopy(self.receipt); case['evidence'][field] = value; cases.append(case)
        for target in ('source_events','chunks'):
            cases += [dict(self.receipt,**{target:[]}),dict(self.receipt,**{target:[None]})]
            case = copy.deepcopy(self.receipt); case[target].append(copy.deepcopy(case[target][0])); cases.append(case)
            for key in self.receipt[target][0]:
                case = copy.deepcopy(self.receipt); del case[target][0][key]; cases.append(case)
        for case in cases:
            with self.subTest(case=case), self.assertRaises(ValueError):
                loader_class(self)(self.client).record(self.current,case)
        self.assertEqual(self.client.calls, [])

    def test_source_event_binding_shapes_labels_and_times(self):
        for field,value in (('source_sha256','9'*64),('event_sha256','bad'),
                ('owner_event_sha256','BAD'),('actual_owner_label',' '),('representation','guessed'),
                ('timestamp_meaning',''),('recorded_at','2026-02-30T00:00:00Z'),
                ('recorded_at','2026-10-17T00:00:00Z')):
            case = copy.deepcopy(self.receipt); case['source_events'][0][field] = value
            with self.subTest(field=field,value=value),self.assertRaises(ValueError):
                loader_class(self)(self.client).record(self.current,case)
        case = copy.deepcopy(self.receipt); case['reviewer_label'] = 'unbound person'
        with self.assertRaises(ValueError):
            loader_class(self)(self.client).record(self.current,case)
        self.assertEqual(self.client.calls, [])

    def test_field_span_and_dependency_bindings_are_complete_and_local(self):
        changes = [('field_associations',[]),('required_neighbor_chunk_ids',['b'*64]),
            ('source_limits',None)]
        for key,value in changes:
            case = copy.deepcopy(self.receipt); case['chunks'][0]['type_fields'][key] = value
            with self.subTest(key=key),self.assertRaises(ValueError):
                loader_class(self)(self.client).record(self.current,case)
        for field,value in (('event_sha256','9'*64),('span_indexes',[]),('span_indexes',[True]),
                ('span_indexes',[1]),('span_indexes',[0,0]),('name',''),('source_blank','false')):
            case = copy.deepcopy(self.receipt); case['chunks'][0]['type_fields']['field_associations'][0][field] = value
            with self.subTest(field=field,value=value),self.assertRaises(ValueError):
                loader_class(self)(self.client).record(self.current,case)
        for field,value in (('chunk_id','b'*64),('span_order',1),('page',True),
                ('version_id','ver-other'),('byte_sha256','9'*64),('locator',None)):
            case = copy.deepcopy(self.receipt); case['chunks'][0]['spans'][0][field] = value
            with self.subTest(field=field),self.assertRaises(ValueError):
                loader_class(self)(self.client).record(self.current,case)
        self.assertEqual(self.client.calls, [])

    def test_initial_c1_states_and_distinct_evidence_are_required(self):
        cases = [pending_version(),partial_record(self.current,self.receipt),
            dict(self.current,approval_id='forbidden')]
        duplicate = copy.deepcopy(self.current); duplicate['evidence'].append(self.receipt['evidence']); cases.append(duplicate)
        for field in ('verification_state','approval_state'):
            case = copy.deepcopy(self.current); case[field]['state'] = 'observed'; cases.append(case)
        for case in cases:
            with self.subTest(case=case),self.assertRaises(ValueError):
                loader_class(self)(self.client).record(case,self.receipt)
        self.assertEqual(self.client.calls, [])

    def test_altered_return_and_uncertain_storage_outcome_never_trigger_retry(self):
        for response in ([],{},self.current,dict(partial_record(self.current,self.receipt),filename='other.pdf')):
            self.client.response = response
            with self.subTest(response=response),self.assertRaises(ValueError):
                loader_class(self)(self.client).record(self.current,self.receipt)
        self.client = RecordingClient(); self.client.error = StorageError('synthetic timeout')
        with self.assertRaises(StorageError):
            loader_class(self)(self.client).record(self.current,self.receipt)
        self.assertEqual(len(self.client.calls), 1)


class PartialReviewDatabaseTests(unittest.TestCase):
    def setUp(self):
        self.db = StorageDatabase(); self.addCleanup(self.db.close)
        self.client = DatabaseStorageClient(self.db)
        initial = pending_version()
        SourceRegistrationLoader(self.client).load_versions([initial],[document_record()])
        self.current = SourceAcquisitionLoader(self.client).observe(initial,byte_check(initial)).model_dump(mode='json')
        self.receipt = receipt_for(self.current)
        snapshot = self.receipt['chunks'][0]
        self.chunk = dict(chunk_id=snapshot['chunk_id'],chunk_type='policy',
            document_id=self.current['document_id'],version_id=self.current['version_id'],
            edition_id=self.current['edition_id'],byte_sha256=self.current['byte_sha256'],
            source_verification='pending',content_review='pending',
            text=snapshot['spans'][0]['text'],source_text=snapshot['spans'][0]['text'],
            content_hash=snapshot['content_hash'],spans=snapshot['spans'],type_fields=snapshot['type_fields'])
        BatchKnowledgeLoader(self.client).load_chunks([self.chunk])
        self.loader = SourcePartialReviewLoader(self.client)

    def rpc(self, current=None, receipt=None):
        return self.client.rpc('record_source_partial_review',dict(
            p_expected_register=self.current if current is None else current,
            p_receipt=self.receipt if receipt is None else receipt),role='admin')

    def snapshot(self):
        return {t:self.client.select(t,role='admin') for t in
            ('document_versions','chunks','source_spans','source_partial_reviews')}

    def test_persistence_and_exact_replay_retain_all_other_rows_and_columns(self):
        expected = partial_record(self.current,self.receipt)
        before = self.client.select('document_versions',role='admin')[0]
        self.assertEqual(self.rpc(),expected)
        after = self.client.select('document_versions',role='admin')[0]
        self.assertEqual(after['source_register'],expected)
        self.assertEqual(after['content_review_state'],'partially_reviewed')
        self.assertEqual({k:v for k,v in before.items() if k not in ('content_review_state','source_register')},
                         {k:v for k,v in after.items() if k not in ('content_review_state','source_register')})
        stored = self.snapshot()
        self.assertEqual(stored['source_partial_reviews'][0]['receipt'],self.receipt)
        self.assertEqual(self.rpc(),expected)
        self.assertEqual(self.snapshot(),stored)
        self.assertEqual(stored['chunks'][0]['content_review'],'pending')

    def test_direct_malformed_shapes_roles_timestamps_and_source_bindings_rollback(self):
        calls = [(None,self.receipt),([],self.receipt),(self.current,None),(self.current,[])]
        for key in self.receipt:
            for value in (None,False,0,[],{}):
                calls.append((self.current,dict(self.receipt,**{key:value})))
            calls.append((self.current,{k:v for k,v in self.receipt.items() if k != key}))
        for target in ('evidence','source_events','chunks'):
            original = self.receipt[target][0] if target != 'evidence' else self.receipt[target]
            for key in original:
                for value in (None,False,{},[]):
                    if type(value) is type(original[key]) and value == original[key]:
                        continue
                    case = copy.deepcopy(self.receipt)
                    (case[target][0] if target != 'evidence' else case[target])[key] = value
                    calls.append((self.current,case))
        for field,value in (('recorded_by','researcher'),('kind','printed_text_span'),
                ('recorded_at','2026-02-30T00:00:00Z'),('recorded_at','2026-10-12T00:00:00Z'),
                ('recorded_at','2026-10-16T25:00:00Z'),('authorization_ref','forbidden'),('evidence_id',' ')):
            case = copy.deepcopy(self.receipt); case['evidence'][field] = value; calls.append((self.current,case))
        before = self.snapshot()
        for current,receipt in calls:
            with self.subTest(current=current,receipt=receipt),self.assertRaises(StorageError):
                self.client.rpc('record_source_partial_review',dict(p_expected_register=current,p_receipt=receipt),role='admin')
        self.assertEqual(self.snapshot(),before)

    def test_snapshot_omissions_foreign_bindings_and_dependencies_fail_without_writes(self):
        cases = []
        for key,value in (('field_associations',[]),('source_limits',[]),
                ('required_neighbor_chunk_ids',['b'*64]),('applicability_basis_ref','redacted')):
            case = copy.deepcopy(self.receipt); case['chunks'][0]['type_fields'][key] = value; cases.append(case)
        case = copy.deepcopy(self.receipt); case['chunks'][0]['type_fields']['field_associations'][0]['event_sha256'] = '9'*64; cases.append(case)
        for key,value in (('span_order',1),('text','altered'),('page',2),('byte_sha256','9'*64)):
            case = copy.deepcopy(self.receipt); case['chunks'][0]['spans'][0][key] = value; cases.append(case)
        cases += [dict(self.receipt,version_id='ver-other'),dict(self.receipt,review_scope='whole_source')]
        before = self.snapshot()
        for case in cases:
            with self.subTest(case=case),self.assertRaises(StorageError): self.rpc(receipt=case)
        self.assertEqual(self.snapshot(),before)

    def test_relational_chunk_and_span_drift_fail_on_first_call_and_replay(self):
        assignments = [('document_versions',"filename='changed.pdf'"),
            ('document_versions',"issuer='{}'::jsonb"),('chunks',"content_review='reviewed'"),
            ('chunks',"edition_id=null"),('chunks',"type_fields=type_fields || '{\"extra\":true}'::jsonb"),
            ('source_spans',"text='altered span'")]
        for replay in (False,True):
            for table,assignment in assignments:
                with self.subTest(replay=replay,table=table,assignment=assignment):
                    # Roll back fixture mutations and any successful setup, retaining the same initial rows.
                    setup = ''
                    if replay:
                        setup = 'select public.record_source_partial_review('+sql_literal(json.dumps(self.current))+'::jsonb,'+sql_literal(json.dumps(self.receipt))+'::jsonb);'
                    sql = 'begin; '+setup+' update public.'+table+' set '+assignment+';'
                    sql += ' select public.record_source_partial_review('+sql_literal(json.dumps(self.current))+'::jsonb,'+sql_literal(json.dumps(self.receipt))+'::jsonb); rollback;'
                    before = self.snapshot()
                    with self.assertRaises(AssertionError): self.db.execute(sql)
                    self.assertEqual(self.snapshot(),before)

    def test_missing_conflicting_receipt_and_immutable_update_delete_truncate(self):
        self.rpc(); before = self.snapshot()
        for statement in ("update public.source_partial_reviews set receipt='{}'::jsonb;",
                'delete from public.source_partial_reviews;','truncate public.source_partial_reviews;'):
            with self.subTest(statement=statement),self.assertRaises(AssertionError): self.db.execute(statement)
            self.assertEqual(self.snapshot(),before)
        altered = dict(self.receipt,compiler_label='another compiler')
        with self.assertRaises(StorageError): self.rpc(receipt=altered)
        # Corrupt only this disposable fixture as postgres; ordinary callers cannot remove the receipt.
        self.db.execute('alter table public.source_partial_reviews disable trigger user; delete from public.source_partial_reviews; alter table public.source_partial_reviews enable trigger user;')
        before = self.snapshot()
        with self.assertRaises(StorageError): self.rpc()
        self.assertEqual(self.snapshot(),before)

    def test_runtime_acl_rls_and_invoker_privileges(self):
        self.rpc()
        for role in ('anon','authenticated'):
            for statement in ('select * from public.source_partial_reviews;',
                    'select public.record_source_partial_review(null,null);'):
                with self.subTest(role=role,statement=statement),self.assertRaises(AssertionError):
                    self.db.execute('begin; set local role '+role+'; '+statement+' rollback;')
            self.db.execute('grant select,insert,update,delete on public.source_partial_reviews to '+role+';')
            self.assertEqual(self.db.json('begin;set local role '+role+";select count(*) from public.source_partial_reviews;commit;"),0)
            with self.assertRaises(AssertionError):
                self.db.execute('begin;set local role '+role+";insert into public.source_partial_reviews(version_id,evidence_id,receipt) values ('ver-registration-one','forbidden','{}');commit;")
        attrs = self.db.json("select jsonb_build_object('definer',prosecdef,'public',exists(select 1 from aclexplode(proacl) a where a.grantee=0 and a.privilege_type='EXECUTE')) from pg_proc where proname='record_source_partial_review';")
        self.assertEqual(attrs,dict(definer=False,public=False))
        for privilege in ('UPDATE','DELETE','TRUNCATE'):
            self.assertFalse(self.db.json("select to_jsonb(has_table_privilege('service_role','public.source_partial_reviews',"+sql_literal(privilege)+'));'))

    def test_concurrent_identical_and_competing_receipts_preserve_history(self):
        for same in (True,False):
            other = copy.deepcopy(self.receipt)
            if not same: other['evidence']['evidence_id'] = 'competing-review'
            def record(receipt):
                try: return self.rpc(receipt=receipt)
                except StorageError: return None
            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(pool.map(record,[self.receipt,other]))
            self.assertEqual(sum(r is not None for r in results),2 if same else 1)
            self.assertEqual(len(self.client.select('source_partial_reviews',role='admin')),1)
            if same:
                self.db.execute('alter table public.source_partial_reviews disable trigger user; delete from public.source_partial_reviews; alter table public.source_partial_reviews enable trigger user; update public.document_versions set content_review_state=\'pending\',source_register='+sql_literal(json.dumps(self.current))+'::jsonb;')

    def test_legacy_and_published_sources_remain_immutable(self):
        before = self.snapshot()
        self.db.execute('update public.document_versions set source_register=null;')
        with self.assertRaises(StorageError): self.rpc()
        self.db.execute('update public.document_versions set source_register='+sql_literal(json.dumps(self.current))+'::jsonb;')
        self.assertEqual(self.snapshot(),before)
        from backend.bintanong_storage.release import ReleaseManager
        fixture = FIXTURE.replace("repeat('a',64)","repeat('c',64)").replace("repeat('b',64)","repeat('d',64)")
        self.db.execute(fixture+'commit;')
        ReleaseManager(self.client).activate_release('release-test1')
        # Add the selected source to an already-published fixture using a disabled test-only trigger.
        self.db.execute("alter table public.release_document_versions disable trigger user; insert into public.release_document_versions values ('release-test1','ver-registration-one'); alter table public.release_document_versions enable trigger user;")
        before = self.snapshot()
        with self.assertRaises(StorageError): self.rpc()
        self.assertEqual(self.snapshot(),before)

    def test_timestamp_parity_wide_offsets_and_fraction_text_are_preserved(self):
        self.receipt['evidence']['recorded_at'] = '2026-10-16T10:00:00.123456789+23:59'
        self.receipt['source_events'][0]['recorded_at'] = '2026-10-13T08:00:00.123456789-23:59'
        expected = SourceDocumentVersion.parse(partial_record(self.current,self.receipt))
        self.assertEqual(self.loader.record(self.current,self.receipt),expected)
        self.assertEqual(self.client.select('source_partial_reviews',role='admin')[0]['receipt'],self.receipt)

    def test_late_source_failure_rolls_back_receipt_insert(self):
        self.db.execute("create function public.synthetic_c1_fail() returns trigger language plpgsql as $$ begin raise exception 'synthetic late source failure'; end; $$; create trigger synthetic_c1_fail before update on public.document_versions for each row execute function public.synthetic_c1_fail();")
        before = self.snapshot()
        with self.assertRaisesRegex(StorageError,'synthetic late source failure'): self.rpc()
        self.assertEqual(self.snapshot(),before)

    def test_waiting_receipt_rechecks_snapshot_after_concurrent_writer(self):
        # An advisory-lock sentinel signals that the writer owns the publication
        # lock before the reader starts, avoiding scheduler-dependent assertions.
        marker = 91736402
        writer_sql = "begin; select bintanong_private.publication_lock(); select pg_advisory_xact_lock("+str(marker)+");select pg_sleep(0.8);update public.source_spans set text='concurrent changed span';commit;"
        with ThreadPoolExecutor(max_workers=1) as pool:
            writer = pool.submit(self.db.execute,writer_sql)
            deadline = time.monotonic()+10
            while not self.db.json("select to_jsonb(exists(select 1 from pg_locks where locktype='advisory' and objid="+str(marker)+" and granted));"):
                if time.monotonic()>deadline: self.fail('writer did not acquire test marker')
                time.sleep(0.02)
            with self.assertRaises(StorageError): self.rpc()
            writer.result()
        self.assertEqual(self.client.select('source_partial_reviews',role='admin'),[])
        self.assertEqual(self.client.select('document_versions',role='admin')[0]['source_register'],self.current)

    def test_stale_source_receipt_duplicate_ids_and_unreferenced_events_fail(self):
        cases = []
        for key in ('evidence','source_events','chunks'):
            case = copy.deepcopy(self.receipt)
            if key=='evidence': case[key]['evidence_id']=self.current['evidence'][0]['evidence_id']
            else: case[key].append(copy.deepcopy(case[key][0]))
            cases.append(case)
        case = copy.deepcopy(self.receipt)
        case['source_events'].append(dict(case['source_events'][0],event_sha256='9'*64)); cases.append(case)
        before = self.snapshot()
        for case in cases:
            with self.subTest(case=case),self.assertRaises(StorageError): self.rpc(receipt=case)
        stale = dict(self.current,filename='other.pdf')
        with self.assertRaises(StorageError): self.rpc(current=stale)
        for key in ('verification_state','approval_state','content_review_state','acquisition_state'):
            current = copy.deepcopy(self.current); current[key]['state']='reviewed'
            with self.subTest(key=key),self.assertRaises(StorageError): self.rpc(current=current)
        self.assertEqual(self.snapshot(),before)

    def test_changed_chunk_text_cannot_hide_behind_a_retained_content_hash(self):
        for replay in (False,True):
            for column in ('text','source_text'):
                with self.subTest(replay=replay,column=column):
                    call = 'select public.record_source_partial_review('+sql_literal(json.dumps(self.current))+'::jsonb,'+sql_literal(json.dumps(self.receipt))+'::jsonb);'
                    sql = 'begin; '+(call if replay else '')+' update public.chunks set '+column+"='changed visible content'; "+call+' rollback;'
                    before = self.snapshot()
                    with self.assertRaises(AssertionError): self.db.execute(sql)
                    self.assertEqual(self.snapshot(),before)
