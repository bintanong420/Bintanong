# PR20 local staging

Owner7November requested merge or a local staging environment for manual testing.
Selected isolated loopback staging before merge. PR20 remains draft targeting `p12-dev`;
no mainline/evaluation merge, release activation, source edits or application database writes.

## Access and identity

- Preferred browser URL: **http://localhost:3218/chat**. This separates browser cookies
  from the usual `127.0.0.1:3217` development URL. `127.0.0.1:3218` also serves staging.
- API: `http://127.0.0.1:8023`; model: existing local container on18088.
- Serving worktree: `p12-pr20`, branch `feature/p12-unified-answer-pipeline`.
- Loaded commit: `a34c10c6c3aca8fc09a7ee2cc8b60b5d8893a994`; frontend production Webpack
  build includes `651ce26d` (native labelled recovery disclosures).
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
Latest reload: API4784/server4416, web launcher32664. PIDs are evidence, not permanent identities;
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

- [Recovery/routing implementation](2026-11-07-pr20-compound-recovery-implementation.md):
  owner-confirmed oldBSCS question now answers40.02s with earliest projected DraftC,
 458 visible words/1,642 full copy words. One primary draft and3 native disclosures;
 unknown checks/approval assumptions stay visible. No offering/feasibility guarantee.
- English/Taglish/Filipino compound now answer separately cited2 parts; English mixed Hybrid
  answers3 parts (17.52/15.64/16.45/24.08s respectively on651ce26d). These are spot checks.
-1,120 routing/API/compound regressions and90 recovery/plan-view checks pass; frontend106,
 TypeScript and production Webpack pass. Prior failures remain in dated audit evidence.

Automated inference stopped after bounded checks; model slot is available for owner testing.
No actual browser viewport/interaction verification or independent72-case benchmark performed.
Next: owner review of primary draft/disclosures, independent acceptance and paired compiler
language/latency/browser checks before merge. Staging availability is not institutional approval.
