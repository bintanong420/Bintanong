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
| 4. Entry points, shim, relaunch change | not started | | |
| 5. Isolated batch uses the package | not started | | |
| 6. Golden proof, decision record, Codex gate | not started | | |
| 7. Remove scaffolding, hand off | not started | | |

## Later phases

B markup twin → C status separation → D cache and publication → E RAG provenance → F tools boundary. Each needs its own detailed plan before work starts.

## Log

- 2026-10-03: plan written and branch created. No code changed yet. Next step: Task 1, step 1.
- 2026-10-03: Task 1 done. Baseline confirmed (26 passed + 13 subtests, 80/80, SHA ok). New gate test: 2 failed, none skipped.
- 2026-10-03: Task 2 done. Run-to-run noise in old code: 1 JSON path in candidate.json, ('generated_at',); candidate_review.csv identical. Note the script prints noise=0 while the package is absent, because it only counts files present in C; measured A vs B by hand. Real noise count appears once the package exists.
- 2026-10-03: Task 3 done. Splitter copied verbatim from the plan, no changes. Three harmless false-hit imports (`from .common import track` under `if RICH_AVAILABLE` in courses, prolog, rag: a loop variable named `track` shares the spelling of Rich's `track`); no cycle, left as generated.
