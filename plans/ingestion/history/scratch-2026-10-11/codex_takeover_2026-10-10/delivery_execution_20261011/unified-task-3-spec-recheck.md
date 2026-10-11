# Task3 T3-S1 scoped Spec repair recheck — quota stop

Status: **INCOMPLETE_QUOTA — NOTRUN / NO VERDICT**. T3-S1: **ADDRESSED/NOTADDRESSED determination pending independent tests**. The repair code appears to address the original raw/candidate blank mismatch, but the required independent regression and original-attack tests were not started before the quota stop. This is an incomplete review, not evidence that T3-S1 remains reproducible in the repair.

Scope: ONLY original T3-S1 and regressions in `12d5e373aaba2a2ec43e7a2624fa1e1a84af4a50..5596f810c4d08c7aef87503d06c0027d6b961a4b`. The precise owner exception recorded in AUTHORIZATION.json supersedes the stale not-authorized recheck brief for this one review. No Standards, adoption, source activation, ref movement or push authorized to this reviewer.

Confirmed new findings: **NONE**. No independent runtime finding can be inferred from the unrun tests.

## Inspection and limits

Read review-common, recheck brief, original Task3 brief, original review-scope, original implementation/repair report and original Spec review; owner extractor-reviewer and Claude spec-reviewer-prompt were read as Markdown only. Inspected actual repair patch and bridge, persisted regressions, original immutable adversarial attack, source specification blank/evidence requirements and interacting compiler `_review_decisions`/ledger course locator. The attempted nonexistent unified-task-3-scope.md was corrected to actual unified-task-3-review-scope.md; it did not affect source state.

Bridge repair uses the compiler's existing ledger validation before individually filtering accepted prerequisite entries. A retained accepted-blank entry requires exact complete regenerated row ownership, a genuinely empty prerequisite cell in the actual layout column/row and validated source geometry. Blank spans are not emitted as printed rule support. The latest validated entry IDs are retained only when their locator matches a validated blank owner; the wrapper is copied and original review inputs are not modified. `_review_decisions` validates wrapper and individual entry mapping shapes before the new filter uses `.get`. No protected compiler/producer/contracts code changed in this range. These are inspection results, not substitutes for independent behavior tests.

Unrun mandatory bounded batch: six persisted changed_nonblank_source/unsupported_blank_keeps cases, five applicable genuine-blank ledger cases, public synthetic E2E node, and exact original independent attack retargeted to the new archive (13 cases total). The exact original attack changed only candidate reviewed_empty/empty containers and valid ledger/manifests while retained raw t0-c9 printed CS102. A NEW external retargeted script is task3-spec-recheck-adversarial.py; old script/log/archive remained untouched. No full242/full4k replay or private/original corpus was run. Root's earlier248/520 results are context, not independent proof.

## Actual usage and commands

READ_ONLY_CODEX_USAGE.ps1 was read fully then executed with worktree restored. Actual local Codex app-server account/rateLimits/read samples:

- 2026-10-11 13:32:38 Manila: 83% primary,13% weekly; work could start.
- 2026-10-11 13:34:01 Manila: **86% primary,13% weekly; stop_new_batches=true,save_state_now=true**. No tests had started. New batches stopped and evidence/report saved immediately. Reset shown by actual metadata: primary2026-10-11 16:57:47 Manila.

Both helper invocations exited0. No independent pytest command ran; tests/counts/origin assertions are **NOT RUN**, rather than reported as zero failures or PASS. Actual inspected code paths are archive paths, but actual import origins have not been dynamically asserted.

Exact preservation commands, actual exit0 each:

```powershell
Set-Location -LiteralPath 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$env:PYTHONDONTWRITEBYTECODE='1'
py -3.13 -B 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/task3-recheck-preservation.py' pre
# Before final report save, same prefix:
py -3.13 -B 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/task3-recheck-preservation.py' post
```

The saved external preservation script captures exact commands/assertions. Git diff --check exact range exit0. Before/after JSON evidence: task3-recheck-preflight.json and task3-recheck-postflight.json. All378 actual archive files equal every manifest SHA256; exact file set; no symlinks/junctions; manifest/change.patch/change-stat hashes unchanged. Candidate and owner HEAD/refs/index/status/all tracked-file byte hashes unchanged, including owner modified four files. Old adversarial script SHA256 unchanged. Exact repair scope is the authorized three paths. Source/archive/index/refs/owner remained read-only. Reports, preservation script, JSON snapshots and retargeted reproducer were written only outside Git under D.

Every PowerShell first selected R and used login:false. System py3.13-B/no-bytecode, no install/download/dependency/config change. No descendants, Claude invocation, original/private conversions, API/Docker/network execution, Prolog, embedding/routing/runtime or institutional activation. Future tests must retain absolute frozen archive cwd/PYTHONPATH, asserted import origins, offline/no-cache and unique external basetemp/rootdir/confcutdir.

The one authorized review is incomplete and must not be treated as passed or as a second used recheck. Resumption after quota reset must execute the missing bounded evidence and preservation checks before gate clearance. Separate fullTask3 Standards and final wholebranch review remain downstream gates for the coordinator.

Skipped independent tests because actual Codex usage crossed the mandated stop threshold; source-binding behavior is not independently verified in this repair. **NOTRUN / NO VERDICT.**

## Exact continuation for the same interrupted authorized run

After a fresh actual Codex usage query is below85, rerun preservation preflight (external script), then this bounded command. No new Medium exception is implied or consumed by resuming this interrupted run.

```powershell
Set-Location -LiteralPath 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$env:PYTHONPATH='E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/unified-task-3-review-5596f810/candidate'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
$env:HF_DATASETS_OFFLINE='1'
Set-Location -LiteralPath $env:PYTHONPATH
py -3.13 -B -c "import pathlib,backend.bintanong_tools.document_ingest.prospectus_rules as b,backend.bintanong_tools.document_ingest.prospectus as p,backend.bintanong_tools.document_ingest.bundle as l,backend.bintanong_tools.prospectus_extractor.rule_candidates as c; r=pathlib.Path.cwd(); assert all(pathlib.Path(m.__file__).resolve().is_relative_to(r) for m in (b,p,l,c)); print([m.__file__ for m in (b,p,l,c)])"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
py -3.13 -B -m pytest "$env:PYTHONPATH/tests/test_prospectus_rule_handoff.py" 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/task3-spec-recheck-adversarial.py' -k 'changed_nonblank_source or unsupported_blank_keeps or only_applicable_existing_ledger or combined_synthetic_conversion_bundle_bridge_compiler' -q -s -p no:cacheprovider --rootdir $env:PYTHONPATH --confcutdir $env:PYTHONPATH --basetemp 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/task3-recheck-resume-temp-20261011-a' 2>&1 | Tee-Object -FilePath 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/task3-recheck-resume-a.log'
$task3RecheckExit=$LASTEXITCODE
Set-Location -LiteralPath 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
Write-Output "ACTUAL_PYTEST_EXIT=$task3RecheckExit"
exit $task3RecheckExit
```

Then run preservation postflight with exact command above, inspect actual tests/outputs and replace this incomplete report with the scoped verdict. The basetemp/log suffix above was reserved and has not been created by pytest; choose a new suffix if already present. Original immutable attack: D/task3-spec-adversarial.py; new retargeted copy: D/task3-spec-recheck-adversarial.py. No tests ran during this interrupted review.
