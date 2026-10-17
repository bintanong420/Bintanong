# Candidate subject selection implementation plan — 15 October 2026

Use executing-plans inline with synthetic TDD and one final independent review.
Spec: [the temporal-query failure report's next action](2026-10-15-temporal-unsupported-evaluation-report.md).
Baseline245fd73/product7456613. This small offline module extends the existing
trusted-caller canonical-hint design; no second retrieval architecture or NLP.

## Design

Create `backend/bintanong_retrieval/candidate_subject.py` and
`tests/test_candidate_subject.py`. A trusted researcher supplies complete candidate
chunks and explicit assignments `{reading_id, subject_id, basis_ref}`. The builder
derives IDs from source readings, never from question/gold labels. Bind every
chunk's complete JSON payload, source/version/reading IDs, audience and required
neighbors in a deterministic catalogue with an integrity digest. The digest
detects accidental changes; it is not authentication or institutional approval.
Researcher-supplied assignments remain trusted metadata, not fresh source review.

Interfaces:
- `prepare_candidate_subject_catalogue(chunks, assignments)` returns schema
  `bintanong-candidate-subject-catalogue-v1`, inactive/candidate flags, bindings,
  assignments and `catalogue_sha256`.
- `select_candidate_subject(catalogue, chunks, *, subject_id=None)` validates the
  catalogue against current full chunk bindings and returns `needs_subject` for
  None, `unavailable` for an unknown canonical subject, or `matched` with its
  chunk IDs/assignments. Every result keeps claim coverage unknown and runtime
  filtering unimplemented. It never accepts a natural query, chooses source age,
  verifies a year, asserts claim support or changes the original chunks.

Require unambiguous reading/chunk IDs, valid source hashes/version bindings and
well-formed required IDs. Assigned rows need an existing applicability reference
and undergraduate-only audience metadata; parser success is not human approval.
Every required dependency of an assigned row must be present and assigned to the
same subject, including transitive/cyclic links. Eight curriculum candidates may
remain unassigned; their existing course/curriculum selectors remain authoritative.
Unassigned rows are explicitly visible through catalogue bindings, not silently
promoted. No unsupported audience or held reading enters the selected derivative.

## Constraints and review focus

No engine/query/public-contract/SQL/DB/API changes, new dependencies, installations,
source conversions, model calls, old-vector edits or activation. Preserve owner
artifact changes and all original/sealed evidence. Unknown curriculum/currentness
and F04/G01/G02 holds remain unchanged. Source-subject membership is a researcher
classification based on existing reviewed provenance, not owner confirmation of
new policy content. Corpus/query wordings are unchanged and no new review needed.
Keep experiments using caller subjects visibly annotated as non-automatic NLP.
Review stale payload/source/audience bindings, malformed/duplicate assignments,
cycles/missing/cross-subject dependencies, forged digest assumptions, unknown hints,
result mutation and accidental promotion of subject matches into sufficient answers.

## Task 1: source-bound catalogue and selector

- [ ] Write synthetic tests for matching/unknown/missing subject, explicit input
  validation, stale payload/hash/version/audience, duplicate readings/assignments,
  dependency closure/cycles/cross-subject refusal, digest/flags and immutability.
- [ ] Run RED (missing module), implement the smallest helper, verify GREEN and
  relevant context/query/curriculum regressions. Document trusted-input limits.
- [ ] Run full offline suite with existing Python3.13, no pytest cache, unique
  external basetemp; explicit verified Conventional Commit with checkpoint update.

## Task 2: existing-vector diagnostic and closure

- [ ] Prepare a frozen external subject catalogue for the19selected policy rows
  in seven source subjects from existing reviewed field/record provenance. Preserve
  eight unassigned curriculum rows, full limitations and source bindings. Record
  assignment basis and researcher authorship before applying any query contexts.
- [ ] Annotate only the nine accepted T1/T2/U3 cases with explicit caller subjects
  (pre-enrollment or special-class fees), not source IDs/year validation or gold.
  Reuse243saved scores/27document vectors/ninequery vectors; retain raw controls.
  Select subjects before threshold/top-k and preserve declared dependencies. Compare
  the existing k/threshold/budgets and explicit prefixes without adopting a default.
- [ ] Independently verify selection, contexts, tokens, citations, source limits,
  hashes and untouched raw observations. A subject match cannot answer an absent
  deadline, current-year validity or GCash-permission claim.
- [ ] One final fresh-context review, focused checks and final report/evidence seal.
  Curate current progress/checkpoint/INDEX/CLI pointers, preserve raw evidence under
  workspace/audit-evidence, explicit staging only. No activation or Phase06.

Expected result: better subject-relevant context under trusted caller annotations,
with source/claim uncertainty retained. If measurements disagree, report them;
never tune against gold or relabel the accepted questions. Formal Task4/6 remain
open until development coverage/unsupported behavior and final gates are earned.
