# PR20 local staging

Owner7November requested merge or a local staging environment for manual testing.
Selected isolated loopback staging before merge. PR20 remains draft targeting `p12-dev`;
no mainline/evaluation merge, release activation, source edits or application database writes.

## Access and identity

- Preferred browser URL: **http://localhost:3218/chat**. This separates browser cookies
  from the usual `127.0.0.1:3217` development URL. `127.0.0.1:3218` also serves staging.
- API: `http://127.0.0.1:8023`; model: existing local container on18088.
- Serving worktree: `p12-pr20`, branch `feature/p12-unified-answer-pipeline`.
- Loaded commit: `c5f20a4ed8a1c5b6a27dc79c67bc6c168ad3e346`; frontend production Webpack
  build from `be8948a5` (no frontend source changes through loaded commit).
- `/health/staging` returns the startup identity and flags; `/health/ready` checks model/Janus.
- Existing reviewed cached research snapshot: `p12-research-faqsplit-20261030`,39 curricula.
  Same cache/package composition as prior dev launcher, including grade_completion5120 budget.
  No hosted-currentness probe or source acquisition; candidate/advisory restrictions remain.
- `compound_checks=True` **only in staging** for owner tests. Repository default stays OFF.
  Router compile ON matches the prior dev composition; no default change.
- Loopback-only guest research access, question rate window0 for local benchmarking.
  Origin/session/privacy boundaries and one-running-answer admission remain enforced.

## Launch and recovery evidence

Ignored directory: `audit-evidence/pr20-local-staging-20261107/` under the workspace root.
It contains `start-api.py`, `start-web.ps1`, `pids.json`, `runtime.json`, startup logs and smoke evidence.
Starts use existing Python3.13.5/Node24.21 environments and existing read-only model weights.
Docker Desktop was already running; started existing `bintanong-p09-cuda-latency`, no pull or reconfiguration.
CPU encoder loaded existing verified assets; no installs, downloads or dependency changes.
Recovery reload: API3240/server24116, web launcher4344. PIDs are evidence, not permanent identities;
verify command and port before stopping/restarting a staging process. Original3217 launcher,
evaluation worktree and mainline branches were not modified or started by this task.

To recover, from `p12-pr20` run the ignored `start-api.py` with the existing workspace venv,
and run `start-web.ps1` with PowerShell. Check model18088 first and start its existing container
only if stopped. Launch hidden, preserving unrelated processes. Both services use their own
staging logs. A bounded ignored model-only keepalive runs for4hours (20s checks, at most2
restarts,180s cooldown); stop via the ignored staging `stop-keepalive` sentinel. It does not
restart Docker Desktop or unrelated services. Model context remains8192.

## Executed checks

- Frontend `/chat`, API readiness, frontend `/api/health`, model `/health`: HTTP200.
- Frontend `/api/curricula`: HTTP200 with39 choices, including separately labelled old/proposed BSCS.
- `How to remove an INC?`, through frontend `/api/chat`: HTTP200, answered, four source cards,
  presentationV2, one mapped document part. Approved method/Dean conditions and known deadline
  conflict/source limits retained.26.98s outer frontend-proxy HTTP time, not browser latency.
- `I passed CC1/L. Can I take CC2/L? Can I take CS1/L?`, BSCS2018–2019:
  HTTP200, clarification_needed; **not a passing compound check**.19.41s proxy HTTP time.
- Bounded router-only trace reproduced `invalid_reference`: the model used occurrence1/2 for
  unique CC2/L and CS1/L quotes instead of zero. The host rejected the references; no false
  prerequisite verdict was emitted. Treat as an unresolved live-routing failure, not a source gap.
  Independent trace used existing cached resources, no second encoder; process exited afterward.

- [Recovery follow-up](2026-11-07-pr20-recovery-routing.md): owner confirmed oldBSCS;
  separate container outage and routing overflow diagnosed. v26 preserves source metadata,
  distinguishes recovery advice from an explicit proposed schedule, and keeps hypothetical failure.
  1,077 routing/recovery tests pass. Exact frontend request now answered in44.37s after staging
  API/frontend reload, with dependent subjects, recovery drafts and source/approval/load limits.
  Recovery draft preference/length/optimality remain concerns; this is not plan acceptance.

Automated inference stopped after the bounded checks; model slot is available for owner testing.
No actual browser viewport/interaction verification or independent72-case benchmark was performed.
Next: owner retest on3218; investigate the recorded compound-reference and recovery presentation/
preference concerns before acceptance. Staging availability is not institutional approval.
