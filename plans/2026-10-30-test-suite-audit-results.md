# Test-suite audit execution

Plan: [audit and consolidation](2026-10-30-test-suite-audit-plan.md).
Baseline code: `3ad52e5`, branch `p12-evaluation-harness`; initially clean.
Evidence root: `C:/Coding-projects/bintanong_workspace/audit-evidence/p12-test-audit-20261030/`.
No push, product behavior changes, tool retirement, model download or lockfile changes authorized.

## Checkpoint

| Task | State |
| --- | --- |
| 1 Baseline | Complete: 7,365 collected; 7,357 passed / 6 skipped / 2 xfailed; 1,608 subtests |
| 2 Measure | Complete: 4,640 passed / 6 skipped; 4,646 per-test records |
| 3 Quick wins | Complete: focused 290 passed / 1 skipped; inherited coverage unchanged; 7,364 collected |
| 4 Contracts consolidation | Pending quick wins |
| 5 Other redundancy | Pending consolidation |
| 6 Tool retirement | Owner decision required; retain tooling until answered |
| 7 Final verification | Pending |

## Decisions and boundaries

- Owner approved installing `coverage` and `pytest-cov` into the specified evaluation venv,
  with no pyproject/lockfile changes. Installed after baseline: coverage 7.17.0 / pytest-cov 7.1.0;
  existing pytest 9.1.1 unchanged. `coverage-install.json` / `.log` record the install.
- Owner changed verification schedule during task 3: "Use focused checks during audit; full suite at the end".
  This supersedes full-suite-after-each-commit in the original plan/request. Stopped the intermediate
  quickwins full-suite run after batch 0 passed (1,839 / 2 skips / 334 subtests); batch 1 partial, not a full pass.
  Preserve all partial logs; only the baseline is a completed full-suite run so far.
- This changes test organization, not product requirements. Existing approved requirements and the audit
  plan are the baseline; behavior-preserving refactoring requires passing coverage before changes.
  Any production fix would require its own RED/GREEN regression first.
- User-directed evidence location overrides the execution skill's default `.superpowers` scratch location.
  This dated report is the durable task ledger; raw reports and temporary scripts stay in the evidence root.
- The session-guard skill's suggested session split is superseded by the instruction to persist through this
  authorized plan; maintain this checkpoint and recheck critical rules instead of stopping at a tool-call count.
- Dependencies: task 2 needs task 1's author/file roster and passing baseline; tasks 4/5 need task 2's
  line/branch contexts and assertion review; task 7 compares the same production scope before/after.
  A subset alone does not prove redundant assertions. Protected tests remain unless equivalence is proved.
- Context consulted: thesis physical 17–18 (undergraduate-only, read-only, private-file isolation), runtime
  routing PNG, master sections 1–3 and 11–13, Phase 12 final handoff and current progress.
  No architecture/scope discrepancy; no implementation phase reopened and Phase 13 remains cancelled.

## Collection baseline

`before-collection.log`: `7,365 tests collected in 5.48s` (exit 0).
Family definitions are disjoint: `test_contracts_*` plus `test_source_governance_manifests`;
`test_prospectus_*`; `test_review_gui_*`; `test_evaluation_*`; `test_ocr_*`; remaining files as other.

| Family | All collected before | Inherited before |
| --- | ---: | ---: |
| Contracts | 2,032 | 2,032 |
| Prospectus | 1,291 | 1,290 |
| Review GUI | 407 | 407 |
| Evaluation | 272 | 272 |
| OCR | 100 | 90 |
| Other | 3,263 | 555 |
| Total | 7,365 | 4,646 / 105 files |

`before-inventory.json` records each file, family, collected count and creation author. Use the most recent
addition of the current pathname (`git log --diff-filter=A`), not the oldest historical incarnation:
`test_api_auth.py` was replaced by the owner at `b1bc98b`; its former inherited version is not in the roster.

## Verification and next action

Python 3.13.7 in the owner-specified evaluation venv, `-X utf8`, `PYTHONUTF8=1`.
`pytest -p no:cacheprovider --basetemp=<evidence>/tmp-baseline-N --junitxml=<evidence>/baseline-N.xml -q <batch files>`.
`baseline-batches.json` enumerates every collected file exactly once (sizes 1,842/1,841/1,841/1,841).
Local `supabase_db_Bintanong` started and health confirmed; existing Gemma container untouched, unused by audit.
All four batch exits 0: pass counts 1,839/1,841/1,838/1,839; skips 3/0/1/2; xfails 0/0/2/0;
subtests 183/427/605/393. Pytest durations 296.86/176.29/565.03/343.63 seconds.
Warnings: inherited unregistered `gpu` marker (root invocation), Starlette/httpx and Docling deprecations;
no test failures. Exact warnings and JUnit results remain in `baseline-N.log` / `baseline-N.xml`.
No production changes. Task 3 changes only tests/helpers; final full-suite verification remains required.

Task 2 command is recorded by `run_inherited_coverage.py` in `coverage-before-run.json`: frozen 105-file roster,
`--cov=backend --cov=scripts --cov-branch --cov-context=test`, external `audit.coveragerc` with subprocess tracing.
First attempt exited before tests: parallel cleanup matched a report log sharing the data basename (WinError 32).
Retained `failed-coverage-preflight.log`; isolated data under `coverage-data-before/.coverage`, retry running.
Reports remain separate from data. Source Python coverage cannot by itself measure SQL/Prolog/JS/schema assertions.
Successful inherited run: 4,640 passed / 6 skipped / 13 subtests, exit 0, 426.67s.
Baseline Python coverage: 13,893 / 23,545 statements (59.0062%); 4,319 / 9,284 branches (46.5209%).
`analysis-before.json` lists 2,926 subset candidates and 707 zero-production records (including skipped tests),
and unique line/arc coverage by family. `per-test-before.json.gz` stores all per-test line and transition sets.
The initial context-rich coverage JSON was 2.92 GB; retain it as raw evidence, use compact
`coverage-before-summary.json` for comparisons. Subsequent JSON reports omit repeated contexts; raw SQLite
data and per-test exports retain them. No evidence reduction in the analysis.

## Removal proof and quick wins

Only removal so far (one unparametrized case):
`test_prospectus_b2_codex_review.py::test_item8_the_untouched_entry_is_still_applied` -> retained
`test_o1_old_ledgers_still_read_and_apply_unchanged` in that same file. Identical function AST except name,
including signature/decorators/assertion and same module globals; every measured line/arc is a subset across
10 production files. `removal-proof.json` contains the normalized AST hash and coverage checks.
Keep the descriptive compatibility test. No negative or mutation-survivor test removed.

Renamed zero-test helper to `evaluation_fixtures.py`; updated all five importers; builders unchanged.
Focused command: owner-specified pytest flags over the prospectus review file and those five importers:
290 passed / 1 skipped, exit 0 (`quickwins-focused.log`).
Quickwins inherited run: 4,639 passed / 6 skipped / 13 subtests, exit 0, 405.26s. Collection 7,364.
`comparison-quickwins.json`: all 13,893 previously covered lines and 4,319 branches retained; no lost sets,
same denominators and unchanged production Python hashes. Helper builders have identical ASTs (docstring excluded).

Next: commit quick wins, then task 4 contracts consolidation with focused checks and final-suite schedule.
