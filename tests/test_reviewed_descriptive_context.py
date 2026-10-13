"""Descriptive lists retain source provenance without approving institutional use."""
import copy
import json
import unittest

import test_reviewed_text_segments as fixtures
from backend.bintanong_contracts.source import compute_content_hash
from backend.bintanong_contracts.reviewed_policy_context import serialize_reviewed_fields
from backend.bintanong_tools.document_ingest.reviewed_policy_chunks import build_reviewed_policy_chunks
from backend.bintanong_retrieval.context import build_context


class ReviewedDescriptiveContextTests(unittest.TestCase):
    def setUp(self):
        self.f=fixtures.ReviewedTextSegmentTests();self.f.setUp()

    def body(self, *, eligible=True, opt_in=True):
        if eligible:
            self.f.row.update(applicability='undergraduate',applicability_evidence_ref='synthetic-body-scope')
        mapping=self.f.map()
        return build_reviewed_policy_chunks(self.f.prep(),sources={self.f.sha:self.f.data},
            review_events=self.f.events,source_versions=[self.f.version],
            field_spans=mapping['field_spans'],include_source_limits=opt_in)

    def candidate(self,chunk):
        return {'chunk':chunk,'spans':chunk['spans'],
            'version':self.f.version.model_dump(mode='json'),'similarity':0.9,'neighbors':[]}

    def rewrite(self,row):
        chunk=row['chunk'];fields=chunk['type_fields']
        chunk['text']=serialize_reviewed_fields(fields['field_associations'],fields['source_limits'])
        chunk['content_hash']=compute_content_hash(chunk['source_text'],chunk['text'])

    def test_body_partition_is_metadata_and_only_programme_body_is_cited(self):
        out=self.body();self.assertEqual(len(out['chunks']),1)
        chunk=out['chunks'][0];self.assertEqual(chunk['source_text'],self.f.body)
        self.assertEqual([s['page'] for s in chunk['spans']],[1])
        metadata=chunk['type_fields']['field_associations'][1]
        self.assertEqual(metadata['value'],self.f.row['fields'][1]['reviewed_value'])
        self.assertEqual(metadata['field_kind'],'body_partition')
        self.assertEqual(metadata['raw_text'],self.f.raw)
        self.assertEqual(metadata['raw_item_ref'],'#/texts/12')
        self.assertEqual(metadata['span_indexes'],[])
        context=build_context([self.candidate(chunk)],100000,len)
        self.assertEqual(len(context['evidence']),1)
        displayed=json.loads(context['evidence'][0]['text'])['fields'][1]
        self.assertEqual(displayed['field_role'],'extraction_metadata')
        self.assertIn('Page furniture',displayed['limitation'])
        self.assertFalse(build_context([self.candidate(chunk)],len(context['context'])-1,len)['evidence'])
        self.assertFalse(self.body(opt_in=False)['chunks'])

    def test_unknown_body_scope_and_pending_partition_remain_withheld(self):
        before=copy.deepcopy(self.f.row)
        result=self.body(eligible=False)
        self.assertFalse(result['chunks'])
        self.assertEqual(result['withheld'][0]['reasons'],['undergraduate_applicability_required'])
        self.assertEqual(self.f.row,before)
        self.f.row['fields'][1]['decision']='pending'
        self.assertFalse(self.body()['chunks'])

    def test_body_partition_mutations_withhold_complete_context(self):
        out=self.body();self.assertEqual(len(out['chunks']),1)
        original=self.candidate(out['chunks'][0])
        for edit in ('kind','text','raw','ref','event','range','page','bbox','missing','citation'):
            row=copy.deepcopy(original);meta=row['chunk']['type_fields']['field_associations'][1]
            segment=meta['value'][0]
            if edit=='kind':segment['kind']='page_furniture'
            if edit=='text':segment['text']='Other Programme'
            if edit=='raw':meta['raw_text']='Other Programme'
            if edit=='ref':meta['raw_item_ref']='not-a-text-ref'
            if edit=='event':meta['event_sha256']='b'*64
            if edit=='range':segment['raw_provenance']['charspan']=[0,999]
            if edit=='page':segment['raw_provenance']['page_no']=2
            if edit=='bbox':segment['raw_provenance']['bbox']['l']=11
            if edit=='missing':meta['value'].pop()
            if edit=='citation':meta['span_indexes']=[0]
            self.rewrite(row)
            with self.subTest(edit=edit):self.assertFalse(build_context([row],100000,len)['evidence'])

    def test_body_context_stored_and_json_roundtrip(self):
        out=self.body();self.assertEqual(len(out['chunks']),1)
        row=json.loads(json.dumps(self.candidate(out['chunks'][0])))
        expected=build_context([row],100000,len)['context'];self.assertTrue(expected)
        row['chunk'].pop('spans')
        for i,span in enumerate(row['spans']):
            span.update(chunk_id=row['chunk']['chunk_id'],span_order=i)
        self.assertEqual(build_context([row],100000,len)['context'],expected)


if __name__=='__main__':unittest.main()
