# Your Phase 1–2 human review checklist

You are the reviewer. Automated tests and conversion results below are preparation evidence; no human acceptance, office authorization or policy approval has been recorded. Lawrence's later-phase review stays separate. Review one document first, report your verdict, then choose the next one.

## Run one document in PowerShell

The institutional Handbook/Charter path currently has a CLI and JSON artifacts, not the prospectus correction GUI. Start with the small Charter PPTX, whose conversion was tested. This yields raw review candidates; the current PPTX locator contract deliberately withholds all chunks.

```powershell
Set-Location 'C:\Users\Hawksprey\source\repos\Bintanong'
$root = (Resolve-Path 'backend\bintanong_tools\bintanong_jsonifer_prolog\dataset\handbook_citizen_charter').Path
$relative = 'Citizens Charter\Citizens-Charter_CS (2).pptx'
$classification = 'charter_candidate'
$out = Join-Path $env:USERPROFILE ('Bintanong\output\human-verification\' + [guid]::NewGuid().ToString('N'))

# Use installed dependencies and cached assets; do not install or download models.
$env:HF_HUB_OFFLINE = '1'
$env:TRANSFORMERS_OFFLINE = '1'
py -3.13 -B -m backend.bintanong_tools.document_ingest (Join-Path $root $relative) --root $root --out $out --locator 'owner-review:phase12-charter-cs' --classification $classification
if ($LASTEXITCODE -ne 0) { throw "Ingestion failed. Keep the error and partial folder; use a new output folder when retrying. Folder: $out" }

# Recheck the completed bundle before viewing it.
py -3.13 -B -c "import sys; from backend.bintanong_tools.document_ingest.bundle import load_candidate_bundle; b=load_candidate_bundle(sys.argv[1]); print(b['report']['counts']); print(b['report']['review_needs'])" $out
if ($LASTEXITCODE -ne 0) { throw 'Bundle integrity check failed; do not accept this output.' }

# Readable extraction goes NEXT TO the bundle. Extra files inside it invalidate its manifest.
$view = $out + '-extracted.md'
py -3.13 -B -c "import sys; from pathlib import Path; from docling_core.types.doc import DoclingDocument; p=Path(sys.argv[1]); d=DoclingDocument.model_validate_json((p/'conversion/raw_docling.json').read_text(encoding='utf-8')); Path(sys.argv[2]).write_text(d.export_to_markdown(), encoding='utf-8')" $out $view
if ($LASTEXITCODE -ne 0) { throw 'Readable export failed; retain the raw JSON and error.' }
Write-Host "Original: $(Join-Path $root $relative)"
Write-Host "Readable output: $view"
Write-Host "Pipeline report: $(Join-Path $out 'ingestion_report.json')"
Write-Host "Chunks: $(Join-Path $out 'chunks.json')"
```

Open the original in your PDF/PowerPoint viewer and the extracted Markdown in your editor (VS Code Markdown preview works if installed). The Markdown is only a convenience projection: check `conversion/raw_docling.json`, `conversion/procedure_candidates.json` and the report for exact item/table IDs, omissions and locators. Docling may warn that PPTX geometry is outside slide bounds and clamp it in the Markdown projection; that does not repair or certify provenance.

For another file, change `$relative`, `$classification` and the logical `--locator` label. Run the whole block again so `$out` is new. Keep outputs outside Git. Do not reuse a partial output folder, place review notes inside a bundle, or change a classification just to bypass a failure.

| Source | Classification |
| --- | --- |
| Charter PDF or PPTX | `charter_candidate` |
| Handbook, USG Constitution, Omnibus Election Code PDF | `policy_candidate` |
| BS Computer Science BOR proposal PDF | `curriculum_proposal_candidate` |

Known first-run limitations: `Citizens-Charter_CS.pdf` currently refuses with `raw reading order omits text or tables`. The two unique Charter PPTX variants complete but each emits zero chunks (52 text items and 15 tables withheld). Neither is a completed source-backed chunk-review success. The mixed/scanned long PDFs need explicit OCR handling; default PDF conversion uses OCR off. Stop at the first failure and report it rather than marking the source accepted.

