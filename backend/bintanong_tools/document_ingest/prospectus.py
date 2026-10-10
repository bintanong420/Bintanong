"""Bind legacy prospectus evidence to a pending byte-derived register identity."""
from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from ...bintanong_contracts.chunk_adapter import ChunkMappingError, adapt_chunk
from ...bintanong_contracts.governance import SourceDocumentVersion
from ...bintanong_contracts.source import (bind_chunk, check_chunk_binding, check_span_binding,
                                         privileged_key_paths)
from .register import load_pending_register


def bind_prospectus_chunks(payload: Mapping[str, Any], version: SourceDocumentVersion, *,
                           page_sizes: Mapping[tuple[str, int], tuple[float, float]]) -> dict[str, Any]:
    """Refuse global identity/shape violations; account for unsupported chunks individually.

    All identity claims are checked before binding, whose shared helper replaces span versions.
    Inputs remain untouched, including on refusal. Output is a candidate, never an approval.
    """
    version = load_pending_register([version])[0]
    if not isinstance(payload, Mapping) or not isinstance(page_sizes, Mapping):
        raise ValueError("payload and page_sizes must be mappings")
    identity = payload.get("run_identity")
    if not isinstance(identity, Mapping) or identity.get("pdf_sha256") != version.byte_sha256:
        raise ValueError("payload digest does not match the pending registered bytes")
    rag = payload.get("rag")
    if not isinstance(rag, Mapping):
        raise ValueError("rag must be a mapping")
    raw_chunks = []
    seen = set()
    for group in ("semantic_chunks", "hierarchical_chunks"):
        chunks = rag.get(group)
        if not isinstance(chunks, list):
            raise ValueError(f"rag.{group} must be a list")
        for raw in chunks:
            if not isinstance(raw, Mapping):
                raise ValueError("chunk must be a mapping")
            chunk_id = raw.get("chunk_id")
            if not isinstance(chunk_id, str) or re.fullmatch(r"[0-9a-f]{64}", chunk_id) is None:
                raise ValueError("chunk needs a SHA-256 identity")
            if chunk_id in seen:
                raise ValueError("duplicate chunk identity")
            seen.add(chunk_id)
            if privileged_key_paths(raw):
                raise ValueError("chunk carries privileged fields")
            if raw.get("pdf_sha256") != version.byte_sha256:
                raise ValueError("chunk digest differs from pending registered bytes")
            for name in ("version_id", "document_id", "edition_id"):
                if raw.get(name) is not None:
                    raise ValueError(f"preexisting chunk {name} is not allowed")
            spans = raw.get("source_spans")
            if not isinstance(spans, list) or any(not isinstance(s, Mapping) for s in spans):
                raise ValueError("source_spans must be a list of mappings")
            for span in spans:
                if span.get("version_id") is not None:
                    raise ValueError("preexisting span version_id is not allowed")
                if span.get("pdf_sha256") != version.byte_sha256:
                    raise ValueError("span digest differs from pending registered bytes")
            raw_chunks.append(raw)

    emitted, rejected = [], []
    for raw in raw_chunks:
        try:
            chunk = adapt_chunk(raw, page_sizes=page_sizes).chunk
        except ChunkMappingError as exc:
            rejected.append({"chunk_id": raw["chunk_id"], "reason": exc.reason})
            continue
        for span in chunk.spans:
            check_span_binding(span, version)
        if any(not s.is_complete or s.bbox is None or s.bbox_origin is None or s.page_size is None
               for s in chunk.spans):
            rejected.append({"chunk_id": raw["chunk_id"], "reason": "incomplete_source_span"})
            continue
        bound = bind_chunk(chunk, version)
        check_chunk_binding(bound, version)
        for span in bound.spans:
            check_span_binding(span, version)
        emitted.append(bound.model_dump(mode="json"))
    return {"version_id": version.version_id, "source_sha256": version.byte_sha256,
            "chunks": emitted, "rejections": rejected}
