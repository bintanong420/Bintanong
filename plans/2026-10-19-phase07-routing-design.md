# Phase 07 multilingual interpretation and routing design

Status: accepted for implementation, 19 October 2026: “proceed to phase 07 lets go!”
The owner requested continuation
into Phase 07 in the existing p07 worktree and specifically reminded this agent to
check Context. Owner19October2026 explicitly confirms the evidence roles and
response-language requirements below, then authorized implementation.

## Purpose and inherited state

Let a student ask an undergraduate academic-affairs question naturally in English,
Filipino or Taglish. Bintu interprets the question and chooses the required evidence
path, or identifies a reason the request cannot proceed. Students need not name a
memo or repeat the website's undergraduate audience. Program/curriculum and personal
facts are requested only when they materially affect the requested check.

Baseline c5f110b includes the other developer's completed Phase 06 and the receiving
developer's accepted audit. Reuse its three typed operations, reviewed BSCS scope,
unknown semantics and fixed-goal boundary. Do not reopen source reviews, demand
missing historical receipts or reactivate institutional capabilities. Phase 06's
73-case verification is accepted predecessor evidence, not a new local replay.

## Architecture and boundaries

Owner-confirmed evidence roles: prospectus/curriculum knowledge primarily belongs
in reviewed structured facts and deterministic Prolog checks for prerequisites,
eligibility and dependencies. Handbook, Citizens' Charter and memorandum content
primarily supplies cited RAG explanations and procedures. Hybrid combines a
structured check with a document explanation or next-step procedure when both
are needed. These roles apply equally across English, Filipino and Taglish.

Choose the actual route by the requested evidence/operation, not the PDF extension
or language. Exact curriculum facts use scoped structured operations once those
operations exist; unsupported operations remain unavailable. Curriculum explanatory
text can still supply citations. Do not use vector similarity to determine
eligibility or turn a retrieved handbook/memo clause into an executable rule
without its separately reviewed authoring/capability work.

Bintu remains the semantic interpreter/router. No keyword classifier, trained
replacement router, semantic-search eligibility decision or general-chat policy
answer is introduced. Minimal Python normalization, exact entity resolution and
capability validation check Bintu's output; they do not choose its semantic route.

Use one structured model call initially, with interpretation and routing fields
separately visible. Keep the existing shared NormalizedQuery, RoutingDecision,
PredicateRequest and CapabilityRegistry contracts. Add a small routing package
around them rather than a competing fourth-route contract. The legacy client and
its Direct value have no dispatch role in this new path. Preserve its historical
adapter refusal until deliberately retiring that consumer; never map Direct by
guessing whether it meant a greeting or an excluded request.

Phase 07 produces validated routing data, not final student answers. Retrieval,
Prolog execution and combined EvidenceBundle assembly belong to Phase 08; response
generation belongs to Phase 09. The new router does not call those executors,
publish an API, change source lifecycle state or fill EMPTY_REGISTRY. Synthetic
capabilities are explicitly injected in offline tests. Institutional loading and
activation remain independently gated.

## Owner-confirmed response-language preference

| Student query | Intended response style |
| --- | --- |
| English | English response throughout. |
| Tagalog mixed with English / Taglish | Natural Taglish response using both languages. |
| Tagalog / Filipino | Filipino throughout where practical; otherwise predominantly Filipino with familiar English technical or institutional terms. |

Do not force awkward literal translations of course names, codes, official terms
or concepts with no useful Filipino equivalent. Preserve their meaning and use
natural conversational Filipino around them. The owner's preference for a high
Filipino proportion is qualitative; no numeric word-ratio threshold is specified.

Phase07 carries the intended response language/style in the interpretation
envelope for later answer generation, including clarification and fallback text.
Keep it distinct from routing and from evidence language. Route/meaning consistency
across languages remains required; response style is not a reason to change the
selected evidence path. Answer generation and its language-quality evaluation
remain later-phase work; this records their required behavior now.

Implementation recommendation: infer conversational style from the student's own
question, rather than treating one course code, an official source title or a
quoted English passage as enough to make a Filipino question Taglish. Evaluate
these cases with synthetic interpretation fixtures without inventing new PalSU
benchmark approvals.

## Image attachments reserved for later phases

Owner confirms students will eventually be able to attach an image with a query.
This remains later-phase upload/private-context work (master15/Phase10); do not
add image upload, OCR or a vision-model dependency to Phase07. Its future extracted
context must preserve session ownership and extraction uncertainty, remain separate
from institutional knowledge, and never install rules or verify policy authority.
The student's language preference remains applicable when the query has an image.

## Observable request flow

