---
artifact: phase-plan
phase: 5
status: in_progress
master: plans/master_implementation_plan_original_long.md
previous_handoff: plans/phase-04-handoff.md
---

# Phase 5 — Retrieval Plan

Originally prepared at `4244870`; corrected storage baseline `c5beecd`. Owner formally started Phase 05 on 12 October 2026 from `10bfd6f` in `feat/p05-retrieval-logic`. The complete Phase 04 corrective handoff governs eligibility.
Nothing here constitutes institutional policy approval or active production release.
Anything not run is marked NOT RUN.

## Goal and Context

Master section 10 (10.1 retrieval algorithm, 10.2 configuration, and evaluation):
Return relevant, authorized, source-linked context without depending on answer generation.

- Encoder convention: `aisingapore/SEA-LION-E5-Embedding-600M` using the pinned adapter's Retrieval instruction prompt (confirmed in the local model configuration). The earlier generic `query: ` wording is corrected to preserve Phase 03 compatibility.
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

- [x] Task 1: Retrieval request specification and query embedding pipeline (matching Retrieval instruction via `SeaLionEmbeddingAdapter`).
- [x] Task 2: Pinned release and scope-filtered vector similarity search via `match_chunks`.
- [x] Task 3: Context window budgeting, span deduplication, and adjacent section inclusion.
- [ ] Task 4: Relevance and coverage threshold calibration (handling insufficient evidence).
- [x] Task 5: Structured retrieval response formatter with source locators, scores, and configuration fingerprints.
- [ ] Task 6: Phase 5 evaluation, benchmark verification, and final handoff.

## Implementation interfaces and verification

Spec: master section 10; implement inline using the executing-plans skill. Existing isolated worktree is retained; no installs, lock changes, shared resets or institutional activation.

1. Create `backend/bintanong_retrieval/query.py` and `types.py`: validated `RetrievalRequest(query, release_id, scope, entity_hints, document_version_ids)`; `RetrievalSettings(top_k, context_budget, min_similarity)`; strict local query encoder wrapping the pinned adapter. Test missing models, configuration mismatch, empty/overlong queries and invalid vectors in `tests/test_retrieval_query.py`. Hash existing external assets before model work; no network fallback or synthetic runtime vectors.
2. Add a CLI-generated additive migration defining `retrieve_context` as SECURITY INVOKER, STABLE, with explicit runtime EXECUTE. One database statement verifies the pinned active release/configuration and returns ranked chunks, version/span locators and required neighbors. Runtime history stays hidden; stale pins return `release_changed` and no evidence. Scope is supplied verified metadata, unknown scope stays empty; exact entities use `type_fields.entity_hints`. Test real anon/authenticated roles, wrong scope/edition, stale release, matching fingerprints, citation integrity and deterministic ranking in `tests/test_retrieval_database.py` against disposable databases only.
3. Create `context.py`: count the actual serialized context using an injected exact tokenizer, deduplicate shared span identities, include explicitly required neighbors from `type_fields.required_neighbor_chunk_ids` atomically with their parent. Omit incomplete groups; never silently truncate clauses. Test overlap, textless tables, oversized groups and missing neighbors in `tests/test_retrieval_context.py`.
4. Create `engine.py`: always use runtime RPC, check encoder fingerprints against active set before embedding and again inside search, expose insufficient evidence, ambiguity, conflicts and gaps. Canonical hints narrow exact matches; unknown hints yield no evidence rather than semantic substitution. Test pipeline failures, stale metadata and budget coverage in `tests/test_retrieval_engine.py`.
5. Create `cli.py` and module entrypoint: internal debug command returns versioned structured JSON containing source identity, scores, configuration fingerprints, serialized context/token count and gap reasons. No API deployment or answer generation. Unit-test command parsing/output without reading private inputs.
6. Add retrieval evaluation functions/explicit synthetic multilingual development fixtures and report under `evaluation/` and `plans/`. Compare k=3/5/8, Precision@k and Recall@k by language/category; calibration must use development cases only. Existing human-approved policy cases remain required for the formal exit gate; synthetic fixtures do not approve institutional cases.

For each task: write focused tests, observe expected RED, implement minimal change, run GREEN, update checkpoint/progress and explicitly stage a cohesive commit. System Python 3.13.7 lacks pytest and model dependencies: use unittest for the unittest suites, without installing anything. Raw logs and generated evidence stay in `C:/Coding-projects/bintanong_workspace/audit-evidence/p05-20261012/`.

## Review focus

- Publication during embedding: stale release fails closed; never return mixed editions.
- Wrong encoder fingerprint or unavailable local model: reject before search; no mock runtime embeddings.
- Unknown curriculum/entity and conflicting editions: expose ambiguity/conflict without choosing policy authority by score.
- Overlapping and required adjacent clauses: preserve cited provenance and whole-group budget integrity.
- Synthetic evaluation and missing approved development cases: report separately and keep formal advancement gated.

## Exit gate

Run all retrieval/storage/embedding unittest suites and phase-state tests; verify migration in disposable databases and effective RPC ACL/RLS. Run development-only evaluation by language/category with every returned span resolving to its source/version/page/locator. Record exact versions and external model/file digests. Formal completion additionally requires approved labeled development cases recovering expected evidence and detecting unsupported cases without answer generation. If those cases are unavailable, retain Phase 05 active with a blocked handoff/recovery condition; do not create Phase 06.
