# Supplementary review of published sources

Approved scope: Phase 11 checkpoint g2 and owner choice recorded in the owner-decisions ledger.
Spec: source-gap/scope/service-association policies, existing C1 and selected-release contracts, and
[actual source decisions](2026-10-24-partial-topics-source-review.md). Execution uses inline TDD.
No new phase, authority claim, PDF version, dependency, model, UI, or executable disciplinary rules.

## Goal and acceptance

Undergraduates can ask about the newly reviewed disciplinary rows and complete pre-enrollment service
and receive cited documentary answers, including all applicable original gaps and conditions. Preserve
the current release's 19 chunks and 39 curriculum links. Preserve old sources, receipts and releases byte
for byte. A supplementary receipt is evidence for selected fields only; it never changes source authority.
Activate only after local rehearsal, exact owner field reviews and hosted read-back. Rollback restores
`p09-research-selected-20261022` and its matching runtime package.

## Design

- Reuse the existing C1 receipt structure and Python `_validate_receipt`. New
  `SourceSupplementaryReviewLoader` handles an already partially-reviewed source; it does not invoke
  the original source-state transition. Require the current source register plus a prior receipt id.
- Append a cumulative C1 receipt to `source_partial_reviews` and an immutable parent link in a new
  `source_review_supplements` table. Parent receipts/chunks/events must be retained exactly; new evidence
  binds only new owner readings. The original document_versions/source_register is unchanged.
- Extract shared SQL receipt validation from the original RPC into a private helper, preserving the
  original RPC's pending-state requirement, publication refusal and replay/conflict behavior. New RPC
  validates cumulative snapshot/event/dependency closure, current registered source, parent binding,
  exact stored chunks/spans and replay. Both functions remain SECURITY INVOKER, service-role only.
- Extend selected-review source binding through the immutable parent chain to an evidence item already
  in the unchanged source register. Preserve all selected-context, exact span/content and scope checks.
  One cumulative receipt per source works with the existing selected-review format.
- New chunks can inherit the current source's verification state and partial-review state only when
  their new review receipt is checked. They stay outside the active release until its replacement is ready.
  No disabling triggers, mutating published evidence, or storing a fabricated source edition.
- Capacity finding: the complete table ends at physical p.95 (p.96 starts student services), with more
  than 32 logical rows once the academic-dishonesty subrows and shared corrective measures are retained.
  Raise only the trusted chunk-id filter bound to 128 in the g2 migration, with boundary tests; keep
  existing scope/version/entity bounds at32 and top-k unchanged. This avoids merging unrelated offenses
  or dropping reviewed rows to fit a technical limit. Existing migration history stays unchanged.
- Build a new embedding manifest/set with the same pinned model/configuration; reuse existing vectors
  unchanged and embed new chunks locally. Create a new selected review/research release, copy all 39
  ledger links, and switch runtime package/release pins together. Keep rollback artifacts ignored.

## Tasks and verification

1. Finish item g's roster comparison before g2 production changes; record existing router misses separately.
2. Add synthetic database regressions: append review to a published source without mutating its register,
   old release or receipt; exact replay; changed replay, wrong parent/hash/spans/events and missing old
   coverage reject atomically; anon/authenticated cannot read/write review records or call the RPC.
   New release can combine old/new chunks; old release remains unchanged and rollback still works.
   Observe RED on the actual disposable Docker DB before implementing the migration.
3. Add client contract tests using the real receipt validator and an explicit boundary transport. Confirm
   source states, JSON safety, exact admin RPC payload and returned receipt identity; observe RED.
4. Implement the smallest shared validators/append-only path; GREEN on new tests and existing C1,
   selected-review, source-verification, release/security and runtime suites. Mutation-check key guards.
5. Build reviewed source fields from original native spans and rendered pages. Keep full logical rows and
   continuation groups. Source gaps remain explicit; no invented interpretation of malformed exceptions.
   Apply recorded standing approval to clear repeated cases; ask owner only about new ambiguity. Source approvals are not release
   currentness or school approval. Save actual owner decisions immediately in the source-review report.
6. Reuse the package preparation/governed loading pipelines from the checkpoint. Rehearse the complete
   new release locally, including immutable old data comparison, exact ledger membership and rollback.
   Apply through hosted MCP only after tests/rehearsal; read back exact content, grants, RLS and advisors.
7. Switch the local research pin/package and hosted release together; live source questions in all three
   languages, roster comparison, full `tests/` suite, independent review and compact checkpoint.

Commands: shared Python 3.13 venv with `PYTHONUTF8=1`, `-X utf8 -B -m pytest -q -p no:cacheprovider`,
external evidence/basetemp in workspace audit-evidence. SQL migrations created by installed CLI
`migration new`. No installs. Serialize model runs/full suite to fit available RAM.

## Review focus

New correctness finding during package preparation: build_multi_research_resources derives its root
release id only from curriculum members, so changing only documents reuses it. Before switching sources,
add a regression and bind the runtime root id to the document embedding/catalogue/review snapshot too,
while preserving the unchanged symbolic rule-bundle version. Apply to relevant research factories;
reuse existing release translation rather than changing Prolog facts. This is necessary version binding,
not a scope expansion. Full suite at f591416 passed6628 +1589 subtests; any new code gets fresh checks.

- A cumulative review must not silently omit or rewrite an old field or source event.
- A new receipt must not imply that the university approved the source or resolved an original defect.
- Runtime roles must see only active-release chunks, never pending reviews or another user's private data.
- Source-register immutability and old-release rollback must hold after every intermediate operation.
- Multi-page penalties/procedures must retain their offense/step, responsible roles, times and conditions.

## Current state

Owner approved route/source batches1-12 and standing treatment of clear remaining rows/blanks;
missing item22 separately settled. All61 draft records independently source-checked. Actual DB/client RED observed, then GREEN8 tests
+20 subtests (after fixing fixture observation and SQL compilation issues). Independent review found that
direct service-role INSERTs could bypass RPC validation. A direct-insert regression reproduced it (expected
exception absent); added row-level validation using the same proof helper. GREEN9 +20 subtests. Added
second-generation ancestry and changed-replay coverage included in final focused run.
Final focused g2 run:12 passed +20 subtests (`supplement-final.log`). Legacy selection:87 passed +564
subtests, two security-audit subtest failures caused by the old retrieval signature; audit corrected at
`c048bcb`, focused rerun1 passed +2 subtests. Capacity RED observed at33/128 ids, then GREEN33 tests
+17 subtests;129 rejects, other filters retain32 limit. Five isolated DB mutations caught: link proof,
parent history, parent binding, RPC grant and capacity bound. No production files changed by mutation runs.
Roster19 complete63/63, 0 exceptions, no previously answered status/decision lost; see topic execution report.
No hosted g2 change. Full suite at f591416 passed6628 +1589 subtests (6 skipped,2 xfailed).
Subsequent dirty root-id/blank changes: latest focused1 failed,38 passed,+20 subtests; blank null
conflicts with existing selected-review codec empty-string contract. Owner paused before /clear;
[session handoff](2026-10-25-phase11-session-handoff.md) records exact recovery/package steps.
Real-source package compilation and governed rehearsal remain pending.

Ruling: prepare/implement the additive g2 path locally while the existing hosted roster finishes. This
independent work cannot change its already-loaded runtime or hosted release. Defer all hosted g2 changes,
source/package switching and activation until item g comparison is complete. This saves idle time without
weakening the planned integration gate. Published release lifecycle status may change on activation;
its content, review receipts and source records remain immutable.
