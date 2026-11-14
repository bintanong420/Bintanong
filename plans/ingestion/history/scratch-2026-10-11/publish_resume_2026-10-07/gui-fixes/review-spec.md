# Independent specification review

Range: `cf8b11c566d76bd5048a761a169907aee31a242b..8caa1eb7c8a226528db30d8bbc4534b2857625cb`, GUI worktree, 7 October 2026. Review is read-only except external evidence/report files and focused-test temporary files. Repository status remained clean.

## Specification

One confirmed missing requirement:

**P2 — PDF image requests fail without a visible, actionable failure message.** `backend/bintanong_tools/prospectus_review_gui/static/review.js:198` assigns `/api/page/{page}.png` directly to the image source. These GET requests bypass the shared `api` wrapper, and `renderPdf` registers neither an `error` listener nor `onerror`. If question JSON succeeds but the image request fails, the GUI retains an unhidden broken image, empty PDF note, and no status message. For ordinary course questions the same path also leaves source-cell overlays present despite unavailable source evidence. The user's requirement, "Handle failed requests visibly, preserve entered answers and describe lost responses as save status unknown," does not restrict failed GET requests to JSON endpoints.

Concrete reproduction: from any directory run:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
py -3.13 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\gui-fixes\review-spec-repro.py'
```

This executes actual `renderPdf` through the existing Node VM harness, registers an observable image-error event boundary, renders a valid section question, then dispatches the image error to any installed listener. Observed: `hasErrorHandler=False`, `imageHidden=False`, `pdfNote=''`, `status=''`; current question, choice, title and reason remain intact. The runnable assertion fails because no visible error exists. Equivalent browser steps, not executed here: block `/api/page/*.png`, then select a question whose JSON loads successfully; or disconnect the server before an uncached page image loads. No browser completion claim is made.

Smallest required correction: handle the image error where `renderPdf` sets the source, visibly explain that the PDF page failed to load with a manual recovery action, announce the error through the existing live region, avoid presenting highlights without the page, and preserve entered answers. No automatic retry is required or authorized by this finding.

The rest of the scoped requirements are satisfied by inspection and focused execution:

- Section confirmations expose valid PDF pages through existing geometry and intentionally empty boxes; section-specific alternative text avoids undefined course references.
- Prerequisite twin questions focus and scroll to the prerequisite cell; a missing prerequisite cell does not substitute the code cell.
- JSON GET failures are visible. Fetch rejection, malformed JSON, missing/null success envelopes, and POST 5xx produce actionable failure/unknown-status text. Committed-then-lost POST simulations make one request and retain current question, choice, edits and reason; confirmed validation errors retain the known rejection message. A failed queue refresh after save is not overwritten.
- Existing prerequisite No plus bulk Yes behavior remains unchanged and has regression coverage. Only a current hash-bound accepted originally blank prerequisite with a unique locator is stamped `reviewed_empty`; stale, foreign, corrected, unresolved, ambiguous and duplicate-locator cases remain excluded.
- Publication protections remain: captured PDF digest in markup; all prerequisite states reclassified with original ambiguity evidence; persisted unclaimed/anomaly completeness; authority rebuilt after accepted-blank stamping and always blocked for stale derived views; semantic bytes parsed and hashed from one capture with pre-publication change detection.
- Decision record accurately retains pending human trial/final closeout and distinguishes unavailable browser/Lighthouse gates. No unexpected scope addition was found.

## Evidence

Independently rerun command, from the GUI checkout:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
py -3.13 -m pytest tests/test_review_gui_client.py tests/test_review_gui_static.py tests/test_review_gui_api.py tests/test_review_gui_session.py tests/test_review_gui_prerequisites.py tests/test_prospectus_materialise.py tests/test_prospectus_ledger.py tests/test_prospectus_input_snapshot.py tests/test_prospectus_markup.py -q -p no:cacheprovider --basetemp 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\gui-fixes\gui-spec-parent\gui-spec-temp'
```

Actual result: **232 passed in 21.58 seconds, exit 0**, no skips. The image-failure reproducer is additional adversarial evidence, not part of those passing tests. No broad gate was rerun. Parent-reported full-suite/corpus numbers were not claimed as this reviewer's own execution.

`git diff --check` over the requested range exited 0. The independently checked merge-parent histories preserve every original line as an ordered subsequence: OCR plan 566/568 lines, GUI plan 490/492 lines, progress 880/826 lines for `cf8b11c`/`3227ac8`. All original test functions remain: ledger 14/14 and materialise 23/13. The supplied external original stage-2/stage-3 preservation report agrees.

## Behavior preservation and quality

No extractor split was performed in this range; generated-module/shim split checks are not applicable. The scoped merged publication protections and GUI semantics above remain intact. No raw PDFs, generated output artifacts or user `.gitignore` edits are included in the range. No code was changed in this review.

## Unverified concerns and remaining gates

No additional suspected defect is promoted to a finding. Browser, keyboard, Lighthouse and human trial remain NOT RUN/pending as explicitly recorded; the image failure is confirmed at the client error-event boundary, not through a browser screenshot. Linux/macOS remain untested. Tasks 12 and 13 are not closed by this technical review.

CHANGES NEEDED — P2 PDF image GET failure handling at `static/review.js:198`.
