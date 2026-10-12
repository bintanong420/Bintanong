---
artifact: phase-plan
phase: 5
status: ready
preparation_only: true
master: plans/master_implementation_plan_original_long.md
previous_handoff: plans/phase-04-handoff.md
---

# Phase 5 — Retrieval Plan

Originally prepared at `4244870`; corrected storage baseline `c5beecd`. Prepared plan awaiting owner review/formal start. The complete Phase 04 corrective handoff governs eligibility.
Nothing here constitutes institutional policy approval or active production release.
Anything not run is marked NOT RUN.

## Goal and Context

Master section 10 (10.1 retrieval algorithm, 10.2 configuration, and evaluation):
Return relevant, authorized, source-linked context without depending on answer generation.

- Encoder convention: `aisingapore/SEA-LION-E5-Embedding-600M` using `query: ` prefix.
- Vector backend: Supabase PostgreSQL with pgvector cosine distance `<=>` over active release chunks.
- Authorized scope: filter by verified curriculum/scope; unknown scope remains unknown without fabrication.
- Candidate ranking: ascending cosine distance (`1 - distance` similarity) for top-k candidates (`k = 3, 5, 8`).
- Evidence synthesis: deduplicate overlapping spans, honor context token budget, return insufficient evidence when appropriate.

## Global Constraints

- **Scope Integrity**: Unknown scope remains unknown; never fabricate a college or curriculum filter.
- **Release Binding**: Queries must target the active release or a pinned validated release ID.
- **Context Budget**: Respect bounded token budgets; do not overfill context.
- **Privacy & Role Separation**: Retrieval runs strictly under runtime role (`anon`) with RLS enforcement.

Corrected storage prerequisite: runtime RLS currently exposes only the active approved release. Superseded evidence is immutable for validated administrative rollback. Request-pinned access across publication requires an explicitly authorized Phase 05 interface; do not make history globally readable by relaxing RLS. Verify external model asset digests before model work; Phase 04 did not execute/hash weights.

## Task Checklist

- [ ] Task 1: Retrieval request specification and query embedding pipeline (`query: ` prefix via `SeaLionEmbeddingAdapter`).
- [ ] Task 2: Pinned release and scope-filtered vector similarity search via `match_chunks`.
- [ ] Task 3: Context window budgeting, span deduplication, and adjacent section inclusion.
- [ ] Task 4: Relevance and coverage threshold calibration (handling insufficient evidence).
- [ ] Task 5: Structured retrieval response formatter with source locators, scores, and configuration fingerprints.
- [ ] Task 6: Phase 5 evaluation, benchmark verification, and final handoff.
