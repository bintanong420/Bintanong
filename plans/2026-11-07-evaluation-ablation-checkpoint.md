# Evaluation page and ablation checkpoint

Separate branch `feature/p12-evaluation-ablation`, worktree `p12-evaluation-ablation`.
Base `df802638`; PR20 feature branch must remain at that pre-import head locally.
Published PR20 remains `73d5d16e`; no published history rewritten. No numbered phase.
Thesis evaluation worktree has owner changes and was inspected read-only.

## Delivered and verified

- [Plan/protocol](2026-11-07-ablation-test-page-plan.md); six remote evaluation commits
  imported with original provenance, not a whole-branch merge. Local baseline ref
  was stale; fresh remote evaluation head was `69fc7cea`.
- Existing72-case benchmark UI, gated API, source observations and scoring retained.
- Controlled experimental comparison A/B/C uses frozen actual evidence and optional
  checked symbolic report; common prompt/profile; no answer-key or reference-prose leak.
- Matching model metadata checked; outcomes/failures/export remain separate from
  validated student answers and original benchmark scoring.
-113 focused backend tests,125 frontend tests, TypeScript pass. Imported initial
  gate97 passes; overlapping counts must not be summed. RED demonstrated absent
  comparison module/API and blocked proxy paths before implementation.
- Production Webpack build passes; known external node_modules tracing warnings.
- `b796b27b`: research-specific privacy disclosure/acknowledgment and setting-unknown copy.
  Seven synthetic API browser checks pass, including persisted marks, failures/export,
  research notice after ordinary-site acknowledgment, and narrow layout.
- Actual A01-EN through browser: reference answered,3 completed experimental conditions,
  matched recorded model settings, JSON download identical,1440/390px no overflow.
  Workflow37.964s includes preparation/model/browser checks, not warm pipeline latency.
- No dependency/lock/model changes or institutional database writes. One developer smoke
  case ran; no full or independently scored benchmark.

## Next action and limits

Page http://localhost:3219/dev/evaluation, API8024; correct branch/startup identity.
API code `c0a1a921`, frontend `b796b27b` content; local passcode in ignored workspace
`audit-evidence/p12-ablation-staging-20261107/evaluation-passcode.txt`. Empty answer-key
configuration means human judgment only. Runtime evidence/browser artifacts and local
JSONL records are in that folder. PR20 staging3218 remains `0634d12c` and healthy.
Next: owner review and explicit protocol/evidence freeze before formal scoring.
A comparison occupies the shared model slot. Historical end-to-end RAG-only conditionB
suite remains unrun. C here is controlled generation, not the full production pipeline;
source cards may be fragments and raw model output may conflict with the checked result.
Use human scoring; transport completion does not establish correctness.
