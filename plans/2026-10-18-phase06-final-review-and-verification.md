# Phase06 final CSV review and verification procedure

Current18October2026 at product49bc993. This is the concrete closing procedure,
not a claim that pending review/institutional gates have passed.

## The requested Excel CSV

Ignored delivery:workspace/audit-evidence/p06-final-review-csv-20261018/
BSCS-generated-prerequisites-review.csv. Seven rows,15 columns, UTF8 BOM,
CRLF and quoted fields. Printed source line wraps are joined with spaces.
Compare Printed prerequisite with Generated prerequisite meaning. Enter matches,
mismatch or unsure in Your verdict and explain differences in Your notes; optional
Reviewer/Review date record attribution. Source images/page and exact generated
file/line remain at the right. CSV does not preserve workbook styling/dropdowns.

Earlier feedback is carried forward without changing the original reviewed CSV:
six rule rows reference its48 ok cases. The seventh, oldCS1/L, references H27-H32
and records the subsequent CC1/L confirmation/corrected results. Original no
verdicts are preserved as historical disagreements, not rewritten to ok.
New output-review cells stay blank; prior runtime review is not falsely labeled
as a new blanket approval of regenerated files. Technical categories are omitted.

source-bindings.json binds each row to exact record/source spans, image/PL/bundle
hashes and the earlier review's hash. The CSV is authored/import-checked with
Artifact Tool, independently checked with Python csv, and rendered for inspection.
All seven rows/source paths/PL lines, blank review fields, no formulas and exact
roundtrip checked. The renderer checks the working table; native Excel not opened.
Docs/phase554 passed/11 subtests13.15s; phase state validates and remains blocked.
Logs:delivery root/docs.log. No actual curriculum execution was repeated solely
for this CSV export; the identity-aware73-case acceptance remains its named evidence.

## Construct the final verification record

Owner follow-up requests runtime cases limited to corrections and skipped rows.
Separate CSV:workspace/audit-evidence/p06-runtime-followup-csv-20261018/
BSCS-runtime-corrections-and-skipped-review.csv. Exactly25 rows:H27-H42/H65-H73;
six correctedCS1/L and19 previously skipped, excluding all48 ok cases.
Each row explains meaning, actual input, expected/observed result, why, and what
to check. Prior verdict/notes remain verbatim; new verdict/notes stay blank.
Unknown-course displays course-unknown, not the misleading CC5/L base label.
Repeat/timeout rows identify developer assertions and the limits of a single CSV
observation. Existing identity-aware results are exported; no fresh runtime run.
Artifact Tool/Python verify exact selection/annotations, UTF8 BOM/CRLF/roundtrip,
no formulas and original file preservation. Rendered corrected/skipped samples checked.
Follow-up docs/phase554 passed/11 subtests27.24s; phase state valid/blocked.

1. **Record the human result.** Preserve the returned reviewer copy. Match stable
   IDs to this delivery and compare non-review cells; record the actual answers
   with the exact CSV/bundle hashes. Reuse the48 accepted cases and the recorded
   CC1/L decision. A mismatch changes authoring only when supported by actual
   source evidence/decision; regenerate and rerun affected cases. Never edit PL
   independently or convert unsure/blank into approval.
2. **Prove the current pipeline.** Copy the existing identity-aware verifier into
   a new ignored evidence folder. Rebuild authoring/PL/runtime bundles, preserve
   originals and run the73 actual BSCS cases, four concurrent checks,39 spans,
   repeat equality and timeout recovery. Use fictional completion facts only.
3. **Run relevant regressions and phase checks.** Use the command sequence below;
   save exit codes/logs. Do not reuse a historical passing log as a fresh exit run.
4. **Account for release gates.** Record actual source-authority/approval and
   governed institutional runtime evidence if available. The current actual-data
   runtime is research-only. Do not fabricate those prerequisites or activate
   sources merely because developer tests and human output review pass.
5. **Write the final handoff.** Include supported scope, actual review decisions,
   commit/tool versions, source/PL/bundle hashes, exact commands/results, limits,
   known failures and next-phase prerequisites. If applicable gates pass, mark
   the handoff complete, supersede the checkpoint and update INDEX. Otherwise
   retain a blocked handoff with the exact missing evidence/recovery condition.
   Run validate and can-advance after those updates; advance only if permitted.

The existing blocked recovery condition remains authoritative. An offline-only
software milestone while institutional gates remain pending requires an explicit
recorded scope/exit decision; the developer cannot silently substitute that scope.

## Reusable commands after review reconciliation

From the active p06 worktree, run in PowerShell. The new folder prevents replacing
earlier sealed deliveries. No dependency install or product service is needed.

```powershell
$phase06ExitEvidence = Join-Path 'C:/Coding-projects/bintanong_workspace/audit-evidence' ('p06-final-check-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $phase06ExitEvidence -ErrorAction Stop | Out-Null
Set-Content -LiteralPath (Join-Path $phase06ExitEvidence '.gitignore') -Value '*' -Encoding utf8
$env:TEMP = $phase06ExitEvidence
$env:TMP = $phase06ExitEvidence
Copy-Item -LiteralPath 'C:/Coding-projects/bintanong_workspace/audit-evidence/p06-cc1-identity-20261018/verify_identity.py' -Destination (Join-Path $phase06ExitEvidence 'verify_identity.py')
py -3.13 -B (Join-Path $phase06ExitEvidence 'verify_identity.py') 'C:/Coding-projects/bintanong_workspace/worktrees/Bintanong/p06' *> (Join-Path $phase06ExitEvidence 'pipeline.log')
if ($LASTEXITCODE -ne 0) { throw 'Pipeline verification failed; inspect pipeline.log' }
$phase06Tests = @(
  'tests/test_symbolic_offline_research.py', 'tests/test_symbolic_runtime_bundle.py',
  'tests/test_symbolic_runtime.py', 'tests/test_symbolic_queries.py',
  'tests/test_symbolic_review_bundle.py', 'tests/test_symbolic_compiler.py',
  'tests/test_symbolic_authoring.py', 'tests/test_contracts_symbolic.py',
  'tests/test_contracts_answer.py', 'tests/test_contracts_runtime.py',
  'tests/test_contracts_runtime_fix2.py', 'tests/test_contracts_fix3_runtime.py',
  'tests/test_contracts_adversarial.py', 'tests/test_rule_candidates.py',
  'tests/test_prospectus_rule_handoff.py', 'tests/test_docs_hygiene.py',
  '.agents/skills/bintanong-phase-handoff/tests/test_phase_state.py'
)
py -3.13 -B -m pytest -q -p no:cacheprovider @phase06Tests --basetemp="$phase06ExitEvidence/pytest-temp" *> (Join-Path $phase06ExitEvidence 'regressions.log')
if ($LASTEXITCODE -ne 0) { throw 'Regression verification failed; inspect regressions.log' }
py -3.13 -B .agents/skills/bintanong-phase-handoff/scripts/phase_state.py validate --repo .
py -3.13 -B .agents/skills/bintanong-phase-handoff/scripts/phase_state.py can-advance --repo .
```

These closing command lines are prepared, not claimed executed in this CSV task.
The verifier currently reproduces the confirmed CC1/L bundle. If review changes
authoring again, update its input binding/independent expectations before using it
as the final run. Full-prospectus extraction defects/two historical system Docling
failures remain disclosed separately; this does not claim the entire project green.
