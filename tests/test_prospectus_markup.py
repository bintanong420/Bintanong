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


def first_line(markup: str) -> str:
    return markup.splitlines()[0]


def test_error_and_warn_audits_are_flagged_review_required_on_line_one():
    for status in ("error", "warn"):
        line = first_line(render_prospectus_markup(evidence([banner_table()]), {"audit": {"status": status}}))
        assert line == f"<!-- extraction_audit: {status} | REVIEW REQUIRED | pdf_sha256: not recorded -->"


def test_missing_audit_is_treated_as_review_required():
    line = first_line(render_prospectus_markup(evidence([banner_table()]), {}))
    assert line == "<!-- extraction_audit: unknown | REVIEW REQUIRED | pdf_sha256: not recorded -->"


def test_ok_audit_is_still_only_a_pending_candidate_and_shows_a_given_hash():
    digest = "ab" * 32
    line = first_line(render_prospectus_markup(evidence([banner_table()]), OK, pdf_sha256=digest))
    assert line == f"<!-- extraction_audit: ok | content_review: pending | pdf_sha256: {digest} -->"
    assert "REVIEW REQUIRED" not in line


def test_status_comment_cannot_be_broken_out_of():
    line = first_line(render_prospectus_markup(evidence([]), {"audit": {"status": "x --> <b>"}}))
    assert line.count("-->") == 1 and line.endswith("-->") and "<b>" not in line


@pytest.mark.parametrize("origin", ["BL", "TL"])
def test_blocks_follow_the_page_top_to_bottom_in_either_coordinate_frame(origin):
    table = make_table(
        2,
        2,
        [
            make_cell(0, 0, 1, 0, 1, "CS 1", top=700, origin=origin),
            make_cell(1, 1, 2, 0, 1, "CS 2", top=690, origin=origin),
        ],
    )
    texts = [  # deliberately scrambled
        text_item(3, "footnote", "CS Elect 4/La. Mathematical Methods", top=120, origin=origin),
        text_item(0, "section_header", "PROPOSED PROGRAM OF STUDY", top=800, origin=origin),
        text_item(4, "page_footer", "50", top=50, origin=origin),
        text_item(1, "text", "Effective SY 2025-2026", top=790, origin=origin),
    ]
    html = render_prospectus_markup(evidence([table], texts), OK)
    order = [
        html.index("PROPOSED PROGRAM OF STUDY"),
        html.index("Effective SY 2025-2026"),
        html.index("<table"),
        html.index("CS Elect 4/La."),
        html.index(">50<"),
    ]
    assert order == sorted(order)
    assert '<h2 data-item="text-0" data-label="section_header" data-page="1">PROPOSED PROGRAM OF STUDY</h2>' in html
    assert '<p data-item="text-3" data-label="footnote" data-page="1"><small>CS Elect 4/La. Mathematical Methods</small></p>' in html


def test_items_on_one_printed_line_read_left_to_right_despite_tiny_height_differences():
    right = text_item(0, "footnote", "RIGHT column", top=200.0, left=262.0)
    left = text_item(1, "footnote", "LEFT column", top=199.4, left=57.0)  # 0.6 pt lower, listed second
    html = render_prospectus_markup(evidence([], [right, left]), OK)
    assert html.index("LEFT column") < html.index("RIGHT column")


def test_each_text_item_appears_once_and_is_escaped():
    texts = [text_item(0, "text", "Name of Student: ____ & ID <No.>")]
    html = render_prospectus_markup(evidence([], texts), OK)
    assert html.count('data-item="text-0"') == 1
    assert "Name of Student: ____ &amp; ID &lt;No.&gt;" in html


