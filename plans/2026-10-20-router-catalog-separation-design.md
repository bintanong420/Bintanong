# Proposed router catalog separation

Phase09;20October2026;baseline7e150ed/product062589c. Status:proposed,NOT approved
or implemented. Design only;no new inference,product code or service operations.
One fresh read-only builder check found no material unanswered question,
substantive contradiction or unsupported benefit claim. No second check needed.
Uses [sealed v12 failures](2026-10-20-semantic-guidance-observation-results.md),
the [standing owner approach](2026-10-19-prompt-engineering-and-validation-decision.md)
and the existing LLM/structured-Prolog/RAG architecture.

## Capability,question and limits

Student capability:ask ordinary documentary questions without irrelevant course
facts being inserted,and retain correct target/failure/parts for Hybrid requests.
Evidence path:LLM literal interpretation -> exact host quote normalization ->
reviewed alias/scope resolution -> RAG/Prolog as requested -> validated answer.
Phase09 exit advanced:correct complete evidence-backed output for the intended
question. Unresolved question:does supplying the entire curriculum alias catalog
to literal extraction contribute to the observed metadata-only course mentions?

All three v12 documentary questions emit ZX101,which exists in the supplied
catalog but not the question. Both proposals per case reject at exact grounding.
The Hybrid case uses the actual courses correctly and passes. This establishes
the failed boundary,NOT the model's internal cause. Removing catalog exposure
may help,may do nothing,or may harm correct entity interpretation. Coalesced
question parts are a separate remaining failure;this design does not explain
them away or weaken their quality criterion. Do not claim a general model limit
or a proven catalog cause from four cases.

## Choices and recommendation

| Choice | Consequence |
| --- | --- |
| Keep present candidate and stop experiments | Preserves known1/4result and safeguards;does not satisfy the actual quality gate or close Phase09 |
| Keep catalog host-side during literal extraction (recommended) | Changes one input boundary using an existing resolver;no new model,call or guard;needs measured verification |
| Add a separate semantic extraction/classifier stage or change model | Broader architecture/runtime decision with new cost/accuracy evidence;not selected or implicitly authorized |

More instructions/examples and silent deletion of invented mentions are rejected:
the stopped prompt sequence does not justify another admonition or hiding errors.
Do not substitute keyword routing or infer eligibility from similarity.

## Proposed contract and precise scope

Keep build_messages(text,context,catalog,registry) callable compatibility. Continue
passing the full reviewed catalog unchanged to Router/CombinedRouter and their
existing validate_interpretation calls. Omit ONLY reviewed_aliases from the
model-visible data object. Remaining fields stay original_text,normalized_text,
context(program_id,curriculum_id,facts with course_id/state) and available_operations.
No new conversation-memory/anaphora capability is implied;current request/context
semantics remain. Session/request/private fact IDs stay excluded as before.

The LLM still chooses audience,language,route/control,mentions,claims/modes,
operations and requested parts from the original question. It emits quoted
references,never canonical institutional identities or executable Prolog. The
host already resolves each quoted mention through the full reviewed catalog,
checks actual curriculum/program and combines scoped supplied session facts.
Canonical scope remains available to all existing host checks/dispatch;it is
not guessed or removed. A missing/ambiguous/conflicting alias still clarifies.

Adjust prompt wording only where it falsely says the interpreter receives
reviewed aliases;explain that the host resolves identities after literal extraction.
Preserve the one v12worked example and all other task guidance. Router promptv13,
combined promptv4;combined remains explicit/unselected and inherits the same payload.
No decoder/schema/normalizer/host resolver/repair/generation/Prolog/rule-data change.
No host alias prefilter against keywords,no second LLM/classifier,no extra retry.
Keep supplied Gemma/Bintu,ctx8192,out768,temp0,seed0,cachefalse,requested reasoningnone
and120/120/120/180s budgets. No training,downloads,dependencies,startup or DB changes.

Catalog-based extraction hints would be lost. An unfamiliar abbreviation could be
misclassified or missed,and metadata in the retained context or the existing
fictional example can still be copied. Exact quote guards still reject invented
entities;they cannot prove every intended mention,claim or part was extracted.
Host tests and the limited actual gate cannot establish broad multilingual safety.
No quality or latency improvement is assumed from removing input bytes.

## Reviewable acceptance and stopping boundary

Implementation only AFTER explicit approval of this input-boundary change. Use
inline focused TDD and one whole-change reviewer;no repeated review/model sweeps.

1. Actual separate/combined model-visible payloads omit the catalog. For the same
   request/context/registry,different catalog contents produce identical messages.
   Preserve all other payload fields and original question/private-ID exclusions.
2. At real Router boundaries,a scripted literal packet still resolves against the
   host's catalog and selected curriculum. Unknown/ambiguous/cross-edition aliases,
   scope conflicts,conflicting session grades and nonasserted modes retain guards.
   Existing tests can supply regressions;add only distinct uncovered boundaries.
3. Observe focused RED before implementation;minimal prompt/payload/version edits,
   GREEN and relevant routing regressions. Scripted tests prove host behavior and
   input separation,NOT that the LLM extracts the right mentions or meaning.
4. Freeze changed software,then bind ONE separately defined actual observation
   BEFORE inference. Reuse the same4unchanged developer cases/references/order and
   finite budgets/call limits. Preserve all three document parts/meaning failures
   in assessment;the model must still succeed at separate details and Hybrid.
   Require4/4response AND full-quality pass for this limited gate;even4/4does not
   establish population accuracy,pure Symbolic or all-language Hybrid performance.
5. Any regression/incomplete meaning blocks promotion. Stop on failure and discuss
   capability/model limits;no rescue probe,next prompt fix or silent host rewrite.
   A passing limited gate permits planning remaining approved coverage,not Phase10.

The prior stopped observation and seals remain unchanged. Four explicit if/kung
cases stay held for the unanswered conditional-answer decision. This design does
not authorize hypothetical execution or promote reported/assumed grades to actual.
Undergraduate/read-only/source-gap/privacy/institutional-release/one-week holds
and accepted75wordings persist. No source decision,activation,push or deployment.

## Timing and phase estimate

No inference or latency measurement in this design. A later component observation
must exclude/report actual retrieval/Supabase/API/browser/startup/load factors as
before;input-byte reduction is not a measured speedup. Preserve the saved browser
15-20s/conditional20-30complexHybrid proposal and accuracy-first requirement.
The earlier4-8active-hour Phase09 estimate remains low-confidence after the failed
gate. This design is one bounded decision,not permission to keep tuning until a
time target passes. All remaining route/language/exit evidence still applies.
