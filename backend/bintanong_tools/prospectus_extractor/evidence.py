"""Normalized Docling evidence: cells, tables, source boxes."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Sequence

from .text import clean_str


@dataclass(frozen=True)
class SourceBBox:
    """A source-space box. Coordinates retain Docling's native orientation."""

    page: int | None
    left: float | None
    top: float | None
    right: float | None
    bottom: float | None

    def is_complete(self) -> bool:
        return None not in (self.left, self.top, self.right, self.bottom)

    def as_list(self) -> list[float] | None:
        if not self.is_complete():
            return None
        return [float(self.left), float(self.top), float(self.right), float(self.bottom)]

    def as_dict(self) -> dict[str, Any]:
        return {
            "page": self.page,
            "bbox": self.as_list(),
        }


@dataclass(frozen=True)
class NormalizedCell:
    """One Docling table cell, including its original span and source box."""

    cell_id: str
    table_index: int
    raw_text: str
    text: str
    row_start: int
    row_end: int
    col_start: int
    col_end: int
    bbox: SourceBBox | None = None

    @property
    def row_span(self) -> int:
        return max(0, self.row_end - self.row_start)

    @property
    def col_span(self) -> int:
        return max(0, self.col_end - self.col_start)

    def overlaps(self, row: int, col: int | None = None) -> bool:
        if not (self.row_start <= row < self.row_end):
            return False
        return col is None or self.col_start <= col < self.col_end

    def as_evidence_dict(self) -> dict[str, Any]:
        return {
            "cell_id": self.cell_id,
            "table_index": self.table_index,
            "text": self.text,
            "raw_text": self.raw_text,
            "row_start": self.row_start,
            "row_end": self.row_end,
            "col_start": self.col_start,
            "col_end": self.col_end,
            "page": self.bbox.page if self.bbox else None,
            "bbox": self.bbox.as_list() if self.bbox else None,
        }


@dataclass
class NormalizedTable:
    table_index: int
    num_rows: int
    num_cols: int
    cells: list[NormalizedCell] = field(default_factory=list)

    def cell_map(self) -> dict[str, NormalizedCell]:
        return {cell.cell_id: cell for cell in self.cells}

    def cells_on_row(self, row: int) -> list[NormalizedCell]:
        return sorted(
            (cell for cell in self.cells if cell.row_start <= row < cell.row_end),
            key=lambda cell: (cell.col_start, cell.col_end, cell.cell_id),
        )


@dataclass
class ProspectusEvidence:
    """Canonical evidence passed from Docling to curriculum interpretation.

    ``tables`` is authoritative. ``grids`` below is a derived compatibility
    projection and must never be used to reconstruct provenance.
    """

    tables: list[NormalizedTable] = field(default_factory=list)
    text_items: list[dict[str, Any]] = field(default_factory=list)
    markdown: str = ""
    docling_document: Any = None
    source_kind: str = ""
    table_year_hints: dict[int, str] = field(default_factory=dict)
    table_year_hint_sources: dict[int, str] = field(default_factory=dict)

    @property
    def docling_doc(self) -> Any:  # compatibility for the layout chunker
        return self.docling_document

    @property
    def grids(self) -> list[list[list[str]]]:  # compatibility/debug view only
        return [project_table_to_grid(table) for table in self.tables]

    def all_cells(self) -> dict[str, NormalizedCell]:
        return {cell.cell_id: cell for table in self.tables for cell in table.cells}


# Kept as an import-compatible name. The canonical model is ProspectusEvidence.
LoadedDocument = ProspectusEvidence


def project_table_to_grid(table: NormalizedTable, repeat_spans: bool = True) -> list[list[str]]:
    """Derive a grid for layout detection and diagnostics without mutating the IR."""
    grid = [["" for _ in range(table.num_cols)] for _ in range(table.num_rows)]
    for cell in sorted(table.cells, key=lambda c: (c.row_start, c.col_start, c.cell_id)):
        rows = range(cell.row_start, min(cell.row_end, table.num_rows))
        cols = range(cell.col_start, min(cell.col_end, table.num_cols))
        for row in rows:
            for col in cols:
                if not repeat_spans and (row != cell.row_start or col != cell.col_start):
                    continue
                if not grid[row][col]:
                    grid[row][col] = cell.text
    return grid


def normalized_table_from_grid(
    grid: Sequence[Sequence[Any]], table_index: int = 0
) -> NormalizedTable:
    """Fixture/compatibility adapter that collapses contiguous duplicate spans.

    Production loading never uses this helper; production tables come from
    Docling ``table_cells`` through ``docling_to_normalized_table``.
    """
    rows = [[clean_str(value) for value in row] for row in grid]
    num_rows = len(rows)
    num_cols = max((len(row) for row in rows), default=0)
    cells: list[NormalizedCell] = []
    cell_number = 0
    for row_index, row in enumerate(rows):
        col = 0
        while col < num_cols:
            value = row[col] if col < len(row) else ""
            if not value:
                col += 1
                continue
            end = col + 1
            while end < num_cols and end < len(row) and row[end] == value:
                end += 1
            cells.append(
                NormalizedCell(
                    cell_id=f"t{table_index}-c{cell_number}",
                    table_index=table_index,
                    raw_text=value,
                    text=value,
                    row_start=row_index,
                    row_end=row_index + 1,
                    col_start=col,
                    col_end=end,
                    bbox=None,
                )
            )
            cell_number += 1
            col = end
    return NormalizedTable(table_index, num_rows, num_cols, cells)
