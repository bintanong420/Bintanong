<!-- CODEX LIVE START -->
## CODEX LIVE CHECKPOINT (2026-10-07T04:03:52.6929380+08:00)

- Owner: /root; worktree: C:\Users\Hawksprey\source\repos\Bintanong-wt\integration-gui; branch: integration/gui-0710; HEAD: cf8b11c566d76bd5048a761a169907aee31a242b.
- Owner dev remains 5c34fd73adbd2806d6c48362eb248b74921fb79c. No AI trailers, pushes or dev movement authorized.
- Step: Gates a-g green; Spec completed (2 Medium, 1 Low ambiguity, no High); Standards running
- Recovery/evidence: E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\gui_integration_2026-10-07\checkpoint.json; gate-*.log/json; events.jsonl.
- Workers: /root/gui_integration_standards read-only active; Spec completed; gate processes finished; PowerShell checkpoint PID 37924.
- Next: Complete Standards report, atomically update pickup LATE/state table and owner untracked status sections3/8; STOP without moving dev
- The 2026-10-07 LATE rules and integration prompt supersede older queue and hashes. Verify live workers and Git before takeover.
<!-- CODEX LIVE END -->
# Codex pickup log: Bintanong prospectus workstream

## UPDATE 2026-10-07 (latest; it overrides the older HANDOFF NOW section below)

