"""Year/semester verifier: per-section flags, fix proposals and a health status for one candidate.

Reads a candidate payload (and, when given, the PDF text layer) and groups the courses into
year x semester sections in printed order. Nothing here changes a value. A section is:
  clean    no flag above `info`
  review   only `warn` flags (a prerequisite order, a title or code not found in the PDF text)
  broken   at least one `error` flag (banner text in a field, printed total mismatch, a course in
           two terms or none, a printed code no course claimed)
Flag kinds: banner_leak, unit_total, code_not_in_pdf, title_not_in_pdf, duplicate_course, no_term,
prereq_order, unclaimed_code, audit_anomaly, term_mismatch (warn: the course's own cell opens with a banner for\nanother term; a move_term proposal exists) (and `banner_in_cell`, info only). banner_leak is an error when\nthe banner words are printed in a banner cell of the course's table, a warn when they are not (a title such\nas "SUMMER INTERNSHIP" that only looks like a banner).
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from .course_checks import PdfPage, check_course_pdf
from .fixes import banner_confirmed, banner_words, propose_fixes
from .placement import attach, unclaimed_items
from .prerequisites import is_standing_rule
from .text import SEMESTER_ORDER, YEAR_ORDER, clean_str, has_banner_text, is_banner_text, norm_key, term_index

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


def _regions(sections: Sequence[Section], courses: Sequence[Mapping[str, Any]], layout, evidence_ids) -> dict:
    """sid -> page -> [left, top, right, bottom]. Horizontal extent from the course's own cells
    (so the two semesters of one year do not overlap); the top includes the section banner."""
    out: dict[str, dict[int, list[float]]] = {}
    for section in sections:
        for row in section.rows:
            if row.course is None:
                continue
            course = courses[row.course]
            own = [c for cells in own_role_cells(course, layout, evidence_ids).values() for c in cells if c.get("bbox")]
            allb = [c["bbox"] for c in (course.get("provenance") or {}).get("source_cells") or [] if c.get("bbox")]
            page = (course.get("provenance") or {}).get("page")
            if not own or page is None:
                continue
            left, right = min(c["bbox"][0] for c in own), max(c["bbox"][2] for c in own)
            top, bottom = min(b[1] for b in allb), max(b[3] for b in allb)
            box = out.setdefault(section.sid, {}).setdefault(page, [left, top, right, bottom])
            box[:] = [min(box[0], left), min(box[1], top), max(box[2], right), max(box[3], bottom)]
    return out


def _banner_words_by_table(courses, evidence_ids) -> dict[Any, frozenset[str]]:
    """table_index -> banner words printed in that table's section-banner and context cells (the
    extractor's evidence cells, and any cell made only of banner words)."""
    out: dict[Any, set[str]] = {}
    for course in courses:
        for cell in (course.get("provenance") or {}).get("source_cells") or []:
            if cell.get("cell_id") in evidence_ids or is_banner_text(cell.get("text") or ""):
                out.setdefault(cell.get("table_index"), set()).update(banner_words(cell.get("text") or ""))
    return {table: frozenset(words) for table, words in out.items()}


def _course_flags(index, course, ctx) -> tuple[list[Flag], list]:
    flags: list[Flag] = []
    roles = own_role_cells(course, ctx["layout"], ctx["evidence_ids"])
    table = (course.get("_source") or {}).get("table_index")
    for name in ("course_code", "course_title", "prerequisites_raw"):
        value = clean_str(course.get(name))
        if not value or (name == "prerequisites_raw" and is_standing_rule(value)):
            continue
        if has_banner_text(value):
            seen = banner_confirmed(value, ctx["banners"].get(table, ()))
            flags.append(Flag("banner_leak", ERROR if seen else WARN,
                              f'{name} holds banner text: "{value}"' + ("" if seen else " (not a banner this table prints)"), name))
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
    page = ctx["pages"].get((course.get("provenance") or {}).get("page")) if ctx["pages"] else None
    title_missing = False
    if page is not None:
        got = {r["check"]: r["status"] for r in check_course_pdf(course, page.text, page.chars, page.height, ctx["layout"])}
        if got.get("B_code") == "fail":
            flags.append(Flag("code_not_in_pdf", WARN, "code not found in the PDF text", "course_code"))
        if got.get("B_title") == "fail":
            title_missing = True
            flags.append(Flag("title_not_in_pdf", WARN, "title not found in the PDF text", "course_title"))
    fixes = propose_fixes(course, roles, title_not_in_pdf=title_missing, page_text=page.text if page else None,
                          known_codes=ctx["codes"], banners=ctx["banners"].get(table, ()))
    for fix in fixes:
        if fix.kind == "move_term":
            flags.append(Flag("term_mismatch", WARN, f"{fix.note}, but the course is placed in {fix.old}", "term"))
    return flags, fixes


