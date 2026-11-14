"""Sheet scenarios whose build_entries output is frozen in fixtures/sheet_entries_golden.json.

The golden file was written from the sheet code as it was before the decision builder became public
and gained unit and prerequisite edits. `python tests/sheet_golden_scenarios.py` rewrites it; only do
that when the sheet's output is meant to change.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path[:0] = [str(Path(__file__).parent), str(Path(__file__).parent.parent)]

import fixer_fixtures as fx  # noqa: E402
from sheet_helpers import edit_row, set_line  # noqa: E402

from backend.bintanong_tools.prospectus_extractor.course_checks import PdfPage  # noqa: E402
from backend.bintanong_tools.prospectus_extractor.sheet import (  # noqa: E402
    build_entries, candidate_sha256, parse_sheet, render_sheet,
)
from backend.bintanong_tools.prospectus_extractor.verify import verify_candidate  # noqa: E402

HASH = "a" * 64
NOW = datetime(2026, 10, 4, 9, 30, tzinfo=timezone.utc)
GOLDEN = Path(__file__).parent / "fixtures" / "sheet_entries_golden.json"

# (name, fixture, with pdf, [("row", rid, columns) | ("line", sid, key, value)])
SCENARIOS = [
    ("ok", "bscs", False, [("row", "S1-02", {"decision": "ok"})]),
    ("ok with reason", "bscs", False, [("row", "S1-02", {"decision": "ok: checked against the PDF"})]),
    ("unresolved", "bscs", False, [("row", "S1-01", {"decision": "unresolved: cannot read the scan"})]),
    ("unresolved without reason", "bscs", False, [("row", "S1-01", {"decision": "unresolved"})]),
    ("edit code", "bscs", False, [("row", "S1-02", {"decision": "edit: PDF shows another code", "new_code": "CC 1/X"})]),
    ("edit title", "bscs", False, [("row", "S1-02", {"decision": "edit: typo", "new_title": "Intro to Computing"})]),
    ("edit term", "bscs", False, [("row", "S1-02", {"decision": "edit: wrong term", "new_term": "2nd Year / 1st Semester"})]),
    ("edit term loosely typed", "bscs", False, [("row", "S1-02", {"decision": "edit: wrong term", "new_term": "2nd year first sem"})]),
    ("edit all three", "bscs", False, [("row", "S1-02", {"decision": "edit: all wrong", "new_code": "ZZ 9", "new_title": "Z", "new_term": "3rd Year / 2nd Semester"})]),
    ("edit unchanged", "bscs", False, [("row", "S1-02", {"decision": "edit: same", "new_code": "CC 1/L"})]),
    ("edit bad term", "bscs", False, [("row", "S1-02", {"decision": "edit: bad", "new_term": "someday"})]),
    ("edit without reason", "bscs", False, [("row", "S1-02", {"decision": "edit", "new_title": "X"})]),
    ("confirm section", "bscs", False, [("line", "S1", "confirm", "yes")]),
    ("confirm section with reason", "bscs", False, [("line", "S2", "confirm", "yes"), ("line", "S2", "reason", "read against the PDF")]),
    ("fix all proposals", "arch", True, [("row", "S1-02", {"decision": "fix"})]),
    ("fix letter with reason", "arch", True, [("row", "S1-04", {"decision": "fix a: matches the PDF"})]),
    ("fix and edit another row", "arch", True, [("row", "S1-02", {"decision": "fix"}), ("row", "S1-01", {"decision": "edit: typo", "new_title": "Fixed"})]),
    ("fix and edit the same field", "arch", True, [("row", "S1-02", {"decision": "fix", "new_title": "Other"})]),
    ("unclaimed ok and unresolved", "arch", True, [("row", "SU-U1", {"decision": "ok: footnote code"}), ("row", "SU-U2", {"decision": "unresolved: unclear"})]),
    ("unclaimed fix refused", "arch", True, [("row", "SU-U1", {"decision": "fix"})]),
    ("section accept class", "arch", True, [("line", "S2", "accept", "title_from_pdf"), ("line", "S2", "reason", "PDF agrees")]),
]


def run(fixture: str, pdf: bool, steps: list):
    payload = getattr(fx, {"bscs": "bscs", "arch": "architecture"}[fixture])()
    v = verify_candidate(payload, {1: PdfPage(fx.ARCH_PAGE_TEXT)} if pdf else None)
    text = render_sheet(payload, v, {"pdf_sha256": HASH, "candidate_sha256": candidate_sha256(payload)})
    for step in steps:
        text = edit_row(text, step[1], **step[2]) if step[0] == "row" else set_line(text, step[1], step[2], step[3])
    parsed = parse_sheet(text)
    assert parsed.errors == []
    entries, errors = build_entries(parsed, payload, v, reviewer="Nestor", pdf_sha256=HASH, now=NOW)
    return {"entries": entries, "errors": errors}


def capture() -> list:
    return [{"name": name, **run(fixture, pdf, steps)} for name, fixture, pdf, steps in SCENARIOS]


if __name__ == "__main__":
    GOLDEN.parent.mkdir(exist_ok=True)
    GOLDEN.write_text(json.dumps(capture(), indent=1, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print("wrote", GOLDEN)
