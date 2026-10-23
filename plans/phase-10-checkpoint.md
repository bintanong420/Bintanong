---
artifact: phase-checkpoint
phase: 10
status: in_progress
sequence: 3
plan: plans/phase-10-private-files-session-plan.md
head_commit: 0f2b70d
working_tree: clean
updated_at: 2026-10-23T21:00:00+08:00
---

# Phase 10 checkpoint - tasks 1-3 done; task 4 code done, live multi-turn check pending

## Completed Tasks

- Phase 10 started on the owner's go. Decisions D1-D4 are in the plan and the ledger. The worktree environment
  was verified (ignored files match main). Orca's lockfile churn was restored, and its setup script now uses `npm ci`.
- Task 1 session store (`4d596be`): memory-only `SessionStore`, SHA-256 credential digests, 30 min idle expiry,
  delete/wipe, session bound. 17 tests; mutations caught.
- Task 2 (`55aba06`, `bd39906`): D4 put pypdfium2 5.13.0 and Pillow 12.3.0 in the `api` extra. The uv 0.12.17
  relock changed no package version, and `uv lock --check` passes. Upload validation covers the streaming
  byte cap (15 MiB), sniffed type only, a PDF page cap of 20 with zero pages unreadable, and images opened with
  the sniffed plugin only plus a 60 MP cap. 20 tests. A mutation exposed a real bug (`UploadRejected` was
  swallowed as `ValueError`), which is fixed.
- Task 3 (`34f22fc`): born-digital grade rows are matched only by the session curriculum's reviewed aliases
  (short forms included). A row holds only the printed code, candidate courses and display-only grade marks.
  Unknown codes are counted, never matched. There is no text layer for scans, and photos wait for step 5. The
  student states passed/failed per row; the system never maps a grade. The session has a pending slot;
  confirming replaces an earlier statement per course, and batch-prefixed fact ids avoid collisions. 14+5 tests.
- Task 4 code (`aabb5ee`, `0f2b70d`) follows the [design](2026-10-23-conversation-context-design.md):
  - `ConversationContext` holds ids only, and `RequestContext.conversation` carries it.
  - `capture` keeps a course or subject only when the turn used exactly one.
  - `follow_up_context` carries scope.
  - For `previous_course_quote`, the model marks the words, and the host supplies the stored course only
    while it is still in the request's curriculum. Otherwise the router clarifies.
  - Single-turn prompt, schema and messages are byte-identical to before. Checked against a `git archive`
    of HEAD: prompt `6a9c2e7e...` (= Phase 09 v17), schema `7cde5320...`.

## Current Task

Task 4 remainder: multi-turn en/fil/Taglish cases and a live-model check of `previous_course_quote`.

## Repository State

Branch `feat/p10-private-files-pipeline` at `0f2b70d` plus this checkpoint commit. Not pushed.

## Verification Evidence

- Full suite at task 1: 6218 passed, 6 skipped, 1552 subtests (19m33s). Run with `PYTHONUTF8=1 <venv python>
  -X utf8 -B -m pytest -q -p no:cacheprovider tests --basetemp=audit-evidence/p10-20261023/...`.
- Full suite at task 2: see `audit-evidence/p10-20261023/full-suite-task2.log`.
- Subset at `0f2b70d` (routing, orchestration, runtime, private_context): 525 passed.
- No linter is installed (no ruff on the host or in the venv); this is disclosed.

## Versions and Digests

Python 3.13.7; FastAPI 0.141.1; pypdfium2 5.13.0 and Pillow 12.3.0 (locked, `api` extra). The shared test venv
has pypdfium2 5.14.0 (drift; the image follows the lock). The uv relock ran in `python:3.13.15-slim-bookworm` with
the uv 0.12.17 binary copied from `ghcr.io/astral-sh/uv:0.12.17`, which is distroless. Node 24.21.0 / npm 11.19.0.
Frontend `npm audit`: 3 pre-existing findings, unchanged.

## Decisions

- D1-D4 as recorded in the plan and ledger.
- Technical: uploads use a raw body. Limits are 15 MiB, 20 pages and 60 MP (research defaults, not
  institutional values).
- Grade rows never become pass/fail without the student's choice (the existing router rule forbids it).
- Follow-up references are host-resolved.
- Context consulted 23 Oct: thesis physical 17-19 and 65-66, plus the routing PNG. No discrepancy.

## Known Failures or Blockers

- New multi-turn benchmark wording needs owner acceptance before a counted run.
- The live check needs the model container `bintanong-p09-cuda-latency` running.

## Next Action

Show the owner proposed multi-turn cases (en/fil/Taglish follow-up, two-antecedent, topic switch, scope
change). After acceptance, run them and the single-turn roster on the live model.

## Do Not Repeat

Tasks 1-3, task 4 host/router code, D1-D4, the environment/lockfile check, the Context reading for this resume,
and the single-turn digest comparison.
