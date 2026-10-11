# Phase D F2 discovery implementation report

Status: DONE for scoped F2 implementation; independent parent reviews pending. Scope ONLY F2. Base: 597e8c0289b8c090edf494248a9bd3fedad6aeb4. Worktree C:/Users/Hawksprey/source/repos/Bintanong-wt/phase-d.

## Implementation and shared flow
scan_inputs now filters standard ignored names only in path.relative_to(root).parts[:-1]. Absolute ancestors and filenames cannot accidentally suppress inputs. Blanket failed exclusion removed. failure.json in a candidate directory or its ancestors up to/inclusive selected root marks the diagnostic subtree; nothing above root is inspected. Marker contents are not parsed. scan_pdfs is the direct shared alias. run_batch, all four TUI scan calls, and prospectus_batch.run_isolated route through this scanner; no separate caller patches required.

Controller ruling: selected output/failed and a marked per-run folder must exclude diagnostic files. No literal failed component required. A user folder containing failure.json is intentionally classified diagnostic until marker removed; that is the explicit marker rule's cost, not a claim that payload contents establish ownership.

18 new parametrized regression cases cover failed/FAILED and standard ignored-looking absolute ancestors; requested .git filename; failed.pdf; recursive/nonrecursive PDF and explicitly requested cached Docling JSON scanning; duplicate requested patterns; nested legitimate failed inputs; standard ignored subdirectories; diagnostics and nested descendants; legitimate sibling/direct inputs; selected failed root, marked run root and marker-bearing unrelated-name root; markers above selected root ignored. Existing diagnostics fixture now includes the actual failure.json marker.

## TDD and observed command evidence
All commands run from the worktree with MAIN_PY C:/Users/Hawksprey/source/repos/Bintanong/backend/.venv/Scripts/python.exe, PYTHONDONTWRITEBYTECODE=1 and external temporary roots. No dependency install/sync.

RED (production unchanged):
MAIN_PY -m pytest -q tests/test_prospectus_batch_skip.py -k 'test_scan' -p no:cacheprovider --basetemp 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_resume_2026-10-06/d-discovery-red-tmp'
Observed exit1: 11 failed, 8 passed, 19 deselected in1.04s. Log task-d-discovery-red.log. All failures were assertion failures: four ignored-looking absolute ancestor cases, two filename/nested legitimate-input cases, two marker-bearing subtree/nondiagnostic sibling cases, three selected-root marker cases. No collection errors. Expected root cause: baseline absolute path parts filter and blanket failed exclusion, plus no marker detection outside failed names.

Focused GREEN:
MAIN_PY -m pytest -q tests/test_prospectus_batch_skip.py tests/test_prospectus_batch.py tests/test_prospectus_entrypoints.py -p no:cacheprovider --basetemp 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_resume_2026-10-06/d-discovery-green-tmp'
Observed exit0: 48 passed in27.97s, no warnings. Log task-d-discovery-green.log. Entry-point tests include their self-test subprocess assertions; no separate standalone final-gate selftest command was run.

Real TUI integration smoke:
PYTHONPATH=worktree MAIN_PY 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_resume_2026-10-06/task-d-discovery-tui-check.py'
Observed exit0: ProspectusTUI.scan found exactly the legitimate failed/legitimate/failed.pdf beneath an absolute FAILED ancestor and excluded the sibling marked diagnostic run. Only pause was mocked to avoid interactive input; discovery was real. Script and task-d-discovery-tui.log preserved externally.

Main full suite:
MAIN_PY -m pytest -q tests --ignore=tests/test_api_probes.py --ignore=tests/test_embedding_service.py -p no:cacheprovider --basetemp 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_resume_2026-10-06/d-discovery-full-tmp'
Observed exit0: 928 passed, 13 subtests passed, 3 warnings in100.25s. task-d-discovery-full.log. All warnings are upstream Docling/Pydantic deprecations from tests/test_tools_contract.py::ToolsContractTests::test_synthetic_pdf_fixture_exists_and_parses (force_full_page_ocr, generate_table_images/TableItem.get_image, rec_font_path). No failures or collection errors.

Complete GUI-review-venv suite: NOT RUN for this task, deferred to final Phase D gates. Standalone final-gate selftest: NOT RUN for this task, deferred to final Phase D gates. Prior counts are not current task evidence. Real corpus comparer/B2/C/trial gates: NOT RUN for this task, parent-owned final Phase D gates.

## Changed files and self-review
backend/bintanong_tools/prospectus_extractor/batch.py: six lines added/two removed, shared root-relative and marker predicate only.
tests/test_prospectus_batch_skip.py: one existing marker fixture correction, eighteen new cases.
plans/plan_current_progress/extractor_split_progress.md: preserved preexisting controller F1 review checkpoints and added F2 checkpoints/progress.

Self-review: shared callers and alias traced, no new dependency/helper/config/payload parsing, no publication/identity/schema/default-path changes. git diff --check passed; Git emits existing autocrlf informational warnings for LF files, no diff whitespace failures. Python pathlib writes source/progress/evidence LF. No main checkout edits, generated repo artifacts, push, branch switch, merge, worktree removal or preserved-file cleanup.

## Remaining work
Parent independent F2 specification then quality review. F4/F5/S1/S2/S4, final Phase D gates and Task10 remain queued. This report does not claim Phase D complete. Commit/range/status will be appended after full verification and commit.

