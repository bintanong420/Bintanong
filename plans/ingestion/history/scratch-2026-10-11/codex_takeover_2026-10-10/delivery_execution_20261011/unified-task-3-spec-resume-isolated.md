# Task3 T3-S1 scoped Spec repair review — isolated continuation

Verdict: **PASS — APPROVED within the scoped repair review**. **T3-S1 ADDRESSED**. Confirmed new repair findings: **NONE**.

This completes the ONE interrupted authorized Spec repair review, previously INCOMPLETE_QUOTA / NOTRUN / NO VERDICT. It is not a second completed recheck or a full Task3 Standards review. Scope is ONLY T3-S1 and repair regressions in `12d5e373aaba2a2ec43e7a2624fa1e1a84af4a50..5596f810c4d08c7aef87503d06c0027d6b961a4b`, using frozen `unified-task-3-review-5596f810/candidate`.

## Independent inspection

Read the complete pickup, review-common, scoped recheck report/brief, original Task3 scope/brief/Spec/report, shared unified ingestion SPEC/IMPLEMENTATION_PLAN and Phase6 compiler SPEC; owner extractor-reviewer and historical spec-reviewer-prompt were read as Markdown only. Inspected the actual three-path repair patch, complete bridge, changed regressions, saved original/retargeted attack, and interacting compiler review validator/classification, ledger course locator/latest-entry selection, section field ownership, normalized cells, layout and SourceSpan checks. Implementer/root counts were not used as proof.

The repair at prospectus_rules.py:141–161 verifies that the regenerated owner has no prerequisite wording, the candidate raw wording is empty, and the complete regenerated course provenance remains present. It finds the prerequisite column in the actual layout and permits only one genuinely blank cell overlapping this course's row range. Existing span validation verifies its source version/digest, physical page, native geometry and captured page size. Blank spans validate review binding and are not emitted as printed support.

At prospectus_rules.py:195–204, the existing compiler validator checks review wrapper and individual entry mapping shapes before the new filter calls `.get`. It validates version/hash/entry integrity and selects latest applicable entries. Only accepted prerequisite entries bound to a validated blank locator survive; filtering is per entry, preserving unrelated valid decisions and copying the wrapper. Compiler/producer/contracts/helpers were not modified in the repair range. No new review authority or correction materialization was introduced.

## Independently executed evidence

**13 passed, 30 deselected in 60.93s; actual pytest exit 0.** No warning/failure summary was emitted. The four imported module origins (bridge, producer, checked bundle and compiler) all resolved beneath the frozen archive; origin assertion exit 0.

The bounded selection comprises six persisted repair regressions, five applicable genuine-blank ledger variants, the public synthetic conversion → producer → checked bundle → bridge → compiler case, and the exact original attack retargeted to the repaired archive. Log: `task3-spec-resume-isolated-20261011.log`. Exact invocation including environment/origin assertion and actual exit capture is saved in `task3-spec-resume-isolated-20261011-command.ps1` and reproduced below.

The original attack leaves raw cell t0-c9 printing CS102 while changing only candidate prerequisite containers/state plus current accepted-blank ledger and manifest hashes. Its actual repaired record is `blank_unreviewed`, retains span text CS102 and cell t0-c9, has no review evidence refs, and has blockers `blank_unreviewed` plus `missing_or_unmatched_field_evidence:prerequisites_raw`. It contains no `review_view`. Thus it reaches the bridge and remains blocked rather than silently erasing supported semantics.

