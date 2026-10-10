"""Checked candidate consumption, with synthetic producer/CLI integration."""
import importlib
import json
from pathlib import Path

import pytest

from backend.bintanong_tools.prospectus_extractor import loader
from backend.bintanong_tools.prospectus_extractor.identity import bytes_sha256
from test_prospectus_ingestion import prospectus_input, runner, synthetic_converter
from test_policy_chunks import item, raw_document


def consumer():
    spec = importlib.util.find_spec("backend.bintanong_tools.document_ingest.bundle")
    assert spec is not None, "checked candidate consumer is missing"
    return importlib.import_module(spec.name).load_candidate_bundle


def publish(prospectus_input, tmp_path, monkeypatch):
    root, snap, version = prospectus_input
    out = tmp_path / "bundle"
    runner()(snap, [version], input_root=root, out=out, converter=synthetic_converter(monkeypatch, snap))
    return out


def replace_artifact(out, name, change):
    """Rehash intentionally so binding checks, rather than only digests, are exercised."""
    target = out / name
    data = json.loads(target.read_bytes())
    change(data)
    target.write_text(json.dumps(data), encoding="utf-8")
    manifest = json.loads((out / "manifest.json").read_bytes())
    manifest["files"][name] = bytes_sha256(target.read_bytes())
    (out / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


@pytest.mark.parametrize("attack", ["raw", "settings", "source", "foreign_span", "null_span", "duplicate_chunk",
    "private", "unknown_file", "unknown_kind", "escaping", "duplicate_key", "root_false", "nested_false", "nested_only", "extra_disk"])
def test_consumer_refuses_altered_or_incomplete_bundles(prospectus_input, tmp_path, monkeypatch, attack):
    out = publish(prospectus_input, tmp_path, monkeypatch)
    load = consumer()
    if attack in {"raw", "settings"}:
        target = out / "conversion" / ("raw_docling.json" if attack == "raw" else "raw_docling.meta.json")
        data = json.loads(target.read_bytes())
        if attack == "raw":
            data["texts"][0]["text"] = "changed"
        else:
            data["conversion_settings"]["backend"] = "changed"
        target.write_text(json.dumps(data), encoding="utf-8")
    elif attack in {"foreign_span", "null_span", "duplicate_chunk"}:
        def mutate(data):
            if attack == "duplicate_chunk":
                data["chunks"].append(data["chunks"][0])
            else:
                data["chunks"][0]["spans"][0]["version_id"] = "ver-foreign" if attack == "foreign_span" else None
        replace_artifact(out, "chunks.json", mutate)
    elif attack == "private":
        replace_artifact(out, "source_register.json", lambda data: data[0].update(namespace="private"))
    elif attack == "nested_false":
        replace_artifact(out, "conversion/manifest.json", lambda data: data.update(complete=False))
    elif attack == "nested_only":
        (out / "manifest.json").unlink()
    elif attack == "extra_disk":
        (out / "not-listed.json").write_text("{}")
    else:
        path = out / "manifest.json"
        data = json.loads(path.read_bytes())
        if attack == "root_false":
            data["complete"] = False
        elif attack == "source":
            data["source_sha256"] = "b" * 64
        elif attack == "unknown_kind":
            data["document_kind"] = "private_upload"
        elif attack in {"unknown_file", "escaping"}:
            data["files"]["../outside.json" if attack == "escaping" else "unknown.json"] = "b" * 64
        if attack == "duplicate_key":
            text = json.dumps(data)
            text = text[:-1] + ', "files": ' + json.dumps(data["files"]) + "}"
        else:
            text = json.dumps(data)
        path.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError):
        load(out)


def test_symlink_artifact_refused(prospectus_input, tmp_path, monkeypatch):
    out = publish(prospectus_input, tmp_path, monkeypatch)
    target = out / "chunks.json"
    outside = tmp_path / "outside.json"
    outside.write_bytes(target.read_bytes())
    target.unlink()
    try:
        target.symlink_to(outside)
    except OSError as exc:
        pytest.skip(f"symlink creation unavailable: {exc}")
    with pytest.raises(ValueError, match="symlink|regular|contain"):
        consumer()(out)


def test_interrupted_publication_never_consumed_or_implicitly_retried(prospectus_input, tmp_path, monkeypatch):
    root, snap, version = prospectus_input
    out = tmp_path / "interrupted"
    write = loader._write_bytes_atomic
    def interrupt(path, data):
        if path.name == "chunks.json":
            raise OSError("synthetic interruption")
        write(path, data)
    monkeypatch.setattr(loader, "_write_bytes_atomic", interrupt)
    converter = synthetic_converter(monkeypatch, snap)
    with pytest.raises(OSError):
        runner()(snap, [version], input_root=root, out=out, converter=converter)
    assert not (out / "manifest.json").exists()
    with pytest.raises(ValueError):
        consumer()(out)
    with pytest.raises(ValueError, match="empty"):
        runner()(snap, [version], input_root=root, out=out, converter=converter)
    assert len(converter.calls) == 1


@pytest.mark.parametrize("kind", ["policy_candidate", "procedure_candidate", "charter_candidate", "form", "curriculum_proposal_candidate"])
def test_existing_generic_manifest_without_kind_is_checked(prospectus_input, tmp_path, monkeypatch, kind):
    from backend.bintanong_tools.document_ingest.pipeline import run_ingestion
    root, snap, version = prospectus_input
    out = tmp_path / kind
    raw = raw_document([item("Printed fee: none")], pages=1)
    report = run_ingestion(snap, [version], input_root=root, out=out, classification=kind,
                          converter=synthetic_converter(monkeypatch, snap, raw))
    checked = consumer()(out)
    assert checked["document_kind"] == kind and checked["report"] == report
    assert len(checked["chunks"]) == 1 and checked["review_eligible"] is False


