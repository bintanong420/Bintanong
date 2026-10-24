---
artifact: phase-checkpoint
phase: 11
status: in_progress
sequence: 30
plan: plans/phase-11-backend-api-plan.md
head_commit: f989081
working_tree: dirty
updated_at: 2026-10-24T18:50:39+08:00
---

# Phase 11: original frontend with Lawrence's API

## Completed Tasks

- API/auth transport58bf669, connected original workspacea8b3091; real text/source/
  file/clear/Stop/queue controls and Supabase PKCE/sign-out. Backend authorization
  verifies PSU Google identity per request; no production synthetic fallback.
- Owner-requested13-commit backend sync through4a134bf; merge04a03ea, including E3,
  prerequisite display, missing courses, unsupported lookups and multi-topic retrieval.
  [Sync/recovery](2026-10-24-frontend-backend-sync.md); original frontend retained.
- Main frontend mergeede9f84 and dependency sync; owner-authorized origin/frontend
  fast-forwardf974eab ->60d285f verified14:36+08 with exact remote SHA and0/0 divergence.
- Owner-selected landing concept3/auth concept2 implemented locally; public root,
  protected /chat, correct sign-in destinations and explicit scope/privacy copy.
  [Decisions and delivery gate](2026-10-24-landing-auth-concept2.md).
- Ignored local public auth config prepared; owner configured Google Cloud/Supabase.
  Hosted Google now enabled; actual app/Supabase/Google redirect chain verified.
- Owner24Oct confirmed "PalSU email works now". Successful actual PSU login is
  owner-verified; this does not verify non-PSU rejection or the whole chat/upload flow.

## Current Task

Owner-requested student UI correction delivered ec403f5: visible logout, bounded
local credential removal despite research/auth outages, honest cleanup notice,
retry/progress and student-facing curriculum wording aligned with the thesis.
[Delivery and verification](2026-10-24-student-account-usability.md).
Sidebar a184d7c and guided clarification4dcd9bf/68b70e1 remain delivered. Temporary
state only; persistent/multiple resumable history has not been authorized/built.
Real API startup remains blocked by hosted-ledger fact validation. Phase11 final
integration review/acceptance remains open; no institutional activation or closure.

## Repository State

Main checkout frontend atec403f5; account/sidebar/clarification committed locally.
Recovered exact previous session01a16c88-a2f7-7e63-b82a-f32c00d47160. Product clean;
delivery/checkpoint/progress documentation being saved. Execution/evidence in polish report.
Changed frontend: root/login/chat, OAuth callback, proxy/auth-policy, styles,
appearance control and new page-access regression. Changed docs: student integration,
Google setup guide, dated landing/auth report, progress and this checkpoint.
Owner-local historical review remains unstaged in progress; untracked status review
and SEA-LION-E5-Embedding-600M directory remain untouched/excluded.
Implementation worktree retains15 modified product/test files and3 untracked lifecycle
files, previously verified byte-identical; no lifecycle WIP copied into main.
Full pre-condensation checkpoint/progress:ec403f5; prior1c0ab97/60d285f.
Recovery refs/copies remain in the sync record.
Local pre-condensation copies also in ignored landing-auth-setup evidence.
Next/login127.0.0.1:3215 restored200. API8021 fails hosted-ledger validation on startup.
Ignored frontend/.env.local contains existing hosted public key/origins, no Google secret.

## Verification Evidence

- Account correction:55 UI tests/typecheck PASS;11 serial browser checks plus one
  added running-answer logout regression PASS. Backend cleanup503 and expired-token
  refresh503 observed RED→GREEN; expired logout now approximately5s, own auth chunks
  removed/unrelated app cookie preserved. Origin/revocation/timeout/retry/concurrency
  checks PASS; eight light/dark widths and200% CSS zoom/focus/44px targets checked.
  Independent review's expired-token/clear race findings fixed; final review no
  remaining important issue. Isolated webpack build PASS; default Turbopack cannot
  resolve external node_modules junction, standalone tracing27-file warning remains.
  Copied-tree compile evidence does not prove a deployable standalone artifact.
