# Hosted Supabase integration plan (Phase 09 reopened)

22 October 2026. Owner direction: "we should really utilize supabase because after all it will
in the end run in supabase. So we are going to continue in phase 9 still." Phase 09 is reopened;
the 22 Oct closeout handoff stays as a historical record (`git show a31ac32:plans/phase-09-handoff.md`).

## Read-only findings (22 Oct, Supabase MCP, project `jyrudbiuajahsucsorco`)

- MCP connection works (not logged out). Applied migrations: 6 (Phase 04 only).
- All 19 public tables exist, RLS on, **0 rows**. The 7 Phase 05 migrations in
  `supabase/migrations/` (2026-10-12 013339 to 2026-10-16 162938) are not applied.
- Advisors: security none; performance 24 INFO "unused index" (empty tables; ignore).
- `retrieve_context` serves only the row in `active_release`. `activate_knowledge_release`
  refuses documents unless `approval_state='approved'`, `verification_state='verified'`,
  `content_review_state='reviewed'`, and rules unless `approval_state='authorized'`.
- Local `.env` `SUPABASE_DB_URL` points at the local Docker DB, not the hosted project;
  no hosted URL/keys are configured on this machine.
- Why it was not used before: earlier sessions treated hosted schema/data changes as
  needing explicit owner approval, and the 21 Oct real-data decision did not name the
  hosted database, so research mode used the read-only PackageStorage stand-in.

## Decision needed: how a research release becomes readable

Marking sources `approved` would record a university approval that does not exist.
Options: (A, recommended) a new migration adds an honest research path: release kind
`research` with the owner authorization reference `research-owner-20261021`, sources in a
distinct `research_authorized` state, activation allowed only for that kind, answers still
labelled candidate/research; institutional activation rules unchanged. (B) set `approved`
with the owner reference as approval ID (not recommended: misstates authority).

## Tasks (after the decision)

1. Apply the 7 Phase 05 migrations to hosted via MCP `apply_migration`; re-run advisors.
2. Research-release migration and Python contract support (TDD; local Docker DB first).
3. Load reviewed real data with the existing loaders (register sources, chunks, 1024-d
   embeddings, reviewed BSCS course facts/rules), create and activate the research release.
   Needs hosted `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` in the ignored `.env` (owner).
4. Runtime: research mode reads hosted Supabase through the existing storage client;
   check retrieval equivalence with PackageStorage (39/39 offered chunks).
5. Re-run the 63-case roster; report Supabase/network timing separately.
6. Phase 09 closeout again with the updated evidence.

Boundaries: undergraduate scope, source-gap rules, F04 held, no institutional approval
recorded, no public deployment. Real data use per the 21 Oct owner decision.
