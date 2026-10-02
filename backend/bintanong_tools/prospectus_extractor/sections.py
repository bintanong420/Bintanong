"""Structural tokenizer, curriculum sections and course row assembly."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Any
from typing import Mapping
from typing import Protocol
from typing import Sequence
import re

from .text import INLINE_SEMESTER_PREFIX, YEAR_ORDER, clean_str, is_banner_text, match_semester_labels, match_year_label, norm_key, term_index
from .footnotes import FootnoteContext
from .units import parse_units, rescue_units_from_title
from .prerequisites import ADMIN_METADATA_PATTERN, POLICY_NOTE_PATTERN, TOTAL_ROW_PATTERN, is_standing_rule, is_unit_like_token
from .grid import GridParseResult, _first_int, canonicalize_course_code, extract_grand_total, is_probable_course_code, looks_like_course
from .layout import ColumnGroup, classify_header_cell, is_header_row
from .evidence import NormalizedCell, NormalizedTable, ProspectusEvidence, project_table_to_grid


class TokenType(str, Enum):
    YEAR_MARKER = "YEAR_MARKER"
    SEMESTER_MARKER = "SEMESTER_MARKER"
    HEADER = "HEADER"
    COURSE_CODE_CANDIDATE = "COURSE_CODE_CANDIDATE"
    COURSE_TITLE_CANDIDATE = "COURSE_TITLE_CANDIDATE"
    UNIT_CANDIDATE = "UNIT_CANDIDATE"
    PREREQUISITE_CANDIDATE = "PREREQUISITE_CANDIDATE"
    TERM_TOTAL = "TERM_TOTAL"
    PROGRAM_TOTAL = "PROGRAM_TOTAL"
    CONTINUATION = "CONTINUATION"
    FOOTNOTE = "FOOTNOTE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class StructuralToken:
    token_type: TokenType
    table_index: int
    row_start: int
    row_end: int
    col_start: int
    col_end: int
    cell_id: str
    text: str
    value: str | None = None
    group_index: int | None = None
    confidence: str = "high"
    reasons: tuple[str, ...] = ()
    supporting_cell_ids: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "type": self.token_type.value,
            "table_index": self.table_index,
            "row_start": self.row_start,
            "row_end": self.row_end,
            "col_start": self.col_start,
            "col_end": self.col_end,
            "cell_id": self.cell_id,
            "text": self.text,
            "value": self.value,
            "group_index": self.group_index,
            "confidence": self.confidence,
            "reasons": list(self.reasons),
            "supporting_cell_ids": list(self.supporting_cell_ids),
        }


@dataclass
class FieldCandidate:
    value: str
    evidence_cell_ids: list[str] = field(default_factory=list)
    confidence_flags: list[str] = field(default_factory=list)

    def append(self, value: str, cell_ids: Sequence[str], separator: str = " ") -> None:
        value = clean_str(value)
        if value:
            self.value = clean_str(f"{self.value}{separator}{value}") if self.value else value
        for cell_id in cell_ids:
            if cell_id not in self.evidence_cell_ids:
                self.evidence_cell_ids.append(cell_id)


@dataclass
class CourseCandidate:
    candidate_id: str
    table_index: int
    group_index: int
    row_start: int
    row_end: int
    code: FieldCandidate | None = None
    title: FieldCandidate | None = None
    units: FieldCandidate | None = None
    prerequisites: FieldCandidate | None = None
    year_level: FieldCandidate | None = None
    semester: FieldCandidate | None = None
    source_cell_ids: list[str] = field(default_factory=list)
    confidence_flags: list[str] = field(default_factory=list)
    discarded_fragments: list[dict[str, Any]] = field(default_factory=list)

    def absorb(self, field_name: str, candidate: FieldCandidate | None) -> None:
        if candidate is None or not candidate.value:
            return
        current = getattr(self, field_name)
        if current is None:
            setattr(self, field_name, candidate)
        else:
            separator = "" if field_name == "code" and current.value.endswith("-") else " "
            if not separator:
                current.value = re.sub(r"\s+-$", "-", current.value)
            current.append(candidate.value, candidate.evidence_cell_ids, separator)
            if "adjacent_row_continuation" not in current.confidence_flags:
                current.confidence_flags.append("adjacent_row_continuation")
        for cell_id in candidate.evidence_cell_ids:
            if cell_id not in self.source_cell_ids:
                self.source_cell_ids.append(cell_id)


@dataclass
class CurriculumSection:
    table_index: int
    year_level: str
    semester_by_group: dict[int, str]
    start_row: int
    end_row: int
    evidence_cells: list[str] = field(default_factory=list)
    confidence_flags: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "table_index": self.table_index,
            "year_level": self.year_level,
            "semester_by_group": {str(k): v for k, v in self.semester_by_group.items()},
            "start_row": self.start_row,
            "end_row": self.end_row,
            "evidence_cells": list(self.evidence_cells),
            "confidence_flags": list(self.confidence_flags),
        }


class SemanticRepairProvider(Protocol):
    """Callable boundary for an optional evidence-constrained repair model."""

    def __call__(self, packet: Mapping[str, Any]) -> Mapping[str, Any] | str: ...


def _cell_for_column(table: NormalizedTable, row: int, col: int) -> NormalizedCell | None:
    candidates = [cell for cell in table.cells if cell.overlaps(row, col)]
    if not candidates:
        return None
    return min(
        candidates,
        key=lambda cell: (
            cell.row_span * cell.col_span,
            0 if cell.row_start == row else 1,
            cell.col_start,
            cell.cell_id,
        ),
    )


def _cells_in_group_row(
    table: NormalizedTable, row: int, group: ColumnGroup
) -> list[NormalizedCell]:
    left, right = min(group.span()), max(group.span()) + 1
    return sorted(
        (
            cell
            for cell in table.cells_on_row(row)
            if cell.col_start < right and cell.col_end > left
        ),
        key=lambda cell: (cell.col_start, cell.col_end, cell.cell_id),
    )


def _field_at(table: NormalizedTable, row: int, col: int) -> FieldCandidate | None:
    cell = _cell_for_column(table, row, col)
    if cell is None or not cell.text:
        return None
    return FieldCandidate(cell.text, [cell.cell_id])


def _split_year_banners(
    table: NormalizedTable, groups: Sequence[ColumnGroup]
) -> list[tuple[NormalizedCell, NormalizedCell, str]]:
    """Find year headings split at the boundary between two course groups."""
    if len(groups) < 2:
        return []
    ordinal_words = {"FIRST", "SECOND", "THIRD", "FOURTH", "FIFTH",
                     "1ST", "2ND", "3RD", "4TH", "5TH"}
    found: list[tuple[NormalizedCell, NormalizedCell, str]] = []
    for ordinal in table.cells:
        if (clean_str(ordinal.text).upper() not in ordinal_words
                or not groups[0].unit_idx < ordinal.col_start <= groups[1].code_idx):
            continue
        for year_cell in table.cells:
            next_row = year_cell.row_start == ordinal.row_start + 1
            adjacent = (year_cell.col_start == ordinal.col_end if not next_row
                        else ordinal.col_start <= year_cell.col_start < ordinal.col_end)
            if (year_cell.row_start not in (ordinal.row_start, ordinal.row_start + 1)
                    or not adjacent or not re.match(r"^YEAR\b", year_cell.text, re.IGNORECASE)):
                continue
            year = match_year_label(f"{ordinal.text} {year_cell.text}")
            if year:
                found.append((ordinal, year_cell, year))
                break
    return found


def tokenize_table(table: NormalizedTable, groups: Sequence[ColumnGroup]) -> list[StructuralToken]:
    """Classify immutable source cells. Interpretations never replace source text."""
    tokens: list[StructuralToken] = []
    group_for_col: dict[int, int] = {}
    for group in groups:
        for col in group.span():
            group_for_col[col] = group.index

    for cell in table.cells:
        text = cell.text
        if not text:
            continue
        span_ratio = cell.col_span / max(table.num_cols, 1)
        year = match_year_label(text)
        semesters = match_semester_labels(text)
        header_kind = classify_header_cell(text)
        group_index = group_for_col.get(cell.col_start)
        common = dict(
            table_index=table.table_index,
            row_start=cell.row_start,
            row_end=cell.row_end,
            col_start=cell.col_start,
            col_end=cell.col_end,
            cell_id=cell.cell_id,
            text=text,
            group_index=group_index,
        )

        overlaps = _groups_overlapping_cell(cell, groups)
        row_has_course = any(
            other.cell_id != cell.cell_id
            and other.row_start == cell.row_start
            and is_probable_course_code(other.text)
            and any(other.col_start in group.span() for group in overlaps)
            for other in table.cells_on_row(cell.row_start)
        )
        structural = span_ratio >= 0.45 or (
            cell.col_span >= 2 and is_banner_text(text) and not row_has_course
        )

        if year and structural:
            tokens.append(
                StructuralToken(
                    TokenType.YEAR_MARKER,
                    value=year,
                    reasons=("year_text", "wide_span" if span_ratio >= 0.45 else "pure_banner"),
                    **common,
                )
            )
        inline_semester = bool(
            INLINE_SEMESTER_PREFIX.match(text)
            and any(cell.col_start in (group.code_idx, group.title_idx) for group in groups)
        )
        standalone_semester = bool(
            is_banner_text(text) and not row_has_course
            and len(overlaps) == 1
            and cell.col_start in (overlaps[0].code_idx, overlaps[0].title_idx)
            and not any(
                other.text and not is_banner_text(other.text)
                and any(other.col_start <= group.code_idx < other.col_end for group in groups)
                for other in table.cells_on_row(cell.row_start)
            )
        )
        if semesters and (structural or inline_semester or standalone_semester):
            for _position, semester in semesters:
                tokens.append(
                    StructuralToken(
                        TokenType.SEMESTER_MARKER,
                        value=semester,
                        reasons=("semester_text", "inline_course_heading" if inline_semester else
                                 "standalone_banner" if standalone_semester else "geometric_span"),
                        **common,
                    )
                )
        if header_kind != "other":
            tokens.append(StructuralToken(TokenType.HEADER, value=header_kind, **common))
        elif extract_grand_total(text) is not None:
            tokens.append(StructuralToken(TokenType.PROGRAM_TOTAL, value=text, **common))
        elif TOTAL_ROW_PATTERN.search(text):
            tokens.append(StructuralToken(TokenType.TERM_TOTAL, value=text, **common))
        elif is_probable_course_code(text):
            tokens.append(StructuralToken(TokenType.COURSE_CODE_CANDIDATE, value=text, **common))
        elif is_unit_like_token(text):
            tokens.append(StructuralToken(TokenType.UNIT_CANDIDATE, value=text, **common))
        elif not year and not semesters and header_kind == "other":
            tokens.append(
                StructuralToken(TokenType.UNKNOWN, value=text, confidence="unclassified", **common)
            )
    for ordinal, year_cell, year in _split_year_banners(table, groups):
        marker_row = year_cell.row_start
        if not any(
            (code := _field_at(table, marker_row, group.code_idx))
            and is_probable_course_code(re.sub(r"^YEAR\b\s*", "", code.value,
                                           count=1, flags=re.IGNORECASE))
            for group in groups
        ):
            marker_row = min(marker_row + 1, table.num_rows)
        if any(token.token_type == TokenType.YEAR_MARKER and token.row_start == marker_row
               and token.value == year for token in tokens):
            continue
        tokens.append(StructuralToken(
            TokenType.YEAR_MARKER, table.table_index,
            marker_row, marker_row,
            ordinal.col_start, year_cell.col_end,
            ordinal.cell_id, f"{ordinal.text} {year_cell.text}",
            value=year, confidence="structural",
            reasons=("split_year_banner",), supporting_cell_ids=(year_cell.cell_id,),
        ))
    return tokens


def _groups_overlapping_cell(
    cell: NormalizedCell, groups: Sequence[ColumnGroup]
) -> list[ColumnGroup]:
    out: list[ColumnGroup] = []
    for group in groups:
        left, right = min(group.span()), max(group.span()) + 1
        if cell.col_start < right and cell.col_end > left:
            out.append(group)
    return out


def _semester_mapping_at_row(
    table: NormalizedTable,
    row: int,
    groups: Sequence[ColumnGroup],
    tokens: Sequence[StructuralToken],
) -> tuple[dict[int, str], list[str], list[str]]:
    """Map semester evidence to groups; never fan one label across many groups."""
    mapping: dict[int, str] = {}
    evidence: list[str] = []
    problems: list[str] = []
    token_cells = {
        token.cell_id
        for token in tokens
        if token.token_type == TokenType.SEMESTER_MARKER and token.row_start == row
    }
    cells_by_id = table.cell_map()
    for cell_id in sorted(token_cells):
        cell = cells_by_id[cell_id]
        labels = [label for _position, label in match_semester_labels(cell.text)]
        overlaps = _groups_overlapping_cell(cell, groups)
        if len(labels) == len(overlaps) and labels:
            for group, label in zip(overlaps, labels):
                mapping[group.index] = label
            evidence.append(cell_id)
        elif len(labels) == 1 and len(overlaps) == 1:
            mapping[overlaps[0].index] = labels[0]
            evidence.append(cell_id)
        elif len(labels) == 1 and len(overlaps) > 1:
            label = labels[0]
            label_lower = label.lower()
            if "1st" in label_lower or "first" in label_lower:
                mapping[overlaps[0].index] = label
                if len(overlaps) >= 2:
                    mapping[overlaps[1].index] = "2nd Semester"
            elif ("2nd" in label_lower or "second" in label_lower) and len(overlaps) >= 2:
                mapping[overlaps[0].index] = "1st Semester"
                mapping[overlaps[1].index] = label
            elif ("3rd" in label_lower or "third" in label_lower) and len(overlaps) >= 3:
                mapping[overlaps[0].index] = "1st Semester"
                mapping[overlaps[1].index] = "2nd Semester"
                mapping[overlaps[2].index] = label
            else:
                for group in overlaps:
                    mapping[group.index] = label
            evidence.append(cell_id)
        else:
            problems.append(
                f"semester cell {cell_id} has {len(labels)} label(s) for "
                f"{len(overlaps)} column group(s)"
            )
    for group in groups:
        if group.index in mapping:
            continue
        code = _field_at(table, row, group.code_idx)
        title = _field_at(table, row, group.title_idx)
        if title and is_banner_text(title.value):
            labels = match_semester_labels(title.value)
            if len(labels) == 1:
                mapping[group.index] = labels[0][1]
                evidence.append(title.evidence_cell_ids[0])
                continue
        if code and title and re.match(r"^FIRST\b", code.value, re.IGNORECASE) and re.match(
            r"^SEMESTER\b", title.value, re.IGNORECASE
        ):
            mapping[group.index] = "1st Semester"
            evidence.extend([code.evidence_cell_ids[0], title.evidence_cell_ids[0]])
    return mapping, evidence, problems


def build_curriculum_sections(
    evidence: ProspectusEvidence,
    table: NormalizedTable,
    groups: Sequence[ColumnGroup],
    tokens: Sequence[StructuralToken],
) -> tuple[list[CurriculumSection], list[dict[str, Any]]]:
    """Build explicit year/semester-bounded sections from structural evidence."""
    anomalies: list[dict[str, Any]] = []
    year_tokens: list[StructuralToken] = []
    seen_year_rows: set[tuple[int, str]] = set()
    for token in sorted(tokens, key=lambda t: (t.row_start, t.col_start, t.cell_id)):
        if token.token_type != TokenType.YEAR_MARKER or not token.value:
            continue
        key = (token.row_start, token.value)
        if key not in seen_year_rows:
            year_tokens.append(token)
            seen_year_rows.add(key)

    if year_tokens and year_tokens[0].row_start > 0:
        early_semesters = [t for t in tokens if t.token_type == TokenType.SEMESTER_MARKER and t.row_start < year_tokens[0].row_start]
        if early_semesters:
            year_tokens.insert(0, StructuralToken(
                TokenType.YEAR_MARKER,
                table.table_index,
                0,
                0,
                0,
                table.num_cols,
                "",
                "1st Year",
                value="1st Year",
                confidence="inferred",
                reasons=("inferred_from_early_semesters",)
            ))

    if not year_tokens and table.table_index in evidence.table_year_hints:
        year = evidence.table_year_hints[table.table_index]
        source_id = evidence.table_year_hint_sources.get(table.table_index, "")
        year_tokens.append(
            StructuralToken(
                TokenType.YEAR_MARKER,
                table.table_index,
                0,
                0,
                0,
                table.num_cols,
                source_id,
                year,
                value=year,
                confidence="document_order",
                reasons=("preceding_docling_text",),
            )
        )

    # Two-up prospectuses close both terms before starting the next year.
    # Docling sometimes omits the intervening year banner while retaining totals.
    for row in range(table.num_rows - 1):
        if any(token.row_start in (row, row + 1) for token in year_tokens):
            continue
        if not groups or not all(_is_total_row_for_group(table, row, group) for group in groups):
            continue
        code_columns = {group.code_idx for group in groups}
        if not any(
            is_probable_course_code(cell.text)
            and any(cell.col_start <= col < cell.col_end for col in code_columns)
            for next_row in range(row + 1, min(row + 3, table.num_rows))
            for cell in table.cells_on_row(next_row)
        ):
            continue
        previous = max((token for token in year_tokens if token.row_start < row),
                       key=lambda token: token.row_start, default=None)
        next_order = YEAR_ORDER.get(previous.value, 0) + 1 if previous else 0
        next_year = next((label for label, order in YEAR_ORDER.items() if order == next_order), None)
        following = min((token for token in year_tokens if token.row_start > row + 1),
                        key=lambda token: token.row_start, default=None)
        if not next_year or not following or YEAR_ORDER.get(following.value, 0) <= next_order:
            continue
        source = next((cell for cell in table.cells_on_row(row) if TOTAL_ROW_PATTERN.search(cell.text)), None)
        year_tokens.append(StructuralToken(
            TokenType.YEAR_MARKER, table.table_index, row + 1, row + 1,
            0, table.num_cols, source.cell_id if source else "", next_year,
            value=next_year, confidence="structural",
            reasons=("preceding_two_term_totals",),
        ))
    year_tokens.sort(key=lambda token: token.row_start)

    if not year_tokens:
        anomalies.append(
            {
                "id": f"t{table.table_index}-missing-year",
                "type": "missing_year_marker",
                "table_index": table.table_index,
                "row": 0,
                "reason": "table contains no verified year marker",
                "source_cell_ids": [],
            }
        )
        return [], anomalies

    sections: list[CurriculumSection] = []
    last_mapping: dict[int, str] = {}
    for year_pos, year_token in enumerate(year_tokens):
        year_mapping: dict[int, str] = {}
        year_search_start = max(0, year_token.row_start)
        year_end = (
            year_tokens[year_pos + 1].row_start
            if year_pos + 1 < len(year_tokens)
            else table.num_rows
        )
        semester_rows = sorted(
            {
                token.row_start
                for token in tokens
                if token.token_type == TokenType.SEMESTER_MARKER
                and year_search_start <= token.row_start < year_end
            }
        )
        events: list[tuple[int, int, dict[int, str], list[str]]] = []
        for semester_row in semester_rows:
            mapping, semester_evidence, problems = _semester_mapping_at_row(
                table, semester_row, groups, tokens
            )
            for problem in problems:
                anomalies.append(
                    {
                        "id": f"t{table.table_index}-r{semester_row}-semester-ambiguous",
                        "type": "semester_mapping_ambiguous",
                        "table_index": table.table_index,
                        "row": semester_row,
                        "reason": problem,
                        "source_cell_ids": semester_evidence,
                    }
                )
            row_end = max(
                (
                    token.row_end
                    for token in tokens
                    if token.token_type == TokenType.SEMESTER_MARKER
                    and token.row_start == semester_row
                ),
                default=semester_row + 1,
            )
            if any(
                "inline_course_heading" in token.reasons
                for token in tokens
                if token.token_type == TokenType.SEMESTER_MARKER and token.row_start == semester_row
            ):
                row_end = semester_row
            if year_token.row_start == semester_row:
                row_end = max(row_end, year_token.row_end)
            if mapping:
                year_mapping.update(mapping)
                last_mapping = year_mapping.copy()
                events.append((semester_row, row_end, year_mapping.copy(), semester_evidence))

        if not events:
            if last_mapping and "Summer" not in last_mapping.values():
                # Inherit mapping from the previous section
                start = year_search_start if year_token.row_end == year_token.row_start else year_search_start + 1
                events.append((year_search_start, start, last_mapping.copy(), []))
            else:
                anomalies.append(
                    {
                        "id": f"t{table.table_index}-r{year_search_start}-missing-semester",
                        "type": "missing_semester_marker",
                        "table_index": table.table_index,
                        "row": year_search_start,
                        "reason": f"{year_token.value} has no verified semester mapping",
                        "source_cell_ids": [year_token.cell_id, *year_token.supporting_cell_ids]
                        if year_token.cell_id else [],
                    }
                )
                sections.append(
                    CurriculumSection(
                        table.table_index,
                        year_token.value or "",
                        {},
                        year_token.row_end,
                        year_end,
                        [year_token.cell_id, *year_token.supporting_cell_ids]
                        if year_token.cell_id else [],
                        ["missing_semester_mapping"],
                    )
                )
                continue

        for event_pos, (event_row, event_end, mapping, semester_evidence) in enumerate(events):
            section_end = events[event_pos + 1][0] if event_pos + 1 < len(events) else year_end
            missing_groups = [group.index for group in groups if group.index not in mapping]
            flags: list[str] = []
            if missing_groups:
                flags.append("incomplete_semester_mapping")
                anomalies.append(
                    {
                        "id": f"t{table.table_index}-r{event_row}-missing-groups",
                        "type": "missing_semester_for_group",
                        "table_index": table.table_index,
                        "row": event_row,
                        "reason": f"semester not verified for column group(s) {missing_groups}",
                        "source_cell_ids": semester_evidence,
                    }
                )
            cells = [year_token.cell_id] if year_token.cell_id else []
            cells.extend(year_token.supporting_cell_ids)
            cells.extend(cell_id for cell_id in semester_evidence if cell_id not in cells)
            sections.append(
                CurriculumSection(
                    table.table_index,
                    year_token.value or "",
                    mapping,
                    event_end,
                    section_end,
                    cells,
                    flags,
                )
            )
    return sections, anomalies


def _row_field_candidates(
    table: NormalizedTable, row: int, group: ColumnGroup,
    groups: Sequence[ColumnGroup],
) -> dict[str, FieldCandidate | None]:
    fields: dict[str, FieldCandidate | None] = {
        "code": _field_at(table, row, group.code_idx),
        "title": _field_at(table, row, group.title_idx),
        "units": _field_at(table, row, group.unit_idx),
        "prerequisites": _field_at(table, row, group.prereq_idx),
    }
    split_years = _split_year_banners(table, groups)
    for ordinal, year_cell, _year in split_years:
        for name, field in fields.items():
            if field is None:
                continue
            if ordinal.row_start == row and ordinal.cell_id in field.evidence_cell_ids:
                fields[name] = None
            elif year_cell.row_start == row and year_cell.cell_id in field.evidence_cell_ids:
                remainder = re.sub(r"^YEAR\b\s*", "", field.value, count=1, flags=re.IGNORECASE)
                fields[name] = (FieldCandidate(remainder, field.evidence_cell_ids,
                                               ["split_year_banner"]) if remainder else None)
    code = fields["code"]
    if code:
        code.value = re.sub(r"\s*/\s*", "/", code.value)
    code, title = fields["code"], fields["title"]
    if not code and title and fields["units"] and is_unit_like_token(fields["units"].value):
        fused = re.match(
            r"^([A-Z]{2,8}(?:[\s-]+[A-Z]{2,8})?[\s-]*\d{1,4}(?:/[A-Z0-9]+)?)\s+(.+)$",
            title.value,
        )
        if fused and is_probable_course_code(fused.group(1)):
            fields["code"] = FieldCandidate(fused.group(1), title.evidence_cell_ids, ["fused_code_title"])
            fields["title"] = FieldCandidate(fused.group(2), title.evidence_cell_ids, ["fused_code_title"])
            code, title = fields["code"], fields["title"]
    if code and title and re.match(r"^SEMESTER\s+", title.value, re.IGNORECASE):
        first = re.match(r"^FIRST\s+(.+)$", code.value, re.IGNORECASE)
        if first and is_probable_course_code(first.group(1)):
            fields["code"] = FieldCandidate(first.group(1), code.evidence_cell_ids, ["split_semester_heading"])
            fields["title"] = FieldCandidate(
                re.sub(r"^SEMESTER\s+", "", title.value, flags=re.IGNORECASE),
                title.evidence_cell_ids, ["split_semester_heading"],
            )
    code = fields["code"]
    inline = INLINE_SEMESTER_PREFIX.match(code.value) if code else None
    if inline:
        parts = inline.group(1).split()
        for length in range(min(3, len(parts)), 0, -1):
            possible_code = " ".join(parts[:length])
            if is_probable_course_code(possible_code):
                fields["code"] = FieldCandidate(possible_code, code.evidence_cell_ids, ["inline_course_heading"])
                remainder = " ".join(parts[length:])
                if remainder:
                    fields["title"] = FieldCandidate(remainder, code.evidence_cell_ids, ["inline_course_heading"])
                break
    code = fields["code"]
    numeric_prefix = re.match(r"^\d{1,3}\s+(.+)$", code.value) if code else None
    if numeric_prefix and is_probable_course_code(numeric_prefix.group(1)):
        fields["code"] = FieldCandidate(
            numeric_prefix.group(1), code.evidence_cell_ids, ["leading_numeric_bleed"]
        )
    code = fields["code"]
    if code and not is_probable_course_code(code.value) and not TOTAL_ROW_PATTERN.search(code.value):
        parts = code.value.split()
        for length in range(len(parts) - 1, 0, -1):
            possible_code = " ".join(parts[:length])
            if is_probable_course_code(possible_code):
                fields["code"] = FieldCandidate(possible_code, code.evidence_cell_ids, ["fused_code_title"])
                prefix = " ".join(parts[length:])
                old_title = fields["title"]
                fields["title"] = FieldCandidate(
                    clean_str(f"{prefix} {old_title.value if old_title else ''}"),
                    list(dict.fromkeys(code.evidence_cell_ids + (old_title.evidence_cell_ids if old_title else []))),
                    ["fused_code_title"],
                )
                break
    title = fields["title"]
    inline = INLINE_SEMESTER_PREFIX.match(title.value) if title else None
    if inline:
        fields["title"] = FieldCandidate(inline.group(1), title.evidence_cell_ids, ["inline_course_heading"])
    prereq = fields["prerequisites"]
    fused_unit = re.match(r"^(\d+(?:/\d+)?)\s+(.+)$", prereq.value) if prereq else None
    if not fields["units"] and fused_unit:
        fields["units"] = FieldCandidate(fused_unit.group(1), prereq.evidence_cell_ids, ["fused_unit_prerequisite"])
        fields["prerequisites"] = FieldCandidate(
            fused_unit.group(2), prereq.evidence_cell_ids, ["fused_unit_prerequisite"]
        )
    cells = _cells_in_group_row(table, row, group)
    structural_ids = {
        cell.cell_id
        for cell in cells
        if match_year_label(cell.text)
        or match_semester_labels(cell.text)
        or classify_header_cell(cell.text) != "other"
    }
    structural_ids.update(cell.cell_id for ordinal, year_cell, _year in split_years
                          for cell in (ordinal, year_cell)
                          if cell.row_start == row and (cell == ordinal or clean_str(cell.text).upper() == "YEAR"))

    code = fields["code"]
    if code is None or not code.value:
        hits = [
            cell for cell in cells
            if cell.cell_id not in structural_ids
            and cell.col_start in (group.code_idx, group.title_idx)
            and is_probable_course_code(cell.text)
        ]
        if len(hits) == 1:
            fields["code"] = FieldCandidate(
                hits[0].text, [hits[0].cell_id], ["geometry_recovered_code"]
            )

    units = fields["units"]
    if units is None or not is_unit_like_token(units.value):
        hits = [cell for cell in cells if cell.cell_id not in structural_ids and is_unit_like_token(cell.text)]
        if len(hits) == 1:
            fields["units"] = FieldCandidate(
                hits[0].text, [hits[0].cell_id], ["geometry_recovered_units"]
            )

    used = {
        cell_id
        for candidate in fields.values()
        if candidate is not None
        for cell_id in candidate.evidence_cell_ids
    }
    title = fields["title"]
    if title is None or any(cell_id in structural_ids for cell_id in title.evidence_cell_ids):
        remaining = [
            cell
            for cell in cells
            if cell.cell_id not in used
            and cell.cell_id not in structural_ids
            and not is_probable_course_code(cell.text)
            and not is_unit_like_token(cell.text)
            and not TOTAL_ROW_PATTERN.search(cell.text)
        ]
        if remaining:
            best = max(remaining, key=lambda cell: (len(cell.text), -cell.col_start))
            fields["title"] = FieldCandidate(
                best.text, [best.cell_id], ["geometry_recovered_title"]
            )
    return fields


def _candidate_has_payload(fields: Mapping[str, FieldCandidate | None]) -> bool:
    return any(candidate is not None and candidate.value for candidate in fields.values())


def _is_total_row_for_group(table: NormalizedTable, row: int, group: ColumnGroup) -> bool:
    cells = _cells_in_group_row(table, row, group)
    if any(
        TOTAL_ROW_PATTERN.search(cell.text)
        for cell in cells
        if cell.text and cell.col_start <= group.code_idx < cell.col_end
    ):
        return True
    # A damaged TOTAL label may survive only in the opposite group; a bare
    # numeric unit cell on that same row is still a checksum, not a course.
    unit = _field_at(table, row, group.unit_idx)
    code = _field_at(table, row, group.code_idx)
    return bool(
        unit and is_unit_like_token(unit.value)
        and (not code or not code.value)
        and any(
            TOTAL_ROW_PATTERN.search(cell.text)
            and cell.col_start not in group.span()
            for cell in table.cells_on_row(row)
        )
    )


def _strip_structural_prerequisite_bleed(
    raw: str, year_level: str, evidence_ids: Sequence[str]
) -> tuple[str, list[dict[str, Any]]]:
    """Remove a year word only when it prefixes a code-like prerequisite run."""
    ordinal = {
        "1st Year": "FIRST",
        "2nd Year": "SECOND",
        "3rd Year": "THIRD",
        "4th Year": "FOURTH",
        "5th Year": "FIFTH",
    }.get(year_level)
    value = clean_str(raw)
    if not ordinal or not value:
        return value, []
    pattern = re.compile(
        rf"^({ordinal}(?:\s+YEAR)?)\s+(?=[A-Z]{{1,8}}(?:[\s-]+[A-Z]{{1,6}})?[\s-]*\d)",
        re.IGNORECASE,
    )
    match = pattern.match(value)
    if not match:
        return value, []
    cleaned = clean_str(value[match.end() :])
    return cleaned, [
        {
            "text": match.group(1),
            "source_cell_ids": list(evidence_ids),
            "reason": "structural year-banner bleed before prerequisite code",
        }
    ]


def _union_bbox(cells: Sequence[NormalizedCell]) -> tuple[int | None, list[float] | None]:
    boxes = [cell.bbox for cell in cells if cell.bbox and cell.bbox.is_complete()]
    if not boxes:
        return None, None
    pages = {box.page for box in boxes}
    page = next(iter(pages)) if len(pages) == 1 else None
    if page is None:
        return None, None
    return page, [
        min(float(box.left) for box in boxes if box.left is not None),
        min(float(box.top) for box in boxes if box.top is not None),
        max(float(box.right) for box in boxes if box.right is not None),
        max(float(box.bottom) for box in boxes if box.bottom is not None),
    ]


def _make_provenance(
    evidence: ProspectusEvidence,
    table_index: int,
    source_cell_ids: Sequence[str],
    resolution_method: str = "deterministic",
    repair_id: str | None = None,
) -> dict[str, Any]:
    all_cells = evidence.all_cells()
    unique_ids = list(dict.fromkeys(cell_id for cell_id in source_cell_ids if cell_id))
    cells = [all_cells[cell_id] for cell_id in unique_ids if cell_id in all_cells]
    page, bbox = _union_bbox(cells)
    return {
        "source_document": None,
        "raw_docling_json": None,
        "table_index": table_index,
        "source_cell_ids": unique_ids,
        "source_cells": [cell.as_evidence_dict() for cell in cells],
        "page": page,
        "bbox": bbox,
        "resolution_method": resolution_method,
        "repair_id": repair_id,
        "valid": bool(unique_ids) and len(cells) == len(unique_ids),
        "highlightable": page is not None and bbox is not None,
    }


def _assemble_section_candidates(
    evidence: ProspectusEvidence,
    table: NormalizedTable,
    groups: Sequence[ColumnGroup],
    section: CurriculumSection,
    result: GridParseResult,
) -> list[CourseCandidate]:
    candidates: list[CourseCandidate] = []
    pending: dict[int, CourseCandidate] = {}
    blocked_cells = {
        cell_id for anomaly in result.anomalies
        if anomaly.get("type") == "multiple_course_codes_in_cell"
        and anomaly.get("table_index") == table.table_index
        for cell_id in anomaly["source_cell_ids"]
    }
    grid = project_table_to_grid(table)

    def flush(group_index: int) -> None:
        candidate = pending.pop(group_index, None)
        if candidate is not None:
            candidates.append(candidate)

    for row in range(section.start_row, section.end_row):
        row_cells = table.cells_on_row(row)
        if not row_cells:
            continue
        row_text = " ".join(dict.fromkeys(cell.text for cell in row_cells if cell.text))
        projected = grid[row] if row < len(grid) else []
        if is_header_row(projected) or ADMIN_METADATA_PATTERN.search(row_text):
            continue
        if any(
            cell.col_span / max(table.num_cols, 1) >= 0.45
            and (match_year_label(cell.text) or match_semester_labels(cell.text))
            for cell in row_cells
        ):
            continue
        if POLICY_NOTE_PATTERN.search(row_text):
            note = clean_str(row_text)
            if note and note not in result.policy_notes:
                result.policy_notes.append(note)

        for group in groups:
            if any(cell.cell_id in blocked_cells
                   for cell in _cells_in_group_row(table, row, group)):
                # Flattened cell text cannot establish separate title/prerequisite ownership.
                flush(group.index)
                continue
            if any(
                extract_grand_total(cell.text) is not None
                and cell.col_start <= group.code_idx < cell.col_end
                for cell in row_cells
            ):
                flush(group.index)
                continue
            code_cell = _field_at(table, row, group.code_idx)
            if (not code_cell or not is_probable_course_code(code_cell.value)) and any(
                POLICY_NOTE_PATTERN.search(cell.text)
                for cell in _cells_in_group_row(table, row, group)
            ):
                flush(group.index)
                continue
            previous = pending.get(group.index)
            leading_number = re.match(r"^(\d{1,3})\s+(.+)$", code_cell.value) if code_cell else None
            if (
                previous and previous.code
                and not is_probable_course_code(previous.code.value)
                and not re.search(r"\d", previous.code.value)
                and leading_number and is_probable_course_code(leading_number.group(2))
            ):
                previous.absorb(
                    "code", FieldCandidate(leading_number.group(1), code_cell.evidence_cell_ids,
                                           ["adjacent_code_suffix"])
                )
            fields = _row_field_candidates(table, row, group, groups)
            suffix_and_code = re.fullmatch(r"([A-Z]{2,3})\s+(.+)", fields["code"].value) if fields["code"] else None
            if (
                previous and previous.row_end == row and previous.code
                and (previous.code.value.endswith(":")
                     or re.fullmatch(r"[A-Z]{2,8}\s*-", previous.code.value))
                and suffix_and_code
                and suffix_and_code.group(2).isupper()
                and is_probable_course_code(suffix_and_code.group(2))
            ):
                previous.absorb("code", FieldCandidate(suffix_and_code.group(1), fields["code"].evidence_cell_ids))
                fields["code"] = FieldCandidate(
                    suffix_and_code.group(2), fields["code"].evidence_cell_ids, ["adjacent_code_suffix"]
                )
            semester = section.semester_by_group.get(group.index)
            mixed_total = None
            if _is_total_row_for_group(table, row, group):
                existing = pending.get(group.index)
                code_fragment = fields.get("code")
                units_fragment = fields.get("units")
                course_prefix = re.match(r"^(.+?)\s+TOTAL\b", code_fragment.value, re.IGNORECASE) if code_fragment else None
                split_units = re.fullmatch(r"(\d+(?:/\d+)?)\s+(\d{1,3})", units_fragment.value) if units_fragment else None
                if course_prefix and split_units and is_probable_course_code(course_prefix.group(1)):
                    fields["code"] = FieldCandidate(course_prefix.group(1), code_fragment.evidence_cell_ids)
                    fields["units"] = FieldCandidate(split_units.group(1), units_fragment.evidence_cell_ids)
                    mixed_total = int(split_units.group(2))
                else:
                    suffix = re.match(r"^(\d{1,3})\s+TOTAL\b", code_fragment.value, re.IGNORECASE) if code_fragment else None
                    if (
                        course_prefix and existing and existing.code
                        and norm_key(existing.code.value) == norm_key(course_prefix.group(1))
                        and not existing.prerequisites and fields.get("prerequisites")
                    ):
                        existing.absorb("prerequisites", fields["prerequisites"])
                    if suffix and existing and existing.code and not re.search(r"\d", existing.code.value):
                        existing.absorb("code", FieldCandidate(suffix.group(1), code_fragment.evidence_cell_ids))
                        for name in ("title", "prerequisites"):
                            fragment = fields.get(name)
                            if fragment and fragment.value and not TOTAL_ROW_PATTERN.search(fragment.value):
                                existing.absorb(name, fragment)
                        existing.row_end = row + 1
                    declared = _first_int(
                        candidate.value
                        for candidate in (
                            fields.get("units"),
                            fields.get("prerequisites"),
                            fields.get("title"),
                            fields.get("code"),
                        )
                        if candidate is not None
                    )
                    if declared is not None and semester:
                        result.declared_term_units[(section.year_level, semester)] = declared
                    flush(group.index)
                    continue
            if mixed_total is not None and semester:
                result.declared_term_units[(section.year_level, semester)] = mixed_total

            prior = pending.get(group.index)
            if (
                prior and prior.units and prior.row_end == row
                and fields.get("code") and is_probable_course_code(fields["code"].value)
                and fields.get("title") and not fields.get("units")
            ):
                spill = re.fullmatch(r"([1-9])\s+([1-9])", prior.units.value)
                if spill:
                    evidence_ids = prior.units.evidence_cell_ids
                    prior.units = FieldCandidate(spill.group(1), evidence_ids, ["adjacent_unit_spillover"])
                    fields["units"] = FieldCandidate(spill.group(2), evidence_ids, ["adjacent_unit_spillover"])
            if (
                prior and prior.title and prior.units
                and not fields.get("code") and fields.get("title") and fields.get("units")
                and row + 1 < section.end_row
                and _is_total_row_for_group(table, row + 1, group)
            ):
                following_code = _field_at(table, row + 1, group.code_idx)
                mixed_code = re.fullmatch(r"(.+?)\s+TOTAL", following_code.value, re.IGNORECASE) if following_code else None
                if mixed_code and is_probable_course_code(mixed_code.group(1)):
                    fragment = fields.get("prerequisites")
                    if (
                        prior.prerequisites and fragment
                        and re.fullmatch(r"[A-Z]{2,8}(?:\s+[A-Z]{2,8})?", prior.prerequisites.value)
                        and re.fullmatch(r"\d{1,3}(?:/[A-Z])?", fragment.value)
                        and is_probable_course_code(f"{prior.prerequisites.value} {fragment.value}")
                    ):
                        prior.absorb("prerequisites", fragment)
                        fields["prerequisites"] = None
                    flush(group.index)
                    fields["code"] = FieldCandidate(
                        mixed_code.group(1), following_code.evidence_cell_ids,
                        ["adjacent_code_on_total_row"],
                    )
                    if not fields.get("prerequisites"):
                        fields["prerequisites"] = _field_at(table, row + 1, group.prereq_idx)

            code = fields.get("code")
            title = fields.get("title")
            units = fields.get("units")
            prereq = fields.get("prerequisites")
            looks_course = bool(
                code
                and not re.search(r"[.!?]$", code.value)
                and looks_like_course(
                    code.value,
                    title.value if title else "",
                    units.value if units else "",
                )
            )
            starts_split_course = bool(code and is_probable_course_code(code.value))
            if looks_course or starts_split_course:
                existing = pending.get(group.index)
                if (
                    existing is not None and existing.row_end == row
                    and existing.prerequisites and is_standing_rule(existing.prerequisites.value)
                    and not existing.prerequisites.value.endswith((".", ":", ";"))
                    and prereq and re.fullmatch(r"[a-z]{4,}", prereq.value)
                    and code and title and units
                ):
                    source_ids = list(dict.fromkeys(
                        existing.prerequisites.evidence_cell_ids
                        + code.evidence_cell_ids + title.evidence_cell_ids
                        + units.evidence_cell_ids + prereq.evidence_cell_ids
                    ))
                    source_cells = [cell for cell in table.cells if cell.cell_id in source_ids]
                    result.anomalies.append({
                        "id": f"t{table.table_index}-r{row}-g{group.index}-prereq-spill",
                        "type": "ambiguous_adjacent_prerequisite_fragment",
                        "table_index": table.table_index,
                        "row": row,
                        "page": next((cell.bbox.page for cell in source_cells
                                      if cell.bbox and cell.bbox.page), None),
                        "reason": ("a lowercase prerequisite fragment beside a new course may "
                                   "continue the preceding standing rule; ownership unresolved"),
                        "source_cell_ids": source_ids,
                        "source_cells": [cell.as_evidence_dict() for cell in source_cells],
                    })
                    fields["prerequisites"] = prereq = None
                if (
                    existing is not None and existing.row_end == row and existing.prerequisites
                    and re.fullmatch(r"(?:[1-5](?:ST|ND|RD|TH)|FIRST|SECOND|THIRD|FOURTH|FIFTH) YEAR",
                                     existing.prerequisites.value, re.IGNORECASE)
                    and prereq and re.match(r"^STANDING\b", prereq.value, re.IGNORECASE)
                ):
                    existing.absorb("prerequisites", FieldCandidate("Standing", prereq.evidence_cell_ids))
                    remainder = re.sub(r"^STANDING\b\s*", "", prereq.value, count=1, flags=re.IGNORECASE)
                    fields["prerequisites"] = prereq = (
                        FieldCandidate(remainder, prereq.evidence_cell_ids) if remainder else None
                    )
                if existing is not None and existing.row_end == row and existing.prerequisites and prereq:
                    previous_prereq = existing.prerequisites.value
                    carried = None
                    if re.fullmatch(r"[A-Z]{2,8}(?:\s+[A-Z]{2,8})?", previous_prereq):
                        fragment = re.match(r"^(\d{1,3}(?:/[A-Z])?)(?:\s+(.+))?$", prereq.value)
                        if fragment and is_probable_course_code(f"{previous_prereq} {fragment.group(1)}"):
                            carried = fragment
                    elif previous_prereq.endswith("&"):
                        carried = re.match(
                            r"^([A-Z]{1,8}(?:\s+[A-Z]{1,8})?\s*\d{1,3}(?:/[A-Z])?)(?:\s+(.+))?$",
                            prereq.value,
                        )
                        if carried and not is_probable_course_code(carried.group(1)):
                            carried = None
                    if carried:
                        existing.absorb("prerequisites", FieldCandidate(carried.group(1), prereq.evidence_cell_ids))
                        fields["prerequisites"] = prereq = (
                            FieldCandidate(carried.group(2), prereq.evidence_cell_ids)
                            if carried.group(2) else None
                        )
                if existing is not None and existing.row_end == row and existing.title and title:
                    if existing.title.value.count("(") > existing.title.value.count(")"):
                        wrapped = re.match(r"^([^()]*\))\s+(.+)$", title.value)
                        if wrapped:
                            separator = "" if existing.title.value.endswith("-") else " "
                            existing.title.append(wrapped.group(1), title.evidence_cell_ids, separator)
                            for cell_id in title.evidence_cell_ids:
                                if cell_id not in existing.source_cell_ids:
                                    existing.source_cell_ids.append(cell_id)
                            title = FieldCandidate(
                                wrapped.group(2), title.evidence_cell_ids,
                                ["adjacent_title_wrap"],
                            )
                            fields["title"] = title
                if (
                    existing is not None and existing.row_end == row
                    and existing.prerequisites and existing.prerequisites.value.endswith(",")
                    and prereq and re.fullmatch(r"[A-Za-z][A-Za-z0-9/-]{1,18}", prereq.value)
                ):
                    existing.absorb("prerequisites", prereq)
                    fields["prerequisites"] = prereq = None
                if (
                    existing is not None and existing.row_end == row
                    and all(
                        (getattr(existing, name).value if getattr(existing, name) else "")
                        == (fields[name].value if fields[name] else "")
                        for name in ("code", "title", "units", "prerequisites")
                    )
                ):
                    existing.row_end = row + 1
                    continue
                flush(group.index)
                candidate = CourseCandidate(
                    candidate_id=f"t{table.table_index}-r{row}-g{group.index}",
                    table_index=table.table_index,
                    group_index=group.index,
                    row_start=row,
                    row_end=row + 1,
                    code=code,
                    title=title,
                    units=units,
                    prerequisites=prereq,
                    year_level=FieldCandidate(section.year_level, section.evidence_cells[:1]),
                    semester=(
                        FieldCandidate(semester, section.evidence_cells[1:]) if semester else None
                    ),
                )
                for field_value in (code, title, units, prereq):
                    if field_value:
                        for cell_id in field_value.evidence_cell_ids:
                            if cell_id not in candidate.source_cell_ids:
                                candidate.source_cell_ids.append(cell_id)
                for cell_id in section.evidence_cells:
                    if cell_id and cell_id not in candidate.source_cell_ids:
                        candidate.source_cell_ids.append(cell_id)
                if not semester:
                    candidate.confidence_flags.append("semester_unverified")
                    result.anomalies.append(
                        {
                            "id": f"{candidate.candidate_id}-semester",
                            "type": "course_without_verified_semester",
                            "candidate_id": candidate.candidate_id,
                            "table_index": table.table_index,
                            "row": row,
                            "reason": "course lies in a section without a verified semester mapping",
                            "source_cell_ids": candidate.source_cell_ids,
                        }
                    )
                pending[group.index] = candidate
                if mixed_total is not None:
                    flush(group.index)
                continue

            existing = pending.get(group.index)
            continuation_fields = {
                "title": title,
                "units": units,
                "prerequisites": prereq,
            }
            if (
                existing is not None 
                and any(item is not None and item.value for item in continuation_fields.values())
                and not (code and code.value and code.value.strip())
            ):
                for field_name, field_value in continuation_fields.items():
                    if field_value is None:
                        continue
                    # A projected code/title value can point to the same wide
                    # structural cell. Never append structural evidence.
                    if match_year_label(field_value.value) or match_semester_labels(field_value.value):
                        continue
                    existing.absorb(field_name, field_value)
                existing.row_end = max(existing.row_end, row + 1)
                if "adjacent_row_reconstruction" not in existing.confidence_flags:
                    existing.confidence_flags.append("adjacent_row_reconstruction")
            elif _candidate_has_payload(fields) and not _is_total_row_for_group(table, row, group):
                payload_ids = list(
                    dict.fromkeys(
                        cell_id
                        for item in fields.values()
                        if item is not None
                        for cell_id in item.evidence_cell_ids
                    )
                )
                if any(
                    is_probable_course_code(item.value)
                    for item in fields.values()
                    if item is not None
                ):
                    result.anomalies.append(
                        {
                            "id": f"t{table.table_index}-r{row}-g{group.index}-orphan",
                            "type": "unassembled_course_fragment",
                            "table_index": table.table_index,
                            "row": row,
                            "reason": "course-like evidence could not be assembled deterministically",
                            "source_cell_ids": payload_ids,
                        }
                    )

    for group in groups:
        flush(group.index)
    return candidates


def _candidate_to_raw_course(
    candidate: CourseCandidate,
    evidence: ProspectusEvidence,
    footnotes: FootnoteContext,
) -> dict[str, Any]:
    code_raw = candidate.code.value if candidate.code else ""
    title_raw = candidate.title.value if candidate.title else ""
    unit_raw = candidate.units.value if candidate.units else ""
    prereq_raw = candidate.prerequisites.value if candidate.prerequisites else ""
    title_with_units, unit_text = rescue_units_from_title(title_raw, unit_raw)
    title, marker = footnotes.clean_title(title_with_units, unit_text)
    year = candidate.year_level.value if candidate.year_level else None
    semester = candidate.semester.value if candidate.semester else None
    cleaned_prereq, discarded = _strip_structural_prerequisite_bleed(
        prereq_raw,
        year or "",
        candidate.prerequisites.evidence_cell_ids if candidate.prerequisites else [],
    )
    candidate.discarded_fragments.extend(discarded)
    code = canonicalize_course_code(code_raw, title)
    provenance = _make_provenance(
        evidence, candidate.table_index, candidate.source_cell_ids, "deterministic"
    )
    if discarded:
        provenance["discarded_fragments"] = discarded
        provenance["resolution_method"] = "deterministic_repair"
    return {
        "_candidate_id": candidate.candidate_id,
        "year_level": year,
        "semester": semester,
        "term_index": term_index(year or "", semester or ""),
        "course_code": code,
        "course_title": title,
        "title_raw": clean_str(title_raw),
        "footnote_marker": marker,
        "units": parse_units(unit_text),
        "prerequisites_raw": cleaned_prereq,
        "confidence_flags": list(candidate.confidence_flags),
        "provenance": provenance,
        "_source": {
            "table_index": candidate.table_index,
            "row_index": candidate.row_start,
            "column_group": candidate.group_index,
        },
    }


def detect_source_course_candidates(
    evidence: ProspectusEvidence,
    layouts: Mapping[int, Sequence[ColumnGroup]],
) -> list[dict[str, Any]]:
    """Permissive document-wide inventory constrained by code-column geometry."""
    found: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for table in evidence.tables:
        groups = layouts.get(table.table_index, [])
        code_columns = {group.code_idx for group in groups}
        for cell in table.cells:
            if not any(cell.col_start <= col < cell.col_end for col in code_columns):
                continue
            code = clean_str(cell.text)
            if not is_probable_course_code(code):
                continue
            key = (norm_key(code), cell.cell_id)
            if key in seen:
                continue
            seen.add(key)
            found.append(
                {
                    "code": code,
                    "normalized_code": norm_key(code),
                    "cell_ids": [cell.cell_id],
                    "table_index": table.table_index,
                    "page": cell.bbox.page if cell.bbox else None,
                    "bbox": cell.bbox.as_list() if cell.bbox else None,
                    "confidence": "high",
                }
            )
    return found
