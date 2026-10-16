# Acquisition observation implementation plan

> **For agentic workers:** Use executing-plans to implement inline, task by task, with TDD and one final independent review. Preserve the existing isolated worktree.

**Goal:** Persist only the approved A1 acquisition pending→observed transition from an existing source-bound byte check.

**Architecture:** A small administrative loader validates existing contracts and
derives the observed record. One invoker RPC independently derives the same
change under the existing publication lock, enforces complete row consistency
and compare-and-set semantics, and returns the persisted register.

**Tech Stack:** Existing Python 3.13/Pydantic contracts, PostgreSQL/pgvector
storage harness and Supabase migration CLI. No dependencies or installs.

**Spec:** [Approved design](2026-10-16-acquisition-observation-design.md), owner
“ok proceed” after `78ae763`. This approval covers implementation and a disposable
five-source rehearsal; it adds no source verification/approval or shared deployment.

## Global constraints

- Only A1: all four supplied lifecycle states initially pending/not_requested,
  null references/approval ID; only acquisition and appended evidence may change.
- Exact four-key check envelope; existing Evidence/schema/vocabulary validation.
- No original-source I/O in the loader; trusted administrative check preparation.
- Existing identity/scope/history retained; exact replay cannot hide row drift.
- Only service_role executes the new invoker RPC. Runtime roles remain denied.
- Reuse sealed source checks/package/vectors; original artifacts remain unchanged.
- No shared migrations, activation, new encodings, office-response request or Phase06.
- Raw logs/artifacts and pytest basetemp under ignored workspace/audit-evidence;
  models remain under C:/Coding-projects/MODELS. Preserve owner artifact changes.

## Review focus

1. Divergent flattened metadata on a replay must fail, not return success.
2. Direct RPC null/missing/wrongly typed members must fail without partial updates.
3. Stale callers and simultaneous different observations must not overwrite history.
4. Published or legacy/null-register sources must remain immutable/unsupported.
5. Uncertain HTTP outcomes must not trigger automatic retries or role escalation.

## Task 1: Validated administrative loader

**Files:** create backend/bintanong_storage/source_acquisition.py and
tests/test_storage_source_acquisition.py. Reuse SourceDocumentVersion, Evidence,
evidence_authorizes, SourceRegistrationLoader and synthetic pending fixtures.

**Interface:** SourceAcquisitionLoader(client=None).observe(current, check)
returns SourceDocumentVersion. Current accepts a model or JSON dictionary;
check is the exact envelope in the design. RPC name observe_source_acquisition,
params p_expected_register/p_check, role admin. Parse and compare its return.

- [x] Write focused unit tests for exact derived return/administrative parameters,
  untouched inputs/retained prior evidence, invalid source/hash/locator/kind/role/
  timestamp/duplicate ID/initial-state guards before RPC, and altered RPC returns.
- [x] Run the focused unit tests; observe the missing implementation failure.
- [x] Implement the smallest loader using existing contract validators. Let storage
  failures propagate without retry. Reject noncanonical return values.
- [x] Verify GREEN and existing registration/client contract regressions; commit.

## Task 2: Atomic database observation

**Files:** add the CLI-generated phase5_acquisition_observation migration; record
its exact generated path in this plan/checkpoint. Extend the new test file with
actual disposable-database tests. Modify storage README for the interface.

**Interface:** observe_source_acquisition(p_expected_register jsonb, p_check jsonb)
returns jsonb (the exact stored SourceDocumentVersion). SECURITY INVOKER, explicit
service_role EXECUTE, runtime/PUBLIC revoked. No caller-supplied desired record.

- [ ] Write actual-role tests: correct first call/replay and flattened register
  consistency, retained evidence, stale/different concurrent observations,
  malformed direct calls, wrong source binding and attempted wider transitions.
  Pin each of the five Review Focus conditions with assertions, including
  published/null-register rejection and replay with drifted relational metadata.
- [ ] Observe RED for missing RPC. Discover existing CLI usage with --help;
  generate the additive migration without applying it to shared databases.
- [ ] Implement closed-shape/null/type/initial-state/A1 checks. Validate real
  timestamp syntax/value. Derive the observed JSON from expected + one Evidence.
  Acquire publication lock; require full stored register/row projection equality
  for either expected or exact observed replay; reject published membership.
  Update only acquisition_state and source_register, then return the register.
- [ ] Verify actual persisted values and no writes on failures, both runtime-role
  denials and importer conflict after observation. Run relevant storage/governance
  regressions. Commit the cohesive SQL/test increment.

## Task 3: Existing five-source rehearsal and closure

**Files:** update this plan, active checkpoint/progress/index/handoffs and a concise
delivery report in plans/. Raw driver/results stay ignored, not in product code.

- [ ] Bind existing pending five-version package and sealed byte-check inputs by
  hash. Prepare only the design's check projection, preserving actual recording
  times/roles and fresh-hash-{version_id} Evidence IDs.
- [ ] In one uniquely named disposable database, register initial sources, apply
  each A1 observation twice and compare complete stored/returned records. Retain
  all other states, source identities and existing span/vector bindings.
- [ ] Reuse the existing chunks/vectors for an inactive draft compatibility check;
  verify both runtime roles remain unable to see the real-source corpus/release.
  Keep original package files unchanged; remove only the rehearsal database.
- [ ] Run one independent final review; resolve material findings with focused
  RED/GREEN. Run applicable full/product and documentation/ledger checks once the
  final code is stable. Record exact commands/results/raw hashes and limitations.
- [ ] Commit verified delivery and continuity; validate phase ledger. Keep formal
  Tasks4/6/Phase06 blocked on their remaining real verification/approval/runtime gates.

Self-review: all design interfaces, guards, replay ordering and rehearsal limits
map to these tasks. Execution remains inline as already established; no repeated
design or execution-method approval is needed for the approved scope.

Task1 evidence: missing-module RED31 failing cases/subcases, then GREEN11tests/
46subtests (loader + existing HTTP client) in1.87s. Inline execution ledger is
this repository plan/current checkpoint plus ignored audit root, following owner
location/continuity instructions rather than an extra .superpowers workspace.
Pre-flight: Task1 produces the exact two-param admin RPC consumed by Task2;
Task2 returns the full source register consumed by Task1/Task3; no conflicts.
Ruling: retain execution inline without a second plan/method approval because
owner approved the complete bounded design and continuation. No wider gate added.
