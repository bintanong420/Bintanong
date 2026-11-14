# Phase D S1 quality review

## Reviewed range and state

- BASE: `52da4aaca7d734e83054b1ecd39221ac09302a3b`
- TIP / observed HEAD throughout review: `4320327bb68ec0973dd79ee7716ab5d893fe00a8`
- Checkout: `C:\Users\Hawksprey\source\repos\Bintanong-wt\phase-d`
- Start status: ` M plans/plan_current_progress/extractor_split_progress.md` only.
- End observed status: the same single modified progress path; 21 added lines; index clean and no untracked files reported. The controller's progress checkpoints may advance during read-only reviews; this review made no checkout changes.

Read the review package, S1 brief/report/spec APPROVED, finalized-root and 32-hex preflight rulings, immutable diff, production modules and callers through CLI, TUI/BatchConfig, build_batch_items, pipeline, loader, publication and failure preservation. Applied the current superpowers 6.4.2 requesting-code-review/code-reviewer.md template. No subagents, dependency changes, checkout/index/HEAD mutations, home writes, old-output moves/deletions or repeated broad suites.

## Strengths

- `backend/bintanong_tools/prospectus_extractor/paths.py:36`: the portable home-relative root is centralized. BatchConfig's factory supplies the TUI; CLI batch/grid and PDF pipeline call the helper. Explicit output branches are unchanged. JSON review-input sibling output behavior is unchanged. The helper does not create directories. The report records the old-output migration rule and limited path budget.
- `backend/bintanong_tools/prospectus_extractor/publish.py:60`: one small private helper shares the UTF-8 stem digest prefix between generation and cleanup, reusing identity.bytes_sha256. No generic path abstraction or new dependency. The 32-hex key avoids the practical collision weakness of the superseded eight-hex proposal; generation adds eight UUID hex characters. A random name collision is not silently reused or overwritten: mkdir raises rather than accepting an existing stage. One writer per output stem remains necessary.
- `publish.py:64`: cleanup stays in the supplied parent and matches the full stem prefix. The test at `tests/test_prospectus_publish.py:194` uses real directories/files and independent literal digests: stale matching directories disappear, a different digest sharing eight leading characters survives, another stem survives, unrelated directories survive, and a matching regular file survives. Generation/cleanup cannot drift between independent prefix implementations.
- `backend/bintanong_tools/prospectus_extractor/loader.py:312`: only the mkstemp prefix changes. Stdlib uniqueness, same-directory replacement, retries and per-call temporary-file ownership remain intact. Tests at `tests/test_prospectus_cache.py:192`, `:235` and `:256` exercise real generated temporary names and real filesystem bytes, with injected interleaving/write/replace failures. Old bytes survive failed writes/replaces and temporary files are removed.
- The pipeline uses the returned stage path directly; no caller parses or depends on the former long stage name. Existing conversion/parser failure tests at `tests/test_prospectus_publication.py:21` and `:41` keep previously published artifacts byte-identical and preserve diagnostics. The existing interruption matrix verifies coherent generations at each publication boundary. S1 changes neither manifest-last publication nor failed/<base>/ copying and final cleanup.
- Path coverage uses the actual longest corpus-relative Tiniguiban CS directory and filename, plus the separate Citizens Charter (2) boundary. Tests at `tests/test_prospectus_publish.py:236` generate actual stages and atomic temporary files externally, then project final, staged, temporary and failure-copy paths. The all44 external projection similarly calls implemented helpers; its root35, stage44 and temp15 lengths are observed rather than invented. Maxima final181/stage226/temp161/failed251 include unchanged raw cache metadata names and failure copies; old final/cache maximum268. No original-PDF conversion or home-output write is implied by this evidence.

## Issues

Critical: NONE.

Important: NONE.

Minor: NONE.

No concrete regression, unnecessary abstraction, unsafe change in cleanup scope, or missing S1 failure-preservation check found. No unresolved suspicion remains requiring a targeted probe. No new tests were executed by this reviewer.

## Verification evidence

Read the actual log tails: final authentic RED 8 failed / 1 passed / 88 deselected; GREEN 9 passed / 88 deselected; focused 386 passed; main full 961 passed plus 13 subtests and three upstream deprecation warnings. The full command in the report retains the approved API/embedding exclusions. These are the implementer's existing execution results, not fresh runs claimed by this review. Immutable-range git diff --check passed.

## Declined to judge

- Arbitrarily longer home directories or explicit output roots: the approved S1 ruling expressly limits the current corpus budget; eight additional root characters fit below260, and a shorter explicit output root is the documented remedy.
- Cleanup/migration of legacy .<base>.staging-* directories or old default artifacts: explicitly retained; no migration/deletion of prior artifacts is authorized by S1.
- Simultaneous writers to one output stem, including case aliases on a case-insensitive filesystem: the approved one-writer-per-stem assumption is retained; S1 does not introduce a concurrency protocol.
- New hardening against hostile local staging-directory replacement or changed ACLs: local output-directory ownership and existing cleanup/error semantics are unchanged; S1 adds no remote or multi-tenant filesystem trust boundary.
- Whole-output-set atomic transactions and failure-diagnostics persistence under a failing filesystem: existing file-by-file publication, manifest-last detection and diagnostics behavior are unchanged; replacing that protocol is outside S1.
- Fresh extraction accuracy, semantic44 comparison, GUI comprehensive suite, selftest80 and trials: later final-D gates; projected path lengths do not validate extraction semantics.
- S2, S4, F5, final Phase D completion, Task10 and downstream work: still queued, not outcomes of this review.

## Assessment

**APPROVED** — S1 quality gate only. The minimal change preserves output identities, per-call atomic temporary ownership, failure handling and caller behavior while reducing the measured path budget. No fixes are required before proceeding with the remaining queued work; this is not a Phase D completion, merge or deployment authorization.
