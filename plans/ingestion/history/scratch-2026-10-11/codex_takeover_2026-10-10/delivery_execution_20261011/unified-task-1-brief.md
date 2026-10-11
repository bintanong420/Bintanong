# Task1 dispatch brief

## Global constraints

- Baseline is clean draft/phase2-candidates-20261010 at57b598522cc7ed5d13e40eb8d1bcafede8c9ba1b; verify fresh Git and usage before execution.
- Every PowerShell starts Set-Location to the actual worktree; all paths absolute; py -3.13 -B; pytest -p no:cacheprovider with a new external basetemp. Offline, no installs/downloads/dependency/lock changes.
- No owner writes, protected-ref movement, push/PR/merge/history rewrite or attribution. Explicit staging only. Originals/private/generated artifacts outside Git.
- No embeddings, executable .pl files, Janus, routing, API/Docker or institutional activation. Candidate completion never grants source/content approval.
- Preserve pending-only register preparation. Keep existing loaders/contracts/extractor APIs intact. Do not adopt entire F files or reuse its unreviewed fixes implicitly.
- Stop new batches at>=85% of either Codex window; save promptly above85%; never spend toward90%.
- M1 repair remains independently unrechecked. A new feature review must not masquerade as its prohibited Medium recheck; retain that separate review debt until an explicit exception.


## Task1: Bind existing prospectus chunks to pending source versions

**Files:** create backend/bintanong_tools/document_ingest/prospectus.py; create tests/test_prospectus_ingestion.py; create docs/decisions/phase-02-unified-ingestion.md. Do not modify backend/bintanong_contracts/chunk_adapter.py or the extractor.

**Consumes:** adapt_chunk(raw,*,page_sizes,on_missing_page_size='reject')->AdaptedChunk; SourceDocumentVersion; SourceSpan/Chunk parsing and check_span_binding; source.bind_chunk/check_chunk_binding; load_pending_register.

**Produces:** `bind_prospectus_chunks(payload: Mapping[str,Any], version: SourceDocumentVersion, *, page_sizes: Mapping[tuple[str,int],tuple[float,float]]) -> dict[str,Any]`. Result keys: version_id,source_sha256,chunks,rejections; chunks are serialized existing Chunk contracts, rejections contain original chunk_id/reason. This is a domain-specific candidate result, not a new public contract.

- [ ] Write focused failing tests: valid semantic/hierarchical source chunks retain chunk_id/content_hash; all emitted chunks and spans name the exact registered version and document/edition IDs; no approval promotion; missing payload digest, digest mismatch, foreign/non-null version, duplicate chunk identity and forged privileged fields refuse; absent page geometry/raw-text hash mismatch are explicit rejections; deep-copied inputs remain equal after both success and refusal. Include M01's check-before-write case at this new boundary without changing the historical52/52 claim.
- [ ] Run only tests/test_prospectus_ingestion.py with system Python, no cache and external basetemp; record actual RED exit before product implementation.
- [ ] Implement binding: validate pending source and payload.run_identity.pdf_sha256 first; consume rag.semantic_chunks and rag.hierarchical_chunks; reuse adapt_chunk with actual captured-PDF page sizes. Precheck foreign preexisting identity/span claims, then reuse source.bind_chunk/check_chunk_binding to copy registered states/evidence and bind spans; validate complete support. Preserve raw chunk order, content hashes and IDs. Current ver-<byteSHA> identities make the byte-derived legacy IDs version-separated; another identity scheme needs an explicit migration policy. Reject global identity/shape violations; account for each individual unsupported chunk. Keep scopes pending; no fabricated issuer or status.
- [ ] Run focused GREEN plus existing tests/test_contracts_chunk_adapter.py and tests/test_register_minting.py. Assert imports are worktree-bound and Git diff --check passes.
- [ ] Root checks evidence, explicitly stages only the three named paths and commits `feat(ingest): bind prospectus candidate chunks to source versions`. Separate Spec then Standards runs against a frozen external archive; no self-review. Retain existing M1/F/session debts separately.


Owner rules: no descendants, no commits/staging by worker; root commits after its independent focused acceptance. No self-review gate: separate reviewers are mandatory. Worktree C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010. BASE57b598522cc7ed5d13e40eb8d1bcafede8c9ba1b. Read extractor-implementer.md and S/implementer-prompt.md as Markdown only; use system Python override. Save full RED/GREEN commands, real exits and counts to external task report/logs. If Codex account reaches>=85, stop starting new batches and checkpoint; never spend toward90. This is Task1 only, not wrapper/compiler/bridge.
