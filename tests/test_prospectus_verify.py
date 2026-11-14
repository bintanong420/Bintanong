import copy

import pytest

from backend.bintanong_tools.prospectus_extractor.text import has_banner_text, leading_banner, trailing_banner
from backend.bintanong_tools.prospectus_extractor.verify import verify_candidate

import fixer_fixtures as fx
from fixer_fixtures import by_code, kinds, section



# --- banner text helpers (also used by the parser split in the last task)

@pytest.mark.parametrize("text,banner,rest", [
    ("FIRST YEAR FIRST SEMESTER SECOND SEMESTER Discrete Structures", "FIRST YEAR FIRST SEMESTER SECOND SEMESTER", "Discrete Structures"),
    ("FIRST SEMESTER Discrete Structures 1 1", "FIRST SEMESTER", "Discrete Structures 1 1"),
    ("FIRST Ethics", "FIRST", "Ethics"),
    ("SECOND SEMESTER", "SECOND SEMESTER", ""),
    ("Discrete Structures", "", "Discrete Structures"),
    ("First Aid", "", "First Aid"),            # title case is a real title
    ("Summer Internship", "", "Summer Internship"),
])
def test_leading_banner(text, banner, rest):
    assert leading_banner(text) == (banner, rest)


def test_trailing_banner_and_has_banner_text():
    assert trailing_banner("Practicum FOURTH YEAR FIRST SEMESTER") == ("Practicum", "FOURTH YEAR FIRST SEMESTER")
    assert trailing_banner("Practicum") == ("Practicum", "")
    assert has_banner_text("EE FIRST SEMESTER Environmental Engineering")
    assert has_banner_text("FIRST Ethics")
    assert not has_banner_text("First Aid") and not has_banner_text("Summer Internship") and not has_banner_text("3RD YEAR".lower())


# --- sections, ids, order, totals

def test_a_clean_candidate_has_clean_sections_in_printed_order():
    payload = fx.bscs()
    v = verify_candidate(payload)
    assert [(s.sid, s.year, s.semester, s.health) for s in v.sections] == [
        ("S1", "1st Year", "1st Semester", "clean"), ("S2", "1st Year", "2nd Semester", "clean")]
    assert [r.rid for r in section(v, "S1").rows] == ["S1-01", "S1-02"]
    assert (section(v, "S1").declared, section(v, "S1").computed) == (6, 6)
    assert v.health == "clean" and v.pdf_checked is False and v.counts() == {}


def test_banner_text_in_the_courses_own_cell_is_info_and_banner_cells_of_other_courses_are_ignored():
    payload = fx.bscs()
    rows = by_code(payload, verify_candidate(payload))
    assert kinds(rows["CS 1"]) == ["banner_in_cell"] and rows["CS 1"].flags[0].severity == "info"
    for code in ("CC 1/L", "CS 2", "CC 3/L"):  # t0-c9 rides along in their provenance as section context
        assert kinds(rows[code]) == [], code


def test_banner_text_still_in_a_field_is_an_error_and_breaks_the_section():
    payload = fx.bscs()
    payload["courses"][1]["course_title"] = "EE FIRST SEMESTER Introduction to Computing"
    v = verify_candidate(payload)
    row = by_code(payload, v)["CC 1/L"]
    assert kinds(row) == ["banner_leak"] and row.flags[0].severity == "error"
    assert row.fixes == []  # banner in the middle of a title: flag only, no guess where the title starts
    assert section(v, "S1").health == "broken" and v.health == "mixed"


def test_a_standing_rule_in_the_prerequisite_is_not_banner_text():
    payload = fx.bscs()
    payload["courses"][2]["prerequisites_raw"] = "3RD YEAR STANDING"
    assert kinds(by_code(payload, verify_candidate(payload))["CS 2"]) == []


def test_unit_total_mismatch_is_a_section_error_with_the_difference():
    payload = fx.architecture()
    payload["audit"]["term_unit_audit"][0]["declared_units"] = 11
    v = verify_candidate(payload)
    s1 = section(v, "S1")
    assert [f.kind for f in s1.flags] == ["unit_total"] and "printed total 11, extracted 10 (-1)" in s1.flags[0].message
    assert s1.health == "broken" and section(v, "S2").health == "clean"
    assert v.counts() == {"unit_total": 1}


def test_a_printed_total_for_a_term_with_no_courses_gets_an_empty_section():
    payload = fx.innovation()
    v = verify_candidate(payload)
    assert [(s.sid, s.year, s.semester, len(s.rows)) for s in v.sections if s.sid != "SU"] == [
        ("S1", "1st Year", "1st Semester", 0), ("S2", "4th Year", "1st Semester", 1), ("S3", "4th Year", "2nd Semester", 1)]
    assert section(v, "S1").flags[0].kind == "unit_total" and section(v, "S1").health == "broken"


def test_course_in_two_terms_or_none():
    payload = fx.bscs()
    twin = copy.deepcopy(payload["courses"][0])
    twin["year_level"], twin["semester"], twin["term_index"] = "2nd Year", "1st Semester", 21
    twin["provenance"]["source_cell_ids"] = ["t9-c1"]
    lost = copy.deepcopy(payload["courses"][1])
    lost["year_level"] = lost["semester"] = None
    lost["course_code"] = "ZZ 9"
    lost["provenance"]["source_cell_ids"] = ["t9-c2"]
    payload["courses"] += [twin, lost]
    v = verify_candidate(payload)
    rows = {payload["courses"][r.course]["provenance"]["source_cell_ids"][0]: r for s in v.sections for r in s.rows if r.course is not None}
    assert "duplicate_course" in kinds(rows["t0-c11"]) and "duplicate_course" in kinds(rows["t9-c1"])
    assert kinds(rows["t9-c2"]) == ["no_term"]
    assert [s.sid for s in v.sections][-1] == "SN" and section(v, "SN").title == "No year or semester"


def test_prerequisite_in_the_same_or_a_later_term_is_a_warning():
    payload = fx.bscs()
    payload["courses"][0]["prerequisites"] = ["CS 2"]       # CS 2 is in the next semester
    payload["courses"][2]["prerequisites"] = ["CC 3/L"]     # same semester
    v = verify_candidate(payload)
    rows = by_code(payload, v)
    assert "prereq_order" in kinds(rows["CS 1"]) and "prereq_order" in kinds(rows["CS 2"])
    assert section(v, "S1").health == "review" and v.health == "warnings_only"


# --- unclaimed printed codes and where they sit


def test_health_overall_vocabulary_without_unclaimed_codes():
    assert verify_candidate(fx.bscs()).health == "clean"
    payload = fx.architecture()
    payload["audit"]["term_unit_audit"][0]["declared_units"] = 11
    assert verify_candidate(payload).health == "mixed"
    one_section = fx.bscs()
    one_section["courses"] = one_section["courses"][:2]          # a single term section: not enough to call it sound
    assert verify_candidate(one_section).health == "broken"
