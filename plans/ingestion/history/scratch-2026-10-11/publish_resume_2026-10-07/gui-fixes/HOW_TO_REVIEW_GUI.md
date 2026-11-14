# Review the prospectus with the local GUI

Prepared for Task 12; the human verdict is pending. Start after the controller finishes the browser/accessibility and final technical gates. This example uses the existing scratch Phase C BSBA-HRM extraction, which has real prerequisite questions. The original PDFs and original review folders remain the accuracy reference; use a new review directory for this trial.

From PowerShell:

```powershell
Set-Location 'C:\Users\Hawksprey\source\repos\Bintanong-wt\gui-fixes'
$env:PYTHONDONTWRITEBYTECODE = '1'
$trial = 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\gui_e2e_0710'
py -3.13 -m backend.bintanong_tools.prospectus_review `
  --candidate "$trial\fresh\16_BSBA-HRM\BSBA-HRM_fresh_prospectus.json" `
  --pdf "$trial\copies\16_BSBA-HRM\BSBA-HRM-for-student-new-version.pdf" `
  --docling-json "$trial\fresh\16_BSBA-HRM\BSBA-HRM-for-student-new-version_docling.json" `
  --review-dir 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\gui-fixes\human-trial\16_BSBA-HRM' `
  --reviewer 'Your name'
```

The browser opens the local address printed in the terminal. Compare the PDF, reconstructed table and JSON. **Yes** accepts the extraction; **No** records uncertainty with your reason; **Other** records your typed correction with a reason. No answer is selected automatically. Course Other accepts text, a readable year/semester or whole-number units; server validation explains rejected values. Prerequisite Other accepts text or an empty value. Accept a blank prerequisite only after checking the source; it becomes `reviewed_empty` when the corrected candidate is written.

Keys: **Y/N/O** choose, **Enter** saves, **Esc** leaves Other, **J/K** or **Down/Up** move, **1–9** copy a proposal, **Z** zooms the PDF, **/** filters, **?** opens help. Typing inside a field does not answer questions. Clean sections have a bulk Yes/No question; earlier course decisions are retained. Prerequisite No remains unresolved even after bulk Yes and holds content review at `partially_reviewed`.

Answers append to `decision_ledger.jsonl` in the review directory above. **Write corrected candidate** creates `corrected_candidate.json` there. The original candidate and PDF are read only. A reviewed prospectus is not an approved curriculum; the corrected file does not authorize eligibility execution.

If Save says **status unknown**, keep your entered answer. The server may have saved it. Check the connection and inspect the ledger before submitting again; there is no automatic retry. Load failures are shown on the page. Stop with **Ctrl+C** in PowerShell, then close the tab. Restarting with the same review directory resumes the ledger.

For the four-candidate trial, the controller supplies separate scratch Phase C candidate/PDF paths for `01_Architecture`, `13_BSE-Innovation-and-Tech`, `16_BSBA-HRM` and `33_BSCS-2025-2026`; do not invent prerequisite questions or reuse scripted-answer ledgers. Review a few questions in each and the same rows in one review sheet. Record whether the GUI finds the sheet's problems, whether highlights and twin focus match the printed cell, whether wording is clear, and what feels slow or irritating. Report the verdict to the controller; this guide contains no human result.
