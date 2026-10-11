---
artifact: phase-checkpoint
phase: 4
status: in_progress
sequence: 9
plan: plans/phase-04-supabase-storage-plan.md
head_commit: 6e762a5
working_tree: dirty
updated_at: 2026-10-12T03:27:00+08:00
---

# Phase 4 Checkpoint — security gate reopened

The [independent security review](phase-04-security-review-2026-10-12.md) invalidates the original exit-gate ruling. The final handoff is now blocked; Phase 05 is preparation only. The original closure record follows for historical context, then the current recovery state.

## Historical Completion Record (02:35 closure)

- Initialized Phase 4 plan, ledger index, and checkpoint (committed in `3b33c3f`).
- Task 1: Designed complete relational and pgvector schema covering 19 tables in `public` with foreign keys, check constraints, `vector(1024)` embeddings, and singleton active release pointer.
- Task 2: Authored migration `20261012000000_phase4_knowledge_schema.sql` and applied locally with `npx supabase db reset`. Verified all 19 tables created.
- Task 3: Implemented idempotent batch loader in `backend/bintanong_storage/loader.py` importing Phase 3 artifacts (`embeddings.jsonl` and manifest) with duplicate detection (verified in `test_storage_loader_idempotency.py`).
- Task 4: Implemented atomic release publication, activation, and rollback mechanisms in `backend/bintanong_storage/release.py` and PostgreSQL stored procedures (verified in `test_storage_release_isolation.py`).
- Task 5: Authored migration `20261012010000_phase4_rls_policies.sql` enabling RLS on all tables, configuring strict release-isolation SELECT policies, revoking mutation from runtime roles (`anon`, `authenticated`), and adding RPC functions (`match_chunks`, `activate_knowledge_release`, `rollback_knowledge_release`) with `search_path` protections.
- Task 6: Phase 4 exit gate verification, idempotency tests, vector search accuracy, and handoff documentation.
- Verified Supabase Security & Performance Advisors via `npx supabase db advisors`: 0 issues found.

## Historical Repository State

- Head commit: `4244870`.
- Working tree: clean.
- Branch: `feat/p04-supabase-rls`.

## Historical Verification Evidence

- `npx supabase db advisors`: Zero issues reported.
- `tests/test_storage_*.py`: 8 tests passed (exit 0).
- `tests/test_embedding_*.py`: 10 tests passed (exit 0).
- `.agents/skills/bintanong-phase-handoff/tests/test_phase_state.py`: 19 tests passed (exit 0).
- GitHub MCP: repository `bintanong420/Bintanong` inspected and verified.

## Completed Tasks

- Independently reviewed Phase 04 migrations, storage implementation, master sections 9/10/18 and the handoff at `8f53b72`.
- Inspected hosted tables, policies, effective privileges, functions, vector version, migration history and both advisors through Supabase MCP. GitHub MCP confirmed the phase branch exists remotely.
- Reproduced draft-course/out-of-release-rule reads, unchecked activation and mutable publication locally under actual runtime roles in transactions rolled back in full.
- Recorded four P1 findings and one P2 deployment-history finding; reopened the exit gate without changing implementation or hosted state.

## Current Task

Tasks 1 and 2 of [the recovery plan](2026-10-12-phase04-security-repair.md) pass isolated verification. Continue Task 3 deployment reconciliation and final review. Phase 05 has not started.

## Repository State

- Review baseline HEAD: `8f53b72`, branch `feat/p04-supabase-rls`; initially clean.
- `head_commit` identifies the audited implementation baseline. The following documentation-only audit commit is discoverable through Git; a docs-only HEAD mismatch does not mean database/code verification was repeated at a new implementation revision.
- Documentation changes: `plans/INDEX.md`, this checkpoint, the Phase 04 plan/handoff, current progress, `plans/phase-04-security-review-2026-10-12.md`, and `docs/decisions/phase-04-security-review.md`.
- Implementation, migrations and dependency files unchanged. Raw probes/catalog outputs remain outside Git.
- Repair start: reconciled HEAD to the audit commit `7c0ed85`; dirty changes are this checkpoint, the recovery plan, new CLI-generated additive migrations, tests and progress/decision updates as each task starts. No owner changes were present.

