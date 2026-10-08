"""Phase 1 Task 3, group 3: EmbeddingRecord (validation only; no embedding or vector calls)."""

from __future__ import annotations

import json
import math

import pytest
from pydantic import ValidationError

from backend.bintanong_contracts import base, embedding, source

H = "d" * 64
REVISION = "0123456789abcdef" * 2 + "01234567"


def rec(**over):
    d = {"schema_version": "bintanong-embedding-record-v1", "chunk_id": "c" * 64, "chunk_content_hash": H,
         "model_id": "synthetic-model", "model_revision": REVISION, "tokenizer_fingerprint": "1" * 64,
         "preprocessing_fingerprint": "2" * 64, "prompt_fingerprint": "3" * 64, "dimension": 4,
         "normalization": "l2", "vector": [0.5, 0.5, 0.5, 0.5],
         "token_count": {"count": 12, "method": f"tokenizer:synthetic-model@{REVISION}", "exact": True,
                         "includes_prefix_and_special_tokens": True}}
    d.update(over)
    return d


def bad(match, **over):
    """The record must be rejected, and for the stated reason."""
    with pytest.raises((ValidationError, base.ContractError), match=match):
        embedding.EmbeddingRecord.parse(rec(**over))


def test_valid_record_roundtrips_canonically():
    r = embedding.EmbeddingRecord.parse(rec())
    t = base.canonical_json(r)
    assert embedding.EmbeddingRecord.parse(t) == r and base.canonical_json(embedding.EmbeddingRecord.parse(t)) == t
    assert isinstance(r.vector, tuple)


@pytest.mark.parametrize("over,match", [
    (dict(vector=[0.5, 0.5, 0.5]), "vector has 3 values"),                       # length != dimension
    (dict(vector=[0.5, 0.5, 0.5, 0.5, 0.5]), "vector has 5 values"),
    (dict(dimension=0), "dimension"), (dict(dimension=-4), "dimension"), (dict(dimension=True), "dimension"),
    (dict(vector=[1.0, 1.0, 1.0, 1.0]), "declared l2-normalized"),                  # claims l2 but norm is 2
    (dict(vector=[0.0, 0.0, 0.0, 0.0]), "declared l2-normalized"),
    (dict(vector=[0.5, 0.5, 0.5, "x"]), "vector"),
    (dict(normalization="unit"), "normalization"), (dict(normalization=None), "normalization"),
    (dict(chunk_id="nothex"), "chunk_id"), (dict(chunk_content_hash="short"), "chunk_content_hash"),
    (dict(model_id=""), "model_id"), (dict(model_revision=""), "model_revision"),
    (dict(model_revision="main"), "pinned revision"), (dict(model_revision="latest"), "pinned revision"),
    (dict(model_revision="HEAD"), "pinned revision"),
    (dict(tokenizer_fingerprint=""), "tokenizer_fingerprint"), (dict(tokenizer_fingerprint="Z" * 64), "tokenizer_fingerprint"),
    (dict(preprocessing_fingerprint=None), "preprocessing_fingerprint"), (dict(prompt_fingerprint="abc"), "prompt_fingerprint"),
    (dict(unknown=1), "unknown"), (dict(verified=True), "verified"),
    (dict(schema_version="bintanong-embedding-record-v2"), "unknown schema_version"),
])
def test_malformed_embedding_record_is_rejected(over, match):
    bad(match, **over)


def test_non_finite_vector_values_are_rejected():
    for value in ("NaN", "Infinity", "-Infinity"):
        text = json.dumps(rec()).replace("[0.5, 0.5, 0.5, 0.5]", f"[0.5, 0.5, 0.5, {value}]")
        with pytest.raises((ValidationError, ValueError)):
            embedding.EmbeddingRecord.parse(text)


