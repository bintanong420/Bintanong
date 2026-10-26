# Corrected78-chunk candidate: runtime and query results

Code `d72b88f` passes its software tests;the six-query answer-quality gate did not pass.
The corrected78-chunk release stays inactive. No pages,topics,chunks,vectors,prompts or hosted
release/active-pin changes in this runtime-check increment. [Plan](2026-10-26-corrected-candidate-runtime-checks.md) ·
[Source correction results](2026-10-26-hosted-chunk-correction-results.md).

## Delivered runtime fixes

- Optional trusted package subject_context_budgets now reaches the existing engine and binds into
  the root research release identity. Absent-key legacy defaults stay unchanged;invalid/null maps
  reject. Budget-only changes retain the same symbolic rule-bundle version and source membership.
- Local PackageStorage follows transitive required companions through cycles,within the eligible
  source version/audience/chunk/version filters,including companions below the ranking threshold.
  This corrects its local dependency behavior to match the existing hosted SQL;SQL itself unchanged.
- Previously reviewed Charter1–4 sequence was carried into a separate validated runtime claim-register
  overlay for visible pre-enrollment instructions. Original78source artifacts/receipts/vectors unchanged.
  The overlay preserves the existing source-order guard;it is not a new procedure or wording approval.

## Verification

Budget RED12 failures;initial GREEN61. Independent review found null disabling legacy budgets;
edge RED2 confirmed that,plus3closure failures(cycle/transitivity,version,audience). Version-filter
RED1 separately observed. Final focused109passed +9subtests,3.39s;independent61passed,no important
review finding remaining. Pre-existing config/entity-hint local parity was not expanded in this patch.

Full frozen d72b88f suite:6821passed +1595subtests,6skipped,2xfailed,6warnings,1341.43s(22m21),exit0.
Shared Python3.13 `-X utf8 -u -B -m pytest -q -p no:cacheprovider tests/`,external basetemp/storage
evidence. The earlier run was interrupted94% without a result;do not count it as a pass or failure.
Hidden helper restarted once,then ran the six cases only after success. No model case was repeated.
No installed lint/formatter claimed;diff/link/phase-state checks are separate documentation checks.

Actual composition with saved-vector component probes(no model/encoder inference,not natural-query
accuracy):fraud3records2382tokens/3072;Charter6records3816/4096;grading4records1866/2048;fee3records
1552/2048;canonical cheating+shared measures2records1301/3072. All present without context-budget
or missing-neighbor gaps. Development calibration marker retained. The old cheating source variant
remains deliberately unassigned in runtime claims;canonical II.7a is the selected answer source.

## Six exact queries:one attempt each

All routes RAG;3answered/validated,3insufficient_evidence/control_fallback,0exceptions. These status
counts are not a quality score. Author reading finds material gaps in every case against the frozen
expectations;neither source corrections nor a positive ordinary review establish complete answers.

| Case | Result | Evidence/quality finding | Inner pipeline seconds |
| --- | --- | --- | ---: |
| removal-en | insufficient_evidence | Router chose grading_scale instead of grade_completion,including8irrelevant numeric mappings. Only3scale rows emitted;incomplete_context. Reviewed re-exam passage never reached the answer. |40.417|
| inc-period-taglish | insufficient_evidence | Subject omitted;needs_subject/subject_hint_required. Remaining-original-INC-period evidence not selected. |14.723|
| fraud-en | answered/validated | Router selected admission+registration and retrieval supplied all3related records. Draft answered only registration;admission penalties/overlap warning omitted. Ordinary review accepted the incomplete part. |34.508|
| procedure-fil | answered/validated | Correct checklist+four client steps in reviewed order;all6records retrieved. Cutoff quoted/referral preserved. Step1agency actions omitted;step2“i-enlist…ito” blurs student versus form;25-versus20-minute discrepancy absent. |61.569|
| fee-taglish | answered/validated | Correct370.37/hour,54hours/20,000example and unknown individual-charge referral. Same host-written block repeated for two interpreted parts;currentness limitation not surfaced. No new arithmetic. |14.952|
| cheating-en | insufficient_evidence | Selected unrelated “penalty type for two weeks” gap rather than examination-cheating claim;requested_claim_not_established. Relevant source records exist but the requested claim was not established. |10.758|

Exact questions/expected claims are frozen in the plan and raw cases.json.16model completions total,
canonical references,768output cap,prefix reuse,greedy/seed0/current resident model;no prompt sweep,
thinking experiment,retry rescue or default change. Three fallbacks safely withheld unsupported
answers,but are capability failures because the relevant reviewed source is available.

Fraud trace:requested II.8a+II.8b;3passages include34/45/46. Only registration claim was drafted,and
the ordinary review returned part “answers” plus supported verdict. Missing admission coverage is
therefore a generation/review completeness gap,not a missing companion chunk or kNN truncation.
Charter trace confirms6passages and explicit source_ordered record coverage;order guard works,
but sentence meaning and source-limit disclosure still need separate validation.
Independent source-trace review confirms this quality assessment. Cheating did retrieve the exact
exam-cheating row and shared measures;the misselected claim caused refusal. Fraud generation input
contained both admission rows/progression/overlap warning;whole-part review still accepted a single
registration-only claim. Fee output was host-rendered(router+style calls only),so no model-answer
review checked that duplicated block. Prioritize declared-claim/limitation coverage and semantic
routing,then procedure field fidelity/duplicate slots;no new chunk/budget sweep justified.

Fee trace has2parts both assigned printed three-lecture-unit example;host reply emits same rate+
example block twice. Duplication is answer composition,not duplicate lecture_hours data.

## Timing and scope

10.758–61.569s warm resident-model inner pipeline observations include routing/retrieval/generation/
review as applicable. Model-service queueing unmeasured within calls. Encoder/composition startup
excluded. No Supabase/API/browser/student end-to-end timing or15–20sSLA achieved claim.
Observations used the sealed local package;hosted active19/draft80/corrected draft78 unchanged.
Long-tokenizer warning670>512 arose while counting context;no silent query truncation or encoder
exception occurred in these completed cases. No uploads/private records/browser flow exercised.

## Next bounded work

Source data/group capacity is verified. Work from the saved exact traces rather than more source
chunks or repeating this battery:fix router selection for removal/INC/cheating;enforce requested
admission+registration coverage and overlap warning;deduplicate same-subject host fee blocks;preserve
service action meaning/limitations. Each behavior fix requires a failing regression before code.
Do not activate corrected release or integrate as quality-approved on these results. Wider Phase11
query/style/UI gates remain;no phase completion or public/institutional authority implied.

## Recovery and artifacts

Ignored root:workspace/audit-evidence/p11-corrected-runtime-20261026/. RED/GREEN logs,component check,
full-suite-interrupted.log,full-suite-restart.log/full-suite.exit,runner/seal,raw requests/responses,
per-case integration/answer files,results.jsonl and completion.json retained. No jobs still running.
Root release:`release-offline-research-set-7d01d8dbae838128`.
Runtime order-register SHA256:`1dba7278b673c560d89a226c62637e2339fcc4c7aeecfe3e4fa8e4b22742b200`.
Cases SHA256:`1b7ccdc9bf4e9b7e528ff36bd2a695839adbeaa0478c601193da22a37adde6a5`.
Embedding set remains:`cb7ac3a56b94bdb9ced8f8bd9c012b3cff2adf1e3e761347acbe147ce3c38845`.
Retain code d72b88f and full results;do not repeat successful suite without new behavior changes.
