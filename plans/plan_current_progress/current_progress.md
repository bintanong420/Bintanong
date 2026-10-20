# Current progress

Updated:20October2026. Phase09 active,p09/feat/p09-generation-validation.
[Checkpoint](../phase-09-checkpoint.md) Ã‚Â· [Latest speed results](../2026-10-20-fast-replies-results.md).
Last full pre-condensation snapshot:791413e:plans/plan_current_progress/current_progress.md.

## Latest delivery

Owner continues;[combined routing plan](../2026-10-20-combined-routing-plan.md) removes
one round trip only if existing15case route/meaning/style promotion checks pass.
Combined contract/router GREEN142tests2.14s;profile/evaluation wiring GREEN81tests
3.27s after RED16/11failures. Separate default retained pending actual-model check.

Owner asks for further speed/research. Research plan8f502fb;implementation791413e.
Auto GPU fit512MiB selected35/43layers including output,about2.8GBVRAM/1.1free.
Same8192context/768output/8threads/weights/decoder/budgets. Unchanged-prompt Hybrid
83.059s vs148.043s on fixed24layers;observed decode~23tokens/s. Prior capacity
assumption from full GGUF size was too conservative;separate embeddings stay CPU.
CUDA remains18088,CPU fallback stopped intact. Explicit --url18088 flag required.

Shared compact-output guidance added to4versioned prompts;full guards,instructions,
source payloads/four calls/repairs unchanged. RED4failures/GREEN196tests4.19s.
Actual resident batch:35.662sRAG/35.058sSymbolic/52.967sHybrid;expected routes,typed
outcomes/full decoder hashes,1draft/1check/0repairs each. Output tokens462/540/859
vs642/824/1113prior. 11/12outputs one-line;Hybrid draft still pretty JSON530tokens.

Startup is separate:encoder25.131s,totalprocess26.408s. QueryEncoder already retains
its loaded model per application;batch reused app,not answers/student facts/vectors.
Each retrieval re-encoded/rechecked release. One-shot CLI still pays startup for
RAG/Hybrid;do not present warm-vs-cold as a pure prompt/runtime gain. Sub10s working
comparison aim remains unmet;4serial calls/decoded tokens dominate. No new API.

Fresh48-selection gate1898passed/66subtests89.01s,exit0. One independent final review:
no new P1/P2 code defect;setup docs reconciled auto placement and fixed24/CPU fallback.
Eight actual claims:7clear fits,1known Hybrid c2 documentary-only citation for an
executed prerequisite check. Canonical decision is correct,fallible checker still
accepts prose;human review pending. This is not accuracy/readiness evidence.
Raw:workspace/audit-evidence/p09-fast-replies-20261020/;report binds commands/hashes.

## Preserved evidence and boundaries

[Prior latency results](../2026-10-20-phase09-latency-results.md):24layer runs85Ã¢â‚¬â€œ148s,
original-message CUDA171.410s vs355.696sCPU;compaction-only gain not established.
[Composition delivery](../2026-10-20-live-backend-composition-results.md) preserves
actual baseline/failures/local RPC migration and sealed evidence.7227732/df99ac6
wire services,fab0225 snapshots input bytes,ab9aee9 bounds reads. No hosted changes.
Only fictional local release active;no real institutional sources/rules promoted.

[Phase07 audit](../2026-10-20-phase07-functionality-audit.md):core interpreter/router
present;two Taglish errors/no explicit post-retrieval reconsideration remain.
Current English cases do not validate Filipino/Taglish. Technical IDs hurt usability.
[Architecture audit](../2026-10-20-runtime-architecture-implementation-audit.md) and
[historical offline handoff](../phase-09-handoff.md) are preserved. Guarde0e86ea
prevents advancement while reopened checkpoint unfinished;valid/9/cannotadvance.

Thesis physical17Ã¢â‚¬â€œ18/39Ã¢â‚¬â€œ40,actual PNG/master12Ã¢â‚¬â€œ14 reconsulted;undergraduate,
read-only/structured-Prolog/unknown/source-gap rules preserved. Owner model root
workspace/MODELS reused. No weights/dependencies/locks changed or new downloads.
[Standing prompt decision](../2026-10-19-prompt-engineering-and-validation-decision.md):
no parameter training,one-week accuracy cap. Institutional/source/schema/privacy/
auth/activation holds remain. Phase10 separate/unstarted;no student API/deploy/push.

## Next action

Implement/test combined routing/style packet and evaluate existing15synthetic
multilingual variants before runtime selection. Retain separate rollback and
known Hybrid quality/source/release holds. No broad prompt/seed/model sweep.
