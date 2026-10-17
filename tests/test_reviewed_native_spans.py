"""Synthetic native PDF fields and original-range callbacks, no source approvals."""
import copy
import hashlib
import json
import unittest

from backend.bintanong_contracts.source import SourceSpan
from backend.bintanong_tools.document_ingest.register import mint_pending_register
from backend.bintanong_tools.document_ingest.reviewed_policy import build_reviewed_policy_bundle
from backend.bintanong_tools.document_ingest.reviewed_policy_chunks import build_reviewed_policy_chunks


class NativeFieldSpanTests(unittest.TestCase):
    def setUp(self):
        self.source = b"synthetic original PDF bytes"
        self.sha = hashlib.sha256(self.source).hexdigest()
        self.sources = {self.sha:self.source}
        self.version = mint_pending_register([{"filename":"native-synthetic.pdf","sha256":self.sha,
            "acquisition_locator":"shelf:synthetic-native"}],synthetic=True)[0]
        self.event = json.dumps({"source_sha256":self.sha,"owner_statement":"The displayed fields match."}).encode()
        self.ev = hashlib.sha256(self.event).hexdigest()
        self.events = {self.ev:self.event}
        self.field = {"name":"grade","original_value":"SYN","reviewed_value":"SYN",
            "source_blank":False,"decision":"accepted","review_event_sha256":self.ev,
            "locator":{"physical_pages":[2],"field":"grade","evidence":{
                "field":"grade","proposed_text":"SYN","native_text":"SYN",
                "native_character_span":[10,13],"pdf_bbox":[20,40,55,50],
                "coordinate_order":"left,bottom,right,top","origin":"BOTTOMLEFT"}}}
        self.row = {"reading_id":"synthetic-grade-row","source_sha256":self.sha,
            "version_id":self.version.version_id,"intended_audience":"undergraduate",
            "applicability":"unknown","applicability_evidence_ref":None,
            "fields":[self.field],"gaps":[],"preserved_evidence":[{"artifact":"native-evidence.json","sha256":"a"*64}],
            "original_row_evidence":{"page_size":[600,800]},"raw_cells_for_comparison":[{"text":"raw wrong column","column_start":2}]}
        self.observed = {"text":"SYN","bbox":[20,40,55,50],"page_size":[600,800],
            "coordinate_order":"left,bottom,right,top","origin":"BOTTOMLEFT"}
        self.calls = []

    def prep(self):
        return build_reviewed_policy_bundle([self.row],sources=self.sources,review_events=self.events)

    def reader(self, source, page, start, end):
        self.calls.append((source,page,start,end))
        return copy.deepcopy(self.observed)

    def build(self,bundle=None,reader=None):
        from backend.bintanong_tools.document_ingest.reviewed_native_spans import map_reviewed_native_spans
        return map_reviewed_native_spans(self.prep() if bundle is None else bundle,sources=self.sources,
            review_events=self.events,source_versions=[self.version],read_native_range=reader or self.reader)

    def reasons(self,result):
        return [r['reason'] for r in result['withheld_fields']]

    def test_verified_range_yields_honest_native_text_locator_and_coordinate_order(self):
        result=self.build()
        span=result['field_spans'][self.row['reading_id']]['grade'][0]
        self.assertEqual(self.calls,[(self.source,2,10,13)])
        parsed=SourceSpan.parse(span)
        self.assertEqual(parsed.bbox,(20,50,55,40))
        self.assertEqual(parsed.locator.kind,'text_item')
        self.assertEqual(parsed.locator.item_ids,('native-pdf:p2:chars10-13',))
        self.assertEqual(parsed.extraction.source_kind,'native_pdf')
        self.assertEqual(span['text'],'SYN')
        self.assertTrue(result['candidate_only'])
        self.assertFalse(result['activation_eligible'])

    def test_top_left_coordinates_use_declared_order_without_guessing(self):
        e=self.field['locator']['evidence']
        e.update(pdf_bbox=[20,40,55,50],coordinate_order='left,top,right,bottom',origin='TOPLEFT')
        self.observed.update(bbox=[20,40,55,50],coordinate_order='left,top,right,bottom',origin='TOPLEFT')
        self.assertEqual(self.build()['field_spans'][self.row['reading_id']]['grade'][0]['bbox'],[20,40,55,50])

    def test_blank_is_explicit_empty_mapping_with_no_reader_or_glyphs(self):
        self.field.update(original_value='',reviewed_value='',source_blank=True)
        self.field['locator']['evidence']={'field':'grade','proposed_text':'',
            'native_character_span':None,'pdf_bbox':None,'basis':'blank original field'}
        result=self.build()
        self.assertEqual(result['field_spans'][self.row['reading_id']]['grade'],[])
        self.assertEqual(result['coverage']['mapped_blank_fields'],1)
        self.assertEqual(self.calls,[])
        self.assertIsNone(result['mapping_evidence'][0]['span'])

    def test_unknown_applicability_stays_withheld_after_technical_mapping(self):
        prep=self.prep()
        result=self.build(prep)
        chunks=build_reviewed_policy_chunks(prep,sources=self.sources,review_events=self.events,
            source_versions=[self.version],field_spans=result['field_spans'])
        self.assertEqual(chunks['chunks'],[])
        self.assertEqual(chunks['withheld'][0]['reasons'],['undergraduate_applicability_required'])

    def test_synthetic_explicit_applicability_can_produce_only_pending_chunk(self):
        self.row.update(applicability='undergraduate',applicability_evidence_ref='synthetic-scope#row')
        prep=self.prep()
        spans=self.build(prep)['field_spans']
        result=build_reviewed_policy_chunks(prep,sources=self.sources,review_events=self.events,
            source_versions=[self.version],field_spans=spans)
        self.assertEqual(len(result['chunks']),1)
        self.assertEqual(result['chunks'][0]['content_review'],'pending')
        self.assertFalse(result['activation_eligible'])

    def test_original_source_event_bundle_and_raw_associations_remain_unchanged(self):
        prep=self.prep()
        original=copy.deepcopy((prep,self.sources,self.events))
        result=self.build(prep)
        self.assertEqual((prep,self.sources,self.events),original)
        self.assertEqual(result['preparation'],prep)
        result['preparation']['readings'][0]['raw_cells_for_comparison'][0]['text']='changed'
        self.assertEqual((prep,self.sources,self.events),original)

    def test_changed_source_bytes_event_or_cached_selection_is_rejected(self):
        prep=self.prep()
        self.sources[self.sha]=b'changed'
        with self.assertRaisesRegex(ValueError,'digest'):
            self.build(prep)
        self.sources[self.sha]=self.source
        bad=copy.deepcopy(prep)
        bad['selection']['undergraduate']=[self.row['reading_id']]
        with self.assertRaisesRegex(ValueError,'preparation'):
            self.build(bad)
        self.events[self.ev]=b'changed'
        with self.assertRaisesRegex(ValueError,'digest'):
            self.build(prep)

    def test_native_reader_must_match_recorded_text_box_and_page_size(self):
        for change in [{'text':'other'},{'bbox':[21,40,55,50]},{'page_size':[601,800]},
            {'origin':'TOPLEFT'},{'coordinate_order':'pixels'}]:
            with self.subTest(change=change):
                original=copy.deepcopy(self.observed)
                self.observed.update(change)
                result=self.build()
                self.assertEqual(result['field_spans'],{})
                self.assertIn('native_observation_mismatch',self.reasons(result))
                self.observed=original

    def test_invalid_range_field_text_or_pixel_geometry_is_withheld(self):
        variants=[{'native_character_span':[True,13]},{'native_character_span':[-1,13]},
            {'native_character_span':[13,13]},{'native_character_span':[10,13.0]},
            {'native_text':'different'},{'field':'other'},{'pdf_bbox':[-1,40,55,50]},
            {'pdf_bbox':[20,40,float('inf'),50]},{'coordinate_order':'left,top,right,bottom_pixels'},
            {'origin':'TOPLEFT_pixels'}]
        saved=copy.deepcopy(self.field['locator']['evidence'])
        for change in variants:
            with self.subTest(change=change):
                self.field['locator']['evidence']={**saved,**change}
                if 'pdf_bbox' in change and any(isinstance(x,float) and x==float('inf') for x in change['pdf_bbox']):
                    with self.assertRaisesRegex(ValueError,'finite'):
                        self.build()
                else:
                    result=self.build()
                    self.assertEqual(result['field_spans'],{})
                    self.assertIn('invalid_native_evidence',self.reasons(result))
        self.field['locator']['evidence']=saved

    def test_image_fields_missing_page_size_and_multiple_pages_stay_unmapped(self):
        self.field['locator']['evidence']={'field':'grade','proposed_image_region':[1,2,3,4]}
        self.assertIn('native_evidence_unavailable',self.reasons(self.build()))
        self.setUp()
        self.row['original_row_evidence']={}
        self.assertIn('native_page_size_unavailable',self.reasons(self.build()))
        self.setUp()
        self.field['locator']['physical_pages']=[2,3]
        self.assertIn('native_page_split_requires_mapping',self.reasons(self.build()))

    def test_unconfirmed_field_does_not_get_anchors_from_a_whole_table_review(self):
        for decision in ['pending','unresolved']:
            self.field['decision']=decision
            self.assertIn('field_not_confirmed',self.reasons(self.build()))
        self.assertEqual(self.calls,[])

    def test_duplicate_ranges_are_withheld_for_both_fields(self):
        second=copy.deepcopy(self.field)
        second['name']='description'
        second['locator']['field']='description'
        second['locator']['evidence']['field']='description'
        self.row['fields'].append(second)
        result=self.build()
        self.assertEqual(result['field_spans'],{})
        self.assertEqual(self.reasons(result),['duplicate_native_range','duplicate_native_range'])

    def test_reader_failure_never_creates_an_anchor(self):
        def broken(*args):
            raise OSError('unreadable original')
        result=self.build(reader=broken)
        self.assertEqual(result['field_spans'],{})
        self.assertIn('native_reader_failure',self.reasons(result))

    def test_native_reader_runtime_error_is_a_field_failure(self):
        def broken(*args):
            # PDFium's library exception derives from RuntimeError; no PDF dependency in this fixture.
            raise RuntimeError('native PDF data format failure')
        result=self.build(reader=broken)
        self.assertEqual(result['field_spans'],{})
        self.assertEqual(self.reasons(result),['native_reader_failure'])

    def test_version_mismatch_is_rejected_before_original_read(self):
        self.row['version_id']='ver-other'
        with self.assertRaisesRegex(ValueError,'version'):
            self.build()
        self.assertEqual(self.calls,[])

    def test_excluded_or_unknown_audience_does_not_enter_undergraduate_anchor_mapping(self):
        for audience in ['law','medicine','graduate','laboratory_school','faculty','staff','mixed','unknown']:
            with self.subTest(audience=audience):
                self.row['intended_audience']=audience
                result=self.build()
                self.assertEqual(result['field_spans'],{})
                self.assertIn('undergraduate_review_audience_required',self.reasons(result))
        self.row.update(intended_audience='undergraduate',applicability='excluded',
            applicability_evidence_ref='synthetic-exclusion#row')
        self.assertIn('undergraduate_review_audience_required',self.reasons(self.build()))
        self.assertEqual(self.calls,[])


if __name__=='__main__':
    unittest.main()
