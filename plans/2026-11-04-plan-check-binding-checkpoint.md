# Plan-check request/result binding defect: resume checkpoint

4 November 2026. Owner requested an immediate handoff before the session limit.
Worktree `p12pc`, branch `feat/plan-check-replies`, implementation at `77207f8d`.
Superseded by [binding correction and verification](2026-11-04-plan-check-binding-results.md).
The reproduction and original next action below remain as historical handoff evidence at `69f43e35`.

## Confirmed defect

Independent review found that `plan_check_lines` verifies only curriculum identity and term count.
A passing result for a different plan with the same curriculum and term count can therefore render
against a blocked plan as Works. Fresh synthetic reproduction on this worktree:

- Good: BASE in year 1 first semester, no stated results; result works.
- Bad: D1 in year 2 second semester, X stated failed; actual result blocked.
- `plan_check_lines(bad, check_plan(good, runtime, POLICY), 'en', shown)` printed
  `second year, second semester: course-syn106 — ✅ Works.`
- `check_plan(bad, runtime, POLICY).terms[0].outcome` printed `blocked`.

The reproduction used the existing `test_planning_check` synthetic fixtures and the pinned Python
3.13 venv. No live service, model, university source or stored student data was used.

## Exact next action

1. Add failing tests in `tests/test_planning_chat.py`: the reproduction above; same courses/terms
   but changed facts; changed course modes; changed term order. Renderer must reject all mismatches.
2. Add a canonical full-input binding to the shared `PlanCheckResult` contract. Recommended:
   required immutable `checked_request: PlanCheckRequest` and `request_sha256`, hashing canonical
   sorted JSON of the whole effective request plus policy identity. Bump result schema to v2;
   validate its digest, curriculum and term count. Do not infer the binding from course count.
3. Populate the binding in the sole production constructor, `checker.check_plan`, and enforce it
   in `plan_check_reply.plan_check_lines` before rendering any verdict. Policy warnings are taken
   from the checked result; any additional policy context included in the digest must be canonical.
4. Adapter nuance: `SymbolicAdapter.check_typed_plan` injects owning-session facts. The parsed
   request may have `facts=()` while the effective checked request has real session assertions.
   Caller must render the effective `result.checked_request`, rather than dropping facts from the
   digest or rendering against the original unbound input. Add a regression for this path.
5. Update synthetic integration-copy fixture in `test_integration_plan_field_is_pinned_to_the_same_release`:
   it changes result.curriculum_id and will also need its checked request and digest updated.
   Repository search found only one production `PlanCheckResult` constructor, in checker.py;
   other existing consumers read results without constructing them.
6. Run the focused suite first (existing venv, no installs):

```powershell
& C:/Coding-projects/bintanong_workspace/audit-evidence/p12-env-20261031/venv/Scripts/python.exe -m pytest tests/test_planning_chat.py -p no:cacheprovider --basetemp C:/Coding-projects/bintanong_workspace/audit-evidence/p12pc-binding-bt -q
```

Then run existing planning checker/recovery and affected generation/orchestration suites. No new
long run was started after the immediate-handoff request. Earlier 77207f8d test counts do not prove
this missing binding. Main coordinator owns current_progress.md and the central continuation log.
No routing edits, dependency changes, live calls, push or merge in this checkpoint turn.
