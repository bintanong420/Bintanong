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
| 3. Header, text blocks, reading order, page breaks | done | see git log | red: 11 failed, 10 passed (plan expected 12 failed: the determinism test already passes on the tables-only renderer); green: 22 passed; prospectus + other collectable tests 50 passed + 13 subtests (2 files uncollectable: no fastapi in this env); self-test 80/80. KNOWN DEFECT (real data): table cells are TOPLEFT frame, text items BOTTOMLEFT, so _y_down values are not comparable across the two and every text on a page sorts before every table (footnotes land above the table). Needs page height or a frame-normalising step; not fixed here. |
| 4. Pipeline, CLI, batch, TUI wiring | pending | | |
| 5. Course-field regression on 44 inputs | pending | | |
| 6. Visual check against the PDFs | pending | | |
| 7. Decision record, Codex gate | pending | | |

### Phase B log

- 2026-10-03: Task 1 done. Branch created from dev at 69ca855 (plan said 8d26f18; later docs commits only). Line references re-read: unchanged except pipeline.py essentials_path.write_text( now starts at line 233 (plan: block ends 237); loader.py export_to_markdown at 201; tui.py config row 89, ask 196, single_file 265-275.
- 2026-10-03: Task 2 done. Test and markup code taken verbatim from the plan; no deviations.
- 2026-10-03: Review fix commit 6a214e2: gap-assertion made falsifiable, line breaks in cell text rendered as <br>. Task 3 uses the same rule for text blocks (_esc_block).
- 2026-10-03: Task 3 done; plan code verbatim except _render_text uses _esc_block. Real-data check on BS CS 2025-2026 and BSA: 16/16 and 5/5 text items rendered, header text before first table, but mixed coordinate frames break text/table order (see Task 3 row).
