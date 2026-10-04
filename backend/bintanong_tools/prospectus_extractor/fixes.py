"""Fix proposals for one flagged course. A proposal is only a proposal: a human accepts it.

Three kinds, each derived from text the document already holds, never from a guess:
  strip_banner    a banner phrase at the start or end of the code or title is removed
  move_term       the course's own code/title cell starts with a banner that names another term
  title_from_pdf  the title is read from the PDF text layer when exactly one PDF row matches
Anything that would need invented text (a title, a prerequisite) gets no proposal.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Collection, Iterable, Mapping, Sequence

from .course_checks import pdf_clean
from .text import BANNER_PHRASE, BANNER_WORDS, clean_str, leading_banner, match_semester_labels, match_year_label, trailing_banner

FIELD_CODE, FIELD_TITLE, FIELD_TERM = "course_code", "course_title", "term"


@dataclass(frozen=True)
class Fix:
    kind: str       # strip_banner | move_term | title_from_pdf
    field: str      # course_code | course_title | term
    old: str
    new: str
    note: str
    fix_id: str     # stable across sheet regenerations: "<kind>:<field>@<first source cell id>"


def format_term(year: str | None, semester: str | None) -> str:
    return f"{year or '?'} / {semester or '?'}"


def parse_term(text: str, default_year: str | None = None) -> tuple[str, str] | None:
    """'2nd Year / 1st Semester' (or just '1st Semester') to (year, semester), else None."""
    value = clean_str(text)
    year = match_year_label(value) or default_year
    labels = {label for _position, label in match_semester_labels(value)}
    if not year or len(labels) != 1:
        return None
    return year, labels.pop()


def strip_banner(text: str) -> str | None:
    """`text` without banner phrases at its start or end, or None when nothing sensible remains:
    nothing to strip, nothing left, or banner text still inside it (a banner in the middle of a
    title cannot be removed without guessing where the course text starts)."""
    value = clean_str(text)
    _banner, rest = leading_banner(value)
    rest, _tail = trailing_banner(rest)
    rest = clean_str(rest)
    if not rest or rest == value or BANNER_PHRASE.search(rest):
        return None
    return rest


def banner_words(text: str) -> frozenset[str]:
    """The banner words ("FIRST", "SEM", "YEAR", ...) printed in `text`, upper case, full stops dropped."""
    return frozenset(w for w in (t.strip(".,:") for t in clean_str(text).upper().split()) if w in BANNER_WORDS)


def banner_confirmed(value: str, context: Collection[str]) -> bool:
    """True when every banner phrase `value` carries (at its start, its end or inside) is made of words
    the table itself prints in a section-banner or context cell. A title that merely looks like a banner
    ("SUMMER INTERNSHIP" in a table with no SUMMER banner) is not confirmed."""
    lead, rest = leading_banner(value)
    found = banner_words(lead) | banner_words(trailing_banner(rest)[1]) | banner_words(" ".join(BANNER_PHRASE.findall(clean_str(value).upper())))
    return bool(found) and found <= set(context)


def _fix_id(kind: str, field: str, cell_ids: Sequence[str]) -> str:
    return f"{kind}:{field}@{cell_ids[0] if cell_ids else 'none'}"


def printed_without_banner(remainder: str, texts: Iterable[str]) -> bool:
    """True when `remainder` occurs in one of `texts` with no banner phrase right before or after it.
    The remainder of a strip must be printed in the document on its own (a clean cell, the PDF row),
    not only inside the very banner-bearing text being stripped: "FIRST SEMESTER PRACTICUM" printed
    once, as one string, never proves that "PRACTICUM" is the title."""
    pattern = re.compile(rf"(?<!\w){re.escape(remainder)}(?!\w)")
    for text in texts:
        value = clean_str(text)
        for m in pattern.finditer(value):
            if not trailing_banner(value[: m.start()])[1] and not leading_banner(value[m.end():])[0]:
                return True
    return False


# A course code, known or not, ends a row band: "CS 1", "OTHER 2", "ENTRE 15", "GE-MMW". Upper-case prefixes only,
# so a title such as "Calculus 1" is not mistaken for the next row.
ANY_CODE = re.compile(r"(?<!\S)(?:[A-Z]{1,8}[\s\-]?\d{1,4}[A-Za-z]?(?:/[A-Z])?|GE[\s\-][A-Za-z]{2,6})(?=\s|$)")


def row_bands(page_text: str, anchor: str, units_raw: str, other_codes: Sequence[str], remainder: str = "") -> list[str]:
    """This course's own stretch of the PDF text, one per place `anchor` (its code, or the code being
    proposed) is printed: from the anchor to the next code (known, or any course-code-shaped token), and no
    further than the first whole-token `units_raw` after it (the end of the row). Text of other rows is never part of a band."""
    text = pdf_clean(page_text)
    cuts = sorted({clean_str(c) for c in other_codes if clean_str(c) and clean_str(c) != anchor}, key=len, reverse=True)
    cut = re.compile(r"(?<!\S)(?:" + "|".join(re.escape(c) for c in cuts) + r")(?=\s|$)") if cuts else None
    units = clean_str(units_raw)
    bands = []
    for m in re.finditer(rf"(?<!\S){re.escape(anchor)}(?=\s|$)", text):
        window = text[m.end():]
        stop = cut.search(window) if cut else None
        window = window[: stop.start()] if stop else window
        own = [(r.start(), r.end()) for r in re.finditer(re.escape(remainder), window)] if remainder else []
        # a code-shaped token ends the band unless it starts inside this course's own remaining title ("PE 1 Rhythmic")
        stray = next((c for c in ANY_CODE.finditer(window) if not any(a <= c.start() < b for a, b in own)), None)
        ends = [m for m in (re.search(rf"(?<=\s){re.escape(units)}(?=\s|$)", window) if units else None, stray) if m]
        bands.append(window[: min(m.start() for m in ends)] if ends else window)
    return bands


def _strip_fixes(course: Mapping[str, Any], role_cells: Mapping[str, Sequence[Mapping[str, Any]]], banners: Collection[str],
                 page_text: str | None = None, known_codes: Sequence[str] = ()) -> list[Fix]:
    out = []
    own = [c.get("text") or "" for c in (course.get("provenance") or {}).get("source_cells") or []]
    units = (course.get("units") or {}).get("raw") or ""
    for field, role, name in ((FIELD_CODE, "code", "code"), (FIELD_TITLE, "title", "title")):
        value = clean_str(course.get(field))
        cells = [c["cell_id"] for c in role_cells.get(role, [])]
        stripped = strip_banner(value) if BANNER_PHRASE.search(value) and banner_confirmed(value, banners) else None
        evidence = [t for t in own if clean_str(t) != value]       # this course's other cells, not the banner cell
        if stripped and page_text:
            anchor = stripped if field == FIELD_CODE else clean_str(course.get(FIELD_CODE))
            evidence += row_bands(page_text, anchor, units, known_codes, stripped)
        if stripped and printed_without_banner(stripped, evidence):
            out.append(Fix("strip_banner", field, value, stripped, f"banner text removed from the {name}",
                           _fix_id("strip_banner", field, cells)))
    return out


def _move_fix(course: Mapping[str, Any], role_cells: Mapping[str, Sequence[Mapping[str, Any]]]) -> list[Fix]:
    """A leading banner in the course's own code/title cell names the term the course sits in. Only
    a leading banner counts: a trailing one names the next section. Both semesters named, or an
    unreadable label, means flag-only."""
    year, semester = course.get("year_level"), course.get("semester")
    for role in ("code", "title"):
        for cell in role_cells.get(role, []):
            banner, rest = leading_banner(cell.get("text") or "")
            sems = {label for _p, label in match_semester_labels(banner)}
            if not banner or not rest or len(sems) != 1:
                continue
            target = (match_year_label(banner) or year, next(iter(sems)))
            if None in target or target == (year, semester):
                continue
            return [Fix("move_term", FIELD_TERM, format_term(year, semester), format_term(*target),
                        f'cell {cell["cell_id"]} starts with "{banner}"', _fix_id("move_term", FIELD_TERM, [cell["cell_id"]]))]
    return []


def _before_totals(text: str) -> str:
    """`text` without a trailing "Total" (the totals column) and the units figure printed just before
    it. A title that merely starts with or contains "Total" ("Total Quality Management") is kept."""
    value = text.strip()
    cut = re.sub(r"\s+Total$", "", value, flags=re.IGNORECASE)
    if cut == value:
        return value
    return re.sub(r"\s+(?:\d{1,2}|\d/\d)$", "", cut)


def title_from_pdf(code: str, units_raw: str, current: str, page_text: str, other_codes: Sequence[str]) -> str | None:
    """The title printed between `code` and the printed units, when the PDF text holds exactly one
    row that fits: `code`, words, then the units as a whole token, before the next known code.
    Several fits (a title that repeats the units digit) or none: None."""
    text = pdf_clean(page_text)
    units = clean_str(units_raw)
    if not code or not units:
        return None
    cuts = sorted({clean_str(c) for c in other_codes if clean_str(c) and clean_str(c) != code}, key=len, reverse=True)
    cut = re.compile(r"(?<!\S)(?:" + "|".join(re.escape(c) for c in cuts) + r")(?=\s|$)") if cuts else None
    found: list[str] = []
    for m in re.finditer(rf"(?<!\S){re.escape(code)}(?=\s)", text):
        window = text[m.end():].lstrip()
        stop = cut.search(window) if cut else None
        window = window[: stop.start()] if stop else window
        fits = [_before_totals(window[: u.start()]) for u in re.finditer(rf"(?<=\s){re.escape(units)}(?=\s|$)", window)]
        fits = [t for t in fits if len(re.findall(r"[A-Za-z]", t)) >= 2 and not BANNER_PHRASE.search(t)]
        if len(fits) > 1:
            return None
        found += fits
    if len(found) != 1 or found[0] == clean_str(current):
        return None
    return found[0]


def propose_fixes(
    course: Mapping[str, Any],
    role_cells: Mapping[str, Sequence[Mapping[str, Any]]],
    *,
    title_not_in_pdf: bool = False,
    page_text: str | None = None,
    known_codes: Sequence[str] = (),
    banners: Collection[str] = (),
) -> list[Fix]:
    """`banners`: the banner words the course's table prints in its section-banner cells. A strip is
    proposed only for banner text made of those words, and only when the remainder is printed
    elsewhere without a banner next to it (another cell of this course or this course's own PDF row); else it is flag-only."""
    fixes = _strip_fixes(course, role_cells, banners, page_text, known_codes) + _move_fix(course, role_cells)
    if title_not_in_pdf and page_text and not any(f.field == FIELD_TITLE for f in fixes):
        new = title_from_pdf(clean_str(course.get("course_code")), (course.get("units") or {}).get("raw") or "",
                             course.get("course_title") or "", page_text, known_codes)
        if new:
            cells = [c["cell_id"] for c in role_cells.get("title", [])]
            fixes.append(Fix("title_from_pdf", FIELD_TITLE, clean_str(course.get("course_title")), new,
                             "title read from the PDF text layer (one matching row)", _fix_id("title_from_pdf", FIELD_TITLE, cells)))
    return fixes
