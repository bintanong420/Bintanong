# Real-data runtime plan (owner-authorized development use)

21 October 2026. Authority: owner decision recorded in `AGENTS.md`
("Real-data development"). Development/testing only; no public deployment.

## Current state (verified)

- The live runtime (`backend/bintanong_runtime/application.py`) already uses the
  real query encoder, retrieval engine and local Supabase, but only through a
  synthetic-only release provider (`CheckedSyntheticReleaseProvider`).
- `CurriculumRuntime.from_bundle` refuses non-synthetic ledgers; Phase 06 added
  `CurriculumRuntime.for_offline_research(bundle, authorization=...)` for
  reviewed institutional rules.
- Local Supabase (`supabase_db_Bintanong`) holds 1 chunk (the fictional one).
- Real reviewed documents exist as the Phase 05 loader package: 19 chunks,
  54 source spans, 19 saved vectors (embedding set `02fce0fc...8811`).
- Reviewed BSCS relationships (old 2018-2019 and proposed 2025-2026 curricula)
  exist in the Phase 06 delivery; blank prerequisite cells stay unknown.

## Tasks (each test-first with synthetic stand-ins; real data stays untracked)

1. **Load documents locally.** Load the Phase 05 package into local Supabase as
   one development release with the existing storage loaders; verify counts,
   hashes and that held fields (e.g. F04) are excluded. Local DB only.
2. **Research release provider.** Add an explicit `research` runtime mode that
   pins that release and is refused unless the owner-authorization record is
   present. The synthetic provider stays the default for tests.
3. **Real curriculum rules.** Build the reviewed BSCS bundle and run it through
   `for_offline_research`; supply the real course catalog/aliases per curriculum
   version and the existing capability names. Unknown curriculum -> clarify.
4. **End-to-end observation.** Run the accepted roster's document variants (39)
   and structured reservations (18) once each through the real path; record
   per-stage timing including embedding and Supabase. No new question wording.
5. **Record and close.** Results report, checkpoint/progress, then reassess the
   Phase 09 exit.

## Limits

Retrieval quality and answer accuracy on real data are unknown until task 4.
Source-gap, scope, unknown-versus-unmet, privacy and per-part/withholding rules
are unchanged. Data updates after the university responds are a later task.
