# Phase 11 Charter layout results — 28 October 2026

[Lane task](2026-10-28-p11-charter-layouts-task.md) ·
[Approved split](2026-10-28-phase11-model-workstream-split.md) ·
[Association policy](service-table-association-policy.md)

The inactive559package now has41/44Charter subjects that parse and render in English
and Taglish,up from23/44. All18remaining complete table layouts are covered. The other
three subjects retain their existing model path:initialTOR and complex certifications
have unresolved initial action mappings;feedback is prose,not a service-step table.
This is deterministic parser/render coverage,not a routing,answer-quality,release or
institutional-approval claim. No host integration,source bytes,hosted state or dependencies changed.

## Layout survey and treatment

| Family | Previously refused subjects | Treatment |
| --- | --- | --- |
| Explicit row identifiers | borrowing,library computer | Same row key binds each column;original row numbers remain;interior gaps/mixed grammars refuse. Computer begins at reviewed row2;no invented row1. |
| Record-local complete rows | academic request,cash/check disbursement,library donation acknowledgment,library resource requisition | Client/action and local columns stay in one record. Require a complete same-identity reviewed service_group sequence;sort explicit part_order,never input/retrieval order. Preserve authorization scope and combined agency action text as printed. |
| Scoped checklist/metadata aliases | activity,registration,diploma | Preserve in/out-campus scope,title/note,checklist locations,total aliases and second-copy note. Long overview splits with per-field citations within existing claim bounds. |
| Explicit shared ranges | CAV,refund | Apply only named step/action intervals,with range-record citations;missing targets/conflicts refuse. Preserve printed discrepancies and other source limits. |
| Clinical fields | medical access,dental access | Keep conditional duration verbatim and assistant separate from responsible physician/dentist;do not infer separate duration/fees for assistant. |
| Split fee/source note | readmission | Require both fee fragments;preserve agency heading and original cutoff note/limit. |
| Page continuation/local fields | assessment | Local person/office/window apply to explicitly co-recorded actions;continuation begins at its unique explicit action and ends at named step4. Window1 stays local. |
| Numbered staff pairs | removal | Pair personN with officeN only by same explicit index;preserve joint role text. Missing pair half or competing single/shared person/office refuses. |
| Two procedure phases | admission test | Application and result retain separate step numbering,printed result heading and result-only checklist scope;missing heading,phase gap or mixed ordinary steps refuses. |
| Held partial/prose | initialTOR,complex certifications,feedback | Remain refused;no guessed first actions or conversion of prose into client-step rows. |

Existing reviewed records and previous owner readings are unchanged. Original Charter
physical54–56,66–67,112–113were visually inspected for admission,assessment and removal;
these are clear layout readings within the standing delegated treatment,not new policy decisions.
No consequential new source ambiguity was found. The university's printed inconsistencies,
cutoffs,unknown acronyms and all other recorded limitations remain unresolved.

## Verification and evidence

- Baseline12ac411;unit commits46f11ae,d744df9,ea80d5c,68bd9e3plus final citation hardening.
- Synthetic RED/GREEN logs cover aliases,record rows,explicit ranges,clinical/split fields,
  shuffled input,mixed grammars,long overview,phase resets,local/continuation fields and
  indexed staff. Final focused parser/render/host tests51pass1.79s.
- All generation-module regressions:`test_generation*.py`669pass21.84s,exit0 before review fixes;final rerun below.
- Real data fidelity:44subjects;41parse;41render both languages;2318substantive field
  checks find every value in a claim citing its own record (whitespace/trailing-period
  normalization);46unresolved-limit occurrences retained. Known descriptive metadata
  and printed column labels are outside the substantive-field count,as with the original parser.
- Existing bounds remain8claims,1200characters/claim,8evidence records/claim. Actual
  per-service claim counts/sizes/citations and complete bilingual renderings are retained.
- Ignored evidence:`workspace/audit-evidence/p11-charter-layouts-20261028/`:
  `red1..red6`/`green1..green6` logs,`focused-final.log`/exit,`survey.txt`,
  `verify_fidelity.py`,`fidelity-report.json`,`all-renderings.json`,original-page PNGs.
- Source PDF SHA256:`42a93994e1467df0f32c7038d1c21f638c23ac0f1dee984463acf56caf526529`.
  Package chunks SHA256:`5e790a240eb79e1d2b9d176d462abb587ac7646ea289018ffcbb882f27ed5bdf`.
- Full suite not run in this lane:Claude occupies the shared slot. Mandatory primary
  review/merge/full suite remains the integration gate. No live model or hosted calls.

## Independent review fixes

Review of68bd9e3found scoped requirements could interleave under the wrong last heading,
and unsupported cross-step shared fees could render as repeated charges. Reproduced
6expected failures/34pass (`red-review.log`). Checklist headings now repeat on each
explicit scope transition,with their provenance;in/out-campus and result scopes require
their printed heading. Multi-target step/action fee ranges refuse entirely,since no
reviewed real service needs them. Singular per-step shared fees retain existing handling.
GREEN51focused tests1.79s;real41/44bilingual fidelity remains unchanged.

Final generation rerun after review fixes:675pass18.47s,exit0 (`focused-review.log`/exit).

Primary835aea7merged conflict-free as cb18fe7 (documentation only);post-merge51focused
tests pass2.36s and the real bilingual fidelity check repeats unchanged. Primary review/
merge and the coordinated full suite remain pending;no lane code is activated.
