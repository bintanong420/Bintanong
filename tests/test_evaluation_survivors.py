"""Phase 1 Task 5: tests added after the first mutation pass left twelve mutants alive."""

from __future__ import annotations

import test_evaluation_fixtures as fx
from evaluation import protocol as pr
from evaluation import rubrics as rb
from test_evaluation_case import findings
from test_evaluation_protocol import DEV, FINAL, codes, dev_case, final_case, group_for
from test_evaluation_rubrics import elig_case, elig_out, good_case, out


# ---- case.py: a non-determinate outcome must abstain, with no other rule to hide behind
def test_non_determinate_outcome_without_abstention_is_refused_on_its_own():
    for outcome in ("unknown", "unsupported", "error"):
        c = fx.case(expected_outcome=outcome, adversarial_kinds=[], missing_facts=[], must_abstain=False)
        assert any("never an approval" in f for f in findings(c)), outcome


# ---- protocol.py
def test_near_duplicate_threshold_is_inclusive_at_exactly_point_eight():
    assert pr.similarity("aaa bbb ccc ddd", "aaa bbb ccc ddd eee") == 0.8
    other = group_for("dev", "grp-eq")
    a = dev_case(1, query="aaa bbb ccc ddd")
    b = dev_case(2, group=other, query="aaa bbb ccc ddd eee")
    assert "near_duplicate_group_mismatch" in codes(pr.validate_case_set([a, b]))
    assert "near_duplicate_group_mismatch" not in codes(pr.validate_case_set([a, b], threshold=0.81))


def test_freeze_group_ids_must_be_sorted_and_unique():
    cases = [final_case(1), final_case(2, group=group_for("final", "grp-srt"))]
    fr = pr.make_freeze(cases, registry=fx.REGISTRY)
    assert len(fr["final_group_ids"]) == 2
    flipped = dict(fr, final_group_ids=list(reversed(fr["final_group_ids"])))
    flipped["digest"] = pr.freeze_digest(flipped)                 # a consistent digest does not excuse the order
    assert "freeze_malformed" in codes(pr.validate_case_set(cases, registry=fx.REGISTRY, freeze=flipped))
    doubled = dict(fr, final_group_ids=[fr["final_group_ids"][0]] * 2)
    doubled["digest"] = pr.freeze_digest(doubled)
    assert "freeze_malformed" in codes(pr.validate_case_set(cases, registry=fx.REGISTRY, freeze=doubled))


def test_every_category_needs_ten_even_when_the_total_reaches_fifty():
    plan = {"enrollment": 9, "prerequisites": 9, "grades": 9, "academic_standing": 9, "discipline": 14}
    cases, n = [], 0
    for cat, count in plan.items():
        for _ in range(count):
            n += 1
            cases.append(final_case(n, group=group_for("final", f"grp-p{n}"), category=cat))
    cov = pr.validate_case_set(cases, registry=fx.REGISTRY)["coverage"]
    assert cov["verified_final_taglish_total"] == 50 and cov["met"] is False


def test_findings_are_emitted_sorted_by_code_subject_detail():
    rep = pr.validate_case_set([dev_case(1, group=FINAL), final_case(2, group=DEV), dev_case(3, group=DEV)],
                               registry=fx.REGISTRY)
    keys = [(f["code"], f["subject"], f["detail"]) for f in rep["findings"]]
    assert len(set(f["code"] for f in rep["findings"])) >= 2
    assert keys == sorted(keys)
    assert "group_split_leak" in codes(rep)


# ---- rubrics.py: the outcome rules must work without the stance rules covering for them
def test_reported_outcome_alone_is_judged_against_gold():
    assert "false_approval" in set(rb.score_case(good_case(), out(outcome="eligible", stance="abstain"))["flags"])
    assert "false_denial" in set(rb.score_case(good_case(), out(outcome="ineligible", stance="abstain"))["flags"])
    assert "false_abstention" in set(rb.score_case(elig_case(), elig_out(outcome="unknown", stance="approve"))["flags"])


def test_false_denial_and_error_as_policy_each_zero_the_total_on_their_own():
    s = rb.score_case(elig_case(), elig_out(outcome="ineligible", stance="deny"))
    assert s["critical"] is True and s["total"] == 0.0
    # correct decision, yet the system said it hit an operational error: only error_as_policy fires
    s = rb.score_case(elig_case(), elig_out(operational_error=True))
    assert s["flags"] == ["error_as_policy"] and s["critical"] is True and s["total"] == 0.0
    assert rb.CRITICAL_FLAGS == ("false_approval", "false_denial", "error_as_policy", "unsupported_claim")


def test_a_clarify_control_accepts_only_a_clarifying_stance():
    ctl = good_case(expected_route=None, expected_control="clarify", expected_outcome=None, adversarial_kinds=[],
                    missing_facts=[])
    ok = out(route=None, control="clarify", outcome=None, stance="clarify")
    assert rb.score_case(ctl, ok)["axes"]["answer"] == 1
    assert rb.score_case(ctl, {**ok, "stance": "abstain"})["axes"]["answer"] == 0
