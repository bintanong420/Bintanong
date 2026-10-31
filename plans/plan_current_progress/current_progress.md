# Current progress

Updated 31 October 2026 (machine local date). Worktree p12 / `p12-evaluation-harness`.
Phase 12 research/software write-up complete with disclosures; no active numbered implementation phase.
Post-phase test-suite audit tasks 1–7 complete; Claude review passed (nits only). Phase 13 remains cancelled.
Last expanded progress snapshot before condensation: `db643c0`; recover prior history with `git show`.

## Teammate UI integration (31 Oct)

Owner asked to integrate the teammate's enhanced UI (`worktrees/Bintanong/bintanong-teammate-enhanced-ui`, an
unversioned mock-data Next app). Its design was ported onto the live workspace; the folder itself is unchanged.
Ported: mascot logo/favicon, orange welcome backdrop, Gemini-style sidebar, "Hi, I'm Bintanong" welcome with
pills above a pill composer, user/assistant avatars and bubbles, public `/about` page. Dark mode kept (the
teammate build is light-only; mascot gets a light backing). Assets resized: logo 190 KB -> 13 KB, photo 2.5 MB -> 215 KB.
Not ported: mock chat/multi-session data and sidebar search (one server session per browser), timestamps,
header account avatar, dependency/config changes, Tailwind rewrite. Live starters, sources, clarification,
files, sign-in and 44 px targets kept. Landing/login keep their layout and heading; they only gain the mascot.
About copy corrected: dropped "Graduation Tracking" and "Curriculum Flowchart" (no such capability; thesis
physical 17-18 consulted). Open: the binturong name-origin line is the teammate's; no repo/thesis source confirms it.
Verified: tsc clean; 66/66 unit; production build; browser suite (isolated synthetic fixture on :3219, evidence in
`audit-evidence/p12-teammate-ui-20261031/`) 17 pass / 10 fail on the last full run. Baseline on unchanged code was
17 / 9 of 26; the same nine fail after (older sign-out expectations, missing PDF fixture path; not investigated).
The tenth (`live clarification`) and an earlier `Stop` failure are intermittent: Send still disabled after a
page fill under load; each passed 3/3 alone. Real pipeline via :3216 -> :8021: CC 5/L returned CC 3/L and CC 4/L
in 19 s, an enrollment question returned one source, both themes/phones rendered with no page errors.

## New-machine handoff run (31 Oct, 32 GB machine, HEAD `7327ade`)

Following the [current handoff](../2026-10-30-eight-failures-handoff.md). Environment and logs:
`audit-evidence/p12-env-20261031/` (venv from frozen lock exports; portable Node 24.21.0, system Node stays 22).
Step 1 passed: backend `app constructed` in 145 s; browser guest question answered in 17 s with one source.
Step 2 passed apart from one known guard: default 5,604 pass / 1 fail; `--include-ingestion` 7,399 pass / 1 skip
/ 2 xfail / 1 fail. The failure is `test_scaffold_contract` rejecting uncommitted `.env.example` credentials.
Collected 5,607, not the handoff's ~5,576 (deselected 1,796 matches); the extra 31 are not yet explained.
Steps 3-6 on hosted, single development runs, 0 exceptions in every set:
97-case 88/97 twice (general 26/33, CoS 48/48, other 14/16; baseline 77/97; no pass or status flips, 3 texts differ);
50-case 50/50 twice (baseline 49/50); 91-case gate 88/91 (new hosted baseline). Median warm pipeline 10-15 s.
97 failures: section, honors, grad residence, absence, good-moral, certification fee, transfer fee, two BSHM.
91 failures: library card, certification fee, overdue fee (all `insufficient_evidence`). Honors stays a disclosed
limitation by the 30 Oct owner choice unless its answer text shows otherwise. Run folders: `run-7327ade1-*`.
A first 50-case repeat stopped before any question on a hosted 500 statement timeout while loading curricula
(`-full2`, no observation); the `-full2b` retry completed. Backend startup makes the same read.

Setup findings the handoff omits:
- `api` and `embedding` conflict in one `uv sync`; export each from the frozen lock (76 pins, no clash) and install.
  The default suite also needs the `tools` extra plus `jsonschema` and `opencv-python`, at lock pins.
