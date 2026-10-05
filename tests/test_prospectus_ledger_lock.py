import os
import signal
import subprocess
import sys
import threading
import types
from datetime import datetime, timezone
from pathlib import Path

import pytest

from backend.bintanong_tools.prospectus_extractor import fixer_cli
from backend.bintanong_tools.prospectus_extractor import ledger
from backend.bintanong_tools.prospectus_extractor.ledger import (
    LedgerBusy, LedgerError, LedgerLock, append_entries, lock_path_for, make_entry, read_entries, split_valid,
)
from backend.bintanong_tools.prospectus_extractor.sheet import candidate_sha256, render_sheet
from backend.bintanong_tools.prospectus_extractor.verify import verify_candidate

import fixer_fixtures as fx
from sheet_helpers import edit_row

ROOT = Path(__file__).resolve().parent.parent
HASH = "d" * 64
NOW = datetime(2026, 10, 5, 8, 0, tzinfo=timezone.utc)

CHILD = """
import os, sys
from backend.bintanong_tools.prospectus_extractor.ledger import LedgerLock
with LedgerLock(sys.argv[1], sys.argv[2]):
    print("locked", os.getpid(), flush=True)
    sys.stdin.readline()
"""


def holder_process(ledger_path, who):
    """A real child process holding the lock until its stdin closes or it is killed. Sets proc.real_pid (the venv
    launcher on Windows is a separate process, so Popen.pid is not the lock holder)."""
    proc = subprocess.Popen([sys.executable, "-c", CHILD, str(ledger_path), who], cwd=ROOT, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, text=True)
    tag, pid = proc.stdout.readline().split()
    assert tag == "locked"
    proc.real_pid = int(pid)
    return proc


def release(proc):
    proc.stdin.write("\n")
    proc.stdin.flush()
    proc.wait(timeout=30)


def entry(code="CS 1"):
    return make_entry(reviewer="Nestor", reason="r", pdf_sha256=HASH, locator={"kind": "course", "cell_ids": [code], "page": 1,
                      "table_index": 0, "code_at_review": code}, field="row", disposition="accepted", old_value={"a": code},
                      new_value={"a": code}, section="S", now=NOW)


def test_lock_is_created_next_to_the_ledger_and_released_on_exit(tmp_path):
    path = tmp_path / "review" / "decision_ledger.jsonl"
    with LedgerLock(path, "test"):
        assert lock_path_for(path) == tmp_path / "review" / "decision_ledger.jsonl.lock"
        assert lock_path_for(path).is_file()
        assert not path.exists()  # the lock never creates the ledger itself
    with LedgerLock(path, "test again"):
        pass


def test_second_lock_in_another_process_raises_ledger_busy_naming_the_holder(tmp_path):
    path = tmp_path / "decision_ledger.jsonl"
    proc = holder_process(path, "review-gui-test")
    try:
        with pytest.raises(LedgerBusy) as caught:
            LedgerLock(path, "second").__enter__()
        message = str(caught.value)
        assert "decision_ledger.jsonl is in use by" in message and "review-gui-test" in message
        assert f"pid {proc.real_pid}" in message and "close that tool or wait" in message
        assert isinstance(caught.value, LedgerError)
    finally:
        release(proc)
    with LedgerLock(path, "after release"):
        pass


def test_lock_is_released_when_the_holder_process_is_killed(tmp_path):
    path = tmp_path / "decision_ledger.jsonl"
    proc = holder_process(path, "doomed")
    os.kill(proc.real_pid, signal.SIGTERM)   # TerminateProcess on Windows: no cleanup code runs
    proc.wait(timeout=30)
    with LedgerLock(path, "survivor"):  # no stale-lock state: the OS dropped the lock with the process
        pass


