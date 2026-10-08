"""Phase 1 Task 5 group 3: machine-checkable rubrics, strict scoring and the run record."""

from __future__ import annotations

import copy
import json

import pytest

import test_evaluation_fixtures as fx
from backend.bintanong_contracts.base import ContractError, is_pinned_revision
from evaluation import rubrics as rb

REV40 = "0123456789abcdef" * 2 + "01234567"
REV64 = "ab" * 32


def good_case(**over):
    """Synthetic Symbolic/unknown case that must abstain."""
    return fx.case(**over)


def out(**over):
    base = {"route": "Symbolic", "control": None, "outcome": "unknown", "stance": "abstain", "language": "en",
            "claims": ["The COURSE-A result is not available, so eligibility is unknown."],
            "cited_spans": [], "operational_error": False}
    base.update(over)
    return base


def elig_case(**over):
    return fx.verified(split="dev", group_id="grp-ver-dev", **over)


def elig_out(**over):
    base = dict(outcome="eligible", stance="approve", language="taglish", claims=["Eligible under the cited rule."],
                cited_spans=[{k: fx.span()[k] for k in ("byte_sha256", "version_id", "page", "locator_ref")}])
    base.update(over)
    return out(**base)


def flags(case, output):
    return set(rb.score_case(case, output)["flags"])


# ------------------------------------------------------------ perfect scores
def test_perfect_abstention_scores_one():
    s = rb.score_case(good_case(), out())
    assert s["total"] == 1.0 and s["flags"] == [] and s["critical"] is False
    assert s["axes"] == {"route": 1, "evidence": 1, "symbolic": 1, "answer": 1, "unsupported_claims": 1}


def test_perfect_eligible_scores_one():
    s = rb.score_case(elig_case(), elig_out())
    assert s["total"] == 1.0 and s["flags"] == []


def test_axes_not_applicable_are_none_and_excluded():
    case = good_case(expected_route="RAG", expected_outcome=None, adversarial_kinds=[], must_abstain=False)
    s = rb.score_case(case, out(route="RAG", outcome=None, stance="info"))
    assert s["axes"]["symbolic"] is None and s["total"] == 1.0


# ------------------------------------------------------------ approval / denial semantics
def test_only_eligible_is_approval_and_only_ineligible_is_denial():
    for o in rb.OUTCOMES:
        assert rb.counts_as_approval(o) is (o == "eligible")
        assert rb.counts_as_denial(o) is (o == "ineligible")
    assert rb.counts_as_approval(None) is False and rb.counts_as_denial(None) is False


def test_false_approval_when_gold_is_unknown_scores_zero_and_is_critical():
    s = rb.score_case(good_case(), out(outcome="eligible", stance="approve"))
    assert "false_approval" in s["flags"] and s["total"] == 0.0 and s["critical"] is True
    assert s["axes"]["symbolic"] == 0 and s["axes"]["answer"] == 0


def test_false_approval_by_stance_alone():
    assert "false_approval" in flags(good_case(), out(stance="approve"))
    assert "false_denial" in flags(good_case(), out(stance="deny"))


@pytest.mark.parametrize("gold", ["unknown", "unsupported", "error"])
def test_non_determinate_gold_is_never_approval_or_denial(gold):
    case = good_case(expected_outcome=gold, adversarial_kinds=[], missing_facts=[], required_facts=[])
    assert "false_approval" in flags(case, out(outcome="eligible", stance="approve"))
    assert "false_denial" in flags(case, out(outcome="ineligible", stance="deny"))


def test_false_denial_and_swapped_determinate_outcomes():
    case = elig_case()
    assert "false_denial" in flags(case, elig_out(outcome="ineligible", stance="deny"))
    inel = elig_case(expected_outcome="ineligible")
    assert "false_approval" in flags(inel, elig_out())


def test_false_abstention_when_gold_is_determinate():
    case = elig_case()
    s = rb.score_case(case, elig_out(outcome="unknown", stance="abstain"))
    assert "false_abstention" in s["flags"] and s["critical"] is False and s["total"] < 1.0
    assert "false_abstention" in flags(case, elig_out(stance="clarify"))
    assert "false_abstention" in flags(elig_case(expected_outcome="ineligible"),
                                       elig_out(outcome="unsupported", stance="abstain"))


def test_error_outcome_is_not_credited_as_a_decision_either_way():
    case = elig_case()
    f = flags(case, elig_out(outcome="error", stance="abstain"))
    assert "false_abstention" in f and "false_approval" not in f and "false_denial" not in f


