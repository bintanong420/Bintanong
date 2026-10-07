# Phase 1 Task 2: source governance vocabulary and state transitions

Status: draft vocabulary. It approves no source, no edition and no curriculum. Every example is synthetic with fictional locators. Python validators for these records are Phase 1 Task 3 (`backend/bintanong_contracts/`); the checks in `tests/test_source_governance_manifests.py` are test-local and exist so the data below can be verified now.

Machine-readable files (all under `knowledge/manifests/`):

| File | Role |
|---|---|
| `governance-vocabulary.json` | Closed vocabularies, roles, evidence kinds, namespaces, the five decision outcomes and the transition table. Single source for state names. |
| `schemas/source-register-v1.schema.json` | One acquired byte identity (SourceDocumentVersion register record). |
| `schemas/source-conflict-v1.schema.json` | Conflict record. |
| `schemas/session-fact-v1.schema.json` | Private session fact. |
| `schemas/decision-v1.schema.json` | Closed five-outcome vocabulary (not the SymbolicResult runtime contract). |
| `examples/synthetic-*.json` | Register (3 records), conflict, session fact, five decisions. |

Schemas use `additionalProperties: false`, so an unknown key such as `approved`, `promotion_status` or `verified` is malformed, not ignored. A test asserts every schema enum equals the vocabulary.

## (a) Separate state fields

Acquisition, verification, approval and content review are four fields, each `{state, evidence_ref}`. None implies another.

| Field | States | Meaning |
|---|---|---|
| `acquisition_state` | pending, observed, verified, mismatch | Bytes held and hashed; verified means an independent hash check; mismatch means the bytes differ from the register |
| `verification_state` | pending, observed, verified, rejected | Identity and scope read from the document (observed) versus confirmed by the issuing office (verified) |
| `approval_state` | not_requested, requested, approved, rejected, revoked | Issuing-office authorization to use the source |
| `content_review_state` | pending, partially_reviewed, reviewed | Human review of extracted content (same vocabulary as the extractor ledger); never approval |

`approval_id` is `null` unless `approval_state` is `approved` or `revoked`, and then it must equal the `authorization_ref` carried by the cited issuing-office evidence. All four example approval states are `not_requested`, all approval ids `null`: no authorized evidence exists.

Approval additionally requires (checked, not just documented): acquisition verified, verification verified, issuer verified, every scope and effectivity field verified or explicitly `not_stated`, and a category other than a proposal candidate.

## (b) Allowed transitions and their evidence

The table is `transitions` in the vocabulary file. A state other than the initial state needs an evidence reference that resolves inside the record, whose `kind` and `recorded_by` match a row that enters that state. Nothing skips a step (there is no pending to verified row). A test proves every state is reachable only through an evidenced row.

| Id | Field | From to | Evidence kind | Recorded by |
|---|---|---|---|---|
| F1 / F2 / F3 | scope field and supersession | pending to observed / observed to verified / pending to not_stated | printed_text_span / issuing_office_confirmation / reviewer_absence_check | researcher or reviewer / issuing_office / reviewer |
| A1 / A2 | acquisition | pending to observed / observed to verified | byte_hash_check | researcher, reviewer or system / reviewer or system |
| A3 / A4 | acquisition | observed or verified to mismatch | byte_hash_check | reviewer or system |
| V1 / V2 | verification | pending to observed / observed to verified | printed_text_span / issuing_office_confirmation | researcher or reviewer / issuing_office |
| V3 / V4 | verification | observed or verified to rejected | issuing_office_rejection | issuing_office |
| P1 / P2 / P3 / P4 | approval | not_requested to requested / requested to approved / requested to rejected / approved to revoked | approval_request / issuing_office_authorization / issuing_office_rejection / issuing_office_revocation | researcher or reviewer / issuing_office |
| C1 / C2 / C3 | content review | pending to partially_reviewed to reviewed (or direct) | content_review_record | reviewer |
| R1 / R2 / R3 | conflict | unresolved to referred_to_source_owner / to resolved | conflict_referral / issuing_office_resolution | researcher or reviewer / issuing_office |
| S1 / S2 | session confirmation | unconfirmed to user_confirmed / user_rejected | user_confirmation | user |

Source approval (P2) and content review (C1 to C3) are different transitions with different evidence kinds and roles; a content review record cannot authorize approval, and approval does not mark content reviewed.

Non-authorizing evidence kinds: `extraction_audit`, `extractor_status_label` (EXTRACTED, VERIFIED, promotion labels), `filename_observation`, `local_possession_note`. They may be listed as context. No row accepts them, so citing one for any state is rejected.

Roles are declared labels on an evidence record, not authenticated identities. Authenticating who may write as `issuing_office` is out of scope here (see owner decisions).

## (c) Scope, effectivity and supersession

Fields `issuer`, `campus`, `college`, `program`, `cohort`, `printed_revision`, `effective_from`, `effective_to` and `supersession` each carry a state in `pending | observed | verified | not_stated`, an evidence reference and a basis.