1. Accept text plus a trusted request-context object. Session-owned facts supplied
   by the embedding application must match that object's session; reject foreign
   references. Phase 07 validates this boundary, not browser login or authentication.
2. Preserve original text. Apply NFC and whitespace cleanup only; reject malformed
   Unicode and oversized requests. Preserve negation, numbers, temporal qualifiers,
   hypothetical language and words such as hindi, di, pa, passed and failed.
3. Construct messages from a versioned prompt, available capability descriptions
   and explicitly scoped alias data. Token budgeting uses the actual local model's
   tokenizer/chat template and reserves output space; never use SEA-LION counts.
   Count the complete messages, including any repair context. Do not silently clip
   decisive text, assume the scaffold's 128 output tokens suffice or change pins.
4. Bintu returns language/intent, literal entity mentions, asserted versus
   hypothetical or reported claims, ambiguities, route/control proposal and a short
   reason. User text and alleged policies remain untrusted data. No private grade
   or full query text goes into routine telemetry; raw synthetic offline evidence
   is kept separately in ignored workspace storage.
5. Resolve only unique aliases against injected reviewed identities within the
   explicitly known program/curriculum. Retain the original mention. Never infer
   /L equivalence, a proposed edition's authority, curriculum from student age or
   continuing status, or equivalent courses from similarity. Unknown/ambiguous
   identifiers trigger clarification where they matter. No aliases are invented
   from previously accepted benchmark wording.
6. Validate the proposal against shared contracts, scoped identifiers, operation
   signatures and grounded request-local fact references. The model cannot create
   facts, policy, capability registrations or executable Prolog. Numeric grades
   do not become pass/fail without separately reviewed grade rules. Missing course
   outcomes remain unknown; hypothetical or friend-reported outcomes are not
   silently asserted as actual student records. A sufficiently scoped hypothetical
   may be represented explicitly, without persisting it as actual history.
7. Return interpretation plus an effective RoutingDecision. Retain the model's
   proposed route for evaluation even when validation withholds it. Only an
   effective validated route is eligible for a later executor. Unsupported or
   unavailable required capabilities produce a control outcome, not RAG fallback.

Missing structural arguments such as curriculum or target course block dispatch.
Do not require a complete transcript for every check: Phase 06 already represents
unknown outcomes and can identify a documented unmet prerequisite from supplied
facts. Phase 07 must not replace those semantics with an invented completeness
rule, infer unmentioned passes or decide eligibility itself.

## Routes, controls and failures

Builder-check decisions (agent recommendations, not owner decisions): Bintu may
extract self-reports from the current utterance as candidate claims with exact
original-text offsets/quotes, course mention and actual/hypothetical/reported
mode. Backend code checks those spans, resolves entities and mints request-scoped
fact IDs; the model never assigns trusted IDs or supplies an untraceable fact.
Explicit self-reports do not require routine owner confirmation and remain labeled
student assertions, not official records. This proves textual provenance, not
semantic correctness; language/fact extraction errors require model evaluation.
Contradictory material claims versus current trusted session context remain visible
and yield clarification; do not overwrite history. Hypothetical assumptions are
returned in a separate mode and never persisted as actual history. The future
executor must explicitly support that mode before it can consume such facts;
until then the effective outcome is clarification, with the proposed route kept.
No extracted assertion is converted into the synthetic-only StudentFacts contract
or sent to Prolog in Phase07. The new interpretation envelope carries these
grounded claims beside the existing NormalizedQuery references and decision.

The initial effective decision supports one operation and target. Preserve all
requested parts in the interpretation. When multiple targets/operations are
required, return clarification asking which check to do first; do not silently
drop a request, invent a batch contract or implement Phase08 orchestration.
One supported check plus a document next-step request remains ordinary Hybrid.

| Output | Meaning |
| --- | --- |
| RAG | Applicable document explanation or procedure; no structured student decision. |
| Symbolic | Supported, scoped structured operation; document citations can later be fetched by exact provenance. |
| Hybrid | Both structured evaluation and a document explanation/procedure are required. |
| clarify | A material identity, scope, intent or argument is unresolved. |
| greeting | Social acknowledgement without an institutional claim. |
| unsupported_scope | Explicitly excluded audience/procedure or unrelated request. |
| evidence_unavailable | In-scope information/capability unavailable, invalid output or operational failure; retain a separate diagnostic code. |

A route and control are mutually exclusive in the effective shared contract.
Undergraduate Nursing and shared student services remain in scope; a staff role
mentioned inside a student procedure is not enough to reject the request. Missing
in-scope information differs from excluded audience. Current-year requests do not
verify source currentness. This design does not answer the held F04 fee digit or
complete clipped source text.

