"""Synthetic A2 byte verification after C1; no institutional approval fixtures."""
import copy
from concurrent.futures import ThreadPoolExecutor
import json
import time
import unittest

from backend.bintanong_contracts.governance import SourceDocumentVersion
from backend.bintanong_storage.client import StorageError, PermissionDeniedError
from backend.bintanong_storage.loader import BatchKnowledgeLoader
from backend.bintanong_storage.source_registration import SourceRegistrationLoader
from backend.bintanong_storage.source_partial_review import SourcePartialReviewLoader
from backend.bintanong_storage.release import ReleaseManager
from backend.bintanong_storage.source_acquisition import SourceAcquisitionLoader
from tests.test_storage_source_acquisition import byte_check
from tests.test_storage_source_partial_review import current_source, partial_record, receipt_for
from tests.test_storage_source_registration import pending_version, document_record
from tests.storage_database import StorageDatabase, DatabaseStorageClient, sql_literal, FIXTURE


def partial_source():
    current = current_source()
    return partial_record(current, receipt_for(current))


def subsequent_check(current=None):
    check = byte_check(current or partial_source())
    check['evidence'].update(evidence_id='synthetic-check-two', recorded_at='2026-10-16T12:00:00Z')
    return check


def verified_record(current, check):
    result = copy.deepcopy(current)
    result['evidence'].append(copy.deepcopy(check['evidence']))
    result['acquisition_state'] = dict(state='verified', evidence_ref=check['evidence']['evidence_id'])
    return result


class RecordingClient:
    def __init__(self):
        self.calls, self.response, self.error = [], None, None

    def rpc(self, name, params, role):
        self.calls.append((name, copy.deepcopy(params), role))
        if self.error:
            raise self.error
        return self.response if self.response is not None else verified_record(
            params['p_expected_register'], params['p_check'])


class AcquisitionVerificationLoaderTests(unittest.TestCase):
    def setUp(self):
        self.current = partial_source()
        self.check = subsequent_check(self.current)
        self.client = RecordingClient()
        self.loader = SourceAcquisitionLoader(self.client)

    def verify(self, current=None, check=None):
        self.assertTrue(callable(getattr(self.loader, 'verify', None)), 'A2 verify method missing')
        return self.loader.verify(self.current if current is None else current,
                                  self.check if check is None else check)

    def test_exact_admin_call_return_and_input_history_preservation(self):
        before = copy.deepcopy((self.current,self.check))
        for current in (self.current,SourceDocumentVersion.parse(self.current)):
            result = self.verify(current)
            self.assertEqual(result, SourceDocumentVersion.parse(verified_record(self.current,self.check)))
            self.assertEqual(self.client.calls[-1],('verify_source_acquisition',dict(
                p_expected_register=self.current,p_check=self.check),'admin'))
        self.assertEqual((self.current,self.check), before)

    def test_envelope_and_evidence_fail_before_rpc(self):
        cases = [[],{},dict(self.check,extra=True),dict(self.check,version_id='ver-other'),
            dict(self.check,source_sha256='9'*64),dict(self.check,acquisition_locators=[])]
        for key in self.check:
            cases.append({k:v for k,v in self.check.items() if k != key})
        for key,value in (('kind','content_review_record'),('recorded_by','researcher'),
                ('recorded_by','issuing_office'),('authorization_ref','forbidden'),
                ('recorded_at','2026-02-30T00:00:00Z'),('recorded_at','2026-10-16T08:01:21Z'),
                ('evidence_id',''),('evidence_id',' '),('evidence_id','synthetic-check-one')):
            case = copy.deepcopy(self.check); case['evidence'][key] = value; cases.append(case)
        for check in cases:
            with self.subTest(check=check),self.assertRaises(ValueError):
                self.verify(check=check)
        self.assertEqual(self.client.calls,[])

    def test_lifecycle_boundary_including_pending_content_rejected(self):
        cases = [current_source(),verified_record(self.current,self.check)]
        for field,value in (('verification_state','observed'),('approval_state','requested'),
                ('content_review_state','reviewed')):
            case = copy.deepcopy(self.current); case[field]['state'] = value; cases.append(case)
        for current in cases:
            with self.subTest(current=current),self.assertRaises(ValueError):self.verify(current)
        self.assertEqual(self.client.calls,[])

    def test_specific_cited_observation_controls_time_not_unrelated_earlier_check(self):
        old = dict(self.current['evidence'][0], evidence_id='unrelated-old',recorded_at='2026-10-01T00:00:00Z')
        self.current['evidence'].insert(0,old)
        self.check['evidence']['recorded_at'] = '2026-10-15T00:00:00Z'
        with self.assertRaises(ValueError):self.verify()
        self.assertEqual(self.client.calls,[])

    def test_equivalent_and_equal_instants_wide_offsets_and_fraction_keep_text(self):
        for moment in ('2026-10-16T08:01:22Z','2026-10-16T16:01:22+08:00',
                '2026-10-17T08:00:22+23:59','2026-10-16T08:01:22.123456789Z'):
            with self.subTest(moment=moment):
                self.check['evidence']['recorded_at'] = moment
                self.assertEqual(self.verify().evidence[-1].recorded_at,moment)
        self.check['evidence']['recorded_by'] = 'reviewer'
        self.assertEqual(self.verify().acquisition_state.state,'verified')

    def test_locator_order_and_unused_history_are_preserved(self):
        self.current['acquisition_locators'].append('synthetic:second')
        self.current['evidence'].insert(0,dict(self.current['evidence'][0],evidence_id='unused'))
        self.check = subsequent_check(self.current)
        result = self.verify().model_dump(mode='json')
        self.assertEqual(result['evidence'][:-1],self.current['evidence'])
        self.check['acquisition_locators'].reverse()
        with self.assertRaises(ValueError):self.verify()
        self.assertEqual(len(self.client.calls),1)

    def test_invalid_rpc_returns_and_storage_failure_do_not_retry(self):
        for response in ([],{},self.current,dict(verified_record(self.current,self.check),filename='changed.pdf')):
            with self.subTest(response=response),self.assertRaises(ValueError):
                self.client.response = response; self.verify()
        self.client.error = StorageError('synthetic timeout')
        before = len(self.client.calls)
        with self.assertRaises(StorageError):self.verify()
        self.assertEqual(len(self.client.calls),before+1)


