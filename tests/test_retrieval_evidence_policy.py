"""Synthetic engine policy evidence; no institutional or private fixtures."""
import copy
import importlib
import importlib.util
import unittest

from backend.bintanong_retrieval.candidate_subject import prepare_candidate_subject_catalogue
from backend.bintanong_retrieval.candidate_claims import prepare_candidate_claim_reviews
from tests.test_retrieval_context import evidence
from tests.test_retrieval_engine import Client, Encoder
from backend.bintanong_retrieval.engine import RetrievalEngine
from backend.bintanong_retrieval.types import RetrievalRequest, RetrievalSettings


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


class EvidencePolicyEngineTests(unittest.TestCase):
    def setUp(self):
        self.inputs, self.rows = policy_fixture()
        self.client, self.encoder = Client(), Encoder()
        self.client.payload['items'] = self.rows[:1]
        self.request = RetrievalRequest('Synthetic fee question', 'release-test')

    def remint(self):
        self.inputs['chunks'] = [copy.deepcopy(r['chunk']) | {'spans':copy.deepcopy(r['spans'])} for r in self.rows]
        self.inputs['catalogue'] = prepare_candidate_subject_catalogue(
            self.inputs['chunks'], self.inputs['catalogue']['assignments'])
        self.inputs['claim_reviews'] = prepare_candidate_claim_reviews(
            self.inputs['catalogue'], self.inputs['chunks'], self.inputs['claim_reviews']['reviews'])

    def engine(self, **settings):
        return RetrievalEngine(self.client, self.encoder,
            RetrievalSettings(context_budget=12000, **settings), evidence_policy=policy_class(self)(**self.inputs))

    def result(self, **intent):
        return self.engine().retrieve(self.request, **(dict(subject_id='fees', requested_claims=('printed amount',)) | intent))

    def test_available_fields_use_actual_engine_emission_without_answer_permission(self):
        out = self.result()
        self.assertEqual(out['schema_version'], 'bintanong-retrieval-debug-v2')
        self.assertEqual(out['status'], 'uncalibrated')
        self.assertEqual(out['coverage'], 'partial')
        self.assertIs(out['candidate_only'], True)
        self.assertIs(out['activation_eligible'], False)
        self.assertIs(out['runtime_authorization_verified'], False)
        self.assertEqual(out['answer_sufficiency'], 'unassessed')
        report = out['evidence_policy']['assessment']
        self.assertEqual(report['status'], 'reviewed_fields_available')
        self.assertEqual(report['emitted_chunk_ids'], ['a', 'b'])
        self.assertEqual([e['chunk_id'] for e in out['evidence']], ['a', 'b'])
        self.assertEqual(out['context_tokens'], len(out['context']))
        self.assertIn('shared-source-locators-v1', out['context'])
        self.assertEqual(out['configuration']['fingerprint'], RetrievalSettings(context_budget=12000).fingerprint)
        self.assertTrue(all(role == 'runtime' for role in self.client.roles))

    def test_reviewed_absence_beats_related_high_scoring_context(self):
        out = self.result(requested_claims=('payment permission',))
        self.assertEqual(out['status'], 'insufficient_evidence')
        self.assertIn('requested_claim_not_established', out['gaps'])
        self.assertEqual(out['evidence_policy']['assessment']['claims'][0]['status'], 'not_established')
        self.assertEqual(out['evidence'][0]['similarity'], 0.9)

    def test_known_limit_on_unreturned_member_is_not_erased(self):
        self.rows[0]['chunk']['type_fields']['required_neighbor_chunk_ids'] = []
        self.rows[0]['neighbors'] = []
        self.rows[1]['chunk']['type_fields']['source_limits'] = [dict(gap_id='missing-claim',
            issue='claim_not_stated', message='Synthetic unresolved condition', resolution='unresolved',
            affected_claims=['printed amount'], source_sha256='0'*64, version_id='version')]
        self.remint()
        out = self.result()
        self.assertEqual(out['status'], 'insufficient_evidence')
        self.assertEqual([e['chunk_id'] for e in out['evidence']], ['a'])
        self.assertIs(out['evidence_policy']['assessment']['source_limits'][0]['chunk_emitted'], False)

    def test_unknown_and_mixed_claims_remain_unassessed(self):
        for claims in [('unknown',), ('printed amount','unknown')]:
            with self.subTest(claims=claims):
                out = self.result(requested_claims=claims)
                self.assertEqual(out['status'], 'unassessed')
                self.assertEqual(out['coverage'], 'partial')
        self.assertEqual(self.result(requested_claims=('unknown','payment permission'))['status'], 'insufficient_evidence')

    def test_missing_intent_or_unknown_subject_exposes_no_context_or_values(self):
        for intent, status in [(dict(subject_id=None),'needs_subject'),
                               (dict(subject_id='absent'),'insufficient_evidence'),
                               (dict(requested_claims=None),'needs_claims'),
                               (dict(requested_claims=()),'needs_claims')]:
            with self.subTest(intent=intent):
                out = self.result(**intent)
                self.assertEqual(out['status'], status)
                self.assertEqual(out['context'], '')
                self.assertEqual(out['evidence'], [])
                self.assertEqual(out['coverage'], 'none')
                self.assertIsNone(out['evidence_policy']['assessment'])

    def test_invalid_intent_is_rejected_before_encoding(self):
        for intent in [dict(subject_id='Fees'),dict(subject_id=2),dict(requested_claims=['printed amount']),
                       dict(requested_claims=(' ',)),dict(requested_claims=('same','same'))]:
            with self.subTest(intent=intent):
                out = self.result(**intent)
                self.assertEqual(out['status'], 'invalid_query')
                self.assertEqual(self.encoder.calls, 0)

    def test_legacy_v1_call_is_unchanged_and_rejects_unconfigured_intent(self):
        engine = RetrievalEngine(self.client, self.encoder, RetrievalSettings(context_budget=12000))
        before = engine.retrieve(self.request)
        self.assertEqual(before['schema_version'], 'bintanong-retrieval-debug-v1')
        self.assertNotIn('evidence_policy', before)
        self.assertEqual(engine.retrieve(self.request), before)
        calls = self.encoder.calls
        out = engine.retrieve(self.request, subject_id='fees')
        self.assertEqual(out['status'], 'invalid_query')
        self.assertEqual(self.encoder.calls, calls)

    def test_empty_context_and_missing_neighbors_do_not_use_snapshot_ids_as_emission(self):
        self.client.payload['items'] = []
        out = self.result()
        self.assertEqual(out['status'], 'insufficient_evidence')
        self.assertEqual(out['evidence_policy']['assessment']['emitted_chunk_ids'], [])
        self.client.payload['items'] = [copy.deepcopy(self.rows[0])]
        self.client.payload['items'][0]['neighbors'] = []
        out = self.result()
        self.assertEqual(out['evidence_policy']['assessment']['emitted_chunk_ids'], [])
        self.assertIn('missing_required_neighbor:a', out['gaps'])

    def test_oversized_context_stays_insufficient(self):
        engine = RetrievalEngine(self.client, self.encoder, RetrievalSettings(context_budget=1),
                                 evidence_policy=policy_class(self)(**self.inputs))
        out = engine.retrieve(self.request, subject_id='fees', requested_claims=('printed amount',))
        self.assertEqual(out['status'], 'insufficient_evidence')
        self.assertEqual(out['context_tokens'], 0)
        self.assertIn('context_budget:a', out['gaps'])

    def test_binding_failure_clears_context_and_does_not_expose_snapshot_values(self):
        engine = self.engine()
        self.client.payload['items'][0]['chunk']['text'] = 'Changed transport'
        out = engine.retrieve(self.request, subject_id='fees', requested_claims=('printed amount',))
        self.assertEqual(out['status'], 'policy_binding_error')
        self.assertEqual(out['evidence'], [])
        self.assertEqual(out['context'], '')
        self.assertIsNone(out['evidence_policy']['assessment'])
        self.assertIn('source_snapshot_mismatch', out['gaps'])

    def test_early_retrieval_failures_do_not_assess_source_claims(self):
        for key, value, status in [('status','release_changed','release_changed'),
                                   ('embedding_set_id','wrong-set','policy_binding_error')]:
            with self.subTest(key=key):
                self.client.payload[key] = value
                out = self.result()
                self.assertEqual(out['status'], status)
                self.assertIsNone(out['evidence_policy']['assessment'])
                self.assertTrue(out['evidence_policy']['not_run_reason'])
                self.client.payload.update(status='ok', embedding_set_id='set')

    def test_off_subject_conflicts_and_ambiguous_curricula_win_before_selection(self):
        other = self.rows[2]
        other['chunk'].update(version_id='other-version', byte_sha256='4'*64)
        other['version'].update(version_id='other-version', byte_sha256='4'*64)
        other['spans'][0].update(version_id='other-version', byte_sha256='4'*64)
        self.remint()
        self.client.payload['items'] = [self.rows[0], other]
        out = self.result()
        self.assertEqual(out['status'], 'conflicting_sources')
        self.assertIsNone(out['evidence_policy']['assessment'])
        self.rows[0]['chunk']['scope'].append('curriculum:one')
        other['chunk']['scope'].append('curriculum:two')
        self.remint()
        self.assertEqual(self.result()['status'], 'needs_scope')

    def test_arbitrary_policy_name_cannot_promote_available_fields_to_ok(self):
        out = self.engine(policy_id='pretend-approved').retrieve(
            self.request, subject_id='fees', requested_claims=('printed amount',))
        self.assertEqual(out['status'], 'uncalibrated')
        self.assertEqual(out['coverage'], 'partial')

    def test_invalid_citation_with_matching_binding_cannot_establish_fields(self):
        self.rows[0]['spans'][0]['locator'] = {}
        self.remint()
        out = self.result()
        self.assertEqual(out['status'], 'insufficient_evidence')
        self.assertEqual(out['evidence'], [])
        self.assertIn('invalid_citation:a', out['gaps'])
        self.assertEqual(out['evidence_policy']['assessment']['emitted_chunk_ids'], [])

    def test_reviewed_group_limits_and_exact_context_tokens_survive_engine_assembly(self):
        from tests.test_reviewed_record_context import ReviewedRecordContextTests
        fixture = ReviewedRecordContextTests()
        fixture.setUp()
        bundle = fixture.build(fixture.eligible())
        rows = fixture.candidates(bundle)
        chunks = bundle['chunks']
        catalogue = prepare_candidate_subject_catalogue(chunks, [dict(
            reading_id=c['type_fields']['reading_id'], subject_id='policy', basis_ref='synthetic-review')
            for c in chunks])
        review = dict(subject_id='policy', claim='printed clauses', finding='visible_fields',
            reviewed_chunk_ids=[c['chunk_id'] for c in chunks], field_refs=[dict(
                reading_id=chunks[0]['type_fields']['reading_id'],
                field_name=chunks[0]['type_fields']['field_associations'][0]['name'])],
            basis_ref='synthetic-source-review', basis_sha256='3'*64)
        policy = policy_class(self)(release_id='release-test', embedding_set_id='set', chunks=chunks,
            catalogue=catalogue, claim_reviews=prepare_candidate_claim_reviews(catalogue, chunks, [review]))
        self.client.payload['items'] = rows[:1]
        engine = RetrievalEngine(self.client, self.encoder, RetrievalSettings(context_budget=32000), evidence_policy=policy)
        out = engine.retrieve(self.request, subject_id='policy', requested_claims=('printed clauses',))
        self.assertEqual(out['status'], 'uncalibrated')
        self.assertEqual(len(out['evidence']), 4)
        self.assertIn('shared-source-groups-v1', out['context'])
        self.assertIn('conflicting_deadlines', out['context'])
        self.assertEqual(out['context_tokens'], len(out['context']))
        self.assertEqual(out['evidence_policy']['assessment']['status'], 'reviewed_fields_available')

    def test_emitted_footnote_cannot_stand_in_for_an_unrendered_reviewed_field(self):
        self.rows[0]['spans'][0]['text'] = ''
        self.rows[0]['spans'].append(dict(self.rows[0]['spans'][0], span_id='footnote',
            text='A separate synthetic footnote', locator={'kind':'section','section_path':['Footnote']}))
        self.remint()
        out = self.result()
        self.assertEqual([e['chunk_id'] for e in out['evidence']], ['a', 'b'])
        self.assertNotIn('Synthetic amount a', out['context'])
        self.assertEqual(out['status'], 'insufficient_evidence')
        report = out['evidence_policy']['assessment']
        self.assertEqual(report['status'], 'insufficient_context')
        self.assertEqual(report['claims'][0]['status'], 'reviewed_fields_not_in_context')
        self.assertEqual(report['claims'][0]['unverified_rendered_fields'][0]['field_name'], 'printed_amount')

    def test_malformed_transport_version_returns_a_binding_failure(self):
        engine = self.engine()
        for invalid in (None, [], 'version', 1):
            with self.subTest(invalid=invalid):
                self.client.payload['items'][0]['version'] = invalid
                out = engine.retrieve(self.request, subject_id='fees', requested_claims=('printed amount',))
                self.assertEqual(out['status'], 'policy_binding_error')
                self.assertEqual(out['context'], '')
                self.assertEqual(out['evidence'], [])
                self.assertIsNone(out['evidence_policy']['assessment'])
