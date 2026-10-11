# Exact task brief from C:\Users\Hawksprey\source\repos\Bintanong-wt\phase-d\plans\2026-10-03-prospectus-phase-e-rag-provenance.md

Read approved_execution.md and preflight-ledger.md first. They supersede obsolete base/merge/dev/version/path snippets in this preserved historical plan. Do not edit the original plan. Preserve original task requirements below unless an approved ruling supersedes them.

### Task 1: Start check

**Files:** read only, plus `plans/plan_current_progress/extractor_split_progress.md`.

- [ ] **Step 1: Create the branch and confirm the base**

Run: `git switch dev && git status --short && git log --oneline -5 && git switch -c feature/prospectus-phase-e-rag-provenance`
Expected: `dev` contains the merged Phase B, C and D work; `git status` shows only ` M .gitignore` and `?? plans/CODEX_HANDOFF_prospectus_extractor_phase2_2026-09-26.md`. If either is missing, stop: Phase E must not start before D has merged.

- [ ] **Step 2: Delete the Phase A AST gate if it is still there (conditional)**

Run: `Test-Path tests/test_prospectus_split_equivalence.py`
Expected after Phase B: `False`. If `True` (Phase B did not run), delete it in this branch's first commit: `git rm tests/test_prospectus_split_equivalence.py` and commit `test: drop the 1:1 split gate`. Otherwise skip.

- [ ] **Step 3: Re-read the files this phase touches and update line references**

Open `rag.py`, `pipeline.py`, `courses.py`, `common.py`, `sections.py` (`_make_provenance`), `evidence.py`. For each reference in "What exists today" confirm the line numbers; where an earlier phase moved things, edit this plan's line references in place. Then answer, in the progress file, each of these from the code (not from this plan):

1. Does `build_payload` already accept or return a PDF hash or a `ProvisionalSource`? Run `Select-String -Path backend\bintanong_tools\prospectus_extractor\*.py -Pattern 'sha256|ProvisionalSource|source_verification'`. If yes, note the name; Task 6 then uses it instead of adding the `pdf_sha256` keyword helper.
2. What is `SCHEMA_VERSION` now (`common.py:8`)? Task 6 bumps it by one minor step.
3. Did Phase C or D change `build_payload`'s signature, the `audit["status"]` vocabulary (`pipeline.py:52` uses `!= "error"`), or the `_rag.jsonl` writer? Adjust Tasks 6 and the pipeline snippets accordingly and record what changed.
4. Does `tests/` still contain `test_prospectus_chunks.py`? It should not exist yet.

- [ ] **Step 4: Run the baseline**

Run the full suite and the self-test from "Commands used throughout". Expected: all green; record the observed counts in the progress file (the 36 passed figure will be higher after B to D).

- [ ] **Step 5: Seed the progress section**

Append to `plans/plan_current_progress/extractor_split_progress.md`:

```
## Phase E: source-linked RAG chunks

Branch feature/prospectus-phase-e-rag-provenance from dev <hash>. Baseline: <N> passed, self-test 80/80.
Start-check answers: <the four answers from Task 1 step 3>.
```

- [ ] **Step 6: Commit**

```
git add plans/plan_current_progress/extractor_split_progress.md
git commit -m "docs: start Phase E source-linked chunks"
```

---



### Task 2: Chunk primitives (`chunking.py`)

**Files:**
- Create: `tests/test_prospectus_chunks.py`
- Create: `backend/bintanong_tools/prospectus_extractor/chunking.py`

- [ ] **Step 1: Write the failing tests**

```python
"""Phase E: source-linked, edition-stable candidate chunks."""

from __future__ import annotations

from backend.bintanong_tools.prospectus_extractor import chunking

PDF_A = "a" * 64
PDF_B = "b" * 64
LOCATOR = {"kind": "table_cells", "table_index": 0, "cell_ids": ["t0-c1"]}


def _span(pdf=PDF_A, page=1, locator=LOCATOR, text="x"):
    return chunking.make_span(pdf, page, locator, text, None, "docling-json")


def test_chunk_id_depends_on_every_input(monkeypatch):
    key = chunking.locator_key([_span()])
    base = chunking.make_chunk_id(PDF_A, key, "h1")
    assert base == chunking.make_chunk_id(PDF_A, key, "h1")
    assert len(base) == 64
    assert base != chunking.make_chunk_id(PDF_B, key, "h1")
    other = chunking.locator_key([_span(locator={**LOCATOR, "cell_ids": ["t0-c2"]})])
    assert base != chunking.make_chunk_id(PDF_A, other, "h1")
    assert base != chunking.make_chunk_id(PDF_A, key, "h2")
    monkeypatch.setattr(chunking, "CHUNKER_VERSION", "palsu-chunker-next")
    assert base != chunking.make_chunk_id(PDF_A, key, "h1")


def test_missing_pdf_hash_is_salted_not_empty():
    key = chunking.locator_key([_span(pdf=None)])
    assert chunking.make_chunk_id(None, key, "h") != chunking.make_chunk_id(PDF_A, key, "h")


def test_locator_key_ignores_span_order_and_text():
    first, second = _span(page=1), _span(page=2, locator={**LOCATOR, "cell_ids": ["t0-c9"]})
    assert chunking.locator_key([first, second]) == chunking.locator_key([second, first])
    assert chunking.locator_key([_span(text="a")]) == chunking.locator_key([_span(text="b")])


def test_content_hash_ignores_whitespace_but_not_words():
    assert chunking.content_hash("A  B", "C\nD") == chunking.content_hash("A B", "C D")
    assert chunking.content_hash("A B", "C D") != chunking.content_hash("A B", "C E")
    assert chunking.content_hash("A B", "C D") != chunking.content_hash("A X", "C D")


def test_token_estimate_overcounts_and_cap_includes_reserve():
    assert chunking.estimate_tokens("word " * 100) >= 180  # 1.8 tokens per word floor
    assert chunking.estimate_tokens("x" * 300) >= 100  # 3 chars per token floor
    limit = chunking.TOKEN_HARD_CAP - chunking.TOKEN_RESERVE
    assert chunking.fits_cap(limit)
    assert not chunking.fits_cap(limit + 1)


def test_pack_items_splits_at_the_target_and_repeats_nothing():
    items = [(f"line {n} " + "word " * 40, n) for n in range(10)]
    parts = chunking.pack_items("HEADER", items, limit=200)
    assert len(parts) > 1
    assert [member for _lines, members in parts for member in members] == list(range(10))
    for lines, _members in parts:
        assert chunking.estimate_tokens("\n".join(["HEADER", *lines])) <= 200 or len(lines) == 1


def test_pack_items_keeps_one_oversized_item_alone():
    parts = chunking.pack_items("H", [("big " * 500, "a"), ("small", "b")], limit=100)
    assert [members for _lines, members in parts] == [["a"], ["b"]]
```

