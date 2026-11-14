# Existing frontend compatibility with the Phase 11 backend

Owner asked to inspect `origin/feat/p11-backend-api`, then whether it matches
the existing frontend. Fetched 24 October 2026: remote and local backend both
`34a21ca` (zero commits ahead/behind). Compared the implemented frontend on
`feat/p11-api-interface` at `db4275e`; no merge or product changes performed.

**Finding: the existing chat frontend cannot call this backend unchanged.**
The student layout can be reused, but sharing the AI SDK stream protocol does
not establish application-contract compatibility.

Owner subsequently selected `feat/p11-backend-api` as the integration target and
asked whether the earlier interface branch was inferior. Use this backend as the
foundation; retire the uncommitted SDK6/interface-backend task draft. Original UI
presentation remains reusable. Neither whole-branch replacement nor a new backend
rewrite is justified by this comparison.

| Boundary | Existing frontend at db4275e | Backend at 34a21ca |
|---|---|---|
| Chat body | `request_id`, `turn`, `text` | SDK `messages` with message ID/role/text parts; optional `programId`, `curriculumId` |
| Session creation | Explicit `POST /session`, checked session response | Session issued by `require_session` on an applicable request; no POST/GET session projection |
| Credential | Proxy forwards `bintanong_session` | `__Host-bintanong_session`, Secure/HttpOnly/SameSite=Strict |
| Progress | `data-progress` with `code` | `data-status` with `stage`, including queue waiting |
| Answer order/data | Full `data-answer` before text; identity, language, text, context actions, sources | Text first, `source-document` parts, then `data-answer` with status and conditional flag |
| Errors | Nested HTTP `error.code`; stream `data-failure` | HTTP string `error`; stream `error` with fixed `errorText` |
| Replay | Reuse request/turn identity after uncertain failure | Completed message IDs refused as `already_answered`; not equivalent response replay |
| Upload | Session scope, `file_id`, revision/choices; GET review endpoint | Explicit program/curriculum query parameters, `uploadId`, row/course camelCase fields, confirm `decisions` |
| Source inspection | `src-` IDs, strict snake_case response | Evidence IDs carried by `source-document`; camelCase response and source-limit flag |
| Typed course details | GET/POST `/context` | No equivalent endpoint in this backend |
| Runtime entrypoint | Earlier branch's configured lifespan application | `create_app(ApiServices, ApiSettings)` with real pipeline injected by trusted composition |

Inspected backend `chat.py`, `stream.py`, `session.py`, `app.py`, `uploads.py`,
`sources.py` and frontend `student-transport.ts`, `student-contracts.ts`,
`student-proxy.ts` from the named frontend commit. Direct Pydantic validation
confirms the frontend's actual chat-body shape is rejected for missing
`messages`; a separate assertion confirms the cookie-name mismatch.
These are contract checks, not a browser or inference acceptance run.

Integration should retain the selected frontend's visual components and adapt
its real transport/controller to the chosen backend contracts. Preserve backend
session/origin controls, waiting/busy feedback and explicit upload confirmation.
Resolve typed details, response replay, continuation and answer metadata
deliberately; an adapter must not claim these exist merely by renaming fields.
Use the backend's recorded SDK/auth/dependency decisions when doing that slice;
this comparison does not install or upgrade packages.

The shared worktree changed from the interface branch to the backend branch
during this inspection (Git reflog records checkout at 12:45 +08). The two
old-branch preview processes started by this inspection were stopped to avoid
mixed imports and hot reload across branches. Inference containers were left
running. The old `/chat` preview has not been re-established on this backend;
its root frontend remains the compatibility health dashboard.

E3 (shifting-question clarification) remains the backend checkpoint's next task.
No source decisions, release state, database data or dependency pins changed.

## Comparative capability analysis (independent follow-up)

Compared backend34a21ca with interface db4275e. The backend branch is the stronger
base for its implemented queue, isolated upload work, security fixes and explicit
SDK7/auth decisions. These are reasons to retain it, not proof of complete chat.

