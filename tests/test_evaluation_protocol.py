"""Phase 1 Task 5 group 2: split/group validation, freeze, leakage, near-duplicates, coverage."""

from __future__ import annotations

import copy
import hashlib
import json

import pytest

import test_evaluation_fixtures as fx
from evaluation import protocol as pr
from evaluation.case import CATEGORIES


def group_for(split, prefix="grp-t"):
    """A fictional group id whose derived split is `split`."""
    for i in range(500):
        g = f"{prefix}-{i}"
        if pr.derive_split(g) == split:
            return g
    raise AssertionError("no group found")


DEV = group_for("dev")
FINAL = group_for("final", "grp-f")


def dev_case(n=1, group=DEV, query=None, **over):
    return fx.case(case_id=f"syn-case-{n:03d}", group_id=group,
                   query=query or f"Distinct synthetic question number {n} about unique topic{n} alpha{n} beta{n}",
                   **over)


def final_case(n=1, group=FINAL, **over):
    return fx.verified(case_id=f"ver-case-{n:03d}", group_id=group,
                       query=f"Verified final question {n} regarding sample topic{n} gamma{n} delta{n}", **over)


def codes(report):
    return sorted({f["code"] for f in report["findings"]})


def validate(cases, **kw):
    return pr.validate_case_set(cases, **kw)


# ---------------------------------------------------------------- split derivation
def test_derive_split_is_stable_and_salted():
    assert pr.derive_split("grp-abc") == pr.derive_split("grp-abc")
    splits = {pr.derive_split(f"grp-x-{i}") for i in range(200)}
    assert splits == {"dev", "final"}
    assert {pr.derive_split(f"grp-x-{i}", salt="other") for i in range(200)} == {"dev", "final"}
    moved = sum(pr.derive_split(f"grp-x-{i}") != pr.derive_split(f"grp-x-{i}", salt="other") for i in range(200))
    assert moved > 0
    final = sum(pr.derive_split(f"grp-y-{i}") == "final" for i in range(1000))
    assert 200 < final < 400                      # default 30 percent


def test_derive_split_ignores_case_content_and_order():
    cases = [dev_case(1), dev_case(2)]
    assert validate(cases)["findings"] == validate(list(reversed(cases)))["findings"] == []
    extra = validate(cases + [dev_case(3, group=group_for("dev", "grp-other"))])
    assert extra["findings"] == []


def test_split_not_derived_from_group_is_a_finding():
    assert "split_not_derived" in codes(validate([dev_case(1, group=FINAL)]))
    assert "split_not_derived" in codes(validate([final_case(1, group=DEV)], registry=fx.REGISTRY))


# ---------------------------------------------------------------- leakage / groups
def test_group_in_both_splits_is_a_leak():
    rep = validate([dev_case(1), final_case(2, group=DEV)], registry=fx.REGISTRY)
    assert "group_split_leak" in codes(rep)


def test_group_with_mixed_categories_is_a_finding():
    a, b = dev_case(1), dev_case(2, category="grades")
    assert "group_mixed_category" in codes(validate([a, b]))


def test_duplicate_case_ids():
    assert "duplicate_case_id" in codes(validate([dev_case(1), dev_case(1, query="Another wording entirely zzz qqq")]))


def test_malformed_case_is_reported_with_its_findings():
    rep = validate([dev_case(1, language="ceb")])
    assert "case_invalid" in codes(rep)


# ---------------------------------------------------------------- near duplicates
def test_normalised_similarity():
    assert pr.similarity("Can I enroll?", "can i ENROLL") == 1.0
    assert pr.similarity("alpha beta", "gamma delta") == 0.0
    assert pr.similarity("", "") == 0.0
    assert pr.NEAR_DUPLICATE_THRESHOLD == 0.8


def test_near_duplicate_with_different_group_is_a_finding():
    other = group_for("dev", "grp-nd")
    a = dev_case(1, query="Can I enroll in COURSE-B without my COURSE-A grade posted yet")
    b = dev_case(2, group=other, query="Can I enroll in COURSE-B without my COURSE-A grade posted yet?")
    assert "near_duplicate_group_mismatch" in codes(validate([a, b]))


def test_near_duplicate_in_same_group_is_fine_and_threshold_is_inclusive():
    a = dev_case(1, query="one two three four five")
    b = dev_case(2, query="one two three four five")
    assert validate([a, b])["findings"] == []
    other = group_for("dev", "grp-nd")
    c = dev_case(3, group=other, query="one two three four six")      # 4/6 similar: below 0.8
    assert validate([a, c])["findings"] == []
    d = dev_case(4, group=other, query="one two three four five six seven eight nine ten")
    e = dev_case(5, group=DEV, query="one two three four five six seven eight nine eleven")  # 9/11 = 0.818
    assert "near_duplicate_group_mismatch" in codes(validate([d, e]))
    f = dev_case(6, group=DEV, query="one two three four five six seven eight nine ten")
    assert "near_duplicate_group_mismatch" in codes(validate([d, f]))      # identical
    exact = pr.similarity("a b c d e", "a b c d x")                      # 4/6
    assert exact < pr.NEAR_DUPLICATE_THRESHOLD


