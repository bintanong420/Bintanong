# Acquisition verification implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task inline, as specified by the active Phase05 plan.

**Goal:** Persist only the supported A2 second byte check after existing C1 partial review.

**Architecture:** Extend SourceAcquisitionLoader with verify(current, check).
An admin-only invoker RPC derives the same acquisition-only change atomically,
with exact expected-register comparison, replay, source/evidence binding and
existing publication locks. Verification/approval/review/visibility stay separate.

**Tech Stack:** Existing Python3.13.7/Pydantic, PostgreSQL17.6/pgvector,
Supabase CLI2.117.0 and disposable storage test harness; no dependency changes.

**Spec:** [Approved design](2026-10-16-acquisition-verification-design.md),
approved by the owner after184b33f with “ye i approve, then proceed”.

## Global constraints

- Undergraduate scope only; no excluded-audience positive institutional fixtures.
- Require acquisition observed, verification pending, approval not_requested/null,
  content review partially_reviewed. Append one distinct allowed A2 Evidence.
- Compare new check to the specifically cited valid A1 observation as instants;
  equality allowed under existing contract, actual five checks strictly later.
- No generic lifecycle updater, C1/A1 behavior change, shared migration,
  activation, new model/encoding/conversion/grid or Phase06.
- Preserve owner artifacts/.gitkeep deletion and untracked backend/artifacts.
- Evidence/logs/basetemp under ignored workspace/audit-evidence; explicit staging.

## Review focus

- An older unrelated check cannot substitute for the specifically cited A1 time.
- Wide timezone offsets, long fractions and equivalent instants need Python/SQL parity.
- Exact replay must still reject full relational drift and published membership.
- C1 evidence/receipts and selected-review binding must survive A2 unchanged.
- No new check may alter source verification, approval, chunk bindings or runtime visibility.

## Files and commands

