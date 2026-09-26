# Jsonifier Integration Plan — Phase 2 (Data Ingestion & Chunking)

**Status:** Draft — waiting for Codex-side code stabilization before execution.
**Prepared:** 26 September 2026.
**Depends on:** Phase 0 (complete), Phase 1 (source governance/contracts — not yet started).
**Scope:** Adapt `bintanong_prospectus_jsonifier.py` from a standalone CLI tool into a callable module within the Bintanong backend, aligned with the Master Plan §7 (Phase 2).

> [!IMPORTANT]
> This plan does NOT touch the jsonifier's parsing logic, evidence-gating, or Docling integration.
> Those are battle-tested with regression suites and should remain stable.
> The work here is strictly integration plumbing.

---

## 1. Current State

### What exists

| Component | Location | State |
|---|---|---|
| Prospectus jsonifier (6,229 lines) | `backend/bintanong_tools/bintanong_jsonifer_prolog/bintanong_prospectus_jsonifier.py` | Standalone CLI, actively refined with Codex |
| Generic Docling ingest stub | `backend/bintanong_tools/ingest.py` | Thin Typer wrapper, 78 lines |
| Backend project config | `backend/pyproject.toml` | `tools` extra includes `docling==2.129.0`, `typer`, `reportlab` |
| Phase 0 container scaffold | `compose.yaml` | `ingest` service runs via `--profile tools` |
| Master plan Phase 2 spec | `plans/master_implementation_plan_original_long.md` §7 (lines 272–306) | Requirements defined, not implemented |

### What the jsonifier already produces

The `build_payload()` function (line ~4600) returns a dict containing:

- `courses[]` — parsed course records with provenance, prerequisites, units, year/semester
- `prolog.clauses[]` — ready-to-write Prolog knowledge base facts and rules
- `prolog.relations.prerequisites[]` / `standing_requirements[]` — structured prerequisite graph
- `rag.semantic_chunks[]` + `rag.hierarchical_chunks[]` — RAG-ready JSONL chunks
- `elective_tracks[]` — elective pool linkages
- `audit` — error/warning status, promotion gate, validation evidence
- `evidence` — source provenance (table count, cell count, structural tokens)
- `quality_report` — summary metrics

### What `process_prospectus()` does beyond `build_payload()`

The orchestration function (line 4736) handles:

1. Path resolution and output naming
2. `load_document()` — PDF → Docling conversion or cached JSON loading
3. `build_payload()` — the actual parsing/extraction
4. File I/O: writes `_prospectus.json`, `_essentials.json`, `.pl`, `_rag.jsonl`, `_review.csv`
5. Audit summary printing

This file I/O coupling is the primary integration obstacle.

---

## 2. Integration Architecture

### Principle

Separate the **computation** (parsing, validation, output generation) from the **I/O** (file writes, CLI arguments, path conventions). The jsonifier becomes a library; the pipeline decides where outputs go.

```
┌─────────────────────────────────────────────────────────┐
│                    Current (CLI)                        │
│  CLI args → process_prospectus() → files on disk        │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                  Target (Module)                        │
│  Pipeline config → load_document() → build_payload()   │
│                         ↓                               │
│              ProspectusResult (typed dict)               │
│                   ↙        ↘                            │
│   Supabase writer    Prolog KB writer    File exporter  │
└─────────────────────────────────────────────────────────┘
```

The CLI remains functional for standalone use. The pipeline uses the same functions without the CLI wrapper.

---

## 3. Tasks

### Task 1: Add `__init__.py` to the jsonifier package

**Goal:** Make `bintanong_jsonifer_prolog` importable as a Python package.

**Work:**
- Create `backend/bintanong_tools/bintanong_jsonifer_prolog/__init__.py`
- Export the public API surface:
  - `load_document`
  - `build_payload`
  - `build_essentials`
  - `ProspectusEvidence` / `LoadedDocument` (the central IR type)
  - `NormalizedCell`
  - `run_self_tests`
  - `SCHEMA_VERSION`

**Does NOT change:** Any code in `bintanong_prospectus_jsonifier.py`.

**Verification:** `from bintanong_tools.bintanong_jsonifer_prolog import build_payload` succeeds from the backend root.

---

### Task 2: Extract configuration from hardcoded paths

**Goal:** Replace hardcoded path constants (`SOURCE_PDF_ROOT`, `DEFAULT_SEMANTIC_DOC`, `DEFAULT_TARGET_PDF`, output directory conventions) with injectable parameters.

**Work:**
- Identify all path constants at module scope (likely lines ~80–110 area and near `find_default_output_root()` at line 4860)
- Make `load_document()` and `build_payload()` accept explicit paths instead of falling back to module-level defaults
- The CLI (`main()`) continues to use the defaults — this is a backward-compatible change
- Environment variables (`PALSU_DOCLING_CELL_MATCHING`, `_PALSU_RELAUNCHED`) remain as-is for CLI mode; the module API passes config explicitly

**Verification:** `build_payload(document, source_path, semantic_doc_path=None)` works without any module-level path existing on disk.

> [!NOTE]
> This task should wait until the Codex refinement stabilizes. Changing function signatures on a moving target wastes effort.

