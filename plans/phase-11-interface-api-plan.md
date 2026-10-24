---
artifact: interface-preparation
phase: 11
status: ready
preparation_only: true
master: plans/master_implementation_plan_original_long.md
previous_handoff: plans/phase-10-handoff.md
superseded_by: plans/2026-10-24-student-ui-backend-integration-plan.md
---

# Phase 11 interface and API implementation plan

Historical preparation retained from the original frontend branch. The owner
selected Lawrence's backend plan and approved bringing it into this frontend;
the linked integration tasks now govern execution. This is not a second active
numbered phase plan. Original preparation content is retained below.

**Goal:** connect the student workspace to the existing research pipeline while
preserving validation, privacy, language style and source/version boundaries.
**Architecture:** FastAPI owns research resources, sessions, admission, uploads
and validated responses. Next.js exposes a fixed same-origin transport and renders
student DTOs; it cannot select routes/rules or activate sources.
**Stack:** existing Python3.13/FastAPI, Next16/React19/TypeScript7/shadcn/Tailwind;
proposed SDK6 additions require the dependency decision in the research record.

[Pre-phase research](2026-10-24-phase-11-pre-phase-research.md) |
[Integration assessment](2026-10-24-api-integration-assessment.md) |
[Preparation/recovery](2026-10-24-phase-11-preparation.md).
Execution uses `superpowers:executing-plans` natively, task by task, RED/GREEN and
small Conventional Commits. A plan review/dependency decision precedes substantial
implementation. Prepared in the writable main checkout because the newly created
`p11` worktree became read-only mid-session. Copy accepted preparation documents
into `p11` through normal Git history once write access is restored; do not bypass
the sandbox or implement the phase on `frontend` as a workaround.

## Scope and invariants

- Master16 student routes, clarification, sources, progress, files, confirmation,
  acknowledged deletion and expiry. Master23 session context; master24 carry-overs.
- Authorized real public sources/reviewed Prolog may run in the research build;
  candidate/institutional-use guards remain. No public deployment or activation.
- Undergraduate read-only advice only. Unknown is distinct from unmet. Request
  only missing facts that materially affect the answer; never demand an upload.
- Student text/files never enter institutional ingestion/search or persistent
  history. Logs/errors/telemetry cannot include raw questions, grades or tokens.
- Ownership comes from opaque cookie credentials, not browser IDs. Server-only
  release configuration; no route, arbitrary predicate or source-path overrides.
- Only validated final prose is shown. Safe progress is not academic reasoning.
- Administrative work is a separate design proposal, not a required Phase11 exit.
  No reviewer identity provider, approval workflow or source activation is added.
- Preserve 30-minute idle memory sessions and existing parser/size/fact caps.
  Photos/scans unsupported until master24.1 gates pass; no UI claim of OCR support.

## Interfaces and files

| Module | Responsibility |
| --- | --- |
| `backend/bintanong_api/student_contracts.py` | Strict bounded requests; student answer/source/file/context/error projections |
| `backend/bintanong_api/student_service.py` | Owned session operations, request serialization/replay, expiry/deletion generations |
| `backend/bintanong_api/student_routes.py` | Cookie/origin checks, capped body handling, status mapping, response streaming |
| `backend/bintanong_api/runtime.py` | Explicit research configuration, lifespan creation/cleanup and readiness |
| Existing orchestration/generation/private-context modules | Narrow sink/event propagation and file/fact provenance extensions |
| `frontend/app/api/{chat,session,uploads,sources}/...` | Fixed upstream forwarding; no cache of personal responses |
| `frontend/lib/student-contracts.ts`, `student-transport.ts` | Runtime-validated DTO mapping, SDK transport and typed errors |
| Existing workspace/controller/components | Keep assistant wording separate from context controls; real pending/error/review flows |
| `tests/test_student_api_*.py`, frontend tests | Ownership, transport, race, resource and browser acceptance coverage |

Proposed HTTP surface: `POST /session`, `POST /chat`, `POST /uploads`,
`POST /uploads/{id}/confirm`, `DELETE /uploads/{id}`, `DELETE /session`,
`GET /sources/{source_id}`, health/live and health/ready. Confirm exact schemas in
Task1. `POST /session` issues credentials; it must not silently replace an expired
session during a mutating request. A session projection supplies active files,
pending review and confirmed supported facts. Private source IDs cannot resolve
through the institutional source endpoint.

Chat accepts a bounded current question and request key; the server builds
`RequestContext` and pins the release. It rejects a reused key with different
input. Progress has safe display codes; final is projected from CandidateAnswerv2.
Clarification includes host-validated missing fields/context action information
with the assistant's response text. Generic notes are not trusted course facts.
Cancellation/disconnect never emits a late answer into another session generation.
Decide bounded replay behavior explicitly before exposing retries.

## Tasks and verification

Every unchecked task follows: write the named failure cases, observe RED, implement
the minimum, run GREEN plus affected regressions, review and commit explicitly.

