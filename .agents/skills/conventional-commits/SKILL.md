---
name: conventional-commits
description: Use before creating, amending or rewording any Git commit message, including documentation commits and local history cleanup.
---

# Clear Conventional Commits

Write every commit subject as `type(scope): summary`; scope is optional.
Use a lowercase type, a short scope when useful, and a plain-English imperative
summary naming the actual change. Aim for 72 characters or fewer, without a final
period. Match the staged diff; avoid vague subjects such as "update files".

Choose `feat` for new functionality, `fix` for a defect, `docs` for documentation,
`refactor` for unchanged behavior, `test` for tests, `perf` for performance,
`build` for build/dependency changes, `ci` for automation, `style` for formatting,
and `chore` for other maintenance. Add a body only when motivation or validation
helps. Use `!` or a `BREAKING CHANGE:` footer only for an actual breaking change.

Before committing, inspect the staged diff, run the applicable checks, and read
the final message. Keep unrelated changes in separate commits. Describe candidate
work accurately; do not imply source approval, release activation or deployment.

When rewording history, verify fresh remote refs and select only authorized
unpublished commits. Preserve dirty work, create a recovery ref before rewriting,
and verify file trees afterward. This skill grants no permission to push or rewrite
published history.

Examples:

- `docs(review): record confirmed undergraduate policy readings`
- `fix(ingestion): preserve action and duration associations`

Reference: [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/).
