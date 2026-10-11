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
from test_prospectus_ingestion import prospectus_input, synthetic_converter


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


@pytest.mark.parametrize("location,bad", [
    ("payload", None), ("courses", {}), ("course", None), ("run_identity", []), ("units", []),
    ("field_spans", []), ("field_course", []), ("field_sequence", {}), ("span", None),
    ("review", []), ("review_entries", {}), ("review_entry", None), ("audit", []),
    ("anomalies", {}), ("anomaly", []), ("anomaly_cells", "cell"), ("anomaly_cells", [[]]),
    ("provenance_cells", "cell"), ("provenance_cells", [[]]), ("metadata", []),
    ("elective_tracks", {}), ("term_units", {}), ("authority", []),
])
def test_malformed_boundary_containers_refuse(location, bad):
    payload, source, fields = fixture()
    evidence = None
    if location == "payload": payload = bad
    elif location == "course": payload["courses"][0] = bad
    elif location == "units": payload["courses"][0]["units"] = bad
    elif location == "field_spans": fields = bad
    elif location == "field_course": fields["CS 1"] = bad
    elif location == "field_sequence": fields["CS 1"]["course_code"] = bad
    elif location == "span": fields["CS 1"]["course_code"] = [bad]
    elif location == "review": evidence = bad
    elif location in {"review_entries", "review_entry"}:
        evidence = {"version_id": source.version_id, "entries": bad if location == "review_entries" else [bad]}
    elif location == "anomalies": payload["audit"]["structural_anomalies"] = bad
    elif location == "anomaly": payload["audit"]["structural_anomalies"] = [bad]
    elif location == "anomaly_cells":
        payload["audit"]["structural_anomalies"] = [{
            "type": "ambiguous_adjacent_prerequisite_fragment", "source_cell_ids": bad}]
    elif location == "provenance_cells": payload["courses"][0]["provenance"]["source_cell_ids"] = bad
    else: payload[location] = bad
    before = copy.deepcopy((payload, fields, evidence))
    with pytest.raises(ValueError): compile_candidates(payload, source, fields, review_evidence=evidence)
    assert (payload, fields, evidence) == before


@pytest.mark.parametrize("field,value", [
    ("year_level", True), ("year_level", 1), ("year_level", []), ("semester", {}), ("semester", 1),
    ("term_index", True), ("term_index", -1), ("term_index", 0), ("term_index", 1.5),
    ("term_index", float("inf")), ("term_index", float("nan")), ("term_index", "1"),
    ("prerequisites", "CS 1"), ("prerequisites", [True]), ("prerequisites", [{"code": "CS 1"}]),
    ("prerequisites", ["CS 1", "CS 1"]), ("prerequisites_unresolved", None),
    ("prerequisites_unresolved", ["forged"]), ("standing_requirements", ["forged"]),
    ("prerequisite_state", []), ("prerequisites_raw", None),
])
def test_malformed_course_scalars_and_forged_references_refuse(field, value):
    payload, source, fields = fixture()
    payload["courses"][1][field] = value
    with pytest.raises(ValueError): compile_candidates(payload, source, fields)


@pytest.mark.parametrize("fault", ["source_namespace", "source_privilege", "run_version", "run_edition",
    "top_digest", "authority_digest", "normalized_activation", "nested_review_activation", "malformed_code"])
def test_forged_source_or_activation_claims_refuse(fault):
    payload, source, fields = fixture()
    evidence = None
    if fault in {"source_namespace", "source_privilege"}:
        source = source.model_dump(mode="json")
        if fault == "source_namespace": source["namespace"] = "private_session"
        else: source["approval_id"] = "forged"
    elif fault in {"run_version", "run_edition"}:
        payload["run_identity"]["version_id" if fault == "run_version" else "edition_id"] = "foreign"
    elif fault == "top_digest": payload["pdf_sha256"] = "b" * 64
    elif fault == "authority_digest": payload["authority"]["source_record"] = {"pdf_sha256": "b" * 64}
    elif fault == "normalized_activation": payload["authority"]["Activation-Allowed"] = True
    elif fault == "nested_review_activation":
        evidence = accepted_blank(fixture("")[0], source)
        evidence["entries"][0]["activation_allowed"] = True
    else:
        code = "CS 2\n:- halt."
        payload["courses"][1]["course_code"] = code
        fields[code] = fields.pop("CS 2")
        fields[code]["course_code"][0]["text"] = code
    with pytest.raises(ValueError): compile_candidates(payload, source, fields, review_evidence=evidence)


