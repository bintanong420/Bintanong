# Guest mode — proposed behavior

28 October 2026. Codex B; existing Orca frontend-integration lane. Status: design and
guest-upload choice pending owner response; no guest production behavior changed.

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
- Whether guests also use temporary PDF upload/confirmation is the one open capability choice.
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

Builder check: no additional owner choice beyond guest uploads. Keep absent credentials distinct
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

Current next action: settle the guest-upload choice and approve this bounded flow before
production implementation. Evidence will stay ignored under workspace audit-evidence.
