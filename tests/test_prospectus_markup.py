"""The markup twin: Docling evidence laid out as the printed prospectus reads."""

from __future__ import annotations

import re
from html import unescape

import pytest

from backend.bintanong_tools.prospectus_extractor.evidence import (
    NormalizedCell,
    NormalizedTable,
    ProspectusEvidence,
    SourceBBox,
)
from backend.bintanong_tools.prospectus_extractor.markup import render_prospectus_markup
from backend.bintanong_tools.prospectus_extractor.selftest import cs_fixture_grid, fixture_document

OK = {"audit": {"status": "ok"}}
ERROR = {"audit": {"status": "error"}}


def box(left: float, top: float, origin: str = "BL", height: float = 9.0, width: float = 100.0):
    """[l, t, r, b] for a box whose top edge is `top` points down from the page top in the BL frame.

    BL (Docling BOTTOMLEFT): y grows upward, so top > bottom.
    TL (TOPLEFT): y grows downward, so top < bottom.
    `top` is always given in the BL frame; the TL frame mirrors it on a 1000-point page.
    """
    if origin == "BL":
        return [left, top, left + width, top - height]
    return [left, 1000.0 - top, left + width, 1000.0 - top + height]


def make_cell(index, r0, r1, c0, c1, text, *, table=0, page=1, top=700.0, origin="BL"):
    left, t, right, bottom = box(10.0 * c0, top, origin, width=10.0 * (c1 - c0))
    return NormalizedCell(
        f"t{table}-c{index}", table, text, text, r0, r1, c0, c1, SourceBBox(page, left, t, right, bottom)
    )


def make_table(rows, cols, cells, table=0):
    return NormalizedTable(table, rows, cols, list(cells))


def evidence(tables, texts=()):
    return ProspectusEvidence(tables=list(tables), text_items=list(texts), source_kind="test")


def text_item(index, label, text, *, page=1, top=800.0, left=40.0, origin="BL"):
    return {
        "item_id": f"text-{index}",
        "label": label,
        "text": text,
        "page": page,
        "bbox": box(left, top, origin),
    }


def rows_of(html: str) -> list[str]:
    return re.findall(r"<tr>.*?</tr>", html)


def row_width(row: str) -> int:
    width = 0
    for tag in re.findall(r"<t[dh][^>]*>", row):
        span = re.search(r'colspan="(\d+)"', tag)
        width += int(span.group(1)) if span else 1
    return width


def banner_table():
    return make_table(
        4,
        4,
        [
            make_cell(0, 0, 1, 0, 4, "FIRST YEAR", top=700),
            make_cell(1, 1, 2, 0, 2, "FIRST SEMESTER", top=690),
            make_cell(2, 1, 2, 2, 4, "SECOND SEMESTER", top=690),
            make_cell(3, 2, 3, 0, 1, "Course Code", top=680),
            make_cell(4, 2, 3, 1, 2, "Course Title", top=680),
            make_cell(5, 2, 3, 2, 3, "Course Code", top=680),
            make_cell(6, 2, 3, 3, 4, "Course Title", top=680),
            make_cell(7, 3, 4, 0, 1, "CS 1", top=670),
            make_cell(8, 3, 4, 1, 2, "Discrete Structures 1", top=670),
            make_cell(9, 3, 4, 2, 3, "CS 2", top=670),
            make_cell(10, 3, 4, 3, 4, "Discrete Structures 2", top=670),
        ],
    )


def test_merged_banner_is_one_cell_with_its_real_span():
    html = render_prospectus_markup(evidence([banner_table()]), OK)
    assert html.count("FIRST YEAR") == 1
    assert '<th data-cell="t0-c0" data-page="1" colspan="4">FIRST YEAR</th>' in html


def test_both_semesters_share_one_row_and_headers_are_th():
    html = render_prospectus_markup(evidence([banner_table()]), OK)
    rows = rows_of(html)
    assert "FIRST SEMESTER" in rows[1] and "SECOND SEMESTER" in rows[1]
    assert '<th data-cell="t0-c1" data-page="1" colspan="2">FIRST SEMESTER</th>' in rows[1]
    assert all("<th " in cell for cell in re.findall(r"<t[dh] [^>]*>Course (?:Code|Title)", rows[2]))
    assert '<td data-cell="t0-c7" data-page="1">CS 1</td>' in rows[3]


