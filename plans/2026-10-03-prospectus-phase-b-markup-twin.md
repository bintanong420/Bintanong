# Prospectus Phase B: Markup Twin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task, with superpowers:test-driven-development inside each task. Steps use checkbox (`- [ ]`) syntax for tracking. Update `plans/plan_current_progress/extractor_split_progress.md` after every task commit (each task has a step for it).

**Status:** Written 3 October 2026 against `dev` at `8d26f18`. Phase B of `plans/2026-10-03-prospectus-extractor-package-split.md`. Part of the parallel, review-only prospectus workstream; it does not advance `plans/INDEX.md` and approves no curriculum, RAG, or Prolog release.

**Goal:** Add `prospectus_extractor/markup.py` and the CLI flag `--export-md`, so every extraction can write `<stem>_prospectus.md`: the Docling evidence laid out the way the printed PalSU prospectus looks (header text, then year banners spanning the width, two semesters side by side, `Total` rows, footnotes, elective lists), as Markdown with HTML `<table>` blocks. It is both machine-friendly (RAG, diffs, cell IDs) and the "reconstructed table" view the review GUI (draft Task 5) will show beside the PDF.

**Architecture:** One pure function, `render_prospectus_markup(evidence, payload, *, pdf_sha256=None) -> str`, reads the existing `ProspectusEvidence` (tables with spans and boxes, text items with page and box) and the audit status of the payload. It changes no extracted value and adds no payload key, so `SCHEMA_VERSION` stays `palsu-prospectus-v3.0`. Text and tables are interleaved by page position, not by Docling's internal order, because that is all the evidence carries and it is also what a future OCR path will provide.

**Tech Stack:** Python 3.13, stdlib `html`, pytest, `uv`. No new dependency.

**Base:** `dev` at `8d26f18`. **Branch to create:** `feature/prospectus-markup-twin`. Leave the dirty `.gitignore` and the untracked `plans/CODEX_HANDOFF_prospectus_extractor_phase2_2026-09-26.md` alone; never `git add -A` or `git add .`.

---

## Decisions needed before execution

The plan below assumes every recommendation. Steps that would change are named.

| # | Question | Options | Recommendation and why |
| --- | --- | --- | --- |
| D1 | How is non-table text written? | (a) HTML blocks (`<h2 data-item="text-1" data-page="1">…</h2>`, `<p …>`). (b) Markdown-native (`## …`, plain paragraphs) with a comment carrying the item ID. | (a). The only escaping needed is `html.escape`; with Markdown-native text, a line that starts with `#`, `1.` or `-` silently changes meaning, which would break "source text, never paraphrased". Item IDs and pages ride on the element, so the GUI can highlight them. Both render the same in VS Code. Changes Task 3 only. |
| D2 | Is the `.md` written when the audit is `error`? | (a) Always. (b) Only when not `error`, like `.pl` and `.jsonl`. | (a). The reviewer needs the reconstructed view most when the audit failed (38 of the 44 cached inputs). It carries `REVIEW REQUIRED` and no institutional facts, unlike Prolog and RAG. Changes Task 4 (move the write inside the `else`). |
| D3 | Header cells | (a) `<th>` for the column-header row and for year/semester banner cells; every other cell `<td>`. (b) All `<td>`. | (a). It is what the printed page shows as bold headers and it needs only existing helpers (`is_header_row`, `match_year_label`, `match_semester_labels`). The rule is deliberately cell-level (banner label AND `colspan >= 2`), because Docling sometimes glues a label into a course cell (BSCS row 3: `FIRST SEMESTER Discrete Structures 1 1`), which must stay a `<td>`. |
| D4 | Source hash in the status line | (a) Optional keyword `pdf_sha256`; shown as `not recorded` until Phase C/D passes it. (b) Compute SHA-256 in `process_prospectus` when the input is a PDF. | (a). The payload and `ProspectusEvidence` carry no PDF hash today (`build_payload` stores only `source_file` and `source_path`; the isolated batch computes `pdf_sha256` in its parent process at `prospectus_batch.py:59`, outside the child). Phase D owns the hash and the cache key; (b) would also be wrong for `_docling.json` inputs. |
| D5 | Cells whose rectangle collides with an earlier cell | (a) Keep the table valid: render the later cell after the table as `<p data-unplaced-cell="…">` with its text. (b) Emit it in the row anyway. | (a). 14 of the 44 cached files have overlapping cells (for example ABComm, BSEd-Math, BSTM). Emitting them in place shifts every following cell in that row and makes the view lie. Every cell ID still appears exactly once. |
| D6 | Reading order of text versus tables | (a) Sort by page, then vertical position, then left edge, with a 3-point same-line tolerance. (b) Add Docling's `body.children` order to `ProspectusEvidence`. | (a). Needs no change to `loader.py` or the evidence model, works on hand-built fixtures and on any future OCR source that gives boxes, and matches what a reader sees. Items without page or box (self-test fixtures) fall back to input order: texts, then tables. |
| D7 | `BatchConfig.write_md` default | (a) `True`, like `write_csv`, `write_pl`, `write_jsonl`. (b) `False`. | (a). Consistent with the sibling flags. Users of the in-process batch will see one more file per PDF; the isolated runner (`prospectus_batch.py`) passes no export flags and is unaffected. |

Not a decision, settled by YAGNI: **Docling's own `export_to_markdown()` is not added as a side output.** `evidence_adapter` already calls it into `evidence.markdown` (`loader.py:200-203`) for metadata parsing, so it is available in memory; written to disk it would flatten merged cells into repeated text, which is exactly what this twin exists to avoid. `--dump-grid` already writes the flattened grid for debugging. Revisit only if a reviewer asks to diff Docling's Markdown.

## What a real prospectus looks like as evidence (inspected 3 October 2026)

Cached files read with `load_document` / `evidence_adapter` from `task2b_standing_isolated_2026-09-29` (inspection scripts lived in `$env:TEMP` and are not in the repo). These facts drive the layout rules:

- **One main table per curriculum page, plus a tiny footer table.** BS Computer Science (new 2025-2026): table 0 is 43 rows by 8 columns (two semesters side by side, four columns each: Course Code, Course Title, Unit, Pre- requisite), table 1 is a 3x1 "Legend" box. Architecture (`BSA-for-student-new-version`): table 0 is 48x10 (a leading `Grade` column in each half), table 1 is 1x4 (the `Total no. of units` row). Multi-page: BS Accountancy has tables on pages 2 and 3, BS Nursing on pages 1 and 2, BSBA-MM has five tables on one page.
- **Merged banners are single cells.** BSCS `t0-c8` is `FIRST YEAR`, rows 1-2, columns 0-8 (colspan 8). `t0-c10` is `SECOND SEMESTER`, columns 0-8. Architecture `t0-c10` is `FIRST YEAR FIRST SEMESTER SECOND SEMESTER` spanning columns 1-10.
- **Docling is not always right, and the twin must show that, not hide it.** BSCS `t0-c9` is `FIRST SEMESTER Discrete Structures 1 1` (a banner word glued into a course title); Architecture `t0-c79` is `SECOND AD-2/L, TOA-2,` (a year word glued into a prerequisite). The renderer reproduces cell text exactly; it must never repair it.
- **Cell order is not row-major** (BSCS `c10` comes before `c9`), so the renderer sorts.
- **Empty grid positions are common.** In the 44 files, 23 to 148 of the grid positions per main table are covered by no cell (empty prerequisite and grade columns). They need empty `<td>` placeholders or the columns shift.
- **Overlapping cells exist** (14 of 44 files; up to 3 collisions in one table).
- **Every table cell and text item has page and box** (0 cells without a box, 0 text items without a page in all 44 files). Boxes keep Docling's native orientation (`coord_origin: BOTTOMLEFT`, top greater than bottom; the evidence adapter drops the `coord_origin` label but keeps the numbers). One existing test fixture uses `TOPLEFT`, so the renderer decides orientation from the numbers.
- **Text items present:** `section_header` (`VIII. PROPOSED PROGRAM OF STUDY`, program title, university lines), `text` (`Effective SY 2018-2019*`, `Name of Student: ____`), `footnote` and `list_item` (elective lists such as `CS Elect 4/La. Mathematical Methods…`), `page_footer` (`50`). There is no separate "header block" object: the header is simply the text items above the first table.
- **No PDF hash anywhere in payload or evidence** (see D4). Payload audit status is `payload["audit"]["status"]` in `ok | warn | error`.

## Layout rules (what the renderer emits)

