"""Synthetic engine policy evidence; no institutional or private fixtures."""
import copy
import importlib
import importlib.util
import unittest

from backend.bintanong_retrieval.candidate_subject import prepare_candidate_subject_catalogue
from backend.bintanong_retrieval.candidate_claims import prepare_candidate_claim_reviews
from tests.test_retrieval_context import evidence


def policy_fixture():
    rows = [evidence(i, 'Synthetic amount '+i, page=n) for n, i in enumerate(('a', 'b', 'other'), 1)]
    for row in rows:
        c = row['chunk']
        c.update(chunk_type='text', chunker_version='synthetic-v1', content_hash='1'*64,
                 scope=['audience:undergraduate'])
        c['type_fields'].update(reading_id=c['chunk_id'], applicability_basis_ref='synthetic-review',
            field_associations=[dict(name='printed_amount', value=c['text'], source_blank=False,
                                    event_sha256='2'*64, span_indexes=[0])])
    rows[0]['chunk']['type_fields']['required_neighbor_chunk_ids'] = ['b']
    rows[0]['neighbors'] = [copy.deepcopy(rows[1])]
    chunks = [copy.deepcopy(row['chunk']) | {'spans': copy.deepcopy(row['spans'])} for row in rows]
    assignments = [dict(reading_id=c['chunk_id'], subject_id='other' if c['chunk_id']=='other' else 'fees',
                        basis_ref='synthetic-review') for c in chunks]
    catalogue = prepare_candidate_subject_catalogue(chunks, assignments)
    visible = dict(subject_id='fees', claim='printed amount', finding='visible_fields',
        reviewed_chunk_ids=['a', 'b'], field_refs=[dict(reading_id='a', field_name='printed_amount')],
        basis_ref='synthetic-source-review', basis_sha256='3'*64)
    absent = visible | dict(claim='payment permission', finding='not_stated_in_selected_fields', field_refs=[])
    reviews = prepare_candidate_claim_reviews(catalogue, chunks, [visible, absent])
    return dict(release_id='release-test', embedding_set_id='set', chunks=chunks,
                catalogue=catalogue, claim_reviews=reviews), rows


def policy_class(test):
    name = 'backend.bintanong_retrieval.evidence_policy'
    test.assertIsNotNone(importlib.util.find_spec(name), 'source-aware evidence policy is not implemented')
    return importlib.import_module(name).SourceAwareEvidencePolicy


class EvidencePolicyBindingTests(unittest.TestCase):
    def setUp(self):
        self.inputs, self.rows = policy_fixture()

    def make(self):
        return policy_class(self)(**self.inputs)

    def raw(self, rows=None):
        return dict(release_id='release-test', embedding_set_id='set', items=self.rows if rows is None else rows)

    def test_changed_authoritative_fields_reject_the_transport(self):
        policy = self.make()
        policy._bind('release-test', self.raw())
        for key, value in [('source_text', 'Changed'), ('text', 'Changed'), ('scope', []),
                           ('content_hash', '4'*64), ('type_fields', {})]:
            with self.subTest(key=key):
                rows = copy.deepcopy(self.rows)
                rows[0]['chunk'][key] = value
                with self.assertRaises(ValueError):
                    policy._bind('release-test', self.raw(rows))

    def test_projection_allows_only_transport_and_packaging_extras(self):
        self.inputs['chunks'][0]['source_label'] = 'Original packaging'
        self.inputs['catalogue'] = prepare_candidate_subject_catalogue(
            self.inputs['chunks'], self.inputs['catalogue']['assignments'])
        self.inputs['claim_reviews'] = prepare_candidate_claim_reviews(
            self.inputs['catalogue'], self.inputs['chunks'], self.inputs['claim_reviews']['reviews'])
        policy = self.make()
        rows = copy.deepcopy(self.rows)
        rows[0]['chunk']['created_at'] = 'transport-only'
        rows[0]['spans'][0].update(span_id='database-id', span_order=0, chunk_id='a')
        policy._bind('release-test', self.raw(rows))
        rows[0]['spans'][0]['text'] = 'Changed visible text'
        with self.assertRaises(ValueError):
            policy._bind('release-test', self.raw(rows))

    def test_wrong_release_set_unknown_and_conflicting_duplicate_ids_reject(self):
        policy = self.make()
        for args in [('other', self.raw()), ('release-test', self.raw() | {'release_id':'other'}),
                     ('release-test', self.raw() | {'embedding_set_id':'other'})]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                policy._bind(*args)
        for mutation in ('unknown', 'duplicate', 'missing'):
            rows = copy.deepcopy(self.rows)
            if mutation == 'unknown':
                rows[0]['chunk']['chunk_id'] = 'unknown'
            elif mutation == 'duplicate':
                rows.append(copy.deepcopy(rows[0]))
                rows[-1]['spans'][0]['page'] = 19
            else:
                del rows[0]['chunk']['content_hash']
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                policy._bind('release-test', self.raw(rows))
        policy._bind('release-test', self.raw(self.rows+[copy.deepcopy(self.rows[0])]))

    def test_caller_mutation_cannot_change_bound_snapshot_or_assessment(self):
        policy = self.make()
        digest = policy._metadata()['snapshot_sha256']
        self.inputs['chunks'][0]['text'] = 'Mutated after construction'
        self.inputs['claim_reviews']['reviews'].clear()
        policy._bind('release-test', self.raw())
        report = policy._assess('fees', ('printed amount',), ['a', 'b'])
        self.assertEqual(report['status'], 'reviewed_fields_available')
        report['claims'][0]['source_fields'][0]['field']['value'] = 'Changed'
        self.assertEqual(policy._assess('fees', ('printed amount',), ['a', 'b'])['claims'][0]
                         ['source_fields'][0]['field']['value'], 'Synthetic amount a')
        self.assertEqual(policy._metadata()['snapshot_sha256'], digest)

    def test_invalid_original_catalogue_or_register_is_not_rebound_as_valid(self):
        for mutation in ('chunk', 'review', 'identity'):
            inputs, _ = policy_fixture()
            if mutation == 'chunk':
                inputs['chunks'][0]['type_fields']['field_associations'][0]['value'] = 'Changed'
            elif mutation == 'review':
                inputs['claim_reviews']['reviews'][0]['basis_ref'] = 'Changed'
            else:
                inputs['release_id'] = ''
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                policy_class(self)(**inputs)

    def test_ordered_source_spans_and_nested_neighbors_are_bound(self):
        policy = self.make()
        rows = copy.deepcopy(self.rows)
        rows[0]['neighbors'][0]['spans'][0]['locator']['section_path'] = ['Changed']
        with self.assertRaises(ValueError):
            policy._bind('release-test', self.raw(rows))
        rows = copy.deepcopy(self.rows)
        rows[0]['spans'].append(copy.deepcopy(rows[0]['spans'][0]))
        with self.assertRaises(ValueError):
            policy._bind('release-test', self.raw(rows))

    def test_snapshot_digest_and_subject_selection_are_deterministic(self):
        first = self.make()
        second = self.make()
        self.assertEqual(first._metadata()['snapshot_sha256'], second._metadata()['snapshot_sha256'])
        selected = first._select(self.rows, 'fees')
        self.assertEqual([r['chunk']['chunk_id'] for r in selected], ['a', 'b'])
        self.assertEqual(selected[0]['neighbors'], self.rows[0]['neighbors'])
        self.assertEqual(first._select(self.rows, 'absent'), [])
        self.assertEqual(first._assess('fees', ('payment permission',), [])['status'], 'insufficient_evidence')
