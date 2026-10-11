# Phase D F5 and Tasks 8/9/10 report

Status: DONE for implementation-only documentation and required final runtime gates. Controller's whole-range specification and independent quality reviews remain **PENDING**. Phase D is not fully complete. Recorded 2026-10-06T23:37:16+08:00 (Asia/Manila); documentary commit details appended below after commit.

## Immutable scope and Git state

- Worktree: `C:\Users\Hawksprey\source\repos\Bintanong-wt\phase-d`; branch `feat/prospectus-phase-d-safe-cache`.
- Approved pickup/comparer base: `641523d212839084da03d966ffbfca66c7e83e42`.
- Reviewed production tip: `c40a38c9f633dd085766ca11f81f0dd3890810cc`; no production/test changes in this batch.
- Original implementation base: `189c9eaf453da9a4e7bb5471133a9cf864316012`.
- Main checkout remains `58d4bb681fed946128e4b86aa19e49a60f030f3e` with pre-existing `.gitignore` modification and untracked historical handoff preserved. No main checkout/index/branch/venv operation was performed.
- Initial sole dirty worktree file was `plans/plan_current_progress/extractor_split_progress.md` containing postcommit/review checkpoints. All preserved and included.
- Exact authorized commit files: `docs/decisions/prospectus-cache-and-publication.md`, `plans/plan_current_progress/extractor_split_progress.md`, `plans/plan_current_progress/current_progress.md`.
- Retained baseline worktree `C:\Users\Hawksprey\source\repos\Bintanong-wt\d-baseline-641523d`, detached at the exact base. Existing comparer does not remove it. No worktree removal, push, dev merge or artifact cleanup.

## Environment and commands

PowerShell from the phase-d worktree. Existing main interpreter (`MAINPY`) is `C:\Users\Hawksprey\source\repos\Bintanong\backend\.venv\Scripts\python.exe`; existing comprehensive interpreter (`GUIPY`) is `$env:TEMP\gui-review-venv\Scripts\python.exe`. GUIPY Python 3.13.5, Docling 2.129.0, docling-core 2.97.1, docling-parse 7.20.0, FastAPI 0.141.1, pytest 9.1.1. No installs, model downloads requested, dependency changes or main-venv synchronization. Installed models used for real CPU conversion.

Exact fresh commands (all quoted paths; stdout/stderr retained under this external directory):

```powershell
& "$env:TEMP\gui-review-venv\Scripts\python.exe" -m pytest -q 'tests' -p no:cacheprovider --basetemp 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\d-final-comprehensive-temp'
& 'C:\Users\Hawksprey\source\repos\Bintanong\backend\.venv\Scripts\python.exe' 'backend\bintanong_tools\bintanong_jsonifer_prolog\bintanong_prospectus_jsonifier.py' --self-test
& 'C:\Users\Hawksprey\source\repos\Bintanong\backend\.venv\Scripts\python.exe' 'scripts\prospectus_course_compare.py' --golden 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\docling_jsonified_output\task2b_standing_isolated_2026-09-29' --work 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\d-final-compare' --base-ref '641523d' --worktree 'C:\Users\Hawksprey\source\repos\Bintanong-wt\d-baseline-641523d' --semantic-doc 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\PalSU Undergraduate Prospectus Website Dump\Tiniguiban - Main\palsu_main_undergrad_program_college_meaning.md' --status-report --jobs 6
& 'C:\Users\Hawksprey\source\repos\Bintanong\backend\.venv\Scripts\python.exe' -m pytest -q 'tests\test_prospectus_publication.py' 'tests\test_prospectus_publish.py' 'tests\test_prospectus_input_snapshot.py' 'tests\test_prospectus_batch_skip.py' -p no:cacheprovider --basetemp 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\d-final-focused-temp'
& 'C:\Users\Hawksprey\source\repos\Bintanong\backend\.venv\Scripts\python.exe' 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\task-d-final-real-gates.py'
& 'C:\Users\Hawksprey\source\repos\Bintanong\backend\.venv\Scripts\python.exe' 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\task-d-final-corpus-gates.py'
& 'C:\Users\Hawksprey\source\repos\Bintanong\backend\.venv\Scripts\python.exe' 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\task-d-final-path-projection.py'
```

Each command redirected to `task-d-final-<gate>.log`, then recorded `$LASTEXITCODE` in its matching `.exit` file. All seven completed with exit 0. The real runner records each actual subprocess argument list, return code, manifest summary and skip record in `task-d-final-real-results.json` and per-run logs. Its internal corrupt-PDF command intentionally exits 1.

## Gate results