1. Line 1: `<!-- extraction_audit: STATUS | VERDICT | pdf_sha256: HASH -->`. `VERDICT` is `REVIEW REQUIRED` when STATUS is not `ok`, else `content_review: pending`. `HASH` is the 64-hex value when passed, else `not recorded`. Line 2: `<!-- markup: palsu-prospectus-markup-v1 -->`. Then a visible blockquote saying this is a reconstruction of Docling evidence for comparison with the PDF, and, when not `ok`, starting with `**REVIEW REQUIRED**`.
2. Blocks follow the page top to bottom, left to right on one printed line: text items as `<h1>`/`<h2>`/`<p>` (`title`, `section_header`, everything else), with `<small>` inside for `footnote`, `page_footer`, `page_header`. Each carries `data-item`, `data-label`, `data-page`.
3. Each table is `<table data-table="N" data-page="P" data-rows="R" data-cols="C">` with one `<tr>` per grid row, no blank lines inside (a blank line would end the HTML block in Markdown).
4. One `<td>`/`<th>` per `NormalizedCell`, with `data-cell="t0-c12"`, `data-page`, `colspan`, `rowspan` (only when greater than 1, clamped to the table size). Text is `cell.text` HTML-escaped.
5. A grid position covered by no cell becomes `<td data-gap></td>`. It has no `data-cell`, so a consumer can drop all gaps with one filter and no evidence is invented.
6. A cell that collides with an earlier cell is not placed in the grid; it follows the table as `<p data-unplaced-cell="ID" data-page="P">text</p>`.
7. When the page changes between consecutive blocks, `<!-- page N -->` and `<hr>` precede the block. The first block gets no marker.
8. Output is deterministic: cells sorted by `(row_start, col_start, cell_id)`, blocks by `(page, y, left, kind, id)`, UTF-8, `\n` newlines, trailing newline, no timestamps.

## File structure

All under `backend/bintanong_tools/prospectus_extractor/` unless noted.

| File | Change | Responsibility |
| --- | --- | --- |
| `markup.py` | Create | `render_prospectus_markup` and private helpers. Imports only `evidence`, `layout`, `text`. |
| `pipeline.py` | Modify | `process_prospectus(..., export_md=False)`; write `<base>_prospectus.md`; remove stale `.md`. |
| `cli.py` | Modify | `--export-md`; `--export-all` includes it; pass to batch and single-file paths. |
| `batch.py` | Modify | `BatchConfig.write_md`; `run_batch` passes `export_md`. |
| `tui.py` | Modify | Show and ask the new setting; pass it in single-file mode. |
| `tests/test_prospectus_markup.py` | Create | Renderer, pipeline, CLI, and batch tests. |
| `tests/test_prospectus_split_equivalence.py` | Delete (first commit, if it still exists) | Phase A gate; asserts nothing changed. |
| `scripts/prospectus_course_compare.py` | Create | Field-level old-versus-new comparer (also checks the markup invariants). Reusable by Phases C-F. |
| `docs/decisions/prospectus-markup-twin.md` | Create | Decision record with the evidence. |
| `plans/plan_current_progress/extractor_split_progress.md` | Modify | New "Phase B" section, updated after each task. |

Unchanged on purpose: `common.py` (`SCHEMA_VERSION`), `loader.py`, `evidence.py`, `selftest.py` (still 80/80), `prospectus_batch.py` (the isolated runner passes no export flags).

## Commands used throughout

```
# Full suite (Phase A baseline: 36 passed, 13 subtests passed)
uv run --project backend --extra tools --extra dev --with fastapi==0.141.1 python -m pytest -q tests

# Self-test (baseline 80/80)
uv run --project backend --extra tools --extra dev python -m backend.bintanong_tools.prospectus_extractor --self-test
```

`$GOLDEN` is `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\docling_jsonified_output\task2b_standing_isolated_2026-09-29` (44 `*_docling.json`, outside Git). `$MAP` is `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\PalSU Undergraduate Prospectus Website Dump\Tiniguiban - Main\palsu_main_undergrad_program_college_meaning.md`.

Commit messages in this phase end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Stage by explicit path.

---

### Task 1: Start check, branch, delete the Phase A gate

**Files:**
- Delete: `tests/test_prospectus_split_equivalence.py` (only if it still exists)
- Modify: `plans/plan_current_progress/extractor_split_progress.md`

- [ ] **Step 1: Re-read the files this phase touches and confirm the line references**

Line references in this plan are as of `8d26f18`. Open these and confirm; if an earlier merge moved anything, write the new numbers into the progress file and use them from here on.

| File | What to find | Line at `8d26f18` |
| --- | --- | --- |
| `pipeline.py` | `def process_prospectus(` | 174 (last parameter `quiet` at 185) |
| `pipeline.py` | stale-output loop `for stale in (` | 206-213 |
| `pipeline.py` | `essentials_path.write_text(` block ends | 237 |
| `pipeline.py` | `if payload["audit"]["status"] == "error":` | 239 |
| `cli.py` | `--export-csv` / `--export-all` arguments | 38-39 |
| `cli.py` | `export_csv = args.export_csv or args.export_all` | 73 |
| `cli.py` | `BatchConfig(` and `process_prospectus(` calls | 92-104, 116-125 |
| `batch.py` | `write_jsonl: bool = True` | 43 |
| `batch.py` | `export_csv=config.write_csv,` | 207 |
| `tui.py` | config table row, ask prompts, `single_file` call | 89, 196-198, 271-276 |
| `loader.py` | `markdown = docling_document.export_to_markdown()` | 200-203 |

Run: `git branch --show-current; git log --oneline -1; git status --short`
Expected: branch `dev`, last commit `8d26f18` (or a later merge of the same phase chain), status shows only ` M .gitignore` and `?? plans/CODEX_HANDOFF_prospectus_extractor_phase2_2026-09-26.md`. If anything else is dirty, stop and report.

- [ ] **Step 2: Create the branch and confirm the baseline**

```
git switch -c feature/prospectus-markup-twin
uv run --project backend --extra tools --extra dev --with fastapi==0.141.1 python -m pytest -q tests
uv run --project backend --extra tools --extra dev python -m backend.bintanong_tools.prospectus_extractor --self-test
```

Expected: `36 passed` with 13 subtests passed, and `80/80`. Anything else: stop and report.

- [ ] **Step 3: Delete the Phase A gate (conditional)**

If `tests/test_prospectus_split_equivalence.py` exists (it does at `8d26f18`; a Phase A close-out may already have removed it), delete it. From this phase on the package may differ from the monolith.

```
git rm tests/test_prospectus_split_equivalence.py
uv run --project backend --extra tools --extra dev --with fastapi==0.141.1 python -m pytest -q tests
```

Expected: `34 passed` (36 minus its 2 tests), 13 subtests passed.

- [ ] **Step 4: Append the Phase B section to the progress file**

Add at the end of `plans/plan_current_progress/extractor_split_progress.md`:

```
## Phase B: markup twin (branch feature/prospectus-markup-twin)

Plan: plans/2026-10-03-prospectus-phase-b-markup-twin.md. Decisions D1-D7 in the plan assumed as recommended unless noted here.

| Task | Status | Commit | Evidence |
| --- | --- | --- | --- |
| 1. Start check, branch, delete Phase A gate | done | see git log | baseline 36 passed + 13 subtests, 80/80; 34 passed after deleting the gate |
| 2. Table renderer | pending | | |
| 3. Header, text blocks, reading order, page breaks | pending | | |
| 4. Pipeline, CLI, batch, TUI wiring | pending | | |
| 5. Course-field regression on 44 inputs | pending | | |
| 6. Visual check against the PDFs | pending | | |
| 7. Decision record, Codex gate | pending | | |

### Phase B log

- 2026-10-03: Task 1 done. Line references re-read: (write "unchanged" or the new numbers).
```

- [ ] **Step 5: Commit**

```
git add plans/plan_current_progress/extractor_split_progress.md
git commit -m "test: drop the Phase A equivalence gate before the markup twin" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

(`git rm` already staged the deletion; `git status --short` must show only the deletion and the progress file staged.)

---

### Task 2: Table renderer (spans, gaps, escaping, unplaced cells)

**Files:**
- Create: `backend/bintanong_tools/prospectus_extractor/markup.py`
- Create: `tests/test_prospectus_markup.py`

- [ ] **Step 1: Write the failing tests**

```python
"""The markup twin: Docling evidence laid out as the printed prospectus reads."""

from __future__ import annotations

import re

import pytest

from backend.bintanong_tools.prospectus_extractor.evidence import (
    NormalizedCell,
    NormalizedTable,
    ProspectusEvidence,
    SourceBBox,
)
from backend.bintanong_tools.prospectus_extractor.markup import render_prospectus_markup
from backend.bintanong_tools.prospectus_extractor.selftest import cs_fixture_grid, fixture_document

OK = {"audit": {"status": "ok"}}
ERROR = {"audit": {"status": "error"}}


def box(left: float, top: float, origin: str = "BL", height: float = 9.0, width: float = 100.0):
    """[l, t, r, b] for a box whose top edge is `top` points down from the page top in the BL frame.

    BL (Docling BOTTOMLEFT): y grows upward, so top > bottom.
    TL (TOPLEFT): y grows downward, so top < bottom.
    `top` is always given in the BL frame; the TL frame mirrors it on a 1000-point page.
    """
    if origin == "BL":
        return [left, top, left + width, top - height]
    return [left, 1000.0 - top, left + width, 1000.0 - top + height]


def make_cell(index, r0, r1, c0, c1, text, *, table=0, page=1, top=700.0, origin="BL"):
    left, t, right, bottom = box(10.0 * c0, top, origin, width=10.0 * (c1 - c0))
    return NormalizedCell(
        f"t{table}-c{index}", table, text, text, r0, r1, c0, c1, SourceBBox(page, left, t, right, bottom)
    )


