# Prospectus Extractor Phase 2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Status:** User-approved for parallel, review-only prospectus work. This is a workstream plan, not a formal Phase 2 advancement in `plans/INDEX.md`.

**Goal:** Turn original PalSU prospectus PDFs into source-linked curriculum candidates that a human can compare and correct in a GUI before later RAG and Prolog authoring.

**Architecture:** One canonical Docling extractor in `backend/bintanong_tools/bintanong_jsonifer_prolog/` produces detailed evidence, compact candidate facts, and audit issues. A thin Bintanong adapter binds each run to original PDF bytes and a provisional, hash-based source record that can later be linked to Phase 1's source identity. A human review GUI displays the source PDF, reconstructed table grid, and field-level JSON together; immutable decisions produce a separate corrected candidate. The existing Prolog output remains a review candidate; active RAG and executable Prolog require later source and rule approval.

**Tech Stack:** Existing Python 3.13, Docling 2.129.0, Typer, pytest, Docker Compose tools profile. Bridge to Phase 1 contracts when they exist. No new database, model, or frontend dependency in this workstream.

**Spec:** `plans/phase2_jsonifier_integration_plan.md` (earlier prospectus design), `plans/CODEX_HANDOFF_prospectus_extractor_phase2_2026-09-26.md` (later corpus evidence), and master plan §§6–7, 11 (`plans/master_implementation_plan_original_long.md`). These documents are inputs to this draft, not new instructions or approval from the user.

**Scope boundary:** This is a complete draft for the **prospectus workstream**, not for all of master Phase 2. The master also covers other authorized policies, photographs/scans, OCR verification, and generic chunking. Finishing this workstream alone does not complete Phase 2 or permit Phase 3 advancement.

## Global Constraints

- Phase 0 is complete. The user authorized prospectus JSONification, candidate Prolog generation, validation, and local human review to proceed in parallel with incomplete Phase 1 indexing. Keep `plans/INDEX.md`'s formal phase order intact; Phase 1 source contracts are a prerequisite to active institutional release, not to review-only preparation.
- The original PDF bytes and their SHA-256 are authoritative for extraction. A raw Docling JSON file or `_essentials.json` is never an authorized substitute for a fresh source-PDF regression.
- Keep extraction audit, human field review, and issuing-office/version verification as separate states. The extractor's `promotion_status: "VERIFIED"` means only that its own audit passed.
- Store institution-supplied PDFs and generated artifacts outside Git unless their storage and redistribution are explicitly authorized. Preserve the newly copied, ignored 39-PDF dataset without committing or deleting it.
- Preserve the dirty parser and handoff file already present on `dev`; reconcile their diff and source before editing. The repo parser and dataset extractor were text-identical at this review, but the repo version is uncommitted.
- Canonical extracted text must preserve source meaning; advising summaries are separate and must cite all supporting source spans. No embedding/vector write or active Prolog release is a Phase 2 exit condition.
- The current Docling profile has OCR off. Scanned or mixed pages require a separately validated OCR path under the master plan; do not claim this parser supports them.
- The human review GUI is required as a researcher-operated local tool because the current web app has no reviewer authentication. No public review endpoint exists without authentication and authorization.

## Scope decision and design alternatives

The approved scope is the **prospectus portion of Phase 2**: finish and integrate its already-prepared JSONification and candidate Prolog generation, then add human correction. Phase 1 source indexing can continue in parallel. This plan does not replace the master Phase 1–13 roadmap.

| Approach | Result | Tradeoff |
| --- | --- | --- |
| **A. Pilot, stage, then full reference (provisional recommendation)** | Check two representative PDFs against source pages, repair critical failures, integrate a review-only adapter and manual flagger, then finish the 39-distinct-PDF gold set before any accuracy or release claim. | Researchers can review in Bintanong sooner; staging must be visibly segregated from active knowledge. |
| B. Full reference before integration | Check all 39 distinct PDFs first, then add Bintanong integration. | Stronger extraction baseline before integration; delays the review workflow that helps create that baseline. |
| C. Direct import of current `_essentials.json`, `.pl`, or JSONL | Fastest file copy. | Reject: known wrong course fields, incomplete prerequisites, and no independent source/version approval could become active facts. |

The earlier Phase 2 plan calls for a two-PDF pilot before API integration. The later handoff documents a 44-path batch and calls for a 39-distinct-PDF reference set. The user asked to reconcile them and made human correction in a GUI mandatory. The two-PDF pilot establishes parser defects and GUI behavior; the GUI then supports review of all 39 distinct PDFs. The full reference set gates any field-accuracy percentage or general release claim.

