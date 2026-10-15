# Source-bound claim reviews implementation plan — 15 October 2026

Execute inline with synthetic TDD and one final independent review. Baseline
d2906ca/productc86333b. Spec: [the prior report's next action](2026-10-15-source-limit-claim-report.md),
master10 and standing natural-question/source-gap requirements. Extend the
existing `candidate_claims` module; avoid another parallel reporting layer.

## Design

Add `prepare_candidate_claim_reviews(catalogue, chunks, reviews)` and optional
`claim_reviews=None` to `build_candidate_claim_report`. The default report stays
byte-for-byte compatible. The register is trusted researcher review metadata,
bound to the existing complete source/subject catalogue digest. It does not
authenticate a reviewer, inspect original source truth, interpret a query or
activate output. An integrity digest detects accidental changes only.

Each review has exactly `subject_id`, `claim`, `finding`, `reviewed_chunk_ids`,
`field_refs`, `basis_ref`, `basis_sha256`. Require a known subject and complete
subject snapshot in `reviewed_chunk_ids`; no partial selection can assert absence.
One record per exact subject/claim; lowercase SHA256 and a nonempty basis reference
bind a separate source-side audit artifact. Preserve deterministic order/copies.

`finding` is `visible_fields` or `not_stated_in_selected_fields`. Visible reviews
require unique `{reading_id, field_name}` refs to that subject's existing field
associations: nonblank, present value, review-event hash, valid nonempty span
indexes and matching span source/version. Negative reviews must have no field refs.
The programmer cannot verify semantic truth from these metadata checks. Complete
existing payload hashes preserve qualifiers, source dates, conditions and gaps.

With a valid register, exact requested claims can receive:

- `not_established` for an existing declared limitation or a trusted selected-field
  absence review. This is not a university-wide absence, ban, expiry or permission.
- `reviewed_fields_available` when referenced fields and every transitive required
  dependency are in the supplied emitted IDs. Report copied field/value/span data.
- `reviewed_fields_not_in_context` otherwise, distinguishing unknown emission from
  an explicitly empty context. Carry missing required IDs without truncating groups.
- `unassessed` when no review or declared limit matches. No borrowing another
  subject or substring/case matching. Existing unresolved source limits take
  precedence over a visible-fields review for the exact same claim.

Aggregate known negatives as `insufficient_evidence`, missing reviewed context as
`insufficient_context`, all requested field matches as `reviewed_fields_available`,
otherwise `unassessed`; retain missing-hint statuses. Answer sufficiency remains
unassessed and all runtime/inference/activation flags remain false. A field match
is conditional evidence availability, never a certified answer or eligibility.

## Task 1: report extension

- [ ] Add synthetic tests in `tests/test_candidate_claim_reviews.py`: register
  determinism/staleness, complete snapshot, unknown/cross-subject/duplicate refs,
  blank/foreign spans, zero as explicit value, event metadata, defensive copies,
  negative/unknown/mixed claims, known-limit precedence, transitive dependencies,
  empty/unknown emission and default-report compatibility.
- [ ] Observe missing-function RED; implement smallest extension in
  `backend/bintanong_retrieval/candidate_claims.py`, document README trust limits.
- [ ] Focused GREEN then full offline suite with the existing Python3.13 venv,
  no pytest cache, unique external basetemp; explicit product commit/checkpoint.

## Task 2: source-side preparation and saved-context checks

- [ ] New ignored workspace evidence root. Before loading cases, rankings, labels
  or scores, freeze the complete two-row pre-enrollment/three-row fee field audit,
  their dates/conditions/limits, and source-side review records. Reuse existing
  confirmed source values; do not re-open settled readings or add content.
- [ ] Bounded reviews: selected pre-enrollment fields do not state the requested
  second-semester2026–2027 enrollment deadline; selected fee fields do not state
  GCash permission. These are explicit researcher source judgments, independently
  checked against the full selected fields, not newly owner-confirmed source gaps
  or automatically discovered facts. A contradiction requires actual human review.
- [ ] Positive record: only the as-printed three-lecture-unit example's complete
  F01/F08/F09 field group, including rate/date/effectivity and existing limits.
  This does not label the sum per-student/class-total or certify current billing.
  Validate it with structural field/context probes; no new student question.
- [ ] Apply the frozen register to the same1430saved raw/filtered attempts with
  explicit caller annotations. No benchmark expected labels/gold IDs enter review
  preparation or report logic; no new wordings, encodings, reranking or source edits.
- [ ] Independently verify register/snapshot/field/span bindings, conditional
  report counts, old default replay byte-for-byte and preservation hashes. Record
  known-limit/absence-review/field-context outcomes separately; not NLP accuracy.
- [ ] One final fresh-context review, final evidence seal and report/continuity
  commit. Keep owner artifacts and prior seals/originals/vectors intact.

## Review focus and exclusions

Complete source-audit scope versus arbitrary label insertion; source-basis hash
versus authentication; source limitation versus positive field availability;
transitive context versus literal primary IDs; default compatibility; mixed
unknown claims; mutation and invalid field provenance. Do not consume
`source-claim-labels.json`, expected labels or gold context IDs as report inputs.
Do not count conditioned researcher findings as automatic unsupported detection or
representative calibration. No engine/public contract/SQL/DB/API/Prolog/NLP changes,
new dependencies/downloads, activation or Phase06. FormalTasks4/6 remain open.
