# Optional guest access — verification and delivery

28 October 2026. Codex B in Orca `p11-frontend-integration`. Implements the owner's
guest/full-feature PDF decision; optional PSU login remains. [Design](2026-10-28-guest-mode-design.md)
and [current task](2026-10-28-p11-frontend-integration-task.md). Phase11 remains active.

## Result

Landing and login pages offer direct chatbot access. Guests can select curriculum,
chat, inspect sources, review/confirm temporary PDF course results, delete uploads
and clear their session. The workspace labels guest access and offers optional sign-in.
Small-screen controls retain the curriculum picker and 44px sign-in target.

API guest access requires explicit `allow_guests=true`; default remains false.
Absent credentials may use guest mode. Supplied invalid/non-PSU credentials and
unavailable authentication fail closed. Browser credentials cannot override the
server-resolved token. Guest/account sessions and answer-admission keys stay separate.
Access-change notifications abort pending browser work and reset local private state.
No guest account, database persistence, source activation or dependency change.

Code: 192a892, 805c11d, 9f804a7, 3f297d9. Claude reviewed API/frontend and mobile delta:
approved, no P1/P2. Owner policy amendment23e83aa; review3eb411b in primary.

## Verification

Ignored evidence: workspace `audit-evidence/p11-guest-mode-20261028`.

- Observed API RED13, config RED2, policy RED1; final focused107 passed
  (`api-config-final.log`). Includes guest A/B, guest/account, cookie rotation,
  expiry, PDF lifecycle, CSRF, supplied-token errors and answer admission.
- Frontend RED3; Node UI65 passed (`frontend/ui-green.log`), TypeScript passes.
- Real Edge browser with synthetic auth/answers/PDF: guest lifecycle5 passed;
  broader regressions15 passed. Mobile320 RED -> guest/entry7 passed; screenshot inspected.
  Signed-in controls, invalid-cookie503, in-flight cross-tab abort and private-state
  reset covered. These are application tests, not institutional accuracy results.
- Production build exit0 (`frontend/build-receipt.json`); built public `/chat`200 with
  guest controls at3216 and real proxied guest `/api/curricula` returns39 curricula.
  Existing workspace-root/standalone-start warnings remain.
- Full Python suite exit0 on9f804a7:7195 passed/1608 subtests,6 skipped,2 xfailed,
  6 warnings,1982.23s (`full-suite.log`, `full-suite-receipt.json`). Backend tree
  `9dfca6959a4fdc3055d114eb19d5cfb7f2a1e57e`, tests tree
  `5310b5b1f8780dfce541248d79c8cb595fdc535d`; subsequent lane changes frontend/docs only.
- Actual guest HTTP smoke exit0:39 curricula, five200/v1 streams without transport
  errors; source200, PDF upload/confirm200, delete204, foreign origin403, session clear204.
  Separate no-model cleanup probe confirms removed uploads404 and parsed cookie cleared.

## Actual-answer observations

Outer HTTP request times, excluding browser/render work and cold API/encoder start;
model and hosted/network work inside the API are included, browser end-to-end is unmeasured:
grading answer27.2s (1.0=98–100/Excellent, cited handbook); prerequisite question56.3s
and follow-up31.5s returned generic clarification; mixed Taglish question24.8s asked
for missing CC3 completion; after synthetic confirmed CC3/CC4 passes,22.5s returned
conditions satisfied. This verifies guest integration, not a passing accuracy/latency gate.
The prerequisite wording/follow-up gap was relayed to Claude; no model tuning attempted.
RAG/structured/Hybrid requests were sent but the mixed request remained clarification.
Model slot released after the bounded run; live-guest-smoke.log/live-smoke-receipt.json.
The old reused smoke helper printed a misleading truthy quoted-empty cookie and called
unsupported GET/session (405); live-cleanup.log independently verifies actual deletion
and cookie clearing using SimpleCookie. No production change was needed.

Commands: shared Python3.13 venv, `PYTHONUTF8=1`, `-X utf8 -B -m pytest -q
-p no:cacheprovider tests`, ignored external basetemp; frontend `npm run test:ui`,
`npm run typecheck`, `npm run build`; existing installed Playwright/Edge via
`node --test tests/browser/*.mjs` with explicit fixture environment. No installs.

## Limits and recovery

Real PSU Google sign-in remains owner-deferred. Old guest/account state becomes
unreachable after access changes but remains in process memory until expiry (P3).
A possible early sign-in notification race is unproved; an exploratory passing
probe was discarded without production changes. No claim that this race is resolved.
Guest admission limits apply to a server-issued session, not one human across browsers.
Existing source/scope/privacy, unknown-versus-unmet and English/Taglish guards remain.
No phase completion, institutional approval, public deployment or UAT removal inferred.

Suite and model slots released to Claude. Frontend3216 and real API8021 remain running
locally; synthetic fixture8024 stopped. Next: Claude merges reviewed guest lane and
updates central progress/checkpoint. Any new primary backend/tests changes need their
own appropriate verification; this receipt certifies only the exact trees above.
