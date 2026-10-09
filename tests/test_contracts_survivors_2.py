"""Phase 1 Task 3, fix pass 2: tests for the mutants that survived the fix-pass-2 mutation run.

Every test here failed against at least one mutant of backend/bintanong_contracts in a scratch copy.
"""

from __future__ import annotations

import copy
import json

import pytest
from pydantic import ValidationError

from backend.bintanong_contracts import answer, base, chunk_adapter as ca, governance as gov, runtime, source
import contracts_fixtures as fx
import test_contracts_answer as ta
import test_contracts_base as tb
import test_contracts_chunk_adapter as ex
import test_contracts_governance as g
import test_contracts_source as s1
import test_contracts_source_fix2 as sf
import test_contracts_symbolic as ts


def test_the_year_window_of_a_timestamp_is_inclusive_at_both_ends():
    assert base.parse_timestamp("2000-01-01T00:00:00Z") is not None
    assert base.parse_timestamp("2100-12-31T23:59:59Z") is not None
    assert base.parse_timestamp("1999-12-31T23:59:59Z") is None
    assert base.parse_timestamp("2101-01-01T00:00:00Z") is None
    assert base.parse_timestamp("2026-01-01T00:00:00") is None        # a naive time has no zone


def test_a_mapping_that_is_not_json_is_a_contract_error():
    for broken in (float("nan"), float("inf"), object()):
        with pytest.raises(base.ContractError, match="not JSON-compatible"):
            tb.Sample.parse(tb.sample(name=broken))


def test_evidence_authorizes_honours_the_from_state():
    e = gov.Evidence.model_validate(g.ev("ev-t", "issuing_office_authorization", "issuing_office", authorization_ref="a"))
    assert gov.evidence_authorizes("approval_state", "approved", e, frm="requested")
    assert not gov.evidence_authorizes("approval_state", "approved", e, frm="not_requested")
    assert gov.evidence_authorizes("approval_state", "approved", e)


# ---------------------------------------------------------------- the chunk adapter names every rejection
@pytest.mark.parametrize("change,reason", [
    ({"section_path": "a/b"}, "invalid_section_path"), ({"section_path": [""]}, "invalid_section_path"),
    ({"section_path": [1]}, "invalid_section_path"), ({"section_path": ["a", ""]}, "invalid_section_path"),
    ({"token_count": -1}, "invalid_token_count"), ({"token_count": True}, "invalid_token_count"),
    ({"token_count": "3"}, "invalid_token_count"),
    ({"source_text": 5}, "invalid_source_text"),
    ({"weird": float("nan")}, "type_fields_not_json"),
    ({"chunk_type": ""}, "invalid_chunk"),
    ({"source_spans": [5]}, "invalid_span"),
])
def test_adapter_rejections_have_a_named_reason(change, reason):
    raw = {**ex.one("course"), **change}
    assert ex.reason(raw, page_sizes=ex.PAGE) == reason


def test_a_zero_estimate_token_count_is_a_count():
    got = ca.adapt_chunk({**ex.one("course"), "token_count": 0}, page_sizes=ex.PAGE)
    assert got.chunk.token_count.count == 0 and got.chunk.token_count.exact is False


def test_adapter_span_level_rejections_have_a_named_reason():
    raw = copy.deepcopy(ex.one("course"))

    def with_span(**over):
        c = copy.deepcopy(raw)
        c["source_spans"][0].update(over)
        return c
    missing = copy.deepcopy(raw)
    del missing["source_spans"][0]["text"]
    assert ex.reason(missing, page_sizes=ex.PAGE) == "missing_span_key:text"
    assert ex.reason(with_span(extraction=5), page_sizes=ex.PAGE) == "invalid_span:extraction"
    assert ex.reason(with_span(extraction={"source_kind": "k", "colour": "red"}), page_sizes=ex.PAGE) == "unmapped_extraction_key:colour"
    assert ex.reason(with_span(bbox=[1, 2, 3, "x"]), page_sizes=ex.PAGE) == "invalid_span:bbox"
    assert ex.reason(with_span(bbox=[True, 2, 3, 4]), page_sizes=ex.PAGE) == "invalid_span:bbox"
    with pytest.raises(ValueError, match="on_missing_page_size"):
        ca.adapt_chunk(raw, page_sizes=ex.PAGE, on_missing_page_size="guess")


def test_a_span_with_text_in_a_chunk_that_has_no_source_text_is_a_named_reason():
    raw = sf.layout_with_no_text()
    raw["source_spans"][0]["text"] = "printed after all"
    assert ex.reason(raw) == "span_text_without_source_text"


# ---------------------------------------------------------------- retrieval details
def test_a_section_and_a_reference_locator_show_in_source_locators():
    section = fx.item(1)
    section["chunk"]["spans"][0]["locator"] = {"kind": "section", "table_index": None, "cell_ids": [], "item_ids": [],
                                              "ref": None, "section_path": ["Part I", "Admission"]}
    ref = fx.item(2, 2, 0.8)
    ref["chunk"]["spans"][0]["locator"] = {"kind": "docling_ref", "table_index": None, "cell_ids": [], "item_ids": [],
                                          "ref": "#/texts/2", "section_path": []}
    r = runtime.RetrievalResult.parse(fx.retrieval([section, ref]))
    assert r.items[0].source_locators == (f"{'1' * 64}#p1:section:Part I,Admission",)
    assert r.items[1].source_locators == (f"{'1' * 64}#p1:docling_ref:#/texts/2",)


