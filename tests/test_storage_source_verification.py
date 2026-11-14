"""Synthetic scoped V1 observations; no issuing-office authority fixtures."""
import copy
import importlib
import importlib.util
import unittest

from backend.bintanong_contracts.governance import SourceDocumentVersion
from backend.bintanong_storage.client import StorageError
from tests.test_storage_source_acquisition_verification import partial_source, subsequent_check, verified_record


def acquired_source():
    current=partial_source()
    return verified_record(current,subsequent_check(current))


def observation_for(current=None):
    current=current or acquired_source()
    return dict(receipt_format='selected-source-observation-v1',version_id=current['version_id'],
        source_sha256=current['byte_sha256'],acquisition_locators=list(current['acquisition_locators']),
        partial_review_evidence_id=current['content_review_state']['evidence_ref'],review_scope_id='9'*64,
        observation_scope='selected_reviewed_spans',evidence=dict(evidence_id='synthetic-printed-observation',
            kind='printed_text_span',recorded_by='reviewer',recorded_at='2026-10-16T13:00:00Z',authorization_ref=None),
        reviewer_label='owner (chat confirmation)',compiler_label='Synthetic compiler',
        timestamp_meaning='Compilation time of existing confirmation; not new human or office review')


def observed_record(current,observation):
    result=copy.deepcopy(current)
    result['verification_state']=dict(state='observed',evidence_ref=observation['evidence']['evidence_id'])
    result['evidence'].append(copy.deepcopy(observation['evidence']))
    return result


def loader_class(test):
    name='backend.bintanong_storage.source_verification'
    test.assertIsNotNone(importlib.util.find_spec(name),'Scoped V1 source loader missing')
    return importlib.import_module(name).SourceVerificationLoader


class RecordingClient:
    def __init__(self):self.calls,self.response,self.error=[],None,None

    def rpc(self,name,params,role):
        self.calls.append((name,copy.deepcopy(params),role))
        if self.error:raise self.error
        return self.response if self.response is not None else observed_record(
            params['p_expected_register'],params['p_observation'])


class SourceVerificationLoaderTests(unittest.TestCase):
    def setUp(self):
        self.current=acquired_source();self.observation=observation_for(self.current);self.client=RecordingClient()

    def call(self,current=None,observation=None):
        return loader_class(self)(self.client).observe(self.current if current is None else current,
            self.observation if observation is None else observation)

    def test_exact_request_full_return_and_unchanged_inputs_history(self):
        before=copy.deepcopy((self.current,self.observation))
        for current in (self.current,SourceDocumentVersion.parse(self.current)):
            self.assertEqual(self.call(current),SourceDocumentVersion.parse(observed_record(self.current,self.observation)))
            self.assertEqual(self.client.calls[-1],('observe_source_verification',dict(
                p_expected_register=self.current,p_observation=self.observation),'admin'))
        self.assertEqual((self.current,self.observation),before)

    def test_closed_receipt_scope_source_refs_and_labels_reject_before_rpc(self):
        cases=[[],{},dict(self.observation,extra=True)]
        for key in self.observation:
            cases.append({k:v for k,v in self.observation.items() if k!=key})
        for key,value in (('receipt_format','other'),('observation_scope','whole_source'),
                ('version_id','ver-other'),('source_sha256','8'*64),('acquisition_locators',[]),
                ('partial_review_evidence_id','other-review'),('review_scope_id',''),('review_scope_id','G'*64),
                ('reviewer_label',' '),('compiler_label',''),('timestamp_meaning',None)):
            cases.append(dict(self.observation,**{key:value}))
        for case in cases:
            with self.subTest(case=case),self.assertRaises(ValueError):self.call(observation=case)
        self.assertEqual(self.client.calls,[])

    def test_evidence_id_role_kind_authority_and_c1_time_reject_before_rpc(self):
        for key,value in (('evidence_id',' '),('evidence_id','synthetic-partial-review'),
                ('kind','issuing_office_confirmation'),('recorded_by','system'),('recorded_by','researcher'),
                ('recorded_by','issuing_office'),('authorization_ref','forbidden'),
                ('recorded_at','2026-02-30T00:00:00Z'),('recorded_at','2026-10-16T09:00:00Z')):
            case=copy.deepcopy(self.observation);case['evidence'][key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):self.call(observation=case)
        self.assertEqual(self.client.calls,[])

    def test_only_verified_acquisition_partial_review_pending_verification_and_approval(self):
        for field,state in (('acquisition_state','observed'),('verification_state','observed'),
                ('content_review_state','pending'),('content_review_state','reviewed'),('approval_state','requested')):
            case=copy.deepcopy(self.current);case[field]['state']=state
            with self.subTest(field=field),self.assertRaises(ValueError):self.call(case)
        self.assertEqual(self.client.calls,[])

    def test_time_parity_equal_c1_and_normalized_offsets_preserve_text(self):
        for moment in ('2026-10-16T10:00:00Z','2026-10-16T18:00:00+08:00',
                '2026-10-16T12:00:00+00:99','2026-10-17T10:00:00.123456789+23:59'):
            self.observation['evidence']['recorded_at']=moment
            with self.subTest(moment=moment):self.assertEqual(self.call().evidence[-1].recorded_at,moment)

    def test_locator_order_unused_history_and_other_fields_are_preserved(self):
        self.current['acquisition_locators'].append('synthetic:second')
        self.current['evidence'].insert(0,dict(self.current['evidence'][0],evidence_id='unused-evidence'))
        self.observation=observation_for(self.current)
        result=self.call().model_dump(mode='json')
        self.assertEqual(result['evidence'][:-1],self.current['evidence'])
        self.assertEqual({k:v for k,v in result.items() if k not in ('evidence','verification_state')},
                         {k:v for k,v in self.current.items() if k not in ('evidence','verification_state')})
        self.observation['acquisition_locators'].reverse()
        with self.assertRaises(ValueError):self.call()
        self.assertEqual(len(self.client.calls),1)

    def test_malformed_or_altered_return_and_storage_failure_do_not_retry(self):
        for response in ([],{},self.current,dict(observed_record(self.current,self.observation),filename='changed.pdf')):
            self.client.response=response
            with self.subTest(response=response),self.assertRaises(ValueError):self.call()
        self.client.error=StorageError('synthetic timeout');before=len(self.client.calls)
        with self.assertRaises(StorageError):self.call()
        self.assertEqual(len(self.client.calls),before+1)

    def test_old_chunk_binding_fails_and_existing_rebind_preserves_content(self):
        from backend.bintanong_contracts.source import Chunk,bind_chunk,check_chunk_binding
        from tests.test_contracts_source import chunk_dict,span_dict
        current=SourceDocumentVersion.parse(self.current)
        raw=chunk_dict(chunk_type='policy',document_id=current.document_id,version_id=current.version_id,
            edition_id=current.edition_id,byte_sha256=current.byte_sha256,source_label=current.filename,
            spans=[span_dict(byte_sha256=current.byte_sha256,version_id=current.version_id)])
        old=bind_chunk(Chunk.parse(raw),current)
        observed=self.call()
        with self.assertRaises(ValueError):check_chunk_binding(old,observed)
        bound=bind_chunk(old,observed);check_chunk_binding(bound,observed)
        self.assertEqual(bound.source_verification,'observed')
        self.assertEqual(bound.register_binding.verification_evidence_ref,self.observation['evidence']['evidence_id'])
        for field in ('chunk_id','content_hash','text','source_text','spans','type_fields'):
            self.assertEqual(getattr(bound,field),getattr(old,field))
