"""Visible flow geometry is documentary evidence, including limited originals."""
import copy
import hashlib
import json
import unittest

import test_reviewed_image_spans as fixtures
from backend.bintanong_tools.document_ingest.reviewed_policy import build_reviewed_policy_bundle
from backend.bintanong_tools.document_ingest.reviewed_policy_chunks import build_reviewed_policy_chunks
from backend.bintanong_retrieval.context import build_context
from backend.bintanong_contracts.reviewed_policy_context import serialize_reviewed_fields
from backend.bintanong_contracts.source import SourceSpan,compute_content_hash


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,
        allow_nan=False,separators=(',',':')).encode()).hexdigest()


class ReviewedFlowEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.f=fixtures.ImageFieldSpanTests();self.f.setUp()
        self.f.rows=[]
        for index,(name,text,region) in enumerate([
                ('start','START',[20,40,80,80]),
                ('process','Check the form.',[20,140,120,200]),
                ('end','END',[20,300,80,340])]):
            row=self.f.row('flow-part-'+str(index));field=self.f.field(name,text)
            field['locator']['evidence']['proposed_image_region']=region
            row.update(fields=[field],applicability='undergraduate',
                applicability_evidence_ref='synthetic#undergraduate',
                original_reading_id='flow',part_order=index)
            self.f.rows.append(row)
        yes=self.f.field('yes','Yes')
        yes['locator']['evidence']['proposed_image_region']=[70,240,90,260]
        self.f.rows[1]['fields'].append(yes)
        self.refresh()

    def refresh(self,limited=False,unknown=False):
        mapping=self.f.map();self.anchors=mapping['field_spans']
        self.manifest={'schema_version':'bintanong-flow-evidence-v1','logical_step_id':'flow',
            'source_sha256':self.f.sha,'version_id':self.f.version.version_id,'physical_page':2,
            'image':copy.deepcopy(self.f.pages[(self.f.sha,2)]),
            'nodes':[{'id':'START','kind':'start','field':'start','region':[20,40,80,80]},
                {'id':'a','kind':'decision','field':'process','region':[20,140,120,200]}],
            'labels':{} if unknown else {'yes':'Yes'},'edges':[{'from':'START','to':'a','label':None,
                'region':[45,78,55,142],'route':[[50,80],[50,140]]}],
            'unresolved_outgoing':[],'source_complete':not limited and not unknown,
            'field_bindings':{},'limits_sha256':digest([g for r in self.f.rows for g in r['gaps']])}
        if unknown:
            self.manifest['unresolved_outgoing']=[{'from':'a','region':[45,198,55,222],
                'route':[[50,200],[50,220]]}]
        else:
            self.manifest['nodes'].append({'id':'END','kind':'terminal','field':'end','region':[20,300,80,340]})
            self.manifest['edges'].append({'from':'a','to':'END','label':'yes',
                'label_region':[70,240,90,260],'region':[45,198,55,302],
                'route':[[50,200],[50,300]]})
        for row in self.f.rows:
            for field in row['fields']:
                name=field['name'];self.manifest['field_bindings'][name]=digest({
                    'value':field['reviewed_value'],'source_blank':field['source_blank'],
                    'spans':self.anchors[row['reading_id']][name]})
        self.sign()

    def sign(self):
        self.manifest.pop('review_event_sha256',None)
        event={'source_sha256':self.f.sha,'owner_statement':'Reviewed synthetic visible geometry.',
            'flow_evidence_sha256':digest(self.manifest)}
        raw=json.dumps(event).encode();identity=hashlib.sha256(raw).hexdigest()
        self.f.events[identity]=raw;self.manifest['review_event_sha256']=identity

    def build(self,**changes):
        bundle=build_reviewed_policy_bundle(self.f.rows,sources=self.f.sources,review_events=self.f.events)
        options=dict(field_spans=self.anchors,include_source_limits=True,compact_context=True,
            flow_bindings={'flow':self.manifest},**changes)
        try:
            return build_reviewed_policy_chunks(bundle,sources=self.f.sources,review_events=self.f.events,
                source_versions=[self.f.version],**options)
        except TypeError as exc:
            self.fail('The reviewed chunk builder cannot carry visible flow evidence: '+str(exc))

    def context(self,result,**changes):
        rows=[dict(chunk=c,spans=c['spans'],version=self.f.version.model_dump(mode='json'),
            similarity=1.0) for c in result['chunks']]
        for row in rows:row['neighbors']=[r for r in rows if r is not row]
        return build_context([rows[1]],changes.pop('budget',100000),len,
            shared_citations=True,shared_group_metadata=True,**changes)

    def test_unlabelled_connectors_and_printed_labels_reach_complete_context(self):
        result=self.build();self.assertEqual(result['withheld'],[])
        self.assertEqual(len(result['chunks']),3)
        context=self.context(result);self.assertFalse(context['gaps'])
        payloads=[json.loads(e['text']) for e in context['evidence']]
        node=payloads[1]['flow_evidence']['nodes'][0]
        self.assertEqual(node['field'],'process')
        self.assertEqual(node['outgoing'],[{'label':'Yes','to':'END'}])
        self.assertEqual(payloads[0]['flow_evidence']['nodes'][0]['outgoing'],[{'label':None,'to':'a'}])
        self.assertTrue(all(p['flow_evidence']['source_complete'] for p in payloads))
        self.assertFalse(self.context(result,budget=context['context_tokens']-1)['evidence'])

    def test_clipped_predicate_stays_limited_even_with_visible_end(self):
        field=self.f.rows[1]['fields'][0];field.update(original_value='Partial &',reviewed_value='Partial &')
        field['locator']['evidence']['proposed_reading']='Partial &'
        self.f.rows[1]['gaps']=[{'gap_id':'cut','issue':'source_cutoff','field_names':['process'],
            'visible_text':'Partial &','affected_claims':['complete decision predicate'],
            'locator':{'physical_pages':[2],'field':'process'}}]
        self.refresh(limited=True)
        context=self.context(self.build());self.assertEqual(len(context['evidence']),3)
        payloads=[json.loads(e['text']) for e in context['evidence']]
        self.assertFalse(payloads[1]['flow_evidence']['source_complete'])
        self.assertEqual(payloads[1]['source_limits'][0]['issue'],'source_cutoff')
        self.assertEqual(payloads[2]['flow_evidence']['nodes'][0]['id'],'END')

    def test_unknown_outgoing_connector_does_not_become_end(self):
        self.f.rows=self.f.rows[:2];self.refresh(unknown=True)
        context=self.context(self.build());self.assertEqual(len(context['evidence']),2)
        node=json.loads(context['evidence'][1]['text'])['flow_evidence']['nodes'][0]
        self.assertEqual(node['outgoing'],[])
        self.assertTrue(node['outgoing_unresolved'])
        self.assertNotIn('"to":"END"',context['context'])

    def test_geometry_source_event_and_label_mutations_are_rejected(self):
        original=copy.deepcopy(self.manifest)
        for change in ('outside','nonfinite','page','version','event','label','endpoint','start','field'):
            with self.subTest(change=change):
                self.manifest=copy.deepcopy(original)
                if change=='outside':self.manifest['edges'][0]['region'][0]=-1
                elif change=='nonfinite':self.manifest['edges'][0]['route'][0][0]=float('nan')
                elif change=='page':self.manifest['physical_page']=3
                elif change=='version':self.manifest['version_id']='other-version'
                elif change=='event':self.manifest['review_event_sha256']='d'*64
                elif change=='label':self.manifest['labels']['yes']='Approved automatically'
                elif change=='endpoint':self.manifest['edges'][0]['to']='missing'
                elif change=='start':self.manifest['nodes'][0]['kind']='process'
                else:self.manifest['nodes'][1]['field']='missing'
                if change not in ('event','nonfinite'):self.sign()
                with self.assertRaises(ValueError):self.build()

    def test_cutoff_cannot_be_promoted_by_changing_complete_flag(self):
        self.f.rows=self.f.rows[:2];self.refresh(unknown=True)
        self.manifest['source_complete']=True;self.sign()
        with self.assertRaises(ValueError):self.build()

    def test_missing_or_substituted_flow_companion_withholds_whole_context(self):
        result=self.build()
        rows=[dict(chunk=c,spans=c['spans'],version=self.f.version.model_dump(mode='json'),similarity=1.0)
            for c in result['chunks']]
        for row in rows:row['neighbors']=[r for r in rows if r is not row]
        rows[0]['neighbors']=rows[0]['neighbors'][:1]
        self.assertFalse(build_context([rows[0]],100000,len)['evidence'])
        rows[0]['neighbors']=[rows[1],rows[2]]
        rows[2]['chunk']['type_fields']['service_group'].pop('flow_manifest')
        self.assertFalse(build_context([rows[0]],100000,len)['evidence'])

    def test_saved_flow_manifest_mutation_cannot_hide_known_limits(self):
        result=self.build()
        result['chunks'][1]['type_fields']['service_group']['flow_manifest']['source_complete']=False
        self.assertFalse(self.context(result)['evidence'])

    def test_budget_withholds_all_flow_parts_together(self):
        result=self.build(token_cap=8)
        self.assertFalse(result['chunks']);self.assertEqual(len(result['withheld']),3)

    def test_rewritten_annotation_cannot_reuse_original_review_receipt(self):
        result=self.build()
        for chunk in result['chunks']:
            fields=chunk['type_fields'];fields['service_group']['flow_manifest']['nodes'][1]['kind']='process'
            chunk['text']=serialize_reviewed_fields(fields['field_associations'],fields['source_limits'],
                fields['service_group'],context_format=fields['context_format'])
            chunk['content_hash']=compute_content_hash(chunk['source_text'],chunk['text'])
        self.assertFalse(self.context(result)['evidence'])

    def test_visible_no_loop_is_retained_beside_yes_terminal(self):
        no=self.f.field('no','No');no['locator']['evidence']['proposed_image_region']=[140,220,170,250]
        self.f.rows[1]['fields'].append(no);self.refresh()
        self.manifest['labels']['no']='No'
        self.manifest['edges'].append({'from':'a','to':'a','label':'no','label_region':[140,220,170,250],
            'region':[118,138,142,172],'route':[[120,170],[140,170],[140,140],[120,140]]})
        self.sign();context=self.context(self.build())
        node=json.loads(context['evidence'][1]['text'])['flow_evidence']['nodes'][0]
        self.assertEqual(node['outgoing'],[{'label':'Yes','to':'END'},{'label':'No','to':'a'}])

    def test_stored_rpc_spans_preserve_flow_and_reject_cross_page_substitution(self):
        result=self.build();rows=[]
        for chunk in copy.deepcopy(result['chunks']):
            spans=chunk.pop('spans');chunk.pop('schema_version')
            for order,span in enumerate(spans):
                span.pop('schema_version');span.update(chunk_id=chunk['chunk_id'],span_order=order)
            rows.append(dict(chunk=chunk,spans=spans,version=self.f.version.model_dump(mode='json'),similarity=1.0))
        for row in rows:row['neighbors']=[r for r in rows if r is not row]
        self.assertEqual(len(build_context([rows[1]],100000,len)['evidence']),3)
        rows[0]['spans'][0]['page']=3
        self.assertFalse(build_context([rows[1]],100000,len)['evidence'])

    def test_existing_source_span_model_inputs_remain_supported(self):
        for fields in self.anchors.values():
            for name,spans in fields.items():fields[name]=[SourceSpan.parse(s) for s in spans]
        self.assertEqual(len(self.context(self.build())['evidence']),3)

    def test_shape_outline_can_surround_its_cited_text_region(self):
        self.manifest['nodes'][1]['region']=[18,137,122,202]
        self.sign()
        self.assertEqual(len(self.context(self.build())['evidence']),3)

    def test_malformed_saved_fields_and_limits_withhold_whole_flow(self):
        original=self.build()
        for key,value in [('field_associations',[None]),('field_associations',None),
                ('source_limits',[None]),('source_limits',None)]:
            with self.subTest(key=key,value=value):
                changed=copy.deepcopy(original);changed['chunks'][0]['type_fields'][key]=value
                self.assertFalse(self.context(changed)['evidence'])


if __name__=='__main__':unittest.main()