def test_combined_synthetic_cli_library_smoke(prospectus_input, tmp_path, monkeypatch, capsys):
    """Stable root smoke: pytest this node; both routes run real readers and consumer."""
    cli = importlib.import_module("backend.bintanong_tools.document_ingest.__main__")
    mod = importlib.import_module("backend.bintanong_tools.document_ingest.prospectus")
    generic = importlib.import_module("backend.bintanong_tools.document_ingest.pipeline")
    root, snap, _ = prospectus_input
    run_p, run_g = runner(), generic.run_ingestion
    monkeypatch.setattr(mod, "run_prospectus_ingestion", lambda *args, **kwargs: run_p(*args, **kwargs,
        converter=synthetic_converter(monkeypatch, snap)))
    monkeypatch.setattr(generic, "run_ingestion", lambda *args, **kwargs: run_g(*args, **kwargs,
        converter=synthetic_converter(monkeypatch, snap, raw_document([item("Printed rule")], pages=1))))
    for kind in ("prospectus_candidate", "policy_candidate"):
        out = tmp_path / kind
        assert cli.main([str(snap.path), "--root", str(root), "--out", str(out),
                         "--locator", "shelf:synthetic", "--classification", kind]) == 0
        summary = json.loads(capsys.readouterr().out)
        checked = consumer()(out)
        assert summary["counts"] == checked["report"]["counts"] and summary["candidate_only"] is True


def test_help_does_not_initialize_converter(monkeypatch, capsys):
    monkeypatch.setattr(loader, "get_shared_converter", lambda **_: pytest.fail("help initialized converter"))
    cli = importlib.import_module("backend.bintanong_tools.document_ingest.__main__")
    with pytest.raises(SystemExit) as exited:
        cli.main(["--help"])
    assert exited.value.code == 0 and "prospectus_candidate" in capsys.readouterr().out


@pytest.mark.parametrize("attack", ["settings", "raw", "nested_source", "nested_settings", "metadata_status", "page_sizes"])
def test_rehashed_conversion_attacks_still_refuse(prospectus_input, tmp_path, monkeypatch, attack):
    out = publish(prospectus_input, tmp_path, monkeypatch)
    filename = "raw_docling.json" if attack == "raw" else "manifest.json" if attack.startswith("nested") else "raw_docling.meta.json"
    def mutate(data):
        if attack == "settings":
            data["conversion_settings"]["backend"] = "changed"
        elif attack == "raw":
            data["texts"][0]["text"] = "changed"
        elif attack == "nested_source":
            data["source_sha256"] = "b" * 64
        elif attack == "nested_settings":
            data["conversion_identity"] = "b" * 64
        elif attack == "metadata_status":
            data["conversion_status"] = "partial_success"
        else:
            data["pdf_page_sizes"] = {"1": []}
    replace_artifact(out, f"conversion/{filename}", mutate)
    if filename != "manifest.json":
        digest = bytes_sha256((out / "conversion" / filename).read_bytes())
        replace_artifact(out, "conversion/manifest.json", lambda data: data["files"].update({filename: digest}))
    with pytest.raises(ValueError):
        consumer()(out)


def test_cli_failure_from_checked_consumer_has_no_success_summary(prospectus_input, tmp_path, monkeypatch, capsys):
    cli = importlib.import_module("backend.bintanong_tools.document_ingest.__main__")
    mod = importlib.import_module("backend.bintanong_tools.document_ingest.prospectus")
    root, snap, version = prospectus_input
    out = tmp_path / "bundle"
    run = runner()
    def tamper(*args, **kwargs):
        report = run(*args, **kwargs, converter=synthetic_converter(monkeypatch, snap))
        (kwargs["out"] / "chunks.json").write_text("{}")
        return report
    monkeypatch.setattr(mod, "run_prospectus_ingestion", tamper)
    assert cli.main([str(snap.path), "--root", str(root), "--out", str(out), "--locator", "shelf:synthetic",
                     "--classification", "prospectus_candidate"]) == 1
    captured = capsys.readouterr()
    assert captured.out == "" and "Ingestion incomplete" in captured.err


def test_blocked_audit_still_requires_captured_page_geometry(prospectus_input, tmp_path, monkeypatch):
    from test_prospectus_ingestion import synthetic_prospectus
    root, snap, version = prospectus_input
    raw = synthetic_prospectus()
    raw["tables"] = []
    out = tmp_path / "blocked"
    runner()(snap, [version], input_root=root, out=out, converter=synthetic_converter(monkeypatch, snap, raw))
    assert consumer()(out)["conversion"]["metadata"]["pdf_page_sizes"] == {"1": [612.0, 792.0]}
    replace_artifact(out, "conversion/raw_docling.meta.json", lambda data: data.update(pdf_page_sizes={}))
    digest = bytes_sha256((out / "conversion/raw_docling.meta.json").read_bytes())
    replace_artifact(out, "conversion/manifest.json", lambda data: data["files"].update({"raw_docling.meta.json": digest}))
    # Preserve report agreement so a geometry refusal cannot be hidden by a report mismatch.
    replace_artifact(out, "ingestion_report.json", lambda data: data["conversion"].update(pdf_page_sizes={}))
    with pytest.raises(ValueError, match="geometry|size"):
        consumer()(out)