def test_threshold_is_a_parameter():
    other = group_for("dev", "grp-nd")
    a = dev_case(1, query="one two three four five")
    c = dev_case(3, group=other, query="one two three four six")
    assert "near_duplicate_group_mismatch" in codes(validate([a, c], threshold=0.6))


# ---------------------------------------------------------------- source registry / verified
def test_verified_final_span_must_resolve_to_registered_source():
    good = validate([final_case(1)], registry=fx.REGISTRY)
    assert good["findings"] == []
    assert "unregistered_source" in codes(validate([final_case(1)]))                 # no registry
    assert "unregistered_source" in codes(validate([final_case(1)], registry={"ver-other": fx.SHA_A}))
    assert "unregistered_source" in codes(validate([final_case(1)], registry={fx.VERSION_A: fx.SHA_B}))
    bad = final_case(1, gold_spans=[fx.span(), fx.span(version_id="ver-unregistered-9")])
    assert "unregistered_source" in codes(validate([bad], registry=fx.REGISTRY))


def test_final_synthetic_is_refused_by_the_set_check():
    assert "case_invalid" in codes(validate([dev_case(1, group=FINAL, split="final")]))


# ---------------------------------------------------------------- freeze
def test_make_freeze_is_sorted_and_digested():
    cases = [final_case(2), final_case(1), final_case(3, group=group_for("final", "grp-g"))]
    fr = pr.make_freeze(cases, registry=fx.REGISTRY)
    assert fr["final_group_ids"] == sorted(fr["final_group_ids"]) == sorted({c["group_id"] for c in cases})
    assert set(fr["final_case_digests"]) == {c["case_id"] for c in cases}
    assert fr["salt"] == pr.SPLIT_SALT and fr["schema_version"] == pr.FREEZE_VERSION
    assert fr["digest"] == pr.freeze_digest(fr)
    assert pr.make_freeze(list(reversed(cases)), registry=fx.REGISTRY) == fr


def test_make_freeze_refuses_empty_unverified_or_dev_only():
    with pytest.raises(ValueError):
        pr.make_freeze([dev_case(1)], registry=fx.REGISTRY)
    with pytest.raises(ValueError):
        pr.make_freeze([final_case(1, status="candidate")], registry=fx.REGISTRY)
    with pytest.raises(ValueError):
        pr.make_freeze([final_case(1)])                      # span does not resolve without a registry


def test_untouched_frozen_set_validates():
    cases = [final_case(1), dev_case(2)]
    fr = pr.make_freeze(cases, registry=fx.REGISTRY)
    rep = validate(cases + [dev_case(3, group=group_for("dev", "grp-new"))], registry=fx.REGISTRY, freeze=fr)
    assert rep["findings"] == []


def test_frozen_case_edit_is_a_finding():
    cases = [final_case(1)]
    fr = pr.make_freeze(cases, registry=fx.REGISTRY)
    edited = copy.deepcopy(cases)
    edited[0]["acceptable_claims"] = ["A different claim."]
    assert "freeze_case_edited" in codes(validate(edited, registry=fx.REGISTRY, freeze=fr))


def test_frozen_group_moved_is_a_finding():
    cases = [final_case(1)]
    fr = pr.make_freeze(cases, registry=fx.REGISTRY)
    moved = copy.deepcopy(cases)
    moved[0]["split"] = "dev"
    assert "freeze_group_moved" in codes(validate(moved, registry=fx.REGISTRY, freeze=fr))
    other = group_for("dev", "grp-mv")
    regrouped = copy.deepcopy(cases)
    regrouped[0]["group_id"] = other
    assert "freeze_case_missing" in codes(validate(regrouped, registry=fx.REGISTRY, freeze=fr)) or \
        "freeze_case_edited" in codes(validate(regrouped, registry=fx.REGISTRY, freeze=fr))


def test_frozen_case_removed_or_added_is_a_finding():
    cases = [final_case(1), final_case(2)]
    fr = pr.make_freeze(cases, registry=fx.REGISTRY)
    assert "freeze_case_missing" in codes(validate(cases[:1], registry=fx.REGISTRY, freeze=fr))
    assert "freeze_case_added" in codes(validate(cases + [final_case(3)], registry=fx.REGISTRY, freeze=fr))
    assert "freeze_group_added" in codes(validate(
        cases + [final_case(4, group=group_for("final", "grp-late"))], registry=fx.REGISTRY, freeze=fr))


