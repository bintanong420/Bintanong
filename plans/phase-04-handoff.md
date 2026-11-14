---
artifact: phase-handoff
phase: 4
status: complete
plan: plans/phase-04-supabase-storage-plan.md
final_commit: c5beecd
next_phase: 5
completed_at: 2026-10-12T03:31:31+08:00
---

# Phase 4 Final Handoff: Supabase Vector and Relational Storage

**Current corrective status: COMPLETE at `c5beecd`.** The corrective evidence below governs current status. Phase 05 is eligible for formal start but remains preparation only. Institutional tables and active pointers remain empty.

## Corrective exit gate — 12 October 2026

### Changes and reviewed commits

- `7c0ed85`: independent audit and reopened exit gate (audit baseline `8f53b72`). Findings remain in [the historical review](phase-04-security-review-2026-10-12.md).
- `c48f404`: effective/default runtime privileges revoked; explicit institutional SELECT grants; local automatic exposure disabled.
- `6e762a5`: acyclic active/approved-parent RLS; expected counts and approval/provenance/vector validation; serialized publication; immutable published content; atomic import/release creation; isolated tests.
- `c5beecd`: restrictive runtime denials on operational tables and six covering foreign-key indexes.
- Independent review identified dictionary hash/location, corpus identity, source-text default and nullable-identity gaps. Every finding was corrected; final read-only review of `c5beecd` reported no blockers. `final_commit` identifies verified code; the following documentation closure commit is discoverable in Git.

### Verification commands and results

| Verification | Result |
| --- | --- |
| `python -m unittest discover -s tests -p 'test_storage_*.py' -v` | 31 passed, 78.153s, exit 0; migration set through 10003 |
| `python -m unittest discover -s tests -p 'test_embedding_*.py' -v` | 12 passed, 0.152s, exit 0; existing Starlette/httpx deprecation warning |
| `python -m unittest discover -s .agents/skills/bintanong-phase-handoff/tests -p 'test_phase_state.py' -v` | 19 passed, 17.533s, exit 0 |
| CLI `migration repair 20260920000000 20261012000000 20261012010000 --status applied --project-ref jyrudbiuajahsucsorco` | Missing history recorded only after verifying existing objects; no historical DDL replay |
| CLI `db push --skip-vault --local --yes` and `db push --skip-vault --project-ref jyrudbiuajahsucsorco --yes` | Additive 10001–10003 applied; no reset, seeds, custom roles or vault updates |
| Final local/hosted `db push --dry-run --skip-vault ...` | Up to date, no pending migrations; all six versions recorded |
| Hosted MCP/local psql catalog section digests | Exact parity: 150 columns, 71 constraints, 47 indexes, 19 policies/RLS flags, 8 public functions, 9 private functions, 34 triggers; function line endings normalized |
| Live effective privileges | Both roles: 17 SELECT tables, zero mutations including TRUNCATE/MAINTAIN, zero admin EXECUTE; no public CREATE/private USAGE; no SECURITY DEFINER application functions |
| Local runtime HTTP smoke; hosted actual-role SELECT transactions | Empty institutional/pointer reads; local activation/loading RPCs and operational reads denied, HTTP 401/SQLSTATE 42501 |
| Hosted security/performance MCP; local `db advisors --local --type all --level info --fail-on warn` | Security: zero lints. Zero WARN/ERROR. Only unused-index INFO: 24 hosted/18 local at recorded check |
| Closure `phase_state.py validate`, `can-advance` | Both passed: no active phase, complete Phase 04 handoff, Phase 05 eligible |

Tests cover both actual runtime roles, draft/unreleased child hiding, incomplete/unapproved/revoked publication, content/source/location integrity, immutable membership/configuration/evidence, exact cosine ranking, sequential/concurrent publication, rollback, post-lock writer rejection, stronger-isolation rejection, failed-batch rollback, idempotency/span UUID preservation, and corpus-bound embedding identities. Tests create/drop only uniquely named disposable databases; no shared active-pointer cleanup remains.

