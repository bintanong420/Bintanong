"""Gate-only OCR candidates from registered captured bytes; no engine downloads."""
from __future__ import annotations

import io
import json
import math
import os
import re
import tempfile
import time
from contextlib import closing
from pathlib import Path

from ..ocr_bench import engines
from ..prospectus_extractor.identity import InputSnapshot, bytes_sha256, is_sha256
from ..prospectus_extractor.loader import _write_bytes_atomic
from .inspection import InspectionRefused, check_out
from .register import version_for_snapshot


def _json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def _preflight_engine(config: engines.OcrConfig) -> dict:
    if not isinstance(config, engines.OcrConfig) or config.engine not in engines.ADAPTERS:
        raise ValueError("a registered OCR configuration is required")
    ok, reason = engines.availability(config)
    if not ok:
        raise engines.EngineNotInstalled(reason)
    if config.engine != "tesseract":
        # shortcut: RapidOCR can fetch weights at initialization, enable only after verified local-model-only startup.
        raise engines.EngineNotInstalled("RapidOCR local-model-only initialization is not verified")
    if not re.fullmatch(r"[A-Za-z0-9_]+(?:\+[A-Za-z0-9_]+)*", config.lang):
        raise ValueError("invalid Tesseract language selection")
    prefix = os.environ.get("TESSDATA_PREFIX")
    exe = engines.find_tesseract()
    if not exe or not prefix:
        raise engines.EngineNotInstalled("Tesseract executable and TESSDATA_PREFIX are required")
    models = []
    for lang in config.lang.split("+"):
        path = Path(prefix).resolve() / f"{lang}.traineddata"
        if not path.is_file() or not path.stat().st_size:
            raise engines.EngineNotInstalled(f"local traineddata missing for {lang}")
        models.append({"filename": path.name, "sha256": bytes_sha256(path.read_bytes())})
    return {"executable": exe, "model": models, "tessdata_prefix": str(Path(prefix).resolve())}


def _run_adapter(config, images, out):
    engines.run_ocr(config, images, out)


def _render(snapshot: InputSnapshot, images: Path) -> list[dict]:
    from PIL import Image

    pages = []
    if snapshot.path.suffix.lower() in {".jpg", ".jpeg"}:
        with Image.open(io.BytesIO(snapshot.data)) as image:
            if image.format != "JPEG":
                raise ValueError("JPEG suffix does not match captured bytes")
            image.load()
            with image.convert("RGB") as rgb:
                rgb.save(images / "page-0001.png")
            pages.append({"binding": {"kind": "image", "image_index": 1}, "size": list(image.size)})
    else:
        import pypdfium2 as pdfium

        with pdfium.PdfDocument(snapshot.data) as pdf:
            if len(pdf) == 0:
                raise ValueError("PDF has no physical pages")
            for i in range(len(pdf)):
                with closing(pdf[i]) as page:
                    with closing(page.render(scale=2)) as bitmap:
                        with bitmap.to_pil() as image:
                            image.save(images / f"page-{i + 1:04d}.png")
                            pages.append({"binding": {"kind": "pdf_page", "page": i + 1},
                                          "size": list(image.size)})
    return pages


def validate_candidate(candidate: dict) -> None:
    """Validate the same gate-only evidence at runner and evaluator boundaries."""
    if not isinstance(candidate, dict) or candidate.get("origin") != "ocr_candidate":
        raise ValueError("OCR candidate origin is required")
    digest = candidate.get("source_sha256")
    if not is_sha256(digest) or candidate.get("version_id") != f"ver-{digest}":
        raise ValueError("candidate source/version identity mismatch")
    n = candidate.get("page_count")
    pages = candidate.get("pages")
    if (type(n) is not int or n < 1 or not isinstance(pages, list) or len(pages) != n
            or candidate.get("source_format") not in {"pdf", "jpeg"}
            or (candidate["source_format"] == "jpeg" and n != 1)
            or type(candidate.get("started_at_ns")) is not int or candidate["started_at_ns"] <= 0):
        raise ValueError("candidate page coverage or start time invalid")
    meta = candidate.get("metadata")
    if not isinstance(meta, dict) or any(not isinstance(meta.get(k), str) or not meta[k].strip()
            or meta[k].lower() in {"unknown", "auto", "requested", "not-installed"}
            for k in ("engine", "config", "engine_version", "lang", "device")):
        raise ValueError("actual engine metadata is missing")
    if meta["engine"] not in engines.ADAPTERS or (meta["engine"] == "tesseract" and meta["device"] != "cpu"):
        raise ValueError("invalid actual engine/device")
    if (type(meta.get("images")) is not int or meta["images"] != n
            or type(meta.get("seconds")) not in (int, float) or not math.isfinite(meta["seconds"])
            or meta["seconds"] < 0):
        raise ValueError("actual engine page count/timing missing")
    for i, page in enumerate(pages, 1):
        expected = {"kind": "pdf_page", "page": i} if candidate["source_format"] == "pdf" else {"kind": "image", "image_index": 1}
        if not isinstance(page, dict) or page.get("binding") != expected:
            raise ValueError("candidate physical page/image binding mismatch")
        size, text, words = page.get("size"), page.get("text"), page.get("words")
        if (not isinstance(size, list) or len(size) != 2 or any(type(x) not in (int, float)
                or not math.isfinite(x) or x <= 0 for x in size)
                or not isinstance(text, str) or not text.strip() or not isinstance(words, list) or not words):
            raise ValueError("candidate text/word geometry missing")
        for word in words:
            if not isinstance(word, dict) or not isinstance(word.get("text"), str) or not word["text"].strip():
                raise ValueError("word text missing")
            conf, box = word.get("conf"), word.get("box")
            if type(conf) not in (int, float) or not math.isfinite(conf) or not 0 <= conf <= 100:
                raise ValueError("raw adapter confidence must be finite percent")
            if (not isinstance(box, list) or len(box) != 4 or any(type(x) not in (int, float)
                    or not math.isfinite(x) for x in box) or not 0 <= box[0] < box[2] <= size[0]
                    or not 0 <= box[1] < box[3] <= size[1]):
                raise ValueError("word box lies outside rendered image")


