"""Identity of a conversion and of an output set: what each was made from."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as package_version
from pathlib import Path
from typing import Any, Mapping, Sequence
import hashlib
import json
import os

from .common import SCHEMA_VERSION

PACKAGE_DIR = Path(__file__).resolve().parent
IDENTITY_VERSION = 1
CONVERSION_PROFILE = "palsu-born-digital-v3"
_TRUE_VALUES = {"1", "true", "yes", "on"}


def file_sha256(path: Path) -> str:
    """The one place a PDF or cache file is hashed (fixer, batch record, cache and publish all call it)."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def package_sha256(package: Path = PACKAGE_DIR) -> str:
    """One hash over every module, so any parser change changes the recorded hash."""
    digest = hashlib.sha256()
    for path in sorted(package.glob("*.py")):
        digest.update(path.name.encode())
        digest.update(path.read_bytes().replace(b"\r\n", b"\n"))
    return digest.hexdigest()


def cell_matching_enabled() -> bool:
    raw = os.environ.get("PALSU_DOCLING_CELL_MATCHING", "true").strip().lower()
    return raw in _TRUE_VALUES


def installed_versions() -> dict[str, str]:
    found: dict[str, str] = {}
    for name in ("docling", "docling-core", "docling-parse"):
        try:
            found[name] = package_version(name)
        except PackageNotFoundError:
            found[name] = "not-installed"
    return found


def conversion_settings(do_ocr: bool = False, ocr_languages: Sequence[str] = ()) -> dict[str, Any]:
    """Every setting that changes what Docling produces. Single source for the
    pipeline options (docling_env.get_pipeline_options) and for cache identity."""
    return {
        "profile": CONVERSION_PROFILE,
        "do_ocr": bool(do_ocr),
        "ocr_languages": sorted(ocr_languages) if do_ocr else [],
        "do_table_structure": True,
        "table_mode": "accurate",
        "force_backend_text": True,
        "cell_matching": cell_matching_enabled(),
        "backend": "docling_parse",
        "backend_fallback": "pypdfium2",
        "versions": installed_versions(),
    }


def _canonical_sha256(value: Mapping[str, Any]) -> str:
    text = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(text.encode("ascii")).hexdigest()


def conversion_identity(pdf_sha256: str, settings: Mapping[str, Any]) -> str:
    return _canonical_sha256(
        {"identity_version": IDENTITY_VERSION, "pdf_sha256": pdf_sha256, "settings": dict(settings)}
    )


def run_identity(
    input_path: Path,
    semantic_doc: Path | None,
    *,
    schema_version: str | None = None,
    package_hash: str | None = None,
    settings: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """What one output set is made from. `run_key` is what --skip-existing compares."""
    input_path = Path(input_path)
    suffix = input_path.suffix.lower()
    if suffix == ".pdf":
        kind = "pdf"
    elif suffix == ".json":
        kind = "docling-json"
    else:
        raise ValueError(f"Unsupported input type: {input_path.suffix}")
    input_hash = file_sha256(input_path)
    conversion_id = None
    used_settings = None
    if kind == "pdf":
        used_settings = dict(settings) if settings is not None else conversion_settings()
        conversion_id = conversion_identity(input_hash, used_settings)
    semantic_hash = (
        file_sha256(Path(semantic_doc)) if semantic_doc and Path(semantic_doc).is_file() else None
    )
    core = {
        "input_kind": kind,
        "input_sha256": input_hash,
        "conversion_identity": conversion_id,
        "package_sha256": package_hash or package_sha256(),
        "schema_version": schema_version or SCHEMA_VERSION,
        "semantic_sha256": semantic_hash,
    }
    return {
        "identity_version": IDENTITY_VERSION,
        **core,
        "pdf_sha256": input_hash if kind == "pdf" else None,
        "conversion_settings": used_settings,
        "review_input_only": kind == "docling-json",
        "run_key": _canonical_sha256(core),
    }
