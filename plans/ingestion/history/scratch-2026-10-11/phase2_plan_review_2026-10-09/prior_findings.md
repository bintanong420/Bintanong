# Prior independent findings on the first Phase 2 plan draft (digest for the re-check)

Spec review (no High):
- Missing: master 7.1 step 5 repeated header/footer handling; master 7.1 step 1 how a SourceDocumentVersion is minted for a real unverified source (ids, category, logical locators, scope fields).
- Task 2 miscount: "four PDFs plus the election document" (the folder has exactly four PDFs; the election code is one of them).
- Wrong citations: (1) `ingest parse <path>` is in docs/superpowers/plans/2026-09-21-phase-00-foundation.md:169, not phase-00-handoff.md:31; (2) ocr_run.json convention is engines.py tesseract 129-131 AND rapidocr 203-206; (3) stale 2.129.0 pin at docling_env.py:74 AND 105; (4) hotfix backup suffix is `.pre_bintanong_hotfix.bak`.
- Missed contradictions A-K:
  A distinct policy chunker version cannot reuse chunking.make_chunk_id/assemble_chunk (hard-coded CHUNKER_VERSION at chunking.py:92,120) without editing protected prospectus_extractor.
  B spans_from_text_items (chunking.py:81) uses cleaned text, but Chunk._anchored_rules (source.py ~334-338) needs source_text == joined span text, so spans must come from raw_text.
  C JPG posters/scanned PDFs: OCR route undefined and Task 3 ran before Task 5; scanned PDFs with OCR off yield empty text (need omission records).
  D hardened ingest would print docling_env's stdout lines (docling_env.py:192,195,198) before the JSON.
  E hardened parse_document could succeed with empty text.
  F "pipeline/prolog not imported" is false at runtime (prospectus_extractor/__init__.py imports pipeline; pipeline imports prolog); no side effects.
  G "extractor's split-PDF offsets" does not exist (no producer of original_page/page_offset).
  H loader skips verify_unchanged when stage_dir is given (loader.py:481-482).
  I real conversions would run under unpinned Docling 2.129.0 vs pin 2.133.0.
  J container runs `bintanong_tools.ingest` while tests use `backend.bintanong_tools` (relative imports, lazy docling, `--help` must work).
  K evidence_adapter takes only the first prov per text item and drops level/tree.
- Missing owner decisions: OCR engine/language/device; Docling environment/version for real conversions; register minting; python-pptx vs Docling native PPTX; pydantic declaration.
- Gaps: 1A case-insensitive suffix and empty-text tests; 1B how "inside the repository" is detected (a worktree's .git is a file); Task 4 oversize-clause split cannot be a whole-item text_item locator (suspicion).

Standards review (one High):
- F3.1 HIGH: JPG posters depended on an OCR path no task builds; Task 3 before Task 5; red tests tested a producer that did not exist.
- F3.2 Medium: decision 4 contradicted "do not add a second Typer command"; Task 1A started first but depended on harden-vs-retire.
- F3.3 Medium: Task 1A named no decision record.
- F3.4 Medium: PPTX candidates carry no SourceSpan; Task 4/5 must report them as rejected `pending_locator_contract` with one red test.
- F3.11 Medium: Review-focus items without red tests (span geometry, privileged keys, loader cache path).
- Readability: 63 lines over 200 chars (one of 1604); not scannable; each task a 400-1600 char bullet.
- Low: Known-discrepancy section restated facts without "resolved in Task N"; Task 6 had no Exit line; 1A/1B numbering; "Task 1" reference that did not exist; maintainer vs owner; coordinator/root/implementer undefined; "defaults" two meanings; undefined placeholders (<agent>, <batch>, <date>, <task>, <worktree>, <owner checkout>, <scratch>) so the gate block was not copy-pasteable; stale dev/origin-dev hashes; decisions 4, 9, 10 lacked a labelled default; "Phase F plan D2" is not a file; `Nothing here is institutional approval` was only a semicolon clause.
- Vague phrases: "only where the format fits"; language detector word lists/thresholds; "form fields only if pypdfium2 exposes them"; undocumented thresholds; encrypted-PDF test conditional; "raise UnsupportedDocument or FileNotFoundError"; path over 260 recorded vs failed run; "a small raw-JSON reader"; no invented pass threshold vs existing q11_verdict 98%/2%; Task 2/3 real-run exits could not fail (need units + omissions == text_items); exit lines lacked numbers.
- Over-engineering (ponytail): language detection (yagni), staging/replace_file in the inspection tool, pilot selection algorithm, AST source guard test in 1A, 8-row boundaries table, 14-version environment list, 10 owner decisions (6 are implementer choices), Not-authorized duplicating constraints, Phase F paragraph, Task 4 rules restating master, Review focus overlapping red tests.
- INDEX: ledger row status was not a phase-plan status word (use `ready (preparation only)`); statement repeated three times; shorten the Next-permitted bullet.
- Suspicions: merge Task 2/3 candidate modules; 24 mutants probably too many.