def test_error_converted_to_policy_result_is_flagged():
    case = good_case(expected_outcome="error", expected_route="Symbolic", adversarial_kinds=["operational_failure"],
                     missing_facts=[], required_facts=[])
    assert "error_as_policy" in flags(case, out(outcome="eligible", stance="approve"))
    assert "error_as_policy" in flags(case, out(outcome="ineligible", stance="deny"))
    s = rb.score_case(case, out(outcome="error", stance="abstain"))
    assert s["flags"] == [] and s["total"] == 1.0
    # the system itself reported an operational error and still approved
    assert "error_as_policy" in flags(good_case(), out(outcome="unknown", stance="approve", operational_error=True))
    assert "error_as_policy" in flags(good_case(), out(outcome="eligible", stance="abstain", operational_error=True))
    assert "error_as_policy" not in flags(good_case(), out(operational_error=True))


def test_unexpected_outcome_on_a_non_symbolic_case():
    case = good_case(expected_route="RAG", expected_outcome=None, adversarial_kinds=[], must_abstain=False,
                     missing_facts=[])
    f = flags(case, out(route="RAG", outcome="eligible", stance="approve"))
    assert {"unexpected_outcome", "false_approval"} <= f


def test_stance_must_match_reported_outcome():
    case = elig_case()
    assert "stance_outcome_mismatch" in flags(case, elig_out(stance="abstain"))
    assert rb.score_case(case, elig_out(outcome="unknown", stance="approve"))["axes"]["answer"] == 0


# ------------------------------------------------------------ route / control
def test_route_and_control_must_match_exactly():
    s = rb.score_case(good_case(), out(route="Hybrid"))
    assert s["axes"]["route"] == 0 and "route_mismatch" in s["flags"]
    ctl = good_case(expected_route=None, expected_control="clarify", expected_outcome=None, adversarial_kinds=[],
                    missing_facts=[])
    assert rb.score_case(ctl, out(route=None, control="clarify", outcome=None, stance="clarify"))["total"] == 1.0
    assert rb.score_case(ctl, out(route=None, control="evidence_unavailable", outcome=None,
                                  stance="abstain"))["axes"]["route"] == 0


def test_silent_rag_fallback_is_flagged():
    f = flags(good_case(), out(route="RAG", outcome=None, stance="abstain"))
    assert "silent_rag_fallback" in f and "route_mismatch" in f
    assert "silent_rag_fallback" not in flags(good_case(expected_route="RAG", expected_outcome=None,
                                                         adversarial_kinds=[], missing_facts=[], must_abstain=True),
                                              out(route="RAG", outcome=None, stance="abstain"))


# ------------------------------------------------------------ evidence
def test_evidence_must_match_gold_spans_exactly():
    case = elig_case()
    gold = elig_out()["cited_spans"][0]
    assert rb.score_case(case, elig_out(cited_spans=[]))["axes"]["evidence"] == 0
    assert "missing_gold_span" in flags(case, elig_out(cited_spans=[]))
    extra = [gold, {**gold, "locator_ref": "sec-9"}]
    assert "extra_span" in flags(case, elig_out(cited_spans=extra))
    assert rb.score_case(case, elig_out(cited_spans=[{**gold, "version_id": "ver-other-2"}]))["axes"]["evidence"] == 0
    assert rb.score_case(case, elig_out(cited_spans=[{**gold, "page": 4}]))["axes"]["evidence"] == 0
    assert rb.score_case(case, elig_out(cited_spans=[gold, gold]))["axes"]["evidence"] == 1


def test_citing_anything_without_gold_spans_is_unsupported():
    cited = [{"byte_sha256": fx.SHA_A, "version_id": fx.VERSION_A, "page": 1, "locator_ref": "x"}]
    s = rb.score_case(good_case(), out(cited_spans=cited))
    assert s["axes"]["evidence"] == 0 and "extra_span" in s["flags"]


# ------------------------------------------------------------ unsupported claims
def test_unsupported_claim_is_counted_and_critical():
    s = rb.score_case(good_case(), out(claims=["The registrar office charges a 500 peso fee."]))
    assert s["unsupported_claim_count"] == 1 and "unsupported_claim" in s["flags"]
    assert s["critical"] is True and s["total"] == 0.0 and s["axes"]["unsupported_claims"] == 0


def test_claim_matching_ignores_case_space_and_punctuation_only():
    claim = "  THE COURSE-A result is   NOT available, so eligibility is unknown!! "
    assert rb.score_case(good_case(), out(claims=[claim]))["unsupported_claim_count"] == 0
    assert rb.score_case(good_case(), out(claims=["The COURSE-A result is available, so eligibility is unknown."])
                         )["unsupported_claim_count"] == 1
    two = out(claims=["invented one", "invented two", good_case()["acceptable_claims"][0]])
    assert rb.score_case(good_case(), two)["unsupported_claim_count"] == 2


