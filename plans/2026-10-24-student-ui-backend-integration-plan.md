# Student UI integration with the selected Phase 11 backend

> **For agentic workers:** Use `superpowers:executing-plans` inline, with focused RED/GREEN tests and a final independent review.

**Goal:** connect the original student workspace to `feat/p11-backend-api`, preserving its validated research pipeline and temporary private context.
**Architecture:** Next.js renders the original UI and forwards fixed same-origin requests. The selected FastAPI app owns authorization, sessions, queue, files and validated answers. Bring Lawrence's backend into the original frontend base; no interface-branch backend is merged.
**Tech stack:** existing Python 3.13/FastAPI; Next/React/TypeScript, Tailwind/shadcn, SDK7 and Supabase SSR.
**Spec:** master16/23/24/25; phase-11-backend-api-plan.md; 2026-10-24-frontend-backend-contract-check.md; original UI at db4275e.

## Global constraints

- Owner approved implementation and selected origin/feat/p11-backend-api; baseline34a21ca plus documentation commits through39b38dd. Preserve interface branch/worktree and owner files.
- Owner approved exact pins: Next16.4.3, ai7.0.152, @ai-sdk/react4.0.156, @supabase/ssr0.12.7, @supabase/supabase-js2.118.0; sharp0.35.5/source-map-js1.2.2. Keep React19.3.0/TypeScript7.0.2 and Node24.21.0. Reuse prior approved UI foundation pins/assets.
- Undergraduate/read-only/reviewed-source/private-context boundaries remain. No academic inference in the UI, no raw drafts, no personal history persistence, no model download, no deployment or source activation.
- Reuse queue/upload/readable-result behavior. Adapter changes do not create missing pending-intent/replay features. Stop cancels; interrupted responses disclose uncertainty and never silently resubmit a committed request.
- Real Google sign-in requires external OAuth setup: hosted public auth settings currently report Google disabled. Build fail-closed server verification; do not provide an unauthenticated production fallback.
- UI at /; /chat redirects to the same workspace; developer health at /dev/health. Remove simulated answers/files and example selector from the student path; preserve shell/campus/compact composer/system themes.
- Existing API scope picker provides checked program/curriculum for file confirmation and facts. Clarifications expose checked missing fields. Do not invent an unsupported /context endpoint or claim unknown grades are failed.

## Research and reuse

