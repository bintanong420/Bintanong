# Extractor package split — progress

Resume point for `plans/2026-10-03-prospectus-extractor-package-split.md`. Fresh Git and test output outrank this note.

- Branch: `refactor/prospectus-extractor-package`, created from `dev` at `7591264`.
- Monolith SHA-256 at base: `8ea75006a4c588902738c3a31096d44aa453a2fdfdeffae8750bf681eae3164d`.
- Baseline observed 2026-10-03 on this branch: 26 tests and 13 subtests passed (plus the 2 new failing gate tests); self-test 80/80; monolith hash matches.
- Pre-existing dirty files to leave alone: `.gitignore`, untracked `plans/CODEX_HANDOFF_prospectus_extractor_phase2_2026-09-26.md`.

## Phase A

| Task | State | Commit | Observed result |
| --- | --- | --- | --- |
| 1. Baseline and failing 1:1 test | done | see git log | Baseline matched (26 passed/13 subtests, 80/80, SHA ok). New test: 2 failed (186 names missing, extra empty; KeyError ensure_docling_env), none skipped. |
| 2. Golden-output check | done | see git log | Smoke (1 file, BSA-for-student-new-version): `1/1 FAIL exit old=0 new=1`, files old=[candidate.json, candidate_review.csv] new=[]. A and B hold the same two files. Noise A vs B = 1 path (`generated_at`). |
| 3. Splitter and generated package | done | see git log | Splitter ran clean (26 modules, no SystemExit, no MOVES change, splitter text identical to plan). Gate test: 1 passed (every definition moved unchanged), 1 failed (test_deviations_are_real, intended red for Task 4). Import-all printed ok. Full suite: 27 passed, 1 failed, 13 subtests passed. |
| 4. Entry points, shim, relaunch change | done | see git log | Red before implementation: 4 failed (module, package directory, re-export, relaunch), 1 passed (legacy shim), as predicted. After: full suite 33 passed, 13 subtests passed, 0 failed. 80/80 (exit 0) from -m module, package directory, shim path, and backend-as-root (`--directory backend`). Golden check --limit 3: `3/3 identical` (noise=1 each). Plan text worked unchanged. |
| 5. Isolated batch uses the package | done | see git log | Red: 2 failed (no `package_sha256`; child path was the shim), 3 passed. After: batch tests 5 passed; full suite 35 passed, 13 subtests passed, 0 failed. Child launch check: package dir, 64-hex hash, `--self-test` 80/80. Plan text worked unchanged; no existing test needed changing. |
| 6. Golden proof, decision record, Codex gate | done | see git log (decision record `38af9fd`) | Golden check on 44 cached inputs: `44/44 identical`, exit 0. Full suite 36 passed, 13 subtests passed. Self-test 80/80. Sonnet 5.5 review found the `.docling-venv` lookup effect; Codex CLI 0.157.0 found the shim-patching effect; both recorded in `docs/decisions/prospectus-extractor-package.md`. `.gitignore` line still uncommitted. |
| 7. Remove scaffolding, hand off | done | see git log | Scripts removed with `git rm` (last present at `2dffe3d`); `_golden_old/` deleted (no python process running). Full suite after deletion: 36 passed, 13 subtests passed, 0 failed. |

## Later phases

B markup twin → C status separation → D cache and publication → E RAG provenance → F tools boundary. Each needs its own detailed plan before work starts.

## Log

