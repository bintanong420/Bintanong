# Persisting a supported acquisition observation — 16 October 2026

Status: proposed, awaiting owner design approval. Baseline `3fde038`; product
`b0d6c6d` unchanged. This document does not apply a source transition.

## Purpose and evidence

The existing source-event reconciliation already supplies five matching original
byte checks, with source version IDs, hashes, logical acquisition locators,
actual recording times and system attribution. Its independent contract check
establishes that those observations support transition A1, acquisition pending
to observed. The initial-only SourceRegistrationLoader cannot persist that
supported transition. It deliberately rejects noninitial states.

Student capability advanced: source-linked institutional retrieval whose source
lifecycle can record actual evidence without confusing possession with authority.
Path: existing byte-check record → existing SourceDocumentVersion/Evidence
validation → narrowly constrained administrative persistence → unchanged inactive
draft. This advances the source-governance prerequisite for master 10 / Tasks 4/6.
The specific unresolved question is how to persist this supported A1 observation
without exposing a general status updater or allowing verification/approval.

This is justified by concrete existing A1 evidence, rather than a hypothetical
future office response. It does not supply that response or complete Phase 05.
See the [reconciliation](2026-10-16-source-event-evidence-reconciliation.md) and
[remaining exit packet](2026-10-16-phase05-remaining-exit-packet.md).

## Bounded interface

Add `SourceAcquisitionLoader` in backend/bintanong_storage/source_acquisition.py,
with `observe(current, check)`. It accepts a complete current source contract
and a trusted byte-check envelope. It performs no filesystem/network acquisition
of originals and is not exposed through the student runtime, API or CLI.

The envelope has exactly four fields: `version_id`, `source_sha256`,
`acquisition_locators` and `evidence`. Its Evidence object uses the existing
schema: evidence_id, kind, recorded_by, recorded_at and authorization_ref.
The first three envelope fields must exactly match the current contract, including
locator order. Require kind byte_hash_check and the existing A1-allowed recorder
roles; authorization_ref is null. Reuse Evidence, SourceDocumentVersion and
evidence_authorizes rather than inventing a second governance vocabulary.

For the actual saved checks, preparation projects the existing source ID/hash/
locators and preserves recorded_at/recorded_by. It reuses the already validated
Evidence identity `fresh-hash-` followed by the source version ID. Preserve its
association to the immutable ignored reconciliation packet; do not claim that
an Evidence ID authenticates its recorder or proves the original was checked.
Trusted administrative preparation remains responsible for the truthful check.
The database cannot verify local filesystem bytes or an external evidence file.

Require the supplied current contract to have all four initial lifecycle states,
null state references and null approval_id. Preserve all scope, source identity,
existing evidence and other metadata. Append exactly one new, distinct Evidence
record and set only acquisition_state to observed with its evidence_ref. Validate
the complete resulting SourceDocumentVersion. Reject malformed, duplicate,
wrong-source/hash/locator, wrong-kind/role or inconsistent observations locally
before calling storage. The loader does not accept a caller-authored final record.

Call one new administrative RPC, `observe_source_acquisition`, with
`p_expected_register` (the complete prior contract) and `p_check` (the envelope).
The server independently derives the same resulting record; it does not accept
an arbitrary desired-state parameter. Return the exact persisted source register.
The Python loader parses that return and requires it to equal its expected
observed contract. The constructor follows the existing optional storage-client
injection pattern, without changing SourceRegistrationLoader's interface.

## Atomic persistence and retry behavior

Use one additive migration, generated through the existing CLI workflow during
implementation. No new table, status vocabulary, source-register schema version
or relaxed policy is required. The new function is SECURITY INVOKER, executable
only by service_role; explicitly revoke PUBLIC/anon/authenticated execution.

Within the existing publication lock, locate the version and compare its full
stored source_register with the supplied expected record. Reject missing parents,
legacy null registers, mismatched duplicated relational metadata and any version
ever included in a published release. Preserve existing immutability triggers.
For the duplicated relational fields, use the same source-register-to-row
projection as pending registration, excluding only created_at; do not compare
only version_id or a subset of the lifecycle columns.

Independently check the closed envelope/Evidence shapes, initial lifecycle guards,
source identity/hash/locators, allowed A1 kind/recorder, real timestamp, null
authorization reference and distinct evidence ID. Derive the proposed register
by appending the one Evidence and changing the one acquisition state. Reject
null/missing fields explicitly. Python validation remains the complete contract
validator; SQL enforces the bounded mutation and stored-identity guards against
direct administrative RPC calls. No adversarial-admin authenticity claim follows.

