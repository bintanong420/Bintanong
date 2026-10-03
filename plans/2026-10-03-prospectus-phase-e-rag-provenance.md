# Prospectus Phase E: Source-Linked, Edition-Stable RAG Chunks Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Tasks are run by the project agent `extractor-implementer` and reviewed by `extractor-reviewer`. Append a Phase E section to `plans/plan_current_progress/extractor_split_progress.md` after every task commit.

**Goal:** Every RAG candidate chunk the extractor emits names the PDF it came from (SHA-256), the page(s), table index and cell IDs it came from, keeps the printed source text apart from the advising-style summary, gets an ID that is stable for one PDF and different for another edition, and is length-checked against the 512-token embedding cap. Nothing is embedded and no vector is written.

**Architecture:** One new pure module `prospectus_extractor/chunking.py` (IDs, source spans, token budget, line packing) and a rewrite of `rag.py` on top of it. The chunk dict is defined here so each field maps one-to-one onto the master plan section 6.2 `Chunk`/`SourceSpan` minimum fields; no `backend/app/contracts/` exists yet (there is no `backend/app/` at all), so nothing is imported from there. `build_payload` gains one keyword (`pdf_sha256`) and the `rag` block gains `rejected_chunks`. Elective options gain a `source_item_id` so elective summaries can list their text spans.

**Tech Stack:** Python 3.13 stdlib only (`hashlib`, `json`, `unicodedata`, `math`), pytest 9, `uv`. No new dependency.

**Base:** branch `feature/prospectus-phase-e-rag-provenance`, created from `dev` after Phase D merges. This plan was written against `8d26f18` (Phase A merged; B to D not yet). Line numbers below are as of `8d26f18` and Task 1 re-checks them.

**Status:** Part of the review-only prospectus workstream. Chunks stay candidates. Nothing here approves a curriculum, activates RAG or Prolog, embeds, or writes to a database.

---

## Decisions needed before execution

The rest of the plan assumes the recommendation in each row. Steps that would change are marked **(D1)** to **(D5)**.

| # | Question | Options | Recommendation |
| --- | --- | --- | --- |
| **D1** | Which token counter checks the 512-token cap? The embedding model is `aisingapore/SEA-LION-E5-Embedding-600M` (local folder `SEA-LION-E5-Embedding-600M`, `backend/bintanong_embedding/main.py:12`; master section 2 says 1,024 dimensions and a 512-token limit). Its tokenizer files are **not** on this machine (`C:\Coding-projects\MODELS\SEA-LION-E5-Embedding-600M` does not exist) and are not in the `tools` extra. `tokenizers` 0.23.2 and `transformers` 5.17.0 are present only as transitive Docling dependencies, unpinned. | (a) Exact tokenizer loaded from the model folder as an optional dependency. (b) Conservative estimate with a safety margin, tagged `token_count_method: "estimate-v1"`. (c) Do not measure until Phase 3. | **(b) now, exact in Phase 3.** The estimate is `max(ceil(chars / 3), ceil(words * 1.8))` plus a reserve of 32 tokens for prompt prefix and special tokens (master section 7.2 says the cap must include both). It deliberately over-counts, so a chunk that passes cannot exceed 512 in the real tokenizer. The method name is stored on each chunk so Phase 3 can replace the count without changing the shape. Task 8 has an optional calibration step that runs only if the tokenizer file exists on the executor's machine. (a) would add an unpinned dependency and a model-folder requirement to a review-only phase; (c) would let an over-length chunk through the review step unflagged. Steps marked **(D1)**: Task 2 `estimate_tokens`. |
| **D2** | A chunk whose source cells are missing or do not contain the asserted prerequisite text: exclude or keep flagged? | (a) Exclude it from the chunk list and record it in `rag.rejected_chunks` with a reason. (b) Keep it with `source_valid: false`. | **(a).** The draft (Task 6) says "reject chunks with unresolved source spans as active candidates", and a flagged chunk is one filter away from being embedded by a careless consumer. Nothing is lost: the reviewer sees every rejection in the payload. A rejected course is also left out of its term, elective-slot and policy summaries, which record `omitted_course_codes`. Steps marked **(D2)**: Task 3 and Task 4. |
| **D3** | A run from a cached `*_docling.json` has no PDF in hand, so no `pdf_sha256`. Refuse to emit chunks, or emit them unanchored? | (a) Refuse. (b) Emit with `pdf_sha256: null` and `source_anchored: false`, ID salted with the literal `unanchored`. | **(b).** The 44-input regression and the review workflow run from cached Docling JSON, so refusing would make Phase E untestable on real data. Unanchored chunks are labelled and must never be loaded as institutional chunks: Phase 3 and 4 loaders must reject `source_anchored: false`. Two unanchored editions with identical text and cell IDs would share an ID, which is exactly why they are unusable. The hash comes from the PDF file when the input is a PDF (see Dependencies). Steps marked **(D3)**: Task 6. |
| **D4** | Field names visible to downstream consumers, and which text is the embedding candidate. | (a) Rename `id` to `chunk_id`; keep `text` as the advising summary (the embedding candidate); add `source_text` (printed text, never embedded). (b) Keep `id`. (c) Embed `source_text`, or both. | **(a).** `chunk_id` matches the section 6.2 name, and nothing in the repository reads the old `id` key (`grep` found only the writer). The advising summary is a fixed template over extracted fields, so embedding it keeps retrieval phrasing consistent; `source_text` is what a citation shows. Steps marked **(D4)**: Task 3. |
| **D5** | The 300 to 400 token target (master section 7.2). Merge small chunks up to it, or only split large ones? | (a) Split at 400 estimated tokens, never merge. (b) Also merge small chunks. | **(a).** A course chunk is deliberately one course (about 80 tokens) so a retrieved chunk can be cited for exactly one course. Term, elective and policy summaries split at 400 and repeat their header per part. Task 8 reports the real token distribution so the target can be revisited with data. Steps marked **(D5)**: Task 4. |

