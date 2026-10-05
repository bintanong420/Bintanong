import copy

import pytest

from backend.bintanong_tools.prospectus_extractor.course_checks import PdfPage
from backend.bintanong_tools.prospectus_extractor.ledger import (
    correction_problem, course_locator, entry_problem, locator_key,
)
from backend.bintanong_tools.prospectus_extractor.verify import Flag, verify_candidate
from backend.bintanong_tools.prospectus_review_gui.answers import Answer, answer_to_entries, parse_typed_value
from backend.bintanong_tools.prospectus_review_gui.questions import build_questions

import fixer_fixtures as fx
import review_gui_fixtures as rf

HASH, NOW = rf.HASH, rf.NOW


def setup(payload=None, pages=None):
    payload = payload or rf.mixed()
    v = verify_candidate(payload, pages)
    return payload, v, {q.qid: q for q in build_questions(payload, v, [], HASH)}


def ask(env, qid, choice, *, via="gui", **kw):
    payload, v, questions = env
    return answer_to_entries(questions[qid], Answer(choice=choice, **kw), payload=payload, verification=v,
                             reviewer="Nestor", pdf_sha256=HASH, via=via, now=NOW)


def arch():
    return setup(fx.architecture(), {1: PdfPage(fx.ARCH_PAGE_TEXT)})


def test_yes_on_course_writes_accepted_row_entry_with_reviewer_hash_locator():
    env = setup()
    entries, errors = ask(env, "S1-02", "yes")
    assert errors == [] and len(entries) == 1
    e = entries[0]
    assert (e["field"], e["disposition"], e["reviewer"], e["pdf_sha256"], e["via"]) == ("row", "accepted", "Nestor", HASH, "gui")
    assert e["locator"] == course_locator(env[0]["courses"][1]) and e["locator"]["cell_ids"] == sorted(e["locator"]["cell_ids"])
    assert e["rejected_fixes"] == [] and e["reason"] == "accepted as extracted"
    assert ask(env, "S1-02", "yes", reason="checked on the PDF")[0][0]["reason"] == "checked on the PDF"


def test_yes_cannot_carry_values_or_proposals():
    env = setup()
    assert ask(env, "S1-02", "yes", edits={"course_title": "X"})[1]
    assert ask(env, "S1-02", "yes", proposals=["a"])[1]


def test_other_with_title_writes_row_accepted_plus_corrected_title():
    env = setup()
    entries, errors = ask(env, "S1-02", "other", edits={"course_title": "Intro to Computing"}, reason="PDF prints it shorter")
    assert errors == []
    assert [(e["field"], e["disposition"]) for e in entries] == [("row", "accepted"), ("course_title", "corrected")]
    corrected = entries[1]
    assert (corrected["old_value"], corrected["new_value"], corrected["reason"], corrected["fix_id"]) == \
        ("Introduction to Computing", "Intro to Computing", "PDF prints it shorter", None)


def test_other_requires_a_value_and_a_reason():
    env = setup()
    entries, errors = ask(env, "S1-02", "other", reason="no value typed")
    assert entries == [] and errors and "value" in errors[0]
    entries, errors = ask(env, "S1-02", "other", edits={"course_title": "Intro"})
    assert entries == [] and errors == ["a correction needs a reason"]


@pytest.mark.parametrize("field,typed", [
    ("course_title", "   "), ("course_code", ""), ("term", "someday"), ("lecture_units", "3.5"), ("lecture_units", "100"),
    ("lab_units", "abc"), ("total_units", "1e2"), ("lecture_units", ""),
])
def test_other_value_goes_through_correction_problem(field, typed):
    env = setup()
    entries, errors = ask(env, "S1-02", "other", edits={field: typed}, reason="r")
    assert entries == [] and len(errors) == 1
    assert errors == [correction_problem(field, typed.strip() if field in ("course_title", "course_code") else
                                         int(typed) if typed.isdigit() else typed.strip())]


def test_prerequisites_typed_as_a_number_is_refused_with_the_ledger_message():
    env = setup()
    entries, errors = ask(env, "S1-02", "other", edits={"prerequisites_raw": 5}, reason="r")
    assert entries == [] and errors == [correction_problem("prerequisites_raw", 5)]


def test_unknown_field_is_refused():
    env = setup()
    entries, errors = ask(env, "S1-02", "other", edits={"course_color": "red"}, reason="r")
    assert entries == [] and errors and "can be corrected" in errors[0]