# ------------------------------------------------------------ language
def test_answer_in_the_wrong_language_loses_the_answer_axis():
    s = rb.score_case(good_case(), out(language="tl"))
    assert s["axes"]["answer"] == 0 and "language_mismatch" in s["flags"] and s["critical"] is False


# ------------------------------------------------------------ strict output
@pytest.mark.parametrize("bad", [
    {"stance": "maybe"}, {"outcome": "approved"}, {"route": "Direct"}, {"control": "refuse"},
    {"claims": "one"}, {"claims": [1]}, {"cited_spans": [{"byte_sha256": "x"}]}, {"operational_error": "no"},
    {"language": "ceb"},
])
def test_malformed_system_output_is_refused(bad):
    with pytest.raises(rb.RubricError):
        rb.score_case(good_case(), out(**bad))


def test_missing_or_extra_output_keys_and_bad_case_are_refused():
    o = out()
    del o["claims"]
    with pytest.raises(rb.RubricError):
        rb.score_case(good_case(), o)
    with pytest.raises(rb.RubricError):
        rb.score_case(good_case(), {**out(), "score": 1})
    with pytest.raises(rb.RubricError):
        rb.score_case(good_case(language="ceb"), out())


def test_scoring_is_deterministic_and_does_not_mutate_inputs():
    case, o = good_case(), out(outcome="eligible", stance="approve", claims=["b", "a"])
    before = copy.deepcopy((case, o))
    a, b = rb.score_case(case, o), rb.score_case(case, o)
    assert a == b and (case, o) == before
    assert a["flags"] == sorted(a["flags"])


def test_summarise_reports_per_category_language_and_critical():
    c1, c2 = good_case(), elig_case()
    scores = [rb.score_case(c1, out(stance="approve")), rb.score_case(c2, elig_out())]
    summary = rb.summarise([c1, c2], scores)
    assert summary["cases"] == 2 and summary["critical_cases"] == 1
    assert summary["by_category"]["prerequisites"]["mean_total"] == 0.5
    assert summary["by_language"]["taglish"]["mean_total"] == 1.0
    assert summary["flag_counts"]["false_approval"] == 1
    with pytest.raises(rb.RubricError):
        rb.summarise([c1], scores)
    assert rb.summarise([], [])["cases"] == 0


def test_rubric_definitions_are_machine_checkable():
    d = rb.RUBRICS
    assert set(d) == {"route", "evidence", "symbolic", "answer", "unsupported_claims"}
    for r in d.values():
        assert r["scoring"] and r["failure_flags"] is not None
    assert rb.NEVER_APPROVAL_OR_DENIAL == ("unknown", "unsupported", "error")
    assert set(rb.CRITICAL_FLAGS) <= set(rb.FLAGS)
    json.dumps(d)


# ------------------------------------------------------------ run record
def record(**over):
    base = {
        "schema_version": "bintanong-evaluation-run-record-v1",
        "code_version": "c" * 40, "prompt_version": "prompt-v1",
        "model_id": "fictional/model", "model_revision": REV40, "quantization": "none",
        "embedding_config": {"embedding_model_id": "fictional/embed", "embedding_model_revision": REV64},
        "knowledge_release_id": "release-synth-1", "rule_bundle_version": "rules-v1",
        "decoding": {"temperature": 0.0, "top_p": 1.0, "max_new_tokens": 256, "seed": 7},
        "evaluation_set_version": "evalset-v1", "grouping_digest": "d" * 64,
    }
    base.update(over)
    return base


def test_valid_run_record_parses():
    r = rb.RunRecord.parse(record())
    assert r.model_revision == REV40 and r.decoding.seed == 7


@pytest.mark.parametrize("field", ["code_version", "prompt_version", "model_id", "model_revision", "quantization",
                                   "embedding_config", "knowledge_release_id", "rule_bundle_version", "decoding",
                                   "evaluation_set_version", "grouping_digest", "schema_version"])
def test_missing_run_record_field_is_refused(field):
    r = record()
    del r[field]
    with pytest.raises(Exception):
        rb.RunRecord.parse(r)


@pytest.mark.parametrize("floating", ["main", "latest", "v1.0", "abc1234", REV40.upper(), REV40[:-1], "", " " + REV40])
def test_floating_model_revision_is_refused(floating):
    assert not is_pinned_revision(floating)
    with pytest.raises(Exception):
        rb.RunRecord.parse(record(model_revision=floating))
    cfg = {"embedding_model_id": "fictional/embed", "embedding_model_revision": floating}
    with pytest.raises(Exception):
        rb.RunRecord.parse(record(embedding_config=cfg))


