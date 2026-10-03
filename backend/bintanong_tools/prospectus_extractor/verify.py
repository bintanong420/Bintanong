"""Year/semester verifier: per-section flags, fix proposals and a health status for one candidate.

Reads a candidate payload (and, when given, the PDF text layer) and groups the courses into
year x semester sections in printed order. Nothing here changes a value. A section is:
  clean    no flag above `info`
  review   only `warn` flags (a prerequisite order, a title or code not found in the PDF text)
  broken   at least one `error` flag (banner text in a field, printed total mismatch, a course in
           two terms or none, a printed code no course claimed)
Flag kinds: banner_leak, unit_total, code_not_in_pdf, title_not_in_pdf, duplicate_course, no_term,
prereq_order, unclaimed_code, audit_anomaly (and `banner_in_cell`, info only).
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from .prerequisites import is_standing_rule
from .text import SEMESTER_ORDER, YEAR_ORDER, clean_str, has_banner_text, norm_key, term_index

ERROR, WARN, INFO = "error", "warn", "info"
NO_TERM, UNPLACED = "SN", "SU"
EMPTY_DECLARED = re.compile(
    r"Document declares a total for (\d\w\w Year) (.+?) but no courses were extracted there\."
)


@dataclass(frozen=True)
class Flag:
    kind: str
    severity: str
    message: str
    field: str | None = None


@dataclass
class Row:
    rid: str
    course: int | None = None   # index into payload["courses"]; None for an unclaimed printed code
    item: dict | None = None    # the unclaimed printed code: source, code, page, bbox, cell_ids, snippet
    flags: list[Flag] = field(default_factory=list)
    fixes: list[tuple[str, Any]] = field(default_factory=list)   # (letter, Fix)

    def worst(self) -> str | None:
        severities = {f.severity for f in self.flags}
        return ERROR if ERROR in severities else WARN if WARN in severities else None


@dataclass
class Section:
    sid: str
    year: str | None
    semester: str | None
    rows: list[Row] = field(default_factory=list)
    declared: int | None = None
    computed: int = 0
    flags: list[Flag] = field(default_factory=list)   # section-level: unit_total
    health: str = "clean"

    @property
    def title(self) -> str:
        if self.sid == UNPLACED:
            return "Unplaced printed codes"
        if self.sid == NO_TERM:
            return "No year or semester"
        return f"{self.year} - {self.semester}"


@dataclass
class Verification:
    sections: list[Section]
    pdf_checked: bool
    health: str

    def counts(self) -> dict[str, int]:
        """error and warn flags by kind, for comparing two runs of the extractor."""
        out: Counter = Counter()
        for section in self.sections:
            for flag in section.flags + [f for row in section.rows for f in row.flags]:
                if flag.severity != INFO:
                    out[flag.kind] += 1
        return dict(sorted(out.items()))


def own_role_cells(course: Mapping[str, Any], layout: Sequence[Mapping[str, Any]], evidence_ids: set[str]) -> dict[str, list]:
    """The course's own single-column cells by role. Section banner cells ride along in every
    course's provenance; they are left out unless they are also this course's own row cell
    (BS Computer Science t0-c9 is both the semester banner and the title of CS 1)."""
    src = course.get("_source") or {}
    table = next((t for t in layout if t.get("table_index") == src.get("table_index")), None)
    group = next((g for g in (table or {}).get("column_groups") or [] if g.get("index") == src.get("column_group")), None)
    roles: dict[str, list] = {"code": [], "title": [], "unit": [], "prereq": []}
    if not group:
        return roles
    by_col = {group.get(f"{r}_idx"): r for r in roles if group.get(f"{r}_idx") is not None}
    row = src.get("row_index")
    for cell in (course.get("provenance") or {}).get("source_cells") or []:
        if cell.get("col_end", 0) - cell.get("col_start", 0) != 1 or cell.get("col_start") not in by_col:
            continue
        on_row = row is not None and cell.get("row_start", -1) <= row < cell.get("row_end", -1)
        if cell.get("cell_id") in evidence_ids and not on_row:
            continue
        roles[by_col[cell["col_start"]]].append(cell)
    return roles


def _term_of(course: Mapping[str, Any]) -> int:
    return course.get("term_index") or term_index(course.get("year_level") or "", course.get("semester") or "")


def _course_flags(index, course, ctx) -> list[Flag]:
    flags: list[Flag] = []
    roles = own_role_cells(course, ctx["layout"], ctx["evidence_ids"])
    for name in ("course_code", "course_title", "prerequisites_raw"):
        value = clean_str(course.get(name))
        if not value or (name == "prerequisites_raw" and is_standing_rule(value)):
            continue
        if has_banner_text(value):
            flags.append(Flag("banner_leak", ERROR, f'{name} holds banner text: "{value}"', name))
    for role, name in (("code", "course_code"), ("title", "course_title")):
        for cell in roles[role]:
            if has_banner_text(cell.get("text") or "") and not has_banner_text(course.get(name) or ""):
                flags.append(Flag("banner_in_cell", INFO, f'cell {cell["cell_id"]} carried banner text; the parser removed it from the {role}', name))
    year, semester = course.get("year_level"), course.get("semester")
    if not year or not semester:
        flags.append(Flag("no_term", ERROR, "no verified year or semester"))
    key = norm_key(course.get("course_code") or "")
    if ctx["code_count"][key] > 1:
        others = sorted({f"{o.get('year_level')} {o.get('semester')}" for i, o in enumerate(ctx["courses"])
                         if i != index and norm_key(o.get("course_code") or "") == key})
        flags.append(Flag("duplicate_course", ERROR, f"code appears again in: {', '.join(others)}", "course_code"))
    elif year and semester:
        here = _term_of(course)
        for prereq in course.get("prerequisites") or []:
            there = ctx["positions"].get(prereq)
            if there is not None and there >= here:
                flags.append(Flag("prereq_order", WARN, f"prerequisite {prereq} is in the same or a later term", "prerequisites_raw"))
    return flags


def _health(section: Section) -> str:
    severities = {f.severity for f in section.flags} | {f.severity for r in section.rows for f in r.flags}
    return "broken" if ERROR in severities else "review" if WARN in severities else "clean"


def _overall(sections: Sequence[Section]) -> str:
    """clean | warnings_only | mixed | broken. Broken: most sections broken, or fewer than two term sections."""
    terms = [s for s in sections if s.sid not in (NO_TERM, UNPLACED)]
    broken = sum(s.health == "broken" for s in sections)
    if len(terms) < 2 or broken * 2 > len(sections):
        return "broken"
    if all(s.health == "clean" for s in sections):
        return "clean"
    return "mixed" if broken else "warnings_only"


def verify_candidate(payload: Mapping[str, Any]) -> Verification:
    courses = payload.get("courses") or []
    audit = payload.get("audit") or {}
    layout = audit.get("table_layout") or []
    evidence_ids = {i for s in audit.get("curriculum_sections") or [] for i in s.get("evidence_cells") or []}
    code_count = Counter(norm_key(c.get("course_code") or "") for c in courses)
    ctx = {
        "courses": courses, "layout": layout, "evidence_ids": evidence_ids,
        "code_count": code_count, "codes": [c.get("course_code") or "" for c in courses],
        "positions": {c.get("course_code"): _term_of(c) for c in courses
                      if code_count[norm_key(c.get("course_code") or "")] == 1 and c.get("year_level") and c.get("semester")},
    }
    declared = {(t["year_level"], t["semester"]): t.get("declared_units") for t in audit.get("term_unit_audit") or []}
    keys = {(c.get("year_level"), c.get("semester")) for c in courses if c.get("year_level") and c.get("semester")}
    empty = [(y, s) for e in audit.get("errors") or [] if (m := EMPTY_DECLARED.search(e)) for y, s in [m.groups()]]
    keys |= {t for t in empty if t[0] in YEAR_ORDER and t[1] in SEMESTER_ORDER}
    sections = [Section(f"S{n}", y, s, declared=declared.get((y, s)))
                for n, (y, s) in enumerate(sorted(keys, key=lambda t: term_index(*t)), 1)]
    by_term = {(s.year, s.semester): s for s in sections}
    loose_section = Section(NO_TERM, None, None)
    for index, course in enumerate(courses):
        section = by_term.get((course.get("year_level"), course.get("semester"))) or loose_section
        row = Row(f"{section.sid}-{len(section.rows) + 1:02d}", course=index)
        row.flags = _course_flags(index, course, ctx)
        section.rows.append(row)
        section.computed += course.get("total_units") or 0
    for section in sections:
        if (section.year, section.semester) in empty and not section.rows:
            section.flags.append(Flag("unit_total", ERROR, "a printed total exists for this term but no courses were extracted"))
        elif section.declared is not None and section.declared != section.computed:
            section.flags.append(Flag("unit_total", ERROR, f"printed total {section.declared}, extracted {section.computed} ({section.computed - section.declared:+d})"))
    sections += [s for s in (loose_section,) if s.rows]
    for section in sections:
        section.health = _health(section)
    return Verification(sections, False, _overall(sections))
