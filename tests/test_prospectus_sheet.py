import re

import pytest

from backend.bintanong_tools.prospectus_extractor.course_checks import PdfPage
from backend.bintanong_tools.prospectus_extractor.sheet import (
    candidate_sha256, check_against, esc, parse_sheet, render_sheet, split_cells,
)
from backend.bintanong_tools.prospectus_extractor.verify import verify_candidate

import fixer_fixtures as fx
from sheet_helpers import edit_row, set_line

HASH = "a" * 64


def make(payload, pdf=False):
    v = verify_candidate(payload, {1: PdfPage(fx.ARCH_PAGE_TEXT)} if pdf else None)
    identity = {"pdf_sha256": HASH, "candidate_sha256": candidate_sha256(payload)}
    return v, render_sheet(payload, v, identity)


# --- escaping and layout

@pytest.mark.parametrize("value", ["plain", "a | b", "back\\slash", "ends with \\", "x\\|y", "two  spaces\nand a break"])
def test_a_cell_survives_escape_and_split(value):
    line = "| " + " | ".join([esc("id"), esc(value), esc("tail")]) + " |"
    assert split_cells(line) == ["id", " ".join(value.split()), "tail"]


def test_the_sheet_has_one_table_per_section_in_printed_order_and_a_health_line_each():
    payload = fx.architecture()
    v, text = make(payload, pdf=True)
    headings = re.findall(r"^## (S\w+) - (.*)$", text, re.M)
    assert headings[:2] == [("S1", "1st Year - 1st Semester"), ("S2", "1st Year - 2nd Semester")]
    assert re.findall(r"^health: (\w+)$", text, re.M)[:2] == ["review", "review"]
    assert text.count("| id | code | title | units | prereq | flags | proposal | decision | new code | new title | new term |") == len(v.sections)
    assert "units: printed 10, extracted 10" in text and "confirm: no" in text
    assert "- prospectus health:" in text and f"- pdf_sha256: {HASH}" in text and "- pdf_text_checked: yes" in text
    row = next(l for l in text.splitlines() if l.startswith("| S1-04 |"))
    assert "WARN title_not_in_pdf" in row and 'a) title_from_pdf course_title: "Techniques 1 Purposive Communication" -> "Purposive Communication"' in row


def test_a_sheet_made_without_the_pdf_says_the_text_was_not_checked():
    _v, text = make(fx.architecture())
    assert "- pdf_text_checked: no" in text and "the PDF text was NOT checked" in text


def test_a_pipe_in_a_title_does_not_break_the_row():
    payload = fx.bscs()
    payload["courses"][1]["course_title"] = "Intro | Computing \\ Basics"
    v, text = make(payload)
    parsed = parse_sheet(text)
    assert parsed.sections["S1"].rows["S1-02"]["title"] == "Intro | Computing \\ Basics"
    assert check_against(parsed, parse_sheet(text)) == []


# --- the editable parts and the fixed parts


def test_editing_the_decision_columns_is_allowed_and_editing_anything_else_is_refused():
    payload = fx.bscs()
    _v, text = make(payload)
    expected = parse_sheet(text)
    edited = edit_row(text, "S1-01", decision="ok")
    edited = set_line(edited, "S1", "confirm", "yes")
    assert check_against(parse_sheet(edited), expected) == []
    tampered = text.replace("Discrete Structures 1 |", "Discrete Structures 99 |", 1)
    problems = check_against(parse_sheet(tampered), expected)
    assert len(problems) == 1 and "S1-01: column 'title' was changed" in problems[0] and "new title" in problems[0]
    assert any("units line" in p or "units" in p for p in check_against(parse_sheet(text.replace("printed 6", "printed 7", 1)), expected))


def test_a_sheet_from_another_candidate_or_a_cut_up_sheet_is_refused():
    payload = fx.bscs()
    v, text = make(payload)
    other = fx.bscs()
    other["courses"][0]["course_title"] = "Changed"
    _v2, other_text = make(other)
    problems = check_against(parse_sheet(other_text), parse_sheet(text))
    assert any("candidate_sha256" in p and "regenerate" in p for p in problems)
    cut = "\n".join(l for l in text.splitlines() if not l.startswith("| S1-02 |"))
    assert "S1-02: row is missing" in check_against(parse_sheet(cut), parse_sheet(text))
    assert any("not a prospectus-review-sheet-v1" in e for e in parse_sheet("hello").errors)


# --- properties the owner relies on when editing in VS Code on any platform

NASTY = ["a | b", "back\\slash", "ends with \\", "x\\|y", "\\\\", "||", "| leading and trailing |", "C:\\temp\\new | \\n"]


def line_of(text, prefix):
    return next(n for n, l in enumerate(text.splitlines(), 1) if l.startswith(prefix))


def nasty_payload():
    payload = fx.bscs()
    payload["courses"][0]["course_code"] = NASTY[0]
    payload["courses"][0]["course_title"] = NASTY[1]
    payload["courses"][1]["course_title"] = NASTY[2]
    payload["courses"][2]["course_title"] = NASTY[3]
    payload["courses"][2]["prerequisites_raw"] = NASTY[4]
    payload["courses"][3]["course_title"] = NASTY[7]
    return payload


def test_values_with_pipes_and_backslashes_round_trip_through_render_and_an_edit_free_parse():
    payload = nasty_payload()
    _v, text = make(payload)
    parsed = parse_sheet(text)
    assert parsed.errors == []
    rows = {**parsed.sections["S1"].rows, **parsed.sections["S2"].rows}
    for index, rid in enumerate(["S1-01", "S1-02", "S2-01", "S2-02"]):
        course = payload["courses"][[0, 1, 2, 3][index]]
        assert rows[rid]["code"] == course["course_code"]
        assert rows[rid]["title"] == course["course_title"]
        assert rows[rid]["prereq"] == (course["prerequisites_raw"] or "")
    assert check_against(parsed, parse_sheet(text)) == []
    # a fresh render of the same candidate is what apply compares against: identical
    _v2, again = make(payload)
    assert again == text and parse_sheet(again) == parsed


