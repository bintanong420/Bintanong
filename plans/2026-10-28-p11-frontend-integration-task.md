# Phase 11 frontend integration — Codex B

## Scope and actual approvals

- Lane `p11-frontend-integration` / `feat/p11-frontend-integration`, baseline `12ac411`.
  Last full pre-condensation task record: `f506abf`. Central snapshots remain Claude-owned.
- Owner confirmed snapshot **e172f53c19bdd5d30ef5df2db4bf80ee47e27c3c**, rather than latest,
  this session (28 October); frontend paths imported, no whole frontend-branch merge.
- Owner: **“Approve the exact snapshot dependencies and npm ci.”** Package/lock Git blobs remain
  exactly the snapshot's. Next16.4.3, React/DOM19.3.0, AI SDK7.0.152/@ai-sdk/react4.0.156,
  SupabaseSSR0.12.7/client2.118.0, Tailwind4.3.3, PostCSS8.5.31, snapshot Radix/UI pins and
  sharp0.35.5/source-map-js1.2.2 overrides; no opportunistic upgrades. Node24.21.0/npm11.19.0.
- Metadata/account seams: Claude review `a1ef6de`, owner reply “Actually, we were thinking of
  removing the login but keep it for now because i think itd be easier if we later decided to
  remove it because we are planning to remove the UAT on our study because it seems redundant
  to the research tools we have.” Coordinator confirms secure binding/metadata authorized.
  **Keep login; UAT removal remains a consideration, not a requirements change.**
- Own frontend/API/API tests/this record. SessionStore is explicitly approved shared exception,
  single implementer Codex B. No other shared production, source/package/pin or hosted writes.
- Baseline: master3/11/13/16/23–26, Phase11plan/Phase10handoff and split workflow. Context thesis
  physical17–18/39–44 and routingPNG consulted: undergraduate advisory/private-data scope;
  illustrative closed-world example never overrides unknown-versus-unmet. No discrepancy.
- Prompt decision19Oct and response-time recommendation/measurement contract read. No training,
  activation/deployment/push/phase advancement. Full suite/live slots coordinated through root.

## Delivered commits and behavior

- `86b839b` task/proposals; `90203e4` separate SessionStore+tests only. Every credential method
  checks verified opaque account equality (including None) before renewing idle expiry; foreign
  sessions look unknown. Trusted wipe and unauthenticated test mode unchanged.
- `e853b77` additive student metadata: language, missing fields and canonical clarification;
  printed labels, no new inference or CandidateAnswer schema changes. Unknown never failed.
- `f506abf` approved frontend snapshot and portable shared-Python SDK fixture runner.
- `b1bc98b` server-verified PSU Google identity, account admission, all API identity threading.
- `5b3b04e` clean merge of primary through835aea7 (docs only).
- `de1e68a` API-owned tracked research factory/config/readiness using existing CPU encoder,
  reviewed resources and pipeline. Explicit pin/seal/current78 package/public runtime key;
  per-request hosted active-release/curriculum-link guards; no shared HTTP-embedding additions.
- `83af0e5` reviewP2: validated Taglish reaches notices, clarification replies and retained
  choices. Static navigation stays supplied. Actual outgoing reply covered by browser regression.
- `e1a132d` reviewP2: eagerly load the CPU encoder once before exposing concurrent readiness/
  retrieval. Concurrent RED constructed three models instead of one; focused GREEN33.
- Student capabilities: chat/progress/sources, canonical clarification, curriculum choice,
  PDF review/confirmation/removal and reset; private context remains temporary and separate.

## Verification evidence

Evidence: workspace `audit-evidence/p11-frontend-integration-20261028`.
Python: shared `p05-real-retrieval-readiness-20261012/venv/Scripts/python.exe`, `PYTHONUTF8=1`,
`-X utf8 -B -m pytest -q -p no:cacheprovider`, lane external `--basetemp`.

- Session RED15→GREEN87 (`session-green.log`). Auth RED14→GREEN93 including authenticated
  upload/confirm/chat/removal/reset and foreign-cookie isolation (`auth-green3.log`).
- Actual installed SDK RED rejected missing language/missingFields after repairing test-runner
  setup; metadata goldens RED4→API GREEN47 (`metadata-green2.log`). SDK parses actual Python
  answered/clarification/insufficient streams; **62 UI tests pass** (`frontend-final.log`),
  `BINTANONG_TEST_PYTHON` points to shared venv. Initial setup errors were not treated as RED.
- Factory absent API RED→GREEN24; real readiness RED2→factory/auth/probes **32 pass**
  (`factory-green2.log`), using this runtime's pin, CPU encoder, Janus and model health.
- `npm run typecheck` and final `npm run build` pass; `npm audit --json`: **0 findings**.
  Existing multiple-lockfile/standalone-start warnings disclosed, no dependency/lock drift.
- Public browser passes320/390/768/1440/both themes, enlarged text, contrast, focus/redirect.
  Taglish browser RED actualEnglishnotice→**4 browser tests pass**, language/clarification/chat
  lifecycle/welcome (`language-browser-green.log`), no page errors. Synthetic local auth/API only.
- Initial inline-env synthetic testserver launch was tool-policy rejected (“blocked by policy”,
  no reason). Reviewable Python launcher with loopback/cwd/synthetic-key assertions accepted;
  no production bypass. No real identity/hosted config/model involved in browser fixtures.
- Actual config preflight (`actual-package-preflight.json`):78chunks/78vectors/all7sealedfiles,
  zero client/model loads/network calls. PinSHA5dd2d9c95c3cc96181bdd11d3a24481f1c18a4a5c71284a55316c7d60acecc74;
  sealSHA22ceaa15c300a5fc2d8778062a9f19ebb175bee34700f68267ec651a07b34c0a unchanged.
- Actual factory startup completed72.48s after module imports (hosted curricula17.35s; encoder/
  dependent imports complete42.78s; resources72.45s). Includes reviewed hosted reads and CPU load;
  excludes Gemma boot/inference and browser time, not a student latency/SLA measurement.
- Real owned HTTP: liveness200, unauthenticated curricula401 and chat401/sign_in_required,
  zero model calls (`actual-http-boundary.json`). Initial premature refusal receipt was replaced
  only after actual startup/checks. API/CPU stopped before full suite to preserve memory.
- Read-only public auth settings: Google enabled. Authorized ignored frontend `.env.local` maps
  existing public URL/anon key; no service-role copy. Rebuild passes; local `/login`200,
  `POST /auth/login`303 to Google Supabase authorize with loopback callback, not followed
  (`local-login-boundary.json`). No hosted OAuth configuration writes or actual student sign-in.

## Remaining gates and next action

- Actual student sign-in is still required privately at `http://127.0.0.1:3216/login`; Google
  provider enabled and local redirect prepared, but hosted redirect acceptance/actual PSU login
  remains unverified. Authenticated real-source HTTP/browser smoke remains open; no token paste.
- LIVE RUN: none. No Gemma inference launched by lane. Full suite/final scoped review
  remain required. Distinguish model/backend startup, pipeline, outer HTTP and browser E2E;
  synthetic browser durations are test time, never student/model latency or SLA evidence.
- FULL SUITE: reserved Codex B by coordinator; start after clean primary sync below. Real API/CPU
  model stopped. Local login frontend stays available; no model work during the reserved suite.
- Next action: synchronize current primary cleanly, execute the reserved full suite, then record
  final review and exact actual-auth gap before owner/Claude integration review.
