"""Synthetic A1-only source observations; no institutional authority fixtures."""
import copy
from concurrent.futures import ThreadPoolExecutor
import importlib
import importlib.util
import json
import unittest

from backend.bintanong_contracts.governance import SourceDocumentVersion
from backend.bintanong_storage.client import StorageError
from backend.bintanong_storage.client import PermissionDeniedError
from backend.bintanong_storage.source_registration import SourceRegistrationLoader
from backend.bintanong_storage.source_acquisition import SourceAcquisitionLoader
from tests.storage_database import DatabaseStorageClient, StorageDatabase, FIXTURE, sql_literal
from tests.test_storage_source_registration import pending_version, document_record


def byte_check(version=None):
    version = version or pending_version()
    return dict(version_id=version['version_id'], source_sha256=version['byte_sha256'],
        acquisition_locators=list(version['acquisition_locators']),
        evidence=dict(evidence_id='synthetic-check-one', kind='byte_hash_check',
            recorded_by='system', recorded_at='2026-10-16T08:01:22Z', authorization_ref=None))


def observed_record(current, check):
    result = copy.deepcopy(current)
    result['evidence'].append(copy.deepcopy(check['evidence']))
    result['acquisition_state'] = dict(state='observed', evidence_ref=check['evidence']['evidence_id'])
    return result


def loader_class(test):
    module = 'backend.bintanong_storage.source_acquisition'
    test.assertIsNotNone(importlib.util.find_spec(module), 'A1 acquisition loader is not implemented')
    return importlib.import_module(module).SourceAcquisitionLoader


class RecordingClient:
    def __init__(self):
        self.calls = []
        self.response = None
        self.error = None

    def rpc(self, name, params, role):
        self.calls.append((name, copy.deepcopy(params), role))
        if self.error:
            raise self.error
        return self.response if self.response is not None else observed_record(params['p_expected_register'], params['p_check'])


class AcquisitionLoaderTests(unittest.TestCase):
    def setUp(self):
        self.current = pending_version()
        self.check = byte_check(self.current)
        self.client = RecordingClient()

    def test_exact_administrative_request_and_validated_return_without_input_mutation(self):
        before = copy.deepcopy((self.current, self.check))
        for current in (self.current, SourceDocumentVersion.parse(self.current)):
            result = loader_class(self)(self.client).observe(current, self.check)
            self.assertIsInstance(result, SourceDocumentVersion)
            self.assertEqual(result.model_dump(mode='json'), observed_record(self.current, self.check))
            self.assertEqual(self.client.calls[-1], ('observe_source_acquisition',
                dict(p_expected_register=self.current, p_check=self.check), 'admin'))
        self.assertEqual((self.current, self.check), before)

    def test_invalid_envelopes_fail_before_rpc(self):
        checks = [None, [], {}, dict(self.check, extra=True),
            dict(self.check, version_id='ver-other'), dict(self.check, source_sha256='9'*64),
            dict(self.check, acquisition_locators=[]), dict(self.check, acquisition_locators=None)]
        for field, value in (('kind','issuing_office_confirmation'), ('recorded_by','issuing_office'),
                ('recorded_at','2026-02-30T00:00:00Z'), ('recorded_at',None),
                ('authorization_ref','not-allowed'), ('evidence_id','')):
            check = copy.deepcopy(self.check)
            check['evidence'][field] = value
            checks.append(check)
        for key in self.check:
            checks.append({k:v for k,v in self.check.items() if k != key})
        for check in checks:
            with self.subTest(check=check), self.assertRaises(ValueError):
                loader_class(self)(self.client).observe(self.current, check)
        self.assertEqual(self.client.calls, [])

    def test_only_initial_states_and_new_evidence_ids_are_accepted(self):
        cases = [observed_record(self.current, self.check), dict(self.current, approval_id='not-allowed')]
        duplicate = copy.deepcopy(self.current)
        duplicate['evidence'].append(copy.deepcopy(self.check['evidence']))
        cases.append(duplicate)
        for field in ('verification_state','approval_state','content_review_state'):
            changed = copy.deepcopy(self.current)
            changed[field] = dict(state='observed', evidence_ref=None)
            cases.append(changed)
        for current in cases:
            with self.subTest(current=current), self.assertRaises(ValueError):
                loader_class(self)(self.client).observe(current, self.check)
        self.assertEqual(self.client.calls, [])

    def test_retains_preexisting_evidence_and_locator_order(self):
        self.current['evidence'] = [dict(self.check['evidence'], evidence_id='prior-check')]
        self.current['acquisition_locators'].append('synthetic:registration/second')
        self.check = byte_check(self.current)
        result = loader_class(self)(self.client).observe(self.current, self.check)
        self.assertEqual(result.model_dump(mode='json')['evidence'],
            self.current['evidence'] + [self.check['evidence']])
        swapped = dict(self.check, acquisition_locators=list(reversed(self.check['acquisition_locators'])))
        before = len(self.client.calls)
        with self.assertRaises(ValueError):
            loader_class(self)(self.client).observe(self.current, swapped)
        self.assertEqual(len(self.client.calls), before)

    def test_rejects_invalid_or_altered_rpc_return(self):
        expected = observed_record(self.current, self.check)
        for response in ([], {}, self.current, dict(expected, filename='other.pdf')):
            with self.subTest(response=response), self.assertRaises(ValueError):
                self.client.response = response
                loader_class(self)(self.client).observe(self.current, self.check)

    def test_storage_failure_propagates_without_retry(self):
        self.client.error = StorageError('synthetic transport failure')
        with self.assertRaises(StorageError):
            loader_class(self)(self.client).observe(self.current, self.check)
        self.assertEqual(len(self.client.calls), 1)