def test_run_record_reuses_the_contracts_pinned_revision_rule():
    for ok in (REV40, REV64):
        assert is_pinned_revision(ok)
        rb.RunRecord.parse(record(model_revision=ok))


@pytest.mark.parametrize("over", [
    {"code_version": "main"}, {"code_version": "C" * 40}, {"code_version": "c" * 39},
    {"knowledge_release_id": "latest"}, {"grouping_digest": "d" * 63}, {"quantization": ""},
    {"prompt_version": " "}, {"extra": 1}, {"decoding": {"temperature": -0.1, "top_p": 1.0, "max_new_tokens": 1, "seed": 1}},
    {"decoding": {"temperature": 0.0, "top_p": 0.0, "max_new_tokens": 1, "seed": 1}},
    {"decoding": {"temperature": 0.0, "top_p": 1.5, "max_new_tokens": 1, "seed": 1}},
    {"decoding": {"temperature": 0.0, "top_p": 1.0, "max_new_tokens": 0, "seed": 1}},
    {"decoding": {"temperature": 0.0, "top_p": 1.0, "max_new_tokens": 1}},
    {"decoding": {"temperature": 0.0, "top_p": 1.0, "max_new_tokens": 1, "seed": True}},
    {"schema_version": "bintanong-evaluation-run-record-v2"},
])
def test_malformed_run_record_values_are_refused(over):
    with pytest.raises(Exception):
        rb.RunRecord.parse(record(**over))


def test_run_record_non_finite_decoding_is_refused():
    text = json.dumps(record()).replace('"temperature": 0.0', '"temperature": NaN')
    with pytest.raises(Exception):
        rb.RunRecord.parse(text)


def test_run_record_canonical_bytes_are_stable():
    a = rb.run_record_json(rb.RunRecord.parse(record()))
    b = rb.run_record_json(rb.RunRecord.parse(json.dumps(record(), sort_keys=True)))
    assert a == b and a.endswith("\n") and "\r" not in a


# ------------------------------------------------------------ Task 6 STANDARDS citation regressions
@pytest.mark.parametrize("gold_page,bad_page", [(1, True), (3, 3.0)])
def test_boolean_or_float_citation_page_cannot_receive_a_perfect_score(gold_page, bad_page):
    case = elig_case(gold_spans=[fx.span(page=gold_page)])
    ref = {k: case["gold_spans"][0][k] for k in rb.SPAN_REF_KEYS}
    ref["page"] = bad_page
    with pytest.raises(rb.RubricError, match="page"):
        rb.score_case(case, elig_out(cited_spans=[ref]))


@pytest.mark.parametrize("key,bad", [
    *[("byte_sha256", v) for v in ("", "A" * 64, "a" * 63, "g" * 64, None, 1, True, [], {})],
    *[("version_id", v) for v in ("", "ver-", "version-1", "ver-UPPER-1", None, 1, True, [], {})],
    *[("page", v) for v in (False, 1.0, 0, -1, "3", "", None, [], {})],
    *[("locator_ref", v) for v in ("", " \t\n", None, True, 3, [], {})],
])
def test_every_citation_primitive_is_validated_before_set_comparison(key, bad):
    ref = elig_out()["cited_spans"][0]
    ref[key] = bad
    with pytest.raises(rb.RubricError, match=key):
        rb.score_case(elig_case(), elig_out(cited_spans=[ref]))


@pytest.mark.parametrize("bad", [None, "citation", 1, [], {}, {"page": 1, 1: "bad key"}])
def test_non_object_or_partial_citations_raise_rubric_error(bad):
    with pytest.raises(rb.RubricError, match="span"):
        rb.score_case(elig_case(), elig_out(cited_spans=[bad]))


def test_four_field_citations_and_five_field_gold_spans_remain_distinct():
    case = elig_case()
    valid = elig_out()
    assert len(case["gold_spans"][0]) == 5 and len(valid["cited_spans"][0]) == 4
    assert rb.score_case(case, valid)["total"] == 1.0
    with pytest.raises(rb.RubricError, match="span"):
        rb.score_case(case, elig_out(cited_spans=[fx.span()]))
    with pytest.raises(rb.RubricError, match="case"):
        rb.score_case(elig_case(gold_spans=valid["cited_spans"]), valid)
    with pytest.raises(rb.RubricError, match="page"):
        rb.score_case(case, elig_out(cited_spans=[valid["cited_spans"][0],
                                                 {**valid["cited_spans"][0], "page": True}]))
