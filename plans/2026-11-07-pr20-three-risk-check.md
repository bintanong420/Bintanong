# PR20 compound, length and recovery-order check

Owner requested checking the three remaining risks. Product code unchanged during this audit.
Serving API code `c5f20a4e`; repository head `1fbb63a0`; BSCS2018–2019, existing reviewed
cached research snapshot, compound ON only on staging3218/API8023, model8192 context.

## Live compound spot checks

| Input | Observed result | Frontend-proxy HTTP time |
| --- | --- | --- |
| English: passed CC1/L, can take CC2/L and CS1/L? | Answered, two independently cited V2 parts |24.06s|
| Taglish: Passed na ako sa CC1/L. Pwede ko bang kunin ang CC2/L? Pati CS1/L? | Unnecessary generic clarification |23.66s|
| Filipino: Naipasa ko na ang CC1/L. Maaari ko bang kunin ang CC2/L at CS1/L? | Unnecessary generic clarification |23.04s|
| English two checks plus Good Moral request procedure | Answered, three V2 parts; Charter workflow selected |26.68s|

These are four spot checks, not a language-accuracy estimate or full benchmark. HTTP200 does
not establish answer success; the two clarification cases fail their intended capability.
No actual browser click-to-render timing or original-PDF re-adjudication was performed.

Taglish router trace reproduces `invalid_reference` after repair. The model emits one
CC2/L operation, assigns both question parts to index0, and labels structured parts with a
Handbook policy topic. The CS1/L part therefore references a target outside its own words.
The validator correctly refuses this output. This case is not context overflow: main input5528,
repair5912, each with768 output reserve inside8192. The Filipino case was not separately traced;
do not assert an identical internal cause solely from its clarification message.

## Recovery answer length

Reused exact successful CC4/L frontend result from the prior turn because serving code is
unchanged:1,685 whitespace-separated words,9,931 characters,73 lines, four draft tables and
one full source-quotation section. `recovery_lines` renders every draft and all used clauses.
The recovery answer uses text fallback: presentation V2 currently requires a canonical
decision for this path, whereas the recovery/dependency answer has no eligibility decision.
Consequently, adding V2 did not make this answer concise. This is host-rendered length;
changing only the model's prose prompt would not fix it.

## Recovery preference versus fastest intent

The owner decision ledger's4November entry intentionally prefers the just-in-time DraftD
over the all-summer alternative. Preserve this default; it is not itself a ranking defect.
Existing planner code separately accepts `fastest_asked=True`, sorting by projected rejoin
term then request count. The chat call in `Orchestrator._recovery` passes `regular_asked`
but never passes `fastest_asked`, so the latter remainsFalse even for the owner's explicit
"as soon as possible" question. This is a missing connection between request intent and planner.

Saved checked result: D projects3rd-year2nd-semester, C projects3rd-year1st-semester,
both with4 requests. Every draft has terms with unknown checks; some have load warnings.
Thus C is the earlier projected alternative, not a proven viable/optimal schedule. A fix
must preserve approval/offering/prerequisite/load limits and qualify the headline accordingly.
The existing plan-view helper can identify C as fastest, but that UI remains disabled;
silently activating it is not part of this check.

## Validation and proposed fix order

Raw public-question traces/streams: ignored
`audit-evidence/pr20-local-staging-20261107/risk-check-compound-results.json`,
`risk-check-compound-extra-results.json`, `risk-taglish-router-result.json`.
Recovery evidence: `recovery-repro-result.json`, `recovery-pipeline-result.json`.
Focused deterministic checks:12 passed in61.10s. Existing earliest-summer test confirms
`fastest_asked=True` selects C; plan-view test confirms earliest-rejoin ordering; bounded
compound executor tests pass. These do not prove live model interpretation:

```powershell
& C:/Coding-projects/bintanong_workspace/audit-evidence/p12-env-20261031/venv/Scripts/python.exe -m pytest tests/test_planning_recovery_search.py::test_the_earliest_summer_alternative_is_preserved tests/test_api_plan_view.py::test_fastest_rejoins_earliest_then_fewest_requests tests/test_compound_symbolic.py -q -p no:cacheprovider --basetemp C:/Coding-projects/bintanong_workspace/audit-evidence/pr20-risk-check-focused-20261107
```
An initially broader four-file run was stopped during expensive recovery parity work;
it has no completed-suite pass claim. No product or source data changed.

1. Fix compound task/target extraction across language variants; retain reference guards.
2. Connect explicit fastest intent to existing ordering, retaining defaultD and qualification
   for unknown/overload/request-dependent drafts. Test the chat entrypoint, not only planner flags.
3. Shorten default recovery presentation using checked data; retain detailed alternatives,
   assumptions, warnings and source quotations in an accessible optional detail view.

No merge, configuration/context change, source activation or acceptance sign-off follows from
these checks. Automated inference stops after the four cases and one bounded router trace.
