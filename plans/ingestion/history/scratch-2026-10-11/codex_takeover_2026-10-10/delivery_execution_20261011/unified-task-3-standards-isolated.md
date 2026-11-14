# Task3 FIRST full Standards review — isolated profile

**FAIL — CHANGES NEEDED.** One confirmed **Medium T3-Q1**. This is the first independent full Task3 Standards review, following the completed scoped T3-S1 Spec continuation PASS. It is not a Spec recheck, an implementation review of my own changes, or a whole-branch verdict.

Scope: `6f9a3ec5b5df8b44a5d42a1d7358dee7f68c8dd8..5596f810c4d08c7aef87503d06c0027d6b961a4b`, exactly `backend/bintanong_tools/document_ingest/prospectus_rules.py`, `tests/test_prospectus_rule_handoff.py`, and the extension to `docs/decisions/phase-02-unified-ingestion.md`, plus interacting existing helpers. Actual reviewed tree: `unified-task-3-review-5596f810/candidate`, 378 files. No code repair, staging, commits, ref movement, owner edits, or descendants.

## Strengths

- The 204-line bridge has a clear library interface and delegates publication checks and compilation to existing modules. It reuses actual extractor FieldCandidates rather than reconstructing ownership from a row or chunk union.
- Supplied cell records are compared with captured raw normalized records; physical geometry comes from checked captured-PDF metadata, and native TOPLEFT/BOTTOMLEFT origins are retained. Missing geometry, provenance and ambiguous overlaps generally stay blocked; forged bindings refuse.
- The reviewed-blank repair validates genuine blank ownership and filters accepted entries individually after existing ledger validation, retaining unrelated valid decisions. Pending authority, inactive output, immutable source/bundle bytes, and retained XX999 blockers have meaningful synthetic integration coverage.
- Documentation describes the actual external-bundle API, unsupported derived fields, unsigned local integrity limits, and deferred source/OCR/runtime work accurately.

## Confirmed finding

**Medium T3-Q1 — an individual continuation cell can falsely support a shortened complete field.** Location: `backend/bintanong_tools/document_ingest/prospectus_rules.py:185–194`, particularly lines 192–194. Interacting existing behavior: `backend/bintanong_tools/prospectus_extractor/rule_candidates.py:118–127`.

The new bridge supplies all exact owner field spans, but checks the complete candidate wording only for year/semester. For prerequisite/title fields it never checks that the candidate still represents the complete regenerated field. The existing compiler's `_supported` accepts a match to **any individual span**, or their concatenation. Therefore a changed candidate equal to the first cell of a continued field is treated as source-supported even when another owned cell contradicts or extends it. This is a bridge binding gap, not a request to alter the protected compiler.

Concrete public synthetic reproducer: `task3-multicell-standards-first-isolated-20261011.py`, two tests. Both use a captured synthetic PDF, synthetic converter, actual producer/parser/audit, checked loader, bridge and pure compiler. The source PDF, captured raw conversion and field provenance are retained. Only the candidate JSON and its two manifest hashes are changed; the prerequisite variant also recomputes existing pending-only authority diagnostics so it remains internally consistent. No source or approval state is promoted.

1. `test_partial_multicell_prerequisite_must_remain_blocked`: original regenerated CS101 wording is **`CS102 or equivalent`**, printed in owned cell `t0-c9` (`CS102`) and continuation cell `t0-c14` (`or equivalent`). Change the candidate wording to `CS102`, references to `["CS102"]`, unresolved/standing lists to empty, and state to `resolved`. Explicit `load_candidate_bundle` acceptance succeeds. Actual returned prerequisite record has `raw_text="CS102"`, `prerequisite_state="resolved"`, **`blockers=[]`**, and **`review_view.clauses=["prerequisite('CS101', 'CS102')."]`**. Its retained spans still print both `or equivalent` and `CS102`. The assertion requiring a blocker fails.
2. `test_partial_multicell_title_must_remain_unmatched`: original regenerated title is **`Introduction to Computing with Advanced Topics`**, in the first title cell plus continuation cell. Change only candidate title to `Introduction to Computing`. Checked loading succeeds; both printed fragments remain in its spans, but `missing_or_unmatched_field_evidence:course_title` is absent. The course's other derived-field blockers limit the overall artifact; this still falsely classifies the shortened title as directly supported. The title-specific assertion fails.

Independent result: **2 failed in 23.76s, actual exit 1**. Both failures are the intended behavior assertions after successful publication and checked loading, not collection/import failures. Log: `task3-multicell-standards-first-isolated-20261011.log`. The first converter import also logged the pre-existing installed Docling duplicate `granite_vision_v4` preset message; it did not cause either failure or require a dependency change.

