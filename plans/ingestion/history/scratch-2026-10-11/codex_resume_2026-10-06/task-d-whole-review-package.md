# Review package task-d-whole
Worktree: C:\Users\Hawksprey\source\repos\Bintanong-wt\phase-d
BASE: 641523d212839084da03d966ffbfca66c7e83e42
TIP: 08a8290d7257485d695c4d2b05be5cf6db730d7b

## Commits
08a8290 docs: record the safe cache and output publication design and its evidence
c40a38c fix(prospectus): wire force reconversion into the TUI
10c2d8b fix(prospectus): refuse reuse of context-created outputs
4320327 fix(prospectus): shorten default and intermediate output paths
52da4aa fix(prospectus): write batch manifest and review CSV with LF
4a0cdb7 fix(prospectus): reject glob patterns outside input root
df5eec4 fix(prospectus): scope discovery exclusions to selected inputs
597e8c0 fix: bind prospectus publication to captured cache snapshots
53e3c00 fix: bind prospectus conversion to immutable input bytes

## Stat
 backend/bintanong_tools/prospectus.py              |   5 +-
 .../bintanong_tools/prospectus_extractor/batch.py  |  69 +--
 .../prospectus_extractor/identity.py               |  42 +-
 .../bintanong_tools/prospectus_extractor/loader.py |  95 +++-
 .../bintanong_tools/prospectus_extractor/paths.py  |   2 +-
 .../prospectus_extractor/pipeline.py               |  43 +-
 .../prospectus_extractor/publish.py                | 174 +++++--
 .../bintanong_tools/prospectus_extractor/tui.py    |   9 +-
 .../bintanong_tools/prospectus_extractor/views.py  |   2 +-
 docs/decisions/prospectus-cache-and-publication.md |  53 +++
 plans/plan_current_progress/current_progress.md    |  13 +-
 .../extractor_split_progress.md                    | 501 ++++++++++++++++++++-
 tests/conftest.py                                  |   4 +-
 tests/test_prospectus_authority.py                 |  21 +-
 tests/test_prospectus_batch_skip.py                | 341 +++++++++++++-
 tests/test_prospectus_cache.py                     |  49 +-
 tests/test_prospectus_input_snapshot.py            | 223 +++++++++
 tests/test_prospectus_markup.py                    |   8 +-
 tests/test_prospectus_publication.py               | 284 +++++++++++-
 tests/test_prospectus_publish.py                   | 275 ++++++++++-
 20 files changed, 2062 insertions(+), 151 deletions(-)

