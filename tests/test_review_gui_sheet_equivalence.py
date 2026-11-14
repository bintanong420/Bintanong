"""The GUI path and the sheet path must produce the same ledger entries, by construction and by this test."""

import json
from copy import deepcopy
from datetime import datetime, timezone

import pytest

from backend.bintanong_tools.prospectus_extractor import ledger
from backend.bintanong_tools.prospectus_extractor.course_checks import PdfPage
from backend.bintanong_tools.prospectus_extractor.fixes import Fix
from backend.bintanong_tools.prospectus_extractor.sheet import (
    build_entries, candidate_sha256, parse_sheet, render_sheet,
)
from backend.bintanong_tools.prospectus_extractor.verify import verify_candidate
from backend.bintanong_tools.prospectus_review_gui.answers import Answer, answer_to_entries
from backend.bintanong_tools.prospectus_review_gui.questions import build_questions

import fixer_fixtures as fx
from sheet_helpers import edit_row, set_line

HASH = "a" * 64
NOW = datetime(2026, 10, 5, 10, 0, tzinfo=timezone.utc)
SECOND_FIX = Fix("move_term", "term", "1st Year / 1st Semester", "1st Year / 2nd Semester", "second proposal", "move_term:term@t0-c26")

# name -> (fixture, with a second proposal on S1-02, sheet steps, [(qid, Answer, sheet via)])
CASES = {
    "ok on a clean row": ("bscs", False, [("row", "S1-02", {"decision": "ok"})], [("S1-02", Answer("yes"), "sheet")]),
    "ok with a reason": ("bscs", False, [("row", "S1-02", {"decision": "ok: read on the PDF"})],
                         [("S1-02", Answer("yes", reason="read on the PDF"), "sheet")]),
    "fix with a proposal": ("arch", False, [("row", "S1-02", {"decision": "fix a"})],
                            [("S1-02", Answer("other", proposals=["a"]), "sheet")]),
    "fix a with a rejected second proposal": ("arch", True, [("row", "S1-02", {"decision": "fix a: only the title"})],
                                              [("S1-02", Answer("other", proposals=["a"], reason="only the title"), "sheet")]),
    "edit code": ("bscs", False, [("row", "S1-02", {"decision": "edit: misprint", "new_code": "CC 1/X"})],
                  [("S1-02", Answer("other", edits={"course_code": "CC 1/X"}, reason="misprint"), "sheet")]),
    "edit title": ("bscs", False, [("row", "S1-02", {"decision": "edit: typo", "new_title": "Intro to Computing"})],
                   [("S1-02", Answer("other", edits={"course_title": "Intro to Computing"}, reason="typo"), "sheet")]),
    "edit term": ("bscs", False, [("row", "S1-02", {"decision": "edit: term", "new_term": "2nd year first sem"})],
                  [("S1-02", Answer("other", edits={"term": "2nd year first sem"}, reason="term"), "sheet")]),
    "edit all three": ("bscs", False, [("row", "S1-02", {"decision": "edit: all", "new_code": "ZZ 9", "new_title": "Z",
                                                         "new_term": "3rd Year / 2nd Semester"})],
                       [("S1-02", Answer("other", edits={"course_code": "ZZ 9", "course_title": "Z",
                                                         "term": "3rd Year / 2nd Semester"}, reason="all"), "sheet")]),
    "unresolved": ("bscs", False, [("row", "S1-01", {"decision": "unresolved: cannot read"})],
                   [("S1-01", Answer("no", reason="cannot read"), "sheet")]),
    "unclaimed ok": ("arch", False, [("row", "SU-U1", {"decision": "ok: footnote"})],
                     [("SU-U1", Answer("yes", reason="footnote"), "sheet")]),
    "unclaimed unresolved": ("arch", False, [("row", "SU-U2", {"decision": "unresolved: unclear"})],
                             [("SU-U2", Answer("no", reason="unclear"), "sheet")]),
    "section confirm": ("bscs", False, [("line", "S1", "confirm", "yes")], [("S1:confirm", Answer("yes"), "section_confirm")]),
    "section confirm with a note": ("bscs", False, [("line", "S2", "confirm", "yes"), ("line", "S2", "reason", "against the PDF")],
                                    [("S2:confirm", Answer("yes", note="against the PDF"), "section_confirm")]),
}


def environment(fixture, second_fix):
    payload = getattr(fx, {"bscs": "bscs", "arch": "architecture"}[fixture])()
    v = verify_candidate(payload, {1: PdfPage(fx.ARCH_PAGE_TEXT)} if fixture == "arch" else None)
    if second_fix:
        row = next(r for s in v.sections for r in s.rows if r.rid == "S1-02")
        row.fixes.append(("b", SECOND_FIX))
    return payload, v


def sheet_entries(payload, v, steps):
    text = render_sheet(payload, v, {"pdf_sha256": HASH, "candidate_sha256": candidate_sha256(payload)})
    for step in steps:
        text = edit_row(text, step[1], **step[2]) if step[0] == "row" else set_line(text, step[1], step[2], step[3])
    parsed = parse_sheet(text)
    assert parsed.errors == []
    entries, errors = build_entries(parsed, payload, v, reviewer="Nestor", pdf_sha256=HASH, now=NOW)
    assert errors == []
    return entries


