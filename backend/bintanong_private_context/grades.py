"""Born-digital grade PDFs -> candidate rows -> student-stated facts (master 15.1 steps 5-7).

Rows are found only by the reviewed course aliases of the student's own curriculum, so an
unrecognized code stays unknown. A row carries the matched printed code, its candidate course ids
and grade-like marks shown back to the student; no other file text leaves this module, so
instructions inside a file never reach the router. A printed grade is never turned into
passed/failed here: only the student's explicit choice for a row becomes a ScopedFact.
"""
from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass

import pypdfium2 as pdfium

from ..bintanong_routing.contracts import CatalogEntry, ScopedFact
from .uploads import UploadRejected, ValidatedUpload

# Display-only: shown to the student beside the row, never interpreted.
_MARK = re.compile(r'(?<![\w.])(?:[1-5]\.\d{1,2}|INC|DRP)(?![\w.])')


@dataclass(frozen=True)
class GradeRow:
    row_id: str
    code_text: str
    candidates: tuple[str, ...]
    marks: tuple[str, ...]
    page: int


@dataclass(frozen=True)
class ExtractionResult:
    program_id: str
    curriculum_id: str
    rows: tuple[GradeRow, ...]
    unmatched_lines: int


def extract_grade_rows(upload: ValidatedUpload, catalog: tuple[CatalogEntry, ...], *,
                       program_id: str, curriculum_id: str) -> ExtractionResult:
    if upload.kind != 'pdf':
        raise UploadRejected('photo_ocr_unavailable')
    courses = curriculum_courses(catalog, program_id, curriculum_id)
    code = _code_pattern(courses)
    rows, unmatched = [], 0
    pages = _page_lines(upload.data)
    if not any(line.strip() for lines in pages for line in lines):
        raise UploadRejected('no_text_layer')
    for page_no, lines in enumerate(pages, 1):
        for line_no, line in enumerate(lines, 1):
            match = code.search(line) if code else None
            if match is None:
                unmatched += bool(_MARK.search(line))
                continue
            rows.append(GradeRow(f'row-{page_no}-{line_no}', match.group(), tuple(sorted(courses[match.group()])),
                                 tuple(_MARK.findall(line, match.end())), page_no))
    return ExtractionResult(program_id, curriculum_id, tuple(rows), unmatched)


def confirm_rows(result: ExtractionResult, decisions: dict[str, tuple[str, str]], *,
                 session_id: str, batch: int = 1) -> tuple[ScopedFact, ...]:
    """decisions: row_id -> (course_id, state) exactly as the student chose them. `batch` keeps fact ids
    from separate uploads (which reuse row positions) distinct within one session."""
    rows = {r.row_id: r for r in result.rows}
    facts = []
    for row_id, (course_id, state) in decisions.items():
        row = rows.get(row_id)
        if row is None:
            raise ValueError('unknown_row')
        if course_id not in row.candidates:
            raise ValueError('course_not_in_row')
        facts.append(ScopedFact(fact_id=f'fact-{batch}-{row_id}', session_id=session_id, program_id=result.program_id,
                                curriculum_id=result.curriculum_id, course_id=course_id, state=state))
    return tuple(facts)


def curriculum_courses(catalog: tuple[CatalogEntry, ...], program_id: str, curriculum_id: str) -> dict[str, set]:
    """Reviewed alias -> course ids, for the student's own curriculum only."""
    courses = defaultdict(set)
    for e in catalog:
        if e.kind == 'course' and e.program_id == program_id and e.curriculum_id == curriculum_id:
            for alias in e.aliases:
                courses[alias].add(e.entity_id)
    return courses


def _code_pattern(courses):
    if not courses:
        return None
    alternation = '|'.join(re.escape(a) for a in sorted(courses, key=len, reverse=True))
    return re.compile(rf'(?<![A-Za-z0-9])(?:{alternation})(?![A-Za-z0-9/])')


def _page_lines(data: bytes) -> list[list[str]]:
    document = pdfium.PdfDocument(data)
    try:
        pages = []
        for index in range(len(document)):
            page = document[index]
            text_page = page.get_textpage()
            try:
                pages.append(text_page.get_text_range().splitlines())
            finally:
                text_page.close()
                page.close()
        return pages
    finally:
        document.close()
