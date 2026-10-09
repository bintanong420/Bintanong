"""Phase 1 Task 3, fix pass 3, L-b: privileged keys by stem, all-zero revisions, model_copy re-validation."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend.bintanong_contracts import base, chunk_adapter, runtime, source
import contracts_fixtures as fx

# every key the prospectus extractor emits on a chunk, at any depth (read from a real run; names only)
EXTRACTOR_KEYS = ["b", "bbox", "binary_hash", "captions", "cell_ids", "charspan", "children", "chunk_id", "chunk_index",
                  "chunk_type", "chunker_version", "college", "content_hash", "content_layer", "content_review",
                  "coord_origin", "course_code", "course_title", "cref", "derived_fields", "doc_items", "filename",
                  "headings", "l", "label", "meta", "metadata", "mimetype", "omitted_course_codes", "origin", "page_no",
                  "pages", "parent", "part_count", "part_index", "pdf_sha256", "prerequisite_state", "program", "prov",
                  "r", "schema_name", "self_ref", "semester", "source", "source_anchored", "source_text", "t",
                  "table_indexes", "text", "text_kind", "token_count", "token_count_method", "unsourced_fields", "uri",
                  "version", "year_level"]


@pytest.mark.parametrize("key", EXTRACTOR_KEYS)
def test_no_key_the_extractor_emits_is_privileged(key):
    assert source.privileged_key_paths({key: 1}) == []


@pytest.mark.parametrize("key", [
    "is_approved", "isApproved", "IS-APPROVED", "promotionstatus", "promotion_status", "Promotion Status", "promoted",
    "promoted_by", "reviewed", "is_reviewed", "reviewedBy", "fully reviewed", "verified", "is_verified", "verified_by",
    "verification_state", "source_verification", "approval_date", "approver", "unapproved", "authorized_by", "is_authorized",
    "appr\u200boved", "approv%65d", "\uff41pproved", "pro\u00admoted", "ver\u0456fied", "ap_proved", "pro-motion_status", "re.viewed", "veri fied", "is__verif_ied",
])
def test_a_key_that_claims_status_is_found_by_its_stem(key):
    assert source.privileged_key_paths({key: True}) == [f"/{key}"]
    assert source.privileged_key_paths({"a": [{"b": {key: 1}}]}) == [f"/a/b/{key}"]


def test_a_chunk_refuses_a_stem_key_anywhere_in_type_fields():
    c = fx.chunk().model_dump(mode="json")
    for fields in ({"is_approved": True}, {"x": {"promotionstatus": "ok"}}, {"x": [{"reviewed_by": "me"}]}):
        with pytest.raises(ValidationError, match="privileged status key"):
            source.Chunk.parse({**c, "type_fields": fields})


def test_the_adapter_names_the_stem_key():
    base_chunk = {k: None for k in chunk_adapter.REQUIRED}
    base_chunk["is_approved"] = True
    with pytest.raises(chunk_adapter.ChunkMappingError, match="privileged_field:is_approved"):
        chunk_adapter.adapt_chunk(base_chunk)


# ---------------------------------------------------------------- pinned revisions
@pytest.mark.parametrize("text", ["0" * 40, "0" * 64])
def test_an_all_zero_revision_is_not_pinned(text):
    assert base.is_pinned_revision(text) is False


@pytest.mark.parametrize("text", ["0" * 39 + "1", "f" * 40, "0123456789abcdef" * 4, "a" * 64, "1" + "0" * 63])
def test_other_full_hex_revisions_are_pinned(text):
    assert base.is_pinned_revision(text) is True


def test_an_all_zero_revision_is_refused_where_it_is_used():
    r = fx.retrieval()
    r["config"]["embedding_model_revision"] = "0" * 40
    with pytest.raises(ValidationError, match="pinned"):
        runtime.RetrievalResult.parse(r)
    with pytest.raises(ValidationError, match="exact count"):
        source.TokenCount.parse({"count": 3, "method": "tokenizer:synthetic@" + "0" * 40, "exact": True,
                                 "includes_prefix_and_special_tokens": False})


# ---------------------------------------------------------------- model_copy
def test_model_copy_with_an_update_is_validated_again():
    chunk = fx.chunk()
    with pytest.raises(ValidationError, match="content_hash"):
        chunk.model_copy(update={"text": "silently changed"})
    with pytest.raises(ValidationError, match="Value error, 'approved' is not a verification_state in the g"):
        chunk.model_copy(update={"source_verification": "approved"})
    with pytest.raises(ValidationError, match='Extra inputs are not permitted'):
        chunk.model_copy(update={"unknown_field": 1})


def test_model_copy_without_an_update_still_works_and_equals():
    chunk = fx.chunk()
    assert chunk.model_copy() == chunk
    assert chunk.model_copy(deep=True) == chunk


def test_a_valid_update_is_applied():
    span = fx.span(fx.SHA["1"], text="t")
    moved = source.SourceSpan.parse(span).model_copy(update={"page": 3})
    assert moved.page == 3
    with pytest.raises(ValidationError, match='Input should be greater than or equal to 1'):
        source.SourceSpan.parse(span).model_copy(update={"page": 0})
