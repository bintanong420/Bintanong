# Opt-in compact per-part review references

Code:b695739;baseline:ba7d8b4/codef635ccc.

An explicit `Generator(...,review_reference_profile='short')` now shortens review
wire references using the existing request-local evidence codec. All six measured
review-overflow profiles fit8192with768output/8margin. Canonical review remains the
default;no RuntimeSettings,CLI,active profile or release changed.
[Implementation plan](2026-10-27-short-review-reference-plan.md).

## Preserved behavior

Only structured source-reference fields change:available-source IDs,attached claim
references,source IDs,required coverage,explicit order and quotation references.
Source/claim/quotation text remains literal. All cards,conditions and source limits
remain available. Request-local pack identity is checked before mapping;references
from another pack reject. Host drafts/final claims and bound review identities keep
canonical IDs. The review output schema,part verdicts,support checks and final
validation are unchanged. A negative part verdict still withholds the answer.

The option is restricted to the per-part explanation path. Draft-reference profiles
remain independent. Existing canonical/short-draft default tests remain unchanged.
No source content decision,school approval or activation is inferred.

## Measured review capacity

Same fixed sample claims/questions as the six failing profiles;only review IDs
change. Every inverse-mapped payload equals its original payload exactly,including
all prose,source cards,limits,coverage and metadata. Canonical prompt hashes/token
counts match the frozen prior receipts before comparison.

| Review claim | English before/after | Taglish before/after |
| --- | ---: | ---: |
| Admission test,whole service | 7964/5482 | 7971/5489 |
| Admission test,metadata/checklist | 7488/5457 | 7495/5464 |
| Discipline procedures | 9591/6731 | 9598/6738 |

Inputs only;add776for output/margin. Largest compact total7514fits8192. These are
six capacity probes,not a guarantee for longer questions,history,multiple parts,
Hybrid or larger actual claims. No model inference was needed for these counts.

Three previously saved TOR step-one integrations were replayed through the changed
generator/reviewer only. English input produced English;Filipino/Taglish produced
Taglish.3/3returned the same exact reviewed source quotation with `validated`,one
draft and one review each (six actual model calls). Generation/review inputs:
3314/2917English and3318/2920for each Taglish reply. No new routing/retrieval,
expanded559coverage,Hybrid accuracy or latency improvement is claimed. Runs overlap
the full test suite,so they are unsuitable for a timing comparison.

## Repair remains a distinct capacity blocker

A grammar-valid deliberately incomplete short draft can reach the existing repair
branch within the768-token output bound:676tokens English/677Taglish. Host validation
reports `missing_procedure_record_coverage`;complete evidence remains required.
Using that coverage error alone,repair prompts total8322/8331including reserves
and exceed8192;additional style feedback is not needed to establish the overflow. This is a
reachable synthetic counterexample,not an observed model answer. The prior overflow
was not solely an oversized hypothetical draft. Existing refusal remains in force.
One lossless previous-JSON object probe preserved every value but still totaled
8196/8205including reserves. Encoding alone is insufficient;that bounded question
is resolved,no production repair change was made. Do not reduce the safety margin.
Do not claim that fixing review IDs resolves repair,default retrieval budgets or
all answer-quality/release gates. Original54over2048closures and selector/answer
evaluation remain separate. Active78research release/39curricula remain unchanged.

## Verification and recovery

Synthetic RED:13expected missing-feature failures1.30s. Focused generation/reference/
quote/coverage/parts/API regressions:192passed3.34s. Test setup corrections retained
canonical coverage ordering and existing immediate negative-verdict withholding;
no existing assertion was weakened. Three changed Python files parse;Ruff,Black,
mypy and Bandit remain unavailable and were not installed.

Ignored root:workspace/audit-evidence/p11-short-review-references-20261027,with
RED/focused/full logs,capacity inverse-mapping receipts,six compact review messages,
saved-input answer replays and repair-reachability proof. Source data stay untracked.
Fresh full suite:7038passed/1608subtests,6skipped/2xfailed/6warnings1388.54s,exit0.
Four Windows symlink skips,one CUDA/OCR-extra skip and one legacy dataset skip;
two existing photo-layout refusals remain expected failures. Docs/phase30tests/
14subtests pass25.59s;final docs/phase rerun30/14passes13.00s. Root reviewed the diff;fresh-agent review was unavailable
after the prior worker usage-limit failure,so none is claimed. Independent delivery
checks confirm complete inverse payloads,three sealed saved answers,unchanged old/
current packages/active pin,Python parsing and local links. Four raw roots sealed.
