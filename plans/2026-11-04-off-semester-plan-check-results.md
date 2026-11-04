# Off-semester plan-check correction

Independent review of typed-plan chat found that an unsuffixed regular-term entry was always parsed as
`prescribed`. A course printed for first semester could therefore be scheduled in second semester and receive
`Works` without the offering-confirmation condition. Explicit `special class` suffix tests did not cover this.

## Correction

The shared checker reads the course's reviewed printed semester from its existing `course_facts` result.
For a regular-term placement marked `prescribed` or `retake`, a different semester adds the existing
`off_semester_request` unconfirmed condition. Existing host replies then state the request is unapproved and
include configured reviewed offering conditions. Prerequisite outcomes and load warnings are unchanged.
Moving to a later year in the same semester adds no new request. Explicit requests and summer retain their
existing conditions. The student's proposed modes and facts are not rewritten.

Changes: `backend/bintanong_planning/checker.py`, synthetic regressions in `tests/test_planning_check.py`.
No source-content decision, schema change, dependency, live model call, service operation or push.
This is bounded post-phase work; Phase 13 remains cancelled.

## Verification

Python 3.13, `-B -m pytest`, `-p no:cacheprovider`, external basetemp under workspace
`audit-evidence/codex-claude-20261104/`.

- RED: `tests/test_planning_check.py -k 'different_printed_semester or same_printed_semester'`:
  4 expected failures / 4 positive controls passed / 31 deselected.
- GREEN: `tests/test_planning_check.py tests/test_planning_chat.py tests/test_planning_recovery.py
  tests/test_generation_recovery_reply.py`: 105 passed in 254.56 seconds, exit 0.

Next: integrate this correction into the typed-plan chat branch, verify unsuffixed off-semester input through
that chat pipeline with configured offering conditions, then continue the coordinator's live gates.
