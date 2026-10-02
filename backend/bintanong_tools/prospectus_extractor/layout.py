"""Column-group and header detection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence
import re

from .text import clean_str
from .prerequisites import is_code_like_token, is_unit_like_token
from .grid import is_probable_course_code


@dataclass
class ColumnGroup:
    """One semester block of columns inside a two-up prospectus table."""

    index: int
    code_idx: int
    title_idx: int
    unit_idx: int
    prereq_idx: int

    def span(self) -> range:
        indices = [self.code_idx, self.title_idx, self.unit_idx, self.prereq_idx]
        return range(min(indices), max(indices) + 1)

    def as_dict(self) -> dict[str, int]:
        return {
            "index": self.index,
            "code_idx": self.code_idx,
            "title_idx": self.title_idx,
            "unit_idx": self.unit_idx,
            "prereq_idx": self.prereq_idx,
        }


def infer_column_groups_from_content(grid: list[list[str]]) -> list[ColumnGroup]:
    if not grid or len(grid) < 2:
        return []
    num_cols = max(len(r) for r in grid)
    code_scores = [0] * num_cols
    unit_scores = [0] * num_cols
    for row in grid:
        for c, cell in enumerate(row):
            if is_code_like_token(cell):
                code_scores[c] += 1
            if is_unit_like_token(cell):
                unit_scores[c] += 1

    unit_cols = [c for c in range(num_cols) if unit_scores[c] > 0]
    two_up_unit_pairs = []
    for i in range(len(unit_cols)):
        for j in range(i + 1, len(unit_cols)):
            u1, u2 = unit_cols[i], unit_cols[j]
            if u2 - u1 >= 3:
                two_up_unit_pairs.append((u1, u2))

    if two_up_unit_pairs:
        best_u_pair = max(two_up_unit_pairs, key=lambda p: unit_scores[p[0]] + unit_scores[p[1]])
        u1, u2 = best_u_pair
        c1_candidates = [c for c in range(u1) if code_scores[c] > 0]
        c1 = max(c1_candidates, key=lambda c: code_scores[c]) if c1_candidates else 0
        c2_candidates = [c for c in range(u1 + 1, u2) if code_scores[c] > 0]
        if c2_candidates:
            c2 = max(c2_candidates, key=lambda c: (code_scores[c], -abs((u2 - c) - (u1 - c1))))
        else:
            c2 = u1 + (u2 - u1) // 2
        prereq1 = u1 + 1 if c2 > u1 + 1 else u1
        prereq2 = u2 + 1 if num_cols > u2 + 1 else u2
        g1 = ColumnGroup(0, c1, c1 + 1, u1, prereq1)
        g2 = ColumnGroup(1, c2, c2 + 1 if u2 > c2 + 1 else c2, u2, prereq2)
        return [g1, g2]

    code_cols = [
        c
        for c in range(num_cols)
        if code_scores[c] >= 2 or (code_scores[c] >= 1 and len(grid) <= 8)
    ]
    if not code_cols:
        return []

    two_up_pairs = []
    for i in range(len(code_cols)):
        for j in range(i + 1, len(code_cols)):
            c1, c2 = code_cols[i], code_cols[j]
            if c2 - c1 >= 3:
                two_up_pairs.append((c1, c2))

    if two_up_pairs:
        best_pair = max(two_up_pairs, key=lambda p: code_scores[p[0]] + code_scores[p[1]])
        c1, c2 = best_pair
        u1_candidates = [c for c in range(c1 + 1, c2) if unit_scores[c] > 0]
        u1 = max(u1_candidates, key=lambda c: unit_scores[c]) if u1_candidates else c1 + 2
        u2_candidates = [c for c in range(c2 + 1, num_cols) if unit_scores[c] > 0]
        u2 = max(u2_candidates, key=lambda c: unit_scores[c]) if u2_candidates else min(c2 + 2, num_cols - 1)

        g1 = ColumnGroup(
            index=0,
            code_idx=c1,
            title_idx=c1 + 1 if u1 > c1 + 1 else c1 + 1,
            unit_idx=u1,
            prereq_idx=u1 + 1 if u1 + 1 < c2 else u1,
        )
        g2 = ColumnGroup(
            index=1,
            code_idx=c2,
            title_idx=c2 + 1 if u2 > c2 + 1 else c2 + 1,
            unit_idx=u2,
            prereq_idx=u2 + 1 if u2 + 1 < num_cols else u2,
        )
        return [g1, g2]
    else:
        c1 = code_cols[0]
        u1_candidates = [c for c in range(c1 + 1, num_cols) if unit_scores[c] > 0]
        u1 = max(u1_candidates, key=lambda c: unit_scores[c]) if u1_candidates else min(c1 + 2, num_cols - 1)

        right_units = [c for c in range(u1 + 1, num_cols) if unit_scores[c] > 0]
        if num_cols >= 6 and right_units:
            u2 = max(right_units, key=lambda c: unit_scores[c])
            prereq1_idx = u1 + 1 if (u2 - u1) >= 3 else u1
            c2 = u2 - 1 if u2 > u1 + 1 else u1 + 1
            return [
                ColumnGroup(
                    index=0,
                    code_idx=c1,
                    title_idx=c1 + 1,
                    unit_idx=u1,
                    prereq_idx=prereq1_idx,
                ),
                ColumnGroup(
                    index=1,
                    code_idx=c2,
                    title_idx=c2,
                    unit_idx=u2,
                    prereq_idx=u2,
                ),
            ]

        return [
            ColumnGroup(
                index=0,
                code_idx=c1,
                title_idx=c1 + 1,
                unit_idx=u1,
                prereq_idx=min(u1 + 1, num_cols - 1),
            )
        ]


def classify_header_cell(text: str) -> str:
    """Map a header cell to code/title/units/prereq/grade/other."""
    squashed = re.sub(r"[^a-z]", "", clean_str(text).lower())
    if not squashed:
        return "other"
    if "code" in squashed or squashed in ("course", "courses", "subcode", "subjectcode"):
        return "code"
    if "grade" in squashed:
        return "grade"
    if "title" in squashed or "descriptive" in squashed or "subject" in squashed:
        return "title"
    if "unit" in squashed or "credit" in squashed:
        return "units"
    if "prereq" in squashed or "prerequisite" in squashed or squashed.startswith("prereq"):
        return "prereq"
    if squashed.startswith("pre") and "req" in squashed:
        return "prereq"
    return "other"


def find_header_row(grid: Sequence[Sequence[str]], search_depth: int = 6) -> int:
    """Index of the column-header row, or -1 when the table has none."""
    if len(grid) >= 2:
        combo = [f"{grid[0][c]} {grid[1][c]}".strip() for c in range(min(len(grid[0]), len(grid[1])))]
        kinds = [classify_header_cell(cell) for cell in combo]
        if "code" in kinds and "title" in kinds and kinds.count("code") >= 2:
            return 0

    for row_index in range(min(search_depth, len(grid))):
        kinds = [classify_header_cell(cell) for cell in grid[row_index]]
        if "code" in kinds and "title" in kinds:
            return row_index
    for row_index in range(min(search_depth, len(grid))):
        kinds = [classify_header_cell(cell) for cell in grid[row_index]]
        if kinds.count("title") >= 1 and kinds.count("units") >= 1:
            return row_index
    return -1


def fallback_groups(num_cols: int) -> list[ColumnGroup]:
    """Positional layouts for tables whose header row did not survive extraction."""
    if num_cols >= 10:
        return [ColumnGroup(0, 1, 2, 3, 4), ColumnGroup(1, 6, 7, 8, 9)]
    if num_cols >= 8:
        return [ColumnGroup(0, 0, 1, 2, 3), ColumnGroup(1, 4, 5, 6, 7)]
    if num_cols == 5:
        return [ColumnGroup(0, 1, 2, 3, 4)]
    if num_cols == 4:
        return [ColumnGroup(0, 0, 1, 2, 3)]
    return []


def detect_column_groups(grid: Sequence[Sequence[str]]) -> tuple[list[ColumnGroup], int]:
    """Derive semester column groups from the header row."""
    if not grid:
        return [], -1

    header_index = find_header_row(grid)
    width = max((len(row) for row in grid), default=0)
    if header_index < 0:
        inferred = infer_column_groups_from_content([[clean_str(c) for c in r] for r in grid])
        if inferred:
            return inferred, -1
        return fallback_groups(width), -1

    header = list(grid[header_index])
    h_kinds = [classify_header_cell(c) for c in header]
    if (h_kinds.count("code") < 2 or "title" not in h_kinds) and header_index + 1 < len(grid):
        next_row = list(grid[header_index + 1])
        next_text = " ".join(next_row).upper()
        if not any(w in next_text for w in ["YEAR", "SEMESTER"]):
            max_c = min(len(header), len(next_row))
            merged = [f"{header[c]} {next_row[c]}".strip() for c in range(max_c)]
            m_kinds = [classify_header_cell(c) for c in merged]
            if m_kinds.count("code") >= h_kinds.count("code") and "title" in m_kinds:
                header = merged

    groups: list[ColumnGroup] = []
    current: dict[str, int] = {}

    def flush() -> None:
        if "code" not in current:
            return
        code_idx = current["code"]
        groups.append(
            ColumnGroup(
                index=len(groups),
                code_idx=code_idx,
                title_idx=current.get("title", code_idx + 1),
                unit_idx=current.get("units", code_idx + 2),
                prereq_idx=current.get("prereq", code_idx + 3),
            )
        )

    for col_index, cell in enumerate(header):
        kind = classify_header_cell(cell)
        if kind == "code":
            flush()
            current = {"code": col_index}
        elif kind in {"title", "units", "prereq"} and current:
            current.setdefault(kind, col_index)
    flush()

    width = max((len(row) for row in grid), default=len(header))
    valid = [g for g in groups if g.prereq_idx < width and g.code_idx < width]
    if not valid:
        inferred = infer_column_groups_from_content([[clean_str(c) for c in r] for r in grid])
        if inferred:
            return inferred, header_index
        return fallback_groups(width), header_index
    data_rows = grid[header_index + 1:]
    def code_count(group: ColumnGroup) -> int:
        return sum(
            group.code_idx < len(row) and is_probable_course_code(row[group.code_idx])
            for row in data_rows
        )
    if all(code_count(group) == 0 for group in valid):
        inferred = infer_column_groups_from_content([[clean_str(c) for c in r] for r in grid])
        if inferred and all(code_count(group) >= 2 for group in inferred):
            return inferred, header_index
    return valid, header_index


def is_header_row(cells: Sequence[str]) -> bool:
    """True for the column-header row and for its repeats after a page break."""
    kinds = [classify_header_cell(cell) for cell in cells]
    return kinds.count("code") >= 1 and kinds.count("title") >= 1
