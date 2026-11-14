"""Repeated projections of one source course must not create extra units."""
from dataclasses import replace

from backend.bintanong_tools.bintanong_jsonifer_prolog import bintanong_prospectus_jsonifier as parser


def spanning_course_evidence(*, separate_courses=False, shared_prerequisite=False):
    grid = [
        ["Course Code", "Course Title", "Units", "Prerequisites"],
        ["FOURTH YEAR", "", "", ""],
        ["SECOND SEMESTER", "", "", ""],
        ["SYN 401", "Synthetic placement", "6", "All prior courses"],
        ["SYN 401", "Synthetic placement", "6", "in the program"],
        ["", "", "", ""],
        ["TOTAL", "", "6", ""],
    ]
    evidence = parser.evidence_from_grids([grid])
    table = evidence.tables[0]
    cells = []
    for cell in table.cells:
        if cell.row_start in (1, 2):
            cell = replace(cell, col_end=4)
        if not separate_courses and cell.row_start in (3, 4) and cell.col_start < 3:
            if cell.row_start == 4:
                continue
            cell = replace(cell, row_end=6)
        if shared_prerequisite and cell.col_start == 3 and cell.row_start in (3, 4):
            if cell.row_start == 4:
                continue
            cell = replace(cell, row_end=6)
        cells.append(cell)
    table.cells = cells
    return evidence


def test_one_spanning_course_preserves_both_prerequisite_fragments():
    evidence = spanning_course_evidence()
    result = parser.parse_curriculum_evidence(evidence)

    assert len(result.courses) == 1
    course = result.courses[0]
    assert course["course_code"] == "SYN 401"
    assert course["units"]["total"] == 6
    assert course["prerequisites_raw"] == "All prior courses in the program"
    prereq_ids = {cell.cell_id for cell in evidence.tables[0].cells
                  if cell.col_start == 3 and cell.row_start in (3, 4)}
    assert prereq_ids <= set(course["provenance"]["source_cell_ids"])
    assert result.declared_term_units == {("4th Year", "2nd Semester"): 6}


def test_identical_text_in_distinct_source_cells_remains_two_courses():
    result = parser.parse_curriculum_evidence(spanning_course_evidence(separate_courses=True))

    assert len(result.courses) == 2
    assert [course["units"]["total"] for course in result.courses] == [6, 6]
    audit = parser.build_audit(result.courses, result, {}, [])
    assert audit["status"] == "error"


def test_repeated_prerequisite_cell_is_not_appended_again():
    result = parser.parse_curriculum_evidence(spanning_course_evidence(shared_prerequisite=True))

    assert len(result.courses) == 1
    assert result.courses[0]["prerequisites_raw"] == "All prior courses"


def test_identical_course_fields_with_distinct_cell_ids_are_not_deduplicated():
    evidence = spanning_course_evidence(separate_courses=True)
    table = evidence.tables[0]
    table.cells = [replace(cell, text="All prior courses", raw_text="All prior courses")
                   if cell.row_start == 4 and cell.col_start == 3 else cell
                   for cell in table.cells]

    result = parser.parse_curriculum_evidence(evidence)

    assert len(result.courses) == 2


def test_spanning_course_with_missing_title_is_not_repeated():
    evidence = spanning_course_evidence()
    table = evidence.tables[0]
    table.cells = [cell for cell in table.cells
                   if not (cell.row_start >= 3 and cell.col_start == 1)]

    result = parser.parse_curriculum_evidence(evidence)

    assert len(result.courses) == 1
    assert result.courses[0]["course_title"] == ""
    assert result.courses[0]["prerequisites_raw"] == "All prior courses in the program"
