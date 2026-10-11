from __future__ import annotations

import unittest
from backend.bintanong_storage.client import SupabaseStorageClient
from backend.bintanong_storage.loader import BatchKnowledgeLoader
from backend.bintanong_storage.release import ReleaseManager
from backend.bintanong_storage.retrieval import KnowledgeRetriever


class TestStorageVectorRetrieval(unittest.TestCase):
    def setUp(self):
        self.client = SupabaseStorageClient()
        self.loader = BatchKnowledgeLoader(self.client)
        self.release_mgr = ReleaseManager(self.client)
        self.retriever = KnowledgeRetriever(self.client)

        self.emb_set_id = "7" * 64
        self.loader.load_embedding_manifest({
            "schema_version": "bintanong-embedding-manifest-v1",
            "model_id": "aisingapore/SEA-LION-E5-Embedding-600M",
            "model_revision": "df5b1c55623eeb5ef09ce3f3c50e24e2db433d7d1bbcccf76d2f01ba212df5f1",
            "dimension": 1024,
            "normalization": "l2",
            "prompt_fingerprint": self.emb_set_id,
            "preprocessing_fingerprint": "8" * 64,
            "tokenizer_fingerprint": "9" * 64,
        })

        self.target_chunk_id = "3" * 64
        self.distractor_chunk_id = "4" * 64
        self.unreleased_chunk_id = "5" * 64

        self.loader.load_chunks([
            {
                "chunk_id": self.target_chunk_id,
                "chunk_type": "policy",
                "text": "PalSU Computer Science Degree Graduation Requirements.",
                "content_hash": "a" * 64,
                "byte_sha256": "0" * 64,
                "section_path": ["Academics", "Graduation"],
            },
            {
                "chunk_id": self.distractor_chunk_id,
                "chunk_type": "policy",
                "text": "Campus Parking Regulations and Vehicle Permits.",
                "content_hash": "b" * 64,
                "byte_sha256": "0" * 64,
                "section_path": ["General", "Parking"],
            },
            {
                "chunk_id": self.unreleased_chunk_id,
                "chunk_type": "policy",
                "text": "Draft unreleased curriculum changes.",
                "content_hash": "c" * 64,
                "byte_sha256": "0" * 64,
                "section_path": ["Draft"],
            },
        ])

        # Unit vectors:
        # target_vec has 1.0 at index 0
        target_vec = [0.0] * 1024
        target_vec[0] = 1.0

        # distractor_vec has 1.0 at index 1 (orthogonal to target)
        distractor_vec = [0.0] * 1024
        distractor_vec[1] = 1.0

        # unreleased_vec has 1.0 at index 0 (identical direction as target)
        unreleased_vec = [0.0] * 1024
        unreleased_vec[0] = 1.0

        self.loader.load_embeddings([
            {"chunk_id": self.target_chunk_id, "chunk_content_hash": "a" * 64, "vector": target_vec},
            {"chunk_id": self.distractor_chunk_id, "chunk_content_hash": "b" * 64, "vector": distractor_vec},
            {"chunk_id": self.unreleased_chunk_id, "chunk_content_hash": "c" * 64, "vector": unreleased_vec},
        ], embedding_set_id=self.emb_set_id)

        self.rel_id = "rel-search-001"
        self._cleanup()

        # Release contains ONLY target and distractor chunks (unreleased chunk is omitted)
        self.release_mgr.create_release(
            release_id=self.rel_id,
            release_version="v-search-1",
            description="Release for vector search test",
            embedding_set_id=self.emb_set_id,
            chunk_ids=[self.target_chunk_id, self.distractor_chunk_id],
        )
        self.release_mgr.activate_release(self.rel_id, actor="search-tester")

    def tearDown(self):
        self._cleanup()
        self.client.delete(
            "chunks",
            {"chunk_id": f"in.({self.target_chunk_id},{self.distractor_chunk_id},{self.unreleased_chunk_id})"},
            role="admin",
        )
        self.client.delete("embedding_sets", {"embedding_set_id": f"eq.{self.emb_set_id}"}, role="admin")
        self.client.close()

    def _cleanup(self):
        self.client.delete("active_release", {"id": "eq.1"}, role="admin")
        self.client.delete("release_chunks", {"release_id": f"eq.{self.rel_id}"}, role="admin")
        self.client.delete("knowledge_releases", {"release_id": f"eq.{self.rel_id}"}, role="admin")

    def test_exact_cosine_search_ranking_and_rls_isolation(self):
        """Exact cosine search ranks target first and excludes unreleased chunk."""
        # Query vector aligned with target (index 0 = 1.0)
        query_vec = [0.0] * 1024
        query_vec[0] = 1.0

        # Runtime search (anon role subject to RLS)
        results = self.retriever.search(query_vec, match_threshold=0.0, match_count=10, role="runtime")

        # Must return target and distractor; unreleased chunk MUST NOT be returned!
        retrieved_ids = [r.chunk_id for r in results]
        self.assertIn(self.target_chunk_id, retrieved_ids)
        self.assertIn(self.distractor_chunk_id, retrieved_ids)
        self.assertNotIn(self.unreleased_chunk_id, retrieved_ids, "Unreleased chunk must not leak into search")

        # Target similarity must be approx 1.0
        self.assertAlmostEqual(results[0].similarity, 1.0, places=5)
        self.assertEqual(results[0].chunk_id, self.target_chunk_id)

        # Distractor similarity must be approx 0.0 (orthogonal)
        distractor_res = next(r for r in results if r.chunk_id == self.distractor_chunk_id)
        self.assertAlmostEqual(distractor_res.similarity, 0.0, places=5)

    def test_match_threshold_filtering(self):
        """Chunks below match_threshold are excluded from results."""
        query_vec = [0.0] * 1024
        query_vec[0] = 1.0

        # Set threshold to 0.5; distractor (similarity 0.0) should be excluded
        results = self.retriever.search(query_vec, match_threshold=0.5, match_count=10, role="runtime")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].chunk_id, self.target_chunk_id)


if __name__ == "__main__":
    unittest.main()