def make_table(rows, cols, cells, table=0):
    return NormalizedTable(table, rows, cols, list(cells))


def evidence(tables, texts=()):
    return ProspectusEvidence(tables=list(tables), text_items=list(texts), source_kind="test")


def text_item(index, label, text, *, page=1, top=800.0, left=40.0, origin="BL"):
    return {
        "item_id": f"text-{index}",
        "label": label,
        "text": text,
        "page": page,
        "bbox": box(left, top, origin),
    }


def rows_of(html: str) -> list[str]:
    return re.findall(r"<tr>.*?</tr>", html)


def row_width(row: str) -> int:
    width = 0
    for tag in re.findall(r"<t[dh][^>]*>", row):
        span = re.search(r'colspan="(\d+)"', tag)
        width += int(span.group(1)) if span else 1
    return width


def banner_table():
    return make_table(
        4,
        4,
        [
            make_cell(0, 0, 1, 0, 4, "FIRST YEAR", top=700),
            make_cell(1, 1, 2, 0, 2, "FIRST SEMESTER", top=690),
            make_cell(2, 1, 2, 2, 4, "SECOND SEMESTER", top=690),
            make_cell(3, 2, 3, 0, 1, "Course Code", top=680),
            make_cell(4, 2, 3, 1, 2, "Course Title", top=680),
            make_cell(5, 2, 3, 2, 3, "Course Code", top=680),
            make_cell(6, 2, 3, 3, 4, "Course Title", top=680),
            make_cell(7, 3, 4, 0, 1, "CS 1", top=670),
            make_cell(8, 3, 4, 1, 2, "Discrete Structures 1", top=670),
            make_cell(9, 3, 4, 2, 3, "CS 2", top=670),
            make_cell(10, 3, 4, 3, 4, "Discrete Structures 2", top=670),
        ],
    )


def test_merged_banner_is_one_cell_with_its_real_span():
    html = render_prospectus_markup(evidence([banner_table()]), OK)
    assert html.count("FIRST YEAR") == 1
    assert '<th data-cell="t0-c0" data-page="1" colspan="4">FIRST YEAR</th>' in html


def test_both_semesters_share_one_row_and_headers_are_th():
    html = render_prospectus_markup(evidence([banner_table()]), OK)
    rows = rows_of(html)
    assert "FIRST SEMESTER" in rows[1] and "SECOND SEMESTER" in rows[1]
    assert '<th data-cell="t0-c1" data-page="1" colspan="2">FIRST SEMESTER</th>' in rows[1]
    assert all("<th " in cell for cell in re.findall(r"<t[dh] [^>]*>Course (?:Code|Title)", rows[2]))
    assert '<td data-cell="t0-c7" data-page="1">CS 1</td>' in rows[3]


def test_a_banner_word_inside_a_course_cell_stays_a_td():
    table = make_table(1, 2, [make_cell(0, 0, 1, 0, 2, "FIRST SEMESTER Discrete Structures 1 1")])
    # colspan 2 and a semester label would make it a banner; a one-column glued cell must not
    glued = make_table(1, 2, [make_cell(0, 0, 1, 0, 1, "FIRST SEMESTER Discrete Structures 1 1")])
    assert "<td " in render_prospectus_markup(evidence([glued]), OK)
    assert "<th " not in render_prospectus_markup(evidence([glued]), OK)
    assert "<th " in render_prospectus_markup(evidence([table]), OK)


def test_empty_grid_positions_become_gap_cells_and_columns_line_up():
    table = make_table(
        2,
        3,
        [
            make_cell(0, 0, 1, 0, 1, "A"),
            make_cell(1, 0, 1, 2, 3, "B"),
            make_cell(2, 1, 2, 0, 2, "C"),
        ],
    )
    html = render_prospectus_markup(evidence([table]), OK)
    assert html.count("<td data-gap></td>") == 2  # (0,1) and (1,2)
    assert [row_width(row) for row in rows_of(html)] == [3, 3]
    assert "data-gap" not in "".join(re.findall(r"<td data-cell[^>]*>", html))


def test_rowspan_hides_the_covered_position_but_gaps_still_line_up():
    table = make_table(
        2,
        2,
        [make_cell(0, 0, 2, 0, 1, "A"), make_cell(1, 0, 1, 1, 2, "B")],
    )
    rows = rows_of(render_prospectus_markup(evidence([table]), OK))
    assert 'rowspan="2"' in rows[0]
    assert rows[1] == "<tr><td data-gap></td></tr>"


def test_cell_text_is_html_escaped_never_interpreted():
    table = make_table(1, 1, [make_cell(0, 0, 1, 0, 1, 'A & B <script>alert("x")</script>')])
    html = render_prospectus_markup(evidence([table]), OK)
    assert "<script>" not in html
    assert "A &amp; B &lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;" in html


def test_colliding_cell_is_listed_after_the_table_not_placed():
    table = make_table(
        1,
        3,
        [make_cell(0, 0, 1, 0, 2, "X"), make_cell(1, 0, 1, 1, 3, "Y")],
    )
    html = render_prospectus_markup(evidence([table]), OK)
    assert '<td data-cell="t0-c0"' in html
    assert 'data-cell="t0-c1"' not in html
    assert '<p data-unplaced-cell="t0-c1" data-page="1">Y</p>' in html
    assert html.index("</table>") < html.index("data-unplaced-cell")
    assert [row_width(row) for row in rows_of(html)] == [3]  # X spans 2, one gap, no Y


def test_every_cell_id_appears_exactly_once_for_the_cs_fixture():
    document = fixture_document(cs_fixture_grid(), [("text", "Effective SY 2025-2026")])
    html = render_prospectus_markup(document, OK)
    ids = re.findall(r'data-(?:unplaced-)?cell="([^"]+)"', html)
    assert sorted(ids) == sorted(document.all_cells())
    assert len(ids) == len(set(ids))
    assert re.search(r'<th data-cell="t0-c\d+" colspan="8">FIRST YEAR</th>', html)
    assert any("FIRST SEMESTER" in row and "SECOND SEMESTER" in row for row in rows_of(html))
```

- [ ] **Step 2: Run and confirm the right failure**

Run: `uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_markup.py`
Expected: 1 error at collection, `ModuleNotFoundError: No module named 'backend.bintanong_tools.prospectus_extractor.markup'`. It must not be a syntax error in the test file.

- [ ] **Step 3: Write `markup.py` with the table renderer and a tables-only entry point**

```python
"""Markup twin: Docling evidence laid out the way the printed prospectus reads."""

from __future__ import annotations

from html import escape
from typing import Any
from typing import Mapping

from .evidence import NormalizedCell, NormalizedTable, ProspectusEvidence, project_table_to_grid
from .layout import is_header_row
from .text import match_semester_labels, match_year_label

MARKUP_VERSION = "palsu-prospectus-markup-v1"


def _esc(value: Any) -> str:
    return escape(str(value), quote=True)


def _table_page(table: NormalizedTable) -> int | None:
    pages = [c.bbox.page for c in table.cells if c.bbox is not None and c.bbox.page is not None]
    return min(pages) if pages else None


def _layout_cells(table: NormalizedTable):
    """Split cells into placed (own a free rectangle) and unplaced (collide or fall outside).

    Returns (placed, unplaced, occupied) where occupied is the set of covered (row, col).
    """
    occupied: set[tuple[int, int]] = set()
    placed: list[NormalizedCell] = []
    unplaced: list[NormalizedCell] = []
    for cell in sorted(table.cells, key=lambda c: (c.row_start, c.col_start, c.cell_id)):
        spots = {
            (row, col)
            for row in range(cell.row_start, min(cell.row_end, table.num_rows))
            for col in range(cell.col_start, min(cell.col_end, table.num_cols))
        }
        if not spots or spots & occupied:
            unplaced.append(cell)
        else:
            occupied |= spots
            placed.append(cell)
    return placed, unplaced, occupied


def _is_header_cell(cell: NormalizedCell, header_rows: set[int]) -> bool:
    if cell.row_start in header_rows:
        return True
    # A banner is a label that spans columns; a label glued into a one-column cell is not one.
    return cell.col_span >= 2 and bool(match_year_label(cell.text) or match_semester_labels(cell.text))


def _page_attr(page: int | None) -> str:
    return f' data-page="{page}"' if page is not None else ""


def _render_cell(cell: NormalizedCell, table: NormalizedTable, header_rows: set[int]) -> str:
    tag = "th" if _is_header_cell(cell, header_rows) else "td"
    page = cell.bbox.page if cell.bbox is not None else None
    cols = min(cell.col_end, table.num_cols) - cell.col_start
    rows = min(cell.row_end, table.num_rows) - cell.row_start
    spans = (f' colspan="{cols}"' if cols > 1 else "") + (f' rowspan="{rows}"' if rows > 1 else "")
    return f'<{tag} data-cell="{_esc(cell.cell_id)}"{_page_attr(page)}{spans}>{_esc(cell.text)}</{tag}>'


