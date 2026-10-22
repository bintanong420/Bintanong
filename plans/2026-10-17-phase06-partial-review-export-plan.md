# Partial curriculum review export implementation plan

> Execute inline with executing-plans and TDD; owner approved the full design and
> review03 on 17 October 2026. No further implementation approval needed here.

**Goal:** generate inactive candidate Prolog with explicit partial coverage.
**Architecture:** reuse complete authoring validation/strict quoting; add separate
coverage-aware rendering while preserving the strict preview's exact output.
**Stack:** existing Python3.13/Pydantic/pytest; installed SWI-Prolog data parser only.
**Spec:** [approved design](2026-10-17-phase06-partial-review-export-design.md).

## Global constraints and review focus

No source promotion, runtime query/decision, install/dependency/model/database work.
Private/real-source artifacts stay ignored in workspace audit-evidence. Reviewed
records are truth; `.pl` is derived. Blank cells remain unknown. Keep `/L`, ordered
logic, scope and original spans. Existing strict-preview behavior/version unchanged.

Focus tests on unknown versus verified_none; reviewed target with draft reference;
no draft semantic facts; cycles only in reviewed complete direct rules; exact
digests/privacy/scope rejection and strict-quote compatibility. Parse output only
as ground data, with timeout. No actual student decision/benchmark evaluation.

## Task 1: compiler and synthetic verification

Files: modify `backend/bintanong_symbolic/compiler.py` and README; create
`tests/test_symbolic_review_bundle.py`. Consumes `build_curriculum_ledger` output;
produces `compile_curriculum_review_bundle(ledger) -> dict` as in the spec.

- [x] RED: test reviewed target to draft unresolved reference, expected
  `partial_review_candidate`, no draft fact/requirement, explicit pending identity;
  test reviewed unknown versus explicit verified_none and strict preview unchanged.
- [x] Run focused tests with Python below and capture expected missing API failures.
- [x] Implement coverage, reviewed-only cycle detection and conditional renderer,
  reusing strict validation/expressions/quotes; add separate compiler version.
- [x] GREEN plus meaningful boundary tests: all-draft, nested alternatives and
  co-requisites, draft cycle excluded/reviewed cycle held, quoting/injection,
  deterministic hashes, changed receipts/forged flags/privacy/scope rejected.
- [x] Run related authoring/strict-compiler/contracts/candidate regressions and one
  independent final review; fix actual findings through RED/GREEN. Update README.
- [x] Verify staged scope and commit a cohesive feature increment.

Use `C:/Coding-projects/bintanong_workspace/audit-evidence/p05-real-retrieval-readiness-20261012/venv/Scripts/python.exe`
with `-B -m pytest -q -p no:cacheprovider`; external TEMP/TMP and `--basetemp` under
`C:/Coding-projects/bintanong_workspace/audit-evidence/p06-review-bundle-20261017/`.
Related suites: `test_symbolic_review_bundle.py`, `test_symbolic_compiler.py`,
`test_symbolic_authoring.py`, `test_contracts_symbolic.py`, `test_rule_candidates.py`,
`test_prospectus_rule_handoff.py`. Passing exit0 is GREEN; strict output hash also
compared to baseline on a fixed synthetic fixture. No unrelated suite expansion.

## Task 2: approved source application and candidate delivery

- [x] Bind the actual approval to review03's four original hashes and design238ad3b.
- [x] Apply old CS1/L → CC1/L and reviewed blank-row identities/unknown states;
  add previously prepared oldCC1/L identity as draft. Preserve all prior records.
- [x] Rebuild two ledgers, verify source/receipt/native spans, then generate candidate
  `.pl` and coverage JSON with new API; no consult or eligibility query.
- [x] Deliver plain-language exact-code mapping, original regions and existing
  approval links so human can check generated translation; unknown rows explicit.
- [x] Run docs/phase and evidence hash checks; update compact progress/checkpoint
  and commit curated delivery docs only. Leave full Phase06 exit open.

Pre-flight: Task2 consumes Task1's API; source approval is already explicit. Neither
task changes institutional source states or authenticates review declarations.

Product6fedc45; RED15/GREEN35/final330 related passes. Exact evidence and
source delivery: [generated review delivery](2026-10-17-phase06-prolog-review-delivery.md).
