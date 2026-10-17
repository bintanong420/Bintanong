"""Synthetic trusted source reviews; no student benchmark or real-source fixtures."""
import copy
import unittest

from backend.bintanong_retrieval.candidate_claims import (
    prepare_candidate_claim_reviews, build_candidate_claim_report,
)
from backend.bintanong_retrieval.candidate_subject import prepare_candidate_subject_catalogue


def chunk(identity, required=()):
    return dict(chunk_id=identity, version_id='v', byte_sha256='0'*64,
        text='Synthetic source field', source_text='Synthetic source field',
        scope=['audience:undergraduate'], spans=[dict(version_id='v', byte_sha256='0'*64,
            page=1, span_id='span-'+identity, text='0')], type_fields=dict(
            reading_id=identity, applicability_basis_ref='synthetic-review',
            required_neighbor_chunk_ids=list(required), source_limits=[], field_associations=[
                dict(name='printed_amount', value=0, source_blank=False,
                     event_sha256='1'*64, span_indexes=[0])]))


class CandidateClaimReviewTests(unittest.TestCase):
    def setUp(self):
        self.chunks = [chunk('a', ['b']), chunk('b', ['c']), chunk('c', ['a']), chunk('other')]
        self.assignments = [dict(reading_id=c['chunk_id'],
            subject_id='other' if c['chunk_id']=='other' else 'fees', basis_ref='synthetic-review') for c in self.chunks]
        self.catalogue = prepare_candidate_subject_catalogue(self.chunks, self.assignments)
        self.visible = dict(subject_id='fees', claim='printed amount', finding='visible_fields',
            reviewed_chunk_ids=['a','b','c'], field_refs=[dict(reading_id='a', field_name='printed_amount')],
            basis_ref='synthetic-source-audit#amount', basis_sha256='2'*64)
        self.absence = self.visible | dict(claim='payment permission', finding='not_stated_in_selected_fields', field_refs=[])

    def prepare(self, reviews=None):
        return prepare_candidate_claim_reviews(self.catalogue, self.chunks,
            [self.visible,self.absence] if reviews is None else reviews)

    def report(self, **kwargs):
        args = dict(subject_id='fees', requested_claims=['printed amount'],
                    emitted_chunk_ids=['a','b','c'], claim_reviews=self.prepare())
        args.update(kwargs)
        return build_candidate_claim_report(self.catalogue, self.chunks, **args)

    def test_visible_fields_require_transitive_context_and_preserve_explicit_zero(self):
        report = self.report()
        self.assertEqual(report['schema_version'], 'bintanong-candidate-claim-report-v2')
        self.assertEqual(report['status'], 'reviewed_fields_available')
        self.assertEqual(report['answer_sufficiency'], 'unassessed')
        self.assertEqual(report['claim_coverage'], 'unassessed')
        field = report['claims'][0]['source_fields'][0]
        self.assertEqual(field['field']['value'], 0)
        self.assertEqual(field['spans'], self.chunks[0]['spans'])
        self.assertEqual(report['claims'][0]['required_chunk_ids'], ['a','b','c'])
        for ids, missing in ((['a'], ['b','c']), ([], ['a','b','c']), (None,None)):
            with self.subTest(ids=ids):
                report = self.report(emitted_chunk_ids=ids)
                self.assertEqual(report['status'], 'insufficient_context')
                self.assertEqual(report['claims'][0]['status'], 'reviewed_fields_not_in_context')
                self.assertEqual(report['claims'][0]['missing_required_chunk_ids'], missing)

    def test_absence_review_is_bounded_and_independent_of_emission(self):
        for ids in (None, [], ['other'], ['a','b','c']):
            with self.subTest(ids=ids):
                report = self.report(requested_claims=['payment permission'], emitted_chunk_ids=ids)
                self.assertEqual(report['status'], 'insufficient_evidence')
                self.assertEqual(report['claims'][0]['status'], 'not_established')
                self.assertEqual(report['claims'][0]['source_review']['reviewed_chunk_ids'], ['a','b','c'])
                self.assertIs(report['activation_eligible'], False)

    def test_unknown_mixed_claims_and_other_subjects_are_unassessed(self):
        for args in (dict(requested_claims=['unknown']),
                     dict(requested_claims=['printed amount','unknown']),
                     dict(subject_id='other'), dict(requested_claims=['Printed amount'])):
            with self.subTest(args=args):
                self.assertEqual(self.report(**args)['status'], 'unassessed')
        self.assertEqual(self.report(requested_claims=[])['status'], 'needs_claims')
        self.assertEqual(self.report(subject_id=None)['status'], 'needs_subject')
        self.assertEqual(self.report(subject_id='missing')['status'], 'unavailable_subject')

    def test_known_unresolved_limit_overrides_visible_review(self):
        self.chunks[0]['type_fields']['source_limits']=[dict(gap_id='unknown', issue='source_cutoff',
            resolution='unresolved', affected_claims=['printed amount'], message='Synthetic limit',
            source_sha256='0'*64, version_id='v')]
        self.catalogue=prepare_candidate_subject_catalogue(self.chunks,self.assignments)
        report=self.report()
        self.assertEqual(report['status'],'insufficient_evidence')
        self.assertEqual(report['claims'][0]['status'],'not_established')
        self.assertEqual(report['claims'][0]['source_limit_indexes'],[0])

    def test_register_determinism_and_defensive_copies(self):
        first=self.prepare(); reversed_reviews=copy.deepcopy([self.absence,self.visible])
        reversed_reviews[1]['reviewed_chunk_ids'].reverse()
        self.assertEqual(first,self.prepare(reversed_reviews))
        before=copy.deepcopy((self.catalogue,self.chunks,self.visible,self.absence))
        report=self.report();report['claims'][0]['source_fields'][0]['field']['span_indexes'].append(9)
        report['claims'][0]['source_review']['field_refs'][0]['field_name']='changed'
        first['reviews'][0]['reviewed_chunk_ids'].append('changed')
        self.assertEqual((self.catalogue,self.chunks,self.visible,self.absence),before)

    def test_partial_unknown_duplicate_and_malformed_reviews_rejected(self):
        mutations=[dict(subject_id='missing'),dict(claim=''),dict(finding='supported'),
            dict(reviewed_chunk_ids=['a']),dict(reviewed_chunk_ids=['a','b','c','c']),
            dict(reviewed_chunk_ids=['a','b','other']),dict(field_refs=[]),dict(basis_ref=''),
            dict(basis_sha256='no'),dict(extra=True),dict(field_refs=[dict(reading_id='other',field_name='printed_amount')]),
            dict(field_refs=[dict(reading_id='a',field_name='missing')]),dict(field_refs=[dict(reading_id='a')]),
            dict(field_refs=[dict(reading_id='a',field_name='printed_amount')]*2)]
        for mutation in mutations:
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.prepare([self.visible|mutation])
        for rows in (None, {}, 'reviews', [None], [self.visible,self.visible], [self.absence|dict(field_refs=self.visible['field_refs'])]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                prepare_candidate_claim_reviews(self.catalogue,self.chunks,rows)

    def test_register_field_reference_mutation_does_not_change_input(self):
        before = copy.deepcopy(self.visible)
        register = self.prepare([self.visible])
        register['reviews'][0]['field_refs'][0]['field_name'] = 'changed'
        self.assertEqual(self.visible, before)

    def test_blank_missing_or_foreign_field_provenance_rejected(self):
        for key,value in [('source_blank',True),('source_blank',None),('value',None),('value',''),
                          ('event_sha256','bad'),('span_indexes',[]),('span_indexes',[-1]),
                          ('span_indexes',[True]),('span_indexes',[1]),('span_indexes',[0,0])]:
            with self.subTest(key=key,value=value):
                self.setUp();self.chunks[0]['type_fields']['field_associations'][0][key]=value
                self.catalogue=prepare_candidate_subject_catalogue(self.chunks,self.assignments)
                with self.assertRaises(ValueError):self.prepare()
        for key,value in [('version_id','foreign'),('byte_sha256','1'*64)]:
            with self.subTest(key=key):
                self.setUp();self.chunks[0]['spans'][0][key]=value
                self.catalogue=prepare_candidate_subject_catalogue(self.chunks,self.assignments)
                with self.assertRaises(ValueError):self.prepare()

    def test_stale_or_modified_register_and_snapshot_rejected(self):
        register=self.prepare()
        for key,value in [('reviews',[]),('activation_eligible',True),('catalogue_sha256','9'*64),('reviews_sha256','9'*64)]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.report(claim_reviews=register|{key:value})
        self.chunks[0]['text']='changed'
        with self.assertRaises(ValueError):self.report(claim_reviews=register)

    def test_default_report_is_unchanged_without_opt_in(self):
        args=dict(subject_id='fees',requested_claims=['printed amount'],emitted_chunk_ids=['a','b','c'])
        old=build_candidate_claim_report(self.catalogue,self.chunks,**args)
        self.assertEqual(old,build_candidate_claim_report(self.catalogue,self.chunks,**args,claim_reviews=None))
        self.assertNotIn('claim_reviews_sha256',old)
        self.assertEqual(old['status'],'unassessed')


if __name__=='__main__':
    unittest.main()
