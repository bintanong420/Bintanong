# Phase 2 workstream status and publication scope

Snapshot: 7 October 2026, Asia/Manila. Repository state and fresh verification outrank this snapshot. Nothing here is institutional approval.

## Published completed prospectus sub-phases

Completed A–D code is published on `publish/prospectus-a-d-20261007`, reviewed production tip `54f31f9`, publication tip `3227ac8`, [PR #2 targeting GitHub dev](https://github.com/bintanong420/Bintanong/pull/2). At this snapshot the PR is open/unmerged; local dev `5c34fd7` is unchanged. This publication excludes GUI/OCR implementation and includes their plans. The immutable [master plan](master_implementation_plan_original_long.md) and [prospectus implementation plan](2026-09-26-prospectus-phase2-implementation-draft.md) are included.

| Completed code | Governing plan and evidence |
|---|---|
| A: package split | [Phase A plan](2026-10-03-prospectus-extractor-package-split.md); 44/44 course-field preservation and self-test 80/80 |
| B: PDF/markup twin | [Phase B plan](2026-10-03-prospectus-phase-b-markup-twin.md); 44/44 course-field preservation |
| B2: verifier/fixer code | [Phase B2 plan](2026-10-04-prospectus-phase-b2-section-fixer.md); code built, owner Tasks 12–14 gates remain open |
| C: status separation | [Phase C plan](2026-10-03-prospectus-phase-c-status-separation.md); schema v3.1, distinct audit/content/source states |
| D: safe cache/publication | [Phase D plan](2026-10-03-prospectus-phase-d-safe-cache.md), [handoff](prospectus-phase-d-handoff.md); schema v3.2, reviewed corrections below supersede the historical header tips |

Publication verification on reviewed production code: system Python 3.13 comprehensive suite **1013 passed, 13 subtests passed, five dependency warnings**; self-test **80/80**; comparer versus local dev `5c34fd7` **44/44 course fields identical**, only package digest/run key change; Phase C prerequisite counts unchanged. B2 triage: mixed 21, warnings_only 3, broken 19, clean 1; title_from_pdf 67, strip_banner 0, unclaimed_code 316, banner_leak 3. Trial sheets 01/16/33: zero check_against errors, all 19 trial-folder files byte-identical before/after. Diff check passed; outgoing attribution matches zero. Separate Spec and Standards rechecks approved with no remaining findings. Logs and exact command output remain external.

Five confirmed correctness fixes precede publication: captured PDF hash passed to markup, all materialised prerequisites reclassified, persisted structural anomalies included in review completeness, derived authority made non-executable and recomputed, and semantic-map bytes captured/guarded consistently. Progress and decision records preserve the red/green evidence; earlier task counts and branch headers are historical evidence, not current tips.

## Local implementation and remaining queue

| Workstream | State and next work |
|---|---|
| GUI | Tasks 1–11 and prior reviews exist at local `61d251d`; integration baseline `cf8b11c`. New local fixes address section PDF visibility, prerequisite-cell focus and save-status-unknown failures; full/review/browser gates determine readiness. [GUI plan](2026-10-05-prospectus-review-gui.md) is published; implementation is excluded from this publication |
| E | [RAG provenance plan](2026-10-03-prospectus-phase-e-rag-provenance.md): start from local dev and merge the reviewed GUI candidate locally; schema v3.3, stable IDs, printed source text/spans, rejections/omissions, unanchored cache handling; no embedding or vector writes |
| F | [Tools/CLI plan](2026-10-03-prospectus-phase-f-tools-cli.md): start from reviewed E; provisional source/root adapters, candidate manifest, single/folder commands, container/offline gates; approval remains null |
| OCR | Foundation remains local; [measurement plan](2026-10-04-prospectus-ocr-measurement.md) is published. Remaining payload chain, benchmark, confidence, question adapter, edition matcher and gated accuracy measurement; upgrade from reviewed post-F interfaces without replaying existing commits |

Obsolete E/F snippets are corrected by explicit implementation rulings: reuse Phase D's captured identity, do not independently hash before/after; estimates cannot guarantee embedding token limits; actual Phase C states are required; LF output needs byte verification. Preserve the plans and their historical measurements. Detailed progress is in [extractor_split_progress.md](plan_current_progress/extractor_split_progress.md).

## Whole Phase 2 preparation and sources

The prospectus slice does not complete formal Phase 2. [Phase 1 source-governance/contracts plan](phase-01-source-governance-contracts-plan.md) is ready/preparation-only; active phase remains unset. [Remaining Phase 2 preparation](phase-02-document-ingestion-preparation.md) covers document inspection, Handbook/Charter/procedures/USG/CSG ingestion, policy chunking/reports and the separate ten-scanned-document evaluation. [Evaluation protocol](../evaluation/README.md) separates development from final families and targets 50 verified final Taglish cases; final verification is pending.

External acquisition completed: **78 paths, 59 PDFs, 17 JPGs, two PPTXs; 63 unique byte identities, 13 duplicate groups, 15 additional duplicate paths**. All 78 copies and 156 independent source/destination hash checks passed. The five selected institutional folders are preserved; longest destination path is 220 characters. The detailed source locators/digests stay in the external inventory. Byte verification establishes copy integrity; institutional source verification is pending, approval IDs and authorization evidence are null. Preserve both Handbook editions and differing Charter PPTXs; misfiled BOR proposals remain proposal candidates. CSG coverage is missing. The targeted duplicate prospectus dump is recorded only as an existing comparison copy.

## Owner and external gates

- GitHub dev merge requires explicit owner authorization; no automatic PR merge or local dev movement.
- Human GUI/B2 trial, banner-split go/no-go and final closeout remain pending. Earlier scripted equality checks are not the human verdict.
- Source scope/effectivity/supersession, conflict resolution and institutional activation require authorization evidence, which has not been supplied.
- Real phone photos and reviewed fixed references gate supported-photo OCR accuracy and production integration. Tool completion cannot substitute for those measurements.
- Browser/Lighthouse, containers/offline and Linux/macOS checks remain NOT RUN until actual evidence is recorded; the prospectus photo benchmark cannot substitute for the separate ten-document OCR check.

Next: finish local GUI verification/reviews, then execute E → F → OCR tooling while preparing formal Phase 1. Formal Phase 2 starts only after the required complete Phase 1 handoff and advancement check.
