"""The review GUI command line. Needs the `review` extra; skipped where FastAPI is not installed."""

import io
import json
import re
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("uvicorn")

from backend.bintanong_tools.prospectus_extractor.ledger import LedgerLock, read_entries  # noqa: E402
from backend.bintanong_tools.prospectus_review_gui import cli  # noqa: E402

import review_gui_fixtures as rf  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PACKAGE = ROOT / "backend" / "bintanong_tools" / "prospectus_review_gui"


@pytest.fixture
def no_server(monkeypatch):
    """Replace the blocking server with a recorder: (app, socket) of each run."""
    runs = []

    def record(app, sock):
        runs.append((app, sock.getsockname()))
        sock.close()

    monkeypatch.setattr(cli, "run_server", record)
    monkeypatch.setattr(cli.webbrowser, "open", lambda url: runs.append(("browser", url)))
    return runs


def args(ws, *extra, port="0"):
    out = ["--candidate", str(ws.candidate), "--review-dir", str(ws.review), "--reviewer", "Nestor", "--port", port]
    out += ["--pdf", str(ws.pdf)] if ws.pdf else ["--pdf-sha256", rf.HASH]
    return out + list(extra)


def test_help_runs_and_lists_no_host_option():
    result = subprocess.run([sys.executable, "-m", "backend.bintanong_tools.prospectus_review", "--help"], cwd=ROOT,
                            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    assert result.returncode == 0, result.stderr
    assert "--candidate" in result.stdout and "--no-open" in result.stdout and "--port" in result.stdout
    assert "--host" not in result.stdout and "127.0.0.1" in result.stdout


def test_host_option_is_rejected(tmp_path, no_server):
    ws = rf.workspace(tmp_path)
    with pytest.raises(SystemExit) as caught:
        cli.review_main(args(ws, "--host", "0.0.0.0"))
    assert caught.value.code == 2 and no_server == []


def test_missing_candidate_exits_2_with_a_message(tmp_path, capsys, no_server):
    code = cli.review_main(["--candidate", str(tmp_path / "nope.json"), "--pdf-sha256", rf.HASH, "--reviewer", "N", "--no-open"])
    assert code == 2 and "cannot read candidate" in capsys.readouterr().err and no_server == []


def test_missing_reviewer_exits_2(tmp_path, monkeypatch, capsys, no_server):
    ws = rf.workspace(tmp_path)
    empty = tmp_path / "empty.gitconfig"
    empty.write_text("", encoding="utf-8")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(empty))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.chdir(tmp_path)   # outside the repository, so no repository config either
    code = cli.review_main(["--candidate", str(ws.candidate), "--pdf-sha256", rf.HASH, "--review-dir", str(ws.review), "--no-open"])
    assert code == 2 and "no reviewer" in capsys.readouterr().err
    assert not ws.review.exists() and no_server == []


def test_unsafe_review_dir_exits_2_and_creates_nothing(tmp_path, capsys, no_server):
    ws = rf.workspace(tmp_path)
    inside = ROOT / "backend" / "review_gui_cli_should_not_exist"
    code = cli.review_main(["--candidate", str(ws.candidate), "--pdf-sha256", rf.HASH, "--review-dir", str(inside),
                            "--reviewer", "N", "--no-open"])
    assert code == 2 and "not git-ignored" in capsys.readouterr().err
    assert not inside.exists() and no_server == []


def test_identity_mismatch_exits_2(tmp_path, capsys, no_server):
    payload = rf.mixed()
    payload["run_identity"] = {"pdf_sha256": "f" * 64}
    ws = rf.workspace(tmp_path, payload, pdf=True)
    assert cli.review_main(args(ws, "--no-open")) == 2
    assert "differs from the PDF hash the candidate recorded" in capsys.readouterr().err
    assert not ws.review.exists() and no_server == []


