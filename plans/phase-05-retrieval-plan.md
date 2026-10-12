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

## Candidate recovery checkpoint — 12 October 2026

Software delivery and fresh review are verified at ddf9b83;91 relevant tests passed. Task4 has only synthetic development calibration; Task6 formal approved-case/model exit remains blocked. See phase-05-handoff.md for exact recovery conditions, versions/digests and evidence. Shared migration unapplied, default policy uncalibrated, no institutional release activation. The active Phase05 checkpoint is blocked and retained rather than superseded; plan remains in_progress so phase_state.py continues selecting Phase05 (blocked plans are not active in that inspector). Phase06 cannot begin.

## Owner-resumed source-backed development exam

The owner requested a small practice exam with correct answers/sources and TDD tests. [Practice-exam plan](2026-10-12-phase05-practice-exam-plan.md) implemented at2a497c4; [delivery/verification report](phase-05-practice-exam-report.md) identifies external12-case question/key/packet files, fresh source hashes,21 new TDD tests,74 relevant passing regressions and the Docker-unavailable DB rerun. The set remains candidate pending independent source/answer review and production span mapping; real-model retrieval observations are NOT RUN. Tasks4/6 formal gates remain open, no institutional activation or Phase06 advancement.

## Latest original-corpus recovery

Owner-approved27-case/nine-college set and isolated dependencies/five Docling assets now executed.39 original candidate bundles verified;33audit failures withhold chunks,6warnings emit336. Actual source geometry near27/28targets; only3regions/cases have available emitted chunks.336strict real-model document vectors and27query candidate cosine diagnostics recorded without gold-derived corpus, threshold tuning, approved runtime replay or LLM answers.86c2720 term-index serialization repair verified RED/GREEN; full4906tests/107subtests pass and final reviewer clear. [Execution report](phase-05-real-retrieval-readiness.md) records exact source/model/cache locations, raw manifest, versions and old-process cohort limits. Tasks4/6 remain open on extraction and independently approved source/field/answer labels before approved-release calibration and reviewed shared migration. Earlier unavailable-environment/missing-asset notes above are historical; do not repeat completed setup or all-source conversions.

## Resumed extraction increment and owner review

VerifiedTDD code280a287 removes repeatedsource-row projections; latestcorpus32errors/7warnings/390chunks/vectors,other38source resultsunchanged. Full4912tests/107subtests pass371.98s; ownerreviewguide and27decision rows are ready at C:/Coding-projects/bintanong_workspace/audit-evidence/phase-05-owner-review-20261012. Ownerconfirms reviewnotperformed, allsource/answer/applicability labelsremainpending. Tasks4/6 stayopen. See readinessreport/checkpoint forverified commands,digests andspecific nextsteps.

## Policy-source recovery after owner organization request

The owner supplied Charter2025/fourth edition and handbook2021 and authorized
filesystem organization, preserving prospectuses and deferring their review.
Two pending byte-derived source records now exist. Actual-policy governance,
conversion/span verification and reviewed development retrieval cases remainopen.
Reuse Phase1/2 software and existing offline assets; do not repeat completed code
or promote the prospectus-only diagnostics into a policy-retrieval benchmark.
See plans/2026-10-12-policy-source-recovery-plan.md and the dated next-CLI handoff.

## Current policy evidence recovery — 13 October 2026

Both original policy candidates captured; saved-byte handbook recovery now has
4272chunks after1546exact original-list provenance repairs. Final code d33340e
passes4953tests/107subtests386.83s; source/evidence invariance checked.10text/
18table refusals and critical grading/source-review gates remain; Charter427chunks
unchanged.26original grade readings are separate human-pending correction
proposals. Follow2026-10-13-phase05-list-recovery-handoff.md. Tasks4/6remain open
until approved policy development retrieval/calibration exists; noPhase06.
