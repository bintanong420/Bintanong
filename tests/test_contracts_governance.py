"""Source governance: evidence, authorization, chronology and supersession contracts.

All records are synthetic with fictional locators. Nothing here approves a source."""

from __future__ import annotations

import calendar
import copy
import json
from datetime import date
from pathlib import Path

import pytest
from pydantic import ValidationError

from backend.bintanong_contracts import base
from backend.bintanong_contracts import governance as gov

import contracts_fixtures as fx
import test_source_governance_manifests as tl


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


def bad(rec, match):
    """The record must be rejected, and for the stated reason."""
    with pytest.raises((ValidationError, base.ContractError), match=match):
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
@pytest.mark.parametrize("fn,match", [
    (lambda r: r.pop("byte_sha256"), "byte_sha256"),
    (lambda r: r.update(byte_sha256="XYZ"), "byte_sha256"),
    (lambda r: r.update(byte_sha256="A" * 64), "byte_sha256"),
    (lambda r: r.update(unknown="x"), "unknown"),
    (lambda r: r.update(schema_version="bintanong-source-register-v2"), "unknown schema_version"),
    (lambda r: r.update(namespace="private_session"), "namespace"),
    (lambda r: r.update(document_id="ver-x"), "document_id"),
    (lambda r: r.update(version_id="doc-x"), "version_id"),
    (lambda r: r.update(edition_id="edition-UPPER"), "edition_id"),
    (lambda r: r.update(filename=""), "filename"),
    (lambda r: r.update(acquisition_locators=[]), "acquisition_locators"),
    (lambda r: r.update(document_category="approved_source"), "document_category"),
    (lambda r: r.update(synthetic="yes"), "synthetic"),
    (lambda r: r.update(approved=True), "approved"),
    (lambda r: r.update(promotion_status="VERIFIED"), "promotion_status"),
    (lambda r: r["acquisition_state"].update(state="approved"), "not a acquisition_state"),
    (lambda r: r["evidence"][0].update(recorded_at="yesterday"), "recorded_at"),
])
def test_malformed_register_input_is_rejected(fn, match):
    bad(mut(register()[1], fn), match)


# ---------------------------------------------------------------- forbidden status promotion
def test_approval_id_without_authorized_evidence_is_rejected():
    bad(mut(register()[0], lambda r: r.update(approval_id="auth-1")), "approval_id supplied without authorized approval evidence")


def test_approved_state_without_authorization_ref_is_rejected():
    bad(mut(approved_record(), lambda r: r["evidence"][-2].pop("authorization_ref")), "cannot authorize approved|authorization_ref required")


def test_approved_by_wrong_role_is_rejected():
    bad(mut(approved_record(), lambda r: r["evidence"][-2].update(recorded_by="researcher")), "cannot authorize approved")


def test_approval_id_must_equal_the_authorization_ref():
    bad(mut(approved_record(), lambda r: r.update(approval_id="auth-other")), "approval_id must equal")


@pytest.mark.parametrize("kind", ["extraction_audit", "extractor_status_label", "filename_observation",
                                  "local_possession_note"])
def test_non_authorizing_evidence_cannot_move_any_state(kind):
    # fabricated verification: cite a non-authorizing record for verified acquisition
    def promote(r):
        r["evidence"].append(ev("ev-x", kind, "system"))
        r["acquisition_state"] = {"state": "verified", "evidence_ref": "ev-x"}
    bad(mut(register()[0], promote), "cannot authorize verified")


def test_verified_with_no_evidence_reference_is_rejected():
    bad(mut(register()[1], lambda r: r["verification_state"].update(state="verified", evidence_ref=None)),
        "without an evidence reference")


def test_initial_state_must_not_cite_evidence():
    bad(mut(register()[0], lambda r: r["verification_state"].update(evidence_ref="ev-a1")), "initial state")


def test_pending_to_verified_skips_a_step():
    # issuing-office confirmation is the only way into verified verification and needs observed first
    def skip(r):
        r["evidence"].append(ev("ev-y", "byte_hash_check", "reviewer"))
        r["verification_state"] = {"state": "verified", "evidence_ref": "ev-y"}
    bad(mut(register()[1], skip), "cannot authorize verified")


def test_verification_without_matching_acquired_bytes_is_rejected():
    def f(r):
        r["acquisition_state"] = {"state": "mismatch", "evidence_ref": "ev-b2"}
    bad(mut(register()[1], f), "not acquired and matching")


def test_content_review_never_substitutes_for_approval():
    def f(r):
        r["evidence"].append(ev("ev-cr", "content_review_record", "reviewer"))
        r["approval_state"] = {"state": "approved", "evidence_ref": "ev-cr"}
    bad(mut(approved_record(), f), "cannot authorize approved")


def test_approval_needs_every_guard():
    for fn, match in (
        (lambda r: r["acquisition_state"].update(state="observed", evidence_ref="ev-b1"), "verified acquisition and verified scope"),
        (lambda r: r["issuer"].update(state="observed", evidence_ref="ev-b3", basis="printed_text"), "issuer and scope/effectivity"),
        (lambda r: r["campus"].update(state="pending", evidence_ref=None), "issuer and scope/effectivity"),
        (lambda r: r.update(document_category="curriculum_proposal_candidate"), "proposal candidate cannot be approved"),
    ):
        bad(mut(approved_record(), fn), match)


def test_proposal_candidate_can_never_be_approved():
    bad(mut(approved_record(), lambda r: r.update(document_category="curriculum_proposal_candidate")),
        "proposal candidate cannot be approved")


def test_scope_cannot_be_inferred_from_filename_or_possession():
    for basis in ("filename_date", "college_vs_university_wording", "local_possession"):
        bad(mut(register()[1], lambda r: r["campus"].update(
            value="Main", state="observed", evidence_ref="ev-b3", basis=basis)), "basis")


def test_pending_scope_field_carries_no_value():
    bad(mut(register()[0], lambda r: r["campus"].update(value="Main")), "campus: pending must carry no value")
    bad(mut(register()[0], lambda r: r["campus"].update(basis="printed_text")), "campus: pending must carry no basis")