- Sidebar:55 UI/four browser PASS, no invented history/request replay/local storage.
- Guided clarification:55 UI/typecheck/build,667 API/private/generation PASS,
  2 expected photo xfails; browser scope/unknown/alternatives/review/single-send,
  Escape/focus and retained draft checks PASS.320px/200% header fixed RED→GREEN.
  [Earlier evidence](2026-10-24-student-workspace-polish.md); no actual-model claim.
- Landing/auth:45 UI tests/build PASS; actual app/Supabase/Google redirect checked,
  owner verified successful PSU login. Anonymous API curricula401; full non-PSU and
  authenticated manual checklist remain unverified. No identity/token logging.
- Earlier committed-main baseline3383 backend passes/2 expected photo xfails;
  backend-sync worktree3387/2. Not repeated for this frontend/auth correction.
  Prior synthetic PDF/parser/source/clear/Stop cases10 families/16 requests PASS;
  real Prolog4 sources and bounded RAG handbook page46 observed; Hybrid remains open.
- Saved full suite6494 passed,2 failed,1 skipped,2 xfailed,1552 subtests. Docling
  failures: huggingface-hub2.2.0 versus Transformers>=1.5,<2. No dependency repair.
  WSL owner-reported16GB unverified; last observation8GB/7.8Gi, no config change.

## Versions and Digests

Node24.21.0/npm11.19,React19.3.0,TypeScript7.0.2,Next16.4.3,ai7.0.152,
react SDK4.0.156,Supabase SSR0.12.7/js2.118.0;sharp0.35.5/source-map-js1.2.2.
Tests Python3.13.12; API existing p11 venv3.13.5/FastAPI0.141.1.
All21 direct pins/four manifest+lock hashes unchanged in approved dependency sync;
no further dependency/schema/model changes for landing/auth. Existing model pins retained.
Derivative policy112e86304352928a0d896c3b3194176c11f3ae7ef49ec998a9df47ce3f262240.
Hosted39 curricula/19 chunks/52 fields/54 spans retain their recorded limitations.

## Decisions

- Owner selected landing3/auth2 and antislop during implementation. Existing approved
  campus asset replaces template artwork; no fake user counts, email/GitHub auth or
  invented university seal. Figma browser/prototype read; MCP unavailable.
- Supabase user/email persistence authorized by master25.1; academic chat/files stay
  temporary. Keep server-side verified PSU Google policy and account isolation.
- Preserve real RAG/Prolog/Hybrid, canonical validation, queue and isolated PDF parser.
  Explicit resend is a new check; completed-response replay is not promised.
- Historical interface preparation is not a second formal Phase11 plan.

## Known Failures or Blockers

Actual PSU login owner-verified; non-PSU/full manual flow unverified. Real API startup
now fails load_release_curricula/compiler/_facts: required/allowed fact-field validation.
Runtime-role SELECT isolated unsupported units.printed/units.rle (2117 records in
39 selected ledgers). No source data changed or guard weakened. Merge preview
frontend→origin/dev c0d3e22 clean, matching frontend tree;10 local commits unpushed.
Docling environment failures unresolved. Fee/partial answers,pending-question/replay,
aliases,real grade layouts,Hybrid/language/latency exits remain open; photos unsupported.
No phase closure, university approval, public deployment or institutional activation.

## Next Action

Restore reviewed-ledger field compatibility with regression coverage, then verify
real API startup and authenticated curriculum/clarification before working integration.

## Do Not Repeat

Do not rebuild the backend, reinstall approved pins, download weights or repeat
settled source reviews. Preserve dirty owner work and all source/privacy boundaries.
Context rechecked24Oct after rollover: thesis physical17–18/65–66, routing PNG,
master16/25 and prior23/24; Phase10 handoff. Public scope/privacy wording matches
these boundaries and the explicit master25.1 auth-email storage decision.
