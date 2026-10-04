"""The six OCR configurations of the bake-off (Q14) and the OCR-run step.

`availability` only looks for the executable or the importable package and never imports an
engine. `run_ocr` raises EngineNotInstalled when an engine is missing; otherwise it calls the
adapter registered for the engine in ADAPTERS. An adapter reads every image in a folder and
writes, per image, `<stem>.txt` and `<stem>.words.json` (text, confidence, box), plus one
`ocr_run.json` (config, engine version, device or provider that actually ran, seconds).
These adapters run the bare engines; converting their output into an extractor payload through
the Docling chain is the remaining part of plan Task 4b.
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class OcrConfig:
    id: str
    engine: str    # "tesseract" or "rapidocr"
    lang: str      # engine's own language code


GRID = tuple(OcrConfig(f"{engine}-{lang}", engine, lang) for engine, lang in (
    ("tesseract", "eng"), ("tesseract", "fil"), ("tesseract", "eng+fil"),
    ("rapidocr", "en"), ("rapidocr", "latin"), ("rapidocr", "iso:fil"),
))

ADAPTERS: dict[str, Callable[[OcrConfig, Path, Path], None]] = {}  # engine name -> run(config, images_dir, out_dir)
IMAGE_SUFFIXES = (".jpg", ".jpeg", ".png")
WINDOWS_TESSERACT = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")  # winget's folder; not on PATH until a new shell


class EngineNotInstalled(RuntimeError):
    pass


def find_config(config_id: str) -> OcrConfig | None:
    return next((c for c in GRID if c.id == config_id), None)


def find_tesseract() -> str | None:
    return shutil.which("tesseract") or (str(WINDOWS_TESSERACT) if WINDOWS_TESSERACT.exists() else None)


def availability(config: OcrConfig) -> tuple[bool, str]:
    """(usable, reason). Looks only for the executable or package, never imports an engine."""
    if config.engine == "tesseract":
        if find_tesseract():
            return True, "tesseract executable found"
        return False, "tesseract is not on PATH"
    missing = [m for m in ("rapidocr", "onnxruntime") if importlib.util.find_spec(m) is None]
    if missing:
        return False, f"python package(s) not installed: {', '.join(missing)}"
    return True, "rapidocr and onnxruntime importable"


def _images(images_dir: Path) -> list[Path]:
    return sorted(p for p in Path(images_dir).iterdir() if p.suffix.lower() in IMAGE_SUFFIXES)


def _write(path: Path, text: str) -> None:
    path.write_bytes(text.encode("utf-8"))  # LF on every OS


def parse_tesseract_tsv(tsv: str) -> list[dict]:
    """Word rows (level 5) of Tesseract's TSV: text, confidence 0-100, box [left, top, right, bottom], line key."""
    if not tsv.startswith("level\t"):
        raise ValueError("tesseract output is not TSV (the tsv config was not applied)")
    words = []
    for row in tsv.splitlines()[1:]:
        cols = row.split("\t")
        if len(cols) < 12 or cols[0] != "5" or not cols[11].strip():
            continue
        left, top, width, height = (int(c) for c in cols[6:10])
        words.append({"text": cols[11].strip(), "conf": float(cols[10]), "box": [left, top, left + width, top + height],
                      "line": [int(cols[2]), int(cols[3]), int(cols[4])]})
    return words


def words_to_text(words: list[dict]) -> str:
    lines, current, key = [], [], None
    for w in words:
        if key is not None and w["line"] != key:
            lines.append(" ".join(current))
            current = []
        key = w["line"]
        current.append(w["text"])
    if current:
        lines.append(" ".join(current))
    return "".join(line + "\n" for line in lines)


def _run_tesseract(exe: str, image: Path, lang: str, env: dict) -> str:
    # -c tessedit_create_tsv=1, not the `tsv` config name: that file lives in tessdata/configs, which a pinned TESSDATA_PREFIX lacks
    done = subprocess.run([exe, str(image), "stdout", "-l", lang, "-c", "tessedit_create_tsv=1"], capture_output=True, env=env, check=True)
    return done.stdout.decode("utf-8", "replace")


def _tesseract_version(exe: str) -> str:
    out = subprocess.run([exe, "--version"], capture_output=True, text=True).stdout.splitlines()
    return out[0].replace("tesseract", "").strip() if out else "unknown"


def tesseract_adapter(config: OcrConfig, images_dir: Path, out_dir: Path) -> None:
    exe = find_tesseract()
    prefix = os.environ.get("TESSDATA_PREFIX")
    if not exe:
        raise EngineNotInstalled(f"engine not installed for {config.id}: tesseract is not on PATH")
    if not prefix:
        raise EngineNotInstalled(f"engine not installed for {config.id}: set TESSDATA_PREFIX (python scripts/fetch_tessdata.py prints it)")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "TESSDATA_PREFIX": prefix, "OMP_THREAD_LIMIT": "1"}
    images = _images(images_dir)
    started = time.perf_counter()
    for image in images:
        words = parse_tesseract_tsv(_run_tesseract(exe, image, config.lang, env))
        _write(out_dir / f"{image.stem}.txt", words_to_text(words))
        _write(out_dir / f"{image.stem}.words.json", json.dumps(words, ensure_ascii=False))
    meta = {"config": config.id, "engine": "tesseract", "engine_version": _tesseract_version(exe), "lang": config.lang,
            "device": "cpu", "tessdata_prefix": prefix, "images": len(images), "seconds": round(time.perf_counter() - started, 3)}
    _write(out_dir / "ocr_run.json", json.dumps(meta, indent=2) + "\n")


