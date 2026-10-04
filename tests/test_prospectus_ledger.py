import json
from datetime import datetime, timezone

import pytest

from backend.bintanong_tools.prospectus_extractor.ledger import (
    LedgerError, append_entries, entry_problem, content_review_state, course_locator, course_snapshot, latest_by_field,
    make_entry, read_entries, split_applicable, unclaimed_locator,
)

import fixer_fixtures as fx

HASH = "a" * 64
OTHER = "b" * 64
NOW = datetime(2026, 10, 4, 9, 30, tzinfo=timezone.utc)


def entry(course, field="row", disposition="accepted", old=None, new=None, pdf=HASH, reason="r", **extra):
    snapshot = course_snapshot(course)
    return make_entry(
        reviewer="Nestor", reason=reason, pdf_sha256=pdf, locator=course_locator(course), field=field,
        disposition=disposition, old_value=snapshot if old is None and field == "row" else old,
        new_value=snapshot if new is None and field == "row" else new, section="1st Year - 1st Semester",
        now=NOW, **extra)


def corrected_title(course, new, pdf=HASH):
    return entry(course, "course_title", "corrected", course["course_title"], new, pdf=pdf, fix_id="title_from_pdf:course_title@x")


def test_an_entry_carries_every_field_the_master_plan_names():
    course = fx.bscs()["courses"][0]
    e = corrected_title(course, "Discrete Structures 1")
    assert {"reviewer", "recorded_at", "reason", "pdf_sha256", "locator", "field", "old_value", "new_value",
            "disposition", "fix_id", "section", "entry_id", "ledger_version"} <= set(e)
    assert e["recorded_at"] == "2026-10-04T09:30:00Z"
    assert e["locator"] == {"kind": "course", "table_index": 0, "page": 1, "code_at_review": "CS 1",
                            "cell_ids": ["t0-c11", "t0-c12", "t0-c8", "t0-c9"]}
    assert e == corrected_title(course, "Discrete Structures 1")        # same content, same id
    assert e["entry_id"] != corrected_title(course, "Other")["entry_id"]


def test_an_entry_needs_a_reviewer_a_hash_and_a_known_disposition():
    course = fx.bscs()["courses"][0]
    bad = dict(reviewer="", reason="r", pdf_sha256=HASH, locator=course_locator(course), field="row", disposition="accepted",
               old_value=None, new_value=None, section="s")
    with pytest.raises(LedgerError):
        make_entry(**bad)
    with pytest.raises(LedgerError):
        make_entry(**{**bad, "reviewer": "N", "disposition": "approved"})
    with pytest.raises(LedgerError):
        make_entry(**{**bad, "reviewer": "N", "pdf_sha256": ""})


def test_the_ledger_is_append_only_and_applying_the_same_group_twice_writes_nothing(tmp_path):
    course = fx.bscs()["courses"][0]
    path = tmp_path / "review" / "decision_ledger.jsonl"
    group = [entry(course), corrected_title(course, "Discrete Structures 1")]
    assert append_entries(path, group) == (2, 0)
    before = path.read_bytes()
    assert append_entries(path, group) == (0, 2)
    assert path.read_bytes() == before
    assert b"\r\n" not in before and [json.loads(l)["field"] for l in before.decode().splitlines()] == ["row", "course_title"]
    later = [entry(course, "row", "unresolved", new=None, reason="cannot read the PDF")]
    assert append_entries(path, later) == (1, 0)
    assert path.read_bytes().startswith(before)                                  # old lines untouched
    assert len(read_entries(path)) == 3


def test_a_damaged_ledger_is_read_line_by_line_and_the_bad_lines_are_reported(tmp_path):
    path = tmp_path / "decision_ledger.jsonl"
    path.write_text('{"not": "an entry"}\n{broken\n', encoding="utf-8")
    entries = read_entries(path)                      # never fatal
    assert [bool(entry_problem(e)) for e in entries] == [True, True]
    assert "line 1" in entry_problem(entries[0]) and "not JSON" in entry_problem(entries[1])
    assert append_entries(path, [entry(fx.bscs()["courses"][0])]) == (1, 0)


