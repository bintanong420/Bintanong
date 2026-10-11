# Phase D S2/S4 specification review

APPROVED for implementation batch 4320327bb68ec0973dd79ee7716ab5d893fe00a8..c40a38c9f633dd085766ca11f81f0dd3890810cc.
Reviewer: /root/d_skip_tui_spec. Review recorded: 2026-10-06T23:24:48+08:00. Read-only worktree: C:/Users/Hawksprey/source/repos/Bintanong-wt/phase-d; branch feat/prospectus-phase-d-safe-cache.

## Specification

Confirmed defects: NONE. Missing requirements: NONE. Unrequested production behavior: NONE.

- pipeline.py:347-352 writes skip_reusable from presence of all four specified parameters using `is None`; empty scopes, empty lists, empty/exhausted generators and falsey contract-valid sources/providers therefore remain supplied contexts. It adds neither authority nor context serialization, does not consume generators, and retains the original run key/cache binding. The unchanged build_payload at pipeline.py:75-85 materializes review entries once; the outer process parameter retains its supplied identity for the flag.
- batch.py:181-185 refuses explicit False and missing/nonboolean eligibility before identity reuse. Only literal True can proceed. Existing checks for audit, current run identity, publication/cache coherency and requested companions remain intact at batch.py:186-209. tests/test_prospectus_batch_skip.py:145-219 covers nine successfully published context forms and eight coherent missing/nonboolean flags, then a contextless rebuild and eventual successful skip.
- tests/test_prospectus_batch_skip.py:43-60 now requires exact `unchanged: identical run identity`, checks the True flag and confirms unchanged bytes/mtimes. Force precedence now has the exact expected reason.
- tui.py:91 displays the existing force field; tui.py:202-207 configures it with its current value as default and describes identity-verified, complete, non-error reuse accurately. tui.py:286 threads the same existing field into single-file processing. Existing batch path passes the same configuration unchanged. tests/test_prospectus_batch_skip.py:288-359 exercises both True and False, actual pipeline cache outcomes and interactive batch skip/force precedence.
- No changes to identity ownership, raw cache ownership, source approval, schema version, legacy compatibility exports or executable authority. No new dependency/module/provider serialization. Only pipeline, batch, TUI, regression tests and progress appear in the package.

## Independently executed evidence

All commands used PowerShell from the worktree above, PYTHONDONTWRITEBYTECODE=1, interpreter C:/Users/Hawksprey/source/repos/Bintanong/backend/.venv/Scripts/python.exe, pytest cache disabled, and external basetemp. No installation or worktree edits.

1. `-m pytest -q tests/test_prospectus_batch_skip.py -k 'context_publication or skip_eligibility or repeat_run' -p no:cacheprovider --basetemp 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_resume_2026-10-06/s2-spec-review-temp'`: exit 0, 18 passed, 68 deselected, 15.30s; no warnings. Log task-d-s2-spec-review-tests.log. Current tip includes six S4 tests, so deselection count differs from pre-S4 S2 evidence.
2. `-m pytest -q tests/test_prospectus_batch_skip.py -k tui -p no:cacheprovider --basetemp 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_resume_2026-10-06/s4-spec-review-temp'`: exit 0, 6 passed, 80 deselected, 8.55s; no warnings. Log task-d-s4-spec-review-tests.log.
3. `task-d-skip-tui-spec-probe.py`: exit 0. Independently checks exact identity/force prompts, current force=True default, Rich display and both EOF-preserved defaults. Probe and task-d-skip-tui-spec-probe.log are external. Named risk: new tests cover plain display but not Rich/current-default interaction; probe covers these without writing outputs.

Inspected saved authoritative red logs: S2 validated 18 failed/62 deselected (8.37s), and S4 4 failed/2 passed/80 deselected (7.39s), with exact expected failing test names. Prior S2 fixture/companion mistakes are honestly superseded in the report, not accepted as authoritative red evidence.

Inspected saved task-d-s4-full.log: 984 passed, 13 subtests passed, 3 warnings, 94.15s. This is implementer-run evidence, not rerun by this seat. The three upstream Docling/Pydantic deprecations are force_full_page_ocr, generate_table_images and RapidOCR rec_font_path from test_tools_contract.py::ToolsContractTests::test_synthetic_pdf_fixture_exists_and_parses; they are existing baseline warnings, not introduced by this diff. No task selector warnings. No broad repeat justified by review.

## Behavior preservation / concrete risk checks

The shared context-presence flag affects skip reuse, so inspected actual pipeline caller, authority/review entry flow and publication run-identity cross-binding. The TUI force field is shared across single and batch routes, so inspected those callers and existing batch force precedence. Existing strict read_manifest ensures run_identity is a mapping before the new access. These checks found no contract regression. No generated output/PDF/main .gitignore/historical handoff is staged or in the commit range. Both commits have the required Claude trailer.

Current state before and after review: HEAD c40a38c9f633dd085766ca11f81f0dd3890810cc, branch feat/prospectus-phase-d-safe-cache. Only ` M plans/plan_current_progress/extractor_split_progress.md`; no staged or untracked files. Dirty checkpoint preserved. git diff --check exit0, with existing Git LF-to-CRLF configuration notice only. All reviewer test/probe processes completed; no child agents dispatched.

## Limitations / declined-to-judge

No suspicions requiring follow-up. Separate quality seat, final whole-range D review, comprehensive suite, fresh corpus/real PDF failure gates, self-test and Task10 remain the controller's gates; this approval does not complete Phase D. Baseline original-corpus accuracy is not proven by mocked conversion task tests. No human GUI, real-photo, source-owner approval or institutional activation claim.

Read project extractor-reviewer.md, approved_execution.md, task-d-skip-tui-brief.md, preserved Phase D spec, report and immutable package. Requested old spec-reviewer-prompt.md does not exist in cached6.4.2; used actual task-reviewer-prompt.md scoped guidance with explicit user requirement for separate spec/quality seats and independently rerun commands. The immutable package has only short contextual hunks, so inspected complete affected functions and named shared-contract callers as authorized by task dispatch. No alternate skill approval flow introduced.

APPROVED
