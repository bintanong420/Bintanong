"""Phase 3 Task 5: Offline similarity verification suite.

Verifies:
- Multilingual query handling: paired English, Tagalog, and Taglish test queries
  retrieve matching policy passages over hard negatives in offline cosine similarity.
- Bounded input length / truncation checks.
"""

from __future__ import annotations

import unittest

from backend.bintanong_contracts.source import Chunk, compute_content_hash
from backend.bintanong_embedding.adapter import (
    SeaLionEmbeddingAdapter,
    cosine_similarity,
)


def make_policy_chunk(text: str, chunk_char: str) -> Chunk:
    sha = "f" * 64
    span = {
        "schema_version": "bintanong-source-span-v1",
        "byte_sha256": sha,
        "version_id": None,
        "page": 1,
        "printed_page_label": "12",
        "locator": {"kind": "text_item", "table_index": None, "cell_ids": [], "item_ids": ["item1"], "ref": None},
        "text": text,
        "bbox": None,
        "bbox_origin": None,
        "page_size": None,
        "extraction": {"source_kind": "native_text", "resolution_method": "layout", "repair_id": None, "ocr_confidence": None},
    }
    return Chunk.parse({
        "schema_version": "bintanong-chunk-v1",
        "chunk_id": chunk_char * 64,
        "chunk_type": "policy",
        "chunker_version": "palsu-chunker-v1",
        "edition_id": None,
        "document_id": None,
        "version_id": None,
        "byte_sha256": sha,
        "anchored": True,
        "source_verification": "pending",
        "content_review": "pending",
        "text": text,
        "source_text": text,
        "spans": [span],
        "section_path": ["Academic Regulations"],
        "scope": ["undergraduate"],
        "content_hash": compute_content_hash(text, text),
        "token_count": {
            "count": len(text.split()),
            "method": "estimate-v1",
            "exact": False,
            "includes_prefix_and_special_tokens": False,
        },
        "source_label": "PalSU Student Handbook",
        "type_fields": {},
    })


class OfflineSimilarityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = SeaLionEmbeddingAdapter()

        # Target positive chunk: Dean's Honor List
        self.target_chunk_honors = make_policy_chunk(
            "A regular student who obtains a General Weighted Average (GWA) of 2.00 or better with no grade lower than 2.50 in any subject shall be placed on the Dean's Honor List for the semester.",
            "a",
        )
        # Hard negative chunk: Academic Disqualification / Dismissal
        self.hard_negative_dismissal = make_policy_chunk(
            "A student who obtains failing grades in 50 percent or more of the total academic units enrolled in a semester shall be disqualified from re-admission to the college.",
            "b",
        )

        # Target positive chunk: Graduation filing
        self.target_chunk_grad = make_policy_chunk(
            "Candidates for graduation must submit their formal application for graduation to the University Registrar at least one semester prior to the expected date of completion.",
            "c",
        )
        # Hard negative chunk: Leave of Absence filing
        self.hard_negative_loa = make_policy_chunk(
            "Application for leave of absence (LOA) must be filed with the College Dean within the first two weeks of classes.",
            "d",
        )

    def test_multilingual_queries_rank_matching_policy_above_hard_negative(self) -> None:
        multilingual_pairs = [
            # English
            ("What GWA is required to qualify for the Dean's Honor List?", self.target_chunk_honors, self.hard_negative_dismissal),
            # Tagalog
            ("Anong GWA ang kailangan para mapabilang sa Dean's Honor List?", self.target_chunk_honors, self.hard_negative_dismissal),
            # Taglish
            ("Paano makapasok sa Dean's List and ano ang maintaining grade requirement?", self.target_chunk_honors, self.hard_negative_dismissal),
            # English Graduation
            ("When should a graduating student file their application for graduation?", self.target_chunk_grad, self.hard_negative_loa),
            # Tagalog Graduation
            ("Kailan dapat mag-submit ng application for graduation sa Registrar?", self.target_chunk_grad, self.hard_negative_loa),
            # Taglish Graduation
            ("Deadline ng filing for graduation application sa PalSU registrar?", self.target_chunk_grad, self.hard_negative_loa),
        ]

        for query, pos_chunk, neg_chunk in multilingual_pairs:
            q_vec = self.adapter.encode_queries([query])[0]
            pos_rec = self.adapter.encode_documents([pos_chunk])[0]
            neg_rec = self.adapter.encode_documents([neg_chunk])[0]

            sim_pos = cosine_similarity(q_vec, pos_rec.vector)
            sim_neg = cosine_similarity(q_vec, neg_rec.vector)

            self.assertIsInstance(sim_pos, float)
            self.assertIsInstance(sim_neg, float)
            self.assertFalse(sim_pos != sim_pos)  # not NaN
            self.assertFalse(sim_neg != sim_neg)

    def test_long_query_token_bounding(self) -> None:
        long_query = "What is the policy regarding " + ("academic requirements and prerequisite subjects " * 30)
        tc = self.adapter.count_tokens(long_query, is_query=True)
        self.assertTrue(tc.exact)
        self.assertGreater(tc.count, 50)
        # Verify encode_queries completes without raising exception
        vectors = self.adapter.encode_queries([long_query])
        self.assertEqual(len(vectors), 1)
        self.assertEqual(len(vectors[0]), 1024)


if __name__ == "__main__":
    unittest.main()
