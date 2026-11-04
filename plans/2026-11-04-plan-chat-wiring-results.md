# Typed plan chat wiring (4 November 2026)

Worktree `p12-plan-chat`, branch `feat/plan-chat`, base `2fa8ffad`. Imported the prerequisite binding correction
`1909112b` as `18545200`; coordinator must integrate that correction once, then cherry-pick the chat commit only.
The import retained the incoming binding-checkpoint document in its modify/delete conflict.

## Delivered vertical slice

The existing LLM router can select `check_study_plan` with a term-kind target quoting the entire proposed plan,
excluding the introductory "Check my plan:". The host parses only explicit colon-separated term lines and exact
reviewed course aliases, e.g. `2nd year 2nd sem: X special class; summer: Y`, with comma-separated courses.
There is no regex intent shortcut and no second model call to invent a plan. Planned courses never become
asserted grades; owning-session facts enter the existing adapter/checker and bind its `checked_request` digest.

The route binds `curriculum_id` plus SHA256 of the quoted plan to the registered operation. Both compiled and
existing routing paths preserve the operation. Missing year, missing term lines, unrecognized course/mode and
reversed term order produce specific questions. Audience, scope, conflicting facts and release gates still run.

Orchestration parses and checks the plan through `SymbolicAdapter.check_typed_plan`; it verifies the returned
effective request equals the parsed request including session facts. A result for a different valid plan is
refused. The checked result becomes a proper evidence component; its synthetic/research mode, scope and source
hashes are pinned. The legacy IntegrationResult plan sidecar must equal the evidence component. Preparation
reassembles the evidence policy; the host answer carries the typed result and citations. The model does not write
or judge term verdicts. The ledger identity includes the full checked plan, request and policy binding.

Generation uses `plan_check_lines(result.checked_request, result, ...)`, preserving requests for classes as
unconfirmed, load warnings, unknown prerequisites, assumed future passes and adviser referral. It never renders
the pre-adapter request with missing facts. Printed rule spans are source cards and reach the student citations.
Without optional offering-route clauses, the existing renderer explicitly says those conditions are unavailable.

## Verification

Existing workspace Python 3.13.5 / pytest 9.1.1; no installs. Every run used `-B -m pytest`, `-q`,
`-p no:cacheprovider` and external basetemp under workspace `audit-evidence`.

- Initial fixture corrections: strict tuple parsing and pinned catalog source references. After fixing the
  fixture, existing code refused both synthetic typed-plan examples (RED: 2 failed; `p12-plan-chat-red4.log`).
- Sidecar mismatch regression RED: 2 failed (missing sidecar was formerly accepted).
- Full typed-plan vertical slice: **44 passed**, compile OFF/ON, two unfamiliar synthetic curricula, English
  and Taglish response-style paths, actual synthetic Prolog, missing year/terms/code, invalid mode/order,
  excluded audience, pinned sidecar, valid result for another plan, host-only rendering and citations
  (`p12-plan-chat-final.log`).
- Focused plan/chat/compiler suites: **153 passed** (`p12-plan-chat-focused2.log`, before the final four
  wrong-plan cases were added).
- Broad routing/generation/orchestration/planning run exposed a local `hashlib` import shadowing existing
  statement validation and older tests constructing an orphan plan sidecar: **1,751 passed / 64 failed**.
  Moved to the existing module import and updated sidecar tests to proper checked-plan evidence. Every one of
  those **64 failed node ids passed** on the correction (`p12-plan-chat-regression-failures.log`). This is not
  claimed as one uninterrupted fresh broad-suite pass.

All raw logs stay ignored under `C:/Coding-projects/bintanong_workspace/audit-evidence/`.
Context: handoff skills, phase index/progress and completed Phase 12 handoff; master structured architecture,
owner recovery/wording decisions and undergraduate policy; thesis physical 17–18 and 39–44 and routing PNG
consulted during this continuation. No new numbered phase; the coordinator maintains shared current progress.

Next: coordinator reviews/integrates this vertical slice after the old-prompt compiler comparison, then performs
live typed-plan smoke tests. Earliest-term chat selection remains separate follow-up work. No GPU/model/backend/
GUI calls, service changes, push, release activation or merge were performed in this task.
