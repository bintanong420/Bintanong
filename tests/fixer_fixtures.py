"""Candidate-payload builders for the section verifier, fixer, ledger and review-sheet tests.

Cell texts, spans and boxes are copied from real Docling output in the cached task2b run
(BS Computer Science 2025-2026, BS Architecture, BS Entrepreneurship Innovation and Tech). They
are trimmed to a few courses each. No PDF is stored; PDF text below is a short excerpt.
"""

from __future__ import annotations

from backend.bintanong_tools.prospectus_extractor.text import term_index
from backend.bintanong_tools.prospectus_extractor.units import parse_units

T11 = ("1st Year", "1st Semester")
T12 = ("1st Year", "2nd Semester")


def cell(cid, text, r0, c0, c1, bbox=None, *, r1=None, page=1, table=0):
    return {
        "cell_id": cid, "table_index": table, "text": text, "raw_text": text,
        "row_start": r0, "row_end": r1 if r1 is not None else r0 + 1,
        "col_start": c0, "col_end": c1, "page": page, "bbox": bbox,
    }


def course(code, title, units, term, row, group, cells, *, title_raw=None, prereq="", prereq_list=(), page=1):
    year, semester = term
    units_dict = parse_units(units)
    boxes = [c["bbox"] for c in cells if c["bbox"]]
    union = (
        [min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes)]
        if boxes else None
    )
    return {
        "year_level": year, "semester": semester,
        "term_index": term_index(year or "", semester or ""),
        "course_code": code, "course_title": title,
        "title_raw": title if title_raw is None else title_raw, "footnote_marker": None,
        "units": units_dict, "total_units": units_dict["total"],
        "lecture_units": units_dict["lecture"], "lab_units": units_dict["lab"],
        "prerequisites_raw": prereq, "prerequisites": list(prereq_list),
        "prerequisites_unresolved": [], "confidence_flags": [],
        "provenance": {
            "page": page, "bbox": union, "valid": True, "highlightable": union is not None,
            "source_cell_ids": [c["cell_id"] for c in cells], "source_cells": cells,
        },
        "_source": {"table_index": 0, "row_index": row, "column_group": group},
        "code": code, "title": title,
    }


def payload(courses, *, layout, declared=None, evidence_cells=(), errors=(), unclaimed=(), name="Test Program"):
    """declared: {(year, semester): printed term total}. Computed totals come from the courses."""
    declared = declared or {}
    terms = sorted({(c["year_level"], c["semester"]) for c in courses if c["year_level"] and c["semester"]},
                   key=lambda t: term_index(*t))
    term_audit = [
        {"year_level": y, "semester": s, "declared_units": declared.get((y, s)),
         "computed_units": sum(c["total_units"] or 0 for c in courses if (c["year_level"], c["semester"]) == (y, s)),
         "course_count": sum(1 for c in courses if (c["year_level"], c["semester"]) == (y, s)),
         "matches": declared.get((y, s)) is None
         or declared[(y, s)] == sum(c["total_units"] or 0 for c in courses if (c["year_level"], c["semester"]) == (y, s))}
        for y, s in terms
    ]
    return {
        "program": name, "source_path": "x/x_docling.json",
        "courses": courses,
        "audit": {
            "status": "error" if errors else "ok", "errors": list(errors),
            "term_unit_audit": term_audit, "table_layout": layout,
            "curriculum_sections": [{"table_index": 0, "evidence_cells": list(evidence_cells)}],
            "unclaimed_course_candidates": list(unclaimed),
            "duplicate_course_codes": [],
        },
    }


# --- BS Computer Science 2025-2026: cell t0-c9 is a title cell that starts with the semester banner

BSCS_LAYOUT = [{"table_index": 0, "column_groups": [
    {"index": 0, "code_idx": 0, "title_idx": 1, "unit_idx": 2, "prereq_idx": 3},
    {"index": 1, "code_idx": 4, "title_idx": 5, "unit_idx": 6, "prereq_idx": 7},
]}]
BSCS_YEAR = cell("t0-c8", "FIRST YEAR", 1, 0, 8, [261.0, 173.6, 554.9, 183.5])
BSCS_TITLE_WITH_BANNER = cell("t0-c9", "FIRST SEMESTER Discrete Structures 1 1", 3, 1, 2, [103.4, 187.6, 210.2, 205.7])