- [ ] **Step 2: Run and confirm it fails for the right reason**

Run: `uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_chunks.py`
Expected: collection error `ImportError: cannot import name 'chunking'`.

- [ ] **Step 3: Write `chunking.py` in full**

```python
"""Chunk identity, source spans and token budgeting (Phase E). Pure functions, no I/O."""

from __future__ import annotations

import hashlib
import json
import math
import re
import unicodedata
from typing import Any
from typing import Mapping
from typing import Sequence

CHUNKER_VERSION = "palsu-chunker-v1"
TOKEN_HARD_CAP = 512  # SEA-LION-E5-Embedding-600M context limit (master plan section 2)
TOKEN_RESERVE = 32  # prompt prefix and special tokens that count against the cap (section 7.2)
TOKEN_SPLIT_AT = 400  # upper end of the 300-400 target; summaries are split here
TOKEN_COUNT_METHOD = "estimate-v1"
UNANCHORED = "unanchored"
_WORD = re.compile(r"[0-9a-z]+")


def estimate_tokens(text: str) -> int:
    # ponytail: deliberate over-count until Phase 3 measures with the real tokenizer (Decision D1).
    words = len(text.split())
    return max(math.ceil(len(text) / 3), math.ceil(words * 1.8))


def fits_cap(token_count: int) -> bool:
    return token_count + TOKEN_RESERVE <= TOKEN_HARD_CAP


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_text(text: Any) -> str:
    return unicodedata.normalize("NFC", " ".join(str(text).split()))


def content_hash(source_text: str, text: str) -> str:
    return _sha256(json.dumps([canonical_text(source_text), canonical_text(text)], ensure_ascii=False))


def make_span(
    pdf_sha256: str | None,
    page: int | None,
    locator: Mapping[str, Any],
    text: str | None,
    bbox: Sequence[float] | None,
    source_kind: str,
    resolution_method: str = "deterministic",
    repair_id: str | None = None,
) -> dict[str, Any]:
    return {
        "pdf_sha256": pdf_sha256,
        "page": page,
        "printed_page_label": None,
        "locator": dict(locator),
        "text": text,
        "bbox": list(bbox) if bbox else None,
        "extraction": {
            "source_kind": source_kind,
            "resolution_method": resolution_method,
            "repair_id": repair_id,
            "ocr_confidence": None,
        },
    }


def _union_bbox(boxes: Sequence[Sequence[float] | None]) -> list[float] | None:
    boxes = [box for box in boxes if box]
    if not boxes:
        return None
    return [
        min(box[0] for box in boxes),
        min(box[1] for box in boxes),
        max(box[2] for box in boxes),
        max(box[3] for box in boxes),
    ]


def spans_from_cells(
    cells: Sequence[Mapping[str, Any]],
    pdf_sha256: str | None,
    source_kind: str,
    resolution_method: str = "deterministic",
    repair_id: str | None = None,
) -> list[dict[str, Any]]:
    """One span per (table, page) group of cells, so a multi-page source lists every page."""
    unique: dict[str, Mapping[str, Any]] = {}
    for cell in cells:
        unique.setdefault(cell["cell_id"], cell)
    groups: dict[tuple[int, int | None], list[Mapping[str, Any]]] = {}
    for cell in sorted(
        unique.values(),
        key=lambda c: (c["table_index"], c["row_start"], c["col_start"], c["cell_id"]),
    ):
        groups.setdefault((cell["table_index"], cell.get("page")), []).append(cell)
    spans = []
    for (table_index, page), group in sorted(
        groups.items(), key=lambda item: (item[0][0], item[0][1] is None, item[0][1] or 0)
    ):
        spans.append(
            make_span(
                pdf_sha256,
                page,
                {"kind": "table_cells", "table_index": table_index, "cell_ids": [c["cell_id"] for c in group]},
                " | ".join(c["text"] for c in group if c.get("text")),
                _union_bbox([c.get("bbox") for c in group]),
                source_kind,
                resolution_method,
                repair_id,
            )
        )
    return spans


def spans_from_text_items(
    items: Sequence[Any],
    item_ids: Sequence[str | None],
    pdf_sha256: str | None,
    source_kind: str,
) -> list[dict[str, Any]]:
    by_id = {item.get("item_id"): item for item in items if isinstance(item, Mapping)}
    spans = []
    for item_id in dict.fromkeys(i for i in item_ids if i):
        item = by_id.get(item_id)
        if item is None:
            continue
        spans.append(
            make_span(
                pdf_sha256,
                item.get("page"),
                {"kind": "text_item", "item_ids": [item_id]},
                item.get("text", ""),
                item.get("bbox"),
                source_kind,
            )
        )
    return spans


def locator_key(spans: Sequence[Mapping[str, Any]], fallback: str = "") -> str:
    if not spans:
        return fallback
    return json.dumps(
        sorted(json.dumps([span.get("page"), span["locator"]], sort_keys=True) for span in spans)
    )


def make_chunk_id(pdf_sha256: str | None, locator: str, digest: str) -> str:
    return _sha256(json.dumps([pdf_sha256 or UNANCHORED, locator, digest, CHUNKER_VERSION]))


def course_rejection(course: Mapping[str, Any]) -> str | None:
    """Why a course may not become a chunk, or None. Decision D2: reject, do not flag."""
    provenance = course.get("provenance") or {}
    cells = provenance.get("source_cells") or []
    if not provenance.get("valid") or not provenance.get("source_cell_ids") or not cells:
        return "no_valid_source_cells"
    asserted = set(_WORD.findall(str(course.get("prerequisites_raw") or "").lower()))
    present = set(_WORD.findall(" ".join(str(c.get("text", "")) for c in cells).lower()))
    if not asserted <= present:
        return "prerequisite_not_in_source_text"
    return None


def pack_items(
    header: str, items: Sequence[tuple[str, Any]], limit: int = TOKEN_SPLIT_AT
) -> list[tuple[list[str], list[Any]]]:
    """Greedy split of (line, member) items; every part is rendered under the same header."""
    parts: list[tuple[list[str], list[Any]]] = []
    lines: list[str] = []
    members: list[Any] = []
    for line, member in items:
        if lines and estimate_tokens("\n".join([header, *lines, line])) > limit:
            parts.append((lines, members))
            lines, members = [], []
        lines.append(line)
        members.append(member)
    if lines:
        parts.append((lines, members))
    return parts


def assemble_chunk(
    chunk_type: str,
    fields: Mapping[str, Any],
    text: str,
    spans: Sequence[Mapping[str, Any]],
    *,
    pdf_sha256: str | None,
    source: str,
    source_text: str | None = None,
    locator_fallback: str = "",
) -> dict[str, Any]:
    spans = list(spans)
    if source_text is None:
        source_text = "\n".join(span["text"] for span in spans if span.get("text"))
    digest = content_hash(source_text, text)
    return {
        "chunk_id": make_chunk_id(pdf_sha256, locator_key(spans, locator_fallback), digest),
        "chunk_type": chunk_type,
        "chunker_version": CHUNKER_VERSION,
        "content_review": "pending",
        "pdf_sha256": pdf_sha256,
        "source_anchored": bool(pdf_sha256),
        **fields,
        "text": text,
        "source_text": source_text,
        "source_spans": spans,
        "pages": sorted({span["page"] for span in spans if span.get("page") is not None}),
        "table_indexes": sorted(
            {span["locator"]["table_index"] for span in spans if "table_index" in span["locator"]}
        ),
        "cell_ids": [cell_id for span in spans for cell_id in span["locator"].get("cell_ids", [])],
        "content_hash": digest,
        "token_count": estimate_tokens(text),
        "token_count_method": TOKEN_COUNT_METHOD,
        "source": source,
    }
```

