# Fix round 1: visible PDF image request failures

Code frozen on 7 October 2026, Asia/Manila; exact boundary timestamp is in `checkpoint.json`. Worktree `C:\Users\Hawksprey\source\repos\Bintanong-wt\gui-fixes`; branch `feat/review-gui-fixes-20261007`; HEAD `8caa1eb7c8a226528db30d8bbc4534b2857625cb`. The starting tree was clean. No commit, staging, push, dev/main movement, installation, broad gate, agent delegation or published plan/document edit occurred. No implementer-owned Python/Node/server processes remain.

The independent Spec P2 was confirmed: PDF PNG requests use the native image source and bypass the JSON API. `renderPdf` now installs a native `onerror` handler before assigning the source. It hides the failed image, removes its overlays, and writes an actionable PDF-page message directing the reviewer to check the connection and use Zoom to load again. The PDF note has its own `aria-live="polite"` region; it does not overwrite the global status or answer alert, including existing save-status-unknown messages. Current question, choice, Other title and reason are untouched. There is no automatic retry. Each manual render clears the old handler first, so unavailable/no-page views detach it; manual Zoom reinstalls the source, overlays and a new handler for recovery.

Changed paths, all unstaged:

- `backend/bintanong_tools/prospectus_review_gui/static/review.js`: six lines for native error handling and detachment.
- `backend/bintanong_tools/prospectus_review_gui/static/index.html`: a separate live region on the PDF note.
- `tests/test_review_gui_client.py`: error-event regressions for course/section questions, retained answers/save uncertainty, no automatic retry, explicit Zoom recovery and unavailable/empty-view detachment; the existing DOM boundary gained its native `classList.toggle` behavior for Zoom.
- `tests/test_review_gui_static.py`: verifies the rendered HTML provides a separate PDF-note live region.

## Authentic verification

All commands ran from the GUI worktree with system Python, `PYTHONDONTWRITEBYTECODE=1`, `-q -p no:cacheprovider`, and external basetemp directories here. No new test dependency or framework was added; actual client functions execute through the existing Node VM harness.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
py -3.13 -m pytest tests/test_review_gui_client.py tests/test_review_gui_static.py -k 'pdf_image_failure or pdf_image_can_recover or pdf_error_handler or pdf_load_messages' -q -p no:cacheprovider --basetemp 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\gui-fixes\image-error\red-verified-temp'
```

`red-verified.log`: **4 failed, 2 passed, 49 deselected; exit 1**, before production edits. Failures showed the missing hide/overlay-clear behavior and missing PDF live region. The two empty/unavailable controls already passed because the baseline had no error handler to detach; they protect the new handler's lifecycle. An initial `red.log` had the same counts, but its recovery test also exposed a missing native `classList.toggle` in the controlled DOM. That harness boundary was corrected and the verified red rerun failed on the intended missing production behavior. Both logs are retained.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
py -3.13 -m pytest tests/test_review_gui_client.py tests/test_review_gui_static.py tests/test_review_gui_pages.py tests/test_review_gui_api.py tests/test_review_gui_session.py -q -p no:cacheprovider --basetemp 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\gui-fixes\image-error\green-temp'
```

`green.log`: **120 passed in 20.64 seconds; exit 0**. `git diff --check`: exit 0; only LF→CRLF advisory messages, recorded in `diff-check.log`.

Root owns full-suite/self-test/comparer/browser/Lighthouse and independent recheck gates. This batch contains no browser or human-trial verdict and closes no published plan. Next: root pins these four changed paths, runs the full gates and scoped Spec recheck, then commits explicit paths after gates. Do not repeat publication, original-copy, PR or dev actions; code is frozen and no further implementer edits are pending.
