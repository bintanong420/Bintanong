# Question-parts reference evaluation plan

20October2026;Phase09,p09,baselineac94a4a. Continue inline with TDD and one fresh
whole-change review. Spec:master12.4/13.2/14.2 and the
[foundation limitations](2026-10-20-question-parts-results.md). No new inference.

**Student capability:** retain every requested answer part and distinguish a
supported answer from an unrelated claim or an honest unresolved part.
**Evidence path:** exact original question,complete pinned documents,saved draft,
candidate plan/review and separately frozen author-labeled reference.
**Exit advanced:** question coverage and structured-decision withholding validation.
**Question:** can offline scoring expose omitted extraction and wrong semantic
mapping that the mechanical ledger cannot detect? Actual extraction remains NOT RUN.

## Design

Add evaluation/question_parts.py,not another runtime profile or classifier.
QuestionPartsReference is a strict versioned synthetic-dev-only author label:
case_id,full reference QuestionPlan,ReviewIdentity for that plan/draft,and one
expected PartMapping per reference part. Validate unique/complete IDs and that
expected claims exist in the bound draft. Structured/unknown requirements cannot
have an expected mapped answer in this RAG-only evaluation. No institutional case
or final/sealed benchmark claim follows from these fictional labels.

evaluate_parts(text,integration,plan,draft,review,reference) reuses assess_parts for
candidate validation and review_identity to verify the reference binds the exact
question,release,request,language,full cards and draft. Revalidate supplied models.
Never compare a candidate against its own generated claims as the gold standard.
Reference mappings are author-supplied semantic judgments,not model verdicts.

Match requirements by exact original (start,end,quote),ignoring r-number/order.
Check kind separately. Report exact_span_and_kind_precision/recall,expected/
predicted/matched counts,correct mapping count over ALL reference parts,missing/
unexpected/kind-mismatched parts and incorrect mappings. Compare mapping claim
sets/status/reason with frozen labels;order alone must not fail a valid mapping.
Omitted extraction counts against mapping recall too;never score only matched parts.

This is strict reference agreement,not an automatic semantic-equivalence judge.
Different valid span boundaries or alternative claim combinations require human
adjudication and a new preserved reference version,not silent label rewriting.
agrees_with_reference requires all extraction/mapping checks and existing support
guards. A correct uncertain/unavailable result can agree while the ledger stays
unresolved. false_complete_against_reference identifies a mechanically positive
ledger that disagrees with the frozen reference. Every score remains candidate-only,
no-use/no-activation and semantic_completeness=unverified. Return no answer/text.

## Tasks

1. [x] tests/test_question_parts_evaluation.py RED,then minimal evaluator/contracts.
   Cover omitted fee,wrong mapping,correct unresolved mapping,complete supported
   fixture,kind downgrade,renumber/order independence,claim-set order,all-reference
   denominator,stale question/request/release/language/evidence/draft/reference,
   incomplete/duplicate/unknown labels,private data/invalid integration,strict bounds/
   extra fields and fixed authority flags. Use existing fictional fixtures only.
   GREEN plus relevant generation/evaluation regressions;commit cohesive code/guide.
2. [x] Freeze one author-labeled reference for the already saved actual location+
   fee failure. Reuse the three foundation assessment variants OFFLINE:missing fee
   mapping,omitted fee extraction,wrong fee-to-location mapping. Expected extraction
   match2/2,1/2,2/2;correct mappings1/2 each;false completion false,true,true.
   Add a clearly author-constructed correct uncertain-mapping control:agreement
   true,ledger unresolved. No fabricated new actual-model output or benchmark run.
3. [x] One independent whole-change review,one focused TDD fix pass if needed,
   explicit56-selection regression gate,dated results and compact snapshots.
   Seal raw receipts/source hashes;verify prior evidence unchanged.

## Verification and stop

Use existing readiness Python3.13 -B -m pytest -q -p no:cacheprovider,ignored
TEMP/TMP/basetemp under workspace/audit-evidence/p09-question-parts-evaluation-20261020/.
No installs/downloads,DB/dependency/lock changes,model/service calls or training.
Selected scoped/canonical/separate stays;guarded/covered remain unselected. No
keyword router,Prolog substitute,source truncation or weaker support checks.
Thesis17-18/39-44,actual PNG/master3/11/12.4/13/14 consulted;undergraduate/read-only/
unknown/source-gap/privacy/release holds and one-week cap persist. Preserve the
[timing recommendation](../Context/response-time-recommendation.md);no new latency claim.

Stop once scoring distinguishes the saved mechanical false positives. Do not turn
this into another prompt/model/seed/budget sweep. Actual extractor and per-part
semantic checker need a separate frozen observation gate before runtime integration;
report actual per-language quality NOT RUN here. No Phase10,push,merge or deployment.

Review focus:reference must not be self-generated or silently change with a
candidate;omissions cannot disappear from denominators;correct abstention is not a
complete answer;wrong structured kind cannot pass;reference agreement never grants
runtime authority. Ruling:owner continuation authorizes this reversible bounded
evaluation work. Exact matching favors auditable labels;cost is human adjudication
for alternate boundaries,explicitly disclosed rather than called semantic failure.

Task1:RED35expected missing-module assertion failures1.43s/GREEN35passed0.72s.
Relevant generation/evaluation regressions603passed6.81s,exit0. Raw red.log,
green.log,relevant.log/relevant-selections.txt retain receipts. No runtime change.
Task2:4offline checks match predeclared expectations;two mechanical false positives
exposed against fixed post-hoc author labels. Reference0754b6402bb7dc19912538710d18f5077ea63c8e16b30cee6c17ddcffe5ce755;
saved-output-scores.json records origins/denominators. Actual extractor quality NOT RUN.
Task3:one reviewac94a4a..4f39833,no actionable finding,122passed1.17s. No fix pass.
Final56-selection gate2193passed/66subtests92.41s,exit0;no product changes afterward.
Ruling:input identity binds plan/evidence/draft,not expected annotations;full frozen
reference SHA256 is mandatory receipt provenance. Current caller retains it;future
callers must do so too. Cost if ignored:ambiguous label version across score reports.