Adjacent cases verify missing provenance, ambiguous blank cells, semantic repair, missing geometry and a blank cell belonging to another course cannot clear the blocker. Each preserves the unrelated CS102 valid accepted-blank reference. Genuine blanks remain reviewable only with current applicable evidence; foreign version/PDF, stale and forged entries do not clear blankness. The actual E2E retains XX999 as unresolved and all records inactive, and checks input/bundle byte immutability.

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
py -3.13 -B -m pytest "$env:PYTHONPATH/tests/test_prospectus_rule_handoff.py" 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/task3-spec-adversarial-spec-resume-isolated-20261011.py' -k 'changed_nonblank_source or unsupported_blank_keeps or only_applicable_existing_ledger or combined_synthetic_conversion_bundle_bridge_compiler' -q -s -p no:cacheprovider --rootdir $env:PYTHONPATH --confcutdir $env:PYTHONPATH --basetemp 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/task3-spec-resume-isolated-20261011-temp' 2>&1 | Tee-Object -FilePath 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/task3-spec-resume-isolated-20261011.log'
$task3RecheckExit=$LASTEXITCODE
Set-Location -LiteralPath 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
Write-Output "ACTUAL_PYTEST_EXIT=$task3RecheckExit"
exit $task3RecheckExit
```

## Preservation

Preflight and postflight commands both exited 0:

```powershell
Set-Location -LiteralPath 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$env:PYTHONDONTWRITEBYTECODE='1'
py -3.13 -B 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/task3-recheck-preservation-spec-resume-isolated-20261011.py' pre
# After independent tests, same worktree selection/environment:
py -3.13 -B 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/task3-recheck-preservation-spec-resume-isolated-20261011.py' post
```

The new-suffix copy of the fully read original preservation script writes separate `task3-recheck-spec-resume-isolated-20261011-preflight.json` and `...-postflight.json`; exact results compare equal. **378 actual files, exact manifest file set and every SHA256; no symlinks/junctions; package manifest/patch/stat unchanged.** Source/owner HEAD, refs, index, status and all tracked file byte hashes unchanged. Candidate HEAD remains 5596f810, source status clean, and diff --check exact range exit 0. Exactly the three authorized repair paths changed in the pinned range.

The existing preservation script captures tracked owner bytes but not the three untracked plan bytes. Initial owner FOUR preservation is supplied by the coordinator's `isolated-pickup-preservation.json` (05:57:11 UTC, before this review). I independently supplemented completion checks against `owner-four-pre-integration.json`: all FOUR exact SHA256 values and status match, exit 0, saved `task3-owner-four-spec-resume-isolated-20261011.json`. Historical reproducer hash remains unchanged; old scripts/logs/packages were not written. New retargeted attack `task3-spec-adversarial-spec-resume-isolated-20261011.py` is a byte copy of the prepared retargeted script, leaving historical evidence untouched.

## Account usage and limits

Initial corresponding-profile coordinator sample reused: 13:54:01 Manila, 2% primary/0% weekly, ordinary usage allowed, `isolated_usage_20261011_055401.json`. Independently refreshed through THIS .codex-bintanong-b profile's release 0.162.1 local app-server --stdio and `account/rateLimits/read`, params `excludeResetCreditDetails=true,supportsLunaReserve=false`, with process-local CODEX_HOME; actual exit 0. Completion sample 14:01:50 Manila: **18% primary/3% weekly**, ordinary allowed; resets 18:52:20 Manila / 2026-10-18 13:52:20 Manila. Evidence `task3-usage-spec-resume-isolated-20261011.json`. No threshold was reached; no tokens, auth.json or account email were printed.

Every PowerShell first selected the candidate worktree and used login:false. Tests used system py -3.13 -B, archive cwd/PYTHONPATH, no-bytecode/offline flags, no-cache pytest, absolute rootdir/confcutdir and a new external basetemp. No source/Git/owner writes, descendants, Claude invocation, dependency/config/interpreter changes, installs/downloads or private inputs.

Not assessed: full Task3 Standards, whole-branch integration, corpus/OCR accuracy, human/domain/source approval, private lifecycle, mutation campaign, runtime/Prolog/Janus, embeddings/routing, API/Docker or institutional activation. Local unsigned hashes/ledger check consistency, not malicious-producer authentication. Historical F/session/M01 debts remain unchanged. This scoped PASS clears the T3-S1 Spec repair gate only.

**PASS — APPROVED; T3-S1 ADDRESSED; new findings NONE.**

