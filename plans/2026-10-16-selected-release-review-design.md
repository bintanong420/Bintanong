# Release review coverage for an exact undergraduate selection

Status: proposed for implementation review. Baseline `20b8230`; verified product
remains `9e6526c`. No code, migration, database or release changes in this design.

## Purpose and scope

The owner accepted completion of review for the exact 19 selected chunks after
`234df0c`, conditional on complete coverage. The condition passed: 52 field
associations, 54 spans, zero uncovered spans and 22 required-neighbor edges.
See [the accepted decision](2026-10-16-selected-corpus-review-scope.md).
That decision is settled; this document proposes software that can consume it.

Student capability: retrieve reviewed undergraduate procedures and policy
explanations with their original citations and limitations. Evidence path:
existing immutable C1 receipts and accepted selected-scope decision -> exact
release-review coverage -> existing governed publication -> runtime retrieval.
This addresses the review prerequisite of master6/10 and Phase05 Tasks4/6.
The question resolved by this design is how a release can use reviewed selected
content without claiming that the full original documents were reviewed.

Owner reminder during this work: support undergraduate student procedures;
exclude Law, Medicine and staff-only procedures. Retain the existing graduate
and laboratory-school exclusions. General student procedures need not contain
the word undergraduate: use intended audience and contextual applicability.
Shared services and required staff actions within a student transaction can
remain in scope. Unresolved audience/applicability stays unresolved. Neither
absence of an excluded keyword nor a software scope label supplies that review.
No new corpus content or applicability decision is introduced here.

## Observed limitation and chosen approach

Current `check_chunk_binding` correctly copies source-register review state to
bound chunks. The SQL release validator and runtime policies, however, require
both a whole source and each chunk to have review state `reviewed`. A partially
reviewed source with fully reviewed selected content cannot express that case.

Builder choice: preserve source/chunk scalar states and their existing binding
contract; represent completed selected coverage separately and bind it to an
exact draft release. Keep the existing whole-source-reviewed path for callers
without a selected-review binding. Do not add a generic source-state updater,
set whole documents reviewed, weaken office authorization or use candidate
flags as a publication override. This is a release-review interface, not C2/C3.

A documentation-only decision remains sufficient to preserve the owner's reply.
This additional software is justified by the concrete publication consumer above,
not by a need to record that reply twice. Its implementation requires approval
of this full description; the accepted source-content decision is not re-opened.

## Administrative interface and receipt

Add `SelectedReleaseReviewLoader.record(receipt)` and
`bind_release(release_id, review_scope_id)` in the storage package. Both use
the existing injectable storage client and administrative RPC pattern. There
is no student endpoint, CLI, automatic review inference or model call.

Use a closed receipt format `selected-release-review-v1` with these fields:

- `review_scope_id`: 64 lowercase hexadecimal identity supplied by trusted
  preparation; for this package use the accepted-scope-verification file digest.
  This is an external evidence identifier, not a claim that SQL hashed that file.
- `receipt_format`, `supported_scope='undergraduate_academic_affairs'`.
- `decision`: a closed object with `evidence_id`, `reviewer_label`, `compiler_label`,
  `recorded_at`, `timestamp_meaning`, `owner_response`, `decision_document`,
  `acceptance_record_sha256`, `coverage_inventory_sha256`, `draft_chunks_sha256`.
- `sources`: one entry per version, containing exactly `version_id`,
  `source_sha256`, `partial_review_evidence_id`. These name existing C1 receipts;
  they do not embed or rewrite current authority/register states.
- `chunks`: the exact C1 projection for every selected chunk: `chunk_id`,
  `content_hash`, complete `type_fields` and complete ordered stored `spans`.

Sorted source/version and chunk identity order is required; nested span order,
field order, source-event IDs, gaps and required-neighbor order remain intact.
Reject duplicate sources/chunks, empty coverage, extra keys, malformed hashes,
missing labels, invalid timestamps, nonmatching source/receipt identities or
decision evidence predating its bound source reviews. The compilation recording
time is recorded honestly; do not invent the exact time of a chat response.
The decision_document is a repository-relative path; original/private bytes and
new workstation paths are not added. Existing metadata within exact C1 snapshots
retains its recorded administrative provenance, with no runtime disclosure.

Python reuses Chunk parsing, reviewed-context rendering and existing complete
record/group validation. Require every source span to be covered in order by
the field associations, every field event to occur in its referenced C1 receipt,
and all required neighbors to occur in this same selection/source version.
Retain established applicability_basis_ref values; trusted preparation remains
responsible for truthful audience/content decisions. A recorder label or scope
string does not authenticate a reviewer or establish institutional authority.

Return exactly the stored receipt. Storage errors propagate without a retry
loop. Repeating the same receipt returns the same record; reusing its identity
with any altered content or decision fails. No source/chunk flags change.

## Database storage, binding and validation

Use one new administrative table `selected_release_reviews`, keyed by
review_scope_id, holding the closed receipt and server creation time. Add a
nullable `review_scope_id` foreign key to knowledge_releases, with a supporting
index and restricted deletion. Receipt UPDATE/DELETE/TRUNCATE are denied by
privileges and immutable triggers. Referenced C1 receipts stay immutable.

Two service-role-only SECURITY INVOKER RPCs record the receipt and attach it to
a draft. Use empty search_path, fully qualified relations, explicit PUBLIC/anon/
authenticated EXECUTE denial, table RLS with runtime denials, and the existing
publication advisory lock. SQL independently verifies the closed shapes,
source/C1 identities, exact current chunk hashes/type_fields/span projections,
field/span/event coverage and required neighbors. Recompute current content
hashes; retained stored hashes alone are insufficient to detect text drift.
No filesystem/network/model work occurs while holding the lock.

