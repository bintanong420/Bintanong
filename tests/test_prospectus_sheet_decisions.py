from datetime import datetime, timezone

import pytest

from backend.bintanong_tools.prospectus_extractor.course_checks import PdfPage
from backend.bintanong_tools.prospectus_extractor.sheet import (
    build_entries, candidate_sha256, parse_decision, parse_sheet, render_sheet,
)
from backend.bintanong_tools.prospectus_extractor.verify import verify_candidate

import fixer_fixtures as fx
from sheet_helpers import edit_row, set_line

HASH = "a" * 64
NOW = datetime(2026, 10, 4, 9, 30, tzinfo=timezone.utc)


def make(payload, pdf=False):
    v = verify_candidate(payload, {1: PdfPage(fx.ARCH_PAGE_TEXT)} if pdf else None)
    identity = {"pdf_sha256": HASH, "candidate_sha256": candidate_sha256(payload)}
    return v, render_sheet(payload, v, identity)


def entries_for(payload, text, v=None, pdf=False):
    v = v or verify_candidate(payload, {1: PdfPage(fx.ARCH_PAGE_TEXT)} if pdf else None)
    parsed = parse_sheet(text)
    assert parsed.errors == []
    return build_entries(parsed, payload, v, reviewer="Nestor", pdf_sha256=HASH, now=NOW)


# --- the decision cell

@pytest.mark.parametrize("cell,expected", [
    ("", (None, [], "", None)),
    ("ok", ("ok", [], "", None)),
    ("OK: looks right", ("ok", [], "looks right", None)),
    ("fix", ("fix", [], "", None)),
    ("fix a, c", ("fix", ["a", "c"], "", None)),
    ("fix a b: both fine", ("fix", ["a", "b"], "both fine", None)),
    ("edit: PDF shows X", ("edit", [], "PDF shows X", None)),
    ("unresolved: cannot read", ("unresolved", [], "cannot read", None)),
])
def test_parse_decision(cell, expected):
    assert parse_decision(cell) == expected


def test_parse_decision_rejects_nonsense():
    assert parse_decision("approve")[3] and parse_decision("ok a")[3] and parse_decision("fix ab")[3]


# --- decisions to ledger entries


def test_an_untouched_sheet_writes_nothing():
    payload = fx.architecture()
    _v, text = make(payload, pdf=True)
    assert entries_for(payload, text, pdf=True) == ([], [])


def test_ok_writes_one_row_entry_with_the_row_as_extracted():
    payload = fx.bscs()
    _v, text = make(payload)
    entries, errors = entries_for(payload, edit_row(text, "S1-02", decision="ok"))
    assert errors == [] and len(entries) == 1
    e = entries[0]
    assert (e["field"], e["disposition"], e["reviewer"], e["pdf_sha256"], e["via"]) == ("row", "accepted", "Nestor", HASH, "sheet")
    assert e["old_value"] == e["new_value"] == {"course_code": "CC 1/L", "course_title": "Introduction to Computing", "term": "1st Year / 1st Semester"}
    assert e["locator"]["cell_ids"] == ["t0-c17", "t0-c18", "t0-c19", "t0-c8", "t0-c9"]


def test_fix_accepts_all_proposals_and_fix_a_names_one():
    payload = fx.architecture()
    _v, text = make(payload, pdf=True)
    entries, errors = entries_for(payload, edit_row(text, "S1-04", decision="fix"), pdf=True)
    assert errors == []
    assert [(e["field"], e["disposition"]) for e in entries] == [("row", "accepted"), ("course_title", "corrected")]
    fix = entries[1]
    assert (fix["old_value"], fix["new_value"], fix["fix_id"]) == (
        "Techniques 1 Purposive Communication", "Purposive Communication", "title_from_pdf:course_title@t0-c35")
    assert fix["reason"] == "accepted proposal title_from_pdf"
    one, errors = entries_for(payload, edit_row(text, "S1-04", decision="fix a: checked against the PDF"), pdf=True)
    assert errors == [] and one[1]["reason"] == "checked against the PDF"
    _none, errors = entries_for(payload, edit_row(text, "S1-04", decision="fix b"), pdf=True)
    assert "no proposal b on this row" in errors[0]
    _none, errors = entries_for(payload, edit_row(text, "S1-01", decision="fix"), pdf=True)
    assert "this row has no proposals" in errors[0]


