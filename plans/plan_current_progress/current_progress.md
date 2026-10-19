# Current progress

Updated:19October2026. Phase07 active in p07/feat/p07-router-taglish-nlp.
[Developer handoff](../2026-10-19-phase07-cli-handoff.md), [checkpoint](../phase-07-checkpoint.md),
[comparison/results](../2026-10-19-phase07-prompt-comparison.md),
[standing owner decision](../2026-10-19-prompt-engineering-and-validation-decision.md).
Last full snapshot:00a0e68:plans/plan_current_progress/current_progress.md.

## Current delivery

Audience decoder correctiondfa16d2 verified:excluded/unrelated -> unsupported_scope;
unknown -> clarify. Model still selects audience; host/style/wording unchanged.
Selected three existing excluded-language variants now propose correct control3/3
(previously0/3),effective3/3alreadyguarded. Three fresh routing calls/three exact
baseline style reuses,zero repairs/transport failures. Reused style2/3 unchanged;
Taglish still wronglyFilipino. No full15/fresh-style accuracy claim. Runtime STOPPED.
[Scope correction/results](../2026-10-19-phase07-audience-decoder-correction.md).

## Verified evidence

Baseline at7b99552,original style-v1 loaded before candidate edits:15cases,30fresh
model calls,zero repairs/transport failures. Proposals10/15,effective13/15,style13/15;
entity/claim/operation collections15/15each(6nonempty,9empty),family consistency3/5.
Verifier passed30captures/35artifacts,minimum3853context headroom. This is dev
observation, not population/final-answer accuracy. Exact per-language table in report.
Errors:prerequisite-fil wronglyHybrid,greeting-taglish wronglyRAG; all three
excluded proposals wronglyRAG but existing audience guard returns unsupported_scope.
Procedure-taglish/excluded-taglish wronglyFilipino. Host guard success is separate.

Candidate9dde229 interrupted with21captures:11reused routes,10fresh completed styles.
Paired subset:baseline9/10styles,candidate8/10;zero fixes,one regression
prerequisite-fil (neutral B1 code counted as English). procedure-taglish still wrong.
Five planned outputs incomplete, including unfinished req-0011; no full15 score.
Interruption cause unestablished (container255,OOMKilled=false). Retirement verifier
passed capture/code/profile/grounding/reuse checks; comparison JSON seals retained.
completion-status.json=retired_early_on_observed_regression,runtime_stopped=true.
Restored24-file gate1580passed/11subtests101.65s,exit0;final-regressions.log.
Retirement docs/ledger576passed/11subtests17.50s,exit0;retirement-docs.log.
Prior candidate TDD/review retained in report; fixture integrity did not predict
model accuracy. Two inherited Docling failures remain; no whole-project-green claim.

## Standing decisions and next action

Prompt engineering/guards accepted across future phases; no parameter training,
fine-tuning/LoRA/learned soft prompts. One-week added-improvement cap before defense.
Numeric95%targets remain proposals. Curriculum/Prolog; handbook/Charter/memos RAG;
Hybrid needs both. English/Filipino/Taglish style; final answers/images later.
Undergraduate/read-only/private/source-gap/EMPTY_REGISTRY/release holds preserved.
Context scope17-18 saved extraction/actual routing PNG refreshed; prior architecture
pages39-44/58-59/master3/11/12/13 retained, no discrepancy.

Read-only hosted check confirms same project:6applied versions through12October
vs13repo files;7Phase05 versions absent from history. Actual schema not audited;
no DB mutation. [Status](../2026-10-19-hosted-migration-status.md).

Verification:RED18failed14passed ->176passed1.83s;independent no P1/P2,
176passed2.24s. 24-file gate1612passed/11subtests125.90s;docs577passed/11subtests
31.87s. Saved15outputs:only three excluded contradictions rejected. Scope17-18/
PNG/master12 refreshed. New raw root:workspace/audit-evidence/p07-audience-constraints-20261019/.
verify-evidence.py passed6captures/code/schema/profile/exact-reuse checks;minimum
3317context headroom;report/manifest retained, runtime-stop.json confirms exited.

Next:review prerequisite-fil/greeting-taglish route errors and two style errors
from saved captures under the one-week cutoff; document one bounded correction
only if supported. No new sweep, duplicate calls, host override or Phase08.
