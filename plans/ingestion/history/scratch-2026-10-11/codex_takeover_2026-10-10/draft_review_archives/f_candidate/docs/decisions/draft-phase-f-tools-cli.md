# Draft Phase F: the review-only `prospectus` tools command

Status: DRAFT on branch `draft/phase-f-tools-cli`. Tasks 1 to 7 of `plans/2026-10-03-prospectus-phase-f-tools-cli.md`
are drafted and tested. Docker and compose (Tasks 8 and 9), the final documentation and the Codex gate (Task 11)
are not done. Nothing here approves a source, a curriculum, a rule base or an answer.

## What the draft adds

| Piece | Where |
| --- | --- |
| Source record loader (CSV or JSON), `provisional:sha256:<digest>` IDs, locator rules | `backend/bintanong_tools/prospectus.py` |
| `run_candidate()`, `run_candidates()` (single PDF or folder), `candidate_run.json`, `candidate_runs.json` | same file |
| The `prospectus` Typer command (`prospectus_cmd`) | `backend/bintanong_tools/prospectus_cli.py` |
| Registration of that command on the `ingest` tool (5 lines) | `backend/bintanong_tools/ingest.py` |
| Explicit `source_root` for the PDF locator in essentials (default unchanged) | `backend/bintanong_tools/prospectus_extractor/pipeline.py` |
| Tests | `tests/test_prospectus_source_records.py`, `_source_root.py`, `_candidate_run.py`, `_command.py`, `_folder.py`, `_equivalence.py`, helper `tests/prospectus_cli_fixtures.py` |

Use: `python -m bintanong_tools.ingest prospectus <pdf or folder> --source-root <folder> --source-record <csv or json> --output-dir <new folder> [--semantic-doc <md>] [--device cpu|cuda|auto] [--strict]`.
`parse` stays a subcommand: `ingest parse <path>`. The bare form `ingest <path>` no longer works (see D2).

Exit codes: `0` a candidate was produced; `1` only with `--strict` when an extraction audit is `error`; `2` any
refusal or processing error (a usage error is also 2). Every failure inside the command is caught and mapped to 2,
because an uncaught exception would exit 1, which means "strict audit error".

## Defaults taken for D1 to D5 (not owner decisions)

Each is the plan's recommended option, recorded as a labelled default so the owner can overrule it.

| # | Default taken | Effect if the owner picks otherwise |
| --- | --- | --- |
| D1 | (a) A declared record file, CSV (`pdf_sha256,source_locator,source_verification`) or JSON. A record that declares anything other than `pending` is refused. | Per-PDF `--sha256` flag or run-time hashing would make the mismatch refusal unable to fire; the loader and tests change. |
| D2 | (a) `ingest parse <path>` becomes the form because the tool now has two commands. | A root callback with a default would keep `ingest <path>` but makes the root ambiguous; `ingest.py` changes more. |
| D3 | (a) Folder mode runs one child process per PDF, the same command on one PDF. | An in-process loop loses isolation from native Docling failures; `_run_folder` changes. |
| D4 | (a) Two mounts, read-only sources and a writable candidate folder; record file and semantic map sit inside the source tree. | A third read-only reference mount: Docker work only (Task 8, not drafted). |
| D5 | (a) Named cache volume for Docling weights, first run online. | Docker work only (Tasks 8 and 9, not drafted). |

D4 and D5 are recorded but nothing in this draft depends on them.

## Contradictions between the plan and the current code, and how each was handled

The plan was written before Phases C, D, E and Phase 1 landed. Each item was checked against the tree.

