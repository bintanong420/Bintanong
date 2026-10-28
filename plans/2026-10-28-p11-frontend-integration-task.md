# Phase 11 frontend integration — Codex B

## Current task: optional guest access

28 October 2026. Orca lane p11-frontend-integration / feat/p11-frontend-integration.
Last full task snapshot before replacement: 9f804a7. Prior integrated delivery:
[results](2026-10-28-p11-frontend-integration-results.md).
Primary cad59fd synced through 4aae281 in 9fb6449.

Owner requested entry without login while keeping optional PSU sign-in, then selected
“Same chatbot features, including temporary PDF uploads.” [Design](2026-10-28-guest-mode-design.md).
Claude approved the bounded flow and recorded master25.1/owner amendment23e83aa.
No UAT removal, source activation, dependencies or hosted configuration writes authorized.

## Delivered increments

- f19f017 design; 192a892 explicit guest API policy, verification of supplied tokens,
  separate guest/account sessions and namespaced admission. SessionStore unchanged.
- 805c11d research config allow_guests defaults false; explicit true enables guest access.
  Present invalid/non-PSU/unavailable credentials never downgrade to guest.
- 9f804a7 public chat/guest continuation, optional login, guest/account controls,
  absent-vs-error distinction and browser abort/reset when access changes.
- 3f297d9 mobile guest controls: readable curriculum picker and 44px sign-in link.
- No guest Supabase user/account, stored conversation or private persistence is created.
  Existing cookie, expiry, clear/delete, CSRF, limits, source/scope/privacy and queue remain.

## Verification and active runs

Evidence: workspace audit-evidence/p11-guest-mode-20261028 (frontend subfolder for UI).
Shared Python3.13 venv; PYTHONUTF8=1; -X utf8 -B -m pytest -q -p no:cacheprovider;
external basetemp. Existing Node/browser tools only; no installs.

- API RED13 missing setting -> GREEN; cookie-domain test setup fixed separately.
- Factory config RED2 -> GREEN. Policy combination RED1 -> GREEN.
- Latest API/auth/session/upload/stream/factory focused: 107 passed (api-config-final.log).
- Frontend RED3 -> Node65 passed (frontend/ui-green.log), typecheck passes.
- Browser RED3 -> 5 passed (frontend/browser-lifecycle2.log): guest entry, invalid-cookie
  refusal, cross-tab abort/reset, signed-in controls and complete guest PDF lifecycle.
  Accounts/data/pipeline are synthetic; these checks are not institutional accuracy results.
- Broader browser15 passed; mobile320 RED -> guest/entry7 passed and screenshot inspected.
  TypeScript and production build complete; built guest /chat200 at3216 without login.
- FULL SUITE: exit0 at9f804a7;7195 passed/1608subtests,6skipped,2xfail,6warnings,
  1982.23s. Exact command/head/trees/results in full-suite-receipt.json; full-suite.log
  is raw output. Trees unchanged; suite slot released to Claude.
- LIVE RUN: none; Codex B released model slot after bounded guest HTTP smoke exit0.
  Five200/v1 streams; source200, PDF upload/confirm200, deletions204, foreignOrigin403;
  no-model cleanup proves old uploads404/cookie cleared. See [results](2026-10-28-guest-mode-results.md)
  for actual-answer/HTTP-timing limits; generic prerequisite/follow-up clarify remains.

## Context, boundaries and next action

Thesis17–18/39–44 and routing PNG; master3/11/13/15/16/23–26; Phase10handoff/Phase11plan,
current checkpoint, undergraduate/source-gap and owner decisions consulted.
Guest changes access only; unknown-versus-unmet and English/Taglish replies remain.
Central snapshots/master/owner ledger belong to Claude. No phase advancement.
Native frontend worker hit a usage quota; root completed changes inline. Claude approved
guest API/frontend and mobile delta; no P1/P2. P3: old mode's session stays unreachable until
expiry, and possible early cross-tab notification race remains unproved. Real PSU sign-in
remains owner-deferred. Next: Claude merges reviewed guest branch and central snapshots,
using exact-tree receipts; his new primary changes retain separate verification. No sweep.
