"""Printed codes no course claimed, and which year/semester section they sit in.

Items come from the audit's unclaimed list and anomalies (geometry in the candidate JSON) and, when
the PDF text layer is at hand, from printed code-like strings no course accounts for (geometry from
the PDF character boxes). Placement is conservative: an item is attached to a section only when its
box is inside that section's region (or just under its last row) and exactly one section fits;
anything else stays unplaced for the reviewer.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from .course_checks import DASHES as _PDF_DASHES  # not re-exported as DASHES: text.DASHES is a different set
from .course_checks import PdfPage, check_pdf_missed, loose
from .text import clean_str

BELOW_TOLERANCE = 30.0  # points under a section's last row where a missed course may still sit
# Anomalies already reported by another flag: the audit's own unclaimed list, and courses with no term.
COVERED_ANOMALIES = {"unclaimed_course_candidate", "course_without_verified_semester"}


WRAP_REACH_POINTS = 30.0  # a wrapped code's two lines sit in one code column: no more than this between their extents
MAX_GAP_GLYPHS = 2.0  # a printed code's glyphs touch; more than two glyph widths between two of them is a cell boundary


def _occurrences(page: PdfPage, code: str) -> list[list[tuple]]:
    """Every run of PDF characters that reads as `code` (spaces and dashes ignored), as glyph boxes
    (ch, left, bottom, right, top). Whether the glyphs touch is `_touching`'s question."""
    kept = [i for i, c in enumerate(page.chars or []) if c[0] and not c[0].isspace() and c[0] not in _PDF_DASHES]
    flat = "".join(page.chars[i][0].casefold() for i in kept)
    key = loose(code).casefold()
    found, at = [], flat.find(key) if key else -1
    while at >= 0:
        found.append([page.chars[kept[j]] for j in range(at, at + len(key))])
        at = flat.find(key, at + 1)
    return found


