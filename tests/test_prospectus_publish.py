"""Staging, file-by-file publication, publish manifest, failure diagnostics."""

from __future__ import annotations

import codecs
import csv
import io
import json

import pytest

from backend.bintanong_tools.prospectus_extractor import publish, views

IDENTITY = {"run_key": "a" * 64, "input_kind": "docling-json",
            "input_sha256": "b" * 64, "pdf_sha256": None,
            "conversion_identity": None, "conversion_settings": None, "cache_files": {}}


def stage_files(stage, contents: dict[str, str]):
    stage.mkdir(parents=True, exist_ok=True)
    for name, text in contents.items():
        if name.endswith("_prospectus.json"):
            text = json.dumps({"run_identity": IDENTITY, "marker": text})
        publish.write_text_lf(stage / name, text)


@pytest.mark.parametrize("title", [
    "Sining, kultura – ñ",
    "Sining, kultura\r\nWikang Filipino – ñ",
    "Sining\rWikang Filipino – ñ",
])
def test_review_csv_uses_lf_records_and_preserves_bom_columns_and_field_data(tmp_path, title):
    path = tmp_path / "out" / "a_review.csv"
    views.write_review_csv([{
        "year_level": "FIRST YEAR", "semester": "FIRST SEMESTER", "course_code": "FIL 1",
        "course_title": title, "total_units": 3, "lecture_units": 3, "lab_units": 0,
        "prerequisites": ["GE 1", "GE 2"], "prerequisites_unresolved": ["ñ"],
        "standing_requirements": ["First year", "Approved"], "category": "GE",
        "elective_group": "Wika", "prerequisites_raw": "GE 1, GE 2", "title_raw": "Wikang ñ",
        "footnote_marker": "*", "_source": {"table_index": 0, "row_index": 1, "column_group": 2},
        "provenance": {"source_cell_ids": ["c1", "c2"], "page": 0, "bbox": [1, 2, 3, 4],
                       "resolution_method": "reviewed", "repair_id": "r1"},
    }], path)

    raw = path.read_bytes()
    assert raw.startswith(codecs.BOM_UTF8)
    assert title.encode("utf-8") in raw
    record_bytes = raw.replace(title.encode("utf-8"), b"")
    assert b"\r" not in record_bytes
    assert record_bytes.count(b"\n") == 2
    assert raw.endswith(b"\n")
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    expected = {
        "year_level": "FIRST YEAR", "semester": "FIRST SEMESTER", "course_code": "FIL 1",
        "course_title": title, "units_total": "3", "units_lecture": "3", "units_lab": "0",
        "prerequisites_resolved": "GE 1, GE 2", "prerequisites_unresolved": "ñ",
        "standing_requirements": "First year | Approved", "category": "GE", "elective_group": "Wika",
        "prerequisites_raw": "GE 1, GE 2", "title_raw": "Wikang ñ", "footnote_marker": "*",
        "table_index": "0", "row_index": "1", "column_group": "2", "source_cell_ids": "c1 | c2",
        "page": "0", "bbox": "[1, 2, 3, 4]", "resolution_method": "reviewed", "repair_id": "r1",
    }
    assert reader.fieldnames == list(expected)
    assert list(reader) == [expected]


def test_output_names_match_the_historical_companion_names(tmp_path):
    names = publish.output_names(tmp_path / "out" / "bscs_prospectus.json")
    assert names.base == "bscs"
    assert names.essentials.name == "bscs_essentials.json"
    assert names.prolog.name == "bscs_prospectus.pl"
    assert names.rag.name == "bscs_rag.jsonl"
    assert names.csv.name == "bscs_review.csv"
    assert names.markup.name == "bscs_prospectus.md"  # Phase B markup twin
    assert names.manifest.name == "bscs_publish.json"
    assert names.failed_dir == tmp_path / "out" / "failed" / "bscs"


def test_publish_replaces_existing_files_and_writes_the_manifest_last(tmp_path, monkeypatch):
    names = publish.output_names(tmp_path / "out" / "a_prospectus.json")
    names.final.parent.mkdir(parents=True)
    names.final.write_text("old main", encoding="utf-8")
    names.csv.write_text("old csv", encoding="utf-8")
    stage = tmp_path / "out" / ".a.staging-x"
    stage_files(stage, {"a_review.csv": "new csv", "a_prospectus.json": "new main"})

    order = []
    real = publish.replace_file
    monkeypatch.setattr(publish, "replace_file",
                        lambda source, target, *a, **k: (order.append(target.name), real(source, target, *a, **k)))
    publish.publish_staged(stage, names, ["a_review.csv", "a_prospectus.json"], [], IDENTITY, "ok")

    assert order == ["a_review.csv", "a_prospectus.json", "a_publish.json"]
    assert json.loads(names.final.read_bytes())["marker"] == "new main"
    manifest = publish.read_manifest(names.manifest)
    assert manifest["run_key"] == IDENTITY["run_key"]
    assert manifest["audit_status"] == "ok"
    assert sorted(manifest["files"]) == ["a_prospectus.json", "a_review.csv"]
    assert publish.verify_published(names.final.parent, manifest) == (True, "all files match")


