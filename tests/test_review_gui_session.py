import copy
import hashlib
import json
import threading
import time
from pathlib import Path

import pytest

from backend.bintanong_tools.prospectus_extractor import fixer_cli
from backend.bintanong_tools.prospectus_extractor.fixer_cli import FixerError
from backend.bintanong_tools.prospectus_extractor.ledger import (
    LedgerBusy, LedgerLock, lock_path_for, read_entries, split_valid,
)
from backend.bintanong_tools.prospectus_extractor.sheet import candidate_sha256, render_sheet
from backend.bintanong_tools.prospectus_extractor.verify import verify_candidate
from backend.bintanong_tools.prospectus_review_gui.answers import Answer
from backend.bintanong_tools.prospectus_review_gui.session import open_session

import review_gui_fixtures as rf
from sheet_helpers import edit_row

ROOT = Path(__file__).resolve().parent.parent


def start(ws, reviewer="Nestor", **kw):
    return open_session(ws.candidate, ws.identity, reviewer, ws.review, pdf_path=ws.pdf, **kw)


def listing(*folders):
    return {str(p.relative_to(f)) for f in folders if f.exists() for p in f.rglob("*")}


# --- the ledger lock


def test_open_session_takes_the_ledger_lock_and_releases_it_on_close(tmp_path):
    ws = rf.workspace(tmp_path)
    session = start(ws)
    try:
        assert lock_path_for(ws.ledger).is_file()
        with pytest.raises(LedgerBusy):
            LedgerLock(ws.ledger, "someone else").__enter__()
    finally:
        session.close()
    with LedgerLock(ws.ledger, "after close"):
        pass
    session.close()   # closing twice is harmless


def test_second_session_on_the_same_ledger_is_refused_with_ledger_busy(tmp_path):
    ws = rf.workspace(tmp_path)
    with start(ws):
        with pytest.raises(LedgerBusy, match="in use by .*review GUI"):
            start(ws, reviewer="Second")


def test_fixer_apply_is_refused_while_a_session_is_open(tmp_path, capsys):
    ws = rf.workspace(tmp_path)
    v = verify_candidate(ws.payload, None)
    sheet = tmp_path / "sheet.md"
    text = render_sheet(ws.payload, v, {"pdf_sha256": rf.HASH, "candidate_sha256": candidate_sha256(ws.payload)})
    sheet.write_text(edit_row(text, "S1-01", decision="ok"), encoding="utf-8")
    args = ["apply", "--candidate", str(ws.candidate), "--pdf-sha256", rf.HASH, "--sheet", str(sheet),
            "--ledger", str(ws.ledger), "--reviewer", "Other"]
    with start(ws):
        assert fixer_cli.fixer_main(args) == 2
        assert "in use by" in capsys.readouterr().err
        assert not ws.ledger.exists()


# --- opening a session


def test_open_session_refuses_a_ledger_inside_the_repository(tmp_path):
    ws = rf.workspace(tmp_path)
    inside = ROOT / "backend" / "review_gui_test_should_not_exist"
    with pytest.raises(FixerError, match="not git-ignored"):
        open_session(ws.candidate, ws.identity, "Nestor", inside)
    assert not inside.exists()


def test_open_session_accepts_a_review_dir_outside_git(tmp_path):
    ws = rf.workspace(tmp_path)
    with start(ws) as session:
        assert session.ledger_path == ws.ledger
        assert session.pdf_sha256 == rf.HASH and session.candidate_sha256 == candidate_sha256(ws.payload)


@pytest.mark.parametrize("reviewer", ["", "   ", None])
def test_open_session_needs_a_reviewer(tmp_path, reviewer):
    ws = rf.workspace(tmp_path)
    with pytest.raises(FixerError, match="reviewer"):
        start(ws, reviewer=reviewer)
    assert not ws.review.exists()


def test_session_reads_existing_ledger_and_marks_decided(tmp_path):
    ws = rf.workspace(tmp_path)
    v = verify_candidate(ws.payload, None)
    ws.review.mkdir()
    with LedgerLock(ws.ledger, "seed") as lock:
        from backend.bintanong_tools.prospectus_extractor.ledger import append_entries
        append_entries(ws.ledger, rf.decision(ws.payload, v, "S3-01"), lock)
    with start(ws) as session:
        assert session.question("S3-01").decided
        assert "S3-01" not in [q.qid for q in session.queue()]


# --- answering


