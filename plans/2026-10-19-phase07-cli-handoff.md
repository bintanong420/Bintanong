# Phase07 developer handoff - audience consistency correction

Updated19October2026 after continuation. Phase07 remains IN PROGRESS; this is
not a complete numbered-phase handoff and does not authorize Phase08.
Last full snapshot:00a0e68:plans/2026-10-19-phase07-cli-handoff.md.

## Start here

Workspace:C:/Coding-projects/bintanong_workspace/worktrees/Bintanong/p07,
branchfeat/p07-router-taglish-nlp. Read AGENTS, INDEX, progress and checkpoint;
run phase_state.py inspect/validate. Refresh Context physical17-18 and actual
routing PNG; prior39-44/58-59/master3/11/12/13 remain settled. Preserve dev/p06.

Owner accepts [prompt engineering/guards](2026-10-19-prompt-engineering-and-validation-decision.md)
for later initial-build phases:inference instructions/examples, no parameter
training/fine-tuning/LoRA/learned soft prompts. Maximum one-week added accuracy work.
Numeric95%targets remain proposals. LLM routing, curriculum/Prolog, documents/RAG,
English/Filipino/Taglish preferences remain required. Final generation/images later.
No keyword route override. Undergraduate/read-only/private/source-gap/EMPTY_REGISTRY/
institutional release holds remain. No push/merge/install/other-worktree changes.

## Delivered and verified

- bbaf5f9:standing decision in AGENTS/index/phase plan.
- 29cc8d9:explicit cache_prompt=false profile and safe reported sampler defaults;
  [verified record](2026-10-19-phase07-inference-baseline-plan.md), docs7b99552.
  TDD7failed/10passed ->106passed; independent no P1/P2,106passed;
  prior24-file gate1577passed/11subtests;one actual transport smoke.
- 9dde229:style-v4 six-example candidate, TDD1failed/32passed ->145passed;
  independent review no P1/P2,124passed. Actual model evidence rejected it.
- 833d2f4:only style.py/README/candidate-only test restored exactly to9dde229^;
  Git diff identity verified. Restored24-file gate1580passed/11subtests101.65s,
  exit0;final-regressions.log. No new language fix or accuracy gain claimed.
Retirement docs/ledger576passed/11subtests17.50s,exit0;retirement-docs.log.

## Evidence - do not restart retired work

Raw root:C:/Coding-projects/bintanong_workspace/audit-evidence/p07-prompt-comparison-20261019/.
Captures/scripts/data stay ignored. [Comparison/results](2026-10-19-phase07-prompt-comparison.md).
Baseline COMPLETE at7b99552:15cases/30fresh calls,zero repairs/failures; verifier
passed30captures/35artifacts,minimum3853context headroom. Original style-v1.
Proposals10/15,effective13/15,styles13/15;entity/claim/operation collections15/15each
(6nonempty,9empty),family consistency3/5. Per-language counts in report. Synthetic
observations only; distinct from75accepted institutional variants and final tests.

Candidate interrupted:21captures,11exact reused routes/10fresh completed styles.
No candidate/report.json. Container exited255,OOMKilled=false; cause unestablished.
No model calls added on resume. Paired subset baseline9/10style vs candidate8/10;
zero fixes,one new prerequisite-fil error:neutral B1 code counted as English.
procedure-taglish still incorrectly Filipino. Five planned outputs incomplete,
including unfinished req-0011. No full15-case candidate score; missing not failures.
Observed regression already fails no-new-regressions selection criterion; early
retirement avoids calls that cannot restore acceptability. Keep style-v1.

verify-retired-candidate.py passed code/schema/request/profile/grounding checks
for all21captures and exact baseline reuse. retired-candidate-comparison.json
seals SHA256s;retirement-verification.log;completion-status.json records
retired_early_on_observed_regression,runtime_stopped=true. Task container
bintanong-p07-router-offline STOPPED after retirement and after new scope check.
No live87552/63851jobs. Old --resume and
supervisor instructions obsolete; do not restart retired evaluations.

## Latest scope correction and current task

Productdfa16d2 constrains existing host audience precedence:excluded/unrelated ->
unsupported_scope;unknown -> clarify, preserving compound details. Four original
undergraduate branches, semantic host checks and style-v1 remain. Routerv8 system
wording unchanged. [Correction/evidence](2026-10-19-phase07-audience-decoder-correction.md).
TDD18failed/14passed ->176passed1.83s;independent no P1/P2,176passed2.24s.
24-file gate1612passed/11subtests125.90s;docs577passed/11subtests31.87s,exit0.
Saved15outputs revalidated:only the three excluded contradictions rejected.

Raw root:workspace/audit-evidence/p07-audience-constraints-20261019/.
Selected-three check3451 COMPLETE,exit0. Three fresh routing calls/three exact
baseline style reuses,zero repairs/transport failures. Scope proposals0/3 ->3/3;
effective3/3alreadyguarded. Reused style2/3unchanged,Taglish still wronglyFilipino.
Audience remains excluded in all3;consistency fix,not new audience comprehension.
No full15/fresh-style/two-stage latency claim. verify-evidence.py passed6captures,
case/catalog/code/request/schema/profile/exact reuse;minimum3317context headroom.
excluded-three/report.json and manifest.json sealed;verification.log. Runtime
STOPPED,confirmed by runtime-stop.json and docker inspection. Do not rerun this
resolved scope check. Productdfa16d2,checkpoint464f276;latest docs wrapper in Git.

Baseline residuals:prerequisite-fil wronglyHybrid,greeting-taglish wronglyRAG,
procedure-taglish/excluded-taglish styles wronglyFilipino. Three excluded prior
RAG proposals were guarded correctly; selected check addresses consistency,
not previously unsafe dispatch. Four own-rule unknowns/full-prospectus defects remain.
Next:review the two remaining route errors and two style
errors from saved captures; propose one bounded correction only if evidence supports
it. Do not start a prompt/seed/schema-order sweep or claim Phase07 completion.

## Runtime and separate database boundary

Readiness Python:C:/Coding-projects/bintanong_workspace/audit-evidence/p05-real-retrieval-readiness-20261012/venv/Scripts/python.exe.
Python3.13.7/Pydantic2.13.5/HTTPX0.28.1/pytest9.1.1/Janus1.5.2/SWI10.1.15.
Use -B,pytest -p no:cacheprovider,external TEMP/TMP/basetemp. Owner-corrected model:
workspace/MODELS/GEMMA_4_E4B/gemma-4-E4B-it-UD-Q4_K_XL.gguf,5,126,306,944bytes;
SHA2563cf61de12daa015ee0f7b68e7b7c541405bf220e1e942bad8b47cab827d7df80.
llama.cpp b11718-547208dca; image sha256:4b7be0376002b4450a357a109bab804093ff9251193cc75ed4ce0cb39953ff5c.
Template74a88f94c57c14e22dcdbe08e94127f42b87c6f584cb73838e73e32126f3f6b3.
Profilep07-greedy-no-prefix-cache-v1:T0/seed0/reasoning-none/cachefalse/output768/
context8192/CPU8/one slot. Props T1/top_k64/top_p~.95/min_p~.05/repeat1 separate
from request overrides; no determinism guarantee. Assets retained,no downloads.
Inherited Docling failures outside selected gate remain; no whole-project-green claim.

[Hosted status](2026-10-19-hosted-migration-status.md):same project,6applied through
12October vs13repo files;7Phase05 versions absent from history. Actual schema not
audited;no mutations. Age question did not authorize deployment. Reconcile before
integration; schema deployment and institutional activation remain separate gates.
