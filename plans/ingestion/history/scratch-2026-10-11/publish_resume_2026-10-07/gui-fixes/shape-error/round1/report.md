# GUI response-shape scoped fix round1

Base: 6d8e81e9a83c65f5a92355de637e16112182ae46; worktree gui-fixes; branch feat/review-gui-fixes-20261007.
Requirement: shape-error/review-spec.md P2 nested text-coercion failures after current/view replacement. Reproduced actual reference/proposal/flag render consumers before production edits, including question.flags through the course-null fallback. Existing Fix old/new/note are strings (format_term returns string); flag field may be absent/null/string. Displayed reference values are printed strings/null/finite numbers; member courses are skipped by the display.

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
$roundScratch = 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\gui-fixes\shape-error\round1'
New-Item -ItemType Directory -Force -Path $roundScratch | Out-Null
py -3.13 -m pytest -q -p no:cacheprovider --basetemp "$roundScratch\red-temp" tests/test_review_gui_client.py -k 'nested_render or reference_primitives' *> "$roundScratch\red.log"
$testExit = $LASTEXITCODE
Set-Content -Encoding utf8 "$roundScratch\red.exit.txt" $testExit
```

Verified RED:14 failed,6 passed,119 deselected in1.90s; pytest exit1. No production edits preceded it. Malformed reference/proposal/flag values either throw during String/template rendering or mutate/clear question state instead of displaying recovery. Six supported primitive/proposal-copy controls pass. Successful fixture proposal.note corrected from null to actual server string. Test-only aliased flags copied separately so null question field and absent course field controls independently exercise both optional cases.

No broad gates, commits, staging, push, dependencies, agents or owner-checkout writes. Root owns broad gates/review/commit.

## Final result and exact GREEN commands

Production diff only extends existing predicates: optional flag.field must be absent/null/string; displayed reference values must be string/null/finite numeric; proposal old/new/note must be strings. The ignored courses member list is not coerced to text. Known consumer/server types are checked before current/view replacement, keeping the previous question, choice, reason and correction intact on malformed GET responses. No generic schema, source/ledger edits, auto retry or new dependency.

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
py -3.13 -m pytest -q -p no:cacheprovider --basetemp "$roundScratch\green-temp" tests/test_review_gui_client.py tests/test_review_gui_api.py *> "$roundScratch\green.log"
$testExit = $LASTEXITCODE
Set-Content -Encoding utf8 "$roundScratch\green.exit.txt" $testExit
py -3.13 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\gui-fixes\shape-error\server-shapes.py' $roundScratch *> "$roundScratch\server-shapes.log"
$checkExit = $LASTEXITCODE
Set-Content -Encoding utf8 "$roundScratch\server-shapes.exit.txt" $checkExit
# First server run passed all shape/consumer assertions but scratch deletion failed, exit1.
# Preserve that output, then rerun the same unchanged probe:
Move-Item -LiteralPath "$roundScratch\server-shapes.log" -Destination "$roundScratch\server-shapes-cleanup-failure.log"
py -3.13 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\gui-fixes\shape-error\server-shapes.py' $roundScratch *> "$roundScratch\server-shapes.log"
$checkExit = $LASTEXITCODE
Set-Content -Encoding utf8 "$roundScratch\server-shapes.exit.txt" $checkExit
 git diff --check
```

Observed results:
- Verified RED14failed6passed119deselected in1.90s; pytest exit1, before production edits.
- GREEN166passed in17.67s; pytest exit0.
- Actual ReviewSession/FastAPI/Node client probe:16 real generated response bodies accepted, actual startup/question/save/materialise consumers complete, no answer error; final exit0.
- First actual-server probe passed application assertions, then external TemporaryDirectory cleanup hit WinError32 on decision_ledger.jsonl.lock; retained server-shapes-cleanup-failure.log. An unchanged probe rerun completed with exit0. No application code changed to bypass cleanup.
- git diff --check exit0; only checkout LF-to-CRLF notices.

Frozen files:
1. backend/bintanong_tools/prospectus_review_gui/static/review.js
2. tests/test_review_gui_client.py
3. docs/decisions/prospectus-review-gui.md
4. plans/plan_current_progress/extractor_split_progress.md

No staging/commit/push/broad gates/dependencies/agents/owner-checkout edits. HEAD6d8e81e9a83c65f5a92355de637e16112182ae46 remains unchanged. Root runs broad gates, commits and scoped Spec/Standards rechecks.

Limitations: type/shape validation protects the rendering contract, while source accuracy/correction rules remain the original documents and server/ledger responsibility. Browser/accessibility/human trial/Linux/macOS were not run here. No GUI Task12/13 closeout or institutional approval claim.
Frozen Manila timestamp: 2026-10-07T18:34:49.4153963+08:00
