# Exact service excerpts with office referral

**Goal:** implement the owner's25Oct choice to keep exact printed source terms
and refer to the relevant office when the agency action is cut off.
**Spec:** owner-decisions-ledger.md (cutoff presentation), source-gap-policy.md,
service-table-association-policy.md, existing Phase11/service-cutoff baseline.
**Architecture:** append language-matched advisory referral inside the existing
source-bound excerpt, before ordinary support/relevance review and final fidelity
validation. Keep client/action/office fields separate and the continuation unknown.
Use only the record's nonblank office field; otherwise use a generic university
office referral. A staff role or another office mentioned inside the action does
not establish the referral destination. Existing1200-character/claim/call limits
remain; overlong records hold only the affected part. No schema/dependency change.

User selected the combined behavior after seeing the concrete Taglish example.
This is a small approved presentation change; no new PRD/product scope is needed.
Existing isolated p11/feat/p11-backend-api verified; no new worktree/setup/install.
Brainstorming/design resolved by the exact request; proceed inline with TDD.

## One implementation task

1. In tests/test_generation_service_cutoff.py, add synthetic tests for all three
   language referrals, exact printed quotes, record-office association, absent/
   blank office generic fallback and length-cap behavior. Existing positive-model
   rejection/final guard/independent-parts tests remain applicable.
2. Run focused pytest using shared Python3.13/no cache/external basetemp. Observe
   expected missing-referral RED before touching production code.
3. Change backend/bintanong_generation/service_cutoff.py only: language referral
   templates plus exact office/generic selection, composed before length check.
4. Run focused plus generation/understanding/orchestration/runtime regressions;
   inspect diff and perform scoped review. Commit cohesive code/tests.
5. One full tests/ run on the frozen new commit; save PID/start/head/log/exit and
   recover the result before finishing. Do not duplicate completed2ce3daf suite.
6. Execute the separately bounded saved-integration short-reference observation;
   it evaluates the combined approved excerpt/referral, not a new source package.

## Acceptance and risks

- Exact client/action/office/fee/time quotations, explicit missing continuation,
  and an advisory referral in English/Filipino/Taglish. No invented completion.
- The printed office is not confused with the office embedded in client/action
  prose. Blank/absent office yields no guessed institution-specific destination.
- Ordinary review and exact final fidelity remain mandatory; an added referral
  does not authorize an otherwise rejected claim or erase an independent part.
- The output cap includes the referral; no truncation or relaxed guard to fit.
- Expanded release stays inactive and generation reference default canonical.
  Source sequence/semantic quality and frontend/phase exits remain separate.

Validation commands: shared venv python -X utf8 -B -m pytest -q -p no:cacheprovider
tests/test_generation_service_cutoff.py, then selected regression files and full
tests/, all with unique external --basetemp. git diff --check and phase_state.py
validate; existing linter/formatter unavailable, no install authorized.

## Execution evidence

- RED11 failed/17 passed, all expected missing-referral/length/fidelity assertions;
  no setup failure. GREEN cutoff+short-reference42 passed1.36s.
- Broad generation/understanding/service-coverage/orchestration/runtime selection:
  664 passed21.31s. Independent scoped review: no blockers,42 passed1.48s.
- Code4425538, no production/test changes after commit. One full tests/ suite
  started21:11:21+08 on that commit; runner15680/pytest12732, creation binding and
  exact command in workspace/audit-evidence/p11-cutoff-referral-20261025/
  full-suite.processes.json; head/log/exit alongside. Missing exit never means pass.
- Actual saved-evidence short-profile observation: one draft+ordinary review,
  answered/validated,463+108 output tokens,45.73s generation/review only. Protected
  record has exact fields, cutoff notice and College Enrollment Area referral;
  it is included before ordinary review. All54 sealed source files unchanged.
- Actual record component examples:en531/fil537/Taglish540 characters, below1200.
  Effective saved language is fil despite Taglish question; no Taglish-quality pass.
  No source-order contract or expanded quality/activation approval inferred.
