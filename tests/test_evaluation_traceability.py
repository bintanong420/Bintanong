"""Task 4: a synthetic exercise pins every link without promoting source authority."""

import copy
import hashlib
import json
from pathlib import Path

import pytest

from evaluation.traceability import check_trace
from evaluation.protocol import canonical_json, case_digest

ROOT = Path(__file__).resolve().parents[1]


def example():
    return json.loads((ROOT / "evaluation/examples/traceability-synthetic.json").read_text(encoding="utf-8"))


def test_executable_example_validates_and_roundtrips():
    trace = example()
    assert check_trace(trace) is None
    assert check_trace(json.loads(json.dumps(trace))) is None


@pytest.mark.parametrize("path,value,reason", [
    (("schema_version",), "v2", "schema_version"),
    (("verification_state",), "verified", "synthetic_only"),
    (("relation",), "source_supported_policy", "synthetic_exercise_only"),
    (("document", "byte_sha256"), "2" * 64, "digest"),
    (("document", "version_id"), "ver-other-1", "version_id"),
    (("document", "edition_id"), "edition-other-1", "edition_id"),
    (("document", "document_id"), "doc-other-1", "document_id"),
    (("chunk", "source_verification"), "observed", "evidence|verification"),
    (("binding", "chunk_id"), "2" * 64, "binding"),
    (("binding", "chunk_content_hash"), "2" * 64, "binding"),
    (("binding", "rule_id"), "rule-other-1", "binding"),
    (("binding", "rule_bundle_version"), "bundle-other-1", "binding"),
    (("binding", "rule_draft_digest"), "2" * 64, "binding"),
    (("binding", "case_id"), "syn-other-case", "binding"),
    (("binding", "case_digest"), "2" * 64, "binding"),
    (("content_check", "chunk_id"), "2" * 64, "content_check"),
    (("content_check", "content_hash"), "2" * 64, "content_check"),
    (("content_check", "state"), "source_verified", "cached_extraction"),
    (("content_check", "evidence_ref"), "", "evidence_ref"),
    (("case", "status"), "verified", "case|synthetic"),
    (("case", "query"), "Private fact-synth-0001", "another namespace"),
    (("rule_draft", "decision", "synthetic"), False, "synthetic"),
    (("rule_draft", "decision", "rule_coverage"), "verified", "coverage"),
    (("rule_draft", "capability"), "other", "capability"),
    (("rule_draft", "decision", "predicate"), "other", "registry"),
    (("rule_draft", "rule_ids"), ["rule-a", "rule-b"], "one rule"),
    (("rule_draft", "inputs", 0, "fact_ref"), "fact-synth-0001", "private|session"),
    (("case", "synthetic_policy"), "Different invented rule.", "synthetic policy"),
    (("case", "missing_facts"), ["another fact"], "missing facts"),
    (("case", "scope"), {"institution": "fictional", "edition": "v1", "version_id": None}, "scope"),
])
def test_changed_link_or_promotion_is_refused(path, value, reason):
    trace = example()
    node = trace
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = value
    with pytest.raises(ValueError, match=reason):
        check_trace(trace)


@pytest.mark.parametrize("field,value", [("page", 2), ("text", "Different printed text."),
                                         ("version_id", "ver-other-1"), ("byte_sha256", "2" * 64)])
def test_changed_rule_span_is_refused(field, value):
    trace = example()
    trace["rule_draft"]["rule_spans"][0][field] = value
    trace["binding"]["rule_draft_digest"] = hashlib.sha256(canonical_json(trace["rule_draft"]).encode("utf-8")).hexdigest()
    with pytest.raises(ValueError, match="span|version|digest"):
        check_trace(trace)


def test_ambiguous_or_partial_span_and_extra_keys_are_refused():
    for key in ("rule_draft", "binding"):
        trace = example()
        spans = trace[key]["rule_spans" if key == "rule_draft" else "source_spans"]
        spans.append(copy.deepcopy(spans[0]))
        with pytest.raises(ValueError, match="span"):
            check_trace(trace)
        spans.clear()
        with pytest.raises(ValueError, match="span"):
            check_trace(trace)
    trace = example()
    trace["approved"] = True
    with pytest.raises(ValueError, match="keys"):
        check_trace(trace)


