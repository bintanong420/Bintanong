# Offline course-filter ranking comparison plan

**Goal:** Compare the reusable course selector with the saved semantic/curriculum
rankings on the unchanged accepted questions, while measuring explicit-code coverage.

**Spec:** The next action in `2026-10-14-offline-course-selector-report.md`,
authorized by the owner's continuation request. Baseline `80d66b6`; helper `f9b1502`.

## Design and constraints

Use an ignored experiment script, not a new product/runtime interface. Rebuild the
eight-row index through complete reviewed preparation, reuse all36query vectors
and8document vectors, and recompute the18curriculum query rankings. Verify the
exact baseline rankings before applying restrictions. Gold chunk IDs are used only
for scoring after selection, never as target hints or ranking inputs.

Researcher hints come from exact accepted question fragments: Q2 requests `CC5`,
Q8 requests `AD-2/L`. Other questions receive no single-code hint. Nursing/Tourism
name titles; Criminology compares two codes; practicum names a course without its
code. Do not manufacture hints from expected source rows or choose the first code.
No new question, automatic extractor, entity pipeline or multi-target API.

Compare the unchanged curriculum-only default (12positive scoped variants) with
the optional strict course helper (3Architecture variants). Record9missing-target
helper controls separately; these are input-coverage results, not failures of the
default semantic retrieval. Actual6BSCS questions still require curriculum and
18policy questions retain unresolved applicability. Controlled edition hypotheses
reuse the6existing CC5 branches and6practicum branches; only CC5 has an explicit
code hint. Preserve all hypotheses, including missing-target results.

Use existing evaluation k=3/5/8 and the prior exploratory threshold grid; do not
select a global threshold. Rebuild complete cited contexts through the current
context helper, reusing exact token counts only for identical complete rendered
strings. Preserve source versions, field associations, limitations and citations.

All raw observations, scripts, hints, vectors and logs stay under ignored workspace
audit-evidence. Existing Python3.13/assets only; no installs, downloads, model
execution, database/runtime/Prolog/source activation or Phase06 advancement.

## Work and verification

- [ ] Verify prior evidence seals, source relocation bindings and vector/query identities.
- [ ] Run the bounded comparison and retain all36case statuses, all12controlled
  branches, annotated hints, recomputed rankings, metrics and complete contexts.
- [ ] Independently check scores, filtering coverage, every citation, unchanged
  questions/default outputs and dependency hashes. Run applicable existing tests.
- [ ] Record results/limitations/next action in repository progress/checkpoint/index,
  verify the ledger and commit explicit curated documentation only.

No product behavior changes are planned; the previously verified helper remains
unchanged. Synthetic TDD is required if a genuine product defect is discovered.
Review focus: hint/gold separation, missing roles, scope precedence, conditional
denominators, fixed-k precision, duplicate context counting and stale saved vectors.

## Resume context

Read both handoff skills, active phase plan/checkpoint/blocked handoff and prior
Phase04 complete handoff. Consulted actual thesis physical17–18, routing PNG,
master section10, undergraduate scope/source-gap policies and dataset locations
previously read in this session; no discrepancy. Preserve owner artifact changes.
