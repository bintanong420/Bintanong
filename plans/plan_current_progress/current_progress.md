# Current prospectus workstream progress — 29 September 2026

This is the recoverable handoff for the approved review-only prospectus workstream. It is not a formal numbered phase checkpoint or institutional approval. Fresh Git/test evidence outranks this note.

## Completed work

- Planning commit `e31a881` approved parallel prospectus preparation and the local human correction GUI. Phase 1 source approval still gates active institutional use.
- Task 0 commit `702a38f` added and tested `ProvisionalSource(pdf_sha256, source_locator)`, with source verification fixed pending. It verifies original PDF bytes and rejects hash mismatch. Local copied PDFs match the external corpus's 39 distinct hashes / 44 paths; the ignored inventory is under `backend/bintanong_tools/bintanong_jsonifer_prolog/dataset/PalSU Undergraduate Prospectus Website Dump/provisional-source-inventory.csv`.
- Task 0 review passed; recorded supplemental suite: 19 tests passed using `uv run --project backend --extra tools --extra dev --with fastapi==0.141.1 python -m pytest -q tests`. Full Windows `api` extra could not build `janus-swi` without MSVC. That is prior Task 0 evidence, not a Task 1 rerun.
- Task 1 completed fresh BSCS and Architecture original-PDF conversions and an initial comparison of all 132 scheduled rows. Both complete one-page originals were visually inspected. Independent source transcription and candidate comparison produced 1,320 field decisions. Eight additional BSCS option rows were checked separately.
- Task 1 created a 92-entry field discrepancy/spot-check ledger, plus a fresh 39-hash/44-path review index. Initial checks include Values Education, both Psychology tracks, Civil Engineering, BSBA Marketing, Midwifery, old ComSci and source-total conflicts. Other Engineering PDFs are indexed/rendered but not field-reviewed.

## Current evidence and limits

