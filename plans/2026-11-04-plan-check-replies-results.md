# Plan-check and earliest-term backend handoff (4 November 2026)

Branch `feat/plan-check-replies`, worktree `p12pc`, base `968ba2af`.
Resumed Claude task `agent-a5f3943d78a308ec3`; its worktree was clean before this continuation.
No active numbered phase. Phase 13 remains cancelled.

## Delivered entry points

- `bintanong_planning.chat.parse_plan_terms(text, catalog, curriculum, *, start_term=None, facts=())`
  returns `PlanCheckRequest`. Input is explicit `term: course, course mode; term: ...` text.
  Exact reviewed aliases are scoped to the curriculum; ambiguous/unresolved aliases, incomplete terms,
  duplicate courses, unsupported modes and terms out of order are rejected. No grade is inferred.
  An omitted year needs caller-supplied `start_term` or an earlier explicit term. No year rollover is guessed.
- `SymbolicAdapter.check_typed_plan(text_plan, context)` (async) takes a `PlanCheckRequest`,
  checks its curriculum against the owning `RequestContext`, and invokes the existing `check_plan`
  with the configured load policy. Owning-session facts are used; different supplied grades are rejected.
  `MultiCurriculumSymbolicAdapter` delegates to the requested curriculum's adapter.
- `bintanong_planning.chat.earliest_term(runtime, curriculum_id, course_id, facts, start_term)`
  returns frozen `EarliestTermResult`. `facts` is a sequence of `(course_id, state)` pairs;
  `start_term` is `(year, semester)`. It simulates regular prescribed semesters up to year five,
  using the existing reviewed Prolog checks and request-local assumed passes. Earlier courses are
  assumed passed only when no contrary state was stated; the answer discloses that assumption.
  A candidate co-requisite partner whose own rule is unknown/blocked is removed and all remaining
  candidates are rechecked. Unknown coverage/chains return unknown, never an invented date.
  Successful results retain the target check's rule IDs, source spans and release scope.
- `SymbolicAdapter.earliest_term(course_id, context, start_term)` (async) projects owning-session
  completion facts and invokes that helper; the multi-curriculum adapter delegates by context scope.
- Optional `IntegrationResult.plan_check` carries `PlanCheckResult` only beside ready evidence with
  matching curriculum, synthetic status, pinned release and source hashes. Absent values are excluded.
- `bintanong_generation.plan_check_reply.plan_check_lines(request, result, language, shown, *, routes=None)`
  and `earliest_term_lines(result, language, shown)` return host-written English/Taglish lines.
  `shown` maps IDs to reviewed printed labels. Supply the existing reviewed `RecoveryRoutes` for
  request conditions/source quotes; unavailable route clauses are explicitly unavailable.

## Reply behavior

- Term outcomes: Works; Works, needs confirmation / Works, may kailangan pang i-confirm;
  Works with a heads-up; Blocked; Unknown. D5 and summer warnings reuse the existing friendly
  wording, units, ceiling and Handbook page. They remain warnings rather than blocks.
- Missing co-requisites are called unmet course requirements, never falsely converted into
  a requirement to pass the partner first. Requests retain their conditions, source and
  the warning that dependent courses move later if the requested class does not open.
- Every plan closes with request-local assumed passes and the adviser / not-an-approval boundary.
- Earliest-term replies disclose prior-course and future-pass assumptions and state that
  offerings/approvals are unconfirmed; special-class and summer requests go to the adviser.

## Verification

Synthetic curricula include unfamiliar punctuated codes.
- Baseline planning checker/recovery: 48 passed (175.61 s).
- Wide requested family run: 1,210 passed, two inherited deprecation warnings (324.79 s), exit 0.
  This began with the first 20 chat-helper cases; later co-requisite/provenance corrections are
  covered by the final focused run below rather than claimed as part of this earlier wide observation.
- Final focused helper suite: 26 passed (47.29 s), exit 0; then two added positive/foreign-release
  integration-field cases passed (2.05 s), exit 0. Final production code is the same in both runs.
- `git diff --check` and `phase_state.py validate --repo .`: pass.

All pytest invocations used the pinned existing Python 3.13 venv:
`C:/Coding-projects/bintanong_workspace/audit-evidence/p12-env-20261031/venv/Scripts/python.exe`,
`-p no:cacheprovider`, and external basetemp under the workspace's ignored `audit-evidence`.
Wide selection: every `tests/test_(planning|generation|orchestration|api)*.py`; focused selection:
`tests/test_planning_chat.py`. Logs: `audit-evidence/p12pc-log/related.log`,
`focused-final3.log` (26 cases), plus recorded tool output for the two extra integration cases.
The coordinator owns current_progress.md and records this delivery in its central continuation log;
no competing current-progress edit is committed here.
RED observations: absent helper module; adapter missing (2 fail / 10 pass);
missing typed integration field (2 fail); incorrect prior-completion wording for a co-requisite
(2 fail); uncheckable co-requisite partner wrongly permitting an earliest term (2 fail);
missing earliest-term source provenance (2 fail). Each was followed by the relevant correction.
A negative-test fixture initially attempted an invalid `DecisionOutcome` copy; repaired the fixture
rather than weakening the decision contract. Initial shell log redirection referenced a missing
folder and did not launch pytest; the actual wide run uses the created ignored log directory.

Context consulted: AGENTS/handoff skills; INDEX/current progress; Phase 12 handoff;
master architecture section 3; recovery plan Steps 2-3 and 4 November owner decisions;
thesis physical pp. 17-18 and 39-44 plus runtime routing PNG. No scope discrepancy:
undergraduate advisory only; reviewed deterministic rules remain authoritative.

## Integration still required

No routing files were edited. The coordinator must wire typed plans and earliest-term intents
through the compiled router, provide explicit start-term/context facts and reviewed printed labels,
and connect these reply helpers to the host generation path. Merely attaching `plan_check` does
not cause the current generator to render it. No live-chat capability or latency is claimed here.
Earliest-term simulation assumes future passes and regular prescribed semesters; it does not
confirm offerings, a complete unit-load plan, a minimum-time schedule or academic standing.
The result lists its assumed passes, including other prescribed courses, rather than claiming
that every listed course is a direct prerequisite of the target.
No service/model/GPU calls, process changes, installs, dependency/lock changes, push or merge.
