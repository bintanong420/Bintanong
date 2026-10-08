"""Phase 1 Task 5 group 1: the evaluation case schema and its strict checker."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import test_evaluation_fixtures as fx
from backend.bintanong_contracts.base import VOCAB
from evaluation import case as ec

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "evaluation" / "case.schema.json").read_text(encoding="utf-8"))


def findings(c):
    return ec.case_findings(c)


def test_valid_synthetic_case_has_no_findings():
    assert findings(fx.case()) == []


def test_valid_verified_case_has_no_findings():
    assert findings(fx.verified()) == []


def test_vocabularies_come_from_governance_vocabulary():
    assert ec.ROUTES == tuple(VOCAB["runtime"]["routes"])
    assert ec.CONTROLS == tuple(VOCAB["runtime"]["controls"])
    assert ec.OUTCOMES == tuple(VOCAB["decision"]["outcomes"])
    assert len(ec.OUTCOMES) == 5
    assert ec.CATEGORIES == ("enrollment", "prerequisites", "grades", "academic_standing", "discipline")
    assert ec.LANGUAGES == ("en", "tl", "taglish")
    assert ec.STATUSES == ("synthetic", "candidate", "verified")
    assert ec.ADVERSARIAL_KINDS == ("ambiguity", "negation", "missing_facts", "wrong_edition",
                                    "conflicting_evidence", "unknown_course", "incomplete_coverage",
                                    "unsupported_operation", "operational_failure")


def test_schema_enums_match_code():
    props = SCHEMA["properties"]
    assert tuple(props["category"]["enum"]) == ec.CATEGORIES
    assert tuple(props["language"]["enum"]) == ec.LANGUAGES
    assert tuple(props["status"]["enum"]) == ec.STATUSES
    assert tuple(props["split"]["enum"]) == ec.SPLITS
    assert tuple(props["adversarial_kinds"]["items"]["enum"]) == ec.ADVERSARIAL_KINDS
    assert set(props["expected_route"]["enum"]) == set(ec.ROUTES) | {None}
    assert set(props["expected_control"]["enum"]) == set(ec.CONTROLS) | {None}
    assert set(props["expected_outcome"]["enum"]) == set(ec.OUTCOMES) | {None}
    assert set(SCHEMA["required"]) == set(props) == set(ec.CASE_KEYS)
    assert SCHEMA["additionalProperties"] is False
    assert props["schema_version"]["const"] == ec.SCHEMA_VERSION


@pytest.mark.parametrize("field,value", [
    ("category", "housing"), ("language", "ceb"), ("status", "approved"), ("split", "test"),
    ("expected_route", "Direct"), ("expected_control", "refuse"), ("expected_outcome", "maybe"),
    ("schema_version", "bintanong-evaluation-case-v2"), ("case_id", "Bad Id"), ("group_id", "syn-prereq"),
    ("query", ""), ("query", "   "), ("query", "?!"), ("must_abstain", "yes"),
])
def test_malformed_field_is_refused(field, value):
    assert findings(fx.case(**{field: value}))


def test_missing_and_unknown_keys_are_refused():
    c = fx.case()
    del c["query"]
    assert findings(c)
    c = fx.case()
    c["student_number"] = "x"
    assert findings(c)
    assert findings("not a mapping")


def test_unknown_adversarial_kind_and_duplicates_are_refused():
    assert findings(fx.case(adversarial_kinds=["trick"]))
    assert findings(fx.case(adversarial_kinds=["missing_facts", "missing_facts"]))


def test_route_xor_control_and_outcome_needs_route():
    assert findings(fx.case(expected_route=None, expected_control=None))
    assert findings(fx.case(expected_route="RAG", expected_control="clarify", expected_outcome=None))
    assert findings(fx.case(expected_route=None, expected_control="clarify", expected_outcome="unknown"))
    assert findings(fx.case(expected_route="RAG", expected_outcome="unknown"))
    assert findings(fx.case(expected_route="Symbolic", expected_outcome=None))


def test_synthetic_cannot_be_verified_or_carry_gold_or_final():
    assert findings(fx.case(status="verified"))
    assert findings(fx.case(gold_spans=[fx.span()]))
    assert findings(fx.case(gold_rules=["rule-x"]))
    assert findings(fx.case(split="final"))
    assert findings(fx.case(synthetic_policy=None))
    assert findings(fx.case(review={"author": "a", "reviewer": "r", "evidence_ref": None, "review_version": None}))


def test_scope_null_needs_reason_and_reason_needs_null_scope():
    assert findings(fx.case(scope_null_reason=None))
    assert findings(fx.case(scope={"institution": "fictional", "edition": "e", "version_id": None}))


def test_verified_requires_independent_source_backed_review():
    assert findings(fx.verified(gold_spans=[]))
    for key in ("reviewer", "evidence_ref", "review_version", "author"):
        review = dict(fx.verified()["review"])
        review[key] = None
        assert findings(fx.verified(review=review)), key
    same = {"author": "Pat", "reviewer": " pat ", "evidence_ref": "ev-1", "review_version": "rv-1"}
    assert any("independent" in f for f in findings(fx.verified(review=same)))
    assert findings(fx.verified(scope=None, scope_null_reason="x"))
    assert findings(fx.verified(synthetic_policy="Synthetic rule"))


def test_candidate_with_equal_author_and_reviewer_is_refused():
    review = {"author": "pat", "reviewer": "pat", "evidence_ref": None, "review_version": None}
    assert findings(fx.verified(status="candidate", review=review))


def test_gold_span_shape():
    assert findings(fx.verified(gold_spans=[fx.span(byte_sha256="short")]))
    assert findings(fx.verified(gold_spans=[fx.span(version_id="synth")]))
    assert findings(fx.verified(gold_spans=[fx.span(page=0)]))
    assert findings(fx.verified(gold_spans=[fx.span(page=True)]))
    assert findings(fx.verified(gold_spans=[fx.span(locator_ref="")]))
    assert findings(fx.verified(gold_spans=[fx.span(text_sha256="zz")]))
    assert findings(fx.verified(gold_spans=[{**fx.span(), "text": "passage"}]))


def test_abstention_consistency_with_outcome_and_control():
    assert findings(fx.case(must_abstain=False))                              # unknown must abstain
    assert findings(fx.verified(must_abstain=True))                           # eligible must not
    assert findings(fx.case(expected_route=None, expected_control="clarify", expected_outcome=None,
                            adversarial_kinds=[], must_abstain=False, missing_facts=[]))
    assert findings(fx.case(expected_route=None, expected_control="greeting", expected_outcome=None,
                            adversarial_kinds=[], must_abstain=True, missing_facts=[]))


@pytest.mark.parametrize("kind,over", [
    ("missing_facts", {"missing_facts": []}),
    ("unsupported_operation", {"expected_route": "Symbolic", "expected_outcome": "unknown"}),
    ("operational_failure", {"expected_route": "Symbolic", "expected_outcome": "unknown"}),
    ("wrong_edition", {"must_abstain": False, "expected_outcome": "eligible"}),
    ("ambiguity", {"must_abstain": False, "expected_outcome": "eligible"}),
])
def test_adversarial_kind_rules(kind, over):
    assert findings(fx.case(adversarial_kinds=[kind], **over))


def test_private_identity_is_refused():
    assert findings(fx.case(query="Email me at ana@example.com about COURSE-A"))
    assert findings(fx.case(query="Student 202380180 asks about COURSE-A"))
    assert findings(fx.case(acceptable_claims=["Contact 202380180"]))


def test_text_lists_must_be_nonblank_strings():
    assert findings(fx.case(required_facts=[""]))
    assert findings(fx.case(missing_facts=[1]))
    assert findings(fx.case(acceptable_claims="one claim"))
