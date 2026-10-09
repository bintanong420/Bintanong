"""Phase 1 Task 3, fix pass 3, M3: the scope and rule spans of a decided symbolic result must come from a
register version the bundle carries. A decision cannot vouch for its own provenance."""

from __future__ import annotations

import copy

import pytest

from backend.bintanong_contracts import answer
import contracts_fixtures as fx
import test_contracts_answer as T


def decided(outcome="eligible", mutate=None, **kw):
    kw.setdefault("claims", {"eligible": ("decision_eligible", "policy_passage"),
                             "ineligible": ("decision_ineligible", "policy_passage")}[outcome])
    s = T.symbolic(outcome)
    if mutate:
        mutate(s)
    return T.bundle(outcome=outcome, **kw) | {"symbolic": s}


def reject(payload, match):
    T.bad(answer.EvidenceBundle, payload, match)


@pytest.mark.parametrize("outcome", ["eligible", "ineligible"])
def test_a_decision_whose_provenance_is_carried_is_accepted(outcome):
    answer.EvidenceBundle.parse(decided(outcome))


@pytest.mark.parametrize("outcome", ["eligible", "ineligible"])
def test_a_scope_naming_another_knowledge_release_is_refused(outcome):
    reject(decided(outcome, lambda s: s["scope"].update(knowledge_release_id="release-other")), "release")


@pytest.mark.parametrize("outcome", ["eligible", "ineligible"])
def test_a_rule_span_citing_a_version_the_bundle_does_not_carry_is_refused(outcome):
    reject(decided(outcome, lambda s: s["rule_spans"][0].update(version_id="ver-synth-unrelated-7")),
           "ver-synth-unrelated-7")


@pytest.mark.parametrize("outcome", ["eligible", "ineligible"])
def test_a_rule_span_with_other_bytes_than_its_version_is_refused(outcome):
    reject(decided(outcome, lambda s: s["rule_spans"][0].update(byte_sha256="7" * 64)), "digest|bytes")


@pytest.mark.parametrize("outcome", ["eligible", "ineligible"])
def test_a_scope_edition_the_bundle_does_not_carry_is_refused(outcome):
    reject(decided(outcome, lambda s: s["scope"].update(edition_ids=["edition-synth-unrelated-7"])),
           "edition-synth-unrelated-7")


def test_one_unknown_edition_among_known_ones_is_refused():
    reject(decided("eligible", lambda s: s["scope"].update(
        edition_ids=["edition-synth-handbook-1", "edition-synth-unrelated-7"])), "edition-synth-unrelated-7")


def _two_editions(s):
    s["rule_spans"][0].update(byte_sha256=fx.SHA["2"], version_id="ver-synth-handbook-2")


def test_a_rule_span_from_an_edition_outside_the_decision_scope_is_refused():
    both = [fx.item(1), fx.item(2, rank=2, score=0.8, edition="2", doc="doc-synth-other")]
    payload = decided("eligible", _two_editions, retrieval=True)
    payload["retrieval"] = fx.retrieval(both)
    reject(payload, "outside the decision scope")
    ok = decided("eligible", lambda s: (_two_editions(s), s["scope"].update(
        edition_ids=["edition-synth-handbook-1", "edition-synth-handbook-2"])))
    ok["retrieval"] = fx.retrieval(both)
    answer.EvidenceBundle.parse(ok)


# ---------------------------------------------------------------- no register carried
def test_a_decided_symbolic_bundle_with_no_register_is_refused():
    payload = decided("eligible", retrieval=False, route="Symbolic", claims=("decision_eligible",))
    reject(payload, "no register version")


def test_a_symbolic_bundle_may_carry_the_register_slice_itself():
    payload = decided("eligible", retrieval=False, route="Symbolic", claims=("decision_eligible",),
                      versions=fx.versions_for([fx.item()]))
    answer.EvidenceBundle.parse(payload)


def test_a_hybrid_bundle_with_no_passages_and_no_register_is_refused():
    payload = decided("eligible")
    payload["retrieval"] = fx.retrieval(items=[], coverage="none")
    payload["permitted_claims"] = ["decision_eligible"]
    reject(payload, "no register version")


def test_a_synthetic_decision_without_a_register_is_accepted_and_establishes_no_claim():
    s = T.symbolic("eligible", synthetic=True)
    payload = T.bundle(route="Symbolic", retrieval=False, claims=(), outcome="eligible") | {"symbolic": s}
    answer.EvidenceBundle.parse(payload)
    payload["permitted_claims"] = ["decision_eligible"]
    reject(payload, "synthetic decision establishes no claim")


@pytest.mark.parametrize("outcome", ["unknown", "unsupported", "error"])
def test_results_without_scope_need_no_register(outcome):
    claims = {"unknown": ("unknown_explanation",), "unsupported": ("abstention",), "error": ("error_report",)}[outcome]
    answer.EvidenceBundle.parse(T.bundle(route="Symbolic", retrieval=False, claims=claims, outcome=outcome))


def test_a_synthetic_decision_is_still_checked_when_a_register_is_carried():
    s = T.symbolic("eligible", synthetic=True)
    s["rule_spans"][0]["version_id"] = "ver-synth-unrelated-7"
    payload = T.bundle(claims=(), outcome="eligible") | {"symbolic": s}
    reject(payload, "ver-synth-unrelated-7")


# ---------------------------------------------------------------- the carried versions themselves
def test_carried_versions_must_agree_with_the_retrievals():
    payload = decided("eligible")
    twin = copy.deepcopy(payload["retrieval"]["versions"][0])
    twin["edition_id"] = "edition-synth-handbook-9"
    payload["versions"] = [twin]
    reject(payload, "carried twice with different content")


def test_carried_versions_are_checked_as_a_register():
    payload = decided("eligible", retrieval=False, route="Symbolic", claims=("decision_eligible",))
    a = fx.versions_for([fx.item()])[0]
    b = copy.deepcopy(a)
    b["version_id"], b["edition_id"] = "ver-synth-handbook-5", "edition-synth-handbook-5"
    payload["versions"] = [a, b]                       # the same bytes under two versions
    reject(payload, "same bytes")


def test_the_same_version_carried_by_both_is_accepted():
    payload = decided("eligible")
    payload["versions"] = copy.deepcopy(payload["retrieval"]["versions"])
    answer.EvidenceBundle.parse(payload)