## Master-plan alignment

The master plan now permits prospectus preparation beside Phase 1 indexing, while keeping verification mandatory for active use. It makes a **local researcher GUI** a Phase 2 preparation tool, not a public administrative dashboard:

- Master §7.1 requires original PDF, reconstructed Docling table, and candidate JSON comparison, with accepted/corrected/unresolved decisions that preserve raw evidence.
- Master §7.3 names the decision ledger and corrected candidate JSON as deliverables; unresolved critical facts stay out of rule authoring. The 39-distinct-PDF reference set supports corpus accuracy claims.
- Master §16.1 distinguishes the required local review GUI from a hosted reviewer UI, which requires authenticated identities, authorization, and private source-file access controls.

The user approved this plan with the explicit correction that Phase 1 completion must not block review-only prospectus work. The master plan was updated narrowly to record that parallel path while retaining source approval as an active-release gate.

## File ownership and interfaces

| Path | Responsibility |
| --- | --- |
| `backend/bintanong_tools/bintanong_jsonifer_prolog/bintanong_prospectus_jsonifier.py` | Existing Docling conversion, canonical cell evidence, course parsing, audit, and candidate projections; fix defects at the first boundary that loses source meaning. |
| `backend/bintanong_tools/prospectus.py` (new) | Small adapter: accept an original PDF and provisional source record, call the extractor, return a candidate run with explicit hash and statuses. Link the record to Phase 1 identity later. No release activation. |
| `backend/bintanong_tools/prospectus_review.py` and a small UI asset (new) | Serve a loopback-only PDF, reconstructed Docling table grid, audit issues, and editable candidate JSON. Persist reviewer decisions and render corrected candidates without modifying raw extraction. |
| `backend/bintanong_tools/ingest.py` | Add `prospectus` command without changing the generic `parse` command's meaning. |
| `compose.yaml` | Add read-only institutional PDF input mount and separate writable review output mount for the tools profile. Do not add a public review service. |
| `tests/test_prospectus_*.py` | Small focused regressions for parser evidence, trust boundary, cache/output safety, reviewer decisions, provenance, and CLI. Reuse selected dataset fixtures after checking they contain no restricted PDF content. |
| `plans/plan_current_progress/` | Running checkpoint for this parallel prospectus workstream. Formal Phase 2 artifacts still follow the phase contract when Phase 1 completion permits phase advancement. |

**Adapter input:** `pdf_path: Path`, `output_dir: Path`, and a provisional source record containing the PDF SHA-256 and its local source locator. Issuer, campus/college/program scope, document version, and verification state may be unknown until Phase 1; keep them null/pending, not inferred as approved. The adapter verifies the bytes against the record and later maps it to Phase 1 `SourceDocumentVersion`. It never derives authority from filename or the parser's hardcoded campus.

**Adapter output:** a candidate-run manifest with provisional source ID, optional approved source/version ID, PDF SHA-256, extractor/schema/config versions, paths and hashes of raw Docling/evidence/essentials/review artifacts, extraction audit state, content-review state, and source-verification state. Review decisions are keyed to `(pdf_sha256, course locator, field)` plus reviewer; a changed PDF hash invalidates their applicability. A corrected JSON candidate is deterministically materialized from the immutable extraction plus decisions, rerun through relevant structural checks, and retains links to the original field/cell. When Phase 1 contracts arrive, add a mapping without discarding review history.

## Review Focus

1. Same filename, changed PDF bytes: cache and prior review decisions must not silently apply. Covered by Task 4 and Task 5 tests.
2. Audit pass with unresolved prerequisite, standing condition, or guessed metadata: must remain ineligible for executable rule release. Covered by Task 3 tests.
3. Docling conversion fails after an earlier successful run: prior accepted artifacts remain intact and failed diagnostics stay review-only. Covered by Task 4 test.
4. A merged source cell contains two course codes: no course may be silently lost or fabricated; the affected row stays flagged until PDF-backed resolution. Covered by Task 2 tests.
5. Course or summary chunk cites the wrong edition/page or omits a supporting cell: reject it as a release candidate. Covered by Task 6 tests.

## Work order and checkable tasks

### Task 0: Snapshot and protect provisional sources