def test_a_banner_word_inside_a_course_cell_stays_a_td():
    table = make_table(1, 2, [make_cell(0, 0, 1, 0, 2, "FIRST SEMESTER Discrete Structures 1 1")])
    # colspan 2 and a semester label would make it a banner; a one-column glued cell must not
    glued = make_table(1, 2, [make_cell(0, 0, 1, 0, 1, "FIRST SEMESTER Discrete Structures 1 1")])
    assert "<td " in render_prospectus_markup(evidence([glued]), OK)
    assert "<th " not in render_prospectus_markup(evidence([glued]), OK)
    assert "<th " in render_prospectus_markup(evidence([table]), OK)


def test_empty_grid_positions_become_gap_cells_and_columns_line_up():
    table = make_table(
        2,
        3,
        [
            make_cell(0, 0, 1, 0, 1, "A"),
            make_cell(1, 0, 1, 2, 3, "B"),
            make_cell(2, 1, 2, 0, 2, "C"),
        ],
    )
    html = render_prospectus_markup(evidence([table]), OK)
    assert html.count("<td data-gap></td>") == 2  # (0,1) and (1,2)
    assert [row_width(row) for row in rows_of(html)] == [3, 3]
    tags = re.findall(r"<td\b[^>]*>", html)
    assert tags and not any("data-cell" in tag and "data-gap" in tag for tag in tags)


def test_line_breaks_in_cell_text_become_br_and_never_split_the_table_block():
    original = "a\n\nb\nc & <d>"
    table = make_table(1, 2, [make_cell(0, 0, 1, 0, 1, original), make_cell(1, 0, 1, 1, 2, "next")])
    html = render_prospectus_markup(evidence([table]), OK)
    block = html[html.index("<table") : html.index("</table>")]
    assert "\n\n" not in block
    cell = re.search(r'<td data-cell="t0-c0"[^>]*>(.*?)</td>', block, re.S).group(1)
    assert "\n" not in cell and "<br>" in cell
    assert unescape(cell.replace("<br>", "\n")) == original


def test_rowspan_hides_the_covered_position_but_gaps_still_line_up():
    table = make_table(
        2,
        2,
        [make_cell(0, 0, 2, 0, 1, "A"), make_cell(1, 0, 1, 1, 2, "B")],
    )
    rows = rows_of(render_prospectus_markup(evidence([table]), OK))
    assert 'rowspan="2"' in rows[0]
    assert rows[1] == "<tr><td data-gap></td></tr>"


def test_cell_text_is_html_escaped_never_interpreted():
    table = make_table(1, 1, [make_cell(0, 0, 1, 0, 1, 'A & B <script>alert("x")</script>')])
    html = render_prospectus_markup(evidence([table]), OK)
    assert "<script>" not in html
    assert "A &amp; B &lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;" in html


def test_colliding_cell_is_listed_after_the_table_not_placed():
    table = make_table(
        1,
        3,
        [make_cell(0, 0, 1, 0, 2, "X"), make_cell(1, 0, 1, 1, 3, "Y")],
    )
    html = render_prospectus_markup(evidence([table]), OK)
    assert '<td data-cell="t0-c0"' in html
    assert 'data-cell="t0-c1"' not in html
    assert '<p data-unplaced-cell="t0-c1" data-page="1">Y</p>' in html
    assert html.index("</table>") < html.index("data-unplaced-cell")
    assert [row_width(row) for row in rows_of(html)] == [3]  # X spans 2, one gap, no Y


def test_every_cell_id_appears_exactly_once_for_the_cs_fixture():
    document = fixture_document(cs_fixture_grid(), [("text", "Effective SY 2025-2026")])
    html = render_prospectus_markup(document, OK)
    ids = re.findall(r'data-(?:unplaced-)?cell="([^"]+)"', html)
    assert sorted(ids) == sorted(document.all_cells())
    assert len(ids) == len(set(ids))
    assert re.search(r'<th data-cell="t0-c\d+" colspan="8">FIRST YEAR</th>', html)
    assert any("FIRST SEMESTER" in row and "SECOND SEMESTER" in row for row in rows_of(html))
