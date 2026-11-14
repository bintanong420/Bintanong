# Spec review

Range: `5c34fd73adbd2806d6c48362eb248b74921fb79c...cf8b11c566d76bd5048a761a169907aee31a242b`. Spec = `plans/2026-10-05-prospectus-review-gui.md`; issue lookup skipped by owner instruction. Reviewed actual source, task-specific tests, frozen diff/commits, LATE instructions and gate JSON/log evidence. Integration HEAD/dev hashes and clean worktree independently read.

**Confirmed findings: 2 Medium; High: NONE.** Paths below are relative to `backend/bintanong_tools/prospectus_review_gui/`.

1. **Medium — section confirmation hides the PDF.** Task 8 requires **"PDF page (image plus overlay boxes, zoom control)"**; Task 5's no-highlight rule for section questions does not require hiding the image. `session.py:131` excludes section questions from page records; `static/review.js:168-174` then hides the image despite `question.pages=[1]` and `pdf.available=true`. Reproducer: `spec-section-pdf-probe.py` produces empty `boxes_page_keys` and `renderPdf_hides_image=true`. The probe uses an available-renderer stub and writes no session artifacts. Bulk confirmation loses its original-source pane.

2. **Medium — prerequisite question focuses the code cell in the twin.** Task 8 requires **"the asked cell is marked stronger"**. `static/review.js:206` always selects role `code`, including prerequisite questions; lines 212-215 mark and scroll that cell. Reproducer: `spec-twin-probe.cjs` executes the actual `renderTwin` function with code/prerequisite cells and kind `prerequisite`; both `asked` and `scrolled` equal `code-cell`. This violates field-specific source focus. No browser result is claimed.

**Separate Low spec ambiguity:** D11 says **"any current ledger line on any of their fields, whatever its disposition"** prevents bulk confirmation. `questions.py:158` excludes prerequisite decisions deliberately (progress line 829; prerequisite test). `spec-d11-probe.py`: prerequisite No followed by section Yes adds an accepted row for that course. It preserves the prerequisite decision; No still blocks full content review. Later Task 10 separates prerequisite/course review but does not explicitly amend D11. Record/resolve this wording with the owner; do not claim override or data loss.

Evidence supports recorded gates a-g: 1259/6; 266; 80/80; 44/44 with only package hash/run key changes; unchanged triage; trial checks 0; diff/trailers 0, dev unchanged, 107 original hashes unchanged. Shared builder, locks, immutable raw outputs, source/hash/stale filters, loopback/token/Host/Origin/CSP and accepted-blank stamping traced. Unrequested scope creep: NONE. No broad gates rerun. Browser/Lighthouse, human Task 12, Linux/macOS and institutional approval declined/unrun. No recheck: no High. Nothing here is institutional approval.

Probe outputs and exit codes: `spec-probe-evidence.md` in this directory. All three exited 0. Probe commands (run from this external scratch directory):

```powershell
& 'C:\Users\Hawksprey\source\repos\Bintanong\backend\.venv\Scripts\python.exe' -B .\spec-section-pdf-probe.py
node .\spec-twin-probe.cjs
& 'C:\Users\Hawksprey\source\repos\Bintanong\backend\.venv\Scripts\python.exe' -B .\spec-d11-probe.py
```

