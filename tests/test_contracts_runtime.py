"""Runtime contracts: queries, routing, retrieval and session values."""

from __future__ import annotations

import copy
import random
import string

import pytest
from pydantic import ValidationError

from backend.bintanong_contracts import base
from backend.bintanong_contracts import routing_adapter
from backend.bintanong_contracts import runtime
from backend.bintanong_contracts import symbolic
from backend.bintanong_contracts.base import ContractError

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
    with pytest.raises(routing_adapter.LegacyRoutingError, match="legacy route 'Direct' is not accepted: its meaning is an unr") as info:
        routing_adapter.from_legacy_routing({"route": "Direct", "confidence": 0.9, "reason": "hi"})
    assert info.value.reason == "legacy_direct_unresolved_owner_decision"
    assert "owner" in str(info.value).lower() and "Direct" in str(info.value)
    # and the contract itself never accepts it as a route
    bad(runtime.RoutingDecision, routing(route="Direct"), "not a route")


def test_legacy_symbolic_and_hybrid_need_a_typed_predicate_from_another_component():
    for route in ("Symbolic", "Hybrid"):
        with pytest.raises(routing_adapter.LegacyRoutingError, match='legacy_route_needs_predicate_request: the legacy shape has n') as info:
            routing_adapter.from_legacy_routing({"route": route, "confidence": 0.9, "reason": "r"})
        assert info.value.reason == "legacy_route_needs_predicate_request"
        got = routing_adapter.from_legacy_routing({"route": route, "confidence": 0.9, "reason": "r"},
                                                  predicate_request=predicate())
        assert got.route == route and got.predicate_request.predicate == "can_enroll_fictional"


def test_legacy_rag_with_a_predicate_is_refused():
    with pytest.raises(routing_adapter.LegacyRoutingError, match='legacy_invalid'):
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


# Query normalization, session values and routing constraints






def _reject_runtime_record(cls, payload, match):
    with pytest.raises((ValidationError, base.ContractError), match=match):
        cls.parse(payload)

# ---------------------------------------------------------------- M-h: negations and time qualifiers
def _normalized_query(original, normalized, **over):
    return query(original_text=original, normalized_text=normalized, negations=[], time_qualifiers=[],
                    session_fact_refs=[], **over)

def test_a_dropped_negation_is_rejected_even_when_none_was_declared():
    _reject_runtime_record(runtime.NormalizedQuery, _normalized_query("I did not pass CS 101", "i did pass cs 101"), "dropped the negation 'not'")
    _reject_runtime_record(runtime.NormalizedQuery, _normalized_query("Hindi ako pumasa sa CS 101", "ako pumasa sa cs 101"), "dropped the negation 'hindi'")
    _reject_runtime_record(runtime.NormalizedQuery, _normalized_query("walang prereq ba?", "prereq ba?"), "dropped the negation 'walang'")
    _reject_runtime_record(runtime.NormalizedQuery, _normalized_query("Can I enroll without a prerequisite?", "can i enroll a prerequisite?"), "without")

def test_a_negation_that_survives_is_accepted():
    runtime.NormalizedQuery.parse(_normalized_query("I did NOT pass CS 101", "i did not pass cs 101"))
    runtime.NormalizedQuery.parse(_normalized_query("Hindi ako pumasa", "hindi ako pumasa"))

def test_a_contraction_counts_as_not_and_may_be_expanded():
    runtime.NormalizedQuery.parse(_normalized_query("I don't have a grade", "i do not have a grade"))
    runtime.NormalizedQuery.parse(_normalized_query("I don’t have a grade", "i don't have a grade"))
    _reject_runtime_record(runtime.NormalizedQuery, _normalized_query("I can't enroll", "i can enroll"), "dropped the negation 'not'")