def gui_entries(payload, v, answers, force_via=True):
    questions = {q.qid: q for q in build_questions(payload, v, [], HASH)}
    out = []
    for qid, answer, sheet_via in answers:
        kwargs = {"via": sheet_via} if force_via else {}
        entries, errors = answer_to_entries(questions[qid], answer, payload=payload, verification=v, reviewer="Nestor",
                                            pdf_sha256=HASH, now=NOW, ledger_entries=[], **kwargs)
        assert errors == [], errors
        out += entries
    return out


def as_json(entries):
    return json.loads(json.dumps(entries, sort_keys=True))


@pytest.mark.parametrize("name", list(CASES))
def test_gui_entries_equal_sheet_entries_for_every_verb(name):
    fixture, second, steps, answers = CASES[name]
    payload, v = environment(fixture, second)
    from_sheet = sheet_entries(payload, v, steps)
    from_gui = gui_entries(payload, v, answers)
    assert from_sheet, name
    assert as_json(from_gui) == as_json(from_sheet)   # same keys, same values, same entry_id


@pytest.mark.parametrize("name", list(CASES))
def test_default_gui_entries_differ_from_sheet_entries_only_in_via_and_entry_id(name):
    fixture, second, steps, answers = CASES[name]
    payload, v = environment(fixture, second)
    from_sheet = as_json(sheet_entries(payload, v, steps))
    from_gui = as_json(gui_entries(payload, v, answers, force_via=False))
    assert len(from_gui) == len(from_sheet)
    for g, s in zip(from_gui, from_sheet):
        assert set(g) == set(s)
        assert g["via"] in ("gui", "gui_section_confirm") and s["via"] in ("sheet", "section_confirm")
        assert {k: v_ for k, v_ in g.items() if k not in ("via", "entry_id")} == {k: v_ for k, v_ in s.items() if k not in ("via", "entry_id")}
        assert g["entry_id"] != s["entry_id"]


def comparable(corrected):
    out = deepcopy(corrected)
    out["review"].pop("applied_entry_ids")
    out["review"]["skipped"] = [{k: v for k, v in s.items() if k != "entry_id"} for s in out["review"]["skipped"]]
    return as_json(out)


def test_gui_ledger_materialises_to_the_same_corrected_candidate_as_the_sheet_ledger(tmp_path):
    fixture, second, steps, answers = CASES["edit all three"]
    payload, v = environment("bscs", False)
    steps = [("row", "S1-02", {"decision": "edit: all", "new_code": "ZZ 9", "new_title": "Z", "new_term": "3rd Year / 2nd Semester"}),
             ("row", "S2-01", {"decision": "ok"})]
    answers = [("S1-02", Answer("other", edits={"course_code": "ZZ 9", "course_title": "Z", "term": "3rd Year / 2nd Semester"}, reason="all"), "sheet"),
               ("S2-01", Answer("yes"), "sheet")]
    sheet_ledger, gui_ledger = tmp_path / "sheet.jsonl", tmp_path / "gui.jsonl"
    assert ledger.append_entries(sheet_ledger, sheet_entries(payload, v, steps))[0] == 5
    assert ledger.append_entries(gui_ledger, gui_entries(payload, v, answers, force_via=False))[0] == 5
    from_sheet = ledger.materialise(payload, ledger.read_entries(sheet_ledger), HASH)
    from_gui = ledger.materialise(payload, ledger.read_entries(gui_ledger), HASH)
    assert "ZZ 9" in [c["course_code"] for c in from_sheet[0]["courses"]]   # finalize_courses re-sorts by term
    assert comparable(from_gui[0]) == comparable(from_sheet[0])
    assert as_json(from_gui[0]["review"]["content_review"]) == as_json(from_sheet[0]["review"]["content_review"])
    assert len(from_gui[0]["review"]["applied_entry_ids"]) == len(from_sheet[0]["review"]["applied_entry_ids"]) == 3


def test_gui_only_fields_materialise(tmp_path):
    payload, v = environment("bscs", False)
    questions = {q.qid: q for q in build_questions(payload, v, [], HASH)}
    answer = Answer("other", reason="read on the PDF",
                    edits={"lecture_units": "1", "lab_units": "0", "total_units": "1", "prerequisites_raw": "CS 1"})
    entries, errors = answer_to_entries(questions["S1-02"], answer, payload=payload, verification=v, reviewer="Nestor", pdf_sha256=HASH, now=NOW)
    assert errors == []
    path = tmp_path / "gui.jsonl"
    ledger.append_entries(path, entries)
    corrected, report = ledger.materialise(payload, ledger.read_entries(path), HASH)
    course = corrected["courses"][1]
    assert (course["lecture_units"], course["lab_units"], course["total_units"]) == (1, 0, 1)
    assert course["prerequisites_raw"] == "CS 1" and course["prerequisites"] == ["CS 1"]   # re-resolved from the raw text
    assert report["applied"] == 4
    assert corrected["review"]["verification_counts"] == verify_candidate(corrected).counts()
    assert payload["courses"][1]["lecture_units"] == 2   # the raw candidate is untouched


def test_gui_entries_append_idempotently(tmp_path):
    payload, v = environment("bscs", False)
    answers = [("S1-02", Answer("other", edits={"course_title": "Intro"}, reason="typo"), "gui")]
    path = tmp_path / "gui.jsonl"
    assert ledger.append_entries(path, gui_entries(payload, v, answers)) == (2, 0)
    assert ledger.append_entries(path, gui_entries(payload, v, answers)) == (0, 2)
    assert len(ledger.read_entries(path)) == 2
