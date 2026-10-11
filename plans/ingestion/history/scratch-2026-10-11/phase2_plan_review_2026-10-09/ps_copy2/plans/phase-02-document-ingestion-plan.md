---
artifact: phase-plan
phase: 2
status: ready
preparation_only: true
master: plans/master_implementation_plan_original_long.md
previous_handoff: plans/phase-01-handoff.md
---

# Phase 2 — Document ingestion beyond prospectuses

Base commit `00f1fb1`. Preparation only: implementation needs the owner's review of this plan and a formal start through the handoff skill.
Nothing here is institutional approval. Audit success, EXTRACTED, VERIFIED and content review never approve a source or a curriculum.
Anything not run is marked NOT RUN.

## Goal and context

Master section 7 (7.1 steps 1-9, 7.2 chunk policy, 7.3 ten-scanned-document check): source-linked candidate text, chunks and an ingestion report
from the institutional originals, with no embedding, vector write, executable Prolog or runtime routing change.

- Input: 78 originals under `E:\Bintanong\institutional-sources\originals`, enumerated read-only (names, counts, extensions): 59 PDF, 17 JPG, 2 PPTX, longest path 220 characters.
  Folders: Citizens Charter 8 (6 PDF, 2 PPTX), Memos 6 JPG, Procedures 16 (5 PDF, 11 JPG), Student Handbook and Constitutions 4 PDF, prospectus dump 44 PDF.
- Byte identities (63 unique, 13 duplicate groups, four identical 2025 Charter PDFs) come from the external inventory and are NOT re-verified by this plan; Task 2 re-hashes them.
- The 44 prospectus PDFs belong to the parallel prospectus workstream: Task 2 counts them separately; no task here converts them.
- Output is candidates only: every source stays verification pending, approval null. Issuer, scope, effectivity, supersession and conflicts need authorization evidence not yet supplied.
  CSG evidence is missing and is never inferred from USG.
- Consumed from Phase 1: `backend/bintanong_contracts` (SourceSpan, Chunk, SourceDocumentVersion, `check_chunk_binding`), `knowledge/manifests/governance-vocabulary.json`,
  `evaluation/README.md`.

## Global constraints

- Work only in a worktree under `Bintanong-wt`; the owner checkout keeps its 9 known entries. No push, PR, merge, force-push, history rewrite, or movement of local `dev` or `origin/dev`.
- No attribution trailers; text names "the owner", never an automated actor. No integration-branch merge, OCR-branch merge, GUI acceptance, Docker or compose change.
- Originals and dump folders are read-only. Reports, hashes with local paths, references, converted JSON and OCR output stay outside Git under `$S`.
  Git gets code, tests, synthetic fixtures built in `tmp_path`, plans and decision records.
- No installs, venv syncs, downloads, or changes to `backend/pyproject.toml` or any `uv.lock`. Python only as `py -3.13`; pytest only with `-p no:cacheprovider --basetemp "$S\bt_<name>"`.
- No source approval or activation, no CSG inference, no embeddings or vector writes, no executable Prolog or rule activation, no routing change.
- Phase F adapter and prospectus command are not implemented; not a prerequisite. First inspection uses `InputSnapshot`/`file_sha256`, an explicit input root and an output folder outside
  Git.
- The owner's uncommitted edits to `identity.py`, `pipeline.py` and `publish.py` are not in the base. `prospectus_extractor/` is imported, never edited.
- Environment (py -3.13 metadata): Docling 2.129.0 installed vs 2.133.0 pinned (`backend/pyproject.toml:30`); pypdfium2 5.9.0, Pillow 12.3.0, python-pptx 1.0.2, pypdf 6.13.1.
  pypdf is installed but neither declared nor in `uv.lock`; python-pptx and Pillow are in `uv.lock` only through docling. Default: pypdfium2, Pillow, python-pptx; never pypdf.
- Every task: each red test is seen failing for the stated reason, then passing; then the named mutants each fail at least one named test (scratch copies, one mutant at a time).

## Repository boundaries

