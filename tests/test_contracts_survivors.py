"""Phase 1 Task 3, fix pass 2: tests for the mutants that survived the first mutation run, and vocabulary pins.

The closed lists live in knowledge/manifests/governance-vocabulary.json and the models derive from it.
These pins make a silent edit of the file fail a test instead of quietly changing what the package accepts.
"""

from __future__ import annotations

import copy

import pytest
from pydantic import ValidationError

from backend.bintanong_contracts import base, governance as gov, runtime, source
import test_contracts_governance as g
import test_contracts_source as s1

VOC = base.VOCAB


# ---------------------------------------------------------------- vocabulary pins (kill vocabulary-file drift)
def test_namespace_prefixes_are_pinned():
    assert VOC["namespaces"] == {
        "institutional": {"id_prefixes": ["doc-", "ver-", "edition-", "conflict-"], "lifecycles": ["register"]},
        "private_session": {"id_prefixes": ["sess-", "fact-"], "lifecycles": ["session_only"]}}


def test_scope_fields_origins_and_runtime_lists_are_pinned():
    assert VOC["scope_fields"] == ["issuer", "campus", "college", "program", "cohort", "printed_revision",
                                   "effective_from", "effective_to"]
    assert VOC["session_origins"] == ["user_statement", "private_upload"]
    assert VOC["runtime"]["routes"] == ["RAG", "Hybrid", "Symbolic"]
    assert VOC["runtime"]["controls"] == ["clarify", "greeting", "unsupported_scope", "evidence_unavailable"]
    assert VOC["supersession_relations"] == ["none", "supersedes", "superseded_by"]
    assert VOC["document_categories"] == ["source_document", "curriculum_proposal_candidate"]
    assert VOC["proposal_categories"] == ["curriculum_proposal_candidate"]
    assert VOC["field_bases"]["allowed"] == ["printed_text", "issuing_office_statement", "reviewer_reading"]
    assert VOC["conflict_resolution_bases"] == ["supersession_evidenced", "scope_distinction_evidenced", "source_owner_ruling"]


def test_the_id_patterns_are_derived_from_the_vocabulary_prefixes():
    assert gov.ID_DOC == base.id_pattern("doc-") and gov.ID_CONFLICT == base.id_pattern("conflict-")
    assert gov.ID_FACT == base.id_pattern("fact-") and gov.ID_SESSION == base.id_pattern("sess-")
    with pytest.raises(KeyError, match="chunk\\-' is not an id prefix in the governance vocabulary"):
        base.id_pattern("chunk-")


def test_every_scope_field_of_the_vocabulary_is_a_field_of_the_register_model():
    assert set(VOC["scope_fields"]) <= set(gov.SourceDocumentVersion.model_fields)
    dims = set(gov.AffectedScope.model_fields) - {"capability"}
    assert dims <= set(VOC["scope_fields"])


def test_the_session_origins_of_the_vocabulary_are_exactly_what_a_session_fact_accepts():
    f = g.load("synthetic-session-fact.json")
    for origin in VOC["session_origins"]:
        gov.SessionFact.parse({**f, "origin": origin})
    for origin in ("staff_entry", "official_record", ""):
        with pytest.raises(ValidationError, match="String should match pattern '\\^\\(user_statement\\|private_upload"):
            gov.SessionFact.parse({**f, "origin": origin})


def test_routes_and_controls_of_the_vocabulary_are_exactly_what_a_routing_decision_accepts():
    def decision(**over):
        return {"schema_version": "bintanong-routing-decision-v1", "route": None, "control": None, "confidence": None,
                "predicate_request": None, "required_facts": [], "missing_facts": [], "reason": "r", **over}
    pred = {"predicate": "can_enroll_fictional", "inputs": []}
    for route in VOC["runtime"]["routes"]:
        runtime.RoutingDecision.parse(decision(route=route, predicate_request=None if route == "RAG" else pred))
    for control in VOC["runtime"]["controls"]:
        runtime.RoutingDecision.parse(decision(control=control))
    for bad in ("Direct", "rag", "", "chat"):
        with pytest.raises(ValidationError, match='is not a route in the governance vocabulary'):
            runtime.RoutingDecision.parse(decision(route=bad))
        with pytest.raises(ValidationError, match='is not a control outcome in the governance vocabulary'):
            runtime.RoutingDecision.parse(decision(control=bad))
    assert not hasattr(runtime, "ROUTES") and not hasattr(runtime, "CONTROLS")