def test_rejecting_a_proposal_with_ok_is_recorded_as_accepted_as_extracted():
    payload = fx.architecture()
    _v, text = make(payload, pdf=True)
    entries, errors = entries_for(payload, edit_row(text, "S1-04", decision="ok: the printed title is wrapped"), pdf=True)
    assert errors == [] and [(e["field"], e["disposition"]) for e in entries] == [("row", "accepted")]


def test_edit_needs_a_value_and_a_reason_and_a_readable_term():
    payload = fx.bscs()
    _v, text = make(payload)
    entries, errors = entries_for(payload, edit_row(text, "S1-02", decision="edit: PDF page 1 shows this", new_title="Intro to Computing", new_term="2nd Year / 1st Semester"))
    assert errors == []
    assert [(e["field"], e["old_value"], e["new_value"], e["fix_id"]) for e in entries[1:]] == [
        ("course_title", "Introduction to Computing", "Intro to Computing", None),
        ("term", "1st Year / 1st Semester", "2nd Year / 1st Semester", None)]
    for cols, message in [
        (dict(decision="edit: why"), "fill at least one"),
        (dict(decision="edit", new_title="X"), "needs a reason"),
        (dict(decision="edit: why", new_term="never"), "is not a year and one semester"),
        (dict(decision="edit: why", new_title="Introduction to Computing"), "equals the current one"),
        (dict(new_title="X"), "needs a decision"),
        (dict(decision="ok", new_title="X"), "cannot carry new values"),
    ]:
        _e, errors = entries_for(payload, edit_row(text, "S1-02", **cols))
        assert message in errors[0], (cols, errors)


def test_unresolved_needs_a_reason_and_writes_no_correction():
    payload = fx.bscs()
    _v, text = make(payload)
    _e, errors = entries_for(payload, edit_row(text, "S1-02", decision="unresolved"))
    assert "needs a reason" in errors[0]
    entries, errors = entries_for(payload, edit_row(text, "S1-02", decision="unresolved: PDF unreadable here"))
    assert errors == [] and [(e["field"], e["disposition"], e["new_value"]) for e in entries] == [("row", "unresolved", None)]


def test_confirming_a_clean_section_accepts_every_row_but_not_other_sections():
    payload = fx.bscs()
    _v, text = make(payload)
    entries, errors = entries_for(payload, set_line(text, "S1", "confirm", "yes"))
    assert errors == []
    assert [(e["locator"]["code_at_review"], e["via"], e["reason"]) for e in entries] == [
        ("CS 1", "section_confirm", "section confirmed as extracted"), ("CC 1/L", "section_confirm", "section confirmed as extracted")]
    both = set_line(set_line(text, "S1", "confirm", "yes"), "S1", "reason", "checked against page 1")
    assert {e["reason"] for e in entries_for(payload, both)[0]} == {"checked against page 1"}


def test_confirming_a_section_with_an_undecided_flagged_row_is_refused_and_writes_nothing():
    payload = fx.architecture()
    _v, text = make(payload, pdf=True)
    entries, errors = entries_for(payload, set_line(text, "S1", "confirm", "yes"), pdf=True)
    assert entries == []
    assert sorted(e.split(":")[0] for e in errors) == ["S1-02", "S1-04"] and "flagged but undecided" in errors[0]


def test_info_flags_do_not_block_a_confirm():
    payload = fx.bscs()   # CS 1 carries an info flag (banner text in its own cell)
    _v, text = make(payload)
    assert "INFO banner_in_cell" in text
    assert entries_for(payload, set_line(text, "S1", "confirm", "yes"))[1] == []


def test_accepting_a_class_applies_that_proposal_to_every_undecided_row_of_the_section():
    payload = fx.architecture()
    _v, text = make(payload, pdf=True)
    text = set_line(set_line(text, "S1", "accept", "title_from_pdf"), "S1", "reason", "titles checked against PDF page 1")
    entries, errors = entries_for(payload, edit_row(text, "S1-04", decision="ok: keep as printed"), pdf=True)
    assert errors == []
    assert [(e["locator"]["code_at_review"], e["field"], e["via"]) for e in entries] == [
        ("TOA-1/L", "row", "section_accept"), ("TOA-1/L", "course_title", "section_accept"), ("GE-PC", "row", "sheet")]
    _e, errors = entries_for(payload, set_line(text, "S1", "reason", ""), pdf=True)
    assert "accept needs a reason" in errors[0]
    _e, errors = entries_for(payload, set_line(text, "S1", "accept", "everything"), pdf=True)
    assert "unknown class 'everything'" in errors[0]


