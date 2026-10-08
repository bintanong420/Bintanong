"""Phase 1 Task 3, group 4: NormalizedQuery, RoutingDecision (and its legacy adapter), RetrievalResult."""

from __future__ import annotations

import copy

import pytest
from pydantic import ValidationError

from backend.bintanong_contracts import base, routing_adapter, runtime
import contracts_fixtures as fx


def bad(cls, payload, match):
    """The payload must be rejected, and for the stated reason."""
    with pytest.raises((ValidationError, base.ContractError), match=match):
        cls.parse(payload)


# ---------------------------------------------------------------- NormalizedQuery
def query(**over):
    d = {"schema_version": "bintanong-normalized-query-v1", "original_text": "Hindi ba pwede mag-enroll bukas?",
         "normalized_text": "hindi ba pwede mag-enroll bukas?", "language_hints": ["tl", "en"],
         "intent": "enrollment", "entities": [{"kind": "course", "value": "FICTIONAL-101", "source_ref": None}],
         "ambiguities": [], "negations": ["hindi"], "time_qualifiers": ["bukas"], "session_fact_refs": ["fact-synth-0001"]}
    d.update(over)
    return d


def test_normalized_query_roundtrips():
    q = runtime.NormalizedQuery.parse(query())
    assert runtime.NormalizedQuery.parse(base.canonical_json(q)) == q


@pytest.mark.parametrize("over,match", [
    (dict(original_text=""), "original_text"), (dict(normalized_text=""), "normalized_text"),
    (dict(negations=["not"]), "normalization dropped .not."),                       # normalization dropped the negation
    (dict(time_qualifiers=["next semester"]), "normalization dropped .next semester."),       # normalization dropped the time qualifier
    (dict(session_fact_refs=["ver-synth-handbook-1"]), "session_fact_refs"),   # institutional id as a private fact reference
    (dict(session_fact_refs=["fact-a", "fact-a"]), "duplicate session fact references"),
    (dict(session_fact_refs=["sess-synth-0001"]), "session_fact_refs"),
    (dict(entities=[{"kind": "course", "value": "X", "source_ref": "fact-synth-0001"}]), "only an institutional source id"),  # entity sourced from a private fact
    (dict(language_hints=["Tagalog"]), "language_hints"), (dict(intent=""), "intent"), (dict(verified=True), "verified"),
    (dict(is_policy=True), "is_policy"),
])
def test_malformed_query_is_rejected(over, match):
    bad(runtime.NormalizedQuery, query(**over), match)


def test_user_assertions_are_not_policy_there_is_no_policy_field():
    assert "policy" not in " ".join(runtime.NormalizedQuery.model_fields)


# ---------------------------------------------------------------- RoutingDecision
def routing(**over):
    d = {"schema_version": "bintanong-routing-decision-v1", "route": "RAG", "control": None, "confidence": 0.9,
         "predicate_request": None, "required_facts": [], "missing_facts": [], "reason": "policy explanation"}
    d.update(over)
    return d


def predicate(**over):
    d = {"predicate": "can_enroll_fictional",
         "inputs": [{"name": "course", "value": "FICTIONAL-101", "fact_ref": "fact-synth-0001"}]}
    d.update(over)
    return d


def test_valid_routes_roundtrip():
    for r in (routing(), routing(route="Symbolic", predicate_request=predicate(), required_facts=["course result"]),
              routing(route="Hybrid", predicate_request=predicate())):
        m = runtime.RoutingDecision.parse(r)
        assert runtime.RoutingDecision.parse(base.canonical_json(m)) == m
        assert m.dispatchable


def test_control_outcomes_have_no_route_and_are_not_dispatchable():
    for control in ("clarify", "greeting", "unsupported_scope", "evidence_unavailable"):
        m = runtime.RoutingDecision.parse(routing(route=None, control=control))
        assert not m.dispatchable
        with pytest.raises(base.ContractError, match="control"):
            runtime.dispatch_route(m)


def test_route_and_control_cannot_both_be_absent_or_both_present():
    bad(runtime.RoutingDecision, routing(route=None, control=None), "exactly one of route and control")
    bad(runtime.RoutingDecision, routing(route="RAG", control="greeting"), "exactly one of route and control")
    bad(runtime.RoutingDecision, routing(route="Symbolic", control="clarify", predicate_request=predicate()),
        "exactly one of route and control")