# ---------------------------------------------------------------- survivors of the first mutation run
def test_a_referred_conflict_still_blocks_its_capability():
    c = g.load("synthetic-conflict.json")
    referred = g.mut(c, lambda r: (r["evidence"].append(g.ev("ev-ref", "conflict_referral", "researcher")),
                                   r.update(resolution_state="referred_to_source_owner", resolution_evidence_ref="ev-ref")))
    parsed = gov.SourceConflict.parse(referred)
    assert parsed.resolution_state == "referred_to_source_owner"
    assert gov.blocked_capabilities([parsed]) == {"enrollment_procedure_answers"}
    assert gov.blocked_capabilities([gov.SourceConflict.parse(c)]) == {"enrollment_procedure_answers"}


def pending_acquisition(r):
    r["acquisition_state"] = {"state": "pending", "evidence_ref": None}


def test_verification_against_pending_or_mismatched_bytes_is_rejected():
    for fn in (pending_acquisition, lambda r: r["acquisition_state"].update(state="mismatch")):
        with pytest.raises(ValidationError, match="not acquired and matching"):
            gov.SourceDocumentVersion.parse(g.mut(g.register()[1], fn))
    gov.SourceDocumentVersion.parse(g.register()[1])


def test_a_dangling_evidence_reference_is_named():
    for state_field, state in (("verification_state", "verified"), ("acquisition_state", "verified"), ("approval_state", "approved")):
        with pytest.raises(ValidationError, match="not in the record"):
            gov.SourceDocumentVersion.parse(g.mut(g.register()[1], lambda r, f=state_field, s=state: r[f].update(
                state=s, evidence_ref="ev-nope")))
    with pytest.raises(ValidationError, match="not in the record"):
        gov.SourceConflict.parse(g.mut(g.load("synthetic-conflict.json"), lambda r: r.update(
            resolution_state="resolved", resolution_evidence_ref="ev-nope", resolution_basis="source_owner_ruling")))


def test_a_bounding_box_without_its_origin_is_rejected_at_the_model_level():
    # [1, 40, 30, 2] would be a valid BOTTOMLEFT box, so only the missing origin can reject it
    with pytest.raises(ValidationError, match="origin"):
        source.SourceSpan.parse(s1.span_dict(bbox=[1, 40, 30, 2], bbox_origin=None, page_size=[612, 792]))
    source.SourceSpan.parse(s1.span_dict(bbox=[1, 40, 30, 2], bbox_origin="BOTTOMLEFT", page_size=[612, 792]))


@pytest.mark.parametrize("missing", ["page_size", "page", "byte_sha256"])
def test_a_bounding_box_needs_each_of_its_companions(missing):
    over = dict(bbox=[1, 2, 30, 40], bbox_origin="TOPLEFT", page_size=[612, 792])
    over[missing] = None
    with pytest.raises(ValidationError, match="needs its origin"):
        source.SourceSpan.parse(s1.span_dict(**over))


def test_a_pinned_revision_is_a_full_commit_or_digest_whatever_the_old_denylist_said():
    assert base.is_pinned_revision("a" * 40) and base.is_pinned_revision("a" * 64)
    for text in ("master", "main", "a" * 39, "a" * 41, "a" * 63, "A" * 40, "g" * 40, " " + "a" * 40, "a" * 40 + "\n"):
        assert not base.is_pinned_revision(text), text
