# Phase6 Task1 independent whole-task specification review

Verdict: **FAIL — CHANGES NEEDED**. One confirmed Medium specification defect (P6-S1 below). This is the initial whole-task Spec review, not a repair recheck. Separate Standards review must not start on this verdict.

Reviewed frozen package `phase6-task-1-review-01d1d48b/candidate`, whole-task BASE `8cdb8cfdce03c69f718bb63390903b484437112a` through HEAD `01d1d48b4b17fea59853a354fdfdf8800cf82bd7`, including checkpoint and continuation. The actual diff is exactly the three additive paths plus the conditionally authorized `tests/test_prospectus_materialise.py` refinement. No other product paths changed; whole-range `git diff --check` exit 0.

Read the complete review-common, review-scope, extractor reviewer role, Spec reviewer template, brief, continuation, implementer report, exact Phase6 SPEC/IMPLEMENTATION_PLAN and shared ingestion SPEC. Inspected the frozen changed files/full task patch and interacting source/register, prerequisite/classifier, ledger applicability, cycle detector, quoting, producer and checked-bundle behavior. Implementer/coordinator reports were context only. No descendants, self-review, repair, staging, commits, ref movement or owner writes occurred.

## Confirmed finding

**P6-S1 — Medium — unordered review locator IDs change accepted-blank applicability and semantic identity.**

File: `backend/bintanong_tools/prospectus_extractor/rule_candidates.py:147` (passes unnormalized valid ledger locators into `latest_by_field`); consuming lookup/equality at lines 296–299. The compiler normalizes unordered SourceSpan locator IDs at lines 227–228, but does not apply the same set semantics to the accepted review locator. Existing `latest_by_field` keys the locator's `cell_ids` in input order, while `course_locator(course)` sorts the same IDs. Consequently an otherwise valid decision is lost solely because its two cell IDs are reversed.

Binding requirement: phase6-task-1-continuation.md explicitly requires stable IDs/content_digest under unordered record/span/locator-ID collections, retaining actual review evidence. Phase6 SPEC's candidate-representation contract ignores traversal order and preserves semantic order only when the source supplies one. These locator IDs identify the same supporting cells; their order changes neither the source, reviewed field, decision nor prerequisite semantics.

Concrete reproducer: external `phase6-task-1-spec-reproducer.py::test_accepted_blank_locator_id_order_is_not_semantic`. It uses a synthetic blank prerequisite on CS 2 with source cells `["t0-c2", "t0-c3"]`, creates a valid accepted ledger decision through the actual helper, compiles it, reverses only the review entry's locator cell IDs, recomputes the actual ledger entry ID, and recompiles. `entry_problem` returns None for the reordered decision; the compiler does not mutate inputs. Actual outcomes:

- Original order: `reviewed_empty`, accepted review reference retained, empty supported review view.
- Reordered same cells: `blank_unreviewed`, review reference absent, supported view absent, new blockers.
- Candidate semantic ID and artifact content_digest differ.

The saved independent regression reproducer exits **1: 1 failed in 0.56s**, at the assertion requiring the applicable blank review to remain `reviewed_empty`. This is a conservative false negative rather than authority escalation: every record remains inactive. It nevertheless drops genuine review evidence and violates the requested semantic determinism. Fix belongs in the new compiler's validated decision matching/hash projection, preserving original ledger reference IDs and inputs; no shared ledger rewrite is implied. No repair or recheck was performed here.

## Independent evidence

Required frozen-archive focused suite: **346 passed in 32.73s, actual exit 0**. This includes test_rule_candidates, test_prospectus_materialise, test_contracts_source, both specified authority nodes, test_prospectus_ingestion and test_candidate_bundle. Archive cwd and process-only PYTHONPATH were asserted. Eight relevant module origins (compiler, producer, checked loader, source contract, ledger, prerequisites, audit and generator) were verified under the archive before pytest. System `py -3.13 -B`, no bytecode/cache, offline flags, explicit archive --rootdir/--confcutdir and new external basetemp were used. Actual command and exit are preserved in the external files listed below.

Passing evidence and code inspection support the remaining scoped behavior: registered institutional source/digest/exact span-version checks; malformed inputs and forged promotion refusal; actual unchanged pending producer -> checked loader -> compiler; unknown XX999 and ambiguous/unsupported prerequisite blockers; explicit-none/blank/reviewed-empty distinctions; printed zero versus absent or differently printed numbers; quoting and generator-supported values without defaults/directives/query helpers/completeness markers; inactive records; no mutation or compiler publication/execution. Poison tests exercised the prohibited execution/writing seams without invoking actual Prolog.

The conditional materialise scanner edit is restricted to excluding the pure compiler consumer from a literal writer scan. The real extractor never-emits assertions, classifier check and runtime materialise applicability/immutability cases remain; all 35 materialise tests are within the passing focused suite. It does not justify the locator-order failure above.

## Integrity and authority limits

Before and after: exact **376-file** archive set equals manifest, every SHA256 equals manifest and the prior snapshot, no symlinks/junctions. Manifest/change.patch/change-stat hashes are unchanged. Candidate-worktree HEAD, porcelain status, complete index listing, all refs, working diff and cached diff are byte-for-byte unchanged in the snapshots. HEAD remains the supplied final commit, status/index have no pending changes. Integrity command actual exit **0**. Only external delivery reports/logs/reproducer evidence were written.

Actual fresh Codex app-server quota was queried before work: 47% primary / 34% weekly at 11:25:14 Manila; final sample 55% / 36% at 11:30:01. Every helper invocation restored the candidate worktree cwd. Stop thresholds were not reached.

