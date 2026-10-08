"""Phase 1 Task 3, fix pass 3: span identity ignores whitespace only, and the hash of a table-serialization chunk
whose raw text the extractor dropped is rejected loudly (a pinned extractor-side limitation)."""

from __future__ import annotations

import copy

import pytest
from pydantic import ValidationError

from backend.bintanong_contracts import chunk_adapter, source
from backend.bintanong_tools.prospectus_extractor import chunking
from backend.bintanong_tools.prospectus_extractor.text import clean_str
import contracts_fixtures as fx


def two_span_chunk(second_text, second_cell="t0-c1"):
    """A chunk with two spans on the same cell; the second one's text is `second_text`."""
    base = fx.chunk(1).model_dump(mode="json")
    first = base["spans"][0]
    second = copy.deepcopy(first)
    second["text"] = second_text
    second["locator"]["cell_ids"] = [second_cell]
    base["spans"] = [first, second]
    joined = f"{first['text']} {second_text}"
    base["source_text"] = joined
    base["content_hash"] = source.compute_content_hash(joined, base["text"])
    return base


def test_the_same_span_written_twice_is_refused_even_when_only_whitespace_differs():
    for tail in ("", " ", "  ", "\n", "\t "):
        with pytest.raises(ValidationError, match="identical span repeated"):
            source.Chunk.parse(two_span_chunk("Fictional printed rule 1." + tail))


def test_inner_whitespace_runs_do_not_make_a_span_different():
    with pytest.raises(ValidationError, match="identical span repeated"):
        source.Chunk.parse(two_span_chunk("Fictional  printed\nrule 1."))


def test_two_spans_on_the_same_cell_with_different_text_are_allowed():
    source.Chunk.parse(two_span_chunk("Another printed rule."))


def test_span_identity_depends_on_the_text():
    a = source.SourceSpan.parse(fx.span(fx.SHA["1"], text="one"))
    b = source.SourceSpan.parse(fx.span(fx.SHA["1"], text="two"))
    c = source.SourceSpan.parse(fx.span(fx.SHA["1"], text="one "))
    assert source.span_identity(a) != source.span_identity(b)
    assert source.span_identity(a) == source.span_identity(c)


def test_the_adapter_applies_the_same_identity():
    raw = chunking.assemble_chunk(
        "course", {"chunk_index": 0}, "Total units.",
        [chunking.make_span("ab" * 32, 1, {"kind": "table_cells", "table_index": 0, "cell_ids": ["t0-c1"]}, "Total units.", None, "docling-json"),
         chunking.make_span("ab" * 32, 1, {"kind": "table_cells", "table_index": 0, "cell_ids": ["t0-c1"]}, "Total units. ", None, "docling-json")],
        pdf_sha256="ab" * 32, source="x.pdf", source_text="Total units. Total units.")
    with pytest.raises(chunk_adapter.ChunkMappingError, match='duplicate_source_location: identical span on page 1') as info:
        chunk_adapter.adapt_chunk(raw)
    assert info.value.reason == "duplicate_source_location"


# ---------------------------------------------------------------- L-d: raw text of a table serialization
def table_chunk(raw):
    """What the extractor emits for a table serialization: the hash covers the raw text, then source_text is dropped."""
    spans = [chunking.make_span("ab" * 32, 1, {"kind": "docling_ref", "ref": "#/tables/0"}, None, None, "docling-json")]
    c = chunking.assemble_chunk("hierarchical_layout", {"chunk_index": 0, "text_kind": "table_serialization"}, clean_str(raw),
                                spans, pdf_sha256="ab" * 32, source="x.pdf", source_text=raw)
    c["source_text"] = None
    return c


def test_a_table_serialization_whose_raw_text_is_already_clean_maps():
    assert chunk_adapter.adapt_chunk(table_chunk("Total 3 units of Fit 1")).chunk.source_text is None


@pytest.mark.parametrize("raw", ["Total 3 \u2013 units", "units\u00ad of Fit", "Area m\u00b2", "A \u2014 B"])
def test_a_table_serialization_whose_raw_text_clean_str_changed_is_rejected_loudly(raw):
    # The extractor hashed the raw text and dropped it, so the contract cannot recompute the hash. The chunk is
    # rejected, not trusted. This cannot be told from tampering, so the reason stays content_hash_mismatch.
    assert clean_str(raw) != raw
    with pytest.raises(chunk_adapter.ChunkMappingError, match='content_hash_mismatch') as info:
        chunk_adapter.adapt_chunk(table_chunk(raw))
    assert info.value.reason == "content_hash_mismatch"