def test_entries_for_another_pdf_are_inapplicable():
    course = fx.bscs()["courses"][0]
    mine, theirs = corrected_title(course, "Mine"), corrected_title(course, "Theirs", pdf=OTHER)
    assert split_applicable([mine, theirs], HASH) == ([mine], [theirs])


def test_the_latest_decision_per_field_wins_and_a_row_entry_decides_all_fields():
    course = fx.bscs()["courses"][0]
    first, fix = entry(course), corrected_title(course, "New")
    revert = entry(course, reason="changed my mind")
    key = ("course", tuple(course_locator(course)["cell_ids"]))
    assert latest_by_field([first, fix])[(key, "course_title")] is fix
    assert latest_by_field([first, fix])[(key, "course_code")] is first
    assert latest_by_field([first, fix, revert])[(key, "course_title")] is revert


def decided_all(payload, disposition="accepted"):
    return [entry(c, "row", disposition, new=None if disposition == "unresolved" else None) for c in payload["courses"]]


def test_content_review_state_is_pending_partial_or_reviewed():
    payload = fx.bscs()
    assert content_review_state(payload, [], HASH) == {
        "state": "pending", "courses": 4, "decided": 0, "unresolved": 0, "unclaimed_undecided": 0, "inapplicable_entries": 0,
        "invalid_entries": 0, "stale_entries": 0, "stale_lines": []}
    some = decided_all(payload)[:3]
    assert content_review_state(payload, some, HASH)["state"] == "partially_reviewed"
    assert content_review_state(payload, some, HASH)["decided"] == 3
    assert content_review_state(payload, decided_all(payload), HASH)["state"] == "reviewed"
    unresolved = decided_all(payload)[:3] + [entry(payload["courses"][3], "row", "unresolved", new=None)]
    state = content_review_state(payload, unresolved, HASH)
    assert (state["state"], state["unresolved"]) == ("partially_reviewed", 1)
    assert content_review_state(payload, decided_all(payload), OTHER)["state"] == "pending"
    assert content_review_state(payload, decided_all(payload), OTHER)["inapplicable_entries"] == 4


def test_a_course_with_an_unresolved_field_is_not_decided_even_after_other_fields_were_accepted():
    payload = fx.bscs()
    course = payload["courses"][0]
    mixed = decided_all(payload) + [entry(course, "course_title", "unresolved", course["course_title"], None)]
    state = content_review_state(payload, mixed, HASH)
    assert (state["state"], state["decided"], state["unresolved"]) == ("partially_reviewed", 3, 1)


def test_listed_printed_codes_must_be_decided_before_the_review_counts_as_complete():
    payload = fx.innovation()
    rows = decided_all(payload)
    assert content_review_state(payload, rows, HASH)["unclaimed_undecided"] == 3
    assert content_review_state(payload, rows, HASH)["state"] == "partially_reviewed"
    for item in payload["audit"]["unclaimed_course_candidates"]:
        rows.append(make_entry(reviewer="N", reason="not a course", pdf_sha256=HASH, locator=unclaimed_locator(item),
                               field="unclaimed", disposition="accepted", old_value=item["code"], new_value=item["code"], section="s"))
    assert content_review_state(payload, rows, HASH)["state"] == "reviewed"


def test_ledger_lines_are_lf_utf8_with_sorted_keys_on_every_platform(tmp_path):
    course = fx.bscs()["courses"][0]
    path = tmp_path / "decision_ledger.jsonl"
    group = [entry(course, reason="Ni\u00f1o \u2013 checked"), corrected_title(course, "Matem\u00e1tica")]
    append_entries(path, group)
    expected = "".join(json.dumps(e, ensure_ascii=False, sort_keys=True) + "\n" for e in group).encode("utf-8")
    assert path.read_bytes() == expected and b"\r" not in expected
    assert "Ni\u00f1o".encode("utf-8") in expected