def test_an_apostrophe_negation_in_tagalog_is_found():
    _reject_runtime_record(runtime.NormalizedQuery, _normalized_query("'di ako pumasa", "ako pumasa"), "dropped the negation 'di'")
    _reject_runtime_record(runtime.NormalizedQuery, _normalized_query("'wag muna", "muna"), "dropped the negation 'wag'")

def test_an_added_negation_is_rejected():
    _reject_runtime_record(runtime.NormalizedQuery, _normalized_query("I passed CS 101", "i did not pass cs 101"), "added the negation 'not'")

def test_a_word_that_merely_contains_a_negation_is_not_one():
    runtime.NormalizedQuery.parse(_normalized_query("Is there a knot or notice for CS 101?", "is there a knot or notice for cs 101?"))
    runtime.NormalizedQuery.parse(_normalized_query("What is the nothing-rule?", "what is the nothing-rule?"))

def test_a_dropped_or_added_time_qualifier_is_rejected():
    _reject_runtime_record(runtime.NormalizedQuery, _normalized_query("What can I take next sem?", "what can i take?"), "dropped the time qualifier 'next sem'")
    _reject_runtime_record(runtime.NormalizedQuery, _normalized_query("Pwede ba noong last semester?", "pwede ba last semester?"), "dropped the time qualifier 'noong'")
    _reject_runtime_record(runtime.NormalizedQuery, _normalized_query("Ano ang kukunin sa susunod? sa susunod na term", "ano ang kukunin?"), "time qualifier")
    _reject_runtime_record(runtime.NormalizedQuery, _normalized_query("What can I take?", "what can i take next semester?"), "added the time qualifier 'next semester'")
    runtime.NormalizedQuery.parse(_normalized_query("What can I take Next Sem?", "what can i take next sem?"))
    runtime.NormalizedQuery.parse(_normalized_query("What is the next semester fee?", "what is the next semester fee?"))

def test_a_time_phrase_inside_a_longer_word_is_not_a_qualifier():
    runtime.NormalizedQuery.parse(_normalized_query("The bukasan rules", "the rules"))

def test_declared_markers_must_still_be_in_the_normalized_text():
    _reject_runtime_record(runtime.NormalizedQuery, query(negations=["not"]), "dropped")
    _reject_runtime_record(runtime.NormalizedQuery, query(time_qualifiers=["next semester"]), "dropped")

def test_the_marker_lists_come_from_the_vocabulary_and_are_marked_owner_reviewable():
    markers = base.VOCAB["query_markers"]
    assert "OWNER-reviewable" in markers["note"]
    assert {"not", "hindi", "wala", "walang", "ayaw", "huwag", "di", "wag"} <= set(markers["negations"])
    assert {"noong", "sa susunod", "next semester"} <= set(markers["time_qualifiers"])

# ---------------------------------------------------------------- M-a: entity source references
@pytest.mark.parametrize("ref", ["fact-synth-0001", "sess-1", "ver-synth-1 ", " ver-synth-1", "ver-synth-1\n", "VER-synth-1",
                                 "ver-", "doc-", "ver-synth-1/x", "plain", ""])
def test_an_entity_may_cite_only_a_whole_institutional_id(ref):
    with pytest.raises(ValidationError, match='Value error, an entity may cite only an institutional source'):
        runtime.ResolvedEntity.parse({"kind": "course", "value": "X", "source_ref": ref})

@pytest.mark.parametrize("ref", ["ver-synth-handbook-1", "doc-synth-handbook", "edition-synth-handbook-2", "conflict-synth-0001", None])
def test_an_entity_may_cite_an_institutional_id(ref):
    runtime.ResolvedEntity.parse({"kind": "course", "value": "X", "source_ref": ref})

# ---------------------------------------------------------------- M-j: goals
PREDICATES = ["can_enroll(X)", "a.", "a :- b", "a b", "A", "1a", "", " a", "a ", "a\n", "x" * 65, "a-b", "a:b", "assert(foo)",
              "a,b", "a;b", "'a'", "\"a\"", "a%", "a/b", "A_b", "_a"]