| Gate | Actual result | Evidence |
| --- | --- | --- |
| Fresh comprehensive, all tests including API/embedding | 990 passed, 13 subtests, 5 warnings; exit 0 | `task-d-final-comprehensive.log/.exit` |
| Unchanged-tip main subset, reused with approved ignores | 984 passed, 13 subtests, 3 warnings; original run 94.15 seconds | `task-d-s4-full.log`, S4 report and production-tip review |
| Fresh compatibility-shim self-test | 80/80; exit 0 | `task-d-final-selftest.log/.exit` |
| Fresh focused publish/publication/snapshot/skip | 394 passed; exit 0 | `task-d-final-focused.log/.exit` |
| Full replacement-interruption matrix within fresh focused/full runs | 180 cases: 9 replacement steps × before/after × changed/identical companions × 5 conversion changes | `tests/test_prospectus_publication.py::test_interruptions_only_verify_a_coherent_generation` and focused log |
| Fresh comparer, base 641523d | 44/44 course/audit-field identity; exit 0 | `task-d-final-compare.log/.exit`, `d-final-compare/{old,new}` |
| Fresh original-PDF B2 helper | health mixed 21 / warnings_only 3 / broken 19 / clean 1; title_from_pdf 67, strip_banner 0; unclaimed_code 316, banner_leak 3 | `task-d-final-corpus.log`, `task-d-final-corpus-results.json` |
| Direct candidate Phase C state counts (no missing-field fallback) | blank_unreviewed 1005, resolved 689, unresolved_reference 253, standing_condition 59, unreadable 20, alternative_or_exception 3, stated_none 2 | corpus runner/results and comparer log |
| Trial 01 Architecture, 16 BSBA-HRM, 33 BSCS | `check_against` 0 errors each | corpus log/results |
| Real PDF conversion/failure/skip/snapshot/cleanup | all assertions passed | real runner/results/logs below |
| Path-only default-root projection with actual staging/temp generation | 44 paths; final 181, stage 226, temp 161, diagnostics 251; all <260; no home writes | `task-d-final-path-projection.py/.log/.json/.exit` |

The fresh GUI environment's two additional upstream warnings are Starlette's httpx deprecation and anyio BlockingPortal alias deprecation. The three existing Docling/Pydantic warnings are force_full_page_ocr, generate_table_images and RapidOCR rec_font_path. No warnings were silently removed or counted as failures. Course equivalence proves regression stability, not original-PDF source accuracy. Markup inspection observed 44 files with data-gap, 9 with unplaced cells, largest 25,543 bytes. Payload diffs were limited to added run_identity.cache_files/skip_reusable and changed package_sha256/run_key, each in 44 payloads.

## Fresh real Task 9

Source: institutional `BSE-Franchising-and-Trading-for-student-new-version.pdf`, copied to external short `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\dg\in\target.pdf`. Only the copy was mutated. Output is `scratch\dg\out`. Real installed Docling CPU conversion used the production CLI and semantic map. Args are exact in the real runner and JSON results; A-D have `--batch --skip-existing --export-all --device cpu`; E adds `--force`.

| Run | Observed batch line | Exit / assertion |
| --- | --- | --- |
| A real conversion | 1 extracted, 0 failed audit, 0 skipped, 0 errored | 0; WARN, 53 courses, 159 units; nine published/cache files |
| B unchanged | 0 extracted, 0 failed audit, 1 skipped, 0 errored | 0; exact `identical run identity`; nine hashes unchanged |
| C corrupt scratch PDF | 0 extracted, 0 failed audit, 0 skipped, 1 errored | 1; `ConversionError`, traceback present; nine hashes unchanged; no `.s-*` residue |
| D restore source copy | 0 extracted, 0 failed audit, 1 skipped, 0 errored | 0; prior files unchanged; diagnostics still present |
| E forced real conversion | 1 extracted, 0 failed audit, 0 skipped, 0 errored | 0; diagnostics cleared |

A real cached parse was then wrapped at build_payload only to change the scratch input after parsing. The copy retained original byte length and restored original nanosecond mtime; the final input comparison refused with `Input bytes changed since capture`. All prior files remained unchanged and explicit failure diagnostics existed. Restoring the bytes and successfully publishing from the matching cache recorded `cache='reused'` and cleared diagnostics. No production converter/parser/build function was replaced with a fake for these parses.

The historical Task 9 Marine Biology and Social Work error pilots remain historical observations; their conversions were **NOT RUN fresh** in this batch. Their audit-error behavior is covered by fresh production tests, without inventing new real-pilot evidence. Arbitrarily deep explicit roots and longest-filename real conversion were **NOT RUN**; the approved alternative is fresh default-root path-only regression, with unchanged final filenames.

Original fixture snapshots: 101 files (44 original corpus PDFs, 44 cached inputs, original semantic map and all files in the three trial folders) in `task-d-final-originals-before.json`, `task-d-final-originals-after.json` and `task-d-final-originals-post-corpus.json`. Exact equality was checked around the real workflow and before/after original-PDF/trial helper execution. The comparer started read-only before the first snapshot; no original before-comparer hash timing is claimed. No institutional original/source candidate/sheet was mutated.

