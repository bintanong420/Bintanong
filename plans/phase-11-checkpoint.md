---
artifact: phase-checkpoint
phase: 11
status: in_progress
sequence: 21
plan: plans/phase-11-backend-api-plan.md
head_commit: 60d285f
working_tree: dirty
updated_at: 2026-10-24T15:14:09+08:00
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

## Current Task

Owner manual verification of actual PSU sign-in and authenticated workspace flow.
[One-document checklist](../docs/development/google-sign-in-local-setup.md).
[Integration tasks](2026-10-24-student-ui-backend-integration-plan.md) remain active;
this UI delivery does not close Phase11 or expand institutional release authority.

## Repository State

Main checkout branch frontend at60d285f plus this UI/docs/test increment (not pushed).
Changed frontend: root/login/chat, OAuth callback, proxy/auth-policy, styles,
appearance control and new page-access regression. Changed docs: student integration,
Google setup guide, dated landing/auth report, progress and this checkpoint.
Owner-local historical review remains unstaged in progress; untracked status review
and SEA-LION-E5-Embedding-600M directory remain untouched/excluded.
Implementation worktree retains15 modified product/test files and3 untracked lifecycle
files, previously verified byte-identical; no lifecycle WIP copied into main.
Recovery refs/copies in sync record; last full snapshot before condensation60d285f.
Local pre-condensation copies also in ignored landing-auth-setup evidence.
Next dev127.0.0.1:3215; authenticated research API127.0.0.1:8021; existing model services.
Ignored frontend/.env.local contains existing hosted public key/origins, no Google secret.

## Verification Evidence

- New page-access regression RED missing export ->GREEN2; complete frontend45 PASS.
  Pinned Node24.21: next typegen, tsc --noEmit and final production build PASS.
- Actual Edge31 checks PASS: both pages,320/390/768/1440 widths,light/dark/system,
  keyboard skip, scope/privacy links, protected chat/login, enabled Google control,
  wrong-account error,200% auth text reflow and no browser runtime errors.
- Browser contrast RED1.108:1 exposed inherited anchor foreground overriding shared
  button color; scoped selector fixed it. Final controls minimum14.05:1 both themes.
  Explicit appearance accessible name fixed after browser locator failure.
  Rendered text plus wrong-account alert minimum5.58:1; both themes meet4.5:1.
- Actual root/login200, anonymous chat307 ->login. Google enabled in hosted settings;
  POST/auth/login303 sets PKCE cookie ->Supabase authorize302 ->accounts.google.com.
  Both expected callbacks verified. Actual human code exchange remains unobserved.
- Research readiness200: Supabase/Janus/embedding/Bintu/student-runtime all true;
  anonymous frontend/api/curricula401. No bypass or token/identity logging.
- External browser/scripts/screenshots/oauth-readiness.json: ignored workspace
  audit-evidence/p11-20261024/landing-auth-setup. Exact commands and gate in delivery.
- Earlier committed-main baseline:3383 backend passes,2 expected photo xfails;
  backend-sync combined worktree3387 passes/2 xfails. Core backend matches origin;
  intentional committed API/auth/runtime adapters differ. Not rerun for this UI task.
- Earlier synthetic Next/FastAPI browser:10 families/16 requests PASS, including PDF
  parser/review/remove, failed clear, Stop, sign-out, IME/themes/reflow. Actual Prolog
  validated4 sources; bounded RAG handbook1.0 ->98-100/Excellent with page46 citation.
  Initial RAG outage/Hybrid insufficient evidence and quality limits remain disclosed.
- Saved full suite13:58:6494 passed,2 failed,1 skipped,2 xfailed,1552 subtests.
  Both Docling conversion failures: huggingface-hub2.2.0 vs Transformers>=1.5,<2.
  No dependency repair. Earlier environment check: WSL memory=8GB/7.8Gi observed;
  owner-reported16GB not verified; no config edit/restart performed.

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

Actual PSU/non-PSU human OAuth and authenticated manual flow await owner testing.
Docling environment failures unresolved. Fee/partial answers,pending-question/replay,
aliases,real grade layouts,Hybrid/language/latency exits remain open; photos unsupported.
No phase closure, university approval, public deployment or institutional activation.

## Next Action

Record owner's actual sign-in/workspace manual result using the checklist, then
resume preserved lifecycle review and remaining Phase11 verification.

## Do Not Repeat

Do not rebuild the backend, reinstall approved pins, download weights or repeat
settled source reviews. Preserve dirty owner work and all source/privacy boundaries.
Context rechecked24Oct after rollover: thesis physical17–18/65–66, routing PNG,
master16/25 and prior23/24; Phase10 handoff. Public scope/privacy wording matches
these boundaries and the explicit master25.1 auth-email storage decision.
