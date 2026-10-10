"""Synthetic source-bound inactive candidates; no PDF or generated JSON oracle."""
import copy
import importlib
import json
from pathlib import Path

import pytest

from backend.bintanong_tools.document_ingest.register import mint_pending_register
from backend.bintanong_tools.prospectus_extractor.ledger import course_locator, make_entry
from backend.bintanong_tools.prospectus_extractor.prerequisites import (
    CodeIndex, classify_prerequisite_state, resolve_prerequisites,
)
from backend.bintanong_tools.prospectus_extractor.prolog import generate_prolog_knowledge
from contracts_fixtures import span


def compile_candidates(*args, **kwargs):
    module = importlib.import_module("backend.bintanong_tools.prospectus_extractor.rule_candidates")
    assert Path(module.__file__).resolve().is_relative_to(Path(__file__).resolve().parents[1])
    return module.build_rule_candidates(*args, **kwargs)


def fixture(raw="CS 1", *, title="Algorithms"):
    source = mint_pending_register([{"filename": "synthetic.pdf", "sha256": "a" * 64,
                                    "acquisition_locator": "shelf:synthetic"}], synthetic=True)[0]
    courses = []
    fields = {}
    for n, wording in [(1, "None"), (2, raw)]:
        code = f"CS {n}"
        resolution = resolve_prerequisites(wording, CodeIndex(["CS 1", "CS 2"]))
        course = {"course_code": code, "course_title": "Foundations" if n == 1 else title,
                  "units": {"total": 3, "lecture": 3, "lab": 0}, "year_level": "First Year",
                  "semester": "First Semester", "term_index": 1, "category": "Major",
                  "prerequisites_raw": wording, "prerequisites": resolution.resolved,
                  "prerequisites_unresolved": resolution.unresolved,
                  "standing_requirements": resolution.standing_rules,
                  "provenance": {"page": 1, "source_cell_ids": [f"t0-c{n}"]},
                  "_source": {"table_index": 0}}
        course["prerequisite_state"] = classify_prerequisite_state(course)
        courses.append(course)
        values = {k: course[k] for k in ("course_code", "course_title", "year_level", "semester",
                                       "term_index", "prerequisites_raw", "category")}
        values.update({f"units.{k}": v for k, v in course["units"].items()})
        fields[code] = {}
        for field, value in values.items():
            if value != "":
                support = span(source.byte_sha256, cell=f"t0-c{n}-{field}", text=str(value))
                support["version_id"] = source.version_id
                fields[code][field] = [support]
    payload = {"run_identity": {"pdf_sha256": source.byte_sha256}, "courses": courses,
               "elective_tracks": [], "term_units": [], "metadata": {},
               "extraction_audit": "ok", "content_review": "pending", "source_verification": "pending",
               "authority": {"eligibility_executable": False},
               "audit": {"promotion_status": "candidate", "structural_anomalies": []}}
    return payload, source, fields


def record(artifact, kind, code="CS 2"):
    return next(r for r in artifact["records"] if r["kind"] == kind and r["course_code"] == code)


def test_supported_views_are_inactive_and_match_supported_generator_values():
    payload, source, fields = fixture()
    original = copy.deepcopy((payload, source.model_dump(mode="json"), fields))
    output = compile_candidates(payload, source, fields)
    course = record(output, "course")
    prereq = record(output, "prerequisites")
    assert course["review_view"]["clause"] == "course('CS 2', 'Algorithms', 3, 3, 0, 'First Year', 'First Semester', 1)."
    assert prereq["review_view"]["clauses"] == ["prerequisite('CS 2', 'CS 1')."]
    generated = generate_prolog_knowledge({}, payload["courses"], [], [])
    assert course["review_view"]["clause"] in generated["clauses"]
    assert prereq["review_view"]["clauses"][0] in generated["clauses"]
    for row in output["records"]:
        assert row["activation_allowed"] is False and row["approval_id"] is None
        assert not any(k in row for k in ("eligible", "approved", "rule_complete"))
    assert output["source"]["approval_state"]["state"] == "not_requested"
    assert (payload, source.model_dump(mode="json"), fields) == original
    json.dumps(output, allow_nan=False)


