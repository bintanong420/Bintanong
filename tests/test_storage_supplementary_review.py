"""Synthetic supplementary-review client boundary, using the real C1 validator."""
import copy
import importlib
import importlib.util
import unittest

from tests.test_storage_selected_release_review import selected_fixture, RecordingClient
from tests.test_storage_source_verification import acquired_source, observation_for, observed_record
from tests.test_storage_supplementary_review_database import supplement_fixture


class SupplementaryReviewLoaderTests(unittest.TestCase):
    def setUp(self):
        current = acquired_source()
        self.current = observed_record(current, observation_for(current))
        _, partial, _, _ = selected_fixture()
        self.parent = partial['evidence']['evidence_id']
        self.receipt, _ = supplement_fixture(partial)
        self.client = RecordingClient()

    def loader(self):
        module = 'backend.bintanong_storage.source_supplementary_review'
        self.assertIsNotNone(importlib.util.find_spec(module), 'Supplementary review loader missing')
        return importlib.import_module(module).SourceSupplementaryReviewLoader(self.client)

    def test_append_uses_admin_receipt_rpc_and_preserves_source_state(self):
        current, receipt = copy.deepcopy((self.current, self.receipt))
        out = self.loader().record(self.current, self.receipt, base_evidence_id=self.parent)
        self.assertEqual(out, receipt)
        self.assertEqual(self.client.calls, [('record_source_supplementary_review', dict(
            p_expected_register=current, p_receipt=receipt, p_base_evidence_id=self.parent), 'admin')])
        self.assertEqual(self.current, current)
        self.assertEqual(self.receipt, receipt)
        out['evidence']['evidence_id'] = 'caller mutation'
        self.assertEqual(self.receipt, receipt)

    def test_invalid_source_receipt_and_parent_stop_before_transport(self):
        for mutation in ('initial-state', 'source-hash', 'blank-parent', 'same-parent', 'nan'):
            current, receipt = copy.deepcopy((self.current, self.receipt))
            parent = self.parent
            if mutation == 'initial-state':
                current['content_review_state'] = dict(state='pending', evidence_ref=None)
            elif mutation == 'source-hash': receipt['source_sha256'] = '0'*64
            elif mutation == 'blank-parent': parent = ' '
            elif mutation == 'same-parent': parent = receipt['evidence']['evidence_id']
            else: receipt['chunks'][-1]['type_fields']['field_associations'][0]['value'] = float('nan')
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.loader().record(current, receipt, base_evidence_id=parent)
        self.assertEqual(self.client.calls, [])

    def test_transport_cannot_substitute_a_different_receipt(self):
        self.client.response = copy.deepcopy(self.receipt)
        self.client.response['evidence']['evidence_id'] = 'wrong receipt'
        with self.assertRaisesRegex(ValueError, 'differs'):
            self.loader().record(self.current, self.receipt, base_evidence_id=self.parent)