def test_real_pending_producer_checked_bundle_reaches_pure_compiler(prospectus_input, tmp_path, monkeypatch):
    from backend.bintanong_tools.document_ingest.prospectus import run_prospectus_ingestion
    from backend.bintanong_tools.document_ingest.bundle import load_candidate_bundle
    root, snapshot, version = prospectus_input
    out = tmp_path / "bundle"
    run_prospectus_ingestion(snapshot, [version], input_root=root, out=out,
                            converter=synthetic_converter(monkeypatch, snapshot))
    checked = load_candidate_bundle(out)
    payload = checked["domain_payload"]
    original = copy.deepcopy(payload)
    result = compile_candidates(payload, checked["source_register"][0], {})
    assert payload == original
    assert result["source"]["byte_sha256"] == snapshot.sha256
    assert result["source"]["content_review_state"]["state"] == "pending"
    assert result["source"]["approval_state"]["state"] == "not_requested"
    unknown = record(result, "prerequisites", "CS102")
    assert unknown["raw_text"] == "XX999" and "unresolved_reference" in unknown["blockers"]
    assert all(r["blockers"] and "review_view" not in r and not r["activation_allowed"]
               and r["approval_id"] is None for r in result["records"])


def test_genuine_ambiguous_blank_cannot_be_promoted_by_accepted_review():
    payload, source, fields = fixture("")
    payload["audit"]["structural_anomalies"] = [{
        "type": "ambiguous_adjacent_prerequisite_fragment", "source_cell_ids": ["t0-c2"]}]
    payload["courses"][1]["prerequisite_state"] = "unreadable"
    result = compile_candidates(payload, source, fields, review_evidence=accepted_blank(payload, source))
    item = record(result, "prerequisites")
    assert item["prerequisite_state"] == "unreadable" and "unreadable" in item["blockers"]
    assert "review_view" not in item and item["review_evidence_refs"] == []


@pytest.mark.parametrize("fault", ["digest", "field", "locator", "later_unresolved"])
def test_blank_review_must_match_exact_current_field_source_and_latest_decision(fault):
    from backend.bintanong_tools.prospectus_extractor.ledger import entry_id_of
    payload, source, fields = fixture("")
    evidence = accepted_blank(payload, source)
    entry = evidence["entries"][0]
    if fault == "digest": entry["pdf_sha256"] = "b" * 64
    elif fault == "field": entry["field"] = "course_title"
    elif fault == "locator": entry["locator"]["page"] = 2
    else:
        entry = copy.deepcopy(entry)
        entry["disposition"] = "unresolved"
        evidence["entries"].append(entry)
    entry["entry_id"] = entry_id_of(entry)
    item = record(compile_candidates(payload, source, fields, review_evidence=evidence), "prerequisites")
    assert item["prerequisite_state"] == "blank_unreviewed" and "review_view" not in item


def test_unordered_field_support_and_locator_ids_are_stable():
    payload, source, fields = fixture()
    support = fields["CS 2"]["course_title"][0]
    support["locator"]["cell_ids"] = ["t0-c9", "t0-c8"]
    other = copy.deepcopy(support)
    other["page"] = 2
    fields["CS 2"]["course_title"].append(other)
    first = compile_candidates(payload, source, fields)
    fields["CS 2"]["course_title"].reverse()
    for item in fields["CS 2"]["course_title"]: item["locator"]["cell_ids"].reverse()
    second = compile_candidates(payload, source, fields)
    assert first == second
    assert not record(first, "course")["blockers"]


