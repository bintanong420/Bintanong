"""Source spans and chunks: provenance, geometry, binding and mutation regressions."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from backend.bintanong_contracts import base
from backend.bintanong_contracts import chunk_adapter
from backend.bintanong_contracts import chunk_adapter as ca
from backend.bintanong_contracts import embedding
from backend.bintanong_contracts import governance as gov
from backend.bintanong_contracts import runtime
from backend.bintanong_contracts import source
from backend.bintanong_tools.prospectus_extractor import chunking
from backend.bintanong_tools.prospectus_extractor.text import clean_str

import contracts_fixtures as fx
import test_contracts_chunk_adapter as ex
import test_contracts_governance as g


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


def bad(cls, payload, match):
    """The payload must be rejected, and for the stated reason."""
    with pytest.raises((ValidationError, base.ContractError), match=match):
        cls.parse(payload)


def badspan(match, **over):
    bad(source.SourceSpan, span_dict(**over), match)


def badchunk(match, **over):
    bad(source.Chunk, chunk_dict(**over), match)


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
        badspan("needs its origin, the page size", **o)


@pytest.mark.parametrize("over,match", [
    (dict(bbox=[1, 2, 30, 40], bbox_origin="CENTER", page_size=[612, 792]), "bbox_origin"),
    (dict(bbox=[1, 2, 700, 40], bbox_origin="TOPLEFT", page_size=[612, 792]), "outside the page"),         # right edge off the page
    (dict(bbox=[1, 2, 30, 900], bbox_origin="TOPLEFT", page_size=[612, 792]), "outside the page"),         # bottom edge off the page
    (dict(bbox=[-1, 2, 30, 40], bbox_origin="TOPLEFT", page_size=[612, 792]), "outside the page"),
    (dict(bbox=[30, 2, 1, 40], bbox_origin="TOPLEFT", page_size=[612, 792]), "x range is empty or inverted"),          # inverted x
    (dict(bbox=[1, 40, 30, 2], bbox_origin="TOPLEFT", page_size=[612, 792]), "y range is empty or inverted"),          # inverted y for TOPLEFT
    (dict(bbox=[1, 2, 30, 40], bbox_origin="BOTTOMLEFT", page_size=[612, 792]), "y range is empty or inverted"),       # BOTTOMLEFT needs top > bottom
    (dict(bbox=[1, 2, 30], bbox_origin="TOPLEFT", page_size=[612, 792]), "bbox"),
    (dict(bbox=[1, 2, 30, 40], bbox_origin="TOPLEFT", page_size=[0, 792]), "page_size must be positive"),
    (dict(bbox=[1, 2, 30, 40], bbox_origin="TOPLEFT", page_size=[612, -1]), "page_size must be positive"),
    (dict(bbox=[1, 2, 30, 40], bbox_origin="TOPLEFT", page_size=[612, 792], page=None), "needs its origin"),
    (dict(bbox=[1, 2, 30, 40], bbox_origin="TOPLEFT", page_size=[612, 792], byte_sha256=None), "needs its origin"),
])
def test_invalid_span_geometry_is_rejected(over, match):
    badspan(match, **over)


def test_bottomleft_geometry_is_accepted_when_top_is_above_bottom():
    s = source.SourceSpan.parse(span_dict(bbox=[1, 40, 30, 2], bbox_origin="BOTTOMLEFT", page_size=[612, 792]))
    assert s.bbox_origin == "BOTTOMLEFT"


def test_nan_and_infinity_are_not_geometry():
    for v in ("NaN", "Infinity"):
        with pytest.raises((ValidationError, base.ContractError, ValueError), match='Input should be a finite number'):
            source.SourceSpan.parse(json.dumps(span_dict(bbox=[1, 2, 3, 4])).replace("[1, 2, 3, 4]", f"[1, 2, 3, {v}]"))


@pytest.mark.parametrize("over,match", [
    (dict(page=0), "page"), (dict(page=-1), "page"), (dict(page=True), "page"), (dict(page="1"), "page"),
    (dict(byte_sha256="XYZ"), "byte_sha256"), (dict(byte_sha256="A" * 64), "byte_sha256"),
    (dict(version_id="doc-x"), "version_id"), (dict(version_id="fact-1"), "version_id"),
    (dict(extraction={"source_kind": "", "resolution_method": "deterministic", "repair_id": None, "ocr_confidence": None}), "source_kind"),
    (dict(extraction={"source_kind": "x", "resolution_method": "deterministic", "repair_id": None, "ocr_confidence": 1.5}), "ocr_confidence"),
    (dict(printed_page_label=""), "printed_page_label"),
    (dict(unknown=1), "unknown"), (dict(verified=True), "verified"),
    (dict(locator={"kind": "table_cells", "table_index": None, "cell_ids": ["a"], "item_ids": [], "ref": None}), "do not fit kind"),
    (dict(locator={"kind": "table_cells", "table_index": 0, "cell_ids": [], "item_ids": [], "ref": None}), "do not fit kind"),
    (dict(locator={"kind": "table_cells", "table_index": 0, "cell_ids": ["a", "a"], "item_ids": [], "ref": None}), "duplicate ids"),
    (dict(locator={"kind": "table_cells", "table_index": 0, "cell_ids": ["a"], "item_ids": ["b"], "ref": None}), "do not fit kind"),
    (dict(locator={"kind": "text_item", "table_index": None, "cell_ids": [], "item_ids": [], "ref": None}), "do not fit kind"),
    (dict(locator={"kind": "docling_ref", "table_index": None, "cell_ids": [], "item_ids": [], "ref": None}), "do not fit kind"),
    (dict(locator={"kind": "slide", "table_index": None, "cell_ids": [], "item_ids": ["x"], "ref": None}), "kind"),
])
def test_incomplete_or_malformed_anchored_span_is_rejected(over, match):
    badspan(match, **over)


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
    badspan("no byte digest cannot claim a source version", byte_sha256=None, version_id="ver-x")  # no bytes, no version claim


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
        with pytest.raises(ValidationError, match='estimate|exact|greater than or equal|prefix/special|tokenizer|at least 1 character'):
            source.TokenCount.model_validate(tc(**over))
    ok = source.TokenCount.model_validate(tc(method="tokenizer:synthetic@" + "a" * 40, exact=True,
                                               includes_prefix_and_special_tokens=True))
    assert ok.exact
    with pytest.raises(ValidationError, match="Value error, an exact count must name its tokenizer as 'toke"):
        source.TokenCount.model_validate(tc(method="unspecified", exact=True))


# ---------------------------------------------------------------- Chunk
def test_chunk_roundtrips_and_separates_printed_from_explanatory_text():
    c = source.Chunk.parse(chunk_dict())
    assert c.source_text == "Printed" and c.text == "Summary"
    t = base.canonical_json(c)
    assert source.Chunk.parse(t) == c and base.canonical_json(source.Chunk.parse(t)) == t


def test_anchored_chunk_needs_a_complete_span():
    badchunk("at least one source span", spans=[])
    badchunk("carries no printed text", spans=[span_dict(text=None)])
    badchunk("no physical page", spans=[span_dict(page=None)])
    badchunk("printed source_text", source_text="")


def test_anchor_flag_and_digest_must_agree():
    badchunk("anchored must be true exactly when", byte_sha256=None)                        # anchored without bytes
    badchunk("anchored must be true exactly when", anchored=False)                          # bytes without the flag
    badchunk("digest differs from the chunk digest", spans=[span_dict(byte_sha256=SHA_B)])    # span from other bytes
    badchunk("digest differs from the chunk digest", spans=[span_dict(byte_sha256=None, page=None)])  # unanchored span in an anchored chunk


def test_unanchored_chunk_cannot_assert_a_verified_source():
    un = dict(byte_sha256=None, anchored=False, spans=[span_dict(byte_sha256=None, page=None)])
    assert source.Chunk.parse(chunk_dict(**un)).anchored is False
    assert source.Chunk.parse(chunk_dict(byte_sha256=None, anchored=False, spans=[])).spans == ()
    for state in ("observed", "verified", "rejected"):
        badchunk("cannot assert a source verification state", **un, source_verification=state)
    badchunk("cannot name a source version", **un, version_id="ver-synth-handbook-2")
    badchunk("cannot name a source version", **un, edition_id="edition-synth-handbook-2")


def test_verified_claim_needs_a_bound_version():
    binding = {"verification_evidence_ref": "ev-b3", "content_review_evidence_ref": None}
    badchunk("needs a bound version", source_verification="verified", register_binding=binding)
    badchunk("needs a bound version", source_verification="verified", version_id="ver-synth-handbook-2",
             register_binding=binding)  # no edition
    source.Chunk.parse(chunk_dict(source_verification="verified", version_id="ver-synth-handbook-2",
                                  edition_id="edition-synth-handbook-2", document_id="doc-synth-handbook",
                                  register_binding=binding))


def test_identical_spans_are_rejected_and_distinct_ones_are_not():
    def two(first, second):
        text = f"{first['text']} {second['text']}"
        return dict(spans=[first, second], source_text=text, content_hash=digest(text, "Summary"))
    with pytest.raises(ValidationError, match="identical"):
        source.Chunk.parse(chunk_dict(**two(span_dict(), span_dict())))
    shares = span_dict(text="Other", locator={"kind": "table_cells", "table_index": 0, "cell_ids": ["t0-c1", "t0-c2"],
                                              "item_ids": [], "ref": None})
    assert len(source.Chunk.parse(chunk_dict(**two(span_dict(), shares))).spans) == 2  # shares t0-c1, text differs
    other_page = span_dict(page=2)
    assert len(source.Chunk.parse(chunk_dict(**two(span_dict(), other_page))).spans) == 2
    ok = span_dict(page=2, text="Next", locator={"kind": "table_cells", "table_index": 0, "cell_ids": ["t0-c9"],
                                                "item_ids": [], "ref": None})
    assert len(source.Chunk.parse(chunk_dict(**two(span_dict(), ok))).spans) == 2


@pytest.mark.parametrize("over,match", [
    (dict(content_hash="0" * 64), "content_hash does not match"), (dict(content_hash="short"), "content_hash"),
    (dict(text="Other summary"), "content_hash does not match"), (dict(source_text="Other"), "content_hash does not match|differs"),
    (dict(chunk_id="not-hex"), "chunk_id"), (dict(chunk_id="C" * 64), "chunk_id"), (dict(chunk_type=""), "chunk_type"),
    (dict(chunker_version=""), "chunker_version"),
    (dict(content_review="approved"), "not a content_review_state"), (dict(content_review="verified"), "not a content_review_state"),
    (dict(source_verification="approved"), "not a verification_state"),
    (dict(token_count=tc(exact=True)), "estimate cannot claim an exact count"), (dict(token_count=tc(method="")), "method"),
    (dict(edition_id="ver-x"), "edition_id"), (dict(document_id="edition-x"), "document_id"), (dict(version_id="fact-1"), "version_id"),
    (dict(unknown_field=1), "unknown_field"), (dict(approved=True), "approved"), (dict(approval_id="auth-1"), "approval_id"),
    (dict(promotion_status="VERIFIED"), "promotion_status"),
    (dict(section_path="a/b"), "section_path"), (dict(scope=[""]), "scope"),
    (dict(type_fields={"approved": True}), "privileged"), (dict(type_fields={"verified": "yes"}), "privileged"),
    (dict(type_fields={"promotion_status": "VERIFIED"}), "privileged"),
    (dict(type_fields={"approval_id": "x"}), "privileged"), (dict(type_fields={"source_verification": "verified"}), "privileged"),
    (dict(source_label="C:\\Users\\x\\a.pdf"), "source_label"), (dict(source_label="/home/u/a.pdf"), "source_label"),
])
def test_malformed_or_stale_chunk_is_rejected(over, match):
    badchunk(match, **over)


def test_chunk_is_immutable():
    c = source.Chunk.parse(chunk_dict())
    with pytest.raises(ValidationError, match='Instance is frozen'):
        c.text = "x"
    assert isinstance(c.spans, tuple)


def test_content_hash_matches_the_extractor_algorithm_and_is_whitespace_normalised():
    assert source.compute_content_hash("a  b", "c\nd") == source.compute_content_hash("a b", "c d")
    assert source.compute_content_hash("a", "b") != source.compute_content_hash("b", "a")
    expect = hashlib.sha256(json.dumps(["a", "b"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    assert source.compute_content_hash("a", "b") == expect


# ---------------------------------------------------------------- binding to a register version
BIND = {"verification_evidence_ref": "ev-b3", "content_review_evidence_ref": None}


def bound(**over):
    over = {"source_verification": "observed", "register_binding": dict(BIND), **over}
    return source.Chunk.parse(chunk_dict(
        version_id="ver-synth-handbook-2", edition_id="edition-synth-handbook-2",
        document_id="doc-synth-handbook", **over))


def test_binding_succeeds_only_for_the_same_bytes_and_ids():
    reg = _register(SHA_A)
    source.check_chunk_binding(bound(), reg)
    ids = dict(version_id="ver-synth-handbook-2", edition_id="edition-synth-handbook-2", document_id="doc-synth-handbook",
               source_verification="observed", register_binding=dict(BIND))
    for mutate in (dict(byte_sha256=SHA_B, spans=[span_dict(byte_sha256=SHA_B)]),
                   dict(version_id="ver-synth-handbook-1"),
                   dict(edition_id="edition-synth-handbook-1"),
                   dict(document_id="doc-other")):
        with pytest.raises(base.ContractError, match='register|digest|!='):
            source.check_chunk_binding(source.Chunk.parse(chunk_dict(**{**ids, **mutate})), reg)

def test_binding_rejects_a_verification_claim_that_differs_from_the_register():
    reg = _register(SHA_A)  # register says verification observed
    claim = source.Chunk.parse(chunk_dict(version_id="ver-synth-handbook-2", edition_id="edition-synth-handbook-2",
                                          document_id="doc-synth-handbook", source_verification="verified",
                                          register_binding=dict(BIND)))
    with pytest.raises(base.ContractError, match="verification"):
        source.check_chunk_binding(claim, reg)
    stale = bound(source_verification="pending", register_binding=None)
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
        source.check_chunk_binding(bound(source_verification="pending", register_binding=None), mism)


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
        badspan("page_size must be positive", page_size=size)
    assert source.SourceSpan.parse(span_dict(page_size=[612, 792])).bbox is None


def test_anchor_flag_alone_is_checked():
    badchunk("anchored must be true exactly when", anchored=False, spans=[])                       # bytes present, flag false
    badchunk("anchored must be true exactly when", byte_sha256=None, anchored=True, spans=[])      # flag true, no bytes


def test_anchored_chunk_needs_non_blank_printed_text_even_with_a_matching_hash():
    badchunk("printed source_text", source_text="", content_hash=digest("", "Summary"))
    badchunk("printed source_text", source_text="  ", content_hash=digest("  ", "Summary"))


def test_unanchored_chunk_cannot_hold_an_anchored_span():
    badchunk("cannot hold anchored spans", byte_sha256=None, anchored=False, spans=[span_dict()])


def test_a_span_cannot_name_another_version_than_its_chunk():
    s = span_dict()
    s["version_id"] = "ver-synth-handbook-1"
    badchunk("different source version than the chunk", version_id="ver-synth-handbook-2", edition_id="edition-synth-handbook-2",
             document_id="doc-synth-handbook", source_verification="observed", spans=[s])
    s["version_id"] = "ver-synth-handbook-2"
    source.Chunk.parse(chunk_dict(version_id="ver-synth-handbook-2", edition_id="edition-synth-handbook-2",
                                  document_id="doc-synth-handbook", source_verification="observed", spans=[s]))


def test_chunk_digest_mismatch_is_named_at_the_chunk_level():
    reg = _register(SHA_A)
    other = bound(byte_sha256=SHA_B, spans=[span_dict(byte_sha256=SHA_B)])
    with pytest.raises(base.ContractError, match="chunk digest"):
        source.check_chunk_binding(other, reg)


# Span geometry and register binding






SHA40, SHA64 = "a" * 40, "b" * 64

def _reject_source_record(cls, payload, match):
    with pytest.raises((ValidationError, base.ContractError), match=match):
        cls.parse(payload)

# ---------------------------------------------------------------- M-e: TokenCount
def _typed_chunk(**over):
    return {"count": 5, "method": f"tokenizer:synthetic@{SHA40}", "exact": True,
            "includes_prefix_and_special_tokens": True, **over}

@pytest.mark.parametrize("method", [f"tokenizer:synthetic@{SHA40}", f"tokenizer:m@{SHA64}", f"tokenizer:org/model-x@{SHA40}"])
def test_an_exact_count_names_its_tokenizer_and_a_pinned_revision(method):
    assert source.TokenCount.model_validate(_typed_chunk(method=method)).exact

@pytest.mark.parametrize("method", [
    "tokenizer:@", f"tokenizer:@{SHA40}", "tokenizer:m@", "tokenizer:m@main", "tokenizer:m@r1", "tokenizer:m@latest",
    f"tokenizer:m@{SHA40.upper()}", f"tokenizer:m@{SHA40[:-1]}", f"tokenizer:m@{SHA40} ", "tokenizer:m", "tokenizer:",
    f"tokenizer: m@{SHA40}", f"tokenizer:m @{SHA40}", "unspecified", "estimate-v1"])
def test_an_exact_count_with_an_unpinned_or_malformed_method_is_rejected(method):
    with pytest.raises(ValidationError, match='Value error, an e'):
        source.TokenCount.model_validate(_typed_chunk(method=method))

def test_an_exact_count_of_zero_is_rejected_and_an_estimate_may_be_zero():
    with pytest.raises(ValidationError, match="exact count of 0"):
        source.TokenCount.model_validate(_typed_chunk(count=0))
    source.TokenCount.model_validate({"count": 0, "method": "estimate-v1", "exact": False,
                                      "includes_prefix_and_special_tokens": False})

# ---------------------------------------------------------------- M-e: EmbeddingRecord
def _source_record(**over):
    d = {"schema_version": "bintanong-embedding-record-v1", "chunk_id": "c" * 64, "chunk_content_hash": "d" * 64,
         "model_id": "synthetic-model", "model_revision": SHA40, "tokenizer_fingerprint": "1" * 64,
         "preprocessing_fingerprint": "2" * 64, "prompt_fingerprint": "3" * 64, "dimension": 4,
         "normalization": "l2", "vector": [0.5, 0.5, 0.5, 0.5], "token_count": _typed_chunk()}
    d.update(over)
    return d

@pytest.mark.parametrize("revision", [" main", "main\n", "refs/heads/main", "origin/main", "v1", "stable", "nightly", "x",
                                      "main", "master", "latest", "head", "HEAD", "r1" + "0" * 38, SHA40.upper(), SHA40[:-1],
                                      SHA40 + "0", ""])
def test_a_model_revision_must_be_a_full_lowercase_commit_or_digest(revision):
    with pytest.raises(ValidationError, match='pinned|at least 1 character'):
        embedding.EmbeddingRecord.parse(_source_record(model_revision=revision))

@pytest.mark.parametrize("revision", [SHA40, SHA64, "0123456789abcdef" * 4])
def test_a_full_commit_or_digest_is_a_pinned_revision(revision):
    assert embedding.EmbeddingRecord.parse(_source_record(model_revision=revision)).model_revision == revision

@pytest.mark.parametrize("field", ["tokenizer_fingerprint", "preprocessing_fingerprint", "prompt_fingerprint"])
def test_an_all_zero_fingerprint_is_rejected(field):
    with pytest.raises(ValidationError, match="all-zero"):
        embedding.EmbeddingRecord.parse(_source_record(**{field: "0" * 64}))

def test_the_l2_tolerance_is_one_in_a_million():
    scale = 1 + 2e-6
    with pytest.raises(ValidationError, match="l2-normalized"):
        embedding.EmbeddingRecord.parse(_source_record(vector=[0.5 * scale] * 4))
    scale = 1 + 4e-7
    embedding.EmbeddingRecord.parse(_source_record(vector=[0.5 * scale] * 4))
    assert embedding.L2_TOLERANCE == 1e-6

# ---------------------------------------------------------------- M-d: source_label and adapter source
@pytest.mark.parametrize("label", ["file:///a.pdf", "~/a.pdf", "../a.pdf", "D:rel.pdf", "dir\\a.pdf", "C:\\x\\a.pdf", "/abs/a.pdf",
                                   "https://example.invalid/a.pdf", "a/b.pdf", "..", "a\nb.pdf"])
def test_chunk_source_label_must_be_a_plain_file_name(label):
    _reject_source_record(source.Chunk, chunk_dict(source_label=label), "source_label")

def test_chunk_source_label_accepts_plain_names():
    for label in ("synthetic.pdf", "Student Handbook (2023).pdf", "BSBA-HRM_docling.json"):
        source.Chunk.parse(chunk_dict(source_label=label))

@pytest.mark.parametrize("value", ["file:///a.pdf", "~/a.pdf", "../a.pdf", "D:rel.pdf", "dir\\a.pdf", "https://example.invalid/a.pdf"])
def test_the_adapter_rejects_paths_and_urls_in_source(value):
    raw = ex.one("course")
    assert ex.reason({**raw, "source": value}, page_sizes=ex.PAGE) == "local_path_in_source"

# ---------------------------------------------------------------- M-f: source_text equals the span text
def test_source_text_must_equal_the_joined_span_text_in_span_order():
    other = span_dict(locator={"kind": "table_cells", "table_index": 0, "cell_ids": ["t0-c2"], "item_ids": [], "ref": None},
                      text="Second")
    good = chunk_dict(spans=[span_dict(), other], source_text="Printed Second", content_hash=digest("Printed Second", "Summary"))
    source.Chunk.parse(good)
    _reject_source_record(source.Chunk, {**good, "source_text": "Second Printed", "content_hash": digest("Second Printed", "Summary")},
        "source_text differs from the span text")
    source.Chunk.parse({**good, "source_text": "Printed   Second\n"} | {"content_hash": digest("Printed Second", "Summary")})

def test_the_reviews_accepted_example_is_now_rejected():
    forged = chunk_dict(source_text="Totally different printed rule", content_hash=digest("Totally different printed rule", "Summary"))
    _reject_source_record(source.Chunk, forged, "source_text differs from the span text")

def test_a_chunk_whose_spans_carry_no_printed_text_may_only_assert_no_source_text():
    layout = chunk_dict(source_text=None, spans=[span_dict(text=None)], content_hash=digest(None, "Summary"))
    c = source.Chunk.parse(layout)
    assert c.source_text is None and not c.spans[0].is_complete
    _reject_source_record(source.Chunk, {**layout, "source_text": "Asserted", "content_hash": digest("Asserted", "Summary")}, "no printed text")
    _reject_source_record(source.Chunk, chunk_dict(source_text=None, content_hash=digest(None, "Summary")), "carries printed text")
    _reject_source_record(source.Chunk, {**layout, "spans": []}, "at least one")
    _reject_source_record(source.Chunk, chunk_dict(source_text="", content_hash=digest("", "Summary")), "printed source_text")

def test_a_textless_layout_chunk_is_not_retrievable_evidence():
    from backend.bintanong_contracts import runtime
    c = source.Chunk.parse(chunk_dict(source_text=None, spans=[span_dict(text=None)], content_hash=digest(None, "Summary"),
                                      version_id="ver-synth-handbook-2", edition_id="edition-synth-handbook-2",
                                      document_id="doc-synth-handbook"))
    with pytest.raises(ValidationError, match="printed text"):
        runtime.RetrievedChunk.parse({"rank": 1, "score": 0.5, "knowledge_release_id": "release-synth-1",
                                               "chunk": c.model_dump(mode="json")})

# ---------------------------------------------------------------- M-n: identical spans only
def test_distinct_spans_that_share_a_cell_are_allowed_and_identical_spans_are_not():
    shared = span_dict(locator={"kind": "table_cells", "table_index": 0, "cell_ids": ["t0-c1", "t0-c2"], "item_ids": [], "ref": None},
                       text="Header and body")
    c = source.Chunk.parse(chunk_dict(spans=[span_dict(), shared], source_text="Printed Header and body",
                                      content_hash=digest("Printed Header and body", "Summary")))
    assert len(c.spans) == 2
    _reject_source_record(source.Chunk, chunk_dict(spans=[span_dict(), span_dict()], source_text="Printed Printed",
                                 content_hash=digest("Printed Printed", "Summary")), "identical")

# ---------------------------------------------------------------- M-m: status claims and type_fields
def bound_dict(**over):
    return chunk_dict(version_id="ver-synth-handbook-2", edition_id="edition-synth-handbook-2",
                      document_id="doc-synth-handbook", **over)

BIND = {"verification_evidence_ref": "ev-b3", "content_review_evidence_ref": None}

def test_verified_or_rejected_needs_a_register_binding():
    for state in ("verified", "rejected"):
        _reject_source_record(source.Chunk, bound_dict(source_verification=state), "needs a register_binding")
        source.Chunk.parse(bound_dict(source_verification=state, register_binding=BIND))
    _reject_source_record(source.Chunk, chunk_dict(content_review="reviewed", version_id="ver-synth-handbook-2",
                                 edition_id="edition-synth-handbook-2", document_id="doc-synth-handbook"), "content_review")
    source.Chunk.parse(bound_dict(source_verification="observed", register_binding=BIND))
    source.Chunk.parse(chunk_dict(content_review="reviewed"))            # an unbound extractor label stays a label
    source.Chunk.parse(bound_dict(source_verification="observed"))      # the observed default needs no binding at this level

def test_a_register_binding_must_match_the_claimed_states():
    _reject_source_record(source.Chunk, chunk_dict(register_binding=BIND), "no version")
    _reject_source_record(source.Chunk, bound_dict(source_verification="pending", register_binding=BIND), "verification_evidence_ref")
    _reject_source_record(source.Chunk, bound_dict(source_verification="verified",
                                 register_binding={**BIND, "verification_evidence_ref": None}), "verification_evidence_ref")
    _reject_source_record(source.Chunk, bound_dict(source_verification="observed",
                                 register_binding={**BIND, "content_review_evidence_ref": "ev-x"}), "content_review_evidence_ref")

def _register_version(sha=SHA_A):
    return _register(sha)

def test_the_binding_check_requires_the_registers_evidence_references():
    r = _register_version()
    ok = source.Chunk.parse(bound_dict(source_verification="observed", register_binding=BIND))
    source.check_chunk_binding(ok, r)
    for binding in (None, {**BIND, "verification_evidence_ref": "ev-other"}):
        c = source.Chunk.parse(bound_dict(source_verification="observed", **({"register_binding": binding} if binding else {})))
        with pytest.raises(base.ContractError, match="evidence reference"):
            source.check_chunk_binding(c, r)

def test_content_review_is_checked_against_the_register_when_bound():
    r = _register_version()
    c = source.Chunk.parse(bound_dict(source_verification="observed", content_review="partially_reviewed",
                                      register_binding={**BIND, "content_review_evidence_ref": "ev-x"}))
    with pytest.raises(base.ContractError, match="content review"):
        source.check_chunk_binding(c, r)

def test_bind_chunk_copies_both_states_and_the_evidence_references_from_the_register():
    r = _register_version()
    b = source.bind_chunk(source.Chunk.parse(chunk_dict(content_review="reviewed")), r)
    assert b.content_review == r.content_review_state.state == "pending"      # the extractor label is replaced
    assert b.register_binding.verification_evidence_ref == r.verification_state.evidence_ref
    assert b.register_binding.content_review_evidence_ref is None
    source.check_chunk_binding(b, r)

@pytest.mark.parametrize("key", ["VERIFIED ", " Approved", "extractor_status", "review_status", "Review Status", "source-verification",
                                 "PROMOTION_STATUS", "Status"])
def test_privileged_type_field_keys_are_found_case_and_space_insensitively(key):
    _reject_source_record(source.Chunk, chunk_dict(type_fields={key: True}), "privileged")

@pytest.mark.parametrize("fields", [{"outer": {"approved": True}}, {"outer": [{"deep": {"VERIFIED ": 1}}]},
                                    {"a": {"b": {"c": {"extractor_status": "x"}}}}])
def test_privileged_type_field_keys_are_found_at_any_depth(fields):
    _reject_source_record(source.Chunk, chunk_dict(type_fields=fields), "privileged")

def test_type_fields_cannot_be_mutated_after_validation():
    c = source.Chunk.parse(chunk_dict(type_fields={"course_code": "CS 101", "nested": {"k": [1, 2]}}))
    with pytest.raises(TypeError, match='this mapping is immutable'):
        c.type_fields["approved"] = True
    with pytest.raises(TypeError, match='this mapping is immutable'):
        c.type_fields.update(verified=True)
    with pytest.raises(TypeError, match='this mapping is immutable'):
        del c.type_fields["course_code"]
    with pytest.raises(TypeError, match='this mapping is immutable'):
        c.type_fields["nested"]["k2"] = 1
    assert isinstance(c.type_fields["nested"]["k"], tuple)
    assert source.Chunk.parse(base.canonical_json(c)) == c
    assert copy.deepcopy(c) == c

@pytest.mark.parametrize("chunk_id", ["C" * 64, "c" * 63, "c" * 65, " " + "c" * 63, "c" * 64 + "\n", ""])
def test_chunk_id_is_64_lowercase_hex(chunk_id):
    _reject_source_record(source.Chunk, chunk_dict(chunk_id=chunk_id), "chunk_id")

# ---------------------------------------------------------------- M-g: spans keep original pages and sections
def test_a_span_keeps_the_original_page_of_a_split_pdf():
    s = source.SourceSpan.parse(span_dict(page=3, page_offset=56, original_page=59))
    assert (s.page, s.page_offset, s.original_page) == (3, 56, 59)
    source.SourceSpan.parse(span_dict(page=3, original_page=59))
    for over, match in ((dict(page=3, page_offset=56, original_page=60), "original_page"),
                        (dict(page=None, original_page=5), "physical page"),
                        (dict(page=None, page_offset=4), "physical page"),
                        (dict(page_offset=-1), "page_offset"), (dict(original_page=0), "original_page"),
                        (dict(byte_sha256=None, page=None, text=None, original_page=5), "physical page|byte digest")):
        _reject_source_record(source.SourceSpan, span_dict(**over), match)

def test_a_span_can_locate_a_section():
    loc = {"kind": "section", "table_index": None, "cell_ids": [], "item_ids": [], "ref": None,
           "section_path": ["Part I", "Admission"]}
    s = source.SourceSpan.parse(span_dict(locator=loc))
    assert s.locator.section_path == ("Part I", "Admission")
    for broken in ({**loc, "section_path": []}, {**loc, "item_ids": ["a"]}, {**loc, "section_path": [""]},
                   {**loc, "kind": "text_item", "item_ids": ["a"]}):
        _reject_source_record(source.SourceSpan, span_dict(locator=broken), "locator")
    assert source.SourceSpan.parse(span_dict()).locator.section_path == ()

# ---------------------------------------------------------------- M-n: the adapter on extractor output
def test_the_adapter_still_rejects_an_identical_span_and_names_it():
    raw = copy.deepcopy(ex.one("course"))
    raw["source_spans"].append(copy.deepcopy(raw["source_spans"][0]))
    assert ex.reason(raw, page_sizes=ex.PAGE) == "duplicate_source_location"

def test_the_adapter_accepts_a_distinct_span_sharing_a_cell():
    raw = copy.deepcopy(ex.one("course"))
    first = raw["source_spans"][0]
    twin = copy.deepcopy(first)
    twin["locator"] = {"kind": "table_cells", "table_index": first["locator"]["table_index"],
                       "cell_ids": [first["locator"]["cell_ids"][0], "t0-r9-c9"]}
    twin["text"] = first["text"] + " extra"
    twin["bbox"] = None
    twin["bbox_origin"] = None
    raw["source_spans"].append(twin)
    raw["cell_ids"] = list(dict.fromkeys(i for s in raw["source_spans"] for i in s["locator"].get("cell_ids", [])))
    raw["source_text"] = raw["source_text"] + " " + twin["text"]
    raw["content_hash"] = source.compute_content_hash(raw["source_text"], raw["text"])
    raw["chunk_id"] = ca.make_chunk_id(raw["pdf_sha256"], ca.locator_key(raw["source_spans"]), raw["content_hash"])
    assert ca.adapt_chunk(raw, page_sizes=ex.PAGE).chunk.chunk_id == raw["chunk_id"]

def layout_with_no_text():
    raw = copy.deepcopy(ex.one("hierarchical_layout_fallback", ex.layout_chunks()))
    for sp in raw["source_spans"]:
        sp["text"] = None
    raw["source_text"] = None
    raw["content_hash"] = source.compute_content_hash(None, raw["text"])
    raw["chunk_id"] = ca.make_chunk_id(raw["pdf_sha256"], ca.locator_key(raw["source_spans"]), raw["content_hash"])
    return raw

def test_a_layout_chunk_without_printed_text_maps_only_when_its_source_text_is_none():
    raw = layout_with_no_text()
    c = ca.adapt_chunk(raw).chunk
    assert c.source_text is None and c.spans[0].text is None and c.chunk_id == raw["chunk_id"]

def test_null_span_text_with_a_source_text_is_rejected_with_a_named_reason():
    raw = copy.deepcopy(ex.one("hierarchical_layout_fallback", ex.layout_chunks()))
    raw["source_spans"][0]["text"] = None
    assert ex.reason(raw) == "span_missing_text"

def test_a_source_text_that_differs_from_the_span_text_has_a_named_reason():
    raw = copy.deepcopy(ex.one("course"))
    raw["source_text"] = raw["source_text"] + " and more"
    raw["content_hash"] = source.compute_content_hash(raw["source_text"], raw["text"])
    raw["chunk_id"] = ca.make_chunk_id(raw["pdf_sha256"], ca.locator_key(raw["source_spans"]), raw["content_hash"])
    assert ex.reason(raw, page_sizes=ex.PAGE) == "source_text_differs_from_spans"

def test_a_nested_privileged_key_in_an_extractor_chunk_is_a_named_reason():
    raw = copy.deepcopy(ex.one("course"))
    raw["derived_fields"] = {"nested": {"Approved ": True}}
    assert ex.reason(raw, page_sizes=ex.PAGE).startswith("privileged_field:")

def test_a_chunk_without_printed_text_hashes_its_own_text_in_the_printed_slot_like_the_extractor():
    from backend.bintanong_tools.prospectus_extractor import chunking
    assert source.compute_content_hash(None, "Table  text") == source.compute_content_hash("Table text", "Table text")
    assert source.compute_content_hash(None, "Table text") == chunking.content_hash("Table text", "Table text")


# Extraction provenance and unknown fields





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


# Span identity and table chunks








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


# Mutation regressions: vocabulary and bounds




VOC = base.VOCAB

def test_a_bounding_box_without_its_origin_is_rejected_at_the_model_level():
    # [1, 40, 30, 2] would be a valid BOTTOMLEFT box, so only the missing origin can reject it
    with pytest.raises(ValidationError, match="origin"):
        source.SourceSpan.parse(span_dict(bbox=[1, 40, 30, 2], bbox_origin=None, page_size=[612, 792]))
    source.SourceSpan.parse(span_dict(bbox=[1, 40, 30, 2], bbox_origin="BOTTOMLEFT", page_size=[612, 792]))

@pytest.mark.parametrize("missing", ["page_size", "page", "byte_sha256"])
def test_a_bounding_box_needs_each_of_its_companions(missing):
    over = dict(bbox=[1, 2, 30, 40], bbox_origin="TOPLEFT", page_size=[612, 792])
    over[missing] = None
    with pytest.raises(ValidationError, match="needs its origin"):
        source.SourceSpan.parse(span_dict(**over))


# Mutation regressions: field and relationship guards






# ---------------------------------------------------------------- boundaries of the geometry
def test_a_box_may_touch_the_page_edges_but_not_be_empty():
    page = [612, 792]
    source.SourceSpan.parse(span_dict(bbox=[0, 0, 612, 792], bbox_origin="TOPLEFT", page_size=page))
    source.SourceSpan.parse(span_dict(bbox=[0, 792, 612, 0], bbox_origin="BOTTOMLEFT", page_size=page))
    for origin, box in (("TOPLEFT", [5, 2, 5, 40]), ("TOPLEFT", [1, 7, 30, 7]), ("BOTTOMLEFT", [5, 40, 5, 2]),
                        ("BOTTOMLEFT", [1, 7, 30, 7])):
        with pytest.raises(ValidationError, match="empty or inverted"):
            source.SourceSpan.parse(span_dict(bbox=box, bbox_origin=origin, page_size=page))
    for box in ([-0.1, 0, 10, 10], [0, -0.1, 10, 10], [0, 0, 612.1, 10], [0, 0, 10, 792.1]):
        with pytest.raises(ValidationError, match="outside the page"):
            source.SourceSpan.parse(span_dict(bbox=box, bbox_origin="TOPLEFT", page_size=page))

# ---------------------------------------------------------------- the chunk binding
def test_an_unanchored_chunk_cannot_be_checked_against_a_register_version():
    chunk = source.Chunk.parse(chunk_dict(byte_sha256=None, anchored=False, spans=[]))
    with pytest.raises(base.ContractError, match="unanchored"):
        source.check_chunk_binding(chunk, _register())

def test_a_content_review_claim_beyond_the_registers_is_named_on_its_own():
    rec = json.loads(json.dumps(g.register()[1]))
    rec["byte_sha256"] = SHA_A
    rec["evidence"].append(g.ev("ev-cr", "content_review_record", "reviewer"))
    rec["content_review_state"] = {"state": "partially_reviewed", "evidence_ref": "ev-cr"}
    reg = gov.SourceDocumentVersion.parse(rec)
    binding = {"verification_evidence_ref": "ev-b3", "content_review_evidence_ref": "ev-cr"}
    ids = dict(version_id=reg.version_id, edition_id=reg.edition_id, document_id=reg.document_id,
               source_verification="observed", register_binding=binding)
    ok = source.Chunk.parse(chunk_dict(content_review="partially_reviewed", **ids))
    source.check_chunk_binding(ok, reg)
    inflated = source.Chunk.parse(chunk_dict(content_review="reviewed", **ids))
    with pytest.raises(base.ContractError, match="stale or inflated content review claim"):
        source.check_chunk_binding(inflated, reg)
