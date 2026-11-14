"""Inactive complete first-step associations from checked original region maps.

Consumes trusted verified mapping output, like the reviewed flowchart binder.
Neither parent fee geometry nor field associations grant institutional approval.
"""
from __future__ import annotations

import copy

from ...bintanong_contracts.source import SourceSpan
from .reviewed_image_spans import _span, _transform


PARTS = ("action", "condition_note", "processing_time", "responsible_person", "office")


def _page(mapping, row, number):
    pages = [p for p in mapping["validated_pages"] if p["source_sha256"] == row["source_sha256"]
             and p["physical_page"] == number]
    if len(pages) != 1:
        raise ValueError("original service page unavailable or ambiguous")
    _transform(pages[0])
    return pages[0]


def _mapped_field(mapping, row, field):
    if field["decision"] not in {"accepted", "corrected"} or field["source_blank"]:
        raise ValueError("confirmed nonblank service field required")
    value = field["reviewed_value"]
    located = mapping["field_spans"].get(row["reading_id"], {}).get(field["name"], [])
    result = {"value": copy.deepcopy(value), "source_blank": False,
        "event_sha256": field["review_event_sha256"], "locator": copy.deepcopy(field["locator"])}
    if value is None:
        if field["original_value"] is not None or located:
            raise ValueError("unrecorded note differs from original or has invented spans")
        return {**result, "state": "not_recorded", "spans": []}
    if not isinstance(value, str) or not value or len(located) != 1:
        raise ValueError("service scalar field unmapped")
    span = SourceSpan.parse(located[0])
    if (span.byte_sha256 != row["source_sha256"] or span.version_id != row["version_id"]
            or field["locator"]["physical_pages"] != [span.page] or span.text != value
            or span.bbox is None or span.bbox_origin != "TOPLEFT" or span.page_size is None
            or span.extraction.source_kind != "original_pdf_image"):
        raise ValueError("service scalar association differs from mapped source")
    page = _page(mapping, row, span.page)
    if list(span.page_size) != page["page_size"]:
        raise ValueError("service source dimensions differ")
    evidence = [e for e in mapping["mapping_evidence"] if e["reading_id"] == row["reading_id"]
                and e["field_name"] == field["name"]]
    if (len(evidence) != 1 or evidence[0]["span"] != located[0]
            or evidence[0]["event_sha256"] != field["review_event_sha256"]
            or evidence[0]["image_sha256"] != page["image_sha256"]
            or evidence[0]["original_evidence"] != field["locator"]["evidence"]):
        raise ValueError("service mapped field evidence differs")
    return {**result, "state": "mapped", "spans": copy.deepcopy(located)}


def bind_reviewed_service_step(mapping, *, reading_id, subaction_ids, fee_region):
    """Bind ordered first-step fields and one original parent fee source region.

    Null notes remain explicitly unrecorded. Fee region is a trusted full-page
    TOPLEFT pixel annotation, independently checked by the caller against originals.
    The structured output stays separate from the pending scalar chunk adapter.
    """
    if (mapping.get("candidate_only") is not True or mapping.get("activation_eligible") is not False
            or mapping.get("source_governance_changed") is not False):
        raise ValueError("inactive verified region mapping required")
    rows = {r["reading_id"]: r for r in mapping["preparation"]["readings"]}
    row = rows.get(reading_id)
    if (row is None or row["intended_audience"] != "undergraduate"
            or row["applicability"] == "excluded" or row["gaps"]):
        raise ValueError("complete undergraduate service reading required")
    fields = {f["name"]: f for f in row["fields"]}
    expected = []
    for field in row["fields"]:
        if "/" in field["name"]:
            identity = field["name"].split("/", 1)[0]
            if identity not in expected:
                expected.append(identity)
    if (not isinstance(subaction_ids, list) or not expected or subaction_ids != expected
            or any(not isinstance(i, str) or not i for i in subaction_ids)
            or len(set(subaction_ids)) != len(subaction_ids)
            or set(fields) != {"client_instruction", "shared_fee"} |
                {f"{identity}/{part}" for identity in subaction_ids for part in PARTS}):
        raise ValueError("complete ordered subaction field set required")
    client = _mapped_field(mapping, row, fields["client_instruction"])
    if client["state"] != "mapped":
        raise ValueError("mapped client instruction required")
    actions = []
    for identity in subaction_ids:
        associated = {}
        for part in PARTS:
            field = fields[f"{identity}/{part}"]
            original = field["locator"].get("evidence", {})
            page_key = ("office_source_pages" if part == "office" else
                        "role_source_pages" if part == "responsible_person" else "action_source_pages")
            if (not isinstance(original, dict) or original.get("subaction_id") != identity
                    or part not in original or original[part] != field["reviewed_value"]
                    or original.get(page_key) != field["locator"]["physical_pages"]
                    or (part != "condition_note" and field["reviewed_value"] is None)):
                raise ValueError("service subaction or page association differs")
            associated[part] = _mapped_field(mapping, row, field)
        actions.append({"subaction_id": identity, "fields": associated})
    fee = fields["shared_fee"]
    value = fee["reviewed_value"]
    original = fee["original_value"]
    original_value = {k: v for k, v in original.items() if k != "review"} if isinstance(original, dict) else original
    if (fee["decision"] not in {"accepted", "corrected"} or fee["source_blank"]
            or not isinstance(value, dict) or original_value != value
            or (isinstance(original, dict) and original.get("review", "owner_accepted") != "owner_accepted")
            or not isinstance(value.get("text"), str) or not value["text"]
            or type(value.get("source_page")) is not int
            or fee["locator"]["physical_pages"] != [value["source_page"]]
            or value.get("applies_to") != "logical_client_step_1"):
        raise ValueError("confirmed original parent fee reference required")
    page = _page(mapping, row, value["source_page"])
    fee_span = _span(row, "shared_fee", value["text"], fee_region, page)
    return {"schema_version": "bintanong-reviewed-service-step-v1", "candidate_only": True,
        "activation_eligible": False, "source_governance_changed": False,
        "reading_id": reading_id, "source_sha256": row["source_sha256"], "version_id": row["version_id"],
        "applicability": row["applicability"], "service_provenance_label": row.get("service"),
        "client_instruction": client, "subactions": actions,
        "shared_fee": {"value": copy.deepcopy(value), "span": fee_span,
            "pixel_region": copy.deepcopy(fee_region), "image_sha256": page["image_sha256"],
            "event_sha256": fee["review_event_sha256"], "locator": copy.deepcopy(fee["locator"])},
        "source_limits": copy.deepcopy(row["gaps"])}
