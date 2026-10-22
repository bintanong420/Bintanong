# Orchestration research and Context alignment

Requested by owner19October2026 while continuing from completed Phase08 into
Phase09 planning. This record audits the plan and delivered candidate code against
local study evidence and current primary technical documentation. It does not add
institutional policy, audience, source authority or release authorization.

## Finding

The Phase08 control-flow design fits the supplied routing diagram and the master's
implementation resolutions:LLM interpretation selects RAG/Symbolic/Hybrid, typed
executors collect evidence, integration preserves scoped decisions, and generation
is followed by validation. No agent framework or expanded study scope is needed.
This is an architecture assessment, not proof of institutional readiness or model
accuracy. The default held provider and synthetic-only composition remain necessary.

One documentation correction is required:master15 assigns private files toPhase10;
master16 assigns web/API integration toPhase11. Phase08's developer guide called
the latterPhase10. Correct the active guide; retain prior phase records as history.
One Phase09 plan refinement is required:the composed request deadline must cover
orchestration and generation together, in addition to each component's own bounds.

## Local scope and architecture evidence

Read the actual routing PNG and thesis physical17-18/39-44/58-59. The supplied PDF's
fresh SHA256 matches the existing extraction manifest:
729653540c7991496aceea1f728382d2e2262ca096e4342ce956d072e603c81c.
Text was read from the corresponding byte-matched prior extraction; no new source
conversion/download. Also read master3/11/13/14/15/16, the curriculum clarification,
undergraduate/source-gap policies, Phase08 plan/handoff/code and standing prompt
decision. No new source-content judgment or applicability approval is inferred.

| Requirement | Context / owner basis | Delivered code / planning consequence |
| --- | --- | --- |
| Undergraduate academic affairs,2026–2027; advisory/read-only | Thesis17-18; undergraduate-scope policy | Existing Router scope controls; no administrative writes or excluded-program rule substitution |
| Missing institutional information remains unavailable | Thesis17-18; source-gap policy | Explicit unknown/no_evidence/held/conflict outcomes; no parametric replacement or autonomous acquisition |
| Curriculum checks can bypass retrieval | Thesis39-40; runtime PNG; master3/11; owner16October clarification | Symbolic calls typed Janus adapter only; retain exact version-scoped structure; no requirement to embed every course question |
| Hybrid combines structured decisions with document explanation | Thesis40; runtime PNG; master13 | Independent prepared branches run together and both are required; failure cannot silently become RAG |
| Unknown completion differs from proven failure | Master11.4; standing architecture clarification | Preserve unknown over thesis41-44's illustrative closed-world denial; do not treat missing prerequisites as verified_none |
| Evidence precedes generation and validation precedes rendering | PNG; master3/14 | Phase09 strict drafts, canonical decision rendering, support/citation checks and bounded repair; no unvalidated streaming |
| Private inputs do not become institutional knowledge | Thesis18; master1/15 | Request-local assertions, no hidden transcript/global assertions/indexing; authentication/private-file handling remains later work |
| English/Filipino/Taglish preferences and inference guidance | Thesis17; owner19October prompt decision | Preserve style metadata and separately measure final language/support; no training/fine-tuning or unbounded prompt sweep |

Relevant implementation entry points:
[orchestrator](../backend/bintanong_orchestration/orchestrator.py),
[adapters](../backend/bintanong_orchestration/adapters.py),
[integration policy](../backend/bintanong_orchestration/integration.py),
[fixed Janus worker](../backend/bintanong_symbolic/_janus_worker.py).
The candidate contracts deliberately preserve the institutional answer-contract hold.
Neither matching IDs nor successful synthetic execution establishes source approval.

## Primary technical research

Context7 resolved Python,FastAPI,Pydantic and llama.cpp before scoped documentation
queries. Direct primary pages below corroborate implementation implications. These
are software references, not sources of PalSU policy. No library upgrade is implied.

