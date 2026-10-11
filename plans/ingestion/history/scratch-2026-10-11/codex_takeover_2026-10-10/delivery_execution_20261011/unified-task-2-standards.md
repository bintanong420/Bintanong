# Unified Task 2 independent Standards review

**PASS — APPROVED. Confirmed findings: NONE.**

Approval is limited to the full frozen Task 2 candidate's code quality and documented handoff behavior. It grants no merge/adoption, institutional source/content approval, activation or runtime release. This is a fresh separate Standards review following the independent Spec review and the ONE owner-authorized Medium Spec repair recheck; those reports were context, not proof. No fix or repair recheck was performed in this run.

## Scope and method

Full Task 2 range: `8f4c0a6c674ce33bcbe0fc91c76e03b4184da261..8cdb8cfdce03c69f718bb63390903b484437112a`.
Frozen candidate: `unified-task-2-review-8cdb8cfd/candidate` (373 files).

Read review-common.md completely first; read its exact extractor-reviewer role, Claude code-quality reviewer/requesting-review templates and Codex reviewer template, complete Task2 brief, exact unified_ingestion_design/SPEC.md and IMPLEMENTATION_PLAN.md. Read prior Spec and Spec-recheck reports as context. Inspected all six actual changed files and the interacting register, inspection/output preflight, identity, loader, converter factory, extractor payload/authority, source/chunk/span contracts, procedure reader, policy chunker and ingestion-report helpers. Reviewed the full Task 2 change, not merely the repair package patch. A lightweight memory registry lookup added no candidate-specific proof; the current task documents/code controlled the assessment.

The six changed paths are document_ingest/__main__.py, bundle.py, prospectus.py, docs/decisions/phase-02-unified-ingestion.md, tests/test_candidate_bundle.py and tests/test_prospectus_ingestion.py. No protected extractor/loader/contracts change is present in this range. Live worktree HEAD `84eba1c4e14c615d03cfbf854e61ffbba9599e19` is the later Phase6 checkpoint; it was neither required to equal the archive HEAD nor reviewed as Task2 code.

## Strengths

- The wrapper uses the existing captured snapshot, pending register, loader seam, curriculum parser/audit, chunk binder and atomic writer. It adds no competing extraction or governance framework and keeps the original APIs intact.
- Identity/output/register/settings preflight precedes conversion. The strict converter rejects errors and explicit non-success before raw export or the loader's fallback, rechecks actual exposed options/settings after conversion, and preserves missing status as null. Regression cases poison/count actual conversion/writer calls rather than accepting an eventual exception as sufficient proof.
- Captured-PDF geometry is retained independently of raw converter geometry, including blocked audits; page and document resources are closed. Accounting distinguishes emitted chunks, binding rejections and extractor rejections. Failed audits remain complete diagnostic candidates with no ready chunks.
- Publication retains structured curriculum/audit and raw conversion inputs, omits the legacy Prolog view, hashes exact artifact sets and publishes root completion last. The checked consumer hashes the bytes it parses, rejects duplicate JSON keys, unsafe/missing/extra files and inconsistent identities, reparses governed records/spans and rebuilds expected handoff accounting. Pending review/source states are not promoted.
- CLI classification remains explicit; existing generic dispatch is retained and success summaries now come from checked consumption. Tests exercise the real curriculum parser/audit and policy/procedure readers with synthetic conversion execution rather than mocking the entire behavior under review. Documentation states both the artifact contract and the limits of integrity/attestation.

## Issues

Critical: **NONE**.

Important: **NONE**.

Minor: **NONE**. No optional feature or style-only blocker is proposed.

## Independently executed evidence

Archive-origin assertions passed, exit 0, for prospectus, bundle, institutional pipeline, loader, docling_env, identity and source contracts. Every resolved module.__file__ was beneath the absolute frozen candidate. Evidence: `unified-task-2-standards-imports.log`.

Required seven-file suite: **211 passed in 37.36s, exit 0**, no skips/errors. Evidence: `unified-task-2-standards-tests.log`. This includes the combined synthetic CLI/library smoke and all three cached-default settings regression cases. It is an independent Standards execution, not the implementer's or Spec review's count.

Exact successful test command:

```powershell
Set-Location -LiteralPath 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$taskDelivery='E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011'
$taskArchive="$taskDelivery/unified-task-2-review-8cdb8cfd/candidate"
$env:PYTHONPATH=$taskArchive
$env:PYTHONDONTWRITEBYTECODE='1'
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
$env:HF_DATASETS_OFFLINE='1'
$env:PIP_NO_INDEX='1'
Set-Location -LiteralPath $taskArchive
py -3.13 -B -m pytest "$taskArchive/tests/test_prospectus_ingestion.py" "$taskArchive/tests/test_candidate_bundle.py" "$taskArchive/tests/test_ingestion_report.py" "$taskArchive/tests/test_policy_chunks.py" "$taskArchive/tests/test_policy_text.py" "$taskArchive/tests/test_procedure_text.py" "$taskArchive/tests/test_register_minting.py" -q -p no:cacheprovider --rootdir $taskArchive --confcutdir $taskArchive -o faulthandler_timeout=30 --basetemp "$taskDelivery/unified-task-2-standards-pytest-20261011-1057" *> "$taskDelivery/unified-task-2-standards-tests.log"
$testExit=$LASTEXITCODE
Get-Content -LiteralPath "$taskDelivery/unified-task-2-standards-tests.log"
"pytest_exit=$testExit" | Tee-Object -FilePath "$taskDelivery/unified-task-2-standards-tests.log" -Append
Set-Location -LiteralPath 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
exit $testExit
```

