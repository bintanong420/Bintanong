"""Checked synthetic conversion to exact field evidence and inactive rule review data."""
import copy
import importlib
import json
from pathlib import Path

import pytest

from backend.bintanong_tools.document_ingest.bundle import load_candidate_bundle
from backend.bintanong_tools.prospectus_extractor.identity import bytes_sha256
from test_prospectus_ingestion import (
    prospectus_input, runner, synthetic_converter, synthetic_prospectus,
)
from test_policy_chunks import item, raw_document


def prepare(path):
    name = "backend.bintanong_tools.document_ingest.prospectus_rules"
    assert importlib.util.find_spec(name) is not None, "prospectus rule handoff is missing"
    module = importlib.import_module(name)
    assert Path(module.__file__).resolve().is_relative_to(Path(__file__).resolve().parents[1])
    return module.prepare_rule_candidates(path)


def publish(inputs, tmp_path, monkeypatch, raw=None):
    root, snap, version = inputs
    out = tmp_path / "bundle"
    runner()(snap, [version], input_root=root, out=out,
             converter=synthetic_converter(monkeypatch, snap, raw))
    return out


def record(result, kind, code):
    return next(r for r in result["records"] if r["kind"] == kind and r["course_code"] == code)


def rehash(out, name, change):
    """Deliberate all-level rehash tests ownership independently of accidental damage."""
    target = out / name
    data = json.loads(target.read_bytes())
    change(data)
    target.write_text(json.dumps(data), encoding="utf-8")
    manifest = json.loads((out / "manifest.json").read_bytes())
    manifest["files"][name] = bytes_sha256(target.read_bytes())
    if name.startswith("conversion/") and name != "conversion/manifest.json":
        nested = out / "conversion/manifest.json"
        conversion = json.loads(nested.read_bytes())
        conversion["files"][target.name] = bytes_sha256(target.read_bytes())
        nested.write_text(json.dumps(conversion), encoding="utf-8")
        manifest["files"]["conversion/manifest.json"] = bytes_sha256(nested.read_bytes())
    (out / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


def test_combined_synthetic_conversion_bundle_bridge_compiler(prospectus_input, tmp_path, monkeypatch):
    out = publish(prospectus_input, tmp_path, monkeypatch)
    _, snap, version = prospectus_input
    before = {p.relative_to(out): p.read_bytes() for p in out.rglob("*") if p.is_file()}
    result = prepare(out)
    course = record(result, "course", "CS101")
    by_cell = {s["locator"]["cell_ids"][0]: s for s in course["spans"]}
    assert set(by_cell) == {"t0-c6", "t0-c7", "t0-c8"}
    assert by_cell["t0-c6"]["text"] == "CS101"
    assert by_cell["t0-c7"]["text"] == "Introduction to Computing"
    assert by_cell["t0-c8"]["text"] == "3"
    assert course["raw_text"]["course_code"] == ["CS101"]
    assert course["raw_text"]["course_title"] == ["Introduction to Computing"]
    assert course["raw_text"]["units.total"] == ["3"]
    for span in by_cell.values():
        assert (span["byte_sha256"], span["version_id"], span["page"], span["page_size"],
                span["bbox_origin"]) == (snap.sha256, version.version_id, 1, [612.0, 792.0], "TOPLEFT")
    assert by_cell["t0-c7"]["bbox"] == [130.0, 260.0, 240.0, 275.0]
    assert set(course["blockers"]) == {
        "missing_or_unmatched_field_evidence:" + field for field in
        ("category", "year_level", "semester", "term_index", "units.lecture", "units.lab")}
    none = record(result, "prerequisites", "CS101")
    assert none["spans"][0]["locator"]["cell_ids"] == ["t0-c9"]
    assert none["spans"][0]["text"] == "None"
    assert none["blockers"] == [] and none["review_view"]["clauses"] == []
    unknown = record(result, "prerequisites", "CS102")
    assert unknown["raw_text"] == "XX999"
    assert unknown["spans"][0]["locator"]["cell_ids"] == ["t0-c13"]
    assert unknown["value"]["unresolved"] == ["XX999"]
    assert unknown["blockers"] == ["unresolved_reference"] and "review_view" not in unknown
    assert result["source"]["version_id"] == version.version_id
    assert result["source"]["approval_state"]["state"] == "not_requested"
    assert result["source"]["content_review_state"]["state"] == "pending"
    assert all(r["activation_allowed"] is False and r["approval_id"] is None for r in result["records"])
    assert result == prepare(out)
    assert before == {p.relative_to(out): p.read_bytes() for p in out.rglob("*") if p.is_file()}
    assert snap.path.read_bytes() == snap.data and not list(out.rglob("*.pl"))
    json.dumps(result, allow_nan=False)


@pytest.mark.parametrize("name", ["prospectus_candidates.json", "raw_docling.json", "raw_docling.meta.json"])
def test_changed_candidate_raw_or_settings_hash_refuses(prospectus_input, tmp_path, monkeypatch, name):
    out = publish(prospectus_input, tmp_path, monkeypatch)
    target = out / "conversion" / name
    target.write_bytes(target.read_bytes() + b" ")
    with pytest.raises(ValueError, match="digest"):
        prepare(out)


@pytest.mark.parametrize("attack", ["foreign_cell", "unrelated_cell", "page", "cell_text", "bbox",
    "row", "table", "version", "malformed_ids", "malformed_source", "duplicate_ids", "nontext_cell_id"])
def test_rehashed_forged_ownership_refuses(prospectus_input, tmp_path, monkeypatch, attack):
    out = publish(prospectus_input, tmp_path, monkeypatch)
    def change(data):
        course = data["courses"][0]
        prov = course["provenance"]
        if attack in {"foreign_cell", "unrelated_cell"}:
            prov["source_cell_ids"].append("t9-c999" if attack == "foreign_cell" else "t0-c10")
        elif attack == "page": prov["source_cells"][0]["page"] = 2
        elif attack == "cell_text": prov["source_cells"][0]["raw_text"] = "forged wording"
        elif attack == "bbox": prov["source_cells"][0]["bbox"][0] = 11
        elif attack == "row": course["_source"]["row_index"] = 4
        elif attack == "table": course["_source"]["table_index"] = 1
        elif attack == "version": course["version_id"] = "ver-foreign"
        elif attack == "malformed_ids": prov["source_cell_ids"] = "t0-c6"
        elif attack == "malformed_source": course["_source"] = []
        elif attack == "nontext_cell_id": prov["source_cells"][0]["cell_id"] = []
        else: prov["source_cell_ids"].append(prov["source_cell_ids"][0])
    rehash(out, "conversion/prospectus_candidates.json", change)
    with pytest.raises(ValueError): prepare(out)


@pytest.mark.parametrize("missing", ["ids", "source_cells", "source", "one_field", "all_provenance"])
def test_missing_ownership_blocks_without_borrowing_row_support(prospectus_input, tmp_path, monkeypatch, missing):
    out = publish(prospectus_input, tmp_path, monkeypatch)
    def change(data):
        course = data["courses"][0]
        if missing == "all_provenance": course.pop("provenance")
        elif missing == "source": course.pop("_source")
        elif missing == "ids": course["provenance"]["source_cell_ids"] = []
        elif missing == "source_cells": course["provenance"]["source_cells"] = []
        else:
            course["provenance"]["source_cell_ids"].remove("t0-c7")
            course["provenance"]["source_cells"] = [c for c in course["provenance"]["source_cells"]
                                                       if c["cell_id"] != "t0-c7"]
    rehash(out, "conversion/prospectus_candidates.json", change)
    result = prepare(out)
    course = record(result, "course", "CS101")
    assert "missing_or_unmatched_field_evidence:course_title" in course["blockers"]
    assert course["raw_text"]["course_title"] == [] and "review_view" not in course
    if missing != "one_field":
        assert record(result, "prerequisites", "CS101")["blockers"]


def test_bottomleft_uses_native_origin_and_captured_geometry(prospectus_input, tmp_path, monkeypatch):
    raw = synthetic_prospectus()
    for cell in raw["tables"][0]["data"]["table_cells"]:
        box = cell["bbox"]
        box["t"], box["b"] = 792 - box["t"], 792 - box["b"]
        box["coord_origin"] = "BOTTOMLEFT"
    out = publish(prospectus_input, tmp_path, monkeypatch, raw)
    span = record(prepare(out), "prerequisites", "CS101")["spans"][0]
    assert span["bbox_origin"] == "BOTTOMLEFT"
    assert span["bbox"] == [370.0, 532.0, 480.0, 517.0]
    assert span["page_size"] == [612.0, 792.0]


@pytest.mark.parametrize("damage", ["missing_box", "missing_origin", "missing_page"])
def test_unlocatable_field_never_gets_usable_support(prospectus_input, tmp_path, monkeypatch, damage):
    raw = synthetic_prospectus()
    cell = raw["tables"][0]["data"]["table_cells"][7]
    if damage == "missing_box": cell.pop("bbox")
    elif damage == "missing_origin": cell["bbox"].pop("coord_origin")
    else:
        raw["tables"][0]["prov"] = []
    out = publish(prospectus_input, tmp_path, monkeypatch, raw)
    course = record(prepare(out), "course", "CS101")
    assert "missing_or_unmatched_field_evidence:course_title" in course["blockers"]
    assert "review_view" not in course


def test_repaired_wording_cannot_borrow_unrelated_matching_cell(prospectus_input, tmp_path, monkeypatch):
    out = publish(prospectus_input, tmp_path, monkeypatch)
    rehash(out, "conversion/prospectus_candidates.json",
           lambda data: data["courses"][0].update(course_title="Computer Programming"))
    course = record(prepare(out), "course", "CS101")
    assert "missing_or_unmatched_field_evidence:course_title" in course["blockers"]
    assert course["raw_text"]["course_title"] == ["Introduction to Computing"]


def test_overlapping_cells_leave_field_ownership_ambiguous(prospectus_input, tmp_path, monkeypatch):
    raw = synthetic_prospectus()
    cells = raw["tables"][0]["data"]["table_cells"]
    cells.append(copy.deepcopy(cells[7]))
    out = publish(prospectus_input, tmp_path, monkeypatch, raw)
    course = record(prepare(out), "course", "CS101")
    assert "missing_or_unmatched_field_evidence:course_title" in course["blockers"]
    assert course["raw_text"]["course_title"] == [] and "review_view" not in course


def test_semantic_repair_cannot_be_presented_as_direct_field_support(prospectus_input, tmp_path, monkeypatch):
    out = publish(prospectus_input, tmp_path, monkeypatch)
    def change(data):
        data["courses"][0]["provenance"].update(resolution_method="semantic_repair", repair_id="repair-1")
    rehash(out, "conversion/prospectus_candidates.json", change)
    course = record(prepare(out), "course", "CS101")
    assert "missing_or_unmatched_field_evidence:course_code" in course["blockers"]
    assert not course["spans"] and "review_view" not in course


def test_blank_prerequisite_does_not_infer_review_from_status(prospectus_input, tmp_path, monkeypatch):
    raw = synthetic_prospectus()
    raw["tables"][0]["data"]["table_cells"][9]["text"] = ""
    out = publish(prospectus_input, tmp_path, monkeypatch, raw)
    unknown = record(prepare(out), "prerequisites", "CS101")
    assert unknown["prerequisite_state"] == "blank_unreviewed" and unknown["blockers"]
    assert "review_view" not in unknown


@pytest.mark.parametrize("attack", [None, "foreign_version", "foreign_pdf", "stale", "forged"])
def test_only_applicable_existing_ledger_can_support_reviewed_blank(prospectus_input, tmp_path, monkeypatch, attack):
    from backend.bintanong_tools.prospectus_extractor.ledger import course_locator, make_entry
    raw = synthetic_prospectus()
    raw["tables"][0]["data"]["table_cells"][9]["text"] = ""
    out = publish(prospectus_input, tmp_path, monkeypatch, raw)
    payload = load_candidate_bundle(out)["domain_payload"]
    _, snap, version = prospectus_input
    entry = make_entry(pdf_sha256="b" * 64 if attack == "foreign_pdf" else snap.sha256,
        locator=course_locator(payload["courses"][0]), field="prerequisites_raw",
        old_value="obsolete" if attack == "stale" else "", new_value=None,
        disposition="accepted", reviewer="synthetic-reviewer", reason="Read the original blank cell", section="test")
    if attack == "forged": entry["reviewer"] = ""
    evidence = {"version_id": "ver-other" if attack == "foreign_version" else version.version_id,
                "entries": [entry]}
    rehash(out, "conversion/prospectus_candidates.json", lambda data: data.update(review_evidence=evidence))
    result = record(prepare(out), "prerequisites", "CS101")
    assert result["prerequisite_state"] == ("reviewed_empty" if attack is None else "blank_unreviewed")
    assert ("review_view" in result) is (attack is None)
    assert result["review_evidence_refs"] == ([entry["entry_id"]] if attack is None else [])
    assert result["activation_allowed"] is False


def test_policy_private_and_raw_json_are_refused(prospectus_input, tmp_path, monkeypatch):
    from backend.bintanong_tools.document_ingest.pipeline import run_ingestion
    root, snap, version = prospectus_input
    policy = tmp_path / "policy"
    run_ingestion(snap, [version], input_root=root, out=policy, classification="policy_candidate",
                  converter=synthetic_converter(monkeypatch, snap, raw_document([item("Printed rule")], pages=1)))
    with pytest.raises(ValueError): prepare(policy)
    out = publish(prospectus_input, tmp_path, monkeypatch)
    rehash(out, "source_register.json", lambda data: data[0].update(namespace="private"))
    with pytest.raises(ValueError): prepare(out)
    with pytest.raises(ValueError): prepare(out / "conversion/raw_docling.json")


def test_bridge_has_no_publication_network_or_runtime(prospectus_input, tmp_path, monkeypatch):
    import os
    import socket
    import subprocess
    import sys
    from types import SimpleNamespace
    out = publish(prospectus_input, tmp_path, monkeypatch)
    prepare(out)
    def forbidden(*args, **kwargs): raise AssertionError("publication/network/runtime forbidden")
    monkeypatch.setattr(Path, "write_text", forbidden)
    monkeypatch.setattr(Path, "write_bytes", forbidden)
    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    monkeypatch.setattr(os, "system", forbidden)
    monkeypatch.setitem(sys.modules, "janus", SimpleNamespace(consult=forbidden, query=forbidden))
    monkeypatch.setitem(sys.modules, "janus_swi", sys.modules["janus"])
    assert prepare(out)["records"]


def test_changed_nonblank_source_cannot_be_reviewed_empty(prospectus_input, tmp_path, monkeypatch):
    """T3-S1: current-value ledger consistency cannot erase untouched printed CS102."""
    from backend.bintanong_tools.prospectus_extractor.ledger import course_locator, make_entry
    raw = synthetic_prospectus()
    raw["tables"][0]["data"]["table_cells"][9]["text"] = "CS102"
    out = publish(prospectus_input, tmp_path, monkeypatch, raw)
    payload = load_candidate_bundle(out)["domain_payload"]
    _, snap, version = prospectus_input
    entry = make_entry(pdf_sha256=snap.sha256, locator=course_locator(payload["courses"][0]),
        field="prerequisites_raw", old_value="", new_value=None, disposition="accepted",
        reviewer="reviewer", reason="Accepted blank candidate", section="test")
    def change(data):
        data["courses"][0].update(prerequisites_raw="", prerequisites=[], prerequisites_unresolved=[],
                                  standing_requirements=[], prerequisite_state="reviewed_empty")
        data["review_evidence"] = {"version_id": version.version_id, "entries": [entry]}
    rehash(out, "conversion/prospectus_candidates.json", change)
    # The exact reviewed_empty variant must reach the bridge; blank_unreviewed does not.
    assert load_candidate_bundle(out)["domain_payload"]["courses"][0]["prerequisite_state"] == "reviewed_empty"
    try:
        result = record(prepare(out), "prerequisites", "CS101")
    except ValueError:
        return
    assert result["blockers"], "Printed CS102 prerequisite was erased into unblocked reviewed_empty"
    assert "review_view" not in result


@pytest.mark.parametrize("damage", ["missing", "ambiguous", "repair", "unlocatable", "other_course"])
def test_unsupported_blank_keeps_unrelated_valid_review(prospectus_input, tmp_path, monkeypatch, damage):
    from backend.bintanong_tools.prospectus_extractor.ledger import course_locator, make_entry
    raw = synthetic_prospectus()
    cells = raw["tables"][0]["data"]["table_cells"]
    cells[9]["text"] = cells[13]["text"] = ""
    if damage == "ambiguous": cells.append(copy.deepcopy(cells[9]))
    if damage == "unlocatable": cells[9].pop("bbox")
    if damage == "other_course": cells.remove(cells[9])
    out = publish(prospectus_input, tmp_path, monkeypatch, raw)
    payload = load_candidate_bundle(out)["domain_payload"]
    _, snap, version = prospectus_input
    entries = [make_entry(pdf_sha256=snap.sha256, locator=course_locator(c), field="prerequisites_raw",
        old_value="", new_value=None, disposition="accepted", reviewer="reviewer",
        reason="Read original blank cell", section="test") for c in payload["courses"]]
    def change(data):
        first = data["courses"][0]
        if damage == "missing":
            first["provenance"]["source_cell_ids"].remove("t0-c7")
            first["provenance"]["source_cells"] = [c for c in first["provenance"]["source_cells"]
                                                      if c["cell_id"] != "t0-c7"]
            entries[0]["locator"] = course_locator(first)
            from backend.bintanong_tools.prospectus_extractor.ledger import entry_id_of
            entries[0]["entry_id"] = entry_id_of(entries[0])
        if damage == "repair":
            first["provenance"].update(resolution_method="semantic_repair", repair_id="repair-1")
        data["review_evidence"] = {"version_id": version.version_id, "entries": entries}
    rehash(out, "conversion/prospectus_candidates.json", change)
    result = prepare(out)
    unsupported = record(result, "prerequisites", "CS101")
    assert unsupported["blockers"] and "review_view" not in unsupported
    supported = record(result, "prerequisites", "CS102")
    assert supported["prerequisite_state"] == "reviewed_empty" and supported["blockers"] == []
    assert supported["review_evidence_refs"] == [entries[1]["entry_id"]]