- **dev (main checkout) is now `5c34fd7`**. It contains B2, Phase C, Phase D and the OCR branch, merged via `integration/prospectus-0710` (tip was `f924820`, plus a whitespace fix). Gates passed on that merge: 1040 passed + 1 skipped, self-test 80/80, the 44-input comparer 44/44 identical, B2 triage counts unchanged. Nothing is pushed. `dev` is local only.
- The Claude trailers are stripped from all local branches and from the 4 public branches (GitHub). **Never add one.** Commit hashes in older notes are stale.
- **Phase D is finished** (tip `80dd718`, handoff `plans/prospectus-phase-d-handoff.md`).
- **Still separate:** `feat/prospectus-review-gui` (Tasks 1–9 committed, an independent review was running; Tasks 10–11 not started; **merge `dev` into it first**) and `feat/prospectus-b2-banner-split` (the user's go/no-go after their trial).
- **Phase E and F worktrees should start from `dev`** now, not from the phase-d tip.
- Whitespace nit and the 984-vs-990 count wording are already fixed.
- **GUI update (evening):** the `gui` branch now has `dev` merged in and all independent-review fixes (C1 pdfium lock, C2 partial write, C3 next question, C4 arrow keys, S1 wrong-Docling-JSON check, S2 to S7). Gates: main venv 1248 passed + 4 skipped, web venv `-k review_gui` 233 passed, self-test 80/80. **Next for the GUI:** one narrow independent re-check (read-only), then Task 10 (Phase C hooks: three states, prerequisite questions, `reviewed_empty`) and Task 11 (end to end on the 4 trial prospectuses, read-only), then merge into `dev`. Task 12 is the owner's own trial.

## UPDATE 2026-10-07 LATE: GUI branch finished, HANDOFF TO CODEX (Claude usage hit 90%)

**Start here. Claude stopped at step 4 of 6.** Rules are unchanged: no AI trailer, no push, never touch `C:\Users\Hawksprey\source\repos\Bintanong` (owner's dev, `5c34fd7`, dirty `.gitignore`), worktrees only, test first, PowerShell only, `--basetemp` under `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\`, never inside a repo. Do NOT move dev.

### State
- Branch `feat/prospectus-review-gui`, worktree `Bintanong-wt\gui`, **tip `61d251d`**, tree clean, `dev` (`5c34fd7`) is an ancestor, 0 trailers.
- Gates at `61d251d`: main venv **1259 passed + 6 skipped**, web venv `-k review_gui` **266 passed**, self-test **80/80**. (The extra skip is the new GUI test files, which skip in the main venv because it has no FastAPI.)
- Extra worktree `gui-t10` (branch `feat/prospectus-gui-task10`, tip `cd88706`) is already inside `gui`; delete it with `git worktree remove` when convenient.

### Map of what changed since the first GUI review (`4f894dd` = merge of dev)
| Commits | What | Review |
|---|---|---|
| `0de45ef`..`625ec4a` (C1-C4, S1-S7) | pdfium lock in `PageRenderer`; ledger encodes every entry before writing + text refusal + answer cap; next-question per mode; `keys.js` pure key map + node test; strict Docling cell-text check; socket/exit-code handling | Independent re-check: **no High**, defects D1-D3 |
| `3ee7d21`, `f09291e` (D1-D3, D5) | chunked body without Content-Length; lone surrogate in edit key/proposal and deep nesting no longer 500; edit value cap 2000 | fixed, tested |
| `9c9a748` | `ledger.materialise` stamps `reviewed_empty` only for an `accepted` `prerequisites_raw` on a blank cell, re-runs Phase C state annotation | Task 10 |
| `e255503` | new question kind `prerequisite` (qid `<row>:prereq`), asked for blank_unreviewed / unreadable / unresolved_reference / alternative_or_exception, placed after all course questions | Task 10 |
| `c27cda3`, `cd88706` | `/api/state` `review_states` (extraction audit, content review live from ledger, source verification), fixed line "A reviewed prospectus is not an approved curriculum", page badges | Task 10 |
| `6bc599a` | `tests/test_review_gui_e2e.py` (5 tests) + `scripts/prospectus_review_gui_smoke.py`; real-data run on COPIES of 01, 13, 16, 33; originals' hashes identical before/after; GUI vs sheet ledgers differ only in `via` and `entry_id`, same corrected candidate (Task 4 comparison) on 16 and 01 | Task 11 |
| `1f157fa`..`61d251d` (M1-M7) | page text says a prerequisite **No** holds back content review; materialise lists an accepted prerequisite it did not stamp in `report["skipped"]`; GUI blank test uses `clean_str`; bare-number refusal for all digit scripts; stronger e2e equivalence test; docstring fixes | Independent review of Tasks 10+11: **no High**; fixed. No second re-check needed (rule: only for High). |

### NOT finished (in order)
1. **Step 5, integration branch (not started).** Create `integration/gui-0710` from `dev` in a new worktree, e.g. `git -C ...\Bintanong-wt\gui worktree add C:\Users\Hawksprey\source\repos\Bintanong-wt\integration-gui -b integration/gui-0710 dev`. Merge `feat/prospectus-review-gui` with `--no-ff` (message with NO trailer). If `uv.lock` conflicts: resolve `pyproject.toml` first, then `uv lock`; never hand-merge the lock. Re-run: full suite (expect 1259 + 6 skipped), web `-k review_gui` (266), self-test 80/80, the 44-input comparer (`scripts\prospectus_course_compare.py --base-ref 5c34fd7 --status-report`, base worktree outside the repo and removed after; expect 44/44 identical), B2 triage counts (mixed 21 / warnings_only 3 / broken 19 / clean 1; `title_from_pdf` 67; `strip_banner` 0; `unclaimed_code` 316; `banner_leak` 3; scripts in `...\scratch\b2_1_banner_evidence_2026-10-06\`), read-only `check_against` on trial sheets 01, 16, 33 (0 errors), `git diff --check`, and 0 `Co-Authored-By`.
2. **Step 6:** report the integration tip + every gate number to the owner and ask before fast-forwarding dev. Update the status file (section 3 GUI row, section 8) afterwards.
3. Still open for the **owner** (not code): Task 12 trial review; Task 13 go/no-go.
4. Not done in Task 11: **browser pass and Lighthouse/keyboard walk** (plan Task 11 steps 6-7). No browser run of the page has happened yet; do it before or during the owner's trial.

### Owner decisions waiting (do not decide them for the owner)
- `content_review_state` counts only audit-listed unclaimed codes, so on prospectus 13 it reaches `reviewed` while 59 PDF-found unclaimed questions stay open (pre-existing since B2 `42c60b1`; the sheet path behaves the same).
- A prerequisite **No** (`unresolved`) keeps content review at `partially_reviewed` (B2 test `test_g5_...` demands it). Chosen as the strict reading.
- First question takes ~11 s (torch import when the Docling JSON loads), plan expected 1 s (not a gate).
- Trial candidates on disk predate Phase C (no `prerequisite_state`), so the GUI asks no prerequisite question for them; materialise still adds states. Re-extract from cached Docling JSON for a real trial (done under scratch for BSBA-HRM: 23 prerequisite questions).
- Suspicions left alone: `_next_after` jumps to the queue head after answering a decided question; a hand-edited payload `source_verification` is echoed verbatim; `--json-out` newline CRLF on Windows.

## STEP 0: Read these before any work (skills, roles, context)

Codex cannot invoke Claude skills or spawn Claude subagents, but every one of them is a plain Markdown file. Read the files below and follow them as written. Re-read the role file each time you switch roles.

### A. Project context (read once per session)

| File | Why |
|---|---|
| `C:\Users\Hawksprey\.claude\projects\c--Users-Hawksprey-source-repos-Bintanong\memory\MEMORY.md` and every `.md` file it links (`ocr-user-review-rules.md`, `resume-point-2026-10-05.md`, `bintanong-source-docs.md`) | The user's standing decisions and rules. They override defaults. |
| `C:\Users\Hawksprey\source\repos\Bintanong\plans\master_implementation_plan_original_long.md` | The master plan. Read §1, §4, §7 (Phase 2) and §11.4 (decision semantics). |
| `C:\Users\Hawksprey\source\repos\Bintanong\Context\bintanong_full_runtime_routing_architecture.png` | The runtime architecture: router, then RAG / Hybrid / Symbolic, then validation. |
| `C:\Users\Hawksprey\source\repos\Bintanong\Context\bintanong_thesis_for_context.pdf` | The thesis, for scope, privacy and stack. Read it only when a decision needs it. pdftoppm is not installed; extract text with pypdfium2 from `backend\.venv`. |
| `C:\Users\Hawksprey\source\repos\Bintanong\plans\INDEX.md` | The formal phase ledger. Phase 0 is done, and Phase 1 is the next permitted phase. The prospectus work runs parallel to it. |
| In the worktree you work in: `plans/2026-10-03-prospectus-extractor-package-split.md` (the **cross-phase rules**) and `plans/plan_current_progress/extractor_split_progress.md` | The rules every phase follows, and the record of what has been done. |
| The plan for your task, inside the worktree | e.g. `plans/2026-10-03-prospectus-phase-d-safe-cache.md` or `plans/2026-10-05-prospectus-review-gui.md`. |

### B. Skills to follow (read the SKILL.md, then obey it)

Base path: `S=C:\Users\Hawksprey\.claude\plugins\cache\claude-plugins-official\superpowers\5.1.0\skills`

| When | Skill file |
|---|---|
| Every code change | `S\test-driven-development\SKILL.md`. Write the test, show it failing, write the code, show it passing. |
| Before saying anything is done | `S\verification-before-completion\SKILL.md`. Run the commands and quote their output. |
| A bug or a failing test you don't understand | `S\systematic-debugging\SKILL.md`. Find the root cause before fixing. |
| Running a multi-task plan | `S\executing-plans\SKILL.md` and `S\subagent-driven-development\SKILL.md` (implementer, then spec review, then quality review, per batch). |
| Asking for a review / acting on one | `S\requesting-code-review\SKILL.md` / `S\receiving-code-review\SKILL.md`. Verify every finding before fixing it, and push back when a finding is wrong. |
| Writing a new plan (e.g. Phase 1) | `S\writing-plans\SKILL.md` |
| Finishing a branch | `S\finishing-a-development-branch\SKILL.md`. Do not merge or push; that is up to the user. |
| Starting or finishing a **formal** master-plan phase (Phase 1 onward) | `C:\Users\Hawksprey\source\repos\Bintanong\.agents\skills\bintanong-phase-handoff\SKILL.md` and its `references/artifact-contract.md`. Run `scripts/phase_state.py inspect --repo .` from the main repo; inspecting is read-only. |
| Supabase or Postgres work (Phase 4) | `C:\Users\Hawksprey\source\repos\Bintanong\.agents\skills\supabase\SKILL.md` and `...\supabase-postgres-best-practices\SKILL.md` |

### C. Subagent roles (act them out as separate Codex runs)

| Role | Definition file | How to run it with Codex |
|---|---|---|
| Implementer | `C:\Users\Hawksprey\source\repos\Bintanong\.claude\agents\extractor-implementer.md` plus `S\subagent-driven-development\implementer-prompt.md` | `codex -s workspace-write` in the worktree (see the commands below). |
| Spec reviewer | `C:\Users\Hawksprey\source\repos\Bintanong\.claude\agents\extractor-reviewer.md` plus `S\subagent-driven-development\spec-reviewer-prompt.md` | A **separate** `codex exec -s read-only` run over the committed range only. |
| Quality reviewer | the same reviewer file plus `S\subagent-driven-development\code-quality-reviewer-prompt.md` | A separate read-only run, after the spec review passes. |

The review loop: the implementer commits a batch, a read-only reviewer reports `file:line` plus a reproducer and says NONE when there are no findings, the implementer fixes, and the reviewer re-checks. Repeat until NONE. If the same area fails three times, fix the root cause instead of adding another patch.

Never let the implementer review its own work in the same run.

## HANDOFF NOW (2026-10-06, Claude usage at 94%; all Claude agents stopped)

Start here. Each worktree is self-contained. Verify each tip with `git -C <wt> log -1` first.

1. **phase-d** (tip `641523d`, tree clean)
   - Already done: merge `aa95d04` (B2 2414252 into D); Task 8 (`2e08be8`, 44 inputs identical); Task 9 (`641523d`, failure-injection run).
   - **Next: fix review findings F1–F6 and S1, S2, S4**, test first. The full text is in the section "Phase D review fixes" below. Then do Task 10 (docs, a Codex read-only gate, hand-off).
2. **gui** (tip `ffe0a10`; **uncommitted Task 9 work:** `backend/bintanong_tools/prospectus_review.py`, `prospectus_review_gui/__main__.py`, `prospectus_review_gui/cli.py`, `tests/test_review_gui_cli.py`)
   - Tasks 1–8 are committed: 7 = `11a08dd` session/API, 8 = `ffe0a10` page.
   - **Next:** read the uncommitted files, finish Task 9 test first (show red, then green), and commit.
   - Then run a read-only review of `b00867f..HEAD`: the batch 1 fixes, plus Tasks 6–9.
   - Then merge phase-d into gui (for Phase C), then Task 10 and Task 11. Task 12 is the user's.
   - The web tests need the throwaway venv: `$env:UV_PROJECT_ENVIRONMENT="$env:TEMP\gui-review-venv"`, then `uv sync --locked --extra review --extra dev --extra tools` from `backend`.
3. Then **Phase E** (`plans/2026-10-03-prospectus-phase-e-rag-provenance.md`, schema v3.3) on a new worktree from the phase-d tip. Then Phase F, then OCR integration.
4. Then master Phase 1 together with Phase 2 prep (follow `.agents/skills/bintanong-phase-handoff` in the main repo).

### Phase D review fixes (from the reviewer, 2026-10-06)

- **F1 (medium).** The cache pair (`_docling.json` and its meta) is published first and is not in the manifest. A later publish failure leaves the old set "verified" while the raw JSON belongs to the new PDF.
  - Publish the cache pair after the main JSON and before `_publish.json`.
  - Record its hashes in the manifest under a separate key, and have `verify_published` check them. Stale removal must never delete the cache.
  - Add a parametrised test that fails each publish step: the result must be either the old set verifying with matching raw JSON, or nothing verifying.
  - Record this as a deviation from the plan's publish order.
- **F2.** `batch.py:72/91` matches `failed` against every part of the absolute path, case-insensitively, so inputs get dropped silently.
  - Check only `path.relative_to(root).parts[:-1]`.
  - Skip only our own diagnostics folder (one that contains `<base>/failure.json`).
- **F3.** The PDF is hashed twice or three times per run (`pipeline.py:313`, `loader.py:402`, `verify_pdf`). Hash it once and pass the digest through. If a later read sees different bytes, raise.
- **F4.** `batch_manifest.json` (`batch.py:159`) is written CRLF on Windows; write it LF. Decision: `_review.csv` is LF too (`lineterminator="\n"`, `views.py:48`). Make the LF tests check bytes, so they can fail on any OS.
- **F5.** The Task 6 progress wording is wrong: there are 14 tests, and the real red count should be stated.
- **F6.** Add `identity.bytes_sha256` and build `file_sha256` on it. `loader.py:358/447` must use it.
- **S1.** Shorten the staging and `mkstemp` prefixes so the longest real PDF name ("BS Computer Science_for BOR approval _rev02_v7_6 August 2025 (2).pdf") stays under 260 characters at the default output root. Add a worst-case path-length test.
- **S2.** `run_key` does not cover `source`, `approved_scope`, `review_entries` or `repair_provider`. Either fold them in, or refuse to skip when any is set.
- **S4.** The `tui.py:201` prompt is stale. Fix the text; add a force toggle if it is cheap.
- Also drop the always-true `or "unchanged" in reason` from the skip test.
- Reproducers: `C:\Users\HAWKSP~2\AppData\Local\Temp\claude\c--Users-Hawksprey-source-repos-Bintanong\d3aa6e4b-5be4-4d53-8b8c-e7211a2f99cb\scratchpad\` (`repro.py`, `toctou.py`, `crlf.py`, `paths_len.py`).
- Gates after the fixes: the full suite (621+ at f63cdd3), the self-test (80/80), the 44-input comparer (`--base-ref 641523d`, identical), the B2 triage counts, and the trial-sheet check.

### Exact prompts for the Codex VS Code extension

**Settings:** model **GPT-6.1 Sol** (confirmed working by the user on 2026-10-06), mode **Agent**.

- Approve git commits when asked. A worktree commit writes into the main repo's `.git` folder.
- Approve `uv lock` / `uv sync` network access when asked.
- Open the worktree folder named in each prompt as the VS Code workspace, or start the prompt from it.

**Recommended reasoning effort:**

| Job | Effort | Why |
|---|---|---|
| Phase D fixes F1–F3 and S2 (publish order, path filter, single hash, run_key) | **high** | Concurrency, crash-consistency and identity logic, where subtle mistakes slip through. |
| Phase D F4–F6, S1, S4, docs (LF, wording, digest helper, path length, TUI text) | **medium** | Mechanical, and the steps are already spelled out. |
| GUI Task 9 (finish the CLI), Task 10, Task 11 | **medium** (Task 10: **high**) | Task 10 touches Phase C prerequisite states and the decision log. |
| Any read-only review (spec or quality) | **high** | Reviews must hunt for non-obvious bypasses. |
| Phase E implementation | **high** | Provenance and chunk-ID correctness. |
| Writing a new plan (Phase 1) | **high** | |
| Re-running gates or the triage, or updating this log | **low** | |

**Prompt 1: Phase D review fixes** (workspace `C:\Users\Hawksprey\source\repos\Bintanong-wt\phase-d`, effort high)

```
Read C:\Users\Hawksprey\source\repos\Bintanong-wt\CODEX_PICKUP.md completely. Do STEP 0 first: read every context file, skill file and role file it lists, and follow them. Then act as the implementer and do HANDOFF item 1 in the worktree C:\Users\Hawksprey\source\repos\Bintanong-wt\phase-d. Fix the "Phase D review fixes" (F1-F6, S1, S2, S4) test first, showing red then green for each. Commit in logical groups, staging explicit paths and adding the trailer. Run every gate the log lists. Update the progress file and this log's HANDOFF section with the new tip. Stop before Task 10 and report the commits, the red/green evidence, the suite count and the comparer result. Never push, never merge into dev, never touch C:\Users\Hawksprey\source\repos\Bintanong.
```

**Prompt 2: review of the Phase D fixes** (new chat, same workspace, effort high, read-only: tell it not to edit)

```
Read C:\Users\Hawksprey\source\repos\Bintanong-wt\CODEX_PICKUP.md STEP 0 and the reviewer role files in section C. Act as the spec reviewer, then as the quality reviewer. This is a read-only review: do not edit, stage or commit anything. Review the committed range 641523d..HEAD in C:\Users\Hawksprey\source\repos\Bintanong-wt\phase-d against the "Phase D review fixes" list and plans/2026-10-03-prospectus-phase-d-safe-cache.md. Run tests with --basetemp outside the repo. Report each finding as file:line, a reproducer and a severity. Keep confirmed findings separate from suspicions, and say NONE explicitly if there are none.
```

Repeat prompt 1 with "fix these review findings: <paste>" until prompt 2 returns NONE. Then use this prompt: "Do Phase D Task 10 from the plan, as the implementer, following CODEX_PICKUP.md STEP 0."

**Prompt 3: GUI Task 9 and its review** (workspace `C:\Users\Hawksprey\source\repos\Bintanong-wt\gui`, effort medium)

```
Read C:\Users\Hawksprey\source\repos\Bintanong-wt\CODEX_PICKUP.md completely. Do STEP 0 first: read every context file, skill file and role file it lists, and follow them. Then act as the implementer and do HANDOFF item 2 in C:\Users\Hawksprey\source\repos\Bintanong-wt\gui. Read the four uncommitted Task 9 files first, keep what is correct, and finish Task 9 of plans/2026-10-05-prospectus-review-gui.md test first (show red, then green), then commit. Use the throwaway venv described in the log for the web tests, and never sync into the main venv. Update the progress file and this log's HANDOFF section. Stop after Task 9 and report the commit, the evidence and both suite counts.
```

Then run prompt 2's wording against `b00867f..HEAD` in the gui worktree, using the GUI plan. That reviews the batch 1 fixes and Tasks 6–9.

**Prompt 4: next phase, Phase E** (once Phase D's review returns NONE and Task 10 is done; effort high)

```
Read C:\Users\Hawksprey\source\repos\Bintanong-wt\CODEX_PICKUP.md and do STEP 0. Create a worktree C:\Users\Hawksprey\source\repos\Bintanong-wt\phase-e on a new branch feature/prospectus-phase-e-rag-provenance from the phase-d tip (run git worktree add from the main repo; do not check anything out in the main repo). Then implement plans/2026-10-03-prospectus-phase-e-rag-provenance.md batch by batch as the implementer (Tasks 1-4 first), test first, schema v3.3, taking the recommended option for every decision. Stop after each batch for a separate review run. Keep this log updated.
```

### (Old) CLI commands, kept for reference only

```powershell
$scr='E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch'; $git='C:\Users\Hawksprey\source\repos\Bintanong\.git'
codex -m gpt-6-sol -s workspace-write -C 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase-d' --add-dir $git --add-dir $scr
#   prompt: "Read C:\Users\Hawksprey\source\repos\Bintanong-wt\CODEX_PICKUP.md. Do STEP 0 first (read the context, skills and role files it lists), then do HANDOFF item 1 as the implementer."
codex -m gpt-6-sol -s workspace-write -C 'C:\Users\Hawksprey\source\repos\Bintanong-wt\gui' --add-dir $git --add-dir $scr
#   prompt: "Read C:\Users\Hawksprey\source\repos\Bintanong-wt\CODEX_PICKUP.md. Do STEP 0 first, then do HANDOFF item 2 as the implementer."
# Reviewer run (separate, read-only, after an implementer batch):
codex exec -m gpt-6-sol -s read-only -C 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase-d' "Read C:\Users\Hawksprey\source\repos\Bintanong-wt\CODEX_PICKUP.md STEP 0, act as the spec reviewer (role file C), and review the range <base>..<tip>. Report file:line plus a reproducer, and say NONE explicitly if there are no findings."
```

- `--add-dir` for the main `.git` is needed because worktree commits write there.
- Network may be needed for `uv lock` and `uv sync`. If the sandbox blocks it, run those two commands yourself.
- Keep the table below updated.

Read this file first. It lets Codex continue the work when Claude's usage is near its limit (90–95%), or when the Claude agents are rate-limited.

Last updated: 2026-10-06 19:30 (Asia/Manila), by the Claude orchestrator.

## How to start Codex

```powershell
codex -m gpt-6-sol    # works with this machine's ChatGPT login (verified 2026-10-04..06)
```

- **Use GPT-6.1 Sol.** The user confirmed on 2026-10-06 that it works in the Codex VS Code extension. Earlier CLI runs with a ChatGPT login refused it, so `gpt-6-sol` is the fallback if it errors.
- For small, mechanical tasks, `gpt-6-luna` is the cheaper option.
- OpenAI's current guidance (searched 2026-10-06) is GPT-6.1 Sol for complex coding and agentic work where the account has access, and GPT-6 Luna for focused, repeatable tasks. See https://developers.openai.com/codex/models and https://aidenapp.org/best-codex-model. With a ChatGPT login on this machine, 6.1 Sol is refused, so `gpt-6-sol` is the best model that works here.
- Use Codex only when Claude usage is at 90–95% or the Claude agents are rate-limited. Otherwise Claude subagents do the work and Codex reviews (read-only).
- Run each job inside the worktree it changes, with `--sandbox workspace-write`. Use `--sandbox read-only` for reviews.

## Hard rules (the user's standing instructions)

- `C:\Users\Hawksprey\source\repos\Bintanong` is the user's main checkout, on `dev`. **Never edit it, never `git checkout` there.** All work happens in worktrees under `C:\Users\Hawksprey\source\repos\Bintanong-wt\`.
- Never push. Never merge into `dev`. The merges wait on the user's trial review of `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\review_trial_2026-10-04\`.
- Test first: write the test, run it and see it fail, fix the code, run it and see it pass. Then run the full suite. One commit per logical fix.
- Stage files by explicit path only. Never `git add -A` or `.`. Never stage `.gitignore` or `plans/CODEX_HANDOFF_prospectus_extractor_phase2_2026-09-26.md`.
- **No AI attribution in commits (user decision, 2026-10-07).** Do NOT add `Co-Authored-By:` lines, "Generated with ..." lines, or any other Claude/Codex/AI trailer to commit messages or PR text. This overrides every plan, skill and agent file that says to add one (older plans still say "add the trailer"; ignore that).
- Use PowerShell. Git Bash fails to fork on this machine.
- Never write generated outputs, PDFs or images into a repo. Scratch output goes under `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\<topic>_<date>\`.
- Code must run on Windows, Linux and macOS: use pathlib, LF output, no shell-specific paths.
- Strictness rule (the user's): when a case is ambiguous, refuse rather than guess. Make no proposal, mark the item non-executable, or flag it for a human. Never drop an item silently.

## Running tests in a worktree

```powershell
$py = 'C:\Users\Hawksprey\source\repos\Bintanong\backend\.venv\Scripts\python.exe'
& $py -m pytest -q tests --ignore=tests/test_api_probes.py --ignore=tests/test_embedding_service.py -p no:cacheprovider
# Only if the sandbox blocks %TEMP%: add --basetemp "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\pytest_tmp"
# (and --add-dir that folder for Codex). NEVER point --basetemp inside the worktree: the fixer CLI's outside-Git
# guard refuses to write there, and 11 fixer CLI/e2e tests then fail.
& $py backend\bintanong_tools\bintanong_jsonifer_prolog\bintanong_prospectus_jsonifier.py --self-test   # must print 80/80
```

- The package is not installed in that venv, so running from the worktree root imports the worktree's own code.
- fastapi is missing from it, which is why those two test files are ignored.
- The baseline on b2 at f0e0a3d is 321 passed + 13 subtests.
- SWI-Prolog is at `C:\Program Files\swipl\bin\swipl.exe`.

Real-data gates:
- 44-input comparer: `& $py scripts\prospectus_course_compare.py --base-ref <ref> --status-report ...`. Read `--help`. The inputs are the cached Docling JSON in `E:\...\Bintanong dataset dump\docling_jsonified_output\task2b_standing_isolated_2026-09-29\` (`isolated_manifest.json`).
- B2 triage counts must stay at: health mixed 21 / warnings_only 3 / broken 19 / clean 1; `title_from_pdf` 67; `strip_banner` 0; flags `unclaimed_code` 316, `banner_leak` 3. The triage scripts are in `E:\...\scratch\b2_rereview_2026-10-04\` (`triage_fixes.py`, `cmp3.py`).
- Phase C prerequisite-state counts must stay at: blank_unreviewed 1005, resolved 689, unresolved_reference 253, standing_condition 59, unreadable 20, alternative_or_exception 3, stated_none 2.
- Trial sheets: a read-only `check_against` on 01, 16 and 33 in the trial folder must give 0 errors.

## Worktrees and state

| Worktree | Branch | Tip | State |
|---|---|---|---|
| b2 | feat/prospectus-phase-b2-section-fixer | 2414252 | **DONE.** The strip-evidence rule is final (12f0509): a source cell counts only if it is a code or title role cell, sits on this row alone, is in no other course's provenance, matches the whole remainder exactly, and carries no banner wording in any case. PDF evidence needs an anchored span printed once. 329 tests. Triage unchanged. The review loop has stopped (0 real strip proposals). **Next: merge 2414252 into phase-d** (after the Phase D fixes land), and later into gui. |
| task13 | feat/prospectus-b2-banner-split | db16b26 | Done. Merge only after the trial review. |
| phase-c | feat/prospectus-phase-c-status-separation | 81ac0f1 | Complete. The last Codex gate found **NONE**. |
| phase-d | feat/prospectus-phase-d-safe-cache | 1460536 (+ uncommitted `publish.py`, `tests/test_prospectus_publish.py` from Task 5, half done) | Contains merge 48ea309 (B2 d7860f4 into C) and Phase D Tasks 1–4. **Five open Codex findings (D-1..D-5 below).** Tasks 5–10 remain. |
| gui | feat/prospectus-review-gui | 49162c7 | GUI plan Tasks 1, 2, 2A, 3, 4, 5 done. Task 6 next. The batch 1 review (Tasks 1–4) has not been done yet. Task 10 needs the B2+C base: merge `feat/prospectus-phase-d-safe-cache` or the C tip in first. |
| ocr | feat/ocr-measurement-harness | 5467f51 | Done. Docling pinned at 2.133.0. GPU fixed (HEURISTIC cuDNN plus a one-crop warm-up). Docker CPU and GPU images bake in the models and run offline. Remaining tasks are in its plan (Tasks 4b, 4c, 5–9). |
| gui-plan | docs/prospectus-review-gui-plan | 4de3829 | Plan only, already merged into `gui`. |

Plans (inside the worktrees):
- `plans/2026-10-03-prospectus-phase-d-safe-cache.md`
- `plans/2026-10-05-prospectus-review-gui.md`
- `plans/2026-10-03-prospectus-phase-e-rag-provenance.md`
- `plans/2026-10-03-prospectus-phase-f-tools-cli.md`
- `plans/2026-10-04-prospectus-ocr-measurement.md`

The cross-phase rules are in `plans/2026-10-03-prospectus-extractor-package-split.md`. Progress is tracked in `plans/plan_current_progress/extractor_split_progress.md`, one section per phase. Update it with every commit.

## Open work queue (in order)

### B2-1: DONE (f0e0a3d, then root cause 12f0509 / 2414252). Kept for history.

- `fixes.py:124/132` collects every provenance cell as evidence and excludes only cells whose text equals the field value. A shared section-banner cell (e.g. `t0-c9` = `FIRST SEMESTER Discrete Structures 1 1`) can therefore authorise a strip for another course (CS 2 → `Structures 1`).
- The full reproducer is in `%TEMP%\codex-final7-b2.txt`.
- Fix: source-cell evidence must come only from this course's OWN row cells that are not banner cells (use the verifier's `own_role_cells`). A cell carrying any banner phrase never counts.
- Commit: `fix: source-cell strip evidence comes only from this course's own non-banner cells`.
- Afterwards, merge the new b2 tip into `phase-d` (and later into `gui`).

### D-1..D-5 (worktree phase-d): cache identity defects

The full report is in `%TEMP%\codex-phased-b1.txt`.

1. `docling_env.py:215`: shared converters are keyed only by device and backend, so a converter built under one setting is reused after a settings change. Key them by the full settings identity.
2. `loader.py:302`: every writer uses the same `<target>.tmp`. Use a unique temp name in the same directory, then `os.replace`. Handle a Windows replace failure (retry, then a clean error).
3. `loader.py:330/375`: the cache is hashed, then opened again, so the check and the load can see different files. Read the bytes once, verify the digest on those bytes, and parse those same bytes.
4. `loader.py:328`: the metadata's `pdf_sha256` and `conversion_settings` must match the identity, or the entry is a miss.
5. `prospectus.py:19`: `ProvisionalSource.verify_pdf` uses `hashlib.file_digest`. Route it through `identity.file_sha256`, the single hash owner.

Also (suspicion): a corrupt JSON whose digest matches should trigger a reconvert (cache miss), not raise.

- Do not touch or commit the half-done Task 5 files (`publish.py`, `tests/test_prospectus_publish.py`) unless you are doing Task 5 itself.
- Then continue the Phase D plan from Task 5 to Task 10.

### GUI (worktree gui)

- Review batch 1 (`31a0d39..ae4a335`) read-only before Task 7.
- Then Tasks 6, 7, 8, 9 and 11.
- Task 7 needs FastAPI. Add the `review` extra (same FastAPI/uvicorn/httpx pins as the `api` extra) with `uv lock` only. Test in a throwaway venv: `$env:UV_PROJECT_ENVIRONMENT="$env:TEMP\gui-venv"; uv sync --locked --extra review --extra dev`. Never sync into the main venv.
- Task 10 waits until the B2+C base is merged in.
- Task 12 is the user's own trial.

### After those: Phase E, then Phase F, then OCR integration

These follow their committed plans. Phase E bases on Phase D's tip. Schema versions: C v3.1, D v3.2, E v3.3.

### Later, after the prospectus workstream (user's order)

Master Phase 1 (source manifest + typed contracts) together with Phase 2 prep. Follow `.agents/skills/bintanong-phase-handoff` (in the main repo).

## Review loop that has worked

1. The implementer fixes the issue with a test-first commit.
2. A narrow Codex review, read-only, in that worktree, covering just the new range. Ask for "file:line plus a reproducer, confirmed findings separate from suspicions, say NONE explicitly".
3. Repeat until the review returns NONE.
4. If the same area keeps failing, fix the root cause rather than adding another patch.

## Log of Codex jobs (append here)

| When | Worktree | Job | Result file |
|---|---|---|---|
| 2026-10-06 | phase-c | final gate 5 | `%TEMP%\codex-final5-phasec.txt`: NONE |
| 2026-10-06 | b2 | final gate 7 | `%TEMP%\codex-final7-b2.txt`: B2-1 |
| 2026-10-06 | phase-d | batch 1 review | `%TEMP%\codex-phased-b1.txt`: D-1..D-5 |
