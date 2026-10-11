# Review package task-d-paths
Worktree: C:\Users\Hawksprey\source\repos\Bintanong-wt\phase-d
BASE: 52da4aaca7d734e83054b1ecd39221ac09302a3b
TIP: 4320327bb68ec0973dd79ee7716ab5d893fe00a8

## Commits
4320327 fix(prospectus): shorten default and intermediate output paths

## Stat
 .../bintanong_tools/prospectus_extractor/loader.py |  2 +-
 .../bintanong_tools/prospectus_extractor/paths.py  |  2 +-
 .../prospectus_extractor/publish.py                |  8 +-
 .../extractor_split_progress.md                    | 76 ++++++++++++++++++
 tests/test_prospectus_cache.py                     | 44 +++++++++++
 tests/test_prospectus_publish.py                   | 92 ++++++++++++++++++++--
 6 files changed, 214 insertions(+), 10 deletions(-)

## Diff
```diff
diff --git a/backend/bintanong_tools/prospectus_extractor/loader.py b/backend/bintanong_tools/prospectus_extractor/loader.py
index 63932aa..85c22ec 100644
--- a/backend/bintanong_tools/prospectus_extractor/loader.py
+++ b/backend/bintanong_tools/prospectus_extractor/loader.py
@@ -302,21 +302,21 @@ def _conversion_errors(result: Any) -> list[str]:
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
diff --git a/backend/bintanong_tools/prospectus_extractor/publish.py b/backend/bintanong_tools/prospectus_extractor/publish.py
index ac74fae..b2ba71a 100644
--- a/backend/bintanong_tools/prospectus_extractor/publish.py
+++ b/backend/bintanong_tools/prospectus_extractor/publish.py
@@ -50,35 +50,39 @@ def output_names(final_path: Path) -> OutputNames:
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
diff --git a/plans/plan_current_progress/extractor_split_progress.md b/plans/plan_current_progress/extractor_split_progress.md
index e8d7815..0c2d5d8 100644
--- a/plans/plan_current_progress/extractor_split_progress.md
+++ b/plans/plan_current_progress/extractor_split_progress.md
@@ -486,10 +486,86 @@ Real Docling on CPU, venv Python from the worktree root: `-i <in> --batch -o <ou
 - Evidence: task-d-lf-red.log; task-d-lf-green.log; task-d-lf-cr-red.log; task-d-lf-runtime-probe.log; task-d-lf-resumed-focused.log; task-d-lf-resumed-full.log.
 - Next: Save concise report and F4 progress; explicitly stage five authorized paths; commit with required Claude trailer.
 - Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
 
 ### Phase D F4 LF artifacts (2026-10-06)
 - Batch manifest reuses publish.write_text_lf; review CSV uses stdlib LF record separators with existing UTF8-sig BOM, native minimal quoting, all23 columns and exact values. No output/schema/name changes.
 - Preserved interrupted worker authentic LF RED3failed/126deselected and GREEN3passed/126deselected. Added bare-CR round-trip parameter without comma; its attempted RED actually passed3cases, explicitly characterization rather than failing evidence.
 - Root superseded QUOTE_ALL hypothesis: main and GUI-review Python3.13.5 both already quote bareCR under LF/QUOTE_MINIMAL; backend requires ==3.13.*. Native quoting retained; runtime probe/log external, no unsupported-runtime workaround or new dependency.
 - Fresh focused GREEN361passed/no warnings; main full956passed/13subtests/3upstream warnings with two approved API/embedding excludes. task-d-lf-report.md and exact original/resume logs outside Git in approved scratch; previous progress checkpoints preserved.
 - GUI-review comprehensive suite and standalone final D selftest NOT RUN for F4, deferred final gates. Parent independent specification then quality review pending; S1/S2/S4/F5/final D gates/Task10 and downstream queue remain. Phase D not complete.
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
diff --git a/tests/test_prospectus_cache.py b/tests/test_prospectus_cache.py
index 3f794b3..6f18436 100644
--- a/tests/test_prospectus_cache.py
+++ b/tests/test_prospectus_cache.py
@@ -200,20 +200,22 @@ def test_interleaved_writers_to_one_target_do_not_share_a_temp_file(tmp_path, mo
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
 
@@ -228,30 +230,72 @@ def test_a_briefly_locked_target_is_retried(tmp_path, monkeypatch):
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
 
diff --git a/tests/test_prospectus_publish.py b/tests/test_prospectus_publish.py
index f64eeba..9820f26 100644
--- a/tests/test_prospectus_publish.py
+++ b/tests/test_prospectus_publish.py
@@ -1,22 +1,24 @@
 """Staging, file-by-file publication, publish manifest, failure diagnostics."""
 
 from __future__ import annotations
 
 import codecs
 import csv
 import io
 import json
+from pathlib import Path
+import re
 
 import pytest
 
-from backend.bintanong_tools.prospectus_extractor import publish, views
+from backend.bintanong_tools.prospectus_extractor import batch, loader, paths, publish, views
 
 IDENTITY = {"run_key": "a" * 64, "input_kind": "docling-json",
             "input_sha256": "b" * 64, "pdf_sha256": None,
             "conversion_identity": None, "conversion_settings": None, "cache_files": {}}
 
 
 def stage_files(stage, contents: dict[str, str]):
     stage.mkdir(parents=True, exist_ok=True)
     for name, text in contents.items():
         if name.endswith("_prospectus.json"):
@@ -186,26 +188,104 @@ def test_write_failure_keeps_staged_files_and_clears_the_previous_diagnostics(tm
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

```
