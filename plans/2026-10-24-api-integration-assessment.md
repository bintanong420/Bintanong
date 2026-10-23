# Student API integration assessment

24 October 2026. Repository inspection on `frontend`, starting at `13ae9d2`.
This answers the owner's integration question; it does not start Phase 11.
Read INDEX/current progress, Phase 10 final handoff and master 16/23/24.
Retain the undergraduate/advisory/source-gap/privacy/release boundaries recorded
in the student-facing delivery; no new source or scope decision is made here.

## What exists

| Boundary | Verified code | Remaining work |
| --- | --- | --- |
| HTTP | `backend/bintanong_api/main.py` exposes health/live and health/ready | Student endpoints and application lifetime/dependencies |
| Pipeline | `Orchestrator`, `Generator`, `AnswerPipeline` | Assemble the selected, authorized research release in the HTTP service |
| Runtime resources | `bintanong_runtime/research.py` builds single/multi-curriculum resources with optional hosted storage | Configure reviewed ledgers/package, encoder, hosted release, model URL and budgets; fail closed on mismatches |
| Sessions | `SessionStore` provides memory-only credentials, 30-minute idle expiry, pending extraction, facts and conversation | Cookie issuance/ownership, HTTP expiry/deletion, per-session request ordering |
| Files | capped raw-body read, byte validation, isolated PDF row extraction, explicit row confirmation | HTTP upload/reference/confirmation/removal lifecycle and safe presentation |
| Frontend | `Workspace` calls synthetic adapters; `/api/health` proxies readiness | Typed student transport, server acknowledgments and real answer/source mapping |

`bintanong_runtime/application.py:build_application` is explicitly synthetic;
it must not be relabeled as a production institutional bootstrap. Reuse the
research resource builders for an authorized research preview. Do not promote
sources or disable `CandidateAnswer` candidate/institutional-use guards.

## Smallest coherent implementation sequence

1. **Define and test the HTTP contract.** Request identity, text/clarification,
   session state, progress, final answer, citation references and typed errors.
   Project the current `CandidateAnswer` v2 into student fields; do not expose
   internal diagnostics, rule identifiers or raw model proposals. Preserve its
   validated status, missing information, conditional facts and research limits.
   The older `AnswerEnvelope` is not the delivered student HTTP contract.
2. **Wire text chat and session clearing.** Build the pipeline at service startup,
   own/close resources, issue the opaque credential in an HttpOnly cookie with
   Secure/SameSite and origin protections appropriate to deployment. Assemble
   `RequestContext` from the owned session, never a client-supplied session ID.
   Connect `routed_sink` -> `capture` -> `set_conversation` through the pipeline
   composition. Existing `AnswerPipeline.run` and `RuntimeApplication.run` do not
   forward that optional sink. Preserve clarification and fresh per-turn evidence.
   Acknowledge `DELETE /session`; reject obsolete completions after deletion.
3. **Add uploads and confirmed details.** Raw stream -> `read_capped` ->
   `validate_upload` -> `extract_isolated` -> pending review -> `confirm_pending`.
   Current bounds: 15 MiB, 20 PDF pages, 30-second parser job. Require curriculum
   scope before course matching. Numeric marks never establish passed/failed.
   Define the confirmation endpoint, which master 16's proposed table omits.
   Add owned file references and fact provenance before exposing independent
   file removal: the current store has one pending extraction and merged facts,
   with no multi-file inventory or file-to-fact deletion index. The UI's arbitrary
   typed notes cannot simply become `ScopedFact`; validate supported facts or
   handle the text as a clarification without asserting unsupported knowledge.
4. **Return safe sources and connect the UI.** Resolve citation locators to
   authorized release metadata/excerpts for `GET /sources/{source_id}`; never
   serve arbitrary paths or confuse private uploads with institutional sources.
   Replace the demo adapter with one tested transport, keeping the demo separate.
   Master 16.3 intends Vercel AI SDK; it is not installed. Resolve its compatible
   stable version and protocol during Phase 11 research before adding it.
   Existing orchestration events accumulate in a completed result, so live
   progress requires a deliberate event hook. Publish safe progress and the
   final validated answer, never unvalidated answer tokens.
5. **Verify through the browser and actual services.** RAG/Symbolic/Hybrid,
   clarification, unavailable/conflicting evidence, per-language results,
   upload rejection/confirmation/deletion and source ownership. Exercise duplicate
   requests, disconnect/retry, cancellation, concurrent turns, session expiry,
   reset during work and cross-session access. Deduplicate and serialize on the
   server where needed; a disabled UI button is insufficient. Keep logs free of
   private text/grades and retain candidate-only release behavior.

Start with real **text chat + clarification + session clear + citations**, then
the PDF confirmation flow. These are implementation slices, not a reduced formal
Phase 11 exit gate. Photos/scans remain unsupported unless the separate master
24.1 row-assignment gates pass. Carry Taglish follow-up style into master 24.2.

## Operational constraints and next action

- Compose already connects web/api/model/embedding and defines `API_INTERNAL_URL`,
  but does not configure a complete research runtime or student routes. Resolve
  authorized artifacts and actual model/hosted settings without copying secrets
  or weights into Git. Verify container imports and readiness of the actual
  chat resources; generic health success alone does not prove a chat can run.
- `SessionStore` is process-local. Start with a deliberate single API worker;
  multiple workers/replicas require an explicit compatible memory/session design.
  Restart loses sessions. Do not silently introduce persistent student storage.
- This turn inspected code; it did not start Docker, query Supabase, exercise
  the real model or reverify historical backend acceptance/latency results.
- Follow the repository's Phase 11 pre-phase research and owner summary/go before
  beginning backend integration. No backend, dependencies, deployment or phase
  status changed in this assessment.