Current npm registry metadata checked24Oct: approved versions published no later than23Oct; compatible Node>=22 and React19 peers. Use installed SDK types/parser for wire verification.
[AI SDK transport](https://ai-sdk.dev/docs/ai-sdk-ui/transport), [Supabase SSR](https://supabase.com/docs/guides/auth/server-side/creating-a-client?queryGroups=framework&framework=nextjs), [Next authentication](https://nextjs.org/docs/app/guides/authentication).
Reuse original tokens/local assets, appearance control, dialog, buttons, textarea, sidebar and source/file review layouts. Figma tools are unavailable in this session; existing inspected design evidence/annotations govern reuse, not a claim of fresh Figma approval.
Context consulted: thesis physical17-18/65-66 and routing PNG; master16/25 and Phase10 handoff. No change to institutional scope/routing.

## Review focus

- Account switching must never expose another account's transient session or allow a second simultaneous question.
- Late stream/file responses after Stop/Clear must not mutate the current conversation.
- Missing/expired auth and failed clearing must preserve visible student work until acknowledgment.
- Only checked institutional source IDs can open source panels; file choices remain private, explicit and current-scope.
- Queue/slow network, IME composition, short windows, themes and long text must remain usable without fabricated success.

## Task 1: Backend authorization and checked answer metadata

Files: API auth/session/app/admission/stream modules, private session store; tests/test_api_auth.py and affected API tests.
Consumes existing create_app/ApiServices/ApiSettings and session/queue APIs. Produces optional injected verifier for legacy tests; tracked research composition requires it. Verify Google identity, confirmed PSU email and opaque account identity with Supabase /auth/v1/user on every protected request; bind owned sessions and per-account answer admission. Expose language/missing fields in answer summary without changing canonical CandidateAnswer.
- [ ] RED: missing/forged/non-PSU/unverified/non-Google identity, auth outage, cross-account cookie/delete, two tabs/account, cancellation releases admission; metadata preserves known fields.
- [x] Implement narrow shared guards; GREEN affected API/private-context tests; commit.

## Task 2: Original UI foundation and tested SDK7 transport

Files: frontend package/lock/config/layout/globals, reusable components/assets fromdb4275e; lib/student-contracts.ts, student-transport.ts, student-proxy.ts; fixed API handlers and frontend tests.
Consumes backend ChatRequest/SSE/upload/source/curricula contracts. Produces bounded validated adapter using installed DefaultChatTransport, fixed upstream URLs, correct secure cookie/auth forwarding and typed failures.
- [ ] RED: actual backend stream through SDK parser; malformed/duplicate/missing finish, foreign IDs, origin/body limits, correct cookies, upload/query/confirmation mapping and abort.
- [x] Install approved pins, reuse UI files explicitly, implement adapters; GREEN frontend tests/typecheck; commit.

## Task 3: Connected workspace and PSU sign-in

Files: workspace controller/conversation/composer/source/file/scope panels, root and /chat routes, auth helpers/login/callback/signout.
Consumes Task2 adapter and Task1 checked metadata. Produces one actual conversation using original visuals, explicit curriculum picker, local file-review state with acknowledged confirmation/removal, conditional result notices, working source inspection, Stop and acknowledged New chat. OAuth PKCE callback accepts only internal destinations; server authorization remains authoritative.
- [ ] RED: user message retained; duplicate prevention; Stop/Clear races; failed deletion; clarification fields; unsupported/reselected file preserves others; keyboard/IME; no simulation calls.
- [ ] Implement; GREEN UI tests/typecheck/build; commit.

## Task 4: Reproducible selected-backend research composition

Files: tracked runtime composition/launcher and local development docs, external config/credentials stay ignored.
Consumes validated hosted ledgers/document snapshot and existing derivative review index; builds ResearchPipeline/create_app, isolated PDF extractor and required PSU verifier. Fail startup on missing/mismatched config; readiness includes configured student composition. Never use health-only main.app as the student app.
- [ ] RED: absent config, invalid source/index/release, missing auth, cleanup on failure; actual composition self-check.
- [ ] Implement and verify without DB writes, weight downloads or bypassing review; commit.

## Task 5: Browser verification and delivery

- [ ] Run affected Python tests, SDK parser/transport/UI tests, TypeScript and production build on declared environments.
- [ ] Exercise real Next/FastAPI with deterministic synthetic pipeline/auth in a separate test instance: messages, sources, uploads, waiting/busy, clearing, failures, themes, keyboard/IME/zoom. No production auth bypass.
- [ ] Run bounded actual research-pipeline RAG/Symbolic/Hybrid samples separately; report failures honestly. Real Google login remains unverified until external provider setup and a human PSU login.
- [ ] Independent final review, fix important findings with RED/GREEN, update delivery/progress/checkpoint and commit. Phase11 stays active unless all formal exits actually pass.

## Execution ledger

Plan starts after owner go. Dependency pins approved via UI reply. Google requirement confirmed in master25.1/checkpoint; provider disabled, external setup pending. Prior current-state snapshot39b38dd.
Task1: RED14 auth/ownership/admission failures and RED2 summary failures observed. GREEN131 API/private-session tests using system Python3.13 (`py -3.13 -B -m pytest`, cache disabled, external basetemp integration-api-green-system). Own venv lacks ReportLab; no install or fixture change. Auth is injectable for existing offline callers; tracked real composition will require it. Account limit covers queued and running work, preventing one account occupying multiple queue slots.
Task2: RED missing transport/proxy/reducer modules observed; GREEN14 Node24.21 tests, including actual Python emitter -> installed SDK7 parser, and TypeScript after `next typegen` refreshed stale branch-generated route types. Reused31 explicit visual files/assets fromdb4275e. Approved exact pins installed; no React/TypeScript pin change. Small workspace reducer/composer types shipped with the foundation because reused Composer imports them; no simulated adapter included.

Ruling (owner correction): integration base is frontend c17dcb2, worktree p11-frontend-integration / feat/p11-frontend-integration. Merge Lawrence origin/feat/p11-backend-api34a21ca into it. Preserve original UI and carry only selected earlier integration fixes; older commits/test results remain evidence, not proof of this tree.