def test_server_binds_loopback_only(tmp_path):
    ws = rf.workspace(tmp_path)
    from backend.bintanong_tools.prospectus_review_gui.app import create_app, new_token
    from backend.bintanong_tools.prospectus_review_gui.session import open_session

    sock = cli.bind_loopback(0)
    host, port = sock.getsockname()[:2]
    assert host == "127.0.0.1"
    with open_session(ws.candidate, ws.identity, "Nestor", ws.review) as session:
        server = cli.make_server(create_app(session, new_token(), port=port))
        thread = threading.Thread(target=server.run, kwargs={"sockets": [sock]}, daemon=True)
        thread.start()
        try:
            for _ in range(100):
                if server.started:
                    break
                time.sleep(0.05)
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/state", timeout=10) as response:
                assert response.status == 200 and json.loads(response.read())["reviewer"] == "Nestor"
            other = outside_address()
            if other is None:
                pytest.skip("this machine has no non-loopback IPv4 address to try")
            with pytest.raises(OSError):
                socket.create_connection((other, port), timeout=3).close()
        finally:
            server.should_exit = True
            thread.join(timeout=10)


def outside_address():
    try:
        probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        probe.connect(("192.0.2.1", 9))   # TEST-NET-1: nothing is sent; this only picks the outgoing interface
        address = probe.getsockname()[0]
        probe.close()
    except OSError:
        return None
    return None if address.startswith("127.") or address == "0.0.0.0" else address


def test_port_in_use_exits_2(tmp_path, capsys, no_server):
    ws = rf.workspace(tmp_path)
    holder = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    holder.bind(("127.0.0.1", 0))
    holder.listen()
    try:
        port = holder.getsockname()[1]
        assert cli.review_main(args(ws, "--no-open", port=str(port))) == 2
        assert f"port {port} is in use" in capsys.readouterr().err
    finally:
        holder.close()
    assert no_server == []
    with LedgerLock(ws.ledger, "after"):   # the session was closed: its ledger lock is free again
        pass


def test_ledger_in_use_exits_2_with_the_holder_named(tmp_path, capsys, no_server):
    ws = rf.workspace(tmp_path)
    with LedgerLock(ws.ledger, "the first review GUI"):
        assert cli.review_main(args(ws, "--no-open")) == 2
    assert "in use by the first review GUI" in capsys.readouterr().err and no_server == []


def test_browser_opened_unless_no_open(tmp_path, no_server):
    ws = rf.workspace(tmp_path)
    assert cli.review_main(args(ws)) == 0
    browser, (_app, (host, port)) = no_server   # the browser is opened just before the server starts serving
    assert host == "127.0.0.1" and browser == ("browser", f"http://127.0.0.1:{port}/")
    no_server.clear()
    assert cli.review_main(args(ws, "--no-open")) == 0
    assert len(no_server) == 1 and no_server[0][0] != "browser"


def test_console_output_is_safe_for_non_utf8_windows_consoles(tmp_path, monkeypatch, no_server):
    payload = rf.mixed()
    payload["program"] = "Kurikulum sa Pálawan 中文"
    ws = rf.workspace(tmp_path, payload)
    out = io.TextIOWrapper(io.BytesIO(), encoding="cp1252", errors="strict")
    monkeypatch.setattr(sys, "stdout", out)
    assert cli.review_main(args(ws, "--no-open")) == 0
    out.flush()
    text = out.buffer.getvalue().decode("cp1252")
    assert "Kurikulum sa Pálawan ??" in text and "http://127.0.0.1:" in text


def test_paths_with_spaces_and_unicode_work_end_to_end(tmp_path, monkeypatch, no_server):
    from fastapi.testclient import TestClient

    ws = rf.workspace(tmp_path, pdf=True, folder="Prospectus tèst folder")
    ws.review = ws.root / "review ñ" / "x"

    def post_then_stop(app, sock):   # the "server" here drives the real app in-process, then returns
        client = TestClient(app, base_url=f"http://127.0.0.1:{sock.getsockname()[1]}")
        token = re.search(r'name="review-token" content="([^"]+)"', client.get("/").text).group(1)
        response = client.post("/api/answer", json={"qid": "S3-01", "choice": "yes"}, headers={"X-Review-Token": token})
        no_server.append(response.status_code)
        assert client.get("/api/page/1.png").status_code == 200
        sock.close()

    monkeypatch.setattr(cli, "run_server", post_then_stop)
    assert cli.review_main(args(ws, "--no-open")) == 0
    assert no_server == [200]
    ledger = ws.review / "decision_ledger.jsonl"
    assert len(read_entries(ledger)) == 1


