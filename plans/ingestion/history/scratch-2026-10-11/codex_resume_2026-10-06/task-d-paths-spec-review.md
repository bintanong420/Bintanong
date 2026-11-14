# Phase D S1 specification review

## Reviewed range and state

- BASE: `52da4aaca7d734e83054b1ecd39221ac09302a3b`
- TIP / current HEAD: `4320327bb68ec0973dd79ee7716ab5d893fe00a8`
- Checkout: `C:\Users\Hawksprey\source\repos\Bintanong-wt\phase-d`
- Start and end Git status: ` M plans/plan_current_progress/extractor_split_progress.md` only; expected postcommit progress checkpoint (14 added lines). Index clean; no untracked files reported. No working-tree, index, HEAD, branch, dependency, home-output or prior-artifact changes made by this review.

Read the S1 brief, latest finalized-root/32-hex ruling in preflight-ledger.md, review package/report, immutable production/test/progress diff, actual code, and callers through CLI, BatchConfig/build_batch_items, pipeline, loader cache writes, publication and failure preservation. Applied the current superpowers 6.4.2 requesting-code-review/code-reviewer.md instructions. No subagents or repeated broad test runs.

## Strengths and requirement checks

- `backend/bintanong_tools/prospectus_extractor/paths.py:36`: default exactly `Path.home() / 'Bintanong' / 'output'`. BatchConfig uses its default factory; CLI batch/grid and PDF pipeline default paths call this helper. Explicit output selection remains in the unchanged caller branches. JSON review-input sibling output behavior remains as before. No migration/move/delete behavior added; documented old consumers must pass explicit --output.
- `backend/bintanong_tools/prospectus_extractor/publish.py:60`: one private prefix helper reuses shared identity.bytes_sha256 over UTF-8 base, truncating to 32 hex characters. New stage adds eight UUID hex characters; actual stage name length 44. Generation and cleanup share the prefix. Tests independently pin ASCII/Unicode digest values, retain unrelated directories, a different full digest sharing the first eight characters, another stem, and matching regular files.
- `backend/bintanong_tools/prospectus_extractor/loader.py:312`: only tempfile.mkstemp's prefix changes to .t-; suffix .tmp, same-directory uniqueness, fd/write/replace, retry and exception cleanup remain intact. Interleaved writer, persistent lock and interrupted write checks preserve old/complete data and remove temporary files. Actual generated temp name length 15.
- Unchanged output_names, pipeline cache-name construction and write_failure retain final/cache artifact names and `failed/<base>/`. Publication order, manifest validation, loaded-result identity and atomic replace ownership are untouched.
- Projection helper actually builds batch paths and calls implemented stage/temp helpers in external scratch, including all companions/cache metadata and failure copies. Recorded 44-source maxima are final181/stage226/temp161/failed251 with root35; old final/cache maximum268. The longest actual Tiniguiban CS relative directory and filename is included. The Citizens Charter `(2)` alternative is separately covered by the parametrized boundary test and confirmed present in the source inventory; inventory labels it a distinct 643-page BOR proposal, not the short prospectus. No conversion/opening of that proposal is required or claimed by S1.
- Reviewed actual log tails: authentic final RED 8 failed/1 passed/88 deselected, GREEN 9 passed/88 deselected, focused 386 passed, full 961 passed plus 13 subtests and three upstream deprecation warnings. Full command explicitly excludes approved API/embedding tests. No fresh test execution claimed by this reviewer; no suspected defect required a targeted probe. Immutable-range `git diff --check` passed.

## Findings

Critical: NONE.

Important: NONE.

Minor: NONE.

No concrete specification deviation or reproducible defect found in the reviewed change. No unresolved suspicion remains after tracing callers and projection/test evidence.

## Declined to judge

- Guaranteed MAX_PATH support for arbitrary longer home directories or explicit roots: expressly outside this S1 ruling; current corpus leaves eight additional root characters below260 and the limitation/short explicit-output remedy is documented.
- Cleanup of legacy `.<base>.staging-*` directories: new prefix deliberately does not target them; migration/deletion of previous artifacts was not authorized and the report discloses their retention.
- Multiple simultaneous writers to one output stem, including filesystem case aliases: existing one-writer-per-stem assumption is explicitly retained; no concurrency protocol is part of S1.
- Whole-output-set atomicity: existing file-by-file publication plus manifest-last verification is unchanged; S1 requires preserving it, not replacing the publication protocol.
- Extractor accuracy, fresh original-PDF conversion, semantic44 comparison, GUI comprehensive suite, selftest80 and trials: explicit later final-D gates; path projection is not semantic validation.
- S2, S4, F5, final Phase D completion and downstream task gates: still queued, not outcomes of this review.

## Verdict

**APPROVED** — S1 specification gate only. The minimal implementation matches the finalized requirements and documented limits. Separate quality review follows; this does not declare Phase D complete or authorize integration/deployment.
