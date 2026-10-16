# Source-aware retrieval policy integration — 16 October 2026

Status: approved by the owner with “ye i approve” after `ff53c65`.
Implementation follows the linked dated plan; approval adds no source-content
decision, institutional verification or activation. Original design baseline `88c50de`.

## Purpose and scope

A student can ask about a printed fee or procedure even when closely related
documents do not establish the particular claim. The retrieval result must keep
those two facts separate. Integrate the existing subject/claim assessment into
the engine's actual context assembly and conservative result status, rather than
creating another offline report generator.

This is a bounded, opt-in candidate integration for Phase 05 Task 4 and master
10.1 step 6 / 10.3. It does not select a calibrated default or finish Tasks 4/6.
The initial policy may downgrade or withhold an outcome; it never returns `ok`
or `coverage='sufficient'`. Complete reviewed fields remain uncalibrated and
answer sufficiency remains unassessed.

The existing unconfigured engine/debug/CLI behavior stays unchanged. Automatic
claim recognition and routing belong to Phase 07; curriculum eligibility remains
with reviewed structured facts and later Prolog capabilities. No new SQL,
database loader, public endpoint, CLI flag, institutional activation, dependency,
model call or executable rule is part of this increment.

## Evidence and design choices

Read the [exit reconciliation](2026-10-16-phase05-exit-reconciliation.md), active
phase artifacts and master sections 3/10/11/13. Re-read thesis physical 17–18,
reuse the previous 39–44 consultation, and inspect the actual runtime PNG. The
advisory/undergraduate/private-file separation and unknown-versus-unmet correction
remain unchanged. Scope/source-gap/dataset policies and all settled owner source
decisions govern the integration.

Existing modules inspected:

- [Subject catalogue](../backend/bintanong_retrieval/candidate_subject.py) binds
  complete candidate payloads and explicit researcher assignments. It is
  deliberately inactive and does not infer query subjects.
- [Claim assessment](../backend/bintanong_retrieval/candidate_claims.py) binds
  source-side reviews and limits. Its v2 reports distinguish field availability,
  missing context and unassessed claims; they never certify answer sufficiency.
- [Context assembly](../backend/bintanong_retrieval/context.py) validates and
  renders actual rows, source citations, required groups and exact token budgets.
  It can already render source limits; whole groups must remain intact.
- [Engine](../backend/bintanong_retrieval/engine.py) currently uses the normal
  runtime-role retrieval RPC, then assembly and an uncalibrated policy-name gate.
  Its result does not yet consume the subject/claim modules.

Options considered: change only a similarity threshold; add another caller-owned
composition script; or integrate a conservative policy at the engine. The first
cannot establish missing claims, and the second repeats completed diagnostics.
Choose engine integration. The interface below is an engineering choice for
review, not an owner-approved design or an institutional source decision.

## Interface

Add one module, `backend/bintanong_retrieval/evidence_policy.py`, exposing
`SourceAwareEvidencePolicy`. Its constructor receives a trusted, explicit
candidate snapshot: pinned `release_id`, `embedding_set_id`, complete chunks,
subject catalogue and source-review register. It validates/copies those inputs
and owns their canonical bindings and digest. It performs no I/O.

Add an optional keyword-only `evidence_policy=None` to `RetrievalEngine`'s
constructor. Extend `retrieve(request, *, subject_id=None, requested_claims=None)`.
Claims are an optional tuple of distinct nonblank exact strings; a present tuple
is converted to the existing helper's list representation without changing text.
Use the subject helper's canonical subject syntax. No fields are added to
`RetrievalRequest` or `RetrievalSettings` in this increment.

The engine calls the policy's internal validation/selection/assessment operations;
callers do not pass emitted IDs, assembled text, arbitrary callbacks or a finished
claim report. The engine obtains emission from its own `build_context` result.
The module reuses the existing catalogue and claim functions; it does not copy
their field/limit logic or alter their historical output schemas.

Without an injected policy, supplied subject/claim arguments are rejected as
`invalid_query`, rather than silently ignored. A call with no new arguments has
the exact existing v1 behavior. The policy object is trusted server-side research
configuration, never a student upload, query parameter or a path opened by the
engine. Returning a caller-authored positive assessment is not supported.

## Snapshot and transport binding

Candidate chunks contain source-review packaging absent from database rows;
runtime spans can contain transport identifiers absent from original candidates.
Do not compare their entire dictionaries or weaken the existing catalogue digest.
Prepare a private, deterministic comparison projection for both representations.

