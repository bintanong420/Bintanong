# Review package task-d-skip-tui
Worktree: C:\Users\Hawksprey\source\repos\Bintanong-wt\phase-d
BASE: 4320327bb68ec0973dd79ee7716ab5d893fe00a8
TIP: c40a38c9f633dd085766ca11f81f0dd3890810cc

## Commits
c40a38c fix(prospectus): wire force reconversion into the TUI
10c2d8b fix(prospectus): refuse reuse of context-created outputs

## Stat
 .../bintanong_tools/prospectus_extractor/batch.py  |   5 +
 .../prospectus_extractor/pipeline.py               |   3 +
 .../bintanong_tools/prospectus_extractor/tui.py    |   9 +-
 .../extractor_split_progress.md                    | 118 ++++++++++++++
 tests/test_prospectus_batch_skip.py                | 178 ++++++++++++++++++++-
 5 files changed, 310 insertions(+), 3 deletions(-)

## Diff
```diff
diff --git a/backend/bintanong_tools/prospectus_extractor/batch.py b/backend/bintanong_tools/prospectus_extractor/batch.py
index 4459451..44e3309 100644
--- a/backend/bintanong_tools/prospectus_extractor/batch.py
+++ b/backend/bintanong_tools/prospectus_extractor/batch.py
@@ -171,20 +171,25 @@ def skip_check(
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
+    reusable = manifest["run_identity"].get("skip_reusable")
+    if reusable is False:
+        return False, "previous run used supplied context"
+    if reusable is not True:
+        return False, "previous run skip eligibility is unknown"
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
diff --git a/backend/bintanong_tools/prospectus_extractor/pipeline.py b/backend/bintanong_tools/prospectus_extractor/pipeline.py
index 1c091d3..2525454 100644
--- a/backend/bintanong_tools/prospectus_extractor/pipeline.py
+++ b/backend/bintanong_tools/prospectus_extractor/pipeline.py
@@ -339,20 +339,23 @@ def process_prospectus(
                     or not isinstance(loaded.meta_bytes, bytes)
                     or loaded.raw_json_sha256 is None or loaded.meta_sha256 is None):
                 raise ValueError("PDF load result has no complete captured cache pair")
             cache_files = [raw_cache_path.name, _cache_meta_path(raw_cache_path).name]
             cache_hashes = dict(zip(cache_files, (loaded.raw_json_sha256, loaded.meta_sha256)))
             if loaded.cache_status == "reused":
                 for name, data in zip(cache_files, (loaded.raw_json_bytes, loaded.meta_bytes)):
                     (stage / name).write_bytes(data)
         payload["run_identity"] = {
             **run_id, "cache": loaded.cache_status, "cache_files": cache_hashes,
+            "skip_reusable": all(value is None for value in (
+                source, approved_scope, review_entries, repair_provider,
+            )),
         }
         if run_id["review_input_only"]:
             payload["run_identity"]["review_note"] = REVIEW_INPUT_NOTE
 
         outputs = _stage_outputs(
             stage, names, document, payload, is_pdf, export_pl, export_jsonl, export_csv, export_md,
         )
         captured.verify_unchanged()
         publish_staged(
             stage, names, outputs, cache_files, payload["run_identity"], payload["audit"]["status"],
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
diff --git a/plans/plan_current_progress/extractor_split_progress.md b/plans/plan_current_progress/extractor_split_progress.md
index 0c2d5d8..60c7a92 100644
--- a/plans/plan_current_progress/extractor_split_progress.md
+++ b/plans/plan_current_progress/extractor_split_progress.md
@@ -562,10 +562,128 @@ Real Docling on CPU, venv Python from the worktree root: `-i <in> --batch -o <ou
 - Next: Finish S1 report/progress and normalize edited text LF; stage exact paths.py publish.py loader.py test_prospectus_publish.py test_prospectus_cache.py extractor_split_progress.md; commit with required Claude trailer.
 - Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
 
 ### Phase D S1 compact Windows paths (2026-10-06)
 - Portable default is Path.home() / 'Bintanong' / 'output', replacing the package-local docling_jsonified_output default. Existing artifacts stay in their old location; old consumers must pass explicit --output (JSON path for one file, root for batch). No previous outputs moved/deleted and no home artifacts generated during verification. Existing final/cache filenames, batch sanitization, explicit overrides and failed/<base>/ layout remain unchanged.
 - Stage .s-<32hex UTF8 stem SHA256 prefix>-<8 UUID hex> reuses shared identity.bytes_sha256 through one private prefix helper for generation/cleanup. Cleanup targets the full128bit stem prefix, preserving other stems, unrelated folders and matching regular files. Earlier8digit proposal superseded: cost24 extra path characters, actual stage name44. One writer per output stem retained; no arbitrary-neighbor cleanup or new framework.
 - Atomic cache writer keeps unique tempfile.mkstemp and replacement/failure semantics, shortening only prefix to .t- with .tmp suffix (actual name15). Regression checks cover interleaved writes, locked replacement retry/cleanup and interrupted write cleanup while preserving old bytes.
 - Authentic TDD RED8failed1passed88deselected before production; GREEN9passed88deselected. Fresh focused386passed/no warnings; main full961passed/13subtests/3 existing upstream warnings, with approved API/embedding exclusions. Exact commands/logs in external task-d-paths-report.md and task-d-paths-{red-final,green,focused,full}.log.
 - Read-only original44 corpus projection used actual output directories and generated stage/temp names: root35, final181/stage226/temp161/failed251 versus old final/cache268. Exact maxima paths in external task-d-paths-actual-projection.json. Longest real Tiniguiban CS relative input and separate Citizens Charter BOR proposal (2) boundary covered; no proposal opened/converted. Current corpus fits at most8 extra root characters below260; arbitrary longer home/explicit roots require caller-selected shorter --output, never silent artifact renaming.
 - GUI comprehensive suite, standalone selftest80, semantic44 comparer and trials NOT RUN for S1, deferred parent final D gates. Independent specification then quality reviews pending. S2/S4/F5/final D gates/Task10 and downstream queue remain; Phase D not complete. Existing F4 postcommit/review progress preserved.
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
diff --git a/tests/test_prospectus_batch_skip.py b/tests/test_prospectus_batch_skip.py
index 5474c7d..65b20de 100644
--- a/tests/test_prospectus_batch_skip.py
+++ b/tests/test_prospectus_batch_skip.py
@@ -1,22 +1,26 @@
 """--skip-existing trusts a published set only when identity and audit status say so."""
 
 from __future__ import annotations
 
 from datetime import datetime
 import json
 from types import SimpleNamespace
 
 import pytest
 
-from backend.bintanong_tools.prospectus_extractor import batch, loader, pipeline
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
     monkeypatch.setattr(loader, "get_shared_converter", lambda *a, **k: converter)
@@ -38,21 +42,23 @@ def only(summary):
 
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
@@ -105,23 +111,120 @@ def test_a_file_without_a_manifest_is_not_skipped(env):
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
@@ -174,20 +277,91 @@ def test_single_file_cli_reconverts_only_with_force(monkeypatch, tmp_path):
 
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
 
 
 def test_batch_manifest_writes_utf8_lf_without_changing_content(tmp_path):
     records = [{"status": status, "program": "Sining at kultura – ñ"}
                for status in ("ok", "warn", "audit_error", "skipped", "error")]
     before = datetime.now().replace(microsecond=0)

```