def test_main_json_must_be_the_last_output(tmp_path):
    names = publish.output_names(tmp_path / "out" / "a_prospectus.json")
    stage = tmp_path / "out" / ".a.staging-x"
    stage_files(stage, {"a_review.csv": "c", "a_prospectus.json": "m"})
    with pytest.raises(ValueError, match="main JSON"):
        publish.publish_staged(stage, names, ["a_prospectus.json", "a_review.csv"], [], IDENTITY, "ok")


def test_stale_companions_are_removed_but_cache_files_are_not(tmp_path):
    out = tmp_path / "out"
    names = publish.output_names(out / "a_prospectus.json")
    stage = out / ".a.staging-1"
    stage_files(stage, {"a_prospectus.pl": "pl", "a_prospectus.json": "m1"})
    publish.publish_staged(stage, names, ["a_prospectus.pl", "a_prospectus.json"], [], IDENTITY, "ok")
    (out / "a_docling.json").write_text("cache", encoding="utf-8")  # cache is not a manifest output

    stage2 = out / ".a.staging-2"
    stage_files(stage2, {"a_prospectus.json": "m2"})
    publish.publish_staged(stage2, names, ["a_prospectus.json"], [], IDENTITY, "error")

    assert not (out / "a_prospectus.pl").exists()
    assert (out / "a_docling.json").read_text(encoding="utf-8") == "cache"
    assert publish.read_manifest(names.manifest)["audit_status"] == "error"


def test_manifest_cannot_make_publish_delete_outside_the_output_folder(tmp_path):
    out = tmp_path / "out"
    names = publish.output_names(out / "a_prospectus.json")
    out.mkdir()
    victim = tmp_path / "victim.txt"
    victim.write_text("keep", encoding="utf-8")
    names.manifest.write_text(json.dumps({
        "schema": publish.PUBLISH_SCHEMA, "run_key": "x", "audit_status": "ok",
        "files": {"../victim.txt": "0" * 64},
    }), encoding="utf-8")
    stage = out / ".a.staging-1"
    stage_files(stage, {"a_prospectus.json": "m"})
    publish.publish_staged(stage, names, ["a_prospectus.json"], [], IDENTITY, "ok")
    assert victim.read_text(encoding="utf-8") == "keep"


def test_verify_detects_a_changed_or_missing_file(tmp_path):
    out = tmp_path / "out"
    names = publish.output_names(out / "a_prospectus.json")
    stage = out / ".a.staging-1"
    stage_files(stage, {"a_review.csv": "c", "a_prospectus.json": "m"})
    publish.publish_staged(stage, names, ["a_review.csv", "a_prospectus.json"], [], IDENTITY, "ok")
    manifest = publish.read_manifest(names.manifest)

    names.final.write_text("edited", encoding="utf-8")
    ok, why = publish.verify_published(out, manifest)
    assert (ok, why) == (False, "a_prospectus.json changed since it was published")

    names.csv.unlink()
    ok, why = publish.verify_published(out, manifest)
    assert (ok, why) == (False, "a_review.csv is missing")


def test_read_manifest_rejects_garbage(tmp_path):
    path = tmp_path / "a_publish.json"
    assert publish.read_manifest(path) is None
    path.write_text("{nope", encoding="utf-8")
    assert publish.read_manifest(path) is None
    path.write_text(json.dumps({"schema": "other"}), encoding="utf-8")
    assert publish.read_manifest(path) is None


