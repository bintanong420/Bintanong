"""Phase C: audit, content review, and source verification stay separate states.

A machine audit of ok or warn (legacy label VERIFIED) must never be enough to
produce executable eligibility.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from backend.bintanong_tools.prospectus_extractor.pipeline import build_payload
from backend.bintanong_tools.prospectus_extractor.prolog import generate_prolog_knowledge
from backend.bintanong_tools.prospectus_extractor.selftest import (
    CS_HEADER, _cs_row, _cs_semester_row, _merged, fixture_document,
)
from backend.bintanong_tools.prospectus_extractor.prerequisites import (
    EXECUTABLE_PREREQUISITE_STATES,
    PREREQUISITE_STATES,
    annotate_prerequisite_states,
    classify_prerequisite_state,
)


def course(raw, prereqs=(), unresolved=(), standing=(), cells=("t0-c1",)):
    return {
        "course_code": "X 1",
        "prerequisites_raw": raw,
        "prerequisites": list(prereqs),
        "prerequisites_unresolved": list(unresolved),
        "standing_requirements": list(standing),
        "provenance": {"source_cell_ids": list(cells)},
    }


STATE_CASES = [
    ("blank cell", course(""), "blank_unreviewed"),
    ("printed none", course("none"), "stated_none"),
    ("printed dash", course("-"), "stated_none"),
    ("one code", course("CS 1", ["CS 1"]), "resolved"),
    ("two codes", course("CS 1, CS 2", ["CS 1", "CS 2"]), "resolved"),
    ("standing only", course("Dean consent", standing=["Dean consent."]), "standing_condition"),
    ("code plus standing",
     course("CS 1, 70% of the units", ["CS 1"], standing=["70% of the units."]), "standing_condition"),
    ("unresolved token", course("CS 9", unresolved=["CS 9"]), "unresolved_reference"),
    ("or with leftover token", course("CS 1 or CS 2", ["CS 1", "CS 2"], unresolved=["or"]),
     "alternative_or_exception"),
    ("or that resolved fully", course("CS 1 or CS 2", ["CS 1", "CS 2"]), "alternative_or_exception"),
    ("exception wording",
     course("CS 1 except for transferees", ["CS 1"], unresolved=["except for transferees"]),
     "alternative_or_exception"),
    ("text present, nothing recognised", course("Units"), "unreadable"),
]


@pytest.mark.parametrize(("label", "record", "expected"), STATE_CASES, ids=[c[0] for c in STATE_CASES])
def test_prerequisite_state_of_one_course(label, record, expected):
    assert classify_prerequisite_state(record) == expected
    assert expected in PREREQUISITE_STATES


def test_audit_flagged_cell_is_unreadable_even_when_it_looks_resolved():
    record = course("CS 1", ["CS 1"], cells=("t0-c5", "t0-c6"))
    assert classify_prerequisite_state(record) == "resolved"
    assert classify_prerequisite_state(record, frozenset({"t0-c6"})) == "unreadable"


def test_only_complete_states_are_executable():
    assert EXECUTABLE_PREREQUISITE_STATES == {"resolved", "stated_none", "reviewed_empty"}
    # The extractor can not tell a blank from a missing cell, so it never emits reviewed_empty.
    emitted = {classify_prerequisite_state(record) for _label, record, _state in STATE_CASES}
    assert "reviewed_empty" not in emitted
    assert "blank_unreviewed" not in EXECUTABLE_PREREQUISITE_STATES


def test_annotate_marks_every_course_and_uses_only_prerequisite_anomalies():
    courses = [course("CS 1", ["CS 1"], cells=("t0-c5",)), course("", cells=("t0-c9",))]
    anomalies = [
        {"type": "ambiguous_adjacent_prerequisite_fragment", "source_cell_ids": ["t0-c5"]},
        {"type": "unclaimed_course_candidate", "source_cell_ids": ["t0-c9"]},
    ]
    annotate_prerequisite_states(courses, anomalies)
    assert [c["prerequisite_state"] for c in courses] == ["unreadable", "blank_unreviewed"]


def payload_for(rows, **kwargs):
    grid = [CS_HEADER, _merged("FIRST YEAR", 8), _cs_semester_row(), *rows]
    document = fixture_document(grid, [("title", "BACHELOR OF SCIENCE IN COMPUTER SCIENCE PROGRAM")])
    return build_payload(document, Path("local/x.pdf"), semantic_doc_path=None, **kwargs)


# CS 1 has a blank cell; CS 2 requires exactly CS 1, so its rule is complete.
CONTROL = _cs_row(("CS 1", "Discrete Structures", "3", ""), ("CS 2", "Discrete Structures 2", "3", "CS 1"))


def one_case(cell):
    return _cs_row(("CC 1", "Intro to Computing", "3", cell))


@pytest.mark.parametrize(
    ("cell", "state"),
    [
        ("Units", "unreadable"),
        ("CS 9", "unresolved_reference"),
        ("Dean consent", "standing_condition"),
        ("CS 1 or CS 2", "alternative_or_exception"),
        ("CS 1 except transferees", "alternative_or_exception"),
    ],
)
def test_incomplete_prerequisite_rule_is_not_executable_even_when_audit_says_verified(cell, state):
    payload = payload_for([CONTROL, one_case(cell)])
    # Precondition: the legacy label says go. Without it this test proves nothing.
    assert payload["audit"]["status"] != "error"
    assert payload["audit"]["promotion_status"] == "VERIFIED"

    by_code = {c["course_code"]: c for c in payload["courses"]}
    assert by_code["CC 1"]["prerequisite_state"] == state
    clauses = payload["prolog"]["clauses"]
    assert "rule_complete('CC 1')." not in clauses
    assert "CC 1" not in payload["prolog"]["relations"]["rule_complete"]
    # Control: a fully understood rule still counts, so the exclusion is not blanket.
    assert by_code["CS 2"]["prerequisite_state"] == "resolved"
    assert "rule_complete('CS 2')." in clauses
    # A blank cell is unreviewed, not an empty rule.
    assert by_code["CS 1"]["prerequisite_state"] == "blank_unreviewed"
    assert "rule_complete('CS 1')." not in clauses


def test_courses_without_a_state_are_never_complete():
    record = {
        "course_code": "X 1", "course_title": "T", "units": {"total": 3, "lecture": 3, "lab": 0},
        "year_level": "1st Year", "semester": "1st Semester", "category": "Core / Major",
        "prerequisites": [], "standing_requirements": [],
    }
    knowledge = generate_prolog_knowledge({}, [record], [], [])
    assert knowledge["relations"]["rule_complete"] == []
    assert knowledge["relations"]["prerequisite_states"] == [{"course": "X 1", "state": "unclassified"}]


@pytest.mark.skipif(shutil.which("swipl") is None, reason="SWI-Prolog is not installed")
def test_next_eligible_only_offers_courses_with_complete_rules(tmp_path):
    payload = payload_for([
        CONTROL,
        _cs_row(("CC 1", "Intro to Computing", "3", "CS 1 or CS 2"), ("CC 2", "Other", "3", "CS 1")),
        _cs_row(("CC 3", "Third", "3", "Dean consent")),
    ])
    kb = tmp_path / "kb.pl"
    kb.write_text("\n".join(payload["prolog"]["clauses"]) + "\n", encoding="utf-8", newline="\n")

    def next_eligible(passed):
        driver = tmp_path / "driver.pl"
        driver.write_text(
            f":- consult('{kb.as_posix()}').\n"
            f"main :- findall(C, next_eligible({passed}, C), L), format(\"~q~n\", [L]).\n"
            ":- initialization(main, main).\n",
            encoding="utf-8", newline="\n",
        )
        done = subprocess.run(["swipl", "-q", str(driver)], capture_output=True, text=True, encoding="utf-8")
        assert done.returncode == 0, done.stderr
        return done.stdout.strip()

    assert next_eligible("[]") == "[]"  # CS 1 is blank (unreviewed); CC 2 needs CS 1
    # CC 1 (OR) and CC 3 (standing) are never offered; CC 2 (resolved, CS 1 passed) is.
    assert next_eligible("['CS 1','CS 2']") == "['CC 2']"


def test_blocked_audit_drops_candidate_prolog_and_rag():
    payload = payload_for([CONTROL, _cs_row(("CS 1", "Duplicate code", "3", ""))])
    assert payload["audit"]["status"] == "error"
    assert payload["prolog"]["status"] == "blocked"
    assert payload["prolog"]["clauses"] == []
    assert payload["prolog"]["relations"] == {
        "courses": [], "prerequisites": [], "standing_requirements": [], "elective_tracks": [],
        "prerequisite_states": [], "rule_complete": [],
    }
    assert payload["rag"] == {"semantic_chunks": [], "hierarchical_chunks": []}
    assert "blocked_candidates" not in payload
