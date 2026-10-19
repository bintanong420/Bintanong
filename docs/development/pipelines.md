# Developer pipeline map

Read this after [AGENTS.md](../../AGENTS.md) and the [phase index](../../plans/INDEX.md).
The [master plan](../../plans/master_implementation_plan_original_long.md) defines
the intended system; this guide maps it to code and states what runs today.

Phase 08 delivers **internal candidate orchestration with synthetic release
injection**. The default provider holds execution. There is no student chat
endpoint, institutional release loader, final answer generation or deployment.
Source authority/currentness, held fields and hosted migration gaps remain open.
The existing 75 accepted institutional question variants were not rerun here.

## Two separate pipelines

Institutional preparation happens outside student requests. Private uploads and
conversation facts never update it.

```mermaid
flowchart LR
    S[Original sources and source register] --> I[Ingest and human content review]
    I --> D[Reviewed documentary chunks]
    D --> E[SEA-LION embedding artifacts]
    E --> V[Release-scoped vector storage]
    I --> A[Reviewed structured curriculum ledger]
    A --> P[Generated Prolog bundle and verification]
    V --> R[Authorized compatible knowledge release]
    P --> R
```

The release box is a required authorization boundary. Having candidate files,
matching IDs, parser success or a synthetic test result does not pass that boundary.

| Preparation responsibility | Code / evidence entry point |
| --- | --- |
| Source intake, originals, review holds | [Storage](../../backend/bintanong_storage/README.md), [scope](../../plans/undergraduate-scope-policy.md), [gaps](../../plans/source-gap-policy.md) |
| PDF ingestion and curriculum extraction | `backend/bintanong_tools/document_ingest/`, `backend/bintanong_tools/prospectus_extractor/` |
| Embedding preparation | `backend/bintanong_embedding/` |
| Versioned storage and release controls | `backend/bintanong_storage/`, `supabase/migrations/` |
| Structured authoring, compiler and Janus runtime | [Symbolic module](../../backend/bintanong_symbolic/README.md) |

The student request pipeline has one release pin and one validated route. An LLM
selects the route; host code checks identities, arguments and evidence boundaries.

```mermaid
flowchart TD
    Q[Text and caller-owned RequestContext] --> P[Pin release resources once]
    P --> L[Existing Router: LLM interpretation and response style]
    L --> G{Validated route or control}
    G -->|clarify / greeting / scope / unavailable| C[Control result; no evidence execution]
    G -->|RAG| R[RetrievalAdapter: embedding and retrieval engine]
    G -->|Symbolic| S[SymbolicAdapter: fixed typed operation through Janus]
    G -->|Hybrid| H[Both independent branches; wait for both]
    R --> I[Integration policy: membership, version, gaps, outcomes]
    S --> I
    H --> I
    I --> E[Candidate evidence and stage telemetry]
    E -. Phase 09 .-> A[Answer generation and output validation]
    A -. Phase 10 .-> F[Isolated private-file context]
    F -. Phase 11 .-> U[Authenticated student API and website]
```

No extra orchestration framework, queue or graph service is needed. The control
flow is ordinary async Python in `Orchestrator.run`. API composition is later work;
the existing FastAPI app exposes health probes only.

## Where to make a change

| Responsibility | File / module |
| --- | --- |
| Request stage order, dispatch and total stage deadlines | [orchestrator.py](../../backend/bintanong_orchestration/orchestrator.py) |
| Release provider and typed dependency interfaces | [ports.py](../../backend/bintanong_orchestration/ports.py) |
| Candidate snapshot, evidence and telemetry schemas | [contracts.py](../../backend/bintanong_orchestration/contracts.py) |
| Release consistency and permitted conclusion scope | [integration.py](../../backend/bintanong_orchestration/integration.py) |
| Existing retrieval/Prolog translation and worker admission | [adapters.py](../../backend/bintanong_orchestration/adapters.py) |
| Semantic routing, aliases, claims and language metadata | [Routing module](../../backend/bintanong_routing/README.md) |
| SEA-LION query embedding, source selection and context assembly | [Retrieval module](../../backend/bintanong_retrieval/README.md) |
| Reviewed facts, generated rules, fixed goals and deterministic reasoning | [Symbolic module](../../backend/bintanong_symbolic/README.md) |

Keep policy data in the reviewed authoring ledger and generated bundle. Do not add
course-specific prerequisite rules to the orchestrator, keyword routing, a second
student fact database or a vector lookup for every exact curriculum question.

## Route and result contract

RAG returns documentary passages with source byte hash, version, page and locator.
Symbolic returns a scoped `SymbolicResult`, or `DependencyResult` for
`list_affected_courses`; the latter is a potential dependency listing, not an
eligibility verdict. Hybrid requires both documentary and symbolic components.
An exact source locator can support a symbolic explanation without vector search.

Every completed route returns `CandidateEvidence` inside `IntegrationResult`.
`permitted_scope` names the synthetic check/explanation that completed. All results
carry `candidate_only=true`, `institutional_use_allowed=false` and
`activation_allowed=false`. These contracts intentionally remain separate from
the institutional `EvidenceBundle`/`AnswerEnvelope`, which reject offline research
results. A ready synthetic fixture establishes no real student entitlement.