- [ ] **Step 4: Run and confirm green**

Run the Phase E tests. Expected: 7 passed.

- [ ] **Step 5: Run the full suite and self-test, then update the progress file and commit**

Expected: all green, self-test 80/80 (nothing imports the new module yet).

```
git add backend/bintanong_tools/prospectus_extractor/chunking.py tests/test_prospectus_chunks.py plans/plan_current_progress/extractor_split_progress.md
git commit -m "feat: add chunk identity, span and token-budget primitives"
```

---



### Task 3: Course chunks carry source identity and are edition-stable

**Files:**
- Modify: `tests/test_prospectus_chunks.py` (append)
- Modify: `backend/bintanong_tools/prospectus_extractor/rag.py` (rewrite lines 1-212; this task writes the whole file, Tasks 4 and 5 fill in the parts marked in the code)

This task replaces the file with its final content so later tasks only add tests; the summary and hierarchical code is complete here but only exercised by tests from Tasks 4 and 5. If the executor prefers, write it in three passes, but each pass must keep the previous tests green.

- [ ] **Step 1: Append the helpers and failing tests for course chunks**

```python
from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.bintanong_tools.prospectus_extractor import rag
from backend.bintanong_tools.prospectus_extractor.courses import parse_elective_tracks
from backend.bintanong_tools.prospectus_extractor.evidence import ProspectusEvidence

META = {
    "program_name": "BS Test",
    "degree": "BS Test",
    "college_code": "CT",
    "college_name": "College of Test",
    "campus": "Tiniguiban - Main",
    "effective_school_year": "2018-2019",
    "source_file": "t.pdf",
}


def cell(cell_id, text, page=1, row=0, col=0, table=0):
    return {
        "cell_id": cell_id, "table_index": table, "text": text, "raw_text": text,
        "row_start": row, "row_end": row + 1, "col_start": col, "col_end": col + 1,
        "page": page, "bbox": [1.0, 2.0, 3.0, 4.0] if page is not None else None,
    }


def course(code, title="Intro", year="1st Year", sem="1st Semester", prereq="", cells=None, units=3, standing=()):
    slug = code.replace(" ", "").replace("/", "")
    if cells is None:
        cells = [cell(f"t0-{slug}-a", code), cell(f"t0-{slug}-b", title, col=1)]
        if prereq or standing:
            cells.append(cell(f"t0-{slug}-p", prereq or "; ".join(standing), col=3))
    ids = [c["cell_id"] for c in cells]
    return {
        "course_code": code, "course_title": title, "year_level": year, "semester": sem,
        "units": {"total": units, "lecture": units, "lab": 0}, "total_units": units,
        "prerequisites": [prereq] if prereq else [], "prerequisites_unresolved": [],
        "standing_requirements": list(standing), "prerequisites_raw": prereq or "; ".join(standing),
        "category": "Core / Major", "elective_group": None,
        "provenance": {
            "table_index": 0, "source_cell_ids": ids, "source_cells": cells,
            "resolution_method": "deterministic", "repair_id": None,
            "valid": bool(ids), "highlightable": bool(ids),
        },
    }


def term_units(courses):
    seen = dict.fromkeys((c["year_level"], c["semester"]) for c in courses)
    return [
        {"year_level": y, "semester": s, "declared_units": None,
         "computed_units": sum(c["total_units"] for c in courses if (c["year_level"], c["semester"]) == (y, s))}
        for y, s in seen
    ]


def build(courses, tracks=(), text_items=(), pdf=PDF_A):
    rejected = []
    chunks = rag.build_semantic_rag_chunks(
        META, courses, list(tracks), term_units(courses),
        pdf_sha256=pdf, source_kind="docling-json", text_items=list(text_items), rejected=rejected,
    )
    return chunks, rejected


def of_type(chunks, kind):
    return [c for c in chunks if c["chunk_type"] == kind]


def test_course_chunk_carries_source_identity():
    chunks, rejected = build([course("CS 101")])
    [chunk] = of_type(chunks, "course")
    assert rejected == []
    assert chunk["pdf_sha256"] == PDF_A and chunk["source_anchored"] is True
    assert chunk["content_review"] == "pending"
    assert chunk["chunker_version"] == chunking.CHUNKER_VERSION
    assert chunk["pages"] == [1] and chunk["table_indexes"] == [0]
    assert chunk["cell_ids"] == ["t0-CS101-a", "t0-CS101-b"]
    assert chunk["source_text"] == "CS 101 | Intro"
    assert chunk["source_spans"][0]["locator"] == {
        "kind": "table_cells", "table_index": 0, "cell_ids": chunk["cell_ids"]}
    assert chunk["section_path"] == ["BS Test", "1st Year", "1st Semester"]
    assert chunk["token_count_method"] == chunking.TOKEN_COUNT_METHOD
    assert "id" not in chunk and len(chunk["chunk_id"]) == 64


def test_summary_text_and_source_text_stay_separate():
    [chunk] = of_type(build([course("CS 101")])[0], "course")
    assert chunk["text"].startswith("### Course: CS 101 - Intro")
    assert "CS 101 | Intro" not in chunk["text"]
    assert "### Course" not in chunk["source_text"]


def test_two_editions_of_the_same_course_get_different_ids():
    old = of_type(build([course("CS 101")], pdf=PDF_A)[0], "course")[0]
    new = of_type(build([course("CS 101")], pdf=PDF_B)[0], "course")[0]
    assert old["chunk_id"] != new["chunk_id"]
    assert old["content_hash"] == new["content_hash"]  # same words, different edition
    retitled = of_type(build([course("CS 101", title="Intro v2")], pdf=PDF_A)[0], "course")[0]
    assert retitled["chunk_id"] != old["chunk_id"]


def test_same_inputs_give_the_same_ids():
    first = [c["chunk_id"] for c in build([course("CS 101"), course("CS 102", prereq="CS 101")])[0]]
    second = [c["chunk_id"] for c in build([course("CS 101"), course("CS 102", prereq="CS 101")])[0]]
    assert first == second and len(set(first)) == len(first)


def test_missing_pdf_hash_is_labelled_unanchored():
    [chunk] = of_type(build([course("CS 101")], pdf=None)[0], "course")
    assert chunk["pdf_sha256"] is None and chunk["source_anchored"] is False
    assert chunk["chunk_id"] != of_type(build([course("CS 101")])[0], "course")[0]["chunk_id"]


def test_course_spanning_two_pages_lists_both_pages():
    straddling = course("CS 103", cells=[
        cell("t0-c1", "CS 103", page=1, row=9), cell("t0-c2", "Theory", page=2, row=0, col=1)])
    [chunk] = of_type(build([straddling])[0], "course")
    assert chunk["pages"] == [1, 2]
    assert [s["page"] for s in chunk["source_spans"]] == [1, 2]
    assert "page" not in chunk  # no single fabricated page


def test_unknown_page_stays_unknown():
    [chunk] = of_type(build([course("CS 104", cells=[cell("t0-d1", "CS 104", page=None)])])[0], "course")
    assert chunk["pages"] == [] and chunk["source_spans"][0]["page"] is None


def test_prerequisite_without_source_cells_is_rejected():
    chunks, rejected = build([course("CS 101"), course("CS 102", prereq="CS 101", cells=[])])
    assert [c["course_code"] for c in of_type(chunks, "course")] == ["CS 101"]
    assert rejected == [{"chunk_type": "course", "label": "CS 102", "reason": "no_valid_source_cells"}]


def test_prerequisite_text_missing_from_the_cells_is_rejected():
    stray = course("CS 102", prereq="MATH 7", cells=[cell("t0-x1", "CS 102"), cell("t0-x2", "Intro", col=1)])
    chunks, rejected = build([course("CS 101"), stray])
    assert [c["course_code"] for c in of_type(chunks, "course")] == ["CS 101"]
    assert rejected[0]["reason"] == "prerequisite_not_in_source_text"


def test_rejected_course_is_left_out_of_its_term_summary():
    chunks, _ = build([course("CS 101"), course("CS 102", prereq="CS 101", cells=[])])
    [term] = of_type(chunks, "term_schedule")
    assert "CS 102" not in term["text"] and term["omitted_course_codes"] == ["CS 102"]


def test_course_over_the_hard_cap_is_rejected_not_truncated():
    chunks, rejected = build([course("CS 101"), course("CS 999", title="word " * 600)])
    assert "CS 999" not in [c.get("course_code") for c in chunks]
    assert any(r["label"] == "CS 999" and r["reason"] == "over_token_cap" for r in rejected)
    assert all(chunking.fits_cap(c["token_count"]) for c in chunks)
```

