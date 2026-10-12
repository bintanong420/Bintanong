# Phase 05 real retrieval readiness — 12 October 2026

Current status: owner-authorized dependencies are installed and real local SEA-LION execution is verified. Original-PDF character regions are resolved; production Docling mapping remains blocked on the specific additional assets proposed below. The initial preparation record is preserved alongside the execution updates. It does not approve institutional sources, publish candidate knowledge or advance Phase 05.

## Completed preparation

All current artifacts are under `C:/Coding-projects/bintanong_workspace/audit-evidence/p05-real-retrieval-readiness-20261012/`, outside both the main checkout and this `worktrees/Bintanong/p05` code worktree. The original dataset stays at the [documented deep location](dataset-locations.md), read-only.

- `pending-source-register.json`: 39 real-source records minted through the existing contract with byte-derived document/version/edition IDs. Acquisition, verification, content review and scope stay pending; source approval stays `not_requested`; `synthetic` is false because these are real document bytes.
- `exam-source-id-translation.json`: exact digest/path-bound translation from ten authored exam source/version labels to the pending register identities. These are file-based pending records, not deployed database records.
- [Independent source/answer review sheet](</C:/Coding-projects/bintanong_workspace/audit-evidence/p05-real-retrieval-readiness-20261012/independent-source-answer-review.csv>): 27 rows containing candidate answers/control, original paths/hashes/pages/locators, with independent reviewer and authority/applicability decisions left blank/pending.
- `citation-mapping-requests.json`: 28 distinct semantic locator targets across 27 cases. Actual chunk/span/cell IDs are empty because no real ingestion artifacts exist. This is a mapping request, not a completed cell mapping.
- `strict-encoder-preflight.json`: the existing strict encoder rehashed all ten local model assets, checked the pinned weight identity and local Retrieval prompt, then failed closed because `sentence_transformers` is absent. No vectors or observations were generated.
- `database-readiness.json`: local read-only psql and hosted Supabase MCP SELECTs found zero document versions, chunks, source spans, embeddings, releases and active pointers. No migration or database writes were performed.

All 39 original hashes match the existing provisional CSV inventory, which remains pending. The prepared packet SHA-256 is `3c016d5214f2045d84c4c27eadd817051b66ada06ff33a5a7c4d41c8dfb2fca2`; the packet itself was not changed. Existing local weights SHA-256 is `df5b1c55623eeb5ef09ce3f3c50e24e2db433d7d1bbcccf76d2f01ba212df5f1`, tokenizer `883b037111086fd4dfebbbc9b7cee11e1517b5e0c0514879478661440f137085`.

## Environment findings and verification

System Python 3.13.7 is the only registered interpreter. No workspace `python.exe`/`pyvenv.cfg`, local model/PDF extraction libraries or existing embedding Docker image/container were found. Supabase services are already running; none was started by this work.

Fresh 34 exam unittest checks passed in 0.840s with temporaries inside the readiness directory. An expanded invocation attempted `tests.test_register_minting` and `tests.test_prospectus_input_snapshot`; both failed import with `ModuleNotFoundError: pytest`, while the 34 exam tests passed. These pytest suites did not execute and are not claimed as passing. Existing register parsing was exercised directly on all 39 newly minted records and the preparation artifacts were checked separately. Raw commands/results are in `readiness-regressions.log` and `exam-regressions.log`.

No product code, dependency declaration or lockfile changed. Source-derived review/mapping data remain untracked.

## Concrete dependency proposal — not executed

Create an isolated Python 3.13 environment at:

```text
C:/Coding-projects/bintanong_workspace/audit-evidence/p05-real-retrieval-readiness-20261012/venv
```

The reviewable [requirements proposal](</C:/Coding-projects/bintanong_workspace/audit-evidence/p05-real-retrieval-readiness-20261012/proposed-requirements.txt>) uses existing `backend/pyproject.toml` embedding/tools/dev pins, its existing httpx pin, and pypdfium2 5.14.0 for direct original-PDF geometry checks. It includes torch 2.14.0, sentence-transformers 6.1.0, docling 2.133.0 and pytest 9.1.1. The top-level PyPI metadata was checked read-only; torch has a Python 3.13 Windows wheel, and the PDF binding has a Windows wheel. Full transitive compatibility must still be checked by installation and `pip check`; metadata is not an executed environment gate.

