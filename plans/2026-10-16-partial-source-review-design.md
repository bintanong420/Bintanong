# Recording selected source reviews without claiming complete review

Status: owner approved with “ye sure go ahead” after `b5ddea9`. Baseline `5e69cf3`; product `7c40308`.
No product code, schema, source state or database is changed by this document.

## Purpose and existing evidence

The approved A1 work can persist acquisition observations, but the source
register still cannot durably record the already completed selected content
reviews. The existing reconciliation binds 52 field associations in 19 chunks
to nine source-bound events and eight actual owner records across five sources.
These are existing confirmations, not a request to confirm their readings again.

Student capability advanced: traceable source-linked undergraduate guidance,
with exact content-review coverage and known source defects retained. Evidence
path: existing owner confirmations and field/span bindings → scoped partial
review receipt → administrative source register → unchanged inactive draft.
This advances source governance needed by master sections 6/10 and Phase05
Tasks4/6. The unresolved question is how to persist that exact partial coverage
without representing it as review of the entire source or source authorization.

Use only C1, `content_review_state: pending → partially_reviewed`. No second
reading, new benchmark, retrieval experiment, conversion or embedding is needed.
The existing source-event reconciliation supplies the mapping; do not rebuild it.

## One administrative interface

Add `SourcePartialReviewLoader(client=None).record(current, receipt)` returning
the validated `SourceDocumentVersion`. Reuse the current storage client, source
and Evidence contracts, vocabulary and contract error conventions. This method
does not read original PDFs/images or contact a university office.

`current` is the complete exact expected source register. For this bounded
interface require acquisition `observed`, verification `pending`, approval
`not_requested` with null approval ID, and content review `pending`. Existing
scope fields and acquisition evidence are retained verbatim. A source that
has moved to another lifecycle stage needs its separately designed operation;
this interface does not accept a general desired-state parameter.

The closed receipt is a JSON object with these exact members:

- `receipt_format`: literal `selected-source-partial-review-v1`.
- `version_id`, `source_sha256`, `acquisition_locators`: exact source binding,
  preserving locator order.
- `evidence`: existing five-field Evidence object, kind `content_review_record`,
  role `reviewer`, null authorization reference, unique nonblank evidence ID.
- `reviewer_label`: the existing human label, such as `owner (chat confirmation)`.
- `compiler_label`: truthful label for the researcher/agent assembling the receipt.
- `review_scope`: literal `selected_fields`; never `whole_source` or `complete`.
- `source_events`: nonempty distinct source-bound event records. Each carries
  exactly `event_sha256`, `representation`, `source_sha256`,
  `owner_event_sha256`, `actual_owner_label`, `recorded_at` and
  `timestamp_meaning`. Project the existing bound event to this source without
  changing its digest or representation; source_sha256 equals the receipt's
  source digest. These timestamps retain their original recording meaning.
- `chunks`: nonempty distinct selected chunk snapshots as described below.

The receipt Evidence timestamp is the actual time of compiling the scoped
review record; it is not backdated to an old confirmation. The original event
timestamps remain separately attached. The Evidence role describes the owner's
already performed source-review activity. Retain the actual owner labels and
do not invent a personal name, independent reviewer, school role or new owner
answer. The compiler is recorded separately and cannot substitute its own
unchecked source judgments. The receipt makes no authentication claim about
these supplied identities; trusted administrative preparation remains required.

Each chunk snapshot has exactly `chunk_id`, `content_hash`, `type_fields` and
`spans`. Copy the complete existing type_fields, including reading identity,
field associations, source limits, applicability reference and required
neighbors. Field associations retain exact names, values, blank flags, event
digests and span indexes. Spans use the existing storage projection in source
order, excluding database-generated span UUIDs/creation metadata. No raw-source
rewriting or new span geometry is allowed.

The span projection has exactly `chunk_id`, `span_order`, `version_id`,
`byte_sha256`, `page`, `printed_page_label`, `locator`, `text`, `bbox`,
`bbox_origin`, `page_size` and `extraction`. Use the existing loader's
`_chunk_records` projection/default behavior, including zero-based span_order.
It deliberately does not persist raw-only original_page/page_offset fields.
Validate each selected stored chunk's source/version/edition identities and
pending review/verification flags against the current source and receipt; C1
cannot be used to reclassify a chunk that has already advanced independently.

Require all field event digests to resolve to a receipt source event bound to
this source. Include every field of each selected chunk, its entire span list
and all source limits; subsets cannot silently drop a condition or defect.
Every transitive required neighbor must also appear in this source's receipt.
This operation rejects cross-version dependency closure rather than expanding
review scope. The selected package must be checked for that condition before
implementation; a conflicting case is a design question, not permission to
omit a dependency. Nonselected source chunks remain unreviewed. The read-only
design preflight now confirms 22 dependency edges, all within the selected
19 chunks and their respective source versions; no such conflict is present.

Source-bound events retain their existing original-file or encoded-object
representation. The preparation step verifies those existing digests and
source bindings against the sealed reconciliation and its retained inputs.
It does not redefine historical hashes or claim SQL can inspect external files.

## Durable coverage and atomic persistence

Use a new administrative receipt table, `source_partial_reviews`, keyed by
`(version_id, evidence_id)`, with a restrictive source-version foreign key, the complete
receipt JSON and creation time. Store the coverage itself, not only an external
file digest: the source register's small Evidence object cannot express which
fields were reviewed. Add no new filesystem-path fields and store no original
or private file bytes. Complete type_fields snapshots already contain absolute
provenance strings in applicability_basis_ref and some source limits. Preserve
those strings verbatim in the administrative receipt; they remain administrative
metadata under the receipt's RLS/ACL restrictions. Redacting them here would
break exact snapshot identity and is not part of this change.

