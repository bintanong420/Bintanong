# Phase09 generation review and correction

Fresh read-only reviewer inspected120fb3d..2f9ec1d against master14, the Phase09
plan and orchestration/Context research. Existing39generation tests passed1.26s.
Five P2s reproduced; all accepted after technical verification, with no deferrals.

| Finding | Correction and regression |
| --- | --- |
| Held Hybrid could print eligible/ineligible conclusion | Render canonical conclusions only when integration and final answer permit them; preserve observation as typed data without positive fallback text; conflict/release/uncalibrated matrix |
| Target/course/curriculum/version context dropped | Carry safe bound input name/value pairs, DecisionScope and bundle through model payload, final typed context and renderer; strip private fact_ref; distinct-target regression |
| Claim-to-source mapping lost at render | Preserve typed claims and inline evidence markers next to each claim; validate final mappings/context; two-source regression |
| Hybrid could answer with rule-only prose | Require an actual document-card reference for RAG/Hybrid; rule-only negative/document-positive tests |
| Nested JSON raised uncaught RecursionError | Bound response bytes and treat parser recursion as invalid draft/checker output within the single repair budget; nested40,001-byte regressions |

Author also added unexpected-transport-error coverage:fixed tool_error fallback
without exception body. Focused RED10failures/35deselected1.24s; GREEN55passed1.46s,
exit0 across five generation files, including evaluator mechanics. No second
independent review or actual model quality judgment is claimed after corrections.
Raw workspace/audit-evidence/p09-generation-20261019/review-red.log/review-green.log.

Evaluator test-order correction:an initial uncommitted helper was removed before
observing its six missing-module failures, then implemented and verified with the
same focused suite. evaluator-red.log retains the observed failure. No prior helper
was committed and no real inference was run by the evaluator tests.

These are software guard checks, not proof of entailment/language accuracy. The
same-model prose checker remains fallible; the inherited namespace scanner is not
general PII detection. Institutional/source/privacy/release gates remain unchanged.
Actual-model observation is NOT RUN because automatic approval review rejected
starting the existing offline container with only "blocked by policy" provided.
