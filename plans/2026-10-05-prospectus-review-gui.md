# Prospectus Review GUI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task, with superpowers:test-driven-development inside each task. Steps use checkbox (`- [ ]`) syntax. Tasks run through the project agents `extractor-implementer` and `extractor-reviewer`. Update `plans/plan_current_progress/extractor_split_progress.md` after every task commit (each task has a step for it).

**Status:** Written 5 October 2026 against `dev` plus branch `feat/prospectus-phase-b2-section-fixer` (B2 code at `a77e8ed` in the plan worktree). It builds **after B2 and Phase C have merged into `dev`**. Part of the parallel, review-only prospectus workstream: it advances nothing in `plans/INDEX.md` and approves no curriculum, RAG, or Prolog release. A decision recorded here means "a person looked and decided", never issuing-office or curriculum-version approval.

**Goal:** A local researcher GUI that shows, side by side, the original PDF page (with the asked cell highlighted), the reconstructed table (the markup twin) and the extracted JSON of one course, asks one plain question at a time (Yes / No / Other), and writes every answer into the same append-only B2 decision log through `ledger.make_entry`. This is the "local researcher GUI" required by master plan §7.1 step 7, §7.3 (deliverable) and §16.1 (a required preparation tool, separate from any hosted dashboard).

**Architecture:** A small FastAPI app bound to `127.0.0.1`, serving server-rendered JSON plus one static page (plain HTML, CSS and about 300 lines of JavaScript, no build step, no CDN). It is a thin layer over B2: the verifier produces the sections and flags, a new question builder turns rows into questions, a new answer step turns an answer into the exact entries the review sheet would have produced (by calling the same function), and `ledger.append_entries` writes them. `materialise` and `content_review_state` are called unchanged. The raw candidate and the PDF are only read.

**Tech Stack:** Python 3.13, FastAPI 0.141.1 and uvicorn 0.53.0 (the versions the master plan already pins in the `api` extra), `pypdfium2` and Pillow (both already arrive with Docling), stdlib otherwise, pytest 9, `uv`. No Node, no npm, no Jinja2, no htmx, no desktop toolkit.

**Base:** `dev` after B2 and Phase C merge. **Branch to create:** `feat/prospectus-review-gui`. Leave the dirty `.gitignore` and the untracked `plans/CODEX_HANDOFF_prospectus_extractor_phase2_2026-09-26.md` alone; never `git add -A` or `git add .`; stage by explicit path.

**Schema versions:** unchanged. The GUI adds no key to the candidate payload and no field to a ledger entry. The only new ledger values are two `via` strings (`gui`, `gui_section_confirm`); `via` is already a free-text field (`ledger.make_entry`, parameter `via`, default `"sheet"`) and `entry_problem` does not check it.