def run_document(snapshot: InputSnapshot, register, *, input_root: Path, out: Path,
                 config: engines.OcrConfig) -> dict:
    """Publish validated raw OCR and candidates atomically; manifest is last."""
    root, out = Path(input_root).resolve(), Path(out).resolve()
    if not isinstance(snapshot, InputSnapshot) or root not in snapshot.path.parents:
        raise ValueError("snapshot must belong to the explicit input root")
    suffix = snapshot.path.suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".pdf"}:
        raise ValueError("OCR accepts JPEG or PDF captured bytes")
    try:
        check_out(root, out)
    except InspectionRefused as exc:
        raise ValueError(str(exc)) from exc
    version = version_for_snapshot(snapshot, register)
    started = time.time_ns()
    try:
        preflight = _preflight_engine(config)
        out.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="stage-", dir=out) as temporary:
            stage = Path(temporary)
            images, raw = stage / "images", stage / "raw"
            images.mkdir()
            pages = _render(snapshot, images)
            _run_adapter(config, images, raw)
            metadata = json.loads((raw / "ocr_run.json").read_bytes())
            if (metadata.get("engine"), metadata.get("config"), metadata.get("lang")) != (config.engine, config.id, config.lang):
                raise ValueError("actual metadata differs from passed engine/config/language")
            for i, page in enumerate(pages, 1):
                stem = f"page-{i:04d}"
                page.update(text=(raw / f"{stem}.txt").read_text(encoding="utf-8"),
                            words=json.loads((raw / f"{stem}.words.json").read_bytes()),
                            rendered_sha256=bytes_sha256((images / f"{stem}.png").read_bytes()))
            expected_files = {"ocr_run.json"} | {f"page-{i:04d}{ext}" for i in range(1, len(pages) + 1)
                                                 for ext in (".txt", ".words.json")}
            if {p.name for p in raw.iterdir()} != expected_files:
                raise ValueError("adapter output page coverage mismatch")
            result = {"origin": "ocr_candidate", "source_sha256": snapshot.sha256,
                "version_id": version.version_id, "source_format": "pdf" if suffix == ".pdf" else "jpeg",
                "page_count": len(pages), "started_at_ns": started, "metadata": metadata,
                "settings": {"pdf_render_scale": 2, "confidence_scale": "adapter_percent_0_100",
                             "preflight": preflight}, "pages": pages, "gate_only": True}
            validate_candidate(result)
            snapshot.verify_unchanged()
            if preflight.get("tessdata_prefix"):
                for model in preflight["model"]:
                    if bytes_sha256((Path(preflight["tessdata_prefix"]) / model["filename"]).read_bytes()) != model["sha256"]:
                        raise ValueError("local traineddata changed during OCR")
            artifacts = {p.name: p.read_bytes() for p in raw.iterdir()}
            artifacts["ocr_candidates.json"] = _json_bytes(result)
            for name, data in artifacts.items():
                _write_bytes_atomic(out / name, data)
            snapshot.verify_unchanged()
            _write_bytes_atomic(out / "manifest.json", _json_bytes({"complete": True,
                "source_unchanged": True, "gate_only": True, "source_sha256": snapshot.sha256,
                "version_id": version.version_id, "files": {n: bytes_sha256(b) for n, b in artifacts.items()}}))
            return result
    except engines.EngineNotInstalled as exc:
        snapshot.verify_unchanged()
        _write_bytes_atomic(out / "ocr_run.json", _json_bytes({"evaluation": "NOT RUN",
            "reason": str(exc), "source_sha256": snapshot.sha256, "requested_config": config.id,
            "requested_engine": config.engine, "requested_lang": config.lang}))
        raise
