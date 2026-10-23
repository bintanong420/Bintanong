# Partial prerequisite rules decide from their reviewed parts

23 October 2026. Owner approved ("alright let's proceed") the recommendation: when every part of a
rule is required (all_of), one clearly failed course gives "not eligible" and the unknown part is still
named; a rule needing one of several (any_of) is eligible when a known alternative is passed;
otherwise unknown. Motivation: accuracy (the owner's stated priority), BS Architecture
[review 01](2026-10-22-bsa-prerequisite-review-01.md) Ar-RM 2, Ar-CC 2, SP-3, BM/AA-2.

## Defect

`prepare_runtime_bundle` replaced a reviewed course's whole rule with `{'kind':'unresolved'}` when any
part was unresolved (Phase 06 design), so a known failure was reported as unknown. Real case:
BS Architecture BM/AA-2 printed "PLN-2, PP-4" (PP-4 a source gap); a student who failed PLN-2 got
"unknown" instead of "not eligible".

## Change

- `bundle.py`: a reviewed course's rule is exported with each unresolved part as an unknown leaf
  (no reason text). Fully unresolved and draft rules export exactly as before.
- `curriculum_runtime.pl`: eligibility logic unchanged (combine already gives all_of + known failure
  -> ineligible; any_of + satisfied alternative -> eligible; else unknown). Dependency listings mark
  `rule_unresolved:<course>` for an unresolved part anywhere in a rule (`contains_unresolved/1`), so
  they stay partial; known edges through such rules are now listed.
- `runtime.py`: rule state `resolved` when the outcome is decided by reviewed parts
  (eligible/ineligible), `unresolved_reference` when still unknown. Compiler coverage keeps such
  rules `direct_rule: unresolved`; the review export and cycle check are unchanged (cycle detection
  still considers fully reviewed rules only; dependency traversal is visited-guarded).

## Verification

- TDD: 4 new tests failed first (ineligible, any_of eligible, bundle export, dependency listing),
  2 stay-unknown cases already passed; old test pinning whole-rule withholding replaced.
- Focused symbolic/orchestration/generation/runtime/routing set: 819 passed.
- Real Prolog: BS Architecture 9/9 (was 7/9: BM/AA-2 with PLN-2 failed and Ar-CC 2 with Ar-CC 1
  failed now ineligible); BS Criminology 12/12.