def bscs():
    """Four first-year courses; printed term totals are set to the sums so the sections are clean."""
    cs1 = course("CS 1", "Discrete Structures 1", "3", T11, 3, 0, [
        cell("t0-c11", "CS 1", 3, 0, 1, [64.4, 195.6, 82.3, 205.5]), BSCS_TITLE_WITH_BANNER,
        cell("t0-c12", "3", 3, 2, 3, [246.7, 195.3, 259.7, 205.4]), BSCS_YEAR], title_raw="Discrete Structures 1 1")
    cc1 = course("CC 1/L", "Introduction to Computing", "2/1", T11, 4, 0, [
        cell("t0-c17", "CC 1/L", 4, 0, 1, [61.7, 205.2, 84.1, 215.3]),
        cell("t0-c18", "Introduction to Computing", 4, 1, 2, [99.8, 205.0, 181.7, 215.2]),
        cell("t0-c19", "2/1", 4, 2, 3, [246.7, 205.1, 260.1, 215.3]), BSCS_YEAR, BSCS_TITLE_WITH_BANNER])
    cs2 = course("CS 2", "Discrete Structures 2", "3", T12, 3, 1, [
        cell("t0-c13", "CS 2", 3, 4, 5, [322.2, 195.0, 340.1, 204.6]),
        cell("t0-c14", "Discrete Structures 2 2", 3, 5, 6, [364.7, 195.0, 433.6, 204.9]),
        cell("t0-c15", "3", 3, 6, 7, [494.2, 195.0, 507.2, 205.1]),
        cell("t0-c16", "CS 1", 3, 7, 8, [524.4, 194.1, 544.4, 203.9]), BSCS_YEAR, BSCS_TITLE_WITH_BANNER],
        title_raw="Discrete Structures 2 2", prereq="CS 1", prereq_list=["CS 1"])
    cc3 = course("CC 3/L", "Computer Programming 2", "2/1", T12, 4, 1, [
        cell("t0-c20", "CC 3/L", 4, 4, 5, [320.0, 205.2, 342.0, 215.3]),
        cell("t0-c21", "Computer Programming 2", 4, 5, 6, [364.0, 205.0, 440.0, 215.2]),
        cell("t0-c22", "2/1", 4, 6, 7, [494.0, 205.1, 508.0, 215.3]),
        cell("t0-c23", "CC 2/L", 4, 7, 8, [524.0, 205.1, 546.0, 215.3]), BSCS_YEAR, BSCS_TITLE_WITH_BANNER],
        prereq="CC 2/L")
    return payload([cs1, cc1, cs2, cc3], layout=BSCS_LAYOUT, evidence_cells=["t0-c8", "t0-c9"],
                   declared={T11: 6, T12: 6}, name="BS Computer Science")


# --- BS Architecture: wide banner cell t0-c10 spans the code columns; Docling glued a wrapped
# title line ("Techniques 1") to the start of the next row's title (GE-PC).

ARCH_LAYOUT = [{"table_index": 0, "column_groups": [
    {"index": 0, "code_idx": 1, "title_idx": 2, "unit_idx": 3, "prereq_idx": 4},
    {"index": 1, "code_idx": 6, "title_idx": 7, "unit_idx": 8, "prereq_idx": 9},
]}]
ARCH_BANNER = cell("t0-c10", "FIRST YEAR FIRST SEMESTER SECOND SEMESTER", 1, 1, 10, [69.6, 158.5, 553.8, 169.6])

ARCH_PAGE_TEXT = (
    "FIRST YEAR\r\nFIRST SEMESTER SECOND SEMESTER\r\n"
    "AD-1/L Architectural Design 1-Introduction to Design 1/1 AD-2/L Architectural Design 2-Creative Design and \r\n"
    "Fundamentals\r\n1/1 AD-1/L, \r\nTOA-1\r\n"
    "TOA-1/L Theory of Architecture1 2/1 GR-2/L Architectural Visual Communications 3-\r\nGraphics 2\r\n1/2 GR-1/L\r\n"
    "VT-1/L Architectural Visual Communications 2-Visual \r\nTechniques 1\r\n1/1 VT-2/L Architectural Visual "
    "Communications 4-Visual \r\nTechniques 2\r\n1/1 VT-1/L\r\n"
    "GE-PC Purposive Communication 3 TOA-2 Theory of Architecture 2 3 TOA-1\r\n"
)


