"""Phase 1 Task 3, group 2c: adapter from prospectus_extractor v3.3 chunks to the Chunk contract.

The inputs are produced by the extractor's own chunk builders on a synthetic candidate, not hand-made
dicts. The adapter is read-only: it never edits the dict it is given.
"""

from __future__ import annotations

import copy

import pytest

from backend.bintanong_contracts import base, chunk_adapter as ca, source
from backend.bintanong_tools.prospectus_extractor import chunking, rag
from backend.bintanong_tools.prospectus_extractor.evidence import (
    NormalizedCell, NormalizedTable, ProspectusEvidence, SourceBBox)
from backend.bintanong_tools.prospectus_extractor.prerequisites import classify_prerequisite_state
from backend.bintanong_tools.prospectus_extractor.units import parse_units

PDF_A = "a" * 64
META = {"program_name": "BS Test", "degree": "BS Test", "college_code": "CT", "college_name": "College of Test",
        "campus": None, "effective_school_year": "2018-2019", "source_file": "synthetic.pdf"}
LAYOUT = [{"table_index": 0, "column_groups": [{"index": 0, "code_idx": 0, "title_idx": 1, "unit_idx": 2, "prereq_idx": 3}]}]
PAGE = {(PDF_A, 1): (612.0, 792.0), (PDF_A, 2): (612.0, 792.0)}


def cell(cid, text, page=1, row=0, col=0):
    return {"cell_id": cid, "table_index": 0, "text": text, "raw_text": text, "row_start": row,
            "row_end": row + 1, "col_start": col, "col_end": col + 1, "page": page,
            "bbox": [1.0, 2.0, 30.0, 40.0], "bbox_origin": "TOPLEFT"}


def course(code="CS 101", title="Intro", prereq="", row=1, page=1):
    cells = [cell(f"t0-r{row}-c0", code, row=row, page=page),
             cell(f"t0-r{row}-c1", title, row=row, col=1, page=page),
             cell(f"t0-r{row}-c2", "3", row=row, col=2, page=page)]
    if prereq:
        cells.append(cell(f"t0-r{row}-c3", prereq, row=row, col=3, page=page))
    units = parse_units("3")
    c = {"course_code": code, "course_title": title, "title_raw": title, "year_level": "1st Year",
         "semester": "1st Semester", "units": units, "total_units": units["total"], "prerequisites_raw": prereq,
         "prerequisites": [prereq] if prereq.startswith("CS ") else [], "prerequisites_unresolved": [],
         "standing_requirements": [], "category": "Core / Major", "elective_group": None,
         "_source": {"table_index": 0, "column_group": 0, "row_index": row},
         "provenance": {"table_index": 0, "source_cell_ids": [x["cell_id"] for x in cells], "source_cells": cells,
                        "valid": True, "resolution_method": "deterministic", "repair_id": None}}
    c["prerequisite_state"] = classify_prerequisite_state(c)
    return c


def document_for(courses):
    cells = {}
    for c in courses:
        for s in c["provenance"]["source_cells"]:
            box = SourceBBox(s["page"], *s["bbox"], s.get("bbox_origin"))
            cells[s["cell_id"]] = NormalizedCell(s["cell_id"], s["table_index"], s["raw_text"], s["text"],
                s["row_start"], s["row_end"], s["col_start"], s["col_end"], box)
    return ProspectusEvidence(tables=[NormalizedTable(0, 100, 4, list(cells.values()))], text_items=[],
                              source_kind="docling-json")


def semantic(pdf=PDF_A, courses=None):
    courses = courses or [course(), course("CS 102", "Next", "CS 101", row=2, page=2)]
    rejected = []
    terms = [{"year_level": "1st Year", "semester": "1st Semester", "declared_units": None,
              "computed_units": sum(c["total_units"] or 0 for c in courses)}]
    chunks = rag.build_semantic_rag_chunks(META, courses, [], terms, pdf_sha256=pdf,
        document=document_for(courses), layout=LAYOUT, rejected=rejected)
    assert rejected == []
    return chunks


def layout_chunks(pdf=PDF_A):
    doc = ProspectusEvidence(text_items=[
        {"item_id": "text-0", "label": "title", "text": "BS TEST CURRICULUM", "page": 1, "bbox": None}],
        docling_document=None, source_kind="docling-json")
    return rag.build_hierarchical_rag_chunks(doc, "t.pdf", pdf_sha256=pdf, rejected=[])


def one(kind, chunks=None):
    return next(c for c in (chunks or semantic()) if c["chunk_type"] == kind)