def test_observed_scope_field_needs_value_and_basis():
    bad(mut(register()[1], lambda r: r["issuer"].update(basis=None)), "issuer: observed needs a value and an allowed basis")
    bad(mut(register()[1], lambda r: r["issuer"].update(value=None)), "issuer: observed needs a value and an allowed basis")


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
    for kw, match in (
            (dict(relation="supersedes", target_version_id=None, state="observed", evidence_ref="ev-s", basis="printed_text"),
             "needs a target"),
            (dict(relation="supersedes", target_version_id="ver-synth-handbook-2", state="observed", evidence_ref="ev-s",
                  basis="printed_text"), "cannot supersede itself"),
            (dict(relation="supersedes", target_version_id="ver-synth-handbook-1", state="pending"), "needs a target"),
            (dict(relation="none", target_version_id="ver-synth-handbook-1"), "must not name a target"),
            (dict(relation="replaces"), "relation")):
        bad(mut(register()[1], sup(**kw)), match)


# ---------------------------------------------------------------- namespaces and local paths
def test_private_ids_are_rejected_inside_an_institutional_record():
    bad(mut(register()[1], lambda r: r["acquisition_locators"].append("fact-synth-0001")), "another namespace")
    bad(mut(register()[1], lambda r: r["evidence"][0].update(evidence_id="sess-1")), "another namespace")


@pytest.mark.parametrize("locator", ["C:\\Users\\x\\a.pdf", "c:/users/x/a.pdf", "/home/u/a.pdf", "\\\\srv\\share\\a.pdf"])
def test_local_paths_are_not_acquisition_locators(locator):
    bad(mut(register()[1], lambda r: r["acquisition_locators"].append(locator)), "locator")
    bad(mut(register()[1], lambda r: r.update(filename=locator)), "plain file name")


def test_duplicate_evidence_ids_are_rejected():
    bad(mut(register()[1], lambda r: r["evidence"].append(copy.deepcopy(r["evidence"][0]))), "duplicate evidence id")


def test_duplicate_locators_are_rejected():
    bad(mut(register()[1], lambda r: r["acquisition_locators"].append(r["acquisition_locators"][0])), "duplicate acquisition locators")


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
def cbad(rec, match, versions=None):
    with pytest.raises((ValidationError, base.ContractError), match=match):
        c = gov.SourceConflict.parse(rec)
        if versions is not None:
            gov.check_conflict_versions(c, versions)


def test_conflict_needs_two_distinct_claims():
    c = load("synthetic-conflict.json")
    cbad(mut(c, lambda r: r["claims"].__setitem__(1, copy.deepcopy(r["claims"][0]))), "two distinct claims")
    cbad(mut(c, lambda r: r["claims"].pop()), "claims")


def test_resolved_needs_issuing_office_evidence_and_a_basis():
    c = load("synthetic-conflict.json")

    def resolve(basis="source_owner_ruling", by="issuing_office", kind="issuing_office_resolution"):
        def f(r):
            r["evidence"].append(ev("ev-r", kind, by))
            r.update(resolution_state="resolved", resolution_evidence_ref="ev-r", resolution_basis=basis)
        return f
    gov.SourceConflict.parse(mut(c, resolve()))
    cbad(mut(c, resolve(basis=None)), "resolution basis is required")
    cbad(mut(c, resolve(basis="newest_filename")), "resolution_basis")
    cbad(mut(c, resolve(by="reviewer")), "cannot authorize resolved")
    cbad(mut(c, resolve(kind="extraction_audit")), "cannot authorize resolved")
    cbad(mut(c, lambda r: r.update(resolution_basis="source_owner_ruling")), "resolution basis is required")  # basis without resolution


def test_conflict_cites_only_registered_versions():
    c = load("synthetic-conflict.json")
    cbad(c, "unknown version", versions={"ver-synth-handbook-1"})


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
    cbad(mut(c, lambda r: r["claims"][0].update(span_ref="fact-synth-0001")), "another namespace")


# ---------------------------------------------------------------- session fact
def fbad(rec, match):
    with pytest.raises((ValidationError, base.ContractError), match=match):
        gov.SessionFact.parse(rec)


def test_session_fact_confirmation_only_by_the_user_with_evidence():
    f = load("synthetic-session-fact.json")

    def confirm(by="user", kind="user_confirmation", state="user_confirmed"):
        def g(r):
            r["evidence"].append(ev("ev-u", kind, by))
            r.update(confirmation_state=state, confirmation_evidence_ref="ev-u")
        return g
    gov.SessionFact.parse(mut(f, confirm()))
    fbad(mut(f, confirm(by="issuing_office")), "cannot authorize user_confirmed")
    fbad(mut(f, confirm(by="reviewer")), "cannot authorize user_confirmed")
    fbad(mut(f, confirm(kind="issuing_office_confirmation")), "cannot authorize user_confirmed")
    fbad(mut(f, lambda r: r.update(confirmation_state="user_confirmed")), "without an evidence reference")  # no evidence


@pytest.mark.parametrize("field", ["approval_id", "verified", "ledger_entry", "source_id", "version_id", "promoted"])
def test_session_fact_cannot_carry_institutional_or_ledger_fields(field):
    fbad(mut(load("synthetic-session-fact.json"), lambda r: r.update({field: "x"})), field)


def test_session_fact_is_session_only_and_in_the_private_namespace():
    f = load("synthetic-session-fact.json")
    fbad(mut(f, lambda r: r.update(lifecycle="register")), "lifecycle")
    fbad(mut(f, lambda r: r.update(namespace="institutional")), "namespace")
    fbad(mut(f, lambda r: r.update(fact_id="ver-synth-1")), "fact_id")
    fbad(mut(f, lambda r: r.update(session_id="doc-synth")), "session_id")
    fbad(mut(f, lambda r: r.update(origin="staff_ledger")), "origin")
    fbad(mut(f, lambda r: r["fact"].update(value="edition-synth-1")), "another namespace")  # an institutional id inside a private fact


# ---------------------------------------------------------------- mutation-driven additions
def test_authorization_ref_must_match_the_evidence_kind_even_when_uncited():
    bad(mut(register()[1], lambda r: r["evidence"][0].update(authorization_ref="auth-x")), "authorization_ref not allowed")
    bad(mut(register()[1], lambda r: r["evidence"].append(ev("ev-q", "issuing_office_authorization", "issuing_office"))),
        "authorization_ref required")
    bad(mut(register()[1], lambda r: r["evidence"].append(
        ev("ev-q", "issuing_office_confirmation", "issuing_office", authorization_ref="auth-x"))), "authorization_ref not allowed")


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
    bad(mut(approved_record(), f), "issuer and scope/effectivity")


# Authorization, supersession and source paths





def _reject_governance_record(rec, match):
    with pytest.raises((ValidationError, base.ContractError), match=match):
        gov.SourceDocumentVersion.parse(rec)