def architecture():
    ad1 = course("AD-1/L", "Architectural Design 1-Introduction to Design", "1/1", T11, 2, 0, [
        cell("t0-c11", "AD-1/L", 2, 1, 2, [69.6, 170.0, 93.8, 180.3]),
        cell("t0-c12", "Architectural Design 1-Introduction to Design", 2, 2, 3, [110.1, 171.4, 243.1, 182.0]),
        cell("t0-c13", "1/1", 2, 3, 4, [251.7, 170.9, 268.0, 181.4]), ARCH_BANNER])
    toa1 = course("TOA-1/L", "1 Theory of Architecture1", "2/1", T11, 4, 0, [
        cell("t0-c26", "TOA-1/L", 4, 1, 2, [70.6, 198.9, 97.2, 209.0]),
        cell("t0-c22", "1 Theory of Architecture1", 4, 2, 3, [105.9, 198.9, 226.3, 209.4]),
        cell("t0-c27", "2/1", 4, 3, 4, [253.4, 199.0, 267.6, 209.6]), ARCH_BANNER])
    vt1 = course("VT-1/L", "Architectural Visual Communications 2-Visual", "1/1", T11, 5, 0, [
        cell("t0-c33", "VT-1/L", 5, 1, 2, [70.1, 214.0, 96.9, 224.1]),
        cell("t0-c34", "Architectural Visual Communications 2-Visual", 5, 2, 3, [109.1, 213.8, 241.8, 224.5]),
        cell("t0-c36", "1/1", 5, 3, 4, [254.0, 214.5, 267.1, 224.9]), ARCH_BANNER])
    gepc = course("GE-PC", "Techniques 1 Purposive Communication", "3", T11, 6, 0, [
        cell("t0-c41", "GE-PC", 6, 1, 2, [70.7, 228.3, 94.5, 238.4]),
        cell("t0-c35", "Techniques 1 Purposive Communication", 6, 2, 3, [107.4, 228.1, 208.1, 238.3]),
        cell("t0-c42", "3", 6, 3, 4, [254.4, 229.0, 266.8, 239.3]), ARCH_BANNER])
    ad2 = course("AD-2/L", "Architectural Design 2-Creative Design and", "1/1", T12, 2, 1, [
        cell("t0-c14", "AD-2/L", 2, 6, 7, [339.9, 170.6, 368.5, 180.7]),
        cell("t0-c15", "Architectural Design 2-Creative Design and", 2, 7, 8, [377.4, 171.9, 497.1, 182.4]),
        cell("t0-c17", "1/1", 2, 8, 9, [513.1, 170.3, 529.3, 181.0]),
        cell("t0-c18", "AD-1/L,", 2, 9, 10, [534.9, 170.1, 562.5, 180.2]), ARCH_BANNER],
        prereq="AD-1/L,", prereq_list=["AD-1/L"])
    vt2 = course("VT-2/L", "Graphics 2 Architectural Visual Communications 4-Visual", "1/1", T12, 5, 1, [
        cell("t0-c37", "VT-2/L", 5, 6, 7, [340.1, 214.3, 364.4, 224.1]),
        cell("t0-c30", "Graphics 2 Architectural Visual Communications 4-Visual", 5, 7, 8, [375.5, 213.1, 487.8, 223.7]),
        cell("t0-c39", "1/1", 5, 8, 9, [514.4, 214.4, 527.7, 225.0]),
        cell("t0-c40", "VT-1/L", 5, 9, 10, [537.1, 214.2, 558.5, 224.4]), ARCH_BANNER],
        prereq="VT-1/L", prereq_list=["VT-1/L"])
    toa2 = course("TOA-2", "Techniques 2 Theory of Architecture 2", "3", T12, 6, 1, [
        cell("t0-c43", "TOA-2", 6, 6, 7, [340.8, 228.7, 361.7, 238.6]),
        cell("t0-c38", "Techniques 2 Theory of Architecture 2", 6, 7, 8, [380.6, 228.9, 443.5, 239.3]),
        cell("t0-c44", "3", 6, 8, 9, [516.1, 228.7, 527.7, 239.3]),
        cell("t0-c45", "TOA-1", 6, 9, 10, [538.4, 227.6, 559.7, 237.8]), ARCH_BANNER], prereq="TOA-1")
    return payload([ad1, toa1, vt1, gepc, ad2, vt2, toa2], layout=ARCH_LAYOUT, evidence_cells=["t0-c10"],
                   declared={T11: 10, T12: 7}, name="BS Architecture")