Use constrained JSON decoding when verified against the installed server. Backend
validation is mandatory even then. Otherwise use strict JSON parsing and at most
one format repair, without relaxing semantic/capability checks. Record attempts
and failure codes. A timeout or unavailable server stops with an explicit failure;
do not retry indefinitely or choose a cheaper evidence path. No semantic
reconsideration is implemented initially; future correction must have its own
explicit bound. Model confidence is not a calibrated acceptance threshold.

## Delivery increments and verification

- Request/interpretation contracts and minimal normalization, with synthetic
  regressions for negation, Unicode, temporal qualifiers, hypothetical claims and
  session ownership, plus English/Taglish/Filipino response-style metadata.
  Preserve existing contract/legacy-adapter tests.
- Scoped exact resolution and validation against the existing capability boundary;
  regress ambiguous aliases, wrong editions, extra/missing arguments, invented
  facts, unsupported operations and closed institutional execution.
- Versioned prompt and model transport with chat-template token accounting,
  constrained output or one bounded repair, typed failures and no text/grade logs.
- Offline route evaluation that reports raw proposed route, validated outcome,
  confusion matrices, per-language results, equivalent-variant consistency,
  entity/fact errors, controls, failures and repair counts separately.

Every implementation increment uses focused RED/GREEN tests, appropriate
regressions and a small Conventional Commit. Exact interfaces/test assertions go
in the implementation plan after this design is accepted. Pure code tests may
proceed with injected fake transports; they do not prove Bintu language accuracy.

Reuse the accepted 75 development variants and their exact wording/limitations
where relevant; do not regenerate embeddings or repeat settled retrieval probes.
Review any new route/control labels before institutional route evaluation. Show
new or changed institutional benchmark wording to the owner before testing it.
Tracked generic synthetic tests are not new PalSU policy/benchmark approvals.
Keep sealed final question families separate from prompt-development families.

Exit requires the tested contracts, resolution, versioned prompts and an actual
Bintu evaluation report with model/runtime/prompt/schema hashes, decoding settings,
case split and per-language route/meaning results. Deterministic boundary tests
must show invalid proposals cannot become dispatchable. Report observed routing
accuracy and all critical errors without inventing an approved numeric threshold.
An unavailable model leaves the actual-model exit pending; mock success cannot
complete Phase 07. No Phase 08 advancement without the formal verified handoff.

## Environment and evidence checked

Worktree: C:/Coding-projects/bintanong_workspace/worktrees/Bintanong/p07,
branch feat/p07-router-taglish-nlp; clean baseline c5f110b. Main checkout dev is
also c5f110b; old local p06 is stale and is preserved. GitHub MCP on 19 October
reports remote dev 380551a and remote p06 6923835. Do not roll back local dev,
merge unrelated work or infer unpublished audit notes have been pushed.

Python 3.13.7 is available. Reuse the existing Python 3.13 readiness environment
for installed pytest/Pydantic/httpx/Janus; no installs or lock changes authorized.
Configured llama.cpp image is server-v0.4.1; actual server compatibility is NOT
verified here. Context7 official llama.cpp docs consulted for constrained chat
output and chat-template/token-count endpoints; verify the deployed build rather
than assuming current docs match this historical image. See the
[official server documentation](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

Kickoff observed C:/Coding-projects/MODELS absent and no local8080 listener.
Owner corrected the current root to C:/Coding-projects/bintanong_workspace/MODELS
and confirms Gemma is there. Use the existing weights in place; do not copy them.
No runtime URL was supplied. The configured GGUF name is Gemma-4-E4B; do not claim
this proves a distinct fine-tuned Bintu-1 model identity. Before actual evaluation,
resolve the intended existing model/server, its identity and digest with the owner.
Do not download/copy weights or start paid remote inference by assumption.

Context freshly extracted: thesis physical 17-18/39-44/58-59; cached scope-page
renders and actual runtime-routing PNG viewed. Thesis SHA256:
729653540c7991496aceea1f728382d2e2262ca096e4342ce956d072e603c81c.
Master sections 3/11/12/13, scope/source-gap policy and curriculum-routing
clarification consulted. Missing-fact unknown semantics follow master 11.4 and
owner instructions over the illustrative thesis closed-world denial. Diagram and
master route-before-execution/evidence-before-generation govern over thesis p59's
older universal retrieval and generation-before-validation description.

Raw kickoff evidence: workspace/audit-evidence/p07-kickoff-20261019/.
Fresh builder review raised fact provenance and multi-operation handling; the
decisions above resolve both without changing the fixed phase boundary.
Evidence roles, response-language preference and deferring image attachments are
explicit owner requirements. Other proposed implementation choices are the
agent's recommendations; no new source approval, institutional release or deployed
behavior is established.
