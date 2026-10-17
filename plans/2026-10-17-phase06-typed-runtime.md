# Phase 06 typed prerequisite runtime increment

Owner requests remaining Phase06 implementation in the existing worktree and
defers generated-output inspection: "Check them later. But I will review them."
This is not generated-output approval or permission for institutional execution.
Existing master11.3–11.5 supplies the runtime boundary; no frontend/later phases.

## Implementation ruling

Proceed with the explicitly requested implementation of the existing Phase06
scope, inline with TDD. Keep the real-source candidates inactive and reject them
at this research runtime boundary. Synthetic fixture execution may advance the
runtime software without inventing source authority, passing grades or release
approval. Do not block this independent work on the deferred human review.

First registered operation: `check_prerequisite_eligibility`, input names
`curriculum_id` and `course_id`, using existing PredicateRequest/CapabilityRegistry
and returning existing SymbolicResult. Other operations stay unsupported.
The initial capability family is prerequisite checking; additional proposed
operations are not permission to infer more policy families or deploy them.

## Files, behavior and limits

- Add `backend/bintanong_symbolic/runtime.py`: revalidate/detach authoring ledger
  through existing compiler, retain canonical immutable JSON, reject real sources,
  pass only typed scoped passed/failed/current-enrollment/explicit not_enrolled
  facts as request args.
- Add fixed `curriculum_runtime.pl`: one generic expression evaluator for reviewed
  all_of/any_of/course/co_requisite/verified_none, preserving unknown and draft
  coverage. No course-specific rules or global student assertions.
- Add `_janus_worker.py`: load only the tracked engine; fixed bound Janus goal,
  no caller-supplied Prolog or candidate file consulting. One process per request,
  serialized admission with timeout, hard process kill/wait, bounded input/output.
- Add synthetic tests; update symbolic README. Existing contracts/compiler,
  EMPTY_REGISTRY, dependencies, API, DB and real-source artifacts stay unchanged.

Passed/failed inputs are explicit synthetic completion states, not numeric grade
interpretation or repeated-attempt policy. Missing completion is unknown; a known
failure can establish an unmet required conjunct, while an unknown alternative
prevents a definitive any_of denial. Co-requisites accept explicit completion or
current enrollment; only explicit failed completion plus not_enrolled proves their
unmet condition. Missing enrollment is unknown; contradictions stay unknown unless
an independent alternative establishes the result. Draft identity
or unresolved target rule cannot become eligible. Version mismatch is unknown.

Request-local contradictory completion states produce unknown/conflict; there is
no mutable cross-request student state. Outputs carry rule/source provenance and
validated existing decision semantics. Result truncation/error/timeout never becomes
a policy denial or approval. Stable ordering gives deterministic explanations.

## TDD sequence and acceptance

1. RED: absent runtime API; test eligible, failed, missing, explicit none, unknown
   rule/draft identity/version, conflict, alternatives/co-requisites and unsupported.
2. GREEN: minimal immutable wrapper/fixed Prolog evaluator/Janus subprocess.
3. RED/GREEN adversarial checks: injected identifiers remain data, forged bundle
   rejection, immutable caller inputs, retry/isolation/concurrent requests,
   timeout/admission/output caps and worker operational failures.
4. Run actual Janus tests in system Python3.13, related compiler/contracts suites,
   documentation/phase checks and one independent final review. No installs.
5. Commit verified increment; update compact progress/checkpoint with RED/GREEN,
   exact commands and remaining phase gates. Do not declare full Phase06 complete.

Raw logs/TEMP/TMP/basetemp under ignored workspace
`audit-evidence/p06-typed-runtime-20261017/`. Synthetic tracked fixtures only.
Context rechecked: thesis physical17–18/39–44, runtime PNG, master3/11/13.
Undergraduate/read-only/private isolation and explicit unknown semantics stand.