- 2026-10-03: plan written and branch created. No code changed yet. Next step: Task 1, step 1.
- 2026-10-03: Task 1 done. Baseline confirmed (26 passed + 13 subtests, 80/80, SHA ok). New gate test: 2 failed, none skipped.
- 2026-10-03: Task 2 done. Run-to-run noise in old code: 1 JSON path in candidate.json, ('generated_at',); candidate_review.csv identical. Note the script prints noise=0 while the package is absent, because it only counts files present in C; measured A vs B by hand. Real noise count appears once the package exists.
- 2026-10-03: Task 3 done. Splitter copied verbatim from the plan, no changes. Three harmless false-hit imports (`from .common import track` under `if RICH_AVAILABLE` in courses, prolog, rag: a loop variable named `track` shares the spelling of Rich's `track`); no cycle, left as generated.
- 2026-10-03: Task 4 done. Only generated-module edit: last line of ensure_docling_env. Shim and __main__.py worked as written in the plan, no fixes needed.
- 2026-10-03: Task 5 done. `parser_sha256` in the isolated manifest is now a hash of the whole package (every `*.py`, line endings normalised) and is not comparable with earlier manifests' single-file hash `8ea75006...`. The child command launches the package directory.
- 2026-10-03: Task 6 step 2 done (test added), step 4 done in the working tree but intentionally left uncommitted with the owner's .gitignore edit; steps 1, 3, 5 waiting on the 44-input golden run and Codex.

- 2026-10-03: Task 6 golden result: 44/44 identical, exit 0. Run-to-run noise in the old code was 1 path for 38 inputs and 3 paths for 6 inputs; the 3-path case is the generation timestamp in candidate.json (generated_at and the embedded % Generated: line) and in candidate_prospectus.pl. Cached Docling JSON was used, so PDFs were not re-converted.
- 2026-10-03: Reviews: Sonnet 5.5 found the .docling-venv lookup effect (item 3); Codex CLI 0.157.0, read-only, found that patching a name on the shim no longer affects the package (item 5) and nothing else. Both are recorded in the decision record.
- 2026-10-03: The .gitignore line for prospectus_extractor/docling_jsonified_output/ is in the working tree but uncommitted, waiting for the owner.
- 2026-10-03: Phase A complete; not merged, not pushed; next: user decides on merge, then write the Phase B plan.

## Phase B: markup twin (branch feature/prospectus-markup-twin)

Plan: plans/2026-10-03-prospectus-phase-b-markup-twin.md. Decisions D1-D7 in the plan assumed as recommended unless noted here. Cross-phase rules in plans/2026-10-03-prospectus-extractor-package-split.md override the plan: the markup shows pdf_sha256 only when a caller passes it, scripts/prospectus_course_compare.py is committed, every commit leaves the suite green.

| Task | Status | Commit | Evidence |
| --- | --- | --- | --- |
| 1. Start check, branch, delete Phase A gate | done | see git log | baseline 36 passed + 13 subtests, 80/80; 34 passed after deleting the gate |
| 2. Table renderer | done | see git log | red: collection error ModuleNotFoundError markup; green: 8 passed; full suite 42 passed + 13 subtests |
| 3. Header, text blocks, reading order, page breaks | done | see git log | red: 11 failed, 10 passed (plan expected 12 failed: the determinism test already passes on the tables-only renderer); green: 22 passed; prospectus + other collectable tests 50 passed + 13 subtests (2 files uncollectable: no fastapi in this env); self-test 80/80. Defect found on real data, fixed in the follow-up commit (see log, 2026-10-03 frame fix). |
| 4. Pipeline, CLI, batch, TUI wiring | done | see git log | red 5 failed/26 passed; green 65 passed + 13 subtests; self-test 80/80 |
| 5. Course-field regression on 44 inputs | done | 571f2f2, 42a5d2b | 44/44 identical, exact cell-id check on (base 69ca855); see log |
| 6. Visual check against the PDFs | done | see log | Human check 3-4 Oct 2026 on all 39 distinct PDFs: first-year rows fine; year/semester banner rows broken (Docling merges banner text into neighbouring cells; renderer faithful). Follow-up Phase B2. |
| 7. Decision record, Codex gate | done | see git log | docs/decisions/prospectus-markup-twin.md; Codex review already run, fixed in a24efe2, e15cbe8, 42a5d2b. Phase B complete; merged locally into dev. Next: Phase B2. |

### Phase B log

- 2026-10-03: Task 1 done. Branch created from dev at 69ca855 (plan said 8d26f18; later docs commits only). Line references re-read: unchanged except pipeline.py essentials_path.write_text( now starts at line 233 (plan: block ends 237); loader.py export_to_markdown at 201; tui.py config row 89, ask 196, single_file 265-275.
- 2026-10-03: Task 2 done. Test and markup code taken verbatim from the plan; no deviations.
- 2026-10-03: Review fix commit 6a214e2: gap-assertion made falsifiable, line breaks in cell text rendered as <br>. Task 3 uses the same rule for text blocks (_esc_block).
- 2026-10-03: Task 3 done; plan code verbatim except _render_text uses _esc_block. Real-data check on BS CS 2025-2026 and BSA: 16/16 and 5/5 text items rendered, header text before first table, but mixed coordinate frames break text/table order (see Task 3 row).
- 2026-10-03 frame fix: DEFECT table cells are TOPLEFT (cell bbox.coord_origin), text items BOTTOMLEFT (texts[].prov[].bbox.coord_origin; table prov is BOTTOMLEFT too), so markup._y_down compared -top with top and every text sorted before every table. ROOT CAUSE loader.py _source_bbox (was line 46-52) and the text path in evidence_adapter (was 185-198) dropped coord_origin, and page height (pages[n].size.height, 936 on both samples) was never loaded. FIX additive only: SourceBBox.origin (default None), ProspectusEvidence.page_sizes (default {}), text_items[].origin; markup._y_down converts BOTTOMLEFT to height - top at the single position boundary, TOPLEFT as is, unknown origin or height falls back to the old top>=bottom guess per item. sections/parse/audit untouched. EVIDENCE red: 4 failed, 22 passed (SourceBBox has no origin, ProspectusEvidence has no page_sizes); green 26 passed in test_prospectus_markup.py. Real data, BSCS: header h2,h2,p, table, footnotes (CS Elect 4/La ...), note, legend, table, footer 50; BSA: headers, table, footnote, table. All 44 cached files rendered: 9820 cells, each id exactly once, text equal after unescape, balanced HTML, 1734 rows all width = num_cols. Full suite 60 passed + 13 subtests (with --with fastapi==0.141.1), self-test 80/80.
- 2026-10-03 step 0 (review follow-up): markup._reading_order now treats a page with mixed origins and no page height as unpositioned (texts by item id, then tables) and the status comment gets `| reading_order: approximate (page N: page size unknown)`. RED: test_unknown_page_height_falls_back_deterministically failed on the missing note (1 failed, 25 deselected); GREEN: full suite 60 passed + 13 subtests. Plan D6 option (a) sentence updated.
- 2026-10-03 Task 4: --export-md wired through process_prospectus (export_md last parameter, stale .md removed, written for every audit status per D2), CLI (--export-md, --export-all), BatchConfig.write_md (default True per D7) and the TUI. Plan code verbatim; line references were off by a few lines (pipeline essentials write at 233, signature 185) and were applied by text match. No PDF hashing: status line shows `not recorded`. RED: 5 failed, 26 passed (export_md TypeError, stale .md still present, KeyError export_md, BatchConfig has no write_md, SystemExit 2 on --export-md). GREEN: full suite 65 passed + 13 subtests, self-test 80/80, --help lists --export-md.
- 2026-10-03 Task 5 (partial): step 0 commit 851ab17 (fallback-order test now has a TOPLEFT text the old frame guess ordered after the table; fails with approximate handling reverted, passes on current code; plus single-origin-not-approximate test). scripts/prospectus_course_compare.py committed as a reusable single-command tool (--golden --work --base-ref default 69ca855 --semantic-doc --limit --jobs; old side in a git worktree under TEMP, both sides in parallel); unit tests tests/test_prospectus_course_compare.py. --limit 2: 2/2 identical, markup cell-count check passing. Full 44-input run LAUNCHED DETACHED (PID 30728), log $env:TEMP\phaseb-compare.log, work folder $env:TEMP\phaseb-full, old worktree $env:TEMP\bintanong-compare-69ca855 (remove with git worktree remove --force after the run). RESULT PENDING (44/44 identical and the md stats are recorded when it finishes).
- 2026-10-03 Phase B course audit: scripts/prospectus_course_audit.py (+ tests/test_prospectus_course_audit.py, 11 tests, red then green) checks every course of the 44 cached runs across JSON, markup twin and PDF text layer; measure-only. Outputs E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\course_audit_2026-10-03\ (course_audit.jsonl, course_audit_summary.md). 44 paths / 39 distinct PDFs, all mapped and SHA-256 verified. 44 paths, 2031 courses: A_prov 2031/2031 match; A_title 1956 match, 1 loose, 53 transformed, 21 fail; A_prereq 18 fail; B_code 42 fail, B_title 126 fail (Architecture file 01: 19 of 77), B_units 8 fail and 24 not checked; C (printed code nobody claims) 192 silent, 278 flagged; D (md code cell nobody claims) 71 silent, 145 flagged. md cell count equals evidence cell count in 44/44. Needs human reading of the silent list before OCR reuse.
- 2026-10-03 Codex Phase B review fixes (all verified by a failing test first, suite 80 -> 93 passed). (1) a24efe2 source fidelity: the markup twin renders NormalizedCell.raw_text, which loader.docling_to_normalized_table already sets to the unmodified Docling string (text = clean_str(raw_text)); no code reads .raw_text for parsing (only evidence.py as_evidence_dict output and the renderer), so no new field was needed for cells. Text items gained an additive "raw_text" key beside the cleaned "text" and render from it. On the 44 cached inputs raw_text == text for all 9820 cells (clean_str is a no-op there) but 48 of 521 text items differ and now show the original. Empty text items stay dropped by the loader: the cached data has none (0 with or without a position), so nothing printed is lost; revisit if Docling ever emits positioned empty items. (2) e15cbe8 cells never vanish: a cell whose start is outside [0,rows)x[0,cols) goes to the unplaced list (negative starts were classed as placed and vanished); a span cut to the grid carries data-span-clamped="declared_rows,declared_cols". (3) same commit: data-page and the page comment are escaped (comment text cannot contain -->). (4) 42a5d2b comparer gate: both-sides-nonzero and neither-wrote-candidate.json are failures; markup cell ids (data-cell plus data-unplaced-cell) are compared as an exact multiset against ids derived from the cached Docling JSON; paths are resolved absolute before subprocesses; a reused worktree must be at the requested ref's commit. Re-run: 44/44 identical (exact id check on). Course audit on fresh new\NN outputs (course_audit_2026-10-03b): every headline number identical to course_audit_2026-10-03 (check A uses cell text, and cell raw_text equalled text on all inputs); scripts/prospectus_course_audit.py needed no change.
- Known limitations (Phase B, not fixed): (i) a table whose cells span two pages is rendered whole at its first page's position, because splitting it would break the HTML table; Docling normally splits page-crossing tables. (ii) batch --skip-existing checks only JSON + essentials, so a missing _prospectus.md is not regenerated; owned by Phase D (note added to plans/2026-10-03-prospectus-phase-d-safe-cache.md). Not a defect: the status line's `pdf_sha256: not recorded` is the agreed cross-phase rule.
- 2026-10-04 Task 6 done (human visual check, 3-4 October 2026, all 39 distinct prospectuses, E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\markup_twin_visual_check_2026-10-03\all\ with INDEX.md). Verdict: first-year rows render fine; the year/semester banner rows are broken, with banner text overflowing into course names or misaligned. Diagnosis agreed with the user: the renderer is faithful (it renders Docling's raw cells, not the JSON); the defect is in Docling's table structure, which merges banner text into neighbouring cells (Architecture cell "FIRST YEAR FIRST SEMESTER SECOND SEMESTER" attached to AD-1/L; BSCS t0-c9 "FIRST SEMESTER Discrete Structures 1 1"), and the parser inherits it. Not every degree is equally affected. Follow-up: Phase B2 (year/semester verifier and fixer with a human decision ledger), then a parser banner-split repair.
- 2026-10-04 Task 7 done: decision record docs/decisions/prospectus-markup-twin.md. Codex step skipped because the review already ran (fixes a24efe2, e15cbe8, 42a5d2b). Phase B complete. Next: Phase B2.

## Phase B2: year/semester verifier and fixer (branch feat/prospectus-phase-b2-section-fixer)

Plan: plans/2026-10-04-prospectus-phase-b2-section-fixer.md. Decisions D1-D9 in the plan assumed as recommended unless noted here (user accepted all provisionally; D1 sheet format may still change before Task 8). Base `$B2_BASE`: 58d4bb681fed946128e4b86aa19e49a60f030f3e. Baseline: 93 passed + 13 subtests, self-test 80/80.

| Task | Status | Commit | Evidence |
| --- | --- | --- | --- |
| 2. Move course checks | done | 4ff5043 | red: collection error; after move 1 failed 12 passed; green 13 passed; audit smoke identical; full suite 95 + 13 subtests; full 44-run audit (course_audit_2026-10-04_task2) summary byte-identical to 2026-10-03b, JSONL 21040 rows same order, only change is the new occurrence key on the 470 C rows |
| 3. Banner helpers, fixtures, verifier core | done | 8ef487b | red: ImportError has_banner_text; green 17 passed; full suite 112 + 13 subtests, self-test 80/80. Test proves CC 1/L, CS 2, CC 3/L are not flagged though banner cell t0-c9 is in their provenance (own_role_cells) |
| 4. Fix proposals | done | 72585d4 | red: ModuleNotFoundError fixes; 1 failed 19 passed before the verifier edit; green 20 (37 with verify); full suite 132 + 13 subtests |
| 5. PDF checks, unclaimed codes, placement | done | see git log | red: ModuleNotFoundError placement (9 failed + 1 passed once the module existed; plan listed 7+1, two extra tests added: json-only never pdf_checked, y-flipped PDF box not placed); green 47 (verify+fix+pdf tests; plan said 45); real data matches the 3 Oct course audit exactly (all 5 smoke rows, 62 of 114 titles get a proposal); Architecture 10 sampled title proposals all correct against the printed row; full suite 142 + 13 subtests |
| 6. Decision ledger | done | 05329f5 | red: ModuleNotFoundError ledger; green 10 (plan 9, plus test_ledger_lines_are_lf_utf8_with_sorted_keys_on_every_platform); full suite 152 + 13 subtests (plan 149, +2 from Task 5, +1 extra test) |
| 7. Materialise | done | 7f72771 | red: ImportError materialise; green 6 (plan 5, plus test_the_raw_candidate_file_is_byte_identical_after_materialising; 16 with the ledger tests); full suite 158 + 13 subtests (plan 154, +2 from Task 5, +2 extra tests). Commits: Task 6 05329f5, Task 7 7f72771 |
| 8. Review sheet render/parse/check | done | 6cd1a77 | red: ModuleNotFoundError sheet; plan tests green 11; then 15 added tests (owner-editing safety: pipe/backslash round trip, CRLF/BOM/trailing-space/realigned-table parse identity, exact column count, line numbers in every rejection, row moved between sections, duplicate row/section, stray row) of which 5 red before parse_sheet/check_against were hardened (line numbers, exact 11 columns, duplicate and stray detection); green 26; full suite 184 + 13 subtests (158 + 26) |
| 9. Decisions to entries | done | f37eac2 | red: ImportError build_entries; plan tests green 20 (46 with the sheet tests); then 14 added test cases for owner safety (zero entries from an untouched or editor-resaved sheet, per-section bulk confirm counts and header-line-only edit, re-apply twice writes nothing, unknown decision words and every build error name their line); 8 red before build_entries errors carried line numbers (one red was a wrong expectation in my test, fixed); green 60; full suite 218 + 13 subtests (184 + 34; plan expects 185 + 4 offset from earlier tasks = 189 before the 29 extra test cases of Tasks 8 and 9: 15 + 14). Real-data check (throwaway $env:TEMP\b2-real-sheets): BSBA-HRM (NN 16) 8 sections (7 clean, 1 review) and Architecture (NN 01) 10 sections (1 clean, 8 review, 1 broken) render with the PDF text checked, parse back with no differences, and an untouched sheet yields 0 entries. |
| Review fixes A | done | 4fbc9d3 | Two independent reviews of Tasks 1-9, 10 items, all reproduced red first. A (verify, fixes, text): term_mismatch warn when a move_term proposal exists (a section with one is no longer clean and `confirm: yes` refuses the row); `SEM.` is a banner unit; a bare ordinal before an all-caps word stays ("FIRST AID"); strip proposals only for banner words the table prints in a banner cell, otherwise banner_leak is a warn with no proposal; section order sorts on (term_index, year, semester), checked under 6 PYTHONHASHSEEDs. Suite 227 + 13 subtests. |
| Review fixes B | done | 20d7be2 | B (fixes, placement; the plan named course_checks.py but locate_in_page lives in placement.py): a PDF title proposal drops a trailing "Total" and the units figure before it (run 39 `ES` now "Environmental Science"; 67 proposals before and after, one changed); a printed code whose glyphs are more than 2 median glyph widths apart is not a code (contiguous runs measured at gap ratio <= 1.1, split ones >= 4.9): unclaimed_code 338 to 322 across the 44 outputs, 16 rows gone (Law 3, Self 3, IT Era 3, Care 3, Mind 3, RLE 2/4, Tax 3, TQM 3 and others), run 44 broken to mixed. Suite 230 + 13 subtests. |
| Review fixes C | done | a71467d | C (ledger): lines split on newline only (U+2028/2029/0085 round-trip in value, reason, reviewer), BOM and CRLF tolerated; make_entry refuses unknown fields and unappliable corrections; undecidable lines on read are skipped with `invalid_entry: ...` in the materialise report and counted in content_review_state.invalid_entries; signature includes pdf_sha256; write_corrected(raw_candidate=) refuses the raw path. Suite 236 + 13 subtests. Real-data triage over the 44 outputs before (bde999e) versus after: health clean 1/1, warnings_only 3/3, mixed 20/21, broken 20/19; sections broken 145 to 141, review 51 to 54; flag counts identical except unclaimed_code 338 to 322. Real sheets NN 16 and NN 01 re-rendered, parse back clean, untouched sheet writes 0 entries. |
| 10. CLI, reviewer, outside-Git guard | done | 0ef1f7d | red: ImportError fixer_cli (collection error); green 16 (plan 12: +4 tests for the guard, raw-candidate refusal, missing reviewer, missing sheet); shim keeps cli.main and text.DASHES, shim --self-test 80/80; full suite 253 + 13 subtests with the e2e. Adapted: write_corrected(raw_candidate=args.candidate); sheet problems exit 1 (plan: 2), IO/usage 2; sheet and candidate read as utf-8-sig; OSError caught as exit 2; stdout errors=replace; longer --help. |
| 11. End to end, trial sheets, triage | done | fde8a3e | e2e passes at once and fails (`assert ... == reviewed`) with the reviewed rule disabled; triage table gained a PDF column (test first, red then green). Trial folder E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\review_trial_2026-10-04\ : 16_BSBA-HRM warnings_only, 33_BSCS-2025-2026 mixed, 01_Architecture mixed (17 title proposals), 13_BSE-Innovation-and-Tech broken, each with PDF, twin, JSON, sheet; HOW_TO_REVIEW.md; triage_all_39.md = clean 1, warnings_only 3, mixed 18, broken 17 (plan 1/3/17/18: review fix B moved one prospectus from broken to mixed). Innovation unclaimed_code 74 (plan 76: split glyph runs dropped). Demo loop on a copy of Architecture: 13 ledger entries, 3 titles corrected, raw JSON SHA-256 unchanged, partially_reviewed, re-apply 0 new. |
| Codex review fixes 1 (items 1, 2, 12) | done | 9de2c7b | A strip_banner proposal now needs its remainder printed elsewhere without a banner next to it (another source cell or the PDF row text), so `FIRST SEMESTER PRACTICUM` and `FIRST SEMESTER Galactic Mechanics` get no proposal; glyphs of one printed code must share a text line (placement `_same_line`). Real data over the 39 distinct PDFs: health 1/3/18/17 before and after, strip proposals 0 and title_from_pdf 62 before and after, unclaimed_code 303 to 263 (40 rows of codes wrapped over two lines or glued across a line wrap now not reported). Two old tests that faked a leak printed only inside the banner cell now give the PDF row text. |
| Codex review fixes 2 (items 3, 4, 5) | done | be73759 | `confirm: yes` is refused, with the line number and flag kind, on a section carrying a section-level error or warn flag (unit_total); a repeated confirm, accept or reason line in one section is a line-numbered error; a decision cell that is only `: reason` is a line-numbered error instead of an IndexError. |
| Codex review fixes 3 (items 6 to 11) | done | 625423f | Ledger: unreadable lines come back as `_unreadable` placeholders, skipped and reported with their line number (status prints them on stderr, materialise lists them), never fatal; locator fully type-checked; reviewer, recorded_at, pdf_sha256 and disposition required on read; a newline is written before an append when the last line has none. CLI: a declared or file hash that differs from the candidate's run_identity hash exits 2; the Git guard checks the output file (resolved, so a symlink counts as its target), not its folder. Suite 277 + 13 subtests. |
| Codex re-review fixes A (ledger) | done | 81763ab | A ledger line must carry `entry_id`, `old_value`, a non-empty `reason`, reviewer, time and PDF hash, else it is a reported invalid entry (a missing `entry_id` used to KeyError in `materialise`); `make_entry` refuses a blank reason; `read_entries` splits the raw bytes on newline and decodes each line alone, so a non-UTF-8 line becomes an `_unreadable` placeholder with its line number (BOM and CRLF still tolerated). Known, unverified risks, not fixed: the output-path git guard resolves a path before the later write (a junction swapped in between could redirect it), and a hard link to a tracked file is not seen by `resolve()`. |
| Codex re-review fixes B (banner, wrapped codes) | done | c68bab4 | A strip proposal is now evidenced only by this course's other source cells or by this course's own PDF row band (from its code to the next known code, ending at its first units token), so a PRACTICUM in another row no longer authorises it. A code wrapped over two adjacent lines (each segment contiguous, extents within 30 pt) is no longer dropped: it is an `unclaimed_code` WARN item (`confidence: review`); segments far apart (units column) or over three lines are still dropped. Real data: of the 40 dropped codes, 34 are now review items and 6 stay dropped; health counts on the 44 outputs unchanged, unclaimed_code flags 276 to 316. |
| Codex Phase C review item 5 (stale decisions) | done | see git log | `content_review_state` and `materialise` now drop a decision whose `old_value` no longer matches the current row (`row` entry: the course snapshot; field entry: that field; unclaimed: the printed code) before counting or applying it, via `ledger.split_stale`. The state reports `stale_entries` and `stale_lines` (file line numbers; `read_entries` returns `LedgerLine` dicts that remember theirs); `materialise` lists them as skipped `old_value_changed`. A stale accept no longer masks a valid correction on the same field. Trial sheets 01, 16, 33 still `check_against` cleanly. |
| O1: ledger corrects units and prerequisites | done (ledger and materialise; sheet not extended) | see git log | `make_entry`, `entry_problem` and `materialise` accept corrections to `lecture_units`, `lab_units`, `total_units` (finite numbers, not negative, not bool) and `prerequisites_raw` (text, empty allowed), through the same stale `old_value` check. `COURSE_FIELDS` (code, title, term) is unchanged, so review state and old `row` entries (whose old value is the three-field snapshot) read exactly as before. Units are written into the course's `units` dict and `prerequisites_raw` into the course; the `finalize_courses` call that `materialise` already makes re-derives the flat unit fields, `prerequisites`, `prerequisites_unresolved` and `standing_requirements`, and the edges are rebuilt after it, so no stale derived field survives and no new code was needed for it. A corrected `lecture_units` or `lab_units` does not rewrite `total_units`; the reviewer corrects the field they mean. Sheet: not extended, because new columns change `COLUMNS` and every sheet already handed out (trial sheets included) would fail the column-count check; it needs a sheet-version bump, a separate task. |
| Codex final gate A (ledger: items 1, 2, 3, 5, 6, 7) | done | see git log | `entry_id` must equal `entry_id_of(entry)`, the same hash `make_entry` always used, so old honest ledgers read unchanged and an edited `new_value` or `old_value` is an invalid entry (no id-scheme change, so no version bump). The stale check uses `same_value`: a bool is never a number, int and float compare by value, containers recurse. Units are whole numbers 0 to 99 (`type is int`): `parse_units` reads at most two digits, the extractor derives every unit as an integer and `verify` formats totals with `+d`, and no cached prospectus prints a fraction, so fractions are refused rather than supported; this also removes the `OverflowError` and the `+d` crash (error text truncates huge values). Unresolved decisions on any correctable field keep the state partial. Decisions whose course is absent are `orphan_entries` (skipped `course_not_found`), never counted, and a candidate with 0 courses is never `reviewed`. |
| Codex final gate B (banner band: item 4) | done | see git log | A strip's PDF row band also ends at the first course-code-shaped token (upper-case prefix, so `Calculus 1` is not one), known or not, as well as at the units token and the next known code. Real data on the 44 outputs: health and every flag count unchanged. Trial sheets 01, 16, 33 still `check_against` cleanly. |
| Codex re-gate fixes (items 1 to 4) | done | see git log | `same_value` is fully type-strict (int 0 and float 0.0 differ; bool is never a number). Ledgers written before 12a780f with float unit values are reported invalid, by design (reason names the float; no migration: no real ledger holds one, the demo ledger was a throwaway copy and the trial folder has no decisions). Messages describe values with `_short` (type, bit count or truncated text), never `repr` of an unbounded value, so `10**10000` or a megabyte string cannot raise. A strip's PDF band no longer ends at a code-shaped token that starts inside the course's own remaining title (`PE 1 Rhythmic`); a code-shaped token elsewhere before the units figure still ends it, so the `OTHER 2` cross-row case stays blocked. `entry_id` is tamper-evident only against accidental or careless edits, not a deliberate forger (who can recompute it); fine for a local single-user ledger, stated in the ledger docstring, and not to be claimed as more. |
| Codex re-gate regression (banner strip, strict) | done | see git log | A title strip whose remainder starts with a code-shaped token (`PE 1 Rhythmic`) proposes nothing, known code or not: without layout, the course's own title and the next row's unknown code cannot be told apart, so the row stays flagged (`banner_leak`) for a human. This replaces the previous "own remainder keeps its band" exemption (which let the next row's words authorise a strip); `row_bands` is back to ending at the first code-shaped token. Code-field strips are unaffected (their remainder is a code). 44-output triage unchanged. |
| Strip evidence anchored (root cause of the band-end patches) | done | see git log | The PDF evidence for a strip is no longer a "band until a code-shaped token" (three patches, still leaky): `anchored_in_pdf` requires the whole tokens `<this row's code> <remainder> <units token or end of text>` side by side, nothing between (a title strip anchors on the course code; a code strip on its own title). `row_bands` is deleted; `ANY_CODE` stays only for the earlier decision that a title remainder starting with a code-shaped token is flag-only. A banner between the code and the remainder gives no evidence either, as before (`CC 1/L FIRST SEMESTER PRACTICUM` stays unproposed). The other source remains this course's own non-banner cells. Reproducers blocked: `OTHER 2`, next-row `PE 1`, `LONGPREFIX 2`, lowercase and digit-only words between. |
| Anchored strip evidence needs the anchor printed once | done | see git log | Page text has no row locality, so the anchored PDF evidence counts only when the row's anchor occurs exactly once on the page: its code for a title strip, its title for a code strip. A repeated anchor (`CS 1 Actual Title 3 CS 1 Discrete Structures 1 3`) gives no PDF evidence, and only this course's own non-banner source cells can authorise. Unicode spaces and line breaks inside a valid span are still accepted (`pdf_clean` and `split` normalise them). All earlier reproducers stay blocked; 44-output triage unchanged. |
| Anchored evidence needs both sides printed once | done | see git log | Both the anchor (title for a code strip, code for a title strip) and the proposed remainder must each occur exactly once in the page tokens; a repeated proposed code (`CS 1 Actual Course 3 CS 1 Discrete Structures 1 3`) or repeated remainder gives no PDF evidence, and only this course's own non-banner source cells can authorise. Supersedes the `once` argument of the previous row. Valid single-occurrence cases and all earlier reproducers unchanged; 44-output triage unchanged. |
| B2-1: source-cell evidence from own non-banner cells only | done | see git log | Codex final gate 7: `_strip_fixes` took evidence from every provenance cell except one equal to the field value, so the shared banner cell `t0-c9` (`FIRST SEMESTER Discrete Structures 1 1`, CS 1's title) authorised `FIRST SEMESTER Structures 1` -> `Structures 1` for CS 2. Source-cell evidence now comes only from the verifier's `own_role_cells` (this course's own row cells), and a cell carrying any banner phrase (`has_banner_text`) never counts. Test `test_l1_...` red (`['Structures 1'] == []`), then green; tests h4, i1, j1, k1 still pass. Suite 321 passed + 13 subtests (with system temp; `--basetemp=.pytest_tmp` inside the worktree makes 11 fixer CLI tests fail on the outside-Git guard, unrelated), self-test 80/80. 44-output triage identical to d7860f4 (health 21/3/19/1, title_from_pdf 67, strip_banner 0, unclaimed_code 316, banner_leak 3, 0 items moved). Trial sheets 01, 16, 33 `check_against` 0 errors. |
| B2-1 follow-up: evidence cells belong to this row alone | done | 12f0509 | Review of f0e0a3d found other rows' words still got through. One guard, `_evidence_cells`: a source cell is strip evidence only if it is a code or title role cell (C3 prereq "CS 1", S3 units "3"), spans exactly the course's row (C2 merged cell), is in no other course's provenance (C1; `shared_cell_ids` over the candidate, passed by the verifier as `shared_cells`; None means no cell evidence), equals the whole remainder (S1 "Structures 2" inside "Discrete Structures 2 2"; `printed_without_banner` deleted), and carries no banner wording in any case or glued/TERM form (S2 "First Semester", "FIRSTSEMESTER", "FIRST TERM"; local regex, `has_banner_text` unchanged). Tests `test_m_*` red first with the strip proposed, then green; each dropped strip leaves `banner_leak` on the row; own-row case and h4, i1, j1, k1, l1 unchanged. Suite 329 passed + 13 subtests, self-test 80/80. 44-output triage identical to f0e0a3d (0 moved; strip_banner 0, title_from_pdf 67). Trial sheets 01, 16, 33 `check_against` 0 errors. |

### Resume point (2026-10-04 12:25, Sonnet session limit hit)

- Branch `feat/prospectus-phase-b2-section-fixer` at 388222d, not pushed; dev at 58d4bb6 (local, unpushed: Phase B merge 165b6a4 + B2 plan 58d4bb6). origin/dev at 69ca855.
- Done: B2 Tasks 1-11 plus review-fix batch (4fbc9d3, 20d7be2, a71467d). Suite 253 + 13 subtests; shim self-test 80/80.
- Open: final review of bde999e..388222d (review-fix batch + Tasks 10-11). The Sonnet reviewer died on the session limit; handed to Codex read-only (output $env:TEMP\codex-b2-review.txt).
- Waiting on the user: Task 12 trial review of `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\review_trial_2026-10-04\` (start with HOW_TO_REVIEW.md). Then Task 13 (parser banner split; changes 1 title; merge only on user go) and Task 14 (decision record, Codex gate, hand-off).
- Also waiting on the user: OCR questions Q8-Q16 (all recommendations pending a yes). Then write the OCR measurement plan (standalone bake-off: Tesseract eng/fil/eng+fil, RapidOCR en/latin/iso:fil; simulated photos of all 43 pages + real photos; scorer = prospectus_extractor.course_checks; review rows in the B2 ledger format).
- Still planned after B2: Phases C, D, E, F (plans committed in plans/2026-10-03-prospectus-phase-*.md; cross-phase rules in the package-split plan).
- Known leftover: audit.py:76 sorts terms by term_index alone (Summer/Mid-Year tie order can vary); fix in Phase C.
- To resume: read this file, `git log --oneline dev..HEAD`, rerun the suite (`uv run --project backend --extra tools --extra dev --with fastapi==0.141.1 python -m pytest -q tests`) before trusting any number here.


## Prospectus review GUI

Branch `feat/prospectus-review-gui` in worktree `Bintanong-wt\gui`, base `31a0d39` (B2 tip `d7860f4` plus the GUI plan). Plan: `plans/2026-10-05-prospectus-review-gui.md`. Phase C is NOT merged in this base (no `PREREQUISITE_STATES`, `annotate_prerequisite_states`, `prerequisite_state`, `extraction_audit` or `authority` anywhere in the extractor package); Task 10 stays blocked until C lands.

### Start check (Task 1)

- Python: main venv `python.exe -m pytest -q tests --ignore=tests/test_api_probes.py --ignore=tests/test_embedding_service.py` from the worktree root: 320 passed + 13 subtests. Self-test 80/80. The package is not installed in the venv; a probe test confirmed `backend.bintanong_tools...` imports from the worktree path.
- Runtime pieces: `pypdfium2` 5.13.0 and Pillow 12.3.0 import. `fastapi`, `uvicorn` and `httpx` are NOT in the main venv (per instruction nothing was installed there). Tasks 1-4 are pure Python. `uv.lock` exists at `backend/uv.lock`; the `review` extra (D2) is not added yet, to be added with `uv lock` when the web tasks need it (Task 7, stop-and-report point).
- Interface names, all as the plan says: `sheet._row_entries` (line 291, one caller in `build_entries`), `EDIT_FIELDS` (3 columns), `ledger.make_entry/append_entries/content_review_state/materialise/write_corrected/correction_problem/split_valid/split_applicable/split_stale/latest_by_field`, `ledger.CORRECTABLE_FIELDS = (code, title, term, lecture_units, lab_units, total_units, prerequisites_raw)`, `verify.verify_candidate/own_role_cells/Row/Section/Flag`, `fixer_cli.resolve_identity/resolve_reviewer/assert_outside_git/default_review_dir/_load`, `markup.render_prospectus_markup`, `loader.load_from_raw_json`.
- Deviation from the plan text: `raw_docling_json` is per course (`courses[i].provenance.raw_docling_json`), not a candidate-level `provenance` key (the candidate has no top-level `provenance`). Same for the page/bbox/source_cells, which are per course.
- Recorded Docling JSON paths: all four exist on this machine (the `E:\...\docling_jsonified_output\task2b_standing_isolated_2026-09-29\...` files), so the twin can be shown for all four.
- SHA-256 of the trial inputs (Task 11 re-checks):

| File | SHA-256 |
| --- | --- |
| 01_Architecture PDF | 72dad4a0384f82228d63c8926e4ae8a1eb14a33497c9952e0f60782083e82666 |
| 01_Architecture JSON | f7990d20f968c7bf87918993e0eb1df728387d0a267957543e84d26ab5019a7a |
| 13_BSE-Innovation-and-Tech PDF | bb565585a24422c40e32b6da98b8389cc45b8be7f6538d5d4040821fb5d150c3 |
| 13_BSE-Innovation-and-Tech JSON | e7a336452e3ef056cb6bfc9ae2ceff632f9141a3ed412cb322251857a13ee64e |
| 16_BSBA-HRM PDF | 10d415d041e9b35e6b264789c78b9868ab1059fea1fbfecb290eaf0a9c92ae16 |
| 16_BSBA-HRM JSON | c973b0515a19a58b6769d0e22e14f93cfa72a305ce6862f4128c33a707da9490 |
| 33_BSCS PDF | 600cb36b362cff598d84c66a11598b07593c0e74e78a62658b3c61c89f5d5664 |
| 33_BSCS JSON | c090eab2d9b5b8f0ddf2f1a48ef80407b0474f6a8f4ce53cafad47402e2c914f |

### Task table

| Task | Status | Commit | Evidence |
| --- | --- | --- | --- |
| 1. Start check | done | see git log | baseline 320 + 13 subtests, self-test 80/80, imports as above |
| 2. One decision builder | done | see git log | red: ImportError row_entries (collection error); green 16 in test_review_gui_decisions.py; full suite 336 passed + 13 subtests; self-test 80/80. Golden of 21 sheet scenarios (ok, unresolved, edit code/title/term, confirm, fix, accept, unclaimed, refusals) captured from the unmodified code into tests/fixtures/sheet_entries_golden.json (generator tests/sheet_golden_scenarios.py) and equal after the change. Trial sheets 01, 13, 16, 33: read-only check_against 0 errors, untouched sheet writes 0 entries, re-rendered sheet byte-identical to the stored one. Deviation: edits for code and title now also go through ledger.correction_problem (they would have raised LedgerError in make_entry anyway; no golden changed). |
| 2A. Ledger write lock | done | see git log | red: ImportError LedgerBusy (collection error); green 14 in test_prospectus_ledger_lock.py (real child processes for the busy, killed-holder, append and apply cases; fake msvcrt and fcntl for both OS branches); full suite 350 passed + 13 subtests; self-test 80/80. Notes: on Windows byte 0 is locked so the holder text is read from byte 1 (a whole-file read raises PermissionError); the venv python.exe is a launcher, so tests take the holder pid from the child, not Popen.pid. fixer_cli apply already exited 2 through the LedgerError handler; it now takes the lock itself so the holder text names the tool and reviewer, and cmd_apply prints the busy error and returns 2. The lock file (decision_ledger.jsonl.lock) is left beside the ledger after release, so Task 7's file-listing test must expect it. |
| 3. Questions and the queue | done | see git log | red: ModuleNotFoundError prospectus_review_gui.questions (collection error; the module had been drafted first and was moved aside to show it); green 20 in test_review_gui_questions.py; full suite 370 passed + 13 subtests; self-test 80/80. Deviations: (1) decided-ness is computed once by decision_index(payload, entries, pdf_sha256) and current_decision(question, latest) takes that index, not the raw entries, because the stale check needs the payload (plan signature: current_decision(question, entries, pdf_sha256)). (2) A printed code the audit lists lands in the SU section (qid SU-U1), not in the term section, in the fixture. (3) In attention order sections stay together (health, then printed section order); a clean section's bulk question leads that section, so it comes after broken and review work, not before it. (4) An unresolved decision is shown but the question stays in the queue. (5) Fixture: S1 already carries an info flag (banner_in_cell), so the info-only bulk test needs no extra setup. |
| 4. Answers and the equivalence proof | done | see git log | red: ModuleNotFoundError prospectus_review_gui.answers (both new test files fail at collection); green 60 (test_review_gui_answers.py + test_review_gui_sheet_equivalence.py, the equivalence file runs 13 sheet-vs-GUI cases x 2 plus materialise, GUI-only fields and idempotence); full suite 430 passed + 13 subtests; self-test 80/80. GUI entries equal sheet entries as JSON, entry_id included, when via is forced; with the default via only via and entry_id differ. Deviations: (1) answer_to_entries honours an explicit via on a section question (default gui becomes gui_section_confirm), which is what lets the equivalence test force the sheet's value. (2) Reason errors use GUI wording (a correction needs a reason; a printed code needs a reason) checked before row_entries, which stays the guard. (3) parse_typed_value takes an optional default_year (the course's year, as the sheet does for a term typed without a year). (4) Section No writes nothing and is not an error; Other is refused. (5) Test-side only: finalize_courses re-sorts corrected courses by term, so the materialise test looks the corrected code up by value. |
| 5. Page rendering and highlight geometry | done | see git log | red: ModuleNotFoundError prospectus_review_gui.render (both new files fail at collection); green 24 (test_review_gui_geometry.py 12 + test_review_gui_pages.py 12 with parametrised cases); full suite 454 passed + 13 subtests; self-test 80/80. The frame test renders a reportlab page with text at a known place and checks dark pixels under the fraction, paper elsewhere and none at the y-mirrored spot. Deviations: boxes_for_question returns {boxes, warning} (not a bare list or warning object) and takes page, item and role_cells as keywords (an unclaimed Question carries no bbox, so the verifier's item is passed in; Task 1-4 files untouched). PageError carries a code (missing_pdf, bad_pdf, bad_page, bad_scale) so the API can map 404 and 422; messages hold the file name only. |
| R1. Batch 1 review C1 (section Yes reverted a correction) | done | see git log | Reproducer before the fix (scratch script): Other on S1-02 title "Intro to Computing", append, S1:confirm Yes, append, materialise gave applied 0 and the title reverted. Fix (D11 clarification recorded in the plan): answer_to_entries takes ledger_entries (required for a section answer, refused without it) and a section Yes writes ok only for courses with no current ledger line on any field (questions.has_decision); a section question whose courses all have a decision is decided (leaves the queue) and a Yes on it is refused with nothing written. red: the 3 new tests plus the existing callers failed (TypeError ledger_entries); a mutation with has_decision forced False made the reproducer and all-decided tests fail for the stated reason (an extra S1-02 entry; S1:confirm still queued); green 83 in the answers, equivalence and questions files; full suite 457 passed + 13 subtests; self-test 80/80. |
| R2. Batch 1 review C2-C4, S1, S4 (the ledger lock) | done | see git log | red (test_prospectus_ledger_lock.py, 5 failed / 17 passed): C2 an unentered lock passed to append_entries while a child process held the real lock wrote anyway (DID NOT RAISE); C4 a relative lock path for the same ledger was refused as "another ledger"; C3 os.write raising ENOSPC after the OS lock left the handle open (fstat did not raise EBADF); S1 ENOLCK from both fake branches became LedgerBusy. Fixes in ledger.py: append_entries raises LedgerError "is not held" for an unentered lock and compares resolved lock paths; LedgerLock.__enter__ unlocks and closes on any failure after the lock is taken and re-raises; only EACCES, EAGAIN/EWOULDBLOCK, EDEADLK and Windows ERROR_LOCK_VIOLATION (winerror 33) mean busy, anything else raises LedgerError "the lock file X cannot be locked (errno N: ...)". S4: the busy tests now spy on os.open and assert fstat gives EBADF; the two-threads test appends the same decision from 6 threads with a slowed ledger read and expects one write and five skips. Mutations in a scratch copy outside the worktree: removing the threading.Lock guard fails the threads test (six writes); removing os.close on a refused lock fails the 5 busy and 2 not-busy tests. green 22 in the lock file; full suite 465 passed + 13 subtests; self-test 80/80. |
| R3. Batch 1 review S5, S7 (answer errors) | done | see git log | red: a blank, whitespace or None reviewer raised LedgerError (or AttributeError) from make_entry instead of returning an answer error (3 cases); a section Yes whose second course failed in row_entries returned the first course's entry together with the error. Fixes in answers.py: answer_to_entries returns "a reviewer name is needed" before any entry is built; _confirm returns ([], errors) whenever any course fails (row_entries already appends nothing on its own error, so the course and printed-code paths needed no guard). green 38 in test_review_gui_answers.py; full suite 469 passed + 13 subtests; self-test 80/80. |
| R4. Task 5 flaky test (whole %TEMP% listing) | done | see git log | red: with a second process creating and deleting files in the real %TEMP%, test_render_is_cached_and_writes_no_file failed 5 of 5 runs (another program's file appeared in the listing). Fix (test only): the test points TEMP, TMP, TMPDIR and tempfile.tempdir at an empty folder under tmp_path, runs in an empty working directory, copies the PDF into its own folder, and checks that those three stay as they were. green: 5 of 5 under the same churn; full suite 469 passed + 13 subtests; self-test 80/80. |
| 6. The twin pane and the JSON pane | done | see git log | red: ImportError MAX_JSON_CELLS from prospectus_review_gui.render (collection error); green 10 in test_review_gui_panes.py; full suite 479 passed + 13 subtests; self-test 80/80. load_evidence never raises (missing file, invalid JSON, non-UTF-8, a list, and a dict Docling refuses each give None and a reason naming only the file); a real DoclingDocument export loads. The hostile-text test parses the fragment with html.parser: no script or img tag and no on* attribute, the text survives escaped, and a cell starting with "> " is not dropped. Deviations: (1) cells_fallback(course, role_cells) and course_json(course, row, role_cells) take verify.own_role_cells like boxes_for_question does, so "own cells" has one definition and a truncated course keeps them; (2) course_json returns {course, flags, truncated} with truncated always present (0 when nothing was cut) and the flags as dataclass dicts; (3) the twin is computed per call here, the once-per-session cache belongs to Task 7's session. The corrupt-JSON test takes about 12 s alone because it imports Docling; in the full suite the import is shared. |
| 7. Session and API | done | see git log | The `review` extra (fastapi 0.141.1, httpx 0.28.1, uvicorn 0.53.0, the `api` pins) is in backend/pyproject.toml; `uv lock` resolved 141 packages and added no new package. Nothing was synced into the main venv; the web tests run in a throwaway venv (`UV_PROJECT_ENVIRONMENT=%TEMP%\gui-review-venv`, `uv sync --locked --extra review --extra dev --extra tools`). red: ModuleNotFoundError prospectus_review_gui.session (the module, drafted first, was moved aside for the red run) and ModuleNotFoundError prospectus_review_gui.app; green 21 in test_review_gui_session.py (main venv) and 19 in test_review_gui_api.py (review venv; the file skips itself where FastAPI is missing). Full suite: main venv 500 passed, 1 skipped (the API file) + 13 subtests; review venv 519 passed + 13 subtests; self-test 80/80. The session holds the LedgerLock from open to close (a second session and fixer_cli apply are refused), reads the ledger once per answer under a threading.Lock and passes those entries to answer_to_entries (ledger_entries), validates the reviewer at open and again before every answer, and guards the ledger, its lock file and corrected_candidate.json with assert_outside_git before anything is created. The file-listing test expects decision_ledger.jsonl, decision_ledger.jsonl.lock and, after materialise, corrected_candidate.json. API: Host must be 127.0.0.1 or localhost on the app port; non-GET requests need X-Review-Token (constant-time compare) and, when sent, the app's own Origin; CSP default-src 'none' with self-only script, style, img (plus data:) and connect, frame-ancestors 'none', base-uri 'none', form-action 'none'; nosniff and no-referrer on every response; Cache-Control no-store except the page PNG (private, max-age=300). Deviations: (1) GET /api/twin returns JSON {html, reason} rather than a bare fragment, so the page can show why the twin is missing; (2) GET /api/queue returns {mode, queue, all} so the page can list decided items too; (3) answer errors are 422 with {errors}, an unknown qid 404; (4) static files are a minimal placeholder page until Task 8; (5) materialise failures are logged to the terminal and the browser gets a message without a path. |
| 8. The page (three panes, keyboard, accessibility) | done | see git log | red: 8 of 12 in test_review_gui_static.py failed against the Task 7 placeholder page (landmarks, names, live regions, alt text, focus and reduced-motion CSS, contrast tokens, key help, the single innerHTML use); green 12 (the traversal test runs where FastAPI is installed and skips in the main venv). Full suite: main venv 511 passed, 2 skipped + 13 subtests; review venv 531 passed + 13 subtests; self-test 80/80. Contrast is checked for 11 text pairs in the light and the dark scheme (all at least 4.5:1). Browser check (Chrome DevTools, review venv, a scratch launcher on the 16_BSBA-HRM trial candidate, PDF and its recorded Docling JSON, read-only; review dir under the E: scratch folder review_gui_browser_2026-10-06, which now holds 3 browser-check ledger lines): the page, CSS, JS, twin, state, queue, question and page PNG all loaded 200; the twin rendered; y then Enter saved one line and moved on; j moved to the next question; o, typing a code and Enter without a reason showed "Not saved: a correction needs a reason" in the alert with aria-invalid on the field and the reason; with a reason it saved 2 lines; 1 copied proposal a into the title field; Escape inside the field closed the Other form and returned focus to the radios; z switched to scale 3 and back; p switched to printed order; ? focused the key list; / focused the filter; ArrowDown and k moved; Tab went skip link, print-order button, materialise button, filter; the five boxes sat exactly on GE-STS's code, title and unit cells (strong) and the two banner cells (dashed). Fixed during the check: the Other fields showed while hidden (a display rule beat [hidden]; added [hidden] { display: none !important }), the browser's favicon request logged a 404 (GET /favicon.ico now answers 204), and onKey assumed an Element target. After the fixes the console was empty on load and on key use. The only console error left in the session was the browser's own log line for the deliberate 422 rejection. Not checked: a real screen reader, 200 % zoom (the narrow-window stacking was seen), and Firefox or Safari. |
| 9. Command line, startup guards | done | dbcd575 | `python -m backend.bintanong_tools.prospectus_review` (also `-m ...prospectus_review_gui`): arguments as the plan, no `--host`, binds 127.0.0.1 on a socket made by `bind_loopback` (default port 8765, 0 for any), per-launch token from `new_token()`, `open_session` runs the identity, reviewer, outside-Git and ledger-lock guards before the port is bound; port in use, a held ledger ("in use by ..."), a missing or blank reviewer (a blank flag falls back to `git config user.name`, as the fixer does, and is refused when that is empty too), a wrong or missing PDF and an unsafe folder all exit 2; the session is closed on every exit. The four files came from an earlier stopped agent; its 13 tests already passed against them, so red was shown on a mutated copy in scratch (LOOPBACK 0.0.0.0, a `--host` option, port 9999, a fixed token, no reviewer check): 9 of 19 failed. Added 6 tests (default port, blank reviewer, missing PDF, per-launch token and token-required writes, no external URLs, package `-m`): 19 in test_review_gui_cli.py. Green: review venv 208 review-GUI tests; main venv 511 passed, 3 skipped (the FastAPI files), 13 subtests; self-test 80/80. Cross-platform: portable code only. Linux and macOS were NOT run; the suite ran on Windows only. Tests that catch the usual differences: `test_no_posix_only_calls` (source scan), the cp1252 console test, the spaces-and-unicode path test, LF ledger writes, the injected `msvcrt`/`fcntl` lock tests. A CI matrix (ubuntu, macos, windows) is still to be added with the Docker/CI work and must run this suite including the cross-process lock tests. |
| M. Merge dev (5c34fd7) into the GUI branch | done | 4f894dd, 0de45ef | Conflicts: the progress file (kept both sections) and `backend/uv.lock` (took dev's side, then `uv lock`, never hand-merged); `pyproject.toml` merged on its own (the `review` and `ocr-cpu`/`ocr-gpu` extras are all present). Gates on the bare merge: main venv 1231 passed, 4 skipped; self-test 80/80; review venv 207 passed and 1 failed: `test_identity_mismatch_exits_2` wrote the old `file_sha256` key, but Phase D records `pdf_sha256` (fixed in 0de45ef). |
| F1. PageRenderer pdfium lock (C1, HIGH) | done | 3e56f90 | red: `test_concurrent_mixed_calls_do_not_crash_pdfium` (12 threads, size/rotation/png at varying scales, in a child process) exits 3221226356 (0xC0000374). Fix: one module-level `RLock` around open, size, rotation, png (and its cache) and close. Green. |
| F2. Unencodable and control text, size caps (C2, S5, S6) | done | 24b544b | red: 3 answer-layer tests, 1 ledger test, 2 API tests. `answers.text_problem` refuses lone surrogates and any control character (NUL, newline, tab) in typed values, reason, note and qid (422, nothing written); reason and note are capped at 2000 characters (422); `/api/answer` body is capped at 64 KB (413, also when the length is understated or absent); `append_entries` encodes every entry before the file is opened (test: 2 good entries plus one with a surrogate leave the file byte-identical). |
| F3. `next` after an answer (C3) | done | b692a62 | red: attention and print tests, and a wrap-around/only-one-left test. The request carries `mode` (review.js sends it); `next` is the first question after the answered one in that mode, wrapping, never the answered one, `None` when it is the only one left. The older test that asserted the old behaviour was changed. |
| F4. Arrow keys and the key map (C4, S4) | done | 2af86f7 | The key map is now `static/keys.js` (`keyAction`, pure), tested under node by `tests/test_review_gui_keys.py` (21 cases; skipped without node). Scratch mutations fail it: the typing guard replaced by `if (false)`, and the radio/arrow line removed. There is still no browser run of the page. |
| F5. Concurrent-answers test (S2) | done | 6900a21 | The test now counts threads inside the ledger read that starts `answer()`; with `with self._write_guard:` replaced by `if True:` in a scratch copy it fails (peak 16, expected 1). |
| F6. Docling JSON cross-check (S1) | done | ab9bf8a | Cell ids alone prove nothing (a BSCS JSON had every id the BSBA-HRM candidate records: 243 of 243 ids found, 205 with other text), so `evidence_mismatch` compares id and text of every recorded source cell. On a mismatch the evidence is dropped, the twin says why, `state.docling` carries the warning and the page shows it. The right JSON for BSBA-HRM gives 0 differences. |
| F7. CLI port wiring and startup failures (S3, S7) | done | 625ec4a | S3 test goes through `review_main`: Host and Origin with another port are 403; with `port=port` removed in a scratch copy it fails. S7: a failure in `state()`, `twin()` or `create_app` after the bind closes the socket, prints one line, exits 2; the test checks the port can be bound again and the ledger lock is free. |
| Gates after F1-F7 | done | 625ec4a | Main venv 1248 passed, 4 skipped, 13 subtests; review venv (`-k review_gui`) 233 passed; self-test 80/80. |
| F8. Review fix batch 4f894dd..8818444 (D1, D2, D3) | done | see git log | red 3 failed (new API tests): D1 a chunked body with no Content-Length raised KeyError (500), now processed, or 413 over 64 KB; D2 a lone surrogate in an edit key or proposal letter was echoed into the 422 message and could not be encoded (500), now refused by `text_problem` in `_answer_from`, and a deeply nested body (RecursionError) is a 422; D3 typed edit values are capped at `MAX_REASON` (2000) characters (422, nothing written; 200-character titles and Filipino text still accepted). green: review venv `-k review_gui` 236 passed (233 + 3); main venv 1248 passed, 4 skipped, 13 subtests (the API file skips there); self-test 80/80. |

## Phase C: status separation (branch feat/prospectus-phase-c-status-separation)

Plan: plans/2026-10-03-prospectus-phase-c-status-separation.md. Decisions D1-D8 taken as recommended. Base `$BASE_REF`: 6846da4 (tip of feat/prospectus-phase-b2-section-fixer; B2 unmerged). Deviations from the plan: (1) base is 6846da4 not dev, so `ledger.content_review_state` exists and feeds `content_review` when a ledger and a source hash are passed; with no ledger it stays `pending`. (2) The Phase A gate test is already gone (Test-Path False). (3) audit.py:76 term sort gets a deterministic secondary key. (4) Schema v3.1 as planned. (5) Task 7 uses `scripts/prospectus_course_compare.py --base-ref 6846da4` instead of a new status comparer (cross-phase rule 2).
Baseline: 271 passed + 13 subtests with tests/test_api_probes.py and tests/test_embedding_service.py ignored (no fastapi in this venv; 277 counts those); self-test 80/80. D3 probe printed `error blocked 0` (premise holds).
Anchors: pipeline.py build_payload line 26, blocked Prolog 60-70, payload literal 74, build_essentials 130, process_prospectus 175; as the plan said except +/- a few lines.

| Task | Status | Commit | Evidence |
| --- | --- | --- | --- |
| 1. Start check | done | 1418b3d | baseline 271 passed + 13 subtests (2 fastapi files ignored), 80/80; D3 probe `error blocked 0` |
| 2. Prerequisite states | done | c7e7cc5 | red: ImportError EXECUTABLE_PREREQUISITE_STATES; green 15; mutation (`if False` for NULL_TOKENS) fails the 2 stated_none cases; suite 286 |
| 3. Prolog rule_complete | done | 9139dd4 | red: 8 failed; green 23; mutation (drop rule_complete from eligible/2) fails the swipl test; swipl present; suite 294, 80/80 |
| 4. Metadata observations | done | b6bedf3 | red: KeyError observations (2 failed); green 25; suite 296 |
| 5. Authority block, source, essentials, v3.1 | done | e7242a2 | red: 15 failed (TypeError approved_scope/source/review_entries, KeyError authority, schema v3.0); green 40; mutations (drop content_review_pending, drop hash check) each fail one test; suite 311. Added beyond plan: `review_entries=` feeds `content_review` through `ledger.content_review_state` (needs `source` for the hash; entries for another PDF do not count) with 3 tests and a `content_review_incomplete` blocker |
| audit.py tie order | done | 810f2ca | red: both `Summer`/`Mid-Year` orders seen across 16 PYTHONHASHSEED subprocess runs; green after key `(term_index, year, semester)` (years also `(order, year)`); suite 312 |
| 6. Docs | done | 216bcb7 | audit.py comment, `__init__` docstring, docs/decisions/prospectus-status-separation.md |
| 7. 44-input regression | done | see git log | comparer `--base-ref 6846da4`: 44/44 identical; field diff matches the plan table exactly (prolog.clauses 6, schema_version 44, 8 added keys x 44, prerequisite_state 2031 + 2031); 38 blocked; outputs under dump\scratch\phase_c_2026-10-04\ |
| 8. Review gates | not run | | Reviewer agent and Codex gate not run in this session; open |

Deviations: no new `prospectus_status_compare.py` (the existing comparer plus a scratch field diff were used, per cross-phase rule 2); `sections.py` and `scripts/prospectus_course_compare.py` untouched. Known limits as in the decision record. Suite at the end: 312 passed + 13 subtests (2 fastapi-dependent files not collectable here), self-test 80/80. Next: Phase D (it must keep the `prolog.clauses` comparer allowance in mind).

### Phase C review fixes (4 October 2026)

| Finding | Commit | Red / green |
| --- | --- | --- |
| A. incomplete rule reachable (dropped text read as resolved) | 630ae53, 2972f27 | red: 10 failed (9 synthetic cells end to end plus a classifier-only test; ENTRE 15 `ENTRE 14 units: 159` also moved on real data); green after unconsumed_prerequisite_text; mutation (leftover forced empty) fails the same 10; the second commit widens code matching (spacing, leading zero, lab marker) after the first real-data run wrongly demoted 11 courses (red: 3 failed) |
| B. only exact `verified` source counts | 3a256fe | red: 5 failed (rejected, failed, empty, None, Verified); hash-check cases already blocked (7 passed) and are now locked by tests |
| C. positive eligibility test | 4cd3db5 | passes at once by design; mutation: constant False fails 1, constant True fails 24 |
| suspicions: assumed campus, ledger without source | 088b8a8 | red: 2 failed; green |
| D. status report in the shared comparer | 7870c66 | red: AttributeError (2 failed); green 12 in test_prospectus_course_compare.py; additive block before main, flag --status-report; the scratch status_diff.py is no longer used |

Real data (44 inputs, comparer `--base-ref 6846da4 --status-report`): 44/44 identical, same key table as before (prolog.clauses 6, schema_version 44, 8 added keys x 44, prerequisite_state 2031 + 2031). Prerequisite states: blank_unreviewed 1005, resolved 689 (was 696), unresolved_reference 253, standing_condition 59 (58), unreadable 20 (14), alternative_or_exception 3, stated_none 2. The seven courses that left resolved are listed in the decision record. Suite 352 passed + 13 subtests (2 fastapi files not collectable here), self-test 80/80.

### Phase C Codex review fixes (4 October 2026, items 2, 3, 7, 8)

| Item | Commit | Red / green |
| --- | --- | --- |
| 2. audit success reads as verification | c1ba0e7 | no consumer of the old values outside the extractor package and its tests (repo-wide search); red: 3 failed (prolog.status, essentials_extraction_status, TUI labels); green: prolog `extracted`, essentials `EXTRACTED` / `EXTRACTED_WITH_WARNINGS` / `REVIEW_REQUIRED`, TUI "Extraction audit / Content review / Source verification"; audit.promotion_status kept as the documented legacy label |
| 3. RAG blank read as None | b4ff4d9 | red: blank cell rendered None; green: prerequisite line from state, `prerequisite_state` in course chunk metadata; mutation (always None) fails |
| 7. `OR 1` read as the word or | 11e4d76 | red: 3 failed (`OR 1`, `OR 1, CS 1`, `CS 1, IF 2`); green; real alternatives still caught |
| 8. apostrophe in the Prolog test path | 02c63d5 | red: swipl test failed with an apostrophe directory; green with pl_atom; non-test atoms already used pl_atom; header comments collapsed to one line (red: newline broke out of the comment) |

Real data (44 inputs, comparer `--status-report`): 44/44 identical (no course value changed). New diffs against the earlier run: prolog.status changed 6, rag.semantic_chunks.[].prerequisite_state added 304, rag.semantic_chunks.[].text changed 201 (all in the 6 non-error payloads). Prerequisite states unchanged from the last run (resolved 689 etc.). Suite 363 passed + 13 subtests, self-test 80/80. Item 5 (B2 ledger) left to the B2 branch.

### Phase C D2 decision: stated_none by word matching (4 October 2026)

User confirmed `stated_none` stays executable and asked for word matching as a fallback. Commit 3414604. Red: 27 failed (all printed-none variants once the parser's unresolved-token filing was allowed for; the end-to-end test); green 133 in test_prospectus_authority.py. Mutation (disable the early none check) fails 31. 26 positive forms (None, NONE., none required, no prerequisite(s), No pre-requisite, N/A, n.a., -, --, em and en dash, nil, parentheses and brackets, whitespace) and 16 negatives (None, but CS 1 recommended; none of CS 1; N/A for transferees; bare "no"; ...) are tested. Real data (comparer `--status-report`, 44/44 identical): zero courses change state; counts unchanged (blank_unreviewed 1005, resolved 689, unresolved_reference 253, standing_condition 59, unreadable 20, alternative_or_exception 3, stated_none 2). `audit.promotion_status` and `quality_report.promotion_status` keep VERIFIED by decision. Suite 406 passed + 13 subtests, self-test 80/80.

### Phase C final-gate fixes (4 October 2026)

Commit 23c743f. Red: 12 failed (6 contradictory-none cells, 3 bag-of-words cells, the unresolved-override test, the identity test, the full-gates test). Green: 153 in test_prospectus_authority.py. Every reproducer is also run through SWI-Prolog `next_eligible/2` (swipl present, none skipped): `CS 1, none`, `CS 1 and no prerequisite`, `CS 1; N/A`, `CS 1, nil`, `none, CS 1`, `CS 1, -` never offer CC 1 while the control CS 2 is offered; `None; prerequisite required`, `none required? see CS 1`, `no, CS 1`, `N/A - CS 2`, `none none`, `prerequisite required none`, `no prerequisite recommended`, `none (CS 1)` never offer CC 1. The 26 positive and 16 negative none forms still pass; three new positives (no prerequisite required, No pre-requisites required, None required.). Identity: `{'bogus': ''}`, empty values, unknown keys, unobserved fields and unevidenced values give unverified; the full-gates reproducer gives eligibility_executable False; the good case stays True. Real data (comparer `--status-report`, 44/44 identical): zero state moves; counts unchanged (blank_unreviewed 1005, resolved 689, unresolved_reference 253, standing_condition 59, unreadable 20, alternative_or_exception 3, stated_none 2). Suite 426 passed + 13 subtests, self-test 80/80.

### Phase C second final-gate fixes (4 October 2026)

Commit 650ef72. Red: 20 failed (10 punctuated none forms in the shared negative list, 4 end-to-end question-mark cells, the identity value test, 5 colon/period cells); green 184 in test_prospectus_authority.py. SWI-Prolog `eligible/2` and `next_eligible/2` checks (swipl present, none skipped): `no prerequisite?`, `none?`, `N/A?`, `none (maybe)`, `none ???` never make CC 1 eligible; `CS 1: CS 2`, `CS 1. CS 2`, `CS 1.`, `CS 1: `, `CS 1 .. CS 2` never make CC 1 eligible even with CS 1 and CS 2 passed. `None.`, `N/A.`, `n.a.`, `- none -` still match; `(none)`, `[N/A]`, `None;` moved from positives to negatives. Separators in the real data (resolved cells): only `,` (79), `&` (60), `;` (2), plus `/` and `-` inside codes, so no `.` or `:`. Real data (comparer `--status-report`, 44/44 identical): zero state moves; counts unchanged (blank_unreviewed 1005, resolved 689, unresolved_reference 253, standing_condition 59, unreadable 20, alternative_or_exception 3, stated_none 2). Suite 457 passed + 13 subtests, self-test 80/80.

### Phase C third final-gate fixes (5 October 2026)

Commit e282fb4. Red: 13 failed (7 periods-as-content none cells, 5 sentence-period code lists, the ASCII-case identity test); one extra red appeared while implementing (`N/A..`, because the n/a rewrite swallowed a period) and was fixed. Green: 206 in test_prospectus_authority.py. SWI-Prolog `eligible/2` and `next_eligible/2` (swipl present, none skipped): `none...`, `...none`, `none..`, `N/A..`, `no prerequisite...`, `. none`, `none. .` never make CC 1 eligible; `CS 1, CS 2.`, `CS 1; CS 2.`, `CS 1 and CS 2.`, `CS 1.`, `CS 1, CS 2. ` are eligible with CS 1 and CS 2 passed. Identity: `SS`/sharp s, Turkish dotted I/i and non-ASCII case differences are mismatches; `cs`/`CS`, whitespace and NFC variants are consistent. Real data (comparer `--status-report`, 44/44 identical): zero state moves; counts unchanged (blank_unreviewed 1005, resolved 689, unresolved_reference 253, standing_condition 59, unreadable 20, alternative_or_exception 3, stated_none 2). Suite 479 passed + 13 subtests, self-test 80/80.

### Phase C fourth final-gate fix (6 October 2026)

Commit 748230c. Real-data check first: no course code or prerequisite code in the 44 outputs contains a period, and the 21 cells that contain one are standing conditions or unresolved references, none `resolved`, so the strict rule moves 0 courses (no stop needed). Red: 7 failed (`C.S 1.`, `C.S 1`, `CS. 1`, `CS 1.L`, `CS 1. L`, `C.S. 1`, `CS 1./L`); green after removing the period from the matcher's separator class. SWI-Prolog `eligible/2` and `next_eligible/2` (swipl present, none skipped): CC 1 is never eligible for those cells even with CS 1 and CS 2 passed. The spacing, zero, hyphen, slash and lab-marker cases still resolve. Real data (comparer `--status-report`, 44/44 identical): zero state moves; counts unchanged (blank_unreviewed 1005, resolved 689, unresolved_reference 253, standing_condition 59, unreadable 20, alternative_or_exception 3, stated_none 2). Suite 494 passed + 13 subtests, self-test 80/80.

## Phase D: safe cache and output publication (branch feat/prospectus-phase-d-safe-cache)

Plan: plans/2026-10-03-prospectus-phase-d-safe-cache.md. Decisions D1-D6 taken as recommended (D1 two identities, D2 no device, D3 publish an error audit, D4 reuse the identity-checked cache by default, D5 names as listed, D6 no cache publication on failure). Schema target `palsu-prospectus-v3.2`; `MANIFEST_SCHEMA_VERSION` found `palsu-prospectus-batch-manifest-v3.0`, `SCHEMA_VERSION` found `palsu-prospectus-v3.1` (Phase C).

Deviations from the plan's Task 1:
- Base is not `dev` but this integration branch: Phase C tip 81ac0f1 plus `git merge --no-ff feat/prospectus-phase-b2-section-fixer` (B2 tip d7860f4), merge commit 48ea309. The merge was clean (the progress file merged without a conflict; both the B2 rows and the Phase C section are kept, nothing dropped). Phase B and C code are both present; `tests/test_prospectus_split_equivalence.py` is absent.
- After the merge two Phase C authority tests failed (541 passed, 2 failed). Cause: B2's review fixes treat a ledger decision as stale when its `old_value` no longer matches the current row, and Phase C's test fixture `ledger_row_entries` recorded `old_value=None` for `row` entries. The shape of `ledger.content_review_state` did not break authority (it reads only `["state"]` and stores the whole dict as `content_review_detail`; the new keys `stale_entries`, `orphan_entries`, `stale_lines` ride along). Fix is test-only (bf1cb47): the fixture records `course_snapshot(course)`, and a new test checks that stale entries give a state other than `reviewed` and that the three keys reach `authority.content_review_detail`.
- `tests/conftest.py` does not register pytest markers; the OCR branch's `gpu` marker belongs in `backend/pyproject.toml` and is not added here.
- Stub `build_payload` in conftest accepts `**_phase_c_options` so the Phase C keywords (`source`, `approved_scope`, `pdf_hash_check`, `review_entries`) pass through.
- PDF hash single owner: `identity.file_sha256` (Task 2). `course_checks.sha256` (used by the B2 fixer and `resolve_pdf`) now is that function; the fixer's `resolve_identity` reads `run_identity.pdf_sha256` (B2 had read a `file_sha256` key "written by a later phase"; Phase D writes `pdf_sha256`); `prospectus_batch` records its PDF hash through `file_sha256`. `prospectus.ProvisionalSource.verify_pdf` (`hashlib.file_digest`) belongs to the source-record module outside the extractor package and is left alone; `authority` never computes a hash, it receives `pdf_hash_check` from `process_prospectus`.

Merge verification (all from the integration branch):
- Full suite 544 passed + 13 subtests (was 541 + 2 failed before the test fix, 1 test added).
- Self-test 80/80.
- 44-input comparer `--base-ref 81ac0f1 --status-report`: 44/44 identical, prerequisite states unchanged from Phase C (blank_unreviewed 1005, resolved 689, unresolved_reference 253, standing_condition 59, unreadable 20, stated_none 2, alternative_or_exception 3). Outputs under dump\scratch\phase_d_2026-10-06\merge_compare\.
- B2 triage over the 44 outputs: mixed 21, warnings_only 3, broken 19, clean 1; fix proposals title_from_pdf 67, strip_banner 0.
- Trial sheets 01, 16, 33 (`check_against`, read-only): 0 errors each.

Line references re-checked (plan said 8d26f18): `loader.py` `_docling_runtime_fingerprint` 298-305, `_cache_meta_path` 308, `load_document` 312-388; `pipeline.py` `process_prospectus` 218-327 (the stale-unlink loop at 259-267, raw cache path 268); `batch.py` skip test 197-198, pre-warm test 169-172, `force_reconvert=True` at 213; `cli.py` `force_reconvert=True` at 82 and 128 (line 102 is the batch config `force_reconvert=args.force`); `docling_env.py` `get_pipeline_options` 180. The plan's statements still hold. The Phase B markup companion `_prospectus.md` is also unlinked at pipeline.py:265 and must be a publish companion (Tasks 5 to 7).

### Phase D Task 2: identity module
Red: collection error `ImportError: cannot import name 'identity'` for the whole file. Green: 14 passed (test_prospectus_identity.py 9, batch 5; the plan said 7 + 5, two tests added for the PDF-hash owner). Suite 553 passed + 13 subtests, self-test 80/80. D1/D2 implemented: no device in the identity, package hash only in `run_identity`. Deviations: `course_checks.sha256` is now `identity.file_sha256` (the fixer imports it from there), `prospectus_batch` records its PDF hash through it, and the B2 fixer reads `run_identity.pdf_sha256` instead of `file_sha256`; the two B2 tests that wrote the old key (test_prospectus_b2_codex_review.py:218, test_prospectus_fixer_cli.py:68) changed to `pdf_sha256`. `tests/conftest.py` and `tests/test_prospectus_cache.py` are written but held back until Task 4, because conftest imports identity, loader and pipeline.

### Phase D Task 3: one source for conversion settings
Red: `TypeError: get_pipeline_options() got an unexpected keyword argument 'settings'`. Green: test_prospectus_identity.py 10 passed. Suite 554 passed + 13 subtests, self-test 80/80. The option values are identical to the old hard-coded ones. `get_shared_converter` still keys on `(device, backend)` only (noted in the plan for the OCR phase).

### Phase D Task 4: identity-checked raw Docling JSON cache
Red (4 failed, 6 passed; the plan expected at least five): `test_same_path_with_changed_bytes_reconverts` (the old fingerprint reused the JSON of other PDF bytes), `raw_tampered`, the OCR test (`AttributeError: ... loader has no attribute 'conversion_settings'`) and the record test (`KeyError: 'identity_version'`). `wrong_identity` already passed on the old code, for the wrong reason: the old reader compared the whole meta file to a bare fingerprint, so any new-format meta mismatched. Green: tests/test_prospectus_cache.py 10 passed. Suite 564 passed + 13 subtests, self-test 80/80. D1: the cache key is PDF hash + conversion settings only, with no parser hash. D4: `process_prospectus`, CLI and batch still pass `force_reconvert=True` until Tasks 6 and 7; the tests pass `force_reconvert=False` explicitly. `load_document` takes `stage_dir` (unused until Task 6). conftest's stub `build_payload` accepts the Phase C keywords through `**_phase_c_options`, and `conftest.py` registers no pytest markers (the OCR branch's `gpu` marker belongs in backend/pyproject.toml).

### Phase D Codex batch 1 findings D-1..D-5 (review of 81ac0f1..1460536)
Each fix is test-first in its own commit. Tests run with `--basetemp` outside the repository: with `--basetemp=.pytest_tmp` inside the worktree, 11 fixer tests fail because the fixer refuses to write review files to a path that is inside the repo and not git-ignored. That is an environment effect, not a defect (baseline at 1460536 with an outside basetemp: 574 passed, which includes the 10 untracked Task 5 tests).
- D-1 (767c572) `get_shared_converter(device, backend, settings=None)` keys by `(device, backend, canonical JSON of the full settings)` and builds the options from those settings. `load_document` passes the settings it records, for both the docling_parse and the pypdfium2 fallback converters. Red: the second converter `is` the first after `PALSU_DOCLING_CELL_MATCHING` changed; `TypeError: unexpected keyword argument 'settings'`; the loader requested `{'device','backend'}` only. Green 13/13 in test_prospectus_cache.py.
- D-2 (82c06d6) `_write_bytes_atomic` writes through `tempfile.mkstemp` beside the target, then `loader.replace_file` (`os.replace`, 5 attempts with a growing delay on `PermissionError`, then `ReplaceFailed(OSError)` naming both paths; the temp is removed and the target is left as it was). Red: the interleaved-writer reproducer raised `FileNotFoundError ... a_docling.json.tmp`; the retry tests raised a bare `PermissionError` and failed with `no attribute 'ReplaceFailed'`. Green 16/16.
- D-3 and the corrupt-JSON suspicion (b98bf15) `cache_reuse_check` is replaced by `load_reusable_cache`, which returns `(document | None, reason)`: it reads the bytes once, checks the digest on them, and parses those same bytes. A digest-matching cache that is not UTF-8, not JSON, not an object, or rejected by `DoclingDocument.model_validate` (any `ValueError`) is a miss and reconverts. Red: the swap reproducer loaded `%PDF-other`; corrupt caches raised `JSONDecodeError`, `UnicodeDecodeError` and `AttributeError: 'list' object has no attribute 'get'`; the Docling-rejected cache raised `ValueError`. Green 21/21.
- D-4 (eaef785) `load_reusable_cache(raw, meta, pdf_sha256, settings)` derives the expected identity itself, and also requires the record's `pdf_sha256` and `conversion_settings` to equal the current ones. Red: four new damage cases (edited or missing `pdf_sha256`, edited or missing `conversion_settings`) each reused the cache (1 conversion, expected 2). Green 25/25.
- D-5 (c1c6d34) `ProvisionalSource.verify_pdf` calls `identity.file_sha256`, and `prospectus.py` no longer imports hashlib. This reverses the Task 1 note that left it alone. Red: with the owner patched, `verify_pdf` still computed its own digest (`ValueError: PDF hash mismatch`). Green.
- Deviation: the plan's name `cache_reuse_check` is gone; its only caller was `load_document`.
- After the five commits: suite 590 passed + 13 subtests, self-test 80/80. 44-input comparer `--base-ref 1460536 --status-report`: 44/44 identical, prerequisite states unchanged (blank_unreviewed 1005, resolved 689, unresolved_reference 253, standing_condition 59, unreadable 20, stated_none 2, alternative_or_exception 3). Outputs in dump\scratch\phase_d_2026-10-06\dfix_compare\.

### Phase D Task 5: the publish module
Finished from the half-done untracked files an earlier agent left. The code and the 9 plan tests matched the plan. Kept: `OutputNames.markup` (`<base>_prospectus.md`, the Phase B markup twin, a publish companion) and its test (published before the main JSON, removed as stale when a later run does not write it). Red, redone: with `publish.py` moved aside, `ImportError: cannot import name 'publish'`. Two tests were added and went red against the half-done file: `loader.replace_file is not publish.replace_file`, and `publish has no attribute 'ReplaceFailed'`. Change: one retrying replace. `publish.replace_file` (`os.replace`, 5 attempts with a growing delay on `PermissionError`, then `ReplaceFailed(OSError)` naming both paths) is the owner, and the D-2 cache writer imports it. On the final failure it leaves the source in place, so a failed publication can copy the staged file into `failed/<base>/`; the cache writer removes its own temp. Green: test_prospectus_publish.py 12 passed (9 plan + markup + 2). Suite 592 passed + 13 subtests, self-test 80/80. Why the manifest goes last: a file-by-file publish cannot be atomic, so a hash manifest written after every file is the one thing that makes a half-published mix detectable (the old manifest no longer matches the new files).

### Phase D Task 6: process_prospectus stages and publishes
Corrected historical evidence (6 October 2026 pickup): Task 6 contains 14 publication tests, not the previously recorded 15. The authentic original red runtime log is unavailable. An external reconstruction of pre-fix parent `29eb83200b593f24caa9179a28c0795c30621b5a`, overlaid with `f802c764533bdf67267089bcc109416da5941ca9` publication tests/conftest, observed 12 failed, 2 passed. This is reconstructed evidence, not original chronological test-first proof; it supersedes the inconsistent 11-failed/2-passed wording. Historical symptoms were missing `a_publish.json`, changed earlier files (unlink-first), missing `run_identity`, schema v3.1, absent `publish.replace_file` calls and CRLF output. The passing guards refused an output equal to source and removed companions without a manifest. Corrected publication-test count: 14. Historical publication + cache + publish + identity total 61 remains unchanged because the reconstruction does not establish that total. Script/log: external `scratch/codex_resume_2026-10-06/reconstruct_task6.py` and `task6-red-reconstruction.log`.
- Removed: the unlink-first loop (old pipeline.py:257-267) and the direct `write_text` calls. `process_prospectus` verifies the source hash first (Phase C; nothing is touched on a mismatch). It then creates a staging directory `.<base>.staging-<8 hex>` beside the target, converts into it (`load_document(stage_dir=)`), builds the payload, stages every companion through `_stage_outputs`, and calls `publish_staged`. Order: cache JSON, cache meta, essentials, `.pl`, `_rag.jsonl`, `_review.csv`, `_prospectus.md`, main JSON, `_publish.json`. On any exception, `write_failure` copies the stage to `failed/<base>/`, the stage is removed, and the exception propagates. D3: an `error` audit publishes. D4: `force_reconvert` defaults to False (the CLI and batch still pass True until Task 7). D6: nothing is published on failure.
- Markup twin: `_prospectus.md` is staged for every audit status when `export_md` is set, published just before the main JSON, and listed in the manifest.
- Deviation, stale companions: besides the files the previous manifest lists, `publish_staged` also removes every known companion of the base (essentials, `.pl`, `_rag.jsonl`, `_review.csv`, `_prospectus.md`) that this run did not produce. Without that, a set written before Phase D, which has no manifest, would keep a stale `.pl` or `.md` after an audit-error run (`test_md_is_not_written_by_default_and_a_stale_one_is_removed` requires the removal). Cache files and the manifest are never removed. An unlink failure prints a warning.
- Schema: `SCHEMA_VERSION` `palsu-prospectus-v3.1` -> `palsu-prospectus-v3.2`. The payload gains the top-level object `run_identity`: `identity_version, input_kind, input_sha256, conversion_identity, package_sha256, schema_version, semantic_sha256, pdf_sha256, conversion_settings, review_input_only, run_key, cache` (`converted` / `reused` / `not-applicable`), plus `review_note` for a Docling JSON input. `run_identity.pdf_sha256` is the key the B2 fixer reads; a new test runs `fixer_cli.resolve_identity` on a written payload and gets `how == "run_identity"`. The Phase C literal in test_prospectus_authority.py:281 moved to v3.2.
- Line endings: outputs are now written with LF on Windows (`write_text_lf`). Before, the JSON, essentials, `.pl` and `_rag.jsonl` were CRLF. No course value changes. `_review.csv` keeps the csv module's own line ending.
- Suite 606 passed + 13 subtests, self-test 80/80.

### Phase D Task 7: --skip-existing compares identity and audit status
Red (14 failed, 1 passed, tests/test_prospectus_batch_skip.py, after the conftest stub audit gained `declared_total_units: 0`, as the plan allows; without it every first run recorded `error` on a KeyError): the old reason was `output already exists`; a failed audit, changed PDF bytes, a missing companion, a half-published set and a set without a manifest were all `skipped`; `batch has no attribute 'package_sha256'`; `KeyError: 'skip_check'`; the scan returned `failed/a/a_docling.json`; the single-file CLI passed `force_reconvert` `[True, True]`; manifest schema `v3.0`. The one that passed, `test_force_overrides...`, passes because the old batch always reconverted. Green: 15 passed (10 plan + 5).
- `skip_check(item, config, package_hash)` skips only when `--skip-existing` is given without `--force`, a valid publish manifest exists, its `audit_status` is ok or warn (never error), its `run_key` equals the key computed now, every listed file still hashes to its recorded value, and every companion the current flags request is in the manifest. That includes the markup twin `_prospectus.md` when `write_md` is set (the Task 1 note; two tests: missing from the last run, or deleted since). `run_batch` passes `force_reconvert=config.force_reconvert` (D4) and keeps `export_md=config.write_md`. Records gain `skip_check`, `publish_manifest` and, on error, `failed_dir`. `failed` is in `IGNORED_DIR_PARTS`. CLI: new `--skip-existing`/`--force` help; the single-file run passes `force_reconvert=args.force`; `--dump-grid` is unchanged. `--skip-existing` is batch-only; there is no single-file skip. `prospectus_batch.run_isolated` still passes `--force`.
- `MANIFEST_SCHEMA_VERSION` `palsu-prospectus-batch-manifest-v3.0` -> `v3.1`.
- Test deviations: the env fixture stubs `pipeline.render_prospectus_markup`, because `BatchConfig.write_md` defaults to True and the stub payload cannot be rendered. The plan's mtime check in the unchanged-repeat test leaves out `batch_manifest.json`, because `run_batch` rewrites that file on every run, so the plan's version could never pass; `snapshot` already left it out.
- Suite 621 passed + 13 subtests, self-test 80/80. 44-input comparer `--base-ref 1460536 --status-report` on the Task 5-7 code: 44/44 identical; payload `run_identity` added and `schema_version` changed (44 each); prerequisite states unchanged; no staging or `failed/` directories left. Outputs in dump\scratch\phase_d_2026-10-06\task7_compare\.

### Merge of the finished B2 branch (2414252, B2-1 fixes f0e0a3d and 12f0509)
`git merge --no-ff feat/prospectus-phase-b2-section-fixer` was clean: fixes.py, verify.py, test_prospectus_b2_codex_review.py, test_prospectus_fixes.py and this file. The B2 tests keep Phase D's `run_identity.pdf_sha256` key. Suite 630 passed + 13 subtests, self-test 80/80. 44-input comparer `--base-ref f63cdd3 --semantic-doc <meaning map> --status-report`: 44/44 identical. Only `run_identity.package_sha256` and `run_key` changed (44 each, because fixes.py changed); prerequisite states unchanged (1005/689/253/59/20/2/3). B2 triage over the new side (scratch\phase_d_2026-10-06\triage_counts_flags.py): health mixed 21, warnings_only 3, broken 19, clean 1; fixes title_from_pdf 67, strip_banner 0; flags unclaimed_code 316, banner_leak 3. Trial sheets 01, 16, 33 `check_against` (read-only): 0 errors each. Note: the two earlier comparer runs in this section ran without `--semantic-doc`, so both sides used `--no-semantic-doc`; this run uses the meaning map, as the first merge gate did.

### Phase D Task 8: course fields unchanged on the 44 cached inputs (2026-10-06)
Deviation: the plan's throwaway `scripts/prospectus_course_compare.py` (run/compare subcommands) is superseded by the committed comparer of the same name (Phase B). That one already compares course fields and audit counts, runs old and new in parallel, and checks the markup twin; nothing new was written or committed. Base: 189c9ea, the last commit before any Phase D code (B2+C merge 48ea309 plus test fix bf1cb47 plus docs). New: aa95d04 (Phase D Tasks 2-7, D-1..D-5, the B2-1 merge). Command: `scripts\prospectus_course_compare.py --golden <task2b_standing_isolated_2026-09-29> --work dump\scratch\phase_d_2026-10-06\task8_compare --base-ref 189c9ea --semantic-doc <meaning map> --status-report --jobs 6`. Result: 44/44 identical, exit 0. Payload: `run_identity` added and `schema_version` changed (44 each), nothing else. Prerequisite states unchanged (1005/689/253/59/20/2/3). Output file sets differ only by the new `candidate_publish.json` (44 of 44). The base worktree was removed afterwards.

### Phase D Task 9: one real end-to-end failure-injection run (2026-10-06, aa95d04 code)
Real Docling on CPU, venv Python from the worktree root: `-i <in> --batch -o <out> --skip-existing --export-all --device cpu --semantic-doc <meaning map>`. Scratch is under dump\scratch\phase_d_2026-10-06\ (the hard rules keep scratch out of %TEMP%); the folders are kept as evidence.
- The smallest PDF, BS-Marine-Biology-prospectus-template_07.08.2022-1.pdf (78,713 B), audits `error`. Run A: `0 extracted, 1 failed audit` (exit 1); the set was published without `.pl`/`_rag.jsonl`. Repeat run: `1 failed audit`, not skipped, with skip_check `previous audit status was error`, and it re-parsed from the identity-matched cache ("Reusing raw Docling JSON with matching identity") without reconverting. That proves the failed-audit rule and D4 on real data (folder e2e_marine_bio_error). The next-smallest, BS-Social-Work-for-student-new-version.pdf, also audits `error` (e2e_social_work_error).
- Passing PDF used for steps 2-5: BSE-Franchising-and-Trading-for-student-new-version.pdf (93,101 B; 1 of 6 non-error audits among the 44), folder e2e.
  - Run A: `[*] Batch: 1 extracted, 0 failed audit, 0 skipped, 0 errored.` 9 files: target_docling.json, target_docling.meta.json, target_essentials.json, target_prospectus.json/.md/.pl, target_publish.json, target_rag.jsonl, target_review.csv.
  - Run B (unchanged): `0 extracted, 0 failed audit, 1 skipped, 0 errored.` skip_check `identical run identity`. SHA-256 of all 9 files: no differences.
  - Run C (PDF replaced by `%PDF-1.4 not really a pdf`): `0 extracted, 0 failed audit, 0 skipped, 1 errored.` exit 1; skip_check `input, settings, parser or schema changed`. All 9 earlier files: no differences. No `.target.staging-*` left. `failed\target\failure.json` has error_type `ConversionError` ("docling-parse could not load document ...") and a traceback. Nothing else was staged, because conversion failed before writing.
  - Run D (original PDF restored): `0 extracted, 0 failed audit, 1 skipped, 0 errored.` No differences. `failed\target\` is still present: diagnostics are cleared by the next successful processing, not by a skip (for the Task 10 decision record).

### Codex recovery checkpoint 2026-10-06T20:57:53+08:00
- Task: Phase D resume; step: preflight complete; starting snapshot/hash task; owner: Codex controller.
- HEAD: 641523d212839084da03d966ffbfca66c7e83e42; state: clean.
- Evidence: Prior planning baseline:630 passed,13 subtests; HEAD641523d unchanged; GUI13 focused passed.
- Next: Dispatch Phase D F3/F6 immutable input identity implementer; preserve GUI untracked work.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Phase D F3/F6 immutable input identity (2026-10-06)
- Base: 641523d. One frozen InputSnapshot(path) captures immutable PDF/JSON bytes and a shared bytes_sha256 digest; path linkage checked. Source verification, run identity, skip check and loader reuse the capture. Batch retains one item at a time; loader initializes its shared converter after cache miss.
- Docling conversion receives DocumentStream(BytesIO(captured bytes)) with the original filename; backend fallback gets a fresh stream. Current original bytes are compared before pipeline publication and standalone cache writes; same-size/restored-mtime changes refuse publication and retain earlier files. No schema bump or CLI-declared input digest.
- Internal loader.load_document_result returns DocumentLoadResult(document, raw_json_path, cache_status, raw_json_bytes, raw_json_sha256, meta_bytes, meta_sha256). Reused cache bytes are the exact verified/parsed reads; converted bytes are the exact staging serialization. F1 should bind these digests without reopening cache paths. Public load_document and load_reusable_cache retain tuple contracts.
- Red evidence:8 failing snapshot tests; standalone cache race1failed/1passed; lost skip-check-error fallback1failed then restored to preserve existing processing behavior. Final focused335 passed; fallback follow-up26 passed. Final main full suite641 passed +13 subtests/3 upstream warnings; GUI-venv comprehensive647 passed +13 subtests/5 upstream warnings; shim80/80. Full suites repeated only after the additional fallback fix. No venv sync.
- Evidence: dump/scratch/codex_resume_2026-10-06/task-d-identity-report.md and task-d-identity-{red,standalone-red,green,skip-error-red,skip-error-green,final-fullsuite,final-comprehensive,selftest}.log. Independent reviews and remaining D/corpus gates not run by this implementer; next: controller independent F3/F6 review then F1 publication/cache binding.

### Codex recovery checkpoint 2026-10-06T21:10:39+08:00
- Task: D F3/F6; step: final verified: baseline641 comprehensive647 subtests13 shim80/80; ready to commit; owner: d_identity implementer.
- HEAD: 641523d212839084da03d966ffbfca66c7e83e42; state: M backend/bintanong_tools/prospectus.py
 M backend/bintanong_tools/prospectus_extractor/batch.py
 M backend/bintanong_tools/prospectus_extractor/identity.py
 M backend/bintanong_tools/prospectus_extractor/loader.py
 M backend/bintanong_tools/prospectus_extractor/pipeline.py
 M plans/plan_current_progress/extractor_split_progress.md
 M tests/conftest.py
 M tests/test_prospectus_authority.py
 M tests/test_prospectus_batch_skip.py
 M tests/test_prospectus_markup.py
?? tests/test_prospectus_input_snapshot.py.
- Evidence: task-d-identity-report.md; task-d-identity-final-fullsuite.log; task-d-identity-final-comprehensive.log; task-d-identity-selftest.log.
- Next: Stage only explicit F3/F6 implementation tests and progress files; commit with required final coauthor trailer.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Phase D F1 publication consistency (2026-10-06)
- Baseline53e3c00; publish-v2 now binds main_file, separate output/cache digests and the exact loader snapshot pair inside payload/manifest run_identity. Converted and reused pairs are staged; reused still records cache=reused.
- Approved order deviation: companions -> main JSON -> raw cache JSON/meta -> manifest. File-by-file publication remains non-atomic; mixed generations fail verification, while unchanged early replacements may leave the prior coherent set valid. Stale cleanup uses only known companion names.
- Original focused RED214failed/72passed; focused GREEN310passed; supplementary baseline reconstruction38failed/5passed explicitly labelled reconstruction. Two obsolete doubles fixed after initial broad2failures: authority missing snapshot fields; OCR settings changed only at loader boundary. Corrected focused557passed; validation64passed.
- Final MAIN baseline suite910passed/13subtests/3warnings; GUI comprehensive916passed/13subtests/5warnings; selftest80/80. External evidence/report task-d-publish-report.md in approved scratch root. Public six publish arguments retained with keyword-only cache_hashes; payload remainsv3.2. Default paths and staging/temp names unchanged for S1.
- Independent spec/quality review and remaining D queue/phase gates remain controller-owned; no maincheckout edits, sync, push, merge or worktree removal.

### Codex recovery checkpoint 2026-10-06T21:36:13+08:00
- Task: Phase D F1 publication; step: all gates GREEN; report written; before explicit commit; owner: d_publish.
- HEAD: 53e3c000958eae9cf4e12e197a6e54b7cc7b2e84; state: M backend/bintanong_tools/prospectus_extractor/pipeline.py
 M backend/bintanong_tools/prospectus_extractor/publish.py
 M plans/plan_current_progress/extractor_split_progress.md
 M tests/test_prospectus_authority.py
 M tests/test_prospectus_batch_skip.py
 M tests/test_prospectus_cache.py
 M tests/test_prospectus_publication.py
 M tests/test_prospectus_publish.py.
- Evidence: task-d-publish-report.md; task-d-publish-final-fullsuite.log; task-d-publish-final-comprehensive.log; task-d-publish-selftest.log.
- Next: Explicitly stage two production files, five test files and progress; commit with required trailer; parent independently reviews baseline53e3c00..tip..
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T21:37:12+08:00
- Task: D F1 publication; step: Committed597e8c0 clean; independent specification review active; owner: /root/d_publish_spec.
- HEAD: 597e8c0289b8c090edf494248a9bd3fedad6aeb4; state: clean.
- Evidence: task-d-publish-report.md main910 comprehensive916 +13subtests selftest80/80; task-d-publish-review-package.md.
- Next: Read spec review, reproduce any findings through original implementer; then independent quality review of53e3c00..597e8c0.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T21:40:55+08:00
- Task: D F1 publication; step: 597e8c0 SPEC APPROVED/NONE; separate quality review active; owner: /root/d_publish_quality.
- HEAD: 597e8c0289b8c090edf494248a9bd3fedad6aeb4; state: M plans/plan_current_progress/extractor_split_progress.md.
- Evidence: task-d-publish-spec-review.md APPROVED/NONE; task-d-publish-report.md main910 comprehensive916 +13 selftest80/80.
- Next: Read quality review; resolve confirmed findings through original implementer, or dispatch remainingF2/F4/F5/S1/S2/S4 brief on597e8c0.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T21:48:07+08:00
- Task: D F2 discovery; step: RED observed: 11 failed, 8 passed, 19 deselected; production unchanged; owner: /root/d_discovery.
- HEAD: 597e8c0289b8c090edf494248a9bd3fedad6aeb4; state: M plans/plan_current_progress/extractor_split_progress.md
 M tests/test_prospectus_batch_skip.py.
- Evidence: task-d-discovery-brief.md; task-d-discovery-red.log.
- Next: Implement minimal scan_inputs root-relative directory and marker filter, then run focused scan/batch/TUI relevant tests..
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T21:48:55+08:00
- Task: D F2 discovery; step: Focused GREEN 48 passed; no warnings; preparing main full-suite gate; owner: /root/d_discovery.
- HEAD: 597e8c0289b8c090edf494248a9bd3fedad6aeb4; state: M backend/bintanong_tools/prospectus_extractor/batch.py
 M plans/plan_current_progress/extractor_split_progress.md
 M tests/test_prospectus_batch_skip.py.
- Evidence: task-d-discovery-red.log; task-d-discovery-green.log.
- Next: Run main full suite with two approved ignores and external basetemp; inspect results before report/commit..
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T21:51:47+08:00
- Task: D F2 discovery; step: Main full GREEN928passed/13subtests/3warnings; TUI smokePASS; report ready, before commit; owner: /root/d_discovery.
- HEAD: 597e8c0289b8c090edf494248a9bd3fedad6aeb4; state: M backend/bintanong_tools/prospectus_extractor/batch.py
 M plans/plan_current_progress/extractor_split_progress.md
 M tests/test_prospectus_batch_skip.py.
- Evidence: task-d-discovery-report.md; task-d-discovery-red.log; task-d-discovery-green.log; task-d-discovery-tui.log; task-d-discovery-full.log.
- Next: Explicitly stage batch.py, test_prospectus_batch_skip.py and preserved progress; commit F2 with required trailer, then update report/checkpoint and parent review..
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Phase D F2 discovery (2026-10-06)
- Base597e8c0; shared scan_inputs now checks standard ignored names only in root-relative directory components, retaining legitimate failed/FAILED inputs and requested filenames/JSON. scan_pdfs alias and batch/TUI/isolated callers use the shared fix.
- Ruling: failure.json within candidate parent directories through selected root marks the diagnostic subtree, including direct selection of failed/run; markers above root ignored. A user folder carrying that marker is intentionally diagnostic until removed. No payload parsing, new dependency, configuration or filesystem abstraction.
- RED11failed/8passed/19deselected; focused GREEN48passed/no warnings; real TUI scan smokePASS; main full928passed/13subtests/3upstream warnings. External task-d-discovery-report.md and red/green/TUI/full logs in approved scratch. Existing controller F1 review checkpoints preserved.
- Complete GUI-review suite and standalone final-gate selftest NOT RUN for this task, deferred to Phase D final gates; no prior count reused as current evidence. F2 independent spec/quality review pending. F4/F5/S1/S2/S4 and final Phase D gates/Task10 remain; no Phase D completion claim.

### Codex recovery checkpoint 2026-10-06T21:52:12+08:00
- Task: D F2 discovery; step: Committeddf5eec4; red/green/main full/TUI verified; separate parent reviews pending; owner: /root/d_discovery.
- HEAD: df5eec4bdf0d3b9f46addfce7911b00a705ec126; state: clean.
- Evidence: task-d-discovery-report.md; task-d-discovery-red.log; task-d-discovery-green.log; task-d-discovery-tui.log; task-d-discovery-full.log.
- Next: Parent review committed597e8c0289b8c090edf494248a9bd3fedad6aeb4..df5eec4; preserve new sole dirty progress checkpoint for next focused commit..
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T21:53:04+08:00
- Task: D F2 discovery; step: Committeddf5eec4; red11failed focused48passed full928+13; spec review active; owner: /root/d_discovery_spec.
- HEAD: df5eec4bdf0d3b9f46addfce7911b00a705ec126; state: M plans/plan_current_progress/extractor_split_progress.md.
- Evidence: task-d-discovery-report.md; task-d-discovery-review-package.md; task-d-discovery-full.log928passed/3warnings/+13.
- Next: Read F2 spec verdict then independent quality review; next F4 LF task, followed S1 S2 S4 F5 and finalDgates.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T21:55:50+08:00
- Task: D F2 discovery review repair; step: SPEC found pattern traversal root escape atdf5eec4; final CHANGES_REQUIRED report being written; owner: /root/d_discovery_spec.
- HEAD: df5eec4bdf0d3b9f46addfce7911b00a705ec126; state: M plans/plan_current_progress/extractor_split_progress.md.
- Evidence: Pending task-d-discovery-spec-review.md; external tiny traversal probe discovered ../*.pdf reads above-root failure.json.
- Next: Read concrete spec finding/probe; original d_discovery reproduces failing regression and fixes shared scan_inputs boundary; re-review before quality.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T21:59:03+08:00
- Task: D F2 discovery repair1; step: Reproduced traversal probe; RED18failed/6passed/38deselected; production unchanged; owner: /root/d_discovery.
- HEAD: df5eec4bdf0d3b9f46addfce7911b00a705ec126; state: M plans/plan_current_progress/extractor_split_progress.md
 M tests/test_prospectus_batch_skip.py.
- Evidence: task-d-discovery-spec-review.md; task-d-discovery-repair-reproduction.log; task-d-discovery-repair-red.log.
- Next: Add minimal pathlib pattern rejection, focused green plus repaired targeted probe, then main full baseline..
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T21:59:56+08:00
- Task: D F2 discovery repair1; step: Focused GREEN72passed/no warnings; traversal repair probePASS; before main full gate; owner: /root/d_discovery.
- HEAD: df5eec4bdf0d3b9f46addfce7911b00a705ec126; state: M backend/bintanong_tools/prospectus_extractor/batch.py
 M plans/plan_current_progress/extractor_split_progress.md
 M tests/test_prospectus_batch_skip.py.
- Evidence: task-d-discovery-repair-red.log; task-d-discovery-repair-green.log; task-d-discovery-repair-probe.log.
- Next: Run main full suite with two approved ignores/external basetemp; inspect result before repair report/commit..
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T22:02:01+08:00
- Task: D F2 discovery repair1; step: Full GREEN952passed/13subtests/3warnings; focused72passed/probePASS; before explicit repair commit; owner: /root/d_discovery.
- HEAD: df5eec4bdf0d3b9f46addfce7911b00a705ec126; state: M backend/bintanong_tools/prospectus_extractor/batch.py
 M plans/plan_current_progress/extractor_split_progress.md
 M tests/test_prospectus_batch_skip.py.
- Evidence: task-d-discovery-report.md; task-d-discovery-repair-reproduction.log; task-d-discovery-repair-red.log; task-d-discovery-repair-green.log; task-d-discovery-repair-probe.log; task-d-discovery-repair-full.log.
- Next: Append result/progress; stage only batch.py, test_prospectus_batch_skip.py and preserved progress; commit with required trailer; postcommit checkpoint/report exact tip..
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Phase D F2 specification repair round1 (2026-10-06)
- Reproduced Important review finding: configured ../*.pdf yielded root/../course.pdf and above-root failure.json changed discovery. Original reviewer probe preserved; reproduction logged externally.
- Ruling: root-relative glob patterns cannot have any parent component or anchor. A single PureWindowsPath lexical guard recognizes slash/backslash parent, rooted, drive-relative/absolute and UNC patterns and raises explicit ValueError before glob; valid descendant globs preserved, no symlink resolution/policy change or filesystem abstraction.
- Repair RED18failed/6passed/38deselected; focused GREEN72passed/no warnings; repaired recursive/nonrecursive probePASS with/without above-root marker; main full952passed/13subtests/3upstream warnings. Exact commands/evidence appended task-d-discovery-report.md; repair reproduction/red/green/probe/full logs external.
- Existing controller/implementer progress checkpoints preserved. Complete GUI-review suite and standalone final selftest NOT RUN for scanner repair, final Phase D gates remain. Parent same-seat specification re-review before separate quality review; F4/F5/S1/S2/S4/Task10 remain, no Phase D completion claim.

### Codex recovery checkpoint 2026-10-06T22:02:21+08:00
- Task: D F2 discovery repair1; step: Committed4a0cdb7; repair RED/GREEN/probe/main full verified; specification re-review pending; owner: /root/d_discovery.
- HEAD: 4a0cdb794a337b9cc91846d16585478c3bb5fde0; state: clean.
- Evidence: task-d-discovery-report.md; task-d-discovery-repair-red.log; task-d-discovery-repair-green.log; task-d-discovery-repair-probe.log; task-d-discovery-repair-full.log.
- Next: Parent specification re-review immutable baseline597e8c0..4a0cdb7 with repair delta df5eec4..4a0cdb7; preserve sole dirty postcommit progress checkpoint..
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T22:03:12+08:00
- Task: D F2 repaired discovery; step: Committed4a0cdb7; repairred18failed focused72passed full952+13; spec re-review active; owner: /root/d_discovery_spec.
- HEAD: 4a0cdb794a337b9cc91846d16585478c3bb5fde0; state: M plans/plan_current_progress/extractor_split_progress.md.
- Evidence: task-d-discovery-report.md repairsection; task-d-discovery-final-review-package.md; task-d-discovery-repair-full.log952+13/3warnings.
- Next: Read spec re-review verdict, then separate quality review597e8c0..4a0cdb7; next F4 LF task.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T22:05:10+08:00
- Task: D F2 repaired discovery; step: 4a0cdb7 SPEC APPROVED; independent quality review active; owner: /root/d_discovery_quality.
- HEAD: 4a0cdb794a337b9cc91846d16585478c3bb5fde0; state: M plans/plan_current_progress/extractor_split_progress.md.
- Evidence: task-d-discovery-spec-rereview.md APPROVED, independent4-caseprobe passed; report/full952+13.
- Next: Resolve quality findings or dispatch F4 LF task on4a0cdb7; remainingS1/S2/S4/F5 and finalDgates.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T22:12:13+08:00
- Task: D F4 LF artifacts; step: RED verified3failed/126deselected; production unchanged; owner: /root/d_lf.
- HEAD: 4a0cdb794a337b9cc91846d16585478c3bb5fde0; state: M plans/plan_current_progress/extractor_split_progress.md
 M tests/test_prospectus_batch_skip.py
 M tests/test_prospectus_publish.py.
- Evidence: task-d-lf-brief.md; task-d-lf-red.log.
- Next: Reuse existing publish.write_text_lf for batch JSON and set DictWriter lineterminator LF; run exact regressions GREEN then focused suites..
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T22:12:44+08:00
- Task: D F4 LF artifacts; step: GREEN3passed/126deselected/no warnings; before focused suites; owner: /root/d_lf.
- HEAD: 4a0cdb794a337b9cc91846d16585478c3bb5fde0; state: M backend/bintanong_tools/prospectus_extractor/batch.py
 M backend/bintanong_tools/prospectus_extractor/views.py
 M plans/plan_current_progress/extractor_split_progress.md
 M tests/test_prospectus_batch_skip.py
 M tests/test_prospectus_publish.py.
- Evidence: task-d-lf-red.log; task-d-lf-green.log.
- Next: Run focused batch/publish/publication writer suites, inspect results, then main full excluded baseline..
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T22:35:39+08:00
- Task: D F4 LF artifacts resumed; step: Initial LF RED3 verified from prior logs; new bare-CR regression GREEN3 on main Python3.13.5; QUOTE_ALL hypothesis disproved; owner: /root/d_lf_resume.
- HEAD: 4a0cdb794a337b9cc91846d16585478c3bb5fde0; state: M backend/bintanong_tools/prospectus_extractor/batch.py
 M backend/bintanong_tools/prospectus_extractor/views.py
 M plans/plan_current_progress/extractor_split_progress.md
 M tests/test_prospectus_batch_skip.py
 M tests/test_prospectus_publish.py.
- Evidence: task-d-lf-red.log; task-d-lf-cr-red.log.
- Next: Verify current GUI-review stdlib quoting; retain minimal quoting if safe; focused and main full suite.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T22:37:23+08:00
- Task: D F4 LF artifacts resumed; step: Focused GREEN361 passed, no warnings; minimal quoting safe on both current Python3.13.5 runtimes; owner: /root/d_lf_resume.
- HEAD: 4a0cdb794a337b9cc91846d16585478c3bb5fde0; state: M backend/bintanong_tools/prospectus_extractor/batch.py
 M backend/bintanong_tools/prospectus_extractor/views.py
 M plans/plan_current_progress/extractor_split_progress.md
 M tests/test_prospectus_batch_skip.py
 M tests/test_prospectus_publish.py.
- Evidence: task-d-lf-red.log; task-d-lf-cr-red.log; task-d-lf-runtime-probe.log; task-d-lf-resumed-focused.log.
- Next: Run main full suite with two approved ignores; inspect results, report and explicit commit.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T22:37:49+08:00
- Task: D F4 LF artifacts resumed; step: Focused GREEN361 passed; main full currently running; QUOTE_ALL hypothesis superseded; owner: /root/d_lf_resume.
- HEAD: 4a0cdb794a337b9cc91846d16585478c3bb5fde0; state: M backend/bintanong_tools/prospectus_extractor/batch.py
 M backend/bintanong_tools/prospectus_extractor/views.py
 M plans/plan_current_progress/extractor_split_progress.md
 M tests/test_prospectus_batch_skip.py
 M tests/test_prospectus_publish.py.
- Evidence: task-d-lf-resumed-focused.log; task-d-lf-runtime-probe.log.
- Next: Poll exec session95634; read task-d-lf-resumed-full.log then report/commit if green.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T22:42:19+08:00
- Task: D F4 LF artifacts resumed; step: Fresh focused361 passed and full956 passed/13 subtests/3 upstream warnings; verified before explicit commit; owner: /root/d_lf_resume.
- HEAD: 4a0cdb794a337b9cc91846d16585478c3bb5fde0; state: M backend/bintanong_tools/prospectus_extractor/batch.py
 M backend/bintanong_tools/prospectus_extractor/views.py
 M plans/plan_current_progress/extractor_split_progress.md
 M tests/test_prospectus_batch_skip.py
 M tests/test_prospectus_publish.py.
- Evidence: task-d-lf-red.log; task-d-lf-green.log; task-d-lf-cr-red.log; task-d-lf-runtime-probe.log; task-d-lf-resumed-focused.log; task-d-lf-resumed-full.log.
- Next: Save concise report and F4 progress; explicitly stage five authorized paths; commit with required Claude trailer.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Phase D F4 LF artifacts (2026-10-06)
- Batch manifest reuses publish.write_text_lf; review CSV uses stdlib LF record separators with existing UTF8-sig BOM, native minimal quoting, all23 columns and exact values. No output/schema/name changes.
- Preserved interrupted worker authentic LF RED3failed/126deselected and GREEN3passed/126deselected. Added bare-CR round-trip parameter without comma; its attempted RED actually passed3cases, explicitly characterization rather than failing evidence.
- Root superseded QUOTE_ALL hypothesis: main and GUI-review Python3.13.5 both already quote bareCR under LF/QUOTE_MINIMAL; backend requires ==3.13.*. Native quoting retained; runtime probe/log external, no unsupported-runtime workaround or new dependency.
- Fresh focused GREEN361passed/no warnings; main full956passed/13subtests/3upstream warnings with two approved API/embedding excludes. task-d-lf-report.md and exact original/resume logs outside Git in approved scratch; previous progress checkpoints preserved.
- GUI-review comprehensive suite and standalone final D selftest NOT RUN for F4, deferred final gates. Parent independent specification then quality review pending; S1/S2/S4/F5/final D gates/Task10 and downstream queue remain. Phase D not complete.

### Codex recovery checkpoint 2026-10-06T22:42:47+08:00
- Task: D F4 LF artifacts; step: Committed 52da4aaca7d734e83054b1ecd39221ac09302a3b; focused361/full956+13 verified; parent specification then quality review pending; owner: /root/d_lf_resume.
- HEAD: 52da4aaca7d734e83054b1ecd39221ac09302a3b; state: clean.
- Evidence: task-d-lf-report.md; task-d-lf-red.log; task-d-lf-green.log; task-d-lf-cr-red.log; task-d-lf-runtime-probe.log; task-d-lf-resumed-focused.log; task-d-lf-resumed-full.log.
- Next: Parent review 4a0cdb794a337b9cc91846d16585478c3bb5fde0..52da4aaca7d734e83054b1ecd39221ac09302a3b; preserve sole dirty postcommit progress checkpoint.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T22:45:53+08:00
- Task: D F4 LF artifacts review; step: 52da4aa SPEC APPROVED/NONE; separate qualityseat active; owner: /root/d_lf_quality.
- HEAD: 52da4aaca7d734e83054b1ecd39221ac09302a3b; state: M plans/plan_current_progress/extractor_split_progress.md.
- Evidence: task-d-lf-spec-review.md APPROVED/NONE; focused361 full956+13; task-d-paths-brief.md ready.
- Next: Qualityverdict then S1 compactpaths task on52da4aa; use latest32digitstemkey/defaultroot ruling.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T22:51:46+08:00
- Task: D S1 compact Windows paths; step: Tests written; production unchanged; ready RED; owner: /root/d_paths.
- HEAD: 52da4aaca7d734e83054b1ecd39221ac09302a3b; state: M plans/plan_current_progress/extractor_split_progress.md
 M tests/test_prospectus_cache.py
 M tests/test_prospectus_publish.py.
- Evidence: task-d-paths-brief.md; latest final32digest ruling; s1-path-projection.json.
- Next: Run S1 RED selectors in publish/cache tests with external basetemp; inspect expected failures before production edits.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T22:52:51+08:00
- Task: D S1 compact Windows paths; step: Authentic RED8failed1passed88deselected; production unchanged; owner: /root/d_paths.
- HEAD: 52da4aaca7d734e83054b1ecd39221ac09302a3b; state: M plans/plan_current_progress/extractor_split_progress.md
 M tests/test_prospectus_cache.py
 M tests/test_prospectus_publish.py.
- Evidence: task-d-paths-red-final.log; task-d-paths-red.log.
- Next: Implement home/Bintanong/output, shared32digest stage prefix and mkstemp .t-; rerun exact RED selector GREEN.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T22:53:22+08:00
- Task: D S1 compact Windows paths; step: GREEN9passed88deselected; minimal3productionfiles changed; owner: /root/d_paths.
- HEAD: 52da4aaca7d734e83054b1ecd39221ac09302a3b; state: M backend/bintanong_tools/prospectus_extractor/loader.py
 M backend/bintanong_tools/prospectus_extractor/paths.py
 M backend/bintanong_tools/prospectus_extractor/publish.py
 M plans/plan_current_progress/extractor_split_progress.md
 M tests/test_prospectus_cache.py
 M tests/test_prospectus_publish.py.
- Evidence: task-d-paths-red-final.log; task-d-paths-green.log.
- Next: Run focused path/cache/publication/batch suites; actual generated-name all44 corpus path projection; then main full excluded baseline.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T22:55:00+08:00
- Task: D S1 compact Windows paths; step: Focused386passed/no warnings; before main full approved excludes; owner: /root/d_paths.
- HEAD: 52da4aaca7d734e83054b1ecd39221ac09302a3b; state: M backend/bintanong_tools/prospectus_extractor/loader.py
 M backend/bintanong_tools/prospectus_extractor/paths.py
 M backend/bintanong_tools/prospectus_extractor/publish.py
 M plans/plan_current_progress/extractor_split_progress.md
 M tests/test_prospectus_cache.py
 M tests/test_prospectus_publish.py.
- Evidence: task-d-paths-focused.log386passed; task-d-paths-red-final.log; task-d-paths-green.log; task-d-paths-actual-projection.json.
- Next: Run main Python -m pytest -q tests --ignore=tests/test_api_probes.py --ignore=tests/test_embedding_service.py -p no:cacheprovider --basetemp external/s1-full-temp, log task-d-paths-full.log; inspect exit/counts before commit.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T22:56:47+08:00
- Task: D S1 compact Windows paths; step: Fresh full961passed13subtests3upstreamwarnings; all44projection251max; precommit; owner: /root/d_paths.
- HEAD: 52da4aaca7d734e83054b1ecd39221ac09302a3b; state: M backend/bintanong_tools/prospectus_extractor/loader.py
 M backend/bintanong_tools/prospectus_extractor/paths.py
 M backend/bintanong_tools/prospectus_extractor/publish.py
 M plans/plan_current_progress/extractor_split_progress.md
 M tests/test_prospectus_cache.py
 M tests/test_prospectus_publish.py.
- Evidence: task-d-paths-red-final.log8failed1passed; task-d-paths-green.log9passed; task-d-paths-focused.log386passed; task-d-paths-full.log961passed13subtests3warnings; task-d-paths-actual-projection.json.
- Next: Finish S1 report/progress and normalize edited text LF; stage exact paths.py publish.py loader.py test_prospectus_publish.py test_prospectus_cache.py extractor_split_progress.md; commit with required Claude trailer.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Phase D S1 compact Windows paths (2026-10-06)
- Portable default is Path.home() / 'Bintanong' / 'output', replacing the package-local docling_jsonified_output default. Existing artifacts stay in their old location; old consumers must pass explicit --output (JSON path for one file, root for batch). No previous outputs moved/deleted and no home artifacts generated during verification. Existing final/cache filenames, batch sanitization, explicit overrides and failed/<base>/ layout remain unchanged.
- Stage .s-<32hex UTF8 stem SHA256 prefix>-<8 UUID hex> reuses shared identity.bytes_sha256 through one private prefix helper for generation/cleanup. Cleanup targets the full128bit stem prefix, preserving other stems, unrelated folders and matching regular files. Earlier8digit proposal superseded: cost24 extra path characters, actual stage name44. One writer per output stem retained; no arbitrary-neighbor cleanup or new framework.
- Atomic cache writer keeps unique tempfile.mkstemp and replacement/failure semantics, shortening only prefix to .t- with .tmp suffix (actual name15). Regression checks cover interleaved writes, locked replacement retry/cleanup and interrupted write cleanup while preserving old bytes.
- Authentic TDD RED8failed1passed88deselected before production; GREEN9passed88deselected. Fresh focused386passed/no warnings; main full961passed/13subtests/3 existing upstream warnings, with approved API/embedding exclusions. Exact commands/logs in external task-d-paths-report.md and task-d-paths-{red-final,green,focused,full}.log.
- Read-only original44 corpus projection used actual output directories and generated stage/temp names: root35, final181/stage226/temp161/failed251 versus old final/cache268. Exact maxima paths in external task-d-paths-actual-projection.json. Longest real Tiniguiban CS relative input and separate Citizens Charter BOR proposal (2) boundary covered; no proposal opened/converted. Current corpus fits at most8 extra root characters below260; arbitrary longer home/explicit roots require caller-selected shorter --output, never silent artifact renaming.
- GUI comprehensive suite, standalone selftest80, semantic44 comparer and trials NOT RUN for S1, deferred parent final D gates. Independent specification then quality reviews pending. S2/S4/F5/final D gates/Task10 and downstream queue remain; Phase D not complete. Existing F4 postcommit/review progress preserved.

### Codex recovery checkpoint 2026-10-06T22:57:41+08:00
- Task: D S1 compact Windows paths; step: Committed4320327; targeted9 focused386 full961+13 verified; parent reviews pending; owner: /root/d_paths.
- HEAD: 4320327bb68ec0973dd79ee7716ab5d893fe00a8; state: clean.
- Evidence: task-d-paths-report.md; task-d-paths-red-final.log; task-d-paths-green.log; task-d-paths-focused.log; task-d-paths-full.log; task-d-paths-projection.log; task-d-paths-actual-projection.json.
- Next: Parent fresh specification review 52da4aaca7d734e83054b1ecd39221ac09302a3b..4320327, then independent quality review; preserve sole dirty postcommit progress checkpoint.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T22:58:38+08:00
- Task: D S1 Windows paths review; step: Committed 4320327; red 8 failures, focused 386 and full 961 +13 passed; specification review active; owner: /root/d_paths_spec.
- HEAD: 4320327bb68ec0973dd79ee7716ab5d893fe00a8; state: M plans/plan_current_progress/extractor_split_progress.md.
- Evidence: task-d-paths-report.md; task-d-paths-review-package.md; task-d-paths-actual-projection.json; main full 961 +13 subtests/3 warnings.
- Next: Read S1 specification verdict, then independent quality review; dispatch S2/S4 task after approval.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T23:01:13+08:00
- Task: D S1 Windows paths review; step: 4320327 specification APPROVED/NONE; separate quality review active; owner: /root/d_paths_quality.
- HEAD: 4320327bb68ec0973dd79ee7716ab5d893fe00a8; state: M plans/plan_current_progress/extractor_split_progress.md.
- Evidence: task-d-paths-spec-review.md APPROVED/NONE; report focused386/full961+13; task-d-paths-actual-projection.json.
- Next: Read quality verdict; after approval dispatch task-d-skip-tui-brief.md on 4320327, then F5/final D gates.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T23:08:08+08:00
- Task: D S2 context skip; step: Authentic RED18failed62deselected; eligible flag absent and context/malformed runs incorrectly skipped; owner: /root/d_skip_tui.
- HEAD: 4320327bb68ec0973dd79ee7716ab5d893fe00a8; state: M plans/plan_current_progress/extractor_split_progress.md
 M tests/test_prospectus_batch_skip.py.
- Evidence: task-d-s2-red.log.
- Next: Implement presence-only skip_reusable in pipeline and fail-closed skip_check; run identical focused green command.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T23:09:38+08:00
- Task: D S2 context skip; step: Corrected authentic RED18failed62deselected with successful real payload/publication before expected skip failures; owner: /root/d_skip_tui.
- HEAD: 4320327bb68ec0973dd79ee7716ab5d893fe00a8; state: M plans/plan_current_progress/extractor_split_progress.md
 M tests/test_prospectus_batch_skip.py.
- Evidence: task-d-s2-red-final.log.
- Next: Add minimal skip_reusable presence flag and exact-boolean skip guard; rerun focused green selector context_publication or skip_eligibility or repeat_run.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T23:10:53+08:00
- Task: D S2 context skip; step: Validated RED18failed62deselected; all9 context publications complete/nonerror, old skip returned True; owner: /root/d_skip_tui.
- HEAD: 4320327bb68ec0973dd79ee7716ab5d893fe00a8; state: M plans/plan_current_progress/extractor_split_progress.md
 M tests/test_prospectus_batch_skip.py.
- Evidence: task-d-s2-validated-red.log.
- Next: Reapply minimal flag/guard, run validated focused GREEN then batch/identity/publish/publication/cache/authority suites.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T23:12:32+08:00
- Task: D S2 context skip; step: Validated green18/focused636passed; before main full approved excludes; owner: /root/d_skip_tui.
- HEAD: 4320327bb68ec0973dd79ee7716ab5d893fe00a8; state: M backend/bintanong_tools/prospectus_extractor/batch.py
 M backend/bintanong_tools/prospectus_extractor/pipeline.py
 M plans/plan_current_progress/extractor_split_progress.md
 M tests/test_prospectus_batch_skip.py.
- Evidence: task-d-s2-validated-red.log; task-d-s2-validated-green.log; task-d-s2-focused.log.
- Next: Run main Python -m pytest -q tests --ignore=tests/test_api_probes.py --ignore=tests/test_embedding_service.py -p no:cacheprovider --basetemp external/s2-full-temp; inspect result and commit S2 only.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Phase D S2 context-sensitive skip (2026-10-06)
- Pipeline persists run_identity.skip_reusable=False for any supplied source/approved_scope/review_entries/repair_provider via is None presence checks, including empty mappings/lists/generators and falsey typed source/provider. Normal contextless runs persist True. Publisher retains identical bound main/manifest identity and captured PDF/cache hashes; run key and schema unchanged, no provider serialization or extra ledger consumption. Flag grants no source/review/eligibility authority.
- Batch requires literal True for skip; False reason previous run used supplied context, missing/nonboolean reason previous run skip eligibility is unknown. All existing audit/identity/v2 publication/cache/completeness checks remain. Exact unchanged and force skip reasons replace ineffective assertion. Old outputs without known eligibility are reparsed once rather than trusted.
- Validated RED18failed62deselected; GREEN18passed62deselected; focused636passed/no warnings; main full978passed13subtests3existing upstream warnings with only approved API/embedding ignores. Logs and exact commands in external task-d-skip-tui-report.md and task-d-s2-{validated-red,validated-green,focused,full}.log. Earlier fixture mistakes preserved in initial/intermediate logs and explicitly superseded: wrong evidence adapter caused audit error, then unmatched requested companions caused incomplete-output refusal. Validated red used complete nonerror published sets returning True under old skip.
- S2 self-review found no remaining production concern; independent specification then quality review pending. S4/F5/final D gates/Task10 remain. GUI comprehensive/selftest/original44 corpus/trials NOT RUN here; all downstream/human gates pending, Phase D incomplete. Existing S1 review and checkpoint progress preserved.

### Codex recovery checkpoint 2026-10-06T23:14:29+08:00
- Task: D S2 context skip; step: Fresh focused636/full978+13/3existingwarnings; S2 precommit; owner: /root/d_skip_tui.
- HEAD: 4320327bb68ec0973dd79ee7716ab5d893fe00a8; state: M backend/bintanong_tools/prospectus_extractor/batch.py
 M backend/bintanong_tools/prospectus_extractor/pipeline.py
 M plans/plan_current_progress/extractor_split_progress.md
 M tests/test_prospectus_batch_skip.py.
- Evidence: task-d-skip-tui-report.md; task-d-s2-validated-red.log; task-d-s2-validated-green.log; task-d-s2-focused.log; task-d-s2-full.log.
- Next: Stage exact batch.py pipeline.py test_prospectus_batch_skip.py extractor_split_progress.md; commit S2 with Claude trailer; then S4 red.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T23:15:19+08:00
- Task: D S4 TUI force; step: S2 committed10c2d8b green18/focused636/full978+13; S4 tests next; owner: /root/d_skip_tui.
- HEAD: 10c2d8b5ac30313c7d5c7d2831fb7c8670cd146a; state: clean.
- Evidence: task-d-skip-tui-report.md; task-d-s2-full.log.
- Next: Add behavioral TUI config/display, actual single process True/False, and real batch skip-force precedence tests; capture S4 RED before changing tui.py.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T23:15:58+08:00
- Task: D S4 TUI force; step: S2 implementation-only committed10c2d8b; S4 RED4failed2passed80deselected; owner: /root/d_skip_tui.
- HEAD: 10c2d8b5ac30313c7d5c7d2831fb7c8670cd146a; state: M plans/plan_current_progress/extractor_split_progress.md
 M tests/test_prospectus_batch_skip.py.
- Evidence: task-d-s4-red.log; task-d-skip-tui-report.md.
- Next: Modify tui.py only: display force, accurate identity/completeness nonerror skip prompt, configure existing force flag, pass actual single-file force kwarg; run S4 GREEN.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T23:16:30+08:00
- Task: D S4 TUI force; step: RED4failed2passed; GREEN6passed80deselected; before focused TUI and shared suite; owner: /root/d_skip_tui.
- HEAD: 10c2d8b5ac30313c7d5c7d2831fb7c8670cd146a; state: M backend/bintanong_tools/prospectus_extractor/tui.py
 M plans/plan_current_progress/extractor_split_progress.md
 M tests/test_prospectus_batch_skip.py.
- Evidence: task-d-s4-red.log; task-d-s4-green.log; task-d-skip-tui-report.md.
- Next: Run batchskip/identity/publish/publication/cache/authority/markup focused suite; then approved main full before S4 commit.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T23:18:00+08:00
- Task: D S4 TUI force; step: Fresh focused680passed/no warnings; before main full; owner: /root/d_skip_tui.
- HEAD: 10c2d8b5ac30313c7d5c7d2831fb7c8670cd146a; state: M backend/bintanong_tools/prospectus_extractor/tui.py
 M plans/plan_current_progress/extractor_split_progress.md
 M tests/test_prospectus_batch_skip.py.
- Evidence: task-d-s4-red.log; task-d-s4-green.log; task-d-s4-focused.log.
- Next: Run main Python -m pytest -q tests --ignore=tests/test_api_probes.py --ignore=tests/test_embedding_service.py -p no:cacheprovider --basetemp external/s4-full-temp, log task-d-s4-full.log; inspect counts/warnings then commit S4.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Phase D S4 TUI skip wording and force configuration (2026-10-06)
- Existing BatchConfig.force_reconvert now shown and configured via ask_yes_no with current default. Prompt explains force overrides skip-existing and cached conversion; skip prompt restricts reuse to identity-verified complete outputs with a non-error audit. Single-file TUI now passes the actual force_reconvert kwarg; interactive batch already used the same config. No new conversion implementation or config owner.
- Authentic RED4failed2passed80deselected before production; GREEN6passed80deselected. Both True/False configuration transitions/display tested; actual single-file pipeline sees exact kwargs and converted/reused cache status, converter/build counts; actual interactive batch has force-over-skip precedence with exact reason. Focused680passed/no warnings; fresh main full984passed13subtests3existing upstream deprecations, only two approved API/embedding ignores. Exact commands/results in external task-d-skip-tui-report.md and task-d-s4-{red,green,focused,full}.log.
- S2 implementation-only commit10c2d8b precedes S4; parent separate specification then quality review pending. Self-review no unresolved implementation concerns. F5/final D gates/Task10 and all downstream/human gates pending. GUI comprehensive/selftest/original44 corpus/trials NOT RUN for this batch; Phase D incomplete.

### Codex recovery checkpoint 2026-10-06T23:20:17+08:00
- Task: D S4 TUI force; step: Fresh focused680/full984+13/3existingwarnings; S4 precommit; owner: /root/d_skip_tui.
- HEAD: 10c2d8b5ac30313c7d5c7d2831fb7c8670cd146a; state: M backend/bintanong_tools/prospectus_extractor/tui.py
 M plans/plan_current_progress/extractor_split_progress.md
 M tests/test_prospectus_batch_skip.py.
- Evidence: task-d-skip-tui-report.md; task-d-s4-red.log; task-d-s4-green.log; task-d-s4-focused.log; task-d-s4-full.log.
- Next: Stage exact tui.py test_prospectus_batch_skip.py progress; commit S4 with Claude trailer; record exact range/tips/Git state and return parent for spec then quality reviews.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T23:20:48+08:00
- Task: D S2/S4 implementation-only batch; step: Committed10c2d8b and c40a38c; S2 full978+13, S4 full984+13/3warnings; separate reviews next; owner: /root/d_skip_tui.
- HEAD: c40a38c9f633dd085766ca11f81f0dd3890810cc; state: clean.
- Evidence: task-d-skip-tui-report.md; task-d-s2-validated-red.log; task-d-s2-validated-green.log; task-d-s2-focused.log; task-d-s2-full.log; task-d-s4-red.log; task-d-s4-green.log; task-d-s4-focused.log; task-d-s4-full.log.
- Next: Parent fresh read-only specification review exact range4320327bb68ec0973dd79ee7716ab5d893fe00a8..c40a38c9f633dd085766ca11f81f0dd3890810cc then independent quality review; preserve sole dirty postcommit progress checkpoint.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T23:21:08+08:00
- Task: D S2/S4 independent review; step: Implementation c40a38c verified 680 focused and 984 main plus13subtests; specification review next; owner: /root.
- HEAD: c40a38c9f633dd085766ca11f81f0dd3890810cc; state: M plans/plan_current_progress/extractor_split_progress.md.
- Evidence: task-d-skip-tui-report.md; task-d-s4-full.log; task-d-skip-tui-review-package.md.
- Next: Specification review 4320327..c40a38c then separate quality review.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T23:25:13+08:00
- Task: D S2/S4 independent reviews; step: Specification APPROVED NONE; independent S2 18 and S4 6 plus prompt probe passed; owner: /root.
- HEAD: c40a38c9f633dd085766ca11f81f0dd3890810cc; state: M plans/plan_current_progress/extractor_split_progress.md.
- Evidence: task-d-skip-tui-spec-review.md; task-d-skip-tui-report.md.
- Next: Separate quality review of 4320327..c40a38c then final D gates.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T23:28:38+08:00
- Task: D final verification and F5/Task10 documentation; step: S2/S4 specification and quality APPROVED NONE at c40a38c; final gate writer next; owner: /root.
- HEAD: c40a38c9f633dd085766ca11f81f0dd3890810cc; state: M plans/plan_current_progress/extractor_split_progress.md.
- Evidence: task-d-skip-tui-spec-review.md; task-d-skip-tui-quality-review.md; task-d-final-gates-rulings.md.
- Next: Run final comprehensive/self-test/corpus/real-PDF gates, correct F5 and commit Task10 draft with whole-range reviews pending.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T23:30:51+08:00
- Task: Phase D F5 Tasks 8-10; step: preflight verified c40a38c; begin final gates; owner: /root/d_final_gates.
- HEAD: c40a38c9f633dd085766ca11f81f0dd3890810cc; state: M plans/plan_current_progress/extractor_split_progress.md.
- Evidence: task-d-final-gates-rulings.md; task-d-final-gates-brief.md; task-d-s4-full.log unchanged tip main 984 passed.
- Next: Resume final-gates agent; run fresh comprehensive GUI env, selftest and comparer against 641523d; see task-d-final-gates-rulings.md.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T23:36:31+08:00
- Task: Phase D F5 Tasks 8-10; step: comprehensive990+13, comparer44/44, focused394, real gates passed, originals101unchanged; owner: /root/d_final_gates.
- HEAD: c40a38c9f633dd085766ca11f81f0dd3890810cc; state: M plans/plan_current_progress/extractor_split_progress.md
?? docs/decisions/prospectus-cache-and-publication.md.
- Evidence: task-d-final-comprehensive.log; task-d-final-compare.log; task-d-final-focused.log; task-d-final-real.log; task-d-final-originals-after.json.
- Next: Run task-d-final-corpus-gates.py with MAINPY from phase-d root; no real/comparer relaunch; then finalize three docs and exact-path commit, parent whole-range reviews pending.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Phase D F5 and Tasks 8-10 final implementation/documentary gates (2026-10-06T23:37:16+08:00)
- Base `641523d212839084da03d966ffbfca66c7e83e42`; reviewed unchanged production tip `c40a38c9f633dd085766ca11f81f0dd3890810cc`; branch `feat/prospectus-phase-d-safe-cache`. S2/S4 independent spec/quality APPROVED NONE; whole-range `641523d..final-documentary-tip` specification and quality PENDING. Phase D not fully complete.
- Fresh GUI-review-venv comprehensive (includes API and embedding tests; the main backend venv count is 984): 990 passed, 13 subtests, 5 upstream warnings, exit 0; fresh focused: 394 passed, exit 0, includes 180 full before/after replacement interruptions; fresh MAINPY self-test: 80/80, exit 0. Reused unchanged-tip main gate `task-d-s4-full.log`: 984 passed, 13 subtests, 3 upstream warnings, with two approved API/embedding ignores; no gratuitous rerun, installs or main-venv synchronization.
- Existing comparer `--base-ref 641523d --jobs 6 --status-report` with original semantic map and explicit retained `Bintanong-wt/d-baseline-641523d`: 44/44 identical, exit 0. Direct C states 1005/689/253/59/20/3/2 in blank_unreviewed/resolved/unresolved_reference/standing_condition/unreadable/alternative_or_exception/stated_none order. Regression equivalence, not extraction accuracy. B2 health 21/3/19/1 mixed/warnings_only/broken/clean; title_from_pdf 67, strip_banner 0, unclaimed_code 316, banner_leak 3. Trial 01/16/33 `check_against`: 0 errors each; helpers imported through WT-root runpy context.
- Fresh real BSE-Franchising-and-Trading PDF copy `scratch/dg`: A: 1 extracted (WARN)/0 failed audit/0 skipped/0 errored, exit 0; B: 0/0/1/0, exit 0, identical run identity; C: 0/0/0/1, exit 1, ConversionError+traceback preserves 9 earlier outputs/cache files, no stage residue; D: 0/0/1/0, exit 0, retains diagnostics; E force: 1/0/0/0, exit 0, clears diagnostics. Real cached parse then equal-size/restored-mtime scratch mutation refused with `Input bytes changed since capture`, preserving prior set; restore+successful reused-cache publish clears diagnostics. Originals/cached inputs/map/trial files: 101 hashes unchanged around real and helper workflows; comparer began read-only before this snapshot, no before-comparer timing claim.
- Fresh path-only default-root actual stage/temp projection reproduced 44 paths/maxima final 181/stage 226/temp 161/failed 251 under 35-character `~/Bintanong/output`; no home writes, arbitrary explicit-root guarantee or longest-filename real conversion claim. Original historical error pilots preserved, not freshly rerun.
- F5 original Task 6 count corrected 15 to 14; authentic original red unavailable; reconstruction parent `29eb83200b593f24caa9179a28c0795c30621b5a` + `f802c764533bdf67267089bcc109416da5941ca9` tests/conftest observed 12 failed, 2 passed, explicitly not original chronology. Frozen test collection confirms 14; historical combined 61 retained without inferred correction. Evidence `reconstruct_task6.py`/`task6-red-reconstruction.log`.
- Decision docs/decisions/prospectus-cache-and-publication.md covers all approved deviations and actual gates; current_progress.md updated. Historical plans and existing review/checkpoint history preserved. Evidence task-d-final-gates-report.md and task-d-final-{comprehensive,compare,corpus,focused,selftest,real,path-projection} logs + .exit markers external codex_resume_2026-10-06. No production changes.
- Next: controller whole-range specification then independent quality review `641523d..documentary-tip`. GUI→E→F→OCR/formal/human gates pending, queue remains active; no push, dev merge, worktree removal or main dirty-file edit.

### Codex recovery checkpoint 2026-10-06T23:42:26+08:00
- Task: Phase D F5 Tasks 8-10; step: all fresh final runtime gates passed; three docpaths ready, whole-range reviews pending; owner: /root/d_final_gates.
- HEAD: c40a38c9f633dd085766ca11f81f0dd3890810cc; state: M plans/plan_current_progress/current_progress.md
 M plans/plan_current_progress/extractor_split_progress.md
?? docs/decisions/prospectus-cache-and-publication.md.
- Evidence: task-d-final-gates-report.md; task-d-final-comprehensive.log; task-d-final-selftest.log; task-d-final-focused.log; task-d-final-compare.log; task-d-final-corpus.log; task-d-final-real.log; task-d-final-path-projection.log.
- Next: git add docs/decisions/prospectus-cache-and-publication.md plans/plan_current_progress/extractor_split_progress.md plans/plan_current_progress/current_progress.md; verify cached paths; commit with Claude trailer; postcommit checkpoint then parent separate whole-range reviews641523d..tip.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T23:43:12+08:00
- Task: Phase D F5 Tasks 8-10 implementation-only complete; step: Committed08a8290 three docs only; final gates passed; whole-range spec/quality pending; owner: /root/d_final_gates.
- HEAD: 08a8290d7257485d695c4d2b05be5cf6db730d7b; state: clean.
- Evidence: task-d-final-gates-report.md; task-d-final-comprehensive.log; task-d-final-focused.log; task-d-final-selftest.log; task-d-final-compare.log; task-d-final-corpus.log; task-d-final-real.log; task-d-final-path-projection.log; task6-red-reconstruction.log.
- Next: Controller package review exact641523d212839084da03d966ffbfca66c7e83e42..08a8290d7257485d695c4d2b05be5cf6db730d7b; fresh read-only specification then separate quality seats using task-d-final-gates-report.md and rulings. Preserve sole postcommit progress dirty and all evidence/worktrees; continue approved GUI/E/F/OCR/formal queue..
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

### Codex recovery checkpoint 2026-10-06T23:43:53+08:00
- Task: D whole-range independent reviews; step: Runtime gates and F5/Task10 documentary commit verified at08a8290; whole-range specification next; owner: /root.
- HEAD: 08a8290d7257485d695c4d2b05be5cf6db730d7b; state: M plans/plan_current_progress/extractor_split_progress.md.
- Evidence: task-d-final-gates-report.md; task-d-whole-review-package.md; task-d-whole-review-brief.md.
- Next: Specification review641523d..08a8290 then separate quality review; record actual verdicts before D completion/GUI dispatch.
- Recovery: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\CLAUDE_TAKEOVER.md`.

## GUI Task 10: Phase C hooks (three states, prerequisite questions, `reviewed_empty`) - 2026-10-07

Branch `feat/prospectus-gui-task10` from `feat/prospectus-review-gui` tip 8818444. Dependency check: `prerequisite_state`, `EXECUTABLE_PREREQUISITE_STATES` and the comment reserving `reviewed_empty` for a human decision are in `prospectus_extractor/prerequisites.py` and `authority.py` (Phase C is merged); the extractor emitted nothing named `reviewed_empty` before this task and still does not.

Baseline before the work: main suite 1248 passed + 4 skipped, GUI (`-k review_gui`) 233 passed, self-test 80/80.

What changed
- `ledger.materialise`: after `finalize_courses` it re-runs `annotate_prerequisite_states` (with the audit's `structural_anomalies`, as the pipeline does), then stamps `reviewed_empty` on a course only when the latest applicable `prerequisites_raw` entry is `accepted`, the course is still blank, its re-classified state is `blank_unreviewed` and exactly one course carries the locator. Not for corrected, unresolved, stale, other-PDF or orphan entries, and not for an `unreadable` (ambiguous-cell) course. `content_review_state` is unchanged.
- `questions.py`: kind `prerequisite` (qid `<row id>:prereq`) for courses whose payload `prerequisite_state` is blank_unreviewed, unreadable, unresolved_reference or alternative_or_exception. A course question and a section Yes ignore `prerequisites_raw` decisions (`COURSE_QUESTION_FIELDS`), so a prerequisite answer never changes them.
- `answers.py`: Yes -> `accepted` (old == new), Other -> `corrected` (empty text allowed; a bare number refused, as an int and as digit-only text), No -> `unresolved`. Built with `make_entry` directly (the sheet writes no prerequisite entries, so there is no sheet path to be byte-identical with).
- `session.py` / `review.js` / `index.html`: `/api/state` gains `review_states` (extraction audit, content review, source verification, each with its own word and meaning), `approval_line` ("A reviewed prospectus is not an approved curriculum") and a `prerequisites` count. Content review is computed from the ledger, never from the payload's `content_review`; the payload file is not written. Source verification shows the payload's word (`pending` unless a person verified the source); the verifier's PDF-text health is a separate "PDF text check" badge so it cannot read as verification.

Decisions where the plan was silent (strict, simple option)
- Volume: prerequisite questions sit after every other question in both queue modes (attention and print; printed order in print mode, section-health order in attention mode), so the corpus's 1005 blank cells never push the three course-field questions down. `progress` still counts course-field questions only; `prerequisites` reports its own `decided`/`questions`.
- A candidate whose courses carry no `prerequisite_state` (made before Phase C, which includes the four trial candidates on disk) gets no prerequisite question; `/api/state.prerequisites.unclassified_courses` counts them and the page says so. Nothing is classified on the fly in the GUI.
- Yes needs no typed reason (default reason "accepted as extracted"); Other with text needs a reason; No needs a reason; Other with the same value as the printed one is refused ("answer Yes").
- Conflict found: an `unresolved` entry on `prerequisites_raw` keeps `content_review` at `partially_reviewed` (test `test_g5_an_unresolved_decision_on_any_correctable_field_keeps_the_state_partial` from B2, and the plan says `content_review_state` is unchanged). So accepted and corrected prerequisite answers never hold back `reviewed`, but a prerequisite No does, deliberately: an unresolved item is never hidden.

Evidence
- Red: `tests/test_prospectus_materialise.py` new tests: 3 failed, 11 passed before the `ledger.py` change (stamp missing, `reviewed_empty` writer missing, eligibility still blocked); the other 8 passed on purpose (non-stamping cases, determinism). `tests/test_review_gui_prerequisites.py`: collection error `cannot import name 'PREREQUISITE'` before the code. Green: 14 passed in the materialise file; 14 in the prerequisites file.
- Mutation checks in a scratch copy under `scratch/gui_t10_0710/mut_*` (worktree untouched): stamp without the `accepted` check -> 2 failed; without the blank/state check -> 2 failed; without the stale/other-PDF filter -> 1 failed; `resolved` added to the asked states -> 3 failed; prerequisite entries counted as a course decision -> 2 failed (the last was an early design; the final design leaves `content_review_state` as the plan says).
- Real data (read-only, in memory, originals untouched): the four trial candidates predate Phase C, so none has `prerequisite_state` and none gets a prerequisite question. Run through `materialise` with an empty ledger (which classifies exactly as the pipeline does) their states are blank_unreviewed 68, resolved 97, unresolved_reference 7, standing_condition 8, unreadable 3, i.e. 31 + 1 + 23 + 23 questions across BSA 77 courses, BSE-I&T 2, BSBA-HRM 49, BSCS 55, every one after the course-field questions; two materialise runs give identical bytes. No Phase C output of the 44-input corpus is on disk, so the 1005/689/253/59/20/3/2 counts were not re-measured; `prospectus_extractor` changed only in `ledger.py` (the pipeline, classifier and audit are untouched).
- Gates after the last code change: main suite 1256 passed + 5 skipped (the new GUI test file skips under the main venv, which has no FastAPI), GUI venv -k review_gui 247 passed, self-test 80/80. Linux and macOS were not run.
## GUI Task 11: end to end and the real-data gate - 2026-10-07

Done: plan Steps 1-5 and 8. NOT done: Step 6 (browser pass, PDF highlight by eye, console errors) and Step 7 (Lighthouse, keyboard-only walk). Those stay open for the owner or a session with a browser.

Files: `tests/test_review_gui_e2e.py` (5 tests), `scripts/prospectus_review_gui_smoke.py` (TestClient driver, fixed answer script, `--equivalence-dir`, `--all-unresolved`). Run with the GUI venv (FastAPI): `$env:TEMP\gui-review-venv\Scripts\python.exe scripts\prospectus_review_gui_smoke.py --candidate COPY.json --pdf COPY.pdf --review-dir SCRATCH\review\NAME`.

Tests: red was the smoke-script test (`FileNotFoundError: scripts/prospectus_review_gui_smoke.py`) and two assertion slips of mine in the full-session test (queue order, unclaimed count; fixed to match the app). The other three tests (restart, stale after a rerun, GUI-vs-sheet state) passed at once: they check behaviour built in Tasks 3 to 10, so there was no code to make green for them. The full session covers prerequisite questions: Yes on a blank, Other with text, No with a reason, then materialise: `reviewed_empty` only on the course accepted on a blank, the No course stays `blank_unreviewed`, the raw candidate hash unchanged.

Step 1 and 4: SHA-256 of all 17 files in the four trial folders (PDF, `_prospectus.json`, `.md`, the `review\` files) before and after: identical (`scratch\gui_e2e_0710\hashes_before.txt`, `hashes_after.txt`). The 8 PDF and JSON hashes equal the Task 1 table. Task 1 did not record the `.md` and `review\` hashes, so those are compared before-vs-after only. No file in the trial folders is newer than the run; the only new files are under `scratch\gui_e2e_0710\`.

Step 3, real numbers (copies, scripted answers; every reason says "scripted answer ... not a human review"):

| Prospectus | Sections (clean/review/broken) | Bulk questions | Questions (course/unclaimed/prereq) | First in queue | Answers (bulk, yes, other+proposal, no, unclaimed yes/no) | State after | Refusals |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 16_BSBA-HRM | 8 (7/1/0) | 7 (S1,S2,S3,S5,S6,S7,S8; none for S4) | 49/0/0 | S4-05 (review section) | 7, 4, 1, 2, 0/0 | partially_reviewed, 47/49 decided, 2 unresolved | 0 |
| 01_Architecture | 10 (1/8/1) | 1 (S9) | 77/0/0 | S4-01 (the broken section) | 1, 10, 3, 2, 0/0 | partially_reviewed, 19/77, 2 unresolved | 0 |
| 33_BSCS-2025-2026 | 9 (7/0/2) | 7 | 55/7/0 | S6-U1 (broken S6) | 7, 6, 0, 2, 1/1 | partially_reviewed, 53/55, 3 unresolved | 0 |
| 13_BSE-Innovation-and-Tech | 3 (2/0/1) | 2 | 2/74/0 | SU-U1 | 2, 0, 0, 0, 1/1 | partially_reviewed, 2/2, 1 unresolved, 13 audit-listed codes undecided | 0 |

Plan facts: BSBA-HRM and Architecture match exactly (Architecture: 17 `title_from_pdf` rows, each shows a proposal, 0 pre-selected). BSCS: the SU section lists the footnote codes (`CS Elect 4/La` and so on); Other on an unclaimed question refused, Yes without a reason refused. 13: 74 unclaimed questions against 2 courses (the plan text says 76 codes; 76 is the total question count here, 15 audit-listed codes + 59 found in the PDF text), no proposal anywhere, and all 76 questions answered No-with-reason in a throwaway ledger with 0 refusals. BSBA-HRM's 1 proposal row went to Other (answers are ordered Other, No, then Yes).

Differences: 13 has 2 clean sections (S1, S2) that get a bulk question, 33 has two broken sections (S6 and SU) and S6-U1 comes first. Time to first question (open session, queue, first question) was 11.0 to 11.7 s on every prospectus, far over the one second expectation (not a gate): a profile of `open_session` on BSBA-HRM shows the time is the import of torch and transformers when the Docling JSON is loaded for the markup twin, not GUI work.

Finding for the owner (not changed here): `content_review_state` counts only the audit-listed unclaimed codes. On 13 (copy), Yes on both courses and the 15 audit-listed codes, with the 59 PDF-found unclaimed questions left open, gives `reviewed` while 59 questions are still open. The sheet path has the same rule (shared function); the GUI shows the state word live, so it can say `reviewed` with open questions. "Reviewed" is not approval, but this is worth a decision before the trial.

Phase-C-fresh candidate (BSBA-HRM): the cached Docling JSON (`docling_jsonified_output\task2b_standing_isolated_2026-09-29\...\BSBA-HRM-for-student-new-version_docling.json`, copied to scratch) re-run with `python -m backend.bintanong_tools.prospectus_extractor -i COPY_docling.json -o scratch\fresh\...json --no-semantic-doc` (no PDF reconversion; the tool says the PDF is not verified, so the smoke gets the PDF hash from `--pdf`). 49 courses: resolved 24, blank_unreviewed 23, standing_condition 2. Smoke: 23 prerequisite questions (listed after all course questions), answers Yes 2, No 1, Other 1 (typed `SMOKE 101`), 0 refused; after materialise: reviewed_empty 2 (only the two accepted blanks), unresolved_reference 1 (the typed text), blank_unreviewed 20.

Step 5, equivalence (BSBA-HRM and 01_Architecture, six course-field decisions each: ok, ok with reason, edit title, edit code, unresolved with reason, fix a or edit): GUI ledger and sheet ledger (`fixer_cli sheet`, edited sheet, `fixer_cli apply`) have 9 entries each and differ only in `via` and `entry_id`; `entry_id` is a hash of every other field including `via`, so a different `via` forces a different id, and with `via` normalised and the id recomputed the two ledgers are equal. `recorded_at` was frozen for both (the clock is the only other thing that would differ). `materialise` on both: the corrected JSON is equal under the Task 4 comparison (`review.applied_entry_ids` removed, since those are the entry ids), byte-for-byte NOT identical (only `review.applied_entry_ids` differs). The sheet writes no prerequisite entries, so equivalence covers the course fields only. Outputs: `scratch\gui_e2e_0710\equiv\`, `equiv_*.json`, `smoke_*.json`.

## GUI review fixes (independent review of f09291e..6bc599a) - 2026-10-07

- M1: the badge, and any text, now says "Yes and Other never hold back content review; a No does" (a prerequisite No writes `unresolved`, which keeps `content_review` at `partially_reviewed`; behaviour unchanged, now tested through the session).
- M2: `ledger.materialise` records an accepted `prerequisites_raw` entry it declines to stamp `reviewed_empty` in `report["skipped"]` (and `review.skipped`) as `prerequisite_not_stamped: ambiguous cell | duplicate course locator | cell is not blank`. What is stamped is unchanged. The GUI and `fixer_cli` already print the skipped count.
- M3: the e2e GUI-vs-sheet test now compares ledger entries entry for entry (all but `via`, `entry_id`, `recorded_at`) and the materialised candidates under the Task 4 comparison; a garbled typed title in `answers._course` fails it. The full-session test asserts the exact unresolved entries.
- M4: tests for the exactly-one-course stamp guard and for progress counting only course-field questions.
- M5, M6: the GUI uses the extractor's `clean_str` to decide a blank prerequisite cell; a bare number is refused in any script's digits (`str.isdecimal`).
- M7: `questions.py` docstring fixed; prerequisite questions are in section-health order in attention mode (docstring and the Task 10 note above corrected, behaviour unchanged).

### Publication A–D verification and specification fixes (2026-10-07T05:15:40.7212091+08:00)
- Publication worktree: C:\Users\Hawksprey\source\repos\Bintanong-wt\publish-a-d; branch publish/prospectus-a-d-20261007; base80dd718; code tip9f9a33b. Local dev remains5c34fd7. This branch excludes GUI/OCR implementation and includes their historical plans with explicit unfinished-scope notes (6579483). Whitespace-only correction40801ac.
- Fresh main-venv baseline986passed13subtests3warnings, locked external API/tools/dev environment992passed13subtests6warnings. Owner-authorized system py -3.13 fullsuite992passed13subtests5warnings and actual project Janus probe true. Native Janus in the disposable environment remains NOT RUN (C++ compiler unavailable); system probe is separately verified.
- Independent Spec review confirmed two P2 issues. Authentic markup regression1failed1passed, ledger2failed1passed. Captured PDF digest now passed into markup renderer (74d76ae); all corrected course prerequisite states re-annotated, retaining structural ambiguity evidence (9f9a33b). Existing renderer test doubles now accept the real optional keyword. Initial full rerun209failed788passed exposed those outdated doubles; final focused433passed and full997passed13subtests5warnings after correction. Red outputs retained, not erased or called green.
- Fresh post-fix course comparer versus5c34fd7:44/44 identical; only run_identity.package_sha256/run_key changed44 each. Phase C states1005/689/253/59/20/2/3 (blank/resolved/unresolved/standing/unreadable/none/alternative). Self-test80/80. B2healthmixed21/warnings_only3/broken19/clean1; title_from_pdf67/strip_banner0/unclaimed_code316/banner_leak3. Sheets01/16/33 parse/check_against/build errors0. All19 trial-folder files unchanged around the initial trial gate. Temporary comparer baseline worktrees removed cleanly after completion.
- Evidence: E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\gate-*.log/json, fix-*.log, review-spec.md, checkpoint.json/events.jsonl. Root direct PowerShell ran broad gates. Standards reviewer active; scoped Spec recheck pending. Publication push/PR NOT YET DONE. Institutional copying NOT YET DONE; source preflight78paths59PDF17JPG2PPTX, longest destination220. Source approval null/pending.
- Newly supplied external redocling_handbook.py read only and recorded in handbook-script-inspection.md. Existing CPU text-only helper has no OCR/table processing/source binding and unique-token overlap is not an accuracy gate; future Phase2 plan must preserve original page offsets and use isolated scratch output.
- Next: resolve confirmed Standards findings, independent scoped Spec recheck, outgoing diff/attribution check, then push publication branch and create PR to GitHub dev. No automatic merge/dev movement, no institutional approval. GUI/E/F/OCR remain local; formal Phase1 preparation only.
### Standards fixes F1 RED (2026-10-07T05:19:14.5594843+08:00)
- HEAD: 407813c1fad100bceb662a129d2c64321791bc8f; dirty paths:  M tests/test_prospectus_ledger.py.
- Result: 3 failed, 2 passed, 10 deselected; exit 1; wrong reviewed status for undecided/wrong-PDF/stale anomaly. Command: py -3.13 -m pytest tests/test_prospectus_ledger.py -k persisted_anomalies -q -p no:cacheprovider --basetemp <scratch>/f1-red-temp (PYTHONDONTWRITEBYTECODE=1; f1-red.log).
- Scratch: E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\standards-fixes; running processes: none at boundary.
- Next: Reuse placement.unclaimed_items in both ledger completion and staleness checks; then focused green. Root broad gates and logical commits pending; human trial/approval/real-photo gates pending.


### Standards fixes F1 GREEN (2026-10-07T05:19:58.4364815+08:00)
- HEAD: 407813c1fad100bceb662a129d2c64321791bc8f; dirty paths:  M backend/bintanong_tools/prospectus_extractor/ledger.py;  M plans/plan_current_progress/extractor_split_progress.md;  M tests/test_prospectus_ledger.py.
- Result: 141 passed; exit 0; ledger, sheet, B2 regression files. Command: py -3.13 -m pytest tests/test_prospectus_ledger.py tests/test_prospectus_b2_codex_review.py tests/test_prospectus_b2_review_fixes.py tests/test_prospectus_sheet.py -q -p no:cacheprovider --basetemp <scratch>/f1-green-temp (PYTHONDONTWRITEBYTECODE=1; f1-green.log).
- Scratch: E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\standards-fixes; running processes: none at boundary.
- Next: F2 write authority regressions before production changes. Root broad gates and logical commits pending; human trial/approval/real-photo gates pending.


### Standards fixes F2 RED (2026-10-07T05:20:20.7830196+08:00)
- HEAD: 407813c1fad100bceb662a129d2c64321791bc8f; dirty paths:  M backend/bintanong_tools/prospectus_extractor/ledger.py;  M plans/plan_current_progress/extractor_split_progress.md;  M tests/test_prospectus_ledger.py;  M tests/test_prospectus_materialise.py.
- Result: 5 failed, 9 deselected; exit 1; executable inherited authority, zero incomplete count, pending top-level review. Command: py -3.13 -m pytest tests/test_prospectus_materialise.py -k "stale_authority or top_level_review_status" -q -p no:cacheprovider --basetemp <scratch>/f2-red-temp (PYTHONDONTWRITEBYTECODE=1; f2-red.log).
- Scratch: E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\standards-fixes; running processes: none at boundary.
- Next: Recompute via authority.build_authority, preserve source gates, explicitly block stale derived sections. Root broad gates and logical commits pending; human trial/approval/real-photo gates pending.


### Standards fixes F2 GREEN (2026-10-07T05:21:21.6656947+08:00)
- HEAD: 407813c1fad100bceb662a129d2c64321791bc8f; dirty paths:  M backend/bintanong_tools/prospectus_extractor/ledger.py;  M plans/plan_current_progress/extractor_split_progress.md;  M tests/test_prospectus_ledger.py;  M tests/test_prospectus_materialise.py.
- Result: 351 passed; exit 0; authority, materialise, ledger and B2 regression files. Command: py -3.13 -m pytest tests/test_prospectus_materialise.py tests/test_prospectus_authority.py tests/test_prospectus_ledger.py tests/test_prospectus_b2_codex_review.py tests/test_prospectus_b2_review_fixes.py -q -p no:cacheprovider --basetemp <scratch>/f2-green-temp (PYTHONDONTWRITEBYTECODE=1; f2-green.log).
- Scratch: E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\standards-fixes; running processes: none at boundary.
- Next: F3 write immutable semantic-map identity/publication regressions before production changes. Root broad gates and logical commits pending; human trial/approval/real-photo gates pending.


### Standards fixes F3 RED (2026-10-07T05:22:03.5026300+08:00)
- HEAD: 407813c1fad100bceb662a129d2c64321791bc8f; dirty paths:  M backend/bintanong_tools/prospectus_extractor/ledger.py;  M plans/plan_current_progress/extractor_split_progress.md;  M tests/test_prospectus_input_snapshot.py;  M tests/test_prospectus_ledger.py;  M tests/test_prospectus_materialise.py.
- Result: 4 failed, 2 passed, 11 deselected; exit 1; map edits/deletion/appearance publish and transient edit mislabels metadata under original digest. Command: py -3.13 -m pytest tests/test_prospectus_input_snapshot.py -k semantic -q -p no:cacheprovider --basetemp <scratch>/f3-red-temp (PYTHONDONTWRITEBYTECODE=1; f3-red.log).
- Scratch: E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\standards-fixes; running processes: none at boundary.
- Next: Capture semantic bytes via InputSnapshot, parse captured text with metadata owner, pass same capture to run_identity, check map bytes/presence before publication. Root broad gates and logical commits pending; human trial/approval/real-photo gates pending.


### Standards fixes F3 GREEN (2026-10-07T05:23:04.2020195+08:00)
- HEAD: 407813c1fad100bceb662a129d2c64321791bc8f; dirty paths:  M backend/bintanong_tools/prospectus_extractor/identity.py;  M backend/bintanong_tools/prospectus_extractor/ledger.py;  M backend/bintanong_tools/prospectus_extractor/metadata.py;  M backend/bintanong_tools/prospectus_extractor/pipeline.py;  M plans/plan_current_progress/extractor_split_progress.md;  M tests/test_prospectus_input_snapshot.py;  M tests/test_prospectus_ledger.py;  M tests/test_prospectus_materialise.py.
- Result: 212 passed; exit 0; captured input, identity, cache, skip and publication files. Earlier green selection error: nonexistent historical test_prospectus_runs.py, exit 4, no tests; preserved f3-green-selection-error.log. Command: py -3.13 -m pytest tests/test_prospectus_input_snapshot.py tests/test_prospectus_identity.py tests/test_prospectus_cache.py tests/test_prospectus_batch_skip.py tests/test_prospectus_publish.py -q -p no:cacheprovider --basetemp <scratch>/f3-green-temp (PYTHONDONTWRITEBYTECODE=1; f3-green.log).
- Scratch: E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\standards-fixes; running processes: none at boundary.
- Next: Self-review diff and update two existing decision notes; report uncommitted batch to root for broad gates/review/commits. Root broad gates and logical commits pending; human trial/approval/real-photo gates pending.

### Standards fixes IMPLEMENTER HANDOFF (2026-10-07T05:24:24.2172574+08:00)
- HEAD: 407813c1fad100bceb662a129d2c64321791bc8f; dirty paths:  M backend/bintanong_tools/prospectus_extractor/identity.py;  M backend/bintanong_tools/prospectus_extractor/ledger.py;  M backend/bintanong_tools/prospectus_extractor/metadata.py;  M backend/bintanong_tools/prospectus_extractor/pipeline.py;  M docs/decisions/prospectus-cache-and-publication.md;  M docs/decisions/prospectus-status-separation.md;  M plans/plan_current_progress/extractor_split_progress.md;  M tests/test_prospectus_input_snapshot.py;  M tests/test_prospectus_ledger.py;  M tests/test_prospectus_materialise.py.
- Result: Exactly three fixes implemented; F1 red3failed2passed -> green141passed; F2 red5failed -> green351passed; F3 red4failed2passed -> green212passed. No broad gates or commits run by implementer. git diff --check passes. Command: See external report.md and f1/f2/f3-red/green.log for exact commands and actual results; all pytest invocations py -3.13, PYTHONDONTWRITEBYTECODE=1, -p no:cacheprovider, basetemp under standards-fixes.
- Scratch: E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\standards-fixes; running processes: none at boundary.
- Next: Root pins current dirty code; run fresh full gates and independent scoped specification/standards reviews; only root commits explicit logical paths after gates. Implementer will make no further edits. Root broad gates and logical commits pending; human trial/approval/real-photo gates pending.

### Publication final gates and independent rechecks (2026-10-07T05:31:50.9357905+08:00)
- Code54f31f9: all five confirmed Spec/Standards findings fixed, with genuine red evidence retained. Review-completeness/authority commitad931c4 and captured-semantic-map commit54f31f9 followed root fullgate. Fresh owner-authorized system py -3.13 fullsuite1013passed13subtests5warnings, self80/80; actual Janus1.5.2/SWI10.1.6 arithmetic/project bridge probes passed. Existing environments untouched; system versions recorded externally.
- Final comparer44/44course-fieldidentical vs5c34fd7, onlypackage_sha256/run_key changed44each; PhaseCcounts1005/689/253/59/20/2/3 unchanged. FinalB2counts21/3/19/1health, title67/strip0/unclaimed316/banner3. Finaltrial01/16/33errors0 and19trialoriginalhashesunchanged. Temporary ready comparer baseline removed cleanly. gitdiffcheckpassed; outgoing attribution count0; GUI61d251d/OCRf9e0dbc are not ancestors and their implementation paths/rawinstitutional files absent from outgoingdiff.
- IndependentSpecrecheckAPPROVED/NONE:20externalassertions; independentStandardsrecheckAPPROVED/NONE:16scopedtests+11adjacentassertions. Reportsreview-spec-recheck.md/review-standards-recheck.md attach to frozen reviewedcode; documentary commits do not change it. Evidence E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\gate-ready-*.log/json and review reports. Root directPowerShell ran every broad gate.
- Ready to push publish/prospectus-a-d-20261007 and create GitHub PR targetingdev; no automaticmerge/force/historyrewrite/localdevmovement. GUI/OCR implementation remains local; only their historical plans are included. B2humanTasks12-14, GUItrial/finalcloseout, sourceauthorization and realphotogatesremainpending. Nothing here is institutional approval.


### GUI technical batch MERGE F1 F2 GREEN (2026-10-07T05:43:12.543632+08:00)
- Worktree: C:\Users\Hawksprey\source\repos\Bintanong-wt\gui-fixes; branch `feat/review-gui-fixes-20261007`; HEAD `cf8b11c566d76bd5048a761a169907aee31a242b`; MERGE_HEAD `3227ac8a801396a06b0d593c975df313e7f67c84`.
- Result: Merge-focused initial fixture check 2 failed/74 passed corrected expectation only, final76passed; F1 red2failed22deselected green61passed; F2 red2failed1passed1deselected green42passed; pytest exit1 on reds and0 on greens. Logs/commands: external `publish_resume_2026-10-07/gui-fixes/report.md` and named red/green logs.
- Git at boundary (index conflict labels remain until root explicitly stages):
```text
M  backend/bintanong_tools/prospectus_extractor/identity.py
UU backend/bintanong_tools/prospectus_extractor/ledger.py
M  backend/bintanong_tools/prospectus_extractor/metadata.py
M  backend/bintanong_tools/prospectus_extractor/pipeline.py
 M backend/bintanong_tools/prospectus_review_gui/session.py
 M backend/bintanong_tools/prospectus_review_gui/static/review.js
M  docs/decisions/prospectus-cache-and-publication.md
M  docs/decisions/prospectus-status-separation.md
AA plans/2026-10-04-prospectus-ocr-measurement.md
AA plans/2026-10-05-prospectus-review-gui.md
UU plans/plan_current_progress/extractor_split_progress.md
M  tests/test_prospectus_batch_skip.py
M  tests/test_prospectus_input_snapshot.py
UU tests/test_prospectus_ledger.py
M  tests/test_prospectus_markup.py
UU tests/test_prospectus_materialise.py
M  tests/test_prospectus_publication.py
 M tests/test_review_gui_session.py
?? tests/test_review_gui_client.py
```
- Running processes: none owned by implementer at this completed test boundary. Next: F3 authentic transport/malformed-JSON RED then shared helper/caller minimal fix and focused GREEN; root broad gates follow.
- Do not repeat: publication push/PR, original corpus copy/hash gate, completed GUI Tasks 1-11; no commits/staging/push/dev movement by implementer. Pending: root full gates/browser/Lighthouse/reviews; human Task 12; Task 13 closeout; institutional approval.


### GUI technical batch F3 RED (2026-10-07T05:44:49.547884+08:00)
- Worktree: C:\Users\Hawksprey\source\repos\Bintanong-wt\gui-fixes; branch `feat/review-gui-fixes-20261007`; HEAD `cf8b11c566d76bd5048a761a169907aee31a242b`; MERGE_HEAD `3227ac8a801396a06b0d593c975df313e7f67c84`.
- Result: F3 red30failed1passed4deselected exit1; failures confirm network rejection, malformed/null/incomplete success bodies and5xx unknown-status handling absent across shared API callers; validation422control passed. Logs/commands: external `publish_resume_2026-10-07/gui-fixes/report.md` and named red/green logs.
- Git at boundary (index conflict labels remain until root explicitly stages):
```text
M  backend/bintanong_tools/prospectus_extractor/identity.py
UU backend/bintanong_tools/prospectus_extractor/ledger.py
M  backend/bintanong_tools/prospectus_extractor/metadata.py
M  backend/bintanong_tools/prospectus_extractor/pipeline.py
 M backend/bintanong_tools/prospectus_review_gui/session.py
 M backend/bintanong_tools/prospectus_review_gui/static/review.js
M  docs/decisions/prospectus-cache-and-publication.md
M  docs/decisions/prospectus-status-separation.md
AA plans/2026-10-04-prospectus-ocr-measurement.md
AA plans/2026-10-05-prospectus-review-gui.md
UU plans/plan_current_progress/extractor_split_progress.md
M  tests/test_prospectus_batch_skip.py
M  tests/test_prospectus_input_snapshot.py
UU tests/test_prospectus_ledger.py
M  tests/test_prospectus_markup.py
UU tests/test_prospectus_materialise.py
M  tests/test_prospectus_publication.py
 M tests/test_review_gui_session.py
?? tests/test_review_gui_client.py
```
- Running processes: none owned by implementer at this completed test boundary. Next: Implement central transport/JSON handling and visible caller messages preserving answers without automatic retries; focused green then root broad gates.
- Do not repeat: publication push/PR, original corpus copy/hash gate, completed GUI Tasks 1-11; no commits/staging/push/dev movement by implementer. Pending: root full gates/browser/Lighthouse/reviews; human Task 12; Task 13 closeout; institutional approval.


### GUI technical batch IMPLEMENTER HANDOFF CODE FROZEN (2026-10-07T05:49:46.547495+08:00)
- Worktree: C:\Users\Hawksprey\source\repos\Bintanong-wt\gui-fixes; branch `feat/review-gui-fixes-20261007`; HEAD `cf8b11c566d76bd5048a761a169907aee31a242b`; MERGE_HEAD `3227ac8a801396a06b0d593c975df313e7f67c84`.
- Result: F3green74passed exit0; followup red1failed1passed35deselected exit1; finalfocused175passed exit0; gitdiffcheck0; bothstage2/3 testfunctions and allplan/progresslines preserved; trialguide/Task13decisionpreparation written with gates pending. Logs/commands: external `publish_resume_2026-10-07/gui-fixes/report.md` and named red/green logs.
- Git at boundary (index conflict labels remain until root explicitly stages):
```text
M  backend/bintanong_tools/prospectus_extractor/identity.py
UU backend/bintanong_tools/prospectus_extractor/ledger.py
M  backend/bintanong_tools/prospectus_extractor/metadata.py
M  backend/bintanong_tools/prospectus_extractor/pipeline.py
 M backend/bintanong_tools/prospectus_review_gui/session.py
 M backend/bintanong_tools/prospectus_review_gui/static/review.js
M  docs/decisions/prospectus-cache-and-publication.md
M  docs/decisions/prospectus-status-separation.md
AA plans/2026-10-04-prospectus-ocr-measurement.md
AA plans/2026-10-05-prospectus-review-gui.md
UU plans/plan_current_progress/extractor_split_progress.md
M  tests/test_prospectus_batch_skip.py
M  tests/test_prospectus_input_snapshot.py
UU tests/test_prospectus_ledger.py
M  tests/test_prospectus_markup.py
UU tests/test_prospectus_materialise.py
M  tests/test_prospectus_publication.py
 M tests/test_review_gui_session.py
?? docs/decisions/prospectus-review-gui.md
?? tests/test_review_gui_client.py
```
- Running processes: none owned by implementer at this completed test boundary. Next: Root pins final code, runs broad suite/selftest/corpus/browser/Lighthouse gates, stages explicit resolved foundation paths and feature hunks, commits only after gates and reviews; do not treat index conflict labels as remaining file markers.
- Do not repeat: publication push/PR, original corpus copy/hash gate, completed GUI Tasks 1-11; no commits/staging/push/dev movement by implementer. Pending: root full gates/browser/Lighthouse/reviews; human Task 12; Task 13 closeout; institutional approval.

## GUI technical fixes and reviewed foundation merge — 2026-10-07T06:00:05.6536110+08:00

- Owner /root; local branch feat/review-gui-fixes-20261007; foundation merge1068ef4 joins cf8b11c and reviewed publication3227ac8, preserving both plans/progress/test histories. Localdev5c34fd7 untouched; no GUI push.
- Authentic F1 red2failed→green61; F2 red2failed1passed→green42; F3 red30failed1passed→green74; follow-up queueerror red1failed1passed→finalfocused175passed. Full commands/logs are external scratch publish_resume_2026-10-07/gui-fixes/report.md.
- Root fresh systempy3.13 comprehensive1415passed1skipped13subtests8warnings; self80/80; comparer44/44 vs5c34fd7 with onlypackage_sha256/run_key changes; PhaseC counts1005blank/689resolved/253unresolved/59standing/20unreadable/2none/3alternative unchanged. B2mixed21/warnings3/broken19/clean1,title_from_pdf67,strip_banner0,unclaimed_code316,banner_leak3. Trial01/16/33 zeroerrors,19filesunchanged.
- Fresh scratch BSBA-HRM candidate49courses,23blankprerequisitequestions; localserver started with originalPDF scratchcopy and ready markup twin, then ownedserver stopped. CUA inventory apps=[]/browsers=[], IAB unavailable; keyboard/browser pass NOT RUN. Installed Lighthouse command/package absent; audit NOT RUN. These are not passed gates; humantrial and Task13closeout pending.
- Three fixes: section PDF shown without invented boxes; prerequisite twin focuses prerequisite cell; sharedAPI visibly preserves lost-response saves as unknown without autoretry. D11 ambiguity and existing bulk/prerequisiteNo semantics retained. No sourceapproval or institutionalactivation.
- Separate independent Spec/Standards reviews still required before E integration. Next: reviewcf8b11c..GUIfeaturetip, resolve confirmedfindings, then E fromlocaldev mergedwithreviewedGUIcandidate. Do not repeatpublication/sourcecopy/completedTasks1–11.

### GUI Spec fix round1: PDF image failure — 2026-10-07T06:12:17.7283034+08:00

- Speccf8..8caa1eb:232focusedpassed; oneconfirmedP2 atreview.js image-source assignment, actualNode imageerrorreproducer failed. ImagePNG requests bypassJSONapi and previously hadnovisibleerror.
- Authentic verifiedred4failed2passed49deselected, beforeproductionchanges; corrected missingDOM classList.toggle testharnessboundary ininitialred and retainedbothlogs. Minimum nativeonerror hidesfailedimage/clearsboxes; pdf-note ownlivepolite message preserves answer andglobal save-statusunknown; manualZoomrecovery/noautoretry; handlerclearedforunavailable/no-pageviews.
- Implementerfocused120passed. Rootfreshfull1421passed1skipped13subtests8warnings, freshself80/80. Extractorcodeunchanged since44/44corpus,B2/Ccounts andtrialzeroerrors19hashes inpriorrootbatch. Browser/keyboard/Lighthouse remainNOTRUN forreportedavailability; humantrial/closeoutpending.
- Evidenceexternal publish_resume_2026-10-07/gui-fixes/image-error/{red-verified.log,green.log,report.md}, root-image-full.json, root-image-selftest.log. NextscopedSpecrecheck thenindependentStandards; do notpublishGUI ormovedev.

### GUI Standards P2 response-shape RED — 2026-10-07T18:15:34.0873505+08:00

- Base41fe3c3; branch feat/review-gui-fixes-20261007; production unchanged. Actual client NodeVM:54failed2passed42deselected exit1 before production edits. Complete successful/fallback consumer fixtures pass; present-invalid nested bodies fail visibly in the tests as expected.
- Evidence external publish_resume_2026-10-07/gui-fixes/shape-error/{red.log,report.md,checkpoint.json}; next sharedAPI shape validation, focusedgreen, root broadgates/review/commit. No source approval, autoretry or semantics change.

- 2026-10-07T18:20:23.1877828+08:00 adjacent shared-boundary400 bad-error envelopes: authentic verifiedred12failed9passed98deselected exit1 before error guard; initial arrow-fixture mistake corrected and retained externally. Successful-shape client/APIgreen125passed exit0. Next malformed-error guard and actual server-shape consumption; root owns broadgates/commit.

### GUI Standards P2 response-shape HANDOFF CODE FROZEN — 2026-10-07T18:22:12.4392448+08:00

- SharedAPI native predicates validate consumer-required success values across answer/materialise/state/queue/question/twin, plus malformed error envelopes. UnknownPOST and visibleGET recovery preserve entered answers/currentview, with no autoretry. Valid4xx errors stay definite Not saved; existing source/prerequisite/bulk semantics preserved.
- Authentic red54failed2passed42deselected exit1; malformed-error verifiedred12failed9passed98deselected exit1 (initial fixture error retained and corrected). Final client/APIgreen146passed in8.44s exit0. External actual-serverprobe16shapes accepted, loadedquestion/save/materialise consumed without exceptions exit0. gitdiffcheck passed; no staging/commit/push/dependencies or owner-checkout edits.
- Frozenfiles: review.js; tests/test_review_gui_client.py; docs/decisions/prospectus-review-gui.md; this progress ledger. Exact commands/logs/atomic checkpoint: external publish_resume_2026-10-07/gui-fixes/shape-error/report.md and checkpoint.json. Root next: broadgates, commit, independent scopedSpec/Standards rechecks. HumanTask12/13 closeout remains pending; no institutional approval.

### Root gate boundary 2026-10-07T18:25:16.7121634+08:00
- Frozen malformed-response guard batch: full system py -3.13 tests green; exact observed summary in external gate-gui-shape-comprehensive.json. Self-test80/80, gate-gui-shape-selftest.json. Focused146pass; genuine success-shape controls16 accepted; red54fail2pass and malformed-error red12fail9pass preserved. No extractor source/course behavior changed by this client-only patch. Independent scoped Spec and Standards rechecks next; browser/Lighthouse/human trial remain pending.
