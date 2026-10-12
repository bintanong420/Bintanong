# Phase 05 retrieval report — 12 October 2026

**Software candidate; institutional retrieval exit gate pending.** No answer generation, source approval or release activation follows from these measurements.

The database-backed synthetic development run uses ten explicitly labeled cases: six positive exact-entity/scope retrievals, unavailable policy, unknown acronym, wrong program and outdated edition. Languages: English (4), Filipino (3), Taglish (3). Categories: enrollment (4), prerequisites (4), academic standing (1), grades (1). Discipline is not covered by this fixture.

Queries are assigned manual unit-vector axes; they are not encoded by SEA-LION. Real PostgreSQL pgvector/RLS/RPC rankings and the complete runtime engine are exercised in a disposable database. Source/version/span references resolve inside the synthetic database, whose filenames/hashes are synthetic; original-PDF resolvability and institutional correctness are not measured. The injected context counter counts characters to test budget mechanics; it is not reported as measured model-token accuracy.

Development calibration evaluates thresholds 0, 0.25, 0.5, 0.75 and 0.9. It maximizes equal-case positive recall/unsupported detection, then minimizes irrelevant evidence, with a conservative higher-threshold tie-break. Final-split tuning is rejected. The synthetic selected threshold is 0.9 for all k values; it is not installed as the runtime default.

| k | Mean Precision@k (`hits/k`, including unsupported cases) | Mean positive Recall@k | Unsupported detection (4 cases) |
| ---: | ---: | ---: | ---: |
| 3 | 0.200 | 1.000 | 1.000 |
| 5 | 0.120 | 1.000 | 1.000 |
| 8 | 0.075 | 1.000 | 1.000 |

Each positive case has only one gold chunk, so Precision@k uses the full k denominator while returning fewer chunks. This measures neither corpus accuracy nor an advantage of one k under realistic policy questions. Full per-language/category and threshold trial JSON stays outside Git in `C:/Coding-projects/bintanong_workspace/audit-evidence/p05-20261012/`.

The baseline synthetic run passed five database tests in 19.073s, including 30 complete engine invocations (10 cases × 3 k settings). Query/context/engine/CLI/metric tests have observed missing-module/function RED and passing GREEN evidence. Whole-phase regression and final fresh review results will be appended after execution.

Remaining exit evidence: compatible local real-model execution with matching fingerprints, independently approved development query/gold-source labels, source-file citation resolution and language/category retrieval failure analysis on those approved cases. All existing committed evaluation cases are synthetic; they must not be relabeled as verified. Shared/hosted migration deployment is pending review. Phase 06 may not start from this report.
