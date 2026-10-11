---
artifact: phase-plan
phase: 4
status: in_progress
master: plans/master_implementation_plan_original_long.md
previous_handoff: plans/phase-03-handoff.md
---

# Phase 4 — Supabase Vector and Relational Storage Plan

Reopened for security verification on 12 October 2026. The original task checklist below records delivered work; Tasks 5/6 and the publication invariants require recovery under [the independent review](phase-04-security-review-2026-10-12.md). The current checkpoint and blocked handoff govern advancement.

Formally active implementation plan.
Nothing here constitutes institutional policy approval or active production release.
Anything not run is marked NOT RUN.

## Goal and Context

Master section 9 (9.1 proposed logical schema, 9.2 storage implementation):
Persist the reviewed corpus and candidate structured knowledge into Supabase PostgreSQL with version control, vector embeddings (`vector(1024)`), access control (RLS), and atomic release mechanisms.

- Pinned vector extension: `pgvector 0.8.2` on PostgreSQL 17.6.
- Database targets: Local Supabase instance (`postgresql://postgres:postgres@127.0.0.1:54322/postgres`) and hosted project `Project_Bintanong` (`jyrudbiuajahsucsorco`).
- Source inputs: Candidate chunk artifacts from Phase 2, `embeddings.jsonl`, and `embedding_manifest.json` from Phase 3.
- Access model: Role separation between migration/loader write credentials and runtime read-only application roles.

## Global Constraints

- **Privacy Constraint**: No persistent `student_grades`, transcripts, personal enrollment records, private-file embeddings, or personal chat transcripts in this schema.
- **Relational Integrity**: Foreign keys, uniqueness constraints, and explicit release-membership bindings.
- **Atomic Release Publish**: Incomplete imports must remain invisible to runtime queries; staged or superseded chunks cannot leak into current retrieval.
- **RLS & Security**: Runtime read role cannot mutate institutional knowledge. Unrestricted service role keys must never be exposed to clients.
- **Tooling Workflow**: Utilize Supabase CLI (`npx supabase migration ...`, `npx supabase db push`) and Supabase MCP for schema inspection, migration execution, and advisor audits.

## Task Checklist

- [x] Task 1: Logical schema & migration design (`documents`, `document_versions`, `source_spans`, `chunks`, `embedding_sets`, `chunk_embeddings`, `knowledge_releases`, `active_release`).
- [x] Task 2: Supabase SQL migration files and local database application with `pgvector 0.8.2`.
- [x] Task 3: Idempotent batch loader importing Phase 3 artifacts (`embeddings.jsonl` and manifest) into Supabase with duplicate detection.
- [x] Task 4: Atomic release publication, activation, and rollback mechanisms.
- [x] Task 5: Role-based access control (RLS), runtime read-only policy verification, and security advisor audits via Supabase MCP.
- [x] Task 6: Phase 4 exit gate verification, idempotency tests, and handoff documentation.

## Proposed Relational Schema

| Table / Group | Stored Information |
| :--- | :--- |
| `documents`, `document_versions` | Identity, issuer, scope, verification status, version ID, content hash, source path. |
| `source_spans`, `chunks` | Source-linked text, locators (page/box), hierarchy path, and chunker metadata. |
| `embedding_sets`, `chunk_embeddings` | Encoding fingerprint, model revision, and `vector(1024)` cosine-normalized vectors. |
| `knowledge_releases`, release memberships | Specific document versions, chunk sets, and embedding sets bound into an immutable release. |
| `active_release` | Singleton pointer to currently active knowledge release; prior releases preserved for rollback. |

## Verification and Exit Gate

- **Idempotency**: Running the bulk loader a second time produces 0 duplicate records and 0 corrupted references.
- **Release Isolation**: Chunks and embeddings belonging to inactive or draft releases cannot be retrieved by runtime queries.
- **Permission Enforcement**: The runtime read role cannot execute `INSERT`, `UPDATE`, or `DELETE` on institutional knowledge tables.
- **Advisor & Schema Health**: Supabase security and performance advisors return clean audit results.
