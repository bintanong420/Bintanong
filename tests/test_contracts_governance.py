"""Phase 1 Task 3, group 2a: SourceDocumentVersion, SourceConflict, SessionFact against the real package.

All records are synthetic with fictional locators. Nothing here approves a source.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from backend.bintanong_contracts import base, governance as gov

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "knowledge" / "manifests" / "examples"


def load(name):
    return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))


def register():
    return load("synthetic-register.json")


def ev(eid, kind, by, **extra):
    return {"evidence_id": eid, "kind": kind, "recorded_by": by, "recorded_at": "2026-01-01T00:00:00+00:00", **extra}


def mut(rec, fn):
    c = copy.deepcopy(rec)
    fn(c)
    return c


def approved_record():
    r = copy.deepcopy(register()[1])
    r["evidence"] += [
        ev("ev-b4", "issuing_office_confirmation", "issuing_office"),
        ev("ev-b5", "approval_request", "researcher"),
        ev("ev-b6", "issuing_office_authorization", "issuing_office", authorization_ref="auth-synth-0001"),
        ev("ev-b7", "reviewer_absence_check", "reviewer"),
    ]
    for f in ("issuer", "printed_revision"):
        r[f].update(state="verified", evidence_ref="ev-b4", basis="issuing_office_statement")
    for f in ("campus", "college", "program", "cohort", "effective_from", "effective_to"):
        r[f].update(state="not_stated", evidence_ref="ev-b7")
    r["verification_state"] = {"state": "verified", "evidence_ref": "ev-b4"}
    r["approval_state"] = {"state": "approved", "evidence_ref": "ev-b6"}
    r["approval_id"] = "auth-synth-0001"
    return r


def bad(rec):
    with pytest.raises((ValidationError, base.ContractError)):
        gov.SourceDocumentVersion.parse(rec)


# ---------------------------------------------------------------- examples validate with the package
@pytest.mark.parametrize("index", [0, 1, 2])
def test_register_examples_validate_and_roundtrip(index):
    rec = gov.SourceDocumentVersion.parse(register()[index])
    assert rec.approval_id is None and rec.approval_state.state == "not_requested"
    text = base.canonical_json(rec)
    assert gov.SourceDocumentVersion.parse(text) == rec
    assert base.canonical_json(gov.SourceDocumentVersion.parse(text)) == text


def test_register_example_set_is_consistent():
    gov.check_register([gov.SourceDocumentVersion.parse(r) for r in register()])


def test_conflict_and_session_fact_examples_validate_and_roundtrip():
    c = gov.SourceConflict.parse(load("synthetic-conflict.json"))
    f = gov.SessionFact.parse(load("synthetic-session-fact.json"))
    for m in (c, f):
        assert type(m).parse(base.canonical_json(m)) == m
    assert gov.blocked_capabilities([c]) == {"enrollment_procedure_answers"}


def test_fully_evidenced_synthetic_record_passes_the_guards():
    assert gov.SourceDocumentVersion.parse(approved_record()).approval_state.state == "approved"


# ---------------------------------------------------------------- malformed input
@pytest.mark.parametrize("fn", [
    lambda r: r.pop("byte_sha256"),
    lambda r: r.update(byte_sha256="XYZ"),
    lambda r: r.update(byte_sha256="A" * 64),
    lambda r: r.update(unknown="x"),
    lambda r: r.update(schema_version="bintanong-source-register-v2"),
    lambda r: r.update(namespace="private_session"),
    lambda r: r.update(document_id="ver-x"),
    lambda r: r.update(version_id="doc-x"),
    lambda r: r.update(edition_id="edition-UPPER"),
    lambda r: r.update(filename=""),
    lambda r: r.update(acquisition_locators=[]),
    lambda r: r.update(document_category="approved_source"),
    lambda r: r.update(synthetic="yes"),
    lambda r: r.update(approved=True),
    lambda r: r.update(promotion_status="VERIFIED"),
    lambda r: r["acquisition_state"].update(state="approved"),
    lambda r: r["evidence"][0].update(recorded_at="yesterday"),
])
def test_malformed_register_input_is_rejected(fn):
    bad(mut(register()[1], fn))


# ---------------------------------------------------------------- forbidden status promotion
def test_approval_id_without_authorized_evidence_is_rejected():
    bad(mut(register()[0], lambda r: r.update(approval_id="auth-1")))


def test_approved_state_without_authorization_ref_is_rejected():
    bad(mut(approved_record(), lambda r: r["evidence"][-2].pop("authorization_ref")))


def test_approved_by_wrong_role_is_rejected():
    bad(mut(approved_record(), lambda r: r["evidence"][-2].update(recorded_by="researcher")))


def test_approval_id_must_equal_the_authorization_ref():
    bad(mut(approved_record(), lambda r: r.update(approval_id="auth-other")))


@pytest.mark.parametrize("kind", ["extraction_audit", "extractor_status_label", "filename_observation",
                                  "local_possession_note"])
def test_non_authorizing_evidence_cannot_move_any_state(kind):
    # fabricated verification: cite a non-authorizing record for verified acquisition
    def promote(r):
        r["evidence"].append(ev("ev-x", kind, "system"))
        r["acquisition_state"] = {"state": "verified", "evidence_ref": "ev-x"}
    bad(mut(register()[0], promote))


def test_verified_with_no_evidence_reference_is_rejected():
    bad(mut(register()[1], lambda r: r["verification_state"].update(state="verified", evidence_ref=None)))


def test_initial_state_must_not_cite_evidence():
    bad(mut(register()[0], lambda r: r["verification_state"].update(evidence_ref="ev-a1")))


def test_pending_to_verified_skips_a_step():
    # issuing-office confirmation is the only way into verified verification and needs observed first
    def skip(r):
        r["evidence"].append(ev("ev-y", "byte_hash_check", "reviewer"))
        r["verification_state"] = {"state": "verified", "evidence_ref": "ev-y"}
    bad(mut(register()[1], skip))


def test_verification_without_matching_acquired_bytes_is_rejected():
    def f(r):
        r["acquisition_state"] = {"state": "mismatch", "evidence_ref": "ev-b2"}
    bad(mut(register()[1], f))


def test_content_review_never_substitutes_for_approval():
    def f(r):
        r["evidence"].append(ev("ev-cr", "content_review_record", "reviewer"))
        r["approval_state"] = {"state": "approved", "evidence_ref": "ev-cr"}
    bad(mut(approved_record(), f))


def test_approval_needs_every_guard():
    for fn in (
        lambda r: r["acquisition_state"].update(state="observed", evidence_ref="ev-b1"),
        lambda r: r["issuer"].update(state="observed", evidence_ref="ev-b3", basis="printed_text"),
        lambda r: r["campus"].update(state="pending", evidence_ref=None),
        lambda r: r.update(document_category="curriculum_proposal_candidate"),
    ):
        bad(mut(approved_record(), fn))


def test_proposal_candidate_can_never_be_approved():
    bad(mut(approved_record(), lambda r: r.update(document_category="curriculum_proposal_candidate")))


def test_scope_cannot_be_inferred_from_filename_or_possession():
    for basis in ("filename_date", "college_vs_university_wording", "local_possession"):
        bad(mut(register()[1], lambda r: r["campus"].update(
            value="Main", state="observed", evidence_ref="ev-b3", basis=basis)))


def test_pending_scope_field_carries_no_value():
    bad(mut(register()[0], lambda r: r["campus"].update(value="Main")))
    bad(mut(register()[0], lambda r: r["campus"].update(basis="printed_text")))


def test_observed_scope_field_needs_value_and_basis():
    bad(mut(register()[1], lambda r: r["issuer"].update(basis=None)))
    bad(mut(register()[1], lambda r: r["issuer"].update(value=None)))


# ---------------------------------------------------------------- supersession
def test_supersession_rules():
    def sup(**kw):
        def f(r):
            r["evidence"].append(ev("ev-s", "printed_text_span", "reviewer"))
            r["supersession"].update(kw)
        return f
    ok = mut(register()[1], sup(relation="supersedes", target_version_id="ver-synth-handbook-1",
                                state="observed", evidence_ref="ev-s", basis="printed_text"))
    gov.SourceDocumentVersion.parse(ok)
    for kw in (dict(relation="supersedes", target_version_id=None, state="observed", evidence_ref="ev-s", basis="printed_text"),
               dict(relation="supersedes", target_version_id="ver-synth-handbook-2", state="observed", evidence_ref="ev-s", basis="printed_text"),
               dict(relation="supersedes", target_version_id="ver-synth-handbook-1", state="pending"),
               dict(relation="none", target_version_id="ver-synth-handbook-1"),
               dict(relation="replaces")):
        bad(mut(register()[1], sup(**kw)))


# ---------------------------------------------------------------- namespaces and local paths
def test_private_ids_are_rejected_inside_an_institutional_record():
    bad(mut(register()[1], lambda r: r["acquisition_locators"].append("fact-synth-0001")))
    bad(mut(register()[1], lambda r: r["evidence"][0].update(evidence_id="sess-1")))


@pytest.mark.parametrize("locator", ["C:\\Users\\x\\a.pdf", "c:/users/x/a.pdf", "/home/u/a.pdf", "\\\\srv\\share\\a.pdf"])
def test_local_paths_are_not_acquisition_locators(locator):
    bad(mut(register()[1], lambda r: r["acquisition_locators"].append(locator)))
    bad(mut(register()[1], lambda r: r.update(filename=locator)))


def test_duplicate_evidence_ids_are_rejected():
    bad(mut(register()[1], lambda r: r["evidence"].append(copy.deepcopy(r["evidence"][0]))))


def test_duplicate_locators_are_rejected():
    bad(mut(register()[1], lambda r: r["acquisition_locators"].append(r["acquisition_locators"][0])))


# ---------------------------------------------------------------- register set
def parsed(*recs):
    return [gov.SourceDocumentVersion.parse(r) for r in recs]


def test_same_bytes_as_two_versions_is_rejected():
    a, b = register()[0], register()[1]
    b = mut(b, lambda r: r.update(byte_sha256=a["byte_sha256"]))
    with pytest.raises(base.ContractError, match="same bytes"):
        gov.check_register(parsed(a, b))


def test_same_filename_different_bytes_cannot_share_an_edition():
    a, b = register()[0], register()[1]
    b = mut(b, lambda r: r.update(edition_id=a["edition_id"]))
    assert a["filename"] == b["filename"] and a["byte_sha256"] != b["byte_sha256"]
    with pytest.raises(base.ContractError, match="edition"):
        gov.check_register(parsed(a, b))


def test_duplicate_version_ids_and_dangling_supersession_target_are_rejected():
    a, b = register()[0], register()[1]
    with pytest.raises(base.ContractError, match="duplicate version_id"):
        gov.check_register(parsed(a, mut(b, lambda r: r.update(version_id=a["version_id"]))))

    def dangling(r):
        r["evidence"].append(ev("ev-s", "printed_text_span", "reviewer"))
        r["supersession"].update(relation="supersedes", target_version_id="ver-missing", state="observed",
                                 evidence_ref="ev-s", basis="printed_text")
    with pytest.raises(base.ContractError, match="not in the register"):
        gov.check_register(parsed(mut(b, dangling)))


# ---------------------------------------------------------------- conflict
def cbad(rec, versions=None):
    with pytest.raises((ValidationError, base.ContractError)):
        c = gov.SourceConflict.parse(rec)
        if versions is not None:
            gov.check_conflict_versions(c, versions)


def test_conflict_needs_two_distinct_claims():
    c = load("synthetic-conflict.json")
    cbad(mut(c, lambda r: r["claims"].__setitem__(1, copy.deepcopy(r["claims"][0]))))
    cbad(mut(c, lambda r: r["claims"].pop()))


def test_resolved_needs_issuing_office_evidence_and_a_basis():
    c = load("synthetic-conflict.json")

    def resolve(basis="source_owner_ruling", by="issuing_office", kind="issuing_office_resolution"):
        def f(r):
            r["evidence"].append(ev("ev-r", kind, by))
            r.update(resolution_state="resolved", resolution_evidence_ref="ev-r", resolution_basis=basis)
        return f
    gov.SourceConflict.parse(mut(c, resolve()))
    cbad(mut(c, resolve(basis=None)))
    cbad(mut(c, resolve(basis="newest_filename")))
    cbad(mut(c, resolve(by="reviewer")))
    cbad(mut(c, resolve(kind="extraction_audit")))
    cbad(mut(c, lambda r: r.update(resolution_basis="source_owner_ruling")))  # basis without resolution


def test_conflict_cites_only_registered_versions():
    c = load("synthetic-conflict.json")
    cbad(c, versions={"ver-synth-handbook-1"})


def test_resolving_one_conflict_unblocks_only_its_capability():
    c1 = gov.SourceConflict.parse(load("synthetic-conflict.json"))
    other = load("synthetic-conflict.json")
    other.update(conflict_id="conflict-synth-0002")
    other["affected_scope"]["capability"] = "grade_computation"
    c2 = gov.SourceConflict.parse(other)
    assert gov.blocked_capabilities([c1, c2]) == {"enrollment_procedure_answers", "grade_computation"}
    resolved = mut(load("synthetic-conflict.json"), lambda r: (
        r["evidence"].append(ev("ev-r", "issuing_office_resolution", "issuing_office")),
        r.update(resolution_state="resolved", resolution_evidence_ref="ev-r", resolution_basis="source_owner_ruling")))
    assert gov.blocked_capabilities([gov.SourceConflict.parse(resolved), c2]) == {"grade_computation"}


def test_conflict_rejects_private_ids():
    c = load("synthetic-conflict.json")
    cbad(mut(c, lambda r: r["claims"][0].update(span_ref="fact-synth-0001")))


# ---------------------------------------------------------------- session fact
def fbad(rec):
    with pytest.raises((ValidationError, base.ContractError)):
        gov.SessionFact.parse(rec)


def test_session_fact_confirmation_only_by_the_user_with_evidence():
    f = load("synthetic-session-fact.json")

    def confirm(by="user", kind="user_confirmation", state="user_confirmed"):
        def g(r):
            r["evidence"].append(ev("ev-u", kind, by))
            r.update(confirmation_state=state, confirmation_evidence_ref="ev-u")
        return g
    gov.SessionFact.parse(mut(f, confirm()))
    fbad(mut(f, confirm(by="issuing_office")))
    fbad(mut(f, confirm(by="reviewer")))
    fbad(mut(f, confirm(kind="issuing_office_confirmation")))
    fbad(mut(f, lambda r: r.update(confirmation_state="user_confirmed")))  # no evidence


@pytest.mark.parametrize("field", ["approval_id", "verified", "ledger_entry", "source_id", "version_id", "promoted"])
def test_session_fact_cannot_carry_institutional_or_ledger_fields(field):
    fbad(mut(load("synthetic-session-fact.json"), lambda r: r.update({field: "x"})))


def test_session_fact_is_session_only_and_in_the_private_namespace():
    f = load("synthetic-session-fact.json")
    fbad(mut(f, lambda r: r.update(lifecycle="register")))
    fbad(mut(f, lambda r: r.update(namespace="institutional")))
    fbad(mut(f, lambda r: r.update(fact_id="ver-synth-1")))
    fbad(mut(f, lambda r: r.update(session_id="doc-synth")))
    fbad(mut(f, lambda r: r.update(origin="staff_ledger")))
    fbad(mut(f, lambda r: r["fact"].update(value="edition-synth-1")))  # an institutional id inside a private fact


# ---------------------------------------------------------------- mutation-driven additions
def test_authorization_ref_must_match_the_evidence_kind_even_when_uncited():
    bad(mut(register()[1], lambda r: r["evidence"][0].update(authorization_ref="auth-x")))
    bad(mut(register()[1], lambda r: r["evidence"].append(ev("ev-q", "issuing_office_authorization", "issuing_office"))))
    bad(mut(register()[1], lambda r: r["evidence"].append(
        ev("ev-q", "issuing_office_confirmation", "issuing_office", authorization_ref="auth-x"))))


def test_transition_rows_demand_the_authorization_ref_exactly_where_the_table_says():
    def e(kind, by, **kw):
        return gov.Evidence.model_validate(ev("ev-t", kind, by, **kw))
    assert gov.evidence_authorizes("approval_state", "approved", e("issuing_office_authorization", "issuing_office", authorization_ref="a"))
    assert not gov.evidence_authorizes("approval_state", "approved", e("issuing_office_authorization", "issuing_office"))
    assert not gov.evidence_authorizes("approval_state", "approved", e("issuing_office_authorization", "researcher", authorization_ref="a"))
    assert gov.evidence_authorizes("verification_state", "verified", e("issuing_office_confirmation", "issuing_office"))
    assert not gov.evidence_authorizes("verification_state", "verified",
                                       e("issuing_office_confirmation", "issuing_office", authorization_ref="a"))
    assert not gov.evidence_authorizes("verification_state", "verified", e("extraction_audit", "issuing_office"))


def test_a_state_without_an_evidence_reference_says_so():
    with pytest.raises(ValidationError, match="without an evidence reference"):
        gov.SourceDocumentVersion.parse(mut(
            register()[1], lambda r: r["verification_state"].update(state="verified", evidence_ref=None)))


def test_approval_needs_the_issuer_verified_not_merely_not_stated():
    def f(r):
        r["issuer"].update(value=None, state="not_stated", evidence_ref="ev-b7", basis=None)
    bad(mut(approved_record(), f))
