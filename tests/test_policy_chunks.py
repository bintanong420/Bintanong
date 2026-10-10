"""Governed candidate chunks from synthetic source evidence."""
import copy
import importlib
from dataclasses import replace

import pytest

from backend.bintanong_contracts.source import Chunk, check_chunk_binding, privileged_key_paths
from backend.bintanong_tools.document_ingest import policy_text, procedure_text, register
from backend.bintanong_tools.prospectus_extractor.identity import InputSnapshot


def chunks_module():
    return importlib.import_module("backend.bintanong_tools.document_ingest.policy_chunks")


def item(text, page=1, label="text"):
    return {"text": text, "label": label, "prov": [{"page_no": page, "bbox": {
        "l": 20, "t": 150, "r": 450, "b": 180, "coord_origin": "TOPLEFT"}}]}


def raw_document(texts=(), tables=(), pages=2):
    return {"texts": list(texts), "tables": list(tables), "pages": {
        str(p): {"size": {"width": 600, "height": 800}} for p in range(1, pages + 1)}}


@pytest.fixture
def bound(tmp_path):
    root = tmp_path / "originals"
    root.mkdir()
    source = root / "handbook.pdf"
    source.write_bytes(b"%PDF-synthetic")
    snap = InputSnapshot(source)
    return root, snap, register.pending_version(snap, "shelf:synthetic", synthetic=True)


def test_raw_pending_bound_chunks_roundtrip_and_identity(bound):
    _, _, version = bound
    raw = raw_document([item("Scope", label="section_header"), item("Do not pay 25–50 pesos.²")])
    raw["texts"][1]["approval"] = "approved"
    before = copy.deepcopy(raw)
    candidates = policy_text.read_policy_items(raw, version, printed_page_labels={1: "iv"})
    result = chunks_module().build_policy_chunks(candidates)
    assert raw == before and len(result.chunks) == 2
    chunk = result.chunks[1]
    assert chunk.source_text == chunk.text == "Do not pay 25–50 pesos.²"
    assert chunk.section_path == ("Scope",) and chunk.scope == ()
    assert chunk.type_fields["printed_scope"] == "Do not pay 25–50 pesos.²"
    assert not privileged_key_paths(chunk.type_fields)
    assert chunk.source_verification == chunk.content_review == "pending"
    assert chunk.token_count.method == "estimate-v1" and not chunk.token_count.exact
    assert chunk.spans[0].printed_page_label == "iv"
    assert Chunk.parse(chunk.model_dump(mode="json")) == chunk
    check_chunk_binding(chunk, version)
    assert result == chunks_module().build_policy_chunks(candidates)
    stale = chunk.model_dump(mode="json")
    stale["content_hash"] = "f" * 64
    with pytest.raises(ValueError, match="content_hash"):
        Chunk.parse(stale)


@pytest.mark.parametrize("damage", ["page", "text", "origin", "size", "outside", "digest", "version",
                                    "foreign_page", "foreign_locator", "foreign_bbox"])
def test_forged_spans_reparsed_and_rejected(bound, damage):
    _, _, version = bound
    candidates = policy_text.read_policy_items(raw_document([item("not 12–²")]), version)
    span = candidates.units[0].spans[0]
    data = dict(span.__dict__)
    data.update({"page": None} if damage == "page" else {"text": ""} if damage == "text"
                else {"bbox_origin": None} if damage == "origin" else {"page_size": None}
                if damage == "size" else {"bbox": (0, 0, 999, 999)} if damage == "outside"
                else {"byte_sha256": "f" * 64} if damage == "digest" else {"version_id": "ver-other"}
                if damage == "version" else {"page": 2} if damage == "foreign_page"
                else {"bbox": (25, 150, 450, 180)} if damage == "foreign_bbox"
                else {"locator": span.locator.model_copy(update={"item_ids": ("text-foreign",)})})
    forged = type(span).model_construct(**data)
    candidates = replace(candidates, units=(replace(candidates.units[0], spans=(forged,)),))
    result = chunks_module().build_policy_chunks(candidates)
    assert result.chunks == () and len(result.rejections) == 1


