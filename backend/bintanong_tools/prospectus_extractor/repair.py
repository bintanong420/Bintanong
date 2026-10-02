"""Evidence-constrained semantic repair validation."""

from __future__ import annotations

from typing import Any
from typing import Mapping
from typing import Sequence
import json
import re

from .text import clean_str, match_semester_labels, match_year_label, term_index
from .units import parse_units
from .grid import GridParseResult
from .evidence import ProspectusEvidence
from .sections import SemanticRepairProvider, _make_provenance


def _repair_packet_for_anomaly(
    anomaly: Mapping[str, Any], evidence: ProspectusEvidence, courses: Sequence[dict[str, Any]]
) -> dict[str, Any]:
    table_index = int(anomaly.get("table_index", 0))
    row = int(anomaly.get("row", 0))
    table = next((t for t in evidence.tables if t.table_index == table_index), None)
    cells = []
    if table:
        cells = [
            cell.as_evidence_dict()
            for cell in table.cells
            if max(0, row - 2) <= cell.row_start < min(table.num_rows, row + 3)
        ]
    candidate_id = anomaly.get("candidate_id")
    deterministic = next(
        (course for course in courses if course.get("_candidate_id") == candidate_id), {}
    )
    return {
        "repair_id": f"repair-{anomaly.get('id')}",
        "anomaly_id": anomaly.get("id"),
        "candidate_id": candidate_id,
        "table_index": table_index,
        "row_window": [max(0, row - 2), row + 2],
        "reason": [anomaly.get("type")],
        "cells": cells,
        "deterministic_candidate": {
            key: deterministic.get(key)
            for key in (
                "course_code",
                "course_title",
                "units",
                "prerequisites_raw",
                "year_level",
                "semester",
            )
            if key in deterministic
        },
        "contract": {
            "allowed_fields": [
                "course_code",
                "course_title",
                "units_raw",
                "prerequisites_raw",
                "year_level",
                "semester",
            ],
            "evidence_required_for_every_non_null_field": True,
            "external_knowledge_forbidden": True,
            "ambiguity_must_be_returned_instead_of_guessing": True,
        },
    }


def _normalised_contains(haystack: str, needle: str) -> bool:
    h = re.sub(r"[^A-Z0-9]", "", clean_str(haystack).upper())
    n = re.sub(r"[^A-Z0-9]", "", clean_str(needle).upper())
    return bool(n) and n in h


def validate_repair_decision(
    packet: Mapping[str, Any],
    decision: Mapping[str, Any],
    evidence: ProspectusEvidence,
) -> tuple[bool, list[str]]:
    """Prove that every proposed field is supported by cited source cells."""
    errors: list[str] = []
    if not isinstance(decision.get("ambiguous"), bool):
        errors.append("decision.ambiguous must be a boolean")
    fields = decision.get("fields")
    if not isinstance(fields, Mapping):
        errors.append("decision.fields must be an object")
        return False, errors
    allowed = set(packet.get("contract", {}).get("allowed_fields", []))
    all_cells = evidence.all_cells()
    packet_ids = {cell.get("cell_id") for cell in packet.get("cells", [])}
    for field_name, proposal in fields.items():
        if field_name not in allowed:
            errors.append(f"unsupported repair field: {field_name}")
            continue
        if not isinstance(proposal, Mapping):
            errors.append(f"{field_name} must be an object")
            continue
        value = proposal.get("value")
        cited = proposal.get("evidence")
        if value is None:
            continue
        if not isinstance(cited, list) or not cited:
            errors.append(f"{field_name} has no evidence cell IDs")
            continue
        invalid = [cell_id for cell_id in cited if cell_id not in all_cells or cell_id not in packet_ids]
        if invalid:
            errors.append(f"{field_name} cites cells outside the packet: {invalid}")
            continue
        combined = " ".join(all_cells[cell_id].text for cell_id in cited)
        if field_name == "year_level":
            if not any(match_year_label(all_cells[cell_id].text) == value for cell_id in cited):
                errors.append("year_level is not supported by cited structural evidence")
        elif field_name == "semester":
            labels = [
                label
                for cell_id in cited
                for _position, label in match_semester_labels(all_cells[cell_id].text)
            ]
            if value not in labels:
                errors.append("semester is not supported by cited structural evidence")
        elif not _normalised_contains(combined, str(value)):
            errors.append(f"{field_name} value is not present in cited source text")
        elif field_name == "prerequisites_raw":
            source_prefix = re.match(
                r"^\s*((?:FIRST|SECOND|THIRD|FOURTH|FIFTH)(?:\s+YEAR)?)\b",
                combined,
                re.IGNORECASE,
            )
            value_prefix = re.match(
                r"^\s*(?:FIRST|SECOND|THIRD|FOURTH|FIFTH)(?:\s+YEAR)?\b",
                str(value),
                re.IGNORECASE,
            )
            if source_prefix and not value_prefix:
                recorded = any(
                    isinstance(item, Mapping)
                    and clean_str(item.get("text", "")).upper()
                    == clean_str(source_prefix.group(1)).upper()
                    and item.get("source_cell") in cited
                    for item in decision.get("discarded_fragments", []) or []
                )
                if not recorded:
                    errors.append("removed structural prerequisite prefix was not recorded")

    for discarded in decision.get("discarded_fragments", []) or []:
        if not isinstance(discarded, Mapping):
            errors.append("discarded fragment must be an object")
            continue
        cell_id = discarded.get("source_cell")
        text = discarded.get("text")
        if cell_id not in all_cells or cell_id not in packet_ids:
            errors.append(f"discarded fragment cites invalid cell {cell_id}")
        elif not _normalised_contains(all_cells[cell_id].text, str(text or "")):
            errors.append("discarded fragment is absent from its source cell")
    return not errors, errors


