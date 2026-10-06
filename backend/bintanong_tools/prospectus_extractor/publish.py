"""Staged output publication: write beside the target, publish file by file, manifest last."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping, Sequence
import json
import os
import re
import shutil
import time
import traceback
import uuid

from .identity import IDENTITY_VERSION, bytes_sha256, conversion_identity, file_sha256

PUBLISH_SCHEMA = "palsu-prospectus-publish-v2"
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


def _staging_prefix(base: str) -> str:
    return f".s-{bytes_sha256(base.encode('utf-8'))[:32]}-"


def remove_stale_staging(parent: Path, base: str) -> None:
    """Delete staging directories a killed run left behind. One writer per output stem."""
    prefix = _staging_prefix(base)
    if not Path(parent).is_dir():
        return
    for entry in Path(parent).iterdir():
        if entry.is_dir() and entry.name.startswith(prefix):
            shutil.rmtree(entry, ignore_errors=True)


def new_staging_dir(parent: Path, base: str) -> Path:
    """A fresh directory beside the target, so every replace stays on one filesystem."""
    parent = Path(parent)
    remove_stale_staging(parent, base)
    stage = parent / f"{_staging_prefix(base)}{uuid.uuid4().hex[:8]}"
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


def _leaf_name(value: Any) -> bool:
    return (
        isinstance(value, str) and bool(value) and value not in (".", "..")
        and not any(char in value for char in "/\\:\x00")
        and not value.endswith((".", " "))
    )


def _sha256(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _manifest_error(manifest: Any) -> str | None:
    """Validate the manifest before trusting any path or digest it declares."""
    if not isinstance(manifest, Mapping) or manifest.get("schema") != PUBLISH_SCHEMA:
        return "unsupported publish manifest"
    files, caches = manifest.get("files"), manifest.get("cache_files")
    if not isinstance(files, Mapping) or not files or not isinstance(caches, Mapping):
        return "invalid publish file maps"
    all_names = [*files, *caches]
    if any(not _leaf_name(name) for name in all_names):
        return "invalid publish file name"
    if len({name.casefold() for name in all_names}) != len(all_names):
        return "duplicate publish file name"
    if any(not _sha256(digest) for digest in [*files.values(), *caches.values()]):
        return "invalid publish digest"
    main = manifest.get("main_file")
    if not _leaf_name(main) or main not in files:
        return "missing main file binding"
    identity = manifest.get("run_identity")
    if (not isinstance(identity, Mapping) or not _sha256(manifest.get("run_key"))
            or identity.get("run_key") != manifest["run_key"]):
        return "invalid run identity"
    if identity.get("cache_files") != caches or not _sha256(identity.get("input_sha256")):
        return "invalid cache or input identity binding"
    if identity.get("input_kind") == "pdf":
        raw_names = [name for name in caches if name.endswith("_docling.json")]
        if (len(raw_names) != 1 or len(caches) != 2
                or raw_names[0][:-5] + ".meta.json" not in caches):
            return "missing PDF cache pair binding"
        settings = identity.get("conversion_settings")
        if (identity.get("identity_version") != IDENTITY_VERSION
                or identity.get("pdf_sha256") != identity["input_sha256"]
                or not isinstance(settings, Mapping)
                or identity.get("conversion_identity") != conversion_identity(
                    identity["input_sha256"], settings)):
            return "invalid PDF conversion identity"
    elif identity.get("input_kind") == "docling-json":
        if (caches or identity.get("pdf_sha256") is not None
                or identity.get("conversion_settings") is not None
                or identity.get("conversion_identity") is not None):
            return "invalid review input cache binding"
    else:
        return "unsupported input kind"
    return None


def read_manifest(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(Path(path).read_bytes().decode("utf-8"))
        return data if _manifest_error(data) is None else None
    except (OSError, ValueError, TypeError):
        return None


def verify_published(directory: Path, manifest: Mapping[str, Any]) -> tuple[bool, str]:
    """Check one bytes snapshot per file, including main/cache identity cross-bindings."""
    try:
        error = _manifest_error(manifest)
        if error:
            return False, error
        directory = Path(directory).resolve()
        snapshots = {}
        for name, digest in {**manifest["files"], **manifest["cache_files"]}.items():
            target = directory / name
            if target.resolve().parent != directory:
                return False, f"{name} resolves outside the output directory"
            if not target.is_file():
                return False, f"{name} is missing"
            data = target.read_bytes()
            if bytes_sha256(data) != digest:
                return False, f"{name} changed since it was published"
            snapshots[name] = data
        main = json.loads(snapshots[manifest["main_file"]].decode("utf-8"))
        identity = manifest["run_identity"]
        if not isinstance(main, Mapping) or main.get("run_identity") != identity:
            return False, "main run identity does not match the manifest"
        if identity["input_kind"] == "pdf":
            raw_name = next(name for name in manifest["cache_files"] if name.endswith("_docling.json"))
            meta = json.loads(snapshots[raw_name[:-5] + ".meta.json"].decode("utf-8"))
            raw = json.loads(snapshots[raw_name].decode("utf-8"))
            if not isinstance(raw, Mapping):
                return False, "cached JSON is not a document"
            if (not isinstance(meta, Mapping)
                    or meta.get("identity_version") != identity["identity_version"]
                    or meta.get("pdf_sha256") != identity["pdf_sha256"]
                    or meta.get("conversion_identity") != identity["conversion_identity"]
                    or meta.get("conversion_settings") != identity["conversion_settings"]
                    or meta.get("raw_json_sha256") != manifest["cache_files"][raw_name]):
                return False, "cache metadata does not match the main run identity"
        return True, "all files match"
    except (OSError, ValueError, TypeError) as exc:
        return False, f"published set is unreadable ({type(exc).__name__})"


def publish_staged(
    stage: Path,
    names: OutputNames,
    outputs: Sequence[str],
    cache_files: Sequence[str],
    run_identity: Mapping[str, Any],
    audit_status: str,
    *,
    cache_hashes: Mapping[str, str] | None = None,
) -> Path:
    """Publish companions, main JSON, captured cache pair, then the v2 manifest.

    File replacements are not an atomic set. Manifest-last verification detects mixed
    generations; byte-identical early replacements may leave the old set coherent.
    """
    stage = Path(stage)
    if not outputs or outputs[-1] != names.final.name:
        raise ValueError("the main JSON must be the last staged output")
    all_names = [*outputs, *cache_files, names.manifest.name]
    if (any(not _leaf_name(name) for name in all_names)
            or len({name.casefold() for name in all_names}) != len(all_names)):
        raise ValueError("invalid or duplicate staged file names")
    hashes = dict(cache_hashes) if cache_hashes is not None else {}
    if set(cache_files) != set(hashes):
        raise ValueError("staged cache files must match the captured cache hashes")
    manifest = {
        "schema": PUBLISH_SCHEMA,
        "run_key": run_identity.get("run_key"),
        "audit_status": audit_status,
        "published_at": datetime.now().isoformat(timespec="seconds"),
        "run_identity": dict(run_identity),
        "main_file": names.final.name,
        "files": {name: file_sha256(stage / name) for name in outputs},
        "cache_files": hashes,
    }
    valid, why = verify_published(stage, manifest)
    if not valid:
        raise ValueError(f"Invalid staged publication: {why}")
    write_text_lf(stage / names.manifest.name, json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    target_dir = names.final.parent
    target_dir.mkdir(parents=True, exist_ok=True)
    for name in [*outputs, *cache_files, names.manifest.name]:
        replace_file(stage / name, target_dir / name)

    companions = {path.name for path in (names.essentials, names.prolog, names.rag, names.csv, names.markup)}
    for stale in sorted(companions - set(outputs)):
        try:
            (target_dir / stale).unlink(missing_ok=True)
        except OSError as exc:
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
        record = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": "".join(traceback.format_exception(error)),
            "input_path": str(input_path),
            "run_identity": dict(run_identity) if run_identity else None,
            "failed_at": datetime.now().isoformat(timespec="seconds"),
        }
        # Marker first: a copy that fails midway must still leave a recognisable diagnostics folder.
        write_text_lf(directory / "failure.json", json.dumps(record, indent=2, ensure_ascii=False) + "\n")
        if stage is not None and Path(stage).is_dir():
            for staged in Path(stage).iterdir():
                if staged.is_file():
                    shutil.copy2(staged, directory / staged.name)
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
