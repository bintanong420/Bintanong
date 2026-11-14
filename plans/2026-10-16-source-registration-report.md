# Pending source registration delivery — 16 October 2026

The missing parent-source registration capability from the
[readiness report](2026-10-16-document-loader-readiness-report.md) is implemented
at `dc98b25`, corrected at `8595fb8`. Existing pending document candidates now import into a disposable
database and form an inactive draft. Shared/hosted databases remain unchanged;
this is not an active retrieval release or formal Phase 05 completion.

## Delivered behavior

`SourceRegistrationLoader.load_versions(versions, documents)` validates complete
SourceDocumentVersion contracts, initial states and explicit parent metadata,
then calls administrative `register_pending_sources`. The new candidate migration
`20261016000000_phase5_source_registration.sql` adds nullable
`document_versions.source_register` for full provenance. It projects the existing
metadata and four states without promotion and inserts documents/versions in one
transaction under the publication lock. Exact reimports preserve rows; conflicts
reject the entire registration batch. Runtime roles have no EXECUTE permission.

The importer also invokes the existing cross-record check_register contract.
SQL rejects reused source bytes under distinct version IDs and editions bound
to different bytes, including across subsequent batches, under the publication
lock. It does not silently merge existing data.

The importer accepts only pending acquisition/verification/content review,
not_requested approval and null approval ID. It is not an authorized transition
or legacy-backfill interface. Full contract evidence references are retained;
existing rows remain null in the new column. Existing chunk loader and release
manager behavior are unchanged. Registration and subsequent chunk loading are
separate resumable transactions; pending parents left by a later load failure
remain invisible through existing RLS.

Storage categories and titles come from explicit caller metadata, not filename
heuristics or the generic source-register category. The real rehearsal used
academic_handbook for the handbook and administrative_order for the Charter,
special-class memo and two vehicle image versions. The existing five identities
include no enrollment source; both vehicle images retain their separate IDs.
These are packaging classifications, not source approval or effectivity claims.

## Verification already observed

- Focused RED: missing source_registration module, expected collection error,
  exit 2. Initial GREEN: nine tests / 19 subtests, 22.12s, exit 0.
- Storage/retrieval regressions: 70 tests / 125 subtests, 97.29s, exit 0.
- An additional valid acquired-contract rejection test passes in 2.55s. This
  distinguishes the pending-only boundary from invalid-contract rejection.
- The positive source-derived rehearsal runs actual service_role/anon/
  authenticated PostgreSQL calls through the existing disposable DB harness,
  not a mocked database. No model or tokenizer calls, new vectors or downloads.

Database `bintanong_storage_test_41d1d76616164457979af9aa3a347da0` applied existing
repository migrations only there. It registered sources, imported chunks/vectors
twice, then created one draft without an activation attempt:

| Stored object | Count |
| --- | ---: |
| Documents / document versions | 5 / 5 |
| Chunks / ordered source spans | 19 / 54 |
| Embedding sets / embeddings | 1 / 19 |
| Draft releases / active pointers | 1 / 0 |

All five complete source registers compare exactly with the saved input. Version
rows and span identities remain identical after reimport. Chunk content, scope,
known limits, IDs, token estimates and pending states match. Embedding record
hashes and exact saved token counts match; pgvector's float32 component roundtrip
error is below 5e-9. The second import reports 19 duplicates avoided. The chunk
loader's total_documents_loaded remains zero because registration is separate;
actual document rows are independently checked as five.

Both runtime roles see zero rows across documents, versions, chunks, spans,
embeddings, releases and active pointer. Actual retrieve_context against the
draft pin returns release_changed with no items. The unique database was dropped
through the existing name-checked cleanup. All 50 files in the sealed readiness
input root, including its manifest, remain byte-identical. The embedding set
remains `02fce0fc4caca1c15cc4a58f5e511f70d5dc27be77769f7cbb0f7ce423368811`.

## Final verification and review

The single independent reviewer found one Important identity gap, no Critical
or Minor findings: per-record validation omitted cross-record byte/edition
invariants. It was independently reproduced RED (seven failures across three
tests/subcases), then fixed in one pass using check_register plus locked stored
identity checks. GREEN: 13 tests / 25 subtests, 35.78s, exit 0. No second review.