def reason(raw, **kw):
    with pytest.raises(ca.ChunkMappingError) as info:
        ca.adapt_chunk(raw, **kw)
    return info.value.reason


# ---------------------------------------------------------------- real chunks map and keep identity
def test_every_real_semantic_chunk_maps_with_page_sizes_and_keeps_ids_and_hashes():
    chunks = semantic()
    assert {c["chunk_type"] for c in chunks} >= {"course", "term_schedule", "program_overview"}
    for raw in chunks:
        before = copy.deepcopy(raw)
        got = ca.adapt_chunk(raw, page_sizes=PAGE)
        assert raw == before, "the adapter must not edit its input"
        c = got.chunk
        assert (c.chunk_id, c.content_hash, c.text, c.source_text) == (
            raw["chunk_id"], raw["content_hash"], raw["text"], raw["source_text"])
        assert c.byte_sha256 == raw["pdf_sha256"] == PDF_A and c.anchored
        assert c.chunker_version == raw["chunker_version"] and c.content_review == "pending"
        assert (c.token_count.count, c.token_count.method, c.token_count.exact) == (
            raw["token_count"], "estimate-v1", False)
        assert list(c.section_path) == raw.get("section_path", [])
        assert c.source_verification == "pending" and c.version_id is None and c.edition_id is None
        assert [s.page for s in c.spans] == [s["page"] for s in raw["source_spans"]]
        assert all(s.printed_page_label is None for s in c.spans), "a printed label is never invented"
        assert got.gaps == ()
        assert source.Chunk.parse(base.canonical_json(c)) == c


def test_type_specific_fields_are_kept_not_dropped():
    raw = one("course")
    c = ca.adapt_chunk(raw, page_sizes=PAGE).chunk
    assert c.type_fields["course_code"] == "CS 101"
    assert "derived_fields" in c.type_fields and "unsourced_fields" in c.type_fields
    mapped = {"chunk_id", "chunk_type", "chunker_version", "content_review", "pdf_sha256", "source_anchored",
              "text", "source_text", "source_spans", "pages", "table_indexes", "cell_ids", "content_hash",
              "token_count", "token_count_method", "source", "section_path"}
    assert set(c.type_fields) == set(raw) - mapped


def test_bbox_without_page_size_is_a_named_gap_not_an_invented_size():
    raw = one("course")
    assert any(s["bbox"] for s in raw["source_spans"])
    assert reason(raw) == "bbox_missing_page_size"
    assert reason(raw, page_sizes={(PDF_A, 2): (612.0, 792.0)}) == "bbox_missing_page_size"  # page 1 absent
    got = ca.adapt_chunk(raw, page_sizes={}, on_missing_page_size="omit_and_report")
    assert all(s.bbox is None and s.bbox_origin is None and s.page_size is None for s in got.chunk.spans)
    assert got.chunk.chunk_id == raw["chunk_id"]
    assert got.gaps and all(g.reason == "bbox_missing_page_size" and g.page == 1 for g in got.gaps)
    assert {g.span_index for g in got.gaps} == set(range(len(raw["source_spans"])))


def test_text_item_layout_chunk_without_geometry_needs_no_page_size():
    raw = one("hierarchical_layout_fallback", layout_chunks())
    c = ca.adapt_chunk(raw).chunk
    assert c.spans[0].locator.kind == "text_item" and c.spans[0].bbox is None
    assert c.chunk_id == raw["chunk_id"]


def test_unanchored_real_chunk_maps_as_unanchored_and_stays_pending():
    raw = one("hierarchical_layout_fallback", layout_chunks(pdf=None))
    c = ca.adapt_chunk(raw).chunk
    assert c.anchored is False and c.byte_sha256 is None and c.source_verification == "pending"
    assert all(not s.anchored for s in c.spans)


def test_adapter_helpers_match_the_extractor_algorithms():
    spans = [chunking.make_span(PDF_A, 1, {"kind": "text_item", "item_ids": ["x"]}, "t", None, "k")]
    assert ca.locator_key(spans) == chunking.locator_key(spans)
    assert ca.make_chunk_id(PDF_A, ca.locator_key(spans), "d") == chunking.make_chunk_id(PDF_A, ca.locator_key(spans), "d")
    assert ca.make_chunk_id(None, "k", "d") == chunking.make_chunk_id(None, "k", "d")
    assert source.compute_content_hash("a  b", "c") == chunking.content_hash("a  b", "c")
    assert ca.CHUNKER_VERSION == chunking.CHUNKER_VERSION
    assert ca.ESTIMATE_METHOD == chunking.TOKEN_COUNT_METHOD


