---
artifact: phase-checkpoint
phase: 10
status: in_progress
sequence: 4
plan: plans/phase-10-private-files-session-plan.md
head_commit: e6e420f
working_tree: clean
updated_at: 2026-10-23T23:30:00+08:00
---

# Phase 10 checkpoint - tasks 1-4 done; task 5 (photo OCR) needs D1/D2; exit work after

## Completed Tasks

- Start: owner go, D1-D4, environment check, and the lockfile churn restore (`npm ci` in the Orca setup).
- Task 1 session store (`4d596be`).
- Task 2: D4 deps (`55aba06`, no version change) and upload validation (`bd39906`).
- Task 3: curriculum-matched grade rows and student-confirmed facts (`34f22fc`). The system never maps
  a grade to pass/fail.
- Task 4 conversation context: [design](2026-10-23-conversation-context-design.md),
  [results](2026-10-23-multi-turn-observation-results.md).
  - Host and router code: `aabb5ee`, `0f2b70d`, `ff448ba` (routed sink).
  - Fixes from the live prechecks:
    - `13e4c7f`: store the check-target course (owner approved; F4 revised, F4b added).
    - `304368a`: unrelated new questions are free of the previous turn's scope (owner: most messages are
      not follow-ups).
    - `9950e09`: show the stored course on an unscoped follow-up.
    - `c470ca1`: signal `course_available` instead of a code; required early field; single-operation
      index repair.
    - `ea64ead`: words that name a course are never a back-reference (fixes run-4 F5 wrong carry).
  - Counted multi-turn run 5 at `ea64ead`: 12/12 resolve or clarify, 0 wrong carry-overs.
  - Single-turn roster run 15: all 63 statuses and decisions equal run 14, and the 25 answered texts are
    byte-identical.

## Current Task

Task 5 (photo OCR) is gated on owner decisions D1 (onnxruntime CPU/GPU, Docling pin) and D2 (Gemma vision
measurement), which were deferred to this step.

## Repository State

Branch `feat/p10-private-files-pipeline` at `e6e420f`. Not pushed. Ignored evidence is in
`audit-evidence/p10-20261023/` (multiturn1-5, roster15, suite logs, runners).

## Verification Evidence

- Full suites: task 1 tree 6218 passed/6 skipped; task 2 tree 6238/6. Task 4 tree:
  `full-suite-task4.log` (running at this checkpoint).
- Focused: routing, private_context and orchestration subsets, 475 passed at `ea64ead`.
- Single-turn prompt `6a9c2e7e...` (Phase 09 v17) and schema `7cde5320...` unchanged, compared with a
  `git archive` of the pre-change HEAD.
- Run with `PYTHONUTF8=1 <venv python> -X utf8 -B -m pytest -q -p no:cacheprovider tests --basetemp=<audit-evidence>`.
- No linter is installed; disclosed.

## Versions and Digests

Python 3.13.7; FastAPI 0.141.1; pypdfium2 5.13.0 and Pillow 12.3.0 locked in `api` (the test venv has
pypdfium2 5.14.0). Gemma 4 E4B (Phase 09 GGUF, not re-hashed) in container `bintanong-p09-cuda-latency`,
restarted before run 15. Node 24.21.0 / npm 11.19.0. Frontend `npm audit`: 3 pre-existing findings.

## Decisions

- D1-D4, and the F4/F4b revision, are in `owner-decisions-ledger.md`.
- Owner, 23 Oct: most messages are not follow-ups; context must never bind an unrelated question.
- Technical limits are 15 MiB, 20 pages and 60 MP.
- Turn-1 statements are not carried, by design (a disclosed limit).
- Context consulted 23 Oct: thesis physical 17-19 and 65-66, plus the routing PNG. No discrepancy.

## Known Failures or Blockers

- Photo OCR is not built (D1/D2).
- Taglish follow-up host lines come out mostly in Filipino (the known Phase 09 limit).
- D1/D2 document follow-ups withhold details outside the reviewed facts.
- HTTP endpoints and cookie wiring are Phase 11.

## Next Action

Ask the owner for D1/D2 (photo OCR). Then do the exit work: master 15.3 isolation-case mapping with any
missing tests, a security review of `backend/bintanong_private_context/`, the full suite, and the handoff.

## Do Not Repeat

Tasks 1-4, the multi-turn prechecks and counted run 5, roster run 15, D1-D4 and F4 questions, the
environment check, and the Context reading.
