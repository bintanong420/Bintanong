# Current progress

Updated:19October2026,14:20. Phase07 remains active in p07/feat/p07-router-taglish-nlp.
[Plan](../phase-07-multilingual-routing-plan.md), [checkpoint](../phase-07-checkpoint.md),
[current correction/results](../2026-10-19-phase07-operation-constraint-correction.md),
[prior style results](../2026-10-19-phase07-style-stage-evaluation.md),
[accuracy research](../2026-10-19-phase07-accuracy-research-recommendation.md).
Pre-condensation snapshot:bec3d8e:plans/plan_current_progress/current_progress.md.

## Latest findings and product baseline

Owner accepts [prompt engineering/guards for this and future phases](../2026-10-19-prompt-engineering-and-validation-decision.md),
with a one-week cap on added improvement work. Saved in AGENTS/index/phase plan.
Inference-time guidance is not parameter training; no fine-tuning/soft-prompt tuning.
Owner-reported other4080/8GB is unverified; local3050/4096MiB reading unchanged.
Read-only transport audit:temperature0/seed0/reasoning-none explicit; cache implicit
and effective inference profile incomplete. No model calls or product change.

Owner prioritizes minimal errors/high accuracy; the quality-priority question is
answered. Research confirms prior thinking probe used reasoning_budget=128,
where pinned runtime reads reasoning_budget_tokens/thinking_budget_tokens. Its
three observations do not establish an enforced128budget or controlled comparison.
Pinned runtime also warns cache reuse can change outputs; cause here unproven.
Google recommends a different sampling recipe, not a proven fix. Report links
primary sources, limitations and an ordered comparison before any prompt changes.
No code/new inference/runtime restart/download/install or accuracy improvement.

Product bec3d8e constrains proceeding decoder output:RAG0operations,
Symbolic/Hybrid exactly1. Clarification preserves compounds. Host guard remains
unchanged and withholds a nonconforming transport's compound without truncation
or semantic retry. Prompt text, canonical Interpretation v1 and style-v1 unchanged.
Version router-p07-v7 identifies the changed embedded schema, not a language sweep.

TDD RED6failed/4passed0.80s ->GREEN137routing tests1.33s. Independent review:
no P1/P2,137passed1.42s. Broad24-file gate1567passed/11subtests76.68s,exit0.
Two inherited Docling failures remain disclosed; no whole-project-green claim.

Actual six EXISTING structured variants:6fresh routing calls/6exact-compatible
style captures reused,12logical calls,zero repairs. Operation name/target,
canonical entities and claim meaning6/6. Proposed/effective routes5/6:Filipino
prerequisite wrongly chooses Hybrid; other variants correct. Family consistency1/2.
All three affected-course-plus-procedure cases now select one correct operation,
including previously failing Taglish. Count correctness is not route correctness.
Style6/6 is reused evidence only; two known Taglish errors in prior15-case profile
remain (13/15styles). No new whole15-case or final-answer accuracy claim.

Evidence verifier passed12captures/21sealed artifacts. Exact commands, hashes,
matrices, failed reason and input-token budgets are in the current correction report.
Task-only runtime stopped12:25; inspect=exited. Image/container/models retained.
No weights, installs, locks, sources, registry, other containers/worktrees or remotes changed.

## Decisions and next action

Scope physical17-18 reread from saved extraction, actual routing PNG viewed, PDF
hash verified unchanged. Existing39-44/58-59/master3/11/12/13 decisions preserved.
Master2.2 names quantized Gemma4E4B as Bintu-1; the supplied model is intended.
No separately fine-tuned checkpoint is required. Preserve the same artifact and
all undergraduate/read-only/source-authority/activation/Phase06 boundaries.

Next:specify/test an explicit cache/baseline profile with unchanged semantic prompts,
then the bounded prompt comparison under the one-week cap. Correct the prior probe's
budget-control assumption if checking thinking. Keep both Taglish style errors and
the Filipino Symbolic/Hybrid error open. Proposed95%per-language development targets
are recommendations, not approved gates or measured population accuracy.
Stop the resolved count diagnostic; no blind retired trials/wording sweep, host
semantic override, model change/training or Phase08 advancement. Research/docs
standing-decision gate572passed/11subtests15.20s,exit0; phase state valid/diff check clean.
