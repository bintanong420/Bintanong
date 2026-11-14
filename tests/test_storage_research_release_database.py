"""Disposable actual-role tests of owner-authorized research releases (22 October 2026).

A research release is a selected-review release carrying the owner's research authorization.
Sources keep their true states (approval not requested); institutional rules are unchanged.
"""
import unittest

from backend.bintanong_storage.client import StorageError, PermissionDeniedError
from backend.bintanong_storage.loader import CONFIG_FIELDS
from tests.storage_database import DatabaseStorageClient
from tests.test_storage_selected_review_database import SelectedReviewDatabaseTests

REF = 'research-owner-20261021'
EXCLUDED = """insert into public.chunks(chunk_id,chunk_type,document_id,version_id,edition_id,
    byte_sha256,text,content_hash,scope) select repeat('b',64),chunk_type,document_id,version_id,edition_id,
    byte_sha256,'Excluded staff procedure',bintanong_private.content_hash(null,'Excluded staff procedure'),
    array['audience:staff'] from public.chunks limit 1;"""


class ResearchReleaseDatabaseTests(unittest.TestCase):
    prepare = SelectedReviewDatabaseTests.prepare
    record = SelectedReviewDatabaseTests.record
    bind = SelectedReviewDatabaseTests.bind

    def setUp(self):
        self.prepare()

    def observed(self):
        # The real research-time state: bytes verified, printed spans observed (V1), never approved.
        self.db.execute("update public.document_versions set acquisition_state='verified',verification_state='observed';"
                        "update public.chunks set source_verification='observed';")

    def designate(self, ref=REF):
        return self.manager.designate_research_release('release-selected', ref)

    def ready(self):
        self.record(); self.bind(); self.observed(); self.designate()

    def runtime(self, role='anon'):
        return DatabaseStorageClient(self.db, runtime_role=role)

    def test_research_release_activates_and_runtime_reads_only_its_rows(self):
        self.ready()
        self.db.execute(EXCLUDED)
        self.manager.activate_release('release-selected')
        source = self.client.select('document_versions', role='admin')[0]
        self.assertEqual((source['approval_state'], source['verification_state']), ('not_requested', 'observed'))
        for role in ('anon', 'authenticated'):
            runtime = self.runtime(role)
            self.assertEqual([c['chunk_id'] for c in runtime.select('chunks')], ['a' * 64])
            self.assertEqual(len(runtime.select('document_versions')), 1)
            self.assertEqual(len(runtime.select('source_spans')), 1)
            release = runtime.select('knowledge_releases')[0]
            self.assertEqual((release['release_kind'], release['research_authorization_ref']), ('research', REF))
            configuration = self.client.select('embedding_sets', role='admin')[0]
            response = runtime.rpc('retrieve_context', dict(query_embedding=[1.0] + [0.0] * 1023,
                p_release_id='release-selected', p_config={k: configuration[k] for k in CONFIG_FIELDS},
                p_top_k=3, p_min_similarity=.25, p_scope=['audience:undergraduate'],
                p_entity_hints=[], p_version_ids=[]))
            self.assertEqual(response['status'], 'ok')
            self.assertEqual([item['chunk']['chunk_id'] for item in response['items']], ['a' * 64])

    def test_institutional_release_still_refuses_unapproved_sources(self):
        self.record(); self.bind(); self.observed()
        with self.assertRaises(StorageError):
            self.manager.activate_release('release-selected')
        self.assertEqual(self.client.select('active_release', role='admin'), [])

    def test_research_release_still_needs_observed_sources_and_chunks(self):
        self.ready()
        for sql in ("update public.document_versions set verification_state='pending';",
                    "update public.chunks set source_verification='pending';"):
            with self.subTest(sql=sql):
                self.db.execute(sql)
                with self.assertRaises(StorageError):
                    self.manager.activate_release('release-selected')
                self.observed()

    def test_designation_requires_a_bound_selected_review(self):
        self.record(); self.observed()
        with self.assertRaises(StorageError):
            self.designate()

    def test_designation_requires_an_owner_research_reference(self):
        self.record(); self.bind(); self.observed()
        for ref in ('', 'owner', 'research-owner-2026', 'research-owner-20261021 ', 'approved'):
            with self.subTest(ref=ref), self.assertRaises(StorageError):
                self.designate(ref)
        release = self.client.select('knowledge_releases', role='admin')[0]
        self.assertEqual((release['release_kind'], release['research_authorization_ref']), ('institutional', None))

    def test_designation_is_fixed_once_published(self):
        self.ready()
        self.manager.activate_release('release-selected')
        with self.assertRaises(StorageError):
            self.designate('research-owner-20261022')
        for sql in ("update public.knowledge_releases set release_kind='institutional',research_authorization_ref=null;",
                    "update public.knowledge_releases set research_authorization_ref='research-owner-20261022';"):
            with self.subTest(sql=sql), self.assertRaises(AssertionError):
                self.db.execute(sql)

    def test_kind_and_reference_must_agree(self):
        for sql in ("update public.knowledge_releases set research_authorization_ref='research-owner-20261021';",
                    "update public.knowledge_releases set release_kind='research';"):
            with self.subTest(sql=sql), self.assertRaises(AssertionError):
                self.db.execute(sql)

    def test_runtime_roles_cannot_designate(self):
        self.record(); self.bind()
        for role in ('anon', 'authenticated'):
            with self.subTest(role=role), self.assertRaises(PermissionDeniedError):
                self.runtime(role).rpc('designate_research_release',
                    dict(p_release_id='release-selected', p_authorization_ref=REF))


if __name__ == '__main__':
    unittest.main()