def test_edition_separation_over_cap_and_unanchored_accounting(bound):
    _, snap, version = bound
    raw = raw_document([item("x" * 1500), {"text": "no location", "label": "text", "prov": []}])
    result = chunks_module().build_policy_chunks(policy_text.read_policy_items(raw, version))
    assert not result.chunks
    assert result.rejections[0].reason == "over_token_cap" and len(result.rejections) == 2
    first = chunks_module().build_policy_chunks(policy_text.read_policy_items(raw_document([item("rule")]), version))
    snap.path.write_bytes(b"%PDF-other-edition")
    second_version = register.pending_version(InputSnapshot(snap.path), "shelf:other", synthetic=True)
    second = chunks_module().build_policy_chunks(policy_text.read_policy_items(raw_document([item("rule")]), second_version))
    assert first.chunks[0].chunk_id != second.chunks[0].chunk_id


def table(rows, *, multi_page=False, headers=True):
    cells = []
    for row, text in enumerate(rows):
        cells.append({"cell_id": f"merged-{row}", "text": text,
            "column_header": headers and row == 0, "bbox": item("")["prov"][0]["bbox"],
            "start_row_offset_idx": row, "end_row_offset_idx": row + 1,
            "start_col_offset_idx": 0, "end_col_offset_idx": 2})
    return {"prov": [item("")["prov"][0]] + ([item("", page=2)["prov"][0]] if multi_page else []),
            "data": {"num_rows": len(rows), "num_cols": 2, "table_cells": cells}}


def test_policy_route_and_complete_table_header_split(bound):
    _, _, version = bound
    raw = raw_document([item("Scope", label="section_header")], [table(["Fees–²", "No fee " * 20, "Do not pay " * 15])])
    before = copy.deepcopy(raw)
    candidates = procedure_text.read_procedure_items(raw, version, classification="policy_candidate")
    assert not candidates.fields
    result = chunks_module().build_policy_chunks(candidates, token_cap=90)
    assert raw == before and len(result.table_coverage) == 1 and not result.rejections
    parts = [c for c in result.chunks if "table_id" in c.type_fields]
    assert len(parts) == 2
    assert all(c.spans[0].text == "Fees–²" and c.token_count.count <= 90 for c in parts)
    assert [c.spans[1].locator.cell_ids for c in parts] == [("merged-1",), ("merged-2",)]
    assert all(c.section_path == ("Scope",) for c in parts)


@pytest.mark.parametrize("damage", ["multi_page", "blank", "no_header", "bad_bbox", "oversize_row"])
def test_table_rejections_keep_raw_evidence(bound, damage):
    _, _, version = bound
    raw_table = table(["Header", "row " * 30, "next " * 30], multi_page=damage == "multi_page",
                      headers=damage != "no_header")
    if damage == "blank":
        raw_table["data"]["table_cells"][1]["text"] = ""
    elif damage == "bad_bbox":
        raw_table["data"]["table_cells"][1]["bbox"]["r"] = 999
    elif damage == "oversize_row":
        raw_table["data"]["table_cells"][1]["text"] = "x" * 900
    candidates = procedure_text.read_procedure_items(raw_document([], [raw_table]), version)
    result = chunks_module().build_policy_chunks(candidates, token_cap=80)
    assert not result.chunks and not result.table_coverage
    assert result.rejections[0].candidate_id == "table-0" and result.rejections[0].reason
    import json
    assert json.loads(candidates.tables[0].raw_table_json) == raw_table


def test_pptx_report_only_no_slide_as_pdf_page(bound):
    _, _, version = bound
    candidates = procedure_text.read_procedure_items(raw_document([item("slide")], [table(["cell"])]),
                                                     version, source_format="pptx")
    result = chunks_module().build_policy_chunks(candidates)
    assert not result.chunks and len(result.rejections) == 2
    assert {r.reason for r in result.rejections} == {"pending_locator_contract"}
