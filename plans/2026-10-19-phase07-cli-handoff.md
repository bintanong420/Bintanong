# Phase07 developer handoff - baseline verified, style comparison running

Prepared19October2026 at owner's request. Phase07 remains IN PROGRESS; this is
not a complete numbered-phase handoff and does not authorize Phase08.

## Start here

Workspace:C:/Coding-projects/bintanong_workspace/worktrees/Bintanong/p07,
branchfeat/p07-router-taglish-nlp. Read AGENTS, INDEX, current progress and Phase07
checkpoint; run phase_state.py inspect/validate. Refresh Context physical17-18
and the actual runtime-routing PNG; prior39-44/58-59/master3/11/12/13 stay settled.
Preserve other worktrees/dev/p06, source decisions and all institutional holds.

Owner accepts [prompt engineering/guardrails](2026-10-19-prompt-engineering-and-validation-decision.md)
for remaining initial-build phases:inference instructions/examples, no weight
training/fine-tuning/LoRA/learned soft prompts. Maximum one-week added accuracy
work before defense. Numeric95%targets are proposals, not approved gates. Keep
LLM routing, curriculum/Prolog and document/RAG roles; English/Filipino/Taglish
style matching. Final generation/images later. No keyword route override.

## Delivered commits and verification

- bbaf5f9:standing decision in AGENTS/index/phase plan.
- 29cc8d9:explicit cache_prompt=false profile, safe reported sampling defaults;
  [verified record](2026-10-19-phase07-inference-baseline-plan.md), docs7b99552.
  RED7failed/10passed0.92s ->106passed3.43s; review no P1/P2,106passed2.29s;
  24-file gate1577passed/11subtests128.27s. One actual transport smoke, no accuracy claim.
- 9b61f99:bounded comparison plan. 9dde229:style-v4 CANDIDATE adds six balanced
  unrelated grounded examples; schema/router/host unchanged. RED1failed/32passed
  1.67s ->145passed3.40s; independent review no P1/P2,124passed3.31s.
  Candidate actual-model selection and final broad regressions STILL PENDING.
- 0110668:latest prior checkpoint and read-only hosted migration gap. Subsequent
  handoff documentation commit discoverable in Git. No pushes/merges/installs.

## Running work - inspect before doing anything

Raw root:C:/Coding-projects/bintanong_workspace/audit-evidence/p07-prompt-comparison-20261019/.
All captures/data/scripts stay ignored. [Comparison plan](2026-10-19-phase07-prompt-comparison.md).

1. Baseline unified session71133:evaluate-prompt.py baseline; original style-v1
   already imported at7b99552, code hashes saved BEFORE style-v4 edits. All15
   original synthetic cases, both stages fresh, new explicit-cache profile.
   COMPLETE:30fresh calls,zero repairs/failures; verification passed30captures/
   35artifacts,minimum3853context headroom. Do not run another baseline.
2. Candidate session87552:run-candidate-after-baseline.ps1,process8000 at
   capture. Baseline finished; evaluate-candidate.py candidate is NOW RUNNING.
   Fifteen new style calls, fifteen EXACT-matched current-baseline routing captures
   reused. No fresh-route or two-stage latency claim; no older implicit-cache reuse.
3. Completion supervisor session63851:finish-running-evaluation.ps1. Waits for
   candidate completion, runs verify-comparison.py for both, then compare-results.py,
   writes completion-status.json and stops ONLY bintanong-p07-router-offline.
   It starts no model calls, edits no repository files and never selects a candidate.
   On failure it records needs_review and still stops the task runtime. One-hour
   bound; inspect logs/status before assuming success or rerunning anything.

In this conversation poll the named sessions with write_stdin; across sessions
inspect task-specific process names/log timestamps plus completion-status.json.
Runtime localhost18087. Assets retained. Do not run another client/stop container
while legitimate current model calls are alive. If all jobs finish, confirm
docker inspect state=exited. Supervisor monitors observed queue-wrapper PID8000;
new wrapper PIDs after a manual resume require updating/reviewing the supervisor.

## Verified baseline -15synthetic cases,not population accuracy

Proposals10/15,effective outcomes13/15,styles13/15;entity/claim/operation collections
15/15each(6nonempty,9empty). Family consistency3/5. English4/5proposals,5/5effective,
5/5style;Filipino3/5,4/5,5/5;Taglish3/5,4/5,3/5. No new candidate score yet.

- procedure-taglish still selects Filipino style; this motivated the single candidate.
- prerequisite-fil wrongly selects Hybrid instead of Symbolic.
- greeting-taglish("Hi, kumusta?") wrongly selects RAG even though reason says greeting.
- All three excluded variants propose RAG with audience=excluded; existing explicit
  audience-precedence guard returns unsupported_scope correctly. Count model errors
  separately from guarded success. excluded-taglish also wrongly selects Filipino.

## Recovery and exact next action

First inspect existing jobs and reports. If finished, read completion-status.json,
baseline-verification.log,candidate-verification.log,comparison.json and comparison.log.
If verifier fails, diagnose the saved evidence/command; do not repeat model calls
to fix an offline verification defect. All raw captures include request/schema/
template/token metadata. Model semantic errors stay in denominators.

If candidate was interrupted, NO live candidate/finisher exists and no candidate
report is complete, restart retained task server, verify same props/config, then
use existing readiness Python -B evaluate-candidate.py candidate --resume. It
requires unchanged code/cases/profile, replays exactly matching saved style outputs,
retains saved failures and runs missing calls only. Provenance separates cumulative
captured style calls from new calls/replays in the resumed process. No automatic
retry of a saved model failure. Do not use --resume against a completed report.

After results:select or retire ONLY the current style candidate; compare all15,
especially pure-language regressions. Routing errors remain independent. Finish
the prepared verify-final.ps1 24-file gate, record exact output, seal evidence,
update compact plan/progress/checkpoint and commit explicit paths. If candidate
regresses, restore only its own product/test/docs changes with verified evidence;
preserve history and unrelated edits. Stop task runtime and keep Phase07 active
until actual exits. Do not begin another prompt/seed/schema-order/thinking sweep.

## Runtime and release boundaries

Readiness Python:C:/Coding-projects/bintanong_workspace/audit-evidence/p05-real-retrieval-readiness-20261012/venv/Scripts/python.exe.
Use -B,pytest -p no:cacheprovider,external TEMP/TMP/basetemp. Model stays at owner's
workspace/MODELS/GEMMA_4_E4B, SHA2563cf61de12daa015ee0f7b68e7b7c541405bf220e1e942bad8b47cab827d7df80.
llama.cpp b11718-547208dca; image sha256:4b7be0376002b4450a357a109bab804093ff9251193cc75ed4ce0cb39953ff5c.
Profilep07-greedy-no-prefix-cache-v1:T0/seed0/reasoning-none/cachefalse/output768/
context8192/CPU8/one slot. Props report T1/top_k64/top_p~.95/min_p~.05/repeat1;
reported defaults are distinct from overrides. No new models/dependencies.
Undergraduate/read-only/private separation/source gaps/EMPTY_REGISTRY/release holds
remain. Prior inherited Docling failures disclosed; no whole-project-green claim.

## Supabase question

[Read-only status](2026-10-19-hosted-migration-status.md):same hosted project,
six applied versions through12October vs13repository files; seven Phase05 versions
absent from history. Actual schema drift not audited; no migrations applied. The
owner asked about age, not deployment. Reconcile schema/history before integration;
schema deployment and institutional data/release activation remain separate.

Handoff docs/ledger576passed/11subtests25.98s,exit0;handoff-docs.log in raw root.
