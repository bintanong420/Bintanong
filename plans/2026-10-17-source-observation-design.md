# Recording existing reviewed source observations — 17 October 2026

Status: approved after2a472ba with “alright i approve, continue”.
Baselineee1d851, productdba0777 unchanged. This is V1 pending→observed,
not V2 issuing-office verification or institutional approval.

## Purpose and bounded evidence

Student capability: undergraduate source-linked policy/procedure retrieval with
the reviewed printed evidence traceable through its source lifecycle. Evidence
path: existing owner confirmations → immutable C1 spans/field associations →
accepted undergraduate selection → V1 observation → unchanged inactive draft.
Master6/10 source governance requires these distinct evidence stages before an
authorized release. The unresolved engineering question is how to record the
already established observations without presenting them as school verification.

Five local V1 derivatives can be compiled from the existing A2/C1 records and
accepted19chunk selection:54spans/52field associations/nine source-bound events.
No new reading, transcription, human confirmation or original-byte check is
needed. Preserve the full original source PDFs/images and historical evidence.
Content is selected by undergraduate applicability; a general student procedure
need not literally say undergraduate. Explicit excluded audiences stay excluded.

The original reviewer label remains the C1 receipt's actual owner label. The
compiler is separately identified as Codex compiling those existing confirmations.
New Evidence.recorded_at records this compilation, not a new owner answer,
exact original review time, current-year validation or issuing-office event.
Original event times/attribution remain unchanged in C1. Evidence recorder role
reviewer carries the already recorded human review, as in C1; it is a declared
administrative role, not authenticated identity. Do not create a school recorder.

## Interface and receipt

Add SourceVerificationLoader.observe(current, observation), with existing optional
client injection. Accept SourceDocumentVersion or its full JSON mapping. Require
acquisition verified (existing A2), source verification pending, content review
partially_reviewed (existing C1), approval not_requested/null. Preserve all scope
fields and unknowns. Do not record issuer, effectivity, supersession or program
decisions through this operation.

Closed selected-source-observation-v1 receipt keys:
receipt_format, version_id, source_sha256, acquisition_locators,
partial_review_evidence_id, review_scope_id, observation_scope, evidence,
reviewer_label, compiler_label, timestamp_meaning.

Require observation_scope selected_reviewed_spans and exact source identity/hash/
locator order. partial_review_evidence_id equals the current C1 state reference.
review_scope_id identifies the immutable accepted undergraduate selected-review
receipt already stored through SelectedReleaseReviewLoader. This makes the
concrete selected evidence reachable without duplicating or editing C1 snapshots.

Evidence uses existing schema, distinct nonblank ID, kind printed_text_span,
recorded_by reviewer and null authorization_ref. Use existing contracts/vocabulary
and real timestamp parsing. It cannot authorize V2 or P2. Append one Evidence
and set only verification_state observed with its reference; parse complete
current/resulting contracts. Call observe_source_verification(p_expected_register,
p_observation) once as admin; parse return and require exact derived equality.
Propagate failures without retry or credential fallback. No student API/CLI or
automatic acquisition is added.

## Persistence and exact coverage

Add immutable administrative source_verification_observations with source/evidence
identity, full closed receipt and relational references to existing source,
the composite C1 version/evidence identity and selected review scope. Those
immutable records retain complete printed spans, limits and original event
attribution. No independently edited span/field copies are maintained.

Use one additive CLI-generated migration. New tables have RLS/restrictive runtime
denial, mutation guards and admin-only access, including accidental table grants.
The RPC is SECURITY INVOKER, empty search_path, explicit PUBLIC/anon/authenticated
EXECUTE denial and service_role grant. Preserve earlier migrations and policies.