def test_term_is_stored_as_format_term():
    env = setup()
    entries, errors = ask(env, "S1-02", "other", edits={"term": "2nd year first semester"}, reason="wrong term")
    assert errors == [] and entries[1]["field"] == "term"
    assert (entries[1]["old_value"], entries[1]["new_value"]) == ("1st Year / 1st Semester", "2nd Year / 1st Semester")


def test_term_without_a_year_takes_the_courses_year_like_the_sheet():
    env = setup()
    entries, errors = ask(env, "S1-02", "other", edits={"term": "2nd semester"}, reason="wrong term")
    assert errors == [] and entries[1]["new_value"] == "1st Year / 2nd Semester"


def test_units_text_becomes_int():
    env = setup()
    entries, errors = ask(env, "S1-02", "other", edits={"lab_units": " 3 "}, reason="PDF")
    assert errors == [] and entries[1]["new_value"] == 3 and type(entries[1]["new_value"]) is int and entries[1]["old_value"] == 1
    assert ask(env, "S1-02", "other", edits={"lab_units": "03"}, reason="PDF")[0][1]["new_value"] == 3
    assert ask(env, "S1-02", "other", edits={"lab_units": "+3"}, reason="PDF")[0] == []


def test_parse_typed_value():
    assert parse_typed_value("lecture_units", " 3 ") == (3, None)
    assert parse_typed_value("lecture_units", "03") == (3, None)
    assert parse_typed_value("total_units", "0") == (0, None)
    assert parse_typed_value("course_title", "  Ethics ") == ("Ethics", None)
    assert parse_typed_value("prerequisites_raw", "") == ("", None)
    assert parse_typed_value("prerequisites_raw", " CS 1 ") == ("CS 1", None)
    assert parse_typed_value("term", "2nd year first sem") == ("2nd Year / 1st Semester", None)
    assert parse_typed_value("term", "1st semester", "3rd Year") == ("3rd Year / 1st Semester", None)
    for field, bad in [("lecture_units", "+3"), ("lecture_units", "3.5"), ("lecture_units", "-1"), ("lecture_units", "٣"),
                       ("lecture_units", "100"), ("lecture_units", "9" * 5000), ("course_code", ""), ("term", "someday")]:
        value, message = parse_typed_value(field, bad)
        assert value is None and message, (field, bad[:10])
    assert parse_typed_value("prerequisites_raw", 5) == (None, correction_problem("prerequisites_raw", 5))   # the browser sends text
    assert parse_typed_value("lecture_units", 3)[0] is None and parse_typed_value("lecture_units", 3)[1]


def test_no_without_values_is_unresolved_and_needs_a_reason():
    env = setup()
    entries, errors = ask(env, "S1-02", "no", reason="cannot read the scan")
    assert errors == [] and len(entries) == 1
    assert (entries[0]["field"], entries[0]["disposition"], entries[0]["new_value"]) == ("row", "unresolved", None)
    entries, errors = ask(env, "S1-02", "no")
    assert entries == [] and errors and "reason" in errors[0]


def test_no_with_values_is_a_correction():
    env = setup()
    entries, errors = ask(env, "S1-02", "no", edits={"course_code": "CC 1/X"}, reason="code is misprinted")
    assert errors == [] and [(e["field"], e["disposition"]) for e in entries] == [("row", "accepted"), ("course_code", "corrected")]


def test_proposal_button_value_is_recorded_as_fix():
    env = arch()
    q = env[2]["S1-02"]
    proposal = q.proposals[0]
    entries, errors = ask(env, "S1-02", "other", edits={proposal["field"]: proposal["new"]})
    assert errors == []
    assert [e["field"] for e in entries] == ["row", proposal["field"]]
    assert entries[1]["fix_id"] == proposal["fix_id"] and entries[1]["reason"] == f"accepted proposal {proposal['kind']}"
    # an explicit proposal letter is the same decision
    assert ask(env, "S1-02", "other", proposals=["a"])[0] == entries
    # a differing value is a plain correction
    entries, errors = ask(env, "S1-02", "other", edits={proposal["field"]: proposal["new"] + " (typed)"}, reason="my own reading")
    assert errors == [] and entries[1]["fix_id"] is None and entries[1]["reason"] == "my own reading"


def test_unknown_proposal_letter_is_refused():
    env = arch()
    entries, errors = ask(env, "S1-02", "other", proposals=["z"])
    assert entries == [] and errors == ["no proposal z on this row"]