def _parse_governance_record(rec):
    return gov.SourceDocumentVersion.parse(rec)

def by_id(rec, eid):
    return next(e for e in rec["evidence"] if e["evidence_id"] == eid)

CHAIN = "earlier evidence"

# ---------------------------------------------------------------- H1: the `from` column
def test_approved_without_an_approval_request_is_rejected():
    rec = mut(approved_record(), lambda r: r.__setitem__(
        "evidence", [e for e in r["evidence"] if e["evidence_id"] != "ev-b5"]))
    _reject_governance_record(rec, CHAIN)
    _parse_governance_record(approved_record())

def test_a_request_recorded_after_the_authorization_is_rejected():
    def reorder(r):
        evs = {e["evidence_id"]: e for e in r["evidence"]}
        r["evidence"] = [e for e in r["evidence"] if e["evidence_id"] not in ("ev-b5", "ev-b6")] + [evs["ev-b6"], evs["ev-b5"]]
    _reject_governance_record(mut(approved_record(), reorder), CHAIN)

def test_an_authorization_dated_before_its_request_is_rejected_and_later_is_fine():
    _reject_governance_record(mut(approved_record(), lambda r: by_id(r, "ev-b6").update(recorded_at="2025-12-31T23:59:59+00:00")), CHAIN)
    _parse_governance_record(mut(approved_record(), lambda r: by_id(r, "ev-b6").update(recorded_at="2026-01-02T00:00:00+00:00")))

def revoked(ref="auth-synth-0001"):
    def fn(r):
        r["evidence"].append(ev("ev-b8", "issuing_office_revocation", "issuing_office", authorization_ref=ref,
                                recorded_at="2026-01-03T00:00:00+00:00"))
        r["approval_state"] = {"state": "revoked", "evidence_ref": "ev-b8"}
        r["approval_id"] = ref
    return mut(approved_record(), fn)

def test_revoked_needs_the_approval_chain_even_on_an_all_pending_record():
    _parse_governance_record(revoked())
    no_approval = mut(revoked(), lambda r: r.__setitem__(
        "evidence", [e for e in r["evidence"] if e["kind"] != "issuing_office_authorization"]))
    _reject_governance_record(no_approval, CHAIN)

    def only_revocation(r):
        r["evidence"].append(ev("ev-x", "issuing_office_revocation", "issuing_office", authorization_ref="auth-synth-0001"))
        r["approval_state"] = {"state": "revoked", "evidence_ref": "ev-x"}
        r["approval_id"] = "auth-synth-0001"
    _reject_governance_record(mut(register()[0], only_revocation), CHAIN)   # nothing was ever approved
    _reject_governance_record(mut(register()[1], only_revocation), CHAIN)

def test_a_revocation_must_cite_the_approvals_authorization_ref():
    _reject_governance_record(revoked(ref="auth-synth-0099"), "revocation must cite")

def test_rejected_needs_an_earlier_request():
    without = mut(register()[1], lambda r: (
        r["evidence"].append(ev("ev-x", "issuing_office_rejection", "issuing_office")),
        r["approval_state"].update(state="rejected", evidence_ref="ev-x")))
    _reject_governance_record(without, CHAIN)
    _parse_governance_record(mut(register()[1], lambda r: (
        r["evidence"].extend([ev("ev-q", "approval_request", "researcher"), ev("ev-x", "issuing_office_rejection", "issuing_office")]),
        r["approval_state"].update(state="rejected", evidence_ref="ev-x"))))

def test_verified_states_need_the_earlier_observed_evidence():
    only_confirmation = mut(register()[0], lambda r: (
        r["evidence"].append(ev("ev-v", "issuing_office_confirmation", "issuing_office")),
        r["verification_state"].update(state="verified", evidence_ref="ev-v")))
    _reject_governance_record(only_confirmation, CHAIN)
    only_hash = mut(register()[0], lambda r: (
        r.__setitem__("evidence", [ev("ev-s", "byte_hash_check", "system")]),
        r["acquisition_state"].update(state="verified", evidence_ref="ev-s")))
    _reject_governance_record(only_hash, CHAIN)
    mismatch_from_nothing = mut(register()[0], lambda r: (
        r.__setitem__("evidence", [ev("ev-s", "byte_hash_check", "system")]),
        r["acquisition_state"].update(state="mismatch", evidence_ref="ev-s")))
    _reject_governance_record(mismatch_from_nothing, CHAIN)
    scope = mut(register()[0], lambda r: (
        r["evidence"].append(ev("ev-o", "issuing_office_confirmation", "issuing_office")),
        r["issuer"].update(value="X", state="verified", evidence_ref="ev-o", basis="issuing_office_statement")))
    _reject_governance_record(scope, CHAIN)

def test_the_chain_is_recursive():
    # A2 (observed -> verified) is satisfied by a second hash check only when an earlier one entered observed.
    two_hashes = mut(register()[0], lambda r: (
        r["evidence"].append(ev("ev-a2", "byte_hash_check", "system", recorded_at="2026-01-02T00:00:00+00:00")),
        r["acquisition_state"].update(state="verified", evidence_ref="ev-a2")))
    _parse_governance_record(two_hashes)
    # the earlier hash check is dated later than the verifying one: the order is wrong
    _reject_governance_record(mut(two_hashes, lambda r: by_id(r, "ev-a2").update(recorded_at="2025-01-01T00:00:00+00:00")), CHAIN)

def test_an_unparseable_or_impossible_timestamp_is_an_error_not_a_crash():
    for stamp in ("9999-99-99T99:99:99Z", "2026-13-45T25:61:61Z"):
        with pytest.raises(ValidationError, match="not a real timestamp"):
            _parse_governance_record(mut(approved_record(), lambda r, s=stamp: by_id(r, "ev-b5").update(recorded_at=s)))

@pytest.mark.parametrize("stamp", [
    "2026-13-45T25:61:61Z", "2026-02-30T00:00:00Z", "2026-13-01T00:00:00Z", "2026-01-01T24:00:00Z",
    "2026-01-01T00:60:00Z", "2026-01-01T00:00:61Z", "2026-01-01T00:00:00+99:99", "2026-01-01T00:00:00-24:00",
    "9999-12-31T23:59:59Z", "0001-01-01T00:00:00Z", "\uff12\uff10\uff12\uff16-01-01T00:00:00Z"])
