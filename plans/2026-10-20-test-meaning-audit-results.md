# What the test count actually proves

20October2026;owner requested that2200+tests be meaningful. Baseline073f76e;
[audit plan](2026-10-20-test-meaning-and-recovery-plan.md). This is a bounded review
and refactor,not certification of every test or a chatbot accuracy result.

## Counts and interpretation

Fresh collection of the existing explicit57-selection gate at073f76e found
2240expanded pytest items from649distinct selected test functions.605items were
tests/test_docs_hygiene.py:596per-document format cases,8scanner edge cases and
1scan-coverage check. The last2239passing gate had been collected before one new
results document. Parametrized cases are useful distinct inputs,but are not2240
independent behaviors,questions or human-verified answers.66subtests in the previous
gate are additional nested checks,not extra model evaluations.

The format scan catches actual control-character corruption in plans/JSON/paths;
it is useful repository hygiene. Counting every document separately inflated the
headline without adding chatbot behavior coverage. It now scans EVERY governed
file in one test,collects all damaged paths/codes,and retains8scanner edge cases
plus scan-coverage check. That gives10hygiene items regardless of document count.
The check itself and directories/extensions were preserved.

Duplicate four-stage prompt display/payload assertions were consolidated into
test_compact_json_guidance.py. Routing/style run once each;draft/support cover BOTH
RAG and Hybrid. Schema acceptance-equivalence/adversarial tests stay in
test_prompt_schema_display.py. One repeated test body removed;no production edits.
After collection:1643items from648distinct selected functions,including10hygiene
items. Baseline-to-after difference597reflects595fewer format items and2duplicate
prompt cases. It is not removed safeguards;later documents remain fully scanned.

## Six deliberate-bug checks on EXISTING tests

Baseline15focused cases passed. Each mutation was compiled into a function in a
separate pytest process;source files were never edited. Each named test then failed
at the intended assertion,not import/fixture setup. Expected failing runs are retained.

| Deliberate regression | Existing test evidence | Intended failures |
| --- | --- | --- |
| Accept wrong release | generation_validation:wrong release/language/outcome | 1 |
| Ignore private namespace in claim | generation_validation:fabricated citation/private reference | 1 |
| Ignore negative support verdict | generation_validation:every claim needs positive support | 3 |
| Drop missing fee part from completeness | generation_requirements:missing fee unresolved | 1 |
| Accept another request's review | generation_requirements:request replay | 1 |
| Enlarge shared deadline100times | generation_parts:one deadline covers both calls | 1 |

All6deliberate regressions were detected. This is six sampled safeguards,NOT a
whole-suite mutation score or proof that every649function was useful. It shows
real boundaries,including negative paths,are checked. The fixture transports are
appropriate for deterministic guards;their supplied supported verdicts do not prove
that a real model will recognize support,coverage,language or route correctly.

## Refactor verification and inspected scope

Before refactor,620focused docs/prompt cases passed2.31s. Synthetic copied document
fixtures with two distinct corrupted files were rejected by BOTH old/new scanners;
logs contain both paths and U+0008/U+000C. No original documents were damaged.
First merged prompt run21pass/1fail1.71s exposed a Hybrid-only test fixture reading
pack.decision.outcome for a RAG null decision. Corrected fixture to preserve the
old RAG test's null case;no production correction. Verified22passed1.50s.

One fresh whole-change review of073f76e..011bc2d independently ran154selected tests
(all passed2.64s) and found one P2:normal pytest dict-diff output truncated a large
aggregate failure report. All files were checked,but15of20damaged paths were hidden.
Root reproduced RED on20synthetic copied documents,then replaced the dict assertion
with explicit complete failure text. GREEN confirms all20paths visible while the
damaged documents still cause the expected pytest exit1. One focused fix pass;
no re-review or original-document damage. Exact logs/receipts remain ignored.

Direct assertion review covered generation validation,part analysis/ledger/reference
scoring,pipeline composition,schema-display/compact prompt tests,math/import
compatibility and document hygiene. Collection inventory covers all57selections;
it does not mean all assertion bodies were independently reviewed. Positive/negative
schema variants,synthetic source/operation binding,request isolation and deterministic
symbolic tests remain useful. Existing aggregate software green still coexists with
[actual failed8case quality](2026-10-20-question-parts-observation-results.md).
No test count can substitute for that failed semantic evidence.

Raw:workspace/audit-evidence/p09-test-meaning-audit-20261020/. inventory-before/after,
mutation-specs/results and per-mutation receipt/log files retain exact nodes,
source/function hashes,patches,commands and outcomes. Hygiene before/after copies
and logs retain synthetic equivalence evidence. No new tracked test was added to
raise a count;no new model/service/DB call or dependency change occurred.

## Recovery direction and verification

[Router recovery design](2026-10-20-router-question-understanding-recovery-design.md)
locates question parts in the EXISTING pre-retrieval interpretation stage,with
versioned request/release-bound propagation to output validation. This is design
only;it does not claim source removal fixes the model or authorize new inference.
It preserves the separate language call,LLM semantics,structured Prolog and RAG.

Independent review is complete with the single reporting correction above. Initial
same57-selection gate1643passed/66subtests94.58s. AFTER correction,the final gate
again1643passed/66subtests89.02s,exit0;fixed-regressions.log retains the final result.
The second run was required by the newly fixed reporting issue. No selected runtime
changes,Phase10,push,merge,deployment,institutional activation or new latency claim.
Accuracy-first,scope/privacy/source/release boundaries and one-week cap persist.
