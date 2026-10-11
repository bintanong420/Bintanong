# P2 confirmed Spec findings: implementation evidence

Status: IMPLEMENTED IN EXTERNAL CANDIDATE FOR INDEPENDENT REVIEW. This is not a Spec PASS, phase checkpoint, source adoption, source approval, or institutional approval.

Source archive pin: `ef0cdbff9dca3af7a9f80fdd3036a701c61c2a3c`; base `adf5d5192396dd18e58174add83773f2a0ce4aaa`. No commit created. Archive and worktrees were never written by this implementer.

## Changes

- Ingest: one shared filesystem alias guard before conversion and again before writing. Identical paths, normalized paths, case aliases, hardlinks and symlinks refuse without changing source bytes. A newly created alias during conversion also refuses.
- The exact late writer boundary was then reproduced: hardlink and symlink inserted after the final check still allowed a direct write to overwrite the PDF. Final publication uses stdlib NamedTemporaryFile with delete_on_close=False and existing publish.replace_file. The handle closes before Windows replacement; the context cleans only this call's own generated temporary file. Late file aliases are safely replaced, rather than refused: JSON output succeeds while the original PDF bytes stay unchanged. Forced replacement failure preserves source bytes and previous output, with no staging debris. The Python 3.13 requirement and tempfile cleanup behavior were checked locally. Missing output parent is still refused without directory creation.
- Inspection: final manifest obtains fresh membership via source_manifest(_walk(root)); additions, removals and renames fail with exit 1 and no manifest.json. Existing content-change and normal completion behavior remain tested.

Only production ingest.py and inspection.py, plus test_ingest_hardening.py and test_document_inspection.py, changed. Contract/schema/dependencies/CLI command shape/docs remain untouched. No prospectus_extractor edits. All inputs used were synthetic external fixtures.

## Observed checks

| Run | Result | Exit |
|---|---|---|
| baseline | 49 passed, 6 warnings | 0 |
| red | 10 failed, 1 passed, 42 deselected, 2 warnings | 1 |
| red_late | 1 failed, 29 deselected, 2 warnings | 1 |
| green_regressions | 12 passed, 42 deselected, 2 warnings | 0 |
| green_focused (before added writer-boundary scope) | 61 passed, 6 warnings | 0 |
| red_writer_boundary | 3 failed, 30 deselected, 2 warnings | 1 |
| green_writer_boundary | 4 passed, 29 deselected, 2 warnings | 0 |
| green_final | 64 passed, 6 warnings | 0 |

RED reasons: five existing file aliases and the actual CLI source.pdf -o source.pdf exit 0 and overwrite the source; the early-refusal test reaches the deliberately forbidden converter; file addition exits 0 with completion; removal/rename hit stale-list FileNotFoundError. A hardlink created during conversion fails to refuse. Writer-boundary aliases overwrite original bytes with JSON; direct writing bypasses forced publication failure.

The 6 final warnings are dependency deprecations from Typer/Click, DoclingParseV4DocumentBackend, force_full_page_ocr, and generate_table_images. No skip and no new runtime failure.

The original four focused files were rerun with all 15 new regression cases. System py -3.13, PYTHONDONTWRITEBYTECODE=1, offline Hugging Face settings, candidate-only PYTHONPATH, no pytest cache, explicit candidate rootdir/confcutdir and unique external basetemp were used. Compatibility self-check result is in compatibility_self_check.json (exit 0).

## Integrity and artifacts

Initial and final archive verification each match all 348 original hashes. Initial candidate matches the same 348; final candidate still has exactly 348 files and exactly the 4 allowed changes. Imports of ingest/inspection/identity/publish/docling_env resolve into this candidate. See initial_verification.json, final_verification.json, candidate_hashes.json, changed_files.json, and changes.patch. Every test run has separate command.json/result.json/stdout.txt/stderr.txt.

## Not run

Broad suite/gates, independent Spec/Standards rechecks, self-review, mutation-history gates, real institutional corpus, Docker service execution, Linux/macOS, checkpoint, adoption, Tasks 3-7, and commits: NOT RUN. Root owns full-gate execution and the permitted independent High-fix Spec recheck. No institutional authority is inferred.

