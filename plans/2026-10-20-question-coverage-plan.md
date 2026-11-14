# Question coverage implementation plan

20October2026;Phase09,p09,baselineea749da. Execute inline with executing-plans,
focused TDD and one fresh independent whole-change review.

**Goal:** do not release a source-supported answer that misses the student's
actual question. **Capability:** withhold an unrelated documentary answer when a
misrouted request needs a structured result that was never supplied.
**Evidence path:** existing semantic router,RAG/Prolog and scoped authoring;judge
question coverage alongside source support in the existing RAG review call.
**Exit advanced:** master12.4/13.2/14.2 decision scope and validated answer relevance.
**Question:** does reviewing the actual proposed answer catch the saved language
failures while retaining supported document answers? No new institutional cases.

## Evidence and design

Saved [guard results](2026-10-20-post-retrieval-guard-results.md) show source-entailing
FormQ claims answering a different course-check question. The pre-draft classifier
and one correction failed;do not repeat either. Existing support validation checks
claims but has no required whole-question coverage field. Source truth and answer
relevance need separate acceptance decisions.

[ARES](https://aclanthology.org/2024.naacl-long.20/) evaluates grounding and answer
relevance separately and uses human annotations to mitigate judge errors.
[Ragas](https://arxiv.org/abs/2309.15217) likewise separates retrieval/generation
quality dimensions. These support the distinction,not this prompt's accuracy or
an imported threshold. No framework,training,synthetic training data or judge
fine-tuning is adopted. This design remains an inference-time candidate.

Add explicit explanation_profile=covered,initially unselected. It shares scoped
authoring/host Symbolic behavior. For ready RAG only,replace the existing review
wire contract with CoverageReview(SupportReport):release_id and required
question_coverage=complete/partial/none/uncertain,plus all existing claim verdicts,
language and scope checks. The original question and proposed documentary claims
are untrusted data. Cited full sources stay individually bound to each claim.
State that no structured result is available for RAG;question assertions do not
supply one. No rule result/student facts enter the documentary support basis.

Only complete coverage AND the existing valid support checks can release an
answer. A valid noncomplete coverage result immediately returns a fixed localized
insufficient-evidence response,validation=question_uncovered,no claims/citations,
no reroute or structured decision. Invalid review/schema/release and support errors
keep the existing one-repair policy and shared deadline. Tool/time errors remain
temporary unavailability. Reset coverage on a new draft;record the reviewed draft
number and review seconds in an optional host CoverageObservation. Historical/
other-profile reports retain null. Guarded remains isolated;do not combine probes.

Hybrid keeps its existing separate documentary checker and host structured result;
Symbolic remains host-rendered. This bounded change does not claim Hybrid question
coverage or universal semantic recall. No extra model call,checker removal,source
truncation,keyword routing,cache,downloads,DB/dependency changes or parameter training.
Owner accuracy-first and one-week cap,undergraduate/source-gap/privacy/release holds
remain. The durable [timing recommendation](../Context/response-time-recommendation.md)
is preserved;review seconds are nested in the pipeline,not added twice.

## Tasks and interfaces

1. [x] Tests/test_generation_coverage.py RED,then minimal GREEN:coverage.py strict
   report/schema/messages;scope.py shared documentary review payload without changing
   old prompts;contracts.py optional observation and failed-coverage invariant;
   generator.py covered profile and review gating;render/validation localized
   withholding and final scope;runtime settings/report/CLI explicit profile.
   Cover all languages,complete+supported,partial/none/uncertain,no answer repair
   after valid noncoverage,claim-support failure repair with reset,malformed/extra/
   duplicate/wrong-release reports,deadline/cancellation/concurrency,full-source and
   private-ID boundaries,canonical decisions and non-RAG/control/legacy bypass.
2. [x] Evaluation effective per-case review prompt hashes (covered RAG differs
   from unchanged Hybrid);top-level covered support hash null with explicit coverage
   policy hash. Report pending human question-coverage review separately. Verify
   focused regressions,commit candidate;keep scoped default pending quality.
3. [x] Once:reuse the existing3normalRAG+3forced structured RAG questions and
   evidence from prior experiment,unchanged wording. Run full prepared generation
   with covered,inspect every claim/style/coverage/outcome and report time/calls.
   Expect3documentary answers and3safe withheld results;an operational error is not
   semantic success. Stop if quality fails;no prompt/seed/budget correction sweep.
   If quality passes,run only the existing English actual-service RAG request once
   using resident encoder/local Supabase and explicit covered. Record outer/inner
   request,review and process/readiness boundaries. Do not rerun unchanged service
   Symbolic/Hybrid. No browser/full-cold or institutional accuracy claim.
4. [x] Fresh independent whole-change review after observations;one TDD fix pass
   for important findings. If quality/review pass,RED default-selection tests then
   select covered/canonical/separate for the offline candidate. Otherwise keep it
   unselected. Preserve legacy historical report defaults and old experimental
   evidence. Run explicit54-selection regression gate,new dated results,compact
   progress/checkpoint/index and integrity receipts. Phase09 remains active until
   its applicable exit is separately reconciled;no Phase10/push/merge/deployment.

Existing Python3.13 readiness interpreter,-B pytest -q -p no:cacheprovider;external
TEMP/TMP/basetemp under workspace/audit-evidence/p09-question-coverage-20261020/.
Reuse CUDA18088,owner workspace/MODELS and existing240s observation budgets;
shipped120s inference/generation/stage and180s request unchanged.

## Review focus

- Correct claims on the wrong subject must not be released as answered.
- Whole-question coverage cannot substitute for source support or permit personal
  conclusions without the corresponding typed structured result.
- A stale successful review cannot apply to a replacement draft or another request.
- Hybrid scope must not be judged incomplete merely because its host-owned part is
  absent from the documentary checker;this profile's coverage claim is RAG only.
- Reports must identify actual review prompt,failed attempts and timing boundaries.

## Actual quality outcome and ruling

Product040c27d:prepared6cases pass (3answers/9supported claims;3localized withheld
results),12calls/zero repairs. All negative reviews also within_scope=false,so this
does not isolate coverage's causal contribution. Actual-service RAG then fails:
question asks location AND fee;only location generated;review falsely complete
despite full source including40tokens. Independent reviewer confirms one P2 and
243focused tests5.18s. Unreleased FIL draft mixes language while checker says true;
document as a residual judge limitation. No supported complete-answer timing claim.

Reviewer P2 remains open in explicit covered;do not select it. Stop rule applies:
no prompt/seed/budget correction or further inference. Two anticipated promotion
tests were RED before reviewer finding;promotion was never implemented. Replace
them with rejection/default-isolation regressions. Keep scoped/canonical/separate
selected. This is quarantine,not a semantic fix;multipart completeness remains
unresolved. Final task is review/result integrity and explicit regression delivery.

Ruling:one aggregate model coverage field cannot prove all requested parts were
answered. Next recovery design must expose question requirements separately from
answer claims and bind each to actual evidence/withholding. That design itself
still needs validation that no requirement was omitted;do not call a checklist a
guarantee or substitute keyword routing. No new model experiment starts here.

Delivery:rejection/isolationeb9ceb9;focused844pass5.18s;explicit54-selection gate
2086passed/66subtests91.14s,exit0.103raw files sealed and verified. The experiment
is delivered with an open semantic P2;required capability and Phase09 remain active.
