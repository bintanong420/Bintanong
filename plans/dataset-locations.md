# Dataset locations and relocation

## Current machine verification — 17 October 2026

For Hawksprey420's Phase 06 worktree, the freshly verified dataset parent is:

```text
C:/Coding-projects/bintanong_workspace/worktrees/Bintanong/p06/dataset
```

The prospectus root is its `PalSU Undergraduate Prospectus Website Dump/` child:
39 PDFs and one CSV, including both BSCS originals with review01 hashes intact.
The supplied current tree has62 files:44 PDFs,12 JPGs, one CSV, four MD and one JSON.
Policy originals now use `CitizenCharter/2025/University/`, `StudentHandbook/2021/`,
`Student Government Constitutions and Election Code/` and
`Misc. Student related procedures/` (gatepass, special-class fee and enrollment).
No dataset files were changed during resume; presence does not establish approval
or equivalence to the historical62-file inventory.

This supersedes the scaffold's55-file/legacy-layout availability observation.
Its sealed manifest is retained:15 saved destination paths are absent, eight have
hash-identical categorized matches, seven old copies remain only in the original
checkout; all101 original source paths still match. Do not restore the old layout
over the supplied current tree. Exact path/hash mapping and a fresh inventory stay
ignored in `workspace/audit-evidence/p06-resume-20261017/`.
The p05 path below is historical and absent here. See the [resume audit](2026-10-17-phase06-resume-verification.md)
for fresh evidence, missing review-bundle recovery and verification limits.
Originals/generated derivatives stay inactive and ignored by Git.

## Current source-retention decision — 15 October 2026

The owner keeps the added student-related memos, fees, enrollment material and
student-government sources for provisional undergraduate review. Poor image
quality is handled per field with human verification and recorded unreadable/cropped
limits, not by inventing text or silently deleting whole sources. Retention is
settled and supersedes the interim proposal to defer them solely to retain a two-PDF
policy baseline. Start [the short verification packet](2026-10-15-additional-source-human-review.md)
atF1; no source-content readings/new question wordings or school verification are
approved merely by this retention decision. Keep the source facts/current-year
effectivity and runtime activation states separate.

## Student-government files observed — 15 October 2026

Two additional originals are now present under
`dataset/Student Government Constitutions and Election Code/`:

| File | Pages | SHA-256 |
| --- | ---: | --- |
| `THE-2023-TINIGUIBAN-USG-Constitution (2).pdf` |34 | `b40cca9e22d8f30dc9e48b684aa179a2f666ef1aef325c8132d170ec80b8d68d` |
| `The-PALAWAN-STATE-UNIVERSITY-Omnibus-Election-Code-1.pdf` |21 | `c46652fe52889425458cf52b1566fe2cd85234831080c137ce0cac77e1688f9e` |

The constitution cover prints2023/TiniguibanCampus and ratification15November2023.
ArticleXIV, physical17–21, addresses College Student Government. The election code
opening explicitly includes USG and CSG elections. No separate college-specific
CSG constitution file was found in the current dataset. This is partial CSG-related
source coverage, not evidence that every college constitution has been collected.
The handbook70–76 also contains student-government references/general provisions,
not an identified set of separate college constitutions. These two newly observed
PDFs are inventoried/read-only; neither is reviewed, embedded or active. There are
now62local dataset files, including the earlier60file inventory, not62approved
documents. Raw hashes/native inspection/covers remain ignored under
`C:/Coding-projects/bintanong_workspace/audit-evidence/p05-student-government-inventory-20261015/`.

## Added student procedures received — 15 October 2026

The owner supplied13files (12distinct byte hashes) at repository-root
`dataset/Misc. Student related procedures/`: five vehicle/gatepass images,
one2023special-class fee photograph, six incoming-student enrollment images
(one exact duplicate), and one continuing-student enrollment PDF. The incoming
advisory prints first-semester2026–2027; the continuing PDF prints second-semester
2025–2026 despite its2026folder. No file was moved, deleted or activated.

The [intake and focused review](2026-10-15-additional-source-intake-report.md)
records source hashes, proposed page order, enrollment differences and visible
gaps/conflicts. Keep the unique enrollment content; exclude only the exact
duplicate occurrence from later derivatives, retaining both original paths.
The earlier "no files supplied" and incoming-staging notes below are historical.
Fresh verification preserves all47relocation baseline files and all13new originals.
The60file total describes local files, not approved documents or an active corpus.
Do not edit the historical acquisition catalog or sealed relocation evidence to
make old counts look current; use the new ignored intake inventory and report.
Raw manifest/native inspection/page renders:
`C:/Coding-projects/bintanong_workspace/audit-evidence/p05-additional-source-intake-20261015/`.

Updated 14 October 2026 after the owner-authorized root relocation in the Phase 05
worktree. Read this guide when resuming source reading, ingestion or practice-exam
work; discover files again rather than assuming another worktree contains ignored data.

The current dataset parent is:

```text
C:/Coding-projects/bintanong_workspace/worktrees/Bintanong/p05/dataset
```

The original PDF corpus root passed to `evaluation.practice_exam --source-root` is **one level below** that parent:

```text
C:/Coding-projects/bintanong_workspace/worktrees/Bintanong/p05/dataset/PalSU Undergraduate Prospectus Website Dump
```

