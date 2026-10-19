---
artifact: phase-checkpoint
phase: 7
status: in_progress
sequence: 34
plan: plans/phase-07-multilingual-routing-plan.md
head_commit: 7b99552
working_tree: prompt comparison plan, progress and checkpoint documentation
updated_at: 2026-10-19T15:11:00+08:00
---

# Phase07 checkpoint - explicit inference profile verified

## Completed Tasks

Original routing/contracts/resolution/style/transport/evaluator/scope guards and
count correction delivered. Normal2calls/max3with one shared format repair;
same Gemma for both stages, EMPTY_REGISTRY default, no executor. Standing decision
bbaf5f9 saved in AGENTS/index/phase plan for subsequent phases.
Product29cc8d9 adds fixed no-prefix-cache requests and safe reported-defaults
metadata, both decoding modes; no semantic prompt/schema/guard/call-limit changes.
[Profile plan/results](2026-10-19-phase07-inference-baseline-plan.md).

## Current Task

Profile correction verified:RED/GREEN,24-file gate,independent review and one
actual transport smoke complete. Resolved diagnostic stops here. Next fresh15-case
baseline [comparison](2026-10-19-phase07-prompt-comparison.md) is running, before
a single justified prompt intervention. Known route/style errors
remain open; no new accuracy or completion claim.

## Repository State

p07/feat/p07-router-taglish-nlp. Product29cc8d9; standing decisionbbaf5f9.
Full previous snapshot:29cc8d9:plans/phase-07-checkpoint.md.
Only plan/progress/checkpoint docs pending; product/tests committed.
Other worktrees/dev/p06 preserved; no push/merge/source/registry mutation.

## Verification Evidence

Transport RED7failed/10passed0.92s ->GREEN106passed3.43s. Independent review:
no P1/P2,106passed2.29s. Broad24-file gate1577passed/11subtests128.27s,exit0.
Raw workspace/audit-evidence/p07-explicit-profile-20261019/:red.log,green.log,
verify-profile.ps1,regressions.log,smoke-profile.py,smoke.json,verification.log.
Actual synthetic smoke1call,24input tokens,valid JSON;cachefalse request and
reported defaults verified. No multilingual/route/answer accuracy claim.
verify-evidence.py passed8sealed artifacts again on resume; current transport and
unchanged semantic-module bytes,build/template/context budget checked. Runtime
inspect=exited; stopped14:32,assets retained. No duplicate inference on resume.
Prior inherited Docling failures remain; no whole-project-green claim.
Final docs/phase gate573passed/11subtests15.55s,exit0;final-docs.log.

Historicalbec3d8e6structured:operations/entities/claims6/6,routes5/6;6routingfresh,
6stylesreused. Prior style-v1 full15profile13/15. Do not combine with newprofile
or claim current15score. Exact commands/results in profile plan.

## Versions and Digests

Python3.13.7/Pydantic2.13.5/HTTPX0.28.1/pytest9.1.1/Janus1.5.2/SWI10.1.15 unchanged.
Owner-corrected model root:workspace/MODELS/GEMMA_4_E4B,5,126,306,944bytes.
Model SHA2563cf61de12daa015ee0f7b68e7b7c541405bf220e1e942bad8b47cab827d7df80.
Official image sha256:4b7be0376002b4450a357a109bab804093ff9251193cc75ed4ce0cb39953ff5c;
llama.cpp b11718-547208dca. Template74a88f94c57c14e22dcdbe08e94127f42b87c6f584cb73838e73e32126f3f6b3.
Promptrouter-p07-v7/style-v1;schemasunchanged. Profilep07-greedy-no-prefix-cache-v1:
T0/seed0/reasoning-none/cachefalse/output768/context8192/CPU8threads/parallel1.
Reported defaults:T1/top_k64/top_p~.95/min_p~.05/repeat_penalty1;order saved.
Defaults separate from request overrides and external startup configuration.

## Decisions

Owner accepts [prompt engineering/guards across future phases](2026-10-19-prompt-engineering-and-validation-decision.md),
one-week added-improvement cap. Inference-time guidance is not parameter training;
no fine-tuning/LoRA/learned soft prompts. Numeric95%targets remain proposals.
Carry decision into later plans/handoffs. Context physical17-18 saved extraction
and actual runtime PNG refreshed on resume; prior39-44/58-59/master3/11/12/13
architecture preserved; no discrepancy. Curriculum structured/Prolog, documents
RAG,Hybrid when both needed. English/Filipino/Taglish preference; final answers/
images later. Undergraduate/read-only/private/source-gap/EMPTY_REGISTRY/release
holds preserved. Cacheoff does not guarantee determinism/accuracy. Previous
reasoning_budget probe used wrong key; no unchanged thinking/sampling sweep.

## Known Failures or Blockers

No environment blocker. Prior prerequisite-fil wronglyHybrid; procedure-taglish/
excluded-taglish wronglyFilipino. No new language fix. Prior combined-wire,
native-thinking,label-first,compact trials retired. Four own-rule unknowns,
full-prospectus defects and inherited Docling failures remain disclosed.

## Next Action

Finish running fresh15-case baseline under explicit profile, retaining both stages
under workspace/audit-evidence/p07-prompt-comparison-20261019/baseline/.
Then one justified prompt change and matched
evaluation. Preserve failures/denominators and final-family separation. No semantic
host override or Phase08 advancement.

## Do Not Repeat

Resolved cache/count diagnostics,completed model setup/downloads,unchanged retired
language/wording/schema-order/thinking sweeps,75wording acceptance,source/CSV review,
Phase06 receipts,arbitrary Prolog,activation,merges or other worktree edits.
