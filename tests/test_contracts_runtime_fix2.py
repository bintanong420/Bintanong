"""Phase 1 Task 3, fix pass 2 (runtime): queries, goals, retrieval consistency and the register path.

Synthetic data only. Written red first (run against the pre-fix package in a scratch copy).
"""

from __future__ import annotations

import copy

import pytest
from pydantic import ValidationError

from backend.bintanong_contracts import base, runtime, symbolic
import contracts_fixtures as fx
import test_contracts_runtime as rt


def bad(cls, payload, match):
    with pytest.raises((ValidationError, base.ContractError), match=match):
        cls.parse(payload)


# ---------------------------------------------------------------- M-h: negations and time qualifiers
def query(original, normalized, **over):
    return rt.query(original_text=original, normalized_text=normalized, negations=[], time_qualifiers=[],
                    session_fact_refs=[], **over)


def test_a_dropped_negation_is_rejected_even_when_none_was_declared():
    bad(runtime.NormalizedQuery, query("I did not pass CS 101", "i did pass cs 101"), "dropped the negation 'not'")
    bad(runtime.NormalizedQuery, query("Hindi ako pumasa sa CS 101", "ako pumasa sa cs 101"), "dropped the negation 'hindi'")
    bad(runtime.NormalizedQuery, query("walang prereq ba?", "prereq ba?"), "dropped the negation 'walang'")
    bad(runtime.NormalizedQuery, query("Can I enroll without a prerequisite?", "can i enroll a prerequisite?"), "without")


def test_a_negation_that_survives_is_accepted():
    runtime.NormalizedQuery.parse(query("I did NOT pass CS 101", "i did not pass cs 101"))
    runtime.NormalizedQuery.parse(query("Hindi ako pumasa", "hindi ako pumasa"))


def test_a_contraction_counts_as_not_and_may_be_expanded():
    runtime.NormalizedQuery.parse(query("I don't have a grade", "i do not have a grade"))
    runtime.NormalizedQuery.parse(query("I don’t have a grade", "i don't have a grade"))
    bad(runtime.NormalizedQuery, query("I can't enroll", "i can enroll"), "dropped the negation 'not'")


def test_an_apostrophe_negation_in_tagalog_is_found():
    bad(runtime.NormalizedQuery, query("'di ako pumasa", "ako pumasa"), "dropped the negation 'di'")
    bad(runtime.NormalizedQuery, query("'wag muna", "muna"), "dropped the negation 'wag'")


def test_an_added_negation_is_rejected():
    bad(runtime.NormalizedQuery, query("I passed CS 101", "i did not pass cs 101"), "added the negation 'not'")


def test_a_word_that_merely_contains_a_negation_is_not_one():
    runtime.NormalizedQuery.parse(query("Is there a knot or notice for CS 101?", "is there a knot or notice for cs 101?"))
    runtime.NormalizedQuery.parse(query("What is the nothing-rule?", "what is the nothing-rule?"))


def test_a_dropped_or_added_time_qualifier_is_rejected():
    bad(runtime.NormalizedQuery, query("What can I take next sem?", "what can i take?"), "dropped the time qualifier 'next sem'")
    bad(runtime.NormalizedQuery, query("Pwede ba noong last semester?", "pwede ba last semester?"), "dropped the time qualifier 'noong'")
    bad(runtime.NormalizedQuery, query("Ano ang kukunin sa susunod? sa susunod na term", "ano ang kukunin?"), "time qualifier")
    bad(runtime.NormalizedQuery, query("What can I take?", "what can i take next semester?"), "added the time qualifier 'next semester'")
    runtime.NormalizedQuery.parse(query("What can I take Next Sem?", "what can i take next sem?"))
    runtime.NormalizedQuery.parse(query("What is the next semester fee?", "what is the next semester fee?"))


def test_a_time_phrase_inside_a_longer_word_is_not_a_qualifier():
    runtime.NormalizedQuery.parse(query("The bukasan rules", "the rules"))


def test_declared_markers_must_still_be_in_the_normalized_text():
    bad(runtime.NormalizedQuery, rt.query(negations=["not"]), "dropped")
    bad(runtime.NormalizedQuery, rt.query(time_qualifiers=["next semester"]), "dropped")


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
    d = copy.deepcopy(rt_decision())
    d["predicate"] = name
    bad(symbolic.DecisionOutcome, d, "predicate|String")
    bad(runtime.PredicateRequest, {"predicate": name, "inputs": []}, "predicate|String")


def rt_decision():
    import json
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    return json.loads((root / "knowledge/manifests/examples/synthetic-decisions.json").read_text(encoding="utf-8"))[0]


def test_a_decision_predicate_identifier_is_accepted():
    d = rt_decision()
    for name in ("can_enroll_fictional", "a", "x" * 64, "p2_check"):
        symbolic.DecisionOutcome.parse({**d, "predicate": name})


def value(v):
    return {"name": "course", "value": v, "fact_ref": None}


@pytest.mark.parametrize("v", [" CS 101", "CS 101 ", "CS  101", "a\x00b", "a\tb", "a\x1fb", "a‮b", "a\nb", ""])
def test_a_bound_value_refuses_padding_control_characters_and_empty_text(v):
    with pytest.raises(ValidationError, match='printable text|padding|at least 1 character'):
        runtime.BoundInput.parse(value(v))


