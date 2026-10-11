# Unified Task 1 independent specification review

Verdict: PASS. Confirmed findings: NONE. APPROVED.

Reviewed BASE 57b598522cc7ed5d13e40eb8d1bcafede8c9ba1b to HEAD 8f4c0a6c674ce33bcbe0fc91c76e03b4184da261 using the frozen `unified-task-1-review-8f4c0a6c/candidate` archive and its supplied patch. This is a separate Codex specification review; no implementer report or root/worker test count was trusted. The full dispatch brief and both requested reviewer Markdown prompts were read. No descendants, Claude invocation, Standards review, historical M1 recheck, F-file adoption, generic repair, or broader suite was performed.

## Specification

The patch adds exactly the three permitted files: the prospectus binder, focused tests, and decision document. It does not change the chunk adapter, extractor, loaders, public contracts, dependency/configuration files, or runtime integrations.

- `prospectus.py:23-30` reparses the pending register and checks payload digest before chunk conversion. The existing loader enforces byte-derived document/version/edition identities and pending scope/states.
- `prospectus.py:33-63` consumes semantic chunks followed by hierarchical chunks, preserving their order. It checks group/chunk/span shapes, SHA identities, duplicate IDs, privileged fields, per-chunk/span byte digests, and non-null preexisting source IDs before the conversion/binding loop.
- `prospectus.py:65-82` reuses `adapt_chunk` with supplied page sizes, records original chunk ID and adapter reason for each unsupported chunk, rejects incomplete printed/geometry support, binds registered states/evidence through the shared helper, and checks the resulting chunk and each span. Output uses the four requested keys and serialized existing Chunk contracts.
- The adapter recomputes content hashes and legacy IDs; the binder preserves those IDs/text/hashes. The current register loader rejects identity schemes other than `ver-<byteSHA>` and its corresponding document/edition forms. The decision document records the migration-policy requirement for a future scheme.
- The 20 focused tests cover both source groups, identity/order preservation, pending states, binding, input immutability, missing/mismatching digest, foreign/non-null claims, duplicate identity, forged privileged fields, malformed shapes, missing page geometry, raw-text hash mismatch, incomplete source support, and promoted-register refusal. The binder's successful flow and the global precheck flow do not mutate input structures.
- An additional external assert-based check injected a foreign version into the second group's span and instrumented the shared binder. The entire call refused before any `bind_chunk` invocation, and payload/version/page_sizes remained unchanged. This directly verifies the new boundary's check-before-write behavior; it does not change the historical M1 52/52 claim or its separate review debt.

No missing requirement, unrelated feature, or confirmed specification defect was found within the authorized Task 1 scope.

## Independent evidence

Before testing, the actual imported `__file__` of prospectus/register/chunk_adapter/source was asserted to reside under the frozen candidate archive. Tests used system `py -3.13 -B`, process-local absolute archive PYTHONPATH, PYTHONDONTWRITEBYTECODE=1, HF_HUB_OFFLINE=1, TRANSFORMERS_OFFLINE=1, HF_DATASETS_OFFLINE=1, and PIP_NO_INDEX=1. The test command used absolute paths for exactly:

1. tests/test_prospectus_ingestion.py
2. tests/test_contracts_chunk_adapter.py
3. tests/test_register_minting.py

Arguments: `-q -p no:cacheprovider --basetemp` with a new absolute external directory. Actual independent result: **48 passed in 0.45s; exit 0**. The external check-before-write script also passed with exit 0.

The preexisting raw `unified-task-1-red.log` was inspected directly: it records 20 focused tests failing because the feature module is absent. Historical RED was not rerun against this committed GREEN archive; the raw log alone does not independently prove command-line options, process exit code, or pre-implementation chronology. Those historical execution details remain outside the evidence I personally reproduced. This limitation is not presented as a code defect.

Archive integrity: all **371** manifest-listed candidate files matched SHA-256 values before and after review. `manifest.json`, `change.patch`, and `change-stat.txt` hashes also remained identical. Only external review reports/logs/reproducer were created; no candidate/worktree/index/HEAD/code changes, installs, downloads, `.pth`, global configuration, or dependency/lock changes were made.

Evidence files in this delivery directory:

- unified-task-1-spec-hashes-before.json
- unified-task-1-spec-hashes-after.json
- unified-task-1-spec-test-command.json (exact absolute command inputs/environment)
- unified-task-1-spec-imports.log
- unified-task-1-spec-tests.log
- unified-task-1-spec-precheck.py
- unified-task-1-spec-precheck.log

Fresh usage: 15% primary / 16% weekly at 02:15:59 Manila before the test batch; 18% / 16% at 02:18:30 Manila afterward. Both were below the 85% stop threshold. Worktree location was restored after the usage script and archive execution.

Skipped: full suite, real-corpus conversion, deployment/institutional activation, separate Standards review, and historical M1/F/session debts. Risk: this synthetic candidate-binding approval establishes neither source/content approval nor production readiness.

APPROVED