- Eight encoder text files were LF here; verified hashes are of CRLF bytes, so startup would refuse them. Copied
  the verified bytes from a local copy; 10/10 assets match; LF originals in `encoder-lf-backup/`.
- Use `next dev -H 127.0.0.1 -p 3216`; without `-H`, Next blocks `/_next/hmr` and the page reloads repeatedly.
- System Python 3.13.12 does not match the lock (18/76), so runs use the venv. A 16 GB WSL limit is set.

Open: uncommitted `.env.example` (live hosted secrets; tracked file) and `.gitignore` await an owner decision; do
not stage them. Docker Desktop stopped by itself at 04:38:58 (cause unknown; run discarded).
Google sign-in docs use port 3215 while this setup uses 3216; guest use unaffected.

## Latest delivery: test-suite audit

[Completed plan](../2026-10-30-test-suite-audit-plan.md) · [Counts, removal proofs and results](../2026-10-30-test-suite-audit-results.md).
Overall collected: **7,365 -> 7,363**; inherited Hawksprey420 cases: **4,646 -> 4,644**.
Contracts: **25 -> 11 files**, all **2,032 cases retained**; 235 moved test functions verified against originals.
Fourteen fix-pass/survivor fragments folded into module files; shared path/ID matrices centralized.
Two removals: identical ledger compatibility duplicate, and OCR text-format case covered by a retained real
adapter test with the same oracle. Per-test line/arc subsets documented; both OCR tests catch lost-newline mutant.
Evaluation helper renamed; five imports fixed; executable builder AST unchanged.

Final test code `4ed03dc`: **7,355 passed / 6 skipped / 2 xfailed / 1,608 subtests**, four batch exits 0.
Fresh inherited run: **4,638 passed / 6 skipped / 13 subtests**, exit 0.
Coverage before/after: **14,444 / 24,492 statements; 4,631 / 9,720 branches** (`backend/`, `scripts/`, `evaluation/`).
Exact covered sets preserved globally and within every family; production Python hashes unchanged.
Root evaluation coverage corrected using original archived tests and hash-verified production code.
No negative/privacy/scope/security/source-gap/original mutation-survivor case removed.

Owner approved coverage 7.17.0 + pytest-cov 7.1.0 in the evaluation venv only; no lock/dependency edits.
Owner amended verification to focused checks during audit and one final full suite; interrupted intermediate
run is recorded separately and never claimed as full evidence. Owner kept review GUI, OCR bench and prospectus
fixer as offline ingestion tools. Their inherited families: 1,787 -> 1,785 cases, separate from runtime evidence.
No test-command/CI default changed. Local Supabase started/healthy; Gemma untouched and unnecessary here.

Fresh Codex review checked helpers/matrices and found a shared vocabulary binding that weakened checker
independence. Separate package/checker bindings restored; process-local probe RED fail -> GREEN pass, contracts
2,032 pass. Passing counts/ASTs alone do not prove binding independence. External Claude review done; see below.
Commits: `db643c0` baseline; `4e80c56` quick wins; `f071293` consolidation; `0f7849b` OCR; `4ed03dc` checker fix.
Claude review (30 Oct, read-only): all 7,363 IDs map to originals; 115 moved bodies differ only by helper
renames/module-prefix drops/equal fixture matrices; no remaining top-level rebinding. Runtime suite (187 files, no
prospectus/GUI/OCR or tool-importing tests, DB up): 4,843 pass / 2 xfail, exit 0. Nits only: 7-8 blank-line runs,
duplicate `BIND`, misnamed `_typed_chunk`/`_source_record`, alias `_chunk_adapter_reason`.
Owner (30 Oct): keep ingestion tools but out of the default suite. `tests/conftest.py` deselects prospectus/GUI/OCR
files unless `--include-ingestion` or named: default 5,576 / 7,372 collected (1,796 deselected). Selection test
RED 9 fail -> GREEN 9 pass; remaining default files 728 pass / 3 skip; with the runtime run, all 5,576 accounted.
Closure documentation follows. Raw evidence/temp/scripts remain under ignored workspace audit-evidence.
No production behavior, source corpus, dependency/model/lock changes, merge or push.

## Research release and accuracy follow-ups