The table is invisible to PUBLIC/anon/authenticated: enable RLS, deny runtime
access explicitly, grant only required service_role SELECT/INSERT, and forbid
ordinary receipt UPDATE/DELETE with an immutability trigger. Receipt insertion
is available only through the governed administrative operation in the normal
application workflow. Direct malicious administration is outside the trust
model; SECURITY DEFINER or broad runtime privileges are unnecessary.

Add one SECURITY INVOKER RPC, `record_source_partial_review`, accepting
`p_expected_register` and `p_receipt`. Only service_role may execute it. The
server independently checks the closed receipt shape, C1 evidence, source
identity, expected initial lifecycle, field/event references and exact selected
stored chunk/span/type_fields snapshots. Validate caller input before mutation.

Use the existing publication lock followed by the source row lock. Check the
complete source-register/relational projection, including on replay, and reject
any published membership or legacy/null register. Source/chunk/span writers
must obey the same publication serialization. Verify that existing triggers
cover the inspected chunk/span rows; add only a necessary narrow guard if the
implementation preflight proves a gap. No filesystem/network work under locks.

Derive exactly one appended Evidence and C1 state reference. In one transaction
insert the immutable receipt and update only the source's content_review_state
and source_register. A failed receipt or register check rolls back both writes.
Do not update chunk review flags, source verification, acquisition, issuer,
scope, approval, release membership or active pointers.

Exact replay with the same original expected register and identical receipt
returns the same source register without UPDATE/INSERT. Require the exact
stored receipt, derived register, complete relational projection and unchanged
selected chunk/span snapshots. Missing receipt, reused ID with altered content,
different evidence, stale expected state or content drift is an error; do not
repair it silently. Parallel identical calls succeed idempotently; competing
calls must not overwrite history. Storage errors propagate without automatic
retry or credential escalation. Python validates the exact returned register.

## Verification and delivery

After approval, write an implementation plan and use focused TDD. Cover closed
shapes/types/nulls, truthful retained labels/timestamps, wrong roles/transitions,
foreign or omitted fields/events/dependencies/limits/spans, exact projection,
first-call/replay drift, missing/conflicting receipts, immutable receipt writes,
concurrency, rollback and both actual runtime-role denials. Use synthetic tracked
fixtures; source-derived receipts and raw SQL stay in ignored audit-evidence.

In a uniquely named disposable database, register the same five pending sources,
replay their supported A1 checks, reuse the same 19 chunks/vectors and 54 spans,
then record/replay five scoped C1 receipts. Verify the existing 52 associations
and nine event bindings, unchanged original inputs and all other source/chunk
states, zero active pointers and both runtime roles still hidden. Drop only
that database. Do not rewrite any sealed evidence or shared source register.

Run one independent final review and applicable regression/full-suite checks
once final code is stable. Use existing Python3.13 tools/assets; no dependency,
model, lock or installation changes. Generate an additive migration through
the existing local CLI workflow, without applying it to shared databases.

This is partial content-review bookkeeping for existing confirmed fields. It
does not establish C2/C3 complete review, source verification, office authority,
currentness, approval, calibrated answer sufficiency, institutional activation
or Phase06 eligibility. F04/G01/originalG02 and all source gaps/conflicts remain
held. School-response and source-wording questions are not reopened.

## Choices and approval boundary

Engineering choices: one C1-only interface; a separate immutable receipt table
to preserve actual scope; exact chunk/span snapshots; retained original owner
labels with a separate compilation identity/time; no chunk-status promotion.
The alternative of storing only Evidence would lose the scope of the review.
A general lifecycle updater would exceed the evidence and approved work.

The single builder check reports “nothing important left” after clarifying the
existing-path issue. The builder independently confirms 52 associations/nine
events, 21 unchanged input hashes, 54 spans and 22 same-source dependency edges.
Owner labels are the two existing owner/chat labels; no new personal identity
or office role is introduced. Engineering choice: preserve existing provenance
paths only in admin receipt snapshots. Its cost is retaining workstation paths
as internal metadata; avoiding redaction preserves exact historical identity.

Read-only preflight also verifies the 8-file reconciliation, 49-file readiness
and 119-file A1 seals. Existing five source records remain acquisition observed,
verification/content review pending, approval not_requested/null. No proposed
C1 receipt or resulting source register is persisted. Raw preflight script and
input-readiness.json are under ignored workspace/audit-evidence/
p05-partial-review-design-20261016. No database call or new source decision.

Context consulted: thesis physical17–18, runtime routing PNG already inspected
in this same session, master sections6/10, active phase documents and dataset
location/source-gap guidance. No scope or architecture discrepancy. Models stay
at C:/Coding-projects/MODELS; owner artifact changes remain untouched/unstaged.

The brainstorming skill requires: “Nothing gets built until your human partner
approves the full description”. This design is a new interface beyond the
approved A1 operation. Its implementation and disposable rehearsal need approval
of this description at
[the applied skill](C:/Users/joel/.agents/skills/brainstorming/SKILL.md).
Approval would cover this bounded build, not a new content confirmation, school
authorization, shared deployment, activation or phase advancement.

Final design verification: 514 documentation/phase-ledger tests and 11 subtests
pass in 11.63s, exit0. Phase validation exits0; can-advance exits1 as expected
for the blocked Phase05 handoff. Whitespace checks pass. No product/test/SQL
change, so the completed full suite is not repeated. The design and four
continuity files form one documentation commit; owner artifacts stay unstaged.
The baseline precedes that commit, whose SHA is discoverable from Git.
