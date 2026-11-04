# Recovery offering follow-up correction

4 November 2026. Branch `fix/recovery-term-followup`, isolated worktree
`p12-recovery-followup`, base `48416b20`. No active numbered phase.

## Failure and bounded correction

The compiled router answered a recovery question, then treated `paano kung summer?` as
an empty clarification. Its normal follow-up logic required a newly named course;
the existing recovery cue deliberately excludes `paano kung`, and a bare summer has
no year for `parse_term`. The previous validated dependency course was already stored.

A shared `recovery_follow_up(text, context)` now recognizes only a whole short offering
alternative (`paano kung summer?`, `what about summer?`, and equivalent short special-class /
off-semester alternatives). It requires a previous `list_affected_courses` question with
one course, matching program/curriculum, and no competing prior document subject.
The compiler uses that exact text as a grounded back-reference only when the model gave
no executable check or document topic and the previous course still belongs to the
reviewed curriculum. Existing registry and routing validation still authorize the check.
No new result/grade is created, and no program/course is hard-coded.

Orchestration uses the same helper to attach the existing recovery routes/drafts only
for compiled turns. The ordinary noncompiled path and broad `asks_recovery` vocabulary
are unchanged. Conversation context is supplied solely to that recovery decision;
it is not added to the symbolic fact scope.

A bare summer still does not establish a calendar year. The answer repeats the existing
recovery alternatives (including summer) and checked drafts with the existing explicit
failed-course/start-term assumptions. It does not invent a summer year, confirm an offering,
or claim that summer was selected as an approved plan. A focused summer-only draft is
outside this bounded clarification fix.

## Verification

- Compiler RED: 4 failed / 2 passed (English/Taglish, two curricula).
- Compiler GREEN: 6 passed / 71 deselected, then rechecked after additional curriculum-switch
  and prior-eligibility negatives: 6 passed / 71 deselected (1.34 s).
- Two-turn synthetic release/runtime test: dependency -> captured course context -> summer
  follow-up. RED: 2 failed (ready dependency result but no recovery attached). GREEN: 2 passed
  (18.68 s); both curricula, no new assumed fact and `term_stated=False`.
- Related compiler, recovery routing/replies, orchestration pipeline, API turns and private
  conversation suite: 170 passed in 34.71 s, exit 0. The last added negative assertions
  were rechecked in the six-case focused run above; production code was unchanged. Log in
  workspace ignored evidence:
  `audit-evidence/p12pc-log/recovery-followup-final3.log`.
- Negative checks: fresh session, no prior course, unknown course, curriculum switch,
  previous eligibility operation, selected unrelated documentary topic, longer summer fee /
  deadline questions, compiler disabled. These retain their previous paths.
- A new helper-test edit initially had an extra closing parenthesis; corrected before RED.
  Two attempted suite commands named nonexistent orchestration test files and ran no tests;
  the actual run uses the repository's `test_orchestration_pipeline.py`.

Existing pinned Python 3.13 venv, pytest cache disabled, external workspace basetemp.
No live/GPU/model/service calls, source changes, installs, dependency changes, push or merge.
The main coordinator maintains current_progress and performs live acceptance after integration.
Context reused: Bintanong handoff workflows, current INDEX/progress and Phase 12 handoff,
master architecture and thesis physical 17-18/39-44/routing diagram from this continuation.
Undergraduate advisory limits, unknown/unmet distinction and source gates remain intact.
