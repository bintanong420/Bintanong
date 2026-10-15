# Source-limit claim report implementation plan — 15 October 2026

Use executing-plans inline, synthetic TDD and one final independent review.
Baseline85986fd/product5cd5120. Spec: the next action in
[the subject-selection report](2026-10-15-candidate-subject-selection-report.md),
master10 and settled [response requirements](2026-10-15-natural-query-response-requirements.md).

## Design and limits

Add one optional metadata report after retrieval. Exact trusted caller claim
strings can match existing unresolved `source_limits[].affected_claims` on the
selected subject's source-bound chunks. A matching limitation reports
`not_established`; every unmatched claim stays `unassessed`, including when fields,
scores or assembled context look complete. No affirmative support outcome exists.
Missing subject/claims require those hints; unknown subjects select no source limits.

Use the existing public subject selector to validate the complete catalogue/chunk
snapshot. Do not create a parallel catalogue, alter payloads or infer absent facts.
Return copied source-limit records, source/reading/chunk identities and whether
each referenced chunk ID was supplied as emitted. Context IDs describe literal
identities only; they do not prove a cited limit was serialized. Report known
source limitations even when the corresponding chunk was not retrieved, with that
absence explicit. Reject unknown/duplicate context IDs and malformed source-limit
metadata; preserve all unrelated declared limits as visible trace information.

`build_candidate_claim_report(catalogue, chunks, *, subject_id=None,
requested_claims=None, emitted_chunk_ids=None)` lives in
`backend/bintanong_retrieval/candidate_claims.py`. Inputs are trusted researcher
metadata. Missing/empty claims cannot vacuously establish coverage. Outputs bind
the subject catalogue digest, requested claims, per-claim statuses, copied limits
and source/context identities; candidate/inactive/runtime-unimplemented flags
remain explicit. Aggregate decision is `insufficient_evidence` if any requested
claim has a declared unresolved limitation; otherwise `unassessed`. Missing hints
and unavailable subjects get explicit statuses. This is a deterministic declared
limitation report, not semantic inference, citation verification or authentication.

F09's existing current-year limitation can match a trusted caller claim annotation.
T1 deadline and U3 GCash claims have no matching source-declared limitation, so
they stay unassessed. Never load `source-claim-labels.json` or gold context IDs into
the helper/annotation preparation to force unsupported-case success. No new source
gap or field judgment is authorized here. No default gate, engine/public contract,
query parser, model call, new dependency, source edit, DB/API/runtime/Prolog change,
activation or Phase06. Keep F04/G01/G02 and all settled owner decisions intact.

## Task 1: source-limit report

- [ ] Create synthetic `tests/test_candidate_claims.py`: known limitation survives
  complete/empty/unrelated context IDs; unknown claims stay unassessed; no positive
  outcome, missing hints, stale catalogue, wrong subject, duplicate/malformed claims
  and context IDs, malformed/foreign source-limit identities, nonmutation.
- [ ] Run RED for missing module; implement the smallest function and validation.
  Validate unresolved-limit IDs, issue/message/claim strings and source/version
  identity; complete existing source payloads remain bound by the subject catalogue.
- [ ] GREEN focused source/claim/context/query/curriculum regressions. Add README
  usage and trust limits. Full existing offline suite, Python3.13 existing venv,
  pytest no cache and a unique external basetemp. Commit explicit verified paths.

## Task 2: saved-context sidecar and closure

- [ ] New ignored workspace audit root, never a writing destination in old seals.
  Freeze researcher claim annotations before loading accepted questions/evaluations:
  current-year claim uses exact existing F09 affected-claim wording; deadline and
  GCash use explicit descriptive claims with no invented source-gap match. These
  are caller conditions, not measured NLP or fresh owner/source approval.
- [ ] Reuse saved nine accepted cases, raw and subject-filtered attempts, the
  counterfactual wrong-subject control and27unchangedchunks. Run reports as sidecars
  only; rankings, tokens, citations, source limits and original contexts unchanged.
  Keep empty/unknown-claim controls; do not create new benchmark wordings or vectors.
- [ ] Independently recompute expected source-limit matches without the new helper,
  verify digest/preservation/source-limit/context identity checks and report counts.
  Known T2 limitations and unassessed T1/U3 are expected conditional observations,
  not unsupported detection accuracy or completed Phase05 calibration.
- [ ] One final fresh-context review. Curated report/checkpoint/current progress/
  INDEX/CLI pointers, evidence seal and explicit Conventional Commit. No activation.

## Review focus and completion

Check exact matching versus unsafe substring/case normalization; known source gap
versus absent context; malformed source identity versus unknown claim; defensive
copies; empty-claim vacuity; and accidental reuse of expected labels as inference.
The helper cannot find an undeclared gap, certify sufficient evidence, establish
payment permission/prohibition/currentness or settle source authority. Task4/6
and formal phase exit remain open. Existing source-bound limitations and all
previous seals/originals/weights/owner artifact changes must be preserved.
