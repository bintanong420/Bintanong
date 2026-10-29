# Current progress

Updated 29 October 2026 (machine local date; inherited handoffs are dated 30 October).
Phase 12 active in p12 / `p12-evaluation-harness`; Phase 11 complete with disclosures.
[Plan](../phase-12-evaluation-writeup-plan.md) · [Checkpoint](../phase-12-checkpoint.md) ·
[Claude's executor handoff](../2026-10-30-hosted-560-codex-handoff.md).
Last full snapshot before condensation: `76d5a92`; use `git show` for prior history.

## Latest change

Codex read Claude's handoff at `76d5a92` and verified the prepared activation artifacts.
Hosted post-activation MCP: new560 active; corrected78 superseded (retained as rollback).
Owner supplied pooler host `aws-0-ap-southeast-1.pooler.supabase.com` and asked Codex to build the URI.
Owner corrected the password; privately rebuilt URI passed hosted psql SELECT 1. Hosted staging passed in 106.11 s.
.env is ignored and untracked; owner reiterated it must never be committed.
Activation exit 0 in 121.08 s: 560 anon-visible chunks / 39 links, retrieval hit, rows preserved.
Hosted backend starting for smoke; Phase 12 remains open.

Prepared ignored hosted pin/config after verifying all 560 chunk-ID/content-hash pairs match the bound review.
All sealed package files verify; protected receipts/events/snapshot unchanged. Backend `ResearchApiConfig`
and `_package` accepted the config with 560 chunks/vectors and hosted gate composition.
[Preflight results and exact next command](../2026-10-30-hosted-560-activation-results.md).

## Verified delivery already available

- Evaluation [report](../../docs/evaluation/phase12-evaluation-report.md),
  [benchmark results](../2026-10-29-phase12-benchmark-results.md), paired statistics complete.
  Original C 40/50 versus A 3/50 strict; main v2 38/50; rerun 39/50; Tagalog 19/26;
  shorthand 15/26; broken English 2/4. Development reuse and single-author/single-run limits disclosed.
- Historical full suite on merged `a3ff208`: 7314 pass / 1608 subtests, 6 skip / 2 xfail.
  Backend hosted-pin change `48330f7`: related 108 pass (Claude evidence; not rerun this session).
- Local 560 rehearsal saved PASS: 560 chunks/vectors, 39 links, replay no-op, anon/auth visibility,
  retrieval hit, rollback 78, existing rows preserved. Hosted flow migration already applied.
- Receipts cover 560 chunks; 257 re-authored records use the owner's activation directive with no
  per-chunk human approval. No receipt regeneration or source-state promotion authorized.

## Boundaries

Owner authorizes hosted 560 research activation, with corrected78 rollback. Deployment cancelled;
no institutional approval. No dependency/model changes or accuracy tuning. Use only `hosted.py` for writes;
do not edit bound artifacts, rerun snapshot, change hosted functions/grants/timeouts, or print credentials.
Original source gaps, undergraduate scope, unknown-versus-unmet and private-file separation remain.
Answer-quality benchmark on hosted composition is the owner's/Claude's follow-up.

## Next action

Run hosted-config HTTP and browser smoke; roll back if a required smoke criterion fails.
Follow Claude's stop/rollback rules; never stage .env or raw evidence.
