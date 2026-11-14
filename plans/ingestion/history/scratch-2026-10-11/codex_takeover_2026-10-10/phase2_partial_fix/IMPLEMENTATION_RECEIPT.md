# Bounded M1 implementation receipt

Status: focused fix verified; final product bytes frozen pending controller acceptance. No staging or commit, independent recheck, self-review or child delegation occurred.

Scope: only backend/bintanong_tools/ingest.py, tests/test_ingest_hardening.py, docs/decisions/phase-02-ingest-hardening.md. HEAD remains 7fe26c07fc5338dfeaae874438d8a802ae4ad774 on draft/phase2-candidates-20261010.

Cause: parse_document discarded ConversionResult.status/errors while taking .document. Installed ConversionStatus is str/Enum: pending, started, failure, success, partial_success, skipped. The shared loader._conversion_errors renders raw errors; ingest only needs presence, so the fix directly checks errors without importing/rendering a private helper or exposing raw ErrorItem details.

Change: retain the result and keep original .document try/except handling. After immutable-source verification, reject any reported errors or explicit status other than success before Markdown export. Missing status remains compatible with existing converter doubles; explicit null and unknown status are refused. Existing parse_document/CLI signatures, result keys, digest/identity behavior on success, optional Docling help paths and publication boundary are unchanged.

Test-first evidence: red.log / red_command.json / red_exit.txt: 12 expected failures, 33 deselected, 23.18s, exit 1. Library reached Markdown export on failed statuses; CLI accepted concrete partial conversion and published output. No product change existed for RED.

First GREEN: green.log / green_command.json / green_exit.txt: 48 passed, 4 upstream deprecation warnings, 67.54s, exit 0. Final essential command after restoring original .document try/except scope: final.log / final_command.json / final_exit.txt: 48 passed, 4 upstream deprecation warnings, 48.58s, exit 0. These runs contain only test_ingest_hardening.py and unchanged test_tools_contract.py. Tests include installed enum and real ErrorItem partial results, nonempty two-page partial CLI, errors despite SUCCESS, all installed nonsuccess statuses, unknown/null status, pre-export refusal, no stdout JSON, no new output, unchanged existing output/input, real synthetic PDF parse and CLI, optional-Docling help in both import roots, and existing alias/publication/immutability checks.

Commands: every PowerShell invocation selected the candidate worktree. Main test commands were py -3.13 -B <this evidence folder>/verify.py red, green and final, with PYTHONDONTWRITEBYTECODE=1, HF_HUB_OFFLINE=1, TRANSFORMERS_OFFLINE=1, HF_HUB_DISABLE_TELEMETRY=1. Exact pytest argv, Python path, cwd and environment are recorded per phase in *_command.json; each external basetemp is unique and pytest cache is disabled. *_imports.json asserts every loaded backend tools module stays in this worktree. No environment synchronization, install or download was used.

Preservation: freeze.py verifies unchanged HEAD, exact three-file allowlist, no staged files or untracked files, git diff --check exit 0, and writes freeze_manifest.json with final SHA-256 hashes and final_patch.diff. Git emits existing LF/CRLF normalization notices only. No owner files, protected extractor files, dependencies, lockfiles, originals or generated source outputs were edited.

Skipped: broad suite, mutation campaign, original corpus, actual OCR engines, Docker/platform/deployment, independent repair recheck and formal phase-exit gates. These remain deferred; the inherited Standards FAIL is not converted into independent PASS by implementer tests. No commit exists for this fix until the controller explicitly authorizes staging after its gate.
