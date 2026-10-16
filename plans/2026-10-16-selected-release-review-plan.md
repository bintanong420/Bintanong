# Selected release review implementation plan

> **For agentic workers:** Use executing-plans inline, task by task. Owner approved
> the complete design at28be67e with "i approve, proceed"; no repeated plan/method approval.

**Goal:** Consume exact selected undergraduate review coverage without claiming
whole-source completion or weakening source authority.
**Architecture:** Immutable administrative receipt, exact draft binding, and
publication/RLS integration retaining the existing whole-reviewed path.
**Tech stack:** Existing Python3.13, PostgreSQL/Supabase migrations and test harness.
**Spec:** [approved design](2026-10-16-selected-release-review-design.md).

## Global constraints

- Undergraduate academic affairs; general student applicability judged in context.
- No positive excluded-audience policy fixtures, shared application, actual-source
  activation, downloads, dependency changes, executable Prolog or Phase06.
- Existing owner artifact changes stay untouched; explicit staging only.
- Existing isolated feat/p05-retrieval-logic worktree retained.
- All raw evidence/temp files under workspace/audit-evidence/p05-selected-release-review-20261016.
- Python readiness venv, -B, pytest -p no:cacheprovider and external basetemp.
- Exact receipt fields and interface are defined by the approved spec.

## Review focus

- Text drift with retained hashes: SQL must recompute current hashes on first/replay/publication.
- Cross-source neighbors or partial groups: reject before binding/publication.
- Lifecycle changes after C1: compare content snapshots, not historical authority flags.
- Draft membership changes after binding: revalidate exact membership at publication/rollback.
- Runtime privacy: no administrative receipt reads, recursive RLS or privileged bypass.

## Task 1 — Receipt loader and synthetic validation

Status: complete. Expected missing-loader RED46subcases; GREEN4tests/52subtests
0.51s. Initial fixture-only missing locator keys corrected before actual RED.
Ruling: the receipt is a stored C1 projection, not a full Chunk contract; use
the existing codec stored-row path (parses each SourceSpan), avoiding invented
document/tokenizer metadata. SQL owns binding to actual C1 events/current rows.

Files: create backend/bintanong_storage/selected_release_review.py and
tests/test_storage_selected_release_review.py; reuse existing reviewed-context/
group renderers and C1 snapshot conventions.
Interfaces: SelectedReleaseReviewLoader.record(receipt) -> dict;
bind_release(release_id, review_scope_id) -> dict with exactly those two keys.
RPC names: record_selected_release_review(p_receipt),
bind_selected_release_review(p_release_id,p_review_scope_id), both admin only.

- [ ] Write synthetic receipt/recording-client tests: closed shapes, sorting,
  hashes/timestamps/path, exact reconstructed text, full ordered spans, event/
  source references, same-source neighbors and complete groups; returns exact
  receipt/binding; malformed response rejected; transport error propagates once.
- [ ] Run focused tests and observe expected missing-loader RED.
- [ ] Implement minimal loader validation; reconstruct Chunk input from stored
  receipt projection using existing context codec and derive hashes, not statuses.
- [ ] Run focused GREEN plus existing C1/contract regressions; record results.
- [ ] Explicitly stage/commit verified loader/tests and checkpoint/progress.

## Task 2 — Atomic scoped publication and actual-role verification

Status: complete. Actual missing-RPC RED; final relevant41tests/387subtests
GREEN157.03s, including actual-role ACL/RLS, content drift, membership changes,
publication/rollback, C1 compatibility and source-aware database integration.

Files: CLI-generated migration, same synthetic test file/database integration
companion as needed, backend/bintanong_storage/README.md.
Interface: table selected_release_reviews and nullable knowledge_releases scope
FK; two RPCs above. Existing release manager interfaces remain compatible.

- [ ] Add disposable database tests; observe missing-RPC RED before migration.
- [ ] Generate migration with installed supabase migration new; implement receipt
  validation, immutable storage, exact draft binding, replay/conflict checks and
  publication-lock protection using existing C1 snapshots.
- [ ] Extend validate_release and active source/chunk RLS only for explicitly
  bound, exact selected coverage. Retain source/chunk state matching and every
  independent authority/provenance/embedding check. Keep old full-reviewed path.
- [ ] Verify direct malformed admin calls, role ACL/RLS, late rollback, text/
  metadata/span/neighbor drift, membership extension/omission, concurrent writers,
  immutable published metadata, exact selected visibility and rollback.
- [ ] Run existing storage/retrieval integration regressions. Stage/commit the
  additive migration/tests/docs with checkpoint results after GREEN.

## Task 3 — Inactive saved-package rehearsal and final closure

Files: ignored rehearsal/verification script, tracked dated delivery report,
plan/checkpoint/progress/index/handoff and relevant package README.

- [ ] Reuse existing five source records/A1/C1 receipts, 19 chunks/vectors;
  preserve all input hashes and source gaps. Prepare receipt from the actual
  accepted decision, using its recorded compilation timestamp honestly.
- [ ] One uniquely named disposable draft: import, A1/C1, existing bind_chunk
  metadata copy/reimport, store/replay receipt and bind/replay draft. Confirm
  activation denied without authority and both runtime roles hidden. Drop DB.
- [ ] One fresh independent whole-change review; fix any material issue with
  RED/GREEN, then relevant regressions. No per-task review dispatches.
- [ ] Run appropriate full suite and documentation/phase-ledger checks, verify
  actual output and owned DB cleanup. Seal new raw evidence without touching
  historical seals. Record exact commits/digests/results and remaining gates.
- [ ] Mark this plan complete and commit documentary closure. Phase05 formal
  Tasks4/6 remain open until actual source/release/runtime prerequisites pass.

Self-review: spec receipt/publication/runtime requirements mapped to Tasks1/2;
real-source privacy, scope and execution limits mapped to Task3. No new owner
content/source/scope decisions required. Inline method follows existing phase
plan and owner instruction to proceed; a second method approval would repeat it.
