"""Read-only adapter: prospectus_extractor v3.3 chunk dict -> Chunk contract.

It never edits its input and never imports the extractor. It preserves chunk ids, content hashes and
token-count methods, recomputes them to catch stale or altered chunks, and raises ChunkMappingError
with a stable `reason` for anything it cannot map. The extractor does not record the page size next
to a bounding box; this adapter will not invent one. Pass `page_sizes` or choose
on_missing_page_size="omit_and_report" to drop the box with a reported gap.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from .base import VOCAB, ContractError, is_plain_filename
from .source import Chunk, SourceSpan, canonical_text, compute_content_hash, joined_span_text, privileged_key_paths

CHUNKER_VERSION = "palsu-chunker-v1"
ESTIMATE_METHOD = "estimate-v1"
_SHA = re.compile(r"^[0-9a-f]{64}$")

REQUIRED = ("chunk_id", "chunk_type", "chunker_version", "content_review", "pdf_sha256", "source_anchored",
            "text", "source_text", "source_spans", "pages", "table_indexes", "cell_ids", "content_hash",
            "token_count", "token_count_method", "source")
MAPPED = frozenset(REQUIRED) | {"section_path"}
SPAN_KEYS = ("pdf_sha256", "page", "printed_page_label", "locator", "text", "bbox", "bbox_origin", "extraction")
LOCATOR_KEYS = {"table_cells": ("kind", "table_index", "cell_ids"), "text_item": ("kind", "item_ids"),
                "docling_ref": ("kind", "ref")}
EXTRACTION_KEYS = ("source_kind", "resolution_method", "repair_id", "ocr_confidence")


class ChunkMappingError(ContractError):
    def __init__(self, reason: str, detail: str = ""):
        super().__init__(f"{reason}{': ' + detail if detail else ''}")
        self.reason = reason


@dataclass(frozen=True)
class Gap:
    span_index: int
    page: int | None
    reason: str


@dataclass(frozen=True)
class AdaptedChunk:
    chunk: Chunk
    gaps: tuple[Gap, ...]


def _hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def locator_key(spans) -> str:
    return json.dumps(sorted(json.dumps([s.get("page"), s["locator"]], sort_keys=True) for s in spans))


def make_chunk_id(pdf_sha256: str | None, locator: str, digest: str) -> str:
    return _hash([pdf_sha256 or "unanchored", locator, digest, CHUNKER_VERSION])


def adapt_chunk(raw: Any, *, page_sizes: Mapping[tuple[str, int], tuple[float, float]] | None = None,
                on_missing_page_size: str = "reject") -> AdaptedChunk:
    if on_missing_page_size not in ("reject", "omit_and_report"):
        raise ValueError("on_missing_page_size must be 'reject' or 'omit_and_report'")
    if not isinstance(raw, Mapping):
        raise ChunkMappingError("not_a_mapping")
    for key in REQUIRED:
        if key not in raw:
            raise ChunkMappingError(f"missing_key:{key}")
    privileged = privileged_key_paths({k: v for k, v in raw.items() if k != "source_spans"})
    if privileged:
        raise ChunkMappingError(f"privileged_field:{privileged[0].lstrip('/')}")
    if raw["chunker_version"] != CHUNKER_VERSION:
        raise ChunkMappingError("unsupported_chunker_version", str(raw["chunker_version"]))
    if raw["token_count_method"] != ESTIMATE_METHOD:
        raise ChunkMappingError("unsupported_token_count_method", str(raw["token_count_method"]))
    sha = raw["pdf_sha256"]
    if sha is not None and not (isinstance(sha, str) and _SHA.match(sha)):
        raise ChunkMappingError("invalid_pdf_sha256")
    if raw["source_anchored"] is not (sha is not None):
        raise ChunkMappingError("anchor_flag_mismatch")
    if not isinstance(raw["source"], str) or not is_plain_filename(raw["source"]):
        raise ChunkMappingError("local_path_in_source")
    if raw["source_text"] is not None and not isinstance(raw["source_text"], str):
        raise ChunkMappingError("invalid_source_text")
    if raw["content_review"] not in VOCAB["states"]["content_review_state"]:
        raise ChunkMappingError("invalid_content_review", str(raw["content_review"]))
    raw_spans = raw["source_spans"]
    if not isinstance(raw_spans, list) or not raw_spans:
        raise ChunkMappingError("no_source_spans")

    gaps: list[Gap] = []
    has_text = raw["source_text"] is not None
    spans = [_map_span(i, s, sha, page_sizes or {}, on_missing_page_size, gaps, has_text)
             for i, s in enumerate(raw_spans)]
    # Only an identical span (same page, locator and text) is a duplicate. Distinct spans may share a cell,
    # as the extractor's term schedules share header cells. A strict default the owner may overrule.
    seen: set = set()
    for s in spans:
        identity = (s.page, s.locator.model_dump_json(), s.text)
        if identity in seen:
            raise ChunkMappingError("duplicate_source_location", f"identical span on page {s.page}")
        seen.add(identity)

    if compute_content_hash(raw["source_text"], raw["text"]) != raw["content_hash"]:
        raise ChunkMappingError("content_hash_mismatch")
    if make_chunk_id(sha, locator_key(raw_spans), raw["content_hash"]) != raw["chunk_id"]:
        raise ChunkMappingError("chunk_id_mismatch")
    derived = {
        "pages": sorted({s.page for s in spans if s.page is not None}),
        "table_indexes": sorted({s.locator.table_index for s in spans if s.locator.table_index is not None}),
        "cell_ids": list(dict.fromkeys(i for s in spans for i in s.locator.cell_ids)),
    }
    for key, value in derived.items():
        if raw[key] != value:
            raise ChunkMappingError(f"derived_field_mismatch:{key}")

    if has_text and canonical_text(raw["source_text"]) != joined_span_text(spans):
        raise ChunkMappingError("source_text_differs_from_spans")

    section = raw.get("section_path", [])
    if not isinstance(section, list) or not all(isinstance(p, str) and p for p in section):
        raise ChunkMappingError("invalid_section_path")
    count = raw["token_count"]
    if not isinstance(count, int) or isinstance(count, bool) or count < 0:
        raise ChunkMappingError("invalid_token_count")
    payload = {
        "schema_version": Chunk.SCHEMA_VERSION, "chunk_id": raw["chunk_id"], "chunk_type": raw["chunk_type"],
        "chunker_version": raw["chunker_version"], "edition_id": None, "document_id": None, "version_id": None,
        "byte_sha256": sha, "anchored": sha is not None, "source_verification": "pending",
        "content_review": raw["content_review"], "text": raw["text"], "source_text": raw["source_text"],
        "spans": [s.model_dump(mode="json") for s in spans], "section_path": section, "scope": [],
        "content_hash": raw["content_hash"],
        "token_count": {"count": count, "method": ESTIMATE_METHOD, "exact": False,
                        "includes_prefix_and_special_tokens": False},
        "source_label": raw["source"], "type_fields": {k: v for k, v in raw.items() if k not in MAPPED},
    }
    try:
        chunk = Chunk.parse(payload)
    except ContractError as exc:
        raise ChunkMappingError("type_fields_not_json", str(exc)) from exc
    except ValidationError as exc:
        raise ChunkMappingError("invalid_chunk", str(exc).splitlines()[1] if len(str(exc).splitlines()) > 1 else "") from exc
    return AdaptedChunk(chunk, tuple(gaps))


def _map_span(index: int, raw: Any, chunk_sha: str | None, page_sizes, mode: str, gaps: list[Gap],
              source_text_present: bool = True) -> SourceSpan:
    if not isinstance(raw, Mapping):
        raise ChunkMappingError("invalid_span", f"span {index} is not a mapping")
    for key in raw:
        if key not in SPAN_KEYS:
            raise ChunkMappingError(f"unmapped_span_key:{key}")
    for key in SPAN_KEYS:
        if key not in raw:
            raise ChunkMappingError(f"missing_span_key:{key}")
    if raw["pdf_sha256"] != chunk_sha:
        raise ChunkMappingError("span_digest_differs")
    page = raw["page"]
    if chunk_sha is not None:
        if page is None:
            raise ChunkMappingError("span_missing_page")
        # A span without printed text is allowed only in a chunk that itself asserts no source_text
        # (a layout fallback chunk); otherwise the printed text it claims has nothing behind it.
        if source_text_present and not (isinstance(raw["text"], str) and raw["text"].strip()):
            raise ChunkMappingError("span_missing_text")
        if not source_text_present and raw["text"] is not None:
            raise ChunkMappingError("span_text_without_source_text")
    label = raw["printed_page_label"]
    if label is not None and not (isinstance(label, str) and label):
        raise ChunkMappingError("invalid_span:printed_page_label")
    locator = _map_locator(raw["locator"])
    extraction = raw["extraction"]
    if not isinstance(extraction, Mapping) or set(extraction) - set(EXTRACTION_KEYS):
        bad = sorted(set(extraction) - set(EXTRACTION_KEYS)) if isinstance(extraction, Mapping) else []
        raise ChunkMappingError(f"unmapped_extraction_key:{bad[0]}" if bad else "invalid_span:extraction")
    bbox, origin, size = raw["bbox"], raw["bbox_origin"], None
    if bbox is not None:
        if not (isinstance(bbox, (list, tuple)) and len(bbox) == 4
                and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in bbox)):
            raise ChunkMappingError("invalid_span:bbox")
        if origin is None:
            raise ChunkMappingError("bbox_missing_origin")
        size = page_sizes.get((chunk_sha, page)) if chunk_sha is not None else None
        if size is None:
            if mode == "reject":
                raise ChunkMappingError("bbox_missing_page_size", f"span {index}, page {page}")
            gaps.append(Gap(index, page, "bbox_missing_page_size"))
            bbox = origin = None
    try:
        return SourceSpan.parse({
            "schema_version": SourceSpan.SCHEMA_VERSION, "byte_sha256": chunk_sha, "version_id": None,
            "page": page, "printed_page_label": label, "locator": locator, "text": raw["text"],
            "bbox": list(bbox) if bbox is not None else None, "bbox_origin": origin,
            "page_size": list(size) if size is not None else None, "extraction": dict(extraction)})
    except (ValidationError, ContractError) as exc:
        raise ChunkMappingError("invalid_span_geometry" if bbox is not None else "invalid_span", str(exc)[:200]) from exc


def _map_locator(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or raw.get("kind") not in LOCATOR_KEYS:
        raise ChunkMappingError("unknown_locator_kind", str(raw.get("kind") if isinstance(raw, Mapping) else raw))
    kind = raw["kind"]
    for key in raw:
        if key not in LOCATOR_KEYS[kind]:
            raise ChunkMappingError(f"unmapped_locator_key:{key}")
    return {"kind": kind, "table_index": raw.get("table_index"), "cell_ids": list(raw.get("cell_ids", [])),
            "item_ids": list(raw.get("item_ids", [])), "ref": raw.get("ref")}
