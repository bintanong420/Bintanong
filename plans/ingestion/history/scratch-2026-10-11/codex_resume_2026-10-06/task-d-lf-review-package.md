# Review package task-d-lf
Worktree: C:\Users\Hawksprey\source\repos\Bintanong-wt\phase-d
BASE: 4a0cdb794a337b9cc91846d16585478c3bb5fde0
TIP: 52da4aaca7d734e83054b1ecd39221ac09302a3b

## Commits
52da4aa fix(prospectus): write batch manifest and review CSV with LF

## Stat
 .../bintanong_tools/prospectus_extractor/batch.py  |  4 +-
 .../bintanong_tools/prospectus_extractor/views.py  |  2 +-
 .../extractor_split_progress.md                    | 92 ++++++++++++++++++++++
 tests/test_prospectus_batch_skip.py                | 23 ++++++
 tests/test_prospectus_publish.py                   | 44 ++++++++++-
 5 files changed, 161 insertions(+), 4 deletions(-)

## Diff
```diff
diff --git a/backend/bintanong_tools/prospectus_extractor/batch.py b/backend/bintanong_tools/prospectus_extractor/batch.py
index e9e5eb7..4459451 100644
--- a/backend/bintanong_tools/prospectus_extractor/batch.py
+++ b/backend/bintanong_tools/prospectus_extractor/batch.py
@@ -13,21 +13,21 @@ import json
 import re
 import traceback
 
 from .common import MANIFEST_SCHEMA_VERSION, RICH_AVAILABLE, console
 
 if RICH_AVAILABLE:
     from .common import track
 from .identity import InputSnapshot, package_sha256, run_identity
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
 
 
@@ -155,21 +155,21 @@ def write_manifest(records: Sequence[dict[str, Any]], output_root: Path) -> Path
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
 
 
 def skip_check(
     item: BatchItem, config: BatchConfig, package_hash: str, *, snapshot: InputSnapshot | None = None,
 ) -> tuple[bool, str]:
     """May this item be skipped? Returns (skip, reason). Never skips a failed audit."""
     if not config.skip_existing:
         return False, "skip-existing not requested"
     if config.force_reconvert:
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
diff --git a/plans/plan_current_progress/extractor_split_progress.md b/plans/plan_current_progress/extractor_split_progress.md
index cb68764..e8d7815 100644
--- a/plans/plan_current_progress/extractor_split_progress.md
+++ b/plans/plan_current_progress/extractor_split_progress.md
@@ -394,10 +394,102 @@ Real Docling on CPU, venv Python from the worktree root: `-i <in> --batch -o <ou
  M tests/test_prospectus_batch_skip.py.
 - Evidence: task-d-discovery-report.md; task-d-discovery-repair-reproduction.log; task-d-discovery-repair-red.log; task-d-discovery-repair-green.log; task-d-discovery-repair-probe.log; task-d-discovery-repair-full.log.
 - Next: Append result/progress; stage only batch.py, test_prospectus_batch_skip.py and preserved progress; commit with required trailer; postcommit checkpoint/report exact tip..
 - Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.
 
 ### Phase D F2 specification repair round1 (2026-10-06)
 - Reproduced Important review finding: configured ../*.pdf yielded root/../course.pdf and above-root failure.json changed discovery. Original reviewer probe preserved; reproduction logged externally.
 - Ruling: root-relative glob patterns cannot have any parent component or anchor. A single PureWindowsPath lexical guard recognizes slash/backslash parent, rooted, drive-relative/absolute and UNC patterns and raises explicit ValueError before glob; valid descendant globs preserved, no symlink resolution/policy change or filesystem abstraction.
 - Repair RED18failed/6passed/38deselected; focused GREEN72passed/no warnings; repaired recursive/nonrecursive probePASS with/without above-root marker; main full952passed/13subtests/3upstream warnings. Exact commands/evidence appended task-d-discovery-report.md; repair reproduction/red/green/probe/full logs external.
 - Existing controller/implementer progress checkpoints preserved. Complete GUI-review suite and standalone final selftest NOT RUN for scanner repair, final Phase D gates remain. Parent same-seat specification re-review before separate quality review; F4/F5/S1/S2/S4/Task10 remain, no Phase D completion claim.
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
diff --git a/tests/test_prospectus_batch_skip.py b/tests/test_prospectus_batch_skip.py
index 1b67e3f..5474c7d 100644
--- a/tests/test_prospectus_batch_skip.py
+++ b/tests/test_prospectus_batch_skip.py
@@ -1,14 +1,16 @@
 """--skip-existing trusts a published set only when identity and audit status say so."""
 
 from __future__ import annotations
 
+from datetime import datetime
+import json
 from types import SimpleNamespace
 
 import pytest
 
 from backend.bintanong_tools.prospectus_extractor import batch, loader, pipeline
 from backend.bintanong_tools.prospectus_extractor.batch import BatchConfig, run_batch
 
 pytestmark = pytest.mark.usefixtures("fake_docling")
 
 
@@ -178,20 +180,41 @@ def test_single_file_cli_reconverts_only_with_force(monkeypatch, tmp_path):
     assert cli.main(["-i", str(pdf), "--force"]) == 0
     assert [call["force_reconvert"] for call in seen] == [False, True]
 
 
 def test_batch_manifest_schema_names_the_new_record_shape():
     from backend.bintanong_tools.prospectus_extractor import common
 
     assert common.MANIFEST_SCHEMA_VERSION == "palsu-prospectus-batch-manifest-v3.1"
 
 
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
 @pytest.mark.parametrize("name", ["a_docling.json", "a_docling.meta.json"])
 @pytest.mark.parametrize("deleted", [False, True])
 def test_changed_or_missing_cache_refuses_skip(env, name, deleted):
     env.run()
     path = env.out / name
     if deleted:
         path.unlink()
     else:
         path.write_bytes(b"{}")
     record = only(env.run())
diff --git a/tests/test_prospectus_publish.py b/tests/test_prospectus_publish.py
index 53a9607..f64eeba 100644
--- a/tests/test_prospectus_publish.py
+++ b/tests/test_prospectus_publish.py
@@ -1,33 +1,75 @@
 """Staging, file-by-file publication, publish manifest, failure diagnostics."""
 
 from __future__ import annotations
 
+import codecs
+import csv
+import io
 import json
 
 import pytest
 
-from backend.bintanong_tools.prospectus_extractor import publish
+from backend.bintanong_tools.prospectus_extractor import publish, views
 
 IDENTITY = {"run_key": "a" * 64, "input_kind": "docling-json",
             "input_sha256": "b" * 64, "pdf_sha256": None,
             "conversion_identity": None, "conversion_settings": None, "cache_files": {}}
 
 
 def stage_files(stage, contents: dict[str, str]):
     stage.mkdir(parents=True, exist_ok=True)
     for name, text in contents.items():
         if name.endswith("_prospectus.json"):
             text = json.dumps({"run_identity": IDENTITY, "marker": text})
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

```
