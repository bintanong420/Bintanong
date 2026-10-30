# Current progress

Updated 30 October 2026 (machine local date). Worktree p12 / `p12-evaluation-harness`.
Phase 12 research/software write-up complete with disclosures; no active numbered implementation phase.
Post-phase test-suite audit tasks 1–7 complete; Claude review passed (nits only). Phase 13 remains cancelled.
Last expanded progress snapshot before condensation: `db643c0`; recover prior history with `git show`.

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
Owner restarts :8021 to serve the new HEAD.
Honors guard kept by owner; INC now answers printed quotes with limitation/referral. Prior repair history remains
in `db643c0`, dated results and [accuracy handoff](../2026-10-30-eight-failures-handoff.md).
No live model benchmark or student-visible latency claim from this audit.

## Boundaries and next action

Preserve undergraduate scope, source gaps, privacy, unknown-versus-unmet, printed terms and release guards.
F04 stays held; research activation is not institutional approval or public deployment.
Next: owner decides on cosmetic nits; ingestion tools kept, opt-in tests. No push/merge. Keep branch/worktree; no merge/push or Phase 13 advancement.
