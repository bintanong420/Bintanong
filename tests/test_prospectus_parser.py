from __future__ import annotations

from dataclasses import replace
import unittest

from backend.bintanong_tools.bintanong_jsonifer_prolog import bintanong_prospectus_jsonifier as parser


# Actual Docling cell topology, checked against the original PDFs, physical page 1.
# Clinical Psychology t0-c124..126 and c129..131; Values Education c200..202/c205.
MERGED_ROWS = [[(124,
   {'bbox': {'l': 58.26687243580818,
             't': 519.1218705177307,
             'r': 97.04081428050995,
             'b': 530.2964782714844,
             'coord_origin': 'TOPLEFT'},
    'row_span': 1,
    'col_span': 1,
    'start_row_offset_idx': 27,
    'end_row_offset_idx': 28,
    'start_col_offset_idx': 1,
    'end_col_offset_idx': 2,
    'text': 'Psych 9 Psych 10',
    'column_header': False,
    'row_header': True,
    'row_section': False,
    'fillable': False}),
  (125,
   {'bbox': {'l': 103.4568263888359,
             't': 518.7374777793884,
             'r': 210.57115840911865,
             'b': 529.6185975074768,
             'coord_origin': 'TOPLEFT'},
    'row_span': 1,
    'col_span': 1,
    'start_row_offset_idx': 27,
    'end_row_offset_idx': 28,
    'start_col_offset_idx': 2,
    'end_col_offset_idx': 3,
    'text': 'Abnormal Psychology Field Methods in Psychology',
    'column_header': False,
    'row_header': True,
    'row_section': False,
    'fillable': False}),
  (126,
   {'bbox': {'l': 227.85001027584076,
             't': 520.9992158412933,
             'r': 238.53287708759308,
             'b': 531.9366676807404,
             'coord_origin': 'TOPLEFT'},
    'row_span': 1,
    'col_span': 1,
    'start_row_offset_idx': 27,
    'end_row_offset_idx': 28,
    'start_col_offset_idx': 3,
    'end_col_offset_idx': 4,
    'text': '3 5',
    'column_header': False,
    'row_header': False,
    'row_section': False,
    'fillable': False})],
 [(129,
   {'bbox': {'l': 60.14044493436813,
             't': 536.6692852973938,
             'r': 91.55375748872757,
             'b': 561.6814254143646,
             'coord_origin': 'TOPLEFT'},
    'row_span': 1,
    'col_span': 1,
    'start_row_offset_idx': 28,
    'end_row_offset_idx': 29,
    'start_col_offset_idx': 1,
    'end_col_offset_idx': 2,
    'text': 'Psych Elect GE-IER',
    'column_header': False,
    'row_header': True,
    'row_section': False,
    'fillable': False}),
  (130,
   {'bbox': {'l': 104.33584272861481,
             't': 539.1384589672089,
             'r': 203.06834495067596,
             'b': 561.6814254143646,
             'coord_origin': 'TOPLEFT'},
    'row_span': 1,
    'col_span': 1,
    'start_row_offset_idx': 28,
    'end_row_offset_idx': 29,
    'start_col_offset_idx': 2,
    'end_col_offset_idx': 3,
    'text': 'Psych Electives Intensive English Review',
    'column_header': False,
    'row_header': True,
    'row_section': False,
    'fillable': False}),
  (131,
   {'bbox': {'l': 229.5551974773407,
             't': 535.5813477039337,
             'r': 239.65734362602234,
             'b': 561.6814254143646,
             'coord_origin': 'TOPLEFT'},
    'row_span': 1,
    'col_span': 1,
    'start_row_offset_idx': 28,
    'end_row_offset_idx': 29,
    'start_col_offset_idx': 3,
    'end_col_offset_idx': 4,
    'text': '3 3',
    'column_header': False,
    'row_header': False,
    'row_section': False,
    'fillable': False})],
 [(200,
   {'bbox': {'l': 70.72262418270111,
             't': 756.9953705072403,
             'r': 98.60860413312912,
             'b': 775.3624972375691,
             'coord_origin': 'TOPLEFT'},
    'row_span': 1,
    'col_span': 1,
    'start_row_offset_idx': 33,
    'end_row_offset_idx': 34,
    'start_col_offset_idx': 1,
    'end_col_offset_idx': 2,
    'text': 'Ed 12 FS 2',
    'column_header': False,
    'row_header': False,
    'row_section': False,
    'fillable': False}),
  (201,
   {'bbox': {'l': 104.03872340917587,
             't': 757.4934477806091,
             'r': 190.302976667881,
             'b': 769.0927278995514,
             'coord_origin': 'TOPLEFT'},
    'row_span': 1,
    'col_span': 1,
    'start_row_offset_idx': 33,
    'end_row_offset_idx': 34,
    'start_col_offset_idx': 2,
    'end_col_offset_idx': 3,
    'text': 'Environmental Education Field Study 2',
    'column_header': False,
    'row_header': False,
    'row_section': False,
    'fillable': False}),
  (202,
   {'bbox': {'l': 242.42874038219452,
             't': 757.6142390966415,
             'r': 252.99689531326294,
             'b': 775.3624972375691,
             'coord_origin': 'TOPLEFT'},
    'row_span': 1,
    'col_span': 1,
    'start_row_offset_idx': 33,
    'end_row_offset_idx': 34,
    'start_col_offset_idx': 3,
    'end_col_offset_idx': 4,
    'text': '3 3',
    'column_header': False,
    'row_header': False,
    'row_section': False,
    'fillable': False}),
  (205,
   {'bbox': {'l': 270.7951205968857,
             't': 754.9599822759628,
             'r': 305.9233261346817,
             'b': 779.1208318471909,
             'coord_origin': 'TOPLEFT'},
    'row_span': 1,
    'col_span': 1,
    'start_row_offset_idx': 33,
    'end_row_offset_idx': 34,
    'start_col_offset_idx': 4,
    'end_col_offset_idx': 5,
    'text': 'All Prof.',
    'column_header': False,
    'row_header': False,
    'row_section': False,
    'fillable': False})]]


