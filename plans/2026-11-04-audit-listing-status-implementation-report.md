# Audit prerequisite listing and status recovery

Date: 4 November 2026. Candidate development only; no institutional activation.

## Recovery

Resumed branch `fix/dialogue-status-and-prereq-listing` at `ee014749`, preserving Claude's dirty work from session `b73f3662-df93-4755-8a11-22c52689e6e8`, subagent `a7cc515253896355a`. The original tracked patch and new tests were saved under ignored `audit-evidence/p12ds-resume-20261104/` before edits. The parent coordinates the active checkpoint, shared progress and scope/context evidence.

`2026-11-04-architecture-stabilization-plan.md` and `2026-11-04-independent-audit-memory-conversation.md` match the supplied Downloads originals after newline normalization. Checkout CRLF versus original LF explains different byte hashes; no plan content was changed.

## Delivered behavior

- `list_course_prerequisites` is a distinct version-scoped structured lookup. It reads the reviewed authoring ledger's canonical requirement tree and supplies source spans, rule IDs and bundle version. It never invokes the eligibility worker or returns a student decision.
- The registry, semantic router prompt, compiler, adapters and research capability inventory recognize the operation. No phrase-matching router patches were introduced.
- Host wording preserves all-of, any-of, co-requisite and reviewed-none semantics. Unresolved printed conditions, including nested conditions, retain their quoted limitations and adviser/college referral. Existing reviewed blank-cell normalization remains authoritative; no new source decisions were made.
- A listing can offer an optional eligibility check. It does not ask a mandatory passed-grade question or create pending eligibility state. Existing personalized eligibility remains unknown when completion facts are absent.
- Unanswered turns carry a typed reason separately from public status. An empty clarification gets `dialogue_unresolved`, names prior course/topic context where available, and avoids a reviewed-source-gap claim. Actual missing facts, retrieval misses, unsupported scope, source conflicts, validation and system failures remain distinct. Retrieval budget/neighbor gaps do not establish an original-source defect.
- The API emits optional `reason` metadata and the frontend strict schema accepts its ten enumerated values. Existing answered metadata and ordinary lookup serialization remain unchanged.

## Verification

All commands used system Python 3.13, `-B`, `-p no:cacheprovider` and external basetemp under ignored workspace `audit-evidence`.

- RED: new listing test rejected the previous alias to eligibility (no bound listing request). Corrected initial fixture strict-constructor mistakes before observing this behavior failure.
- RED: retrieval budget gap incorrectly reported `source_incomplete`; new negative regression exposed it.
- RED: API dropped typed reason (`KeyError: reason`).
- RED: nested unresolved condition lost its printed wording.
- GREEN: combined focused run, **186 passed in 6.29s**: `test_api_stream`, `test_generation_prerequisite_listing`, `test_orchestration_reasons`, `test_generation_course_facts`, `test_symbolic_course_facts`, `test_routing_course_facts`, `test_routing_compile`, `test_routing_prompt_example`.
- After adding nested-condition regression/rendering: **33 passed in 2.64s** (`test_generation_prerequisite_listing` and `test_generation_course_facts`).
- `git diff --check` passed. Raw local logs: ignored `audit-evidence/p12ds-resume-20261104/{red2,gap-red,api-reason-red,nested-red,final-verified,nested-green}.txt`.
- Frontend transport test could not execute because this isolated worktree lacks the existing `ai` dependency. No installation or dependency junction was made. Parent must run the new Node transport test and TypeScript check using its existing dependency tree after integration.

## Boundaries and next action

No live model, browser, GPU, database or hosted service validation was performed. No dependencies, source authoring records, private inputs or release activation were changed. The two-curriculum/three-language fixtures are synthetic and do not prove live semantic routing accuracy. The parent owns source-backed BSIT/live validation and independent review.

Next: integrate and independently review this increment; verify frontend metadata in the parent checkout. Phase 2 conversation-state ledger remains unimplemented. A statement such as "I have passed CC5/L" after a listing must not be treated as an automatically approved eligibility request; semantic follow-up/acknowledgment behavior and shifting/topic-switch regressions remain separate follow-up work. This report does not close the broader unreviewed-data, curriculum-planning or conversationality checklist.