Unverifiable/deferred: original PDF/corpus accuracy, actual private inputs, human/issuing-office review and authenticity of review author identity, full Phase6/release/runtime behavior, actual Prolog execution, routing/embeddings/API/Docker and broad ~4k suite. Synthetic interoperability proves the interface under the tested fixture, not source accuracy or the later field-evidence bridge. This verdict grants no adoption, merge, institutional approval, activation or phase advancement. Unrelated historical M1/F/session debts and the owner's High-only repair recheck limits remain unchanged. This Medium finding does not authorize a repair recheck.

## External evidence files

- `phase6-task-1-spec-before.json`, `phase6-task-1-spec-after.json`: all hashes, exact set, package hashes and unchanged Git state.
- `phase6-task-1-spec-test-command.ps1`, `phase6-task-1-spec-origins.log`, `phase6-task-1-spec-tests.log`, `phase6-task-1-spec-test-exit.json`: exact required independent commands/origins/results.
- `phase6-task-1-spec-reproducer.py`, `phase6-task-1-spec-reproducer-command.ps1`, `phase6-task-1-spec-reproducer.log`, `phase6-task-1-spec-reproducer-exit.json`: exact confirmed-finding input/command/failure.
- `phase6-task-1-spec-integrity-command.py`, `phase6-task-1-spec-integrity.log`: exact after-verification code/result, compared against the before snapshot.

## Exact focused test invocation

```powershellSet-Location -LiteralPath 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$reviewArchive='E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/phase6-task-1-review-01d1d48b/candidate'
$reviewDelivery='E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011'
$env:PYTHONPATH=$reviewArchive
$env:PYTHONDONTWRITEBYTECODE='1'
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
Set-Location -LiteralPath $reviewArchive
@"
import importlib, os
from pathlib import Path
root=Path(r'$reviewArchive').resolve()
assert Path.cwd().resolve()==root
assert os.environ['PYTHONPATH']==str(root).replace('\\','/')
for name in ['backend.bintanong_tools.prospectus_extractor.rule_candidates','backend.bintanong_tools.document_ingest.prospectus','backend.bintanong_tools.document_ingest.bundle','backend.bintanong_contracts.source','backend.bintanong_tools.prospectus_extractor.ledger','backend.bintanong_tools.prospectus_extractor.prerequisites','backend.bintanong_tools.prospectus_extractor.audit','backend.bintanong_tools.prospectus_extractor.prolog']:
 module=importlib.import_module(name)
 assert Path(module.__file__).resolve().is_relative_to(root),module.__file__
 print(name,module.__file__)
"@ | py -3.13 -B - *> "$reviewDelivery/phase6-task-1-spec-origins.log"
$originExit=$LASTEXITCODE
if ($originExit -ne 0) { Set-Location -LiteralPath 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'; throw "origin check failed: $originExit" }
py -3.13 -B -m pytest "$reviewArchive/tests/test_rule_candidates.py" "$reviewArchive/tests/test_prospectus_materialise.py" "$reviewArchive/tests/test_contracts_source.py" "$reviewArchive/tests/test_prospectus_authority.py::test_prerequisite_state_of_one_course" "$reviewArchive/tests/test_prospectus_authority.py::test_prolog_and_essentials_status_name_the_extraction_not_a_verification" "$reviewArchive/tests/test_prospectus_ingestion.py" "$reviewArchive/tests/test_candidate_bundle.py" --rootdir "$reviewArchive" --confcutdir "$reviewArchive" -q -p no:cacheprovider --basetemp "$reviewDelivery/pytest_phase6_spec_20261011_1129_435a" *> "$reviewDelivery/phase6-task-1-spec-tests.log"
$reviewExit=$LASTEXITCODE
[ordered]@{origin_exit=$originExit;test_exit=$reviewExit;cwd=(Get-Location).Path;pythonpath=$env:PYTHONPATH;command_file="$reviewDelivery/phase6-task-1-spec-test-command.ps1"} | ConvertTo-Json | Set-Content -LiteralPath "$reviewDelivery/phase6-task-1-spec-test-exit.json"
Get-Content -LiteralPath "$reviewDelivery/phase6-task-1-spec-tests.log"
Set-Location -LiteralPath 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
Write-Output "pytest actual exit: $reviewExit"

```

## Exact independent finding invocation

```powershell
Set-Location -LiteralPath 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$reviewArchive='E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/phase6-task-1-review-01d1d48b/candidate'
$reviewDelivery='E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011'
$env:PYTHONPATH=$reviewArchive
$env:PYTHONDONTWRITEBYTECODE='1'
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
Set-Location -LiteralPath $reviewArchive
py -3.13 -B -m pytest "$reviewDelivery/phase6-task-1-spec-reproducer.py" --rootdir "$reviewArchive" --confcutdir "$reviewArchive" -q -s -p no:cacheprovider --basetemp "$reviewDelivery/pytest_phase6_spec_reproducer_20261011_1130_978f" *> "$reviewDelivery/phase6-task-1-spec-reproducer.log"
$reproExit=$LASTEXITCODE
[ordered]@{test_exit=$reproExit;command_file="$reviewDelivery/phase6-task-1-spec-reproducer-command.ps1"} | ConvertTo-Json | Set-Content -LiteralPath "$reviewDelivery/phase6-task-1-spec-reproducer-exit.json"
Get-Content -LiteralPath "$reviewDelivery/phase6-task-1-spec-reproducer.log"
Set-Location -LiteralPath 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
Write-Output "reproducer actual exit: $reproExit"

```

Integrity invocation (first worktree Set-Location retained): `py -3.13 -B '<D>/phase6-task-1-spec-integrity-command.py'`; actual exit 0.

Skipped corpus, broad suite and runtime execution as required; the confirmed Medium locator-order defect prevents Spec approval.

