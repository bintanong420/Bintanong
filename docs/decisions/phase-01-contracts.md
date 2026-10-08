# Phase 1 Task 3: shared contracts (`backend/bintanong_contracts/`)

Status: implemented and tested; approves no source, edition or curriculum. Every example is synthetic with fictional ids and digests. Phase 1 as a whole is NOT complete: Tasks 4 to 6 and an independent review remain. No runtime behaviour of `bintanong_api`, `bintanong_embedding` or `bintanong_tools` changed; the package is new code whose adapters read the shapes those packages emit.

## Package layout

| Module | Contracts (schema version) | Notes |
|---|---|---|
| `base.py` | `Record`, `Contract`, `canonical_json`, namespaces | Extra fields forbidden, instances frozen, strict types, exact `schema_version`. The closed vocabularies are loaded from `knowledge/manifests/governance-vocabulary.json`, the single source of truth. |
| `governance.py` | `SourceDocumentVersion` (`bintanong-source-register-v1`), `SourceConflict` (`...-source-conflict-v1`), `SessionFact` (`...-session-fact-v1`) | Replaces the test-local checker in `tests/test_source_governance_manifests.py` for runtime use; that file is kept as an independent cross-check. `check_register` holds the cross-record rules. |
| `source.py` | `SourceSpan` (`...-source-span-v1`), `Chunk` (`...-chunk-v1`), `TokenCount` | `bind_chunk` / `check_chunk_binding` tie a chunk to a register version. |
| `chunk_adapter.py` | adapter | Prospectus extractor v3.3 chunk dict to `Chunk`. Read-only, imports nothing from the extractor. |
| `embedding.py` | `EmbeddingRecord` (`...-embedding-record-v1`) | Validation only. No embedding or vector call exists. |
| `runtime.py` | `NormalizedQuery`, `RoutingDecision`, `RetrievalResult` (`...-v1` each), `PredicateRequest`, `BoundInput` | |
| `routing_adapter.py` | adapter | Legacy client routing shape to `RoutingDecision`. Refuses legacy `Direct`. |
| `symbolic.py` | `DecisionOutcome` (`bintanong-decision-v1`), `SymbolicResult` (`...-symbolic-result-v1`), `CapabilityRegistry` | Five outcomes enforced from the vocabulary file. |
| `answer.py` | `EvidenceBundle`, `AnswerEnvelope` (`...-v1` each) | |

Tests: `tests/test_contracts_*.py` (nine files). `tests/contracts_fixtures.py` holds synthetic builders.

## What is enforced

- Forbidden status promotion: a state other than the initial one must cite evidence inside the record whose kind and recorder match a transition row; extraction audit, extractor labels, filenames and possession never match a row; `approval_id` exists only with issuing-office authorization evidence carrying the same reference; approval additionally needs verified acquisition, verified scope, verified issuer and a non-proposal category. A chunk can carry no privileged status key, and a chunk's `source_verification` must equal the register's state when bound (neither inflated nor stale).
- Institutional and private mixing: institutional (`doc-`, `ver-`, `edition-`, `conflict-`) and private (`sess-`, `fact-`) ids are checked by pattern and by a scan of every string in every record; a session fact has no field through which it could become a source; an evidence bundle rejects a private id inside any institutional part; a decision resting on a student statement is accepted only when the student confirmed it; a rejected statement is refused everywhere.
- Source anchoring: spans carry the exact byte digest; geometry needs origin AND page size, must be non-empty and lie inside the page; the printed page label is never derived from the physical page; duplicate locations are rejected; an unanchored chunk can never claim a version, an edition or a verification state.
- Routing and outcomes: exactly one of route and control outcome; there is no `Direct` route; a symbolic goal is a registered predicate name plus bound inputs whose values cannot carry Prolog syntax; an error is operational and never converted; `unknown`, `unsupported` and `error` can never be an approval or a denial in an answer envelope; a RAG explanation can never stand in for a failed Hybrid symbolic half.
- Determinism: canonical JSON has sorted keys, two-space indent, LF and one trailing newline; serialise, parse and re-serialise give equal text.

## Adapters

- Chunk adapter (`chunk_adapter.adapt_chunk`): preserves `chunk_id`, `content_hash`, the printed `source_text` and the `estimate-v1` token-count method; recomputes id, hash and derived `pages`/`table_indexes`/`cell_ids` and rejects a mismatch (`chunk_id_mismatch`, `content_hash_mismatch`, `derived_field_mismatch:<key>`). Fields the contract has no slot for (`course_code`, `derived_fields`, ...) are kept in `type_fields`, not dropped. Rejection reasons are stable strings on `ChunkMappingError.reason`, for example `no_source_spans`, `span_missing_page`, `unknown_locator_kind`, `unmapped_span_key:<k>`, `privileged_field:<k>`, `duplicate_source_location`.
- Precise gap: the extractor records a bounding box and its origin but no page size. The adapter will not invent one. By default a chunk with a box and no supplied page size is rejected with `bbox_missing_page_size` naming the span and page. The caller may pass `page_sizes` keyed by (digest, page), or opt in to `on_missing_page_size="omit_and_report"`, which drops the box and returns a `Gap` for every dropped box. Closing the gap properly means the extractor recording page size, which is an extractor change outside this task.
- Routing adapter (`routing_adapter.from_legacy_routing`): duck-types `bintu_client.RoutingDecision` without importing it. Legacy `Direct` raises `LegacyRoutingError` with reason `legacy_direct_unresolved_owner_decision` and a message that names the open owner decision. Legacy `Symbolic` and `Hybrid` are accepted only with a typed `predicate_request` from a validated source, because the legacy shape has no predicate.

