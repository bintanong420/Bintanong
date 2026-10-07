"""Pure candidate-chunk identity, source spans and review-size estimates."""

from __future__ import annotations

import hashlib
import json
import math
import unicodedata
from typing import Any, Mapping, Sequence

CHUNKER_VERSION = "palsu-chunker-v1"
TOKEN_HARD_CAP = 512
TOKEN_RESERVE = 32
TOKEN_SPLIT_AT = 400
TOKEN_COUNT_METHOD = "estimate-v1"


def estimate_tokens(text: str) -> int:
    # ponytail: review heuristic only; exact model prefix/special-token counting before embedding.
    return max(math.ceil(len(text) / 3), math.ceil(len(text.split()) * 1.8))


def fits_cap(token_count: int) -> bool:
    """Fits the estimated review budget, not a proven tokenizer bound."""
    return token_count + TOKEN_RESERVE <= TOKEN_HARD_CAP


def canonical_text(text: Any) -> str:
    return unicodedata.normalize("NFC", " ".join(str(text).split()))


def _hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def content_hash(source_text: str, text: str) -> str:
    return _hash([canonical_text(source_text), canonical_text(text)])


def make_span(pdf_sha256: str | None, page: int | None, locator: Mapping[str, Any], text: str | None,
              bbox: Sequence[float] | None, source_kind: str, resolution_method: str = "deterministic",
              repair_id: str | None = None, *, bbox_origin: str | None = None) -> dict[str, Any]:
    return {"pdf_sha256": pdf_sha256, "page": page, "printed_page_label": None,
            "locator": dict(locator), "text": text, "bbox": list(bbox) if bbox else None,
            "bbox_origin": bbox_origin,
            "extraction": {"source_kind": source_kind, "resolution_method": resolution_method,
                           "repair_id": repair_id, "ocr_confidence": None}}


def spans_from_cells(cells: Sequence[Mapping[str, Any]], pdf_sha256: str | None, source_kind: str,
                     resolution_method: str = "deterministic", repair_id: str | None = None) -> list[dict[str, Any]]:
    unique = {c["cell_id"]: c for c in cells}
    groups: dict[tuple, list] = {}
    for c in sorted(unique.values(), key=lambda c: (c["table_index"], c["row_start"], c["col_start"], c["cell_id"])):
        origin = c.get("bbox_origin")
        unknown_box = c["cell_id"] if c.get("bbox") and origin not in {"TOPLEFT", "BOTTOMLEFT"} else ""
        groups.setdefault((c["table_index"], c.get("page"), origin, unknown_box), []).append(c)
    spans = []
    for (table, page, origin, _unknown_box), group in sorted(groups.items(), key=lambda item: (
            item[0][0], item[0][1] is None, item[0][1] or 0, item[0][2] or "", item[0][3])):
        boxes = [c["bbox"] for c in group if c.get("bbox")]
        box = None
        if boxes and page is not None:
            box = [min(b[0] for b in boxes),
                   (max if origin == "BOTTOMLEFT" else min)(b[1] for b in boxes),
                   max(b[2] for b in boxes),
                   (min if origin == "BOTTOMLEFT" else max)(b[3] for b in boxes)]
        spans.append(make_span(pdf_sha256, page,
            {"kind": "table_cells", "table_index": table, "cell_ids": [c["cell_id"] for c in group]},
            " | ".join(c["text"] for c in group if c.get("text")), box, source_kind,
            resolution_method, repair_id, bbox_origin=origin))
    return spans


def spans_from_text_items(items: Sequence[Any], item_ids: Sequence[str | None], pdf_sha256: str | None,
                          source_kind: str) -> list[dict[str, Any]]:
    by_id = {i.get("item_id"): i for i in items if isinstance(i, Mapping)}
    return [make_span(pdf_sha256, item.get("page"), {"kind": "text_item", "item_ids": [item_id]},
                     item.get("text", ""), item.get("bbox"), source_kind,
                     bbox_origin=item.get("origin", item.get("bbox_origin")))
            for item_id in dict.fromkeys(i for i in item_ids if i)
            if (item := by_id.get(item_id)) is not None]


def locator_key(spans: Sequence[Mapping[str, Any]], fallback: str = "") -> str:
    return json.dumps(sorted(json.dumps([s.get("page"), s["locator"]], sort_keys=True)
                             for s in spans)) if spans else fallback


def make_chunk_id(pdf_sha256: str | None, locator: str, digest: str) -> str:
    return _hash([pdf_sha256 or "unanchored", locator, digest, CHUNKER_VERSION])


def pack_items(header: str, items: Sequence[tuple[str, Any]], limit: int = TOKEN_SPLIT_AT
               ) -> list[tuple[list[str], list[Any]]]:
    parts, lines, members = [], [], []
    for line, member in items:
        if lines and estimate_tokens("\n".join([header, *lines, line])) > limit:
            parts.append((lines, members))
            lines, members = [], []
        lines.append(line)
        members.append(member)
    if lines:
        parts.append((lines, members))
    return parts


def assemble_chunk(chunk_type: str, fields: Mapping[str, Any], text: str,
                   spans: Sequence[Mapping[str, Any]], *, pdf_sha256: str | None, source: str,
                   source_text: str | None = None, locator_fallback: str = "") -> dict[str, Any]:
    spans = list(spans)
    if source_text is None:
        source_text = "\n".join(s["text"] for s in spans if s.get("text"))
    digest = content_hash(source_text, text)
    return {**fields, "chunk_id": make_chunk_id(pdf_sha256, locator_key(spans, locator_fallback), digest),
            "chunk_type": chunk_type, "chunker_version": CHUNKER_VERSION, "content_review": "pending",
            "pdf_sha256": pdf_sha256, "source_anchored": bool(pdf_sha256), "text": text,
            "source_text": source_text, "source_spans": spans,
            "pages": sorted({s["page"] for s in spans if s.get("page") is not None}),
            "table_indexes": sorted({s["locator"]["table_index"] for s in spans if "table_index" in s["locator"]}),
            "cell_ids": list(dict.fromkeys(i for s in spans for i in s["locator"].get("cell_ids", []))),
            "content_hash": digest, "token_count": estimate_tokens(text), "token_count_method": TOKEN_COUNT_METHOD,
            "source": source}
