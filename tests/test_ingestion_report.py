"""Synthetic candidate accounting and conversion-to-report pipeline."""
import importlib
import json
from dataclasses import replace
from types import SimpleNamespace

import pytest

from backend.bintanong_tools.document_ingest import policy_text, procedure_text, register
from backend.bintanong_tools.prospectus_extractor import loader
from backend.bintanong_tools.prospectus_extractor.identity import InputSnapshot
from test_policy_chunks import bound, chunks_module, item, raw_document, table


def report_module():
    return importlib.import_module("backend.bintanong_tools.document_ingest.report")


def test_report_every_item_table_page_omission_and_pending_state(bound):
    _, _, version = bound
    raw = raw_document([item("rule"), item(""), {"text": "unlocated", "label": "text", "prov": []}],
                       [table(["Header", "row"], multi_page=True)], pages=3)
    candidates = procedure_text.read_procedure_items(raw, version, printed_page_labels={1: "iv"})
    result = chunks_module().build_policy_chunks(candidates)
    metadata = {"source_sha256": version.byte_sha256, "conversion_identity": "b" * 64,
                "conversion_settings": {"backend": "synthetic", "versions": {"docling": "stub"}}}
    report = report_module().build_ingestion_report(candidates, result, conversion_metadata=metadata)
    assert report["accounting_complete"] is True and report["approval_id"] is None
    assert report["source_verification"] == report["content_review"] == "pending"
    assert report["counts"] == {"raw_items": 3, "covered_items": 1, "rejected_items": 1,
                                "omitted_items": 1, "raw_tables": 1, "emitted_tables": 0,
                                "rejected_tables": 1, "chunks": 1}
    assert {r["candidate_id"] for r in report["rejections"]} == {"text-2", "table-0"}
    assert report["rejections"][1]["evidence"]["raw_table_json"] == candidates.tables[0].raw_table_json
    assert report["item_omissions"][0]["raw_text"] == ""
    assert [p["physical_page"] for p in report["page_map"]] == [1, 2, 3]
    assert report["page_map"][0]["printed_page_label"] == "iv"
    assert report["conversion"] == metadata and report["tool_versions"] == {"docling": "stub"}
    assert report["review_needs"] and report["conflicts"] == []


@pytest.mark.parametrize("damage", ["coverage", "rejections", "source", "hash", "cap", "chunk_id"])
def test_report_refuses_incomplete_or_forged_results(bound, damage):
    _, _, version = bound
    candidates = policy_text.read_policy_items(raw_document([item("rule")]), version)
    result = chunks_module().build_policy_chunks(candidates)
    if damage == "coverage":
        result = replace(result, item_coverage=())
    elif damage == "rejections":
        result = replace(result, rejections=(chunks_module().ChunkRejection("text-0", "unlocated"),))
    elif damage == "source":
        result = replace(result, byte_sha256="f" * 64)
    elif damage == "cap":
        result = replace(result, token_cap=999)
    else:
        chunk = result.chunks[0]
        fields = dict(chunk.__dict__)
        fields["content_hash" if damage == "hash" else "chunk_id"] = "f" * 64
        result = replace(result, chunks=(type(chunk).model_construct(**fields),))
    with pytest.raises(ValueError):
        report_module().build_ingestion_report(candidates, result)


def test_pptx_report_retains_slide_and_table_rejections(bound):
    _, _, version = bound
    candidates = procedure_text.read_procedure_items(raw_document([item("slide", page=2)], [table(["cell"])]),
                                                     version, source_format="pptx")
    report = report_module().build_ingestion_report(candidates, chunks_module().build_policy_chunks(candidates))
    assert report["page_map"] == []
    assert report["counts"]["raw_items"] == report["counts"]["rejected_items"] == 1
    assert report["rejections"][0]["evidence"]["slide_index"] == 2
    assert "page" not in report["rejections"][0]["evidence"]


def test_table_parts_do_not_inflate_raw_counts(bound):
    _, _, version = bound
    candidates = procedure_text.read_procedure_items(raw_document([], [table(["Header", "row " * 30, "next " * 25])]), version)
    result = chunks_module().build_policy_chunks(candidates, token_cap=70)
    report = report_module().build_ingestion_report(candidates, result)
    assert report["counts"]["raw_tables"] == report["counts"]["emitted_tables"] == 1
    assert report["counts"]["chunks"] == 2 and report["counts"]["raw_items"] == 0


def pipeline_module():
    return importlib.import_module("backend.bintanong_tools.document_ingest.pipeline")


def stub_converter(monkeypatch, raw, snap, *, mutate=False):
    doc = SimpleNamespace(export_to_dict=lambda: raw, export_to_markdown=lambda: "synthetic")
    monkeypatch.setattr(loader, "load_docling", lambda: {
        "DoclingDocument": SimpleNamespace(model_validate=lambda data: doc)})
    def convert(stream):
        assert stream.stream.read() == snap.data
        if mutate:
            snap.path.write_bytes(b"changed")
        return SimpleNamespace(document=doc, errors=[])
    return SimpleNamespace(convert=convert)


