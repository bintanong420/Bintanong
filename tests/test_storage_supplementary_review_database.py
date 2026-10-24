"""Append selected-field evidence without rewriting a published source; synthetic only."""
import copy
import json
import unittest

from backend.bintanong_contracts.reviewed_policy_context import serialize_reviewed_fields
from backend.bintanong_contracts.source import compute_content_hash
from backend.bintanong_storage.client import PermissionDeniedError, StorageError
from backend.bintanong_storage.loader import BatchKnowledgeLoader
from tests.storage_database import DatabaseStorageClient, sql_literal
from tests import test_storage_source_verification_database as source_verification_database


def supplement_fixture(partial):
    receipt = copy.deepcopy(partial)
    receipt['evidence'].update(evidence_id='synthetic-supplement', recorded_at='2026-10-17T10:00:00Z')
    event = copy.deepcopy(receipt['source_events'][0])
    event.update(event_sha256='6'*64, owner_event_sha256='5'*64, recorded_at='2026-10-17T09:00:00Z')
    receipt['source_events'].append(event)
    chunk = copy.deepcopy(receipt['chunks'][0])
    chunk['chunk_id'] = 'b'*64
    chunk['spans'][0].update(chunk_id='b'*64, page=2, text='Another synthetic condition')
    fields = chunk['type_fields']
    fields['reading_id'] = 'synthetic-additional-reading'
    fields['field_associations'][0].update(name='second_condition', value='Another synthetic condition',
                                         event_sha256=event['event_sha256'])
    text = serialize_reviewed_fields(fields['field_associations'], fields['source_limits'])
    chunk['content_hash'] = compute_content_hash(chunk['spans'][0]['text'], text)
    receipt['chunks'].append(chunk)
    return receipt, text