@pytest.mark.parametrize("over,match", [
    (dict(route="Direct"), "not a route"), (dict(route="rag"), "not a route"), (dict(route=""), "not a route"),
    (dict(route="Symbolic"), "needs a typed predicate request"),    # symbolic needs a predicate
    (dict(route="Hybrid"), "needs a typed predicate request"),
    (dict(route="RAG", predicate_request=predicate()), "carries no symbolic predicate request"),                                   # RAG with a symbolic request
    (dict(route="RAG", missing_facts=["x"]), "missing_facts must be a subset"),                                             # cannot dispatch with missing facts
    (dict(route="Symbolic", predicate_request=predicate(), missing_facts=["x"]), "missing_facts must be a subset"),
    (dict(route=None, control="greeting", predicate_request=predicate()), "carries no predicate request or facts"),
    (dict(route=None, control="greeting", missing_facts=["x"]), "missing_facts must be a subset|carries no predicate"),
    (dict(route=None, control="unsupported_scope", required_facts=["x"]), "carries no predicate request or facts"),
    (dict(route=None, control="evidence_unavailable", predicate_request=predicate()), "carries no predicate request or facts"),
    (dict(route=None, control="chat"), "not a control outcome"), (dict(route=None, control="Direct"), "not a control outcome"),
    (dict(confidence=1.5), "confidence"), (dict(confidence=-0.1), "confidence"), (dict(reason=""), "reason"),
    (dict(reason="x" * 241), "reason"),
    (dict(required_facts=[""]), "required_facts"), (dict(unknown=1), "unknown"),
    (dict(schema_version="bintanong-routing-decision-v2"), "unknown schema_version"), (dict(schema_version=None), "schema_version"),
])
def test_contradictory_or_malformed_routing_is_rejected(over, match):
    bad(runtime.RoutingDecision, routing(**over), match)


def test_clarify_may_keep_the_predicate_and_must_name_what_is_missing():
    m = runtime.RoutingDecision.parse(routing(route=None, control="clarify", predicate_request=predicate(),
                                              required_facts=["a"], missing_facts=["a"]))
    assert m.missing_facts == ("a",) and not m.dispatchable
    bad(runtime.RoutingDecision, routing(route=None, control="clarify", predicate_request=predicate(),
                                         required_facts=["a"], missing_facts=["b"]), "missing_facts must be a subset")  # missing must be required


@pytest.mark.parametrize("bad_predicate,match", [
    ({"predicate": "can_enroll(X)", "inputs": []}, "predicate"),
    ({"predicate": "can_enroll_fictional(a).", "inputs": []}, "predicate"),
    ({"predicate": "assert(foo)", "inputs": []}, "predicate"),
    ({"predicate": "Can_Enroll", "inputs": []}, "predicate"),
    ({"predicate": "", "inputs": []}, "predicate"),
    ({"predicate": "can_enroll_fictional", "inputs": [{"name": "course", "value": "a\nb", "fact_ref": None}]}, "value"),
    ({"predicate": "can_enroll_fictional", "inputs": [{"name": "course", "value": "", "fact_ref": None}]}, "value"),
    ({"predicate": "can_enroll_fictional", "inputs": [{"name": "Course", "value": "x", "fact_ref": None}]}, "name"),
    ({"predicate": "can_enroll_fictional", "inputs": [{"name": "c", "value": "x", "fact_ref": None},
                                                       {"name": "c", "value": "y", "fact_ref": None}]}, "duplicate input names"),
    ({"predicate": "can_enroll_fictional", "inputs": [{"name": "c", "value": "x", "fact_ref": "ver-synth-1"}]}, "fact_ref"),
    ({"predicate": "can_enroll_fictional", "inputs": [], "goal": "can_enroll_fictional(x)."}, "goal"),
])
def test_free_form_generated_goals_are_not_accepted(bad_predicate, match):
    bad(runtime.RoutingDecision, routing(route="Symbolic", predicate_request=bad_predicate), match)


