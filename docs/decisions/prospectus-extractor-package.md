# Prospectus Extractor Package Split

Date: 2026-10-03
Status: accepted; Phase A complete on branch `refactor/prospectus-extractor-package`, not merged

## What changed and why

The prospectus extractor was one 6,320-line file, `backend/bintanong_tools/bintanong_jsonifer_prolog/bintanong_prospectus_jsonifier.py`. It is now the package `backend/bintanong_tools/prospectus_extractor/`, split by responsibility so later phases (markup twin, status separation, safe publication, RAG provenance) can change one area at a time. The split is meant to be 1:1: no behavior change. The base commit is `7591264`, and the monolith at that commit has SHA-256 `8ea75006a4c588902738c3a31096d44aa453a2fdfdeffae8750bf681eae3164d`. The old file path still works as a thin compatibility shim.

## Modules

Modules are listed in import order. A module imports only from modules above it. The table was checked against the actual package folder; every module below exists and no other module does.

| Module | Responsibility |
| --- | --- |
| `common.py` | Schema versions; optional Rich console objects. |
| `docling_env.py` | Lazy Docling import, version guard, CUDA check, converter cache. |
| `text.py` | Text cleaning, code keys, year and semester label matching. |
| `footnotes.py` | Footnote marker detection and stripping. |
| `units.py` | Lecture/lab/total unit parsing. |
| `prerequisites.py` | Prerequisite tokenising, `CodeIndex`, resolution. |
| `grid.py` | Course-code recognition, total rows, `GridParseResult`, table year contexts. |
| `layout.py` | Column-group and header detection. |
| `evidence.py` | `SourceBBox`, `NormalizedCell`, `NormalizedTable`, `ProspectusEvidence`. |
| `sections.py` | Structural tokenizer, curriculum sections, row assembly, provenance. The parser core, kept whole. |
| `repair.py` | Evidence-constrained semantic repair validation. |
| `parse.py` | `parse_curriculum_evidence`, `evidence_from_grids`, `parse_curriculum_grids`. |
| `legacy.py` | Deprecated `_parse_curriculum_grids_legacy`, kept for documentation. |
| `courses.py` | Course finalisation, classification, elective tracks. |
| `metadata.py` | Program, college, school-year metadata. |
| `audit.py` | Prerequisite cycles and `build_audit`. |
| `views.py` | Term tree, prerequisite edges, review CSV. |
| `prolog.py` | Candidate Prolog knowledge base. |
| `rag.py` | Semantic and layout RAG chunks. |
| `paths.py` | Default input and output locations. |
| `loader.py` | Docling-to-evidence adapter, cache, `load_document`, `dump_grid`. |
| `pipeline.py` | `build_payload`, `build_essentials`, `process_prospectus`. |
| `batch.py` | In-process batch engine and manifest. |
| `selftest.py` | Fixtures and the 80 checks, unchanged. |
| `tui.py` | Interactive terminal UI. |
| `cli.py` | `build_cli`, `main`. |
| `__init__.py` | Docstring and the small public API. |
| `__main__.py` | `python -m ...prospectus_extractor` and run-by-path entry. |

## Relocated definitions

Six definitions sit in a different module than their position in the monolith suggests. Their text is unchanged. They moved to keep the import graph free of cycles.

- `MULTIPART_CODE`, `is_probable_course_code`, and `_two_course_codes_in_cell` moved into `grid.py`. `layout.py` needs the course-code recognizer, so it has to live below `layout.py` in the import order.
- `build_hierarchical_rag_chunks` moved into `rag.py`, which keeps all chunking together.
- `find_default_input_root` and `find_default_output_root` moved into `paths.py`. `pipeline.py` needs the default output root, and `batch.py` imports `pipeline.py`.

## Differences from the single file

Exactly five differences exist. Only the first edits a line of code.

