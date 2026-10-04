"""Regression tests for the Codex read-only review of Phase B2 (12 confirmed defects)."""

import copy
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pytest

from backend.bintanong_tools.prospectus_extractor.course_checks import PdfPage
from backend.bintanong_tools.prospectus_extractor.fixes import propose_fixes
from backend.bintanong_tools.prospectus_extractor.verify import own_role_cells, verify_candidate

import fixer_fixtures as fx
from fixer_fixtures import by_code

HASH = "a" * 64


def set_cell_text(payload, cell_id, text):
    for course in payload["courses"]:
        for c in course["provenance"]["source_cells"]:
            if c["cell_id"] == cell_id:
                c["text"] = text


def roles(course, payload):
    audit = payload["audit"]
    ids = {i for s in audit["curriculum_sections"] for i in s["evidence_cells"]}
    return own_role_cells(course, audit["table_layout"], ids)


BANNERS = {"FIRST", "SEMESTER", "YEAR"}


# --- commit 1: proposals come from the source and never strip a title word

def test_item1_a_title_that_is_only_banner_plus_one_word_in_its_own_cell_is_not_stripped():
    payload = copy.deepcopy(fx.bscs())
    course = payload["courses"][1]
    course["course_title"] = "FIRST SEMESTER PRACTICUM"
    set_cell_text(payload, "t0-c18", "FIRST SEMESTER PRACTICUM")
    pdf = "CC 1/L FIRST SEMESTER PRACTICUM 2/1"
    assert propose_fixes(course, roles(course, payload), page_text=pdf, banners=BANNERS) == []
    row = by_code(payload, verify_candidate(payload))["CC 1/L"]
    assert row.fixes == [] and row.worst() is not None       # still flagged, section not clean


def test_item1_a_strip_is_proposed_when_the_pdf_prints_the_remainder_without_the_banner():
    payload = copy.deepcopy(fx.bscs())
    course = payload["courses"][0]       # CS 1: only its title cell t0-c9 carries the banner
    course["course_title"] = "FIRST SEMESTER Discrete Structures 1"
    page = "FIRST SEMESTER CS 1 Discrete Structures 1 3 CC 1/L Introduction to Computing 2/1"
    fixes = propose_fixes(course, roles(course, payload), page_text=page, banners=BANNERS)
    assert [f.new for f in fixes] == ["Discrete Structures 1"]
    assert propose_fixes(course, roles(course, payload), banners=BANNERS) == []   # nothing to confirm it with


def test_item2_a_remainder_that_is_in_no_source_cell_or_pdf_text_is_not_proposed():
    payload = copy.deepcopy(fx.bscs())
    course = payload["courses"][1]
    course["course_title"] = "FIRST SEMESTER Galactic Mechanics"      # its cell says "Introduction to Computing"
    page = "CC 1/L Introduction to Computing 2/1"
    assert propose_fixes(course, roles(course, payload), page_text=page, banners=BANNERS) == []
    assert by_code(payload, verify_candidate(payload))["CC 1/L"].fixes == []


# --- item 12: glyphs of one printed code sit on one text line

def make_two_line_page():
    # "Mktg" at the end of a wrapped line, "2001" at the start of the next one: horizontally adjacent
    # (the second word starts 3 pt after the first ends) but on different lines.
    chars = []
    for i, ch in enumerate("Mktg"):
        chars.append((ch, 400.0 + i * 5, 700.0, 405.0 + i * 5, 710.0))
    for i, ch in enumerate("2001"):
        chars.append((ch, 423.0 + i * 5, 686.0, 428.0 + i * 5, 696.0))
    return PdfPage("Mktg 2001", chars, 800.0)


def test_item12_glyphs_on_different_lines_are_not_one_code():
    from backend.bintanong_tools.prospectus_extractor.placement import is_split_across_cells, locate_in_page
    page = make_two_line_page()
    assert locate_in_page(page, "Mktg 2001") is None
    assert is_split_across_cells(page, "Mktg 2001")


# --- commit 2: sheet controls and bulk confirm respect section flags

from backend.bintanong_tools.prospectus_extractor.sheet import (
    build_entries, candidate_sha256, check_against, parse_decision, parse_sheet, render_sheet,
)
from sheet_helpers import edit_row, set_line