def test_page_change_inserts_one_marker_and_the_first_page_gets_none():
    page2 = make_table(1, 1, [make_cell(0, 0, 1, 0, 1, "A", page=2)], table=0)
    page3 = make_table(1, 1, [make_cell(0, 0, 1, 0, 1, "B", page=3, table=1)], table=1)
    header = text_item(0, "section_header", "TITLE", page=2, top=800)
    html = render_prospectus_markup(evidence([page3, page2], [header]), OK)
    assert html.count("<!-- page 3 -->\n<hr>") == 1
    assert "<!-- page 2 -->" not in html
    assert html.index('data-table="0"') < html.index("<!-- page 3 -->") < html.index('data-table="1"')


def test_items_without_a_position_keep_input_order_texts_then_tables():
    document = fixture_document(cs_fixture_grid(), [("section_header", "PROGRAM OF STUDY"), ("text", "Effective SY")])
    html = render_prospectus_markup(document, OK)
    assert html.index("PROGRAM OF STUDY") < html.index("Effective SY") < html.index("<table")


def test_output_is_deterministic_and_independent_of_input_order():
    table = banner_table()
    texts = [text_item(0, "section_header", "TITLE", top=800), text_item(1, "footnote", "NOTE", top=100)]
    first = render_prospectus_markup(evidence([table], texts), ERROR)
    again = render_prospectus_markup(evidence([banner_table()], list(texts)), ERROR)
    shuffled = make_table(table.num_rows, table.num_cols, reversed(table.cells))
    reordered = render_prospectus_markup(evidence([shuffled], list(reversed(texts))), ERROR)
    assert first == again == reordered
    assert first.endswith("\n") and "\r" not in first


def test_non_ok_audit_gets_a_visible_warning_and_ok_does_not_claim_approval():
    flagged = render_prospectus_markup(evidence([banner_table()]), ERROR)
    assert "> **REVIEW REQUIRED**" in flagged
    calm = render_prospectus_markup(evidence([banner_table()]), OK)
    assert "REVIEW REQUIRED" not in calm
    assert "not an approved curriculum" in calm


def test_line_breaks_in_text_blocks_become_br():
    html = render_prospectus_markup(evidence([], [text_item(0, "text", "a\n\nb")]), OK)
    assert ">a<br><br>b</p>" in html


def real_cell(index, text, *, top, page=1, table=0, row=0):
    """A table cell as Docling records it: TOPLEFT origin, top < bottom."""
    bbox = SourceBBox(page, 50.0, top, 150.0, top + 12.0, origin="TOPLEFT")
    return NormalizedCell(f"t{table}-c{index}", table, text, text, row, row + 1, 0, 1, bbox)


def real_text(index, label, text, *, top, page=1):
    """A text item as Docling records it: BOTTOMLEFT origin, top > bottom."""
    return {
        "item_id": f"text-{index}",
        "label": label,
        "text": text,
        "page": page,
        "bbox": [46.0, top, 278.0, top - 11.0],
        "origin": "BOTTOMLEFT",
    }


def real_evidence(tables, texts, sizes):
    return ProspectusEvidence(tables=list(tables), text_items=list(texts), source_kind="test", page_sizes=sizes)


def test_mixed_frames_on_one_page_read_header_table_footnote():
    table = make_table(1, 1, [real_cell(0, "CS 101", top=157.0)])  # TOPLEFT, near the top
    texts = [
        real_text(2, "footnote", "CS Elect 4/La. footnote", top=120.0),  # BOTTOMLEFT, near the bottom
        real_text(1, "section_header", "PROPOSED PROGRAM OF STUDY", top=861.0),  # BOTTOMLEFT, near the top
    ]
    html = render_prospectus_markup(real_evidence([table], texts, {1: (612.0, 936.0)}), OK)
    order = [html.index("PROPOSED PROGRAM OF STUDY"), html.index("<table"), html.index("CS Elect 4/La.")]
    assert order == sorted(order)


