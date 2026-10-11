from __future__ import annotations

import unittest
from backend.bintanong_storage.client import (
    SupabaseStorageClient,
    PermissionDeniedError,
)
from backend.bintanong_storage.loader import BatchKnowledgeLoader
from backend.bintanong_storage.release import ReleaseManager


class TestStorageReleaseIsolation(unittest.TestCase):
    def setUp(self):
        self.client = SupabaseStorageClient()
        self.loader = BatchKnowledgeLoader(self.client)
        self.release_mgr = ReleaseManager(self.client)

        self.emb_set_id = "4" * 64
        self.loader.load_embedding_manifest({
            "schema_version": "bintanong-embedding-manifest-v1",
            "model_id": "test-model",
            "model_revision": "df5b1c55623eeb5ef09ce3f3c50e24e2db433d7d1bbcccf76d2f01ba212df5f1",
            "dimension": 1024,
            "normalization": "l2",
            "prompt_fingerprint": self.emb_set_id,
            "preprocessing_fingerprint": "5" * 64,
            "tokenizer_fingerprint": "6" * 64,
        })

        self.chunk_r1_id = "1" * 64
        self.chunk_r2_id = "2" * 64

        self.loader.load_chunks([
            {
                "chunk_id": self.chunk_r1_id,
                "chunk_type": "policy",
                "text": "Chunk exclusive to Release 1",
                "content_hash": "a" * 64,
                "byte_sha256": "0" * 64,
            },
            {
                "chunk_id": self.chunk_r2_id,
                "chunk_type": "policy",
                "text": "Chunk exclusive to Release 2",
                "content_hash": "b" * 64,
                "byte_sha256": "0" * 64,
            },
        ])

        self.rel_1_id = "rel-test-001"
        self.rel_2_id = "rel-test-002"

        # Ensure cleanup of any leftover active release or test releases
        self._cleanup()

        # Create Release 1 (draft) containing chunk 1
        self.release_mgr.create_release(
            release_id=self.rel_1_id,
            release_version="v1.0.0",
            description="First test release",
            embedding_set_id=self.emb_set_id,
            chunk_ids=[self.chunk_r1_id],
        )

        # Create Release 2 (draft) containing chunk 2
        self.release_mgr.create_release(
            release_id=self.rel_2_id,
            release_version="v2.0.0",
            description="Second test release",
            embedding_set_id=self.emb_set_id,
            chunk_ids=[self.chunk_r2_id],
        )

    def tearDown(self):
        self._cleanup()
        self.client.delete("chunks", {"chunk_id": f"in.({self.chunk_r1_id},{self.chunk_r2_id})"}, role="admin")
        self.client.delete("embedding_sets", {"embedding_set_id": f"eq.{self.emb_set_id}"}, role="admin")
        self.client.close()

    def _cleanup(self):
        self.client.delete("active_release", {"id": "eq.1"}, role="admin")
        self.client.delete("release_chunks", {"release_id": f"in.({self.rel_1_id},{self.rel_2_id})"}, role="admin")
        self.client.delete("knowledge_releases", {"release_id": f"in.({self.rel_1_id},{self.rel_2_id})"}, role="admin")

    def test_release_isolation_and_atomic_transition(self):
        """Exit gate: staged or superseded chunks cannot leak into current retrieval."""
        # 1. While both releases are in DRAFT status:
        # Runtime (anon) querying chunks should see 0 chunks!
        runtime_chunks_draft = self.client.select("chunks", role="runtime")
        self.assertEqual(len(runtime_chunks_draft), 0, "Draft chunks must not be visible to runtime queries")

        # 2. Activate Release 1
        self.release_mgr.activate_release(self.rel_1_id, actor="admin-tester")

        # Now runtime querying chunks must see ONLY chunk 1, NOT chunk 2
        runtime_chunks_r1 = self.client.select("chunks", role="runtime")
        self.assertEqual(len(runtime_chunks_r1), 1)
        self.assertEqual(runtime_chunks_r1[0]["chunk_id"], self.chunk_r1_id)

        # Verify active_release singleton
        active = self.release_mgr.get_active_release()
        self.assertIsNotNone(active)
        self.assertEqual(active["release_id"], self.rel_1_id)
        self.assertEqual(active["status"], "active")

        # 3. Activate Release 2
        self.release_mgr.activate_release(self.rel_2_id, actor="admin-tester")

        # Release 1 is now superseded; Release 2 is active.
        # Runtime querying chunks must see ONLY chunk 2, and chunk 1 must NOT leak!
        runtime_chunks_r2 = self.client.select("chunks", role="runtime")
        self.assertEqual(len(runtime_chunks_r2), 1)
        self.assertEqual(runtime_chunks_r2[0]["chunk_id"], self.chunk_r2_id)

        # 4. Rollback to Release 1
        self.release_mgr.rollback_release(self.rel_1_id, actor="admin-tester")

        # Runtime querying chunks must now see chunk 1 again, and chunk 2 must be hidden!
        runtime_chunks_rolled_back = self.client.select("chunks", role="runtime")
        self.assertEqual(len(runtime_chunks_rolled_back), 1)
        self.assertEqual(runtime_chunks_rolled_back[0]["chunk_id"], self.chunk_r1_id)

    def test_runtime_cannot_activate_or_rollback_releases(self):
        """Exit gate: runtime role cannot execute release mutation procedures."""
        with self.assertRaises(PermissionDeniedError):
            self.client.rpc("activate_knowledge_release", {"p_release_id": self.rel_1_id}, role="runtime")

        with self.assertRaises(PermissionDeniedError):
            self.client.rpc("rollback_knowledge_release", {"p_target_release_id": self.rel_1_id}, role="runtime")


if __name__ == "__main__":
    unittest.main()
