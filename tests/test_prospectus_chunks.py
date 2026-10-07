"""Source-linked candidate chunks; review estimates do not certify tokenizer lengths."""

from __future__ import annotations

import pytest
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

from backend.bintanong_tools.prospectus_extractor import chunking
from backend.bintanong_tools.prospectus_extractor import rag
from backend.bintanong_tools.prospectus_extractor.evidence import NormalizedCell, NormalizedTable, ProspectusEvidence, SourceBBox
from backend.bintanong_tools.prospectus_extractor.prerequisites import classify_prerequisite_state
from backend.bintanong_tools.prospectus_extractor.units import parse_units
from backend.bintanong_tools.prospectus_extractor.courses import parse_elective_tracks

PDF_A, PDF_B = "a" * 64, "b" * 64
LOCATOR = {"kind": "table_cells", "table_index": 0, "cell_ids": ["t0-c1"]}


def span(pdf=PDF_A, page=1, locator=None, text="x"):
    return chunking.make_span(pdf, page, locator or LOCATOR, text, None, "docling-json")


def test_chunk_identity_changes_with_edition_locator_content_and_version(monkeypatch):
    key = chunking.locator_key([span()])
    base = chunking.make_chunk_id(PDF_A, key, "h1")
    assert len(base) == 64 and base == chunking.make_chunk_id(PDF_A, key, "h1")
    assert base != chunking.make_chunk_id(PDF_B, key, "h1")
    assert base != chunking.make_chunk_id(PDF_A, chunking.locator_key([span(page=2)]), "h1")
    assert base != chunking.make_chunk_id(PDF_A, key, "h2")
    monkeypatch.setattr(chunking, "CHUNKER_VERSION", "palsu-chunker-next")
    assert base != chunking.make_chunk_id(PDF_A, key, "h1")


def test_missing_pdf_hash_is_salted():
    key = chunking.locator_key([span(pdf=None)])
    assert chunking.make_chunk_id(None, key, "h") != chunking.make_chunk_id(PDF_A, key, "h")


def test_locator_identity_ignores_order_dict_order_and_text():
    first, second = span(), span(page=2)
    assert chunking.locator_key([first, second]) == chunking.locator_key([second, first])
    assert chunking.locator_key([span(text="a")]) == chunking.locator_key([span(text="b")])
    reverse = dict(reversed(list(LOCATOR.items())))
    assert chunking.locator_key([span()]) == chunking.locator_key([span(locator=reverse)])


def test_content_identity_normalizes_line_endings_whitespace_and_unicode():
    assert chunking.content_hash("A  B", "C\r\nD") == chunking.content_hash("A B", "C D")
    assert chunking.content_hash("caf\u00e9", "x") == chunking.content_hash("cafe\u0301", "x")
    assert chunking.content_hash("A", "C") != chunking.content_hash("B", "C")


def test_estimate_review_budget_includes_reserve():
    assert chunking.estimate_tokens("word " * 100) == 180
    assert chunking.estimate_tokens("x" * 300) == 100
    assert chunking.fits_cap(480) and not chunking.fits_cap(481)


def test_pack_items_preserves_order_and_keeps_oversize_item_alone():
    items = [(f"line {n} " + "word " * 40, n) for n in range(10)]
    parts = chunking.pack_items("HEADER", items, limit=200)
    assert len(parts) > 1
    assert [m for _lines, members in parts for m in members] == list(range(10))
    assert all(chunking.estimate_tokens("\n".join(["HEADER", *lines])) <= 200 for lines, _ in parts)
    parts = chunking.pack_items("H", [("big " * 500, "a"), ("small", "b")], limit=100)
    assert [members for _lines, members in parts] == [["a"], ["b"]]


def cell(cid, text, page=1, row=0, col=0, origin="TOPLEFT", table=0):
    return {"cell_id": cid, "table_index": table, "text": text, "raw_text": text,
            "row_start": row, "row_end": row + 1, "col_start": col, "col_end": col + 1,
            "page": page, "bbox": [1.0, 2.0, 3.0, 4.0] if page else None,
            "bbox_origin": origin if page else None}


def test_cell_spans_preserve_all_pages_reading_order_and_known_origin():
    cells = [cell("t0-b", "B", page=2), cell("t0-a", "A", col=1), cell("t0-c", "C"), cell("t0-c", "C")]
    spans = chunking.spans_from_cells(cells, PDF_A, "docling-json")
    assert [s["page"] for s in spans] == [1, 2]
    assert spans[0]["text"] == "C | A"
    assert spans[0]["locator"]["cell_ids"] == ["t0-c", "t0-a"]
    assert spans[0]["bbox_origin"] == "TOPLEFT"


def test_incompatible_origins_and_unknown_pages_are_not_unioned():
    spans = chunking.spans_from_cells([
        cell("a", "A"), cell("b", "B", origin="BOTTOMLEFT"),
        cell("c", "C", page=None), cell("d", "D", origin=None)], None, "docling-json")
    assert len(spans) == 4
    assert any(s["page"] is None and s["bbox"] is None for s in spans)
    assert {s["bbox_origin"] for s in spans} == {"TOPLEFT", "BOTTOMLEFT", None}


def test_text_item_spans_preserve_source_locator_and_unknown_geometry():
    items = [{"item_id": "text-7", "text": "Printed", "page": 2, "bbox": None}]
    [s] = chunking.spans_from_text_items(items, ["text-7", "text-7"], None, "docling-json")
    assert s["locator"] == {"kind": "text_item", "item_ids": ["text-7"]}
    assert s["text"] == "Printed" and s["bbox_origin"] is None


def test_assembled_chunk_separates_source_text_and_summary_without_approval():
    chunk = chunking.assemble_chunk("course", {"section_path": ["Test"]}, "Summary", [span(text="Printed")],
                                    pdf_sha256=None, source="renamed.json")
    assert chunk["source_text"] == "Printed" and chunk["text"] == "Summary"
    assert chunk["content_review"] == "pending" and chunk["source_anchored"] is False
    assert chunk["pages"] == [1] and chunk["table_indexes"] == [0] and chunk["cell_ids"] == ["t0-c1"]
    other = chunking.assemble_chunk("course", {"section_path": ["Test"]}, "Summary", [span(text="Printed")],
                                    pdf_sha256=None, source="original.json")
    assert chunk["chunk_id"] == other["chunk_id"]


