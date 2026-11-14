"""Complete candidate accounting, with pending authority and explicit review gaps."""
from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from ...bintanong_contracts.source import Chunk, check_chunk_binding
from .policy_chunks import PolicyChunkResult, build_policy_chunks
from .policy_text import PolicyCandidates
from .procedure_text import ProcedureCandidates
from .register import load_pending_register


def build_ingestion_report(candidates: PolicyCandidates | ProcedureCandidates, result: PolicyChunkResult, *,
                           conversion_metadata: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Refuse incomplete/mismatched caller results; completeness concerns accounting only."""
    candidates.check_invariants()
    version = load_pending_register([candidates.version])[0]
    if not isinstance(result, PolicyChunkResult):
        raise ValueError("expected a governed chunk result")
    for chunk in result.chunks:
        parsed = Chunk.parse(chunk.model_dump(mode="json"))
        check_chunk_binding(parsed, version)
    expected = build_policy_chunks(candidates, token_cap=result.token_cap)
    if result.as_dict() != expected.as_dict():
        raise ValueError("chunk result mismatches candidates or has incomplete accounting")
    metadata = json.loads(json.dumps(dict(conversion_metadata or {}), allow_nan=False))
    for key in ("source_sha256", "pdf_sha256"):
        if key in metadata and metadata[key] != version.byte_sha256:
            raise ValueError("conversion metadata names different source bytes")
    settings = metadata.get("conversion_settings", {})
    if not isinstance(settings, dict):
        raise ValueError("conversion settings must be an object")
    payload = candidates.as_dict()
    pdf = candidates if isinstance(candidates, PolicyCandidates) else candidates.pdf
    pdf_payload = pdf.as_dict() if pdf is not None else None
    units = pdf_payload["units"] if pdf_payload is not None else payload["pptx_units"]
    evidence = {u["item_id"]: u for u in units}
    tables = payload.get("tables", [])
    evidence.update({t["table_id"]: t for t in tables})
    rejections = [{"candidate_id": r.candidate_id, "reason": r.reason,
                   "evidence": evidence[r.candidate_id]} for r in result.rejections]
    item_omissions = pdf_payload["item_omissions"] if pdf_payload is not None else []
    page_omissions = pdf_payload["page_omissions"] if pdf_payload is not None else []
    omitted_pages = {o["page"] for o in page_omissions}
    covered_pages = {p for u in units for p in u.get("pages", [])}
    covered_pages.update(p for o in item_omissions for p in o["pages"])
    covered_pages.update(s.page for c in result.chunks for s in c.spans)
    labels: dict[int, set[str]] = {}
    if pdf is not None:
        for unit in pdf.units:
            for span in unit.spans:
                if span.printed_page_label is not None:
                    labels.setdefault(span.page, set()).add(span.printed_page_label)
    for chunk in result.chunks:
        for span in chunk.spans:
            if span.printed_page_label is not None:
                labels.setdefault(span.page, set()).add(span.printed_page_label)
    conflicts = [{"physical_page": p, "reason": "conflicting_printed_page_labels", "labels": sorted(values)}
                 for p, values in sorted(labels.items()) if len(values) > 1]
    page_map = []
    for page in range(1, pdf.page_count + 1 if pdf is not None else 1):
        values = labels.get(page, set())
        if page not in covered_pages and page not in omitted_pages:
            raise ValueError("physical page accounting is incomplete")
        page_map.append({"physical_page": page,
                         "printed_page_label": next(iter(values)) if len(values) == 1 else None,
                         "coverage": "covered" if page in covered_pages else "omitted"})
    item_rejected = sum(r.candidate_id.startswith("text-") for r in result.rejections)
    table_rejected = sum(r.candidate_id.startswith("table-") for r in result.rejections)
    item_ids = [c.candidate_id for c in result.item_coverage] + [r.candidate_id for r in result.rejections
        if r.candidate_id.startswith("text-")] + [o["item_id"] for o in item_omissions]
    table_ids = [c.candidate_id for c in result.table_coverage] + [r.candidate_id for r in result.rejections
                                                                             if r.candidate_id.startswith("table-")]
    raw_tables = len(tables)
    if (len(item_ids) != candidates.raw_item_count or set(item_ids) != {f"text-{i}" for i in range(candidates.raw_item_count)}
            or len(table_ids) != raw_tables or set(table_ids) != {f"table-{i}" for i in range(raw_tables)}):
        raise ValueError("every raw item/table must occur in exactly one accounting category")
    needs = ["source_verification_pending", "content_review_pending", "scope_issuer_effectivity_pending",
             "estimated_tokens_only", "conflicts_not_assessed"]
    if not metadata.get("conversion_identity"):
        needs.append("conversion_identity_not_supplied")
    if rejections or item_omissions or page_omissions:
        needs.append("extraction_findings_require_review")
    return {"accounting_complete": True, "source_version": version.model_dump(mode="json"),
            "source_sha256": version.byte_sha256, "source_verification": "pending",
            "content_review": "pending", "approval_id": None,
            "classification": payload.get("classification", "policy_candidate"),
            "source_format": payload.get("source_format", "pdf"), "conversion": metadata,
            "tool_versions": settings.get("versions", {}), "conversion_settings": settings,
            "page_map": page_map, "counts": {"raw_items": candidates.raw_item_count,
                "covered_items": len(result.item_coverage), "rejected_items": item_rejected,
                "omitted_items": len(item_omissions), "raw_tables": raw_tables,
                "emitted_tables": len(result.table_coverage), "rejected_tables": table_rejected,
                "chunks": len(result.chunks)},
            "item_coverage": result.as_dict()["item_coverage"],
            "table_coverage": result.as_dict()["table_coverage"], "rejections": rejections,
            "item_omissions": item_omissions, "page_omissions": page_omissions,
            "conflicts": conflicts, "review_needs": needs}
