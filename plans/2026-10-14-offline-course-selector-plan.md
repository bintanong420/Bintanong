# Offline course selector implementation plan

**Goal:** Make the completed course-identity diagnostic reusable for offline
candidate retrieval after explicit curriculum selection.

**Spec:** The exact next action in
`2026-10-14-dataset-relocation-and-cli-handoff.md` and
`2026-10-14-course-identity-diagnostic-report.md`. The owner requested continuation;
settled source reviews and development authorization apply.

**Architecture:** Add `candidate_course.py` alongside the existing curriculum
helper. Preparation calls the complete reviewed curriculum preparation contract
and binds each candidate to its reviewed `course_code` field, spans and event.
Selection calls the existing curriculum selector before applying a separately
supplied target hint. Existing curriculum APIs and default outputs stay unchanged.

**Implementation calls:** Keep a digest-bound index containing the curriculum
catalogue and identity rows. Normalize case and whitespace only; printed `/L`
codes also expose the diagnostic's base key. Preserve punctuation/leading zeros.
Missing target roles return `needs_target_course`; unknown targets return
`unavailable` within the selected candidates, never a full-curriculum claim.
Return matching chunk IDs and copied identity evidence, not rewritten chunks.

## Constraints and review focus

- Python 3.13, existing authorized environment, no dependency/install changes.
- Candidate only; no runtime, database, Prolog, release or source activation.
- Preserve source values, field associations, spans, limitations and input objects.
- Reject changed source/review/chunk bindings through existing preparation replay.
- Curriculum ambiguity takes precedence; prerequisites never supply target identity.
- Existing 36 questions stay unchanged; synthetic controls are not benchmark cases.
- Inspect duplicate targets, missing/blank identity fields, digest changes, punctuation
  collisions and mutation through returned values during final review.

## Task 1: Prepare and select reviewed target courses

- [ ] Write `tests/test_candidate_course.py` with synthetic reviewed rows for two
  computing editions and another undergraduate program. Observe missing helper RED.
- [ ] Implement preparation/selection in
  `backend/bintanong_tools/document_ingest/candidate_course.py`.
- [ ] Run new tests and related curriculum/reviewed-context regressions GREEN.
- [ ] Replay the existing eight-row candidate preparation and six controlled CC5
  branches using saved evidence, resolving historical paths through the relocation
  mapping. Do not re-encode vectors or alter questions.
- [ ] Review the bounded change, run required verification, commit explicit files,
  update current progress/checkpoint/index and record the exact next action.

Verification uses pytest without cache and basetemp under workspace audit-evidence.
Full phase advancement remains blocked on existing formal source/retrieval gates.

## Resume evidence

Baseline `87f2b81`; owner deletion `artifacts/.gitkeep` and untracked
`backend/artifacts/` preserved. Consulted actual thesis physical17–18, routing PNG,
master section10, Phase04 complete handoff and Phase05 plan/checkpoint/blocked handoff,
scope/source-gap policies and dataset guide. No scope/routing discrepancy.
GitHub MCP lists remote p05 at `f10d5cd`; local work continues without push.