def _render_table(table: NormalizedTable) -> str:
    placed, unplaced, occupied = _layout_cells(table)
    grid = project_table_to_grid(table)
    header_rows = {index for index, row in enumerate(grid) if is_header_row(row)}
    starts = {(cell.row_start, cell.col_start): cell for cell in placed}
    lines = [
        f'<table data-table="{table.table_index}"{_page_attr(_table_page(table))}'
        f' data-rows="{table.num_rows}" data-cols="{table.num_cols}">'
    ]
    for row in range(table.num_rows):
        parts = []
        for col in range(table.num_cols):
            cell = starts.get((row, col))
            if cell is not None:
                parts.append(_render_cell(cell, table, header_rows))
            elif (row, col) not in occupied:
                parts.append("<td data-gap></td>")  # no evidence here; keeps the columns aligned
        lines.append("  <tr>" + "".join(parts) + "</tr>")
    lines.append("</table>")
    for cell in unplaced:
        page = cell.bbox.page if cell.bbox is not None else None
        lines.append(f'<p data-unplaced-cell="{_esc(cell.cell_id)}"{_page_attr(page)}>{_esc(cell.text)}</p>')
    return "\n".join(lines)


def render_prospectus_markup(
    evidence: ProspectusEvidence, payload: Mapping[str, Any], *, pdf_sha256: str | None = None
) -> str:
    return "\n\n".join(_render_table(table) for table in evidence.tables) + "\n"
```

- [ ] **Step 4: Run and confirm green**

Run: `uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_markup.py`
Expected: `8 passed`. If `test_both_semesters_share_one_row_and_headers_are_th` fails on the `Course Code` header check, read `layout.classify_header_cell` and report: do not loosen the assertion, because it is the proof that header rows become `<th>`.

- [ ] **Step 5: Run the whole suite**

Run the full-suite command. Expected: `42 passed`, 13 subtests passed.

- [ ] **Step 6: Record progress and commit**

Update the Task 2 row in the progress file (status done, counts observed, anything surprising).

```
git add backend/bintanong_tools/prospectus_extractor/markup.py tests/test_prospectus_markup.py plans/plan_current_progress/extractor_split_progress.md
git commit -m "feat: render Docling tables as HTML tables with real spans, gaps and cell IDs" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: Status line, text blocks, reading order, page breaks

**Files:**
- Modify: `backend/bintanong_tools/prospectus_extractor/markup.py`
- Modify: `tests/test_prospectus_markup.py`

- [ ] **Step 1: Append the failing tests to `tests/test_prospectus_markup.py`**

```python
def first_line(markup: str) -> str:
    return markup.splitlines()[0]


def test_error_and_warn_audits_are_flagged_review_required_on_line_one():
    for status in ("error", "warn"):
        line = first_line(render_prospectus_markup(evidence([banner_table()]), {"audit": {"status": status}}))
        assert line == f"<!-- extraction_audit: {status} | REVIEW REQUIRED | pdf_sha256: not recorded -->"


def test_missing_audit_is_treated_as_review_required():
    line = first_line(render_prospectus_markup(evidence([banner_table()]), {}))
    assert line == "<!-- extraction_audit: unknown | REVIEW REQUIRED | pdf_sha256: not recorded -->"


def test_ok_audit_is_still_only_a_pending_candidate_and_shows_a_given_hash():
    digest = "ab" * 32
    line = first_line(render_prospectus_markup(evidence([banner_table()]), OK, pdf_sha256=digest))
    assert line == f"<!-- extraction_audit: ok | content_review: pending | pdf_sha256: {digest} -->"
    assert "REVIEW REQUIRED" not in line


def test_status_comment_cannot_be_broken_out_of():
    line = first_line(render_prospectus_markup(evidence([]), {"audit": {"status": "x --> <b>"}}))
    assert line.count("-->") == 1 and line.endswith("-->") and "<b>" not in line


@pytest.mark.parametrize("origin", ["BL", "TL"])
def test_blocks_follow_the_page_top_to_bottom_in_either_coordinate_frame(origin):
    table = make_table(
        2,
        2,
        [
            make_cell(0, 0, 1, 0, 1, "CS 1", top=700, origin=origin),
            make_cell(1, 1, 2, 0, 1, "CS 2", top=690, origin=origin),
        ],
    )
    texts = [  # deliberately scrambled
        text_item(3, "footnote", "CS Elect 4/La. Mathematical Methods", top=120, origin=origin),
        text_item(0, "section_header", "PROPOSED PROGRAM OF STUDY", top=800, origin=origin),
        text_item(4, "page_footer", "50", top=50, origin=origin),
        text_item(1, "text", "Effective SY 2025-2026", top=790, origin=origin),
    ]
    html = render_prospectus_markup(evidence([table], texts), OK)
    order = [
        html.index("PROPOSED PROGRAM OF STUDY"),
        html.index("Effective SY 2025-2026"),
        html.index("<table"),
        html.index("CS Elect 4/La."),
        html.index(">50<"),
    ]
    assert order == sorted(order)
    assert '<h2 data-item="text-0" data-label="section_header" data-page="1">PROPOSED PROGRAM OF STUDY</h2>' in html
    assert '<p data-item="text-3" data-label="footnote" data-page="1"><small>CS Elect 4/La. Mathematical Methods</small></p>' in html


def test_items_on_one_printed_line_read_left_to_right_despite_tiny_height_differences():
    right = text_item(0, "footnote", "RIGHT column", top=200.0, left=262.0)
    left = text_item(1, "footnote", "LEFT column", top=199.4, left=57.0)  # 0.6 pt lower, listed second
    html = render_prospectus_markup(evidence([], [right, left]), OK)
    assert html.index("LEFT column") < html.index("RIGHT column")


def test_each_text_item_appears_once_and_is_escaped():
    texts = [text_item(0, "text", "Name of Student: ____ & ID <No.>")]
    html = render_prospectus_markup(evidence([], texts), OK)
    assert html.count('data-item="text-0"') == 1
    assert "Name of Student: ____ &amp; ID &lt;No.&gt;" in html


def test_page_change_inserts_one_marker_and_the_first_page_gets_none():
    page2 = make_table(1, 1, [make_cell(0, 0, 1, 0, 1, "A", page=2)], table=0)
    page3 = make_table(1, 1, [make_cell(0, 0, 1, 0, 1, "B", page=3, table=1)], table=1)
    header = text_item(0, "section_header", "TITLE", page=2, top=800)
    html = render_prospectus_markup(evidence([page3, page2], [header]), OK)
    assert html.count("<!-- page 3 -->\n<hr>") == 1
    assert "<!-- page 2 -->" not in html
    assert html.index('data-table="0"') < html.index("<!-- page 3 -->") < html.index('data-table="1"')


def test_items_without_a_position_keep_input_order_texts_then_tables():
    document = fixture_document(cs_fixture_grid(), [("section_header", "PROGRAM OF STUDY"), ("text", "Effective SY")])
    html = render_prospectus_markup(document, OK)
    assert html.index("PROGRAM OF STUDY") < html.index("Effective SY") < html.index("<table")


def test_output_is_deterministic_and_independent_of_input_order():
    table = banner_table()
    texts = [text_item(0, "section_header", "TITLE", top=800), text_item(1, "footnote", "NOTE", top=100)]
    first = render_prospectus_markup(evidence([table], texts), ERROR)
    again = render_prospectus_markup(evidence([banner_table()], list(texts)), ERROR)
    shuffled = make_table(table.num_rows, table.num_cols, reversed(table.cells))
    reordered = render_prospectus_markup(evidence([shuffled], list(reversed(texts))), ERROR)
    assert first == again == reordered
    assert first.endswith("\n") and "\r" not in first


def test_non_ok_audit_gets_a_visible_warning_and_ok_does_not_claim_approval():
    flagged = render_prospectus_markup(evidence([banner_table()]), ERROR)
    assert "> **REVIEW REQUIRED**" in flagged
    calm = render_prospectus_markup(evidence([banner_table()]), OK)
    assert "REVIEW REQUIRED" not in calm
    assert "not an approved curriculum" in calm
```

- [ ] **Step 2: Run and confirm they fail for the right reasons**

Run: `uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_markup.py`
Expected: the 8 Task 2 tests pass; the 12 new tests fail (the first line is `<table …>`, no text blocks, no markers). Examples: `test_error_and_warn…` fails with an assertion on the first line; `test_blocks_follow…` fails with `ValueError: substring not found`. A failure that is an `ImportError` or `NameError` is a test typo; fix the test.

- [ ] **Step 3: Replace the tail of `markup.py`**

Add these module-level names under `MARKUP_VERSION`:

```python
LINE_TOLERANCE = 3.0  # points: text whose tops differ by less than this shares a printed line
_HEADING_TAG = {"title": "h1", "section_header": "h2"}
_SMALL_LABELS = {"footnote", "page_footer", "page_header"}
```

Replace the existing `render_prospectus_markup` (the last function) with all of the following. Keep `_esc`, `_table_page`, `_layout_cells`, `_is_header_cell`, `_page_attr`, `_render_cell`, `_render_table` exactly as in Task 2.