def rendered(payload, v):
    return render_sheet(payload, v, {"pdf_sha256": HASH, "candidate_sha256": candidate_sha256(payload)})


def test_item3_confirm_yes_on_a_section_with_a_section_level_flag_is_refused_naming_the_flag():
    payload = copy.deepcopy(fx.bscs())
    payload["audit"]["term_unit_audit"][0]["declared_units"] = 99        # S1: printed 99, extracted 5
    v = verify_candidate(payload)
    assert [r.worst() for r in v.sections[0].rows] == [None, None] and v.sections[0].flags
    text = set_line(rendered(payload, v), "S1", "confirm", "yes")
    entries, errors = build_entries(parse_sheet(text), payload, v, reviewer="N", pdf_sha256=HASH)
    assert entries == []
    assert any("S1" in e and "unit_total" in e and "(line " in e for e in errors), errors


@pytest.mark.parametrize("key", ["confirm", "accept", "reason"])
def test_item4_a_repeated_control_line_in_one_section_is_rejected_with_its_line_number(key):
    payload = copy.deepcopy(fx.bscs())
    v = verify_candidate(payload)
    base = rendered(payload, v)
    lines = base.splitlines()
    at_line = next(i for i, l in enumerate(lines) if l.startswith(f"{key}:"))
    lines.insert(at_line + 1, f"{key}: no")
    text = "\n".join(lines) + "\n"
    errors = check_against(parse_sheet(text), parse_sheet(base))
    assert any(f"line {at_line + 2}" in e and key in e and "twice" in e for e in errors), errors


def test_item5_a_decision_that_is_only_a_reason_is_a_validation_error_not_a_crash():
    assert parse_decision(": because")[3] is not None
    payload = copy.deepcopy(fx.bscs())
    v = verify_candidate(payload)
    text = edit_row(rendered(payload, v), "S1-01", decision=": because")
    entries, errors = build_entries(parse_sheet(text), payload, v, reviewer="N", pdf_sha256=HASH)
    assert entries == [] and any("S1-01" in e and "(line " in e for e in errors)


# --- commit 3: ledger and CLI refuse unattributed, malformed or mismatched input

from backend.bintanong_tools.prospectus_extractor import fixer_cli
from backend.bintanong_tools.prospectus_extractor.fixer_cli import (
    FixerError, assert_outside_git, default_review_dir, fixer_main, resolve_identity,
)
from backend.bintanong_tools.prospectus_extractor.ledger import (
    append_entries, content_review_state, course_locator, course_snapshot, entry_problem, make_entry, materialise,
    read_entries,
)

NOW = datetime(2026, 10, 4, 9, 30, tzinfo=timezone.utc)


def good_entry(course, **changes):
    snapshot = course_snapshot(course)
    entry = make_entry(reviewer="N", reason="r", pdf_sha256=HASH, locator=course_locator(course), field="course_title",
                       disposition="corrected", old_value=snapshot["course_title"], new_value="Discrete Structures One",
                       section="s", now=NOW)
    return {k: v for k, v in {**entry, **changes}.items() if v is not ...}


def write_lines(path, *items):
    path.write_text("".join((i if isinstance(i, str) else json.dumps(i, sort_keys=True)) + "\n" for i in items), encoding="utf-8")


def test_item6_a_non_json_line_is_skipped_and_reported_with_its_line_number(tmp_path):
    payload = fx.bscs()
    course = payload["courses"][0]
    good = good_entry(course)
    path = tmp_path / "ledger.jsonl"
    write_lines(path, good, "{broken", {"not": "an entry"}, good)
    entries = read_entries(path)                       # no LedgerError
    corrected, report = materialise(payload, entries, HASH)
    reasons = sorted(s["reason"] for s in report["skipped"])
    assert len(reasons) == 2 and "line 2" in reasons[0] + reasons[1] and "line 3" in reasons[0] + reasons[1]
    assert report["applied"] == 1 and content_review_state(payload, entries, HASH)["invalid_entries"] == 2
    assert append_entries(path, [good_entry(payload["courses"][1])]) == (1, 0)