def test_bound_input_values_allow_course_codes_and_decimal_grades():
    for v in ("CS 101", "FICTIONAL-101", "1.75", "2018-2019"):
        runtime.BoundInput.model_validate({"name": "x", "value": v, "fact_ref": None})


# ---------------------------------------------------------------- legacy adapter
def test_legacy_rag_route_converts_and_keeps_confidence_and_reason():
    got = routing_adapter.from_legacy_routing({"route": "RAG", "confidence": 0.8, "reason": "handbook lookup"})
    assert got.route == "RAG" and got.control is None and got.confidence == 0.8 and got.reason == "handbook lookup"


def test_legacy_object_with_attributes_is_accepted_duck_typed():
    class Legacy:
        route, confidence, reason = "RAG", 0.5, "r"
    assert routing_adapter.from_legacy_routing(Legacy()).route == "RAG"


def test_legacy_direct_is_refused_and_names_the_open_owner_decision():
    with pytest.raises(routing_adapter.LegacyRoutingError) as info:
        routing_adapter.from_legacy_routing({"route": "Direct", "confidence": 0.9, "reason": "hi"})
    assert info.value.reason == "legacy_direct_unresolved_owner_decision"
    assert "owner" in str(info.value).lower() and "Direct" in str(info.value)
    # and the contract itself never accepts it as a route
    bad(runtime.RoutingDecision, routing(route="Direct"), "not a route")


def test_legacy_symbolic_and_hybrid_need_a_typed_predicate_from_another_component():
    for route in ("Symbolic", "Hybrid"):
        with pytest.raises(routing_adapter.LegacyRoutingError) as info:
            routing_adapter.from_legacy_routing({"route": route, "confidence": 0.9, "reason": "r"})
        assert info.value.reason == "legacy_route_needs_predicate_request"
        got = routing_adapter.from_legacy_routing({"route": route, "confidence": 0.9, "reason": "r"},
                                                  predicate_request=predicate())
        assert got.route == route and got.predicate_request.predicate == "can_enroll_fictional"


def test_legacy_rag_with_a_predicate_is_refused():
    with pytest.raises(routing_adapter.LegacyRoutingError):
        routing_adapter.from_legacy_routing({"route": "RAG", "confidence": 0.9, "reason": "r"},
                                            predicate_request=predicate())


@pytest.mark.parametrize("legacy,why", [
    ({"route": "Direct"}, "legacy_direct_unresolved_owner_decision"),
    ({"route": "Other", "confidence": 0.5, "reason": "r"}, "legacy_unknown_route"),
    ({"route": "RAG", "confidence": 0.5}, "legacy_missing_field:reason"),
    ({"route": "RAG", "reason": "r"}, "legacy_missing_field:confidence"),
    ({"route": "RAG", "confidence": 0.5, "reason": "r", "extra": 1}, "legacy_unknown_field:extra"),
    ({"route": "RAG", "confidence": 2.0, "reason": "r"}, "legacy_invalid"),
    ({"route": "RAG", "confidence": 0.5, "reason": "x" * 500}, "legacy_invalid"),
    ("RAG", "legacy_not_a_decision"), (None, "legacy_not_a_decision"),
])
def test_legacy_malformed_input_is_refused_with_a_named_reason(legacy, why):
    with pytest.raises(routing_adapter.LegacyRoutingError) as info:
        routing_adapter.from_legacy_routing(legacy)
    assert info.value.reason == why


# ---------------------------------------------------------------- RetrievalResult
def rbad(match, **over):
    bad(runtime.RetrievalResult, fx.retrieval(**over), match)


def test_retrieval_result_roundtrips_and_exposes_source_locators():
    r = runtime.RetrievalResult.parse(fx.retrieval([fx.item(1, 1, 0.9), fx.item(2, 2, 0.5)]))
    assert runtime.RetrievalResult.parse(base.canonical_json(r)) == r
    assert [i.chunk.chunk_id[-1] for i in r.items] == ["1", "2"]
    assert len(r.items[0].source_locators) == 1 and r.items[0].source_locators[0].startswith("1" * 64)


def test_mixing_editions_of_one_document_is_rejected():
    rbad("more than one edition", items=[fx.item(1, 1, 0.9, edition="1"), fx.item(2, 2, 0.8, edition="2")])


