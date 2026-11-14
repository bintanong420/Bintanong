# Prospectus Markup Twin

Date: 2026-10-04
Status: accepted; Phase B complete on branch `feature/prospectus-markup-twin`, merged locally into `dev`, not pushed

## Purpose

The markup twin is a source-faithful rendering of the Docling evidence for one prospectus, written as `<name>_prospectus.md` beside the JSON outputs. It shows what Docling saw: its table grid with real row and column spans, and its text items, in page reading order. It is a review aid built from evidence. It is not an approved curriculum, and it carries no institutional facts.

It has two jobs. First, it is a comparison view against the printed PDF: a reviewer can see exactly which cells Docling produced and where. Second, it is the source view for the later review tools (Phase B2 and the GUI), because every cell and text item carries its ID and page, so a reviewer's decision can point at a specific piece of evidence.

The renderer reads the evidence model (`ProspectusEvidence`), not the parsed JSON. It changes nothing the parser reads, so course fields are unchanged (see Evidence).

## Format

- Line 1 is a status comment: `<!-- extraction_audit: STATUS | VERDICT | pdf_sha256: HASH -->`. `VERDICT` is `REVIEW REQUIRED` when the audit status is not `ok`, else `content_review: pending`. When page order could not be fixed, the comment also carries `| reading_order: approximate (page N: page size unknown)`.
- Line 2 is `<!-- markup: palsu-prospectus-markup-v1 -->`, followed by a visible blockquote saying this is a reconstruction for comparison with the PDF (starting with `**REVIEW REQUIRED**` when not `ok`).
- Tables are HTML: `<table data-table data-page data-rows data-cols>`, one `<tr>` per grid row, one `<td>`/`<th>` per Docling cell with `data-cell="t0-c12"`, `data-page`, and `colspan`/`rowspan` when greater than 1. HTML is used because Markdown pipe tables cannot express spans.
- `data-gap`: a grid position covered by no cell becomes `<td data-gap></td>`. It has no cell ID, so no evidence is invented and a consumer can drop all gaps with one filter.
- `data-unplaced-cell="ID"`: a cell whose rectangle collides with an earlier cell, or starts outside the grid, is not placed in the row. It follows the table as `<p data-unplaced-cell="ID" data-page="P">text</p>`. Every cell ID appears exactly once.
- `data-span-clamped="declared_rows,declared_cols"`: a span cut to fit the grid carries the declared values.
- Text blocks are `<h1>`/`<h2>`/`<p>` with `<small>` for footnotes, headers and footers, each with `data-item`, `data-label`, `data-page`. Page changes are marked with `<!-- page N -->` and `<hr>`; the first block gets no marker.
- Line breaks inside a cell or text item are written as `<br>`. A raw newline inside a table would end the HTML block in Markdown.
- Text is the original Docling string (`raw_text`), HTML-escaped, not the cleaned string the parser uses. `data-page` and the page comment are escaped too.
- Output is deterministic: cells sorted by `(row_start, col_start, cell_id)`, UTF-8, `\n` newlines, no timestamps.

`export_to_markdown()` from Docling was deliberately not used: it flattens spans and cannot carry cell IDs. No payload key was added, so `SCHEMA_VERSION` is unchanged.

## Decisions

All seven were accepted as recommended in the plan (`plans/2026-10-03-prospectus-phase-b-markup-twin.md`).

| ID | Decision |
| --- | --- |
| D1 | Non-table text is HTML blocks, not Markdown-native. Markdown would silently change the meaning of a line starting with `#`, `1.` or `-`; IDs and pages ride on the element. |
| D2 | The `.md` is written for every audit status, including `error`. The reviewer needs the view most when the audit failed (38 of 44 cached inputs). It carries `REVIEW REQUIRED`. |
| D3 | `<th>` for the column-header row and for year/semester banner cells that span 2 or more columns; every other cell `<td>`. The rule is cell-level because Docling sometimes glues a banner label into a course cell (BSCS `FIRST SEMESTER Discrete Structures 1 1`), which must stay `<td>`. |
| D4 | The source hash is an optional keyword `pdf_sha256`, shown as `not recorded` until Phase D passes it. The payload and evidence hold no PDF hash. |
| D5 | Colliding cells are rendered after the table as `data-unplaced-cell`, keeping the table valid. 14 of the 44 cached files have overlapping cells. |
| D6 | Reading order is page, then vertical position, then left edge, with a 3-point same-line tolerance. Items without page or box fall back to input order (texts, then tables). |
| D7 | `BatchConfig.write_md` defaults to `True`, like the sibling export flags. The isolated runner passes no export flags and is unaffected. |

## Reading-order frame fix

