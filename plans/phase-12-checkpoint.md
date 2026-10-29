---
artifact: phase-checkpoint
phase: 12
status: in_progress
sequence: 4
plan: plans/phase-12-evaluation-writeup-plan.md
head_commit: 76d5a92
working_tree: docs changes for activation preflight and current state; ignored hosted config prepared
updated_at: 2026-10-29T23:13:28+08:00
---

# Phase 12 checkpoint — hosted activation preflight verified; connection missing

## Completed Tasks

- Report `36ae881`, plan/research `f2b00dc`, paired statistics and benchmark runs already delivered.
- Merge into dev `a3ff208`; dedicated p12 / `p12-evaluation-harness` exists.
- Claude: receipts prepared, local 560 rehearsal passed, hosted flow migration applied (`222d9ab`),
  hosted pin support `48330f7`; executor handoff `76d5a92` read by Codex.
- Codex: 560 runtime/bound chunk content maps identical; all seal files verify; protected evidence unchanged.
  Hosted pin/config prepared and accepted by backend config/package loader.

## Current Task

Resume [Claude's hosted activation handoff](2026-10-30-hosted-560-codex-handoff.md).
Connection prerequisite missing; no hosted writes attempted. Results recorded in
[activation status](2026-10-30-hosted-560-activation-results.md).

## Repository State

Started clean at `76d5a92` in p12 / `p12-evaluation-harness`. Current changes are documentation only;
prepared pin/config and raw evidence remain ignored. Last full progress snapshot: `76d5a92`.
Machine local date is 29 Oct; preserve inherited 30 Oct records and release identifiers unchanged.

## Verification Evidence

- Fresh read-only MCP: active corrected78, 78 chunks / 39 curriculum links; new release absent.
- `codex-preflight-result.json`: PASS, 560 identical content mappings, all sealed files verified,
  protected artifact hashes unchanged, zero hosted writes.
- Shared-venv `ResearchApiConfig.model_validate_json` + `_package`: PASS (560 chunks/vectors; hosted gate).
- Saved rehearsal: PASS, replay no-op, anon/auth 560 visibility, retrieval hit, rollback 78, rows preserved.
- Historical suite: merge `a3ff208` 7314 pass / 1608 subtests, 6 skip / 2 xfail;
  `48330f7` related 108 pass. Not rerun for this operational/docs-only preflight.

## Versions and Digests

Model unchanged: Gemma 4 E4B, llama.cpp b11723-31288c9c6; external MODELS directory only.
Hosted config seal `954d376e3c47e55856f2e7c959f4dd9b98f5195a2fb25242807e6081e4cabb8e`.
Pin/config hashes and exact artifact locations: linked activation results. Selected review scope
`17e11149b93c5f0e29fb43f29ea23d2aa87b6b4a602280fb8c53c402ce61d2a1`.

## Decisions

Owner directives in ledger authorize hosted 560 research activation and the session-pooler path;
257 re-authored records use the activation directive, with no per-chunk human approval.
No further permission needed for those steps. Deployment cancelled; institutional release held.

## Known Failures or Blockers

Owner supplied pooler host `aws-0-ap-southeast-1.pooler.supabase.com` and authorized assembling the URI.
Hosted database password missing; owner asked to add `SUPABASE_HOSTED_DB_PASSWORD` privately to p12/.env.
No stage/activate or hosted website smoke run. Benchmark failures and unmeasured metrics remain in report.

## Next Action

Once the password is added, construct `SUPABASE_HOSTED_DB_URL` with the supplied host, port 5432,
user `postgres.jyrudbiuajahsucsorco` and percent-encoded password; validate without exposing it; run logged
`hosted.py stage`, inspect exact readback, activate, then hosted-config website smoke.
Follow executor failure/rollback rules; complete report/handoff only after evidence.

## Do Not Repeat

Benchmark runs, selector replays, statistics, dev merge, local rehearsal, receipt preparation,
hosted snapshot or applied migration. Never edit bound artifacts or write hosted rows by hand.

## Context consulted

Codex resume: master 3/11/13/17/26, Phase 11 handoff, undergraduate scope policy, thesis physical
17–18 and 39–44 via pypdfium2, routing PNG. RAG/Symbolic/Hybrid separation preserved.
Thesis closed-world example does not override unknown-versus-unmet guards; English/Taglish replies follow
the owner decision while English/Filipino/Taglish inputs remain. No new scope or routing discrepancy.
