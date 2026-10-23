# Phase 11 pre-phase research

24 October 2026. Preparation for master 16, 23.3 and 24; no phase exit claim.
Owner requested a Phase 11 worktree, clearer assistant context requests and an
admin design based on repository requirements. This is the recommendation record
required by AGENTS.md, before the numbered phase plan.

## Verified baseline and context

- `frontend` at `09568f3`; Phase 10 complete, no active numbered phase.
  `phase_state.py can-advance --repo .` succeeds. Preserve unrelated owner edits.
- Created `C:/Coding-projects/bintanong_workspace/worktrees/Bintanong/p11`, branch
  `feat/p11-api-interface`, from `09568f3`. The frontend dependency directory is a
  junction to the existing identical-lock checkout; nothing was installed.
- Read Phase 10 handoff, integration assessment, master 16/23/24, undergraduate
  policy, prompt/validation decision, latency profile and response-time guidance.
  Thesis physical 17-19, 65-66, 76-79 and routing PNG inspected in this session.
  Preserve English/Filipino/Taglish style, reviewed Prolog reasoning, per-turn
  evidence, private session isolation and accuracy before latency.
- Actual API exposes health only. `AnswerPipeline`, research resource builders,
  model transport, guarded generation, sessions and bounded PDF extraction exist.
  `RuntimeApplication` wraps a synthetic bootstrap; `research.py` separately
  builds authorized real-data research resources. The runtime README's synthetic
  description does not document that latter path; do not remove its guards.
- Session state lacks a multi-file inventory and file-to-fact deletion index.
  The frontend's arbitrary typed notes do not match `ScopedFact` automatically.
  Orchestration events are collected in the result; they are not a live stream.
- Admin discrepancy: master 16.1 explicitly makes a hosted reviewer dashboard
  optional. Existing local correction GUI and CLI ingestion/activation remain.
  Owner asked for a recommendation; recommend student APIs first, admin design
  alongside, then authenticated read-only access as a separately accepted slice.

## Current official technology evidence

Registry metadata read directly on 24 October, before network restrictions changed:

| Package | Existing pin | Observed stable/version line | Recommendation |
| --- | --- | --- | --- |
| `ai` | absent | latest 7.0.152; `ai-v6` 6.0.315 | Propose exact 6.0.315, matching thesis major; no silent major upgrade |
| `@ai-sdk/react` | absent | latest 4.0.156; `ai-v6` 3.0.318 | Propose exact 3.0.318 with the selected SDK6 |
| Next.js | 16.3.5 | latest 16.4.3 | Preserve pin; assess existing advisories in a separate approved update |
| FastAPI | 0.141.1 | PyPI latest 0.162.0 | Reuse pinned supported primitives; avoid a framework upgrade inside wiring |

SDK6 packages above were published 23 October UTC. Registry peer ranges:
`ai` accepts Zod `^3.25.76 || ^4.1.8`; React adapter accepts React
`^18 || ~19.0.1 || ~19.1.2 || ^19.2.1`, including installed React19.3.0.
Resolve and record an exact compatible stable Zod pin before the approved install;
search listings differ on its newest patch. No package or lockfile was changed.
Primary metadata: [ai registry](https://registry.npmjs.org/ai),
[React adapter registry](https://registry.npmjs.org/@ai-sdk%2freact),
[Next registry](https://registry.npmjs.org/next),
[FastAPI PyPI](https://pypi.org/pypi/fastapi/json).

Official docs support a configurable client transport and typed custom data parts.
Use a contract test against the actual installed SDK, since the live docs now show
v7 and the `v6.ai-sdk.dev` address redirects to them. Do not copy v7 examples as
proof of SDK6 compatibility. [Transport](https://ai-sdk.dev/docs/ai-sdk-ui/transport),
[stream protocol](https://ai-sdk.dev/docs/ai-sdk-ui/stream-protocol),
[custom data](https://ai-sdk.dev/docs/ai-sdk-ui/streaming-data).

Use application lifespan to load/close shared resources once; use response cookies
for the opaque credential and a bounded streaming response for safe progress.
These do not require new Python dependencies.
[FastAPI lifespan](https://fastapi.tiangolo.com/advanced/events/),
[cookies](https://fastapi.tiangolo.com/advanced/response-cookies/),
[streaming responses](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse).
Reviewer authorization must protect data access and endpoints, not just a layout
or hidden menu. [Next.js authentication guide](https://nextjs.org/docs/app/guides/authentication).

Context7 is not available among connected tools. The requested Supabase changelog
Markdown endpoint was rejected by the web reader's content-type handling. No
Supabase feature/schema/auth change is proposed now; refresh its relevant official
docs and changelog when that separate connected reviewer slice is authorized.

## Options, expected gains and costs

| Choice | Expected gain | Cost/risk | Recommendation |
| --- | --- | --- | --- |
| Reuse research builders + pipeline vs rebuild services | Preserves tested routing/validation; fewer new code paths | HTTP ownership/cancellation still needs tests | Reuse |
| Lifespan resources vs per-message loading | Avoids repeating encoder/model setup; reduces resident copies | Startup failure must fail readiness | One encoder/client lifetime, one API worker initially |
| Safe progress + validated final vs raw token streaming | Makes waiting visible while preserving answer validation | Does not make final inference faster | Never expose unchecked policy prose |
| Same-origin Next proxy vs browser-to-internal API | Keeps model/DB secrets behind server; simpler cookie behavior | Proxy abort, status, cookie and stream forwarding require tests | Fixed upstream, explicit paths, no arbitrary target URL |
| Memory sessions vs new database history | Matches privacy protocol; no student-record persistence | Restart loses context, replicas do not share it | Keep memory, bound sessions/jobs/replay records |
| Student APIs first vs simultaneous hosted admin | Delivers required thesis workflow sooner | Admin live access is deferred | Prepare separate read-only design now |
| Bounded PDF support vs adding photo OCR while wiring | Reuses working parser/confirmation boundary | Real PalSU layouts still unverified | PDFs first; photo support is a separate acceptance gate |

On RTX4060 8GB, reuse the existing inference service and prefix-cache setting; do
not start another model or move embeddings onto VRAM by default. Apply bounded
admission and parser jobs, not extra parallel LLM workers. No new models or sweeps.
The existing warm-backend observations exclude browser/API/queueing and are not
an end-to-end SLA. Measure those layers separately; retain all validation.

## Workstream and proposed decisions

Implement sequentially where ownership/contracts depend on each other: HTTP DTOs
and admission; research bootstrap/session chat; progress and SDK adapter; source
projection; uploads/provenance/confirmation; browser acceptance. Admin design can
proceed independently. Reuse synthetic contracts/tests and accepted language cases;
do not repeat source reviews, train a model or rerun all retrieval experiments.
No subagents launched; no benefit justifies additional coordination for this setup.

Owner summary: retain stack and framework pins, propose compatible SDK6 packages
and a resolved Zod peer only with owner approval, build text/clarification/clear/
citations first, then private PDFs. Prepare the admin design separately with no
private student data or approval/activation controls. Carry master24 photo and
Taglish limits explicitly; formal Phase 11 exit still requires its browser flows.