def test_tampered_freeze_record_is_a_finding():
    cases = [final_case(1)]
    fr = pr.make_freeze(cases, registry=fx.REGISTRY)
    t = copy.deepcopy(fr)
    t["final_group_ids"] = []
    assert "freeze_digest_mismatch" in codes(validate(cases, registry=fx.REGISTRY, freeze=t))
    t = copy.deepcopy(fr)
    t["final_case_digests"]["ver-case-001"] = "0" * 64
    assert "freeze_digest_mismatch" in codes(validate(cases, registry=fx.REGISTRY, freeze=t))
    t = copy.deepcopy(fr)
    t["salt"] = "different"
    t["digest"] = pr.freeze_digest(t)
    assert "freeze_salt_mismatch" in codes(validate(cases, registry=fx.REGISTRY, freeze=t))
    assert "freeze_malformed" in codes(validate(cases, registry=fx.REGISTRY, freeze={"digest": "x"}))
    t = copy.deepcopy(fr)
    t["schema_version"] = "v0"
    assert "freeze_malformed" in codes(validate(cases, registry=fx.REGISTRY, freeze=t))


# ---------------------------------------------------------------- prompt example leakage
def test_final_case_text_reused_as_prompt_example_is_a_finding():
    cases = [final_case(1)]
    q = cases[0]["query"]
    assert pr.prompt_example_findings(cases, ["unrelated example text here"]) == []
    assert pr.prompt_example_findings(cases, [q])[0]["code"] == "final_text_in_prompt_example"
    assert pr.prompt_example_findings(cases, [q.upper() + "!!"])
    assert pr.prompt_example_findings(cases, [cases[0]["acceptable_claims"][0]])
    assert "final_text_in_prompt_example" in codes(validate(cases, registry=fx.REGISTRY, prompt_examples=[q]))
    assert pr.prompt_example_findings([dev_case(1)], [dev_case(1)["query"]]) == []    # dev text may be reused


def test_near_copy_of_final_text_in_prompt_example_is_a_finding():
    q = final_case(1)["query"]
    assert pr.prompt_example_findings([final_case(1)], [q + " please"])


# ---------------------------------------------------------------- coverage
def test_coverage_reports_not_met_with_zero_verified():
    rep = validate([dev_case(1)])
    cov = rep["coverage"]
    assert cov["met"] is False
    assert cov["verified_final_total"] == 0 and cov["verified_final_taglish_total"] == 0
    assert all(v == 0 for v in cov["verified_final_taglish_by_category"].values())
    assert set(cov["verified_final_taglish_by_category"]) == set(CATEGORIES)
    assert cov["status_line"].startswith("NOT MET: 0 verified final")
    assert cov["targets"] == {"per_category": 10, "taglish_total": 50}
    assert rep["integrity_ok"] is True                      # no findings, yet the gate is still NOT MET


def test_coverage_counts_only_valid_verified_final_taglish():
    cases = [final_case(1), final_case(2, language="en"), final_case(3, status="candidate"),
             dev_case(4)]
    cov = validate(cases, registry=fx.REGISTRY)["coverage"]
    assert cov["verified_final_total"] == 2
    assert cov["verified_final_taglish_total"] == 1
    assert cov["verified_final_taglish_by_category"]["prerequisites"] == 1
    assert cov["met"] is False
    unresolved = validate([final_case(1)])["coverage"]                 # no registry -> not counted
    assert unresolved["verified_final_total"] == 0


def test_coverage_met_only_at_targets():
    cats = ["enrollment", "prerequisites", "grades", "academic_standing", "discipline"]
    cases, n = [], 0
    for cat in cats:
        for _ in range(10):
            n += 1
            cases.append(final_case(n, group=group_for("final", f"grp-c{n}"), category=cat))
    cov = validate(cases, registry=fx.REGISTRY)["coverage"]
    assert cov["verified_final_taglish_total"] == 50 and cov["met"] is True
    assert cov["status_line"].startswith("MET:")
    short = validate(cases[:-1], registry=fx.REGISTRY)["coverage"]
    assert short["met"] is False and short["status_line"].startswith("NOT MET:")
    # 50 total but unbalanced: still not met
    lopsided = [final_case(i, group=group_for("final", f"grp-l{i}")) for i in range(1, 51)]
    assert validate(lopsided, registry=fx.REGISTRY)["coverage"]["met"] is False


def test_claimed_met_with_zero_verified_is_a_finding():
    cases = [dev_case(1)]
    claim = {"met": True, "status_line": "MET: everything"}
    assert "coverage_claim_false" in codes(validate(cases, coverage_claim=claim))
    honest = validate(cases)["coverage"]
    assert validate(cases, coverage_claim=honest)["findings"] == []
    assert pr.coverage_claim_findings(cases, {"met": False}) == []
    assert pr.coverage_claim_findings(cases, "met") != []


