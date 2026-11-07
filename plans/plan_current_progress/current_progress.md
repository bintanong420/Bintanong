# Current progress

Updated7November2026. Active follow-up: `p12-evaluation-ablation`, branch
`feature/p12-evaluation-ablation`. No numbered phase started or advanced.
Last full snapshot before condensation: `c0a1a921` (`git show` recovers it).

## Current candidate

[Protocol/plan](../2026-11-07-ablation-test-page-plan.md) and
[checkpoint](../2026-11-07-evaluation-ablation-checkpoint.md).
- Parent PR20 remains separate: original checkout `p12-pr20` restored to
  `df802638`, published PR20 `73d5d16e`; no evaluation code published onto that branch.
- Fresh remote `origin/p12-evaluation-harness` was `69fc7cea`. Six evaluation commits
  imported selectively with provenance. Thesis checkout kept untouched.
- `c0a1a921`: controlled comparison alongside the original benchmark page.
  One reference run, then A(no evidence), B(fixed source cards), C(same cards plus
  checked symbolic report), common prompt/profile. Reference prose/gold not supplied.
- `b796b27b`: research-log privacy disclosure and separate acknowledgment, clear
  unknown model-setting status; regression covers failed-condition display/export.
- Comparison outputs are unvalidated and separate from scored reference runs.
  Fixed-order single runs do not prove accuracy, causation or statistical significance.

## Verification

-113 focused backend tests,125 frontend tests, TypeScript/production Webpack pass.
  Seven synthetic API browser tests cover gating,72 cases, human marks/reload,
  failed runs, comparison failure/export, privacy notice and phone-width overflow.
- One actual A01-EN browser comparison: reference answered, A/B/C completed,
  matching recorded model settings, exact JSON download,1440/390px without overflow.
  Workflow37.964s includes preparation, model calls and browser checks/download;
  not warm-pipeline latency. Per-condition wall times include HTTP/preflight/queue/
  inference and exclude shared preparation. Completed is not a correctness pass.
- Ignored evidence: workspace `audit-evidence/p12-ablation-staging-20261107/`.

## Runtime and boundaries

Research page: http://localhost:3219/dev/evaluation; API8024, existing model18088.
API loads `c0a1a921`; frontend built from `b796b27b` content.39 cached reviewed curricula.
Passcode in ignored `evaluation-passcode.txt`; no token in Git, URL or logs.
Local JSONL research records; no private uploads, corpus/database writes or activation.
No dependency/model downloads. Existing dependencies reused via junction; known
external-module standalone tracing warnings remain. PR20 staging3218 stays ready.

## Next action

[Validity/metrics audit](../2026-11-07-ablation-validity-and-metrics-audit.md): existing page is
exploratory, not a thesis-ready ablation.42 exported references are empty; Q11 provenance
needs reconciliation. Success-conditioned context/case selection must be replaced before scoring.
Next: freeze independent cases/context/gold and explicit executors, then shared metric export/
adapters and blinded calibration. C is not production; historical RAG-only suite remains unrun.
No new model/judge calls, installs, source decisions or formal experiment performed by this audit.
