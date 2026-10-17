"""Synthetic source-aware engine integration; no institutional approvals or model."""
import copy
from dataclasses import replace
import json
import unittest

from backend.bintanong_contracts.source import compute_content_hash
from backend.bintanong_embedding.adapter import EmbeddingConfig
from backend.bintanong_retrieval.candidate_claims import prepare_candidate_claim_reviews
from backend.bintanong_retrieval.candidate_subject import prepare_candidate_subject_catalogue
from backend.bintanong_retrieval.engine import RetrievalEngine
from backend.bintanong_retrieval.evidence_policy import SourceAwareEvidencePolicy
from backend.bintanong_retrieval.types import RetrievalRequest, RetrievalSettings
from backend.bintanong_storage.release import ReleaseManager
from tests.storage_database import DatabaseStorageClient, FIXTURE, StorageDatabase, sql_literal
from tests.test_retrieval_database import IDENTITY


class DatabaseRuntimeRoleTests(unittest.TestCase):
    def test_client_executes_reads_and_rpc_under_each_explicit_runtime_role(self):
        class RecordingDatabase:
            def __init__(self):
                self.statements = []

            def json(self, sql):
                self.statements.append(sql)
                return []

        for configured, role in ((None, 'anon'), ('anon', 'anon'), ('authenticated', 'authenticated')):
            with self.subTest(role=role):
                db = RecordingDatabase()
                client = DatabaseStorageClient(db) if configured is None else DatabaseStorageClient(db, runtime_role=configured)
                client.select('knowledge_releases')
                client.rpc('retrieve_context', {})
                client.select('knowledge_releases', role='admin')
                client.rpc('create_release', {}, role='admin')
                self.assertEqual(len(db.statements), 4)
                self.assertTrue(all(f'begin; set local role {role};' in s for s in db.statements[:2]))
                self.assertTrue(all('begin; set local role service_role;' in s for s in db.statements[2:]))

    def test_runtime_role_cannot_be_privileged_or_injected(self):
        for role in ('postgres', 'service_role', 'admin', 'anon; reset role;', None):
            with self.subTest(role=role), self.assertRaises(ValueError):
                DatabaseStorageClient(object(), runtime_role=role)


class SyntheticEncoder:
    config = replace(EmbeddingConfig(), **IDENTITY)

    def __init__(self):
        self.calls = 0

    def encode(self, query):
        self.calls += 1
        return [1.0] + [0.0] * 1023

    def count_context_tokens(self, text):
        return len(text)  # Explicit fixture counter, not a model token measurement.


def synthetic_chunks():
    """Declared source snapshot, independent of RPC/database serialization."""
    chunks = []
    for key, text, page, heading, required in (
        ('a', 'Test one', 1, 'Test', ['c'*64]),
        ('c', 'Required exception', 2, 'Exception', []),
    ):
        chunks.append(dict(chunk_id=key*64, document_id='doc-test', version_id='ver-test1',
            edition_id='edition-test', byte_sha256='0'*64, chunk_type='policy',
            chunker_version='synthetic-source-aware-v1', text=text, source_text=text,
            content_hash=compute_content_hash(text, text), section_path=[],
            scope=['audience:undergraduate', 'program:TEST'],
            type_fields=dict(reading_id=key, applicability_basis_ref='synthetic-review',
                required_neighbor_chunk_ids=required,
                field_associations=[dict(name='printed_condition', value=text,
                    source_blank=False, event_sha256='2'*64, span_indexes=[0])]),
            spans=[dict(version_id='ver-test1', byte_sha256='0'*64, page=page,
                text=text, locator=dict(kind='section', section_path=[heading]))]))
    return chunks


class SourceAwareDatabaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = StorageDatabase()
        cls.addClassCleanup(cls.db.close)
        cls.chunks = synthetic_chunks()
        main, neighbor = cls.chunks
        cls.db.execute(FIXTURE + f"""
            update public.chunks set chunker_version={sql_literal(main['chunker_version'])},
              scope=array['audience:undergraduate','program:TEST'],
              type_fields={sql_literal(json.dumps(main['type_fields']))}::jsonb
              where chunk_id=repeat('a',64);
            insert into public.chunks(chunk_id,chunk_type,document_id,version_id,edition_id,
              byte_sha256,chunker_version,text,source_text,content_hash,scope,type_fields,
              source_verification,content_review)
            values (repeat('c',64),'policy','doc-test','ver-test1','edition-test',repeat('0',64),
              {sql_literal(neighbor['chunker_version'])},'Required exception','Required exception',
              {sql_literal(neighbor['content_hash'])},array['audience:undergraduate','program:TEST'],
              {sql_literal(json.dumps(neighbor['type_fields']))}::jsonb,'verified','reviewed');
            insert into public.source_spans(chunk_id,version_id,byte_sha256,text,page,locator)
            values (repeat('c',64),'ver-test1',repeat('0',64),'Required exception',2,
              '{{"kind":"section","section_path":["Exception"]}}'::jsonb);
            insert into public.chunk_embeddings(chunk_id,embedding_set_id,chunk_content_hash,embedding)
            values (repeat('c',64),'set-test',{sql_literal(neighbor['content_hash'])},
              ('[' || '0,1,' || repeat('0,',1021) || '0]')::extensions.vector);
            update public.embedding_sets set total_chunks=3 where embedding_set_id='set-test';
            commit;
        """)
        cls.manager = ReleaseManager(DatabaseStorageClient(cls.db))
        cls.manager.create_release('release-source-aware', 'source-aware-test', 'Synthetic only',
            'set-test', ['a'*64, 'c'*64], ['ver-test1'])
        cls.manager.activate_release('release-source-aware')

    def policy(self, chunks=None):
        chunks = self.chunks if chunks is None else chunks
        catalogue = prepare_candidate_subject_catalogue(chunks, [dict(reading_id=c['type_fields']['reading_id'],
            subject_id='synthetic_policy', basis_ref='synthetic-review') for c in chunks])
        visible = dict(subject_id='synthetic_policy', claim='printed condition', finding='visible_fields',
            reviewed_chunk_ids=['a'*64, 'c'*64],
            field_refs=[dict(reading_id=c['type_fields']['reading_id'], field_name='printed_condition')
                        for c in chunks], basis_ref='synthetic-source-review', basis_sha256='3'*64)
        absent = visible | dict(claim='unsupported claim', finding='not_stated_in_selected_fields', field_refs=[])
        reviews = prepare_candidate_claim_reviews(catalogue, chunks, [visible, absent])
        return SourceAwareEvidencePolicy(release_id='release-source-aware', embedding_set_id='set-test',
            chunks=chunks, catalogue=catalogue, claim_reviews=reviews)

    def engine(self, role, *, budget=2048, policy=None, encoder=None):
        return RetrievalEngine(DatabaseStorageClient(self.db, runtime_role=role), encoder or SyntheticEncoder(),
            RetrievalSettings(top_k=3, min_similarity=.25, context_budget=budget,
                policy_id='uncalibrated-document-development-v1'),
            evidence_policy=policy or self.policy())

    def request(self, *, release='release-source-aware', scope=('audience:undergraduate', 'program:TEST')):
        return RetrievalRequest('Synthetic policy question', release, scope)

    def retrieve(self, engine, request=None, claim='printed condition'):
        return engine.retrieve(request or self.request(), subject_id='synthetic_policy', requested_claims=(claim,))

    def assert_conservative(self, out):
        self.assertIs(out['candidate_only'], True)
        self.assertIs(out['activation_eligible'], False)
        self.assertIs(out['runtime_authorization_verified'], False)
        self.assertEqual(out['answer_sufficiency'], 'unassessed')

    def test_real_rows_bind_and_render_the_whole_required_group(self):
        for role in ('anon', 'authenticated'):
            with self.subTest(role=role):
                out = self.retrieve(self.engine(role))
                self.assertEqual(out['status'], 'uncalibrated', out)
                self.assertEqual(out['evidence_policy']['assessment']['status'], 'reviewed_fields_available')
                self.assertEqual({e['chunk_id'] for e in out['evidence']}, {'a'*64, 'c'*64})
                self.assertEqual({e['chunk_id'] for e in out['evidence'] if e['selection']=='primary'}, {'a'*64})
                self.assertIn('Test one', out['context'])
                self.assertIn('Required exception', out['context'])
                self.assertEqual(out['context_tokens'], len(out['context']))
                self.assertLessEqual(out['context_tokens'], 2048)
                for item in out['evidence']:
                    for citation in item['citations']:
                        self.assertEqual(citation['version_id'], 'ver-test1')
                        self.assertEqual(citation['byte_sha256'], '0'*64)
                        self.assertIn(citation['page'], (1, 2))
                        self.assertTrue(citation['locator'])
                self.assert_conservative(out)
                (self.db.evidence / f'source-aware-{role}.json').write_text(json.dumps(out, indent=2), encoding='utf-8')

    def test_related_context_does_not_establish_an_absent_claim(self):
        for role in ('anon', 'authenticated'):
            with self.subTest(role=role):
                out = self.retrieve(self.engine(role), claim='unsupported claim')
                self.assertEqual(out['status'], 'insufficient_evidence')
                self.assertEqual(out['gaps'], ['requested_claim_not_established'])
                self.assertTrue(out['evidence'])
                self.assertEqual(out['evidence_policy']['assessment']['claims'][0]['status'], 'not_established')
                self.assert_conservative(out)

    def test_scope_exclusion_and_tiny_budget_do_not_emit_partial_context(self):
        for role in ('anon', 'authenticated'):
            for budget, scope in ((1, ('audience:undergraduate', 'program:TEST')), (2048, ('program:OTHER',))):
                with self.subTest(role=role, budget=budget, scope=scope):
                    out = self.retrieve(self.engine(role, budget=budget), self.request(scope=scope))
                    self.assertEqual(out['status'], 'insufficient_evidence')
                    self.assertEqual(out['evidence'], [])
                    self.assertEqual(out['context'], '')
                    self.assert_conservative(out)

    def test_changed_snapshot_rejects_actual_transport_before_emission(self):
        chunks = copy.deepcopy(self.chunks)
        chunks[0]['spans'][0]['page'] = 99
        policy = self.policy(chunks)
        for role in ('anon', 'authenticated'):
            with self.subTest(role=role):
                out = self.retrieve(self.engine(role, policy=policy))
                self.assertEqual(out['status'], 'policy_binding_error')
                self.assertEqual(out['evidence'], [])
                self.assertIsNone(out['evidence_policy']['assessment'])
                self.assert_conservative(out)

    def test_stale_pin_stops_before_encoding_under_both_runtime_roles(self):
        self.manager.activate_release('release-test2')
        try:
            for role in ('anon', 'authenticated'):
                with self.subTest(role=role):
                    encoder = SyntheticEncoder()
                    out = self.retrieve(self.engine(role, encoder=encoder))
                    self.assertEqual(out['status'], 'release_changed')
                    self.assertEqual(encoder.calls, 0)
                    self.assertEqual(out['evidence'], [])
                    self.assertIsNone(out['evidence_policy']['assessment'])
                    self.assert_conservative(out)
        finally:
            self.manager.rollback_release('release-source-aware')

    def test_configuration_mismatch_stops_before_encoding(self):
        for role in ('anon', 'authenticated'):
            with self.subTest(role=role):
                encoder = SyntheticEncoder()
                encoder.config = replace(encoder.config, prompt_fingerprint='9'*64)
                out = self.retrieve(self.engine(role, encoder=encoder))
                self.assertEqual(out['status'], 'configuration_mismatch')
                self.assertEqual(encoder.calls, 0)
                self.assertEqual(out['evidence'], [])
                self.assertIsNone(out['evidence_policy']['assessment'])
                self.assert_conservative(out)
