"""Synthetic scoped C1 receipts, never institutional source approvals."""
import copy
import importlib
import importlib.util
import unittest

from backend.bintanong_contracts.governance import SourceDocumentVersion
from backend.bintanong_storage.client import StorageError
from tests.test_storage_source_acquisition import byte_check, observed_record
from tests.test_storage_source_registration import pending_version


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
