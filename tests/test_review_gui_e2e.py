"""Task 11: whole review sessions on synthetic data, through the HTTP API a browser would use. Needs the `review` extra."""

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402

from backend.bintanong_tools.prospectus_extractor import ledger  # noqa: E402
from backend.bintanong_tools.prospectus_extractor.ledger import FIELD_PREREQ, content_review_state, read_entries  # noqa: E402
from backend.bintanong_tools.prospectus_extractor.sheet import build_entries, candidate_sha256, parse_sheet, render_sheet  # noqa: E402
from backend.bintanong_tools.prospectus_extractor.verify import verify_candidate  # noqa: E402
from backend.bintanong_tools.prospectus_review_gui.app import create_app, new_token  # noqa: E402
from backend.bintanong_tools.prospectus_review_gui.session import open_session  # noqa: E402

import fixer_fixtures as fx  # noqa: E402
import review_gui_fixtures as rf  # noqa: E402
from sheet_helpers import edit_row, set_line  # noqa: E402
from test_review_gui_prerequisites import with_states  # noqa: E402
from test_review_gui_sheet_equivalence import comparable  # noqa: E402

PORT = 8765
SMOKE = Path(__file__).resolve().parents[1] / "scripts" / "prospectus_review_gui_smoke.py"


def open_app(ws):
    session = open_session(ws.candidate, ws.identity, "Nestor", ws.review)
    token = new_token()
    return session, TestClient(create_app(session, token, port=PORT), base_url=f"http://127.0.0.1:{PORT}"), token


def post(client, token, path, body):
    return client.post(path, content=json.dumps(body), headers={"X-Review-Token": token, "Content-Type": "application/json"})


def answer(client, token, qid, choice, **fields):
    response = post(client, token, "/api/answer", {"qid": qid, "choice": choice, **fields})
    assert response.status_code == 200, (qid, response.text)
    return response.json()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def test_full_session_synthetic(tmp_path):
    ws = rf.workspace(tmp_path, with_states())
    raw_before = sha(ws.candidate)
    session, client, token = open_app(ws)
    try:
        queue = client.get("/api/queue").json()["queue"]
        qids = [q["qid"] for q in queue]
        assert qids[0] == "S3-01" and set(qids[-3:]) == {"S3-01:prereq", "S1-01:prereq", "S2-02:prereq"}   # broken first, prerequisites last
        assert "S1:confirm" in [q["qid"] for q in client.get("/api/queue").json()["all"]]
        assert "S2:confirm" not in qids   # a review section gets no bulk question
        answer(client, token, "S1:confirm", "yes")                                           # bulk, 2 courses
        answer(client, token, "S2-01", "yes")
        answer(client, token, "S2-02", "other", edits={"course_title": "Computer Programming Two"}, reason="printed so")
        answer(client, token, "S3-01", "no", reason="cannot read the units")                 # stays open
        refused = post(client, token, "/api/answer", {"qid": "SU-U1", "choice": "other", "edits": {"course_code": "X 1"}, "reason": "r"})
        assert refused.status_code == 422                                                    # an unclaimed code refuses Other
        assert post(client, token, "/api/answer", {"qid": "SU-U1", "choice": "yes"}).status_code == 422   # Yes needs a reason
        answer(client, token, "SU-U1", "yes", reason="a footnote")
        assert answer(client, token, "S1-01:prereq", "yes")["written"] == 1                  # Yes on a blank
        assert answer(client, token, "S2-02:prereq", "other", edits={FIELD_PREREQ: "CS 1"}, reason="read on the PDF")["written"] == 1
        assert answer(client, token, "S3-01:prereq", "no", reason="cannot tell")["written"] == 1
        state = client.get("/api/state").json()
        assert state["content_review"]["state"] == "partially_reviewed"
        assert state["content_review"]["unresolved"] == 1 and state["content_review"]["unclaimed_undecided"] == 0   # one course, counted once
        assert state["approval_line"] == "A reviewed prospectus is not an approved curriculum"
        assert state["content_review"]["state"] == "partially_reviewed"
        unresolved = sorted((e["locator"]["code_at_review"], e["field"]) for e in read_entries(ws.ledger) if e["disposition"] == "unresolved")
        assert unresolved == [("GE-ET", "prerequisites_raw"), ("GE-ET", "row")]   # the course No and the prerequisite No, both on the same course
        done = post(client, token, "/api/materialise", {})
        assert done.status_code == 200 and done.json()["content_review"]["state"] == "partially_reviewed"
    finally:
        session.close()
    corrected = json.loads((ws.review / "corrected_candidate.json").read_text(encoding="utf-8"))
    by_code = {c["course_code"]: c for c in corrected["courses"]}
    assert [c["prerequisite_state"] for c in corrected["courses"] if c["prerequisite_state"] == "reviewed_empty"] == ["reviewed_empty"]
    assert by_code["CS 1"]["prerequisite_state"] == "reviewed_empty"            # accepted on a blank
    assert by_code["GE-ET"]["prerequisite_state"] == "blank_unreviewed"         # No stays unreviewed
    assert by_code["CC 3/L"]["prerequisites_raw"] == "CS 1" and by_code["CC 3/L"]["prerequisite_state"] != "reviewed_empty"
    assert any(c["course_title"] == "Computer Programming Two" for c in corrected["courses"])
    assert corrected["review"]["content_review"]["state"] == "partially_reviewed"
    assert sha(ws.candidate) == raw_before                                      # the raw candidate is never written
    assert {e["via"] for e in read_entries(ws.ledger)} == {"gui", "gui_section_confirm"}


