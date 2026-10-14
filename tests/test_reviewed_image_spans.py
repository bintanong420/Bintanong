"""Synthetic full-page render identity, reviewed image fields and directional graphs."""
import copy
import hashlib
import json
import unittest

from backend.bintanong_tools.document_ingest.register import mint_pending_register
from backend.bintanong_tools.document_ingest.reviewed_policy import build_reviewed_policy_bundle
from backend.bintanong_tools.document_ingest.reviewed_policy_chunks import build_reviewed_policy_chunks


class ImageFieldSpanTests(unittest.TestCase):
    def setUp(self):
        self.data=b'synthetic original source'
        self.sha=hashlib.sha256(self.data).hexdigest()
        self.sources={self.sha:self.data}
        self.image=b'synthetic full page render'
        self.image_sha=hashlib.sha256(self.image).hexdigest()
        self.version=mint_pending_register([{'filename':'synthetic.pdf','sha256':self.sha,
            'acquisition_locator':'shelf:synthetic-image'}],synthetic=True)[0]
        self.event=json.dumps({'source_sha256':self.sha,'owner_statement':'Displayed synthetic fields and arrows match.'}).encode()
        self.ev=hashlib.sha256(self.event).hexdigest()
        self.events={self.ev:self.event}
        self.rows=[self.row('node-a')]
        self.pages={(self.sha,2):{'image_sha256':self.image_sha,'image_size':[1200,1600],
            'page_size':[600,800],'scale':2,'rotation':0,'crop':None}}
        self.observed={**self.pages[(self.sha,2)],'image_bytes':self.image}
        self.calls=[]

    def field(self,name='instruction',value='Get the form.'):
        return {'name':name,'original_value':value,'reviewed_value':value,'source_blank':False,
            'decision':'accepted','review_event_sha256':self.ev,
            'locator':{'physical_pages':[2],'field':name,'evidence':{'field':name,'proposed_reading':value,
                'proposed_image_region':[20,40,120,100],'region_origin':'TOPLEFT_pixels',
                'region_basis':'original image visual review region'}}}

    def row(self,identity):
        return {'reading_id':identity,'source_sha256':self.sha,'version_id':self.version.version_id,
            'intended_audience':'undergraduate','applicability':'unknown','applicability_evidence_ref':None,
            'fields':[self.field()],'gaps':[],
            'preserved_evidence':[{'artifact':'synthetic-layout.json','sha256':'a'*64}]}

    def prep(self):
        return build_reviewed_policy_bundle(self.rows,sources=self.sources,review_events=self.events)

    def reader(self,data,page):
        self.calls.append((data,page))
        return copy.deepcopy(self.observed)

    def map(self,bundle=None,reader=None,**changes):
        from backend.bintanong_tools.document_ingest.reviewed_image_spans import map_reviewed_image_spans
        return map_reviewed_image_spans(self.prep() if bundle is None else bundle,sources=self.sources,
            review_events=self.events,source_versions=[self.version],image_pages=self.pages,
            read_page_image=reader or self.reader,**changes)

    def correction_setup(self):
        field=self.rows[0]['fields'][0]
        field.update(decision='corrected',reviewed_value='Get the corrected form.')
        event={'source_sha256':self.sha,'owner_statement':'The corrected synthetic field matches.',
            'physical_page':2,'original_image_sha256':self.image_sha,
            'reviewed_rows':[{'row_id':'row-1','fields':[{'field':'instruction',
                'original_proposal_text':field['original_value'],'reviewed_text':field['reviewed_value'],
                'review_decision':'corrected','original_image_evidence':copy.deepcopy(field['locator']['evidence'])}]}]}
        return event

    def set_correction_event(self,event):
        data=json.dumps(event).encode()
        digest=hashlib.sha256(data).hexdigest()
        self.events={digest:data}
        self.rows[0]['fields'][0]['review_event_sha256']=digest

    def test_corrected_field_maps_only_with_exact_event_and_preserves_original(self):
        event=self.correction_setup()
        self.set_correction_event(event)
        before=copy.deepcopy(self.rows)
        result=self.map(correction_rows={'node-a':'row-1'})
        span=result['field_spans']['node-a']['instruction'][0]
        self.assertEqual(span['text'],'Get the corrected form.')
        evidence=result['mapping_evidence'][0]
        self.assertEqual(evidence['original_evidence']['proposed_reading'],'Get the form.')
        self.assertEqual(evidence['correction_review']['event_row_id'],'row-1')
        self.assertEqual(evidence['correction_review']['field_review'],event['reviewed_rows'][0]['fields'][0])
        self.assertEqual(self.rows,before)
        self.assertEqual(result['preparation']['readings'][0]['fields'][0]['original_value'],'Get the form.')

    def test_correction_without_selected_event_row_stays_unmapped(self):
        self.set_correction_event(self.correction_setup())
        for aliases in (None,{}, {'node-a':'missing'}):
            with self.subTest(aliases=aliases):
                result=self.map(correction_rows=aliases)
                self.assertFalse(result['field_spans'])
                self.assertEqual(result['withheld_fields'][0]['reason'],'correction_review_mismatch')

    def test_preparation_decision_annotation_does_not_replace_original_event_evidence(self):
        event=self.correction_setup()
        self.set_correction_event(event)
        evidence=self.rows[0]['fields'][0]['locator']['evidence']
        evidence['recorded_decision']='corrected'
        result=self.map(correction_rows={'node-a':'row-1'})
        self.assertEqual(result['field_spans']['node-a']['instruction'][0]['text'],'Get the corrected form.')
        self.assertEqual(result['mapping_evidence'][0]['original_evidence']['recorded_decision'],'corrected')
        evidence['recorded_decision']='accepted'
        self.assertFalse(self.map(correction_rows={'node-a':'row-1'})['field_spans'])
        evidence['recorded_decision']='corrected'
        evidence['unreviewed_change']='other'
        self.assertFalse(self.map(correction_rows={'node-a':'row-1'})['field_spans'])

    def test_corrected_review_source_page_image_original_text_and_region_must_match(self):
        original=self.correction_setup()
        mutations=[('physical_page',3),('original_image_sha256','c'*64),
            ('field','other'),('review_decision','accepted'),('original_proposal_text','other'),
            ('reviewed_text','other'),('original_image_evidence',{})]
        for key,value in mutations:
            with self.subTest(key=key):
                event=copy.deepcopy(original)
                target=event if key in {'physical_page','original_image_sha256'} else event['reviewed_rows'][0]['fields'][0]
                target[key]=value
                self.set_correction_event(event)
                result=self.map(correction_rows={'node-a':'row-1'})
                self.assertFalse(result['field_spans'])
                self.assertEqual(result['withheld_fields'][0]['reason'],'correction_review_mismatch')

    def test_ambiguous_corrected_event_rows_or_fields_are_withheld(self):
        original=self.correction_setup()
        for duplicate in ('rows','fields'):
            event=copy.deepcopy(original)
            target=event['reviewed_rows'] if duplicate=='rows' else event['reviewed_rows'][0]['fields']
            target.append(copy.deepcopy(target[0]))
            self.set_correction_event(event)
            result=self.map(correction_rows={'node-a':'row-1'})
            self.assertFalse(result['field_spans'])
            self.assertEqual(result['withheld_fields'][0]['reason'],'correction_review_mismatch')

    def test_mapping_corrected_visible_fragment_preserves_gap_and_chunk_withholding(self):
        self.set_correction_event(self.correction_setup())
        self.rows[0]['gaps']=[{'gap_id':'clipped','field_names':['instruction'],'issue':'source_cutoff',
            'visible_text':'Get the corrected form.','affected_claims':['remaining steps'],
            'locator':{'physical_pages':[2],'field':'instruction'}}]
        prep=self.prep()
        result=self.map(prep,correction_rows={'node-a':'row-1'})
        self.assertEqual(result['preparation']['readings'][0]['gaps'],prep['readings'][0]['gaps'])
        pending=build_reviewed_policy_chunks(prep,sources=self.sources,review_events=self.events,
            source_versions=[self.version],field_spans=result['field_spans'])
        self.assertEqual(pending['chunks'],[])
        self.assertIn('source_gap_requires_context_support',pending['withheld'][0]['reasons'])

    def graph_setup(self):
        second=self.row('node-b')
        second['fields'][0]['locator']['evidence']['proposed_image_region']=[20,200,120,260]
        arrows=self.row('arrows')
        value=[{'from':'a','label':'Yes','to':'b'},{'from':'a','label':'No','to':'END'}]
        arrows['fields']=[self.field('arrows',value)]
        self.rows += [second,arrows]
        return [{'from':'a','label':'Yes','to':'b','pixel_region':[60,100,100,200]},
            {'from':'a','label':'No','to':'END','pixel_region':[120,80,180,350]}]

    def table_setup(self,kind='source_region_pixels',blank=False):
        field=self.rows[0]['fields'][0]
        evidence=field['locator']['evidence']
        evidence.pop('proposed_image_region')
        evidence.pop('region_origin')
        evidence.update(proposed_blank=blank,original_native_region_text='neighbor glyph overhang')
        if kind=='source_region_pixels':
            evidence['source_region']=[20,40,120,100]
        else:
            evidence['raw_cell']={'bbox':{'l':10,'t':20,'r':60,'b':50,'coord_origin':'TOPLEFT'},
                'text':'retained raw diagnostic','start_col_offset_idx':0}
        if blank:
            field.update(original_value='',reviewed_value='',source_blank=True)
            evidence['proposed_reading']=''
        return {(self.sha,2):kind}

    def region_binding(self):
        field=self.rows[0]['fields'][0]
        field['locator']['evidence']={'basis':'confirmed original logical-step field'}
        return {'node-a':{'instruction':{'reading_id':'node-a','field_name':'instruction',
            'source_sha256':self.sha,'version_id':self.version.version_id,'physical_page':2,
            'original_value':field['original_value'],'reviewed_value':field['reviewed_value'],
            'original_evidence':copy.deepcopy(field['locator']['evidence']),
            'image_sha256':self.image_sha,'pixel_region':[20,40,120,100],
            'region_origin':'TOPLEFT_pixels'}}}

    def test_explicit_region_binding_keeps_original_paginated_evidence(self):
        bindings=self.region_binding()
        before=copy.deepcopy((self.rows,bindings,self.pages,self.events))
        result=self.map(field_region_bindings=bindings)
        record=result['mapping_evidence'][0]
        self.assertEqual(record['span']['bbox'],[10,20,60,50])
        self.assertEqual(record['span']['text'],'Get the form.')
        self.assertEqual(record['region_binding'],bindings['node-a']['instruction'])
        self.assertEqual(record['original_evidence'],{'basis':'confirmed original logical-step field'})
        self.assertEqual((self.rows,bindings,self.pages,self.events),before)

    def test_region_binding_source_value_page_render_and_evidence_are_exact(self):
        original=self.region_binding()
        for key,value in {'reading_id':'other','field_name':'other','source_sha256':'b'*64,
            'version_id':'other','physical_page':3,'original_value':'Other original.',
            'reviewed_value':'Other instruction.','original_evidence':{'basis':'other'},
            'image_sha256':'b'*64,'region_origin':'BOTTOMLEFT_pixels'}.items():
            with self.subTest(key=key):
                bindings=copy.deepcopy(original)
                bindings['node-a']['instruction'][key]=value
                result=self.map(field_region_bindings=bindings)
                self.assertFalse(result['field_spans'])
                self.assertEqual(result['withheld_fields'][0]['reason'],'original_region_binding_mismatch')

    def test_region_binding_requires_known_reading_and_field_names(self):
        self.region_binding()
        for bindings in ([],{'missing':{}},{'node-a':{'missing':{}}},{'node-a':[]}):
            with self.subTest(bindings=bindings):
                with self.assertRaisesRegex(ValueError,'region binding'):
                    self.map(field_region_bindings=bindings)

    def test_region_binding_never_overrides_saved_table_or_image_regions(self):
        bindings=self.region_binding()
        evidence=self.rows[0]['fields'][0]['locator']['evidence']
        evidence.update(field='instruction',proposed_reading='Get the form.',
            proposed_image_region=[40,80,240,200],region_origin='TOPLEFT_pixels')
        result=self.map(field_region_bindings=bindings)
        self.assertEqual(result['field_spans']['node-a']['instruction'][0]['bbox'],[20,40,120,100])
        self.assertNotIn('region_binding',result['mapping_evidence'][0])
        evidence.pop('proposed_image_region');evidence.pop('region_origin')
        evidence.update(proposed_blank=False,source_region=[40,80,240,200])
        result=self.map(field_region_bindings=bindings,table_region_formats={(self.sha,2):'source_region_pixels'})
        self.assertEqual(result['field_spans']['node-a']['instruction'][0]['bbox'],[20,40,120,100])

    def test_binding_does_not_replace_retained_table_geometry_without_a_declared_format(self):
        bindings=self.region_binding()
        evidence=self.rows[0]['fields'][0]['locator']['evidence']
        evidence['source_region']=[40,80,240,200]
        bindings['node-a']['instruction']['original_evidence']=copy.deepcopy(evidence)
        self.assertFalse(self.map(field_region_bindings=bindings)['field_spans'])

    def test_binding_for_missing_geometry_can_share_a_page_with_retained_table_fields(self):
        bindings=self.region_binding()
        result=self.map(field_region_bindings=bindings,
            table_region_formats={(self.sha,2):'source_region_pixels'})
        self.assertEqual(result['field_spans']['node-a']['instruction'][0]['text'],'Get the form.')

    def test_region_binding_cannot_bypass_partial_review_or_render_geometry(self):
        for edit in ('review','audience','pages','render','box'):
            with self.subTest(edit=edit):
                self.setUp();bindings=self.region_binding()
                if edit=='review':self.rows[0]['fields'][0]['decision']='pending'
                if edit=='audience':self.rows[0]['intended_audience']='staff'
                if edit=='pages':self.rows[0]['fields'][0]['locator']['physical_pages']=[2,3]
                if edit=='render':self.observed['image_bytes']=b'changed render'
                if edit=='box':bindings['node-a']['instruction']['pixel_region']=[0,0,1300,50]
                self.assertFalse(self.map(field_region_bindings=bindings)['field_spans'])

    def test_changed_corrected_field_cannot_use_region_binding_as_a_review(self):
        bindings=self.region_binding()
        self.rows[0]['fields'][0].update(decision='corrected',reviewed_value='Changed instruction.')
        bindings['node-a']['instruction']['reviewed_value']='Changed instruction.'
        result=self.map(field_region_bindings=bindings)
        self.assertFalse(result['field_spans'])
        self.assertEqual(result['withheld_fields'][0]['reason'],'correction_review_mismatch')

    def test_retained_pixel_or_point_table_region_keeps_reviewed_column_text(self):
        for kind in ('source_region_pixels','raw_cell_points'):
            with self.subTest(kind=kind):
                self.setUp()
                formats=self.table_setup(kind)
                result=self.map(table_region_formats=formats)
                record=result['mapping_evidence'][0]
                self.assertEqual(record['span']['text'],'Get the form.')
                self.assertEqual(record['span']['bbox'],[10,20,60,50])
                self.assertEqual(record['pixel_region'],[20,40,120,100])
                self.assertEqual(record['region_format'],kind)
                self.assertEqual(record['original_evidence'],self.rows[0]['fields'][0]['locator']['evidence'])
                self.assertEqual(record['span']['locator']['cell_ids'],[])
                self.assertEqual(len(self.calls),1)

    def test_reviewed_blank_maps_empty_spans_despite_neighbor_glyph_diagnostic(self):
        for kind in ('source_region_pixels','raw_cell_points'):
            with self.subTest(kind=kind):
                self.setUp()
                formats=self.table_setup(kind,blank=True)
                result=self.map(table_region_formats=formats)
                self.assertEqual(result['field_spans'],{'node-a':{'instruction':[]}})
                record=result['mapping_evidence'][0]
                self.assertTrue(record['source_blank'])
                self.assertIsNone(record['span'])
                self.assertEqual(record['pixel_region'],[20,40,120,100])
                self.assertEqual(record['original_evidence']['original_native_region_text'],'neighbor glyph overhang')
                self.assertEqual(len(self.calls),1)

    def test_table_coordinate_format_is_explicit_and_never_guessed(self):
        self.table_setup()
        for formats in ({},{(self.sha,2):'pixels'},{(self.sha,2):'raw_cell_points'},
                        {(self.sha,3):'source_region_pixels'}, {(self.sha,2):[]}, {(self.sha,2):{}}):
            with self.subTest(formats=formats):
                self.assertFalse(self.map(table_region_formats=formats)['field_spans'])
        with self.assertRaisesRegex(ValueError,'table region formats'):
            self.map(table_region_formats=[])

    def test_blank_flag_must_be_literal_and_match_reviewed_empty_value(self):
        for value in (None,False,1,'true'):
            with self.subTest(value=value):
                self.setUp()
                formats=self.table_setup(blank=True)
                self.rows[0]['fields'][0]['locator']['evidence']['proposed_blank']=value
                self.assertFalse(self.map(table_region_formats=formats)['field_spans'])
        self.setUp()
        formats=self.table_setup()
        self.rows[0]['fields'][0]['locator']['evidence']['proposed_blank']=True
        self.assertFalse(self.map(table_region_formats=formats)['field_spans'])

    def test_invalid_retained_table_regions_never_map_text_or_blank(self):
        for blank in (False,True):
            for kind in ('source_region_pixels','raw_cell_points'):
                for box in ([0,0,1300,50],[10,50,60,20],[10,20,float('inf'),50],[10,20,60]):
                    with self.subTest(blank=blank,kind=kind,box=box):
                        self.setUp()
                        formats=self.table_setup(kind,blank)
                        evidence=self.rows[0]['fields'][0]['locator']['evidence']
                        if kind=='source_region_pixels':
                            evidence['source_region']=box
                        else:
                            evidence['raw_cell']['bbox']=dict(zip(('l','t','r','b'),box),coord_origin='TOPLEFT')
                        # Nonfinite preparation itself must fail before mapping.
                        if any(n==float('inf') for n in box):
                            with self.assertRaises(ValueError):self.map(table_region_formats=formats)
                        else:
                            self.assertFalse(self.map(table_region_formats=formats)['field_spans'])

    def test_raw_cell_origin_and_confirmed_field_association_are_required(self):
        for edit in ('origin','field','reading','page','decision','audience'):
            with self.subTest(edit=edit):
                self.setUp()
                formats=self.table_setup('raw_cell_points')
                field=self.rows[0]['fields'][0]
                evidence=field['locator']['evidence']
                if edit=='origin':evidence['raw_cell']['bbox']['coord_origin']='BOTTOMLEFT'
                if edit=='field':evidence['field']='other penalty'
                if edit=='reading':evidence['proposed_reading']='Other text.'
                if edit=='page':field['locator']['physical_pages']=[2,3]
                if edit=='decision':field['decision']='pending'
                if edit=='audience':self.rows[0]['intended_audience']='staff'
                self.assertFalse(self.map(table_region_formats=formats)['field_spans'])

    def test_table_blank_requires_matching_original_render(self):
        formats=self.table_setup(blank=True)
        self.observed['image_bytes']=b'different original image'
        result=self.map(table_region_formats=formats)
        self.assertFalse(result['field_spans'])
        self.assertEqual(result['withheld_fields'][0]['reason'],'original_image_mismatch')

    def test_explicit_absent_raw_blank_cell_retains_no_fabricated_region(self):
        formats=self.table_setup('raw_cell_points',blank=True)
        self.rows[0]['fields'][0]['locator']['evidence']['raw_cell']=None
        result=self.map(table_region_formats=formats)
        self.assertEqual(result['field_spans'],{'node-a':{'instruction':[]}})
        record=result['mapping_evidence'][0]
        self.assertIsNone(record['pixel_region'])
        self.assertIsNone(record['span'])
        self.assertEqual(len(self.calls),1)

    def test_absent_raw_cell_only_maps_an_explicit_confirmed_blank(self):
        for blank,missing in ((False,False),(True,True)):
            with self.subTest(blank=blank,missing=missing):
                self.setUp()
                formats=self.table_setup('raw_cell_points',blank=blank)
                evidence=self.rows[0]['fields'][0]['locator']['evidence']
                if missing:evidence.pop('raw_cell')
                else:evidence['raw_cell']=None
                self.assertFalse(self.map(table_region_formats=formats)['field_spans'])

    def test_table_format_cannot_bypass_corrected_field_event(self):
        formats=self.table_setup()
        self.rows[0]['fields'][0].update(decision='corrected',reviewed_value='Corrected instruction.')
        result=self.map(table_region_formats=formats)
        self.assertFalse(result['field_spans'])
        self.assertEqual(result['withheld_fields'][0]['reason'],'correction_review_mismatch')

    def test_table_mapping_preserves_inputs_gaps_and_applicability_withholding(self):
        formats=self.table_setup()
        self.rows[0]['gaps']=[{'gap_id':'condition','field_names':['instruction'],
            'issue':'malformed_source_condition','visible_text':'Get the form.',
            'affected_claims':['eligibility'],'locator':{'physical_pages':[2],'field':'instruction'}}]
        prep=self.prep()
        before=copy.deepcopy((prep,self.sources,self.events,self.pages,formats))
        result=self.map(prep,table_region_formats=formats)
        pending=build_reviewed_policy_chunks(prep,sources=self.sources,review_events=self.events,
            source_versions=[self.version],field_spans=result['field_spans'])
        self.assertEqual(pending['chunks'],[])
        self.assertIn('source_gap_requires_context_support',pending['withheld'][0]['reasons'])
        self.assertIn('undergraduate_applicability_required',pending['withheld'][0]['reasons'])
        self.assertEqual((prep,self.sources,self.events,self.pages,formats),before)
        result['mapping_evidence'][0]['original_evidence']['proposed_reading']='mutated'
        self.assertEqual((prep,self.sources,self.events,self.pages,formats),before)

    def bind(self,mapping,edges,**changes):
        from backend.bintanong_tools.document_ingest.reviewed_image_spans import bind_reviewed_flowchart
        args={'arrow_reading_id':'arrows','row_reading_ids':{'a':'node-a','b':'node-b'},
            'edge_regions':edges,'terminal_region':[60,340,140,380],**changes}
        return bind_reviewed_flowchart(mapping,**args)

    def test_exact_original_render_and_scale_yield_reviewed_image_region(self):
        result=self.map()
        span=result['field_spans']['node-a']['instruction'][0]
        self.assertEqual(span['bbox'],[10,20,60,50])
        self.assertEqual(span['bbox_origin'],'TOPLEFT')
        self.assertEqual(span['extraction']['source_kind'],'original_pdf_image')
        self.assertEqual(span['locator']['cell_ids'],[])
        self.assertEqual(span['locator']['item_ids'],['image-region:p2:instruction:20,40,120,100'])
        self.assertEqual(self.calls,[(self.data,2)])
        self.assertEqual(result['mapping_evidence'][0]['image_sha256'],self.image_sha)
        self.assertFalse(result['activation_eligible'])

    def test_source_or_render_change_and_cached_prep_tampering_are_rejected(self):
        prep=self.prep()
        self.sources[self.sha]=b'changed'
        with self.assertRaisesRegex(ValueError,'digest'):
            self.map(prep)
        self.sources[self.sha]=self.data
        prep['activation_eligible']=True
        with self.assertRaisesRegex(ValueError,'preparation'):
            self.map(prep)
        self.observed['image_bytes']=b'other'
        result=self.map()
        self.assertFalse(result['field_spans'])
        self.assertEqual(result['withheld_fields'][0]['reason'],'original_image_mismatch')

    def test_crop_rotation_dimensions_and_scale_are_not_guessed(self):
        original=copy.deepcopy(self.pages[(self.sha,2)])
        for change in [{'crop':[1,0,0,0]},{'rotation':90},{'image_size':[1201,1600]},
            {'scale':1},{'scale':True},{'page_size':[601,800]}]:
            self.pages[(self.sha,2)]={**original,**change}
            result=self.map()
            self.assertFalse(result['field_spans'])
            self.assertEqual(result['withheld_fields'][0]['reason'],'invalid_image_transform')
        self.pages[(self.sha,2)]=original

    def test_observed_page_dimensions_or_rotation_must_match_captured_page(self):
        for change in [{'image_size':[1201,1600]},{'page_size':[601,800]},
            {'rotation':90},{'crop':[1,0,0,0]}]:
            original=copy.deepcopy(self.observed)
            self.observed.update(change)
            self.assertEqual(self.map()['withheld_fields'][0]['reason'],'original_image_mismatch')
            self.observed=original

    def test_original_render_must_explicitly_report_crop_and_transform(self):
        original=copy.deepcopy(self.observed)
        for key in ['crop','scale','rotation','image_size','page_size']:
            with self.subTest(key=key):
                self.observed=copy.deepcopy(original)
                del self.observed[key]
                result=self.map()
                self.assertFalse(result['field_spans'])
                self.assertEqual(result['withheld_fields'][0]['reason'],'original_image_mismatch')
        self.observed=original

    def test_wrong_field_text_origin_or_outside_region_has_no_span(self):
        e=self.rows[0]['fields'][0]['locator']['evidence']
        original=copy.deepcopy(e)
        for change in [{'field':'other'},{'proposed_reading':'other'},{'region_origin':'BOTTOMLEFT_pixels'},
            {'proposed_image_region':[-1,40,120,100]},{'proposed_image_region':[20,40,1300,100]},
            {'proposed_image_region':[120,40,20,100]},{'proposed_image_region':[True,40,120,100]}]:
            self.rows[0]['fields'][0]['locator']['evidence']={**original,**change}
            result=self.map()
            self.assertFalse(result['field_spans'])
            self.assertEqual(result['withheld_fields'][0]['reason'],'invalid_image_field_evidence')

    def test_missing_image_unconfirmed_fields_and_excluded_audiences_stay_unmapped(self):
        self.pages={}
        self.assertEqual(self.map()['withheld_fields'][0]['reason'],'image_page_unavailable')
        self.setUp()
        self.rows[0]['fields'][0]['decision']='pending'
        self.assertEqual(self.map()['withheld_fields'][0]['reason'],'field_not_confirmed')
        self.setUp()
        self.rows[0]['intended_audience']='law'
        self.assertEqual(self.map()['withheld_fields'][0]['reason'],'undergraduate_review_audience_required')
        self.assertEqual(self.calls,[])

    def test_unknown_applicability_stays_withheld_and_native_diagnostics_stay_separate(self):
        prep=self.prep()
        mapped=self.map(prep)
        result=build_reviewed_policy_chunks(prep,sources=self.sources,review_events=self.events,
            source_versions=[self.version],field_spans=mapped['field_spans'])
        self.assertEqual(result['chunks'],[])
        self.assertEqual(result['withheld'][0]['reasons'],['undergraduate_applicability_required'])

    def test_blank_or_structured_field_has_no_invented_text_region(self):
        self.rows[0]['fields'][0].update(reviewed_value='',source_blank=True)
        self.assertEqual(self.map()['withheld_fields'][0]['reason'],'blank_image_field_requires_mapping')
        self.setUp()
        self.rows[0]['fields'][0]['reviewed_value']=['Yes','No']
        self.assertEqual(self.map()['withheld_fields'][0]['reason'],'structured_image_field_requires_mapping')

    def test_original_render_reader_runtime_error_withholds_the_field(self):
        def broken(*args):
            raise RuntimeError('render failure')
        result=self.map(reader=broken)
        self.assertEqual(result['withheld_fields'][0]['reason'],'image_reader_failure')

    def test_rows_and_directional_edges_bind_as_inactive_structured_graph(self):
        edges=self.graph_setup()
        mapping=self.map()
        before=copy.deepcopy((mapping,edges))
        graph=self.bind(mapping,edges)
        self.assertEqual([n['node_id'] for n in graph['nodes']],['a','b'])
        self.assertEqual([(e['from'],e['label'],e['to']) for e in graph['edges']],
            [('a','Yes','b'),('a','No','END')])
        self.assertEqual(graph['edges'][0]['label_span']['text'],'Yes')
        self.assertEqual(graph['terminal']['label'],'END')
        self.assertFalse(graph['activation_eligible'])
        self.assertEqual((mapping,edges),before)

    def test_changed_direction_label_or_dangling_endpoint_is_not_accepted(self):
        edges=self.graph_setup()
        for change in [{'from':'b'},{'to':'unknown'},{'label':'Maybe'}]:
            bad=copy.deepcopy(edges)
            bad[0].update(change)
            with self.assertRaisesRegex(ValueError,'arrow'):
                self.bind(self.map(),bad)

    def test_incomplete_row_review_or_terminal_geometry_cannot_complete_a_graph(self):
        edges=self.graph_setup()
        self.rows[1]['fields'][0]['decision']='pending'
        with self.assertRaisesRegex(ValueError,'row'):
            self.bind(self.map(),edges)
        self.rows[1]['fields'][0]['decision']='accepted'
        self.rows[2]['fields'][0]['decision']='pending'
        with self.assertRaisesRegex(ValueError,'arrow'):
            self.bind(self.map(),edges)
        self.rows[2]['fields'][0]['decision']='accepted'
        with self.assertRaisesRegex(ValueError,'region'):
            self.bind(self.map(),edges,terminal_region=[0,0,2000,50])

    def test_mapping_and_graph_do_not_mutate_source_events_or_preparation(self):
        edges=self.graph_setup()
        prep=self.prep()
        before=copy.deepcopy((prep,self.sources,self.events,self.pages))
        mapping=self.map(prep)
        graph=self.bind(mapping,edges)
        self.assertEqual((prep,self.sources,self.events,self.pages),before)
        graph['nodes'][0]['fields'][0]['value']='changed'
        self.assertEqual((prep,self.sources,self.events,self.pages),before)


if __name__=='__main__':
    unittest.main()
