# Phase07 implementation review

Fresh independent read-only review covered87ece27..9286c76 against the accepted
design/implementation plan. No model-server calls or source-content reviews.
Reviewer reported three actionable P2 findings and no minor findings.

## Findings and verified corrections

1. Canonical not from an English contraction was declared as a literal marker in
   NormalizedQuery, whose literal check could reject correct original text. Router
   surfaced invalid_grounding for “didn't”/“didn’t”. Keep original spelling and
   shared before/after semantic-marker validation; declare only markers actually
   present literally. Both apostrophe variants now have focused regressions.
2. Evaluation checked the entity collection but omitted operation/target meaning.
   A request checking the wrong course could otherwise score all fields correct.
   Require expected scoped operation bindings, score them separately per language
   and include them in equivalent-family consistency. New regression swaps target
   while preserving both mentions and verifies operation_correct=false.
3. HTTP200 choices=['invalid'] escaped the typed transport boundary as AttributeError.
   Validate choices/message object shape before access; malformed shapes return
   invalid_server_response without body text. Four envelope variants are covered.

Reproduced review gate:**4failed/3passed**, then focused routing gate
**75passed,2.43s,exit0**. Logs:workspace/audit-evidence/p07-implementation-20261019/
review-red.log and review-green.log. Relevant23-file regression gate:
**1499passed/11subtests,266.57s,exit0** (regressions.log), including the Phase06
17-file gate and routing/legacy-client tests. This ran alongside CPU inference;
the elapsed time is not a controlled performance benchmark.
During that run, a self-review found unrelated context-grade conflicts could
unnecessarily block document-only RAG. Focused regression RED1 -> corrected gate
**76passed,2.31s,exit0** (material-facts-*.log); preserve those fact references
without requiring their resolution for a lookup that performs no grade check.
The23-file collection predates that last test/change; the final76-case suite
specifically covers the validation delta. Shared Phase06 code remains unchanged.
No shared-contract change, source promotion, evidence execution or activation.

## Evaluation identity and limits

An already-running15-variant/five-family synthetic-model batch is pinned to9286c76,
promptv2 and its original case/metric contract. It predates operation-target scoring.
Keep its initial inputs and output unchanged. Any later operation-aware rescore
must identify the annotation/code revision and reuse the original model outputs;
do not present the old run as testing the updated evaluation code.

Declined to judge:actual-model language/meaning accuracy, because model evaluation
was pending and excluded from reviewer calls. Implementer ruling:that remains an
explicit phase-exit requirement, evaluated separately with actual Gemma outputs;
neither independent review nor passing mocks establish it. No institutional/final
benchmark claim is authorized. Initial model probe failures remain evidence.

## Later bounded model diagnostic

An actual prerequisite-output replay identified correct course/operation/failed
claim text but incorrect character offsets. Root evidence:
structured-original-output.json SHA256
0e799cf8e2d268dc02805f355b9975faecd3a18b9640235bbdf721223acec54d.
Implementation ruling:host can anchor a complete literal quote only when it occurs
exactly once; never guess repeated/missing text or reinterpret the claim's state.
Correction count is explicit. New regression RED1/1passed -> focused248passed,
5.02s,exit0 (anchor-*.log); wrong/repeated/missing quotes still withhold dispatch.
The same captured model output replayed without another model call now yields
Symbolic/check_prerequisite_eligibility on course-b, failed course-a, three offset
corrections. structured-quote-replay.json records this bounded result. It is not a
new multilingual accuracy run or evidence that all old failed outputs are repaired.
