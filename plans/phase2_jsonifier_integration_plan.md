# Phase 2 Prospectus JSONifier Plan — Validation Before Integration

**Status:** Draft for team review; no Phase 2 implementation or institutional ingestion is approved by this document.

**Prepared:** 26 September 2026.

**Code reviewed:** `dev` at `db756bde` (`bintanong_prospectus_jsonifier.py`, 6,230 lines).

**Depends on:** Phase 0 foundation (complete); Phase 1 source identity and contract decisions (pending).

**Scope:** The prospectus track of Phase 2 only. This plan does not edit or redefine the Phase 1 or master plans.

## Goal

Validate the existing Docling-based prospectus JSONifier against real PalSU PDFs, repair demonstrated extraction and audit defects, preserve source evidence through the generated chunks, and **then** expose it as a callable backend module. Passing the JSONifier's synthetic self-tests is a baseline, not a substitute for PDF-to-output review.

The previous draft assumed the parser and evidence gates were already stable and limited this phase to packaging. That assumption is too strong while the actual BSCS and Architecture PDFs still need a fresh run after the Codex outage. The first deliverable is a discrepancy report, not an importable `__init__.py`.

## Existing flow to preserve and verify

| Boundary in `bintanong_prospectus_jsonifier.py` | What it does | Risk to test |
| --- | --- | --- |
| `get_pipeline_options()` / `load_document()` | Converts a PDF through Docling or loads cached raw Docling JSON. | Wrong/missing tables, no OCR for scanned pages, stale cached conversion. |
| `evidence_adapter()` / `parse_curriculum_evidence()` | Retains canonical cells, finds structural tokens and year/term sections, assembles course rows. | Misassigned years/terms, wrapped fields, header or total-row contamination, unclaimed source courses. |
| `finalize_courses()` / `build_audit()` | Resolves prerequisite text, checks provenance and units, assigns audit status. | Unknown requirements or metadata receiving `VERIFIED` status. |
| `build_payload()` / `process_prospectus()` | Builds review JSON/CSV, optional Prolog and RAG JSONL, and batch outputs. | Missing source spans in chunks; review-only data mistaken for approved data; old outputs removed by a failed rerun. |

The script's `--self-test` currently reports **80/80 checks passed**. These include constructed/transcribed BSCS and Architecture layouts. No claim of real-PDF accuracy follows from that result. The actual authorized PDFs, their Docling outputs, and a human row comparison are required for the pilot gate.

## Code-derived review priorities

1. **Incomplete prerequisites and standing conditions.** `build_audit()` leaves unresolved prerequisite tokens as warnings, yet `warn` becomes `promotion_status="VERIFIED"`. `generate_prolog_knowledge()` emits only resolved `prerequisite/2` edges. Its `eligible/2` predicate checks those edges but does not check unresolved tokens or `standing_requirement/2`. The current `.pl` must be treated as a **candidate**, never a student-facing eligibility authority. Phase 2 must expose missing/unknown coverage; Phase 6 owns the approved rule semantics and release.
2. **Metadata authority.** `resolve_metadata()` currently sets `campus` to `"Tiniguiban - Main"` and derives other fields from a path, document head, and optional semantic Markdown. Missing program, college, or school year produces warnings, which can still yield `VERIFIED`. Match extraction metadata to the Phase 1 approved source identity; do not let a guessed or absent value authorize a curriculum.
3. **Course-to-chunk provenance.** `_make_provenance()` records source cell IDs, table index, page, and bbox. `build_semantic_rag_chunks()` emits an advising summary with IDs such as `<course-code>::course` and a source filename, but lacks the source version and the course's page/cells. A type annotation cannot reconstruct provenance after it has been dropped.
4. **Stale or displaced output.** `_docling_runtime_fingerprint()` omits the input PDF hash, `--skip-existing` checks output existence, and `process_prospectus()` unlinks old outputs before converting. A revised PDF at the same path or a failed rerun can produce the wrong state. `_essentials.json` is written on an audit error; it must remain review-only in that case.
5. **Docling profile scope.** `get_pipeline_options()` sets `do_ocr=False` and `force_backend_text=True`. The current profile is for born-digital prospectuses. Scanned or mixed pages require detection and a separately validated OCR path; they cannot be silently counted as supported by this track.

