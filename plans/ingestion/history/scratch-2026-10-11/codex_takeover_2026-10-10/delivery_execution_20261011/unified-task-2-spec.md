# Unified Task 2 independent SPEC review

Verdict: **FAIL — CHANGES NEEDED**. One confirmed Medium finding. This is a candidate specification review only; it grants no adoption, merge, source/content approval, institutional use or activation.

Scope: `8f4c0a6c674ce33bcbe0fc91c76e03b4184da261..361b5ad41af7d5f202a8152edc0ae989c171f2a2`.
Frozen package: `unified-task-2-review-361b5ad4`; 373 candidate files.

## Specification

Read the full review-common.md, unified-task-2-brief.md, exact unified_ingestion_design/SPEC.md and IMPLEMENTATION_PLAN.md, extractor-reviewer.md and spec-reviewer-prompt.md. Inspected all six changed files directly and interacting register, inspection, loader, identity, Docling factory, extractor payload/authority, report, procedure reader and chunk contracts. Implementer reports were context only.

The implementation meets the requested pending-only registration, explicit PDF/snapshot/output preflight, strict status/error refusal before raw export, captured geometry with closed resources, no ambient semantic lookup, structured domain payload retention, omission of legacy Prolog/helper export, Task1 binding and candidate/rejection accounting, blocked audit diagnostics, atomic manifest-last publication, exact artifact sets, duplicate-key/path/symlink refusal, checked typed source/chunk/span consumption, domain/raw conversion return, and checked CLI summary. Existing five classifications remain accepted in the independently run suite. No unrelated extractor/loader/contracts changes appear in the six-file diff. The following actual-settings requirement is incomplete.

### M-T2-S1 — default shared converter bypasses actual-settings verification

Severity: **Medium**.
Location: `backend/bintanong_tools/document_ingest/prospectus.py:243-248`, with the conditional guard at `:139`.

The injected-converter path compares introspectable backend/options/languages/installed versions against declared metadata before and after conversion. The default path takes conversion_settings(), fetches the existing mutable cached converter, and constructs `_StrictConverter(..., attested=False)`. The guard therefore skips actual-options verification for that real Docling converter. Existing `docling_env.get_shared_converter` returns its cached mutable instance under the settings key; changing the returned instance's PDF pipeline options does not update that key.

Concrete reproduction: construct the actual existing shared Docling converter with default settings (do_ocr=False), change its actual PDF `pipeline_options.do_ocr` to True, replace only its conversion execution with the existing synthetic converter to avoid model/network work, and call `run_prospectus_ingestion` without a converter argument. The default factory returns the same actual converter. The wrapper publishes the complete root manifest and `load_candidate_bundle` accepts it, while metadata/report declare do_ocr=False and actual converter options are True. The reproduction uses actual installed DocumentConverter and PdfFormatOption/PdfPipelineOptions objects; it is not an opaque custom-converter attestation dispute.

External reproducer: `unified-task-2-spec-default-settings-repro.py`; exact output: `unified-task-2-spec-default-settings-repro.log`. Result: exit 0, **1 passed in 13.29s**, asserting the mismatch and accepted manifest. Printed result: `REPRODUCED: real shared Docling converter do_ocr=True, published/consumed metadata do_ocr=False`.

Impact: a source/settings-bound complete candidate can falsely describe the actual conversion configuration. The conversion identity then binds the declared settings rather than the settings used by the mutable cached converter. This violates Task2's actual-settings/reject-unverifiable-settings requirement and changed-settings refusal. Pending review state prevents institutional activation, but does not repair this integrity defect. The fix belongs at the new wrapper seam, without changing the protected loader or rechecking historical M1.

Required correction: verify the default introspectable converter's backend/options against the supplied settings before conversion and verify them again before raw export, as for the injected real Docling path. Add a focused regression covering cached default options drift; no dependency/framework expansion is needed.

## Independent evidence

