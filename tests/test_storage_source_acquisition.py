"""Synthetic A1-only source observations; no institutional authority fixtures."""
import copy
import importlib
import importlib.util
import unittest

from backend.bintanong_contracts.governance import SourceDocumentVersion
from backend.bintanong_storage.client import StorageError
from tests.test_storage_source_registration import pending_version


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