If the stored record equals the derived observed record, return it without an
UPDATE: an exact retry of the original call is idempotent. Otherwise require an
exact expected-record match, then update only document_versions.acquisition_state
and source_register together. A stale expected record, different observation or
divergent relational projection fails atomically. Publication and observation
must serialize under the existing lock; no pointer or release membership changes.
For a replay, duplicated columns must match the observed projection; for a first
application they must match the pending projection. Check this before returning
or updating, so idempotency cannot conceal inconsistent flattened metadata.

An uncertain transport outcome must not trigger an automatic retry. An explicit
replay uses the same original expected record and envelope and can recognize a
committed observation. Pending registration retains its current behavior: trying
to register the old pending record after observation is a conflict, never a
downgrade. Resume the observation operation directly rather than replaying initial
registration. Other transitions and general loader-resume changes are separate.

## Verification and delivery boundary

After approval, write an implementation plan, then focused TDD. Synthetic tests
must cover local rejection before RPC, actual persisted flattened/full-record
consistency, exact replay, conflicting/stale updates, retained pre-existing
evidence, mismatched source/hash/locators, invalid timestamps, null/malformed
direct RPC inputs, wrong kinds/roles, attempted wider state changes and published
immutability. Test runtime EXECUTE denial under both actual roles. Verify the
ordinary pending importer still rejects conflicting or noninitial registration.

Use only uniquely named disposable databases for migration/role verification.
The real-package rehearsal imports the existing five pending versions first,
then applies only their five already supported A1 observations. Reuse the saved
chunks/vectors for an inactive draft if needed to verify downstream compatibility;
do not rerun source conversion, encodings, ranking experiments or wording review.
Both runtime roles must still see no real-source corpus/release. All verification,
approval and content-review states and chunk bindings remain pending/unchanged.
Original sealed inputs stay unchanged; new observed artifacts/logs belong in a
new ignored audit-evidence root. Drop only the rehearsal's own database.

Run relevant storage/governance regressions and one independent review. Final
verification must substantiate every changed behavior and check; use the existing
Python 3.13 environment without installs or dependency changes. Production/shared
migration application, source verification/approval, release activation, runtime
authorization claims and Phase 06 remain outside this increment. No A2, V1/V2,
C1/C2/C3 or P1/P2 transitions are added or inferred.

## Choices and review status

The single-version compare-and-set interface, closed envelope, exact retry,
server-derived update and A1-only boundary are engineering choices for review.
They keep the initial importer separate and avoid a configurable transition
engine. Existing governance contracts, settled source decisions and the five
actual byte checks constrain the design. No new human source-reading decision
or school-response question is needed for acquisition observation.

Context consulted: thesis physical 17–18, actual routing PNG, master section 10,
active phase artifacts, source reconciliation and current governance/registration
code. No undergraduate advisory/structured-routing discrepancy. Builder check
and documentation verification are recorded after they complete. Approval of
this design would authorize its bounded implementation and disposable rehearsal,
not shared deployment or institutional approval.

The single builder check reports “nothing important left.” In-memory checks
against the five existing pending source records and saved byte checks validate
all five A1 evidence/source bindings and proposed SourceDocumentVersion values;
verification/content review remain pending and approval not_requested/null.
No derived source file, source state, database, product code or test was changed.
The reconciliation's eight-file seal verifies unchanged. Documentation/phase-ledger
checks pass 523 tests / 11 subtests in 11.63s, exit 0. Check logs are ignored under
workspace/audit-evidence/p05-acquisition-design-checks-20261016.

The required design-approval boundary comes from
[C:/Users/joel/.agents/skills/brainstorming/SKILL.md](C:/Users/joel/.agents/skills/brainstorming/SKILL.md):
“Nothing gets built until your human partner approves the full description”.
It applies to this new persistence interface, whose full description was not
part of the previously approved source-aware engine integration. The standing
research permission supports preparing this design; no source-content or school
authority decision is being requested. After actual approval, use writing-plans
before implementation. Formal Phase 05 gates remain unchanged.

Final phase checks: validate exits 0; can-advance exits 1 (expected blocked).
Whitespace checks pass. The baseline precedes this documentary commit; product,
tests, source records and SQL remain unchanged. Owner artifacts stay unstaged.
