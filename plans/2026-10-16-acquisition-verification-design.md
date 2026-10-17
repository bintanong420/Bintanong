# Persisting a subsequent acquisition byte check — 16 October 2026

Status: approved by the owner after184b33f with “ye i approve, then proceed”. Baseline
`a4661f1`, product `6378994` unchanged. This is the A2 acquisition transition,
not issuing-office verification or institutional approval.

## Purpose and concrete evidence

Student capability advanced: source-linked undergraduate policy/procedure
retrieval with an accurate record of the original bytes used. Evidence path:
original dataset file → new SHA-256 measurement → existing A1 history and C1
partial-review register → existing A2 contract → administrative persistence.
Master sections 6 and 10 require source governance before an authorized release;
this supplies only its byte-acquisition prerequisite. It does not close formal
Phase05 Tasks4/6 or supply missing issuing-office evidence.

The new ignored packet is
`workspace/audit-evidence/p05-acquisition-recheck-20261016/`. A fresh read of each
of the five originals matches its recorded byte hash. Each system check is
recorded after its cited A1 observation. Five local derivative contracts pass
SourceDocumentVersion validation, retaining all C1 partial-review evidence and
the accepted selected19chunk review. They append one Evidence and change only
acquisition_state to verified. No database call or migration was made.

The unresolved engineering question is how to persist exactly that supported
transition without permitting broader source promotion. Existing observe()
supports A1 only; a generic lifecycle updater is unnecessary. Alternatives are
leaving the valid derivative outside storage, adding one A2 operation, or adding
a general updater. Choose the narrow A2 operation because the existing schema
already distinguishes acquisition from source verification and authority.

## Interface and validation

Extend existing SourceAcquisitionLoader with verify(current, check), retaining
observe() unchanged. Accept a SourceDocumentVersion or its complete JSON mapping.
The check is the same exact four-field envelope as A1: version_id,
source_sha256, acquisition_locators, evidence. Identity/hash/locator order must
equal the current record. Accept no caller-authored final register.

Require current acquisition_state observed; verification_state pending;
approval_state not_requested and approval_id null; content_review_state
partially_reviewed. This explicitly supports the five existing C1 records,
without requiring their re-review or downgrading them. Parse the complete
current and resulting contracts with the existing SourceDocumentVersion model.
Preserve scope fields, source identity, limits and all other data verbatim.

Use Evidence and the existing A2 vocabulary: kind byte_hash_check, recorded_by
reviewer or system, null authorization_ref. Its evidence_id must be nonblank
and distinct from every prior evidence ID. Its timestamp must be real and no
earlier than the evidence cited by current acquisition_state, compared as
instants using the existing parser. Require that cited observation itself has
valid A1 evidence. Do not merely find any older byte check elsewhere in history.
The five prepared checks are strictly later; the interface retains the existing
contract's allowance for equal timestamps with distinct ordered evidence.

Append exactly that new Evidence and set acquisition_state to verified with
its evidence_ref. Call verify_source_acquisition(p_expected_register, p_check)
once under the admin role. Parse the returned full register and require exact
equality with the locally derived result. Storage failures propagate without
automatic retry, role fallback or a partial success result.

Trusted administrative preparation binds actual local measurements to these
envelopes. Neither evidence_id nor a declared recorder label authenticates a
person. SQL cannot read the original file or prove an external check occurred.
There is no new student API/CLI, filesystem acquisition, download or model work.

## Atomic storage and lifecycle compatibility

Use an additive migration and a service_role-only SECURITY INVOKER function
with empty search_path and explicit PUBLIC/anon/authenticated EXECUTE revocation.
No new table, vocabulary, contract version or RLS relaxation is needed.

Under the existing publication lock and version row lock, require a registered
version with nonnull source_register and no membership in any published release.
Independently check the closed envelope/Evidence shape, exact source binding,
state boundary, distinct evidence ID, cited A1 evidence and chronological order.
Reject missing/null fields explicitly. Validate calendars, offsets and fractions
consistently with the existing Python contract; do not rely on a PostgreSQL
timestamptz cast that rejects allowed wide UTC offsets. Preserve timestamp text.

