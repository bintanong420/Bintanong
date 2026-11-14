---
artifact: phase-plan
phase: 8
status: complete
master: plans/master_implementation_plan_original_long.md
previous_handoff: plans/phase-07-handoff.md
---

# Phase 08 orchestration implementation plan

**Goal:** join the existing LLM router, documentary retrieval and typed Prolog
runtime through an inspectable, request-local candidate evidence pipeline.
**Spec:** master sections 3, 11, 12 and 13; Phase 07 final handoff;
`2026-10-19-prompt-engineering-and-validation-decision.md`; owner resume request
19 October 2026 explicitly starts Phase 08 in p08 and requests organized pipelines.
**Execution:** implement inline using executing-plans and TDD; use the existing
isolated `feat/p08-orchestration` worktree. No new dependencies or infrastructure.

## Constraints and design

- The LLM selects semantics. Host code validates and executes the selected route;
  it never changes a failed Symbolic/Hybrid request into RAG.
- Default release provider denies execution. This increment supports explicit
  synthetic release snapshots only. No institutional loader/activation is inferred.
- Existing retrieval debug reports and synthetic/dependency Prolog results cannot
  be relabeled as institutional `EvidenceBundle`/`AnswerEnvelope`. Use a versioned
  candidate integration envelope with explicit inactive/noninstitutional flags.
- Pin document membership and rule-bundle identity once before routing; check both
  branches against that snapshot. A stale or mixed branch withholds conclusions.
- Keep student assertions separate from institutional evidence. Caller authenticates
  ownership; request context is ephemeral. No transcript store, private-file parsing,
  policy acquisition, grade-threshold inference or globally asserted student facts.
- Follow-up turns reuse only explicitly supplied owned, scoped facts. Never infer
  an omitted target from the previous answer; ambiguity must clarify. Do not mutate
  caller context or automatically persist new model-extracted assertions.
- English/Filipino/Taglish metadata passes through unchanged; Phase 07's two known
  style errors remain disclosed. Generation/output validation belongs to Phase 09;
  authenticated student HTTP transport belongs to Phase 10.
- Prompt engineering means inference guidance, no weight training/fine-tuning;
  preserve the one-week improvement cap and all source/scope/privacy/release holds.

## File responsibilities and interfaces

Create `backend/bintanong_orchestration/` with `contracts.py` (candidate snapshots,
document evidence, integration envelope), `ports.py` (typed dependency protocols,
default hold and synthetic resources), `adapters.py` (existing retrieval/Prolog
translation), `integration.py` (release checks and permitted scope),
`orchestrator.py` (bounded request flow/telemetry), `README.md` (developer pipeline
map and recipes), and `__init__.py`. Update root README navigation only.

Public entry: `await Orchestrator(transport, releases=provider).run(text, context)`
returns `IntegrationResult`. `context` is existing `RequestContext`.
Provider `await pin()` returns one `ReleaseResources` with immutable `ReleasePin`,
reviewed catalog, capability registry and async retrieval/symbolic adapters.
Adapters receive the pinned release and resolved request context, never global
student state. No network/model/source calls in unit fixtures.

## Tasks and verification

Each implementation task writes a focused regression, observes RED, implements the
smallest behavior, verifies GREEN/relevant regressions, records evidence and commits.
Use existing Python 3.13 readiness environment, `-B -m pytest -q -p no:cacheprovider`,
TEMP/TMP and `--basetemp` under workspace/audit-evidence/p08-orchestration-20261019.

1. [x] Candidate contracts and release integration policy.
   Tests: three routes, empty evidence, unknown/unsupported/error distinctions,
   membership/version mismatch, conflicts, dependency-list scope, synthetic-only
   boundary and serialization. No inference from empty lists.
2. [x] Typed adapters over existing retrieval and curriculum runtime.
   Tests: preserve uncalibrated/source gaps; no vector call on Symbolic; dispatch
   all three fixed operations; request-local asserted facts; reject research results;
   bounded admission across thread cancellation. Real synthetic Janus smoke test.
3. [x] Request orchestrator with bounded stages and safe telemetry.
   Tests: default hold; each route through real Router with scripted transport;
   Hybrid waits for both; no reroute; stage timeout/invalid output; cancellation;
   only allowlisted metadata in telemetry; concurrent session isolation.
4. [x] Follow-up/session regressions and developer pipeline documentation.
   Tests: explicitly scoped context reuse, absent/foreign context, asserted versus
   hypothetical claims, curriculum changes, no target invention or persistence.
   Document preparation versus request pipeline, files, failure matrix, testing,
   extension seams and remaining integration/release prerequisites.
5. [x] Verify scoped full regression gate, review the whole change, record exact
   results/limitations and a resumable checkpoint. Phase completion requires exit
   mapping and final handoff; keep Phase 08 active if any required exit is unverified.

## Review focus

Release rollover between branches; a failed Hybrid component alongside a valid
decision; hypothetical facts entering Prolog; cross-session/curriculum follow-ups;
thread work continuing after async cancellation. Pin tests to these behaviors.

## Exit gate

All three synthetic route fixtures produce the same typed candidate envelope;
unknown facts remain unknown, conflicts abstain, failures keep distinct outcomes,
and concurrent sessions cannot share facts. Real synthetic adapter smoke and
existing routing/retrieval/symbolic/contract regression tests pass. Developer guide
links actual files and distinguishes delivered behavior from planned features.
These are offline software exits, not source accuracy, real-model end-to-end
quality, institutional runtime authorization or deployment approval.
