# Unified Task 2 implementer report

Status: DONE. Awaiting coordinator independent acceptance, local draft commit and separate reviews. No staging or commits performed by this implementer.

Baseline: clean `8f4c0a6c674ce33bcbe0fc91c76e03b4184da261`; HEAD unchanged. Worktree: `C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010`.

## Implemented

- Strict prospectus wrapper uses the actual existing loader, parser/audit and Task 1 binder. Captured source/register/output preflight runs before converter or writer calls. Conversion errors and explicit non-success statuses refuse before loader raw export or implicit backend fallback.
- Injected conversion settings are explicit caller attestations; absent or malformed declarations refuse. Known Docling backend and actual pipeline options are checked when exposed, and settings are rechecked after conversion. Default converter uses the existing factory/settings path. Metadata records actual seam settings/backend, identity, nullable actual status and settings basis.
- Captured PDF page sizes are read with explicit page closure and document context closure, retained in hash-checked metadata even when audit suppresses chunks, and checked against raw converter page-size claims within 0.01 points.
- Published prospectus payload retains structured courses, provenance, audit, unresolved prerequisites and candidates, removes the entire legacy Prolog/helper view, and clears the misleading production-emitted diagnostic flag. Failed audits stay blocked diagnostic candidates with no ready chunks. Reports retain every extraction rejection and account for every binding candidate.
- Both manifests hash exact sets; root is last, pending and candidate-only. Interrupted outputs cannot be consumed or reused as retry targets. Shared consumer rejects changed hashes/settings/raw, missing/false completion, duplicate JSON keys, unknown files/kinds, unsafe paths/symlinks and foreign/null span versions; reparses register/chunks and reconstructs policy/procedure reports and prospectus binding/accounting.
- CLI adds prospectus_candidate, retains all five existing classifications/flags, and uses the checked bundle for success summary. Help initializes no converter.

Exact six changed paths:

1. backend/bintanong_tools/document_ingest/prospectus.py
2. backend/bintanong_tools/document_ingest/bundle.py
3. backend/bintanong_tools/document_ingest/__main__.py
4. tests/test_prospectus_ingestion.py
5. tests/test_candidate_bundle.py
6. docs/decisions/phase-02-unified-ingestion.md

## Test-first execution

Read the exact brief, current unified SPEC and IMPLEMENTATION_PLAN, extractor-implementer role, implementer prompt Markdown and Codex TDD skill/reference. Actual child was Codex; no Claude invocation, descendants, installs or downloads. User's focused Python 3.13/offline constraints superseded role uv/full-suite instructions. Only synthetic source bytes were used. No actual private inputs or corpus artifacts were read.

The following are the full executed test invocations; logs retain full pytest output. The actual shell captured `$LASTEXITCODE`, displayed the log tail, then exited with that code.


### Initial RED fixture characterization

```powershell
Set-Location -LiteralPath 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'; $env:PYTHONPATH='C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'; $env:PYTHONDONTWRITEBYTECODE='1'; $env:HF_HUB_OFFLINE='1'; $env:TRANSFORMERS_OFFLINE='1'; py -3.13 -B -m pytest 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_prospectus_ingestion.py' 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_candidate_bundle.py' -q -p no:cacheprovider --basetemp 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\tmp-task2-red-1' *> 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-2-red.log'; $testExit=$LASTEXITCODE; Get-Content -LiteralPath 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-2-red.log' -Tail 12; Write-Output "RED_EXIT=$testExit"; exit $testExit
```

Actual exit: 1. 1 failed, 20 passed, 35 errors in 1.13s; PdfPage does not implement context-manager protocol. Fixture corrected to explicit close before production changes.


### Corrected feature RED

```powershell
Set-Location -LiteralPath 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'; $env:PYTHONPATH='C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'; $env:PYTHONDONTWRITEBYTECODE='1'; $env:HF_HUB_OFFLINE='1'; $env:TRANSFORMERS_OFFLINE='1'; py -3.13 -B -m pytest 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_prospectus_ingestion.py' 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_candidate_bundle.py' -q -p no:cacheprovider --basetemp 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\tmp-task2-red-2' *> 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-2-red-corrected.log'; $testExit=$LASTEXITCODE; Get-Content -LiteralPath 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-2-red-corrected.log' -Tail 8; Write-Output "RED_EXIT=$testExit"; exit $testExit
```

Actual exit: 1. 36 failed, 20 passed in 40.29s; failures name missing publisher, consumer, and prospectus CLI choice; no setup errors.