@pytest.mark.parametrize("name", PREDICATES)
def test_a_decision_predicate_is_an_identifier_never_prolog(name):
    d = copy.deepcopy(_routing_record())
    d["predicate"] = name
    _reject_runtime_record(symbolic.DecisionOutcome, d, "predicate|String")
    _reject_runtime_record(runtime.PredicateRequest, {"predicate": name, "inputs": []}, "predicate|String")

def _routing_record():
    import json
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    return json.loads((root / "knowledge/manifests/examples/synthetic-decisions.json").read_text(encoding="utf-8"))[0]

def test_a_decision_predicate_identifier_is_accepted():
    d = _routing_record()
    for name in ("can_enroll_fictional", "a", "x" * 64, "p2_check"):
        symbolic.DecisionOutcome.parse({**d, "predicate": name})

def _session_value(v):
    return {"name": "course", "value": v, "fact_ref": None}

@pytest.mark.parametrize("v", [" CS 101", "CS 101 ", "CS  101", "a\x00b", "a\tb", "a\x1fb", "a\u202eb", "a\nb", ""])
def test_a_bound_value_refuses_padding_control_characters_and_empty_text(v):
    with pytest.raises(ValidationError, match='printable text|padding|at least 1 character'):
        runtime.BoundInput.parse(_session_value(v))

@pytest.mark.parametrize("v", ["X", "Course", "_", "_foo", "Y1", "CS101", "MATH101", "A_B", "is", "IS", "mod", "rem", "div", "xor",
                               "-", "/", "--", "..", ".5", "x), halt(", "x :- true", "a;b", "a'b"])
def test_a_bound_value_is_data_so_prolog_looking_text_is_accepted_and_must_be_quoted(v):
    assert runtime.BoundInput.parse(_session_value(v)).value == v
    assert runtime.prolog_quote(v).startswith("'") and runtime.prolog_quote(v).endswith("'")

@pytest.mark.parametrize("v", ["CS 101", "ITEC 101", "FICTIONAL-101", "1.75", "2018-2019", "cs101", "cs 101", "Intro to Computing",
                               "BS Computer Science", "a_b c", "Section 2B", "3"])
def test_ordinary_values_and_course_codes_with_a_separator_are_accepted(v):
    runtime.BoundInput.parse(_session_value(v))

def test_the_bound_value_comment_makes_no_false_claim():
    comment = runtime.__doc__ + open(runtime.__file__, encoding="utf-8").read()
    assert "no full stops" not in comment.lower()

# ---------------------------------------------------------------- M-e: the retrieval configuration
@pytest.mark.parametrize("revision", [" main", "main\n", "refs/heads/main", "origin/main", "v1", "stable", "nightly", "x", "main",
                                      "master", "r1" + "0" * 38, fx.REVISION.upper(), fx.REVISION[:-1], ""])
def test_the_retrieval_config_needs_a_pinned_revision(revision):
    r = fx.retrieval()
    r["config"]["embedding_model_revision"] = revision
    _reject_runtime_record(runtime.RetrievalResult, r, "pinned|embedding_model_revision")

def test_a_full_commit_or_digest_is_accepted_by_the_config():
    for revision in (fx.REVISION, "f" * 64):
        r = fx.retrieval()
        r["config"]["embedding_model_revision"] = revision
        runtime.RetrievalResult.parse(r)

# ---------------------------------------------------------------- RoutingDecision
def test_a_blank_reason_is_rejected():
    for reason in ("   ", "\t\n"):
        _reject_runtime_record(runtime.RoutingDecision, routing(reason=reason), "reason")

# ---------------------------------------------------------------- M-l: retrieval consistency
def _reject_routing_record(items, match, **over):
    _reject_runtime_record(runtime.RetrievalResult, fx.retrieval(items, **over), match)

