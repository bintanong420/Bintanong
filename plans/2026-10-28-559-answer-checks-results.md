# Current 559-chunk candidate: bounded answer-check results

**Quality gate FAILED.** The inactive559package stays inactive;active78/hosted releases unchanged.
[Frozen plan](2026-10-28-559-answer-checks-plan.md);code8386501+86d9e6d. Development probes,one
attempt per case,author-read against the printed source;not a formal evaluation or accuracy rate.

## Component evidence (passes)

Per-subject budget map (54subjects,largest closure rounded up to1024,max8192) reproduces the active
academic_misconduct3072/pre_enrollment4096. Saved-vector component check through real engine/
PackageStorage:all240claim reviews pass;238complete contexts with no gaps,2intentional not-stated
claims refuse;max7864E5. No encoder/model inference,no hosted call.

## Run 1:default composition — routing overflow on every case

All11cases `temporarily_unavailable` in0.7–2.2s:the first routing call carried the full145-topic
detailed menu (70.7k-character system prompt) and the transport preflight refused `context_overflow`.
The compact selector (f726e72) existed only as `Router(topic_selection=True)`;nothing above Router
could enable it. Retained as evidence in `cases/`.

**Fix 86d9e6d:** `Orchestrator(topic_selection=False)` passes the existing opt-in to Router (both
profiles);default unchanged. RED4fail/1pass -> GREEN5;focused routing/orchestration/runtime/API748pass.
The full project suite for86d9e6d did not complete:the host stopped it for low system memory
(not a test result);rerun before relying on this change beyond the focused coverage.

## Run 2:topic selection enabled (same frozen cases)

| Case | Result | Author reading against printed source |
| --- | --- | --- |
| good-moral-en | temporarily_unavailable | Selector/router/retrieval correct (2parts,10records). Draft exceeded768output tokens (`truncated_output`);long procedure answers do not fit the output cap. |
| library-card-taglish | insufficient_evidence | Router requested the source-limit text ("one-photo…unresolved") as the claim for both parts;not a printed claim,so retrieval refused. |
| entrance-health-fil | abstained | Selector offered both;router chose handbook policy (2records),not the Charter procedure. Repair still missed record coverage. |
| leave-en | answered | Correct:writing before semester,reason/period<=1year,Chair/Dean,maternity1month. Omits "no readmission" and Dean->Registrar notice;duplicate parts. |
| shifting-taglish | insufficient_evidence | Selector correct;router returned `clarify` with zero parts for a clear question. |
| cross-enroll-en | answered — **inaccurate** | Joins conditions a–e with OR ("not major…OR same description"),so a major subject could appear allowed;also labels the out-going conditions as "from other institutions". Review accepted it. |
| discipline-en | abstained | Repair overflowed (call5);new retry without previous draft fit (6853in) — fix exercised live. Second draft still missed record coverage;safe abstention. |
| hybrid-bscs-en | answered — **partly inaccurate** | Route Hybrid;Prolog ineligible (CC4/L not completed,CC3/L unknown) correct. Document part repeats the OR reading of conditions. |

Regressions:cs-cc5-failed-cc4-en (Symbolic ineligible) and criminology-corequisite-tl (clarification,
unknown) **match**. grade-excellent-taglish **regressed**:selector chose grade_solicitation,not
grading_scale;answered on active78,insufficient_evidence here.

4/8answered,but2of those contain a material condition-logic error that the same-model review
accepted. Safe refusals are capability failures where reviewed source exists. 15.5–99.2s warm inner
pipeline per case (selector adds a call);no student/browser latency claim.

## Findings for regression-first fixes (ordered)

1. **Condition semantics:** cross-enrollment a–e rendered as any-of. The source does not establish
   all-of/any-of explicitly for every item;answers must not assert OR. Highest priority:wrong advice.
2. **Selector recall:** grading_scale missed (regression);entrance health Charter procedure not chosen.
3. **Router claims:** a source-limit description offered/accepted as a requested claim;`clarify`
   with zero parts on a clear shifting question.
4. **Output budget:** full procedure answers (good moral,7steps) exceed768output tokens.
5. **Coverage:** two repairs still miss required procedure records;leave answer omits two sentences.

No activation,default,hosted or source change follows. Each fix needs a failing regression first;
do not repeat this battery as a sweep.

## Recovery

Ignored root:workspace/audit-evidence/p11-559-answer-checks-20261028:budgets,component check/result,
`cases/` (run1),`cases-selector/` (run2:binding,per-call requests/results/failures,integration,
answers,results.jsonl,completion),logs,RED/GREEN/focused logs. Package SHAs verified before each run.
Root release (run2) recorded in `cases-selector/binding.json`. Curricula read-only from hosted
p11-research-corrected-20261026;no hosted write.
