# GUI merge and technical fixes — implementer handoff

Code frozen 7 October 2026, Asia/Manila. Worktree `C:\Users\Hawksprey\source\repos\Bintanong-wt\gui-fixes`, branch `feat/review-gui-fixes-20261007`, HEAD `cf8b11c566d76bd5048a761a169907aee31a242b`, MERGE_HEAD `3227ac8a801396a06b0d593c975df313e7f67c84`. Exact timestamp and Git status are in `checkpoint.json`/`handoff-state.log`; Git and fresh tests outrank this note. No commits, staging, push, dev movement, branch switches, installations, original corpus copies or original mutations were performed. Original automatic merge staging remains intact. No implementer-owned Python/Node/server processes remain.

## Merge result

Resolved working-tree conflict content in `prospectus_extractor/ledger.py`, `tests/test_prospectus_ledger.py`, `tests/test_prospectus_materialise.py`, both GUI/OCR plans and `extractor_split_progress.md`. Index `UU`/`AA` labels deliberately remain until root explicitly stages the resolved paths; no file conflict markers remain. Kept publication's shared persisted-unclaimed/anomaly stale/hash/completion behavior, rebuilt authority and stale-derived-view blocker, all publication tests and history, plus the GUI accepted-blank stamp block and all GUI tests/history. The stamp executes after classification with original audit ambiguity evidence and before `build_authority`, so final prerequisite counts are correct. Removed one duplicated annotation import introduced by auto-merge.

New 10-case merge regression checks reviewed blanks, unresolved/foreign/stale/ambiguous acceptance and pending/verified source records. Materialisation always stays non-executable and preserves source verification. Existing prerequisite No + bulk Yes partial-review semantics and M1–M7 are unchanged. D11 wording ambiguity is recorded without changing decisions. Both publication-scope historical plan headers remain, with a local context note.

`merge-preservation.log` proves every original stage-2/stage-3 function remains in both conflicted test files: ledger 14/14 functions; materialise 23/13 functions. It also proves every original line remains in both plans and progress history (OCR 566/568; GUI 490/492; progress 880/826 lines). Added lines do not replace histories.

## Three technical fixes

1. `session.question_view` includes valid section-confirmation PDF pages through the existing geometry helper, which returns empty boxes for sections. `renderPdf` describes the section instead of undefined highlighted course cells. New session/Node checks exercise visibility, alt text and absence of invented boxes.
2. `renderTwin` uses role `prereq` for prerequisite questions and scrolls only to that asked cell. Missing prerequisite cells do not substitute or scroll to code. Course questions retain their existing code focus. Node tests exercise present/missing prerequisite cells and a course control.
3. Shared `api` catches fetch rejection, malformed JSON, null/non-object bodies, incomplete success envelopes and POST 5xx responses. It returns a visible GET load error or POST save-status-unknown error; it never retries. All six callers were traced: state, queue, question, answer, materialise and twin. Answer fields, reason, choice and current question remain intact on uncertainty; validated HTTP 422 retains its known rejection message. Existing alert/live regions announce errors. Queue refresh errors survive toggle/start flows and the confirmed-save follow-up path, which previously overwrote failure with an all-answered message.

The controlled transport tests simulate a completed POST before response loss; they assert one request, retained answer values and unknown-status wording. They execute actual client functions using the existing Python subprocess/Node VM approach; no package or test framework was added. These are narrow client-boundary tests, not browser or human-trial evidence.

## Authentic commands and results

All pytest commands ran from the GUI worktree with `PYTHONDONTWRITEBYTECODE=1`, system `py -3.13`, `-q -p no:cacheprovider`, and `--basetemp` under this external `gui-fixes` directory. Python 3.13.12 and Node v22.22.3 were observed. Full commands use the following test selection plus the common flags; names below are the actual log and basetemp stems.