def test_session_survives_restart(tmp_path):
    ws = rf.workspace(tmp_path, with_states())
    session, client, token = open_app(ws)
    answer(client, token, "S2-01", "yes")
    answer(client, token, "S1-01:prereq", "yes")
    before = {q["qid"]: q["decided"] for q in client.get("/api/queue").json()["all"]}
    ledger_bytes = ws.ledger.read_bytes()
    session.close()
    session, client, token = open_app(ws)   # a new session, the same ledger
    try:
        after = {q["qid"]: q["decided"] for q in client.get("/api/queue").json()["all"]}
        assert after == before and after["S2-01"] and after["S1-01:prereq"] and not after["S2-02"]
        assert ws.ledger.read_bytes() == ledger_bytes
    finally:
        session.close()


def test_resume_after_candidate_rerun_marks_old_entries_stale(tmp_path):
    ws = rf.workspace(tmp_path, with_states())
    session, client, token = open_app(ws)
    answer(client, token, "S2-01", "yes")
    assert client.get("/api/state").json()["content_review"]["stale_entries"] == 0
    session.close()
    rerun = json.loads(ws.candidate.read_text(encoding="utf-8"))
    rerun["courses"][2]["course_title"] = "Discrete Structures Two"   # the extractor reads the title differently now
    ws.candidate.write_text(json.dumps(rerun, ensure_ascii=False), encoding="utf-8")
    session, client, token = open_app(ws)
    try:
        review = client.get("/api/state").json()["content_review"]
        assert review["stale_entries"] + review["orphan_entries"] >= 1 and review["decided"] == 0
        queue = client.get("/api/queue").json()
        assert "S2-01" in [q["qid"] for q in queue["queue"]]                 # back in the queue
        assert not {q["qid"]: q for q in queue["all"]}["S2-01"]["decided"]
    finally:
        session.close()


def test_gui_and_sheet_ledgers_agree_entry_for_entry_and_materialise_equal(tmp_path):
    payload = fx.bscs()
    ws = rf.workspace(tmp_path, payload)
    v = verify_candidate(payload, None)
    text = render_sheet(payload, v, {"pdf_sha256": rf.HASH, "candidate_sha256": candidate_sha256(payload)})
    text = set_line(text, "S1", "confirm", "yes")
    text = edit_row(text, "S2-01", decision="edit: typo", new_title="Discrete Structures Two")
    parsed = parse_sheet(text)
    assert parsed.errors == []
    sheet, errors = build_entries(parsed, payload, v, reviewer="Nestor", pdf_sha256=rf.HASH, now=rf.NOW)
    assert errors == [] and sheet
    from_sheet = content_review_state(payload, sheet, rf.HASH)
    session, client, token = open_app(ws)
    try:
        answer(client, token, "S1:confirm", "yes")
        answer(client, token, "S2-01", "other", edits={"course_title": "Discrete Structures Two"}, reason="typo")
        from_gui = client.get("/api/state").json()["content_review"]
    finally:
        session.close()
    gui = read_entries(ws.ledger)
    assert from_gui == from_sheet and from_sheet["state"] == "partially_reviewed"
    assert content_review_state(payload, gui, rf.HASH) == from_sheet

    def core(entries):   # everything but how and when it was made
        return sorted(({k: v_ for k, v_ in e.items() if k not in ("via", "entry_id", "recorded_at")} for e in entries),
                      key=lambda e: json.dumps(e, sort_keys=True))
    assert core(gui) == core(sheet)
    assert {e["via"] for e in gui} == {"gui", "gui_section_confirm"} and {e["via"] for e in sheet} == {"sheet", "section_confirm"}
    corrected_gui, corrected_sheet = (ledger.materialise(payload, entries, rf.HASH)[0] for entries in (gui, sheet))
    assert comparable(corrected_gui) == comparable(corrected_sheet)
    assert "Discrete Structures Two" in [c["course_title"] for c in corrected_gui["courses"]]

def test_smoke_script_drives_a_synthetic_prospectus_and_prints_counts(tmp_path):
    spec = importlib.util.spec_from_file_location("review_gui_smoke", SMOKE)
    smoke = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(smoke)
    ws = rf.workspace(tmp_path, with_states())
    result = smoke.run(ws.candidate, None, ws.review, "Nestor", pdf_sha256=rf.HASH)
    assert result["sections"]["clean"] == 1 and result["bulk_questions"] == 1
    assert result["first_queue_qid"] == "S3-01"
    assert result["materialised"]["file"] == "corrected_candidate.json"
    assert result["answers"]["bulk_yes"] == 1 and result["answers"]["refused"] == []
    assert (ws.review / "corrected_candidate.json").is_file()
