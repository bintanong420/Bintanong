# Phase 05 next-CLI handoff — policy sources and dataset organization

This is a developer continuation note, not a complete phase handoff. Phase 05
remains active; Phase 06 has not started. Use Git and fresh checks over old notes.

## Start here

Worktree: `C:/Coding-projects/bintanong_workspace/worktrees/Bintanong/p05`.
Branch: `feat/p05-retrieval-logic`; main checkout: workspace `Bintanong/`.
Read `AGENTS.md`, both repository Bintanong handoff skills, `plans/INDEX.md`,
`plans/phase-05-checkpoint.md`, current progress and the blocked Phase 05 handoff.
The updated loop also requires `Context/`: inspect the runtime routing PNG and
read relevant thesis pages. Physical pages 36, 55 and 68 establish institutional
RAG sources and isolation of supplemental user inputs. Master sections 6, 7 and
10 govern source recovery, ingestion and retrieval; section 11 governs Prolog.

Then read `plans/2026-10-12-policy-source-recovery-plan.md` and
`plans/dataset-locations.md`. Run the existing phase-state inspector, compare
HEAD/status with the checkpoint and preserve owner or other-worker changes.

## What the owner decided in this CLI

1. Continue Phase 05 from a previous account and use TDD for product changes.
   Repository instructions now explicitly require relevant skills and RED/GREEN.
2. Prospectus source review is deferred for Phase 06 curriculum preparation.
   The 27-case packet is retained; it is not the current owner review task or a
   replacement for the handbook/Charter retrieval benchmark.
3. Phase 05 prioritizes handbook, university Charter and policy retrieval.
   Explicit source conditions may later support Prolog, but executable rules are
   Phase 06. Preserve RAG/Symbolic/Hybrid separation and cited evidence.
4. The owner supplied university Charter and handbook PDFs and authorized their
   organization by category and printed edition year. Preserve prospectuses.
5. Keep 2024–2027 folders for older public materials and future updates; additional
   real edition years and `UnknownYear` are valid. Keep existing editions rather
   than replacing them. Directory year alone does not establish active policy.
6. College-specific Charter photographs and organization policies are future,
   deferred inputs. They may arrive later; not all college Charters are available.
   Their absence does not block supplied university-wide source preparation.
7. Dataset files must be ignored. Plans, decisions and handoffs remain in Git;
   raw inputs, inventories, conversions, vectors and logs stay ignored locally.
8. Consult `Context/` on phase start/resume, rollover and another CLI/account.
   Work in recoverable increments under the owner's usage limits.

## Exact current dataset

Root:
`backend/bintanong_tools/bintanong_jsonifer_prolog/dataset/` in this worktree.

```text
dataset/
  PalSU Undergraduate Prospectus Website Dump/   # unchanged
  CitizenCharter/
    2024/University/
    2025/University/PALAWAN-STATE-UNIVERSITY-Citizens-Charter-2025-4th-Edition.pdf
    2026/University/
    2027/University/
    UnknownYear/University/
  StudentHandbook/
    2021/PSU Student Handbook.pdf
    2024/  2025/  2026/  2027/  UnknownYear/
  Memoranda/
    2024/  2025/  2026/  2027/  UnknownYear/
  Deferred/
    CollegeCitizenCharter/
    OrganizationPolicies/
  README.md
  _source-catalog.json
```

Only the two loose policy PDFs moved. All 42 original files retained identical
bytes. The prospectus subtree contains 39 PDFs and its inventory CSV: all 40
paths/hashes unchanged. No memorandum or deferred-source files were supplied.
The dataset README explains safe additions, photo ordering and same-year editions.

| Source | Original SHA-256 | Observed edition and limits |
| --- | --- | --- |
| University Charter | `42a93994e1467df0f32c7038d1c21f638c23ac0f1dee984463acf56caf526529` | Cover visibly 2025, fourth edition; 117 physical pages. All pages have some PDF text; page69 is sparse. Contains nonstudent services too; scope must be reviewed. |
| Student handbook | `4c9a95bf6895ddba75a997a37fa069644ac081dd7ab4a43f882496db834351c8` | Image cover visibly 2021; 394 physical pages. The printed BOR approval is2020-11-11/Resolution104 series2020, distinct from edition2021. Physical page1 has no PDF text; other pages do. |

These are observed source properties, not issuing-office verification, effective
dates, current applicability, content accuracy or OCR measurements. Acquisition
URLs/source provenance remain missing; record the owner's public source/office
evidence when available. Both new SourceDocumentVersion records are real bytes,
`synthetic:false`, all states pending, `approval_id:null`.

## Source governance and ingestion recovery

Historical Phase 1–2 plans already name handbook/Charter files at an external
`E:` location and deliver governance/ingestion software. The earlier local drive
was unavailable in this CLI; do not assume old paths or manifests match the newly
supplied bytes. `plans/ingestion/CURRENT_STATUS.md` explicitly records that actual
handbook/Charter completed bundles were unproved. Recover this input/evidence
gap; do not restart closed software phases or assert the earlier source task was
verified merely because the numbered phase was closed.

Reused interfaces, inspected from current code:

