# Current progress

Updated 30 October 2026 (machine local date). Worktree p12 / `p12-evaluation-harness`.
Phase 12 research/software evaluation write-up complete with disclosures; no active numbered phase.
Post-phase test-suite audit authorized. Phase 13 deployment remains cancelled by owner.
Last full progress snapshot before condensation: `3ad52e5`; recover prior detail with `git show`.

## Latest change: test-suite audit

[Plan](../2026-10-30-test-suite-audit-plan.md) · [Execution checkpoint/results](../2026-10-30-test-suite-audit-results.md).
Tasks 1–2 complete: baseline7,365 collected; full suite7,357pass/6skip/2xfail/1,608subtests, four exits0.
Local `supabase_db_Bintanong` started and healthy. Gemma not needed; existing model container untouched.
Inherited roster reconciled:105 collecting files /4,646 tests created by Hawksprey420 (current file incarnations).
Owner approved coverage7.17.0 + pytest-cov7.1.0 in the evaluation venv only; installed, no lock/dependency edits.
Per-test report:2,926 subset candidates /707 zero-production records; neither alone proves redundancy.
Baseline Python coverage13,893/23,545 statements and4,319/9,284 branches (`backend/` + `scripts/`).

Task 3 complete: removed one identical-body prospectus ledger test, retained its descriptive compatibility twin;
same module globals and all measured lines/arcs covered by retained test. Renamed zero-test evaluation helper
to `evaluation_fixtures.py`; five imports updated; builder AST unchanged. Collection7,364 (exactly one removed).
Focused290pass/1skip. Fresh inherited coverage4,639pass/6skip/13subtests; **no lost lines or branches**,
same denominators and production hashes. Evidence/temp/scripts remain under ignored workspace audit-evidence.

Owner changed the verification schedule: **focused checks during audit; one full suite at the end**.
Stopped intermediate quickwins full-suite run after one green batch; partial logs are not full-suite evidence.
Task 4 contracts consolidation next. No tooling retired; task 6 requires the owner's decision.
No push, production behavior changes, additional installs or dependency/model/lock changes.

## Research release and accuracy follow-ups

[Phase 12 handoff](../phase-12-handoff.md) · [Frozen report](../../docs/evaluation/phase12-evaluation-report.md) ·
[Activation results](../2026-10-30-hosted-560-activation-results.md).
Hosted research release `p12-research-faqsplit-20261030`:560 chunks/vectors,39 curriculum links;
corrected78 superseded and retained for rollback. Bound artifacts/source states unchanged.
Backend :8021 uses the ignored hosted-560 config; frontend :3216; model :18088. Servers are owner-managed.
Do not use the old corrected78/local-document config after activation or repeat staging/activation.

Frozen main v2:38/50; original C40/50, rerun39/50; A strict3/50, content8/50. Participant research,
independent scoring, institutional validation and several planned metrics remain unavailable/disclosed.
These results are separate from subsequent development regressions; no student-visible latency SLA established.

[Hosted-parity results](../2026-10-30-hosted-regression-results.md): owner-run `-hosted2` on63b9653,
47/50, no exceptions, versus local44/50 (three gains/no losses). Both documents and curricula used hosted paths.
Remaining:summer-load-en (Dean exception omitted), grad-residence-taglish and disc-uniform-taglish (model choices).
Honors introduced_disjunction guard retained by owner; INC now answers exact printed quotations with limitation
and referral. Prior repairs/replays and exact decisions remain in `3ad52e5`, dated results and
[accuracy handoff](../2026-10-30-eight-failures-handoff.md). No new live benchmark runs during this audit.

## Boundaries and next action

Preserve undergraduate scope, source gaps, privacy, unknown-versus-unmet, printed terms and release guards.
F04 stays held; research activation is not school approval or public deployment.
Next: commit verified task 3 quick wins, then consolidate contracts (task 4), review other candidates (task 5),
obtain tooling decision (task 6), and run final full-suite/coverage verification (task 7).