### Initial GREEN

```powershell
Set-Location -LiteralPath 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'; $env:PYTHONPATH='C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'; $env:PYTHONDONTWRITEBYTECODE='1'; $env:HF_HUB_OFFLINE='1'; $env:TRANSFORMERS_OFFLINE='1'; py -3.13 -B -m pytest 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_prospectus_ingestion.py' 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_candidate_bundle.py' -q -p no:cacheprovider --basetemp 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\tmp-task2-green-1' *> 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-2-green-1.log'; $testExit=$LASTEXITCODE; Get-Content -LiteralPath 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-2-green-1.log' -Tail 14; Write-Output "GREEN_EXIT=$testExit"; exit $testExit
```

Actual exit: 0. 56 passed in 27.72s.


### Settings adversarial RED

```powershell
Set-Location -LiteralPath 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'; $env:PYTHONPATH='C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'; $env:PYTHONDONTWRITEBYTECODE='1'; $env:HF_HUB_OFFLINE='1'; $env:TRANSFORMERS_OFFLINE='1'; py -3.13 -B -m pytest 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_prospectus_ingestion.py' 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_candidate_bundle.py' -q -p no:cacheprovider --basetemp 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\tmp-task2-red-3' *> 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-2-red-settings.log'; $testExit=$LASTEXITCODE; Get-Content -LiteralPath 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-2-red-settings.log' -Tail 10; Write-Output "RED_EXIT=$testExit"; exit $testExit
```

Actual exit: 1. 2 failed, 69 passed in 20.07s; null version attestation and absent actual PDF options were accepted. Both fixed at the settings seam.


### Geometry adversarial RED

```powershell
Set-Location -LiteralPath 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'; $env:PYTHONPATH='C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'; $env:PYTHONDONTWRITEBYTECODE='1'; $env:HF_HUB_OFFLINE='1'; $env:TRANSFORMERS_OFFLINE='1'; py -3.13 -B -m pytest 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_prospectus_ingestion.py::test_raw_geometry_cannot_override_captured_pdf_size' 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_candidate_bundle.py::test_blocked_audit_still_requires_captured_page_geometry' -q -p no:cacheprovider --basetemp 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\tmp-task2-red-geometry' *> 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-2-red-geometry.log'; $testExit=$LASTEXITCODE; Get-Content -LiteralPath 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-2-red-geometry.log' -Tail 8; Write-Output "RED_EXIT=$testExit"; exit $testExit
```

Actual exit: 1. 2 failed in 13.10s; producer raw geometry mismatch and blocked consumer missing capture were accepted. Shared captured-geometry check added.


### Required focused GREEN before acceptance clarification

```powershell
Set-Location -LiteralPath 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'; $env:PYTHONPATH='C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'; $env:PYTHONDONTWRITEBYTECODE='1'; $env:HF_HUB_OFFLINE='1'; $env:TRANSFORMERS_OFFLINE='1'; py -3.13 -B -m pytest 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_prospectus_ingestion.py' 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_candidate_bundle.py' 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_ingestion_report.py' 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_policy_chunks.py' 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_policy_text.py' 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_procedure_text.py' 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_register_minting.py' -q -p no:cacheprovider --basetemp 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\tmp-task2-green-complete' *> 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-2-green-complete.log'; $testExit=$LASTEXITCODE; Get-Content -LiteralPath 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-2-green-complete.log' -Tail 15; Write-Output "GREEN_EXIT=$testExit"; exit $testExit
```

Actual exit: 0. 204 passed in 22.72s; no skips or errors.


## Independent origin/scope checks

Initial and final Python processes independently asserted imports originate inside the candidate worktree. Final check covered backend namespace paths, new prospectus/bundle, generic pipeline, protected loader and source contracts. Actual exit 0; full paths in `unified-task-2-imports.log`. PYTHONPATH pointed exactly to this worktree, with bytecode disabled; no global configuration changed.

`git diff --check` exit 0. Final allowed-path equality assertion, empty staged-index assertion, unchanged HEAD assertion and explicit protected loader/extractor pipeline/generic pipeline/contracts diffs all passed (exit 0). Hashes and exact scope saved in `unified-task-2-final-scope.json`. Git emitted only existing LF/CRLF working-copy notices, not diff-check errors. No protected source edits.

## Stable combined synthetic smoke for root