Real Docling JSON mixes coordinate frames: table cell boxes are TOPLEFT, text item boxes are BOTTOMLEFT. The first renderer compared the two as if they shared a frame, so every text sorted before every table. The loader had dropped `coord_origin` and never loaded page height. The fix (commit 8d76b89) is additive: `SourceBBox.origin`, `ProspectusEvidence.page_sizes`, and `text_items[].origin`. The renderer converts BOTTOMLEFT to a top-down value (`page height - top`) at one position boundary. The parser, sections and audit were not touched.

A page that mixes origins and has no known page height cannot be ordered reliably. It falls back to texts-then-tables and the status line says `reading_order: approximate`. This is a visible warning, not a silent guess (commit 6bf8699, test tightened in 851ab17).

## Codex review fixes

A Codex review ran on Phase B and its findings were fixed, each with a failing test first (suite 80 to 93 passed).

- `a24efe2` Source fidelity: cells and text items render original Docling text (`raw_text`). On the 44 cached inputs `raw_text` equals `text` for all 9820 cells, but 48 of 521 text items differ and now show the original.
- `e15cbe8` Cells never vanish: out-of-grid cells (including negative starts) are listed as unplaced, clamped spans are marked, and `data-page` and the page comment are escaped.
- `42a5d2b` The comparer fails on missing outputs, on both sides nonzero, and when neither side wrote `candidate.json`. Markup cell IDs are compared as an exact multiset against IDs derived from the cached Docling JSON.

## Known limitations

- A table whose cells span two pages is rendered whole at its first page's position, because splitting it would break the HTML table. Docling normally splits page-crossing tables itself.
- Batch `--skip-existing` checks only the JSON and essentials files, so a missing `_prospectus.md` is not regenerated. Phase D owns this.
- `pdf_sha256` shows `not recorded` until Phase D passes it. `prospectus_batch.py` hashes the PDF in the parent process, but the child does not receive it.
- Banner defect, found by the visual check below: Docling merges year/semester banner text into neighbouring cells, and the twin shows that faithfully.

## Tools committed in this phase

- `scripts/prospectus_course_compare.py`: field-level old-versus-new comparer over the cached inputs, with markup invariants (each cell ID exactly once). Options `--golden --work --base-ref --semantic-doc --limit --jobs`; old code runs in a git worktree.
- `scripts/prospectus_course_audit.py`: checks every course across JSON, markup twin and PDF text layer (checks A, B, C, D below). It is measure-only today, and it is the planned scorer for OCR output: run it on an OCR source to see which courses the printed PDF does not support.

## Evidence

- Course-field regression: 44 of 44 cached inputs identical to the base `69ca855` on every course field, with the exact cell-ID check on (re-run after the Codex fixes). Cached Docling JSON was used, so PDFs were not re-converted.
- Full suite: 93 passed, 13 subtests passed (`--with fastapi==0.141.1`); extractor self-test 80/80.
- Course audit `course_audit_2026-10-03b` (fresh outputs after the Codex fixes, identical to the first run): 44 paths, 39 distinct PDFs, 2031 courses, markup cell count equal to evidence cell count in 44 of 44.
  - A (course value found in its own `.md` cells): provenance 2031/2031 match; code 1990 match, 33 loose, 8 fail; title 1956 match, 1 loose, 53 transformed, 21 fail; prerequisites 1003 match, 2 loose, 18 fail, 1008 empty.
  - B (value found in the PDF text layer): code 1859 match, 130 loose, 42 fail; title 1892 match, 13 loose, 126 fail; units 1953 match, 46 loose, 8 fail, 24 not checked.
  - C (printed code-like strings no course accounts for): 470 total, 192 silent, 278 flagged.
  - D (code-like `.md` cells no course claims): 216 total, 71 silent, 145 flagged.
  - The silent C and D lists need human reading before any OCR reuse. These are measurements, not an accuracy claim.
- Human visual check (3 and 4 October 2026, all 39 distinct prospectuses, rendered twin beside the PDF): first-year rows render fine. The year/semester banner rows are broken: banner text overflows into course names or is misaligned. Diagnosis: the renderer is faithful, because it draws Docling's raw cells and not the JSON. The defect is in Docling's table structure, which merges banner text into neighbouring cells (Architecture: the cell "FIRST YEAR FIRST SEMESTER SECOND SEMESTER" is attached to AD-1/L; BSCS `t0-c9`: "FIRST SEMESTER Discrete Structures 1 1"), and the parser inherits it. Not every degree is equally affected.

## Follow-up

Phase B2: a year/semester verifier and fixer with a human decision ledger. Later: a parser banner-split repair. Phase D: PDF hash and cache key, and `.md` regeneration under `--skip-existing`.
