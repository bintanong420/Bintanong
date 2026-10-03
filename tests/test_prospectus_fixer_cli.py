import json
from pathlib import Path

import pytest

from backend.bintanong_tools.prospectus_extractor import fixer_cli
from backend.bintanong_tools.prospectus_extractor.course_checks import PdfPage
from backend.bintanong_tools.prospectus_extractor.fixer_cli import (
    FixerError, REPO, assert_outside_git, default_review_dir, fixer_main as main, resolve_identity, resolve_reviewer,
)
from backend.bintanong_tools.prospectus_extractor.ledger import read_entries

import fixer_fixtures as fx
from sheet_helpers import edit_row, set_line

HASH = "c" * 64


def write_candidate(folder: Path, payload, name="x_prospectus.json") -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def sheet_path(candidate: Path) -> Path:
    return default_review_dir(candidate) / "review_sheet.md"


def run(*argv):
    return main([str(a) for a in argv])


def test_default_review_folder_sits_next_to_the_candidate_not_in_the_repository(tmp_path):
    candidate = write_candidate(tmp_path / "run" / "CAD", fx.bscs())
    folder = default_review_dir(candidate)
    assert folder == (tmp_path / "run" / "CAD" / "review" / "x_prospectus").resolve()
    assert_outside_git(folder)   # no error


def test_writing_into_a_tracked_place_in_the_repository_is_refused():
    with pytest.raises(FixerError, match="inside the repository and not git-ignored"):
        assert_outside_git(REPO / "docs" / "review-output")


def test_reviewer_comes_from_the_flag_or_git_config(monkeypatch):
    assert resolve_reviewer("  Nestor ") == "Nestor"

    class Done:
        stdout = "Git Name\n"

    monkeypatch.setattr(fixer_cli.subprocess, "run", lambda *a, **k: Done())
    assert resolve_reviewer(None) == "Git Name"
    Done.stdout = ""
    with pytest.raises(FixerError, match="no reviewer"):
        resolve_reviewer(None)


def test_pdf_identity_comes_from_the_file_then_the_hash_then_a_manifest(tmp_path):
    pdf = tmp_path / "a.pdf"
    pdf.write_bytes(b"%PDF fake")
    digest = fixer_cli.sha256(pdf)
    payload = {"source_path": str(tmp_path / "x_docling.json")}
    assert resolve_identity(payload, pdf=pdf) == {"pdf_sha256": digest, "pdf_path": pdf, "how": "pdf file"}
    with pytest.raises(FixerError, match="does not match"):
        resolve_identity(payload, pdf=pdf, pdf_sha256="0" * 64)
    assert resolve_identity(payload, pdf_sha256=HASH)["pdf_path"] is None
    assert resolve_identity({"run_identity": {"file_sha256": HASH}})["how"] == "run_identity"
    golden = tmp_path / "golden"
    golden.mkdir()
    (golden / "isolated_manifest.json").write_text(json.dumps({"records": [
        {"source": str(pdf), "pdf_sha256": digest, "json_path": str(tmp_path / "x_prospectus.json")}]}), encoding="utf-8")
    found = resolve_identity(payload, golden=golden, pdf_root=tmp_path)
    assert (found["pdf_sha256"], found["pdf_path"], found["how"]) == (digest, pdf, "manifest")
    (golden / "isolated_manifest.json").write_text(json.dumps({"records": [
        {"source": str(pdf), "pdf_sha256": "0" * 64, "json_path": str(tmp_path / "x_prospectus.json")}]}), encoding="utf-8")
    with pytest.raises(FixerError, match="does not match the manifest hash"):
        resolve_identity(payload, golden=golden, pdf_root=tmp_path)
    with pytest.raises(FixerError, match="pdf_sha256 unknown"):
        resolve_identity(payload)