@pytest.mark.parametrize("fault", ["digest", "edition", "namespace", "approved", "executable", "nested_authority",
                                   "null_version", "foreign_version", "foreign_digest", "page", "text", "geometry",
                                   "unknown_field", "foreign_course", "duplicate", "self", "forged_resolved"])
def test_global_refusal_preserves_inputs(fault):
    payload, source, fields = fixture()
    if fault == "digest": payload["run_identity"]["pdf_sha256"] = "b" * 64
    elif fault == "edition": payload["edition_id"] = "edition-foreign"
    elif fault == "namespace": payload["namespace"] = "private_session"
    elif fault == "approved": payload["approved"] = True
    elif fault == "executable": payload["authority"]["eligibility_executable"] = True
    elif fault == "nested_authority": payload["courses"][0]["is_approved"] = True
    elif fault in ("null_version", "foreign_version", "foreign_digest", "page", "text", "geometry"):
        support = fields["CS 2"]["course_title"][0]
        support.update({"null_version": {"version_id": None}, "foreign_version": {"version_id": "ver-foreign"},
                        "foreign_digest": {"byte_sha256": "b" * 64}, "page": {"page": None},
                        "text": {"text": ""}, "geometry": {"bbox": [2, 1, 1, 2]}}[fault])
    elif fault == "unknown_field": fields["CS 2"]["program"] = []
    elif fault == "foreign_course": fields["XX 9"] = fields["CS 2"]
    elif fault == "duplicate": payload["courses"].append(copy.deepcopy(payload["courses"][0]))
    elif fault == "self": payload["courses"][1]["prerequisites"] = ["CS 2"]
    elif fault == "forged_resolved": payload["courses"][1]["prerequisites"] = ["XX999"]
    original = copy.deepcopy((payload, fields))
    with pytest.raises(ValueError):
        compile_candidates(payload, source, fields)
    assert (payload, fields) == original


@pytest.mark.parametrize("value", [True, -1, float("nan"), float("inf"), "3", {}, []])
def test_malformed_units_refuse(value):
    payload, source, fields = fixture()
    payload["courses"][1]["units"]["total"] = value
    with pytest.raises(ValueError): compile_candidates(payload, source, fields)


def test_missing_numeric_support_never_fabricates_zero():
    payload, source, fields = fixture()
    payload["courses"][1]["units"]["total"] = None
    del fields["CS 2"]["units.total"]
    missing = record(compile_candidates(payload, source, fields), "course")
    assert missing["value"]["units"]["total"] is None
    assert missing["blockers"] and "review_view" not in missing
    payload["courses"][1]["units"]["total"] = 0
    unsupported_zero = record(compile_candidates(payload, source, fields), "course")
    assert unsupported_zero["blockers"] and "review_view" not in unsupported_zero


@pytest.mark.parametrize("raw,state", [("", "blank_unreviewed"), ("No prerequisite required", "stated_none"),
    ("XX999", "unresolved_reference"), ("CS 1 or XX999", "alternative_or_exception"),
    ("CS 1 except with consent", "alternative_or_exception"), ("Third year standing", "standing_condition"),
    ("co-requisite: CS 1", "unresolved_reference"), ("not required — ²", "unresolved_reference")])
def test_raw_semantics_remain_distinct(raw, state):
    payload, source, fields = fixture(raw)
    item = record(compile_candidates(payload, source, fields), "prerequisites")
    assert item["raw_text"] == raw and item["prerequisite_state"] == state
    if state != "stated_none":
        assert item["blockers"] and "review_view" not in item
    else: assert item["review_view"]["clauses"] == []
    if raw: assert item["spans"][0]["text"] == raw


def test_false_state_claim_is_recomputed_and_refused():
    payload, source, fields = fixture("XX999")
    payload["courses"][1]["prerequisite_state"] = "resolved"
    with pytest.raises(ValueError): compile_candidates(payload, source, fields)


def accepted_blank(payload, source):
    course = payload["courses"][1]
    entry = make_entry(pdf_sha256=source.byte_sha256, locator=course_locator(course),
                       field="prerequisites_raw", old_value="", new_value=None, disposition="accepted",
                       reviewer="synthetic-reviewer", reason="Checked the blank source cell", section="synthetic")
    return {"version_id": source.version_id, "entries": [entry]}


