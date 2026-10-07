# Prospectus Phase E: decision hand-off

Status: Phase E code and the corpus and pilot checks (plan Tasks 1 to 8) were carried out on `feat/prospectus-phase-e-rag-provenance`, local only, with deviations: the plan's Task 7 step 6 pass criterion is NOT met, the Codex gate (Task 8 step 4) was not run, and the by-eye PDF check (Task 8 step 2) was replaced by an automated overlap script (see "Plan criteria not met" and "Not run"). This note records what it delivers, what the gates measured, and the decisions that belong to the owner. Nothing here approves a source, a curriculum or a chunk: every chunk carries `content_review: pending`. The design record is `prospectus-rag-provenance.md`; this note adds the measured results.

## What Phase E delivers

- Candidate chunks (course, term, program overview, elective pool, enrolment policy, and Docling layout chunks) that carry the PDF SHA-256 captured once per run, page, table, cell IDs, source spans with extraction method and coordinate origin, printed `source_text` apart from the advising summary, and a stable `chunk_id` (edition, locator, content and chunker version only).
- Strict source proof. A course becomes a chunk only when its code, title, units and prerequisite text equal the complete printed text of its own cells. Anything else is refused and listed in `rag.rejected_chunks` with a reason; nothing is dropped silently, and a rejected course is left out of every summary.
- `estimate-v1` token counts (512 cap, 32 reserve) as review metadata. They are not tokenizer counts.
- Schema `palsu-prospectus-v3.3` and a canonical `_rag.jsonl` (LF, sorted keys, no path or timestamp).
- A read-only corpus report in `scripts/prospectus_course_compare.py` (`--corpus-report`): blocked audits apart, accepted and rejected courses per file by reason, title rejections in three groups, layout rejections, chunk statistics.

## Corpus gate (44 cached Docling JSON inputs, base `1236c99`)

- Course fields and audit counts: 44 of 44 identical to the base.
- Blocked audit: 38 of 44 inputs have audit status `error` and emit no chunks and no rejections (reported apart; the report computes the chunk and rejection counts of each blocked input and shows `rejections=0` for every one). Six inputs are not blocked.
- Over the six: 304 courses, 279 accepted, 25 rejected (8.2%), none unaccounted. This reproduces the independent review's figures.
- Rejections by reason: `title_not_in_source_text` 17, `code_not_in_source_text` 4, `no_valid_source_cells` 2, `prerequisite_not_in_source_text` 2. By file: 2, 5, 2, 2, 9 and 5.
- The 17 title rejections: 16 are the printed title cell equal to the claimed title plus a year or semester banner word (`FIRST`, `FIRST SEMESTER`, `SECOND SEMESTER`); 1 is a claimed title longer than its cell (a title that continues in a neighbouring cell); 0 are other. The 16 are banner words; the classifier also counts a total or units word and a token with no letters (a footnote or row digit) as a "marker token", so the group is named `printed_equals_claim_plus_token`; the extractor's banner vocabulary is reused and only the extra words are kept apart in the script. The other reasons are not one family: the four `code` rejections are a printed code with a `Total` or a digit around it or a parser merge across rows, and the four prerequisite and source-cell rejections are listed under "Plan criteria not met".
- Chunk statistics use the true median (the earlier report showed the upper middle for even counts, for example enrolment policy n=2 as 162).
- Layout: the Docling table chunk is rejected as `over_token_cap` in 6 of 6 not-blocked files (3,154 to 3,977 estimated tokens). The curriculum facts in that table are covered by the course and term chunks, so no fact is lost, but the layout view of the table is not a candidate.
- Chunks: 372 in six inputs; course chunks 78 to 138 estimated tokens (median 94), term summaries up to 358; no course or term chunk above the 480-token review cap. All 372 are unanchored (`pdf_sha256` null) because every input is a Docling JSON.

## Anchored pilots (real pipeline from the PDF)

Copies of three prospectus PDFs were run through the full pipeline; originals were hashed before and after and are unchanged. The PDF hash in every chunk equals the captured run identity and the original file hash. Every chunk was checked against the Docling cells and the PDF page text. Course chunks also had their section checked against the year and semester headings printed above the row; term chunks got a "listed codes on page" check instead, and other chunk types have no section check.

