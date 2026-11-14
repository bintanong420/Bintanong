# Plan chat continuation checkpoint

Branch `feat/plan-chat`, worktree `p12-plan-chat`. Committed vertical slice `b324ec01`, conditions/context
review fixes `a7d9a789`; imported prerequisite evidence corrections as `18545200` and `51376df8`.
Coordinator cherry-picks only task commits, not imported duplicates. No active numbered phase.

Current dirty work: earliest-course-term operation through routing/orchestration/evidence/generation; source
proof for configured offering routes via already loaded package chunks. Earliest initial RED: 12 failed;
first implementation returned actual host answers for 8 cases (only expected term spelling differed) and
specific start-term questions for 4 cases. Latest combined plan/earliest test run is in
`audit-evidence/p12-earliest-route-green.log`; inspect final output before claiming completion.

Offering-route review finding: synthetic flag alone allowed invented source claims. Added exact pinned
chunk/version/hash/page + actual nonblank source-field text checks and reject unresolved source limits.
No model/retrieval call is added. ReleaseResources has optional source proof at the end of its fields to
preserve positional callers. Need finish negative boundary tests, final verification, and commit.

No live calls/services/GPU operations. Root owns restart/live comparisons. Another reviewer owns central
checker inference for unsuffixed off-semester placements in `p12pc`; do not duplicate that change.
Next: finish source-proof/earliest boundary tests, inspect final results, commit verified task increment,
send coordinator exact commit and limitations. Shared current progress is coordinator-owned.
