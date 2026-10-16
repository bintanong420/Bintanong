# Bintanong implementation ledger

## Current state

- Active phase: **05 — Retrieval**; candidate software delivered, formal exit blocked.
- [Master plan](master_implementation_plan_original_long.md) is unchanged.
- [Active plan](phase-05-retrieval-plan.md) · [Checkpoint](phase-05-checkpoint.md) ·
  [Blocked handoff](phase-05-handoff.md) · [Current progress](plan_current_progress/current_progress.md).
- Last completed implementation: V1 source observations, product `ee7567a`,
  documentary closure `9a0eea7`. Phase 06 is not authorized.
- Remaining gates: applicable source/release authorization, calibrated retrieval
  acceptance and actual authorized real-source runtime evaluation. See checkpoint.

## Resume order

1. Run `python .agents/skills/bintanong-phase-handoff/scripts/phase_state.py inspect --repo .`.
2. Read current progress and the active checkpoint; use the plan/handoff for scope.
3. Compare Git status/log with recorded commits; preserve unrelated owner changes.
4. On phase resume, consult relevant Context thesis pages and the routing PNG.
5. Follow the checkpoint's single next action. Read linked evidence only as needed.

## Phase ledger

Historical completion labels are retained. The
[Phase 1–2 claims audit](2026-10-12-phase12-progress-claims-audit.md) records unmet
real-source exits; ledger validity alone does not prove source readiness.

| Phase | Name | Recorded status | Plan | Checkpoint | Handoff |
| ---: | --- | --- | --- | --- | --- |
| 0 | Docker and compatibility | complete | [Plan](phase-00-docker-compatibility-plan.md) | [Checkpoint](phase-00-checkpoint.md) | [Handoff](phase-00-handoff.md) |
| 1 | Source governance and contracts | complete; source gates qualified above | [Plan](phase-01-source-governance-contracts-plan.md) | [Superseded](phase-01-checkpoint.md) | [Handoff](phase-01-handoff.md) |
| 2 | Document ingestion | historical complete; audit applies | [Plan](phase-02-document-ingestion-plan.md) | none | [Handoff](phase-02-handoff.md) |
| 3 | Embedding generation | complete | [Plan](phase-03-embedding-generation-plan.md) | [Superseded](phase-03-checkpoint.md) | [Handoff](phase-03-handoff.md) |
| 4 | Vector and relational storage | complete after security remediation | [Plan](phase-04-supabase-storage-plan.md) | [Superseded](phase-04-checkpoint.md) | [Handoff](phase-04-handoff.md) |
| 5 | Retrieval | blocked formal exit; candidate verified | [Plan](phase-05-retrieval-plan.md) | [Active](phase-05-checkpoint.md) | [Blocked](phase-05-handoff.md) |

## Read only when relevant

- Sources: [locations](dataset-locations.md), [undergraduate scope](undergraduate-scope-policy.md),
  [source gaps](source-gap-policy.md), [service tables](service-table-association-policy.md).
- Architecture: [curriculum/Symbolic direction](2026-10-16-curriculum-symbolic-routing-clarification.md).
- Retrieval: [selected profile](2026-10-16-document-development-profile.md),
  [bounded acceptance](2026-10-16-document-development-acceptance-contract.md),
  [remaining exits](2026-10-16-phase05-remaining-exit-packet.md).
- Latest delivery: [V1 report](2026-10-17-source-observation-report.md).
- Ingestion: [supporting index](ingestion/README.md), only for ingestion work.
- Benchmarks: [evaluation protocol](../evaluation/README.md).
- Settled owner decisions: `AGENTS.md`; consult its linked records for exact evidence.

## History and upkeep

Owner requested compact handoffs on 17 October 2026. These are current snapshots,
not activity logs. Replace stale state; keep durable evidence in dated reports.
The full pre-cleanup index/progress/checkpoint/handoff are preserved at commit
`81be71a`. Recover any one with `git show 81be71a:<repository-relative-path>`;
for example `git show 81be71a:plans/phase-05-checkpoint.md`.
Do not read the historical snapshots during routine resume or copy them back here.
