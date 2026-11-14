"""Course finalisation, classification and elective tracks."""

from __future__ import annotations

from collections import Counter
from typing import Any
from typing import Iterable
from typing import Mapping
from typing import Sequence
import re

from .common import RICH_AVAILABLE

if RICH_AVAILABLE:
    from .common import track
from .text import clean_str, norm_key, relaxed_key
from .units import parse_units
from .prerequisites import CodeIndex, resolve_prerequisites


ELECTIVE_OPTION = re.compile(
    r"^([A-Za-z][A-Za-z\.\s]{0,20}?Elect(?:ive)?\.?\s*(\d{1,2})\s*/\s*[A-Za-z0-9]+)\s*[\.\)]\s*(.+)$",
    re.IGNORECASE,
)


def sort_courses(courses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        courses,
        key=lambda c: (
            c.get("term_index", 99),
            c.get("_source", {}).get("table_index", 0),
            c.get("_source", {}).get("column_group", 0),
            c.get("_source", {}).get("row_index", 0),
        ),
    )


def classify_course(code: str, title: str) -> dict[str, Any]:
    """Flag electives, GE courses, NSTP/PE and thesis/practicum rows."""
    upper_code = clean_str(code).upper()
    upper_title = clean_str(title).upper()
    is_elective = bool(re.match(r"^(?:GE[- :]+)?(?:[A-Z]{1,8}\\s+)?ELECT(?:IVE)?(?:\\s*[:.-]?\\s*\\d{1,2})?(?:/L)?$", upper_code, re.IGNORECASE)) or bool(re.search(r"\\bELECTIVE\\b", upper_title))
    if upper_code.startswith("GE"):
        category = "General Education"
    elif upper_code.startswith(("NSTP", "PATH", "CWTS", "ROTC")):
        category = "NSTP / PATHFit"
    elif "THESIS" in upper_code or "PRACTICUM" in upper_code or "THESIS" in upper_title:
        category = "Capstone / Practicum"
    else:
        category = "Core / Major"
    return {
        "is_elective": is_elective,
        "elective_kind": ("General Education" if is_elective and upper_code.startswith("GE") else "Major")
        if is_elective
        else None,
        "category": category,
    }


def finalize_courses(
    courses: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], CodeIndex, list[dict[str, Any]]]:
    """Resolve prerequisites against the document's own codes and add flat fields."""
    index = CodeIndex(c["course_code"] for c in courses)
    finalized: list[dict[str, Any]] = []

    for course in courses:
        resolution = resolve_prerequisites(
            course.get("prerequisites_raw", ""),
            index,
            current_course_code=course.get("course_code", ""),
        )
        units = course.get("units") or parse_units("")
        classification = classify_course(course["course_code"], course["course_title"])

        record = dict(course)
        record.pop("_candidate_id", None)
        record.update(
            {
                "code": course["course_code"],
                "title": course["course_title"],
                "units": units,
                "total_units": units.get("total"),
                "lecture_units": units.get("lecture"),
                "lab_units": units.get("lab"),
                "prerequisites": resolution.resolved,
                "prerequisites_unresolved": resolution.unresolved,
                "standing_requirements": resolution.standing_rules,
                "elective_group": None,
                **classification,
            }
        )
        finalized.append(record)

    finalized = sort_courses(finalized)

    counts = Counter(c["course_code"] for c in finalized)
    duplicates = [
        {
            "course_code": code,
            "occurrences": [
                {"year_level": c["year_level"], "semester": c["semester"], "source": c["_source"]}
                for c in finalized
                if c["course_code"] == code
            ],
        }
        for code, count in counts.items()
        if count > 1
    ]
    return finalized, index, duplicates


def _iter_text_pairs(text_items: Sequence[Any]) -> Iterable[tuple[str, str]]:
    for item in text_items:
        if isinstance(item, Mapping):
            yield str(item.get("label", "text")), clean_str(item.get("text", ""))
        elif isinstance(item, (tuple, list)) and len(item) >= 2:
            yield str(item[0]), clean_str(item[1])


def parse_elective_tracks(text_items: Sequence[Any]) -> list[dict[str, Any]]:
    """Collect elective pools such as 'CS Elect 4/La. ...' into grouped options.

    Grouping keys off the elective number inside each option code, so a missing
    or reordered section header can no longer scramble the pools (v1 relied on
    header ordering and auto-created groups mid-stream).
    """
    grouped: dict[str, list[dict[str, Any]]] = {}
    order: list[str] = []

    for item in text_items:
        item_id = item.get("item_id") if isinstance(item, Mapping) else None
        for _label, text in _iter_text_pairs([item]):
            line = clean_str(text)
            if not line:
                continue
            for candidate in re.split(r"(?<=[a-z\)])\s{2,}", line):
                match = ELECTIVE_OPTION.match(clean_str(candidate))
                if not match:
                    continue
                option_code = clean_str(match.group(1))
                number = match.group(2)
                title = clean_str(match.group(3))
                prefix_match = re.match(r"^([A-Za-z]+)", option_code)
                prefix = prefix_match.group(1).upper() if prefix_match else "CS"
                group_name = f"{prefix} Elective {number}"
                if group_name not in grouped:
                    grouped[group_name] = []
                    order.append(group_name)
                if not any(o["course_code"] == option_code for o in grouped[group_name]):
                    grouped[group_name].append({"course_code": option_code, "course_title": title, "source_item_id": item_id})

    return [
        {
            "group": name,
            "elective_number": int(re.search(r"(\d{1,2})", name).group(1)),
            "options": grouped[name],
        }
        for name in order
        if grouped[name]
    ]


def link_elective_tracks(
    courses: list[dict[str, Any]], tracks: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Attach each elective pool to the curriculum row that consumes it."""
    for track in tracks:
        number = track["elective_number"]
        prefix = track["group"].split()[0]
        wanted = {norm_key(f"{prefix} Elect {number}"), norm_key(f"{prefix} Elect {number} L"),
                  norm_key(f"{prefix} Elective {number}")}
        slots: list[str] = []
        for course in courses:
            key = norm_key(course["course_code"])
            if key in wanted or relaxed_key(course["course_code"]) in {norm_key(f"{prefix} Elect {number}")}:
                course["elective_group"] = track["group"]
                course["elective_option_count"] = len(track["options"])
                slots.append(course["course_code"])
        track["curriculum_slots"] = slots
    return tracks
