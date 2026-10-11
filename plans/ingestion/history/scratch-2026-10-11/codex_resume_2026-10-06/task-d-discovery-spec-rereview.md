# Phase D F2 independent specification re-review

Seat: /root/d_discovery_spec. Updated immutable reviewed range: 597e8c0289b8c090edf494248a9bd3fedad6aeb4..4a0cdb794a337b9cc91846d16585478c3bb5fde0.
Repair delta independently reviewed: df5eec4bdf0d3b9f46addfce7911b00a705ec126..4a0cdb794a337b9cc91846d16585478c3bb5fde0.
Original task-d-discovery-spec-review.md CHANGES_REQUIRED verdict and original probe/script/log remain intact. This separate re-review supersedes its open finding only for the repaired tip.

## Finding resolution and strengths

The Important finding at old batch.py:89,93-94 is RESOLVED. The new shared guard at backend/bintanong_tools/prospectus_extractor/batch.py:85-87 uses PureWindowsPath to reject any anchor or '..' component with explicit ValueError before that pattern reaches glob/rglob. It recognizes slash/backslash parent components, rooted, drive-relative, drive-absolute and UNC patterns. This prevents the demonstrated lexical root/../course.pdf result from reaching marker inspection above root. It rejects even parent paths that could normalize back inside root, consistent with the finalized pattern contract documented in the repair report/progress.

This is the smallest coherent shared correction: one stdlib import and three guard lines, with no caller patches, normalization, link-resolution policy change, new dependency, configuration or abstraction. Current root-relative directory filtering at batch.py:92-93 and marker predicate at :96-97 retain the original approved F2 behavior for descendant patterns. Selected diagnostic root detection, legitimate failed folders/siblings, requested JSON, filename handling, standard ignored directories, sorted deduplication and recursive/nonrecursive scanning remain preserved.

Actual shared callers still route through scan_inputs: run_batch at batch.py:209; direct alias scan_pdfs at :107; isolated run at prospectus_batch.py:24; TUI calls at tui.py:169,206,220,241. The accepted TUI patterns therefore receive the same explicit guard.

## Tests and proof

Read updated task-d-discovery-final-review-package.md, task-d-discovery-report.md repair section, repair reproduction/red/green/probe/full logs, committed production/test diff, and actual Git state. The 18 malformed-pattern cases cover both recursion modes and repeat with/without an above-root failure.json. Six accepted relative-glob cases verify nested/*.pdf, n*/*.pdf and **/*.pdf in both modes. Earlier F2 regressions remain in the focused set.

Inspected recorded repair evidence (not independently rerun):
- RED: 18 failed, 6 passed, 38 deselected in 0.63s; accepted traversal and pathlib NotImplementedError mismatches reproduce the behavior gap, without collection errors.
- Focused GREEN: 72 passed in 16.12s, no warnings.
- Implementer repaired probe: all four recursive/nonrecursive and above-root-marker absent/present combinations reject '../*.pdf' with the intended ValueError.
- Main full: 952 passed, 13 subtests passed, 3 warnings in 82.25s. Warning text is the same upstream Docling/Pydantic synthetic-PDF deprecation set. The two approved API/embedding ignores remain documented.

Independent targeted confirmation in this re-review: from the phase-d worktree, existing main Python with -B read a PowerShell-piped stdin snippet invoking runpy.run_path on the unchanged external task-d-discovery-repair-probe.py. It ran only the four-combination original traversal probe, exited 0, and emitted four explicit rejections plus Traversal repair probe PASS. Independent output is preserved in task-d-discovery-spec-rereview-probe.log beside this report. No broad suite was repeated. This reproduces the original failure's exact '../*.pdf' trigger and proves the above-root marker no longer changes acceptance.

Complete GUI-review suite, standalone final-gate selftest, corpus comparer/B2/C/trial gates were NOT RUN for this scanner repair and remain separate final gates. Entrypoint tests' selftest subprocess assertions do not substitute for a separately observed standalone final-gate command. No Phase D completion claim is made.

## Issues and unresolved suspicions

Critical: none. Important: none. Minor: none. Unresolved suspicions within the narrow F2 spec scope: none. The original finding is resolved by committed code and executable regression coverage.

## Actual Git state and review discipline

Observed HEAD: 4a0cdb794a337b9cc91846d16585478c3bb5fde0, matching reviewed tip.
Observed branch: feat/prospectus-phase-d-safe-cache.
Only dirty path: M plans/plan_current_progress/extractor_split_progress.md; inspected unstaged content is the expected implementer/coordinator postcommit checkpoints. Source/tests are clean, staged diff is empty. git diff --check for the complete reviewed range passed. Required Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com> trailer verified.

Read-only checkout review: no repository/index/HEAD mutations, subagents, installs, main writes, push, merge, worktree removal or broad-suite repetition. Only the distinct re-review report and independent tiny-probe log were written to approved external scratch; temporary probe inputs were external and removed automatically.

## Declined to judge

- F4 manifest/CSV line endings: explicitly separate queued work, unchanged by this range.
- F5 historical evidence/count correction: explicitly separate queued work.
- S1 default output root and compact staging/temp paths: explicitly separate queued work.
- S2 supplied-context skip eligibility: explicitly separate queued work.
- S4 TUI skip wording and force toggle: explicitly separate queued work.
- Final Phase D corpus/GUI/selftest/B2/C/trial gates and Task10: separate queued gates; this scanner spec review does not replace them.
- Marker authenticity/payload parsing: explicit marker-only classification and its cost are approved; no payload ownership guarantee is inferred.
- Existing symlink/junction traversal policy and concurrent filesystem changes: unchanged and outside this exact pattern repair; no link-policy assurance or expansion is issued here.
- Existing stale TUI last_scan behavior or direct single-file processing bypassing discovery: unchanged workflow outside this narrow discovery specification.

## Verdict

APPROVED for scoped F2 at 4a0cdb794a337b9cc91846d16585478c3bb5fde0. The single Important finding is resolved, the original root-relative diagnostic behavior is preserved, and no unresolved scoped spec issue remains. Independent quality review of the same immutable range remains required before the parent closes F2; F4/F5/S1/S2/S4 and final Phase D gates remain queued.