- [ ] **Step 2: Run and confirm the new tests fail**

Run the Phase E tests. Expected: the 7 primitive tests pass; the 11 new tests fail with `TypeError: build_semantic_rag_chunks() got an unexpected keyword argument 'pdf_sha256'` (the helpers `build` pass it).

- [ ] **Step 3: Replace `rag.py` with the final content**

```python
"""Semantic and layout RAG chunks, source-linked and edition-stable (Phase E)."""

from __future__ import annotations

from typing import Any
from typing import Sequence

from .common import RICH_AVAILABLE

if RICH_AVAILABLE:
    from .common import track
from .docling_env import load_docling
from .text import clean_str
from .evidence import LoadedDocument
from .courses import _iter_text_pairs
from .views import build_unlocks_map
from .chunking import (
    assemble_chunk,
    course_rejection,
    fits_cap,
    make_span,
    pack_items,
    spans_from_cells,
    spans_from_text_items,
)


def _cells(course: dict[str, Any]) -> list[dict[str, Any]]:
    return (course.get("provenance") or {}).get("source_cells") or []


def _emit(
    chunks: list[dict[str, Any]], rejected: list[dict[str, Any]], chunk: dict[str, Any], label: str
) -> None:
    if fits_cap(chunk["token_count"]):
        chunks.append(chunk)
    else:
        rejected.append(
            {
                "chunk_type": chunk["chunk_type"],
                "label": label,
                "reason": "over_token_cap",
                "token_count": chunk["token_count"],
            }
        )


def build_semantic_rag_chunks(
    metadata: dict[str, Any],
    courses: Sequence[dict[str, Any]],
    elective_tracks: Sequence[dict[str, Any]],
    term_units: Sequence[dict[str, Any]],
    *,
    pdf_sha256: str | None = None,
    source_kind: str = "",
    text_items: Sequence[Any] = (),
    rejected: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Advising-shaped chunks: one per course, per term part, per elective pool part, plus an overview.

    A course without valid source cells, or whose prerequisite words are not in its cells, is not
    chunked and is recorded in ``rejected`` (Decision D2). Summaries leave such courses out.
    """
    chunks: list[dict[str, Any]] = []
    rejected = rejected if rejected is not None else []
    degree = metadata.get("degree") or metadata.get("program_name") or "the program"
    college = metadata.get("college_name") or "PalSU"
    school_year = metadata.get("effective_school_year") or "n/a"
    source = metadata.get("source_file", "")
    unlocks = build_unlocks_map(courses)

    def spans_of(members: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
        cells = [cell for member in members for cell in _cells(member)]
        return spans_from_cells(cells, pdf_sha256, source_kind, "aggregate")

    def emit(chunk_type: str, label: str, fields: dict[str, Any], text: str, spans: list[dict[str, Any]]) -> None:
        chunk = assemble_chunk(chunk_type, fields, text, spans, pdf_sha256=pdf_sha256, source=source)
        _emit(chunks, rejected, chunk, label)

    def refuse(chunk_type: str, label: str, reason: str) -> None:
        rejected.append({"chunk_type": chunk_type, "label": label, "reason": reason})

    accepted: list[dict[str, Any]] = []
    for course in courses:
        reason = course_rejection(course)
        if reason:
            refuse("course", course["course_code"], reason)
        else:
            accepted.append(course)
    accepted_ids = {id(course) for course in accepted}

    total_units = sum(c.get("total_units") or 0 for c in courses)
    overview = [
        f"### Program Overview: {metadata.get('program_name') or degree}",
        f"- **Degree**: {degree}",
        f"- **College**: {college} ({metadata.get('college_code') or 'n/a'}), {metadata.get('campus')}",
        f"- **Effective School Year**: {school_year}",
        f"- **Total Units**: {total_units} across {len(courses)} courses",
        "- **Terms**: " + ", ".join(
            "{0} {1}".format(t["year_level"], t["semester"]) for t in term_units
        ),
    ]
    if metadata.get("bor_resolution"):
        overview.append(f"- **BOR Resolution**: {metadata['bor_resolution']} {metadata.get('bor_date') or ''}".rstrip())
    emit(
        "program_overview",
        "program",
        {
            "college": metadata.get("college_code"),
            "program": degree,
            "section_path": [degree],
            # These lines come from the file name, the semantic map and document text, not from table cells.
            "unsourced_fields": ["program", "college", "effective_school_year"]
            + (["bor_resolution"] if metadata.get("bor_resolution") else []),
        },
        "\n".join(overview) + "\n",
        spans_of(courses),
    )

    for course in accepted:
        code = course["course_code"]
        prereqs = course.get("prerequisites", [])
        unresolved = course.get("prerequisites_unresolved", [])
        standing = course.get("standing_requirements", [])
        prereq_text = ", ".join(prereqs) if prereqs else "None"
        if unresolved:
            prereq_text += f" (unverified in this document: {', '.join(unresolved)})"
        if standing:
            prereq_text += f" (Policy: {'; '.join(standing)})"
        opened = unlocks.get(code, [])
        units = course.get("units", {})
        body = [
            f"### Course: {code} - {course['course_title']}",
            f"- **Program**: {degree} ({college}, SY {school_year})",
            f"- **When taken**: {course['year_level']}, {course['semester']}",
            f"- **Units**: {units.get('total') or 'n/a'} total "
            f"(lecture {units.get('lecture') or 0}, laboratory {units.get('lab') or 0})",
            f"- **Prerequisites**: {prereq_text}",
            f"- **Unlocks**: {', '.join(opened) if opened else 'No downstream course depends on it'}",
            f"- **Classification**: {course.get('category')}"
            + (f" / elective pool {course['elective_group']}" if course.get("elective_group") else ""),
        ]
        provenance = course.get("provenance") or {}
        emit(
            "course",
            code,
            {
                "course_code": code,
                "course_title": course["course_title"],
                "year_level": course["year_level"],
                "semester": course["semester"],
                "college": metadata.get("college_code"),
                "program": degree,
                "section_path": [degree, course["year_level"], course["semester"]],
            },
            "\n".join(body) + "\n",
            spans_from_cells(
                _cells(course),
                pdf_sha256,
                source_kind,
                provenance.get("resolution_method") or "deterministic",
                provenance.get("repair_id"),
            ),
        )

    for term in term_units:
        year, semester = term["year_level"], term["semester"]
        in_term = [c for c in courses if (c["year_level"], c["semester"]) == (year, semester)]
        term_courses = [c for c in in_term if id(c) in accepted_ids]
        omitted = [c["course_code"] for c in in_term if id(c) not in accepted_ids]
        label = f"{year} {semester}"
        if not term_courses:
            refuse("term_schedule", label, "no_accepted_courses")
            continue
        declared = term.get("declared_units")
        checksum = (
            f"- **Printed total in prospectus**: {declared}\n" if declared is not None else ""
        )

        def head(part_label: str = "", year=year, semester=semester, term=term, checksum=checksum,
                 count=len(term_courses)) -> str:
            return (
                f"### Term Schedule: {degree} - {year}, {semester}{part_label}\n"
                f"- **College**: {college}\n"
                f"- **Effective School Year**: {school_year}\n"
                f"- **Courses**: {count}\n"
                f"- **Total units this term**: {term['computed_units']}\n"
                f"{checksum}"
                "- **Course list**:"
            )

        items = [
            (
                f"  - **{c['course_code']}**: {c['course_title']} "
                f"({c.get('total_units')} units; prerequisites: "
                f"{', '.join(c.get('prerequisites', [])) or 'None'})",
                c,
            )
            for c in term_courses
        ]
        parts = pack_items(head(), items)  # Decision D5: split at 400, never merge
        for number, (lines, members) in enumerate(parts, 1):
            part_label = f" (part {number} of {len(parts)})" if len(parts) > 1 else ""
            emit(
                "term_schedule",
                label,
                {
                    "year_level": year,
                    "semester": semester,
                    "college": metadata.get("college_code"),
                    "program": degree,
                    "section_path": [degree, year, semester],
                    "part_index": number,
                    "part_count": len(parts),
                    "omitted_course_codes": omitted,
                },
                head(part_label) + "\n" + "\n".join(lines) + "\n",
                spans_of(members),
            )

    by_code = {c["course_code"]: c for c in courses}
    for track in elective_tracks:
        items = [
            (f"  - **{o['course_code']}**: {o['course_title']}", o) for o in track["options"]
        ]
        slots = track.get("curriculum_slots") or []

        def pool_head(part_label: str = "", track=track, slots=slots) -> str:
            return (
                f"### Elective Pool: {track['group']} ({degree}){part_label}\n"
                f"- **Taken as**: {', '.join(slots) if slots else 'see curriculum'}\n"
                f"- **Choose one of**:"
            )

        parts = pack_items(pool_head(), items)
        for number, (lines, options) in enumerate(parts, 1):
            spans = spans_from_text_items(
                text_items, [o.get("source_item_id") for o in options], pdf_sha256, source_kind
            )
            if not spans:
                refuse("elective_pool", track["group"], "no_source_text_items")
                continue
            spans += spans_of([by_code[code] for code in slots if code in by_code])
            part_label = f" (part {number} of {len(parts)})" if len(parts) > 1 else ""
            emit(
                "elective_pool",
                track["group"],
                {
                    "elective_group": track["group"],
                    "college": metadata.get("college_code"),
                    "program": degree,
                    "section_path": [degree, track["group"]],
                    "part_index": number,
                    "part_count": len(parts),
                },
                pool_head(part_label) + "\n" + "\n".join(lines) + "\n",
                spans,
            )

    policy_courses = [c for c in accepted if c.get("standing_requirements")]
    if policy_courses:
        policy_head = (
            f"### Enrolment Policies and Standing Requirements ({degree})\n"
            "Some courses are gated by academic standing rather than by a specific course:"
        )
        items = [
            (
                f"  - **{c['course_code']}** ({c['year_level']}, {c['semester']}): "
                f"{'; '.join(c['standing_requirements'])}",
                c,
            )
            for c in policy_courses
        ]
        parts = pack_items(policy_head, items)
        for number, (lines, members) in enumerate(parts, 1):
            part_label = f" (part {number} of {len(parts)})" if len(parts) > 1 else ""
            emit(
                "enrolment_policy",
                "program",
                {
                    "college": metadata.get("college_code"),
                    "program": degree,
                    "section_path": [degree, "Enrolment policies"],
                    "part_index": number,
                    "part_count": len(parts),
                },
                policy_head.replace(f"({degree})", f"({degree}){part_label}", 1) + "\n" + "\n".join(lines) + "\n",
                spans_of(members),
            )

    return chunks


def build_hierarchical_rag_chunks(
    document: LoadedDocument,
    source_name: str,
    *,
    pdf_sha256: str | None = None,
    rejected: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Docling's own layout chunks when available, otherwise a labelled text fallback.

    Layout chunks over the token cap are not split here; they are recorded in ``rejected``.
    """
    rejected = rejected if rejected is not None else []
    kind = document.source_kind
    doc = document.docling_doc
    if doc is not None:
        try:
            dl = load_docling()
            chunker = dl["HierarchicalChunker"]()
            chunks: list[dict[str, Any]] = []
            skipped: list[dict[str, Any]] = []
            produced = False
            for index, chunk in enumerate(chunker.chunk(doc)):
                text = clean_str(getattr(chunk, "text", ""))
                if not text:
                    continue
                produced = True
                meta = getattr(chunk, "meta", None)
                meta_dict = meta.model_dump(mode="json") if hasattr(meta, "model_dump") else {}
                spans = [
                    make_span(pdf_sha256, prov.get("page_no"), {"kind": "docling_ref", "ref": item.get("self_ref")},
                              None, None, kind)
                    for item in meta_dict.get("doc_items") or []
                    for prov in item.get("prov") or []
                ]
                built = assemble_chunk(
                    "hierarchical_layout",
                    {
                        "chunk_index": index,
                        "section_path": list(meta_dict.get("headings") or []),
                        "metadata": meta_dict,
                    },
                    text,
                    spans,
                    pdf_sha256=pdf_sha256,
                    source=source_name,
                    source_text=text,
                    locator_fallback=f"docling_hierarchical:{index}",
                )
                _emit(chunks, skipped, built, f"docling_hierarchical:{index}")
            if produced:
                rejected.extend(skipped)
                return chunks
        except Exception:
            pass

    chunks = []
    for index, (label, text) in enumerate(_iter_text_pairs(document.text_items)):
        built = assemble_chunk(
            "hierarchical_layout_fallback",
            {"chunk_index": index, "section_path": [], "metadata": {"label": label}},
            text,
            [],
            pdf_sha256=pdf_sha256,
            source=source_name,
            source_text=text,
            locator_fallback=f"layout_fallback:{index}",
        )
        _emit(chunks, rejected, built, f"layout_fallback:{index}")
    return chunks
```