The complete former `backend/bintanong_tools/bintanong_jsonifer_prolog/dataset/`
directory was moved to repository-root `dataset/`. All 47 files (41 PDFs), 63
subdirectories and original relative paths were retained; file SHA-256 values match.
The old directory is absent. `/dataset/` is explicitly ignored by Git and Docker.
Ignored data does not travel with a clone or branch change into another worktree.
Use this actual local root explicitly rather than reinstalling or acquiring sources.
New originals, conversions, gold answers and raw evidence remain untracked within
`C:/Coding-projects/bintanong_workspace`; never force-add the dataset.

**Organization established 12 October 2026, preserved by the 14 October move:**
the owner authorized categorization within the dataset parent. The prospectus tree
and policy edition folders below retain their contents and relative paths.
Historical relocation notes describe a possible later root move, not an action
performed during this organization.

| Category | Current source location relative to dataset parent | Status |
| --- | --- | --- |
| University Charter | `CitizenCharter/2025/University/PALAWAN-STATE-UNIVERSITY-Citizens-Charter-2025-4th-Edition.pdf` |2025/fourth edition,117pages;427candidate chunks/3table refusals; governance/content approval pending |
| Student handbook | `StudentHandbook/2021/PSU Student Handbook.pdf` |2021,394pages,printed2020BOR approval separate;4272candidate chunks/10text+18table refusals after list recovery; governance/content approval pending |
| Memoranda | `Memoranda/2024/` through `2027/`, plus `UnknownYear/` | No files supplied yet; original photos will be retained |
| College-specific Charters | `Deferred/CollegeCitizenCharter/` | No longer expected in the incoming batch per owner14October; historical folder retained |
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
`plans/2026-10-12-phase05-policy-candidates-handoff.md`. Before/after inventories, move
journal, cover renders,511page text profile and two pending source contracts live
at `C:/Coding-projects/bintanong_workspace/audit-evidence/p05-dataset-organization-20261012/`.
Older readiness/extraction evidence is preserved.

Checked policy bundles remain outside Git under workspace audit-evidence:
`p05-policy-source-recovery-20261012/charter-recovered-candidate/` and
`p05-handbook-source-recovery-20261012/handbook-recovered-candidate/`. Raw conversion,
chunks, reports and retained refusals stay ignored; original dataset contains the
preserved sources. Incomplete first-run candidate directories are diagnostic only.
Do not rerun original conversion to resume source-span diagnosis.

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
$datasetRoot = (Resolve-Path -LiteralPath 'dataset/PalSU Undergraduate Prospectus Website Dump').Path
python -B -m evaluation.practice_exam --exam C:/Coding-projects/bintanong_workspace/audit-evidence/p05-college-expansion-20261012/practice-exam.json --source-root $datasetRoot --output-dir C:/Coding-projects/bintanong_workspace/audit-evidence/p05-college-expansion-20261012/exam --allow-ignored-output
```

The current move is complete; portable exam packets retain their relative paths.
For later relocation preserve the campus/college tree and original bytes, pass the
new root explicitly, re-inventory and update this guide/checkpoint/progress. Test
coverage verifies unchanged relative paths and bytes survive a root change. A newly
added college still requires its declared coverage/cases to be updated.

## Historical absolute paths after relocation

Do not edit sealed historical scripts, source records, inventories or citations
merely to replace paths. The old prefix is
`C:/Coding-projects/bintanong_workspace/worktrees/Bintanong/p05/backend/bintanong_tools/bintanong_jsonifer_prolog/dataset/`;
the current prefix is `C:/Coding-projects/bintanong_workspace/worktrees/Bintanong/p05/dataset/`.
Resolve a saved path through the recorded exact mapping, retain its relative suffix
and require its original SHA-256 to match the relocated file before using it.
Do not create a junction or duplicate corpus at the old location.

Raw before/after manifests and the 47-file mapping are ignored at
`C:/Coding-projects/bintanong_workspace/audit-evidence/p05-dataset-relocation-20261014/relocation-map.json`.
The tracked cleanup and next-CLI handoff is
`plans/2026-10-14-dataset-relocation-and-cli-handoff.md`. Earlier no-relocation notes
below describe historical execution, not the present dataset root.

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

## Incoming college Charters and memoranda staging — 14 October2026

Latest owner correction: the incoming batch will no longer include college-specific
Citizens' Charters. It may include memoranda such as vehicle gatepass guidance.
Continue Phase05 with the existing university Charter/handbook/curricula while
school verification is deferred. Verify each supplied memo's actual undergraduate
student audience, source identity and effectivity during intake. No gatepass facts
or query cases are added until a source arrives and is reviewed. Existing folders
and earlier staging instructions below are historical, preserved for recovery.

Ignored intake root: `C:/Coding-projects/bintanong_workspace/worktrees/Bintanong/p05/dataset/Incoming/2026-10-14/`.

Use `Memoranda/<Document>/` for the current future batch; retain complete original
PPTX/PDF files and photo sequences. The local CURRENT-INCOMING-BATCH.md carries the
latest owner correction. Older PLACE-ORIGINALS-HERE.md college-Charter instructions
are historical. The entire root dataset is ignored; no incoming sources inspected.
Owner may copy originals now and notify when collection is complete; source
registration/extraction/human review/governance follow in a separate batch. This
is staging availability, not corpus activation or formal Phase05 completion.
