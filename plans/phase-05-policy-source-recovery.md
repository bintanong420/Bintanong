# Phase05 actual policy-source recovery

**Latest state:**117page Charter candidate verified with427chunks/3retained table
rejections; handbook next. Final product verification: first full run4help-decoding
failures/4921passes/107subtests,367.13s. UTF8mode resolves4help checks(4passed2.07s);
fresh full rerun4926passed/107subtests,6skips/6warnings362.06s,exit0. Ledger19tests
pass14.221s. Exact latest continuation:
[policy recovery handoff](2026-10-12-phase05-policy-recovery-handoff.md).

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

Pre-conversion checkpoint committed`5940d93`.

## First complete-document run and recoverable failure

Existing CLI ran the complete117page Charter with`--root <dataset parent>`,
`--out <evidence>/charter-candidate`, original pending logical acquisition locator
and`--classification charter_candidate`. Existing offline flags/cache/TEMP and
8CPU threads retained. Execution21:19:11–21:28:29+08:00,558.178s, exit1:
`raw reading order omits text or tables`. No completion bundle or candidate chunks.
Docling reported dropped cells on three grids (1/158,1/145,67/67); these require
source review regardless of reader success. Logs and execution JSON preserved.

Existing temporary cleanup removed raw conversion on candidate-reader refusal.
Synthetic PDF/PPTX retention regression2RED38.14s; smallest correction publishes
raw/meta diagnostics after source invariance guard, before reader interpretation.
Completion manifests remain absent on refusal; no candidate eligibility inferred.
Relevant procedure/bundle/policy suites126passed/1skipped79.97s after correction.

Docling documentation describes content-item children as part of reading order.
Current readers only followed groups; a synthetic text-parent/child hierarchy
reproduces the same refusal(2RED2.58s). Minimal traversal correction GREEN:
130passed/1skipped51.30s across procedure/bundle/policy modules, including descendant
cycles/duplicates and source-mutation guards. Actual Charter graph still needs
inspection before claiming source repair. No full-suite pass claimed yet.

Second whole-source conversion runs through existing`load_document_result` into
`charter-raw-capture/` to preserve exact source-bound raw/meta bytes before any
reader. After capture, reuse it for diagnostics and candidate recovery; no further
expensive conversion unless evidence shows capture invalid. No installation.

Original sample review notes remain external and agent-reviewed, not approved.
Pre-enrollment physical102–103/printed98–99has four5minute rows and printed total
25minutes; retain source discrepancy for clarification. No inferred correction.

## Actual-source recovery and review corrections

Durable complete conversion528.029s produced raw SHA256
`11cce11c35151aa4a03af24ea12d4d847729379dd90677b4ddec3c366997fe62`.
Actual graph has305texts/123tables. Legacy walk misses27nested text/group fragments
onphysical92and3table-owned footnotes onphysical10/20. Procedure traversal now
accounts for428refs; policy traversal needed table children too.

Independent read-only review of`5940d93..ab4a6ec` found twoP2issues: PDF policy
reader skipped table-owned text, and malformed descendant text refs could resolve
through tail-only integer parsing. Both reproduced before fixing: table-footnote
1RED0.53s; malformed descendant1RED0.50s. Additional tablecycle1RED0.47s protects
new recursion. Guarded table traversal/canonical refs GREEN5tests0.40s, and actual
reader now succeeds with all428refs. Reviewer8focused regressions passed30.06s.
Reviewer set aside original-source accuracy/dropped-cell correctness, authority,
applicability, retrieval, activation and historical changes; these remain separate
pending gates, not waived by review. Full product suite running on final code.

Final verification supersedes that in-progress note: approvedPython`-B -m pytest
tests -q -p no:cacheprovider --basetemp=<evidence>/pytest-final-utf8` with existing
offline assets,8CPUthreads,PYTHONUTF8=1andPYTHONIOENCODING=utf-8:4926passed,
107subtests,6skips,6warnings362.06s,exit0. Initial whole run4help-decoding failures
were from outputUTF8versus parentcp1252; all4then passed in2.07s under UTF8mode,
with no test/product changes. Phase-state unittest19passed14.221s,exit0.

`recover_charter_candidate.py` validated source/settings/raw identity using the
existing loader cache checks and Docling schema, replayed exact captured output
through the existing converter-injection API, then checked raw/meta equality and
`load_candidate_bundle`. This is actual original-source conversion replay, not
fresh conversion or synthetic institutional text. Execution30.429s, exit0.
Recovered bundle:`<evidence>/charter-recovered-candidate/`.

| Accounting | Result |
| --- | ---: |
| Physical pages |117|
| Raw/covered text items |305/305|
| Rejected/omitted text items |0/0|
| Raw/emitted/rejected tables |123/120/3|
| Candidate chunks |427|
| Page omissions |0|

Three retained table rejections: table0/physical3ambiguous or missing headers;
table10/physical12ambiguous raw row order; table94/physical92missing or blank cell
text. Docling's dropped-cell warnings remain unresolved extraction findings.
Accounting completeness does not establish complete policy content.

`verify_charter.py` independently checked manifests/bindings, exact existing pending
register, all45dataset entries unchanged and all117page records.192sample spans
onphysical6/7/69/102/103/109/110were compared with original PDFium bbox text:
175whitespace/NFC matches and17differences. Separate classification confirms all17
are typographic apostrophe/dash substitutions; strict findings remain retained,
candidate text untouched. This bounded agent check is not human approval, an OCR
measurement or a whole-document accuracy estimate. All chunks have pending review
and verification, empty scope and no source approval. No embeddings or retrieval
scoring of these policy bytes, database publication, activation or Phase06.

## Closure evidence

Final45entry inventory unchanged.70task evidence files sealed, excluding pytest
temporary trees; manifest SHA256:
`c3dc18e7693f392e357e6a1fe705b7cb5d9fb2e7ef844cfee2c1e1bd282bd779`.
Manifest and all raw outputs stay ignored under the evidence root. Current Context
resume and dataset-ignore rules verified already present; no duplicate setup or
organization. Phase05 exit remains blocked on actual approved policy retrieval.
