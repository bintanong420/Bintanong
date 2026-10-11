Publishes the completed prospectus extractor phases A–D: modular extraction, markup comparison, the discrepancy verifier/fixer and ledger, separate review/source states, and byte-bound cache/publication verification. Five confirmed cross-phase review defects are fixed: missing markup PDF hashes, stale prerequisite states, omitted structural-anomaly review obligations, inherited executable authority on corrected candidates, and semantic-map identity races.

GUI and OCR implementation remain local and are excluded from this branch and its ancestry. Their existing plan documents are included alongside the existing E/F plans, explicitly labelled unfinished. No institutional originals or generated evidence are added.

Verification on the reviewed code:
- System Python 3.13: 1,013 passed, 13 subtests passed, five dependency deprecation warnings; native Janus 1.5.2 / SWI-Prolog 10.1.6 functional.
- Self-test: 80/80. Course comparer against local integration baseline 5c34fd7: 44/44 identical; only parser-package digest and run key change.
- B2 health counts: mixed21 / warnings_only3 / broken19 / clean1; title_from_pdf67, strip_banner0, unclaimed_code316, banner_leak3. Phase C prerequisite-state counts unchanged.
- Read-only trial sheets01/16/33: zero parse/check_against/build errors; all19 trial-folder files remained byte-identical. Publication interruption/input-change regressions pass; outgoing diff check passes.
- Independent specification and standards reviews approved the corrected code with no remaining confirmed defects. Details and deviations are recorded in plans/plan_current_progress/extractor_split_progress.md and the decision records.

Human B2/GUI trials and closeout, banner-split decision, real-photo support, source authorization and institutional activation remain pending. This PR does not complete whole master-plan Phase2 or move the formal phase ledger. Nothing here is institutional approval.

Local dev remains unchanged. This PR targets GitHub dev and is left unmerged for the owner's decision.
### Planning publication update — 7 October 2026

Publication tip: 4d780b7. Existing A/B/B2/C/D task plans, Phase D handoff, the immutable full master plan and the prospectus Phase 2 implementation plan are included. E/F and GUI/OCR plans remain preserved with unfinished implementation excluded.

Added a ready, preparation-only Phase 1 source-governance/contracts plan, remaining whole-Phase-2 document ingestion preparation, evaluation split/rubric protocol and a workstream status map. The formal ledger stays inactive with Phase 1 next permitted. Source approval, human trials and real-photo evidence remain distinct pending gates.

A completed, independently reviewed continuity fix distinguishes explicitly prepared ready plans from active phases and preserves superseded checkpoints. It changes no runtime behavior. Fresh continuity checks: 19 passed, 11 subtests passed; inspect/validate/can-advance valid, active phase null, latest Phase 0 handoff, next phase 1. Separate planning Spec and Standards reviews: APPROVED, findings NONE.

Fresh full publication suite at this tip: 1013 passed, 13 subtests passed, five dependency warnings, using owner-authorized system Python 3.13. Existing reviewed production corpus gates remain 80/80 self-test, 44/44 course-field preservation, unchanged B2/C counts and zero trial-sheet errors. No extractor production code changed in this planning update.

Institutional acquisition is outside Git: 78 originals copied, 156 independent hash checks passed; 63 unique byte identities, 13 duplicate groups, 15 additional duplicate paths. Acquisition integrity does not establish authority; verification remains pending and approval identifiers null. Detailed acquisition locators and originals are excluded.

GUI/OCR implementation stays local. This PR does not automatically merge into GitHub dev or move local dev. Nothing here is institutional approval.