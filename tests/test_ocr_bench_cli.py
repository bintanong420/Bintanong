import copy
import importlib.util
import json
from pathlib import Path

from PIL import Image

from backend.bintanong_tools.ocr_bench import engines
from test_ocr_bench_score import reference

_spec = importlib.util.spec_from_file_location(
    "ocr_bench_cli", Path(__file__).resolve().parents[1] / "scripts" / "ocr_bench.py")
cli = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cli)


def _write(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_the_grid_is_the_six_q14_configurations():
    assert [c.id for c in engines.GRID] == [
        "tesseract-eng", "tesseract-fil", "tesseract-eng+fil", "rapidocr-en", "rapidocr-latin", "rapidocr-iso:fil"]


def test_a_missing_engine_is_reported_as_not_installed(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(engines, "availability", lambda config: (False, "tesseract is not on PATH"))
    code = cli.main(["ocr", "--config", "tesseract-fil", "--images", str(tmp_path), "--out", str(tmp_path / "o")])
    assert code == 3
    assert "engine not installed" in capsys.readouterr().err


def test_an_unknown_config_is_refused(tmp_path, capsys):
    assert cli.main(["ocr", "--config", "nope", "--images", str(tmp_path), "--out", str(tmp_path)]) == 2
    assert "unknown config" in capsys.readouterr().err


def test_list_shows_every_config_and_its_availability(monkeypatch, capsys):
    monkeypatch.setattr(engines, "availability", lambda config: (False, "x"))
    assert cli.main(["ocr", "--list"]) == 0
    out = capsys.readouterr().out
    assert all(c.id in out for c in engines.GRID)


def test_simulate_writes_images_and_a_manifest(tmp_path):
    src = tmp_path / "pdfs" / "inst"
    src.mkdir(parents=True)
    Image.new("RGB", (612, 936), "white").save(src / "a.pdf")
    out = tmp_path / "out"
    assert cli.main(["simulate", "--pdf-dir", str(tmp_path / "pdfs"), "--out", str(out), "--conditions", "flat_good,blur",
                     "--dpi", "50", "--seed", "3"]) == 0
    assert sorted(p.name for p in out.glob("*.jpg")) == ["a_p01_blur.jpg", "a_p01_flat_good.jpg"]
    manifest = json.loads((out / "simulate_manifest.json").read_text(encoding="utf-8"))
    assert manifest["seed"] == 3 and len(manifest["images"]) == 2
    assert b"\r\n" not in (out / "simulate_manifest.json").read_bytes()


def test_score_passes_a_document_against_itself_and_fails_a_damaged_copy(tmp_path, capsys):
    ref_dir, good_dir, bad_dir = tmp_path / "ref", tmp_path / "good", tmp_path / "bad"
    _write(ref_dir / "doc.json", reference())
    _write(good_dir / "doc.json", reference())
    damaged = copy.deepcopy(reference())
    damaged["courses"].pop(1)
    damaged["courses"][0]["lab_units"] = 2
    _write(bad_dir / "doc.json", damaged)

    assert cli.main(["score", "--reference", str(ref_dir), "--candidate", str(good_dir), "--out", str(tmp_path / "r1")]) == 0
    assert cli.main(["score", "--reference", str(ref_dir), "--candidate", str(bad_dir), "--out", str(tmp_path / "r2")]) == 1
    report = json.loads((tmp_path / "r2" / "ocr_score.json").read_text(encoding="utf-8"))
    assert report["corpus"]["verdict"]["supported"] is False
    assert report["documents"]["doc"]["missing"] == ["CS 102"]
    text = (tmp_path / "r2" / "ocr_score.md").read_text(encoding="utf-8")
    assert "NOT SUPPORTED" in text and "missing" in text and b"\r\n" not in (tmp_path / "r2" / "ocr_score.md").read_bytes()


def test_a_reference_with_no_candidate_counts_as_all_courses_missing(tmp_path):
    _write(tmp_path / "ref" / "doc.json", reference())
    (tmp_path / "cand").mkdir()
    assert cli.main(["score", "--reference", str(tmp_path / "ref"), "--candidate", str(tmp_path / "cand"), "--out", str(tmp_path / "o")]) == 1
    report = json.loads((tmp_path / "o" / "ocr_score.json").read_text(encoding="utf-8"))
    assert report["documents"]["doc"]["missing"] == ["CS 101", "CS 102", "MATH 101"]