def test_distinct_documents_may_share_a_result():
    r = runtime.RetrievalResult.parse(fx.retrieval([fx.item(1, 1, 0.9, doc="doc-a"), fx.item(2, 2, 0.8, doc="doc-b", edition="2")]))
    assert len(r.items) == 2


def test_mixing_release_ids_is_rejected():
    rbad("different knowledge release", items=[fx.item(1, 1, 0.9), fx.item(2, 2, 0.8, release="release-synth-2")])
    rbad("different knowledge release", release="release-synth-2")


def test_mixed_chunker_versions_are_rejected():
    rbad("chunker versions", items=[fx.item(1, 1, 0.9), fx.item(2, 2, 0.8, chunker="palsu-chunker-v2")])


def test_unbound_or_unanchored_chunks_cannot_be_retrieved_as_institutional_evidence():
    it = fx.item(1)
    it["chunk"].update(version_id=None, edition_id=None, document_id=None, source_verification="pending", register_binding=None)
    for s in it["chunk"]["spans"]:
        s["version_id"] = None
    rbad("anchored and bound", items=[it])
    un = fx.item(1)
    un["chunk"].update(byte_sha256=None, anchored=False, source_verification="pending", version_id=None,
                       edition_id=None, document_id=None, spans=[], register_binding=None)
    rbad("anchored and bound", items=[un])


@pytest.mark.parametrize("fn,match", [
    (lambda r: r["items"].__setitem__(1, copy.deepcopy(r["items"][0])), "duplicate chunk"),             # duplicate chunk
    (lambda r: r["items"][1].update(rank=1), "ranks must be 1..n"),                                        # duplicate rank
    (lambda r: r["items"][0].update(rank=2), "ranks must be 1..n"),                                        # ranks not contiguous from 1
    (lambda r: r["items"][1].update(score=0.95), "non-increasing score"),                                    # not ordered by score
    (lambda r: r["items"][0].update(score="nan"), "score"),
    (lambda r: r["items"][0].update(score=True), "score"),
    (lambda r: r.update(coverage_status="none"), "coverage_status .none. exactly when"),                                    # none with chunks
    (lambda r: r.update(coverage_status="complete"), "coverage_status"),
    (lambda r: r.update(items=[]), "coverage_status .none. exactly when"),                                                  # sufficient with no chunks
    (lambda r: r["config"].update(top_k=1), "more chunks than top_k"),                                         # more chunks than top_k
    (lambda r: r["config"].update(top_k=0), "top_k"),
    (lambda r: r["config"].update(min_score=0.95), "below the configured minimum"),                                  # item below the stated floor
    (lambda r: r["config"].update(embedding_model_revision="main"), "pinned"),
    (lambda r: r["config"].update(score_metric=""), "score_metric"),
    (lambda r: r.update(knowledge_release_id="fact-synth-1"), "knowledge_release_id"),
    (lambda r: r.update(unknown=1), "unknown"),
])
def test_malformed_retrieval_is_rejected(fn, match):
    r = fx.retrieval([fx.item(1, 1, 0.9), fx.item(2, 2, 0.5)])
    fn(r)
    bad(runtime.RetrievalResult, r, match)


def test_empty_result_must_say_so():
    ok = runtime.RetrievalResult.parse(fx.retrieval([], coverage="none"))
    assert ok.items == ()
    bad(runtime.RetrievalResult, fx.retrieval([], coverage="partial"), "coverage_status .none. exactly when")


# ---------------------------------------------------------------- mutation-driven additions
def test_a_route_with_missing_facts_must_become_a_clarification():
    bad(runtime.RoutingDecision, routing(route="RAG", required_facts=["x"], missing_facts=["x"]), "missing facts cannot be dispatched")
    bad(runtime.RoutingDecision, routing(route="Symbolic", predicate_request=predicate(),
                                         required_facts=["x"], missing_facts=["x"]), "missing facts cannot be dispatched")


def test_a_duplicate_chunk_is_rejected_even_with_valid_ranks_and_scores():
    dup = fx.item(1, 2, 0.5)
    bad(runtime.RetrievalResult, fx.retrieval([fx.item(1, 1, 0.9), dup]), "duplicate chunk")
