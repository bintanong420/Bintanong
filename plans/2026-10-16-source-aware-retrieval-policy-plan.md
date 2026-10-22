# Source-aware Retrieval Policy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan inline, task by task. Steps use checkbox syntax for tracking.

**Goal:** Integrate the approved conservative source/claim policy into actual engine context assembly.

**Architecture:** A trusted, immutable-in-use candidate policy validates and projects complete source snapshots. The engine checks actual RPC bindings, selects the supplied subject, assembles once and obtains the claim assessment from actual emitted evidence. Legacy calls retain v1 behavior; opt-in v2 calls never report sufficient/ok.

**Tech Stack:** Existing Python 3.13, standard library, existing retrieval/catalogue/claim/context helpers and pytest environment; no dependency changes.

**Spec:** [Approved design](2026-10-16-source-aware-retrieval-policy-design.md), approved by the owner with “ye i approve” after `ff53c65`.

## Global Constraints

- Phase 05 stays active/blocked; no SQL, public endpoint, CLI flag, activation or Phase 06 work.
- Use the existing isolated p05 worktree and preserve the owner's artifact changes.
- Use exact supplied canonical subjects/claims; no interpretation, new benchmark wording or source judgment.
- All opt-in results keep candidate-only/inactive/unverified-authorization flags and unassessed answer sufficiency.
- Retain whole required groups, source limits, conflict precedence and exact serialized token counts.
- Raw evidence/logs/test temporaries live under workspace `audit-evidence/p05-source-aware-policy-20261016/`; preserve all sealed roots.
- Reviewed source holds and all prior accepted cases remain unchanged; reuse saved vectors without new encodings.

## Review Focus

- A claimed release match does not prove runtime membership: v2 must stay inactive and explicitly authorization-unverified.
- Packaging differences must not mask changed text, ordered spans, full type_fields or conflicting duplicate identities.
- Off-subject conflicting editions/curricula must be examined before subject filtering.
- Empty or deduplicated context must not be replaced by caller-supplied emission IDs or promoted to available fields.
- Invalid/missing intent and non-uncalibrated settings names must never bypass the opt-in gate.

## Files and execution

Create `backend/bintanong_retrieval/evidence_policy.py` and `tests/test_retrieval_evidence_policy.py`.
Modify `engine.py` at its constructor/retrieve flow and README at the opt-in module description.
Maintain this plan, the active checkpoint/current progress and a delivery report in `plans/`.
Use native inline execution as already required by the active phase plan. Owner design/implementation
approval covers this mechanical plan; do not introduce a second permission request.

### Task 1: Bind a trusted source snapshot

**Interfaces:** `SourceAwareEvidencePolicy(*, release_id, embedding_set_id, chunks, catalogue, claim_reviews)`;
private intent validation, RPC binding, subject selection, assessment and metadata methods used by Task 2.
Use a fixed `source-aware-candidate-policy-v1` identity and canonical JSON digest. Root v2 safety
flags identify candidate status; `evidence_policy` contains version, digest, intent and assessment/not-run reason.

- [x] Write synthetic tests exercising transport-field changes, whole-snapshot validation,
  packaging extras, ordered span changes, duplicate/unknown IDs, release/set mismatch and defensive copies.
  Tests must fail explicitly because the source-aware policy is missing, rather than fail during collection.
- [x] Run `pytest tests/test_retrieval_evidence_policy.py -q -p no:cacheprovider` with external basetemp;
  expected RED assertions identify the missing feature.
- [x] Implement the class and a `PolicyBindingError` in `evidence_policy.py`. Reuse existing catalogue/
  register preparation and reporting functions. Do not weaken their full-payload validation.
- [x] Run the new tests plus existing candidate-subject/claim tests; expected GREEN with no failing cases.
- [x] Record RED/GREEN and commit this independently testable snapshot module/tests increment.

### Task 2: Integrate with actual engine evidence