```python
def _y_down(top: float, bottom: float) -> float:
    """Distance down the page. The evidence keeps Docling's native frame without its
    coord_origin label: BOTTOMLEFT has top >= bottom (y grows upward), TOPLEFT the reverse."""
    return -top if top >= bottom else top


def _text_position(item: Mapping[str, Any]) -> tuple[int, float, float] | None:
    bbox = item.get("bbox")
    if item.get("page") is None or not bbox:
        return None
    left, top, _right, bottom = bbox
    return (int(item["page"]), _y_down(top, bottom), float(left))


def _table_position(table: NormalizedTable) -> tuple[int, float, float] | None:
    spots = [
        (int(c.bbox.page), _y_down(c.bbox.top, c.bbox.bottom), float(c.bbox.left))
        for c in table.cells
        if c.bbox is not None and c.bbox.is_complete() and c.bbox.page is not None
    ]
    return min(spots) if spots else None


def _reading_order(evidence: ProspectusEvidence) -> list[tuple[str, Any]]:
    """Text items and tables in page order. Entries are ("text", item) or ("table", table)."""
    placed: list[tuple[tuple[int, float, float], str, Any]] = []
    loose_texts: list[tuple[str, Any]] = []
    loose_tables: list[tuple[str, Any]] = []
    for item in evidence.text_items:
        position = _text_position(item)
        if position is None:
            loose_texts.append(("text", item))
        else:
            placed.append((position, "text", item))
    for table in evidence.tables:
        position = _table_position(table)
        if position is None:
            loose_tables.append(("table", table))
        else:
            placed.append((position, "table", table))

    def ident(entry) -> str:
        _position, kind, obj = entry
        return f"{obj.table_index:08d}" if kind == "table" else str(obj.get("item_id", ""))

    placed.sort(key=lambda entry: (entry[0], entry[1], ident(entry)))
    ordered: list[tuple[str, Any]] = []
    line: list[tuple[tuple[int, float, float], str, Any]] = []

    def flush() -> None:
        for _position, kind, obj in sorted(line, key=lambda e: (e[0][2], ident(e))):
            ordered.append((kind, obj))
        line.clear()

    for entry in placed:
        position, kind, obj = entry
        if kind != "text":
            flush()
            ordered.append((kind, obj))
            continue
        if line and (position[0] != line[0][0][0] or position[1] - line[0][0][1] > LINE_TOLERANCE):
            flush()
        line.append(entry)
    flush()
    return ordered + loose_texts + loose_tables


def _render_text(item: Mapping[str, Any]) -> str:
    label = str(item.get("label", "text"))
    tag = _HEADING_TAG.get(label, "p")
    body = _esc(item.get("text", ""))
    if label in _SMALL_LABELS:
        body = f"<small>{body}</small>"
    page = item.get("page")
    return (
        f'<{tag} data-item="{_esc(item.get("item_id", ""))}" data-label="{_esc(label)}"'
        f"{_page_attr(page)}>{body}</{tag}>"
    )


def _comment_text(value: Any) -> str:
    """Text safe inside an HTML comment: no markup, and no `--`."""
    return _esc(value).replace("--", "- -")


def _block_page(kind: str, obj: Any) -> int | None:
    return _table_page(obj) if kind == "table" else obj.get("page")


def render_prospectus_markup(
    evidence: ProspectusEvidence, payload: Mapping[str, Any], *, pdf_sha256: str | None = None
) -> str:
    """Markdown with HTML tables that mirrors the printed prospectus.

    Source text only, HTML-escaped. Extraction status and (when known) the PDF hash are on
    line 1. Nothing here is corrected, merged or inferred: grid positions with no Docling cell
    become `<td data-gap>`, and cells that collide are listed after their table.
    """
    status = str(((payload or {}).get("audit") or {}).get("status", "unknown"))
    flagged = status != "ok"
    verdict = "REVIEW REQUIRED" if flagged else "content_review: pending"
    digest = pdf_sha256 or "not recorded"
    notice = (
        "> **REVIEW REQUIRED** (extraction audit: " + _esc(status) + "). "
        if flagged
        else "> "
    ) + (
        "Reconstruction of the Docling evidence for comparison with the PDF page. "
        "Candidate for review, not an approved curriculum."
    )
    parts = [
        f"<!-- extraction_audit: {_comment_text(status)} | {verdict} | pdf_sha256: {_comment_text(digest)} -->\n"
        f"<!-- markup: {MARKUP_VERSION} -->",
        notice,
    ]
    current_page: int | None = None
    for kind, obj in _reading_order(evidence):
        page = _block_page(kind, obj)
        block = _render_table(obj) if kind == "table" else _render_text(obj)
        if page is not None:
            if current_page is not None and page != current_page:
                block = f"<!-- page {page} -->\n<hr>\n\n{block}"
            current_page = page
        parts.append(block)
    return "\n\n".join(parts) + "\n"
```

- [ ] **Step 4: Run and confirm green**

Run: `uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_markup.py`
Expected: `20 passed`. If `test_items_on_one_printed_line…` fails, the line grouping is wrong: that test is the only proof of it, do not delete it.

- [ ] **Step 5: Run the whole suite and the self-test**

Expected: `54 passed`, 13 subtests passed; self-test `80/80`.

- [ ] **Step 6: Record progress and commit**

```
git add backend/bintanong_tools/prospectus_extractor/markup.py tests/test_prospectus_markup.py plans/plan_current_progress/extractor_split_progress.md
git commit -m "feat: markup twin status line, reading order and page breaks" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: Wire `--export-md` through the pipeline, CLI, batch, and TUI

**Files:**
- Modify: `backend/bintanong_tools/prospectus_extractor/pipeline.py` (import near line 20; signature at 174-186; stale list 206-213; write block after 237)
- Modify: `backend/bintanong_tools/prospectus_extractor/cli.py` (lines 38-39, 73, 92-104, 116-125)
- Modify: `backend/bintanong_tools/prospectus_extractor/batch.py` (lines 43, 207)
- Modify: `backend/bintanong_tools/prospectus_extractor/tui.py` (lines 89, 196-198, 271-276)
- Modify: `tests/test_prospectus_markup.py`

- [ ] **Step 1: Append the failing tests**

```python
from backend.bintanong_tools.prospectus_extractor import batch, cli, pipeline  # noqa: E402


def _fake_run(tmp_path, monkeypatch, status="error", **flags):
    source = tmp_path / "x_docling.json"
    source.write_text("{}", encoding="utf-8")
    document = evidence(
        [banner_table()], [text_item(0, "section_header", "PROPOSED PROGRAM OF STUDY")]
    )
    monkeypatch.setattr(pipeline, "load_document", lambda *args, **kwargs: (document, None))
    monkeypatch.setattr(pipeline, "build_payload", lambda *args, **kwargs: {"audit": {"status": status}})
    target = tmp_path / "out" / "x_prospectus.json"
    pipeline.process_prospectus(source, target, quiet=True, **flags)
    return target


def test_export_md_writes_the_twin_beside_the_json_even_when_the_audit_failed(tmp_path, monkeypatch):
    target = _fake_run(tmp_path, monkeypatch, status="error", export_md=True)
    twin = target.with_name("x_prospectus.md")
    text = twin.read_text(encoding="utf-8")
    assert text.splitlines()[0].startswith("<!-- extraction_audit: error | REVIEW REQUIRED |")
    assert "PROPOSED PROGRAM OF STUDY" in text and "\r" not in text


def test_md_is_not_written_by_default_and_a_stale_one_is_removed(tmp_path, monkeypatch):
    stale = tmp_path / "out" / "x_prospectus.md"
    stale.parent.mkdir()
    stale.write_text("old", encoding="utf-8")
    _fake_run(tmp_path, monkeypatch, status="ok")
    assert not stale.exists()


def _cli_flags(monkeypatch, tmp_path, *argv):
    seen: dict = {}
    monkeypatch.setattr(cli, "process_prospectus", lambda *a, **k: seen.update(k) or {"audit": {"status": "ok"}})
    source = tmp_path / "x_docling.json"
    source.write_text("{}", encoding="utf-8")
    assert cli.main(["-i", str(source), *argv]) == 0
    return seen


def test_cli_export_md_flag_and_export_all(monkeypatch, tmp_path):
    assert _cli_flags(monkeypatch, tmp_path)["export_md"] is False
    only = _cli_flags(monkeypatch, tmp_path, "--export-md")
    assert only["export_md"] is True and only["export_csv"] is False
    everything = _cli_flags(monkeypatch, tmp_path, "--export-all")
    assert everything["export_md"] and everything["export_csv"] and everything["export_pl"]


def test_cli_batch_receives_write_md(monkeypatch, tmp_path):
    seen = {}

    def fake_batch(config):
        seen["write_md"] = config.write_md
        return {"succeeded": 1, "audit_failed": 0, "skipped": 0, "failed": 0, "manifest_path": None}

    monkeypatch.setattr(cli, "run_batch", fake_batch)
    assert cli.main(["-i", str(tmp_path), "--batch", "--export-md"]) == 0
    assert seen["write_md"] is True
    assert cli.main(["-i", str(tmp_path), "--batch"]) == 0
    assert seen["write_md"] is False


