# Fraud precedence correction

Resumed from `c1fc29a`; Phase 11 remains active. This bounded bug fix reuses the
approved source-gap requirements and source-review batches 4/7. No product scope
or source reading changes; the expanded release stays inactive. The checker trial
and verified malformed-source guard are closed and will not be repeated.

Student capability: explain the two overlapping admission-fraud rows without
choosing a sanction. Evidence path: retrieved reviewed fields -> per-part host
assembly -> bound ledger -> cited reply. This advances the expanded-candidate
quality gate only; it cannot close the full gate or authorize a switch.

1. Add synthetic regressions in `tests/test_generation_precedence.py`: an approving
   model selecting either row must yield both printed labels/penalty columns and
   an unresolved-precedence referral in en/fil/Taglish; preserve independent and
   canonical parts. Missing or incompatible counterpart must withhold that slot.
   Ordinary/resolved not-stated limits must retain existing behavior.
2. Observe RED, then implement the smallest per-part correction before numbering
   and review, following the existing host-claim pattern. Recognize only the
   recorded admission-fraud precedence limitation, not arbitrary missing claims.
   Copy retrieved values; never encode sanctions or infer blank-cell meaning.
3. Run focused generation/understanding regressions, review the increment, run
   the full suite with shared Python 3.13, no pytest cache and external basetemp.
   Reuse a bounded actual-model fraud replay against the inactive package if
   available; report host behavior separately from model quality and latency.
4. Commit verified increments with explicit staging; refresh checkpoint, progress
   and session recovery. No source/package/migration/pin/frontend/dependency changes.

Review focus: wrong-version siblings; missing/duplicate rows; uncited limitations;
malformed-source holds taking priority; claim budgets and reviewer/ledger binding.
Context refreshed: thesis physical 17–18 and routing PNG; master 3/13/14/16 and
Phase 10 handoff reviewed. No scope/routing discrepancy. Curriculum routing is
unchanged. No new phase research is needed for this existing Phase 11 correction.

Verification commands use workspace `audit-evidence/p11-fraud-precedence-20261025`.
No installed linter; use pytest, diff checks and phase-state validation.

## Execution evidence

- Initial RED: 11 behavior failures, 1 foreign-version fixture setup failure,
  3 passes. Fixture repaired; isolated pre-fix `to_draft` from c1fc29a confirms
  the cross-version regression fails for the unsafe answer (baseline-version-red.log).
  Working production files were never reverted. First focused GREEN15 passed.
- Edge RED2/15: newly added held counterpart bypassed its source hold; expanding
  an eight-part draft lost independent parts. Recheck final references against
  existing holds; reserve remaining claim budget, combine rows with both refs
  when they fit one claim, otherwise hold only the affected slot. GREEN508.
- Independent review found P2: marking comparison slots `host` bypassed per-part
  relevance confirmation. Corrected by retaining normal `answered` review status.
  RED7/11 (six review-coverage assertions plus the false-positive answer case).
  Test questions now request fictional sanctions, rather than an unrelated office.
- Ruling: retain ordinary model review for corrected comparisons. A checker may
  still incorrectly judge relevance/support, but cannot restore discarded model
  sanctions. Existing whole-draft fallback applies if that review rejects a part.
  Scope cost: this change does not improve semantic checker accuracy.
- Single saved live fraud replay: router chose Hybrid plus an irrelevant
  prerequisite operation; evidence_unavailable before retrieval, generation not
  reached. No retry or router fix; this does not validate the correction live.
  Expanded release remains inactive. Full suite PASSED6695 +1595 subtests,6 skipped,
  2 xfailed,6 warnings,22m44s,exit0; [delivery record](2026-10-25-fraud-precedence-results.md).