This single node runs both prospectus and policy CLI routes and reads each output through the public checked library consumer. Conversion is synthetic; real parser/audit/readers/publication/binding/consumer/CLI execute. It passed within the final 208-test run; coordinator can independently run it with a new external basetemp:

```powershell
Set-Location -LiteralPath 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'; $env:PYTHONPATH='C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'; $env:PYTHONDONTWRITEBYTECODE='1'; $env:HF_HUB_OFFLINE='1'; $env:TRANSFORMERS_OFFLINE='1'; py -3.13 -B -m pytest 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_candidate_bundle.py::test_combined_synthetic_cli_library_smoke' -q -p no:cacheprovider --basetemp 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\tmp-task2-root-smoke-NEW'
```

## Task 3 handoff

`load_candidate_bundle(path)` returns reparsed `source_register` and `chunks`, `report`, `document_kind`, `candidate_only=True` and `review_eligible=False`. Prospectus-only entries: `domain_payload` is hash-checked prospectus_candidates.json; `conversion['raw_docling']` is captured hash-checked raw Docling JSON; `conversion['metadata']` is hash-checked source/settings/raw/status identity metadata. Captured geometry is `conversion['metadata']['pdf_page_sizes']`, physical-page string -> [width,height] points. It remains present for blocked audits. Field binding must derive exact per-field raw-cell support; bundle integrity does not certify extraction accuracy or authenticate a malicious producer replacing all hashes.

## Usage and limits

Fresh local READ_ONLY_CODEX_USAGE.ps1 RPC checks were read and run exactly, restoring candidate cwd afterwards. Readings: 02:26:03 Manila 26% primary/18% secondary; 02:32:31 35%/19%; 02:37:33 40%/20%; 02:41:35 43%/20%; latest 02:46:03 49%/21%. No stop threshold reached. Baseline/latest state saved externally; no owner write, protected ref movement or attribution.

Skipped as directed: full ~4k suite, original corpus/office/OCR/private-lifecycle validation, API/Docker/routing/embedding/Prolog execution, commits and independent reviews. Historical generic M1 repair remains independently unrechecked; this new strict converter boundary is separate evidence. Candidate technical completion grants no source/content approval, active release or executable rule authority.

## Coordinator acceptance clarification and final rerun

Coordinator requested checking enabled OCR language declarations against actual existing options and real-options package declarations against installed_versions(). Added narrow tests first; observed both gaps, then added the small shared-seam checks. Opaque synthetic/custom converter metadata remains an explicit caller attestation; exposed real Docling options additionally verify backend, pipeline settings, enabled OCR languages and installed package versions. No OCR integration, new dependency or profile framework.

### Acceptance OCR-language RED

```powershell
Set-Location -LiteralPath 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'; $env:PYTHONPATH='C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'; $env:PYTHONDONTWRITEBYTECODE='1'; $env:HF_HUB_OFFLINE='1'; $env:TRANSFORMERS_OFFLINE='1'; py -3.13 -B -m pytest 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_prospectus_ingestion.py::test_injected_docling_ocr_languages_must_match_actual_options' -q -p no:cacheprovider --basetemp 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\tmp-task2-red-languages' *> 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-2-red-languages.log'; $testExit=$LASTEXITCODE; Get-Content -LiteralPath 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-2-red-languages.log' -Tail 10; Write-Output "RED_EXIT=$testExit"; exit $testExit
```

Actual exit 1. 1 failed in 15.61s. Real-options enabled OCR declaration did not match ocr_options.lang yet was accepted.

### Acceptance language GREEN

```powershell
Set-Location -LiteralPath 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'; $env:PYTHONPATH='C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'; $env:PYTHONDONTWRITEBYTECODE='1'; $env:HF_HUB_OFFLINE='1'; $env:TRANSFORMERS_OFFLINE='1'; py -3.13 -B -m pytest 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_prospectus_ingestion.py' 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_candidate_bundle.py' 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_ingestion_report.py' 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_policy_chunks.py' 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_policy_text.py' 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_procedure_text.py' 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_register_minting.py' -q -p no:cacheprovider --basetemp 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\tmp-task2-green-languages' *> 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-2-green-languages.log'; $testExit=$LASTEXITCODE; Get-Content -LiteralPath 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-2-green-languages.log' -Tail 15; Write-Output "GREEN_EXIT=$testExit"; exit $testExit
```

Actual exit 0. 205 passed in 21.10s.

### Acceptance package-version RED

