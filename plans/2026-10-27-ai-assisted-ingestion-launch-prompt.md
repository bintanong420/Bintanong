You are implementing the Bintanong Phase 11 AI-assisted ingestion extension on `feat/p11-policy-ingestion-review`.

Read and execute:

`plans/2026-10-27-ai-assisted-ingestion-codex-plan.md`

Also read the existing Phase 11 plans/checkpoint, `AGENTS.md`, relevant Phase 2 ingestion plans, and Lawrence-authored planning files in the worktree before changing production code.

This is NOT a greenfield implementation.

The branch already has the important Phase 11 pipeline:

- source-bound preparation;
- review packets;
- source/PDF evidence;
- PDF rendering;
- `ReviewSession`;
- human `accepted/corrected/unresolved/pending` decisions;
- researcher reviewer UI;
- `proposed_value`/review-template proposal behavior;
- reviewed package build;
- verification.

Do not rebuild those pieces.

Lawrence's remaining requirement is narrowly:

1. existing native/script extraction + multimodal page-image verification + human verification;
2. LlamaParse as an alternate parser strategy feeding the SAME existing human-review boundary;
3. an A/B evaluation of those approaches.

Core invariant:

**Parsers produce candidates. AI produces advisory proposals. Humans produce review decisions. Only human-reviewed decisions may feed authoritative downstream knowledge.**

First inspect the actual repository and confirm the safest integration point for the existing `proposed_value` mechanism and packet hashing.

Prefer:

`existing candidate -> AI proposed_value -> existing pending review`

over inventing a new AI persistence/review architecture.

Because packets are hash-bound, do not casually mutate finalized `packet.json`. Determine whether proposals should be generated before packet finalization or represented as a separately hash-bound advisory sidecar only if existing proposal handling cannot safely accommodate them.

Execution mode:

- Work through the entire plan sequentially.
- Do not ask me for approval between ordinary tasks.
- Use tests first.
- Run focused tests and relevant regression tests after every task.
- Make small local commits as tasks become green.
- Continue automatically after successful tasks.
- Preserve unrelated user changes.
- Do not force-push or use destructive Git operations.
- Do not push unless separately authorized.

Reuse existing model/provider infrastructure if appropriate. If none fits, add only the smallest ingestion-assistance interface needed.

Use a deterministic fake provider for normal tests.

Live multimodal/LlamaParse tests are optional when credentials are unavailable. If credentials do not exist, finish the mocked/tested implementation and report the live smoke as NOT RUN rather than blocking implementation.

For LlamaParse, verify its current official API behavior before implementing live calls. Do not hardcode assumptions about current pricing, free-tier quotas, or credit usage.

Do not introduce:

- autonomous AI approval;
- AI writes directly to reviewed chunks;
- a second reviewer;
- a second review journal;
- a second build pipeline;
- trusted PDF-to-Prolog generation;
- hosted Supabase mutation;
- release/publish behavior;
- model training;
- broad source-contract changes merely for convenience.

Stop only for the explicit STOP conditions in the plan, particularly if a shared canonical contract requires a major change or the repository materially differs from the documented checkpoint.

Otherwise, make the engineering decisions yourself and keep going.

At completion, provide the full final report required by Section 22 of the plan, including:

- final architecture;
- reused components;
- changed files;
- human-authority proof;
- exact test commands and results;
- live tests run/not run;
- A/B evaluation state;
- limitations;
- commits;
- remaining T4/T5 work.

Begin by verifying repository/branch state and executing Task 0, then continue through the rest of the plan automatically if no STOP condition is triggered.