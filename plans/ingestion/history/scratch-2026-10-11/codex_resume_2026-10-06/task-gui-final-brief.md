# Exact task brief from C:\Users\Hawksprey\source\repos\Bintanong-wt\gui\plans\2026-10-05-prospectus-review-gui.md

Read approved_execution.md and preflight-ledger.md first. They supersede obsolete base/merge/dev/version/path snippets in this preserved historical plan. Do not edit the original plan. Preserve original task requirements below unless an approved ruling supersedes them.

### Task 10: Phase C hooks: the three states, prerequisite questions, `reviewed_empty`

**Confirmed by the user (5 October 2026):** the reviewer answers "Yes, no prerequisite" on a blank cell; that writes an `accepted` `prerequisites_raw` entry and `materialise` stamps `reviewed_empty`; the small `ledger.py` edit happens after Phase C merges.`n`n**Depends on Phase C being merged.** If Task 1 found it is not, stop here and report; Tasks 1 to 9 stand alone.

**Files:**
- Modify: `prospectus_review_gui/questions.py` (kind `prerequisite`), `session.py` (live `content_review`), `static/review.js` (state badges)
- Modify: `prospectus_extractor/ledger.py` (`materialise`: stamp the state)
- Test: `tests/test_review_gui_prerequisites.py`, additions to `tests/test_prospectus_materialise.py`

Behavior. For each course whose C `prerequisite_state` is `blank_unreviewed`, `unreadable`, `unresolved_reference` or `alternative_or_exception`, the queue offers a prerequisite question: for a blank cell, "Is it right that *<title>* (*<code>*) has no prerequisite?"; otherwise, "Is the prerequisite *<raw text>* of *<title>* correct?". **Yes** writes an `accepted` entry on field `prerequisites_raw` (old value equal to new value); **Other** writes a `corrected` entry with the typed text (empty text allowed: `correction_problem` accepts the empty string, "none"); **No** writes `unresolved`. `materialise` then marks a course whose latest applicable `prerequisites_raw` entry is `accepted` on a blank value as `prerequisite_state = reviewed_empty` (the only writer of that state, as C reserved), and re-runs C's state annotation after applying corrections. `content_review_state` is unchanged: it still asks only for the three course fields, so prerequisite review never blocks `reviewed`, but the corrected candidate and the GUI show it. The header shows the three states from C (extraction audit, content review computed live from the ledger instead of the payload's `pending`, source verification), each with its word, and the line "A reviewed prospectus is not an approved curriculum".

