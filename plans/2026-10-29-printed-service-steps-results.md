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
`model_connection_error`);archived as `live-check-model-down`,not a result. Remaining blockers are
routing (selector recall,source-limit text offered as claim),not the printed-steps path.

## Evidence

Ignored:workspace/audit-evidence/p11-printed-steps-20261029 (grammar survey,real parse/render
checks,sample renderings,RED/GREEN/focused logs,live-check traces,full suite).