def _apply_valid_repair(
    packet: Mapping[str, Any],
    decision: Mapping[str, Any],
    courses: list[dict[str, Any]],
    evidence: ProspectusEvidence,
) -> bool:
    candidate_id = packet.get("candidate_id")
    course = next((item for item in courses if item.get("_candidate_id") == candidate_id), None)
    if course is None:
        return False
    mapping = {
        "course_code": "course_code",
        "course_title": "course_title",
        "prerequisites_raw": "prerequisites_raw",
        "year_level": "year_level",
        "semester": "semester",
    }
    cited_ids: list[str] = []
    for field_name, proposal in decision.get("fields", {}).items():
        if not isinstance(proposal, Mapping) or proposal.get("value") is None:
            continue
        if field_name == "units_raw":
            course["units"] = parse_units(proposal["value"])
        elif field_name in mapping:
            course[mapping[field_name]] = clean_str(proposal["value"])
        cited_ids.extend(proposal.get("evidence", []))
    course["term_index"] = term_index(course.get("year_level") or "", course.get("semester") or "")
    existing = course.get("provenance", {}).get("source_cell_ids", [])
    provenance = _make_provenance(
        evidence,
        int(packet.get("table_index", 0)),
        [*existing, *cited_ids],
        "llm_repair",
        str(packet.get("repair_id")),
    )
    provenance["discarded_fragments"] = list(decision.get("discarded_fragments", []) or [])
    course["provenance"] = provenance
    return True


def apply_semantic_repairs(
    result: GridParseResult,
    evidence: ProspectusEvidence,
    repair_provider: SemanticRepairProvider | None,
) -> None:
    """Call a model only for anomaly packets; invalid output never reaches courses."""
    result.repair_packets = [
        _repair_packet_for_anomaly(anomaly, evidence, result.courses)
        for anomaly in result.anomalies
    ]
    if repair_provider is None:
        return

    resolved_anomaly_ids: set[str] = set()
    for packet in result.repair_packets:
        try:
            raw = repair_provider(packet)
            decision = json.loads(raw) if isinstance(raw, str) else dict(raw)
        except Exception as exc:
            result.invalid_repairs.append(
                {
                    "repair_id": packet["repair_id"],
                    "errors": [f"repair provider failed: {type(exc).__name__}: {exc}"],
                }
            )
            continue
        valid, errors = validate_repair_decision(packet, decision, evidence)
        if decision.get("ambiguous") is True:
            valid = False
            errors.append("repair model returned ambiguous=true")
        if valid and _apply_valid_repair(packet, decision, result.courses, evidence):
            result.repairs.append(
                {
                    "repair_id": packet["repair_id"],
                    "anomaly_id": packet["anomaly_id"],
                    "status": "accepted",
                    "decision": decision,
                }
            )
            resolved_anomaly_ids.add(str(packet["anomaly_id"]))
        else:
            if valid:
                errors.append("repair target was not an existing deterministic candidate")
            result.invalid_repairs.append(
                {"repair_id": packet["repair_id"], "errors": errors, "decision": decision}
            )
    if resolved_anomaly_ids:
        result.anomalies = [
            anomaly
            for anomaly in result.anomalies
            if str(anomaly.get("id")) not in resolved_anomaly_ids
        ]