Original policy/lifecycle regressions had 29 failing cases; privilege regressions had four failing role subtests. Additional review cases and explicit operational denials were reproduced before fixing. An isolation-test cleanup bug left orphan fixture chunks in its own disposable database, causing later fixture conflicts; it was corrected and the whole suite rerun. No shared data were affected.

Raw evidence remains outside Git at `C:/Coding-projects/bintanong_workspace/audit-evidence/p04-repair-20261012/`: `final-storage-tests-10003.out`, `local-final-catalog.json`, `hosted-final-verification.json`, `local-final-advisors.json`, historical-baseline catalogs and numbered SQL/output files. No disposable test databases remain. Local/hosted documents, chunks, embeddings, releases and active pointers remain zero; no institutional release was activated.

### Versions and digests

Python 3.13.7; httpx 0.28.1; pydantic 2.13.5; installed CLI 2.117.0 (2.120.0 reported available; existing executable retained under the no-install instruction). Local PostgreSQL 17.6; hosted 17.6.1.166; vector 0.8.2; 1024 dimensions, l2 tolerance 1e-6. No dependencies, locks, images or model assets were downloaded/changed.

Working-file SHA-256 values; original migrations preserved:

| File | SHA-256 |
| --- | --- |
| `20260920000000_enable_vector.sql` | `4a915b03677970e0043876db380d5d00c44687e45c94a57da8ce51212c649d94` |
| `20261012000000_phase4_knowledge_schema.sql` | `3c855a7d814777c1d5c530f14a5ed5e3e2320f95bd495ec844fdefc05c56d8a4` |
| `20261012010000_phase4_rls_policies.sql` | `2b70ba63a08f0beb279e41fae337d7ba544dec8d9fa71e91df4f52ca726072b4` |
| `20261012010001_phase4_runtime_privileges.sql` | `76a1dfee7e5004f0ccc6808b65089784a337e541cf5d651dcda9b9c92e09b484` |
| `20261012010002_phase4_release_security.sql` | `58b12d0e8fc33c41c7d956d12a2741cd35996e15a0d145cc55fd6ae1aa76dfde` |
| `20261012010003_phase4_advisor_hardening.sql` | `998a3c688684609a21b8e613bbdb609603c904825a8f4b7ab8b07529a465c88f` |
| `backend/bintanong_storage/loader.py` | `ad22a179c162aa34ec8c42f01fdad40af327cd1821c78849620b09e8de1034c9` |
| `backend/bintanong_storage/release.py` | `c643186374f3febfae9efadd180e36b4ec499cfd1d75836374641b23ed35d212` |

Model root remains `C:/Coding-projects/MODELS`. Existing encoder configuration names `aisingapore/SEA-LION-E5-Embedding-600M` at revision `df5b1c55623eeb5ef09ce3f3c50e24e2db433d7d1bbcccf76d2f01ba212df5f1`. Actual model-file hashing/execution NOT RUN for this database repair; the earlier revision-shaped weights digest is not fresh file evidence. Verify external asset digests before Phase 05 model work.

### Decisions and remaining limits

