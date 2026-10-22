"""Synthetic controls for the optional offline selection report."""
import copy
import unittest

from backend.bintanong_retrieval.context import build_context
from backend.bintanong_retrieval.context_selection import build_context_selection_report


def row(identity, text='Synthetic undergraduate clause', page=1):
    return dict(chunk=dict(chunk_id=identity, document_id='doc', version_id='v',
        edition_id='edition', byte_sha256='0'*64, source_text=text, text=text,
        section_path=['Policy'], scope=[], type_fields={}),
        version=dict(version_id='v', byte_sha256='0'*64, filename='synthetic.pdf'),
        similarity=0.9, spans=[dict(span_id=identity, text=text, version_id='v',
            byte_sha256='0'*64, page=page,
            locator=dict(kind='section', section_path=['Policy']))], neighbors=[])


def requires(primary, *neighbors):
    primary['chunk']['type_fields']['required_neighbor_chunk_ids'] = [
        n['chunk']['chunk_id'] for n in neighbors]
    primary['neighbors'] = list(neighbors)
    return primary


class ContextSelectionTests(unittest.TestCase):
    def report(self, candidates, budget=100000, **kwargs):
        result = build_context_selection_report(candidates, budget, len, **kwargs)
        self.assertEqual(result['schema_version'], 'context-selection-report-v1')
        self.assertIs(result['candidate_only'], True)
        self.assertIs(result['activation_eligible'], False)
        self.assertEqual(result['claim_coverage'], 'unknown')
        return result

    def test_default_preserves_builder_in_all_display_modes_without_mutation(self):
        candidates = [requires(row('a'), row('b', page=2)), row('c', page=3)]
        before = copy.deepcopy(candidates)
        for options in ({}, dict(compact_citations=True), dict(shared_citations=True),
                        dict(shared_citations=True, shared_group_metadata=True)):
            with self.subTest(options=options):
                result = self.report(candidates, **options)
                self.assertEqual(result['assembly'], build_context(candidates, 100000, len, **options))
                self.assertEqual(result['requested_primary_ids'], ['a', 'c'])
                self.assertEqual(result['deferred_primary_ids'], [])
        self.assertEqual(candidates, before)

    def test_deferred_candidate_is_distinct_from_budget_refused_group(self):
        a, b = row('a'), row('b', 'X'*5000, page=2)
        budget = len(build_context([a], 100000, len)['context'])
        full = self.report([a, b], budget)
        prefix = self.report([a, b], budget, primary_limit=1)
        self.assertEqual(full['assembly']['gaps'], ['context_budget:b'])
        self.assertEqual(full['offered'][1]['assembly_gaps'], ['context_budget:b'])
        self.assertEqual(prefix['assembly']['gaps'], [])
        self.assertEqual(prefix['deferred_primary_ids'], ['b'])
        self.assertFalse(prefix['offered'][1]['requested'])
        self.assertFalse(prefix['offered'][1]['primary_emitted'])
        self.assertEqual(prefix['offered'][1]['assembly_gaps'], [])
        self.assertEqual(prefix['offered'][1]['similarity'], 0.9)
        self.assertEqual(prefix['offered'][1]['version_id'], 'v')
        self.assertEqual(prefix['offered'][1]['byte_sha256'], '0'*64)

    def test_atomic_group_refusal_does_not_emit_only_cheap_primary(self):
        a = requires(row('a'), row('b', 'X'*5000, page=2))
        result = self.report([a], 1000)
        trace = result['offered'][0]
        self.assertEqual(result['assembly']['evidence'], [])
        self.assertEqual(result['assembly']['gaps'], ['context_budget:a'])
        self.assertEqual(trace['required_chunk_ids'], ['b'])
        self.assertEqual(trace['absent_required_chunk_ids'], [])
        self.assertEqual(trace['unemitted_required_chunk_ids'], ['b'])
        self.assertTrue(trace['dependency_trace_complete'])

    def test_transitive_cycle_and_deferred_primary_emitted_as_neighbor(self):
        a, b, c = row('a'), row('b', page=2), row('c', page=3)
        requires(a, b)
        requires(b, c)
        requires(c, a)
        b['neighbors'] = []
        c['neighbors'] = []
        a['neighbors'] = [b, c]
        before = copy.deepcopy(a)
        result = self.report([a, b], primary_limit=1)
        self.assertEqual(result['offered'][0]['required_chunk_ids'], ['b', 'c'])
        self.assertEqual(result['offered'][0]['unemitted_required_chunk_ids'], [])
        self.assertTrue(result['offered'][1]['primary_emitted'])
        self.assertFalse(result['offered'][1]['requested'])
        self.assertEqual(result['deferred_primary_ids'], ['b'])
        self.assertEqual(a, before)

    def test_missing_neighbor_is_not_borrowed_from_another_primary(self):
        a, b = row('a'), row('b', page=2)
        a['chunk']['type_fields']['required_neighbor_chunk_ids'] = ['b']
        result = self.report([a, b], primary_limit=1)
        trace = result['offered'][0]
        self.assertEqual(trace['absent_required_chunk_ids'], ['b'])
        self.assertEqual(result['assembly']['gaps'], ['missing_required_neighbor:a'])
        self.assertTrue(trace['dependency_trace_complete'])

    def test_transitive_absent_and_malformed_dependencies_are_separate(self):
        for dependency in ('b', None, [1]):
            with self.subTest(dependency=dependency):
                a, b = row('a'), row('b', page=2)
                b['chunk']['type_fields']['required_neighbor_chunk_ids'] = dependency
                requires(a, b)
                result = self.report([a])
                self.assertFalse(result['offered'][0]['dependency_trace_complete'])
                self.assertEqual(result['offered'][0]['malformed_dependency_chunk_ids'], ['b'])
                self.assertEqual(result['assembly']['gaps'], ['missing_required_neighbor:a'])
        a, b = row('a'), row('b', page=2)
        b['chunk']['type_fields']['required_neighbor_chunk_ids'] = ['absent']
        requires(a, b)
        trace = self.report([a])['offered'][0]
        self.assertEqual(trace['required_chunk_ids'], ['absent', 'b'])
        self.assertEqual(trace['absent_required_chunk_ids'], ['absent'])

    def test_deferred_malformed_rows_are_reported_without_becoming_assembly_gaps(self):
        a = row('a')
        a['chunk']['type_fields']['required_neighbor_chunk_ids'] = None
        result = self.report([a], primary_limit=0)
        self.assertEqual(result['assembly'], dict(evidence=[], context='', context_tokens=0, gaps=[]))
        self.assertFalse(result['offered'][0]['dependency_trace_complete'])
        self.assertEqual(result['offered'][0]['assembly_gaps'], [])

    def test_unemitted_overlap_is_not_claimed_to_be_missing_information(self):
        a, b = row('a'), row('b')
        result = self.report([a, b])
        self.assertEqual(result['emitted_chunk_ids'], ['a'])
        self.assertFalse(result['offered'][1]['primary_emitted'])
        self.assertTrue(result['offered'][1]['requested'])
        self.assertEqual(result['assembly']['gaps'], [])

    def test_invalid_citation_remains_a_gap_and_cannot_be_sufficient(self):
        a = row('a')
        a['spans'][0]['byte_sha256'] = '1'*64
        result = self.report([a])
        self.assertEqual(result['assembly']['gaps'], ['invalid_citation:a'])
        self.assertEqual(result['offered'][0]['assembly_gaps'], ['invalid_citation:a'])
        self.assertEqual(result['emitted_chunk_ids'], [])

    def test_missing_trace_metadata_preserves_invalid_or_deferred_assembly(self):
        for field in ('version_id', 'byte_sha256', 'similarity'):
            for limit in (0, 1):
                with self.subTest(field=field, limit=limit):
                    a = row('a')
                    del (a if field == 'similarity' else a['chunk'])[field]
                    expected = build_context([a][:limit], 100000, len)
                    result = self.report([a], primary_limit=limit)
                    self.assertEqual(result['assembly'], expected)
                    self.assertIsNone(result['offered'][0][field])
                    self.assertEqual(expected['gaps'], ['invalid_citation:a'] if limit else [])

    def test_empty_zero_and_full_prefix_are_explicit(self):
        self.assertEqual(self.report([])['offered'], [])
        a = row('a')
        result = self.report([a], primary_limit=0)
        self.assertEqual(result['requested_primary_ids'], [])
        self.assertEqual(result['deferred_primary_ids'], ['a'])
        self.assertEqual(result['assembly']['context_tokens'], 0)
        self.assertEqual(self.report([a], primary_limit=1)['deferred_primary_ids'], [])

    def test_prefix_limit_rejects_bool_noninteger_negative_and_oversized(self):
        for limit in (True, False, -1, 2, 1.0, '1'):
            with self.subTest(limit=limit), self.assertRaisesRegex(ValueError, 'primary_limit'):
                self.report([row('a')], primary_limit=limit)

    def test_flags_retain_original_validation_even_for_zero_prefix(self):
        for options in (dict(compact_citations=1), dict(shared_citations=1),
                        dict(shared_group_metadata=1), dict(shared_group_metadata=True)):
            with self.subTest(options=options), self.assertRaises(ValueError):
                self.report([row('a')], primary_limit=0, **options)

    def test_duplicate_offered_ids_keep_rank_order_and_literal_status(self):
        a = row('a')
        result = self.report([a, a], primary_limit=1)
        self.assertEqual([r['rank'] for r in result['offered']], [1, 2])
        self.assertEqual(result['deferred_primary_ids'], ['a'])
        self.assertTrue(result['offered'][1]['primary_emitted'])


if __name__ == '__main__':
    unittest.main()