def test_each_page_uses_its_own_height_and_pages_stay_in_order():
    p1_table = make_table(1, 1, [real_cell(0, "P1 row", top=157.0, page=1)], table=0)
    p2_table = make_table(1, 1, [real_cell(0, "P2 row", top=150.0, page=2, table=1)], table=1)
    texts = [
        real_text(0, "section_header", "P1 HEADER", top=861.0, page=1),
        real_text(1, "footnote", "P1 FOOTNOTE", top=120.0, page=1),
        # 500-point page: top=400 is 100 down, above the table at 150 (936 would put it at 536).
        real_text(2, "section_header", "P2 HEADER", top=400.0, page=2),
        real_text(3, "footnote", "P2 FOOTNOTE", top=40.0, page=2),
    ]
    html = render_prospectus_markup(
        real_evidence([p2_table, p1_table], texts, {1: (612.0, 936.0), 2: (612.0, 500.0)}), OK
    )
    order = [html.index(s) for s in ("P1 HEADER", "P1 row", "P1 FOOTNOTE", "P2 HEADER", "P2 row", "P2 FOOTNOTE")]
    assert order == sorted(order)


def test_loader_carries_origin_and_page_size_from_raw_docling_json():
    from backend.bintanong_tools.prospectus_extractor.loader import evidence_adapter

    raw = {
        "pages": {"1": {"size": {"width": 612.0, "height": 936.0}}},
        "texts": [
            {
                "label": "footnote",
                "text": "FOOT",
                "prov": [{"page_no": 1, "bbox": {"l": 46, "t": 120, "r": 278, "b": 109, "coord_origin": "BOTTOMLEFT"}}],
            }
        ],
        "tables": [
            {
                "prov": [{"page_no": 1}],
                "data": {
                    "num_rows": 1,
                    "num_cols": 1,
                    "table_cells": [
                        {
                            "text": "A",
                            "bbox": {"l": 50, "t": 157, "r": 150, "b": 169, "coord_origin": "TOPLEFT"},
                            "start_row_offset_idx": 0,
                            "end_row_offset_idx": 1,
                            "start_col_offset_idx": 0,
                            "end_col_offset_idx": 1,
                        }
                    ],
                },
            }
        ],
    }
    ev = evidence_adapter(raw)
    assert ev.page_sizes == {1: (612.0, 936.0)}
    assert ev.text_items[0]["origin"] == "BOTTOMLEFT"
    assert ev.tables[0].cells[0].bbox.origin == "TOPLEFT"


def test_unknown_page_height_falls_back_deterministically():
    table = make_table(1, 1, [real_cell(0, "CS 101", top=157.0)])
    # TOPLEFT text far below the table: the old frame guess put it after the table (top 700 > 157).
    low = {"item_id": "text-3", "label": "footnote", "text": "LOW", "page": 1,
           "bbox": [46.0, 700.0, 278.0, 711.0], "origin": "TOPLEFT"}
    texts = [real_text(1, "section_header", "HEADER", top=861.0), real_text(2, "footnote", "FOOT", top=120.0), low]
    first = render_prospectus_markup(real_evidence([table], texts, {}), OK)
    again = render_prospectus_markup(real_evidence([table], list(reversed(texts)), {}), OK)
    assert first == again
    assert all(s in first for s in ("HEADER", "<table", "FOOT"))
    # mixed origins and no page height: texts then tables, and the status line says so
    assert max(first.index(s) for s in ("HEADER", "FOOT", "LOW")) < first.index("<table")
    assert "reading_order: approximate (page 1: page size unknown)" in first.splitlines()[0]
    known = render_prospectus_markup(real_evidence([table], texts, {1: (612.0, 936.0)}), OK)
    assert "reading_order" not in known


def test_single_origin_without_page_height_is_not_flagged_approximate():
    texts = [real_text(1, "section_header", "HEADER", top=861.0), real_text(2, "footnote", "FOOT", top=120.0)]
    html = render_prospectus_markup(real_evidence([], texts, {}), OK)
    assert "reading_order" not in html.splitlines()[0]
    assert html.index("HEADER") < html.index("FOOT")


from backend.bintanong_tools.prospectus_extractor import batch, cli, pipeline  # noqa: E402


