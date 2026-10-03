"""Markup twin: Docling evidence laid out the way the printed prospectus reads."""

from __future__ import annotations

from html import escape
from typing import Any
from typing import Mapping

from .evidence import NormalizedCell, NormalizedTable, ProspectusEvidence, project_table_to_grid
from .layout import is_header_row
from .text import match_semester_labels, match_year_label

MARKUP_VERSION = "palsu-prospectus-markup-v1"

LINE_TOLERANCE = 3.0  # points: text whose tops differ by less than this shares a printed line
_HEADING_TAG = {"title": "h1", "section_header": "h2"}
_SMALL_LABELS = {"footnote", "page_footer", "page_header"}


def _esc(value: Any) -> str:
    return escape(str(value), quote=True)


def _esc_block(value: Any) -> str:
    """Escape, then turn line breaks into <br>: a blank line would end a Markdown HTML block."""
    return _esc(value).replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br>")


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
    return f'<{tag} data-cell="{_esc(cell.cell_id)}"{_page_attr(page)}{spans}>{_esc_block(cell.text)}</{tag}>'


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
        lines.append(f'<p data-unplaced-cell="{_esc(cell.cell_id)}"{_page_attr(page)}>{_esc_block(cell.text)}</p>')
    return "\n".join(lines)


def _y_down(top: float, bottom: float, origin: str | None, page_height: float | None) -> float:
    """Distance down the page in one top-down frame. Docling text boxes are BOTTOMLEFT
    (y up) and table cells TOPLEFT (y down), so BOTTOMLEFT tops become height - top.
    Fallback when origin or page height is unknown: the item's own frame is guessed from
    top >= bottom (BOTTOMLEFT, y = -top) vs top < bottom (TOPLEFT, y = top), as before."""
    if origin == "TOPLEFT":
        return top
    if origin == "BOTTOMLEFT" and page_height is not None:
        return page_height - top
    return -top if top >= bottom else top


def _page_height(evidence: ProspectusEvidence, page: int) -> float | None:
    size = evidence.page_sizes.get(page)
    return size[1] if size else None


def _text_position(item: Mapping[str, Any], evidence: ProspectusEvidence) -> tuple[int, float, float] | None:
    bbox = item.get("bbox")
    if item.get("page") is None or not bbox:
        return None
    left, top, _right, bottom = bbox
    page = int(item["page"])
    return (page, _y_down(top, bottom, item.get("origin"), _page_height(evidence, page)), float(left))


def _table_position(table: NormalizedTable, evidence: ProspectusEvidence) -> tuple[int, float, float] | None:
    spots = [
        (
            int(c.bbox.page),
            _y_down(c.bbox.top, c.bbox.bottom, c.bbox.origin, _page_height(evidence, int(c.bbox.page))),
            float(c.bbox.left),
        )
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
        position = _text_position(item, evidence)
        if position is None:
            loose_texts.append(("text", item))
        else:
            placed.append((position, "text", item))
    for table in evidence.tables:
        position = _table_position(table, evidence)
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
    body = _esc_block(item.get("text", ""))
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
