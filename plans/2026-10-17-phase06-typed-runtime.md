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
and returning existing SymbolicResult. Other operations remain unsupported in
this first committed increment.
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

## First delivery and follow-on query operations

Product232727d:56 runtime acceptance cases and705 related tests passed50.00s.
Independent code review completed, including co-requisite enrollment unknowns,
nested unresolved provenance, complete response caps and oversized request refs.
Owner review of real generated mappings remains explicitly deferred.

Continue master11.2's remaining proposed operations within the same synthetic
boundary: `list_missing_prerequisites` returns the prerequisite SymbolicResult's
known unmet/unknown conditions (not a flattened new conjunction), and
`list_affected_courses` returns a separate typed dependency-inspection result.
Dependency inspection is a potential prior-completion graph query, not a claim
that every alternative is blocking or that a student is ineligible. Retain
partial/unknown coverage and source provenance; never call an incomplete empty
listing exhaustive. Scope completeness to the supplied bundle, not a curriculum
corpus. Co-requisites are not prior-completion edges. Use the same fixed worker,
immutable inputs, resource bounds and source/activation gates. Add RED tests for
these operations, then minimal GREEN, related checks and independent final review.

## Verified query delivery

Both follow-on operations now use the same bounded worker. The dependency result
is a separate synthetic-only contract with explicit supplied-bundle coverage,
source/version requirements and conservative completeness checks. Empty partial
results never become an exhaustive answer. Operational failures never become
empty success. Non-synthetic ledgers still reject before worker execution.

TDD evidence in the ignored raw root: initial30 missing-runtime failures; focused
adversarial/co-requisite/provenance/request-limit failures before their fixes;
queries-red.log has11 absent-operation failures; query-contract-red2.log has5
contract failures, query-extra-red.log has6 label/completeness failures. Final
queries-final-green.log:79 passed22.47s. Independent final run:79 passed20.87s,
no remaining actionable findings. Broader queries-related-final.log:728 passed
82.54s, exit0. These are synthetic software results, not source authority evidence.

Exact broader command (PowerShell, from p06; TEMP/TMP=`$raw/temp`):

```powershell
$raw='C:/Coding-projects/bintanong_workspace/audit-evidence/p06-typed-runtime-20261017'
$env:TEMP="$raw/temp"
$env:TMP="$raw/temp"
py -3.13 -B -m pytest -q -p no:cacheprovider tests/test_symbolic_queries.py tests/test_symbolic_runtime.py tests/test_symbolic_review_bundle.py tests/test_symbolic_compiler.py tests/test_symbolic_authoring.py tests/test_contracts_symbolic.py tests/test_contracts_runtime.py tests/test_contracts_runtime_fix2.py tests/test_contracts_fix3_runtime.py tests/test_contracts_adversarial.py tests/test_rule_candidates.py tests/test_prospectus_rule_handoff.py --basetemp="$raw/queries-related-final-temp"
```

Remaining Phase06 work: the deferred inspection of real generated output, governed
non-synthetic bundle/runtime integration and its authorized source-bound tests,
followed by applicable phase-exit verification and final handoff. A later review
answer alone does not automatically authorize execution or activation. No numeric
passing policy, exceptions or equivalencies are inferred from synthetic fixtures.