- Code: `backend/bintanong_tools/ingest.py` (Task 1 only, still one Typer command) and a new package `backend/bintanong_tools/document_ingest/`, one module per task, created when the task
  starts (no empty modules).
  Contracts stay untouched unless owner decision 1 is accepted. Layout follows `ocr_bench/` (package under `bintanong_tools`, flat tests); master section 20's `backend/app/ingestion/` does
  not exist.
- Tests and fixtures: flat `tests/test_*.py` importing `backend.bintanong_tools...`; fixtures built in `tmp_path` with reportlab, Pillow and python-pptx; no institutional bytes in Git.
- Docs and outside Git: one `docs/decisions/phase-02-*.md` record per task; no new schema; reports, manifests and converted data under `$S`.

## Task checklist

- [ ] 1. Harden `ingest.py` (starts after the owner answers harden-vs-retire, or proceeds with the labelled default harden).
- [ ] 2. Read-only inspection of the 78 originals.
- [ ] 3. Handbook editions, USG constitution and Election Code candidates.
- [ ] 4. Charter, procedure and form candidates (PDF and the two PPTX).
- [ ] 5. Policy chunks, ingestion report and pending source-register records.
- [ ] 6. OCR extraction runner and the ten-document OCR gate.
- [ ] 7. Independent Spec then Standards reviews, gates, honest handoff.

### Task 1. Harden ingest.py

- Purpose: no path returns text without a Docling conversion, a digest and a real page count. Default design; if the owner chooses retire, this becomes removal of `parse_document` and the
  CLI body.
- Files: `backend/bintanong_tools/ingest.py`, `tests/test_ingest_hardening.py`, `docs/decisions/phase-02-ingest-hardening.md`.
- Reuse (verified): `docling_env.get_shared_converter` (`docling_env.py:219-245`) with `identity.conversion_settings()` (`identity.py:85-99`, OCR off), `DoclingUnavailable`
  (`docling_env.py:18`),
  `InputSnapshot` and `verify_unchanged` (`identity.py:37-58`). New: suffix check, zero-page and empty-text refusal, JSON-only stdout.
- Current defects: `ingest.py:36-37` falls back only on ImportError; `:44` regex-scrapes `(..) Tj`; `:51` reads with `errors="ignore"`; `:52-58` returns `text_extracted`, `num_pages` 1, no
  digest;
  `:33` `or 1`; `:25-26` raw default `DocumentConverter()`; `:34,57` `str(path)` in output. Importers: `tests/test_tools_contract.py:9,17-25,37-46`,
  `tests/test_scaffold_contract.py:23,60-61`,
  `compose.yaml:92-104`, `docker/ingest.Dockerfile:10`; nothing else.
- Preserve: module path, `parse_document`, `--help`, keys `title/text/num_pages/metadata`, `-o/--output`, one command (`ingest PATH`). Deliberately change: fallback removed, PDF only,
  `format` always `docling_markdown`, added `sha256` and `conversion_identity`, `metadata.source` becomes a plain file name.
- Red tests:
  - Docling unavailable (`docling_env.load_docling` patched to raise `DoclingUnavailable`) raises it and returns nothing.
  - A missing path raises `FileNotFoundError`; a directory, `.txt`, `.docx` and `.jpg` raise `UnsupportedDocument`; the suffix check is case-insensitive, so `.PDF` is accepted.
  - Garbage bytes named `.pdf`, a zero-page result, or empty extracted text raise; no result ever has `text_extracted`, a forced `num_pages` of 1, or a missing digest.
  - The result `sha256` equals `file_sha256`; a stub converter that changes the input mid-run makes the call raise through `verify_unchanged`.
  - `ingest PATH` stdout is JSON only: `docling_env.py:192,195,198` print to stdout, so conversion output is redirected to stderr inside `ingest.py` without editing `prospectus_extractor`.
  - `--help` works with Docling blocked from import, and `ingest.py` uses relative imports (the container runs `bintanong_tools.ingest`, tests run `backend.bintanong_tools`).
  - `tests/test_tools_contract.py` still passes; its synthetic-PDF test runs real Docling on the 2,691-byte fixture (NOT RUN until executed).