def test_printed_codes_can_only_be_ok_or_unresolved_and_both_need_a_reason():
    payload = fx.innovation()
    _v, text = make(payload)
    assert "SU-U1" in text
    _e, errors = entries_for(payload, edit_row(text, "SU-U1", decision="ok"))
    assert "needs a reason" in errors[0]
    _e, errors = entries_for(payload, edit_row(text, "SU-U1", decision="fix"))
    assert "can only be `ok` or `unresolved`" in errors[0]
    entries, errors = entries_for(payload, edit_row(text, "SU-U1", decision="unresolved: row above the first banner is missing"))
    assert errors == [] and (entries[0]["field"], entries[0]["disposition"], entries[0]["locator"]["kind"]) == ("unclaimed", "unresolved", "unclaimed")
    all_ok = set_line(set_line(text, "SU", "accept", "unclaimed"), "SU", "reason", "these are listed prerequisites, not courses")
    entries, errors = entries_for(payload, all_ok)
    assert errors == [] and [e["disposition"] for e in entries] == ["accepted"] * 3


# --- properties the owner relies on: nothing written by accident, nothing written twice, errors name a line

from backend.bintanong_tools.prospectus_extractor.ledger import append_entries, read_entries


def line_of(text, prefix):
    return next(n for n, l in enumerate(text.splitlines(), 1) if l.startswith(prefix))


@pytest.mark.parametrize("which", ["bscs", "architecture"])
def test_an_unchanged_sheet_with_no_confirmations_writes_zero_ledger_entries_even_after_an_editor_resaved_it(which, tmp_path):
    payload = getattr(fx, which)()
    pdf = which == "architecture"
    _v, text = make(payload, pdf=pdf)
    resaved = "\ufeff" + "".join(l + "  \r\n" for l in text.splitlines())
    for sheet_text in (text, resaved):
        entries, errors = entries_for(payload, sheet_text, pdf=pdf)
        assert (entries, errors) == ([], [])
    ledger = tmp_path / "decision_ledger.jsonl"
    assert append_entries(ledger, entries) == (0, 0) and not ledger.exists()


def test_confirming_one_section_writes_exactly_one_entry_per_course_of_that_section_and_none_for_others():
    payload = fx.bscs()
    v, text = make(payload)
    per_section = {s.sid: [r for r in s.rows if r.course is not None] for s in v.sections}
    assert set(per_section) == {"S1", "S2"} and all(len(rows) == 2 for rows in per_section.values())
    for sid, other in (("S1", "S2"), ("S2", "S1")):
        entries, errors = entries_for(payload, set_line(text, sid, "confirm", "yes"))
        assert errors == [] and len(entries) == len(per_section[sid])
        wanted = {payload["courses"][r.course]["course_code"] for r in per_section[sid]}
        not_wanted = {payload["courses"][r.course]["course_code"] for r in per_section[other]}
        got = [e["locator"]["code_at_review"] for e in entries]
        assert sorted(got) == sorted(wanted) and not set(got) & not_wanted
        assert {(e["field"], e["disposition"], e["via"], e["section"]) for e in entries} == {
            ("row", "accepted", "section_confirm", next(s.title for s in v.sections if s.sid == sid))}
    both, errors = entries_for(payload, set_line(set_line(text, "S1", "confirm", "yes"), "S2", "confirm", "yes"))
    assert errors == [] and len(both) == 4


def test_a_clean_section_is_confirmed_by_editing_only_its_header_line_and_a_yes_in_any_case_or_spacing_works():
    payload = fx.bscs()
    _v, text = make(payload)
    edited = set_line(text, "S1", "confirm", "yes")
    changed = [n for n, (a, b) in enumerate(zip(text.splitlines(), edited.splitlines()), 1) if a != b]
    assert changed == [line_of(text, "confirm: no")]
    for spelling in ("YES", "Yes  ", "yes"):
        assert len(entries_for(payload, set_line(text, "S1", "confirm", spelling))[0]) == 2


