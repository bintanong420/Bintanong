# Service cutoff fidelity implementation plan

**Goal:** prevent a model/reviewer from completing a documented service-record
cutoff or blending its separate client/action/office fields into an invented link.
Baselinec197901. Existing Phase11 baseline, source-gap/service-association policies,
25Oct simple-question requirement and owner autonomous-work direction apply.
No product/source scope change. User opted out of routine implementation questions.

**Architecture:** before claim numbering/review, replace prose citing a service
record with an explicit unresolved agency_action/source_cutoff by one source-bound excerpt of that record's
visible fields and a clear cutoff notice. Quote original wording; do not translate,
complete, resolve or join the fields. Preserve independent claims. Reuse ordinary
part relevance/support review and existing claim/call limits. Repeat fidelity
validation at draft/final boundaries so model verdicts cannot waive it.

**Evidence:** saved6b47449 English service answer invents "for further action"
and blends offices despite all required citations and positive model review.
The source_limit explicitly binds agency_action/source_cutoff/unresolved; existing
fraud replacement establishes the pre-review transformation pattern. Source rows
lack an explicit reviewed sequence contract; no order inference from IDs/ranking.

**Stack:** existing Python/Pydantic generation modules, no new dependencies.
**Spec:** source-gap-policy.md, service-table-association-policy.md and the saved
service-routing-completeness-results.md. Existing requirements reused.

## Task and acceptance checks

1. Add synthetic regression cases in tests/test_generation_service_cutoff.py.
   Observe RED for invented continuation, false-positive reviewer, separate field
   labels, English/Filipino/Taglish, unaffected records, duplicate citations,
   missing/ambiguous fields, overlong record and independent-part claim budget.
2. Add generation/service_cutoff.py: read only source-bound JSON record fields and
   explicit unresolved cutoff metadata; malformed/oversized affected records yield
   source_gap, never partial silent truncation. No question-keyword classification.
   Exact source quotations have local-language framing; language quality remains
   a separate human/model acceptance concern, not proved by a function-word floor.
3. Apply in part_answers.to_draft before numbering and normal review, keeping the
   existing malformed-condition hold and fraud comparison. Preserve independent
   claims and their budgets. Add draft/final fidelity checks; legacy profiles may
   use existing repair/withhold flow when they cannot provide safe excerpts.
4. GREEN focused/broad generation, understanding, orchestration/runtime regressions;
   scoped independent review; commit small verified increment. No live sweep.
   Use the actual sealed record in an ignored component check for length/binding
   and produce concrete review examples, without a new LLM completion.
5. One full tests/ suite on frozen code, external basetemp/no cache; diff/links/phase
   checks and compact current-state recovery. Keep expanded80 draft/inactive;
   source/package/embedding/DB/model/output-budget/frontend unchanged.

## Review focus and boundary

Quotes must be exact and tied to one record; blank fields are not "none"; no
cross-version blending. Unknown field names/duplicate fields/mismatched limitation
names must not release prose. Source quotation is data, never executable advice.
Normal review cannot restore discarded prose. Missing evidence/over-budget output
withholds only the affected slot, retaining independent parts where possible.
No claim of full service quality, resolved order, Taglish runtime recovery or SLA.
After verification, hand off before more model experiments; flag any actual new
source judgment with exact evidence, reusing settled readings and unavailable text.

## Execution

RED12 failed/3 passed, then GREEN15. Added malformed field-name and independent
budget cases: edge RED1 failed/16 passed (unhashable dict), corrected by scalar-name
validation. Broad739 passed23.87s; independent review no blockers/27 passed1.12s.
Actual sealed Step3 component: en466/fil477/Taglish474 characters, exact visible
fields, no invented continuation, five retained claims. No model/review call; not
a live quality pass. All54 sealed source files unchanged. Full suite follows the
frozen code commit. Raw evidence: workspace/audit-evidence/p11-service-cutoff-20261025.
