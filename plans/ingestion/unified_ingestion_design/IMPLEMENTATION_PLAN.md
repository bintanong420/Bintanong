# Shared Institutional Ingestion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox tracking.

**Goal:** Produce one checked, version-bound institutional candidate handoff from the existing prospectus and policy/procedure readers.

**Architecture:** Retain existing extraction and domain-specific candidate artifacts. Add a small prospectus binding boundary, explicit CLI dispatch and a consumer-side bundle check. Keep private processing, OCR accuracy certification, embeddings, releases and rule execution outside this change.

**Tech Stack:** System Python3.13, existing Pydantic contracts, installed Docling/pypdfium2, pytest; no new dependency.

**Spec:** [SPEC.md](SPEC.md).

Status: owner explicitly authorized implementation of plan_alignment_20261011/REPORT.md on2026-10-11. Report corrections are incorporated below; execution is authorized in isolated local draft batches. Execution method already selected: separate fresh implementer, independent Spec, then separate Standards, maximum coordinator+one active child. No need to ask for method again. This plan does not approve adoption or a formal phase start.

## Global constraints

- Baseline is clean draft/phase2-candidates-20261010 at57b598522cc7ed5d13e40eb8d1bcafede8c9ba1b; verify fresh Git and usage before execution.
- Every PowerShell starts Set-Location to the actual worktree; all paths absolute; py -3.13 -B; pytest -p no:cacheprovider with a new external basetemp. Offline, no installs/downloads/dependency/lock changes.
- No owner writes, protected-ref movement, push/PR/merge/history rewrite or attribution. Explicit staging only. Originals/private/generated artifacts outside Git.
- No embeddings, executable .pl files, Janus, routing, API/Docker or institutional activation. Candidate completion never grants source/content approval.
- Preserve pending-only register preparation. Keep existing loaders/contracts/extractor APIs intact. Do not adopt entire F files or reuse its unreviewed fixes implicitly.
- Stop new batches at>=85% of either Codex window; save promptly above85%; never spend toward90%.
- M1 repair remains independently unrechecked. A new feature review must not masquerade as its prohibited Medium recheck; retain that separate review debt until an explicit exception.

## Review focus

1. Explicit partial conversion with surviving text must not produce a consumable root manifest (Task2).
2. Same bytes with a forged version/foreign span must fail before publication; preserve input objects (Task1).
3. Malformed, extra, escaping or replaced manifest artifacts must not be consumed (Task2).
4. Missing geometry/raw table text and oversized legacy chunks must remain named rejections, never invented evidence (Task1).
5. Interrupted work, private namespaces and raw JSON review inputs must never become institutional-ready bundles (Task2).

## Task1: Bind existing prospectus chunks to pending source versions

**Files:** create backend/bintanong_tools/document_ingest/prospectus.py; create tests/test_prospectus_ingestion.py; create docs/decisions/phase-02-unified-ingestion.md. Do not modify backend/bintanong_contracts/chunk_adapter.py or the extractor.

**Consumes:** adapt_chunk(raw,*,page_sizes,on_missing_page_size='reject')->AdaptedChunk; SourceDocumentVersion; SourceSpan/Chunk parsing and check_span_binding; source.bind_chunk/check_chunk_binding; load_pending_register.

**Produces:** `bind_prospectus_chunks(payload: Mapping[str,Any], version: SourceDocumentVersion, *, page_sizes: Mapping[tuple[str,int],tuple[float,float]]) -> dict[str,Any]`. Result keys: version_id,source_sha256,chunks,rejections; chunks are serialized existing Chunk contracts, rejections contain original chunk_id/reason. This is a domain-specific candidate result, not a new public contract.