def test_write_failure_keeps_staged_files_and_clears_the_previous_diagnostics(tmp_path):
    out = tmp_path / "out"
    names = publish.output_names(out / "a_prospectus.json")
    names.failed_dir.mkdir(parents=True)
    (names.failed_dir / "old_docling.json").write_text("old", encoding="utf-8")
    stage = out / ".a.staging-1"
    stage_files(stage, {"a_docling.json": "converted"})

    try:
        raise ValueError("parser blew up")
    except ValueError as error:
        directory = publish.write_failure(names, error, tmp_path / "in" / "a.pdf", {"run_key": "k"}, stage)

    assert directory == names.failed_dir
    assert not (directory / "old_docling.json").exists()
    assert (directory / "a_docling.json").read_text(encoding="utf-8") == "converted"
    record = json.loads((directory / "failure.json").read_text(encoding="utf-8"))
    assert record["error_type"] == "ValueError"
    assert record["error_message"] == "parser blew up"
    assert "Traceback" in record["traceback"]
    assert record["run_identity"] == {"run_key": "k"}

    publish.clear_failure(names)
    assert not names.failed_dir.exists()


def test_stale_staging_directories_are_removed_for_the_same_base_only(tmp_path):
    out = tmp_path / "out"
    (out / ".a.staging-dead").mkdir(parents=True)
    (out / ".b.staging-live").mkdir()
    stage = publish.new_staging_dir(out, "a")
    assert not (out / ".a.staging-dead").exists()
    assert (out / ".b.staging-live").exists()
    assert stage.parent == out and stage.name.startswith(".a.staging-") and stage.is_dir()


def test_markup_twin_is_published_before_the_main_json_and_removed_when_stale(tmp_path):
    out = tmp_path / "out"
    names = publish.output_names(out / "a_prospectus.json")
    stage = out / ".a.staging-1"
    stage_files(stage, {"a_prospectus.md": "md", "a_prospectus.json": "m1"})
    publish.publish_staged(stage, names, ["a_prospectus.md", "a_prospectus.json"], [], IDENTITY, "ok")
    assert names.markup.read_text(encoding="utf-8") == "md"
    stage2 = out / ".a.staging-2"
    stage_files(stage2, {"a_prospectus.json": "m2"})
    publish.publish_staged(stage2, names, ["a_prospectus.json"], [], IDENTITY, "ok")
    assert not names.markup.exists()


def test_the_cache_writer_and_publication_share_one_replace():
    from backend.bintanong_tools.prospectus_extractor import loader

    assert loader.replace_file is publish.replace_file
    assert loader.ReplaceFailed is publish.ReplaceFailed


def test_a_publish_target_that_stays_locked_keeps_the_staged_file_for_diagnostics(tmp_path, monkeypatch):
    import os
    import time

    out = tmp_path / "out"
    names = publish.output_names(out / "a_prospectus.json")
    out.mkdir()
    names.final.write_text("old main", encoding="utf-8")
    stage = out / ".a.staging-1"
    stage_files(stage, {"a_prospectus.json": "new main"})

    def locked(src, dst):
        raise PermissionError(13, "The process cannot access the file", str(dst))

    monkeypatch.setattr(os, "replace", locked)
    monkeypatch.setattr(time, "sleep", lambda _seconds: None)
    with pytest.raises(publish.ReplaceFailed, match="a_prospectus.json"):
        publish.publish_staged(stage, names, ["a_prospectus.json"], [], IDENTITY, "ok")
    assert json.loads((stage / "a_prospectus.json").read_bytes())["marker"] == "new main"
    assert names.final.read_text(encoding="utf-8") == "old main"
    assert not names.manifest.exists()



def valid_manifest():
    return {"schema": publish.PUBLISH_SCHEMA, "run_key": IDENTITY["run_key"],
            "run_identity": dict(IDENTITY), "main_file": "a_prospectus.json",
            "files": {"a_prospectus.json": "d" * 64}, "cache_files": {}}


BAD_NAMES = ["", ".", "..", "../victim", "..\\victim", "nested/file", "nested\\file",
             "C:/victim", "C:relative", "\\\\server\\share", "a:stream", "a.", "a ", "a\x00b"]


@pytest.mark.parametrize("name", BAD_NAMES)
def test_manifest_rejects_unsafe_leaf_names(tmp_path, name):
    manifest = valid_manifest()
    manifest["files"] = {name: "d" * 64}
    manifest["main_file"] = name
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    assert publish.read_manifest(path) is None
    assert publish.verify_published(tmp_path, manifest)[0] is False