- `document_ingest.register.pending_version` / `load_pending_register`.
- `document_ingest.pipeline.run_ingestion(snapshot, register, input_root=..., out=..., classification=...)`.
- `document_ingest.bundle.load_candidate_bundle` for complete identity/report checks.
- CLI: `python -B -m backend.bintanong_tools.document_ingest --help`.
  `--root`, `--out`, `--locator` and `--classification` are required for a run;
  Charter uses `charter_candidate`, handbook uses `policy_candidate`.

The current standard policy path accepts PDF/PPTX, not raw JPG/PNG. Separate
`document_ingest/ocr_run.py` is gate-only and requires verified local Tesseract
assets; image-to-policy integration/readiness must be checked when memorandum
or college photos arrive. Do not download OCR models or assume the five approved
Docling layout/table assets authorize any additional downloads.

## Environment and evidence locations

Approved isolated Python3.13:
`C:/Coding-projects/bintanong_workspace/audit-evidence/p05-real-retrieval-readiness-20261012/venv/Scripts/python.exe`.
System Python is3.13.7. Existing resolved packages/assets are already installed.
No package/lock changes or new installation is authorized by organization.

Reuse the readiness directory's `hf-cache`, `docling-cache`, `docling-artifacts`
and `tmp`. Set `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `HF_HOME`,
`HF_HUB_CACHE`, `DOCLING_CACHE_DIR`, `DOCLING_ARTIFACTS_PATH`, TEMP/TMP to their
existing workspace locations before conversion. Existing SEA-LION/GEMMA weights
stay strictly at `C:/Coding-projects/MODELS`; no new download or copy.

Organization evidence:
`C:/Coding-projects/bintanong_workspace/audit-evidence/p05-dataset-organization-20261012/`:
before/after inventories, move journal, source cover images, policy text profile,
`policy-pending-source-register.json`, verification summary and test-count report.
Do not modify old sealed readiness or extraction-recovery evidence.

## Previous verified work — do not repeat

- Retrieval module, scoped SQL/RLS checks, strict encoder and citation/context
  logic already exist. Candidate retrieval software is not the current blocker.
- Commit`280a287` fixes repeated curriculum row projections with five synthetic
  regressions. Financial Management now matches printed146units/49courses and
  emits54newcandidate chunks. Other38prospectus results unchanged.
- Latest prospectus mixture:32auditerrors/7warnings/390chunks and real vectors;
  historical336vector/27query diagnostics preserved. Only3exam cases have matching
  chunks; these are prospectus-only candidates, not policy retrieval accuracy.
- Latest full product verification from the earlier repair:4912passed,
  107subtests,6skips,6warnings,371.98s. This is historical for this organization
  turn; no full product rerun was needed for filesystem/prose changes.
- Instructions/TDD`670d948`, scope clarification`ed5dada`, review deferral`7082d59`,
  and Context/ignore/organization-plan increment`8f9e922` are committed. Later
  documentary closure is found via Git, not a self-referential checkpoint SHA.
- The owner review kit is retained at workspace
  `audit-evidence/phase-05-owner-review-20261012/`, marked deferred.

## Test-volume concern

Collection during this turn before the new documentation:4,919cases,1,816definitions,124modules. Largest modules
include contract parity413, document hygiene340, source governance294,
publication226 and authority222. A single hygiene test expands over331files;
one register-parity test has222variants; publication-interruption test180variants.
This explains part of the count, not necessity or redundancy. Do not attribute
all tests to course-code inconsistency or delete tests on that assumption.
A later targeted coverage/redundancy audit is separate from source organization.
Avoid redundant broad reruns for documentation-only work.

## Exact next action

1. Verify current Git and organized source hashes, read updated Context/handoff
   loop, and check the two pending contracts and observed metadata.
2. Recover acquisition/effectivity/scope evidence without approving by filename.
   Inspect relevant Charter/student handbook pages against originals.
3. Prepare a fresh external candidate output and log for the117page university
   Charter, using existing CLI/library/offline assets. Checkpoint before this
   long operation. The CLI supports a single complete input; do not silently
   split PDFs and lose physical-page/source identity. Run one source at a time.
4. Inspect every completion/binding/report result, retained rejections and
   source-byte invariance, then checkpoint and commit meaningful code/docs work.
   Process the394page handbook in a separate recoverable step.
5. Independently review critical spans and development answers, then encode and
   evaluate actual policy retrieval by language/category with source citations.
   Keep unsupported/deferred sources out of claims; calibrate development only.

Actual policy conversion, embeddings, retrieval rankings and calibration have
not run for these two bytes. No shared migration, release activation, Prolog
execution or Phase06 advancement occurred. Earn the Phase05 exit; do not infer it.

## Prompt to paste into the next CLI

```text
Continue Bintanong Phase05 in the p05 worktree. Read AGENTS.md, both Bintanong
handoff skills, Context thesis/routing diagram, plans/INDEX.md, the active
checkpoint and plans/2026-10-12-phase05-next-cli-handoff.md. Follow
plans/2026-10-12-policy-source-recovery-plan.md. Dataset organization is already
done; prospectuses and their review are preserved/deferred. Resume the two new
policy sources' pending governance and actual candidate ingestion, one source
at a time, in the existing approved offline environment. Verify Git and original
hashes first. Keep inputs/results ignored, use TDD for product fixes, update
checkpoint/current progress after material work, and commit small verified
increments. Do not repeat setup, redo closed software phases, activate sources,
or start Phase06. Deferred college/organization inputs need not be present.
```