META = {"program_name": "BS Test", "degree": "BS Test", "college_code": "CT",
        "college_name": "College of Test", "campus": None, "effective_school_year": "2018-2019", "source_file": "t.pdf"}
LAYOUT = [{"table_index": 0, "column_groups": [{"index": 0, "code_idx": 0, "title_idx": 1, "unit_idx": 2, "prereq_idx": 3}]}]


def course(code="CS 101", title="Intro", prereq="", row=1, page=1, unit_raw="3"):
    cells = [cell(f"t0-r{row}-c0", code, row=row, page=page),
             cell(f"t0-r{row}-c1", title, row=row, col=1, page=page),
             cell(f"t0-r{row}-c2", unit_raw, row=row, col=2, page=page)]
    if prereq:
        cells.append(cell(f"t0-r{row}-c3", prereq, row=row, col=3, page=page))
    units = parse_units(unit_raw)
    c = {"course_code": code, "course_title": title, "title_raw": title,
         "year_level": "1st Year", "semester": "1st Semester", "units": units, "total_units": units["total"],
         "prerequisites_raw": prereq, "prerequisites": [prereq] if prereq.startswith("CS ") else [],
         "prerequisites_unresolved": [], "standing_requirements": [prereq] if "Standing" in prereq else [],
         "category": "Core / Major", "elective_group": None,
         "_source": {"table_index": 0, "column_group": 0, "row_index": row},
         "provenance": {"table_index": 0, "source_cell_ids": [c["cell_id"] for c in cells], "source_cells": cells,
                        "valid": True, "resolution_method": "deterministic", "repair_id": None}}
    c["prerequisite_state"] = classify_prerequisite_state(c)
    return c


def document_for(courses, items=()):
    cells = {}
    for c in courses:
        for s in c["provenance"]["source_cells"]:
            box = SourceBBox(s["page"], *(s["bbox"] or [None] * 4), s.get("bbox_origin"))
            cells[s["cell_id"]] = NormalizedCell(s["cell_id"], s["table_index"], s["raw_text"], s["text"],
                s["row_start"], s["row_end"], s["col_start"], s["col_end"], box)
    return ProspectusEvidence(tables=[NormalizedTable(0, 100, 4, list(cells.values()))],
                              text_items=list(items), source_kind="docling-json")


def build(courses, *, pdf=PDF_A, doc=None, tracks=(), layout=LAYOUT):
    rejected = []
    terms = [{"year_level": "1st Year", "semester": "1st Semester", "declared_units": None,
              "computed_units": sum(c["total_units"] or 0 for c in courses)}]
    chunks = rag.build_semantic_rag_chunks(META, courses, tracks, terms, pdf_sha256=pdf,
                document=doc or document_for(courses), layout=layout, rejected=rejected)
    return chunks, rejected


def of_type(chunks, kind):
    return [c for c in chunks if c["chunk_type"] == kind]


def test_course_chunk_preserves_identity_source_and_known_origin():
    c = course()
    doc = document_for([c])
    # The legacy provenance projection omits origin; the canonical evidence still knows it.
    for s in c["provenance"]["source_cells"]:
        s.pop("bbox_origin")
    chunks, rejected = build([c], doc=doc)
    [chunk] = of_type(chunks, "course")
    assert rejected == []
    assert chunk["pdf_sha256"] == PDF_A and chunk["source_anchored"]
    assert chunk["content_review"] == "pending" and "id" not in chunk
    assert chunk["pages"] == [1] and chunk["table_indexes"] == [0]
    assert chunk["source_text"] == "CS 101 | Intro | 3"
    assert chunk["source_spans"][0]["bbox_origin"] == "TOPLEFT"
    assert chunk["section_path"] == ["BS Test", "1st Year", "1st Semester"]
    assert "### Course" in chunk["text"] and "### Course" not in chunk["source_text"]
    assert {"units", "unlocks", "category"} <= set(chunk["derived_fields"])
    assert "program" in chunk["unsourced_fields"]
    assert "No downstream course depends on it" not in chunk["text"]


def test_course_edition_and_filename_independence(monkeypatch):
    [first] = of_type(build([course()])[0], "course")
    [second] = of_type(build([course()], pdf=PDF_B)[0], "course")
    assert first["chunk_id"] != second["chunk_id"] and first["content_hash"] == second["content_hash"]
    monkeypatch.setitem(META, "source_file", "renamed_docling.json")
    [again] = of_type(build([course()])[0], "course")
    assert first["chunk_id"] == again["chunk_id"]
    [unanchored] = of_type(build([course()], pdf=None)[0], "course")
    assert unanchored["pdf_sha256"] is None and not unanchored["source_anchored"]


def test_course_multiple_pages_and_origins_remain_separate():
    c = course()
    c["provenance"]["source_cells"][1].update(page=2, bbox_origin="BOTTOMLEFT")
    c["provenance"]["page"] = None
    [chunk] = of_type(build([c])[0], "course")
    assert chunk["pages"] == [1, 2] and "page" not in chunk
    assert {s["bbox_origin"] for s in chunk["source_spans"]} == {"TOPLEFT", "BOTTOMLEFT"}


def test_course_unknown_page_and_origin_stay_unknown():
    [chunk] = of_type(build([course(page=None)])[0], "course")
    assert chunk["pages"] == []
    assert all(s["page"] is None and s["bbox"] is None and s["bbox_origin"] is None for s in chunk["source_spans"])


@pytest.mark.parametrize("damage", ["empty", "missing", "extra", "text", "table", "row", "column", "malformed"])
def test_invalid_course_locators_are_rejected(damage):
    c = course(prereq="CS 100")
    doc = document_for([c])
    p = c["provenance"]
    if damage == "empty": p["source_cells"] = []
    if damage == "missing": p["source_cell_ids"].append("ghost")
    if damage == "extra": p["source_cells"].append(cell("ghost", "CS 100", col=3))
    if damage == "text": p["source_cells"][-1]["text"] = "CS 999"
    if damage == "table": p["source_cells"][-1]["table_index"] = 99
    if damage == "row": p["source_cells"][-1]["row_start"] = 99
    if damage == "column": p["source_cells"][-1]["col_start"] = 1
    if damage == "malformed": p["source_cells"][-1].pop("cell_id")
    chunks, rejected = build([c], doc=doc)
    assert of_type(chunks, "course") == []
    assert any(r["label"] == "CS 101" and r["reason"] == "no_valid_source_cells" for r in rejected)


