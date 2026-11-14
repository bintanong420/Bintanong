# Co-requisite links in the affected-course listing

23 October 2026. Owner direction after [BS Criminology review 01](2026-10-22-crim-prerequisite-review-01.md):
"we have to fix this" — "stuff like that are important to fix because after all we're looking for a
great achievement in high accuracy".

## Defect

`list_affected_courses` (Prolog `dependencies/4`) followed only `course` references, so a course
needing another as a co-requisite was never listed as affected. Real case: BS Criminology CDI 4 listed
nothing, although CDI 5 requires "CDI 4 (co-requisite)" and CDI 6..CDI 11 depend on CDI 5 in turn.
Phase 06 excluded co-requisites deliberately ("not prior completion"); the listing was therefore
incomplete for a student asking what a failed course affects.

## Change

- `backend/algorithms/curriculum_runtime.pl`: `requirement_reference/2` (renamed from
  `prior_reference/2`) also follows `co_requisite`; traversal stays transitive and visited-guarded.
  Reason: a co-requisite failed and not taken in the same term also blocks its dependent.
- The result's relation label changes from `potential_prior_completion_dependency` to
  `potential_prerequisite_or_corequisite_dependency` so it stays accurate (`runtime.py`).
- Unchanged: eligibility semantics (co-requisite = passed or enrolled the same term), cycle detection
  (mutual co-requisites are still not a prerequisite cycle), partial/complete coverage rules.
- Engine SHA256 changes; runtime bundles are rebuilt from ledgers, so no stored bundle is affected.
  Historical Phase 06 records citing the old engine digest stay unchanged as history.

## Verification

- TDD: `tests/test_symbolic_queries.py` new `test_corequisite_dependents_are_listed_directly_and_transitively`
  and the updated relation assertion failed first (empty listing; old label), then passed.
- Focused symbolic/generation/orchestration/routing set: 339 passed.
- Real Prolog: BS Criminology 12/12; CDI 4 -> CDI 5..CDI 11, Crim 1 -> Crim 2..Crim 8.
  BS Architecture 7/9 unchanged (no co-requisites; the 2 known conservative unknowns remain).