def test_item6_status_reports_the_bad_line_and_still_exits_0(tmp_path, capsys):
    payload = fx.bscs()
    candidate = tmp_path / "x_prospectus.json"
    candidate.write_text(json.dumps(payload), encoding="utf-8")
    ledger = default_review_dir(candidate) / "decision_ledger.jsonl"
    ledger.parent.mkdir(parents=True)
    ledger.write_text("{broken\n", encoding="utf-8")
    assert fixer_main(["status", "--candidate", str(candidate), "--pdf-sha256", HASH]) == 0
    assert "line 1" in capsys.readouterr().err


@pytest.mark.parametrize("cell_ids", [[["bad"]], "t0-c1", [1], {"a": 1}])
def test_item7_a_locator_with_the_wrong_shape_is_invalid_not_a_crash(tmp_path, cell_ids):
    payload = fx.bscs()
    course = payload["courses"][0]
    bad = good_entry(course, locator={"kind": "course", "cell_ids": cell_ids})
    assert entry_problem(bad)
    path = tmp_path / "ledger.jsonl"
    write_lines(path, bad)
    entries = read_entries(path)
    _corrected, report = materialise(payload, entries, HASH)
    assert report["applied"] == 0 and report["skipped"][0]["reason"].startswith("invalid_entry")
    assert content_review_state(payload, entries, HASH)["invalid_entries"] == 1
    assert append_entries(path, [good_entry(payload["courses"][1])]) == (1, 0)


@pytest.mark.parametrize("missing", ["reviewer", "recorded_at", "disposition", "pdf_sha256"])
def test_item8_an_entry_without_reviewer_time_disposition_or_pdf_is_never_applied(tmp_path, missing):
    payload = fx.bscs()
    path = tmp_path / "ledger.jsonl"
    write_lines(path, good_entry(payload["courses"][0], **{missing: ...}))
    _corrected, report = materialise(payload, read_entries(path), HASH)
    assert report["applied"] == 0 and len(report["skipped"]) == 1
    assert good_entry(payload["courses"][0], reviewer="  ") and entry_problem(good_entry(payload["courses"][0], reviewer="  "))


def test_item8_the_untouched_entry_is_still_applied(tmp_path):
    payload = fx.bscs()
    path = tmp_path / "ledger.jsonl"
    write_lines(path, good_entry(payload["courses"][0]))
    assert materialise(payload, read_entries(path), HASH)[1]["applied"] == 1


def test_item9_a_declared_hash_that_differs_from_the_candidates_recorded_one_is_refused(capsys, tmp_path):
    payload = {**fx.bscs(), "run_identity": {"file_sha256": HASH}}
    with pytest.raises(FixerError, match="recorded"):
        resolve_identity(payload, pdf_sha256="b" * 64)
    assert resolve_identity(payload, pdf_sha256=HASH)["pdf_sha256"] == HASH
    assert resolve_identity(payload)["pdf_sha256"] == HASH
    candidate = tmp_path / "x_prospectus.json"
    candidate.write_text(json.dumps(payload), encoding="utf-8")
    assert fixer_main(["sheet", "--candidate", str(candidate), "--pdf-sha256", "b" * 64]) == 2
    assert "recorded" in capsys.readouterr().err
    pdf = tmp_path / "a.pdf"
    pdf.write_bytes(b"%PDF fake")
    with pytest.raises(FixerError, match="recorded"):
        resolve_identity(payload, pdf=pdf)


def _git(repo, *args):
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


@pytest.fixture
def temp_repo(tmp_path, monkeypatch):
    repo = (tmp_path / "repo").resolve()
    repo.mkdir()
    _git(repo, "init", "-q")
    (repo / ".gitignore").write_text("review/\n", encoding="utf-8")
    (repo / "review").mkdir()
    (repo / "review" / "corrected_candidate.json").write_text("{}\n", encoding="utf-8")
    _git(repo, "add", "-f", "review/corrected_candidate.json")
    monkeypatch.setattr(fixer_cli, "REPO", repo)
    return repo


