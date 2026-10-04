"""Phase C: audit, content review, and source verification stay separate states.

A machine audit of ok or warn (legacy label VERIFIED) must never be enough to
produce executable eligibility.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from backend.bintanong_tools.prospectus import ProvisionalSource
from backend.bintanong_tools.prospectus_extractor import pipeline
from backend.bintanong_tools.prospectus_extractor.common import SCHEMA_VERSION
from backend.bintanong_tools.prospectus_extractor.ledger import course_locator, make_entry
from backend.bintanong_tools.prospectus_extractor.metadata import resolve_metadata
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


SEMANTIC_MAP = {
    "CS": {
        "name": "College of Sciences",
        "programs": [
            {"program_name": "Bachelor of Science in Computer Science", "degree": "BS Computer Science"}
        ],
    }
}


def test_metadata_keeps_its_values_and_adds_observations_with_evidence():
    metadata, _warnings = resolve_metadata(
        Path("Tiniguiban - Main/CS/bscs.pdf"),
        doc_text="BACHELOR OF SCIENCE IN COMPUTER SCIENCE Effective SY 2025-2026",
        semantic_map=SEMANTIC_MAP,
    )
    assert metadata["campus"] == "Tiniguiban - Main"          # unchanged value
    assert metadata["college_code"] == "CS"
    assert metadata["program_name"] == "Bachelor of Science in Computer Science"
    assert metadata["effective_school_year"] == "2025-2026"

    seen = metadata["observations"]
    assert seen["campus"] == {
        "value": "Tiniguiban - Main", "basis": "extractor_default", "evidence": None, "status": "candidate",
    }
    assert seen["college_code"] == {
        "value": "CS", "basis": "path_segment", "evidence": "CS", "status": "candidate",
    }
    assert seen["program_name"]["basis"] == "semantic_map_match"
    assert seen["program_name"]["evidence"] == "Bachelor of Science in Computer Science"
    assert seen["effective_school_year"]["basis"] == "path_or_document_head"
    assert seen["effective_school_year"]["evidence"] == "Effective SY 2025-2026"
    assert all(item["status"] == "candidate" for item in seen.values())


def test_unknown_metadata_has_no_basis_and_the_same_warnings_as_before():
    metadata, warnings = resolve_metadata(Path("unknown/x.pdf"), doc_text="", semantic_map={})
    assert len(warnings) == 3
    seen = metadata["observations"]
    for name in ("college_code", "program_name", "effective_school_year"):
        assert seen[name] == {"value": None, "basis": None, "evidence": None, "status": "candidate"}
    assert seen["campus"]["basis"] == "extractor_default"  # still an assumption, now labelled as one


def test_mismatched_scope_with_an_approved_identity_blocks_eligibility():
    payload = payload_for([CONTROL], approved_scope={"campus": "Elsewhere Campus"})
    assert payload["audit"]["promotion_status"] == "VERIFIED"
    identity = payload["authority"]["identity_check"]
    assert identity["state"] == "mismatch"
    assert identity["mismatched_fields"] == ["campus"]
    assert "identity_mismatch" in payload["authority"]["blocked_by"]
    assert payload["authority"]["eligibility_executable"] is False
    # The parser's campus is still reported, but only as a labelled observation.
    assert payload["campus"] == "Tiniguiban - Main"
    assert payload["metadata"]["observations"]["campus"]["basis"] == "extractor_default"


def test_pending_identity_is_a_state_not_an_audit_error():
    with_scope = payload_for([CONTROL], approved_scope={"campus": "Tiniguiban - Main"})
    pending = payload_for([CONTROL])
    assert pending["authority"]["identity_check"] == {
        "state": "pending", "approved_scope": None, "mismatched_fields": [], "unverified_fields": [],
    }
    assert "identity_pending" in pending["authority"]["blocked_by"]
    assert pending["audit"]["errors"] == [] and pending["audit"]["errors"] == with_scope["audit"]["errors"]
    assert pending["audit"]["warnings"] == with_scope["audit"]["warnings"]
    assert pending["authority"]["eligibility_executable"] is False


def test_a_consistent_identity_alone_still_does_not_authorize():
    program = payload_for([CONTROL])["metadata"]["program_name"]
    payload = payload_for([CONTROL], approved_scope={"program_name": program})
    assert payload["authority"]["identity_check"]["state"] == "consistent"
    assert "identity_pending" not in payload["authority"]["blocked_by"]
    assert "content_review_pending" in payload["authority"]["blocked_by"]
    assert payload["authority"]["eligibility_executable"] is False


@pytest.mark.parametrize("cell", ["Units", "CS 9", "Dean consent", "CS 1 or CS 2", "CS 1 except transferees"])
def test_authority_block_blocks_eligibility_when_a_rule_is_incomplete(cell):
    payload = payload_for([CONTROL, one_case(cell)])
    assert payload["audit"]["promotion_status"] == "VERIFIED"
    assert payload["authority"]["eligibility_executable"] is False
    assert "prerequisite_rules_incomplete" in payload["authority"]["blocked_by"]
    assert payload["authority"]["courses_with_incomplete_prerequisite_rule"] >= 2


def test_three_states_are_separate_fields_and_promotion_status_is_unchanged():
    payload = payload_for([CONTROL])
    assert payload["schema_version"] == SCHEMA_VERSION == "palsu-prospectus-v3.1"
    assert payload["extraction_audit"] == payload["audit"]["status"] == "warn"
    assert payload["content_review"] == "pending"
    assert payload["source_verification"] == "pending"
    assert payload["audit"]["promotion_status"] == "VERIFIED"           # kept for compatibility
    assert payload["quality_report"]["promotion_status"] == "VERIFIED"
    assert "not approval" in payload["authority"]["note"]
    assert payload["authority"]["source_record"] is None


def test_source_record_is_carried_but_not_trusted_without_a_hash_check():
    source = ProvisionalSource("0" * 64, "local/x.pdf")
    payload = payload_for([CONTROL], source=source)
    assert payload["source_verification"] == "pending"
    assert payload["authority"]["source_record"] == {
        "pdf_sha256": "0" * 64, "source_locator": "local/x.pdf", "pdf_hash_check": "not_checked",
    }
    assert "pdf_hash_not_checked" in payload["authority"]["blocked_by"]
    assert payload["authority"]["eligibility_executable"] is False


def test_hash_mismatch_raises_before_any_output_is_touched(tmp_path):
    pdf = tmp_path / "prospectus.pdf"
    pdf.write_bytes(b"%PDF-1.4\nchanged bytes")
    out = tmp_path / "x_prospectus.json"
    out.write_text("previous accepted output", encoding="utf-8")
    source = ProvisionalSource(hashlib.sha256(b"%PDF-1.4\noriginal").hexdigest(), "local/prospectus.pdf")
    with pytest.raises(ValueError, match="hash mismatch"):
        pipeline.process_prospectus(pdf, output_path=out, semantic_doc_path=None, quiet=True, source=source)
    assert out.read_text(encoding="utf-8") == "previous accepted output"
    assert not (tmp_path / "x_essentials.json").exists()


def test_matching_hash_is_recorded_and_still_does_not_authorize(tmp_path, monkeypatch):
    pdf = tmp_path / "prospectus.pdf"
    pdf.write_bytes(b"%PDF-1.4\noriginal")
    source = ProvisionalSource(hashlib.sha256(b"%PDF-1.4\noriginal").hexdigest(), "local/prospectus.pdf")
    grid = [CS_HEADER, _merged("FIRST YEAR", 8), _cs_semester_row(), CONTROL]
    document = fixture_document(grid, [("title", "BACHELOR OF SCIENCE IN COMPUTER SCIENCE PROGRAM")])
    monkeypatch.setattr(pipeline, "load_document", lambda *args, **kwargs: (document, None))
    out = tmp_path / "x_prospectus.json"

    payload = pipeline.process_prospectus(pdf, output_path=out, semantic_doc_path=None, quiet=True, source=source)

    assert payload["authority"]["source_record"]["pdf_hash_check"] == "matched"
    assert "pdf_hash_not_checked" not in payload["authority"]["blocked_by"]
    assert payload["authority"]["eligibility_executable"] is False
    essentials = json.loads((tmp_path / "x_essentials.json").read_text(encoding="utf-8"))
    assert essentials["schema_version"] == "palsu-prospectus-essentials-v2"
    assert essentials["extraction_status"] == "VERIFIED"                # legacy field still present
    assert essentials["extraction_audit"] == "warn"
    assert essentials["content_review"] == "pending"
    assert essentials["source_verification"] == "pending"
    assert essentials["eligibility_executable"] is False
    assert all("prerequisite_state" in item for item in essentials["courses"])
    assert essentials["campus"] == "Tiniguiban - Main"                  # compact shape unchanged


# content_review comes from the Phase B2 decision ledger when one is passed with a source hash.
SOURCE_HASH = "0" * 64


def ledger_row_entries(payload, count=None):
    courses = payload["courses"][:count]
    return [
        make_entry(
            reviewer="reviewer-a", reason="matches the printed row", pdf_sha256=SOURCE_HASH,
            locator=course_locator(course), field="row", disposition="accepted",
            old_value=None, new_value=None, section="FIRST YEAR / 1st Semester",
        )
        for course in courses
    ]


def test_content_review_reads_the_ledger_and_never_authorizes_alone():
    source = ProvisionalSource(SOURCE_HASH, "local/x.pdf")
    base = payload_for([CONTROL], source=source)
    assert base["content_review"] == "pending"                     # no ledger passed

    empty = payload_for([CONTROL], source=source, review_entries=[])
    assert empty["content_review"] == "pending"

    partial = payload_for([CONTROL], source=source, review_entries=ledger_row_entries(base, 1))
    assert partial["content_review"] == "partially_reviewed"
    assert "content_review_incomplete" in partial["authority"]["blocked_by"]
    assert "content_review_pending" not in partial["authority"]["blocked_by"]

    full = payload_for([CONTROL], source=source, review_entries=ledger_row_entries(base))
    assert full["content_review"] == "reviewed"
    assert full["authority"]["content_review_detail"]["decided"] == 2
    assert "content_review_pending" not in full["authority"]["blocked_by"]
    assert "content_review_incomplete" not in full["authority"]["blocked_by"]
    # Reviewed content is still not a verified source, a checked hash, or a complete rule.
    assert full["audit"]["promotion_status"] == "VERIFIED"
    assert full["authority"]["eligibility_executable"] is False
    assert "source_verification_pending" in full["authority"]["blocked_by"]


def test_ledger_entries_for_another_pdf_do_not_count_as_review():
    source = ProvisionalSource("1" * 64, "local/x.pdf")
    base = payload_for([CONTROL], source=source)
    other_pdf = ledger_row_entries(base)  # recorded against SOURCE_HASH, not the source's hash
    payload = payload_for([CONTROL], source=source, review_entries=other_pdf)
    assert payload["content_review"] == "pending"
    assert payload["authority"]["content_review_detail"]["inapplicable_entries"] == 2


def test_ledger_without_a_source_hash_cannot_be_applied():
    base = payload_for([CONTROL])
    payload = payload_for([CONTROL], review_entries=ledger_row_entries(base))
    assert payload["content_review"] == "pending"


TIE_SCRIPT = """
import copy, json
from pathlib import Path
from backend.bintanong_tools.prospectus_extractor.audit import build_audit
from backend.bintanong_tools.prospectus_extractor.parse import parse_curriculum_evidence
from backend.bintanong_tools.prospectus_extractor.pipeline import build_payload
from backend.bintanong_tools.prospectus_extractor.selftest import (
    CS_HEADER, _cs_row, _cs_semester_row, _merged, fixture_document,
)