def test_recorded_at_must_be_a_real_calendar_timestamp_in_every_record_type(stamp):
    with pytest.raises(ValidationError, match="timestamp|String should match"):
        _parse_governance_record(mut(register()[1], lambda r: r["evidence"][0].update(recorded_at=stamp)))
    c = load("synthetic-conflict.json")
    c["evidence"].append(ev("ev-c9", "conflict_referral", "researcher", recorded_at=stamp))
    with pytest.raises(ValidationError, match="timestamp|String should match"):
        gov.SourceConflict.parse(c)
    f = load("synthetic-session-fact.json")
    f["evidence"].append(ev("ev-s9", "user_confirmation", "user", recorded_at=stamp))
    with pytest.raises(ValidationError, match="timestamp|String should match"):
        gov.SessionFact.parse(f)

def test_a_valid_timestamp_with_an_offset_is_accepted():
    _parse_governance_record(mut(register()[1], lambda r: r["evidence"][0].update(recorded_at="2026-01-01T07:59:59.123+08:00")))

# ---------------------------------------------------------------- M-b: supersession
def pair(newer="supersedes"):
    regs = register()
    for r in regs[:2]:
        r["evidence"].append(ev("ev-sup", "printed_text_span", "researcher"))
    inverse = {"supersedes": "superseded_by", "superseded_by": "supersedes"}
    a, b = regs[1], regs[0]
    a["supersession"] = {"relation": newer, "target_version_id": b["version_id"], "state": "observed",
                         "evidence_ref": "ev-sup", "basis": "printed_text"}
    b["supersession"] = {"relation": inverse[newer], "target_version_id": a["version_id"], "state": "observed",
                         "evidence_ref": "ev-sup", "basis": "printed_text"}
    return regs

def sup(rec, relation, target, state="observed", basis="printed_text"):
    rec["supersession"] = {"relation": relation, "target_version_id": target, "state": state,
                           "evidence_ref": "ev-sup", "basis": basis}

def check(regs):
    gov.check_register([_parse_governance_record(r) for r in regs])

def chain3():
    regs = register()
    for r in regs:
        r["evidence"].append(ev("ev-sup", "printed_text_span", "researcher"))
    return regs

def third_handbook(regs):
    twin = copy.deepcopy(regs[1])
    twin.update(version_id="ver-synth-handbook-3", edition_id="edition-synth-handbook-3", byte_sha256="b" * 64)
    twin["supersession"] = copy.deepcopy(register()[0]["supersession"])
    regs.append(twin)
    return twin

def test_reciprocal_pairs_are_accepted_in_both_directions():
    check(pair())
    check(pair("superseded_by"))

def test_a_one_sided_claim_is_rejected():
    regs = pair()
    regs[0]["supersession"] = copy.deepcopy(register()[0]["supersession"])
    with pytest.raises(base.ContractError, match="reciprocal"):
        check(regs)

def test_a_two_cycle_is_rejected():
    regs = pair()
    sup(regs[0], "supersedes", regs[1]["version_id"])
    with pytest.raises(base.ContractError, match="cycle"):
        check(regs)

def test_a_longer_cycle_is_rejected_and_a_chain_is_not():
    regs = chain3()
    third_handbook(regs)
    h1, h2, h3 = regs[0], regs[1], regs[3]
    sup(h3, "supersedes", h2["version_id"]); sup(h2, "supersedes", h1["version_id"])
    h1["supersession"] = copy.deepcopy(register()[0]["supersession"])
    regs[2]["supersession"] = copy.deepcopy(register()[2]["supersession"])
    try:
        check(regs)
    except base.ContractError as exc:
        assert "cycle" not in str(exc)
    sup(h1, "supersedes", h3["version_id"])
    with pytest.raises(base.ContractError, match="cycle"):
        check(regs)

def test_two_successors_of_one_version_are_rejected():
    regs = chain3()
    third_handbook(regs)
    sup(regs[1], "supersedes", regs[0]["version_id"]); sup(regs[3], "supersedes", regs[0]["version_id"])
    sup(regs[0], "superseded_by", regs[1]["version_id"])
    with pytest.raises(base.ContractError, match="successor"):
        check(regs)

def test_a_source_document_and_a_proposal_candidate_cannot_supersede_each_other():
    for newer, older in ((1, 2), (2, 1)):
        regs = chain3()
        sup(regs[newer], "supersedes", regs[older]["version_id"])
        sup(regs[older], "superseded_by", regs[newer]["version_id"])
        with pytest.raises(base.ContractError, match="category"):
            check(regs)

def test_supersession_across_different_documents_is_rejected():
    regs = pair()
    regs[1]["document_id"] = "doc-synth-other"
    with pytest.raises(base.ContractError, match="different document"):
        check(regs)

RECORD_BAD = {
    "supersedes_but_not_stated": (lambda r: r["supersession"].update(
        relation="supersedes", target_version_id="ver-synth-handbook-1", state="not_stated", evidence_ref="ev-b7", basis=None),
        "needs a target and an observed or verified state"),
    "supersedes_but_pending": (lambda r: r["supersession"].update(
        relation="supersedes", target_version_id="ver-synth-handbook-1"),
        "needs a target and an observed or verified state"),
    "none_but_observed": (lambda r: r["supersession"].update(
        relation="none", target_version_id=None, state="observed", evidence_ref="ev-b3", basis="printed_text"),
        "relation none cannot be observed or verified"),
    "none_but_verified": (lambda r: (r["evidence"].append(ev("ev-b8", "issuing_office_confirmation", "issuing_office")),
                                     r["supersession"].update(relation="none", target_version_id=None, state="verified",
                                                              evidence_ref="ev-b8", basis="issuing_office_statement")),
        "relation none cannot be observed or verified"),
    "observed_without_basis": (lambda r: r["supersession"].update(
        relation="supersedes", target_version_id="ver-synth-handbook-1", state="observed", evidence_ref="ev-b3", basis=None),
        "needs an allowed basis"),
    "pending_with_basis": (lambda r: r["supersession"].update(basis="printed_text"), "pending must carry no basis"),
    "none_with_target": (lambda r: r["supersession"].update(
        relation="none", target_version_id="ver-synth-handbook-1", state="not_stated", evidence_ref="ev-b7"),
        "relation none must not name a target"),
    "self": (lambda r: r["supersession"].update(
        relation="supersedes", target_version_id="ver-synth-handbook-2", state="observed", evidence_ref="ev-b3", basis="printed_text"),
        "cannot supersede itself"),
}

@pytest.mark.parametrize("name", RECORD_BAD)
def test_weak_supersession_records_are_rejected(name):
    fn, message = RECORD_BAD[name]

    def build(r):
        r["evidence"].append(ev("ev-b7", "reviewer_absence_check", "reviewer"))
        fn(r)
    _reject_governance_record(mut(register()[1], build), message)

