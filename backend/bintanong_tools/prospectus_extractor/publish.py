"""Staged output publication: write beside the target, publish file by file, manifest last."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping, Sequence
import json
import os
import shutil
import time
import traceback
import uuid

from .identity import file_sha256

PUBLISH_SCHEMA = "palsu-prospectus-publish-v1"
FAILED_DIR_NAME = "failed"


@dataclass(frozen=True)
class OutputNames:
    base: str
    final: Path
    essentials: Path
    prolog: Path
    rag: Path
    csv: Path
    markup: Path
    manifest: Path

    @property
    def failed_dir(self) -> Path:
        return self.final.parent / FAILED_DIR_NAME / self.base


def output_names(final_path: Path) -> OutputNames:
    """Companion file names, derived exactly as process_prospectus always derived them."""
    final = Path(final_path)
    base = final.stem.replace("_prospectus", "")
    return OutputNames(
        base=base,
        final=final,
        essentials=final.with_name(f"{base}_essentials.json"),
        prolog=final.with_name(f"{base}_prospectus.pl"),
        rag=final.with_name(f"{base}_rag.jsonl"),
        csv=final.with_name(f"{base}_review.csv"),
        markup=final.with_name(f"{base}_prospectus.md"),
        manifest=final.with_name(f"{base}_publish.json"),
    )


def write_text_lf(path: Path, text: str) -> None:
    """UTF-8 with \\n on every platform, so the same run hashes the same everywhere."""
    Path(path).write_bytes(text.encode("utf-8"))


def remove_stale_staging(parent: Path, base: str) -> None:
    """Delete staging directories a killed run left behind. One writer per output stem."""
    prefix = f".{base}.staging-"
    if not Path(parent).is_dir():
        return
    for entry in Path(parent).iterdir():
        if entry.is_dir() and entry.name.startswith(prefix):
            shutil.rmtree(entry, ignore_errors=True)


def new_staging_dir(parent: Path, base: str) -> Path:
    """A fresh directory beside the target, so every replace stays on one filesystem."""
    parent = Path(parent)
    remove_stale_staging(parent, base)
    stage = parent / f".{base}.staging-{uuid.uuid4().hex[:8]}"
    stage.mkdir(parents=True)
    return stage


class ReplaceFailed(OSError):
    """A finished file could not be moved over its target (on Windows: the target stayed locked)."""


def replace_file(source: Path, target: Path, attempts: int = 5, delay: float = 0.2) -> None:
    """os.replace with a short retry: Windows scanners and indexers briefly lock fresh files.

    The one replace used by the cache writer (loader) and by publication. After the last
    attempt ReplaceFailed names both paths; the target keeps what it held and the source
    is left in place (a failed publication copies it to failed/<base>/).
    """
    for attempt in range(attempts):
        try:
            os.replace(source, target)
            return
        except PermissionError as exc:
            if attempt == attempts - 1:
                raise ReplaceFailed(
                    f"could not replace {target} with {source} after {attempts} "
                    f"attempts (the target stayed locked): {exc}"
                ) from exc
            time.sleep(delay * (attempt + 1))


def read_manifest(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if (
        not isinstance(data, dict)
        or data.get("schema") != PUBLISH_SCHEMA
        or not isinstance(data.get("files"), dict)
        or not isinstance(data.get("run_key"), str)
    ):
        return None
    return data


def verify_published(directory: Path, manifest: Mapping[str, Any]) -> tuple[bool, str]:
    """Does every file the manifest lists still hash to the value recorded when it was published?"""
    for name, digest in manifest["files"].items():
        target = Path(directory) / name
        if not target.is_file():
            return False, f"{name} is missing"
        if file_sha256(target) != digest:
            return False, f"{name} changed since it was published"
    return True, "all files match"


def publish_staged(
    stage: Path,
    names: OutputNames,
    outputs: Sequence[str],
    cache_files: Sequence[str],
    run_identity: Mapping[str, Any],
    audit_status: str,
) -> Path:
    """Move a finished stage into place, one file at a time.

    `outputs` are file names inside `stage` in publish order; the main JSON must be last.
    `cache_files` (raw Docling JSON and its meta) are published first and are not part of
    the manifest: they have their own identity record. The manifest is published very last.
    A crash part-way leaves an old manifest whose hashes no longer match: verify_published
    reports the set incomplete, so nothing trusts it.
    """
    stage = Path(stage)
    if not outputs or outputs[-1] != names.final.name:
        raise ValueError("the main JSON must be the last staged output")
    target_dir = names.final.parent
    target_dir.mkdir(parents=True, exist_ok=True)

    previous = read_manifest(names.manifest)
    previous_files = set(previous["files"]) if previous else set()

    manifest = {
        "schema": PUBLISH_SCHEMA,
        "run_key": run_identity["run_key"],
        "audit_status": audit_status,
        "published_at": datetime.now().isoformat(timespec="seconds"),
        "run_identity": dict(run_identity),
        "files": {name: file_sha256(stage / name) for name in outputs},
    }
    write_text_lf(stage / names.manifest.name, json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

    for name in [*cache_files, *outputs, names.manifest.name]:
        replace_file(stage / name, target_dir / name)

    # Stale: whatever the previous manifest listed, plus every known companion of this base
    # (an output set written before publish manifests existed has none), that this run did
    # not produce. The cache files and the manifest itself are never stale companions.
    companions = {path.name for path in (names.essentials, names.prolog, names.rag, names.csv, names.markup)}
    keep = {*outputs, *cache_files, names.manifest.name}
    for stale in sorted((previous_files | companions) - keep):
        if Path(stale).name != stale:  # a tampered manifest must not reach outside this folder
            continue
        try:
            (target_dir / stale).unlink(missing_ok=True)
        except OSError as exc:  # not in the new manifest, so it cannot pass for current output
            print(f"[!] Could not remove stale companion {target_dir / stale}: {exc}")
    return names.manifest


def write_failure(
    names: OutputNames,
    error: BaseException,
    input_path: Path,
    run_identity: Mapping[str, Any] | None,
    stage: Path | None,
) -> Path | None:
    """Keep what a failed run produced under failed/<base>/, never over published output."""
    directory = names.failed_dir
    try:
        directory.mkdir(parents=True, exist_ok=True)
        for old in directory.iterdir():
            if old.is_file():
                old.unlink()
        if stage is not None and Path(stage).is_dir():
            for staged in Path(stage).iterdir():
                if staged.is_file():
                    shutil.copy2(staged, directory / staged.name)
        record = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": "".join(traceback.format_exception(error)),
            "input_path": str(input_path),
            "run_identity": dict(run_identity) if run_identity else None,
            "failed_at": datetime.now().isoformat(timespec="seconds"),
        }
        write_text_lf(directory / "failure.json", json.dumps(record, indent=2, ensure_ascii=False) + "\n")
        return directory
    except OSError as exc:
        print(f"[!] Could not write failure diagnostics to {directory}: {exc}")
        return None


def clear_failure(names: OutputNames) -> None:
    """A later successful publish makes older diagnostics misleading."""
    shutil.rmtree(names.failed_dir, ignore_errors=True)
    try:
        names.failed_dir.parent.rmdir()  # only succeeds when failed/ is now empty
    except OSError:
        pass
