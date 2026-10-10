"""Pending prospectus binding at the ingestion seam; synthetic bytes only."""
import copy
import importlib.util

import pytest

from backend.bintanong_contracts.chunk_adapter import locator_key, make_chunk_id
from backend.bintanong_contracts.governance import SourceDocumentVersion
from backend.bintanong_contracts.source import Chunk, check_chunk_binding, check_span_binding
from backend.bintanong_tools.document_ingest.register import mint_pending_register

MODULE = "backend.bintanong_tools.document_ingest.prospectus"
SHA = "a" * 64
PAGE = {(SHA, 1): (612.0, 792.0)}
# Known hash of canonical ["Printed course", "Printed course"].
HASH = "cac9449ee6e482d28a7615974ee06152385c1d31c0fc71441c40e0d517e7deed0"


def binder():
    assert importlib.util.find_spec(MODULE) is not None, "prospectus ingestion feature is missing"
    return importlib.import_module(MODULE).bind_prospectus_chunks


def inputs():
    version = mint_pending_register([{"sha256": SHA, "filename": "synthetic.pdf",
                                     "acquisition_locator": "shelf:synthetic"}], synthetic=True)[0]
    spans = [{"pdf_sha256": SHA, "page": 1, "printed_page_label": None,
              "locator": {"kind": "text_item", "item_ids": ["text-1"]},
              "text": "Printed course", "bbox": [1., 2., 30., 40.], "bbox_origin": "TOPLEFT",
              "extraction": {"source_kind": "docling-json", "resolution_method": "deterministic",
                             "repair_id": None, "ocr_confidence": None}}]
    from backend.bintanong_contracts.source import compute_content_hash
    digest = compute_content_hash("Printed course", "Printed course")
    chunk = {"chunk_id": make_chunk_id(SHA, locator_key(spans), digest), "chunk_type": "course",
             "chunker_version": "palsu-chunker-v1", "content_review": "pending", "pdf_sha256": SHA,
             "source_anchored": True, "text": "Printed course", "source_text": "Printed course",
             "source_spans": spans, "pages": [1], "table_indexes": [], "cell_ids": [],
             "content_hash": digest, "token_count": 3, "token_count_method": "estimate-v1",
             "source": "synthetic.pdf"}
    hierarchical = copy.deepcopy(chunk)
    hierarchical["source_spans"][0]["locator"]["item_ids"] = ["text-2"]
    hierarchical["chunk_id"] = make_chunk_id(SHA, locator_key(hierarchical["source_spans"]), digest)
    hierarchical["chunk_type"] = "hierarchical_text"
    payload = {"run_identity": {"pdf_sha256": SHA},
               "rag": {"semantic_chunks": [chunk], "hierarchical_chunks": [hierarchical]}}
    return payload, version


def test_binds_both_groups_preserving_identity_text_order_and_pending_states():
    bind = binder()
    payload, version = inputs()
    before, version_before = copy.deepcopy(payload), version.model_dump(mode="json")
    result = bind(payload, version, page_sizes=PAGE)
    assert set(result) == {"version_id", "source_sha256", "chunks", "rejections"}
    assert (result["version_id"], result["source_sha256"], result["rejections"]) == (version.version_id, SHA, [])
    original = payload["rag"]["semantic_chunks"] + payload["rag"]["hierarchical_chunks"]
    assert len(result["chunks"]) == 2
    for raw, serialized in zip(original, result["chunks"], strict=True):
        chunk = Chunk.parse(serialized)
        assert (chunk.chunk_id, chunk.content_hash, chunk.source_text, chunk.text) == (
            raw["chunk_id"], raw["content_hash"], raw["source_text"], raw["text"])
        assert (chunk.version_id, chunk.document_id, chunk.edition_id) == (
            version.version_id, version.document_id, version.edition_id)
        assert (chunk.content_review, chunk.source_verification, chunk.scope) == ("pending", "pending", ())
        check_chunk_binding(chunk, version)
        for span in chunk.spans:
            check_span_binding(span, version)
            assert span.version_id == version.version_id
    assert payload == before and version.model_dump(mode="json") == version_before


