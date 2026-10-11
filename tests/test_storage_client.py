from __future__ import annotations

import unittest
from backend.bintanong_storage.client import (
    SupabaseStorageClient,
    PermissionDeniedError,
)
from backend.bintanong_storage.config import StorageConfig


class TestSupabaseStorageClient(unittest.TestCase):
    def setUp(self):
        self.config = StorageConfig.from_env()
        self.client = SupabaseStorageClient(self.config)

    def tearDown(self):
        self.client.close()

    def test_client_select_public_table_runtime(self):
        """Runtime (anon) can select public table (active_release)."""
        res = self.client.select("active_release", role="runtime")
        self.assertIsInstance(res, list)

    def test_client_mutation_denied_for_runtime(self):
        """Runtime (anon) cannot insert into documents due to RLS."""
        with self.assertRaises(PermissionDeniedError):
            self.client.insert(
                "documents",
                {
                    "document_id": "doc-unauthorized-test",
                    "title": "Unauthorized Test",
                    "document_category": "curriculum_prospectus",
                },
                role="runtime",
            )

    def test_client_admin_can_insert_and_delete(self):
        """Admin (service_role) can insert and delete institutional documents."""
        doc_id = "doc-admin-test-01"
        try:
            self.client.delete("documents", {"document_id": f"eq.{doc_id}"}, role="admin")
            self.client.insert(
                "documents",
                {
                    "document_id": doc_id,
                    "title": "Admin Insertion Test",
                    "document_category": "academic_handbook",
                },
                role="admin",
            )
            rows = self.client.select("documents", filters={"document_id": f"eq.{doc_id}"}, role="admin")
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["title"], "Admin Insertion Test")
        finally:
            self.client.delete("documents", {"document_id": f"eq.{doc_id}"}, role="admin")


if __name__ == "__main__":
    unittest.main()
