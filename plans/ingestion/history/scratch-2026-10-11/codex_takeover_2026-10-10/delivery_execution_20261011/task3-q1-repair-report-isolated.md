# Medium T3-Q1 bounded draft repair

Implemented and committed locally as **5342587c56dd3dcb3cc1201bd8f7a1561b8c2f88**, parent **5596f810c4d08c7aef87503d06c0027d6b961a4b**. The candidate worktree is clean. This is implementation evidence only; no Spec/Standards recheck, whole-branch review, dev integration or push was performed. The original Standards FAIL remains pending a separately authorized independent recheck.

Authorization: root's bounded repair dispatch, current checkpoint's confirmed-defect draft repair entry and emergency-fix authorization, plus ISOLATED_CLI_PICKUP.md step 3. The historical Task3 brief's no-worker-commit restriction was superseded by the explicit current instruction to save ONE local draft commit. No descendants or Claude execution.

Changed exactly the three authorized paths:

- backend/bintanong_tools/document_ingest/prospectus_rules.py: after validating every owned cell independently, multi-cell fields become one complete SourceSpan. Raw fragments are joined in actual table row/column order, checked against the regenerated FieldCandidate.value, and retain all exact cell IDs. Same-page/origin/page-size agreement is required. The bbox is an envelope derived from validated captured boxes, honoring TOPLEFT or BOTTOMLEFT. Only complete wording reaches the existing compiler, so a partial cell cannot falsely support a shortened field. Single-cell spans retain existing behavior. Year/semester filtering still excludes unmatched normalized labels and now uses validated complete text rather than unordered cell IDs.
- tests/test_prospectus_rule_handoff.py: persisted the exact two public synthetic partial-field attacks and three complete-continuation cases. Includes valid full title, valid all-of prerequisite and complete OR/equivalence wording that remains semantically blocked. All use actual producer/parser/checked loader/bridge/compiler; candidate edits retain raw conversion and rehash existing manifests. The prerequisite attack recomputes existing pending-only authority diagnostics exactly as the historical reproducer did.
- docs/decisions/phase-02-unified-ingestion.md: explains complete field spans, raw fragment order, derived bbox envelope and unsupported multi-page/origin cases.

Compiler, producer, loader, helpers, contracts, runtime, dependencies and locks were not changed. No compiler result mutation or new output schema was introduced.

## Actual test results

All four imported production modules resolved beneath R. System py -3.13 -B, process-local PYTHONPATH=R, offline/no-bytecode, pytest no-cache, absolute R rootdir/confcutdir and new external basetemps were used. Every PowerShell first selected R with Set-Location -LiteralPath; login:false.

1. Persisted RED before production edit: **5 failed, 42 deselected in 16.50s, exit 1**. The exact historical title and prerequisite assertions failed after explicit checked-loader acceptance. The three complete fields also failed because the compiler's canonical cell-ID order put c14 before c7/c9. No import/collection failure counted as RED. Exact command: task3-q1-repair-red-command.ps1; output: task3-q1-repair-red.log.
2. Initial handoff GREEN attempt: **1 failed, 46 passed in 23.58s, exit 1**. All five new continuation cases passed. Existing test_combined_synthetic_conversion_bundle_bridge_compiler failed because moving the year/semester filter initially exposed unmatched normalized heading spans. The filter was corrected without changing the test. Exact command: task3-q1-repair-green-command.ps1; output: task3-q1-repair-green.log. This failed log is retained.
3. Final required four-module focused gate: **253 passed in 32.87s, exit 0**, covering the previous 248 cases plus five new cases. Modules: test_prospectus_rule_handoff.py, test_prospectus_ingestion.py, test_candidate_bundle.py, test_rule_candidates.py. Exact command: task3-q1-repair-focused-command.ps1; output: task3-q1-repair-focused.log. No further test batch ran after this PASS.

The focused gate preserves T3-S1 nonblank-CS102 blocking, genuine blank geometry/ownership, unrelated valid ledger references, missing/ambiguous/semantic-repair support, unknown XX999, inactive flags, pending source authority, native single-cell origins, immutability and no publication/network/runtime. Complete multi-cell raw wording remains in blocked review spans, including the printed equivalence condition. Numeric support remains delegated to the compiler's existing complete-number checks; no numeric coercion/default/semantic correction was added.

The first RED converter import logged the existing installed Docling duplicate granite_vision_v4 preset message; it did not cause any assertion failure. No dependency changes were made. Final focused PASS emitted no warning summary. Git emitted existing LF-to-CRLF notices while checking/staging the three files; diff --check and cached diff --check both exited 0.

## Preservation and commit commands