The policy header uses a `.replace` only to insert the part label after the program name; if that reads badly to the executor, build `policy_head(part_label)` as a small function like `head` and `pool_head` above. Behaviour must stay the same.

- [ ] **Step 4: Run the Phase E tests**

Expected: all 18 pass. If `test_prerequisite_without_source_cells_is_rejected` shows an extra rejection, a term or pool path refused something; read the `rejected` list before changing any test.

- [ ] **Step 5: Run the full suite and the self-test**

Expected: the suite is green. The self-test must still be 80/80: `selftest.py:583` asserts `not no_semester["rag"]["semantic_chunks"]` for an error audit, and `build_payload` is not edited yet, so the old call still works because every new parameter has a default. If the self-test or any existing test reads `chunk["id"]`, stop and report; none was found at `8d26f18`.

- [ ] **Step 6: Update the progress file and commit**

```
git add backend/bintanong_tools/prospectus_extractor/rag.py tests/test_prospectus_chunks.py plans/plan_current_progress/extractor_split_progress.md
git commit -m "feat: source-linked, hash-stable course and summary chunks"
```

---



### Task 4: Summary chunks list every contributing span

**Files:**
- Modify: `tests/test_prospectus_chunks.py` (append)
- Modify: `backend/bintanong_tools/prospectus_extractor/courses.py` (`parse_elective_tracks`, 122-160)

