import hashlib
import importlib.util
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("fetch_rapidocr_models", REPO / "scripts" / "fetch_rapidocr_models.py")
fetch = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fetch)


def test_every_rapidocr_config_is_built_once_and_the_models_are_hashed(tmp_path):
    built = []

    def build(config):
        built.append(config.id)
        (tmp_path / f"{config.lang.replace(':', '_')}.onnx").write_bytes(config.id.encode())

    result = fetch.fetch(build, tmp_path)
    assert built == ["rapidocr-en", "rapidocr-latin", "rapidocr-iso:fil"]
    assert result["en.onnx"] == hashlib.sha256(b"rapidocr-en").hexdigest()
    assert sorted(result) == ["en.onnx", "iso_fil.onnx", "latin.onnx"]


def test_main_writes_an_lf_manifest(tmp_path, monkeypatch):
    monkeypatch.setattr(fetch, "build_engine", lambda config: (tmp_path / "m.onnx").write_bytes(b"x"))
    monkeypatch.setattr(fetch, "models_dir", lambda: tmp_path)
    out = tmp_path / "manifest.json"
    assert fetch.main(["--manifest", str(out)]) == 0
    assert json.loads(out.read_text(encoding="utf-8")) == {"m.onnx": hashlib.sha256(b"x").hexdigest()}
    assert b"\r\n" not in out.read_bytes()


def test_a_run_that_fetched_no_model_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(fetch, "build_engine", lambda config: None)
    monkeypatch.setattr(fetch, "models_dir", lambda: tmp_path)
    assert fetch.main([]) == 1
