---
artifact: phase-checkpoint
phase: 9
status: in_progress
sequence: 105
plan: plans/phase-09-generation-validation-plan.md
head_commit: 6745393
working_tree: dirty
updated_at: 2026-10-21T18:30:00+08:00
---

# Phase 09 checkpoint - per-part generation delivered (mock-verified)

Last full snapshot before this replacement: `0a08d8d:plans/phase-09-checkpoint.md`
(task-first trial, checker diagnosis and their digests; use `git show`).

## Completed Tasks

- Task-first interpretation trial (`8060c7b`, results `8dbb15d`): interpretation
  4/4, full quality 3/4 FAIL (English omitted the fee; reviewer falsely mapped it).
- Checker diagnosis (`0a08d8d`); its native-thinking trial was proposed, never run.
- This session (Claude Code, taking over from Codex): owner approved per-part
  generation instead. Delivered the `parts` profile with TDD. See
  [decision](2026-10-21-per-part-generation-decision.md).

## Current Task

Run the fixed actual-model observation (protocol in the decision record). The
existing CUDA container `bintanong-p09-cuda-latency` was restarted (it had exited
after ~9 h; cold start ~72 s, not counted in any latency figure).

## Repository State

Branch `feat/p09-generation-validation`. Code/tests/READMEs committed as `6745393`
(`feat(generation): require one answer slot per question part`); this checkpoint,
progress, INDEX and the decision record follow in a docs commit. No
startup, model call, dependency, DB, source or institutional change.

## Verification Evidence

- RED: 10 new tests failed for the missing feature (default still `scoped`, no
  `answers` slot); 2 more failed for runtime default and evaluation hashes.
- GREEN: 12/12. Nine older tests failed on the default switch as expected and
  were pinned to `scoped` or updated to `parts` without weakening assertions.
- Focused generation/understanding/runtime/docs set: 406 passed in 7.19s.
- Full suite: FULL_SUITE_RESULT.
- Command form: `<p05 venv python> -B -m pytest -q -p no:cacheprovider tests
  --basetemp=<workspace>/audit-evidence/p09-per-part-20261021/<dir>`.
  Log: `audit-evidence/p09-per-part-20261021/full-suite.log`.

## Versions and Digests

New contracts: `bintanong-part-explanation-v1`, `bintanong-part-confirmation-v1`.
Prompt hashes are exported as `PART_PROMPT_SHA256` / `CONFIRM_PROMPT_SHA256`
and reported by evaluation. Unchanged: router v14, wire v2, ledger
`bintanong-bound-requirement-ledger-v1`, ctx 8192, out 768, temp 0, seed 0,
deadlines 120/120/120/180 s. Prior raw evidence and seals remain in
`audit-evidence/p09-task-first-20261021/` (57-file seal
`e10ca82c572f48557b04aa258b17cdb1bd11d5c0f5ec46369fc866ba36b0fd3d`).

## Decisions

- Owner: per-part generation over the thinking trial (this session).
- The thinking-trial proposal is superseded; do not run it.
- Old profiles stay explicit and selectable; `parts` is the default.

## Known Failures or Blockers

Actual-model quality of `parts` is unmeasured. The reviewer can still confirm
wrongly; the generator can wrongly declare `not_in_evidence` (fails safe).
One unresolved part withholds the whole answer (contract behaviour, follow-up).
Student end-to-end latency remains unmeasured. Phase 09 exit still held.

## Next Action

Write a short plan for one actual-model observation of `parts` on the four saved
developer cases (no reruns or sweeps), then run it against the resident service.

## Do Not Repeat

Task-first trial, checker diagnosis, thinking trial, source/benchmark reviews,
asset setup. Do not overwrite existing test files (an existing
`tests/test_generation_parts.py` was briefly overwritten and restored from Git).
