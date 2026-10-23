---
artifact: phase-checkpoint
phase: 11
status: in_progress
sequence: 1
plan: plans/phase-11-backend-api-plan.md
head_commit: 2c2d335
working_tree: dirty
updated_at: 2026-10-23T23:59:00+08:00
---

# Phase 11 checkpoint - started (backend only); task 1 next

## Completed Tasks

- Start: owner go (backend only), environment check, can-advance, pre-phase research (`2c2d335`).
- Owner decisions O1-O5 recorded (ledger, master section 2 "Current pins", 16.3).

## Current Task

Task 1: app factory, session cookie, CSRF guard, `DELETE /session` (test first).

## Repository State

Branch `feat/p11-backend-api` from `dev` `cbaa6a7`. Uncommitted: this plan, checkpoint, INDEX, master and ledger
edits (to be committed together as the phase-start docs commit).

## Verification Evidence

- Ignored inputs match the main checkout (sha256 over sorted files); three lockfiles identical to HEAD and main.
- `phase_state.py validate` / `can-advance`: valid, yes (before this plan).
- Owner-sample OCR probe (RapidOCR, local models, no download), private output in
  `audit-evidence/p11-20261023/private-owner-samples/`: Report of Grades screenshot 413 boxes, skew <= 3 px, codes
  mostly exact (2 PATH-Fit misreads, one code+title merged box, "ELECTRONI" truncated by the source system); rows
  carry units, midterm and final numbers. Handwritten prospectus photo: printed codes read, about 11 of ~20
  handwritten grades read.

## Versions and Digests

Python 3.13.7 (shared venv `audit-evidence/p05-real-retrieval-readiness-20261012/venv`), FastAPI 0.141.1,
SWI-Prolog 10.1.15, PostgreSQL 17.6, pgvector 0.8.2, Gemma 4 E4B GGUF on :18088 (not re-hashed). Owner samples
sha256: `46bf8a11...` and `0451f6f0...` (same Report of Grades screenshot), `dccc1c2a...` (prospectus photo).

## Decisions

O1 AI SDK v7; O2 OCR deps may join `api`; O3 `GET /curricula`; O4 diagnostics out of student text; O5 symmetric
style floor. Only the last user message of an AI SDK request is used (no transcripts).

## Known Failures or Blockers

None. `uv` is not on PATH in this shell (needed for the O2 relock; locate before task 8).

## Context Consulted

Thesis physical 17-18 and 65-66, routing PNG (23 Oct). No discrepancy.

## Next Action

Commit phase-start docs, then task 1 RED: API tests for cookie issue, expiry, deletion, isolation and CSRF.

## Do Not Repeat

Environment check, research, npm version lookup, owner-sample OCR probe.
