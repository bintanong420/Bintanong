# Printed service steps:results

[Plan](2026-10-29-printed-service-steps-plan.md);owner decisions in the ledger (29Oct:option A,one
column per line,Tagalog lead-ins only for Taglish,defects shown as printed with a note).

## Delivered (TDD,synthetic fixtures)

- `service_steps.py`:strict parser b92cce2 (every field by explicit grammar,else no table) and
  renderer 8c332ca/4fd8958/6677c5b:overview/requirements,one claim per step (continuation when a
  step exceeds one claim),each office action and column on its own line,printed total,limits and
  the original-document note;English labels/data,Tagalog lead-ins for Taglish/Filipino questions;
  <=1200chars and <=8records per claim or nothing renders. 18parser/renderer tests.
- c177400:document parts whose required records parse are answered with these host claims beside
  fee/grade replies;host claims may cite several records;other parts keep the model path with one
  claim reserved each. 3integration tests;focused1097pass/282subtests (Docker up).
- Real 559data:23/44Charter services parse and render in both languages (incl.7with printed
  defects shown as is). 21row/unnumbered/continuation layouts keep today's path (refuse,no guess).

## Live check (one attempt each,real 559package,c177400)

| Case | Before | Now |
| --- | --- | --- |
| good-moral-en | abstain/timeout 77–117s | **answered 28.8s**,printed steps,routing calls only |
| library-card-taglish | insufficient | insufficient:router requests the source-limit text as claim |
| entrance-health-fil | abstain | abstain:router picks handbook policy,not the Charter procedure |
| leave-en / cross-enroll-en | answered | answered 37.9s / 43.8s (model path unchanged) |
| Regressions | 2/3 | 2/3 (grade-excellent selector miss unchanged) |

An earlier attempt ran while the model container was down after laptop sleep (all
`model_connection_error`);archived as `live-check-model-down`,not a result. Remaining blockers were
routing (selector recall,source-limit text offered as claim),not the printed-steps path.
c177400 full suite:7079pass/1608subtests,6skip/2xfail,1406.99s,exit0.

## Routing fixes and second live check (1e5d249)

- 248b04f:malformed-condition and printed-total-discrepancy limits are no longer offered as
  not-stated menu claims (owner29Oct shows them as printed);absence-type limits stay selectable.
  Deliberate requirement change to the earlier "every limit selectable" test,split by kind.
- 1e5d249:`build_multi_research_resources(routing_context=True)` opt-in passes the existing reviewed
  source labels/column hints (36d5f56) to the menu;default composition unchanged. Real559:145
  topics,35labelled (e.g. charter_entrance_health "1. MEDICAL EXAMINATION").

Live (topic selection + routing context,one attempt each):

| Case | Result | Seconds |
| --- | --- | ---: |
| good-moral-en | answered,printed steps | 36.2 |
| library-card-taglish | **answered**,Taglish lead-ins,defect shown with note | 22.0 |
| entrance-health-fil | **answered**,Charter MEDICAL EXAMINATION steps | 19.9 |
| leave-en | answered (model path) | 37.0 |
| grade-excellent-taglish | **answered,matches active78** (grading_scale) | 21.0 |
| cs-cc5-failed-cc4-en / criminology-corequisite-tl | match (ineligible / clarification) | 21.3 / 27.5 |

All3regressions now match. Warm inner pipeline only;no browser/student latency claim. Not a
full benchmark or activation decision;discipline/admission-test and other unparsed layouts remain.

## Evidence

Ignored:workspace/audit-evidence/p11-printed-steps-20261029 (grammar survey,real parse/render
checks,sample renderings,RED/GREEN/focused logs,live-check traces,full suite).

## Full559battery refresh (d9bdb3a,code1e5d249;selector+routing context)

Full suite for1e5d249:7081pass/1608subtests,6skip/2xfail,1434.89s,exit0 (an earlier attempt was
stopped by low memory and is not counted). Same frozen cases as 28Oct,one attempt each:

| Case | 28Oct | Now |
| --- | --- | --- |
| good-moral-en | temporarily_unavailable | answered,printed steps 43.4s |
| library-card-taglish | insufficient | answered 21.6s |
| entrance-health-fil | abstained | answered 19.8s |
| leave-en | answered | answered 35.4s |
| shifting-taglish | insufficient | insufficient:router returns `clarify` with zero parts (selector correct) |
| cross-enroll-en | answered,OR misreading | answered 42.0s;no OR,but says "conditions must be met … and e)" — still implies all-of for a)/b) |
| discipline-en | abstained | abstained 97.9s (long handbook flow,not a Charter table) |
| hybrid-bscs-en | answered,OR misreading | answered 54.8s;Prolog ineligible + a)–e) under printed "provided:" |
| Regressions | 2/3 | **3/3** |

6/8answered (was4/8),3/3regressions (was2/3). Remaining:router `clarify` on clear questions;
added "and/must be met" over printed condition lists (the or-guard does not cover it);discipline
long-flow answer;21unparsed Charter layouts. Gate not passed;559stays inactive.