def test_a_reviewed_absence_of_supersession_stays_accepted():
    _parse_governance_record(mut(register()[1], lambda r: (
        r["evidence"].append(ev("ev-b7", "reviewer_absence_check", "reviewer")),
        r["supersession"].update(state="not_stated", evidence_ref="ev-b7"))))

def test_effective_to_before_effective_from_is_rejected():
    def dates(frm, to):
        def fn(r):
            r["evidence"].append(ev("ev-d", "printed_text_span", "researcher"))
            r["effective_from"].update(value=frm, state="observed", evidence_ref="ev-d", basis="printed_text")
            r["effective_to"].update(value=to, state="observed", evidence_ref="ev-d", basis="printed_text")
        return mut(register()[1], fn)
    _parse_governance_record(dates("2023-08-01", "2024-05-31"))
    _parse_governance_record(dates("2023-08-01", "2023-08-01"))
    _parse_governance_record(dates("2023", "2023-12"))            # partial dates overlap: not provably reversed
    _parse_governance_record(dates("not a date", "also not"))     # a format the owner has not fixed is not compared
    _reject_governance_record(dates("2024-05-31", "2023-08-01"), "effective_to is before effective_from")
    _reject_governance_record(dates("2024", "2023-12"), "effective_to is before effective_from")

# ---------------------------------------------------------------- M-c: authorization
def twin_approved():
    a = approved_record()
    b = copy.deepcopy(a)
    b.update(version_id="ver-synth-handbook-3", edition_id="edition-synth-handbook-3", byte_sha256="c" * 64)
    return a, b

def test_the_same_authorization_ref_on_two_versions_is_rejected():
    a, b = twin_approved()
    with pytest.raises(base.ContractError, match="authorization ref"):
        check([a, b])
    other = mut(b, lambda r: (r.__setitem__("approval_id", "auth-synth-0002"),
                              next(e for e in r["evidence"] if e["kind"] == "issuing_office_authorization").update(
                                  authorization_ref="auth-synth-0002")))
    check([a, other])

@pytest.mark.parametrize("value", [" ", "", "auth x", " auth-synth-0001", "auth-synth-0001 ", "auth-synth-0001\n", "auth\tx"])
def test_blank_or_padded_approval_id_and_authorization_ref_are_rejected(value):
    rec = mut(approved_record(), lambda r: (r.__setitem__("approval_id", value), by_id(r, "ev-b6").update(authorization_ref=value)))
    with pytest.raises(ValidationError, match="String should match pattern"):
        _parse_governance_record(rec)
    with pytest.raises(ValidationError, match="String should match pattern"):
        _parse_governance_record(mut(approved_record(), lambda r: r.__setitem__("approval_id", value)))

def test_an_authorization_dated_before_the_acquisition_or_the_scope_verification_is_rejected():
    _reject_governance_record(mut(approved_record(), lambda r: by_id(r, "ev-b6").update(recorded_at="2025-06-01T00:00:00+00:00")), "dated before")
    # the authorization may not precede the evidence that verified acquisition or scope either
    late_scope = mut(approved_record(), lambda r: by_id(r, "ev-b4").update(recorded_at="2026-01-05T00:00:00+00:00"))
    _reject_governance_record(late_scope, "dated before|earlier evidence")

# ---------------------------------------------------------------- M-d: paths and URLs
@pytest.mark.parametrize("name", fx.MODEL_INVALID_SOURCE_FILENAMES)
def test_filename_must_be_a_plain_name_not_a_path_or_url(name):
    _reject_governance_record(mut(register()[1], lambda r: r.update(filename=name)), "plain file name")

@pytest.mark.parametrize("good", fx.PLAIN_SOURCE_FILENAMES)
def test_plain_filenames_are_accepted(good):
    _parse_governance_record(mut(register()[1], lambda r: r.update(filename=good)))

@pytest.mark.parametrize("loc", fx.MODEL_PRIVATE_SOURCE_LOCATORS)
def test_acquisition_locators_reject_local_paths(loc):
    _reject_governance_record(mut(register()[1], lambda r: r.update(acquisition_locators=["synthetic-locator-alpha/2", loc])), "locator")

@pytest.mark.parametrize("good", fx.PUBLIC_SOURCE_LOCATORS)
def test_logical_locators_and_https_urls_stay_accepted(good):
    _parse_governance_record(mut(register()[1], lambda r: r.update(acquisition_locators=[good])))

# ---------------------------------------------------------------- M-a: the namespace scan
PRIVATE_IN_INSTITUTIONAL = fx.MODEL_PRIVATE_ID_VARIANTS

INSTITUTIONAL_IN_SESSION = fx.MODEL_INSTITUTIONAL_ID_VARIANTS

PROSE = fx.LEGITIMATE_ID_PROSE

@pytest.mark.parametrize("value", PRIVATE_IN_INSTITUTIONAL)
def test_private_id_variants_are_found_in_every_institutional_string(value):
    with pytest.raises(ValidationError, match="another namespace"):
        _parse_governance_record(mut(register()[1], lambda r: r["issuer"].update(value=value)))
    with pytest.raises(ValidationError, match="another namespace"):
        _parse_governance_record(mut(register()[1], lambda r: r.update(acquisition_locators=["synthetic-locator-alpha/2", "x/" + value.strip() + "/y"])))
    with pytest.raises(ValidationError, match="another namespace"):
        gov.SourceConflict.parse(mut(load("synthetic-conflict.json"), lambda r: r["claims"][0].update(claim_text=value)))
    with pytest.raises(ValidationError, match="another namespace"):
        gov.SourceConflict.parse(mut(load("synthetic-conflict.json"), lambda r: r["claims"][0].update(span_ref=value)))

@pytest.mark.parametrize("value", INSTITUTIONAL_IN_SESSION)
def test_institutional_id_variants_are_found_in_a_session_fact(value):
    for field in ("value", "key"):
        with pytest.raises(ValidationError, match="another namespace"):
            gov.SessionFact.parse(mut(load("synthetic-session-fact.json"), lambda r, f=field: r["fact"].update({f: value})))

@pytest.mark.parametrize("value", PROSE)
def test_ordinary_prose_is_not_flagged(value):
    _parse_governance_record(mut(register()[1], lambda r: r["issuer"].update(value=value)))
    gov.SessionFact.parse(mut(load("synthetic-session-fact.json"), lambda r: r["fact"].update(value=value)))