```powershell
Set-Location -LiteralPath 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'; $env:PYTHONPATH='C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'; $env:PYTHONDONTWRITEBYTECODE='1'; $env:HF_HUB_OFFLINE='1'; $env:TRANSFORMERS_OFFLINE='1'; py -3.13 -B -m pytest 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_prospectus_ingestion.py::test_injected_docling_versions_must_match_installed_packages' -q -p no:cacheprovider --basetemp 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\tmp-task2-red-versions' *> 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-2-red-versions.log'; $testExit=$LASTEXITCODE; Get-Content -LiteralPath 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-2-red-versions.log' -Tail 10; Write-Output "RED_EXIT=$testExit"; exit $testExit
```

Actual exit 1. 3 failed in 12.83s. Each of docling/docling-core/docling-parse accepted a forged version in the real-options seam.

### FINAL focused GREEN

```powershell
Set-Location -LiteralPath 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'; $env:PYTHONPATH='C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'; $env:PYTHONDONTWRITEBYTECODE='1'; $env:HF_HUB_OFFLINE='1'; $env:TRANSFORMERS_OFFLINE='1'; py -3.13 -B -m pytest 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_prospectus_ingestion.py' 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_candidate_bundle.py' 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_ingestion_report.py' 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_policy_chunks.py' 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_policy_text.py' 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_procedure_text.py' 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_register_minting.py' -q -p no:cacheprovider --basetemp 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\tmp-task2-green-final' *> 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-2-green-final.log'; $testExit=$LASTEXITCODE; Get-Content -LiteralPath 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-2-green-final.log' -Tail 15; Write-Output "GREEN_EXIT=$testExit"; exit $testExit
```

Actual exit 0. 208 passed in 21.41s; no skips/errors.

Final independent import-origin checks repeated after acceptance clarification: exit 0 (`unified-task-2-imports-final.log`). Final scope/hash assertions and `git diff --check` repeated: exit 0, only six allowed paths, no staging, HEAD unchanged, protected files unchanged. `unified-task-2-final-scope.json` contains final hashes. Smoke command quoting is corrected. No further test runs are needed from the implementer; coordinator handles independent acceptance/reviews/commit.
Final fresh quota at 02:47:45 Manila: 51% primary, 22% secondary; ordinary usage allowed, no stop/save threshold. Implementer work complete; pending coordinator acceptance and reviews.


## Confirmed Spec Medium repair M-T2-S1

Repair status: IMPLEMENTED; independent Medium recheck remains pending the owner-specific exception. This is implementation evidence, not a Spec/Standards verdict or review clearance. No staging/commit/descendants performed. Current unchanged HEAD: 361b5ad41af7d5f202a8152edc0ae989c171f2a2.

Read the entire unified-task-2-spec.md and retained unified-task-2-spec-default-settings-repro.py. The confirmed issue was the default cached mutable converter skipping actual settings verification because attested=False. Reproduced with the existing external script against actual candidate backend imports; real installed DocumentConverter/options were constructed, while conversion execution alone remained synthetic. No model inference/download/network work.

Only two paths changed: document_ingest/prospectus.py and tests/test_prospectus_ingestion.py. The shared settings helper now accepts explicit factory settings and requires introspectable default options. The wrapper checks actual cached backend/options/languages/installed package versions against those supplied settings before conversion; the strict seam repeats that validation before raw export. Injected opaque converters retain the bounded explicit-attestation behavior. Protected loader, factory, extractor, contracts and generic pipeline are unchanged. No ADR update is needed: the repair fulfills the documented actual-settings invariant rather than changing the interface.

Regression uses an actual installed shared converter, isolates its cache and replaces only execution. Before-convert drift must make zero converter and writer calls; during-convert drift must make one converter call and zero writer calls. Both retain unchanged source bytes and an untouched preexisting empty output. The unchanged default path publishes and consumes normally, without model execution.

Full exact test commands and observed exits follow; shell captures the real $LASTEXITCODE and exits with it.

### Retained external reproducer, initial harness

```powershell
Set-Location -LiteralPath 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'; $env:PYTHONPATH='C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'; $env:PYTHONDONTWRITEBYTECODE='1'; $env:HF_HUB_OFFLINE='1'; $env:TRANSFORMERS_OFFLINE='1'; $env:HF_DATASETS_OFFLINE='1'; $env:PIP_NO_INDEX='1'; py -3.13 -B -m pytest 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-2-spec-default-settings-repro.py' -q -s -p no:cacheprovider --basetemp 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\tmp-task2-fix-existing-repro' *> 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-2-fix-existing-repro.log'; $testExit=$LASTEXITCODE; Get-Content -LiteralPath 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-2-fix-existing-repro.log' -Tail 12; Write-Output "REPRO_EXIT=$testExit"; exit $testExit
```