1. Stale line numbers (`ingest.py` 61 to 73, `pipeline.py` 129 and 174 to 186, `compose.yaml`, `docling_env.py:180-208`): not used; names were re-read.
2. `process_prospectus` now takes `export_md`, `source`, `approved_scope`, `review_entries` and a private `_snapshot`. The adapter passes `source`, `export_md=True` and the snapshot; `source_root` was added as a keyword-only argument before `_snapshot`.
3. The plan's `fake_conversion` fixture patches `pipeline.load_document` and `tests/conftest.py` is "created". The file exists (with `fake_docling` and others) and the pipeline calls `load_document_result(..., stage_dir, snapshot)` with a captured cache pair. `conftest.py` is untouched; `tests/prospectus_cli_fixtures.py` holds a fake that returns a real `DocumentLoadResult`.
4. The plan hashes the PDF with its own `file_sha256` and verifies twice. Now `identity.InputSnapshot` is the one capture and `identity.file_sha256` / `bytes_sha256` the hash owner. The adapter captures once, checks the record before anything is written, and passes the snapshot on; the pipeline checks it again and refuses a PDF that changed. No second digest implementation exists.
5. `prospectus_batch.package_sha256`, `importlib.metadata` versions: replaced by `payload["run_identity"]` (package hash, conversion identity, library versions), so the manifest cannot disagree with the payload.
6. `_status_fields` accepted either a string or `{"status": ...}` and fell back to `audit.status`. Phase C landed plain strings (`extraction_audit`, `content_review`, `source_verification`). The adapter reads them strictly, refuses any value other than `ok`/`warn`/`error` for the audit and anything but `pending` for the other two, and requires `authority.eligibility_executable` to be `false` and `pdf_hash_check` to be `matched`.
7. Schema versions: payload `palsu-prospectus-v3.3` and essentials `palsu-prospectus-essentials-v2` (the plan names `-v1`). Neither is bumped. The new manifest schemas are `palsu-prospectus-candidate-run-v1` and `palsu-prospectus-candidate-runs-v1`.
8. The plan lists whatever files sit in the run folder. Now the artifact list is exactly what the Phase D publish manifest (`<base>_publish.json`, `palsu-prospectus-publish-v2`) vouches for, checked with `verify_published` first, plus that manifest. Digests are the publisher's. `failed/` diagnostics are not artifacts.
9. Roles: `_docling.meta.json` is the conversion metadata (`conversion_metadata`), not a "runtime fingerprint"; `_prospectus.md` (Phase B twin) is requested and has the role `prospectus_markup`. Only the review CSV and the markup are requested; no `.pl` or `.jsonl` file is written (the Prolog and chunks stay inside the payload, as Phases C and E define them).
10. Completed-output refusal: the plan refused only a run folder holding its own manifest. Now a folder holding `candidate_run.json` or any `*_publish.json` is refused (a published but unfinished run is also not reused), and a folder run refuses an existing `candidate_runs.json` index before any child starts.
11. Folder scanning: the plan used a bare `rglob`. Now `scan_inputs` is reused, which skips subtrees carrying a `failure.json` marker and the known generated folders.
12. Locator rules: the plan's `normalize_locator` did not reject `:` or NUL; now it does (drive letters, alternate data streams). `run_dir_for` additionally requires the canonical form, safe folder names and containment in the output root; `locator_for` resolves symlinks, so a link pointing outside the source root is refused.
13. Read-only sources: the plan only mounts read-only. The draft also refuses, in code, an output folder inside the source root and a source root inside the output folder, and the tests compare the source tree byte for byte before and after.
14. Absolute paths: the plan did not address them. The manifest and index carry relative locators and names only; child output is scrubbed of the two root paths before it enters the index. The extractor payload still holds absolute `source_path` values and `failed/<base>/failure.json` holds the input path; those are existing Phase D and E behaviours, left alone. Host and container equivalence is therefore defined on `candidate_facts_sha256` and on the bytes of the essentials, review CSV, markup, raw JSON and conversion metadata, not on the payload file.
15. Line endings: the plan's finding 4 (CRLF on Windows) is obsolete. Phase D writes LF everywhere; a test checks every JSON, markdown and CSV artifact and both manifests for carriage returns.
16. Exit codes: the plan caught `EXPECTED_FAILURES` only. Any other exception would exit 1, which collides with the strict audit code, so the command catches every `Exception`.
17. The plan's `__spec__.name`-based child module: now `<package>.prospectus_cli`, computed from `__package__` (so `backend.bintanong_tools...` on the host and `bintanong_tools...` in the image), and the child is run as `-m <module> prospectus <pdf> ...`.
18. `ingest.py`: the plan puts the command body in `ingest.py`. The Phase 2 draft hardens that file, so the body lives in `prospectus_cli.py` and `ingest.py` gets only an import and one registration line. Merge-conflict risk: small, in the import block and after `parse_cmd`.
19. `scripts/prospectus_course_compare.py` is "created, deleted at the end" in the plan; it exists, is committed and has tests. It was run, not deleted.
20. Baselines: the plan's 36 tests and `uv run --with fastapi` commands are obsolete; the baseline here is 4036 passed, 1 skipped, 13 subtests, and the self-test is 80/80.
21. The plan appends to `plans/plan_current_progress/extractor_split_progress.md` after every commit and ends commits with a trailer. This draft leaves the progress file and `plans/INDEX.md` alone and writes no trailer.
22. `tests/test_prospectus_split_equivalence.py` (Task 1, step 2) is already gone; nothing to stop on.

## What is not done

Docker, compose, `.dockerignore`, `.env.example`, the weight cache and the Linux and macOS checks (Tasks 8 and 9) are not
drafted and not run. The final documentation and the Codex gate (Task 11) are not written. No institution PDF was
converted with real Docling; the tests use a fake conversion that returns the in-memory BSCS fixtures.
