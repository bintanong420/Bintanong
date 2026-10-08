import json
from datetime import datetime, timezone

import pytest

from backend.bintanong_tools.prospectus_extractor import fixer_cli, sheet
from backend.bintanong_tools.prospectus_extractor.ledger import (
    CORRECTED, CORRECTABLE_FIELDS, correction_problem, course_snapshot,
)
from backend.bintanong_tools.prospectus_extractor.sheet import row_entries
from backend.bintanong_tools.prospectus_extractor.verify import verify_candidate

import fixer_fixtures as fx
import sheet_golden_scenarios as golden
from sheet_helpers import edit_row

HASH = "b" * 64
NOW = datetime(2026, 10, 5, 8, 0, tzinfo=timezone.utc)


def target(rid="S1-01"):
    payload = fx.bscs()
    v = verify_candidate(payload, None)
    for section in v.sections:
        for row in section.rows:
            if row.rid == rid:
                return payload, section, row
    raise AssertionError(rid)


def call(verb, *, edits=None, reason="", rid="S1-01", letters=()):
    payload, section, row = target(rid)
    entries = []
    errors = row_entries(entries, row, section, payload, verb, list(letters), reason, edits or {}, "gui", "Nestor", HASH, NOW)
    return payload, payload["courses"][row.course], entries, errors


def test_row_entries_is_public_and_build_entries_uses_it(monkeypatch):
    assert not hasattr(sheet, "_row_entries")
    calls = []
    real = sheet.row_entries

    def spy(*args):
        calls.append(args[1].rid)
        return real(*args)

    monkeypatch.setattr(sheet, "row_entries", spy)
    payload = fx.bscs()
    v = verify_candidate(payload, None)
    text = sheet.render_sheet(payload, v, {"pdf_sha256": HASH, "candidate_sha256": sheet.candidate_sha256(payload)})
    text = edit_row(edit_row(text, "S1-01", decision="ok"), "S2-02", decision="ok")
    entries, errors = sheet.build_entries(sheet.parse_sheet(text), payload, v, reviewer="Nestor", pdf_sha256=HASH, now=NOW)
    assert errors == [] and len(entries) == 2
    assert calls == ["S1-01", "S2-02"]


def test_load_candidate_is_public():
    assert fixer_cli.load_candidate is fixer_cli._load


def test_row_entries_ok_writes_one_accepted_row_entry():
    payload, course, entries, errors = call("ok")
    assert errors == [] and len(entries) == 1
    e = entries[0]
    assert (e["field"], e["disposition"], e["reason"]) == ("row", "accepted", "accepted as extracted")
    assert e["old_value"] == e["new_value"] == course_snapshot(course)


def test_row_entries_edit_unit_field_writes_corrected_int():
    payload = fx.bscs()
    old = payload["courses"][0]["lecture_units"]
    _p, course, entries, errors = call("edit", edits={"lecture_units": old + 1}, reason="PDF prints another figure")
    assert errors == []
    assert [e["field"] for e in entries] == ["row", "lecture_units"]
    corrected = entries[1]
    assert corrected["disposition"] == CORRECTED
    assert (corrected["old_value"], corrected["new_value"]) == (old, old + 1)
    assert type(corrected["new_value"]) is int
    assert correction_problem("lecture_units", corrected["new_value"]) is None


def test_row_entries_edit_total_units_and_prerequisites():
    _p, course, entries, errors = call("edit", edits={"prerequisites_raw": "CS 2", "total_units": 4}, reason="read from the PDF")
    assert errors == []
    assert [e["field"] for e in entries] == ["row", "total_units", "prerequisites_raw"]  # ledger.CORRECTABLE_FIELDS order
    assert entries[1]["old_value"] == course["total_units"] and entries[1]["new_value"] == 4
    assert entries[2]["old_value"] == "" and entries[2]["new_value"] == "CS 2"
    assert all(e["via"] == "gui" for e in entries)


def test_row_entries_edit_may_clear_prerequisites():
    _p, course, entries, errors = call("edit", edits={"prerequisites_raw": ""}, reason="none printed", rid="S2-01")
    assert course["prerequisites_raw"] == "CS 1"
    assert errors == [] and entries[1]["new_value"] == ""


@pytest.mark.parametrize("bad", [3.5, 100, True, "3", -1])
def test_row_entries_rejects_fraction_and_out_of_range_units(bad):
    _p, _c, entries, errors = call("edit", edits={"lecture_units": bad}, reason="r")
    assert entries == []
    assert errors == [correction_problem("lecture_units", bad)]


def test_row_entries_rejects_non_text_prerequisites():
    _p, _c, entries, errors = call("edit", edits={"prerequisites_raw": 5}, reason="r")
    assert entries == [] and errors == [correction_problem("prerequisites_raw", 5)]


def test_row_entries_rejects_unchanged_value():
    payload = fx.bscs()
    course = payload["courses"][0]
    for name, value in [("lecture_units", course["lecture_units"]), ("total_units", course["total_units"]),
                        ("prerequisites_raw", course["prerequisites_raw"])]:
        _p, _c, entries, errors = call("edit", edits={name: value}, reason="r")
        assert entries == [] and errors == [f"{name}: the new value equals the current one"], name


def test_row_entries_edit_needs_a_reason_and_a_known_field():
    assert call("edit", edits={"lecture_units": 1})[3] == ["edit needs a reason after the colon"]
    assert call("edit", edits={"nonsense": "x"}, reason="r")[3]
    assert call("edit", edits={}, reason="r")[3]


def test_correctable_fields_are_the_edit_order():
    assert CORRECTABLE_FIELDS[0:3] == ("course_code", "course_title", "term")


def test_sheet_output_is_unchanged_for_code_title_term():
    frozen = json.loads(golden.GOLDEN.read_text(encoding="utf-8"))
    assert json.loads(json.dumps(golden.capture())) == frozen
    assert len(frozen) == len(golden.SCENARIOS)
