# Reusable offline course selector — 14 October 2026

The course-identity diagnostic is now a reusable candidate helper at `f9b1502`.
It prepares a reviewed course index and applies an explicit target-course hint
after the existing curriculum selector. All six saved controlled CC5 branches
reproduce their expected reviewed row. These are three accepted questions evaluated
under two explicit edition hypotheses, not six independent student cases.

## Behavior and boundaries

`prepare_candidate_course_index` accepts the same complete reviewed bundle,
inactive chunks, source bytes, review events, source versions and assignments as
`prepare_candidate_curriculum_catalogue`. It calls that preparation contract,
including original chunk replay, before deriving identities from each reviewed
`course_code` field. Each identity retains printed code, field association,
review-event digest, source/version/reading/chunk bindings and original spans.

`select_candidate_course` accepts this index and explicit `program_id`,
`version_id`, `student_context` and `target_course` hints. Curriculum ambiguity and
wrong program/version retain existing scope results. A selected curriculum without
a target role returns `needs_target_course` with no chunks. Matching narrows the
candidate chunk IDs and returns copied identity evidence. No match means
`target_course_not_in_candidates`, not absence from the complete curriculum.

Case and whitespace normalize for comparison. Punctuation and leading zeros remain
distinct. A printed combined `/L` code additionally exposes its base comparison
key, as in the prior diagnostic; the printed row and its requirements remain whole.
Prerequisite mentions never populate identity keys. Duplicate target rows remain
separate matching candidates for later ranking/context handling.

The existing curriculum module and its default behavior are unchanged. The new
module does not parse a student's query or implement automatic entity/role
extraction. Its digest detects changed preparation, not institutional approval or
an authenticated signature. Reprepare from trusted bytes/reviews after changes.
Original chunks, fields, spans, limitations and questions remain unchanged.

## Verification

- Synthetic missing-module RED:33failed/6passed,1.42s. The first implementation
  run exposed two stale expected fixture IDs after replacing synthetic source
  fields; the fixture now derives IDs from rebuilt chunks. No product correction
  was needed for that test-data error.
- Related curriculum/reviewed/context regressions:93passed/174subtests,4.03s.
- Final new-module tests:14passed/30subtests,2.35s, including retained gaps,
  duplicate targets, unknown codes, prerequisite-only mentions, changed source/
  review/chunk/index bindings, missing roles, scope ambiguity and copied outputs.
- Existing real preparation replay:8rows/13identity spans,6of6expected CC5 matches;
  catalogue equals the prior catalogue exactly. Six original PDF hashes verified
  via exact relocation mapping;1358prior dependency hashes preserved. No model
  encoding, source conversion or question edits.
- One independent read-only reviewer: no Critical/Important/Minor findings;
  focused28tests/79subtests pass3.62s. No additional reviewer or fix pass.
- Documentation/ledger checks before closure:455passed/11subtests,12.17s.
- Full fresh offline suite: **5236passed/494subtests**,6skipped/6warnings,
  **313.57s (5m13s),exit0**. Existing deprecation/GPU-marker warnings remain.
  Final documentation/ledger:456passed/11subtests,10.79s. Phase validation
  exits0; advancement exits1 as expected (formal Phase05 gates remain blocked).

Commands use the existing approved Python3.13 environment with `-B -m pytest`,
`-q -p no:cacheprovider`, and unique basetemp under
`C:/Coding-projects/bintanong_workspace/audit-evidence/p05-offline-course-selector-20261014/`.
The full command is `pytest tests -q -p no:cacheprovider`; offline model/Docling
configuration and existing assets are reused. No installs or dependency changes.

## Recovery and next action

Plan commit `17d86cc`; helper/tests commit `f9b1502`. Ignored evidence in the folder
above includes `replay_actual.py`, `candidate-course-index.json`, `cc5-replay.json`,
`replay-summary.json` and `full-tests.log`. Historical source paths are resolved
through the existing `p05-dataset-relocation-20261014/relocation-map.json`; old
manifests and source bytes are preserved.

Next authorized development can add the helper to a bounded offline ranking
comparison using the saved vectors and accepted scoped cases, with separately
recorded researcher target hints. Preserve baseline comparisons, missing target/
curriculum controls and complete cited contexts; do not claim automatic query
extraction or use semantic similarity to choose an edition. New/changed benchmark
wordings still require owner review before testing.

Actual six BSCS cases still require curriculum clarification; policy applicability,
source governance and formal retrieval calibration remain open. School validation
is deferred under standing owner authorization, not a blanket research-development
block. No database/runtime/Prolog/release activation or Phase06 advancement.
Owner `artifacts/.gitkeep` deletion and untracked `backend/artifacts/` preserved.
Consulted actual thesis physical17–18, routing PNG, master section10, previous
Phase04 handoff, Phase05 records and scope/source-gap/dataset policies; no discrepancy.

Evidence seal:10files/two code digests; manifest SHA256:
`7b12fbccda457e645a6fb4d6467cfd03c248653726bc927a18e6529f7bda372d`. Final Git includes only explicit helper/test/document paths;
original dataset remains untracked and owner artifact changes remain intact.
