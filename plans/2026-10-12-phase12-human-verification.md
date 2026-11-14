# Phase 1–2 connected pipeline: human verification batch

Started 12 October 2026 at the owner's request. This is source-backed review preparation alongside Lawrence's independent later-phase verification. It does not reopen completed numbered software phases or start Phase 05.

## Scope and coordination

- Copy original PDF/PPTX documents from the supplied `Citizens Charter` and `Student Handbook and Constitutions` folders into `backend/bintanong_tools/bintanong_jsonifer_prolog/dataset/handbook_citizen_charter/`, retaining folder names and duplicate aliases.
- Preserve external originals, existing generated outputs, the owner's dirty `.gitignore`, and Lawrence's work. Do not merge review decisions or identify either reviewer as having approved anything without their recorded decision.
- Use original bytes as truth. Exclude old JSON/Markdown conversions, Python helpers and bytecode from the source copy. Generate fresh candidate bundles through the existing pending-source register, ingestion pipeline and checked bundle consumer.
- Keep institutional files ignored locally and raw evidence/generated review packets outside Git. The owner's existing backslash ignore entry is preserved; a valid forward-slash rule in `.git/info/exclude` protects the local dataset. It is machine-local and must be recreated on another checkout before copying documents there.
- No database writes, embeddings, executable Prolog, runtime services, release activation or institutional approval are part of this batch.

## Evidence locations and baseline

- Code baseline: `10bfd6f` on `dev`; initial working-tree change: `.gitignore` only.
- Separate evidence root: `E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/phase12_human_20261012_37f9e9e2/`.
- `copy_manifest.json`: all 15 originals copied, 9 distinct byte hashes, 52,937,795 bytes. Every original/copy SHA-256 matched immediately after copying. No existing different-byte destination was overwritten.
- Actual runtime: system Python 3.13.12, Docling 2.129.0, docling-core 2.97.1, docling-parse 7.20.0, pytest 9.0.3, Pydantic 2.13.4, pypdfium2 5.9.0. Declared dependency pins differ; no install/sync/lock change is authorized or needed for this evidence run.

## Verification steps

1. Inspect copied originals with the existing read-only inventory tool: health, pages/slides, text-layer class, duplicate identities and path accessibility.
2. Run relevant governance/contracts/evaluation and candidate-ingestion tests on system Python 3.13, disabling pytest cache and using external basetemp.
3. Convert each unique original with recorded installed settings, offline existing assets only, into separate new output folders; independently call `load_candidate_bundle` on each completed result. Keep converter failures and chunk/item/table rejections explicit.
4. Prepare an external review packet linking original page images, candidate text, exact source hashes/locators and ingestion findings. Prepopulate only machine evidence; leave human decisions and reviewer names blank.
5. Record measured results here and in current progress; verify original/copy hashes again. Commit only curated documentation (and a narrowly justified fix if a reproducible defect requires one).

## Human review and acceptance

Human decisions distinguish source authority/version/scope from extraction fidelity. A content check does not establish issuing-office authorization. Compare the original rendered page against candidate text and table association; record accepted/corrected/unresolved, reviewer, date, reason and source locator. Check negation, requirements, exceptions, thresholds, fees, dates and complete ordered steps. Resolve conflicts between editions through source-owner evidence, never filename recency.

This batch is independently namespaced. Lawrence may review the same source bytes, but his later-phase results remain separate until both reviewers explicitly reconcile specific findings. Disagreements are retained for adjudication. No final accuracy percentage or OCR character error rate is valid without an independent manual reference. The ten scanned-document/real-photo benchmark and formal final Taglish cases remain separate gates.

## Measured results and owner clarification

The owner clarified that THEY perform human verification and need run instructions plus a per-file checklist before choosing the next run. [Run instructions and checklist](2026-10-12-phase12-human-review-checklist.md) now govern that interaction. The automatic conversion batch was stopped; no batch Python processes remain. No human verdict was assigned by the agent.

- Read-only inspection: 15 healthy paths, 9 unique byte identities; 0 inaccessible paths, 0 page-accounting invariant violations. The unique PDFs have 17, 21, 34, 117, 361, 394 and 643 pages. Three contain scanned pages. Text-layer classes are heuristics, not content acceptance.
- Automated connected-boundary gate: 2,589 tests passed, 0 failed, 3 dependency deprecation warnings in 138.82 seconds. Exact reproduction command and test selection are in the checklist; raw output is `pytest.log` externally. No full repository, database, runtime or model-accuracy test is claimed.
- Pending-source register: nine byte-derived versions, all 15 acquisition locators retained; verification/content/scope/effectivity pending, no approvals.
- Both distinct Charter PPTX variants completed conversion and checked-bundle consumption: each has 52 raw text items and 15 raw tables; all withheld under the pending slide locator/table contracts, zero chunks. Markdown export additionally reports out-of-bounds slide geometry clamping; it is a convenience projection, not repaired provenance.
- The 17-page Charter PDF fresh trial failed after conversion at `read_procedure_items` → `_reading_refs`: `ValueError: raw reading order omits text or tables`. No completed bundle was published. The following election-code trial was interrupted while stopping the batch. All remaining files are explicitly not converted.
- External human packet: two readable raw PPTX Markdown files and `human-review/decisions.csv` with 45 pending axis rows, blank reviewers/dates/corrections/authority evidence. Source-derived text stays outside Git. A scratch runner initially supplied a path as `filename`; the plain-filename contract rejected it before conversion, then the runner was corrected to use the basename. No production code was changed.
- Final integrity check: all 15 external originals and all 15 repository copies still match their captured SHA-256 hashes. No dependencies/models were installed or downloaded; no protected source or Lawrence artifact was changed.

## Next action

Owner runs or opens one prepared output, follows the per-file checklist and reports an accepted/corrected/unresolved finding with source hash and exact location. Preserve the PDF failure for a subsequent focused reproduce/fix/regression task; do not bypass completeness or claim readiness from synthetic tests. No broader conversion or human review is pending on an agent process.