## Dependencies on earlier phases (checked against `8d26f18`)

- **PDF hash.** At `8d26f18` nothing in the package knows the PDF hash. `prospectus_batch.py:59` hashes the PDF only for the batch manifest, and `ProvisionalSource(pdf_sha256, source_locator)` in `backend/bintanong_tools/prospectus.py` exists but the extractor never imports it. Phase C adds `source_verification` from `ProvisionalSource` and Phase D puts the PDF SHA-256 in the cache key. Phase E therefore takes `pdf_sha256` as an explicit keyword on `build_payload` and computes it in `process_prospectus` from the PDF bytes (`hashlib.file_digest`, the same call `ProvisionalSource.verify_pdf` uses). **Task 1 must look at what Phases C and D added.** If either already puts the hash in the payload or passes a `ProvisionalSource` into `build_payload`, use that value and delete the helper written in Task 6 rather than computing the hash twice. Do not read the hash back out of the Docling JSON: its `origin.binary_hash` is Docling's own integer, not SHA-256.
- **Audit gate.** `build_payload` emits no chunks when the audit status is `error` (`pipeline.py:52-71`). Phase C changes the audit and status fields; Phase E keeps that gate and never emits chunks for an error audit. Of the six cached inputs tried on 3 October only one (`ABPhilStud`, status `warn`) produced chunks; `BSA`, both `ABComm` and both `PolSci` inputs were `error`. This matters for the gate in Task 8.
- **OCR room.** Source spans carry `extraction.source_kind` (copied from `document.source_kind`) and `extraction.ocr_confidence: null`. A later OCR path can fill both without a shape change. Nothing here assumes a born-digital text layer.

## What exists today (read from the code at `8d26f18`)

- `rag.py:19-171` `build_semantic_rag_chunks(metadata, courses, elective_tracks, term_units)` returns dicts with `id` (`"<code>::course"`, `"<year>_<semester>::term"`, `"<group>::elective"`, `"program::overview"`, `"program::policies"`), `text`, `source` (the file name) and a few labels. No hash, page, table or cell ID. `rag.py:174-212` `build_hierarchical_rag_chunks(document, source_name)` returns Docling layout chunks with `id` `"docling_hierarchical::<index>"` or `"layout_fallback::<index>"`.
- Each finalised course already carries what is needed: `course["provenance"]` is built by `_make_provenance` (`sections.py:841-864`) with `table_index`, `source_cell_ids`, `source_cells` (full cell dicts including `cell_id`, `table_index`, `text`, `row_start`, `col_start`, `page`, `bbox`), `page`, `bbox`, `resolution_method`, `repair_id`, `valid`, `highlightable`. **`provenance["page"]` is `None` whenever the cells span more than one page** (`_union_bbox`, `sections.py:825-838`), so the per-cell `page` values are the truth and the chunker must group by them. Real data, 3 October, `ABPhilStud`: all 48 courses are single-page, `valid: true`, `highlightable: true`; `source_cells` includes the year/semester banner cell as well as the course cells.
- Elective tracks (`courses.py:122-160`) are `{"group", "elective_number", "options": [{"course_code", "course_title"}], "curriculum_slots"}`. They carry no source information. Text items (`loader.py:178-195`) do: `{"item_id": "text-N", "label", "text", "page", "bbox"}`.
- `pipeline.py:56-57` builds the chunks, `pipeline.py:104` puts `{"semantic_chunks", "hierarchical_chunks"}` in `payload["rag"]`, `pipeline.py:248-254` writes `_rag.jsonl` with `open("w", encoding="utf-8")` (no `newline`).
- A real `_rag.jsonl` (older batch, `batch 6\...\PolSci-for-student-new-version\prospectus_rag.jsonl`, 60 lines) confirms the old shape: 45 `course`, 8 `term_schedule`, 1 `program_overview`, 6 `hierarchical_layout`, none with a page or hash. A fresh run of `ABPhilStud` on 3 October (`$env:TEMP\phaseE_rag\r4`) gave 48 course, 8 term and 1 overview chunks. The term chunks are 58 to 123 words each. One Docling layout chunk in that run is **1,980 words** (a whole table in one chunk), so it exceeds 512 tokens several times over; Docling's `HierarchicalChunker` does not split by tokens.

## Chunk shape (maps to master section 6.2)

`SourceSpan` (one per table-and-page group, or per text item, or per Docling item):

| Field | Meaning | Section 6.2 field |
| --- | --- | --- |
| `pdf_sha256` | SHA-256 of the PDF, or `null` (D3). Becomes a `SourceDocumentVersion` ID later without changing. | document version |
| `page` | PDF page position, 1-based as Docling reports it; `null` when unknown. Never a guess. | PDF page position |
| `printed_page_label` | Always `null` today (not extracted). | printed page label |
| `locator` | `{"kind": "table_cells", "table_index": int, "cell_ids": [...]}`, `{"kind": "text_item", "item_ids": [...]}` or `{"kind": "docling_ref", "ref": "#/texts/2"}` | section/table locator |
| `text` | Printed text of those cells, joined with ` \| ` in reading order; `null` for Docling refs. | text |
| `bbox` | Union box `[left, top, right, bottom]` or `null` | (extra) |
| `extraction` | `{"source_kind", "resolution_method", "repair_id", "ocr_confidence"}` | extraction provenance |

`Chunk`:

