# Scoped source-observation implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use executing-plans inline, as specified by the active Phase05 plan.

**Goal:** Persist supported V1 printed observations bound to existing C1 and accepted undergraduate selection.

**Architecture:** SourceVerificationLoader.observe(current, observation) derives
one observed verification state and appended Evidence. An admin invoker RPC
stores an immutable receipt and the source change atomically, using existing
selected-review validation and publication locks. Chunk metadata is rebound
separately through the existing authoring/loader path; content/vectors stay intact.

**Tech Stack:** Existing Python3.13.7/Pydantic, PostgreSQL17.6/pgvector and
Supabase CLI2.117.0; no installations or dependency/lock changes.

**Spec:** [Approved design](2026-10-17-source-observation-design.md), approved
after2a472ba with “alright i approve, continue”.

## Global constraints

- Exact selected-source-observation-v1 keys and selected_reviewed_spans scope.
- Current acquisition verified, verification pending, content partially_reviewed,
  approval not_requested/null; V1 does not establish V2/P2 or school authority.
- Preserve actual owner/C1 attribution and original event times; new time is
  compilation only. Keep source gaps, unknown scope fields and undergraduate scope.
- Reuse sealed five prepared receipts/derivatives and existing19chunks/54spans/
  52fields/nineevents/19vectors. No new source reviews, hashing originals, encoding,
  benchmark/grid, shared migrations, activation, runtime deployment orPhase06.
- Use retained isolated branch/worktree, explicit staging and owner artifact dirt.
- Raw evidence root:workspace/audit-evidence/p05-source-observation-20261017;
  system Python3.13 readiness venv, -B pytest no cache/external basetemp/TEMP/TMP.

## Review focus

- A valid receipt for another source/selection must not count as this source's evidence.
- Exact retries must recheck immutable receipt, full source projection and current snapshots.
- Compiler time must not impersonate a fresh human confirmation or bypass cited C1/decision order.
- Old chunk bindings must fail until ordinary rebinding, without content/vector drift.
- Runtime accidental grants must not expose or mutate observation receipts or source states.

## Task 1: Validated loader

Create backend/bintanong_storage/source_verification.py and
tests/test_storage_source_verification.py. Interface:
SourceVerificationLoader(client=None).observe(current, observation) -> SourceDocumentVersion;
RPC observe_source_verification(p_expected_register, p_observation), role admin.

- [x] Write synthetic loader tests for exact closed schema, source/hash/locator/C1
  ref and scope identity syntax; current lifecycle boundary; reviewer role/new
  Evidence ID/null authority; complete returned contract; preserved inputs/history;
  real timezone/fraction/equivalent instants and observation>=current C1; storage
  failure propagation once. Assert old binding fails/new bind_chunk agrees.
- [x] Run missing-module RED. Implement minimal local validation/derivation,
  existing models/vocabulary and one RPC; no new parsing or status vocabulary.
- [x] Run new unit class plus existing A2/C1 units; expected GREEN. Record results
  and explicitly commit focused loader/tests/continuity increment.

## Task 2: Atomic scoped receipt and admin RPC

Create tests/test_storage_source_verification_database.py and CLI-generated
supabase/migrations/*_phase5_source_observation.sql; update storage README.
Consumes Task1 envelope; produces immutable source_verification_observations and
observe_source_verification returning exact full register.

- [x] Seed synthetic A1/C1/A2 and accepted selected review using existing fixtures.
  Write actual-role DB tests for positive persist/replay/no second UPDATE, C1/
  selected identity/label/time membership, malformed direct RPC, false scopes,
  snapshot/span/field/group drift, missing/legacy/stale/relational drift, concurrent
  equals/conflicts, publication locks/rollback/ever-published guard, runtime receipt
  access/mutation denial including accidental grants, and ordinary chunk rebind.
- [x] Run positive test before migration; expected RED missing RPC/table.
- [x] Generate additive migration using installed CLI help/new. Add composite
  source/evidence PK, source/C1/scope FKs, scope-ref index, RLS/runtime-denial policy,
  immutable mutation/publication-lock triggers and least-privilege grants. RPC
  independently validates shape/state/evidence/source, existing immutable C1 and
  selected coverage via validate_selected_review, exact C1 source snapshot coverage,
  attribution and compilation>=C1/selected-decision times using acquisition_check_time.
  Under publication+row locks derive proposed record, compare full register and
  relational projection, store receipt/change atomically or exact no-update replay.
  Reject missing/stale/published/drift/receipt conflicts without wider promotion.
- [x] Run complete new unit/DB files plus selected-review DB regressions and source
  binding contract tests; expected GREEN. Existing A1/C1/A2 stay unchanged. Document
  rebind/retry boundaries, record evidence and explicitly commit cohesive increment.

## Task 3: Inactive package and final delivery

Consumes Task1/2 and sealed preparation packet; produces report
plans/2026-10-17-source-observation-report.md, single review, final checks/seal.

- [x] One disposable rehearsal reuses pending→A1→C1→A2 records and stored accepted
  review, applies/replays five V1 receipts and compares exact prepared derivatives.
  Rebind/load19chunks without text/span/hash/vector changes, retain C1/selected
  receipts/binding, deny missing-authority activation, verify both actual roles
  see no corpus/retrieve data or admin receipts; drop DB and check input hashes.
- [ ] One fresh final reviewer for2a472ba..implementationHEAD, supplied spec/plan/
  review focus/rulings; resolve material findings in one RED/GREEN fix pass, no
  second review. Final applicable full suite on final product; inspect every result.
- [ ] Verify all owned/reviewer DB cleanup, inputs and earlier seals; seal curated
  new evidence. Finish report/plan/INDEX/checkpoint/blocked handoff/current progress;
  run docs/phase-ledger checks, validate0/can-advance1 expected blocked. Explicit
  Conventional Commit; keep branch/worktree/owner dirt. No shared publication.

## Preflight and rulings

Task1→2 exact RPC/parameter/contract names agree. Task2→3 needs selected review
stored before V1 and bind_chunk after V1; existing saved package supports that.
No source-content or scope decision is missing. Self-review found no design gaps.
Ruling: execute inline without new method/plan confirmation because explicit
approved-design/proceed instruction and active Phase05 plan already supply it;
cost if wrong: isolated rework. Ruling: repository plan/checkpoint and ignored raw
root replace skill scratch/deletion defaults per owner instructions; cost: manual
ledger upkeep. Existing linked branch verified; thesis17–18/routing PNG/master6/10
reconsulted, no discrepancy. Original school/authority/formal phase gates retained.

Task1 RED50missing-module failures/subcases observed; initialGREEN20tests/157
subtests0.80s. Added authoring composition check: stale binding fails, existing
bind_chunk produces V1 reference without content drift; final21tests/157subtests
pass0.86s. Task2 missing-RPC RED1test5.99s, ambiguous SQL column corrected after
11failed/12passed/149subtests76.31s. Final relevant326tests/216subtests pass185.23s.
One selector typo exited4/no tests before corrected run. Inactive rehearsal
5V1/5replays/19rebound chunks/13unchanged inputs passes; DB dropped.
