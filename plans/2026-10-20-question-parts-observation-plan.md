# Fixed question-parts extraction and review observation

20October2026;Phase09,p09,baselineae9ff28. Inline TDD,one fresh whole-change review.
Spec:master12.4/13.2/14.2,[ledger](2026-10-20-question-parts-results.md),
[reference scorer](2026-10-20-question-parts-evaluation-results.md). No runtime wiring.

**Capability:** detect every requested answer part and keep unsupported structured
decisions or omitted answers unresolved. **Evidence path:** original question,full
pinned documentary cards,supplied draft,actual extracted quotes/per-part reviews,
host ledger and separately frozen author references. **Exit advanced:** question
coverage/structured withholding. **Question:** does one fixed decomposition/review
workflow expose the saved multipart omission and distinguish supported procedures
from structured results across the existing three languages? Stop after one batch.

## Detached interface and guards

Add backend/bintanong_generation/parts.py with strict ExtractionProposal/QuotedPart,
PartAnalysis contracts and QuestionPartAnalyzer(transport,timeout_seconds=120).
await analyze(text,integration,draft) validates ready RAG and documentary draft
before inference. Under ONE overall deadline,call existing transport.infer at most
twice:extraction,then per-part support/mapping review. No retries,repair,routing,
answer generation,Prolog execution or renderer. External cancellation propagates.

Extraction emits1-8 unique r1..r8 records with kind=document/structured/unknown
and exact original quote. Pin release/question hash. Host computes Python offsets
only for unique exact occurrences;absent/repeated/blank quotes or wrong identity
reject output,never fuzzy-match/normalize it. No keyword splitting/classifier.
Use generic instructions without evaluation names/questions/examples or gold labels.

Review emits existing RequirementReview with host-pinned two identity digests,
part/claim ID schema enums and pinned nested SupportReport version. Include original
question,full documentary cards,plan and draft as untrusted data;exclude request/
session IDs,gold labels and private fact refs. Support each claim ONLY from its own
cited cards. Distinguish claims that answer a part from facts merely in sources;
unanswered draft parts are uncertain even if the source contains their answer.
No structured result exists in this RAG foundation:structured/unknown parts remain
unresolved. Existing assess_parts guards validate returned review/ledger.

PartAnalysis returns candidate-only/no-use/no-activation,semantic completeness
unverified,status(ok/invalid_output/timeout/tool_error),stage,plan/review/ledger,
call counts and total/extraction/review seconds. ok means an assessed ledger,not a
complete answer. Failures use fixed nonsensitive states,never raw exception text or
unchecked review. Keep source text complete and existing default pipeline unchanged.

## Tasks and fixed observation gate

1. [x] Focused tests/test_generation_parts.py RED,then minimal contracts/prompts/
   analyzer GREEN. Test two-call bound,typed quotes/original offsets/identity,
   missing/repeated spans,foreign part/claim IDs,private/nonready/non-RAG inputs,
   support failures,structured withholding,empty/malformed/truncated/tool failure,
   shared deadline,cancellation and concurrent request isolation. Verify all generation
   and reference scorer regressions;commit code/guide before inference.
2. [x] Freeze eight synthetic dev cases/references before first call:
   saved actual English location+fee incomplete draft;one AUTHOR-CONSTRUCTED complete
   pair using its same question/source;the existing six prepared procedure/forced-
   structured cases from coverage experiment. Reuse exact six questions,full
   integrations and first saved draft claim only,explicitly labeled a selected
   subset of saved model output. Original full drafts/traces remain unchanged.
   Positive procedure references:one document part,mapped c1. Structured references:
   one structured part,unavailable/structured_check_not_run;no document decision.
   Multipart references:two document parts;incomplete r1->c1/r2->uncertain;
   complete control r1->c1/r2->c2. Freeze exact clause quotes in raw inputs.