| Field | Meaning | Section 6.2 field |
| --- | --- | --- |
| `chunk_id` | SHA-256 over `[pdf_sha256 or "unanchored", locator key, content_hash, CHUNKER_VERSION]` | chunk ID |
| `chunk_type`, `part_index`, `part_count` | kind, and part numbers when a summary is split | (extra) |
| `source_spans`, plus derived `pages`, `table_indexes`, `cell_ids` | all contributing spans; the flat lists are for easy filtering | source spans |
| `text` | advising-style summary; the embedding candidate (D4) | content |
| `source_text` | canonical printed text of the spans; never embedded | content |
| `section_path` | `[program, year, semester]` and similar | section path |
| `college`, `program` | existing labels, kept | scope (full scope object is left to the Phase F adapter) |
| `token_count`, `token_count_method` | estimate and its name (D1) | token count |
| `content_hash` | SHA-256 of `[canonical(source_text), canonical(text)]` | content hash |
| `chunker_version` | `palsu-chunker-v1` | chunker version |
| `pdf_sha256`, `source_anchored` | hash and whether it is real (D3) | document version |
| `content_review` | always `"pending"` | (review state) |
| `source` | file name, kept | (extra) |

## File structure

| File | Change | Responsibility |
| --- | --- | --- |
| `backend/bintanong_tools/prospectus_extractor/chunking.py` | **create** | Constants, `estimate_tokens`, `fits_cap`, `canonical_text`, `content_hash`, `make_span`, `spans_from_cells`, `spans_from_text_items`, `locator_key`, `make_chunk_id`, `course_rejection`, `pack_items`, `assemble_chunk`. Imports only the standard library. |
| `backend/bintanong_tools/prospectus_extractor/rag.py` | rewrite (lines 1-212) | Builds the chunks with the helpers above. |
| `backend/bintanong_tools/prospectus_extractor/courses.py` | modify `parse_elective_tracks` (122-160) | Add `source_item_id` to each elective option. |
| `backend/bintanong_tools/prospectus_extractor/pipeline.py` | modify (25-126, 174-263) | `pdf_sha256` keyword, new `rag` block, jsonl `newline`. |
| `backend/bintanong_tools/prospectus_extractor/common.py` | modify line 8 | Bump `SCHEMA_VERSION`. |
| `tests/test_prospectus_chunks.py` | **create** | All Phase E tests. |

The module order rule from Phase A still holds: `chunking.py` imports nothing from the package, and `rag.py` imports it.

## Commands used throughout

```
# Full suite (observed baseline at 8d26f18: 36 passed, 13 subtests passed)
uv run --project backend --extra tools --extra dev --with fastapi==0.141.1 python -m pytest -q tests

# Phase E tests only
uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_chunks.py

# Self-test (baseline 80/80)
uv run --project backend --extra tools --extra dev python -m backend.bintanong_tools.prospectus_extractor --self-test
```

Commit rule for every task: stage by explicit path, never `.gitignore` or `plans/CODEX_HANDOFF_prospectus_extractor_phase2_2026-09-26.md`, and end each message with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

---

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

### Task 5: Layout chunks get IDs, pages and a token check

**Files:**
- Modify: `tests/test_prospectus_chunks.py` (append)

`build_hierarchical_rag_chunks` was already rewritten in Task 3. This task proves it. Decision: layout chunks over the cap are rejected, not split, because they are Docling's own units and the curriculum facts are already covered by course and term chunks; the real data has one 1,980-word table chunk.

- [ ] **Step 1: Append the tests**

```python
def _layout_document(text_items=(), docling_document=None):
    return ProspectusEvidence(
        text_items=list(text_items), docling_document=docling_document, source_kind="docling-json")


def test_fallback_layout_chunks_are_hash_bound_and_capped():
    document = _layout_document([
        {"item_id": "text-0", "label": "title", "text": "BS TEST CURRICULUM", "page": 1, "bbox": None},
        {"item_id": "text-1", "label": "text", "text": "word " * 700, "page": 1, "bbox": None},
    ])
    rejected = []
    chunks = rag.build_hierarchical_rag_chunks(document, "t.pdf", pdf_sha256=PDF_A, rejected=rejected)
    assert [c["chunk_type"] for c in chunks] == ["hierarchical_layout_fallback"]
    assert chunks[0]["pdf_sha256"] == PDF_A and chunks[0]["content_review"] == "pending"
    assert chunks[0]["source_text"] == "BS TEST CURRICULUM"
    again = rag.build_hierarchical_rag_chunks(document, "t.pdf", pdf_sha256=PDF_B)
    assert again[0]["chunk_id"] != chunks[0]["chunk_id"]
    assert [(r["label"], r["reason"]) for r in rejected] == [("layout_fallback:1", "over_token_cap")]


def test_docling_layout_chunks_carry_their_pages(monkeypatch):
    meta = SimpleNamespace(model_dump=lambda mode="json": {
        "headings": ["FIRST YEAR"],
        "doc_items": [{"self_ref": "#/texts/2", "prov": [{"page_no": 2}]}],
    })
    chunk = SimpleNamespace(text="Effective SY 2018-2019", meta=meta)
    fake = SimpleNamespace(chunk=lambda doc: [chunk])
    monkeypatch.setattr(rag, "load_docling", lambda: {"HierarchicalChunker": lambda: fake})
    chunks = rag.build_hierarchical_rag_chunks(_layout_document(docling_document=object()), "t.pdf", pdf_sha256=PDF_A)
    assert [c["chunk_type"] for c in chunks] == ["hierarchical_layout"]
    assert chunks[0]["pages"] == [2] and chunks[0]["section_path"] == ["FIRST YEAR"]
    assert chunks[0]["source_spans"][0]["locator"] == {"kind": "docling_ref", "ref": "#/texts/2"}


def test_all_oversized_docling_chunks_do_not_fall_back_to_the_text_path(monkeypatch):
    huge = SimpleNamespace(text="word " * 700, meta=None)
    fake = SimpleNamespace(chunk=lambda doc: [huge])
    monkeypatch.setattr(rag, "load_docling", lambda: {"HierarchicalChunker": lambda: fake})
    rejected = []
    chunks = rag.build_hierarchical_rag_chunks(
        _layout_document([{"item_id": "t", "label": "text", "text": "kept?", "page": 1, "bbox": None}],
                         docling_document=object()),
        "t.pdf", pdf_sha256=PDF_A, rejected=rejected)
    assert chunks == [] and rejected[0]["reason"] == "over_token_cap"
```