Derive the proposed record in SQL, rather than accepting a desired state. Require
the full stored register to equal the expected record, or exactly the derived
record for replay. Check the complete duplicated relational projection, excluding
only created_at, against whichever record is stored before returning/updating.
Only acquisition_state and source_register may change. Reject stale/conflicting
records, legacy null registers, relational drift and published membership
atomically. An exact explicit replay returns without UPDATE. Concurrent equal
calls converge; different checks conflict. All publication paths retain the
existing lock/immutability protections.

Old A1/C1 calls remain compare-and-set operations: replaying them after A2 with
obsolete expected metadata may conflict; they must never downgrade acquisition.
Resume an uncertain A2 call using its original expected record and envelope.
C1 partial_review_evidence_id and selected-review coverage remain unchanged.
Keep chunks' source_verification pending: A2 is acquisition, not V2. No release
membership, embedding, chunk content/span, review receipt or pointer changes.

Ruling from the single builder check: require C1 partial review before this A2
operation. Existing C1 requires acquisition observed; accepting a pending-content
source into A2 would prevent its later C1 call. All five actual sources already
have C1, so this bounded ordering serves the concrete packet without changing
C1 or adding a new review path. Cost: sources without partial review cannot use
this operation yet. This is an operation boundary, not a claim that the general
governance vocabulary forbids another properly implemented ordering.

## Verification and delivery

After description approval, write a repository implementation plan and apply
focused TDD. Cover Python rejection before RPC, exact return validation,
partial-review preservation and pending-content rejection, history/input immutability and
no retry. Use synthetic tracked fixtures only.

Disposable database tests must exercise direct malformed RPC inputs, forbidden
roles/kinds/states, cited-evidence identity and ordering, timezone/fraction parity,
duplicate IDs, exact replay, stale/concurrent calls, full relational projection,
legacy/missing versions, published immutability and both actual runtime roles'
EXECUTE denial. Existing A1/importer/C1/scoped-review regressions must remain
compatible. Use existing Python3.13/PostgreSQL/CLI, without installation or a
shared database mutation.

One real-package rehearsal may register five pending versions, reuse their A1
and C1 evidence, then apply/replay the five new A2 envelopes in a disposable
database. Compare exact prepared derivatives and retain pending source
verification, not_requested/null approval, partial content review, existing
selected-review bindings and runtime invisibility. Reuse saved chunks/vectors
only if needed; no new conversions, embeddings or ranking experiment. Drop the
database and verify input hashes/cleanup. Follow existing applicable regression,
single independent review, evidence-seal and phase-ledger delivery requirements.

Builder choices: implementation factoring and test organization are left to the
builder, subject to preserving existing public interfaces and error boundaries.
Do not refactor earlier migrations or introduce a generic status-update helper.
An A2 operation alone cannot enable institutional publication. Source V2/P1/P2,
school validation, shared deployment, activation, executable Prolog and Phase06
remain at their existing boundaries. Undergraduate audience, source gaps and
settled owner decisions remain unchanged.

## Context and documentation evidence

Consulted thesis physical17–18/39–44, runtime routing PNG, master3/6/10/11/13,
scope/source-gap policy, dataset locations, current ledger, A1/C1/scoped-review
deliveries and the governance vocabulary. No scope/routing discrepancy. A2
does not route curriculum eligibility into semantic search.

Current Supabase documentation fetched through Context7 `/supabase/supabase`
supports invoker functions with restricted EXECUTE grants; see the official
[database functions guide](https://supabase.com/docs/guides/database/functions).
No Supabase feature has been implemented in this design-only increment.

One fresh builder check identified the C1/A2 ordering issue above. It is resolved
by narrowing the operation to the already-established five-source C1 boundary;
there are no remaining owner-content questions or deferred builder questions.
