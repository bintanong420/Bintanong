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
- No dependency/lock/model changes, database writes or new benchmark runs.

## Next action and limits

Complete separate worktree move, production build and opt-in local evaluation
launcher/browser checks. Current3218 service still loads old PR20 code `0634d12c`;
do not claim the new page is loaded there. A comparison needs one reference plus
three serial model generations and occupies the shared slot. Historical conditionB
remains unrun. C in this controlled experiment is not the full production pipeline.