The seven requested focused files passed independently: **208 passed in 23.76s, exit 0**, no skips/errors. Log: `unified-task-2-spec-tests.log`. The combined CLI/library smoke is already one test within that suite; no separate root smoke rerun was made.

Exact test invocation (all variables resolve to the shown absolute paths):

```powershell
Set-Location -LiteralPath 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$A='E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/unified-task-2-review-361b5ad4/candidate'
$env:PYTHONPATH=$A
$env:PYTHONDONTWRITEBYTECODE='1'
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
$env:HF_DATASETS_OFFLINE='1'
$env:PIP_NO_INDEX='1'
Set-Location -LiteralPath $A
py -3.13 -B -m pytest "$A/tests/test_prospectus_ingestion.py" "$A/tests/test_candidate_bundle.py" "$A/tests/test_ingestion_report.py" "$A/tests/test_policy_chunks.py" "$A/tests/test_policy_text.py" "$A/tests/test_procedure_text.py" "$A/tests/test_register_minting.py" -q -p no:cacheprovider --basetemp 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/unified-task-2-spec-pytest-20261011-0254'
Set-Location -LiteralPath 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
```

Before pytest, a separate `py -3.13 -B -` assertion imported prospectus, bundle and loader, resolved each module.__file__, asserted the absolute frozen candidate directory was in its parents, and printed all three archive origins. All passed, exit 0. Tests ran from the archive with process-only PYTHONPATH exactly equal to that archive.

Exact reproduction pytest invocation, with the same process-only offline/no-bytecode environment and archive cwd established above:

```powershell
py -3.13 -B -m pytest 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/unified-task-2-spec-default-settings-repro.py' -q -s -p no:cacheprovider --basetemp 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/unified-task-2-spec-settings-repro-temp-0300'
```

The reproduction's actual source is retained externally and contains the complete setup/assertions; only execution is synthetic, not converter/options construction. No real private input, model inference, network conversion or Prolog execution occurred.

## Integrity and boundaries

Both before and after review, independently checked all **373 SHA-256 hashes AND the exact recursive file set** against the package manifest. Both passed. The three package hashes remained identical:

- manifest.json: `807bcba51462b240d28d9d4650b396573d46a34c558972ec0de0be449c886bad`
- change.patch: `f1fbae5d19a640c218054f359d18e73fc4621bded28a85b626d1e6c0875d3690`
- change-stat.txt: `1b43752747e6429a86e98639f996cb94cdb7c6d42c6e3c9a307253e9e800cc45`

Evidence: `unified-task-2-spec-integrity-before.json` and `unified-task-2-spec-integrity-after.json`. Also matched the six archive changed files to HEAD after CRLF normalization, checked clean worktree status and unchanged supplied HEAD, and ran `git diff --check BASE HEAD` successfully. An additional raw Git-blob hash comparison initially failed because archive checkout bytes use CRLF; the corrected normalized comparison passed. This did not affect the exact manifest hash checks, which passed unchanged.

Fresh exact READ_ONLY_CODEX_USAGE.ps1 was read and executed independently: initial 02:53:21 Manila 56% primary/22% weekly; final queried 02:56:18 Manila 62% primary/23% weekly. Neither stop/save threshold was reached. Actual worktree cwd was restored after usage queries/testing. No worktree/archive/index/ref writes, staging, commits or descendants. Review report/reproducer/logs were written only in external delivery D. Standards has not started.

## Deferred scope and limits

This review checks source/settings/artifact integrity and requested behavior; it does not certify original-corpus extraction accuracy, office/domain approval, OCR accuracy, actual phone photographs, tokenizer/512-token accounting, private lifecycle, embeddings, API/Docker/routing/runtime release, inactive-rule compilation or historical M1/F/session debts. The seven-file suite uses synthetic conversion execution, and the focused additional reproduction uses a real installed default converter's options without running model inference. No optional feature/style-only blocker was introduced.

**CHANGES NEEDED — M-T2-S1 (Medium).**