3. [x] ONE sequential batch,8cases/at most16calls. Reuse existing local CUDA18088
   only if ready;otherwise NOT RUN,no startup/download. Fixed transport240s,
   analyzer480s,output768,temperature0/seed0/cachefalse/reasoningnone,full sources.
   No schema/prompt/model/seed/budget changes or second run after observations.
   Save all messages/output/errors/usage/timings,prompt/schema/input/reference/code
   hashes and server metadata. Never overwrite prior evidence. This is prepared-
   integration/supplied-draft component evidence,NOT full pipeline/end-to-end timing.
   Score strict reference agreement and inspect actual semantic boundaries/mappings
   separately. Do not silently edit labels after seeing different valid boundaries.
   Report any such need as adjudication,not an established semantic error. Structured
   irrelevant draft claims remain unmapped;ledger may carry unmapped_claim as intended.
4. [x] One independent review,one TDD fix pass for important software findings only,
   explicit57-selection regression gate,dated results and compact snapshots/seals.
   Semantic failures remain open;no inference rerun to make a fix look successful.

Success for this narrow observation:all procedure positives map to their actual
answer,all structured cases classified/withheld appropriately,multipart missing fee
uncertain and complete control mapped. Schema failures/timeouts are failures,not
semantic successes. Report per-language counts and raw failures;strict span mismatch
and researcher semantic assessment stay separate. Even a clean8case result is too
small for general recall,student validation or default/runtime promotion.

## Verification and preserved boundaries

Existing readiness Python3.13 -B -m pytest -q -p no:cacheprovider,ignored TEMP/TMP/
basetemp under workspace/audit-evidence/p09-question-parts-observation-20261020/.
No installs/downloads/model copy/DB/dependency/lock changes or training. Supabase
readiness/database/retrieval/Prolog/browser/API/queue/startup are NOT measured here.
Accuracy first;[saved target](../Context/response-time-recommendation.md) remains
proposed15-20s warm student-visible/conditional20-30s complexHybrid,not achieved SLA.
Undergraduate/read-only/structured-Prolog/unknown/source-gap/privacy/release holds
and one-week cap persist. Context17-18/39-44,actual PNG/master3/11/12.4/13/14 consulted.
No Phase10,push,merge,deployment,institutional activation or selected-profile change.

Review focus:quote resolution cannot hide an omitted requirement;review identity
cannot cross requests/drafts;no raw identifiers/gold labels in messages;one deadline
and at most2calls;component timings are not validated answer or browser latency.
Ruling:owner continuation authorizes this bounded reversible candidate experiment;
prompt guidance remains inference-only. No repeated failed aggregate-checker sweep.

Task1:RED45expected missing-module assertion failures1.59s. First implementation
44passed/1failed1.20s:hand-counted Unicode end offset25 was wrong;visible quote is
15characters at11..26. Corrected test expectation only,retaining original log.
Relevant generation/reference GREEN376passed4.44s,exit0 (green-verified.log;
relevant-selections.txt). No selected runtime change or inference yet.
Task2:8cases frozen at6073fbe;frozen-cases SHA256
187a6d594ac8c1c9eb65aad2232f3682a9fa1d4cbe9fca2354074b6af07ea21c.
Independent code reviewae9ff28..6073fbe:no actionable findings,175passed1.89s.
Observer records exact outputs/schemas/messages/usage/timings and a single-attempt
lock;code/inputs/prompts snapshotted before first inference. No correction sweep.
Task3:ONE batch8cases/11calls finished;quality FAILED0/8. Five invalid source-copy
extractions blocked review;three unknown-kind structured cases safely unresolved.
No corrected run or settings change. assess_batch.py verified frozen inputs/code,
messages/schemas/outputs and origins;root-assessment.json preserves exact findings.
Task4:review found no actionable software defect,no fix pass/re-review required.
Final57-selection gate2239passed/66subtests92.19s,exit0;semantic gate still FAILED.
62sealed files,manifest46823c29023e5146443eeebb9bf1105f65ed8624367e13dd6d8d3c5f179e2f77.
Prior20+16+103sealed files verified unchanged. See
[results](2026-10-20-question-parts-observation-results.md) for exact limits/recovery.