def test_pipeline_snapshot_conversion_policy_table_chunks_and_report(bound, tmp_path, monkeypatch):
    root, snap, version = bound
    raw = raw_document([item("Scope", label="section_header"), item("No fee–²")], [table(["Fee", "None"])])
    out = tmp_path / "bundle"
    report = pipeline_module().run_ingestion(snap, [version], input_root=root, out=out,
        classification="policy_candidate", converter=stub_converter(monkeypatch, raw, snap))
    assert report["counts"]["raw_tables"] == report["counts"]["emitted_tables"] == 1
    assert report["counts"]["chunks"] == 3 and report["accounting_complete"]
    assert sorted(p.name for p in root.iterdir()) == [snap.path.name]
    manifest = json.loads((out / "manifest.json").read_text())
    assert manifest["complete"] and manifest["source_unchanged"]
    from backend.bintanong_tools.prospectus_extractor.identity import bytes_sha256
    for name, digest in manifest["files"].items():
        assert bytes_sha256((out / name).read_bytes()) == digest
    assert json.loads((out / "ingestion_report.json").read_text(encoding="utf-8")) == report
    assert not list(out.rglob("*.pl")) and snap.path.read_bytes() == snap.data


@pytest.mark.parametrize("damage", ["source", "register", "inside_root", "inside_git", "nonempty", "classification"])
def test_pipeline_preflight_and_mutation_no_complete_bundle(bound, tmp_path, monkeypatch, damage):
    root, snap, version = bound
    out = tmp_path / "bundle"
    records, kind = [version], "policy_candidate"
    calls = []
    converter = stub_converter(monkeypatch, raw_document([item("rule")]), snap, mutate=damage == "source")
    if damage == "register":
        record = version.model_dump(mode="json")
        record["approval_id"] = "approval-injected"
        records = [record]
    elif damage == "inside_root":
        out = root / "bundle"
    elif damage == "inside_git":
        (tmp_path / ".git").write_text("gitdir: synthetic")
    elif damage == "nonempty":
        out.mkdir()
        (out / "keep").write_text("keep")
    elif damage == "classification":
        kind = "approved_policy"
    if damage != "source":
        converter = SimpleNamespace(convert=lambda *_: calls.append("reached"))
    with pytest.raises(ValueError):
        pipeline_module().run_ingestion(snap, records, input_root=root, out=out,
                                       classification=kind, converter=converter)
    assert not (out / "manifest.json").exists() and not calls


def test_pipeline_last_source_check_and_failed_publication(bound, tmp_path, monkeypatch):
    root, snap, version = bound
    converter = stub_converter(monkeypatch, raw_document([item("rule")]), snap)
    write = loader._write_bytes_atomic
    def mutate(path, data):
        write(path, data)
        if path.name == "ingestion_report.json":
            snap.path.write_bytes(b"changed after report")
    monkeypatch.setattr(loader, "_write_bytes_atomic", mutate)
    out = tmp_path / "bundle"
    with pytest.raises(ValueError, match="changed"):
        pipeline_module().run_ingestion(snap, [version], input_root=root, out=out,
                                       classification="procedure_candidate", converter=converter)
    assert not (out / "manifest.json").exists()


@pytest.mark.parametrize("damage", ["raw", "metadata", "candidate", "write_failure"])
def test_pipeline_tamper_or_write_failure_never_completes(bound, tmp_path, monkeypatch, damage):
    root, snap, version = bound
    converter = stub_converter(monkeypatch, raw_document([item("rule")]), snap)
    mod = pipeline_module()
    extract = mod.extract_procedure
    def tamper(*args, **kwargs):
        candidates = extract(*args, **kwargs)
        if damage != "write_failure":
            filename = {"raw": "raw_docling.json", "metadata": "raw_docling.meta.json",
                        "candidate": "procedure_candidates.json"}[damage]
            target = kwargs["out"] / filename
            target.write_bytes(b"{}")
        return candidates
    monkeypatch.setattr(mod, "extract_procedure", tamper)
    write = loader._write_bytes_atomic
    def fail(path, data):
        if damage == "write_failure" and path.name == "chunks.json":
            raise OSError("synthetic failed publication")
        return write(path, data)
    monkeypatch.setattr(loader, "_write_bytes_atomic", fail)
    out = tmp_path / "bundle"
    with pytest.raises((ValueError, OSError)):
        mod.run_ingestion(snap, [version], input_root=root, out=out,
                          classification="policy_candidate", converter=converter)
    assert not (out / "manifest.json").exists()


def test_module_cli_help_has_explicit_required_inputs(capsys):
    cli = importlib.import_module("backend.bintanong_tools.document_ingest.__main__")
    with pytest.raises(SystemExit) as exited:
        cli.main(["--help"])
    assert exited.value.code == 0
    help_text = capsys.readouterr().out
    assert all(flag in help_text for flag in ("--root", "--out", "--locator", "--classification"))