| Primary reference | What it establishes | Consequence for this repository |
| --- | --- | --- |
| [Python3.13 coroutine/task documentation](https://docs.python.org/3.13/library/asyncio-task.html) | Async tasks can overlap independent work; cancelling a gather cancels unfinished children; timeout cancellation has defined behavior | Keep explicit Hybrid concurrency only after inputs are ready; propagate cancellation, classify deadline failure and retain tests |
| [Python executor cancellation](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.Future.cancel) | A running worker future cannot be cancelled by cancelling its wait | The existing adapter correctly retains its admission lock until the thread finishes; do not claim an async timeout kills embedding or Prolog work |
| [FastAPI async utilities](https://fastapi.tiangolo.com/async/#other-utility-functions) | Directly called synchronous helpers do not automatically receive FastAPI's endpoint threadpool behavior | Keep explicit offloading around blocking existing adapters; future chat API must await the orchestrator rather than call blocking helpers directly |
| [SWI Janus input bindings](https://www.swi-prolog.org/pldoc/man?section=janus-call-prolog) | Fixed query strings plus input mappings avoid interpolation/injection and repeated query compilation | Existing worker uses fixed GOAL/DEPENDENCIES and bound arguments; LLM must never generate executable Prolog |
| [SWI Janus threading](https://www.swi-prolog.org/pldoc/man?section=janus-threads) | Python threads can call Prolog; attaching engines and shared runtime state still require deliberate lifecycle handling | Keep the existing bounded worker/subprocess isolation; thread support does not authorize global student assertions or unbounded parallel execution |
| [Pydantic JSON validation](https://docs.pydantic.dev/latest/concepts/json/) and [model validators](https://docs.pydantic.dev/latest/concepts/validators/#model-validators) | Strict JSON parsing and host validators enforce typed/cross-field rules; model instances and schema descriptions are not semantic evidence | Reparse external drafts and revalidate integration; use host checks for release/citation/outcome consistency rather than trust model labels |
| [llama.cpp grammar limitations](https://github.com/ggml-org/llama.cpp/blob/master/grammars/README.md) | JSON-schema conversion supports a subset and may skip unsupported constraints; prompt instructions and grammar constraints have different jobs | Use simple constrained schemas, include instructions in prompts, keep independent backend validation and test the pinned runtime; do not infer factual correctness from valid JSON |
| [OWASP prompt-injection prevention](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html) | Retrieved text can carry indirect instructions; model output remains untrusted; model checks supplement deterministic controls | Separate trusted instructions from source/question data, validate claims/references externally and test adversarial content; a same-model support verdict is fallible |

Our inference from these references is that explicit Python control flow plus typed
ports is sufficient for the current bounded workflow. The references do not require
LangChain/LangGraph, queues, autonomous agents, new model weights or new services.
No such dependency is added. Prompt delimiters/checkers do not guarantee injection
prevention or semantic correctness; residual failures require actual evaluation.

## Actions carried into Phase09

1. Revalidate candidate integration against its pinned components before exposing
   allowed evidence cards. Preserve source/version/locator and complete conditions.
2. Render symbolic outcome and condition lists from host-owned verified results.
   Generated prose cannot replace those fields; a model agreement is not authority.
3. Validate every claim's allowed references, then require one complete, unique
   constrained support verdict per claim. Missing/malformed verdicts withhold output.
   Test fabricated citation, wrong edition, negation and source instruction attacks.
4. Retain one answer repair over unchanged evidence. Track routing repairs separately.
   The composed pipeline gets an overall request deadline; generation has its own
   bounded deadline. Never expose draft tokens before final validation.
5. Report schema/guard results separately from actual semantic support and language
   observations. The same supplied model/checker may make correlated errors; retain
   human assessment and fallback/error counts. No accuracy promise follows here.
6. Keep all inherited source/hosted-schema/style holds, private-input separation,
   accepted75question roster and one-week improvement cap unchanged. Institutional
   loading, private-file support and web/API exposure retain their own phase gates.

Fresh focused architecture regression/docs/phase gate:702passed/11subtests16.09s,
exit0. Exact raw:workspace/audit-evidence/p09-generation-20261019/
research-alignment.log. Five orchestration test files plus routing validation/
contracts,docs hygiene and phase-state tests; no model or database calls.
Research alone does not close Phase09.