- Task 1 report: `.superpowers/sdd/2026-09-26-prospectus-phase2-implementation-draft/task-1-report.md` (ignored local review workspace).
- All detailed source-derived review artifacts remain outside Git: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\docling_jsonified_output\task1_baseline_2026-09-29`.
- Authoritative conversion source: original PDFs under the external `PalSU Undergraduate Prospectus Website Dump`. Generated JSON is diagnostic output, never the expected source reading.
- Fresh self-test: 80/80. Runtime Python 3.13.5, Docling 2.129.0, docling-parse 7.20.0. Repo/dataset parser text still matches after normalizing line endings.
- Fresh BSCS: 55 courses, 159 units, audit WARN, strict exit 0. Fresh Architecture: 77 courses, 230 units, audit ERROR, strict exit 1. Both audit states are extractor-only.
- All 132 scheduled codes and course units match visible source rows. Missing scheduled codes: 0/132 source rows; false scheduled codes: 0/132 emitted rows. Course identities being present does not make their fields correct.
- Nine critical field groups per row: 1,112 matches, 73 mismatches, 3 source-unresolved / 1,188 comparisons under documented whitespace/hyphen/terminal-period normalization. Physical page is measured separately. No corpus accuracy percentage is claimed.
- BSCS truncates one standing requirement and spills its last word into the next course's prerequisite. Architecture has 33 wrong titles, 13 wrong raw prerequisite fields, 11 wrong resolved prerequisite fields, and 3 unresolved source references. Explicit elective labels are not correctly reflected in `is_elective` for 12 pilot rows.
- Architecture's printed second-year second-term 23 and grand 231 conflict with visible row sums 22 and 230. Extracted individual course units agree with the source; do not change units to force its checksum.
- All discrepancy records have PDF hash/page/cell locators. Corrected cell ownership and geometry still require independent review, especially where Docling merged or misplaced text. The 37 other unique PDFs lack complete field review. This is an agent-reviewed initial baseline, not a human-approved gold set.
- The old v5 batch manifest was freshly read: 44 paths, 1 OK, 6 WARN, 37 audit failures, 0 exceptions. Its 7/44 audit-pass count is not field accuracy. The non-pilot spot checks compare original PDF views against this older v5 output and are labeled as not freshly converted.

## Repository state

- Task 1 implementation base: `dev`, HEAD `702a38f`. The next documentation commit updates this note; identify that commit from Git rather than treating the earlier planning HEAD `8e382bd` as current.
- Pre-existing dirty files remain untouched: `.gitignore`, `backend/bintanong_tools/bintanong_jsonifer_prolog/bintanong_prospectus_jsonifier.py`, and untracked `plans/CODEX_HANDOFF_prospectus_extractor_phase2_2026-09-26.md`.
- Parser SHA-256 at review: `b50ece65539252cc4c7b519dac8506497dd40ec0f3b9220c0575bab6f745c835`; its pre-existing diff is 41 insertions / 3 deletions. HEAD alone does not identify this parser snapshot.
- No Task 1 parser edits, institution PDF staging, production release companions, active RAG/Prolog activation, database writes, or formal phase advancement occurred. Local legacy full candidate JSON retains parser-embedded candidate Prolog/RAG fields; these have no approval status.
- `phase_state.py inspect` reports a valid ledger, no active numbered phase, Phase 0 complete, Phase 1 next permitted. `plans/INDEX.md` remains authoritative.

## Next action

1. Review the Task 1 report and local source-backed discrepancy ledger. Independently confirm corrected cell ownership before marking a source reference human-approved.
2. Begin Task 2 with one focused failing regression per demonstrated topology failure. Include the newly demonstrated BSCS standing spill and Architecture row spill alongside the Values Education/Psychology merged rows. Keep ambiguous source references explicitly unresolved.
3. After each shared parser change, run the self-test and original-PDF 44-path regression, compare repaired/newly broken fields, and preserve all source aliases. Complete the 39-PDF reference before any general accuracy claim.
4. Continue the approved adapter, review GUI and provenance tasks in plan order. Pending Phase 1 indexing does not block local review preparation; active institutional release still requires source/version and rule approval.

Do not repeat Task 0 or discard the pre-existing dirty parser. Do not use generated JSON as the conversion source. No numbered Phase 2 exit or Phase 3 advancement is implied.

## Parallel prospectus Task 2 recovery (29 September 2026)

- The full source-backed report is `plans/prospectus_extractor_recovery_2026-09-29.md`. New parser guards withhold fused multi-course cells and preserve page/cell evidence; original-PDF checked slash-code repairs cover old ComSci, Hospitality, and Tourism. A process-isolated command checkpoints each PDF so one Docling child crash cannot erase later results.
- Final regression used 44 original PDF paths (39 distinct hashes), with 44 detailed and 44 compact review JSON files. Processing errors: 0. Extractor audit: 1 OK, 6 WARN, 37 ERROR; strict run exit 1. These are candidate outputs, not approved curricula. Forty-five merged-code issues in 14 paths have PDF review evidence. No Prolog or RAG companions were generated in this run.
- Verification: Bintanong tests 25 passed and 13 subtests passed (5 dependency warnings); extractor self-test 80/80. The supported isolated command passed a separate two-original-PDF smoke run; the 44-path result came from an external equivalent runner. Full row-field reference remains only two PDFs, so no corpus accuracy claim is justified.
- Remaining critical parser defects include incomplete BSCS standing ownership and the Social Work `World` spill into SW 13. Architecture has many wrong titles/prerequisites. Task 2 remains partial, review-only. The formal phase ledger is unchanged; Phase 1 source approval and later human curriculum/rule review still gate active use.

### Latest standing-spill check

- A source-backed guard now withholds one-word standing continuations from the following course and raises a blocking anomaly with PDF cells. The original new BSCS PDF changed from WARN to ERROR; GE-STS no longer carries `semesters`, while CS Elect 4/L still needs its complete standing reconstructed by review.
- The supported isolated command completed all 44 original paths: 39 distinct hashes, 0 processing errors, 1 OK, 5 WARN, 38 ERROR, exit 1 due to audits. Only BSCS changed audit status. Candidate fields changed in new BSCS, Social Work, and Civil Engineering; visual checks of the original latter two PDFs confirm blank next-course prerequisites. The earlier 45 fused-course flags remain, plus 3 standing-fragment flags.
- Verification: full suite 26 passed and 13 subtests passed; extractor self-test 80/80. No corpus accuracy claim, institutional approval, or active RAG/Prolog release follows.
