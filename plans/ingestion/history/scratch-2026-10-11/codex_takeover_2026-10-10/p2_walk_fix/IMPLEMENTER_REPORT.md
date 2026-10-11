# P2 walk failure implementation package

Status: DONE. Implementation only; no review verdict.

Candidate source is frozen after focused GREEN. Root owns full gate; no automatic Standards Medium recheck was run or claimed.

## Change

`_walk` passes an `onerror` callback to real `os.walk`; enumeration errors raise `InspectionRefused` with cause. Existing `main` refusal boundary returns 2. Both snapshots fail before output publication. No report schema/default change.

The single focused regression is parameterized for denial starting on the before snapshot and denial on the after snapshot. Its real two-file tree and real `os.walk` use only `os.scandir` fault injection. It asserts exit 2, no completion manifest, a diagnostic containing the denied error, and unchanged bytes and source snapshot.

## Files

- `backend/bintanong_tools/document_ingest/inspection.py`
- `tests/test_document_inspection.py`

Exact patch: `P2_WALK_FIX.patch`; changed hashes: `changed_files.json`.

## Verification

- Invalid initial RED: 2 failed / 24 deselected, exit 1, no candidate import-origin assertion; retained in `red.log` and not used as TDD proof. Unexpected after result exposed cwd import precedence.
- Valid candidate-bound RED: 2 failed / 24 deselected, exit 1. Before returned 0 (silently omitted subtree); after returned 1 (misidentified omitted subtree as source change); expected refusal 2. `red_bound.log`.
- Focused inspection suite GREEN: 26 passed, exit 0. All 39 backend imports were candidate-bound before and after pytest. `green.log`.
- Both valid runs emitted one `PytestConfigWarning` for unknown `asyncio_mode` in the system Python environment. No dependency install or config edit.
- Original immutable archive: all 348 bound files verified before and after. Original manifest bytes unchanged. `source_before.json`, `source_after.json`.
- Candidate: exactly 348 bound files, exactly the two changes above. `candidate_hashes_348.json`.
- Extras: 0 original, 5 candidate; preserved, recorded in `extras.json`.

Commands: exact argv, environment, cwd and outcomes in `test_commands.json`; all PowerShell shells began with `Set-Location -LiteralPath 'C:\Users\Hawksprey\source\repos\Bintanong-wt\draft-p2'`. Preparation/test/fix/packaging scripts are external. System `py -3.13 -B` used throughout, pytest cache disabled, explicit candidate root/confcutdir/config and unique external basetemps.

Commit: none; staging/ref/attribution changes were prohibited. No self-review, reviewer invocation or subagent delegation.

Skipped: full suite and Medium recheck are owned by root and were not run here. Risk: Linux/real ACL denial not exercised; deterministic real-scandir fault injection covers this failure boundary.