## Verification Evidence

- Both local runtime roles have SELECT/INSERT/UPDATE/DELETE/TRUNCATE on all 19 tables. Hosted roles have no INSERT/UPDATE/DELETE, but retain TRUNCATE on all 19. Hosted/local SELECT predicates match.
- External `run_audit.py`: exit 0, both role probes completed. Draft curriculum hidden while course/alias readable; authorized rule readable without release; incomplete release accepted; pending/unapproved evidence then readable; published data/membership changed in place.
- Basic chunk isolation, sequential activation/rollback, exact vector visibility, runtime INSERT denial and administrative RPC denial passed. UPDATE/DELETE affected zero rows under local RLS.
- Hosted security/performance advisors: zero lints. Hosted migration list empty and migration history relation absent.
- Post-rollback fixture and active-pointer counts all zero, matching the original local baseline.
- Ledger validation passed; `can-advance` rejected advancement because the Phase 04 handoff is blocked. Documentation links and whitespace checks passed.
- Existing storage pytest suites NOT RUN: they delete the shared pointer; system Python lacks pytest. No installs. See the review for exact evidence locations and limitations.

## Versions and Digests

- System Python 3.13.7; local PostgreSQL 17.6; hosted PostgreSQL 17.6.1.166; vector 0.8.2 on both.
- Exact migration SHA-256 values recorded in the review. No model execution/download occurred; existing model root remains `C:/Coding-projects/MODELS`.

## Decisions

- [Security ruling](../docs/decisions/phase-04-security-review.md): current security evidence overrides the historical complete handoff. Keep Phase 04 active for recovery and block advancement.
- Preserve historical completion/test claims with their provenance; advisor cleanliness is insufficient to certify application authorization.

## Known Failures or Blockers

- F1–F4 violate privilege, approval/release and publication invariants; F5 prevents a reproducible hosted migration account.
- Historical audit defects are repaired in committed/additive candidate code; shared/hosted application and final review remain pending. Do not infer Phase 04 completion yet.

## Next Action

Finish independent re-review, commit the passing Task 2 increment, dry-run/apply only the two additive migrations locally and hosted, inspect roles/advisors/catalog/history, and run the final storage/phase gates. Restore a complete handoff only after reading every result.

## Do Not Repeat

- Repair Task 1: original migration regression failed in 4 role subtests; additive privilege migration now passes both tests. Command: `python -m unittest tests.test_storage_security -v` under Python 3.13.7. Each run created/dropped only its disposable database; raw evidence is under `audit-evidence/p04-repair-20261012/` outside the worktree. Shared/hosted databases are not yet migrated. The new explicit local auto-exposure setting takes effect on a future normal stack start; no restart was needed for SQL verification.

- Do not reinstall dependencies or rerun the existing destructive storage suite against a shared/configured hosted database.
- Do not replay hosted CREATE POLICY migrations blindly, reset existing state, activate candidate institutional sources or begin Phase 05 from the historical completion claim.
- Do not regenerate models/embeddings or duplicate weights to review database security.

## Repair Task 2 verified (12 October 2026)

