---
artifact: phase-checkpoint
phase: 12
status: in_progress
sequence: 3
plan: plans/phase-12-evaluation-writeup-plan.md
head_commit: a3ff208
working_tree: clean
updated_at: 2026-10-30T12:00:00+08:00
---

# Phase 12 checkpoint — report written; full suite passed; paused for worktree move

## Completed Tasks

- absence-taglish loss diagnosed as one-off server non-determinism (`0d6ebac`).
- Plan and pre-phase research (`f2b00dc`); owner decisions recorded (`6494b43`): single runs disclosed;
  write-up before hosted 560 activation.
- Paired statistics (`p12-benchmark-20261029/stats/paired_stats.py`, `paired_stats.json`).
- Evaluation report `docs/evaluation/phase12-evaluation-report.md` (`36ae881`).

## Current Task

Paused for the dedicated Phase 12 worktree (branch from `dev` a3ff208). First task there: hosted 560 activation
(owner 30 Oct); see the [session handoff](2026-10-30-phase12-session-handoff.md).

## Repository State

p11 merged into `dev` (`a3ff208`, origin and local; full suite 7314 / 1608 pass). Clean.

## Verification Evidence

- Selector replays: 8/8 handbook_attendance (`p12-benchmark-20261029/absence-taglish-diagnosis/README.txt`).
- Full suite at `0d6ebac` (A/p11-fullsuite-20261030a, 4 batches): 7271 pass / 1608 subtests, 6 skip / 2 xfail,
  all 4 batches exit 0 (later commits docs only).

## Versions and Digests

Gemma 4 E4B `gemma-4-E4B-it-UD-Q4_K_XL.gguf`, llama.cpp build b11723-31288c9c6, chat template sha256 74a88f94…f6b3.
Package `p11-faq-split-20261028/runtime-package` (draft-chunks sha256 480a0ff6…9fbf). Hosted active release
unchanged: `p11-research-corrected-20261026` (78 chunks / 39 curricula).

## Decisions

Owner 30 Oct: single runs disclosed; write-up first, hosted activation only if time remains (ledger).

## Known Failures or Blockers

v2 failures (12) listed in the report section 4. Hosted 560 activation pending (needs staging + selected review).

## Next Action

Hosted 560 activation per the session handoff; then report section 8, the Phase 12 handoff; supersede this checkpoint; validate and update INDEX/progress.

## Do Not Repeat

Benchmark runs (A, C, rerun, Tagalog, shorthand, loose); selector replays; statistics.

## Context consulted

30 Oct: master 17 (Phase 12) and 26; Phase 11 handoff; Context/response-time-recommendation.md; thesis physical
17–18 (Scope and Limitations, text via pypdfium2: undergraduate only, read-only, clarify/unavailable/referral,
private-file cross-session evaluation) and the routing PNG (RAG/Hybrid/Symbolic -> integration -> generation ->
validation loop; condition C covers all three paths). Discrepancy: thesis accepts English/Filipino/Taglish
queries; inputs still do, replies are English/Taglish (owner 27 Oct, master 26). No scope or routing change.