rows = [
    _cs_row(("CS 1", "A", "3", ""), ("CS 2", "B", "3", "")),
    _cs_row(("CS 3", "C", "3", ""), ("CS 4", "D", "3", "")),
]
grid = [CS_HEADER, _merged("FIRST YEAR", 8), _cs_semester_row(), *rows]
document = fixture_document(grid, [("title", "BACHELOR OF SCIENCE IN COMPUTER SCIENCE PROGRAM")])
payload = build_payload(document, Path("local/x.pdf"), semantic_doc_path=None)
courses = copy.deepcopy(payload["courses"])
for course, semester in zip(courses, ("Summer", "Mid-Year", "Summer", "Mid-Year")):
    course["year_level"], course["semester"] = "1st Year", semester
audit = build_audit(courses, parse_curriculum_evidence(document), payload["metadata"], [], [])
print(json.dumps(audit["terms_detected"]))
"""


def test_terms_with_the_same_index_are_listed_in_a_fixed_order():
    import os
    import sys

    repo = Path(__file__).resolve().parents[1]
    seen = set()
    for seed in range(16):
        env = dict(os.environ, PYTHONHASHSEED=str(seed), PYTHONPATH=str(repo))
        done = subprocess.run(
            [sys.executable, "-c", TIE_SCRIPT], capture_output=True, text=True, encoding="utf-8", cwd=repo, env=env,
        )
        assert done.returncode == 0, done.stderr[-1500:]
        seen.add(done.stdout.strip())
    # Summer and Mid-Year share an index; the tie breaks on year then semester text.
    assert seen == {'["1st Year Mid-Year", "1st Year Summer"]'}


# Review finding A: text the parser dropped silently must not leave a rule "resolved".
DROPPED_TEXT_CASES = [
    ("CS 1 with a grade of 85", "standing_condition"),
    ("CS 1, 18 units", "standing_condition"),
    ("CS 1 min grade 2.0", "standing_condition"),
    ("CS 1 Hours", "unreadable"),
    ("CS 1 Page 2", "unreadable"),
    ("CS 1 Note", "unreadable"),
    ("CS 1, Semester", "unreadable"),
    ("CS 1 | CS 2", "alternative_or_exception"),
    ("CS 1 / CS 2", "alternative_or_exception"),
]


@pytest.mark.parametrize(("cell", "state"), DROPPED_TEXT_CASES, ids=[c[0] for c in DROPPED_TEXT_CASES])
def test_text_the_parser_dropped_keeps_the_rule_out_of_eligible(cell, state):
    payload = payload_for([CONTROL, one_case(cell)])
    assert payload["audit"]["status"] != "error"
    by_code = {c["course_code"]: c for c in payload["courses"]}
    assert by_code["CC 1"]["prerequisite_state"] == state, by_code["CC 1"]["prerequisites_raw"]
    assert "rule_complete('CC 1')." not in payload["prolog"]["clauses"]
    assert "CC 1" not in payload["prolog"]["relations"]["rule_complete"]


def test_every_dropped_text_form_is_resolved_for_the_classifier_alone():
    # Same cells, as the parser reports them: the codes resolved and the leftover word vanished.
    for cell, state in DROPPED_TEXT_CASES:
        codes = ["CS 1", "CS 2"] if ("|" in cell or "/" in cell) else ["CS 1"]
        assert classify_prerequisite_state(course(cell, codes)) == state, cell


@pytest.mark.parametrize(
    ("raw", "prereqs"),
    [
        ("CS 1", ["CS 1"]),
        ("CS1", ["CS 1"]),
        ("cs 1, CS 2", ["CS 1", "CS 2"]),
        ("CS 1 and CS 2", ["CS 1", "CS 2"]),
        ("CS 1; CS 2 & CS 3", ["CS 1", "CS 2", "CS 3"]),
        ("CC 1/L", ["CC 1/L"]),
        ("BT-2", ["BT-2/L"]),
        ("MATH 19-20", ["Math 19", "Math 20"]),
        ("CS 1\nCS 2", ["CS 1", "CS 2"]),
        # Printed variants of a resolved code seen in the 44 cached runs (spacing, leading zero, lab marker).
        ("PATH Fit 1", ["PATHFit 1"]),
        ("Res 01/L", ["Res 1"]),
        ("Bio 108/L", ["Bio 108"]),
    ],
)
def test_plainly_resolved_cells_stay_resolved(raw, prereqs):
    assert classify_prerequisite_state(course(raw, prereqs)) == "resolved"


# Review finding B: only the exact verified literals count.
def authority_for(**kwargs):
    from types import SimpleNamespace
    from backend.bintanong_tools.prospectus_extractor.authority import build_authority

    source = kwargs.pop("source", SimpleNamespace(pdf_sha256="0" * 64, source_locator="x.pdf", source_verification="verified"))
    return build_authority(
        audit_status="ok", metadata={"program_name": "P"}, courses=[{"prerequisite_state": "resolved"}],
        source=source, approved_scope={"program_name": "P"}, pdf_hash_check="matched", **kwargs,
    )


@pytest.mark.parametrize("bad", ["rejected", "failed", "", None, "Verified", "pending"])
def test_only_the_exact_verified_literal_counts_as_source_verification(bad):
    from types import SimpleNamespace

    source = SimpleNamespace(pdf_sha256="0" * 64, source_locator="x.pdf", source_verification=bad)
    result = authority_for(source=source, content_review={"state": "reviewed"})
    assert result["authority"]["eligibility_executable"] is False
    assert {"source_verification_pending", "source_not_verified"} & set(result["authority"]["blocked_by"])


@pytest.mark.parametrize("bad", ["rejected", "failed", "", None, "Matched", "not_checked"])
def test_only_an_exact_matched_hash_check_counts(bad):
    from types import SimpleNamespace
    from backend.bintanong_tools.prospectus_extractor.authority import build_authority

    source = SimpleNamespace(pdf_sha256="0" * 64, source_locator="x.pdf", source_verification="verified")
    result = build_authority(
        audit_status="ok", metadata={"program_name": "P"}, courses=[{"prerequisite_state": "resolved"}],
        source=source, approved_scope={"program_name": "P"}, pdf_hash_check=bad,
        content_review={"state": "reviewed"},
    )
    assert result["authority"]["eligibility_executable"] is False
    assert "pdf_hash_not_checked" in result["authority"]["blocked_by"]


# Review finding C: the positive direction. Every gate satisfied at once must say so.
def test_eligibility_is_executable_only_when_every_gate_is_satisfied():
    from types import SimpleNamespace

    source = SimpleNamespace(pdf_sha256=SOURCE_HASH, source_locator="local/x.pdf", source_verification="verified")
    rows = [_cs_row(("CS 1", "Discrete Structures", "3", "none"), ("CS 2", "Discrete Structures 2", "3", "CS 1"))]
    draft = payload_for(rows, source=source)
    program = draft["metadata"]["program_name"]
    assert program and draft["metadata"]["observations"]["program_name"]["basis"] != "extractor_default"
    assert [c["prerequisite_state"] for c in draft["courses"]] == ["stated_none", "resolved"]

    payload = payload_for(
        rows, source=source, pdf_hash_check="matched", approved_scope={"program_name": program},
        review_entries=ledger_row_entries(draft),
    )
    assert payload["extraction_audit"] != "error"
    assert payload["content_review"] == "reviewed"
    assert payload["authority"]["identity_check"]["state"] == "consistent"
    assert payload["authority"]["blocked_by"] == []
    assert payload["authority"]["eligibility_executable"] is True

    # Each gate, removed alone, blocks again.
    for change in (
        {"pdf_hash_check": "not_checked"},
        {"approved_scope": None},
        {"approved_scope": {"program_name": "Something Else"}},
        {"review_entries": ledger_row_entries(draft, 1)},
        {"review_entries": None},
        {"source": SimpleNamespace(pdf_sha256=SOURCE_HASH, source_locator="x", source_verification="pending")},
    ):
        kwargs = {
            "source": source, "pdf_hash_check": "matched", "approved_scope": {"program_name": program},
            "review_entries": ledger_row_entries(draft),
        } | change
        assert payload_for(rows, **kwargs)["authority"]["eligibility_executable"] is False, change


# Review suspicions: an assumed value cannot confirm an identity, and a ledger is never dropped silently.
def test_an_assumed_campus_cannot_make_the_identity_consistent():
    payload = payload_for([CONTROL], approved_scope={"campus": "Tiniguiban - Main"})
    identity = payload["authority"]["identity_check"]
    assert payload["metadata"]["observations"]["campus"]["basis"] == "extractor_default"
    assert identity["state"] == "unverified"
    assert identity["unverified_fields"] == ["campus"]
    assert identity["mismatched_fields"] == []
    assert "identity_unverified" in payload["authority"]["blocked_by"]
    assert payload["authority"]["eligibility_executable"] is False


def test_a_mismatch_outranks_an_unverified_field():
    payload = payload_for([CONTROL], approved_scope={"campus": "Tiniguiban - Main", "program_name": "Nope"})
    assert payload["authority"]["identity_check"]["state"] == "mismatch"
    assert "identity_mismatch" in payload["authority"]["blocked_by"]


def test_a_ledger_passed_without_a_source_is_reported_as_ignored():
    base = payload_for([CONTROL])
    entries = iter(ledger_row_entries(base))  # a generator must not be lost either
    payload = payload_for([CONTROL], review_entries=entries)
    assert payload["content_review"] == "pending"
    assert payload["authority"]["content_review_detail"] == {
        "state": "pending", "ignored": "no source hash to apply the ledger against", "entries": 2,
    }