---

### Task 3: Define `ProspectusResult` as a typed contract

**Goal:** Align the jsonifier's output with the Master Plan §6.2 shared contracts (`SourceSpan`, `Chunk`, `SourceDocumentVersion`).

**Work:**
- Define a `ProspectusResult` TypedDict (or Pydantic model, matching the Phase 1 contract decisions) that formalizes the `build_payload()` return shape
- Map the existing payload fields to the Phase 1 contract types:

| Payload field | Phase 1 contract |
|---|---|
| `source_path`, `metadata` | → `SourceDocumentVersion` |
| `courses[].provenance` | → `SourceSpan` |
| `rag.semantic_chunks[]` | → `Chunk` |
| `rag.hierarchical_chunks[]` | → `Chunk` |
| `prolog.clauses[]` | → Rule artifacts (Phase 1 will define the exact shape) |
| `audit` | → Ingestion run metadata |

**Depends on:** Phase 1 contract definitions. If Phase 1 hasn't defined the contract shapes yet, this task defines the jsonifier-side types first and adapts them when Phase 1 lands.

**Verification:** `ProspectusResult` can be instantiated from an existing `build_payload()` return value without data loss.

---

### Task 4: Wire into the `ingest` CLI/service

**Goal:** Replace or extend `backend/bintanong_tools/ingest.py` to use the jsonifier for prospectus documents.

**Work:**
- Add a `prospectus` subcommand to the existing Typer app in `ingest.py`:
  ```
  bintanong ingest prospectus --input <path> [--export-all] [--strict]
  ```
- This subcommand calls `load_document()` + `build_payload()` from the jsonifier module
- Output handling follows the pipeline convention (write to configured output directory or return structured data)
- The existing `parse` command in `ingest.py` remains for generic Docling parsing of non-prospectus documents

**Verification:** `docker compose --profile tools run --rm ingest prospectus --help` works and matches the Phase 0 command contract.

---

### Task 5: Docling dependency alignment

**Goal:** Ensure the jsonifier's Docling usage matches the containerized environment.

**Work:**
- Verify the jsonifier's `load_docling()` function (line 172) is compatible with `docling==2.129.0` as pinned in `pyproject.toml`
- Remove the `ensure_docling_env()` venv-relaunch mechanism (lines 128–143) for the module path — it's a CLI convenience that doesn't apply inside a Docker container
- The `_venv_python()` and subprocess relaunch remain available for standalone CLI use but are not called from the module API

**Verification:** `load_docling()` succeeds inside the `ingest` Docker container without triggering a subprocess relaunch.

---

### Task 6: Self-test integration

**Goal:** Make the jsonifier's regression suite runnable from `pytest`.

**Work:**
- Wrap `run_self_tests()` (line ~5800+) as a pytest test case in `tests/`
- The existing assertion-based checks already have clear pass/fail semantics
- Optionally expose as: `pytest tests/test_prospectus_jsonifier.py -v`

**Verification:** `docker compose --profile tools run --rm ingest pytest tests/test_prospectus_jsonifier.py` passes.

---

## 4. What this plan does NOT include

These are explicitly **FUTURE** scope:

| Item | Classification | Reason |
|---|---|---|
| FastAPI endpoint for on-demand prospectus ingestion | FUTURE | Ingestion is a batch/admin operation, not a student-request path |
| Async ingestion with progress reporting | FUTURE | No concurrent ingestion requirement exists yet |
| Database writes (Supabase/pgvector) | Phase 4 | The Master Plan §9 separates storage from ingestion |
| Embedding generation from chunks | Phase 3 | The Master Plan §8 separates embedding from chunking |
| Non-prospectus document ingestion | Phase 2 (parallel track) | Handbook, Charter, USG/CSG docs need their own parsers |
| Semantic repair provider integration | EXTENSION | The jsonifier supports it but no provider is implemented |

---

## 5. Execution sequence

```
Phase 1 (contracts) must complete first
         ↓
Task 1: __init__.py (trivial, can do immediately)
         ↓
Task 2: Config extraction (after Codex stabilization)
         ↓
Task 3: Typed contracts (after Phase 1 or in parallel with initial types)
         ↓
Task 4: Ingest CLI wiring (after Tasks 1-2)
         ↓
Task 5: Docling alignment (can run in parallel with Task 4)
         ↓
Task 6: Test integration (after Tasks 1-2)
```

Tasks 1 and 5 can start before Phase 1 completes.
Tasks 2, 3, 4, 6 should wait for the jsonifier code to stabilize under Codex.

---

## 6. Exit gate (Phase 2, prospectus track)

Per the Master Plan §7 exit gate (line 306):

- [ ] Each sampled chunk resolves to the correct page/section
- [ ] Tables retain meaning
- [ ] No unreviewed critical extraction error reaches rule authoring
- [ ] Phase succeeds without calling an embedding model or writing vectors
- [ ] The jsonifier's existing regression suite passes inside the container
- [ ] `ProspectusResult` validates against the Phase 1 contracts
- [ ] `build_payload()` is callable from the pipeline without CLI arguments or hardcoded paths
