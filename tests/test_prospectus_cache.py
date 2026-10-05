"""The raw Docling JSON cache is reused only for the same PDF bytes and the same conversion settings."""

from __future__ import annotations

import json

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