- `pending` and `not_stated` carry no value and no basis: nothing is inferred.
- `observed` and `verified` need a value, evidence and a basis from `printed_text`, `issuing_office_statement`, `reviewer_reading`. The basis enum excludes `filename_date`, `college_vs_university_wording` and `local_possession`, so an effective year, a hierarchy or an authority cannot be asserted from them.
- Supersession: `relation` is `none`, `supersedes` or `superseded_by`; a relation needs a target present in the same register, never itself, and a non-pending state with evidence. A supersession is never derived from a newer-looking filename.
- Duplicates: the same bytes are one version with several `acquisition_locators`. Same bytes recorded as two versions is rejected. Same filename with different bytes are distinct versions and may not share an `edition_id` (an edition maps to one byte identity until a verified same-edition relation is defined). The example register keeps two handbook versions that share a filename and differ in hash. The two Charter PPTXs are handled the same way when they are registered.
- A BOR curriculum proposal uses category `curriculum_proposal_candidate`, which can never be approved as a source.

## (d) Conflict record

Fields: `claims` (at least two distinct `version_id` plus `span_ref` plus text), `affected_scope` (capability plus campus, college, program, cohort), `resolution_state`, `resolution_evidence_ref`, `resolution_basis`.

- Resolved requires issuing-office resolution evidence and a basis from `supersession_evidenced`, `scope_distinction_evidenced`, `source_owner_ruling`; not resolved requires neither. Newest filename and office precedence are not bases.
- Claims must cite versions present in the register.
- An unresolved or referred conflict blocks only `affected_scope.capability`; the test checks that other capabilities stay unblocked and that resolving removes the block.

## (e) Institutional and private-session namespaces

| Namespace | Id prefixes | Lifecycle | Storage |
|---|---|---|---|
| `institutional` | doc-, ver-, edition-, conflict- | register | Institutional manifests and ledger |
| `private_session` | sess-, fact- | `session_only` | Session scope only; never the institutional ledger |

A private id inside an institutional record (or the reverse) is rejected wherever it appears, by pattern on id fields and by a scan of every string. A session fact records `origin` (`user_statement` or `private_upload`) and `confirmation_state` (`unconfirmed`, `user_confirmed`, `user_rejected`). Confirmation means the student confirmed their own statement; no transition recordable by `user` touches an institutional field, and a session fact has no `approval_id`, `verified` or ledger key (unknown keys are rejected).

Retention, deletion and isolation (requirements, since no session or upload route exists yet; see the consumer inventory): original bytes and parser files deleted after extraction; idle lifetime proposed at 30 minutes (master 15.1, a proposal); explicit deletion, expiry and failure cleanup remove all session state; Session B must not reach Session A's file, text, facts, cache or in-progress result; private content never enters the institutional search path or evaluation exports. These are checked when the Phase 11 session routes exist, not now.

## (f) Five decision outcomes (closed vocabulary)

`eligible`, `ineligible`, `unknown`, `unsupported`, `error`, with per-outcome constraints in `decision.outcomes`:

- eligible: supported predicate, verified rule coverage, satisfied conditions and evidence present; no violated or unknown conditions, missing facts or unresolved conflicts; prerequisite rule state null or one of the executable states. It implies no official enrollment approval.
- ineligible: at least one violated condition with evidence; no unresolved conflict.
- unknown: needs a reason (missing fact, unknown condition, unresolved conflict, coverage not verified, or a non-executable prerequisite rule); never carries a violated condition.
- unsupported: predicate not supported, coverage absent, no conditions, evidence or conflicts; never an invented decision.
- error: error code required; no conditions or evidence; never converted into a policy result. All other outcomes require a null error code.

Verified zero prerequisites (`stated_none`, `reviewed_empty`) is distinct from `blank_unreviewed`, `unreadable`, `unresolved_reference`, `standing_condition` and `alternative_or_exception`. The vocabulary reuses the extractor's `PREREQUISITE_STATES` and `EXECUTABLE_PREREQUISITE_STATES`; a test fails if they diverge. The existing eligible example gained a synthetic evidence reference because the plan requires authoritative rule coverage for `eligible`.

## Verification

`tests/test_source_governance_manifests.py` (131 tests): schema and example validation, table consistency, and 100+ negative cases (malformed input, unknown privileged status, forged verified or approved state, transition not in the table, approval id without authorized evidence, same filename with different hash as one edition, private fact id in an institutional namespace, plus conflict, session and decision guards). Guards were mutation-checked in scratch copies (37 mutations, all caught). The test-local schema checker supports a documented keyword subset and raises on any other keyword; its results match the full `jsonschema` library on 96 mutated cases. `jsonschema` is not a repository dependency and is not used by the tests.

## Ambiguities resolved strictly, and owner decisions needed

Resolved strictly (refuse rather than guess): no hierarchy, effective year or authority from filenames, wording or possession; same bytes are one version, different bytes are different editions; `approval_id` null without authorization evidence carrying a matching reference; proposal candidates never approvable; unknown keys rejected.

Owner decisions (not decided here):

1. Document category list. Only `source_document` and `curriculum_proposal_candidate` exist; whether Handbook, Charter, USG, CSG and prospectus get their own categories is open.
2. Who may record as `issuing_office`, and how an authorization is authenticated (the table trusts a declared role).
3. Whether independent acquisition verification needs a different recorder than the observer (currently any reviewer or system record qualifies).
4. Whether `resolved` conflicts may be reopened, and whether `revoked` or `rejected` approvals may be re-requested (no such rows exist).
5. Format of printed effective dates (currently free text recorded as printed).
6. Session idle lifetime (30 minutes is a master-plan proposal).
7. The Direct routing meaning (still open, see the consumer inventory).
