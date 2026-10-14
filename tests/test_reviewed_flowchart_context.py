"""Synthetic reviewed arrows stay structured and travel with complete node context."""
import copy
import json
import unittest

import test_reviewed_image_spans as fixtures
from backend.bintanong_contracts.source import compute_content_hash
from backend.bintanong_contracts.reviewed_policy_context import serialize_reviewed_fields
from backend.bintanong_tools.document_ingest.reviewed_policy import build_reviewed_policy_bundle
from backend.bintanong_tools.document_ingest.reviewed_policy_chunks import build_reviewed_policy_chunks
from backend.bintanong_retrieval.context import build_context


class ReviewedFlowchartContextTests(unittest.TestCase):
    def setUp(self):
        self.f=fixtures.ImageFieldSpanTests();self.f.setUp()
        self.edges=self.f.graph_setup()

    def prepare(self,mapping=None,**changes):
        from backend.bintanong_tools.document_ingest.reviewed_flowchart_context import prepare_reviewed_flowchart_context
        return prepare_reviewed_flowchart_context(self.f.map() if mapping is None else mapping,
            arrow_reading_id='arrows',row_reading_ids={'a':'node-a','b':'node-b'},
            edge_regions=self.edges,terminal_region=changes.get('terminal_region',[60,340,140,380]))

    def eligible(self):
        for row in self.f.rows:
            row.update(applicability='undergraduate',applicability_evidence_ref='synthetic-scope#flowchart')
        return self.prepare()

    def build(self,p=None,**changes):
        p=self.prepare() if p is None else p
        bundle=build_reviewed_policy_bundle(p['readings'],sources=self.f.sources,review_events=self.f.events)
        options={'field_spans':p['field_spans'],'required_readings':p['required_readings'],
            'flowchart_bindings':p['flowchart_bindings'],'include_source_limits':True,**changes}
        return build_reviewed_policy_chunks(bundle,sources=self.f.sources,review_events=self.f.events,
            source_versions=[self.f.version],**options)

    def candidates(self,result):
        rows=[{'chunk':c,'spans':c['spans'],'version':self.f.version.model_dump(mode='json'),
            'neighbors':[],'similarity':0.9} for c in result['chunks']]
        for row in rows:row['neighbors']=[r for r in rows if r is not row]
        return rows

    def test_preparation_preserves_original_arrays_steps_and_scope(self):
        mapping=self.f.map();before=copy.deepcopy(mapping);p=self.prepare(mapping)
        self.assertEqual(mapping,before)
        self.assertEqual(p['original_readings'],[self.f.rows[2],self.f.rows[0],self.f.rows[1]])
        self.assertEqual([r['reading_id'] for r in p['readings']],['arrows','node-a','node-b'])
        self.assertEqual(p['readings'][0]['fields'],self.f.rows[2]['fields'])
        self.assertEqual([s['text'] for s in p['field_spans']['arrows']['arrows']],['Yes','No','END'])
        self.assertEqual(p['required_readings']['arrows'],['node-a','node-b'])
        self.assertFalse(p['activation_eligible'])
        result=self.build(p);self.assertFalse(result['chunks'])
        self.assertEqual(len(result['withheld']),3)
        self.assertTrue(all(r['reasons']==['undergraduate_applicability_required'] for r in result['withheld']))

    def test_eligible_synthetic_structured_edges_render_in_source_order_and_budget(self):
        out=self.build(self.eligible());self.assertEqual(len(out['chunks']),3)
        self.assertTrue(all(c['token_count']['count']<=480 for c in out['chunks']))
        arrows=out['chunks'][0]['type_fields']['field_associations'][0]
        self.assertEqual(arrows['value'],self.f.rows[2]['fields'][0]['reviewed_value'])
        self.assertEqual(arrows['field_kind'],'arrows')
        self.assertEqual(arrows['node_reading_ids'],{'a':'node-a','b':'node-b'})
        rows=self.candidates(out);context=build_context([rows[2]],100000,len)
        self.assertEqual([r['chunk_id'] for r in context['evidence']],[c['chunk_id'] for c in out['chunks']])
        display=json.loads(context['evidence'][0]['text'])['fields'][0]
        self.assertEqual(display['value'],arrows['value']);self.assertEqual(display['node_reading_ids'],arrows['node_reading_ids'])
        self.assertEqual(len(context['evidence'][0]['citations']),3)
        self.assertFalse(build_context([rows[2]],len(context['context'])-1,len)['evidence'])
        rows[2]['neighbors']=rows[2]['neighbors'][:1]
        self.assertFalse(build_context([rows[2]],100000,len)['evidence'])
        self.assertFalse(self.build(self.eligible(),token_cap=8)['chunks'])

    def test_missing_opt_in_or_binding_never_emits_partial_flowchart(self):
        p=self.eligible()
        for changes in [{'include_source_limits':False},{'flowchart_bindings':{}}]:
            with self.subTest(changes=changes):self.assertFalse(self.build(p,**changes)['chunks'])
        # Graph dependencies are mandatory even if the caller omits the sidecar.
        out=self.build(p,required_readings={});rows=self.candidates(out)
        rows[0]['neighbors']=[]
        self.assertFalse(build_context([rows[0]],100000,len)['evidence'])

    def test_shared_citations_preserve_ordered_graph_and_reject_bad_node_citation(self):
        out=self.build(self.eligible(),compact_context=True);rows=self.candidates(out)
        original=build_context([rows[-1]],100000,len,compact_citations=True)
        shared=build_context([rows[-1]],100000,len,shared_citations=True)
        self.assertEqual(shared['evidence'],original['evidence'])
        self.assertEqual(shared['gaps'],[])
        self.assertIn('"node_reading_ids":{"a":"node-a","b":"node-b"}',shared['context'])
        self.assertLess(shared['context_tokens'],original['context_tokens'])
        rows[1]['spans'][0]['page']=None
        changed=build_context([rows[-1]],100000,len,shared_citations=True)
        self.assertEqual(changed['evidence'],[])
        self.assertTrue(changed['gaps'])

    def test_partial_reviews_excluded_nodes_and_invalid_terminal_are_rejected(self):
        for edit in ['excluded','review','gaps','terminal']:
            mapping=self.f.map()
            if edit=='excluded':mapping['preparation']['readings'][0]['applicability']='excluded'
            elif edit=='review':mapping['preparation']['readings'][0]['fields'][0]['decision']='pending'
            elif edit=='gaps':mapping['preparation']['readings'][0]['gaps']=[{'issue':'source_cutoff'}]
            with self.subTest(edit=edit),self.assertRaises(ValueError):
                self.prepare(mapping,terminal_region=[0,0,2000,50] if edit=='terminal' else [60,340,140,380])

    def test_graph_evidence_cannot_differ_from_exact_reviewed_rows_and_spans(self):
        for edit in ['direction','label','terminal','node','event','page','version']:
            p=self.eligible();graph=p['flowchart_bindings']['arrows']
            if edit=='direction':graph['edges'][0]['from']='b'
            elif edit=='label':graph['edges'][0]['label_span']['text']='Maybe'
            elif edit=='terminal':graph['terminal']['span']['text']='Done'
            elif edit=='node':graph['nodes'][0]['fields'][0]['value']='Different instruction.'
            elif edit=='event':graph['edges'][0]['event_sha256']='b'*64
            elif edit=='page':graph['edges'][0]['label_span']['page']=3
            else:graph['version_id']='different-version'
            with self.subTest(edit=edit),self.assertRaises(ValueError):self.build(p)

    def test_stored_roundtrip_and_malformed_structures_fail_closed(self):
        result=self.build(self.eligible())
        rows=json.loads(json.dumps([{k:v for k,v in r.items() if k!='neighbors'}
            for r in self.candidates(result)],sort_keys=True))
        for row in rows:row['neighbors']=[r for r in rows if r is not row]
        for row in rows:
            chunk=row['chunk'];chunk.pop('spans');chunk.pop('schema_version')
            for i,span in enumerate(row['spans']):
                span.pop('schema_version');span.update(chunk_id=chunk['chunk_id'],span_order=i)
        self.assertEqual(len(build_context([rows[1]],100000,len)['evidence']),3)
        for edit in ['endpoint','duplicate','missing_terminal','node_mapping','node_substitution','field_kind']:
            bad=copy.deepcopy(rows);root=bad[0]['chunk'];field=root['type_fields']['field_associations'][0]
            if edit=='endpoint':field['value'][0]['to']='unknown'
            elif edit=='duplicate':field['value'].append(copy.deepcopy(field['value'][0]))
            elif edit=='missing_terminal':field['value'][1]['to']='b'
            elif edit=='node_mapping':field['node_reading_ids']['b']='substituted'
            elif edit=='node_substitution':bad[2]['chunk']['type_fields']['reading_id']='substituted'
            else:field['field_kind']='arbitrary_array'
            root['text']=serialize_reviewed_fields(root['type_fields']['field_associations'],[],root['type_fields']['service_group'])
            root['content_hash']=compute_content_hash(root['source_text'],root['text'])
            with self.subTest(edit=edit):self.assertFalse(build_context([bad[0]],100000,len)['evidence'])

    def test_malformed_node_mapping_and_field_records_are_withheld_without_crashing(self):
        rows=self.candidates(self.build(self.eligible()))
        for value in [None,[],False,'node-a']:
            bad=copy.deepcopy(rows)
            bad[0]['chunk']['type_fields']['field_associations'][0]['node_reading_ids']=value
            with self.subTest(mapping=value):self.assertFalse(build_context([bad[0]],100000,len)['evidence'])
        for value in [None,42,[]]:
            bad=copy.deepcopy(rows)
            bad[0]['chunk']['type_fields']['field_associations']=[value]
            with self.subTest(field=value):self.assertFalse(build_context([bad[0]],100000,len)['evidence'])

    def test_displayed_node_identity_resolves_each_structured_endpoint(self):
        rows=self.candidates(self.build(self.eligible()))
        context=build_context([rows[2]],100000,len)
        displayed=[json.loads(r['text']) for r in context['evidence']]
        self.assertEqual([p['service_group']['part_reading_id'] for p in displayed],['arrows','node-a','node-b'])
        mapping=displayed[0]['fields'][0]['node_reading_ids']
        self.assertEqual(set(mapping.values()),{p['service_group']['part_reading_id'] for p in displayed[1:]})
        for edit in ['missing','substitution']:
            bad=copy.deepcopy(rows);meta=bad[2]['chunk']['type_fields']['service_group']
            if edit=='missing':meta.pop('part_reading_id')
            else:meta['part_reading_id']='different-step'
            bad[2]['chunk']['text']=serialize_reviewed_fields(bad[2]['chunk']['type_fields']['field_associations'],[],meta)
            bad[2]['chunk']['content_hash']=compute_content_hash(bad[2]['chunk']['source_text'],bad[2]['chunk']['text'])
            with self.subTest(edit=edit):self.assertFalse(build_context([bad[0]],100000,len)['evidence'])

    def test_flowchart_nodes_must_stay_on_the_original_arrow_page(self):
        rows=self.candidates(self.build(self.eligible()))
        rows[1]['spans'][0]['page']=3
        self.assertFalse(build_context([rows[0]],100000,len)['evidence'])


if __name__=='__main__':unittest.main()