## File checklist: all 15 copied paths

Paths are relative to `$root`. Check a box only after YOUR review. Identical SHA-256 files can share one content review, but each alias's acquisition/authority claims still need evidence. Matching names across formats do not establish equivalent content.

### Citizens Charter (11 files, 5 distinct hashes)

- [ ] `Citizens Charter/BS Computer Science_for BOR approval _rev02_v7_6 August 2025 (2).pdf` — 643 pages; `4ddcb8741b54…`; curriculum proposal, not proof of BOR approval. Mixed: 62 scanned, 7 unknown pages. Conversion not run.
- [ ] `Citizens Charter/Citizens-Charter_CS (2).pptx` — 17 slides; `4768b823b087…`; converted, all chunks withheld; human review pending.
- [ ] `Citizens Charter/Citizens-Charter_CS (3).pptx` — exact-byte alias of `(2).pptx`; preserve acquisition evidence.
- [ ] `Citizens Charter/Citizens-Charter_CS (4).pptx` — 17 slides; `e2923cae0716…`; converted, all chunks withheld; human review pending.
- [ ] `Citizens Charter/Citizens-Charter_CS.pptx` — exact-byte alias of `(4).pptx`; preserve acquisition evidence.
- [ ] `Citizens Charter/Citizens-Charter_CS.pdf` — 17 pages; `27a53568cc7e…`; fresh trial failed reading-order completeness; no completed bundle.
- [ ] `Citizens Charter/PALAWAN-STATE-UNIVERSITY-Citizens-Charter-2025-4th-Edition.pdf` — 117 pages; `42a93994e146…`; 104 native and 13 unknown pages; conversion not run.
- [ ] `Citizens Charter/PALAWAN-STATE-UNIVERSITY-Citizens-Charter-2025-4th-Edition (1).pdf` — exact-byte alias of the preceding PDF.
- [ ] `Citizens Charter/PALAWAN-STATE-UNIVERSITY-Citizens-Charter-2025-4th-Edition (2).pdf` — same exact-byte alias group.
- [ ] `Citizens Charter/PALAWAN-STATE-UNIVERSITY-Citizens-Charter-2025-4th-Edition (3).pdf` — same exact-byte alias group.
- [ ] `Citizens Charter/PALAWAN-STATE-UNIVERSITY-Citizens-Charter-2025-4th-Edition (4).pdf` — same exact-byte alias group.

### Student Handbook and Constitutions (4 files, 4 distinct hashes)

- [ ] `Student Handbook and Constitutions/764396659-Revised-Psu-Student-Handbook-2020.pdf` — 361 pages; `ed49075c722d…`; mixed, 1 scanned and 9 unknown pages; conversion not run. Confirm edition and acquisition authority independently.
- [ ] `Student Handbook and Constitutions/PSU Student Handbook.pdf` — 394 pages; `4c9a95bf6895…`; mixed, 1 scanned and 16 unknown pages; conversion not run. Do not infer that it replaces the other handbook.
- [ ] `Student Handbook and Constitutions/THE-2023-TINIGUIBAN-USG-Constitution (2).pdf` — 34 native pages; `b40cca9e22d8…`; conversion not run; confirm Tiniguiban scope and effectivity.
- [ ] `Student Handbook and Constitutions/The-PALAWAN-STATE-UNIVERSITY-Omnibus-Election-Code-1.pdf` — 21 native pages; `c46652fe5288…`; trial interrupted when the owner clarified the workflow; no completed bundle.

The original-source copy excludes old `_rag_index` Markdown/JSON, Docling caches, `redocling_handbook.py`, its test and bytecode. They remain untouched externally. They are not independent reference truth.

## Repeat this checklist for each distinct source

