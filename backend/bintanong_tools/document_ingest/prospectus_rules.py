"""Checked prospectus cells to the existing pure, inactive rule candidate compiler."""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from ...bintanong_contracts.source import SourceSpan, canonical_text, check_span_binding
from ..prospectus_extractor.evidence import project_table_to_grid
from ..prospectus_extractor.layout import detect_column_groups
from ..prospectus_extractor.ledger import course_locator, same_value
from ..prospectus_extractor.loader import evidence_adapter
from ..prospectus_extractor.parse import parse_curriculum_evidence
from ..prospectus_extractor.rule_candidates import _review_decisions, build_rule_candidates
from ..prospectus_extractor.sections import (
    FieldCandidate, _assemble_section_candidates, _candidate_to_raw_course, build_curriculum_sections,
    tokenize_table,
)
from .bundle import load_candidate_bundle
from .prospectus import _captured_page_sizes


def _mapping(value, name):
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} must be a mapping")
    return value


def _ids(value):
    if (not isinstance(value, list) or any(not isinstance(v, str) or not v for v in value)
            or len(set(value)) != len(value)):
        raise ValueError("source_cell_ids must be unique nonempty text IDs")
    return value


def _source_claims(value, source):
    if isinstance(value, Mapping):
        for name, item in value.items():
            if name in {"version_id", "edition_id", "document_id", "namespace", "byte_sha256", "pdf_sha256"}:
                wanted = source.byte_sha256 if name == "pdf_sha256" else getattr(source, name)
                if item != wanted:
                    raise ValueError(f"field ownership {name} differs from registered source")
            _source_claims(item, source)
    elif isinstance(value, list):
        for item in value:
            _source_claims(item, source)


def _owners(evidence):
    """Recover FieldCandidates dropped by the parser's public projection, using its helpers."""
    parsed = parse_curriculum_evidence(evidence)
    owners = defaultdict(list)
    for table in evidence.tables:
        groups, _ = detect_column_groups(project_table_to_grid(table))
        if not groups:
            continue
        sections, _ = build_curriculum_sections(evidence, table, groups, tokenize_table(table, groups))
        for section in sections:
            for candidate in _assemble_section_candidates(evidence, table, groups, section, parsed):
                raw = _candidate_to_raw_course(candidate, evidence, parsed.footnotes)
                owners[(candidate.table_index, candidate.row_start, candidate.group_index)].append((candidate, raw))
    return owners


def _course_owner(course, owners, cells):
    provenance = _mapping(course.get("provenance", {}), "course provenance")
    location = _mapping(course.get("_source", {}), "course source")
    ids = _ids(provenance.get("source_cell_ids", []))
    supplied = provenance.get("source_cells", [])
    if not isinstance(supplied, list):
        raise ValueError("source_cells must be a list")
    supplied_ids = []
    for claim in supplied:
        claim = _mapping(claim, "source cell")
        _ids([claim.get("cell_id")])
        cell = cells.get(claim.get("cell_id"))
        if cell is None or not same_value(dict(claim), cell.as_evidence_dict()):
            raise ValueError("source cell differs from captured raw conversion")
        supplied_ids.append(cell.cell_id)
    _ids(supplied_ids)
    if any(cell_id not in cells for cell_id in ids):
        raise ValueError("unknown source cell")
    if location:
        if (set(location) != {"table_index", "row_index", "column_group"}
                or any(type(v) is not int or v < 0 for v in location.values())):
            raise ValueError("malformed course ownership locator")
        matches = owners.get((location["table_index"], location["row_index"], location["column_group"]), [])
        if not matches:
            raise ValueError("course ownership locator is foreign to the captured curriculum")
    else:
        return None, set()
    if len(matches) != 1:
        return None, set()
    owner, raw = matches[0]
    expected = raw["provenance"]
    if not (set(ids) | set(supplied_ids)) <= set(owner.source_cell_ids):
        raise ValueError("course claims a legitimate but unrelated source cell")
    for name in ("table_index", "page", "bbox"):
        if name in provenance and not same_value(provenance[name], expected[name]):
            raise ValueError(f"course provenance {name} differs from captured ownership")
    if provenance.get("resolution_method") != "deterministic" or provenance.get("repair_id") is not None:
        return None, set()
    return owner, set(ids) & set(supplied_ids)


