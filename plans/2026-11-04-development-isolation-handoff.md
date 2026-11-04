# Development isolation during data gathering

Owner requested a separate worktree so development can continue while p12 serves actual data gathering.

- Gathering checkout: `C:/Coding-projects/bintanong_workspace/worktrees/Bintanong/p12`, branch
  `p12-evaluation-harness`, frozen by this session at `8f15cfe0` (same remote tip when inspected).
- Development checkout: `C:/Coding-projects/bintanong_workspace/worktrees/Bintanong/p12-dev`, branch
  `work/post-gathering-fixes`, based on `8f15cfe0`, with no remote upstream.
- Original checkout's dirty progress notes and `.playwright-mcp/` remain there, untouched.
- Worktree creation did not restart, reconfigure or probe any application/model service.
- Continue code changes only in p12-dev. Do not merge or push to the gathering branch during collection.
  Offline checks may run here; live model probes remain paused because both checkouts share the same GPU/service.
  A future development server must use separate ports/configuration and must not mutate shared data.
- Existing verification: reply/presentation gate 95 passed; multiline compiler gate 203 passed, including
  two synthetic cross-program regressions first observed RED. A source-backed live multiline rerun preserved
  the stated failed CC 4/L fact and answered ineligible. This supersedes the earlier incident note's open
  grade-extraction diagnosis; broader conversation/browser/device acceptance remains incomplete.
- Running gathering backend predates recent fixes; this Git base is not proof of serving version.
  Preserve the running setup during collection and record that distinction in collected results.

Next: continue the course-name/conversational presentation work and pending browser checks in this worktree,
using offline evidence while gathering is active. No numbered phase advancement or institutional approval.
