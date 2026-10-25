# Clarification recurrence and stable local preview

25 October 2026; local frontend only. Phase 11 remains active.

The owner reported CC4/L not passed, CC3/L passed, BSCS 2018 curriculum,
repeated idle page refreshes, and an unsolicited grade popup for prerequisite listings.

## Cause and correction

The v20 three-line prompt improvement was incomplete. A fresh full-path run with
short CC5 invented an extra operation from supplied completion statements; target
containment rejected it and generic repair repeated it. The same choices with
printed CC5/L passed. Alias resolution itself remained valid.

Commit252a951 adds narrowly scoped repair guidance for uncontained_part_target and
part_count_mismatch. The latter is extracted from a known Pydantic error on the
existing repair attempt. Both ask the interpreter to preserve genuine questions
and supplied claims while removing invented work. Persistent errors retain their
prior failure outcomes. Router prompt version is v22; validation, retry budgets,
Prolog, reviewed data and authorization are unchanged.

The backend already returns prerequisites before offering a completion check.
The frontend opened every supported clarification automatically. Commit9e0a399
initializes it closed: the existing clarification button opens it explicitly.
This applies to supported clarifications generally; required unknowns and canonical
answer statuses remain unchanged. No keyword routing or inferred grades were added.

## Verification and limits

- Repair regression RED1, then count-error RED1; final focused28 and broader905
  routing/generation/API tests PASS,25.52s. System Python3.13, pytest without cache,
  external basetemp repair-v22-regressions under workspace audit-evidence.
- Actual v21 full pipeline: inverse Filipino grades -> ineligible; both passed ->
  eligible; both unmet -> ineligible. No missing facts. The additional English case
  FAILED due to declared2/emitted3 parts; the overall v21 runner exited1.
- v22 English router probe: recorded first packet/input replay, then actual live
  repair and style calls -> validated Symbolic,1 part, both claims retained, no
  missing facts. This is component evidence, not a fresh English API/Prolog run.
- Browser regression RED unsolicited modal -> GREEN explicit button, preserved
  selected facts, two explicit sends, no invented fallback dialog. Synthetic
  loopback fixture only; no owner Google credentials or production auth bypass.
-57 UI tests PASS; production Next build/TypeScript PASS. Initial rebuild attempts
  hit Windows EBUSY in the running standalone directory; after stopping the server
  and returning its terminal to repository root, the fresh build passed.

## Running preview and recovery

http://127.0.0.1:3215 now serves the production standalone build, removing HMR.
Same frontend environment, PSU authentication and API8021. API restarted with v22;
model18088 and encoder8001 unchanged. API readiness and proxied frontend health
return200 with all five probes true. Clean-browser45s idle check: zero extra
navigations, HMR sockets or page errors. Owner's authenticated idle tab is untested.
Dev logs contained repeated compilation/chat requests and Dark Reader hydration
warnings; the extension is not established as the cause of the refreshes.

Orca terminals: frontend term_c27fc4d5-7f8b-44d0-89d6-4760153be9d9;
API term_d7ff23ac-0d58-4d28-b913-bdaff5cd6f30. Restart frontend with workspace
audit-evidence/p11-20261025/local-server-restart/serve-stable.mjs, not next dev.
After rebuilding, copy .next/static and public into the standalone frontend tree.
API launcher remains audit-evidence/p11-20261024/guided-clarification/start-owner-preview.py api.
One browser reload and a fresh chat are needed after these server restarts.

Raw ignored evidence: workspace audit-evidence/p11-20261025/clarification-loop/
inverse-v20, repair-v21, repair-v22; local-server-restart/stable-idle.json.
Mixed prerequisite/procedure questions remain a known routing failure. No general
language, latency, RAG/Hybrid or full browser acceptance claim. No push, source pin
activation, dependency change or database write. Existing source/release holds remain.
