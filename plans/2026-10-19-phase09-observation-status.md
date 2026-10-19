# Phase09 actual-model observations

**Offline observation completed.** Initial120s baseline:nine timeout fallbacks,
zero validated explanations. Corrected RAG follow-up at240s:three validated
explanations,four source-supported claims and three appropriate language styles
by agent inspection. These separate denominators do not establish general accuracy
or readiness under the default deadline. [Final handoff](phase-09-handoff.md).

## Scope and reproducibility

Student capability: explain supplied documentary evidence and canonical prerequisite
checks in English, Filipino and Taglish without inventing policy or changing scope.
Evidence path: fixed Phase08 synthetic integration -> source cards -> constrained
draft -> optional support check/one repair -> host validation/rendering. This is a
generation component observation, not an actual routing/retrieval/Prolog evaluation.

Nine dev inputs: one RAG, one Symbolic and one Hybrid family in each language.
Sources, identities, rules and the Form Q service are fictional. Three language
variants per family are related observations, not nine independent policy scenarios.
The accepted75 institutional variants and held sources were untouched. No prompt
examples contain these cases; no training, download, dependency or release change.

Product e668e0e; run resumed from documentation HEAD6ff5635. Input SHA256:
1cb09a8a967b5502203ddf897c797800d6562409cb25811b7f188e87973e5c99.
Exact CLI: [module guide](../backend/bintanong_generation/README.md), timeout120.
Raw root: C:/Coding-projects/bintanong_workspace/audit-evidence/p09-generation-20261019/.
Command/log: actual-observation-cli.log; timestamps: observation-{started,finished}.txt;
prepared cases: synthetic-dev-cases.json; result: actual-observations.json, SHA256
e5ded53ddd60e16f3e14dd30abc7950251d72a094e2e15f6bd1f019a82e6123f.

Owner started the existing bintanong-p07-router-offline container after the earlier
automatic startup denial. No agent startup retry. Readiness503 resolved to ok.
Runtime image4b7be0376002b4450a357a109bab804093ff9251193cc75ed4ce0cb39953ff5c;
buildb11718-547208dca, Gemma4 E4B UD-Q4_K_XL,8192context,768output tokens,
temperature0/seed0, reasoning_effort=none,cache_prompt=false,parallel1,threads8.
Template SHA256:74a88f94c57c14e22dcdbe08e94127f42b87c6f584cb73838e73e32126f3f6b3.
Full props/container snapshots retained under that raw root. Model SHA inherited
from Phase07/08; no new model hash or hardware-performance generalization claimed.
Draft/support prompt and schema hashes remain in the original delivery manifest.

## Baseline results

| Case suffix | Draft attempts | Support attempts | Repairs | Final result |
| --- | ---: | ---: | ---: | --- |
| rag-en | 2 | 0 | 1 | timeout |
| rag-fil | 2 | 0 | 1 | timeout |
| rag-taglish | 2 | 0 | 1 | timeout |
| symbolic-en | 1 | 1 | 0 | timeout |
| symbolic-fil | 1 | 1 | 0 | timeout |
| symbolic-taglish | 1 | 1 | 0 | timeout |
| hybrid-en | 1 | 1 | 0 | timeout |
| hybrid-fil | 1 | 0 | 0 | timeout |
| hybrid-taglish | 1 | 1 | 0 | timeout |

CLI exit0 means the report was written, not that answers succeeded. Counts are
attempts initiated, including cancelled calls. Each language:0/3 answered,3/3 timeout;
each route:0/3 answered,3/3 timeout. Totals12draft attempts,5support attempts,3repairs.
No generated claims survived. The six supplied structured decisions remained equal;
the three RAG decision fields stayed null. The metric canonical_decision_preserved
is true9/9 including those nulls; it is not a student-answer accuracy score.

Agent inspection of all nine final texts found localized unavailable fallbacks,
no rendered positive eligibility result and no generated institutional claim. The
six structured outputs retain typed scope and rule citations. These are host
behaviors. Actual model prose support/language quality:0/9 final explanations to
assess; human language/support review remains pending. Injection resistance is not
measured by this benign batch. No institutional correctness or activation claim.

## Focused investigation

