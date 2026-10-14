"""Whole-field record groups retain complete unresolved evidence under the cap."""
import copy
import hashlib
import json
import unittest

from backend.bintanong_contracts.source import compute_content_hash
from backend.bintanong_contracts.reviewed_policy_context import serialize_reviewed_fields
from backend.bintanong_tools.document_ingest.register import mint_pending_register
from backend.bintanong_tools.document_ingest.reviewed_policy import build_reviewed_policy_bundle
from backend.bintanong_tools.document_ingest.reviewed_policy_chunks import build_reviewed_policy_chunks
from backend.bintanong_retrieval.context import build_context


class ReviewedRecordContextTests(unittest.TestCase):
    def setUp(self):
        self.data=b'synthetic undergraduate policy original';self.sha=hashlib.sha256(self.data).hexdigest()
        self.sources={self.sha:self.data}
        self.version=mint_pending_register([{'filename':'synthetic.pdf','sha256':self.sha,
            'acquisition_locator':'shelf:synthetic-record'}],synthetic=True)[0]
        event=json.dumps({'source_sha256':self.sha,'owner_statement':'Synthetic clauses confirmed; meaning unresolved.'}).encode()
        ev=hashlib.sha256(event).hexdigest();self.events={ev:event}
        self.names=['clause-a','clause-b','clause-c','clause-d']
        values=[f'Synthetic undergraduate clause {n}: '+('reviewed deadline words '*3) for n in self.names]
        self.row={'reading_id':'record','source_sha256':self.sha,'version_id':self.version.version_id,
            'intended_audience':'undergraduate','applicability':'unknown','applicability_evidence_ref':None,
            'fields':[{'name':n,'original_value':v,'reviewed_value':v,'source_blank':False,'decision':'accepted',
                'review_event_sha256':ev,'locator':{'physical_pages':[2],'field':n,'evidence':{'basis':'synthetic'}}}
                for n,v in zip(self.names,values)],
            'gaps':[{'gap_id':'deadlines','issue':'conflicting_deadlines','field_names':self.names[:],
                'visible_text':values[:],'affected_claims':['applicable deadline','precedence'],
                'locator':{'physical_pages':[2],'field':','.join(self.names)},'evidence_ref':'synthetic#gap'}],
            'preserved_evidence':[{'artifact':'synthetic-event.json','sha256':ev}]}
        self.anchors={'record':{n:[{'schema_version':'bintanong-source-span-v1','byte_sha256':self.sha,
            'version_id':self.version.version_id,'page':2,'printed_page_label':None,
            'locator':{'kind':'text_item','item_ids':['synthetic:'+n],'cell_ids':[],'table_index':None,'ref':None},
            'text':v,'bbox':[10,10+i*30,500,30+i*30],'bbox_origin':'TOPLEFT','page_size':[600,800],
            'extraction':{'source_kind':'original_pdf_image','resolution_method':'owner_transcribed_region',
                'repair_id':'a'*64,'ocr_confidence':None}}] for i,(n,v) in enumerate(zip(self.names,values))}}

    def bundle(self):
        return build_reviewed_policy_bundle([self.row],sources=self.sources,review_events=self.events)

    def prepare(self,groups=None):
        from backend.bintanong_tools.document_ingest.reviewed_record_context import prepare_reviewed_record_context
        return prepare_reviewed_record_context(self.bundle(),reading_id='record',field_groups=groups or [[n] for n in self.names],
            field_spans=self.anchors,sources=self.sources,review_events=self.events)

    def eligible(self):
        self.row.update(applicability='undergraduate',applicability_evidence_ref='synthetic-record-scope')
        return self.prepare()

    def build(self,p,**changes):
        options=dict(sources=self.sources,review_events=self.events,source_versions=[self.version],
            field_spans=p['field_spans'],required_readings=p['required_readings'],
            record_bindings=p['record_bindings'],include_source_limits=True)
        options.update(changes)
        return build_reviewed_policy_chunks(build_reviewed_policy_bundle(p['readings'],sources=self.sources,
            review_events=self.events),**options)

    def candidates(self,result):
        rows=[{'chunk':c,'spans':c['spans'],'version':self.version.model_dump(mode='json'),
            'neighbors':[],'similarity':0.9} for c in result['chunks']]
        for r in rows:r['neighbors']=[x for x in rows if x is not r]
        return rows

    def rewrite(self,row):
        c=row['chunk'];f=c['type_fields'];c['text']=serialize_reviewed_fields(f['field_associations'],f['source_limits'],f['service_group'])
        c['content_hash']=compute_content_hash(c['source_text'],c['text'])

    def test_complete_projection_retains_original_and_distributed_gap_fields(self):
        before=copy.deepcopy((self.row,self.anchors));p=self.prepare()
        self.assertEqual(p['original_reading'],self.row)
        self.assertEqual([f for r in p['readings'] for f in r['fields']],self.row['fields'])
        self.assertEqual((self.row,self.anchors),before)
        self.assertEqual([r['part_order'] for r in p['readings']],[0,1,2,3])
        self.assertTrue(all(r['applicability']=='unknown' for r in p['readings']))
        self.assertFalse(p['activation_eligible'])
        result=self.build(p);self.assertFalse(result['chunks'])
        self.assertTrue(all(r['reasons']==['undergraduate_applicability_required'] for r in result['withheld']))

    def test_synthetic_complete_parts_fit_cap_and_restore_full_gap_in_order(self):
        p=self.eligible();out=self.build(p);self.assertEqual(len(out['chunks']),4)
        self.assertTrue(all(c['token_count']['count']<=480 for c in out['chunks']))
        rows=self.candidates(out);context=build_context([rows[-1]],100000,len)
        self.assertEqual([r['chunk_id'] for r in context['evidence']],[c['chunk_id'] for c in out['chunks']])
        for row in rows:
            limit=row['chunk']['type_fields']['source_limits'][0]
            self.assertEqual(limit['visible_text'],[row['chunk']['type_fields']['field_associations'][0]['value']])
            display=json.loads(row['chunk']['text'])['source_limits'][0]
            self.assertNotIn('visible_text',display)
            self.assertIn('precedence',display['message'])
        self.assertFalse(build_context([rows[-1]],len(context['context'])-1,len)['evidence'])
        rows[-1]['neighbors'].pop();self.assertFalse(build_context([rows[-1]],100000,len)['evidence'])

    def test_binding_mismatch_pending_excluded_and_invalid_field_partition_fail(self):
        for edit in ('scope','review','order','missing','duplicate','span'):
            self.setUp();groups=[[n] for n in self.names]
            if edit=='scope':self.row['applicability']='excluded';self.row['applicability_evidence_ref']='synthetic-negative'
            if edit=='review':self.row['fields'][2]['decision']='pending'
            if edit=='order':groups.reverse()
            if edit=='missing':groups.pop()
            if edit=='duplicate':groups[1]=groups[0][:]
            if edit=='span':self.anchors['record'][self.names[1]][0]['page']=3
            with self.subTest(edit=edit),self.assertRaises(ValueError):self.prepare(groups)
        self.setUp();p=self.eligible();p['readings'][1]['fields'][0]['reviewed_value']='Other'
        with self.assertRaises(ValueError):self.build(p)
        p=self.eligible()
        with self.assertRaises(ValueError):self.build(p,record_bindings={})
        self.assertFalse(self.build(p,include_source_limits=False)['chunks'])

    def test_manifest_gap_and_stored_mutations_withhold_complete_group(self):
        original=self.candidates(self.build(self.eligible()))
        for edit in ('gap_hash','gap_metadata','gap_fields','field_value','reading_id','manifest'):
            rows=copy.deepcopy(original)
            for row in rows:
                fields=row['chunk']['type_fields'];meta=fields['service_group']['record_manifest']
                if edit=='gap_hash':meta['gaps']['deadlines']['sha256']='b'*64
                if edit=='gap_metadata':fields['source_limits'][0]['evidence_ref']='different'
                if edit=='gap_fields':
                    origin=meta['gaps']['deadlines'];origin['field_names']=origin['field_names'][:-1]
                    origin['locator']['field']=','.join(origin['field_names'])
                if edit=='field_value':fields['field_associations'][0]['value']='Different clause'
                if edit=='reading_id':fields['service_group']['part_reading_id']='different-part'
                if edit=='manifest':meta['parts']=list(reversed(meta['parts']))
                self.rewrite(row)
            with self.subTest(edit=edit):self.assertFalse(build_context([rows[1]],100000,len)['evidence'])
        rows=json.loads(json.dumps([{k:v for k,v in row.items() if k!='neighbors'} for row in original]))
        for row in rows:row['neighbors']=[other for other in rows if other is not row]
        expected=build_context([rows[1]],100000,len)['context']
        for row in rows:
            row['chunk'].pop('spans')
            for i,s in enumerate(row['spans']):s.update(chunk_id=row['chunk']['chunk_id'],span_order=i)
        self.assertEqual(build_context([rows[1]],100000,len)['context'],expected)

    def test_source_blank_fields_stay_blank_with_complete_group(self):
        f=self.row['fields'][-1];f.update(original_value='',reviewed_value='',source_blank=True)
        self.anchors['record'][f['name']]=[]
        self.row['gaps'][0]['field_names'].pop();self.row['gaps'][0]['visible_text'].pop()
        self.row['gaps'][0]['locator']['field']=','.join(self.names[:-1])
        self.row.update(applicability='undergraduate',applicability_evidence_ref='synthetic-record-scope')
        p=self.prepare([[self.names[0]],[*self.names[1:]]]);out=self.build(p)
        self.assertEqual(len(out['chunks']),2)
        fields=out['chunks'][1]['type_fields']['field_associations']
        self.assertEqual(fields[-1]['value'],'');self.assertTrue(fields[-1]['source_blank'])
        self.assertEqual(fields[-1]['span_indexes'],[])
        self.assertTrue(build_context([self.candidates(out)[1]],100000,len)['evidence'])

    def test_duplicate_part_reading_identity_cannot_substitute_context(self):
        rows=self.candidates(self.build(self.eligible()))
        fields=rows[1]['chunk']['type_fields']
        fields['reading_id']=rows[0]['chunk']['type_fields']['reading_id']
        fields['service_group']['part_reading_id']=fields['reading_id']
        self.rewrite(rows[1])
        self.assertFalse(build_context([rows[1]],100000,len)['evidence'])

    def test_malformed_projected_gap_locator_withholds_without_crashing(self):
        original=self.candidates(self.build(self.eligible()))
        for locator in (None,[],1,'x',True):
            rows=copy.deepcopy(original)
            rows[1]['chunk']['type_fields']['source_limits'][0]['locator']=locator
            with self.subTest(locator=locator):
                result=build_context([rows[1]],100000,len)
                self.assertFalse(result['evidence'])
                self.assertTrue(any(g.startswith('invalid_reviewed_context:') for g in result['gaps']))

    def test_projected_gap_pages_must_reconstruct_original_page_declaration(self):
        rows=self.candidates(self.build(self.eligible()))
        rows[1]['chunk']['type_fields']['source_limits'][0]['locator']['physical_pages']=[3]
        rows[1]['spans'][0]['page']=3
        self.rewrite(rows[1])
        self.assertFalse(build_context([rows[1]],100000,len)['evidence'])

    def test_gap_free_record_uses_existing_scalar_route(self):
        self.row['gaps']=[]
        with self.assertRaises(ValueError):self.prepare()

    def test_original_gap_pages_require_complete_source_span_coverage(self):
        self.row['gaps'][0]['locator']['physical_pages']=[2,3]
        with self.assertRaises(ValueError):self.prepare()

    def test_compact_v2_keeps_full_group_manifest_validation_and_atomic_budget(self):
        prepared=self.eligible();out=self.build(prepared,compact_context=True)
        rows=self.candidates(out);expected_manifest=prepared['readings'][0]['record_manifest']
        for row in rows:
            chunk=row['chunk'];stored=chunk['type_fields']['service_group']
            self.assertEqual(stored['record_manifest'],expected_manifest)
            self.assertNotIn('record_manifest',json.loads(chunk['text'])['service_group'])
            self.assertIn('visible_text',chunk['type_fields']['source_limits'][0])
        result=build_context([rows[-1]],100000,len)
        self.assertEqual([e['chunk_id'] for e in result['evidence']],[c['chunk_id'] for c in out['chunks']])
        self.assertIn('precedence',result['context'])
        self.assertFalse(build_context([rows[-1]],len(result['context'])-1,len)['evidence'])
        changed=copy.deepcopy(rows)
        for row in changed:row['chunk']['type_fields']['service_group']['record_manifest']['gaps']['deadlines']['sha256']='b'*64
        self.assertFalse(build_context([changed[-1]],100000,len)['evidence'])
        rows[-1]['neighbors'].pop()
        self.assertFalse(build_context([rows[-1]],100000,len)['evidence'])


if __name__=='__main__':unittest.main()
