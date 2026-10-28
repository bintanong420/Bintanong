# Phase 11 frontend integration results

28 October 2026. Codex B, isolated `p11-frontend-integration` worktree. Phase 11 remains active;
this is local research integration, without public deployment, institutional approval or source activation.

## Delivered behavior and provenance

The owner selected frontend snapshot `e172f53c19bdd5d30ef5df2db4bf80ee47e27c3c`, then explicitly
approved its exact dependencies and `npm ci`. The lane imported only `frontend/`, retaining the
co-worker's layout, same-origin proxy, PSU Google login, confirmation controls and tests. Package
and lock Git blobs are exactly the supplied snapshot's; no whole-branch frontend merge occurred.

The API now sends the validated reply language, supported missing-field names and canonical
clarification choices expected by the real AI SDK consumer. Choices come only from host-resolved
printed course codes and validated unknown conditions. It does not infer a failed condition from
missing information, expose internal predicate names in choices, or change generation contracts.

Server-side Supabase verification requires a confirmed PSU email and verified matching Google
identity. It does not trust editable user metadata. Opaque verified account identity is threaded
through every API session mutation and per-account admission. Every credential-based SessionStore
operation checks that identity before touching state or idle expiry; another account's cookie
looks unknown. Unauthenticated test mode and trusted global wipe retain their original behavior.
No raw bearer token or email is stored by the SessionStore.

The tracked `backend/bintanong_api/research_app.py` factory uses the existing CPU query encoder,
reviewed curriculum resources and `ResearchPipeline`. Trusted ignored configuration pins the
current corrected 78-chunk package, exact pin/seal hashes and existing model verification manifest.
All seven package files are verified before client/model startup. Each answer rechecks hosted
active-research state and curriculum links; no shared HTTP-embedding modules, default 559 activation,
new dependency or synthetic institutional fallback was added. The CPU model loads once before
concurrent readiness/retrieval is exposed. Configuration and launch instructions are in the
[API README](../backend/bintanong_api/README.md).

Frontend notices, clarification dialogs, confirmed replies and retained student choices preserve
the validated English/Taglish reply language. The supplied static navigation remains English.

Owner direction recorded in primary `50a016b` asks for program/curriculum up front. The existing
picker now opens on a fresh chat, with no preselection and an explicit **Skip for now** for general
policy questions. Choosing or skipping never sends a question; only the student's selected scope
is sent with a later explicit submission. A successful chat reset prompts again. Manual reopening
keeps Cancel, and a failed list fetch still permits skipping. No new backend state or persistence.

## Verification receipts

Evidence root: `C:/Coding-projects/bintanong_workspace/audit-evidence/p11-frontend-integration-20261028`.
Synthetic fixtures are tracked; private/runtime inputs, environment files and raw receipts are ignored.

| Check | Observed result / receipt |
| --- | --- |
| Dependency install | Exact snapshot `npm ci --no-fund --no-audit`, 89 packages, exit 0 |
| Package/lock identity | Git blob parity with selected snapshot; no post-install lock drift |
| Session account binding | RED 15 → GREEN 87, `session-green.log` |
| Actual installed SDK/Python stream | RED for absent language/missingFields → GREEN; answered, clarification and insufficient-evidence streams parsed |
| Metadata/stream/presentation/chat | 47 pass, `metadata-green2.log` |
| Auth/session/upload/chat/stream isolation | RED 14 → GREEN 93, `auth-green3.log` |
| Factory/readiness/auth/probes | Readiness RED 2 → GREEN 32, `factory-green2.log` |
| Concurrent cold encoder | RED 3 model constructions versus expected 1 → GREEN 33, `cold-encoder-green.log` |
| Frontend unit/transport tests | `npm run test:ui`: 62 pass, `frontend-final.log`; explicit shared Python runner |
| TypeScript/build | `npm run typecheck`, `npm run build` pass; actual local-login configuration rebuild also passes |
| Dependency security | `npm audit --json`: 0 findings, `npm-audit.json` |
| Public browser | Both themes at 320/390/768/1440, enlarged text, contrast, keyboard focus and login redirect pass |
| Taglish/browser lifecycle | Observed English-notice RED → 4 pass for language, clarification, chat lifecycle and welcome, `language-browser-green.log` |
| Upfront scope and final browser regressions | Missing-prompt RED 3 → **11 pass**, sequential 8-file run, `scope-browser-final2.log`; 390/1440, unavailable list, Taglish, chat/clarification/Stop/navigation/welcome/header/public layout |
| Existing picker responsive behavior | Manual-Cancel regression RED → **1 pass** across 8 width/theme combinations and zoom, `scope-manual-green.log` |
| Real package preflight | 78 chunks / 78 vectors; 7 sealed files verified, zero network/model loads, `actual-package-preflight.json` |
| Real owned HTTP app | Liveness 200; unauthenticated curricula/chat 401 `sign_in_required`, `actual-http-boundary.json` |
| Public hosted auth settings | Read-only settings HTTP 200, Google enabled; no user-data query, `auth-public-settings.json` |
| Local login start | `/login` 200; `POST /auth/login` 303 to Google authorize with local callback; redirect not followed, `local-login-boundary.json` |
| Full Python suite | **7,164 pass / 1,608 subtests pass**, 6 skip / 2 expected failures / 6 warnings, 1500.12s, exit 0; tested `c4f6f07737714a1e873182e421b205d260fc3982`, `full-suite.log` / `full-suite-receipt.json` |