Server logs show approximately8generated tokens/second and request cancellations
at the shared deadline. Context lengths fit8192. RAG attempted repair before any
support check; the baseline report does not retain the rejected draft or error.

One completed diagnostic reused fictional-rag-en with unchanged prompt/schema/evidence
and decoding, a240-second observation window and intermediate response/error capture.
Raw script/log/report: trace-one-synthetic-case.py,one-case-trace.log,one-case-trace.json.
Both drafts were rejected for wrong_outcome:the first invented eligible,the repair
invented unknown; the supplied RAG decision was null. Calls60.431s/65.466s,total125.907s;
no support check. Longer time alone yielded repair_exhausted,not a valid answer.
Agent inspection found natural English and source-backed desk/fee wording in these
unreleased drafts; their fabricated decision fields still make them invalid.

## Narrow correction and follow-up question

The request grammar now binds decision_outcome to the host value (null for RAG;
the exact supplied outcome for structured decisions). The prompt explicitly states
the null case. Generic draft contracts,independent wrong-outcome rejection,source
evidence,repair limits and default120seconds remain unchanged. No route or decision
is inferred by keyword or hidden from the validator. RED3/GREEN60 generation tests;
the two negative nonconforming-transport cases already passed before this correction.

Context7 resolve/query consulted current primary
[llama.cpp server docs](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md),
[grammar limitations](https://github.com/ggml-org/llama.cpp/blob/master/grammars/README.md)
and [Pydantic schema docs](https://docs.pydantic.dev/latest/concepts/json_schema/).
Schema-constrained sampling and schema customization support this boundary; skipped
constraints and semantic errors still require host validation and actual runtime checks.

The bounded follow-up asked whether the same three RAG language variants preserve
the absent decision and yield supported,appropriately styled explanations after
the correction. It used one batch at240seconds per candidate. No all-nine repeat,
new questions or tuning on accepted institutional/final families occurred.

## Corrected RAG follow-up

Product37c8d69; same model/runtime/decoding,source evidence and original wording.
240s observation deadline; default120s remains unchanged. Raw input:
rag-followup-cases.json,SHA256
84688e02858d7e03d7ab6d61534724e233363a4e717f40ffc53ef2df3e5836ce.
Raw result:rag-followup-observations.json,SHA256
4180d622f11ae8466c5226ee02f57e332bf754148406886d7279bf0bf9563784.
Command:the same module CLI with those input/output names and --timeout240;
rag-followup-cli.log exit0. Wall time249.815s for all three sequential cases,
including imports/preflight/output. No per-case latency measurement or120s pass claim.

| Requested style | Answered | Draft/check attempts | Repairs | Agent support/style assessment |
| --- | ---: | --- | ---: | --- |
| English | 1/1 | 1/1 | 0 | One supported desk-submission claim; natural English |
| Filipino | 1/1 | 1/1 | 0 | Two supported submission/40-token claims; predominantly Filipino |
| Taglish | 1/1 | 1/1 | 0 | One supported submission claim; natural mixed phrasing |

All three decision fields stayed null. All four claims mapped to the supplied
document card and its physical1/fictional/1 locator. No new office,fee,deadline,
permission or student fact appeared. Agent manual assessment is independent of the
model checker's positive verdicts,not an independent human or school assessment.
Raw human_language_review/human_claim_support_review remain pending; raw
actual_model_accuracy remains unmeasured. One source family/one variant per language
is insufficient for language-wide accuracy or a calibrated safety claim.

Post-correction manifestcd770d526c8b51632e46b5dd9078400fd464d2b81f5b1a7bd450c3f3dbf78743
binds product files,inputs,base schemas and request schemas at run start. Draft
prompt36f84e98c384e93543d32d5e537eb1939f92e25e8ba35e356f6625974e12f351;
support prompt unchanged. Request RAG schema
1d386f8d654fdb9af5a34fcc9c2f822e7f1a908937d4aa43090f092134035e76;
the generic draft schema remains unchanged. No equivalent performance comparison
is possible because both correction and observation deadline changed.

The bounded question is resolved; stop this diagnostic. Default-budget latency,
successful structured/Hybrid model explanations,adversarial model behavior and
independent human assessment remain later evaluation/release work. Candidate code
and regression exits are complete; institutional source/loading/privacy/release
holds remain. No universal correctness,student service or deployment claim.