def test_answer_appends_one_line_and_never_rewrites_earlier_lines(tmp_path):
    ws = rf.workspace(tmp_path)
    with start(ws) as session:
        assert session.answer("S3-01", Answer("yes"), now=rf.NOW)["written"] == 1
        before = ws.ledger.read_bytes()
        assert session.answer("S2-01", Answer("no", reason="unclear"), now=rf.NOW)["written"] == 1
        after = ws.ledger.read_bytes()
    assert after.startswith(before) and len(after.splitlines()) == 2
    assert b"\r\n" not in after


def test_second_answer_for_same_course_is_a_new_line_and_wins(tmp_path):
    ws = rf.workspace(tmp_path)
    with start(ws) as session:
        session.answer("S3-01", Answer("yes"), now=rf.NOW)
        session.answer("S3-01", Answer("no", reason="second look"), now=rf.NOW)
        assert len(read_entries(ws.ledger)) == 2
        q = session.question("S3-01")
        assert q.decision["disposition"] == "unresolved" and q.decision["reason"] == "second look"


def test_answer_with_error_writes_nothing(tmp_path):
    ws = rf.workspace(tmp_path)
    with start(ws) as session:
        result = session.answer("S3-01", Answer("other", edits={"lecture_units": "3.5"}, reason="r"))
        assert result["written"] == 0 and result["errors"]
        with pytest.raises(KeyError):
            session.answer("S9-99", Answer("yes"))
    assert not ws.ledger.exists()


def test_section_answer_reads_the_ledger_at_answer_time(tmp_path):
    ws = rf.workspace(tmp_path)
    with start(ws) as session:
        session.answer("S1-02", Answer("other", edits={"course_title": "Intro to Computing"}, reason="PDF"), now=rf.NOW)
        result = session.answer("S1:confirm", Answer("yes"), now=rf.NOW)
        assert result["errors"] == [] and result["written"] == 1   # S1-01 only; the correction stands
        assert session.materialise()["applied"] == 1


def test_concurrent_answers_are_serialised(tmp_path):
    ws = rf.workspace(tmp_path, rf.many(16))
    with start(ws) as session:
        qids = [q.qid for q in session.queue("print") if q.kind == "course"]
        assert len(qids) == 16
        errors = []
        # The check-then-write inside answer() must not overlap: watch the one ledger read it starts with and count how
        # many threads are inside it at once (a short sleep makes any overlap certain).
        gate, state, read_ledger = threading.Lock(), {"now": 0, "peak": 0}, session._entries

        def watched_entries():
            with gate:
                state["now"] += 1
                state["peak"] = max(state["peak"], state["now"])
            time.sleep(0.02)
            try:
                return read_ledger()
            finally:
                with gate:
                    state["now"] -= 1

        session._entries = watched_entries

        def work(qid):
            try:
                assert session.answer(qid, Answer("yes"))["written"] == 1
            except Exception as exc:  # pragma: no cover - failure path
                errors.append(exc)

        threads = [threading.Thread(target=work, args=(qid,)) for qid in qids]
        [t.start() for t in threads]
        [t.join() for t in threads]
        session._entries = read_ledger
    assert errors == [] and state["peak"] == 1
    entries = read_entries(ws.ledger)
    valid, invalid = split_valid(entries)
    assert len(valid) == 16 and invalid == [] and not [e for e in entries if "_unreadable" in e]


def test_state_counts_foreign_stale_and_invalid_entries(tmp_path):
    ws = rf.workspace(tmp_path)
    v = verify_candidate(ws.payload, None)
    changed = copy.deepcopy(ws.payload)
    changed["courses"][0]["course_title"] = "Not what the candidate holds"
    stale = rf.decision(changed, verify_candidate(changed, None), "S1-01")
    foreign = rf.decision(ws.payload, v, "S3-01", pdf_sha256="e" * 64)
    ws.review.mkdir()
    ws.ledger.write_text("".join(json.dumps(e) + "\n" for e in stale + foreign) + "{not json\n", encoding="utf-8")
    with start(ws) as session:
        state = session.state()
    review = state["content_review"]
    assert (review["inapplicable_entries"], review["stale_entries"], review["invalid_entries"]) == (1, 1, 1)
    assert review["state"] == "pending"
    assert state["extraction_audit"] == ws.payload["audit"]["status"]
    assert state["source_verification"]["health"] == v.health and state["source_verification"]["pdf_checked"] is False
    assert state["progress"] == {"decided": 0, "questions": len(session.questions())}
    assert "not an approval" in state["note"]


