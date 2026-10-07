"""Fix proposals for one flagged course. A proposal is only a proposal: a human accepts it.

Three kinds, each derived from text the document already holds, never from a guess:
  strip_banner    a banner phrase at the start or end of the code or title is removed
  move_term       the course's own code/title cell starts with a banner that names another term
  title_from_pdf  the title is read from the PDF text layer when exactly one PDF row matches
Anything that would need invented text (a title, a prerequisite) gets no proposal.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from typing import Any, Collection, Iterable, Mapping, Sequence

from .course_checks import pdf_clean
from .text import BANNER_PHRASE, BANNER_WORDS, clean_str, has_banner_text, leading_banner, match_semester_labels, match_year_label, trailing_banner

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


# Banner wording in an evidence cell, any case, glued or spaced, TERM forms too: "First Semester",
# "FIRSTSEMESTER", "FIRST TERM". Stricter than has_banner_text, whose upper-case rule the verifier flags rely on.
_EVIDENCE_BANNER = re.compile(r"(?:FIRST|SECOND|THIRD|FOURTH|FIFTH|1ST|2ND|3RD|4TH|5TH)\s*(?:YEAR|SEM|TERM)"
                              r"|(?<![A-Z])(?:SEMESTER|SUMMER|MID[\s-]?YEAR)(?![A-Z])")


def _evidence_cells(course: Mapping[str, Any], role_cells: Mapping[str, Sequence[Mapping[str, Any]]],
                    shared_cells: Collection[str] | None) -> set[str]:
    """Clean texts of the cells that may authorise a strip: this course's code or title cells, spanning exactly
    its own row, owned by no other course, with no banner wording. Unknown ownership (None) means none."""
    row = (course.get("_source") or {}).get("row_index")
    if shared_cells is None or row is None:
        return set()
    return {clean_str(c.get("text")) for role in ("code", "title") for c in role_cells.get(role, [])
            if c.get("row_start") == row and c.get("row_end") == row + 1 and c.get("cell_id") not in shared_cells
            and not has_banner_text(c.get("text") or "") and not _EVIDENCE_BANNER.search(clean_str(c.get("text")).upper())}


# A course code, known or not, ends a row band: "CS 1", "OTHER 2", "ENTRE 15", "GE-MMW". Upper-case prefixes only,
# so a title such as "Calculus 1" is not mistaken for the next row.
ANY_CODE = re.compile(r"(?<!\S)(?:[A-Z]{1,8}[\s\-]?\d{1,4}[A-Za-z]?(?:/[A-Z])?|GE[\s\-][A-Za-z]{2,6})(?=\s|$)")


def _count(tokens: Sequence[str], run: Sequence[str]) -> int:
    return sum(tokens[at:at + len(run)] == list(run) for at in range(len(tokens) - len(run) + 1))


def anchored_in_pdf(page_text: str, head: str, tail: str, units_raw: str) -> bool:
    """True when the PDF text holds the whole tokens `head`, `tail` side by side and then this row's units token
    (or the end of the text): "<this code> <remainder> <units>". Nothing may sit between the two, not a word,
    not an unknown code, so words of another row can never serve as this row's evidence. The page text has no row
    locality, so both sides (the anchor and the proposed remainder) must each be printed exactly once on the
    page; if either repeats there is no PDF evidence and only this course's own source cells can authorise."""
    tokens, first, second = pdf_clean(page_text).split(), clean_str(head).split(), clean_str(tail).split()
    units = clean_str(units_raw).split()
    if not tokens or not first or not second:
        return False
    run = first + second
    if _count(tokens, first) != 1 or _count(tokens, second) != 1:
        return False
    for at in range(len(tokens) - len(run) + 1):
        if tokens[at:at + len(run)] == run:
            after = tokens[at + len(run):]
            if not after or (units and after[:len(units)] == units):
                return True
    return False


def shared_cell_ids(courses: Iterable[Mapping[str, Any]]) -> frozenset[str]:
    """Cell ids that sit in the provenance of more than one course."""
    seen = Counter(i for c in courses for i in {s.get("cell_id") for s in (c.get("provenance") or {}).get("source_cells") or []})
    return frozenset(i for i, n in seen.items() if i is not None and n > 1)


def _strip_fixes(course: Mapping[str, Any], role_cells: Mapping[str, Sequence[Mapping[str, Any]]], banners: Collection[str],
                 page_text: str | None = None, shared_cells: Collection[str] | None = None) -> list[Fix]:
    out = []
    evidence = _evidence_cells(course, role_cells, shared_cells)
    units = (course.get("units") or {}).get("raw") or ""
    for field, role, name in ((FIELD_CODE, "code", "code"), (FIELD_TITLE, "title", "title")):
        value = clean_str(course.get(field))
        cells = [c["cell_id"] for c in role_cells.get(role, [])]
        stripped = strip_banner(value) if BANNER_PHRASE.search(value) and banner_confirmed(value, banners) else None
        if stripped and field == FIELD_TITLE and ANY_CODE.match(stripped):
            stripped = None   # "PE 1 Rhythmic": this course's title or the next row's code? Without layout, flag only.
        anchored = bool(stripped and page_text) and (
            anchored_in_pdf(page_text, clean_str(course.get(FIELD_CODE)), stripped, units) if field == FIELD_TITLE
            else anchored_in_pdf(page_text, stripped, clean_str(course.get(FIELD_TITLE)), units))
        if stripped and (anchored or stripped in evidence):
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
    shared_cells: Collection[str] | None = None,
) -> list[Fix]:
    """`banners`: the banner words the course's table prints in its section-banner cells. A strip is
    proposed only for banner text made of those words, and only when the remainder is printed on its own:
    exactly as one of this course's own code/title cells (see `_evidence_cells`), or anchored in its PDF row;
    else it is flag-only. `shared_cells`: `shared_cell_ids(candidate courses)`; None means no cell is evidence."""
    fixes = _strip_fixes(course, role_cells, banners, page_text, shared_cells) + _move_fix(course, role_cells)
    if title_not_in_pdf and page_text and not any(f.field == FIELD_TITLE for f in fixes):
        new = title_from_pdf(clean_str(course.get("course_code")), (course.get("units") or {}).get("raw") or "",
                             course.get("course_title") or "", page_text, known_codes)
        if new:
            cells = [c["cell_id"] for c in role_cells.get("title", [])]
            fixes.append(Fix("title_from_pdf", FIELD_TITLE, clean_str(course.get("course_title")), new,
                             "title read from the PDF text layer (one matching row)", _fix_id("title_from_pdf", FIELD_TITLE, cells)))
    return fixes
