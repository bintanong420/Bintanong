"""The six OCR configurations of the bake-off (Q14) and the pluggable OCR-run step.

Nothing here imports an OCR engine. `availability` only looks for the executable or the importable
package; `run_ocr` is a stub that raises EngineNotInstalled until an adapter is registered in
ADAPTERS (plan task for the real run, after the per-OS install in Q15 is approved).
"""

from __future__ import annotations

import importlib.util
import shutil
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


class EngineNotInstalled(RuntimeError):
    pass


def find_config(config_id: str) -> OcrConfig | None:
    return next((c for c in GRID if c.id == config_id), None)


def availability(config: OcrConfig) -> tuple[bool, str]:
    """(usable, reason). Looks only for the executable or package, never imports an engine."""
    if config.engine == "tesseract":
        if shutil.which("tesseract"):
            return True, "tesseract executable found"
        return False, "tesseract is not on PATH"
    missing = [m for m in ("rapidocr", "onnxruntime") if importlib.util.find_spec(m) is None]
    if missing:
        return False, f"python package(s) not installed: {', '.join(missing)}"
    return True, "rapidocr and onnxruntime importable"


def run_ocr(config: OcrConfig, images_dir: Path, out_dir: Path) -> None:
    ok, reason = availability(config)
    if not ok:
        raise EngineNotInstalled(f"engine not installed for {config.id}: {reason}")
    adapter = ADAPTERS.get(config.engine)
    if adapter is None:
        raise EngineNotInstalled(f"engine not installed for {config.id}: engine found but no adapter is registered yet")
    adapter(config, Path(images_dir), Path(out_dir))