def test_item10_a_tracked_file_inside_an_ignored_folder_is_not_overwritten(temp_repo, tmp_path):
    assert_outside_git(temp_repo / "review" / "new_file.json")                 # a new file there is fine
    with pytest.raises(FixerError, match="not git-ignored"):
        assert_outside_git(temp_repo / "review" / "corrected_candidate.json")  # the tracked file itself
    candidate = tmp_path / "c" / "x_prospectus.json"
    candidate.parent.mkdir()
    candidate.write_text(json.dumps(fx.bscs()), encoding="utf-8")
    out = temp_repo / "review" / "corrected_candidate.json"
    assert fixer_main(["materialise", "--candidate", str(candidate), "--pdf-sha256", HASH, "--out", str(out)]) == 2
    assert out.read_text(encoding="utf-8") == "{}\n"


def test_item10_an_output_name_that_is_a_symlink_to_a_tracked_file_is_refused(temp_repo, tmp_path):
    link = tmp_path / "outside" / "corrected.json"
    link.parent.mkdir()
    try:
        link.symlink_to(temp_repo / "review" / "corrected_candidate.json")
    except OSError:
        pytest.skip("symlinks need privileges on this machine")
    candidate = tmp_path / "c" / "x_prospectus.json"
    candidate.parent.mkdir()
    candidate.write_text(json.dumps(fx.bscs()), encoding="utf-8")
    tracked = temp_repo / "review" / "corrected_candidate.json"
    assert fixer_main(["materialise", "--candidate", str(candidate), "--pdf-sha256", HASH, "--out", str(link)]) == 2
    assert tracked.read_text(encoding="utf-8") == "{}\n"


def test_item11_appending_after_a_last_line_without_a_newline_keeps_one_entry_per_line(tmp_path):
    payload = fx.bscs()
    path = tmp_path / "ledger.jsonl"
    path.write_text(json.dumps(good_entry(payload["courses"][0]), sort_keys=True), encoding="utf-8", newline="")  # no "\n"
    assert append_entries(path, [good_entry(payload["courses"][1])]) == (1, 0)
    text = path.read_text(encoding="utf-8")
    assert "}{" not in text and len(text.splitlines()) == 2 and len(read_entries(path)) == 2


# --- re-review round 2: incomplete entries, missing reason, non-UTF-8 bytes

@pytest.mark.parametrize("missing", ["entry_id", "old_value", "reason"])
def test_r2_item2_3_an_entry_missing_entry_id_old_value_or_reason_is_invalid_not_a_crash(tmp_path, missing):
    payload = fx.bscs()
    path = tmp_path / "ledger.jsonl"
    write_lines(path, good_entry(payload["courses"][0], **{missing: ...}))
    entries = read_entries(path)
    assert entry_problem(entries[0]) and missing in entry_problem(entries[0])
    _c, report = materialise(payload, entries, "b" * 64)          # another PDF: used to KeyError on entry_id
    assert report["applied"] == 0 and report["skipped"][0]["reason"].startswith("invalid_entry")
    assert materialise(payload, entries, HASH)[1]["applied"] == 0
    assert content_review_state(payload, entries, HASH)["invalid_entries"] == 1


def test_r2_item3_a_blank_reason_is_invalid_and_make_entry_refuses_it():
    payload = fx.bscs()
    assert entry_problem(good_entry(payload["courses"][0], reason="  "))
    with pytest.raises(Exception, match="reason"):
        make_entry(reviewer="N", reason=" ", pdf_sha256=HASH, locator=course_locator(payload["courses"][0]), field="row",
                   disposition="accepted", old_value={}, new_value={}, section="s")


def test_r2_item4_non_utf8_bytes_become_unreadable_lines_with_their_number(tmp_path):
    payload = fx.bscs()
    good = json.dumps(good_entry(payload["courses"][0]), sort_keys=True).encode("utf-8")
    path = tmp_path / "ledger.jsonl"
    path.write_bytes(b"\xef\xbb\xbf" + good + b"\r\n\xff\xfe bad\n" + good.replace(b"Discrete", b"Discr\xe9te") + b"\n" + good + b"\n")
    entries = read_entries(path)                         # no UnicodeDecodeError, BOM and CRLF tolerated
    bad = [e["_unreadable"] for e in entries if "_unreadable" in e]
    assert len(entries) == 4 and bad[0].startswith("line 2") and len(bad) == 2 and bad[1].startswith("line 3")
    assert materialise(payload, entries, HASH)[1]["applied"] == 1