- [ ] Original opens; filename, full SHA-256, page/slide count and duplicate aliases agree with the copy manifest.
- [ ] Record visible title, issuer, edition/date, campus/college/program scope and acquisition evidence. Leave unstated facts unknown. Filename dates and `for BOR approval` wording do not prove authorization.
- [ ] Review every relevant original page/slide against the extracted text. Record reviewed pages explicitly; a sample is not full-document acceptance.
- [ ] Check missing/duplicated passages, heading/section ownership, reading order, printed versus physical page, punctuation, numbers, dates, fees, thresholds, negation, requirements and exceptions.
- [ ] Check table headers, row/column associations, merged cells, ordered steps, responsible offices and timings. A Markdown table looking plausible does not establish correct extraction.
- [ ] Compare each reviewed chunk with its exact original page/section and source spans. Record omitted/rejected items and missing chunk coverage. Check that qualifiers and exceptions stay attached to their rule.
- [ ] Flag scans, OCR-off omissions and illegible passages; do not invent missing text. No OCR accuracy or character-error-rate claim without a separately transcribed manual reference.
- [ ] Record conflicts between versions/formats without choosing authority from filename recency. Obtain source-owner adjudication where required.
- [ ] Log each decision as `accepted`, `corrected` or `unresolved`, with your reviewer name, actual date, full source hash, page/slide, candidate item/chunk ID and reason/correction. Preserve raw outputs; a corrected observation does not rewrite or approve the bundle.
- [ ] Keep source authority and extraction fidelity as separate decisions. Retain Lawrence's independent verdicts and disagreements; reconcile by source hash and exact location rather than overwriting either ledger.

Report back using: `file | hash | page/slide | item/chunk | accepted/corrected/unresolved | exact issue/correction`. Pending decisions cannot promote source/register states, approve rules, activate releases or serve as final benchmark answers.

## Prepared evidence and current measured results

Evidence root: `E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/phase12_human_20261012_37f9e9e2/`.

- `copy_manifest.json`: full hashes, original/copy paths and duplicate aliases; all 15 original/copy hashes unchanged at the final check.
- `inspection/inspection_report.json`: 15 healthy paths, 9 byte identities, zero inaccessible paths, zero page-accounting invariant errors. Text-layer classes are inspection heuristics, not OCR accuracy.
- `pending_source_register.json`: 9 governed pending versions, preserving all 15 acquisition locators; no approvals.
- `pytest.log`: **2,589 passed, 0 failed, 3 dependency deprecation warnings, 138.82s**, system Python 3.13.12. Focus: governance/contracts/evaluation, inspection, policy/procedure/chunk/report/bundle/prospectus ingestion, OCR gate and ingest hardening. This is not a full repository-suite claim.
- `conversion_results.json`: two checked PPTX bundles, one failed Charter PDF trial. Election-code trial was subsequently interrupted; other files were not converted. All batch processes were stopped.
- `human-review/source-01-extracted.md` and `source-02-extracted.md`: readable raw PPTX extractions; no human verification performed.
- `human-review/decisions.csv`: 45 pending rows (three review axes per copied path); reviewer/date/correction/authority fields blank. Add rows per specific finding/page. If Lawrence uses the template, make his own named copy.

Reproduce the automated gate without installs or database access:

```powershell
Set-Location 'C:\Users\Hawksprey\source\repos\Bintanong'
$temp = Join-Path $env:TEMP ('bintanong-phase12-' + [guid]::NewGuid().ToString('N'))
$testFiles = @(Get-ChildItem tests/test_contracts_*.py,tests/test_evaluation_*.py,tests/test_source_governance_manifests.py,tests/test_document_inspection.py,tests/test_policy_*.py,tests/test_procedure_text.py,tests/test_candidate_bundle.py,tests/test_ingestion_report.py,tests/test_prospectus_ingestion.py,tests/test_ocr_gate.py,tests/test_ingest_hardening.py | ForEach-Object FullName)
py -3.13 -B -m pytest -q @testFiles -p no:cacheprovider --basetemp $temp
```