- [ ] **Step 2: Run**

Expected: all three pass at once, because the code exists. To make sure they can fail, temporarily change `TOKEN_HARD_CAP` to `10_000` in `chunking.py`, rerun, and confirm `test_fallback_layout_chunks_are_hash_bound_and_capped` and the last test fail; then revert the edit.

- [ ] **Step 3: Full suite, progress note, commit**

```
git add tests/test_prospectus_chunks.py plans/plan_current_progress/extractor_split_progress.md
git commit -m "test: pin layout chunk IDs, pages and token cap"
```

---

### Task 6: Wire the pipeline: hash, payload shape, jsonl, schema version

**Files:**
- Modify: `tests/test_prospectus_chunks.py` (append)
- Modify: `backend/bintanong_tools/prospectus_extractor/pipeline.py` (lines 25-126, 174-263)
- Modify: `backend/bintanong_tools/prospectus_extractor/common.py` (line 8)

- [ ] **Step 1: Append the failing end-to-end tests**

```python
import hashlib
import json
import time

from backend.bintanong_tools.prospectus_extractor import pipeline
from backend.bintanong_tools.prospectus_extractor.common import SCHEMA_VERSION
from backend.bintanong_tools.prospectus_extractor.pipeline import build_payload
from backend.bintanong_tools.prospectus_extractor.selftest import (
    CS_TEXT_ITEMS, cs_fixture_grid, fixture_document)


def _cs_payload(pdf):
    return build_payload(
        fixture_document(cs_fixture_grid(), CS_TEXT_ITEMS), Path("cs.pdf"),
        semantic_doc_path=None, pdf_sha256=pdf)


def _ids(payload):
    return [c["chunk_id"] for c in payload["rag"]["semantic_chunks"]]


def test_same_pdf_gives_same_ids_even_when_the_timestamp_differs():
    first = _cs_payload(PDF_A)
    time.sleep(1.1)  # generated_at has one-second resolution
    second = _cs_payload(PDF_A)
    assert first["generated_at"] != second["generated_at"]
    assert _ids(first) and _ids(first) == _ids(second)
    assert len(set(_ids(first))) == len(_ids(first))


def test_another_edition_shares_no_chunk_id():
    assert not set(_ids(_cs_payload(PDF_A))) & set(_ids(_cs_payload(PDF_B)))


def test_payload_rag_block_reports_chunker_and_rejections():
    payload = _cs_payload(PDF_A)
    rag_block = payload["rag"]
    assert payload["pdf_sha256"] == PDF_A
    assert rag_block["chunker_version"] == chunking.CHUNKER_VERSION
    assert rag_block["token_count_method"] == chunking.TOKEN_COUNT_METHOD
    assert rag_block["rejected_chunks"] == [], rag_block["rejected_chunks"]
    assert payload["quality_report"]["total_rejected_chunks"] == 0
    assert payload["schema_version"] == SCHEMA_VERSION
    for chunk in rag_block["semantic_chunks"] + rag_block["hierarchical_chunks"]:
        assert chunk["pdf_sha256"] == PDF_A and chunk["content_review"] == "pending"
        assert chunking.fits_cap(chunk["token_count"])
    for chunk in of_type(rag_block["semantic_chunks"], "course"):
        assert chunk["cell_ids"] and chunk["source_spans"] and chunk["source_text"]
    for chunk in of_type(rag_block["semantic_chunks"], "elective_pool"):
        assert any(s["locator"]["kind"] == "text_item" for s in chunk["source_spans"])


def test_blocked_audit_still_emits_no_chunks_and_no_rejections():
    from backend.bintanong_tools.prospectus_extractor.selftest import bsa_fixture_grid, BSA_TEXT_ITEMS
    payload = build_payload(
        fixture_document(bsa_fixture_grid(), BSA_TEXT_ITEMS), Path("bsa.pdf"),
        semantic_doc_path=None, pdf_sha256=PDF_A)
    assert payload["audit"]["status"] == "error"
    assert payload["rag"]["semantic_chunks"] == [] and payload["rag"]["rejected_chunks"] == []


def test_process_prospectus_hashes_the_pdf_and_writes_lf_jsonl(tmp_path, monkeypatch):
    pdf = tmp_path / "cs.pdf"
    pdf.write_bytes(b"%PDF-test")
    monkeypatch.setattr(
        pipeline, "load_document",
        lambda *_args, **_kwargs: (fixture_document(cs_fixture_grid(), CS_TEXT_ITEMS), None))
    pipeline.process_prospectus(
        pdf, tmp_path / "cs_prospectus.json", export_jsonl=True, semantic_doc_path=None, quiet=True)
    raw = (tmp_path / "cs_rag.jsonl").read_bytes()
    assert b"\r\n" not in raw
    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines()]
    assert rows and {r["pdf_sha256"] for r in rows} == {hashlib.sha256(b"%PDF-test").hexdigest()}
    assert all("chunk_id" in r and "id" not in r for r in rows)


def test_docling_json_input_runs_unanchored(tmp_path, monkeypatch):
    source = tmp_path / "cs_docling.json"
    source.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(
        pipeline, "load_document",
        lambda *_args, **_kwargs: (fixture_document(cs_fixture_grid(), CS_TEXT_ITEMS), source))
    payload = pipeline.process_prospectus(
        source, tmp_path / "cs_prospectus.json", semantic_doc_path=None, quiet=True)
    assert payload["pdf_sha256"] is None
    assert {c["source_anchored"] for c in payload["rag"]["semantic_chunks"]} == {False}
```

- [ ] **Step 2: Run and confirm the failures**