The Python command uses the shared verified venv, `PYTHONUTF8=1`,
`-X utf8 -B -m pytest -q -p no:cacheprovider`, with the lane's external `--basetemp`.
The complete suite command targets `tests`, without substituting a focused subset.
Exact command, with `PYTHONUTF8=1`:

```text
C:/Coding-projects/bintanong_workspace/audit-evidence/p05-real-retrieval-readiness-20261012/venv/Scripts/python.exe -X utf8 -B -m pytest -q -p no:cacheprovider tests --basetemp=C:/Coding-projects/bintanong_workspace/audit-evidence/p11-frontend-integration-20261028/full-suite-temp
```

UI tests set `BINTANONG_TEST_PYTHON` to that venv and run `npm run test:ui`.
Latest post-onboarding unit receipt: `ui-scope-final.log`, 62 pass. Final build including TypeScript:
`build-scope-final.log`, exit 0. Browser command uses `node --test --test-concurrency=1` over
`scope-onboarding`, `reply-language`, `clarification-loop`, `chat-workspace`, `welcome-layout`,
`workspace-navigation`, `entry-design` and `composer-stop` files. The separate account-controls run
selects its responsive dialog case; other account/OAuth fixture cases were not rerun.

Initial missing-fixture/Python-runner and BoundInput fixture setup errors were corrected before
recording behavior RED. One test initially omitted selected scope; its fixture was corrected.
An inline-env synthetic server launch was rejected by tool policy (“blocked by policy”, with no
stated reason). A reviewed launcher with explicit loopback/cwd/synthetic-key assertions and no shell
interpolation succeeded; no production auth bypass was added.
The historical `scope-browser-final.log` records a failed parallel browser run: two five-second
navigation timeouts under concurrent load and a navigation fixture missing its synthetic answer
pipeline. The fixture was completed and browsers ran sequentially; assertions stayed intact.
That historical failure is not the passing final receipt (`scope-browser-final2.log`).

## Review and commits

- `86b839b` task/proposals; `90203e4` isolated session binding and tests, independently reviewed clean.
- `e853b77` canonical stream metadata; `f506abf` approved frontend snapshot.
- `b1bc98b` server auth/account API integration.
- `5b3b04e` clean primary sync through `835aea7`.
- `de1e68a` sealed tracked runtime, readiness and launch documentation.
- `83af0e5` review P2 language override fix with browser RED/GREEN.
- `e1a132d` review P2 duplicate cold-load fix with concurrent RED/GREEN.
- `3a83152` startup/login checkpoint; `c4f6f0` clean primary sync including approved Charter lane.
- `130c4c7` owner-requested upfront scope prompt and browser regressions. Coordinator allowed
  frontend-only GREEN while the Python suite ran after checking Python has no Workspace/ScopePanel
  dependency. Backend, Python tests, dependency manifests and locks remain identical to the tested
  `c4f6f0` tree; UI validation is separate. `tested-python-trees.json` retains exact tree hashes.

The coordinator's independent reviews found the two P2 issues above; both were reproduced and
fixed. No remaining P1/P2 was reported after the cold-load fix. Central phase snapshots and
source/routing/generation files were not authored by this lane; current primary changes came
through conflict-free merges. The owner keeps login for now; considering UAT removal did not
change current product/evaluation requirements.

## Current limitations and remaining work

**Owner decision: “Leave real sign-in verification pending.”** Do not ask for a pasted token or
change hosted OAuth configuration to finish this lane. Actual PSU sign-in, accepted hosted local
redirect and authenticated real-source RAG/Prolog/Hybrid, follow-up, upload and deletion HTTP/browser
smoke remain pending. The synthetic authenticated lifecycle, SDK bridge and real unauthenticated
boundary checks do not establish that end-to-end live gate. No Gemma inference ran in this lane.

The local review login is `http://127.0.0.1:3216/login`. Its ignored environment maps only existing
public URL/anon credentials; no service-role key. The owned API and CPU model were stopped before
the exclusive full suite. Photos/scans remain unsupported, and the known answer/source/release
limitations inherited from Phase 11 remain in effect.

Observed factory construction was 72.48 seconds after module imports: hosted curriculum loading
finished at 17.35 seconds, encoder/dependent imports at 42.78, resource construction at 72.45.
These are one startup diagnostic, including hosted reads/CPU model load; they exclude Gemma boot,
inference, browser submission/rendering and queueing. They are neither student-visible latency nor
an achieved SLA or speed improvement. No browser/model latency distribution was measured.

Build/start report existing multiple-lockfile-root and standalone-start warnings. No formatter,
Python lint/type/security package was installed; full-suite and existing checks govern this build.
The institutional corpus/pin, models, dependencies outside the approved frontend snapshot and
release state remain unchanged. The suite's six warnings are existing Starlette/httpx, unregistered
GPU-mark and Docling/Pydantic deprecations; no failed test is hidden as a warning. Backend tree
`c4038d77d9358b18a88002880dbbc74372b49114` and Python test tree
`9b42e6511e13c1d4a6cd0d482127e03d0009c3f6` remain exact after the frontend-only onboarding commit.
The lane is ready for Claude's integration review with the owner-deferred authenticated live gate
explicitly open. No Phase 11 completion or release activation is claimed.