def test_the_synthetic_examples_are_not_flagged():
    for rec in register():
        _parse_governance_record(rec)
    gov.SourceConflict.parse(load("synthetic-conflict.json"))
    gov.SessionFact.parse(load("synthetic-session-fact.json"))

def test_namespace_of_needs_more_than_a_bare_prefix_and_the_whole_id():
    for prefix in ("doc-", "ver-", "edition-", "conflict-", "sess-", "fact-"):
        assert base.namespace_of(prefix) is None, prefix
    assert base.namespace_of("doc-a") == "institutional" and base.namespace_of("fact-a") == "private_session"
    for padded in ("doc-a ", " doc-a", "doc-a\n", "DOC-a", "doc-a/b"):
        assert base.namespace_of(padded) is None, repr(padded)


# Chronology and package/schema parity





VOC = tl.vocabulary()

LATE = "2026-02-20T00:00:00+00:00"

def package_rejects(rec) -> bool:
    try:
        gov.SourceDocumentVersion.parse(rec)
    except (ValidationError, base.ContractError):
        return True
    return False

def package_message(rec) -> str:
    try:
        gov.SourceDocumentVersion.parse(rec)
    except (ValidationError, base.ContractError) as exc:
        return str(exc)
    return ""

def both_reject(rec, match):
    assert tl.register_errors(rec, VOC), "test-local checker accepted"
    assert package_rejects(rec), "package accepted"
    assert match in package_message(rec).lower(), package_message(rec)

def both_accept(rec):
    assert tl.register_errors(rec, VOC) == []
    assert not package_rejects(rec), package_message(rec)

def bare_revoked(category=None, ref="AUTH-1"):
    """The re-check's reproducer: request, authorization and revocation, and nothing else verified."""
    def fn(r):
        r["evidence"] = [tl.ev("q", "approval_request", "researcher"),
                         tl.ev("a", "issuing_office_authorization", "issuing_office", authorization_ref=ref),
                         tl.ev("v", "issuing_office_revocation", "issuing_office", authorization_ref=ref)]
        r["acquisition_state"] = {"state": "pending", "evidence_ref": None}
        r["approval_state"] = {"state": "revoked", "evidence_ref": "v"}
        r["approval_id"] = ref
        if category:
            r["document_category"] = category
    return tl.mutated(tl.register()[0], fn)

# ---------------------------------------------------------------- M2
def test_the_reproducer_is_rejected_by_both():
    both_reject(bare_revoked(), "revoked")
    both_reject(bare_revoked("curriculum_proposal_candidate"), "revoked")

def test_a_fully_evidenced_revocation_is_accepted_by_both():
    both_accept(tl._revoked())

REVOKED_GUARDS = {
    "acquisition_only_observed": lambda r: r["acquisition_state"].update(state="observed", evidence_ref="ev-b1"),
    "scope_only_observed": lambda r: r["verification_state"].update(state="observed", evidence_ref="ev-b3"),
    "issuer_not_verified": lambda r: r["issuer"].update(state="observed", evidence_ref="ev-b3", basis="printed_text"),
    "issuer_not_stated": lambda r: r["issuer"].update(value=None, state="not_stated", evidence_ref="ev-b7", basis=None),
    "effective_field_unresolved": lambda r: r["effective_from"].update(value=None, state="pending", evidence_ref=None, basis=None),
    "proposal_candidate": lambda r: r.__setitem__("document_category", "curriculum_proposal_candidate"),
    "acquisition_mismatch": lambda r: (r["evidence"].append(tl.ev("ev-mm", "byte_hash_check", "system")),
                                       r["acquisition_state"].update(state="mismatch", evidence_ref="ev-mm")),
}

@pytest.mark.parametrize("name", list(REVOKED_GUARDS))
def test_every_approval_guard_also_guards_a_revocation(name):
    rec = tl.mutated(tl._revoked(), REVOKED_GUARDS[name])
    assert tl.register_errors(rec, VOC), name
    assert package_rejects(rec), name

def test_a_revocation_must_name_the_authorization_it_revokes():
    both_reject(tl._revoked(ref="auth-synth-0099"), "revoke")
    other = tl.mutated(tl._revoked(), lambda r: r.__setitem__("approval_id", "auth-synth-0002"))
    assert tl.register_errors(other, VOC) and package_rejects(other)

# ---------------------------------------------------------------- L-c
def _late_issuer(r):
    r["evidence"].append(tl.ev("ev-late", "issuing_office_confirmation", "issuing_office", recorded_at=LATE))
    r["issuer"]["evidence_ref"] = "ev-late"

def _late_absence(r):
    r["evidence"].append(tl.ev("ev-late", "reviewer_absence_check", "reviewer", recorded_at=LATE))
    r["campus"]["evidence_ref"] = "ev-late"

def _late_verification(r):
    r["evidence"].append(tl.ev("ev-late", "issuing_office_confirmation", "issuing_office", recorded_at=LATE))
    r["verification_state"]["evidence_ref"] = "ev-late"

def _late_acquisition(r):
    r["evidence"].append(tl.ev("ev-late", "byte_hash_check", "system", recorded_at=LATE))
    r["acquisition_state"]["evidence_ref"] = "ev-late"

def _late_basis(r):
    r["evidence"].append(tl.ev("ev-late", "printed_text_span", "researcher", recorded_at=LATE))
    r["printed_revision"].update(state="observed", evidence_ref="ev-late", basis="printed_text")

@pytest.mark.parametrize("fn", [_late_issuer, _late_absence, _late_verification, _late_acquisition])
@pytest.mark.parametrize("builder", [tl.approved_record, tl._revoked])
def test_evidence_dated_after_the_authorization_is_rejected_for_every_relied_field(builder, fn):
    rec = tl.mutated(builder(), fn)
    both_reject(rec, "dated before")

def _reissued(r):
    # a second authorization with the same ref, dated after the evidence the scope rests on
    r["evidence"][next(i for i, e in enumerate(r["evidence"]) if e["evidence_id"] == "ev-b7")]["recorded_at"] = "2026-01-02T00:00:00+00:00"
    r["evidence"].append(tl.ev("ev-b9", "issuing_office_authorization", "issuing_office", recorded_at="2026-02-01T00:00:00+00:00",
                               authorization_ref="auth-synth-0001"))

def _other_authorization(r):
    r["evidence"].append(tl.ev("ev-b9", "issuing_office_authorization", "issuing_office", recorded_at="2025-12-01T00:00:00+00:00",
                               authorization_ref="auth-synth-0099"))

