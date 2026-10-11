# Independent Phase F Spec review — 2026-10-10

SPEC FAIL — two confirmed Medium findings. Reviewer: separate run /root/f_spec_review; pin dd699958505996358864383ff9c184cb98aec985 plus external digest-boundary regression.

1. Absolute paths enter the folder index — backend/bintanong_tools/prospectus.py:335–340,423.
Reproducer: run folder mode with a valid PDF/record and ExtractionSettings(semantic_doc=<external directory>/missing.md), outside both roots. The real child refuses correctly, but candidate_runs.json retains the complete absolute semantic-map path. Decision correction 14 requires relative locators/names in the index.
Regression acceptance: the refusal remains processing_error, creates no candidate artifacts, and stores no absolute external semantic-map path in the index.
Reproduction: evidence-root f_spec_relative_index_ofadu98g/.

2. An unusable child manifest aborts the remaining batch — backend/bintanong_tools/prospectus.py:399–411,429.
Reproducer: two PDFs; substitute a child returning exit 0 with a manifest containing the checked identity/pending fields but omitting extraction_audit. _child_manifest accepts it; _summary raises KeyError('extraction_audit') outside the handler. Only the first child runs; no folder index is written. Expected: record that child's processing error and continue.
Regression acceptance: the malformed first manifest produces a processing_error index entry, the second PDF still runs, and both outcomes remain indexed.
Reproduction: evidence-root f_spec_child_manifest_5frmyduz/.

Independent verification: 97 passed, two installed Typer/Click deprecation warnings, exit 0, 18.07s. Candidate and pipeline imports asserted against archive; all 352 candidate files matched hash manifest. Baseline comparison confirmed only declared F changes and added regression.
Read: reviewer role/templates/Codex SDD, review package, 22 corrections, Tasks1–7, production diff, six F test files/helper/new regression, shared identity/publication/pipeline integration, M01 result/RED log.

Skipped: broad gates, mutant rerun, real Docling, Docker Tasks8/9 and final documentation Task11. Standards remains separate and gated. Both findings unresolved at review time; 52/52 UNPROVED. No institutional approval or full PhaseF completion.