@pytest.mark.parametrize("field,value,reason", [
    ("prerequisites_raw", "MATH 7", "prerequisite_not_in_source_text"),
    ("course_title", "Invented", "title_not_in_source_text"),
    ("course_code", "CS 999", "code_not_in_source_text"),
])
def test_course_field_assertions_need_their_own_source_cells(field, value, reason):
    c = course(title="MATH 7", prereq="CS 100")
    doc = document_for([c])
    c[field] = value
    chunks, rejected = build([c], doc=doc)
    assert of_type(chunks, "course") == []
    assert any(r["reason"] == reason for r in rejected)


def test_prerequisite_order_is_not_a_bag_of_words():
    c = course(prereq="CS 1 or CS 2")
    doc = document_for([c])
    c["prerequisites_raw"] = "CS 2 or CS 1"
    chunks, rejected = build([c], doc=doc)
    assert of_type(chunks, "course") == [] and rejected[0]["reason"] == "prerequisite_not_in_source_text"


def test_printed_units_need_the_unit_field_and_parse_consistency():
    c = course(title="Topic 3", unit_raw="")
    doc = document_for([c])
    c["units"] = parse_units("3")
    c["total_units"] = 3
    chunks, rejected = build([c], doc=doc)
    assert of_type(chunks, "course") == [] and rejected[0]["reason"] == "units_not_in_source_text"
    c = course()
    c["units"]["total"] = 99
    chunks, rejected = build([c])
    assert of_type(chunks, "course") == [] and rejected[0]["reason"] == "units_not_derivable_from_source"


def test_missing_canonical_evidence_or_layout_cannot_certify_source():
    for kwargs in ({"document": ProspectusEvidence()}, {"layout": []}):
        rejected = []
        chunks = rag.build_semantic_rag_chunks(META, [course()], [], [], rejected=rejected, **kwargs)
        assert of_type(chunks, "course") == [] and rejected


def test_oversize_course_is_rejected_and_omitted_from_aggregates():
    good, bad = course(), course("CS 999", title="word " * 600, row=2)
    chunks, rejected = build([good, bad])
    assert [c["course_code"] for c in of_type(chunks, "course")] == ["CS 101"]
    assert any(r["label"] == "CS 999" and r["reason"] == "over_token_cap" for r in rejected)
    assert all("CS 999" not in c["text"] for c in chunks)


def test_pipeline_passes_canonical_evidence_layout_and_source_kind():
    from backend.bintanong_tools.prospectus_extractor.pipeline import build_payload
    from backend.bintanong_tools.prospectus_extractor.selftest import CS_HEADER, _cs_row, _cs_semester_row, _merged, fixture_document
    doc = fixture_document([CS_HEADER, _merged("FIRST YEAR", 8), _cs_semester_row(),
        _cs_row(("CS 1", "First", "3", ""), ("CS 2", "Second", "3", "CS 1"))], [])
    doc.tables[0].cells = [replace(c, bbox=SourceBBox(2, 1, 2, 3, 4, "BOTTOMLEFT")) for c in doc.tables[0].cells]
    payload = build_payload(doc, Path("test.pdf"), semantic_doc_path=None)
    chunks = of_type(payload["rag"]["semantic_chunks"], "course")
    assert len(chunks) == 2
    assert all(c["source_spans"][0]["bbox_origin"] == "BOTTOMLEFT" for c in chunks)
    assert all(c["source_spans"][0]["extraction"]["source_kind"] == doc.source_kind for c in chunks)
    assert all(c["pdf_sha256"] is None for c in chunks)


def test_term_and_overview_keep_every_contributing_page_and_origin():
    chunks, rejected = build([course(), course("CS 102", row=2, page=2)])
    assert rejected == []
    for kind in ("term_schedule", "program_overview"):
        [c] = of_type(chunks, kind)
        assert c["pages"] == [1, 2] and "page" not in c
        assert {"t0-r1-c0", "t0-r2-c2"} <= set(c["cell_ids"])
        assert all(s["bbox_origin"] == "TOPLEFT" for s in c["source_spans"])
        assert c["content_review"] == "pending" and "id" not in c


def test_rejected_courses_are_omitted_from_all_aggregate_text_totals_and_spans():
    good, bad = course(), course("CS 999", prereq="CS 101", row=2)
    doc = document_for([good, bad])
    bad["provenance"]["valid"] = False
    chunks, rejected = build([good, bad], doc=doc)
    assert rejected[0]["label"] == "CS 999"
    for kind in ("term_schedule", "program_overview"):
        [c] = of_type(chunks, kind)
        assert c["omitted_course_codes"] == ["CS 999"]
        assert "CS 999" not in c["text"] and "6" not in c["text"]
        assert not set(bad["provenance"]["source_cell_ids"]) & set(c["cell_ids"])


def test_no_accepted_course_does_not_emit_course_aggregate():
    c = course()
    c["provenance"]["valid"] = False
    chunks, rejected = build([c])
    assert of_type(chunks, "term_schedule") == [] and of_type(chunks, "program_overview") == []
    assert any(r["reason"] == "no_accepted_courses" for r in rejected)


def test_summary_parts_repeat_header_keep_every_member_once_and_fit_review_budget():
    many = [course(f"CS {n}", title="Advanced Topic " + "word " * 12, row=n - 100) for n in range(100, 140)]
    chunks, rejected = build(many)
    parts = of_type(chunks, "term_schedule")
    assert rejected == [] and len(parts) > 1
    assert [p["part_index"] for p in parts] == list(range(1, len(parts) + 1))
    assert {p["part_count"] for p in parts} == {len(parts)}
    assert len({p["chunk_id"] for p in parts}) == len(parts)
    assert all(p["text"].startswith("### Term Schedule: BS Test - 1st Year, 1st Semester (part ") for p in parts)
    assert all(p["token_count"] <= 480 for p in parts)
    for n in range(100, 140):
        assert sum(f"**CS {n}**" in p["text"] for p in parts) == 1
        containing = next(p for p in parts if f"**CS {n}**" in p["text"])
        assert f"t0-r{n-100}-c0" in containing["cell_ids"]