def test_the_same_bytes_under_two_editions_or_versions_are_rejected():
    a = fx.item(1, 1, 0.9, edition="1")
    b = fx.item(2, 2, 0.8, edition="1", doc="doc-other")
    b["chunk"].update(edition_id="edition-synth-handbook-9", version_id="ver-synth-handbook-9")
    for s in b["chunk"]["spans"]:
        s["version_id"] = "ver-synth-handbook-9"
    _reject_routing_record([a, b], "same bytes")

def test_the_same_edition_over_different_bytes_under_different_documents_is_rejected():
    a = fx.item(1, 1, 0.9, edition="1")
    b = fx.item(2, 2, 0.8, edition="2", doc="doc-other")
    b["chunk"]["edition_id"] = "edition-synth-handbook-1"
    _reject_routing_record([a, b], "edition")

def test_two_editions_of_one_document_are_still_rejected():
    _reject_routing_record([fx.item(1, 1, 0.9, edition="1"), fx.item(2, 2, 0.8, edition="2")], "more than one edition")

def test_chunker_versions_in_one_result_stay_a_strict_default():
    _reject_routing_record([fx.item(1, 1, 0.9), fx.item(2, 2, 0.8, chunker="palsu-chunker-v2")], "chunker versions")

# ---------------------------------------------------------------- M-m: the register check runs inside the result
def test_a_result_needs_the_register_versions_its_chunks_cite():
    r = fx.retrieval()
    r["versions"] = []
    _reject_runtime_record(runtime.RetrievalResult, r, "not in the result's versions")
    r = fx.retrieval()
    r["versions"] = r["versions"] + [fx.version_for({**fx.item(2, edition="2")["chunk"]})]
    _reject_runtime_record(runtime.RetrievalResult, r, "no chunk cites it")

def test_a_chunk_claiming_more_than_its_register_version_is_rejected_inside_the_result():
    it = fx.item(1)
    it["chunk"]["source_verification"] = "verified"
    _reject_routing_record([it], "stale or inflated verification claim")

def test_a_chunk_citing_other_register_evidence_is_rejected_inside_the_result():
    it = fx.item(1)
    it["chunk"]["register_binding"]["verification_evidence_ref"] = "ev-forged"
    _reject_routing_record([it], "evidence reference")

def test_a_chunk_whose_bytes_differ_from_the_register_is_rejected_inside_the_result():
    r = fx.retrieval()
    r["versions"][0]["byte_sha256"] = "9" * 64
    _reject_runtime_record(runtime.RetrievalResult, r, "digest")

def test_the_registers_own_consistency_is_checked_inside_the_result():
    r = fx.retrieval([fx.item(1, 1, 0.9, edition="1"), fx.item(2, 2, 0.8, edition="1", doc="doc-other")])
    r["versions"].append(copy.deepcopy(r["versions"][0]))
    _reject_runtime_record(runtime.RetrievalResult, r, "duplicate version_id")

def test_an_honest_result_with_two_documents_is_accepted():
    r = runtime.RetrievalResult.parse(fx.retrieval([fx.item(1, 1, 0.9, doc="doc-a"), fx.item(2, 2, 0.8, doc="doc-b", edition="2")]))
    assert len(r.versions) == 2


# Unicode values and negation boundaries







SHAPES = ["HBO", "TQM", "P2101", "P2108", "E2101", "E2104", "Practicum", "GE- Elect: EM", "GE-Elect: PES",
          "CS 101", "GE-ET", "ITEC 101", "FICTIONAL-101", "CS101", "X", "Y1", "_foo", "A_B", "is", "mod", "-", "..",
          "a'b", "a\\b", ":- foo", "x), halt(", "a;b", "50% (lab)", "\u00d1and\u00fa 1"]

def _runtime_session_value(v):
    return {"name": "course", "value": v, "fact_ref": None}

