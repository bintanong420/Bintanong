"""Audit that fails loudly instead of emitting plausible garbage."""

from __future__ import annotations

from collections import defaultdict
from typing import Any
from typing import Sequence
import re

from .text import YEAR_ORDER, clean_str, match_semester_labels, match_year_label, norm_key, term_index
from .prerequisites import is_standing_rule
from .grid import GridParseResult


def find_prerequisite_cycles(courses: Sequence[dict[str, Any]]) -> list[list[str]]:
    # Accumulate per code: a duplicated course row must not overwrite the edges
    # contributed by its twin, or a real cycle can hide behind the duplicate.
    graph: dict[str, list[str]] = defaultdict(list)
    for course in courses:
        code = course["course_code"]
        for prereq in course.get("prerequisites", []):
            if prereq != code and norm_key(prereq) != norm_key(code):
                if prereq not in graph[code]:
                    graph[code].append(prereq)
        graph.setdefault(code, graph[code])
    cycles: list[list[str]] = []
    state: dict[str, int] = defaultdict(int)  # 0 unvisited, 1 in stack, 2 done
    stack: list[str] = []

    def visit(node: str) -> None:
        state[node] = 1
        stack.append(node)
        for neighbour in graph.get(node, []):
            if neighbour not in graph:
                continue
            if state[neighbour] == 0:
                visit(neighbour)
            elif state[neighbour] == 1:
                cycle = stack[stack.index(neighbour) :] + [neighbour]
                if cycle not in cycles:
                    cycles.append(cycle)
        stack.pop()
        state[node] = 2

    for code in list(graph.keys()):
        if state[code] == 0:
            visit(code)
    return cycles