def test_review_timestamp_and_local_path_do_not_change_candidate_semantic_hashes():
    from backend.bintanong_tools.prospectus_extractor.ledger import entry_id_of
    payload, source, fields = fixture("")
    evidence = accepted_blank(payload, source)
    first = compile_candidates(payload, source, fields, review_evidence=evidence)
    entry = evidence["entries"][0]
    entry["recorded_at"] = "2099-01-01T00:00:00Z"
    entry["section"] = "C:/elsewhere/source.pdf"
    entry["entry_id"] = entry_id_of(entry)
    second = compile_candidates(payload, source, fields, review_evidence=evidence)
    assert [r["id"] for r in first["records"]] == [r["id"] for r in second["records"]]
    assert first["content_digest"] == second["content_digest"]
    assert record(second, "prerequisites")["review_evidence_refs"] == [entry["entry_id"]]


def test_accepted_blank_locator_id_order_is_not_semantic():
    from backend.bintanong_tools.prospectus_extractor.ledger import entry_id_of, entry_problem
    payload, source, fields = fixture("")
    payload["courses"][1]["provenance"]["source_cell_ids"] = ["t0-c2", "t0-c3"]
    evidence = accepted_blank(payload, source)
    original_inputs = copy.deepcopy((payload, fields, evidence))
    first = compile_candidates(payload, source, fields, review_evidence=evidence)
    assert (payload, fields, evidence) == original_inputs
    changed = copy.deepcopy(evidence)
    changed["entries"][0]["locator"]["cell_ids"].reverse()
    changed["entries"][0]["entry_id"] = entry_id_of(changed["entries"][0])
    assert entry_problem(changed["entries"][0]) is None
    before = copy.deepcopy((payload, fields, changed))
    second = compile_candidates(payload, source, fields, review_evidence=changed)
    assert (payload, fields, changed) == before
    one, two = record(first, "prerequisites"), record(second, "prerequisites")
    assert one["prerequisite_state"] == two["prerequisite_state"] == "reviewed_empty"
    assert one["review_view"] == two["review_view"] == {"clauses": [], "relations": []}
    assert one["review_evidence_refs"] == [evidence["entries"][0]["entry_id"]]
    assert two["review_evidence_refs"] == [changed["entries"][0]["entry_id"]]
    assert one["id"] == two["id"] and first["content_digest"] == second["content_digest"]


def test_actual_all_of_order_and_lab_course_codes_are_preserved():
    payload, source, fields = fixture()
    lab = copy.deepcopy(payload["courses"][0])
    lab["course_code"] = "CC 1/L"
    lab["provenance"]["source_cell_ids"] = ["t0-lab"]
    payload["courses"].append(lab)
    fields[lab["course_code"]] = copy.deepcopy(fields["CS 1"])
    fields[lab["course_code"]]["course_code"][0]["text"] = lab["course_code"]
    course = payload["courses"][1]
    course.update(prerequisites_raw="CC 1/L, CS 1", prerequisites=["CC 1/L", "CS 1"])
    fields["CS 2"]["prerequisites_raw"][0]["text"] = course["prerequisites_raw"]
    result = compile_candidates(payload, source, fields)
    item = record(result, "prerequisites")
    assert item["value"]["all_of"] == ["CC 1/L", "CS 1"]
    assert item["review_view"]["clauses"] == ["prerequisite('CS 2', 'CC 1/L').", "prerequisite('CS 2', 'CS 1')."]


def test_printed_self_edge_cannot_hide_in_filtered_extractor_references():
    payload, source, fields = fixture("CS 2")
    payload["courses"][1].update(prerequisites=[], prerequisite_state="unreadable")
    with pytest.raises(ValueError): compile_candidates(payload, source, fields)


@pytest.mark.parametrize("fault", ["term_bool", "term_negative", "term_nonfinite", "term_year",
    "elective_options", "elective_option", "elective_number", "program_type",
    "nested_identity", "nested_content_review", "camel_activation", "completeness"])