- Documents require approved/verified/reviewed governance states; curricula/rules require authorized states. Trusted administration supplies those states. Synthetic labels in isolated tests confer no institutional approval on candidate artifacts.
- Active-release RLS is the current runtime interface. Superseded publications remain immutable for validated rollback. Request-pinned retrieval spanning activation requires the Phase 05 authorized interface; do not loosen global RLS to expose history.
- Import/release creation is transactional. Unchanged reimports preserve span UUIDs; identity/configuration conflicts fail. Automatic embedding-set identity includes configuration and the full sorted corpus/vector content. Manifest-only loading requires an explicit set ID.
- `span_order` preserves printed-source agreement. Textless table locators are supported; retrieval falls back to table text. Initial legacy ordering uses created_at/UUID until a reviewed draft reimport establishes order. Both audited targets had no legacy evidence rows.
- Publication/mutation writes require READ COMMITTED (READ UNCOMMITTED behaves equivalently in PostgreSQL). REPEATABLE READ/SERIALIZABLE are rejected because old snapshots could defeat advisory-lock-only protection. PostgREST uses supported isolation.
- New application objects are postgres-owned, with closed table/sequence/function defaults. Hosted platform-managed `supabase_admin` defaults retain platform grants; postgres cannot alter that protected role's defaults. Continue application migrations under audited postgres ownership and explicit ACLs. Managed-role/manual creation requires fresh effective-privilege review; it grants no access to any current application object.
- Advisor health means zero WARN/ERROR and zero security lints. [Unused-index INFO](https://supabase.com/docs/guides/database/database-linter?lint=0005_unused_index) is expected on empty corpora; required indexes were retained. Missing-FK and policy-free operational notices were resolved by 10003.
- No actual-corpus approval/load measurements, hosted synthetic activation, API deployment or model-weight execution are claimed. HTTP construction uses MockTransport; integration tests exercise real SQL roles/RPCs. The shared stack was not reset/restarted.

### Phase 05 prerequisites

Review the corrected storage interface and prepared Phase 05 plan before formal start. Implement matching query configuration, scope/entity filters, request-pinned authorized release access, source-linked results and labeled retrieval evaluation. Keep source/rule candidates inactive until their applicable approvals. Phase 05 remains `ready`, `preparation_only: true`; no Phase 05 implementation occurred.

## Preserved historical handoff and reopening narrative

The following is the original `4244870` completion claim and subsequent audit record. Its commits/dates/results are historical; corrective evidence above governs current status.

**Corrective audit, 12 October 2026: BLOCKED.** [Independent verification](phase-04-security-review-2026-10-12.md) invalidated the read-only privilege, authorized-release and immutable-publication assertions below. They are preserved as the original completion narrative, not current verified guarantees. Phase 05 remains preparation only. `final_commit` and `completed_at` record the original handoff baseline; the audit baseline is `8f53b72`.

Nothing here constitutes institutional policy approval or active production release.

## 1. Summary of Accomplishment

Phase 4 establishes the relational and pgvector knowledge storage architecture in Supabase PostgreSQL, persisting the candidate corpus, structured academic curricula, policy rules, and vector embeddings (`vector(1024)`). The implementation enforces strict Row Level Security (RLS) and singleton-pointer active release isolation, guaranteeing that staged, draft, or superseded chunks never leak into runtime student retrieval and runtime client roles cannot mutate institutional knowledge.

## 2. Exit-Gate Evidence

- **Relational & pgvector Schema (`20261012000000_phase4_knowledge_schema.sql`)**:
  - Pinned `pgvector 0.8.2` on PostgreSQL 17.6 in schema `extensions`.
  - Created 19 relational knowledge and operational tables: `documents`, `document_versions`, `chunks`, `source_spans`, `embedding_sets`, `chunk_embeddings`, `programs`, `curriculum_versions`, `courses`, `course_aliases`, `policy_rules`, `rule_source_spans`, `knowledge_releases`, `release_document_versions`, `release_chunks`, `release_rules`, `active_release`, `ingestion_runs`, `evaluation_runs`.
  - Privacy constraint verified: 0 tables or columns for persistent student grades, transcripts, enrollment records, private-file embeddings, or user chat logs.
- **Role-Based Access Control and RLS (`20261012010000_phase4_rls_policies.sql`)**:
  - RLS enabled on all 19 public tables.
  - Granted `SELECT` only to `anon` and `authenticated` runtime roles; write mutation (`INSERT`, `UPDATE`, `DELETE`) blocked by permission checks and RLS policy absence.
  - Release isolation: runtime `chunks`, `chunk_embeddings`, and `source_spans` SELECT queries dynamically resolve only through the `active_release` singleton.
  - RPC functions with explicit `search_path = public, extensions`: `match_chunks` (exact cosine search), `activate_knowledge_release`, and `rollback_knowledge_release` (restricted to `service_role`).
- **Idempotent Batch Loader (`BatchKnowledgeLoader`)**:
  - Implemented in `backend/bintanong_storage/loader.py`.
  - Tested in `tests/test_storage_loader_idempotency.py`: running the loader a second time with identical data produces 0 duplicate records and 0 corrupted references.
- **Atomic Release Manager (`ReleaseManager`)**:
  - Implemented in `backend/bintanong_storage/release.py`.
  - Tested in `tests/test_storage_release_isolation.py`: verified draft release chunks are invisible to runtime queries, activation promotes target release and supersedes previous releases atomically, rollback restores prior release visibility, and runtime roles cannot execute release mutation.
- **Exact Vector Cosine Search (`KnowledgeRetriever`)**:
  - Implemented in `backend/bintanong_storage/retrieval.py` using `<=>` cosine distance.
  - Tested in `tests/test_storage_vector_retrieval.py`: verified ranking accuracy and exclusion of unreleased chunks and sub-threshold candidates.
- **Supabase Security & Performance Advisors**:
  - `npx supabase db advisors` executed cleanly with 0 security or performance issues.
- **Verification Suites**:
  - 8 storage unit & integration tests passing (exit 0) in `tests/test_storage_*.py`.
  - 10 embedding suite unit tests passing (exit 0) in `tests/test_embedding_*.py`.
  - 19 phase state tests passing (exit 0) in `.agents/skills/bintanong-phase-handoff/tests/test_phase_state.py`.
- **MCP & Infrastructure Integration**:
  - GitHub MCP (`github-mcp-server`) verified against remote repository `bintanong420/Bintanong` (branches, commits, PR status).
  - Supabase CLI v2.117.0 and local stack operational on ports 54321 / 54322.

## 3. Commit Ledger and Baseline

- **`3b33c3f`**: `docs(plans): formally initialize Phase 4 plan and checkpoint`
- **`5f8af9c`**: `feat(db): add Phase 4 knowledge schema, pgvector storage, and RLS migrations`
- **`2e48670`**: `feat(storage): implement idempotent loader, release manager, and vector retrieval`
- **`4244870`**: `feat(storage): add CLI for storage management and mark Phase 4 tasks complete`
- **Branch**: `feat/p04-supabase-rls` at base `03adccc`.

## 4. Versions, Digests, and Locations

- **Database Engine**: PostgreSQL 17.6 with pgvector 0.8.2
- **Vector Dimension**: 1,024 (`extensions.vector(1024)`)
- **Distance Operator**: Cosine distance `<=>` (similarity `1 - distance`)
- **Local DB Endpoint**: `postgresql://postgres:postgres@127.0.0.1:54322/postgres`
- **Local API Endpoint**: `http://127.0.0.1:54321/rest/v1`
- **Remote Project Ref**: `jyrudbiuajahsucsorco` (`Project_Bintanong`, region `ap-southeast-1`)
- **Model Storage Root**: `C:\Coding-projects\MODELS` (`MODELS_DIR=C:/Coding-projects/MODELS`)
- **Encoder Model**: `aisingapore/SEA-LION-E5-Embedding-600M` (Revision `df5b1c55623eeb5ef09ce3f3c50e24e2db433d7d1bbcccf76d2f01ba212df5f1`)

## 5. Deviations, Rulings, and Unresolved Risks

- **Reference Exact Search**: In strict accordance with Master Plan Section 9.2, exact cosine search (`<=>`) is implemented as the reference baseline. HNSW indexing is deferred to later phases when corpus size justifies approximate search.
- **Role Isolation**: Runtime clients (`anon`, `authenticated`) have zero write permissions in PostgreSQL. Administrative operations (migrations, loaders, release activations) require `service_role`.
- **Privacy Enforcement**: No private student data or chat transcripts are stored in the database.

## 6. Next-Phase Prerequisites (Phase 5)

Advancement to Phase 5 (Retrieval):
- Implement query embedding integration using `SeaLionEmbeddingAdapter` with query prefix `query: `.
- Implement retrieval algorithm per Master Plan Section 10: query text, canonical entity hints, authorized scope, top-k ranking (`k = 3, 5, 8`), and context budget management.
- Deduplicate overlapping evidence and calibrate relevance/coverage thresholds.