Actual exit 4. 1 collection error in 0.24s; pytest attempted E:/WpSystem/__init__.py and Windows returned invalid security ID. No product behavior reached. Corrected only pytest rootdir/confcutdir.

### Retained external reproducer, rooted harness

```powershell
Set-Location -LiteralPath 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'; $env:PYTHONPATH='C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'; $env:PYTHONDONTWRITEBYTECODE='1'; $env:HF_HUB_OFFLINE='1'; $env:TRANSFORMERS_OFFLINE='1'; $env:HF_DATASETS_OFFLINE='1'; $env:PIP_NO_INDEX='1'; py -3.13 -B -m pytest 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-2-spec-default-settings-repro.py' -q -s -p no:cacheprovider --rootdir 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011' --confcutdir 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011' --basetemp 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\tmp-task2-fix-existing-repro-rooted' *> 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-2-fix-existing-repro-rooted.log'; $testExit=$LASTEXITCODE; Get-Content -LiteralPath 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-2-fix-existing-repro-rooted.log' -Tail 12; Write-Output "REPRO_EXIT=$testExit"; exit $testExit
```

Actual exit 0. 1 passed in 15.58s; printed REPRODUCED real shared do_ocr=True while published/consumed metadata=False. This is bug reproduction, not desired behavior.

### Desired regression RED

```powershell
Set-Location -LiteralPath 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'; $env:PYTHONPATH='C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'; $env:PYTHONDONTWRITEBYTECODE='1'; $env:HF_HUB_OFFLINE='1'; $env:TRANSFORMERS_OFFLINE='1'; $env:HF_DATASETS_OFFLINE='1'; $env:PIP_NO_INDEX='1'; py -3.13 -B -m pytest 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_prospectus_ingestion.py::test_default_cached_converter_settings_checked_before_and_after_conversion' -q -p no:cacheprovider --basetemp 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\tmp-task2-fix-red' *> 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-2-fix-red.log'; $testExit=$LASTEXITCODE; Get-Content -LiteralPath 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-2-fix-red.log' -Tail 12; Write-Output "RED_EXIT=$testExit"; exit $testExit
```

Actual exit 1. 2 failed, 1 passed in 14.58s; before/during drift DID NOT RAISE, unchanged default normal case passed.

### Required focused GREEN

```powershell
Set-Location -LiteralPath 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'; $env:PYTHONPATH='C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'; $env:PYTHONDONTWRITEBYTECODE='1'; $env:HF_HUB_OFFLINE='1'; $env:TRANSFORMERS_OFFLINE='1'; $env:HF_DATASETS_OFFLINE='1'; $env:PIP_NO_INDEX='1'; py -3.13 -B -m pytest 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_prospectus_ingestion.py' 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_candidate_bundle.py' 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_ingestion_report.py' 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_policy_chunks.py' 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_policy_text.py' 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_procedure_text.py' 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_register_minting.py' -q -p no:cacheprovider --basetemp 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\tmp-task2-fix-green' *> 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-2-fix-green.log'; $testExit=$LASTEXITCODE; Get-Content -LiteralPath 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-2-fix-green.log' -Tail 12; Write-Output "GREEN_EXIT=$testExit"; exit $testExit
```

Actual exit 0. 211 passed in 21.83s; no skips/errors.

Independent import-origin assertions after repair pass against the actual candidate worktree for backend namespace, prospectus, bundle, protected loader/factory and source contracts. Evidence: unified-task-2-fix-imports.log. Final HEAD, exact two-path diff, no-untracked, empty staged index, protected-directory diffs and git diff --check assertions all pass, exit 0. Final before/after SHA-256 values are in unified-task-2-fix-scope.json.

Fresh quota queried with the exact usage script before work: 02:59:02 Manila 65% primary/24% secondary; after GREEN: 03:02:27 Manila 68%/24%, stop/save false. Actual candidate cwd restored after each query. Full suite, additional broad probes, real corpus/model/network/OCR certification and independent reviews were not run; focused checks do not clear the Medium finding's separate review debt. Root owns acceptance/commit; no independent Medium recheck or Standards was performed.
