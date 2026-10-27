---
artifact: phase-plan
phase: 11
status: in_progress
master: plans/master_implementation_plan_original_long.md
previous_handoff: plans/phase-10-handoff.md
---

# Phase 11 backend API implementation plan (backend only)

**Goal:** expose the Phase 08-10 pipeline over HTTP: cookie session, `POST /chat` with session conversation
context and clarification replies, uploads with a confirm step, deletion, citations, and a tested AI SDK UI
message stream. Also 24.1 (photo/scan grade rows) and 24.2 (Taglish follow-up style).
**Spec:** master 16.1/16.3, addenda 23.3 and 24; [pre-phase research](2026-10-23-phase-11-pre-phase-research.md);
owner decisions O1-O5 (`owner-decisions-ledger.md`, 23 Oct); Phase 10 final handoff.
**Worktree:** `p11` / `feat/p11-backend-api` from `dev` `cbaa6a7`.
**Scope boundary (owner, 23 Oct):** backend only. No UI pages or components; the frontend waits for the co-worker's
design. If the UI stays delayed, the owner may close Phase 11 backend-only and start Phase 12 non-UI evaluation;
ask at that point. Master 16's browser exit gate is not claimed by this plan.
**Owner update, 25 October 2026:** the frontend is ready for integration. Finish pending work first;
integration remains deferred until then. The earlier design-wait status is superseded.
**Owner update, 26 October 2026:** execute the [two-developer workflow](2026-10-26-phase11-two-developer-workflow.md):
finish bounded Handbook/Charter verification,commit a fixed source/package baseline,
then primary frontend/runtime versus separate local-only ingestion tooling/review UI.
Source words/datasets stay unchanged;merge of tooling does not publish candidates.
This authorizes integration of the existing frontend after the baseline,without new phase advancement.
**Execution:** inline TDD per task (RED observed -> GREEN -> REFACTOR), small commits without attribution,
synthetic fixtures in tracked tests, owner samples only in workspace `audit-evidence/p11-20261023/` (private).

**Owner update,27October2026:** [English/Taglish replies](2026-10-27-english-taglish-response-decision.md)
replace the exclusive-Filipino output target to reduce burden and improve response
time. Filipino input remains supported. Apply the approved migration across prompts,
host rendering and current reply-style expectations with TDD;retain old raw runs.
Software migration delivered28edea4;[results](2026-10-27-english-taglish-migration-results.md)
record revised wire/expectations and bounded observations. Full suite6974passed;
not a complete language-accuracy or latency claim. No accepted input rewording needed.

## Owner decisions (23 Oct 2026)

- O1: AI SDK v7 (current major). Master section 2 "Current pins" and 16.3 updated. The npm install waits for the
  frontend; the backend targets UI message stream protocol v1 (same in v6 and v7).
- O2: RapidOCR 3.9.2 + onnxruntime 1.30.0 CPU (+ opencv) may join the `api` extra. Owner samples: a Report of
  Grades screenshot and a phone photo of a printed prospectus with handwritten grades (layouts may differ).
- O3: `GET /curricula` (read-only program/curriculum names for a picker) may be added.
- O4: students never see variable/function names: diagnostics and raw ids leave the student text.
- O5: symmetric style floor `filipino` -> `taglish` on literal English conversation words, within scope.

## Interfaces

- `create_app(services)` app factory; `services` holds `SessionStore`, a chat pipeline port
  (`run(text, context, routed_sink, progress) -> CandidateAnswer`), curriculum catalog, source lookup and upload
  extractor. Tests inject fakes; a tracked real-data composition builds the live one from env paths (data ignored).
- Cookie `__Host-bintanong_session`: HttpOnly, Secure, SameSite=Strict, Path=/. Unsafe methods require an allowed
  `Origin` (configured; never `null`), reject `Sec-Fetch-Site: cross-site`, and need the expected content type.