- [ ] Write focused failing tests: valid semantic/hierarchical source chunks retain chunk_id/content_hash; all emitted chunks and spans name the exact registered version and document/edition IDs; no approval promotion; missing payload digest, digest mismatch, foreign/non-null version, duplicate chunk identity and forged privileged fields refuse; absent page geometry/raw-text hash mismatch are explicit rejections; deep-copied inputs remain equal after both success and refusal. Include M01's check-before-write case at this new boundary without changing the historical52/52 claim.
- [ ] Run only tests/test_prospectus_ingestion.py with system Python, no cache and external basetemp; record actual RED exit before product implementation.
- [ ] Implement binding: validate pending source and payload.run_identity.pdf_sha256 first; consume rag.semantic_chunks and rag.hierarchical_chunks; reuse adapt_chunk with actual captured-PDF page sizes. Precheck foreign preexisting identity/span claims, then reuse source.bind_chunk/check_chunk_binding to copy registered states/evidence and bind spans; validate complete support. Preserve raw chunk order, content hashes and IDs. Current ver-<byteSHA> identities make the byte-derived legacy IDs version-separated; another identity scheme needs an explicit migration policy. Reject global identity/shape violations; account for each individual unsupported chunk. Keep scopes pending; no fabricated issuer or status.
- [ ] Run focused GREEN plus existing tests/test_contracts_chunk_adapter.py and tests/test_register_minting.py. Assert imports are worktree-bound and Git diff --check passes.
- [ ] Root checks evidence, explicitly stages only the three named paths and commits `feat(ingest): bind prospectus candidate chunks to source versions`. Separate Spec then Standards runs against a frozen external archive; no self-review. Retain existing M1/F/session debts separately.

## Task2: Shared candidate publication, consumption and explicit CLI route

**Files:** extend document_ingest/prospectus.py and tests/test_prospectus_ingestion.py; create document_ingest/bundle.py and tests/test_candidate_bundle.py; modify document_ingest/__main__.py and docs/decisions/phase-02-unified-ingestion.md. Existing policy pipeline and generic ingest CLI remain compatible.

**Consumes:** Task1 binding; InputSnapshot; pending_version/version_for_snapshot; inspection.check_out; loader.load_document_result(...,snapshot=...); pipeline.build_payload(...,semantic_doc_path=None,semantic_map={},source=ProvisionalSource(...),pdf_sha256=...,pdf_hash_check='matched'); existing document_ingest.pipeline.run_ingestion.

**Produces:** `run_prospectus_ingestion(snapshot:InputSnapshot, register, *, input_root:Path, out:Path, converter:Any=None)->dict[str,Any]`; `load_candidate_bundle(path:Path)->dict[str,Any]` returning reparsed source_register, chunks and report, plus domain_payload and conversion for prospectus bundles. domain_payload is the hash-checked prospectus_candidates.json payload; conversion contains the hash-checked raw Docling document and metadata. These are explicit domain handoff inputs, not approved rules. The existing CLI accepts one added explicit classification `prospectus_candidate`; all existing classifications retain current dispatch.

- [ ] Write RED tests for a captured synthetic prospectus through actual existing parser/audit with a synthetic converter; a policy/procedure bundle remains accepted; private namespace and raw JSON input refuse; partial/non-success result refuses before any completion manifest; changed source/settings/raw artifacts, cross-version spans, duplicate/unknown files, path escapes/symlinks, false root completion and nested-only completion refuse. Interrupt publication and prove a later consumer refuses it. No .pl file or PROLOG_RULES helper code is published. Help and existing CLI flags remain valid without initializing a converter.
- [ ] Run new focused tests and record RED. Use public/synthetic bytes only; no real private data.
- [ ] Implement the prospectus wrapper: pending-register/output preflight before conversion; explicit external conversion paths and captured snapshot passed to the existing loader. Use its converter seam to reject errors/explicit non-success status before raw export; the stricter new wrapper must not silently rely on the generic-ingest M1 repair. Keep the protected loader unchanged. Record actual settings/backend and reject unverifiable settings rather than inventing metadata. Read page sizes from the captured PDF with resources closed. Build existing curriculum payload without ambient semantic-file lookup; retain structured candidates/audit, omit legacy consult-ready prolog/helper views from the published candidate. Bind chunks through Task1 and account for every candidate/rejection in the report. A failing curriculum audit remains visibly blocked, not a ready chunk bundle.
- [ ] Publish captured raw_docling.json/meta plus prospectus_candidates.json in conversion/, a nested conversion manifest, source_register.json, chunks.json and ingestion_report.json; root manifest last, containing candidate_only=true,document_kind='prospectus_candidate',source/version IDs and exact artifact hashes. Reuse atomic writers. Use a new/empty external output and verify original identity before all publication. No implicit retry into stale outputs.
- [ ] Implement bundle consumption against exact documented policy/procedure and prospectus artifact sets. Existing manifests without document_kind follow the existing policy/procedure schema and must match their report. Validate safe regular-file containment, digests, nested completion/settings identity, source register and every chunk/span binding; distinguish technical completeness from review eligibility. Reject unknown kinds and artifacts; never promote pending sources. CLI uses the checked result for its summary.
- [ ] Run focused tests plus tests/test_ingestion_report.py,test_policy_chunks.py,test_policy_text.py,test_procedure_text.py,test_register_minting.py. Root runs one stable combined synthetic CLI/library smoke covering both domains. Existing exact-tokenizer/512-token validation stays in Phase3; estimate-v1 is reported truthfully.
- [ ] Explicitly stage the six named paths, commit `feat(ingest): share checked institutional candidate handoff`, then separate Spec and Standards runs on a frozen archive. Any confirmed repair follows the user's actual recheck rules.

