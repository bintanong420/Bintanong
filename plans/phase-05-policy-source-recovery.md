# Phase05 actual policy-source recovery

Continuation of the [recovery plan](2026-10-12-policy-source-recovery-plan.md),
resumed from clean `3d464be` on12October2026. This is execution evidence, not
source approval or phase completion. Dataset organization, Context resume loop
and full dataset exclusion already exist; no repeat moves or setup.

## Resume verification and bounded task

- Existing phase inspector: valid, Phase05 active, advancement blocked. Stale
  checkpoint pointer reconciled against Git. GitHub MCP remote inspection:
  dev`10bfd6f`; Phase05 work remains local.
- Fresh dataset inventory equals all45 organization entries byte-for-byte,
  including40prospectus-tree files and42original files. Two pending source
  contracts validated with existing `load_pending_register`; no promotion.
- Original covers confirm Charter2025fourth edition and handbook2021; handbook
  BOR approval2020 is separate. PDFium confirms117/394physical pages; handbook
  physical1has no native text. No OCR accuracy claim.
- Context thesis physical36/55/68 and runtime diagram reviewed; master6/7/10,
  Phase04 complete handoff and Phase05 blocked handoff consulted. Institutional
  policy RAG preparation remains separate from Phase06 executable rules.
- Charter contains nonstudent services; handbook includes school-level,
  graduate and law material. Folder/title does not establish applicability.
  Acquisition URL, issuing-office verification, effective dates, supersession
  and undergraduate scope remain pending. Initial public-source lookup did not
  establish same-byte acquisition; stop replacement searches after owner's
  clarification that supplied editions are the latest available.
- Physical/printed labels have changing offsets: Charter physical6prints5,
  physical69prints65. Keep physical pages; do not invent a global label mapping.

Current task: one complete117page Charter ingestion using existing CLI and
`charter_candidate`, followed by checked-bundle validation and sampled original
span review. Handbook is a separate recoverable step. No split PDF conversion,
new dependency/model download, database write, activation or Phase06.

## Environment, evidence and commands

Existing approved Python3.13 environment:
`C:/Coding-projects/bintanong_workspace/audit-evidence/p05-real-retrieval-readiness-20261012/venv/Scripts/python.exe`.
Reuse its HF cache, Docling artifacts and temporary directory with offline flags.
Repository-native converter uses OCRoff/native text and accurate tables. Context7
Docling documentation confirms supported local artifact configuration; existing
settings and pins retained.

New evidence root:
`C:/Coding-projects/bintanong_workspace/audit-evidence/p05-policy-source-recovery-20261012/`.
Old organization/readiness/extraction artifacts preserved. `inspect_sources.py`
reads originals, compares the45entry inventory, validates pending contracts,
extracts diagnostic native text and renders original pages. First run stopped on
cp1252 stdout for a thesis bullet; UTF8 stdout rerun succeeded. No product change.

Command: approved Python`-B <evidence>/inspect_sources.py`; exit0. Outputs:
`resume-inventory.json`, `source-preflight.json`, native-text page diagnostics,
selected page renders and `source-inspection.log`. Gitcheck-ignore confirms nested
dataset metadata exclusion; `git ls-files -- <dataset>` empty.

Whole-source candidate execution: **NOT RUN** at this pre-conversion checkpoint.
No product code changed; TDD applies if execution reveals a product defect.
