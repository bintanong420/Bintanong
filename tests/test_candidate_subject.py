"""Synthetic provenance/selection controls; no institutional source fixtures."""
import copy
import unittest

from backend.bintanong_retrieval.candidate_subject import (
    prepare_candidate_subject_catalogue, select_candidate_subject,
)


def chunk(identity, *, subject_audience='audience:undergraduate', required=()):
    return dict(chunk_id=identity, version_id='v', byte_sha256='0'*64,
        source_text='Synthetic source', text='Synthetic reviewed payload',
        scope=[subject_audience], spans=[], type_fields=dict(reading_id=identity,
            applicability_basis_ref='synthetic-review', required_neighbor_chunk_ids=list(required)))


def assignment(reading, subject='fees'):
    return dict(reading_id=reading, subject_id=subject, basis_ref='synthetic-field-provenance')


class CandidateSubjectTests(unittest.TestCase):
    def result(self, catalogue, chunks, **hints):
        result = select_candidate_subject(catalogue, chunks, **hints)
        self.assertIs(result['candidate_only'], True)
        self.assertIs(result['activation_eligible'], False)
        self.assertIs(result['runtime_filter_implemented'], False)
        self.assertEqual(result['claim_coverage'], 'unknown')
        self.assertEqual(result['validation_scope'], 'metadata_bindings_only')
        return result

    def test_explicit_subject_keeps_other_subjects_and_unassigned_rows_separate(self):
        chunks = [chunk('a'), chunk('b'), chunk('curriculum')]
        assignments = [assignment('a'), assignment('b', 'vehicles')]
        before = copy.deepcopy((chunks, assignments))
        catalogue = prepare_candidate_subject_catalogue(chunks, assignments)
        result = self.result(catalogue, chunks, subject_id='fees')
        self.assertEqual(result['status'], 'matched')
        self.assertEqual(result['chunk_ids'], ['a'])
        self.assertEqual(result['rows'][0]['version_id'], 'v')
        self.assertEqual(result['rows'][0]['source_sha256'], '0'*64)
        self.assertEqual(result['rows'][0]['basis_ref'], 'synthetic-field-provenance')
        self.assertEqual(catalogue['unassigned_chunk_ids'], ['curriculum'])
        self.assertEqual((chunks, assignments), before)

    def test_none_and_unknown_subject_never_fall_back_to_all_candidates(self):
        chunks = [chunk('a')]
        catalogue = prepare_candidate_subject_catalogue(chunks, [assignment('a')])
        self.assertEqual(self.result(catalogue, chunks)['status'], 'needs_subject')
        result = self.result(catalogue, chunks, subject_id='not_catalogued')
        self.assertEqual(result['status'], 'unavailable')
        self.assertEqual(result['chunk_ids'], [])
        self.assertEqual(self.result(catalogue, chunks)['chunk_ids'], [])

    def test_missing_or_changed_complete_chunk_snapshot_is_rejected(self):
        chunks = [chunk('a'), chunk('unassigned')]
        catalogue = prepare_candidate_subject_catalogue(chunks, [assignment('a')])
        for field, value in (('text', 'Changed payload'), ('source_text', 'Changed source'),
                ('version_id', 'other'), ('byte_sha256', '1'*64),
                ('scope', ['audience:graduate']), ('spans', [{'text': 'changed'}])):
            with self.subTest(field=field), self.assertRaises(ValueError):
                changed = copy.deepcopy(chunks)
                changed[0][field] = value
                self.result(catalogue, changed, subject_id='fees')
        with self.assertRaises(ValueError):
            self.result(catalogue, chunks[:1], subject_id='fees')
        changed = copy.deepcopy(chunks)
        changed[1]['text'] = 'Unassigned rows are bound too'
        with self.assertRaises(ValueError):
            self.result(catalogue, changed, subject_id='fees')

    def test_dependency_chain_and_cycle_require_same_subject_membership(self):
        chunks = [chunk('a', required=['b']), chunk('b', required=['c']), chunk('c', required=['a'])]
        catalogue = prepare_candidate_subject_catalogue(chunks, [assignment(i) for i in 'abc'])
        self.assertEqual(set(self.result(catalogue, chunks, subject_id='fees')['chunk_ids']), set('abc'))
        for assignments in ([assignment('a')], [assignment('a'), assignment('b'), assignment('c', 'other')]):
            with self.subTest(assignments=assignments), self.assertRaisesRegex(ValueError, 'dependency'):
                prepare_candidate_subject_catalogue(chunks, assignments)
        with self.assertRaisesRegex(ValueError, 'dependency'):
            prepare_candidate_subject_catalogue([chunk('a', required=['absent'])], [assignment('a')])

    def test_unknown_mixed_or_excluded_audience_is_never_assigned(self):
        for scope in ([], ['audience:law'], ['audience:graduate'], ['audience:faculty'],
                      ['audience:undergraduate', 'audience:medicine']):
            with self.subTest(scope=scope), self.assertRaises(ValueError):
                c = chunk('a');c['scope'] = scope
                prepare_candidate_subject_catalogue([c], [assignment('a')])

    def test_missing_applicability_reference_is_not_promoted_by_tagging(self):
        for value in (None, '', ' '):
            with self.subTest(value=value), self.assertRaises(ValueError):
                c = chunk('a');c['type_fields']['applicability_basis_ref'] = value
                prepare_candidate_subject_catalogue([c], [assignment('a')])

    def test_duplicate_or_missing_reading_assignments_are_ambiguous(self):
        chunks = [chunk('a')]
        for assignments in ([assignment('a'), assignment('a')], [assignment('absent')]):
            with self.subTest(assignments=assignments), self.assertRaises(ValueError):
                prepare_candidate_subject_catalogue(chunks, assignments)
        for field in ('chunk_id', 'reading_id'):
            with self.subTest(field=field), self.assertRaises(ValueError):
                b = chunk('b')
                if field == 'reading_id':b['type_fields'][field] = 'a'
                else:b[field] = 'a'
                prepare_candidate_subject_catalogue(chunks+[b], [])

    def test_invalid_assignment_and_hint_types_are_rejected(self):
        for invalid in ({}, {'reading_id': 'a', 'subject_id': 'fees'},
                        assignment('a') | {'subject_id': True}, assignment('a') | {'subject_id': 'Fees '},
                        assignment('a') | {'basis_ref': ''}, assignment('a') | {'gold': ['a']}):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                prepare_candidate_subject_catalogue([chunk('a')], [invalid])
        chunks = [chunk('a')];catalogue = prepare_candidate_subject_catalogue(chunks, [assignment('a')])
        for hint in ('', ' fees', True, [], 7):
            with self.subTest(hint=hint), self.assertRaises(ValueError):
                self.result(catalogue, chunks, subject_id=hint)

    def test_source_hash_and_neighbor_metadata_are_validated(self):
        for required in ('b', [1], [''], ['b', 'b']):
            with self.subTest(required=required), self.assertRaises(ValueError):
                c = chunk('a');c['type_fields']['required_neighbor_chunk_ids'] = required
                prepare_candidate_subject_catalogue([c], [])
        c = chunk('a');c['byte_sha256'] = 'bad'
        with self.assertRaises(ValueError):prepare_candidate_subject_catalogue([c], [])

    def test_catalogue_digest_flags_and_extra_fields_are_checked(self):
        chunks = [chunk('a')];catalogue = prepare_candidate_subject_catalogue(chunks, [assignment('a')])
        for field, value in (('candidate_only', 1), ('activation_eligible', True),
                ('runtime_filter_implemented', True), ('claim_coverage', 'sufficient'),
                ('catalogue_sha256', 'f'*64), ('extra', 'ignored?')):
            with self.subTest(field=field), self.assertRaises(ValueError):
                changed = copy.deepcopy(catalogue);changed[field] = value
                self.result(changed, chunks, subject_id='fees')
        changed = copy.deepcopy(catalogue);changed['assignments'][0]['subject_id'] = 'vehicles'
        with self.assertRaises(ValueError):self.result(changed, chunks, subject_id='vehicles')

    def test_catalogue_order_is_stable_and_results_do_not_alias_inputs(self):
        chunks = [chunk('b'), chunk('a')];assignments = [assignment('b'), assignment('a')]
        catalogue = prepare_candidate_subject_catalogue(chunks, assignments)
        self.assertEqual(catalogue, prepare_candidate_subject_catalogue(chunks[::-1], assignments[::-1]))
        before = copy.deepcopy((chunks, catalogue))
        result = self.result(catalogue, chunks, subject_id='fees')
        result['rows'][0]['required_chunk_ids'].append('changed')
        result['chunk_ids'].clear()
        self.assertEqual((chunks, catalogue), before)

    def test_empty_catalogue_does_not_invent_support(self):
        catalogue = prepare_candidate_subject_catalogue([], [])
        self.assertEqual(self.result(catalogue, [])['status'], 'needs_subject')
        self.assertEqual(self.result(catalogue, [], subject_id='fees')['status'], 'unavailable')

    def test_unassigned_nested_metadata_does_not_alias_the_source_snapshot(self):
        c = chunk('unassigned')
        c['type_fields']['applicability_basis_ref'] = {'pending': ['unreviewed']}
        before = copy.deepcopy(c)
        catalogue = prepare_candidate_subject_catalogue([c], [])
        catalogue['bindings'][0]['applicability_basis_ref']['pending'].append('changed')
        self.assertEqual(c, before)


if __name__ == '__main__':
    unittest.main()
