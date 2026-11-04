# Bind plan-check replies to the checked request

4 November 2026; `feat/plan-check-replies`, worktree `p12pc`.
Resumed from `69f43e35`; the earlier checkpoint preserves the confirmed reproduction.
No numbered phase is started. The coordinator owns current_progress and live integration.

## Correction

`PlanCheckResult` is now `bintanong-plan-check-result-v2` with required immutable
`checked_request`, `request_sha256`, and nullable `policy_sha256` fields. The binding hashes
canonical sorted UTF-8 JSON of the entire effective request (curriculum, all ordered terms,
courses/modes and stated facts), the policy ID, and the SHA-256 of the whole checked load
policy. A missing policy has null ID/hash. Policy content changes under an unchanged ID
therefore still change the binding. No dependency or persisted source is changed.

The checker is the single production result constructor and populates the binding. The
result contract validates its digest, curriculum, term count, sequential verdict indices
and policy/hash presence. Older v1 results are rejected rather than promoted without proof.
`plan_check_lines` verifies the supplied request against this binding before rendering.
The reported passing-BASE-result/blocked-D1-request reuse now raises `plan_result_mismatch`.

The adapter uses owning-session facts, so the effective checked request can differ from
the parsed plan's empty facts. Integration MUST render:

```python
result = await symbolic.check_typed_plan(parsed_plan, context)
lines = plan_check_lines(result.checked_request, result, language, shown, routes=routes)
```

Do not weaken the digest to exclude facts or render with a different request. The original
parsed request is intentionally refused when session facts were injected. The optional
integration field continues to enforce the existing release/source pin separately.

## Verification

- Original independent-review reproduction: RED 2 failures (one per synthetic curriculum).
- Same reproduction plus existing pinned integration fixture: GREEN 4 passed.
- Broader focused run: 127 passed in 285.57 s, exit 0: chat helpers, checker, recovery
  planner, recovery replies, orchestration integration. This run loaded the binding correction
  before the separate earliest-chain provenance correction; see its separate evidence.
- Regressions also cover changes to facts, mode, semester, term order, policy content,
  invalid schema version, canonical serialization round trip and adapter-injected facts.
- No live services/models, source-derived fixtures, process changes, dependency installs,
  push or merge. Tests use the existing pinned Python 3.13 venv, cache disabled and external
  basetemp. Raw execution log: workspace `audit-evidence/p12pc-log/binding-regressions.log`.

## Context and next action

Read the Bintanong handoff workflows, current Git/INDEX/progress, binding checkpoint,
Phase 12 handoff and the planning contract/checker/render callers. Scope and architecture
remain those consulted during this continuation: thesis physical 17-18 and 39-44 and the
runtime routing diagram; undergraduate advisory use, unknown/unmet and request-local
assumptions remain intact. Integrator must use the effective checked request above and
run its complete chat-path tests; no live-chat success follows from these backend tests.
