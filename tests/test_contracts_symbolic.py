"""Phase 1 Task 3, group 5a: the five-outcome DecisionOutcome, SymbolicResult and the capability registry."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from backend.bintanong_contracts import base, runtime, symbolic
from backend.bintanong_tools.prospectus_extractor import prerequisites

ROOT = Path(__file__).resolve().parents[1]
DECISIONS = json.loads((ROOT / "knowledge/manifests/examples/synthetic-decisions.json").read_text(encoding="utf-8"))
BY_OUTCOME = {d["outcome"]: d for d in DECISIONS}


def mut(rec, **kw):
    c = copy.deepcopy(rec)
    c.update(kw)
    return c


def bad(cls, payload):
    with pytest.raises((ValidationError, base.ContractError)):
        cls.parse(payload)


# ---------------------------------------------------------------- examples validate with the package
@pytest.mark.parametrize("outcome", ["eligible", "ineligible", "unknown", "unsupported", "error"])
def test_decision_examples_validate_and_roundtrip(outcome):
    d = symbolic.DecisionOutcome.parse(BY_OUTCOME[outcome])
    t = base.canonical_json(d)
    assert symbolic.DecisionOutcome.parse(t) == d and base.canonical_json(symbolic.DecisionOutcome.parse(t)) == t


def test_outcome_vocabulary_is_exactly_the_five_and_comes_from_the_json():
    assert set(base.VOCAB["decision"]["outcomes"]) == {"eligible", "ineligible", "unknown", "unsupported", "error"}
    bad(symbolic.DecisionOutcome, mut(BY_OUTCOME["eligible"], outcome="approved"))
    bad(symbolic.DecisionOutcome, mut(BY_OUTCOME["eligible"], outcome="denied"))


def test_prerequisite_states_track_the_extractor_vocabulary():
    d = base.VOCAB["decision"]
    assert set(d["prerequisite_rule_states"]) == set(prerequisites.PREREQUISITE_STATES)
    assert set(d["executable_prerequisite_rule_states"]) == set(prerequisites.EXECUTABLE_PREREQUISITE_STATES)


# ---------------------------------------------------------------- per-outcome semantics
E, I, U, S, X = (BY_OUTCOME[k] for k in ("eligible", "ineligible", "unknown", "unsupported", "error"))


@pytest.mark.parametrize("label,payload", [
    ("eligible without evidence", mut(E, evidence_refs=[])),
    ("eligible without satisfied conditions", mut(E, satisfied_conditions=[])),
    ("eligible with a violated condition", mut(E, violated_conditions=["x"])),
    ("eligible with an unknown condition", mut(E, unknown_conditions=["x"])),
    ("eligible with a missing fact", mut(E, missing_facts=["x"])),
    ("eligible with an unresolved conflict", mut(E, unresolved_conflicts=["conflict-synth-0001"])),
    ("eligible on partial coverage", mut(E, rule_coverage="partial")),
    ("eligible on absent coverage", mut(E, rule_coverage="absent")),
    ("eligible on unsupported predicate", mut(E, predicate_supported=False)),
    ("eligible over a blank prerequisite", mut(E, prerequisite_rule_state="blank_unreviewed")),
    ("eligible over an unreadable prerequisite", mut(E, prerequisite_rule_state="unreadable")),
    ("eligible over an unresolved reference", mut(E, prerequisite_rule_state="unresolved_reference")),
    ("eligible with an error code", mut(E, error_code="x")),
    ("ineligible without a violated condition", mut(I, violated_conditions=[])),
    ("ineligible without evidence", mut(I, evidence_refs=[])),
    ("ineligible with an unresolved conflict", mut(I, unresolved_conflicts=["conflict-synth-0001"])),
    ("ineligible on absent coverage", mut(I, rule_coverage="absent")),
    ("ineligible over a standing condition", mut(I, prerequisite_rule_state="standing_condition")),
    ("ineligible with an error code", mut(I, error_code="x")),
    ("unknown with nothing missing", mut(U, missing_facts=[], rule_coverage="verified")),
    ("unknown carrying a violated condition", mut(U, violated_conditions=["x"])),
    ("unknown with an error code", mut(U, error_code="x")),
    ("unsupported but predicate supported", mut(S, predicate_supported=True)),
    ("unsupported with coverage", mut(S, rule_coverage="verified")),
    ("unsupported with satisfied conditions", mut(S, satisfied_conditions=["x"])),
    ("unsupported with evidence", mut(S, evidence_refs=["x"])),
    ("unsupported with missing facts", mut(S, missing_facts=["x"])),
    ("unsupported with a conflict", mut(S, unresolved_conflicts=["x"])),
    ("error without a code", mut(X, error_code=None)),
    ("error with a satisfied condition", mut(X, satisfied_conditions=["x"])),
    ("error with a violated condition", mut(X, violated_conditions=["x"])),
    ("error with evidence", mut(X, evidence_refs=["x"])),
    ("error with an empty code", mut(X, error_code="")),
])
def test_forbidden_outcome_shapes_are_rejected(label, payload):
    bad(symbolic.DecisionOutcome, payload)


def test_error_can_never_be_a_policy_result():
    result = _result(X)
    with pytest.raises(base.ContractError, match="operational"):
        symbolic.as_policy_result(result)
    assert symbolic.as_policy_result(_result(E)) == "eligible"
    assert symbolic.as_policy_result(_result(U)) == "unknown"


def test_verified_zero_prerequisites_differs_from_blank_or_unreadable():
    for state in ("stated_none", "reviewed_empty", "resolved", None):
        symbolic.DecisionOutcome.parse(mut(E, prerequisite_rule_state=state))
    for state in ("blank_unreviewed", "unreadable", "unresolved_reference", "standing_condition", "alternative_or_exception"):
        bad(symbolic.DecisionOutcome, mut(E, prerequisite_rule_state=state))
        # but unknown may state exactly why: a non-executable prerequisite is itself the reason
        symbolic.DecisionOutcome.parse(mut(U, prerequisite_rule_state=state, rule_coverage="verified", missing_facts=[]))


@pytest.mark.parametrize("over", [
    dict(rule_coverage="complete"), dict(prerequisite_rule_state="none"), dict(predicate=""),
    dict(satisfied_conditions=[""]), dict(satisfied_conditions="x"), dict(predicate_supported="yes"),
    dict(unknown_field=1), dict(approved=True), dict(promotion_status="VERIFIED"),
    dict(schema_version="bintanong-decision-v2"),
])
def test_malformed_decision_is_rejected(over):
    bad(symbolic.DecisionOutcome, mut(E, **over))


# ---------------------------------------------------------------- SymbolicResult
def _result(decision, **over):
    d = {"schema_version": "bintanong-symbolic-result-v1", "decision": decision, "capability": "enrollment_eligibility",
         "inputs": [{"name": "course", "value": "FICTIONAL-101", "fact_ref": "fact-synth-0001"}],
         "rule_ids": ["rule-synth-1"], "rule_bundle_version": "bundle-synth-1"}
    if decision["outcome"] in ("unsupported", "error"):
        d.update(rule_ids=[], rule_bundle_version=None)
    d.update(over)
    return symbolic.SymbolicResult.parse(d)


def test_symbolic_result_roundtrips():
    r = _result(E)
    assert symbolic.SymbolicResult.parse(base.canonical_json(r)) == r


@pytest.mark.parametrize("over", [
    dict(rule_ids=[]), dict(rule_bundle_version=None), dict(rule_ids=["rule-synth-1", "rule-synth-1"]),
])
def test_eligible_and_ineligible_need_rule_ids_and_a_bundle_version(over):
    for decision in (E, I):
        with pytest.raises((ValidationError, base.ContractError)):
            _result(decision, **over)


def test_unsupported_predicate_cannot_invent_rules():
    with pytest.raises((ValidationError, base.ContractError)):
        _result(S, rule_ids=["rule-synth-1"], rule_bundle_version="bundle-synth-1")


@pytest.mark.parametrize("over", [
    dict(capability=""), dict(inputs=[{"name": "c", "value": "x); halt(", "fact_ref": None}]),
    dict(inputs=[{"name": "c", "value": "x", "fact_ref": "ver-synth-1"}]),
    dict(goal="can_enroll(x)."), dict(prolog="can_enroll(x)."), dict(query_string="x"),
    dict(rule_ids=["fact-synth-1"]), dict(schema_version="bintanong-symbolic-result-v2"),
])
def test_symbolic_result_rejects_free_form_goals_and_foreign_ids(over):
    with pytest.raises((ValidationError, base.ContractError)):
        _result(E, **over)


# ---------------------------------------------------------------- registry and fixed goals
def registry():
    return symbolic.CapabilityRegistry({
        "can_enroll_fictional": symbolic.Capability("enrollment_eligibility", ("course",))})


def req(**kw):
    d = {"predicate": "can_enroll_fictional", "inputs": [{"name": "course", "value": "FICTIONAL-101", "fact_ref": None}]}
    d.update(kw)
    return runtime.PredicateRequest.parse(d)


def test_the_default_registry_is_empty_so_everything_is_unsupported():
    assert symbolic.EMPTY_REGISTRY.supports("can_enroll_fictional") is False
    with pytest.raises(symbolic.UnsupportedRequest):
        symbolic.EMPTY_REGISTRY.goal(req())


def test_a_registered_goal_binds_inputs_in_registered_order():
    goal = registry().goal(req())
    assert goal.predicate == "can_enroll_fictional" and goal.args == (("course", "FICTIONAL-101"),)
    assert goal.capability == "enrollment_eligibility"


@pytest.mark.parametrize("request_", [
    {"predicate": "not_registered", "inputs": []},
    {"predicate": "can_enroll_fictional", "inputs": []},                                  # missing input
    {"predicate": "can_enroll_fictional", "inputs": [
        {"name": "course", "value": "x", "fact_ref": None}, {"name": "extra", "value": "y", "fact_ref": None}]},
    {"predicate": "can_enroll_fictional", "inputs": [{"name": "other", "value": "x", "fact_ref": None}]},
])
def test_goals_outside_the_registry_or_with_wrong_inputs_are_unsupported(request_):
    with pytest.raises(symbolic.UnsupportedRequest):
        registry().goal(runtime.PredicateRequest.parse(request_))


def test_a_result_must_agree_with_the_registry():
    reg = registry()
    reg.check_result(_result(E))
    # eligible for a predicate the registry does not know
    unknown_pred = mut(E, predicate="not_registered")
    with pytest.raises(base.ContractError, match="registry"):
        reg.check_result(_result(unknown_pred))
    # registered predicate reported as unsupported
    with pytest.raises(base.ContractError, match="registry"):
        reg.check_result(_result(mut(S, predicate="can_enroll_fictional")))
    # unregistered predicate correctly reported unsupported is fine
    reg.check_result(_result(mut(S, predicate="fictional_unregistered")))
    # wrong capability or wrong inputs on a decided result
    with pytest.raises(base.ContractError, match="capability"):
        reg.check_result(_result(E, capability="other_capability"))
    with pytest.raises(base.ContractError, match="inputs"):
        reg.check_result(_result(E, inputs=[]))
    # an error report for any predicate stays an error
    reg.check_result(_result(X))


# ---------------------------------------------------------------- mutation-driven additions
def test_unknown_may_rest_on_coverage_alone():
    d = symbolic.DecisionOutcome.parse(mut(U, missing_facts=[], rule_coverage="partial"))
    assert d.rule_coverage == "partial" and not d.missing_facts
    bad(symbolic.DecisionOutcome, mut(U, missing_facts=[], rule_coverage="verified"))


def test_symbolic_result_rejects_duplicate_input_names_and_rule_ids():
    dup = [{"name": "c", "value": "x", "fact_ref": None}, {"name": "c", "value": "y", "fact_ref": None}]
    with pytest.raises((ValidationError, base.ContractError)):
        _result(E, inputs=dup)