## Final commit and handoff
Commit: df5eec4bdf0d3b9f46addfce7911b00a705ec126 — fix(prospectus): scope discovery exclusions to selected inputs
Review range: 597e8c0289b8c090edf494248a9bd3fedad6aeb4..df5eec4bdf0d3b9f46addfce7911b00a705ec126
Commit trailer verified: Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>.
Only the three explicit files were staged. Worktree was clean immediately after commit. Required post-commit checkpoint --progress leaves only:
M plans/plan_current_progress/extractor_split_progress.md
That final recovery entry is intentionally preserved for the parent's next focused progress commit; no source/test changes remain dirty. No commands/sessions remain active. Self-review found no unresolved scoped implementation issue; parent independent review gate is still pending. Phase D is not complete.

## Specification repair round1 — glob root boundary
Base df5eec4bdf0d3b9f46addfce7911b00a705ec126. Parent report task-d-discovery-spec-review.md identified an Important concrete failure: relative_to(root) is lexical, so root.glob('../*.pdf') returns root/../course.pdf and the new marker check can observe outer/failure.json. Reproduced original task-d-discovery-spec-probe.py on existing Python exit0; task-d-discovery-repair-reproduction.log retains exact unmarked external file vs marked-above-root empty result. Original probe/script/log preserved unchanged.

Ruling: patterns must be root-relative, without any parent-directory component. One shared PureWindowsPath lexical guard rejects anchors (rooted, drive-relative, drive-absolute and UNC) and '..' components with ValueError("Input pattern must stay within input root: ...") before invoking that pattern's glob. It recognizes both separators consistently across platforms. Even a parent component that might later normalize inside root is rejected; there is no outside traversal/normalization, caller patch, generic framework, new config, payload parsing or symlink/junction policy change. Controller confirmed PureWindowsPath stdlib guard as the portable Windows-origin contract.

New tests: 18 recursive/nonrecursive malformed-pattern cases for '../*.pdf', nested/../../, their backslash equivalents, slash/backslash rooted paths, drive-relative C:*.pdf, absolute-drive paths and UNC paths. Each case checks rejection with and without an above-root failure.json. Six valid relative glob cases cover nested/*.pdf, n*/*.pdf and **/*.pdf in both modes. Prior legitimate failed, diagnostic, ignored ancestor, filename and requested JSON cases remain.

Repair RED (production unchanged):
MAIN_PY -m pytest -q tests/test_prospectus_batch_skip.py -k 'test_scan_rejects_patterns or test_scan_preserves_valid_relative_globs' -p no:cacheprovider --basetemp 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_resume_2026-10-06/d-discovery-repair-red-tmp'
Exit1: 18 failed, 6 passed, 38 deselected in0.63s. Expected failures were accepted parent traversal (did not raise ValueError) and pathlib NotImplementedError for anchored patterns instead of the clear scanner ValueError. Log task-d-discovery-repair-red.log. No collection errors.

Repair focused GREEN:
MAIN_PY -m pytest -q tests/test_prospectus_batch_skip.py tests/test_prospectus_batch.py tests/test_prospectus_entrypoints.py -p no:cacheprovider --basetemp 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_resume_2026-10-06/d-discovery-repair-green-tmp'
Exit0: 72 passed in16.12s, no warnings. Log task-d-discovery-repair-green.log.

Repair probe:
PYTHONPATH=worktree MAIN_PY -B 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_resume_2026-10-06/task-d-discovery-repair-probe.py'
Exit0: all four recursive/nonrecursive, parent marker absent/present combinations reject '../*.pdf' with the specified ValueError. Script and task-d-discovery-repair-probe.log retained externally.

Repair main full:
MAIN_PY -m pytest -q tests --ignore=tests/test_api_probes.py --ignore=tests/test_embedding_service.py -p no:cacheprovider --basetemp 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_resume_2026-10-06/d-discovery-repair-full-tmp'
Observed exit0: 952 passed, 13 subtests passed, 3 warnings in82.25s. task-d-discovery-repair-full.log. Same upstream Docling/Pydantic deprecations from test_tools_contract synthetic PDF test; no failures or collection errors. Complete GUI-review suite, standalone final-gate selftest, corpus/B2/C/trials: NOT RUN for repair; unchanged scanner-only scope and final Phase D gates remain controller-owned. Entry-point tests execute their own selftest assertions, not a separate final-gate run.

Self-review: only batch.py's import and three-line guard, tests and preserved progress checkpoints changed. All shared callers still route through scan_inputs; valid glob behavior and direct alias unchanged. git diff --check passed. Source/evidence written LF with pathlib; no repo artifacts, installs/sync/maincheckout changes/push/devmerge/worktree cleanup. This repair resolves the demonstrated pattern traversal rather than changing symlink behavior. Separate parent specification re-review then quality review pending.

Repair commit: 4a0cdb794a337b9cc91846d16585478c3bb5fde0 — fix(prospectus): reject glob patterns outside input root
Repair range: df5eec4bdf0d3b9f46addfce7911b00a705ec126..4a0cdb794a337b9cc91846d16585478c3bb5fde0
Updated F2 immutable review range: 597e8c0289b8c090edf494248a9bd3fedad6aeb4..4a0cdb794a337b9cc91846d16585478c3bb5fde0
Status: DONE for repair implementation; parent same-seat specification re-review then independent quality review pending. Required Claude Opus5.5 trailer verified. Only three explicit changed files staged; worktree clean immediately after commit. Required postcommit --progress leaves only M plans/plan_current_progress/extractor_split_progress.md. No source/test changes dirty; no commands/sessions running. Complete GUI-review/standalone final selftest NOT RUN for this repair, no prior counts reused as current. Remaining F4/F5/S1/S2/S4/final gates/Task10 untouched; no Phase D completion claim.