## Diff
```diff
diff --git a/backend/bintanong_tools/prospectus.py b/backend/bintanong_tools/prospectus.py
index a12ce01..d4fd45e 100644
--- a/backend/bintanong_tools/prospectus.py
+++ b/backend/bintanong_tools/prospectus.py
@@ -10,12 +10,15 @@ from .prospectus_extractor import identity
 
 
 @dataclass(frozen=True)
 class ProvisionalSource:
     pdf_sha256: str
     source_locator: str
     source_verification: Literal["pending"] = field(default="pending", init=False)
 
     def verify_pdf(self, pdf_path: Path) -> None:
         actual_hash = identity.file_sha256(pdf_path)  # the one PDF-hash owner
+        self.verify_digest(actual_hash)
+
+    def verify_digest(self, actual_hash: str) -> None:
         if actual_hash != self.pdf_sha256:
-            raise ValueError(f"PDF hash mismatch for {pdf_path}")
+            raise ValueError(f"PDF hash mismatch for {self.source_locator}")
diff --git a/backend/bintanong_tools/prospectus_extractor/batch.py b/backend/bintanong_tools/prospectus_extractor/batch.py
index ea6ed10..44e3309 100644
--- a/backend/bintanong_tools/prospectus_extractor/batch.py
+++ b/backend/bintanong_tools/prospectus_extractor/batch.py
@@ -1,34 +1,33 @@
 """In-process batch engine and manifest."""
 
 from __future__ import annotations
 
 from dataclasses import dataclass
 from dataclasses import field
 from datetime import datetime
-from pathlib import Path
+from pathlib import Path, PureWindowsPath
 from typing import Any
 from typing import Iterable
 from typing import Sequence
 import json
 import re
 import traceback
 
 from .common import MANIFEST_SCHEMA_VERSION, RICH_AVAILABLE, console
 
 if RICH_AVAILABLE:
     from .common import track
-from .docling_env import ensure_docling_env, get_shared_converter
-from .identity import package_sha256, run_identity
+from .identity import InputSnapshot, package_sha256, run_identity
 from .paths import DEFAULT_SEMANTIC_DOC, find_default_input_root, find_default_output_root
 from .pipeline import process_prospectus
-from .publish import output_names, read_manifest, verify_published
+from .publish import output_names, read_manifest, verify_published, write_text_lf
 
 
 def safe_stem(path: Path) -> str:
     stem = Path(path).stem.strip()
     if stem.endswith("_docling"):  # batching saved Docling JSON should not double the suffix
         stem = stem[: -len("_docling")]
     stem = re.sub(r"[^A-Za-z0-9._ -]+", "_", stem)
     return re.sub(r"\s+", " ", stem).strip() or "prospectus"
 
 
@@ -62,40 +61,47 @@ class BatchItem:
     jsonl_path: Path
 
     @property
     def pdf_path(self) -> Path:
         return self.source_pdf
 
 
 IGNORED_DIR_PARTS = {
     "palsu_jsonified_output", "docling_jsonified_output", ".venv", ".docling-venv",
     "__pycache__", ".git", "node_modules",
-    "failed",  # publish.write_failure diagnostics hold copies of *_docling.json; never inputs
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
+        pattern_path = PureWindowsPath(pattern)
+        if pattern_path.anchor or ".." in pattern_path.parts:
+            raise ValueError(f"Input pattern must stay within input root: {pattern!r}")
         iterator = root.rglob(pattern) if recursive else root.glob(pattern)
         for path in iterator:
             if not path.is_file():
                 continue
-            if any(part.lower() in IGNORED_DIR_PARTS for part in path.parts):
+            relative = path.relative_to(root)
+            if any(part.lower() in IGNORED_DIR_PARTS for part in relative.parts[:-1]):
+                continue
+            # A marker identifies this run subtree, even when selected as the root.
+            if any((root / directory / "failure.json").is_file()
+                   for directory in (relative.parent, *relative.parent.parents)):
                 continue
             if path.name.endswith("_docling.json") and pattern == "*.json":
                 pass  # explicitly requested
             if path not in found:
                 found.append(path)
     return sorted(found)
 
 
 # Backwards-compatible alias for callers that used the v1 name.
 scan_pdfs = scan_inputs
@@ -149,38 +155,45 @@ def write_manifest(records: Sequence[dict[str, Any]], output_root: Path) -> Path
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
-    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
+    write_text_lf(target, json.dumps(payload, indent=2, ensure_ascii=False))
     return target
 
 
-def skip_check(item: BatchItem, config: BatchConfig, package_hash: str) -> tuple[bool, str]:
+def skip_check(
+    item: BatchItem, config: BatchConfig, package_hash: str, *, snapshot: InputSnapshot | None = None,
+) -> tuple[bool, str]:
     """May this item be skipped? Returns (skip, reason). Never skips a failed audit."""
     if not config.skip_existing:
         return False, "skip-existing not requested"
     if config.force_reconvert:
         return False, "--force given"
     names = output_names(item.json_path)
     manifest = read_manifest(names.manifest)
     if manifest is None:
         return False, "no publish manifest"
+    reusable = manifest["run_identity"].get("skip_reusable")
+    if reusable is False:
+        return False, "previous run used supplied context"
+    if reusable is not True:
+        return False, "previous run skip eligibility is unknown"
     status = manifest.get("audit_status")
     if status not in ("ok", "warn"):
         return False, f"previous audit status was {status}"
-    expected = run_identity(item.source_pdf, config.semantic_doc, package_hash=package_hash)
+    expected = run_identity(item.source_pdf, config.semantic_doc, package_hash=package_hash, snapshot=snapshot)
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
@@ -196,72 +209,60 @@ def skip_check(item: BatchItem, config: BatchConfig, package_hash: str) -> tuple
     return True, "identical run identity"
 
 
 def run_batch(config: BatchConfig) -> dict[str, Any]:
     """Extract every prospectus under config.input_root, then write a manifest."""
     sources = scan_inputs(config.input_root, config.recursive, config.include_patterns)
     items = build_batch_items(sources, config)
     records: list[dict[str, Any]] = []
 
     package_hash = package_sha256()
-    decisions: list[tuple[bool, str]] = []
-    for item in items:
-        try:
-            decisions.append(skip_check(item, config, package_hash))
-        except Exception as exc:  # an unreadable PDF is reported by the run itself
-            decisions.append((False, f"identity check failed: {type(exc).__name__}: {exc}"))
-
-    converter = None
-    needs_conversion = any(
-        not skipped
-        for item, (skipped, _why) in zip(items, decisions)
-        if item.source_pdf.suffix.lower() == ".pdf"
-    )
-    if needs_conversion:
-        try:
-            ensure_docling_env()
-            converter = get_shared_converter(device=config.device)
-        except Exception as exc:
-            print(f"[!] Could not pre-warm Docling: {exc}")
-
-    work: Iterable[tuple[BatchItem, tuple[bool, str]]] = list(zip(items, decisions))
+    # The loader requests its shared converter lazily, after attempting cache reuse.
+    work: Iterable[BatchItem] = items
     if RICH_AVAILABLE and console and items:
         work = track(work, description="Extracting prospectuses...")
 
-    for item, (skip, why) in work:
+    for item in work:
         names = output_names(item.json_path)
         essentials_path = names.essentials
         record: dict[str, Any] = {
             "source": str(item.source_pdf),
             "json_path": str(item.json_path),
             "csv_path": str(item.csv_path),
             "status": "pending",
-            "skip_check": why,
+            "skip_check": "identity check pending",
         }
         try:
+            captured = InputSnapshot(item.source_pdf)
+            try:
+                skip, why = skip_check(item, config, package_hash, snapshot=captured)
+            except Exception as exc:
+                skip, why = False, f"identity check failed: {type(exc).__name__}: {exc}"
+            record["skip_check"] = why
             if skip:
                 record.update({"status": "skipped", "reason": f"unchanged: {why}"})
                 records.append(record)
+                captured = None
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
-                converter=converter,
                 force_reconvert=config.force_reconvert,
                 quiet=True,
+                _snapshot=captured,
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
@@ -279,20 +280,22 @@ def run_batch(config: BatchConfig) -> dict[str, Any]:
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
+        # Release this item's bytes before capturing the next item.
+        captured = None
 
     manifest_path = write_manifest(records, config.output_root) if config.write_manifest else None
     summary = {
         "total": len(records),
         "succeeded": sum(1 for r in records if r["status"] in {"ok", "warn"}),
         "audit_failed": sum(1 for r in records if r["status"] == "audit_error"),
         "skipped": sum(1 for r in records if r["status"] == "skipped"),
         "failed": sum(1 for r in records if r["status"] == "error"),
         "manifest_path": str(manifest_path) if manifest_path else None,
         "records": records,
diff --git a/backend/bintanong_tools/prospectus_extractor/identity.py b/backend/bintanong_tools/prospectus_extractor/identity.py
index 41c5165..fac08f6 100644
--- a/backend/bintanong_tools/prospectus_extractor/identity.py
+++ b/backend/bintanong_tools/prospectus_extractor/identity.py
@@ -1,37 +1,62 @@
 """Identity of a conversion and of an output set: what each was made from."""
 
 from __future__ import annotations
 
+from dataclasses import dataclass
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
 
 
+def bytes_sha256(data: bytes) -> str:
+    """Shared owner of byte digests for input and cache identities."""
+    return hashlib.sha256(data).hexdigest()
+
+
 def file_sha256(path: Path) -> str:
-    """The one place a PDF or cache file is hashed (fixer, batch record, cache and publish all call it)."""
-    digest = hashlib.sha256()
-    with Path(path).open("rb") as handle:
-        for block in iter(lambda: handle.read(1 << 20), b""):
-            digest.update(block)
-    return digest.hexdigest()
+    return bytes_sha256(Path(path).read_bytes())
+
+
+@dataclass(frozen=True, init=False)
+class InputSnapshot:
+    """Capture a path's immutable bytes and digest together; never accept a declared digest."""
+
+    path: Path
+    data: bytes
+    sha256: str
+
+    def __init__(self, path: Path):
+        path = Path(path).resolve()
+        data = path.read_bytes()
+        object.__setattr__(self, "path", path)
+        object.__setattr__(self, "data", data)
+        object.__setattr__(self, "sha256", bytes_sha256(data))
+
+    def require_path(self, path: Path) -> None:
+        if Path(path).resolve() != self.path:
+            raise ValueError(f"Snapshot path does not match input: {path}")
+
+    def verify_unchanged(self) -> None:
+        if self.path.read_bytes() != self.data:
+            raise ValueError(f"Input bytes changed since capture: {self.path}")
 
 
 def package_sha256(package: Path = PACKAGE_DIR) -> str:
     """One hash over every module, so any parser change changes the recorded hash."""
     digest = hashlib.sha256()
     for path in sorted(package.glob("*.py")):
         digest.update(path.name.encode())
         digest.update(path.read_bytes().replace(b"\r\n", b"\n"))
     return digest.hexdigest()
 
@@ -79,31 +104,34 @@ def conversion_identity(pdf_sha256: str, settings: Mapping[str, Any]) -> str:
     )
 
 
 def run_identity(
     input_path: Path,
     semantic_doc: Path | None,
     *,
     schema_version: str | None = None,
     package_hash: str | None = None,
     settings: Mapping[str, Any] | None = None,
+    snapshot: InputSnapshot | None = None,
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
-    input_hash = file_sha256(input_path)
+    captured = snapshot if snapshot is not None else InputSnapshot(input_path)
+    captured.require_path(input_path)
+    input_hash = captured.sha256
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
diff --git a/backend/bintanong_tools/prospectus_extractor/loader.py b/backend/bintanong_tools/prospectus_extractor/loader.py
index fef5126..85c22ec 100644
--- a/backend/bintanong_tools/prospectus_extractor/loader.py
+++ b/backend/bintanong_tools/prospectus_extractor/loader.py
@@ -1,25 +1,26 @@
 """Docling-to-evidence adapter, conversion cache and document loading."""
 
 from __future__ import annotations
 
+from dataclasses import dataclass
+from io import BytesIO
 from pathlib import Path
 from typing import Any
 from typing import Mapping
 from typing import Sequence
-import hashlib
 import json
 import os
 import tempfile
 
 from .docling_env import _docling_importable, ensure_docling_env, get_shared_converter, load_docling
-from .identity import IDENTITY_VERSION, conversion_identity, conversion_settings, file_sha256
+from .identity import IDENTITY_VERSION, InputSnapshot, bytes_sha256, conversion_identity, conversion_settings
 from .publish import ReplaceFailed, replace_file
 from .text import clean_str, match_semester_labels, match_year_label
 from .grid import extract_table_year_contexts
 from .layout import detect_column_groups, is_header_row
 from .evidence import LoadedDocument, NormalizedCell, NormalizedTable, ProspectusEvidence, SourceBBox, normalized_table_from_grid, project_table_to_grid
 
 
 def _page_from_mapping(value: Any, default: int | None = None) -> int | None:
     if not isinstance(value, Mapping):
         return default
@@ -301,45 +302,57 @@ def _conversion_errors(result: Any) -> list[str]:
 def _cache_meta_path(raw_json_path: Path) -> Path:
     return raw_json_path.with_name(raw_json_path.stem + ".meta.json")
 
 
 def _write_bytes_atomic(path: Path, data: bytes) -> None:
     """Write a temp file of this call's own beside the target, then replace: a reader
     never sees half a file and two writers never share a temp file. If the replace
     fails (publish.ReplaceFailed after retries), the temp is removed."""
     path = Path(path)
     path.parent.mkdir(parents=True, exist_ok=True)
-    handle, temp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
+    handle, temp_name = tempfile.mkstemp(dir=path.parent, prefix=".t-", suffix=".tmp")
     temp = Path(temp_name)
     try:
         with os.fdopen(handle, "wb") as stream:
             stream.write(data)
         replace_file(temp, path)
     except BaseException:
         temp.unlink(missing_ok=True)
         raise
 
 
-def load_reusable_cache(
+@dataclass(frozen=True)
+class DocumentLoadResult:
+    document: LoadedDocument
+    raw_json_path: Path | None
+    cache_status: str
+    raw_json_bytes: bytes | None = None
+    raw_json_sha256: str | None = None
+    meta_bytes: bytes | None = None
+    meta_sha256: str | None = None
+
+
+def _load_reusable_cache_result(
     raw_json_path: Path, meta_path: Path, pdf_sha256: str, settings: Mapping[str, Any]
-) -> tuple[LoadedDocument | None, str]:
+) -> tuple[DocumentLoadResult | None, str]:
     """The cached raw Docling JSON as a document when it may stand in for a fresh
     conversion, else (None, reason). Any doubt is a miss, never an error.
 
     The record's `pdf_sha256` and `conversion_settings` must each equal the current ones
     and its `conversion_identity` must be the identity of exactly those. The JSON is read
     once; the digest is checked on those bytes and those same bytes are parsed, so a
     writer replacing the file meanwhile cannot slip other content in.
     """
     expected_identity = conversion_identity(pdf_sha256, settings)
     try:
-        meta = json.loads(Path(meta_path).read_bytes().decode("utf-8"))
+        meta_bytes = Path(meta_path).read_bytes()
+        meta = json.loads(meta_bytes.decode("utf-8"))
     except FileNotFoundError:
         return None, "cached Docling JSON has no identity record"
     except (OSError, ValueError):
         return None, "identity record is unreadable"
     if (
         not isinstance(meta, dict)
         or meta.get("identity_version") != IDENTITY_VERSION
         or "conversion_identity" not in meta
     ):
         return None, "identity record is from an older version"
@@ -348,87 +361,105 @@ def load_reusable_cache(
     if meta.get("pdf_sha256") != pdf_sha256:
         return None, "identity record names other PDF bytes"
     if meta.get("conversion_settings") != dict(settings):
         return None, "identity record names other conversion settings"
     try:
         raw_bytes = Path(raw_json_path).read_bytes()
     except FileNotFoundError:
         return None, "no cached Docling JSON"
     except OSError:
         return None, "cached Docling JSON is unreadable"
-    if meta.get("raw_json_sha256") != hashlib.sha256(raw_bytes).hexdigest():
+    raw_hash = bytes_sha256(raw_bytes)
+    if meta.get("raw_json_sha256") != raw_hash:
         return None, "cached JSON does not match its identity record"
     try:
         data = json.loads(raw_bytes.decode("utf-8"))
         if not isinstance(data, dict):
             return None, "cached Docling JSON is not a document"
-        return load_from_raw_json(data), "identity matches"
+        return DocumentLoadResult(
+            load_from_raw_json(data), raw_json_path, "reused", raw_bytes, raw_hash,
+            meta_bytes, bytes_sha256(meta_bytes),
+        ), "identity matches"
     except ValueError as exc:  # bad UTF-8, bad JSON, or a dict Docling rejects
         return None, f"cached Docling JSON is corrupt ({type(exc).__name__})"
 
 
-def load_document(
+def load_reusable_cache(
+    raw_json_path: Path, meta_path: Path, pdf_sha256: str, settings: Mapping[str, Any]
+) -> tuple[LoadedDocument | None, str]:
+    result, reason = _load_reusable_cache_result(raw_json_path, meta_path, pdf_sha256, settings)
+    return (result.document if result is not None else None), reason
+
+
+def load_document_result(
     input_path: Path,
     device: str = "auto",
     force_reconvert: bool = True,
     converter: Any = None,
     raw_json_path: Path | None = None,
     stage_dir: Path | None = None,
-) -> tuple[LoadedDocument, Path | None]:
+    *,
+    snapshot: InputSnapshot | None = None,
+) -> DocumentLoadResult:
     """Load a PDF (convert or reuse an identity-matched cache) or a raw Docling JSON.
 
     A Docling JSON given as the input is a review input: nothing verifies which PDF
     or settings produced it. When `stage_dir` is given, a fresh conversion is written
     there and the returned path is where it will be published; the caller publishes it.
     """
     input_path = Path(input_path).resolve()
     if not input_path.exists():
         raise FileNotFoundError(f"Input file not found: {input_path}")
+    captured = snapshot if snapshot is not None else InputSnapshot(input_path)
+    captured.require_path(input_path)
 
     suffix = input_path.suffix.lower()
     if suffix == ".json":
-        data = json.loads(input_path.read_text(encoding="utf-8"))
+        data = json.loads(captured.data.decode("utf-8"))
         print(f"[*] Loading Docling JSON: {input_path.name} (review input; source PDF not verified)")
-        return load_from_raw_json(data), input_path
+        return DocumentLoadResult(load_from_raw_json(data), input_path, "not-applicable")
 
     if suffix != ".pdf":
         raise ValueError(f"Unsupported input type: {input_path.suffix}")
 
     ensure_docling_env()
     load_docling()
 
     raw_json_path = Path(raw_json_path).resolve() if raw_json_path else input_path.parent / f"{input_path.stem}_docling.json"
     meta_path = _cache_meta_path(raw_json_path)
     settings = conversion_settings()
-    pdf_hash = file_sha256(input_path)
+    pdf_hash = captured.sha256
     expected = conversion_identity(pdf_hash, settings)
 
     if not force_reconvert:
-        cached, reason = load_reusable_cache(raw_json_path, meta_path, pdf_hash, settings)
+        cached, reason = _load_reusable_cache_result(raw_json_path, meta_path, pdf_hash, settings)
         if cached is not None:
             print(f"[*] Reusing raw Docling JSON with matching identity: {raw_json_path.name}")
-            return cached, raw_json_path
+            return cached
         if raw_json_path.exists():
             print(f"[*] Ignoring cached Docling JSON ({reason}); reconverting.")
 
     print(f"[*] Converting with Docling ({device.upper()}): {input_path.name}")
     active = converter or get_shared_converter(
         device=device, backend="docling_parse", settings=settings)
-    result = active.convert(str(input_path))
+    from docling.datamodel.base_models import DocumentStream
+
+    result = active.convert(DocumentStream(name=input_path.name, stream=BytesIO(captured.data)))
 
     if _conversion_has_bad_alloc(result):
         print(
             "[!] Native Docling PDF backend hit std::bad_alloc; retrying through "
             "Docling's PyPdfium backend (NOT PyMuPDF)."
         )
         result = get_shared_converter(
-            device=device, backend="pypdfium2", settings=settings).convert(str(input_path))
+            device=device, backend="pypdfium2", settings=settings).convert(
+                DocumentStream(name=input_path.name, stream=BytesIO(captured.data)))
 
     if _conversion_has_bad_alloc(result):
         raise MemoryError(
             "Docling still reported std::bad_alloc after backend retry. Confirm "
             "docling-parse>=7.12 (Bintanong pins >=7.20) and a Windows pagefile."
         )
 
     remaining_errors = _conversion_errors(result)
     if remaining_errors:
         raise RuntimeError(
@@ -437,32 +468,52 @@ def load_document(
         )
 
     doc = result.document
     raw = doc.export_to_dict() if hasattr(doc, "export_to_dict") else doc.model_dump(mode="json")
     raw_bytes = json.dumps(raw, indent=2, ensure_ascii=False).encode("utf-8")
     meta = {
         "identity_version": IDENTITY_VERSION,
         "pdf_sha256": pdf_hash,
         "conversion_settings": settings,
         "conversion_identity": expected,
-        "raw_json_sha256": hashlib.sha256(raw_bytes).hexdigest(),
+        "raw_json_sha256": bytes_sha256(raw_bytes),
     }
     write_dir = Path(stage_dir) if stage_dir else raw_json_path.parent
+    if stage_dir is None:
+        captured.verify_unchanged()
     # raw JSON first, meta second: a crash between them leaves a pair that fails the sha check.
     _write_bytes_atomic(write_dir / raw_json_path.name, raw_bytes)
-    _write_bytes_atomic(write_dir / meta_path.name, json.dumps(meta, indent=2).encode("utf-8"))
+    meta_bytes = json.dumps(meta, indent=2).encode("utf-8")
+    _write_bytes_atomic(write_dir / meta_path.name, meta_bytes)
     print(f"[+] Raw Docling JSON -> {write_dir / raw_json_path.name}")
 
     rehydrated = load_docling()["DoclingDocument"].model_validate(raw)
-    return _load_from_rehydrated_docling_document(
-        rehydrated, "docling-document", raw
-    ), raw_json_path
+    return DocumentLoadResult(
+        _load_from_rehydrated_docling_document(rehydrated, "docling-document", raw),
+        raw_json_path, "converted", raw_bytes, meta["raw_json_sha256"],
+        meta_bytes, bytes_sha256(meta_bytes),
+    )
+
+
+def load_document(
+    input_path: Path,
+    device: str = "auto",
+    force_reconvert: bool = True,
+    converter: Any = None,
+    raw_json_path: Path | None = None,
+    stage_dir: Path | None = None,
+) -> tuple[LoadedDocument, Path | None]:
+    """Compatibility wrapper for callers that unpack (document, raw JSON path)."""
+    result = load_document_result(
+        input_path, device, force_reconvert, converter, raw_json_path, stage_dir,
+    )
+    return result.document, result.raw_json_path
 
 def dump_grid(document: LoadedDocument) -> str:
     """Human-readable dump of every reconstructed table row - the debugging tool v1 lacked."""
     lines: list[str] = []
     for table in document.tables:
         table_index = table.table_index
         grid = project_table_to_grid(table)
         groups, header_index = detect_column_groups(grid)
         lines.append(
             f"== Table {table_index}: {len(grid)} rows x {max((len(r) for r in grid), default=0)} cols, "
diff --git a/backend/bintanong_tools/prospectus_extractor/paths.py b/backend/bintanong_tools/prospectus_extractor/paths.py
index e285f41..a992fb0 100644
--- a/backend/bintanong_tools/prospectus_extractor/paths.py
+++ b/backend/bintanong_tools/prospectus_extractor/paths.py
@@ -27,11 +27,11 @@ DEFAULT_TARGET_PDF = (
     / "New Curriculum (2025-2026)"
     / "1_BS Computer Science_for BOR approval _rev02_v7_6 August 2025.pdf"
 )
 
 
 def find_default_input_root() -> Path:
     return SOURCE_PDF_ROOT.resolve()
 
 
 def find_default_output_root() -> Path:
-    return (Path(__file__).resolve().parent / "docling_jsonified_output").resolve()
+    return Path.home() / "Bintanong" / "output"
diff --git a/backend/bintanong_tools/prospectus_extractor/pipeline.py b/backend/bintanong_tools/prospectus_extractor/pipeline.py
index d2872f1..2525454 100644
--- a/backend/bintanong_tools/prospectus_extractor/pipeline.py
+++ b/backend/bintanong_tools/prospectus_extractor/pipeline.py
@@ -18,22 +18,22 @@ from .parse import parse_curriculum_evidence
 from .courses import finalize_courses, link_elective_tracks, parse_elective_tracks
 from .prerequisites import annotate_prerequisite_states
 from .metadata import parse_semantic_markdown, resolve_metadata
 from .audit import build_audit
 from .ledger import content_review_state
 from .views import build_curriculum_by_term, build_unlocks_map, make_prerequisite_edges, write_review_csv
 from .prolog import generate_prolog_knowledge
 from .rag import build_hierarchical_rag_chunks, build_semantic_rag_chunks
 from .markup import render_prospectus_markup
 from .paths import DEFAULT_SEMANTIC_DOC, SOURCE_PDF_ROOT, find_default_output_root
-from .identity import run_identity
-from .loader import _cache_meta_path, load_document
+from .identity import InputSnapshot, run_identity
+from .loader import _cache_meta_path, load_document_result
 from .publish import (
     clear_failure, new_staging_dir, output_names, publish_staged, write_failure, write_text_lf,
 )
 
 REVIEW_INPUT_NOTE = (
     "Docling JSON given without its source PDF: the PDF hash and conversion settings are "
     "not verified, so this output is a review input only."
 )
 
 
@@ -269,20 +269,21 @@ def process_prospectus(
     semantic_doc_path: Path | None = DEFAULT_SEMANTIC_DOC,
     force_reconvert: bool = False,
     converter: Any = None,
     repair_provider: SemanticRepairProvider | None = None,
     quiet: bool = False,
     export_md: bool = False,
     *,
     source: Any = None,
     approved_scope: Mapping[str, str] | None = None,
     review_entries: Iterable[Mapping[str, Any]] | None = None,
+    _snapshot: InputSnapshot | None = None,
 ) -> dict[str, Any]:
     """Full pipeline for one prospectus: convert, parse, audit, then publish.
 
     Nothing already published is touched until conversion and audit have finished. On any
     exception the staged files go to <output dir>/failed/<base>/ and the exception propagates.
     """
     input_path = Path(input_path).resolve()
     stem = input_path.stem
     if stem.endswith("_docling"):
         stem = stem[: -len("_docling")]
@@ -292,65 +293,81 @@ def process_prospectus(
         try:
             relative_parent = input_path.relative_to(SOURCE_PDF_ROOT.resolve()).parent
         except ValueError:
             relative_parent = Path()
         final_path = find_default_output_root() / relative_parent / f"{stem}_prospectus.json"
     else:
         final_path = input_path.parent / f"{stem}_prospectus.json"
     if final_path.suffix.lower() != ".json" or final_path.resolve() == input_path:
         raise ValueError("Output must be a JSON file distinct from the source")
     pdf_hash_check = "not_checked"
+    captured = _snapshot if _snapshot is not None else InputSnapshot(input_path)
+    captured.require_path(input_path)
     if source is not None and input_path.suffix.lower() == ".pdf":
-        source.verify_pdf(input_path)  # raises ValueError on a hash mismatch, before any output is touched
+        source.verify_digest(captured.sha256)  # before any output is touched
         pdf_hash_check = "matched"
 
     names = output_names(final_path)
     is_pdf = input_path.suffix.lower() == ".pdf"
     raw_cache_path = final_path.parent / f"{stem}_docling.json" if is_pdf else None
     final_path.parent.mkdir(parents=True, exist_ok=True)
     stage = new_staging_dir(final_path.parent, names.base)
     run_id: dict[str, Any] | None = None
     try:
-        run_id = run_identity(input_path, semantic_doc_path)
-        document, raw_json_path = load_document(
+        run_id = run_identity(input_path, semantic_doc_path, snapshot=captured)
+        loaded = load_document_result(
             input_path, device=device, force_reconvert=force_reconvert,
-            converter=converter, raw_json_path=raw_cache_path, stage_dir=stage,
+            converter=converter, raw_json_path=raw_cache_path, stage_dir=stage, snapshot=captured,
         )
+        document, raw_json_path = loaded.document, loaded.raw_json_path
         payload = build_payload(
             document,
             input_path,
             semantic_doc_path,
             raw_json_path,
             repair_provider=repair_provider,
             source=source,
             approved_scope=approved_scope,
             pdf_hash_check=pdf_hash_check,
             review_entries=review_entries,
         )
 
         cache_files: list[str] = []
+        cache_hashes: dict[str, str] = {}
         if raw_cache_path is not None:
-            cache_files = [
-                name for name in (raw_cache_path.name, _cache_meta_path(raw_cache_path).name)
-                if (stage / name).exists()
-            ]
+            if (loaded.cache_status not in ("converted", "reused")
+                    or not isinstance(loaded.raw_json_bytes, bytes)
+                    or not isinstance(loaded.meta_bytes, bytes)
+                    or loaded.raw_json_sha256 is None or loaded.meta_sha256 is None):
+                raise ValueError("PDF load result has no complete captured cache pair")
+            cache_files = [raw_cache_path.name, _cache_meta_path(raw_cache_path).name]
+            cache_hashes = dict(zip(cache_files, (loaded.raw_json_sha256, loaded.meta_sha256)))
+            if loaded.cache_status == "reused":
+                for name, data in zip(cache_files, (loaded.raw_json_bytes, loaded.meta_bytes)):
+                    (stage / name).write_bytes(data)
         payload["run_identity"] = {
-            **run_id,
-            "cache": ("converted" if cache_files else "reused") if is_pdf else "not-applicable",
+            **run_id, "cache": loaded.cache_status, "cache_files": cache_hashes,
+            "skip_reusable": all(value is None for value in (
+                source, approved_scope, review_entries, repair_provider,
+            )),
         }
         if run_id["review_input_only"]:
             payload["run_identity"]["review_note"] = REVIEW_INPUT_NOTE
 
         outputs = _stage_outputs(
             stage, names, document, payload, is_pdf, export_pl, export_jsonl, export_csv, export_md,
         )
-        publish_staged(stage, names, outputs, cache_files, payload["run_identity"], payload["audit"]["status"])
+        captured.verify_unchanged()
+        publish_staged(
+            stage, names, outputs, cache_files, payload["run_identity"], payload["audit"]["status"],
+            cache_hashes=cache_hashes,
+        )
         clear_failure(names)
     except Exception as exc:
         write_failure(names, exc, input_path, run_id, stage)
         raise
     finally:
         shutil.rmtree(stage, ignore_errors=True)
 
     if not quiet:
         for name in outputs:
             print(f"[+] {name} -> {final_path.parent}")
diff --git a/backend/bintanong_tools/prospectus_extractor/publish.py b/backend/bintanong_tools/prospectus_extractor/publish.py
index 177d6e8..b2ba71a 100644
--- a/backend/bintanong_tools/prospectus_extractor/publish.py
+++ b/backend/bintanong_tools/prospectus_extractor/publish.py
@@ -1,28 +1,29 @@
 """Staged output publication: write beside the target, publish file by file, manifest last."""
 
 from __future__ import annotations
 
 from dataclasses import dataclass
 from datetime import datetime
 from pathlib import Path
 from typing import Any, Mapping, Sequence
 import json
 import os
+import re
 import shutil
 import time
 import traceback
 import uuid
 
-from .identity import file_sha256
+from .identity import IDENTITY_VERSION, bytes_sha256, conversion_identity, file_sha256
 
-PUBLISH_SCHEMA = "palsu-prospectus-publish-v1"
+PUBLISH_SCHEMA = "palsu-prospectus-publish-v2"
 FAILED_DIR_NAME = "failed"
 
 
 @dataclass(frozen=True)
 class OutputNames:
     base: str
     final: Path
     essentials: Path
     prolog: Path
     rag: Path
@@ -49,35 +50,39 @@ def output_names(final_path: Path) -> OutputNames:
         markup=final.with_name(f"{base}_prospectus.md"),
         manifest=final.with_name(f"{base}_publish.json"),
     )
 
 
 def write_text_lf(path: Path, text: str) -> None:
     """UTF-8 with \\n on every platform, so the same run hashes the same everywhere."""
     Path(path).write_bytes(text.encode("utf-8"))
 
 
+def _staging_prefix(base: str) -> str:
+    return f".s-{bytes_sha256(base.encode('utf-8'))[:32]}-"
+
+
 def remove_stale_staging(parent: Path, base: str) -> None:
     """Delete staging directories a killed run left behind. One writer per output stem."""
-    prefix = f".{base}.staging-"
+    prefix = _staging_prefix(base)
     if not Path(parent).is_dir():
         return
     for entry in Path(parent).iterdir():
         if entry.is_dir() and entry.name.startswith(prefix):
             shutil.rmtree(entry, ignore_errors=True)
 
 
 def new_staging_dir(parent: Path, base: str) -> Path:
     """A fresh directory beside the target, so every replace stays on one filesystem."""
     parent = Path(parent)
     remove_stale_staging(parent, base)
-    stage = parent / f".{base}.staging-{uuid.uuid4().hex[:8]}"
+    stage = parent / f"{_staging_prefix(base)}{uuid.uuid4().hex[:8]}"
     stage.mkdir(parents=True)
     return stage
 
 
 class ReplaceFailed(OSError):
     """A finished file could not be moved over its target (on Windows: the target stayed locked)."""
 
 
 def replace_file(source: Path, target: Path, attempts: int = 5, delay: float = 0.2) -> None:
     """os.replace with a short retry: Windows scanners and indexers briefly lock fresh files.
@@ -92,95 +97,174 @@ def replace_file(source: Path, target: Path, attempts: int = 5, delay: float = 0
             return
         except PermissionError as exc:
             if attempt == attempts - 1:
                 raise ReplaceFailed(
                     f"could not replace {target} with {source} after {attempts} "
                     f"attempts (the target stayed locked): {exc}"
                 ) from exc
             time.sleep(delay * (attempt + 1))
 
 
+def _leaf_name(value: Any) -> bool:
+    return (
+        isinstance(value, str) and bool(value) and value not in (".", "..")
+        and not any(char in value for char in "/\\:\x00")
+        and not value.endswith((".", " "))
+    )
+
+
+def _sha256(value: Any) -> bool:
+    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None
+
+
+def _manifest_error(manifest: Any) -> str | None:
+    """Validate the manifest before trusting any path or digest it declares."""
+    if not isinstance(manifest, Mapping) or manifest.get("schema") != PUBLISH_SCHEMA:
+        return "unsupported publish manifest"
+    files, caches = manifest.get("files"), manifest.get("cache_files")
+    if not isinstance(files, Mapping) or not files or not isinstance(caches, Mapping):
+        return "invalid publish file maps"
+    all_names = [*files, *caches]
+    if any(not _leaf_name(name) for name in all_names):
+        return "invalid publish file name"
+    if len({name.casefold() for name in all_names}) != len(all_names):
+        return "duplicate publish file name"
+    if any(not _sha256(digest) for digest in [*files.values(), *caches.values()]):
+        return "invalid publish digest"
+    main = manifest.get("main_file")
+    if not _leaf_name(main) or main not in files:
+        return "missing main file binding"
+    identity = manifest.get("run_identity")
+    if (not isinstance(identity, Mapping) or not _sha256(manifest.get("run_key"))
+            or identity.get("run_key") != manifest["run_key"]):
+        return "invalid run identity"
+    if identity.get("cache_files") != caches or not _sha256(identity.get("input_sha256")):
+        return "invalid cache or input identity binding"
+    if identity.get("input_kind") == "pdf":
+        raw_names = [name for name in caches if name.endswith("_docling.json")]
+        if (len(raw_names) != 1 or len(caches) != 2
+                or raw_names[0][:-5] + ".meta.json" not in caches):
+            return "missing PDF cache pair binding"
+        settings = identity.get("conversion_settings")
+        if (identity.get("identity_version") != IDENTITY_VERSION
+                or identity.get("pdf_sha256") != identity["input_sha256"]
+                or not isinstance(settings, Mapping)
+                or identity.get("conversion_identity") != conversion_identity(
+                    identity["input_sha256"], settings)):
+            return "invalid PDF conversion identity"
+    elif identity.get("input_kind") == "docling-json":
+        if (caches or identity.get("pdf_sha256") is not None
+                or identity.get("conversion_settings") is not None
+                or identity.get("conversion_identity") is not None):
+            return "invalid review input cache binding"
+    else:
+        return "unsupported input kind"
+    return None
+
+
 def read_manifest(path: Path) -> dict[str, Any] | None:
     try:
-        data = json.loads(Path(path).read_text(encoding="utf-8"))
-    except (OSError, ValueError):
-        return None
-    if (
-        not isinstance(data, dict)
-        or data.get("schema") != PUBLISH_SCHEMA
-        or not isinstance(data.get("files"), dict)
-        or not isinstance(data.get("run_key"), str)
-    ):
+        data = json.loads(Path(path).read_bytes().decode("utf-8"))
+        return data if _manifest_error(data) is None else None
+    except (OSError, ValueError, TypeError):
         return None
-    return data
 
 
 def verify_published(directory: Path, manifest: Mapping[str, Any]) -> tuple[bool, str]:
-    """Does every file the manifest lists still hash to the value recorded when it was published?"""
-    for name, digest in manifest["files"].items():
-        target = Path(directory) / name
-        if not target.is_file():
-            return False, f"{name} is missing"
-        if file_sha256(target) != digest:
-            return False, f"{name} changed since it was published"
-    return True, "all files match"
+    """Check one bytes snapshot per file, including main/cache identity cross-bindings."""
+    try:
+        error = _manifest_error(manifest)
+        if error:
+            return False, error
+        directory = Path(directory).resolve()
+        snapshots = {}
+        for name, digest in {**manifest["files"], **manifest["cache_files"]}.items():
+            target = directory / name
+            if target.resolve().parent != directory:
+                return False, f"{name} resolves outside the output directory"
+            if not target.is_file():
+                return False, f"{name} is missing"
+            data = target.read_bytes()
+            if bytes_sha256(data) != digest:
+                return False, f"{name} changed since it was published"
+            snapshots[name] = data
+        main = json.loads(snapshots[manifest["main_file"]].decode("utf-8"))
+        identity = manifest["run_identity"]
+        if not isinstance(main, Mapping) or main.get("run_identity") != identity:
+            return False, "main run identity does not match the manifest"
+        if identity["input_kind"] == "pdf":
+            raw_name = next(name for name in manifest["cache_files"] if name.endswith("_docling.json"))
+            meta = json.loads(snapshots[raw_name[:-5] + ".meta.json"].decode("utf-8"))
+            raw = json.loads(snapshots[raw_name].decode("utf-8"))
+            if not isinstance(raw, Mapping):
+                return False, "cached JSON is not a document"
+            if (not isinstance(meta, Mapping)
+                    or meta.get("identity_version") != identity["identity_version"]
+                    or meta.get("pdf_sha256") != identity["pdf_sha256"]
+                    or meta.get("conversion_identity") != identity["conversion_identity"]
+                    or meta.get("conversion_settings") != identity["conversion_settings"]
+                    or meta.get("raw_json_sha256") != manifest["cache_files"][raw_name]):
+                return False, "cache metadata does not match the main run identity"
+        return True, "all files match"
+    except (OSError, ValueError, TypeError) as exc:
+        return False, f"published set is unreadable ({type(exc).__name__})"
 
 
 def publish_staged(
     stage: Path,
     names: OutputNames,
     outputs: Sequence[str],
     cache_files: Sequence[str],
     run_identity: Mapping[str, Any],
     audit_status: str,
+    *,
+    cache_hashes: Mapping[str, str] | None = None,
 ) -> Path:
-    """Move a finished stage into place, one file at a time.
+    """Publish companions, main JSON, captured cache pair, then the v2 manifest.
 
-    `outputs` are file names inside `stage` in publish order; the main JSON must be last.
-    `cache_files` (raw Docling JSON and its meta) are published first and are not part of
-    the manifest: they have their own identity record. The manifest is published very last.
-    A crash part-way leaves an old manifest whose hashes no longer match: verify_published
-    reports the set incomplete, so nothing trusts it.
+    File replacements are not an atomic set. Manifest-last verification detects mixed
+    generations; byte-identical early replacements may leave the old set coherent.
     """
     stage = Path(stage)
     if not outputs or outputs[-1] != names.final.name:
         raise ValueError("the main JSON must be the last staged output")
-    target_dir = names.final.parent
-    target_dir.mkdir(parents=True, exist_ok=True)
-
-    previous = read_manifest(names.manifest)
-    previous_files = set(previous["files"]) if previous else set()
-
+    all_names = [*outputs, *cache_files, names.manifest.name]
+    if (any(not _leaf_name(name) for name in all_names)
+            or len({name.casefold() for name in all_names}) != len(all_names)):
+        raise ValueError("invalid or duplicate staged file names")
+    hashes = dict(cache_hashes) if cache_hashes is not None else {}
+    if set(cache_files) != set(hashes):
+        raise ValueError("staged cache files must match the captured cache hashes")
     manifest = {
         "schema": PUBLISH_SCHEMA,
-        "run_key": run_identity["run_key"],
+        "run_key": run_identity.get("run_key"),
         "audit_status": audit_status,
         "published_at": datetime.now().isoformat(timespec="seconds"),
         "run_identity": dict(run_identity),
+        "main_file": names.final.name,
         "files": {name: file_sha256(stage / name) for name in outputs},
+        "cache_files": hashes,
     }
+    valid, why = verify_published(stage, manifest)
+    if not valid:
+        raise ValueError(f"Invalid staged publication: {why}")
     write_text_lf(stage / names.manifest.name, json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
-
-    for name in [*cache_files, *outputs, names.manifest.name]:
+    target_dir = names.final.parent
+    target_dir.mkdir(parents=True, exist_ok=True)
+    for name in [*outputs, *cache_files, names.manifest.name]:
         replace_file(stage / name, target_dir / name)
 
-    # Stale: whatever the previous manifest listed, plus every known companion of this base
-    # (an output set written before publish manifests existed has none), that this run did
-    # not produce. The cache files and the manifest itself are never stale companions.
     companions = {path.name for path in (names.essentials, names.prolog, names.rag, names.csv, names.markup)}
-    keep = {*outputs, *cache_files, names.manifest.name}
-    for stale in sorted((previous_files | companions) - keep):
-        if Path(stale).name != stale:  # a tampered manifest must not reach outside this folder
-            continue
+    for stale in sorted(companions - set(outputs)):
         try:
             (target_dir / stale).unlink(missing_ok=True)
-        except OSError as exc:  # not in the new manifest, so it cannot pass for current output
+        except OSError as exc:
             print(f"[!] Could not remove stale companion {target_dir / stale}: {exc}")
     return names.manifest
 
 
 def write_failure(
     names: OutputNames,
     error: BaseException,
     input_path: Path,
     run_identity: Mapping[str, Any] | None,
     stage: Path | None,
diff --git a/backend/bintanong_tools/prospectus_extractor/tui.py b/backend/bintanong_tools/prospectus_extractor/tui.py
index 8fc84f1..819dc4e 100644
--- a/backend/bintanong_tools/prospectus_extractor/tui.py
+++ b/backend/bintanong_tools/prospectus_extractor/tui.py
@@ -81,20 +81,21 @@ class ProspectusTUI:
         cfg = self.config
         rows = [
             ("Input root", str(cfg.input_root)),
             ("Output root", str(cfg.output_root)),
             ("Device", cfg.device.upper()),
             ("Recursive", str(cfg.recursive)),
             ("Preserve structure", str(cfg.preserve_structure)),
             ("Export mode", cfg.export_mode),
             ("Write CSV / PL / JSONL / MD", f"{cfg.write_csv} / {cfg.write_pl} / {cfg.write_jsonl} / {cfg.write_md}"),
             ("Skip existing", str(cfg.skip_existing)),
+            ("Force reconversion", str(cfg.force_reconvert)),
             ("Semantic map", str(cfg.semantic_doc) if cfg.semantic_doc else "(none)"),
             ("Files in last scan", str(len(self.last_scan))),
         ]
         if RICH_AVAILABLE and console:
             table = Table(title="Current settings")
             table.add_column("Setting", style="bold")
             table.add_column("Value")
             for key, value in rows:
                 table.add_row(key, value)
             console.print(table)
@@ -191,21 +192,26 @@ class ProspectusTUI:
         cfg.preserve_structure = ask_yes_no("Mirror the input folder structure?", cfg.preserve_structure)
         print_line("\n[1] side_by_side  output/<rel>/<stem>_prospectus.json")
         print_line("[2] per_pdf_folder output/<rel>/<stem>/prospectus.json")
         mode = ask_text("Export mode", "1" if cfg.export_mode == "side_by_side" else "2").strip()
         cfg.export_mode = "side_by_side" if mode == "1" else "per_pdf_folder"
         cfg.write_csv = ask_yes_no("Write review CSV?", cfg.write_csv)
         cfg.write_pl = ask_yes_no("Write Prolog knowledge base?", cfg.write_pl)
         cfg.write_jsonl = ask_yes_no("Write RAG JSONL?", cfg.write_jsonl)
         cfg.write_md = ask_yes_no("Write prospectus-style Markdown?", cfg.write_md)
         cfg.write_manifest = ask_yes_no("Write batch manifest?", cfg.write_manifest)
-        cfg.skip_existing = ask_yes_no("Skip files whose output already exists?", cfg.skip_existing)
+        cfg.skip_existing = ask_yes_no(
+            "Skip only identity-verified, complete outputs with a non-error audit?", cfg.skip_existing,
+        )
+        cfg.force_reconvert = ask_yes_no(
+            "Force reconversion (overrides skip-existing and cached conversion)?", cfg.force_reconvert,
+        )
         self.pause("Settings updated.")
 
     def preview(self) -> None:
         if not self.last_scan:
             self.last_scan = scan_inputs(
                 self.config.input_root, self.config.recursive, self.config.include_patterns
             )
         items = build_batch_items(self.last_scan, self.config)
         print_line(f"\nBatch plan ({len(items)} file(s)):")
         for item in items[:10]:
@@ -270,20 +276,21 @@ class ProspectusTUI:
             return
         try:
             payload = process_prospectus(
                 path,
                 export_pl=self.config.write_pl,
                 export_jsonl=self.config.write_jsonl,
                 export_csv=self.config.write_csv,
                 export_md=self.config.write_md,
                 device=self.config.device,
                 semantic_doc_path=self.config.semantic_doc,
+                force_reconvert=self.config.force_reconvert,
             )
             self.pause(
                 f"Extracted {payload['audit']['total_courses']} courses "
                 f"({payload['audit']['status'].upper()})."
             )
         except Exception as exc:
             self.pause(f"Extraction failed: {type(exc).__name__}: {exc}")
 
     def dump_grid_interactive(self) -> None:
         path = self._pick_file()
diff --git a/backend/bintanong_tools/prospectus_extractor/views.py b/backend/bintanong_tools/prospectus_extractor/views.py
index 41b341c..34bf7fd 100644
--- a/backend/bintanong_tools/prospectus_extractor/views.py
+++ b/backend/bintanong_tools/prospectus_extractor/views.py
@@ -39,21 +39,21 @@ def write_review_csv(courses: Sequence[dict[str, Any]], output_path: Path) -> No
     """Human-reviewable flat table - the artefact a registrar can actually check."""
     fields = [
         "year_level", "semester", "course_code", "course_title", "units_total",
         "units_lecture", "units_lab", "prerequisites_resolved", "prerequisites_unresolved",
         "standing_requirements", "category", "elective_group", "prerequisites_raw",
         "title_raw", "footnote_marker", "table_index", "row_index", "column_group",
         "source_cell_ids", "page", "bbox", "resolution_method", "repair_id",
     ]
     output_path.parent.mkdir(parents=True, exist_ok=True)
     with output_path.open("w", newline="", encoding="utf-8-sig") as handle:
-        writer = csv.DictWriter(handle, fieldnames=fields)
+        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
         writer.writeheader()
         for course in courses:
             source = course.get("_source", {})
             provenance = course.get("provenance", {})
             writer.writerow(
                 {
                     "year_level": course.get("year_level", ""),
                     "semester": course.get("semester", ""),
                     "course_code": course.get("course_code", ""),
                     "course_title": course.get("course_title", ""),
diff --git a/docs/decisions/prospectus-cache-and-publication.md b/docs/decisions/prospectus-cache-and-publication.md
new file mode 100644
index 0000000..c27f775
--- /dev/null
+++ b/docs/decisions/prospectus-cache-and-publication.md
@@ -0,0 +1,53 @@
+# Prospectus cache identity and output publication
+
+Recorded during the 6 October 2026 Asia/Manila pickup, branch `feat/prospectus-phase-d-safe-cache`. The original Phase D implementation started from `189c9eaf453da9a4e7bb5471133a9cf864316012`. The approved pickup/regression base is `641523d212839084da03d966ffbfca66c7e83e42`; reviewed production tip is `c40a38c9f633dd085766ca11f81f0dd3890810cc`. This decision and the final evidence update are documentation only. Whole-range specification and quality reviews of `641523d..final-documentary-tip` are **PENDING**; Phase D is not yet fully complete.
+
+## Identity and captured input
+
+`identity.bytes_sha256` is the shared byte-digest owner; `file_sha256` delegates to it. One immutable `InputSnapshot` captures the input path, bytes and digest. Source digest verification, run identity, batch skip checking and loading share that capture. Batch captures one item at a time and initializes Docling only after a cache miss. Before publication, the original file is compared byte-for-byte with the capture; equal size or a restored modification time does not bypass this check.
+
+Docling receives `DocumentStream(name=original_filename, stream=BytesIO(captured_bytes))`. A `std::bad_alloc` fallback gets a fresh stream over the same capture with the same filename and uses the PyPdfium backend. No unchecked path reopen supplies conversion bytes. Internal `load_document_result` returns the document, cache status, exact raw JSON/meta bytes and their digests. Public `load_document` preserves the legacy two-value `(document, raw_json_path)` contract.
+
+Two identities implement D1. `conversion_identity` hashes identity version, PDF digest and conversion settings: profile, OCR enablement/languages, table structure/mode, forced backend text, cell matching, primary/fallback backends and installed Docling/docling-core/docling-parse versions. Parser code is excluded from this identity so parser-only changes can reparse a valid raw cache. `run_key` hashes input kind/digest, conversion identity, parser package digest, payload schema and semantic-map digest. The package digest includes all extractor `.py` files with normalized line endings. D2 excludes the CPU/CUDA device; a measured device-dependent conversion difference would require changing the settings identity and its tests.
+
+Cache metadata contains `identity_version` (1), `pdf_sha256`, `conversion_settings`, `conversion_identity` and `raw_json_sha256`. Reuse verifies all fields and the digest of the exact raw bytes subsequently parsed, including Docling model validation. Missing, mismatched, malformed or rejected records cause reconversion when a PDF is available. Both converted and reused caches retain their exact byte pair through staging and publication.
+
+The payload schema is `palsu-prospectus-v3.2`; the batch schema is `palsu-prospectus-batch-manifest-v3.1`. Top-level `run_identity` contains `identity_version`, `input_kind`, `input_sha256`, `conversion_identity`, `package_sha256`, `schema_version`, `semantic_sha256`, `pdf_sha256`, `conversion_settings`, `review_input_only`, `run_key`, `cache`, `cache_files` and `skip_reusable`. JSON review inputs also contain `review_note`. D5 preserves these public names and `<base>_publish.json`, `skip_check` and `failed_dir` in batch records. A directly supplied Docling JSON is a review input whose PDF origin is unverified; the payload and console say so. None of these identities approves a source or curriculum.
+
+## Publication and failure
+
+All companions, main JSON and cache bytes are staged beside the destination. Publication uses retrying `os.replace` on individual files, which supports replacing Windows files; no directory is replaced. The publish schema is `palsu-prospectus-publish-v2`, with separate `files` and `cache_files` SHA-256 maps, `main_file`, `run_key`, `run_identity`, audit status and publication time. Verification binds the main payload identity to the manifest and the cache metadata to the input/conversion identity and raw digest. Old manifests fail verification and skip eligibility.
+
+The order is essentials, Prolog, RAG JSONL, review CSV, markup (when produced), **main JSON**, captured cache JSON, captured cache meta, then **publish manifest**. The stage must verify before any replacement. The manifest is last because several replacements cannot form one atomic transaction: a mixed generation fails verification; byte-identical early replacements can leave the old coherent set valid. Manifest publication may complete before a later injected exception, in which case the new coherent set verifies. This is detectability, not rollback or whole-set atomicity.
+
+After publication, cleanup removes only known companions not produced by this run: essentials, Prolog, RAG, CSV and markup. It never uses arbitrary manifest names to delete unrelated files or deletes cache files as stale companions. Cleanup failures print an explicit warning. D3 publishes a completed `error` audit for review, omits Prolog/RAG and removes stale downstream companions. Such an audit never qualifies for skip. D6 keeps a fresh conversion cache staged if parsing, building or auditing raises before publication.
+
+Before publication, a failure preserves the previous main, companions, cache pair and publish manifest byte-for-byte. During publication, a failure can replace earlier files; verification detects any inconsistent set. Diagnostics under `<output>/failed/<base>/` retain available staged files and `failure.json` with error type/message, traceback, input, identity and timestamp. Diagnostic-write errors are reported. The stage is removed afterward. Restoring an input and skipping leaves diagnostics intact; a later successful processing/publish clears them.
+
+One writer per output stem remains required: stale stage cleanup is stem-scoped, and concurrent writers are not coordinated. Hashes prove local identity/coherency; they do not protect an artifact store from a party authorized to rewrite both data and manifests, or prove extraction accuracy.
+
+## Skip, discovery, line endings and paths
+
+D4 makes pipeline, CLI and batch cache reuse the default; `--force` requests conversion and overrides skip. The low-level compatibility loader retains its existing default. `prospectus_batch.run_isolated` retains forced conversions. `--skip-existing` is batch-only: it requires a verified complete set with current run identity, requested companions and an `ok` or `warn` audit. The TUI shows/configures the existing force field and describes this identity/completeness rule accurately.
+
+Default runs with all four context arguments omitted record `skip_reusable=True`. Context-bearing runs set `skip_reusable=False` when `source`, `approved_scope`, `review_entries` or `repair_provider` is supplied, including empty supplied values (`is not None`). A later caller omitting context must still reprocess those outputs rather than silently reuse them. Missing or non-boolean eligibility is a rebuild miss (`previous run skip eligibility is unknown`); coherence verification alone does not grant skip reuse.
+
+Discovery exclusions inspect directory components relative to the selected root, excluding filenames and absolute ancestors. A `failure.json` marker in any candidate parent within that root, including the selected root itself, identifies diagnostics; ancestors above the selected root are ignored. A legitimate directory named `failed` without that marker remains discoverable. Glob patterns anchored outside the root or containing `..` are refused. A user directory containing `failure.json` is intentionally treated as diagnostic until the marker is removed.
+
+JSON, text companions and the batch manifest use UTF-8 LF bytes. Review CSV retains UTF-8-sig/BOM, all 23 columns and stdlib `QUOTE_MINIMAL`, with LF record separators. Supported Python 3.13.5 already quotes embedded bare CR correctly; adversarial round-trip checks preserve CR/CRLF field data. The earlier QUOTE_ALL proposal was superseded after runtime verification. The attempted CR red log passed, whereas the original LF red log contains three real failures; neither is relabeled.
+
+The default PDF/batch output root moved from the package-relative `docling_jsonified_output` to `Path.home() / 'Bintanong' / 'output'`. Existing files are never moved or deleted for this migration; consumers of the old automatic location must supply their former explicit output root or adopt the new default. Final filenames and corpus-relative subdirectories remain intact. Stages use `.s-<32 hex stem digest>-<8 random hex>` and atomic cache temps use `.t-<random>.tmp`. The final 32-digit ruling supersedes the initial 8-digit proposal. Read-only projection of all 44 original paths under this user's 35-character default root measured maxima final 181, stage 226, temp 161 and diagnostics 251 characters, below 260. The former root reached 268 for cache meta. These measurements do not guarantee arbitrarily long explicit output roots; final gate conversions use short external scratch and path-only default-root regression rather than rename final artifacts or write to home.
+
+## Historical evidence correction and final gates
+
+Original Task 6 at `f802c764533bdf67267089bcc109416da5941ca9` contains **14**, not 15, publication tests. The authentic original red runtime log is unavailable. The external reconstruction archives parent `29eb83200b593f24caa9179a28c0795c30621b5a` and overlays that commit's publication tests/conftest; it observed **12 failed, 2 passed**. This is reconstructed pre-fix evidence, not original chronological test-first proof. The inconsistent historical 11-failed/2-passed and 15-green wording is superseded. The historical combined 61 remains unchanged because this reconstruction does not establish that total. Evidence: [reconstruction script](<E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_resume_2026-10-06/reconstruct_task6.py>) and [reconstructed log](<E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_resume_2026-10-06/task6-red-reconstruction.log>).
+
+Final production-tip gate evidence at 2026-10-06T23:37:16+08:00 is recorded in the external [Task D final report](<E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_resume_2026-10-06/task-d-final-gates-report.md>). Fresh comprehensive existing GUI-review environment: 990 passed, 13 subtests, five upstream warnings, exit 0, including required API/embedding tests. Fresh self-test: 80/80, exit 0. Fresh focused publication/publish/input-snapshot/batch-skip tests: 394 passed, exit 0, including all 180 replacement-interruption combinations (nine steps, before/after, changed/identical companions, five conversion changes). The unchanged-tip main subset gate is reused from `task-d-s4-full.log`: 984 passed, 13 subtests, three upstream warnings, with the two approved API/embedding ignores. No environment installs or main-venv synchronization occurred.
+
+The final comparer observed **44/44 identical**, exit 0; new payload changes were limited to added `run_identity.cache_files`/`skip_reusable` and changed package digest/run key, each in 44 payloads. Direct Phase C candidate-state counts: blank_unreviewed 1005, resolved 689, unresolved_reference 253, standing_condition 59, unreadable 20, alternative_or_exception 3 and stated_none 2. Fresh original-PDF B2 helper results: mixed 21, warnings_only 3, broken 19, clean 1; title_from_pdf 67, strip_banner 0 (no such proposals), unclaimed_code 316, banner_leak 3. Trial sheets 01 Architecture, 16 BSBA-HRM and 33 BSCS each returned zero `check_against` errors. Original corpus PDFs, 44 cached JSON inputs, semantic map and all files in the three trial folders were hash-checked: 101 files unchanged before/after the fresh real workflows and again before/after read-only helper gates. The comparer is read-only and began before that snapshot; no historical before-comparer hash timing is claimed.
+
+Fresh real Docling CPU conversion used a copy of `BSE-Franchising-and-Trading-for-student-new-version.pdf` in external `scratch/dg`. A: `1 extracted, 0 failed audit, 0 skipped, 0 errored`, exit 0, WARN audit. B unchanged: `0 extracted, 0 failed audit, 1 skipped, 0 errored`, exit 0, exact reason `identical run identity`, all nine prior published/cache files unchanged. C corrupt scratch PDF: `0 extracted, 0 failed audit, 0 skipped, 1 errored`, exit 1, `ConversionError` with traceback, all nine prior files unchanged and no stage residue. D restored input: the same one-skip outcome, files unchanged and diagnostics retained. E forced real conversion: one extraction, exit 0, diagnostics cleared. A further cached real parse changed only the scratch input bytes after parsing while preserving size and restoring mtime; publication refused with `Input bytes changed since capture`, preserving the previous set. Restoring bytes and a subsequent successful reused-cache publish cleared those diagnostics. The historical Marine Biology/Social Work error-pilot observations remain historical evidence; their fresh conversion was not rerun. Fresh default-root path-only projection reproduced final/stage/temp/diagnostics maxima 181/226/161/251 without home writes; no arbitrary long explicit-root conversion is claimed.
+
+Final Task 8 uses the existing committed comparer with base `641523d`, 44 cached inputs, the original semantic map, six jobs and explicit retained baseline worktree `C:/Users/Hawksprey/source/repos/Bintanong-wt/d-baseline-641523d`. Generated evidence stays in the external dataset scratch. Course-field equality is regression equivalence, not proof of source accuracy. The comparer and baseline worktree remain for Phase F; historical removal steps are superseded.
+
+Separate whole-range specification and quality seats must review `641523d..final-documentary-tip` before Phase D completion. Next queue remains GUI review/integration/human trial, Phase E, Phase F, OCR evidence and formal Phase 1/2 preparation. Human GUI/source-owner approval and real-photo support gates remain pending; no active curriculum, Prolog, RAG or institutional release is approved. No push, dev merge, worktree removal or main-checkout synchronization is part of this handoff.
diff --git a/plans/plan_current_progress/current_progress.md b/plans/plan_current_progress/current_progress.md
index 7172dfd..d51271f 100644
--- a/plans/plan_current_progress/current_progress.md
+++ b/plans/plan_current_progress/current_progress.md
@@ -73,11 +73,22 @@ Do not repeat Task 0 or discard the pre-existing dirty parser. Do not use genera
 - Golden result on 44 cached Docling JSON inputs: 44/44 identical to the old file apart from run-to-run timestamps. Cached JSON was used, so PDFs were not re-converted through Docling.
 - parser_sha256 in the isolated batch manifest is now a hash over every .py file in the package (line endings normalised). It is not comparable with the single-file hash 8ea75006... in earlier manifests.
 - Decision record: docs/decisions/prospectus-extractor-package.md. The scaffolding scripts were removed; recover them from Git at 2dffe3d.
 - Next: user decides on merge, then Phase B (markup twin that looks like the printed prospectus). Outputs remain review candidates; nothing here approves a curriculum, RAG, or Prolog release.
 
 ## Prospectus markup twin, Phase B closed (4 October 2026)
 
 - Branch feature/prospectus-markup-twin: the pipeline now writes <name>_prospectus.md, an HTML-table rendering of the Docling evidence with cell IDs, spans, gaps and original text (--export-md). Course fields unchanged: 44/44 identical to base 69ca855. Suite 93 passed, 13 subtests. Merged into dev locally, not pushed.
 - The course audit (44 paths, 39 PDFs, 2031 courses) is committed as scripts/prospectus_course_audit.py, the planned OCR scorer; scripts/prospectus_course_compare.py is the old-versus-new comparer.
 - Human visual check (3-4 October): first-year rows fine, year/semester banner rows broken because Docling merges banner text into neighbouring cells; the twin is faithful and the parser inherits the defect.
-- Decision record: docs/decisions/prospectus-markup-twin.md. Next: Phase B2 (year/semester verifier and fixer with a human decision ledger), then a parser banner-split repair.
\ No newline at end of file
+- Decision record: docs/decisions/prospectus-markup-twin.md. Next: Phase B2 (year/semester verifier and fixer with a human decision ledger), then a parser banner-split repair.
+
+## Phase D final implementation gates and documentary handoff (6 October 2026)
+
+- Branch `feat/prospectus-phase-d-safe-cache`; approved pickup/regression base `641523d212839084da03d966ffbfca66c7e83e42`, reviewed production tip `c40a38c9f633dd085766ca11f81f0dd3890810cc`. S2/S4 independent specification and quality seats approved; final whole-range specification and quality reviews of `641523d..final-documentary-tip` remain **PENDING**, so Phase D is not yet fully complete.
+- Fresh comprehensive existing GUI-review Python: 990 passed, 13 subtests, five upstream warnings; focused publication/publish/snapshot/skip: 394 passed including all 180 replacement interruptions; self-test 80/80. Unchanged-production-tip main subset evidence reused: 984 passed, 13 subtests, three upstream warnings, with the two previously approved API/embedding ignores. All final gate commands exited 0 except the deliberately corrupted scratch PDF, which exited 1 as required. No installs or main-venv changes.
+- Fresh comparer against `641523d`: 44/44 course fields identical. B2 health mixed/warnings_only/broken/clean = 21/3/19/1; title_from_pdf 67, strip_banner 0, unclaimed_code 316, banner_leak 3. Direct prerequisite states blank_unreviewed/resolved/unresolved_reference/standing_condition/unreadable/alternative_or_exception/stated_none = 1005/689/253/59/20/3/2. Original trial 01/16/33 sheets: zero `check_against` errors each. These prove regression stability, not corpus extraction accuracy or approval.
+- Fresh real PDF A published WARN; B skipped with `identical run identity`; C conversion failure preserved all nine earlier files and wrote `ConversionError` diagnostics; D restore skipped and retained diagnostics; E successful forced conversion cleared them. Same-size/restored-mtime mutation after a real cached parse refused publication; restoring bytes and a successful reused-cache publish cleared diagnostics. Original/source candidate/trial files: 101 hashes unchanged around these workflows. Evidence retained externally, including explicit timing/provenance limits.
+- [Decision record](../../docs/decisions/prospectus-cache-and-publication.md) records snapshots/DocumentStream and the legacy wrapper, separate conversion/run identities, publish-v2 cache/main bindings and companion→main→cache→manifest order, prepublication preservation versus interrupted-publication detection, known-only cleanup, root-relative marker discovery, LF/BOM CSV with supported stdlib minimal quoting, context-sensitive `skip_reusable`, TUI force, default migration to `~/Bintanong/output` without moves, actual 181/226/161/251 path maxima and single-writer limit. Original JSON is review-only; no source approval follows.
+- F5 corrected Task 6 count 15→14. Authentic original red log unavailable; explicitly reconstructed parent `29eb832` plus `f802c76` tests observed 12 failed/2 passed. Frozen `f802c76` test collection confirms 14; the historical combined 61 is retained with its provenance limit. Preserved historical plans are unchanged.
+- External report/evidence root: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\task-d-final-gates-report.md`. Only the three authorized documents are committed. No push, dev merge, worktree deletion, main dirty-file edit or institution-source mutation. Comparer and baseline worktree are retained for Phase F.
+- Next: controller whole-range D reviews, then continue GUI integration/review/human trial, Phase E and Phase F, OCR evidence and formal Phase 1/2 preparation. Human/source-owner/real-photo and release gates stay pending; no numbered-phase advancement or institutional activation is claimed.
diff --git a/plans/plan_current_progress/extractor_split_progress.md b/plans/plan_current_progress/extractor_split_progress.md
index 2b2213d..24be134 100644
--- a/plans/plan_current_progress/extractor_split_progress.md
+++ b/plans/plan_current_progress/extractor_split_progress.md
@@ -214,21 +214,21 @@ Each fix is test-first in its own commit. Tests run with `--basetemp` outside th
 - D-3 and the corrupt-JSON suspicion (b98bf15) `cache_reuse_check` is replaced by `load_reusable_cache`, which returns `(document | None, reason)`: it reads the bytes once, checks the digest on them, and parses those same bytes. A digest-matching cache that is not UTF-8, not JSON, not an object, or rejected by `DoclingDocument.model_validate` (any `ValueError`) is a miss and reconverts. Red: the swap reproducer loaded `%PDF-other`; corrupt caches raised `JSONDecodeError`, `UnicodeDecodeError` and `AttributeError: 'list' object has no attribute 'get'`; the Docling-rejected cache raised `ValueError`. Green 21/21.
 - D-4 (eaef785) `load_reusable_cache(raw, meta, pdf_sha256, settings)` derives the expected identity itself, and also requires the record's `pdf_sha256` and `conversion_settings` to equal the current ones. Red: four new damage cases (edited or missing `pdf_sha256`, edited or missing `conversion_settings`) each reused the cache (1 conversion, expected 2). Green 25/25.
 - D-5 (c1c6d34) `ProvisionalSource.verify_pdf` calls `identity.file_sha256`, and `prospectus.py` no longer imports hashlib. This reverses the Task 1 note that left it alone. Red: with the owner patched, `verify_pdf` still computed its own digest (`ValueError: PDF hash mismatch`). Green.
 - Deviation: the plan's name `cache_reuse_check` is gone; its only caller was `load_document`.
 - After the five commits: suite 590 passed + 13 subtests, self-test 80/80. 44-input comparer `--base-ref 1460536 --status-report`: 44/44 identical, prerequisite states unchanged (blank_unreviewed 1005, resolved 689, unresolved_reference 253, standing_condition 59, unreadable 20, stated_none 2, alternative_or_exception 3). Outputs in dump\scratch\phase_d_2026-10-06\dfix_compare\.
 
 ### Phase D Task 5: the publish module
 Finished from the half-done untracked files an earlier agent left. The code and the 9 plan tests matched the plan. Kept: `OutputNames.markup` (`<base>_prospectus.md`, the Phase B markup twin, a publish companion) and its test (published before the main JSON, removed as stale when a later run does not write it). Red, redone: with `publish.py` moved aside, `ImportError: cannot import name 'publish'`. Two tests were added and went red against the half-done file: `loader.replace_file is not publish.replace_file`, and `publish has no attribute 'ReplaceFailed'`. Change: one retrying replace. `publish.replace_file` (`os.replace`, 5 attempts with a growing delay on `PermissionError`, then `ReplaceFailed(OSError)` naming both paths) is the owner, and the D-2 cache writer imports it. On the final failure it leaves the source in place, so a failed publication can copy the staged file into `failed/<base>/`; the cache writer removes its own temp. Green: test_prospectus_publish.py 12 passed (9 plan + markup + 2). Suite 592 passed + 13 subtests, self-test 80/80. Why the manifest goes last: a file-by-file publish cannot be atomic, so a hash manifest written after every file is the one thing that makes a half-published mix detectable (the old manifest no longer matches the new files).
 
 ### Phase D Task 6: process_prospectus stages and publishes
