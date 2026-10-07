import copy

import pytest

from backend.bintanong_tools.prospectus_extractor.course_checks import PdfPage
from backend.bintanong_tools.prospectus_extractor.placement import locate_in_page
from backend.bintanong_tools.prospectus_extractor.verify import verify_candidate

import fixer_fixtures as fx
from fixer_fixtures import by_code, kinds, section


def test_unclaimed_codes_above_the_first_banner_stay_unplaced():
    payload = fx.innovation()
    v = verify_candidate(payload)
    unplaced = section(v, "SU")
    assert [r.item["code"] for r in unplaced.rows] == ["ENTRE 7", "GE-IER", "ENTRE 9"]  # ENTRE 9 sits 17 pt above FOURTH YEAR
    assert [r.rid for r in unplaced.rows] == ["SU-U1", "SU-U2", "SU-U3"] and unplaced.health == "broken"
    assert v.health == "broken"


def test_an_unclaimed_code_below_a_sections_last_row_is_attached_to_that_section():
    payload = fx.innovation()
    box = {"code": "ENTRE 99", "cell_ids": ["t0-c90"], "table_index": 0, "page": 1, "bbox": [71.2, 822.0, 98.3, 832.0]}
    right = {"code": "ENTRE 98", "cell_ids": ["t0-c91"], "table_index": 0, "page": 1, "bbox": [345.5, 822.0, 372.6, 832.0]}
    far = {"code": "ENTRE 97", "cell_ids": ["t0-c92"], "table_index": 0, "page": 1, "bbox": [71.2, 900.0, 98.3, 910.0]}
    payload["audit"]["unclaimed_course_candidates"] = [box, right, far]
    v = verify_candidate(payload)
    assert [r.item["code"] for r in section(v, "S2").rows if r.item] == ["ENTRE 99"]
    assert [r.item["code"] for r in section(v, "S3").rows if r.item] == ["ENTRE 98"]
    assert [r.item["code"] for r in section(v, "SU").rows] == ["ENTRE 97"]


def test_other_audit_anomalies_become_rows_too_but_covered_ones_do_not():
    payload = fx.innovation()
    payload["audit"]["unclaimed_course_candidates"] = []
    payload["audit"]["structural_anomalies"] = [
        {"type": "multiple_course_codes_in_cell", "table_index": 0, "page": 1, "candidate_codes": ["GE-PH", "GE-STS"],
         "reason": "one source cell contains two codes", "source_cell_ids": ["t0-c70"],
         "source_cells": [{"cell_id": "t0-c70", "bbox": [71.2, 822.0, 98.3, 832.0]}]},
        {"type": "unclaimed_course_candidate", "source_cell_ids": ["t0-c0"]},
        {"type": "course_without_verified_semester", "source_cell_ids": ["t0-c1"]},
    ]
    v = verify_candidate(payload)
    rows = [r for s in v.sections for r in s.rows if r.item]
    assert [(r.item["code"], kinds(r)) for r in rows] == [("GE-PH, GE-STS", ["audit_anomaly"])]
    assert rows[0].rid.startswith("S2-U")


# --- PDF text layer (check 3) and silent printed codes

def test_title_and_code_not_in_the_pdf_text_are_warnings_and_only_with_the_pdf():
    payload = fx.architecture()
    assert not any(kinds(r) for s in verify_candidate(payload).sections for r in s.rows)
    v = verify_candidate(payload, {1: PdfPage(fx.ARCH_PAGE_TEXT)})
    rows = by_code(payload, v)
    assert v.pdf_checked is True
    assert kinds(rows["TOA-1/L"]) == ["title_not_in_pdf"] and kinds(rows["GE-PC"]) == ["title_not_in_pdf"]
    assert kinds(rows["AD-1/L"]) == [] and kinds(rows["VT-1/L"]) == []   # stored title is the start of the printed one
    assert kinds(rows["TOA-2"]) == ["title_not_in_pdf"] and kinds(rows["VT-2/L"]) == ["title_not_in_pdf"] and kinds(rows["AD-2/L"]) == []
    assert section(v, "S1").health == "review" and section(v, "S2").health == "review"


def test_json_only_never_reports_a_pdf_pass():
    v = verify_candidate(fx.architecture())
    assert v.pdf_checked is False
    assert verify_candidate(fx.architecture(), {}).pdf_checked is False