Install binary wheels into that isolated environment, keeping pip cache, temporary files and execution evidence in the same workspace directory. Record the resolved transitive versions after installation. Preserve system Python, repository dependency/lock files and the main checkout.

Read existing SEA-LION weights from `C:/Coding-projects/MODELS`; do not copy or download them. Keep Hugging Face/model loading offline. Docling extraction assets were not found or authorized for download; if its converter requires missing model assets, stop at that specific error and identify the asset requirement. Package installation approval must not silently authorize extra model downloads, corpus publication or source approval.

The executable setup commands are prepared in `proposed-setup.ps1` under the artifact directory, and have not run. Explicit owner authorization is required by the repository instruction: **“No installs/downloads or dependency/lock changes without an applicable owner instruction.”** The owner's request to proceed authorized preparation; it did not explicitly approve installing packages.

## Recovery sequence after environment authorization

1. Install/check the isolated environment, record exact versions and rerun the currently unavailable register/input-snapshot pytest checks with cache disabled and workspace basetemp.
2. Execute strict local SEA-LION loading and normalized 1024-dimensional query/document embeddings with the pinned Retrieval instruction. Refuse truncation, network loading and synthetic fallback; record exact tokenizer counts/configuration fingerprints.
3. Run the existing ingestion path on original PDFs independently of the answer key. The exam gold passages must never be used to construct the retrieval corpus. Obtain actual candidate spans/cells/chunks and resolve the 28 locator requests against matching bytes/pages/coordinates; quarantine ambiguous or absent matches rather than inventing IDs. If the existing converter lacks required assets, report that remaining execution prerequisite.
4. Keep original-friendly exam version labels and byte-derived register IDs distinct. Expected benchmark citations can be translated using the audited digest-bound mapping; preserve runtime observations with their actual returned IDs rather than relabeling them to fit the key.
5. Have an independent source/domain reviewer complete the prepared answer/source/applicability sheet and provide review evidence. Agent source reading and the owner's permission to run code do not authenticate institutional authority.
6. Once approved cases and source-linked chunks exist, run k=3/5/8 retrieval under runtime roles in an authorized disposable evaluation environment. Record actual evidence/control/rankings by language/category/college, preserve unknown scope, test unsupported and edition ambiguity, and calibrate dev only. No LLM answer generation is required by master section 10.

The shared/hosted corpus remains inactive. Source approval, actual ingestion mapping and real model measurements remain open. Only earned master-section-10 evidence permits a complete handoff and Phase 06.

