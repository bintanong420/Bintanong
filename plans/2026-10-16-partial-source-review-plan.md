# Scoped partial source review implementation plan

> **For agentic workers:** Use executing-plans inline, task by task, with TDD and one final independent review. Preserve this isolated worktree.

**Goal:** Persist C1 partial content review with immutable exact coverage.

**Architecture:** One administrative loader validates the closed scoped receipt
and derives the source register. One invoker RPC checks source and chunk/span
snapshots under existing publication serialization and atomically inserts an
immutable administrative receipt and advances only content_review_state.

**Tech Stack:** Existing Python3.13/Pydantic, PostgreSQL/pgvector harness and
local Supabase CLI. No installs or dependency/model/lock changes.

**Spec:** [Approved design](2026-10-16-partial-source-review-design.md), owner
“ye sure go ahead” after b5ddea9. Covers implementation/disposable rehearsal.

## Global constraints

- Only C1: acquisition observed, verification pending, approval not_requested/
  null, content review pending → partially_reviewed; scope/history retained.
- Exact receipt/source/event/chunk/span shapes and same-source dependency closure.
- Original owner labels/times remain separate from compiler identity/time.
- Snapshot existing type_fields verbatim, including admin provenance strings.
- Exact replay checks receipt, register, complete relational row and snapshots.
- Runtime/PUBLIC denied; no chunk flags, authority, release or pointer changes.
- Keep all generated/source-derived evidence ignored under workspace/audit-evidence;
  models stay C:/Coding-projects/MODELS and owner artifacts remain unstaged.
- No shared migration, new source decision/wording, grid, encoding or Phase06.

## Review focus

1. A replay with missing/altered receipt or changed source/chunk/span metadata fails.
2. Malformed direct RPC calls fail without leaving either half of the transaction.
3. Competing observations and concurrent chunk writers cannot invalidate snapshots.
4. A subset cannot hide a field, limit, event, span or required neighbor.
5. Runtime roles cannot read/modify receipts or execute the invoker RPC, even
   under accidental future table grants; ordinary admin updates/deletes are denied.

## Task1: Closed administrative loader

**Files:** create backend/bintanong_storage/source_partial_review.py and
tests/test_storage_source_partial_review.py. Reuse Evidence/SourceDocumentVersion,
parse_timestamp, existing span locator validation and client conventions.

**Interfaces:** SourcePartialReviewLoader(client=None).record(current, receipt)
returns SourceDocumentVersion; RPC record_source_partial_review, params
p_expected_register/p_receipt, role admin. Receipt shape is fixed by the spec.

- [x] Write unit tests with synthetic observed source/receipt fixtures: exact
  parameters/return, no input mutation, retained labels/history/paths, malformed
  envelope/event/span/field/dependency data, timestamp chronology, invalid
  lifecycle/evidence/roles, altered return and one-call storage failure.
- [x] Run only loader tests; expected RED is missing implementation.
- [x] Implement the smallest closed-shape validator and derived-record operation;
  validate field/span/event bindings and whole neighbor closure before RPC.
  Storage still independently validates actual row/snapshot equality.
- [x] Verify unit GREEN plus existing acquisition/client/registration units;
  commit loader/tests/continuity explicitly.

## Task2: Atomic C1 storage and immutable receipts

**Files:** CLI-generated additive supabase/migrations/*_phase5_partial_source_review.sql;
extend tests/test_storage_source_partial_review.py; update storage README.

**Interfaces:** source_partial_reviews(version_id,evidence_id,receipt,created_at),
restrictive version FK and composite key; record_source_partial_review(jsonb,jsonb)
returns exact stored register. SECURITY INVOKER, empty search_path, service only.

- [ ] Add actual-role tests for correct persistence/replay and unchanged columns,
  SQL malformed input matrix, wrong lifecycle/evidence, field/event/span/neighbor
  omissions, source/chunk/span drift on first/replay, missing/conflicting receipt,
  exact/competing concurrency, published/legacy rejection and all receipt ACLs.
- [ ] Observe missing-RPC RED; discover the installed CLI via existing repository
  evidence/--help and generate the migration without shared application.
- [ ] Implement exact C1 guards, complete source projection and receipt/snapshot
  comparison under publication lock then source row lock. Existing statement
  triggers already serialize source/chunk/span writes; retain them.
- [ ] Add RLS plus restrictive runtime policies, minimal admin SELECT/INSERT,
  immutable UPDATE/DELETE/TRUNCATE guard and explicit function EXECUTE ACLs.
  Insert receipt and update source register atomically; reject inconsistent replay.
- [ ] Verify GREEN and storage security/idempotency/acquisition/registration plus
  source-aware database regressions; inspect advisor-equivalent ACL/RLS catalog
  and FK coverage inside the disposable harness. Commit SQL/tests/README/ledger.

## Task3: Saved-package rehearsal and final verification

**Files:** ignored driver/results under workspace/audit-evidence/
p05-partial-source-review-20261016; tracked delivery report and continuity docs.

- [ ] Hash-bind prior sealed reconciliation, A1 checks and saved19chunk/vector/
  54span package. Prepare five closed receipts from existing nine event bindings,
  preserving owner labels/original times and recording actual compiler time.
- [ ] In one unique disposable database: register five initial sources, replay A1,
  load19saved chunks/vectors, record/replay five C1 receipts and create inactive
  draft. Verify52field associations/nine events, unchanged other source/chunk
  flags, zero pointers, runtime-role hiding and unchanged original inputs; drop DB.
- [ ] One independent final review of b5ddea9..final product. Material findings
  get focused RED/GREEN; run full suite after final code, then doc/ledger checks.
- [ ] Seal ignored evidence, record exact commands/results/digests and limits,
  update current progress/checkpoint/index/blocked handoff and commit closure.
  Keep Phase05Tasks4/6 and Phase06 blocked on actual remaining prerequisites.

## Execution ledger and rulings

Self-review: each spec requirement maps to Task1/2/3; all five review focuses
have actual-role coverage in Task2. Task1's two-param RPC consumes Task2's exact
register return; Task3 uses the same five records/chunks and immutable receipt.

Ruling: retain established inline execution and proceed after this self-reviewed
plan without another method/plan approval. Owner approved the complete design
and explicitly said go ahead; cost if wrong is bounded implementation rework.
Ruling: use this repository plan/checkpoint/progress and ignored audit-evidence
instead of a disposable skill workspace, following owner storage/continuity
instructions; cost is manual ledger upkeep. Keep the active phase branch.

Task1 RED:81 expected missing-implementation failures/subcases; unit GREEN:
11tests/96subtests2.05s (new loader and existing client). The first implementation
run also exposed a duplicate keyword in locator-default merging; existing tests
reproduced it and dictionary unpacking fixes it without changing source data.
Actual role/SQL validation remains Task2; no C1 source update has occurred.
