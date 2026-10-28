# Guest mode design: Claude review

28 October 2026. This reviews Codex B's `plans/2026-10-28-guest-mode-design.md` (lane
`p11-frontend-integration`) under the [workstream split](2026-10-28-phase11-model-workstream-split.md).
Verdict: **approve the bounded flow**, subject to the conditions below. Central records (master 25.1, owner
ledger, progress) get updated once the owner confirms the flow. Until then the design stays a proposal.

## Why the design is safe as proposed

- Isolation already exists. Guest sessions carry `account_id=None`, and the merged session binding
  (`sessions.py`) returns "unknown session" whenever the account differs. So guest↔account and
  account A↔account B cannot share state. No SessionStore change is needed, as the design says.
- A bearer token that is present but invalid fails closed. A bad or non-PSU token must never fall back
  to guest. Missing credentials alone mean guest, and only when guest mode is configured.
- No new persistence, Supabase anonymous users, dependencies or migrations. Signed-in sessions are also
  memory-only, so guest mode adds no new stored data.

## Conditions

1. **Explicit configuration.** Guest access is a settings flag. It defaults off in code and is enabled
   in the research configuration, so the authenticated-only mode stays testable and selectable.
2. **Separate state on mode switch.** Signing in or out starts a new session. Never adopt, merge or
   carry over guest uploads, confirmed grades or conversation, in either direction (the design already says this).
3. **Same answer path.** Guests get exactly the same routing, scope, source and privacy guards. There is no
   reduced or different answer pipeline, and the UI labels guest state clearly.
4. **Capacity disclosure.** Guests can open many sessions. The existing session cap, eviction of empty
   sessions and the global model queue bound load, but this is a research-build limit, not abuse protection
   for public deployment. Record that limit, with no public-deployment claim.
5. **Tests first:** guest chat/stream without a token; invalid present token refused; guest A/B and
   guest/account isolation through chat, clear and expiry; flag off restores sign-in-required behavior.

## Owner decision still open: guest PDF upload

Recommendation: **allow it with the same temporary handling.** Uploads are already in memory only,
confirmed per session, deletable, and expire on idle for signed-in users too. A guest gets the same
privacy, and blocking it would remove the main personalised prerequisite feature from guests.
If the owner prefers caution on shared computers, the alternative is to show guests a
"sign in to upload grades" prompt. Either way, no upload state carries across a sign-in.

## Requirement change to record after approval

Master 25.1 currently requires PSU sign-in to enter the chatbot. After owner approval, record this:
guest access allowed; PSU sign-in optional and unchanged; real PSU sign-in verification still
owner-deferred. Add a dated owner-ledger entry. No change to undergraduate scope, UAT status or release gates.
