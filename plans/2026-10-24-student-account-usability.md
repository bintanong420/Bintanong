# Student account controls and curriculum wording

Owner request: fix logout and confusing UI, using wording familiar to a PalSU
undergraduate and consistent with the thesis's academic-guide role. This is a
Phase 11 correction on `frontend`, starting from `a184d7c`, not a retention change.

## Scope and implementation

- Reproduce failed session cleanup through the actual Next sign-out route and a
  synthetic API; signing out must remain possible while the research API is down.
- Bound cleanup waiting, clear browser credentials, and distinguish local sign-out
  from unconfirmed server cleanup. Preserve strict Origin checks and account isolation.
- Make Sign out visible; show progress and actionable failure text. Constrain alerts
  to the conversation width. Preserve drafts when an operation fails.
- Explain program/curriculum selection through subjects, prerequisites and the
  student's prospectus. Keep version/Proposed labels and advisory limitations.
- Reuse existing fonts, buttons, dialogs and auth SDK; no dependencies or saved chats.
- Verify expired/missing sessions, cleanup failure, cross-site rejection, responsive
  layout, keyboard use, light/dark themes and relevant UI regressions before committing.

Consulted after resume: thesis physical 17–18 and 65; routing PNG; master 23.2,
25.1 and recorded Phase 11 state. Private academic data remains temporary; sign-in
email is the explicit exception. No source, hosting or university-approval change.

## Diagnosis and design review

`POST /auth/signout` returned the research API's failed DELETE response before
calling Supabase signOut. The real API currently fails hosted-ledger validation,
so an unrelated service outage strands the account. Installed auth-js removes
local session storage even when remote revocation returns an error; verify actual
cookie removal and protected-route rejection rather than assuming revocation.

Heuristic baseline: user control severity 4 (logout blocked), visibility severity 3
(logout hidden in ellipsis), match-to-student-language severity 2 (research jargon),
error recovery severity 2 (full-width banner without a direct logout retry).
Subjective scoped design baseline: usability 4/10, typography 6/10, visual hierarchy
6/10. These are engineering judgments, not student usability-study results.

## Verification and delivery

Product commit: `ec403f5`. Independent read-only review identified expired-token
refresh failure and overlapping New chat/sign-out; both corrected and covered.
Final reviewer found no remaining important issue. No push or phase closure.

- Actual Next route RED: backend DELETE503 prevented sign-out; GREEN:204, auth
  revocation attempted, both browser credentials removed, protected chat redirects.
- Second RED: expired token plus refresh503 returned503 after26.6s. GREEN:204
  after approximately5s; own chunked auth cookies removed, another app's cookie
  retained. Five-second total cleanup deadline and three-second backend sublimit.
- Installed SDK can keep retry bookkeeping briefly after timeout; aborted fetch
  and the cookie-write guard prevent late requests/writes from restoring sign-in.
- `node --experimental-strip-types --test tests/*.test.mjs`:55 PASS.
- `node --test --test-concurrency=1 tests/browser/workspace-navigation.mjs
  tests/browser/composer-stop.mjs tests/browser/guided-clarification.mjs
  tests/browser/account-controls.mjs`:11 PASS. Added running-answer sign-out
  regression then passed separately using `--test-name-pattern="can stop an answer"`.
  Total12 browser checks, including eight theme/width layouts and enlarged text.
- `node node_modules/typescript/bin/tsc --noEmit`:PASS. Isolated
  `node node_modules/next/dist/bin/next build --webpack`:PASS, including TypeScript.
  Default Turbopack failed resolving the copied tree's external node_modules
  junction. Webpack standalone tracing warned about27 external dependency files;
  this copied-tree build is compile evidence, not a deployable standalone artifact.
- Tested curriculum load failure/retry, draft preservation, visible logout/progress,
  failed request retry, missing/expired sessions, remote revocation failure,
  slow cleanup, cross-site protection and clearing concurrency.
  Layouts:320/390/768/1440px, light/dark, Escape/focus restoration,44px targets,
  16px dialog body and CSS zoom200%. Mobile/desktop screenshots inspected.

Raw synthetic evidence:
`C:/Coding-projects/bintanong_workspace/audit-evidence/p11-20261024/account-controls/`.
Contains fixture/preview launchers, synthetic auth state, RED/GREEN logs and screenshots;
none are institutional/student records. Test environment:
`BINTANONG_BROWSER_URL=http://localhost:3219`,
`BINTANONG_TEST_API_URL=http://127.0.0.1:18093`,
`BINTANONG_BROWSER_STATE=<evidence>/synthetic-browser-state.json`,
`PLAYWRIGHT_MODULE=<existing cached Playwright>/index.mjs`.
The loopback fixture injects failed DELETE, slow DELETE, refresh503 and revocation503;
its synthetic auth endpoints bypass the research API's Origin middleware, while the
actual Next sign-out route retains its production Origin checks. No production bypass.

Final scoped engineering judgment: usability8/10 and typography8/10; student SUS/UAT
is still required. Top-design weighted rubric5.3→5.9/10 (typography6,composition6,
motion4,color6,details8): stronger interaction craft, existing composition/identity.
Reaching10 would need broader composition/craft work and student validation, outside
this correction. Refactoring UI:6/8 diagnostics,8/10 rounded; label/value hierarchy
and a fully uniform spacing scale remain refinement areas. No cinematic motion or
font/dependency changes were justified for these form and account tasks.

Official reference: [Supabase signOut](https://supabase.com/docs/reference/javascript/auth-signout).
Installed SSR0.12.7/js2.118.0 implementation was inspected before using
`clearAuthCookiesAtScopes`; sign-out remains local to this browser's auth session.
Current browser credential deletion is not a claim that every issued JWT is revoked.

Live PSU OAuth login/logout was not repeated. The real research API remains blocked
on hosted-ledger fact-field validation, so live curriculum/answer acceptance remains
unverified. Validation guards and institutional source data were not changed.

## Follow-up: exact startup blocker and frontend-to-dev readiness

Fresh runtime-role SELECT against the configured release on24October:39 linked
ledgers contain2117 course records outside local `authoring.FACT_FIELDS`. The
unsupported names are `units.printed` and `units.rle`; the first rejection is in
`abcomm-2018-2019`, with course_code present. The current allowed unit fields are
units.total/units.lecture/units.lab. `load_release_curricula → prepare_runtime_bundle
→ compiler._rebuild → authoring._facts` refuses the record before API startup.
This isolates the first validation failure; further compatibility checks have not
been passed. No hosted data, validation guard or source interpretation was changed.
Summary: ignored `account-controls/hosted-fact-field-diagnosis.json`.

Fresh Git fetch and GitHub compare:origin/dev=c0d3e22,origin/frontend=60d285f,
local frontend=f989081 at review. `git merge-tree --write-tree origin/dev frontend`
exited0 with a resulting tree equal to frontend: no conflicts. Source has37 unique
commits and dev one (the backend merge commit);10 frontend commits are local only.
The branch comparison spans114 files,8429 insertions/850 deletions, not just the
latest logout fix. A clean merge is not full integration acceptance: startup blocker,
real authenticated curriculum/chat checks and inherited suite failures remain.
No merge/push performed. Restore compatible validation with focused regression
coverage and rerun the real flow before calling the integration operational.