The corrected positive draft rehearsal repeats the same counts/full register,
span/row identity, float32 and runtime checks in disposable database
`bintanong_storage_test_09d62e5529ed4cfb96bc8eb13ca6d1dc`, then drops it. All 50
sealed input files remain unchanged; no source-state promotion or activation.
Initial and post-review raw outputs remain separate.

The first full-suite invocation failed because its nested basetemp parent was
missing. Result: 4437 passed / 708 subtests, two skipped, five warnings, 965 setup
errors and two failures, 334.69s, exit 1. The failures were both parameterizations
of test_actual_long_paths_fit_with_generated_stage_and_atomic_temp_names; the
first setup error was test_consumer_refuses_altered_or_incomplete_bundles[raw].
Tracebacks identify basetemp mkdir WinError 3, not product assertions. A targeted
document-inspection and embedding setup check each pass with an existing parent.
The corrected full suite uses a flat scratch path whose parent exists:
**5404 passed / 714 subtests, six skipped, six upstream warnings, 374.88s,
exit 0**, at corrected code `8595fb8`. The initial failed output is preserved.
Command: readiness Python `-B -m pytest tests -q -p no:cacheprovider --basetemp
<raw-root>/final-temp`, with external MODELS_DIR, offline model flags and ignored
process temporaries. No further product behavior changes follow this run.

Documentation/phase-ledger tests pass 504 tests / 11 subtests, 14.98s, exit 0.
Phase validation succeeds; can-advance exits 1 for the expected blocked handoff.
Whitespace checks pass. Final check logs remain in a separate sibling so the
raw seal is not mutated by subsequent verification.

Final same-suite closure verification also passes 504 tests / 11 subtests in
12.82s, exit 0; the four current/prior curated seals verify unchanged.

Reviewer exclusions are bounded rulings: source authority/content/currentness,
future transitions/backfill, hostile administrative callers, hosted HTTP/JWT/
deployment/performance and formal calibration/phase completion remain outside
this candidate interface. Existing approval/RLS/phase gates stand; a trusted
administrative ingester is required and SQL is not a replacement for all Python
contract checks. Mistaking candidate import for institutional permission would
expose unapproved guidance. No deferred minor findings.

## Boundaries and next action

The student capability advanced is source-backed retrieval of undergraduate
procedures and explanations. Evidence now traverses the parent-source importer,
chunk/vector loader and draft-release manager. This closes the reproduced
registration prerequisite, not calibration or source authorization. Existing
source-aware outcomes remain uncalibrated/insufficient; formal Tasks 4/6 remain
open. Curriculum facts/eligibility retain their structured/Symbolic path.

Next reconcile and select the bounded document-retrieval calibration policy
using the existing accepted cases/evidence and delivered integration; shared
migration/application and institutional activation retain their gates. Do not
repeat package construction, source conversions, completed draft verification,
new embeddings or settled wording/source reviews. School verification, F04,
G01/original G02 and original cutoffs/conflicts remain held. No Phase 06 plan.

Implementation ruling: initial-state registration deliberately defers acquired/
approved transitions and legacy backfill to a separate governed interface.
The cost is additional later transition work, rather than silent source upgrades.
Packaging correction: no enrollment version is present; two existing vehicle
image identities remain separate. This changes no source content or approval.

## Evidence and reproduction

Ignored raw root: workspace/audit-evidence/p05-source-registration-20261016.
It contains RED/GREEN/regression logs, explicit storage metadata, positive draft
script/result and SQL outputs. Use the existing Python3.13 readiness venv, -B,
pytest -p no:cacheprovider and external basetemp; no dependency/lock changes.
Context scope physical17–18 (existing original renders), runtime routing PNG and
master9/10 were consulted on resume; no discrepancy. Context7 official Supabase
invoker/grants guidance and current changelog consulted; no shared migration.
Owner artifacts/.gitkeep deletion and backend/artifacts remain preserved/unstaged.

Curated raw evidence seal: 164 files, manifest SHA-256
`9ec29c54682ac14663d7872c89c49dced4e82abea4689c1437412f69e88d6c9e`.
It covers top-level logs/scripts/metadata and initial/post-review draft plus
reviewer identity SQL evidence, excluding test scratch/repetitive test DB logs.
Use only `python -B seal_evidence.py verify`; do not rerun writers in this root.
Prior readiness, source-aware integration and document-comparison seals remain
unchanged. Check logs: workspace/audit-evidence/p05-source-registration-checks-20261016.