-Red (11 failed, 2 passed, tests/test_prospectus_publication.py): `a_publish.json` was missing from the snapshot; a failed run changed the earlier files (the unlink-first loop); `KeyError: 'run_identity'`; `'palsu-prospectus-v3.1' == 'palsu-prospectus-v3.2'`; no `publish.replace_file` calls; CRLF in `a_prospectus.json`. The two guards that passed: output equal to the source is refused, and companions without a manifest are removed (the old unlink loop did that too). Green: 15 publication tests; publication + cache + publish + identity 61 passed.
+Corrected historical evidence (6 October 2026 pickup): Task 6 contains 14 publication tests, not the previously recorded 15. The authentic original red runtime log is unavailable. An external reconstruction of pre-fix parent `29eb83200b593f24caa9179a28c0795c30621b5a`, overlaid with `f802c764533bdf67267089bcc109416da5941ca9` publication tests/conftest, observed 12 failed, 2 passed. This is reconstructed evidence, not original chronological test-first proof; it supersedes the inconsistent 11-failed/2-passed wording. Historical symptoms were missing `a_publish.json`, changed earlier files (unlink-first), missing `run_identity`, schema v3.1, absent `publish.replace_file` calls and CRLF output. The passing guards refused an output equal to source and removed companions without a manifest. Corrected publication-test count: 14. Historical publication + cache + publish + identity total 61 remains unchanged because the reconstruction does not establish that total. Script/log: external `scratch/codex_resume_2026-10-06/reconstruct_task6.py` and `task6-red-reconstruction.log`.
 - Removed: the unlink-first loop (old pipeline.py:257-267) and the direct `write_text` calls. `process_prospectus` verifies the source hash first (Phase C; nothing is touched on a mismatch). It then creates a staging directory `.<base>.staging-<8 hex>` beside the target, converts into it (`load_document(stage_dir=)`), builds the payload, stages every companion through `_stage_outputs`, and calls `publish_staged`. Order: cache JSON, cache meta, essentials, `.pl`, `_rag.jsonl`, `_review.csv`, `_prospectus.md`, main JSON, `_publish.json`. On any exception, `write_failure` copies the stage to `failed/<base>/`, the stage is removed, and the exception propagates. D3: an `error` audit publishes. D4: `force_reconvert` defaults to False (the CLI and batch still pass True until Task 7). D6: nothing is published on failure.
 - Markup twin: `_prospectus.md` is staged for every audit status when `export_md` is set, published just before the main JSON, and listed in the manifest.
 - Deviation, stale companions: besides the files the previous manifest lists, `publish_staged` also removes every known companion of the base (essentials, `.pl`, `_rag.jsonl`, `_review.csv`, `_prospectus.md`) that this run did not produce. Without that, a set written before Phase D, which has no manifest, would keep a stale `.pl` or `.md` after an audit-error run (`test_md_is_not_written_by_default_and_a_stale_one_is_removed` requires the removal). Cache files and the manifest are never removed. An unlink failure prints a warning.
 - Schema: `SCHEMA_VERSION` `palsu-prospectus-v3.1` -> `palsu-prospectus-v3.2`. The payload gains the top-level object `run_identity`: `identity_version, input_kind, input_sha256, conversion_identity, package_sha256, schema_version, semantic_sha256, pdf_sha256, conversion_settings, review_input_only, run_key, cache` (`converted` / `reused` / `not-applicable`), plus `review_note` for a Docling JSON input. `run_identity.pdf_sha256` is the key the B2 fixer reads; a new test runs `fixer_cli.resolve_identity` on a written payload and gets `how == "run_identity"`. The Phase C literal in test_prospectus_authority.py:281 moved to v3.2.
 - Line endings: outputs are now written with LF on Windows (`write_text_lf`). Before, the JSON, essentials, `.pl` and `_rag.jsonl` were CRLF. No course value changes. `_review.csv` keeps the csv module's own line ending.
 - Suite 606 passed + 13 subtests, self-test 80/80.
 
 ### Phase D Task 7: --skip-existing compares identity and audit status
 Red (14 failed, 1 passed, tests/test_prospectus_batch_skip.py, after the conftest stub audit gained `declared_total_units: 0`, as the plan allows; without it every first run recorded `error` on a KeyError): the old reason was `output already exists`; a failed audit, changed PDF bytes, a missing companion, a half-published set and a set without a manifest were all `skipped`; `batch has no attribute 'package_sha256'`; `KeyError: 'skip_check'`; the scan returned `failed/a/a_docling.json`; the single-file CLI passed `force_reconvert` `[True, True]`; manifest schema `v3.0`. The one that passed, `test_force_overrides...`, passes because the old batch always reconverted. Green: 15 passed (10 plan + 5).
 - `skip_check(item, config, package_hash)` skips only when `--skip-existing` is given without `--force`, a valid publish manifest exists, its `audit_status` is ok or warn (never error), its `run_key` equals the key computed now, every listed file still hashes to its recorded value, and every companion the current flags request is in the manifest. That includes the markup twin `_prospectus.md` when `write_md` is set (the Task 1 note; two tests: missing from the last run, or deleted since). `run_batch` passes `force_reconvert=config.force_reconvert` (D4) and keeps `export_md=config.write_md`. Records gain `skip_check`, `publish_manifest` and, on error, `failed_dir`. `failed` is in `IGNORED_DIR_PARTS`. CLI: new `--skip-existing`/`--force` help; the single-file run passes `force_reconvert=args.force`; `--dump-grid` is unchanged. `--skip-existing` is batch-only; there is no single-file skip. `prospectus_batch.run_isolated` still passes `--force`.
