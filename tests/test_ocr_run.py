"""Synthetic OCR adapter output; no installed engine is initialized."""
import importlib
import json
from pathlib import Path

import pytest
from PIL import Image
from reportlab.pdfgen import canvas

from backend.bintanong_tools.document_ingest.register import pending_version
from backend.bintanong_tools.ocr_bench import engines
from backend.bintanong_tools.prospectus_extractor.identity import InputSnapshot


@pytest.fixture
def runner():
    return importlib.import_module("backend.bintanong_tools.document_ingest.ocr_run")


@pytest.fixture
def source(tmp_path):
    root = tmp_path / "originals"
    root.mkdir()
    path = root / "poster.jpg"
    Image.new("RGB", (120, 80), "white").save(path)
    snapshot = InputSnapshot(path)
    return root, snapshot, [pending_version(snapshot, "shelf:ocr-test", synthetic=True)]


def fake_ocr(config, images, out):
    out.mkdir()
    for path in images.iterdir():
        (out / (path.stem + ".txt")).write_text("Shall not pay.\n", encoding="utf-8")
        (out / (path.stem + ".words.json")).write_text(json.dumps([
            {"text": "Shall not pay.", "conf": 41.25, "box": [1, 2, 110, 30]}]))
    (out / "ocr_run.json").write_text(json.dumps({"engine": config.engine,
        "config": config.id, "lang": config.lang, "engine_version": "stub-1",
        "device": "cpu", "images": len(list(images.iterdir())), "seconds": 0.01}))


@pytest.fixture
def stub(runner, monkeypatch):
    monkeypatch.setattr(runner, "_preflight_engine", lambda config: {"model": "synthetic-test"})
    monkeypatch.setattr(runner, "_run_adapter", fake_ocr)


def invoke(runner, source, tmp_path):
    root, snapshot, records = source
    return runner.run_document(snapshot, records, input_root=root, out=tmp_path / "out",
        config=engines.OcrConfig("tesseract-eng", "tesseract", "eng"))


def test_image_binding_raw_confidence_manifest_and_actual_metadata(runner, source, tmp_path, stub):
    result = invoke(runner, source, tmp_path)
    assert result["pages"][0]["binding"] == {"kind": "image", "image_index": 1}
    assert "page" not in result["pages"][0]["binding"]
    assert result["pages"][0]["words"][0]["conf"] == 41.25
    assert result["metadata"]["lang"] == "eng" and result["metadata"]["device"] == "cpu"
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_bytes())
    assert manifest["complete"] and manifest["source_unchanged"]
    assert "ocr_candidates.json" in manifest["files"]


def test_pdf_all_pages_have_physical_binding(runner, tmp_path, stub):
    root = tmp_path / "originals"
    root.mkdir()
    path = root / "scan.pdf"
    pdf = canvas.Canvas(str(path), pagesize=(120, 80))
    for _ in range(2):
        pdf.showPage()
    pdf.save()
    snapshot = InputSnapshot(path)
    result = invoke(runner, (root, snapshot, [pending_version(snapshot, "shelf:scan", synthetic=True)]), tmp_path)
    assert [p["binding"] for p in result["pages"]] == [
        {"kind": "pdf_page", "page": 1}, {"kind": "pdf_page", "page": 2}]


def test_missing_engine_records_not_run_and_raises(runner, source, tmp_path, monkeypatch):
    def missing(config):
        raise engines.EngineNotInstalled("no local model")
    monkeypatch.setattr(runner, "_preflight_engine", missing)
    with pytest.raises(engines.EngineNotInstalled):
        invoke(runner, source, tmp_path)
    record = json.loads((tmp_path / "out" / "ocr_run.json").read_bytes())
    assert record["evaluation"] == "NOT RUN"
    assert not (tmp_path / "out" / "manifest.json").exists()


