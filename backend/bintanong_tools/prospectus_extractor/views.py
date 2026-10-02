"""Derived views: term tree, prerequisite edges, review CSV."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any
from typing import Sequence
import csv
import json


def build_curriculum_by_term(courses: Sequence[dict[str, Any]]) -> dict[str, dict[str, list[dict[str, Any]]]]:
    tree: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for course in sorted(courses, key=lambda c: c.get("term_index", 99)):
        tree.setdefault(course["year_level"], {}).setdefault(course["semester"], []).append(course)
    return tree


def make_prerequisite_edges(courses: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    for course in courses:
        for prereq in course.get("prerequisites", []):
            edges.append({"from": prereq, "to": course["course_code"], "resolved": True})
        for token in course.get("prerequisites_unresolved", []):
            edges.append({"from": token, "to": course["course_code"], "resolved": False})
    return edges


def build_unlocks_map(courses: Sequence[dict[str, Any]]) -> dict[str, list[str]]:
    unlocks: dict[str, list[str]] = defaultdict(list)
    for course in courses:
        for prereq in course.get("prerequisites", []):
            unlocks[prereq].append(course["course_code"])
    return dict(unlocks)


def write_review_csv(courses: Sequence[dict[str, Any]], output_path: Path) -> None:
    """Human-reviewable flat table - the artefact a registrar can actually check."""
    fields = [
        "year_level", "semester", "course_code", "course_title", "units_total",
        "units_lecture", "units_lab", "prerequisites_resolved", "prerequisites_unresolved",
        "standing_requirements", "category", "elective_group", "prerequisites_raw",
        "title_raw", "footnote_marker", "table_index", "row_index", "column_group",
        "source_cell_ids", "page", "bbox", "resolution_method", "repair_id",
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for course in courses:
            source = course.get("_source", {})
            provenance = course.get("provenance", {})
            writer.writerow(
                {
                    "year_level": course.get("year_level", ""),
                    "semester": course.get("semester", ""),
                    "course_code": course.get("course_code", ""),
                    "course_title": course.get("course_title", ""),
                    "units_total": course.get("total_units", ""),
                    "units_lecture": course.get("lecture_units", ""),
                    "units_lab": course.get("lab_units", ""),
                    "prerequisites_resolved": ", ".join(course.get("prerequisites", [])),
                    "prerequisites_unresolved": ", ".join(course.get("prerequisites_unresolved", [])),
                    "standing_requirements": " | ".join(course.get("standing_requirements", [])),
                    "category": course.get("category", ""),
                    "elective_group": course.get("elective_group") or "",
                    "prerequisites_raw": course.get("prerequisites_raw", ""),
                    "title_raw": course.get("title_raw", ""),
                    "footnote_marker": course.get("footnote_marker") if course.get("footnote_marker") else "",
                    "table_index": source.get("table_index", ""),
                    "row_index": source.get("row_index", ""),
                    "column_group": source.get("column_group", ""),
                    "source_cell_ids": " | ".join(provenance.get("source_cell_ids", [])),
                    "page": provenance.get("page") if provenance.get("page") is not None else "",
                    "bbox": json.dumps(provenance.get("bbox"), ensure_ascii=False)
                    if provenance.get("bbox") is not None
                    else "",
                    "resolution_method": provenance.get("resolution_method", ""),
                    "repair_id": provenance.get("repair_id") or "",
                }
            )
