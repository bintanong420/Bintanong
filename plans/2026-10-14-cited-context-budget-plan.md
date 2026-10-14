# Cited curriculum context budget diagnostic

**Goal:** Check whether each of the eight reviewed candidate curriculum rows fits
the existing retrieval context budget when complete citations are serialized.

**Spec:** Master10.1 context budget/citations, current Phase05 plan, preflight report
and unchanged candidate chunks. Owner says proceed; school verification is deferred.

Use existing `build_context` and strict local QueryEncoder's exact tokenizer offline.
The candidates are manually supplied for assembly only, with similarity null and no
ranker/RPC/release. Check each row separately so old/new BSCS alternatives are never
combined into an eligibility claim. Preserve source/register/event/chunk/history hashes.
No new query, source fact, vector, authority/effectivity decision or active release.

- [ ] Verify current candidate packet/code/source/model bindings and context contract.
- [ ] Count all eight complete contexts with a high diagnostic cap, then replay
  1024/2048/4096/8192 budgets through existing builder; preserve full text/citations.
- [ ] Separate original source length from added citation/metadata repetition.
  If retention would change source content, show original/affected region to owner.
  If the issue is purely technical serialization, record a bounded proposed fix
  and use synthetic TDD before changing product behavior; do not remove citations.
- [ ] Record actual counts/gaps, direct preservation checks, required verification,
  sealed ignored evidence and current checkpoint/progress/handoff. KeepPhase05blocked.

Evidence root: workspace/audit-evidence/p05-cited-context-budget-20261014/.
Baseline22896c1; existing p05 worktree, Python3.13.7, external weights and packages.
Thesis physical17–18/routing PNG/master10/current handoff consulted; no discrepancy.
Source-use verification remains deferred. Future batch excludescollegeCharters;
possiblememoranda such as student vehiclegatepass, none newly received.

## Measured result and bounded correction

Baseline: payload286–478tokens; fullcited contexts2000–3528. Only2/8fit2048,
all8fit4096. Existingbuilder correctly withholds entire over-budget groups.
113citation objects/source text unchanged; cause is repeated version/hash prefixes
in the display serialization, not missing PDF text or a source-retention choice.

Ruling: add `build_context(..., *, compact_citations=False)` and corresponding private
serializer flag. Default output stays byte-identical. Opt-in context displays JSON
citation groups by exact(version_id,byte_sha256,page), retaining every locator in
its original per-group order. Structured evidence/citations and payload remain
identical. No engine/settings/API/RPC caller switches format in this task. Cost:
later governed runtime integration must opt in; this alone does not activate sources.

- [ ] SyntheticRED: compact assembly recovers full evidence under a budget where
  repeated prefixes do not fit; retain every locator, multi-page binding/order,
  complete required-neighbor groups, unchanged default/input and invalid flags.
- [ ] MinimalGREEN serializer/context flag; related and full suite, actual8row
  opt-in versus original replay, exact limits and preserved113citations/sourcefields.
- [ ] One fresh final review per executing-plans; one TDD fix pass for consequential
  findings if any, no secondreview. Seal evidence and update phase ledger/report.

Execute inline with executing-plans/TDD; no source-content decision needed for this
lossless citation display. No new dependencies/modelweights or user questions.

Implementation: expectedRED6failures0.48s (missingflag), relatedGREEN83tests/
125subtests1.70s. Opt-in only; original runtimecaller stayslegacy. Actualreplay/full
suite and onefresh finalreview pending; sourceverification stilldeferred.
