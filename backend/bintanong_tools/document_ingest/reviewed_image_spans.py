"""Inactive original-image field regions and explicit reviewed decision graphs.

Regions are human transcription evidence, not native glyph/Docling-cell evidence.
Trusted render/layout inputs never grant institutional applicability or approval.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import re
from collections.abc import Mapping

from ...bintanong_contracts.source import SourceSpan
from .register import load_pending_register
from .reviewed_policy import build_reviewed_policy_bundle


def _json(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)


def _numbers(value, count):
    if (not isinstance(value, (list, tuple)) or len(value) != count
            or any(type(n) not in (int, float) or not math.isfinite(n) for n in value)):
        raise ValueError("finite region dimensions required")
    return list(value)


def _transform(page):
    size = _numbers(page.get("page_size"), 2)
    image = page.get("image_size")
    scale = page.get("scale")
    if (min(size) <= 0 or not isinstance(image, (list, tuple)) or len(image) != 2
            or any(type(n) is not int or n < 1 for n in image)
            or type(scale) not in (int, float) or not math.isfinite(scale) or scale <= 0
            or type(page.get("rotation")) is not int or page["rotation"] != 0
            or page.get("crop", "absent") is not None
            or list(image) != [math.ceil(d * scale) for d in size]
            or not isinstance(page.get("image_sha256"), str)
            or not re.fullmatch(r"[0-9a-f]{64}", page["image_sha256"])):
        raise ValueError("invalid original image transform")


def _region(box, page):
    l, t, r, b = _numbers(box, 4)
    width, height = page["image_size"]
    if not 0 <= l < r <= width or not 0 <= t < b <= height:
        raise ValueError("region outside original page image")
    result = [n / page["scale"] for n in (l, t, r, b)]
    pw, ph = page["page_size"]
    if result[2] > pw or result[3] > ph:
        raise ValueError("region extends past source points")
    return result


def _table_region(evidence, region_format, page, *, source_blank=False):
    if region_format == "source_region_pixels":
        return _numbers(evidence.get("source_region"), 4)
    if region_format == "raw_cell_points":
        cell = evidence.get("raw_cell")
        if source_blank and "raw_cell" in evidence and cell is None:
            return None
        box = cell.get("bbox") if isinstance(cell, dict) else None
        if not isinstance(box, dict) or box.get("coord_origin") != "TOPLEFT":
            raise ValueError("explicit TOPLEFT raw-cell coordinates required")
        return [n * page["scale"] for n in _numbers([box.get(k) for k in ("l", "t", "r", "b")], 4)]
    raise ValueError("explicit table region format required")


def _span(row, name, text, region, page):
    pixel_label = ",".join(str(n) for n in region)
    data = {"schema_version": SourceSpan.SCHEMA_VERSION, "byte_sha256": row["source_sha256"],
        "version_id": row["version_id"], "page": page["physical_page"], "printed_page_label": None,
        "locator": {"kind": "text_item", "table_index": None, "cell_ids": [],
            "item_ids": [f"image-region:p{page['physical_page']}:{name}:{pixel_label}"], "ref": None},
        "text": text, "bbox": _region(region, page), "bbox_origin": "TOPLEFT", "page_size": page["page_size"],
        "extraction": {"source_kind": "original_pdf_image", "resolution_method": "owner_transcribed_region",
            "repair_id": hashlib.sha256(_json([row["source_sha256"], name, text, region, page]).encode()).hexdigest(),
            "ocr_confidence": None}}
    return SourceSpan.parse(data).model_dump(mode="json")


def _correction_review(row, field, evidence, page, events, aliases):
    event = events[field["review_event_sha256"]]
    alias = aliases.get(row["reading_id"])
    entries = event.get("reviewed_rows")
    if (not isinstance(alias, str) or not alias or not isinstance(entries, list)
            or event.get("source_sha256") != row["source_sha256"]
            or type(event.get("physical_page")) is not int or event["physical_page"] != page["physical_page"]
            or event.get("original_image_sha256") != page["image_sha256"]):
        return None
    matches = [r for r in entries if isinstance(r, dict) and r.get("row_id") == alias]
    if len(matches) != 1 or not isinstance(matches[0].get("fields"), list):
        return None
    fields = [f for f in matches[0]["fields"] if isinstance(f, dict) and f.get("field") == field["name"]]
    if len(fields) != 1:
        return None
    review = fields[0]
    original_evidence = {k: v for k, v in evidence.items() if k != "recorded_decision"}
    if (review.get("review_decision") != "corrected"
            or review.get("original_proposal_text") != field["original_value"]
            or evidence.get("proposed_reading") != field["original_value"]
            or review.get("reviewed_text") != field["reviewed_value"]
            or evidence.get("recorded_decision", "corrected") != "corrected"
            or review.get("original_image_evidence") != original_evidence):
        return None
    return {"event_row_id": alias, "field_review": copy.deepcopy(review)}


def map_reviewed_image_spans(bundle, *, sources, review_events, source_versions, image_pages, read_page_image,
                             correction_rows=None, table_region_formats=None):
    """Map confirmed scalar fields using hash-matched, full-page, unrotated renders.

    image_pages keys are (source_sha256,physical_page). The injected trusted reader
    receives exact source bytes/page, returns image_bytes and actual render metadata.
    Original proposal/event scope remains the caller's reviewed mapping responsibility.
    correction_rows maps reading IDs to trusted event row IDs; changed corrected
    fields require an exact field review, preserving the original proposed text.
    table_region_formats keys are (source_sha256,physical_page), with explicit
    source_region_pixels or raw_cell_points values for retained table evidence.
    Confirmed table blanks retain their regions/evidence and an empty span list.
    """
    if not callable(read_page_image) or not isinstance(image_pages, Mapping):
        raise ValueError("original page reader and image descriptors required")
    if not isinstance(bundle, dict) or not isinstance(bundle.get("readings"), list):
        raise ValueError("invalid reviewed preparation")
    core = build_reviewed_policy_bundle(bundle["readings"], sources=sources, review_events=review_events)
    if any(_json(bundle.get(k)) != _json(v) for k, v in core.items()):
        raise ValueError("reviewed preparation differs from original evidence")
    if correction_rows is None:
        correction_rows = {}
    if not isinstance(correction_rows, Mapping):
        raise ValueError("correction row mapping required")
    if table_region_formats is None:
        table_region_formats = {}
    if not isinstance(table_region_formats, Mapping):
        raise ValueError("table region formats mapping required")
    versions = {v.version_id: v for v in load_pending_register(source_versions)}
    for row in core["readings"]:
        version = versions.get(row["version_id"])
        if version is None or version.byte_sha256 != row["source_sha256"]:
            raise ValueError("reading source/version absent or mismatched")
    cache, anchors, mapped, withheld = {}, {}, [], []
    def checked_page(sha, number):
        key = (sha, number)
        if key in cache:
            return cache[key]
        declaration = image_pages.get(key)
        if not isinstance(declaration, dict):
            cache[key] = (None, "image_page_unavailable")
            return cache[key]
        try:
            _transform(declaration)
        except ValueError:
            cache[key] = (None, "invalid_image_transform")
            return cache[key]
        try:
            observed = read_page_image(sources[sha], number)
        except (OSError, ValueError, IndexError, RuntimeError):
            cache[key] = (None, "image_reader_failure")
            return cache[key]
        if (not isinstance(observed, dict)
                or not {"image_bytes", "image_size", "page_size", "scale", "rotation", "crop"} <= observed.keys()
                or not isinstance(observed.get("image_bytes"), bytes)
                or hashlib.sha256(observed["image_bytes"]).hexdigest() != declaration["image_sha256"]
                or any(observed.get(k) != declaration.get(k) for k in ("image_size", "page_size", "scale", "rotation", "crop"))):
            cache[key] = (None, "original_image_mismatch")
            return cache[key]
        page = {k: copy.deepcopy(declaration[k]) for k in ("image_sha256", "image_size", "page_size", "scale", "rotation", "crop")}
        page.update(source_sha256=sha, physical_page=number)
        cache[key] = (page, None)
        return cache[key]
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
            if not isinstance(field["reviewed_value"], str):
                reject("structured_image_field_requires_mapping")
                continue
            evidence = field["locator"].get("evidence")
            corrected = field["decision"] == "corrected" and field["original_value"] != field["reviewed_value"]
            if not isinstance(evidence, dict):
                reject("image_region_unavailable")
                continue
            table = "proposed_image_region" not in evidence
            pages = field["locator"]["physical_pages"]
            region_format = table_region_formats.get((row["source_sha256"], pages[0])) if table else None
            if table and (not isinstance(region_format, str)
                          or region_format not in {"source_region_pixels", "raw_cell_points"}):
                reject("image_region_unavailable")
                continue
            if field["source_blank"] and not table:
                reject("blank_image_field_requires_mapping")
                continue
            if (evidence.get("field") != name or field["locator"]["field"] != name
                    or (not corrected and evidence.get("proposed_reading") != field["reviewed_value"])
                    or (not table and evidence.get("region_origin") != "TOPLEFT_pixels")
                    or (table and evidence.get("proposed_blank") is not field["source_blank"])
                    or (field["source_blank"] and (field["original_value"] != "" or field["reviewed_value"] != ""))
                    or len(pages) != 1):
                reject("invalid_image_field_evidence")
                continue
            page, error = checked_page(row["source_sha256"], field["locator"]["physical_pages"][0])
            if error:
                reject(error)
                continue
            correction = None
            if corrected:
                correction = _correction_review(row, field, evidence, page, core["review_events"], correction_rows)
                if correction is None:
                    reject("correction_review_mismatch")
                    continue
            try:
                region = (_table_region(evidence, region_format, page, source_blank=field["source_blank"])
                          if table else evidence["proposed_image_region"])
                if region is not None:
                    _region(region, page)
                span = None if field["source_blank"] else _span(row, name, field["reviewed_value"], region, page)
            except ValueError:
                reject("invalid_image_field_evidence")
                continue
            anchors.setdefault(identity, {})[name] = [] if span is None else [span]
            mapped.append({"reading_id": identity, "field_name": name,
                "event_sha256": field["review_event_sha256"], "image_sha256": page["image_sha256"],
                "original_evidence": copy.deepcopy(evidence), "pixel_region": copy.deepcopy(region),
                "span": span})
            if table:
                mapped[-1].update(region_format=region_format, source_blank=field["source_blank"])
            if correction is not None:
                mapped[-1]["correction_review"] = correction
    return {"schema_version": "bintanong-reviewed-image-spans-v1", "candidate_only": True,
        "activation_eligible": False, "source_governance_changed": False, "field_spans": anchors,
        "mapping_evidence": mapped, "withheld_fields": withheld,
        "validated_pages": [copy.deepcopy(p) for p, error in cache.values() if error is None],
        "preparation": copy.deepcopy(bundle), "coverage": {"mapped_fields": len(mapped), "withheld_fields": len(withheld)}}


def bind_reviewed_flowchart(mapping, *, arrow_reading_id, row_reading_ids, edge_regions, terminal_region):
    """Preserve exact reviewed decision edges and full scalar rows as inactive graph.

    Pixel route regions are trusted original-layout annotations, not an autonomous
    interpretation of graph direction. These edges never become executable rules.
    """
    if mapping.get("candidate_only") is not True or mapping.get("activation_eligible") is not False:
        raise ValueError("inactive image mapping required")
    prep = mapping["preparation"]
    rows = {r["reading_id"]: r for r in prep["readings"]}
    arrow = rows.get(arrow_reading_id)
    if (arrow is None or arrow["intended_audience"] != "undergraduate" or arrow["applicability"] == "excluded"
            or arrow["gaps"] or len(arrow["fields"]) != 1):
        raise ValueError("complete undergraduate arrow reading required")
    field = arrow["fields"][0]
    if field["name"] != "arrows" or field["decision"] not in {"accepted", "corrected"}:
        raise ValueError("confirmed arrow field required")
    if (not isinstance(edge_regions, list) or not edge_regions
            or [{k: e.get(k) for k in ("from", "label", "to")} for e in edge_regions] != field["reviewed_value"]):
        raise ValueError("arrow directions/labels/endpoints differ from reviewed values")
    if (not isinstance(row_reading_ids, Mapping) or not row_reading_ids or "END" in row_reading_ids
            or len(set(row_reading_ids.values())) != len(row_reading_ids)):
        raise ValueError("distinct row mappings required")
    nodes = []
    pages = field["locator"]["physical_pages"]
    if len(pages) != 1:
        raise ValueError("arrow page mapping unresolved")
    page = next((p for p in mapping["validated_pages"] if p["source_sha256"] == arrow["source_sha256"]
        and p["physical_page"] == pages[0]), None)
    if page is None:
        raise ValueError("arrow original page unavailable")
    _transform(page)
    for node_id, identity in row_reading_ids.items():
        row = rows.get(identity)
        if (not isinstance(node_id, str) or not node_id or row is None or row["gaps"]
                or row["source_sha256"] != arrow["source_sha256"] or row["version_id"] != arrow["version_id"]):
            raise ValueError("row source/version or limits differ")
        fields = []
        for item in row["fields"]:
            located = mapping["field_spans"].get(identity, {}).get(item["name"])
            if item["decision"] not in {"accepted", "corrected"} or not located:
                raise ValueError("row has unconfirmed or unmapped fields")
            spans = [SourceSpan.parse(s) for s in located]
            if any(s.byte_sha256 != arrow["source_sha256"] or s.version_id != arrow["version_id"]
                or s.page != pages[0] or s.text != item["reviewed_value"] for s in spans):
                raise ValueError("row field association differs from mapped source")
            fields.append({"name": item["name"], "value": copy.deepcopy(item["reviewed_value"]),
                "spans": copy.deepcopy(located), "event_sha256": item["review_event_sha256"]})
        nodes.append({"node_id": node_id, "reading_id": identity, "fields": fields})
    edges = []
    for index, edge in enumerate(edge_regions):
        if edge["from"] not in row_reading_ids or edge["to"] not in set(row_reading_ids) | {"END"}:
            raise ValueError("arrow has dangling row endpoint")
        span = _span(arrow, f"edge-{index}-{edge['label']}", edge["label"], edge["pixel_region"], page)
        edges.append({**copy.deepcopy(edge), "label_span": span, "event_sha256": field["review_event_sha256"]})
    if not any(e["to"] == "END" for e in edges):
        raise ValueError("reviewed arrow terminal absent")
    terminal_span = _span(arrow, "terminal-END", "END", terminal_region, page)
    return {"schema_version": "bintanong-reviewed-flowchart-v1", "candidate_only": True,
        "activation_eligible": False, "source_governance_changed": False,
        "arrow_reading_id": arrow_reading_id, "source_sha256": arrow["source_sha256"],
        "version_id": arrow["version_id"], "image_sha256": page["image_sha256"],
        "nodes": nodes, "edges": edges, "terminal": {"label": "END", "pixel_region": copy.deepcopy(terminal_region),
            "span": terminal_span, "event_sha256": field["review_event_sha256"]},
        "source_limits": copy.deepcopy(arrow["gaps"])}