Impact: a printed equivalence condition can disappear from the blocker-free prerequisite review view while the untouched source spans still contain it. This violates complete field correspondence and the requirement that alternatives/semantic repairs remain blocked. Output remains inactive with null approval and pending source states, so severity is Medium, not a demonstrated runtime or institutional activation defect. The title variant is the same cause and is not counted as a separate finding.

Recommended bounded fix: validate candidate correspondence against the **complete regenerated directly owned field**, accounting for continuation wording, before it can acquire usable field support; refuse or retain a blocker on the mismatch. Persist both regressions in the allowed handoff test path. Preserve genuine complete fields, all owned raw text, unresolved alternatives, and the T3-S1 genuine-blank/unrelated-ledger behavior. No repair or repair verdict is performed here.

Other confirmed Critical/High/Low findings: **NONE**. Broader suspicions are not reported as defects.

## Independent evidence and commands

Full dispatched focused suite: **248 passed in 48.62s, actual pytest exit 0**. This includes all 42 handoff cases, producer, checked-bundle and compiler modules, including actual snapshot/converter → producer → checked loader → bridge → compiler acceptance. It covers altered hashes, deliberately rehashed ownership, malformed locators/IDs, pending/privileged authority, physical geometry/native origins, missing/ambiguous field evidence, semantic repairs, blanks/applicable/foreign/stale/edited ledger, retained XX999, inactive views and absence of publication/network/Prolog execution. The continuation-cell probes were justified by an uncovered complete-field correspondence concern found during code inspection; no broad suite or repeated full suite ran.

Seven pre-test import origins (bridge, producer, bundle, compiler, sections, loader, source contracts) resolved beneath the frozen archive; origin assertion exit **0**. Full exact command and exit capture: `task3-standards-first-isolated-20261011-command.ps1`; saved exits `task3-standards-first-isolated-20261011-exits.json`; output `task3-standards-first-isolated-20261011.log`.

```powershell
Set-Location -LiteralPath 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$env:PYTHONPATH='E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/unified-task-3-review-5596f810/candidate'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
$env:HF_DATASETS_OFFLINE='1'
Set-Location -LiteralPath $env:PYTHONPATH
py -3.13 -B -c "import pathlib,backend.bintanong_tools.document_ingest.prospectus_rules as b,backend.bintanong_tools.document_ingest.prospectus as p,backend.bintanong_tools.document_ingest.bundle as l,backend.bintanong_tools.prospectus_extractor.rule_candidates as c,backend.bintanong_tools.prospectus_extractor.sections as s,backend.bintanong_tools.prospectus_extractor.loader as e,backend.bintanong_contracts.source as t; r=pathlib.Path.cwd(); assert all(pathlib.Path(m.__file__).resolve().is_relative_to(r) for m in (b,p,l,c,s,e,t)); print([m.__file__ for m in (b,p,l,c,s,e,t)])"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
py -3.13 -B -m pytest "$env:PYTHONPATH/tests/test_prospectus_rule_handoff.py" "$env:PYTHONPATH/tests/test_prospectus_ingestion.py" "$env:PYTHONPATH/tests/test_candidate_bundle.py" "$env:PYTHONPATH/tests/test_rule_candidates.py" -q -p no:cacheprovider --rootdir $env:PYTHONPATH --confcutdir $env:PYTHONPATH --basetemp 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/task3-standards-first-isolated-20261011-temp' 2>&1 | Tee-Object -FilePath 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/task3-standards-first-isolated-20261011.log'
$task3StandardsExit=$LASTEXITCODE
Set-Location -LiteralPath 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
Write-Output "ACTUAL_PYTEST_EXIT=$task3StandardsExit"
exit $task3StandardsExit
```

Exact continuation probe command used the same five environment values and initial worktree/archive selections above, then the following origin/assertion, pytest invocation, exit capture and restoration (origin exit 0, pytest exit 1):

```powershell
py -3.13 -B -c "import pathlib,backend.bintanong_tools.document_ingest.prospectus_rules as b; assert pathlib.Path(b.__file__).resolve().is_relative_to(pathlib.Path.cwd()); print(b.__file__)"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
py -3.13 -B -m pytest 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/task3-multicell-standards-first-isolated-20261011.py' -q -s -p no:cacheprovider --rootdir $env:PYTHONPATH --confcutdir $env:PYTHONPATH --basetemp 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/task3-multicell-standards-first-isolated-20261011-temp' 2>&1 | Tee-Object -FilePath 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/task3-multicell-standards-first-isolated-20261011.log'
$task3MulticellExit=$LASTEXITCODE
Set-Location -LiteralPath 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
Write-Output "ACTUAL_MULTICELL_EXIT=$task3MulticellExit"
exit $task3MulticellExit
```

