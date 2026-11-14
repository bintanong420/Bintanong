---
artifact: phase-checkpoint
phase: 12
status: superseded
sequence: 8
plan: plans/phase-12-evaluation-writeup-plan.md
head_commit: 62ecb96
working_tree: closure documentation; raw evidence and configuration remain ignored
updated_at: 2026-10-29T23:40:04+08:00
---

# Phase 12 checkpoint — superseded by final handoff

## Completed Tasks

- Evaluation report, paired statistics and fixed benchmark summaries delivered.
- Hosted 560 staging/activation/readbacks passed; existing rows preserved; corrected78 retained as rollback.
- HTTP 3/3 cited answers; guest browser smoking-penalty/source-panel check passed with 0 console errors/warnings.
- Fresh report-number verification matches original outputs; protected receipt/event/snapshot hashes unchanged.
- Delivery/recovery evidence: [Phase 12 final handoff](phase-12-handoff.md),
  [activation results](2026-10-30-hosted-560-activation-results.md).

## Current Task

Complete. This checkpoint is superseded; use the final handoff. Deployment (Phase 13) cancelled by owner.

## Repository State

p12 / `p12-evaluation-harness`. `62ecb96` anchors verified activation; subsequent closure commit contains final docs.
No production code, dependencies or models changed in this continuation. .env is ignored/untracked and never staged.
Last full progress snapshot before condensation: `76d5a92`.

## Verification Evidence

- Staging exit 0, 106.11 s: 560 chunks/vectors, 39 links, selected review bound, previous rows preserved.
- Activation exit 0, 121.08 s: active new560, anon 560/39, retrieval hit; MCP confirms corrected78 superseded.
- Backend live/ready HTTP 200; construction 110.88 s; HTTP smoke 3/3 answered/cited, exit 0.
- Browser smoking penalty cites Handbook p.93; source panel works; 0 console errors/warnings.
- Fresh saved-output audit: v2 38/50; original C40, rerun39, A3/8; robustness19/26,15/26,2/4.
- Historical merged suite `a3ff208`: 7314/1608 pass, 6 skip/2 xfail; four exits 0, logs re-read.
  `48330f7` related108 pass (inherited). No full regression rerun for operational/docs-only scope.
- Final phase-state, local-link and diff validation accompany closure; exact artifacts/commands in handoff.

## Versions and Digests

Full versions, model locations, image/package/pin/config digests and review scope are in the final handoff.
Runtime package seal `954d376e3c47e55856f2e7c959f4dd9b98f5195a2fb25242807e6081e4cabb8e`.
Hosted release `p12-research-faqsplit-20261030`; authorization `research-owner-20261029`; gate composition.

## Decisions

Owner activation directive covers research use of the 560 package; 257 re-authored records carry no per-chunk
human approval. Source states unchanged. Single benchmark runs disclosed; no deployment/institutional approval.
Owner reiterated never commit .env; all staging is explicit by path.

## Known Failures or Blockers

No activation blocker. Report's 12 v2 failures, unmeasured thesis metrics, deferred PSU sign-in and unsupported
photos remain disclosed. Hosted benchmark not rerun; smoke is not accuracy parity. Initial authentication error resolved.

## Next Action

No next implementation phase. Owner/Claude may separately request hosted answer-quality validation;
Phase 13 remains cancelled even if the structural validator reports next_phase13.

## Do Not Repeat

Benchmark runs, selector replays, statistics, dev merge, local rehearsal, receipt preparation, snapshot,
applied migration, staging or activation. Preserve bound artifacts and corrected78 rollback.

## Context consulted

Master3/11/13/17/26, Phase11 handoff, undergraduate-scope policy, thesis physical17–18/39–44 via pypdfium2,
routing PNG. Scope, RAG/Symbolic/Hybrid separation and unknown-versus-unmet guards preserved.
English/Taglish replies follow owner decision; all three input languages retained. No new architectural discrepancy.
Machine local date29Oct differs from inherited30Oct records; historical names preserved.