def _touching(boxes: Sequence[tuple]) -> bool:
    """No two consecutive glyphs further apart than MAX_GAP_GLYPHS median glyph widths, and all on one text
    line (a negative gap after a line wrap is not touching). "Law" at the end
    of a title cell and a "3" in the units cell read as `Law 3` in the text layer but are not a code."""
    widths = sorted(b[3] - b[1] for b in boxes)
    limit = MAX_GAP_GLYPHS * widths[len(widths) // 2]
    return all(nxt[1] - prev[3] <= limit and _same_line(prev, nxt) for prev, nxt in zip(boxes, boxes[1:]))


def _same_line(a: tuple, b: tuple) -> bool:
    """Two glyph boxes (ch, left, bottom, right, top) share a text line when they overlap vertically by
    more than half of the shorter one; the end of one wrapped line and the start of the next do not."""
    overlap = min(a[4], b[4]) - max(a[2], b[2])
    return overlap > 0.5 * min(a[4] - a[2], b[4] - b[2])


def _wrapped(boxes: Sequence[tuple]) -> bool:
    """A code printed as two segments on adjacent text lines ("Mktg" / "2001" in one code cell that wrapped):
    each segment is internally contiguous, the second line starts within one line height below the first,
    and the segments' horizontal extents are at most WRAP_REACH_POINTS apart, so both sit in one code
    column. A numeric tail 100 pt away (the units column) or three lines are not a wrap."""
    cut = next((i for i, (a, b) in enumerate(zip(boxes, boxes[1:]), 1) if not _same_line(a, b)), None)
    if cut is None:
        return False
    first, second = boxes[:cut], boxes[cut:]
    if any(not _same_line(a, b) for a, b in zip(second, second[1:])) or not (_touching(first) and _touching(second)):
        return False
    height = max(b[4] - b[2] for b in boxes)
    vertical_gap = min(b[2] for b in first) - max(b[4] for b in second)
    reach = max(min(b[1] for b in second) - max(b[3] for b in first), min(b[1] for b in first) - max(b[3] for b in second))
    return -height <= vertical_gap <= height and reach <= WRAP_REACH_POINTS


def wrapped_location(page: PdfPage, code: str) -> list[float] | None:
    """Box of the one wrapped occurrence of `code` when the page holds exactly one and no touching one."""
    runs = _occurrences(page, code)
    wrapped = [r for r in runs if _wrapped(r)]
    if len(wrapped) != 1 or any(_touching(r) for r in runs) or not page.height:
        return None
    return _box(wrapped[0], page.height)


def is_wrapped(page: PdfPage, code: str) -> bool:
    runs = _occurrences(page, code)
    return not any(_touching(r) for r in runs) and any(_wrapped(r) for r in runs)


def is_split_across_cells(page: PdfPage, code: str) -> bool:
    """True when the page text layer holds `code` only as glyphs that do not touch."""
    runs = _occurrences(page, code)
    return bool(runs) and not any(_touching(r) for r in runs)


def locate_in_page(page: PdfPage, code: str) -> list[float] | None:
    """[left, top, right, bottom] (top-left frame) of `code` in the PDF characters, only when the
    page holds exactly one such string made of touching glyphs; several (CS 1 inside CS 10) cannot
    be placed safely."""
    if not page.chars or not page.height:
        return None
    runs = [r for r in _occurrences(page, code) if _touching(r)]
    if len(runs) != 1:
        return None
    return _box(runs[0], page.height)


def _box(boxes: Sequence[tuple], height: float) -> list[float]:
    # chars are (ch, left, bottom, right, top) with y up from the page bottom
    return [min(b[1] for b in boxes), height - max(b[4] for b in boxes),
            max(b[3] for b in boxes), height - min(b[2] for b in boxes)]


def attach(item: Mapping[str, Any], regions: Mapping[str, Mapping[int, Sequence[float]]]) -> str | None:
    """The one section whose region holds the item, else None. Inside a region wins outright;
    otherwise a section whose last row ends within BELOW_TOLERANCE above the item; a tie is None.
    regions: section id -> page -> [left, top, right, bottom] in the table-cell (top-left) frame."""
    bbox, page = item.get("bbox"), item.get("page")
    if not bbox or page is None:
        return None
    left, top, right, bottom = bbox
    inside, below = [], []
    for sid, pages in regions.items():
        box = pages.get(page)
        if not box or min(right, box[2]) - max(left, box[0]) <= 0:
            continue
        middle = (top + bottom) / 2
        if box[1] <= middle <= box[3]:
            inside.append(sid)
        elif box[3] < middle <= box[3] + BELOW_TOLERANCE:
            below.append(sid)
    pool = inside or below
    return pool[0] if len(pool) == 1 else None


def unclaimed_items(audit: Mapping[str, Any], courses: Sequence[Mapping[str, Any]], pages: Mapping[int, PdfPage] | None) -> list[dict]:
    """Printed codes and anomalies no course accounts for: {source, code, page, bbox, cell_ids, table_index, snippet}."""
    items = [
        {"source": "audit", "code": u.get("code") or "", "page": u.get("page"), "bbox": u.get("bbox"),
         "cell_ids": list(u.get("cell_ids") or []), "table_index": u.get("table_index"), "snippet": ""}
        for u in audit.get("unclaimed_course_candidates") or []
    ]
    for anomaly in audit.get("structural_anomalies") or []:
        if anomaly.get("type") in COVERED_ANOMALIES:
            continue
        boxes = [c["bbox"] for c in anomaly.get("source_cells") or [] if c.get("bbox")]
        items.append({
            "source": "anomaly", "type": anomaly.get("type"), "page": anomaly.get("page"),
            "code": ", ".join(anomaly.get("candidate_codes") or []) or str(anomaly.get("type")),
            "bbox": [min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes)] if boxes else None,
            "cell_ids": list(anomaly.get("source_cell_ids") or []), "table_index": anomaly.get("table_index"),
            "snippet": clean_str(anomaly.get("reason")),
        })
    for page_no, page in sorted((pages or {}).items()):
        for row in check_pdf_missed(courses, audit, page.text, None, page_no):
            if row["status"] != "silent":
                continue  # the audit's own list is already above
            wrapped = is_wrapped(page, row["json"])
            if is_split_across_cells(page, row["json"]) and not wrapped:
                continue  # glyphs in different cells (a title word and the units digit): not a code
            items.append({"source": "pdf", "code": row["json"], "page": page_no,
                          "bbox": wrapped_location(page, row["json"]) if wrapped else locate_in_page(page, row["json"]),
                          "cell_ids": [], "table_index": None, "snippet": row["pdf"],
                          "confidence": "review" if wrapped else "high"})
    return items
