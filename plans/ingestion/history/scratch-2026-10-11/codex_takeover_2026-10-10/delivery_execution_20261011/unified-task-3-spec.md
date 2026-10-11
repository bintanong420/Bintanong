# Unified Task3 independent Spec review

Verdict: **FAIL — CHANGES NEEDED**. Initial independent review, not a repair recheck. Standards must wait for an authorized Spec PASS. No repair, staging, commit or ref movement performed.

Reviewed exact BASE `6f9a3ec5b5df8b44a5d42a1d7358dee7f68c8dd8` .. HEAD `12d5e373aaba2a2ec43e7a2624fa1e1a84af4a50`, frozen package `unified-task-3-review-12d5e373`. Exactly three changed paths: prospectus_rules.py, test_prospectus_rule_handoff.py and phase-02-unified-ingestion.md. Historical brief baseline57 is superseded by the dispatched exact range.

## Confirmed finding

**Medium T3-S1 — accepted-blank review can erase a printed prerequisite without a blocker.** Location: `backend/bintanong_tools/document_ingest/prospectus_rules.py:168` (ownership/span mapping at159–166).

The bridge forwards checked candidate wording plus review evidence to the compiler without ensuring a candidate blank prerequisite is actually blank in its regenerated exact owner. The existing compiler intentionally trusts the caller's reviewed-blank field binding: it accepts the applicable ledger at rule_candidates.py:299–303 and skips printed-wording support for reviewed_empty at305. This new bridge is responsible for binding that claim to captured raw cells. Ledger hash/version/locator/current-value consistency alone checks the edited candidate, not whether the captured source is blank.

Concrete public synthetic reproducer: `task3-spec-adversarial.py::test_changed_nonblank_source_cannot_be_reviewed_empty` (external report directory). Produce a real synthetic snapshot/converter -> run_prospectus_ingestion bundle whose CS101 prerequisite cell t0-c9 prints **CS102**. Leave raw conversion, source, geometry and provenance unchanged. In the captured candidate set CS101 prerequisites_raw to empty text, references/unresolved/standing to empty lists and prerequisite_state to reviewed_empty; attach an existing make_entry accepted prerequisites_raw decision with old_value empty, exact current version/PDF/course locator and valid entry integrity. Rehash the changed candidate in both completion manifests. The checked loader accepts it. The bridge returns:

- prerequisite_state=reviewed_empty, raw_text=''; value.all_of=[];
- spans[0].text='CS102', locator.cell_ids=['t0-c9'];
- review_evidence_refs containing the applicable entry;
- **blockers=[] and review_view={clauses:[], relations:[]}**.

The independent expectation that this source/candidate mismatch must refuse or retain a blocker failed: **1 failed in21.28s, actual exit1**, log task3-spec-adversarial3.log. This removes a real printed prerequisite from the supported review representation. Records remain inactive and source states pending, limiting runtime impact; source integrity and semantic-repair blocking still fail. Require the bridge to refuse or block review-blank claims inconsistent with the exact raw owner and add this regression within the authorized change scope. No protected compiler edit is implied by this recommendation.

Two earlier diagnostic variants used blank_unreviewed and were refused by the checked loader's authority consistency check (1passed22.90s; instrumented retry1passed22.74s, actualexit0 each). The final reviewed_empty variant preserves those existing diagnostic counts and exposes the field-binding gap. Those preliminary refusals are not evidence against the confirmed final reproducer.

## Requirement coverage

| Requirement | Independent evidence/result |
|---|---|
| Checked prospectus-only API, exact selected register/source digest/version | load_candidate_bundle and bridge inspected directly; producer/bundle/compiler focused suites pass; policy/private/raw misuse cases pass |
| Reuse existing parser ownership instead of competing parser | inspected _owners, parse_curriculum_evidence, FieldCandidate/CourseCandidate, layout/evidence/loader and _candidate_to_raw_course interactions; satisfied |
| Exact individual owned field cells, source text, page, native origin and captured geometry | source spans use raw cells and captured pdf_page_sizes, SourceSpan parses/checks binding; TOPLEFT/BOTTOMLEFT and malformed/foreign binding tests pass |
| Missing/ambiguous/unlocatable/derived/semantic-repair evidence remains blocked | supplied missing/overlap/repair tests pass, derived/default splits stay unsupported; **reviewed-empty source mismatch fails T3-S1** |
| XX999 retained and unresolved | actual combined synthetic E2E retains raw XX999, exact t0-c13 span and unresolved_reference blocker |
| Applicable existing ledger, no counts/status inferred, no authority promotion | ordinary producer emits no entries; blank stays blank_unreviewed; valid/foreign/stale/edited-ledger cases pass; **raw blank correspondence is incomplete T3-S1** |
| Captured correction decisions/raw text retained | bridge leaves checked payload/conversion unchanged; documentation distinguishes retained captured input from compiler output refs; corrections are not materialized |
| Inactive pure compiler artifact, no publication/network/runtime | actual E2E input/bundle byte checks and forbidden-operation test pass; source inspection finds no writing/execution in bridge |
| Documented external-bundle command | import/function signature and JSON artifact agree with actual API; documented E:/external path is an illustrative placeholder, not a real corpus run |
| Exact allowed scope | three-path Git diff; no extractor/contracts/runtime source changes |

## Independent tests and exact commands

