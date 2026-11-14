# Fixed question-parts actual-model results

20October2026;Phase09 remains active. Plan ce9d993/product6073fbe. The ONE frozen
batch failed its predeclared quality gate:0/8narrow-quality successes. Keep this
detached analyzer unselected;no prompt correction,rerun or runtime promotion.
[Plan](2026-10-20-question-parts-observation-plan.md) ·
[Reference evaluation](2026-10-20-question-parts-evaluation-results.md).

## Capability and observed failure

Student capability:identify every requested answer part,then map actual supplied
claims or preserve unresolved structured checks. Evidence path:original questions,
complete pinned documents,supplied drafts,actual extraction/review output,host
ledger and frozen synthetic author references. This tests master12.4/13.2/14.2;
it does not establish the phase exit or repair the prior semantic P2s.

`QuestionPartAnalyzer` uses at most two sequential calls under one deadline:
extract exact question quotes,then review each declared part and every draft claim.
Host code resolves unique quotes,binds identities and applies existing ledger
guards. It returns no answer,route,Prolog outcome or release authority. Shared
deadline/cancellation,private namespaces,wrong IDs and invalid output have tests.
Selected scoped/canonical/separate remains unchanged.

The five document/multipart cases copied SOURCE sentences into the quote field.
Those strings do not occur in the original questions. Host validation rejected
all five after extraction,so documentary part review was NOT EXERCISED. Example:
question asks where to submit fictional FormQ and its fee;output quote instead
says to submit it at the Synthetic Student Desk. This is source/question confusion,
not harmless alternate question boundaries. The incomplete and constructed complete
controls both failed extraction. Schema-shaped JSON did not establish valid spans.

All three structured-result cases produced kind=unknown instead of structured.
They reached review and remained unresolved,with no mapped claims. Host ledger
retained unknown_requirement_kind and unmapped_claim. This prevented a document
procedure from satisfying the decision,but is NOT correct structured classification.
English extraction also dropped the course from its quote;Taglish retained final
punctuation,contrary to instructions. Filipino matched the reference span but used
the wrong kind. These are separately visible from strict-span disagreement.

All three selected procedure claims received supported verdicts;researcher inspection
finds their action in the cited fictional source,while those claims do not answer
the structured question. The supplied FIL draft contains code switching despite a
positive style verdict;no new student-facing prose was generated. No independent
human/source validation or general semantic/language accuracy is inferred.

| Language | Cases | Invalid question-span extraction | Assessed unresolved | Correct structured kind | Narrow quality successes |
| --- | --- | --- | --- | --- | --- |
| English | 4 | 3 | 1 | 0/1 | 0/4 |
| Filipino | 2 | 1 | 1 | 0/1 | 0/2 |
| Taglish | 2 | 1 | 1 | 0/1 | 0/2 |

Actual11calls:8extraction+3review,no operational transport errors,no repairs.
Strict reference agreement0/3assessed ledgers;0/8overall pass decisions when the
five extraction failures remain in the denominator. There were no mechanically
mapped ledgers. The small,familiar development set establishes no general recall.

## Freeze and reproduction

Raw root:workspace/audit-evidence/p09-question-parts-observation-20261020/.
freeze_cases.py writes8cases/author references before inference;frozen-cases SHA256
187a6d594ac8c1c9eb65aad2232f3682a9fa1d4cbe9fca2354074b6af07ea21c.
Inputs:one exact saved incomplete actual-service draft;one explicitly AUTHOR-
CONSTRUCTED complete control;the first saved claim from each of six earlier prepared
procedure/forced-structured cases. Exact questions and full integration documents
are reused. Claim selection and reconstructed multipart integration are labeled;
original full drafts/traces remain untouched. These are supplied-draft component
cases,not eight new generated answers or an institutional benchmark.

pre-inference.json binds code6073fbe,input/reference/prompt/observer hashes,source
snapshots,server props and parameters. frozen-inputs.json preserves full reference
hashes;labels were not rewritten after outputs. single-attempt.lock prevents rerun.
Per-case JSON/trace files retain messages,schemas,outputs,usage and nested timings.
assess_batch.py verifies all inputs/code/prompt bytes and records researcher findings
in root-assessment.json. No inference after the batch;no retry or settings sweep.

## Versions and measurement boundary

Existing localCUDA18088 ready,b11723-31288c9c6,context8192/output768,temp0/seed0,
cachefalse/reasoningnone. Template SHA256
74a88f94c57c14e22dcdbe08e94127f42b87c6f584cb73838e73e32126f3f6b3.
Transport240s and shared analyzer480s were observation limits;shipped pipeline
120s infer/generation/stage and180s request defaults remain unchanged. Existing
owner workspace/MODELS reused;no model download/copy/rehash or service startup.

Outer component seconds,in frozen order:21.113444,9.099365,7.803882,10.582538,
8.108561,22.817629,21.632858,20.807335. These measure extraction/review over already
prepared evidence and supplied drafts. HTTP props/template/tokenization/inference
work is included;stage durations are already nested. Five are failed-extraction
durations;three produce unresolved ledgers. NONE is complete validated-answer latency.
No routing,embedding,retrieval,Supabase,Prolog,API/browser/queue or cold startup was
measured;no isolated connection handshake,p50/p95 or student acceptance claim.
[Saved recommendation](../Context/response-time-recommendation.md) stays proposed
15-20s warm student-visible/conditional20-30s complexHybrid,accuracy first,not SLA.

## Software verification and delivery

Readiness Python3.13.7,-B -m pytest -q -p no:cacheprovider,ignored TEMP/TMP/basetemp.
- RED45expected missing-module failures1.59s. First implementation44pass/1fail1.20s:
  hand-counted test offset25should26;corrected fixture only,original log retained.
- Relevant generation/reference376passed4.44s,exit0.
- One fresh reviewae9ff28..6073fbe:no actionable finding;175passed1.89s,exit0.
  No software fix pass/re-review required;review does not certify actual model quality.
- Explicit57-selection regression gate2239passed/66subtests92.19s,exit0. Exact
  command/selections in verify-regressions.ps1,output in final-regressions.log.
  No product code changed after inference or this gate;later guide changes only.

Delivery manifest seals62fixed source/input/reference/observation/review/test
receipt files;SHA25646823c29023e5146443eeebb9bf1105f65ed8624367e13dd6d8d3c5f179e2f77.
source-inference/ binds actual code;source-delivery/ preserves current guide/test/
analyzer/evaluator. verification-commands.json retains executed commands. Later
documentation-only check logs are excluded. Prior evaluator20,foundation16 and
coverage103sealed files verified unchanged,including all three manifests.
Docs/phase gate625passed/14subtests14.09s,exit0.101local links/active snapshot
caps pass;historical123line handoff remains unchanged4022711 with its inherited
3line exception. Phase state valid,active9,cannot advance.

## Preserved boundaries and next action

Undergraduate/read-only,reviewed structured-Prolog,unknown/source-gap/privacy/source/
release holds and one-week accuracy cap persist. Context17-18/39-44,actual routing
PNG/master3/11/12.4/13/14 reconsulted;no discrepancy. No installs/downloads,training,
dependency/lock/DB changes,Phase10,push,merge,deployment or institutional activation.
Prior guard/coverage semantic P2s remain open. Do not promote this analyzer or rerun
its diagnostic;the fixed question is resolved negatively.

Next action:review remaining Phase09 quality requirements against the EXISTING
router interpretation contract,using saved failures,to decide a bounded recovery
design before further inference. Avoid accumulating another standalone classifier
or speculative runtime profile. Preserve the best verified selected candidate.