# ---------------------------------------------------------------- determinism / canonical json
def test_canonical_json_is_sorted_lf_and_stable():
    text = pr.canonical_json({"b": 1, "a": [3, {"z": 1, "y": "é"}]})
    assert text == '{\n  "a": [\n    3,\n    {\n      "y": "é",\n      "z": 1\n    }\n  ],\n  "b": 1\n}\n'
    assert "\r" not in text


def test_report_is_independent_of_case_order():
    cases = [dev_case(1), dev_case(2), dev_case(3, group=group_for("dev", "grp-o"))]
    a = pr.canonical_json(validate(cases))
    b = pr.canonical_json(validate(list(reversed(cases))))
    assert a == b


def test_case_digest_is_content_hash():
    c = dev_case(1)
    assert pr.case_digest(c) == hashlib.sha256(pr.canonical_json(c).encode("utf-8")).hexdigest()
    assert json.loads(pr.canonical_json(c)) == c


# ---------------------------------------------------------------- Task 6 SPEC regressions
@pytest.mark.parametrize("field", ["query", "acceptable_claims"])
@pytest.mark.parametrize("normalised", [False, True])
def test_final_text_embedded_in_long_context_is_leakage(field, normalised):
    c = final_case(1)
    text = c[field] if field == "query" else c[field][0]
    if normalised:
        text = text.upper().replace(" ", "\u00a0\n").replace(".", "!")
    example = " ".join(f"context{i}" for i in range(100)) + "\nFinal material: " + text
    assert pr.similarity(text, example) < pr.NEAR_DUPLICATE_THRESHOLD
    assert pr.prompt_example_findings([c], [example])[0]["code"] == "final_text_in_prompt_example"


@pytest.mark.parametrize("query,example", [("car", "scar"), ("car", "cart"),
                                          ("alpha beta", "beta alpha")])
def test_literal_leakage_needs_whole_words_in_order(query, example):
    c = final_case(1, acceptable_claims=[])
    c["query"] = query
    long_example = " ".join(f"context{i}" for i in range(100)) + " " + example
    assert pr.prompt_example_findings([c], [long_example]) == []


@pytest.mark.parametrize("wrong,extra_spans,registry", [
    ("ver-unregistered-wrong-1", [], fx.REGISTRY),
    ("ver-registered-other-1", [], {**fx.REGISTRY, "ver-registered-other-1": fx.SHA_A}),
    (fx.VERSION_A, [fx.span(version_id="ver-registered-other-1", byte_sha256=fx.SHA_B)],
     {**fx.REGISTRY, "ver-registered-other-1": fx.SHA_B}),
])
def test_declared_verified_version_must_resolve_to_all_gold_spans(wrong, extra_spans, registry):
    c = final_case(1)
    c["scope"]["version_id"] = wrong
    c["gold_spans"] += extra_spans
    report = pr.validate_case_set([c], registry=registry)
    assert "unregistered_source" in codes(report)
    assert report["integrity_ok"] is False
    assert pr.coverage([c], registry)["verified_final_total"] == 0
    with pytest.raises(ValueError, match="source-resolved"):
        pr.make_freeze([c], registry=registry)


def test_repeated_case_ids_cannot_create_independent_coverage_or_a_freeze():
    originals = [final_case(n + 1, group=group_for("final", f"grp-c{n}"), category=cat)
                 for n, cat in enumerate(CATEGORIES)]
    repeated = [case for case in originals for _ in range(10)]
    assert len({c["case_id"] for c in repeated}) == 5
    cov = pr.coverage(repeated, registry=fx.REGISTRY)
    assert cov["met"] is False and cov["verified_final_total"] == 0
    assert pr.coverage_claim_findings(repeated, {"met": True}, registry=fx.REGISTRY)
    assert "duplicate_case_id" in codes(validate(repeated, registry=fx.REGISTRY))
    with pytest.raises(ValueError, match="duplicate"):
        pr.make_freeze(repeated, registry=fx.REGISTRY)


def test_freeze_refuses_duplicate_ids_even_outside_final_and_coverage_excludes_conflicting_or_invalid_copies():
    with pytest.raises(ValueError, match="duplicate"):
        pr.make_freeze([final_case(1), dev_case(2), dev_case(2)], registry=fx.REGISTRY)
    for duplicate in (final_case(1, language="en"), {"case_id": final_case(1)["case_id"]}):
        cases = [final_case(1), duplicate, final_case(2)]
        assert pr.coverage(cases, registry=fx.REGISTRY)["verified_final_total"] == 1
