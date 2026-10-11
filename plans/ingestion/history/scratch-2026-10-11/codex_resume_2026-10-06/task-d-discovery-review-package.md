# Review package task-d-discovery
Worktree: C:\Users\Hawksprey\source\repos\Bintanong-wt\phase-d
BASE: 597e8c0289b8c090edf494248a9bd3fedad6aeb4
TIP: df5eec4bdf0d3b9f46addfce7911b00a705ec126

## Commits
df5eec4 fix(prospectus): scope discovery exclusions to selected inputs

## Stat
 .../bintanong_tools/prospectus_extractor/batch.py  |  8 ++-
 .../extractor_split_progress.md                    | 46 ++++++++++++
 tests/test_prospectus_batch_skip.py                | 82 ++++++++++++++++++++++
 3 files changed, 134 insertions(+), 2 deletions(-)

## Diff
```diff
diff --git a/backend/bintanong_tools/prospectus_extractor/batch.py b/backend/bintanong_tools/prospectus_extractor/batch.py
index e8964e3..170325d 100644
--- a/backend/bintanong_tools/prospectus_extractor/batch.py
+++ b/backend/bintanong_tools/prospectus_extractor/batch.py
@@ -61,40 +61,44 @@ class BatchItem:
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
diff --git a/plans/plan_current_progress/extractor_split_progress.md b/plans/plan_current_progress/extractor_split_progress.md
index 9feba7a..6d90972 100644
--- a/plans/plan_current_progress/extractor_split_progress.md
+++ b/plans/plan_current_progress/extractor_split_progress.md
@@ -295,10 +295,56 @@ Real Docling on CPU, venv Python from the worktree root: `-i <in> --batch -o <ou
  M backend/bintanong_tools/prospectus_extractor/publish.py
  M plans/plan_current_progress/extractor_split_progress.md
  M tests/test_prospectus_authority.py
  M tests/test_prospectus_batch_skip.py
  M tests/test_prospectus_cache.py
  M tests/test_prospectus_publication.py
  M tests/test_prospectus_publish.py.
 - Evidence: task-d-publish-report.md; task-d-publish-final-fullsuite.log; task-d-publish-final-comprehensive.log; task-d-publish-selftest.log.
 - Next: Explicitly stage two production files, five test files and progress; commit with required trailer; parent independently reviews baseline53e3c00..tip..
 - Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
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
diff --git a/tests/test_prospectus_batch_skip.py b/tests/test_prospectus_batch_skip.py
index b6dccc0..7ca7b5d 100644
--- a/tests/test_prospectus_batch_skip.py
+++ b/tests/test_prospectus_batch_skip.py
@@ -125,20 +125,21 @@ def test_error_record_points_at_the_diagnostics_and_keeps_earlier_files(env):
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
@@ -204,10 +205,91 @@ def test_old_v1_manifest_refuses_skip(env):
     import json
     env.run()
     path = env.out / "a_publish.json"
     old = json.loads(path.read_bytes())
     old["schema"] = "palsu-prospectus-publish-v1"
     path.write_text(json.dumps(old), encoding="utf-8")
     record = only(env.run())
     assert record["status"] == "ok"
     assert record["skip_check"] == "no publish manifest"
     assert env.state.builds == 2
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

```
