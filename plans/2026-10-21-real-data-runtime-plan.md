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

## Findings while starting task 1 (21 October 2026)

1. **Supabase loading would require a false approval record.** Runtime reads only
   an active release, and activation requires sources recorded as approved.
   The owner's development authorization is not school approval, so task 1 is
   replaced: research mode will serve the 19 reviewed chunks/vectors through a
   read-only storage stand-in (as Phase 05's accepted evaluation did), with the
   real retrieval engine and real query encoder. Supabase stays untouched.
2. **Real retrieval is labelled `uncalibrated`**, which the pipeline maps to
   `insufficient_evidence`; every real document answer would be withheld.
   Phase 05 never calibrated a threshold. Needs an owner decision: in research
   mode, may a `reviewed_fields_available` result feed generation (the per-part
   reviewer and support checks remain the backstop)?
3. **No live subject selection.** Phase 05 supplied a trusted subject per
   question (7 subjects). The live pipeline has none. Options: run without the
   subject filter (global top-3), or let the router choose from the 7 subjects.

## Owner decisions on the findings (21 October 2026)

- Calibration: in research mode, a retrieval result whose evidence assessment is
  `reviewed_fields_available` may feed generation, still labelled candidate/
  uncalibrated; missing/conflicting/unsupported stay withheld. Per-part reviewer
  and support checks remain the backstop.
- Topic: no subject filter; plain top-k over the 19 reviewed chunks.

## Conflict found in the two decisions

`RetrievalEngine._retrieve_source_aware` produces the `reviewed_fields_available`
assessment only when given a `subject_id` and `requested_claims`; without a
subject it fails with `needs_subject`. Plain top-k (no policy) returns
`uncalibrated` with no reviewed-field assessment. So "no topic filter" and
"only reviewed-fields results proceed" cannot both hold. Awaiting owner choice.

## Owner resolution and revised tasks

Owner chose: the router picks the topic and requested reviewed facts, keeping the
reviewed-fields safety check. The reviewed universe is 7 subjects / 10 claim
reviews (8 `visible_fields`, 2 `not_stated_in_selected_fields`), so selection is
a closed list supplied by the pinned release; no extra model call.

Revised tasks (each test-first; synthetic stand-ins in tracked tests):
1. Read-only package storage stand-in serving the 19 reviewed chunks/vectors to
   the real `RetrievalEngine` with `SourceAwareEvidencePolicy`; Supabase untouched.
2. Router: optional per-document-part `subject_id` + `requested_claims`, enum-
   constrained to the release's menu; host validates; absent -> clarify/insufficient.
3. Research release mode: owner-authorization record required; real BSCS bundle
   via `for_offline_research`; real course catalog; `reviewed_fields_available`
   maps to ready only in this mode.
4. One observation of the accepted roster (39 document + 18 structured variants),
   per-stage timing including embedding.
5. Results, checkpoint/progress, Phase 09 exit reassessment.
