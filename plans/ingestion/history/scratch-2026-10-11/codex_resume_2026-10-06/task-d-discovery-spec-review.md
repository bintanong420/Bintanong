# Phase D F2 independent specification review

Reviewed range: 597e8c0289b8c090edf494248a9bd3fedad6aeb4..df5eec4bdf0d3b9f46addfce7911b00a705ec126
Seat: /root/d_discovery_spec. Read-only review of the phase-d checkout. The requesting-code-review/code-reviewer.md reviewer instructions were read and applied. No subagents, checkout/index/HEAD changes, installs, main writes, pushes, merges, or broad suite repeats.

## Requirements and strengths

The task brief, final F2 selected diagnostic-root ruling in preflight-ledger.md, approved_execution.md, remaining-fixes brief, package-split cross-phase rules, committed diff, actual caller code, tests, report, and recorded red/green/TUI/full evidence were reviewed.

For normal descendant glob results, batch.py:89-94 implements the approved rule directly: standard ignored names are checked only in root-relative directory components, failed is no longer globally excluded, and failure.json markers are checked from candidate parent through selected root. Marker payload parsing and a literal failed component are correctly absent. scan_pdfs remains the direct alias at batch.py:104. Explicit JSON patterns, duplicate-pattern deduplication, sorted results, and recursive/nonrecursive iterator selection are preserved.

Shared flow traced: batch.run_batch at batch.py:206; package export at __init__.py:19; isolated run at prospectus_batch.py:24; all four TUI scanner calls at tui.py:169,206,220,241. TUI configure accepts caller-supplied patterns at tui.py:188-189. No parallel filtering implementation was introduced.

Regression additions directly cover the originally reported descendant cases, selected failed/marked-run roots, marker-only unrelated names, nondiagnostic siblings, ignored absolute ancestors, filenames, requested JSON, and the alias. Existing diagnostics fixture now reflects the actual marker rather than merely naming its directory failed.

## Issues

### Critical
None.

### Important
1. Parent-traversing patterns allow the new marker predicate to inspect above the selected root.
   - File: backend/bintanong_tools/prospectus_extractor/batch.py:89 and :93-94; reachable user configuration at tui.py:188-189.
   - Root cause: Path.relative_to(root) is lexical. A path returned by root.glob('../*.pdf') is root/../course.pdf, so relative is ../course.pdf and relative.parent is '..'. The new predicate evaluates root / '..' / 'failure.json', which is outside the selected tree.
   - Requirement violated: the finalized controller ruling says to inspect marker parents within the selected tree and never above root. This is an actual supported caller input, not an invented API: arbitrary patterns are accepted by the shared scanner and TUI configuration. Existing external-file discovery through '..' predates this diff, but reading its above-root marker is introduced here.
   - Reproduction on the existing main Python in this Windows checkout: create outer/inputs as selected root and outer/course.pdf. scan_inputs(root, recursive=False, patterns=['../*.pdf']) returns root/../course.pdf. Add only outer/failure.json, leaving selected root unchanged: the same call now returns []. The only marker capable of changing this result is above root.
   - Impact: an unrelated parent marker changes the selected-root scan, contradicting the root boundary guarantee; callers can also discover a file outside the configured root.
   - Smallest coherent correction: enforce that candidate paths or accepted patterns cannot escape the selected root before any marker inspection. Reject parent-traversal patterns explicitly or normalize candidates and reject those outside root; keep one shared guard and add a regression using '../*.pdf' with an above-root marker. Do not patch every caller. Select a policy deliberately if normalization would also change existing link behavior.
   - Evidence: task-d-discovery-spec-probe.log records the one tiny targeted probe performed by this reviewer; task-d-discovery-spec-probe.py preserves the reproduction externally. No broad tests were rerun. The observed run used the listed Python with -B and the probe code piped on stdin from PowerShell; to replay the preserved script from the phase-d worktree, set $env:PYTHONPATH to the worktree root, then run & "C:/Users/Hawksprey/source/repos/Bintanong/backend/.venv/Scripts/python.exe" -B "E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_resume_2026-10-06/task-d-discovery-spec-probe.py". The recorded result is exit 0 with unmarked containing root/../course.pdf and marked above root returning [].

### Minor
None.

## Evidence assessment

Recorded evidence was inspected, not independently rerun: red log ends with 11 failed, 8 passed, 19 deselected; focused green ends with 48 passed in 27.97s; the preserved real TUI script patches only pause and its log shows exactly one legitimate failed/legitimate/failed.pdf, marked run excluded; main full ends with 928 passed, 13 subtests passed, 3 warnings in 100.25s. Warning text matches upstream Docling/Pydantic deprecations in test_tools_contract. Existing entrypoint tests do execute selftest subprocesses and assert 80/80; this does not convert the separately deferred standalone final gate into a current standalone run.

No claim of complete Phase D validation follows from F2. Complete GUI-review suite, standalone final selftest, corpus comparer, B2/C/trial gates were NOT RUN for this task and remain final-gate work as documented. Existing green evidence does not cover the confirmed parent-traversal case.

## Unresolved suspicions

None in the narrow reviewed F2 behavior; one concrete issue above remains unresolved. No additional probe or broad suite is justified before that issue is addressed.

## Actual Git state

Observed branch: feat/prospectus-phase-d-safe-cache.
Observed HEAD: df5eec4bdf0d3b9f46addfce7911b00a705ec126, matching reviewed tip.
Only dirty path: M plans/plan_current_progress/extractor_split_progress.md. The inspected unstaged diff contains the expected implementer/coordinator postcommit recovery checkpoints. Source/tests are clean; staged diff is empty. git diff --check for the reviewed range produced no whitespace failures. Commit trailer is Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>.

## Declined to judge

- F4 manifest/CSV line endings: explicitly separate queued work; no changed implementation in this range.
- F5 historical red-count correction: explicitly separate queued evidence work.
- S1 default output root and compact staging/temp names: explicitly separate queued work.
- S2 supplied-context skip eligibility: explicitly separate queued behavior work.
- S4 TUI skip wording and force toggle: explicitly separate queued behavior work.
- Final Phase D corpus/GUI/selftest/B2/C/trial gates and Task10: explicitly separate queued gates; this review does not replace them.
- Marker payload authenticity and whether an unrelated user failure.json should be diagnostic: finalized ruling explicitly approves marker-only classification and its cost, so payload parsing is not an omitted F2 requirement.
- Existing symlink/junction traversal policy and concurrent filesystem/marker changes: not changed by this narrow diff and not exercised; no assurance about those policies is issued here. They must not be silently expanded while fixing the confirmed parent-traversal marker boundary.
- Existing stale TUI last_scan behavior or direct single-file processing bypassing discovery: existing caller behavior outside the requested discovery filter; no separate workflow redesign judged here.

## Verdict

CHANGES_REQUIRED. The main descendant cases match the specification, but the new marker check violates the explicit selected-root boundary for a real accepted pattern. Resolve the single Important finding and preserve targeted red/green evidence before this spec seat can approve F2. Independent quality review remains a separate gate.
