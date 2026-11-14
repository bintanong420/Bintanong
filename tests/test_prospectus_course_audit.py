import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "prospectus_course_audit", Path(__file__).resolve().parents[1] / "scripts" / "prospectus_course_audit.py"
)
audit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(audit)


def cell(cell_id, text, col, bbox=None, page=1):
    return {"cell_id": cell_id, "text": text, "col_start": col, "col_end": col + 1, "page": page, "bbox": bbox}


def course(code="CS 101", title="Intro to Computing", units_raw="3/2", lec=3, lab=2, total=5, prereq="", **extra):
    cells = [cell("t0-c1", code, 1), cell("t0-c2", title, 2), cell("t0-c3", units_raw, 3), cell("t0-c4", prereq, 4)]
    base = {
        "course_code": code, "course_title": title, "title_raw": title, "footnote_marker": None,
        "units": {"raw": units_raw, "lecture": lec, "lab": lab, "total": total},
        "prerequisites_raw": prereq,
        "provenance": {"page": 1, "source_cell_ids": [c["cell_id"] for c in cells], "source_cells": cells},
        "_source": {"table_index": 0, "row_index": 1, "column_group": 0},
    }
    base.update(extra)
    return base


LAYOUT = [{"table_index": 0, "column_groups": [{"index": 0, "code_idx": 1, "title_idx": 2, "unit_idx": 3, "prereq_idx": 4}]}]


def md_for(*cells):
    rows = "".join(f'<td data-cell="{i}" data-page="1">{t}</td>' for i, t in cells)
    return f'<table data-table="0"><tr>{rows}</tr></table>'


def by_check(rows):
    return {r["check"]: r for r in rows}


def md_cells(c, **override):
    texts = {"t0-c1": c["course_code"], "t0-c2": c["course_title"], "t0-c3": c["units"]["raw"], "t0-c4": c["prerequisites_raw"]}
    texts.update(override)
    return audit.parse_markup(md_for(*texts.items()))


def test_matching_course_passes_md_checks_and_units_are_transformed_not_matched():
    c = course(prereq="CS 100")
    r = by_check(audit.check_course_md(c, md_cells(c), LAYOUT))
    assert r["A_prov"]["status"] == "match" and r["A_code"]["status"] == "match"
    assert r["A_title"]["status"] == "match" and r["A_prereq"]["status"] == "match"
    assert r["A_lecture"]["status"] == "transformed" and r["A_total"]["status"] == "transformed"


def test_title_absent_from_its_cell_fails_and_missing_cell_fails_provenance():
    c = course()
    r = by_check(audit.check_course_md(c, md_cells(c, **{"t0-c2": "Something Else"}), LAYOUT))
    assert r["A_title"]["status"] == "fail"
    gone = audit.parse_markup(md_for(("t0-c1", "CS 101")))
    assert by_check(audit.check_course_md(c, gone, LAYOUT))["A_prov"]["status"] == "fail"


def test_footnote_stripped_title_is_transformed_and_unit_sum_mismatch_fails():
    c = course(title="Intro", total=6)
    c["title_raw"], c["footnote_marker"] = "Intro*", "*"
    r = by_check(audit.check_course_md(c, md_cells(c, **{"t0-c2": "Intro*"}), LAYOUT))
    assert r["A_title"]["status"] == "transformed"
    assert r["A_total"]["status"] == "fail"


def test_loose_tier_is_separate_from_match():
    c = course(title="Visual Communications 3-Graphics 2")
    r = by_check(audit.check_course_md(c, md_cells(c, **{"t0-c2": "Visual Communications 3- Graphics 2"}), LAYOUT))
    assert r["A_title"]["status"] == "loose"


def test_pdf_title_strict_loose_and_fail():
    c = course()
    page = "CS 101 Intro to Computing 3/2"
    assert by_check(audit.check_course_pdf(c, page, None, None))["B_title"]["status"] == "match"
    wrapped = "CS 101 Intro to Com-\r\nputing 3/2"
    assert by_check(audit.check_course_pdf(c, wrapped, None, None))["B_title"]["status"] == "loose"
    r = by_check(audit.check_course_pdf(c, "CS 101 Different Title 3/2", None, None))
    assert r["B_title"]["status"] == "fail" and "CS 101" in r["B_title"]["pdf"]
    assert r["B_units"]["status"] == "not_checked"