- `POST /chat`: AI SDK request body (`id`, `messages`, `trigger`, `messageId`) plus optional `programId`,
  `curriculumId`. Only the **last user message text** is used; earlier messages are ignored (no transcripts,
  master 23.2). Response: SSE with header `x-vercel-ai-ui-message-stream: v1`; parts `start`, transient
  `data-status` progress, one validated `text-start/delta/end`, `source-document` per citation, typed `error`,
  `finish`, `[DONE]`. One in-flight chat per session (409 `chat_in_progress`); disconnect cancels and skips
  capture; a repeated completed `messageId` returns `already_answered`.
- `POST /uploads?curriculumId=` raw body -> pending rows; `POST /uploads/{id}/confirm`; `DELETE /uploads/{id}`;
  `DELETE /session`; `GET /sources/{source_id}` (pinned release only); `GET /curricula`.

## Tasks (dependency order)

1. [ ] App factory, settings, session cookie dependency, CSRF guard, `DELETE /session`. Tests: issue on first call,
   expiry, deletion, session B cannot use A, missing/foreign origin, cross-site fetch metadata.
2. [ ] `POST /chat` core on a fake pipeline: context from the session (`follow_up_context`), `routed_sink` ->
   `capture` -> `set_conversation` only after a validated turn, clarification reply completes through the stored
   context, scope validated against the catalog, typed errors, in-flight lock, duplicate `messageId`.
   `GET /curricula`.
3. [ ] Student render profile (O4): student text without check-scope lines, predicate names, release hashes or
   `ev-` ids; those go to a researcher diagnostics field off by default. Validated content unchanged (tests on the
   existing render fixtures).
4. [ ] UI message stream v1 encoder (golden byte tests), progress callback in the pipeline, streaming response;
   cancellation, disconnect and retry tests.
5. [ ] Uploads endpoints over `read_capped` -> `validate_upload` -> `extract_isolated` -> pending; confirm and
   delete; isolation and expiry tests; printed labels only, no grades in errors.
6. [ ] `GET /sources/{source_id}`: title, page/section, excerpt from the pinned release; unknown or other-release
   ids -> 404.
7. [ ] 24.2: RED tests for Taglish messages labelled `filipino`; symmetric floor; counted roster rerun (63 cases vs
   run 15) and multi-turn rerun (12 cases): no single-turn status/decision lost, 0 wrong carry-over.
8. [ ] 24.1 photo rows: deskew from word-box baselines; header-aware columns (COURSE CODE, FINAL, REMARKS) for the
   Report of Grades layout; refuse when rows, columns or marks are uncertain; strict grade-row scorer (no missing
   or invented row, exact marks, zero silent errors) on simulated photos of synthetic pages; then O2 deps and the
   worker; owner samples measured privately (counts only in Git). Handwriting is refused unless it meets the gate.
9. [ ] Tracked real-data composition and live HTTP smoke (single uvicorn worker, Gemma :18088, hosted release):
   one RAG, one Prolog, one Hybrid question, a follow-up, an upload and deletion.
10. [ ] Exit: full suite, whole-change review, docs (`docs/development/pipelines.md`), handoff.

Tasks 1-6 are independent of 7-8.

## Verification

- Focused: `PYTHONUTF8=1 <venv python> -X utf8 -B -m pytest -q -p no:cacheprovider tests/<file> --basetemp=<ws>`.
- Full suite before exit (about 20 min; background). No linter is installed; disclosed.
- Live runs: roster/multi-turn harnesses in workspace evidence; results reported as counts, raw output ignored.

## Exit gate (backend-only)

- Every endpoint has API tests, including isolation, expiry, deletion, CSRF, duplicate and disconnect cases.
- The stream encoder matches protocol v1 golden output; contract test against the SDK parser is deferred to the
  frontend install (disclosed).
- Live HTTP smoke covers RAG, Prolog, Hybrid, a follow-up, an upload and deletion.
- 24.2: counted Taglish improvement with no single-turn status/decision lost; multi-turn 0 wrong carry-over.
- 24.1: photos supported under the scorer gates, or disclosed as unsupported (per layout).
- No persistent grades, transcripts or private files; no logs with raw text or grades.
- Full suite passes.
