# Unreferenced routing operation repair

Resume baseline18a2eab; approved requirements remain the Phase11 plan, master3/13/14
and standing prompt/validation decision. This is a bounded bug fix, no product-scope
change. Expanded release stays inactive; verified fraud comparison/checker work remains closed.

Student capability: a document question must not fail solely because the router
emitted an operation that none of its own declared parts requested. Evidence path:
model interpretation -> reference/part consistency -> existing one-repair budget ->
normal routing validation -> reviewed retrieval -> unchanged generation safeguards.
Unresolved question: can the existing model repair recover this structural mismatch
without silent rerouting, widening authority or losing legitimate structured requests?

1. Synthetic regression in tests/test_routing_operation_coverage.py: a raw document
   part plus an orphan eligibility operation must be rejected as an invalid reference
   during normalization, rather than after the repair opportunity. Observe RED.
   A valid second model interpretation dispatches RAG; repeated invalid output
   stays unavailable after the same shared repair allowance. Preserve linked
   Symbolic/Hybrid operations, single-operation index correction and clarification controls.
2. Add a normalizer coverage check for substantive routes and a precise repair hint
   in router.py. The model must reinterpret the original request; do not remove
   operations, invent a course or route by topic keywords. Observe GREEN and run
   routing/orchestration/generation regressions.
3. One bounded replay of the saved raw interpretation through the current real router
   repair, then an inactive-package end-to-end fraud replay if useful. Stop after
   those observations; no prompt/model sweep or source activation. Record failures
   and latency boundaries. Tests use synthetic data; raw source evidence stays ignored.
4. Independent scoped review, focused fixes under TDD if needed, full tests/ suite,
   whitespace/phase checks, verified small commits, compact recovery/progress updates.

Affected files: backend/bintanong_routing/wire.py, router.py; focused synthetic test
file; routing README/current reports only. No dependencies/schema/pins/frontend changes.
Review focus: control/audience precedence; linked versus orphan operations; invalid
quote handling; shared three-call budget; original request/evidence-bound topics.
Shared Python3.13, pytest -q -p no:cacheprovider, external basetemp under workspace
audit-evidence/p11-operation-repair-20261025. No installed linter/formatter.
Context refreshed: thesis physical17-18/39-44 and runtime routing PNG; master3/11/13
and standing prompt decision. Unknown-versus-unmet follows the settled owner policy,
not the illustrative thesis closed-world example. No routing/scope discrepancy.

## Execution evidence

- RED6 failed/7 passed: late inconsistency rejection skipped the repair opportunity.
- First broad selection:1 failed/1007 passed. Existing wrong-RAG evaluation exposed
  an unintended change to refusal/reporting; retain that earlier RAG guard and apply
  the new check to Symbolic/Hybrid only. No assertions weakened. Final1008 passed.
- Ruling: explicit controls, non-undergraduate audience and semantic ambiguity
  retain their established precedence over this structural repair. This preserves
  held requests; cost if wrong is continued honest refusal, not inferred authority.
- Independent scoped review: no blockers;13 focused checks independently passed.
- Saved bad first packet injected once into current router -> real model repair
  selected RAG -> retrieval/unchanged generation/review answered with both fraud
  rows and unresolved-precedence notice (40.315s inner pipeline). Fresh same-question
  pipeline also answered safely (24.954s). No browser/API latency or broad accuracy
  claim; both model drafts still selected one sanction, and existing comparison
  assembly discarded that selection before review. Full suite/delivery pending.
