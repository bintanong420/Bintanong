"""Pending source registration against actual disposable PostgreSQL roles."""
import copy
import json
from pathlib import Path
import unittest

from backend.bintanong_storage.source_registration import SourceRegistrationLoader
from backend.bintanong_storage.client import PermissionDeniedError, StorageError
from tests.storage_database import DatabaseStorageClient, StorageDatabase


def pending_version(suffix='one', document='doc-registration'):
    scope = dict(value=None, state='pending', evidence_ref=None, basis=None)
    state = dict(state='pending', evidence_ref=None)
    return dict(schema_version='bintanong-source-register-v1', namespace='institutional',
        synthetic=True, document_id=document, version_id='ver-registration-'+suffix,
        edition_id='edition-registration-'+suffix, filename=suffix+'.pdf',
        byte_sha256=('1' if suffix == 'one' else '2')*64,
        acquisition_locators=['synthetic:registration/'+suffix], document_category='source_document',
        **{k:copy.deepcopy(scope) for k in ('issuer','campus','college','program','cohort',
            'printed_revision','effective_from','effective_to')},
        supersession=dict(relation='none', target_version_id=None, state='pending',
            evidence_ref=None, basis=None), acquisition_state=copy.deepcopy(state),
        verification_state=copy.deepcopy(state), content_review_state=copy.deepcopy(state),
        approval_state=dict(state='not_requested', evidence_ref=None), approval_id=None, evidence=[])


def document_record(document='doc-registration'):
    return dict(document_id=document, namespace='institutional', synthetic=True,
        document_category='academic_handbook', title='Synthetic undergraduate handbook')


class TestSourceRegistration(unittest.TestCase):
    def setUp(self):
        self.db = StorageDatabase()
        self.addCleanup(self.db.close)
        self.client = DatabaseStorageClient(self.db)
        self.loader = SourceRegistrationLoader(self.client)
        self.version = pending_version()
        self.document = document_record()

    def register(self, versions=None, documents=None):
        return self.loader.load_versions(versions if versions is not None else [self.version],
            documents if documents is not None else [self.document])

    def test_register_retains_full_payload_and_initial_states(self):
        untouched = copy.deepcopy(self.version)
        self.register()
        row = self.client.select('document_versions', role='admin')[0]
        self.assertEqual(row['source_register'], untouched)
        self.assertEqual(self.version, untouched)
        self.assertEqual((row['acquisition_state'],row['verification_state'],
            row['approval_state'],row['content_review_state']),
            ('pending','pending','not_requested','pending'))
        self.assertEqual(row['issuer'], untouched['issuer'])
        self.assertEqual(row['acquisition_locators'], ['synthetic:registration/one'])
        self.assertEqual(self.client.select('documents', role='admin')[0]['document_category'],
            'academic_handbook')

    def test_exact_reimports_preserve_rows_and_multiple_versions_share_document(self):
        self.register([self.version, pending_version('two')])
        before = self.client.select('document_versions', role='admin')
        self.register([pending_version('two'), self.version])
        self.assertEqual(self.client.select('document_versions', role='admin'), before)
        self.assertEqual(len(self.client.select('documents', role='admin')), 1)

    def test_changed_version_fails_atomically_without_new_document_or_overwrite(self):
        self.register()
        changed = dict(self.version, filename='changed.pdf')
        new = pending_version('new', 'doc-new-registration')
        with self.assertRaisesRegex(StorageError, 'identity conflicts'):
            self.register([new, changed], [document_record('doc-new-registration'),self.document])
        self.assertEqual(len(self.client.select('documents', role='admin')), 1)
        self.assertEqual(self.client.select('document_versions', role='admin')[0]['filename'], 'one.pdf')

    def test_changed_document_metadata_is_rejected(self):
        self.register()
        with self.assertRaisesRegex(StorageError, 'identity conflicts'):
            self.register(documents=[dict(self.document,title='Different title')])
        self.assertEqual(self.client.select('documents', role='admin')[0]['title'], self.document['title'])

    def test_invalid_batches_are_rejected_without_writes(self):
        batches = [([],[]), ([self.version,self.version],[self.document]),
            ([self.version],[self.document,self.document]), ([self.version],[]),
            ([self.version],[document_record('doc-unrelated')]),
            ([self.version],[dict(self.document,document_category='source_document')]),
            ([self.version],[dict(self.document,namespace='private')]),
            ([self.version],[dict(self.document,synthetic=False)]),
            ([dict(self.version,byte_sha256='invalid')],[self.document]),
            ([dict(self.version,filename='../private.pdf')],[self.document])]
        for versions, documents in batches:
            with self.subTest(batch=(versions,documents)), self.assertRaises(ValueError):
                self.register(versions,documents)
        self.assertEqual(self.client.select('documents', role='admin'), [])

    def test_initial_registration_cannot_promote_governance(self):
        for name,value in [('verification_state','verified'),('acquisition_state','observed'),
                ('approval_state','approved'),('content_review_state','reviewed')]:
            bad = copy.deepcopy(self.version)
            bad[name]['state'] = value
            with self.subTest(field=name), self.assertRaises(ValueError):
                self.register([bad])
        self.assertEqual(self.client.select('document_versions', role='admin'), [])

    def test_valid_acquired_contract_requires_a_separate_transition_workflow(self):
        from backend.bintanong_contracts.governance import SourceDocumentVersion
        path = Path(__file__).resolve().parents[1]/'knowledge/manifests/examples/synthetic-register.json'
        acquired = json.loads(path.read_text(encoding='utf-8'))[0]
        SourceDocumentVersion.parse(acquired)
        with self.assertRaisesRegex(ValueError, 'initial pending'):
            self.register([acquired], [document_record(acquired['document_id'])])
        self.assertEqual(self.client.select('documents', role='admin'), [])

    def test_direct_rpc_rejects_promotion_and_rolls_back_documents(self):
        bad = copy.deepcopy(self.version)
        bad['verification_state']['state'] = 'verified'
        with self.assertRaisesRegex(StorageError, 'initial pending'):
            self.client.rpc('register_pending_sources',dict(p_documents=[self.document],
                p_versions=[bad]),role='admin')
        self.assertEqual(self.client.select('documents', role='admin'), [])

    def test_direct_rpc_checks_parent_metadata_and_duplicate_versions(self):
        for versions,documents in [([self.version,self.version],[self.document]),
                ([self.version],[dict(self.document,synthetic=False)]),
                ([self.version],[self.document,document_record('doc-extra')])]:
            with self.subTest(versions=versions,documents=documents), self.assertRaises(StorageError):
                self.client.rpc('register_pending_sources',dict(p_documents=documents,
                    p_versions=versions),role='admin')
        self.assertEqual(self.client.select('documents',role='admin'),[])

    def test_runtime_roles_cannot_register_or_see_pending_sources(self):
        self.register()
        with self.assertRaises(PermissionDeniedError):
            self.client.rpc('register_pending_sources',dict(p_documents=[self.document],
                p_versions=[self.version]),role='runtime')
        for role in ('anon','authenticated'):
            with self.subTest(role=role):
                rows = self.db.json(f"begin; set local role {role}; select coalesce(jsonb_agg(to_jsonb(v)), '[]') from public.document_versions v; commit;")
                self.assertEqual(rows, [])
                allowed = self.db.json(f"select to_jsonb(has_function_privilege('{role}','public.register_pending_sources(jsonb,jsonb)','EXECUTE'));")
                self.assertFalse(allowed)

