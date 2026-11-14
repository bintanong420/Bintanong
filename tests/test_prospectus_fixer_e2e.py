"""Three candidates of different health through sheet, apply, status and materialise."""

import json

from backend.bintanong_tools.prospectus_extractor import fixer_cli
from backend.bintanong_tools.prospectus_extractor.course_checks import PdfPage
from backend.bintanong_tools.prospectus_extractor.fixer_cli import default_review_dir, fixer_main as main

import fixer_fixtures as fx
from sheet_helpers import edit_row, set_line


def step(capsys, *argv):
    code = main([str(a) for a in argv])
    return code, capsys.readouterr()


def state(capsys, candidate, *identity):
    code, out = step(capsys, "status", "--candidate", candidate, *identity)
    assert code == 0
    return json.loads(out.out)


def review(tmp_path, name, payload, pdf):
    candidate = tmp_path / name / "candidate.json"
    candidate.parent.mkdir()
    candidate.write_text(json.dumps(payload), encoding="utf-8")
    return candidate, default_review_dir(candidate)


def test_clean_medium_and_broken_candidates(tmp_path, monkeypatch, capsys):
    pdf = tmp_path / "x.pdf"
    pdf.write_bytes(b"%PDF fake")

    # clean: confirm both sections in two lines, the whole review is one apply
    candidate, folder = review(tmp_path, "bscs", fx.bscs(), pdf)
    declared = ("--pdf-sha256", "d" * 64)   # no PDF at hand: the text checks are skipped, the rest runs
    assert step(capsys, "sheet", "--candidate", candidate, *declared)[0] == 0
    sheet = folder / "review_sheet.md"
    text = sheet.read_text(encoding="utf-8")
    assert "- prospectus health: clean (2 clean, 0 review, 0 broken)" in text
    sheet.write_text(set_line(set_line(text, "S1", "confirm", "yes"), "S2", "confirm", "yes"), encoding="utf-8")
    assert step(capsys, "apply", "--candidate", candidate, *declared, "--reviewer", "Nestor")[0] == 0
    assert state(capsys, candidate, *declared)["state"] == "reviewed"

    # medium: glued titles get proposals; one class accept per section, then confirm
    monkeypatch.setattr(fixer_cli, "load_pdf_pages", lambda path: {1: PdfPage(fx.ARCH_PAGE_TEXT)})
    candidate, folder = review(tmp_path, "arch", fx.architecture(), pdf)
    assert step(capsys, "sheet", "--candidate", candidate, "--pdf", pdf)[0] == 0
    sheet = folder / "review_sheet.md"
    text = sheet.read_text(encoding="utf-8")
    assert "- prospectus health: mixed (0 clean, 2 review, 1 broken)" in text   # the broken one is SU: printed codes in the PDF no course claims
    for sid in ("S1", "S2"):
        text = set_line(set_line(set_line(text, sid, "accept", "title_from_pdf"), sid, "reason", "titles checked on PDF page 1"), sid, "confirm", "yes")
    sheet.write_text(text, encoding="utf-8")
    assert step(capsys, "apply", "--candidate", candidate, "--pdf", pdf, "--reviewer", "Nestor")[0] == 0
    assert state(capsys, candidate, "--pdf", pdf)["state"] == "reviewed"
    assert step(capsys, "materialise", "--candidate", candidate, "--pdf", pdf)[0] == 0
    corrected = json.loads((folder / "corrected_candidate.json").read_text(encoding="utf-8"))
    titles = {c["course_code"]: c["course_title"] for c in corrected["courses"]}
    assert titles["GE-PC"] == "Purposive Communication" and titles["TOA-2"] == "Theory of Architecture 2"
    assert titles["VT-2/L"] == "Architectural Visual Communications 4-Visual Techniques 2"
    assert corrected["review"]["applied_entry_ids"] and corrected["review"]["skipped"] == []
    original = json.loads(candidate.read_text(encoding="utf-8"))
    assert {c["course_code"]: c["course_title"] for c in original["courses"]}["GE-PC"] == "Techniques 1 Purposive Communication"

    # broken: the sheet lists what could not be read; the reviewer can only mark it unresolved
    candidate, folder = review(tmp_path, "innov", fx.innovation(), pdf)
    assert step(capsys, "sheet", "--candidate", candidate, "--pdf-sha256", "e" * 64)[0] == 0
    sheet = folder / "review_sheet.md"
    text = sheet.read_text(encoding="utf-8")
    assert "- prospectus health: broken" in text and "## SU - Unplaced printed codes" in text and "## S1 - 1st Year - 1st Semester" in text
    for rid in ("SU-U1", "SU-U2", "SU-U3"):
        text = edit_row(text, rid, decision="unresolved: printed on the PDF above the FOURTH YEAR banner, not parsed")
    sheet.write_text(set_line(set_line(text, "S2", "confirm", "yes"), "S3", "confirm", "yes"), encoding="utf-8")
    assert step(capsys, "apply", "--candidate", candidate, "--pdf-sha256", "e" * 64, "--reviewer", "Nestor")[0] == 0
    code, out = step(capsys, "status", "--candidate", candidate, "--pdf-sha256", "e" * 64)
    result = json.loads(out.out)
    assert (result["state"], result["decided"], result["unresolved"], result["unclaimed_undecided"]) == ("partially_reviewed", 2, 3, 0)