The chunk projection contains `chunk_id`, `document_id`, `version_id`,
`edition_id`, `byte_sha256`, `chunk_type`, `chunker_version`, `content_hash`,
`text`, `source_text`, `scope`, `section_path`, and the complete `type_fields`.
The ordered span projection contains `version_id`, `byte_sha256`, `page`,
`printed_page_label`, `locator`, `bbox` and `text`. Only the last three optional
source-location/text fields and printed label may normalize absence to null;
required identity/content fields must be present. Preserve ordered spans because
field associations refer to span indexes. Do not infer omitted values.

Exclude only additional transport/packaging keys from this comparison; the full
`type_fields` object, including fields, source limits, group metadata and required
neighbors, must match exactly. The original constructor inputs first pass their
existing full-payload catalogue/register validation. Derive a private catalogue
and register over the projected chunks using the same assignments/reviews and
existing preparation functions. Original bundles and their digests are untouched.
The actual assembler receives original RPC rows, not the comparison projection.

Compare request and RPC release IDs plus RPC embedding-set ID with the snapshot.
Compare every offered primary and supplied neighbor with its projected snapshot
record before subject filtering; conflicting duplicate identities, unknown IDs,
changed text/fields/limits/spans or malformed rows fail closed. Identical repeated
rows are allowed. No score enters this content comparison.

The snapshot covers the bounded candidate universe, not a university-wide corpus.
A matching declared release ID is a consistency check, not proof of release
membership, source authorization or currentness. This increment adds no loader
that establishes those properties. Every opt-in result explicitly keeps
`runtime_authorization_verified=False` and `activation_eligible=False` and stays
internal; a future governed release loader and real-role verification are required
before institutional use. No administrative storage fallback is permitted.

## Execution and precedence

1. Validate the optional intent syntax before encoding. Preserve the existing
   configuration, runtime-role, encoder and pinned-RPC checks.
2. In opt-in mode validate snapshot/RPC bindings before assembly. A binding failure
   returns `policy_binding_error`, empty evidence/context, zero tokens and a stable
   gap code; it must not expose copied snapshot fields or limits.
3. Preserve the existing ambiguity/conflict checks over all offered rows and
   neighbors before subject selection can hide them. Such failures retain their
   current statuses. Claim assessment does not run for configuration, storage,
   release, scope or source-conflict failures.
4. Select an explicitly supplied subject using the existing helper. Retain only
   matching primary candidates, preserving rank and similarity; keep each retained
   primary's whole neighbor group. The catalogue already requires same-subject
   dependencies. No second search, top-k backfill, entity inference or new SQL
   filter is added. Missing subject/claims do not authorize a guess.
5. Call `build_context` once using the same budget/token counter. In opt-in mode
   use the already-supported `shared_citations=True` and
   `shared_group_metadata=True`. This is an explicit opt-in display choice for
   complete reviewed groups, not a change to default formatting or token settings.
6. Pass the actual assembly evidence IDs, including a literal empty list, into
   `build_candidate_claim_report` with the private validated snapshot/register.
   Inspect selected-subject limits/reviews across that snapshot, including omitted
   chunks. Do not treat missing emission as no limitation or an empty claim list
   as complete coverage. Required IDs missing after deduplication remain a
   conservative insufficiency; no span-equivalence promotion is added.
7. Apply the following status precedence. Keep the assembly gaps and the nested
   source assessment, so a known missing claim can be explained separately from
   missing context. No positive report can override earlier failures or gaps.

| State after prior validation/conflict gates | Opt-in result status | Coverage |
| --- | --- | --- |
| Missing subject | `needs_subject` | `none` |
| Unknown subject in this bounded snapshot | `insufficient_evidence` with `subject_unavailable` | `none` |
| Missing or empty claims | `needs_claims` | `none` |
| Any requested claim is `not_established` | `insufficient_evidence` with `requested_claim_not_established` | `partial` if evidence exists, else `none` |
| No emitted evidence, any assembly gap, or reviewed required fields absent from context | `insufficient_evidence` with the applicable context gaps | `partial` if evidence exists, else `none` |
| Unknown claim or mixed available/unassessed claims | `unassessed` | `partial` |
| All requested reviewed fields available without gaps | `uncalibrated` | `partial` |

Missing subject/claims return no context and no claim values; they can stop after
the validated RPC without assembling. Unknown subject gets the bounded unknown
finding, never a university-wide absence claim. Unknown claim remains unassessed,
distinct from a reviewed absence. A caller-selected non-uncalibrated `policy_id`
cannot promote an opt-in result to `ok`; this policy's conservative gate controls.
The legacy no-policy branch is unchanged by this increment.

## Result contract

Opt-in calls use `bintanong-retrieval-debug-v2`, including early failures. Preserve
existing result fields, scores, actual evidence/citations, context and exact token
count. Add `evidence_policy` containing the fixed candidate-policy version,
snapshot digest, supplied subject/claims, and nested assessment or null with a
`not_run` reason. Include `candidate_only=True`, `activation_eligible=False`,
`runtime_authorization_verified=False`, and `answer_sufficiency='unassessed'`.
The existing retrieval settings fingerprint remains intact; the separate policy
version/snapshot digest identifies the additional behavior.