Filesystem checks and final tree manifests are bounded snapshots; this change does not promise an immutable filesystem against arbitrary external directory replacement or later source mutation. The exact file-alias writer boundary requested by the root is regression protected.

## Exact executed pytest commands

Each command below ran with the cwd/environment captured in its command.json. Outer PowerShell tool invocations began with Set-Location -LiteralPath 'C:\Users\Hawksprey\source\repos\Bintanong-wt\draft-p2'.

### baseline

```text
py -3.13 -m pytest -q "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\candidate\tests\test_ingest_hardening.py" "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\candidate\tests\test_tools_contract.py" "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\candidate\tests\test_scaffold_contract.py" "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\candidate\tests\test_document_inspection.py" -p no:cacheprovider --rootdir "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\candidate" --confcutdir "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\candidate" --basetemp "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\bt_baseline"
```

Exit 0; duration 52.53s. Full output: baseline.stdout.txt and baseline.stderr.txt.

### red

```text
py -3.13 -m pytest -q "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\candidate\tests\test_ingest_hardening.py" "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\candidate\tests\test_document_inspection.py" -k "output_alias or same_output or separate_output or tree_membership" -p no:cacheprovider --rootdir "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\candidate" --confcutdir "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\candidate" --basetemp "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\bt_red"
```

Exit 1; duration 26.50s. Full output: red.stdout.txt and red.stderr.txt.

### red_late

```text
py -3.13 -m pytest -q "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\candidate\tests\test_ingest_hardening.py" -k created_during_conversion -p no:cacheprovider --rootdir "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\candidate" --confcutdir "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\candidate" --basetemp "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\bt_red_late"
```

Exit 1; duration 2.58s. Full output: red_late.stdout.txt and red_late.stderr.txt.

### green_regressions

```text
py -3.13 -m pytest -q "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\candidate\tests\test_ingest_hardening.py" "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\candidate\tests\test_document_inspection.py" -k "output_alias or same_output or separate_output or tree_membership" -p no:cacheprovider --rootdir "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\candidate" --confcutdir "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\candidate" --basetemp "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\bt_green_regressions"
```

Exit 0; duration 2.81s. Full output: green_regressions.stdout.txt and green_regressions.stderr.txt.

### green_focused

```text
py -3.13 -m pytest -q "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\candidate\tests\test_ingest_hardening.py" "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\candidate\tests\test_tools_contract.py" "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\candidate\tests\test_scaffold_contract.py" "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\candidate\tests\test_document_inspection.py" -p no:cacheprovider --rootdir "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\candidate" --confcutdir "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\candidate" --basetemp "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\bt_green_focused"
```

Exit 0; duration 64.19s. Full output: green_focused.stdout.txt and green_focused.stderr.txt.

### red_writer_boundary

```text
py -3.13 -m pytest -q "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\candidate\tests\test_ingest_hardening.py" -k "writer_boundary or publish_failure" -p no:cacheprovider --rootdir "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\candidate" --confcutdir "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\candidate" --basetemp "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\bt_red_writer_boundary"
```

Exit 1; duration 2.50s. Full output: red_writer_boundary.stdout.txt and red_writer_boundary.stderr.txt.

### green_writer_boundary

```text
py -3.13 -m pytest -q "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\candidate\tests\test_ingest_hardening.py" -k "writer_boundary or publish_failure or separate_output" -p no:cacheprovider --rootdir "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\candidate" --confcutdir "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\candidate" --basetemp "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\bt_green_writer_boundary"
```

Exit 0; duration 2.09s. Full output: green_writer_boundary.stdout.txt and green_writer_boundary.stderr.txt.

### green_final

```text
py -3.13 -m pytest -q "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\candidate\tests\test_ingest_hardening.py" "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\candidate\tests\test_tools_contract.py" "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\candidate\tests\test_scaffold_contract.py" "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\candidate\tests\test_document_inspection.py" -p no:cacheprovider --rootdir "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\candidate" --confcutdir "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\candidate" --basetemp "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\p2_spec_fixes\bt_green_final"
```

Exit 0; duration 34.36s. Full output: green_final.stdout.txt and green_final.stderr.txt.

