"""Batch embedding execution and progress resumption for SEA-LION E5.

Implements Phase 3 Task 3 & 4 per Master Implementation Plan Section 8:
- Resumable batch embedding over candidate Chunks.
- Checks chunk_id and content_hash; reuses valid cached records.
- Checkpoints completed batches to a JSONL vector artifact without Supabase.
- Produces an embedding manifest linking model revision and fingerprints.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

from backend.bintanong_contracts import base
from backend.bintanong_contracts.embedding import EmbeddingRecord, check_embedding_matches_chunk
from backend.bintanong_contracts.source import Chunk
from backend.bintanong_embedding.adapter import SeaLionEmbeddingAdapter, compute_sha256_hex


class BatchEmbeddingRunner:
    def __init__(
        self,
        adapter: SeaLionEmbeddingAdapter | None = None,
        output_dir: Path | str = "artifacts/embeddings",
        batch_size: int = 16,
    ) -> None:
        self.adapter = adapter or SeaLionEmbeddingAdapter()
        self.output_dir = Path(output_dir)
        self.batch_size = max(1, batch_size)
        self.records_file = self.output_dir / "embeddings.jsonl"
        self.manifest_file = self.output_dir / "embedding_manifest.json"

    def load_existing_records(self) -> Dict[str, EmbeddingRecord]:
        """Load previously checkpointed records if file exists."""
        records: Dict[str, EmbeddingRecord] = {}
        if not self.records_file.is_file():
            return records

        with self.records_file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                rec = EmbeddingRecord.parse(data)
                records[rec.chunk_id] = rec
        return records

    def embed_chunks(
        self,
        chunks: Sequence[Chunk],
        resume: bool = True,
    ) -> Tuple[List[EmbeddingRecord], Path]:
        """Batch encode chunks with progress checkpointing and resumption."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        cached_records: Dict[str, EmbeddingRecord] = self.load_existing_records() if resume else {}

        all_records: List[EmbeddingRecord] = []
        pending_chunks: List[Chunk] = []

        for chunk in chunks:
            cached = cached_records.get(chunk.chunk_id)
            if (
                cached is not None
                and cached.chunk_content_hash == chunk.content_hash
                and cached.model_revision == self.adapter.config.model_revision
                and cached.prompt_fingerprint == self.adapter.config.prompt_fingerprint
            ):
                all_records.append(cached)
            else:
                pending_chunks.append(chunk)

        # Append newly embedded chunks in batches
        with self.records_file.open("a" if resume else "w", encoding="utf-8") as out_f:
            for i in range(0, len(pending_chunks), self.batch_size):
                batch = pending_chunks[i : i + self.batch_size]
                new_records = self.adapter.encode_documents(batch)
                for rec in new_records:
                    out_f.write(json.dumps(rec.model_dump(mode="json"), sort_keys=True) + "\n")
                    all_records.append(rec)
                out_f.flush()

        manifest = self._write_manifest(len(chunks), len(all_records))
        return all_records, self.manifest_file

    def _write_manifest(self, total_input_chunks: int, total_embedded: int) -> dict:
        manifest_data = {
            "schema_version": "bintanong-embedding-manifest-v1",
            "model_id": self.adapter.config.model_id,
            "model_revision": self.adapter.config.model_revision,
            "dimension": self.adapter.config.dimension,
            "normalization": self.adapter.config.normalization,
            "prompt_fingerprint": self.adapter.config.prompt_fingerprint,
            "preprocessing_fingerprint": self.adapter.config.preprocessing_fingerprint,
            "tokenizer_fingerprint": self.adapter.config.tokenizer_fingerprint,
            "total_input_chunks": total_input_chunks,
            "total_embedded_records": total_embedded,
            "artifact_records_file": str(self.records_file.as_posix()),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        self.manifest_file.write_text(
            json.dumps(manifest_data, indent=2, sort_keys=True), encoding="utf-8"
        )
        return manifest_data
