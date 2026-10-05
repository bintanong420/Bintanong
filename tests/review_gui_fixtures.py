"""Fixtures for the review GUI tests, built on tests/fixer_fixtures.py.

mixed(): one clean section (S1), one review section (S2, a prerequisite in the same term) and one broken section (S3,
a printed total that the courses do not add up to, plus an unclaimed printed code), with a title that holds a double
quote and a non-ASCII letter.
"""

from __future__ import annotations

from datetime import datetime, timezone

from backend.bintanong_tools.prospectus_extractor.sheet import row_entries
from backend.bintanong_tools.prospectus_extractor.verify import verify_candidate

import fixer_fixtures as fx

HASH = "c" * 64
NOW = datetime(2026, 10, 5, 9, 0, tzinfo=timezone.utc)
Y21 = ("2nd Year", "1st Semester")
ODD_TITLE = 'Ethics "Applied" of Pálawan'


def mixed():
    payload = fx.bscs()
    payload["courses"][2]["prerequisites"] = ["CC 3/L"]   # S2: CS 2 needs a course of its own term -> prereq_order (warn)
    eth = fx.course("GE-ET", ODD_TITLE, "3", Y21, 6, 0, [
        fx.cell("t0-c30", "GE-ET", 6, 0, 1, [64.0, 225.0, 84.0, 235.0], page=2),
        fx.cell("t0-c31", ODD_TITLE, 6, 1, 2, [100.0, 225.0, 200.0, 235.0], page=2),
        fx.cell("t0-c32", "3", 6, 2, 3, [246.0, 225.0, 260.0, 235.0], page=2)], page=2)
    payload["courses"].append(eth)
    payload["audit"]["term_unit_audit"].append({"year_level": Y21[0], "semester": Y21[1], "declared_units": 5,
                                                "computed_units": 3, "course_count": 1, "matches": False})
    payload["audit"]["unclaimed_course_candidates"] = [{
        "code": "CS 9", "normalized_code": "CS9", "cell_ids": ["t0-c40"], "table_index": 0, "page": 3,
        "bbox": [64.0, 300.0, 84.0, 310.0], "confidence": "high"}]
    return payload


def verified(payload):
    return verify_candidate(payload, None)


def row_of(verification, rid):
    for section in verification.sections:
        for row in section.rows:
            if row.rid == rid:
                return section, row
    raise AssertionError(rid)


def decision(payload, verification, rid, verb="ok", *, reason="", edits=None, letters=(), pdf_sha256=HASH, via="gui"):
    """Ledger entries for one decision, built by the shared builder (so tests never hand-build an entry)."""
    section, row = row_of(verification, rid)
    entries: list = []
    errors = row_entries(entries, row, section, payload, verb, list(letters), reason, edits or {}, via, "Nestor", pdf_sha256, NOW)
    assert errors == [], errors
    return entries