@@ -243,10 +243,509 @@ Red (14 failed, 1 passed, tests/test_prospectus_batch_skip.py, after the conftes
 Deviation: the plan's throwaway `scripts/prospectus_course_compare.py` (run/compare subcommands) is superseded by the committed comparer of the same name (Phase B). That one already compares course fields and audit counts, runs old and new in parallel, and checks the markup twin; nothing new was written or committed. Base: 189c9ea, the last commit before any Phase D code (B2+C merge 48ea309 plus test fix bf1cb47 plus docs). New: aa95d04 (Phase D Tasks 2-7, D-1..D-5, the B2-1 merge). Command: `scripts\prospectus_course_compare.py --golden <task2b_standing_isolated_2026-09-29> --work dump\scratch\phase_d_2026-10-06\task8_compare --base-ref 189c9ea --semantic-doc <meaning map> --status-report --jobs 6`. Result: 44/44 identical, exit 0. Payload: `run_identity` added and `schema_version` changed (44 each), nothing else. Prerequisite states unchanged (1005/689/253/59/20/2/3). Output file sets differ only by the new `candidate_publish.json` (44 of 44). The base worktree was removed afterwards.
 
 ### Phase D Task 9: one real end-to-end failure-injection run (2026-10-06, aa95d04 code)
 Real Docling on CPU, venv Python from the worktree root: `-i <in> --batch -o <out> --skip-existing --export-all --device cpu --semantic-doc <meaning map>`. Scratch is under dump\scratch\phase_d_2026-10-06\ (the hard rules keep scratch out of %TEMP%); the folders are kept as evidence.
 - The smallest PDF, BS-Marine-Biology-prospectus-template_07.08.2022-1.pdf (78,713 B), audits `error`. Run A: `0 extracted, 1 failed audit` (exit 1); the set was published without `.pl`/`_rag.jsonl`. Repeat run: `1 failed audit`, not skipped, with skip_check `previous audit status was error`, and it re-parsed from the identity-matched cache ("Reusing raw Docling JSON with matching identity") without reconverting. That proves the failed-audit rule and D4 on real data (folder e2e_marine_bio_error). The next-smallest, BS-Social-Work-for-student-new-version.pdf, also audits `error` (e2e_social_work_error).
 - Passing PDF used for steps 2-5: BSE-Franchising-and-Trading-for-student-new-version.pdf (93,101 B; 1 of 6 non-error audits among the 44), folder e2e.
   - Run A: `[*] Batch: 1 extracted, 0 failed audit, 0 skipped, 0 errored.` 9 files: target_docling.json, target_docling.meta.json, target_essentials.json, target_prospectus.json/.md/.pl, target_publish.json, target_rag.jsonl, target_review.csv.
   - Run B (unchanged): `0 extracted, 0 failed audit, 1 skipped, 0 errored.` skip_check `identical run identity`. SHA-256 of all 9 files: no differences.
   - Run C (PDF replaced by `%PDF-1.4 not really a pdf`): `0 extracted, 0 failed audit, 0 skipped, 1 errored.` exit 1; skip_check `input, settings, parser or schema changed`. All 9 earlier files: no differences. No `.target.staging-*` left. `failed\target\failure.json` has error_type `ConversionError` ("docling-parse could not load document ...") and a traceback. Nothing else was staged, because conversion failed before writing.
   - Run D (original PDF restored): `0 extracted, 0 failed audit, 1 skipped, 0 errored.` No differences. `failed\target\` is still present: diagnostics are cleared by the next successful processing, not by a skip (for the Task 10 decision record).
+
+### Codex recovery checkpoint 2026-10-06T20:57:53+08:00
+- Task: Phase D resume; step: preflight complete; starting snapshot/hash task; owner: Codex controller.
+- HEAD: 641523d212839084da03d966ffbfca66c7e83e42; state: clean.
+- Evidence: Prior planning baseline:630 passed,13 subtests; HEAD641523d unchanged; GUI13 focused passed.
+- Next: Dispatch Phase D F3/F6 immutable input identity implementer; preserve GUI untracked work.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Phase D F3/F6 immutable input identity (2026-10-06)
+- Base: 641523d. One frozen InputSnapshot(path) captures immutable PDF/JSON bytes and a shared bytes_sha256 digest; path linkage checked. Source verification, run identity, skip check and loader reuse the capture. Batch retains one item at a time; loader initializes its shared converter after cache miss.
+- Docling conversion receives DocumentStream(BytesIO(captured bytes)) with the original filename; backend fallback gets a fresh stream. Current original bytes are compared before pipeline publication and standalone cache writes; same-size/restored-mtime changes refuse publication and retain earlier files. No schema bump or CLI-declared input digest.
+- Internal loader.load_document_result returns DocumentLoadResult(document, raw_json_path, cache_status, raw_json_bytes, raw_json_sha256, meta_bytes, meta_sha256). Reused cache bytes are the exact verified/parsed reads; converted bytes are the exact staging serialization. F1 should bind these digests without reopening cache paths. Public load_document and load_reusable_cache retain tuple contracts.
+- Red evidence:8 failing snapshot tests; standalone cache race1failed/1passed; lost skip-check-error fallback1failed then restored to preserve existing processing behavior. Final focused335 passed; fallback follow-up26 passed. Final main full suite641 passed +13 subtests/3 upstream warnings; GUI-venv comprehensive647 passed +13 subtests/5 upstream warnings; shim80/80. Full suites repeated only after the additional fallback fix. No venv sync.
+- Evidence: dump/scratch/codex_resume_2026-10-06/task-d-identity-report.md and task-d-identity-{red,standalone-red,green,skip-error-red,skip-error-green,final-fullsuite,final-comprehensive,selftest}.log. Independent reviews and remaining D/corpus gates not run by this implementer; next: controller independent F3/F6 review then F1 publication/cache binding.
+
+### Codex recovery checkpoint 2026-10-06T21:10:39+08:00
+- Task: D F3/F6; step: final verified: baseline641 comprehensive647 subtests13 shim80/80; ready to commit; owner: d_identity implementer.
+- HEAD: 641523d212839084da03d966ffbfca66c7e83e42; state: M backend/bintanong_tools/prospectus.py
+ M backend/bintanong_tools/prospectus_extractor/batch.py
+ M backend/bintanong_tools/prospectus_extractor/identity.py
+ M backend/bintanong_tools/prospectus_extractor/loader.py
+ M backend/bintanong_tools/prospectus_extractor/pipeline.py
+ M plans/plan_current_progress/extractor_split_progress.md
+ M tests/conftest.py
+ M tests/test_prospectus_authority.py
+ M tests/test_prospectus_batch_skip.py
+ M tests/test_prospectus_markup.py
+?? tests/test_prospectus_input_snapshot.py.
+- Evidence: task-d-identity-report.md; task-d-identity-final-fullsuite.log; task-d-identity-final-comprehensive.log; task-d-identity-selftest.log.
+- Next: Stage only explicit F3/F6 implementation tests and progress files; commit with required final coauthor trailer.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Phase D F1 publication consistency (2026-10-06)
+- Baseline53e3c00; publish-v2 now binds main_file, separate output/cache digests and the exact loader snapshot pair inside payload/manifest run_identity. Converted and reused pairs are staged; reused still records cache=reused.
+- Approved order deviation: companions -> main JSON -> raw cache JSON/meta -> manifest. File-by-file publication remains non-atomic; mixed generations fail verification, while unchanged early replacements may leave the prior coherent set valid. Stale cleanup uses only known companion names.
+- Original focused RED214failed/72passed; focused GREEN310passed; supplementary baseline reconstruction38failed/5passed explicitly labelled reconstruction. Two obsolete doubles fixed after initial broad2failures: authority missing snapshot fields; OCR settings changed only at loader boundary. Corrected focused557passed; validation64passed.
+- Final MAIN baseline suite910passed/13subtests/3warnings; GUI comprehensive916passed/13subtests/5warnings; selftest80/80. External evidence/report task-d-publish-report.md in approved scratch root. Public six publish arguments retained with keyword-only cache_hashes; payload remainsv3.2. Default paths and staging/temp names unchanged for S1.
+- Independent spec/quality review and remaining D queue/phase gates remain controller-owned; no maincheckout edits, sync, push, merge or worktree removal.
+
+### Codex recovery checkpoint 2026-10-06T21:36:13+08:00
+- Task: Phase D F1 publication; step: all gates GREEN; report written; before explicit commit; owner: d_publish.
+- HEAD: 53e3c000958eae9cf4e12e197a6e54b7cc7b2e84; state: M backend/bintanong_tools/prospectus_extractor/pipeline.py
+ M backend/bintanong_tools/prospectus_extractor/publish.py
+ M plans/plan_current_progress/extractor_split_progress.md
+ M tests/test_prospectus_authority.py
+ M tests/test_prospectus_batch_skip.py
+ M tests/test_prospectus_cache.py
+ M tests/test_prospectus_publication.py
+ M tests/test_prospectus_publish.py.
+- Evidence: task-d-publish-report.md; task-d-publish-final-fullsuite.log; task-d-publish-final-comprehensive.log; task-d-publish-selftest.log.
+- Next: Explicitly stage two production files, five test files and progress; commit with required trailer; parent independently reviews baseline53e3c00..tip..
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T21:37:12+08:00
+- Task: D F1 publication; step: Committed597e8c0 clean; independent specification review active; owner: /root/d_publish_spec.
+- HEAD: 597e8c0289b8c090edf494248a9bd3fedad6aeb4; state: clean.
+- Evidence: task-d-publish-report.md main910 comprehensive916 +13subtests selftest80/80; task-d-publish-review-package.md.
+- Next: Read spec review, reproduce any findings through original implementer; then independent quality review of53e3c00..597e8c0.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T21:40:55+08:00
+- Task: D F1 publication; step: 597e8c0 SPEC APPROVED/NONE; separate quality review active; owner: /root/d_publish_quality.
+- HEAD: 597e8c0289b8c090edf494248a9bd3fedad6aeb4; state: M plans/plan_current_progress/extractor_split_progress.md.
+- Evidence: task-d-publish-spec-review.md APPROVED/NONE; task-d-publish-report.md main910 comprehensive916 +13 selftest80/80.
+- Next: Read quality review; resolve confirmed findings through original implementer, or dispatch remainingF2/F4/F5/S1/S2/S4 brief on597e8c0.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T21:48:07+08:00
+- Task: D F2 discovery; step: RED observed: 11 failed, 8 passed, 19 deselected; production unchanged; owner: /root/d_discovery.
+- HEAD: 597e8c0289b8c090edf494248a9bd3fedad6aeb4; state: M plans/plan_current_progress/extractor_split_progress.md
+ M tests/test_prospectus_batch_skip.py.
+- Evidence: task-d-discovery-brief.md; task-d-discovery-red.log.
+- Next: Implement minimal scan_inputs root-relative directory and marker filter, then run focused scan/batch/TUI relevant tests..
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T21:48:55+08:00
+- Task: D F2 discovery; step: Focused GREEN 48 passed; no warnings; preparing main full-suite gate; owner: /root/d_discovery.
+- HEAD: 597e8c0289b8c090edf494248a9bd3fedad6aeb4; state: M backend/bintanong_tools/prospectus_extractor/batch.py
+ M plans/plan_current_progress/extractor_split_progress.md
+ M tests/test_prospectus_batch_skip.py.
+- Evidence: task-d-discovery-red.log; task-d-discovery-green.log.
+- Next: Run main full suite with two approved ignores and external basetemp; inspect results before report/commit..
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T21:51:47+08:00
+- Task: D F2 discovery; step: Main full GREEN928passed/13subtests/3warnings; TUI smokePASS; report ready, before commit; owner: /root/d_discovery.
+- HEAD: 597e8c0289b8c090edf494248a9bd3fedad6aeb4; state: M backend/bintanong_tools/prospectus_extractor/batch.py
+ M plans/plan_current_progress/extractor_split_progress.md
+ M tests/test_prospectus_batch_skip.py.
+- Evidence: task-d-discovery-report.md; task-d-discovery-red.log; task-d-discovery-green.log; task-d-discovery-tui.log; task-d-discovery-full.log.
+- Next: Explicitly stage batch.py, test_prospectus_batch_skip.py and preserved progress; commit F2 with required trailer, then update report/checkpoint and parent review..
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Phase D F2 discovery (2026-10-06)
+- Base597e8c0; shared scan_inputs now checks standard ignored names only in root-relative directory components, retaining legitimate failed/FAILED inputs and requested filenames/JSON. scan_pdfs alias and batch/TUI/isolated callers use the shared fix.
+- Ruling: failure.json within candidate parent directories through selected root marks the diagnostic subtree, including direct selection of failed/run; markers above root ignored. A user folder carrying that marker is intentionally diagnostic until removed. No payload parsing, new dependency, configuration or filesystem abstraction.
+- RED11failed/8passed/19deselected; focused GREEN48passed/no warnings; real TUI scan smokePASS; main full928passed/13subtests/3upstream warnings. External task-d-discovery-report.md and red/green/TUI/full logs in approved scratch. Existing controller F1 review checkpoints preserved.
+- Complete GUI-review suite and standalone final-gate selftest NOT RUN for this task, deferred to Phase D final gates; no prior count reused as current evidence. F2 independent spec/quality review pending. F4/F5/S1/S2/S4 and final Phase D gates/Task10 remain; no Phase D completion claim.
+
+### Codex recovery checkpoint 2026-10-06T21:52:12+08:00
+- Task: D F2 discovery; step: Committeddf5eec4; red/green/main full/TUI verified; separate parent reviews pending; owner: /root/d_discovery.
+- HEAD: df5eec4bdf0d3b9f46addfce7911b00a705ec126; state: clean.
+- Evidence: task-d-discovery-report.md; task-d-discovery-red.log; task-d-discovery-green.log; task-d-discovery-tui.log; task-d-discovery-full.log.
+- Next: Parent review committed597e8c0289b8c090edf494248a9bd3fedad6aeb4..df5eec4; preserve new sole dirty progress checkpoint for next focused commit..
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T21:53:04+08:00
+- Task: D F2 discovery; step: Committeddf5eec4; red11failed focused48passed full928+13; spec review active; owner: /root/d_discovery_spec.
+- HEAD: df5eec4bdf0d3b9f46addfce7911b00a705ec126; state: M plans/plan_current_progress/extractor_split_progress.md.
+- Evidence: task-d-discovery-report.md; task-d-discovery-review-package.md; task-d-discovery-full.log928passed/3warnings/+13.
+- Next: Read F2 spec verdict then independent quality review; next F4 LF task, followed S1 S2 S4 F5 and finalDgates.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T21:55:50+08:00
+- Task: D F2 discovery review repair; step: SPEC found pattern traversal root escape atdf5eec4; final CHANGES_REQUIRED report being written; owner: /root/d_discovery_spec.
+- HEAD: df5eec4bdf0d3b9f46addfce7911b00a705ec126; state: M plans/plan_current_progress/extractor_split_progress.md.
+- Evidence: Pending task-d-discovery-spec-review.md; external tiny traversal probe discovered ../*.pdf reads above-root failure.json.
+- Next: Read concrete spec finding/probe; original d_discovery reproduces failing regression and fixes shared scan_inputs boundary; re-review before quality.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T21:59:03+08:00
+- Task: D F2 discovery repair1; step: Reproduced traversal probe; RED18failed/6passed/38deselected; production unchanged; owner: /root/d_discovery.
+- HEAD: df5eec4bdf0d3b9f46addfce7911b00a705ec126; state: M plans/plan_current_progress/extractor_split_progress.md
+ M tests/test_prospectus_batch_skip.py.
+- Evidence: task-d-discovery-spec-review.md; task-d-discovery-repair-reproduction.log; task-d-discovery-repair-red.log.
+- Next: Add minimal pathlib pattern rejection, focused green plus repaired targeted probe, then main full baseline..
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T21:59:56+08:00
+- Task: D F2 discovery repair1; step: Focused GREEN72passed/no warnings; traversal repair probePASS; before main full gate; owner: /root/d_discovery.
+- HEAD: df5eec4bdf0d3b9f46addfce7911b00a705ec126; state: M backend/bintanong_tools/prospectus_extractor/batch.py
+ M plans/plan_current_progress/extractor_split_progress.md
+ M tests/test_prospectus_batch_skip.py.
+- Evidence: task-d-discovery-repair-red.log; task-d-discovery-repair-green.log; task-d-discovery-repair-probe.log.
+- Next: Run main full suite with two approved ignores/external basetemp; inspect result before repair report/commit..
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T22:02:01+08:00
+- Task: D F2 discovery repair1; step: Full GREEN952passed/13subtests/3warnings; focused72passed/probePASS; before explicit repair commit; owner: /root/d_discovery.
+- HEAD: df5eec4bdf0d3b9f46addfce7911b00a705ec126; state: M backend/bintanong_tools/prospectus_extractor/batch.py
+ M plans/plan_current_progress/extractor_split_progress.md
+ M tests/test_prospectus_batch_skip.py.
+- Evidence: task-d-discovery-report.md; task-d-discovery-repair-reproduction.log; task-d-discovery-repair-red.log; task-d-discovery-repair-green.log; task-d-discovery-repair-probe.log; task-d-discovery-repair-full.log.
+- Next: Append result/progress; stage only batch.py, test_prospectus_batch_skip.py and preserved progress; commit with required trailer; postcommit checkpoint/report exact tip..
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Phase D F2 specification repair round1 (2026-10-06)
+- Reproduced Important review finding: configured ../*.pdf yielded root/../course.pdf and above-root failure.json changed discovery. Original reviewer probe preserved; reproduction logged externally.
+- Ruling: root-relative glob patterns cannot have any parent component or anchor. A single PureWindowsPath lexical guard recognizes slash/backslash parent, rooted, drive-relative/absolute and UNC patterns and raises explicit ValueError before glob; valid descendant globs preserved, no symlink resolution/policy change or filesystem abstraction.
+- Repair RED18failed/6passed/38deselected; focused GREEN72passed/no warnings; repaired recursive/nonrecursive probePASS with/without above-root marker; main full952passed/13subtests/3upstream warnings. Exact commands/evidence appended task-d-discovery-report.md; repair reproduction/red/green/probe/full logs external.
+- Existing controller/implementer progress checkpoints preserved. Complete GUI-review suite and standalone final selftest NOT RUN for scanner repair, final Phase D gates remain. Parent same-seat specification re-review before separate quality review; F4/F5/S1/S2/S4/Task10 remain, no Phase D completion claim.
+
+### Codex recovery checkpoint 2026-10-06T22:02:21+08:00
+- Task: D F2 discovery repair1; step: Committed4a0cdb7; repair RED/GREEN/probe/main full verified; specification re-review pending; owner: /root/d_discovery.
+- HEAD: 4a0cdb794a337b9cc91846d16585478c3bb5fde0; state: clean.
+- Evidence: task-d-discovery-report.md; task-d-discovery-repair-red.log; task-d-discovery-repair-green.log; task-d-discovery-repair-probe.log; task-d-discovery-repair-full.log.
+- Next: Parent specification re-review immutable baseline597e8c0..4a0cdb7 with repair delta df5eec4..4a0cdb7; preserve sole dirty postcommit progress checkpoint..
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T22:03:12+08:00
+- Task: D F2 repaired discovery; step: Committed4a0cdb7; repairred18failed focused72passed full952+13; spec re-review active; owner: /root/d_discovery_spec.
+- HEAD: 4a0cdb794a337b9cc91846d16585478c3bb5fde0; state: M plans/plan_current_progress/extractor_split_progress.md.
+- Evidence: task-d-discovery-report.md repairsection; task-d-discovery-final-review-package.md; task-d-discovery-repair-full.log952+13/3warnings.
+- Next: Read spec re-review verdict, then separate quality review597e8c0..4a0cdb7; next F4 LF task.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T22:05:10+08:00
+- Task: D F2 repaired discovery; step: 4a0cdb7 SPEC APPROVED; independent quality review active; owner: /root/d_discovery_quality.
+- HEAD: 4a0cdb794a337b9cc91846d16585478c3bb5fde0; state: M plans/plan_current_progress/extractor_split_progress.md.
+- Evidence: task-d-discovery-spec-rereview.md APPROVED, independent4-caseprobe passed; report/full952+13.
+- Next: Resolve quality findings or dispatch F4 LF task on4a0cdb7; remainingS1/S2/S4/F5 and finalDgates.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T22:12:13+08:00
+- Task: D F4 LF artifacts; step: RED verified3failed/126deselected; production unchanged; owner: /root/d_lf.
+- HEAD: 4a0cdb794a337b9cc91846d16585478c3bb5fde0; state: M plans/plan_current_progress/extractor_split_progress.md
+ M tests/test_prospectus_batch_skip.py
+ M tests/test_prospectus_publish.py.
+- Evidence: task-d-lf-brief.md; task-d-lf-red.log.
+- Next: Reuse existing publish.write_text_lf for batch JSON and set DictWriter lineterminator LF; run exact regressions GREEN then focused suites..
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T22:12:44+08:00
+- Task: D F4 LF artifacts; step: GREEN3passed/126deselected/no warnings; before focused suites; owner: /root/d_lf.
+- HEAD: 4a0cdb794a337b9cc91846d16585478c3bb5fde0; state: M backend/bintanong_tools/prospectus_extractor/batch.py
+ M backend/bintanong_tools/prospectus_extractor/views.py
+ M plans/plan_current_progress/extractor_split_progress.md
+ M tests/test_prospectus_batch_skip.py
+ M tests/test_prospectus_publish.py.
+- Evidence: task-d-lf-red.log; task-d-lf-green.log.
+- Next: Run focused batch/publish/publication writer suites, inspect results, then main full excluded baseline..
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T22:35:39+08:00
+- Task: D F4 LF artifacts resumed; step: Initial LF RED3 verified from prior logs; new bare-CR regression GREEN3 on main Python3.13.5; QUOTE_ALL hypothesis disproved; owner: /root/d_lf_resume.
+- HEAD: 4a0cdb794a337b9cc91846d16585478c3bb5fde0; state: M backend/bintanong_tools/prospectus_extractor/batch.py
+ M backend/bintanong_tools/prospectus_extractor/views.py
+ M plans/plan_current_progress/extractor_split_progress.md
+ M tests/test_prospectus_batch_skip.py
+ M tests/test_prospectus_publish.py.
+- Evidence: task-d-lf-red.log; task-d-lf-cr-red.log.
+- Next: Verify current GUI-review stdlib quoting; retain minimal quoting if safe; focused and main full suite.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T22:37:23+08:00
+- Task: D F4 LF artifacts resumed; step: Focused GREEN361 passed, no warnings; minimal quoting safe on both current Python3.13.5 runtimes; owner: /root/d_lf_resume.
+- HEAD: 4a0cdb794a337b9cc91846d16585478c3bb5fde0; state: M backend/bintanong_tools/prospectus_extractor/batch.py
+ M backend/bintanong_tools/prospectus_extractor/views.py
+ M plans/plan_current_progress/extractor_split_progress.md
+ M tests/test_prospectus_batch_skip.py
+ M tests/test_prospectus_publish.py.
+- Evidence: task-d-lf-red.log; task-d-lf-cr-red.log; task-d-lf-runtime-probe.log; task-d-lf-resumed-focused.log.
+- Next: Run main full suite with two approved ignores; inspect results, report and explicit commit.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T22:37:49+08:00
+- Task: D F4 LF artifacts resumed; step: Focused GREEN361 passed; main full currently running; QUOTE_ALL hypothesis superseded; owner: /root/d_lf_resume.
+- HEAD: 4a0cdb794a337b9cc91846d16585478c3bb5fde0; state: M backend/bintanong_tools/prospectus_extractor/batch.py
+ M backend/bintanong_tools/prospectus_extractor/views.py
+ M plans/plan_current_progress/extractor_split_progress.md
+ M tests/test_prospectus_batch_skip.py
+ M tests/test_prospectus_publish.py.
+- Evidence: task-d-lf-resumed-focused.log; task-d-lf-runtime-probe.log.
+- Next: Poll exec session95634; read task-d-lf-resumed-full.log then report/commit if green.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T22:42:19+08:00
+- Task: D F4 LF artifacts resumed; step: Fresh focused361 passed and full956 passed/13 subtests/3 upstream warnings; verified before explicit commit; owner: /root/d_lf_resume.
+- HEAD: 4a0cdb794a337b9cc91846d16585478c3bb5fde0; state: M backend/bintanong_tools/prospectus_extractor/batch.py
+ M backend/bintanong_tools/prospectus_extractor/views.py
+ M plans/plan_current_progress/extractor_split_progress.md
+ M tests/test_prospectus_batch_skip.py
+ M tests/test_prospectus_publish.py.
+- Evidence: task-d-lf-red.log; task-d-lf-green.log; task-d-lf-cr-red.log; task-d-lf-runtime-probe.log; task-d-lf-resumed-focused.log; task-d-lf-resumed-full.log.
+- Next: Save concise report and F4 progress; explicitly stage five authorized paths; commit with required Claude trailer.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Phase D F4 LF artifacts (2026-10-06)
+- Batch manifest reuses publish.write_text_lf; review CSV uses stdlib LF record separators with existing UTF8-sig BOM, native minimal quoting, all23 columns and exact values. No output/schema/name changes.
+- Preserved interrupted worker authentic LF RED3failed/126deselected and GREEN3passed/126deselected. Added bare-CR round-trip parameter without comma; its attempted RED actually passed3cases, explicitly characterization rather than failing evidence.
+- Root superseded QUOTE_ALL hypothesis: main and GUI-review Python3.13.5 both already quote bareCR under LF/QUOTE_MINIMAL; backend requires ==3.13.*. Native quoting retained; runtime probe/log external, no unsupported-runtime workaround or new dependency.
+- Fresh focused GREEN361passed/no warnings; main full956passed/13subtests/3upstream warnings with two approved API/embedding excludes. task-d-lf-report.md and exact original/resume logs outside Git in approved scratch; previous progress checkpoints preserved.
+- GUI-review comprehensive suite and standalone final D selftest NOT RUN for F4, deferred final gates. Parent independent specification then quality review pending; S1/S2/S4/F5/final D gates/Task10 and downstream queue remain. Phase D not complete.
+
+### Codex recovery checkpoint 2026-10-06T22:42:47+08:00
+- Task: D F4 LF artifacts; step: Committed 52da4aaca7d734e83054b1ecd39221ac09302a3b; focused361/full956+13 verified; parent specification then quality review pending; owner: /root/d_lf_resume.
+- HEAD: 52da4aaca7d734e83054b1ecd39221ac09302a3b; state: clean.
+- Evidence: task-d-lf-report.md; task-d-lf-red.log; task-d-lf-green.log; task-d-lf-cr-red.log; task-d-lf-runtime-probe.log; task-d-lf-resumed-focused.log; task-d-lf-resumed-full.log.
+- Next: Parent review 4a0cdb794a337b9cc91846d16585478c3bb5fde0..52da4aaca7d734e83054b1ecd39221ac09302a3b; preserve sole dirty postcommit progress checkpoint.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T22:45:53+08:00
+- Task: D F4 LF artifacts review; step: 52da4aa SPEC APPROVED/NONE; separate qualityseat active; owner: /root/d_lf_quality.
+- HEAD: 52da4aaca7d734e83054b1ecd39221ac09302a3b; state: M plans/plan_current_progress/extractor_split_progress.md.
+- Evidence: task-d-lf-spec-review.md APPROVED/NONE; focused361 full956+13; task-d-paths-brief.md ready.
+- Next: Qualityverdict then S1 compactpaths task on52da4aa; use latest32digitstemkey/defaultroot ruling.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T22:51:46+08:00
+- Task: D S1 compact Windows paths; step: Tests written; production unchanged; ready RED; owner: /root/d_paths.
+- HEAD: 52da4aaca7d734e83054b1ecd39221ac09302a3b; state: M plans/plan_current_progress/extractor_split_progress.md
+ M tests/test_prospectus_cache.py
+ M tests/test_prospectus_publish.py.
+- Evidence: task-d-paths-brief.md; latest final32digest ruling; s1-path-projection.json.
+- Next: Run S1 RED selectors in publish/cache tests with external basetemp; inspect expected failures before production edits.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T22:52:51+08:00
+- Task: D S1 compact Windows paths; step: Authentic RED8failed1passed88deselected; production unchanged; owner: /root/d_paths.
+- HEAD: 52da4aaca7d734e83054b1ecd39221ac09302a3b; state: M plans/plan_current_progress/extractor_split_progress.md
+ M tests/test_prospectus_cache.py
+ M tests/test_prospectus_publish.py.
+- Evidence: task-d-paths-red-final.log; task-d-paths-red.log.
+- Next: Implement home/Bintanong/output, shared32digest stage prefix and mkstemp .t-; rerun exact RED selector GREEN.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T22:53:22+08:00
+- Task: D S1 compact Windows paths; step: GREEN9passed88deselected; minimal3productionfiles changed; owner: /root/d_paths.
+- HEAD: 52da4aaca7d734e83054b1ecd39221ac09302a3b; state: M backend/bintanong_tools/prospectus_extractor/loader.py
+ M backend/bintanong_tools/prospectus_extractor/paths.py
+ M backend/bintanong_tools/prospectus_extractor/publish.py
+ M plans/plan_current_progress/extractor_split_progress.md
+ M tests/test_prospectus_cache.py
+ M tests/test_prospectus_publish.py.
+- Evidence: task-d-paths-red-final.log; task-d-paths-green.log.
+- Next: Run focused path/cache/publication/batch suites; actual generated-name all44 corpus path projection; then main full excluded baseline.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T22:55:00+08:00
+- Task: D S1 compact Windows paths; step: Focused386passed/no warnings; before main full approved excludes; owner: /root/d_paths.
+- HEAD: 52da4aaca7d734e83054b1ecd39221ac09302a3b; state: M backend/bintanong_tools/prospectus_extractor/loader.py
+ M backend/bintanong_tools/prospectus_extractor/paths.py
+ M backend/bintanong_tools/prospectus_extractor/publish.py
+ M plans/plan_current_progress/extractor_split_progress.md
+ M tests/test_prospectus_cache.py
+ M tests/test_prospectus_publish.py.
+- Evidence: task-d-paths-focused.log386passed; task-d-paths-red-final.log; task-d-paths-green.log; task-d-paths-actual-projection.json.
+- Next: Run main Python -m pytest -q tests --ignore=tests/test_api_probes.py --ignore=tests/test_embedding_service.py -p no:cacheprovider --basetemp external/s1-full-temp, log task-d-paths-full.log; inspect exit/counts before commit.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T22:56:47+08:00
+- Task: D S1 compact Windows paths; step: Fresh full961passed13subtests3upstreamwarnings; all44projection251max; precommit; owner: /root/d_paths.
+- HEAD: 52da4aaca7d734e83054b1ecd39221ac09302a3b; state: M backend/bintanong_tools/prospectus_extractor/loader.py
+ M backend/bintanong_tools/prospectus_extractor/paths.py
+ M backend/bintanong_tools/prospectus_extractor/publish.py
+ M plans/plan_current_progress/extractor_split_progress.md
+ M tests/test_prospectus_cache.py
+ M tests/test_prospectus_publish.py.
+- Evidence: task-d-paths-red-final.log8failed1passed; task-d-paths-green.log9passed; task-d-paths-focused.log386passed; task-d-paths-full.log961passed13subtests3warnings; task-d-paths-actual-projection.json.
+- Next: Finish S1 report/progress and normalize edited text LF; stage exact paths.py publish.py loader.py test_prospectus_publish.py test_prospectus_cache.py extractor_split_progress.md; commit with required Claude trailer.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Phase D S1 compact Windows paths (2026-10-06)
+- Portable default is Path.home() / 'Bintanong' / 'output', replacing the package-local docling_jsonified_output default. Existing artifacts stay in their old location; old consumers must pass explicit --output (JSON path for one file, root for batch). No previous outputs moved/deleted and no home artifacts generated during verification. Existing final/cache filenames, batch sanitization, explicit overrides and failed/<base>/ layout remain unchanged.
+- Stage .s-<32hex UTF8 stem SHA256 prefix>-<8 UUID hex> reuses shared identity.bytes_sha256 through one private prefix helper for generation/cleanup. Cleanup targets the full128bit stem prefix, preserving other stems, unrelated folders and matching regular files. Earlier8digit proposal superseded: cost24 extra path characters, actual stage name44. One writer per output stem retained; no arbitrary-neighbor cleanup or new framework.
+- Atomic cache writer keeps unique tempfile.mkstemp and replacement/failure semantics, shortening only prefix to .t- with .tmp suffix (actual name15). Regression checks cover interleaved writes, locked replacement retry/cleanup and interrupted write cleanup while preserving old bytes.
+- Authentic TDD RED8failed1passed88deselected before production; GREEN9passed88deselected. Fresh focused386passed/no warnings; main full961passed/13subtests/3 existing upstream warnings, with approved API/embedding exclusions. Exact commands/logs in external task-d-paths-report.md and task-d-paths-{red-final,green,focused,full}.log.
+- Read-only original44 corpus projection used actual output directories and generated stage/temp names: root35, final181/stage226/temp161/failed251 versus old final/cache268. Exact maxima paths in external task-d-paths-actual-projection.json. Longest real Tiniguiban CS relative input and separate Citizens Charter BOR proposal (2) boundary covered; no proposal opened/converted. Current corpus fits at most8 extra root characters below260; arbitrary longer home/explicit roots require caller-selected shorter --output, never silent artifact renaming.
+- GUI comprehensive suite, standalone selftest80, semantic44 comparer and trials NOT RUN for S1, deferred parent final D gates. Independent specification then quality reviews pending. S2/S4/F5/final D gates/Task10 and downstream queue remain; Phase D not complete. Existing F4 postcommit/review progress preserved.
+
+### Codex recovery checkpoint 2026-10-06T22:57:41+08:00
+- Task: D S1 compact Windows paths; step: Committed4320327; targeted9 focused386 full961+13 verified; parent reviews pending; owner: /root/d_paths.
+- HEAD: 4320327bb68ec0973dd79ee7716ab5d893fe00a8; state: clean.
+- Evidence: task-d-paths-report.md; task-d-paths-red-final.log; task-d-paths-green.log; task-d-paths-focused.log; task-d-paths-full.log; task-d-paths-projection.log; task-d-paths-actual-projection.json.
+- Next: Parent fresh specification review 52da4aaca7d734e83054b1ecd39221ac09302a3b..4320327, then independent quality review; preserve sole dirty postcommit progress checkpoint.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T22:58:38+08:00
+- Task: D S1 Windows paths review; step: Committed 4320327; red 8 failures, focused 386 and full 961 +13 passed; specification review active; owner: /root/d_paths_spec.
+- HEAD: 4320327bb68ec0973dd79ee7716ab5d893fe00a8; state: M plans/plan_current_progress/extractor_split_progress.md.
+- Evidence: task-d-paths-report.md; task-d-paths-review-package.md; task-d-paths-actual-projection.json; main full 961 +13 subtests/3 warnings.
+- Next: Read S1 specification verdict, then independent quality review; dispatch S2/S4 task after approval.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T23:01:13+08:00
+- Task: D S1 Windows paths review; step: 4320327 specification APPROVED/NONE; separate quality review active; owner: /root/d_paths_quality.
+- HEAD: 4320327bb68ec0973dd79ee7716ab5d893fe00a8; state: M plans/plan_current_progress/extractor_split_progress.md.
+- Evidence: task-d-paths-spec-review.md APPROVED/NONE; report focused386/full961+13; task-d-paths-actual-projection.json.
+- Next: Read quality verdict; after approval dispatch task-d-skip-tui-brief.md on 4320327, then F5/final D gates.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T23:08:08+08:00
+- Task: D S2 context skip; step: Authentic RED18failed62deselected; eligible flag absent and context/malformed runs incorrectly skipped; owner: /root/d_skip_tui.
+- HEAD: 4320327bb68ec0973dd79ee7716ab5d893fe00a8; state: M plans/plan_current_progress/extractor_split_progress.md
+ M tests/test_prospectus_batch_skip.py.
+- Evidence: task-d-s2-red.log.
+- Next: Implement presence-only skip_reusable in pipeline and fail-closed skip_check; run identical focused green command.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T23:09:38+08:00
+- Task: D S2 context skip; step: Corrected authentic RED18failed62deselected with successful real payload/publication before expected skip failures; owner: /root/d_skip_tui.
+- HEAD: 4320327bb68ec0973dd79ee7716ab5d893fe00a8; state: M plans/plan_current_progress/extractor_split_progress.md
+ M tests/test_prospectus_batch_skip.py.
+- Evidence: task-d-s2-red-final.log.
+- Next: Add minimal skip_reusable presence flag and exact-boolean skip guard; rerun focused green selector context_publication or skip_eligibility or repeat_run.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T23:10:53+08:00
+- Task: D S2 context skip; step: Validated RED18failed62deselected; all9 context publications complete/nonerror, old skip returned True; owner: /root/d_skip_tui.
+- HEAD: 4320327bb68ec0973dd79ee7716ab5d893fe00a8; state: M plans/plan_current_progress/extractor_split_progress.md
+ M tests/test_prospectus_batch_skip.py.
+- Evidence: task-d-s2-validated-red.log.
+- Next: Reapply minimal flag/guard, run validated focused GREEN then batch/identity/publish/publication/cache/authority suites.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T23:12:32+08:00
+- Task: D S2 context skip; step: Validated green18/focused636passed; before main full approved excludes; owner: /root/d_skip_tui.
+- HEAD: 4320327bb68ec0973dd79ee7716ab5d893fe00a8; state: M backend/bintanong_tools/prospectus_extractor/batch.py
+ M backend/bintanong_tools/prospectus_extractor/pipeline.py
+ M plans/plan_current_progress/extractor_split_progress.md
+ M tests/test_prospectus_batch_skip.py.
+- Evidence: task-d-s2-validated-red.log; task-d-s2-validated-green.log; task-d-s2-focused.log.
+- Next: Run main Python -m pytest -q tests --ignore=tests/test_api_probes.py --ignore=tests/test_embedding_service.py -p no:cacheprovider --basetemp external/s2-full-temp; inspect result and commit S2 only.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Phase D S2 context-sensitive skip (2026-10-06)
+- Pipeline persists run_identity.skip_reusable=False for any supplied source/approved_scope/review_entries/repair_provider via is None presence checks, including empty mappings/lists/generators and falsey typed source/provider. Normal contextless runs persist True. Publisher retains identical bound main/manifest identity and captured PDF/cache hashes; run key and schema unchanged, no provider serialization or extra ledger consumption. Flag grants no source/review/eligibility authority.
+- Batch requires literal True for skip; False reason previous run used supplied context, missing/nonboolean reason previous run skip eligibility is unknown. All existing audit/identity/v2 publication/cache/completeness checks remain. Exact unchanged and force skip reasons replace ineffective assertion. Old outputs without known eligibility are reparsed once rather than trusted.
+- Validated RED18failed62deselected; GREEN18passed62deselected; focused636passed/no warnings; main full978passed13subtests3existing upstream warnings with only approved API/embedding ignores. Logs and exact commands in external task-d-skip-tui-report.md and task-d-s2-{validated-red,validated-green,focused,full}.log. Earlier fixture mistakes preserved in initial/intermediate logs and explicitly superseded: wrong evidence adapter caused audit error, then unmatched requested companions caused incomplete-output refusal. Validated red used complete nonerror published sets returning True under old skip.
+- S2 self-review found no remaining production concern; independent specification then quality review pending. S4/F5/final D gates/Task10 remain. GUI comprehensive/selftest/original44 corpus/trials NOT RUN here; all downstream/human gates pending, Phase D incomplete. Existing S1 review and checkpoint progress preserved.
+
+### Codex recovery checkpoint 2026-10-06T23:14:29+08:00
+- Task: D S2 context skip; step: Fresh focused636/full978+13/3existingwarnings; S2 precommit; owner: /root/d_skip_tui.
+- HEAD: 4320327bb68ec0973dd79ee7716ab5d893fe00a8; state: M backend/bintanong_tools/prospectus_extractor/batch.py
+ M backend/bintanong_tools/prospectus_extractor/pipeline.py
+ M plans/plan_current_progress/extractor_split_progress.md
+ M tests/test_prospectus_batch_skip.py.
+- Evidence: task-d-skip-tui-report.md; task-d-s2-validated-red.log; task-d-s2-validated-green.log; task-d-s2-focused.log; task-d-s2-full.log.
+- Next: Stage exact batch.py pipeline.py test_prospectus_batch_skip.py extractor_split_progress.md; commit S2 with Claude trailer; then S4 red.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T23:15:19+08:00
+- Task: D S4 TUI force; step: S2 committed10c2d8b green18/focused636/full978+13; S4 tests next; owner: /root/d_skip_tui.
+- HEAD: 10c2d8b5ac30313c7d5c7d2831fb7c8670cd146a; state: clean.
+- Evidence: task-d-skip-tui-report.md; task-d-s2-full.log.
+- Next: Add behavioral TUI config/display, actual single process True/False, and real batch skip-force precedence tests; capture S4 RED before changing tui.py.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T23:15:58+08:00
+- Task: D S4 TUI force; step: S2 implementation-only committed10c2d8b; S4 RED4failed2passed80deselected; owner: /root/d_skip_tui.
+- HEAD: 10c2d8b5ac30313c7d5c7d2831fb7c8670cd146a; state: M plans/plan_current_progress/extractor_split_progress.md
+ M tests/test_prospectus_batch_skip.py.
+- Evidence: task-d-s4-red.log; task-d-skip-tui-report.md.
+- Next: Modify tui.py only: display force, accurate identity/completeness nonerror skip prompt, configure existing force flag, pass actual single-file force kwarg; run S4 GREEN.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T23:16:30+08:00
+- Task: D S4 TUI force; step: RED4failed2passed; GREEN6passed80deselected; before focused TUI and shared suite; owner: /root/d_skip_tui.
+- HEAD: 10c2d8b5ac30313c7d5c7d2831fb7c8670cd146a; state: M backend/bintanong_tools/prospectus_extractor/tui.py
+ M plans/plan_current_progress/extractor_split_progress.md
+ M tests/test_prospectus_batch_skip.py.
+- Evidence: task-d-s4-red.log; task-d-s4-green.log; task-d-skip-tui-report.md.
+- Next: Run batchskip/identity/publish/publication/cache/authority/markup focused suite; then approved main full before S4 commit.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T23:18:00+08:00
+- Task: D S4 TUI force; step: Fresh focused680passed/no warnings; before main full; owner: /root/d_skip_tui.
+- HEAD: 10c2d8b5ac30313c7d5c7d2831fb7c8670cd146a; state: M backend/bintanong_tools/prospectus_extractor/tui.py
+ M plans/plan_current_progress/extractor_split_progress.md
+ M tests/test_prospectus_batch_skip.py.
+- Evidence: task-d-s4-red.log; task-d-s4-green.log; task-d-s4-focused.log.
+- Next: Run main Python -m pytest -q tests --ignore=tests/test_api_probes.py --ignore=tests/test_embedding_service.py -p no:cacheprovider --basetemp external/s4-full-temp, log task-d-s4-full.log; inspect counts/warnings then commit S4.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Phase D S4 TUI skip wording and force configuration (2026-10-06)
+- Existing BatchConfig.force_reconvert now shown and configured via ask_yes_no with current default. Prompt explains force overrides skip-existing and cached conversion; skip prompt restricts reuse to identity-verified complete outputs with a non-error audit. Single-file TUI now passes the actual force_reconvert kwarg; interactive batch already used the same config. No new conversion implementation or config owner.
+- Authentic RED4failed2passed80deselected before production; GREEN6passed80deselected. Both True/False configuration transitions/display tested; actual single-file pipeline sees exact kwargs and converted/reused cache status, converter/build counts; actual interactive batch has force-over-skip precedence with exact reason. Focused680passed/no warnings; fresh main full984passed13subtests3existing upstream deprecations, only two approved API/embedding ignores. Exact commands/results in external task-d-skip-tui-report.md and task-d-s4-{red,green,focused,full}.log.
+- S2 implementation-only commit10c2d8b precedes S4; parent separate specification then quality review pending. Self-review no unresolved implementation concerns. F5/final D gates/Task10 and all downstream/human gates pending. GUI comprehensive/selftest/original44 corpus/trials NOT RUN for this batch; Phase D incomplete.
+
+### Codex recovery checkpoint 2026-10-06T23:20:17+08:00
+- Task: D S4 TUI force; step: Fresh focused680/full984+13/3existingwarnings; S4 precommit; owner: /root/d_skip_tui.
+- HEAD: 10c2d8b5ac30313c7d5c7d2831fb7c8670cd146a; state: M backend/bintanong_tools/prospectus_extractor/tui.py
+ M plans/plan_current_progress/extractor_split_progress.md
+ M tests/test_prospectus_batch_skip.py.
+- Evidence: task-d-skip-tui-report.md; task-d-s4-red.log; task-d-s4-green.log; task-d-s4-focused.log; task-d-s4-full.log.
+- Next: Stage exact tui.py test_prospectus_batch_skip.py progress; commit S4 with Claude trailer; record exact range/tips/Git state and return parent for spec then quality reviews.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T23:20:48+08:00
+- Task: D S2/S4 implementation-only batch; step: Committed10c2d8b and c40a38c; S2 full978+13, S4 full984+13/3warnings; separate reviews next; owner: /root/d_skip_tui.
+- HEAD: c40a38c9f633dd085766ca11f81f0dd3890810cc; state: clean.
+- Evidence: task-d-skip-tui-report.md; task-d-s2-validated-red.log; task-d-s2-validated-green.log; task-d-s2-focused.log; task-d-s2-full.log; task-d-s4-red.log; task-d-s4-green.log; task-d-s4-focused.log; task-d-s4-full.log.
+- Next: Parent fresh read-only specification review exact range4320327bb68ec0973dd79ee7716ab5d893fe00a8..c40a38c9f633dd085766ca11f81f0dd3890810cc then independent quality review; preserve sole dirty postcommit progress checkpoint.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T23:21:08+08:00
+- Task: D S2/S4 independent review; step: Implementation c40a38c verified 680 focused and 984 main plus13subtests; specification review next; owner: /root.
+- HEAD: c40a38c9f633dd085766ca11f81f0dd3890810cc; state: M plans/plan_current_progress/extractor_split_progress.md.
+- Evidence: task-d-skip-tui-report.md; task-d-s4-full.log; task-d-skip-tui-review-package.md.
+- Next: Specification review 4320327..c40a38c then separate quality review.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T23:25:13+08:00
+- Task: D S2/S4 independent reviews; step: Specification APPROVED NONE; independent S2 18 and S4 6 plus prompt probe passed; owner: /root.
+- HEAD: c40a38c9f633dd085766ca11f81f0dd3890810cc; state: M plans/plan_current_progress/extractor_split_progress.md.
+- Evidence: task-d-skip-tui-spec-review.md; task-d-skip-tui-report.md.
+- Next: Separate quality review of 4320327..c40a38c then final D gates.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T23:28:38+08:00
+- Task: D final verification and F5/Task10 documentation; step: S2/S4 specification and quality APPROVED NONE at c40a38c; final gate writer next; owner: /root.
+- HEAD: c40a38c9f633dd085766ca11f81f0dd3890810cc; state: M plans/plan_current_progress/extractor_split_progress.md.
+- Evidence: task-d-skip-tui-spec-review.md; task-d-skip-tui-quality-review.md; task-d-final-gates-rulings.md.
+- Next: Run final comprehensive/self-test/corpus/real-PDF gates, correct F5 and commit Task10 draft with whole-range reviews pending.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T23:30:51+08:00
+- Task: Phase D F5 Tasks 8-10; step: preflight verified c40a38c; begin final gates; owner: /root/d_final_gates.
+- HEAD: c40a38c9f633dd085766ca11f81f0dd3890810cc; state: M plans/plan_current_progress/extractor_split_progress.md.
+- Evidence: task-d-final-gates-rulings.md; task-d-final-gates-brief.md; task-d-s4-full.log unchanged tip main 984 passed.
+- Next: Resume final-gates agent; run fresh comprehensive GUI env, selftest and comparer against 641523d; see task-d-final-gates-rulings.md.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Codex recovery checkpoint 2026-10-06T23:36:31+08:00
+- Task: Phase D F5 Tasks 8-10; step: comprehensive990+13, comparer44/44, focused394, real gates passed, originals101unchanged; owner: /root/d_final_gates.
+- HEAD: c40a38c9f633dd085766ca11f81f0dd3890810cc; state: M plans/plan_current_progress/extractor_split_progress.md
+?? docs/decisions/prospectus-cache-and-publication.md.
+- Evidence: task-d-final-comprehensive.log; task-d-final-compare.log; task-d-final-focused.log; task-d-final-real.log; task-d-final-originals-after.json.
+- Next: Run task-d-final-corpus-gates.py with MAINPY from phase-d root; no real/comparer relaunch; then finalize three docs and exact-path commit, parent whole-range reviews pending.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
+
+### Phase D F5 and Tasks 8-10 final implementation/documentary gates (2026-10-06T23:37:16+08:00)
+- Base `641523d212839084da03d966ffbfca66c7e83e42`; reviewed unchanged production tip `c40a38c9f633dd085766ca11f81f0dd3890810cc`; branch `feat/prospectus-phase-d-safe-cache`. S2/S4 independent spec/quality APPROVED NONE; whole-range `641523d..final-documentary-tip` specification and quality PENDING. Phase D not fully complete.
+- Fresh GUI-review comprehensive: 990 passed, 13 subtests, 5 upstream warnings, exit 0; fresh focused: 394 passed, exit 0, includes 180 full before/after replacement interruptions; fresh MAINPY self-test: 80/80, exit 0. Reused unchanged-tip main gate `task-d-s4-full.log`: 984 passed, 13 subtests, 3 upstream warnings, with two approved API/embedding ignores; no gratuitous rerun, installs or main-venv synchronization.
+- Existing comparer `--base-ref 641523d --jobs 6 --status-report` with original semantic map and explicit retained `Bintanong-wt/d-baseline-641523d`: 44/44 identical, exit 0. Direct C states 1005/689/253/59/20/3/2 in blank_unreviewed/resolved/unresolved_reference/standing_condition/unreadable/alternative_or_exception/stated_none order. Regression equivalence, not extraction accuracy. B2 health 21/3/19/1 mixed/warnings_only/broken/clean; title_from_pdf 67, strip_banner 0, unclaimed_code 316, banner_leak 3. Trial 01/16/33 `check_against`: 0 errors each; helpers imported through WT-root runpy context.
+- Fresh real BSE-Franchising-and-Trading PDF copy `scratch/dg`: A: 1 extracted (WARN)/0 failed audit/0 skipped/0 errored, exit 0; B: 0/0/1/0, exit 0, identical run identity; C: 0/0/0/1, exit 1, ConversionError+traceback preserves 9 earlier outputs/cache files, no stage residue; D: 0/0/1/0, exit 0, retains diagnostics; E force: 1/0/0/0, exit 0, clears diagnostics. Real cached parse then equal-size/restored-mtime scratch mutation refused with `Input bytes changed since capture`, preserving prior set; restore+successful reused-cache publish clears diagnostics. Originals/cached inputs/map/trial files: 101 hashes unchanged around real and helper workflows; comparer began read-only before this snapshot, no before-comparer timing claim.
+- Fresh path-only default-root actual stage/temp projection reproduced 44 paths/maxima final 181/stage 226/temp 161/failed 251 under 35-character `~/Bintanong/output`; no home writes, arbitrary explicit-root guarantee or longest-filename real conversion claim. Original historical error pilots preserved, not freshly rerun.
+- F5 original Task 6 count corrected 15 to 14; authentic original red unavailable; reconstruction parent `29eb83200b593f24caa9179a28c0795c30621b5a` + `f802c764533bdf67267089bcc109416da5941ca9` tests/conftest observed 12 failed, 2 passed, explicitly not original chronology. Frozen test collection confirms 14; historical combined 61 retained without inferred correction. Evidence `reconstruct_task6.py`/`task6-red-reconstruction.log`.
+- Decision docs/decisions/prospectus-cache-and-publication.md covers all approved deviations and actual gates; current_progress.md updated. Historical plans and existing review/checkpoint history preserved. Evidence task-d-final-gates-report.md and task-d-final-{comprehensive,compare,corpus,focused,selftest,real,path-projection} logs + .exit markers external codex_resume_2026-10-06. No production changes.
+- Next: controller whole-range specification then independent quality review `641523d..documentary-tip`. GUI→E→F→OCR/formal/human gates pending, queue remains active; no push, dev merge, worktree removal or main dirty-file edit.
+
+### Codex recovery checkpoint 2026-10-06T23:42:26+08:00
+- Task: Phase D F5 Tasks 8-10; step: all fresh final runtime gates passed; three docpaths ready, whole-range reviews pending; owner: /root/d_final_gates.
+- HEAD: c40a38c9f633dd085766ca11f81f0dd3890810cc; state: M plans/plan_current_progress/current_progress.md
+ M plans/plan_current_progress/extractor_split_progress.md
+?? docs/decisions/prospectus-cache-and-publication.md.
+- Evidence: task-d-final-gates-report.md; task-d-final-comprehensive.log; task-d-final-selftest.log; task-d-final-focused.log; task-d-final-compare.log; task-d-final-corpus.log; task-d-final-real.log; task-d-final-path-projection.log.
+- Next: git add docs/decisions/prospectus-cache-and-publication.md plans/plan_current_progress/extractor_split_progress.md plans/plan_current_progress/current_progress.md; verify cached paths; commit with Claude trailer; postcommit checkpoint then parent separate whole-range reviews641523d..tip.
+- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
diff --git a/tests/conftest.py b/tests/conftest.py
index 54f29c9..7be9c1b 100644
--- a/tests/conftest.py
+++ b/tests/conftest.py
@@ -32,24 +32,24 @@ class FakeDoc:
 
 
 class FakeConverter:
     """Stands in for a Docling converter; the raw JSON carries the PDF bytes so tests can see which bytes were converted."""
 
     def __init__(self, fail: bool = False):
         self.fail = fail
         self.calls: list[str] = []
 
     def convert(self, path):
-        self.calls.append(str(path))
+        self.calls.append(path.name if hasattr(path, "stream") else str(path))
         if self.fail:
             raise RuntimeError("converter exploded")
-        marker = Path(path).read_bytes().decode("latin-1")
+        marker = (path.stream.read() if hasattr(path, "stream") else Path(path).read_bytes()).decode("latin-1")
         return SimpleNamespace(errors=[], document=FakeDoc({**RAW_BASE, "marker": marker}))
 
 
 @pytest.fixture
 def fake_docling(monkeypatch):
     def no_real_converter(*_args, **_kwargs):
         raise AssertionError("a real Docling converter was requested in a unit test")
 
     monkeypatch.setattr(loader, "ensure_docling_env", lambda: None)
     monkeypatch.setattr(loader, "load_docling", lambda: {"DoclingDocument": FakeDoc})
diff --git a/tests/test_prospectus_authority.py b/tests/test_prospectus_authority.py
index afcf9e6..7ae11c0 100644
--- a/tests/test_prospectus_authority.py
+++ b/tests/test_prospectus_authority.py
@@ -310,21 +310,40 @@ def test_hash_mismatch_raises_before_any_output_is_touched(tmp_path):
     assert out.read_text(encoding="utf-8") == "previous accepted output"
     assert not (tmp_path / "x_essentials.json").exists()
 
 
 def test_matching_hash_is_recorded_and_still_does_not_authorize(tmp_path, monkeypatch):
     pdf = tmp_path / "prospectus.pdf"
     pdf.write_bytes(b"%PDF-1.4\noriginal")
     source = ProvisionalSource(hashlib.sha256(b"%PDF-1.4\noriginal").hexdigest(), "local/prospectus.pdf")
     grid = [CS_HEADER, _merged("FIRST YEAR", 8), _cs_semester_row(), CONTROL]
     document = fixture_document(grid, [("title", "BACHELOR OF SCIENCE IN COMPUTER SCIENCE PROGRAM")])
-    monkeypatch.setattr(pipeline, "load_document", lambda *args, **kwargs: (document, None))
+    from backend.bintanong_tools.prospectus_extractor import identity
+    from backend.bintanong_tools.prospectus_extractor.loader import DocumentLoadResult, _cache_meta_path
+
+    def load_fixture(*args, **kwargs):
+        raw_path = kwargs["raw_json_path"]
+        raw = json.dumps({"texts": document.text_items, "tables": [{"data": {"grid": grid}}]}).encode()
+        raw_hash = hashlib.sha256(raw).hexdigest()
+        settings = identity.conversion_settings()
+        meta = json.dumps({
+            "identity_version": 1, "pdf_sha256": source.pdf_sha256,
+            "conversion_settings": settings,
+            "conversion_identity": identity.conversion_identity(source.pdf_sha256, settings),
+            "raw_json_sha256": raw_hash,
+        }).encode()
+        (kwargs["stage_dir"] / raw_path.name).write_bytes(raw)
+        (kwargs["stage_dir"] / _cache_meta_path(raw_path).name).write_bytes(meta)
+        return DocumentLoadResult(document, raw_path, "converted", raw, raw_hash,
+                                  meta, hashlib.sha256(meta).hexdigest())
+
+    monkeypatch.setattr(pipeline, "load_document_result", load_fixture)
     out = tmp_path / "x_prospectus.json"
 
     payload = pipeline.process_prospectus(pdf, output_path=out, semantic_doc_path=None, quiet=True, source=source)
 
     assert payload["authority"]["source_record"]["pdf_hash_check"] == "matched"
     assert "pdf_hash_not_checked" not in payload["authority"]["blocked_by"]
     assert payload["authority"]["eligibility_executable"] is False
     essentials = json.loads((tmp_path / "x_essentials.json").read_text(encoding="utf-8"))
     assert essentials["schema_version"] == "palsu-prospectus-essentials-v2"
     assert essentials["extraction_status"] == "EXTRACTED_WITH_WARNINGS"  # an audit result, never "verified"
diff --git a/tests/test_prospectus_batch_skip.py b/tests/test_prospectus_batch_skip.py
index 3d19248..65b20de 100644
--- a/tests/test_prospectus_batch_skip.py
+++ b/tests/test_prospectus_batch_skip.py
@@ -1,31 +1,36 @@
 """--skip-existing trusts a published set only when identity and audit status say so."""
 
 from __future__ import annotations
 
+from datetime import datetime
+import json
 from types import SimpleNamespace
 
 import pytest
 
-from backend.bintanong_tools.prospectus_extractor import batch, pipeline
+from backend.bintanong_tools.prospectus import ProvisionalSource
+from backend.bintanong_tools.prospectus_extractor import batch, identity, loader, pipeline, publish, tui
 from backend.bintanong_tools.prospectus_extractor.batch import BatchConfig, run_batch
+from backend.bintanong_tools.prospectus_extractor.selftest import (
+    CS_HEADER, _cs_row, _cs_semester_row, _merged, fixture_document,
+)
 
 pytestmark = pytest.mark.usefixtures("fake_docling")
 
 
 @pytest.fixture
 def env(tmp_path, monkeypatch, pdf_factory, converter, pipeline_state, snapshot):
     source = tmp_path / "pdfs"
     out = tmp_path / "out"
     pdf = pdf_factory(source)
-    monkeypatch.setattr(batch, "ensure_docling_env", lambda: None)
-    monkeypatch.setattr(batch, "get_shared_converter", lambda *a, **k: converter)
+    monkeypatch.setattr(loader, "get_shared_converter", lambda *a, **k: converter)
     # BatchConfig.write_md defaults to True; the stub payload is not renderable as markup.
     monkeypatch.setattr(pipeline, "render_prospectus_markup", lambda document, payload: "twin\n")
 
     def run(**overrides):
         config = BatchConfig(input_root=source, output_root=out, semantic_doc=None,
                              skip_existing=True, **overrides)
         return run_batch(config)
 
     return SimpleNamespace(pdf=pdf, out=out, converter=converter, state=pipeline_state,
                            run=run, snapshot=snapshot)
@@ -37,21 +42,23 @@ def only(summary):
 
 def test_repeat_run_of_unchanged_input_skips_and_leaves_identical_files(env):
     assert only(env.run())["status"] == "ok"
     before = env.snapshot(env.out)
     mtimes = {p.name: p.stat().st_mtime_ns for p in env.out.iterdir() if p.is_file()
               and p.name != "batch_manifest.json"}
 
     record = only(env.run())
 
     assert record["status"] == "skipped"
-    assert "identical run identity" in record["reason"] or "unchanged" in record["reason"]
+    assert record["reason"] == "unchanged: identical run identity"
+    assert record["skip_check"] == "identical run identity"
+    assert json.loads((env.out / "a_publish.json").read_bytes())["run_identity"]["skip_reusable"] is True
     assert env.snapshot(env.out) == before
     assert {p.name: p.stat().st_mtime_ns for p in env.out.iterdir() if p.is_file()
             and p.name != "batch_manifest.json"} == mtimes
     assert len(env.converter.calls) == 1
     assert env.state.builds == 1
 
 
 def test_skip_existing_never_skips_a_failed_audit(env):
     env.state.status = "error"
     assert only(env.run())["status"] == "audit_error"
@@ -104,42 +111,140 @@ def test_a_file_without_a_manifest_is_not_skipped(env):
     (env.out / "a_publish.json").unlink()
     record = only(env.run())
     assert record["status"] == "ok"
     assert record["skip_check"] == "no publish manifest"
 
 
 def test_force_overrides_skip_existing_and_reconverts(env):
     env.run()
     record = only(env.run(force_reconvert=True))
     assert record["status"] == "ok"
+    assert record["skip_check"] == "--force given"
     assert len(env.converter.calls) == 2
 
 
+class FalseySource(ProvisionalSource):
+    def __bool__(self):
+        return False
+
+
+class FalseyProvider:
+    def __bool__(self):
+        return False
+
+    def __call__(self, packet):
+        return {"ambiguous": True}
+
+    def __str__(self):
+        raise AssertionError("provider must not be serialized")
+
+
+@pytest.mark.parametrize("context", [
+    "source", "falsey_source", "scope", "empty_scope", "empty_entries",
+    "empty_generator", "generator", "provider", "falsey_provider",
+])
+def test_context_publication_cannot_be_reused_by_later_contextless_batch(
+    tmp_path, monkeypatch, pdf_factory, converter, context,
+):
+    pdf = pdf_factory(tmp_path / "in")
+    out = tmp_path / "out"
+    document = fixture_document(
+        [CS_HEADER, _merged("FIRST YEAR", 8), _cs_semester_row(),
+         _cs_row(("CS 1", "Discrete Structures", "3", ""),
+                 ("CS 2", "Discrete Structures 2", "3", "CS 1"))],
+        [("title", "BACHELOR OF SCIENCE IN COMPUTER SCIENCE PROGRAM")],
+    )
+    monkeypatch.setattr(loader, "evidence_adapter", lambda *args: document)
+    monkeypatch.setattr(loader, "get_shared_converter", lambda *a, **k: converter)
+    contexts = {
+        "source": {"source": ProvisionalSource(identity.file_sha256(pdf), "local/a.pdf")},
+        "falsey_source": {"source": FalseySource(identity.file_sha256(pdf), "local/a.pdf")},
+        "scope": {"approved_scope": {"program_name": "Computer Science"}},
+        "empty_scope": {"approved_scope": {}},
+        "empty_entries": {"review_entries": []},
+        "empty_generator": {"review_entries": (entry for entry in [])},
+        "generator": {"review_entries": (entry for entry in [{}])},
+        "provider": {"repair_provider": lambda packet: {"ambiguous": True}},
+        "falsey_provider": {"repair_provider": FalseyProvider()},
+    }
+    payload = pipeline.process_prospectus(
+        pdf, output_path=out / "a_prospectus.json", semantic_doc_path=None,
+        converter=converter, quiet=True, **contexts[context],
+    )
+    assert payload["audit"]["status"] in ("ok", "warn")
+    assert payload["content_review"] == "pending"
+    assert payload["source_verification"] == "pending"
+    assert payload["authority"]["eligibility_executable"] is False
+    if context == "generator":
+        assert payload["authority"]["content_review_detail"]["entries"] == 1
+    manifest = publish.read_manifest(out / "a_publish.json")
+    assert publish.verify_published(out, manifest) == (True, "all files match")
+    config = BatchConfig(input_root=pdf.parent, output_root=out, semantic_doc=None,
+                         skip_existing=True, write_csv=False, write_pl=False,
+                         write_jsonl=False, write_md=False)
+    item = batch.build_batch_items([pdf], config)[0]
+    assert batch.skip_check(item, config, identity.package_sha256()) == (
+        False, "previous run used supplied context",
+    )
+    assert payload["run_identity"]["skip_reusable"] is False
+    assert manifest["run_identity"]["skip_reusable"] is False
+    assert payload["run_identity"]["run_key"] == identity.run_identity(pdf, None)["run_key"]
+    record = only(run_batch(config))
+    assert record["status"] in ("ok", "warn")
+    assert record["skip_check"] == "previous run used supplied context"
+    assert len(converter.calls) == 1  # reparsing may still reuse the verified conversion cache
+    assert only(run_batch(config))["status"] == "skipped"
+
+
+@pytest.mark.parametrize("value", ["missing", None, 0, 1, "true", "false", [], {}])
+def test_missing_or_nonboolean_skip_eligibility_fails_closed(env, value):
+    env.run()
+    path = env.out / "a_publish.json"
+    manifest = json.loads(path.read_bytes())
+    run_id = manifest["run_identity"]
+    if value == "missing":
+        run_id.pop("skip_reusable", None)
+    else:
+        run_id["skip_reusable"] = value
+    main_path = env.out / "a_prospectus.json"
+    payload = json.loads(main_path.read_bytes())
+    payload["run_identity"] = run_id
+    main_path.write_bytes(json.dumps(payload).encode("utf-8"))
+    manifest["files"][main_path.name] = identity.file_sha256(main_path)
+    path.write_bytes(json.dumps(manifest).encode("utf-8"))
+    assert publish.verify_published(env.out, manifest) == (True, "all files match")
+    record = only(env.run())
+    assert record["status"] == "ok"
+    assert record["skip_check"] == "previous run skip eligibility is unknown"
+    assert env.state.builds == 2
+
+
 def test_error_record_points_at_the_diagnostics_and_keeps_earlier_files(env):
     env.run()
     before = env.snapshot(env.out)
     env.pdf.write_bytes(b"%PDF-two")
     env.converter.fail = True
 
     record = only(env.run())
 
     assert record["status"] == "error"
     assert record["error_type"] == "RuntimeError"
     assert record["failed_dir"].endswith("failed" + __import__("os").sep + "a")
     assert env.snapshot(env.out) == before
 
 
 def test_scan_ignores_the_failed_diagnostics_folder(tmp_path):
     root = tmp_path / "in"
     (root / "failed" / "a").mkdir(parents=True)
     (root / "keep_docling.json").write_text("{}", encoding="utf-8")
     (root / "failed" / "a" / "a_docling.json").write_text("{}", encoding="utf-8")
+    (root / "failed" / "a" / "failure.json").write_text("{}", encoding="utf-8")
     found = batch.scan_inputs(root, patterns=["*.json"])
     assert [p.name for p in found] == ["keep_docling.json"]
 
 
 # --- Phase B markup twin (Task 1 note: a missing _prospectus.md must be regenerated)
 
 
 def test_a_markup_twin_requested_now_but_missing_from_the_last_run_is_not_skipped(env):
     env.run(write_md=False)
     record = only(env.run())  # write_md defaults to True
@@ -172,14 +277,242 @@ def test_single_file_cli_reconverts_only_with_force(monkeypatch, tmp_path):
 
     seen = []
     monkeypatch.setattr(cli, "process_prospectus", lambda *a, **k: seen.append(k) or {"audit": {"status": "ok"}})
     pdf = tmp_path / "a.pdf"
     pdf.write_bytes(b"%PDF-one")
     assert cli.main(["-i", str(pdf)]) == 0
     assert cli.main(["-i", str(pdf), "--force"]) == 0
     assert [call["force_reconvert"] for call in seen] == [False, True]
 
 
+@pytest.mark.parametrize("force", [False, True])
+def test_tui_configuration_changes_and_displays_force_setting(monkeypatch, capsys, force):
+    app = tui.ProspectusTUI()
+    app.config.force_reconvert = not force
+    monkeypatch.setattr(tui, "RICH_AVAILABLE", False)
+    monkeypatch.setattr(tui, "ask_text", lambda prompt, default="": default)
+    monkeypatch.setattr(tui, "ask_yes_no", lambda prompt, default=True:
+                        force if prompt.startswith("Force reconversion") else default)
+    monkeypatch.setattr(app, "pause", lambda *args: None)
+
+    app.configure()
+
+    assert app.config.force_reconvert is force
+    app.show_config()
+    assert f"Force reconversion: {force}" in capsys.readouterr().out
+
+
+@pytest.mark.parametrize("force", [False, True])
+def test_tui_single_file_passes_force_to_actual_pipeline(env, monkeypatch, force):
+    env.run()
+    app = tui.ProspectusTUI()
+    app.config.force_reconvert = force
+    app.config.device = "cpu"
+    app.config.semantic_doc = None
+    app.config.write_pl = False
+    app.config.write_jsonl = False
+    calls, payloads, messages = [], [], []
+
+    def process(path, **kwargs):
+        calls.append((path, kwargs))
+        payload = pipeline.process_prospectus(
+            path, output_path=env.out / "a_prospectus.json", quiet=True, **kwargs,
+        )
+        payloads.append(payload)
+        return payload
+
+    monkeypatch.setattr(app, "_pick_file", lambda: env.pdf)
+    monkeypatch.setattr(app, "pause", lambda message="": messages.append(message))
+    monkeypatch.setattr(tui, "process_prospectus", process)
+
+    app.single_file()
+
+    assert calls == [(env.pdf, {
+        "export_pl": False, "export_jsonl": False, "export_csv": True, "export_md": True,
+        "device": "cpu", "semantic_doc_path": None, "force_reconvert": force,
+    })]
+    assert messages == ["Extracted 0 courses (OK)."]
+    assert payloads[0]["run_identity"]["cache"] == ("converted" if force else "reused")
+    assert len(env.converter.calls) == (2 if force else 1)
+    assert env.state.builds == 2
+
+
+@pytest.mark.parametrize("force", [False, True])
+def test_tui_batch_force_takes_precedence_over_skip(env, monkeypatch, force):
+    env.run()
+    app = tui.ProspectusTUI()
+    app.config = BatchConfig(input_root=env.pdf.parent, output_root=env.out, semantic_doc=None,
+                             skip_existing=True, force_reconvert=force)
+    app.last_scan = [env.pdf]
+    monkeypatch.setattr(tui, "ask_yes_no", lambda *args, **kwargs: True)
+    monkeypatch.setattr(app, "pause", lambda *args: None)
+
+    app.run_batch_interactive()
+
+    record = json.loads((env.out / "batch_manifest.json").read_bytes())["records"][0]
+    assert record["status"] == ("ok" if force else "skipped")
+    assert record["skip_check"] == ("--force given" if force else "identical run identity")
+    assert len(env.converter.calls) == (2 if force else 1)
+    assert env.state.builds == (2 if force else 1)
+
+
 def test_batch_manifest_schema_names_the_new_record_shape():
     from backend.bintanong_tools.prospectus_extractor import common
 
     assert common.MANIFEST_SCHEMA_VERSION == "palsu-prospectus-batch-manifest-v3.1"
+
+
+def test_batch_manifest_writes_utf8_lf_without_changing_content(tmp_path):
+    records = [{"status": status, "program": "Sining at kultura – ñ"}
+               for status in ("ok", "warn", "audit_error", "skipped", "error")]
+    before = datetime.now().replace(microsecond=0)
+
+    path = batch.write_manifest(records, tmp_path / "out")
+
+    raw = path.read_bytes()
+    assert b"\n" in raw and b"\r" not in raw
+    assert "Sining at kultura – ñ".encode("utf-8") in raw
+    payload = json.loads(raw)
+    assert path == tmp_path / "out" / "batch_manifest.json"
+    assert set(payload) == {"schema_version", "generated_at", "summary", "records"}
+    assert payload["schema_version"] == "palsu-prospectus-batch-manifest-v3.1"
+    assert before <= datetime.fromisoformat(payload["generated_at"]) <= datetime.now()
+    assert payload["summary"] == {
+        "total": 5, "ok": 1, "warn": 1, "audit_failed": 1, "skipped": 1, "failed": 1,
+    }
+    assert payload["records"] == records
+
+
+@pytest.mark.parametrize("name", ["a_docling.json", "a_docling.meta.json"])
+@pytest.mark.parametrize("deleted", [False, True])
+def test_changed_or_missing_cache_refuses_skip(env, name, deleted):
+    env.run()
+    path = env.out / name
+    if deleted:
+        path.unlink()
+    else:
+        path.write_bytes(b"{}")
+    record = only(env.run())
+    assert record["status"] == "ok"
+    assert record["skip_check"] == (f"{name} is missing" if deleted
+                                     else f"{name} changed since it was published")
+    assert len(env.converter.calls) == 2
+
+
+def test_old_v1_manifest_refuses_skip(env):
+    import json
+    env.run()
+    path = env.out / "a_publish.json"
+    old = json.loads(path.read_bytes())
+    old["schema"] = "palsu-prospectus-publish-v1"
+    path.write_text(json.dumps(old), encoding="utf-8")
+    record = only(env.run())
+    assert record["status"] == "ok"
+    assert record["skip_check"] == "no publish manifest"
+    assert env.state.builds == 2
+
+
+@pytest.mark.parametrize("ancestor", ["failed", "FAILED", ".venv", "node_modules"])
+def test_scan_keeps_inputs_below_ignored_looking_absolute_ancestors(tmp_path, ancestor):
+    root = tmp_path / ancestor / "inputs"
+    root.mkdir(parents=True)
+    pdf = root / "failed.pdf"
+    pdf.write_bytes(b"%PDF-input")
+    assert batch.scan_inputs(root) == [pdf]
+    assert batch.scan_pdfs(root) == [pdf]
+
+
+@pytest.mark.parametrize("recursive", [False, True])
+def test_scan_keeps_failed_inputs_and_honors_requested_patterns(tmp_path, recursive):
+    root = tmp_path / "inputs"
+    legitimate = root / "courses" / "failed"
+    legitimate.mkdir(parents=True)
+    for relative in ["failed.pdf", "keep_docling.json", "courses/failed/course.pdf",
+                     "courses/failed/course_docling.json"]:
+        (root / relative).write_bytes(b"input")
+    # A filename that matches an ignored directory name is still a requested input.
+    (root / ".git").write_bytes(b"input")
+    assert [p.relative_to(root).as_posix() for p in batch.scan_inputs(root, recursive)] == (
+        ["courses/failed/course.pdf", "failed.pdf"] if recursive else ["failed.pdf"]
+    )
+    assert [p.relative_to(root).as_posix() for p in batch.scan_inputs(
+        root, recursive, patterns=["*.json", ".git", "*.json"]
+    )] == ([".git", "courses/failed/course_docling.json", "keep_docling.json"]
+          if recursive else [".git", "keep_docling.json"])
+
+
+@pytest.mark.parametrize("failed_name", ["failed", "FAILED"])
+def test_scan_excludes_only_marked_failure_runs_and_their_descendants(tmp_path, failed_name):
+    root = tmp_path / "inputs"
+    diagnostic = root / "results" / failed_name / "diagnosed"
+    sibling = diagnostic.parent / "legitimate"
+    (diagnostic / "nested").mkdir(parents=True)
+    sibling.mkdir()
+    (diagnostic / "failure.json").write_text("{}", encoding="utf-8")
+    for folder in [diagnostic, diagnostic / "nested", sibling]:
+        (folder / "course.pdf").write_bytes(b"%PDF-input")
+        (folder / "course_docling.json").write_text("{}", encoding="utf-8")
+    (diagnostic.parent / "direct.pdf").write_bytes(b"%PDF-input")
+    (diagnostic.parent / "direct_docling.json").write_text("{}", encoding="utf-8")
+    assert batch.scan_inputs(root) == [diagnostic.parent / "direct.pdf", sibling / "course.pdf"]
+    assert batch.scan_inputs(root, patterns=["*.json"]) == [
+        diagnostic.parent / "direct_docling.json", sibling / "course_docling.json"]
+    assert batch.scan_inputs(root, recursive=False, patterns=["*.pdf", "*.json"]) == []
+
+
+@pytest.mark.parametrize("ignored", ["palsu_jsonified_output", "docling_jsonified_output",
+                                      ".venv", ".docling-venv", "__pycache__", ".git", "node_modules"])
+def test_scan_still_ignores_standard_root_relative_directories(tmp_path, ignored):
+    root = tmp_path / "inputs"
+    (root / "courses" / ignored / "nested").mkdir(parents=True)
+    keep = root / "keep.pdf"
+    keep.write_bytes(b"%PDF-input")
+    (root / "courses" / ignored / "nested" / "drop.pdf").write_bytes(b"%PDF-input")
+    assert batch.scan_inputs(root) == [keep]
+
+
+@pytest.mark.parametrize("selected", ["failed", "failed/diagnosed", "archive"])
+def test_scan_honors_diagnostic_markers_within_the_selected_root(tmp_path, selected):
+    output = tmp_path / "output"
+    diagnostic = output / "failed" / "diagnosed"
+    sibling = output / "failed" / "legitimate"
+    archive = output / "archive"
+    for folder in [diagnostic / "nested", sibling, archive / "nested"]:
+        folder.mkdir(parents=True)
+        (folder / "course.pdf").write_bytes(b"%PDF-input")
+        (folder / "course_docling.json").write_text("{}", encoding="utf-8")
+    (diagnostic / "failure.json").write_text("{}", encoding="utf-8")
+    (archive / "failure.json").write_text("{}", encoding="utf-8")
+    # Above-root markers must not classify the selected legitimate tree as diagnostics.
+    (output / "failure.json").write_text("{}", encoding="utf-8")
+    root = output / selected
+    expected = [sibling / "course.pdf", sibling / "course_docling.json"] if selected == "failed" else []
+    assert batch.scan_inputs(root, patterns=["*.pdf", "*.json"]) == sorted(expected)
+    assert batch.scan_inputs(sibling, patterns=["*.pdf", "*.json"]) == [
+        sibling / "course.pdf", sibling / "course_docling.json"]
+    assert batch.scan_inputs(root, recursive=False, patterns=["*.pdf", "*.json"]) == []
+
+
+@pytest.mark.parametrize("recursive", [False, True])
+@pytest.mark.parametrize("pattern", ["../*.pdf", "nested/../../*.pdf", r"..\*.pdf",
+                                      r"nested\..\..\*.pdf", "/outside/*.pdf",
+                                      r"\outside\*.pdf", "C:*.pdf", "C:/outside/*.pdf",
+                                      r"\\server\share\*.pdf"])
+def test_scan_rejects_patterns_that_can_leave_the_selected_root(tmp_path, recursive, pattern):
+    root = tmp_path / "inputs"
+    (root / "nested").mkdir(parents=True)
+    (tmp_path / "course.pdf").write_bytes(b"%PDF-outside")
+    for above_root_marker in [False, True]:
+        if above_root_marker:
+            (tmp_path / "failure.json").write_text("{}", encoding="utf-8")
+        with pytest.raises(ValueError, match="Input pattern must stay within input root"):
+            batch.scan_inputs(root, recursive=recursive, patterns=[pattern])
+
+
+@pytest.mark.parametrize("recursive", [False, True])
+@pytest.mark.parametrize("pattern", ["nested/*.pdf", "n*/*.pdf", "**/*.pdf"])
+def test_scan_preserves_valid_relative_globs(tmp_path, recursive, pattern):
+    root = tmp_path / "inputs"
+    (root / "nested").mkdir(parents=True)
+    keep = root / "nested" / "course.pdf"
+    keep.write_bytes(b"%PDF-input")
+    assert batch.scan_inputs(root, recursive=recursive, patterns=[pattern]) == [keep]
diff --git a/tests/test_prospectus_cache.py b/tests/test_prospectus_cache.py
index 8d457da..6f18436 100644
--- a/tests/test_prospectus_cache.py
+++ b/tests/test_prospectus_cache.py
@@ -85,22 +85,23 @@ def test_changed_cell_matching_setting_invalidates_the_cache(
     process(pdf, out, converter, force_reconvert=False)
     assert len(converter.calls) == 2
 
 
 def test_born_digital_cache_is_never_reused_for_an_ocr_run(
     tmp_path, monkeypatch, pdf_factory, converter, process
 ):
     pdf = pdf_factory(tmp_path / "in")
     out = tmp_path / "out"
     process(pdf, out, converter, force_reconvert=False)
-    monkeypatch.setattr(loader, "conversion_settings",
-                        lambda: identity.conversion_settings(do_ocr=True, ocr_languages=["en", "fil"]))
+    ocr_settings = identity.conversion_settings(do_ocr=True, ocr_languages=["en", "fil"])
+    monkeypatch.setattr(loader, "conversion_settings", lambda: ocr_settings)
+    monkeypatch.setattr(identity, "conversion_settings", lambda: ocr_settings)
     process(pdf, out, converter, force_reconvert=False)
     assert len(converter.calls) == 2
     meta = json.loads((out / "a_docling.meta.json").read_text(encoding="utf-8"))
     assert meta["conversion_settings"]["do_ocr"] is True
 
 
 def test_cache_record_names_the_pdf_and_the_json_it_guards(tmp_path, pdf_factory, converter, process):
     import hashlib
 
     pdf = pdf_factory(tmp_path / "in")
@@ -199,20 +200,22 @@ def test_interleaved_writers_to_one_target_do_not_share_a_temp_file(tmp_path, mo
         sources.append(Path(src))
         if len(sources) == 1:  # writer A paused between its write and its replace; writer B runs fully
             loader._write_bytes_atomic(target, b"B")
         return real_replace(src, dst)
 
     monkeypatch.setattr(os, "replace", replace)
     loader._write_bytes_atomic(target, b"A")
     assert target.read_bytes() == b"A"
     assert len(sources) == 2 and sources[0] != sources[1]
     assert all(source.parent == target.parent for source in sources)
+    assert all(source.name.startswith(".t-") and source.name.endswith(".tmp")
+               and len(source.name) == 15 for source in sources)
     assert sorted(path.name for path in target.parent.iterdir()) == ["a_docling.json"]
 
 
 def test_a_briefly_locked_target_is_retried(tmp_path, monkeypatch):
     import time
 
     target = tmp_path / "a_docling.json"
     real_replace = os.replace
     failures = []
 
@@ -227,30 +230,72 @@ def test_a_briefly_locked_target_is_retried(tmp_path, monkeypatch):
     loader._write_bytes_atomic(target, b"new")
     assert target.read_bytes() == b"new"
     assert len(failures) == 2
 
 
 def test_a_target_that_stays_locked_raises_a_clean_error_and_leaves_no_temp(tmp_path, monkeypatch):
     import time
 
     target = tmp_path / "a_docling.json"
     target.write_bytes(b"old")
+    sources = []
 
     def replace(src, dst):
+        sources.append(Path(src))
         raise PermissionError(13, "The process cannot access the file", str(dst))
 
     monkeypatch.setattr(os, "replace", replace)
     monkeypatch.setattr(time, "sleep", lambda _seconds: None)
     with pytest.raises(loader.ReplaceFailed, match="could not replace .*a_docling.json"):
         loader._write_bytes_atomic(target, b"new")
     assert target.read_bytes() == b"old"
     assert sorted(path.name for path in tmp_path.iterdir()) == ["a_docling.json"]
+    assert len(set(sources)) == 1 and len(sources) == 5
+    assert sources[0].name.startswith(".t-") and len(sources[0].name) == 15
+
+
+def test_atomic_write_failure_preserves_old_bytes_and_removes_short_temp(tmp_path, monkeypatch):
+    target = tmp_path / "a_docling.json"
+    target.write_bytes(b"old")
+    sources = []
+    real_fdopen = os.fdopen
+
+    def fail_write(handle, mode):
+        stream = real_fdopen(handle, mode)
+
+        class InterruptedWrite:
+            def __enter__(self):
+                return self
+
+            def write(self, data):
+                stream.write(data[:1])
+                raise OSError("interrupted write")
+
+            def __exit__(self, *args):
+                stream.close()
+
+        return InterruptedWrite()
+
+    real_mkstemp = loader.tempfile.mkstemp
+
+    def mkstemp(**kwargs):
+        handle, name = real_mkstemp(**kwargs)
+        sources.append(Path(name))
+        return handle, name
+
+    monkeypatch.setattr(os, "fdopen", fail_write)
+    monkeypatch.setattr(loader.tempfile, "mkstemp", mkstemp)
+    with pytest.raises(OSError, match="interrupted write"):
+        loader._write_bytes_atomic(target, b"new")
+    assert target.read_bytes() == b"old"
+    assert list(tmp_path.iterdir()) == [target]
+    assert sources[0].name.startswith(".t-") and len(sources[0].name) == 15
 
 
 # --- D-3: the bytes whose digest was checked are the bytes that are parsed.
 
 
 def _load(pdf, raw_path, active_converter):
     document, _path = loader.load_document(
         pdf, force_reconvert=False, converter=active_converter, raw_json_path=raw_path)
     return document
 
diff --git a/tests/test_prospectus_input_snapshot.py b/tests/test_prospectus_input_snapshot.py
new file mode 100644
index 0000000..db93c27
--- /dev/null
+++ b/tests/test_prospectus_input_snapshot.py
@@ -0,0 +1,223 @@
+"""One captured input supplies conversion, identity, and publication checks."""
+
+from dataclasses import FrozenInstanceError
+import hashlib
+import json
+import os
+from pathlib import Path
+from types import SimpleNamespace
+
+import pytest
+
+from backend.bintanong_tools import prospectus
+from backend.bintanong_tools.prospectus_extractor import batch, identity, loader, pipeline
+from conftest import FakeDoc, RAW_BASE
+
+pytestmark = pytest.mark.usefixtures("fake_docling", "pipeline_state")
+
+
+def converted(source):
+    body = source.stream.read() if hasattr(source, "stream") else Path(source).read_bytes()
+    return SimpleNamespace(errors=[], document=FakeDoc({**RAW_BASE, "marker": body.decode("latin-1")}))
+
+
+def test_same_size_restored_mtime_change_during_conversion_preserves_publication(
+    tmp_path, pdf_factory, converter, process, snapshot
+):
+    pdf = pdf_factory(tmp_path / "in")
+    out = tmp_path / "out"
+    process(pdf, out, converter)
+    before = snapshot(out)
+    original_stat = pdf.stat()
+
+    def mutate(source):
+        result = converted(source)
+        pdf.write_bytes(b"%PDF-two")
+        os.utime(pdf, ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns))
+        return result
+
+    with pytest.raises(ValueError, match="Input bytes changed"):
+        process(pdf, out, SimpleNamespace(convert=mutate), force_reconvert=True)
+    assert snapshot(out) == before
+    assert (out / "failed" / "a" / "failure.json").is_file()
+
+
+def test_standalone_loader_refuses_changed_source_before_overwriting_cache(
+    tmp_path, pdf_factory, converter
+):
+    pdf = pdf_factory(tmp_path / "in")
+    raw = tmp_path / "out" / "a_docling.json"
+    loader.load_document(pdf, converter=converter, raw_json_path=raw)
+    meta = loader._cache_meta_path(raw)
+    before = (raw.read_bytes(), meta.read_bytes())
+
+    def mutate(source):
+        result = converted(source)
+        pdf.write_bytes(b"%PDF-two")
+        return result
+
+    with pytest.raises(ValueError, match="Input bytes changed"):
+        loader.load_document(pdf, converter=SimpleNamespace(convert=mutate), raw_json_path=raw)
+    assert (raw.read_bytes(), meta.read_bytes()) == before
+
+
+def test_conversion_uses_capture_even_when_original_changes_before_conversion(tmp_path, pdf_factory):
+    pdf = pdf_factory(tmp_path)
+    captured = identity.InputSnapshot(pdf)
+    pdf.write_bytes(b"%PDF-two")
+    loaded = loader.load_document_result(
+        pdf, converter=SimpleNamespace(convert=converted), snapshot=captured, stage_dir=tmp_path / "stage",
+    )
+    assert loaded.document.docling_document.raw["marker"] == "%PDF-one"
+    assert loaded.raw_json_sha256 == hashlib.sha256(loaded.raw_json_bytes).hexdigest()
+
+
+def test_snapshot_cannot_be_reassigned_or_attached_to_another_path(tmp_path, pdf_factory):
+    pdf = pdf_factory(tmp_path)
+    captured = identity.InputSnapshot(pdf)
+    with pytest.raises(FrozenInstanceError):
+        captured.data = b"other"
+    other = pdf_factory(tmp_path, name="other.pdf")
+    with pytest.raises(ValueError, match="Snapshot path"):
+        loader.load_document_result(other, snapshot=captured)
+
+
+def test_one_input_digest_supplies_source_run_and_cache_identity(
+    tmp_path, monkeypatch, pdf_factory, converter, process
+):
+    pdf = pdf_factory(tmp_path / "in")
+    digested = []
+    real_digest = identity.bytes_sha256
+
+    def digest(body):
+        if body == b"%PDF-one":
+            digested.append(body)
+        return real_digest(body)
+
+    monkeypatch.setattr(identity, "bytes_sha256", digest)
+    source = prospectus.ProvisionalSource(hashlib.sha256(b"%PDF-one").hexdigest(), "local/a.pdf")
+    payload = process(pdf, tmp_path / "out", converter, source=source)
+    assert payload["run_identity"]["pdf_sha256"] == source.pdf_sha256
+    assert digested == [b"%PDF-one"]
+
+
+def test_reused_cache_result_retains_exact_parsed_json_and_meta_bytes(
+    tmp_path, monkeypatch, pdf_factory, converter
+):
+    pdf = pdf_factory(tmp_path / "in")
+    raw = tmp_path / "out" / "a_docling.json"
+    first = loader.load_document(pdf, converter=converter, raw_json_path=raw)
+    assert len(first) == 2  # public callers still unpack document and path
+    raw_bytes = raw.read_bytes()
+    meta_path = loader._cache_meta_path(raw)
+    meta_bytes = meta_path.read_bytes()
+    real_read = Path.read_bytes
+
+    def read(path):
+        body = real_read(path)
+        if path == raw:
+            path.write_bytes(b'{"marker": "other"}')
+        elif path == meta_path:
+            path.write_bytes(b'{}')
+        return body
+
+    monkeypatch.setattr(Path, "read_bytes", read)
+    loaded = loader.load_document_result(pdf, force_reconvert=False, converter=converter, raw_json_path=raw)
+    assert loaded.document.docling_document.raw["marker"] == "%PDF-one"
+    assert loaded.cache_status == "reused"
+    assert loaded.raw_json_bytes == raw_bytes
+    assert loaded.meta_bytes == meta_bytes
+    assert loaded.raw_json_sha256 == hashlib.sha256(raw_bytes).hexdigest()
+    assert loaded.meta_sha256 == hashlib.sha256(meta_bytes).hexdigest()
+    assert len(converter.calls) == 1
+
+
+def test_backend_retry_receives_a_fresh_capture_stream_with_original_filename(tmp_path, monkeypatch, pdf_factory):
+    pdf = pdf_factory(tmp_path, name="original filename.pdf")
+    sources = []
+
+    def primary(source):
+        sources.append(source)
+        assert source.stream.read() == b"%PDF-one"
+        return SimpleNamespace(errors=["std::bad_alloc"], document=None)
+
+    def fallback(source):
+        sources.append(source)
+        return converted(source)
+
+    monkeypatch.setattr(loader, "get_shared_converter", lambda **kwargs: SimpleNamespace(convert=fallback))
+    document, _ = loader.load_document(pdf, converter=SimpleNamespace(convert=primary))
+    assert document.docling_document.raw["marker"] == "%PDF-one"
+    assert [source.name for source in sources] == [pdf.name, pdf.name]
+    assert sources[0].stream is not sources[1].stream
+
+
+def test_json_input_is_parsed_from_the_same_capture_used_for_identity(tmp_path):
+    raw = tmp_path / "review.json"
+    raw.write_bytes(json.dumps({**RAW_BASE, "marker": "original"}).encode())
+    captured = identity.InputSnapshot(raw)
+    raw.write_bytes(b'{}')
+    loaded = loader.load_document_result(raw, snapshot=captured)
+    run = identity.run_identity(raw, None, snapshot=captured)
+    assert loaded.document.docling_document.raw["marker"] == "original"
+    assert run["input_sha256"] == captured.sha256
+    assert run["review_input_only"] is True
+
+
+def test_batch_captures_one_item_at_a_time_and_reuses_skip_identity(
+    tmp_path, monkeypatch, pdf_factory, converter
+):
+    root = tmp_path / "in"
+    first = pdf_factory(root)
+    second = pdf_factory(root, name="b.pdf", body=b"%PDF-two")
+    out = tmp_path / "out"
+    config = batch.BatchConfig(input_root=root, output_root=out, semantic_doc=None,
+                               skip_existing=True, write_md=False)
+    monkeypatch.setattr(loader, "get_shared_converter", lambda **kwargs: converter)
+    assert batch.run_batch(config)["succeeded"] == 2
+    reads = []
+    real_read = Path.read_bytes
+
+    def read(path):
+        if path in (first, second):
+            reads.append(path.name)
+        return real_read(path)
+
+    monkeypatch.setattr(Path, "read_bytes", read)
+    (out / "a_publish.json").unlink()
+    result = batch.run_batch(config)
+    assert result["succeeded"] == 1 and result["skipped"] == 1
+    assert reads == ["a.pdf", "a.pdf", "b.pdf"]  # capture, prepublish check, next capture
+
+
+def test_batch_cache_reparse_does_not_initialize_a_converter(tmp_path, monkeypatch, pdf_factory, converter):
+    root = tmp_path / "in"
+    pdf_factory(root)
+    out = tmp_path / "out"
+    config = batch.BatchConfig(input_root=root, output_root=out, semantic_doc=None, write_md=False)
+    monkeypatch.setattr(loader, "get_shared_converter", lambda **kwargs: converter)
+    assert batch.run_batch(config)["succeeded"] == 1
+
+    def unexpected(**kwargs):
+        raise AssertionError("cache reparse initialized a converter")
+
+    monkeypatch.setattr(loader, "get_shared_converter", unexpected)
+    assert batch.run_batch(config)["succeeded"] == 1
+
+
+def test_batch_processes_a_captured_item_when_skip_check_is_unreadable(
+    tmp_path, monkeypatch, pdf_factory, converter
+):
+    root = tmp_path / "in"
+    pdf_factory(root)
+    config = batch.BatchConfig(input_root=root, output_root=tmp_path / "out",
+                               semantic_doc=None, skip_existing=True, write_md=False)
+    monkeypatch.setattr(loader, "get_shared_converter", lambda **kwargs: converter)
+
+    def unreadable(*args, **kwargs):
+        raise OSError("manifest temporarily unreadable")
+
+    monkeypatch.setattr(batch, "skip_check", unreadable)
+    result = batch.run_batch(config)
+    assert result["succeeded"] == 1
+    assert result["records"][0]["skip_check"] == "identity check failed: OSError: manifest temporarily unreadable"
diff --git a/tests/test_prospectus_markup.py b/tests/test_prospectus_markup.py
index e025efa..dad67da 100644
--- a/tests/test_prospectus_markup.py
+++ b/tests/test_prospectus_markup.py
@@ -407,21 +407,23 @@ def test_single_origin_without_page_height_is_not_flagged_approximate():
 
 from backend.bintanong_tools.prospectus_extractor import batch, cli, pipeline  # noqa: E402
 
 
 def _fake_run(tmp_path, monkeypatch, status="error", **flags):
     source = tmp_path / "x_docling.json"
     source.write_text("{}", encoding="utf-8")
     document = evidence(
         [banner_table()], [text_item(0, "section_header", "PROPOSED PROGRAM OF STUDY")]
     )
-    monkeypatch.setattr(pipeline, "load_document", lambda *args, **kwargs: (document, None))
+    from backend.bintanong_tools.prospectus_extractor.loader import DocumentLoadResult
+    monkeypatch.setattr(pipeline, "load_document_result",
+                        lambda *args, **kwargs: DocumentLoadResult(document, None, "not-applicable"))
     monkeypatch.setattr(pipeline, "build_payload", lambda *args, **kwargs: {"audit": {"status": status}})
     target = tmp_path / "out" / "x_prospectus.json"
     pipeline.process_prospectus(source, target, quiet=True, **flags)
     return target
 
 
 def test_export_md_writes_the_twin_beside_the_json_even_when_the_audit_failed(tmp_path, monkeypatch):
     target = _fake_run(tmp_path, monkeypatch, status="error", export_md=True)
     twin = target.with_name("x_prospectus.md")
     text = twin.read_text(encoding="utf-8")
@@ -474,22 +476,20 @@ def test_batch_defaults_to_writing_md_and_passes_it_on(monkeypatch, tmp_path):
     source.mkdir()
     (source / "a.pdf").write_bytes(b"%PDF-test")
     seen = []
     result = {
         "audit": {
             "status": "ok", "total_courses": 0, "computed_total_units": 0,
             "declared_total_units": None, "years_detected": [], "errors": [], "warnings": [],
         },
         "metadata": {},
     }
-    monkeypatch.setattr(batch, "ensure_docling_env", lambda: None)
-    monkeypatch.setattr(batch, "get_shared_converter", lambda **kwargs: None)
     monkeypatch.setattr(batch, "process_prospectus", lambda *a, **k: seen.append(k) or result)
     config = batch.BatchConfig(input_root=source, output_root=tmp_path / "out", write_manifest=False)
     batch.run_batch(config)
     assert seen[0]["export_md"] is True
     config.write_md = False
     batch.run_batch(config)
     assert seen[1]["export_md"] is False
 
 
 # --- source fidelity: the twin shows Docling's own strings, not the parser's cleaned text ---
@@ -549,11 +549,11 @@ def test_span_beyond_the_grid_is_clamped_visibly_with_the_declared_spans():
     assert "data-span-clamped" not in fine
 
 
 def test_page_values_are_escaped_in_attributes_and_comments():
     bad = '1" onmouseover="x'
     a = dict(text_item(0, "text", "A"), page=bad, bbox=None)
     b = dict(text_item(1, "text", "B"), page="2 --> <b>", bbox=None)
     html = render_prospectus_markup(evidence([], [a, b]), OK)
     assert 'onmouseover="x' not in html and "<b>" not in html
     comment = re.search(r"<!-- page (.*?) -->\n<hr>", html).group(1)
-    assert "-->" not in comment and "<" not in comment and "--" not in comment
\ No newline at end of file
+    assert "-->" not in comment and "<" not in comment and "--" not in comment
diff --git a/tests/test_prospectus_publication.py b/tests/test_prospectus_publication.py
index ad19b4f..9466e3e 100644
--- a/tests/test_prospectus_publication.py
+++ b/tests/test_prospectus_publication.py
@@ -92,22 +92,22 @@ def test_audit_error_run_is_published_and_removes_stale_companions(
 
 def test_publication_order_puts_the_main_json_before_the_manifest(
     tmp_path, monkeypatch, pdf_factory, converter, pipeline_state, process
 ):
     order = []
     real = publish.replace_file
     monkeypatch.setattr(publish, "replace_file",
                         lambda source, target, *a, **k: (order.append(target.name), real(source, target, *a, **k)))
     pdf = pdf_factory(tmp_path / "in")
     process(pdf, tmp_path / "out", converter)
-    assert order == ["a_docling.json", "a_docling.meta.json", "a_essentials.json", "a_prospectus.pl",
-                     "a_rag.jsonl", "a_review.csv", "a_prospectus.json", "a_publish.json"]
+    assert order == ["a_essentials.json", "a_prospectus.pl", "a_rag.jsonl", "a_review.csv",
+                     "a_prospectus.json", "a_docling.json", "a_docling.meta.json", "a_publish.json"]
 
 
 def test_a_crash_between_replaces_is_detected_by_the_manifest(
     tmp_path, monkeypatch, pdf_factory, converter, pipeline_state, process, snapshot
 ):
     pdf = pdf_factory(tmp_path / "in")
     out = tmp_path / "out"
     process(pdf, out, converter)
     old_manifest = (out / "a_publish.json").read_bytes()
 
@@ -156,20 +156,24 @@ def test_docling_json_input_is_marked_as_a_review_input(
     raw = tmp_path / "in" / "a_docling.json"
     raw.parent.mkdir()
     raw.write_text(json.dumps({"texts": [{"text": "BS", "label": "text"}], "tables": []}), encoding="utf-8")
     out = tmp_path / "out"
     payload = process(raw, out, None)
 
     block = payload["run_identity"]
     assert block["input_kind"] == "docling-json"
     assert block["review_input_only"] is True
     assert block["cache"] == "not-applicable"
+    assert block["cache_files"] == {}
+    manifest = publish.read_manifest(out / "a_publish.json")
+    assert manifest["cache_files"] == {}
+    assert publish.verify_published(out, manifest) == (True, "all files match")
     assert "review input only" in block["review_note"]
     assert "a_essentials.json" not in snapshot(out)  # essentials still require a source PDF
 
 
 def test_schema_version_names_the_new_payload_shape():
     assert common.SCHEMA_VERSION == EXPECTED_SCHEMA
 
 
 def test_output_inside_the_input_folder_is_still_refused(tmp_path, pdf_factory, converter, pipeline_state):
     from backend.bintanong_tools.prospectus_extractor import pipeline
@@ -188,21 +192,22 @@ def test_markup_twin_is_published_just_before_the_main_json(
     from backend.bintanong_tools.prospectus_extractor import pipeline
 
     monkeypatch.setattr(pipeline, "render_prospectus_markup", lambda document, payload: "twin\n")
     order = []
     real = publish.replace_file
     monkeypatch.setattr(publish, "replace_file",
                         lambda source, target, *a, **k: (order.append(target.name), real(source, target, *a, **k)))
     pdf = pdf_factory(tmp_path / "in")
     out = tmp_path / "out"
     process(pdf, out, converter, export_md=True)
-    assert order[-3:] == ["a_prospectus.md", "a_prospectus.json", "a_publish.json"]
+    assert order[-5:] == ["a_prospectus.md", "a_prospectus.json", "a_docling.json",
+                          "a_docling.meta.json", "a_publish.json"]
     assert (out / "a_prospectus.md").read_bytes() == b"twin\n"
     assert "a_prospectus.md" in publish.read_manifest(out / "a_publish.json")["files"]
 
 
 def test_companions_of_an_output_set_without_a_manifest_are_removed_after_publication(
     tmp_path, pdf_factory, converter, pipeline_state
 ):
     from backend.bintanong_tools.prospectus_extractor import pipeline
 
     out = tmp_path / "out"
@@ -233,10 +238,283 @@ def test_the_b2_fixer_reads_the_pdf_hash_this_run_recorded(
     assert found["how"] == "run_identity"
     assert found["pdf_sha256"] == hashlib.sha256(b"%PDF-one").hexdigest()
 
 
 def test_outputs_are_written_with_lf_line_endings(tmp_path, pdf_factory, converter, pipeline_state, process):
     pdf = pdf_factory(tmp_path / "in")
     out = tmp_path / "out"
     process(pdf, out, converter)
     for name in ("a_prospectus.json", "a_essentials.json", "a_prospectus.pl", "a_rag.jsonl", "a_publish.json"):
         assert b"\r\n" not in (out / name).read_bytes(), name
+
+
+@pytest.mark.parametrize("reuse", [False, True])
+def test_publish_v2_binds_the_exact_loaded_cache(tmp_path, monkeypatch, pdf_factory, converter,
+                                              pipeline_state, process, reuse):
+    from backend.bintanong_tools.prospectus_extractor import pipeline
+    pdf = pdf_factory(tmp_path / "in")
+    out = tmp_path / "out"
+    if reuse:
+        process(pdf, out, converter)
+    captures = []
+    real = pipeline.load_document_result
+    def capture(*args, **kwargs):
+        loaded = real(*args, **kwargs)
+        captures.append(loaded)
+        return loaded
+    monkeypatch.setattr(pipeline, "load_document_result", capture)
+    payload = process(pdf, out, converter)
+    loaded = captures[0]
+    manifest = publish.read_manifest(out / "a_publish.json")
+    assert manifest["schema"] == "palsu-prospectus-publish-v2"
+    assert manifest["main_file"] == "a_prospectus.json"
+    assert manifest["cache_files"] == {
+        "a_docling.json": hashlib.sha256(loaded.raw_json_bytes).hexdigest(),
+        "a_docling.meta.json": hashlib.sha256(loaded.meta_bytes).hexdigest(),
+    } == payload["run_identity"]["cache_files"]
+    assert not set(manifest["files"]) & set(manifest["cache_files"])
+    assert payload["run_identity"]["cache"] == ("reused" if reuse else "converted")
+    assert len(converter.calls) == 1
+    assert publish.verify_published(out, manifest) == (True, "all files match")
+
+
+@pytest.mark.parametrize("part", ["a_docling.json", "a_docling.meta.json"])
+def test_changed_staged_cache_is_refused_before_publication(tmp_path, monkeypatch, pdf_factory,
+                                                           converter, pipeline_state, process,
+                                                           snapshot, part):
+    from backend.bintanong_tools.prospectus_extractor import pipeline
+    pdf = pdf_factory(tmp_path / "in")
+    out = tmp_path / "out"
+    process(pdf, out, converter)
+    before = snapshot(out)
+    real = pipeline._stage_outputs
+    def tamper(stage, *args, **kwargs):
+        outputs = real(stage, *args, **kwargs)
+        (stage / part).write_bytes(b"{}")
+        return outputs
+    monkeypatch.setattr(pipeline, "_stage_outputs", tamper)
+    with pytest.raises(ValueError, match="cache|changed"):
+        process(pdf, out, converter, force_reconvert=True)
+    assert snapshot(out) == before
+
+
+@pytest.mark.parametrize("mutation", ["pair", "raw", "meta", "delete-raw", "delete-meta"])
+def test_reused_cache_changes_after_parse_cannot_rebind_output(tmp_path, monkeypatch, pdf_factory,
+                                                              converter, pipeline_state, process,
+                                                              mutation):
+    from backend.bintanong_tools.prospectus_extractor import pipeline
+    pdf = pdf_factory(tmp_path / "in")
+    out = tmp_path / "out"
+    process(pdf, out, converter)
+    raw_path, meta_path = out / "a_docling.json", out / "a_docling.meta.json"
+    raw_bytes, meta_bytes = raw_path.read_bytes(), meta_path.read_bytes()
+    changed_raw = json.dumps({"texts": [], "tables": [], "marker": "never parsed"}).encode()
+    changed_meta = json.loads(meta_bytes)
+    changed_meta["raw_json_sha256"] = hashlib.sha256(changed_raw).hexdigest()
+    real = pipeline.build_payload
+    def tamper(*args, **kwargs):
+        payload = real(*args, **kwargs)
+        if mutation in ("pair", "raw"):
+            raw_path.write_bytes(changed_raw)
+        if mutation in ("pair", "meta"):
+            meta_path.write_bytes(json.dumps(changed_meta).encode())
+        if mutation == "delete-raw":
+            raw_path.unlink()
+        if mutation == "delete-meta":
+            meta_path.unlink()
+        return payload
+    monkeypatch.setattr(pipeline, "build_payload", tamper)
+    result = process(pdf, out, converter)
+    assert result["run_identity"]["cache"] == "reused"
+    assert raw_path.read_bytes() == raw_bytes
+    assert meta_path.read_bytes() == meta_bytes
+    assert result["run_identity"]["cache_files"]["a_docling.json"] == hashlib.sha256(raw_bytes).hexdigest()
+    assert publish.verify_published(out, publish.read_manifest(out / "a_publish.json"))[0]
+    assert len(converter.calls) == 1
+
+
+PUBLICATION_ORDER = ["a_essentials.json", "a_prospectus.pl", "a_rag.jsonl", "a_review.csv",
+                     "a_prospectus.md", "a_prospectus.json", "a_docling.json",
+                     "a_docling.meta.json", "a_publish.json"]
+
+
+@pytest.mark.parametrize("step", PUBLICATION_ORDER)
+@pytest.mark.parametrize("after", [False, True], ids=["before", "after"])
+@pytest.mark.parametrize("stable", [False, True], ids=["changed-companions", "identical-companions"])
+@pytest.mark.parametrize("change", ["new-pdf", "settings", "reconversion", "settings-identical-raw",
+                                     "new-pdf-identical-raw"])
+def test_interruptions_only_verify_a_coherent_generation(tmp_path, monkeypatch, pdf_factory,
+                                                         converter, pipeline_state, process,
+                                                         snapshot, step, after, stable, change):
+    from backend.bintanong_tools.prospectus_extractor import pipeline
+    monkeypatch.setattr(pipeline, "render_prospectus_markup",
+                        lambda document, payload: "twin " + str(payload["nonce"]))
+    if change.endswith("identical-raw"):
+        from conftest import FakeDoc
+        from types import SimpleNamespace
+        monkeypatch.setattr(converter, "convert", lambda stream: SimpleNamespace(
+            errors=[], document=FakeDoc({"texts": [], "tables": [], "marker": "constant"})))
+    pdf = pdf_factory(tmp_path / "in")
+    out = tmp_path / "out"
+    process(pdf, out, converter, export_md=True)
+    before = snapshot(out)
+    old = publish.read_manifest(out / "a_publish.json")
+    assert publish.verify_published(out, old)[0]
+    if stable:
+        stage_real = pipeline._stage_outputs
+        def identical_companions(stage, *args, **kwargs):
+            outputs = stage_real(stage, *args, **kwargs)
+            for name in outputs[:-1]:
+                (stage / name).write_bytes(before[name])
+            return outputs
+        monkeypatch.setattr(pipeline, "_stage_outputs", identical_companions)
+    if change.startswith("new-pdf"):
+        pdf.write_bytes(b"%PDF-two")
+    elif change.startswith("settings"):
+        monkeypatch.setenv("PALSU_DOCLING_CELL_MATCHING", "false")
+    elif change == "reconversion":
+        real_convert = converter.convert
+        def reconvert(stream):
+            result = real_convert(stream)
+            result.document.raw["marker"] = "new conversion of same PDF"
+            return result
+        monkeypatch.setattr(converter, "convert", reconvert)
+    seen = []
+    real = publish.replace_file
+    def interrupt(source, target, *args, **kwargs):
+        seen.append(target.name)
+        if target.name == step and not after:
+            raise OSError("injected interruption")
+        real(source, target, *args, **kwargs)
+        if target.name == step and after:
+            raise OSError("injected interruption")
+    monkeypatch.setattr(publish, "replace_file", interrupt)
+    with pytest.raises(OSError, match="injected interruption"):
+        process(pdf, out, converter, export_md=True, force_reconvert=True)
+    assert seen == PUBLICATION_ORDER[:PUBLICATION_ORDER.index(step) + 1]
+    current = publish.read_manifest(out / "a_publish.json")
+    valid, _ = publish.verify_published(out, current)
+    if step == "a_publish.json" and after:
+        assert valid
+        assert current["run_identity"] != old["run_identity"]
+    elif valid:
+        assert snapshot(out) == before  # every published byte belongs to the old coherent set
+    main_replaced = PUBLICATION_ORDER.index(step) > 5 or (step == "a_prospectus.json" and after)
+    if main_replaced and not (step == "a_publish.json" and after):
+        assert not valid  # main binds even byte-identical raw/companion writes to this generation
+
+
+
+def rebind_cache_for_verification(out, manifest, name, data):
+    """Give tampering honest hashes, so identity checks (not hash mismatches) catch it."""
+    (out / name).write_bytes(data)
+    manifest["cache_files"][name] = hashlib.sha256(data).hexdigest()
+    manifest["run_identity"]["cache_files"] = dict(manifest["cache_files"])
+    main_path = out / "a_prospectus.json"
+    main = json.loads(main_path.read_bytes())
+    main["run_identity"] = manifest["run_identity"]
+    main_bytes = json.dumps(main).encode()
+    main_path.write_bytes(main_bytes)
+    manifest["files"][main_path.name] = hashlib.sha256(main_bytes).hexdigest()
+
+
+@pytest.mark.parametrize("field,value", [
+    ("pdf_sha256", "f" * 64), ("conversion_identity", "f" * 64),
+    ("conversion_settings", {}), ("raw_json_sha256", "f" * 64), ("identity_version", 0),
+])
+def test_matching_hashes_do_not_hide_metadata_identity_mismatch(tmp_path, pdf_factory, converter,
+                                                               pipeline_state, process, field, value):
+    pdf = pdf_factory(tmp_path / "in")
+    out = tmp_path / "out"
+    process(pdf, out, converter)
+    manifest = publish.read_manifest(out / "a_publish.json")
+    meta = json.loads((out / "a_docling.meta.json").read_bytes())
+    meta[field] = value
+    rebind_cache_for_verification(out, manifest, "a_docling.meta.json", json.dumps(meta).encode())
+    assert publish.verify_published(out, manifest) == (
+        False, "cache metadata does not match the main run identity")
+
+
+@pytest.mark.parametrize("name", ["a_docling.json", "a_docling.meta.json"])
+@pytest.mark.parametrize("data", [b"{", b"\xff", b"[]", b"null"])
+def test_hash_matching_malformed_cache_fails_closed(tmp_path, pdf_factory, converter,
+                                                  pipeline_state, process, name, data):
+    pdf = pdf_factory(tmp_path / "in")
+    out = tmp_path / "out"
+    process(pdf, out, converter)
+    manifest = publish.read_manifest(out / "a_publish.json")
+    rebind_cache_for_verification(out, manifest, name, data)
+    assert publish.verify_published(out, manifest)[0] is False
+
+
+def test_other_valid_cache_generation_cannot_rebind_the_parsed_main(tmp_path, pdf_factory, converter,
+                                                                 pipeline_state, process):
+    pdf = pdf_factory(tmp_path / "in")
+    out = tmp_path / "out"
+    process(pdf, out, converter)
+    manifest = publish.read_manifest(out / "a_publish.json")
+    raw = json.dumps({"texts": [], "tables": [], "marker": "different generation"}).encode()
+    meta = json.loads((out / "a_docling.meta.json").read_bytes())
+    meta["raw_json_sha256"] = hashlib.sha256(raw).hexdigest()
+    for name, data in [("a_docling.json", raw), ("a_docling.meta.json", json.dumps(meta).encode())]:
+        (out / name).write_bytes(data)
+        manifest["cache_files"][name] = hashlib.sha256(data).hexdigest()
+    manifest["run_identity"]["cache_files"] = dict(manifest["cache_files"])
+    assert publish.verify_published(out, manifest) == (
+        False, "main run identity does not match the manifest")
+
+
+@pytest.mark.parametrize("part", ["raw_json_bytes", "meta_bytes", "raw_json_sha256", "meta_sha256"])
+def test_incomplete_loaded_snapshot_refuses_without_changing_published_files(tmp_path, monkeypatch,
+                                                                           pdf_factory, converter,
+                                                                           pipeline_state, process,
+                                                                           snapshot, part):
+    from dataclasses import replace
+    from backend.bintanong_tools.prospectus_extractor import pipeline
+    pdf = pdf_factory(tmp_path / "in")
+    out = tmp_path / "out"
+    process(pdf, out, converter)
+    before = snapshot(out)
+    real = pipeline.load_document_result
+    monkeypatch.setattr(pipeline, "load_document_result",
+                        lambda *args, **kwargs: replace(real(*args, **kwargs), **{part: None}))
+    with pytest.raises(ValueError, match="complete captured cache pair"):
+        process(pdf, out, converter)
+    assert snapshot(out) == before
+
+
+def test_verification_hashes_and_parses_each_files_same_read(tmp_path, monkeypatch, pdf_factory,
+                                                          converter, pipeline_state, process):
+    from pathlib import Path
+    pdf = pdf_factory(tmp_path / "in")
+    out = tmp_path / "out"
+    process(pdf, out, converter)
+    manifest = publish.read_manifest(out / "a_publish.json")
+    reads = {}
+    real = Path.read_bytes
+    def read_then_replace(path):
+        data = real(path)
+        reads[path.name] = reads.get(path.name, 0) + 1
+        if path.name in ("a_prospectus.json", "a_docling.json", "a_docling.meta.json"):
+            path.write_bytes(b"null")
+        return data
+    monkeypatch.setattr(Path, "read_bytes", read_then_replace)
+    assert publish.verify_published(out, manifest) == (True, "all files match")
+    assert reads == {name: 1 for name in {*manifest["files"], *manifest["cache_files"]}}
+    assert publish.verify_published(out, manifest)[0] is False
+
+
+@pytest.mark.parametrize("cache_map", [{}, {"a_docling.json": "a" * 64},
+    {"a_docling.json": "a" * 64, "b_docling.meta.json": "b" * 64},
+    {"a_docling.json": "a" * 64, "a_docling.meta.json": "b" * 64, "extra": "c" * 64}])
+def test_pdf_manifest_requires_its_complete_matching_cache_pair(tmp_path, pdf_factory, converter,
+                                                              pipeline_state, process, cache_map):
+    pdf = pdf_factory(tmp_path / "in")
+    out = tmp_path / "out"
+    process(pdf, out, converter)
+    manifest = publish.read_manifest(out / "a_publish.json")
+    manifest["cache_files"] = cache_map
+    manifest["run_identity"]["cache_files"] = cache_map
+    path = out / "a_publish.json"
+    path.write_text(json.dumps(manifest), encoding="utf-8")
+    assert publish.read_manifest(path) is None
+    assert publish.verify_published(out, manifest)[0] is False
diff --git a/tests/test_prospectus_publish.py b/tests/test_prospectus_publish.py
index 776a035..9820f26 100644
--- a/tests/test_prospectus_publish.py
+++ b/tests/test_prospectus_publish.py
@@ -1,29 +1,77 @@
 """Staging, file-by-file publication, publish manifest, failure diagnostics."""
 
 from __future__ import annotations
 
+import codecs
+import csv
+import io
 import json
+from pathlib import Path
+import re
 
 import pytest
 
-from backend.bintanong_tools.prospectus_extractor import publish
+from backend.bintanong_tools.prospectus_extractor import batch, loader, paths, publish, views
 
-IDENTITY = {"run_key": "k" * 64}
+IDENTITY = {"run_key": "a" * 64, "input_kind": "docling-json",
+            "input_sha256": "b" * 64, "pdf_sha256": None,
+            "conversion_identity": None, "conversion_settings": None, "cache_files": {}}
 
 
 def stage_files(stage, contents: dict[str, str]):
     stage.mkdir(parents=True, exist_ok=True)
     for name, text in contents.items():
+        if name.endswith("_prospectus.json"):
+            text = json.dumps({"run_identity": IDENTITY, "marker": text})
         publish.write_text_lf(stage / name, text)
 
 
+@pytest.mark.parametrize("title", [
+    "Sining, kultura – ñ",
+    "Sining, kultura\r\nWikang Filipino – ñ",
+    "Sining\rWikang Filipino – ñ",
+])
+def test_review_csv_uses_lf_records_and_preserves_bom_columns_and_field_data(tmp_path, title):
+    path = tmp_path / "out" / "a_review.csv"
+    views.write_review_csv([{
+        "year_level": "FIRST YEAR", "semester": "FIRST SEMESTER", "course_code": "FIL 1",
+        "course_title": title, "total_units": 3, "lecture_units": 3, "lab_units": 0,
+        "prerequisites": ["GE 1", "GE 2"], "prerequisites_unresolved": ["ñ"],
+        "standing_requirements": ["First year", "Approved"], "category": "GE",
+        "elective_group": "Wika", "prerequisites_raw": "GE 1, GE 2", "title_raw": "Wikang ñ",
+        "footnote_marker": "*", "_source": {"table_index": 0, "row_index": 1, "column_group": 2},
+        "provenance": {"source_cell_ids": ["c1", "c2"], "page": 0, "bbox": [1, 2, 3, 4],
+                       "resolution_method": "reviewed", "repair_id": "r1"},
+    }], path)
+
+    raw = path.read_bytes()
+    assert raw.startswith(codecs.BOM_UTF8)
+    assert title.encode("utf-8") in raw
+    record_bytes = raw.replace(title.encode("utf-8"), b"")
+    assert b"\r" not in record_bytes
+    assert record_bytes.count(b"\n") == 2
+    assert raw.endswith(b"\n")
+    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
+    expected = {
+        "year_level": "FIRST YEAR", "semester": "FIRST SEMESTER", "course_code": "FIL 1",
+        "course_title": title, "units_total": "3", "units_lecture": "3", "units_lab": "0",
+        "prerequisites_resolved": "GE 1, GE 2", "prerequisites_unresolved": "ñ",
+        "standing_requirements": "First year | Approved", "category": "GE", "elective_group": "Wika",
+        "prerequisites_raw": "GE 1, GE 2", "title_raw": "Wikang ñ", "footnote_marker": "*",
+        "table_index": "0", "row_index": "1", "column_group": "2", "source_cell_ids": "c1 | c2",
+        "page": "0", "bbox": "[1, 2, 3, 4]", "resolution_method": "reviewed", "repair_id": "r1",
+    }
+    assert reader.fieldnames == list(expected)
+    assert list(reader) == [expected]
+
+
 def test_output_names_match_the_historical_companion_names(tmp_path):
     names = publish.output_names(tmp_path / "out" / "bscs_prospectus.json")
     assert names.base == "bscs"
     assert names.essentials.name == "bscs_essentials.json"
     assert names.prolog.name == "bscs_prospectus.pl"
     assert names.rag.name == "bscs_rag.jsonl"
     assert names.csv.name == "bscs_review.csv"
     assert names.markup.name == "bscs_prospectus.md"  # Phase B markup twin
     assert names.manifest.name == "bscs_publish.json"
     assert names.failed_dir == tmp_path / "out" / "failed" / "bscs"
@@ -37,21 +85,21 @@ def test_publish_replaces_existing_files_and_writes_the_manifest_last(tmp_path,
     stage = tmp_path / "out" / ".a.staging-x"
     stage_files(stage, {"a_review.csv": "new csv", "a_prospectus.json": "new main"})
 
     order = []
     real = publish.replace_file
     monkeypatch.setattr(publish, "replace_file",
                         lambda source, target, *a, **k: (order.append(target.name), real(source, target, *a, **k)))
     publish.publish_staged(stage, names, ["a_review.csv", "a_prospectus.json"], [], IDENTITY, "ok")
 
     assert order == ["a_review.csv", "a_prospectus.json", "a_publish.json"]
-    assert names.final.read_text(encoding="utf-8") == "new main"
+    assert json.loads(names.final.read_bytes())["marker"] == "new main"
     manifest = publish.read_manifest(names.manifest)
     assert manifest["run_key"] == IDENTITY["run_key"]
     assert manifest["audit_status"] == "ok"
     assert sorted(manifest["files"]) == ["a_prospectus.json", "a_review.csv"]
     assert publish.verify_published(names.final.parent, manifest) == (True, "all files match")
 
 
 def test_main_json_must_be_the_last_output(tmp_path):
     names = publish.output_names(tmp_path / "out" / "a_prospectus.json")
     stage = tmp_path / "out" / ".a.staging-x"
@@ -140,26 +188,104 @@ def test_write_failure_keeps_staged_files_and_clears_the_previous_diagnostics(tm
     assert record["error_message"] == "parser blew up"
     assert "Traceback" in record["traceback"]
     assert record["run_identity"] == {"run_key": "k"}
 
     publish.clear_failure(names)
     assert not names.failed_dir.exists()
 
 
 def test_stale_staging_directories_are_removed_for_the_same_base_only(tmp_path):
     out = tmp_path / "out"
-    (out / ".a.staging-dead").mkdir(parents=True)
-    (out / ".b.staging-live").mkdir()
+    prefix = ".s-ca978112ca1bbdcafac231b39a23dc4d-"  # SHA256 of UTF-8 "a", first 128 bits
+    stale = out / (prefix + "deadbeef")
+    stale.mkdir(parents=True)
+    (stale / "partial.json").write_bytes(b"partial")
+    neighbors = [out / ".s-ca978112ffffffffffffffffffffffff-12345678",
+                 out / ".s-3e23e8160039594a33894f6564e1b1348-12345678",
+                 out / "unrelated"]
+    for neighbor in neighbors:
+        neighbor.mkdir()
+        (neighbor / "keep.txt").write_bytes(b"keep")
+    matching_file = out / (prefix + "87654321")
+    matching_file.write_bytes(b"keep file")
     stage = publish.new_staging_dir(out, "a")
-    assert not (out / ".a.staging-dead").exists()
-    assert (out / ".b.staging-live").exists()
-    assert stage.parent == out and stage.name.startswith(".a.staging-") and stage.is_dir()
+    assert not stale.exists()
+    assert all((neighbor / "keep.txt").read_bytes() == b"keep" for neighbor in neighbors)
+    assert matching_file.read_bytes() == b"keep file"
+    assert stage.parent == out and stage.is_dir()
+    assert re.fullmatch(re.escape(prefix) + "[0-9a-f]{8}", stage.name)
+    second = publish.new_staging_dir(out, "a")
+    assert second != stage and second.is_dir() and not stage.exists()
+
+
+def test_default_output_root_is_home_relative_without_creating_it(tmp_path, monkeypatch):
+    home = tmp_path / "absent-home"
+    monkeypatch.setattr(Path, "home", classmethod(lambda cls: home))
+    assert paths.find_default_output_root() == home / "Bintanong" / "output"
+    assert batch.BatchConfig().output_root == home / "Bintanong" / "output"
+    explicit = tmp_path / "explicit-output"
+    assert batch.BatchConfig(output_root=explicit).output_root == explicit
+    assert not home.exists() and not explicit.exists()
+
+
+def test_compact_staging_uses_the_utf8_stem_digest(tmp_path):
+    stage = publish.new_staging_dir(tmp_path, "ñ prospectus")
+    assert re.fullmatch(r"\.s-47ceaa5e781a5b7de3677827a86b6d52-[0-9a-f]{8}", stage.name)
+
+
+@pytest.mark.parametrize("relative,expected_base", [
+    ("Tiniguiban - Main/CS/Computer Science/New Curriculum (2025-2026)/"
+     "1_BS Computer Science_for BOR approval _rev02_v7_6 August 2025.pdf",
+     "1_BS Computer Science_for BOR approval _rev02_v7_6 August 2025"),
+    ("Citizens Charter/BS Computer Science_for BOR approval _rev02_v7_6 August 2025 (2).pdf",
+     "BS Computer Science_for BOR approval _rev02_v7_6 August 2025 _2_"),
+])
+def test_actual_long_paths_fit_with_generated_stage_and_atomic_temp_names(
+    tmp_path_factory, monkeypatch, relative, expected_base,
+):
+    # Project only: actual files stay in pytest's external scratch, never in the home output root.
+    tmp_path = tmp_path_factory.mktemp("paths")
+    relative = Path(relative)
+    item = batch.build_batch_items([tmp_path / "inputs" / relative], batch.BatchConfig(
+        input_root=tmp_path / "inputs", output_root=paths.find_default_output_root(),
+    ))[0]
+    names = publish.output_names(item.json_path)
+    stage = publish.new_staging_dir(tmp_path / "out", names.base)
+    assert len(str(names.final)) < 260
+    assert len(str(names.final.parent / stage.name / names.final.name)) < 260
+    temp_names = []
+    real_replace = loader.replace_file
+
+    def replace(source, target):
+        temp_names.append(source.name)
+        real_replace(source, target)
+
+    monkeypatch.setattr(loader, "replace_file", replace)
+    raw = stage / f"{relative.stem}_docling.json"
+    meta = loader._cache_meta_path(raw)
+    loader._write_bytes_atomic(meta, b"cache bytes")
+    assert meta.read_bytes() == b"cache bytes" and len(temp_names) == 1
+    artifacts = [names.final, names.essentials, names.prolog, names.rag, names.csv,
+                 names.markup, names.manifest, names.final.parent / raw.name,
+                 names.final.parent / meta.name]
+    projected_stage = names.final.parent / stage.name
+    projected = {
+        "final": artifacts,
+        "stage": [projected_stage / artifact.name for artifact in artifacts],
+        "temp": [projected_stage / temp_names[0]],
+        "failed": [names.failed_dir / artifact.name for artifact in artifacts]
+                  + [names.failed_dir / "failure.json"],
+    }
+    assert names.final.name == f"{expected_base}_prospectus.json"
+    assert names.failed_dir == names.final.parent / "failed" / expected_base
+    for kind, candidates in projected.items():
+        assert max(len(str(path)) for path in candidates) < 260, (kind, candidates)
 
 
 def test_markup_twin_is_published_before_the_main_json_and_removed_when_stale(tmp_path):
     out = tmp_path / "out"
     names = publish.output_names(out / "a_prospectus.json")
     stage = out / ".a.staging-1"
     stage_files(stage, {"a_prospectus.md": "md", "a_prospectus.json": "m1"})
     publish.publish_staged(stage, names, ["a_prospectus.md", "a_prospectus.json"], [], IDENTITY, "ok")
     assert names.markup.read_text(encoding="utf-8") == "md"
     stage2 = out / ".a.staging-2"
@@ -186,13 +312,144 @@ def test_a_publish_target_that_stays_locked_keeps_the_staged_file_for_diagnostic
     stage = out / ".a.staging-1"
     stage_files(stage, {"a_prospectus.json": "new main"})
 
     def locked(src, dst):
         raise PermissionError(13, "The process cannot access the file", str(dst))
 
     monkeypatch.setattr(os, "replace", locked)
     monkeypatch.setattr(time, "sleep", lambda _seconds: None)
     with pytest.raises(publish.ReplaceFailed, match="a_prospectus.json"):
         publish.publish_staged(stage, names, ["a_prospectus.json"], [], IDENTITY, "ok")
-    assert (stage / "a_prospectus.json").read_text(encoding="utf-8") == "new main"
+    assert json.loads((stage / "a_prospectus.json").read_bytes())["marker"] == "new main"
     assert names.final.read_text(encoding="utf-8") == "old main"
     assert not names.manifest.exists()
+
+
+
+def valid_manifest():
+    return {"schema": publish.PUBLISH_SCHEMA, "run_key": IDENTITY["run_key"],
+            "run_identity": dict(IDENTITY), "main_file": "a_prospectus.json",
+            "files": {"a_prospectus.json": "d" * 64}, "cache_files": {}}
+
+
+BAD_NAMES = ["", ".", "..", "../victim", "..\\victim", "nested/file", "nested\\file",
+             "C:/victim", "C:relative", "\\\\server\\share", "a:stream", "a.", "a ", "a\x00b"]
+
+
+@pytest.mark.parametrize("name", BAD_NAMES)
+def test_manifest_rejects_unsafe_leaf_names(tmp_path, name):
+    manifest = valid_manifest()
+    manifest["files"] = {name: "d" * 64}
+    manifest["main_file"] = name
+    path = tmp_path / "manifest.json"
+    path.write_text(json.dumps(manifest), encoding="utf-8")
+    assert publish.read_manifest(path) is None
+    assert publish.verify_published(tmp_path, manifest)[0] is False
+
+
+@pytest.mark.parametrize("field,value", [
+    ("schema", "palsu-prospectus-publish-v1"), ("files", {}), ("files", []), ("files", None),
+    ("files", {"a_prospectus.json": None}), ("files", {"a_prospectus.json": "D" * 64}),
+    ("files", {"a_prospectus.json": "g" * 64}), ("files", {"a_prospectus.json": 3}),
+    ("run_key", "k" * 64), ("run_key", None), ("main_file", "absent.json"),
+    ("main_file", None), ("cache_files", []), ("cache_files", None),
+    ("cache_files", {"a_docling.json": "e" * 64}), ("run_identity", None),
+    ("run_identity", []), ("run_identity", {"run_key": "b" * 64}),
+])
+def test_manifest_rejects_invalid_shape(tmp_path, field, value):
+    manifest = valid_manifest()
+    manifest[field] = value
+    path = tmp_path / "manifest.json"
+    path.write_text(json.dumps(manifest), encoding="utf-8")
+    assert publish.read_manifest(path) is None
+    assert publish.verify_published(tmp_path, manifest)[0] is False
+
+
+@pytest.mark.parametrize("root", [None, [], 1, "manifest"])
+def test_manifest_root_fails_closed(tmp_path, root):
+    path = tmp_path / "manifest.json"
+    path.write_text(json.dumps(root), encoding="utf-8")
+    assert publish.read_manifest(path) is None
+    assert publish.verify_published(tmp_path, root)[0] is False
+
+
+@pytest.mark.parametrize("field", ["input_kind", "cache_files", "run_key"])
+def test_missing_identity_fields_fail_closed(tmp_path, field):
+    manifest = valid_manifest()
+    manifest["run_identity"].pop(field)
+    assert publish.verify_published(tmp_path, manifest)[0] is False
+
+
+@pytest.mark.parametrize("content", [b"\xff", b"{", b"[]", b"null", b"{}"])
+def test_main_must_parse_and_bind_manifest_identity(tmp_path, content):
+    import hashlib
+    manifest = valid_manifest()
+    (tmp_path / "a_prospectus.json").write_bytes(content)
+    manifest["files"]["a_prospectus.json"] = hashlib.sha256(content).hexdigest()
+    assert publish.verify_published(tmp_path, manifest)[0] is False
+
+
+def test_unreadable_file_fails_closed(tmp_path, monkeypatch):
+    from pathlib import Path
+    manifest = valid_manifest()
+    (tmp_path / "a_prospectus.json").write_bytes(b"{}")
+    real = Path.read_bytes
+    def denied(path):
+        if path.name == "a_prospectus.json":
+            raise PermissionError("locked")
+        return real(path)
+    monkeypatch.setattr(Path, "read_bytes", denied)
+    assert publish.verify_published(tmp_path, manifest)[0] is False
+
+
+def test_resolved_leaf_cannot_escape_directory(tmp_path, monkeypatch):
+    from pathlib import Path
+    manifest = valid_manifest()
+    real = Path.resolve
+    def escape(path, *args, **kwargs):
+        if path.name == "a_prospectus.json":
+            return tmp_path.parent / "victim.json"
+        return real(path, *args, **kwargs)
+    monkeypatch.setattr(Path, "resolve", escape)
+    assert publish.verify_published(tmp_path, manifest)[0] is False
+
+
+def test_stale_cleanup_keeps_arbitrary_previous_entries_and_cache(tmp_path):
+    import hashlib
+    out = tmp_path / "out"
+    names = publish.output_names(out / "a_prospectus.json")
+    out.mkdir()
+    keep = ["a_docling.json", "a_docling.meta.json", "neighbor.txt"]
+    for name in [*keep, "a_prospectus.pl"]:
+        (out / name).write_bytes(b"keep")
+    previous = valid_manifest()
+    previous["files"].update({name: hashlib.sha256(b"keep").hexdigest() for name in keep})
+    names.manifest.write_text(json.dumps(previous), encoding="utf-8")
+    stage = out / ".stage"
+    stage_files(stage, {"a_prospectus.json": "new"})
+    publish.publish_staged(stage, names, ["a_prospectus.json"], [], IDENTITY, "ok")
+    assert all((out / name).read_bytes() == b"keep" for name in keep)
+    assert not names.prolog.exists()
+
+
+@pytest.mark.parametrize("outputs,caches", [
+    (["a_prospectus.json", "a_prospectus.json"], []),
+    (["../victim", "a_prospectus.json"], []),
+    (["a_publish.json", "a_prospectus.json"], []),
+    (["a_prospectus.json"], ["a_prospectus.json"]),
+])
+def test_invalid_publish_names_refuse_before_any_replace(tmp_path, monkeypatch, outputs, caches):
+    names = publish.output_names(tmp_path / "out" / "a_prospectus.json")
+    stage = tmp_path / "stage"
+    stage_files(stage, {"a_prospectus.json": "new"})
+    def must_not_replace(*args, **kwargs):
+        pytest.fail("invalid publication attempted a replace")
+    monkeypatch.setattr(publish, "replace_file", must_not_replace)
+    with pytest.raises(ValueError):
+        publish.publish_staged(stage, names, outputs, caches, IDENTITY, "ok")
+
+
+
+def test_invalid_utf8_manifest_is_rejected(tmp_path):
+    path = tmp_path / "manifest.json"
+    path.write_bytes(b"\xff")
+    assert publish.read_manifest(path) is None

```