# --- safety


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def test_raw_candidate_bytes_and_pdf_bytes_unchanged_after_a_session(tmp_path):
    ws = rf.workspace(tmp_path, pdf=True)
    before = digest(ws.candidate), digest(ws.pdf)
    with start(ws) as session:
        for q in session.queue("print"):
            session.answer(q.qid, Answer("yes", reason="checked"))
        session.page_png(1, 1.0)
        session.materialise()
    assert (digest(ws.candidate), digest(ws.pdf)) == before


def test_only_the_ledger_and_the_corrected_candidate_are_written(tmp_path):
    ws = rf.workspace(tmp_path, pdf=True)
    before = listing(ws.root)
    with start(ws) as session:
        session.answer("S3-01", Answer("yes"))
        session.page_png(1, 1.0)
        session.twin()
        assert listing(ws.root) - before == {"review", str(Path("review") / "decision_ledger.jsonl"),
                                              str(Path("review") / "decision_ledger.jsonl.lock")}
        session.materialise()
    assert listing(ws.root) - before == {"review", str(Path("review") / "decision_ledger.jsonl"),
                                          str(Path("review") / "decision_ledger.jsonl.lock"),
                                          str(Path("review") / "corrected_candidate.json")}


def test_materialise_never_targets_the_raw_candidate(tmp_path, monkeypatch):
    ws = rf.workspace(tmp_path)
    import backend.bintanong_tools.prospectus_review_gui.session as session_module
    seen = {}
    real = session_module.write_corrected

    def spy(path, corrected, *, raw_candidate=None):
        seen["raw_candidate"] = raw_candidate
        return real(path, corrected, raw_candidate=raw_candidate)

    monkeypatch.setattr(session_module, "write_corrected", spy)
    with start(ws) as session:
        session.materialise()
    assert seen["raw_candidate"] == ws.candidate


def test_materialise_runs_the_outside_git_guard(tmp_path, monkeypatch):
    ws = rf.workspace(tmp_path)
    import backend.bintanong_tools.prospectus_review_gui.session as session_module
    guarded = []
    real = session_module.assert_outside_git
    monkeypatch.setattr(session_module, "assert_outside_git", lambda p: (guarded.append(Path(p).name), real(p)))
    with start(ws) as session:
        guarded.clear()
        session.materialise()
    assert guarded == ["corrected_candidate.json"]


def test_question_view_has_course_json_boxes_and_cells(tmp_path):
    ws = rf.workspace(tmp_path, pdf=True)
    with start(ws) as session:
        view = session.question_view("S1-01")
        assert view["question"]["qid"] == "S1-01" and view["course"]["course"]["course_code"] == "CS 1"
        assert view["twin_cell_ids"] == ws.payload["courses"][0]["provenance"]["source_cell_ids"]
        assert {c["cell_id"] for c in view["cells"]} == {"t0-c11", "t0-c9", "t0-c12"}
        assert list(view["boxes"]) == ["1"] and view["boxes"]["1"]["boxes"]
        assert view["pdf"] == {"available": True, "name": "x.pdf", "pages": 1}


def test_session_without_pdf_or_twin_says_so(tmp_path):
    ws = rf.workspace(tmp_path)
    with start(ws) as session:
        view = session.question_view("S1-01")
        assert view["pdf"]["available"] is False and view["boxes"] == {}
        assert session.question_view("S1:confirm")["course"] is None
        twin = session.twin()
        assert twin["html"] is None and "markup twin unavailable" in twin["reason"]


def test_a_mismatched_docling_json_is_flagged_in_the_state_and_the_twin_is_withheld(tmp_path, monkeypatch):
    from backend.bintanong_tools.prospectus_review_gui import session as session_module
    import test_review_gui_panes as panes

    ws = rf.workspace(tmp_path)
    foreign = panes.evidence_of(rf.many(4))
    monkeypatch.setattr(session_module, "load_evidence", lambda path: (foreign, None))
    with start(ws, docling_json=tmp_path / "other_docling.json") as session:
        state, twin = session.state(), session.twin()
        assert session.evidence is None
    assert state["docling"]["ok"] is False and "other_docling.json" in state["docling"]["warning"]
    assert twin["html"] is None and "another prospectus" in twin["reason"]
    good = panes.evidence_of(ws.payload)
    monkeypatch.setattr(session_module, "load_evidence", lambda path: (good, None))
    with start(ws, docling_json=tmp_path / "x_docling.json") as session:
        assert session.state()["docling"] == {"ok": True, "warning": None} and session.twin()["html"]
