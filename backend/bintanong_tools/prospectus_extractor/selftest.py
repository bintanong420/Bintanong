"""Built-in fixtures and the 80-check self-test."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any
from typing import Mapping
from typing import Sequence

from .text import match_year_label, relaxed_key
from .units import parse_units
from .prerequisites import is_standing_rule, split_prereq_fragments
from .evidence import LoadedDocument, ProspectusEvidence, normalized_table_from_grid, project_table_to_grid
from .prolog import pl_atom
from .loader import evidence_adapter, normalize_evidence
from .pipeline import build_payload


# Fixtures are transcriptions of the two prospectuses that broke v1:
#   * BS Computer Science, SY 2025-2026 (8-column table, merged banner rows,
#     superscript footnote markers, wrapped prerequisite text)
#   * BS Architecture, SY 2018-2019 (10-column table with Grade columns, five
#     year levels, series-numbered titles such as "History of Architecture 3")
# Merged cells are repeated across their span exactly as Docling renders them.
CS_HEADER = [
    "Course Code", "Course Title", "Unit", "Pre- requisite",
    "Course Code", "Course Title", "Unit", "Pre- requisite",
]


def _cs_row(left: Sequence[str], right: Sequence[str] = ("", "", "", "")) -> list[str]:
    return [*left, *right]


def _merged(text: str, width: int) -> list[str]:
    return [text] * width


def _cs_semester_row() -> list[str]:
    return ["FIRST SEMESTER"] * 4 + ["SECOND SEMESTER"] * 4


def cs_fixture_grid() -> list[list[str]]:
    grid: list[list[str]] = [CS_HEADER]

    grid.append(_merged("FIRST YEAR", 8))
    grid.append(_cs_semester_row())
    grid += [
        _cs_row(("CS 1", "Discrete Structures 1 1", "3", ""), ("CS 2", "Discrete Structures 2 2", "3", "CS 1")),
        _cs_row(("CC 1/L", "Introduction to Computing", "2/1", ""), ("CC 3/L", "Computer Programming 2", "2/1", "CC 2/L")),
        _cs_row(("CC 2/L", "Computer Programming 1", "2/1", ""), ("Electronics/L", "Fundamentals of Electronics 3", "1/2", "")),
        _cs_row(("GE-AA", "Art Appreciation", "3", ""), ("AMR 1", "Statistical Methods for Computer Science 4", "3", "")),
        _cs_row(("GE-PH", "Readings in Philippine History", "3", ""), ("GE-PC", "Purposive Communication", "3", "")),
        _cs_row(("GE-MMW", "Mathematics in the Modern World", "3", ""), ("GE-UTS", "Understanding the Self", "3", "")),
        _cs_row(("PATHFit 1", "Movement Competency Training", "2", ""), ("PATHFit 2", "Exercise-based Fitness Activities", "2", "PATH Fit 1")),
        _cs_row(("NSTP 1", "CWTS/ROTC 1", "3", ""), ("NSTP 2", "CWTS/ROTC 2", "3", "NSTP 1")),
        _cs_row(("Total", "", "23", ""), ("Total", "", "23", "")),
    ]

    grid.append(_merged("SECOND YEAR", 8))
    grid.append(_cs_semester_row())
    grid += [
        _cs_row(("CS 3", "Automata Theory and Formal Languages 5", "3", "CS 2, CC 2/L"), ("CS 6/L", "Computer Architecture and Organization", "2/1", "CC 4/L, CC 1/L")),
        _cs_row(("CS 4/L", "Web Systems and Technologies 6", "2/1", "CC 3/L, CC 1/L"), ("CS 7", "Algorithms and Complexities", "3", "CC 4/L, CS 3")),
        _cs_row(("CS 5/L", "Object Oriented Programming", "2/1", "CC 3/L"), ("CS 8/L", "Multimedia Technology 9", "2/1", "CC 1/L")),
        _cs_row(("CC 4/L", "Data Structures and Algorithms", "2/1", "CC 3/L, CS 2"), ("CS 9/L", "Software Engineering 1 10", "2/1", "CS 5/L, CC 5/L")),
        _cs_row(("CC 5/L", "Information Management 1 7", "2/1", "CC 3/L, CS 2"), ("GE-CW", "The Contemporary World 11", "3", "")),
        _cs_row(("AMR 2", "Calculus for Computer Science 8", "4", "GE: MMW"), ("GE-LWR", "Life and Works of Rizal", "3", "")),
        _cs_row(("GE-Elect: EM", "The Entrepreneurial Mind", "3", ""), ("GE-PS", "Palawan Studies", "3", "")),
        _cs_row(("PATHFit 3", "Dance and Sports", "2", "PATH Fit 2"), ("PATHFit 4", "Recreation", "2", "PATH Fit 2")),
        _cs_row(("Total", "", "24", ""), ("Total", "", "23", "")),
    ]

    grid.append(_merged("THIRD YEAR", 8))
    grid.append(_cs_semester_row())
    grid += [
        _cs_row(("CS 10/L", "Information Management 2 12", "2/1", "CC 5/L"), ("CS 12/L", "Software Engineering 2 18", "2/1", "CS 9/L")),
        _cs_row(("CS 11/L", "Programming Languages", "2/1", "CS 3"), ("CS 13/L", "Computer Security and Information Assurance", "2/1", "CS 6/L CS 10/L")),
        _cs_row(("CS Elect 1/L", "Intelligent Systems 1 13", "2/1", "CC 4/L, CS 3"), ("CS 14/L", "Operating Systems 19", "2/1", "CS 6/L, CS 7")),
        _cs_row(("CS Elect 2/L", "Graphics and Visual Computing 14", "2/1", "CS 5/L, CC 4/L,"), ("CS 15/L", "Networks and Communication 20", "2/1", "CC 4/L, CS 6/L")),
        _cs_row(("CC 6/L", "Application Development and Emerging Technologies", "2/1", "CS 4/L, CS 5/L"), ("CS Elect 3/L", "Intelligent Systems 2 21", "2/1", "CS Elect 1 CS 5/L AMR 1")),
        _cs_row(("GE-ET", "Ethics 15", "3", ""), ("CS Elect 4/L", "CS Elective 4 22", "2/1", "70% of the total units of the past")),
        # wrapped prerequisite continuation row, exactly as Docling emits it
        _cs_row(("", "", "", ""), ("", "", "", "semesters.")),
        _cs_row(("GE-Elect: ES", "Environmental Science 16", "3", ""), ("GE-STS", "Science, Technology and Society 23 3", "3", "")),
        _cs_row(("GE-IER", "Intensive English Review 17", "3", ""), ("Thesis 1", "Proposal Writing", "2", "CS 9/L, CS Elect 1/L")),
        _cs_row(("Total", "", "24", ""), ("Total", "", "23", "")),
    ]

    grid.append(_merged("FOURTH YEAR", 8))
    grid.append(_cs_semester_row())
    grid += [
        _cs_row(("CS 16/L", "Human Computer Interaction 24", "2/1", "CC 6/L"), ("PRACTICUM", "Practicum (300 hours)", "3", "90% of all major courses")),
        _cs_row(("CS 17", "Social Issues and Professional Practices", "3", "CC 5/L, CC 6/L"), ("Thesis 3", "Thesis Writing and Colloquium", "2", "Thesis 2")),
        _cs_row(("CS Elect 5/L", "CS Elective 5 25", "2/1", "70% of the total units of the past semesters.")),
        _cs_row(("GE-Elect: LIT", "Great Books 26", "3", "")),
        _cs_row(("Thesis 2", "Data Gathering and Writing", "2", "Thesis 1")),
        _cs_row(("Total", "", "14", ""), ("Total", "", "5", "")),
    ]

    grid.append(_merged("TOTAL: 159", 8))
    return grid


CS_TEXT_ITEMS: list[tuple[str, str]] = [
    ("section_header", "VIII. PROPOSED PROGRAM OF STUDY"),
    ("title", "PROPOSED BACHELOR OF SCIENCE IN COMPUTER SCIENCE PROGRAM OF STUDY"),
    ("text", "Proposed Date of Implementation: First Semester, SY 2025-2026"),
    ("text", "CS Elective 4 22"),
    ("text", "CS Elect 4/La. Mathematical Methods for Computational Science"),
    ("text", "CS Elect 4/Lb. IT Audits and Controls"),
    ("text", "CS Elect 4/Lc. Integrative Programming and Technologies 1"),
    ("text", "CS Elect 4/Ld. Platform Technologies"),
    ("text", "CS Elective 5 25"),
    ("text", "CS Elect 5/La. Parallel and Distributed Computing"),
    ("text", "CS Elect 5/Lb. IT Service Management"),
    ("text", "CS Elect 5/Lc. Event Driven Programming"),
    ("text", "CS Elect 5/Ld. Human Computer Interaction 2"),
    ("text", "Note: All major courses are written in italics."),
]


BSA_HEADER = [
    "Grade", "Course Code", "Course Title", "Unit/s", "Pre- Req",
    "Grade", "Course Code", "Course Title", "Unit/s", "Pre- Req",
]


def _bsa_row(left: Sequence[str], right: Sequence[str] = ("", "", "", "")) -> list[str]:
    return ["", *left, "", *right]


def _bsa_semester_row() -> list[str]:
    return ["FIRST SEMESTER"] * 5 + ["SECOND SEMESTER"] * 5


def bsa_fixture_grid() -> list[list[str]]:
    """Years 1, 2 and 5 of the Architecture prospectus (enough to pin the regressions)."""
    grid: list[list[str]] = [BSA_HEADER]

    grid.append(_merged("FIRST YEAR", 10))
    grid.append(_bsa_semester_row())
    grid += [
        _bsa_row(("AD-1/L", "Architectural Design 1-Introduction to Design", "1/1", ""), ("AD-2/L", "Architectural Design 2-Creative Design and Fundamentals", "1/1", "AD-1/L, TOA-1")),
        _bsa_row(("GR-1/L", "Architectural Visual Communications 1-Graphics 1", "1/2", ""), ("AR-INT/L", "Architectural Interiors", "2/1", "TOA-1")),
        _bsa_row(("TOA-1/L", "Theory of Architecture1", "2/1", ""), ("GR-2/L", "Architectural Visual Communications 3-Graphics 2", "1/2", "GR-1/L")),
        _bsa_row(("VT-1/L", "Architectural Visual Communications 2-Visual Techniques 1", "1/1", ""), ("VT-2/L", "Architectural Visual Communications 4-Visual Techniques 2", "1/1", "VT-1/L")),
        _bsa_row(("GE-PC", "Purposive Communication", "3", ""), ("TOA-2", "Theory of Architecture 2", "3", "TOA-1")),
        _bsa_row(("GE-PH", "Readings in Philippine History", "3", ""), ("GE-AA", "Art Appreciation", "3", "")),
        _bsa_row(("GE-UTS", "Understanding the Self", "3", ""), ("GE-MMW", "Mathematics in the Modern World", "3", "")),
        _bsa_row(("NSTP-1", "CWTS 1/ ROTC 1", "3", ""), ("Math 19", "Solid Mensuration", "2", "")),
        _bsa_row(("PATH-Fit 1", "Movement Enhancement", "2", ""), ("NSTP-2", "CWTS 2/ ROTC 2", "3", "NSTP-1")),
        _bsa_row(("", "", "", ""), ("PATH-Fit 2", "Fitness Exercises", "2", "PATH-Fit 1")),
        _bsa_row(("Total", "", "24", ""), ("Total", "", "26", "")),
    ]

    grid.append(_merged("SECOND YEAR", 10))
    grid.append(_bsa_semester_row())
    grid += [
        _bsa_row(("AD-3/L", "Architectural Design 3-Creative Design in Architectural Interiors", "1/2", "AD-2/L, TOA-2, AR-INT"), ("AD-4/L", "Architectural Design 4 - Space Planning 1", "1/2", "AD-3/L")),
        _bsa_row(("BT-1", "Building Technology 1 - Building Materials", "3", ""), ("BT-2/L", "Building Technology 2 - Construction Drawings in Wood, Steel and Concrete (1-Storey)", "2/1", "BT-1, BU-1/L")),
        _bsa_row(("BU-1/L", "Building Utilities 1-Plumbing and Sanitary Systems", "2/1", ""), ("HOA-2", "History of Architecture 2", "3", "HOA-1")),
        _bsa_row(("HOA-1", "History of Architecture 1", "3", ""), ("BES 1", "Statics of Rigid Bodies", "3", "MATH 20")),
        _bsa_row(("TD-1", "Tropical Design 1", "3", ""), ("CE 31/FB", "Elementary Surveying", "2", "MATH 19-20")),
        _bsa_row(("VT-3/L", "Architectural Visual Communications 5-Visual Techniques 3", "1/1", "VT-2/L"), ("GE-Elect: ES", "Environmental Science", "3", "")),
        _bsa_row(("Math 20", "Differential and Integral Calculus", "3", "MATH 19"), ("GE-CW", "The Contemporary World", "3", "")),
        _bsa_row(("PATH-Fit 3", "Dance and Sports", "2", "PATH-Fit 1"), ("PATH-Fit 4", "Recreation", "2", "PATH-Fit 1")),
        _bsa_row(("Total", "", "22", ""), ("Total", "", "23", "")),
    ]

    grid.append(_merged("FIFTH YEAR", 10))
    grid.append(_bsa_semester_row())
    grid += [
        _bsa_row(("AD-9/L", "Architectural Design 9 -Thesis Research Writing", "1/4", "AD-8/L"), ("D-10/L", "Architectural Design 9 - Thesis Research Application", "1/4", "AD-9/L")),
        _bsa_row(("Ar-CC 2", "Architectural Comprehensive Course 2", "3", "4th Year Standing, Arc 1"), ("PEC", "Professional Elective Course", "3", "")),
        _bsa_row(("BM/AA-1", "Business Management & Application for Architecture 1", "3", "PLN-2, PP-3"), ("SP-3", "Specialization 3 - Urban Design", "3", "D-7, PLN-2")),
        _bsa_row(("GE- PS", "Palawan Studies", "3", ""), ("BM/AA-2", "Business Management & Application for Architecture 2", "3", "PLN-2, PP-4")),
    ]
    return grid


BSA_TEXT_ITEMS: list[tuple[str, str]] = [
    ("title", "BACHELOR OF SCIENCE IN ARCHITECTURE CURRICULUM PROGRAM OF STUDY"),
    ("text", "Effective SY 2018-2019*"),
    ("text", "*BOR Resolution No. 62, s. 2019 Dated 3 July 2019"),
    ("text", "Doc. Ref. No: PSU-CIM-CUR-011B Revision No: 00 Effective Date: 11 June 2018"),
    ("text", "Total no. of units: 231"),
]


def fixture_document(grid: list[list[str]], text_items: list[tuple[str, str]]) -> LoadedDocument:
    markdown = "\n".join(text for _label, text in text_items)
    return ProspectusEvidence(
        tables=[normalized_table_from_grid(grid, 0)],
        text_items=[
            {"item_id": f"text-{index}", "label": label, "text": text, "page": None, "bbox": None}
            for index, (label, text) in enumerate(text_items)
        ],
        markdown=markdown,
        source_kind="fixture",
    )


def run_self_tests(verbose: bool = True) -> int:
    """Regression suite. Returns the number of failures (0 == healthy)."""
    failures: list[str] = []
    passed = 0

    def check(condition: bool, message: str) -> None:
        nonlocal passed
        if condition:
            passed += 1
        else:
            failures.append(message)
            if verbose:
                print(f"  FAIL: {message}")

    # ---------------- unit-level helpers --------------------------------
    check(match_year_label("SECOND YEAR") == "2nd Year", "upper-case banner must map to 2nd Year")
    check(match_year_label("Second Year") == "2nd Year", "title-case banner must map to 2nd Year")
    check(match_year_label("4th Year Standing") is None, "'4th Year Standing' must not be a banner")
    check(match_year_label("FOURTH YEAR") == "4th Year", "FOURTH YEAR must map to 4th Year")
    check(parse_units("2/1")["total"] == 3, "2/1 must parse to 3 units")
    check(parse_units("23 3")["total"] == 3, "footnote-prefixed unit cell must parse to 3")
    check(parse_units("1/2") == {"raw": "1/2", "lecture": 1, "lab": 2, "total": 3}, "1/2 lecture/lab split")
    check(split_prereq_fragments("CE 31/FB") == ["CE 31/FB"], "'/' must not split a course code")
    check(split_prereq_fragments("AD-2/L, TOA-2, AR-INT") == ["AD-2/L", "TOA-2", "AR-INT"], "comma split")
    check(is_standing_rule("70% of the total units"), "percentage rules are standing rules")
    check(relaxed_key("BT-2/L") == relaxed_key("BT-2"), "lab suffix must not break code matching")

    # ---------------- normalized evidence IR ---------------------------
    raw_ir_fixture = {
        "tables": [
            {
                "prov": [{"page_no": 1, "bbox": {"l": 0, "t": 0, "r": 800, "b": 600}}],
                "data": {
                    "num_rows": 2,
                    "num_cols": 8,
                    "table_cells": [
                        {
                            "text": "SECOND YEAR",
                            "start_row_offset_idx": 0,
                            "end_row_offset_idx": 1,
                            "start_col_offset_idx": 0,
                            "end_col_offset_idx": 8,
                            "bbox": {"l": 10, "t": 10, "r": 790, "b": 30},
                        },
                        {
                            "text": "COMM RE 12",
                            "start_row_offset_idx": 1,
                            "end_row_offset_idx": 2,
                            "start_col_offset_idx": 0,
                            "end_col_offset_idx": 1,
                            "bbox": {"l": 10, "t": 35, "r": 100, "b": 55},
                        },
                    ],
                },
            }
        ],
        "texts": [],
    }
    ir = evidence_adapter(raw_ir_fixture)
    check(len(ir.tables[0].cells) == 2, "IR: a merged cell must remain one canonical cell")
    check(
        ir.tables[0].cells[0].col_start == 0 and ir.tables[0].cells[0].col_end == 8,
        "IR: merged-cell column topology must be retained",
    )
    check(
        project_table_to_grid(ir.tables[0])[0] == ["SECOND YEAR"] * 8,
        "IR: grid projection may repeat a merged cell without changing the canonical IR",
    )
    check(
        ir.tables[0].cells[0].bbox is not None and ir.tables[0].cells[0].bbox.page == 1,
        "IR: table provenance must supply page information to cell bboxes",
    )
    check(
        normalize_evidence(raw_ir_fixture) == normalize_evidence(evidence_adapter(raw_ir_fixture)),
        "IR: serialized and already-adapted evidence must normalize identically",
    )

    raw_cells: list[dict[str, Any]] = []

    def raw_cell(text: str, row: int, col_start: int, col_end: int | None = None) -> None:
        raw_cells.append(
            {
                "text": text,
                "start_row_offset_idx": row,
                "end_row_offset_idx": row + 1,
                "start_col_offset_idx": col_start,
                "end_col_offset_idx": col_end if col_end is not None else col_start + 1,
                "bbox": {
                    "l": float(col_start * 100),
                    "t": float(row * 20),
                    "r": float((col_end if col_end is not None else col_start + 1) * 100),
                    "b": float((row + 1) * 20),
                },
            }
        )

    for column, value in enumerate(CS_HEADER):
        raw_cell(value, 0, column)
    raw_cell("FIRST YEAR", 1, 0, 8)
    raw_cell("FIRST SEMESTER", 2, 0, 4)
    raw_cell("SECOND SEMESTER", 2, 4, 8)
    for column, value in enumerate(
        ["AA 1", "Alpha", "3", "", "BB 1", "Beta", "2/1", "AA 1"]
    ):
        if value:
            raw_cell(value, 3, column)
    raw_docling_fixture = {
        "tables": [
            {
                "prov": [{"page_no": 2}],
                "data": {"num_rows": 4, "num_cols": 8, "table_cells": raw_cells},
            }
        ],
        "texts": [{"label": "title", "text": "BACHELOR OF SCIENCE IN TESTING"}],
    }
    raw_payload = build_payload(
        evidence_adapter(raw_docling_fixture),
        Path("raw_fixture_docling.json"),
        semantic_doc_path=None,
    )
    check(
        [(c["course_code"], c["semester"]) for c in raw_payload["courses"]]
        == [("AA 1", "1st Semester"), ("BB 1", "2nd Semester")],
        "raw Docling integration: structural spans must drive two-up term assignment",
    )
    check(
        all(c["provenance"]["highlightable"] for c in raw_payload["courses"]),
        "raw Docling integration: page/bbox provenance must be viewer-ready",
    )
    check(
        not raw_payload["audit"]["unclaimed_course_candidates"],
        "raw Docling integration: every high-confidence code cell must be claimed",
    )

    # ---------------- BS Computer Science (the document v1 broke) -------
    cs = build_payload(
        fixture_document(cs_fixture_grid(), CS_TEXT_ITEMS),
        Path("1_BS Computer Science_for BOR approval _rev02_v7_6 August 2025.pdf"),
        semantic_doc_path=None,
    )
    audit = cs["audit"]
    courses = {c["course_code"]: c for c in cs["courses"]}
    terms = Counter((c["year_level"], c["semester"]) for c in cs["courses"])

    check(audit["total_courses"] == 55, f"CS: expected 55 courses, got {audit['total_courses']}")
    check(
        audit["years_detected"] == ["1st Year", "2nd Year", "3rd Year", "4th Year"],
        f"CS: year banners must yield four years, got {audit['years_detected']}",
    )
    check(
        terms[("1st Year", "1st Semester")] == 8 and terms[("4th Year", "2nd Semester")] == 2,
        f"CS: term distribution wrong: {sorted(terms.items())}",
    )
    check(audit["computed_total_units"] == 159, f"CS: expected 159 units, got {audit['computed_total_units']}")
    check(audit["declared_total_units"] == 159, "CS: grand total 'TOTAL: 159' must be captured")
    check(all(t["matches"] for t in audit["term_unit_audit"]), "CS: every term checksum must match")
    check(not audit["errors"], f"CS: audit errors: {audit['errors']}")
    check(courses["CS 1"]["course_title"] == "Discrete Structures 1", "CS: footnote marker stripped, series kept")
    check(courses["CS 8/L"]["course_title"] == "Multimedia Technology", "CS: single footnote marker stripped")
    check(
        courses["GE-STS"]["course_title"] == "Science, Technology and Society"
        and courses["GE-STS"]["total_units"] == 3,
        "CS: 'Science, Technology and Society 23 3' must clean to title + 3 units",
    )
    check(courses["PATHFit 2"]["prerequisites"] == ["PATHFit 1"], "CS: 'PATH Fit 1' must resolve to PATHFit 1")
    check(courses["AMR 2"]["prerequisites"] == ["GE-MMW"], "CS: 'GE: MMW' must resolve to GE-MMW")
    check(
        courses["CS 13/L"]["prerequisites"] == ["CS 6/L", "CS 10/L"],
        "CS: separator-less prerequisite run must split into two codes",
    )
    check(
        courses["CS Elect 3/L"]["prerequisites"] == ["CS Elect 1/L", "CS 5/L", "AMR 1"],
        "CS: 'CS Elect 1 CS 5/L AMR 1' must resolve to three codes",
    )
    check(not audit["unresolved_prerequisites"], f"CS: unresolved prerequisites: {audit['unresolved_prerequisites']}")
    check(
        courses["CS Elect 4/L"]["standing_requirements"]
        and "semesters" in courses["CS Elect 4/L"]["standing_requirements"][0],
        "CS: wrapped prerequisite text must be stitched back onto the course",
    )
    check(not audit["prerequisite_ordering_violations"], "CS: no prerequisite should follow its dependent")
    check(not audit["prerequisite_cycles"], "CS: prerequisite graph must be acyclic")
    check(len(cs["elective_tracks"]) == 2, "CS: two elective pools expected")
    check(
        all(len(t["options"]) == 4 for t in cs["elective_tracks"]),
        "CS: each elective pool has four options",
    )
    check(
        courses["CS Elect 4/L"]["elective_group"] == "CS Elective 4",
        "CS: elective pool must be linked to its curriculum slot",
    )
    check(cs["degree"] == "BS Computer Science", f"CS: degree detection, got {cs['degree']}")
    check(
        cs["metadata"]["effective_school_year"] == "2025-2026",
        f"CS: SY detection, got {cs['metadata']['effective_school_year']}",
    )
    check(
        all(c["provenance"]["source_cell_ids"] for c in cs["courses"]),
        "CS: every course must retain source-cell provenance",
    )
    check(
        courses["CS 1"]["year_level"] == "1st Year"
        and courses["CS 10/L"]["year_level"] == "3rd Year",
        "CS: known term assignments must survive the section parser",
    )
    check(
        courses["Electronics/L"]["is_elective"] is False,
        "CS: Electronics/L must not be classified as an elective",
    )
    check(
        "semesters" not in courses["GE-STS"]["prerequisites_raw"].lower(),
        "CS: wrapped standing text must not leak into GE-STS",
    )

    # ---------------- BS Architecture (must not regress) ----------------
    bsa = build_payload(
        fixture_document(bsa_fixture_grid(), BSA_TEXT_ITEMS),
        Path("BSA-for-student-new-version.pdf"),
        semantic_doc_path=None,
    )
    bsa_audit = bsa["audit"]
    bsa_courses = {c["course_code"]: c for c in bsa["courses"]}

    check(
        bsa_audit["years_detected"] == ["1st Year", "2nd Year", "5th Year"],
        f"BSA: year banners wrong: {bsa_audit['years_detected']}",
    )
    check(
        bsa_courses["Ar-CC 2"]["year_level"] == "5th Year",
        "BSA: '4th Year Standing' in a prerequisite must not move the year",
    )
    check(
        bsa_courses["HOA-2"]["course_title"] == "History of Architecture 2",
        "BSA: series numbers must survive (no footnote stripping in this document)",
    )
    check(
        bsa_audit["footnotes"]["enabled"] is False,
        "BSA: footnote stripping must stay disabled for a document without markers",
    )
    check(bsa_courses["AD-1/L"]["total_units"] == 2, "BSA: 1/1 must parse to 2 units")
    check(
        bsa_courses["CE 31/FB"]["prerequisites"] == ["Math 19", "Math 20"],
        "BSA: 'MATH 19-20' must expand to two codes",
    )
    check(
        bsa_courses["BT-2/L"]["prerequisites"] == ["BT-1", "BU-1/L"],
        "BSA: 'BT-1, BU-1/L' must resolve",
    )
    check(
        any("4th Year Standing" in rule for rule in bsa_courses["Ar-CC 2"]["standing_requirements"]),
        "BSA: standing requirement must be captured as a policy rule",
    )
    check(
        "Arc 1" in bsa_courses["Ar-CC 2"]["prerequisites_unresolved"],
        "BSA: an unmatched prerequisite must be reported, not silently emitted",
    )
    check(
        "PP-4" in bsa_courses["BM/AA-2"]["prerequisites_unresolved"],
        "BSA: PP-4 does not exist in this curriculum and must be flagged",
    )
    mismatch = [
        t for t in bsa_audit["term_unit_audit"]
        if (t["year_level"], t["semester"]) == ("2nd Year", "2nd Semester")
    ]
    check(
        bool(mismatch) and mismatch[0]["matches"] is False,
        "BSA: the printed 23-unit total for 2nd Year 2nd Semester must be flagged (courses sum to 22)",
    )
    check(
        bsa["metadata"]["bor_resolution"] is not None and "62" in bsa["metadata"]["bor_resolution"],
        f"BSA: BOR resolution detection, got {bsa['metadata'].get('bor_resolution')}",
    )
    check(
        bsa["metadata"]["effective_school_year"] == "2018-2019",
        f"BSA: SY detection, got {bsa['metadata'].get('effective_school_year')}",
    )
    check(bsa["degree"] == "BS Architecture", f"BSA: degree detection, got {bsa['degree']}")
    check(
        bsa_courses["AD-3/L"]["year_level"] == "2nd Year"
        and bsa_courses["AD-3/L"]["semester"] == "1st Semester",
        "BSA: AD-3/L must resolve to 2nd Year / 1st Semester",
    )

    # ---------------- the exact v1 failure mode -------------------------
    collapsed = build_payload(
        fixture_document(
            [row for row in cs_fixture_grid() if not match_year_label(" ".join(row))], CS_TEXT_ITEMS
        ),
        Path("no_banners.pdf"),
        semantic_doc_path=None,
    )
    check(
        collapsed["audit"]["status"] == "error",
        "A document whose year banners are missing must fail the audit, not pass silently",
    )

    # ---------------- layout and graph edge cases ------------------------
    header8 = ["Course Code", "Course Title", "Unit", "Pre- requisite"] * 2

    def tiny(grid: list[list[str]]) -> dict[str, Any]:
        return build_payload(
            fixture_document(grid, [("title", "BACHELOR OF SCIENCE IN TESTING")]),
            Path("edge.pdf"),
            semantic_doc_path=None,
        )

    architecture_bleed = tiny(
        [
            BSA_HEADER,
            _merged("SECOND YEAR", 10),
            _bsa_semester_row(),
            _bsa_row(
                (
                    "AD-3/L",
                    "Architectural Design 3-Creative Design in Architectural Interiors",
                    "1/2",
                    "SECOND AD-2/L, TOA-2",
                )
            ),
        ]
    )
    architecture_ad3 = architecture_bleed["courses"][0]
    check(
        architecture_ad3["year_level"] == "2nd Year"
        and architecture_ad3["semester"] == "1st Semester",
        "Architecture bleed: AD-3/L must retain the explicit 2Y1S section",
    )
    check(
        "SECOND" not in architecture_ad3["prerequisites_raw"].upper()
        and architecture_ad3["provenance"]["discarded_fragments"],
        "Architecture bleed: structural SECOND must be removed and recorded",
    )

    ab_communication = tiny(
        [
            header8,
            _merged("SECOND YEAR", 8),
            _cs_semester_row(),
            ["GE - STS", "Science, Technology and Society", "3", "", "", "", "", ""],
            _merged("THIRD YEAR", 8),
            _cs_semester_row(),
            [
                "COMM RE 12", "Communication Research 2", "3", "COMM RE 11",
                "COMM CRC 15", "Communication and Culture 15", "3", "",
            ],
        ]
    )
    ab_courses = {course["course_code"]: course for course in ab_communication["courses"]}
    check(
        ab_courses["GE - STS"]["year_level"] == "2nd Year"
        and ab_courses["GE - STS"]["semester"] == "1st Semester",
        "AB Communication: GE - STS must be recovered in 2Y1S",
    )
    check(
        ab_courses["COMM RE 12"]["year_level"] == "3rd Year"
        and ab_courses["COMM RE 12"]["semester"] == "1st Semester",
        "AB Communication: COMM RE 12 must be recovered in 3Y1S",
    )
    check(
        ab_courses["COMM CRC 15"]["year_level"] == "3rd Year"
        and ab_courses["COMM CRC 15"]["semester"] == "2nd Semester",
        "AB Communication: COMM CRC 15 must be recovered in 3Y2S",
    )

    no_semester = tiny(
        [
            ["Course Code", "Course Title", "Unit", "Pre-requisite"],
            _merged("FIRST YEAR", 4),
            ["ZZ 1", "Zulu", "3", ""],
        ]
    )
    check(
        no_semester["courses"][0]["semester"] is None
        and no_semester["audit"]["status"] == "error",
        "missing semester evidence must remain null and route the document to review",
    )
    check(
        not no_semester["prolog"]["clauses"]
        and not no_semester["rag"]["semantic_chunks"]
        and no_semester["audit"]["promotion_status"] == "REVIEW_REQUIRED",
        "failed audit must emit zero production Prolog/RAG artifacts",
    )

    no_semester_evidence = fixture_document(
        [
            ["Course Code", "Course Title", "Unit", "Pre-requisite"],
            _merged("FIRST YEAR", 4),
            ["ZZ 1", "Zulu", "3", ""],
        ],
        [("title", "BACHELOR OF SCIENCE IN TESTING")],
    )

    def unsupported_repair(packet: Mapping[str, Any]) -> Mapping[str, Any]:
        code_cell = next(
            cell["cell_id"] for cell in packet["cells"] if cell["text"] == "ZZ 1"
        )
        return {
            "fields": {
                "semester": {"value": "1st Semester", "evidence": [code_cell]},
            },
            "discarded_fragments": [],
            "ambiguous": False,
        }

    rejected_repair = build_payload(
        no_semester_evidence,
        Path("unsupported_repair.pdf"),
        semantic_doc_path=None,
        repair_provider=unsupported_repair,
    )
    check(
        rejected_repair["courses"][0]["semester"] is None
        and rejected_repair["audit"]["invalid_repairs"],
        "an LLM repair may not introduce a semester unsupported by structural evidence",
    )

    split_course = tiny(
        [
            ["Course Code", "Course Title", "Unit", "Pre-requisite"],
            _merged("FIRST YEAR", 4),
            _merged("FIRST SEMESTER", 4),
            ["AA 1", "", "", ""],
            ["", "Alpha", "3", ""],
        ]
    )
    check(
        len(split_course["courses"]) == 1
        and split_course["courses"][0]["course_title"] == "Alpha"
        and split_course["courses"][0]["total_units"] == 3,
        "course assembly must join a code row with adjacent title/unit evidence",
    )

    headerless = tiny(
        [
            _merged("FIRST YEAR", 8),
            _cs_semester_row(),
            ["AA 1", "Alpha", "3", "", "BB 1", "Beta", "2/1", "AA 1"],
            _merged("SECOND YEAR", 8),
            _cs_semester_row(),
            ["AA 2", "Alpha 2", "3", "AA 1", "", "", "", ""],
        ]
    )
    check(
        [c["year_level"] for c in headerless["courses"]] == ["1st Year", "1st Year", "2nd Year"],
        "a table with no header row must still fall back to a positional layout",
    )

    merged_semesters = tiny(
        [
            header8,
            _merged("FIRST YEAR", 8),
            _merged("FIRST SEMESTER SECOND SEMESTER", 8),
            ["AA 1", "Alpha", "3", "", "BB 1", "Beta", "3", ""],
            header8,  # header repeats after a page break
            _merged("SECOND YEAR", 8),
            _merged("FIRST SEMESTER SECOND SEMESTER", 8),
            ["AA 2", "Alpha 2", "3", "AA 1", "BB 2", "Beta 2", "3", "BB 1"],
        ]
    )
    check(
        [(c["year_level"], c["semester"]) for c in merged_semesters["courses"]]
        == [
            ("1st Year", "1st Semester"), ("1st Year", "2nd Semester"),
            ("2nd Year", "1st Semester"), ("2nd Year", "2nd Semester"),
        ],
        "a fully merged semester row must be assigned across the column groups in order",
    )

    summer = tiny(
        [
            ["Course Code", "Course Title", "Unit", "Pre-requisite"],
            _merged("THIRD YEAR", 4),
            _merged("SUMMER", 4),
            ["OJT 1", "Practicum", "3", "60% of all major courses"],
            ["Total", "", "3", ""],
        ]
    )
    check(
        summer["courses"][0]["semester"] == "Summer"
        and summer["courses"][0]["standing_requirements"] == ["60% of all major courses."],
        "single-block tables, Summer terms and percentage rules must all survive",
    )

    cyclic = tiny(
        [
            header8,
            _merged("FIRST YEAR", 8),
            _cs_semester_row(),
            ["AA 1", "Alpha", "3", "AA 2", "AA 2", "Bravo", "3", "AA 1"],
            ["AA 1", "Alpha duplicate", "3", "", "", "", "", ""],
        ]
    )
    check(
        cyclic["audit"]["prerequisite_cycles"] == [["AA 1", "AA 2", "AA 1"]],
        "a cycle must be reported even when a duplicated row would overwrite its edges",
    )
    check(
        [d["course_code"] for d in cyclic["audit"]["duplicate_course_codes"]] == ["AA 1"],
        "duplicated course codes must be reported",
    )
    check(cyclic["audit"]["status"] == "error", "a cyclic prerequisite graph must fail the audit")

    no_banner = tiny([header8, ["ZZ 1", "Zulu", "3", "", "", "", "", ""]])
    check(
        not no_banner["courses"]
        and no_banner["audit"]["status"] == "error"
        and any("before any year banner" in e for e in no_banner["audit"]["errors"]),
        "courses appearing before any banner must fail closed instead of guessing 1st Year",
    )

    # ---------------- Prolog escaping -----------------------------------
    check(pl_atom("Ethics") == "'Ethics'", "atom quoting")
    check(pl_atom("Bachelor's Degree") == "'Bachelor''s Degree'", "ISO quote doubling inside atoms")

    if verbose:
        total = passed + len(failures)
        print(f"\nSelf-test: {passed}/{total} checks passed.")
        if failures:
            print("Failures:")
            for message in failures:
                print(f"  - {message}")
    return len(failures)