# --- BS Entrepreneurship Innovation and Tech: only the 4th-year rows were parsed; fifteen printed
# codes above the "FOURTH YEAR" banner were left unclaimed (audit.unclaimed_course_candidates).

INNOV_LAYOUT = [{"table_index": 0, "column_groups": [
    {"index": 0, "code_idx": 1, "title_idx": 2, "unit_idx": 3, "prereq_idx": 4},
    {"index": 1, "code_idx": 5, "title_idx": 6, "unit_idx": 7, "prereq_idx": 8},
]}]
INNOV_YEAR = cell("t0-c62", "FOURTH YEAR", 9, 0, 9, [279.5, 782.3, 337.4, 789.5])
INNOV_SEM = cell("t0-c63", "FIRST SEMESTER SECOND SEMESTER", 10, 0, 9, [136.4, 792.3, 483.6, 799.5])
Y4 = ("4th Year", "1st Semester")
Y4B = ("4th Year", "2nd Semester")


def innovation():
    e14 = course("ENTRE 14", "Business Implementation 1", "5", Y4, 11, 0, [
        cell("t0-c64", "ENTRE 14", 11, 1, 2, [71.2, 802.6, 98.3, 818.9]),
        cell("t0-c65", "Business Implementation 1", 11, 2, 3, [107.2, 802.6, 203.1, 809.7]),
        cell("t0-c66", "5", 11, 3, 4, [247.5, 802.6, 251.9, 809.7]),
        cell("t0-c67", "ENTRE 10", 11, 4, 5, [272.1, 802.6, 299.2, 818.9]), INNOV_YEAR, INNOV_SEM],
        prereq="ENTRE 10")
    e15 = course("ENTRE 15", "Business Implementation 2", "5", Y4B, 11, 1, [
        cell("t0-c68", "ENTRE 15", 11, 5, 6, [345.5, 802.6, 372.6, 818.9]),
        cell("t0-c69", "Business Implementation 2", 11, 6, 7, [390.5, 802.6, 486.4, 809.7]),
        cell("t0-c70", "5", 11, 7, 8, [522.4, 802.6, 526.8, 809.7]),
        cell("t0-c71", "ENTRE 14", 11, 8, 9, [546.8, 802.6, 573.9, 818.9]), INNOV_YEAR, INNOV_SEM],
        prereq="ENTRE 14", prereq_list=["ENTRE 14"])

    def unclaimed(code, cid, bbox):
        return {"code": code, "normalized_code": code.replace(" ", ""), "cell_ids": [cid], "table_index": 0,
                "page": 1, "bbox": bbox, "confidence": "high"}

    items = [unclaimed("ENTRE 7", "t0-c0", [71.2, 579.5, 98.3, 595.9]),
             unclaimed("GE-IER", "t0-c4", [345.5, 584.1, 373.1, 591.3]),
             unclaimed("ENTRE 9", "t0-c54", [71.2, 749.0, 98.3, 765.0])]
    errors = ["Document declares a total for 1st Year 1st Semester but no courses were extracted there.",
              "3 high-confidence source course code(s) were not claimed by the parser."]
    return payload([e14, e15], layout=INNOV_LAYOUT, evidence_cells=["t0-c62", "t0-c63"], declared={Y4: 5, Y4B: 5},
                   errors=errors, unclaimed=items, name="BS Entrepreneurship Innovation and Tech")


# --- reading helpers for tests

def kinds(row):
    return [f.kind for f in row.flags]


def section(verification, sid):
    return next(s for s in verification.sections if s.sid == sid)


def by_code(payload, verification):
    return {payload["courses"][r.course]["course_code"]: r for s in verification.sections for r in s.rows if r.course is not None}