| Log / basetemp stem | Actual selection after `py -3.13 -m pytest` | Result / exit |
| --- | --- | --- |
| `merge-focused.log` / `merge-temp` | `tests/test_prospectus_materialise.py tests/test_prospectus_ledger.py tests/test_review_gui_prerequisites.py` | 2 failed, 74 passed / 1 |
| `merge-green.log` / `merge-green-temp` | same selection | 76 passed / 0 |
| `f1-red.log` / `f1-red-temp` | `tests/test_review_gui_session.py tests/test_review_gui_client.py -k 'section_confirmation_shows or section_pdf_is_visible'` | 2 failed, 22 deselected / 1 |
| `f1-green.log` / `f1-green-temp` | `tests/test_review_gui_session.py tests/test_review_gui_client.py tests/test_review_gui_geometry.py tests/test_review_gui_pages.py tests/test_review_gui_static.py` | 61 passed / 0 |
| `f2-red.log` / `f2-red-temp` | `tests/test_review_gui_client.py -k twin_focuses` | 2 failed, 1 passed, 1 deselected / 1 |
| `f2-green.log` / `f2-green-temp` | `tests/test_review_gui_client.py tests/test_review_gui_panes.py tests/test_review_gui_prerequisites.py` | 42 passed / 0 |
| `f3-red.log` / `f3-red-temp` | `tests/test_review_gui_client.py -k 'response_loss or get_failures or confirmed_validation'` | 30 failed, 1 passed, 4 deselected / 1 |
| `f3-green.log` / `f3-green-temp` | `tests/test_review_gui_client.py tests/test_review_gui_static.py tests/test_review_gui_api.py` | 74 passed / 0 |
| `f3-followup-red.log` / `f3-followup-red-temp` | `tests/test_review_gui_client.py -k saved_answer_keeps` | 1 failed, 1 passed, 35 deselected / 1 |
| `focused-final.log` / `focused-final-temp` | `tests/test_review_gui_client.py tests/test_review_gui_static.py tests/test_review_gui_api.py tests/test_review_gui_session.py tests/test_review_gui_prerequisites.py tests/test_prospectus_materialise.py tests/test_prospectus_ledger.py` | 175 passed / 0 |

For example, the final exact command was:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
py -3.13 -m pytest tests/test_review_gui_client.py tests/test_review_gui_static.py tests/test_review_gui_api.py tests/test_review_gui_session.py tests/test_review_gui_prerequisites.py tests/test_prospectus_materialise.py tests/test_prospectus_ledger.py -q -p no:cacheprovider --basetemp 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\gui-fixes\focused-final-temp'
```

`git diff --check` exited 0 (only existing LF→CRLF advisory messages). `py -3.13 check-preservation.py` exited 0 with the stage-preservation results above. Phase-state inspect reported valid formal ledger, active phase none, dirty tree; this parallel workstream does not advance the formal ledger. No broad suite, extractor self-test, comparer, Janus bridge, browser, Lighthouse or human trial was run by the implementer; root owns those gates.

The first new merge regression incorrectly expected one ambiguous course; the printed-row fixture shares provenance across two courses, so the correct count is two. Only that test expectation was corrected, with the failed log retained. The three GUI reds failed for the missing production behavior before their production edits. A first overly greedy merge text script briefly discarded content; conflict files were immediately restored from the untouched index and resolved again with a line-state parser. The preservation check verifies both original sides survived. Initial read-only exploration also had missing `.claude/rules`, top-level AGENTS.md and `web.py` paths and a PowerShell glob/rg argument mismatch; no source or environment changes resulted.

## Changed paths and ownership

Publication paths already automatically staged at start: extractor `identity.py`, `metadata.py`, `pipeline.py`; existing cache/publication and status decision notes; tests `test_prospectus_batch_skip.py`, `test_prospectus_input_snapshot.py`, `test_prospectus_markup.py`, `test_prospectus_publication.py`. Their initial staging was preserved.

Resolved but unstaged content (index still unmerged): extractor `ledger.py`; tests `test_prospectus_ledger.py`, `test_prospectus_materialise.py`; plans `2026-10-04-prospectus-ocr-measurement.md`, `2026-10-05-prospectus-review-gui.md`, `plan_current_progress/extractor_split_progress.md`.

GUI feature paths are unstaged/untracked: `backend/bintanong_tools/prospectus_review_gui/session.py`, `static/review.js`, `tests/test_review_gui_session.py`, new `tests/test_review_gui_client.py`, new `docs/decisions/prospectus-review-gui.md`. No `.gitignore` change or attribution was added. `review.js` and the client test file contain multiple fix hunks; root should use explicit hunks if making separate F1/F2/F3 commits.

External-only artifacts: every log/basetemp directory, checkpoint scripts/state, this report and `HOW_TO_REVIEW_GUI.md`. The guide references the existing real Phase C BSBA-HRM scratch candidate (live read confirmed 23 blank, 24 resolved and 2 standing-condition courses), original-PDF scratch copy and a new human review directory. No new prerequisite questions or institutional files were invented/copied. Root must provide fresh scratch Phase C paths for the other trial candidates before the four-candidate human run. The Task 13 decision record distinguishes historical scripted measurements from current verification and leaves human verdict/final closeout pending.

## Next / do not repeat

Root pins the frozen code, runs fresh broad suite/self-test/corpus/browser/Lighthouse gates and independent Spec/Standards reviews, then explicitly stages the resolved foundation and commits logical feature hunks after gates. Do not treat retained index `UU`/`AA` labels as unresolved file content. Do not rerun publication push/PR creation, original corpus copying, completed Tasks 1–11, or alter owner dev. Do not install into existing environments or publish GUI/OCR automatically. Human Task 12, Task 13 final closeout, source authorization and institutional approval remain pending.
