# GUI response-shape fix evidence

Base: 41fe3c3241c7fdbbab66e50d805454488fbac656, branch feat/review-gui-fixes-20261007.
Worktree: C:\Users\Hawksprey\source\repos\Bintanong-wt\gui-fixes.
Finding: successful HTTP/JSON responses with present but invalid nested values escape api(); answer falsely says Saved before renderState throws; queue failure stays invisible.

## Verified RED

Production review.js is unchanged at the base during this run. Tests execute the actual client under the existing Node stdlib VM harness. The DOM double gained its real addEventListener operation to allow valid question/queue rendering. Successful fixtures now match actual consumer/server shapes.

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
$shapeScratch = 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\gui-fixes\shape-error'
py -3.13 -m pytest -q -p no:cacheprovider --basetemp "$shapeScratch\red-temp" tests/test_review_gui_client.py -k 'present_but_invalid or consumer_shaped' *> "$shapeScratch\red.log"
$testExit = $LASTEXITCODE
```

54 failed, 2 passed, 42 deselected in 4.61s. pytest exit 1. Full output: red.log.
All 54 bad-shape cases fail because the existing response boundary accepts unusable values; the two genuine successful response/fallback cases pass. No test errors or dependency failure.

Plan path correction: the split plan exists as plans/2026-10-03-prospectus-extractor-package-split.md, not the dispatch's older date. Its cross-phase source-hash owner/schema/newline/full-green rules are unchanged. This task does not commit; root owns broad gates and any commit.

## Adjacent non-success envelope RED — 2026-10-07T18:20:23.1877828+08:00

Root independently confirmed400{errors:1} escapes the same shared response boundary and crashes errors.join. Added tests before changing error-envelope guard. Initial error-red.log had18failed3passed98deselected because the JSON arrow fixture lacked object parentheses; that initial run is not claimed as evidence. Corrected fixture, verified error-red-verified.log:12failed9passed98deselected in1.41s, pytestexit1. All12POST bad-envelopes fail as expected;6GET recovery cases and3valid4xx controls pass. First successful guard focusedgreen:125passed in8.55s pytestexit0 (green-verified.log).

Real-server initial probe server-shapes.log failed with Windows command-line length WinError206; no application-shape rejection was observed. Fix probe transport by reading scenario from an external file, retaining initial log. No production change for that probe failure.

## GREEN and frozen handoff

Production change: native typed predicates at the shared response boundary validate only the consumer-required state, question, queue, twin and write-result shapes. Failed error envelopes must provide string error and/or string-array errors before the caller uses them. This prevents false success announcements, exceptions after state replacement and error-array join failures. Existing recovery messages, no automatic retry, entered answers, current question, source authority, blank prerequisite acceptance and bulk/prerequisite behavior are preserved. No dependency or general schema framework added.

Exact remaining commands (same worktree and external scratch variable as RED):

```powershell
# Followup initial fixture run: not claimed as an authentic red
py -3.13 -m pytest -q -p no:cacheprovider --basetemp "$shapeScratch\error-red-temp" tests/test_review_gui_client.py -k 'error_envelopes' *> "$shapeScratch\error-red.log"
# Verified followup RED, before production error-envelope guard
py -3.13 -m pytest -q -p no:cacheprovider --basetemp "$shapeScratch\error-red-verified-temp" tests/test_review_gui_client.py -k 'error_envelopes' *> "$shapeScratch\error-red-verified.log"
# First success-shape GREEN: client only
py -3.13 -m pytest -q -p no:cacheprovider --basetemp "$shapeScratch\green-temp" tests/test_review_gui_client.py *> "$shapeScratch\green.log"
# Success-shape verified GREEN: client + API
py -3.13 -m pytest -q -p no:cacheprovider --basetemp "$shapeScratch\green-verified-temp" tests/test_review_gui_client.py tests/test_review_gui_api.py *> "$shapeScratch\green-verified.log"
# Final GREEN after malformed error-envelope guard
py -3.13 -m pytest -q -p no:cacheprovider --basetemp "$shapeScratch\final-green-temp" tests/test_review_gui_client.py tests/test_review_gui_api.py *> "$shapeScratch\final-green.log"
$testExit = $LASTEXITCODE
Set-Content -Encoding utf8 "$shapeScratch\final-green.exit.txt" $testExit
# Actual ReviewSession/FastAPI response consumption through actual Node VM client
py -3.13 "$shapeScratch\server-shapes.py" "$shapeScratch" *> "$shapeScratch\server-shapes.log"
$checkExit = $LASTEXITCODE
Set-Content -Encoding utf8 "$shapeScratch\server-shapes.exit.txt" $checkExit
# Diff hygiene
 git diff --check
```

Results:
- Verified RED: 54 failed, 2 passed, 42 deselected in 4.61s; pytest exit 1.
- Initial success-shape GREEN: 98 passed in 5.94s; log complete but PTY exit was not captured, so not used as the final green claim.
- Verified success-shape GREEN: 125 passed in 8.55s; pytest exit 0.
- Followup verified error-envelope RED: 12 failed, 9 passed, 98 deselected in 1.41s; pytest exit 1.
- Final GREEN: 146 passed in 8.44s; pytest exit 0.
- Actual server-shape control: 16 response bodies from a real synthetic ReviewSession and FastAPI TestClient, all accepted by responseShape, actual start/question/save/materialise consumers complete with no errors; exit 0. Includes real course/unclaimed/section shapes and unavailable-twin fallback. server-shapes.py is a repeatable external probe, server-shapes.log its output. Synthetic provenance is not a source-accuracy gate.
- git diff --check exit 0; Git emits only existing checkout LF-to-CRLF normalization warnings.

Frozen worktree files:
1. backend/bintanong_tools/prospectus_review_gui/static/review.js
2. tests/test_review_gui_client.py
3. docs/decisions/prospectus-review-gui.md
4. plans/plan_current_progress/extractor_split_progress.md

No commit, staging, push, dependency installation, other agents, broad gates or owner-checkout writes. HEAD remains 41fe3c3241c7fdbbab66e50d805454488fbac656. Root owns full-suite/self-test/corpus gates, independent Spec/Standards rechecks and commit.

Risks/limits: these predicates defend render/write response contracts; source correctness and correction validation remain with the server/ledger and original documents. Browser/accessibility/human trial/Linux/macOS were not run for this task. A malformed POST may already have committed, so recovery intentionally reports unknown and requires manual ledger/file inspection before another submission. Tasks12/13 and institutional approval remain uncompleted.
Frozen Manila timestamp: 2026-10-07T18:22:12.4392448+08:00
