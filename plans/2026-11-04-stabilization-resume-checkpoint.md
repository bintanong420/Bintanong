# Architecture stabilization resume — 4 November 2026

Owner asked Codex to continue Claude session `b73f3662-df93-4755-8a11-22c52689e6e8` using the independent audit/plan.
Starting main HEAD `678c2a1d`; main has an inherited owner USG progress paragraph and `.playwright-mcp/`, preserved.
No active numbered implementation phase; the audit's phases are bounded work slices, not Phase 13 authorization.

## Inputs and scope

- [Independent audit](2026-11-04-independent-audit-memory-conversation.md), exact SHA-256
  `a6c37d9566193d90a87ed0c13a826f92e1cf0422f01eb83bed093bcdca1bf73d`.
- [Implementation plan](2026-11-04-architecture-stabilization-plan.md), exact SHA-256
  `5560fbe84e4b43d5c99c0b16c87cf0589ff5ca1549ded0ecb59eb52a1eea49aa`.
- Both match the owner's Downloads files byte-for-byte. Copied already at `ee014749`; do not duplicate.
- Read Claude main session's final turns and the last agent tool/results. User requested generic preferred Draft B;
  coordinator's just-in-time generalization is recorded at `678c2a1d` and remains revisable, not institutional policy.
- Consulted handoff skills, INDEX/progress, Phase 12 handoff, master routing/session architecture, undergraduate scope,
  owner ledger, thesis physical 17–18 and 39–44, and viewed runtime routing PNG. Advisory/source/privacy limits remain.

## Where Claude stopped

| Worktree / branch | Verified starting state | Current task |
|---|---|---|
| `p12ds` / `fix/dialogue-status-and-prereq-listing` | Recovered at `e40b2f92`, clean | Integrated `63681288`; real worker allowlist corrected separately at `8a470088` |
| `p12jit` / `feat/recovery-just-in-time` | Recovered `2bb42018` / `f06e2809`, clean | Integrated `9d260c8d` / `aeddd05c`; expanded gate + corrected selections recorded in its report |
| `p12rr` / `feat/recovery-routes-more` | `2696bb69` clean | Already ancestor of main; Claude audited 184 tests, do not redo completed implementation |
| `p12pv` / `feat/plan-view` | `b62d021e` clean | Already ancestor of main; no separate merge needed |

## Implementation decisions

- The inherited p12ds code mostly changes status while aliasing listing to eligibility. Audit requires a distinct
  requirement-description operation/result, with reviewed rule structure/provenance and no student decision outcome.
- Keep eligibility/personalized missing-prerequisite behavior separate; retain unresolved printed conditions.
- Dialogue-reference failures need a dialogue reason; never assert source absence merely because interpretation failed.
- No extra feature-specific pending states or exact-phrase repair patches. Generic in-memory ledger/context compiler
  is split at its commit boundary: bounded exchange store + atomic chat commit delivered `f5dff2ad`,
  [report](2026-11-04-ephemeral-dialogue-ledger.md). Context compiler/semantic acts remain pending.
  Durable history still needs privacy signoff. No whole-memory or conversation-repair completion claim.
- JIT preferred and faster alternative must both remain available; no course/program constants, no assumed offerings.
- Teammate complaints are tracked in [the checklist](2026-11-04-teammate-regression-checklist.md).
  What-if labels fixed `3b34a67e`; unsafe optional term dependency prose withheld `66c6422c`.
- Luna frontend `dd376036` / `79b13f51` slims both program-control states; `3e05c6b1` removes only
  the About-page scope/privacy link. TypeScript checks passed; browser render not verified.

## Verification and runtime

- Fresh phase inspector valid, no active numbered phase; dirty main preserved.
- Current serving API processes observed `76524` / `45316`, started 10:53:16; model/API not restarted by this resume.
  API does not publish serving commit/flag identity, so do not claim the serving process equals main HEAD.
- Baseline harness runs pinned current code, real cached reviewed BSIT ledger, model, chat path; OFF/ON C01–C03.
  Outputs under ignored workspace `audit-evidence/stabilization-20261104/`; no retrieval/HTTP/browser in this harness.
  Completed six turns on starting code: both modes C01 -> `list_missing_prerequisites`, unknown, clarification;
  C02 -> eligibility unknown/clarification; C03 -> eligibility eligible/answered. Confirms intent/contract defect
  independent of compiler flag. First observed turn 64.013 s; later turns 17.954–21.755 s, backend turn only,
  not student-visible browser latency and not a model/service cold-start measurement.
  Reviewed cached BSIT ledger bytes SHA-256 `2823930c645d6dd51e79da179ae2338fd558a8b02f202c7fa4852dfabac06f5a`;
  IT 14/L rule references IT 3/L, physical source page 1, source PDF hash
  `70f7893959244addd897e77a57ac69736c55c1f6262292faf6e278fb0df26ac5`. No ledger edits.
  C04 graduation source diagnosis needs a separate full documentary trace; no predetermined positive/negative answer.
- Integrated listing/status gate: 82 Python, 10 frontend transport tests + TypeScript passed.
  Atomic ledger/session/chat gate: 84 passed. Term generation: 25 passed.
  Worker/research/listing regression: 45 passed after live C02/C03 exposed its stale authorization allowlist.
- Fresh source-backed rerun at `8a470088`, compiler OFF/ON: all six C01–C03 intent/outcome checks passed.
  C01 answered/listing/no decision; C02 unknown/clarification; C03 eligible/answered.
  Times 8.191–12.164 s per backend turn; same harness exclusions apply. No browser/SLA/speedup claim.
  Ignored outputs `stabilization-20261104/post-worker.{json,log}` preserve the rows.
- [Graduation diagnosis](2026-11-04-graduation-source-diagnosis.md), integrated `7ca35188`, verifies
  page-64 application procedure is present but original endpoint clipped. Live documentary cause still unverified.
- Recovery expanded gate: 51 pass / 4 stale-expectation failures, corrected selections 4 pass;
  full plan-view file 10 pass after correcting canonical regular-rejoin ranking. Long gate not repeated.
- System Python 3.13 or existing 3.13 venv; pytest no cache/external basetemp, no installs/model/dependency changes.

## Next action

Implement the bounded server-side context compiler and semantic reference/repair handling against
the committed ledger. Test raw utterances, topic switches and cross-program conversations before any
backend restart. No push, deployment, durable transcript storage or new formal phase is authorized here.