class AcquisitionDatabaseTests(unittest.TestCase):
    def setUp(self):
        self.db = StorageDatabase()
        self.addCleanup(self.db.close)
        self.client = DatabaseStorageClient(self.db)
        self.current = pending_version()
        self.check = byte_check(self.current)
        self.registration = SourceRegistrationLoader(self.client)
        self.registration.load_versions([self.current], [document_record()])
        self.loader = SourceAcquisitionLoader(self.client)

    def rows(self):
        return self.client.select('document_versions', role='admin')

    def rpc(self, current=None, check=None):
        return self.client.rpc('observe_source_acquisition', dict(
            p_expected_register=self.current if current is None else current,
            p_check=self.check if check is None else check), role='admin')

    def test_persisted_record_and_exact_replay_preserve_all_other_columns(self):
        before = self.rows()[0]
        result = self.loader.observe(self.current, self.check)
        after = self.rows()[0]
        self.assertEqual(after['source_register'], result.model_dump(mode='json'))
        self.assertEqual(after['acquisition_state'], 'observed')
        self.assertEqual({k:v for k,v in before.items() if k not in ('source_register','acquisition_state')},
                         {k:v for k,v in after.items() if k not in ('source_register','acquisition_state')})
        self.assertEqual(self.loader.observe(self.current, self.check), result)
        self.assertEqual(self.rows()[0], after)
        with self.assertRaises(StorageError):
            self.registration.load_versions([self.current], [document_record()])
        with self.assertRaises(ValueError):
            self.registration.load_versions([result], [document_record()])
        self.assertEqual(self.rows()[0], after)

    def test_retains_unused_preexisting_evidence(self):
        current = pending_version('two')
        check = byte_check(current)
        current['evidence'] = [dict(check['evidence'], evidence_id='old-observation')]
        self.registration.load_versions([current], [document_record()])
        out = self.loader.observe(current, check).model_dump(mode='json')
        self.assertEqual(out['evidence'], current['evidence']+[check['evidence']])
        self.assertEqual(self.loader.observe(current, check).model_dump(mode='json'), out)

    def test_preserves_valid_contract_timestamp_with_wide_offset_and_fraction(self):
        self.check['evidence']['recorded_at'] = '2026-10-16T08:01:22.123456789+23:59'
        expected = SourceDocumentVersion.parse(observed_record(self.current,self.check))
        self.assertEqual(self.loader.observe(self.current,self.check), expected)

    def test_direct_rpc_rejects_malformed_observations_without_updates(self):
        calls = [(None,self.check), ([],self.check), (self.current,None),
            (self.current,[]), (self.current,{}), (self.current,dict(self.check,extra=True)),
            (self.current,dict(self.check,version_id='ver-other')),
            (self.current,dict(self.check,source_sha256='9'*64)),
            (self.current,dict(self.check,acquisition_locators=[]))]
        for key in self.check:
            calls.append((self.current,{k:v for k,v in self.check.items() if k != key}))
        for field,value in (('kind','issuing_office_confirmation'), ('recorded_by','issuing_office'),
                ('recorded_at','2026-02-30T00:00:00Z'),('recorded_at','2026-10-16T25:01:00Z'),
                ('recorded_at','2026-10-16T00:01:00+24:00'),('recorded_at','1999-10-16T00:01:00Z'),
                ('recorded_at',None),('authorization_ref','forbidden'),('evidence_id','')):
            check = copy.deepcopy(self.check)
            check['evidence'][field] = value
            calls.append((self.current,check))
        for field in self.check['evidence']:
            check = copy.deepcopy(self.check)
            del check['evidence'][field]
            calls.append((self.current,check))
        for field in ('verification_state','content_review_state','approval_state'):
            current = copy.deepcopy(self.current)
            current[field]['state'] = 'verified'
            calls.append((current,self.check))
        before = self.rows()
        for current,check in calls:
            with self.subTest(current=current,check=check), self.assertRaises(StorageError):
                self.client.rpc('observe_source_acquisition',dict(p_expected_register=current,p_check=check),role='admin')
        self.assertEqual(self.rows(), before)

    def test_stale_expected_record_and_different_evidence_do_not_overwrite(self):
        self.loader.observe(self.current, self.check)
        before = self.rows()
        stale = dict(self.current, filename='stale.pdf')
        different = copy.deepcopy(self.check)
        different['evidence']['evidence_id'] = 'different-observation'
        for current,check in ((stale,self.check),(self.current,different)):
            with self.subTest(current=current,check=check), self.assertRaises(StorageError):
                self.rpc(current,check)
        self.assertEqual(self.rows(), before)

    def test_relational_drift_is_rejected_on_first_application_and_replay(self):
        for replay in (False,True):
            for assignment in ("filename='changed.pdf'", "acquisition_state='pending'" if replay else "acquisition_state='observed'",
                    "verification_state='verified'", "issuer='{}'::jsonb"):
                with self.subTest(replay=replay,assignment=assignment):
                    if replay:
                        self.loader.observe(self.current,self.check)
                    self.db.execute('update public.document_versions set '+assignment+
                        " where version_id='ver-registration-one';")
                    before = self.rows()
                    with self.assertRaises(StorageError):
                        self.rpc()
                    self.assertEqual(self.rows(), before)
                    self.db.execute("update public.document_versions set filename='one.pdf', acquisition_state='pending',"
                        "verification_state='pending',issuer="+sql_literal(json.dumps(self.current['issuer']))+
                        "::jsonb,source_register="+sql_literal(json.dumps(self.current))+"::jsonb where version_id='ver-registration-one';")

    def test_missing_and_legacy_null_registers_are_rejected(self):
        other = pending_version('two')
        with self.assertRaises(StorageError):
            self.loader.observe(other,byte_check(other))
        self.db.execute("update public.document_versions set source_register=null;")
        before = self.rows()
        with self.assertRaises(StorageError):
            self.rpc()
        self.assertEqual(self.rows(), before)

    def test_both_runtime_roles_cannot_execute_or_read_observed_source(self):
        self.loader.observe(self.current,self.check)
        for role in ('anon','authenticated'):
            with self.subTest(role=role):
                client = DatabaseStorageClient(self.db,runtime_role=role)
                with self.assertRaises(PermissionDeniedError):
                    client.rpc('observe_source_acquisition',dict(p_expected_register=self.current,p_check=self.check))
                self.assertEqual(client.select('document_versions'), [])
        attrs = self.db.json("select jsonb_build_object('definer',prosecdef,'public',exists(select 1 from "
            "aclexplode(proacl) x where x.grantee=0 and x.privilege_type='EXECUTE')) from pg_proc "
            "where proname='observe_source_acquisition';")
        self.assertEqual(attrs,dict(definer=False,public=False))

    def test_concurrent_equal_replays_succeed_and_different_observations_conflict(self):
        for same in (True,False):
            other = copy.deepcopy(self.check)
            if not same:
                other['evidence']['evidence_id'] = 'competing-observation'
            def observe(check):
                try:
                    return self.loader.observe(self.current,check).model_dump(mode='json')
                except StorageError:
                    return None
            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(pool.map(observe,[self.check,other]))
            self.assertEqual(sum(x is not None for x in results), 2 if same else 1)
            stored = self.rows()[0]
            self.assertEqual(len(stored['source_register']['evidence']), 1)
            self.assertIn(stored['source_register'], results)
            self.db.execute("update public.document_versions set acquisition_state='pending',source_register="+
                sql_literal(json.dumps(self.current))+"::jsonb;")

    def test_published_membership_is_rejected_even_with_a_pending_register(self):
        from backend.bintanong_storage.release import ReleaseManager
        self.db.execute(FIXTURE+"update public.document_versions set source_register="+
            sql_literal(json.dumps(self.current))+"::jsonb where version_id='ver-test1'; commit;")
        ReleaseManager(self.client).activate_release('release-test1')
        before = self.rows()
        expected = copy.deepcopy(self.current)
        expected['version_id'] = 'ver-test1'
        check = byte_check(expected)
        with self.assertRaisesRegex(StorageError,'Published'):
            self.rpc(expected,check)
        self.assertEqual(self.rows(), before)