Modify backend/bintanong_storage/source_acquisition.py and its README;
create tests/test_storage_source_acquisition_verification.py; add one CLI-generated
supabase/migrations/*_phase5_acquisition_verification.sql. Preserve old migrations.
Report at plans/2026-10-16-acquisition-verification-report.md; maintain this plan,
checkpoint, INDEX, handoff and current_progress. Raw root:
workspace/audit-evidence/p05-acquisition-verification-20261016.

PY = existing readiness venv/Scripts/python.exe. Every test command uses
`PY -B -m pytest -q -p no:cacheprovider <selectors> --basetemp <raw-root>/<unique>`.
Use external TEMP/TMP and BINTANONG_STORAGE_EVIDENCE_DIR. Expected passing exit0.

## Task 1: Validated A2 loader

Interfaces: consumes existing SourceDocumentVersion/Evidence/A2 vocabulary;
produces SourceAcquisitionLoader.verify(current, check) -> SourceDocumentVersion
via verify_source_acquisition(p_expected_register=current, p_check=check), admin.

- [x] Write synthetic loader tests for exact request/return, unchanged inputs/history,
  envelope/identity/hash/locator rejection, duplicate/blank IDs, wrong kinds/roles,
  unsupported lifecycle, pending-content rejection, specifically cited A1 order,
  equal/equivalent instants and malformed return/one propagated storage failure.
- [x] Run loader class; expected RED: verify method absent.
- [x] Implement smallest verify method, retaining observe() unchanged. Parse both
  contracts, derive acquisition/evidence only and validate the returned exact record.
- [x] Run loader and existing A1 unit classes; expected all GREEN. Record counts
  and explicitly commit loader/test/continuity as one cohesive increment.

## Task 2: Atomic admin RPC and actual-role regressions

Interfaces: consumes Task1 request; produces service_role-only invoker RPC,
returning complete persisted source register; no schema/vocabulary/RLS change.

- [x] Add disposable DB tests with actual A1 and C1 synthetic preparation. Assert
  persist/exact no-update replay, preserved projection/history/receipts, direct
  malformed inputs and null/missing fields, specific A1 refs/order/time parity,
  stale/conflicting/concurrent calls, missing/null register, first/replay drift,
  published immutability, publication-lock serialization and rollback; assert
  anon/authenticated EXECUTE denial and invisibility, PUBLIC denied/invoker ACL.
- [x] Run positive DB test before migration; expected RED: missing RPC.
- [x] Generate additive migration using installed CLI help/new workflow. Implement
  independent closed shape/state/evidence/source guards and exact register CAS
  under publication + row locks. Compare timestamps without narrow timestamptz
  displacement; preserve original text. Match existing Python microsecond parsing
  for chronological comparison. Complete duplicated projection excludes created_at.
- [x] Run new full file plus A1, C1, selected-review DB/loader, registration and
  storage security regressions; expected GREEN. Document supported boundary/error
  behavior in README; explicitly commit verified SQL/tests/docs/continuity.

## Task 3: Real-package compatibility, one review and final delivery

Interfaces: consumes Task1/2 and sealed five A2 envelopes/expected derivatives;
produces inactive disposable evidence, final review, checks/seal/report.

- [x] One rehearsal reuses saved five pending/A1/C1 records and19chunks/54spans/
  19vectors; compare five A2 results and exact replays to prepared derivatives.
  Retain selected-review receipt/release binding, deny missing-authority activation,
  assert both runtime roles see no corpus/retrieve evidence, then drop own DB.
- [x] Dispatch one fresh independent final reviewer for184b33f..implementation HEAD,
  supplied approved design/plan/rulings. Verify any material findings; one TDD fix
  pass if needed. Do not reopen earlier features or run repeated independent review.
- [x] Run final applicable whole suite once on final product code; if review changes
  product/tests, run it after those fixes. Verify all owned/reviewer DB cleanup,
  input hashes and earlier seals; seal new curated evidence. Never write old seals.
- [x] Finish report/README/INDEX/current progress/checkpoint/blocked handoff and
  final docs/ledger checks; validate0/can-advance1 expected blocked. Explicit
  Conventional Commit, retain branch/worktree and owner artifacts. No shared push.

## Execution rulings and preflight

Ruling: continue inline without another plan/method confirmation: the owner
approved the full design and explicitly directed execution; active Phase05 plan
already specifies inline. Cost if wrong: isolated implementation rework.
Ruling: repository plan/checkpoint are the execution ledger and ignored raw root
holds evidence, following owner location/continuity requirements instead of
external skill scratch tools. Retain evidence/worktree rather than delete them.
Preflight Task1→2: RPC name/parameter names and full contract return agree.
Preflight Task2→3: C1 must occur before A2; prepared inputs already satisfy that.
No other subsystem is added; no spec gaps found in self-review.

Task1 RED:37missing-method failures/subcases,2passing subcases (raw loader-red.log).
GREEN:13tests/60subtests0.58s, exit0, new loader plus existing A1 unit class.
Task1 implementation explicitly committed after this evidence; no behavior change
to observe(). Task2 missing-RPC RED next.

Task2 missing-RPC RED1/4.85s; initial14tests/115subtests pass plus three test-harness
assumptions corrected, corrected3tests/12subtests GREEN15.96s. No product failure.
One real-package rehearsal5A2/5replays/11unchanged inputs/hiddenroles/droppedDB.
Ruling: commit the verified bounded SQL/test increment while broader compatibility
regressions finish, retaining Task2's remaining gate open; one final review can
run concurrently on stable code. Cost if wrong: a subsequent corrective commit,
with no publication or shared migration. Final full suite remains mandatory.

Task2 complete atd20153e: final relevant94tests/630subtests pass376.57s, exit0.
One final review is running; final full suite starts on unchanged d20153e.
Any material review correction requires final verification on corrected code.

Final: fixed sole Important offset-parity finding — new/cited A1 normalization
regression RED4subcases; narrow A2 wrapper and invalid-displacement coverage;
complete A2 plus C1-loader GREEN23tests/201subtests106.03s. No other material or
deferred minor finding; declined-boundary rulings/costs in delivery report.
Initial full run intentionally interrupted before any DB tests, preserved as
history. Commit fix then final corrected-code full suite; no second review.

Final productdba0777 full5507tests/1323subtests GREEN754.26s, six skips/warnings,
exit0. Fresh verifier confirms11inputs, prior6seals8/49/119/489/16047/10files and
all177owned/reviewer databases absent. Final evidence seal/docs/commit closure
follows; no further product, unchanged full-suite or rehearsal work remains.

Approved bounded plan complete:14825-file seal created/verified, digest in report.
Final docs/phase-ledger537tests/11subtests pass12.09s; phasevalidate0 and
can-advance1(expected blocked), whitespace clear. Following documentary commit
closes delivery on unchanged productdba0777; owner artifacts/worktree retained.

Context: thesis physical17–18/routing PNG reconsulted this resume; prior39–44 and
master3/6/10/11/13 architecture retained. No scope/routing discrepancy. Existing
linked isolated branch feat/p05-retrieval-logic verified; owner dirt preserved.
