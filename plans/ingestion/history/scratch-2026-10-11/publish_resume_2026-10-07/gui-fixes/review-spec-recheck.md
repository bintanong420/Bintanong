# Scoped independent specification recheck

Range: `8caa1eb7c8a226528db30d8bbc4534b2857625cb..41fe3c3241c7fdbbab66e50d805454488fbac656`, GUI worktree, 7 October 2026. Scope is only the previously confirmed P2 PDF image GET failure and adjacent lifecycle/answer preservation. No broad review or broad gate was performed. Repository status is clean; no tracked files were edited.

## Specification and confirmed P2 closure

APPROVED/NONE. The original defect is resolved.

`renderPdf` installs the native `onerror` handler before assigning `img.src`. A failed PDF image request hides the image, clears all overlays, and writes a page-specific message with a manual recovery action (check connection, then use Zoom). The PDF note is an independent `aria-live="polite"` region. It leaves current question, selected answer, edits, reason, global status and answer alert intact, including save-status-unknown text. No automatic retry is introduced.

Each render clears the previous handler first. No-PDF/no-page views remove the source, hide the image, clear overlays and detach the error handler. Manual Zoom sets a new source and handler and restores normal image/overlay rendering. The actual-client error-event tests cover both course and section questions.

## Independently executed evidence

1. The original `review-spec-repro.py` was rerun without modification:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
py -3.13 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\gui-fixes\review-spec-repro.py'
```

**Exit 0.** Observed `hasErrorHandler=True`, `imageHidden=True`, actionable `pdfNote='PDF page 1 could not be loaded. Check the connection, then use Zoom to load the page again.'`. Current question, Other choice, reviewer title and reason all match their entered values. The original failing assertion now passes.

2. New image failure/live-region/lifecycle tests plus adjacent lost-response preservation tests were rerun from the GUI checkout:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
py -3.13 -m pytest tests/test_review_gui_client.py tests/test_review_gui_static.py -k 'pdf_image_failure or pdf_image_can_recover or pdf_error_handler or pdf_load_messages or response_loss' -q -p no:cacheprovider --basetemp 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\gui-fixes\spec-image-recheck-temp'
```

**16 passed, 39 deselected in 0.99 seconds, exit 0.** The six new cases cover course/section image failure, manual Zoom recovery, no-PDF/no-page handler detachment and a separate accessible PDF failure announcement. Ten adjacent tests cover committed-then-lost answer/materialisation responses, retained entered answers and no automatic retry.

3. `git diff --check 8caa1eb7c8a226528db30d8bbc4534b2857625cb 41fe3c3241c7fdbbab66e50d805454488fbac656`: exit 0. Checkout status remains clean.

The supplied image-error implementer report was read. Its red/focused counts and root full-suite/self-test counts are parent/implementer evidence, not independently rerun here. Browser/Lighthouse and human trial remain unexecuted/pending; client error-event execution does not claim browser screenshots or a human verdict. No residual defect was confirmed within this scoped recheck.

APPROVED/NONE