def build_audit(
    courses: Sequence[dict[str, Any]],
    parse: GridParseResult,
    metadata: dict[str, Any],
    duplicates: Sequence[dict[str, Any]],
    extra_warnings: Sequence[str] = (),
) -> dict[str, Any]:
    """Cross-check the extraction against the document's own printed totals."""
    errors: list[str] = []
    warnings: list[str] = [*parse.warnings, *extra_warnings]
    structural = [w for w in warnings if clean_str(w).startswith("STRUCTURAL_ERROR:")]
    if structural:
        errors.extend(structural)
        warnings = [w for w in warnings if w not in structural]

    years = sorted(
        {c.get("year_level") for c in courses if c.get("year_level")},
        key=lambda y: (YEAR_ORDER.get(y, 99), y),
    )
    terms = sorted(
        {
            (c.get("year_level"), c.get("semester"))
            for c in courses
            if c.get("year_level") and c.get("semester")
        },
        # The text keys break ties (Summer and Mid-Year share an index) so the order never depends on set order.
        key=lambda t: (term_index(t[0] or "", t[1] or ""), t[0] or "", t[1] or ""),
    )
    years_present = {c.get("year_level") for c in courses}

    if not courses:
        errors.append("No courses extracted.")
    elif len(years_present) <= 1 and len(courses) >= 20:
        errors.append(
            f"All {len(courses)} courses landed in '{list(years_present)[0]}' - the year banner rows were not "
            "recognised. Run with --dump-grid and check the banner detection."
        )
    elif len(terms) < 2 and len(courses) >= 20:
        errors.append("All courses landed in a single term; semester banners were not recognised.")

    missing_year = [c.get("course_code") for c in courses if not c.get("year_level")]
    missing_semester = [c.get("course_code") for c in courses if not c.get("semester")]
    if missing_year:
        errors.append(f"{len(missing_year)} course(s) have no verified year: {missing_year}.")
    if missing_semester:
        errors.append(
            f"{len(missing_semester)} course(s) have no verified semester: {missing_semester}."
        )

    computed_terms: dict[tuple[str, str], int] = defaultdict(int)
    for course in courses:
        if course.get("year_level") and course.get("semester"):
            computed_terms[(course["year_level"], course["semester"])] += course.get("total_units") or 0

    term_audit: list[dict[str, Any]] = []
    for term in terms:
        declared = parse.declared_term_units.get(term)
        computed = computed_terms.get(term, 0)
        matches = declared is None or declared == computed
        term_audit.append(
            {
                "year_level": term[0],
                "semester": term[1],
                "declared_units": declared,
                "computed_units": computed,
                "course_count": sum(
                    1 for c in courses if (c["year_level"], c["semester"]) == term
                ),
                "matches": matches,
            }
        )
        if not matches:
            errors.append(
                f"Unit checksum mismatch for {term[0]} {term[1]}: document says {declared}, "
                f"extracted {computed}."
            )

    for term, declared in parse.declared_term_units.items():
        if term not in computed_terms:
            errors.append(
                f"Document declares a total for {term[0]} {term[1]} but no courses were extracted there."
            )

    computed_total = sum(c.get("total_units") or 0 for c in courses)
    declared_total = parse.declared_grand_total
    if declared_total is not None and declared_total != computed_total:
        errors.append(
            f"Grand total mismatch: document says {declared_total} units, extracted {computed_total}."
        )

    unresolved = [
        {"course_code": c["course_code"], "token": token, "raw": c.get("prerequisites_raw", "")}
        for c in courses
        for token in c.get("prerequisites_unresolved", [])
    ]
    if unresolved:
        warnings.append(
            f"{len(unresolved)} prerequisite token(s) could not be matched to a course code in this "
            "document; see unresolved_prerequisites."
        )

    ordering: list[dict[str, Any]] = []
    positions = {c["course_code"]: c.get("term_index", 99) for c in courses}
    for course in courses:
        for prereq in course.get("prerequisites", []):
            if prereq in positions and positions[prereq] >= course.get("term_index", 99):
                ordering.append(
                    {
                        "course_code": course["course_code"],
                        "course_term": f"{course['year_level']} {course['semester']}",
                        "prerequisite": prereq,
                        "prerequisite_term": next(
                            f"{c['year_level']} {c['semester']}"
                            for c in courses
                            if c["course_code"] == prereq
                        ),
                    }
                )
    if ordering:
        warnings.append(
            f"{len(ordering)} prerequisite(s) are scheduled at or after the course that requires them."
        )

    cycles = find_prerequisite_cycles(courses)
    if cycles:
        errors.append(f"Prerequisite graph contains {len(cycles)} cycle(s): {cycles}.")

    missing_units = [c["course_code"] for c in courses if c.get("total_units") is None]
    if missing_units:
        errors.append(f"{len(missing_units)} course(s) have no parsed units: {missing_units}.")

    if duplicates:
        errors.append(
            f"{len(duplicates)} course code(s) appear more than once: "
            f"{[d['course_code'] for d in duplicates]}."
        )

    if parse.unclaimed_course_candidates:
        errors.append(
            f"{len(parse.unclaimed_course_candidates)} high-confidence source course code(s) "
            "were not claimed by the parser."
        )

    if parse.anomalies:
        errors.append(
            f"{len(parse.anomalies)} unresolved structural ambiguity/anomaly item(s) remain; "
            "see audit.structural_anomalies."
        )
        if any(item.get("type") == "missing_year_marker" for item in parse.anomalies) and any(
            item.get("type") == "unclaimed_course_candidate" for item in parse.anomalies
        ):
            errors.append(
                "Course rows started before any year banner; they were left unclaimed rather than guessed."
            )

    if parse.invalid_repairs:
        errors.append(
            f"{len(parse.invalid_repairs)} semantic repair result(s) failed evidence validation."
        )

    invalid_provenance: list[dict[str, Any]] = []
    unhighlightable: list[str] = []
    for course in courses:
        provenance = course.get("provenance") or {}
        if not provenance.get("valid") or not provenance.get("source_cell_ids"):
            invalid_provenance.append(
                {"course_code": course.get("course_code"), "provenance": provenance}
            )
        elif not provenance.get("highlightable"):
            unhighlightable.append(course.get("course_code"))
    if invalid_provenance:
        errors.append(
            f"{len(invalid_provenance)} course(s) have invalid source-cell provenance."
        )
    if unhighlightable:
        warnings.append(
            f"{len(unhighlightable)} course(s) have source cells but no page bbox; "
            "viewer highlighting is unavailable for those rows."
        )

    contamination: list[dict[str, str]] = []
    leading_bleed = re.compile(
        r"^(?:FIRST|SECOND|THIRD|FOURTH|FIFTH)(?:\s+YEAR)?\s+"
        r"(?=[A-Z]{1,8}(?:[\s-]+[A-Z]{1,6})?[\s-]*\d)",
        re.IGNORECASE,
    )
    for course in courses:
        for field_name in ("course_code", "course_title", "prerequisites_raw"):
            value = clean_str(course.get(field_name, ""))
            if not value:
                continue
            if field_name == "prerequisites_raw" and is_standing_rule(value):
                continue
            contaminated = bool(match_year_label(value) or match_semester_labels(value))
            contaminated = contaminated or bool(leading_bleed.search(value))
            if contaminated:
                contamination.append(
                    {
                        "course_code": course.get("course_code", ""),
                        "field": field_name,
                        "value": value,
                    }
                )
    if contamination:
        errors.append(
            f"{len(contamination)} canonical course field(s) contain structural marker contamination."
        )

    schema_errors: list[str] = []
    required_fields = ("course_code", "course_title", "units", "provenance")
    for index, course in enumerate(courses):
        for field_name in required_fields:
            if field_name not in course:
                schema_errors.append(f"courses[{index}] is missing {field_name}")
    if schema_errors:
        errors.append(f"Canonical course schema has {len(schema_errors)} error(s).")

    for key in ("program_name", "degree", "effective_school_year", "college_code"):
        if not metadata.get(key):
            warnings.append(f"Metadata field '{key}' is null.")

    status = "error" if errors else ("warn" if warnings else "ok")
    return {
        "status": status,
        "promotion_status": "REVIEW_REQUIRED" if errors else "VERIFIED",
        "errors": errors,
        "warnings": warnings,
        "total_courses": len(courses),
        "years_detected": years,
        "terms_detected": [f"{y} {s}" for y, s in terms],
        "term_unit_audit": term_audit,
        "declared_total_units": declared_total,
        "computed_total_units": computed_total,
        "total_units_match": None if declared_total is None else declared_total == computed_total,
        "unresolved_prerequisites": unresolved,
        "prerequisite_ordering_violations": ordering,
        "prerequisite_cycles": cycles,
        "duplicate_course_codes": duplicates,
        "courses_without_units": missing_units,
        "courses_without_verified_year": missing_year,
        "courses_without_verified_semester": missing_semester,
        "source_course_candidates": parse.source_course_candidates,
        "unclaimed_course_candidates": parse.unclaimed_course_candidates,
        "structural_anomalies": parse.anomalies,
        "repair_packets": parse.repair_packets,
        "repairs": parse.repairs,
        "invalid_repairs": parse.invalid_repairs,
        "invalid_provenance": invalid_provenance,
        "unhighlightable_courses": unhighlightable,
        "structural_contamination": contamination,
        "schema_errors": schema_errors,
        "footnotes": parse.footnotes.audit(),
        "table_layout": parse.layout,
        "curriculum_sections": parse.sections,
    }
