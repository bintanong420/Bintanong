# Phase D F2 independent quality review

Seat: /root/d_discovery_quality. Read-only quality review after the repaired specification verdict APPROVED.

Reviewed BASE: 597e8c0289b8c090edf494248a9bd3fedad6aeb4.
Reviewed TIP: 4a0cdb794a337b9cc91846d16585478c3bb5fde0.
Repair delta: df5eec4bdf0d3b9f46addfce7911b00a705ec126..4a0cdb794a337b9cc91846d16585478c3bb5fde0.
Worktree: C:/Users/Hawksprey/source/repos/Bintanong-wt/phase-d.

## Review basis

Read task-d-discovery-final-review-package.md, task-d-discovery-brief.md, task-d-discovery-report.md including the repair, task-d-discovery-spec-rereview.md, preflight-ledger.md including the F2 selected-root ruling, approved_execution.md and the remaining-task scope. Applied the requesting-code-review/code-reviewer.md reviewer template, including its explicit declined-to-judge requirement.

Inspected the actual committed scanner/test diff, full scanner surrounding behavior, batch/isolated/CLI/TUI consumers, diagnostics marker creation, test assertions and recorded red/green/full/TUI evidence. Reviewed the complete range's progress-document changes and the expected unstaged recovery checkpoints. This is a separate quality seat; the specification verdict was evidence, not a substitute for reading production code and tests.

## Strengths

- Root-cause correction is in the shared scan_inputs function. The direct scan_pdfs alias at backend/bintanong_tools/prospectus_extractor/batch.py:107, run_batch at :209, prospectus_batch.run_isolated at backend/bintanong_tools/prospectus_batch.py:24, and TUI scan calls at backend/bintanong_tools/prospectus_extractor/tui.py:169,206,220,241 all use it. No duplicate caller filters or new abstraction were introduced.
- The lexical guard at batch.py:85-87 rejects Windows-origin anchors and exact parent components before the offending pattern reaches glob/rglob. The explicit ValueError states the invalid-pattern boundary. A rejected scan does not return a partial source list or start batch publication. Missing/non-directory root failures remain explicit at :78-81.
- Directory filtering at batch.py:92-93 uses only root-relative directory components. It preserves requested filenames and inputs below ignored-looking absolute ancestors, while retaining the existing standard-directory list. Removing blanket failed suppression directly fixes the legitimate-input loss.
- The marker parent chain at batch.py:96-97 is bounded by lexical root-relative parents, including the selected root. With the repaired pattern contract, it cannot produce the old root/../ ancestor chain. It suppresses a marked run and descendants without suppressing unmarked siblings; marker detection does not depend on a literal failed directory. The actual publisher writes failure.json, matching the regression fixture.
- Tests at tests/test_prospectus_batch_skip.py:210-321 use actual temporary files and scanner outputs, rather than mocking discovery or asserting the implementation's internal expressions. They cover the source-loss failures, direct alias, sorted deduplication, requested JSON/filename patterns, marked descendant and selected-root boundaries, malformed patterns in both recursion modes, and accepted descendant globs. The repair tests match ValueError and its message, so a pathlib NotImplementedError or silently accepted traversal would fail.
- The production delta is one standard-library import, one shared pattern guard, and two scoped predicates. Existing ordering, deduplication, alias, glob operation and caller architecture remain intact. No speculative cache, helper/configuration layer, normalization, payload parser or dependency was added.

## Evidence and targeted concern probe

Inspected existing repair logs; did not repeat broad tests:
- Repair RED: 18 failed, 6 passed, 38 deselected in 0.63s. Failures are the real accepted-traversal/exception-type gaps, with no collection errors.
- Focused GREEN: 72 passed in 16.12s, no warnings.
- Main full: 952 passed, 13 subtests passed, 3 upstream Docling/Pydantic deprecation warnings in 82.25s. The two approved API/embedding ignores remain in the recorded command.
- Earlier external TUI smoke uses real discovery and mocks only the interactive pause; it retains the legitimate failed.pdf and excludes the marked sibling run. The guard repair does not change that accepted pattern path.
- The separate repaired-spec seat independently confirmed the original '../*.pdf' trigger in four recursion/above-root-marker combinations.