def option_item(item_id="text-7", code="CS Elect 4/La", title="Machine Learning", page=2):
    return {"item_id": item_id, "label": "text", "text": f"{code}. {title}", "page": page, "bbox": None}


def test_elective_options_keep_item_id_and_legacy_unknown_id():
    [pool] = parse_elective_tracks([option_item()])
    assert pool["options"] == [{"course_code": "CS Elect 4/La", "course_title": "Machine Learning", "source_item_id": "text-7"}]
    [legacy] = parse_elective_tracks([("text", option_item()["text"])])
    assert legacy["options"][0]["source_item_id"] is None


def test_elective_pool_cites_every_option_and_accepted_slot():
    items = [option_item(), option_item("text-8", "CS Elect 4/Lb", "Data Mining", page=3)]
    tracks = parse_elective_tracks(items)
    tracks[0]["curriculum_slots"] = ["CS Elect 4/L"]
    slot = course("CS Elect 4/L", title="CS Elective 4")
    chunks, rejected = build([slot], tracks=tracks, doc=document_for([slot], items))
    assert rejected == []
    [pool] = of_type(chunks, "elective_pool")
    assert pool["pages"] == [1, 2, 3]
    assert {s["locator"]["kind"] for s in pool["source_spans"]} == {"table_cells", "text_item"}
    assert {i for s in pool["source_spans"] for i in s["locator"].get("item_ids", [])} == {"text-7", "text-8"}
    assert set(slot["provenance"]["source_cell_ids"]) <= set(pool["cell_ids"])


@pytest.mark.parametrize("damage", ["missing", "wrong_text", "wrong_title", "wrong_code"])
def test_elective_option_with_unsupported_assertion_is_omitted_even_if_another_has_source(damage):
    items = [option_item(), option_item("text-8", "CS Elect 4/Lb", "Data Mining")]
    tracks = parse_elective_tracks(items)
    bad = tracks[0]["options"][1]
    bad["source_item_id"] = "ghost" if damage == "missing" else "text-7" if damage == "wrong_text" else "text-8"
    if damage == "wrong_title": bad["course_title"] = "Invented"
    if damage == "wrong_code": bad["course_code"] = "CS Elect 9/Lb"
    c = course()
    chunks, rejected = build([c], tracks=tracks, doc=document_for([c], items))
    [pool] = of_type(chunks, "elective_pool")
    assert bad["course_code"] not in pool["text"]
    assert pool["omitted_option_codes"] == [bad["course_code"]]
    assert {i for s in pool["source_spans"] for i in s["locator"].get("item_ids", [])} == {"text-7"}
    assert any(r["chunk_type"] == "elective_option" for r in rejected)


def test_elective_slot_without_accepted_course_is_not_asserted_or_cited():
    good, bad = course(), course("CS Elect 4/L", row=2)
    items = [option_item()]
    doc = document_for([good, bad], items)
    bad["provenance"]["valid"] = False
    tracks = parse_elective_tracks(items)
    tracks[0]["curriculum_slots"] = ["CS Elect 4/L", "missing slot"]
    chunks, rejected = build([good, bad], doc=doc, tracks=tracks)
    [pool] = of_type(chunks, "elective_pool")
    assert "CS Elect 4/L," not in pool["text"] and "missing slot" not in pool["text"]
    assert pool["omitted_course_codes"] == ["CS Elect 4/L", "missing slot"]
    assert pool["cell_ids"] == [] and pool["pages"] == [2]


def test_elective_pool_with_no_valid_text_item_is_rejected():
    track = {"group": "CS Elective 9", "options": [{"course_code": "CS Elect 9/La", "course_title": "X"}], "curriculum_slots": []}
    chunks, rejected = build([course()], tracks=[track])
    assert of_type(chunks, "elective_pool") == []
    assert any(r["chunk_type"] == "elective_pool" and r["reason"] == "no_source_text_items" for r in rejected)


def test_policy_spans_include_only_accepted_standing_courses():
    plain, gated, bad = course(), course("CS 401", prereq="4th Year Standing", row=2, page=2), course("CS 999", prereq="4th Year Standing", row=3)
    doc = document_for([plain, gated, bad])
    bad["provenance"]["valid"] = False
    chunks, rejected = build([plain, gated, bad], doc=doc)
    [policy] = of_type(chunks, "enrolment_policy")
    assert policy["pages"] == [2]
    assert set(policy["cell_ids"]) == set(gated["provenance"]["source_cell_ids"])
    assert "CS 999" not in policy["text"] and policy["omitted_course_codes"] == ["CS 999"]


def test_duplicate_course_chunk_identity_is_not_emitted_twice():
    chunks, _ = build([course(), course()])
    ids = [c["chunk_id"] for c in chunks]
    assert len(set(ids)) == len(ids)


def test_summary_ids_do_not_depend_on_course_dictionary_order_or_line_endings():
    c = course()
    first, _ = build([c])
    c = dict(reversed(list(c.items())))
    c["provenance"]["source_cells"][1]["text"] += "\r\n"
    second, _ = build([c])
    assert {p["chunk_id"] for p in first} == {p["chunk_id"] for p in second}


def test_native_bottomleft_union_preserves_top_and_bottom():
    a, b = cell("a", "A", origin="BOTTOMLEFT"), cell("b", "B", origin="BOTTOMLEFT")
    a["bbox"], b["bbox"] = [1, 20, 3, 10], [2, 40, 4, 30]
    [s] = chunking.spans_from_cells([a, b], PDF_A, "docling-json")
    assert s["bbox"] == [1, 40, 4, 10] and s["bbox_origin"] == "BOTTOMLEFT"


def test_unrecorded_origin_does_not_infer_union_direction():
    a, b = cell("a", "A", origin=None), cell("b", "B", origin=None)
    a["bbox"], b["bbox"] = [1, 20, 3, 10], [2, 40, 4, 30]
    spans = chunking.spans_from_cells([a, b], None, "docling-json")
    assert len(spans) == 2
    assert [s["bbox"] for s in spans] == [[1, 20, 3, 10], [2, 40, 4, 30]]
    assert all(s["bbox_origin"] is None for s in spans)


def test_elective_text_item_preserves_actual_canonical_origin_key():
    item = option_item()
    item.update(origin="BOTTOMLEFT", bbox=[1, 20, 3, 10])
    c = course()
    chunks, _ = build([c], tracks=parse_elective_tracks([item]), doc=document_for([c], [item]))
    [pool] = of_type(chunks, "elective_pool")
    [s] = pool["source_spans"]
    assert s["bbox_origin"] == "BOTTOMLEFT" and s["bbox"] == [1, 20, 3, 10]