def test_applying_the_same_edited_sheet_twice_writes_nothing_the_second_time(tmp_path):
    ledger = tmp_path / "review" / "decision_ledger.jsonl"
    payload = fx.architecture()
    _v, text = make(payload, pdf=True)
    sheet_text = edit_row(set_line(text, "S2", "confirm", "no"), "S1-04", decision="fix a: checked against the PDF")
    sheet_text = edit_row(sheet_text, "S1-02", decision="ok: fine as printed")
    sheet_text = edit_row(sheet_text, "S1-01", decision="edit: PDF shows 2nd year", new_term="2nd Year / 1st Semester")
    first, errors = entries_for(payload, sheet_text, pdf=True)
    assert errors == [] and len(first) >= 4
    assert append_entries(ledger, first) == (len(first), 0)
    before = ledger.read_bytes()
    later = datetime(2026, 10, 5, 8, 0, tzinfo=timezone.utc)
    again, errors = build_entries(parse_sheet(sheet_text), payload, verify_candidate(payload, {1: PdfPage(fx.ARCH_PAGE_TEXT)}),
                                  reviewer="Nestor", pdf_sha256=HASH, now=later)
    assert errors == [] and len(again) == len(first)
    assert append_entries(ledger, again) == (0, len(first))
    assert ledger.read_bytes() == before and len(read_entries(ledger)) == len(first)


def test_applying_a_section_confirmation_twice_writes_nothing_the_second_time_and_a_changed_decision_does(tmp_path):
    ledger = tmp_path / "decision_ledger.jsonl"
    payload = fx.bscs()
    _v, text = make(payload)
    confirmed = set_line(text, "S1", "confirm", "yes")
    assert append_entries(ledger, entries_for(payload, confirmed)[0]) == (2, 0)
    assert append_entries(ledger, entries_for(payload, confirmed)[0]) == (0, 2)
    changed = edit_row(confirmed, "S1-02", decision="unresolved: PDF unreadable here")
    assert append_entries(ledger, entries_for(payload, changed)[0]) == (1, 1)  # CS 1 is unchanged, only S1-02 is new
    assert append_entries(ledger, entries_for(payload, changed)[0]) == (0, 2)


@pytest.mark.parametrize("cell,expected", [
    ("approve", "unknown decision 'approve'"),
    ("accepted", "unknown decision 'accepted'"),
    ("ok a", "only `fix` takes proposal letters"),
    ("fix ab", "only `fix` takes proposal letters"),
    ("edit", "fill at least one"),
    ("unresolved", "needs a reason"),
])
def test_a_bad_decision_is_refused_naming_the_row_and_the_line(cell, expected):
    payload = fx.bscs()
    _v, text = make(payload)
    n = line_of(text, "| S1-02 |")
    entries, errors = entries_for(payload, edit_row(text, "S1-02", decision=cell))
    assert entries == [] and len(errors) == 1
    assert errors[0].startswith("S1-02:") and expected in errors[0] and f"line {n}" in errors[0], errors


def test_every_other_refusal_names_the_line_it_came_from():
    payload = fx.architecture()
    _v, text = make(payload, pdf=True)
    row = line_of(text, "| S1-04 |")
    none, errors = entries_for(payload, set_line(text, "S1", "confirm", "yes"), pdf=True)
    assert none == [] and errors and all("line " in e for e in errors)
    assert {f"line {line_of(text, '| S1-02 |')}", f"line {row}"} <= {m for e in errors for m in [e[e.rindex("line "):].rstrip(")")]}
    for edited, needle in [
        (set_line(text, "S1", "confirm", "maybe"), "confirm must be yes or no"),
        (set_line(text, "S1", "accept", "everything"), "unknown class"),
        (set_line(text, "S1", "accept", "title_from_pdf"), "accept needs a reason"),
    ]:
        _e, errs = entries_for(payload, edited, pdf=True)
        assert any(needle in e and "line " in e for e in errs), errs
    _e, errs = entries_for(payload, set_line(text, "S1", "confirm", "maybe"), pdf=True)
    assert f"line {line_of(text, 'confirm: no')}" in errs[0]
    _e, errs = entries_for(payload, edit_row(text, "S1-04", new_title="X"), pdf=True)
    assert f"line {row}" in errs[0] and "needs a decision" in errs[0]


def test_one_bad_row_means_no_entries_at_all():
    payload = fx.bscs()
    _v, text = make(payload)
    mixed = edit_row(edit_row(text, "S1-01", decision="ok"), "S1-02", decision="approve")
    entries, errors = entries_for(payload, mixed)
    assert entries == [] and len(errors) == 1
