---
artifact: phase-checkpoint
phase: 4
status: blocked
sequence: 4
plan: plans/phase-04-supabase-storage-plan.md
head_commit: 8f53b72
working_tree: clean
updated_at: 2026-10-12T02:54:00+08:00
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

Security review is delivered. Remediation remains pending; no Phase 05 implementation has started.

## Repository State

- Review baseline HEAD: `8f53b72`, branch `feat/p04-supabase-rls`; initially clean.
- `head_commit` identifies the audited implementation baseline. The following documentation-only audit commit is discoverable through Git; a docs-only HEAD mismatch does not mean database/code verification was repeated at a new implementation revision.
- Documentation changes: `plans/INDEX.md`, this checkpoint, the Phase 04 plan/handoff, current progress, `plans/phase-04-security-review-2026-10-12.md`, and `docs/decisions/phase-04-security-review.md`.
- Implementation, migrations and dependency files unchanged. Raw probes/catalog outputs remain outside Git.

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
- No fix has been applied. Phase 05 prerequisites and full Phase 04 exit-gate validation remain pending.

## Next Action

Implement and verify an additive least-privilege migration for F1 in an isolated database; then repair the F2 access matrix, F3 activation validation and F4 publication invariants, reconcile F5, and run the full exit gate under both runtime roles. Restore a complete handoff only after reading every result.

## Do Not Repeat

- Do not reinstall dependencies or rerun the existing destructive storage suite against a shared/configured hosted database.
- Do not replay hosted CREATE POLICY migrations blindly, reset existing state, activate candidate institutional sources or begin Phase 05 from the historical completion claim.
- Do not regenerate models/embeddings or duplicate weights to review database security.