Documentation consulted: [Sentence Transformers local loading](https://github.com/huggingface/sentence-transformers/blob/main/sentence_transformers/base/model.py), [PDFium text and coordinate API](https://pypdfium2.readthedocs.io/en/stable/python_api.html), and official [torch package metadata](https://pypi.org/pypi/torch/2.14.0/json), [Sentence Transformers metadata](https://pypi.org/pypi/sentence-transformers/6.1.0/json), [Docling metadata](https://pypi.org/pypi/docling/2.133.0/json). Context7 was used for the library documentation.

Fresh independent agent review validated all39 live source hashes/pending contracts, ten translations,27 review rows and28 unresolved citation requests with no P1/P2 findings. Agent review does not supply institutional authority. Setup remains unexecuted pending explicit owner authorization.

## Authorized execution update

Owner explicitly approved the prepared package setup. Installation completed in the isolated workspace environment; pip check found no broken requirements, and the resolved versions are recorded in resolved-environment.txt. Original system Python and repository dependency/lock files are unchanged.67 targeted pytest checks plus19 subtests pass17.02s, including previously unavailable register/input-snapshot tests.

Actual strictSEA-LION execution completed offline:27 real query embeddings and one original-source documentprefix smoke test,1024 normalized dimensions,512-token model limit; querytokens50..75 and document193. Weight/tokenizer/prompt checks passed. Runtime packages: torch2.14.0 (CPU), sentence-transformers6.1.0, transformers5.19.0, tokenizers0.23.3. This proves model compatibility/execution, not recovered policy evidence or retrieval quality. See real-encoder-report.json and real-query-embeddings.jsonl in the readiness folder.

PDFium independently extracted all39 originals/43physical pages without empty pages or changed bytes.28 authored regions now resolve to actual PDF characters and valid pending SourceSpan contracts in original-region-inspection.json. These are PDF character inspection spans, not invented Docling table/cell identities; production ingestion mapping remains incomplete.

The first full pytest run reported7 failures,4898 passes,5 skips and107 passing subtests in447.84s. Three tests used external click.Exit while the pinned public API is typer.Exit; one Windows fixture lacked symlink privilege; the legacy shim imported the extractor at a namespace depth incompatible with contract imports; two real converter tests need missing Docling model assets. Root causes were reproduced before changes. Commit66bce2a fixes the shim and test API/capability checks, preserving all source-protection assertions. Focused47 pass/2skip/oneassettestdeselected20.76s; the final whole-suite rerun is recorded separately when complete.

## Remaining Docling assets — concrete proposal, not downloaded

The existing converter fails closed in offline mode because its Heron layout model has no cached snapshot. Its configured accurate TableFormer also needs its checkpoint/config. Package installation did not include permission to download extra model assets. The metadata-only proposed-docling-assets.json and proposed-docling-download.py identify five files totaling384,428,156 bytes (384.43MB), stored only in this task's workspace hf-cache if approved. Existing SEA-LION/GEMMA weights stay in place under MODELS; no duplicate is proposed.

| Required bundle | Pinned commit | Files / size |
| --- | --- | --- |
| docling-project/docling-layout-heron |8f39ad3c0b4c58e9c2d2c84a38465abf757272d8 |config.json,model.safetensors,preprocessor_config.json;171,662,708 bytes |
| docling-project/docling-models, runtime v2.3.0 |fc0f2d45e2218ea24bce5045f58a389aed16dc23 |accurate/tableformer_accurate.safetensors and tm_config.json under model_artifacts/tableformer;212,765,448 bytes |

Metadata includes official LFS SHA-256 for both safetensor files. The prepared helper limits downloads to those five pinned files, checks their sizes/hashes, and binds offline cache revision labels to the reviewed commits. No extra OCR/VLM/LLM model, dependency change, corpus activation or policy approval is included. Owner authorization for these model files, or an existing compatible local asset directory, is the next converter prerequisite. The independent source/domain reviewer sheet remains pending separately.

## Final installed-environment gate and recovery

After the reproduced fixes, the fresh full command `venv/Scripts/python.exe -B -m pytest tests -p no:cacheprovider --basetemp <workspace-readiness>/tmp/pytest-full-rerun -q` reports **4902 passed,107 subtests passed,6 skipped,2 failed** in405.12s. The two remaining failures are `tests/test_ingest_hardening.py::test_real_cli_stdout_parses_as_json` and `tests/test_tools_contract.py::ToolsContractTests::test_synthetic_pdf_fixture_exists_and_parses`, both stopped by the uncached Docling layout assets in enforced offline mode. They remain failures, not skips or a full passing-suite claim. Six skips include unsupported Windows symlink privileges. Full logs are `full-pytest.log` and `full-pytest-rerun.log`; no cache files are written into Git.

Fresh independent review: no P1/P2 findings. Reviewer verified all39 hashes/43 extracted pages, all28 PDF character regions/bboxes and source bindings, every27-vector dimension/norm/configuration, source-only documentprobe and maintained CLI/input protections. Five entrypoint tests pass independently; hardening checks independently42pass/2skip/oneasset-dependent failure. Reviewer declined institutional-authority and retrieval-quality claims because neither is established here.

Location ruling: the owner explicitly required all new task artifacts under `C:/Coding-projects/bintanong_workspace`. That higher-priority instruction overrides the handoff skill's default model-storage location for these **proposed new Docling assets** only. Existing SEA-LION/GEMMA weights remain in MODELS and are read in place. The additional download proposal names the workspace hf-cache explicitly; no model downloads are authorized yet. Set DOCLING_CACHE_DIR to the workspace docling-cache directory for future runs as well as HF_HOME/TEMP/TMP. Inspection confirms this converter's model snapshots use the Hugging Face cache, so the proposed pinned cache reference bindings match its offline lookup.

Next action: obtain explicit approval for the five Docling files (or an existing compatible asset directory), then rerun conversion/source-cell mapping and both blocked integration tests. All package setup/model smoke work already authorized is complete. Keep source/domain review pending and preserve candidate inactivity; actual retrieval rankings/calibration still require the source-linked corpus and review evidence.
