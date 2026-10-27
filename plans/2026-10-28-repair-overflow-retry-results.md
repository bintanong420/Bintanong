# Repair overflow retry without the previous draft

Baseline:f8953d4/codeb695739. Addresses the reachable discipline repair overflow in
[short review results](2026-10-27-short-review-reference-results.md).

## Change

When a draft repair (attempt 2) is refused by the transport's pre-inference
`context_overflow` check,the generator retries that repair once without
`untrusted_previous_draft`. The prompt keeps the complete source evidence,the
validation errors,coverage/order/quotation instructions and the schema. The model's
own previous draft is the only content removed;it is not source evidence.
Window8192/output768/margin8,budgets,defaults and the review path are unchanged.
An overflow on the first draft,or on the retry itself,still refuses as before
(`temporarily_unavailable`/`tool_error`). The retried draft still goes through all
host validation and the per-part review;no check is skipped.

## Evidence

Synthetic RED:2expected failures (overflowing repair returned
`temporarily_unavailable`;no retry sent),1characterization pass (initial overflow
not retried). One earlier test setup error (`reason`→`validation` field) was fixed
before RED was accepted. GREEN3pass;focused generation/parts/quote/coverage/API/
orchestration907pass/254subtests170.52s. Full suite with the change:7041pass/
1608subtests,6skip/2xfail/6warnings1357.08s,exit0 (baseline b695739 re-run:7038pass/
1608subtests,1461.63s,exit0,matching Codex's record). Docs/phase30pass/14subtests.
Ruff/Black/mypy/Bandit remain unavailable and were not installed.

Real-source capacity (local Gemma template/tokenize,zero inference),same deliberately
incomplete676/677-token short draft and `missing_procedure_record_coverage` error:

| Language | Repair with previous draft | Retry without it | Fits8192 |
| --- | ---: | ---: | --- |
| English | 7546in/8322total | 6819in/7595total | Yes |
| Taglish | 7555in/8331total | 6827in/7603total | Yes |

Totals include768output and8margin. The original8322/8331figures reproduce exactly.
Retry evidence payloads are identical to the overflowing repair's. These are capacity
probes,not observed model answers;longer questions/history/Hybrid may cost more and
remain covered by the existing refusal. No answer-quality,release or latency claim.

## Verification and recovery

Ignored root:workspace/audit-evidence/p11-claude-verify-20261028 (RED/GREEN/focused/full
logs,`check_repair_retry_capacity.py`,`repair-retry-capacity.json`,retry messages).
Independent re-verification of b695739 (Claude,28Oct):short-review RED reproduced on
the parent commit (13fail);focused804pass/254subtests;review output carries claim IDs
only,so short aliases need no inverse mapping. Supabase MCP reachable;hosted active
release p11-research-corrected-20261026 (78chunks/39curricula) matches the handoff.