| Capability | Backend branch | Interface branch/reference value |
|---|---|---|
| Answer capacity | Implemented1 running/4 waiting and early busy response | Earlier admission cap without that queue; do not replace the queue |
| Student condition wording | `presentation.py` already humanizes the known canonical conditions | The earlier task to build this would duplicate completed work |
| PDF confirmation/deletion | Existing isolated parser, explicit choices and linked-fact deletion | Multi-file review/revisions and typed `/context` flow exist; adapt only needed behavior |
| Conversational controls | Generator returns fixed host controls; no conversation status/dialogue generator | Natural bounded dialogue and checked catalogue controls were added; useful reference, not a wholesale port |
| Clarification completion | Previous validated entity/topic context only; no pending question | Also lacks a complete pending-intent lifecycle; neither branch solves it already |
| Lost committed response | Completed latest message returns409 `already_answered` | Exact committed-response replay exists; review and port the behavior to current identity/session rules |
| Confirmed facts with natural scope | Filtered before semantic scope resolution; explicit picker scope supplies them | Later binding/available-facts correction exists; preserve ownership and current scope |
| Frontend/SDK | Minimal health UI; SDK7 client/parser integration still due | Original UI and tested SDK6 transport exist; preserve presentation, implement the selected backend contract |
| PSU sign-in | Master25 requires it with UI; token/domain/account enforcement is not implemented in the inspected app | Earlier temporary-session UI is not an account-auth implementation either |

Do not count a capability as missing merely because its type/function name differs.
In particular, repeat neither readable-condition projection nor basic upload/queue
implementation. Conversely, adapting field names cannot create pending-question
memory, response replay, typed detail APIs or account authorization.

### Fresh executable evidence

In an isolated checkout of34a21ca, system Python3.13.12 ran:

```powershell
py -3.13 -B -m pytest -q -p no:cacheprovider --basetemp=C:/Coding-projects/bintanong_workspace/audit-evidence/p11-backend-analysis-20261024/api-baseline tests/test_api_chat_turns.py tests/test_api_stream.py tests/test_api_session.py tests/test_api_uploads.py tests/test_api_sources.py tests/test_api_curricula.py tests/test_api_presentation.py tests/test_api_research_pipeline.py
```

Result: **83 passed in4.18s**. Six additional synthetic boundary probes passed
with `py -3.13 -B .../audit-evidence/p11-backend-analysis-20261024/probe_chat_link.py`:

1. After an original question and a curriculum-only reply, the chat port supplies
   only that latest reply; `SessionView` has no pending-question field. This probes
   the port with a recording pipeline, not actual semantic-model performance.
2. Retrying a committed message returns409 `already_answered`, not its answer;
   pipeline call count stays1. The existing regenerate path is different work.
3. A saved synthetic fact reaches the pipeline0 times when scope exists only in
   message text, and1 time when the same scope is supplied through checked picker
   fields. This proves pre-routing filtering, not a claim about all model outcomes.
4. For two distinct inputs routed as greeting controls, generation returns identical
   fixed text without model generation. This does not assert the live router would
   classify every social reply as greeting.
5. A candidate's `missing_facts=('curriculum_id',)` survives internally but the
   stream's `data-answer` contains only `status` and `conditional`; structured
   language/missing-field/continuation metadata is absent.
6. The default `main.app` exposes health and no chat. The injected `app.create_app`
   is the student application; preserve that distinction in a tracked launcher.

### Consequence for the next plan

Build on the selected backend, reuse the original UI, and add only verified gaps:
complete checked answer/action metadata; bounded same-question continuation;
fact binding after current-scope resolution; committed-response recovery; then
adapt the original controller/transport and review actions to these contracts.
Keep its queue, source boundaries, isolated parser and existing presentation.
Carry SDK7, approved dependency-review and PSU sign-in requirements into their
UI integration slice; do not silently reintroduce SDK6 or call planned auth built.

The approved natural-conversation design and this branch's master25 fixed-control
policy need explicit reconciliation in that plan: permit useful bounded social
repair while preserving off-topic refusal and evidence-backed institutional claims.
Do not weaken academic validation or add general institutional model answers.
The user's later clarification asks for comparison, not deletion of either branch.

No product edits, installs, model/DB calls, service restart or fresh browser/latency
acceptance by this follow-up. Reported prior full-suite/model observations remain
historical evidence, separate from these83 tests and six synthetic probes.
Documentation verification:10 `test_docs_hygiene.py` tests pass4.01s; phase-state
validation and `git diff --check` pass. Phase11 still has no complete final handoff.