def test_append_entries_refuses_while_another_process_holds_the_lock_and_writes_nothing(tmp_path):
    path = tmp_path / "decision_ledger.jsonl"
    append_entries(path, [entry("CS 1")])
    before = path.read_bytes()
    proc = holder_process(path, "other tool")
    try:
        with pytest.raises(LedgerBusy):
            append_entries(path, [entry("CS 2")])
        assert path.read_bytes() == before
    finally:
        release(proc)
    assert append_entries(path, [entry("CS 2")]) == (1, 0)


def test_append_entries_works_when_the_caller_holds_the_lock_itself(tmp_path):
    path = tmp_path / "decision_ledger.jsonl"
    with LedgerLock(path, "session") as lock:
        assert append_entries(path, [entry("CS 1")], lock=lock) == (1, 0)
        assert append_entries(path, [entry("CS 1")], lock=lock) == (0, 1)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["decision_ledger.jsonl", "decision_ledger.jsonl.lock"]
    assert len(read_entries(path)) == 1


def test_append_entries_refuses_a_lock_for_another_ledger(tmp_path):
    with LedgerLock(tmp_path / "a.jsonl", "session") as lock:
        with pytest.raises(LedgerError, match="another ledger"):
            append_entries(tmp_path / "b.jsonl", [entry()], lock=lock)
    assert not (tmp_path / "b.jsonl").exists()


def test_two_threads_of_one_process_are_serialised_by_the_session_lock_not_the_os_lock(tmp_path):
    path = tmp_path / "decision_ledger.jsonl"
    # The OS lock belongs to one open handle: a second lock object in the same process is refused, so the OS lock
    # cannot order two threads that each take their own; a session holds one lock and adds a threading.Lock.
    with LedgerLock(path, "session") as lock:
        with pytest.raises(LedgerBusy):
            LedgerLock(path, "second thread's own lock").__enter__()
        guard = threading.Lock()
        errors = []

        def work(n):
            try:
                with guard:
                    append_entries(path, [entry(f"CS {n}")], lock=lock)
            except Exception as exc:  # pragma: no cover - failure path
                errors.append(exc)

        threads = [threading.Thread(target=work, args=(n,)) for n in range(12)]
        [t.start() for t in threads]
        [t.join() for t in threads]
    assert errors == []
    valid, invalid = split_valid(read_entries(path))
    assert len(valid) == 12 and invalid == []


def test_busy_message_when_the_holder_text_is_unreadable_says_unknown_holder(tmp_path):
    path = tmp_path / "decision_ledger.jsonl"
    with LedgerLock(path, "holder"):
        with lock_path_for(path).open("r+b") as raw:  # wipe the holder text (everything after the locked byte 0)
            raw.truncate(1)
        with pytest.raises(LedgerBusy, match="in use by unknown holder; close that tool or wait"):
            LedgerLock(path, "second").__enter__()


def test_lock_file_holds_no_decision_data(tmp_path):
    path = tmp_path / "decision_ledger.jsonl"
    append_entries(path, [entry("CS 1")])
    with LedgerLock(path, "who is me") as lock:
        append_entries(path, [entry("CS 2")], lock=lock)
        with lock_path_for(path).open("rb") as raw:  # byte 0 is locked; the holder text starts at byte 1
            raw.seek(1)
            text = raw.read().decode("utf-8")
    lines = [line for line in text.splitlines() if line.strip()]
    assert len(lines) == 1 and "who is me" in lines[0] and f"pid {os.getpid()}" in lines[0]
    assert "CS 1" not in text and "locator" not in text and "entry_id" not in text


def candidate_and_sheet(tmp_path):
    payload = fx.bscs()
    cand = tmp_path / "cand" / "x_prospectus.json"
    cand.parent.mkdir()
    import json
    cand.write_text(json.dumps(payload), encoding="utf-8")
    v = verify_candidate(payload, None)
    text = render_sheet(payload, v, {"pdf_sha256": HASH, "candidate_sha256": candidate_sha256(payload)})
    sheet = tmp_path / "review" / "review_sheet.md"
    sheet.parent.mkdir()
    sheet.write_text(edit_row(text, "S1-01", decision="ok"), encoding="utf-8")
    return cand, sheet