def test_blocked_records_do_not_excuse_malformed_data_or_privileged_claims(fault):
    payload, source, fields = fixture()
    if fault.startswith("term_"):
        term = {"year_level": "1st Year", "semester": "1st Semester", "computed_units": 6}
        if fault == "term_bool": term["computed_units"] = True
        elif fault == "term_negative": term["computed_units"] = -1
        elif fault == "term_nonfinite": term["computed_units"] = float("nan")
        else: term["year_level"] = []
        payload["term_units"] = [term]
    elif fault.startswith("elective_"):
        track = {"group": "CS Elective 1", "options": []}
        if fault == "elective_options": track["options"] = {}
        elif fault == "elective_option": track["options"] = [None]
        else: track["elective_number"] = True
        payload["elective_tracks"] = [track]
    elif fault == "program_type": payload["metadata"] = {"program_name": []}
    elif fault == "nested_identity": payload["authority"]["identity_check"] = {"state": "consistent", "approved_scope": None}
    elif fault == "nested_content_review": payload["authority"]["content_review_detail"] = {"state": "reviewed"}
    elif fault == "camel_activation": payload["activationAllowed"] = True
    else: payload["complete"] = True
    with pytest.raises(ValueError): compile_candidates(payload, source, fields)


def test_semantic_review_change_changes_identity_without_changing_source_states():
    from backend.bintanong_tools.prospectus_extractor.ledger import entry_id_of
    payload, source, fields = fixture("")
    evidence = accepted_blank(payload, source)
    first = compile_candidates(payload, source, fields, review_evidence=evidence)
    entry = evidence["entries"][0]
    entry["reason"] = "An independent source-cell recheck"
    entry["entry_id"] = entry_id_of(entry)
    second = compile_candidates(payload, source, fields, review_evidence=evidence)
    assert record(first, "prerequisites")["id"] != record(second, "prerequisites")["id"]
    assert first["content_digest"] != second["content_digest"]
    assert first["source"] == second["source"]


def test_unknown_source_supported_reference_and_cyclic_dependencies_never_get_completeness_views():
    payload, source, fields = fixture("XX999")
    output = compile_candidates(payload, source, fields)
    item = record(output, "prerequisites")
    assert item["value"] == {"all_of": [], "unresolved": ["XX999"], "standing": []}
    assert item["spans"][0]["version_id"] == source.version_id
    assert "review_view" not in item and "unresolved_reference" in item["blockers"]


def test_compiler_cannot_reach_inprocess_prolog_or_indirect_writers(monkeypatch):
    import os
    import sys
    from types import SimpleNamespace
    payload, source, fields = fixture()
    def forbidden(*args, **kwargs): raise AssertionError("Prolog and publication forbidden")
    monkeypatch.setitem(sys.modules, "janus", SimpleNamespace(consult=forbidden, query=forbidden, query_once=forbidden))
    monkeypatch.setitem(sys.modules, "janus_swi", sys.modules["janus"])
    monkeypatch.setattr(os, "system", forbidden)
    monkeypatch.setattr(Path, "open", forbidden)
    result = compile_candidates(payload, source, fields)
    assert all(not r["activation_allowed"] and r["approval_id"] is None for r in result["records"])


def test_root_program_values_are_retained_as_unsupported_review_data():
    payload, source, fields = fixture()
    payload.update(program="A pending program", degree="BS", campus="A pending campus")
    result = compile_candidates(payload, source, fields)
    item = record(result, "program", None)
    assert item["value"]["payload_fields"] == {
        "program": "A pending program", "degree": "BS", "campus": "A pending campus"}
    assert item["blockers"] == ["unsupported_field_evidence"] and "review_view" not in item


@pytest.mark.parametrize("number,printed", [(0, "0." + "0" * 400 + "1"),
    (0.1, "0.100000000000000000000000000001")])
def test_numeric_field_support_cannot_round_a_different_printed_number(number, printed):
    payload, source, fields = fixture()
    payload["courses"][1]["units"]["total"] = number
    fields["CS 2"]["units.total"][0]["text"] = printed
    item = record(compile_candidates(payload, source, fields), "course")
    assert "missing_or_unmatched_field_evidence:units.total" in item["blockers"]
    assert "review_view" not in item
