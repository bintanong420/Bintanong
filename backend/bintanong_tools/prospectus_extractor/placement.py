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


def locate_in_page(page: PdfPage, code: str) -> list[float] | None:
    """[left, top, right, bottom] (top-left frame) of `code` in the PDF characters, only when the
    page holds exactly one such string; several (CS 1 inside CS 10) cannot be placed safely."""
    if not page.chars or not page.height:
        return None
    kept = [i for i, c in enumerate(page.chars) if c[0] and not c[0].isspace() and c[0] not in _PDF_DASHES]
    flat = "".join(page.chars[i][0].casefold() for i in kept)
    key = loose(code).casefold()
    if not key or flat.count(key) != 1:
        return None
    at = flat.index(key)
    boxes = [page.chars[kept[j]] for j in range(at, at + len(key))]
    # chars are (ch, left, bottom, right, top) with y up from the page bottom
    return [min(b[1] for b in boxes), page.height - max(b[4] for b in boxes),
            max(b[3] for b in boxes), page.height - min(b[2] for b in boxes)]


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
            if row["status"] == "silent":  # the audit's own list is already above
                items.append({"source": "pdf", "code": row["json"], "page": page_no,
                              "bbox": locate_in_page(page, row["json"]), "cell_ids": [], "table_index": None,
                              "snippet": row["pdf"]})
    return items
