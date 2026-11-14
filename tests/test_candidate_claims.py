"""Synthetic source-limit reporting; no institutional or benchmark fixtures."""
import copy
import unittest

from backend.bintanong_retrieval.candidate_claims import build_candidate_claim_report
from backend.bintanong_retrieval.candidate_subject import prepare_candidate_subject_catalogue


def chunk(identity, subject='fees', limits=()):
    return dict(chunk_id=identity, version_id='v', byte_sha256='0'*64,
        source_text='Synthetic undergraduate evidence', text='Synthetic evidence',
        scope=['audience:undergraduate'], spans=[], type_fields=dict(
            reading_id=identity, applicability_basis_ref='synthetic-review',
            required_neighbor_chunk_ids=[], source_limits=copy.deepcopy(list(limits))))


def limit():
    return dict(gap_id='validity-unknown', issue='effectivity_currentness_unknown',
        resolution='unresolved', affected_claims=['current-year validity'],
        message='Current-year validity is unverified.', source_sha256='0'*64,
        version_id='v', field_names=['printed_effectivity'], span_indexes=[0])


class CandidateClaimTests(unittest.TestCase):
    def setUp(self):
        self.chunks = [chunk('fee', limits=[limit()]), chunk('enrollment')]
        self.catalogue = prepare_candidate_subject_catalogue(self.chunks, [
            dict(reading_id='fee', subject_id='fees', basis_ref='synthetic-review'),
            dict(reading_id='enrollment', subject_id='enrollment', basis_ref='synthetic-review')])

    def report(self, **overrides):
        args = dict(subject_id='fees', requested_claims=['current-year validity'],
                    emitted_chunk_ids=['fee'])
        args.update(overrides)
        result = build_candidate_claim_report(self.catalogue, self.chunks, **args)
        self.assertIs(result['candidate_only'], True)
        self.assertIs(result['activation_eligible'], False)
        self.assertIs(result['runtime_filter_implemented'], False)
        self.assertIs(result['claim_inference_implemented'], False)
        self.assertEqual(result['catalogue_sha256'], self.catalogue['catalogue_sha256'])
        return result

    def test_declared_limit_blocks_with_complete_empty_and_unrelated_context(self):
        for ids in (['fee'], [], ['enrollment'], None):
            with self.subTest(ids=ids):
                result = self.report(emitted_chunk_ids=ids)
                self.assertEqual(result['status'], 'insufficient_evidence')
                self.assertEqual(result['claims'][0]['status'], 'not_established')
                self.assertEqual(result['claims'][0]['source_limit_indexes'], [0])
                self.assertEqual(result['source_limits'][0]['chunk_emitted'],
                                 None if ids is None else 'fee' in ids)
                self.assertEqual(result['source_limits'][0]['limit'], limit())

    def test_unknown_claims_and_field_names_never_establish_support(self):
        for claim in ('payment channel', 'printed_effectivity', 'Current-year validity',
                      'current-year', 'prefix current-year validity suffix'):
            with self.subTest(claim=claim):
                result = self.report(requested_claims=[claim])
                self.assertEqual(result['status'], 'unassessed')
                self.assertEqual(result['claims'][0]['status'], 'unassessed')
                self.assertEqual(len(result['source_limits']), 1)

    def test_missing_hints_and_unknown_subjects(self):
        for args, status in ((dict(subject_id=None), 'needs_subject'),
                (dict(subject_id='other'), 'unavailable_subject'),
                (dict(requested_claims=None), 'needs_claims'),
                (dict(requested_claims=[]), 'needs_claims')):
            with self.subTest(args=args):
                result = self.report(**args)
                self.assertEqual(result['status'], status)
                if 'subject_id' in args:
                    self.assertEqual(result['source_limits'], [])

    def test_wrong_subject_does_not_borrow_a_limit(self):
        result = self.report(subject_id='enrollment')
        self.assertEqual(result['status'], 'unassessed')
        self.assertEqual(result['source_limits'], [])
        self.assertEqual(result['other_context_chunk_ids'], ['fee'])

    def test_mixed_known_and_unknown_claims_stay_distinct(self):
        result = self.report(requested_claims=['payment channel', 'current-year validity'])
        self.assertEqual(result['status'], 'insufficient_evidence')
        self.assertEqual([r['status'] for r in result['claims']], ['unassessed', 'not_established'])

    def test_malformed_claims_and_context_ids_are_rejected(self):
        for key, values in {
            'requested_claims': ['claim', {}, [None], [''], ['x', 'x'], ['x'*2049]],
            'emitted_chunk_ids': ['fee', {}, [None], [''], ['fee', 'fee'], ['missing']],
        }.items():
            for value in values:
                with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                    self.report(**{key: value})

    def test_stale_payload_or_catalogue_is_rejected(self):
        self.chunks[0]['text'] += ' changed'
        with self.assertRaises(ValueError):
            self.report()

    def test_malformed_limits_are_rejected_even_for_an_unknown_claim(self):
        for key, value in [('source_sha256', '1'*64), ('version_id', 'other'),
                ('gap_id', ''), ('resolution', 'resolved'), ('issue', None),
                ('message', ''), ('affected_claims', []), ('affected_claims', ['x', 'x']),
                ('affected_claims', [None])]:
            with self.subTest(key=key):
                self.setUp()
                self.chunks[0]['type_fields']['source_limits'][0][key] = value
                self.catalogue = prepare_candidate_subject_catalogue(self.chunks, self.catalogue['assignments'])
                with self.assertRaises(ValueError):
                    self.report(requested_claims=['unknown'])
        for value in (None, {}, [None]):
            with self.subTest(limits=value):
                self.setUp()
                self.chunks[0]['type_fields']['source_limits'] = value
                self.catalogue = prepare_candidate_subject_catalogue(self.chunks, self.catalogue['assignments'])
                with self.assertRaises(ValueError):
                    self.report()

    def test_input_and_result_mutation_are_isolated(self):
        before = copy.deepcopy((self.catalogue, self.chunks))
        result = self.report()
        result['source_limits'][0]['limit']['affected_claims'].append('other')
        result['claims'][0]['source_limit_indexes'].append(100)
        self.assertEqual((self.catalogue, self.chunks), before)
        self.assertEqual(self.report()['source_limits'][0]['limit'], limit())


if __name__ == '__main__':
    unittest.main()
