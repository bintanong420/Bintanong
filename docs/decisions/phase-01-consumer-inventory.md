# Phase 1 Task 1: consumer inventory for the ten shared contracts

Status: inventory only. It changes no runtime behaviour, creates no model, and approves no source. Line numbers are for commit ec0eac7 (reviewed Phase E tip); paths are repository-relative. Pydantic 2.13.4 is already importable and is the existing model convention (`bintu_client.py:10`, `embedding/main.py:7`, `api/main.py:5`).

Inspected: `plans/phase-00-handoff.md`, `docs/decisions/phase-00-compatibility.md`, `docs/decisions/prospectus-phase-e-handoff.md`, `backend/bintanong_api/`, `backend/bintanong_embedding/`, `backend/bintanong_tools/` (including `prospectus_extractor/`), `tests/test_bintu_inference.py`, master sections 1.3, 6, 11.4 and 16.

## Version strings in use today

| String | Where | Meaning |
|---|---|---|
| `palsu-prospectus-v3.3` | `prospectus_extractor/common.py:8` (`SCHEMA_VERSION`), emitted at `pipeline.py:145` | Prospectus candidate payload schema |
| `palsu-prospectus-batch-manifest-v3.1` | `common.py:11`, `batch.py:153` | Batch manifest |
| `palsu-prospectus-essentials-v2` | `pipeline.py:225` | Essentials file |
| `palsu-chunker-v1` | `chunking.py:11` (`CHUNKER_VERSION`), `rag.chunker_version` at `pipeline.py:177` | Chunk identity input |
| `estimate-v1` | `chunking.py:17` (`TOKEN_COUNT_METHOD`) | Heuristic token count, not a tokenizer bound |
| `prospectus-decision-ledger-v1` | `ledger.py:41` | Human decision ledger entry |
| `prospectus-corrected-candidate-v1` | `ledger.py:42` | Corrected candidate |
| `isolated-original-pdf-run-v1` | `prospectus_batch.py:76` | Isolated run manifest |
| `palsu-born-digital-v3`, `IDENTITY_VERSION = 1` | `identity.py:18-19` | Conversion profile and run identity |
| `SEA-LION-E5-Embedding-600M`, dimension 1024 | `embedding/main.py:11-12` | Embedding model name and size; no revision, tokenizer or prompt fingerprint is recorded |
| none | `bintu_client.py` `RoutingDecision` | The routing model has no schema version |

## Contract by contract

For each contract: existing code that already models something similar, the gaps, and the adapter plan. The rule is reuse and adapt; no parallel model that duplicates a field set already produced by the extractor.

### 1. SourceDocumentVersion

- Existing: `ProvisionalSource` (`backend/bintanong_tools/prospectus.py:13-24`): `pdf_sha256`, `source_locator`, `source_verification` fixed to `"pending"`, hash check in `verify_digest` (`:22`). `authority.build_authority` reads it by duck typing (`authority.py:82-110`). `run_identity` (`identity.py:113-160`) holds `input_sha256`, `pdf_sha256`, `conversion_identity`, `schema_version`. Metadata observations carry `basis` and `evidence` (`metadata.py:151`, `:172-173`).
- Gaps: no document ID or version ID; no issuer; no campus/college/program/cohort scope as a governed record (only observed `campus`, `college_code`, `program_name`, `effective_school_year`, `authority.py:25`); no effectivity or supersession; no approval identifiers; verification is a single string rather than three separate states. `payload["source_path"]` (`pipeline.py:153`) is a machine-specific absolute path inside the candidate payload, which must not enter any committed register.
- Adapter: the new contract wraps `pdf_sha256` and the observed identity fields. `ProvisionalSource.source_verification == "pending"` maps to verification `pending` and approval ids `null`. Locators in committed material are fictional.

### 2. SourceSpan

- Existing: `make_span` (`chunking.py:42-49`) yields `pdf_sha256`, `page`, `printed_page_label` (always `None`), `locator` (`table_cells` with `table_index` and `cell_ids`, or `text_item` with `item_ids`), `text`, `bbox`, `bbox_origin`, and `extraction` (`source_kind`, `resolution_method`, `repair_id`, `ocr_confidence`). `spans_from_cells` and `spans_from_text_items` (`:52`, `:77`).
- Gaps: printed page label never filled; no page size alongside the box (origin is present, page size is not); no slide index for PPTX; `pdf_sha256` may be `None` (unanchored); `page` may be `None`.
- Adapter: map field for field. An unanchored span (`pdf_sha256` null) is representable but can never assert a verified source.

### 3. Chunk

- Existing: `assemble_chunk` (`chunking.py:109-127`): `chunk_id` (`make_chunk_id`, `:91`, hash of edition, locator, content digest and chunker version), `chunk_type`, `chunker_version`, `content_review: "pending"`, `pdf_sha256`, `source_anchored`, `text`, `source_text` (printed, separate from `text`), `source_spans`, `pages`, `table_indexes`, `cell_ids`, `content_hash`, `token_count`, `token_count_method`, `source`. A chunk needs at least one span (`:114`). Rejections are listed, never dropped (`rag.py:26-39`, `_rejection` at `:61`, payload `rag.rejected_chunks` at `pipeline.py:181`).
- Gaps: no section path or scope field as such (fields vary by chunk type through `**fields`); no document-version ID; no governed namespace.
- Adapter: contract fields are the existing keys; add the missing scope and section path as optional, empty by default, never inferred. Reject a chunk with no spans, exactly as `assemble_chunk` does.

