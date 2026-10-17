"""Synthetic complete service-group context, never institutional approval."""
import copy
import unittest

import test_reviewed_service_steps as fixtures
from backend.bintanong_tools.document_ingest.reviewed_policy import build_reviewed_policy_bundle
from backend.bintanong_tools.document_ingest.reviewed_policy_chunks import build_reviewed_policy_chunks
from backend.bintanong_retrieval.context import build_context


class ReviewedServiceContextTests(unittest.TestCase):
    def setUp(self):
        self.f=fixtures.ReviewedServiceStepTests();self.f.setUp()

    def prepare(self,mapping=None):
        from backend.bintanong_tools.document_ingest.reviewed_service_context import prepare_reviewed_service_context
        return prepare_reviewed_service_context(self.f.mapping() if mapping is None else mapping,
            reading_id='client-step',subaction_ids=self.f.ids,fee_region=[300,20,400,60])

    def build(self,p=None,**options):
        p=self.prepare() if p is None else p
        bundle=build_reviewed_policy_bundle(p['readings'],sources={self.f.sha:self.f.data},review_events=self.f.events)
        return build_reviewed_policy_chunks(bundle,sources={self.f.sha:self.f.data},review_events=self.f.events,
            source_versions=[self.f.version],field_spans=p['field_spans'],
            required_readings=p['required_readings'],include_source_limits=options.get('opt_in',True),
            token_cap=options.get('token_cap',480))

    def approved_synthetic(self):
        self.f.row.update(applicability='undergraduate',applicability_evidence_ref='synthetic-scope#step')
        return self.prepare()

    def candidates(self,result):
        rows=[{'chunk':c,'spans':c['spans'],'version':self.f.version.model_dump(mode='json'),
            'neighbors':[],'similarity':0.9} for c in result['chunks']]
        for row in rows:row['neighbors']=[r for r in rows if r is not row]
        return rows

    def test_complete_projection_keeps_original_fee_one_parent_and_null_notes(self):
        mapping=self.f.mapping();before=copy.deepcopy(mapping);p=self.prepare(mapping)
        self.assertEqual(p['original_reading'],self.f.row)
        self.assertEqual(mapping,before)
        self.assertEqual(len(p['readings']),3)
        parent=p['readings'][0]
        self.assertEqual([f['name'] for f in parent['fields']],['client_instruction','shared_fee'])
        fee=parent['fields'][1]
        self.assertEqual(fee['reviewed_value'],'None')
        self.assertEqual(fee['locator']['evidence']['original_field'],self.f.row['fields'][1])
        self.assertEqual(p['field_spans'][parent['reading_id']]['shared_fee'][0]['page'],2)
        self.assertTrue(all('shared_fee' not in p['field_spans'][r['reading_id']] for r in p['readings'][1:]))
        note=next(f for f in p['readings'][2]['fields'] if f['name'].endswith('/condition_note'))
        self.assertIsNone(note['reviewed_value']);self.assertFalse(note['source_blank'])
        self.assertEqual(p['field_spans'][p['readings'][2]['reading_id']][note['name']],[])
        office=next(f for f in p['readings'][2]['fields'] if f['name'].endswith('/office'))
        self.assertEqual(office['locator']['physical_pages'],[3])
        self.assertEqual(p['required_readings'][parent['reading_id']],[r['reading_id'] for r in p['readings'][1:]])

    def test_unknown_applicability_remains_unknown_and_emits_no_actual_scope(self):
        p=self.prepare();out=self.build(p)
        self.assertFalse(out['chunks']);self.assertEqual(len(out['withheld']),3)
        self.assertTrue(all('undergraduate_applicability_required' in r['reasons'] for r in out['withheld']))
        self.assertTrue(all(r['applicability']=='unknown' for r in p['readings']))

    def test_synthetic_parts_under_cap_require_complete_group_and_single_parent_fee(self):
        p=self.approved_synthetic();out=self.build(p)
        self.assertEqual(len(out['chunks']),3)
        self.assertTrue(all(c['token_count']['count']<=480 for c in out['chunks']))
        rows=self.candidates(out);context=build_context([rows[2]],100000,len)
        self.assertEqual(len(context['evidence']),3)
        self.assertEqual([r['chunk_id'] for r in context['evidence']],
            [c['chunk_id'] for c in out['chunks']])
        self.assertIn('"part_order":0',context['context'])
        self.assertEqual(context['context'].count('"name":"shared_fee"'),1)
        self.assertIn('not_recorded',context['context'])
        self.assertIn('Additional conditions are not separately recorded',context['context'])
        self.assertIn('Evaluator / Records Officer',context['context'])
        self.assertIn('"action-2/office"',context['context'])
        small=build_context([rows[2]],len(context['context'])-1,len)
        self.assertFalse(small['evidence'])
        rows[2]['neighbors']=rows[2]['neighbors'][:1]
        self.assertFalse(build_context([rows[2]],100000,len)['evidence'])
        self.assertFalse(self.build(p,token_cap=8)['chunks'])
        self.assertFalse(self.build(p,opt_in=False)['chunks'])

    def test_invalid_or_partial_confirmed_step_cannot_be_projected(self):
        for edit in ['excluded','review','field','span']:
            mapping=self.f.mapping();row=mapping['preparation']['readings'][0]
            if edit=='excluded':row['applicability']='excluded'
            elif edit=='review':row['fields'][3]['decision']='pending'
            elif edit=='field':row['fields'].pop()
            else:mapping['field_spans']['client-step']['action-2/office'][0]['page']=2
            with self.subTest(edit=edit),self.assertRaises(ValueError):self.prepare(mapping)

    def test_null_clients_and_tampered_note_messages_do_not_become_context(self):
        p=self.approved_synthetic();p['readings'][0]['fields'][0]['reviewed_value']=None
        p['readings'][0]['fields'][0]['original_value']=None
        p['field_spans'][p['readings'][0]['reading_id']]['client_instruction']=[]
        self.assertFalse(self.build(p)['chunks'])
        p=self.approved_synthetic();rows=self.candidates(self.build(p))
        candidate=copy.deepcopy(rows[2]);candidate['neighbors']=[]
        association=next(f for f in candidate['chunk']['type_fields']['field_associations'] if f['value'] is None)
        association['field_state']='no_conditions'
        candidate['chunk']['type_fields']['required_neighbor_chunk_ids']=[]
        self.assertFalse(build_context([candidate],100000,len)['evidence'])

    def test_impossible_declared_group_size_is_withheld_without_allocation(self):
        rows=self.candidates(self.build(self.approved_synthetic()))
        for row in rows:row['chunk']['type_fields']['service_group']['part_count']=2**65
        self.assertFalse(build_context([rows[0]],100000,len)['evidence'])


if __name__=='__main__':unittest.main()
