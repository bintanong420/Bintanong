# Request understanding recovery design

20October2026;DESIGN ONLY. Existing selected behavior remains unchanged. This
follows the [failed part analyzer](2026-10-20-question-parts-observation-results.md)
and the owner's request for meaningful validation. No new inference authorized by
this document alone;implementation still needs its bounded TDD plan/observation gate.

## Problem and inspected evidence

The selected router already interprets original text BEFORE retrieval/Prolog.
Its Interpretation contract records language,audience,intent,mentions,claims,
operations and one route/control,but no explicit list of requested answer parts.
RoutingResult retains that proposal locally;IntegrationResult passes route/style/
evidence/missing facts to generation and drops the interpretation. Generator thus
cannot mechanically distinguish every requested document detail. A whole-question
coverage verdict later missed a requested fee despite its presence in source text.

The detached analyzer then received sources during extraction and copied source
sentences into question-quote fields in5/8cases. All3structured requests were
classified unknown. These observations establish failures,not a proven causal
claim that source removal alone will fix the model. Do not repeat that batch.

Inspected files:backend/bintanong_routing/{contracts,prompt,router,validation}.py;
backend/bintanong_orchestration/{orchestrator,contracts}.py;
backend/bintanong_generation/{generator,requirements}.py. Relevant master3/11/
12.4/13/14,thesis17-18/39-44 and actual routing PNG support pre-evidence
interpretation,reviewed Prolog decisions and validated documentary explanation.

## Proposed change at the existing interpretation boundary

Extend the EXISTING semantic interpretation output with1-8 requested parts,
without another classifier call or developer profile. Use an explicit new contract
version and reject old payloads at the new boundary;do not silently treat an old
interpretation without parts as complete. Preserve separate response-style call,
existing single shared format repair and operation/capability guards. No combined
routing/style revival,keyword classification or generation-side rerouting.

Proposed RequestPart:part_id r1..r8,exact original text/start/end using Quote,
evidence_need=document/structured/unknown,and operation_indices0..3. Document
parts have no operation indices. A structured part can have none when its required
operation is unsupported/unresolved;that is a missing capability,not document-only
work. Preserve every request,its course/subject,negation/condition/date and operation
association. Do not fabricate policy facts or use a blank prerequisite as none.
Greeting/excluded controls retain empty parts and existing precedence.

Existing prompt gets original question,trusted scoped context,reviewed entity aliases
and capability names. It receives NO retrieved documentary cards,no draft,no gold
reference and no source-content examples. Host anchoring reuses exact quote logic;
ambiguous repeated text needs valid original offsets or clarification,not guessed
selection. Model parts remain untrusted;they cannot create rule authority.

Host consistency checks compare the ONE proposed route with declared evidence needs:
document-only ->RAG,structured-only supported operation ->Symbolic,both ->Hybrid.
Unknown part or unavailable structured operation prevents an unrestricted answer;
use existing clarification/evidence-unavailable control. Never downgrade a missing
structured capability to RAG. Multiple operations retain the existing compound-
request clarification boundary. These checks compare declared fields;they do not
constitute a second semantic router or prove extraction completeness.

## Carry understanding to output validation

RoutingResult carries validated parts. Orchestrator binds their exact original
question hash and request/release identity after pinning,and passes a typed plan
through an explicitly versioned IntegrationResult boundary. Keep original spans
and reviewed operations distinct from retrieved policy content and private fact IDs.
Update all producers/consumers together;no optional empty-plan compatibility default
that could silently restore coverage blindness. Historical observation loaders remain
separate and must not promote old artifacts into the new runtime contract.

Generation must address each declared part through an actual claim,canonical
structured result or explicit unresolved state. A Prolog prerequisite check does
not cover full enrollment. Supported documentary prose cannot satisfy a structured
part. Reuse the existing ledger/reference-evaluation ideas where applicable rather
than maintaining independent copies;RAG-only helper support does not imply Hybrid/
Symbolic implementation already exists. Per-part support can be integrated into
the existing documentary checker only after bounded validation. Keep source cards
complete,release binding,one repair/deadline and no unvalidated streaming.

## Minimum meaningful verification before implementation/promotion

Write tests only where a realistic regression could break a required boundary:
missing/duplicate/misbound parts;wrong request/release;unknown operation silently
becoming RAG;structured part answered by document;compound requests losing a part;
missing document detail incorrectly marked complete;language call/counter changes;
privacy/cancellation/deadline propagation. Reuse existing schema/quote/operation
tests;do not add constructor or copied-prompt wording tests for each new field.

Before ANY new inference,freeze questions,independent expected part/operation
labels,prompt/code/schema/model/settings hashes and strict/semantic scoring criteria.
Reuse accepted institutional wordings only within their gates or explicitly fictional
dev fixtures;do not silently turn the known failed set into unseen validation.
One bounded actual-model gate must measure extraction,route,required operation,
part coverage,source support and language separately. Schema success/mocked positive
verdicts or safe abstention alone do not establish those outcomes. Failed required
capabilities block promotion;no prompt/model/seed/budget sweep to obtain a pass.

This design does not yet choose new benchmark wording or claim improved quality/
latency. Existing timing target/exclusions,accuracy-first rule,undergraduate/read-only/
structured-Prolog/privacy/source/release gates and one-week cap remain. Do not start
Phase10 or activate institutional use. Next implementation should be one coherent
router-to-output contract change,with actual quality validation before selection.