| Outcome | Meaning / allowed behavior |
| --- | --- |
| `ready` | Required synthetic branches completed with matching membership/version and no reported gaps; use only the named scope |
| `unknown` | Missing facts, rule coverage or incomplete dependency listing; no definitive eligibility |
| `clarify` | Required target/scope or model interpretation unresolved |
| `greeting`, `unsupported_scope`, `evidence_unavailable` | Router control; no evidence executor runs |
| `no_evidence`, `uncalibrated` | Retrieved context does not establish answer readiness |
| `conflict` | Reported source or symbolic contradiction; conclusions withheld |
| `release_mismatch` | Stale release, wrong bundle or evidence outside pinned membership |
| `unsupported`, `error` | Preserved symbolic operation/operational result; no policy conclusion |
| `held`, `timeout`, `busy`, `invalid_output`, `tool_error` | Execution cannot complete; no substitute route or parametric institutional answer |

Operational failures return no partial evidence package. When both components
return typed observations but one is not ready, the package preserves them with
`permitted_scope=none`. Downstream code must never treat a retained successful
component as permission to answer the failed combined request. Detected conflicts
are supplied by upstream policy/runtime checks; this code does not semantically
compare arbitrary document prose with Prolog rules.
When typed branches disagree on failure status, the precedence is release mismatch,
conflict, error, unsupported, unknown, clarification, no evidence, then uncalibrated.
Both component observations remain available; a lower-priority hold cannot conceal
a symbolic conflict or operational failure. Router timeout/transport/invalid-output
diagnostics retain their operational classification rather than becoming controls.

## Follow-ups, ownership and private context

The caller must authenticate session ownership before constructing `RequestContext`.
The pipeline validates consistency; it does not authenticate users or expire sessions.
For a follow-up, pass only the owning session's explicit program/curriculum and
scoped facts. Missing grades remain unknown. New asserted claims may enter this
request's Prolog arguments; hypothetical/reported claims cannot. There is no hidden
history, automatic fact persistence, implicit course-target reuse or transcript
completeness inference. A target like "that one" needs clarification when unresolved.

A future conversation manager must separately establish confirmation, correction,
expiry and ownership before persisting/reusing facts. Clearing or changing curriculum
requires clearing incompatible facts. Private file extraction is later work and must
remain session-local; it cannot become a source catalog entry or institutional rule.

## Resource and telemetry behavior

Each stage has a finite `stage_timeout` (default120s, configurable up to300s).
Retrieval's stage covers embedding plus storage; it does not report separate embedding
and SQL durations. Preserve existing storage transport timeouts and Prolog's own
bounded subprocess/admission limits. Generation deadlines belong to Phase09.
The adapters admit one worker each and return `busy` under overlap. Hybrid branches
start concurrently only after independent inputs are ready; cancellation propagates
to async branches. Cancelling an async wait cannot kill its running thread: adapter
admission remains held until that worker finishes. Avoid retrying by creating fresh
adapters; share the bounded instances in the release resources.

`StageEvent` contains only stage, duration, route, release ID, outcome, retry count
and evidence IDs. Raw text, prompts, facts, grades, session IDs and exception bodies
are absent. The returned evidence is request-private; never log the entire result.
There is no automatic telemetry exporter or external logging in this module.

## Verify and extend

From the repository root in the prepared Python3.13 environment:

```powershell
$env:TEMP='C:/Coding-projects/bintanong_workspace/audit-evidence/p08-local-tests'
$env:TMP=$env:TEMP
New-Item -ItemType Directory -Force $env:TEMP | Out-Null
python -B -m pytest -q -p no:cacheprovider --basetemp=$env:TEMP/run tests/test_orchestration_integration.py tests/test_orchestration_adapters.py tests/test_orchestration_pipeline.py tests/test_orchestration_sessions.py tests/test_orchestration_smoke.py
```

The [smoke fixture](../../tests/test_orchestration_smoke.py) is the complete synthetic
composition recipe: actual Router, RetrievalEngine and Janus; scripted model output,
manual embedding vector and synthetic database responses. It measures integration
mechanics, not multilingual accuracy or institutional source quality. No model/DB
service is required; the prepared environment needs the existing Janus/SWI runtime.

Before institutional composition, implement an authorized release loader with actual
membership, source authority, scope, recency, rule review and compatible embedding
identity checks. Reconcile the [hosted migration gap](../../plans/2026-10-19-hosted-migration-status.md).
Then honor the applicable phase/release gates. Do not flip a synthetic flag to bypass
them. Phase09 must consume verified evidence, preserve unknowns and validate claims,
citations and response language. Phase07's two Taglish style errors remain; passing
metadata through is not proof of answer-language quality. The standing
[prompt decision](../../plans/2026-10-19-prompt-engineering-and-validation-decision.md)
still applies: inference guidance/guards, no parameter training and a one-week cap.
