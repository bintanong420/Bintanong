"""Phase C: audit, content review, and source verification stay separate states.

A machine audit of ok or warn (legacy label VERIFIED) must never be enough to
produce executable eligibility.
"""

from __future__ import annotations

import pytest

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
