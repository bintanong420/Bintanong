import json

import pytest

from backend.bintanong_tools.ocr_bench import engines

TSV = (
    "level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext\n"
    "1\t1\t0\t0\t0\t0\t0\t0\t100\t50\t-1\t\n"
    "5\t1\t1\t1\t1\t1\t10\t10\t30\t12\t96.5\tCS\n"
    "5\t1\t1\t1\t1\t2\t45\t10\t40\t12\t91.0\t101\n"
    "5\t1\t1\t1\t2\t1\t10\t30\t80\t12\t40.0\tIntro\n"
)


def test_tsv_words_keep_text_confidence_and_box_and_skip_structure_rows():
    words = engines.parse_tesseract_tsv(TSV)
    assert [w["text"] for w in words] == ["CS", "101", "Intro"]
    assert words[0] == {"text": "CS", "conf": 96.5, "box": [10, 10, 40, 22], "line": [1, 1, 1]}


def test_output_that_is_not_tsv_is_an_error_not_an_empty_page():
    with pytest.raises(ValueError, match="not TSV"):
        engines.parse_tesseract_tsv("Republic of the Philippines\nPALAWAN STATE UNIVERSITY\n")


def test_tesseract_is_asked_for_tsv_without_a_config_file(monkeypatch):
    seen = []
    monkeypatch.setattr(engines.subprocess, "run", lambda cmd, **kw: seen.append(cmd) or type("R", (), {"stdout": b"level\n"})())
    engines._run_tesseract("tesseract", engines.Path("a.jpg"), "fil", {})
    assert "tessedit_create_tsv=1" in seen[0] and "tsv" not in seen[0]  # the `tsv` config lives in tessdata/configs, absent from a pinned TESSDATA_PREFIX


def test_text_is_rebuilt_line_by_line():
    assert engines.words_to_text(engines.parse_tesseract_tsv(TSV)) == "CS 101\nIntro\n"


def test_the_tesseract_adapter_writes_text_words_and_run_metadata(tmp_path, monkeypatch):
    images, out = tmp_path / "img", tmp_path / "out"
    images.mkdir()
    (images / "a.jpg").write_bytes(b"x")
    (images / "notes.txt").write_text("not an image")
    calls = []
    monkeypatch.setattr(engines, "_run_tesseract", lambda exe, image, lang, env: calls.append((image.name, lang)) or TSV)
    monkeypatch.setattr(engines, "_tesseract_version", lambda exe: "5.5.3")
    monkeypatch.setattr(engines, "find_tesseract", lambda: "tesseract")
    monkeypatch.setenv("TESSDATA_PREFIX", str(tmp_path))
    engines.tesseract_adapter(engines.find_config("tesseract-eng+fil"), images, out)
    assert calls == [("a.jpg", "eng+fil")]
    assert (out / "a.txt").read_text(encoding="utf-8") == "CS 101\nIntro\n"
    assert json.loads((out / "a.words.json").read_text(encoding="utf-8"))[0]["conf"] == 96.5
    meta = json.loads((out / "ocr_run.json").read_text(encoding="utf-8"))
    assert meta["config"] == "tesseract-eng+fil" and meta["engine_version"] == "5.5.3" and meta["device"] == "cpu"
    assert meta["images"] == 1 and meta["tessdata_prefix"] == str(tmp_path)


def test_the_tesseract_adapter_needs_tessdata_prefix(tmp_path, monkeypatch):
    monkeypatch.delenv("TESSDATA_PREFIX", raising=False)
    monkeypatch.setattr(engines, "find_tesseract", lambda: "tesseract")
    with pytest.raises(engines.EngineNotInstalled, match="TESSDATA_PREFIX"):
        engines.tesseract_adapter(engines.find_config("tesseract-fil"), tmp_path, tmp_path / "o")


class _FakeResult:
    boxes = [[[10, 10], [60, 10], [60, 30], [10, 30]], [[10, 40], [90, 40], [90, 60], [10, 60]]]
    txts = ("CS 101", "Intro")
    scores = (0.97, 0.41)


def test_the_rapidocr_adapter_writes_lines_with_percent_confidence_and_the_provider_that_ran(tmp_path, monkeypatch):
    images, out = tmp_path / "img", tmp_path / "out"
    images.mkdir()
    (images / "a.png").write_bytes(b"x")
    built = []
    monkeypatch.setattr(engines, "_rapidocr_engine", lambda config, use_cuda: built.append((config.lang, use_cuda)) or (
        lambda path: _FakeResult(), ["CUDAExecutionProvider", "CPUExecutionProvider"]))
    monkeypatch.setenv("OCR_BENCH_DEVICE", "cuda")
    engines.rapidocr_adapter(engines.find_config("rapidocr-iso:fil"), images, out)
    assert built == [("iso:fil", True)]
    assert (out / "a.txt").read_text(encoding="utf-8") == "CS 101\nIntro\n"
    words = json.loads((out / "a.words.json").read_text(encoding="utf-8"))
    assert [(w["text"], w["conf"]) for w in words] == [("CS 101", 97.0), ("Intro", 41.0)]
    assert words[0]["box"] == [10, 10, 60, 30]
    meta = json.loads((out / "ocr_run.json").read_text(encoding="utf-8"))
    assert meta["device"] == "cuda" and meta["providers"][0] == "CUDAExecutionProvider"


def test_a_cuda_request_that_ran_on_cpu_is_refused(tmp_path, monkeypatch):
    (tmp_path / "a.png").write_bytes(b"x")
    monkeypatch.setattr(engines, "_rapidocr_engine", lambda config, use_cuda: (lambda path: _FakeResult(), ["CPUExecutionProvider"]))
    monkeypatch.setenv("OCR_BENCH_DEVICE", "cuda")
    with pytest.raises(engines.EngineNotInstalled, match="CUDA"):
        engines.rapidocr_adapter(engines.find_config("rapidocr-en"), tmp_path, tmp_path / "o")


def test_adapters_are_registered_for_both_engines():
    assert set(engines.ADAPTERS) == {"tesseract", "rapidocr"}
