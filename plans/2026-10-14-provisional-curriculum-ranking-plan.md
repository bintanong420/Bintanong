# Provisional curriculum ranking experiment plan

> Execute inline using the existing offline candidate tools. Owner instructions to
> continue thesis testing supply authorization; no additional plan approval needed.

**Goal:** Measure real retrieval on the accepted curriculum questions while school
verification remains pending, without treating missing scope as an empty gold set.

**Architecture:** Reuse the 36 recorded query vectors and encode only the eight
reviewed undergraduate curriculum payloads with the same strict local SEA-LION
configuration. Compare real cosine rankings before and after trusted curriculum
metadata selection, then assemble fully cited candidate contexts.

**Spec:** `2026-10-14-thesis-development-source-use-clarification.md`, the accepted
12-scenario evidence packet, `phase-05-retrieval-plan.md`, undergraduate scope and
source-gap policies. This is a bounded experiment inside Phase 05, not its exit gate.

## Constraints and review focus

- Keep source registers pending; no fabricated school authorization or validation date.
- Preserve all PDFs, reviews, prior seals, query wordings and external model weights.
- Eight payloads fit the encoder's 512-token limit; no truncation or new downloads.
- Twelve explicit-edition curriculum variants can be scored. Six BSCS variants
  require curriculum clarification. Eighteen policy variants remain unranked because
  their candidate applicability is unresolved; neither set counts as unsupported cases.
- Trusted scope annotations are supplied separately from the question. This run
  does not demonstrate automatic extraction of program or curriculum from free text.
- One candidate per explicitly selected program/edition makes scoped positives easy;
  show unfiltered rankings too. Precision uses the evaluator's fixed k denominator.
- Positive-only results on eight rows cannot establish a global threshold, negative
  detection, whole-corpus accuracy, formal calibration or institutional readiness.

## Tasks

- [ ] Bind current vectors, candidate chunks, catalogue, original hashes, pending
  registers and model manifest in ignored `audit-evidence/p05-provisional-curriculum-retrieval-20261014/`.
- [ ] Encode eight document payloads without a query prompt; validate identity,
  exact token lengths, 1024 finite dimensions and L2 normalization.
- [ ] Record unfiltered observations for all 18 curriculum variants, then scoped
  observations for the 12 eligible variants using `select_candidate_curriculum`.
  Keep six clarification cases and 18 policy cases outside numeric evaluation.
- [ ] Run `evaluate_rankings` for k=3/5/8 and exploratory thresholds
  0/0.25/0.5/0.75/0.9; select no production threshold. Build complete scoped contexts
  using `build_context(..., compact_citations=True)` with exact 2048-token budgets.
- [ ] Independently recompute scores/labels/citation bindings, verify source and
  historical preservation, run relevant existing tests, seal generated evidence.
- [ ] Commit a concise report and updated checkpoint/progress/handoff/index with
  measured limits and the exact next action. Product code remains unchanged unless
  an actual defect is discovered; any behavior fix then requires TDD and its checks.

## Verification and recovery

Use the existing Python 3.13 environment, cache-free pytest and external basetemp.
Generated scripts/vectors/results/logs stay ignored. Check all source identities,
the prior context-code snapshot exception and current product digests explicitly.
Commit curated text only. Repeat only affected source embedding/ranking if later
school evidence changes an edition or its applicability; query vectors are reusable
when their strings and encoder identity remain unchanged.

Context consulted on resume: thesis physical17–18 (printed16–17), routing PNG and
master-plan section10. No scope/routing discrepancy; undergraduate advisory scope
and private-upload separation remain intact. Formal Phase 05 advancement is blocked.