def test_batch_defaults_to_writing_md_and_passes_it_on(monkeypatch, tmp_path):
    assert batch.BatchConfig().write_md is True
    source = tmp_path / "in"
    source.mkdir()
    (source / "a.pdf").write_bytes(b"%PDF-test")
    seen = []
    result = {
        "audit": {
            "status": "ok", "total_courses": 0, "computed_total_units": 0,
            "declared_total_units": None, "years_detected": [], "errors": [], "warnings": [],
        },
        "metadata": {},
    }
    monkeypatch.setattr(batch, "ensure_docling_env", lambda: None)
    monkeypatch.setattr(batch, "get_shared_converter", lambda **kwargs: None)
    monkeypatch.setattr(batch, "process_prospectus", lambda *a, **k: seen.append(k) or result)
    config = batch.BatchConfig(input_root=source, output_root=tmp_path / "out", write_manifest=False)
    batch.run_batch(config)
    assert seen[0]["export_md"] is True
    config.write_md = False
    batch.run_batch(config)
    assert seen[1]["export_md"] is False
```

- [ ] **Step 2: Run and confirm the failures**

Run: `uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_markup.py`
Expected: 20 passed, 5 failed: `process_prospectus() got an unexpected keyword argument 'export_md'` (twice), `KeyError: 'export_md'` (CLI), `AttributeError: … 'BatchConfig' … 'write_md'` (twice).

- [ ] **Step 3: `pipeline.py`**

Add to the imports (after the `from .rag import …` line):

```python
from .markup import render_prospectus_markup
```

Add `export_md: bool = False,` as the last parameter of `process_prospectus`, after `quiet: bool = False,` (appended at the end so existing positional callers cannot shift). In the stale-outputs tuple add `final_path.with_name(f"{base}_prospectus.md"),` after the `_review.csv` entry. Insert this block directly after the `if input_path.suffix.lower() == ".pdf":` essentials block (after the `print(f"[+] Curriculum essentials -> …")` lines) and before `if payload["audit"]["status"] == "error":`:

```python
    if export_md:  # written for every audit status: the reviewer needs it most when the audit failed
        md_path = final_path.with_name(f"{base}_prospectus.md")
        md_path.write_text(render_prospectus_markup(document, payload), encoding="utf-8", newline="\n")
        if not quiet:
            print(f"[+] Prospectus markup -> {md_path}")
```

(D2 alternative: put the block inside the `else:` branch to skip it on `error`.)

- [ ] **Step 4: `cli.py`**

After the `--export-csv` argument add:

```python
    parser.add_argument("--export-md", action="store_true", help="Also write the prospectus-style Markdown view")
```

Change the `--export-all` help to `"Write .pl, .jsonl, .csv and .md companions"`. After `export_csv = args.export_csv or args.export_all` add `export_md = args.export_md or args.export_all`. Add `write_md=export_md,` to the `BatchConfig(...)` call after `write_csv=export_csv,`, and `export_md=export_md,` to the `process_prospectus(...)` call after `export_csv=export_csv,`. In the epilog example line change to `"  %(prog)s -i prospectus.pdf --export-pl --export-csv --export-jsonl --export-md\n"`.

- [ ] **Step 5: `batch.py`**

Add `    write_md: bool = True` after `write_jsonl: bool = True` in `BatchConfig`. In `run_batch` add `export_md=config.write_md,` after `export_csv=config.write_csv,`. Do not touch `BatchItem` (its `csv_path`, `pl_path`, `jsonl_path` are descriptive only; `process_prospectus` derives the real file names from `json_path`).

- [ ] **Step 6: `tui.py`**

Line 89: `("Write CSV / PL / JSONL / MD", f"{cfg.write_csv} / {cfg.write_pl} / {cfg.write_jsonl} / {cfg.write_md}"),`. After the `write_jsonl` prompt add `        cfg.write_md = ask_yes_no("Write prospectus-style Markdown?", cfg.write_md)`. In `single_file`'s `process_prospectus(...)` call add `export_md=self.config.write_md,` after `export_csv=self.config.write_csv,`.

- [ ] **Step 7: Run and confirm green**

Run: `uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_markup.py`
Expected: `25 passed`.

Run the full suite and the self-test. Expected: `59 passed`, 13 subtests passed; `80/80`. Also run `uv run --project backend --extra tools --extra dev python -m backend.bintanong_tools.prospectus_extractor --help` and confirm `--export-md` appears and `--export-all` mentions `.md`.

- [ ] **Step 8: Record progress and commit**

```
git add backend/bintanong_tools/prospectus_extractor/pipeline.py backend/bintanong_tools/prospectus_extractor/cli.py backend/bintanong_tools/prospectus_extractor/batch.py backend/bintanong_tools/prospectus_extractor/tui.py tests/test_prospectus_markup.py plans/plan_current_progress/extractor_split_progress.md
git commit -m "feat: add --export-md and write the markup twin from the pipeline and batch" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: Prove course fields are unchanged on the 44 cached inputs

**Files:**
- Create: `scripts/prospectus_course_compare.py`

No extractor code changed parsing in this phase, so the expected result is zero differences. The same script also checks the new files: every cell of every cached prospectus appears exactly once in its `.md`.

The earlier golden script (`git show 2dffe3d:scripts/prospectus_golden_check.py`) ran old and new together and compared whole files. This one is smaller and field-level: `run` produces one tree's outputs, `compare` compares two output folders, so the two ~90-minute runs can go in parallel.

- [ ] **Step 1: Write the script**