def test_pdf_units_read_from_character_boxes_at_the_unit_cell():
    c = course()
    c["provenance"]["source_cells"][2]["bbox"] = [100.0, 10.0, 120.0, 20.0]  # top-left frame, page 100 high
    chars = [(ch, 100 + 5 * i, 80.0, 105 + 5 * i, 90.0) for i, ch in enumerate("3/2")]  # y up: 10..20 from top
    assert by_check(audit.check_course_pdf(c, "x", chars, 100.0))["B_units"]["status"] == "match"
    bad = [(ch, 100 + 5 * i, 80.0, 105 + 5 * i, 90.0) for i, ch in enumerate("1/1")]
    assert by_check(audit.check_course_pdf(c, "x", bad, 100.0))["B_units"]["status"] == "fail"
    assert by_check(audit.check_course_pdf(c, "x", [], 100.0))["B_units"]["status"] == "not_checked"


def test_unclaimed_printed_code_is_silent_and_audit_listed_code_is_flagged():
    c = course(prereq="CS 100")
    page = "CS 101 Intro to Computing 3/2 CS 100\r\nZZ-999 Ghost Course 3"
    md = md_cells(c)
    rows = audit.check_pdf_missed([c], {}, page, md, page_no=1)
    silent = [r for r in rows if r["status"] == "silent"]
    assert [r["json"] for r in silent] == ["ZZ-999"]
    flagged_audit = {"structural_anomalies": [{"candidate_codes": ["ZZ-999"], "source_cell_ids": [], "source_cells": []}]}
    rows = audit.check_pdf_missed([c], flagged_audit, page, md, page_no=1)
    assert [r["status"] for r in rows if r["json"] == "ZZ-999"] == ["flagged"]


def test_prerequisite_mentions_are_not_silent_misses():
    c = course(prereq="CS 100")
    page = "CS 101 Intro to Computing 3/2 CS 100"
    assert audit.check_pdf_missed([c], {}, page, md_cells(c), page_no=1) == []


def test_md_code_cell_nobody_claims_is_silent_unless_audit_lists_it():
    c = course()
    md = md_cells(c)
    md.cells["t0-c9"] = "ZZ-999"
    rows = audit.check_md_unclaimed([c], {}, md)
    assert [(r["check"], r["status"], r["cell"]) for r in rows] == [("D", "silent", "t0-c9")]
    listed = {"unclaimed_course_candidates": [{"code": "ZZ-999", "cell_ids": ["t0-c9"]}]}
    assert [r["status"] for r in audit.check_md_unclaimed([c], listed, md)] == ["flagged"]


def test_parse_markup_reads_cells_unplaced_cells_and_br():
    md = (
        '<td data-cell="a" data-page="1">Line one<br>two &amp; three</td>'
        '<p data-unplaced-cell="b" data-page="1">X</p><h2 data-item="text-0" data-label="x">Head</h2>'
    )
    parsed = audit.parse_markup(md)
    assert parsed.cells == {"a": "Line one\ntwo & three", "b": "X"} and parsed.items == {"text-0": "Head"}


def test_pdf_title_cleaned_by_parser_is_transformed_when_only_the_printed_text_is_in_the_pdf():
    c = course(title="Ethics")
    c["title_raw"] = "FIRST Ethics"
    r = by_check(audit.check_course_pdf(c, "CS 101 FIRST Ethics 3/2", None, None))
    assert r["B_title"]["status"] == "match"  # the stored title itself is printed
    r = by_check(audit.check_course_pdf(c, "CS 101 Morals 3/2", None, None))
    assert r["B_title"]["status"] == "fail"
    c["title_raw"], c["course_title"] = "Intro*", "Introduction"
    r = by_check(audit.check_course_pdf(c, "CS 101 Intro* 3/2", None, None))
    assert r["B_title"]["status"] == "transformed"