@pytest.mark.parametrize("fault", [None, "foreign", "stale", "unresolved", "forged"])
def test_recorded_blank_review_reuses_applicable_ledger_semantics(fault):
    from backend.bintanong_tools.prospectus_extractor.ledger import entry_id_of
    payload, source, fields = fixture("")
    evidence = accepted_blank(payload, source)
    if fault == "foreign": evidence["version_id"] = "ver-other"
    if fault == "stale": evidence["entries"][0]["old_value"] = "obsolete"
    if fault == "unresolved": evidence["entries"][0]["disposition"] = "unresolved"
    if fault in ("stale", "unresolved"): evidence["entries"][0]["entry_id"] = entry_id_of(evidence["entries"][0])
    if fault == "forged": evidence["entries"][0]["reviewer"] = ""
    item = record(compile_candidates(payload, source, fields, review_evidence=evidence), "prerequisites")
    assert item["prerequisite_state"] == ("reviewed_empty" if fault is None else "blank_unreviewed")
    assert ("review_view" in item) is (fault is None)
    assert item["approval_id"] is None


def test_cycles_block_all_affected_prerequisite_views():
    payload, source, fields = fixture()
    first = payload["courses"][0]
    first.update(prerequisites_raw="CS 2", prerequisites=["CS 2"], prerequisite_state="resolved")
    fields["CS 1"]["prerequisites_raw"][0]["text"] = "CS 2"
    result = compile_candidates(payload, source, fields)
    for code in ("CS 1", "CS 2"):
        item = record(result, "prerequisites", code)
        assert "prerequisite_cycle" in item["blockers"] and "review_view" not in item


def test_program_terms_electives_preserved_but_blocked():
    payload, source, fields = fixture()
    payload["metadata"] = {"program_name": "Unverified degree"}
    payload["term_units"] = [{"computed_units": 6}]
    payload["elective_tracks"] = [{"group": "Track A", "options": []}]
    result = compile_candidates(payload, source, fields)
    for kind, value in [("program", payload["metadata"]), ("term_units", payload["term_units"][0]),
                        ("elective_track", payload["elective_tracks"][0])]:
        item = record(result, kind, None)
        assert item["value"] == value and item["blockers"] == ["unsupported_field_evidence"]
        assert "review_view" not in item


def test_deterministic_without_timestamp_path_or_collection_order():
    payload, source, fields = fixture()
    first = compile_candidates(payload, source, fields)
    payload["courses"].reverse()
    payload["generated_at"] = "2099-01-01"
    payload["metadata"] = {"source_file": "C:/elsewhere/file.pdf", "generated_at": "2099"}
    payload["prolog"] = {"clauses": [":- halt."]}
    second = compile_candidates(payload, source, dict(reversed(list(fields.items()))))
    assert first == second


def test_quoting_keeps_injection_as_data_and_compiler_has_no_side_effects(monkeypatch):
    import builtins
    import socket
    import subprocess
    title = "O'Brien \\ path\n% comment\n:- halt. — ²"
    payload, source, fields = fixture(title=title)
    # Load first: import machinery may read Python source, but preparation must be pure.
    compile_candidates(payload, source, fields)
    def forbidden(*args, **kwargs): raise AssertionError("publication/execution is forbidden")
    with monkeypatch.context() as guard:
        guard.setattr(builtins, "open", forbidden)
        guard.setattr(Path, "write_text", forbidden)
        guard.setattr(Path, "write_bytes", forbidden)
        guard.setattr(socket, "socket", forbidden)
        guard.setattr(subprocess, "Popen", forbidden)
        result = compile_candidates(payload, source, fields)
    item = record(result, "course")
    assert item["value"]["course_title"] == title
    assert "O''Brien" in item["review_view"]["clause"]
    assert "\n" not in item["review_view"]["clause"]
    assert all(not c.startswith(":-") and "rule_complete(" not in c and "eligible(" not in c
               for r in result["records"] for c in ([r["review_view"]["clause"]]
                   if "clause" in r.get("review_view", {}) else r.get("review_view", {}).get("clauses", [])))