## Phase 2 work order

### 1. Establish a real-PDF baseline

**Primary file:** `backend/bintanong_tools/bintanong_jsonifer_prolog/bintanong_prospectus_jsonifier.py`.

**Evidence:** Original authorized PDF (kept outside Git unless authorized), raw Docling JSON, audit JSON, grid dump, review CSV, and a discrepancy ledger.

- [ ] In the pinned environment, run the existing `--self-test` and record Python, Docling, and `docling-parse` versions. Keep the 80/80 result separate from live conversion evidence.
- [ ] Run the standalone JSONifier with `-i <PDF> -o <review-output.json> --export-csv --strict` on the BSCS PDF and the Architecture PDF previously affected by year misassignment. Keep the original source and the generated raw Docling JSON together with their hashes. Do not publish the resulting `.pl` or JSONL.
- [ ] Review **every course row in those two pilot PDFs** against the JSON/CSV: code, title, year, semester, lecture/lab/total units, raw prerequisite, resolved/unresolved tokens, standing condition, elective group, source page, and cell IDs. Check printed term/grand totals separately; matching totals do not prove that courses are in the right term.
- [ ] Group mismatches by cause and record PDF location, observed extraction, correct reading, and affected function. Include false year/semester banners, `TOTAL` rows, split/multiline fields, footnotes, elective options, missing course codes, and wrong page/cell references. Inspect the full pilot before deciding which defect class to fix first.

**Gate:** A discrepancy ledger exists for both real PDFs. Each critical field is either checked against its source, explicitly unresolved, or blocked. The pilot does not pass because the self-test passed.

### 2. Repair the earliest boundary that loses source meaning

**Code targets as indicated by the discrepancy:** `evidence_adapter()`, `tokenize_table()`, `build_curriculum_sections()`, `_assemble_section_candidates()`, `detect_source_course_candidates()`, `finalize_courses()`, `parse_elective_tracks()`, or `build_audit()`.

- [ ] For each confirmed defect class, add a minimal failing regression fixture that retains enough original Docling cell topology to reproduce it. Verify the failure before changing parsing logic.
- [ ] Correct the earliest failing boundary. Preserve the raw cell text, source cell IDs, and any structural decisions; do not add blanket defaults for an undetected year, semester, or prerequisite.
- [ ] Rerun the focused fixture, the full built-in self-tests, and the affected real PDF. Compare the actual rows again rather than relying solely on printed unit totals.
- [ ] If a course's source text is unreadable or ambiguous, retain that uncertainty in the audit. A semantic repair provider may suggest a candidate only if it cites source cells and passes deterministic validation; it cannot approve the institutional fact.

**Gate:** The pilot's critical extraction mismatches have been fixed or left visibly blocked, with a regression covering each fixed failure mode.

### 3. Separate extraction quality from rule coverage

**Code targets:** `resolve_metadata()`, `resolve_prerequisites()`, `build_audit()`, `build_payload()`, `generate_prolog_knowledge()`, `build_essentials()`.

- [ ] Require the caller's approved source identity and PDF hash for an institutional promotion decision; cross-check campus, college, program, and curriculum version against the PDF. Remove the hardcoded campus as evidence of authority. The Phase 1 contract supplies these values; this task does not change Phase 1.
- [ ] Distinguish at least: a reviewed empty prerequisite cell, an unreadable/missing cell, an unresolved course reference (including a possible outside-program course), and a separate standing condition. Preserve the original text in every case. Do not interpret an unmatched code as “no prerequisite.”
- [ ] If a course has unresolved prerequisites, standing conditions that require interpretation, or ambiguous `AND`/`OR`/exception text, block **that course's executable eligibility**. The other rows can remain candidates for review. Keep `eligible/2` and `next_eligible/2` out of a live Prolog release until the Phase 6 rule gate addresses complete coverage and semantics.
- [ ] Make audit errors, source authorization, and human review distinct fields. A machine `warn` is not human approval. Mark failed-audit `_essentials.json` and other portable outputs review-only, and make the noninteractive ingestion path return nonzero on critical or authorization failures.

**Tests:** Unresolved token with no resolved edges; a standing-only condition; verified no prerequisites; absent or unreadable prerequisite cell; `OR`/exception text; wrong campus; missing source identity. Assert that none can be promoted as a verified eligibility decision.