@pytest.mark.parametrize("builder", [tl.approved_record, tl._revoked])
def test_the_earliest_authorization_with_the_ref_is_the_one_that_counts(builder):
    both_reject(tl.mutated(builder(), _reissued), "dated before")

@pytest.mark.parametrize("builder", [tl.approved_record, tl._revoked])
def test_an_authorization_with_another_ref_is_not_the_grant(builder):
    both_accept(tl.mutated(builder(), _other_authorization))

def test_a_not_yet_verified_field_cannot_hide_behind_a_late_observation():
    # printed_revision observed (not verified) is not allowed by the approval guard either way
    rec = tl.mutated(tl.approved_record(), _late_basis)
    assert tl.register_errors(rec, VOC) and package_rejects(rec)

def test_the_authorization_date_guard_accepts_equal_times():
    both_accept(tl.approved_record())
    on_the_day = tl.mutated(tl.approved_record(), lambda r: (
        r["evidence"].append(tl.ev("ev-eq", "issuing_office_confirmation", "issuing_office")),
        r["issuer"].update(evidence_ref="ev-eq")))
    both_accept(on_the_day)

# ---------------------------------------------------------------- L-e: impossible dates
def _dates(a, b="__none__"):
    def fn(r):
        r["evidence"].append(tl.ev("ev-d", "printed_text_span", "researcher"))
        r["effective_from"].update(value=a, state="observed", evidence_ref="ev-d", basis="printed_text")
        if b != "__none__":
            r["effective_to"].update(value=b, state="observed", evidence_ref="ev-d", basis="printed_text")
    return tl.mutated(tl.register()[1], fn)

@pytest.mark.parametrize("a", ["2025-02-30", "2023-02-29", "2023-13", "2023-00", "2023-04-31", "2023-06-00", "0000-01-01"])
def test_an_impossible_iso_date_is_rejected_even_when_nothing_is_compared(a):
    both_reject(_dates(a), "calendar")

@pytest.mark.parametrize("a", ["2024-02-29", "2023-12", "2023", "2023-12-31", "soon", "August 2023", "2023-1-01", "1 Jan 2023"])
def test_possible_dates_and_unparsed_text_are_accepted(a):
    both_accept(_dates(a))

def test_an_impossible_end_date_is_rejected_too():
    both_reject(_dates("2023-01-01", "2023-02-30"), "calendar")

# ---------------------------------------------------------------- L-e: authorization refs
def _twin_with(ref_b):
    a, b = tl._twin_approved()
    b = tl.mutated(b, lambda r: (
        r.__setitem__("approval_id", ref_b),
        next(e for e in r["evidence"] if e["kind"] == "issuing_office_authorization").update(authorization_ref=ref_b)))
    return [a, b]

@pytest.mark.parametrize("ref_b", ["AUTH-SYNTH-0001", "Auth-Synth-0001", "auth-synth-0001\u200b", "auth-synth\u00ad-0001",
                                   "auth\u2011synth-0001", "\ufeffauth-synth-0001"])
def test_one_authorization_written_two_ways_is_still_one_authorization(ref_b):
    recs = _twin_with(ref_b)
    assert tl.register_set_errors(recs, VOC), ref_b
    with pytest.raises(base.ContractError, match="authorization ref"):
        gov.check_register([gov.SourceDocumentVersion.parse(r) for r in recs])

def test_two_different_authorizations_are_accepted():
    recs = _twin_with("auth-synth-0002")
    assert tl.register_set_errors(recs, VOC) == []
    gov.check_register([gov.SourceDocumentVersion.parse(r) for r in recs])

# ---------------------------------------------------------------- L-f: boundaries, written by hand
def _stamped(stamp):
    """An unreferenced extra piece of evidence carrying `stamp`: it only has to be a real, plausible time."""
    return tl.mutated(tl.register()[1], lambda r: r["evidence"].append(
        tl.ev("ev-z", "printed_text_span", "researcher", recorded_at=stamp)))

def _observed_before_confirmation(observed_at):
    """verified scope rests on an observation that must not be dated after the confirmation (2026-01-01 UTC)."""
    def fn(r):
        r["evidence"][2]["recorded_at"] = observed_at           # ev-b3, the printed-text observation
        r["evidence"].append(tl.ev("ev-b4", "issuing_office_confirmation", "issuing_office"))
        r["verification_state"].update(state="verified", evidence_ref="ev-b4")
    return tl.mutated(tl.register()[1], fn)

def _cross_pair(**second):
    regs = tl._pair()
    regs[0].update(second)
    return regs

# (label, record, rejected?) : every verdict is written here by hand, from the rule as the owner reads it.
HAND_VERDICTS = [
    ("effective 2023-06-15 .. 2023-06 (a later day in the same month is possible)", _dates("2023-06-15", "2023-06"), False),
    ("effective 2024-02-29 .. 2024-02 (leap February has 29 days)", _dates("2024-02-29", "2024-02"), False),
    ("effective 2023-06-30 .. 2023-06 (the month has 30 days)", _dates("2023-06-30", "2023-06"), False),
    ("effective 2023-06-15 .. 2023-06-15 (one day is allowed)", _dates("2023-06-15", "2023-06-15"), False),
    ("effective 2023-06-15 .. 2023-06-14 (ends before it starts)", _dates("2023-06-15", "2023-06-14"), True),
    ("effective 2023-07 .. 2023-06 (ends in an earlier month)", _dates("2023-07", "2023-06"), True),
    ("effective 2025-02-30 (not a day)", _dates("2025-02-30"), True),
    ("stamp 2000-01-01 (first accepted year)", _stamped("2000-01-01T00:00:00Z"), False),
    ("stamp 2051-06-01 (beyond a 2050 window)", _stamped("2051-06-01T00:00:00Z"), False),
    ("stamp 2100-12-31 (last accepted year)", _stamped("2100-12-31T23:59:59Z"), False),
    ("stamp 2101-01-01 (too far)", _stamped("2101-01-01T00:00:00Z"), True),
    ("stamp 1999-12-31 (too early)", _stamped("1999-12-31T23:59:59Z"), True),
    ("verified scope: observation earlier than confirmation", _observed_before_confirmation("2025-12-31T23:59:59+00:00"), False),
    ("verified scope: observation at the same instant", _observed_before_confirmation("2026-01-01T00:00:00+00:00"), False),
    ("verified scope: observation dated after the confirmation", _observed_before_confirmation("2026-01-01T00:00:01+00:00"), True),
    ("revoked with nothing verified", bare_revoked(), True),
    ("revoked with every approval guard met", tl._revoked(), False),
]

