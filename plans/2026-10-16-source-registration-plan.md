# Pending source registration implementation plan

> Execute inline with executing-plans and TDD; one final independent review.

Goal: register the existing pending document versions so their unchanged chunks
and saved vectors can enter an inactive draft. This implements the next action
in the owner-accepted [readiness report](2026-10-16-document-loader-readiness-report.md).
The owner's latest continuation authorizes this bounded importer; no source
content confirmation, activation or shared migration approval is inferred.

Architecture: a separate SourceRegistrationLoader validates the existing
SourceDocumentVersion contracts and explicit document storage metadata before
one administrative RPC. A new migration retains the complete register in a
nullable document_versions.source_register JSONB column, projects its existing
metadata/states into existing columns, and inserts parent documents/versions
atomically under the existing publication lock. Exact reimports are no-ops;
conflicting identities fail without overwriting. Pending-only registration
rejects acquisition/verification/review/approval promotion, leaving future
authorized transitions outside this interface. Existing chunk loader/release
manager, RLS, activation gates and legacy rows remain unchanged.

Builder calls: documents require explicit document_id/title/document_category/
namespace/synthetic metadata; generic source_document is not inferred into a
storage category. One document can own several versions; its storage title is
independent of version filenames. No new CLI, downloads or dependency changes.
Full register retention avoids losing evidence references or approval_id. A
source row may persist pending after a later chunk-import failure; that separate
operation cannot activate it. Do not backfill legacy rows through this importer.

Files: backend/bintanong_storage/source_registration.py; one new versioned SQL
migration; tests/test_storage_source_registration.py; backend README; this plan,
checkpoint/current progress and final delivery report.

## Tasks

- [x] 1. Write RED tests for pending registration, full provenance/state retention,
  explicit category requirements, malformed/duplicate/unmatched input rejection,
  exact idempotency, identity-conflict rollback and direct-RPC privilege/promotion
  rejection. Add the smallest Python adapter and transactional invoker SQL RPC;
  run GREEN plus storage/retrieval regressions. Commit verified unit.
- [x] 2. Reuse the sealed 19-chunk/19-vector package in a fresh ignored evidence
  sibling and unique disposable DB. Supply explicit packaging categories:
  handbook academic_handbook, Charter administrative_order, special-class and
  two vehicle memo image versions administrative_order. No enrollment version
  is in this package; the five identities are handbook, Charter, fee and two
  vehicle images. Preserve each existing image identity separately.
  These are storage classifications, not applicability/authority judgments.
  Register sources, import twice, create draft without activation; compare exact
  stored states/full registers/counts/spans/vectors, verify runtime invisibility
  for anon/authenticated and draft pin, then drop only that disposable DB.
- [x] 3. Run full offline suite with existing Python3.13/assets, one independent
  review, fix material findings with RED/GREEN, seal raw evidence, update phase
  ledger/handoffs/report and commit. Phase05 Tasks4/6 stay open; no Phase06.

Verification uses pytest -B/-p no:cacheprovider and ignored external basetemp,
existing StorageDatabase role tests and exact artifact hashes. Raw logs/data:
workspace/audit-evidence/p05-source-registration-20261016; existing sealed
readiness root is read-only. No shared/hosted database mutation. Context scope
physical17–18 and runtime routing PNG reconsulted; master9/10 govern this task.

Ruling: implement only initial-state registration, rather than a general source
approval/updater — this closes the reproduced pending-source prerequisite with
no authority inference. Cost if wrong: later authorized transitions need their
own reviewed interface; existing sources cannot be silently upgraded here.

Task1 evidence: missing-module RED exit2; initial GREEN9tests/19subtests22.12s;
storage/retrieval regression70tests/125subtests97.29s exit0. An additional valid
acquired-contract guard regression is included in final verification. Task2
positive rehearsal exit0:5documents/5versions/19chunks/54spans/19embeddings,
one draft/no active pointer; both runtime roles see zero rows/RPC release_changed;
identical source registers/reimported versions/spans,50sealed input files unchanged.
Packaging ruling: actual fifth source is a second vehicle image, not enrollment;
the explicit five-version map preserves both image identities. No source change.

Final: one Important review finding fixed at8595fb8, cross-record byte/edition
invariants: RED7failures across3tests/subcases;GREEN13tests/25subtests35.78s.
Post-review draft repeats all checks; final full suite5404pass/714subtests,
6skips/6upstreamwarnings374.88s exit0. First full invocation's missing scratch
parent caused965setup errors/two failures; preserved and corrected, no product
patch for that setup issue. Doc/ledger504tests/11subtests14.98s pass.164-file raw
seal recorded in delivery report. No second review or deferred minor findings.
Final rulings: reviewer exclusions remain outside initial candidate ingestion;
trusted administrator boundary, source authority and deployment/phase gates
remain. Cost if treated as authorization: unapproved material could be used as
guidance. Formal Tasks4/6 open; next bounded document calibration, not new source
conversions or embeddings. Product committed dc98b25/8595fb8; documentary closure
follows. See [delivery report](2026-10-16-source-registration-report.md).