- BSBA-HRM: audit `warn`; 61 chunks (47 course, 8 term, 1 overview, 1 policy, 4 layout), all resolved. 2 courses rejected (title with a banner word), 1 layout table over the cap.
- Information Technology (an added pilot beyond the brief): audit `warn`; 62 chunks (48 course, 7 term, 1 overview, 1 policy, 5 layout), all resolved. 4 title rejections, 1 `no_valid_source_cells`, 1 term with no accepted course, 1 layout table over the cap.
- BS Computer Science (2025-2026): audit `error` (one structural ambiguity), so no chunks. Its anchored path is therefore not exercised by the brief's second pilot; the check was carried by the added one above.
- The gate fails when a hash, page, section or cell reference is tampered with (four tampers each reported not resolved).
- Two observations. A semester banner cell that rides along with every course in that semester is Docling's composite of several headings, so its text is not one literal printed run; each of its words is on the page, but it does not satisfy the literal check that the own-field cells do. And Docling cell boxes can cover only the first line of a multi-line cell or under-cover the text width, so box checks are an overlap check on a widened box, not exact geometry.

## Plan criteria not met

- Task 7 step 6 asks for 0 `prerequisite_not_in_source_text` and 0 `no_valid_source_cells` on real inputs. Measured: 2 and 2. This criterion is NOT MET. Nothing was loosened; the four cases are listed:
  1. BS-Bio, Thesis 1: the prerequisite cell `2 75% of Major Subjects` picked up the units digit (`2`).
  2. BS-Bio, Practicum: the prerequisite is split across two rows (`90% of Major` / `Subjects`).
  3. BSE-Franchising, ENTRE 15: code and title are fused in one cell (`ENTRE 15 Business Implementation 2`), so no own cell holds the code alone (`no_valid_source_cells`).
  4. Information Technology, IT 22: the title `TOTAL` was taken from another row (`no_valid_source_cells`).
- The code rejections (4) and title rejections (17) are likewise parser-versus-printed differences, reported and not loosened.

## Not run

- Codex gate (plan Task 8 step 4): NOT RUN.
- By-eye check against the PDF (plan Task 8 step 2): NOT DONE by eye; replaced by an automated widened-box overlap script (a scratch tool, not in Git), which is weaker than a person reading the page.

- Exact tokenizer count: NOT RUN. The embedding model's tokenizer is not available on this machine and nothing was downloaded. Exact counting that includes prefix and special tokens is mandatory before any embedding.
- Human checks: the GUI trial, source-owner approval and real-photo support remain separate and pending.

## Open owner decisions

1. Strictness versus usefulness for banner-word titles. Sixteen of the 25 rejected courses, and most of the title rejections in the pilots, are a printed title cell with a year or semester banner word merged into it by the table extraction. The strict rule refuses them correctly (the printed text is not the title). Options: keep refusing; or reuse the existing banner and footnote cleaning so the printed cell is compared after removing a banner token that the section parser already recognises as a banner. The second option recovers the courses but makes equality depend on the cleaning rules, so its removal list must be explicit and tested. Nothing was loosened in this phase.
2. The lost layout table chunk. Docling's whole-table chunk exceeds the cap in every file and is refused rather than split. Options: leave it refused (the course and term chunks carry the facts); or split it by row into cell-anchored chunks.
3. Banner text inside `source_text`. A course chunk's `source_text` can begin with the banner cell. Decide whether `source_text` should be limited to the course's own cells (the banner stays in the spans) before anything is shown as a citation.
4. Whether a claimed title longer than its cell (a title continued in a neighbouring cell) should ever be accepted. The current answer is no.
5. Anchored coverage. The corpus gate only covers Docling JSON, which is always unanchored. Decide which PDFs form the anchored acceptance set before Phase F.

## What Phase F must consume

- Schema `palsu-prospectus-v3.3`; top-level `pdf_sha256`; `run_identity.pdf_sha256` as the only hash source (never re-hash, never read Docling's `binary_hash`).
- Per chunk: `chunk_id`, `chunk_type`, `source_anchored`, `pdf_sha256`, `source_spans`, `pages`, `cell_ids`, `source_text`, `text`, `token_count` and `token_count_method`, `content_review`. A loader must refuse any chunk with `source_anchored: false` and any chunk whose `content_review` is not an explicit approval recorded elsewhere.
- `rag.rejected_chunks` and `quality_report.total_rejected_chunks`, so a run is never judged by its accepted chunks alone.
- `_rag.jsonl` as canonical LF with sorted keys; identical across folders for the same PDF bytes, not across renamed copies (the file name stays in `source`).
- The exact-tokenizer check before embedding, and the open decisions above.