@pytest.mark.parametrize("label,rec,rejected", HAND_VERDICTS, ids=[h[0] for h in HAND_VERDICTS])
def test_the_package_and_the_checker_give_the_hand_written_verdict(label, rec, rejected):
    assert bool(tl.register_errors(rec, VOC)) is rejected, (label, tl.register_errors(rec, VOC))
    assert package_rejects(rec) is rejected, (label, package_message(rec))

def _set_rejected_by_package(recs):
    try:
        gov.check_register([gov.SourceDocumentVersion.parse(r) for r in recs])
    except (ValidationError, base.ContractError):
        return True
    return False

HAND_SET_VERDICTS = [
    ("supersession across categories with the same document", _cross_pair(document_category="curriculum_proposal_candidate"), True),
    ("supersession with the same category and document", tl._pair(), False),
]

@pytest.mark.parametrize("label,recs,rejected", HAND_SET_VERDICTS, ids=[h[0] for h in HAND_SET_VERDICTS])
def test_register_sets_give_the_hand_written_verdict(label, recs, rejected):
    assert bool(tl.register_set_errors(recs, VOC)) is rejected, (label, tl.register_set_errors(recs, VOC))
    assert _set_rejected_by_package(recs) is rejected, label


# Mutation regressions: vocabulary and bounds




_PACKAGE_VOCAB = base.VOCAB

def test_every_scope_field_of_the_vocabulary_is_a_field_of_the_register_model():
    assert set(_PACKAGE_VOCAB["scope_fields"]) <= set(gov.SourceDocumentVersion.model_fields)
    dims = set(gov.AffectedScope.model_fields) - {"capability"}
    assert dims <= set(_PACKAGE_VOCAB["scope_fields"])

def test_the_session_origins_of_the_vocabulary_are_exactly_what_a_session_fact_accepts():
    f = load("synthetic-session-fact.json")
    for origin in _PACKAGE_VOCAB["session_origins"]:
        gov.SessionFact.parse({**f, "origin": origin})
    for origin in ("staff_entry", "official_record", ""):
        with pytest.raises(ValidationError, match="String should match pattern '\\^\\(user_statement\\|private_upload"):
            gov.SessionFact.parse({**f, "origin": origin})

# ---------------------------------------------------------------- survivors of the first mutation run
def test_a_referred_conflict_still_blocks_its_capability():
    c = load("synthetic-conflict.json")
    referred = mut(c, lambda r: (r["evidence"].append(ev("ev-ref", "conflict_referral", "researcher")),
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
            gov.SourceDocumentVersion.parse(mut(register()[1], fn))
    gov.SourceDocumentVersion.parse(register()[1])

def test_a_dangling_evidence_reference_is_named():
    for state_field, state in (("verification_state", "verified"), ("acquisition_state", "verified"), ("approval_state", "approved")):
        with pytest.raises(ValidationError, match="not in the record"):
            gov.SourceDocumentVersion.parse(mut(register()[1], lambda r, f=state_field, s=state: r[f].update(
                state=s, evidence_ref="ev-nope")))
    with pytest.raises(ValidationError, match="not in the record"):
        gov.SourceConflict.parse(mut(load("synthetic-conflict.json"), lambda r: r.update(
            resolution_state="resolved", resolution_evidence_ref="ev-nope", resolution_basis="source_owner_ruling")))


# Mutation regressions: field and relationship guards


def test_evidence_authorizes_honours_the_from_state():
    e = gov.Evidence.model_validate(ev("ev-t", "issuing_office_authorization", "issuing_office", authorization_ref="a"))
    assert gov.evidence_authorizes("approval_state", "approved", e, frm="requested")
    assert not gov.evidence_authorizes("approval_state", "approved", e, frm="not_requested")
    assert gov.evidence_authorizes("approval_state", "approved", e)


# Mutation regressions: dates, identifiers and language markers







# 1. governance._date_span: month end taken as 28
@pytest.mark.parametrize("year", [2023, 2024, 1900, 2000])
def test_date_span_ends_on_the_real_last_day_of_each_month(year):
    for month in range(1, 13):
        first, last = gov._date_span(f"{year}-{month:02d}")
        assert first == date(year, month, 1)
        assert last == date(year, month, calendar.monthrange(year, month)[1])
    assert gov._date_span(str(year)) == (date(year, 1, 1), date(year, 12, 31))
    assert gov._date_span(f"{year}-07-04") == (date(year, 7, 4), date(year, 7, 4))

def test_date_span_leaves_other_formats_and_impossible_dates_alone():
    assert gov._date_span("soon") is None and gov._date_span(None) is None and gov._date_span("2023-02-30") is None
    assert gov._date_span("2023-1-01") is None and gov._date_span("2023-13") is None

# 2. governance._effectivity_errors: b[1] < a[0] became b[0] < a[0]
def test_a_partial_end_date_is_judged_by_its_last_possible_day():
    def effective(a, b):
        return tl.mutated(tl.register()[1], lambda r: (
            r["evidence"].append(tl.ev("ev-d", "printed_text_span", "researcher")),
            r["effective_from"].update(value=a, state="observed", evidence_ref="ev-d", basis="printed_text"),
            r["effective_to"].update(value=b, state="observed", evidence_ref="ev-d", basis="printed_text")))

    gov.SourceDocumentVersion.parse(effective("2023-06-15", "2023-06"))          # the month still has days to come
    gov.SourceDocumentVersion.parse(effective("2023-06-15", "2023-06-15"))       # one day
    gov.SourceDocumentVersion.parse(effective("2023-06-30", "2023-06"))          # the month's last day
    gov.SourceDocumentVersion.parse(effective("2024-02-29", "2024-02"))          # leap year
    for a, b in (("2023-06-15", "2023-06-14"), ("2023-07", "2023-06"), ("2024-03-01", "2024-02")):
        with pytest.raises(ValidationError, match="effective_to is before effective_from"):
            gov.SourceDocumentVersion.parse(effective(a, b))

def test_a_register_refuses_an_id_with_no_body():
    rec = tl.mutated(tl.register()[1], lambda r: r.__setitem__("document_id", "doc-"))
    with pytest.raises(ValidationError, match="String should match pattern '\\^doc\\\\\\-\\[a\\-z0\\-9\\-\\]\\+\\$"):
        gov.SourceDocumentVersion.parse(rec)