New external preservation script task3-q1-repair-preservation.py and pre/edited/post JSON snapshots preserve the exact owner FOUR status/head/SHA256 values against owner-four-pre-integration.json, all **23 other worktrees (24 total, including R)** tips/status from isolated-pickup-preservation.json, the frozen 378-file exact manifest/hash set with no links/junctions, every frozen package file, historical original attacks/logs/scripts, protected source bytes, and dev/origin-dev refs at 0caeaba8d8221a0f75b154e94bc3167b780f1407. The supplied preservation list contains 24 total worktrees; no claim of 24 additional worktrees is made. Preflight required clean parent; edited check required unchanged index and HEAD; postflight required one new child commit and clean status with exactly the three allowed committed paths.

Preservation invocations, each exit 0, used this prefix and the modes pre, edited, post respectively:

```powershell
Set-Location -LiteralPath 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$env:PYTHONDONTWRITEBYTECODE = '1'
py -3.13 -B 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/task3-q1-repair-preservation.py' pre
```

The edited verification shell also ran git diff --check, git diff --stat and git diff -- for the bridge; overall exit 0. Exact three-path stage, cached whitespace check, commit and postflight commands (all completed, shell exit 0):

```powershell
Set-Location -LiteralPath 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
git -C 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010' add -- 'backend/bintanong_tools/document_ingest/prospectus_rules.py' 'tests/test_prospectus_rule_handoff.py' 'docs/decisions/phase-02-unified-ingestion.md'
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
git -C 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010' diff --cached --check
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
git -C 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010' diff --cached --name-only
git -C 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010' commit -m 'fix(ingest): bind continued fields to complete source wording'
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
git -C 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010' rev-parse HEAD
$env:PYTHONDONTWRITEBYTECODE = '1'
py -3.13 -B 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/task3-q1-repair-preservation.py' post
exit $LASTEXITCODE
```

Commit output: 3 files changed, 110 insertions, 5 deletions; no attribution trailer. Exact changed source byte hashes are in task3-q1-repair-preservation-post.json. Owner checkout and protected refs were not written. No stash/reset/clean/process kill/owner staging.

## Read context and quota

Read the supplied handoff/current checkpoint, complete first Standards finding and its historical two-case script/log, scoped T3-S1 PASS, Task3 brief/scope/report, shared ingestion SPEC and IMPLEMENTATION_PLAN, Phase6 SPEC, actual bridge/handoff tests/decision record and interacting compiler/FieldCandidate conversion/text/source-contract code. Extractor implementer role was Markdown only. Applied Codex test-driven-development (including writing-good-tests), receiving-code-review and surgical-patch skills. No relevant AGENTS.md was found in R or its applicable ancestors. A broad read-only AGENTS discovery emitted access-denied for an unrelated Intel logs directory; no unrelated file was edited or used for instructions.

Corresponding isolated-profile usage helper was read completely and executed against this CODEX_HOME=.codex-bintanong-b release 0.162.1. Pre sample **14:15:27 Manila: 31% primary / 5% weekly**, ordinary usage allowed, exit 0; resets **18:52:20 Manila October 11 / 13:52:20 Manila October 18**. Saved task3-q1-repair-usage-pre.json. Completion refresh failed **account/read: workspace routing discovery timed out**, actual helper exit 1. Post usage is explicitly **UNVERIFIED**, saved task3-q1-repair-usage-post.json; the last successful sample is not presented as current. An earlier completion-refresh tool call returned no command result and produced no JSON; the explicit retry produced the recorded failure. No account/config/interpreter changes or unidentified process termination were attempted. No additional test batches followed the final PASS.

Both refresh commands used the initial R selection, PYTHONDONTWRITEBYTECODE=1 and py -3.13 -B isolated_profile_usage.py piped to Tee-Object at the corresponding new pre/post JSON path. The helper's own finally block only manages its own subprocess. The post failure traceback was reported to root; no new account health claim is made.

## Limits and remaining work

No broad ~4k suite, original/private inputs, OCR certification, installation/download, global configuration, API/Docker, routing/embedding, Janus/executable Prolog, runtime/institutional activation or historical-debt clearance. This synthetic bounded repair establishes complete-field consistency; unsigned local hashes are not producer authentication. Multi-page/mixed-origin or incomplete geometric fields remain unsupported, with raw fragments retained in captured review inputs. New focused tests cover same-page TOPLEFT continuation envelopes; multi-cell BOTTOMLEFT envelope arithmetic and mixed-page/origin fallback were implemented conservatively but not independently probed by new cases. Existing single-cell BOTTOMLEFT regression passed.

Root must independently verify/freeze this clean draft commit and obtain the ONE specific Medium Standards recheck exception before dispatching that review. The original T3-S1 Spec exception cannot be reused. No review verdict, integration or push permission is conferred by this report. Worker stops here.