`rag.py` already contains the summary logic from Task 3; this task adds the tests that exercise it and the one change outside `rag.py`: elective options need a `source_item_id`. The outline listed only `rag.py` and `pipeline.py`; elective tracks carry no source information today, so this small extra change is required for "elective summaries list all contributing spans". It adds a key to track options and changes no course value.

- [ ] **Step 1: Append the failing tests**

```python
def test_term_and_overview_list_every_contributing_page():
    first = course("CS 101", cells=[cell("t0-a1", "CS 101", page=1), cell("t0-a2", "Intro", page=1, col=1)])
    second = course("CS 102", cells=[cell("t0-b1", "CS 102", page=2, row=5), cell("t0-b2", "Algo", page=2, row=5, col=1)])
    chunks, _ = build([first, second])
    [term] = of_type(chunks, "term_schedule")
    assert term["pages"] == [1, 2]
    assert sorted({s["page"] for s in term["source_spans"]}) == [1, 2]
    assert {"t0-a1", "t0-b2"} <= set(term["cell_ids"])
    assert "page" not in term
    [overview] = of_type(chunks, "program_overview")
    assert overview["pages"] == [1, 2]
    assert "program" in overview["unsourced_fields"]


def test_large_term_is_split_into_parts_that_repeat_the_header():
    many = [course(f"CS {n}", title="Advanced Topic " + "word " * 12) for n in range(100, 140)]
    chunks, rejected = build(many)
    parts = of_type(chunks, "term_schedule")
    assert rejected == [] and len(parts) >= 2
    assert [p["part_index"] for p in parts] == list(range(1, len(parts) + 1))
    assert {p["part_count"] for p in parts} == {len(parts)}
    assert all(p["text"].startswith("### Term Schedule: BS Test - 1st Year, 1st Semester (part ") for p in parts)
    assert all(p["token_count"] <= chunking.TOKEN_SPLIT_AT + 10 for p in parts)
    for n in range(100, 140):
        assert sum(f"**CS {n}**" in p["text"] for p in parts) == 1
    assert len({p["chunk_id"] for p in parts}) == len(parts)


def test_elective_options_remember_the_text_item_they_came_from():
    items = [{"item_id": "text-7", "label": "text", "text": "CS Elect 4/La. Machine Learning", "page": 2, "bbox": None}]
    [pool] = parse_elective_tracks(items)
    assert pool["options"] == [
        {"course_code": "CS Elect 4/La", "course_title": "Machine Learning", "source_item_id": "text-7"}]
    [legacy] = parse_elective_tracks([("text", "CS Elect 4/La. Machine Learning")])
    assert legacy["options"][0]["source_item_id"] is None


def test_elective_pool_lists_text_item_and_slot_spans():
    items = [{"item_id": "text-7", "label": "text", "text": "CS Elect 4/La. Machine Learning", "page": 2, "bbox": None}]
    tracks = parse_elective_tracks(items)
    tracks[0]["curriculum_slots"] = ["CS Elect 4/L"]
    slot = course("CS Elect 4/L", title="CS Elective 4")
    chunks, rejected = build([slot], tracks, items)
    [pool] = of_type(chunks, "elective_pool")
    assert rejected == []
    assert {s["locator"]["kind"] for s in pool["source_spans"]} == {"text_item", "table_cells"}
    assert pool["pages"] == [1, 2]
    assert "text-7" in [i for s in pool["source_spans"] for i in s["locator"].get("item_ids", [])]


def test_elective_pool_without_source_items_is_rejected():
    track = {"group": "CS Elective 9", "elective_number": 9, "curriculum_slots": [],
             "options": [{"course_code": "CS Elect 9/La", "course_title": "X"}]}
    chunks, rejected = build([course("CS 101")], [track], [])
    assert of_type(chunks, "elective_pool") == []
    assert {"chunk_type": "elective_pool", "label": "CS Elective 9", "reason": "no_source_text_items"} in rejected


def test_policy_summary_lists_the_cells_of_its_courses():
    gated = course("CS 401", standing=("4th Year Standing",))
    chunks, _ = build([course("CS 101"), gated])
    [policy] = of_type(chunks, "enrolment_policy")
    assert "CS 401" in policy["text"] and "CS 101" not in policy["text"]
    assert set(policy["cell_ids"]) == {c["cell_id"] for c in gated["provenance"]["source_cells"]}
    assert policy["section_path"] == ["BS Test", "Enrolment policies"]
```