def _fake_run(tmp_path, monkeypatch, status="error", **flags):
    source = tmp_path / "x_docling.json"
    source.write_text("{}", encoding="utf-8")
    document = evidence(
        [banner_table()], [text_item(0, "section_header", "PROPOSED PROGRAM OF STUDY")]
    )
    from backend.bintanong_tools.prospectus_extractor.loader import DocumentLoadResult
    monkeypatch.setattr(pipeline, "load_document_result",
                        lambda *args, **kwargs: DocumentLoadResult(document, None, "not-applicable"))
    monkeypatch.setattr(pipeline, "build_payload", lambda *args, **kwargs: {"audit": {"status": status}})
    target = tmp_path / "out" / "x_prospectus.json"
    pipeline.process_prospectus(source, target, quiet=True, **flags)
    return target


def test_export_md_writes_the_twin_beside_the_json_even_when_the_audit_failed(tmp_path, monkeypatch):
    target = _fake_run(tmp_path, monkeypatch, status="error", export_md=True)
    twin = target.with_name("x_prospectus.md")
    text = twin.read_text(encoding="utf-8")
    assert text.splitlines()[0].startswith("<!-- extraction_audit: error | REVIEW REQUIRED |")
    assert "PROPOSED PROGRAM OF STUDY" in text and "\r" not in text


def test_md_is_not_written_by_default_and_a_stale_one_is_removed(tmp_path, monkeypatch):
    stale = tmp_path / "out" / "x_prospectus.md"
    stale.parent.mkdir()
    stale.write_text("old", encoding="utf-8")
    _fake_run(tmp_path, monkeypatch, status="ok")
    assert not stale.exists()


def _cli_flags(monkeypatch, tmp_path, *argv):
    seen: dict = {}
    monkeypatch.setattr(cli, "process_prospectus", lambda *a, **k: seen.update(k) or {"audit": {"status": "ok"}})
    source = tmp_path / "x_docling.json"
    source.write_text("{}", encoding="utf-8")
    assert cli.main(["-i", str(source), *argv]) == 0
    return seen


def test_cli_export_md_flag_and_export_all(monkeypatch, tmp_path):
    assert _cli_flags(monkeypatch, tmp_path)["export_md"] is False
    only = _cli_flags(monkeypatch, tmp_path, "--export-md")
    assert only["export_md"] is True and only["export_csv"] is False
    everything = _cli_flags(monkeypatch, tmp_path, "--export-all")
    assert everything["export_md"] and everything["export_csv"] and everything["export_pl"]


def test_cli_batch_receives_write_md(monkeypatch, tmp_path):
    seen = {}

    def fake_batch(config):
        seen["write_md"] = config.write_md
        return {"succeeded": 1, "audit_failed": 0, "skipped": 0, "failed": 0, "manifest_path": None}

    monkeypatch.setattr(cli, "run_batch", fake_batch)
    assert cli.main(["-i", str(tmp_path), "--batch", "--export-md"]) == 0
    assert seen["write_md"] is True
    assert cli.main(["-i", str(tmp_path), "--batch"]) == 0
    assert seen["write_md"] is False


def test_batch_defaults_to_writing_md_and_passes_it_on(monkeypatch, tmp_path):
    assert batch.BatchConfig().write_md is True
    source = tmp_path / "in"
    source.mkdir()
    (source / "a.pdf").write_bytes(b"%PDF-test")
    seen = []
    result = {
        "audit": {
            "status": "ok", "total_courses": 0, "computed_total_units": 0,
            "declared_total_units": None, "years_detected": [], "errors": [], "warnings": [],
        },
        "metadata": {},
    }
    monkeypatch.setattr(batch, "process_prospectus", lambda *a, **k: seen.append(k) or result)
    config = batch.BatchConfig(input_root=source, output_root=tmp_path / "out", write_manifest=False)
    batch.run_batch(config)
    assert seen[0]["export_md"] is True
    config.write_md = False
    batch.run_batch(config)
    assert seen[1]["export_md"] is False


