from __future__ import annotations

import math
import unittest

from backend.bintanong_contracts import base
from backend.bintanong_contracts.embedding import check_embedding_matches_chunk, L2_TOLERANCE
from backend.bintanong_contracts.source import Chunk, SourceSpan, compute_content_hash
from backend.bintanong_embedding.adapter import (
    EmbeddingConfig,
    SeaLionEmbeddingAdapter,
    cosine_similarity,
    MODEL_DIMENSION,
)


def make_dummy_chunk(text: str, chunk_char: str = "b") -> Chunk:
    sha = "a" * 64
    span = {
        "schema_version": "bintanong-source-span-v1",
        "byte_sha256": sha,
        "version_id": None,
        "page": 1,
        "printed_page_label": None,
        "locator": {"kind": "text_item", "table_index": None, "cell_ids": [], "item_ids": ["t1"], "ref": None},
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
        "section_path": [],
        "scope": [],
        "content_hash": compute_content_hash(text, text),
        "token_count": {
            "count": len(text.split()),
            "method": "estimate-v1",
            "exact": False,
            "includes_prefix_and_special_tokens": False,
        },
        "source_label": "x",
        "type_fields": {},
    })


class EmbeddingAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = SeaLionEmbeddingAdapter()

    def test_config_fingerprints_non_empty_and_deterministic(self) -> None:
        cfg1 = EmbeddingConfig()
        cfg2 = EmbeddingConfig()
        self.assertEqual(cfg1.prompt_fingerprint, cfg2.prompt_fingerprint)
        self.assertEqual(cfg1.preprocessing_fingerprint, cfg2.preprocessing_fingerprint)
        self.assertEqual(cfg1.tokenizer_fingerprint, cfg2.tokenizer_fingerprint)
        self.assertEqual(len(cfg1.prompt_fingerprint), 64)
        self.assertEqual(len(cfg1.tokenizer_fingerprint), 64)

    def test_encode_queries_returns_normalized_vectors(self) -> None:
        queries = [
            "What is the grading system in PalSU?",
            "Ano ang mga requirements para sa graduation?",
            "Pano mag-file ng leave of absence (LOA)?",
        ]
        vectors = self.adapter.encode_queries(queries)
        self.assertEqual(len(vectors), 3)

        for vec in vectors:
            self.assertEqual(len(vec), MODEL_DIMENSION)
            norm = math.sqrt(sum(v * v for v in vec))
            self.assertTrue(math.isclose(norm, 1.0, abs_tol=L2_TOLERANCE))
            # Assert all elements are finite floats
            for v in vec:
                self.assertIsInstance(v, float)
                self.assertFalse(math.isnan(v))
                self.assertFalse(math.isinf(v))

    def test_encode_documents_creates_valid_embedding_records(self) -> None:
        chunk1 = make_dummy_chunk("A student must maintain a GWA of at least 2.50 to remain in good standing.", "1")
        chunk2 = make_dummy_chunk("Ang pag-file ng leave of absence ay dapat gawin bago magsimula ang semestre.", "2")

        records = self.adapter.encode_documents([chunk1, chunk2])
        self.assertEqual(len(records), 2)

        # Validate that each record matches its chunk
        check_embedding_matches_chunk(records[0], chunk1)
        check_embedding_matches_chunk(records[1], chunk2)

        # Check normalization
        for rec in records:
            norm = math.sqrt(sum(v * v for v in rec.vector))
            self.assertTrue(math.isclose(norm, 1.0, abs_tol=L2_TOLERANCE))
            self.assertEqual(rec.dimension, MODEL_DIMENSION)
            self.assertTrue(rec.token_count.exact)
            self.assertTrue(rec.token_count.includes_prefix_and_special_tokens)

    def test_empty_inputs_raise_value_error(self) -> None:
        with self.assertRaises(ValueError):
            self.adapter.encode_queries([])
        with self.assertRaises(ValueError):
            self.adapter.encode_documents([])

    def test_cosine_similarity_computation(self) -> None:
        v1 = (1.0, 0.0, 0.0)
        v2 = (1.0, 0.0, 0.0)
        v3 = (0.0, 1.0, 0.0)
        v4 = (-1.0, 0.0, 0.0)

        self.assertAlmostEqual(cosine_similarity(v1, v2), 1.0)
        self.assertAlmostEqual(cosine_similarity(v1, v3), 0.0)
        self.assertAlmostEqual(cosine_similarity(v1, v4), -1.0)


if __name__ == "__main__":
    unittest.main()