## Ambiguities resolved with the strict option

1. A bounding box with no page size is refused, not given a default (see the gap above).
2. A box that extends past the page edge by any amount is refused (no tolerance).
3. An anchored span without a physical page or printed text is representable (the extractor emits them) but never complete, so an anchored chunk containing one is refused.
4. Two spans of one chunk that share a cell, item or reference on the same page are refused as duplicate source locations.
5. A decision may be `eligible` or `ineligible` only when every input that came from a student statement was confirmed by the student; unconfirmed statements may still support `unknown`.
6. A legacy routing reason longer than 240 characters is refused, not truncated.
7. A retrieval result that holds two editions of one document is refused outright; it is not silently merged.
8. A model revision of `main`, `master`, `latest` or `head` is not a pinned revision.
9. A synthetic decision may support only an abstention or an error report, never a decision or passage claim.
10. A conflict that is unresolved or referred blocks decisions only in its own capability; an `unknown` outcome in that capability must list it.
11. Registry default is empty: with no authorized rules every request is `unsupported`.
12. Free-text claims are not parsed: the envelope status and the permitted claims are structural, so wording is not policed.

## Owner decisions needed (none decided here)

1. What legacy `Direct` means (greeting, out of scope, or both) and whether the live router prompt should keep a fourth class. Until decided it is refused everywhere.
2. Where page sizes come from: should the extractor record them next to every box, or is omitting boxes acceptable for retrieval?
3. Whether a small geometry tolerance outside the page is acceptable.
4. Whether unconfirmed student statements may ever support an `eligible` or `ineligible` decision.
5. Who produces the typed predicate request for `Symbolic` and `Hybrid` routes (router prompt change, or a separate component), and who authorizes capability registry entries.
6. How a source conflict's `capability` maps to a route and to retrieved passages (today the mapping is exact name equality against the symbolic capability only).
7. Whether a comparison query may deliberately retrieve two editions of a document (needs an explicit flag and an answer that names both).
8. The intent taxonomy for `NormalizedQuery` (free text today) and the language set (`en`, `tl`, `taglish` today).
9. The exact-token-count convention (`tokenizer:<id>@<revision>`), which tokenizer, and the pinned embedding model revision. No exact count has been run.
10. The knowledge-release id convention (`release-...`) and who mints release ids.
11. Dependency declaration: `pydantic` is declared in the `api` and `embedding` extras only, so the contracts tests need a pydantic install that the `tools` plus `dev` extras do not provide; `jsonschema` is used only through an optional import. `backend/pyproject.toml` and `uv.lock` were not edited.
12. Earlier open items remain (see `phase-01-source-governance.md`): document categories, who may record as issuing office, verifier independence, reopening of resolved or revoked records, printed date format, session idle lifetime.

## Verification

- `tests/test_contracts_*.py`: 520 tests, all passing on system Python 3.13 (pydantic 2.13.4, jsonschema optional). Full suite 2325 passed, 1 skipped, 13 subtests; the prospectus jsonifier self-test is 80/80.
- Red first: each test file was run before its module existed and failed at collection (module not found).
- Schema compatibility: all synthetic examples validate with the real package and roundtrip to equal canonical text; the model field sets equal the schema properties; for every single-value mutation of the examples that the JSON Schema rejects, the package also rejects (the package is at least as strict).
- Mutation checks in a scratch copy: 192 guard mutations first run killed 160 and 32 survived. Six survivors were redundant guards (another check already covered the same case) and were deleted; the rest got new tests. Re-run: 188 mutations, 188 killed, 0 survived.

## Not done or not run

- No embedding, vector, network or model call; no real PDF or institutional source was read; no source was verified or approved.
- Retention, deletion and session isolation remain requirements: no session route exists yet.
- Copied private text is detected by id and namespace, not by text similarity (a text match would reject legitimate course codes that appear in both a student statement and a handbook).
- `type_fields` on a chunk is an opaque dictionary and is not deep-frozen; privileged status keys are refused at its top level only.
- The `docling_ref` locator kind is exercised by contract tests but not by a real extractor chunk in these tests (the extractor builds it only from a Docling document).
