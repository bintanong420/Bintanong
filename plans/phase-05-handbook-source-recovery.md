# Phase05 Student Handbook source recovery

Owner authorized continuation after university Charter candidate recovery. Resumed
clean `d58b830`; code `c061238` unchanged. This records candidate ingestion, not
institutional approval or phase completion. Follow
[latest policy handoff](2026-10-12-phase05-policy-recovery-handoff.md) and
[recovery plan](2026-10-12-policy-source-recovery-plan.md).

## Preflight and scope

Original:`backend/bintanong_tools/bintanong_jsonifer_prolog/dataset/StudentHandbook/2021/PSU Student Handbook.pdf`.
SHA256:`4c9a95bf6895ddba75a997a37fa069644ac081dd7ab4a43f882496db834351c8`.
Fresh PDFium count394physical pages. Existing pending version/locator matches;
all45dataset entries unchanged. Cover2021and BORapproval2020remain distinct.
Physical1has no native text; no OCR asset download or accuracy claim.
Institutional applicability/effectivity/content review remain pending by section.

Context thesis physical36/55/68and routingPNG consulted; master6/7/10reviewed.
Institutional RAG preparation remains separate from private user context and later
executable Prolog. Original university Charter and prospectus files/results remain
preserved. Deferred prospectus review/future college and organization inputs stay
deferred. No replacement source search, organization/setup repeat orPhase06.

## Execution environment and new evidence

Approved Python3.13.7:
`C:/Coding-projects/bintanong_workspace/audit-evidence/p05-real-retrieval-readiness-20261012/venv/Scripts/python.exe`.
Reuse existing readiness HFcache, Docling artifacts andtmp with offline flags,
PYTHONUTF8=1/PYTHONIOENCODING=utf-8and8CPUthreads. Native-text/OCRoff conversion
settings unchanged; models remain outside Git. No packages/locks/install changes.

New ignored evidence root:
`C:/Coding-projects/bintanong_workspace/audit-evidence/p05-handbook-source-recovery-20261012/`.
Operational runner uses original InputSnapshot/existing pending register and
`run_ingestion(... classification="policy_candidate")`, complete original document
and new`handbook-candidate/`; success checked by`load_candidate_bundle`.
`handbook-execution.json`records running/success/refusal and elapsed time.

Preflight command: approvedPython`-B <evidence>/run_handbook.py preflight`; exit0,
394pages/exact original/pending record/45unchanged entries. Outputs:
`before-inventory.json`, `handbook-preflight.json`. No product code change;
synthetic RED/GREEN required if actual execution exposes a product defect.

Whole-source run: **NOT RUN** at this pre-conversion checkpoint. Next command:
approvedPython`-B -u <evidence>/run_handbook.py run`, separate external logs.
Then check complete manifests, page/item/table accounting, raw retained rejections,
source invariance and sampled critical original spans before committing results.

## Whole run active and original inspection

Pre-conversion checkpoint`7fe2f07`. Actual run began22:16:02+08:00with status/logs
in new evidence root; no candidate completion yet.24original pages rendered and
selected requirements/grade contexts visually inspected. Sparse-page samples
include map/organization-chart images, illustrated divider and blank bodies; the
presence of header text cannot establish body coverage. Physical31waiver conditions,
32/33distinct admission checklists and34negative/numeric cross-enrollment clauses
need preservation. Physical46/144/355have different grading contexts; no universal
undergraduate rule inferred. Physical47has succeeding-term/one-year timing wording
for source-owner interpretation. Notes remain ignored/agentreview/pending; no
approved gold answers, content rewrite or rules. Preserve sealed Charter evidence.

## Whole-source refusal and TDD recovery

Conversion finished after922.075s, then reader refused`raw reading order omits text
or tables`(exit1). Prior retention fix preserved raw7,533,900bytes and718byte
metadata in incomplete`handbook-candidate/conversion/`; no completed bundle.
Docling dropped-cell warnings retained. No new PDF conversion is needed.

Actual graph5731texts/133tables/433pictures;83unvisited text items are children of
picture nodes. Existing readers handled text/table/group children but skipped
pictures, losing native captions/headings/text from accounting.8synthetic RED
regressions0.96s reproduce PDF/PPTX omission and policy/procedure malformed,
missing and cyclic picture refs. Guarded group/picture traversal preserves native
child order without adding picture bytes to text or inventing OCR. Relevant suites
141passed/1skipped27.69s, and actual reader succeeds with all5864text/table refs.

`recover_handbook.py`now reuses exact verified raw/source/settings/schema through
existing pipeline in fresh`handbook-recovered-candidate/`. Original refused output
and raw logs remain intact. No completion or source accuracy claim until checked
bundle and original invariance/results are read. Full-suite/review still pending.