**Files:** `backend/bintanong_tools/prospectus.py` for the provisional record, `tests/test_prospectus_sources.py` for its boundary check, `plans/plan_current_progress/current_progress.md`, and a local source inventory outside Git or under the ignored dataset folder.

**Interface produced:** `ProvisionalSource(pdf_sha256: str, source_locator: str)` in `backend/bintanong_tools/prospectus.py`, with `source_verification` fixed to `"pending"`, plus `verify_pdf(pdf_path: Path) -> None` that raises `ValueError` on a hash mismatch. It can be linked to a later Phase 1 `SourceDocumentVersion` without changing its hash or review decisions.

- [ ] Preserve the already-dirty parser, `.gitignore`, and untracked handoff; record their diff/status before implementation. Verify the 39 ignored PDFs match the 39 unique hashes in the external 44-path corpus.
- [ ] Define and test the minimal provisional record interface above. Reject a declared hash that disagrees with the bytes; do not accept a filename or the extractor audit as source approval.
- [ ] Keep the local record and generated evidence outside Git by default. Record which fields are still unknown; do not fill issuer, scope, or approval from directory names.

**Gate:** The review-only pipeline can operate on exact PDFs without invented authority. No provisional record is eligible for active institutional use. Phase 1 indexing remains separate work and can later bind approved identity to these hash-keyed records.

### Task 1: Establish the PDF-checked baseline

**Files:** Original PDFs and review artifacts in the external dataset workspace; new regression/gold files under a separately approved test-data location. Keep private or redistribution-restricted PDF bytes out of Git.

**Consumes:** Task 0 provisional source inventory and the current `v5_final_cross_college_2026-09-26` batch manifest.

- [ ] Record the current repo parser diff, normalized text equality with the dataset extractor, Python/Docling/`docling-parse` versions, and the 80-check self-test result in a baseline report. Re-run tests rather than inheriting the handoff's result.
- [ ] Re-run original BSCS and Architecture PDFs using the current parser and compare every course row with the visible PDF: code, title, year, term, units, raw and resolved prerequisites, standing, elective scope, page, cell IDs. Classify wrong printed source totals separately from parser errors.
- [ ] Build a field-level discrepancy ledger with PDF hash/page/cell, observed value, correct or unresolved reading, defect class, and review disposition. Start the 39-unique-PDF reference set with Values Education, both Psychology tracks, Engineering, BSBA Marketing, Midwifery, old ComSci, and source-total conflicts.
- [ ] Count missed courses, false courses, and exact critical-field matches separately. Report denominators. Do not call `7/44` an accuracy rate.

**Check:** A second reviewer can locate each pilot finding in its original PDF. No unresolved critical field is labeled correct. The 44 source paths remain in the later regression batch even though five pairs have identical hashes.

### Task 2: Repair only demonstrated extraction defects

**Files:** Existing extractor and `tests/test_prospectus_parser.py`; selected existing dataset fixtures may be adapted into repo tests.

**Consumes:** Task 1 discrepancy ledger and raw Docling cell topology.

**Produces:** More accurate candidates or a visible audit issue where the source cannot be read unambiguously.

- [ ] For each defect class, add one small regression using the original cell/row topology; confirm it fails on the present code. Start with merged-code cells and title/prerequisite spillover in Values Education and Psychology.
- [ ] Fix the earliest responsible parser boundary (`evidence_adapter`, table/section assembly, candidate finalization, or audit), without degree-specific correction tables or invented prerequisite text.
- [ ] Compare fixed rows with the source PDF, run the focused test and all 80 self-checks, then rerun the affected original PDF. Preserve unresolved cases as review issues.
- [ ] After each shared parser fix, rerun the 44-path original-PDF batch with `--force`, compare audit states and field-level reference values with the prior manifest, and report newly repaired and newly broken fields.

**Gate:** Pilot critical mismatches are correct or explicitly blocked. The complete 39-PDF reference set remains required before general accuracy and release claims.

### Task 3: Bind audit to source identity and rule coverage

**Files:** Existing extractor, new adapter, `tests/test_prospectus_authority.py`.

**Consumes:** Task 0 provisional source record and Task 2 candidate facts; optionally the approved Phase 1 identity when available.

**Produces:** Distinct `extraction_audit`, `content_review`, and `source_verification` states in the candidate-run manifest. Existing extractor output can retain its legacy `promotion_status` for compatibility, but loaders must not treat it as release approval.

