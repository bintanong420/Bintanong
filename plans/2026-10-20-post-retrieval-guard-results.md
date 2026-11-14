# Post-retrieval decision guard results

20 October 2026;Phase09 active,p09. [Plan](2026-10-20-post-retrieval-guard-plan.md),
[prior scoped selection](2026-10-20-scoped-explanations-results.md),
[timing boundaries](2026-10-20-response-time-measurement-contract.md).

## Behavior and scope

Product48307b8 initially adds one explicit release-bound LLM assessment after
retrieval. Following failed quality gates,it is isolated as an explicit developer
`explanation_profile='guarded'`;selected scoped/canonical/separate remains unchanged.
Only document_only proceeds to documentary drafting and separate
per-claim checking. Required/uncertain/invalid output returns localized withholding
without generated claims. Transport/time failures stop. The host records result
and monotonic seconds;the call remains inside the existing generation/request
deadline. No guard repair,hidden reroute,new rule execution or keyword classifier.
Symbolic/Hybrid already have structured results;nonready and other profiles retain
their behavior. Historical reports retain null guard observations. Guarded is not
promoted;the missing safeguard remains an unresolved Phase09 exit requirement.

The student capability is avoiding an unsupported course-check answer after a
misroute. Evidence is still complete supplied documentary cards plus reviewed typed
structured results where actually executed. No source trimming,cache,training,
model/seed sweep,dependency/lock/DB changes or institutional activation occurred.

## Initial quality gate and reviewer finding

Reuse9existing fictional multilingual questions,then assign the3existing Symbolic
questions unchanged RAG document evidence with no structured result. These are
prepared-generation software probes,not router accuracy or institutional benchmark
cases. Normal9:6documentary answers/18supported claims and3host-only Symbolic
outputs. Both author and independent reviewer find these appropriate in scope and
style. Forced EN withheld;FIL incorrectly document_only and released3unrelated
FormQ/fee claims as answered;Taglish uncertain/withheld. Zero repairs,20physical
calls across12cases. The FIL claims match their source but miss the question.
Entailment and answer relevance are separate quality measures. No fabricated
eligibility conclusion was observed.

One independent whole-change review identified this P2 and no other actionable
defect. Its separate189test selection passed5.61s. Raw reviewer/assessment.md and
focused-regressions.log preserve its finding. That test activity overlapped the
initial model experiment;individual durations are descriptive,not controlled
latency comparisons. No additional model runs occurred in the reviewer.

## Single bounded correction

The question's assertion that a check outcome exists is not evidence of a check.
Clarify this in the semantic guard instructions:reporting/confirming/interpreting
an allegedly existing course-rule outcome still requires a trusted structured
result. No evaluation question/example or language keyword routing is inserted.

Actual saved-output regression test_model_gate.py reproduced FIL RED:1failed,
5passed0.39s. Corrected unit scope/guard/evaluation tests82passed1.54s. Rerun only
the unchanged3forced questions and3ordinaryRAG controls once in correction/.
Normal controls:3answers/9supported claims,9calls,zero repairs;author inspection
finds appropriate styles. Forced EN structured_required/withheld,FIL tool_error
after reaching768completion tokens,Taglish document_only/answered unrelated FormQ.
Corrected regression2failed/4passed0.33s. The Taglish answer's3claims are source-
supported but irrelevant to the requested check. No unverified eligibility decision
was observed;the operational fallback is distinct from a successful classification.

Reject the correction;restore the initial prompt for reproducibility. Retain the
guard only in the explicit experimental profile. Isolation RED2/GREEN209tests3.75s;
an intermediate1failed/208passed CLI-help wrapping check was corrected. There is
one open semantic P2 in the unselected experiment;this is quarantine,not its fix.
Full actual-service RAG observation was NOT RUN because the quality prerequisite
failed. Its prepared observer script is retained unused. No subsequent prompt,
seed,budget or model run. Raw historical reports say scoped because that was the
candidate profile at inference time;do not relabel their sealed observations.

## Measured time and selection

| Prepared generation / guard seconds | English | Filipino | Taglish |
| --- | ---: | ---: | ---: |
| Initial ordinary RAG |39.246 /16.153|26.987 /3.494|25.196 /3.499|
| Initial forced structured request |29.919 /29.918|25.694 /3.411 (wrong answer)|35.124 /35.123 (uncertain)|
| Corrected ordinary RAG |24.675 /3.776|25.351 /3.599|24.888 /3.603|
| Corrected forced request |24.711 /24.710|36.792 /36.791 (tool error)|25.580 /3.895 (wrong answer)|

