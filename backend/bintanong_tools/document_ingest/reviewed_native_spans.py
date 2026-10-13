"""Map retained native PDF character evidence to separate, inactive source spans.

An injected original-range reader checks the exact source bytes. Native locators
name actual PDF character ranges, never invented Docling items/cells. Technical
mapping does not resolve audience applicability or raise institutional governance.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from ...bintanong_contracts.source import SourceSpan, check_span_binding
from .register import load_pending_register
from .reviewed_policy import build_reviewed_policy_bundle


def _json(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)


def _range(value):
    return (isinstance(value, list) and len(value) == 2
        and all(type(n) is int for n in value) and 0 <= value[0] < value[1])


def _numbers(value, count):
    if (not isinstance(value, (list, tuple)) or len(value) != count
            or any(type(n) not in (int, float) or not math.isfinite(n) for n in value)):
        raise ValueError("finite PDF point coordinates required")
    return list(value)


def _box(value, order):
    box = _numbers(value, 4)
    if order == "left,bottom,right,top":
        return [box[0], box[3], box[2], box[1]]
    if order == "left,top,right,bottom":
        return box
    raise ValueError("explicit native PDF point coordinate order required")


def map_reviewed_native_spans(
    bundle: dict[str, Any], *, sources: Mapping[str, bytes], review_events: Mapping[str, bytes],
    source_versions: Sequence[Any], read_native_range: Callable,
) -> dict[str, Any]:
    """Recheck native evidence with source bytes and preserve every unmapped field.

    Reader signature: (source_bytes, physical_page, start, end_exclusive) ->
    {text, bbox, page_size, coordinate_order, origin}. It is a trusted original-PDF
    reader, not an approval authority. No source geometry is guessed from images.
    """
    if not callable(read_native_range):
        raise ValueError("original native-range reader required")
    if not isinstance(bundle, dict) or not isinstance(bundle.get("readings"), list):
        raise ValueError("invalid reviewed preparation")
    core = build_reviewed_policy_bundle(bundle["readings"], sources=sources, review_events=review_events)
    if any(_json(bundle.get(key)) != _json(value) for key, value in core.items()):
        raise ValueError("reviewed preparation differs from original evidence")
    versions = {v.version_id: v for v in load_pending_register(source_versions)}
    for row in core["readings"]:
        version = versions.get(row["version_id"])
        if version is None or version.byte_sha256 != row["source_sha256"]:
            raise ValueError("reading source/version missing or mismatched")
    ranges = Counter()
    for row in core["readings"]:
        for field in row["fields"]:
            evidence = field["locator"].get("evidence", {})
            native_range = evidence.get("native_character_span") if isinstance(evidence, dict) else None
            if _range(native_range) and len(field["locator"]["physical_pages"]) == 1:
                ranges[(row["source_sha256"], field["locator"]["physical_pages"][0], *native_range)] += 1
    anchors, mapped, withheld = {}, [], []
    blanks = 0
    for row in core["readings"]:
        for field in row["fields"]:
            identity, name = row["reading_id"], field["name"]
            def reject(reason):
                withheld.append({"reading_id": identity, "field_name": name, "reason": reason})
            if row["intended_audience"] != "undergraduate" or row["applicability"] == "excluded":
                reject("undergraduate_review_audience_required")
                continue
            if field["decision"] not in {"accepted", "corrected"}:
                reject("field_not_confirmed")
                continue
            evidence = field["locator"].get("evidence")
            if not isinstance(evidence, dict) or not {"native_character_span", "pdf_bbox"} <= evidence.keys():
                reject("native_evidence_unavailable")
                continue
            value = field["reviewed_value"]
            pages = field["locator"]["physical_pages"]
            if len(pages) != 1:
                reject("native_page_split_requires_mapping")
                continue
            native_range = evidence["native_character_span"]
            if (not isinstance(value, str) or evidence.get("field") != name
                    or field["locator"]["field"] != name
                    or evidence.get("proposed_text") != value
                    or evidence.get("native_text", "") != value):
                reject("invalid_native_evidence")
                continue
            span, observation = None, None
            if field["source_blank"]:
                if native_range is not None or evidence["pdf_bbox"] is not None:
                    reject("invalid_native_evidence")
                    continue
                blanks += 1
            else:
                if not _range(native_range):
                    reject("invalid_native_evidence")
                    continue
                page, (start, end) = pages[0], native_range
                if ranges[(row["source_sha256"], page, start, end)] != 1:
                    reject("duplicate_native_range")
                    continue
                size = row.get("original_row_evidence", {}).get("page_size")
                if size is None:
                    reject("native_page_size_unavailable")
                    continue
                try:
                    size = _numbers(size, 2)
                    bbox = _box(evidence["pdf_bbox"], evidence.get("coordinate_order"))
                    data = {"schema_version": SourceSpan.SCHEMA_VERSION,
                        "byte_sha256": row["source_sha256"], "version_id": row["version_id"],
                        "page": page, "printed_page_label": None,
                        "locator": {"kind": "text_item", "table_index": None, "cell_ids": [],
                            "item_ids": [f"native-pdf:p{page}:chars{start}-{end}"], "ref": None},
                        "text": value, "bbox": bbox, "bbox_origin": evidence.get("origin"), "page_size": size,
                        "extraction": {"source_kind": "native_pdf", "resolution_method": "original_native_range",
                            "repair_id": hashlib.sha256(_json([row["source_sha256"], page, name, evidence, size]).encode()).hexdigest(),
                            "ocr_confidence": None}}
                    span = SourceSpan.parse(data)
                    check_span_binding(span, versions[row["version_id"]])
                except ValueError:
                    reject("invalid_native_evidence")
                    continue
                try:
                    observation = read_native_range(sources[row["source_sha256"]], page, start, end)
                except (OSError, ValueError, IndexError):
                    reject("native_reader_failure")
                    continue
                try:
                    if (not isinstance(observation, dict) or observation.get("text") != value
                            or observation.get("origin") != evidence["origin"]
                            or _numbers(observation.get("page_size"), 2) != size
                            or _box(observation.get("bbox"), observation.get("coordinate_order")) != bbox):
                        raise ValueError("observed original range differs from saved evidence")
                    # Reject non-finite/unsupported metadata returned by the reader.
                    _json(observation)
                except (TypeError, ValueError):
                    reject("native_observation_mismatch")
                    continue
            serialized = span.model_dump(mode="json") if span is not None else None
            anchors.setdefault(identity, {})[name] = [serialized] if serialized is not None else []
            mapped.append({"reading_id": identity, "field_name": name, "source_sha256": row["source_sha256"],
                "version_id": row["version_id"], "physical_page": pages[0],
                "native_character_range": copy.deepcopy(native_range), "source_blank": field["source_blank"],
                "event_sha256": field["review_event_sha256"], "original_evidence": copy.deepcopy(evidence),
                "observed_native": copy.deepcopy(observation), "span": serialized})
    return {"schema_version": "bintanong-reviewed-native-spans-v1", "candidate_only": True,
        "activation_eligible": False, "source_governance_changed": False, "field_spans": anchors,
        "mapping_evidence": mapped, "withheld_fields": withheld, "preparation": copy.deepcopy(bundle),
        "coverage": {"supplied_fields": sum(len(r["fields"]) for r in core["readings"]),
            "mapped_nonblank_fields": len(mapped) - blanks, "mapped_blank_fields": blanks,
            "withheld_fields": len(withheld), "scope": "supplied native evidence only"}}