@pytest.mark.parametrize("field,value", [
    ("schema", "palsu-prospectus-publish-v1"), ("files", {}), ("files", []), ("files", None),
    ("files", {"a_prospectus.json": None}), ("files", {"a_prospectus.json": "D" * 64}),
    ("files", {"a_prospectus.json": "g" * 64}), ("files", {"a_prospectus.json": 3}),
    ("run_key", "k" * 64), ("run_key", None), ("main_file", "absent.json"),
    ("main_file", None), ("cache_files", []), ("cache_files", None),
    ("cache_files", {"a_docling.json": "e" * 64}), ("run_identity", None),
    ("run_identity", []), ("run_identity", {"run_key": "b" * 64}),
])
def test_manifest_rejects_invalid_shape(tmp_path, field, value):
    manifest = valid_manifest()
    manifest[field] = value
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    assert publish.read_manifest(path) is None
    assert publish.verify_published(tmp_path, manifest)[0] is False


@pytest.mark.parametrize("root", [None, [], 1, "manifest"])
def test_manifest_root_fails_closed(tmp_path, root):
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(root), encoding="utf-8")
    assert publish.read_manifest(path) is None
    assert publish.verify_published(tmp_path, root)[0] is False


@pytest.mark.parametrize("field", ["input_kind", "cache_files", "run_key"])
def test_missing_identity_fields_fail_closed(tmp_path, field):
    manifest = valid_manifest()
    manifest["run_identity"].pop(field)
    assert publish.verify_published(tmp_path, manifest)[0] is False


@pytest.mark.parametrize("content", [b"\xff", b"{", b"[]", b"null", b"{}"])
def test_main_must_parse_and_bind_manifest_identity(tmp_path, content):
    import hashlib
    manifest = valid_manifest()
    (tmp_path / "a_prospectus.json").write_bytes(content)
    manifest["files"]["a_prospectus.json"] = hashlib.sha256(content).hexdigest()
    assert publish.verify_published(tmp_path, manifest)[0] is False


def test_unreadable_file_fails_closed(tmp_path, monkeypatch):
    from pathlib import Path
    manifest = valid_manifest()
    (tmp_path / "a_prospectus.json").write_bytes(b"{}")
    real = Path.read_bytes
    def denied(path):
        if path.name == "a_prospectus.json":
            raise PermissionError("locked")
        return real(path)
    monkeypatch.setattr(Path, "read_bytes", denied)
    assert publish.verify_published(tmp_path, manifest)[0] is False


def test_resolved_leaf_cannot_escape_directory(tmp_path, monkeypatch):
    from pathlib import Path
    manifest = valid_manifest()
    real = Path.resolve
    def escape(path, *args, **kwargs):
        if path.name == "a_prospectus.json":
            return tmp_path.parent / "victim.json"
        return real(path, *args, **kwargs)
    monkeypatch.setattr(Path, "resolve", escape)
    assert publish.verify_published(tmp_path, manifest)[0] is False


def test_stale_cleanup_keeps_arbitrary_previous_entries_and_cache(tmp_path):
    import hashlib
    out = tmp_path / "out"
    names = publish.output_names(out / "a_prospectus.json")
    out.mkdir()
    keep = ["a_docling.json", "a_docling.meta.json", "neighbor.txt"]
    for name in [*keep, "a_prospectus.pl"]:
        (out / name).write_bytes(b"keep")
    previous = valid_manifest()
    previous["files"].update({name: hashlib.sha256(b"keep").hexdigest() for name in keep})
    names.manifest.write_text(json.dumps(previous), encoding="utf-8")
    stage = out / ".stage"
    stage_files(stage, {"a_prospectus.json": "new"})
    publish.publish_staged(stage, names, ["a_prospectus.json"], [], IDENTITY, "ok")
    assert all((out / name).read_bytes() == b"keep" for name in keep)
    assert not names.prolog.exists()


@pytest.mark.parametrize("outputs,caches", [
    (["a_prospectus.json", "a_prospectus.json"], []),
    (["../victim", "a_prospectus.json"], []),
    (["a_publish.json", "a_prospectus.json"], []),
    (["a_prospectus.json"], ["a_prospectus.json"]),
])
def test_invalid_publish_names_refuse_before_any_replace(tmp_path, monkeypatch, outputs, caches):
    names = publish.output_names(tmp_path / "out" / "a_prospectus.json")
    stage = tmp_path / "stage"
    stage_files(stage, {"a_prospectus.json": "new"})
    def must_not_replace(*args, **kwargs):
        pytest.fail("invalid publication attempted a replace")
    monkeypatch.setattr(publish, "replace_file", must_not_replace)
    with pytest.raises(ValueError):
        publish.publish_staged(stage, names, outputs, caches, IDENTITY, "ok")



def test_invalid_utf8_manifest_is_rejected(tmp_path):
    path = tmp_path / "manifest.json"
    path.write_bytes(b"\xff")
    assert publish.read_manifest(path) is None
