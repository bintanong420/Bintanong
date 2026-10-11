# M01 recovery checkpoint

Status: PARTIAL. The implementer finished and stopped at the 86 percent usage gate. No test process was started, no mutation or regression was written, and no repository file changed.

Fresh archives and extracted trees exist: pinned_tip.tar, pinned_tip/, pinned_baseline.tar, pinned_baseline/. All four archive/extract commands exited 0. Source pin dd699958505996358864383ff9c184cb98aec985; baseline 0caeaba8d8221a0f75b154e94bc3167b780f1407. Source draft-f HEAD and clean status were verified by the implementer.

Static observation only: adapter prospectus.py:262 verifies snapshot digest. pipeline.py:350 verifies the same digest before directory creation at356. A later guard may mask M01; this is NOT runtime-proved. M01 classification, fresh imports, baseline focused run, exact replacement and mutated run remain outstanding. Historical 52/52 kills is UNPROVED.

Next, after fresh Codex usage is below85 in both windows: run the untouched archive's six focused tests, then make a separate mutant copy and remove exactly the adapter line once. Record complete logs, exit codes and imported module path. Check pre-write refusal rather than treating any nonzero exit as a kill. Add a minimal regression only if an observable coverage gap is confirmed. No other mutants; do not overwrite historical evidence. Root broad gates and separate Spec then Standards reviews follow only while the usage policy permits them.

```powershell
Set-Location -LiteralPath 'C:\Users\Hawksprey\source\repos\Bintanong-wt\draft-f'
$env:PYTHONDONTWRITEBYTECODE = '1'
Push-Location -LiteralPath 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\m01_recovery\pinned_tip'
try {
    py -3.13 -m pytest -q -p no:cacheprovider --basetemp 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\m01_recovery\bt_focused_original' 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\m01_recovery\pinned_tip\tests\test_prospectus_source_records.py' 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\m01_recovery\pinned_tip\tests\test_prospectus_source_root.py' 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\m01_recovery\pinned_tip\tests\test_prospectus_candidate_run.py' 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\m01_recovery\pinned_tip\tests\test_prospectus_command.py' 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\m01_recovery\pinned_tip\tests\test_prospectus_folder.py' 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\m01_recovery\pinned_tip\tests\test_prospectus_equivalence.py' *> 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\m01_recovery\focused_original.log'
    $LASTEXITCODE | Set-Content -LiteralPath 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\m01_recovery\focused_original.exit.txt'
} finally { Pop-Location }
```
