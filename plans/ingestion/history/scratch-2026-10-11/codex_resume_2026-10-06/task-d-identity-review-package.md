# Review package task-d-identity
Worktree: C:\Users\Hawksprey\source\repos\Bintanong-wt\phase-d
BASE: 641523d212839084da03d966ffbfca66c7e83e42
TIP: 53e3c000958eae9cf4e12e197a6e54b7cc7b2e84

## Commits
53e3c00 fix: bind prospectus conversion to immutable input bytes

## Stat
 backend/bintanong_tools/prospectus.py              |   5 +-
 .../bintanong_tools/prospectus_extractor/batch.py  |  47 ++---
 .../prospectus_extractor/identity.py               |  42 +++-
 .../bintanong_tools/prospectus_extractor/loader.py |  93 +++++++--
 .../prospectus_extractor/pipeline.py               |  17 +-
 .../extractor_split_progress.md                    |  31 +++
 tests/conftest.py                                  |   4 +-
 tests/test_prospectus_authority.py                 |   4 +-
 tests/test_prospectus_batch_skip.py                |   5 +-
 tests/test_prospectus_input_snapshot.py            | 223 +++++++++++++++++++++
 tests/test_prospectus_markup.py                    |   8 +-
 11 files changed, 406 insertions(+), 73 deletions(-)

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
index ea6ed10..e8964e3 100644
--- a/backend/bintanong_tools/prospectus_extractor/batch.py
+++ b/backend/bintanong_tools/prospectus_extractor/batch.py
@@ -10,22 +10,21 @@ from typing import Any
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
 from .publish import output_names, read_manifest, verify_published
 
 
 def safe_stem(path: Path) -> str:
     stem = Path(path).stem.strip()
     if stem.endswith("_docling"):  # batching saved Docling JSON should not double the suffix
         stem = stem[: -len("_docling")]
     stem = re.sub(r"[^A-Za-z0-9._ -]+", "_", stem)
@@ -153,34 +152,36 @@ def write_manifest(records: Sequence[dict[str, Any]], output_root: Path) -> Path
             "audit_failed": sum(1 for r in records if r.get("status") == "audit_error"),
             "skipped": sum(1 for r in records if r.get("status") == "skipped"),
             "failed": sum(1 for r in records if r.get("status") == "error"),
         },
         "records": records,
     }
     target.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
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
@@ -196,72 +197,60 @@ def skip_check(item: BatchItem, config: BatchConfig, package_hash: str) -> tuple
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
@@ -279,20 +268,22 @@ def run_batch(config: BatchConfig) -> dict[str, Any]:
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
index fef5126..63932aa 100644
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
@@ -312,34 +313,46 @@ def _write_bytes_atomic(path: Path, data: bytes) -> None:
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
diff --git a/backend/bintanong_tools/prospectus_extractor/pipeline.py b/backend/bintanong_tools/prospectus_extractor/pipeline.py
index d2872f1..da252d9 100644
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
@@ -292,36 +293,39 @@ def process_prospectus(
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
@@ -336,20 +340,21 @@ def process_prospectus(
         payload["run_identity"] = {
             **run_id,
             "cache": ("converted" if cache_files else "reused") if is_pdf else "not-applicable",
         }
         if run_id["review_input_only"]:
             payload["run_identity"]["review_note"] = REVIEW_INPUT_NOTE
 
         outputs = _stage_outputs(
             stage, names, document, payload, is_pdf, export_pl, export_jsonl, export_csv, export_md,
         )
+        captured.verify_unchanged()
         publish_staged(stage, names, outputs, cache_files, payload["run_identity"], payload["audit"]["status"])
         clear_failure(names)
     except Exception as exc:
         write_failure(names, exc, input_path, run_id, stage)
         raise
     finally:
         shutil.rmtree(stage, ignore_errors=True)
 
     if not quiet:
         for name in outputs:
diff --git a/plans/plan_current_progress/extractor_split_progress.md b/plans/plan_current_progress/extractor_split_progress.md
index 2b2213d..a18762f 100644
--- a/plans/plan_current_progress/extractor_split_progress.md
+++ b/plans/plan_current_progress/extractor_split_progress.md
@@ -243,10 +243,41 @@ Red (14 failed, 1 passed, tests/test_prospectus_batch_skip.py, after the conftes
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
index afcf9e6..e1cecca 100644
--- a/tests/test_prospectus_authority.py
+++ b/tests/test_prospectus_authority.py
@@ -310,21 +310,23 @@ def test_hash_mismatch_raises_before_any_output_is_touched(tmp_path):
     assert out.read_text(encoding="utf-8") == "previous accepted output"
     assert not (tmp_path / "x_essentials.json").exists()
 
 
 def test_matching_hash_is_recorded_and_still_does_not_authorize(tmp_path, monkeypatch):
     pdf = tmp_path / "prospectus.pdf"
     pdf.write_bytes(b"%PDF-1.4\noriginal")
     source = ProvisionalSource(hashlib.sha256(b"%PDF-1.4\noriginal").hexdigest(), "local/prospectus.pdf")
     grid = [CS_HEADER, _merged("FIRST YEAR", 8), _cs_semester_row(), CONTROL]
     document = fixture_document(grid, [("title", "BACHELOR OF SCIENCE IN COMPUTER SCIENCE PROGRAM")])
-    monkeypatch.setattr(pipeline, "load_document", lambda *args, **kwargs: (document, None))
+    from backend.bintanong_tools.prospectus_extractor.loader import DocumentLoadResult
+    monkeypatch.setattr(pipeline, "load_document_result",
+                        lambda *args, **kwargs: DocumentLoadResult(document, None, "converted"))
     out = tmp_path / "x_prospectus.json"
 
     payload = pipeline.process_prospectus(pdf, output_path=out, semantic_doc_path=None, quiet=True, source=source)
 
     assert payload["authority"]["source_record"]["pdf_hash_check"] == "matched"
     assert "pdf_hash_not_checked" not in payload["authority"]["blocked_by"]
     assert payload["authority"]["eligibility_executable"] is False
     essentials = json.loads((tmp_path / "x_essentials.json").read_text(encoding="utf-8"))
     assert essentials["schema_version"] == "palsu-prospectus-essentials-v2"
     assert essentials["extraction_status"] == "EXTRACTED_WITH_WARNINGS"  # an audit result, never "verified"
diff --git a/tests/test_prospectus_batch_skip.py b/tests/test_prospectus_batch_skip.py
index 3d19248..228e1ae 100644
--- a/tests/test_prospectus_batch_skip.py
+++ b/tests/test_prospectus_batch_skip.py
@@ -1,31 +1,30 @@
 """--skip-existing trusts a published set only when identity and audit status say so."""
 
 from __future__ import annotations
 
 from types import SimpleNamespace
 
 import pytest
 
-from backend.bintanong_tools.prospectus_extractor import batch, pipeline
+from backend.bintanong_tools.prospectus_extractor import batch, loader, pipeline
 from backend.bintanong_tools.prospectus_extractor.batch import BatchConfig, run_batch
 
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

```
