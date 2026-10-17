# BSCS original-source pipeline and Excel review delivery

Owner requested fresh BSCS-only source artifacts/test cases and CSV review in
Microsoft Excel, then explicitly selected two sets:full prospectuses and reviewed
Phase06 subset. Baselinea8efcc8/product49bc993; no product/dependency/lock changes.
Repository handoff/reminder, spreadsheet and relevant verification workflows used.

## Delivered files

Ignored root:C:/Coding-projects/bintanong_workspace/audit-evidence/p06-bscs-excel-20261017.

| Set | Reviewer CSV | Rows | Meaning |
| --- | --- | ---: | --- |
| Full prospectus | full-prospectus/bscs-old-review.csv |53| Detected2018-2019 draft course rows |
| Full prospectus | full-prospectus/bscs-proposed-review.csv |55| DetectedPROPOSED2025-2026 draft course rows |
| Phase06 reviewed subset | phase06-reviewed/bscs-rules-review.csv |11| Seven reviewed expressions/four unknowns; one draft identity |
| Phase06 runtime tests | phase06-reviewed/bscs-runtime-test-cases.csv |73| Fresh actual-Janus observations with fictional completion facts |

BSCS-review-package.zip includes these four CSVs, original PDF copies, actual
fresh Docling/prospectus JSON, pipeline CSV/Markdown/publish manifests, fresh
source-bound authoring JSON/PL/runtime bundles, source images, test results and
READ-ME.md. Original pipeline exports remain unchanged; the reviewer CSVs are
separate additions. Reviewer verdict/name/date/notes columns start unreviewed/blank.
CSV editing does not automatically update authoring or establish approval.

Original dataset root and source hashes match [review01](2026-10-17-phase06-translation-review-01.md)
and [dataset guide](dataset-locations.md). Full original PDFs were read directly,
not replaced by previously generated JSON. Native selected-field regeneration
also reads those originals, applying unchanged tracked decisions01-03. Fresh
reviewed ledgers/PL match the earlier sealed candidates exactly; no old receipt
was recreated or new human verdict inferred. Both original dataset PDFs are intact.

## Actual full-extraction outcome

Existing backend.bintanong_tools.prospectus_extractor ran once for each PDF with
--export-csv --export-pl --export-md --device cpu --no-semantic-doc --force --strict.
Both published review-only JSON/CSV/Markdown and returned1 because audit=error.
The pipeline withheld full-prospectus PL as required. These counts do not prove
whole-prospectus completeness or accuracy. No extraction/content correction made.

- Old:five unit-checksum discrepancies and missing parsed CS3 units. First-year
  printed totals of3 are visible in the original; do not silently replace them.
  Full extraction also merges neighboring prerequisite text into oldCC5/L:
  `CC 3/L, CC 4/L CC 1/L, CC`. The already-reviewed original is only
  `CC 3/L, CC 4/L`. The CSV explicitly flags this disagreement, preserving both.
- Proposed:unresolved ownership of an adjacent `semesters` prerequisite fragment;
  table1 skipped for no usable layout. Exact source-cell/page/bbox evidence stays
  in audit.structural_anomalies. No standing rule inferred or activated.

The reviewed Phase06 set is generated separately from its settled native source
fields. Full extraction defects cannot enter its structured authoring truth.
Unknowns/draftCC1/L, version labels and literal /L remain unchanged.

## Verification and reproduction

- Fresh73 runtime cases and four concurrent isolation checks passed using the
  existing authoring/compiler/bundle/runtime APIs and fixed tracked engine.
  runtime-test-results.json records complete requests, facts and results.
- Independently checked39 native source-span occurrences against originals.
- CSV assertions:UTF-8 BOM, quoted fields, CRLF, exact row/value roundtrips,
  blank versus zero, Excel cell limits, unfilled reviewer fields and11 synthetic
  formula-text/quoting safety cases. No formula-leading source cells found.
- Artifact Tool independently imported all four CSVs:53x37,55x37,11x23,73x21
  data rows/columns; no formulas. Native Excel was not opened. READ-ME explains
  Excel UTF-8/comma import, Text identifiers and review-copy handling.
- Focused tests109 passed12.14s, exit0:system Python3.13 -B -m pytest -q
  -p no:cacheprovider tests/test_prospectus_publish.py
  tests/test_curriculum_term_views.py tests/test_symbolic_offline_research.py
  tests/test_symbolic_runtime_bundle.py, external basetemp under this root/test-temp.
- Prior37-file regeneration and32-file real-runtime manifests verified unchanged
  before/after reviewed-source generation. Full pipeline publish hashes checked.
- Final docs/phase550 passed/11 subtests27.26s, exit0; raw docs.log. Phase state
  validates; advancement remains refused by the unchanged blocked Phase06 handoff.

Source conversion used the already-installed primary-checkout Python3.13.5 venv
at C:/Users/Hawksprey/source/repos/Bintanong/backend/.venv/Scripts/python.exe,
Docling2.129.0/core2.97.1/parse7.20.0, transformers5.17.0/hub1.32.0. Existing cached
Docling models were reused with HF_HUB_OFFLINE/TRANSFORMERS_OFFLINE/
HF_DATASETS_OFFLINE=1. No installs/downloads or environment files changed.
System3.13.12 verified source/compiler/Janus/CSVs/tests. Its earlier two full-suite
Docling dependency failures remain unresolved; this uses a compatible existing
conversion interpreter without claiming that conflict fixed.

Raw reproduction scripts generate_reviewed.py/export_csv.py/package.py and logs
remain ignored under the root. They reuse repository functions and bind actual
source hashes. Helpers/temporaries/node_modules junction/logs are excluded from
the user archive. The53-file delivery manifest SHA-256 is
`7a417f051e41d4a93f798cbe3ec99e16a0201958ba5e1c6c7031e6a37a052dbc`;
ZIP SHA-256:`986e37338a8d11107e6fa2574b551596b02ba3b548ac024e96f1d2ae0867aec6`.
Archive contents were decompressed and byte/hash-checked against the manifest.

Phase06 output review remains pending; formal blocked handoff/release guards stay.
No frontend/API/DB/later-phase work or unrelated Docker edits included.