### 1. HTTP contracts and ownership/admission

- [ ] Define DTOs and fixed error/status codes; project CandidateAnswerv2, not the
  older AnswerEnvelope. Exclude diagnostics, raw file contents and internal refs.
- [ ] RED tests: whitespace/oversize/malformed input, unknown/foreign session,
  forged IDs, cross-origin mutation, session saturation, reused request key with
  changed body, duplicate pending request and expiry during admission.
- [ ] Implement HttpOnly/SameSite cookie, Secure in HTTPS deployment, fixed origin
  checks and bounded admission/replay; no unbounded cache or logging private text.

### 2. Research runtime and text chat

- [ ] Reuse `build_multi_research_resources`/hosted storage, `Orchestrator`,
  `Generator` and `AnswerPipeline`; load verified configured artifacts once.
- [ ] RED tests: missing/mismatched held inputs, all three paths, clarification,
  unsupported/unknown/conflict/timeout states, no client-selected route/release.
- [ ] Propagate `routed_sink` through composition, capture owned context, preserve
  fresh evidence and ambiguity fallback. Add health readiness for actual resources.
- [ ] Verify container namespace imports/startup/cleanup; repair the runtime README
  to distinguish synthetic bootstrap from authorized research resources.

### 3. Clear/expiry, progress and client transport

- [ ] RED tests: clear while pending, stale session write, retry after disconnect,
  concurrent turns, abort before/after completion, restart and idle expiry.
- [ ] Serialize owned mutations and invalidate generations on clear. Bound work;
  disconnect must stop or safely detach work without retaining private payloads.
- [ ] Add safe stage events at real boundaries and final validation before output.
  Test exact SDK6 stream parsing/types after approved install; reject v7 drift.
- [ ] Implement fixed Next forwarding with cookie/status/error/abort behavior,
  no-store, no secret exposure. Keep demo mode explicitly separate from real mode.

### 4. Sources and conversation rendering

- [ ] RED tests: forged source ID, source from another release, held/missing source,
  unsafe locator/path, private-upload masquerading as institutional citation.
- [ ] Render authorized source title/date/page/section and supported excerpt/link;
  retain source gaps and conditional conclusions. No unvalidated HTML or reasoning.
- [ ] Use backend assistant text to explain missing information before context
  controls; clarify in the conversation, not by silently setting a profile.

### 5. Private files and explicit fact review

- [ ] Extend memory state with owned file references and file-to-fact provenance.
  Define repeat confirmation/removal semantics; never store raw files permanently.
- [ ] RED tests: capped streaming, sniff/type/page/parser failure, duplicate upload,
  foreign reference/row, stale confirmation, grade-to-pass inference rejection,
  file removal invalidating only linked facts and pending extraction replacement.
- [ ] Wire raw-body validation and isolated parser, curriculum-scoped row matching,
  explicit reviewed choices and supported typed facts. Preserve question/other
  files on a rejected selection; do not clear on an unacknowledged server failure.

### 6. Browser acceptance and carry-overs

- [ ] Test text/clarification/citations, supported PDFs, confirmation/edit/removal,
  acknowledged clear, idle expiry, duplicate/retry/disconnect and unavailable API.
- [ ] Verify keyboard/IME, focus/status announcements, light/dark/system, long
  content, short VSCode-sized windows, zoom/reflow and student privacy boundaries.
- [ ] Test-first fix Taglish follow-up host style under master24.2; reuse accepted
  language cases and report actual model observations separately from mocks.
- [ ] Photo/scans: either meet master24.1 row-assignment gates with authorized
  private examples or disclose unsupported status. No false completion claim.
- [ ] Run focused/full relevant regressions, frontend typecheck/build, API browser
  smoke against actual services and documented latency boundaries. No new SLA.

## Optional admin design

[Standalone design](designs/phase-11-reviewer-dashboard.html): source status,
unresolved review items and service readiness, synthetic data only. Separate route
and navigation from students when connected. No student-chat/grade/file browser.
Future live access requires selected reviewer identity/role authority and endpoint
authorization tests. CLI ingestion/activation remain unchanged. Owner asked which
to do first; student APIs first is a recommendation, not recorded acceptance of
an identity provider or a new mandatory phase gate.

## Review focus and exit gate

Review focus: clear/completion races (Task3), request-key replay with altered input
(Task1), cross-session file/source access (Tasks4/5), numeric grade inference and
arbitrary typed-fact escalation (Task5), unchecked prose/diagnostic leakage (Task3).

Exit: browser exercises RAG/Symbolic/Hybrid, missing information, validation failure,
uploads/confirmation/deletion and unavailable services; ownership/expiry/concurrency
tests pass; sources and language limits are visible. Report unsupported photos and
remaining evaluation gaps. Produce final handoff before advancing to Phase12.
Do not count this prepared plan, admin mockup or synthetic UI tests as that exit.