Full focused run: **242 passed in44.92s, actual exit0**, including all36 new handoff cases and actual `test_combined_synthetic_conversion_bundle_bridge_compiler`. Log: task3-spec-focused.log. Before pytest, system py -3.13 -B imported bridge/producer/bundle/compiler and asserted each __file__ resolves beneath the frozen archive. All four assertions passed. PYTHONPATH was only the absolute archive; cwd was archive to avoid owner/source import precedence. No broad4k/corpus suite ran.

```powershell
Set-Location -LiteralPath 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'
$env:PYTHONPATH='E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-3-review-12d5e373\candidate'
$env:PYTHONDONTWRITEBYTECODE='1'; $env:HF_HUB_OFFLINE='1'; $env:TRANSFORMERS_OFFLINE='1'; $env:HF_DATASETS_OFFLINE='1'
Set-Location -LiteralPath $env:PYTHONPATH
py -3.13 -B -m pytest 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-3-review-12d5e373\candidate\tests\test_prospectus_rule_handoff.py' 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-3-review-12d5e373\candidate\tests\test_prospectus_ingestion.py' 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-3-review-12d5e373\candidate\tests\test_candidate_bundle.py' 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-3-review-12d5e373\candidate\tests\test_rule_candidates.py' -q -p no:cacheprovider --rootdir 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-3-review-12d5e373\candidate' --confcutdir 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-3-review-12d5e373\candidate' --basetemp 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\task3-spec-pytest-20261011-1240' 2>&1 | Tee-Object -FilePath 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\task3-spec-focused.log'
$task3SpecExit=$LASTEXITCODE
Set-Location -LiteralPath 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'
Write-Output "ACTUAL_PYTEST_EXIT=$task3SpecExit"
exit $task3SpecExit
```

Final independent reproducer run (archive bridge origin assertion also passed immediately before pytest):

```powershell
Set-Location -LiteralPath 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'
$env:PYTHONPATH='E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-3-review-12d5e373\candidate'
$env:PYTHONDONTWRITEBYTECODE='1'; $env:HF_HUB_OFFLINE='1'; $env:TRANSFORMERS_OFFLINE='1'; $env:HF_DATASETS_OFFLINE='1'
Set-Location -LiteralPath $env:PYTHONPATH
py -3.13 -B -m pytest 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\task3-spec-adversarial.py' -q -s -p no:cacheprovider --rootdir 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-3-review-12d5e373\candidate' --confcutdir 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\unified-task-3-review-12d5e373\candidate' --basetemp 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\task3-spec-adversarial-temp3-20261011-1252' 2>&1 | Tee-Object -FilePath 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\delivery_execution_20261011\task3-spec-adversarial3.log'
$task3SpecExit=$LASTEXITCODE
Set-Location -LiteralPath 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'
Write-Output "ACTUAL_ADVERSARIAL_EXIT=$task3SpecExit"
exit $task3SpecExit
```

Diagnostic exact pytest invocations used the same prefix/root/confcutdir/no-cache flags and external script, with --basetemp task3-spec-adversarial-temp-20261011-1250 and task3-spec-adversarial-temp2-20261011-1251 respectively (absolute under D); logs task3-spec-adversarial.log and task3-spec-adversarial2.log. The second run added printed refusal diagnostics, the third changed only candidate state from blank_unreviewed to reviewed_empty. The saved script is the final failing variant.

## Preservation and review boundary

Read COMPLETE review-common/scope/brief/report, shared SPEC+IMPLEMENTATION_PLAN, Phase6 SPEC, owner extractor-reviewer and spec-reviewer-prompt as Markdown; actual patch, three changed files and interacting ownership/bundle/compiler/contracts/ledger helpers inspected. Reports were not accepted as test proof. No descendants or Claude invocation.

Pre/post evidence: task3-spec-preflight.json and task3-spec-postflight.json. **Exact378 actual files, every manifest SHA256, no symlinks/junctions, package manifest/patch/stat unchanged before and after.** Archive content matches all378 HEAD Git blobs after CRLF/LF normalization; archive is CRLF for the sampled bridge while Git blob is LF. Raw worktree bytes separately snapshotted and unchanged. Two initial stricter raw-byte comparison probes failed on expected line-ending differences; no source/archive edit was made. HEAD unchanged12d5e373, clean status, index SHA256 unchanged; git diff --check exact range exit0.

READ_ONLY_CODEX_USAGE.ps1 read fully then actual Codex app-server rateLimits queried:12:34:48 Manila44%primary/7%weekly;12:40:58 Manila52%primary/8%weekly. Both allowed continued work. Actual worktree restored after helper/test processes. System Python3.13-B, no-bytecode/offline/no-cache, unique absolute external basetemps; no dependency/config/interpreter changes.

Not verified: original corpus/OCR/real converter accuracy, human/domain/source approval, private lifecycle, full suite/mutation campaign, runtime/Janus/Prolog, embeddings/routing/API-Docker/release/institutional activation. Synthetic acceptance proves interface behavior only. Existing M1/F/session review scopes are not replayed or cleared by this review. Local unsigned manifest/ledger hashes provide consistency, not malicious-producer authenticity; T3-S1 is narrower: even retained untouched raw conversion contradicts the emitted blockerless semantics.

Skipped broader/runtime checks as dispatched; the remaining risk is the confirmed inactive-candidate source-binding defect. **FAIL — CHANGES NEEDED.**