```python
#!/usr/bin/env python3
"""Course-field regression for prospectus extractor changes.

    python scripts/prospectus_course_compare.py run TREE GOLDEN OUT [--semantic-doc MAP] [--limit N]
    python scripts/prospectus_course_compare.py compare OLD_OUT NEW_OUT [--expect-markup]

`run` executes the extractor found in the source tree TREE (a checkout or git worktree) over every
*_docling.json under GOLDEN and stores candidate.json plus companions under OUT/NN/.
`compare` checks that only course fields, audit status and counts are compared (never timestamps),
and with --expect-markup that each NEW candidate has a prospectus.md in which every canonical cell
appears exactly once.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

COURSE_FIELDS = (
    "course_code", "course_title", "year_level", "semester", "total_units", "lecture_units",
    "lab_units", "prerequisites", "prerequisites_raw", "prerequisites_unresolved",
    "standing_requirements", "category", "is_elective", "elective_group",
)
AUDIT_FIELDS = ("status", "errors", "total_courses", "computed_total_units", "years_detected")


def run(args: argparse.Namespace) -> int:
    sources = sorted(args.golden.rglob("*_docling.json"))[: args.limit]
    if not sources:
        sys.exit(f"no *_docling.json under {args.golden}")
    extra = ["--semantic-doc", str(args.semantic_doc)] if args.semantic_doc else ["--no-semantic-doc"]
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONHASHSEED="0")
    for number, source in enumerate(sources, 1):
        target = args.out / f"{number:02d}"
        target.mkdir(parents=True, exist_ok=True)
        (target / "source.txt").write_text(str(source), encoding="utf-8")
        done = subprocess.run(
            [sys.executable, "-m", "backend.bintanong_tools.prospectus_extractor",
             "-i", str(source), "-o", str(target / "candidate.json"),
             "--export-all", "--device", "cpu", *extra],
            cwd=args.tree, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        (target / "exit.txt").write_text(str(done.returncode), encoding="utf-8")
        (target / "log.txt").write_text(done.stdout + done.stderr, encoding="utf-8")
        print(f"{number}/{len(sources)} exit={done.returncode} {source.name}", flush=True)
    return 0


def _load(folder: Path) -> dict | None:
    path = folder / "candidate.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def _fields(payload: dict) -> dict:
    return {
        "courses": [{f: course.get(f) for f in COURSE_FIELDS} for course in payload["courses"]],
        "audit": {f: payload["audit"].get(f) for f in AUDIT_FIELDS},
    }


def _markup_problems(folder: Path, payload: dict) -> list[str]:
    twin = folder / "candidate_prospectus.md"
    if not twin.exists() or twin.stat().st_size == 0:
        return ["missing or empty candidate_prospectus.md"]
    text = twin.read_text(encoding="utf-8")
    status = payload["audit"]["status"]
    problems = []
    if not text.splitlines()[0].startswith(f"<!-- extraction_audit: {status} |"):
        problems.append(f"line 1 does not announce audit status {status!r}")
    cells = text.count('data-cell="') + text.count('data-unplaced-cell="')
    expected = payload["evidence"]["canonical_cell_count"]
    if cells != expected:
        problems.append(f"markup has {cells} cell elements, evidence has {expected}")
    return problems


def compare(args: argparse.Namespace) -> int:
    folders = sorted(path for path in args.old.iterdir() if path.is_dir())
    if not folders:
        sys.exit(f"no run folders under {args.old}")
    failures = 0
    for old in folders:
        new = args.new / old.name
        issues: list[str] = []
        if not new.is_dir():
            issues.append("missing in new run")
        else:
            if (old / "source.txt").read_text(encoding="utf-8") != (new / "source.txt").read_text(encoding="utf-8"):
                issues.append("different source file")
            if (old / "exit.txt").read_text() != (new / "exit.txt").read_text():
                issues.append("exit code differs")
            before, after = _load(old), _load(new)
            if (before is None) != (after is None):
                issues.append("candidate.json exists in only one run")
            elif before is not None and _fields(before) != _fields(after):
                old_fields, new_fields = _fields(before), _fields(after)
                if old_fields["audit"] != new_fields["audit"]:
                    issues.append(f"audit differs: {old_fields['audit']} != {new_fields['audit']}")
                for index, (a, b) in enumerate(zip(old_fields["courses"], new_fields["courses"])):
                    if a != b:
                        issues.append(f"course {index} differs: {sorted(k for k in a if a[k] != b[k])}")
                        break
                if len(old_fields["courses"]) != len(new_fields["courses"]):
                    issues.append("course count differs")
            if args.expect_markup and after is not None:
                issues += _markup_problems(new, after)
        failures += bool(issues)
        name = Path((old / "source.txt").read_text(encoding="utf-8")).name
        print(f"{old.name} {'FAIL' if issues else 'ok'} {name}")
        for issue in issues:
            print(f"    {issue}")
    print(f"{len(folders) - failures}/{len(folders)} identical")
    return 1 if failures else 0


def main() -> int:
    cli = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = cli.add_subparsers(dest="command", required=True)
    runner = sub.add_parser("run")
    runner.add_argument("tree", type=Path)
    runner.add_argument("golden", type=Path)
    runner.add_argument("out", type=Path)
    runner.add_argument("--semantic-doc", type=Path)
    runner.add_argument("--limit", type=int)
    runner.set_defaults(func=run)
    comparer = sub.add_parser("compare")
    comparer.add_argument("old", type=Path)
    comparer.add_argument("new", type=Path)
    comparer.add_argument("--expect-markup", action="store_true")
    comparer.set_defaults(func=compare)
    args = cli.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Prove the comparer can fail (3 inputs, minutes not hours)**

Create the old tree and run both sides on 3 files. Use a scratch folder under `$env:TEMP`.

```powershell
git worktree add --detach "$env:TEMP\bintanong-phaseb-old" 8d26f18
$G = 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\docling_jsonified_output\task2b_standing_isolated_2026-09-29'
$M = 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\PalSU Undergraduate Prospectus Website Dump\Tiniguiban - Main\palsu_main_undergrad_program_college_meaning.md'
$S = "$env:TEMP\phaseb-smoke"
uv run --project backend --extra tools --extra dev python scripts/prospectus_course_compare.py run "$env:TEMP\bintanong-phaseb-old" $G "$S\old" --semantic-doc $M --limit 3
uv run --project backend --extra tools --extra dev python scripts/prospectus_course_compare.py run (Get-Location).Path $G "$S\new" --semantic-doc $M --limit 3
uv run --project backend --extra tools --extra dev python scripts/prospectus_course_compare.py compare "$S\old" "$S\new" --expect-markup
```

Expected: three `exit=0` lines per run, then `3/3 identical`. Each `new\NN` folder has `candidate_prospectus.md`; no `old\NN` folder does.

Then make it fail on purpose to prove the comparer detects change: edit one `title` value in `$S\new\01\candidate.json` (for example change the first course's `course_title`) and rerun `compare`. Expected: `01 FAIL` with `course 0 differs: ['course_title']` and `2/3 identical`, exit code 1. Rerun the new side for folder 01 afterwards or delete `$S`.

- [ ] **Step 3: Launch the full 44-input run detached**

Each Docling-JSON extraction takes about 2 minutes, so a side takes about 90 minutes. Background tool calls die at 10 minutes. Launch both sides as detached `pwsh` processes writing log files, then poll the logs. Write the launcher to a file to avoid quoting problems:

```powershell
$R = (Get-Location).Path
$run = "$env:TEMP\phaseb-full"
New-Item -ItemType Directory -Force $run | Out-Null
@"
`$G = 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\docling_jsonified_output\task2b_standing_isolated_2026-09-29'
`$M = 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\PalSU Undergraduate Prospectus Website Dump\Tiniguiban - Main\palsu_main_undergrad_program_college_meaning.md'
Set-Location '$R'
uv run --project backend --extra tools --extra dev python scripts/prospectus_course_compare.py run `$args[0] `$G `$args[1] --semantic-doc `$M
"@ | Set-Content "$run\launch.ps1" -Encoding utf8
Start-Process pwsh -ArgumentList '-NoProfile','-File',"$run\launch.ps1","$env:TEMP\bintanong-phaseb-old","$run\old" -RedirectStandardOutput "$run\old.log" -RedirectStandardError "$run\old.err" -WindowStyle Hidden
Start-Process pwsh -ArgumentList '-NoProfile','-File',"$run\launch.ps1",$R,"$run\new" -RedirectStandardOutput "$run\new.log" -RedirectStandardError "$run\new.err" -WindowStyle Hidden
```

Poll with `Get-Content "$env:TEMP\phaseb-full\old.log" -Tail 3` and the same for `new.log` every few minutes (do not sleep in a loop in one call). Finished when both logs show `44/44`.

- [ ] **Step 4: Compare**

```powershell
uv run --project backend --extra tools --extra dev python scripts/prospectus_course_compare.py compare "$env:TEMP\phaseb-full\old" "$env:TEMP\phaseb-full\new" --expect-markup
```

Expected final line: `44/44 identical`, exit 0. Any `FAIL` is a real difference: use superpowers:systematic-debugging; the likely causes are a markup invariant (`cell elements` count) or something this phase should not have touched. Record the measured numbers in the progress file: inputs, identical count, how many of the 44 `.md` files contain at least one `data-gap` (expected: all), at least one `data-unplaced-cell` (expected: about 14), and the largest `.md` size.

- [ ] **Step 5: Clean up and commit the script**

```powershell
git worktree remove --force "$env:TEMP\bintanong-phaseb-old"
```

```
git add scripts/prospectus_course_compare.py plans/plan_current_progress/extractor_split_progress.md
git commit -m "test: add field-level old-versus-new course comparer with markup invariants" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6: Human visual check against the PDFs (BS Computer Science and Architecture)

**Files:**
- Modify: `plans/plan_current_progress/extractor_split_progress.md`

This is a human gate. An agent can generate the files and fill the checklist from the data, but cannot truthfully say a rendered page "looks like" the PDF. If no human is present, record `visual check: pending human review` and do not mark the task done; do not claim a pass.

- [ ] **Step 1: Render both prospectuses from the cached Docling JSON (no PDF conversion, about 1 minute each)**

```powershell
$G = 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\docling_jsonified_output\task2b_standing_isolated_2026-09-29'
$M = 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\PalSU Undergraduate Prospectus Website Dump\Tiniguiban - Main\palsu_main_undergrad_program_college_meaning.md'
$V = "$env:TEMP\phaseb-visual"; New-Item -ItemType Directory -Force $V | Out-Null
$cs  = (Get-ChildItem $G -Recurse -Filter '1_BS Computer*_docling.json').FullName
$bsa = (Get-ChildItem $G -Recurse -Filter 'BSA-for-student*_docling.json').FullName
uv run --project backend --extra tools --extra dev python -m backend.bintanong_tools.prospectus_extractor -i $cs  -o "$V\bscs.json"         --export-md --semantic-doc $M
uv run --project backend --extra tools --extra dev python -m backend.bintanong_tools.prospectus_extractor -i $bsa -o "$V\architecture.json" --export-md --semantic-doc $M
Get-ChildItem $V -Filter *_prospectus.md
```

Expected: `bscs_prospectus.md` and `architecture_prospectus.md`; each starts with `<!-- extraction_audit: error | REVIEW REQUIRED | pdf_sha256: not recorded -->` (both audits are `error` at this commit; if one is not, record the real status).

- [ ] **Step 2: Open each `.md` rendered next to its PDF page**

The PDFs (outside Git):
- BSCS: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\PalSU Undergraduate Prospectus Website Dump\Tiniguiban - Main\CS\Computer Science\New Curriculum (2025-2026)\1_BS Computer Science_for BOR approval _rev02_v7_6 August 2025.pdf` (1 page)
- Architecture: `…\Tiniguiban - Main\CAD\BSA-for-student-new-version.pdf` (1 page)

In VS Code: `code "$V\bscs_prospectus.md"`, press `Ctrl+Shift+V` for the Markdown preview, and place the PDF beside it (`code` the PDF, or open it in the browser). Preview, not the raw text, is what is being judged. Raw HTML tables render in VS Code's preview; if table borders are invisible, that is the preview theme, not a defect, so compare structure.

- [ ] **Step 3: Fill the comparison table in the progress file**

For each of the two, record one row per check, with `same`, `different (Docling)` or `different (renderer)`, and a note. "Docling" means the cell text or span is already wrong in the evidence (compare with `--dump-grid` if unsure); "renderer" means the twin shows something the evidence does not say. Only `different (renderer)` blocks the gate.

| Check | BSCS | Architecture |
| --- | --- | --- |
| Header lines above the table present, in order (program title, effective SY) | | |
| Column header row: same columns (BSCS: Course Code, Course Title, Unit, Pre- requisite, twice; Architecture: Grade, Course Code, Course Title, Unit/s, Pre- Req, twice) | | |
| Year banners span the full width, one per year | | |
| Two semesters side by side, columns aligned under their own half | | |
| Same number of course rows per semester as the PDF | | |
| `Total` rows present with the printed unit totals | | |
| Empty prerequisite and grade columns stay empty and aligned (gaps) | | |
| Footnote, elective list, legend or `Note:` text below the table, in order | | |
| Page footer / page number present | | |
| Nothing appears that is not on the PDF | | |

Expected differences caused by Docling, recorded for the later parser work, not fixed here: BSCS row `FIRST SEMESTER Discrete Structures 1 1` (banner word glued into a title cell); Architecture `FIRST YEAR FIRST SEMESTER SECOND SEMESTER` as one banner and `SECOND AD-2/L, TOA-2,` as one cell. List any others found.

- [ ] **Step 4: Optional sanity screenshot an agent can take**

If a human is not available, an agent may wrap the file in a minimal HTML page and screenshot it with the Playwright MCP, to catch a structurally broken table (for example a collapsed row), and attach the result to the progress file as "agent screenshot, not a human comparison":

```powershell
$html = "<html><head><meta charset='utf-8'><style>td,th{border:1px solid #888;padding:2px 4px}table{border-collapse:collapse;font-size:12px}</style></head><body>" + (Get-Content "$V\bscs_prospectus.md" -Raw -Encoding utf8) + "</body></html>"
Set-Content "$V\bscs_preview.html" $html -Encoding utf8
```

Open `file:///…/bscs_preview.html` with the browser tool. (The one `>` blockquote line shows as plain text in this wrapper; that is expected.)

