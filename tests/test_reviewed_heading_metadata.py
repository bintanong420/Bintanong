"""Synthetic curriculum headings: derived values stay distinct from quotations."""
import copy
import json
import unittest

import test_reviewed_policy_chunks as fixtures
from backend.bintanong_contracts.source import compute_content_hash
from backend.bintanong_contracts.reviewed_policy_context import (
    render_reviewed_policy_context, serialize_reviewed_fields,
)
from backend.bintanong_retrieval.context import build_context


class ReviewedHeadingMetadataTests(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.ReviewedPolicyChunkTests()
        self.f.setUp()
        self.identity = 'step-1'
        self.f.rows[0]['fields'] = [self.f.field('course_code', 'XY 2'),
            self.f.field('course_title', 'Synthetic Computing'),
            self.f.field('placement', 'Second Year / Second Semester'),
            self.f.field('edition_status', 'PROPOSED 2025-2026')]
        self.f.anchors = {self.identity: {
            'course_code': [self.span('code', 'XY 2', [350, 200, 370, 210])],
            'course_title': [self.span('title', 'Synthetic Computing', [380, 200, 460, 215])],
        }}
        self.headings = [self.span('year', 'SECOND YEAR', [270, 140, 330, 150]),
            self.span('term', 'SECOND SEMESTER', [380, 160, 470, 170])]
        self.proposal = [self.span('proposal',
            'PROPOSED BACHELOR OF SCIENCE IN COMPUTING PROGRAM OF STUDY', [100, 50, 530, 65]),
            self.span('implementation',
                'Proposed Date of Implementation: First Semester, SY 2025-2026', [160, 80, 500, 95])]
        self.bindings = {self.identity: {
            'placement': self.binding('placement', 'year_term_heading_metadata', self.headings),
            'edition_status': self.binding('edition_status', 'proposed_edition_heading_metadata', self.proposal),
        }}

    def span(self, name, text, box):
        starts = {'code': 10, 'title': 30, 'year': 100, 'term': 120, 'proposal': 200, 'implementation': 400}
        span = self.f.span(name, text)
        span['bbox'] = box
        span['locator']['item_ids'] = [f'native-pdf:p1:chars{starts[name]}-{starts[name]+len(text)}']
        span['extraction'] = {'source_kind': 'native_pdf', 'resolution_method': 'original_native_range',
            'repair_id': None, 'ocr_confidence': None}
        return span

    def binding(self, name, kind, spans):
        field = next(f for f in self.f.rows[0]['fields'] if f['name'] == name)
        return {'reading_id': self.identity, 'field_name': name, 'source_sha256': self.f.sha,
            'version_id': self.f.version.version_id, 'owner_event_sha256': self.f.ev,
            'confirmed_value': field['reviewed_value'], 'projection_kind': kind,
            'is_literal_scalar_quote': False, 'literal_source_spans': copy.deepcopy(spans),
            'row_anchor_spans': copy.deepcopy([s for name in ('course_code', 'course_title')
                for s in self.f.anchors[self.identity][name]]), 'effectivity_inferred': False}

    def build(self, **options):
        return self.f.build(include_source_limits=True, compact_context=True,
            heading_metadata_bindings=self.bindings, **options)

    def chunk(self):
        result = self.build()
        self.assertEqual(result['withheld'], [])
        self.assertEqual(len(result['chunks']), 1)
        return result['chunks'][0]

    def assert_rejected(self, name='placement'):
        result = self.build()
        self.assertEqual(result['chunks'], [])
        self.assertIn('invalid_heading_metadata:'+name, result['withheld'][0]['reasons'])

    def rewrite(self, chunk):
        fields = chunk['type_fields']
        chunk['text'] = serialize_reviewed_fields(fields['field_associations'], fields['source_limits'],
            context_format=fields['context_format'])
        chunk['content_hash'] = compute_content_hash(chunk['source_text'], chunk['text'])

    def test_derived_metadata_keeps_literal_headings_and_proposal_warning(self):
        before = copy.deepcopy((self.f.rows, self.f.anchors, self.bindings))
        chunk = self.chunk()
        display = json.loads(chunk['text'])['fields']
        self.assertEqual(display[2]['value'], 'Second Year / Second Semester')
        self.assertEqual(display[2]['source_headings'], ['SECOND YEAR', 'SECOND SEMESTER'])
        self.assertEqual(display[2]['value_origin'], 'derived_from_printed_headings')
        self.assertEqual(display[3]['value'], 'PROPOSED 2025-2026')
        self.assertIn('effectivity is not established', display[3]['limitation'])
        self.assertIn(self.proposal[1]['text'], chunk['source_text'])
        self.assertNotIn('Second Year / Second Semester', chunk['source_text'])
        self.assertEqual(render_reviewed_policy_context(chunk, chunk['spans']), chunk['text'])
        self.assertFalse(self.build()['activation_eligible'])
        self.assertEqual((self.f.rows, self.f.anchors, self.bindings), before)
        self.assertEqual(self.chunk(), chunk)

    def test_default_literal_adapter_output_is_unchanged(self):
        before = self.f.build(include_source_limits=True, compact_context=True)
        after = self.f.build(include_source_limits=True, compact_context=True, heading_metadata_bindings=None)
        self.assertEqual(before, after)
        self.assertIn('missing_field_spans:placement', after['withheld'][0]['reasons'])
        with self.assertRaises(ValueError):
            self.f.build(heading_metadata_bindings=self.bindings)

    def test_unknown_applicability_remains_withheld_after_complete_mapping(self):
        self.f.rows[0].update(applicability='unknown', applicability_evidence_ref=None)
        result = self.build()
        self.assertEqual(result['chunks'], [])
        self.assertEqual(result['withheld'][0]['reasons'], ['undergraduate_applicability_required'])

    def test_shared_summer_heading_retains_year_and_wrap_image_anchor(self):
        field = self.f.rows[0]['fields'][2]
        field.update(original_value='Second Year / Summer', reviewed_value='Second Year / Summer')
        summer = self.span('term', 'SUMMER', [270, 160, 330, 170])
        self.bindings[self.identity]['placement'] = self.binding('placement', 'year_term_heading_metadata',
            [self.headings[0], summer])
        self.f.anchors[self.identity]['course_code'][0]['extraction']['source_kind'] = 'original_pdf_image'
        self.bindings[self.identity]['placement']['row_anchor_spans'] = copy.deepcopy(
            [s for n in ('course_code', 'course_title') for s in self.f.anchors[self.identity][n]])
        self.bindings[self.identity]['edition_status']['row_anchor_spans'] = copy.deepcopy(
            self.bindings[self.identity]['placement']['row_anchor_spans'])
        self.assertEqual(json.loads(self.chunk()['text'])['fields'][2]['value'], 'Second Year / Summer')

    def test_bottomleft_geometry_and_reordered_fields_roundtrip(self):
        for fields in self.f.anchors.values():
            for spans in fields.values():
                for span in spans:
                    l,t,r,b = span['bbox'];span.update(bbox=[l,800-t,r,800-b], bbox_origin='BOTTOMLEFT')
        for binding in self.bindings[self.identity].values():
            for span in binding['literal_source_spans']:
                l,t,r,b = span['bbox'];span.update(bbox=[l,800-t,r,800-b], bbox_origin='BOTTOMLEFT')
            binding['row_anchor_spans'] = copy.deepcopy(
                [s for n in ('course_code', 'course_title') for s in self.f.anchors[self.identity][n]])
        self.f.rows[0]['fields'] = self.f.rows[0]['fields'][2:] + self.f.rows[0]['fields'][:2]
        chunk = self.chunk()
        self.assertEqual(render_reviewed_policy_context(chunk, chunk['spans']), chunk['text'])

    def test_binding_rejects_wrong_identity_event_value_and_projection(self):
        original = copy.deepcopy(self.bindings)
        for key,value in [('reading_id','other'),('field_name','other'),('source_sha256','0'*64),
            ('version_id','other'),('owner_event_sha256','0'*64),('confirmed_value','First Year / Second Semester'),
            ('projection_kind','arbitrary_normalization'),('is_literal_scalar_quote',True),('effectivity_inferred',True)]:
            with self.subTest(key=key):
                self.bindings = copy.deepcopy(original)
                self.bindings[self.identity]['placement'][key] = value
                self.assert_rejected()

    def test_binding_rejects_partial_or_changed_course_row_anchors(self):
        original = copy.deepcopy(self.bindings)
        for change in ('missing','text','geometry','page'):
            with self.subTest(change=change):
                self.bindings = copy.deepcopy(original)
                anchors = self.bindings[self.identity]['placement']['row_anchor_spans']
                if change == 'missing': anchors.pop()
                elif change == 'text': anchors[0]['text'] = 'XY 99'
                elif change == 'geometry': anchors[0]['bbox'] = [10,200,30,210]
                else: anchors[0]['page'] = 2
                self.assert_rejected()

    def test_heading_rejects_wrong_column_order_page_geometry_and_nonliteral_provenance(self):
        original = copy.deepcopy(self.bindings)
        for change in ('column','below','year_order','page','origin','text','kind','range','size'):
            with self.subTest(change=change):
                self.bindings = copy.deepcopy(original)
                spans = self.bindings[self.identity]['placement']['literal_source_spans']
                if change == 'column': spans[1]['bbox'] = [100,160,180,170]
                elif change == 'below': spans[1]['bbox'] = [380,240,470,250]
                elif change == 'year_order': spans[0]['bbox'] = [270,180,330,190]
                elif change == 'page': spans[1]['page'] = 2
                elif change == 'origin': spans[1]['bbox_origin'] = 'BOTTOMLEFT'
                elif change == 'text': spans[1]['text'] = 'FIRST SEMESTER'
                elif change == 'kind': spans[1]['extraction']['source_kind'] = 'original_pdf_image'
                elif change == 'range': spans[1]['locator']['item_ids'] = ['invented-heading']
                else: spans[1]['page_size'] = [900,800]
                self.assert_rejected()

    def test_proposed_edition_rejects_effective_wording_and_invalid_year(self):
        original = copy.deepcopy(self.bindings)
        for change in ('effective','year','marker'):
            with self.subTest(change=change):
                self.bindings = copy.deepcopy(original)
                spans = self.bindings[self.identity]['edition_status']['literal_source_spans']
                if change == 'effective': spans[1]['text'] = 'Effective SY 2025-2026'
                elif change == 'year': spans[1]['text'] = spans[1]['text'].replace('2026','2028')
                else: spans[0]['text'] = spans[0]['text'].replace('PROPOSED','APPROVED')
                self.assert_rejected('edition_status')

    def test_unknown_binding_field_or_row_is_rejected(self):
        for bindings in ({'other': {}}, {self.identity: {'other': {}}}, []):
            with self.subTest(bindings=bindings), self.assertRaises(ValueError):
                self.f.build(include_source_limits=True, heading_metadata_bindings=bindings)

    def test_direct_scalar_mapping_cannot_override_metadata_binding(self):
        self.f.anchors[self.identity]['placement'] = copy.deepcopy(self.headings)
        self.assert_rejected()

    def test_stored_context_and_retrieval_reject_regenerated_metadata_tampering(self):
        original = self.chunk()
        candidate = {'chunk': original, 'spans': original['spans'],
            'version': self.f.version.model_dump(mode='json'), 'similarity': 0.9, 'neighbors': []}
        self.assertTrue(build_context([candidate],100000,len)['evidence'])
        for change in ('value','headings','projection','anchor','event','blank','partial'):
            with self.subTest(change=change):
                chunk = copy.deepcopy(original)
                meta = chunk['type_fields']['field_associations'][2]
                if change == 'value': meta['value'] = 'First Year / Second Semester'
                elif change == 'headings': meta['source_headings'][0] = 'FIRST YEAR'
                elif change == 'projection': meta['projection_kind'] = 'arbitrary_normalization'
                elif change == 'anchor': meta['row_anchor_indexes'] = [0]
                elif change == 'event': meta['event_sha256'] = '0'*64
                elif change == 'blank': meta['source_blank'] = True
                else: meta['span_indexes'].pop()
                self.rewrite(chunk)
                with self.assertRaises(ValueError):
                    render_reviewed_policy_context(chunk, chunk['spans'])
                self.assertFalse(build_context([{**candidate,'chunk':chunk,'spans':chunk['spans']}],100000,len)['evidence'])

    def test_stored_span_rows_without_inline_spans_validate_heading_metadata(self):
        chunk = json.loads(json.dumps(self.chunk()))
        spans = chunk.pop('spans')
        for i,span in enumerate(spans): span.update(chunk_id=chunk['chunk_id'],span_order=i)
        self.assertEqual(render_reviewed_policy_context(chunk,spans),chunk['text'])

    def test_stored_metadata_rejects_unrecognized_field_with_null_projection_kind(self):
        chunk = self.chunk()
        field = chunk['type_fields']['field_associations'][3]
        field.update(name='other_metadata', projection_kind=None)
        self.rewrite(chunk)
        with self.assertRaises(ValueError):
            render_reviewed_policy_context(chunk,chunk['spans'])


if __name__ == '__main__':
    unittest.main()
