---
artifact: phase-checkpoint
phase: 11
status: in_progress
sequence: 5
plan: plans/phase-11-backend-api-plan.md
head_commit: 4931177
working_tree: clean
updated_at: 2026-10-24T05:30:00+08:00
---

# Phase 11 checkpoint - tasks 1-8 done; task 9 live HTTP smoke next, then exit

## Completed Tasks

- Start: owner go (backend only), environment check, can-advance, pre-phase research (`2c2d335`); O1-O5 (`3ba8d7d`).
- Task 1 cookie session, origin guard, `DELETE /session` (`d42feac`, `d59d0e2`).
- Task 2 store turn tracking (`e77e3af`), `ChatTurns` (`1287bbc`), `GET /curricula` (`017efc4`).
- Task 3 student view without ids, operations or condition codes (`7e1d34d`).
- Task 4 `POST /chat` AI SDK UI message stream v1 with progress, cancel on disconnect (`c2cae2e`).
- Task 5 store upload ids (`4b73b21`); upload/confirm/delete endpoints (`8b70e21`).
- Task 6 `GET /sources/{source_id}` (`b8f829b`).
- Task 7 (24.2): owner path recorded (`d1e7f31` ledger); floor `3eb4f59`, `6abfb40`; prompt trial declined;
  [results](2026-10-24-taglish-style-floor-results.md) (`4931177`).
- Task 8 (24.1): photo rows `a495db2`..`72a196b`, scorer `7328519`/`c55a6ac`, limits as strict xfails `15dbe41`;
  [results](2026-10-24-photo-grade-rows-results.md) (`5e1eb1f`). Photos stay unsupported; no dependency added.
- Task 9 part: `ResearchPipeline` chat port over the real answer path (`6f0cf36`).

## Current Task

Task 9: live HTTP smoke with the untracked launcher (`audit-evidence/p11-20261023/live-api/`), after multi-turn run 6.

## Repository State

Branch `feat/p11-backend-api` from `dev` `cbaa6a7`; commits through `4931177`, nothing pushed.

## Verification Evidence

- Each code task: RED observed, then GREEN; every new guard mutation-checked (each mutation failed a test).
  Latest focused runs: API files 76 passed; photo rows 27 passed + 2 strict xfails; scorer 10; style floor 27;
  routing style/router 131; research pipeline 2.
- Roster run 16 (HEAD `6abfb40`, run 15 settings): 0 of 63 status/decision changes; replies en 21/21, fil 21/21,
  Taglish 15/21 (run 15: 10/21); 23 of 25 answered texts identical, 2 changed only in language.
- Photo measurement: 42 simulated photos, 0 silent errors; plain layout exact in all 7 conditions; Report-of-Grades
  style exact in flat/dim; owner's real screenshot refused (two causes pinned as xfails).
- Full suite not yet run this phase.

## Versions and Digests

Python 3.13.7 (shared venv `audit-evidence/p05-real-retrieval-readiness-20261012/venv`), FastAPI 0.141.1,
SWI-Prolog 10.1.15, PostgreSQL 17.6, pgvector 0.8.2, RapidOCR 3.9.2 + onnxruntime 1.30.0 CPU (venv only, local
models), Gemma 4 E4B GGUF on :18088 (not re-hashed). Owner samples sha256: `46bf8a11...`, `0451f6f0...`,
`dccc1c2a...`. Stream chunk shapes per `ai` 7.0.150.

## Decisions

- O1-O5 as recorded; 24.2 path (floor kept, prompt trial declined); 24.1 photos unsupported, no `api` dependency.
- Only the last user message of an AI SDK request is used. 422s before the stream; turn lock inside it.
- Canonical answer text stays the researcher diagnostic; students get `student_text`.

## Known Failures or Blockers

None blocking. Disclosed limits: 6 register-only Taglish questions reply in Filipino; photos unsupported (real
screenshot refused); no disconnect test through a real server yet (task 9 smoke); full suite pending.

## Context Consulted

Thesis physical 17-18 and 65-66, routing PNG (23 Oct). No discrepancy.

## Next Action

Read multi-turn run 6, start the live API, run `smoke_http.py`, then the full suite and the exit handoff.

## Do Not Repeat

Environment check, research, npm lookup, owner-sample OCR probe, tasks 1-8, roster run 16, the three style prompts.