def test_unnormalized_vectors_are_allowed_only_when_declared_none():
    r = embedding.EmbeddingRecord.parse(rec(normalization="none", vector=[1.0, 1.0, 1.0, 1.0]))
    assert math.isclose(math.sqrt(sum(v * v for v in r.vector)), 2.0)


@pytest.mark.parametrize("count", [
    dict(method="estimate-v1", exact=False, includes_prefix_and_special_tokens=False),  # an estimate
    dict(exact=True, includes_prefix_and_special_tokens=False),                          # no prefix/special tokens
    dict(exact=False, includes_prefix_and_special_tokens=False),
    dict(method="estimate-v1", exact=True),                                              # estimate claiming exact
])
def test_embedding_record_cannot_claim_exact_counting_from_an_estimate(count):
    base_count = rec()["token_count"]
    bad("token_count|estimate|exact", token_count={**base_count, **count})


def test_embedding_record_must_match_the_chunk_it_embeds():
    r = embedding.EmbeddingRecord.parse(rec(chunk_id="a" * 64, chunk_content_hash=source.compute_content_hash("p", "s")))
    chunk = _chunk()
    assert (chunk.chunk_id, chunk.content_hash) != (r.chunk_id, r.chunk_content_hash)
    with pytest.raises(base.ContractError, match="chunk"):
        embedding.check_embedding_matches_chunk(r, chunk)
    ok = embedding.EmbeddingRecord.parse(rec(chunk_id=chunk.chunk_id, chunk_content_hash=chunk.content_hash))
    embedding.check_embedding_matches_chunk(ok, chunk)
    stale = embedding.EmbeddingRecord.parse(rec(chunk_id=chunk.chunk_id, chunk_content_hash="9" * 64))
    with pytest.raises(base.ContractError, match="stale"):
        embedding.check_embedding_matches_chunk(stale, chunk)


def _chunk():
    sha = "a" * 64
    span = {"schema_version": "bintanong-source-span-v1", "byte_sha256": sha, "version_id": None, "page": 1,
            "printed_page_label": None,
            "locator": {"kind": "text_item", "table_index": None, "cell_ids": [], "item_ids": ["t1"], "ref": None},
            "text": "Printed", "bbox": None, "bbox_origin": None, "page_size": None,
            "extraction": {"source_kind": "k", "resolution_method": "m", "repair_id": None, "ocr_confidence": None}}
    return source.Chunk.parse({
        "schema_version": "bintanong-chunk-v1", "chunk_id": "b" * 64, "chunk_type": "course",
        "chunker_version": "palsu-chunker-v1", "edition_id": None, "document_id": None, "version_id": None,
        "byte_sha256": sha, "anchored": True, "source_verification": "pending", "content_review": "pending",
        "text": "Summary", "source_text": "Printed", "spans": [span], "section_path": [], "scope": [],
        "content_hash": source.compute_content_hash("Printed", "Summary"),
        "token_count": {"count": 3, "method": "estimate-v1", "exact": False,
                        "includes_prefix_and_special_tokens": False},
        "source_label": "x", "type_fields": {}})


# ---------------------------------------------------------------- mutation-driven additions
def test_vector_length_is_checked_independently_of_the_norm():
    bad("vector has 4 values, dimension says 3", dimension=3, vector=[0.5, 0.5, 0.5, 0.5])        # four unit-norm values, dimension says three
    bad("vector has 4 values, dimension says 5", dimension=5, vector=[0.5, 0.5, 0.5, 0.5])


def test_a_zero_vector_is_not_an_embedding_even_when_unnormalized():
    bad("zero vector", normalization="none", vector=[0.0, 0.0, 0.0, 0.0])


def test_an_embedding_for_another_chunk_is_named_even_when_the_hash_matches():
    chunk = _chunk()
    other = embedding.EmbeddingRecord.parse(rec(chunk_id="a" * 64, chunk_content_hash=chunk.content_hash))
    with pytest.raises(base.ContractError, match="another chunk"):
        embedding.check_embedding_matches_chunk(other, chunk)
