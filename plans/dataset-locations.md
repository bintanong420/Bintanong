# Dataset locations and relocation

Recorded 2026-10-12 from the owner's Phase 05 worktree. Read this guide when resuming source reading, ingestion or practice-exam work; discover files again rather than assuming another worktree contains the ignored dataset.

The current dataset parent is:

```text
C:/Coding-projects/bintanong_workspace/worktrees/Bintanong/p05/backend/bintanong_tools/bintanong_jsonifer_prolog/dataset
```

The original PDF corpus root passed to `evaluation.practice_exam --source-root` is **one level below** that parent:

```text
C:/Coding-projects/bintanong_workspace/worktrees/Bintanong/p05/backend/bintanong_tools/bintanong_jsonifer_prolog/dataset/PalSU Undergraduate Prospectus Website Dump
```

This deep codebase location is temporary; the owner intends to relocate it. No relocation was performed during the exam expansion. Existing ignored originals remain read-only. New originals, conversions, gold answers and raw evidence must remain untracked within `C:/Coding-projects/bintanong_workspace`, following the owner's location correction; do not force-add the existing dataset.

**Current organization, 12 October 2026:** the owner authorized categorization
inside this existing dataset parent. The prospectus corpus root above remains
unchanged. Only two loose policy PDFs moved into the edition folders below.
Historical relocation notes describe a possible later root move, not an action
performed during this organization.

| Category | Current source location relative to dataset parent | Status |
| --- | --- | --- |
| University Charter | `CitizenCharter/2025/University/PALAWAN-STATE-UNIVERSITY-Citizens-Charter-2025-4th-Edition.pdf` | Visually observed2025/fourth edition,117pages; pending source governance/ingestion |
| Student handbook | `StudentHandbook/2021/PSU Student Handbook.pdf` | Cover visibly2021,394pages; printed2020BOR approval kept separate; pending governance/ingestion |
| Memoranda | `Memoranda/2024/` through `2027/`, plus `UnknownYear/` | No files supplied yet; original photos will be retained |
| College-specific Charters | `Deferred/CollegeCitizenCharter/` | Future photographs/documents intentionally deferred |
| Organization policies | `Deferred/OrganizationPolicies/` | Future sources intentionally deferred |

Charter and handbook categories also have2024–2027 andUnknownYear folders.
Additional real edition years are allowed. The dataset README and local
`_source-catalog.json` explain same-year revisions and observed metadata.
The folder year is an organizational label; byte-derived source/version IDs,
reviewed applicability/effectivity and knowledge-release membership govern
runtime use. Preserve old editions and never activate the newest folder by default.

All42original file bytes were preserved. The prospectus tree's39PDFs and inventory
CSV have identical paths and hashes. Both `/dataset/` and the actual nested
dataset parent are now fully ignored, including future image inputs and local
catalogs; no original file is tracked or staged.

Current source-recovery plan:
`plans/2026-10-12-policy-source-recovery-plan.md`; next-CLI context:
`plans/2026-10-12-phase05-next-cli-handoff.md`. Before/after inventories, move
journal, cover renders,511page text profile and two pending source contracts live
at `C:/Coding-projects/bintanong_workspace/audit-evidence/p05-dataset-organization-20261012/`.
Older readiness/extraction evidence is preserved.

The main checkout is `C:/Coding-projects/bintanong_workspace/Bintanong`; Phase 05 code changes belong to its isolated `C:/Coding-projects/bintanong_workspace/worktrees/Bintanong/p05` worktree. `audit-evidence` is shared workspace storage outside both code checkout folders. An unrelated ancestor `.git` was observed earlier at `C:/Coding-projects`. Final fresh verification finds that marker absent and the evidence folders outside Git. No Git metadata was removed by this agent; the main checkout and p05 worktree remain intact.

## Observed corpus

All current PDF paths are under `Tiniguiban - Main/<college>/...`. Fresh inventory found 39 PDF paths, across nine college directories:

| College directory | PDF paths | Balanced dev questions |
| --- | ---: | ---: |
| CAD | 1 | 3 |
| CAH | 6 | 3 |
| CBA | 9 | 3 |
| CCJE | 1 | 3 |
| CHTM | 3 | 3 |
| CNHS | 2 | 3 |
| CoE | 4 | 3 |
| CS | 6 | 3 |
| CTE | 7 | 3 |