def test_apply_exits_2_with_the_in_use_message_when_ledger_is_locked(tmp_path, capsys):
    cand, sheet = candidate_and_sheet(tmp_path)
    ledger_path = tmp_path / "review" / "decision_ledger.jsonl"
    args = ["apply", "--candidate", str(cand), "--pdf-sha256", HASH, "--sheet", str(sheet), "--ledger", str(ledger_path),
            "--reviewer", "Nestor"]
    proc = holder_process(ledger_path, "review-gui apply-test")
    try:
        assert fixer_cli.fixer_main(args) == 2
        err = capsys.readouterr().err
        assert "decision_ledger.jsonl is in use by" in err and "review-gui apply-test" in err
        assert not ledger_path.exists()
    finally:
        release(proc)
    assert fixer_cli.fixer_main(args) == 0
    assert len(read_entries(ledger_path)) == 1


def test_lock_path_for_handles_spaces_and_unicode_in_the_path(tmp_path):
    path = tmp_path / "Kuwentong Pálawan ñ" / "decision ledger.jsonl"
    with LedgerLock(path, "unicode") as lock:
        assert lock_path_for(path).name == "decision ledger.jsonl.lock"
        assert append_entries(path, [entry()], lock=lock) == (1, 0)
    with pytest.raises(LedgerBusy, match="decision ledger.jsonl is in use"):
        with LedgerLock(path, "a"):
            LedgerLock(path, "b").__enter__()


class FakeOS:
    def __init__(self, fail=False):
        self.calls, self.fail = [], fail


def fake_msvcrt(state):
    def locking(fd, mode, nbytes):
        state.calls.append(("msvcrt.locking", mode, nbytes))
        if state.fail and mode == 2:
            raise OSError("locked")
    return types.SimpleNamespace(LK_NBLCK=2, LK_UNLCK=0, locking=locking)


def fake_fcntl(state):
    def flock(fd, op):
        state.calls.append(("fcntl.flock", op))
        if state.fail and op & 4:
            raise BlockingIOError("locked")
    return types.SimpleNamespace(LOCK_EX=2, LOCK_NB=4, LOCK_UN=8, flock=flock)


def test_platform_branch_is_chosen_at_call_time(tmp_path, monkeypatch):
    state = FakeOS()
    monkeypatch.setitem(sys.modules, "msvcrt", fake_msvcrt(state))
    monkeypatch.setitem(sys.modules, "fcntl", fake_fcntl(state))

    monkeypatch.setattr(sys, "platform", "win32")
    with LedgerLock(tmp_path / "w.jsonl", "windows branch"):
        pass
    assert state.calls == [("msvcrt.locking", 2, 1), ("msvcrt.locking", 0, 1)]

    state.calls.clear()
    monkeypatch.setattr(sys, "platform", "linux")
    with LedgerLock(tmp_path / "l.jsonl", "posix branch"):
        pass
    assert state.calls == [("fcntl.flock", 2 | 4), ("fcntl.flock", 8)]


@pytest.mark.parametrize("platform", ["win32", "linux"])
def test_each_branch_turns_a_refused_lock_into_ledger_busy(tmp_path, monkeypatch, platform):
    state = FakeOS(fail=True)
    monkeypatch.setitem(sys.modules, "msvcrt", fake_msvcrt(state))
    monkeypatch.setitem(sys.modules, "fcntl", fake_fcntl(state))
    monkeypatch.setattr(sys, "platform", platform)
    lock = LedgerLock(tmp_path / "x.jsonl", "busy")
    with pytest.raises(LedgerBusy, match="in use by"):
        lock.__enter__()
    assert len(state.calls) == 1  # nothing to unlock; no handle left open