One independent quality concern needed a tiny probe: Windows trailing spaces/dots might be interpreted by native I/O differently from PureWindowsPath's lexical components. From this worktree, existing main Python -B executed a PowerShell-piped snippet with external TemporaryDirectory inputs. It tested '.. /*.pdf', '.../*.pdf', '.. ./*.pdf', and '. /*.pdf' in both recursion modes, with a real outside.pdf above inputs and inside.pdf within inputs. All eight observations returned an empty list; no outside candidate was returned and no exception occurred. Exit 0. Output preserved in task-d-discovery-quality-path-probe.log. This clears the concrete suspicion on the observed Windows/Python environment; it is not a new universal filesystem or link-policy guarantee. Temporary inputs were removed automatically. No broad suite was repeated.

## Issues

Critical: none.
Important: none.
Minor: none.
Concrete severity/file-line/reproduction findings requiring repair: none.
Unresolved suspicions within this narrow F2 change: none. The possible Windows lexical/native discrepancy above was probed and not reproduced.

## Git state and review discipline

Observed HEAD matches TIP: 4a0cdb794a337b9cc91846d16585478c3bb5fde0.
Observed branch: feat/prospectus-phase-d-safe-cache.
Only dirty path: M plans/plan_current_progress/extractor_split_progress.md, with expected implementer/coordinator postcommit checkpoints including the active quality seat. Source/tests are clean; staged diff is empty. Complete-range git diff --check passed. Both focused commit trailers include the required Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>.

No checkout/index/HEAD mutation, subagents, installs, main-checkout writes, push, dev merge, worktree removal or preserved-file cleanup. Only this external report and the external tiny-probe log were written by this reviewer. No command/session remains running.

## Declined to judge

- F4 manifest/CSV line endings: separate queued behavior, unchanged by this range.
- F5 historical evidence/count correction: separate queued documentation work.
- S1 output-root and staging/temp path length policy: separate queued work; discovery does not change it.
- S2 supplied-context skip eligibility and the preexisting loose skip-reason assertion: explicit separate queued work, unrelated to scanner filtering.
- S4 TUI skip wording and force toggle: explicit separate queued work.
- Complete GUI-review suite, standalone final-gate selftest, corpus comparer/B2/C/trial gates and Task10: NOT RUN for this quality review; separate final Phase D gates. Recorded entrypoint selftests do not substitute for the final standalone command.
- Marker authenticity or payload ownership: the approved marker-only rule intentionally classifies any folder containing failure.json as diagnostic until removal; no payload validation/authenticity guarantee is inferred.
- Existing symlink/junction traversal/resolution policy and concurrent marker/filesystem changes: explicitly outside this narrow change; no new link or snapshot-consistency guarantee is issued.
- Existing stale TUI last_scan and directly selected single-file workflows bypassing discovery: unchanged surrounding workflow, outside F2.
- Existing CLI traceback/error presentation and _pick_file's broad scan-error fallback: unchanged caller presentation; the new scanner guard communicates a clear error and batch processing does not begin after rejection.
- Arbitrary POSIX-native literal backslash/colon filename compatibility: the approved portable contract is Windows-origin glob patterns, not every POSIX filename grammar; PureWindowsPath's conservative rejection is intentional.
- Scanner traversal pruning, per-directory marker caching and list-to-set deduplication optimization: no measured performance failure in this scope; avoid unrelated algorithm/policy changes for a correctness fix.

## Verdict

APPROVED for scoped Phase D F2 at 4a0cdb794a337b9cc91846d16585478c3bb5fde0.

Ready to accept this focused change: Yes. The shared implementation addresses both original source suppression and the demonstrated pattern-boundary root cause, with meaningful executable regression coverage and no unresolved scoped quality finding. This verdict does not approve or complete F4/F5/S1/S2/S4, final Phase D gates, Task10, or Phase D as a whole.
