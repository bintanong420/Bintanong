# Question-coverage experiment results

20October2026;Phase09 active. [Plan](2026-10-20-question-coverage-plan.md),
[standing timing recommendation](../Context/response-time-recommendation.md),
[measurement boundaries](2026-10-20-response-time-measurement-contract.md).

**Decision:keep covered unselected.** Prepared multilingual probes passed,but the
single actual-service multipart question exposed a false complete verdict. Default
scoped/canonical/separate remains. No further inference or prompt correction.

## Implementation and relevant evidence

Plan6eca2ac/product040c27d introduces explicit covered profile with ready RAG
CoverageReview:required release binding,question_coverage plus every existing
claim-support/language/scope check in the same review call. Complete+supported
permits release;partial/none/uncertain returns localized insufficient_evidence/
question_uncovered with no claims/citations. Other invalid/support failures retain
one repair and the same evidence/deadline. Coverage resets for each draft;optional
host observation records reviewed attempt and combined review seconds. Hybrid keeps
the existing documentary checker and host result;Symbolic remains host-rendered.
Per-case hashes distinguish effective review prompts;historical fields stay null.

This investigates supported claims answering the wrong student question after a
misroute. Full passages/provenance,scope/version/unknown/privacy boundaries remain.
The existing semantic router,Prolog and RAG are unchanged. No source truncation,
checker removal,extra classifier call,cache,training,downloads,dependency/DB changes.

Primary research distinguishes answer relevance from faithfulness:
[ARES,NAACL2024](https://aclanthology.org/2024.naacl-long.20/) and
[Ragas](https://arxiv.org/abs/2309.15217). This supports separate quality dimensions,
not the accuracy of this model/prompt. No framework or judge training is adopted.

## Actual prepared observations

Reuse the3normalRAG and3forced structured questions from the prior guard experiment
unchanged,including English/Filipino/Taglish. Prepared evidence is supplied directly;
these are generation software probes,not semantic-router or institutional accuracy.

| Case group | English generation/review seconds | Filipino | Taglish |
| --- | ---: | ---: | ---: |
| Normal document question |21.917 /6.729|23.228 /6.626|22.557 /6.620|
| Forced RAG course-check question |23.830 /6.984|24.797 /7.166|23.921 /6.728|

Normal3:answered,complete,9source-supported claims,appropriate final styles by
author/independent reviewer. Forced3:none,localized insufficient evidence,no claims,
citations or decision.12physical calls,zero repairs/errors/timeouts. All forced
reviews also mark within_scope=false;there is no ablation proving which judgment
caused rejection. The unreleased forcedFIL draft mixes styles although the checker
marks language_appropriate=true. This is a remaining checker limitation,not a
released-answer language error. Prepared saved-output gate6passed0.30s.

## Actual-service failure and independent finding

Original unchanged question:**Where do I submit Form Q and what is its fee?**
Full retrieved source includes submission at Synthetic Student Desk and **40tokens**.
The final answer contains only the location claim. Review incorrectly returns
complete/supported/language=true/scope=true;host releases answered/validated.
Fee is absent from proposed claims even though present in its cited source.
Citation payload content does not fill an omission in the visible answer.

Independent whole-change review confirms one P2:multipart answer completeness
false positive.243focused tests5.18s pass;no additional actionable deterministic
finding. Review waited for model observations to finish before testing. Receipt:
raw reviewer/assessment.md and focused-tests.log. No reviewer inference/re-review.

Actual saved-output regression reproduces **1failed/6passed0.31s**. An initial
loose numeric assertion falsely passed because an evidence hash contained40;
corrected assertion checks40tokens in claim text. Both receipts retained;the
corrected failure is authoritative. Mechanical test success cannot fix semantic
failure. Two anticipated default-promotion tests were RED before review;no
promotion code was applied. Replacement tests lock scoped default and isolate
covered. Reviewer P2 stays open in the unselected experiment. No correction sweep.

## Timing boundaries and recommendation

Actual-service outer backend27.265337s/inner pipeline27.265130s,4physical calls,
1draft+review,zero repairs. Combined review5.342653s is already nested inside the
request. **This is an incomplete-answer duration**,not supported complete-answer
latency. Do not promote it as meeting a performance objective or accuracy gain.

Separate script-entry-to-ready24.184131s:imports/identity0.833315s,build/encoder
warmup23.288540s,initial verified Supabase reads0.062273s. Local127.0.0.1:54321;
model/Docker/Supabase already running. Readiness is multiple release verification
reads,not an isolated TCP/TLS handshake. Interpreter startup before script entry,
complete cold-system boot,browser/API/network/queue/hosted overhead unmeasured.
No nested-span double counting,p50/p95,controlled speedup or student wait acceptance.

Owner asked to preserve the earlier research recommendation:commitea749da adds
Context/response-time-recommendation.md and AGENTS pointer. Proposed15-20s warm
student-visible validated response,preferunder10s short questions,and conditional
20-30s complex Hybrid remain **unproven targets**,not an approved SLA. Retain every
necessary check and reject quality regressions;undergraduate status does not prove
an acceptable wait. Startup/connections/Supabase/network/browser metrics remain
distinct. That record links seven primary sources and the measurement contract.

## Verification and recovery

Initial focused RED32;GREEN187tests2.96s. Expanded generation/runtime/docs gate
841passed5.20s,exit0. New profile's nonready/Hybrid/Symbolic/private-ID/release/
repair-reset/deadline/cancellation/concurrency/per-route prompt metadata paths pass.
Final explicit54-selection gate and integrity seal pending. No institutional75-case
evaluation or owner content/style approval. No semantic-success claim from mocks.

Raw:workspace/audit-evidence/p09-question-coverage-20261020/. Pre-inference manifests
bind code040c27d,original input hashes,observer scripts and runtime props. Source-
inference/ retains exact bytes;full messages/schema hashes/usage/timings/failed
outputs retained. Existing CUDAb11723-31288c9c6/context8192/output768/temp0/seed0/
reasoningnone/cachefalse,35/43GPU layers,owner workspace/MODELS. No model rehash.
Observation budgets240s infer/generation,300s stage/600s fullrequest;shipped
120s infer/generation/stage,180s request unchanged. Existing Python3.13 readiness
interpreter,-B pytest -q -p no:cacheprovider;ignored workspace TEMP/TMP/basetemp.

Thesis17-18/39-44,actual routing PNG/master3/11/12.4/13/14 reconsulted. Undergraduate/
read-only/structured-Prolog/unknown/source-gap boundaries agree. One-week prompt cap
and all institutional/source/privacy/auth/hosted migration holds persist. Guarded
experiment stays separately rejected. Upstream2Taglish style errors/opaque IDs remain.

Next recovery design:represent question requirements before drafting and bind each
to an actual claim/evidence or explicit unavailable result,with host all-item checks.
Requirement extraction can itself omit a question part;validate that separately.
This is a design question,not an implemented guarantee or authorization for another
model sweep. Phase09 remains active;no Phase10,push,merge,deployment or activation.