- [ ] **Step 2: Run and confirm the failures**

Run the Phase E tests. Expected: `test_elective_options_remember_the_text_item_they_came_from` and `test_elective_pool_lists_text_item_and_slot_spans` fail (options have no `source_item_id`); the elective-without-source test passes already; the term, split and policy tests pass because Task 3 wrote that logic. If any of those three fail, fix `rag.py`, not the test.

- [ ] **Step 3: Add `source_item_id` in `parse_elective_tracks`**

In `courses.py`, replace the loop header and the option append. The loop now walks the items so it knows each item's ID:

```python
    for item in text_items:
        item_id = item.get("item_id") if isinstance(item, Mapping) else None
        for _label, text in _iter_text_pairs([item]):
            line = clean_str(text)
            if not line:
                continue
            for candidate in re.split(r"(?<=[a-z\)])\s{2,}", line):
                match = ELECTIVE_OPTION.match(clean_str(candidate))
                if not match:
                    continue
                option_code = clean_str(match.group(1))
                number = match.group(2)
                title = clean_str(match.group(3))
                prefix_match = re.match(r"^([A-Za-z]+)", option_code)
                prefix = prefix_match.group(1).upper() if prefix_match else "CS"
                group_name = f"{prefix} Elective {number}"
                if group_name not in grouped:
                    grouped[group_name] = []
                    order.append(group_name)
                if not any(o["course_code"] == option_code for o in grouped[group_name]):
                    grouped[group_name].append(
                        {"course_code": option_code, "course_title": title, "source_item_id": item_id}
                    )
```

This is the same body as lines 132-150 re-indented one level, with only `item_id` and the new dict key added. Keep the `return` block (152-160) as is.

- [ ] **Step 4: Run Phase E tests, full suite, self-test**

Expected: all pass, self-test 80/80 (`CS: each elective pool has four options` still holds; the extra key does not change the option count). `prolog.py` reads only `course_code` and `course_title` of options; confirm with `Select-String -Path backend\bintanong_tools\prospectus_extractor\prolog.py -Pattern "options"` and record that nothing iterates option keys.

- [ ] **Step 5: Update the progress file and commit**

```
git add backend/bintanong_tools/prospectus_extractor/courses.py tests/test_prospectus_chunks.py plans/plan_current_progress/extractor_split_progress.md
git commit -m "feat: summary chunks list every contributing source span"
```

---