def test_rapidocr_refused_before_initialization(runner, monkeypatch):
    monkeypatch.setattr(engines, "availability", lambda config: (True, "available"))
    with pytest.raises(engines.EngineNotInstalled, match="local-model"):
        runner._preflight_engine(engines.OcrConfig("rapidocr-en", "rapidocr", "en"))


def test_tesseract_checks_each_selected_traineddata(runner, tmp_path, monkeypatch):
    monkeypatch.setattr(engines, "availability", lambda config: (True, "available"))
    monkeypatch.setattr(engines, "find_tesseract", lambda: "tesseract")
    monkeypatch.setenv("TESSDATA_PREFIX", str(tmp_path))
    (tmp_path / "eng.traineddata").write_bytes(b"local-model")
    with pytest.raises(engines.EngineNotInstalled, match="fil"):
        runner._preflight_engine(engines.OcrConfig("tesseract-eng+fil", "tesseract", "eng+fil"))


@pytest.mark.parametrize("mutation", ["metadata", "language", "page", "text", "confidence", "box"])
def test_invalid_adapter_output_never_gets_completion_manifest(runner, source, tmp_path, stub, monkeypatch, mutation):
    def malformed(config, images, out):
        fake_ocr(config, images, out)
        metadata = json.loads((out / "ocr_run.json").read_bytes())
        if mutation == "metadata":
            del metadata["engine_version"]
        if mutation == "language":
            metadata["lang"] = "fil"
        (out / "ocr_run.json").write_text(json.dumps(metadata))
        if mutation == "page":
            next(out.glob("*.words.json")).unlink()
        if mutation == "text":
            next(out.glob("*.txt")).write_text("")
        if mutation in {"confidence", "box"}:
            path = next(out.glob("*.words.json"))
            words = json.loads(path.read_bytes())
            words[0]["conf" if mutation == "confidence" else "box"] = -1 if mutation == "confidence" else [0, 0, 10000, 20]
            path.write_text(json.dumps(words))
    monkeypatch.setattr(runner, "_run_adapter", malformed)
    with pytest.raises((ValueError, FileNotFoundError)):
        invoke(runner, source, tmp_path)
    assert not (tmp_path / "out" / "manifest.json").exists()


def test_source_mutation_fails_before_publication(runner, source, tmp_path, stub, monkeypatch):
    def changed(config, images, out):
        fake_ocr(config, images, out)
        source[1].path.write_bytes(b"changed")
    monkeypatch.setattr(runner, "_run_adapter", changed)
    with pytest.raises(ValueError, match="changed"):
        invoke(runner, source, tmp_path)
    assert not (tmp_path / "out" / "manifest.json").exists()


@pytest.mark.parametrize("location", ["input", "git", "nonempty"])
def test_output_containment_precedes_engine(runner, source, tmp_path, monkeypatch, location):
    root, snapshot, records = source
    out = root / "out" if location == "input" else tmp_path / location / "out"
    if location == "git":
        out.parent.mkdir()
        (out.parent / ".git").write_text("worktree")
    if location == "nonempty":
        out.mkdir(parents=True)
        (out / "existing").write_text("keep")
    monkeypatch.setattr(runner, "_preflight_engine", lambda config: pytest.fail("engine reached"))
    with pytest.raises(ValueError):
        runner.run_document(snapshot, records, input_root=root, out=out,
            config=engines.OcrConfig("tesseract-eng", "tesseract", "eng"))


def test_unregistered_source_precedes_engine(runner, source, tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "_preflight_engine", lambda config: pytest.fail("engine reached"))
    other = source[0] / "other.jpg"
    Image.new("RGB", (120, 80), "black").save(other)
    records = [pending_version(InputSnapshot(other), "shelf:other", synthetic=True)]
    with pytest.raises(ValueError, match="matching pending"):
        runner.run_document(source[1], records, input_root=source[0], out=tmp_path / "out",
            config=engines.OcrConfig("tesseract-eng", "tesseract", "eng"))
