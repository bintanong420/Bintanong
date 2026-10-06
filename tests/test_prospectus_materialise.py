import copy
import json
from datetime import datetime, timezone

from backend.bintanong_tools.prospectus_extractor.ledger import (entry_id_of,
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
    stale["entry_id"] = entry_id_of(stale)      # an honestly written entry, not a forged one
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


# --- Task 10: reviewed_empty is written here and nowhere else

from pathlib import Path

from backend.bintanong_tools.prospectus_extractor.authority import build_authority
from backend.bintanong_tools.prospectus_extractor.courses import finalize_courses
from backend.bintanong_tools.prospectus_extractor.prerequisites import annotate_prerequisite_states

PKG = Path(__file__).resolve().parent.parent / "backend" / "bintanong_tools" / "prospectus_extractor"


def stated(payload):
    payload['courses'] = finalize_courses(payload['courses'])[0]   # as the pipeline does, so the states are the extractor's own
    annotate_prerequisite_states(payload["courses"], (payload.get("audit") or {}).get("structural_anomalies") or [])
    return payload


def prereq_entry(course, disposition, new=None, pdf=HASH, old=""):
    old = course["prerequisites_raw"] if old is None else old
    new = old if disposition == "accepted" else new
    return entry(course, "prerequisites_raw", disposition, old, new, pdf=pdf)


def state_of(corrected, code):
    return {c["course_code"]: c["prerequisite_state"] for c in corrected["courses"]}[code]


def test_materialise_stamps_reviewed_empty_only_for_an_accepted_blank():
    payload = stated(fx.bscs())
    cs1, cc1, cs2 = payload["courses"][0], payload["courses"][1], payload["courses"][2]
    assert (cs1["prerequisite_state"], cc1["prerequisite_state"], cs2["prerequisite_state"]) == ("blank_unreviewed", "blank_unreviewed", "resolved")
    base = state_of(materialise(copy.deepcopy(payload), [], HASH)[0], "CS 1")
    assert base == "blank_unreviewed"
    # accepted on a blank: stamped
    assert state_of(materialise(copy.deepcopy(payload), [prereq_entry(cs1, "accepted")], HASH)[0], "CS 1") == "reviewed_empty"
    # accepted on a cell that is not blank: stays what the extractor said
    assert state_of(materialise(copy.deepcopy(payload), [prereq_entry(cs2, "accepted", old=None)], HASH)[0], "CS 2") == "resolved"
    # unresolved: not stamped
    assert state_of(materialise(copy.deepcopy(payload), [prereq_entry(cs1, "unresolved", old="")], HASH)[0], "CS 1") == "blank_unreviewed"
    # corrected to text: re-classified from the new text, never reviewed_empty
    out = materialise(copy.deepcopy(payload), [prereq_entry(cc1, "corrected", "CS 1")], HASH)[0]
    assert state_of(out, "CC 1/L") == "resolved"
    # corrected to empty text: the cell is still blank and the human did not accept it as such
    out = materialise(copy.deepcopy(payload), [prereq_entry(cs2, "corrected", "", old=None)], HASH)[0]
    assert state_of(out, "CS 2") == "blank_unreviewed"
    # stale (the value it was made on is gone) and another PDF: not stamped, reported
    stale = prereq_entry(cs1, "accepted", old="CC 9")
    other = prereq_entry(cs1, "accepted", pdf=OTHER)
    out, report = materialise(copy.deepcopy(payload), [stale, other], HASH)
    assert state_of(out, "CS 1") == "blank_unreviewed"
    assert {s["reason"] for s in report["skipped"]} == {"old_value_changed", "pdf_sha256_mismatch"}


def test_a_later_unresolved_or_correction_overrides_an_earlier_accepted_blank():
    payload = stated(fx.bscs())
    cs1 = payload["courses"][0]
    ledger = [prereq_entry(cs1, "accepted"), prereq_entry(cs1, "unresolved", old="")]
    assert state_of(materialise(copy.deepcopy(payload), ledger, HASH)[0], "CS 1") == "blank_unreviewed"


def test_an_unreadable_ambiguous_cell_is_never_stamped_reviewed_empty():
    payload = fx.bscs()
    payload["audit"]["structural_anomalies"] = [
        {"type": "ambiguous_adjacent_prerequisite_fragment", "source_cell_ids": ["t0-c11"]}]
    stated(payload)
    cs1 = payload["courses"][0]
    assert cs1["prerequisite_state"] == "unreadable"
    assert state_of(materialise(copy.deepcopy(payload), [prereq_entry(cs1, "accepted")], HASH)[0], "CS 1") == "unreadable"


def test_a_prerequisite_entry_for_a_course_that_is_not_there_is_an_orphan_and_stamps_nothing():
    payload = stated(fx.bscs())
    gone = copy.deepcopy(payload["courses"][0])
    gone["provenance"]["source_cell_ids"] = ["t9-c1"]
    ghost = prereq_entry(gone, "accepted")
    out, report = materialise(copy.deepcopy(payload), [ghost], HASH)
    assert report["skipped"] == [{"entry_id": ghost["entry_id"], "reason": "course_not_found"}]
    assert "reviewed_empty" not in {c["prerequisite_state"] for c in out["courses"]}


def test_materialise_rerun_is_deterministic_with_prerequisite_entries(tmp_path):
    payload = stated(fx.bscs())
    cs1, cc1 = payload["courses"][0], payload["courses"][1]
    ledger = [prereq_entry(cs1, "accepted"), prereq_entry(cc1, "corrected", "CS 1")]
    one, two = tmp_path / "one.json", tmp_path / "two.json"
    write_corrected(one, materialise(copy.deepcopy(payload), list(ledger), HASH)[0])
    write_corrected(two, materialise(copy.deepcopy(payload), list(reversed(ledger)), HASH)[0])
    assert one.read_bytes() == two.read_bytes()


def test_materialise_does_not_change_the_extractors_own_states():
    payload = stated(fx.bscs())
    before = [c["prerequisite_state"] for c in payload["courses"]]
    out, _ = materialise(copy.deepcopy(payload), [], HASH)
    assert [c["prerequisite_state"] for c in payload["courses"]] == before
    assert sorted(c["prerequisite_state"] for c in out["courses"]) == sorted(before)


def test_extractor_never_emits_reviewed_empty():
    payload = stated(fx.bscs())
    assert "reviewed_empty" not in {c["prerequisite_state"] for c in payload["courses"]}
    writers = sorted(p.name for p in PKG.glob("*.py") if '"reviewed_empty"' in p.read_text(encoding="utf-8") and p.name != "selftest.py")
    assert writers == ["ledger.py", "prerequisites.py"]   # prerequisites.py only lists the vocabulary; ledger.py is the one writer
    assert 'reviewed_empty' not in (PKG / "prerequisites.py").read_text(encoding="utf-8").split("def classify_prerequisite_state")[1]


def test_eligibility_stays_blocked_until_the_blank_is_reviewed():
    payload = fx.bscs()
    payload["courses"][1]["prerequisites_raw"] = "None"        # every other rule is understood, so the one blank is the only open prerequisite
    payload["courses"][3]["prerequisites_raw"] = "CS 1"
    stated(payload)
    assert [c["prerequisite_state"] for c in payload["courses"]] == ["blank_unreviewed", "stated_none", "resolved", "resolved"]
    cs1 = payload["courses"][0]
    metadata = {}
    review = {"state": "reviewed"}

    def blocked(courses):
        return build_authority(audit_status="ok", metadata=metadata, courses=courses, content_review=review)["authority"]["blocked_by"]

    open_ = materialise(copy.deepcopy(payload), [corrected_title(cs1, "Discrete Structures One")], HASH)[0]
    assert "prerequisite_rules_incomplete" in blocked(open_["courses"])
    done = materialise(copy.deepcopy(payload), [corrected_title(cs1, "Discrete Structures One"), prereq_entry(cs1, "accepted")], HASH)[0]
    assert state_of(done, "CS 1") == "reviewed_empty"
    assert "prerequisite_rules_incomplete" not in blocked(done["courses"])