@pytest.mark.parametrize("attack", ["missing_digest", "wrong_digest", "foreign_version", "nonnull_version",
    "foreign_document", "foreign_edition", "foreign_span_version", "foreign_span_digest", "duplicate",
    "privileged_chunk", "privileged_span", "bad_rag", "bad_group", "bad_chunk", "missing_id"])
def test_global_refusal_checks_claims_before_any_write(attack):
    bind = binder()
    payload, version = inputs()
    chunk = payload["rag"]["hierarchical_chunks"][0]
    if attack == "missing_digest":
        payload["run_identity"].clear()
    elif attack == "wrong_digest":
        payload["run_identity"]["pdf_sha256"] = "b" * 64
    elif attack in {"foreign_version", "nonnull_version"}:
        chunk["version_id"] = "ver-other" if attack == "foreign_version" else version.version_id
    elif attack == "foreign_document":
        chunk["document_id"] = "doc-other"
    elif attack == "foreign_edition":
        chunk["edition_id"] = "edition-other"
    elif attack == "foreign_span_version":
        chunk["source_spans"][0]["version_id"] = "ver-other"
    elif attack == "foreign_span_digest":
        chunk["source_spans"][0]["pdf_sha256"] = "b" * 64
    elif attack == "duplicate":
        payload["rag"]["hierarchical_chunks"] = copy.deepcopy(payload["rag"]["semantic_chunks"])
    elif attack == "privileged_chunk":
        chunk["extra"] = {"is_approved": True}
    elif attack == "privileged_span":
        chunk["source_spans"][0]["extraction"]["verified_by"] = "forged"
    elif attack == "bad_rag":
        payload["rag"] = []
    elif attack == "bad_group":
        payload["rag"]["semantic_chunks"] = {}
    elif attack == "bad_chunk":
        payload["rag"]["hierarchical_chunks"] = [None]
    elif attack == "missing_id":
        del chunk["chunk_id"]
    before = copy.deepcopy(payload)
    with pytest.raises(ValueError):
        bind(payload, version, page_sizes=PAGE)
    assert payload == before


@pytest.mark.parametrize("failure,reason", [("geometry", "bbox_missing_page_size"),
    ("hash", "content_hash_mismatch"), ("unsupported", "incomplete_source_span")])
def test_each_unsupported_chunk_has_original_identity_and_reason(failure, reason):
    bind = binder()
    payload, version = inputs()
    chunk = payload["rag"]["hierarchical_chunks"][0]
    sizes = PAGE
    if failure == "geometry":
        sizes = {}
    elif failure == "hash":
        chunk["source_text"] = "altered raw text"
    else:
        chunk["source_text"] = None
        chunk["source_spans"][0]["text"] = None
    before = copy.deepcopy(payload)
    result = bind(payload, version, page_sizes=sizes)
    rejected = result["rejections"]
    assert any(r == {"chunk_id": chunk["chunk_id"], "reason": reason} for r in rejected)
    assert len(result["chunks"]) + len(rejected) == 2
    assert payload == before


def test_pending_loader_refuses_promoted_version_without_mutation():
    bind = binder()
    payload, version = inputs()
    data = version.model_dump()
    data["issuer"].update(state="not_stated", evidence_ref="ev-absence")
    data["evidence"] = ({"evidence_id": "ev-absence", "kind": "reviewer_absence_check",
                         "recorded_by": "reviewer", "recorded_at": "2026-01-01T00:00:00+00:00"},)
    promoted = SourceDocumentVersion.model_validate(data)
    before = promoted.model_dump(mode="json")
    with pytest.raises(ValueError):
        bind(payload, promoted, page_sizes=PAGE)
    assert promoted.model_dump(mode="json") == before
