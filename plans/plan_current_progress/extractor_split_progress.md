# Extractor package split — progress

Resume point for `plans/2026-10-03-prospectus-extractor-package-split.md`. Fresh Git and test output outrank this note.

- Branch: `refactor/prospectus-extractor-package`, created from `dev` at `7591264`.
- Monolith SHA-256 at base: `8ea75006a4c588902738c3a31096d44aa453a2fdfdeffae8750bf681eae3164d`.
- Recorded baseline (29 September, not rerun yet on this branch): 26 tests and 13 subtests passed; self-test 80/80.
- Pre-existing dirty files to leave alone: `.gitignore`, untracked `plans/CODEX_HANDOFF_prospectus_extractor_phase2_2026-09-26.md`.

## Phase A

| Task | State | Commit | Observed result |
| --- | --- | --- | --- |
| 1. Baseline and failing 1:1 test | not started | | |
| 2. Golden-output check | not started | | |
| 3. Splitter and generated package | not started | | |
| 4. Entry points, shim, relaunch change | not started | | |
| 5. Isolated batch uses the package | not started | | |
| 6. Golden proof, decision record, Codex gate | not started | | |
| 7. Remove scaffolding, hand off | not started | | |

## Later phases

B markup twin → C status separation → D cache and publication → E RAG provenance → F tools boundary. Each needs its own detailed plan before work starts.

## Log

- 2026-10-03: plan written and branch created. No code changed yet. Next step: Task 1, step 1.
