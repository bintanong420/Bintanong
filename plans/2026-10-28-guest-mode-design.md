# Guest mode — approved behavior

28 October 2026. Codex B; existing Orca frontend-integration lane. Status: approved scope;
implemented in 192a892/805c11d/9f804a7/3f297d9; final verification running. Owner requested guest access with optional login, then selected
“Same chatbot features, including temporary PDF uploads” after the proposed flow was shown.

## Request and requirements baseline

Owner asks for a guest mode: students may go straight to the chatbot without signing in,
while the existing login remains available. This revises master 25.1's exclusive PSU-login
entry requirement. It does not remove UAT, expand undergraduate scope, activate sources,
or authorize hosted auth/database configuration changes. Existing master 15/16/23/26 and
thesis physical17–18 privacy/read-only boundaries remain. Routing PNG consulted; no routing
or reasoning change. Baseline primary `cad59fd`; current lane includes its documentation.

## Proposed student flow

- The landing page's chat action opens `/chat` directly. Login remains optional, with a
  visible guest continuation on the login page even when Google auth is unavailable.
- The chatbot shows Guest and Sign in for visitors; verified signed-in users retain Sign out.
- Guests use the same curriculum picker, grounded answers, sources and clarification flow.
- Guests also use temporary PDF upload, review, confirmation and deletion (owner confirmed).
- Guest chat/course context stays in the existing temporary session. No guest account, email,
  stored chat history or Supabase anonymous user is created. Existing clear/idle-expiry rules apply.
- Switching between guest and signed-in access starts separate session state; do not silently
  transfer or adopt guest uploads/grades into an account or expose account state as guest state.

## Proposed implementation boundaries

Codex B owns frontend/API/test changes. Reuse the existing opaque Secure/HttpOnly/SameSite
session cookie and account-aware SessionStore; no shared-store behavior change is needed.
Permit missing bearer credentials only under explicit guest-enabled API configuration;
present malformed, invalid or non-PSU credentials still fail verification. Preserve the
existing authenticated mode and distinguish unavailable auth from an intentional guest visit.
Keep CSRF, size, source/scope and queue guards. Guests share the model's global queue;
use the existing server-issued session identity for same-guest concurrent-answer admission.
This does not promise account-level limits across independent guest browsers.

Do not create a new auth service, dependency, database migration or persistence layer.
Master/phase/owner-ledger updates are proposed to Claude, which owns the central records.

Builder check: no additional owner choice; guest uploads are now confirmed. Keep absent credentials distinct
from invalid credentials and unavailable auth (the current token helper conflates them). Namespace
account/session admission keys. A mode change must abort pending browser work, discard late results
and reset chat, curriculum and private details, including sign-in/sign-out in another tab. Use the
existing auth integration for change notification; this does not authorize access by a client claim.
An explicit guest-enabled setting supplements authentication; do not disable token verification.

## Acceptance and validation plan

1. Observed RED tests: no-login page/API/stream, optional login, invalid credential refusal.
2. Guest A/B and guest/account isolation through chat, clear, expiry and (if approved) PDF
   confirmation/deletion; account switching cannot adopt another mode's private state.
3. Preserve same-origin CSRF and stream/citation/clarification contracts, queue bounds and
   signed-in PSU verification. No inferred curriculum or changed answer quality guards.
4. Focused API/session tests and Node tests, typecheck/build, actual guest browser lifecycle
   with synthetic sources/grades and a separate unchanged signed-in regression.
5. Fresh whole-change review and exclusive full Python suite; coordinate any model smoke
   with Claude. Real PSU sign-in remains owner-deferred; guest testing must not claim it.

## Implementation order and ownership

1. API: synthetic guest lifecycle/isolation/invalid-token/CSRF/admission regressions; observe RED;
   add explicit `allow_guests` alongside `require_auth`, enable it in the research factory, and
   namespace admission by verified account or server-issued guest session. Keep SessionStore intact.
2. Frontend independently: RED tests for public chat, token-free forwarding, optional-login copy,
   guest controls and identity-change resets. Preserve real server auth failures as failures.
   Change existing auth policy/proxy/pages/workspace, using existing dependencies only.
3. Integrate the two paths; focused API/Node suites, guest browser lifecycle, signed-in regressions,
   typecheck/build and review. Root stages/commits explicit units after reviewing worker output.
4. Coordinate one full Python suite and, when the shared model is free, bounded real guest HTTP
   smoke. No real-source accuracy result follows from the synthetic lifecycle.

Evidence: workspace `audit-evidence/p11-guest-mode-20261028`. Shared existing Python venv,
`PYTHONUTF8=1`, `-X utf8 -B -m pytest -p no:cacheprovider`, lane basetemp; Node `test:ui`,
typecheck/build, existing installed browser tooling. No installs/locks/model/hosted writes.
Current verification and next action: [lane task](2026-10-28-p11-frontend-integration-task.md).
