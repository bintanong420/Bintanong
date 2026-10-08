"""Phase 1 Task 3, fix pass 2 (symbolic result, bundle, envelope).

Synthetic data only. Written red first (run against the pre-fix package in a scratch copy).
"""

from __future__ import annotations

import copy

import pytest
from pydantic import ValidationError

from backend.bintanong_contracts import answer, base, symbolic
import contracts_fixtures as fx
import test_contracts_answer as ta


def bad(cls, payload, match):
    with pytest.raises((ValidationError, base.ContractError), match=match or None):
        cls.parse(payload)


def sym(outcome="eligible", **over):
    return {**ta.symbolic(outcome), **over}


def result(outcome="eligible", **over):
    return symbolic.SymbolicResult.parse(sym(outcome, **over))


# ---------------------------------------------------------------- M-g: scope and rule spans
def test_a_decided_result_needs_its_scope_and_rule_spans():
    for outcome in ("eligible", "ineligible"):
        result(outcome)
        bad(symbolic.SymbolicResult, sym(outcome, scope=None), "needs its scope")
        bad(symbolic.SymbolicResult, sym(outcome, rule_spans=[]), "rule source spans")


def test_an_unsupported_or_error_result_has_no_scope_or_rule_spans_to_give():
    for outcome in ("unsupported", "error"):
        assert result(outcome).scope is None and result(outcome).rule_spans == ()
        bad(symbolic.SymbolicResult, sym(outcome, rule_spans=[fx.rule_span()]), "cannot cite rule source spans")
    result("unknown")                                              # scope is optional for an unknown outcome
    result("unknown", scope=fx.scope(), rule_spans=[fx.rule_span()])


def test_a_rule_span_must_be_anchored_versioned_and_carry_printed_text():
    for broken in ({"text": None}, {"text": "  "}, {"version_id": None}, {"page": None}):
        span = {**fx.rule_span(), **broken}
        bad(symbolic.SymbolicResult, sym(rule_spans=[span]), "rule span 0")
    bad(symbolic.SymbolicResult, sym(rule_spans=[{**fx.rule_span(), "byte_sha256": None, "version_id": None, "page": None,
                                                  "text": None}]), "rule span 0")


def test_the_scope_names_a_release_and_editions():
    for scope in ({**fx.scope(), "edition_ids": []}, {**fx.scope(), "edition_ids": ["doc-synth-handbook"]},
                  {**fx.scope(), "knowledge_release_id": "fact-synth-1"},
                  {**fx.scope(), "edition_ids": ["edition-synth-handbook-1", "edition-synth-handbook-1"]},
                  {**fx.scope(), "scope_ids": [""]}, {**fx.scope(), "extra": 1}):
        bad(symbolic.SymbolicResult, sym(scope=scope), "")
    result(scope={**fx.scope(), "scope_ids": ["program-synth-1"]})


def test_the_scope_and_rule_spans_roundtrip():
    r = result()
    assert symbolic.SymbolicResult.parse(base.canonical_json(r)) == r
    assert r.scope.edition_ids == ("edition-synth-handbook-1",)


# ---------------------------------------------------------------- M-k and M-a: private ids in a decision
VARIANTS = ["fact-synth-0001", "FACT-synth-0001", "fact-synth-0001 ", " fact-synth-0001", "fact-synth-0001\n", "ｆact-synth-0001",
            "fact‑synth-0001", "x/fact-synth-0001", "sess-synth-0001\t"]


@pytest.mark.parametrize("ref", VARIANTS)
def test_a_session_fact_id_in_the_evidence_refs_of_a_standalone_result_is_rejected(ref):
    d = {**ta.decision("eligible"), "evidence_refs": [ref]}
    bad(symbolic.SymbolicResult, sym(decision=d), "another namespace")


@pytest.mark.parametrize("field", ["satisfied_conditions", "evidence_refs"])
def test_a_private_id_in_any_decision_text_field_is_rejected(field):
    d = {**ta.decision("eligible"), field: ["fictional-prereq-met", "see fact-synth-0001"]}
    bad(symbolic.SymbolicResult, sym(decision=d), "another namespace")


@pytest.mark.parametrize("ref", VARIANTS)
def test_a_session_fact_id_in_the_decision_of_a_bundle_is_rejected(ref):
    b = ta.bundle()
    b["symbolic"]["decision"]["evidence_refs"] = [ref]
    bad(answer.EvidenceBundle, b, "another namespace")


def test_a_session_fact_id_in_a_rule_span_or_scope_is_rejected():
    b = ta.bundle()
    b["symbolic"]["rule_spans"][0]["text"] = "Rule text from fact-synth-0001"
    bad(answer.EvidenceBundle, b, "another namespace")
    b = ta.bundle()
    b["symbolic"]["scope"]["scope_ids"] = ["sess-synth-0001"]
    bad(answer.EvidenceBundle, b, "another namespace")


def test_the_input_fact_reference_itself_stays_legitimate():
    answer.EvidenceBundle.parse(ta.bundle())


def test_ordinary_prose_in_a_decision_is_not_a_private_id():
    d = {**ta.decision("eligible"), "satisfied_conditions": ["fact-checking passed", "edition-specific rule met"]}
    result(decision=d)


# ---------------------------------------------------------------- M-k: sessions and decided inputs
def test_session_facts_from_two_sessions_cannot_share_a_bundle():
    b = ta.bundle(facts=("user_confirmed", "user_confirmed"))
    b["session_facts"][1].update(fact_id="fact-synth-0002", session_id="sess-synth-0002")
    bad(answer.EvidenceBundle, b, "more than one session")
    b["session_facts"][1]["session_id"] = b["session_facts"][0]["session_id"]
    answer.EvidenceBundle.parse(b)