ADAPTERS["tesseract"] = tesseract_adapter


def wanted_device() -> str:
    """OCR_BENCH_DEVICE: cuda, cpu or auto (cuda when onnxruntime lists the CUDA provider)."""
    value = os.environ.get("OCR_BENCH_DEVICE", "auto").lower()
    if value == "auto":
        import onnxruntime

        return "cuda" if "CUDAExecutionProvider" in onnxruntime.get_available_providers() else "cpu"
    return value


def _rapidocr_engine(config: OcrConfig, use_cuda: bool):
    """(callable image path -> result, providers the sessions actually use). Language resolution is
    Docling's own (`iso:fil` becomes PP-OCRv6 `tl`), so this measures what Docling would run."""
    import onnxruntime

    if use_cuda and hasattr(onnxruntime, "preload_dlls"):
        onnxruntime.preload_dlls()  # load the pip-wheel CUDA and cuDNN libraries before any session (a system CUDA on PATH can otherwise win)
    from docling.models.stages.ocr.rapid_ocr_model import _resolve_rapidocr
    from rapidocr import ModelType, OCRVersion, RapidOCR

    spec = _resolve_rapidocr(config.lang, "onnxruntime")
    size = ModelType("small" if spec.ppocr_version == OCRVersion.PPOCRV6 else "mobile")
    engine = RapidOCR(params={
        "Det.ocr_version": spec.ppocr_version, "Det.lang_type": "ch", "Det.model_type": size,
        "Rec.ocr_version": spec.ppocr_version, "Rec.lang_type": spec.rapidocr_code, "Rec.model_type": size,
        "Det.use_cuda": use_cuda, "Cls.use_cuda": use_cuda, "Rec.use_cuda": use_cuda,
        "EngineConfig.onnxruntime.use_cuda": use_cuda,
        # On the RTX 4060 with onnxruntime-gpu 1.30.0 / cuDNN 9.24 the PP-OCRv6 recognizer fails on its first
        # batch (CUDNN_STATUS_EXECUTION_FAILED_CUDART) with RapidOCR's default EXHAUSTIVE search and also with
        # HEURISTIC; only DEFAULT ran, repeatably (see the plan, Task 4a results).
        "EngineConfig.onnxruntime.cuda_ep_cfg.cudnn_conv_algo_search": "DEFAULT",
    })
    providers = list(engine.text_rec.session.session.get_providers())
    return engine, providers


def rapidocr_adapter(config: OcrConfig, images_dir: Path, out_dir: Path) -> None:
    device = wanted_device()
    engine, providers = _rapidocr_engine(config, device == "cuda")
    if device == "cuda" and "CUDAExecutionProvider" not in providers:
        raise EngineNotInstalled(f"engine not installed for {config.id}: CUDA was requested but the session uses {providers}")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    images = _images(images_dir)
    started = time.perf_counter()
    for image in images:
        result = engine(str(image))
        lines = []
        for box, text, score in zip(result.boxes if result.boxes is not None else [], result.txts or (), result.scores or ()):
            xs, ys = [int(p[0]) for p in box], [int(p[1]) for p in box]
            lines.append({"text": text, "conf": round(float(score) * 100, 1), "box": [min(xs), min(ys), max(xs), max(ys)]})
        _write(out_dir / f"{image.stem}.txt", "".join(w["text"] + "\n" for w in lines))
        _write(out_dir / f"{image.stem}.words.json", json.dumps(lines, ensure_ascii=False))
    import importlib.metadata

    meta = {"config": config.id, "engine": "rapidocr", "engine_version": importlib.metadata.version("rapidocr"),
            "lang": config.lang, "device": device, "providers": providers, "images": len(images),
            "seconds": round(time.perf_counter() - started, 3)}
    _write(out_dir / "ocr_run.json", json.dumps(meta, indent=2) + "\n")


ADAPTERS["rapidocr"] = rapidocr_adapter


def run_ocr(config: OcrConfig, images_dir: Path, out_dir: Path) -> None:
    ok, reason = availability(config)
    if not ok:
        raise EngineNotInstalled(f"engine not installed for {config.id}: {reason}")
    adapter = ADAPTERS.get(config.engine)
    if adapter is None:
        raise EngineNotInstalled(f"engine not installed for {config.id}: engine found but no adapter is registered yet")
    adapter(config, Path(images_dir), Path(out_dir))