**Consumes:** Task 1 policy and existing `build_context`/runtime RPC.
**Produces:** `RetrievalEngine(..., *, evidence_policy=None)` and
`retrieve(request, *, subject_id=None, requested_claims=None)` using v2 only when opted in.

- [x] Add engine-level RED tests for exact legacy v1 compatibility, intent rejection before encoding,
  positive-field uncalibrated output, reviewed absence/omitted limits, unknown/mixed claims,
  actual empty/over-budget/invalid-citation/missing-neighbor context, whole groups and conflicts.
  Include root safety flags, unchanged settings fingerprint, actual source citations and arbitrary policy names.
- [x] Run new engine tests; expected failure is unsupported constructor/intent behavior or incorrect status.
- [x] Wire validation/binding before assembly, preserve original legacy flow, check opt-in conflicts before
  filtering, assemble retained subject rows once with shared citations/group metadata, and assess actual IDs.
  Binding errors clear evidence/context; early retrieval failures carry a null assessment and not-run reason.
- [x] Run all retrieval non-database and candidate helper regressions; expected GREEN. Update README.
- [x] Record RED/GREEN and commit engine/tests/documentation increment.

### Task 3: Verify, replay and close this bounded increment

**Consumes:** Task 2 v2 engine and already saved accepted document cases/vectors/rankings.
**Produces:** Ignored replay evidence, a repository delivery report and one fresh whole-change review.

- [x] Replay compatible saved document cases through the real engine with saved-score/runtime doubles
  and an exact tokenizer-only counter; disclose supplied intent and simulated storage/encoder roles.
  No fresh embeddings, parameter grid or unsupported end-to-end/runtime-authorization claim.
- [x] Run the complete project pytest suite in the existing offline environment with no pytest cache,
  external basetemp/TEMP and existing model/cache paths. Record all actual failures, skips and warnings.
- [x] Request one fresh whole-change review, then reproduce/fix material findings with RED/GREEN;
  preserve any declined findings as explicit rulings. No per-task implementer/reviewer agents.
- [x] Verify original seals read-only, links, phase validate and expected blocked can-advance;
  update report/INDEX/handoffs/checkpoint/progress and explicitly commit only task paths.

## Verification commands

Use `C:/Coding-projects/bintanong_workspace/audit-evidence/p05-real-retrieval-readiness-20261012/venv/Scripts/python.exe -B -m pytest`
with `-q -p no:cacheprovider --basetemp <raw-root>/<unique-step>` and the named test files.
Full suite target is `tests`; retain raw logs. No installs, downloads, dependency/lock changes or shared writes.

## Execution ledger

- Owner approved the complete design at `ff53c65`; native execution is already specified by the active phase plan.
- Pre-flight: Task 1's policy methods are consumed by Task 2; both use the same snapshot/intent schemas.
- Pre-flight: Task 3 consumes actual Task 2 engine results, never independent caller-authored emission lists.
- Project instructions require repository plans/checkpoints plus ignored audit-evidence logs. Use those existing
  locations rather than a separate skill scratch ledger, and retain them for the next agent.
- Estimate requested by owner: approximately 80% technical Phase 05 completion, rough 75–85% range;
  not a weighted measurement or formal exit result. Core retrieval exists; this work integrates source/claim gates.
  Final integration, saved-case verification, testing/review and source/release governance remain.

- Task 1: complete — missing module RED; 39 tests / 139 subtests GREEN in 0.70s; snapshot/transport bindings and original helper regressions verified.

- Task 2: complete — engine integration RED then 104 tests / 184 subtests GREEN, 1.35s; legacy behavior and conservative source-aware output verified.

- Final review: two Important findings independently reproduced and fixed in one RED/GREEN pass; 106 tests / 188 subtests GREEN. Final full-suite/replay verification pending.

- Task 3: complete — corrected full5388tests/689subtests pass359.99s; corrected saved39-case replay18/21; single final review/two material fixes RED/GREEN verified; raw seal and phase gates preserved. Final documentation closure follows.
