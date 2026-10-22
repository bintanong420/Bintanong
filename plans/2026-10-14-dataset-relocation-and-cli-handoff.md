# Dataset relocation and next-CLI handoff — 14 October 2026

The owner requested moving the complete backend dataset to the repository root and
preserving critical conversation context so a new CLI can continue independently.
The dataset now lives at `dataset/` in this Phase05 worktree. All file contents and
relative directory paths are preserved. Standing owner decisions are recorded in
`AGENTS.md`; read those before asking the owner to repeat a settled decision.

## Start here in a new CLI

Open `C:/Coding-projects/bintanong_workspace/worktrees/Bintanong/p05` on branch
`feat/p05-retrieval-logic`. Read `AGENTS.md`, its two handoff skills, `plans/INDEX.md`,
current progress, Phase05 checkpoint/plan/handoff and relevant master section10.
Use fresh Git and verification rather than the age or filename of a plan. Phase05
remains active; this cleanup does not authorize Phase06 or source activation.

Current original roots:

- Dataset: `dataset/`.
- Prospectus corpus: `dataset/PalSU Undergraduate Prospectus Website Dump/`.
- Handbook: `dataset/StudentHandbook/2021/PSU Student Handbook.pdf`.
- University Charter: `dataset/CitizenCharter/2025/University/PALAWAN-STATE-UNIVERSITY-Citizens-Charter-2025-4th-Edition.pdf`.
- Future batch staging: `dataset/Incoming/2026-10-14/`.

The root exists only in this local worktree; Git does not distribute ignored data.
Keep generated artifacts/private inputs/logs under the owner's ignored workspace
`audit-evidence/`, and models at `C:/Coding-projects/MODELS`. Existing Python3.13
environment: `C:/Coding-projects/bintanong_workspace/audit-evidence/p05-real-retrieval-readiness-20261012/venv/Scripts/python.exe`.
No reinstall, model download or repeat raw conversion is needed.

## Important settled context

- This is thesis development/testing. The owner authorizes provisional offline
  retrieval of supplied public undergraduate sources while school validation is
  pending. Do not turn that wait into a blanket development block or invent approval.
- The source-use/authenticity/current-SY letter was planned for submission on
  15October2026; no same-day reply expected. Wait for actual owner/university evidence,
  and bring it up before institutional activation or when a reply is reported.
- Owner cohort guidance: 2018–2019 remains usable when no newer supplied edition
  replaces it for that program; old cohorts can retain older curricula. New incoming
  BSCS students use the supplied proposed2025–2026 edition under owner guidance.
  Keep its proposed status and clarify unknown student curriculum.
- Eight selected rows/46fields and all12 expected evidence groups were confirmed.
  Do not reopen those reviews. Preserve Charter103 step3's original ending after
  "for" and handbook47's conflicting completion deadlines. Do not append or resolve
  missing institutional content without new original evidence/review.
- The accepted set is12scenarios/36 EN/Filipino/Taglish variants. Show the owner any
  new/changed proposed benchmark questions before testing. The exact thesis question
  is case-tl and already ranks CC5 first; the observed practicum mismatch belongs to
  the approved case-taglish paraphrase. See the corrected course diagnostic report.
- Additional data is expected once the owner is ready: no further college-specific
  Charters, possibly memoranda such as undergraduate vehicle-gatepass service.
  Shared staff use does not exclude student clauses. No new memo has arrived.
- Continue authorized work until a new human content decision is needed, work is
  complete or a verified checkpoint supports handoff. Preserve originals, source
  limitations and private-input separation; never infer authorization from testing.

## Latest development result and exact next action

Closure `90fed07` records the course-identity diagnostic. Reviewed target-course
field filtering changes the six controlled CC5 edition branches from5/6 to6/6
expected top matches. Six complete contexts preserve78citations and fit2048tokens.
Hints were explicit researcher annotations; automatic target-role extraction and
runtime filtering are not implemented. Actual sixBSCS cases still need curriculum
clarification;18policy cases remain unranked because applicability is unresolved.

Next implement a bounded reusable **offline** candidate course selector under
synthetic TDD. Bind an identity index through the existing fully reviewed curriculum
preparation contract; filter an explicitly supplied target-course hint after curriculum
selection, preserving defaults, printed codes, source fields/spans and gaps. Test
unknown codes, prerequisites mistaken for targets, altered source bindings and
ambiguous edition. No database/runtime/Prolog activation belongs to this next unit.
Latest detailed report: `2026-10-14-course-identity-diagnostic-report.md`.

## Relocation verification and recovery

Native PowerShell checked resolved source/destination stay inside the owner workspace,
refused an existing destination or any reparse point, and moved the complete directory.
All47files,41PDFs and63subdirectories retained their hashes/relative paths. No data
is staged; root `/dataset/` was already Git-ignored and is now explicitly documented,
with matching Docker build-context exclusion. Extractor default input paths now
resolve from repository-root dataset; explicit practice-exam source-root examples
and `plans/dataset-locations.md` are updated.

Ignored evidence folder:
`C:/Coding-projects/bintanong_workspace/audit-evidence/p05-dataset-relocation-20261014/`.
Its `relocation-map.json` binds every old absolute path to the new path and hash.
Historical sealed evidence is left untouched; resolve paths via this mapping before
replay rather than editing manifests or recreating the old directory. Relative-path
exam packets use the new source root directly. Directory movement changes location,
not source identity, approval or citation evidence.

Fresh regression RED: default extractor input incorrectly pointed into backend/tools
instead of root dataset (1failed,0.31s). Minimal root-path correction plus relevant
practice-exam regressions GREEN:35passed/19subtests,1.08s. Documentation/ledger:
454passed/11subtests,10.72s. Independent relocation verification records47ignored
files, zero tracked dataset files and24770707preserved bytes.1333prior dependency
bindings verify as1325unchanged plus8exact relocated paths;12/27case packets validate.
Phasevalidate exits0/canadvance exits1(expected blocked). Eighteen raw files sealed;
manifest SHA256: `7ee860b2785850664abf46143f1969ca5f3590b51afe2f9bb0072b87afb26f82`.
The initial native safety script rejected an incompatible Split-Path parameter
combination before any move; replaced it with .NET directory-name resolution.
Move log's byte-sum field is null; independent verification records the actual sum.

Preserve unrelated owner work: `artifacts/.gitkeep` deletion and untracked
`backend/artifacts/` were present at resume. They were not staged or changed by this
cleanup. Context consulted: actual thesis physical17–18 (printed16–17), runtime
routing PNG, master section10 and dataset guide; no scope/routing discrepancy.