def test_no_posix_only_calls():
    patterns = [r"\bos\.fork\b", r"\bsignal\.SIGKILL\b", r"\bfcntl\b", r"\bos\.getuid\b", r"\bos\.geteuid\b",
                r"\+\s*[\"']/[\"']", r"[\"']/[\"']\s*\+", r"[\"']\\\\[\"']", r"\bos\.sep\b"]
    sources = sorted(PACKAGE.rglob("*.py")) + [ROOT / "backend" / "bintanong_tools" / "prospectus_review.py"]
    assert len(sources) >= 9
    for path in sources:
        text = path.read_text(encoding="utf-8")
        for pattern in patterns:
            assert not re.search(pattern, text), (path.name, pattern)


def test_default_port_is_8765_and_no_host_attribute():
    parsed = cli.build_parser().parse_args(["--candidate", "c.json"])
    assert parsed.port == 8765 and not hasattr(parsed, "host")


def test_blank_reviewer_exits_2(tmp_path, monkeypatch, capsys, no_server):
    ws = rf.workspace(tmp_path)   # a blank flag falls back to git config user.name, as in the fixer; with that empty too it is refused
    empty = tmp_path / "empty.gitconfig"
    empty.write_text("", encoding="utf-8")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(empty))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.chdir(tmp_path)
    code = cli.review_main(["--candidate", str(ws.candidate), "--pdf-sha256", rf.HASH, "--review-dir", str(ws.review),
                            "--reviewer", "   ", "--no-open"])
    assert code == 2 and "no reviewer" in capsys.readouterr().err
    assert not ws.review.exists() and no_server == []


def test_missing_pdf_file_exits_2(tmp_path, capsys, no_server):
    ws = rf.workspace(tmp_path)
    code = cli.review_main(["--candidate", str(ws.candidate), "--pdf", str(tmp_path / "gone.pdf"), "--review-dir", str(ws.review),
                            "--reviewer", "N", "--no-open"])
    assert code == 2 and capsys.readouterr().err.startswith("error:")
    assert not ws.review.exists() and no_server == []


def test_each_launch_gets_its_own_token_and_writes_need_it(tmp_path, no_server):
    from fastapi.testclient import TestClient

    ws = rf.workspace(tmp_path)
    tokens = []

    def probe(app, sock):
        client = TestClient(app, base_url=f"http://127.0.0.1:{sock.getsockname()[1]}")
        tokens.append(re.search(r'name="review-token" content="([^"]+)"', client.get("/").text).group(1))
        assert client.post("/api/answer", json={"qid": "S3-01", "choice": "yes"}).status_code == 403
        assert client.post("/api/answer", json={"qid": "S3-01", "choice": "yes"}, headers={"X-Review-Token": "wrong"}).status_code == 403
        sock.close()

    import pytest as _pytest
    with _pytest.MonkeyPatch.context() as mp:
        mp.setattr(cli, "run_server", probe)
        mp.setattr(cli.webbrowser, "open", lambda url: None)
        assert cli.review_main(args(ws, "--no-open")) == 0
        assert cli.review_main(args(ws, "--no-open")) == 0
    assert len(tokens) == 2 and tokens[0] != tokens[1] and len(tokens[0]) >= 32
    assert read_entries(ws.review / "decision_ledger.jsonl") == []


def test_no_external_urls_in_the_package():
    allowed = re.compile(r"https?://(127\.0\.0\.1|localhost)\b|\{LOOPBACK\}")
    for path in sorted(PACKAGE.rglob("*")):
        if path.suffix in {".py", ".js", ".css", ".html"}:
            for found in re.findall(r"(?:https?:)?//[A-Za-z0-9.{}$_-]+", path.read_text(encoding="utf-8")):
                if found.startswith("//") and path.suffix == ".py":
                    continue   # a comment marker or path, not a URL
                assert allowed.search(found), (path.name, found)


def test_package_main_module_runs(tmp_path):
    result = subprocess.run([sys.executable, "-m", "backend.bintanong_tools.prospectus_review_gui", "--help"], cwd=ROOT,
                            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    assert result.returncode == 0 and "--candidate" in result.stdout