def test_sheet_apply_status_materialise_round_trip(tmp_path, capsys):
    candidate = write_candidate(tmp_path, fx.bscs())
    assert run("sheet", "--candidate", candidate, "--pdf-sha256", HASH) == 0
    sheet = sheet_path(candidate)
    assert "health=clean" in capsys.readouterr().out and sheet.is_file()
    assert run("sheet", "--candidate", candidate, "--pdf-sha256", HASH) == 2          # would overwrite a sheet
    assert "exists" in capsys.readouterr().err
    assert run("sheet", "--candidate", candidate, "--pdf-sha256", HASH, "--force") == 0
    capsys.readouterr()

    assert run("status", "--candidate", candidate, "--pdf-sha256", HASH) == 0
    assert json.loads(capsys.readouterr().out)["state"] == "pending"

    text = set_line(set_line(sheet.read_text(encoding="utf-8"), "S1", "confirm", "yes"), "S2", "confirm", "yes")
    sheet.write_text(text, encoding="utf-8")
    assert run("apply", "--candidate", candidate, "--pdf-sha256", HASH, "--reviewer", "Nestor", "--dry-run") == 0
    assert not (sheet.parent / "decision_ledger.jsonl").exists()
    assert run("apply", "--candidate", candidate, "--pdf-sha256", HASH, "--reviewer", "Nestor") == 0
    assert "4 entries written, 0 already" in capsys.readouterr().out.splitlines()[-1]
    assert run("apply", "--candidate", candidate, "--pdf-sha256", HASH, "--reviewer", "Nestor") == 0
    assert "0 entries written, 4 already" in capsys.readouterr().out
    ledger = sheet.parent / "decision_ledger.jsonl"
    assert {e["reviewer"] for e in read_entries(ledger)} == {"Nestor"}

    assert run("status", "--candidate", candidate, "--pdf-sha256", HASH) == 0
    assert json.loads(capsys.readouterr().out)["state"] == "reviewed"
    assert run("status", "--candidate", candidate, "--pdf-sha256", "d" * 64) == 0     # another PDF: nothing applies
    other = json.loads(capsys.readouterr().out)
    assert (other["state"], other["inapplicable_entries"]) == ("pending", 4)

    assert run("materialise", "--candidate", candidate, "--pdf-sha256", HASH) == 0
    corrected = json.loads((sheet.parent / "corrected_candidate.json").read_text(encoding="utf-8"))
    assert corrected["review"]["content_review"]["state"] == "reviewed" and corrected["review"]["schema"] == "prospectus-corrected-candidate-v1"


def test_apply_refuses_a_sheet_that_no_longer_matches_the_candidate_and_writes_nothing(tmp_path, capsys):
    candidate = write_candidate(tmp_path, fx.bscs())
    assert run("sheet", "--candidate", candidate, "--pdf-sha256", HASH) == 0
    sheet = sheet_path(candidate)
    sheet.write_text(set_line(sheet.read_text(encoding="utf-8"), "S1", "confirm", "yes"), encoding="utf-8")
    changed = fx.bscs()
    changed["courses"][0]["course_title"] = "Another title"
    write_candidate(tmp_path, changed)
    capsys.readouterr()
    assert run("apply", "--candidate", candidate, "--pdf-sha256", HASH, "--reviewer", "N") == 1
    assert "regenerate it" in capsys.readouterr().err
    assert not (sheet.parent / "decision_ledger.jsonl").exists()


def test_apply_with_a_bad_decision_lists_every_problem_and_writes_nothing(tmp_path, capsys):
    candidate = write_candidate(tmp_path, fx.bscs())
    run("sheet", "--candidate", candidate, "--pdf-sha256", HASH)
    sheet = sheet_path(candidate)
    text = edit_row(sheet.read_text(encoding="utf-8"), "S1-01", decision="approve")
    sheet.write_text(edit_row(text, "S1-02", decision="edit"), encoding="utf-8")
    capsys.readouterr()
    assert run("apply", "--candidate", candidate, "--pdf-sha256", HASH, "--reviewer", "N") == 1
    err = capsys.readouterr().err
    assert "2 problem(s); nothing was written" in err and "S1-01: unknown decision" in err and "S1-02: edit: fill at least one" in err
    assert not (sheet.parent / "decision_ledger.jsonl").exists()


def test_the_pdf_text_checks_run_when_the_pdf_file_is_given(tmp_path, monkeypatch, capsys):
    pdf = tmp_path / "bsa.pdf"
    pdf.write_bytes(b"%PDF fake")
    monkeypatch.setattr(fixer_cli, "load_pdf_pages", lambda path: {1: PdfPage(fx.ARCH_PAGE_TEXT)})
    candidate = write_candidate(tmp_path, fx.architecture())
    assert run("sheet", "--candidate", candidate, "--pdf", pdf) == 0
    text = sheet_path(candidate).read_text(encoding="utf-8")
    assert "- pdf_text_checked: yes" in text and f"- pdf_sha256: {fixer_cli.sha256(pdf)}" in text and "title_from_pdf" in text
    capsys.readouterr()
    assert run("sheet", "--candidate", candidate, "--pdf", pdf, "--no-pdf-text", "--force") == 0
    assert "pdf_text_checked=no" in capsys.readouterr().out