- [ ] **Step 5: Decide the gate and commit the record**

Gate: for both prospectuses a person finds the same rows, columns, and merged cells as the PDF, apart from items marked `different (Docling)`. If any `different (renderer)` row exists, stop, write a failing test that reproduces it in Task 2 or 3's test file, fix, rerun Tasks 5 step 4 for the affected invariant, and redo this task.

```
git add plans/plan_current_progress/extractor_split_progress.md
git commit -m "docs: record the visual comparison of the markup twin with two prospectus PDFs" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 7: Decision record, Codex gate, hand off

**Files:**
- Create: `docs/decisions/prospectus-markup-twin.md`
- Modify: `plans/plan_current_progress/extractor_split_progress.md`

- [ ] **Step 1: Write the decision record**

`docs/decisions/prospectus-markup-twin.md` must state, in plain sentences: what the twin is and that it is a review aid built from evidence, not an approved curriculum; the layout rules 1-8 from this plan; the decisions D1-D7 as taken (note any that changed during execution); that `export_to_markdown()` was deliberately not added, with the reason; that no payload key was added so `SCHEMA_VERSION` is unchanged; that the source hash shows `not recorded` until Phase D passes it, and that `prospectus_batch.py` already hashes the PDF in the parent process but the child does not receive it; the facts from "What a real prospectus looks like" that surprised the plan (gaps in 23 to 148 grid positions per main table, 14 of 44 files with overlapping cells, Docling gluing banner words into cells); the measured results of Tasks 5 and 6 with dates; and the OCR note below.

OCR note to include: the renderer takes whatever `ProspectusEvidence` it is given. Nothing in it assumes a text layer: ordering and `data-page` come from boxes, and a future Docling OCR source can attach per-cell confidence and `source_kind="ocr"` without changing this module (a later change could add `data-ocr-confidence` to a cell).

- [ ] **Step 2: Run everything one last time**

Full suite (expected `59 passed`, 13 subtests passed), self-test (`80/80`), and `git status --short` (only the files this phase lists, plus the two files you must leave alone).

- [ ] **Step 3: Codex gate (read-only, detached, about 15 minutes)**

Write the prompt to a file and launch detached so the 10-minute tool limit does not kill it:

```powershell
$run = "$env:TEMP\phaseb-codex"; New-Item -ItemType Directory -Force $run | Out-Null
@'
Review branch feature/prospectus-markup-twin against dev (8d26f18) in this repo. Read backend/bintanong_tools/prospectus_extractor/markup.py, the changes to pipeline.py, cli.py, batch.py, tui.py, and tests/test_prospectus_markup.py. Claims to attack: (1) every NormalizedCell appears exactly once in the output, as a td/th or as an unplaced-cell paragraph; (2) no cell text is ever interpreted as markup or HTML, and the first-line comment cannot be broken out of; (3) grid positions covered by no cell render as data-gap cells that carry no cell ID, so no evidence is invented; (4) output is deterministic and independent of input order; (5) reading order is right for both BOTTOMLEFT and TOPLEFT boxes and for multi-page documents; (6) no extracted course value, payload key, or SCHEMA_VERSION changed. Look for HTML block rules in CommonMark that would end the table early (blank lines, indentation), Windows newline problems, tables whose rowspan/colspan clamp is wrong, and any caller of process_prospectus or BatchConfig that this change breaks. Do not modify files. Report findings with file and line, and say which you could not confirm.
'@ | Set-Content "$run\prompt.txt" -Encoding utf8
Start-Process pwsh -ArgumentList '-NoProfile','-Command',"codex exec --sandbox read-only -o '$run\codex-report.md' (Get-Content '$run\prompt.txt' -Raw)" -WorkingDirectory (Get-Location).Path -RedirectStandardOutput "$run\codex.log" -RedirectStandardError "$run\codex.err" -WindowStyle Hidden
```

Poll `Get-Content "$run\codex.log" -Tail 5` until the process ends, then read `codex-report.md`. If Codex is rate-limited or errors, record that in the progress file and continue; do not block. Fix each confirmed finding with a failing test first; note and skip unconfirmed ones.

- [ ] **Step 4: Update the progress file and commit**

Set every Phase B row to done with the real evidence, add the Codex findings, and the line: "Phase B complete on branch feature/prospectus-markup-twin; not merged, not pushed; next: user decides on merge, then write the Phase C plan. Phase C and D should pass `pdf_sha256=` into `render_prospectus_markup` (call site: `pipeline.process_prospectus`, the `if export_md:` block)."

```
git add docs/decisions/prospectus-markup-twin.md plans/plan_current_progress/extractor_split_progress.md
git commit -m "docs: record the markup twin and its visual and regression evidence" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

Do not merge into `dev` and do not push; ask the user (superpowers:finishing-a-development-branch).

**Phase B gate:** 25 markup tests green and the full suite green (59); self-test 80/80; `44/44 identical` course fields with every `.md` holding exactly the canonical cell count; BSCS and Architecture compared with their PDFs with no `different (renderer)` finding; Codex findings resolved or recorded; decision record written.

---

## Self-review

**Spec coverage (outline, brief, and the user's requirements):**
- Mirror the printed prospectus, LLM/RAG/diff friendly, and the GUI "reconstructed table" view: layout rules 1-8, cell and item IDs on every element (Tasks 2-3, decision record).
- HTML `<table>` inside Markdown, one `<td>`/`<th>` per `NormalizedCell` with `data-cell` and `data-page`, real spans: Task 2 tests 1-2, 5, 8.
- Source text, escaped, never paraphrased: escape tests (Task 2 test 6, Task 3 text test), and the plan states Docling's glued cells are reproduced, not repaired.
- Status first line with audit status, REVIEW REQUIRED when not ok, hash when known; hash availability investigated: Task 3 tests; D4 and "What a real prospectus looks like" (no hash in payload or evidence; shows `not recorded`; Phase D passes it).
- Deterministic: Task 3 determinism test (also input-order independence).
- `--export-md`, in `--export-all`, `<stem>_prospectus.md`, batch support via `BatchConfig.write_md`: Task 4 (CLI, pipeline, batch, TUI, tests).
- `export_to_markdown()` side output: decided not to add, with the concrete finding that `evidence.markdown` already holds it.
- Multi-page and multiple tables: reading order and page-marker tests, plus BSBA-MM (5 tables) and Accountancy/Nursing (multi-page) named in the evidence section.
- Empty grid positions without inventing cells: `data-gap` with no cell ID, tested for alignment including rowspan; colliding cells handled by D5.
- Human visual check with the progress-file record: Task 6.
- Regression on the 44 cached inputs with the field-level comparer (recovered/adapted, full code, detached launch, polling): Task 5.
- Delete the Phase A gate conditionally in the first commit: Task 1 step 3. Start check with line references: Task 1 step 1. Progress-file step in every task. Codex gate: Task 7. `SCHEMA_VERSION`: not bumped, with the reason, because the payload shape is unchanged. OCR room: Task 7 note and no text-layer assumption.
- "Decisions needed before execution" section: D1-D7 at the top.

**Placeholder scan:** no TBD or "similar to Task N"; every code step has complete code. The only fill-in items are the observation tables in Task 6, which are records of what a human sees and cannot be pre-written.

**Name consistency:** `render_prospectus_markup(evidence, payload, *, pdf_sha256=None)`, `_render_table`, `_render_cell`, `_layout_cells`, `_reading_order`, `_render_text`, `LINE_TOLERANCE`, `MARKUP_VERSION`, `export_md`, `write_md`, `data-unplaced-cell`, `data-gap` are used identically in the tests, the module, and the CLI/batch edits. Test counts: baseline 36, minus 2 equivalence tests = 34, +8 (Task 2) = 42, +12 (Task 3) = 54, +5 (Task 4) = 59; the markup test file totals 25 (8+12+5).
