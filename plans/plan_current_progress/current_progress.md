# Current progress

Updated:19October2026,15:09. Phase07 active in p07/feat/p07-router-taglish-nlp.
[Plan](../phase-07-multilingual-routing-plan.md), [checkpoint](../phase-07-checkpoint.md),
[standing decision](../2026-10-19-prompt-engineering-and-validation-decision.md),
[verified baseline correction](../2026-10-19-phase07-inference-baseline-plan.md).
Full previous snapshot:29cc8d9:plans/plan_current_progress/current_progress.md.

## Latest verified change

Product29cc8d9 makes cache_prompt=false explicit for both decoder modes and records
request settings separately from allowlisted server defaults. Semantic prompts,
schemas, host guards and call limits unchanged. No training.
RED7failed/10passed0.92s ->GREEN106passed3.43s. Independent review:no P1/P2,
106passed2.29s. Broad24-file gate1577passed/11subtests128.27s,exit0.
One actual synthetic transport smoke passed;24input tokens,one model call,valid
JSON. This is no routing/language accuracy result. Evidence verifier passed8sealed
artifacts again on resume; unchanged semantic modules and runtime inspect=exited.
Exact commands/settings/evidence in baseline plan; task runtime stopped14:32.

Server defaults:T1/top_k64/top_p~0.95/min_p~0.05/repeat_penalty1. Requests override
T0/seed0/reasoning-none; profile=p07-greedy-no-prefix-cache-v1. Cacheoff does not
prove determinism; fresh evaluation must measure quality. No duplicated setup,
weights/downloads/installs/locks/registry changes.

## Open accuracy evidence

Prior productbec3d8e six structured cases:6fresh routing/6reused style calls;
operations/entities/claims6/6,routes5/6. Prerequisite-fil wronglyHybrid.
Prior full15style profile13/15:procedure-taglish/excluded-taglish wronglyFilipino.
These differ from current profile; do not merge them into current accuracy.
[Prior correction](../2026-10-19-phase07-operation-constraint-correction.md),
[style report](../2026-10-19-phase07-style-stage-evaluation.md).
Two inherited Docling failures remain disclosed; no whole-project-green claim.

## Decisions and next action

Owner accepts prompt engineering/guards across future initial-build phases, maximum
one-week added-improvement work before defense. Guidance is inference-time, not
parameter training. No fine-tuning/LoRA/learned soft prompts. Numeric95%targets
remain proposed, not an approved gate. Carry decision into later handoffs.
Context physical17-18 saved extraction/actual routing PNG refreshed on resume;
prior39-44/58-59/master3/11/12/13 retained. No scope discrepancy.
Curriculum/Prolog; handbook/Charter/memos RAG; Hybrid needs both. English/Filipino/
Taglish preference; final answers/images later. Undergraduate/read-only, source
gaps, EMPTY_REGISTRY and institutional-release holds remain.

Next:run one fresh baseline on existing15synthetic cases under explicit profile,
retaining both stages/raw captures. Then one justified prompt change with matched
evaluation and no final-family leakage/semantic host override. Stop resolved cache
and count diagnostics and unchanged retired sweeps. Phase08 gated.