def test_prerequisite_in_another_rows_prerequisite_cell_is_not_own_evidence():
    c = course(prereq="CS 100")
    actual = c["provenance"]["source_cells"][-1]
    actual.update(row_start=7, row_end=8)
    rejected = []
    chunks = rag.build_semantic_rag_chunks(META, [c], [], [], document=document_for([c]),
                            layout=LAYOUT, evidence_ids=[actual["cell_id"]], rejected=rejected)
    assert of_type(chunks, "course") == [] and rejected[0]["reason"] == "prerequisite_not_in_source_text"


@pytest.mark.parametrize("code,source_code", [("CS 10", "CS 101"), ("CS 1", "CS 10")])
def test_code_substring_is_not_source_confirmation(code, source_code):
    c = course(source_code)
    doc = document_for([c])
    c["course_code"] = code
    chunks, rejected = build([c], doc=doc)
    assert of_type(chunks, "course") == [] and rejected[0]["reason"] == "code_not_in_source_text"


def test_unit_digit_substring_does_not_confirm_different_printed_units():
    c = course(unit_raw="13")
    doc = document_for([c])
    c["units"], c["total_units"] = parse_units("3"), 3
    chunks, rejected = build([c], doc=doc)
    assert of_type(chunks, "course") == [] and rejected[0]["reason"] == "units_not_in_source_text"


def test_source_row_must_resolve_the_course_code():
    c = course()
    c["_source"]["row_index"] = 99
    chunks, rejected = build([c])
    assert of_type(chunks, "course") == [] and rejected[0]["reason"] == "no_valid_source_cells"


@pytest.mark.parametrize("ids", ["t0-r1-c0", [{"id": "t0-r1-c0"}], [None]])
def test_malformed_source_id_lists_are_rejected_without_crashing(ids):
    c = course()
    c["provenance"]["source_cell_ids"] = ids
    chunks, rejected = build([c])
    assert of_type(chunks, "course") == [] and rejected[0]["reason"] == "no_valid_source_cells"


@pytest.mark.parametrize("damage,reason", [
    ("code_suffix", "code_not_in_source_text"),
    ("title_subphrase", "title_not_in_source_text"),
    ("prerequisite_subphrase", "prerequisite_not_in_source_text"),
    ("unit_fraction_prefix", "units_not_in_source_text"),
    ("other_course_row", "prerequisite_not_in_source_text"),
])
def test_complete_own_field_required_for_course_admission(damage, reason):
    c = course("CS 101/L" if damage == "code_suffix" else "CS 101",
               title="Introduction to Computer Science" if damage == "title_subphrase" else "Intro",
               prereq="CS 100 and MATH 1" if damage == "prerequisite_subphrase" else "CS 100",
               unit_raw="3/2" if damage == "unit_fraction_prefix" else "3")
    other = course("CS 777", prereq="CS 100", row=7)
    doc = document_for([c, other])
    if damage == "code_suffix": c["course_code"] = "CS 101"
    if damage == "title_subphrase": c["course_title"] = "Computer Science"
    if damage == "prerequisite_subphrase": c["prerequisites_raw"] = "CS 100"
    if damage == "unit_fraction_prefix": c["units"], c["total_units"] = parse_units("3"), 3
    if damage == "other_course_row":
        own = c["provenance"]["source_cells"].pop()
        c["provenance"]["source_cell_ids"].remove(own["cell_id"])
        foreign = other["provenance"]["source_cells"][-1]
        c["provenance"]["source_cells"].append(foreign)
        c["provenance"]["source_cell_ids"].append(foreign["cell_id"])
    chunks, rejected = build([c], doc=doc)
    assert of_type(chunks, "course") == []
    assert (rejected[0]["chunk_type"], rejected[0]["label"], rejected[0]["reason"]) == ("course", c["course_code"], reason)
    assert of_type(chunks, "term_schedule") == [] and of_type(chunks, "program_overview") == []


@pytest.mark.parametrize("control", ["complete_fields", "normalized_code", "canonical_spanning_cells"])
def test_complete_own_field_and_existing_normalization_controls_remain_accepted(control):
    c = course("CS 101/L", title="Introduction to Computer Science", prereq="CS 100 and MATH 1", unit_raw="3/2")
    if control == "canonical_spanning_cells":
        for s in c["provenance"]["source_cells"]:
            s.update(row_start=0, row_end=3)
    doc = document_for([c])
    if control == "normalized_code": c["course_code"] = "CS101/L"
    chunks, rejected = build([c], doc=doc)
    assert rejected == []
    [chunk] = of_type(chunks, "course")
    assert "Introduction to Computer Science" in chunk["text"]
    assert "5 total (lecture 3, laboratory 2)" in chunk["text"]
    assert "CS 100 and MATH 1" in chunk["source_text"]
    assert set(chunk["cell_ids"]) == set(c["provenance"]["source_cell_ids"])


@pytest.mark.parametrize("field,reason", [
    ("prerequisites_raw", "prerequisite_not_in_source_text"),
    ("course_code", "code_not_in_source_text"),
    ("course_title", "title_not_in_source_text"),
])
def test_blank_claim_cannot_erase_complete_printed_own_field(field, reason):
    c = course(prereq="CS 100")
    doc = document_for([c])
    c[field] = ""
    if field == "prerequisites_raw":
        c.update(prerequisites=[], prerequisite_state="blank_unreviewed")
    chunks, rejected = build([c], doc=doc)
    assert of_type(chunks, "course") == []
    assert (rejected[0]["chunk_type"], rejected[0]["label"], rejected[0]["reason"]) == ("course", c["course_code"], reason)


@pytest.mark.parametrize("missing_cell", [False, True])
def test_genuinely_blank_or_missing_own_prerequisite_remains_unreviewed(missing_cell):
    c = course()
    if not missing_cell:
        blank = cell("t0-r1-c3", "", row=1, col=3)
        c["provenance"]["source_cells"].append(blank)
        c["provenance"]["source_cell_ids"].append(blank["cell_id"])
    chunks, rejected = build([c])
    assert rejected == []
    [chunk] = of_type(chunks, "course")
    assert "- **Prerequisites**: not recorded in the prospectus (unreviewed)" in chunk["text"]
    assert chunk["prerequisite_state"] == "blank_unreviewed"