Expected: all six fail with `TypeError: build_payload() got an unexpected keyword argument 'pdf_sha256'` or `KeyError: 'pdf_sha256'`. (If Task 1 found that Phase C or D already passes the hash into `build_payload`, rename the keyword in these tests to match before running, and skip Step 3's helper.)

- [ ] **Step 3: Edit `pipeline.py`**

Imports: add `import hashlib` next to `import json`.

`build_payload` signature, add the keyword last:

```python
    repair_provider: SemanticRepairProvider | None = None,
    pdf_sha256: str | None = None,
) -> dict[str, Any]:
```

Replace lines 52-71 (the `verified` block) with:

```python
    verified = audit["status"] != "error"
    rejected_chunks: list[dict[str, Any]] = []
    if verified:
        prolog = generate_prolog_knowledge(metadata, courses, tracks, term_units)
        prolog["status"] = "verified"
        semantic_chunks = build_semantic_rag_chunks(
            metadata, courses, tracks, term_units,
            pdf_sha256=pdf_sha256,
            source_kind=document.source_kind,
            text_items=document.text_items,
            rejected=rejected_chunks,
        )
        hierarchical_chunks = build_hierarchical_rag_chunks(
            document, Path(input_path).name, pdf_sha256=pdf_sha256, rejected=rejected_chunks
        )
    else:
        prolog = {
            "status": "blocked",
            "reason": "audit status is error; institutional facts require review",
            "clauses": [],
            "relations": {
                "courses": [],
                "prerequisites": [],
                "standing_requirements": [],
                "elective_tracks": [],
            },
        }
        semantic_chunks = []
        hierarchical_chunks = []
```

If Phase C changed this block (for example it stopped embedding blocked Prolog), keep Phase C's `else` branch and only change the two `build_*` calls and the new `rejected_chunks` list.

In the payload dict: add `"pdf_sha256": pdf_sha256,` after `"source_path"`, and replace the `"rag"` entry with:

```python
        "rag": {
            "chunker_version": CHUNKER_VERSION,
            "token_count_method": TOKEN_COUNT_METHOD,
            "semantic_chunks": semantic_chunks,
            "hierarchical_chunks": hierarchical_chunks,
            "rejected_chunks": rejected_chunks,
        },
```

and add `"total_rejected_chunks": len(rejected_chunks),` after `"total_hierarchical_chunks"` in `quality_report`. Import the two constants: `from .chunking import CHUNKER_VERSION, TOKEN_COUNT_METHOD`.

Add the helper above `process_prospectus`:

```python
def _file_sha256(path: Path) -> str:
    with Path(path).open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()
```

In `process_prospectus`, after the `raw_cache_path` line (214) add:

```python
    pdf_sha256 = _file_sha256(input_path) if input_path.suffix.lower() == ".pdf" else None
```

and pass `pdf_sha256=pdf_sha256` in the `build_payload(...)` call (219-225). In the jsonl writer (249-252) change `jsonl_path.open("w", encoding="utf-8")` to `jsonl_path.open("w", encoding="utf-8", newline="\n")`.

**(D3)** For a Docling JSON input `pdf_sha256` stays `None`. Do not try to recover it from the JSON.

- [ ] **Step 4: Bump the schema version**

In `common.py:8` change `SCHEMA_VERSION` to the next minor of whatever Task 1 recorded (from `palsu-prospectus-v3.0` that is `palsu-prospectus-v3.1`; after earlier phases bumped it, one step further). Record in the progress file: "payload shape: new top-level `pdf_sha256`; `rag.semantic_chunks` and `rag.hierarchical_chunks` entries replace `id` with `chunk_id` and gain `chunker_version`, `content_review`, `pdf_sha256`, `source_anchored`, `source_text`, `source_spans`, `pages`, `table_indexes`, `cell_ids`, `content_hash`, `token_count`, `token_count_method`, `section_path`; new `rag.chunker_version`, `rag.token_count_method`, `rag.rejected_chunks`; new `quality_report.total_rejected_chunks`; elective options gain `source_item_id`."

- [ ] **Step 5: Run Phase E tests, full suite, self-test**

Expected: all pass, self-test 80/80. If `test_payload_rag_block_reports_chunker_and_rejections` fails on `rejected_chunks == []`, print the list and look at the reason: `prerequisite_not_in_source_text` on the CS fixture means a real course whose prerequisite words are not in its cells, which is a finding to report, not a reason to weaken the rule. Run `$env:TEMP`-style one-off to list them and record in the progress file; then decide with the controller.

- [ ] **Step 6: Update the progress file and commit**

```
git add backend/bintanong_tools/prospectus_extractor/pipeline.py backend/bintanong_tools/prospectus_extractor/common.py tests/test_prospectus_chunks.py plans/plan_current_progress/extractor_split_progress.md
git commit -m "feat: carry the PDF hash through the payload and emit source-linked chunks"
```

---

### Task 7: Regression: course fields unchanged on the 44 cached inputs

**Files:** no repository change. The comparer lives in `$env:TEMP\phaseE\course_fields_check.py` and is not added to Git. (It is adapted from the Phase A golden script, `git show 2dffe3d:scripts/prospectus_golden_check.py`, which compared whole payloads with run-to-run noise. Phase E needs a field-level comparison of old against new because the payload shape changes on purpose.)

- [ ] **Step 1: Write the comparer**

Create `$env:TEMP\phaseE\course_fields_check.py`:

```python
#!/usr/bin/env python3
"""Phase E regression: course fields and audit outcome unchanged between two code trees.

    python course_fields_check.py run ROOT OUT GOLDEN MAP     # one side
    python course_fields_check.py compare OLD_OUT NEW_OUT     # field-level diff
    python course_fields_check.py stats NEW_OUT               # Phase E chunk statistics
Run it under `uv run --project <repo>/backend --extra tools` so sys.executable has Docling.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

COURSE_KEYS = (
    "course_code", "course_title", "year_level", "semester", "term_index", "units",
    "prerequisites_raw", "prerequisites", "prerequisites_unresolved", "standing_requirements",
    "category", "is_elective", "elective_group",
)


def view(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        "courses": [{k: c.get(k) for k in COURSE_KEYS} for c in data["courses"]],
        "tracks": [
            {"group": t["group"], "slots": t.get("curriculum_slots"),
             "options": [{"course_code": o["course_code"], "course_title": o["course_title"]} for o in t["options"]]}
            for t in data["elective_tracks"]
        ],
        "audit": data["audit"]["status"],
        "errors": data["audit"]["errors"],
    }


def run(root: Path, out: Path, golden: Path, semantic_map: Path) -> None:
    sources = sorted(golden.rglob("*_docling.json"))
    env = dict(os.environ, PYTHONHASHSEED="0", PYTHONIOENCODING="utf-8")
    for number, source in enumerate(sources, 1):
        target = out / f"{number:02d}"
        target.mkdir(parents=True, exist_ok=True)
        (target / "source.txt").write_text(str(source), encoding="utf-8")
        done = subprocess.run(
            [sys.executable, "-m", "backend.bintanong_tools.prospectus_extractor", "-i", str(source),
             "-o", str(target / "candidate.json"), "--export-all", "--device", "cpu",
             "--semantic-doc", str(semantic_map)],
            cwd=root, env=env, capture_output=True,
        )
        (target / "exit.txt").write_text(str(done.returncode), encoding="utf-8")
        print(f"{number}/{len(sources)} exit={done.returncode} {source.name}", flush=True)


def compare(old: Path, new: Path) -> int:
    failures = 0
    folders = sorted(p.name for p in old.iterdir() if p.is_dir())
    for name in folders:
        a, b = old / name / "candidate.json", new / name / "candidate.json"
        problems = []
        if (old / name / "exit.txt").read_text() != (new / name / "exit.txt").read_text():
            problems.append("exit code differs")
        if a.exists() != b.exists():
            problems.append(f"candidate.json exists old={a.exists()} new={b.exists()}")
        elif a.exists():
            left, right = view(a), view(b)
            for key in left:
                if left[key] != right[key]:
                    problems.append(f"{key} differs")
            for i, (x, y) in enumerate(zip(left["courses"], right["courses"])):
                if x != y:
                    problems.append(f"first course diff #{i}: {x['course_code']} -> {y['course_code']}")
                    break
        failures += bool(problems)
        print(f"{name} {'FAIL' if problems else 'ok'} {(old / name / 'source.txt').read_text()[-60:]}")
        for problem in problems:
            print(f"    {problem}")
    print(f"{len(folders) - failures}/{len(folders)} identical")
    return 1 if failures else 0


def stats(new: Path) -> None:
    kinds, reasons, tokens, anchored = Counter(), Counter(), [], Counter()
    produced = 0
    for path in sorted(new.glob("*/candidate.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        rag = data["rag"]
        chunks = rag["semantic_chunks"] + rag["hierarchical_chunks"]
        produced += bool(chunks)
        for chunk in chunks:
            kinds[chunk["chunk_type"]] += 1
            tokens.append((chunk["token_count"], chunk["chunk_type"]))
            anchored[chunk["source_anchored"]] += 1
            assert chunk["cell_ids"] or chunk["chunk_type"].startswith("hierarchical") or chunk["chunk_type"] == "program_overview"
        for r in rag["rejected_chunks"]:
            reasons[(r["chunk_type"], r["reason"])] += 1
    print("inputs with chunks:", produced)
    print("chunks by type:", dict(kinds))
    print("rejected:", dict(reasons))
    print("source_anchored:", dict(anchored))
    for kind in sorted(kinds):
        values = sorted(t for t, k in tokens if k == kind)
        print(f"{kind}: n={len(values)} min={values[0]} median={values[len(values)//2]} max={values[-1]}")


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "run":
        run(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]), Path(sys.argv[5]))
    elif mode == "compare":
        raise SystemExit(compare(Path(sys.argv[2]), Path(sys.argv[3])))
    elif mode == "stats":
        stats(Path(sys.argv[2]))
```

- [ ] **Step 2: Prove the comparer can fail**

Make a one-input smoke directory and compare it with itself and with a tampered copy:

```
$t = "$env:TEMP\phaseE"; New-Item -ItemType Directory -Force $t | Out-Null
$repo = (Get-Location).Path
$golden = 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\docling_jsonified_output\task2b_standing_isolated_2026-09-29'
$map = 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\PalSU Undergraduate Prospectus Website Dump\Tiniguiban - Main\palsu_main_undergrad_program_college_meaning.md'
```

Run the `run` mode once with the new tree on a single-input folder (copy one `*_docling.json` into `$t\one`), then `compare` that output with itself (expect `1/1 identical`), then edit one `course_title` in a copy of `candidate.json` and compare again (expect `FAIL` with `courses differs`). Record both results.

- [ ] **Step 3: Create the old-tree worktree**

```
git worktree add "$env:TEMP\phaseE\old" <phase-start-commit>
```

`<phase-start-commit>` is the `dev` commit recorded in Task 1 step 1 (the base of this branch). The worktree has no `.venv`; use the repo's own: all runs go through `uv run --project $repo\backend`, with `cwd` set to the tree being tested, so `python -m backend.bintanong_tools.prospectus_extractor` resolves from that tree's `backend/` folder.

- [ ] **Step 4: Launch both sweeps detached**

Each sweep takes roughly 90 minutes (44 Docling-JSON runs). Tool calls die at 10 minutes, so start them with `Start-Process` and poll the log files:

```
$cmd = { param($root,$out,$log) uv run --project "$repo\backend" --extra tools --extra dev python "$t\course_fields_check.py" run $root $out $golden $map *> $log }
Start-Process pwsh -WindowStyle Hidden -ArgumentList '-NoProfile','-Command',"cd '$t\old'; uv run --project '$repo\backend' --extra tools --extra dev python '$t\course_fields_check.py' run '$t\old' '$t\out_old' '$golden' '$map' *> '$t\old.log'"
Start-Process pwsh -WindowStyle Hidden -ArgumentList '-NoProfile','-Command',"cd '$repo'; uv run --project '$repo\backend' --extra tools --extra dev python '$t\course_fields_check.py' run '$repo' '$t\out_new' '$golden' '$map' *> '$t\new.log'"
```

(Drop the unused `$cmd` line; it is shown only to name the three arguments.) Poll with `Get-Content "$t\new.log" -Tail 3` until the last line reads `44/44 exit=...`.

- [ ] **Step 5: Compare**

Run: `uv run --project backend --extra tools python "$env:TEMP\phaseE\course_fields_check.py" compare "$env:TEMP\phaseE\out_old" "$env:TEMP\phaseE\out_new"`
Expected final line: `44/44 identical`. Any `FAIL` is a real change in a course field, audit status or elective option. Use superpowers:systematic-debugging; the likely culprit is the `parse_elective_tracks` edit in Task 4, which must produce the same `options` apart from `source_item_id`. Do not continue past a FAIL.

- [ ] **Step 6: Chunk statistics**

Run: `... course_fields_check.py stats "$env:TEMP\phaseE\out_new"`
Record in the progress file: inputs with chunks (expect well under 44, because error audits emit none), chunks by type, rejected counts by reason, token min/median/max per type, anchored counts (expect `False` for all, since every input is cached Docling JSON). Pass criteria: no `course` or `term_schedule` chunk above 480 estimated tokens; rejected `course` chunks with reason `prerequisite_not_in_source_text` or `no_valid_source_cells` should be 0 on the real inputs. If not 0, list the codes and stop for the controller; do not loosen `course_rejection`. Expected `hierarchical_layout` rejections for over-cap table chunks; record their count.

- [ ] **Step 7: Clean up the worktree and commit the progress note**

```
git worktree remove --force "$env:TEMP\phaseE\old"
git add plans/plan_current_progress/extractor_split_progress.md
git commit -m "docs: record Phase E regression and chunk statistics"
```

---

### Task 8: Gate, optional token calibration, Codex review

**Files:** `plans/plan_current_progress/extractor_split_progress.md`; scratch scripts in `$env:TEMP\phaseE`.

- [ ] **Step 1: Resolve every chunk back to cells (automatic part of the gate)**

Create `$env:TEMP\phaseE\chunk_gate.py`:

```python
"""For each chunk in one candidate run, confirm its cell IDs, text and pages exist in the evidence."""
import json
import sys
from pathlib import Path

from backend.bintanong_tools.prospectus_extractor.loader import load_document

run_dir = Path(sys.argv[1])
source = Path((run_dir / "source.txt").read_text(encoding="utf-8"))
payload = json.loads((run_dir / "candidate.json").read_text(encoding="utf-8"))
document, _ = load_document(source, device="cpu", force_reconvert=False)
cells = document.all_cells()
checked = 0
for chunk in payload["rag"]["semantic_chunks"]:
    for span in chunk["source_spans"]:
        if span["locator"]["kind"] != "table_cells":
            continue
        for cell_id in span["locator"]["cell_ids"]:
            cell = cells[cell_id]  # KeyError means the chunk points at a cell that does not exist
            assert (cell.bbox.page if cell.bbox else None) == span["page"], (chunk["chunk_id"], cell_id)
            assert cell.text in span["text"], (chunk["chunk_id"], cell_id)
        checked += 1
print("spans resolved:", checked, "chunks:", len(payload["rag"]["semantic_chunks"]))
for chunk in payload["rag"]["semantic_chunks"]:
    if chunk["chunk_type"] == "course" and ("Prerequisites**: None" not in chunk["text"]):
        print(chunk["chunk_id"][:12], chunk["course_code"], "p", chunk["pages"], chunk["cell_ids"], "|", chunk["source_text"])
```

Run it for each output folder from Task 7 whose `candidate.json` has chunks (find them with `Get-ChildItem $env:TEMP\phaseE\out_new -Recurse -Filter candidate.json | Where-Object { (Get-Content $_ -Raw | ConvertFrom-Json).rag.semantic_chunks.Count -gt 0 }`). Expected: `spans resolved: N` with no assertion error for every one.

- [ ] **Step 2: Human check against the PDF (manual part of the gate)**

The pilot PDFs are BSCS and Architecture. Their audits may be `error` after this phase (BSA was `error` on 3 October with 77 courses and no chunks by design), in which case their gate result is "no chunks emitted, blocked by audit, owned by the parser repairs"; record that and do not force it. For the non-error pilot (`ABPhilStud`, `warn`), take the printed list from step 1, pick every course that prints a prerequisite or standing condition (up to 10), open the original PDF at the printed page, and confirm the course row text equals `source_text` and the prerequisite text is in it. Record each checked chunk ID prefix, page and verdict in the progress file. Any mismatch fails the gate.

- [ ] **Step 3: Optional token calibration (Decision D1)**

Only if `$env:MODELS_DIR\SEA-LION-E5-Embedding-600M\tokenizer.json` exists on the executor's machine (it does not on the planning machine):

```
uv run --project backend --extra tools python -c "
import json,sys,os
from pathlib import Path
from tokenizers import Tokenizer
tok = Tokenizer.from_file(str(Path(os.environ['MODELS_DIR'])/'SEA-LION-E5-Embedding-600M'/'tokenizer.json'))
worst = 10.0
for p in Path(sys.argv[1]).glob('*/candidate.json'):
    for c in json.loads(p.read_text(encoding='utf-8'))['rag']['semantic_chunks']:
        exact = len(tok.encode(c['text']).ids)
        worst = min(worst, c['token_count'] / max(exact, 1))
print('smallest estimate/exact ratio:', round(worst, 2))
" "$env:TEMP\phaseE\out_new"
```

Pass: ratio at least 1.0 (the estimate never under-counts). If under 1.0, raise the multipliers in `estimate_tokens`, change `TOKEN_COUNT_METHOD` to `estimate-v2`, bump `CHUNKER_VERSION` to `palsu-chunker-v2` (split points change, so content and IDs change), update the tests that mention the old constants, and rerun Task 7 step 6. If the file does not exist, write "tokenizer not available; exact counting is Phase 3" in the progress file.

- [ ] **Step 4: Codex gate (read-only, detached, about 15 minutes)**

```
$prompt = 'Review branch feature/prospectus-phase-e-rag-provenance against dev in this repo. Claim: every chunk from backend/bintanong_tools/prospectus_extractor/rag.py carries pdf_sha256, pages, table indexes and cell IDs from the extractor evidence; chunk_id is stable for one PDF and different for another edition; no chunk is built from a course without valid source cells; summaries list all contributing pages and never a single fabricated page; the 512-token cap including a 32-token reserve is enforced; no embedding call or vector write was added; no course field changed. Try to break each claim: find a path where provenance page is None but a page is invented, where the ID depends on a timestamp or dict ordering, where a rejected course still appears in a summary, where text can exceed the cap, or where Windows line endings change an ID or hash. Do not modify files. Report findings with file and line.'
Start-Process pwsh -WindowStyle Hidden -ArgumentList '-NoProfile','-Command',"codex exec --sandbox read-only -o '$env:TEMP\phaseE\codex_e.txt' '$prompt'"
```

Poll `Get-Item "$env:TEMP\phaseE\codex_e.txt"` until it exists. Record the findings in the progress file. Fix each confirmed finding with a failing test first; note and skip unconfirmed ones. If Codex is rate-limited or errors, record that and continue.

- [ ] **Step 5: Final run and hand-off note**

Run the full suite and the self-test. Expected: all green, 80/80. Append to the progress file: test counts, the `44/44 identical` line, the stats, the gate verdicts, Codex findings, the new `SCHEMA_VERSION`, and "next: Phase F". Do not merge into `dev` and do not push; ask the user (superpowers:finishing-a-development-branch).

```
git add plans/plan_current_progress/extractor_split_progress.md
git commit -m "docs: record Phase E gate results"
```

**Phase E gate:** `tests/test_prospectus_chunks.py` green; `44/44 identical` course fields; every chunk of every non-error input resolves to existing cells with matching text and page; every checked prerequisite or standing chunk of the non-error pilot matches the PDF by eye; no `course` or `term_schedule` chunk exceeds the cap; Codex findings resolved or recorded. No embedding call and no vector write exist in the diff (check with `git diff dev --stat` and `Select-String -Path backend\bintanong_tools\prospectus_extractor\*.py -Pattern "embed|encode|vector"`, expecting nothing new).

---

## Self-review

**Spec coverage.**
- `pdf_sha256` on every chunk: `assemble_chunk` sets it; dependency and D3 explain the missing-hash case (Tasks 2, 6).
- Page, table index, cell IDs, source text separate from summary: `pages`, `table_indexes`, `cell_ids`, `source_text` vs `text` (Tasks 2, 3).
- Term and elective summaries list all spans, no fabricated page: Task 4 tests; course and summary pages come from per-cell pages, never from `provenance["page"]` (Task 3).
- Chunk ID from hash, source locator, content hash and chunker version, replacing `<code>::course`: `make_chunk_id`; `id` removed (Tasks 2, 3).
- Token cap 512 with 300 to 400 target; counter decision: D1, D5, Tasks 2 and 8.
- `content_review: pending`: every chunk (Task 2).
- Tests first: two editions, same PDF with different timestamps, multi-page summary, prerequisite without source cells, token cap: Tasks 3, 4, 6.
- No embedding or vector write: stated and checked in the gate.
- Required plan items: start check (Task 1), conditional AST-gate deletion (Task 1), schema bump with description (Task 6), regression on 44 inputs with a detached run and a recovered, adapted comparer (Task 7), progress-file updates (every task), Codex gate (Task 8), Decisions section, OCR room (`source_kind`, `ocr_confidence`), commit rules.

**Placeholder scan.** No TBD or "handle edge cases". Two places depend on facts that only exist at execution time and say how to resolve them: the next `SCHEMA_VERSION` value and whether Phase C or D already provide the hash (Task 1 step 3 records both; Task 6 branches on it).

**Type consistency.** `make_span`, `spans_from_cells`, `spans_from_text_items`, `locator_key`, `make_chunk_id`, `course_rejection`, `pack_items`, `assemble_chunk`, `fits_cap`, `estimate_tokens`, `CHUNKER_VERSION`, `TOKEN_*` are defined in Task 2 and used under the same names in Tasks 3 to 6. Rejection records have the shape `{"chunk_type", "label", "reason"}` plus `token_count` for over-cap, in code and tests. `build_semantic_rag_chunks(..., *, pdf_sha256, source_kind, text_items, rejected)` and `build_hierarchical_rag_chunks(document, source_name, *, pdf_sha256, rejected)` match the pipeline calls. The `rag.py` code uses `"aggregate"` as the resolution method for summary spans; no test depends on it.

**Known limits, stated rather than hidden.**
- The prerequisite check is word containment (every alphanumeric token of `prerequisites_raw` appears in the cells), not order. It stops a prerequisite with no matching source; it does not prove the words came from the prerequisite column.
- Course `source_cells` include the year and semester banner cell, so `source_text` and the span carry that banner text.
- Overview chunks carry `unsourced_fields` because program, college and school year come from the file name, semantic map and document text, not from table cells.
- Elective options split across parts share their slot-course spans.
- Without a PDF (cached Docling JSON) chunks are unanchored and must not be loaded as institutional chunks.
- The review-corrected projection (draft Task 6, last bullet) cannot be used yet because the review GUI does not exist; chunks are built from extractor output and labelled `content_review: pending`.
