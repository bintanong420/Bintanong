# Phase 2 draft: governed chunks, report and single-document pipeline

This owner-authorized draft follows `5d543ee` on `draft/phase2-candidates-20261010`. It does not start or complete formal Phase 2 or adopt institutional content. The phase ledger, protected contracts, extractor, API, embedding packages and dependencies remain unchanged.

## Shared candidate route

The smallest shared route adds explicit `policy_candidate` classification to the new `procedure_text` reader and conversion wrapper. That route retains policy text and every raw table from the same byte-bound conversion, while leaving procedure fields empty. Existing procedure, Charter, form and proposal classifications retain their behavior. Neither classification nor filename changes register authority. The older direct `PolicyCandidates` interface remains accepted by the chunk/report library; its text-only representation cannot assert raw table coverage. The complete pipeline therefore uses the shared reader for policy PDFs too.

## Chunk and report interfaces

`build_policy_chunks(candidates, *, token_cap=480) -> PolicyChunkResult` consumes `PolicyCandidates` or `ProcedureCandidates`. Frozen result records contain the source version/digest, chunks, item/table coverage and explicit rejections. The existing `SourceDocumentVersion`, `SourceSpan` and `Chunk` contracts are reparsed from serialized dictionaries, then checked with `check_span_binding`, `bind_chunk` and `check_chunk_binding`. The source register remains initial/pending with null approval ID. There is no copied contract/schema or privileged state inside chunk `type_fields`.

Chunker version is `palsu-policy-chunker-v1`. Stable chunk IDs derive from edition, physical-page/locator identities, content hash and chunker version. The existing `compute_content_hash`, `canonical_text` and `estimate_tokens` are reused. Printed chunk content is the raw span text joined with newlines; punctuation, negation, numeric values, en dashes and superscripts are preserved. Canonical whitespace is used for identity/containment only. Each unit retains its raw heading path, label, printed scope candidate and exception link; printed scope never becomes an authorized scope field. Geometry and text-item locator/provenance must agree. Missing/bad geometry, digest/version mismatch, missing text or unanchored units remain report rejections. Multi-provenance text whose joined fragments cannot satisfy the source-text contract is rejected rather than rewritten.

The cap is an `estimate-v1` review estimate, retaining the existing 32-token reserve under the proposed 512-token budget. It is not an exact tokenizer bound, including model prefix/special tokens. Oversized non-table clauses are rejected as `over_token_cap`; they are never split or summarized.

Every raw table remains in the candidate export with its complete wrapper and page geometry. PDF tables emit only when every used cell has complete raw text and geometry support. Cell provenance is used directly; a raw cell bbox may inherit the table page only when the wrapper unambiguously identifies exactly one physical page. A multi-page wrapper never supplies an invented cell page. Raw cell array order, IDs (or stable raw-array IDs when Docling exports none), merged row/column offsets and exact text are retained. Blank or unsupported cells reject the whole table with its raw evidence; no blank cell or table is silently dropped.

Supported oversized tables split at complete row groups, keeping merged rows indivisible. Only leading rows whose raw `column_header` flags identify every cell as a header may repeat. Ambiguous, absent or later header flags reject an oversized table. Every emitted part repeats complete header spans, stays within the estimate cap and retains the source section path. PPTX units/tables remain `pending_locator_contract`; slide indices never become PDF pages.

`build_ingestion_report(candidates, result, *, conversion_metadata=None) -> dict` reparses chunk contracts and checks the supplied result against a deterministic rebuild before publishing complete accounting. A stale hash, fabricated ID, mismatched source, omitted rejection/coverage or inflated cap is refused. Every raw text item occurs exactly once in chunk coverage, rejection or item omission; every table is emitted (possibly several parts) or rejected. Repeated headers and split parts do not increase original item/table counts. Every physical PDF page is covered or explicitly omitted; text-layer absence findings remain visible even on table-covered pages.

The report records source identity, actual supplied conversion metadata/settings/tool versions, physical-to-printed page labels, original counts, chunk counts, coverage, rejections with full raw evidence, omissions, conflicts and review needs. Source verification/content review stay pending and approval ID stays null. `accounting_complete` describes accounting only. Empty conflict findings do not claim that semantic conflicts were assessed; that review need remains explicit. Missing conversion identity is recorded as a review gap by the standalone report interface; the pipeline requires byte-bound conversion metadata.

## Usable external-output pipeline

`run_ingestion(snapshot, register, *, input_root, out, classification, converter=None, printed_page_labels=None) -> dict` is the smallest library entrypoint. The registered immutable snapshot, whole pending register, explicit classification/input root and new/empty external output folder are validated before conversion. Policy classification requires PDF; supported procedure/form classifications can use PDF or PPTX. The installed conversion stack runs once under `out/conversion` using captured bytes; a supplied stub converter exercises the same synthetic end-to-end path.

The pipeline verifies conversion completion, artifact digests, source/raw byte metadata and conversion identity/settings, then rereads candidates from those same authenticated raw bytes. It writes `source_register.json`, `chunks.json` and `ingestion_report.json` outside Git. Original snapshot verification occurs after conversion and immediately before the root `manifest.json` is written last. Each manifest lists exact output digests. A missing root completion manifest means an incomplete bundle, even if the nested conversion stage completed. Failed runs require a new output folder for retry. Partial files are evidence only, never an active release; there is no activation/publishing integration.

Minimal command (explicit acquisition locator and candidate classification):

```powershell
py -3.13 -B -m backend.bintanong_tools.document_ingest SOURCE.pdf --root ORIGINALS_ROOT --out NEW_EXTERNAL_FOLDER --locator shelf:handbook-copy --classification policy_candidate
```

`--help` needs no conversion. CLI conversion output goes to stderr; success stdout is a small JSON accounting summary. It does not replace generic `ingest.py` or the unfinished Phase F command.

## Focused evidence and remaining work

Synthetic red/green checks exercise contract round trips, immutable input, status injection, stale hashes/IDs, editions, geometry/version/locator mismatch, cap refusal, raw table header splitting and accounting, unsupported cell evidence, PPTX rejection, report omissions/rejections, snapshot preflight, conversion tampering, output containment, source mutation after conversion/report publication, failed writes and CLI help. Exact commands/results/source hashes and consumer notes are recorded outside Git under `phase2_chunks_report` in the takeover evidence root. Acceptance is coordinator-managed; no self-review verdict or readiness claim is made.

NOT RUN: institutional conversions/content reading, corpus/mutation campaign, broad four-thousand-test suite, exact tokenizer, embedding/rule/vector/database writes, authenticated scope/issuer/effectivity/supersession, OCR gate, phone photographs, Docker/API/Linux/macOS, institutional approval and phase-exit/adoption/merge gates. The existing loader reports its conversion settings; this draft adds no independent inspection of its backend-fallback execution or authentication of an arbitrary caller-supplied converter.
