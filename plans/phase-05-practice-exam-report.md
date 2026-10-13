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

## Owner-approved balanced college expansion and workspace correction

The owner selected27 questions, balanced three per each of CAD, CAH, CBA, CCJE, CHTM, CNHS, CoE, CS and CTE, using Superpowers bounded-design/TDD/review/verification workflows. There is one English, one Filipino and one Taglish question per college.26 scenario families remain entirely in dev; both Architecture design questions share their family. The prior12-case version is preserved rather than expanded in place.

Current artifact root: `C:/Coding-projects/bintanong_workspace/audit-evidence/p05-college-expansion-20261012`.

- [27-question sheet](</C:/Coding-projects/bintanong_workspace/audit-evidence/p05-college-expansion-20261012/exam/questions.md>)
- [Answer key with original-source links](</C:/Coding-projects/bintanong_workspace/audit-evidence/p05-college-expansion-20261012/exam/answer-key.md>)
- [Candidate packet](</C:/Coding-projects/bintanong_workspace/audit-evidence/p05-college-expansion-20261012/practice-exam.json>)
- [Validation](</C:/Coding-projects/bintanong_workspace/audit-evidence/p05-college-expansion-20261012/exam/validation.json>)
- [Dataset location and relocation guide](dataset-locations.md)

Fresh inventory:39 PDFs with39 distinct byte digests across nine college folders. One inspected program per college supplies the exam; this is college-folder coverage, not exhaustive program/policy coverage. Ten originals are used because CS has two editions.25 answerable, one curriculum clarification, one wrong-program source control. Categories: prerequisites11, enrollment13, corequisites1, source_scope1, academic_standing1. Grade-cutoff and discipline policies remain unmeasured by this balanced set; the archived12-case set retains its bounded grade-absence control.

Original pages and selected row crops were visually reviewed. Nursing uses physical/printed page1of2. HRM PDF has two physical pages but its first sheet prints Page1of1; the page labels are retained exactly. No questions depend on its uninspected second physical page. All other new-source questions use physical page1 with printed Page1of1. CS proposal prints50 and remains explicitly proposed. A Criminology row marks a co-requisite, not a completed prerequisite; its printed spelling is preserved in the manual excerpt. Native renderer nonzero exit after emitting images is recorded as a limitation, never a passed executable gate. Source hashes/byte validation and manual image checking support the reading; no PDF text parser or institutional authentication is claimed.

The original deep dataset root has not moved. Both exam versions and this task's earlier disposable-database evidence moved into workspace audit-evidence after the owner required all work under `C:/Coding-projects/bintanong_workspace`. The main code checkout is `Bintanong`; implementation stayed in `worktrees/Bintanong/p05`. The unrelated Coding-projects ancestorGit marker observed earlier is absent on final inspection; no Git metadata was deleted by this agent. Each task folder still has preventive `.gitignore: *`. Gold data and original PDFs were never staged.

Verified commits: `e1ea578` adds college validation/reporting and the location guide; `317bf54` applies the owner location correction and explicit ignored-output export. The latter retains default Git-root rejection and requires every output to be ignored in every containing repository when opted in. Inputs, links and stale grading remain protected. Project-specific source locations are documented in AGENTS/INDEX/this guide, where the existing handoff skill discovers them, rather than editing a generic skill.

TDD: ten synthetic-college tests observed missing coverage/reporting RED before implementation; three realGit private-output tests observed missing-option RED before implementation.34 exam tests now pass. Committed fixtures contain invented sources/answers only.

| Fresh command / verification | Result |
| --- | --- |
|34 exam tests plus22 retrieval query/context/engine/CLI/evaluation units |56 passed1.352s, exit0 |
| `python -B -m unittest discover -s tests -p 'test_embedding_*.py' -v` |12 passed0.269s, exit0; existing Starlette/httpx warning |
| `python -B -m unittest discover -s .agents/skills/bintanong-phase-handoff/tests -v` |19 passed19.347s, exit0 |
| `python -B -m unittest discover -s tests -p 'test_retrieval_*.py' -v` |29 passed34.949s, exit0, including7 disposable-DB checks |
| Fresh independent agent reviews | No P1/P2;31 then34 exam checks independently passed, source rows/boxes and both moved packets checked |
| Final source validation/export/manifest recheck |27 cases/26 groups/10 originals; every college balanced, exports match packet, original12 four hashes unchanged, no answer leakage or grading |

94 distinct relevant automated checks pass (56+12+19+7 DB checks beyond the already counted22 retrieval units). Docker became externally available; no Docker startup was performed. Latest test temporaries/raw evidence are inside the workspace folder. This supersedes the prior unavailable-Docker attempt, while all earlier results above remain historical. The whole repository pytest suite was not run; pytest is unavailable and no dependency installs were authorized. Database/storage production code did not change.

Raw final logs: `unit-regressions.log`, `embedding-regressions.log`, `ledger-regressions.log`, `full-retrieval-gate.log` in the artifact root. Latest synthetic DB evidence is under `tmp/bintanong_storage_test_f1c033e361294151afab85b9ea2808ec`. `delivery-manifest.json` records all original source paths/hashes, inventory and unchanged archival digests.

| Balanced artifact | SHA-256 |
| --- | --- |
| `practice-exam.json` | `3c016d5214f2045d84c4c27eadd817051b66ada06ff33a5a7c4d41c8dfb2fca2` |
| `exam/questions.md` | `508c5453ae19f321e506cbb22214b2f523ca73a951a4b1a3724841562af529c0` |
| `exam/answer-key.md` | `b21055eac25f5bf826f744e53bf905085fca3f16fb766a0bf844608d00766ec6` |
| `exam/validation.json` | `c3df1899dec07792035e9c63f377fc5eef4c621a662deea8531b0bc39c9acad2` |

| Original source ID / college | SHA-256 |
| --- | --- |
| `src-cad` / CAD | `72dad4a0384f82228d63c8926e4ae8a1eb14a33497c9952e0f60782083e82666` |
| `src-cah` / CAH | `998a83c0c0a64dbe90552e6212a73e017ea5d4d08def617589ca51ffc07fc14f` |
| `src-cba` / CBA | `10d415d041e9b35e6b264789c78b9868ab1059fea1fbfecb290eaf0a9c92ae16` |
| `src-ccje` / CCJE | `b3b43dece33b171af81fdc738da45864f204188b068d66a180b670270f36a2d3` |
| `src-chtm` / CHTM | `7186c5428945363aaa063c68971a9f8b280ede361945574566ab7c86c8e452eb` |
| `src-cnhs` / CNHS | `f1e01951f1a2a034128e09db9f730107cb524ea61a152be9bb918b08ff279603` |
| `src-coe` / CoE | `7af0f48f75e7ce2bd2015699bba6e5af90a85c251fa2e9a0ee9ffb2d172de99b` |
| `src-cte` / CTE | `f98e9b4436f225a2d5a09ecefdeb5c2d913a3f6f054fd0a7bc0fb72fe6b491a0` |
| `src-bscs-new` / CS | `600cb36b362cff598d84c66a11598b07593c0e74e78a62658b3c61c89f5d5664` |
| `src-bscs-old` / CS | `c781052fc7242ba520410910f171379721e9bfd0c695b2f0094a3e3981641e4d` |

Fresh agent review checks source reading; it does not replace institutional/domain approval. Both packets remain candidate, source_approval not_claimed, and have no grading.json or real observations. Independent source applicability/answer approval, semantic locator-to-ingestion mapping and actual matching SEA-LION/runtime retrieval remain prerequisites for master section10. Phase05 formal exit stays blocked; no Phase06, release activation, shared migration, push or merge.