class SupplementaryReviewDatabaseTests(unittest.TestCase):
    def setUp(self):
        source_verification_database.SourceVerificationDatabaseTests.setUp(self)
        self.current = self.observer.observe(self.current, self.observation).model_dump(mode='json')
        self.db.execute("update public.chunks set source_verification='observed';")
        self.manager.designate_research_release('release-selected', 'research-owner-20261021')
        self.manager.activate_release('release-selected')
        self.supplement, _ = supplement_fixture(self.partial)
        self.load_snapshot(self.supplement['chunks'][-1])

    def load_snapshot(self, snap):
        text = serialize_reviewed_fields(snap['type_fields']['field_associations'],
                                        snap['type_fields']['source_limits'])
        record = copy.deepcopy(self.chunk)
        record.update(chunk_id=snap['chunk_id'], spans=snap['spans'], type_fields=snap['type_fields'],
            text=text, source_text=snap['spans'][0]['text'], content_hash=snap['content_hash'],
            source_verification='observed', content_review='partially_reviewed')
        BatchKnowledgeLoader(self.client).load_chunks([record])

    def record(self, receipt=None, parent=None, current=None, client=None):
        return (client or self.client).rpc('record_source_supplementary_review', dict(
            p_expected_register=self.current if current is None else current,
            p_receipt=self.supplement if receipt is None else receipt,
            p_base_evidence_id=parent or self.partial['evidence']['evidence_id']), role='admin')

    def protected_snapshot(self):
        return {table:self.client.select(table, role='admin') for table in
                ('document_versions', 'knowledge_releases', 'release_document_versions',
                 'release_chunks', 'selected_release_reviews', 'active_release', 'chunks', 'source_spans')}

    def test_published_source_accepts_cumulative_receipt_without_mutating_existing_evidence(self):
        before = self.protected_snapshot()
        original = self.client.select('source_partial_reviews', role='admin')
        self.assertEqual(self.record(), self.supplement)
        self.assertEqual(self.record(), self.supplement)  # Exact retry is harmless.
        changed = copy.deepcopy(self.supplement)
        changed['compiler_label'] = 'Different synthetic compiler'
        with self.assertRaisesRegex(StorageError, 'replay conflict'):
            self.record(changed)
        self.assertEqual(self.protected_snapshot(), before)
        saved = self.client.select('source_partial_reviews', role='admin')
        self.assertEqual(len(saved), len(original)+1)
        self.assertTrue(all(row in saved for row in original))
        links = self.client.select('source_review_supplements', role='admin')
        self.assertEqual(len(links), 1)
        self.assertEqual((links[0]['version_id'], links[0]['evidence_id'], links[0]['base_evidence_id']),
            (self.current['version_id'], 'synthetic-supplement', self.partial['evidence']['evidence_id']))

    def test_wrong_parent_or_changed_source_snapshot_cannot_append_evidence(self):
        for mutation in ('parent', 'hash', 'old-field', 'new-span', 'old-event', 'missing-old', 'source'):
            receipt = copy.deepcopy(self.supplement)
            current = copy.deepcopy(self.current)
            parent = None
            if mutation == 'parent': parent = 'not-a-receipt'
            elif mutation == 'hash': receipt['source_sha256'] = '0'*64
            elif mutation == 'old-field': receipt['chunks'][0]['type_fields']['field_associations'][0]['value'] = 'Changed'
            elif mutation == 'new-span': receipt['chunks'][-1]['spans'][0]['page'] = 99
            elif mutation == 'old-event': receipt['source_events'][0]['actual_owner_label'] = 'Changed'
            elif mutation == 'missing-old': receipt['chunks'] = receipt['chunks'][1:]
            else: current['filename'] = 'different.pdf'
            with self.subTest(mutation=mutation), self.assertRaises(StorageError):
                self.record(receipt, parent, current)
        self.assertEqual(len(self.client.select('source_partial_reviews', role='admin')), 1)
        self.assertEqual(self.client.select('source_review_supplements', role='admin'), [])

    def test_runtime_roles_cannot_record_or_read_supplementary_evidence(self):
        self.record()
        for role in ('anon', 'authenticated'):
            runtime = DatabaseStorageClient(self.db, runtime_role=role)
            with self.subTest(role=role), self.assertRaises(PermissionDeniedError):
                runtime.rpc('record_source_supplementary_review', dict(p_expected_register=self.current,
                    p_receipt=self.supplement, p_base_evidence_id=self.partial['evidence']['evidence_id']))
            with self.subTest(role=role), self.assertRaisesRegex(AssertionError, 'permission denied'):
                runtime.select('source_review_supplements')

    def test_second_supplement_preserves_first_and_binds_through_its_parent(self):
        self.record()
        second = copy.deepcopy(self.supplement)
        second['evidence'].update(evidence_id='synthetic-supplement-two', recorded_at='2026-10-18T10:00:00Z')
        event = copy.deepcopy(second['source_events'][-1])
        event.update(event_sha256='4'*64, owner_event_sha256='3'*64, recorded_at='2026-10-18T09:00:00Z')
        second['source_events'].append(event)
        third = copy.deepcopy(second['chunks'][-1])
        third['chunk_id'] = 'c'*64
        third['spans'][0].update(chunk_id='c'*64, page=3, text='Third synthetic condition')
        fields = third['type_fields']
        fields['reading_id'] = 'third-synthetic-reading'
        fields['field_associations'][0].update(value='Third synthetic condition', event_sha256='4'*64)
        third['content_hash'] = compute_content_hash(third['spans'][0]['text'],
            serialize_reviewed_fields(fields['field_associations'], fields['source_limits']))
        second['chunks'].append(third)
        self.load_snapshot(third)
        before = self.protected_snapshot()
        self.assertEqual(self.record(second, 'synthetic-supplement'), second)
        self.assertEqual(self.protected_snapshot(), before)
        self.assertEqual(len(self.client.select('source_review_supplements', role='admin')), 2)

    def test_new_rows_cannot_replace_parent_rows_even_when_event_and_count_checks_pass(self):
        replacement = copy.deepcopy(self.supplement['chunks'][0])
        replacement['chunk_id'] = 'c'*64
        replacement['spans'][0].update(chunk_id='c'*64, page=3, text='Substitute synthetic condition')
        fields = replacement['type_fields']
        fields['reading_id'] = 'substitute-synthetic-reading'
        fields['field_associations'][0]['value'] = 'Substitute synthetic condition'
        replacement['content_hash'] = compute_content_hash(replacement['spans'][0]['text'],
            serialize_reviewed_fields(fields['field_associations'], fields['source_limits']))
        self.load_snapshot(replacement)
        changed = copy.deepcopy(self.supplement)
        changed['chunks'][0] = replacement
        with self.assertRaisesRegex(StorageError, 'retained exactly'):
            self.record(changed)

    def test_unbound_receipt_cannot_become_a_trusted_parent(self):
        unbound = copy.deepcopy(self.partial)
        unbound['evidence']['evidence_id'] = 'unbound-parent'
        self.db.execute('begin; set local role service_role; '
            'insert into public.source_partial_reviews(version_id,evidence_id,receipt) values ('+
            ','.join((sql_literal(self.current['version_id']), "'unbound-parent'",
                      sql_literal(json.dumps(unbound))+'::jsonb'))+'); commit;')
        with self.assertRaisesRegex(StorageError, 'Source-bound cumulative parent'):
            self.record(parent='unbound-parent')

    def test_supplementary_receipts_and_parent_links_are_immutable(self):
        self.record()
        for sql in (
            "update public.source_review_supplements set base_evidence_id='changed';",
            'delete from public.source_review_supplements;',
            'truncate public.source_review_supplements;',
            "update public.source_partial_reviews set receipt='{}'::jsonb where evidence_id='synthetic-supplement';",
        ):
            with self.subTest(sql=sql), self.assertRaises(AssertionError):
                self.db.execute(sql)

    def test_direct_service_role_inserts_cannot_bypass_cumulative_history(self):
        forged = copy.deepcopy(self.supplement)
        forged['chunks'] = forged['chunks'][1:]  # Omit the parent's reviewed row.
        forged['source_events'] = forged['source_events'][1:]
        self.db.execute('begin; set local role service_role; '
            'insert into public.source_partial_reviews(version_id,evidence_id,receipt) values ('+
            ','.join((sql_literal(self.current['version_id']), "'synthetic-supplement'",
                      sql_literal(json.dumps(forged))+'::jsonb'))+'); commit;')
        with self.assertRaisesRegex(AssertionError, 'cumulative|retained'):
            self.db.execute('begin; set local role service_role; '
                'insert into public.source_review_supplements(version_id,evidence_id,base_evidence_id) values ('+
                ','.join((sql_literal(self.current['version_id']), "'synthetic-supplement'",
                          sql_literal(self.partial['evidence']['evidence_id'])))+'); commit;')
        self.assertEqual(self.client.select('source_review_supplements', role='admin'), [])

    def test_new_selected_release_uses_supplement_and_old_release_can_be_restored(self):
        self.record()
        source_before = self.client.select('document_versions', role='admin')
        self.db.execute("""
            insert into public.embedding_sets select (jsonb_populate_record(null::public.embedding_sets,
                to_jsonb(e) || '{"embedding_set_id":"set-supplement","total_chunks":2}'::jsonb)).*
                from public.embedding_sets e where embedding_set_id='set-selected';
            insert into public.chunk_embeddings(chunk_id,embedding_set_id,chunk_content_hash,embedding)
                select chunk_id,'set-supplement',content_hash,
                    ('[' || '1,' || repeat('0,',1022) || '0]')::extensions.vector from public.chunks;
        """)
        selected = copy.deepcopy(self.receipt)
        selected.update(review_scope_id='c'*64, chunks=copy.deepcopy(self.supplement['chunks']))
        selected['sources'][0]['partial_review_evidence_id'] = 'synthetic-supplement'
        selected['decision'].update(evidence_id='synthetic-selected-supplement', recorded_at='2026-10-18T10:00:00Z')
        self.assertEqual(self.loader.record(selected), selected)
        self.manager.create_release('release-supplement', 'supplement', 'Synthetic expanded review',
            'set-supplement', ['a'*64, 'b'*64], [self.current['version_id']])
        self.loader.bind_release('release-supplement', 'c'*64)
        self.manager.designate_research_release('release-supplement', 'research-owner-20261021')
        self.manager.activate_release('release-supplement')
        runtime = DatabaseStorageClient(self.db)
        self.assertEqual(sorted(c['chunk_id'] for c in runtime.select('chunks')), ['a'*64, 'b'*64])
        self.assertEqual(self.client.select('document_versions', role='admin'), source_before)
        self.manager.rollback_release('release-selected')
        self.assertEqual([c['chunk_id'] for c in runtime.select('chunks')], ['a'*64])
        self.assertEqual(self.client.select('document_versions', role='admin'), source_before)