def test_triage_lists_the_healthiest_first_and_collapses_a_repeated_pdf(tmp_path, capsys):
    runs, golden = tmp_path / "runs", tmp_path / "golden"
    golden.mkdir()
    records = []
    for number, (payload, digest) in enumerate([(fx.innovation(), "1" * 64), (fx.bscs(), "2" * 64), (fx.bscs(), "2" * 64)], 1):
        folder = runs / f"{number:02d}"
        write_candidate(folder, payload, "candidate.json")
        source = tmp_path / "docling" / f"p{number}_docling.json"
        (folder / "source.txt").write_text(str(source), encoding="utf-8")
        records.append({"source": str(tmp_path / f"p{number}.pdf"), "pdf_sha256": digest, "json_path": str(source).replace("_docling.json", "_prospectus.json")})
    (golden / "isolated_manifest.json").write_text(json.dumps({"records": records}), encoding="utf-8")
    out = tmp_path / "out" / "TRIAGE.md"
    assert run("triage", "--runs", runs, "--golden", golden, "--out", out) == 0
    lines = out.read_text(encoding="utf-8").splitlines()
    table = [l for l in lines if l.startswith("| 0")]
    assert [l.split("|")[1].strip() for l in table] == ["02", "01"]          # clean BS CS before the broken one
    assert "| clean |" in table[0] and "| broken |" in table[1] and "unclaimed_code 3" in table[1]
    assert "Skipped duplicates: 03 (same PDF as 02)" in lines[-1]


def test_the_module_entry_point_is_a_thin_wrapper():
    from backend.bintanong_tools import prospectus_fixer
    assert prospectus_fixer.main is fixer_cli.fixer_main


def test_a_damaged_ledger_is_reported_without_a_traceback(tmp_path, capsys):
    candidate = write_candidate(tmp_path, fx.bscs())
    run("sheet", "--candidate", candidate, "--pdf-sha256", HASH)
    ledger = default_review_dir(candidate) / "decision_ledger.jsonl"
    ledger.write_text("{broken\n", encoding="utf-8")
    capsys.readouterr()
    assert run("status", "--candidate", candidate, "--pdf-sha256", HASH) == 2
    assert "not JSON" in capsys.readouterr().err


def test_the_legacy_shim_still_exposes_the_extractors_own_main_and_text_constants():
    # The shim re-exports every public name of every module, last module wins: a new module that
    # defines `main` or its own DASHES would silently replace the extractor's.
    from backend.bintanong_tools.bintanong_jsonifer_prolog import bintanong_prospectus_jsonifier as shim
    from backend.bintanong_tools.prospectus_extractor import cli, text

    assert shim.main is cli.main and shim.DASHES is text.DASHES

def test_nothing_is_written_to_a_tracked_or_in_repository_place(tmp_path, capsys):
    candidate = write_candidate(tmp_path, fx.bscs())
    inside = REPO / "docs" / "decisions" / "review-output"
    assert run("sheet", "--candidate", candidate, "--pdf-sha256", HASH, "--review-dir", inside) == 2
    assert "inside the repository and not git-ignored" in capsys.readouterr().err and not inside.exists()
    with pytest.raises(FixerError):
        assert_outside_git(REPO / "README.md")   # a tracked file's own place


def test_materialise_never_overwrites_the_raw_candidate(tmp_path, capsys):
    candidate = write_candidate(tmp_path, fx.bscs())
    before = candidate.read_bytes()
    assert run("materialise", "--candidate", candidate, "--pdf-sha256", HASH, "--out", candidate) == 2
    assert "raw candidate" in capsys.readouterr().err and candidate.read_bytes() == before


def test_apply_without_any_reviewer_name_is_refused_and_writes_nothing(tmp_path, monkeypatch, capsys):
    candidate = write_candidate(tmp_path, fx.bscs())
    run("sheet", "--candidate", candidate, "--pdf-sha256", HASH)
    sheet = sheet_path(candidate)
    sheet.write_text(set_line(sheet.read_text(encoding="utf-8"), "S1", "confirm", "yes"), encoding="utf-8")

    class Nothing:
        stdout = ""

    monkeypatch.setattr(fixer_cli.subprocess, "run", lambda *a, **k: Nothing())
    capsys.readouterr()
    assert run("apply", "--candidate", candidate, "--pdf-sha256", HASH) == 2
    assert "no reviewer" in capsys.readouterr().err and not (sheet.parent / "decision_ledger.jsonl").exists()


def test_a_missing_sheet_is_an_io_error_not_a_traceback(tmp_path, capsys):
    candidate = write_candidate(tmp_path, fx.bscs())
    assert run("apply", "--candidate", candidate, "--pdf-sha256", HASH, "--reviewer", "N") == 2
    assert "cannot read the review sheet" in capsys.readouterr().err