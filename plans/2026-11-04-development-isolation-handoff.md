# Development isolation during data gathering

Current branch decision,7November2026: continue in the existing `p12-dev` worktree on
new branch `p12-dev`, based on published `039e80a2`. `p12-evaluation-harness` is reserved
for netorare's thesis system evaluation; do not automatically merge ongoing development
there. `p12-post-gathering-fixes` remains the earlier published checkpoint. The historical
creation and data-gathering evidence below is retained; no worktree relocation or server
restart was needed for this branch split.

Owner requested a separate worktree so development can continue while p12 serves actual data gathering.

- Gathering checkout: `C:/Coding-projects/bintanong_workspace/worktrees/Bintanong/p12`, branch
  `p12-evaluation-harness`, frozen by this session at `8f15cfe0` (same remote tip when inspected).
- Development checkout: `C:/Coding-projects/bintanong_workspace/worktrees/Bintanong/p12-dev`, branch
  `p12-post-gathering-fixes`, based on `8f15cfe0`, now tracks its same-named origin backup branch.
- Original checkout's dirty progress notes and `.playwright-mcp/` remain there, untouched.
- Worktree creation did not restart, reconfigure or probe any application/model service.
- Continue code changes only in p12-dev. Do not merge or push to the gathering branch during collection.
  Offline checks may run here; live probes require a free model window because both checkouts share the GPU/service.
  A future development server must use separate ports/configuration and must not mutate shared data.
- Existing verification: reply/presentation gate 95 passed; multiline compiler gate 203 passed, including
  two synthetic cross-program regressions first observed RED. A source-backed live multiline rerun preserved
  the stated failed CC 4/L fact and answered ineligible. This supersedes the earlier incident note's open
  grade-extraction diagnosis; broader conversation/browser/device acceptance remains incomplete.
- Running gathering backend predates recent fixes; this Git base is not proof of serving version.
  Preserve the running setup during collection and record that distinction in collected results.

Owner confirmed a free model window on 5 Nov; the isolated 3217/8022 candidate completed
[72 live PDF variants + three dependency turns](2026-11-05-live-language-browser-results.md).
Gathering 3216/8021 was not modified/restarted. Temporary candidate services can be stopped independently;
their ignored launcher is in the dated raw-evidence directory. Next: diagnose failures in this worktree and
coordinate any further live window. No numbered phase advancement or institutional approval.