Copied source reviews/limits are internal research metadata, not independently
authorized runtime evidence. Their original provenance is retained and they do
not join the emitted context or token budget implicitly. Field availability must
come from actual matching emitted IDs; the v2 response never claims a final
answer is permitted. No public result contract or website copy changes.

## Acceptance cases for implementation

Write focused synthetic RED cases against the engine's public call before adding
implementation. Keep source-derived artifacts ignored and reuse existing test
helpers where their fixtures fit. Observe the expected failure, then implement
the smallest correction and run relevant regressions.

| Case | Required observation |
| --- | --- |
| Legacy call, no injected policy | Exact old v1 result/format/status; existing tests pass |
| Intent without a policy, invalid claims/subject | Explicit `invalid_query`; no encoding for malformed intent |
| All reviewed fields emitted with required group | Nested `reviewed_fields_available`, top `uncalibrated`, never sufficient/ok |
| Related context and reviewed absence | Top insufficient despite high similarity and a complete assembly |
| Known unresolved limit on an unreturned subject member | Claim stays not established; omission does not erase the limit |
| Unknown/mixed claims | Unassessed unless a known missing claim or prior failure takes precedence |
| Empty result, group over budget, invalid citation or required neighbor missing | Explicit insufficiency with actual gaps; no fabricated field availability |
| Missing/unknown subject or claims | States above, no guessed subject/claim, no exposed context/values |
| Wrong release/set, changed field/limit/span, unknown or conflicting duplicate ID | Binding error and cleared context; no snapshot-value leakage |
| Matching DB transport extras and original source packaging differences | Projection matches; changed authoritative values still reject |
| Wrong edition/ambiguous curricula among off-subject rows | Existing conflict/scope status wins before filtering |
| Private upload or constructor input mutated after preparation | Never loaded by the module; defensive copying prevents later mutation |
| Arbitrary settings policy name | Cannot bypass the opt-in conservative gate |
| Complete reviewed groups and source limits | Existing renderer and exact serialized token count preserved |

Do not add new benchmark wordings. Following implementation, use compatible saved
inputs/vectors for a bounded integration replay, with declared trusted inputs and
separate context/claim statuses. Do not rerun encoders or the full parameter grid.
Real runtime authorization, selected policy calibration, source/release governance
and final Phase 05 exit checks remain separate unfinished work.

## Review and next action

The single read-only builder check completed with “nothing important left”.
The reviewer inspected the written design and linked modules as needed; no
implementation, source approval or institutional certification is inferred.
After owner design approval, write the implementation plan and execute focused
TDD. Keep Phase 05 active/blocked, all source holds unchanged and owner artifact
changes unstaged. This document does not authorize Phase 06 or activation.

The approval requirement comes from
[the brainstorming skill](C:/Users/joel/.agents/skills/brainstorming/SKILL.md):
“Nothing gets built until your human partner approves the full description”.
The current instruction to continue authorized preparing this design; it did
not yet approve the concrete interface choices first presented here.

## Verification of this design increment

The existing readiness Python 3.13 environment ran:

```powershell
$policyDesignRoot = 'C:/Coding-projects/bintanong_workspace/audit-evidence/p05-source-aware-policy-design-20261016'
& C:/Coding-projects/bintanong_workspace/audit-evidence/p05-real-retrieval-readiness-20261012/venv/Scripts/python.exe -B -m pytest tests/test_docs_hygiene.py .agents/skills/bintanong-phase-handoff/tests/test_phase_state.py -q -p no:cacheprovider --basetemp "$policyDesignRoot/docs-tests"
python .agents/skills/bintanong-phase-handoff/scripts/phase_state.py validate --repo .
python .agents/skills/bintanong-phase-handoff/scripts/phase_state.py can-advance --repo .
python C:/Coding-projects/bintanong_workspace/audit-evidence/p05-document-evidence-calibration-20261016/seal_evidence.py verify
git diff --check
```

Documentation/ledger preflight: 499 passed / 11 subtests in 12.68s, exit 0.
Phase validate exits 0; can-advance exits 1 as expected for blocked Phase 05.
Read-only verification matches the existing 41-file seal; all document links and
five continuity pointers resolve. Product-path diff against `232a418` is empty.
Owner artifact deletion/untracked directory are preserved. Final documentation
verification uses the same suite and a separate `docs-tests-final` basetemp/log
under the raw root above. No product/full/native/model/database tests were rerun
for this design-only change; behavior tests await design approval and TDD.
