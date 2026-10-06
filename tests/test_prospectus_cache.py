"""The raw Docling JSON cache is reused only for the same PDF bytes and the same conversion settings."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.bintanong_tools.prospectus_extractor import identity, loader

pytestmark = pytest.mark.usefixtures("fake_docling", "pipeline_state")


def test_unchanged_pdf_reuses_the_cache(tmp_path, pdf_factory, converter, process):
    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    process(pdf, out, converter, force_reconvert=False)
    process(pdf, out, converter, force_reconvert=False)
    assert len(converter.calls) == 1


def test_same_path_with_changed_bytes_reconverts(tmp_path, pdf_factory, converter, process):
    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    process(pdf, out, converter, force_reconvert=False)
    pdf.write_bytes(b"%PDF-two")
    process(pdf, out, converter, force_reconvert=False)
    assert len(converter.calls) == 2
    raw = json.loads((out / "a_docling.json").read_text(encoding="utf-8"))
    assert raw["marker"] == "%PDF-two"


@pytest.mark.parametrize(
    "damage", ["wrong_identity", "old_format", "raw_tampered", "meta_missing", "meta_garbage"]
)
def test_cache_with_mismatching_identity_is_ignored(
    damage, tmp_path, pdf_factory, converter, process
):
    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    process(pdf, out, converter, force_reconvert=False)
    raw_path = out / "a_docling.json"
    meta_path = out / "a_docling.meta.json"
    if damage == "wrong_identity":
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["conversion_identity"] = "0" * 64
        meta_path.write_text(json.dumps(meta), encoding="utf-8")
    elif damage == "old_format":  # what the code wrote before Phase D
        meta_path.write_text(
            json.dumps({"profile": "palsu-born-digital-v3", "docling": "t1", "cell_matching": "true"}),
            encoding="utf-8",
        )
    elif damage == "raw_tampered":
        raw_path.write_text(raw_path.read_text(encoding="utf-8") + " ", encoding="utf-8")
    elif damage == "meta_missing":
        meta_path.unlink()
    else:
        meta_path.write_text("{not json", encoding="utf-8")
    process(pdf, out, converter, force_reconvert=False)
    assert len(converter.calls) == 2


def test_changed_cell_matching_setting_invalidates_the_cache(
    tmp_path, monkeypatch, pdf_factory, converter, process
):
    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    process(pdf, out, converter, force_reconvert=False)
    monkeypatch.setenv("PALSU_DOCLING_CELL_MATCHING", "false")
    process(pdf, out, converter, force_reconvert=False)
    assert len(converter.calls) == 2


def test_born_digital_cache_is_never_reused_for_an_ocr_run(
    tmp_path, monkeypatch, pdf_factory, converter, process
):
    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    process(pdf, out, converter, force_reconvert=False)
    monkeypatch.setattr(loader, "conversion_settings",
                        lambda: identity.conversion_settings(do_ocr=True, ocr_languages=["en", "fil"]))
    process(pdf, out, converter, force_reconvert=False)
    assert len(converter.calls) == 2
    meta = json.loads((out / "a_docling.meta.json").read_text(encoding="utf-8"))
    assert meta["conversion_settings"]["do_ocr"] is True


def test_cache_record_names_the_pdf_and_the_json_it_guards(tmp_path, pdf_factory, converter, process):
    import hashlib

    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    process(pdf, out, converter, force_reconvert=False)
    meta = json.loads((out / "a_docling.meta.json").read_text(encoding="utf-8"))
    assert meta["identity_version"] == identity.IDENTITY_VERSION
    assert meta["pdf_sha256"] == hashlib.sha256(b"%PDF-one").hexdigest()
    assert meta["raw_json_sha256"] == identity.file_sha256(out / "a_docling.json")
    assert meta["conversion_identity"] == identity.conversion_identity(
        meta["pdf_sha256"], meta["conversion_settings"])


# --- D-1: a shared converter is keyed by every conversion setting, not only device and backend.

from types import SimpleNamespace

from backend.bintanong_tools.prospectus_extractor import docling_env


@pytest.fixture
def fake_converter_factory(monkeypatch):
    """docling_env with fake Docling classes: a 'converter' records the settings its options came from."""
    fake = {
        "DocumentConverter": lambda format_options: SimpleNamespace(format_options=format_options),
        "PdfFormatOption": lambda pipeline_options, backend: SimpleNamespace(
            pipeline_options=pipeline_options, backend=backend),
        "InputFormat": SimpleNamespace(PDF="pdf"),
        "PyPdfiumDocumentBackend": "pypdfium",
        "DoclingParseV4DocumentBackend": "docling-parse",
    }
    monkeypatch.setattr(docling_env, "load_docling", lambda: fake)
    monkeypatch.setattr(docling_env, "_SHARED_CONVERTERS", {})
    monkeypatch.setattr(
        docling_env, "get_pipeline_options",
        lambda device="auto", settings=None: SimpleNamespace(
            settings=dict(settings if settings is not None else identity.conversion_settings())),
    )

    def built_with(converter):
        return converter.format_options["pdf"].pipeline_options.settings

    return built_with


def test_shared_converter_is_rebuilt_when_a_setting_changes(monkeypatch, fake_converter_factory):
    built_with = fake_converter_factory
    monkeypatch.setenv("PALSU_DOCLING_CELL_MATCHING", "true")
    first = docling_env.get_shared_converter("cpu")
    monkeypatch.setenv("PALSU_DOCLING_CELL_MATCHING", "false")
    second = docling_env.get_shared_converter("cpu")
    assert second is not first
    assert built_with(first)["cell_matching"] is True
    assert built_with(second)["cell_matching"] is False
    assert docling_env.get_shared_converter("cpu") is second


def test_shared_converter_honours_explicit_settings(fake_converter_factory):
    built_with = fake_converter_factory
    plain = docling_env.get_shared_converter("cpu")
    ocr_settings = identity.conversion_settings(do_ocr=True, ocr_languages=["en"])
    ocr = docling_env.get_shared_converter("cpu", settings=ocr_settings)
    assert ocr is not plain
    assert built_with(ocr) == ocr_settings
    assert docling_env.get_shared_converter("cpu", settings=dict(ocr_settings)) is ocr


def test_loader_asks_for_a_converter_built_with_the_settings_it_records(
    tmp_path, monkeypatch, pdf_factory, converter, process
):
    requests = []

    def shared(**kwargs):
        requests.append(kwargs)
        return converter

    monkeypatch.setattr(loader, "get_shared_converter", shared)
    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    process(pdf, out, None, force_reconvert=False)
    meta = json.loads((out / "a_docling.meta.json").read_text(encoding="utf-8"))
    assert requests and requests[0].get("settings") == meta["conversion_settings"]


# --- D-2: every write has its own temp file beside the target; a locked target is retried, then refused cleanly.

import os


def test_interleaved_writers_to_one_target_do_not_share_a_temp_file(tmp_path, monkeypatch):
    target = tmp_path / "cache" / "a_docling.json"
    real_replace = os.replace
    sources = []

    def replace(src, dst):
        sources.append(Path(src))
        if len(sources) == 1:  # writer A paused between its write and its replace; writer B runs fully
            loader._write_bytes_atomic(target, b"B")
        return real_replace(src, dst)

    monkeypatch.setattr(os, "replace", replace)
    loader._write_bytes_atomic(target, b"A")
    assert target.read_bytes() == b"A"
    assert len(sources) == 2 and sources[0] != sources[1]
    assert all(source.parent == target.parent for source in sources)
    assert sorted(path.name for path in target.parent.iterdir()) == ["a_docling.json"]


def test_a_briefly_locked_target_is_retried(tmp_path, monkeypatch):
    import time

    target = tmp_path / "a_docling.json"
    real_replace = os.replace
    failures = []

    def replace(src, dst):
        if len(failures) < 2:
            failures.append(dst)
            raise PermissionError(13, "The process cannot access the file", str(dst))
        return real_replace(src, dst)

    monkeypatch.setattr(os, "replace", replace)
    monkeypatch.setattr(time, "sleep", lambda _seconds: None)
    loader._write_bytes_atomic(target, b"new")
    assert target.read_bytes() == b"new"
    assert len(failures) == 2


def test_a_target_that_stays_locked_raises_a_clean_error_and_leaves_no_temp(tmp_path, monkeypatch):
    import time

    target = tmp_path / "a_docling.json"
    target.write_bytes(b"old")

    def replace(src, dst):
        raise PermissionError(13, "The process cannot access the file", str(dst))

    monkeypatch.setattr(os, "replace", replace)
    monkeypatch.setattr(time, "sleep", lambda _seconds: None)
    with pytest.raises(loader.ReplaceFailed, match="could not replace .*a_docling.json"):
        loader._write_bytes_atomic(target, b"new")
    assert target.read_bytes() == b"old"
    assert sorted(path.name for path in tmp_path.iterdir()) == ["a_docling.json"]
