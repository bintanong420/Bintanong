# Scoped explanations: selected offline candidate and timing boundaries

20 October 2026;Phase09 active,p09. Plan2660f6f,implementation1563ae8,
selection/provenance correction9d4f32d. [Plan](2026-10-20-scoped-explanations-plan.md)
continues the previous saved scope failures. Accuracy stays ahead of speed.
No Phase10 advancement,institutional activation,student API,push or deployment.

## Change and selection

The selected default is now **scoped explanations,canonical references,separate
LLM routing/style**. Generator,RuntimeSettings and runtime CLI select scoped;
legacy remains an explicit developer comparison with known scope limitations.
The rejected short-ID candidate stays separate and cannot be combined with scoped.
Historical RuntimeRun records missing explanation_profile still default to legacy;
new runs explicitly record their selection,so older evidence is not relabeled.

The host renders the typed decision/conditions/dependency list. Ready pure Symbolic
answers contain no new LLM paraphrase;they still execute actual routing/style and
Prolog,then host validation. RAG/Hybrid generate only documentary explanations via
a distinct strict wire contract,with every reference bound to a documentary card.
Decision fields are copied by the host. The checker sees each claim's own full
cited document cards,without borrowing a canonical result to justify an unstated
procedure purpose. Full documentary text/metadata and host rule provenance remain.
Unknown/conflict/held states,privacy/source/release guards,deadlines and bounded
repairs are preserved. No keyword routing,weights,dependencies or database changes.

## Actual quality observations

Reused the existing9prepared fictional dev cases:3routes in English/Filipino/
Taglish. The3Symbolic outputs are host-rendered,not LLM generation accuracy cases.
The6document-generated outputs contain18claims;agent and independent review find
all source-supported,within scope and appropriately styled. These are tiny related
fictional families,not institutional multilingual accuracy or calibration.

| Prepared route | en,s | fil,s | Taglish,s | Calls per case |
| --- | ---: | ---: | ---: | ---: |
| RAG generation/check only |22.066|22.315|21.984|2|
| Symbolic host generation stage only |0.003|0.003|0.003|0|
| Hybrid generation/check only |21.132|22.323|21.975|2|

The earlier Taglish enrollment-eligibility paraphrase is absent because structured
wording is host-owned. The earlier Hybrid enrollment purpose is absent;the new
explanation retains the generic service. RAG English says submitting Form Q is a
necessary action to complete the service;neither reviewer reads it as saying that
submission alone guarantees completion. Source purpose/fee/test-only status remain.
Positive automated checker results are not the sole basis of this assessment.

After that gate,3existing English questions ran the actual composed services:
local LLM routing/style,SEA-LION/PostgREST/pgvector where required,Janus/Prolog
where required,integration,generation/checking where applicable and final assembly.
All3answered with expected routes/canonical outcomes. Agent and independent review
find the4generated documentary claims supported. Hybrid now states the documented
prerequisite requirement separately from the host's actual checked result;it does
not use documentary text alone to assert the student's executed check succeeded.
No repairs were used in either batch:12prepared-model calls plus10runtime calls.

## Complete warm backend timings

| Route | Prior selected inner pipeline,s | New inner pipeline,s | New outer backend request,s | New LLM calls |
| --- | ---: | ---: | ---: | ---: |
| RAG |35.662|29.915087|29.915279|4|
| Symbolic |35.058|16.999259|16.999440|2|
| Hybrid |52.967|38.884336|38.884462|4|

Each is one observation,not p50/p95 or a controlled speedup distribution. Original
questions/spec,separate routing,canonical IDs,CUDA build/model/sampling were reused.
Prompts/output content and Symbolic rendering policy differ. Symbolic removes
redundant generated prose by design;RAG/Hybrid keep their separate support checks.
No answer/student-fact/query/prefix cache or scripted inference was substituted.
All required retrieval/Prolog paths still execute. No sub10s or general15–20s claim.

The new outer timer surrounds the app.run call,including per-request setup. The
inner timer surrounds AnswerPipeline.run after those objects are constructed.
Both include request-time LLM connections/template/tokenization,Supabase reads and
any reconnects,required embedding/retrieval,Prolog worker startup/execution and
validation/repairs. They exclude process/service startup and browser/API time.

This process-to-readiness observation,with model/Docker/Supabase already running:

- Imports/identity preflight:0.713s.
- Application build plus encoder verification/load/first encode:24.930s.
- Initial Supabase release-readiness reads:0.312s,within the startup total;this is
  not an isolated connection-handshake benchmark.
- Process-to-ready:25.955s total. Supabase endpoint is localhost54321.

These costs must not all be added as independent extras:readiness is included in
the startup total. A warm query does not reload resident weights. A complete cold
system/model/Docker boot,first user request under that condition,hosted Supabase
network,queueing,student API/browser and upload/OCR have **not been measured**.
The [measurement contract](2026-10-20-response-time-measurement-contract.md) records
the owner's follow-up and their appropriate later-phase metrics. The proposed
15–20s target is student submission to visible validated answer,not backend alone.
Current observations do not establish that target or local student acceptability.

## Verification and review

Scope TDD RED30/GREEN160tests3.22s;expanded35scope tests plus product/docs gate
758passed4.29s. Default selection RED3. Independent review found one P2:evaluation
reports always labeled runs with legacy prompt hashes. Reproduced RED4;fixed
effective profiles/hashes and host-only/documentary/legacy generation-mode labels.
Combined focused gate172passed3.16s;reviewer independently172passed3.19s. No open
P1/P2 finding in its consolidated final assessment. Today's raw observations use
exact message/schema/source hashes and were unaffected by that report-label bug.

The first runtime observer attempt had a copied keyword typo and failed before
application construction or model inference. Corrected once,with failed script,
log and preflight receipt preserved;the full3-route run is the corrected batch.
Final explicit52-selection gate2008passed/66subtests89.45s,exit0. Raw exact command
is verify-regressions.ps1,output final-regressions.log. Delivery manifest seals
94files,all verified;SHA256
b85805aac9d79c987339874c96a4f46da60e7ceecd8693272b37b5bc45b081b9.
Later delivery-doc logs are separate. Compact recovery state is in the checkpoint.

## Recovery and limits

Raw root:workspace/audit-evidence/p09-scoped-explanations-20261020/. Prepared and
runtime-corrected pre-inference manifests bind inputs/code/props. Per-case traces
preserve messages/output/usage and schema hashes;assessment.json and
reviewer-final-assessment.json record bounded quality reviews. Generation/runtime
files were not overwritten. No owner language/support review is claimed.

Fresh actual runtime metadata:b11723-31288c9c6,8192context,768output,temperature0,
seed0,reasoningnone,cache_promptfalse,inference/generation240s,stage300s,request600s.
Existing image/model/template/35of43GPU placement reused;no pull/restart/tuning or
fresh GGUF rehash. Owner workspace/MODELS weights remain unchanged. Python3.13.7.
Exact digests/recovery are retained in the preceding handoff and current raw seal.

Source/institutional/auth/privacy/hosted-migration gates remain. No75-case evaluation
or broad source accuracy claim. Prior upstream2Taglish style errors and absent
explicit post-retrieval reconsideration remain. Next:design a bounded post-retrieval
decision-withholding check for misrouted RAG requests requiring structured decisions,
preserving LLM semantic routing and source/unknown boundaries before Phase09 exit.