def _field_spans(field, owner, allowed, cells, tables, source, sizes, *, allow_blank=False):
    if field is None or not field.evidence_cell_ids or not set(field.evidence_cell_ids) <= allowed:
        return []
    spans = []
    for cell_id in field.evidence_cell_ids:
        cell = cells[cell_id]
        if cell.table_index != owner.table_index:
            raise ValueError("field owner names a foreign table")
        if any(other.cell_id not in field.evidence_cell_ids and other.text
               and other.row_start < cell.row_end and other.row_end > cell.row_start
               and other.col_start < cell.col_end and other.col_end > cell.col_start
               for other in tables[cell.table_index].cells):
            return []
        box = cell.bbox
        if (box is None or box.page is None or not box.is_complete() or box.origin is None
                or (not cell.raw_text.strip() and not allow_blank)):
            return []
        if (source.byte_sha256, box.page) not in sizes:
            raise ValueError("field page is outside captured PDF geometry")
        span = SourceSpan.parse({
            "schema_version": SourceSpan.SCHEMA_VERSION, "byte_sha256": source.byte_sha256,
            "version_id": source.version_id, "page": box.page, "printed_page_label": None,
            "locator": {"kind": "table_cells", "table_index": cell.table_index,
                        "cell_ids": [cell_id], "item_ids": [], "ref": None},
            "text": cell.raw_text, "bbox": box.as_list(), "bbox_origin": box.origin,
            "page_size": sizes[(source.byte_sha256, box.page)],
            "extraction": {"source_kind": "docling-json", "resolution_method": "deterministic",
                           "repair_id": None, "ocr_confidence": None},
        })
        check_span_binding(span, source)
        spans.append(span)
    return spans


def _blank_review_locator(course, owner, allowed, cells, tables, source, sizes):
    if (owner.prerequisites is not None or set(owner.source_cell_ids) != allowed
            or canonical_text(course.get("prerequisites_raw")) != ""):
        return None
    table = tables[owner.table_index]
    groups, _ = detect_column_groups(project_table_to_grid(table))
    group = next(g for g in groups if g.index == owner.group_index)
    if group.prereq_idx is None:
        return None
    owned = [c for c in table.cells if any(c.overlaps(row, group.prereq_idx)
                                          for row in range(owner.row_start, owner.row_end))]
    if len(owned) != 1 or owned[0].raw_text.strip():
        return None
    field = FieldCandidate("", [owned[0].cell_id])
    # Validate blank-cell geometry for the review binding; never supply blank spans to the compiler.
    if _field_spans(field, owner, allowed | set(field.evidence_cell_ids), cells, tables,
                    source, sizes, allow_blank=True):
        return course_locator(course)
    return None


def prepare_rule_candidates(bundle_path: Path) -> dict[str, Any]:
    """Read a checked institutional prospectus; return review JSON without publication."""
    checked = load_candidate_bundle(bundle_path)
    if checked["document_kind"] != "prospectus_candidate":
        raise ValueError("rule handoff requires a prospectus_candidate bundle")
    payload = checked["domain_payload"]
    source = next(v for v in checked["source_register"] if v.version_id == checked["report"]["source_version"]["version_id"])
    conversion = checked["conversion"]
    sizes = _captured_page_sizes(conversion["metadata"], conversion["raw_docling"])
    evidence = evidence_adapter(conversion["raw_docling"])
    owners, cells = _owners(evidence), evidence.all_cells()
    tables = {t.table_index: t for t in evidence.tables}
    support = {}
    blank_locators = []
    for course in payload["courses"]:
        _source_claims(course, source)
        owner, allowed = _course_owner(course, owners, cells)
        fields = support.setdefault(course["course_code"], {})
        if owner is None:
            continue
        blank = _blank_review_locator(course, owner, allowed, cells, tables, source, sizes)
        if blank is not None:
            blank_locators.append(blank)
        for name, field in (("course_code", owner.code), ("course_title", owner.title),
                            ("units.total", owner.units), ("prerequisites_raw", owner.prerequisites),
                            ("year_level", owner.year_level), ("semester", owner.semester)):
            if name in {"year_level", "semester"} and (field is None or
                    canonical_text(course.get(name)) != canonical_text(" ".join(cells[i].raw_text for i in field.evidence_cell_ids))):
                continue
            # A plain unit cell prints the total; lecture/lab defaults are not independent source facts.
            spans = _field_spans(field, owner, allowed, cells, tables, source, sizes)
            if spans:
                fields[name] = spans
    review = payload.get("review_evidence")
    decisions = _review_decisions(review, source)
    if review is not None:
        bound_blank_ids = {e["entry_id"] for e in decisions.values()
                           if e["field"] == "prerequisites_raw" and e["disposition"] == "accepted"
                           and e["locator"] in blank_locators}
        review = {**review, "entries": [e for e in review["entries"]
                  if e.get("field") != "prerequisites_raw" or e.get("disposition") != "accepted"
                  or e.get("entry_id") in bound_blank_ids]}
    return build_rule_candidates(payload, source, support, review_evidence=review)