## F5 correction and documentary changes

Frozen `f802c764533bdf67267089bcc109416da5941ca9` publication tests contain 14 test functions. Corrected the Task 6 progress count from 15 to 14 and replaced inconsistent 11-failed/2-passed wording with honest provenance. Authentic original red log unavailable. Controller's existing reconstruction archives parent `29eb83200b593f24caa9179a28c0795c30621b5a` and overlays f802c76 tests/conftest; saved log observes 12 failed, 2 passed. This is **reconstructed** pre-fix evidence, not original chronological runtime proof. Existing reconstruction script/log were read, not rerun. Historical combined 61 remains unchanged and is explicitly not established by this reconstruction. Original plans and full review/checkpoint history preserved.

Decision/current progress documents cover all approved D1-D6/rulings, snapshots and DocumentStream fallback/wrapper, publish-v2 exact cache/main identity/order, prepublication preservation versus midpublication detection, known-only cleanup, marker/root-relative discovery and glob boundaries, LF/BOM supported CSV behavior, skip_reusable and TUI force, default-root migration without moves, final32-digit stage digest and path limits, explicit review-only/unapproved outputs and single-writer assumption.

## Processes and recovery

- Comprehensive exec session 3794: pwsh 59168, venv Python 7224, runtime Python 12928; completed.
- Comparer exec session 77546: pwsh 9624, venv Python 64636, runtime Python 20208 and extractor children; completed.
- Real exec session 10471: runtime PID 19512, per-run conversion children; completed.
- Focused exec session 55195; completed.
- Detailed launch snapshot: `task-d-final-processes.json`; sessions/log paths/next actions are recorded through checkpoint.py/events.jsonl. `.exit` markers disambiguate finished commands from incomplete logs.
- Exact resume: read `CLAUDE_TAKEOVER.md`, this report and `checkpoint.json`; confirm no PID remains using `Get-CimInstance Win32_Process`; inspect `task-d-final-*.exit`; inspect phase-d HEAD/status. All runtime gates passed; do not relaunch them absent a code change, failure or new concern. Proceed to separate whole-range specification then quality review of `641523d..documentary commit`.

Required checkpoint.py was called at preflight, after launches, after gate completion and before commit, using owner `/root/d_final_gates`; task-boundary calls use `--progress`. Postcommit call deliberately leaves only progress dirty for controller pickup. No worker-spawned agents.

## Remaining gates

Whole-range D specification/quality reviews are **PENDING** and belong to controller's independent seats. The batch reports implementation-only DONE and does not mark Phase D fully complete. GUI integration/review and human trial, Phase E, Phase F/container checks, OCR real-photo evidence and formal Phase 1/2 preparation remain in the authorized queue. No source-owner approval, active curriculum/RAG/Prolog release, numbered-phase completion or human trial verdict is asserted.

## Final commit and pickup (2026-10-06 Asia/Manila)

- Documentary commit: 08a8290d7257485d695c4d2b05be5cf6db730d7b; exact three authorized paths, required final Claude trailer verified. Exact command: git commit -m 'docs: record the safe cache and output publication design and its evidence' -m 'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>'.
- Full controller review range: 641523d212839084da03d966ffbfca66c7e83e42..08a8290d7257485d695c4d2b05be5cf6db730d7b; specification and quality PENDING. Production/scripts/tests diff c40a38c..08a8290 is empty. Clean immediately after commit; required postcommit checkpoint deliberately leaves only M plans/plan_current_progress/extractor_split_progress.md.
- Retained baseline HEAD641523d212839084da03d966ffbfca66c7e83e42; main remains58d4bb681fed946128e4b86aa19e49a60f030f3e with only original .gitignore and historical handoff dirty/untracked. End-of-batch hashes for those two files are task-d-final-main-preserved-hashes.json, unchanged across commit; these are not claimed as initial pre-worker hashes.
- Precommit document/evidence assertions passed: all seven .exit markers0; all101originalhashes still match; decision count/eligibility/PENDING assertions; unstaged and cached git diff --check both passed. No final gate Python process remains.
- Tooling correction: an incidental Python -c formatting command exited1 with SyntaxError from literal newline escaping, before any statement executed. It was replaced by apply_patch. A temporary whole-file LF normalization exposed historical trailing whitespace in current_progress.md during git diff --check; the original historical prefix was restored byte-exact from HEAD and only the new appendix uses LF. Final diff checks pass. Neither event changed production or invalidated a runtime gate.
- Main dirtyfile hashes, originalsource hashes, all environment/runtime/evidence files remain external. This documentation-only batch did not require a new production red test. F5 reconstruction was not rerun.