def test_unclaimed_yes_and_no_need_a_reason():
    env = setup()
    for choice, disposition in (("yes", "accepted"), ("no", "unresolved")):
        entries, errors = ask(env, "SU-U1", choice)
        assert entries == [] and errors and "reason" in errors[0]
        entries, errors = ask(env, "SU-U1", choice, reason="footnote marker")
        assert errors == [] and len(entries) == 1 and entries[0]["field"] == "unclaimed" and entries[0]["disposition"] == disposition
        assert entries[0]["via"] == "gui"


def test_unclaimed_other_is_refused_with_a_clear_message():
    env = setup()
    entries, errors = ask(env, "SU-U1", "other", edits={"course_code": "CS 9"}, reason="r")
    assert entries == [] and errors == ["a printed code can only be answered Yes or No; no course is added or corrected here"]


def test_section_confirm_refused_when_section_has_blocking_flag():
    env = setup()
    _payload, v, questions = env
    assert "S1:confirm" in questions
    v.sections[0].rows[1].flags.append(Flag("title_not_in_pdf", "warn", "a flag that appeared after the question was built"))
    entries, errors = ask(env, "S1:confirm", "yes")
    assert entries == [] and errors and "cannot cover a section flagged" in errors[0] and "title_not_in_pdf" in errors[0]


def test_section_confirm_writes_one_entry_per_course_with_gui_section_confirm():
    env = setup()
    entries, errors = ask(env, "S1:confirm", "yes")
    assert errors == [] and len(entries) == 2
    assert {e["via"] for e in entries} == {"gui_section_confirm"}
    assert [e["field"] for e in entries] == ["row", "row"] and {e["disposition"] for e in entries} == {"accepted"}
    assert {e["reason"] for e in entries} == {"section confirmed as extracted"}
    assert [locator_key(e["locator"]) for e in entries] == [locator_key(course_locator(c)) for c in env[0]["courses"][:2]]
    noted = ask(env, "S1:confirm", "yes", note="all read against the PDF")[0]
    assert {e["reason"] for e in noted} == {"all read against the PDF"}


def test_section_confirm_no_writes_nothing_and_other_is_refused():
    env = setup()
    assert ask(env, "S1:confirm", "no") == ([], [])
    entries, errors = ask(env, "S1:confirm", "other", edits={"course_title": "x"})
    assert entries == [] and errors == ["a section question can only be answered Yes or No"]


def test_unknown_choice_is_refused():
    env = setup()
    assert ask(env, "S1-02", "maybe") == ([], ["the answer must be yes, no or other, not 'maybe'"])


def test_every_entry_passes_ledger_entry_problem():
    env = arch()
    mixed_env = setup()
    cases = [(env, "S1-02", "yes", {}), (env, "S1-02", "other", {"proposals": ["a"]}),
             (env, "S1-04", "other", {"edits": {"course_title": "Typed"}, "reason": "r"}),
             (env, "S1-01", "no", {"reason": "unclear"}), (env, "SU-U1", "yes", {"reason": "r"}),
             (env, "SU-U2", "no", {"reason": "r"}), (mixed_env, "S1:confirm", "yes", {}),
             (mixed_env, "S1-02", "other", {"edits": {"lecture_units": "1", "lab_units": "2", "total_units": "4",
                                                      "prerequisites_raw": "CS 1", "term": "2nd semester"}, "reason": "r"})]
    seen = 0
    for e, qid, choice, kw in cases:
        entries, errors = ask(e, qid, choice, **kw)
        assert errors == [], (qid, errors)
        for entry in entries:
            assert entry_problem(entry) is None
            seen += 1
    assert seen >= 15


def test_answer_never_mutates_candidate():
    payload, v, questions = setup()
    before = copy.deepcopy(payload)
    ask((payload, v, questions), "S1-02", "other", edits={"course_title": "Z", "lecture_units": "1"}, reason="r")
    ask((payload, v, questions), "S1:confirm", "yes")
    assert payload == before


def test_unknown_question_is_refused():
    payload, v, questions = setup()
    q = copy.copy(questions["S1-02"])
    q.qid = "S9-99"
    entries, errors = answer_to_entries(q, Answer(choice="yes"), payload=payload, verification=v, reviewer="N", pdf_sha256=HASH)
    assert entries == [] and errors == ["unknown question S9-99"]
