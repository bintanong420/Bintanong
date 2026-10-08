"""Phase 1 Task 3, fix pass 3: revoked is as guarded as approved, the authorization-date guard covers all the
evidence a decision relies on, impossible calendar dates are refused, and authorization refs are compared
the way a person reads them. The package and the test-local checker must both give the verdict written here,
and each expected verdict below is written by hand, not derived from either implementation."""

from __future__ import annotations

import copy

import pytest
from pydantic import ValidationError

from backend.bintanong_contracts import base, governance as gov
import test_source_governance_manifests as tl

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
