# Phase 05 real retrieval readiness — 12 October 2026

The owner requested continuation from the prepared 27-question exam toward citation mapping and real retrieval measurements. This document records completed preparation and a concrete dependency setup proposal. It does not approve institutional sources, publish candidate knowledge or advance Phase 05.

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
