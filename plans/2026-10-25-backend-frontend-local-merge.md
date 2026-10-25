# Local backend to frontend merge,25October2026

Owner requested merging the synchronized backend branch into local frontend.
This is a development integration; no remote push or release activation.

Verified merge commit `6a8931b20ee4d9862dfddbd0b554732ae2eb1b2b`, with the two input parents below.
Documentation receipt follows the tested product; local frontend receives both.

## Inputs and recovery

Frontend parent1525dc6a77570543a95acbfe4704ce6ee4936c47.
Backend parent357aa80710a944108a748ffb7206cd78f27286c7.
Recovery ref recovery/frontend-before-backend-merge-20261025 retains frontend parent.
Isolated worktree p11-frontend-dev-sync, branch integration/p11-backend-to-frontend-20261025.
Main owner dirty files copied with hashes and binary patch under ignored workspace
`audit-evidence/p11-20261025/backend-to-frontend-merge/` before any integration.
Other worktrees, model assets, local environment and lifecycle WIP remain separate.

## Conflict resolution

- Runtime catalog: retain backend's unique normalized printed titles and code-collision
  guard, preserving scoped aliases and repeated-course clarification.
- Authoring: retain backend's explicit numeric-unit set, text units.printed and units.rle.
- Catalog test hunk: retain readable assertion formatting and both branches' regressions.
  The older frontend shared-title test expected missing_facts=(); observed RED1/122PASS
  focused and RED1/3654PASS broad. The current course-facts plan explicitly requires
  duplicate titles to ask for a printed code: align to missing_facts=(course_id,) and
  retain clarification/no predicate execution. No upstream routing behavior is changed.
  Its inherited "could not find" wording for shared titles remains a disclosed UX limit.
- Index/checkpoint/progress: reconcile frontend delivery with newer backend source/quality
  status; Phase11 remains active. Backend handoff remains preserved as historical evidence.
- Existing UI/auth/admission/session/stream/readiness changes remain intact. No frontend,
  dependency manifest or lockfile changes introduced by this merge.

## Verification

Fresh merged candidate:

- Backend136 modules:3655 passed,2 expected photo xfails,179 subtests,142.71s.
- Disposable local databases:34 passed/86 subtests,168.54s. Retrieval filter/order,
  roles/privileges, supplementary append/immutability/rollback; shared/hosted data untouched.
- Frontend:55 tests; Next typegen and TypeScript PASS. Existing Node24/modules reused.
- Independent static review: no additional important integration defect. Synthetic
  course_facts/list_term_courses -> student text/SSE checks pass in all three languages.
- Phase-state validation and diff whitespace checks PASS; Phase11 cannot advance.

Commands/outputs are in the ignored evidence directory: backend-command.json,
backend.log, backend-red.log, database-command.json, database.log, frontend-results.json,
ui.log/typegen.log/typescript.log, independent-review.md. Python3.13, no pytest cache,
external basetemp; database tests create/drop guarded unique disposable databases.
No full-suite, actual-model or authenticated browser acceptance claim.

## Boundaries

Expanded80-chunk draft remains inactive. Existing19-chunk research release stays active;
no hosted migration, source writes, runtime pin switch or model experiment is performed.
Backend's failed live nine-case expanded-source gate and existing coverage/quality/
language/latency/browser acceptance limits remain; this merge does not close Phase11.
