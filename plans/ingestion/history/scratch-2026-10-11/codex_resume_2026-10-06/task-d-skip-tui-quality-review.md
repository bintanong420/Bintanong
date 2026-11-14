# Phase D S2/S4 quality review

Specification handoff: APPROVED/NONE in task-d-skip-tui-spec-review.md. This seat independently reviews quality only.

Reviewer: /root/d_skip_tui_quality. Worktree: C:/Users/Hawksprey/source/repos/Bintanong-wt/phase-d. Branch: feat/prospectus-phase-d-safe-cache.
Exact immutable range: 4320327bb68ec0973dd79ee7716ab5d893fe00a8..c40a38c9f633dd085766ca11f81f0dd3890810cc.
S2 commit: 10c2d8b5ac30313c7d5c7d2831fb7c8670cd146a.
S4 commit: c40a38c9f633dd085766ca11f81f0dd3890810cc.

## Confirmed defects

NONE. Critical: NONE. Important: NONE. Task-introduced minor defects: NONE. No reproducer is required because no defect was confirmed.

## Quality checks and strengths

- pipeline.py:349-351 uses identity-presence checks for all four parameters. This neither invokes falsey objects nor consumes generators nor serializes providers. The original outer review_entries remains supplied after build_payload materializes its local parameter once at pipeline.py:75-85. Contextless outputs retain the original run key; context-bearing outputs cannot become eligible by being empty or exhausted.
- batch.py:181-185 accepts only literal True. False, unknown and nonboolean eligibility conservatively rebuild; it adds no identity or authority bypass. Existing audit, expected run key, strict publication verification and requested companion checks still follow at batch.py:186-209. Existing force precedence at batch.py:173-176 remains intact.
- Named risk: direct manifest[run_identity].get could crash or trust malformed identity. Checked the complete affected skip function and publish.py:119-169. read_manifest returns a manifest only after requiring a Mapping identity and validating run key/cache/input binding at publish.py:136-160. The new access is safe for actual parsed manifests.
- Named risk: the new eligibility bit could diverge between main JSON and manifest, allowing a context-created payload to skip. Checked the cut-off pipeline function through pipeline.py:360-363 and existing publisher ownership at publish.py:237-249. The exact main identity is passed to publication; verify_published checks every file digest and main identity equality at publish.py:180-193. No independent eligibility owner or unchecked publication path was added.
- Named risk: a force toggle could affect only one TUI route or lose existing options. Checked tui.py:224-242 and tui.py:272-293, plus actual batch routing at batch.py:235-258. Single-file now forwards the same existing field; batch already passes it. Existing export/device/semantic kwargs and error handling remain intact. The shared process parameter goes to load_document_result at pipeline.py:317-320.
- Named risk: fixture stubs could conceal the context defect or bypass cache/publication behavior. Checked the new tests in the immutable package and scoped fixture definitions tests/conftest.py:19-61,76-109. Context tests at tests/test_prospectus_batch_skip.py:145-219 do not request pipeline_state, so they run actual parsing/auditing/authority and publication with an evidence adapter. TUI route tests at tests/test_prospectus_batch_skip.py:305-359 deliberately stub established payload generation while exercising actual pipeline/cache/publisher and batch skip functions. Tests assert exact refusal reasons, coherent published sets, cache/converter counts and both force values; none merely assert a mocked success.
- tests/test_prospectus_batch_skip.py:43-60 replaces the permissive skip-reason assertion with exact values and checks unchanged output bytes/mtimes. Missing/nonboolean tests update both main identity and its manifest digest and verify coherent publication before the refusal, isolating the intended failure rather than passing because files are corrupt.

Complete affected functions were read only because the immutable package's short hunks cut off their contracts. Outside-diff checks were limited to the named manifest/publication/caller/fixture risks above. No whole-repository crawl, new abstractions, dependencies or production cleanup were requested.

## Evidence inspected

No test or probe was rerun by this quality seat: code inspection left no specific unresolved doubt beyond already exercised behavior. This follows the dispatch and installed scoped-review guidance; passing broad suites were not repeated. All commands below are evidence inspected, not quality-seat execution claims.

- task-d-s2-validated-red.log: 18 failed, 62 deselected, 8.37s; named context/default/malformed-eligibility assertions fail. Superseded fixture and requested-companion errors are preserved and honestly distinguished in the implementer report.
- task-d-s4-red.log: 4 failed, 2 passed, 80 deselected, 7.39s; actual configuration and single-file forwarding assertions fail before the TUI edit.
- Independently executed specification evidence: task-d-s2-spec-review-tests.log, 18 passed/68 deselected, 15.30s; task-d-s4-spec-review-tests.log, 6 passed/80 deselected, 8.55s. No warnings. The spec review also records an external actual Rich/prompt/default probe passing.
- task-d-s4-focused.log: 680 passed, 61.65s, no warnings. Command: main venv Python -m pytest -q tests/test_prospectus_batch_skip.py tests/test_prospectus_identity.py tests/test_prospectus_publish.py tests/test_prospectus_publication.py tests/test_prospectus_cache.py tests/test_prospectus_authority.py tests/test_prospectus_markup.py -p no:cacheprovider --basetemp external/s4-focused-temp.
- task-d-s4-full.log: 984 passed, 13 subtests passed, 3 warnings, 94.15s. Command: main venv Python -m pytest -q tests --ignore=tests/test_api_probes.py --ignore=tests/test_embedding_service.py -p no:cacheprovider --basetemp external/s4-full-temp. Only the approved two exclusions are reported.

## Suspicions and declined items

Unresolved suspicions: NONE.

The three full-suite upstream Docling/Pydantic deprecations (force_full_page_ocr, generate_table_images, RapidOCR rec_font_path) come from tests/test_tools_contract.py::ToolsContractTests::test_synthetic_pdf_fixture_exists_and_parses. They are visible evidence noise, already present in the approved baseline, and unaffected by these edits; they do not establish a task defect. No warning-cleanup rewrite is requested.

No threat model granting an adversary write access to both published output and its manifest was invented. This change preserves existing digest/coherency boundaries; it does not introduce source approval or institutional authority.

Original-corpus extraction correctness cannot be proved by converter doubles. Final comprehensive/corpus/selftest/whole-range D reviews and Task10 remain pending, as do GUI/E/F/OCR/formal/human gates. This task approval does not complete Phase D.

## Read-only boundary

Read the project extractor-reviewer instructions, installed task-reviewer scoped guidance, approved_execution.md, exact brief, implementation report, immutable package and prior specification verdict. No checkout, index, HEAD, branch, progress checkpoint, dependency or main-checkout mutation was performed. Only this external report was written; no child agents or background/test processes were started. Exact refs and dirty progress status are the immutable package/spec-seat observations, not an invented new Git-state verification.

APPROVED
