## Standards

Reviewed committed `git diff 5c34fd73adbd2806d6c48362eb248b74921fb79c...cf8b11c566d76bd5048a761a169907aee31a242b` and the accompanying commit list. Sources: user-provided AGENTS.md, extractor-reviewer.md, code-quality-reviewer-prompt.md, code-review/SKILL.md, the GUI plan and package-split cross-phase rules. Repo-specific choices override Fowler heuristics; tooling-enforced checks are excluded.

### Confirmed documented-standard breach

**Medium — transport failure silently abandons Save.** `backend/bintanong_tools/prospectus_review_gui/static/review.js:32` awaits `fetch` without handling rejection; `:279` awaits that helper without a catch. The HTTP-error branch never executes when the request itself fails. A stopped server or interrupted connection therefore produces an unhandled promise rejection and no visible save error. `writeCorrected` at `:316` has the same shared-helper failure.

**Standard:** supplied AGENTS.md §6, “Handle errors intentionally” and “Avoid silent failures”; §13, important state must be visible and error messages must communicate what the user can do next.

**Reproducer:** open a question, choose Yes, stop the local server, then Save. Source-level executable verification used Node's stdlib VM to run the actual `api` and `submit` functions with `fetch` rejecting `TypeError('Failed to fetch')`. Output: `{"rejected":"Failed to fetch","visibleAnswerError":"","visibleStatus":""}`; exit 0. This was a narrow mocked transport probe, not a browser test. Handle rejection centrally and display an actionable connection/save-status message; do not claim a failed response proves the server never committed.

### Fowler heuristics

NONE warrant a finding. The sibling GUI package, shared row-entry builder, OS ledger lock and native static page follow documented choices. No speculative abstraction or unrelated rewrite identified.

### Separate suspicion

`session.py:187-190` materialises without the session write guard, while the HTTP route runs in the worker pool. Concurrent materialisations or a materialisation during an append deserve a targeted integrity probe. No corruption was reproduced; this is not a confirmed finding.

Owner-run gates a–g are green as supplied; they were not rerun. Browser/Lighthouse/human-trial evidence remains NOT RUN. Usage percentage: UNVERIFIED.

CHANGES NEEDED — 1 confirmed Standards finding; worst severity Medium.
