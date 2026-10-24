# Topic-filtered retrieval continuation

Approved design: owner ledger item g and Phase 11 checkpoint, handed off at `f1eafe9`.
Student capability: recover reviewed evidence for a model-selected topic, including simple passing-grade
questions. Keep cosine ranking, threshold, source binding, scope, active-release RLS and required neighbors.
No dependency changes, new source readings, release activation or UI work in this change.

1. Observe baseline; add SQL filter/validation regressions, package parity, and a real engine/package test
   with three higher-scoring unrelated chunks. Observe expected RED before implementation.
2. Create migration through installed CLI: optional `p_chunk_ids jsonb default '[]'`, same limits as version
   ids; filter eligible chunks, replace old RPC signature, restore explicit grants and reload schema cache.
   Make the disposable DB adapter distinguish this JSONB argument from release-creation text arrays.
3. Have the bound evidence policy expose its subject chunk ids to the engine before ranking; apply the
   same filter in PackageStorage. HostedReleaseStorage already preserves optional arguments.
4. GREEN: focused storage/retrieval/runtime suite, actual disposable Postgres, meaningful mutations;
   then hosted migration and read-back/advisors. Commit small verified units with explicit staging.
5. Live grade/fee risk cases, roster19 vs18, then full suite and review. Report route/language failures
   separately from retrieval results. Prepare g2 route choice and exact review batch before asking.

Verification: shared Python 3.13 venv, `PYTHONUTF8=1`, pytest `-B -q -p no:cacheprovider`, ignored external
basetemp/evidence under workspace `audit-evidence/p11-topic-filter-20261024/`; no installs.
Full project `tests/` suite required before completion. Existing project has no installed linter.

Ruling: reuse the already approved plan/PRD baseline and its exact filter design; no new PRD or renewed
approval. Use the active checkpoint plus this report as execution ledger (existing non-task-numbered plan).

Current official docs: [Supabase schema cache reload](https://supabase.com/docs/guides/troubleshooting/refresh-postgrest-schema)
via Context7 confirms `NOTIFY pgrst, 'reload schema'`. [Changelog](https://supabase.com/changelog.md) fetched
through PowerShell after browser content-type refusal; no relevant RPC breaking change identified. No package/API
upgrade proposed. Installed CLI 2.117.0 `migration new --help` consulted; no upgrade/download.

## Execution evidence

- Baseline: 48 passed, 31 subtests. Expected RED: missing RPC overload/filter, package accepting invalid
  lists, and real engine/package crowding regression (20 failures including subtests; `red.log`).
- First GREEN: 68 passed, 63 subtests. One test-adapter scalar JSON encoding correction preceded GREEN.
- Independent review: no new security/backward-compatibility defect; whitespace-only ids differed across
  SQL/package. Added tab/newline RED, corrected new JSONB field validation only, preserved old filters.
  Review also prompted real DB five-chunk crowding/dependency coverage and a same-version package fixture.
- Final retrieval/runtime selection: 157 passed, 86 subtests (`review-green.log`, 53.84 s).
- Four isolated mutations caught: engine omits filter, package omits filter, package omits validation,
  SQL omits eligible predicate. Production files never altered by mutation runner (`mutations.py`).
- Hosted baseline security: only owner-accepted leaked-password warning. Performance: one pre-existing
  unindexed curriculum-link foreign key and 19 unused-index INFO notices; no index changes in this work.
- Review finding fixed, no deferred review items. Full suite and hosted/live verification remain pending.