def _health(section: Section) -> str:
    severities = {f.severity for f in section.flags} | {f.severity for r in section.rows for f in r.flags}
    return "broken" if ERROR in severities else "review" if WARN in severities else "clean"


def _overall(sections: Sequence[Section], course_count: int) -> str:
    """clean | warnings_only | mixed | broken. Broken: most sections broken, fewer than two term
    sections, or printed codes no course claimed numbering a quarter of the courses (three at least)."""
    terms = [s for s in sections if s.sid not in (NO_TERM, UNPLACED)]
    broken = sum(s.health == "broken" for s in sections)
    unclaimed = sum(r.item is not None for s in sections for r in s.rows)
    if len(terms) < 2 or broken * 2 > len(sections) or (unclaimed >= 3 and unclaimed * 4 >= course_count):
        return "broken"
    if all(s.health == "clean" for s in sections):
        return "clean"
    return "mixed" if broken else "warnings_only"


def verify_candidate(payload: Mapping[str, Any], pdf_pages: Mapping[int, PdfPage] | None = None) -> Verification:
    courses = payload.get("courses") or []
    audit = payload.get("audit") or {}
    layout = audit.get("table_layout") or []
    evidence_ids = {i for s in audit.get("curriculum_sections") or [] for i in s.get("evidence_cells") or []}
    code_count = Counter(norm_key(c.get("course_code") or "") for c in courses)
    ctx = {
        "courses": courses, "layout": layout, "evidence_ids": evidence_ids, "pages": pdf_pages or {},
        "banners": _banner_words_by_table(courses, evidence_ids),
        "code_count": code_count, "codes": [c.get("course_code") or "" for c in courses],
        "positions": {c.get("course_code"): _term_of(c) for c in courses
                      if code_count[norm_key(c.get("course_code") or "")] == 1 and c.get("year_level") and c.get("semester")},
    }
    declared = {(t["year_level"], t["semester"]): t.get("declared_units") for t in audit.get("term_unit_audit") or []}
    keys = {(c.get("year_level"), c.get("semester")) for c in courses if c.get("year_level") and c.get("semester")}
    empty = [(y, s) for e in audit.get("errors") or [] if (m := EMPTY_DECLARED.search(e)) for y, s in [m.groups()]]
    keys |= {t for t in empty if t[0] in YEAR_ORDER and t[1] in SEMESTER_ORDER}
    sections = [Section(f"S{n}", y, s, declared=declared.get((y, s)))
                for n, (y, s) in enumerate(sorted(keys, key=lambda t: (term_index(*t), *t)), 1)]
    by_term = {(s.year, s.semester): s for s in sections}
    loose_section = Section(NO_TERM, None, None)
    for index, course in enumerate(courses):
        section = by_term.get((course.get("year_level"), course.get("semester"))) or loose_section
        row = Row(f"{section.sid}-{len(section.rows) + 1:02d}", course=index)
        row.flags, fixes = _course_flags(index, course, ctx)
        row.fixes = [(chr(ord("a") + i), fix) for i, fix in enumerate(fixes)]
        section.rows.append(row)
        section.computed += course.get("total_units") or 0
    for section in sections:
        if (section.year, section.semester) in empty and not section.rows:
            section.flags.append(Flag("unit_total", ERROR, "a printed total exists for this term but no courses were extracted"))
        elif section.declared is not None and section.declared != section.computed:
            section.flags.append(Flag("unit_total", ERROR, f"printed total {section.declared}, extracted {section.computed} ({section.computed - section.declared:+d})"))
    regions = _regions(sections, courses, layout, evidence_ids)
    unplaced = Section(UNPLACED, None, None)
    by_sid = {s.sid: s for s in sections}
    for item in unclaimed_items(audit, courses, pdf_pages):
        section = by_sid.get(attach(item, regions)) or unplaced
        row = Row(f"{section.sid}-U{sum(r.item is not None for r in section.rows) + 1}", item=item)
        if item["source"] == "anomaly":
            row.flags.append(Flag("audit_anomaly", ERROR, f'{item["type"]}: {item["snippet"]} (page {item["page"]})'))
        else:
            wrapped = item.get("confidence") == "review"   # no column evidence: a wrapped code is for a human to judge
            row.flags.append(Flag("unclaimed_code", WARN if wrapped else ERROR,
                                  f'printed code "{item["code"]}" was not claimed by any course ({item["source"]}, page {item["page"]}'
                                  + ("; wrapped over two lines, low confidence)" if wrapped else ")")))
        section.rows.append(row)
    sections += [s for s in (loose_section, unplaced) if s.rows]
    for section in sections:
        section.health = _health(section)
    return Verification(sections, bool(pdf_pages), _overall(sections, len(courses)))
