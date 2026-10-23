---
artifact: phase-checkpoint
phase: 11
status: in_progress
sequence: 4
plan: plans/phase-11-backend-api-plan.md
head_commit: f774611
working_tree: clean
updated_at: 2026-10-24T02:00:00+08:00
---

# Phase 11 checkpoint - tasks 1-6 done; task 7 (24.2) waits for an owner judgement

## Completed Tasks

- Start: owner go (backend only), environment check, can-advance, pre-phase research (`2c2d335`).
- Owner decisions O1-O5 recorded (ledger, master section 2 "Current pins", 16.3) (`3ba8d7d`).
- Task 1 cookie session, origin guard, `DELETE /session` (`d42feac`; boundary moved to `session.py` `d59d0e2`).
- Task 2 store turn tracking (`e77e3af`), `ChatTurns` (`1287bbc`), `GET /curricula` (`017efc4`).
- Task 3 student view without ids, operations or condition codes (`7e1d34d`; canonical text unchanged).
- Task 4 `POST /chat` as AI SDK UI message stream v1 with progress, cancel on disconnect (`c2cae2e`).
- Task 5 store upload ids/fact ownership (`4b73b21`); upload, confirm, delete endpoints (`8b70e21`).
- Task 6 `GET /sources/{source_id}` from cards cited in this process (`b8f829b`).

## Current Task

Task 7 (24.2) paused for an owner judgement (bounded-attempt rule). Run 15 baseline by reply template (first
line of each answer): English 21/21, Filipino (`-tl`) 21/21, Taglish (`-taglish`) 10/21; 11 Taglish got Filipino.
Offline simulation of a symmetric floor over the 63 roster questions (no model calls): closed-class English words
plus English number/ordinal words, quoted text ignored, fixes 5/11 and wrongly flips 1 Filipino question (course
title "Microbiology and Parasitology"), so catalog titles must be excluded too. The other 6 misses differ from their
owner-accepted Filipino twins by register (pwede/pasado/bagsak vs maaari/naipasa), not English words. Tuning a list
on the counted roster would also contaminate it.

## Repository State

Branch `feat/p11-backend-api` from `dev` `cbaa6a7`; commits through `b8f829b`, nothing pushed.

## Verification Evidence

- Ignored inputs match the main checkout (sha256 over sorted files); three lockfiles identical to HEAD and main.
- Owner-sample OCR probe (RapidOCR, local models, no download), private output in
  `audit-evidence/p11-20261023/private-owner-samples/`: Report of Grades screenshot 413 boxes, skew <= 3 px, codes
  mostly exact (2 PATH-Fit misreads, one code+title merged box, "ELECTRONI" truncated by the source system); rows
  carry units, midterm and final numbers. Handwritten prospectus photo: printed codes read, about 11 of ~20
  handwritten grades read.
- Each task: RED observed for the missing behaviour, then GREEN; every new guard mutation-checked (each mutation
  failed a test): session 4, turns 5, presentation 4, stream 4 (disconnect test bounded so a regression fails in
  ~7 s instead of hanging), uploads 4, sources 2.
- Last focused run (all API test files): 76 passed; private-context session/isolation/conversation files pass.

## Versions and Digests

Python 3.13.7 (shared venv `audit-evidence/p05-real-retrieval-readiness-20261012/venv`), FastAPI 0.141.1,
SWI-Prolog 10.1.15, PostgreSQL 17.6, pgvector 0.8.2, Gemma 4 E4B GGUF on :18088 (not re-hashed). Owner samples
sha256: `46bf8a11...` and `0451f6f0...` (same Report of Grades screenshot), `dccc1c2a...` (prospectus photo).
Stream chunk shapes checked against `ai` 7.0.150 `src/ui-message-stream/ui-message-chunks.ts` (unpkg, read only).

## Decisions

- O1-O5 as recorded. Only the last user message of an AI SDK request is used (no transcripts).
- Validation errors (422) are returned before the stream; the turn lock is taken inside the stream, so a client
  gone before streaming cannot leave a session stuck. Later failures are an `error` chunk with a fixed code.
- The canonical answer text stays the researcher diagnostic (validator checks it byte for byte); students get
  `student_text`. Prolog decisions are flagged `conditional` (they rest on student-supplied facts).
- `GET /sources` serves only cards cited by this process's answers (bounded LRU); no internal locators.
- Plain `StreamingResponse` is used instead of `fastapi.sse` so the bytes are exactly the SDK's `data:` lines.

## Known Failures or Blockers

None. `uv` is not on PATH in this shell (needed for the O2 relock; locate before task 8). No disconnect test
through a real HTTP server yet (generator-level test only); task 9 live smoke covers the real server.

## Context Consulted

Thesis physical 17-18 and 65-66, routing PNG (23 Oct). No discrepancy.

## Next Action

Owner judgement on 24.2 options (closed-class floor only; plus a style-prompt revision; or accept Filipino replies
for register-only Taglish). Meanwhile tasks 8 (photo rows) and 9 (real-data composition, live smoke).

## Do Not Repeat

Environment check, research, npm version lookup, owner-sample OCR probe, tasks 1-6.
