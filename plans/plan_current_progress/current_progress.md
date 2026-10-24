# Current progress

Updated24October2026. Phase11 remains active; no phase closure or deployment.
Implementation worktree: p11-frontend-integration / feat/p11-frontend-integration.
Owner preview: C:/Users/Hawksprey/source/repos/Bintanong / frontend.
[Tasks](../2026-10-24-student-ui-backend-integration-plan.md) |
[Checkpoint](../phase-11-checkpoint.md) |
[Landing/auth delivery](../2026-10-24-landing-auth-concept2.md).
Last full snapshot before this condensation:1c0ab97; use git show for history.

## Latest change

Sidebar examples removed in favor of actual current-chat navigation, an empty state
and selected first-question title. Opening it preserves drafts and sends no request;
acknowledged New chat clears it.55 UI/four browser tests/typecheck/build PASS;
navigation RED→GREEN; desktop/mobile/light/dark screenshots checked.
Existing master8/23.2 retention remains: temporary only. Production recommendation
is opt-in saved history plus temporary mode, with owned conversation APIs/RLS,
retention/deletion and independent bounded reasoning context; not yet authorized
or implemented. Plain chat can contain academic data too; PDF exclusion is insufficient.
Guided clarification remains4dcd9bf/68b70e1;667 backend tests/2 photo xfails from that
delivery were not repeated for this sidebar-only change.
[Evidence/current blocker](../2026-10-24-student-workspace-polish.md).

Next/login3215 restored200; real API8021 restart fails loading hosted curriculum
facts: `facts require course_code and only supported field names`. Exact hosted
field mismatch undiagnosed; guards/data unchanged. No live clarification/model claim.

Earlier landing3/auth2 delivered; actual PSU login owner-verified ("PalSU email works
now"). Non-PSU rejection/full authenticated manual checklist remain unverified.
Local public config remains ignored; no secrets staged. [Auth/setup delivery](../2026-10-24-landing-auth-concept2.md)
and [manual checklist](../../docs/development/google-sign-in-local-setup.md) retain details.

## Verified integration baseline

13 newer backend commits through4a134bf merged as04a03ea; frontend mergeede9f84.
Owner-approved push fast-forwarded origin/frontend to60d285f at14:36+08; new UI
increment committed locally asa88acf5. Core routing/orchestration/generation/symbolic/contracts
matched origin; intentional auth/runtime integration adapters remain. Main pins
synced by npm ci; all21 direct pins and four manifest/lock hashes unchanged.
No unfinished lifecycle work copied from the integration worktree:15 modified
product/test files and3 untracked lifecycle files preserved there, byte-identical.
Main local review and model directory preserved and excluded from staging.

Earlier fresh main baseline:3383 backend passes/2 expected photo xfails. Earlier
synthetic Next/FastAPI browser:10 families/16 requests pass. Actual Prolog validated
4 sources; bounded RAG returned handbook page46. Hybrid/quality acceptance remains
incomplete. These backend observations were not repeated for this UI-only change.
Saved full suite:6494 passed,2 failed,1 skipped,2 xfailed,1552 subtests. Both failures
are Docling/Transformers requiring huggingface-hub<2 while2.2 is installed. No repair.
WSL16GB remains unverified: last check found memory=8GB and Ubuntu7.8Gi total.

## Next action

Diagnose the real API's hosted-ledger fact-field mismatch against its reviewed
release before rerunning actual authenticated clarification acceptance.
[Evidence](../2026-10-24-student-workspace-polish.md).

## Remaining boundaries

E3 office referral is included. Special-class fee, partial answers, pending-question/
replay, aliases, actual grade layouts and Hybrid/language/latency exits remain open.
Photos/scans unsupported. Research source/scope/privacy holds remain; no university
approval, public activation or persistent academic records. Figma references were
read in the browser because MCP was unavailable; original design exports not obtained.
