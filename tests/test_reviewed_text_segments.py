"""Synthetic reviewed raw partitions; furniture never becomes body source text."""
import copy,hashlib,json,unittest

from backend.bintanong_tools.document_ingest.register import mint_pending_register
from backend.bintanong_tools.document_ingest.reviewed_policy import build_reviewed_policy_bundle
from backend.bintanong_tools.document_ingest.reviewed_policy_chunks import build_reviewed_policy_chunks


class ReviewedTextSegmentTests(unittest.TestCase):
    def setUp(self):
        self.data=b'synthetic original segmented PDF';self.sha=hashlib.sha256(self.data).hexdigest()
        self.body='Synthetic Programme';self.furniture='UNIVERSITY HEADER'
        self.raw=self.body+' '+self.furniture
        self.version=mint_pending_register([{'filename':'synthetic.pdf','sha256':self.sha,
            'acquisition_locator':'shelf:synthetic-segment'}],synthetic=True)[0]
        event=json.dumps({'source_sha256':self.sha,'owner_statement':'Synthetic body and furniture separations match.'}).encode()
        self.ev=hashlib.sha256(event).hexdigest();self.events={self.ev:event}
        self.prov=[{'page_no':1,'bbox':{'l':10,'b':40,'r':180,'t':55,'coord_origin':'BOTTOMLEFT'},
            'charspan':[0,len(self.body)]},
            {'page_no':2,'bbox':{'l':20,'b':750,'r':200,'t':765,'coord_origin':'BOTTOMLEFT'},
            'charspan':[len(self.body)+1,len(self.raw)]}]
        raw={'self_ref':'#/texts/12','text':self.raw,'orig':self.raw,'content_layer':'body','prov':copy.deepcopy(self.prov)}
        self.row={'reading_id':'programme-body','source_sha256':self.sha,'version_id':self.version.version_id,
            'intended_audience':'undergraduate','applicability':'unknown','applicability_evidence_ref':None,
            'fields':[self.field('body',self.raw,self.body,raw),
                self.field('segmentation',copy.deepcopy(self.prov),[
                    {'kind':'programme_name','text':self.body,'raw_provenance':copy.deepcopy(self.prov[0])},
                    {'kind':'page_furniture','text':self.furniture,'raw_provenance':copy.deepcopy(self.prov[1])}],copy.deepcopy(self.prov))],
            'gaps':[],'preserved_evidence':[{'artifact':'synthetic-raw.json','sha256':'a'*64}]}
        self.images={1:b'synthetic body render',2:b'synthetic furniture render'}
        self.pages={(self.sha,p):{'image_sha256':hashlib.sha256(data).hexdigest(),
            'image_size':[1200,1600],'page_size':[600,800],'scale':2,'rotation':0,'crop':None}
            for p,data in self.images.items()}
        self.calls=[]

    def field(self,name,original,value,evidence):
        return {'name':name,'original_value':original,'reviewed_value':value,'source_blank':False,
            'decision':'corrected','review_event_sha256':self.ev,
            'locator':{'physical_pages':[1,2],'field':name,'evidence':evidence}}

    def partition(self):
        from backend.bintanong_tools.document_ingest.reviewed_text_segments import reviewed_body_partition
        return reviewed_body_partition(self.row)

    def prep(self):
        return build_reviewed_policy_bundle([self.row],sources={self.sha:self.data},review_events=self.events)

    def reader(self,data,page):
        self.assertEqual(data,self.data);self.calls.append(page)
        return {**self.pages[(self.sha,page)],'image_bytes':self.images[page]}

    def map(self,**options):
        from backend.bintanong_tools.document_ingest.reviewed_text_segments import map_reviewed_body_segments
        return map_reviewed_body_segments(self.prep(),sources=options.get('sources',{self.sha:self.data}),
            review_events=self.events,source_versions=[self.version],image_pages=self.pages,
            read_page_image=options.get('reader',self.reader))

    def test_partition_preserves_full_original_and_derives_only_body_page(self):
        before=copy.deepcopy(self.row)
        result=self.partition()
        self.assertEqual(result['body_pages'],[1])
        self.assertEqual(result['body_text'],self.body)
        self.assertEqual(result['segments'],self.row['fields'][1]['reviewed_value'])
        self.assertEqual(result['raw_text'],self.raw)
        self.assertEqual(self.row,before)

    def test_original_image_mapper_excludes_furniture_and_keeps_corrected_provenance(self):
        result=self.map();span=result['field_spans']['programme-body']['body'][0]
        self.assertEqual(span['text'],self.body);self.assertEqual(span['page'],1)
        self.assertEqual(span['bbox'],[10,745,180,760])
        self.assertEqual(span['extraction']['source_kind'],'original_pdf_image')
        self.assertEqual(span['locator']['cell_ids'],[])
        evidence=result['mapping_evidence'][0]
        self.assertEqual(evidence['original_body_locator']['physical_pages'],[1,2])
        self.assertEqual(evidence['partition']['segments'][1]['text'],self.furniture)
        self.assertEqual(set(self.calls),{1,2})

    def test_partial_or_different_review_events_reject_partition(self):
        for edit in ('body','segmentation','event','blank','audience'):
            with self.subTest(edit=edit):
                self.setUp()
                if edit=='body':self.row['fields'][0]['decision']='pending'
                if edit=='segmentation':self.row['fields'][1]['decision']='unresolved'
                if edit=='event':self.row['fields'][1]['review_event_sha256']='b'*64
                if edit=='blank':self.row['fields'][0]['source_blank']=True
                if edit=='audience':self.row['intended_audience']='staff'
                with self.assertRaises(ValueError):self.partition()

    def test_raw_provenance_text_order_ranges_and_roles_must_match(self):
        for edit in ('missing','order','text','role','provenance','raw_text','original_segmentation','pages','range'):
            with self.subTest(edit=edit):
                self.setUp();body,seg=self.row['fields'];segments=seg['reviewed_value']
                if edit=='missing':segments.pop()
                if edit=='order':segments.reverse()
                if edit=='text':segments[0]['text']='Other programme'
                if edit=='role':segments[0]['kind']='unknown'
                if edit=='provenance':segments[0]['raw_provenance']['bbox']['l']=11
                if edit=='raw_text':body['locator']['evidence']['text']='Changed raw'
                if edit=='original_segmentation':seg['original_value'].pop()
                if edit=='pages':body['locator']['physical_pages']=[1]
                if edit=='range':segments[0]['raw_provenance']['charspan']=[0,999]
                with self.assertRaises(ValueError):self.partition()

    def test_malformed_role_or_body_value_is_rejected_as_a_partition_error(self):
        for value in ([],{},None):
            with self.subTest(role=value):
                self.setUp();self.row['fields'][1]['reviewed_value'][0]['kind']=value
                with self.assertRaises(ValueError):self.partition()
            with self.subTest(body=value):
                self.setUp();self.row['fields'][0]['reviewed_value']=value
                with self.assertRaises(ValueError):self.partition()

    def test_invalid_furniture_geometry_is_not_hidden_by_a_valid_body(self):
        for provenance in (self.row['fields'][0]['locator']['evidence']['prov'][1],
            self.row['fields'][1]['original_value'][1],self.row['fields'][1]['locator']['evidence'][1],
            self.row['fields'][1]['reviewed_value'][1]['raw_provenance']):
            provenance['bbox']['r']=700
        self.assertFalse(self.map()['field_spans'])

    def test_geometry_or_original_render_mismatch_withholds_body(self):
        for edit in ('origin','bounds','image','dimensions'):
            with self.subTest(edit=edit):
                self.setUp()
                if edit in ('origin','bounds'):
                    for provenance in (self.row['fields'][0]['locator']['evidence']['prov'][0],
                        self.row['fields'][1]['original_value'][0],self.row['fields'][1]['locator']['evidence'][0],
                        self.row['fields'][1]['reviewed_value'][0]['raw_provenance']):
                        if edit=='origin':provenance['bbox']['coord_origin']='pixels'
                        else:provenance['bbox']['r']=700
                def reader(data,page):
                    observed=self.reader(data,page)
                    if edit=='image':observed['image_bytes']=b'different original'
                    if edit=='dimensions':observed['page_size']=[601,800]
                    return observed
                self.assertFalse(self.map(reader=reader)['field_spans'])

    def test_pending_adapter_accepts_body_page_without_requiring_furniture_text(self):
        self.row.update(applicability='undergraduate',applicability_evidence_ref='synthetic-reviewed-scope')
        prep=self.prep();mapping=self.map()
        result=build_reviewed_policy_chunks(prep,sources={self.sha:self.data},review_events=self.events,
            source_versions=[self.version],field_spans=mapping['field_spans'])
        reasons=result['withheld'][0]['reasons']
        self.assertNotIn('invalid_field_spans:body',reasons)
        self.assertIn('field_requires_scalar_mapping:segmentation',reasons)
        self.assertEqual(result['chunks'],[])

    def test_pending_adapter_independently_rejects_wrong_body_page_and_unreviewed_partition(self):
        mapping=self.map()
        for edit in ('page','review'):
            with self.subTest(edit=edit):
                anchors=copy.deepcopy(mapping['field_spans'])
                if edit=='page':anchors['programme-body']['body'][0]['page']=2
                if edit=='review':self.row['fields'][1]['decision']='pending'
                result=build_reviewed_policy_chunks(self.prep(),sources={self.sha:self.data},review_events=self.events,
                    source_versions=[self.version],field_spans=anchors)
                self.assertIn('invalid_field_spans:body',result['withheld'][0]['reasons'])
                self.assertEqual(result['chunks'],[])

    def test_source_gaps_and_unknown_applicability_persist_without_input_mutation(self):
        self.row['gaps']=[{'gap_id':'historical-scope','field_names':['body'],'issue':'unknown_applicability',
            'visible_text':self.body,'affected_claims':['current offering'],
            'locator':{'physical_pages':[1],'field':'body'}}]
        prep=self.prep();before=copy.deepcopy((prep,self.row,self.pages,self.events))
        result=self.map();self.assertFalse(result['activation_eligible'])
        self.assertEqual(result['preparation'],prep)
        pending=build_reviewed_policy_chunks(prep,sources={self.sha:self.data},review_events=self.events,
            source_versions=[self.version],field_spans=result['field_spans'])
        self.assertIn('undergraduate_applicability_required',pending['withheld'][0]['reasons'])
        self.assertIn('source_gap_requires_context_support',pending['withheld'][0]['reasons'])
        self.assertEqual((prep,self.row,self.pages,self.events),before)
        result['mapping_evidence'][0]['partition']['segments'][0]['text']='Changed'
        self.assertEqual((prep,self.row,self.pages,self.events),before)
        with self.assertRaisesRegex(ValueError,'digest'):self.map(sources={self.sha:b'changed'})


if __name__=='__main__':unittest.main()
