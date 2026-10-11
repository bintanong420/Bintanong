from __future__ import annotations

import unittest
from backend.bintanong_storage.client import SupabaseStorageClient
from backend.bintanong_storage.loader import BatchKnowledgeLoader


class TestBatchKnowledgeLoaderIdempotency(unittest.TestCase):
    def setUp(self):
        self.client = SupabaseStorageClient()
        self.loader = BatchKnowledgeLoader(self.client)

        self.test_manifest = {
            "schema_version": "bintanong-embedding-manifest-v1",
            "model_id": "aisingapore/SEA-LION-E5-Embedding-600M",
            "model_revision": "df5b1c55623eeb5ef09ce3f3c50e24e2db433d7d1bbcccf76d2f01ba212df5f1",
            "dimension": 1024,
            "normalization": "l2",
            "prompt_fingerprint": "1111111111111111111111111111111111111111111111111111111111111111",
            "preprocessing_fingerprint": "2222222222222222222222222222222222222222222222222222222222222222",
            "tokenizer_fingerprint": "3333333333333333333333333333333333333333333333333333333333333333",
            "total_embedded_records": 2,
        }

        self.chunk_1_id = "a" * 64
        self.chunk_2_id = "b" * 64

        self.test_chunks = [
            {
                "chunk_id": self.chunk_1_id,
                "chunk_type": "policy",
                "chunker_version": "palsu-chunker-v1",
                "byte_sha256": "c" * 64,
                "anchored": True,
                "text": "Academic retention policy for CS majors.",
                "source_text": "Academic retention policy for CS majors.",
                "section_path": ["Retention"],
                "scope": ["BSCS"],
                "content_hash": "d" * 64,
                "spans": [
                    {
                        "byte_sha256": "c" * 64,
                        "page": 1,
                        "text": "Academic retention policy for CS majors.",
                        "locator": {"kind": "text_item", "item_ids": ["t1"]},
                    }
                ],
            },
            {
                "chunk_id": self.chunk_2_id,
                "chunk_type": "policy",
                "chunker_version": "palsu-chunker-v1",
                "byte_sha256": "e" * 64,
                "anchored": True,
                "text": "Prerequisites for CS 121: CS 111 with passing grade.",
                "source_text": "Prerequisites for CS 121: CS 111 with passing grade.",
                "section_path": ["Prerequisites"],
                "scope": ["BSCS"],
                "content_hash": "f" * 64,
                "spans": [],
            },
        ]

        vec1 = [0.0] * 1024
        vec1[0] = 1.0
        vec2 = [0.0] * 1024
        vec2[1] = 1.0

        self.test_embeddings = [
            {
                "chunk_id": self.chunk_1_id,
                "chunk_content_hash": "d" * 64,
                "vector": vec1,
            },
            {
                "chunk_id": self.chunk_2_id,
                "chunk_content_hash": "f" * 64,
                "vector": vec2,
            },
        ]

    def tearDown(self):
        set_id = self.test_manifest["prompt_fingerprint"]
        self.client.delete("chunk_embeddings", {"embedding_set_id": f"eq.{set_id}"}, role="admin")
        self.client.delete("source_spans", {"chunk_id": f"eq.{self.chunk_1_id}"}, role="admin")
        self.client.delete("source_spans", {"chunk_id": f"eq.{self.chunk_2_id}"}, role="admin")
        self.client.delete("chunks", {"chunk_id": f"eq.{self.chunk_1_id}"}, role="admin")
        self.client.delete("chunks", {"chunk_id": f"eq.{self.chunk_2_id}"}, role="admin")
        self.client.delete("embedding_sets", {"embedding_set_id": f"eq.{set_id}"}, role="admin")
        self.client.close()

    def test_idempotent_import_produces_zero_duplicates(self):
        """Exit gate: running the bulk loader a second time produces 0 duplicate records."""
        # 1. First import run
        set_id = self.loader.load_embedding_manifest(self.test_manifest)
        chunks_count_1 = self.loader.load_chunks(self.test_chunks)
        embs_count_1 = self.loader.load_embeddings(self.test_embeddings, embedding_set_id=set_id)

        self.assertEqual(chunks_count_1, 2)
        self.assertEqual(embs_count_1, 2)

        # Inspect database counts
        chunks_db_1 = self.client.select("chunks", filters={"chunk_id": f"in.({self.chunk_1_id},{self.chunk_2_id})"}, role="admin")
        embs_db_1 = self.client.select("chunk_embeddings", filters={"embedding_set_id": f"eq.{set_id}"}, role="admin")
        self.assertEqual(len(chunks_db_1), 2)
        self.assertEqual(len(embs_db_1), 2)

        # 2. Second import run with identical data
        chunks_count_2 = self.loader.load_chunks(self.test_chunks)
        embs_count_2 = self.loader.load_embeddings(self.test_embeddings, embedding_set_id=set_id)

        self.assertEqual(chunks_count_2, 2)
        self.assertEqual(embs_count_2, 2)

        # Inspect database counts after second run: MUST BE EXACTLY 2 (zero duplicates)
        chunks_db_2 = self.client.select("chunks", filters={"chunk_id": f"in.({self.chunk_1_id},{self.chunk_2_id})"}, role="admin")
        embs_db_2 = self.client.select("chunk_embeddings", filters={"embedding_set_id": f"eq.{set_id}"}, role="admin")
        self.assertEqual(len(chunks_db_2), 2, "Second load must not duplicate chunks")
        self.assertEqual(len(embs_db_2), 2, "Second load must not duplicate embeddings")

        # Verify spans: exactly 1 span for chunk 1
        spans = self.client.select("source_spans", filters={"chunk_id": f"eq.{self.chunk_1_id}"}, role="admin")
        self.assertEqual(len(spans), 1, "Spans must not duplicate")


if __name__ == "__main__":
    unittest.main()
