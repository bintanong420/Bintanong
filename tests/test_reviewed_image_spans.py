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

    def map(self,bundle=None,reader=None):
        from backend.bintanong_tools.document_ingest.reviewed_image_spans import map_reviewed_image_spans
        return map_reviewed_image_spans(self.prep() if bundle is None else bundle,sources=self.sources,
            review_events=self.events,source_versions=[self.version],image_pages=self.pages,
            read_page_image=reader or self.reader)

    def graph_setup(self):
        second=self.row('node-b')
        second['fields'][0]['locator']['evidence']['proposed_image_region']=[20,200,120,260]
        arrows=self.row('arrows')
        value=[{'from':'a','label':'Yes','to':'b'},{'from':'a','label':'No','to':'END'}]
        arrows['fields']=[self.field('arrows',value)]
        self.rows += [second,arrows]
        return [{'from':'a','label':'Yes','to':'b','pixel_region':[60,100,100,200]},
            {'from':'a','label':'No','to':'END','pixel_region':[120,80,180,350]}]

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
