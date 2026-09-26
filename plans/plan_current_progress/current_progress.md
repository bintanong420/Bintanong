# Current prospectus workstream progress — 26 September 2026

This is the cross-agent handoff for the approved, review-only prospectus workstream. It is not a formal numbered phase checkpoint or evidence of institutional source approval. Verify it against Git and fresh tests before acting.

## Repository state observed

- Branch `dev`, HEAD `8e382bddf17330c10da118e86f42016fd71dadb8`.
- `phase_state.py inspect --repo .` reports a valid ledger, Phase 0 complete, no active phase or plan, and Phase 1 as the next permitted phase. `plans/INDEX.md` remains the phase authority.
- Working tree was already dirty before this planning work: `backend/bintanong_tools/bintanong_jsonifer_prolog/bintanong_prospectus_jsonifier.py` is modified, and `plans/CODEX_HANDOFF_prospectus_extractor_phase2_2026-09-26.md` is untracked. Preserve both. The parser's text matched the dataset workspace extractor line for line at inspection time; file SHA-256 values differed because the files use different line endings.
- During this review, `backend/bintanong_tools/bintanong_jsonifer_prolog/dataset/` appeared with 39 PDF files and a `json_output/` directory; `.gitignore` also became modified. None was created by this planning pass. The PDFs' 39 SHA-256 hashes exactly match the 39 distinct hashes among the 44 original dataset PDFs. Permission to store institutional PDFs in Git is still unverified; preserve these concurrent changes and do not commit the PDFs by default.
- `backend/bintanong_tools/ingest.py` offers generic `parse`, not a prospectus command or review/release workflow. The Compose `ingest` service runs help by default and has no institutional PDF input mount.

## Evidence available, with limits

- Dataset workspace: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump`. The original PDFs under `PalSU Undergraduate Prospectus Website Dump/` are the extraction source; generated JSON is diagnostic output.
- The latest dataset manifest, `docling_jsonified_output/v5_final_cross_college_2026-09-26/batch_manifest.json`, was present and reports 44 PDF paths, 37 audit failures, 6 warnings, 1 OK, and 0 processing exceptions. The handoff reports 39 distinct PDF hashes and 2,075 extracted course records. These counts are not course-field accuracy measurements.
- The dataset handoff reports 39/39 focused/inventory tests and 80/80 extractor self-checks. Those results were produced in the dataset workspace; no fresh Bintanong integration test or human PDF-checked reference set has been recorded here.
- Known PDF-backed defects include merged Values Education `Ed 12`/`FS 2` and Psychology `Psych 9`/`Psych 10` rows, contaminated titles/prerequisites, and missing term assignments in other programs. Seven extractor-audit passes are still candidates, without human content review or issuing-office/version approval.
- The existing Phase 2 plan covers the prospectus track and requires source-linked extraction, safe reruns, provenance, and a callable backend. The later handoff adds the 44-path corpus results, a 39-unique-PDF reference set, and a Bintanong manual flagger/release gate proposal. The master plan makes Phase 1 source contracts a dependency of Phase 2.

## Planning status

- Approved workstream plan: `plans/2026-09-26-prospectus-phase2-implementation-draft.md`. The user clarified that incomplete Phase 1 indexing must not block prospectus preparation already underway in parallel.
- The user clarified that human post-processing is required in a GUI. The draft now requires synchronized source PDF, reconstructed table layout, and extracted JSON views with traceable corrections. It reconciles the two-PDF pilot with later review of all 39 distinct PDFs.
- The master plan now records parallel prospectus preparation, a local researcher correction GUI in Phase 2, decision/corrected-candidate artifacts, and a separate gate for hosted reviewer access and active institutional release.
- No product implementation, source approval, database ingestion, or active RAG/Prolog release was performed in this planning pass.
- The executable scope is prospectus JSONification, candidate Prolog generation, PDF-backed validation, and local human correction. Provisional source records use original PDF hashes while Phase 1 indexing catches up; pending issuer/version verification cannot be promoted as active knowledge.
- Planning checks: `python .agents/skills/bintanong-phase-handoff/scripts/phase_state.py validate --repo .` reported `State: valid`, no active phase/plan, and Phase 1 next; `git diff --check` found no whitespace errors. No product tests were run because only planning files were changed by this pass.

## Next agent action

1. Read `plans/INDEX.md`, the new draft plan when present, the three source documents named above, and the user's answers to open questions.
2. Re-run `python .agents/skills/bintanong-phase-handoff/scripts/phase_state.py inspect --repo .`, inspect Git status/diff, and preserve the pre-existing dirty files.
3. Continue the approved prospectus workstream from its first unchecked task while Phase 1 indexing proceeds separately. Do not interpret this progress note, a provisional hash record, or any extractor audit status as institutional authorization.