Binding requires an unpublished draft, exact equality between release chunk IDs
and receipt chunk IDs, exact equality between release source membership and
receipt sources, and no institutional rule members. Replaying the same binding
is idempotent. Reject replacing another binding; changing a selection requires
a distinct draft/receipt with its own actually applicable review decision.
Do not infer acceptance for another selection merely because this API is generic.

Publication validates current coverage again under the same lock, including
the exact required neighbors, fields, spans, content, limits and membership.
For an explicitly bound selection only, content review may be `partially_reviewed`
at source and chunk level with matching existing C1 evidence; `reviewed` remains
valid. Source/chunk review claims still agree through existing bind/check logic.
An initial/pending review state cannot use this path. No unbound partially
reviewed source passes publication. Default whole-reviewed behavior is unchanged.

All existing source verification, approval/reference, acquisition/provenance,
embedding integrity, counts, immutability, rule and active-pointer requirements
continue to apply. The receipt supplies content-review coverage only. Missing
office evidence remains missing. Publication with the current real-source
registers must still fail; this build does not implement verification or approval
transitions. Published release metadata/membership/covered evidence remain frozen.
Rollback revalidates the same immutable receipt and the existing other guards.

## Runtime visibility without exposing receipts

Keep the existing acyclic policy dependency order: active pointer -> active
release -> memberships -> document versions -> chunks -> spans/embeddings.
For active published releases with an explicit selected-review binding, permit
their approved/verified partial-review sources and corresponding partial-review
chunks. The publication validator has already proved exact review coverage;
runtime policies must still check the active membership and source identity.
Drafts, unselected chunks, unrelated versions and superseded releases stay hidden.

Runtime policies do not SELECT administrative receipt tables or call privileged
helpers. Do not introduce a reverse dependency from release membership into
chunks, recursive RLS or SECURITY DEFINER access. The release's opaque scope ID
may be visible with its existing metadata; receipt contents remain administrative.
Current retrieval request/result schemas, candidate flags and source-aware
calibration statuses remain unchanged. Source/date/gap context stays attached.

## Verification and execution limits

After full-description approval, write the implementation plan and use focused
TDD. Synthetic tracked fixtures must cover receipt validation, exact replay,
changed decision/text/hash/metadata/span/neighbor rejection, membership extension
or omission, wrong source/scope, actual-role ACL/RLS, immutability, concurrency
with chunk/release writers, whole-reviewed compatibility and rollback.

Use actual anon/authenticated roles in disposable databases. A synthetic source
with separately valid synthetic authority can demonstrate successful publication
and exact selected visibility; nearby unreviewed chunks and explicit excluded-
audience controls must remain hidden. This tests software, not actual source
authority. Do not create positive Medicine/Law/staff policy fixtures.

Reuse the existing 19 saved real vectors and package for a single inactive
disposable rehearsal: import parents/chunks, record A1/C1 using existing evidence,
derive disposable chunk binding metadata with existing bind_chunk against the
actual C1 register, and reimport those bound chunks with the same text, hashes,
spans and saved vectors. This copies partial review from the register; it does
not assert whole-source completion. Store this receipt and bind its exact draft.
Receipt comparisons intentionally cover content/type_fields/spans, not evolving
source verification/approval state. Verify both runtime
roles see nothing and activation rejects missing authority. Preserve original
inputs, prior seals and history; clean up only owned disposable databases.
Do not repeat the multilingual grid, query encodings or source confirmations.

No shared migration/application, hosted write, real-source publication, runtime
deployment, model/dependency install, executable Prolog or Phase06 advancement.
One final independent implementation review and appropriate final regression
checks follow implementation. Any later source/release activation retains its
separate evidence and authorization requirements.

## Context and documentation references

Same-session thesis physical17–18/39–44 and routing PNG remain applicable;
master3/6/10/11/13, accepted scope decision, actual binding code and Phase04/05
release policies were consulted. The scoped path preserves the undergraduate
advisory boundary and structured/Prolog curriculum architecture.

Current Context7 Supabase documentation confirms explicit function privileges
and invoker functions; RLS documentation warns against mutual policy recursion.
This design keeps the repository's acyclic approach rather than adding a
privileged bypass. Sources: [database functions](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/functions.mdx)
and [row security](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/postgres/row-level-security.mdx).
Changelog index consulted; local version changes or upgrades are not proposed.

The brainstorming skill requires: "Nothing gets built until your human partner
approves the full description". See [the applied skill](C:/Users/joel/.agents/skills/brainstorming/SKILL.md).
Approval here concerns this release-review software and disposable verification,
not renewed content confirmation or school approval.

One independent read-only builder check reports "nothing important left".
No additional source/wording/scope decision was requested. Parent review confirms
the existing whole-reviewed path is retained and scoped publication still needs
actual verification/approval. No implementation or database job was run.
Documentation/phase-ledger checks: 519 tests and 11 subtests pass in13.62s,
exit0, using the existing Python3.13 environment, bytecode/cache disabled and
ignored workspace basetemp. Phasevalidate passes; can-advance remains blocked;
whitespace checks pass. Raw log under workspace/audit-evidence/
p05-selected-release-review-design-20261016/docs-ledger.log. No product-suite
rerun, source-state change or database call was required for this design.
