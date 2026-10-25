# Service routing and completeness results

Phase11 remains active. Expanded release remains inactive. This is a verified
software increment with a FAILED live semantic-quality gate, not phase completion.
[Plan](2026-10-25-service-routing-completeness-plan.md). Baseline7f957c1.

## Changes

- a2a2f19: router receives bounded title/description context only from its topic's
  reviewed assigned service fields. LLM still chooses topics; data is untrusted.
  Completeness review sees all available documentary records once; each individual
  support verdict remains restricted to that claim's own citations.
- 6b47449: reviewed client_step record requirements travel through retrieval,
  integration and evidence preparation, bound to exact subject/requested claim.
  Draft/final checks require an answered part's own citations to cover those
  records. Existing single repair is reused; missing coverage then withholds.
  Absent metadata is omitted from serialization, preserving older digests.
- 4d391f6: remove the earlier hard ban on formal Filipino words, following the
  settled25Oct owner decision. Everyday wording remains preferred; the Filipino
  function-word floor and ordinary support checks remain. No live rerun afterward.

This floor proves record citation coverage only. It cannot establish correct step
order, semantic completeness, field association or support for added prose.
No hardcoded procedure facts, keyword routing, source changes, dependencies,
migrations, model defaults, output/call budgets or release activation.

## Verification

Evidence root E = workspace/audit-evidence/p11-service-refinement-20261025.
Shared Python3.13 -X utf8 -B -m pytest -q -p no:cacheprovider; external --basetemp.
All tracked fixtures are synthetic. Raw source/model packets remain ignored.

| Boundary | Observed RED | GREEN |
| --- | --- | --- |
| Topic/coverage context | 5 failed/9 passed after fixture correction | 944 broad passed20.46s;30 focused1.25s |
| Record transfer | 5 failed/4 passed | Transfer then7 passed; host2 failed |
| Host/final citation floor | 3 failed/7 passed including final bypass | 1121 passed29.74s |
| Formality preference | 3 failed/40 passed | 1121 passed29.77s |

Independent scoped reviews: initial14 focused passed2.26s; new record boundary10
focused passed0.95s; final preference43 passed2.42s; none reported blockers.
Full tests/ suite is running on frozen4d391f6; result pending. No installed
linter/formatter; whitespace/phase/doc checks follow the run. Prior6708 full-suite
result belongs to3fbea08 and is not substituted for this increment's full suite.

## Bounded live observations

Three natural pre-enrollment questions, English/Filipino/Taglish, each run once per
new boundary against the explicitly inactive local80-record package. No injected
model packet. Existing Gemma service: thinking disabled,768 output cap,8192 context.
Both runners exit0; this means the harness completed, not that answers passed.

| Run/code | English | Filipino | Taglish |
| --- | --- | --- | --- |
| Context/a2a2f19 | answered77.871s; right service/all steps, poor citation/office association | answered34.908s; checklist only | answered32.601s; checklist only |
| Coverage/6b47449 | answered62.848s; all four step records cited, semantic failure | abstained88.281s; two drafts rejected for formal wording | temporarily_unavailable55.137s; tool_error |

These are resident-model inner-pipeline observations, excluding encoder/composition
startup, outer HTTP/API/browser/student-visible end-to-end and separately measured
hosted readiness. Queueing is unmeasured and remains inside timed calls. They are
neither an SLA nor a final accuracy sample. Existing encoder3816>512 warning remains.

First English output blurred client/agency location and attached too much to the
header citation; first Filipino/Taglish outputs omitted all steps despite positive
completeness verdicts. Exposing the context alone did not resolve omissions.

Second English output cited all steps, but completed the original Step3 text ending
in "for" as "for further action" and used "where" to blend the client's Dean's
Office destination with the Enrolling Officer's separately printed College
Enrollment Area. A generic source-gap footer does not justify either addition.
Second Filipino drafts cited every step but reversed Steps1/2; they also used
"isusumite", triggering the older hard style ban. That rejection is corrected in
4d391f6; these saved drafts are not rerun or retrospectively scored as passing.

Taglish's saved integration is ready/RAG/pre_enrollment. Generation returned
tool_error before any draft/review packet was saved. The resident log's last call
generated768 tokens, consistent with the output cap; the harness records packets
only after successful infer, so an exact failure reason/raw completion was not
captured. Do not report truncation as conclusively established by these artifacts.

## Boundaries and next action

Fresh read-only hosted query: p09-research-selected-20261022 active19;
p11-research-expanded-20261025 draft/inactive80. Source seal verifies54 files,
zero mismatches; seal SHA256
137dbe0e7558f50fd7c6f95dfb6babd45fc71e431265d7291ac36b0c50e3c924.
No source switch or original/sealed package edits. Existing Charter Step3 cutoff
and25-vs20min discrepancy remain unresolved. Fraud/weapon/checker evidence reused.

Next work must preserve reviewed step order and action/office associations, prevent
invented cutoff continuations, and distinguish the Taglish generation failure
from semantic errors using existing traces. No additional prompt-only sweep.
The simple-question requirement, expanded quality/roster/switch gates and later
frontend integration remain open. No Phase12 advancement.
