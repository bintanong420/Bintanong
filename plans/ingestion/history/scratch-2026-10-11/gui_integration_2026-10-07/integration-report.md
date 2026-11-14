Next: owner decides whether to fast-forward dev; no dev movement has been performed.

Integration tip: cf8b11c566d76bd5048a761a169907aee31a242b (integration/gui-0710, clean).
Owner dev: 5c34fd73adbd2806d6c48362eb248b74921fb79c, unchanged.
Nothing here is institutional approval.

| Gate | Expected | Fresh actual |
|---|---|---|
| a main venv | 1259 passed + 6 skipped | 1259 passed, 6 skipped, 13 subtests passed, 4 warnings; exit 0 |
| b web venv | 266 passed | 266 passed, 1081 deselected, 3 warnings; exit 0 |
| c self-test | 80/80 | 80/80; exit 0 |
| d comparer vs 5c34fd7 | 44/44 identical; only package_sha256/run_key change | 44/44 identical; exactly those two run_identity fields changed across 44 payloads; exit 0 |
| e B2 | mixed21/warnings_only3/broken19/clean1; title67/strip0/unclaimed316/banner3 | 21/3/19/1; 67/0/316/3; exit 0 |
| f trial sheets01/16/33 | 0 check_against errors | 0 each; parse/build errors also 0; exit 0 |
| g diff + attribution | diff-check0, trailers0 | both0; integration equals GUI tree; 107 source/cache/trial hashes unchanged |

Spec review: 2 Medium defects, 1 Low wording ambiguity, no High. Medium: section-confirm PDF hidden (session.py:131, static/review.js:168); prerequisite twin marks/scrolls code rather than prerequisite (static/review.js:206). Low: older D11 any-field exemption conflicts with intentionally separate Task10 prerequisite decisions; unresolved prerequisites survive and still block full content review. No code fixes/recheck in this merge batch.
Standards review: 1 Medium documented-standard breach: transport failure leaves Save/write-corrected without visible error (static/review.js:32,279,316); no High. Separate concurrent-materialisation suspicion UNVERIFIED, no corruption reproduced. See separate review-spec.md / review-standards.md. Browser/Lighthouse are NOT RUN.

## 1. COMPLETED (merged in dev 5c34fd7 unless noted; with evidence)

1. A package split and B markup twin: both branch tips are ancestors of dev. Fresh current integration regression: 44/44 course fields identical vs dev and self-test80/80. Original A 44/44 +80/80 and B 44/44 phase-era gates: UNVERIFIED as fresh historical runs; recorded by owner's status.
2. B2 verifier/fixer: branch is an ancestor of dev; current triage and read-only sheets pass above. Code completion is recorded in owner's ledger; Tasks12-14 remain owner gates. C status separation: branch in dev; schema v3.1 verified from C tip, current prerequisite counts unchanged. Historical last Codex gate NONE: UNVERIFIED independently this batch.
3. D safe cache/publish: branch in dev, schema v3.2 verified from D tip. Historical independent-review approval: UNVERIFIED independently this batch; owner's ledger reports it. Stale decision-record header remains an owner decision.
4. Previous integration into dev5c34fd7 is verified by Git ancestry. Its historical 1040 passed+1skipped,44/44,unchangedB2,0trailers report: UNVERIFIED as fresh historical gates. Fresh GUI integration gates a-g above are verified; dev is unchanged.
5. Review GUI Tasks1-11 plus review fixes: GUI61d251d clean, contains dev, merge tree equals GUI, NOT yet in dev. Current independent Spec findings above have no High; historical Task10/11 reviews noHigh UNVERIFIED independently. Historical real-data evidence for copies01/13/16/33: 17 before/after originals hashes equal; 16 ledger-equivalence JSON confirms 9/9 entries differ only via/entry_id, corrected candidates equal under Task4 comparison (bytes differ only applied_entry_ids). Fresh107 original hashes also unchanged. Human/browser trial not claimed.

## 2. IN PROGRESS / MIDDLE

1. GUI integration/gui-0710: merged clean at cf8b11c; all a-g gates green; Both reviews complete: Spec2Medium+Lowambiguity; Standards1Medium; no High. All three Medium findings and Low wording ambiguity remain open. Browser pass and Lighthouse audit NOT DONE (Task11 steps6-7).
2. OCR measurement: branch in dev verified; about50% is owner's estimate, UNVERIFIED as a measured percentage. Remaining:4b Docling payload chain,4c bench,Q16 confidence matching,question-style review adapter,edition matcher,real-data gates,decision record,owner's real phone photos.
3. Master Phase2: only prospectus slice worked according to ledger. Handbook,Citizen's Charter,USG/CSG ingestion,10-document scanned OCR check,document inspection have no plan yet; implementation completeness UNVERIFIED beyond ledger inspection.

## 3. PENDING: READY AND WAITING FOR THE OWNER'S SIGN-OFF

1. Owner must authorize dev fast-forward to integration/gui-0710; no push/history rewrite/dev movement performed. Recommendation: hold dev while owner considers all three recorded Medium findings and browser/Lighthouse checks. Current account usage percentage UNVERIFIED.
2. Owner's B2 Task12 trial: review_trial_2026-10-04/HOW_TO_REVIEW.md; GUI Task12: owner's GUI trial. Re-extract scratch trial candidates with PhaseC so real trial includes prerequisite questions.
3. Task13 banner split branch exists, owner go/no-go after trial; reported effect1title,54courses gain discarded_fragments,banner_leak3->2 is UNVERIFIED as fresh branch comparison. B2Task14 closeout follows trial and Task13 decision.
4. Owner decisions: content_review_state reviewed with59PDF-found unclaimed questions still open on13 (pre-existing sheet semantics); prerequisiteNo keeps partially_reviewed; firstquestion~11s torchimport is not a gate; stale D header hashes; owner push timing; CI matrix and Linux/macOS (onlyWindows run). Historical59/11s claims are from saved Task11/progress evidence, not new measurements. Also resolve D11 bulk/prerequisite wording ambiguity. No curriculum/source approval granted.
5. NOT STARTED, await owner's order: E provenance/schema3.3 fromdev (Prompt4), F toolsCLI/Docker/CI, masterPhase1 source manifest/contracts withPhase2prep. Formal Phase1 preparation does not authorize Phase2 advancement.

Evidence directory: E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\gui_integration_2026-10-07
Atomic pickup/checkpoint and logs provide takeover state. Main owner's untracked status sections3/8 updated only; not committed. Temporary baseline worktree removed; all unfinished worktrees retained; no dependencies installed/synced.