**Evidence base:** every statement about the code below was read in the plan worktree on 5 October 2026 (`ledger.py`, `sheet.py`, `verify.py`, `fixes.py`, `fixer_cli.py`, `markup.py`, `placement.py`, `evidence.py`, `loader.py`, `course_checks.py`) and every statement about the data was read from `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\review_trial_2026-10-04\16_BSBA-HRM\`. Task 1 re-checks both, because B2 and C will have moved.

---

## Scope, and what this is not

**In scope.** Institutional prospectus review by researchers, on their own machine: open one candidate, answer questions, rebuild the corrected candidate, see the three states (extraction audit, content review, source verification) change as answers arrive.

**Not in scope, stated so nobody mixes them up.**

1. **This is not the end-user OCR photo review.** The OCR review (a student confirms values read from their own photographed grades or curriculum, master plan §15) is session-only, runs inside the hosted student app, and **never touches the institutional knowledge base**. This GUI runs on a researcher's machine, reads institutional PDFs and candidate JSON, and its decisions never reach a student request path. The two share no code, no storage, no ledger and no UI. (A future OCR bake-off may write review rows in the B2 ledger *format* for its own measurement; that is a file format reuse, not a shared tool.)
2. **No hosted reviewer dashboard.** Master plan §16.1: a hosted reviewer interface needs authenticated identities and controlled PDF access and is not required for the thesis pipeline. This tool has no login; it is protected only by being loopback-only (D8).
3. **No new editing power over the raw extraction.** The candidate JSON is never modified. A corrected candidate is a separate file built by `ledger.materialise`.
4. **No "add a missing course" action.** Same as B2 decision D8: it needs per-field cell provenance and belongs to a later parser or GUI step. Printed codes no course claimed can be decided (`accepted` or `unresolved`), never invented.
5. **No approval.** `content_review: reviewed` means a person decided every course. The GUI header says so in plain words, and so does the decision record.

---

## Decisions needed before execution

The rest of the plan assumes the recommendation in each row. Steps that would change are marked **[D#]**.

| # | Question | Options | Recommendation and why |
| --- | --- | --- | --- |
| D1 | Tech choice for the local GUI. | (a) FastAPI serving one static page of plain HTML/CSS/JS plus JSON endpoints (server-rendered twin and question text, small JS for keyboard and panes). (b) FastAPI plus Jinja2 plus htmx. (c) A Next.js page in `frontend/`. (d) A Python desktop toolkit (Tkinter, PySide6, or a Gradio/Streamlit-style framework). | **(a).** The master plan's stack is Python 3.13 and FastAPI for the backend (§2) and Next.js with shadcn/ui and Tailwind for the **student-facing** interface (§16). This tool is local, offline and researcher-only, and §16.1 itself separates it from the hosted interface. (c) would add Node, `npm install`, a build step and a second dev server to a tool whose users run one command; it also tempts reuse of the student app's design system for a screen that has nothing to do with students. Its only real benefit (shared components) does not apply. (d) PySide6 is a 100+ MB dependency with a licensing question, Tkinter cannot show an HTML table with highlighted cells without writing a renderer, and the markup twin is already HTML, which a browser shows for free. (b) saves little: the page has three panes and one form, and Jinja2 plus htmx are two more things to vendor for offline use. FastAPI is already planned, pinned, and tested in this repository, and the browser gives zoom, find, tab order and screen-reader support at no cost. **Consequence:** the front end is hand-written and small; any later move to Next.js would reuse the JSON endpoints unchanged. |
| D2 | How the new dependencies are declared. | (a) A new optional extra `review` in `backend/pyproject.toml` with the same three pins as `api` (`fastapi==0.141.1`, `uvicorn==0.53.0`, `httpx==0.28.1` for the test client), no conflict declaration. (b) Document `--with` flags only. (c) Reuse the `api` extra. | **(a).** The `api` extra conflicts with `embedding` in `[tool.uv] conflicts` and carries `asyncpg`, `janus-swi` and `pydantic`, none of which a reviewer needs; `--with` flags drift out of the docs. Same pins as the master plan, so no new version decision. `pypdfium2` and Pillow come with the `tools` extra (Docling); Task 1 proves it and stops if Pillow is missing. Changes Tasks 1 and 9 (and `uv.lock` if the repository keeps one; Task 1 checks). |
| D3 | Question queue order. | (a) Printed order. (b) Broken sections first, then review, then clean; inside a section, flagged rows (errors, then warnings) before clean rows; printed order breaks ties. (c) User-sorted. | **(b).** B2's whole premise is "spend time on broken, confirm clean in bulk". The sheet orders by print because it is a document; a queue should put the work that needs a human first. Printed order is one keystroke away (a "print order" toggle in the queue panel, same data). Clean sections are offered as one bulk question first (D11) so most of their rows never become individual questions. Decided items drop out of the queue and stay reachable from the section list. Changes Task 3. |
| D4 | What one question is, and how Yes / No / Other map to ledger entries. | (a) One question per course row, per unclaimed printed code, per section bulk confirm, and per prerequisite that Phase C marks as not understood. Yes / No / Other map onto the **existing sheet verbs** (`ok`, `fix`, `edit`, `unresolved`) and are written by the same function. (b) One question per field. (c) A diff editor. | **(a).** Per-field questions triple the clicks for the common case (the row is right). The mapping is exact: **Yes** = `ok` (an `accepted` `row` entry, reason "accepted as extracted"). **Other** = `edit` (a `row` accepted entry plus one `corrected` entry per typed field, the typed value validated by `ledger.correction_problem`; reason required). **No** = `unresolved` (a `row` entry with disposition `unresolved`, reason required) when no value is typed, and the same as Other when the reviewer then types a value. A proposal from the fixer is a *hint under the question*, never pre-selected; a button "use proposal a" fills the typed field (explicit click) and, when the typed value equals the proposal's, the answer is recorded as `fix` (with `fix_id`), exactly as the sheet records it. Question text, e.g. "Is the subject *Ethics* with course code *GE-ET* correct?", and for a printed code "The PDF prints *CS 9* on page 3 but no course uses it. Is it right to leave it out?" Changes Tasks 2 to 4. |
| D5 | Keyboard-first flow. | (a) Single-key answers with a visible key hint on every control: `Y` Yes, `N` No, `O` Other, `Enter` submit, `Esc` cancel the Other form, `J`/`K` or `Down`/`Up` next/previous question, `1`-`9` use proposal a-i, `Z` zoom the PDF, `/` focus the queue filter, `?` key help. Single keys are disabled while a text field has focus. (b) Mouse only. (c) Vim-style chords. | **(a).** A reviewer answering several hundred rows should not leave the keyboard. Disabling single keys inside text fields is what keeps typing a title safe. All keys are also real buttons, so mouse and screen reader users lose nothing. Changes Task 8. |
| D6 | How "Other" input is validated. | (a) Server-side only, by `ledger.correction_problem`, after a typed-value parser that turns text into the field's type (whole numbers for units, `year / semester` text for term via `parse_term`, text otherwise); the message is shown next to the field and nothing is written. (b) Client-side regexes. (c) Both. | **(a).** The ledger already owns the rules and reads them back (`entry_problem` re-runs `correction_problem` on every line), so a second copy in JavaScript would drift. The browser only enables the submit button when a field is non-empty. Typed values are never reformatted silently: units `"3"` becomes `3`, `"3.5"` and `"1e2"` are refused with the ledger's own message; a term typed as `2nd year first sem` is accepted only if `parse_term` reads it, and is stored as `format_term(...)`, same as the sheet. Changes Task 4. |
| D7 | Offline assets. | (a) No external URL anywhere: system font stack, one CSS file, one JS file, an inline SVG icon set, all served from the package. A test fails on any `http://` or `https://` in served assets. (b) CDN for htmx or fonts. | **(a).** Master scope is "local, offline, researcher-only" and the prospectus data is institutional. A CDN call would leak nothing secret but breaks offline use and invites a supply-chain surprise. The only network the page uses is `fetch` to its own origin. Changes Tasks 7 and 8. |
| D8 | Bind address, port and local-attack hardening. | (a) Bind `127.0.0.1` only; there is **no `--host` option**; default port 8765, `--port 0` picks a free one; reject any request whose `Host` header is not `127.0.0.1:<port>` or `localhost:<port>` (DNS rebinding); every POST needs a per-launch random token (in the page's meta tag, sent as `X-Review-Token`) and, if an `Origin` header is present, it must be the app's own origin (a web page elsewhere in the researcher's browser must not be able to write decisions); send a strict Content-Security-Policy (`default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'`), which is why the page has no inline script or style. (b) Allow `--host 0.0.0.0` with a warning. | **(a).** A tool that holds an institutional ledger and a reviewer's name must not listen on the network, and a locally running web server is reachable by any web page the reviewer opens, so loopback alone is not enough. Remote use, if ever needed, is an SSH tunnel, not a flag. Changes Tasks 7 and 9. |
| D9 | How the page image and the highlight are made. | (a) Render the page with `pypdfium2` to PNG (scale 1.5 by default, up to 3), serve it, and draw the highlight in the browser as a CSS overlay in percent of the page, computed on the server from the cell bbox and the page size. (b) Draw the box into the PNG with Pillow on the server. (c) Use pdf.js. | **(a).** Percent overlays survive zoom without re-rendering, let the browser draw several boxes (the asked cell strong, the course's other cells faint), and keep the PNG cacheable per page. (c) is a JavaScript library to vendor and trust. The mapping rule is fixed by the data: candidate cell boxes are in the table-cell frame (`SourceBBox.origin == TOPLEFT`, y down), and so are the boxes the verifier gives unclaimed items (`placement.py` converts PDF text boxes with `height - y`), so `left/width`, `top/height` of the page size. Page size comes from `pypdfium2`'s `page.get_size()` (points) and is cross-checked against Docling's `page_sizes` when the raw Docling JSON is available; a page with a non-zero rotation, or a size mismatch over 1 point, gets **no highlight and a visible warning**, never a wrong box. Changes Tasks 5 and 6. |
| D10 | Where the twin and the JSON pane come from, and what happens when something is missing. | (a) Candidate (required), PDF (required for the image and the PDF checks; `--pdf` or via `fixer_cli.resolve_identity`), raw Docling JSON (optional, `--docling-json`, default the path recorded in `provenance.raw_docling_json`) for the twin. Missing PDF: the page pane says so, questions still work from the hash. Missing Docling JSON: the twin pane shows the course's own source cells (id, row, column, text) from the candidate instead and says "markup twin unavailable". (b) Refuse to start without all three. | **(a).** The candidate stores cell text and boxes but **not** the box origin or page sizes, and the twin needs the raw Docling evidence (`loader.load_from_raw_json`, then `markup.render_prospectus_markup`). The recorded path is an absolute path from the machine that ran the extraction (BSBA-HRM's points into `E:\...\docling_jsonified_output\...`), so it may not exist on another computer. A tool that refuses to open is worse than one that degrades visibly. The `pdf_sha256` is the one thing that must be known; the existing `resolve_identity` already insists on it. Changes Tasks 6 and 9. |
| D11 | Bulk "confirm section". | (a) Offered only for a section with no flags above `info`, the same rule as the sheet (`build_entries` rejects `confirm: yes` on a section with a blocking flag): one question, "Are all N courses in *1st Year - 1st Semester* correct as extracted?", options Yes and No only (Other has nothing to type, so it is shown disabled with the reason; an optional note becomes the entry reason, default "section confirmed as extracted"). Yes writes one `row` `accepted` entry per course, `via` = `gui_section_confirm`. (b) Allow bulk on flagged sections after a warning. | **(a).** It is the rule the owner already tested. The server re-checks it on every answer (not only when building the question), so a stale browser tab cannot confirm a section that has since become flagged. Changes Tasks 3 and 4. |
| D12 | Where the GUI package lives. | (a) A new sibling package `backend/bintanong_tools/prospectus_review_gui/` with a `__main__`, plus a thin `backend/bintanong_tools/prospectus_review.py` entry like `prospectus_fixer.py`. (b) Modules inside `prospectus_extractor/`. | **(a).** Fact from B2: the legacy shim re-exports every public name of every module in the extractor package, last module wins, so a new module there that defines `main` or `create_app` silently replaces another. The GUI also imports FastAPI, which the extractor package must not need. It imports the extractor modules; the extractor never imports it. Changes the file structure. |

## What the code and the data say (read 5 October 2026)

1. **The decision pipeline is already one function.** `sheet._row_entries(entries, row, section, payload, verb, letters, reason, edits, via, reviewer, pdf_sha256, now)` turns a verb into entries for a course; `build_entries` only parses a sheet around it. The GUI must call that function (made public in Task 2), not re-derive entries. That is what makes "identical in shape to the sheet path" true by construction and provable by a test.
2. **`_row_entries` only edits code, title and term.** The ledger can now correct units and `prerequisites_raw` too (`ledger.CORRECTABLE_FIELDS`), but the sheet's edit columns (`EDIT_FIELDS`) are only the first three. Task 2 extends the shared function to the other fields; the sheet keeps its three columns (it stays a maintainer fallback and its output must not change; its tests are the guard).
3. **The candidate does not carry what the twin and the highlight need.** `provenance.source_cells[*]` has `cell_id`, `page`, `bbox` (4 numbers), row/column spans and text, but no `origin` and no page size. Page sizes live in the raw Docling JSON (`loader.load_from_raw_json` builds `ProspectusEvidence.page_sizes`) and in the PDF itself. A course's `provenance.bbox` is the union of all its cells **including the section banner cell**, so highlighting it would box the whole banner row; the verifier's `own_role_cells(course, layout, evidence_ids)` gives the course's own code, title, unit and prerequisite cells and is what the highlight uses.
4. **The twin is one Markdown document with raw HTML blocks.** `markup.render_prospectus_markup(evidence, payload, pdf_sha256=...)` returns a document with a leading `> ` notice line, HTML comments, `<h1>/<h2>/<p>` text items and `<table data-table data-page>` with `<td data-cell="t0-c12" data-page="1">`. Everything is already HTML-escaped by the renderer. The GUI strips the `> ` notice (it states the audit status; the GUI header shows its own), wraps the rest in one container, and scrolls to and highlights `[data-cell="<id>"]` for the course's `source_cell_ids`. No Markdown library is needed.
5. **A decision is located by cell ids.** `ledger.course_locator` uses sorted `source_cell_ids`, page, table index and `code_at_review`; an unclaimed item uses `unclaimed_locator`. The GUI never invents a locator; it passes the row to the shared function.
6. **The outside-Git guard exists and must be reused.** `fixer_cli.assert_outside_git(path)` resolves the path and refuses a tracked or non-ignored place inside the repository. At this worktree's `.gitignore` there is no `review/` rule, so the guard really does refuse a ledger under the repository; the GUI calls it at startup for the ledger and again before writing the corrected candidate. The GUI writes **nothing else**: page images are rendered into memory and cached in memory.
7. **Entries can be stale or foreign, and the GUI must show it, not hide it.** `ledger.split_valid`, `split_applicable` and `split_stale` classify entries (invalid, another PDF, old value changed, course not found). `content_review_state` reports the counts. The GUI shows them in a status panel and applies nothing it should not; "change my answer" is a new entry, never an edit (later entry per course and field wins, `latest_by_field`).
8. **Trial data.** The four prospectuses are `01_Architecture` (mixed, 17 titles with a `title_from_pdf` proposal), `13_BSE-Innovation-and-Tech` (broken: 76 unclaimed codes against 2 courses), `16_BSBA-HRM` (warnings only, 8 sections), `33_BSCS-2025-2026` (mixed, a `SU` section of footnote codes). Each folder already contains a `review/` sub-folder from the sheet trial; **the gate must not write there** (Task 11 uses a scratch review directory and copies).
9. **Phase C changes what the GUI can ask.** C adds `prerequisite_state` per course and reserves `reviewed_empty` "for a human review decision" (C plan D1); C's own plan does not say how that decision is recorded. Task 10 defines it (an `accepted` `prerequisites_raw` entry on a blank prerequisite) and makes `materialise` stamp the state. Task 1 reads C as merged and records the real names; Task 10 uses them.

## File structure

New package code is under `backend/bintanong_tools/prospectus_review_gui/`. A module imports only from modules above it in this list, and from the extractor package.

| File | Change | Responsibility |
| --- | --- | --- |
| `prospectus_extractor/sheet.py` | Modify (Task 2) | `_row_entries` becomes public `row_entries`; generalised to units and prerequisite edits. No change to rendering, parsing or sheet output. |
| `prospectus_extractor/fixer_cli.py` | Modify (Task 2) | Public alias `load_candidate` for `_load`; nothing else. |
| `prospectus_review_gui/questions.py` | Create (Task 3) | `Question`, `build_questions`, `order_queue`, `decided_keys`: what to ask, in which order, what is already decided. |
| `prospectus_review_gui/answers.py` | Create (Task 4) | `Answer`, `parse_typed_value`, `answer_to_entries`: an answer to ledger entries, validated, via `sheet.row_entries`. |
| `prospectus_review_gui/geometry.py` | Create (Task 5) | `bbox_fraction`, `boxes_for_question`: box to percent-of-page, rotation and size-mismatch refusal. |
| `prospectus_review_gui/render.py` | Create (Tasks 5, 6) | `PageRenderer` (pypdfium2 to PNG, in-memory cache), `twin_fragment`, `cells_fallback`, `course_json`. |
| `prospectus_review_gui/session.py` | Create (Task 7) | `ReviewSession`: candidate, identity, verification, ledger path, reviewer, lock; `queue()`, `question()`, `answer()`, `state()`, `materialise()`. |
| `prospectus_review_gui/app.py` | Create (Task 7) | `create_app(session, token)`: routes, Host/Origin/token checks, CSP headers. |
| `prospectus_review_gui/static/index.html`, `review.css`, `review.js` | Create (Task 8) | The page, three panes, keyboard map. |
| `prospectus_review_gui/cli.py`, `__main__.py` | Create (Task 9) | Arguments, startup guards, uvicorn on loopback, optional browser open. |
| `backend/bintanong_tools/prospectus_review.py` | Create (Task 9) | Thin `python -m` entry. |
| `prospectus_extractor/ledger.py` | Modify (Task 10, only after Phase C) | `materialise` stamps `reviewed_empty` for an accepted blank prerequisite. |
| `backend/pyproject.toml` | Modify (Task 1 or 9) | The `review` extra (D2). |
| `tests/test_review_gui_*.py` | Create | One focused file per task (names below). |
| `tests/review_gui_fixtures.py` | Create (Task 3) | Candidate and PDF fixtures reusing `tests/fixer_fixtures.py`. |
| `scripts/prospectus_review_gui_smoke.py` | Create (Task 11) | Drives the app through TestClient on real candidates, read-only. |
| `docs/decisions/prospectus-review-gui.md` | Create (Task 13) | Decision record. |
| `plans/plan_current_progress/extractor_split_progress.md` | Modify | New "Review GUI" section, updated after each task. |

Unchanged on purpose: `ledger.py` (except Task 10), `verify.py`, `fixes.py`, `markup.py`, `placement.py`, `loader.py`, `pipeline.py`, `selftest.py` (still 80/80). The GUI adds no extractor behavior.

## Commands used throughout

PowerShell, repo root (Git Bash is broken on this machine).

```
# Full suite (record the baseline in Task 1)
uv run --project backend --extra tools --extra dev --extra review python -m pytest -q tests

# One file
uv run --project backend --extra tools --extra dev --extra review python -m pytest -q tests/test_review_gui_questions.py

# Self-test (baseline 80/80; it must not change)
uv run --project backend --extra tools --extra dev python -m backend.bintanong_tools.prospectus_extractor --self-test

# The GUI (after Task 9)
uv run --project backend --extra tools --extra review python -m backend.bintanong_tools.prospectus_review --candidate CANDIDATE.json --pdf ORIGINAL.pdf --review-dir SCRATCH_DIR
```

Real-data paths (outside Git): `$TRIAL` is `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\review_trial_2026-10-04` (four folders, each with the PDF, `*_prospectus.json`, `*_prospectus.md` and an existing `review\` folder that is **never written to**). `$SCRATCH` is a fresh folder under `$env:TEMP`.

Commit trailer for every commit in this plan: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

---

### Task 1: Start check

**Files:** read only, plus the progress file and, if D2 is accepted, `backend/pyproject.toml`.

- [ ] **Step 1: Confirm the base.** On `dev`, `git log --oneline -15` shows the B2 merge and the Phase C merge. If either is missing, stop: this plan builds on both. Create `feat/prospectus-review-gui` from `dev`.
- [ ] **Step 2: Baseline.** Run the full suite and the self-test with the commands above. Record the pass counts (B2 closed at 253 plus 13 subtests, self-test 80/80; Phase C adds more). The self-test must be 80/80.
- [ ] **Step 3: Re-read the five interfaces this plan calls and record their final names in the progress file.** `sheet.row_entries`/`_row_entries` and `build_entries`; `ledger.make_entry`, `append_entries`, `content_review_state`, `materialise`, `write_corrected`, `correction_problem`, `split_valid`, `split_applicable`, `split_stale`, `latest_by_field`; `verify.verify_candidate`, `own_role_cells`, `Row`, `Section`, `Flag`; `fixer_cli.resolve_identity`, `resolve_reviewer`, `assert_outside_git`, `default_review_dir`; `markup.render_prospectus_markup` and `loader.load_from_raw_json`. Also read Phase C as merged: the names of the prerequisite-state vocabulary (`PREREQUISITE_STATES`, `EXECUTABLE_PREREQUISITE_STATES`, `annotate_prerequisite_states`), the `extraction_audit`/`content_review`/`source_verification` payload fields and the `authority` block. If a name differs from this plan, the plan's tasks use the merged name and the progress file records the mapping.
- [ ] **Step 4: Prove the runtime pieces import.** Run (extras as above): `python -c "import fastapi, uvicorn, httpx, pypdfium2, PIL; print(pypdfium2.version.PYPDFIUM_INFO, PIL.__version__)"`. If `fastapi`, `uvicorn` or `httpx` fail, add the `review` extra to `backend/pyproject.toml` now (D2) with the three pins, regenerate the lock if the repository has one (`uv lock --project backend`), and re-run. **If `PIL` fails, stop and raise it**: the page renderer needs Pillow or a hand-written PNG encoder, which is a design change.
- [ ] **Step 5: Prove the real data opens read-only.** Read `$TRIAL\16_BSBA-HRM\*_prospectus.json` and confirm: courses have `provenance.source_cells[*].bbox` and `page`; `provenance.raw_docling_json` is a path; `audit.table_layout` and `audit.curriculum_sections` exist. Compute and record the SHA-256 of every PDF and `*_prospectus.json` in the four folders into the progress file (Task 11 re-checks them).
- [ ] **Step 6: Check that the recorded Docling JSON path exists on this machine** for each of the four candidates (`Test-Path` on `provenance.raw_docling_json`). Record which exist: it decides whether Task 6 and Task 11 can show the twin or only the fallback.
- [ ] **Step 7: Progress entry.** Append a "Review GUI" section to `plans/plan_current_progress/extractor_split_progress.md` (branch, base commit, baseline counts, the name mapping). Commit that file (and `backend/pyproject.toml`/lock if changed) by explicit path: `chore: start the review GUI branch and record the B2 and C interfaces`.

---

### Task 2: One decision builder for the sheet and the GUI

**Files:**
- Modify: `backend/bintanong_tools/prospectus_extractor/sheet.py` (rename `_row_entries` to `row_entries` with no alias left behind, update its one caller in `build_entries`, extend field handling)
- Modify: `backend/bintanong_tools/prospectus_extractor/fixer_cli.py` (public `load_candidate`)
- Test: `tests/test_review_gui_decisions.py` (new), existing `tests/test_prospectus_sheet.py`, `tests/test_prospectus_sheet_decisions.py`, `tests/test_prospectus_fixer_cli.py` (must stay green and unchanged)

Why first: every later task depends on this function. The sheet is the fallback and must not change behavior; the GUI needs the same function with two extra editable fields.

- [ ] **Step 1: Write the failing tests** in `tests/test_review_gui_decisions.py`, using a fixture candidate from `tests/fixer_fixtures.py` and `verify_candidate` to get a real `Row` and `Section`:
  - `test_row_entries_is_public_and_build_entries_uses_it` (import `row_entries` from `sheet`; the old private name is gone; a spy on `row_entries` is called once per decided row by `build_entries`).
  - `test_row_entries_ok_writes_one_accepted_row_entry` (verb `ok`, no reason: one entry, field `row`, disposition `accepted`, `old_value == new_value == course_snapshot`, reason `accepted as extracted`).
  - `test_row_entries_edit_unit_field_writes_corrected_int` (edits `{"lecture_units": 2}`; entries are the `row` accepted entry plus one `corrected` entry with `old_value` the current `lecture_units` and `new_value` `2`, `correction_problem` is `None`).
  - `test_row_entries_edit_total_units_and_prerequisites`.
  - `test_row_entries_rejects_fraction_and_out_of_range_units` (`3.5`, `100`, `True`, `"3"` each return an error string equal to `ledger.correction_problem`'s text; no entry).
  - `test_row_entries_rejects_unchanged_value` (the existing "new value equals the current one" rule now also applies to units and prerequisites).
  - `test_sheet_output_is_unchanged_for_code_title_term` (apply the three existing sheet verbs to a fixture through `build_entries` and compare the entries with a golden list captured **before** the edit, committed as `tests/fixtures/` JSON written in this step from the unmodified code).
- [ ] **Step 2: Run to verify red.** `... pytest -q tests/test_review_gui_decisions.py`. Expected: ImportError on `row_entries`; the golden test is red only because the import fails (capture the golden first, from the old code).
- [ ] **Step 3: Implement the minimum.** Rename and update the caller. Generalise the "changes" loop from `(FIELD_CODE, FIELD_TITLE, FIELD_TERM)` to `ledger.CORRECTABLE_FIELDS` with the same order (code, title, term, then the three unit fields, then `prerequisites_raw`); old values for units and prerequisites come from `ledger._current` semantics (the course's own field). Typed values for units are `int`, validated by `correction_problem` before an entry is built (an invalid value returns an error string instead of raising, like the other messages). Do not add columns to the sheet. Add `load_candidate` in `fixer_cli.py` as a one-line public name for `_load`.
- [ ] **Step 4: Run to verify green**, then the whole suite: nothing that passed before may fail; the sheet golden is unchanged byte for byte.
- [ ] **Step 5: Commit.** `refactor: share one decision builder between the review sheet and the GUI`, staging the two source files and the test files by explicit path.
- [ ] **Step 6: Progress entry**, committed by path.

---

### Task 3: Questions and the queue

**Files:**
- Create: `backend/bintanong_tools/prospectus_review_gui/__init__.py` (empty), `questions.py`
- Create: `tests/review_gui_fixtures.py`
- Test: `tests/test_review_gui_questions.py`

Behavior: from the candidate, the verification and the ledger entries, build the questions and order them (D3, D4, D11). A `Question` carries: `qid` (the row id, e.g. `S1-02`, `S1-U1`, or `S1:confirm`), `kind` (`course`, `unclaimed`, `section_confirm`, later `prerequisite`), `section` (sid and title), `prompt` (the sentence), `reference` (the values shown: code, title, term, units, prerequisites), `flags` (severity, kind, message), `proposals` (letter, kind, field, old, new, note), `editable_fields`, `other_allowed` (False for unclaimed and for section confirm), `decision` (the current decision, if any, from the ledger), and `pages` (page numbers involved). Function names: `build_questions(payload, verification, entries, pdf_sha256)`, `order_queue(questions, mode)` with modes `attention` and `print`, `current_decision(question, entries, pdf_sha256)`.

- [ ] **Step 1: Write the failing tests** (fixtures: the three B2 fixtures plus a new small candidate with one clean section, one `review` section and one `broken` section):
  - `test_one_question_per_course_row_and_per_unclaimed_item`.
  - `test_course_prompt_names_title_and_code` (exact sentence: `Is the subject "<title>" with course code "<code>" correct?`; a title containing a double quote or a non-ASCII letter is kept intact, not escaped in the data).
  - `test_unclaimed_prompt_names_code_and_page`.
  - `test_clean_section_gets_one_bulk_question_and_flagged_section_does_not` (D11; the bulk question lists the course count; Other is not allowed).
  - `test_bulk_question_absent_when_only_info_flags`... inverse: a section with only `info` flags still gets it (same rule as `build_entries`' `blocking = severity != "info"`).
  - `test_queue_order_attention_puts_broken_then_review_then_clean_and_errors_before_warnings`.
  - `test_queue_order_print_is_printed_order`.
  - `test_reference_value_is_never_preselected` (no question has a `selected` or `default_answer` field; the proposals are data only).
  - `test_decided_questions_leave_the_attention_queue_but_stay_listed` (an `accepted` row entry for the course removes it from the queue, shows it as `decision.disposition == "accepted"` in the section list).
  - `test_entry_for_another_pdf_does_not_count_as_decided` and `test_stale_entry_does_not_count_as_decided` (old value changed).
  - `test_later_entry_wins` (accepted then unresolved: shown unresolved and back in the queue).
  - `test_questions_do_not_mutate_the_payload` (deep-equal before and after).
- [ ] **Step 2: Run to verify red** (module missing).
- [ ] **Step 3: Implement the minimum.** Use `verify_candidate` rows and sections as given, `ledger.split_valid`/`split_applicable`/`split_stale`/`latest_by_field` for "decided", `locator_key(course_locator(course))` as the key. No new matching logic.
- [ ] **Step 4: Run to verify green**, then the whole suite.
- [ ] **Step 5: Commit** `feat: build the review questions and order the queue`; progress entry.

---

### Task 4: Answers to ledger entries, and the equivalence proof

**Files:**
- Create: `backend/bintanong_tools/prospectus_review_gui/answers.py`
- Test: `tests/test_review_gui_answers.py`, `tests/test_review_gui_sheet_equivalence.py`

Behavior: `Answer` (choice `yes | no | other`, `edits` as `{field: text}`, `proposals` as letters, `reason`, `note`). `parse_typed_value(field, text)` returns `(value, None)` or `(None, message)`. `answer_to_entries(question, answer, *, payload, verification, reviewer, pdf_sha256, via="gui", now=None)` returns `(entries, errors)`; any error means no entries (same all-or-nothing rule as the sheet). Mapping (D4): yes to `ok`; other to `edit` (or `fix` plus `edit` when proposal letters are given); no to `unresolved` when no value is typed, else as other; unclaimed: yes to `ok`, no to `unresolved`, reason required for both (as the sheet requires it); section confirm: one `ok` per course with `via="gui_section_confirm"`, re-checking D11.

- [ ] **Step 1: Write the failing tests** in `tests/test_review_gui_answers.py`:
  - `test_yes_on_course_writes_accepted_row_entry_with_reviewer_hash_locator` (reviewer, `pdf_sha256`, `locator` with the course's sorted cell ids, `via == "gui"`, `rejected_fixes == []`).
  - `test_other_with_title_writes_row_accepted_plus_corrected_title`.
  - `test_other_requires_a_value_and_a_reason`.
  - `test_other_value_goes_through_correction_problem` (empty title, a term that `parse_term` cannot read, units `3.5`, units `100`, units `"abc"`, prerequisites typed as a number: each gives the ledger's message and no entry).
  - `test_term_is_stored_as_format_term` (typed `2nd year first semester`, stored `2nd Year / 1st Semester`).
  - `test_units_text_becomes_int` (`"3"` to `3`; `" 3 "` to `3`; `"03"` accepted as `3`; `"+3"` refused).
  - `test_no_without_values_is_unresolved_and_needs_a_reason`; `test_no_with_values_is_a_correction`.
  - `test_proposal_button_value_is_recorded_as_fix` (typed value equal to proposal `a`'s new value gives `fix_id` and `reason` from the sheet's wording; a differing value gives `fix_id None`).
  - `test_unclaimed_yes_and_no_need_a_reason`; `test_unclaimed_other_is_refused_with_a_clear_message`.
  - `test_section_confirm_refused_when_section_has_blocking_flag` (answer-time re-check, not only question-time).
  - `test_section_confirm_writes_one_entry_per_course_with_gui_section_confirm`.
  - `test_every_entry_passes_ledger_entry_problem` (property over all of the above).
  - `test_answer_never_mutates_candidate` (deep-equal).
- [ ] **Step 2: Write the equivalence tests** in `tests/test_review_gui_sheet_equivalence.py`. This is the test the requirement asks for:
  - `test_gui_entries_equal_sheet_entries_for_every_verb` (parametrised over: ok on a clean row, `fix` on a row with proposals, `fix a` with a rejected second proposal, `edit` of code, of title, of term, of all three, `unresolved`, unclaimed `ok`, unclaimed `unresolved`, and section confirm). For each case: render the sheet, edit it with `tests/sheet_helpers.py`, run `parse_sheet` plus `build_entries` with a fixed `now`, and run `answer_to_entries` for the equivalent answer with the same `now` and `via` forced to the value the sheet used. Assert the two entry lists are **equal as JSON** (same keys, same values, same `entry_id`).
  - `test_default_gui_entries_differ_from_sheet_entries_only_in_via_and_entry_id` (with the default `via="gui"`: after removing `via` and `entry_id` the lists are equal, and the key sets are identical).
  - `test_gui_ledger_materialises_to_the_same_corrected_candidate_as_the_sheet_ledger` (append both lists to two ledger files, run `ledger.materialise` on each, compare the corrected payloads after removing `review.applied_entry_ids` and `review.skipped` ids, which differ only through `entry_id`; and compare `content_review_state`).
  - `test_gui_only_fields_materialise` (a `lecture_units` and a `prerequisites_raw` correction recorded through the GUI path produce the corrected values and a re-resolved prerequisite list, and `verification_counts` is rebuilt).
  - `test_gui_entries_append_idempotently` (answering the same thing twice through `append_entries`: second call writes 0, skips 1).
- [ ] **Step 3: Run to verify red**, **Step 4: implement the minimum** (thin: build `row`/`edits` for `sheet.row_entries`; never build an entry directly), **Step 5: green and full suite**, **Step 6: commit** `feat: turn review answers into ledger entries through the sheet's own builder`; progress entry.

---

### Task 5: Page rendering and highlight geometry

**Files:**
- Create: `backend/bintanong_tools/prospectus_review_gui/geometry.py`, `render.py` (the `PageRenderer` part)
- Test: `tests/test_review_gui_geometry.py`, `tests/test_review_gui_pages.py`

Behavior (D9): `bbox_fraction(bbox, page_size)` gives `{left, top, width, height}` as fractions of the page, in the TOPLEFT frame, clamped to 0..1, `None` for an incomplete box or a zero page size. `boxes_for_question(question, course, role_cells, page_size, rotation, docling_size)` returns a list of `{role, strong, fractions}` or `{"warning": ...}` with no boxes. `PageRenderer(pdf_path)` opens the PDF with `pypdfium2`, `png(page_number, scale)` returns PNG bytes, `size(page_number)` returns `(width, height)` in points, `rotation(page_number)`; an in-memory cache of the last 8 renders; raises a typed `PageError` for a missing PDF or an out-of-range page. Nothing is written to disk.

- [ ] **Step 1: Write the failing tests.**
  - `test_bbox_fraction_top_left_frame` (page 600 by 800, box `[60, 80, 120, 160]` gives `0.1, 0.1, 0.1, 0.1`).
  - `test_bbox_fraction_clamps_and_refuses_incomplete_boxes`.
  - `test_unclaimed_item_box_uses_the_same_frame` (a box from `placement.locate_in_page` on a generated PDF lands on the code when drawn: rendered pixels under the fraction contain dark pixels, paper elsewhere; uses a one-page reportlab PDF with a known text position).
  - `test_course_highlight_uses_own_role_cells_not_the_banner` (BSBA-HRM-like fixture: the `GE-ET` course's boxes are the code, title and unit cells; the banner cell `t0-c10` is not drawn strong; `provenance.bbox` is not used).
  - `test_rotated_page_gets_warning_and_no_boxes` (reportlab page with `setPageRotation(90)`).
  - `test_size_mismatch_with_docling_over_one_point_warns` and `test_size_within_one_point_is_accepted`.
  - `test_png_is_a_png_with_scaled_dimensions` (signature `\x89PNG`, width equals `ceil(width_pt * scale)` within one pixel; use `tests/fixtures/synthetic_academic_guide.pdf`).
  - `test_render_is_cached_and_writes_no_file` (second call returns identical bytes without reopening the page; the temp directory listing and the working directory are unchanged).
  - `test_missing_pdf_and_bad_page_raise_page_error`.
  - `test_scale_is_limited` (scale 0, negative or 10 is refused; 1.5 default, 3 maximum, so a hostile query string cannot allocate a huge bitmap).
  - `test_pdf_with_spaces_and_unicode_in_its_path_opens` (cross-platform path handling).
- [ ] **Step 2 to 5: red, minimum, green, full suite.**
- [ ] **Step 6: Commit** `feat: render PDF pages and compute highlight boxes in the table-cell frame`; progress entry.

---

### Task 6: The twin pane and the JSON pane

**Files:**
- Modify: `backend/bintanong_tools/prospectus_review_gui/render.py` (`twin_fragment`, `cells_fallback`, `course_json`, `load_evidence`)
- Test: `tests/test_review_gui_panes.py`

Behavior: `load_evidence(docling_json_path)` uses `loader.load_from_raw_json`; returns `None` plus a reason string when the file is missing or unreadable (never raises into the request). `twin_fragment(evidence, payload, pdf_sha256)` returns the twin HTML: `markup.render_prospectus_markup` with the leading `> ` notice lines removed and nothing else changed; computed once per session. `cells_fallback(course)` returns the course's own source cells as rows `{cell_id, row, col, text}` for when there is no evidence. `course_json(course, verification_row)` returns the course dict as the extractor wrote it, plus the flag list kept apart (a `"_review"` key would not be in the candidate, so it is returned beside, not inside).

- [ ] **Step 1: Write the failing tests.**
  - `test_twin_fragment_keeps_every_data_cell_id_of_the_course` (all `source_cell_ids` of a fixture course appear as `data-cell` attributes in the fragment).
  - `test_twin_fragment_drops_the_notice_but_nothing_else` (the fragment equals the renderer output minus the lines starting with `> `; table count unchanged).
  - `test_twin_fragment_carries_no_script_or_event_handler_for_hostile_cell_text` (a cell whose text is `<script>alert(1)</script>` and another with `"><img onerror=x>` come out escaped; assert no `<script` and no `onerror=` outside escaped text, using `html.parser`, not substring).
  - `test_twin_missing_docling_json_returns_none_and_reason`; `test_corrupt_docling_json_returns_none_and_reason`.
  - `test_cells_fallback_lists_only_the_courses_own_cells_with_their_ids`.
  - `test_course_json_is_the_candidate_course_unmodified` (deep-equal to the input; the returned object is a copy).
  - `test_course_json_for_huge_provenance_is_bounded` (an artificial course with 5,000 cells is returned with `source_cells` truncated and a `"truncated": N` marker, so one request cannot return megabytes; the first cells and the course's own role cells are kept).
  - `test_twin_page_numbers_match_pdf_pages` (the `data-page` of the course's code cell equals `provenance.page`).
- [ ] **Step 2 to 5: red, minimum, green, full suite.**
- [ ] **Step 6: Commit** `feat: serve the markup twin, the cell fallback and the course JSON for the review panes`; progress entry.

---

### Task 7: Session and API

**Files:**
- Create: `backend/bintanong_tools/prospectus_review_gui/session.py`, `app.py`
- Test: `tests/test_review_gui_session.py`, `tests/test_review_gui_api.py`

Behavior. `ReviewSession` is built by `open_session(candidate, identity, reviewer, review_dir, pdf_path=None, docling_json=None)`: loads the candidate (`fixer_cli.load_candidate`), runs `verify_candidate` with the PDF text when the PDF is at hand, calls `assert_outside_git` on the ledger path, computes the candidate hash (`sheet.candidate_sha256`), and holds one `threading.Lock` around every append (single process; a second GUI on the same ledger is not supported, see "Known limits"). Methods: `queue(mode)`, `question(qid)`, `answer(qid, answer, now=None)`, `state()` (`content_review_state` plus the three states and the stale/foreign/invalid counts), `materialise()`. After every answer the verification is **not** recomputed (the candidate is immutable); decided-ness is recomputed from the ledger.

Routes (all JSON unless noted): `GET /` (the page; embeds the token in a `<meta>`), `GET /static/{file}`, `GET /api/state`, `GET /api/queue?mode=attention|print`, `GET /api/question/{qid}` (question, course JSON, boxes, twin cell ids, warnings), `GET /api/page/{n}.png?scale=` (PNG), `GET /api/twin` (HTML fragment, cached), `POST /api/answer`, `POST /api/materialise`. Every response carries the CSP and `Cache-Control: no-store` (except the page PNG: `private, max-age=300`, since the PDF is immutable for the session). Middleware order: Host check, then (POST only) Origin and token check.

- [ ] **Step 1: Write the failing tests** (`fastapi.testclient.TestClient`, tmp directories outside the repository so the guard accepts them):
  - Session: `test_open_session_refuses_a_ledger_inside_the_repository` (`FixerError` from the shared guard; no file created), `test_open_session_accepts_a_review_dir_outside_git`, `test_session_reads_existing_ledger_and_marks_decided`, `test_answer_appends_one_line_and_never_rewrites_earlier_lines` (file bytes before are a prefix of the bytes after), `test_second_answer_for_same_course_is_a_new_line_and_wins`, `test_answer_with_error_writes_nothing`, `test_concurrent_answers_are_serialised` (16 threads each answering a different course; ledger has 16 valid lines, no interleaved line, `read_entries` yields no `_unreadable`), `test_state_counts_foreign_stale_and_invalid_entries` (a ledger seeded with an entry for another PDF hash, one with a changed old value and one corrupt line).
  - API security: `test_foreign_host_header_is_refused_403`, `test_localhost_and_127_0_0_1_hosts_are_accepted`, `test_post_without_token_is_403`, `test_post_with_wrong_token_is_403`, `test_post_with_foreign_origin_is_403`, `test_get_requests_need_no_token_but_do_need_a_good_host`, `test_csp_and_no_store_headers_on_every_response`, `test_token_differs_between_two_app_instances`.
  - API behavior: `test_api_answer_returns_updated_state_and_next_question`, `test_api_question_unknown_qid_is_404`, `test_api_page_png_scale_is_bounded_422`, `test_api_page_without_pdf_is_404_with_message`, `test_api_question_includes_boxes_and_warnings`, `test_api_error_messages_never_include_a_server_path` (a missing PDF names the file name, not its directory).
  - Safety: `test_raw_candidate_bytes_and_pdf_bytes_unchanged_after_a_session` (hash before and after a full run of answers and a materialise), `test_only_the_ledger_and_the_corrected_candidate_are_written` (directory listing of the candidate folder, the PDF folder and the review dir before and after: the only new files are `decision_ledger.jsonl` and, after materialise, `corrected_candidate.json`), `test_materialise_never_targets_the_raw_candidate` (`write_corrected(raw_candidate=...)` is passed), `test_materialise_runs_the_outside_git_guard`.
- [ ] **Step 2 to 5: red, minimum, green, full suite.** `create_app` takes the session and the token as arguments (no globals) so tests build many apps.
- [ ] **Step 6: Commit** `feat: add the local review session and its loopback-only API`; progress entry.

---

### Task 8: The page (three panes, keyboard, accessibility)

**Files:**
- Create: `backend/bintanong_tools/prospectus_review_gui/static/index.html`, `review.css`, `review.js`
- Test: `tests/test_review_gui_static.py`

Layout. A header (prospectus title, reviewer name, the three states as text badges with the words "not an approval", progress "decided N of M", queue mode toggle). Left: queue and section list (collapsible by section, health word beside each: clean, review, broken). Centre top: the question, its flags, its proposals as hints, the three answer controls, and the Other form (one labelled field per editable value, a required reason field, an inline error line). Centre: three panes in a resizable row, **PDF page** (image plus overlay boxes, zoom control), **Markup twin** (scrolls to and highlights the course's cells; the asked cell is marked stronger), **Extracted JSON** (the course, pretty-printed, flagged fields marked, `textContent` only). Footer: status line (aria-live) and the key help. Narrow windows stack the panes; nothing relies on colour alone (each highlight also has an outline style, each badge has a word).

- [ ] **Step 1: Write the failing tests** (Python only; the JavaScript is kept so small that its behavior is checked in the browser gate, but the static files are checked mechanically):
  - `test_no_external_url_in_any_static_asset` (D7: no `http://` or `https://` substring other than the XML namespace string inside an SVG, which is allow-listed by exact value).
  - `test_page_has_no_inline_script_style_or_event_handler_attribute` (parsed with `html.parser`; needed by the CSP).
  - `test_page_landmarks_and_headings` (one `h1`, a `main`, a `nav` for the queue, `header`, `footer`; a skip link as the first focusable element).
  - `test_every_form_control_has_an_accessible_name` (each `input`, `textarea`, `select`, `button` has a `label`, `aria-label` or text content; the answer options are a `fieldset` with a `legend`, native radio inputs).
  - `test_live_region_exists_for_status_and_errors` (`aria-live="polite"` for status, `role="alert"` for the inline validation message).
  - `test_images_and_overlays_have_text_alternatives` (the page image has an `alt` generated from the page number; overlays are `aria-hidden` because the same information is in the question text).
  - `test_css_defines_visible_focus_and_respects_reduced_motion` (a `:focus-visible` rule with an outline of at least 2px and a `prefers-reduced-motion` block; no `outline: none` without a replacement).
  - `test_css_colours_meet_contrast` (the colour tokens declared in `:root` are parsed and each foreground/background pair used for text is checked to be at least 4.5:1 with a 15-line luminance function in the test; a dark scheme under `prefers-color-scheme` is checked the same way).
  - `test_key_help_lists_every_bound_key` (the keys in `review.js`'s key map and the keys in the help list are the same set; read by regex from the two files).
  - `test_static_route_refuses_path_traversal` (`/static/..%2f..%2fsession.py` is 404).
- [ ] **Step 2 to 5: red, minimum, green, full suite.** The JavaScript does only: fetch and render, key map, overlay positioning from the server's fractions, scroll-to-cell in the twin, and posting the answer. It makes no decision about validity or order.
- [ ] **Step 6: Run the browser check once** (superpowers `browser-automation` skill or the Chrome DevTools tools against a running instance on a fixture): no console errors, no failed network requests, every key works (answer with `Y`, open Other with `O`, type, `Enter`, next with `J`), and tabbing reaches every control in a sensible order. Record what was seen in the progress entry.
- [ ] **Step 7: Commit** `feat: add the review page with three panes, keyboard answers and accessible controls`; progress entry.

---

### Task 9: Command line, startup guards, cross-platform behavior

**Files:**
- Create: `backend/bintanong_tools/prospectus_review_gui/cli.py`, `__main__.py`, `backend/bintanong_tools/prospectus_review.py`
- Modify: `backend/pyproject.toml` (the `review` extra, if Task 1 did not)
- Test: `tests/test_review_gui_cli.py`

Behavior. Arguments: `--candidate` (required), `--pdf`, `--pdf-sha256`, `--golden`, `--pdf-root` (all passed to `fixer_cli.resolve_identity`, so identity rules are identical to the sheet's), `--docling-json`, `--review-dir` (default `fixer_cli.default_review_dir`), `--reviewer` (default `resolve_reviewer`), `--port` (default 8765, `0` for any free port), `--no-open`. **No `--host`.** It binds `127.0.0.1`, prints the URL, opens the default browser unless `--no-open`, and stops on Ctrl+C. Exit codes as the fixer: 0 done, 2 cannot run (missing file, missing reviewer, unsafe folder, port in use).

- [ ] **Step 1: Write the failing tests.**
  - `test_help_runs_and_lists_no_host_option` (subprocess `--help`, exit 0; the text does not contain `--host`).
  - `test_host_option_is_rejected` (exit 2 from argparse).
  - `test_missing_candidate_exits_2_with_a_message`; `test_missing_reviewer_exits_2` (no `--reviewer`, `git config user.name` made empty through an environment override).
  - `test_unsafe_review_dir_exits_2_and_creates_nothing` (a path under the repository that is not git-ignored).
  - `test_identity_mismatch_exits_2` (`--pdf` whose hash differs from the candidate's recorded hash; message from `resolve_identity`).
  - `test_server_binds_loopback_only` (start the server on port 0 in a thread; the bound socket address is `127.0.0.1`; a connection to the machine's non-loopback address, when one exists, is refused; skipped with a stated reason when the machine has no other address).
  - `test_port_in_use_exits_2`.
  - `test_browser_opened_unless_no_open` (monkeypatch `webbrowser.open`; called once with the `http://127.0.0.1:<port>/` URL, never called with `--no-open`).
  - `test_console_output_is_safe_for_non_utf8_windows_consoles` (non-ASCII titles in the status line; stdout `reconfigure(errors="replace")` like `fixer_main`).
  - `test_paths_with_spaces_and_unicode_work_end_to_end` (candidate, PDF and review dir all under a folder named `Prospectus tèst folder`).
  - `test_no_posix_only_calls` (a source scan of the package for `os.fork`, `signal.SIGKILL`, `fcntl`, `os.getuid`, hard-coded `/` joins of paths, so a Windows-only or POSIX-only dependency fails the test on any OS).
- [ ] **Step 2 to 5: red, minimum, green, full suite.**
- [ ] **Step 6: Cross-platform note.** The suite runs on this Windows machine. State in the progress entry that Linux and macOS were **not** run, and which tests exist to catch the usual differences (path separators, console encoding, newline in the ledger: entries are written by `append_entries` with `newline="\n"`). If a Linux or macOS machine or CI runner becomes available, run the full suite there before the user's trial.
- [ ] **Step 7: Commit** `feat: add the review GUI command line (loopback only, same identity and folder guards as the fixer)`; progress entry.

---

### Task 10: Phase C hooks: the three states, prerequisite questions, `reviewed_empty`

**Depends on Phase C being merged.** If Task 1 found it is not, stop here and report; Tasks 1 to 9 stand alone.

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
- **Phase D to F.** None required. Phase D's safe-cache and Phase F's container/CLI work do not touch the GUI. If Phase E adds source locators for RAG, the GUI does not need them. If Phase F's container image is meant to run the GUI, that is a new decision (it would need a published port and a different bind address and is **out of scope** by D8).
- **Master plan.** Satisfies §7.1 step 7 (local researcher GUI; PDF page, reconstructed cells and extracted JSON together; accepted, corrected or unresolved decisions with reviewer, reason, source cell and page, PDF hash; raw extraction preserved; corrected candidate derived separately), §7.3 (deliverable: a local correction GUI, decision ledger and corrected candidate JSON), §4 last paragraph (local correction tooling in parallel with Phase 1; outputs remain candidates), §15 (kept separate from private-file review: no shared storage or code), §16.1 (required preparation tool, not a hosted dashboard) and §20 (no new top-level module is created in `backend/app/`; this lives with the tools).

## Known limits (state them in the decision record, do not hide them)

1. **One GUI per ledger.** A process lock serialises appends in one process; two GUIs (or a GUI and `fixer_cli apply`) on the same ledger at the same moment can interleave writes. `append_entries` repairs a missing final newline but is not a cross-process lock. Reviewers should not run two at once. A lock file is a candidate follow-up if the trial shows it happens.
2. **The reviewer name is whatever `--reviewer` or `git config user.name` says.** No authentication. The `entry_id` hash catches accidental edits, not forgery (the ledger module says so too).
3. **No highlight on rotated pages or when sizes disagree** (by design, D9). If many real pages are rotated, a follow-up adds rotation handling with a test PDF.
4. **PDF-text-only printed codes** (found by the PDF text layer, not by Docling) can be decided but do not gate `reviewed` (B2 D5).
5. **Linux and macOS are covered by portable code and tests, not yet by a run** (Task 9 step 6).
6. **The twin needs the raw Docling JSON.** Without it the middle pane is the cell list, which still names the cells but does not show the table.

## Hand-off

**What exists when this is done:** a command, `python -m backend.bintanong_tools.prospectus_review --candidate ... --pdf ...`, that opens a loopback-only page showing the PDF page with the asked cell boxed, the markup twin scrolled to the same cell, and the course JSON; asks one Yes / No / Other question at a time; appends every answer to the B2 ledger through the sheet's own entry builder; shows live content-review state; and rebuilds the corrected candidate on request. The B2 sheet remains the maintainer fallback and produces entries identical in shape.

**What the next person must know:**

- Never write a ledger entry from the GUI code directly; go through `answers.answer_to_entries`, which goes through `sheet.row_entries`. The equivalence tests exist to catch drift.
- Never add a `--host` option, an inline script, or a CDN link. Three tests fail if you do (CLI help, CSP/inline check, external-URL scan).
- The ledger and corrected candidate go outside Git; the guard is `fixer_cli.assert_outside_git`. Do not run the GUI with `--review-dir` pointing into the trial folders' existing `review\` folders unless the user asks.
- This is institutional prospectus review. It is not the student OCR photo review (§15), which is session-only and never touches the institutional knowledge base.
- Read `docs/decisions/prospectus-review-gui.md` and the "Review GUI" section of `plans/plan_current_progress/extractor_split_progress.md` before changing anything.

**Open items after this plan:** the lock-file question (limit 1); rotation handling if real pages need it; whether a later "add a missing course" action is wanted (B2 D8); running the suite on Linux and macOS; whether the hosted reviewer interface of §16.1 is ever needed (it would be a new plan with authentication).

## Self-review

- **Requirement coverage.** Local, not hosted: D8, Task 9. PDF page, twin and JSON side by side: Tasks 5, 6, 8. Question-style Yes / No / Other, one question per item, reference never pre-selected: D4, Tasks 3 and 4. "Other" validated by `ledger.correction_problem`: D6, Task 4. Answers through `ledger.make_entry` into the same JSONL, with reviewer, hash and locator, raw candidate untouched, corrected candidate separate: Tasks 2, 4, 7. Ledger fields code, title, term, units and prerequisites: Tasks 2 and 4 (and 10). Bulk confirm only without flags: D11, Tasks 3 and 4. Windows, Linux, macOS: Task 9. Outside-Git guard reused: Tasks 7 and 9. No heavy new dependency, tech choice as a decision row: D1, D2. pypdfium2 rendering and bbox highlight with TOPLEFT and page sizes: D9, Task 5. Sheet kept; identical entries proven by a test: Task 2 step 1 (golden), Task 4 equivalence tests, Task 11 step 5. Separate from OCR photo review: Scope section 1 and the hand-off.
- **Names used across tasks.** `row_entries`, `load_candidate` (Task 2); `Question`, `build_questions`, `order_queue`, `current_decision` (Task 3); `Answer`, `parse_typed_value`, `answer_to_entries` (Task 4); `bbox_fraction`, `boxes_for_question`, `PageRenderer`, `PageError` (Task 5); `load_evidence`, `twin_fragment`, `cells_fallback`, `course_json` (Task 6); `ReviewSession`, `open_session`, `create_app` (Task 7). Task 10 uses C's merged names as recorded in Task 1.
- **No placeholders.** Every task names its files, its tests by function name, its commands and its commit message. The two things that depend on code not yet merged (the exact names from B2 review fixes and from Phase C) are handled by Task 1 step 3, not left open.
