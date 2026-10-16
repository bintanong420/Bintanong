"""Synthetic A2 byte verification after C1; no institutional approval fixtures."""
import copy
import unittest

from backend.bintanong_contracts.governance import SourceDocumentVersion
from backend.bintanong_storage.client import StorageError
from backend.bintanong_storage.source_acquisition import SourceAcquisitionLoader
from tests.test_storage_source_acquisition import byte_check
from tests.test_storage_source_partial_review import current_source, partial_record, receipt_for


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
