# Saved-ranking context-prefix diagnostic

Use the executing-plans workflow inline. This is a read-only offline diagnostic,
not a runtime behavior change. Continue from product `feaa961` / report `91bba1f`
and the exact approved questions/evidence in the preceding evaluation.

## Purpose and fixed inputs

U2 recovered complete expected evidence at k3/0.5/2048, but context assembly also
reported budget refusals for additional unrelated primary groups. The current
engine treats any context gap as insufficient context. Diagnose that distinction
without silently ignoring refusals, selecting from gold, or assuming that a
gap-free context answers the requested claim.

Reuse all 27 candidate chunks, 54 saved query vectors/rankings, source versions,
source-limit/dependency bindings and the exact approved 18 new variants /36 prior
variants. Six prior BSCS curriculum holds remain holds. No re-encoding, source
conversion, model-weight loading, downloads, installs or dependency changes.
The three A1 variants retain separate ambiguity traces. Scope traces are explicit
researcher request annotations, not measured automatic interpretation.

## Bounded comparison

- [x] Verify the previous 43-file seal, its preserved inputs and tokenizer hash.
- [x] Reproduce previous primary candidates and contexts at each saved k3/5/8,
  threshold0/0.25/0.5/0.75/0.9 and budget2048/4096 combination.
- [x] For each combination, assemble ranking prefixes of length1 through the
  configured maximum k, retaining all declared transitive required neighbors.
  Prefix length uses ranking order alone, never expected-reading IDs or results.
- [x] Record actual primary IDs/scores, returned IDs/limits, budget and invalid
  refusals, exact tokens and original citations for every attempt. Separate
  missing expected evidence, unsupported claim coverage and omitted extra groups.
- [x] Compare fixed one/two/all-primary strategies and an **experimental**
  longest-gap-free-prefix strategy. The latter is a diagnostic only: record its
  omissions and evaluate against gold afterward; do not install it as a policy.
- [x] Include raw S1/S2/P1 rankings and A1 diagnostic controls to show whether
  apparently valid compact contexts still contain wrong/ambiguous evidence.
- [x] Independently replay selection, token counts, citations and summary counts;
  run relevant existing context tests without cache and with external basetemp.
- [x] Record results and a qualified progress estimate; commit curated report,
  checkpoint/current progress/INDEX/CLI pointers and seal new ignored evidence.

## Constraints and completion evidence

Master10 and thesis physical17–18 govern. No new benchmark wordings, source-content
decisions, program/edition guesses, additional source acquisition, gold padding,
source-gap removal or activation. Preserve full originals and all earlier seals.
All work stays in the existing p05 worktree; owner artifact changes stay unstaged.
New raw evidence lives under workspace/audit-evidence/
`p05-context-prefix-diagnostic-20261015/`. No product edit is planned, so no new
TDD/full-suite rerun is needed unless findings justify an implementation change.

The report must say whether complete evidence with rejected extras differs from
missing required evidence, and whether prefix selection loses important context.
Any future opt-in implementation needs its own synthetic RED/GREEN and review.
Formal Phase05 calibration/governance/exit gates and Phase06 boundary remain.

## Progress estimate basis

Planning estimate at resume: approximately **80% of Phase05 technical work**,
roughly **75–85%** uncertainty range, not measured corpus accuracy or formal exit
completion. Four of six top-level tasks are delivered; remaining tasks are uneven
in size. Finish context/coverage selection, representative unsupported-case
calibration and final verification/handoff. School-verification timing is unknown
and separate from authorized offline work. Revisit this estimate after the
diagnostic instead of treating the count of passing fixtures as a completion score.

Results recorded in2026-10-15-context-prefix-diagnostic-report.md; no product policy
installed. Exact comparisons/replay preserved in new ignored evidence root.
