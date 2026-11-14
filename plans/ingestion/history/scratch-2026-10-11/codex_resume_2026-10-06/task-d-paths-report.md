# D S1 compact Windows paths

Base: 52da4aaca7d734e83054b1ecd39221ac09302a3b. Worktree: C:/Users/Hawksprey/source/repos/Bintanong-wt/phase-d. Commit: 4320327bb68ec0973dd79ee7716ab5d893fe00a8 — fix(prospectus): shorten default and intermediate output paths. Immutable review range: 52da4aaca7d734e83054b1ecd39221ac09302a3b..4320327bb68ec0973dd79ee7716ab5d893fe00a8.

Implemented ~/Bintanong/output, .s-<32 UTF-8 stem SHA256 hex>-<8 UUID hex>, and unique mkstemp .t-*.tmp. Reused identity.bytes_sha256 and one private shared stage-prefix helper. Cleanup remains scoped to the full stem prefix; other stems (including one sharing its first8digest chars), unrelated folders and matching regular files survive. Atomic replacement still preserves complete bytes, handles interleaved writes, retries locked targets, and removes temporary files on failed writes/replaces.

Existing final names, batch sanitization, explicit output roots and failed/<base>/ layout are unchanged. Previous default outputs remain in place; consumers needing the old location must supply --output (JSON filename for single processing, root directory for batch). No old outputs moved/deleted and no home artifacts written. One writer per stem remains required; legacy long-named abandoned stage folders are not targeted by the new digest prefix. Arbitrarily longer home/explicit roots are not guaranteed below260; choose a shorter explicit root rather than silently renaming artifacts.

Read-only projection of all44 original PDFs used actual batch directories, output_names, generated staging names and atomic mkstemp names. Current host root35characters; actual stage44/temp15. Maximum lengths: final181/stage226/temp161/failed251; old final/cache maximum268. Thus at most8additional root characters fit this corpus below260. Exact paths/names: task-d-paths-actual-projection.json. Longest real relative PDF is the Tiniguiban CS New Curriculum file. Additional Citizens Charter/BS Computer Science_for BOR approval _rev02_v7_6 August 2025 (2).pdf is a distinct source-inventory boundary, only projected, never opened/converted; no synthetic path represented as real.

## Commands and results

All commands ran in the worktree above with main Python; test files/temp artifacts and logs were external. Define the literal paths:

```powershell
$Py = 'C:\Users\Hawksprey\source\repos\Bintanong\backend\.venv\Scripts\python.exe'
$Scratch = 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06'
```

Authentic RED before any production change: initial task-d-paths-red.log7failed1passed88deselected; added UTF8 case and independent literal sanitized-name expectations, then final RED8failed1passed88deselected (exit1; assertion failures, no collection/setup errors). Expected failures: root, full32digest cleanup/naming, UTF8 stem, real relative-path projection (266main under oldroot), and short atomic prefix after existing preservation checks. The one passing selected case was preexisting failure-lock coverage.

```powershell
& $Py -m pytest -q tests/test_prospectus_publish.py tests/test_prospectus_cache.py -k 'stale_staging or default_output_root or compact_staging or actual_long_paths or interleaved_writers or stays_locked or atomic_write_failure' -p no:cacheprovider --basetemp "$Scratch\s1-red2-temp" *> "$Scratch\task-d-paths-red-final.log"
& $Py -m pytest -q tests/test_prospectus_publish.py tests/test_prospectus_cache.py -k 'stale_staging or default_output_root or compact_staging or actual_long_paths or interleaved_writers or stays_locked or atomic_write_failure' -p no:cacheprovider --basetemp "$Scratch\s1-green-temp" *> "$Scratch\task-d-paths-green.log"
```

GREEN:9passed88deselected, exit0, no warnings.

```powershell
& $Py -m pytest -q tests/test_prospectus_publish.py tests/test_prospectus_cache.py tests/test_prospectus_publication.py tests/test_prospectus_batch_skip.py -p no:cacheprovider --basetemp "$Scratch\s1-focused-temp" *> "$Scratch\task-d-paths-focused.log"
& $Py "$Scratch\s1_implemented_path_projection.py" *> "$Scratch\task-d-paths-projection.log"
```

Focused386passed in51.07s, exit0, no warnings. Actual44projection exit0, complete maxima above; helper writes only external scratch.

```powershell
& $Py -m pytest -q tests --ignore=tests/test_api_probes.py --ignore=tests/test_embedding_service.py -p no:cacheprovider --basetemp "$Scratch\s1-full-temp" *> "$Scratch\task-d-paths-full.log"
```

Main full:961passed/13subtests/3warnings in89.02s, exit0 (session18615 finished). Warnings are existing upstream deprecations for force_full_page_ocr, generate_table_images, and rec_font_path under test_tools_contract.py::ToolsContractTests::test_synthetic_pdf_fixture_exists_and_parses. Approved API/embedding exclusions remain explicit above; this is not the comprehensive environment suite. git diff --check passed.

## Review boundary

Changed six files: paths.py, publish.py, loader.py, tests/test_prospectus_publish.py, tests/test_prospectus_cache.py, plans/plan_current_progress/extractor_split_progress.md. Preserved preexisting dirty F4 postcommit/review checkpoints in progress. Self-review: minimal shared-prefix implementation; no dependency or path framework; no unrelated behavior changes.

GUI comprehensive suite, selftest80, semantic44comparer and trials: NOT RUN for S1, deferred final D gates. Separate parent specification/quality reviews pending. S2/S4/F5/final D gates/Task10 and downstream queue remain; Phase D is not complete.

Explicit six-path staging and required Claude coauthor trailer verified. Working tree was clean immediately after commit; postcommit checkpoint.py --progress leaves only plans/plan_current_progress/extractor_split_progress.md modified, intentionally preserved for the next task. No active pytest processes remain. Next: parent fresh specification review of the immutable range, then independent quality review.
