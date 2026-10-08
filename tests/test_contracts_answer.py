"""Phase 1 Task 3, group 5b: EvidenceBundle and AnswerEnvelope (synthetic; no outcome here is policy)."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from backend.bintanong_contracts import answer, base
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
        with pytest.raises(base.ContractError):
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