Under existing publication lock then source row lock, independently validate the
closed receipt/Evidence, exact source/A2/C1 boundary, distinct ID, reviewer-label
match to stored C1 and selected scope membership. Reuse the existing private
validate_selected_review on the stored selected receipt to recheck immutable C1
coverage against actual chunks/spans, fields/limits, neighbors and full groups.
Require this source's selected snapshots to equal its referenced C1 snapshots;
no unselected chunk can supply a printed observation. This is a bounded operation
for the accepted selection, not an arbitrary future-source updater.

Check observation compilation is no earlier than cited C1 and selected-decision
recording times. Compare instants using acquisition_check_time, which implements
the existing Python offset/fraction acceptance; retain original timestamp text.
This is a new compilation record, so it need not pretend to be an older event.

Compare full stored source_register and complete relational projection, excluding
only created_at, against expected or exact derived state. Reject missing/legacy,
stale/different, drifted and ever-published sources. Insert receipt and update
verification_state/source_register atomically; rollback both on failure. Exact
explicit replay requires unchanged receipt/current snapshots/projection and
returns without UPDATE. Concurrency serializes with publication; equal calls
converge, different observations conflict. Caller supplies no desired final state.

## Chunk binding and compatibility

V1 does not change chunk text, spans, IDs, content hashes, type_fields, vectors,
source limits, C1/selected-review receipts, membership or active pointer. It does
not silently claim that existing chunk register bindings are current afterward.
Use existing bind_chunk with the returned source, then the ordinary administrative
chunk loader, when preparing the inactive draft: source_verification observed and
verification_evidence_ref must match V1; content review keeps its C1 reference.
This follows the existing C1 separate rebind/load workflow. Until rebinding,
check_chunk_binding must reject the old metadata; release guards remain closed.

Uncertain V1 outcomes resume with the original expected record and observation.
Obsolete A1/C1/A2 replays may conflict after V1 and cannot downgrade the source.
Selected review coverage remains bound to unchanged source content and C1 identity.
Observation alone cannot satisfy release verification/approval gates or expose
candidate data to either runtime role.

## Verification and delivery

After full-description approval, write a repository implementation plan and
focused TDD. Synthetic fixtures stay undergraduate/generic; no original content
or source-derived JSON is tracked. Cover Python early rejection, unchanged
history/limits/attribution, timestamp/evidence/source binding, exact return and
one propagated storage failure; SQL direct malformed/null inputs, unknown scopes,
wrong C1/labels, snapshot drift and incomplete groups, relational drift first/
replay, rollback/concurrency/publication, immutable receipt access and actual-role
denials. Verify old chunk binding fails and existing rebinding restores agreement.

One disposable real-package rehearsal may reuse five pending→A1→C1→A2 records,
19saved chunks/vectors, the stored accepted selected review and five proposed V1
receipts. Compare exact local derivatives/replays, rebind chunks, preserve C1/
selected receipts and source limitations, deny missing-authority activation and
verify both roles remain hidden. Drop own DB and verify inputs. Do not repeat
conversions, original hashing, embeddings, wording review or retrieval experiments.

Use existing Python3.13.7/PostgreSQL17.6/CLI2.117.0, no installations/dependency
changes. Relevant regressions, one independent final review, final whole suite,
cleanup/evidence seals and repository handoff apply. Keep the branch/worktree,
owner artifacts/.gitkeep deletion and untracked backend/artifacts unchanged.

Builder choices: file organization and constraint/helper factoring may follow
existing storage conventions; do not expand to general verification/approval or
rewrite earlier lifecycle methods. Actual V2 office evidence, issuer/scope
verification, P1 submission/P2 authorization, shared deployment, activation,
Phase06 and executable rules retain their existing boundaries. Missing school
response stays pending without another status question.

Context: actual thesis17–18/routing PNG, master6/10 and active phase documents,
scope/source-gap/dataset policies and completed A1/C1/A2/selected-review evidence.
No scope/routing discrepancy; curriculum eligibility remains structured/Symbolic.

One fresh builder check: “nothing important left”. No additional source-content,
reviewer-identity or ordering question was raised; no prior owner decision reopened.
