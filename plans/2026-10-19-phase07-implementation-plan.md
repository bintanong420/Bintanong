# Phase 07 routing implementation plan

> Execute inline with executing-plans and test-driven-development. Owner explicitly
> accepted the scope and directed implementation: “proceed to phase 07 lets go!”

Goal: validated multilingual LLM interpretation/routing with scoped entities,
request-local claims, response-style metadata and reproducible offline evaluation.
Architecture: one Bintu JSON proposal followed by deterministic shared-contract
validation; no retrieval/Prolog execution or API publication.
Tech: existing Python3.13/Pydantic2/HTTPX and owner's existing Gemma GGUF.
Spec: [accepted design](2026-10-19-phase07-routing-design.md).

## Global constraints

English -> English; Taglish -> Taglish; Filipino -> predominantly Filipino with
natural technical terms. Prospectus checks primarily structured/Prolog; documents
primarily RAG; Hybrid requires both. Preserve unknowns, scope, negation, source gaps
and session separation. Institutional registry empty, candidates inactive. No
installs, dependency changes or weight copies. Owner corrects model root to
C:/Coding-projects/bintanong_workspace/MODELS; use existing assets in place.

## Review focus

- Genuine quote/span does not prove model meaning: evaluate fact errors separately.
- Reused course aliases must not select a curriculum from a course name.
- Repair cannot introduce unsupported operations or silently choose RAG.
- Failures must not log personal text or grades.
- English course codes alone do not make a Filipino question Taglish.

## Task 1: interpretation and request boundary

Files: backend/bintanong_routing/__init__.py, contracts.py;
tests/test_routing_contracts.py.
Interfaces: RequestContext carries session_id/request_id, explicit program/curriculum
and scoped session facts. Interpretation carries language/audience/intent, grounded
mentions/claims, proposed route/control, operations, ambiguities and short reason.
prepare_query(text: str) -> str applies only NFC and whitespace cleanup; reject
empty, malformed/control text, >8192characters or >16384UTF8bytes. Claims name
mention indices and original quoted offsets; model never supplies trusted IDs.

- [ ] RED: normalization preserves “Hindi pa passed ang A1 next sem”; invalid or
  oversized text, foreign sessions, duplicate IDs, Direct, extras, coercion and
  invalid mention/claim indices fail.
- [ ] Implement strict immutable records from shared Record/Contract.
- [ ] GREEN: focused tests plus runtime/legacy-client contract regressions.
- [ ] Commit verified increment with checkpoint evidence.

## Task 2: scoped resolution and effective decision

Files: backend/bintanong_routing/validation.py; tests/test_routing_validation.py.
Interfaces: CatalogEntry carries kind/id/program/curriculum, reviewed aliases,
source/review references (trusted injection, not source authorization).
validate_interpretation(text, context, interpretation, *, catalog=(),
registry=EMPTY_REGISTRY, documents_available=False, synthetic=False) -> RoutingResult.
Result carries shared NormalizedQuery/RoutingDecision, proposed interpretation,
grounded claims, response style and fixed diagnostic codes.

- [ ] RED: scoped exact aliases resolve; ambiguous/wrong editions clarify; only
  explicit context or corresponding scope mentions select program/curriculum.
- [ ] RED: one supported operation yields bound data; empty registry withholds it;
  unavailable documents withhold RAG/Hybrid; multi-requests, hypothetical/conflicting
  facts and material ambiguities clarify. Missing completion is not failure.
- [ ] Implement exact resolution and operation validation; host mints request-scoped
  claim IDs. Do not enable institutional execution through injection.
- [ ] GREEN: new suites and existing shared/symbolic contracts; commit increment.

## Task 3: versioned prompt and bounded model transport

Files: backend/bintanong_routing/prompt.py, transport.py, router.py;
tests/test_routing_transport.py, tests/test_routing_router.py.
Interfaces: LlamaTransport(base_url, *, timeout_seconds=120, max_output_tokens=768,
constrained=True, client=None). infer(messages, schema) -> str counts complete
chat-template input with actual n_ctx and output reserve before inference.
Router.route(text, context) -> RoutingResult permits one format/schema repair.
No semantic rerouting or execution. Inject transport for boundary tests.

- [ ] RED: HTTP MockTransport verifies template/token/props and JSON payload;
  initial/repair overflow prevents inference; timeout/non200/oversized/malformed
  responses have nonsensitive codes.
- [ ] RED: language style survives; invalid JSON repairs once; second failure stops;
  semantic hold never retries or substitutes RAG.
- [ ] Implement versioned prompt, complete-message token budget, strict output,
  prompt/schema hashes and attempts without raw-text telemetry.
- [ ] GREEN: all routing and relevant regressions; commit increment.

## Task 4: offline evaluation and recovery documentation

Files: backend/bintanong_routing/evaluation.py, README.md;
tests/test_routing_evaluation.py; plans/2026-10-19-phase07-routing-evaluation.md.
Interface: async evaluate_cases(router, cases, metadata) -> dict. Synthetic dev
cases name family/language and expected route/control/entity/claim/style. Report
raw proposals separately from effective controls, confusion matrices, per-language
and equivalent-family results, semantic errors, failures and repair counts. Record
case/model/runtime/prompt/schema identities and decoding; gold never enters prompts.

- [ ] RED: wrong proposal remains wrong behind a safe guard; failures remain in
  denominators; duplicate IDs, mixed dev/final splits and inconsistent families fail.
- [ ] Implement evaluation and a CLI with explicit JSON input/ignored raw output.
- [ ] GREEN: routing suites, legacy/runtime contracts, Phase06 regression gate and
  phase-state checks; inspect all results and record bounded coverage.
- [ ] Run existing Gemma on generic synthetic EN/Filipino/Taglish development
  fixtures if existing runtime is available. Mocks are not model accuracy. New
  institutional wording/route labels retain applicable review requirements; do
  not redo retrieval or invent policy to fill capability gaps.
- [ ] Fresh whole-change independent review; important fixes get RED/GREEN.
  Commit final verified increment. No Phase08 advancement without full exit/handoff.

## Execution ledger and rulings

Owner's explicit “proceed” accepts design and execution already described; no
second scope approval is requested. Pre-flight:tasks2/3/4 consume task1 records;
task3 consumes task2 RoutingResult; transport returns text only; task4 separately
observes proposed/effective outputs. No competing contract/executor is introduced.
Checkpoint is the durable ledger; raw logs and test temporaries reside under
workspace/audit-evidence/p07-implementation-20261019. Owner evidence location
overrides skill-default scratch paths. Missing model/runtime blocks actual model
exit only; leave phase active with one exact next action if unavailable.