- F2: acyclic active-release/approved-parent SELECT predicates hide draft courses/aliases and unbound rules/spans. Operational tables have no runtime access.
- F3: expected membership counts, approved/verified/reviewed documents, source/version/hash/location bindings, complete normalized embeddings and authorized rule provenance are validated before publication.
- F4: statement/row publication locks and immutable published data/configuration/membership guards cover superseded/revoked history; atomic admin RPCs load chunk/span/artifact batches and create releases. Exact reimports preserve span UUIDs.
- Original lifecycle/policy regressions: 29 failing cases before fixes. First full gate: 22 tests passed. Independent review found two P2 import gaps; fixed content/hash/locator checks and automatic set identities bound to the full corpus/vector content. Re-run: 25 tests passed in 57.574s under Python 3.13.7, including an observed concurrent advisory-lock wait and post-publication mutation denial.
- Command: `python -m unittest discover -s tests -p 'test_storage_*.py' -v`. Docker-backed disposable PostgreSQL databases only; no shared pointer cleanup. Raw outputs/artifacts remain under external `audit-evidence/p04-repair-20261012/`.
- Hosted baseline exactly matches historical migration schema: 146 columns, 67 constraints, 37 indexes, 19 policies/RLS flags and 3 functions after CRLF/LF normalization. Prior ACL drift remains recorded. Hosted documents/chunks/embeddings/releases/pointer all zero.
- CLI project-ref connectivity works. `migration repair ... --status applied --project-ref jyrudbiuajahsucsorco` recorded the three verified historical versions without replaying SQL; no institutional data or pointer changed. Final additive migrations are not yet applied.
- Current dirty paths: new release-security migration; production loader/release; isolated test helper and all storage tests (including new concurrency test); recovery plan/checkpoint/progress/decision updates. Existing original migrations preserved.

### Final-review follow-through

- A residual missing-source-text default and nullable SQL inequality were corrected after re-review. Ordered spans now make SQL publication check exact normalized printed-source agreement. Nullable source text supports the existing textless table contract; retrieval falls back to serialized table text.
- Publication/mutation RPCs and triggers reject REPEATABLE READ/SERIALIZABLE snapshots, since the publication lock alone cannot refresh their old transaction snapshots. READ COMMITTED is the supported PostgREST/admin write isolation.
- Unicode/whitespace SQL hash parity and runtime/private function ACL tests pass. An isolation-test fixture cleanup left orphan draft chunks in its own disposable database and caused 16 later fixture conflicts; fixed by giving that test its own disposable database. Targeted verification: all 10 security tests and the nullable-identity regression pass (11 tests, 18.243s). Whole suite re-run pending. No shared data were affected.
- Embedding tests: 12 passed (0.152s; existing Starlette/httpx deprecation warning). Phase ledger tests: 19 passed (17.533s). Both local and hosted dry runs select only migrations 10001/10002. No additive deployment yet.

### Task 2 final gate

All 30 storage tests passed in 69.867s after the final nullable-identity and fixture-isolation corrections. Independent review identified no other actionable findings; all reported P2 items are corrected. No disposable test databases remain. Record the following verified code commit from Git, then apply the two reviewed additive migrations. Raw complete final output: external `p04-repair-20261012/final-storage-tests.out`.

## Task 3 deployment and advisor follow-through

- Task 2 commit: `6e762a5`; 30 tests passed. CLI `db push --skip-vault` applied 10001/10002 to local and hosted targets, with no seeds/roles/vault updates or reset.
- Live local/hosted checks: both runtime roles have 17 SELECT grants, zero writes/admin RPC execution/public CREATE/private USAGE; all 19 tables use RLS, all application functions are INVOKER, vector 0.8.2, institutional tables and active pointer remain empty. Migration history exactly matches all five files.
- Advisor results at INFO level: no WARN/ERROR; six pre-existing uncovered foreign keys, two deliberate admin-only tables without policies, and unused indexes on empty tables. New additive 10003 covers the six foreign keys and adds restrictive runtime-deny policies for operational tables without grants. New policy regression observed RED (one failure), then all 11 security tests passed after correction.
- The CLI-generated 10003 empty scaffold was replaced by the next numeric version, preserving previously applied history. Pending: commit/apply 10003, verify catalog parity and advisors, then the final full suite and handoff. Unused-index INFO notices are expected on empty corpora; do not remove required indexes to suppress them.
