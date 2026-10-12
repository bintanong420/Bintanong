# Phase 05 source-backed development practice exam — 12 October 2026

The requested small development practice exam is delivered as a candidate question sheet, answer key and machine-readable packet. Answers were manually read from the original PDFs and checked against full-page and row-detail renders. Source bytes were freshly hashed and matched the preserved provisional inventory. This proves a reproducible source-reading exercise, not institutional authority or model retrieval quality.

## Artifacts

Persistent external root: `C:/Coding-projects/bintanong_workspace/audit-evidence/p05-dev-exam-20261012`.

- [Question sheet](</C:/Coding-projects/bintanong_workspace/audit-evidence/p05-dev-exam-20261012/exam/questions.md>)
- [Answer key and original-source links](</C:/Coding-projects/bintanong_workspace/audit-evidence/p05-dev-exam-20261012/exam/answer-key.md>)
- [Machine-readable candidate packet](</C:/Coding-projects/bintanong_workspace/audit-evidence/p05-dev-exam-20261012/practice-exam.json>)
- [Source validation result](</C:/Coding-projects/bintanong_workspace/audit-evidence/p05-dev-exam-20261012/exam/validation.json>)

Gold answers/passages, rendered originals, inspection crops, inventories and logs now remain untracked in ignored workspace evidence folders on the owner's later location instruction; initial delivery used AppData to satisfy the earlier outside-Git rule. The first audit-evidence destination was found inside an unrelated `C:/Coding-projects/.git` root; only this task's newly created artifacts were moved to AppData after exact source/destination checks, then moved back into the owner-selected workspace. The root and links above identify the current location. Existing original PDFs and earlier evidence were preserved. No gold passages or actual-source answer key are committed.

## Coverage and sources

12 cases, eight scenario families, four English/four Filipino/four Taglish. Nine source-answerable cases, one curriculum clarification, two insufficient-evidence controls. Categories: prerequisites5, enrollment2, academic standing4, grades1; discipline is not covered. Language paraphrases and edition variants remain in their scenario family, all in dev; no final-set tuning.

Two one-page BSCS prospectuses: the printed Effective SY2018-2019 sheet and the explicitly proposed2025-2026 program of study. The proposal is never presented as approved/current policy. Native Windows.Data.Pdf was used without installing a renderer or Python package; full-page/critical row render artifacts were visually inspected. The helper's initial async-action binder failure was corrected for rendering, and its nonzero process exit is not counted as a verification pass. Successful PNG outputs/metadata and visual inspection, not helper exit status, support the source reading.

Both sources are physical PDF page1; the proposed sheet prints page50 and the older sheet prints Page1 of1. Case evidence records edition/version/hash, semantic row/column locator, conservative PDF-point bbox, printed label and a manually transcribed excerpt digest. Table separators are added for readability. Unsupported cases have background evidence describing the bounded sources examined, not invented supporting policy. Wrong-program scope records the explicitly requested BSIT with unknown edition; the BSCS source remains background only.

| Source | Fresh original SHA-256 | Inventory governance |
| --- | --- | --- |
| Proposed2025-2026 BSCS PDF | `600cb36b362cff598d84c66a11598b07593c0e74e78a62658b3c61c89f5d5664` | pending |
| Effective SY2018-2019 BSCS PDF | `c781052fc7242ba520410910f171379721e9bfd0c695b2f0094a3e3981641e4d` | pending |

| External artifact | SHA-256 |
| --- | --- |
| `practice-exam.json` | `04f7d3c5d5c793ef8a8aaf7c272690aa0757adb49ee775f30120977cdc55e096` |
| `exam/questions.md` | `752032c10141629794b34cbeb13f7d2f56722153f5fc624c927d1187b12ad7eb` |
| `exam/answer-key.md` | `9c48a3ce898904399574d28e2a642d9c9ee77809325773a59c67130cb594159d` |
| `exam/validation.json` | `f2ff5e4c901b60f239afc09ac6609eb5a17f5bedd4102d0f7bf46a6ed0592ca5` |

## TDD and fresh verification

Verified code tip `2a497c4`; planning `f7534c8`, validator/grader `4eedfb6`, CLI/readme `1fb9d1b`, linked-output fix `2a497c4`. No push, merge or shared database migration.

Missing-module and missing-CLI-function RED observed before implementation. Additional primitive-citation RED caught bool/float page equivalence and an unhashable locator; exact source-citation primitives now fail grading safely. Final/Git-root/stale-grade/output-hardlink cases also observed RED before fixes. Tests use invented source bytes, answers and metadata, with temporaries outside Git.

| Command / verification | Result |
| --- | --- |
| New practice-exam suites (`tests.test_practice_exam`, `tests.test_practice_exam_cli`) |21 passed0.234s, exit0 |
| Final combined new suites plus query/context/engine/CLI/evaluation retrieval units |43 passed0.241s, exit0 |
| `python -m unittest discover -s tests -p 'test_embedding_*.py' -v` |12 passed0.159s, exit0; existing Starlette/httpx warning |
| Phase-state unittest suite |19 passed12.177s, exit0 |
| Fresh reviewer correction rerun |9 CLI tests passed0.179s; no remaining P1/P2 |
| Actual external packet CLI validation/export |12 cases,2 byte-verified originals,8 groups; exit0; grading null |
| Original hash recheck against provisional CSV |Both match; pending governance preserved |
| Full `test_retrieval_*.py` DB-inclusive rerun |Attempted; two fixture failures because Docker Linux-engine named pipe/daemon is unavailable; not a fresh passing DB gate |

74 relevant unit/regression tests passed in this work (43+12+19). Database/storage code is unchanged. Existing Phase05 DB passes are historical; do not substitute them for the unavailable rerun. No containers started, installs, dependency/lock changes or real model execution. System Python3.13.7; the new checker uses the standard library only. pytest remains unavailable, so unittest suites were used without installing it.

The grader separates fixed-key answer, control and exact source agreement; a right answer with a wrong edition/page/row fails, comparisons require both editions and missing responses fail. Grading accepts only explicitly authored answer variants with NFC/case/whitespace normalization; it is not a semantic prose judge. Output refuses all Git roots/worktrees, protected inputs and existing symlink/hardlink destinations. Stale grading files cannot accompany an ungraded export.

## Review and limits

Fresh review confirmed both full pages and seven detail images against answer/source labels, proposal/effective wording, physical/printed pagination and bboxes. One P2 output-hardlink bypass was reproduced in temporary synthetic fixtures and corrected with preflight rejection before writes; both preservation regressions pass and re-review is clear. Real originals were never mutated.

The candidate packet still has independent policy/domain review pending. Visual agent checking does not authenticate source authority or approve institutional applicability. The checker validates authored page/coordinate/locator metadata and byte/excerpt integrity; it does not parse PDF text or automatically prove an expected answer. Semantic row locators must be mapped to production ingestion span/cell identities before live retrieval scoring.

No actual retrieval responses, answer-key replay score or fabricated observations were generated. `grading` is null and no `grading.json` exists. Real matching SEA-LION execution, independently approved development labels/source applicability and actual runtime evidence recovery remain pending. Phase05 stays active; this report does not authorize Phase06 or activate candidate knowledge.