def test_a_decided_outcome_needs_inputs_and_each_input_needs_a_session_fact():
    b = ta.bundle()
    b["symbolic"]["inputs"] = []
    bad(answer.EvidenceBundle, b, "rests on no input")
    b = ta.bundle()
    b["symbolic"]["inputs"][0]["fact_ref"] = None
    bad(answer.EvidenceBundle, b, "cites no session fact")
    b = ta.bundle(outcome="ineligible", claims=("decision_ineligible",))
    b["symbolic"]["inputs"] = []
    bad(answer.EvidenceBundle, b, "rests on no input")
    # an unknown outcome may have no input at all
    b = ta.bundle(outcome="unknown", claims=("unknown_explanation",), facts=())
    b["symbolic"]["inputs"] = []
    answer.EvidenceBundle.parse(b)


# ---------------------------------------------------------------- M-i: the envelope
def test_an_answered_symbolic_or_hybrid_envelope_needs_a_citation():
    for route in ("Symbolic", "Hybrid"):
        answer.AnswerEnvelope.parse(ta.envelope(route=route, decision=ta.decision("eligible")))
        bad(answer.AnswerEnvelope, ta.envelope(route=route, decision=ta.decision("eligible"), citations=[]), "at least one citation")
    bad(answer.AnswerEnvelope, ta.envelope(citations=[]), "at least one citation")


def test_unsupported_unknown_and_error_may_cite_nothing():
    ok = {"passed": True, "checks": ["routing_checked"], "failures": []}
    for status, outcome in (("abstained", "unsupported"), ("abstained", "unknown"), ("clarification_needed", "unknown")):
        answer.AnswerEnvelope.parse(ta.envelope(status=status, route="Symbolic", decision=ta.decision(outcome), citations=[],
                                                validation=ok))
    answer.AnswerEnvelope.parse(ta.envelope(status="error", route="Symbolic", decision=ta.decision("error"), citations=[],
                                            validation={"passed": False, "checks": [], "failures": ["engine timeout"]}))
    answer.AnswerEnvelope.parse(ta.envelope(status="abstained", route=None, decision=None, citations=[], validation=ok))


def test_a_passed_validation_needs_a_check_that_ran():
    answer.ValidationResult.parse({"passed": True, "checks": ["c"], "failures": []})
    answer.ValidationResult.parse({"passed": False, "checks": [], "failures": ["f"]})
    bad(answer.ValidationResult, {"passed": True, "checks": [], "failures": []}, "at least one check")
    bad(answer.ValidationResult, {"passed": True, "checks": ["c"], "failures": ["f"]}, "exactly when")
    bad(answer.ValidationResult, {"passed": False, "checks": ["c"], "failures": []}, "exactly when")
    bad(answer.AnswerEnvelope, ta.envelope(validation={"passed": True, "checks": [], "failures": []}), "at least one check")


# ---------------------------------------------------------------- M-a: the envelope text, citations and decision
@pytest.mark.parametrize("ref", VARIANTS)
def test_a_private_id_in_the_answer_text_is_rejected(ref):
    bad(answer.AnswerEnvelope, ta.envelope(text=f"Your record {ref} says so."), "another namespace|private id")


@pytest.mark.parametrize("ref", VARIANTS)
def test_a_private_id_in_a_citation_or_decision_of_an_envelope_is_rejected(ref):
    bad(answer.AnswerEnvelope, ta.envelope(citations=[{**ta.cite(), "locator_ref": ref}]), "private id")
    bad(answer.AnswerEnvelope, ta.envelope(route="Hybrid", decision={**ta.decision("eligible"), "evidence_refs": [ref]}), "private id")


def test_ordinary_answer_prose_is_not_flagged():
    answer.AnswerEnvelope.parse(ta.envelope(text="Fact-checking is done by the Registrar; edition-specific rules apply."))


# ---------------------------------------------------------------- M-m: the register check inside the bundle path
def test_a_bundle_rejects_a_retrieved_chunk_that_claims_more_than_its_register_version():
    b = ta.bundle(route="RAG", sym=False, facts=(), claims=("policy_passage",))
    b["retrieval"]["items"][0]["chunk"]["source_verification"] = "verified"
    bad(answer.EvidenceBundle, b, "stale or inflated verification claim")


def test_a_bundle_rejects_a_retrieval_without_its_register_versions():
    b = ta.bundle(route="RAG", sym=False, facts=(), claims=("policy_passage",))
    b["retrieval"]["versions"] = []
    bad(answer.EvidenceBundle, b, "not in the result's versions")


# ---------------------------------------------------------------- M-g: a section locator can be cited
def test_a_citation_can_name_a_section_locator():
    b = ta.bundle(route="RAG", sym=False, facts=(), claims=("policy_passage",))
    chunk = b["retrieval"]["items"][0]["chunk"]
    chunk["spans"][0]["locator"] = {"kind": "section", "table_index": None, "cell_ids": [], "item_ids": [], "ref": None,
                                    "section_path": ["Part I", "Admission"]}
    bundle = answer.EvidenceBundle.parse(b)
    cite = {**ta.cite(), "locator_ref": "Part I/Admission"}
    env = answer.AnswerEnvelope.parse(ta.envelope(citations=[cite]))
    answer.check_envelope_against_bundle(env, bundle)
    other = answer.AnswerEnvelope.parse(ta.envelope(citations=[{**cite, "locator_ref": "Part II"}]))
    with pytest.raises(base.ContractError, match="page or locator"):
        answer.check_envelope_against_bundle(other, bundle)
