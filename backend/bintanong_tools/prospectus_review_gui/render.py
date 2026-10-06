"""What the review GUI's three panes show: the PDF page image, the markup twin and the course JSON.

Everything is built in memory; nothing is written to disk.
"""

from __future__ import annotations

import copy
import io
import json
import math
import threading
from collections import OrderedDict
from dataclasses import asdict
from pathlib import Path
from typing import Any, Mapping, Sequence

from ..prospectus_extractor.evidence import ProspectusEvidence
from ..prospectus_extractor.loader import load_from_raw_json
from ..prospectus_extractor.markup import render_prospectus_markup

DEFAULT_SCALE, MAX_SCALE = 1.5, 3
CACHE_SIZE = 8
MAX_JSON_CELLS = 100   # source cells returned per course; a real course has about ten
ROLES = ("code", "title", "unit", "prereq")
# pdfium is not thread-safe and FastAPI runs the sync handlers in a thread pool: one lock for every pdfium call.
_PDFIUM = threading.RLock()   # ponytail: one lock for all documents; per-document locks if rendering ever needs to overlap


def load_evidence(docling_json: Path) -> tuple[ProspectusEvidence | None, str | None]:
    """(evidence, None), or (None, reason) when the Docling JSON is missing or cannot be read. Never raises: the twin
    is then replaced by the cell fallback. The reason names the file, not its folder."""
    name = Path(docling_json).name
    try:
        data = json.loads(Path(docling_json).read_bytes())
    except FileNotFoundError:
        return None, f"the Docling JSON {name} was not found"
    except (OSError, ValueError) as exc:   # ValueError covers JSON and UTF-8 decoding errors
        return None, f"the Docling JSON {name} cannot be read ({type(exc).__name__})"
    if not isinstance(data, dict):
        return None, f"the Docling JSON {name} cannot be read (not a JSON object)"
    try:
        return load_from_raw_json(data), None
    except Exception as exc:  # a Docling validation error, or any shape the adapter does not expect
        return None, f"the Docling JSON {name} cannot be read ({type(exc).__name__})"


def twin_fragment(evidence: ProspectusEvidence, payload: Mapping[str, Any], pdf_sha256: str | None) -> str:
    """The markup twin without its `> ` notice line (the GUI header states the audit status itself). Nothing else is
    changed; the renderer escapes every source text, so no other line can start with `> `."""
    markup = render_prospectus_markup(evidence, payload, pdf_sha256=pdf_sha256)
    return "\n".join(line for line in markup.split("\n") if not line.startswith("> "))


def _own_ids(role_cells: Mapping[str, Sequence[Mapping[str, Any]]]) -> dict[Any, str]:
    return {cell.get("cell_id"): role for role in ROLES for cell in (role_cells or {}).get(role) or []}


def cells_fallback(course: Mapping[str, Any], role_cells: Mapping[str, Sequence[Mapping[str, Any]]]) -> list[dict[str, Any]]:
    """The course's own cells (`role_cells` is verify.own_role_cells) as {cell_id, role, row, col, text}, in grid order:
    what the twin pane shows when there is no Docling evidence. Banner cells are not the course's own and are left out."""
    own = _own_ids(role_cells)
    rows = [{"cell_id": c.get("cell_id"), "role": own[c.get("cell_id")], "row": c.get("row_start"), "col": c.get("col_start"),
             "text": c.get("text")} for c in (course.get("provenance") or {}).get("source_cells") or [] if c.get("cell_id") in own]
    return sorted(rows, key=lambda r: (r["row"] if isinstance(r["row"], int) else -1, r["col"] if isinstance(r["col"], int) else -1))


def course_json(course: Mapping[str, Any], row: Any, role_cells: Mapping[str, Sequence[Mapping[str, Any]]] | None = None) -> dict[str, Any]:
    """{"course": a copy of the course as the extractor wrote it, "flags": the verifier's flags (beside it, never inside),
    "truncated": how many source cells were left out}. Past MAX_JSON_CELLS source cells only the first ones and the
    course's own role cells are kept, so one request cannot return megabytes."""
    out = copy.deepcopy(dict(course))
    cells = (out.get("provenance") or {}).get("source_cells")
    truncated = 0
    if isinstance(cells, list) and len(cells) > MAX_JSON_CELLS:
        own = _own_ids(role_cells or {})
        kept = [c for i, c in enumerate(cells) if i < MAX_JSON_CELLS or (isinstance(c, Mapping) and c.get("cell_id") in own)]
        truncated = len(cells) - len(kept)
        out["provenance"]["source_cells"] = kept
    return {"course": out, "flags": [asdict(f) for f in getattr(row, "flags", None) or []], "truncated": truncated}


class PageError(ValueError):
    """A page cannot be shown. `code` is missing_pdf, bad_pdf, bad_page or bad_scale; messages carry file names only."""

    def __init__(self, message: str, code: str):
        super().__init__(message)
        self.code = code


class PageRenderer:
    """pypdfium2 behind a small interface: page_count, size(n) and rotation(n) in points and degrees, png(n, scale)."""

    def __init__(self, pdf_path: Path):
        import pypdfium2 as pdfium

        self.name = Path(pdf_path).name
        if not Path(pdf_path).is_file():
            raise PageError(f"the PDF {self.name} was not found", "missing_pdf")
        try:
            with _PDFIUM:
                self._pdf = pdfium.PdfDocument(str(pdf_path))
                self.page_count = len(self._pdf)
        except Exception as exc:  # pypdfium2 raises PdfiumError for a damaged file
            raise PageError(f"the PDF {self.name} cannot be opened", "bad_pdf") from exc
        self.render_count = 0
        self._cache: OrderedDict[tuple[int, float], bytes] = OrderedDict()

    def __enter__(self) -> "PageRenderer":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def close(self) -> None:
        with _PDFIUM:
            self._pdf.close()

    def _page(self, number):
        if type(number) is not int or not 1 <= number <= self.page_count:
            raise PageError(f"page {number!r} is not in {self.name} (1 to {self.page_count})", "bad_page")
        return self._pdf[number - 1]

    def size(self, number: int) -> tuple[float, float]:
        with _PDFIUM:
            page = self._page(number)
            try:
                return tuple(page.get_size())
            finally:
                page.close()

    def rotation(self, number: int) -> int:
        with _PDFIUM:
            page = self._page(number)
            try:
                return int(page.get_rotation())
            finally:
                page.close()

    def png(self, number: int, scale: float = DEFAULT_SCALE) -> bytes:
        if isinstance(scale, bool) or not isinstance(scale, (int, float)) or not math.isfinite(scale) or not 0 < scale <= MAX_SCALE:
            raise PageError(f"scale must be above 0 and at most {MAX_SCALE}", "bad_scale")
        key = (number, float(scale))
        with _PDFIUM:   # the cache is shared by the worker threads too
            if key in self._cache:
                self._cache.move_to_end(key)
                return self._cache[key]
            page = self._page(number)
            try:
                buffer = io.BytesIO()
                page.render(scale=float(scale)).to_pil().save(buffer, format="PNG")
            finally:
                page.close()
            self.render_count += 1
            self._cache[key] = buffer.getvalue()
            while len(self._cache) > CACHE_SIZE:
                self._cache.popitem(last=False)
            return self._cache[key]
