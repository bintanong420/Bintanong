"""Descriptive lists retain source provenance without approving institutional use."""
import copy
import hashlib
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

    def cover_setup(self, *, eligible=True):
        self.labels=['SYNTHETIC UNIVERSITY','CITIZEN’S CHARTER','2026 (1st Edition)']
        event=json.dumps({'source_sha256':self.f.sha,'owner_statement':'Synthetic cover labels match.',
            'physical_page':1,'accepted_cover_labels':self.labels}).encode()
        ev=hashlib.sha256(event).hexdigest();self.f.events={ev:event}
        self.f.row={'reading_id':'cover','source_sha256':self.f.sha,'version_id':self.f.version.version_id,
            'intended_audience':'undergraduate','applicability':'undergraduate' if eligible else 'unknown',
            'applicability_evidence_ref':'synthetic-cover-scope' if eligible else None,
            'fields':[{'name':'cover_labels','original_value':self.labels[:],'reviewed_value':self.labels[:],
                'source_blank':False,'decision':'accepted','review_event_sha256':ev,
                'locator':{'physical_pages':[1],'field':'cover_labels','evidence':{'basis':'synthetic reading'}}}],
            'gaps':[{'gap_id':'currentness','field_names':['cover_labels'],'issue':'effectivity_currentness_unknown',
                'visible_text':self.labels[:],'affected_claims':['effective date','current policy status'],
                'locator':{'physical_pages':[1],'field':'cover_labels'}}],
            'preserved_evidence':[{'artifact':'synthetic-event.json','sha256':ev}]}
        self.cover_regions=[[10,20,350,55],[10,60,350,100],[10,110,350,145]]

    def cover_map(self, **changes):
        from backend.bintanong_tools.document_ingest.reviewed_cover_context import map_reviewed_cover_labels
        options=dict(sources={self.f.sha:self.f.data},review_events=self.f.events,
            source_versions=[self.f.version],image_page=self.f.pages[(self.f.sha,1)],
            read_page_image=self.f.reader,label_regions=self.cover_regions,reading_id='cover')
        options.update(changes)
        return map_reviewed_cover_labels(self.f.prep(),**options)

    def cover(self, **changes):
        mapping=self.cover_map()
        options=dict(sources={self.f.sha:self.f.data},review_events=self.f.events,
            source_versions=[self.f.version],field_spans=mapping['field_spans'],include_source_limits=True)
        options.update(changes)
        return build_reviewed_policy_chunks(self.f.prep(),**options)

    def test_cover_labels_and_currentness_gap_keep_complete_ordered_citations(self):
        self.cover_setup();before=copy.deepcopy(self.f.row)
        mapped=self.cover_map();self.assertEqual(mapped['original_reading'],before)
        self.assertFalse(mapped['activation_eligible'])
        out=self.cover();self.assertEqual(len(out['chunks']),1)
        chunk=out['chunks'][0];self.assertEqual([s['text'] for s in chunk['spans']],self.labels)
        self.assertEqual(chunk['type_fields']['source_limits'][0]['visible_text'],self.labels)
        context=build_context([self.candidate(chunk)],100000,len)
        self.assertEqual(len(context['evidence'][0]['citations']),3)
        displayed=json.loads(context['evidence'][0]['text'])
        self.assertEqual(displayed['fields'][0]['value'],self.labels)
        self.assertIn('current policy status',displayed['source_limits'][0]['message'])
        self.assertFalse(build_context([self.candidate(chunk)],len(context['context'])-1,len)['evidence'])
        self.assertEqual(self.f.row,before)
        self.assertFalse(self.cover(include_source_limits=False)['chunks'])

    def test_cover_mapping_rejects_partial_review_regions_or_changed_render(self):
        self.cover_setup()
        for edit in ('regions','bounds','transform','image','review','event','labels','version'):
            self.cover_setup();options={}
            if edit=='regions':options['label_regions']=self.cover_regions[:2]
            if edit=='bounds':options['label_regions']=[[0,0,2000,20],*self.cover_regions[1:]]
            if edit=='transform':options['image_page']={**self.f.pages[(self.f.sha,1)],'crop':[0,0,0,0]}
            if edit=='image':options['read_page_image']=lambda data,page:{**self.f.reader(data,page),'image_bytes':b'changed'}
            if edit=='review':self.f.row['fields'][0]['decision']='pending'
            if edit=='event':self.f.row['fields'][0]['review_event_sha256']='b'*64
            if edit=='labels':self.f.row['fields'][0]['reviewed_value'].reverse()
            if edit=='version':self.f.row['version_id']='ver-other'
            with self.subTest(edit=edit),self.assertRaises(ValueError):self.cover_map(**options)

    def test_cover_unknown_scope_and_tampered_or_partial_stored_context_withhold(self):
        self.cover_setup(eligible=False)
        result=self.cover();self.assertFalse(result['chunks'])
        self.assertEqual(result['withheld'][0]['reasons'],['undergraduate_applicability_required'])
        self.cover_setup();out=self.cover();self.assertEqual(len(out['chunks']),1)
        original=self.candidate(out['chunks'][0]);expected=build_context([original],100000,len)['context']
        row=json.loads(json.dumps(original));row['chunk'].pop('spans')
        for i,span in enumerate(row['spans']):span.update(chunk_id=row['chunk']['chunk_id'],span_order=i)
        self.assertEqual(build_context([row],100000,len)['context'],expected)
        for edit in ('labels','visible','page','partial'):
            row=copy.deepcopy(original);fields=row['chunk']['type_fields']
            if edit=='labels':fields['field_associations'][0]['value'].reverse()
            if edit=='visible':fields['source_limits'][0]['visible_text'][0]='Other University'
            if edit=='page':row['spans'][1]['page']=2
            if edit=='partial':row['spans'].pop()
            self.rewrite(row)
            with self.subTest(edit=edit):self.assertFalse(build_context([row],100000,len)['evidence'])


if __name__=='__main__':unittest.main()
