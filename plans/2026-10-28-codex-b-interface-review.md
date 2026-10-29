# Codex B shared-interface proposals: Claude review

28 October 2026. These are the proposals in Codex B's task record (`feat/p11-frontend-integration`,
`plans/2026-10-28-p11-frontend-integration-task.md`), reviewed under the
[workstream split](2026-10-28-phase11-model-workstream-split.md). This review approves the design so
Codex B can work on it. It does not merge anything. The owner can override it.

## 1. Additive `data-answer` metadata: approved, with conditions

`language`, `missingFields` and an optional canonical `clarification` may be added to the
`data-answer` stream part (`backend/bintanong_api/stream.py`). Conditions:

- Build them only from fields of the already validated `CandidateAnswer`, plus labels the host has
  already resolved: printed course codes and the program/curriculum scope. Do not reason anything new
  at the API layer, and do not change the `CandidateAnswer` or generation contracts.
- `language` is the answer's validated reply language (`en`/`taglish`). Never use the input-language guess.
- Student-facing values carry no predicate names, check-scope lines, release/edition hashes or `ev-`
  ids, the same as the student render profile. Map internal codes such as `completion_unknown:<code>`
  to a kind plus the printed course code.
- Keep unknown separate from unmet. A missing fact is never shown as a failed condition.
- Write a RED test first: golden stream bytes for answered, clarification and insufficient cases, plus
  the SDK parser consuming them.

## 2. Optional `account_id` binding in `sessions.py`: approved, with conditions

The goal is to stop a session cookie from being used across accounts. This is a security fix, so it
is worth taking. Codex B is the single implementer. Conditions:

- Keep it optional: unauthenticated/test mode behaves exactly as today. A session issued for
  account A refuses account B, in `resolve` and in every mutating method. The mismatch looks the same
  as an unknown session, so it reveals nothing about the other account. Expiry, deletion and
  `wipe` are unchanged.
- Write RED tests first, in a separate commit that touches only `sessions.py` and its tests, so I can
  review it on its own.
- The API must verify the bearer on the server side before the binding is used. Identity enforced only
  in the frontend is not enough. The bearer must not be logged or stored beyond its digest.
- No hosted Supabase auth configuration, writes or new secrets without an explicit owner instruction.

## Merge

When the lane is ready, I review the commit range, merge it into `feat/p11-backend-api`, and run the
full suite plus the API tests. If answer text could change, I also rerun the live battery. Unfinished
branches are not merged.