### 4. EmbeddingRecord

- Existing: service only. `EncodeRequest`, `EncodeResponse(dimension, count, embeddings)` (`embedding/main.py:65-72`), `MODEL_DIMENSION = 1024`, normalised vectors (`:61`), weights digest check (`verifier.py:16`, `main.py:13`).
- Gaps: no chunk ID linkage, no model revision, tokenizer or prompt fingerprint, no preprocessing record, no exact token count (the only counter is the `estimate-v1` heuristic, `chunking.py:20`; the Phase E handoff states exact counting with prefix and special tokens is not run).
- Adapter: contract only; no embedding or vector calls in Phase 1.

### 5. NormalizedQuery

- Existing: none. `route_query(query: str)` (`bintu_client.py:59`) takes a bare string.
- Gap: everything. Session-fact references need the institutional/private separation defined in Task 2.

### 6. RoutingDecision

- Existing: `RoutingDecision(route, confidence, reason)` (`bintu_client.py:13-16`), validated in `route_query` (`:78`); prompt at `:42-50`; tests `tests/test_bintu_inference.py:17-26`.
- Gaps: no schema version, no control outcome, no typed predicate request, no required/missing facts. `route` allows `"Direct"` (see the discrepancy below).
- Adapter: the new contract extends this model in place of replacing it; the existing three fields stay.

### 7. RetrievalResult

- Existing: nothing at runtime. `rag.semantic_chunks`, `hierarchical_chunks` in the candidate payload (`pipeline.py:176-182`) are the only chunk source.
- Gaps: no knowledge-release ID, scores, coverage status; no check that results do not mix editions.

### 8. SymbolicResult

- Existing: prerequisite states `PREREQUISITE_STATES` and `EXECUTABLE_PREREQUISITE_STATES = {resolved, stated_none, reviewed_empty}` (`prerequisites.py:223-235`); `authority.eligibility_executable` and `blocked_by` (`authority.py:137-153`); Janus readiness probe in `api/probes.py` and `api/main.py:39`. `stated_none` (printed none) and `reviewed_empty` (human decision) are distinct from `blank_unreviewed` and `unreadable`.
- Gaps: no five-outcome status, no predicate registry, no rule bundle version, no rule IDs. The state `eligibility_executable` is not an outcome and is always false today.
- Adapter: reuse the prerequisite states as the input to "rule coverage present"; verified zero prerequisites is `stated_none` or `reviewed_empty`, never blank.

### 9. EvidenceBundle

- Existing: none.
- Gaps: everything; the private/institutional split is the main trust boundary (Task 2).

### 10. AnswerEnvelope

- Existing: only `HealthStatus` (`api/main.py:16-19`) and the health routes; no chat route exists yet (master 16.1 lists `POST /chat`, `/uploads`, `DELETE /session`, `GET /sources/{id}` as proposed).
- Gaps: everything. Because no session or upload route exists, retention, deletion and isolation can only be stated as requirements here and checked when those routes are built.

### Authority and ledger (cross-cutting, feeds Task 2)

- `build_authority` keeps three separate fields: `extraction_audit`, `content_review`, `source_verification` (`authority.py:137-141`) and states that `promotion_status` is not approval (`:148-152`). `content_review_state` returns `pending | partially_reviewed | reviewed` and says it is not approval (`ledger.py:443-448`). Ledger entries carry reviewer, reason, `pdf_sha256`, locator, disposition and a content-derived `entry_id` (`ledger.py:206-228`).
- Gaps: no approval-id concept, no authorized-evidence reference, no transition table. Task 2 supplies the vocabulary; the ledger remains a content-review record, never a source approval.

## Direct routing discrepancy

- Code: `backend/bintanong_api/bintu_client.py:14` allows `route` in `RAG | Hybrid | Symbolic | Direct`. The system prompt at `:48` defines Direct as "simple conversational greetings or out-of-scope questions". Phase 0 handoff `plans/phase-00-handoff.md:34` recorded the same four values. `tests/test_bintu_inference.py:17-26` covers `RAG` and an invalid route; no test uses `Direct`.
- Master intent: master section 3 (about line 134) states that greetings, missing context, unsupported scope and unavailable evidence are control outcomes, not a fourth substantive route; `route` may be null; no institutional claim may bypass retrieval or approved symbolic evidence through a general-chat shortcut.
- Proposed contract meaning (for owner decision): `route` is one of `RAG`, `Hybrid`, `Symbolic` or null; a separate closed `control` field carries clarify, greeting, unsupported scope, evidence unavailable. A legacy `Direct` from the live client is accepted only by an adapter that maps it to `route = null` with a control outcome, so a Direct decision can never carry an institutional claim. The existing model and prompt stay untouched in Phase 1 Task 1.
- Regression evidence needed before any runtime change: a test that the legacy `Direct` value still parses through the adapter (compatibility), a test that the new contract rejects `Direct` as a route, a test that a null route with a control outcome cannot be dispatched to retrieval or symbolic components, and a test that a Direct-derived decision cannot produce an institutional citation. None of these is written in this task.
- Status: unresolved. No runtime behaviour was changed.

## Other findings

- `tools/ingest.py:34` and `:57` put `str(path)` in output metadata (a local path). Committed evidence must not carry it; the register uses a locator label instead.
- `tools/evaluate.py:19` is a placeholder; there is no evaluation harness to adapt yet.
- Chunk and rejected-chunk shapes are stable at schema v3.3 and are the compatibility target for the Chunk and SourceSpan contracts.
