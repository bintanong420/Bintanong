import pytest

from backend.bintanong_tools.prospectus_extractor.fixes import (
    format_term, parse_term, propose_fixes, strip_banner, title_from_pdf,
)
from backend.bintanong_tools.prospectus_extractor.verify import own_role_cells, verify_candidate

import fixer_fixtures as fx
from fixer_fixtures import by_code


@pytest.mark.parametrize("text,expected", [
    ("FIRST SEMESTER Discrete Structures 1", "Discrete Structures 1"),
    ("FIRST YEAR FIRST SEMESTER SECOND SEMESTER Discrete Structures", "Discrete Structures"),
    ("FIRST Ethics", "Ethics"),
    ("Practicum FOURTH YEAR", "Practicum"),
    ("EE FIRST SEMESTER Environmental Engineering", None),   # banner in the middle: no guess
    ("SECOND SEMESTER", None),                               # nothing left
    ("Discrete Structures", None),                           # nothing to strip
    ("First Aid", None),
])
def test_strip_banner(text, expected):
    assert strip_banner(text) == expected


def test_term_text_round_trip():
    assert format_term("2nd Year", "1st Semester") == "2nd Year / 1st Semester"
    assert parse_term("2nd Year / 1st Semester") == ("2nd Year", "1st Semester")
    assert parse_term("FIRST SEMESTER", default_year="3rd Year") == ("3rd Year", "1st Semester")
    assert parse_term("FIRST SEMESTER SECOND SEMESTER", default_year="3rd Year") is None
    assert parse_term("1st Semester") is None


def roles(course, payload):
    audit = payload["audit"]
    ids = {i for s in audit["curriculum_sections"] for i in s["evidence_cells"]}
    return own_role_cells(course, audit["table_layout"], ids)


def test_a_leading_banner_in_the_title_gets_a_strip_proposal_keyed_to_its_cell():
    payload = fx.bscs()
    course = payload["courses"][0]
    course["course_title"] = "FIRST SEMESTER Discrete Structures 1"
    fixes = propose_fixes(course, roles(course, payload), banners={"FIRST", "SEMESTER"})
    assert [(f.kind, f.field, f.old, f.new, f.fix_id) for f in fixes] == [
        ("strip_banner", "course_title", "FIRST SEMESTER Discrete Structures 1", "Discrete Structures 1",
         "strip_banner:course_title@t0-c9")]


def test_a_leading_banner_in_the_code_gets_a_strip_proposal():
    payload = fx.bscs()
    course = payload["courses"][0]
    course["course_code"] = "FIRST SEMESTER CS 1"
    fixes = propose_fixes(course, roles(course, payload), banners={"FIRST", "SEMESTER"})
    assert [(f.field, f.new) for f in fixes] == [("course_code", "CS 1")]


def test_a_banner_that_names_another_semester_proposes_a_move_but_one_that_names_both_does_not():
    payload = fx.bscs()
    course = payload["courses"][0]   # CS 1 sits in 1st Year / 1st Semester; its title cell is t0-c9
    cells = roles(course, payload)
    cells["title"][0] = {**cells["title"][0], "text": "SECOND SEMESTER Discrete Structures 1 1"}
    fixes = propose_fixes(course, cells)
    assert [(f.kind, f.field, f.old, f.new) for f in fixes] == [("move_term", "term", "1st Year / 1st Semester", "1st Year / 2nd Semester")]
    cells["title"][0] = {**cells["title"][0], "text": "FIRST SEMESTER SECOND SEMESTER Discrete Structures 1 1"}
    assert propose_fixes(course, cells) == []
    cells["title"][0] = {**cells["title"][0], "text": "FIRST YEAR SECOND SEMESTER Discrete Structures 1 1"}
    assert propose_fixes(course, cells)[0].new == "1st Year / 2nd Semester"


def test_the_real_bscs_banner_cell_agrees_with_the_course_so_no_move_is_proposed():
    payload = fx.bscs()
    assert all(propose_fixes(c, roles(c, payload)) == [] for c in payload["courses"])


def test_a_trailing_banner_names_the_next_section_and_never_moves_the_course():
    payload = fx.bscs()
    course = payload["courses"][0]
    cells = roles(course, payload)
    cells["title"][0] = {**cells["title"][0], "text": "Discrete Structures 1 SECOND SEMESTER"}
    assert propose_fixes(course, cells) == []


CODES = ["AD-1/L", "TOA-1/L", "VT-1/L", "VT-2/L", "GR-2/L", "GE-PC", "TOA-2", "AD-2/L"]


@pytest.mark.parametrize("code,units,current,expected", [
    ("TOA-1/L", "2/1", "1 Theory of Architecture1", "Theory of Architecture1"),
    ("GE-PC", "3", "Techniques 1 Purposive Communication", "Purposive Communication"),
    ("VT-1/L", "1/1", "Architectural Visual Communications 2-Visual", "Architectural Visual Communications 2-Visual Techniques 1"),
    ("AD-1/L", "1/1", "Architectural Design 1-Introduction to Design", None),   # already the printed title
])
def test_title_from_pdf_reads_the_one_matching_row(code, units, current, expected):
    assert title_from_pdf(code, units, current, fx.ARCH_PAGE_TEXT, CODES) == expected


def test_title_from_pdf_refuses_when_the_row_is_ambiguous_or_absent():
    page = "HOA-3 History of Architecture 3 3 HOA-2 BU-3/L Building Utilities 3 2/1"
    assert title_from_pdf("HOA-3", "3", "x", page, ["HOA-3", "BU-3/L"]) is None      # the units digit repeats in the title
    assert title_from_pdf("NOPE 1", "3", "x", page, ["HOA-3"]) is None               # code not printed
    twice = "CS 1 Alpha Beta 3 CS 2 Gamma 3 CS 1 Delta Epsilon 3"
    assert title_from_pdf("CS 1", "3", "x", twice, ["CS 1", "CS 2"]) is None         # two rows start with the code
    mention = "CS 2 Gamma 3 CS 1, CS 9 Other 3"
    assert title_from_pdf("CS 1", "3", "x", mention, ["CS 1", "CS 2", "CS 9"]) is None  # a prerequisite mention is not a row


def test_the_verifier_numbers_the_proposals_of_each_row():
    payload = fx.bscs()
    payload["courses"][0]["course_title"] = "FIRST SEMESTER Discrete Structures 1"
    payload["courses"][1]["course_code"] = "FIRST YEAR CC 1/L"
    v = verify_candidate(payload)
    rows = by_code(payload, v)
    assert [(l, f.kind, f.new) for l, f in rows["CS 1"].fixes] == [("a", "strip_banner", "Discrete Structures 1")]
    assert [(l, f.field, f.new) for l, f in rows["FIRST YEAR CC 1/L"].fixes] == [("a", "course_code", "CC 1/L")]
    assert rows["CS 2"].fixes == []