1. **`ensure_docling_env` re-launch line.** Before: `subprocess.call([str(venv_py), str(Path(__file__).resolve())] + sys.argv[1:], env=env)`. After: `subprocess.call([str(venv_py), *sys.orig_argv[1:]], env=env)`. The old line re-ran the file containing the function, which after the move would be `docling_env.py` and not an entry point. The new line re-runs the original command line, so script, `-m`, and package-directory starts all work on every OS. Affected: anyone who relies on the automatic re-launch into a `.docling-venv`. This is the only edited code line.
2. **`find_default_output_root`.** The text is unchanged, but it now resolves to `prospectus_extractor/docling_jsonified_output` instead of the old `bintanong_jsonifer_prolog/docling_jsonified_output`. It is used only when `-o` is omitted. Affected: anyone who runs without `-o` and expects output in the old folder.
3. **`_venv_python`.** The text is unchanged, but it now looks for `.docling-venv` inside `prospectus_extractor/` instead of next to the old file. No such folder exists in this checkout; the supported environment is `uv run`. Affected: anyone with a sibling `.docling-venv`, who must move it into `prospectus_extractor/`.
4. **`--help` program name.** `argparse` derives the name from how the tool was started. Through the package it shows `__main__.py` or `prospectus_extractor`; through the shim it shows the old file name. Affected: only the displayed help text.
5. **Patching names on the shim.** Rebinding a name on the compatibility shim module, for example assigning a fake to `load_document` on the shim, no longer changes what the package's own functions call, because each module holds its own reference. A test that needs to patch a function must patch it on the module that uses it. Nothing in this repository relied on the old behavior. This was found by the Codex review.

`DATA_ROOT` resolves to `backend/bintanong_tools` before and after, so the default source and semantic-map paths are unchanged.

## Evidence

All of this was observed on 3 October 2026 on this branch.

- **AST gate.** `tests/test_prospectus_split_equivalence.py` checks that every top-level definition of the monolith (126 functions, 19 classes, 40 assignments, 1 optional-import block) exists in exactly one package module with an identical AST, apart from `ensure_docling_env`. A reviewer's line-level comparison found all code and comment lines identical apart from section banners, imports, and that one line.
- **Golden-output check.** Command: `uv run --project backend --extra tools --extra dev python scripts/prospectus_golden_check.py <44 cached *_docling.json files from the task2b_standing_isolated_2026-09-29 run> <work dir> --semantic-doc <palsu_main_undergrad_program_college_meaning.md>`. For each input the old file ran twice and the package once with `--export-all --device cpu`. Result: 44/44 identical, exit 0. Run-to-run noise in the old code was 1 path for 38 inputs and 3 paths for 6 inputs. The 1-path case is the `generated_at` timestamp in `candidate.json`. For the 3-path cases, a diff of the two old-code runs for one input (`ABPhilStud-for-student-new-version`) showed only the generation timestamp, which appears in three files: `generated_at` in `candidate.json`, the `% Generated:` comment line embedded in `candidate.json`, and the same comment line in `candidate_prospectus.pl`. `candidate_rag.jsonl` and `candidate_review.csv` were identical.
- **Limit of the golden check.** It used cached Docling JSON. It proves the parsing and output code is unchanged. It did not re-convert PDFs through Docling.
- **Tests.** The full suite gave 36 passed and 13 subtests passed. The self-test gave 80/80 from four entry points: module from the repo root, module with `backend/` as the import root, package directory by path, and the legacy shim by path.
- **Independent reviews.** A Sonnet 5.5 reviewer found difference 3, and confirmed the package imports and passes without Rich installed, the shim re-exports every old name as the same object, and `package_sha256` is stable across CRLF and LF. Codex CLI 0.157.0 in read-only mode found difference 5 and nothing else.

## How to run

Prefix each command with `uv run --project backend --extra tools --extra dev`. The forms are the same on Windows, Linux and macOS.

- From the repo root: `python -m backend.bintanong_tools.prospectus_extractor ...`
- With `backend/` as the working directory, as in the Docker image: `python -m bintanong_tools.prospectus_extractor ...`
- By path to the package folder: `python <path to prospectus_extractor folder> ...`
- Through the legacy shim file: `python backend/bintanong_tools/bintanong_jsonifer_prolog/bintanong_prospectus_jsonifier.py ...`

The isolated batch runner: `python -m backend.bintanong_tools.prospectus_batch -i PDF_FOLDER -o NEW_RUN_FOLDER`.

## Consequences

- The `parser_sha256` field in the `prospectus_batch` manifest is now a hash over every `.py` file in the package, with line endings normalised. It is not comparable with the single-file hash in earlier manifests.
- Outputs remain review candidates. Nothing here approves a curriculum, RAG, or Prolog release.
- The scaffolding scripts `scripts/split_prospectus_extractor.py` and `scripts/prospectus_golden_check.py` were removed after use. They can be recovered from Git at commit `2dffe3d`, where they last exist.
- `tests/test_prospectus_split_equivalence.py` is to be deleted when Phase B starts changing behavior, because it asserts that nothing changed.
