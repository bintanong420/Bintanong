---
title: Test-suite audit and consolidation plan (inherited Phase 1-2 tests)
date: 2026-10-30
worktree: p12
branch: p12-evaluation-harness
status: planned (read-only audit done; no test changed yet)
---

# Test-suite audit and consolidation plan

Owner request (30 Oct 2026): the previous developer (git author `Hawksprey420`) handed over about 5,000 tests. Verify
them, find redundant or useless tests, and plan fixes. Codex executes; Claude reviews.

## Read-only audit (Claude, 30 Oct, HEAD 8565182)

- 7,365 tests collected (`pytest --collect-only`, 6 s). Files created by `Hawksprey420`: **105 files, 4,646 tests**
  (2026-09-26..2026-10-24). Files created by the owner (`Netoerare`): 187 files, 2,719 tests.
- **No dependency on the dataset, `.env` or absolute paths.** Path-like strings (`C:\Users\x\a.pdf` and similar) are
  negative inputs checking that validators reject absolute or private paths. Skips are environment guards (no CUDA,
  no Node, case-sensitive filesystem, Windows-only, reportlab encryption); the full suite reports 6 skipped and
  2 xfail. Inherited tests therefore run in a fresh worktree.
- **Largest families:**
  - contracts: about 1,850 tests in 25 files (`test_contracts_*.py`, `*_fix2`, `*_fix3_*`, `*_survivors*`,
    `test_contracts_parity.py` 413, `test_source_governance_manifests.py` 294)
  - prospectus extractor/fixer: about 1,300 tests (`test_prospectus_*`)
  - review GUI: about 410 tests (`test_review_gui_*`)
  - evaluation: about 270 tests
  - OCR bench: about 90 tests
- **Contracts tests are real tests,** asserting through helpers (`reject()`, `T.bad()`, `pytest.raises`). The
  `*_survivors` files kill mutants that survived mutation testing, which is a legitimate purpose. Their problem is
  **fragmentation**: fix-pass files (`_fix2`, `_fix3_*`) extend earlier files by importing them (`import
  test_contracts_answer as T`). Some negative-input lists repeat across files: the bad-path list appears in
  `test_contracts_parity.py`, `test_source_governance_manifests.py` and `test_contracts_governance_fix2.py`.
  Whether these overlap or hit different validators is unmeasured.
- Exact duplicate test bodies: one pair (`test_prospectus_b2_codex_review.py`: `test_item8_...` and `test_o1_...`).
- `tests/test_evaluation_fixtures.py` collects 0 tests (a helper module with a `test_` name).
- **Tooling:** no `coverage`, `pytest-cov`, `mutmut` or `xdist` in the evaluation venv, so redundancy cannot yet be
  measured. Installing a dev-only tool needs the owner's approval.

## Principles

- Remove a test only with evidence that it adds nothing: an identical body, or the same production lines and
  branches as a retained test (per-test coverage contexts) with no unique assertion. Never on name or size alone.
- Prefer **consolidation** (merging fix-pass files into the module's main test file, deduplicating shared input
  lists into one parametrized fixture) over deletion. Behaviour coverage must not drop.
- Keep negative, privacy, scope, security and source-gap tests and mutation-survivor tests unless a retained test
  provably covers the same mutant or branch.
- Tests for tooling that is no longer used (review GUI, OCR bench, prospectus fixer) are kept unless the **owner**
  decides the tool itself is retired. Retiring a tool is an owner decision, not a test-cleanup step.
- Small, cohesive commits (Conventional Commits, no AI attribution). The full suite stays green after every commit
  (local Supabase up for DB tests). Counts before and after are reported per family.

## Tasks (dependency order)

1. **Baseline.** Run the full suite with the local Supabase DB up and record pass/skip/xfail and the collected
   count. Ask the owner to approve a dev-only `coverage` (or `pytest-cov`) install into the evaluation venv, with no
   lock or `pyproject` change unless the owner agrees.
2. **Measure.** With approval, run coverage with per-test contexts over the inherited files. Produce an ignored
   report (`audit-evidence/p12-test-audit-<date>/`): for each test, the set of covered lines and branches; tests
   whose set is a subset of another test's set in the same family; tests covering no production line; and per-family
   unique coverage. Without approval, use AST and name analysis only and say that subset claims are unverified.
3. **Quick wins (no coverage needed):** drop the duplicate pair in `test_prospectus_b2_codex_review.py` (keep one,
   with the more descriptive name); rename or move `test_evaluation_fixtures.py` to a non-`test_` helper name if it is
   only imported.
4. **Consolidate the contracts family.** Per module (answer, runtime, governance, source, symbolic, embedding, base),
   fold `_fix2`, `_fix3_*` and `_survivors*` into one file per module (or a small `tests/contracts/` package), keeping
   every distinct assertion. Move shared negative-input lists (bad paths, IDs) into `contracts_fixtures.py`. Keep
   test names descriptive. Collected-count drops only where coverage shows a true duplicate.
5. **Redundancy removal elsewhere.** Use the task 2 report for the prospectus, review GUI, evaluation and OCR
   families. Remove only proven subset-and-no-unique-assertion tests, list each removal with its covering test, and
   keep mutation-survivor tests.
6. **Owner decisions** (ask; do not act): whether the review GUI, OCR bench and prospectus fixer tooling is retired.
   If a tool is retired, its tests and code go in one dedicated, reviewed change.
7. **Verify and report.** Full suite green (local DB up). Report counts before and after per family, the removed
   test list with its evidence, and the coverage before and after (it must not decrease). Update
   `plans/plan_current_progress/current_progress.md`.

## Commands

- Python: `audit-evidence/p05-real-retrieval-readiness-20261012/venv/Scripts/python.exe -X utf8`, `PYTHONUTF8=1`.
- Tests: `pytest -p no:cacheprovider --basetemp=<external ignored dir> tests/` (in batches if memory is tight). DB
  tests need `supabase_db_Bintanong` running and healthy; the Gemma model is not needed.
- Collection count: `pytest --collect-only -q tests/ | tail -1`.
