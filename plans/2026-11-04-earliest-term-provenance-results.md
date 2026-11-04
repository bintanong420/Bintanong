# Earliest-term chain provenance correction

4 November 2026, `feat/plan-check-replies`, worktree `p12pc`.
Independent review found that `earliest_term` kept only the target course's final check
provenance, omitting the intermediate prerequisite passes that justified its simulated term.

The helper now accumulates de-duplicated rule IDs and full source spans for every course
accepted as a simulated pass, including contributing earlier terms, same-term co-requisite
partners and the target. It rejects a contributing rule from another release scope rather
than combining releases. Failed/unknown candidates removed before accepting a term do not
become successful-pass evidence. Earlier courses assumed already passed remain explicitly
assumptions; this change does not manufacture rule evidence for unstated real grades.
The result shape and its advisory/offerings/load-plan limits are unchanged.

Verification (synthetic curricula, including unfamiliar printed codes):
- RED: 2 failures show X and D1 rule IDs absent for the chain X -> D1 -> Z.
- GREEN: 10 passed / 34 deselected in 62.10 s (new provenance cases plus existing earliest
  and co-requisite cases). The region wrapper assigns each synthetic rule its own source
  locator so both intermediate rule IDs and distinct source spans must survive aggregation.
- Added scope-integrity cases: 2 passed / 2 deselected in 17.33 s; mixed rule releases refused.
- `git diff --check` passed. Existing Python 3.13 venv, pytest cache disabled, external basetemp.
  Raw log: workspace `audit-evidence/p12pc-log/provenance-green.log`; scope run in tool output.

No routing/live service, model, source corpus, policy, dependency, push or merge changes.
The main coordinator owns chat integration and current_progress. This is provenance repair,
not new evidence of live accuracy or a confirmed offering or academic standing.