# ---------------------------------------------------------------- named rejections
def test_not_a_mapping_and_missing_keys():
    assert reason([1]) == "not_a_mapping"
    raw = one("course")
    for key in ("chunk_id", "source_spans", "content_hash", "pdf_sha256", "token_count", "text"):
        broken = {k: v for k, v in raw.items() if k != key}
        assert reason(broken, page_sizes=PAGE) == f"missing_key:{key}"


def test_stale_or_altered_identity_is_rejected():
    raw = one("course")
    assert reason({**raw, "chunk_id": "0" * 64}, page_sizes=PAGE) == "chunk_id_mismatch"
    assert reason({**raw, "text": raw["text"] + "x"}, page_sizes=PAGE) == "content_hash_mismatch"
    assert reason({**raw, "source_text": "forged"}, page_sizes=PAGE) == "content_hash_mismatch"
    assert reason({**raw, "pages": [9]}, page_sizes=PAGE) == "derived_field_mismatch:pages"
    assert reason({**raw, "cell_ids": ["nope"]}, page_sizes=PAGE) == "derived_field_mismatch:cell_ids"
    assert reason({**raw, "table_indexes": [3]}, page_sizes=PAGE) == "derived_field_mismatch:table_indexes"
    assert reason({**raw, "chunker_version": "palsu-chunker-v0"}, page_sizes=PAGE) == "unsupported_chunker_version"
    assert reason({**raw, "token_count_method": "tokenizer:x@1"}, page_sizes=PAGE) == "unsupported_token_count_method"


def test_anchor_flag_digest_and_span_problems_are_rejected():
    raw = one("course")
    assert reason({**raw, "source_anchored": False}, page_sizes=PAGE) == "anchor_flag_mismatch"
    assert reason({**raw, "pdf_sha256": "nothex"}, page_sizes=PAGE) == "invalid_pdf_sha256"
    assert reason({**raw, "source_spans": []}, page_sizes=PAGE) == "no_source_spans"
    other = copy.deepcopy(raw)
    other["source_spans"][0]["pdf_sha256"] = "b" * 64
    assert reason(other, page_sizes=PAGE) == "span_digest_differs"


def test_span_problems_are_named():
    raw = one("course")

    def with_span(**over):
        c = copy.deepcopy(raw)
        c["source_spans"][0].update(over)
        return c
    assert reason(with_span(page=None), page_sizes=PAGE) == "span_missing_page"
    assert reason(with_span(text=None), page_sizes=PAGE) == "span_missing_text"
    assert reason(with_span(locator={"kind": "slide", "ids": ["x"]}), page_sizes=PAGE) == "unknown_locator_kind"
    assert reason(with_span(locator={"kind": "text_item", "item_ids": ["a"], "colour": "red"}), page_sizes=PAGE) \
        == "unmapped_locator_key:colour"
    assert reason(with_span(bbox_origin=None), page_sizes=PAGE) == "bbox_missing_origin"
    assert reason(with_span(bbox=[1, 2, 3]), page_sizes=PAGE) == "invalid_span:bbox"
    assert reason(with_span(bbox=[1.0, 2.0, 9999.0, 40.0]), page_sizes=PAGE) == "invalid_span_geometry"
    assert reason(with_span(printed_page_label=7), page_sizes=PAGE) == "invalid_span:printed_page_label"
    extra = copy.deepcopy(raw)
    extra["source_spans"][0]["approved"] = True
    assert reason(extra, page_sizes=PAGE) == "unmapped_span_key:approved"
    dup = copy.deepcopy(raw)
    dup["source_spans"].append(copy.deepcopy(dup["source_spans"][0]))
    assert reason(dup, page_sizes=PAGE) == "duplicate_source_location"


def test_privileged_status_keys_and_local_paths_are_rejected():
    raw = one("course")
    for key in ("approved", "promotion_status", "source_verification", "approval_id"):
        assert reason({**raw, key: "VERIFIED"}, page_sizes=PAGE) == f"privileged_field:{key}"
    assert reason({**raw, "source": "C:\\Users\\x\\a.pdf"}, page_sizes=PAGE) == "local_path_in_source"
    assert reason({**raw, "content_review": "approved"}, page_sizes=PAGE) == "invalid_content_review"


def test_a_page_missing_chunk_with_docling_ref_is_rejected_not_filled_in():
    raw = one("hierarchical_layout_fallback", layout_chunks())
    raw = copy.deepcopy(raw)
    raw["source_spans"][0]["page"] = None
    # page is part of the identity, so the page-free chunk is first refused for the missing page
    assert reason(raw) == "span_missing_page"