# ---- rejection reporting (Standards F1 and the follow-up suspicions) ----

def test_rejected_course_record_names_code_term_reason_and_claimed_source_ids():
    c = course(prereq="CS 100")
    doc = document_for([c])
    c["course_title"] = "Invented"
    chunks, rejected = build([c], doc=doc)
    course_record = next(r for r in rejected if r["chunk_type"] == "course")
    assert course_record == {
        "chunk_type": "course", "label": "CS 101", "reason": "title_not_in_source_text",
        "course_code": "CS 101", "year_level": "1st Year", "semester": "1st Semester",
        "source_cell_ids": c["provenance"]["source_cell_ids"], "source_item_ids": []}
    term_record = next(r for r in rejected if r["chunk_type"] == "term_schedule")
    assert term_record["reason"] == "no_accepted_courses"
    assert (term_record["year_level"], term_record["semester"]) == ("1st Year", "1st Semester")
    assert term_record["source_cell_ids"] == c["provenance"]["source_cell_ids"]
    overview = next(r for r in rejected if r["chunk_type"] == "program_overview")
    assert overview["source_cell_ids"] == c["provenance"]["source_cell_ids"]


def test_rejected_elective_option_record_names_its_text_item():
    items = [option_item(), option_item("text-8", "CS Elect 4/Lb", "Data Mining")]
    tracks = parse_elective_tracks(items)
    tracks[0]["options"][1]["course_title"] = "Invented"
    c = course()
    _chunks, rejected = build([c], tracks=tracks, doc=document_for([c], items))
    [record] = [r for r in rejected if r["chunk_type"] == "elective_option"]
    assert record["course_code"] == "CS Elect 4/Lb" and record["reason"] == "option_not_in_source_text"
    assert record["source_item_ids"] == ["text-8"] and record["source_cell_ids"] == []


def test_over_cap_rejection_keeps_its_token_count_and_record_shape():
    _chunks, rejected = build([course(), course("CS 999", title="word " * 600, row=2)])
    [record] = [r for r in rejected if r["reason"] == "over_token_cap"]
    assert record["course_code"] == "CS 999" and record["token_count"] > 480
    assert record["source_cell_ids"] and set(record) >= {"year_level", "semester", "source_item_ids"}


def test_same_code_twin_does_not_flag_the_accepted_course_as_omitted():
    good, bad = course(), course(row=2)
    doc = document_for([good, bad])
    bad["course_title"] = "Invented"
    chunks, rejected = build([good, bad], doc=doc)
    [term] = of_type(chunks, "term_schedule")
    assert [c["course_code"] for c in of_type(chunks, "course")] == ["CS 101"]
    assert "**CS 101**" in term["text"] and term["omitted_course_codes"] == ["CS 101"]
    assert len([r for r in rejected if r["chunk_type"] == "course"]) == 1


def test_duplicate_course_chunk_is_recorded_as_a_rejection_not_dropped_silently():
    _chunks, rejected = build([course(), course()])
    [record] = [r for r in rejected if r["chunk_type"] == "course"]
    assert record["reason"] == "duplicate_chunk_id" and record["course_code"] == "CS 101"


def test_duplicate_summary_chunk_is_recorded_as_a_rejection():
    items = [option_item()]
    tracks = parse_elective_tracks(items) * 2
    c = course()
    chunks, rejected = build([c], tracks=tracks, doc=document_for([c], items))
    assert len(of_type(chunks, "elective_pool")) == 1
    assert [r["reason"] for r in rejected if r["chunk_type"] == "elective_pool"] == ["duplicate_chunk_id"]


@pytest.mark.parametrize("key,value", [("source_cells", 5), ("source_cells", "ab"), ("source_cells", {"a": 1}),
                                       ("source_cell_ids", 5)])
def test_non_list_source_fields_reject_instead_of_raising(key, value):
    c = course()
    doc = document_for([c])
    c["provenance"][key] = value
    chunks, rejected = build([c], doc=doc)
    assert of_type(chunks, "course") == [] and rejected[0]["reason"] == "no_valid_source_cells"


def test_non_mapping_provenance_rejects_instead_of_raising():
    c = course()
    doc = document_for([c])
    c["provenance"] = "not a mapping"
    chunks, rejected = build([c], doc=doc)
    assert of_type(chunks, "course") == [] and rejected[0]["reason"] == "no_valid_source_cells"
    assert rejected[0]["source_cell_ids"] == []


def _synthetic_payload(title="FIRST Second", **kwargs):
    from backend.bintanong_tools.prospectus_extractor.pipeline import build_payload
    from backend.bintanong_tools.prospectus_extractor.selftest import CS_HEADER, _cs_row, _cs_semester_row, _merged, fixture_document
    doc = fixture_document([CS_HEADER, _merged("FIRST YEAR", 8), _cs_semester_row(),
        _cs_row(("CS 1", "First", "3", ""), ("CS 2", title, "3", "CS 1"))], [])
    return build_payload(doc, Path("test.pdf"), semantic_doc_path=None, **kwargs)


def test_payload_reports_every_rejected_course_and_term_with_reason():
    payload = _synthetic_payload()
    assert payload["audit"]["status"] != "error"
    rejected = payload["rag"]["rejected_chunks"]
    assert [(r["chunk_type"], r["label"], r["reason"]) for r in rejected] == [
        ("course", "CS 2", "title_not_in_source_text"),
        ("term_schedule", "1st Year 2nd Semester", "no_accepted_courses")]
    assert rejected[0]["source_cell_ids"] and rejected[1]["source_cell_ids"] == rejected[0]["source_cell_ids"]
    assert payload["quality_report"]["total_rejected_chunks"] == 2
    assert [c["course_code"] for c in of_type(payload["rag"]["semantic_chunks"], "course")] == ["CS 1"]


def test_payload_with_nothing_rejected_reports_an_empty_list():
    payload = _synthetic_payload(title="Second")
    assert payload["rag"]["rejected_chunks"] == [] and payload["quality_report"]["total_rejected_chunks"] == 0


