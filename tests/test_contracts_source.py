"""Phase 1 Task 3, group 2b: SourceSpan and Chunk (synthetic, fictional digests)."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from backend.bintanong_contracts import base, governance as gov, source

ROOT = Path(__file__).resolve().parents[1]
SHA_A, SHA_B = "a" * 64, "b" * 64


def span_dict(**over):
    d = {"schema_version": "bintanong-source-span-v1", "byte_sha256": SHA_A, "version_id": None, "page": 1,
         "printed_page_label": None,
         "locator": {"kind": "table_cells", "table_index": 0, "cell_ids": ["t0-c1"], "item_ids": [], "ref": None},
         "text": "Printed", "bbox": None, "bbox_origin": None, "page_size": None,
         "extraction": {"source_kind": "docling-json", "resolution_method": "deterministic",
                        "repair_id": None, "ocr_confidence": None}}
    d.update(over)
    return d


def digest(source_text, text):
    return source.compute_content_hash(source_text, text)


def chunk_dict(**over):
    d = {"schema_version": "bintanong-chunk-v1", "chunk_id": "c" * 64, "chunk_type": "course",
         "chunker_version": "palsu-chunker-v1", "edition_id": None, "document_id": None, "version_id": None,
         "byte_sha256": SHA_A, "anchored": True, "source_verification": "pending", "content_review": "pending",
         "text": "Summary", "source_text": "Printed", "spans": [span_dict()], "section_path": [], "scope": [],
         "content_hash": digest("Printed", "Summary"),
         "token_count": {"count": 3, "method": "estimate-v1", "exact": False,
                         "includes_prefix_and_special_tokens": False},
         "source_label": "synthetic.pdf", "type_fields": {}}
    d.update(over)
    return d


def bad(cls, payload):
    with pytest.raises((ValidationError, base.ContractError)):
        cls.parse(payload)


def badspan(**over):
    bad(source.SourceSpan, span_dict(**over))


def badchunk(**over):
    bad(source.Chunk, chunk_dict(**over))


# ---------------------------------------------------------------- SourceSpan
def test_anchored_span_roundtrips_canonically():
    s = source.SourceSpan.parse(span_dict())
    assert s.is_complete and s.printed_page_label is None
    text = base.canonical_json(s)
    assert source.SourceSpan.parse(text) == s and base.canonical_json(source.SourceSpan.parse(text)) == text


def test_geometry_needs_origin_and_page_size_together():
    ok = dict(bbox=[1.0, 2.0, 30.0, 40.0], bbox_origin="TOPLEFT", page_size=[612.0, 792.0])
    assert source.SourceSpan.parse(span_dict(**ok)).bbox == (1.0, 2.0, 30.0, 40.0)
    for drop in ("bbox_origin", "page_size"):
        o = dict(ok)
        o[drop] = None
        badspan(**o)


@pytest.mark.parametrize("over", [
    dict(bbox=[1, 2, 30, 40], bbox_origin="CENTER", page_size=[612, 792]),
    dict(bbox=[1, 2, 700, 40], bbox_origin="TOPLEFT", page_size=[612, 792]),         # right edge off the page
    dict(bbox=[1, 2, 30, 900], bbox_origin="TOPLEFT", page_size=[612, 792]),         # bottom edge off the page
    dict(bbox=[-1, 2, 30, 40], bbox_origin="TOPLEFT", page_size=[612, 792]),
    dict(bbox=[30, 2, 1, 40], bbox_origin="TOPLEFT", page_size=[612, 792]),          # inverted x
    dict(bbox=[1, 40, 30, 2], bbox_origin="TOPLEFT", page_size=[612, 792]),          # inverted y for TOPLEFT
    dict(bbox=[1, 2, 30, 40], bbox_origin="BOTTOMLEFT", page_size=[612, 792]),       # BOTTOMLEFT needs top > bottom
    dict(bbox=[1, 2, 30], bbox_origin="TOPLEFT", page_size=[612, 792]),
    dict(bbox=[1, 2, 30, 40], bbox_origin="TOPLEFT", page_size=[0, 792]),
    dict(bbox=[1, 2, 30, 40], bbox_origin="TOPLEFT", page_size=[612, -1]),
    dict(bbox=[1, 2, 30, 40], bbox_origin="TOPLEFT", page_size=[612, 792], page=None),
    dict(bbox=[1, 2, 30, 40], bbox_origin="TOPLEFT", page_size=[612, 792], byte_sha256=None),
])
def test_invalid_span_geometry_is_rejected(over):
    badspan(**over)


def test_bottomleft_geometry_is_accepted_when_top_is_above_bottom():
    s = source.SourceSpan.parse(span_dict(bbox=[1, 40, 30, 2], bbox_origin="BOTTOMLEFT", page_size=[612, 792]))
    assert s.bbox_origin == "BOTTOMLEFT"


def test_nan_and_infinity_are_not_geometry():
    for v in ("NaN", "Infinity"):
        with pytest.raises((ValidationError, base.ContractError, ValueError)):
            source.SourceSpan.parse(json.dumps(span_dict(bbox=[1, 2, 3, 4])).replace("[1, 2, 3, 4]", f"[1, 2, 3, {v}]"))


@pytest.mark.parametrize("over", [
    dict(page=0), dict(page=-1), dict(page=True), dict(page="1"),
    dict(byte_sha256="XYZ"), dict(byte_sha256="A" * 64),
    dict(version_id="doc-x"), dict(version_id="fact-1"),
    dict(extraction={"source_kind": "", "resolution_method": "deterministic", "repair_id": None, "ocr_confidence": None}),
    dict(extraction={"source_kind": "x", "resolution_method": "deterministic", "repair_id": None, "ocr_confidence": 1.5}),
    dict(printed_page_label=""),
    dict(unknown=1), dict(verified=True),
    dict(locator={"kind": "table_cells", "table_index": None, "cell_ids": ["a"], "item_ids": [], "ref": None}),
    dict(locator={"kind": "table_cells", "table_index": 0, "cell_ids": [], "item_ids": [], "ref": None}),
    dict(locator={"kind": "table_cells", "table_index": 0, "cell_ids": ["a", "a"], "item_ids": [], "ref": None}),
    dict(locator={"kind": "table_cells", "table_index": 0, "cell_ids": ["a"], "item_ids": ["b"], "ref": None}),
    dict(locator={"kind": "text_item", "table_index": None, "cell_ids": [], "item_ids": [], "ref": None}),
    dict(locator={"kind": "docling_ref", "table_index": None, "cell_ids": [], "item_ids": [], "ref": None}),
    dict(locator={"kind": "slide", "table_index": None, "cell_ids": [], "item_ids": ["x"], "ref": None}),
])
def test_incomplete_or_malformed_anchored_span_is_rejected(over):
    badspan(**over)


@pytest.mark.parametrize("over", [dict(page=None), dict(text=""), dict(text="  "), dict(text=None)])
def test_span_without_page_or_printed_text_parses_but_is_never_complete(over):
    assert not source.SourceSpan.parse(span_dict(**over)).is_complete


def test_other_locator_kinds_validate():
    for loc in ({"kind": "text_item", "table_index": None, "cell_ids": [], "item_ids": ["text-1"], "ref": None},
                {"kind": "docling_ref", "table_index": None, "cell_ids": [], "item_ids": [], "ref": "#/texts/2"}):
        assert source.SourceSpan.parse(span_dict(locator=loc)).locator.kind == loc["kind"]


def test_printed_label_is_kept_only_when_given():
    s = source.SourceSpan.parse(span_dict(printed_page_label="iv", page=7))
    assert (s.page, s.printed_page_label) == (7, "iv")


def test_unanchored_span_is_representable_but_never_complete():
    s = source.SourceSpan.parse(span_dict(byte_sha256=None, page=None, text=None))
    assert not s.is_complete and not s.anchored
    badspan(byte_sha256=None, version_id="ver-x")  # no bytes, no version claim


def test_span_binding_detects_a_mutated_source_digest():
    ver = source.SourceSpan.parse(span_dict())
    reg = _register(SHA_A)
    source.check_span_binding(ver, reg)
    with pytest.raises(base.ContractError, match="digest"):
        source.check_span_binding(source.SourceSpan.parse(span_dict(byte_sha256=SHA_B)), reg)
    with pytest.raises(base.ContractError, match="unanchored"):
        source.check_span_binding(source.SourceSpan.parse(span_dict(byte_sha256=None, page=None, text=None)), reg)
    with pytest.raises(base.ContractError, match="version"):
        source.check_span_binding(source.SourceSpan.parse(span_dict(version_id="ver-other-1")), reg)


def _register(sha=SHA_A, **over):
    rec = json.loads((ROOT / "knowledge/manifests/examples/synthetic-register.json").read_text(encoding="utf-8"))[1]
    rec["byte_sha256"] = sha
    rec.update(over)
    return gov.SourceDocumentVersion.parse(rec)


# ---------------------------------------------------------------- TokenCount
def tc(**over):
    return {"count": 5, "method": "estimate-v1", "exact": False, "includes_prefix_and_special_tokens": False, **over}


def test_estimates_never_claim_exactness():
    assert source.TokenCount.model_validate(tc()).exact is False
    for over in (dict(exact=True), dict(method="estimate-v2", exact=True),
                 dict(includes_prefix_and_special_tokens=True), dict(count=-1), dict(method="")):
        with pytest.raises(ValidationError):
            source.TokenCount.model_validate(tc(**over))
    ok = source.TokenCount.model_validate(tc(method="tokenizer:synthetic@r1", exact=True,
                                               includes_prefix_and_special_tokens=True))
    assert ok.exact
    with pytest.raises(ValidationError):
        source.TokenCount.model_validate(tc(method="unspecified", exact=True))


# ---------------------------------------------------------------- Chunk
def test_chunk_roundtrips_and_separates_printed_from_explanatory_text():
    c = source.Chunk.parse(chunk_dict())
    assert c.source_text == "Printed" and c.text == "Summary"
    t = base.canonical_json(c)
    assert source.Chunk.parse(t) == c and base.canonical_json(source.Chunk.parse(t)) == t


def test_anchored_chunk_needs_a_complete_span():
    badchunk(spans=[])
    badchunk(spans=[span_dict(text=None)])
    badchunk(spans=[span_dict(page=None)])
    badchunk(source_text="")


def test_anchor_flag_and_digest_must_agree():
    badchunk(byte_sha256=None)                        # anchored without bytes
    badchunk(anchored=False)                          # bytes without the flag
    badchunk(spans=[span_dict(byte_sha256=SHA_B)])    # span from other bytes
    badchunk(spans=[span_dict(byte_sha256=None, page=None)])  # unanchored span in an anchored chunk


def test_unanchored_chunk_cannot_assert_a_verified_source():
    un = dict(byte_sha256=None, anchored=False, spans=[span_dict(byte_sha256=None, page=None)])
    assert source.Chunk.parse(chunk_dict(**un)).anchored is False
    assert source.Chunk.parse(chunk_dict(byte_sha256=None, anchored=False, spans=[])).spans == ()
    for state in ("observed", "verified", "rejected"):
        badchunk(**un, source_verification=state)
    badchunk(**un, version_id="ver-synth-handbook-2")
    badchunk(**un, edition_id="edition-synth-handbook-2")


def test_verified_claim_needs_a_bound_version():
    badchunk(source_verification="verified")
    badchunk(source_verification="verified", version_id="ver-synth-handbook-2")  # no edition
    source.Chunk.parse(chunk_dict(source_verification="verified", version_id="ver-synth-handbook-2",
                                  edition_id="edition-synth-handbook-2", document_id="doc-synth-handbook"))


def test_duplicate_source_locations_are_rejected():
    badchunk(spans=[span_dict(), span_dict()])
    other = span_dict(locator={"kind": "table_cells", "table_index": 0, "cell_ids": ["t0-c1", "t0-c2"],
                               "item_ids": [], "ref": None})
    badchunk(spans=[span_dict(), other])  # shares t0-c1
    ok = span_dict(page=2, locator={"kind": "table_cells", "table_index": 0, "cell_ids": ["t0-c9"],
                                    "item_ids": [], "ref": None})
    assert len(source.Chunk.parse(chunk_dict(spans=[span_dict(), ok])).spans) == 2


@pytest.mark.parametrize("over", [
    dict(content_hash="0" * 64), dict(content_hash="short"), dict(text="Other summary"), dict(source_text="Other"),
    dict(chunk_id="not-hex"), dict(chunk_id="C" * 64), dict(chunk_type=""), dict(chunker_version=""),
    dict(content_review="approved"), dict(content_review="verified"), dict(source_verification="approved"),
    dict(token_count=tc(exact=True)), dict(token_count=tc(method="")),
    dict(edition_id="ver-x"), dict(document_id="edition-x"), dict(version_id="fact-1"),
    dict(unknown_field=1), dict(approved=True), dict(approval_id="auth-1"), dict(promotion_status="VERIFIED"),
    dict(section_path="a/b"), dict(scope=[""]),
    dict(type_fields={"approved": True}), dict(type_fields={"verified": "yes"}), dict(type_fields={"promotion_status": "VERIFIED"}),
    dict(type_fields={"approval_id": "x"}), dict(type_fields={"source_verification": "verified"}),
    dict(source_label="C:\\Users\\x\\a.pdf"), dict(source_label="/home/u/a.pdf"),
])
def test_malformed_or_stale_chunk_is_rejected(over):
    badchunk(**over)


def test_chunk_is_immutable():
    c = source.Chunk.parse(chunk_dict())
    with pytest.raises(ValidationError):
        c.text = "x"
    assert isinstance(c.spans, tuple)


def test_content_hash_matches_the_extractor_algorithm_and_is_whitespace_normalised():
    assert source.compute_content_hash("a  b", "c\nd") == source.compute_content_hash("a b", "c d")
    assert source.compute_content_hash("a", "b") != source.compute_content_hash("b", "a")
    expect = hashlib.sha256(json.dumps(["a", "b"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    assert source.compute_content_hash("a", "b") == expect


# ---------------------------------------------------------------- binding to a register version
def bound(**over):
    over = {"source_verification": "observed", **over}
    return source.Chunk.parse(chunk_dict(
        version_id="ver-synth-handbook-2", edition_id="edition-synth-handbook-2",
        document_id="doc-synth-handbook", **over))


def test_binding_succeeds_only_for_the_same_bytes_and_ids():
    reg = _register(SHA_A)
    source.check_chunk_binding(bound(), reg)
    ids = dict(version_id="ver-synth-handbook-2", edition_id="edition-synth-handbook-2", document_id="doc-synth-handbook",
               source_verification="observed")
    for mutate in (dict(byte_sha256=SHA_B, spans=[span_dict(byte_sha256=SHA_B)]),
                   dict(version_id="ver-synth-handbook-1"),
                   dict(edition_id="edition-synth-handbook-1"),
                   dict(document_id="doc-other")):
        with pytest.raises(base.ContractError):
            source.check_chunk_binding(source.Chunk.parse(chunk_dict(**{**ids, **mutate})), reg)

def test_binding_rejects_a_verification_claim_that_differs_from_the_register():
    reg = _register(SHA_A)  # register says verification observed
    claim = source.Chunk.parse(chunk_dict(version_id="ver-synth-handbook-2", edition_id="edition-synth-handbook-2",
                                          document_id="doc-synth-handbook", source_verification="verified"))
    with pytest.raises(base.ContractError, match="verification"):
        source.check_chunk_binding(claim, reg)
    stale = bound(source_verification="pending")
    with pytest.raises(base.ContractError, match="stale|verification"):
        source.check_chunk_binding(stale, reg)


def test_binding_rejects_mismatched_acquisition():
    reg = _register(SHA_A)
    d = json.loads(base.canonical_json(reg))
    d["acquisition_state"] = {"state": "mismatch", "evidence_ref": "ev-b2"}
    d["verification_state"] = {"state": "pending", "evidence_ref": None}
    d["issuer"].update(value=None, state="pending", evidence_ref=None, basis=None)
    d["printed_revision"].update(value=None, state="pending", evidence_ref=None, basis=None)
    mism = gov.SourceDocumentVersion.parse(d)
    with pytest.raises(base.ContractError, match="acquisition"):
        source.check_chunk_binding(bound(source_verification="pending"), mism)


def test_bind_chunk_produces_a_bound_copy_and_never_a_verified_claim_beyond_the_register():
    reg = _register(SHA_A)
    unbound = source.Chunk.parse(chunk_dict())
    b = source.bind_chunk(unbound, reg)
    assert (b.version_id, b.edition_id, b.document_id) == (reg.version_id, reg.edition_id, reg.document_id)
    assert b.source_verification == reg.verification_state.state == "observed"
    assert all(s.version_id == reg.version_id for s in b.spans)
    assert unbound.version_id is None
    with pytest.raises(base.ContractError, match="digest"):
        source.bind_chunk(source.Chunk.parse(chunk_dict(byte_sha256=SHA_B, spans=[span_dict(byte_sha256=SHA_B)])), reg)
    with pytest.raises(base.ContractError, match="unanchored"):
        source.bind_chunk(source.Chunk.parse(chunk_dict(byte_sha256=None, anchored=False, spans=[])), reg)


# ---------------------------------------------------------------- mutation-driven additions
def test_only_an_exact_count_can_claim_prefix_and_special_token_coverage():
    with pytest.raises(ValidationError, match="only an exact count"):
        source.TokenCount.model_validate(tc(method="unspecified", exact=False, includes_prefix_and_special_tokens=True))


def test_page_size_must_be_positive_even_without_a_box():
    for size in ([0, 792], [612, 0], [-1, 5]):
        badspan(page_size=size)
    assert source.SourceSpan.parse(span_dict(page_size=[612, 792])).bbox is None


def test_anchor_flag_alone_is_checked():
    badchunk(anchored=False, spans=[])                       # bytes present, flag false
    badchunk(byte_sha256=None, anchored=True, spans=[])      # flag true, no bytes


def test_anchored_chunk_needs_non_blank_printed_text_even_with_a_matching_hash():
    badchunk(source_text="", content_hash=digest("", "Summary"))
    badchunk(source_text="  ", content_hash=digest("  ", "Summary"))


def test_unanchored_chunk_cannot_hold_an_anchored_span():
    badchunk(byte_sha256=None, anchored=False, spans=[span_dict()])


def test_a_span_cannot_name_another_version_than_its_chunk():
    s = span_dict()
    s["version_id"] = "ver-synth-handbook-1"
    badchunk(version_id="ver-synth-handbook-2", edition_id="edition-synth-handbook-2",
             document_id="doc-synth-handbook", source_verification="observed", spans=[s])
    s["version_id"] = "ver-synth-handbook-2"
    source.Chunk.parse(chunk_dict(version_id="ver-synth-handbook-2", edition_id="edition-synth-handbook-2",
                                  document_id="doc-synth-handbook", source_verification="observed", spans=[s]))


def test_chunk_digest_mismatch_is_named_at_the_chunk_level():
    reg = _register(SHA_A)
    other = bound(byte_sha256=SHA_B, spans=[span_dict(byte_sha256=SHA_B)])
    with pytest.raises(base.ContractError, match="chunk digest"):
        source.check_chunk_binding(other, reg)
