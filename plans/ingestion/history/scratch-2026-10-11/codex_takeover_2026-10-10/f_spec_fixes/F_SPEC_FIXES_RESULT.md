# Bounded Phase F Medium fixes — implementer result

Status: Assigned two fixes implemented in the new external scratch candidate; focused verification passed. Root full gate remains pending. No Spec or Standards verdict, review recheck, institutional approval, commit, or Phase F completion is claimed.

Source pin: `dd699958505996358864383ff9c184cb98aec985`, plus the unchanged single M01 boundary regression. The candidate was created once with `shutil.copytree` only after asserting its target did not exist. Its initial 352 files exactly matched the archived candidate hash manifest. Original candidate archives and pinned baseline were not written.

## Exact scope

Only these candidate files differ from the original archive:
- `backend/bintanong_tools/prospectus.py`: `_scrub` also replaces the resolved semantic-map native/slash absolute path with its filename; both child-output and exception paths pass that setting. `_child_manifest` rejects non-object JSON and missing/invalid extraction audits before `_summary` consumes them, through the existing ValueError processing-error handler.
- `tests/test_prospectus_folder.py`: add-only tests for real-child external missing semantic-map refusal, missing extraction audit, invalid audit values (null, object, list, unknown state), non-object JSON (null, list, string, number), and semantic-map diagnostics via stdout or OSError. Each manifest case indexes the bad first child and a successful second child.

All original folder test bytes are preserved as an unchanged prefix. No files were added/deleted in the candidate. M01 regression and extractor pipeline/digest guard remain unchanged. `final_integrity.json` records the checks. `source.patch` and `tests.patch` contain the complete reviewable changes.

## Observed verification

| Run | Observed result | Exit |
| --- | --- | --- |
| `red_path.log` | 1 failed, 2 warnings in 0.95s | 1 |
| `red_manifest.log` | 1 failed, 2 warnings in 0.69s | 1 |
| `red_adjacent.log` | 10 failed, 15 deselected, 2 warnings in 4.57s | 1 |
| `green_regressions.log` | 12 passed, 13 deselected, 2 warnings in 5.71s | 0 |
| `green_focused.log` | 109 passed, 2 warnings in 24.71s | 0 |

Both primary REDs ran before any source edit. The external-map test failed because its decoded index error contained the complete absolute semantic-map path from a real subprocess. The missing-audit test failed because the CLI caught KeyError('extraction_audit') after the manifest was accepted; the first run left no folder index and the second had not run. Adjacent REDs exposed invalid audit states accepted as candidates, non-object manifests aborting, and leaking alternate error paths. GREEN preserves actionable error text and the semantic-map filename, processing_error with no candidate artifacts for the real missing-map refusal, and continued indexed outcomes after malformed manifests.

Focused GREEN covers the six original Phase F files plus the unchanged M01 regression and the 12 new cases: 109 passed, exit 0. The two warnings are installed Typer/Click deprecations. No collection or dependency failures occurred in these five test runs. All runs assert prospectus and pipeline imports inside this new candidate; `imports.json` and each log record actual paths. System Python 3.13 was used with PYTHONDONTWRITEBYTECODE=1, no pytest cache, and unique external basetemps. Exact program arguments, environment, cwd, log/result/exit metadata are in `commands.json`; the full shell test commands are in `test_commands.ps1.txt`. These are captured commands, not instructions to rerun and overwrite existing basetemps.

`candidate_hashes.json` binds all 352 candidate files; its SHA-256 is `b416271b07c8f4f9b52bbd78a7d2ab40431561073b86d3e1f88019249e261545`. Candidate hashes were checked again after focused GREEN. The original 352-file archive still matches its source hash manifest.

## Remaining / limitations

Root runs the broad full suite on this candidate. No broad suite, further mutation work, Medium review recheck, independent Spec/Standards review, real Docling conversion, Docker, deployment, dependencies, locks, repository/ref/staging/owner writes, CLI/API routing, or approval workflow was performed here. 52/52 remains UNPROVED; no M01 production change was made. The redactor handles the two declared roots and known semantic-map path; arbitrary unrelated absolute paths from unknown future child diagnostics were not tested.
