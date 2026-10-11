---
artifact: phase-plan
phase: 3
status: complete
master: plans/master_implementation_plan_original_long.md
previous_handoff: plans/phase-02-handoff.md
---

# Phase 3 — Embedding Generation Plan

Base commit `9f2b1d9`. Implementation started per owner authorization.
Nothing here constitutes institutional approval or vector persistence.
Anything not run is marked NOT RUN.

## Goal and Context

Master section 8 (8.1 embedding adapter, 8.2 verification and re-embedding rules):
Create reusable vector artifacts from candidate chunks, independent of persistence and retrieval.
Operate strictly outside Supabase / database writes.

- Pinned encoder: `aisingapore/SEA-LION-E5-Embedding-600M` (1,024 dimensions, 512-token context limit, L2 normalized).
- Interfaces: Distinct `encode_documents()` (with document/passage prompt prefix) and `encode_queries()` (with query prompt prefix).
- Contracts consumed: `backend/bintanong_contracts.embedding.EmbeddingRecord`, `TokenCount`, `check_embedding_matches_chunk`, and `backend/bintanong_contracts.source.Chunk`.
- Batch and resumption: Memory-safe batching with serializable progress checkpointing to resume without re-embedding identical chunks.
- Fingerprinting: Comprehensive configuration fingerprints (model revision, prompt convention, tokenizer, normalization, chunker version).

## Global Constraints

- No database writes, migrations, or Supabase vector storage in Phase 3 (storage belongs strictly to Phase 4).
- No Bintu-1 tokenizer sharing; SEA-LION tokenizer and vocabulary remain fully isolated.
- Respect pinned dependency and worktree rules. System Python 3.13; pytest with `-p no:cacheprovider --basetemp "$S\bt_NAME"`.
- Clean working tree and explicit staging; no attribution lines in commits.

## Task Checklist

- [x] Task 1: SEA-LION E5 prompt convention verification and adapter contract design (`encode_documents` and `encode_queries`).
- [x] Task 2: Pinned model revision and configuration fingerprint generator (model revision, tokenizer hash, preprocessing hash, prompt hash).
- [x] Task 3: In-memory and batch document encoder with exact token counting conforming to `EmbeddingRecord` and `check_embedding_matches_chunk`.
- [x] Task 4: Resumable batch embedding runner with chunk cache and interruption recovery.
- [x] Task 5: Offline similarity verification suite (paired English, Tagalog, and Taglish test queries vs candidate chunks + hard negatives).
- [x] Task 6: Phase 3 exit gate verification, validation report, checkpoint supersession, and handoff preparation.

## Interfaces and Output Artifacts

- Python module: `backend/bintanong_embedding/adapter.py` providing `SeaLionEmbeddingAdapter`.
- Batch CLI: `bintanong_tools.embed` or `backend/bintanong_embedding/batch.py`.
- Output artifacts: JSONL/Parquet/Numpy vector artifacts alongside manifest `embedding_manifest.json`.

## Verification and Exit Gate

- The candidate chunk corpus can be embedded, interrupted, resumed, and validated without calling Supabase.
- Vectors satisfy 1,024 dimensions, non-zero finite values, and unit norm (`L2_TOLERANCE = 1e-6`).
- Offline similarity demonstrates appropriate clustering for English, Tagalog, and Taglish test pairs against candidate chunks with clear separation from hard negatives.
