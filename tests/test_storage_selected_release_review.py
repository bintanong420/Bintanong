"""Exact synthetic undergraduate review coverage, without source authority."""
import copy
import importlib
import importlib.util
import unittest

from backend.bintanong_contracts.reviewed_policy_context import serialize_reviewed_fields
from backend.bintanong_contracts.source import SourceSpan, compute_content_hash
from backend.bintanong_contracts.reviewed_policy_context import make_source_limits
from backend.bintanong_contracts.reviewed_record_groups import make_record_manifest
from backend.bintanong_storage.client import StorageError
from tests.test_storage_source_partial_review import current_source, receipt_for


def selected_fixture():
    source = current_source()
    partial = receipt_for(source)
    chunk = partial['chunks'][0]
    span = chunk['spans'][0]
    span['locator'].update(table_index=None, cell_ids=[], item_ids=[], ref=None)
    span.update(bbox=[1, 1, 10, 10], bbox_origin='TOPLEFT', page_size=[100, 100],
        extraction=dict(source_kind='synthetic', resolution_method='deterministic',
            repair_id=None, ocr_confidence=None))
    parsed = SourceSpan.parse(dict(schema_version=SourceSpan.SCHEMA_VERSION,
        **{k:v for k,v in span.items() if k not in ('chunk_id','span_order')})).model_dump(mode='json')
    span.update({k:parsed[k] for k in span if k in parsed})
    fields = chunk['type_fields']; fields['source_limits'] = []
    text = serialize_reviewed_fields(fields['field_associations'], [])
    chunk['content_hash'] = compute_content_hash(span['text'], text)
    selected = dict(receipt_format='selected-release-review-v1', review_scope_id='9'*64,
        supported_scope='undergraduate_academic_affairs',
        decision=dict(evidence_id='synthetic-selected-review', reviewer_label=partial['reviewer_label'],
            compiler_label='Synthetic compiler', recorded_at='2026-10-16T11:00:00Z',
            timestamp_meaning='Compilation recording time, not exact chat time',
            owner_response='Complete for this exact selection, with its limits.',
            decision_document='plans/synthetic-review.md', acceptance_record_sha256='9'*64,
            coverage_inventory_sha256='6'*64, draft_chunks_sha256='5'*64),
        sources=[dict(version_id=source['version_id'], source_sha256=source['byte_sha256'],
            partial_review_evidence_id=partial['evidence']['evidence_id'])],
        chunks=[copy.deepcopy(chunk)])
    return source, partial, selected, text


def loader(test, client):
    name = 'backend.bintanong_storage.selected_release_review'
    test.assertIsNotNone(importlib.util.find_spec(name), 'Selected review loader is not implemented')
    return importlib.import_module(name).SelectedReleaseReviewLoader(client)


def add_record_group(partial):
    """Synthetic two-part source defect whose full visible fields stay together."""
    original = dict(gap_id='synthetic-conflict', issue='conflicting_deadlines',
        affected_claims=['applicable synthetic deadline'], field_names=['first','second'],
        visible_text=['First visible condition','Second visible condition'],
        locator=dict(physical_pages=[1,2],field='first,second'))
    manifest = make_record_manifest({'gaps':[original]},[['first'],['second']])
    initial = partial['chunks'][0]; parts = []
    for i,name in enumerate(('first','second')):
        chunk = copy.deepcopy(initial); chunk['chunk_id'] = ('a' if i==0 else 'b')*64
        span = chunk['spans'][0]; span.update(chunk_id=chunk['chunk_id'],page=i+1,text=original['visible_text'][i])
        fields = chunk['type_fields']; fields['reading_id'] = 'synthetic-record::part:'+str(i)
        field = fields['field_associations'][0]; field.update(name=name,value=span['text'])
        fields['required_neighbor_chunk_ids'] = [('b' if i==0 else 'a')*64]
        fields['service_group'] = dict(logical_step_id='synthetic-record',part_order=i,part_count=2,
            part_reading_id=fields['reading_id'],record_manifest=copy.deepcopy(manifest))
        projected = copy.deepcopy(original); projected.update(field_names=[name],visible_text=[span['text']],
            locator=dict(physical_pages=[i+1],field=name))
        located = SourceSpan.parse(dict(schema_version=SourceSpan.SCHEMA_VERSION,
            **{k:v for k,v in span.items() if k not in ('chunk_id','span_order')}))
        fields['source_limits'] = make_source_limits(dict(source_sha256=partial['source_sha256'],
            version_id=partial['version_id'],gaps=[projected]),[field],[located])
        parts.append(chunk)
    partial['chunks'] = parts


class RecordingClient:
    def __init__(self):
        self.calls = []; self.response = None; self.error = None

    def rpc(self, name, params, role):
        self.calls.append((name, copy.deepcopy(params), role))
        if self.error: raise self.error
        if self.response is not None: return self.response
        return copy.deepcopy(params['p_receipt']) if 'p_receipt' in params else dict(
            release_id=params['p_release_id'], review_scope_id=params['p_review_scope_id'])