## Task3: Connect the checked prospectus bundle to inactive rule candidates

**Depends on:** unified Tasks1–2 and the Phase6 pure compiler task. Execute after the compiler is tested and independently reviewed.

**Files:** create backend/bintanong_tools/document_ingest/prospectus_rules.py and tests/test_prospectus_rule_handoff.py; extend docs/decisions/phase-02-unified-ingestion.md. No extractor/contracts/runtime changes.

**Produces:** `prepare_rule_candidates(bundle_path:Path)->dict[str,Any]`. It uses load_candidate_bundle, requires prospectus_candidate kind and passes the verified domain_payload, exact registered source, derived per-course/per-field SourceSpans and applicable review evidence to build_rule_candidates. It returns inactive JSON in memory; no publication, .pl, network or runtime execution.

- [ ] Write RED using actual synthetic snapshot/converter -> run_prospectus_ingestion -> checked bundle -> prepare_rule_candidates; assert exact field cell/page/version support, inactive flags and the retained unresolved XX999 blocker. Changed candidate/raw/settings hashes, foreign cell/page/version, missing/ambiguous field provenance and policy/private bundle misuse must never acquire usable rule support.
- [ ] Map only explicit extractor field ownership/provenance and corresponding actual raw normalized cells/text. Reuse installed evidence/locator helpers. Whole-row or whole-chunk spans cannot stand in for unrelated individual fields. Retain missing/unlocatable/ambiguous field support as compiler blockers; malformed/forged ownership or source binding refuses. Derived category/year/semester/program/elective fields without direct support remain blocked. Retain raw source text and documented correction decisions without inventing approval.
- [ ] Run focused RED/GREEN and one combined synthetic end-to-end acceptance case. Record a documented library command for an external checked prospectus bundle; outputs remain external JSON review data and source hashes remain unchanged. This closes the cross-plan interface gap, not corpus accuracy/source authorization.
- [ ] Root focused acceptance, explicit staging of the three paths, local draft commit, frozen read-only archive, separate fresh Spec then Standards. Preserve existing unrelated review debts and exact recheck limits.

## Execution commands and exits

For every test command, first Set-Location -LiteralPath 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'. Set PYTHONDONTWRITEBYTECODE=1 and existing offline flags in that process only. Use `py -3.13 -B -m pytest <ABSOLUTE_TEST_PATHS> -q -p no:cacheprovider --basetemp <NEW_ABSOLUTE_EXTERNAL_PATH>`. Assert imports inside the worktree before running tests. RED must fail for the named missing behavior; GREEN must exit0. Actual counts are recorded, not predetermined. Every local commit requires clean allowed-path staging, diff check and saved commands/logs/hashes externally.

## Subsequent evidence, not silently completed by this plan

Run representative original prospectus/Handbook/Charter readers after the stable boundary exists; verify unchanged original hashes and source-span samples. The39-distinct-prospectus corpus, ten independent policy-OCR references, OCR payload/confidence/review/edition work, simulated/real photos, human/domain/source authorization and private lifecycle remain explicit separate work. The already executed one-page Tesseract smoke is startup evidence only. Phase6's pure compiler has its own plan. No batch here awards a fixed progress percentage.

Owner instruction to implement the alignment report authorizes these written-plan corrections and implementation; no repeat confirmation is required. The already selected separate-subagent method is preserved. No formal phase-ledger update or adoption is authorized by that plan confirmation.