A small external assert-based compatibility check additionally exercised existing PDF procedure publication with printed page label `iv`, and PPTX procedure publication through the new consumer. Both passed, exit 0. PDF labels survived; PPTX remained technically complete with zero ready chunks and explicit `pending_locator_contract` rejection. The original synthetic bytes stayed unchanged. This closed the consumer-specific compatibility question without rerunning a broad suite.

Source: `unified-task-2-standards-compat.py`; output: `unified-task-2-standards-compat.log`. With the identical archive cwd/process-only environment above, its exact execution was:

```powershell
py -3.13 -B "$taskDelivery/unified-task-2-standards-compat.py" *> "$taskDelivery/unified-task-2-standards-compat.log"
$compatExit=$LASTEXITCODE
Get-Content -LiteralPath "$taskDelivery/unified-task-2-standards-compat.log"
"compat_exit=$compatExit" | Tee-Object -FilePath "$taskDelivery/unified-task-2-standards-compat.log" -Append
```

`git diff --check 8f4c0a6c674ce33bcbe0fc91c76e03b4184da261 8cdb8cfdce03c69f718bb63390903b484437112a` passed, exit 0.

## Integrity and boundaries

Before and after review independently verified all **373 manifest-listed SHA-256 hashes AND the exact recursive actual file set**, with no symlinks. Both passed. The archive's six changed-file contents also matched supplied Git head blobs after CRLF normalization. Full-task patch bytes matched `git diff --binary 8f4c0a6c... 8cdb8cfd...` exactly before and after. The package patch/stat matched its own repair range `361b5ad4...8cdb8cfd...`, not the full task range.

Before/after package hashes were identical:

- manifest.json: `972e4c314a177ed8b95aee60ba463a796a0c8b126d1735da810639afde420b8c`
- change.patch: `2c7ffacd75799d34cb3b7200556eee9681dd39ff20b6ca989b169fa39eac546c`
- change-stat.txt: `bce1dbcde3824b20daa21c020d8f465cdf9ff088cf5d51a8e593ddfcc00243d3`
- full Task2 patch: `0260a3fdd62fa4e6e8d55c473c33d8008006556482eb485bd8b423a699e0f5c0`

Evidence: `unified-task-2-standards-integrity-before.json` and `unified-task-2-standards-integrity-after.json`. Live worktree remained clean with unchanged HEAD, index hash and complete refs hash. No source/archive/index/ref writes, descendants, installs/downloads, dependencies/lock/config changes, model inference, private actual inputs, API/Docker, embedding/routing or Prolog execution occurred. Review logs/report/assert reproducer were written only externally under D. The mandated usage helper writes its own external records under parent E.

Read the exact READ_ONLY_CODEX_USAGE.ps1 fully and queried actual Codex metadata independently. Initial 10:52:32 Manila: 10% primary/29% weekly; final 10:56:33: 18%/30%. Both below stop/save thresholds. Restored the actual worktree cwd after usage queries and tests.

## Declined to judge

- Original-corpus extraction accuracy, original-PDF visual correctness, curriculum completeness and issuing-office/domain approval: this task verifies the synthetic preparation/handoff boundary; original-corpus and human/source review remain explicitly separate work.
- OCR accuracy, ten independent references and real phone photographs: no actual OCR/model conversion or hardware measurement was requested/authorized in this review.
- Arbitrary opaque injected-converter truthfulness: the explicit caller attestation is documented; actual exposed Docling options and installed package versions are checked. The seam does not authenticate arbitrary Python implementations.
- Authentication of a producer able to replace every artifact, metadata and manifest hash: this local bundle contract provides internal integrity and pending authority, not signatures or independent original-PDF authenticity. Documentation says so explicitly.
- Missing converter status: the contract rejects explicit non-success; an absent status remains null and is not invented as success. Requiring every injected converter to provide status would change the documented seam.
- Concurrent jobs intentionally sharing one output directory: not executed; the researcher workflow requires distinct new/empty output folders, and shared-output locking/resume is not part of Task2. No concurrency guarantee is awarded.
- Reviewed/promoted-register ingestion and institutional activation: deliberately refused by the pending-only preparation API; no new approval path was requested.
- Exact tokenizer counts and the 512-token requirement: reserved for Phase3; this boundary truthfully reports estimate-v1.
- Private lifecycle/deletion, embeddings, storage/release activation, API/Docker/routing/runtime and executable rule compilation: expressly outside this isolated candidate review.
- Historical M1/F/session defects and repair claims, including the historical mutation claim: not rechecked or cleared by the new wrapper's tests or this approval. Existing review debts remain.
- Later Phase6 checkpoint code and future Task3 field-level mapping: outside the supplied full Task2 range; retained raw/domain handoff inputs do not certify their later consumers.

## Recommendations and assessment

No required Task2 correction or additional optional implementation is recommended from this review. Preserve the documented deferred checks and review debts when recording progress.

**Assessment: PASS — APPROVED for frozen full Task2 candidate Standards.** Source/content approval, adoption/merge and runtime release are not granted or assessed. The new boundary is coherent, tested and fail-closed for the concrete malformed/partial/mismatched/interrupted cases in scope; its integrity and authority claims remain appropriately bounded.

Skipped: broad ~4k suite, actual original-corpus/OCR/private/runtime work and historical debt rechecks. Risk: synthetic conversion and internal bundle integrity do not establish institutional accuracy, producer authenticity or authorization.
