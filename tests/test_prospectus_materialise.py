import copy
import json
from datetime import datetime, timezone

from backend.bintanong_tools.prospectus_extractor.ledger import (
    CORRECTED, course_locator, course_snapshot, make_entry, materialise, write_corrected,
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


def test_entries_for_another_pdf_are_reported_not_applied():
    payload = fx.bscs()
    course = payload["courses"][0]
    theirs = corrected_title(course, "Theirs", pdf=OTHER)
    corrected, report = materialise(payload, [theirs], HASH)
    assert corrected["courses"][0]["course_title"] == "Discrete Structures 1"
    assert report["skipped"] == [{"entry_id": theirs["entry_id"], "reason": "pdf_sha256_mismatch"}]
    assert corrected["review"]["content_review"]["inapplicable_entries"] == 1


def test_materialise_applies_corrections_rebuilds_views_and_leaves_the_input_alone():
    payload = fx.architecture()
    original = copy.deepcopy(payload)
    gepc, toa = payload["courses"][3], payload["courses"][1]
    move = payload["courses"][4]   # AD-2/L: 1st Year 2nd Semester
    entries = [
        entry(gepc), corrected_title(gepc, "Purposive Communication"),
        entry(toa), corrected_title(toa, "Theory of Architecture1"),
        entry(move), entry(move, "term", "corrected", "1st Year / 2nd Semester", "1st Year / 1st Semester"),
    ]
    corrected, report = materialise(payload, entries, HASH)
    assert payload == original                                          # never edited in place
    by_code = {c["course_code"]: c for c in corrected["courses"]}
    assert by_code["GE-PC"]["course_title"] == "Purposive Communication" and by_code["GE-PC"]["title"] == "Purposive Communication"
    assert by_code["AD-2/L"]["semester"] == "1st Semester" and by_code["AD-2/L"]["term_index"] == 11
    assert [c["course_code"] for c in corrected["curriculum_by_term"]["1st Year"]["1st Semester"]][-1] == "AD-2/L"
    assert corrected["review"]["applied_entry_ids"] == sorted(e["entry_id"] for e in entries if e["disposition"] == CORRECTED)
    assert report["applied"] == 3 and report["skipped"] == []
    assert set(corrected["review"]["derived_sections_stale"]) >= {"audit", "prolog", "rag"}
    assert corrected["review"]["verification_counts"] == {"prereq_order": 1, "unit_total": 2}  # the move is a bad one: the verifier says so
    assert corrected["review"]["content_review"]["state"] == "partially_reviewed"


def test_a_correction_is_skipped_when_the_value_it_was_made_against_has_changed_or_the_course_is_gone():
    payload = fx.architecture()
    toa = payload["courses"][1]
    stale = corrected_title(toa, "Theory of Architecture1")
    stale["old_value"] = "something the extractor no longer produces"
    gone = copy.deepcopy(toa)
    gone["provenance"]["source_cell_ids"] = ["t9-c1"]
    lost = corrected_title(gone, "Nowhere")
    corrected, report = materialise(payload, [entry(toa), stale, entry(gone), lost], HASH)
    assert {s["reason"] for s in report["skipped"]} == {"old_value_changed", "course_not_found"}
    assert corrected["courses"][1]["course_title"] == toa["course_title"]


def test_a_later_row_accept_reverts_an_earlier_correction():
    payload = fx.architecture()
    toa = payload["courses"][1]
    entries = [entry(toa), corrected_title(toa, "Theory of Architecture1"), entry(toa, reason="reverted")]
    corrected, report = materialise(payload, entries, HASH)
    assert report["applied"] == 0
    assert {c["course_code"]: c["course_title"] for c in corrected["courses"]}["TOA-1/L"] == toa["course_title"]


def test_the_corrected_candidate_is_byte_identical_for_the_same_inputs(tmp_path):
    payload = fx.architecture()
    toa = payload["courses"][1]
    entries = [entry(toa), corrected_title(toa, "Theory of Architecture1")]
    one, two = tmp_path / "one.json", tmp_path / "two.json"
    write_corrected(one, materialise(payload, entries, HASH)[0])
    write_corrected(two, materialise(copy.deepcopy(payload), list(entries), HASH)[0])
    assert one.read_bytes() == two.read_bytes() and b"\r\n" not in one.read_bytes()


def test_the_raw_candidate_file_is_byte_identical_after_materialising(tmp_path):
    payload = fx.architecture()
    toa = payload["courses"][1]
    raw = tmp_path / "candidate.json"
    write_corrected(raw, payload)                  # stands in for the extractor's file
    before = raw.read_bytes()
    loaded = json.loads(raw.read_text(encoding="utf-8"))
    corrected, _ = materialise(loaded, [entry(toa), corrected_title(toa, "Theory of Architecture1")], HASH)
    write_corrected(tmp_path / "corrected.json", corrected)
    assert raw.read_bytes() == before
    assert json.loads(raw.read_text(encoding="utf-8")) == payload