def test_text_typed_into_an_editable_cell_with_pipes_and_backslashes_comes_back_unchanged():
    payload = fx.bscs()
    _v, text = make(payload)
    typed = "edit: see C:\\scans\\p1 | p2"
    edited = edit_row(text, "S1-02", decision=typed, new_title="Intro \\ Computing | I")
    parsed = parse_sheet(edited)
    row = parsed.sections["S1"].rows["S1-02"]
    assert (row["decision"], row["new title"]) == (typed, "Intro \\ Computing | I")
    assert check_against(parsed, parse_sheet(text)) == []


@pytest.mark.parametrize("name,transform", [
    ("crlf", lambda t: t.replace("\n", "\r\n")),
    ("bom", lambda t: "\ufeff" + t),
    ("bom and crlf", lambda t: "\ufeff" + t.replace("\n", "\r\n")),
    ("trailing spaces and tabs", lambda t: "".join(l + "  \t \n" for l in t.splitlines())),
    ("realigned table cells", lambda t: "\n".join(
        l.replace(" | ", "   |   ") if l.startswith("|") and "---" not in l else l for l in t.splitlines()) + "\n"),
    ("spaced separator row", lambda t: t.replace("|---|---|", "| --- | --- |")),
    ("no final newline", lambda t: t.rstrip("\n")),
])
def test_an_editor_that_rewrites_line_endings_bom_or_spacing_still_parses_identically(name, transform):
    payload = nasty_payload()
    _v, text = make(payload)
    expected = parse_sheet(text)
    parsed = parse_sheet(transform(text))
    assert parsed.errors == [], name
    assert parsed == expected, name
    assert check_against(parsed, expected) == [], name


def test_a_decision_typed_with_crlf_and_trailing_spaces_is_read_like_the_plain_one():
    payload = fx.bscs()
    _v, text = make(payload)
    edited = set_line(edit_row(text, "S1-02", decision="ok: fine"), "S1", "confirm", "yes")
    mangled = "\ufeff" + "".join(l + "   \r\n" for l in edited.splitlines())
    assert parse_sheet(mangled) == parse_sheet(edited)


# --- a malformed edit is refused and the message names the line

def test_a_row_with_the_wrong_number_of_columns_is_refused_naming_the_line():
    payload = fx.bscs()
    _v, text = make(payload)
    n = line_of(text, "| S1-02 |")
    lines = text.splitlines()
    for label, bad in [("too many", lines[n - 1] + " extra |"), ("lost a trailing cell", lines[n - 1].rsplit(" | ", 1)[0] + " |"),
                       ("lost all editable cells", " | ".join(lines[n - 1].split(" | ")[:7]) + " |")]:
        broken = lines[:]
        broken[n - 1] = bad
        problems = check_against(parse_sheet("\n".join(broken) + "\n"), parse_sheet(text))
        assert any(f"line {n}" in p and "columns" in p for p in problems), (label, problems)


def test_a_read_only_column_edit_is_refused_naming_the_line_and_the_row():
    payload = fx.bscs()
    _v, text = make(payload)
    n = line_of(text, "| S1-02 |")
    tampered = text.replace("Introduction to Computing", "Intro to Computing", 1)
    problems = check_against(parse_sheet(tampered), parse_sheet(text))
    assert len(problems) == 1 and "S1-02: column 'title' was changed" in problems[0] and f"line {n}" in problems[0]
    changed = text.replace("\nhealth: clean", "\nhealth: broken", 1)
    problems = check_against(parse_sheet(changed), parse_sheet(text))
    assert len(problems) == 1 and f"line {line_of(text, 'health: clean')}" in problems[0]


def test_a_row_moved_to_another_section_is_refused_naming_the_line_and_both_sections():
    payload = fx.bscs()
    _v, text = make(payload)
    lines = text.splitlines()
    moved = lines.pop(line_of(text, "| S1-02 |") - 1)
    after = next(i for i, l in enumerate(lines) if l.startswith("| S2-01 |"))
    lines.insert(after + 1, moved)
    shifted = "\n".join(lines) + "\n"
    n = line_of(shifted, "| S1-02 |")
    problems = check_against(parse_sheet(shifted), parse_sheet(text))
    assert len(problems) == 1, problems
    assert "S1-02" in problems[0] and "S2" in problems[0] and "S1" in problems[0] and f"line {n}" in problems[0]


def test_a_duplicated_row_or_section_is_refused_naming_the_line():
    payload = fx.bscs()
    _v, text = make(payload)
    lines = text.splitlines()
    n = line_of(text, "| S1-02 |")
    twice = "\n".join(lines[:n] + [lines[n - 1]] + lines[n:]) + "\n"
    problems = check_against(parse_sheet(twice), parse_sheet(text))
    assert any(f"line {n + 1}" in p and "S1-02" in p and "twice" in p for p in problems), problems
    h = line_of(text, "## S2 ")
    both = "\n".join(lines + [lines[h - 1]]) + "\n"
    problems = check_against(parse_sheet(both), parse_sheet(text))
    assert any("S2" in p and "twice" in p and f"line {len(lines) + 1}" in p for p in problems), problems


def test_a_table_row_outside_any_section_is_refused_naming_the_line():
    payload = fx.bscs()
    _v, text = make(payload)
    stray = "| S9-01 | X | Y | 1 | | | | ok | | | |\n" + text
    problems = check_against(parse_sheet(stray), parse_sheet(text))
    assert any("line 1" in p for p in problems), problems
