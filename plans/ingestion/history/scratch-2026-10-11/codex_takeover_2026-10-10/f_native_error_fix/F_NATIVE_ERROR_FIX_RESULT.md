# Native filename OSError leak — bounded implementer result

Status: Assigned native-OSError repair implemented in a new external scratch candidate; focused verification passed. Root broad gate remains pending. No Spec or Standards verdict or review/recheck is claimed or initiated. The single authorized Spec recheck remains consumed with its recorded FAIL.

Source is the clean immutable `draft_review_archives/f_fixed` archive, descended from pin `dd699958505996358864383ff9c184cb98aec985` plus the unchanged single M01 regression and the prior two Medium fixes. Created once with copytree after asserting that the new target did not exist. All 352 copied files initially matched `f_fixed_hashes.json`.

Only changed candidate files:
- `backend/bintanong_tools/prospectus.py`: two lines in the existing shared `_scrub` sets add `repr(str(path))[1:-1]` to the native/slash forms already recognized for the semantic map and each declared root. This matches native Python filename-bearing OSError diagnostics with escaped Windows backslashes. No generic redaction framework or other diagnostics/features were added.
- `tests/test_prospectus_folder.py`: one add-only parametrized regression with three cases. `_run_child` raises native `OSError(13, "Permission denied", str(filename))` for the external semantic map, a source-root filename, and an output-root filename. The real `run_candidates` boundary persists processing_error, keeps useful error text/filename, rejects native/slash/repr absolute directories, and creates only the run index.

`source.patch` and `tests.patch` contain the complete incremental diffs from immutable f_fixed. `final_integrity.json` confirms exactly these two changed files, no candidate additions/deletions, all previous folder test bytes unchanged as a prefix, and unchanged M01 and extractor pipeline. All previous 109 focused tests are retained and run.

| Run | Observed result | Exit |
| --- | --- | --- |
| `red_native.log` | 3 failed, 25 deselected, 2 warnings in 0.47s | 1 |
| `green_native.log` | 3 passed, 25 deselected, 2 warnings in 0.36s | 0 |
| `green_focused.log` | 112 passed, 2 warnings in 25.08s | 0 |

RED ran before either source line changed and failed at the repr-escaped directory assertion in all three cases. There were no collection/import/dependency failures. GREEN native tests and focused suite confirm the assigned behavior; the focused suite includes the six F files, unchanged M01 test, prior regressions and three new native-error cases. The two warnings are installed Typer/Click deprecations.

Each log captures exact pytest arguments, cwd and prospectus/pipeline import paths. `imports.json` and the runner assert both modules belong to this new candidate. `commands.json` captures exact process arguments, environment, cwd, summaries and exits; `test_commands.ps1.txt` contains their expanded shell commands. System Python 3.13, PYTHONDONTWRITEBYTECODE=1, no pytestcache, explicit candidate --rootdir/--confcutdir, unique external basetemps were used. Recorded commands are evidence; rerunning would reuse basetemps, so use a new location when re-verifying.

All 352 candidate files are bound by `candidate_hashes.json`. Its SHA-256 is `df0ef2c69633670a406506dcb5b8f5f027410e7679cf157b2eacc094dfdd59d6`. Final prospectus.py SHA-256 is `e30dd55027c22c9f825214ddde41eb2fb4ea4b74b4c819797c74e5e372d2e61a`. Candidate hashes matched again after focused GREEN. Both original f_candidate and f_fixed archive trees still match all 352 hashes in their respective immutable manifests. All writes in this run were restricted to f_native_error_fix.

Skipped: root full suite, review/recheck/verdict, self-review, other mutants, real Docling, Docker, deployment and unrelated diagnostics. No repository/owner/ref/staging/attribution/dependency/lock/CLI/API routing changes, installs, downloads, Claude invocation or institutional approval. Generic unknown absolute diagnostics remain outside this narrow fix; 52/52 remains UNPROVED.
