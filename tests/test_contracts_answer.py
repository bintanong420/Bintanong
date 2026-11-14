"""Answer envelopes and evidence bundles: schema, provenance and mutation regressions."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from backend.bintanong_contracts import answer
from backend.bintanong_contracts import base
from backend.bintanong_contracts import symbolic as symbolic_contracts

import contracts_fixtures as fx


ROOT = Path(__file__).resolve().parents[1]
EX = ROOT / "knowledge" / "manifests" / "examples"
DEC = {d["outcome"]: d for d in json.loads((EX / "synthetic-decisions.json").read_text(encoding="utf-8"))}


def decision(outcome, synthetic=False, **over):
    d = {**copy.deepcopy(DEC[outcome]), "synthetic": synthetic}
    d.update(over)
    return d


def symbolic(outcome="eligible", capability="enrollment_eligibility", fact_ref="fact-synth-0001", **dec):
    d = decision(outcome, **dec)
    has_rules = outcome in ("eligible", "ineligible")
    return {"schema_version": "bintanong-symbolic-result-v1", "decision": d, "capability": capability,
            "inputs": [{"name": "course", "value": "FICTIONAL-101", "fact_ref": fact_ref}],
            "rule_ids": ["rule-synth-1"] if has_rules else [],
            "rule_bundle_version": "bundle-synth-1" if has_rules else None, **fx.decided_extras(outcome)}


def fact(state="user_confirmed", fact_id="fact-synth-0001"):
    f = json.loads((EX / "synthetic-session-fact.json").read_text(encoding="utf-8"))
    f["fact_id"] = fact_id
    if state != "unconfirmed":
        f["evidence"] = [{"evidence_id": "ev-u", "kind": "user_confirmation", "recorded_by": "user",
                          "recorded_at": "2026-01-01T00:00:00+00:00"}]
        f.update(confirmation_state=state, confirmation_evidence_ref="ev-u")
    return f


def conflict(capability="enrollment_eligibility", resolved=False):
    c = json.loads((EX / "synthetic-conflict.json").read_text(encoding="utf-8"))
    c["affected_scope"]["capability"] = capability
    if resolved:
        c["evidence"] = [{"evidence_id": "ev-r", "kind": "issuing_office_resolution", "recorded_by": "issuing_office",
                          "recorded_at": "2026-01-01T00:00:00+00:00"}]
        c.update(resolution_state="resolved", resolution_evidence_ref="ev-r", resolution_basis="source_owner_ruling")
    return c


def bundle(route="Hybrid", outcome="eligible", claims=("decision_eligible", "policy_passage"), retrieval=True,
           sym=True, facts=(("user_confirmed",)), conflicts=(), **over):
    d = {"schema_version": "bintanong-evidence-bundle-v1", "request_id": "req-synth-1", "route": route,
         "knowledge_release_id": "release-synth-1",
         "retrieval": fx.retrieval() if retrieval else None,
         "symbolic": symbolic(outcome) if sym else None,
         "session_facts": [fact(s) for s in facts], "conflicts": list(conflicts),
         "permitted_claims": list(claims)}
    d.update(over)
    return d


def bad(cls, payload, match):
    """The payload must be rejected, and for the stated reason."""
    with pytest.raises((ValidationError, base.ContractError), match=match):
        cls.parse(payload)


def bbad(match, **kw):
    bad(answer.EvidenceBundle, bundle(**kw), match)


# ---------------------------------------------------------------- EvidenceBundle
def test_valid_bundles_roundtrip():
    for b in (bundle(),
              bundle(route="RAG", sym=False, facts=(), claims=("policy_passage",)),
              bundle(route="Symbolic", retrieval=False, claims=("decision_eligible",),
                     versions=fx.versions_for([fx.item()]))):
        m = answer.EvidenceBundle.parse(b)
        assert answer.EvidenceBundle.parse(base.canonical_json(m)) == m


@pytest.mark.parametrize("kw,match", [
    (dict(route="RAG", sym=True), "RAG bundle needs retrieval and carries no symbolic result"),                         # RAG carries no symbolic result
    (dict(route="Symbolic", sym=False), "needs a symbolic result"),
    (dict(route="Hybrid", sym=False), "needs both retrieval and a symbolic result"),                     # partial Hybrid: symbolic half missing
    (dict(route="Hybrid", retrieval=False), "needs both retrieval and a symbolic result"),               # partial Hybrid: retrieval half missing
    (dict(route="Direct"), "not a route"), (dict(route=None), "route"),
    (dict(knowledge_release_id="release-synth-2"), "different knowledge release"),        # stale release against the retrieval
    (dict(request_id="fact-synth-1"), "request_id"), (dict(request_id=""), "request_id"),
    (dict(unknown=1), "unknown"), (dict(approved=True), "approved"),
])
def test_route_and_content_must_agree(kw, match):
    bbad(match, **kw)


@pytest.mark.parametrize("outcome,claims,ok", [
    ("eligible", ("decision_eligible",), True),
    ("eligible", ("decision_eligible", "policy_passage"), True),
    ("eligible", ("decision_ineligible",), False),
    ("eligible", ("unknown_explanation",), False),
    ("ineligible", ("decision_ineligible", "policy_passage"), True),
    ("ineligible", ("decision_eligible",), False),
    ("unknown", ("unknown_explanation",), True),
    ("unknown", ("abstention",), True),
    ("unknown", ("decision_eligible",), False),
    ("unknown", ("policy_passage",), False),             # an explanation cannot stand in for a missing decision
    ("unsupported", ("abstention",), True),
    ("unsupported", ("policy_passage",), False),
    ("unsupported", ("decision_eligible",), False),
    ("error", ("error_report",), True),
    ("error", ("policy_passage",), False),               # RAG explanation cannot satisfy a failed symbolic part
    ("error", ("abstention",), False),
    ("error", ("decision_eligible",), False),
    ("error", ("decision_ineligible",), False),
    ("eligible", ("decision_eligible", "decision_eligible"), False),
    ("eligible", ("approved",), False),
    ("eligible", ("decision_eligible", "abstention"), False),
])
def test_permitted_claims_follow_the_symbolic_outcome(outcome, claims, ok):
    def build():
        return answer.EvidenceBundle.parse(bundle(outcome=outcome, claims=claims))
    if ok:
        build()
    else:
        with pytest.raises((ValidationError, base.ContractError), match="not permitted for a|duplicate claims"):
            build()


def test_rag_claims_need_retrieved_passages():
    answer.EvidenceBundle.parse(bundle(route="RAG", sym=False, facts=(), claims=("policy_passage",)))
    empty = fx.retrieval([], coverage="none")
    bbad("needs retrieval", route="RAG", sym=False, facts=(), claims=("policy_passage",), retrieval=None)
    bad(answer.EvidenceBundle, bundle(route="RAG", sym=False, facts=(), claims=("policy_passage",), retrieval=None)
        | {"retrieval": empty}, "policy_passage needs retrieved passages")
    answer.EvidenceBundle.parse(bundle(route="RAG", sym=False, facts=(), claims=("abstention",))
                                | {"retrieval": empty})


def test_private_facts_back_a_decision_only_when_the_student_confirmed_them():
    answer.EvidenceBundle.parse(bundle(facts=("user_confirmed",)))
    for state in ("unconfirmed", "user_rejected"):
        bbad("unconfirmed fact|the student rejected", facts=(state,))
    # a rejected fact poisons even an unknown outcome that uses it as an input
    bbad("the student rejected", outcome="unknown", claims=("unknown_explanation",), facts=("user_rejected",))
    # an unconfirmed fact may be present while the system only abstains or explains unknown
    answer.EvidenceBundle.parse(bundle(outcome="unknown", claims=("unknown_explanation",), facts=("unconfirmed",)))


def test_symbolic_inputs_must_cite_a_session_fact_that_is_in_the_bundle():
    bbad("that is not in the bundle", facts=())
    bbad("that is not in the bundle", facts=("user_confirmed",), sym=True, **{"symbolic": symbolic(fact_ref="fact-other-0002")})


def test_duplicate_session_fact_ids_are_rejected():
    b = bundle()
    b["session_facts"].append(copy.deepcopy(b["session_facts"][0]))
    bad(answer.EvidenceBundle, b, "duplicate session fact ids")


def test_private_ids_never_appear_in_institutional_parts():
    b = bundle()
    b["symbolic"]["decision"]["evidence_refs"] = ["fact-synth-0001"]         # a private fact cited as a rule source
    bad(answer.EvidenceBundle, b, "another namespace")
    b = bundle()
    b["symbolic"]["rule_ids"] = ["sess-synth-1"]
    bad(answer.EvidenceBundle, b, "another namespace")


def test_a_session_fact_is_not_a_conflict_or_a_source_and_cannot_be_promoted():
    b = bundle()
    b["conflicts"] = [fact()]                      # a private fact where an institutional conflict belongs
    bad(answer.EvidenceBundle, b, "conflicts")
    b = bundle()
    b["retrieval"]["items"][0]["chunk"]["source_label"] = "fact-synth-0001"   # copied into an institutional chunk
    bad(answer.EvidenceBundle, b, "another namespace")


def test_an_unresolved_conflict_blocks_a_decision_in_its_capability_only():
    blocking = conflict("enrollment_eligibility")
    other = conflict("grade_computation")
    answer.EvidenceBundle.parse(bundle(conflicts=[other]))                      # unrelated capability stays open
    answer.EvidenceBundle.parse(bundle(conflicts=[conflict("enrollment_eligibility", resolved=True)]))
    bbad("blocks capability", conflicts=[blocking])                                                  # eligible despite the conflict
    ok = bundle(outcome="unknown", claims=("unknown_explanation",), conflicts=[blocking])
    ok["symbolic"]["decision"].update(unresolved_conflicts=["conflict-synth-0001"], rule_coverage="partial")
    answer.EvidenceBundle.parse(ok)
    stray = bundle(outcome="unknown", claims=("unknown_explanation",))
    stray["symbolic"]["decision"].update(unresolved_conflicts=["conflict-synth-0099"])
    bad(answer.EvidenceBundle, stray, "that is not in the bundle")                                           # cites a conflict not in the bundle


def test_a_synthetic_decision_establishes_no_claim():
    b = bundle()
    b["symbolic"]["decision"]["synthetic"] = True
    bad(answer.EvidenceBundle, b, "establishes no claim")
    b = bundle(route="Symbolic", retrieval=False, outcome="unsupported", claims=("abstention",))
    b["symbolic"]["decision"]["synthetic"] = True
    answer.EvidenceBundle.parse(b)


# ---------------------------------------------------------------- AnswerEnvelope
def cite(n=1):
    c = fx.chunk(n)
    return {"chunk_id": c.chunk_id, "byte_sha256": c.byte_sha256, "version_id": c.version_id, "page": 1,
            "locator_ref": f"t0-c{n}"}


def envelope(**over):
    d = {"schema_version": "bintanong-answer-envelope-v1", "request_id": "req-synth-1", "status": "answered",
         "language": "en", "text": "Synthetic answer text.", "route": "RAG", "decision": None,
         "citations": [cite()], "validation": {"passed": True, "checks": ["citations_resolve"], "failures": []}}
    d.update(over)
    return d


def ebad(match, **over):
    bad(answer.AnswerEnvelope, envelope(**over), match)


def test_envelope_roundtrips():
    for e in (envelope(),
              envelope(route="Symbolic", decision=decision("eligible")),
              envelope(status="abstained", route=None, citations=[], decision=None),
              envelope(status="error", route="Symbolic", decision=decision("error"), citations=[],
                       validation={"passed": False, "checks": [], "failures": ["engine timeout"]})):
        m = answer.AnswerEnvelope.parse(e)
        assert answer.AnswerEnvelope.parse(base.canonical_json(m)) == m


@pytest.mark.parametrize("status,outcome,ok", [
    ("answered", "eligible", True), ("answered", "ineligible", True),
    ("answered", "unknown", False), ("answered", "unsupported", False), ("answered", "error", False),
    ("clarification_needed", "unknown", True), ("clarification_needed", "eligible", False),
    ("clarification_needed", "error", False),
    ("abstained", "unknown", True), ("abstained", "unsupported", True),
    ("abstained", "eligible", False), ("abstained", "ineligible", False), ("abstained", "error", False),
    ("error", "error", True), ("error", "unknown", False), ("error", "unsupported", False),
    ("error", "eligible", False), ("error", "ineligible", False),
])
def test_status_follows_the_decision_outcome_and_error_never_becomes_a_verdict(status, outcome, ok):
    passed = status == "answered"
    e = envelope(status=status, route="Symbolic", decision=decision(outcome), citations=[cite()] if passed else [],
                 validation={"passed": passed, "checks": ["c1"] if passed else [], "failures": [] if passed else ["x"]})
    if ok:
        answer.AnswerEnvelope.parse(e)
    else:
        bad(answer.AnswerEnvelope, e, "cannot carry a")


@pytest.mark.parametrize("over,match", [
    (dict(status="approved"), "status"), (dict(status="denied"), "status"), (dict(status="eligible"), "status"),
    (dict(language="de"), "language"), (dict(text=""), "text"), (dict(request_id="fact-1"), "request_id"),
    (dict(route="Direct"), "not a route"),
    (dict(validation={"passed": False, "checks": [], "failures": ["x"]}), "needs a passed validation"),            # answered but validation failed
    (dict(validation={"passed": True, "checks": ["c1"], "failures": ["x"]}), "exactly when"),             # passed with failures
    (dict(validation={"passed": False, "checks": [], "failures": []}), "exactly when"),               # failed with no reason
    (dict(route=None), "needs a route"),                                                                # answered needs a route
    (dict(citations=[]), "at least one citation"),                                                              # RAG answer needs a citation
    (dict(decision=decision("eligible")), "structured decision needs a Symbolic or Hybrid route"),                                             # RAG answer carries no decision
    (dict(citations=[{**cite(), "chunk_id": "nothex"}]), "chunk_id"),
    (dict(citations=[{**cite(), "version_id": "fact-synth-0001"}]), "version_id"),
    (dict(citations=[{**cite(), "locator_ref": "fact-synth-0001"}]), "private id"),
    (dict(citations=[{**cite(), "page": 0}]), "page"),
    (dict(citations=[cite(), cite()]), "duplicate citation"),                                                # duplicate citation
    (dict(unknown=1), "unknown"), (dict(approval_id="x"), "approval_id"),
])
def test_malformed_or_contradictory_envelopes_are_rejected(over, match):
    ebad(match, **over)


def test_hybrid_answer_needs_its_symbolic_decision_not_just_passages():
    ebad("needs its symbolic decision", route="Hybrid", decision=None)                                        # RAG-style passages alone
    answer.AnswerEnvelope.parse(envelope(route="Hybrid", decision=decision("eligible")))
    ebad("cannot carry a", route="Hybrid", decision=decision("error"))                           # passages cannot rescue a failed half
    ebad("needs its symbolic decision", route="Symbolic", decision=None, citations=[])


def test_abstention_and_clarification_may_not_assert_a_decision_verdict():
    answer.AnswerEnvelope.parse(envelope(status="clarification_needed", route="Symbolic", decision=decision("unknown"),
                                         citations=[], validation={"passed": True, "checks": ["c1"], "failures": []}))
    ebad("an error cites nothing", status="error", route="RAG", citations=[cite()])                       # an error cites nothing


# ---------------------------------------------------------------- envelope vs bundle
def test_envelope_must_match_its_evidence_bundle():
    b = answer.EvidenceBundle.parse(bundle())
    e = answer.AnswerEnvelope.parse(envelope(route="Hybrid", decision=decision("eligible"), citations=[cite()]))
    answer.check_envelope_against_bundle(e, b)
    cases = [
        envelope(route="Hybrid", decision=decision("eligible"), request_id="req-other"),
        envelope(route="Symbolic", decision=decision("eligible")),
        envelope(route="Hybrid", decision=decision("ineligible", evidence_refs=["x"])),
        envelope(route="Hybrid", decision=decision("eligible"), citations=[cite(7)]),      # not retrieved
        envelope(route="Hybrid", decision=decision("eligible"), citations=[{**cite(), "byte_sha256": "9" * 64}]),
    ]
    for c in cases:
        with pytest.raises(base.ContractError, match='differs|not permitted|do not include|was not retrieved|names other|names a page'):
            answer.check_envelope_against_bundle(answer.AnswerEnvelope.parse(c), b)


def test_an_answer_needs_permitting_claims():
    no_claims = answer.EvidenceBundle.parse(bundle(claims=()))
    e = answer.AnswerEnvelope.parse(envelope(route="Hybrid", decision=decision("eligible")))
    with pytest.raises(base.ContractError, match="permitted"):
        answer.check_envelope_against_bundle(e, no_claims)
    only_decision = answer.EvidenceBundle.parse(bundle(claims=("decision_eligible",)))
    with_citation = answer.AnswerEnvelope.parse(envelope(route="Hybrid", decision=decision("eligible")))
    with pytest.raises(base.ContractError, match="permitted"):
        answer.check_envelope_against_bundle(with_citation, only_decision)


# ---------------------------------------------------------------- mutation-driven additions
def test_symbolic_route_needs_a_symbolic_result_whatever_the_claims():
    bbad("needs a symbolic result", route="Symbolic", sym=False, retrieval=False, facts=(), claims=())
    bbad("needs a symbolic result", route="Symbolic", sym=False, facts=(), claims=())


def test_without_a_symbolic_result_no_decision_claim_and_no_mixed_abstention():
    bbad("only policy_passage and abstention", route="RAG", sym=False, facts=(), claims=("decision_eligible",))
    bbad("only policy_passage and abstention", route="RAG", sym=False, facts=(), claims=("bogus",))
    bbad("abstention cannot be combined", route="RAG", sym=False, facts=(), claims=("policy_passage", "abstention"))


def test_an_unknown_outcome_in_a_blocked_capability_must_list_the_blocking_conflict():
    blocking = conflict("enrollment_eligibility")
    b = bundle(outcome="unknown", claims=("unknown_explanation",), conflicts=[blocking])
    b["symbolic"]["decision"].update(rule_coverage="partial")     # does not list conflict-synth-0001
    bad(answer.EvidenceBundle, b, "must list the blocking conflict")


def test_a_decision_needs_a_symbolic_or_hybrid_route():
    ebad("needs a Symbolic or Hybrid route", status="clarification_needed", route=None, decision=decision("unknown"), citations=[])
    ebad("needs a Symbolic or Hybrid route", status="answered", route="RAG", decision=decision("eligible"))


def test_an_error_envelope_cites_nothing_and_never_passes_validation():
    err = dict(status="error", route="Symbolic", decision=decision("error"))
    answer.AnswerEnvelope.parse(envelope(**err, citations=[], validation={"passed": False, "checks": [], "failures": ["x"]}))
    ebad("an error cites nothing", **err, citations=[cite()], validation={"passed": False, "checks": [], "failures": ["x"]})
    ebad("cannot carry a passed validation", **err, citations=[], validation={"passed": True, "checks": ["c1"], "failures": []})


def _hybrid_pair(**env_over):
    b = answer.EvidenceBundle.parse(bundle())
    e = answer.AnswerEnvelope.parse(envelope(route="Hybrid", decision=decision("eligible"), citations=[cite()], **env_over))
    return e, b


def test_each_envelope_bundle_mismatch_is_named():
    cases = [
        (dict(request_id="req-other"), "request id"),
        (dict(route="Symbolic"), "route"),
        (dict(decision=decision("eligible", evidence_refs=["other-span"])), "decision differs"),
        (dict(citations=[cite(7)]), "was not retrieved"),
        (dict(citations=[{**cite(), "byte_sha256": "9" * 64}]), "other bytes or version"),
        (dict(citations=[{**cite(), "page": 2}]), "page or locator"),
        (dict(citations=[{**cite(), "locator_ref": "t0-c9"}]), "page or locator"),
    ]
    for over, text in cases:
        e, b = _hybrid_pair()
        e = answer.AnswerEnvelope.parse({**json.loads(base.canonical_json(e)), **json.loads(json.dumps(over))})
        with pytest.raises(base.ContractError, match=text):
            answer.check_envelope_against_bundle(e, b)


def test_abstention_needs_a_claim_that_allows_it():
    b = answer.EvidenceBundle.parse(bundle(route="Symbolic", retrieval=False, outcome="unsupported", claims=("abstention",)))
    ok = answer.AnswerEnvelope.parse(envelope(status="abstained", route="Symbolic", decision=decision("unsupported"),
                                              citations=[], validation={"passed": True, "checks": ["c1"], "failures": []}))
    answer.check_envelope_against_bundle(ok, b)
    none = answer.EvidenceBundle.parse(bundle(route="Symbolic", retrieval=False, outcome="unsupported", claims=()))
    with pytest.raises(base.ContractError, match="do not allow status"):
        answer.check_envelope_against_bundle(ok, none)


# Decision scope and evidence consistency
_answer_bundle = bundle
_answer_cite = cite




def _reject_symbolic_or_answer(cls, payload, match):
    with pytest.raises((ValidationError, base.ContractError), match=match or None):
        cls.parse(payload)

def _symbolic_payload(outcome="eligible", **over):
    return {**symbolic(outcome), **over}

def _symbolic_result(outcome="eligible", **over):
    return symbolic_contracts.SymbolicResult.parse(_symbolic_payload(outcome, **over))

# ---------------------------------------------------------------- M-g: scope and rule spans
def test_a_decided_result_needs_its_scope_and_rule_spans():
    for outcome in ("eligible", "ineligible"):
        _symbolic_result(outcome)
        _reject_symbolic_or_answer(symbolic_contracts.SymbolicResult, _symbolic_payload(outcome, scope=None), "needs its scope")
        _reject_symbolic_or_answer(symbolic_contracts.SymbolicResult, _symbolic_payload(outcome, rule_spans=[]), "rule source spans")

def test_an_unsupported_or_error_result_has_no_scope_or_rule_spans_to_give():
    for outcome in ("unsupported", "error"):
        assert _symbolic_result(outcome).scope is None and _symbolic_result(outcome).rule_spans == ()
        _reject_symbolic_or_answer(symbolic_contracts.SymbolicResult, _symbolic_payload(outcome, rule_spans=[fx.rule_span()]), "cannot cite rule source spans")
    _symbolic_result("unknown")                                              # scope is optional for an unknown outcome
    _symbolic_result("unknown", scope=fx.scope(), rule_spans=[fx.rule_span()])

def test_a_rule_span_must_be_anchored_versioned_and_carry_printed_text():
    for broken in ({"text": None}, {"text": "  "}, {"version_id": None}, {"page": None}):
        span = {**fx.rule_span(), **broken}
        _reject_symbolic_or_answer(symbolic_contracts.SymbolicResult, _symbolic_payload(rule_spans=[span]), "rule span 0")
    _reject_symbolic_or_answer(symbolic_contracts.SymbolicResult, _symbolic_payload(rule_spans=[{**fx.rule_span(), "byte_sha256": None, "version_id": None, "page": None,
                                                  "text": None}]), "rule span 0")

def test_the_scope_names_a_release_and_editions():
    for scope in ({**fx.scope(), "edition_ids": []}, {**fx.scope(), "edition_ids": ["doc-synth-handbook"]},
                  {**fx.scope(), "knowledge_release_id": "fact-synth-1"},
                  {**fx.scope(), "edition_ids": ["edition-synth-handbook-1", "edition-synth-handbook-1"]},
                  {**fx.scope(), "scope_ids": [""]}, {**fx.scope(), "extra": 1}):
        _reject_symbolic_or_answer(symbolic_contracts.SymbolicResult, _symbolic_payload(scope=scope), "")
    _symbolic_result(scope={**fx.scope(), "scope_ids": ["program-synth-1"]})

def test_the_scope_and_rule_spans_roundtrip():
    r = _symbolic_result()
    assert symbolic_contracts.SymbolicResult.parse(base.canonical_json(r)) == r
    assert r.scope.edition_ids == ("edition-synth-handbook-1",)

# ---------------------------------------------------------------- M-k and M-a: private ids in a decision
VARIANTS = ["fact-synth-0001", "FACT-synth-0001", "fact-synth-0001 ", " fact-synth-0001", "fact-synth-0001\n", "ｆact-synth-0001",
            "fact‑synth-0001", "x/fact-synth-0001", "sess-synth-0001\t"]

@pytest.mark.parametrize("ref", VARIANTS)
def test_a_session_fact_id_in_the_evidence_refs_of_a_standalone_result_is_rejected(ref):
    d = {**decision("eligible"), "evidence_refs": [ref]}
    _reject_symbolic_or_answer(symbolic_contracts.SymbolicResult, _symbolic_payload(decision=d), "another namespace")

@pytest.mark.parametrize("field", ["satisfied_conditions", "evidence_refs"])
def test_a_private_id_in_any_decision_text_field_is_rejected(field):
    d = {**decision("eligible"), field: ["fictional-prereq-met", "see fact-synth-0001"]}
    _reject_symbolic_or_answer(symbolic_contracts.SymbolicResult, _symbolic_payload(decision=d), "another namespace")

@pytest.mark.parametrize("ref", VARIANTS)
def test_a_session_fact_id_in_the_decision_of_a_bundle_is_rejected(ref):
    b = bundle()
    b["symbolic"]["decision"]["evidence_refs"] = [ref]
    _reject_symbolic_or_answer(answer.EvidenceBundle, b, "another namespace")

def test_a_session_fact_id_in_a_rule_span_or_scope_is_rejected():
    b = bundle()
    b["symbolic"]["rule_spans"][0]["text"] = "Rule text from fact-synth-0001"
    _reject_symbolic_or_answer(answer.EvidenceBundle, b, "another namespace")
    b = bundle()
    b["symbolic"]["scope"]["scope_ids"] = ["sess-synth-0001"]
    _reject_symbolic_or_answer(answer.EvidenceBundle, b, "another namespace")

def test_the_input_fact_reference_itself_stays_legitimate():
    answer.EvidenceBundle.parse(bundle())

def test_ordinary_prose_in_a_decision_is_not_a_private_id():
    d = {**decision("eligible"), "satisfied_conditions": ["fact-checking passed", "edition-specific rule met"]}
    _symbolic_result(decision=d)

# ---------------------------------------------------------------- M-k: sessions and decided inputs
def test_session_facts_from_two_sessions_cannot_share_a_bundle():
    b = bundle(facts=("user_confirmed", "user_confirmed"))
    b["session_facts"][1].update(fact_id="fact-synth-0002", session_id="sess-synth-0002")
    _reject_symbolic_or_answer(answer.EvidenceBundle, b, "more than one session")
    b["session_facts"][1]["session_id"] = b["session_facts"][0]["session_id"]
    answer.EvidenceBundle.parse(b)

def test_a_decided_outcome_needs_inputs_and_each_input_needs_a_session_fact():
    b = bundle()
    b["symbolic"]["inputs"] = []
    _reject_symbolic_or_answer(answer.EvidenceBundle, b, "rests on no input")
    b = bundle()
    b["symbolic"]["inputs"][0]["fact_ref"] = None
    _reject_symbolic_or_answer(answer.EvidenceBundle, b, "cites no session fact")
    b = bundle(outcome="ineligible", claims=("decision_ineligible",))
    b["symbolic"]["inputs"] = []
    _reject_symbolic_or_answer(answer.EvidenceBundle, b, "rests on no input")
    # an unknown outcome may have no input at all
    b = bundle(outcome="unknown", claims=("unknown_explanation",), facts=())
    b["symbolic"]["inputs"] = []
    answer.EvidenceBundle.parse(b)

# ---------------------------------------------------------------- M-i: the envelope
def test_an_answered_symbolic_or_hybrid_envelope_needs_a_citation():
    for route in ("Symbolic", "Hybrid"):
        answer.AnswerEnvelope.parse(envelope(route=route, decision=decision("eligible")))
        _reject_symbolic_or_answer(answer.AnswerEnvelope, envelope(route=route, decision=decision("eligible"), citations=[]), "at least one citation")
    _reject_symbolic_or_answer(answer.AnswerEnvelope, envelope(citations=[]), "at least one citation")

def test_unsupported_unknown_and_error_may_cite_nothing():
    ok = {"passed": True, "checks": ["routing_checked"], "failures": []}
    for status, outcome in (("abstained", "unsupported"), ("abstained", "unknown"), ("clarification_needed", "unknown")):
        answer.AnswerEnvelope.parse(envelope(status=status, route="Symbolic", decision=decision(outcome), citations=[],
                                                validation=ok))
    answer.AnswerEnvelope.parse(envelope(status="error", route="Symbolic", decision=decision("error"), citations=[],
                                            validation={"passed": False, "checks": [], "failures": ["engine timeout"]}))
    answer.AnswerEnvelope.parse(envelope(status="abstained", route=None, decision=None, citations=[], validation=ok))

def test_a_passed_validation_needs_a_check_that_ran():
    answer.ValidationResult.parse({"passed": True, "checks": ["c"], "failures": []})
    answer.ValidationResult.parse({"passed": False, "checks": [], "failures": ["f"]})
    _reject_symbolic_or_answer(answer.ValidationResult, {"passed": True, "checks": [], "failures": []}, "at least one check")
    _reject_symbolic_or_answer(answer.ValidationResult, {"passed": True, "checks": ["c"], "failures": ["f"]}, "exactly when")
    _reject_symbolic_or_answer(answer.ValidationResult, {"passed": False, "checks": ["c"], "failures": []}, "exactly when")
    _reject_symbolic_or_answer(answer.AnswerEnvelope, envelope(validation={"passed": True, "checks": [], "failures": []}), "at least one check")

# ---------------------------------------------------------------- M-a: the envelope text, citations and decision
@pytest.mark.parametrize("ref", VARIANTS)
def test_a_private_id_in_the_answer_text_is_rejected(ref):
    _reject_symbolic_or_answer(answer.AnswerEnvelope, envelope(text=f"Your record {ref} says so."), "another namespace|private id")

@pytest.mark.parametrize("ref", VARIANTS)
def test_a_private_id_in_a_citation_or_decision_of_an_envelope_is_rejected(ref):
    _reject_symbolic_or_answer(answer.AnswerEnvelope, envelope(citations=[{**cite(), "locator_ref": ref}]), "private id")
    _reject_symbolic_or_answer(answer.AnswerEnvelope, envelope(route="Hybrid", decision={**decision("eligible"), "evidence_refs": [ref]}), "private id")

def test_ordinary_answer_prose_is_not_flagged():
    answer.AnswerEnvelope.parse(envelope(text="Fact-checking is done by the Registrar; edition-specific rules apply."))

# ---------------------------------------------------------------- M-m: the register check inside the bundle path
def test_a_bundle_rejects_a_retrieved_chunk_that_claims_more_than_its_register_version():
    b = bundle(route="RAG", sym=False, facts=(), claims=("policy_passage",))
    b["retrieval"]["items"][0]["chunk"]["source_verification"] = "verified"
    _reject_symbolic_or_answer(answer.EvidenceBundle, b, "stale or inflated verification claim")

def test_a_bundle_rejects_a_retrieval_without_its_register_versions():
    b = bundle(route="RAG", sym=False, facts=(), claims=("policy_passage",))
    b["retrieval"]["versions"] = []
    _reject_symbolic_or_answer(answer.EvidenceBundle, b, "not in the result's versions")

# ---------------------------------------------------------------- M-g: a section locator can be cited
def test_a_citation_can_name_a_section_locator():
    b = _answer_bundle(route="RAG", sym=False, facts=(), claims=("policy_passage",))
    chunk = b["retrieval"]["items"][0]["chunk"]
    chunk["spans"][0]["locator"] = {"kind": "section", "table_index": None, "cell_ids": [], "item_ids": [], "ref": None,
                                    "section_path": ["Part I", "Admission"]}
    bundle = answer.EvidenceBundle.parse(b)
    cite = {**_answer_cite(), "locator_ref": "Part I/Admission"}
    env = answer.AnswerEnvelope.parse(envelope(citations=[cite]))
    answer.check_envelope_against_bundle(env, bundle)
    other = answer.AnswerEnvelope.parse(envelope(citations=[{**cite, "locator_ref": "Part II"}]))
    with pytest.raises(base.ContractError, match="page or locator"):
        answer.check_envelope_against_bundle(other, bundle)


# Answer provenance and namespace integrity





def _decided_bundle(outcome="eligible", mutate=None, **kw):
    kw.setdefault("claims", {"eligible": ("decision_eligible", "policy_passage"),
                             "ineligible": ("decision_ineligible", "policy_passage")}[outcome])
    s = symbolic(outcome)
    if mutate:
        mutate(s)
    return bundle(outcome=outcome, **kw) | {"symbolic": s}

def _reject_answer_bundle(payload, match):
    bad(answer.EvidenceBundle, payload, match)

@pytest.mark.parametrize("outcome", ["eligible", "ineligible"])
def test_a_decision_whose_provenance_is_carried_is_accepted(outcome):
    answer.EvidenceBundle.parse(_decided_bundle(outcome))

@pytest.mark.parametrize("outcome", ["eligible", "ineligible"])
def test_a_scope_naming_another_knowledge_release_is_refused(outcome):
    _reject_answer_bundle(_decided_bundle(outcome, lambda s: s["scope"].update(knowledge_release_id="release-other")), "release")

@pytest.mark.parametrize("outcome", ["eligible", "ineligible"])
def test_a_rule_span_citing_a_version_the_bundle_does_not_carry_is_refused(outcome):
    _reject_answer_bundle(_decided_bundle(outcome, lambda s: s["rule_spans"][0].update(version_id="ver-synth-unrelated-7")),
           "ver-synth-unrelated-7")

@pytest.mark.parametrize("outcome", ["eligible", "ineligible"])
def test_a_rule_span_with_other_bytes_than_its_version_is_refused(outcome):
    _reject_answer_bundle(_decided_bundle(outcome, lambda s: s["rule_spans"][0].update(byte_sha256="7" * 64)), "digest|bytes")

@pytest.mark.parametrize("outcome", ["eligible", "ineligible"])
def test_a_scope_edition_the_bundle_does_not_carry_is_refused(outcome):
    _reject_answer_bundle(_decided_bundle(outcome, lambda s: s["scope"].update(edition_ids=["edition-synth-unrelated-7"])),
           "edition-synth-unrelated-7")

def test_one_unknown_edition_among_known_ones_is_refused():
    _reject_answer_bundle(_decided_bundle("eligible", lambda s: s["scope"].update(
        edition_ids=["edition-synth-handbook-1", "edition-synth-unrelated-7"])), "edition-synth-unrelated-7")

def _two_editions(s):
    s["rule_spans"][0].update(byte_sha256=fx.SHA["2"], version_id="ver-synth-handbook-2")

def test_a_rule_span_from_an_edition_outside_the_decision_scope_is_refused():
    both = [fx.item(1), fx.item(2, rank=2, score=0.8, edition="2", doc="doc-synth-other")]
    payload = _decided_bundle("eligible", _two_editions, retrieval=True)
    payload["retrieval"] = fx.retrieval(both)
    _reject_answer_bundle(payload, "outside the decision scope")
    ok = _decided_bundle("eligible", lambda s: (_two_editions(s), s["scope"].update(
        edition_ids=["edition-synth-handbook-1", "edition-synth-handbook-2"])))
    ok["retrieval"] = fx.retrieval(both)
    answer.EvidenceBundle.parse(ok)

# ---------------------------------------------------------------- no register carried
def test_a_decided_symbolic_bundle_with_no_register_is_refused():
    payload = _decided_bundle("eligible", retrieval=False, route="Symbolic", claims=("decision_eligible",))
    _reject_answer_bundle(payload, "no register version")

def test_a_symbolic_bundle_may_carry_the_register_slice_itself():
    payload = _decided_bundle("eligible", retrieval=False, route="Symbolic", claims=("decision_eligible",),
                      versions=fx.versions_for([fx.item()]))
    answer.EvidenceBundle.parse(payload)

def test_a_hybrid_bundle_with_no_passages_and_no_register_is_refused():
    payload = _decided_bundle("eligible")
    payload["retrieval"] = fx.retrieval(items=[], coverage="none")
    payload["permitted_claims"] = ["decision_eligible"]
    _reject_answer_bundle(payload, "no register version")

def test_a_synthetic_decision_without_a_register_is_accepted_and_establishes_no_claim():
    s = symbolic("eligible", synthetic=True)
    payload = bundle(route="Symbolic", retrieval=False, claims=(), outcome="eligible") | {"symbolic": s}
    answer.EvidenceBundle.parse(payload)
    payload["permitted_claims"] = ["decision_eligible"]
    _reject_answer_bundle(payload, "synthetic decision establishes no claim")

@pytest.mark.parametrize("outcome", ["unknown", "unsupported", "error"])
def test_results_without_scope_need_no_register(outcome):
    claims = {"unknown": ("unknown_explanation",), "unsupported": ("abstention",), "error": ("error_report",)}[outcome]
    answer.EvidenceBundle.parse(bundle(route="Symbolic", retrieval=False, claims=claims, outcome=outcome))

def test_a_synthetic_decision_is_still_checked_when_a_register_is_carried():
    s = symbolic("eligible", synthetic=True)
    s["rule_spans"][0]["version_id"] = "ver-synth-unrelated-7"
    payload = bundle(claims=(), outcome="eligible") | {"symbolic": s}
    _reject_answer_bundle(payload, "ver-synth-unrelated-7")

# ---------------------------------------------------------------- the carried versions themselves
def test_carried_versions_must_agree_with_the_retrievals():
    payload = _decided_bundle("eligible")
    twin = copy.deepcopy(payload["retrieval"]["versions"][0])
    twin["edition_id"] = "edition-synth-handbook-9"
    payload["versions"] = [twin]
    _reject_answer_bundle(payload, "carried twice with different content")

def test_carried_versions_are_checked_as_a_register():
    payload = _decided_bundle("eligible", retrieval=False, route="Symbolic", claims=("decision_eligible",))
    a = fx.versions_for([fx.item()])[0]
    b = copy.deepcopy(a)
    b["version_id"], b["edition_id"] = "ver-synth-handbook-5", "edition-synth-handbook-5"
    payload["versions"] = [a, b]                       # the same bytes under two versions
    _reject_answer_bundle(payload, "same bytes")

def test_the_same_version_carried_by_both_is_accepted():
    payload = _decided_bundle("eligible")
    payload["versions"] = copy.deepcopy(payload["retrieval"]["versions"])
    answer.EvidenceBundle.parse(payload)


# Mutation regressions: field and relationship guards


# ---------------------------------------------------------------- the envelope against its bundle
def test_an_answer_needs_the_decision_claim_of_its_own_outcome():
    only_passage = answer.EvidenceBundle.parse(bundle(claims=("policy_passage",)))
    env = answer.AnswerEnvelope.parse(envelope(route="Hybrid", decision=decision("eligible")))
    with pytest.raises(base.ContractError, match="decision_eligible"):
        answer.check_envelope_against_bundle(env, only_passage)

def test_a_citation_can_name_a_reference_locator():
    b = _answer_bundle(route="RAG", sym=False, facts=(), claims=("policy_passage",))
    b["retrieval"]["items"][0]["chunk"]["spans"][0]["locator"] = {
        "kind": "docling_ref", "table_index": None, "cell_ids": [], "item_ids": [], "ref": "#/texts/2", "section_path": []}
    bundle = answer.EvidenceBundle.parse(b)
    good = answer.AnswerEnvelope.parse(envelope(citations=[{**cite(), "locator_ref": "#/texts/2"}]))
    answer.check_envelope_against_bundle(good, bundle)
    wrong = answer.AnswerEnvelope.parse(envelope(citations=[{**cite(), "locator_ref": "#/texts/9"}]))
    with pytest.raises(base.ContractError, match="page or locator"):
        answer.check_envelope_against_bundle(wrong, bundle)
