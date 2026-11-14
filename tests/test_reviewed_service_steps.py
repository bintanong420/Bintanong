"""Synthetic logical-step associations, continuation labels, parent fees and null notes."""
import copy, hashlib, json, unittest

from backend.bintanong_tools.document_ingest.register import mint_pending_register
from backend.bintanong_tools.document_ingest.reviewed_policy import build_reviewed_policy_bundle
from backend.bintanong_tools.document_ingest.reviewed_image_spans import map_reviewed_image_spans


class ReviewedServiceStepTests(unittest.TestCase):
    def setUp(self):
        self.data=b'synthetic service source'
        self.sha=hashlib.sha256(self.data).hexdigest()
        self.version=mint_pending_register([{'filename':'synthetic.pdf','sha256':self.sha,
            'acquisition_locator':'shelf:service'}],synthetic=True)[0]
        event=json.dumps({'source_sha256':self.sha,'owner_statement':'Synthetic step readings match.'}).encode()
        self.ev=hashlib.sha256(event).hexdigest();self.events={self.ev:event}
        self.images={2:b'synthetic page2',3:b'synthetic page3'}
        self.pages={(self.sha,p):{'image_sha256':hashlib.sha256(data).hexdigest(),
            'image_size':[1200,1600],'page_size':[600,800],'scale':2,'rotation':0,'crop':None}
            for p,data in self.images.items()}
        self.ids=['action-1','action-2']
        self.row={'reading_id':'client-step','source_sha256':self.sha,'version_id':self.version.version_id,
            'intended_audience':'undergraduate','applicability':'unknown','applicability_evidence_ref':None,
            'fields':[],'gaps':[],'preserved_evidence':[{'artifact':'synthetic-review.json','sha256':'a'*64}]}
        self.row['fields']=[self.field('client_instruction','Submit the form.',2),
            self.field('shared_fee',{'text':'None','source_page':2,'applies_to':'logical_client_step_1'},2)]
        for identity in self.ids:
            values={'subaction_id':identity,'action':'Check the form.','condition_note':None,
                'processing_time':'10 minutes','responsible_person':'Evaluator / Records Officer',
                'office':'Registry','action_source_pages':[2],'role_source_pages':[2],
                'office_source_pages':[3 if identity=='action-2' else 2]}
            if identity=='action-1':values['condition_note']='Present originals.'
            for name in ('action','condition_note','processing_time','responsible_person','office'):
                page=values['office_source_pages'][0] if name=='office' else 2
                self.row['fields'].append(self.field(identity+'/'+name,values[name],page,values))

    def field(self,name,value,page,evidence=None):
        return {'name':name,'original_value':value,'reviewed_value':value,'source_blank':False,
            'decision':'accepted','review_event_sha256':self.ev,
            'locator':{'physical_pages':[page],'field':name,'evidence':copy.deepcopy(evidence or {'basis':'synthetic review'})}}

    def mapping(self):
        bundle=build_reviewed_policy_bundle([self.row],sources={self.sha:self.data},review_events=self.events)
        regions={}
        for index,field in enumerate(self.row['fields']):
            if not isinstance(field['reviewed_value'],str):continue
            page=field['locator']['physical_pages'][0]
            regions[field['name']]={'reading_id':'client-step','field_name':field['name'],
                'source_sha256':self.sha,'version_id':self.version.version_id,'physical_page':page,
                'original_value':field['original_value'],'reviewed_value':field['reviewed_value'],
                'original_evidence':copy.deepcopy(field['locator']['evidence']),
                'image_sha256':self.pages[(self.sha,page)]['image_sha256'],
                'pixel_region':[20,index*50+20,240,index*50+60],'region_origin':'TOPLEFT_pixels'}
        def reader(data,page):
            self.assertEqual(data,self.data)
            return {**self.pages[(self.sha,page)],'image_bytes':self.images[page]}
        return map_reviewed_image_spans(bundle,sources={self.sha:self.data},review_events=self.events,
            source_versions=[self.version],image_pages=self.pages,read_page_image=reader,
            field_region_bindings={'client-step':regions})

    def bind(self,mapping=None,**options):
        from backend.bintanong_tools.document_ingest.reviewed_service_steps import bind_reviewed_service_step
        return bind_reviewed_service_step(self.mapping() if mapping is None else mapping,
            reading_id='client-step',subaction_ids=options.get('subaction_ids',self.ids),
            fee_region=options.get('fee_region',[300,20,400,60]))

    def test_complete_step_keeps_joint_role_cross_page_office_and_single_parent_fee(self):
        result=self.bind()
        self.assertTrue(result['candidate_only']);self.assertFalse(result['activation_eligible'])
        self.assertEqual([a['subaction_id'] for a in result['subactions']],self.ids)
        fields=result['subactions'][1]['fields']
        self.assertEqual(fields['responsible_person']['value'],'Evaluator / Records Officer')
        self.assertEqual(fields['responsible_person']['spans'][0]['page'],2)
        self.assertEqual(fields['office']['spans'][0]['page'],3)
        self.assertEqual(result['shared_fee']['value']['text'],'None')
        self.assertEqual(result['shared_fee']['span']['page'],2)
        self.assertEqual(result['shared_fee']['value']['applies_to'],'logical_client_step_1')
        self.assertTrue(all('shared_fee' not in a for a in result['subactions']))

    def test_null_note_is_unrecorded_and_not_a_blank_or_no_condition(self):
        note=self.bind()['subactions'][1]['fields']['condition_note']
        self.assertIsNone(note['value']);self.assertEqual(note['state'],'not_recorded')
        self.assertEqual(note['spans'],[])
        self.assertFalse(note['source_blank'])
        self.assertEqual(self.bind()['subactions'][0]['fields']['condition_note']['value'],'Present originals.')

    def test_client_instruction_cannot_be_an_unrecorded_null_note(self):
        mapping=self.mapping();client=mapping['preparation']['readings'][0]['fields'][0]
        client.update(original_value=None,reviewed_value=None)
        mapping['field_spans']['client-step'].pop('client_instruction')
        with self.assertRaises(ValueError):self.bind(mapping)

    def test_service_step_requires_exact_order_and_complete_subaction_set(self):
        for ids in ([],self.ids[::-1],self.ids[:1],self.ids+[self.ids[0]],self.ids+['missing']):
            with self.subTest(ids=ids):
                with self.assertRaises(ValueError):self.bind(subaction_ids=ids)

    def test_missing_or_changed_field_spans_withhold_whole_step(self):
        for edit in ('missing','text','source','page','geometry','proof'):
            with self.subTest(edit=edit):
                mapping=self.mapping();name='action-2/office'
                if edit=='missing':mapping['field_spans']['client-step'].pop(name)
                else:
                    span=mapping['field_spans']['client-step'][name][0]
                    if edit=='text':span['text']='Another office.'
                    if edit=='source':span['byte_sha256']='b'*64
                    if edit=='page':span['page']=2
                    if edit=='geometry':span['bbox']=None
                    if edit=='proof':mapping['mapping_evidence']=[e for e in mapping['mapping_evidence'] if e['field_name']!=name]
                with self.assertRaises(ValueError):self.bind(mapping)

    def test_partial_review_gaps_excluded_audience_or_changed_association_never_bind(self):
        for edit in ('review','gap','audience','association','location','null_spans'):
            with self.subTest(edit=edit):
                mapping=self.mapping();row=mapping['preparation']['readings'][0]
                field=next(f for f in row['fields'] if f['name']=='action-2/office')
                if edit=='review':field['decision']='pending'
                if edit=='gap':row['gaps']=[{'gap_id':'synthetic-gap'}]
                if edit=='audience':row['intended_audience']='staff'
                if edit=='association':field['locator']['evidence']['subaction_id']='action-1'
                if edit=='location':field['locator']['evidence']['office_source_pages']=[2]
                if edit=='null_spans':mapping['field_spans']['client-step']['action-2/condition_note']=[mapping['field_spans']['client-step']['action-2/office'][0]]
                with self.assertRaises(ValueError):self.bind(mapping)

    def test_fee_must_be_confirmed_source_located_parent_value(self):
        for edit in ('review','page','text','scope','missing_page','blank','region'):
            with self.subTest(edit=edit):
                mapping=self.mapping();fee=mapping['preparation']['readings'][0]['fields'][1]
                options={}
                if edit=='review':fee['decision']='pending'
                if edit=='page':fee['reviewed_value']['source_page']=3
                if edit=='text':fee['reviewed_value']['text']=None
                if edit=='scope':fee['reviewed_value']['applies_to']='every_subaction'
                if edit=='missing_page':mapping['validated_pages']=[p for p in mapping['validated_pages'] if p['physical_page']!=2]
                if edit=='blank':fee['source_blank']=True
                if edit=='region':options['fee_region']=[0,0,2000,50]
                with self.assertRaises(ValueError):self.bind(mapping,**options)

    def test_parent_fee_retains_owner_accepted_annotation_without_changing_value(self):
        mapping=self.mapping();fee=mapping['preparation']['readings'][0]['fields'][1]
        fee['original_value']={**fee['reviewed_value'],'review':'owner_accepted'}
        before=copy.deepcopy(mapping)
        result=self.bind(mapping)
        self.assertEqual(result['shared_fee']['value'],fee['reviewed_value'])
        self.assertEqual(mapping,before)
        fee['original_value']['review']='pending'
        with self.assertRaises(ValueError):self.bind(mapping)
        fee['original_value']={**fee['reviewed_value'],'text':'Other fee','review':'owner_accepted'}
        with self.assertRaises(ValueError):self.bind(mapping)

    def test_binder_copies_all_inputs_and_remains_inactive_with_unknown_applicability(self):
        mapping=self.mapping();before=copy.deepcopy((mapping,self.ids))
        result=self.bind(mapping)
        self.assertFalse(result['source_governance_changed'])
        self.assertEqual(result['applicability'],'unknown')
        result['subactions'][0]['fields']['action']['value']='Changed'
        result['shared_fee']['value']['text']='Changed'
        self.assertEqual((mapping,self.ids),before)


if __name__=='__main__':unittest.main()
