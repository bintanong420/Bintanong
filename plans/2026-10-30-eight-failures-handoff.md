---
title: Handoff - fix the 8 remaining benchmark failures
date: 2026-10-30
worktree: p12
branch: p12-evaluation-harness
head_commit: see `git log -1` (handoff commit follows 9b4111f)
status: open
---

# Handoff: fix the 8 remaining benchmark failures

Owner request (30 Oct 2026): "lets fix those 8 questions first, do a handoff so i can switch cli new context window".
Post-Phase-12 accuracy work on the existing p12 branch; no implementation phase is active and Phase 13 stays cancelled.
Read this, then [current progress](plan_current_progress/current_progress.md) and the
[owner-decisions ledger](owner-decisions-ledger.md) (30 Oct entries). Do not re-ask decisions recorded there.

## State at handoff

- Clean tree. Code commits this session (all test-first): `abbaf58` headings kept despite defects; `9f1b9ac`
  malformed-condition records quoted with limitation + office referral; `1f2f9db`/`1cbc68b` conflicting-deadline
  records outside a real conflict group quoted alone; `880c733` router `fact_headings`; `5904e09` router guard
  (a heading naming >=2 of the part's words replaces a choice whose headings name none); `91fa3c0` limitation
  quotes lead with the printed text. `3430b67` (reviewer instruction) was reverted by `6b7d2a7`.
- Last full regression: 42/50 on `6b7d2a7` (owner-run, `audit-evidence/p12-regression-20261030/run-ddf2338-owner-b1..3`).
  The final code `91fa3c0` is NOT yet regressed: first action is the owner `-owner2` run below.
- INC ("How do I remove an incomplete grade?") answers on `91fa3c0` (diag `run-91fa3c0-inc-reworded`). Honors stays a
  disclosed limitation: owner chose to keep the `introduced_disjunction` guard. Probation passes.
- Related tests: generation/routing/runtime/orchestration/API 1670 pass on `91fa3c0`. Full suite last run on
  `9f1b9ac` (7172 + DB rerun 182, green); rerun before claiming completion.
- Hosted servers (:8021 backend, :3216 frontend) are stopped; the owner runs them in their own PowerShell windows.
- Evaluation honesty: the frozen Phase 12 score stays 38/50. These 50 cases are now development data; report any new
  score as post-fix, same cases, single runs (+/-1). A held-out set is needed for an unbiased post-fix score.

## The 8 failures (run-ddf2338-owner-b*, per-case folders hold call-N-request/result and integration.json)

| Case | Question | Got | Likely cause / first check |
| --- | --- | --- | --- |
| disc-plagiarism-en | What is the penalty for plagiarism? | clarification_needed, no route | Router clarify. Compare call-2 result; see 28 Oct Learnings (grammar-forcing clarify failed twice). |
| disc-plagiarism-taglish | Ano ang parusa sa plagiarism? | same | Same cause as EN. |
| second-year-taglish | Kailan ako considered second year? | insufficient_evidence, control_fallback, no route | Router failure/clarify before topics; check call-1/2. EN passes. |
| cc5-failed-cc4-en | Can I take CC5 even if I failed CC4? I am a Computer Science student. (palsu-bscs, bscs-2018-2019) | RAG to handbook_prerequisite_policy | Should be structured/Prolog, decision ineligible citing CC 4/L. Short-form codes resolve per 21 Oct owner rule; Taglish twin passes. Check router mentions/operations. |
| disc-uniform-taglish | Ano ang parusa kapag mali ang uniform ko? | insufficient_evidence; chose II.13 discourtesy row | Wrong penalty row (uniform row exists, EN passes). Router claim choice; compare EN menu choice. |
| grad-residence-taglish | Ano ang residence requirement para maka-graduate? | answered with p.42 "1 1/2 times prescribed length" clause | Missing the one-year residence clause; claim/record selection or answer omission. EN passes. |
| summer-load-en | What is the normal unit load for summer? | answered "nine (9) units" only | Omits the 12-unit exception with Dean approval. Check whether that record was retrieved and what the reviewer accepted. |
| leave-length-taglish | Gaano katagal pwede ang leave of absence? | answered "isang (1) academic year" | Content correct; keyword check expects "1 academic year". Scoring artifact: changing cases.json/scorer needs an owner decision. |

Rules for fixes: test-first with synthetic fixtures; no institutional data in tracked tests; never weaken
accuracy/source/scope guards to pass a keyword (owner kept the disjunction guard); stop after a bounded attempt and
replay the recorded request with one variable changed before changing prompts (see Learnings, 30 Oct). Prefer
host-side deterministic fixes; check the offline blast radius on recorded router outputs before a model run.
Reusable diagnostics (ignored): `audit-evidence/p12-eight-failures-20261030/blast2.py` (router-guard impact over
recorded integration.json) and `replay_reworded.py` (replay a recorded review request with one change); run from p12.

## How to run on this machine (verified 30 Oct)

- Docker Desktop may be off after reboot: start it, then `docker start bintanong-p09-cuda-latency`, wait for
  `http://127.0.0.1:18088/health` 200. Stop `supabase_db_Bintanong` for model runs; start it again (wait healthy)
  before the full suite, whose 17 DB test files need it.
- Python: `audit-evidence/p05-real-retrieval-readiness-20261012/venv/Scripts/python.exe -X utf8`, `PYTHONUTF8=1`,
  pytest `-p no:cacheprovider --basetemp=<external>`. System Python lacks sentence_transformers.
- Single-case diagnosis: `GATE_ONLY=<id> GATE_SUFFIX=-<tag> PY audit-evidence/p12-doc-diagnosis-20261030/run_diag.py < /dev/null`
  (its cases.json holds inc-en/honors-en/probation-en; the regression runner below also accepts GATE_ONLY for any of
  the 50). Runners refuse a dirty backend and a repeated suffix. Hosted Supabase DNS drops intermittently
  (`getaddrinfo failed`): rerun with a new suffix.
- Claude Code's low-memory reaper kills long background jobs and servers (even at ~4.7 GB free). Run the 50-case
  regression in the owner's own non-admin PowerShell, servers stopped:

```powershell
cd C:\Coding-projects\bintanong_workspace\worktrees\Bintanong\p12
$env:PYTHONUTF8=1
$PY="..\..\..\audit-evidence\p05-real-retrieval-readiness-20261012\venv\Scripts\python.exe"
$R="..\..\..\audit-evidence\p12-regression-20261030"
foreach ($b in 1,2,3) {
  $env:GATE_ONLY = Get-Content "$R\b-6b7d2a7-$b.txt" -Raw
  $env:GATE_SUFFIX = "-owner2-b$b"
  & $PY -X utf8 "$R\run_regression.py" *> "$R\run-owner2-b$b.log"
  "batch $b exit $LASTEXITCODE"
}
```

  Use a new suffix per run. Logs show harmless NativeCommandError text. Compare against `run-ddf2338-owner-b*`
  and the 38/50 run `audit-evidence/p12-benchmark-20261029/run-38ccb83-condition-c-items`.
- Servers (owner windows): backend `PY -X utf8 ..\..\..\audit-evidence\p12-hosted-560-activation-20261030\start_hosted_research_api.py`
  from p12 (ready ~80-110 s, prints `app constructed`); frontend `node_modules\.bin\next dev -p 3216` from p12\frontend.
  A reaped `next dev` can leave an orphan holding :3216.

## Next action

1. Owner runs the `-owner2` regression on the current HEAD (baseline for `91fa3c0`).
2. Fix the failures in order: plagiarism (x2) and second-year Taglish (router), cc5 EN (structured routing),
   uniform/grad-residence Taglish (selection), summer-load EN (completeness); ask the owner about leave-length scoring.
3. Regression after each cohesive fix (owner-run), full suite before completion, update progress and report.