def unquote(atom: str) -> str:
    """An independent reader of a single-quoted Prolog atom: the whole text must be ONE quoted atom."""
    assert len(atom) >= 2 and atom[0] == "'" and atom[-1] == "'", atom
    out, i, body = [], 0, atom[1:-1]
    while i < len(body):
        ch = body[i]
        assert ch != "'", f"unescaped quote inside {atom!r}"
        if ch == "\\":
            i += 1
            assert i < len(body) and body[i] in "\\'", f"bad escape in {atom!r}"
            ch = body[i]
        out.append(ch)
        i += 1
    return "".join(out)

@pytest.mark.parametrize("v", SHAPES)
def test_every_real_shape_parses_and_renders_as_one_quoted_atom(v):
    assert runtime.BoundInput.parse(_runtime_session_value(v)).value == v
    atom = runtime.prolog_quote(v)
    assert unquote(atom) == v

def test_quoting_is_exact_for_the_dangerous_values():
    assert runtime.prolog_quote("X") == "'X'"
    assert runtime.prolog_quote("HBO") == "'HBO'"
    assert runtime.prolog_quote("a'b") == "'a\\'b'"
    assert runtime.prolog_quote("a\\b") == "'a\\\\b'"
    assert runtime.prolog_quote(":- foo") == "':- foo'"

def test_quoting_round_trips_over_random_printable_text():
    rng = random.Random(20261007)
    alphabet = string.printable[:-5] + "'\\'\\\u00e9\u03a9"
    for _ in range(500):
        v = "".join(rng.choice(alphabet) for _ in range(rng.randint(1, 20))).strip()
        if not v or "  " in v:
            continue
        assert unquote(runtime.prolog_quote(v)) == v

@pytest.mark.parametrize("v", ["a\x00b", "a\nb", "a\rb", "a\tb", "a\x1fb", "a\x7fb", "a\x85b", "a\u202eb", "a\u200bb", "a\u00adb", "a\ue000b", "a\u0378b",
                               "a\u00a0b", "a\u2028b", "a\ud800b", ""])
def test_the_renderer_refuses_control_and_format_characters(v):
    with pytest.raises(ContractError, match="control|format|empty|printable"):
        runtime.prolog_quote(v)

@pytest.mark.parametrize("v", ["a\x00b", "a\nb", "a\rb", "a\tb", "a\x1fb", "a\x7fb", "a\u202eb", "a\u200bb", "a\u00a0b", "",
                               " CS 101", "CS 101 ", "CS  101", "x" * (runtime.BOUND_VALUE_MAX + 1)])
def test_a_bound_value_still_refuses_control_padding_empty_and_over_long(v):
    with pytest.raises(ValidationError, match='printable text|padding|at least 1 character|at most'):
        runtime.BoundInput.parse(_runtime_session_value(v))

@pytest.mark.parametrize("v", [None, 5, b"abc", ["a"]])
def test_the_renderer_quotes_text_only(v):
    with pytest.raises(ContractError, match="cannot quote a"):
        runtime.prolog_quote(v)

def test_the_value_cap_is_the_documented_default():
    assert runtime.BOUND_VALUE_MAX == 128

def test_the_longest_allowed_value_parses_and_renders():
    v = "x" * runtime.BOUND_VALUE_MAX
    assert runtime.BoundInput.parse(_runtime_session_value(v)).value == v
    assert unquote(runtime.prolog_quote(v)) == v

def test_the_predicate_name_rule_is_unchanged():
    for name in ("can_enroll", "a", "p2_check"):
        runtime.PredicateRequest.parse({"predicate": name, "inputs": []})
    for name in ("Can", "a b", "a-b", "a(", "_a", "1a", "a:-b", "a.", ""):
        with pytest.raises(ValidationError, match="String should match pattern '\\^\\[a\\-z\\]\\[a\\-z0\\-9_\\]\\*\\$"):
            runtime.PredicateRequest.parse({"predicate": name, "inputs": []})

