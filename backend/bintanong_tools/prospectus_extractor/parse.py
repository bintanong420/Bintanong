"""Evidence-to-curriculum entry points."""

from __future__ import annotations

from typing import Any
from typing import Mapping
from typing import Sequence

from .text import norm_key
from .footnotes import FootnoteContext
from .grid import GridParseResult, _two_course_codes_in_cell, extract_grand_total, is_probable_course_code
from .layout import ColumnGroup, detect_column_groups
from .evidence import ProspectusEvidence, normalized_table_from_grid, project_table_to_grid
from .sections import CourseCandidate, SemanticRepairProvider, StructuralToken, _assemble_section_candidates, _candidate_to_raw_course, _cells_in_group_row, build_curriculum_sections, detect_source_course_candidates, tokenize_table
from .repair import apply_semantic_repairs


def parse_curriculum_evidence(
    evidence: ProspectusEvidence,
    repair_provider: SemanticRepairProvider | None = None,
) -> GridParseResult:
    """Parse canonical Docling evidence without year or semester defaults."""
    result = GridParseResult()
    layouts: dict[int, list[ColumnGroup]] = {}
    candidates: list[CourseCandidate] = []
    all_tokens: list[StructuralToken] = []

    for table in evidence.tables:
        grid = project_table_to_grid(table)
        groups, header_index = detect_column_groups(grid)
        layouts[table.table_index] = groups
        result.layout.append(
            {
                "table_index": table.table_index,
                "rows": table.num_rows,
                "columns": table.num_cols,
                "header_row": header_index,
                "column_groups": [group.as_dict() for group in groups],
                "canonical_cell_count": len(table.cells),
            }
        )
        if not groups:
            result.warnings.append(
                f"Table {table.table_index}: no usable column layout; table skipped."
            )
            continue
        if not any(
            is_probable_course_code(cell.text)
            and any(cell.col_start <= group.code_idx < cell.col_end for group in groups)
            for cell in table.cells
        ):
            continue
        if header_index < 0:
            result.warnings.append(
                f"Table {table.table_index}: no header row found; layout inferred from cell geometry/content."
            )
        tokens = tokenize_table(table, groups)
        all_tokens.extend(tokens)
        for cell in table.cells:
            group = next((group for group in groups
                          if cell.col_start == group.code_idx
                          and cell.col_end == group.code_idx + 1), None)
            if group is None:
                continue
            codes = _two_course_codes_in_cell(cell.text)
            if codes:
                row_cells = {
                    source.cell_id: source
                    for source_row in range(cell.row_start, cell.row_end)
                    for source in _cells_in_group_row(table, source_row, group)
                }
                result.anomalies.append({
                    "id": f"{cell.cell_id}-multiple-codes",
                    "type": "multiple_course_codes_in_cell",
                    "table_index": table.table_index,
                    "row": cell.row_start,
                    "page": cell.bbox.page if cell.bbox else None,
                    "reason": (f"one source cell contains course codes {codes[0]} and {codes[1]}; "
                               "separate field ownership is unresolved; row withheld"),
                    "candidate_codes": list(codes),
                    "source_cell_ids": list(row_cells),
                    "source_cells": [source.as_evidence_dict() for source in row_cells.values()],
                })
        sections, anomalies = build_curriculum_sections(evidence, table, groups, tokens)
        result.anomalies.extend(anomalies)
        result.sections.extend(section.as_dict() for section in sections)
        for section in sections:
            candidates.extend(
                _assemble_section_candidates(evidence, table, groups, section, result)
            )
        for cell in table.cells:
            grand = extract_grand_total(cell.text)
            if grand is not None:
                result.declared_grand_total = grand
        for row in range(table.num_rows):
            grand = extract_grand_total(" ".join(cell.text for cell in table.cells_on_row(row)))
            if grand is not None:
                result.declared_grand_total = grand

    result.structural_tokens = [token.as_dict() for token in all_tokens]
    result.source_course_candidates = detect_source_course_candidates(evidence, layouts)

    titles = [candidate.title.value for candidate in candidates if candidate.title]
    units = [candidate.units.value for candidate in candidates if candidate.units]
    result.footnotes = FootnoteContext.build(titles, units)
    result.courses = [
        _candidate_to_raw_course(candidate, evidence, result.footnotes)
        for candidate in candidates
        if candidate.code and candidate.code.value
    ]

    parsed_keys = {norm_key(course["course_code"]) for course in result.courses}
    result.unclaimed_course_candidates = [
        candidate
        for candidate in result.source_course_candidates
        if candidate["normalized_code"] not in parsed_keys
    ]
    for index, candidate in enumerate(result.unclaimed_course_candidates):
        result.anomalies.append(
            {
                "id": f"unclaimed-{candidate['table_index']}-{index}-{candidate['normalized_code']}",
                "type": "unclaimed_course_candidate",
                "table_index": candidate["table_index"],
                "row": next(
                    (
                        cell.row_start
                        for table in evidence.tables
                        for cell in table.cells
                        if cell.cell_id in candidate["cell_ids"]
                    ),
                    0,
                ),
                "reason": f"high-confidence course code {candidate['code']} was not claimed",
                "source_cell_ids": candidate["cell_ids"],
            }
        )

    apply_semantic_repairs(result, evidence, repair_provider)
    return result


def evidence_from_grids(
    grids: Sequence[Sequence[Sequence[Any]]],
    table_year_hints: Mapping[int, str] | None = None,
) -> ProspectusEvidence:
    """Compatibility adapter for callers that still provide grid fixtures."""
    return ProspectusEvidence(
        tables=[normalized_table_from_grid(grid, index) for index, grid in enumerate(grids)],
        source_kind="grid-compatibility",
        table_year_hints=dict(table_year_hints or {}),
    )


def parse_curriculum_grids(
    grids: Sequence[Sequence[Sequence[str]]],
    table_year_hints: dict[int, str] | None = None,
) -> GridParseResult:
    """Temporary API-compatible wrapper over the canonical evidence parser."""
    return parse_curriculum_evidence(evidence_from_grids(grids, table_year_hints))
