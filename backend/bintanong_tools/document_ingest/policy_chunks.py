"""Pending-only governed chunks; unsupported evidence remains an explicit rejection."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from ...bintanong_contracts.source import (Chunk, SourceSpan, bind_chunk, check_chunk_binding,
                                         check_span_binding, compute_content_hash)
from ..prospectus_extractor.chunking import canonical_text, estimate_tokens
from ..prospectus_extractor.identity import bytes_sha256
from .policy_text import PolicyCandidates, _item_spans
from .procedure_text import ProcedureCandidates
from .register import load_pending_register

CHUNKER_VERSION = "palsu-policy-chunker-v1"
TOKEN_CAP = 480  # estimate-v1 review cap, retaining the existing 32-token reserve.


@dataclass(frozen=True)
class ChunkCoverage:
    candidate_id: str
    chunk_ids: tuple[str, ...]


@dataclass(frozen=True)
class ChunkRejection:
    candidate_id: str
    reason: str


@dataclass(frozen=True)
class PolicyChunkResult:
    version_id: str
    byte_sha256: str
    token_cap: int
    chunks: tuple[Chunk, ...]
    item_coverage: tuple[ChunkCoverage, ...]
    table_coverage: tuple[ChunkCoverage, ...]
    rejections: tuple[ChunkRejection, ...]

    def as_dict(self) -> dict[str, Any]:
        return {"version_id": self.version_id, "byte_sha256": self.byte_sha256,
                "chunker_version": CHUNKER_VERSION, "token_cap": self.token_cap,
                "token_count_method": "estimate-v1",
                "chunks": [c.model_dump(mode="json") for c in self.chunks],
                "item_coverage": [{"item_id": c.candidate_id, "chunk_ids": list(c.chunk_ids)}
                                  for c in self.item_coverage],
                "table_coverage": [{"table_id": c.candidate_id, "chunk_ids": list(c.chunk_ids)}
                                   for c in self.table_coverage],
                "rejections": [{"candidate_id": r.candidate_id, "reason": r.reason}
                               for r in self.rejections]}


def _chunk(spans, version, kind, section_path, fields, cap):
    parsed = tuple(SourceSpan.parse(s.model_dump(mode="json")) for s in spans)
    for span in parsed:
        check_span_binding(span, version)
        if (not span.is_complete or span.version_id != version.version_id or span.bbox is None
                or span.bbox_origin is None or span.page_size is None):
            raise ValueError("incomplete_source_span")
    source_text = "\n".join(s.text for s in parsed)
    count = estimate_tokens(source_text)
    if count > cap:
        raise ValueError("over_token_cap")
    digest = compute_content_hash(source_text, source_text)
    locator = json.dumps(sorted(json.dumps([s.page, s.locator.model_dump(mode="json")], sort_keys=True)
                                for s in parsed))
    chunk_id = bytes_sha256(json.dumps([version.edition_id, locator, digest, CHUNKER_VERSION],
                                      ensure_ascii=False, sort_keys=True).encode("utf-8"))
    chunk = Chunk.parse({"schema_version": Chunk.SCHEMA_VERSION, "chunk_id": chunk_id,
        "chunk_type": kind, "chunker_version": CHUNKER_VERSION, "edition_id": version.edition_id,
        "document_id": version.document_id, "version_id": version.version_id,
        "byte_sha256": version.byte_sha256, "anchored": True, "source_verification": "pending",
        "content_review": "pending", "source_text": source_text, "text": source_text,
        "spans": [s.model_dump(mode="json") for s in parsed], "section_path": list(section_path),
        "scope": [], "content_hash": digest, "source_label": version.filename,
        "token_count": {"count": count, "method": "estimate-v1", "exact": False,
                        "includes_prefix_and_special_tokens": False}, "type_fields": fields})
    chunk = bind_chunk(chunk, version)
    check_chunk_binding(chunk, version)
    return chunk


def _table_parts(table, version, labels, cap):
    raw, pages = json.loads(table.raw_table_json), json.loads(table.raw_geometry_json)
    data = raw.get("data", {})
    cells = data.get("table_cells")
    if not isinstance(cells, list) or not cells:
        raise ValueError("missing_raw_table_cells")
    wrapper = raw.get("prov", [])
    if not isinstance(wrapper, list) or not wrapper or any(not isinstance(p, dict) for p in wrapper):
        raise ValueError("missing_table_provenance")
    table_pages = {p.get("page_no") for p in wrapper}
    if any(type(p) is not int or str(p) not in pages for p in table_pages):
        raise ValueError("invalid_table_page")
    rows, ids = [], set()
    for index, cell in enumerate(cells):
        if not isinstance(cell, dict) or not isinstance(cell.get("text"), str) or not cell["text"].strip():
            raise ValueError("missing_or_blank_cell_text")
        bounds = [cell.get(k) for k in ("start_row_offset_idx", "end_row_offset_idx",
                                      "start_col_offset_idx", "end_col_offset_idx")]
        nr, nc = data.get("num_rows"), data.get("num_cols")
        if (any(type(n) is not int for n in [*bounds, nr, nc])
                or not 0 <= bounds[0] < bounds[1] <= nr or not 0 <= bounds[2] < bounds[3] <= nc):
            raise ValueError("invalid_cell_row_column_bounds")
        cell_id = cell.get("cell_id", f"{table.table_id}-cell-{index}")
        if not isinstance(cell_id, str) or not cell_id.strip() or cell_id in ids:
            raise ValueError("invalid_or_duplicate_cell_id")
        ids.add(cell_id)
        provs = cell.get("prov")
        if provs is None:
            if len(table_pages) != 1 or not isinstance(cell.get("bbox"), dict):
                raise ValueError("unlocated_cell_on_ambiguous_table_page")
            provs = [{"page_no": next(iter(table_pages)), "bbox": cell["bbox"]}]
        if not isinstance(provs, list) or not provs or any(not isinstance(p, dict) for p in provs):
            raise ValueError("invalid_cell_provenance")
        if any(p.get("page_no") not in table_pages for p in provs):
            raise ValueError("cell_page_outside_table_provenance")
        spans = _item_spans(cell_id, cell["text"], provs, pages, version, labels)
        if canonical_text(cell["text"]) != canonical_text(" ".join(s.text for s in spans)):
            raise ValueError("cell_text_differs_from_spans")
        spans = tuple(SourceSpan.parse({**s.model_dump(mode="json"), "locator": {
            "kind": "table_cells", "table_index": int(table.table_id.removeprefix("table-")),
            "cell_ids": [cell_id], "item_ids": [], "ref": None}}) for s in spans)
        header = cell.get("column_header") is True
        # Merged rows form one indivisible group, in the original raw cell order.
        if rows and bounds[0] < rows[-1]["end"]:
            if bounds[0] < rows[-1]["start"]:
                raise ValueError("ambiguous_raw_row_order")
            rows[-1]["end"] = max(rows[-1]["end"], bounds[1])
            rows[-1]["spans"].extend(spans)
            rows[-1]["headers"].append(header)
        else:
            rows.append({"start": bounds[0], "end": bounds[1], "spans": list(spans), "headers": [header]})
    all_spans = [s for row in rows for s in row["spans"]]
    if estimate_tokens("\n".join(s.text for s in all_spans)) <= cap:
        return [all_spans]
    header_rows = []
    for row in rows:
        if all(row["headers"]) and len(header_rows) == rows.index(row):
            header_rows.append(row)
        else:
            break
    if (not header_rows or len(header_rows) == len(rows)
            or any(any(r["headers"]) for r in rows[len(header_rows):])):
        raise ValueError("ambiguous_or_missing_table_headers")
    headers = [s for row in header_rows for s in row["spans"]]
    parts, current = [], list(headers)
    for row in rows[len(header_rows):]:
        trial = current + row["spans"]
        if estimate_tokens("\n".join(s.text for s in trial)) > cap:
            if len(current) == len(headers):
                raise ValueError("over_token_cap")
            parts.append(current)
            current = list(headers) + row["spans"]
            if estimate_tokens("\n".join(s.text for s in current)) > cap:
                raise ValueError("over_token_cap")
        else:
            current = trial
    parts.append(current)
    return parts


def _check_unit_support(unit, version, page_count):
    spans = tuple(SourceSpan.parse(s.model_dump(mode="json")) for s in unit.spans)
    if any(s.page not in unit.pages or s.page is None or not 1 <= s.page <= page_count
           or s.page_size is None for s in spans):
        raise ValueError("raw_span_provenance_mismatch")
    geometry, labels = {}, {}
    for span in spans:
        size = {"size": {"width": span.page_size[0], "height": span.page_size[1]}}
        if str(span.page) in geometry and geometry[str(span.page)] != size:
            raise ValueError("conflicting_span_page_size")
        geometry[str(span.page)] = size
        if span.printed_page_label is not None:
            labels[span.page] = span.printed_page_label
    expected = _item_spans(unit.item_id, unit.source_text, json.loads(unit.raw_provenance_json),
                           geometry, version, labels)
    if spans != expected:
        raise ValueError("raw_span_provenance_mismatch")


def build_policy_chunks(candidates: PolicyCandidates | ProcedureCandidates, *,
                        token_cap: int = TOKEN_CAP) -> PolicyChunkResult:
    """Consume checked candidates without promoting authority or silently losing an item."""
    if type(token_cap) is not int or not 1 <= token_cap <= TOKEN_CAP:
        raise ValueError("token_cap must be a positive estimate at most 480")
    if not isinstance(candidates, (PolicyCandidates, ProcedureCandidates)):
        raise ValueError("expected policy or procedure candidates")
    candidates.check_invariants()
    version = load_pending_register([candidates.version])[0]
    pdf = candidates if isinstance(candidates, PolicyCandidates) else candidates.pdf
    classification = ("policy_candidate" if isinstance(candidates, PolicyCandidates)
                      else candidates.classification)
    chunks, covered, table_covered, rejected = [], [], [], []
    if pdf is not None:
        for unit in pdf.units:
            try:
                if unit.rejection_reason or not unit.spans:
                    raise ValueError(unit.rejection_reason or "incomplete_source_span")
                _check_unit_support(unit, version, pdf.page_count)
                if canonical_text(unit.source_text) != canonical_text(" ".join(s.text or "" for s in unit.spans)):
                    raise ValueError("source_text_differs_from_spans")
                chunk = _chunk(unit.spans, version, classification, unit.heading_path,
                    {"item_id": unit.item_id, "label": unit.label, "printed_scope": unit.printed_scope,
                     "exception_to": unit.exception_to}, token_cap)
            except (KeyError, TypeError, ValueError) as exc:
                rejected.append(ChunkRejection(unit.item_id, str(exc)))
                continue
            chunks.append(chunk)
            covered.append(ChunkCoverage(unit.item_id, (chunk.chunk_id,)))
    else:
        rejected.extend(ChunkRejection(u.item_id, "pending_locator_contract") for u in candidates.pptx_units)
    if isinstance(candidates, ProcedureCandidates):
        labels = {s.page: s.printed_page_label for u in pdf.units for s in u.spans
                  if s.printed_page_label is not None} if pdf is not None else {}
        section = ()
        units = {u.item_id: u for u in pdf.units} if pdf is not None else {}
        tables = {t.table_id: t for t in candidates.tables}
        for ref in candidates.reading_order:
            key = ref.replace("#/texts/", "text-").replace("#/tables/", "table-")
            if key in units:
                section = units[key].heading_path
            if key not in tables:
                continue
            table = tables[key]
            try:
                if pdf is None:
                    raise ValueError("pending_locator_contract")
                parts = _table_parts(table, version, labels, token_cap)
                emitted = [_chunk(part, version, classification, section,
                    {"table_id": key, "part": i + 1, "part_count": len(parts)}, token_cap)
                           for i, part in enumerate(parts)]
            except (KeyError, TypeError, ValueError) as exc:
                rejected.append(ChunkRejection(key, str(exc)))
                continue
            chunks.extend(emitted)
            table_covered.append(ChunkCoverage(key, tuple(c.chunk_id for c in emitted)))
    return PolicyChunkResult(version.version_id, version.byte_sha256, token_cap, tuple(chunks),
                             tuple(covered), tuple(table_covered), tuple(rejected))
