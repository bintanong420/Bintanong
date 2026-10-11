# Independent specification recheck — five publication fixes

**Pinned final code reviewed:** `54f31f9113dddfb942b35022d40e38267a4daaaf` (scoped `407813c...HEAD` plus the prior two committed fixes). The initially reviewed content was `407813c1fad100bceb662a129d2c64321791bc8f` plus the ten reported dirty paths; root committed identical code in `ad931c4` and `54f31f9`. All eight recorded production/test content digests were independently verified unchanged after commits; the only remaining dirty path is the progress document. Also inspected the committed markup/prerequisite fixes `74d76ae` and `9f9a33b`. Approval attaches to the reviewed code and tests, including unchanged subsequent commits; LF-normalized SHA-256 digests for the four production owners and four affected test files are recorded in `spec-recheck-probe-result.json`.

## Findings

Confirmed defects: **NONE**. Unconfirmed suspicions requiring publication blockage: **NONE**.

All five previously confirmed defects are resolved:

1. **Markup hash:** staging supplies the captured `run_identity.pdf_sha256`. A JSON-only input still displays `not recorded`; its JSON digest is never presented as a PDF hash.
2. **Prerequisite state:** materialisation re-annotates every finalized course, including siblings affected by a code correction. Original `audit.structural_anomalies` remain input to annotation; ambiguous prerequisite ownership stays `unreadable` even after a text correction. No GUI `reviewed_empty` behavior was added.
3. **Persisted anomaly decisions:** both completion and old-value staleness enumerate the sheet/verifier's obligations through `placement.unclaimed_items`. Undecided, unresolved, wrong-PDF and stale-old-value anomaly decisions cannot produce `reviewed`. Accepted current decisions can; covered-anomaly and PDF-only policies remain shared with the existing owner.
4. **Corrected authority:** `build_authority` refreshes source, identity, review and prerequisite blockers. Top-level `content_review`, nested review state and authority review detail agree. Materialised artifacts always carry `eligibility_executable=False` and `derived_sections_stale`, including an unchanged candidate whose synthetic inherited source was verified. Pending source verification stays pending; corrections grant no source approval.
5. **Semantic identity:** `InputSnapshot` captures map bytes before loading, the metadata owner parses that capture, and `run_identity` records its same digest. Changed bytes with restored mtime, deletion and missing-map appearance reject publication and preserve prior files. A transient edit restored afterward cannot influence parsed metadata. An unchanged absent map still produces empty reference metadata and a null digest.

These changes satisfy the B/C/D provenance and completeness requirements without advancing the formal phase ledger, claiming extraction accuracy, implementing GUI/OCR, or completing pending human gates. Updated decision notes accurately describe the resulting behavior.

## Independent evidence

Executed `py -3.13 "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\spec-recheck-probe.py"` with bytecode disabled: **20 assertion scenarios passed, exit 0**. Scenarios: PDF/JSON markup (2), own/sibling/ambiguous prerequisite corrections (3), anomaly decisions (5), verified/pending source with changed/unchanged materialisation (4), semantic present/absent/change/delete/appearance/transient-restore (6). Semantic checks used actual `process_prospectus`, `build_payload`, staging, publication and verification; only the conversion boundary was substituted with a fixture document. Generated artifacts remain under external `spec-recheck-probe-a0d44377`.

No broad gate was rerun by this reviewer. Root subsequently reported fresh full-suite **1013 passed, 13 subtests, 5 warnings** and self-test **80/80** on this unchanged content; these are root-observed results, not this reviewer's independent reruns. The fresh comparer remains pending at this update. Focused implementer green counts were read as supporting evidence, not relabeled independent reruns.

**APPROVED — frozen content of all five fixes; confirmed findings NONE.**