def test_the_docs_say_data_not_cannot_carry_syntax():
    text = runtime.__doc__ + open(runtime.__file__, encoding="utf-8").read()
    assert "cannot carry Prolog" not in text
    assert "rendering must quote" in text


# Mutation regressions: vocabulary and bounds




VOC = base.VOCAB

def test_routes_and_controls_of_the_vocabulary_are_exactly_what_a_routing_decision_accepts():
    def decision(**over):
        return {"schema_version": "bintanong-routing-decision-v1", "route": None, "control": None, "confidence": None,
                "predicate_request": None, "required_facts": [], "missing_facts": [], "reason": "r", **over}
    pred = {"predicate": "can_enroll_fictional", "inputs": []}
    for route in VOC["runtime"]["routes"]:
        runtime.RoutingDecision.parse(decision(route=route, predicate_request=None if route == "RAG" else pred))
    for control in VOC["runtime"]["controls"]:
        runtime.RoutingDecision.parse(decision(control=control))
    for bad in ("Direct", "rag", "", "chat"):
        with pytest.raises(ValidationError, match='is not a route in the governance vocabulary'):
            runtime.RoutingDecision.parse(decision(route=bad))
        with pytest.raises(ValidationError, match='is not a control outcome in the governance vocabulary'):
            runtime.RoutingDecision.parse(decision(control=bad))
    assert not hasattr(runtime, "ROUTES") and not hasattr(runtime, "CONTROLS")


# Mutation regressions: field and relationship guards





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


# Mutation regressions: dates, identifiers and language markers




# 4. source.span_identity ignoring the text is covered in test_contracts_source.py

# 5. runtime._TIME_PHRASES lookbehind removed
@pytest.mark.parametrize("text", ["thislast year", "o'last year", "last 2last year", "elast year", "9last year"])
def test_a_time_phrase_must_start_at_a_word_boundary(text):
    assert runtime.time_phrases(text) == set()

def test_a_time_phrase_is_found_between_boundaries():
    assert runtime.time_phrases("Enrolled last year, again.") == {"last year"}
    assert runtime.time_phrases("(next semester)") == {"next semester"}
    assert runtime.time_phrases("last year's grades") == set()      # a possessive is another word
    assert runtime.time_phrases("last years") == set()
    assert runtime.time_phrases("ilast year") == set()

def test_a_word_that_merely_ends_in_a_time_phrase_is_not_one():
    assert runtime.time_phrases("blast year") == set()
    assert runtime.time_phrases("forecast year") == set()
    assert runtime.time_phrases("outlast year") == set()

# the vocabulary additions (owner-reviewable)
@pytest.mark.parametrize("text,found", [("nothing can be enrolled", {"nothing"}), ("Nobody passed", {"nobody"}),
                                        ("none of them", {"none"}), ("no, never", {"no", "never"})])
def test_the_negation_vocabulary_covers_nothing_nobody_and_none(text, found):
    assert runtime.negation_tokens(text) == found

def test_dropping_nobody_in_normalization_is_refused():
    q = {"schema_version": "bintanong-normalized-query-v1", "original_text": "Nobody enrolled last year",
         "normalized_text": "somebody enrolled last year", "language_hints": ["en"], "intent": None, "entities": [],
         "ambiguities": [], "negations": [], "time_qualifiers": [], "session_fact_refs": []}
    with pytest.raises(ValidationError, match="dropped the negation 'nobody'"):
        runtime.NormalizedQuery.parse(q)
    runtime.NormalizedQuery.parse({**q, "normalized_text": "nobody enrolled last year"})

def test_the_abbreviation_no_is_a_known_false_positive():
    # "Course No. 101" is read as a negation; a normalizer that expands it to "Number" is refused. Fail-safe,
    # reported to the owner, not special-cased here.
    assert runtime.negation_tokens("Course No. 101") == {"no"}
