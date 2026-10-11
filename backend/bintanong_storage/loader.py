"""Validated candidate imports through transactional administrative RPCs."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Any, Dict, Optional, Sequence

from backend.bintanong_contracts.embedding import EmbeddingRecord
from backend.bintanong_contracts.source import Chunk, SpanLocator, canonical_text, compute_content_hash
from .client import SupabaseStorageClient

CONFIG_FIELDS = ("model_id", "model_revision", "dimension", "normalization",
                 "prompt_fingerprint", "preprocessing_fingerprint", "tokenizer_fingerprint")


@dataclass(frozen=True)
class LoaderSummary:
    embedding_set_id: str
    total_chunks_loaded: int
    total_embeddings_loaded: int
    total_spans_loaded: int
    total_documents_loaded: int
    duplicate_avoided_count: int


class BatchKnowledgeLoader:
    def __init__(self, client: Optional[SupabaseStorageClient] = None) -> None:
        self.client = client or SupabaseStorageClient()

    @staticmethod
    def _manifest_record(data: Dict[str, Any], embeddings=None) -> dict:
        config = {key: data[key] for key in CONFIG_FIELDS}
        if config["dimension"] != 1024 or config["normalization"] != "l2":
            raise ValueError("Storage requires 1024-dimensional l2 embeddings")
        if not config["model_id"] or not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", config["model_revision"]):
            raise ValueError("Manifest must identify a model and pinned revision")
        for key in ("prompt_fingerprint", "preprocessing_fingerprint", "tokenizer_fingerprint"):
            if not re.fullmatch(r"[0-9a-f]{64}", config[key]) or set(config[key]) == {"0"}:
                raise ValueError(f"Invalid {key}")
        set_id = data.get("embedding_set_id")
        if not set_id:
            if embeddings is None:
                raise ValueError("An explicit embedding_set_id or the full embedding artifact is required")
            # Sorting binds identities to the complete corpus and vector content,
            # while allowing an identical artifact to arrive in a different order.
            corpus = sorted((row["chunk_id"], row["chunk_content_hash"], row["vector"], row.get("token_count", {}))
                            for row in embeddings)
            set_id = hashlib.sha256(json.dumps({"configuration": config, "corpus": corpus},
                sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
        return {
            "embedding_set_id": set_id,
            "schema_version": data.get("schema_version", "bintanong-embedding-manifest-v1"),
            **config,
            "total_chunks": int(data.get("total_embedded_records", 0)),
        }

    def load_embedding_manifest(self, manifest_data: Dict[str, Any]) -> str:
        return self.client.rpc("load_embedding_set", {"p_record": self._manifest_record(manifest_data)}, role="admin")

    @staticmethod
    def _chunk_records(chunks: Sequence[Chunk | Dict[str, Any]], document_id=None, version_id=None):
        records, spans = [], []
        for item in chunks:
            data = item.model_dump(mode="json") if isinstance(item, Chunk) else dict(item)
            if "schema_version" in data:
                data = Chunk.parse(data).model_dump(mode="json")
            # Administrative DB-row dictionaries remain supported for unchanged
            # reimports, with the same content and source-location checks.
            source_text = data.get("source_text", data["text"])
            if data["content_hash"] != compute_content_hash(source_text, data["text"]):
                raise ValueError("Chunk content_hash does not match its content")
            raw_spans = data.get("spans", [])
            if data.get("anchored", True) and not raw_spans:
                raise ValueError("An anchored chunk requires source spans")
            for span in raw_spans:
                SpanLocator.parse({"table_index": None, "cell_ids": [], "item_ids": [], "ref": None,
                                   "section_path": [], **span.get("locator", {})})
                if isinstance(span.get("page"), bool) or not isinstance(span.get("page"), int) or span["page"] < 1:
                    raise ValueError("Source span requires a positive physical page")
                if span.get("byte_sha256", data.get("byte_sha256")) != data.get("byte_sha256"):
                    raise ValueError("Span digest differs from chunk")
                if source_text is not None and (not span.get("text") or not span["text"].strip()):
                    raise ValueError("Source span requires printed text")
                if source_text is None and span.get("text") is not None:
                    raise ValueError("A serialized table without source_text must have textless located spans")
            if source_text is not None and canonical_text(source_text) != canonical_text(" ".join(s["text"] for s in raw_spans)):
                raise ValueError("Chunk source_text differs from span text")
            cid = data["chunk_id"]
            if not re.fullmatch(r"[0-9a-f]{64}", cid):
                raise ValueError("Invalid chunk identity")
            records.append({
                "chunk_id": cid, "chunk_type": data.get("chunk_type", "policy"),
                "chunker_version": data.get("chunker_version", "palsu-chunker-v1"),
                "document_id": data.get("document_id") or document_id,
                "version_id": data.get("version_id") or version_id,
                "edition_id": data.get("edition_id"),
                "byte_sha256": data.get("byte_sha256"), "anchored": data.get("anchored", True),
                "source_verification": data.get("source_verification", "pending"),
                "content_review": data.get("content_review", "pending"), "text": data["text"],
                "source_text": source_text,
                "section_path": data.get("section_path", []), "scope": data.get("scope", []),
                "content_hash": data["content_hash"], "token_count": data.get("token_count", {}),
                "source_label": data.get("source_label", ""), "type_fields": data.get("type_fields", {}),
            })
            for span_order, span in enumerate(raw_spans):
                spans.append({
                    "chunk_id": cid, "span_order": span_order, "byte_sha256": span.get("byte_sha256") or data.get("byte_sha256"),
                    "version_id": span.get("version_id") or data.get("version_id") or version_id,
                    "page": span.get("page"), "printed_page_label": span.get("printed_page_label"),
                    "locator": span.get("locator", {}), "text": span["text"], "bbox": span.get("bbox"),
                    "bbox_origin": span.get("bbox_origin"), "page_size": span.get("page_size"),
                    "extraction": span.get("extraction", {}),
                })
        return records, spans

    def load_chunks(self, chunks: Sequence[Chunk | Dict[str, Any]], document_id=None, version_id=None) -> int:
        records, spans = self._chunk_records(chunks, document_id, version_id)
        return self.client.rpc("load_chunk_batch", {"p_chunks": records, "p_spans": spans}, role="admin")

    @staticmethod
    def _embedding_records(embeddings: Sequence[EmbeddingRecord | Dict[str, Any]], set_id: str,
                           config: dict) -> list[dict]:
        records = []
        for item in embeddings:
            data = item.model_dump(mode="json") if isinstance(item, EmbeddingRecord) else dict(item)
            if "schema_version" in data:
                data = EmbeddingRecord.parse(data).model_dump(mode="json")
            for key in CONFIG_FIELDS:
                if key in data and data[key] != config[key]:
                    raise ValueError(f"Embedding {key} differs from manifest")
            vector = data["vector"]
            if len(vector) != 1024 or any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in vector):
                raise ValueError("Embedding must contain 1024 finite numbers")
            if abs(math.sqrt(math.fsum(v * v for v in vector)) - 1) > 1e-6:
                raise ValueError("Embedding must be l2-normalized")
            records.append({
                "chunk_id": data["chunk_id"], "embedding_set_id": set_id,
                "chunk_content_hash": data["chunk_content_hash"], "embedding": list(vector),
                "token_count": data.get("token_count", {}),
            })
        return records

    def load_embeddings(self, embeddings: Sequence[EmbeddingRecord | Dict[str, Any]], embedding_set_id: str) -> int:
        sets = self.client.select("embedding_sets", filters={"embedding_set_id": f"eq.{embedding_set_id}"}, role="admin")
        if not sets:
            raise ValueError("Embedding set does not exist")
        records = self._embedding_records(embeddings, embedding_set_id, sets[0])
        return self.client.rpc("load_embedding_batch", {"p_records": records, "p_embedding_set_id": embedding_set_id}, role="admin")

    def load_artifacts(self, manifest_path: Path | str, embeddings_path: Path | str,
                       chunks: Optional[Sequence[Chunk | Dict[str, Any]]] = None) -> LoaderSummary:
        manifest_data = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
        embeddings = [json.loads(line) for line in Path(embeddings_path).read_text(encoding="utf-8").splitlines() if line.strip()]
        manifest = self._manifest_record(manifest_data, embeddings)
        if len(embeddings) != manifest["total_chunks"]:
            raise ValueError("Manifest record count does not match embedding artifact")
        if len({row["chunk_id"] for row in embeddings}) != len(embeddings):
            raise ValueError("Duplicate embedding records in artifact")
        records = self._embedding_records(embeddings, manifest["embedding_set_id"], manifest)
        chunk_records, spans = self._chunk_records(chunks or [])
        if chunks is not None and {row["chunk_id"] for row in chunk_records} != {row["chunk_id"] for row in records}:
            raise ValueError("Chunk and embedding artifact identities differ")
        summary = self.client.rpc("load_knowledge_batch", {
            "p_embedding_set": manifest, "p_chunks": chunk_records, "p_spans": spans, "p_embeddings": records,
        }, role="admin")
        return LoaderSummary(**summary)