Read completely the supplied pickup, review-common, full Task3 scope/brief/report/initial Spec/Spec continuation, shared ingestion SPEC/IMPLEMENTATION_PLAN and Phase6 SPEC; reviewer role, both historical Standards templates and current requesting-code-review skill/template were Markdown only. Reviewed the complete full Task3 patch and actual changed bridge/test/decision record, with interacting checked-loader/producer/geometry, parser/section ownership, normalized cells, native bbox adapter, layout, source-span, ledger/current-decision, prerequisite classification, authority and compiler code. Prior root/reviewer counts were context, not independent evidence.

The documented library command matches the actual import, Path argument and in-memory JSON result; its example external path is illustrative. No original corpus command was run. Existing helper interfaces were not modified. No behavior-preservation claim is made for the unrelated whole branch.

## Preservation and account usage

Preflight and postflight each exited **0**. Fully read `task3-recheck-preservation.py` first, then created a new-suffix copy adapted to the **full Task3 base**, keeping the original script/reports/logs untouched. New script: `task3-preservation-standards-first-isolated-20261011.py`; snapshots `task3-standards-first-isolated-20261011-preflight.json` and `...-postflight.json`, exact comparison equal.

```powershell
Set-Location -LiteralPath 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$env:PYTHONDONTWRITEBYTECODE='1'
py -3.13 -B 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/task3-preservation-standards-first-isolated-20261011.py' pre
# After independent tests, same initial worktree selection/environment:
py -3.13 -B 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/task3-preservation-standards-first-isolated-20261011.py' post
```

Verified **378 exact manifest files, exact actual file set, every SHA256, no symlinks/junctions**, package manifest/change.patch/stat, full Task3 patch and whole-branch patch/stat/commits preserved. Source/owner HEAD, refs, index, status and all tracked byte hashes unchanged. Supplemental explicit **all FOUR owner SHA256 values and exact status/head** match `owner-four-pre-integration.json`, including the three untracked plans omitted from the original tracked-byte script; both new snapshots include those checks. Initial pickup preservation remains consistent. Historical adversarial script and original preservation-script hashes unchanged. Candidate clean at `5596f810`; dev and origin/dev remain `0caeaba8`; initial independent `git ls-remote origin refs/heads/dev` exit 0 returned exact `0caeaba8d8221a0f75b154e94bc3167b780f1407`. Full Task3 `git diff --check` exit 0; exactly three authorized paths in the pinned range.

Corresponding isolated-profile helper read completely and independently refreshed before/after using process-local `CODEX_HOME=C:/Users/Hawksprey/.codex-bintanong-b`, its release 0.162.1 local app-server and `account/rateLimits/read`; both helper exits 0. No account ID, auth token or email exposed. Pre sample **14:06:05 Manila, 21% primary / 3% weekly**; post **14:12:15 Manila, 28% / 4%**, ordinary allowed. Resets **18:52:20 Manila October 11 / 13:52:20 Manila October 18**. Evidence: `task3-usage-standards-first-isolated-20261011-pre.json`, `...-post.json`. Thresholds were not reached. Every PowerShell first selected R, used login:false; tests used system py3.13-B, archive cwd/process PYTHONPATH, no-bytecode/offline/no-cache, absolute root/confcutdir and new external basetemps. No installs/downloads/global configuration/interpreter changes/private inputs/API/Docker/routing/embeddings/Janus/executable Prolog. No owner or other CLI process was killed.

## Declined to judge

- Whole-branch architecture/compatibility and dev integration/push: a separate independent whole-branch gate is required after Task3 passes; this finding keeps that gate closed.
- Original prospectus/Handbook/Charter accuracy, real converter/OCR fidelity, phone-photo measurements and human/source/domain approval: synthetic fixtures prove interface behavior only; original corpus and institutional review were explicitly deferred.
- Authentication against a producer replacing all source/raw artifacts and recomputing hashes: local unsigned integrity is documented consistency only. **T3-Q1 is not declined on that ground**: the captured raw field is left untouched and directly contradicts the new supported semantics.
- Review correction materialization and new review authority: explicitly outside this bridge; the existing ledger/accepted-blank interface is reused. No new approval system was required or tested.
- Runtime Prolog/Janus/eligibility, routing/embeddings, API/Docker, private lifecycle and institutional activation: explicitly excluded and not exercised.
- Full ~4k suite, mutation campaign and historical M1/F/session debts: dispatched focused review only; no historical clearance is inferred.
- Additional scalar/container and ordering variants beyond the completed focused suite and the concrete two-case continuation reproducer: no wider investigation after the confirmed finding; no untested suspicion is elevated to a finding.

**Assessment: FAIL — CHANGES NEEDED (Medium T3-Q1).** The focused suite passes, but the independent concrete continuation probes show partial candidate wording can gain false complete-field support. No repair/recheck/whole-branch/integration approval is conferred. Stop here for the coordinator's separate bounded repair workflow and applicable owner recheck rule.