- [ ] Add failing tests for mismatched declared scope when an approved identity exists, pending identity, hash mismatch, unreadable prerequisite cell, unresolved prerequisite token, standing-only condition, and `OR`/exception text. Assert each blocks active eligibility even if the extractor's audit says `VERIFIED`.
- [ ] Treat the current `"Tiniguiban - Main"` default and path-derived program as candidate observations. Preserve original text and evidence; compare them with approved Phase 1 identity when available. Pending identity remains pending, not a parser error.
- [ ] Distinguish explicit reviewed empty prerequisite from missing/unreadable content; retain unresolved external-course references and standing conditions. Do not map unknown to zero prerequisites.
- [ ] Keep generated `.pl` candidate-only and `eligible/2`/`next_eligible/2` out of active use until Phase 6 establishes complete semantics, coverage, tests, and approval.

**Gate:** A machine audit pass alone cannot authorize a curriculum, RAG assertion, or executable eligibility result.

### Task 4: Make conversion, cache, and output publication safe

**Files:** Existing extractor, adapter, `tests/test_prospectus_runs.py`.

**Consumes:** Hash-checked original PDF bytes and Task 3 status contract. Institutional verification may still be pending.

- [ ] Add failing tests for changed PDF bytes at the same path, stale/unversioned raw Docling cache, `--skip-existing` after failed audit, and conversion error after a prior successful run.
- [ ] Include PDF SHA-256 plus conversion-affecting settings and parser/schema versions in run/cache identity. Validate the original PDF before reuse; cached raw JSON without its verified PDF remains review input only.
- [ ] Stage new outputs in a run-specific temporary directory. Publish a complete candidate set only after conversion and audit finish; keep failures in a separate diagnostic location. Never delete previous accepted outputs before attempting conversion.
- [ ] Make noninteractive critical or authorization failures return nonzero; never leave a stale `.pl` or `_rag.jsonl` looking current. Keep `_essentials.json` review-only when audit fails.

**Gate:** Repeat runs of unchanged input are stable; changed input invalidates the cache; failures preserve earlier accepted artifacts and produce diagnostics.

### Task 5: Build the human correction GUI

**Files:** `backend/bintanong_tools/prospectus_review.py`, a minimal local UI asset, `tests/test_prospectus_review.py`.

**Consumes:** Task 4 candidate run, raw Docling table/cell geometry, detailed audit, original PDF, and a locally recorded reviewer identity. The GUI is required and runs locally for this workstream; a hosted reviewer UI is outside this plan.

- [ ] Add failing tests that a decision records reviewer, time, reason, PDF hash, course/field locator, original candidate value, selected disposition/correction, and linked PDF page/cell; changing the PDF hash makes the decision inapplicable.
- [ ] Show three synchronized views: the actual PDF page; a reconstructed prospectus table using Docling row/column spans, banners, cell text, and available bounding boxes; and the extracted JSON fields. Selecting a JSON field highlights its supporting cell/page, and selecting a flagged cell opens affected JSON. When no trustworthy box exists, show the page/cell locator without a false visual highlight.
- [ ] List all audit anomalies and unclaimed source candidates, including issues absent from `_review.csv`. Support accepted, corrected, and unresolved decisions per critical field, with an explicit reason and reviewer. Serve only on loopback or as an offline local artifact unless authenticated web review is chosen; reject paths outside selected roots.
- [ ] Record decisions separately from raw extraction and retain their history. Materialize corrected JSON from the raw candidate plus applicable decisions; rerun duplicate-code, unit, term, and prerequisite checks before marking content review complete. A correction never overwrites the raw candidate or proves issuing-office/version approval.
- [ ] Verify the full GUI path on Values Education `Ed 12`/`FS 2`, Psychology `Psych 9`/`Psych 10`, and one source-total conflict. The reviewer must be able to split/repair a course only when source cells support it, or leave the issue unresolved without guessing.

**Gate:** A reviewer can compare the PDF, reconstructed layout, and extracted JSON; correct or reject wrong fields; and export a traceable corrected candidate. Another run with different PDF bytes cannot silently inherit the decision.

### Task 6: Emit source-linked candidate chunks

**Files:** Existing extractor, adapter, `tests/test_prospectus_chunks.py`.

**Consumes:** Source span fields from the extractor and Task 5 corrected candidates/review dispositions. Map to Phase 1 `SourceSpan`/`Chunk` contracts when available.