**Gate:** No unreviewed or incomplete requirement can yield a live `eligible` result. The JSON retains enough source text and status for Phase 6 reviewers to resolve it.

### 4. Carry provenance into candidate RAG chunks

**Code targets:** `build_semantic_rag_chunks()`, `build_hierarchical_rag_chunks()`, `build_payload()`; Phase 1 `SourceSpan`/`Chunk` contracts once available.

- [ ] Attach approved document version, PDF page, table index, source cell IDs, and original text to each course chunk. A term overview or elective-pool chunk should list **all** source spans used for its generated summary.
- [ ] Derive stable IDs using source version, source locator, content hash, and chunker version. Two editions of the same course must not share the same chunk ID. A repeated run of unchanged input should preserve IDs even if its run timestamp changes.
- [ ] Keep canonical extracted text distinguishable from advising-style summary text. A chunk without a resolvable source span stays in review; do not fabricate a page for a multipage or nonhighlightable source.

**Gate:** Sample every chunk type, and check all pilot chunks that assert prerequisites or standing conditions against exact PDF pages/cells. No embedding call or vector write is needed for this gate.

### 5. Make file runs repeatable, then integrate the API

**Code targets:** `load_document()`, `process_prospectus()`, `run_batch()`, CLI wrapper; later `backend/bintanong_tools/ingest.py`, `compose.yaml`, and a new package `__init__.py`.

- [ ] Include source PDF SHA-256 and conversion-affecting Docling settings in cache identity. `--skip-existing` must check source hash, schema, and audit/review status instead of file existence alone. Cached Docling JSON without its verified source PDF is a review input only.
- [ ] Stage a run's outputs and publish only after conversion and audit succeed. Preserve previously approved outputs on an exception. Write failed-run diagnostics to a separate review location; do not expose stale `.pl` or JSONL.
- [ ] Make `load_document()` and `build_payload()` callable with explicit source identity and configuration while keeping the standalone Windows CLI. Export a small public API and wrap the existing 80-check suite in pytest alongside focused new tests. Avoid a broad rewrite of the 6,230-line module.
- [ ] Only after the pilot gates pass, add `prospectus` to the Typer CLI. For Docker tests, mount input PDFs read-only and outputs separately. The current Compose `ingest` command is `python -m bintanong_tools.ingest --help` with no entrypoint: use `docker compose --profile tools run --rm ingest python -m bintanong_tools.ingest prospectus --help`, or change and verify the entrypoint. The current generic parser's PDF-byte fallback is not an authorized institutional ingestion route.

**Tests:** Same filename with changed PDF bytes; stale/unversioned Docling cache; skip of a failed audit; Docling error after a prior successful output; CLI/API equivalence; absent Docling; container input mount and command help.

**Gate:** The API and CLI yield equivalent candidate values for the same PDF and settings. Changed inputs invalidate cache; failed runs leave earlier approved artifacts intact.

## Exit gate and handoff

- [ ] The two real pilot PDFs have complete row-level review results, with critical discrepancies fixed or visibly blocked. Generalization beyond these layouts remains a separate claim requiring more documents.
- [ ] The JSONifier self-tests and focused new regressions pass in the pinned environment. A real Docling conversion and human PDF comparison are recorded separately.
- [ ] Rule-critical uncertainty never appears as a verified eligibility decision; generated Prolog remains a candidate for Phase 6 review.
- [ ] Candidate RAG chunks resolve to the right authorized PDF version, page, and source cells; stable IDs distinguish curriculum editions.
- [ ] Cache reuse, batch skipping, and failed reruns cannot publish stale data or remove a prior approved output.
- [ ] The containerized CLI and callable module work with a mounted input PDF. The phase succeeds without embeddings, vectors, or Supabase writes.

The handoff records tested PDF hashes, Docling settings, exact commands, self-test results, discrepancy ledger, critical-field review disposition, known unsupported layouts, and open issues. Scanned or mixed-content prospectuses stay explicitly **unsupported by this born-digital profile** until a separately tested OCR workflow passes the master plan's documented check.

**First action when Codex is available again:** rerun BSCS and Architecture through the present script, review all rows against the PDFs, and let the observed failure patterns set the parser-fix order. Do not start with `__init__.py` or the Docker command.
