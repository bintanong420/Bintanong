---
artifact: phase-checkpoint
phase: 9
status: in_progress
sequence: 29
plan: plans/phase-09-generation-validation-plan.md
head_commit: efc6343
working_tree: dirty
updated_at: 2026-10-20T10:47:00+08:00
---

# Phase09 checkpoint - CUDA latency observations

## Completed Tasks

Actual-service composition7227732,CLI df99ac6,input snapshot fab0225 and bounded
reads ab9aee9 delivered. [Prior delivery](2026-10-20-live-backend-composition-results.md).
Workflow guarde0e86ea prevents historical handoff from advancing unfinished Phase09.
Last full pre-condensation snapshot:24423f4:plans/phase-09-checkpoint.md.
CUDA config5d92f9c and compact prompt display24423f4 delivered;see
[latency results](2026-10-20-phase09-latency-results.md) for exact evidence.

## Current Task

Owner requests more speed work/research. Execute [focused plan](2026-10-20-fast-replies-research-plan.md).
Reuse prior evidence;test memory-aware placement and compact decoded JSON.
Prior bounded latency observations complete;Phase09 quality work remains.
All3actual-service compact requests answered:85.297sRAG/79.815sSymbolic/148.043sHybrid
versus277.492/304.913/355.696sCPU. Four model calls,one draft/check,no repairs each.
CUDA original-prompt Hybrid171.410s;router4160tokens read6.813s vs93.972sCPU.
Same-GPU compact model time rose107.042->125.884s;retrieval fell64.284->22.099s.
Different builds,cold costs/output lengths limit causal claims. Compaction reduces
input size;its separate inference/end-to-end gain is not established. Stop diagnostic.

## Repository State

p09/feat/p09-generation-validation. Verified product HEAD24423f4;final wrapper only
updates README/docker docs,INDEX,progress,checkpoint and dated latency results.
These documentation files are the relevant dirty changes. No Phase10 branch/work.
CUDA bintanong-p09-cuda-latency running18088;CPU bintanong-p07-router-offline stopped
intact to freeRAM. Explicit runner --url http://127.0.0.1:18088 required;default18087.

## Verification Evidence

Compose validates;pinned officialamd64image,localhost/read-only weights/one GPU,
no implicit pull. Owner-approved pull completed;8layers~1.1GB then one24layer
capacity adjustment,final2135MiBused/1828free. Readiness/props/DeviceRequests saved.
Display helper REDmissingmodule/GREEN6tests1.69s;actual-builder RED4failures;after
wiring200focused tests pass3.01s. Three legacy byte-equality assertions updated
for compact display;exact decision constraint/decoder immutability remain checked.
New tests cover4builders,literal fields,source payloads and160routing combinations.
Final47-selection gate:1892passed/66subtests95.14s,exit0. Exact roster/command in
raw verify-regressions.ps1;full output final-regressions.log. No full legacy sweep.
Independent final review:current-schema/code/Compose changes accepted;16saved model
outputs schema-valid. Three compact requests/8claims:7clear fits,1Hybrid citation/
scope concern. Canonical decision correct;fallible checker accepts c2's wrong
support basis. No language-wide/accuracy/default-budget readiness claim.
Prior composition gate1881/66subtests88.53s and earlier failures remain preserved;
no repeat source review/setup. State inspect valid/active9/cannotadvance.

## Versions and Digests

Raw:workspace/audit-evidence/p09-latency-20261020/;report links final manifest hash.
All85manifest files verified;docs hygiene584passed1.20s/86local links resolve.
Official CUDA manifest f66a5229a3e0586339d16155e9fe09c37834d7a7f4134bbdee7360b5a1f2546d;
2,594,107,748compressed bytes. CUDA b11723-31288c9c6 vsCPU b11718-547208dca.
RTX3050Laptop4096MiB/driver596.36. Same existing GGUF/template/context8192/output768/
threads8/temp0/seed0/reasoning-none/cachefalse;same full decoder hashes per route.
Python3.13.7/Pydantic2.13.5/HTTPX0.28.1,Janus1.5.2/SWI10.1.15/encoder6.1.0 unchanged.
Observation240s inference/generation,300s stage,600s request retained.
Original model/embedding identities inherited from sealed composition evidence;
SEA-LION strict asset verification reruns;GGUF not independently rehashed here.
Thesis physical17â€“18/39â€“44,actual PNG/master11â€“14 consulted;after rollover reread
physical17â€“18/39â€“40 and PNG. No scope/routing discrepancy. Actual owner model root
workspace/MODELS;former C:/Coding-projects/MODELS absent,no copies/downloads.

## Decisions

Owner20October2026 resumes implementation and explicitly approves "Download and
test the CUDA runtime" (~2.6GB pinned image only). No model/project dependencies.
Keep four-call topology/instructions/full guards while shrinking displayed schema.
No new model,seed/layer sweep,training,benchmark wording or source-content decision.
Separate Phase10 per owner boundary;no phase advancement. Default institutional
provider/source/runtime/activation holds retained. Only fictional local fixture
release is active;anon/RLS reads,exact membership/hash/synthetic checks preserved.

## Known Failures or Blockers

Hybrid c2 claims an executed check using only documentary evidence;requires symbolic
support/tighter scope. Existing broad eligibility phrasing/checker fallibility,
two Taglish style errors,opaque IDs and absent explicit post-retrieval reconsideration
remain. Cold encoder costs and4serial calls still make requests slow. No official
enrollment determination. Human output review pending;university/source/auth/private/
activation holds persist. Hosted still has onlyPhase04 migrations;no hosted changes.

## Next Action

Execute focused speed plan:one memory-aware placement check,compact-output RED/GREEN,
then bounded actual-service observations. Keep known Hybrid citation issue visible;
no broad sweep or claim of very fast replies until measured.

## Do Not Repeat

Resolved CUDA download/capacity/timing diagnostics,prior prompt/model sweeps,
settled source decisions or accepted institutional wordings. Preserve failed and
interrupted observations. Do not substitute preassembled evidence/manual vectors/
scripted inference for actual services,or activate real institutional candidates.