def test_blocked_audit_reports_no_chunks_and_no_rejections():
    from backend.bintanong_tools.prospectus_extractor.pipeline import build_payload
    from backend.bintanong_tools.prospectus_extractor.selftest import BSA_TEXT_ITEMS, bsa_fixture_grid, fixture_document
    payload = build_payload(fixture_document(bsa_fixture_grid(), BSA_TEXT_ITEMS), Path("bsa.pdf"), semantic_doc_path=None)
    assert payload["audit"]["status"] == "error"
    assert payload["rag"]["semantic_chunks"] == [] and payload["rag"]["rejected_chunks"] == []


# ---- pinned behaviour found unguarded by the Standards mutation review (F2) ----

def test_chunk_identity_known_answers():
    assert chunking.make_chunk_id(PDF_A, "café locator", "déjà") == \
        "e6d473bc982677898739c6afc83261f1f56ecd614045b2889ec70782b8f9f7d4"
    assert chunking.make_chunk_id(None, "loc", "dig") == \
        "92bfbb0c2b6f80ec64869925a3c4057b59ac18a3f0f33663bfc83e51d3396149"
    assert chunking.content_hash("Café  x", "y") == \
        "7f1cddca2a35d088bd30feb3568eccbc9eac4706bded7960261723407531ee4b"


def test_review_budget_constants_and_method_name_are_pinned():
    assert (chunking.TOKEN_COUNT_METHOD, chunking.TOKEN_HARD_CAP, chunking.TOKEN_RESERVE,
            chunking.TOKEN_SPLIT_AT, chunking.PART_LABEL_ROOM) == ("estimate-v1", 512, 32, 400, 32)
    chunk = chunking.assemble_chunk("course", {}, "Summary", [span()], pdf_sha256=PDF_A, source="t.pdf")
    assert chunk["token_count_method"] == "estimate-v1" and chunk["chunker_version"] == "palsu-chunker-v1"


def test_assemble_chunk_refuses_an_empty_span_set():
    with pytest.raises(ValueError):
        chunking.assemble_chunk("course", {}, "Summary", [], pdf_sha256=PDF_A, source="t.pdf")


def test_summary_split_leaves_room_for_the_part_label():
    many = [course(f"CS {n}", title="Advanced Topic " + "word " * 12, row=n - 100) for n in range(100, 140)]
    parts = of_type(build(many)[0], "term_schedule")
    assert len(parts) == 8
    assert max(p["token_count"] for p in parts) <= chunking.TOKEN_SPLIT_AT - chunking.PART_LABEL_ROOM


def test_summary_over_the_review_cap_is_rejected_with_its_token_count():
    items = [option_item(title="word " * 600)]
    c = course()
    chunks, rejected = build([c], tracks=parse_elective_tracks(items), doc=document_for([c], items))
    assert of_type(chunks, "elective_pool") == []
    [record] = [r for r in rejected if r["chunk_type"] == "elective_pool"]
    assert record["reason"] == "over_token_cap" and record["token_count"] > 480
    assert record["source_item_ids"] == ["text-7"]


@pytest.mark.parametrize("damage", ["total_units", "units_total", "units_lecture", "units_lab"])
def test_each_numeric_unit_must_match_the_printed_unit_field(damage):
    c = course(unit_raw="3/2")
    doc = document_for([c])
    if damage == "total_units": c["total_units"] = 99
    if damage == "units_total": c["units"]["total"] = 99
    if damage == "units_lecture": c["units"]["lecture"] = 1
    if damage == "units_lab": c["units"]["lab"] = 1
    chunks, rejected = build([c], doc=doc)
    assert of_type(chunks, "course") == [] and rejected[0]["reason"] == "units_not_derivable_from_source"


@pytest.mark.parametrize("field,printed,claim,reason", [
    ("course_title", "Data Base", "Database", "title_not_in_source_text"),
    ("prerequisites_raw", "CS 100", "CS100", "prerequisite_not_in_source_text"),
])
def test_only_the_code_may_match_loosely(field, printed, claim, reason):
    c = course(title=printed if field == "course_title" else "Intro", prereq=printed if field == "prerequisites_raw" else "")
    doc = document_for([c])
    c[field] = claim
    chunks, rejected = build([c], doc=doc)
    assert of_type(chunks, "course") == [] and rejected[0]["reason"] == reason


@pytest.mark.parametrize("field,reason", [("course_code", "code_not_in_source_text"),
                                          ("course_title", "title_not_in_source_text")])
def test_blank_claim_does_not_match_a_blank_printed_cell(field, reason):
    c = course(code="" if field == "course_code" else "CS 101", title="" if field == "course_title" else "Intro")
    chunks, rejected = build([c])
    assert of_type(chunks, "course") == [] and rejected[0]["reason"] == reason


@pytest.mark.parametrize("row_index", [None, "1", 1.0])
def test_non_integer_or_missing_source_row_is_rejected(row_index):
    c = course()
    c["_source"]["row_index"] = row_index
    chunks, rejected = build([c])
    assert of_type(chunks, "course") == [] and rejected[0]["reason"] == "no_valid_source_cells"
    del c["_source"]["row_index"]
    chunks, rejected = build([c])
    assert of_type(chunks, "course") == [] and rejected[0]["reason"] == "no_valid_source_cells"


def test_a_cell_from_another_table_is_not_own_evidence():
    c = course(prereq="CS 100")
    foreign = cell("t1-r1-c3", "CS 100", row=1, col=3, table=1)
    p = c["provenance"]
    p["source_cells"][-1] = foreign
    p["source_cell_ids"][-1] = foreign["cell_id"]
    chunks, rejected = build([c])
    assert of_type(chunks, "course") == [] and rejected[0]["reason"] == "prerequisite_not_in_source_text"


@pytest.mark.parametrize("claim,accepted", [("Intro to CS", True), ("to CS Intro", False)])
def test_multi_cell_field_text_is_read_in_row_then_column_then_id_order(claim, accepted):
    c = course(title="Intro to CS")
    later, earlier = cell("t0-r1-cb", "to CS", row=1, col=1), cell("t0-r1-ca", "Intro", row=0, col=1)
    earlier["row_end"] = 3
    p = c["provenance"]
    p["source_cells"][1:2] = [later, earlier]  # provenance order is the reverse of reading order
    p["source_cell_ids"][1:2] = ["t0-r1-cb", "t0-r1-ca"]
    c["course_title"] = claim
    chunks, rejected = build([c])
    assert bool(of_type(chunks, "course")) is accepted
    assert accepted or rejected[0]["reason"] == "title_not_in_source_text"


