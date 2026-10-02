"""In-process batch engine and manifest."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from pathlib import Path
from typing import Any
from typing import Iterable
from typing import Sequence
import json
import re
import traceback

from .common import MANIFEST_SCHEMA_VERSION, RICH_AVAILABLE, console

if RICH_AVAILABLE:
    from .common import track
from .docling_env import ensure_docling_env, get_shared_converter
from .paths import DEFAULT_SEMANTIC_DOC, find_default_input_root, find_default_output_root
from .pipeline import process_prospectus


def safe_stem(path: Path) -> str:
    stem = Path(path).stem.strip()
    if stem.endswith("_docling"):  # batching saved Docling JSON should not double the suffix
        stem = stem[: -len("_docling")]
    stem = re.sub(r"[^A-Za-z0-9._ -]+", "_", stem)
    return re.sub(r"\s+", " ", stem).strip() or "prospectus"


@dataclass
class BatchConfig:
    input_root: Path = field(default_factory=find_default_input_root)
    output_root: Path = field(default_factory=find_default_output_root)
    recursive: bool = True
    preserve_structure: bool = True
    export_mode: str = "side_by_side"  # side_by_side | per_pdf_folder
    write_json: bool = True
    write_csv: bool = True
    write_pl: bool = True
    write_jsonl: bool = True
    write_manifest: bool = True
    skip_existing: bool = False
    force_reconvert: bool = False
    device: str = "auto"
    strict: bool = False
    semantic_doc: Path | None = DEFAULT_SEMANTIC_DOC
    include_patterns: list[str] = field(default_factory=lambda: ["*.pdf"])


@dataclass
class BatchItem:
    source_pdf: Path
    json_path: Path
    csv_path: Path
    pl_path: Path
    jsonl_path: Path

    @property
    def pdf_path(self) -> Path:
        return self.source_pdf


IGNORED_DIR_PARTS = {
    "palsu_jsonified_output", "docling_jsonified_output", ".venv", ".docling-venv",
    "__pycache__", ".git", "node_modules",
}


def scan_inputs(
    input_root: Path, recursive: bool = True, patterns: Sequence[str] | None = None
) -> list[Path]:
    root = Path(input_root).expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"Input folder does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Input path is not a folder: {root}")

    found: list[Path] = []
    for pattern in patterns or ["*.pdf"]:
        iterator = root.rglob(pattern) if recursive else root.glob(pattern)
        for path in iterator:
            if not path.is_file():
                continue
            if any(part.lower() in IGNORED_DIR_PARTS for part in path.parts):
                continue
            if path.name.endswith("_docling.json") and pattern == "*.json":
                pass  # explicitly requested
            if path not in found:
                found.append(path)
    return sorted(found)


# Backwards-compatible alias for callers that used the v1 name.
scan_pdfs = scan_inputs


def build_batch_items(paths: Sequence[Path], config: BatchConfig) -> list[BatchItem]:
    input_root = Path(config.input_root).expanduser().resolve()
    output_root = Path(config.output_root).expanduser().resolve()
    items: list[BatchItem] = []

    for source in paths:
        source = Path(source).resolve()
        try:
            relative = source.relative_to(input_root)
        except ValueError:
            relative = Path(source.name)
        base_dir = output_root / relative.parent if config.preserve_structure else output_root
        stem = safe_stem(source)

        if config.export_mode == "side_by_side":
            items.append(
                BatchItem(
                    source_pdf=source,
                    json_path=base_dir / f"{stem}_prospectus.json",
                    csv_path=base_dir / f"{stem}_review.csv",
                    pl_path=base_dir / f"{stem}_prospectus.pl",
                    jsonl_path=base_dir / f"{stem}_rag.jsonl",
                )
            )
        else:
            folder = base_dir / stem
            items.append(
                BatchItem(
                    source_pdf=source,
                    json_path=folder / "prospectus.json",
                    csv_path=folder / "review.csv",
                    pl_path=folder / "prospectus.pl",
                    jsonl_path=folder / "rag.jsonl",
                )
            )
    return items


def write_manifest(records: Sequence[dict[str, Any]], output_root: Path) -> Path:
    """Single, unambiguous manifest writer (v1 had two overlapping signatures)."""
    target = Path(output_root).resolve() / "batch_manifest.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "summary": {
            "total": len(records),
            "ok": sum(1 for r in records if r.get("status") == "ok"),
            "warn": sum(1 for r in records if r.get("status") == "warn"),
            "audit_failed": sum(1 for r in records if r.get("status") == "audit_error"),
            "skipped": sum(1 for r in records if r.get("status") == "skipped"),
            "failed": sum(1 for r in records if r.get("status") == "error"),
        },
        "records": records,
    }
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return target


def run_batch(config: BatchConfig) -> dict[str, Any]:
    """Extract every prospectus under config.input_root, then write a manifest."""
    sources = scan_inputs(config.input_root, config.recursive, config.include_patterns)
    items = build_batch_items(sources, config)
    records: list[dict[str, Any]] = []

    converter = None
    if any(item.source_pdf.suffix.lower() == ".pdf" for item in items):
        needs_conversion = any(
            not config.skip_existing or config.force_reconvert or not item.json_path.exists()
            or not item.json_path.with_name(
                f"{item.json_path.stem.replace('_prospectus', '')}_essentials.json"
            ).exists()
            for item in items if item.source_pdf.suffix.lower() == ".pdf"
        )
        if needs_conversion:
            try:
                ensure_docling_env()
                converter = get_shared_converter(device=config.device)
            except Exception as exc:
                print(f"[!] Could not pre-warm Docling: {exc}")

    iterable: Iterable[BatchItem] = items
    if RICH_AVAILABLE and console and items:
        iterable = track(items, description="Extracting prospectuses...")

    for item in iterable:
        essentials_path = item.json_path.with_name(
            f"{item.json_path.stem.replace('_prospectus', '')}_essentials.json"
        )
        record: dict[str, Any] = {
            "source": str(item.source_pdf),
            "json_path": str(item.json_path),
            "csv_path": str(item.csv_path),
            "status": "pending",
        }
        try:
            if (config.skip_existing and not config.force_reconvert and item.json_path.exists()
                    and (item.source_pdf.suffix.lower() != ".pdf" or essentials_path.exists())):
                record.update({"status": "skipped", "reason": "output already exists"})
                records.append(record)
                continue

            payload = process_prospectus(
                item.source_pdf,
                output_path=item.json_path,
                export_pl=config.write_pl,
                export_jsonl=config.write_jsonl,
                export_csv=config.write_csv,
                device=config.device,
                semantic_doc_path=config.semantic_doc,
                converter=converter,
                force_reconvert=True,
                quiet=True,
            )
            audit = payload["audit"]
            record.update(
                {
                    "status": "audit_error" if audit["status"] == "error" else audit["status"],
                    "program": payload.get("program"),
                    "degree": payload.get("degree"),
                    "college": payload.get("college"),
                    "effective_school_year": payload["metadata"].get("effective_school_year"),
                    "course_count": audit["total_courses"],
                    "total_units": audit["computed_total_units"],
                    "declared_total_units": audit["declared_total_units"],
                    "years_detected": audit["years_detected"],
                    "errors": audit["errors"],
                    "warning_count": len(audit["warnings"]),
                    "essentials_path": str(essentials_path)
                    if item.source_pdf.suffix.lower() == ".pdf" else None,
                }
            )
        except Exception as exc:
            record.update(
                {
                    "status": "error",
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                    "traceback": traceback.format_exc(limit=5),
                }
            )
        records.append(record)

    manifest_path = write_manifest(records, config.output_root) if config.write_manifest else None
    summary = {
        "total": len(records),
        "succeeded": sum(1 for r in records if r["status"] in {"ok", "warn"}),
        "audit_failed": sum(1 for r in records if r["status"] == "audit_error"),
        "skipped": sum(1 for r in records if r["status"] == "skipped"),
        "failed": sum(1 for r in records if r["status"] == "error"),
        "manifest_path": str(manifest_path) if manifest_path else None,
        "records": records,
    }
    return summary