def seed_partial(client):
    initial = pending_version()
    SourceRegistrationLoader(client).load_versions([initial],[document_record()])
    observed = SourceAcquisitionLoader(client).observe(initial,byte_check(initial)).model_dump(mode='json')
    receipt = receipt_for(observed)
    snapshot = receipt['chunks'][0]
    chunk = dict(chunk_id=snapshot['chunk_id'],chunk_type='policy',document_id=observed['document_id'],
        version_id=observed['version_id'],edition_id=observed['edition_id'],byte_sha256=observed['byte_sha256'],
        source_verification='pending',content_review='pending',text=snapshot['spans'][0]['text'],
        source_text=snapshot['spans'][0]['text'],content_hash=snapshot['content_hash'],
        spans=snapshot['spans'],type_fields=snapshot['type_fields'])
    BatchKnowledgeLoader(client).load_chunks([chunk])
    current = SourcePartialReviewLoader(client).record(observed,receipt).model_dump(mode='json')
    return current,receipt


class AcquisitionVerificationDatabaseTests(unittest.TestCase):
    def setUp(self):
        self.db = StorageDatabase()
        self.addCleanup(self.db.close)
        self.client = DatabaseStorageClient(self.db)
        self.current,self.receipt = seed_partial(self.client)
        self.check = subsequent_check(self.current)
        self.loader = SourceAcquisitionLoader(self.client)

    def rpc(self, current=..., check=...):
        return self.client.rpc('verify_source_acquisition',dict(
            p_expected_register=self.current if current is ... else current,
            p_check=self.check if check is ... else check),role='admin')

    def snapshot(self):
        return {t:self.client.select(t,role='admin') for t in (
            'document_versions','chunks','source_spans','source_partial_reviews','selected_release_reviews',
            'knowledge_releases','release_document_versions','active_release')}

    def restore(self, current=None):
        current = self.current if current is None else current
        self.db.execute("update public.document_versions set acquisition_state="+
            sql_literal(current['acquisition_state']['state'])+",source_register="+
            sql_literal(json.dumps(current))+"::jsonb where version_id="+sql_literal(self.current['version_id'])+";")

    def test_persist_and_replay_preserve_all_other_data_without_second_update(self):
        before = self.snapshot()
        result = self.loader.verify(self.current,self.check)
        after = self.snapshot()
        self.assertEqual(result.model_dump(mode='json'),verified_record(self.current,self.check))
        self.assertEqual(after['document_versions'][0]['source_register'],result.model_dump(mode='json'))
        self.assertEqual(after['document_versions'][0]['acquisition_state'],'verified')
        for key in before:
            if key != 'document_versions':self.assertEqual(before[key],after[key])
        self.assertEqual({k:v for k,v in before['document_versions'][0].items() if k not in ('acquisition_state','source_register')},
                         {k:v for k,v in after['document_versions'][0].items() if k not in ('acquisition_state','source_register')})
        self.db.execute("create function public.reject_a2_update() returns trigger language plpgsql as $$ begin raise exception 'unexpected replay update'; end $$; create trigger reject_a2_update before update on public.document_versions for each row execute function public.reject_a2_update();")
        self.assertEqual(self.loader.verify(self.current,self.check),result)
        self.assertEqual(self.snapshot(),after)

    def test_direct_malformed_envelopes_and_evidence_reject_without_changes(self):
        cases = [(None,self.check),([],self.check),(self.current,None),(self.current,[]),
            (self.current,dict(self.check,extra=True))]
        for key in self.check:
            cases.append((self.current,{k:v for k,v in self.check.items() if k != key}))
            for value in (None,False,0,{},[]):cases.append((self.current,dict(self.check,**{key:value})))
        for key in self.check['evidence']:
            case = copy.deepcopy(self.check); del case['evidence'][key]; cases.append((self.current,case))
        for key,value in (('evidence_id',''),('evidence_id',' '),('evidence_id','synthetic-check-one'),
                ('evidence_id','synthetic-partial-review'),('recorded_by','researcher'),('recorded_by','issuing_office'),
                ('kind','issuing_office_confirmation'),('authorization_ref','forbidden'),('recorded_at',None),
                ('recorded_at','2026-02-30T00:00:00Z'),('recorded_at','2026-10-16T25:00:00Z'),
                ('recorded_at','2026-10-16T00:00:00+24:00'),('recorded_at','1999-10-16T00:00:00Z'),
                ('recorded_at','2026-10-15T00:00:00Z')):
            case = copy.deepcopy(self.check); case['evidence'][key] = value; cases.append((self.current,case))
        before = self.snapshot()
        for current,check in cases:
            with self.subTest(current=current,check=check),self.assertRaises(StorageError):self.rpc(current,check)
        self.assertEqual(self.snapshot(),before)

    def test_specific_cited_a1_and_lifecycle_guards_on_direct_rpc(self):
        for state in ('pending','verified','mismatch'):
            case = copy.deepcopy(self.current); case['acquisition_state']['state'] = state
            with self.subTest(state=state),self.assertRaises(StorageError):self.rpc(case)
        cases=[]
        for field,state in (('verification_state','verified'),('approval_state','approved'),
                ('content_review_state','pending'),('content_review_state','reviewed')):
            case=copy.deepcopy(self.current);case[field]['state']=state;cases.append(case)
        case=copy.deepcopy(self.current);case['acquisition_state']['evidence_ref']='missing';cases.append(case)
        for key,value in (('kind','content_review_record'),('recorded_by','issuing_office'),
                ('authorization_ref','forbidden'),('recorded_at','2026-02-30T00:00:00Z')):
            case=copy.deepcopy(self.current);case['evidence'][0][key]=value;cases.append(case)
        for case in cases:
            # Store each adversarial register too, so full-row CAS alone cannot mask a missing guard.
            self.restore(case)
            before=self.snapshot()
            with self.subTest(case=case),self.assertRaises(StorageError):self.rpc(case)
            self.assertEqual(self.snapshot(),before)
            self.restore()
        case=copy.deepcopy(self.current)
        case['evidence'].insert(0,dict(case['evidence'][0],evidence_id='unrelated',recorded_at='2026-10-01T00:00:00Z'))
        self.restore(case)
        check=copy.deepcopy(self.check);check['evidence']['recorded_at']='2026-10-15T00:00:00Z'
        with self.assertRaises(StorageError):self.rpc(case,check)

    def test_timestamp_parity_equal_offset_fraction_and_specific_observation(self):
        for prior,new in (
                ('2026-10-16T08:01:22Z','2026-10-16T08:01:22Z'),
                ('2026-10-16T08:01:22Z','2026-10-16T16:01:22+08:00'),
                ('2026-10-16T08:01:22Z','2026-10-17T08:00:22+23:59'),
                ('2026-10-16T08:01:22.123456789Z','2026-10-16T08:01:22.123456001Z'),
                ('2026-10-16T00:00:00-23:59','2026-10-17T23:58:00+23:59')):
            current=copy.deepcopy(self.current);current['evidence'][0]['recorded_at']=prior
            check=copy.deepcopy(self.check);check['evidence']['recorded_at']=new
            self.restore(current)
            with self.subTest(prior=prior,new=new):
                self.assertEqual(self.loader.verify(current,check),SourceDocumentVersion.parse(verified_record(current,check)))
            self.restore()

    def test_conflicts_concurrency_and_stale_replay_do_not_downgrade(self):
        for same in (True,False):
            other=copy.deepcopy(self.check)
            if not same:other['evidence']['evidence_id']='competing-check'
            def call(check):
                try:return self.rpc(check=check)
                except StorageError:return None
            with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(call,[self.check,other]))
            self.assertEqual(sum(r is not None for r in results),2 if same else 1)
            before=self.snapshot()
            stale=dict(self.current,filename='stale.pdf')
            with self.assertRaises(StorageError):self.rpc(stale)
            with self.assertRaises(StorageError):
                SourcePartialReviewLoader(self.client).record(current_source(),self.receipt)
            self.assertEqual(self.snapshot(),before)
            self.restore()

    def test_relational_drift_first_and_replay_are_rejected(self):
        for replay in (False,True):
            for assignment in ("filename='drift.pdf'","verification_state='verified'","issuer='{}'::jsonb",
                    "acquisition_state='pending'"):
                if replay:self.rpc()
                original=self.client.select('document_versions',role='admin')[0]
                self.db.execute('update public.document_versions set '+assignment+';')
                before=self.snapshot()
                with self.subTest(replay=replay,assignment=assignment),self.assertRaises(StorageError):self.rpc()
                self.assertEqual(self.snapshot(),before)
                self.db.execute('update public.document_versions set filename='+sql_literal(original['filename'])+
                    ',verification_state='+sql_literal(original['verification_state'])+',issuer='+
                    sql_literal(json.dumps(original['issuer']))+'::jsonb;')
                self.restore()

    def test_missing_legacy_and_published_versions_are_rejected(self):
        missing=dict(self.current,version_id='ver-missing')
        with self.assertRaises(StorageError):self.rpc(missing,subsequent_check(missing))
        self.db.execute('update public.document_versions set source_register=null;')
        with self.assertRaises(StorageError):self.rpc()
        self.restore()
        # History need not be the active pointer for the published-membership guard.
        self.db.execute(FIXTURE.replace("repeat('a',64)","repeat('c',64)")+"commit;")
        ReleaseManager(self.client).activate_release('release-test1')
        expected=dict(self.current,version_id='ver-test1')
        with self.assertRaisesRegex(StorageError,'Published'):self.rpc(expected,subsequent_check(expected))

    def test_runtime_roles_and_public_cannot_execute_and_sources_stay_hidden(self):
        self.rpc()
        for role in ('anon','authenticated'):
            client=DatabaseStorageClient(self.db,runtime_role=role)
            with self.subTest(role=role),self.assertRaises(PermissionDeniedError):
                client.rpc('verify_source_acquisition',dict(p_expected_register=self.current,p_check=self.check))
            for table in ('documents','document_versions','chunks','source_spans','source_partial_reviews'):
                with self.subTest(role=role,table=table):
                    if table=='source_partial_reviews':
                        with self.assertRaisesRegex(AssertionError,'permission denied'):client.select(table)
                    else:self.assertEqual(client.select(table),[])
        attrs=self.db.json("select jsonb_build_object('definer',prosecdef,'public',exists(select 1 from aclexplode(proacl) x where x.grantee=0 and x.privilege_type='EXECUTE')) from pg_proc where proname='verify_source_acquisition';")
        self.assertEqual(attrs,dict(definer=False,public=False))

    def test_publication_lock_blocks_and_transaction_failure_rolls_back(self):
        def hold_lock():
            return self.db.execute('begin; select bintanong_private.publication_lock(); select pg_sleep(1); commit;')
        with ThreadPoolExecutor(max_workers=1) as pool:
            future=pool.submit(hold_lock)
            # Observe the lock holder rather than assume a sleep acquired the lock.
            deadline=time.monotonic()+5
            while time.monotonic()<deadline:
                if self.db.json("select to_jsonb(exists(select 1 from pg_locks where locktype='advisory' and granted and database=(select oid from pg_database where datname=current_database())));"):break
            else:self.fail('publication lock was not acquired')
            started=time.monotonic();self.rpc();elapsed=time.monotonic()-started
            future.result()
        self.assertGreater(elapsed,.1)
        self.restore();before=self.snapshot()
        sql='begin; set local role service_role; select public.verify_source_acquisition('+sql_literal(json.dumps(self.current))+'::jsonb,'+sql_literal(json.dumps(self.check))+"::jsonb); select 1/0; commit;"
        with self.assertRaises(AssertionError):self.db.execute(sql)
        self.assertEqual(self.snapshot(),before)