- Mutations (guards): refusal replaced by a fallback; suffix allowlist dropped; `verify_unchanged` removed; stdout redirect removed. Four mutants, each failing a named test.
- Gate: `py -3.13 -m pytest -q tests\test_ingest_hardening.py tests\test_tools_contract.py tests\test_scaffold_contract.py -p no:cacheprovider --basetemp "$S\bt_ingest"` shows zero failures.
- Exit: those tests pass; 4 of 4 mutants killed; the decision record lists preserved and changed items. Compose run of the `ingest` service: NOT RUN.
- Stays pending: owner ruling on harden vs retire; Docker and Linux behavior.

### Task 2. Read-only inspection of the 78 originals

- Purpose: master 7.1 step 2 for every original; independent of `ingest.py`.
- Files: new `document_ingest/inspection.py` (argparse entry `python -m backend.bintanong_tools.document_ingest.inspection --root <originals> --out <new or empty folder>`),
  `tests/test_document_inspection.py`, `docs/decisions/phase-02-inspection.md`.
- Reuse: `identity.file_sha256`/`bytes_sha256` (`identity.py:23,33`); `publish.write_text_lf` (`publish.py:54`); pypdfium2 (already used at `ocr_bench/simulate.py:108`,
  `prospectus_review_gui/render.py:113`):
  page count, `get_page_label`, text-layer length, image objects, `get_formtype`; Pillow decode check; python-pptx slide, table and picture counts. New: all classification and reporting.
  Docling is not run.
- Per file: root-relative path (private report only), size, SHA-256, magic bytes vs extension, health (`ok`, `unreadable`, `encrypted`, `zero_pages`, `extension_mismatch`,
  `path_unreachable`; class names only).
  PDF page class by text-layer characters: `native` at 100 or more, `scanned` below 20 with at least one image object, `blank` below 20 with none, otherwise `unknown`.
  Document class: `native` if all non-blank pages are native, `scanned` if all are scanned, `mixed` if both occur, else `unknown`.
  Invariant checked per PDF: native + scanned + blank + unknown == page count == pypdfium2 page count.
- Language is `undetermined` for every file except where the document declares it: PPTX `core_properties.language` is `observed`; pypdfium2 `METADATA_KEYS` has no /Lang, so PDFs stay
  `undetermined`.
  `pdf_page_label` is what the PDF declares; the printed folio is `undetermined`; both fields are kept. Forms: `get_formtype()` recorded, `unknown` if the call fails.
  PDF table count is `not_determined` (needs Docling). Byte-identical files group by SHA-256 and keep every path as a locator; same name with different bytes stay two identities.
- Pilot candidates: a named category list written into the report and marked as candidates for the owner (each Handbook edition, USG constitution, Election Code, each PPTX, one JPG poster,
  one form,
  the 643-page proposal). No selection algorithm.
- Safety: `--out` must be new or empty, outside the repository and the originals root, else refuse. Files opened `rb`. A manifest (relative path, size, mtime_ns, SHA-256) is taken before
  and after;
  any difference fails the run. Report files are written first and a manifest with their digests last; no complete manifest means an incomplete run. Report names are fixed leaf names.
  A path over 260 characters is a `path_unreachable` finding and a non-zero exit.