# ---- Task 5: layout chunks get IDs, pages and a token check ----

def _layout_document(text_items=(), docling_document=None):
    return ProspectusEvidence(
        text_items=list(text_items), docling_document=docling_document, source_kind="docling-json")


def _docling(monkeypatch, *chunks):
    fake = SimpleNamespace(chunk=lambda doc: list(chunks))
    monkeypatch.setattr(rag, "load_docling", lambda: {"HierarchicalChunker": lambda: fake})


def test_fallback_layout_chunks_are_hash_bound_and_capped():
    document = _layout_document([
        {"item_id": "text-0", "label": "title", "text": "BS TEST CURRICULUM", "page": 1, "bbox": None},
        {"item_id": "text-1", "label": "text", "text": "word " * 700, "page": 1, "bbox": None},
    ])
    rejected = []
    chunks = rag.build_hierarchical_rag_chunks(document, "t.pdf", pdf_sha256=PDF_A, rejected=rejected)
    assert [c["chunk_type"] for c in chunks] == ["hierarchical_layout_fallback"]
    assert chunks[0]["pdf_sha256"] == PDF_A and chunks[0]["content_review"] == "pending"
    assert chunks[0]["source_text"] == "BS TEST CURRICULUM" and chunks[0]["pages"] == [1]
    assert chunks[0]["source_spans"][0]["locator"] == {"kind": "text_item", "item_ids": ["text-0"]}
    again = rag.build_hierarchical_rag_chunks(document, "t.pdf", pdf_sha256=PDF_B, rejected=[])
    assert again[0]["chunk_id"] != chunks[0]["chunk_id"] and "id" not in chunks[0]
    assert [(r["label"], r["reason"], r["source_item_ids"]) for r in rejected] == [
        ("layout_fallback:1", "over_token_cap", ["text-1"])]


def test_docling_layout_chunks_carry_their_pages(monkeypatch):
    meta = SimpleNamespace(model_dump=lambda mode="json": {
        "headings": ["FIRST YEAR"],
        "doc_items": [{"self_ref": "#/texts/2", "prov": [{"page_no": 2}]}],
    })
    _docling(monkeypatch, SimpleNamespace(text="Effective SY 2018-2019", meta=meta))
    chunks = rag.build_hierarchical_rag_chunks(
        _layout_document(docling_document=object()), "t.pdf", pdf_sha256=PDF_A, rejected=[])
    assert [c["chunk_type"] for c in chunks] == ["hierarchical_layout"]
    assert chunks[0]["pages"] == [2] and chunks[0]["section_path"] == ["FIRST YEAR"]
    assert chunks[0]["source_spans"][0]["locator"] == {"kind": "docling_ref", "ref": "#/texts/2"}
    assert chunks[0]["source_text"] == "Effective SY 2018-2019" == chunks[0]["text"]
    assert chunks[0]["pdf_sha256"] == PDF_A and chunks[0]["token_count_method"] == "estimate-v1"


def test_all_oversized_docling_chunks_do_not_fall_back_to_the_text_path(monkeypatch):
    _docling(monkeypatch, SimpleNamespace(text="word " * 700, meta=None))
    rejected = []
    chunks = rag.build_hierarchical_rag_chunks(
        _layout_document([{"item_id": "t", "label": "text", "text": "kept?", "page": 1, "bbox": None}],
                         docling_document=object()),
        "t.pdf", pdf_sha256=PDF_A, rejected=rejected)
    assert chunks == [] and [r["reason"] for r in rejected] == ["over_token_cap"]
    assert rejected[0]["chunk_type"] == "hierarchical_layout" and rejected[0]["token_count"] > 480


def test_docling_chunk_without_source_refs_is_rejected_not_invented(monkeypatch):
    meta = SimpleNamespace(model_dump=lambda mode="json": {"headings": [], "doc_items": []})
    _docling(monkeypatch, SimpleNamespace(text="No provenance", meta=meta),
             SimpleNamespace(text="Located", meta=SimpleNamespace(model_dump=lambda mode="json": {
                 "headings": [], "doc_items": [{"self_ref": "#/texts/0", "prov": []}]})))
    rejected = []
    chunks = rag.build_hierarchical_rag_chunks(
        _layout_document(docling_document=object()), "t.pdf", pdf_sha256=PDF_A, rejected=rejected)
    assert [c["text"] for c in chunks] == ["Located"]
    assert chunks[0]["pages"] == [] and chunks[0]["source_spans"][0]["page"] is None
    assert [(r["label"], r["reason"]) for r in rejected] == [("docling_hierarchical:0", "no_source_spans")]


def test_fallback_text_without_an_item_id_is_rejected_and_blank_text_is_skipped():
    document = _layout_document([
        ("text", "legacy tuple item"), {"item_id": "text-1", "label": "text", "text": "   ", "page": 1},
        {"item_id": "text-2", "label": "text", "text": "Located", "page": None, "bbox": None}])
    rejected = []
    chunks = rag.build_hierarchical_rag_chunks(document, "t.pdf", pdf_sha256=None, rejected=rejected)
    assert [c["text"] for c in chunks] == ["Located"] and chunks[0]["source_anchored"] is False
    assert chunks[0]["chunk_index"] == 2
    assert [(r["label"], r["reason"]) for r in rejected] == [("layout_fallback:0", "no_source_spans")]


def test_docling_failure_falls_back_to_the_labelled_text_path(monkeypatch):
    def boom():
        raise RuntimeError("no docling")
    monkeypatch.setattr(rag, "load_docling", boom)
    document = _layout_document([{"item_id": "text-0", "label": "text", "text": "Plain", "page": 1}],
                                docling_document=object())
    chunks = rag.build_hierarchical_rag_chunks(document, "t.pdf", pdf_sha256=PDF_A, rejected=[])
    assert [c["chunk_type"] for c in chunks] == ["hierarchical_layout_fallback"]


def test_assemble_chunk_keeps_an_explicit_source_text():
    chunk = chunking.assemble_chunk("hierarchical_layout", {}, "Layout text", [span(text=None)],
                                    pdf_sha256=PDF_A, source="t.pdf", source_text="Layout text")
    assert chunk["source_text"] == "Layout text" == chunk["text"]
