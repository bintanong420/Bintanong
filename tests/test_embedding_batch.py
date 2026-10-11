from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from backend.bintanong_contracts.source import Chunk, compute_content_hash
from backend.bintanong_embedding.adapter import SeaLionEmbeddingAdapter
from backend.bintanong_embedding.batch import BatchEmbeddingRunner


def make_dummy_chunk(text: str, chunk_id_hex: str) -> Chunk:
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
        "chunk_id": chunk_id_hex,
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


class BatchEmbeddingRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="bt_embed_test_"))
        self.adapter = SeaLionEmbeddingAdapter()
        self.runner = BatchEmbeddingRunner(adapter=self.adapter, output_dir=self.temp_dir, batch_size=2)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_batch_embeds_and_creates_manifest(self) -> None:
        c1 = make_dummy_chunk("Section 1: Academic integrity.", "1" * 64)
        c2 = make_dummy_chunk("Section 2: Grading system.", "2" * 64)
        c3 = make_dummy_chunk("Section 3: Graduation requirements.", "3" * 64)

        records, manifest_path = self.runner.embed_chunks([c1, c2, c3])
        self.assertEqual(len(records), 3)
        self.assertTrue(manifest_path.is_file())

        # Check manifest contents
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["total_input_chunks"], 3)
        self.assertEqual(manifest["total_embedded_records"], 3)
        self.assertEqual(manifest["dimension"], 1024)

        # Check records file
        lines = (self.temp_dir / "embeddings.jsonl").read_text(encoding="utf-8").strip().splitlines()
        self.assertEqual(len(lines), 3)

    def test_resumption_skips_identical_chunks(self) -> None:
        c1 = make_dummy_chunk("Policy 1: Student conduct.", "1" * 64)
        c2 = make_dummy_chunk("Policy 2: Attendance policy.", "2" * 64)

        # First run: embed c1 and c2
        self.runner.embed_chunks([c1, c2])

        # Second run: request c1, c2, plus new c3
        c3 = make_dummy_chunk("Policy 3: Scholarship grant.", "3" * 64)
        records, _ = self.runner.embed_chunks([c1, c2, c3], resume=True)

        self.assertEqual(len(records), 3)
        lines = (self.temp_dir / "embeddings.jsonl").read_text(encoding="utf-8").strip().splitlines()
        # Should only have 3 records in file, not 5
        self.assertEqual(len(lines), 3)


if __name__ == "__main__":
    unittest.main()