- Red tests (synthetic trees):
  - Counts by extension; each health class: truncated PDF, zero-page PDF, PNG named `.jpg`, corrupt zip named `.pptx`, encrypted PDF built with reportlab (skipif reason "reportlab
    encryption unavailable").
  - Native vs image-only page classification and the invariant; duplicate grouping; two runs give byte-identical reports.
  - Originals read-only and unchanged; a file changed between manifests fails the run; a non-empty `--out`, and `--out` inside the root or repository, are refused.
  - A path over 260 characters through the extended-length prefix (skipif not Windows, reason "extended-length paths are Windows only"); the report holds no drive letter, user folder or
    source text.
- Mutations (guards): after-run hash comparison removed; `--out` allowed under the root; file opened for writing. Three mutants, each failing a named test.
- Gate: `py -3.13 -m pytest -q tests\test_document_inspection.py -p no:cacheprovider --basetemp "$S\bt_inspect"`, then the real run over `$R` (NOT RUN until executed) with before and after
  manifests equal.
- Exit: tests pass; 3 of 3 mutants killed; the real run reports 78 files = 59 + 17 + 2 and 78 of 78 hashes equal before and after.
- Stays pending: language of scanned files, PDF table counts, printed folios, scope and authority.

### Task 3. Handbook editions, USG constitution, Election Code

- Purpose: candidate units (scope, clauses, exceptions, spans, page labels) from the four PDFs in the Student Handbook and Constitutions folder: two Handbook editions, the USG constitution,
  the Election Code.
- Files: new `document_ingest/policy_text.py`, `tests/test_policy_text.py`, `docs/decisions/phase-02-policy-text.md`.
- Reuse: `loader.load_document_result` (`loader.py:393-494`) with explicit `raw_json_path` and `stage_dir` under `$S` and a caller-built `snapshot=`. With `raw_json_path` unset it writes
  beside the input
  (`loader.py:427,484-486`); with `stage_dir` set it skips `verify_unchanged` (`loader.py:481-482`), so the caller calls `snapshot.verify_unchanged()` itself and the before and after
  original hash gate also applies.
  `evidence_adapter` (`loader.py:166-241`) gives `text_items` (id `text-N`, page, bbox, origin, `raw_text` at `:200`), `tables` and `page_sizes`.
  Fall back to `get_shared_converter` plus a raw-JSON reader only if the adapter raises on Handbook tables (scratch spike first).
- New: spans built from `raw_text`, not the cleaned `text`: `chunking.spans_from_text_items` uses the cleaned text (`chunking.py:81`), `clean_str` rewrites dashes and superscripts
  (`text.py:18-28`),
  and `Chunk._anchored_rules` (`source.py:334-338`) requires `source_text` equal to the joined span text. Also heading path, clause and exception capture, printed page label
  (`make_span` leaves it None, `chunking.py:45`), scope capture, repeated header and footer detection.
- Rules: both Handbook files stay separate versions with no supersession field; scope is `observed` only when printed, else `not_stated`; USG units carry no CSG scope; Election Code issuer
  and effectivity stay pending.
  Repeated headers and footers (same normalized text in the top or bottom 10 percent of 3 or more pages) are recorded as omission records `repeated_header_footer` with full `raw_text` and
  page, never edited out of the original.
  A scanned page with no text layer yields an omission `scanned_no_text_layer`, never an empty-text success. The historical `_rag_index` Markdown and its token-overlap score are exploration
  evidence only.
- Red tests:
  - Heading path and clause order; an exception stays with its rule; negation, numbers, dates, en dash and superscript are identical in `source_text`; printed label captured with the
    physical page kept.
  - Two near-identical editions get distinct ids; no CSG field is ever set; furniture is recorded, not deleted; a text-layer-free page yields `scanned_no_text_layer`.
  - Every text item is in exactly one unit or one omission (units + omissions == text_items).
  - The test passes `raw_json_path` and `stage_dir` and asserts nothing is written next to the synthetic input; an input changed mid-run fails.
- Mutations (guards): cleaned text used for `source_text`; the units + omissions check removed; output written beside the input. Three mutants, each failing a named test.
- Gate: `py -3.13 -m pytest -q tests\test_policy_text.py -p no:cacheprovider --basetemp "$S\bt_policy"`, then the real run on the 4 PDFs (NOT RUN until executed) with original hashes equal
  before and after.
- Exit: tests pass; 3 of 3 mutants killed; the real run has units + omissions == text_items for 4 of 4 files and 4 of 4 original hashes unchanged.
- Stays pending: authorized issuer, scope, effectivity, supersession; missing CSG; human reading of candidates.

### Task 4. Charter, procedure and form candidates

- Purpose: candidates from the Charter and procedure PDFs and the two distinct Charter PPTXs; step order, office, requirements, fees and processing times only when printed.
  JPG posters are inspected only (Task 2); their extraction is Task 6.
- Files: new `document_ingest/procedure_text.py`, `tests/test_procedure_text.py`, `docs/decisions/phase-02-procedures.md`.
- Reuse: as Task 3 for PDFs. PPTX uses python-pptx or Docling's native PPTX backend (`InputFormat.PPTX` exists; `get_shared_converter` registers only PDF), an implementer choice, for slide
  index, shape id and text.
- Rules: byte-identical 2025 Charter PDFs are one identity with several locators; the two PPTXs (2,145,920 and 2,145,907 bytes) stay distinct versions; a blank form is a form artifact, not
  a policy rule;
  the 643-page BOR proposal is a curriculum-proposal candidate, not a proven Charter or approved curriculum.
- SourceSpan limit (verified): `SpanLocator.kind` is `table_cells`, `text_item`, `docling_ref` or `section` (`source.py:114-141`); `SourceSpan` has a physical page and no slide locator
  (`source.py:151-199`);
  there is no JSON schema for SourceSpan or Chunk; `docs/decisions/phase-01-consumer-inventory.md:36` lists it as a gap. A slide is never recorded as a PDF page.
  Until owner decision 1, PPTX units appear in the ingestion report as rejected with reason `pending_locator_contract`.
- Red tests: PPTX units ordered with slide index and shape id and no PDF `page`; two PPTXs differing in one slide are distinct versions; a form page is typed `form`, never `rule`; numbered
  steps keep order;
  a fee is captured only when present in `raw_text`; duplicate-PDF locators collapse to one identity; every PPTX unit is rejected with `pending_locator_contract`; units + omissions ==
  text_items per PDF.
- Mutations (guards): slide stored as `page`; the units + omissions check removed. Two mutants, each failing a named test.
- Gate: `py -3.13 -m pytest -q tests\test_procedure_text.py -p no:cacheprovider --basetemp "$S\bt_proc"`, then the real run (NOT RUN until executed).
- Exit: tests pass; 2 of 2 mutants killed; the real run has units + omissions == text_items for every converted PDF and 0 PPTX units carrying a PDF page.
- Stays pending: slide-locator ruling; issuer and effectivity of every Charter version; the proposal's status.

### Task 5. Policy chunks, ingestion report, pending register records

- Purpose: master 7.1 steps 1, 8, 9 and 7.2.
- Files: new `document_ingest/policy_chunks.py`, `document_ingest/report.py`, `document_ingest/register.py`; `tests/test_policy_chunks.py`, `tests/test_ingestion_report.py`,
  `tests/test_register_minting.py`; `docs/decisions/phase-02-policy-chunks.md`.
- Reuse by import: `Chunk`, `SourceSpan`, `SourceDocumentVersion`, `check_chunk_binding` (`source.py:349`), `bind_chunk` (`source.py:377`), `chunking.estimate_tokens`, `content_hash`,
  `canonical_text` (`chunking.py:20,38,30`).
  Copied small (a few lines, in the new package): chunk id and locator key, because `chunking.make_chunk_id` hard-codes `CHUNKER_VERSION = "palsu-chunker-v1"` (`chunking.py:11,91-92`) and
  `prospectus_extractor` stays protected.
  Not used: `chunk_adapter.adapt_chunk` (bound to that chunker version and `estimate-v1`, `chunk_adapter.py:87-90`) and the course builder. Policy chunks use `Chunk.parse` with a distinct
  policy chunker version.
  Importing `prospectus_extractor.chunking` runs the package `__init__`, which imports `pipeline`, and `pipeline.py:25` imports `prolog`; those modules are side-effect free and Docling is
  imported lazily,
  so the guard test checks the new package's source text, not `sys.modules`.
- Chunk rules: complete spans (digest, physical page, text, locator); ids from edition, locator, content hash and policy chunker version; repeated table headers on split tables; parent
  section path;
  `estimate-v1` counts, never claimed exact; `source_verification` and `content_review` pending, approval null; a chunk that cannot be fully located is rejected into the report, never
  emitted anchored.
- Report: source version and digest, conversion identity, tool versions, settings, physical-to-printed page map, counts, rejections, omissions, conflicts, review needs and the
  `pending_locator_contract` PPTX entries.
  It claims no verification or approval.
- Register minting (labelled default, owner decision 6): from the Task 2 report create pending `SourceDocumentVersion` records (`governance.py:177-204`): `doc-`, `ver-` and `edition-` ids
  derived deterministically
  from the byte SHA-256, never filenames; `document_category` `source_document` (`curriculum_proposal_candidate` only for a file the owner names); scope fields `pending` or `not_stated`;
  logical non-path locators; initial states from the vocabulary; approval `not_requested`, `approval_id` null.
- Red tests:
  - Round trip through `Chunk.parse`; stale `content_hash` rejected; id stable across runs and changing with edition bytes; a span with missing page or empty text refused; split table
    repeats headers.
  - The report lists every rejection and omission; no privileged status key survives into a chunk; an altered digest fails `check_chunk_binding`.
  - No `.pl` file is written, and the new package source imports no `prolog`, `pipeline`, embedding or vector module.
  - Minted ids are identical across runs and unaffected by renaming the file; duplicate bytes mint one record with two locators; `check_register` accepts the minted set; approval fields
    stay null.
- Mutations (guards): located-span requirement removed; approval set to approved; an embedding or Prolog import added. Three mutants, each failing a named test.
- Gate: `py -3.13 -m pytest -q tests\test_policy_chunks.py tests\test_ingestion_report.py tests\test_register_minting.py -p no:cacheprovider --basetemp "$S\bt_chunks"`,
  then chunks and report for the Task 3 and 4 output (NOT RUN until executed).
- Exit: tests pass; 3 of 3 mutants killed; every Task 3 and 4 text item appears in a chunk, rejection or omission (counts equal); 0 anchored chunks without complete spans.
- Stays pending: exact tokenizer counts (NOT RUN, no tokenizer here), rule authoring, release, authorized scope.

### Task 6. OCR extraction runner and ten-document OCR gate

- Purpose: extract JPG posters and scanned PDFs, and build the master 7.3 tooling (ten scanned documents, manual references, CER, critical fields).
  Separate from the six-configuration prospectus photo benchmark and the real-phone-photo assessment.
- Files: new `document_ingest/ocr_run.py`, `document_ingest/ocr_gate.py`; `tests/test_ocr_run.py`, `tests/test_ocr_gate.py`; `docs/decisions/phase-02-ocr-gate.md`.
- Reuse: `ocr_bench.engines.ADAPTERS`, `availability`, `run_ocr` (`engines.py:37,54,212`) and the `ocr_run.json` convention (tesseract adapter `:129-131`, rapidocr adapter `:203-206`);
  `ocr_bench.score.edit_distance` (`score.py:27`). `score.score_document` (`score.py:97-164`) pairs prospectus `courses` and is not used; no course rows are fabricated. Scanned PDF pages
  are rendered with pypdfium2 first.
- Gap handled: `ocr_languages` is recorded (`identity.py:85-99`) but never applied (`docling_env.py:201` sets `do_ocr` only) and the profile name stays `palsu-born-digital-v3`
  (`identity.py:19`);
  the runner records the engine and language actually passed.
- Gate design: a frozen PDF-backed manual reference per document (reviewer, date, source digest, page map, reference digest) fixed before scoring; the candidate is never the oracle;
  critical fields are negation, numeric thresholds, fees, dates, requirements and exceptions; per-document CER, missing and invented content, critical-field errors, worst document next to
  the pooled result;
  run record with engine, model, device, settings, input hashes and timing. Thresholds are owner defaults (reuse the `q11_verdict` 98 percent critical and 2 percent worst CER,
  `score.py:23-24,76-94`).
  Fewer than ten reviewed references means `blocked` and the evaluation is NOT RUN; the tooling is still completed. The prospectus photo benchmark never certifies policy OCR.
- Red tests: identical text gives CER 0; a dropped negation is a critical error despite tiny pooled CER; missing and invented content counted; a reference changed after freezing is detected
  by digest;
  a candidate used as its own reference is refused; fewer than ten references returns `blocked`; missing engine metadata refused; the worst document is reported;
  a missing engine raises `EngineNotInstalled` and the run is recorded NOT RUN; OCR units carry engine and confidence provenance.
- Mutations (guards): reference-freeze digest check removed; the candidate-as-reference refusal removed. Two mutants, each failing a named test.
- Gate: `py -3.13 -m pytest -q tests\test_ocr_run.py tests\test_ocr_gate.py -p no:cacheprovider --basetemp "$S\bt_ocr"`; the ten-document run only with ten reviewed references.
- Exit: tests pass; 2 of 2 mutants killed; the ten-document result is `blocked` or NOT RUN unless 10 of 10 reviewed references exist.
- Stays pending: reviewed references, engine, language and device ruling, real phone photographs.

### Task 7. Independent reviews, gates, handoff

- Purpose: close the phase on evidence only.
- Files: `plans/phase-02-handoff.md`, ledger edits through the handoff skill; review reports outside Git.
- Reuse: the handoff skill and `phase_state.py`; `git archive` of the final tip for the read-only review runs.
- Red tests: none new; each repaired finding gets its own named regression test.
- Mutations: none new.
- Gate: the block below; independent Spec review, then independent Standards review, as separate read-only runs from the archive; confirmed findings repaired at the shared boundary with red
  and green tests.
- Exit: the block's expected numbers hold; both reviews report 0 unresolved High findings; the handoff lists commits, versions, digests, commands with real results, deviations, risks and
  pending gates, and validates.
- Stays pending: everything under "Exit gate and stays pending".

## Gates

```powershell
$S = 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\phase2_<task>_<date>'  # scratch root, outside Git
$W = 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase-2'  # implementation worktree
$O = 'C:\Users\Hawksprey\source\repos\Bintanong'  # owner checkout, read only
$R = 'E:\Bintanong\institutional-sources\originals'  # originals, read only
New-Item -ItemType Directory -Force -Path $S | Out-Null
py -3.13 -m pytest -q "$W\tests" -p no:cacheprovider --basetemp "$S\bt_full"
py -3.13 "$W\backend\bintanong_tools\bintanong_jsonifer_prolog\bintanong_prospectus_jsonifier.py" --self-test
py -3.13 "$W\.agents\skills\bintanong-phase-handoff\scripts\phase_state.py" validate --repo $W
py -3.13 "$W\.agents\skills\bintanong-phase-handoff\scripts\phase_state.py" can-advance --repo $W
git -C $W diff --check 00f1fb1..HEAD
git -C $W log 00f1fb1..HEAD --format=%B | Select-String 'Co-Authored-By|Generated with'
git -C $W diff --stat 00f1fb1..HEAD -- backend/bintanong_api backend/bintanong_embedding backend/pyproject.toml backend/uv.lock uv.lock backend/bintanong_tools/prospectus_extractor
git -C $O status --short
git -C $O rev-parse dev origin/dev
```

Expected: full suite at least 4035 passed, 1 skipped, 13 subtests plus the new tests; self-test 80/80; validate valid; can-advance exit 0; diff --check 0 errors; attribution matches 0;
protected-path diff empty (`bintanong_contracts` only if owner decision 1 is accepted); the owner checkout shows exactly its 9 known entries; `dev` and `origin/dev` equal the values
recorded at the formal start.
Linux, macOS, containers, browsers and exact tokenizer counts are NOT RUN unless actually run.

## Review focus

- Source mutation or partial writes: Task 2 "a file changed between manifests fails the run"; Task 3 "an input changed mid-run fails".
- Writes into originals or dump folders: Task 2 "`--out` inside the root or repository refused" and "originals read-only and unchanged"; Task 3 "asserts nothing is written next to the
  synthetic input".
- Duplicate locators and editions: Task 2 "duplicate grouping"; Task 3 "two near-identical editions get distinct ids"; Task 4 "duplicate-PDF locators collapse"; Task 5 "duplicate bytes mint
  one record".
- Missing printed labels: Task 3 "printed label captured with the physical page kept".
- Invalid span geometry and privileged keys: Task 5 "a span with missing page or empty text refused" and "no privileged status key survives into a chunk".
- Copied private data: Task 2 "the report holds no drive letter, user folder or source text".
- Unsupported input and missing dependency: Task 1 refusal tests. Over-long Windows paths: Task 2 extended-length path test.
- Slide as page: Task 4 "no PDF `page`" test. USG as CSG: Task 3 "no CSG field is ever set". OCR candidate as reference: Task 6 "a candidate used as its own reference is refused".

## Exit gate and stays pending

Done means: Task 1 to 6 exits met with their named tests and mutants; both independent reviews closed; Gates expectations met; honest handoff written.
Stays pending, never claimed: authorized issuer, scope, effectivity, supersession and conflict evidence; missing CSG documents; ten reviewed scanned references and the OCR result;
at least 50 verified Taglish final cases with at least 10 per category; real phone photographs; Phase E, GUI, B2 and Phase 1 owner decisions; legacy Direct routing;
the integration branch's payload allowlist ruling and its missing saved GUI-interpreter gate; any source approval or activation; embeddings; executable Prolog.

## Known discrepancies

- `ingest parse <path>` is documented (`docs/superpowers/plans/2026-09-21-phase-00-foundation.md:169`); the real single-command CLI is `ingest PATH`. Recorded only.
- The preparation prose cites a Phase F source-root adapter as reusable; it is not implemented. Recorded only.
- The preparation prose wants PPTX slide-index spans; SourceSpan v1 has none. Resolved in Task 4 (report-only) pending owner decision 1.
- The preparation prose says the Handbook helper validates chunk size; `redocling_handbook.py:44-56` does not, it deletes a sibling `_redocling_tmp` (61-63) and scores unique-token overlap.
  Recorded only; not reused.
- `docling_gate_pass_rag.py:9` is a SyntaxError; `apply_bintanong_docling_hotfix.py:460` rewrites a target in place with a `.pre_bintanong_hotfix.bak` copy. Recorded only; neither is reused.
- `ocr_languages` is recorded but never applied. Resolved in Task 6.
- `loader.load_document_result` writes beside its input by default and skips `verify_unchanged` with `stage_dir`. Resolved in Task 3.
- `docling_env.py:74,105` name Docling 2.129.0 while `backend/pyproject.toml:30` pins 2.133.0; `docs/decisions/docling-version.md` gates pin moves. Recorded only.
- Master section 20 paths (`backend/app/ingestion/`) do not exist. Recorded only.
- Docling's native PPTX backend exists (`InputFormat.PPTX`) although `get_shared_converter` registers only PDF. Resolved in Task 4 (implementer choice).

## Owner decisions (none decided)

1. Additive slide locator for PPTX (new locator kind or optional field, schema-version decision, parity tests). Default: no contract change; PPTX is report-only as
`pending_locator_contract`.
2. Harden or retire `ingest.py`. Default: harden.
3. Dependency declarations for the `tools` extra: pypdf, python-pptx, pydantic. Default: no change; use pypdfium2 and Pillow already used in the repo; no pypdf.
4. OCR: engine, language, device, thresholds and which ten sources qualify. Default: reuse the `q11_verdict` 98 percent and 2 percent values, confirmed by the owner.
5. Which environment and Docling version run real conversions. Default: installed 2.129.0, recorded in every conversion identity, no upgrade (pin moves are owner-gated by
`docs/decisions/docling-version.md`).
6. Source-register minting rule (Task 5). Default: ids from byte SHA-256, category `source_document`, scope `pending` or `not_stated`, logical locators, approval null.

### Implementer choices (recorded in the task decision records)

Package layout (default new `document_ingest`); conversion route (default `loader.load_document_result` with explicit scratch paths); policy chunker version string; inspection thresholds
(defaults above);
prospectus PDFs in counts (default counted separately); CPU vs CUDA for large Handbooks; PPTX via Docling native or python-pptx.
