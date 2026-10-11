# Independent scoped M1 Standards repair recheck

Verdict: **PASS — APPROVED for this scoped repair recheck. Original Medium M1: ADDRESSED.** Confirmed findings: **NONE** (0 High, 0 Medium, 0 Low). No new breakage was found in the retained-result/error/status guard. This is not a replay or approval of the whole candidate, an adoption/merge authorization, formal phase exit, or clearance of historical F/session/M01 debts.

## Scope and authority

One fresh independent Codex Standards seat; no descendants. Read review-common.md, m1-standards-recheck-brief.md, complete original SPEC_REVIEW.md and STANDARDS_REVIEW.md, extractor-reviewer role, Claude code-quality/review templates and Codex code-reviewer template as Markdown only. No Claude invocation. Owner's precise Medium M1 exception supplies authority for this one recheck; earlier m1-merge-gate-current.json still says NOTAUTHORIZED and was treated as historical context, not present authorization.

Reviewed BASE `7fe26c07fc5338dfeaae874438d8a802ae4ad774` to repair HEAD `57b598522cc7ed5d13e40eb8d1bcafede8c9ba1b`, frozen candidate_57b5985. Fresh source HEAD remained `12d5e373aaba2a2ec43e7a2624fa1e1a84af4a50`, clean. Exact repair paths: backend/bintanong_tools/ingest.py, tests/test_ingest_hardening.py, docs/decisions/phase-02-ingest-hardening.md. Read the full patch, full changed files, searched all parse_document callers, and inspected interacting InputSnapshot and shared loader error handling. Repair product/tests/docs are byte-identical to frozen repair HEAD and unchanged through current HEAD.

## Strengths and assessment

- ingest.py:51-58 retains the conversion result and rejects nonempty errors or explicit non-success status before Markdown export, using existing ConversionFailed refusal handling. The installed SUCCESS enum compares correctly with the expected success value.
- Existing missing-status converter doubles retain their documented behavior; explicit null/unknown/non-success statuses are refused. No new import or dependency is needed and lazy help behavior remains intact.
- Regression tests exercise actual installed Docling status/ErrorItem types, prevent export on failure, and check CLI stdout, nonzero exit, source preservation and absent/existing output preservation. Documentation matches the narrow change.

The original defect is independently resolved: a real installed Docling PARTIAL_SUCCESS/ErrorItem with surviving page records and text no longer becomes successful library/CLI JSON. No optional feature or style blocker was invented.

## Fresh execution and original M1 reproducer

System Python 3.13 via `py -3.13 -B`, offline process flags, PYTHONDONTWRITEBYTECODE=1, absolute archive PYTHONPATH. Every PowerShell invocation began with source worktree Set-Location, login:false; Python runners selected archive cwd and asserted relevant module __file__ paths inside the archive before testing. Separate source import assertion confirmed ingest resolves inside the actual source worktree (`m1-standards-source-import.json`). Archive assertions cover ingest plus reused modules (`m1-standards-bound-imports.json`); focused runner also asserts docling_env, identity and publish imports.

Repeatable commands, with R=`C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010`, D=this report's directory, A=`D/../phase2_candidate_review/candidate_57b5985` (expand all values to absolute paths):

```powershell
Set-Location -LiteralPath R
$env:PYTHONDONTWRITEBYTECODE='1'
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
$env:HF_HUB_DISABLE_TELEMETRY='1'
$env:PYTHONPATH=A
py -3.13 -B D/m1-standards-corrected-reproducer.py
py -3.13 -B D/m1-standards-run-focused.py
Set-Location -LiteralPath R
```

The focused runner's exact executable, cwd and absolute pytest arguments are saved in m1-standards-test-command.json. It runs only archive tests/test_ingest_hardening.py with `-q -p no:cacheprovider --basetemp D/m1_standards_pytest_temp_1229 --rootdir A --confcutdir A`, all paths expanded absolutely. **45 passed, 1 Docling backend deprecation warning, 52.37s; exit 0.** Full output m1-standards-focused.log and real exit m1-standards-focused-exit.txt. The brief's prior count 48 was not reproduced; the actual frozen file produces 45 passing cases, with no skips/failures in this run.

NEW corrected original reproducer m1-standards-corrected-reproducer.py preserves historical evidence untouched. It uses a copied committed synthetic PDF, installed ConversionStatus.PARTIAL_SUCCESS, installed ErrorItem(DOCUMENT_BACKEND, page_no=2), and surviving two-page document whose Markdown would be `Only page one survived.`. Observed **library ConversionFailed, CLI exit 1, stdout empty, named stderr refusal, zero Markdown exports**. Same complete-document seam accepts both absent status and actual installed ConversionStatus.SUCCESS. Reproducer exit 0; evidence m1-standards-reproducer.log, m1-standards-reproducer-exit.txt, m1-standards-reproducer-observed.json.

## Preservation and resource evidence

m1-standards-preserve.py ran before and after. Both verify the exact actual set of **368 files**, every manifest hash, no symlinks/junctions, and exact repair paths. All parent package-file hashes (including both manifests, patch, original archive and reports), repair diff stat, source/owner status, HEAD/dev/origin/dev and complete index entries are identical before/after. Repair patch SHA-256 remains `1cdeb8f7acc1e3ae25412391fcd973d2cc373e2bc28d98a6c3b665e897271a59`. Evidence m1-standards-before.json, m1-standards-after.json, m1-standards-preservation.log; preservation exit 0. No source/archive/owner/index/ref edits, installs or dependency/configuration changes occurred. Only new external D review scripts/logs/report and synthetic temporary data were written.

Read the complete READ_ONLY_CODEX_USAGE.ps1 and queried fresh actual Codex account/rateLimits/read, restoring R afterwards. At 04:29:36 UTC primary 37%, secondary 6%; at 04:32:25 UTC primary 41%, secondary 6%, ordinary usage allowed, neither stop flag set. No Claude/context percentage substitute was used.

## Declined to judge

- Entire candidate architecture/other tasks and broader regression suite: outside this explicitly bounded M1 repair recheck; no full candidate replay or broad 4k suite.
- Original/private corpus accuracy, human validation, actual OCR engines/models/GPU/device/photos: owner deferred; the reproducer is synthetic and patches only the converter seam.
- Deployment/Linux/Docker/API/routing/embeddings/Prolog execution and institutional use/source authority: outside scope, not run or granted.
- Historical F/session/M01 debts, formal phase exit and local dev integration: independent authorization/gates belong to coordinator; this review clears none of them.
- Pre-existing conversion-exception rendering and unrelated publication behavior: inspected surrounding code for repair interaction, but no broader redesign/security certification is claimed by this narrow reported-result guard review.

APPROVED — scoped M1 repair only; original M1 ADDRESSED, new confirmed repair findings NONE.

Skipped broader suites, actual corpus and deployment checks. Extraction accuracy, institutional authority and unrelated historical debts remain unverified.
`m1-standards-exact-commands.ps1` preserves the fully expanded absolute execution commands; it is evidence only and was not rerun.
