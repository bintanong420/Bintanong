# Phase 04 security repair implementation plan

> Execute inline using the executing-plans skill; request an independent review of the final change.

Goal: resolve F1–F5 from [the approved security review](phase-04-security-review-2026-10-12.md), verify the full Phase 04 storage exit gate, and restore only earned advancement eligibility.

Architecture: additive SQL migrations enforce privileges, active-release visibility, validation and published-data immutability. SECURITY INVOKER admin RPCs perform atomic draft creation/loading and serialized publication. Python storage wrappers call those RPCs. Tests create a disposable database in the existing local PostgreSQL container and never reset the shared Supabase stack.

Stack: existing Python 3.13, PostgreSQL 17.6, vector 0.8.2 and installed Supabase CLI 2.117.0. No installs, model execution, dependency changes or institutional activation. Continue in the existing `feat/p04-supabase-rls` worktree.

## Decisions and access matrix

- Runtime: SELECT on institutional tables only; no writes or sequence access. Ingestion/evaluation runs are administrative, with neither runtime grants nor policies. All runtime tables use active-release/approved-parent predicates. Membership predicates must not depend back on their children, preventing recursive RLS.
- Document approval uses the Phase 01 vocabulary: `approval_state = 'approved'`, `verification_state = 'verified'`, `content_review_state = 'reviewed'`. Chunks must agree with that source/version/hash and have located source spans. Curricula/rules use their existing `authorized` states. These labels come from the trusted administrative source-governance workflow; this repair does not grant institutional authority to candidate artifacts.
- Draft creation records expected chunk/document/rule counts in one transaction. Activation rejects incomplete counts, missing approvals/spans/embeddings, mismatched hashes/configuration, non-unit vectors, invalid statuses and unbound rules before changing any release status/pointer.
- A transaction advisory lock serializes publication with writes to release memberships and referenced content. Published source/chunk/span/vector/configuration/entity/rule content and membership are immutable; exact unchanged upserts may succeed. New evidence/configurations require new identities. Revoked releases cannot be activated/rolled back. Runtime continues to use the active release; Phase 05 pinned requests remain future work.
- Atomic chunk/span loading replaces independent HTTP deletion/insertion; artifact parsing/validation precedes database writes. Conflicting immutable identities fail. Tests exercise the public Python methods as well as SQL roles.
- CLI-generated migration filenames were renumbered to `20261012010001` and `20261012010002` because Gemini's existing migration versions use future UTC timestamps relative to the current clock. Preserve the existing files/history; the new migrations must follow them numerically.
- Hosted execution is authorized by the owner's instruction to fix the audited deployment. Inspect/diff the hosted baseline first, repair matching historical migration entries without replaying their SQL, then apply verified additive changes. Preserve all data and keep the active pointer empty.

## Review focus

- Both runtime roles and inherited/default ACLs, including TRUNCATE and future tables.
- Approval/release policy dependencies without recursion or hidden-parent child leaks.
- Partial artifact imports, wrong source/hash/model/vector values and revoked targets.
- Concurrent activation/loading and mutation of historical evidence after rollback.
- Accidental shared-database test cleanup, missing hosted history and migration timestamp order.

## Task 1 — effective privileges (F1)

Files: `supabase/migrations/20261012010001_phase4_runtime_privileges.sql`, `tests/test_storage_security.py` and its isolated database helper.

- [x] Add a real-database regression asserting no runtime DML/TRUNCATE/REFERENCES/TRIGGER/MAINTAIN grants and no future default table privileges. Original migrations: 4 failing role subtests.
- [x] Revoke existing/default grants for the actual migration owners, grant only explicit runtime reads and admin operations, and verify GREEN: 2 tests passed under system Python.
- [x] Record evidence and commit this increment (identify the task commit in Git).

## Task 2 — policies and release lifecycle (F2–F4)

Files: `supabase/migrations/20261012010002_phase4_release_security.sql`, `backend/bintanong_storage/loader.py`, `release.py`, and storage tests.

- [x] Regress draft child/rule visibility, invalid activation, mutable published records, failed span replacement, idempotency and concurrent publication. Observe the demonstrated failures before implementing.
- [x] Add active/approved-parent policies, expected-count validation, atomic admin loading/creation RPCs and publication/mutation locks/guards.
- [x] Route Python operations through the new RPCs; validate artifacts before importing. Repair unsafe legacy fixture setup/cleanup and use synthetic approved fixtures only in isolated databases.
- [x] Verify all storage tests under both runtime roles plus exact retrieval, rollback and zero-duplicate reimport. Commit the verified increment.

## Task 3 — deployment and exit gate (F5)

Files: repository decisions/progress/checkpoint/handoff, plus a migration baseline verification/repair command if CLI connectivity requires a documented alternative.

- [x] Compare hosted/local schema and functions to the historical migration baseline. Record the original ACL drift, verify no active data, and repair history accurately.
- [x] Apply additive migrations locally and hosted without resetting databases; inspect effective ACLs, schema/functions/history and both advisors.
- [x] Request independent whole-change review, address important findings, run the complete isolated storage gate and phase ledger checks.
- [x] Preserve the original audit and historical completion claims. Add exact new commits/versions/digests/evidence and unresolved limits. Only mark Phase 04 complete if every required gate passes; keep Phase 05 preparation only.

Evidence lives under `C:/Coding-projects/bintanong_workspace/audit-evidence/p04-repair-20261012/`. Use standard-library unittest under system Python if pytest remains unavailable. Raw SQL outputs and synthetic temporary artifacts stay outside Git.

## Advisor follow-through

After 10001/10002 deployment, INFO-level advisor checks identified six original uncovered foreign keys and the two deliberate policy-free operational tables (no WARN/ERROR). Additive `20261012010003_phase4_advisor_hardening.sql` covers these keys and installs restrictive runtime-deny policies. Zero WARN/ERROR is the meaningful health gate; unused-index INFO on the empty corpus is documented, not suppressed by dropping required indexes. The new policy regression was observed failing before implementation.

Completion: commits `c48f404`, `6e762a5`, `c5beecd`; 31 storage tests passed; deployed catalogs/functions/triggers match; six versions recorded; runtime writes/admin EXECUTE zero; security clear, performance INFO only unused indexes. The [corrective handoff](phase-04-handoff.md) governs current status.