- [ ] Add failing tests for two editions of the same course, repeated run timestamps, multi-page/summary chunks, and prerequisite assertions with missing source cells.
- [ ] Carry source version, PDF SHA-256, page, table index, cell IDs, and canonical text into every course chunk; include all contributing spans for term/elective/overview summaries. Do not fabricate a single page for a multi-page source.
- [ ] Make chunk IDs stable from source version, source locator, content hash, and chunker version. Keep canonical source text separate from advising-style summary text.
- [ ] Build candidate chunks from the reviewed/corrected projection, never from a superseded raw field. Reject chunks with unresolved source spans or unreviewed critical assertions as active candidates. Keep the chunk artifacts offline in Phase 2; Phase 3 and Phase 4 own embeddings and storage.

**Gate:** Every sampled candidate chunk, and every pilot chunk that asserts a prerequisite or standing condition, resolves to the correct original PDF text and version.

### Task 7: Expose and verify the Bintanong tools boundary

**Files:** Adapter, `backend/bintanong_tools/ingest.py`, `compose.yaml`, `tests/test_prospectus_cli.py`, and repo-facing run instructions.

**Consumes:** Tasks 3–6 candidate run/review outputs.

- [ ] Add failing CLI/API equivalence tests for the same source identity and PDF. Ensure the existing generic `parse` command still passes its contract test.
- [ ] Add `prospectus` to Typer as a review-only command; require a provisional source record and original PDF. Make missing Docling, missing input, hash mismatch, and denied source state actionable failures.
- [ ] Mount original PDFs read-only and candidate outputs read/write in Compose. Verify the command shape against the actual service: `docker compose --profile tools run --rm ingest python -m bintanong_tools.ingest prospectus --help`, because the service has no entrypoint.
- [ ] Document the local reviewer flow, output statuses, unsupported scanned PDFs, and the boundary to later release authoring. Keep no institution PDF or generated corpus in Git by default.

**Gate:** Host API and container CLI produce equivalent candidate facts for one pilot PDF and setting set; neither path activates RAG, Prolog, or a Supabase release.

### Task 8: Finish reference review and prospectus workstream handoff

**Files:** Field-level reference/measurement report outside Git if restricted, sanitized summary under `plans/` or `docs/`, and the active Phase 2 checkpoint once Phase 2 starts.

- [ ] Complete source-PDF field review across all 39 distinct hashes; run all 44 paths to catch path-dependent metadata behavior. Resolve duplicate-pair discrepancies and classify remaining unreadable or conflicting source facts.
- [ ] Re-run focused repo tests, the extractor self-test, the original-PDF batch, host/API and container CLI checks, and one failure-injection rerun. Record versions, parser commit, source hashes, commands, results, and unsupported layouts.
- [ ] Report course recall/false positives and critical-field exact match with explicit denominators; keep audit pass count, human-review completion, and source authorization as separate columns. Do not claim the desired 90–95% figure without reference evidence.
- [ ] Update the formal Phase 2 checkpoint after verified work and write a prospectus workstream report. Write a final Phase 2 handoff only after the master plan's other ingestion/OCR/chunking requirements also pass; validate phase artifacts with `phase_state.py validate` and `can-advance` before advancing to Phase 3.

**Prospectus workstream gate:** Reviewed candidate text and chunks are traceable to exact original PDF hashes and provisional source records; critical extraction uncertainty is blocked; cache and rerun safety are demonstrated; the researcher can review defects; no unreviewed critical field reaches rule authoring. Linking those records to approved source versions is a later release gate. This workstream ends before embeddings, vectors, and live eligibility rules. The full Phase 2 gate still requires the other source types and OCR verification named by the master plan.

## Execution method and dependencies

The user approved this workstream plan for execution in parallel with incomplete Phase 1 indexing. Use superpowers:subagent-driven-development with a fresh implementer and reviewer per independent task; Task 2's parser fixes may be dispatched one defect class at a time. Preserve an execution ledger and update `plans/plan_current_progress/current_progress.md` after each verified task. When Phase 1 later permits formal Phase 2 advancement, incorporate verified results into the phase checkpoint rather than repeating them.

**Release boundary:** The parallel work can parse, generate candidate Prolog/JSON, flag, correct, and test prospectuses now. It cannot activate an institutional RAG/Prolog release until Phase 1 verifies the applicable original document and version and Phase 6 approves rule semantics. The two-PDF pilot and 39-distinct-PDF reference set remain separate validation gates.
