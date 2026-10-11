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