[Phase 12 handoff](../phase-12-handoff.md) · [Frozen report](../../docs/evaluation/phase12-evaluation-report.md) ·
[Activation](../2026-10-30-hosted-560-activation-results.md).
Hosted research `p12-research-faqsplit-20261030`: 560 chunks/vectors, 39 curricula; corrected78 retained for rollback.
Bound artifacts/source states unchanged. Owner manages backend :8021 (hosted-560 config), frontend :3216,
model :18088. Do not repeat activation or use the old corrected78/local-document config after the switch.
Frozen main v2: 38/50. Participant research, independent scoring and institutional validation remain unavailable.
[Hosted-parity development regression](../2026-10-30-hosted-regression-results.md): 47/50 on `63b9653`, no exceptions;
separate from frozen evaluation. Remaining: summer-load-en Dean omission, grad-residence-taglish, uniform-taglish.
Student-evaluation prep (owner 30 Oct): next week, screen-shared sessions, 2 students per program, mainly College
of Sciences (prior questionnaire evidence) plus a few other colleges; priority is common queries. RAGAS later.
Checker fix: evidence-ID hex matched digit expectations; hosted/gate runners now strip IDs (47/50 and frozen 38/50
rescored unchanged). `f08712d`: omitted printed exception -> repair (RED 8 -> GREEN 8; gen/orch/API 1,014 pass;
104-draft dry run: 8 triggers, all summer load; live repair replays EN/Taglish include 12 units + Dean). A prompt-only
variant was replayed and reverted (1 gain, 3 regressions). `12b35d1`: one printed row naming the part's word
replaces an unrelated row (uniform Taglish); `ac867c6`: a selected topic whose heading names more part words wins
(graduation residence Taglish). Dry runs over 273 routing outputs: 4 and 1 triggers, all correct. Live hosted
subsets: 8/8 and 6/6 incl. all three former failures. Full 50 on `ac867c6` running (Claude, `-claude-full`).
Common-query set: `audit-evidence/p12-common-queries-20261030/` (97 cases: 33 general rewordings reusing reviewed
expectations, 48 CoS across all 6 CoS curricula, 16 from 6 other colleges); first run before any fix.
Full 50 on `ac867c6`: 49/50 (probation-tagalog withheld by style check on a verbatim printed INC sentence).
`41dfd00`: verbatim printed sentence allowed among Taglish claims; 26 non-EN live 25/26 (cheating-tagalog router
nondeterminism, raw model chose not-stated fact; not a code regression). Common set first run on `41dfd00`:
77/97 (general 20/33, CoS 43/48, other 14/16; median warm 21 s). Found: Charter host replies citing held malformed
records crashed (final_malformed_source_fidelity; regression since 28 Oct gate) -> `1468505` routes them to the
per-part quote path; live 10-case probe 6/10, no crashes. `754ee9a`: an ambiguous topic selection carries no
document topic (structured checks proceed); live 8/8 incl. all 5 CoS Taglish term listings. `48ff8d6`: owner-
approved Filipino penalty-row words (uniporme excluded; docs table + sync test) and best-row narrowing; 440-output
dry run: 4 intended changes; live discipline probe 8/8. Open: topic choices (absent, good-moral requirements,
honors wording), certification-of-grades and transfer fee, BSHM clarification. Full 97 rerun was stopped by the
host for low memory (no results); rerun the 97 and 50 on HEAD. Claude restarted :8021 on `48ff8d6` (owner-authorized).
Owner 30 Oct: test runs move to another developer's 32 GB machine; setup, runtime files and run order are in
the [current handoff](../2026-10-30-eight-failures-handoff.md).
Owner restarts :8021 to serve the new HEAD.
Honors guard kept by owner; INC now answers printed quotes with limitation/referral. Prior repair history remains
in `db643c0`, dated results and [accuracy handoff](../2026-10-30-eight-failures-handoff.md).
No live model benchmark or student-visible latency claim from this audit.

## Boundaries and next action

Preserve undergraduate scope, source gaps, privacy, unknown-versus-unmet, printed terms and release guards.
F04 stays held; research activation is not institutional approval or public deployment.
Next: owner sets the score target; then fix failures in order CoS > general > other colleges and add new common-query batches. No push/merge or Phase 13 advancement.