def test_source_span_geometry_and_locator_are_pinned():
    for key, value in (("printed_page_label", "different"), ("locator", {
            "kind": "text_item", "item_ids": ["different"], "cell_ids": [], "ref": None, "table_index": None})):
        trace = example()
        trace["binding"]["source_spans"][0][key] = value
        with pytest.raises(ValueError, match="binding"):
            check_trace(trace)


@pytest.mark.parametrize("value", [True, 1.0])
def test_exact_binding_preserves_json_number_types(value):
    trace = example()
    trace["binding"]["source_spans"][0]["page"] = value
    with pytest.raises(ValueError, match="binding"):
        check_trace(trace)


@pytest.mark.parametrize("field,value", [("value", "DIFFERENT-COURSE"),
                                        ("prerequisite_rule_state", "unreadable")])
def test_valid_rule_edit_cannot_keep_the_original_binding(field, value):
    trace = example()
    if field == "value":
        trace["rule_draft"]["inputs"][0][field] = value
    else:
        trace["rule_draft"]["decision"][field] = value
    with pytest.raises(ValueError, match="binding"):
        check_trace(trace)


def test_cached_only_check_is_not_source_verification():
    trace = example()
    assert trace["document"]["verification_state"] == {"state": "pending", "evidence_ref": None}
    assert trace["document"]["approval_id"] is None
    assert trace["chunk"]["content_review"] == "pending"
    assert trace["case"]["gold_spans"] == trace["case"]["gold_rules"] == []
    assert check_trace(trace) is None


@pytest.mark.parametrize("state,kind", [("verification_state", "printed_text_span"),
                                      ("approval_state", "approval_request")])
def test_even_valid_register_transitions_are_not_promoted_by_this_exercise(state, kind):
    trace = example()
    doc = trace["document"]
    doc[state] = {"state": "observed" if state == "verification_state" else "requested", "evidence_ref": "ev-trace-2"}
    doc["evidence"].append({"evidence_id": "ev-trace-2", "kind": kind,
                            "recorded_by": "researcher", "recorded_at": "2026-01-02T00:00:00+00:00"})
    if state == "verification_state":
        trace["chunk"]["source_verification"] = "observed"
        trace["chunk"]["register_binding"]["verification_evidence_ref"] = "ev-trace-2"
    with pytest.raises(ValueError, match="pending source verification"):
        check_trace(trace)


@pytest.mark.parametrize("change,reason", [
    ("case_invalid", "invalid case"), ("case_scope", "null source applicability"),
    ("case_outcome", "route/outcome"), ("content_check_extra", "content_check keys"),
    ("content_check_private", "another namespace"), ("rule_scope", "no applicability scope"),
    ("rule_empty", "one rule"),
])
def test_guards_are_exercised_after_repinning_unrelated_bindings(change, reason):
    trace = example()
    if change == "case_invalid":
        trace["case"]["query"] = ""
    elif change == "case_scope":
        trace["case"]["scope"] = {"institution": "fictional", "edition": "v1", "version_id": None}
        trace["case"]["scope_null_reason"] = None
    elif change == "case_outcome":
        trace["case"]["expected_outcome"] = "unsupported"
    elif change == "content_check_extra":
        trace["content_check"]["extra"] = True
    elif change == "content_check_private":
        trace["content_check"]["evidence_ref"] = "sess-synth-0001"
    elif change == "rule_scope":
        trace["rule_draft"]["scope"] = {"knowledge_release_id": "release-synth-1",
                                         "edition_ids": [trace["document"]["edition_id"]], "scope_ids": []}
    elif change == "rule_empty":
        trace["rule_draft"]["rule_ids"] = []
        trace["rule_draft"]["rule_bundle_version"] = None
    trace["binding"]["case_digest"] = case_digest(trace["case"])
    with pytest.raises(ValueError, match=reason):
        check_trace(trace)