Initial unchanged Hybrid21.293/22.222/22.679s;host Symbolic about0.003s excludes
upstream routing/Prolog because these are prepared packages. These are individual
samples,not p50/p95 or a controlled speedup. Added guard time is inside generation,
including HTTP/preflight,template/tokenization,model inference and parsing. Failed
and uncertain attempts remain visible. Both new quality gates fail regardless of
latency;neither qualifies as an accuracy improvement or acceptable student wait.

The selected full warm backend remains the PRIOR29.915/16.999/38.884s observation
and process-to-ready25.955s,with Supabase readiness0.312s. No new full backend,
browser/API/queue/hosted connection or complete cold-system timing was measured.
The proposed15-20s student-visible target remains unachieved/unvalidated. Do not
add prepared guard spans to earlier backend samples and call that a measurement.

## Verification and evidence

Mechanical TDD:corrected RED25failures;initial long pytest parameter IDs caused
2Windows harness errors,then concise IDs repaired the harness before RED.
Initial GREEN143tests2.66s;serialized guard-result metadata RED4,then expanded
GREEN802tests5.67s. Raw failed receipts retained. Candidate schema rejects failed
guard observations relabeled as success,nonfinite durations,wrong/duplicate/extra
JSON and cross-release assessment. Deadline/cancellation,request isolation and
legacy/control bypasses are covered. Mocks establish mechanics,not semantic recall.

Final selected productd2d1131 passes the explicit53-selection regression gate:
2048passed/66subtests89.43s,exit0. Exact command script:raw verify-regressions.ps1;
log:final-regressions.log. Python3.13 -B -m pytest -q -p no:cacheprovider with
ignored workspace/audit-evidence test temporaries. Actual semantic gates remain FAILED;passing
mechanical regressions does not close the P2. No product changes after this gate.
Docs/phase gate617passed/14subtests13.40s;phase state valid,active9,cannotadvance
because its checkpoint remains in_progress. No completion/activation is inferred.
Final docs-only check597passed1.17s;112local links and active snapshot caps pass.

Raw root:C:/Coding-projects/bintanong_workspace/audit-evidence/
p09-post-retrieval-guard-20261020/. Original and corrected pre-inference manifests
bind input bytes,code snapshots,observer hashes and server props;traces retain
message/schema hashes,physical call durations and server usage/timings. Originals
are not overwritten. Source-inference/ and correction/source-inference/ retain
exact product bytes for their respective model observations.
Root-assessment.json records all18observations and both failed gates;selected
source snapshotd2d1131 preserves final isolated code. Delivery manifest155files
verified,SHA256300ccd212694d876c695a3cef33ce1092179dd802eaeb1135012bb3b08fb0829.
Later doc-wrapper logs are excluded. Local link/snapshot checks verify112links and
active caps;historical handoff123lines is unchanged from4022711,a retained3line
exception preserving its delivery evidence. No historical handoff rewrite occurs.

Existing CUDA18088,35/43GPU layers,Gemma and owner workspace/MODELS reused. Shipped
defaults120s inference/generation/stage,180s request remain;observations use240s
inference/generation. Existing actual-service composition uses300s stage/600s
request if its quality prerequisite passes. No installs,downloads or model rehash.
Thesis17-18/39-44,actual routing PNG/master3/11/12.4/13/14 consulted;standing
unknown/source-gap/undergraduate boundaries override illustrative closed-world
examples. No architecture or scope discrepancy.

## Remaining limits

The guard is another fallible model assessment. This tiny related-family synthetic
set cannot establish institutional accuracy,per-language recall,tail latency or
student waiting acceptance. No75-case run or owner content/style approval occurs.
The one-week prompt-improvement cap and accuracy-first requirement remain.
Upstream2Taglish style errors,opaque technical IDs,institutional source/runtime/
release holds,private-file/auth and hosted migration remain separate work.
Browser/API/queue/full-cold metrics remain unmeasured in their applicable phases.
No Phase10 advancement,push,merge,deployment or institutional use is authorized.
