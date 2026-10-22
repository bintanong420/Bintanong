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

## Owner decisions (22 Oct)

- Research release kind (option A) chosen.
- Hosted credentials: owner ran a script (Management API, owner's stored access token)
  that wrote `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY` into the ignored
  `.env`. Read-only REST check: both keys HTTP 200 on `knowledge_releases`.

## Task 1 result (done 22 Oct)

The 6 pending Phase 05 migrations were first applied to the local Docker DB; storage DB
tests 146 passed, 844 subtests (583 s). All 7 were then applied to hosted via MCP
`apply_migration`, and each recorded version was reset to the repo file version
(`apply_migration` stamps the current time). Hosted history now matches the repo: 13
versions. Schema digests hosted vs local: columns (165), policies (22), triggers (110) and
migration history identical; all 34 functions identical once CRLF is stripped (the local
DB loaded Windows CRLF files; hosted Phase 05 bodies use LF). Security advisor: none.

## Task 2 design (research release kind)

Refinement of option A: the owner authorization lives on the release, not on each source,
so source registers stay truthful (`approval_state` stays `not_requested`; no new source state).

- `knowledge_releases` gains `release_kind` (`institutional` default | `research`) and
  `research_authorization_ref` (required and `^research-owner-[0-9]{8}$` iff research; null
  otherwise). A research release must be a selected-review release (`review_scope_id` set) and
  carries no rules (selected releases already forbid them).
- `validate_release`: institutional rules unchanged. Research releases instead require each
  source to have acquisition `verified`, verification `observed` (V1) or `verified`, approval
  `not_requested` or `approved`, content `partially_reviewed` or `reviewed`; chunk checks keep
  anchoring, hashes, spans, embeddings and content-review agreement, with source verification
  matching the source's state.
- RLS read policies (document_versions, chunks and their dependants) accept rows reachable
  through the active research release under the same conditions; nothing else becomes readable.
  Administrative receipt tables stay denied.
- Python: release creation accepts the kind/ref; runtime labels research answers as today.
- Tests (local Docker DB, disposable databases): research release activates only with the
  ref and selected review; institutional activation still refuses unapproved sources; anon
  reads only the active research release's rows; a research ref on an institutional release
  and a research release without the ref are both rejected.
- Course facts/Prolog stay in the reviewed bundle for now (out of scope for this release).

## Tasks 2-3 result (done 22 Oct)

- `115d218`: migration `20261022090000_phase9_research_release.sql` and
  `ReleaseManager.designate_research_release`. TDD: 22 new DB tests RED then GREEN; storage
  regression 182 passed, 916 subtests (760 s). Applied to hosted via MCP; version reset to the
  file version (MCP stamps UTC time). Advisors: none.
- Load script (workspace `audit-evidence/p09-supabase-20261022/load_research_release.py`)
  replays the governed Phase 05 chain unchanged, then designates and activates. Local
  disposable rehearsal and hosted run both passed: 5 sources, 19 chunks, 54 spans, 19
  embeddings, 5 V1 observations; anon sees exactly those rows and `retrieve_context` is ok;
  14 inputs byte-unchanged. Hosted active release `p09-research-selected-20261022`
  (research, `research-owner-20261021`); every source `not_requested/observed/partially_reviewed`.
- The owner granted the hosted load in `/permissions` after the classifier first blocked it.

## Tasks (after the decision)

1. [done] Apply the 7 Phase 05 migrations to hosted via MCP `apply_migration`; re-run advisors.
2. [done] Research-release migration and Python contract support (TDD; local Docker DB first).
3. [done, documents only] Load reviewed real data with the existing loaders (register sources, chunks, 1024-d
   embeddings, reviewed BSCS course facts/rules), create and activate the research release.
   Needs hosted `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` in the ignored `.env` (owner).
4. Runtime: research mode reads hosted Supabase through the existing storage client;
   check retrieval equivalence with PackageStorage (39/39 offered chunks).
5. Re-run the 63-case roster; report Supabase/network timing separately.
6. Phase 09 closeout again with the updated evidence.

Boundaries: undergraduate scope, source-gap rules, F04 held, no institutional approval
recorded, no public deployment. Real data use per the 21 Oct owner decision.
