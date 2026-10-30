# Test-suite audit execution

Plan: [audit and consolidation](2026-10-30-test-suite-audit-plan.md).
Baseline code: `3ad52e5`, branch `p12-evaluation-harness`; initially clean.
Evidence root: `C:/Coding-projects/bintanong_workspace/audit-evidence/p12-test-audit-20261030/`.
No push, product behavior changes, tool retirement, model download or lockfile changes authorized.

## Checkpoint

| Task | State |
| --- | --- |
| 1 Baseline | Complete: 7,365 collected; 7,357 passed / 6 skipped / 2 xfailed; 1,608 subtests |
| 2 Measure | Next; owner approved coverage + pytest-cov in evaluation venv only |
| 3 Quick wins | Pending measurement |
| 4 Contracts consolidation | Pending quick wins |
| 5 Other redundancy | Pending consolidation |
| 6 Tool retirement | Owner decision required; retain tooling until answered |
| 7 Final verification | Pending |

## Decisions and boundaries

- Owner approved installing `coverage` and `pytest-cov` into the specified evaluation venv,
  with no pyproject/lockfile changes. Install after the baseline exits (avoid modifying an in-use venv).
- This changes test organization, not product requirements. Existing approved requirements and the audit
  plan are the baseline; behavior-preserving refactoring requires passing coverage before changes.
  Any production fix would require its own RED/GREEN regression first.
- User-directed evidence location overrides the execution skill's default `.superpowers` scratch location.
  This dated report is the durable task ledger; raw reports and temporary scripts stay in the evidence root.
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
Warnings: inherited unregistered `gpu` marker (root invocation), websockets deprecations and pypdfium2 leak warning;
no test failures. Exact warnings and JUnit results remain in `baseline-N.log` / `baseline-N.xml`.
No tests changed or removed. Coverage before/after not measured yet.

Next: install the approved tools, then measure task 2 over the frozen 105-file inherited roster.
