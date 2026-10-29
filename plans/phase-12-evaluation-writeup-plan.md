---
artifact: phase-plan
phase: 12
status: ready
preparation_only: true
master: plans/master_implementation_plan_original_long.md
previous_handoff: plans/phase-11-handoff.md
---

# Phase 12 evaluation write-up plan

**Goal:** turn the benchmark runs already made into a thesis-ready evaluation report (master 17) that states what
was measured, with uncertainty, and what was not. Owner finish date: 30 October 2026.
[Pre-phase research](2026-10-30-phase-12-pre-phase-research.md).

## Constraints

- No new model, dependency, scope or source change; accuracy work is frozen (no prompt/code tuning against the
  benchmark). Deployment (Phase 13) cancelled by the owner.
- Disclose: 40/50 cases were development cases; author-written expectations, single author scorer; single runs;
  condition B skipped; warm-inner latency is not student-visible latency; no institutional validation.
- Raw outputs stay in ignored `audit-evidence/p12-benchmark-20261029`; tracked docs carry summaries only.

## Tasks (dependency order)

1. Batched full suite on the frozen head (`audit-evidence/p11-fullsuite-20261030a`). Exit 0 in all batches.
2. Paired statistics from existing outputs (done: `p12-benchmark-20261029/stats/paired_stats.py`): Wilson 95%
   per condition; exact McNemar A vs C and C vs its rerun.
3. Owner decision: hosted 560 activation now (staging -> activate RPC -> readback -> smoke; corrected78 rollback)
   or keep deferred. Only if approved.
4. Evaluation report `docs/evaluation/phase12-evaluation-report.md`: conditions, dataset, per-category/language
   tables, statistics, robustness sets, failure analysis, latency, private-file test evidence, master 17.3 metric
   coverage table (measured / not measured and why), limitations.
5. Phase 12 handoff; INDEX and current progress.

## Verification

- `phase_state.py validate` and `can-advance` after the handoff.
- Report numbers cross-checked against `summary.json`, `paired_stats.json` and the run `results.jsonl` files.
- Markdown link check by inspection (relative links resolve).

## Exit gate

Full suite passes; the report exists with every number traceable to an evidence file; limitations and not-measured
metrics stated; owner has seen the summary.