def test_the_embedding_model_id_is_scanned_for_private_ids():
    r = fx.retrieval()
    r["config"]["embedding_model_id"] = "fact-synth-0001"
    with pytest.raises(ValidationError, match="another namespace"):
        runtime.RetrievalResult.parse(r)


def test_the_top_k_the_score_order_and_the_floor_are_inclusive():
    two = [fx.item(1, 1, 0.9), fx.item(2, 2, 0.9)]
    r = fx.retrieval(two)
    r["config"].update(top_k=2, min_score=0.9)
    assert len(runtime.RetrievalResult.parse(r).items) == 2
    r["config"]["top_k"] = 1
    with pytest.raises(ValidationError, match="more chunks than top_k"):
        runtime.RetrievalResult.parse(r)
    r["config"].update(top_k=2, min_score=0.91)
    with pytest.raises(ValidationError, match="below the configured minimum"):
        runtime.RetrievalResult.parse(r)


# ---------------------------------------------------------------- boundaries of the geometry
def test_a_box_may_touch_the_page_edges_but_not_be_empty():
    page = [612, 792]
    source.SourceSpan.parse(s1.span_dict(bbox=[0, 0, 612, 792], bbox_origin="TOPLEFT", page_size=page))
    source.SourceSpan.parse(s1.span_dict(bbox=[0, 792, 612, 0], bbox_origin="BOTTOMLEFT", page_size=page))
    for origin, box in (("TOPLEFT", [5, 2, 5, 40]), ("TOPLEFT", [1, 7, 30, 7]), ("BOTTOMLEFT", [5, 40, 5, 2]),
                        ("BOTTOMLEFT", [1, 7, 30, 7])):
        with pytest.raises(ValidationError, match="empty or inverted"):
            source.SourceSpan.parse(s1.span_dict(bbox=box, bbox_origin=origin, page_size=page))
    for box in ([-0.1, 0, 10, 10], [0, -0.1, 10, 10], [0, 0, 612.1, 10], [0, 0, 10, 792.1]):
        with pytest.raises(ValidationError, match="outside the page"):
            source.SourceSpan.parse(s1.span_dict(bbox=box, bbox_origin="TOPLEFT", page_size=page))


# ---------------------------------------------------------------- the chunk binding
def test_an_unanchored_chunk_cannot_be_checked_against_a_register_version():
    chunk = source.Chunk.parse(s1.chunk_dict(byte_sha256=None, anchored=False, spans=[]))
    with pytest.raises(base.ContractError, match="unanchored"):
        source.check_chunk_binding(chunk, s1._register())


def test_a_content_review_claim_beyond_the_registers_is_named_on_its_own():
    rec = json.loads(json.dumps(g.register()[1]))
    rec["byte_sha256"] = s1.SHA_A
    rec["evidence"].append(g.ev("ev-cr", "content_review_record", "reviewer"))
    rec["content_review_state"] = {"state": "partially_reviewed", "evidence_ref": "ev-cr"}
    reg = gov.SourceDocumentVersion.parse(rec)
    binding = {"verification_evidence_ref": "ev-b3", "content_review_evidence_ref": "ev-cr"}
    ids = dict(version_id=reg.version_id, edition_id=reg.edition_id, document_id=reg.document_id,
               source_verification="observed", register_binding=binding)
    ok = source.Chunk.parse(s1.chunk_dict(content_review="partially_reviewed", **ids))
    source.check_chunk_binding(ok, reg)
    inflated = source.Chunk.parse(s1.chunk_dict(content_review="reviewed", **ids))
    with pytest.raises(base.ContractError, match="stale or inflated content review claim"):
        source.check_chunk_binding(inflated, reg)


# ---------------------------------------------------------------- the symbolic result
def test_an_unsupported_result_cannot_cite_rules_through_either_field():
    ts._result(ts.S)
    for over in (dict(rule_ids=["rule-synth-1"]), dict(rule_bundle_version="bundle-synth-1")):
        with pytest.raises(ValidationError, match="unsupported predicate cannot cite rules"):
            ts._result(ts.S, **over)


# ---------------------------------------------------------------- the envelope against its bundle
def test_an_answer_needs_the_decision_claim_of_its_own_outcome():
    only_passage = answer.EvidenceBundle.parse(ta.bundle(claims=("policy_passage",)))
    env = answer.AnswerEnvelope.parse(ta.envelope(route="Hybrid", decision=ta.decision("eligible")))
    with pytest.raises(base.ContractError, match="decision_eligible"):
        answer.check_envelope_against_bundle(env, only_passage)


def test_a_citation_can_name_a_reference_locator():
    b = ta.bundle(route="RAG", sym=False, facts=(), claims=("policy_passage",))
    b["retrieval"]["items"][0]["chunk"]["spans"][0]["locator"] = {
        "kind": "docling_ref", "table_index": None, "cell_ids": [], "item_ids": [], "ref": "#/texts/2", "section_path": []}
    bundle = answer.EvidenceBundle.parse(b)
    good = answer.AnswerEnvelope.parse(ta.envelope(citations=[{**ta.cite(), "locator_ref": "#/texts/2"}]))
    answer.check_envelope_against_bundle(good, bundle)
    wrong = answer.AnswerEnvelope.parse(ta.envelope(citations=[{**ta.cite(), "locator_ref": "#/texts/9"}]))
    with pytest.raises(base.ContractError, match="page or locator"):
        answer.check_envelope_against_bundle(wrong, bundle)
