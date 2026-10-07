# Prospectus candidate chunk provenance

Phase E Tasks 1–4 are a local review-only batch on `feat/prospectus-phase-e-rag-provenance`, starting at `1236c9911de6efc60914839642a86b5911185933`. The immutable historical plan is `plans/2026-10-03-prospectus-phase-e-rag-provenance.md`; the owner brief and additional rulings supersede its outdated snippets. This record does not complete Phase E or advance the formal phase ledger.

## Source and identity

The canonical `ProspectusEvidence` document is authoritative. Course locators must resolve to its actual cells, with matching table/row/column coordinates and printed text. `verify.own_role_cells` supplies the existing field-role inference. Code, title, units and prerequisite text must be supported in their own fields; unrelated banner/title words and code or unit digit prefixes do not suffice. Unit values must match the existing `parse_units` result. Missing/malformed locators or unsupported fields reject a course explicitly. Rejected courses never contribute to aggregate text, totals or source spans.

`chunking.py` remains pure stdlib. Source assertion checks live in `rag.py` because they reuse the existing evidence, field-role and unit owners rather than duplicating them in a pure primitive. This is a deliberate deviation from the historical `course_rejection` word-set helper, which could accept wrong-field evidence.

The semantic builder receives the existing document, parsed layout and section evidence IDs through the minimum pipeline call-site change. A failing pipeline regression preceded that change. It does not pass or compute PDF identity yet: Task 6 must consume Phase D's captured `InputSnapshot`/`run_identity`, never independently rehash a PDF or interpret Docling's integer `binary_hash` as SHA-256. Current pipeline candidates consequently remain unanchored. Explicit builder identity arguments support edition-stability tests, not source approval.

Chunk IDs include source edition identity (or `unanchored`), locator, canonical source/summary content hash and chunker version. NFC, whitespace and line endings are canonicalized; source filenames, timestamps and dictionary order do not establish identity. Duplicate chunk IDs are coalesced. Printed `source_text` stays separate from the advising summary. Extraction method and repair IDs remain on every contributing span. Content review remains pending.

## Geometry and summaries

Pages and coordinate origins come from canonical cells, not the legacy provenance union or filename. The legacy cell projection omits origin, so the builder resolves it from `NormalizedCell.bbox`. Text items already expose their actual origin under `origin`; the span builder preserves that key. Multi-page and incompatible-origin groups remain separate. `BOTTOMLEFT` boxes use their native top/bottom orientation. Boxes with unrecorded origins remain separate because their union direction cannot be inferred; unknown page and geometry stay unknown.

Term, overview, elective and standing summaries retain every contributing span, including option text items and accepted slot cells. Options carry `source_item_id`; tuple-format legacy inputs retain null rather than inventing an ID. Each option must resolve and reproduce the existing elective parser's code/title before inclusion. Rejected options/slots have explicit omission metadata and rejection reasons. Long summaries split while repeating their header; each final rendered estimate is checked. No accepted courses means no course aggregate.

`prerequisite_phrase` is unchanged, preserving blank-unreviewed versus stated-none/reviewed-empty and unresolved/standing wording. Derived unit totals, parsed prerequisite states, classifications and term placement are labelled as derived; program/college/school-year context is unsourced in these chunks. The old negative unlock-completeness statement is omitted because partial extraction cannot prove it. Unlocated BOR/printed term-total statements are also omitted from summary text rather than presented as source-verified PDF assertions. This does not change the extracted course, audit or metadata fields.

## Review estimates and deferred work

`estimate-v1` uses `max(ceil(chars / 3), ceil(words * 1.8))`; 512 and the 32 reserve define a review budget only. They are not an upper bound on the model tokenizer. Exact prefix/special-token-inclusive counting is mandatory before embedding. The 400 target applies to splitting summaries; it does not merge distinct courses.

The hierarchical builder remains unchanged until Task 5. The schema remains v3.2; hash wiring, payload rejection reporting, v3.3 and JSONL integration remain Task 6. Tasks 7–8 corpus/source gates, human pilot checks, GUI trial, source-owner approval and real-photo support remain separate and pending. No embedding, vector write, active curriculum or institutional approval is introduced.

## Verification boundary

Chronological RED/GREEN logs, exact commands and atomic checkpoints are external under `scratch/publish_resume_2026-10-07/phase-e/batch1` in the dataset workspace. The progress ledger records every boundary. Root owns the comprehensive suite, self-test, independent Spec then Quality review, and explicit-path commits after this batch is frozen. Implementer focused checks cover the new chunks, Phase C authority/prerequisite regression, parser and existing course-source checks; focused green is not a passed corpus or human gate.

### Root Tasks1–4 gates (2026-10-07T19:04:53.2081401+08:00)

Frozen implementation tested directly in PowerShell with system py -3.13, existing environments untouched: focused284passed13subtests11.93s; full1574passed1skipped8warnings13subtests145.91s; self80/80. Exact commands/output: external scratch/publish_resume_2026-10-07/gate-e-batch1-{focused,comprehensive,selftest}.json. git diff --check0; owner .gitignore SHA unchanged; dev5c34fd7 unchanged. Commit this frozen batch for separate Spec then Standards review; not PhaseE completion. Task5 layout and Task6 identity/schema/rejection payload remain pending.
