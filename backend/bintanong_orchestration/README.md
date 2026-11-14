# Candidate runtime orchestration

Developer entry point: [pipeline map](../../docs/development/pipelines.md).
It separates source preparation, runtime requests and later generation/API work.
Phase status and exact verification live in the [checkpoint](../../plans/phase-08-checkpoint.md).

`await Orchestrator(transport, releases=provider).run(text, context)` returns a
versioned `IntegrationResult`. Imports start no server or model. The default
`HeldReleaseProvider` returns `held` before any model/evidence calls. Only explicit
`SyntheticReleaseProvider(ReleaseResources(...))` composition is delivered.

| File | Owns |
| --- | --- |
| `contracts.py` | Synthetic release membership, documentary passages/citations, common candidate evidence, integration result and safe telemetry |
| `ports.py` | Async retrieval/symbolic/release interfaces, immutable release resources and default hold |
| `adapters.py` | Retrieval debug-report conversion, typed curriculum operations and bounded thread admission |
| `integration.py` | Component presence, release/source/bundle consistency, status and permitted scope |
| `orchestrator.py` | Request validation, release pin, existing Router, dispatch, timeouts, stage events and integration |

`ReleasePin` binds source-version hashes, chunk-to-source membership and rule-bundle
version. `ReleaseResources` binds the catalog, capability registry and runtime
identity to that pin. Preserve these resources for each request; do not re-pin
between Hybrid branches. Provider metadata is trusted synthetic setup, not an
institutional authorization proof.

`RetrievalAdapter.retrieve(RetrievalRequest)` preserves retrieval status and gaps.
It normalizes absent optional locator fields without inventing source text.
`SymbolicAdapter.execute(PredicateRequest, RequestContext)` dispatches only
`check_prerequisite_eligibility`, `list_missing_prerequisites` and
`list_affected_courses`. The last operation returns a dependency listing rather
than an eligibility decision. Synthetic student assertions remain request-local
arguments; this module neither writes policy nor globally asserts student facts.

RAG executes retrieval only, Symbolic executes the typed operation only, Hybrid
executes both independent branches and waits for both. Router control outcomes
execute neither. Result observations must match the requested operation/arguments
and pinned source/bundle. Missing facts, source gaps and uncalibrated evidence
cannot become a ready conclusion. A valid synthetic prerequisite check is only
the supported prerequisite check, never enrollment/graduation authorization.

The candidate contracts do not replace institutional `EvidenceBundle` or
`AnswerEnvelope`. Offline research results remain barred from the institutional
answer pipeline. There is no automatic source loader, student HTTP endpoint,
answer generation, transcript store, private-upload parser or release activation.

See the pipeline guide for failure semantics, follow-up/session ownership,
cancellation limits and the test command. The executable composition recipe is
[test_orchestration_smoke.py](../../tests/test_orchestration_smoke.py).
