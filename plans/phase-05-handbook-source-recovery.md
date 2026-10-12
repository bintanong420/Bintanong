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