def test_a_printed_code_nobody_claims_is_found_in_the_pdf_and_placed_by_its_box():
    payload = fx.innovation()
    payload["audit"]["unclaimed_course_candidates"] = []
    payload["audit"]["errors"] = []
    text = "ENTRE 14 Business Implementation 1 5 ENTRE 10 ZZ-999 Ghost 3"
    chars = [(ch, 71.2 + 4 * i, 936.0 - 830.0, 75.2 + 4 * i, 936.0 - 822.0) for i, ch in enumerate("ZZ-999")]  # y up
    v = verify_candidate(payload, {1: PdfPage(text, chars, 936.0)})
    items = [r for s in v.sections for r in s.rows if r.item]
    assert [(r.item["source"], r.item["code"]) for r in items] == [("pdf", "ZZ-999")]
    assert items[0].item["bbox"] == pytest.approx([71.2, 822.0, 95.2, 830.0])
    assert items[0].rid.startswith("S1-U")  # no empty 1st-year section here: S1 is 4th Year 1st Semester


def test_a_pdf_code_in_the_y_flipped_position_is_not_placed_in_the_section():
    # Same glyph boxes as above but mirrored to the page top (y up from the bottom: 822..830 is near
    # the top). Read in the wrong frame it would land in S1; the right frame leaves it unplaced.
    payload = fx.innovation()
    payload["audit"]["unclaimed_course_candidates"] = []
    payload["audit"]["errors"] = []
    text = "ENTRE 14 Business Implementation 1 5 ENTRE 10 ZZ-999 Ghost 3"
    chars = [(ch, 71.2 + 4 * i, 822.0, 75.2 + 4 * i, 830.0) for i, ch in enumerate("ZZ-999")]  # y up: near the top
    v = verify_candidate(payload, {1: PdfPage(text, chars, 936.0)})
    items = [(s.sid, r.item["bbox"]) for s in v.sections for r in s.rows if r.item]
    assert [sid for sid, _ in items] == ["SU"]
    assert items[0][1] == pytest.approx([71.2, 106.0, 95.2, 114.0])


def test_locate_in_page_refuses_a_code_that_occurs_twice():
    boxes = lambda s, x0: [(ch, x0 + 5 * i, 10.0, x0 + 5 * i + 4, 20.0) for i, ch in enumerate(s)]
    page = PdfPage("CS 1 .. CS 10", boxes("CS1", 0) + boxes("CS10", 100), 100.0)
    assert locate_in_page(page, "CS 1") is None            # "cs1" is also inside "cs10"
    assert locate_in_page(page, "CS 10") == pytest.approx([100, 80, 119, 90])
    assert locate_in_page(PdfPage("x"), "CS 1") is None


def test_proposals_that_need_the_pdf_appear_only_with_it_and_only_on_flagged_rows():
    payload = fx.architecture()
    v = verify_candidate(payload, {1: PdfPage(fx.ARCH_PAGE_TEXT)})
    rows = by_code(payload, v)
    assert [(l, f.kind, f.new) for l, f in rows["GE-PC"].fixes] == [("a", "title_from_pdf", "Purposive Communication")]
    assert [(l, f.new) for l, f in rows["TOA-1/L"].fixes] == [("a", "Theory of Architecture1")]
    assert [f.new for _l, f in rows["VT-2/L"].fixes] == ["Architectural Visual Communications 4-Visual Techniques 2"]
    assert [f.new for _l, f in rows["TOA-2"].fixes] == ["Theory of Architecture 2"]
    assert rows["AD-1/L"].fixes == [] and rows["VT-1/L"].fixes == [] and rows["AD-2/L"].fixes == []
    assert not any(r.fixes for s in verify_candidate(payload).sections for r in s.rows)   # without the PDF: none


def test_health_is_broken_when_printed_codes_outnumber_a_quarter_of_the_courses():
    assert verify_candidate(fx.innovation()).health == "broken"      # 3 unclaimed codes, 2 courses
    payload = fx.bscs()
    payload["audit"]["unclaimed_course_candidates"] = [
        {"code": f"ZZ {n}", "cell_ids": [f"t0-c9{n}"], "table_index": 0, "page": 1, "bbox": None} for n in range(1, 4)]
    assert verify_candidate(payload).health == "broken"              # 3 of 4 courses
    payload["courses"] = [copy.deepcopy(c) for c in payload["courses"] for _ in range(4)]
    payload["audit"]["term_unit_audit"] = []                          # no printed totals to disagree with
    for index, course in enumerate(payload["courses"]):              # sixteen courses: three codes are under a quarter
        course["provenance"]["source_cell_ids"] = [f"t{index}-c1"]
        course["course_code"] = f"CS {index}"
    assert verify_candidate(payload).health == "mixed"