- [ ] **Step 1: Write the failing tests.**
  - `test_blank_prerequisite_course_gets_a_prerequisite_question_with_the_no_prerequisite_wording`.
  - `test_resolved_prerequisite_gets_no_question`.
  - `test_yes_on_blank_prerequisite_writes_accepted_prerequisites_raw_entry`.
  - `test_other_on_prerequisite_accepts_text_and_empty_text_but_not_a_number`.
  - `test_materialise_stamps_reviewed_empty_only_for_an_accepted_blank` (and not for a corrected or unresolved one, not for a stale entry, not for another PDF).
  - `test_materialise_rerun_is_deterministic_with_prerequisite_entries` (same input, same bytes).
  - `test_extractor_never_emits_reviewed_empty` (C's invariant still holds: only `materialise` writes it).
  - `test_state_badges_come_from_the_ledger_not_the_payload` (payload says `content_review: pending`; after the entries it says `partially_reviewed` or `reviewed` in `/api/state`, and the payload file is unchanged).
  - `test_eligibility_stays_blocked_until_the_blank_is_reviewed` (a corrected candidate with an unreviewed blank keeps C's blocked status; with the accepted entry, `reviewed_empty` is executable per C's D2 vocabulary).
- [ ] **Step 2 to 5: red, minimum, green, full suite and self-test 80/80.**
- [ ] **Step 6: Commit** `feat: ask prerequisite questions and record reviewed_empty through the ledger`; progress entry.

---



### Task 11: End to end and the real-data gate (4 trial prospectuses, read-only)

**Files:**
- Create: `scripts/prospectus_review_gui_smoke.py` (drives the app with `TestClient` through the same questions a reviewer would see; prints counts; no UI)
- Test: `tests/test_review_gui_e2e.py` (synthetic, always runs)

- [ ] **Step 1: Write the end-to-end tests** (synthetic candidate and PDF from the fixtures; skipped never):
  - `test_full_session_synthetic` (open, fetch the queue, answer every question with a mix of Yes, Other, No, bulk confirm; materialise; `content_review_state` equals the expected counts; raw candidate hash unchanged).
  - `test_session_survives_restart` (answer, drop the session, open a new one on the same ledger: the same questions are decided).
  - `test_resume_after_candidate_rerun_marks_old_entries_stale` (change a course title in a copy of the candidate; old entries show as stale in `/api/state` and the course is back in the queue).
  - `test_gui_and_sheet_ledgers_agree_on_content_review_state` (the same decisions entered by sheet and by GUI give the same `content_review_state`).
- [ ] **Step 2: Run to verify red, implement the smoke script, green.**
- [ ] **Step 3: Real-data run on copies.** In `$SCRATCH`, copy each of the four trial folders **without** the `review\` sub-folder (`Copy-Item` the PDF and the `_prospectus.json`; leave the originals untouched). Run the smoke script for each against the copies, with `--review-dir` under `$SCRATCH`, answering by a fixed script: bulk Yes on every clean section, Yes on a sample of 10 rows, Other with a proposal value on 3 rows, No with a reason on 2 rows, Yes and No on 2 unclaimed codes where they exist; then materialise. Expected facts, to be recorded with the real numbers in the progress file (the numbers below are what B2 recorded for the sheet path and must match in kind; if they differ, find out why before going on):
  - `16_BSBA-HRM`: 8 sections (7 clean, 1 review); the bulk question exists for the 7 clean sections and not for the review one.
  - `01_Architecture`: 10 sections (1 clean, 8 review, 1 broken); the attention queue starts with the broken section; rows with `title_from_pdf` proposals show a proposal and no pre-selected answer.
  - `33_BSCS-2025-2026`: the `SU` section lists footnote codes; an unclaimed question refuses Other and needs a reason for Yes.
  - `13_BSE-Innovation-and-Tech`: broken; the queue is dominated by unclaimed codes; nothing offers to fix it; every question can still be answered `unresolved`.
- [ ] **Step 4: Prove nothing was touched.** SHA-256 of every original PDF and `_prospectus.json` in `$TRIAL` equals the values recorded in Task 1; the original `review\` folders in `$TRIAL` are byte-identical to before (hash their files in Task 1 as well); the only new files are under `$SCRATCH` (`decision_ledger.jsonl` and `corrected_candidate.json` per prospectus).
- [ ] **Step 5: Equivalence on real data.** For one prospectus (BSBA-HRM), enter 6 decisions through the GUI session and the same 6 through an edited sheet and `fixer_cli apply` into two separate ledgers; the two ledgers differ only in `via` and `entry_id`; `materialise` on both produces corrected candidates equal under the Task 4 comparison.
- [ ] **Step 6: Browser pass on one real prospectus** (BSBA-HRM, which has the Docling JSON if Task 1 step 6 found it; otherwise Architecture, otherwise the twin-fallback path is what is exercised and the progress file says so): start the GUI on the scratch copy, open it, answer five questions by keyboard only, confirm that the PDF highlight sits on the asked cell (screenshot compared by eye, saved under `$SCRATCH`), that the twin scrolls to the same cell, that the JSON pane shows the same course, and that a page with a warning (rotated or mismatched size, if any real page has one) shows no box. Record console errors (expected: none).
- [ ] **Step 7: Accessibility pass** (see the section below): run the Lighthouse accessibility audit (Chrome DevTools tool) and the keyboard-only walk on the running page; fix any failure in Task 8's files with a test first.
- [ ] **Step 8: Commit** `test: end-to-end review session and real-data smoke script`; progress entry with the real counts, hashes and timing (BSBA-HRM first question under one second after start is the expectation to compare against, not a gate).

---



### Task 12: Trial review by the user (human gate, no code)

- [ ] **Step 1: Prepare.** Write a one-page `HOW_TO_REVIEW_GUI.md` into the user's trial folder outside Git (`$SCRATCH` copy, not the repository), next to the existing `HOW_TO_REVIEW.md`: the command, the three answers, the keys, what "Other" accepts, where the ledger is, that nothing is approved, how to stop. (This is the only documentation file in the plan; it lives outside the repository.)
- [ ] **Step 2: The user reviews** the four prospectuses with the GUI (a few rows each is enough) and the sheet for one of them, and says: does the GUI find the problems the sheet found, is the highlight on the right cell, are the question sentences clear, what is slow or irritating.
- [ ] **Step 3: Record the verdict** in the progress file. Findings that need code become new tasks with a test first; findings that are taste are listed under the hand-off's open items.

---



### Task 13: Decision record, final checks, Codex gate, hand-off

**Files:**
- Create: `docs/decisions/prospectus-review-gui.md`
- Modify: `plans/plan_current_progress/extractor_split_progress.md`

- [ ] **Step 1: Decision record**, in plain sentences, with the date and branch: the tech choice and why not Next.js or a desktop toolkit (D1); the dependency extra (D2); the question model and the Yes / No / Other mapping to ledger verbs (D4); the guarantee that GUI entries are produced by the sheet's own function and the test that proves it; the local-only hardening (D8); what the GUI does not do (no add-course, no approval, not the OCR photo review); the known limits below; and the measured real-data results from Task 11.
- [ ] **Step 2: Final checks.** Full suite green; self-test 80/80; `git diff dev --stat` shows only the files in the structure table; `rg -n "https?://" backend/bintanong_tools/prospectus_review_gui` finds only the allow-listed SVG namespace; no file under `backend/` or `docs/` contains a reviewer name or a title from a real ledger.
- [ ] **Step 3: Codex gate (read-only review).** Same pattern as B2: hand the diff `dev..feat/prospectus-review-gui` to Codex read-only with the claims: GUI answers are only written through `sheet.row_entries` and `ledger.append_entries`; nothing is written into a tracked path; loopback only with Host, Origin and token checks; no raw candidate or PDF is ever written; validation is the ledger's. Fix findings test first.
- [ ] **Step 4: Progress file and hand-off** (below). Commit `docs: record the review GUI decisions and close the phase`. Do not push; do not merge. Merging is the user's decision after the trial.

---

## Accessibility basics

These are requirements, each with a test in Task 8 or a step in Task 11, not aspirations.

1. **Everything works from the keyboard**, in a logical tab order: skip link, header controls, queue, question, answer options, Other form, panes' zoom controls. Single-key shortcuts never fire while a text field has focus and each is also a visible button.
2. **Visible focus** on every control (an outline of at least 2px, never removed without a replacement), and the focused queue item scrolls into view.
3. **Names and roles by native elements first.** Radio inputs in a `fieldset` with a `legend` for the answer, `label` on every field, buttons for actions, real headings and landmarks; ARIA only where a native element does not exist (the live regions).
4. **Status and errors are announced**: progress and "saved" in a polite live region; a rejected answer in a `role="alert"` message beside the field, linked with `aria-describedby`, and the field marked `aria-invalid`.
5. **Colour is never the only signal.** Health, severity, the three states and the highlight each carry a word or a different outline style; text contrast is at least 4.5:1 in the light and the dark scheme (parsed and tested).
6. **Zoom and reflow.** Text scales with the browser; at 200% zoom and at a narrow window the panes stack and nothing needs horizontal scrolling for the question and answer controls. The PDF image may scroll inside its pane.
7. **Motion.** No animation except the scroll-to-cell, which respects `prefers-reduced-motion`.
8. **The PDF image has a text alternative** (page number and the asked field) and the same information appears as text in the question, so the highlight is never the only way to know where to look. A reviewer who cannot see the image can still answer from the question and the JSON pane, and the twin pane is real HTML a screen reader can read cell by cell.

## Dependencies on B2 and Phase C

- **B2 (hard dependency).** The GUI is built on `verify.py`, `fixes.py`, `ledger.py`, `sheet.py` and `fixer_cli.py` as they stand at the B2 merge. If a B2 review fix changes a signature used here, Task 1 step 3 records it and the plan's names follow the code. B2's maintainer sheet stays: Task 2 proves its output is unchanged, and Task 4 proves GUI entries are identical in shape to sheet entries.
- **Phase C (hard dependency for Task 10 only).** Tasks 1 to 9 and 11 do not need C's new fields; they work on a v3.0 candidate. Task 10 needs C's `prerequisite_state`, its `reviewed_empty` reservation and its three payload states, and extends `materialise` (B2 code) once C is in `dev`. If C lands after this plan's other tasks, Task 10 is the only one that waits.
- **Ledger lock (Task 2A).** A change to B2's `ledger.py` and `fixer_cli.py` that benefits the sheet CLI too. It needs only B2 and can land before Phase C.`n- **Phase D to F.** None required. Phase D's safe-cache and Phase F's container/CLI work do not touch the GUI. If Phase E adds source locators for RAG, the GUI does not need them. If Phase F's container image is meant to run the GUI, that is a new decision (it would need a published port and a different bind address and is **out of scope** by D8).
- **Master plan.** Satisfies §7.1 step 7 (local researcher GUI; PDF page, reconstructed cells and extracted JSON together; accepted, corrected or unresolved decisions with reviewer, reason, source cell and page, PDF hash; raw extraction preserved; corrected candidate derived separately), §7.3 (deliverable: a local correction GUI, decision ledger and corrected candidate JSON), §4 last paragraph (local correction tooling in parallel with Phase 1; outputs remain candidates), §15 (kept separate from private-file review: no shared storage or code), §16.1 (required preparation tool, not a hosted dashboard) and §20 (no new top-level module is created in `backend/app/`; this lives with the tools).

## Known limits (state them in the decision record, do not hide them)

1. **The ledger lock is advisory and local.** Task 2A stops a second GUI or `fixer_cli apply` on the same ledger with a clear "in use by ..." error, and the OS releases it on a crash. It does not stop a text editor, and a ledger on a network share may not honour OS locks on every system (D13).
2. **The reviewer name is whatever `--reviewer` or `git config user.name` says.** No authentication. The `entry_id` hash catches accidental edits, not forgery (the ledger module says so too).
3. **No highlight on rotated pages or when sizes disagree** (by design, D9). If many real pages are rotated, a follow-up adds rotation handling with a test PDF.
4. **PDF-text-only printed codes** (found by the PDF text layer, not by Docling) can be decided but do not gate `reviewed` (B2 D5).
5. **Linux and macOS: the code is written to be portable; it has not been tested there.** The suite has only run on Windows. A CI matrix (ubuntu, macos, windows) is to be added when the Docker/CI work lands (confirmed by the user); until then no one should write "tested on Linux/macOS" about this tool (Task 9 step 6).
6. **The twin needs the raw Docling JSON.** Without it the middle pane is the cell list, which still names the cells but does not show the table.

## Hand-off

**What exists when this is done:** a command, `python -m backend.bintanong_tools.prospectus_review --candidate ... --pdf ...`, that opens a loopback-only page showing the PDF page with the asked cell boxed, the markup twin scrolled to the same cell, and the course JSON; asks one Yes / No / Other question at a time; appends every answer to the B2 ledger through the sheet's own entry builder; shows live content-review state; and rebuilds the corrected candidate on request. The B2 sheet remains the maintainer fallback and produces entries identical in shape.

**What the next person must know:**

- Never write a ledger entry from the GUI code directly; go through `answers.answer_to_entries`, which goes through `sheet.row_entries`. The equivalence tests exist to catch drift.
- Never add a `--host` option, an inline script, or a CDN link. Three tests fail if you do (CLI help, CSP/inline check, external-URL scan).
- The ledger and corrected candidate go outside Git; the guard is `fixer_cli.assert_outside_git`. Do not run the GUI with `--review-dir` pointing into the trial folders' existing `review\` folders unless the user asks.
- This is institutional prospectus review. It is not the student OCR photo review (§15), which is session-only and never touches the institutional knowledge base.
- Read `docs/decisions/prospectus-review-gui.md` and the "Review GUI" section of `plans/plan_current_progress/extractor_split_progress.md` before changing anything.

**Open items after this plan:** the CI matrix (limit 5); rotation handling if real pages need it; whether a later "add a missing course" action is wanted (B2 D8); whether the hosted reviewer interface of §16.1 is ever needed (it would be a new plan with authentication).

## Self-review

- **Requirement coverage.** Local, not hosted: D8, Task 9. PDF page, twin and JSON side by side: Tasks 5, 6, 8. Question-style Yes / No / Other, one question per item, reference never pre-selected: D4, Tasks 3 and 4. "Other" validated by `ledger.correction_problem`: D6, Task 4. Answers through `ledger.make_entry` into the same JSONL, with reviewer, hash and locator, raw candidate untouched, corrected candidate separate: Tasks 2, 4, 7. Ledger fields code, title, term, units and prerequisites: Tasks 2 and 4 (and 10). Bulk confirm only without flags: D11, Tasks 3 and 4. Windows, Linux, macOS: Task 9. Outside-Git guard reused: Tasks 7 and 9. No heavy new dependency, tech choice as a decision row: D1, D2. pypdfium2 rendering and bbox highlight with TOPLEFT and page sizes: D9, Task 5. Sheet kept; identical entries proven by a test: Task 2 step 1 (golden), Task 4 equivalence tests, Task 11 step 5. Separate from OCR photo review: Scope section 1 and the hand-off.
- **Names used across tasks.** `row_entries`, `load_candidate` (Task 2); `Question`, `build_questions`, `order_queue`, `current_decision` (Task 3); `Answer`, `parse_typed_value`, `answer_to_entries` (Task 4); `bbox_fraction`, `boxes_for_question`, `PageRenderer`, `PageError` (Task 5); `load_evidence`, `twin_fragment`, `cells_fallback`, `course_json` (Task 6); `ReviewSession`, `open_session`, `create_app` (Task 7). Task 10 uses C's merged names as recorded in Task 1.
- **No placeholders.** Every task names its files, its tests by function name, its commands and its commit message. The two things that depend on code not yet merged (the exact names from B2 review fixes and from Phase C) are handled by Task 1 step 3, not left open.