class SelectedReviewLoaderTests(unittest.TestCase):
    def setUp(self):
        _, _, self.receipt, _ = selected_fixture()
        self.client = RecordingClient()

    def test_exact_record_and_binding_are_admin_only_without_input_mutation(self):
        before = copy.deepcopy(self.receipt)
        subject = loader(self, self.client)
        self.assertEqual(subject.record(self.receipt), before)
        self.assertEqual(self.client.calls[-1], ('record_selected_release_review', {'p_receipt':before}, 'admin'))
        expected = dict(release_id='release-selected', review_scope_id='9'*64)
        self.assertEqual(subject.bind_release(**expected), expected)
        self.assertEqual(self.client.calls[-1], ('bind_selected_release_review', dict(
            p_release_id='release-selected', p_review_scope_id='9'*64), 'admin'))
        self.assertEqual(self.receipt, before)

    def test_closed_shapes_scope_decision_and_references_reject_before_rpc(self):
        cases = [None, [], {}, dict(self.receipt, extra=True),
            dict(self.receipt, supported_scope='staff'), dict(self.receipt, receipt_format='other')]
        for key in self.receipt:
            cases.append({k:v for k,v in self.receipt.items() if k != key})
        for key in self.receipt['decision']:
            case = copy.deepcopy(self.receipt); case['decision'][key] = ''; cases.append(case)
        for path in ('../other.md','/private.md','C:/private.md','https://test/a.md','plans/../x.md'):
            case = copy.deepcopy(self.receipt); case['decision']['decision_document'] = path; cases.append(case)
        for key in ('sources','chunks'):
            cases.append(dict(self.receipt, **{key:[]}))
            case = copy.deepcopy(self.receipt); case[key].append(copy.deepcopy(case[key][0])); cases.append(case)
        for case in cases:
            with self.subTest(case=case), self.assertRaises(ValueError): loader(self,self.client).record(case)
        self.assertEqual(self.client.calls, [])

    def test_complete_content_spans_neighbors_and_source_mapping_required(self):
        for field, value in (('content_hash','0'*64), ('chunk_id','bad'), ('spans',[])):
            case = copy.deepcopy(self.receipt); case['chunks'][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError): loader(self,self.client).record(case)
        for key,value in (('required_neighbor_chunk_ids',['b'*64]), ('field_associations',[]),
                ('applicability_basis_ref','')):
            case = copy.deepcopy(self.receipt); case['chunks'][0]['type_fields'][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError): loader(self,self.client).record(case)
        for field,value in (('value','Unreviewed assertion'), ('span_indexes',[]),
                ('span_indexes',[0,0]), ('span_indexes',[True])):
            case = copy.deepcopy(self.receipt); case['chunks'][0]['type_fields']['field_associations'][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError): loader(self,self.client).record(case)
        for field,value in (('version_id','ver-other'), ('span_order',True), ('byte_sha256','2'*64)):
            case = copy.deepcopy(self.receipt); case['chunks'][0]['spans'][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError): loader(self,self.client).record(case)
        self.assertEqual(self.client.calls, [])

    def test_response_integrity_transport_and_binding_validation(self):
        subject = loader(self,self.client)
        for result in ([], {}, dict(self.receipt, supported_scope='other')):
            self.client.response = result
            with self.subTest(result=result), self.assertRaises(ValueError): subject.record(self.receipt)
        self.client.response = {'release_id':'different','review_scope_id':'9'*64}
        with self.assertRaises(ValueError): subject.bind_release('release-selected','9'*64)
        for release,scope in (('', '9'*64), ('release-selected','bad'), (None,'9'*64)):
            with self.subTest(release=release),self.assertRaises(ValueError): subject.bind_release(release,scope)
        self.client = RecordingClient(); self.client.error = StorageError('Synthetic timeout')
        for operation in ('record','bind'):
            with self.subTest(operation=operation),self.assertRaises(StorageError):
                subject = loader(self,self.client)
                subject.record(self.receipt) if operation == 'record' else subject.bind_release('release-selected','9'*64)
        self.assertEqual(len(self.client.calls), 2)

    def test_ordinary_service_groups_require_all_parts_without_neighbor_hints(self):
        for group in (dict(logical_step_id='synthetic-procedure',part_order=0,part_count=2),
                dict(logical_step_id='synthetic-procedure',part_order=1,part_count=2)):
            case = copy.deepcopy(self.receipt); chunk = case['chunks'][0]
            fields = chunk['type_fields']; fields['service_group'] = group
            chunk['content_hash'] = compute_content_hash(chunk['spans'][0]['text'],
                serialize_reviewed_fields(fields['field_associations'],[],group))
            with self.subTest(group=group),self.assertRaises(ValueError): loader(self,self.client).record(case)