# --- source fidelity: the twin shows Docling's own strings, not the parser's cleaned text ---

SOURCE = "A  B\nC\u2013D\u00a0E"


def test_cell_shows_the_original_docling_string_not_the_cleaned_one():
    cell = NormalizedCell("t0-c0", 0, SOURCE, "A B C-D E", 0, 1, 0, 1, SourceBBox(1, 0.0, 700.0, 10.0, 690.0))
    html = render_prospectus_markup(evidence([make_table(1, 1, [cell])]), OK)
    assert ">A  B<br>C\u2013D\u00a0E</td>" in html


def test_text_item_shows_the_original_docling_string():
    item = dict(text_item(0, "text", "A B C-D E"), raw_text=SOURCE)
    html = render_prospectus_markup(evidence([], [item]), OK)
    assert ">A  B<br>C\u2013D\u00a0E</p>" in html


def test_loader_keeps_original_text_beside_the_cleaned_text_for_cells_and_items():
    from backend.bintanong_tools.prospectus_extractor.loader import evidence_adapter

    raw = {
        "texts": [{"label": "text", "text": SOURCE, "prov": [{"page_no": 1, "bbox": {"l": 1, "t": 9, "r": 2, "b": 8}}]}],
        "tables": [{"prov": [{"page_no": 1}], "data": {"num_rows": 1, "num_cols": 1, "table_cells": [
            {"text": SOURCE, "start_row_offset_idx": 0, "end_row_offset_idx": 1,
             "start_col_offset_idx": 0, "end_col_offset_idx": 1}]}}],
    }
    ev = evidence_adapter(raw)
    assert ev.text_items[0]["text"] == "A B C-D E" and ev.text_items[0]["raw_text"] == SOURCE
    cell = ev.tables[0].cells[0]
    assert cell.text == "A B C-D E" and cell.raw_text == SOURCE

# --- cells never vanish; spans are never silently shortened; nothing unescaped ---


def test_cell_starting_outside_the_grid_is_listed_not_dropped():
    cells = [
        make_cell(0, 0, 1, 0, 1, "OK"),
        make_cell(1, -1, 0, 0, 1, "NEG ROW"),
        make_cell(2, 0, 1, -2, -1, "NEG COL"),
        make_cell(3, 5, 6, 0, 1, "BELOW"),
        make_cell(4, 0, 1, 7, 8, "RIGHT"),
    ]
    html = render_prospectus_markup(evidence([make_table(2, 2, cells)]), OK)
    ids = re.findall(r'data-(?:unplaced-)?cell="([^"]+)"', html)
    assert sorted(ids) == ["t0-c0", "t0-c1", "t0-c2", "t0-c3", "t0-c4"]
    for n in (1, 2, 3, 4):
        assert f'data-unplaced-cell="t0-c{n}"' in html


def test_span_beyond_the_grid_is_clamped_visibly_with_the_declared_spans():
    table = make_table(2, 3, [make_cell(0, 0, 4, 0, 5, "WIDE")])
    html = render_prospectus_markup(evidence([table]), OK)
    assert 'colspan="3" rowspan="2" data-span-clamped="4,5"' in html
    fine = render_prospectus_markup(evidence([make_table(1, 3, [make_cell(0, 0, 1, 0, 3, "F")])]), OK)
    assert "data-span-clamped" not in fine


def test_page_values_are_escaped_in_attributes_and_comments():
    bad = '1" onmouseover="x'
    a = dict(text_item(0, "text", "A"), page=bad, bbox=None)
    b = dict(text_item(1, "text", "B"), page="2 --> <b>", bbox=None)
    html = render_prospectus_markup(evidence([], [a, b]), OK)
    assert 'onmouseover="x' not in html and "<b>" not in html
    comment = re.search(r"<!-- page (.*?) -->\n<hr>", html).group(1)
    assert "-->" not in comment and "<" not in comment and "--" not in comment