@pytest.mark.parametrize("v", ["X", "Course", "_", "_foo", "Y1", "CS101", "MATH101", "A_B", "is", "IS", "mod", "rem", "div", "xor",
                               "-", "/", "--", "..", ".5", "x), halt(", "x :- true", "a;b", "a'b"])
def test_a_bound_value_is_data_so_prolog_looking_text_is_accepted_and_must_be_quoted(v):
    assert runtime.BoundInput.parse(value(v)).value == v
    assert runtime.prolog_quote(v).startswith("'") and runtime.prolog_quote(v).endswith("'")


@pytest.mark.parametrize("v", ["CS 101", "ITEC 101", "FICTIONAL-101", "1.75", "2018-2019", "cs101", "cs 101", "Intro to Computing",
                               "BS Computer Science", "a_b c", "Section 2B", "3"])
def test_ordinary_values_and_course_codes_with_a_separator_are_accepted(v):
    runtime.BoundInput.parse(value(v))


def test_the_bound_value_comment_makes_no_false_claim():
    comment = runtime.__doc__ + open(runtime.__file__, encoding="utf-8").read()
    assert "no full stops" not in comment.lower()


# ---------------------------------------------------------------- M-e: the retrieval configuration
@pytest.mark.parametrize("revision", [" main", "main\n", "refs/heads/main", "origin/main", "v1", "stable", "nightly", "x", "main",
                                      "master", "r1" + "0" * 38, fx.REVISION.upper(), fx.REVISION[:-1], ""])
def test_the_retrieval_config_needs_a_pinned_revision(revision):
    r = fx.retrieval()
    r["config"]["embedding_model_revision"] = revision
    bad(runtime.RetrievalResult, r, "pinned|embedding_model_revision")


def test_a_full_commit_or_digest_is_accepted_by_the_config():
    for revision in (fx.REVISION, "f" * 64):
        r = fx.retrieval()
        r["config"]["embedding_model_revision"] = revision
        runtime.RetrievalResult.parse(r)


# ---------------------------------------------------------------- RoutingDecision
def test_a_blank_reason_is_rejected():
    for reason in ("   ", "\t\n"):
        bad(runtime.RoutingDecision, rt.routing(reason=reason), "reason")


# ---------------------------------------------------------------- M-l: retrieval consistency
def rbad(items, match, **over):
    bad(runtime.RetrievalResult, fx.retrieval(items, **over), match)


def test_the_same_bytes_under_two_editions_or_versions_are_rejected():
    a = fx.item(1, 1, 0.9, edition="1")
    b = fx.item(2, 2, 0.8, edition="1", doc="doc-other")
    b["chunk"].update(edition_id="edition-synth-handbook-9", version_id="ver-synth-handbook-9")
    for s in b["chunk"]["spans"]:
        s["version_id"] = "ver-synth-handbook-9"
    rbad([a, b], "same bytes")


def test_the_same_edition_over_different_bytes_under_different_documents_is_rejected():
    a = fx.item(1, 1, 0.9, edition="1")
    b = fx.item(2, 2, 0.8, edition="2", doc="doc-other")
    b["chunk"]["edition_id"] = "edition-synth-handbook-1"
    rbad([a, b], "edition")


def test_two_editions_of_one_document_are_still_rejected():
    rbad([fx.item(1, 1, 0.9, edition="1"), fx.item(2, 2, 0.8, edition="2")], "more than one edition")


def test_chunker_versions_in_one_result_stay_a_strict_default():
    rbad([fx.item(1, 1, 0.9), fx.item(2, 2, 0.8, chunker="palsu-chunker-v2")], "chunker versions")


# ---------------------------------------------------------------- M-m: the register check runs inside the result
def test_a_result_needs_the_register_versions_its_chunks_cite():
    r = fx.retrieval()
    r["versions"] = []
    bad(runtime.RetrievalResult, r, "not in the result's versions")
    r = fx.retrieval()
    r["versions"] = r["versions"] + [fx.version_for({**fx.item(2, edition="2")["chunk"]})]
    bad(runtime.RetrievalResult, r, "no chunk cites it")


def test_a_chunk_claiming_more_than_its_register_version_is_rejected_inside_the_result():
    it = fx.item(1)
    it["chunk"]["source_verification"] = "verified"
    rbad([it], "stale or inflated verification claim")


def test_a_chunk_citing_other_register_evidence_is_rejected_inside_the_result():
    it = fx.item(1)
    it["chunk"]["register_binding"]["verification_evidence_ref"] = "ev-forged"
    rbad([it], "evidence reference")


def test_a_chunk_whose_bytes_differ_from_the_register_is_rejected_inside_the_result():
    r = fx.retrieval()
    r["versions"][0]["byte_sha256"] = "9" * 64
    bad(runtime.RetrievalResult, r, "digest")


def test_the_registers_own_consistency_is_checked_inside_the_result():
    r = fx.retrieval([fx.item(1, 1, 0.9, edition="1"), fx.item(2, 2, 0.8, edition="1", doc="doc-other")])
    r["versions"].append(copy.deepcopy(r["versions"][0]))
    bad(runtime.RetrievalResult, r, "duplicate version_id")


def test_an_honest_result_with_two_documents_is_accepted():
    r = runtime.RetrievalResult.parse(fx.retrieval([fx.item(1, 1, 0.9, doc="doc-a"), fx.item(2, 2, 0.8, doc="doc-b", edition="2")]))
    assert len(r.versions) == 2
