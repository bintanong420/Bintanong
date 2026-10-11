# Review package task-d-publish
Worktree: C:\Users\Hawksprey\source\repos\Bintanong-wt\phase-d
BASE: 53e3c000958eae9cf4e12e197a6e54b7cc7b2e84
TIP: 597e8c0289b8c090edf494248a9bd3fedad6aeb4

## Commits
597e8c0 fix: bind prospectus publication to captured cache snapshots

## Stat
 .../prospectus_extractor/pipeline.py               |  23 +-
 .../prospectus_extractor/publish.py                | 166 ++++++++----
 .../extractor_split_progress.md                    |  21 ++
 tests/test_prospectus_authority.py                 |  23 +-
 tests/test_prospectus_batch_skip.py                |  29 +++
 tests/test_prospectus_cache.py                     |   5 +-
 tests/test_prospectus_publication.py               | 284 ++++++++++++++++++++-
 tests/test_prospectus_publish.py                   | 141 +++++++++-
 8 files changed, 631 insertions(+), 61 deletions(-)

## Diff
```diff
diff --git a/backend/bintanong_tools/prospectus_extractor/pipeline.py b/backend/bintanong_tools/prospectus_extractor/pipeline.py
index da252d9..1c091d3 100644
--- a/backend/bintanong_tools/prospectus_extractor/pipeline.py
+++ b/backend/bintanong_tools/prospectus_extractor/pipeline.py
@@ -325,37 +325,46 @@ def process_prospectus(
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
         }
         if run_id["review_input_only"]:
             payload["run_identity"]["review_note"] = REVIEW_INPUT_NOTE
 
         outputs = _stage_outputs(
             stage, names, document, payload, is_pdf, export_pl, export_jsonl, export_csv, export_md,
         )
         captured.verify_unchanged()
-        publish_staged(stage, names, outputs, cache_files, payload["run_identity"], payload["audit"]["status"])
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
index 177d6e8..ac74fae 100644
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
@@ -92,95 +93,174 @@ def replace_file(source: Path, target: Path, attempts: int = 5, delay: float = 0
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
diff --git a/plans/plan_current_progress/extractor_split_progress.md b/plans/plan_current_progress/extractor_split_progress.md
index a18762f..9feba7a 100644
--- a/plans/plan_current_progress/extractor_split_progress.md
+++ b/plans/plan_current_progress/extractor_split_progress.md
@@ -274,10 +274,31 @@ Real Docling on CPU, venv Python from the worktree root: `-i <in> --batch -o <ou
  M backend/bintanong_tools/prospectus_extractor/pipeline.py
  M plans/plan_current_progress/extractor_split_progress.md
  M tests/conftest.py
  M tests/test_prospectus_authority.py
  M tests/test_prospectus_batch_skip.py
  M tests/test_prospectus_markup.py
 ?? tests/test_prospectus_input_snapshot.py.
 - Evidence: task-d-identity-report.md; task-d-identity-final-fullsuite.log; task-d-identity-final-comprehensive.log; task-d-identity-selftest.log.
 - Next: Stage only explicit F3/F6 implementation tests and progress files; commit with required final coauthor trailer.
 - Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
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
diff --git a/tests/test_prospectus_authority.py b/tests/test_prospectus_authority.py
index e1cecca..7ae11c0 100644
--- a/tests/test_prospectus_authority.py
+++ b/tests/test_prospectus_authority.py
@@ -310,23 +310,40 @@ def test_hash_mismatch_raises_before_any_output_is_touched(tmp_path):
     assert out.read_text(encoding="utf-8") == "previous accepted output"
     assert not (tmp_path / "x_essentials.json").exists()
 
 
 def test_matching_hash_is_recorded_and_still_does_not_authorize(tmp_path, monkeypatch):
     pdf = tmp_path / "prospectus.pdf"
     pdf.write_bytes(b"%PDF-1.4\noriginal")
     source = ProvisionalSource(hashlib.sha256(b"%PDF-1.4\noriginal").hexdigest(), "local/prospectus.pdf")
     grid = [CS_HEADER, _merged("FIRST YEAR", 8), _cs_semester_row(), CONTROL]
     document = fixture_document(grid, [("title", "BACHELOR OF SCIENCE IN COMPUTER SCIENCE PROGRAM")])
-    from backend.bintanong_tools.prospectus_extractor.loader import DocumentLoadResult
-    monkeypatch.setattr(pipeline, "load_document_result",
-                        lambda *args, **kwargs: DocumentLoadResult(document, None, "converted"))
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
index 228e1ae..b6dccc0 100644
--- a/tests/test_prospectus_batch_skip.py
+++ b/tests/test_prospectus_batch_skip.py
@@ -175,10 +175,39 @@ def test_single_file_cli_reconverts_only_with_force(monkeypatch, tmp_path):
     pdf.write_bytes(b"%PDF-one")
     assert cli.main(["-i", str(pdf)]) == 0
     assert cli.main(["-i", str(pdf), "--force"]) == 0
     assert [call["force_reconvert"] for call in seen] == [False, True]
 
 
 def test_batch_manifest_schema_names_the_new_record_shape():
     from backend.bintanong_tools.prospectus_extractor import common
 
     assert common.MANIFEST_SCHEMA_VERSION == "palsu-prospectus-batch-manifest-v3.1"
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
diff --git a/tests/test_prospectus_cache.py b/tests/test_prospectus_cache.py
index 8d457da..3f794b3 100644
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
index 776a035..53a9607 100644
--- a/tests/test_prospectus_publish.py
+++ b/tests/test_prospectus_publish.py
@@ -1,26 +1,30 @@
 """Staging, file-by-file publication, publish manifest, failure diagnostics."""
 
 from __future__ import annotations
 
 import json
 
 import pytest
 
 from backend.bintanong_tools.prospectus_extractor import publish
 
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
 
 
 def test_output_names_match_the_historical_companion_names(tmp_path):
     names = publish.output_names(tmp_path / "out" / "bscs_prospectus.json")
     assert names.base == "bscs"
     assert names.essentials.name == "bscs_essentials.json"
     assert names.prolog.name == "bscs_prospectus.pl"
     assert names.rag.name == "bscs_rag.jsonl"
     assert names.csv.name == "bscs_review.csv"
@@ -37,21 +41,21 @@ def test_publish_replaces_existing_files_and_writes_the_manifest_last(tmp_path,
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
@@ -186,13 +190,144 @@ def test_a_publish_target_that_stays_locked_keeps_the_staged_file_for_diagnostic
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