class MergedCourseRowsTests(unittest.TestCase):
    def test_bscs_standing_fragment_does_not_become_next_course_prerequisite(self):
        # Original new BSCS PDF, page 1: Docling assigns the final word of
        # CS Elect 4/L's standing to the following GE-STS grid row.
        grid = [[""] * 8 for _ in range(32)]
        grid[0] = ["Course Code", "Course Title", "Units", "Prerequisites",
                   "Course Code", "Course Title", "Units", "Prerequisites"]
        grid[1][0] = "THIRD YEAR"
        grid[2][0], grid[2][4] = "FIRST SEMESTER", "SECOND SEMESTER"
        evidence = parser.evidence_from_grids([grid])
        evidence.tables[0].cells = [
            replace(cell, col_end=8) if cell.row_start == 1
            else replace(cell, col_end=cell.col_start + 4) if cell.row_start == 2
            else cell for cell in evidence.tables[0].cells
        ]
        raw = (
            (177, 30, 4, "CS Elect 4/L", 314.79, 540.96, 346.23, 551.28),
            (178, 30, 5, "CS Elective 4 22", 357.47, 540.89, 411.13, 551.03),
            (179, 30, 6, "2/1", 494.19, 541.02, 506.77, 551.50),
            (180, 30, 7, "70% of the total units of the past", 520.96, 540.83, 547.42, 551.15),
            (181, 31, 7, "semesters", 514.92, 555.86, 553.04, 566.79),
            (185, 31, 4, "GE-STS", 318.62, 556.68, 343.20, 566.87),
            (186, 31, 5, "Science, Technology and Society", 351.27, 556.48, 468.42, 566.92),
            (187, 31, 6, "23 3", 471.55, 556.82, 505.29, 567.34),
        )
        source = [{"text": text, "row_span": 1, "col_span": 1,
                   "start_row_offset_idx": row, "end_row_offset_idx": row + 1,
                   "start_col_offset_idx": col, "end_col_offset_idx": col + 1,
                   "bbox": {"l": left, "t": top, "r": right, "b": bottom,
                            "coord_origin": "TOPLEFT"}}
                  for _, row, col, text, left, top, right, bottom in raw]
        normalized = parser.docling_to_normalized_table(
            {"table_cells": source}, 0, {"prov": [{"page_no": 1}]})
        evidence.tables[0].cells.extend(
            replace(cell, cell_id=f"t0-c{item[0]}")
            for item, cell in zip(raw, normalized.cells)
        )
        result = parser.parse_curriculum_evidence(evidence)
        courses = {course["course_code"]: course for course in result.courses}
        self.assertIn("GE-STS", courses, (list(courses), result.sections, result.anomalies))
        self.assertNotIn("semesters", courses["GE-STS"]["prerequisites_raw"].lower())
        issues = [item for item in result.anomalies
                  if item["type"] == "ambiguous_adjacent_prerequisite_fragment"]
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["page"], 1)
        self.assertIn("t0-c181", issues[0]["source_cell_ids"])
        self.assertTrue(all(cell["bbox"] for cell in issues[0]["source_cells"]))
        self.assertEqual(parser.build_audit(result.courses, result, {}, [])["status"], "error")

    def test_merged_source_rows_are_blocked_with_complete_evidence(self):
        for raw_cells in MERGED_ROWS:
            with self.subTest(code=raw_cells[0][1]["text"]):
                row = raw_cells[0][1]["start_row_offset_idx"]
                grid = [[""] * 10 for _ in range(row + 3)]
                grid[0] = ["", "Course Code", "Course Title", "Units", "Prerequisites",
                           "", "Course Code", "Course Title", "Units", "Prerequisites"]
                grid[1][1] = "FOURTH YEAR"
                grid[2][1], grid[2][6] = "FIRST SEMESTER", "SECOND SEMESTER"
                # A source-real second-term duplicate Ed 12 must remain a separate course.
                grid[row][6:10] = ["Ed 12", "Integrating Course in Education", "3", ""]
                evidence = parser.evidence_from_grids([grid])
                table = evidence.tables[0]
                table.cells = [replace(cell, col_end=10) if cell.row_start == 1
                               else replace(cell, col_end=cell.col_start + 4) if cell.row_start == 2
                               else cell for cell in table.cells]
                normalized = parser.docling_to_normalized_table(
                    {"table_cells": [cell for _, cell in raw_cells]}, 0,
                    {"prov": [{"page_no": 1}]},
                )
                cells = [replace(cell, cell_id=f"t0-c{source_id}")
                         for (source_id, _), cell in zip(raw_cells, normalized.cells)]
                # Keep the source row/column spans, raw text, and native source boxes.
                table.cells = [replace(cell, cell_id="control-" + cell.cell_id)
                               for cell in table.cells] + cells
                result = parser.parse_curriculum_evidence(evidence)
                anomalies = [a for a in result.anomalies
                             if a["type"] == "multiple_course_codes_in_cell"]
                self.assertEqual(len(anomalies), 1)
                self.assertEqual(set(anomalies[0]["source_cell_ids"]),
                                 {cell.cell_id for cell in cells})
                self.assertEqual(anomalies[0]["page"], 1)
                self.assertEqual({cell["cell_id"] for cell in anomalies[0]["source_cells"]},
                                 {cell.cell_id for cell in cells})
                self.assertTrue(all(cell["page"] == 1 and cell["bbox"]
                                    for cell in anomalies[0]["source_cells"]))
                self.assertFalse(any(set(c["provenance"]["source_cell_ids"]) &
                                     {cell.cell_id for cell in cells}
                                     for c in result.courses))
                self.assertTrue(any(c["course_code"] == "Ed 12" for c in result.courses))
                audit = parser.build_audit(result.courses, result, {}, [])
                self.assertEqual(audit["status"], "error")
                self.assertIn(anomalies[0], audit["structural_anomalies"])

    def test_single_multipart_codes_are_not_merged_rows(self):
        for code in ("GE Elect 1", "COMM RE 12", "CE 31/FB 2", "Psych 16-A",
                     "Ed 12", "GE-Elect: ES", "PetE 42 E2"):
            with self.subTest(code=code):
                self.assertIsNone(parser._two_course_codes_in_cell(code))

    def test_spaced_slash_suffix_stays_in_code(self):
        # Original PDF code cells: old ComSci CC 3/L; Culinary HPC 4/FL 1;
        # Tourism TPC 1/FL 1. Docling inserts spaces around the slash.
        cases = (
            ("CC 3 / L", "Computer Programming 2", "CC 3/L"),
            ("HPC 4 / FL 1", "Foreign Language 1", "HPC 4/FL 1"),
            ("TPC 1 / FL 1", "Foreign Language 1", "TPC 1/FL 1"),
        )
        for raw_code, title, expected_code in cases:
            with self.subTest(raw_code=raw_code):
                grid = [["", "", "", "", "Course Code", "Course Title", "Units", "Prerequisites"],
                        ["", "", "", "", raw_code, title, "3", ""]]
                table = parser.evidence_from_grids([grid]).tables[0]
                group = parser.ColumnGroup(1, 4, 5, 6, 7)
                fields = parser._row_field_candidates(table, 1, group, [group])
                self.assertEqual(fields["code"].value, expected_code)
                self.assertEqual(fields["title"].value, title)


if __name__ == "__main__":
    unittest.main()