These counts describe paths, not approved curricula, distinct documents or exhaustive program coverage. College labels follow the actual directory spelling, including `CoE`. One source program per college supplies the bounded exam; CS includes two curriculum editions. Do not infer document content from filenames: one Accountancy-named PDF inspected during this work was a brochure, so the CBA exam uses the inspected HRM curriculum instead.

## Portable source resolution

Exam packets store paths relative to the corpus root, alongside exact original SHA-256/version/page/locator identities. The CLI requires `--source-root`; it has no hardcoded dataset root or automatic environment-variable resolution.

```powershell
$datasetRoot = (Resolve-Path -LiteralPath 'backend/bintanong_tools/bintanong_jsonifer_prolog/dataset/PalSU Undergraduate Prospectus Website Dump').Path
python -B -m evaluation.practice_exam --exam C:/Coding-projects/bintanong_workspace/audit-evidence/p05-college-expansion-20261012/practice-exam.json --source-root $datasetRoot --output-dir C:/Coding-projects/bintanong_workspace/audit-evidence/p05-college-expansion-20261012/exam --allow-ignored-output
```

For the future move, choose an owner-approved untracked location within `C:/Coding-projects/bintanong_workspace`, preserve the campus/college relative tree and original bytes, and pass that new root explicitly. Re-inventory the live PDFs, revalidate hashes/college coverage, and update this guide and the current checkpoint/progress log with the new location. Test coverage proves that a changed root with unchanged relative paths and bytes validates. A newly added college causes an all-college packet to fail validation until its declared coverage and cases are updated.

## External evaluation artifacts

- Original 12-case BSCS version: `C:/Coding-projects/bintanong_workspace/audit-evidence/p05-dev-exam-20261012/`.
- Balanced 27-case version and source-reading images: `C:/Coding-projects/bintanong_workspace/audit-evidence/p05-college-expansion-20261012/`.
- Each version has `practice-exam.json` and `exam/questions.md`, `exam/answer-key.md`, `exam/validation.json`.

Both versions were moved from their initial AppData location after the owner required all task artifacts within the workspace. Each task folder has a `.gitignore` containing `*`; earlier `git check-ignore` confirmed protection while the ancestor repository existed. The final evidence location has no Git ancestor; the ignore files remain preventive protection. Default export still refuses Git roots. The explicit `--allow-ignored-output` option requires every output to be ignored by every containing Git repository, while preserving input/link protections. Never force-add these folders. No real retrieval observations or institutional approval are established by exporting or validating an exam.

## Current real-execution environment

Owner-authorized isolated Python3.13 environment: `C:/Coding-projects/bintanong_workspace/audit-evidence/p05-real-retrieval-readiness-20261012/venv/Scripts/python.exe`. Resolved pins/setup log, encoder reports/vectors and original-source inspection are in its parent directory. Use this environment rather than reinstalling into system Python or the worktree. Set HF_HOME/HF_HUB_CACHE/TEMP/TMP/DOCLING_CACHE_DIR within that evidence directory; existing SEA-LION/GEMMA stay in MODELS. Five owner-approved Docling assets are verified in workspace hf-cache and hardlinked into docling-artifacts; set DOCLING_ARTIFACTS_PATH there and HF_HUB_OFFLINE/TRANSFORMERS_OFFLINE=1.

Actual original-source bundles: `.../p05-real-retrieval-readiness-20261012/original-ingestion/<pdf-sha256>/`.39 remain pending;33audit errors emit no chunks. Actual source mapping, review sheets,336document vectors/27query diagnostics and sealed raw-evidence manifest stay in that readiness root, outside Git. See [execution and limits](phase-05-real-retrieval-readiness.md). No dataset relocation or shared Supabase publication occurred.

## Guided owner review and repaired candidate cohort

Owner-requested prospectus reviewfolder: `C:/Coding-projects/bintanong_workspace/audit-evidence/phase-05-owner-review-20261012`. This review is deferred for Phase06 preparation. Its `START-HERE.md`, editable case/source decision sheets,10byteidentical selectedPDFcopies and12pageimages are retained; originaldataset remainsunchanged. Allreviews pending.

New repaired Financial Management candidate lives under `C:/Coding-projects/bintanong_workspace/audit-evidence/p05-extraction-recovery-20261012/repaired-ingestion/176cbbd07bcec16a9037b610636546c032fc66ac2aa24536e163632988625141/`,with54newvectors recordedseparately. Current source mix32errors/7warnings/390chunks; historical39-bundle/336-vector readinesssnapshot preserved. No datasetmove orsharedpublication.
