"""In-process batch engine and manifest."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from pathlib import Path, PureWindowsPath
from typing import Any
from typing import Iterable
from typing import Sequence
import json
import re
import traceback

from .common import MANIFEST_SCHEMA_VERSION, RICH_AVAILABLE, console

if RICH_AVAILABLE:
    from .common import track
from .identity import InputSnapshot, package_sha256, run_identity
from .paths import DEFAULT_SEMANTIC_DOC, find_default_input_root, find_default_output_root
from .pipeline import process_prospectus
from .publish import output_names, read_manifest, verify_published, write_text_lf


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
    write_md: bool = True
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
        pattern_path = PureWindowsPath(pattern)
        if pattern_path.anchor or ".." in pattern_path.parts:
            raise ValueError(f"Input pattern must stay within input root: {pattern!r}")
        iterator = root.rglob(pattern) if recursive else root.glob(pattern)
        for path in iterator:
            if not path.is_file():
                continue
            relative = path.relative_to(root)
            if any(part.lower() in IGNORED_DIR_PARTS for part in relative.parts[:-1]):
                continue
            # A marker identifies this run subtree, even when selected as the root.
            if any((root / directory / "failure.json").is_file()
                   for directory in (relative.parent, *relative.parent.parents)):
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
    write_text_lf(target, json.dumps(payload, indent=2, ensure_ascii=False))
    return target


def skip_check(
    item: BatchItem, config: BatchConfig, package_hash: str, *, snapshot: InputSnapshot | None = None,
) -> tuple[bool, str]:
    """May this item be skipped? Returns (skip, reason). Never skips a failed audit."""
    if not config.skip_existing:
        return False, "skip-existing not requested"
    if config.force_reconvert:
        return False, "--force given"
    names = output_names(item.json_path)
    manifest = read_manifest(names.manifest)
    if manifest is None:
        return False, "no publish manifest"
    reusable = manifest["run_identity"].get("skip_reusable")
    if reusable is False:
        return False, "previous run used supplied context"
    if reusable is not True:
        return False, "previous run skip eligibility is unknown"
    status = manifest.get("audit_status")
    if status not in ("ok", "warn"):
        return False, f"previous audit status was {status}"
    expected = run_identity(item.source_pdf, config.semantic_doc, package_hash=package_hash, snapshot=snapshot)
    if manifest["run_key"] != expected["run_key"]:
        return False, "input, settings, parser or schema changed"
    intact, why = verify_published(names.final.parent, manifest)
    if not intact:
        return False, why
    wanted = [names.final.name]
    if item.source_pdf.suffix.lower() == ".pdf":
        wanted.append(names.essentials.name)
    if config.write_csv:
        wanted.append(names.csv.name)
    if config.write_pl:
        wanted.append(names.prolog.name)
    if config.write_jsonl:
        wanted.append(names.rag.name)
    if config.write_md:
        wanted.append(names.markup.name)
    missing = [name for name in wanted if name not in manifest["files"]]
    if missing:
        return False, f"requested outputs not in last run: {missing}"
    return True, "identical run identity"


def run_batch(config: BatchConfig) -> dict[str, Any]:
    """Extract every prospectus under config.input_root, then write a manifest."""
    sources = scan_inputs(config.input_root, config.recursive, config.include_patterns)
    items = build_batch_items(sources, config)
    records: list[dict[str, Any]] = []

    package_hash = package_sha256()
    # The loader requests its shared converter lazily, after attempting cache reuse.
    work: Iterable[BatchItem] = items
    if RICH_AVAILABLE and console and items:
        work = track(work, description="Extracting prospectuses...")

    for item in work:
        names = output_names(item.json_path)
        essentials_path = names.essentials
        record: dict[str, Any] = {
            "source": str(item.source_pdf),
            "json_path": str(item.json_path),
            "csv_path": str(item.csv_path),
            "status": "pending",
            "skip_check": "identity check pending",
        }
        try:
            captured = InputSnapshot(item.source_pdf)
            try:
                skip, why = skip_check(item, config, package_hash, snapshot=captured)
            except Exception as exc:
                skip, why = False, f"identity check failed: {type(exc).__name__}: {exc}"
            record["skip_check"] = why
            if skip:
                record.update({"status": "skipped", "reason": f"unchanged: {why}"})
                records.append(record)
                captured = None
                continue

            payload = process_prospectus(
                item.source_pdf,
                output_path=item.json_path,
                export_pl=config.write_pl,
                export_jsonl=config.write_jsonl,
                export_csv=config.write_csv,
                export_md=config.write_md,
                device=config.device,
                semantic_doc_path=config.semantic_doc,
                force_reconvert=config.force_reconvert,
                quiet=True,
                _snapshot=captured,
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
                    "publish_manifest": str(names.manifest),
                }
            )
        except Exception as exc:
            record.update(
                {
                    "status": "error",
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                    "traceback": traceback.format_exc(limit=5),
                    "failed_dir": str(names.failed_dir),
                }
            )
        records.append(record)
        # Release this item's bytes before capturing the next item.
        captured = None

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
