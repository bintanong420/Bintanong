# Phase D handoff: safe cache identity and output publication

Prospectus workstream, parallel to the master plan (not a formal phase; `plans/INDEX.md` is untouched).
Branch `feat/prospectus-phase-d-safe-cache`. Decision record: `docs/decisions/prospectus-cache-and-publication.md`.
Progress log: `plans/plan_current_progress/extractor_split_progress.md`.

## Status

Implementation, documentation and runtime gates are done. **Not complete until the independent Claude whole-range review passes and the human gates below are met.** No Codex gate was run. Nothing was pushed or merged.

## Commits

Phase D range: `git log --oneline 1984b27^..HEAD` (the hashes were rewritten on 2026-10-07; older hashes in other documents are stale). Contains the merge of B2 (`31ca1f0`, `d56ae9f`) and these Phase D commits:

| Commit | Subject |
|---|---|
| `b032472` | feat: add conversion and run identity for the prospectus extractor |
| `f430743` .. `a88b3c6` | cache reuse keyed on PDF bytes and settings; per-write temp files; verified bytes are the parsed bytes |
| `9b9d0e6`, `52b063b`, `4293c0f` | staged publication, manifest, failure diagnostics, skip by run identity |
| `e9b57be`, `6a88721` | immutable input snapshot; captured cache pair bound into publication |
| `f308944`, `ac26d7b` | discovery exclusions scoped to the selected root; unsafe glob patterns refused |
| `7475f58`, `735d0ee` | LF batch manifest and review CSV; shorter staging names and default root |
| `ea710e6`, `ae362d2` | context-created outputs are never reused; force wired into the TUI |
| `5d6723e` | docs: record the safe cache and output publication design and its evidence |
| `a227c95` | fix(prospectus): write the failure marker before copying diagnostics (C1) |
| `10a6d2e` | fix(prospectus): fall back to a drive-root output folder when the home path is long (S-a) |
| `95c56bf` | fix(prospectus): write the isolated manifest with LF bytes (S-c) |
| next | docs: name the venv behind each test count; finalise decision record and Phase D handoff |

## Commands and results (main backend venv, 2026-10-07)

- Full suite: `backend\.venv\Scripts\python.exe -m pytest -q tests --ignore=tests/test_api_probes.py --ignore=tests/test_embedding_service.py ...`: **986 passed**, 13 subtests, 3 warnings. (984 before this session plus 2 new tests. The 990 quoted earlier comes from the GUI-review venv that also runs the API and embedding tests.)
- Self-test: `Self-test: 80/80 checks passed.`
- Comparer: `scripts\prospectus_course_compare.py --base-ref 5d6723e --jobs 6 --status-report` with the 44 cached inputs and the original semantic map: **44/44 identical**, exit 0. Only `run_identity.package_sha256` and `run_identity.run_key` changed (44 each). Prerequisite states: blank_unreviewed 1005, resolved 689, unresolved_reference 253, standing_condition 59, unreadable 20, alternative_or_exception 3, stated_none 2. The base worktree was created under external scratch and removed afterwards.
- B2 triage: health mixed 21, warnings_only 3, broken 19, clean 1; `title_from_pdf` 67; no `strip_banner`; `unclaimed_code` 316; `banner_leak` 3.
- Trial sheets 01, 16, 33 (read-only `check_against`): 0 errors each. The 101 original and trial files were hash-identical before and after.

## Follow-ups from the independent review (this session)

| Item | Red | Green |
|---|---|---|
| C1 | `test_a_failed_copy_still_leaves_a_recognisable_diagnostics_folder`: no `failure.json` after a failed second copy | marker written first; 72 passed in the publish tests |
| S-a | worst-case path test with a 38-character home gave 272 > 260 | default root falls back to `<drive>\Bintanong\output` above 40 characters; 72 passed |
| S-c | `isolated_manifest.json` contained `\r\n` | written through `write_text_lf`; 6 passed in the batch tests |
| Wording | none (docs) | every quoted count names its venv |

The second PDF hash in `prospectus_batch.py` was left in place with a comment: it is one extra read per PDF in a run dominated by Docling.

## Deviations from the plan

- The cache pair is published after the main JSON, listed in the manifest under `cache_files`, and verified (F1). The plan published it first and unlisted.
- Default output root moved to `~/Bintanong/output`, with a drive-root fallback when that exceeds 40 characters (S1, S-a).
- `QUOTE_ALL` for the review CSV was replaced by `QUOTE_MINIMAL` with LF record separators after runtime verification.
- The skip rule also refuses reuse when `source`, `approved_scope`, `review_entries` or `repair_provider` was supplied (S2).

## Risks

- **S-b.** A folder containing any `failure.json` is treated as diagnostics and skipped by discovery until the marker is removed.
- **S-e.** A missing input raises `FileNotFoundError` from the snapshot read before staging, so no `failed/` folder is written for it.
- Publication is not atomic across files; verification detects a mixed set, there is no rollback.
- One writer per output stem; concurrent writers are not coordinated.
- Home paths between 19 and 40 characters of root keep the home default; explicit long output roots are the caller's responsibility.
- Course-field equality is regression equivalence, not proof of extraction accuracy.

## Remaining gates (not done)

1. Independent Claude whole-range review of Phase D (the Codex gate is replaced).
2. The user's trial review of `review_trial_2026-10-04` before B2, C and D merge into `dev`.
3. GUI Phase C integration (merge D into `gui`), then the GUI human trial.
4. No institutional, curriculum, Prolog or RAG release is approved by this work.
