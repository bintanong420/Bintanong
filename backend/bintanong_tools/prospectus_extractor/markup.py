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
