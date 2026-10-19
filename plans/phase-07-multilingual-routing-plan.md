---
artifact: phase-plan
phase: 7
status: in_progress
master: plans/master_implementation_plan_original_long.md
previous_handoff: plans/phase-06-handoff.md
---

# Phase 07 multilingual interpretation and LLM routing

## Goal and authorization

Owner19October2026 requests continuation in p07 after the other developer's
Phase06, and explicitly requests checking Context. Phase-state inspect confirms
the complete Phase06 handoff permits7. Owner now explicitly directs implementation:
“proceed to phase 07 lets go!” Use the [accepted design](2026-10-19-phase07-routing-design.md)
and [implementation plan](2026-10-19-phase07-implementation-plan.md) with inline TDD.
Owner19October2026 confirms prospectus/Prolog and handbook/Charter/memo RAG roles,
matching English/Taglish/Filipino response style and later-phase image attachments;
these settled requirements are incorporated in the design, without treating the
clarification as blanket acceptance of every proposed implementation choice.

Student capability: natural English/Filipino/Taglish queries yield an observable,
validated RAG/Symbolic/Hybrid decision or an explicit clarification/scope/unavailable
control. Evidence path: Bintu interpretation -> scoped reviewed identity resolution
-> shared-contract/capability validation. Exit: actual model route/meaning report
plus deterministic safety regression evidence and a complete final handoff.

## Constraints and review focus

- Bintu performs semantic routing; no replacement classifier or Direct route.
- Reuse shared contracts and Phase06 typed operation signatures. EMPTY_REGISTRY,
  source lifecycle and institutional release/activation guards stay closed.
- Preserve undergraduate/read-only/private boundaries, scoped editions, unresolved
  source gaps and missing-fact unknowns; do not reopen settled source decisions.
- Preserve negation, hypotheticals and time expressions; reject invented facts,
  aliases, equivalencies, unsupported operations and cross-session context.
- Prospectus/curriculum primarily uses structured facts/Prolog; handbook, Citizens'
  Charter and memos primarily use RAG. Hybrid joins both when the question needs it.
- Carry response-style metadata:English -> English, Taglish -> Taglish, Filipino
  -> predominantly Filipino with natural technical terms; no forced translations
  or invented word-ratio quota. Final answer generation remains later work.
- Image attachments/OCR remain later-phase private-context work, outside Phase07.
- Keep proposed route distinct from effective validated control/route; do not
  conceal capability failures by reclassifying a decision request as RAG.
- No dependency installs/pin changes, weight downloads/copies or deployed API.
- Synthetic boundary tests differ from accepted institutional development cases;
  new institutional questions/labels need their applicable review before evaluation.
- Reuse75accepted variants where relevant; preserve sealed final-family separation.

## Tasks

- [x] Verify clean Git baseline, Phase06 accepted handoff and formal advancement.
- [x] Consult required Context evidence, master3/11/12/13 and scope/gap policies.
- [x] Inspect existing contracts/legacy client; draft concrete Phase07 design.
- [x] Complete builder review; clarify fact provenance and compound requests.
- [x] Record owner acceptance of the concrete design and direction to proceed.
- [x] Write/review exact implementation interfaces and RED/GREEN task steps.
- [x] Implement request/interpretation contracts, response-style metadata and minimal normalization.
- [x] Implement scoped exact entity resolution and capability/fact validation.
- [x] Implement versioned Bintu prompt/transport, token budget and bounded repair.
- [x] Review synthetic route labels, resolve model identity/server and run offline evaluation.
- [ ] Review confusion matrices, language/meaning consistency and failures; verify
      exit, complete handoff, supersede checkpoint and validate advancement.

## Interfaces and verification

Design reuses NormalizedQuery/RoutingDecision/PredicateRequest/CapabilityRegistry.
Implemented interfaces and exact task steps are in the accepted implementation
plan and backend/bintanong_routing/README.md. No evidence executors/API were added.
Focused tests use synthetic fixtures, fake transports and existing Python3.13
readiness venv, pytest -B -p no:cacheprovider with workspace-external basetemp.
Actual Bintu runs need model/runtime/template/prompt/schema digests and reviewed
development labels; mocks and Phase05 retrieval scores cannot satisfy that exit.

Verify docs with git diff --check, phase_state.py validate and phase-state tests.
Exit also requires applicable contract/symbolic/transport regressions, explicit
zero unchecked invalid dispatches, actual-model per-language report and honest
disclosure of remaining institutional holds. No numerical routing-accuracy gate
has yet been approved; report observations for review rather than invent one.

## Current dependencies

Owner supplies workspace/MODELS and authorized official runtime image download.
Existing Gemma bytes/image/build/template are verified; no weight copies or package
changes. Independent style/routing candidate ac00ac9 gets15/15guarded outcomes/
meaning and13/15response-style labels. Two Taglish labels remain wrong. Label-first
candidate regresses pure-language cases and is retired. See the
[stage results](2026-10-19-phase07-style-stage-evaluation.md).
The language-style exit remains open; Phase07 is active and Phase08
cannot begin. See the dated evaluation report and exact next checkpoint action.
Phase06 predecessor verification remains accepted; no receipt-recovery task.
