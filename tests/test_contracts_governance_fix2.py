"""Phase 1 Task 3, fix pass 2 (governance): the `from` column, supersession, authorization, paths, scan.

Written red first against 86e48a0. Every guard below is a bypass an independent review of the
package demonstrated. All records are synthetic. Nothing here approves a source.
"""

from __future__ import annotations

import copy

import pytest
from pydantic import ValidationError

from backend.bintanong_contracts import base, governance as gov
import test_contracts_governance as g

ev, mut, load, register, approved_record = g.ev, g.mut, g.load, g.register, g.approved_record


def bad(rec, match):
    with pytest.raises((ValidationError, base.ContractError), match=match):
        gov.SourceDocumentVersion.parse(rec)


def ok(rec):
    return gov.SourceDocumentVersion.parse(rec)


def by_id(rec, eid):
    return next(e for e in rec["evidence"] if e["evidence_id"] == eid)


CHAIN = "earlier evidence"


# ---------------------------------------------------------------- H1: the `from` column
def test_approved_without_an_approval_request_is_rejected():
    rec = mut(approved_record(), lambda r: r.__setitem__(
        "evidence", [e for e in r["evidence"] if e["evidence_id"] != "ev-b5"]))
    bad(rec, CHAIN)
    ok(approved_record())


def test_a_request_recorded_after_the_authorization_is_rejected():
    def reorder(r):
        evs = {e["evidence_id"]: e for e in r["evidence"]}
        r["evidence"] = [e for e in r["evidence"] if e["evidence_id"] not in ("ev-b5", "ev-b6")] + [evs["ev-b6"], evs["ev-b5"]]
    bad(mut(approved_record(), reorder), CHAIN)


def test_an_authorization_dated_before_its_request_is_rejected_and_later_is_fine():
    bad(mut(approved_record(), lambda r: by_id(r, "ev-b6").update(recorded_at="2025-12-31T23:59:59+00:00")), CHAIN)
    ok(mut(approved_record(), lambda r: by_id(r, "ev-b6").update(recorded_at="2026-01-02T00:00:00+00:00")))


def revoked(ref="auth-synth-0001"):
    def fn(r):
        r["evidence"].append(ev("ev-b8", "issuing_office_revocation", "issuing_office", authorization_ref=ref,
                                recorded_at="2026-01-03T00:00:00+00:00"))
        r["approval_state"] = {"state": "revoked", "evidence_ref": "ev-b8"}
        r["approval_id"] = ref
    return mut(approved_record(), fn)


def test_revoked_needs_the_approval_chain_even_on_an_all_pending_record():
    ok(revoked())
    no_approval = mut(revoked(), lambda r: r.__setitem__(
        "evidence", [e for e in r["evidence"] if e["kind"] != "issuing_office_authorization"]))
    bad(no_approval, CHAIN)

    def only_revocation(r):
        r["evidence"].append(ev("ev-x", "issuing_office_revocation", "issuing_office", authorization_ref="auth-synth-0001"))
        r["approval_state"] = {"state": "revoked", "evidence_ref": "ev-x"}
        r["approval_id"] = "auth-synth-0001"
    bad(mut(register()[0], only_revocation), CHAIN)   # nothing was ever approved
    bad(mut(register()[1], only_revocation), CHAIN)


def test_a_revocation_must_cite_the_approvals_authorization_ref():
    bad(revoked(ref="auth-synth-0099"), "revocation must cite")


def test_rejected_needs_an_earlier_request():
    without = mut(register()[1], lambda r: (
        r["evidence"].append(ev("ev-x", "issuing_office_rejection", "issuing_office")),
        r["approval_state"].update(state="rejected", evidence_ref="ev-x")))
    bad(without, CHAIN)
    ok(mut(register()[1], lambda r: (
        r["evidence"].extend([ev("ev-q", "approval_request", "researcher"), ev("ev-x", "issuing_office_rejection", "issuing_office")]),
        r["approval_state"].update(state="rejected", evidence_ref="ev-x"))))


def test_verified_states_need_the_earlier_observed_evidence():
    only_confirmation = mut(register()[0], lambda r: (
        r["evidence"].append(ev("ev-v", "issuing_office_confirmation", "issuing_office")),
        r["verification_state"].update(state="verified", evidence_ref="ev-v")))
    bad(only_confirmation, CHAIN)
    only_hash = mut(register()[0], lambda r: (
        r.__setitem__("evidence", [ev("ev-s", "byte_hash_check", "system")]),
        r["acquisition_state"].update(state="verified", evidence_ref="ev-s")))
    bad(only_hash, CHAIN)
    mismatch_from_nothing = mut(register()[0], lambda r: (
        r.__setitem__("evidence", [ev("ev-s", "byte_hash_check", "system")]),
        r["acquisition_state"].update(state="mismatch", evidence_ref="ev-s")))
    bad(mismatch_from_nothing, CHAIN)
    scope = mut(register()[0], lambda r: (
        r["evidence"].append(ev("ev-o", "issuing_office_confirmation", "issuing_office")),
        r["issuer"].update(value="X", state="verified", evidence_ref="ev-o", basis="issuing_office_statement")))
    bad(scope, CHAIN)


def test_the_chain_is_recursive():
    # A2 (observed -> verified) is satisfied by a second hash check only when an earlier one entered observed.
    two_hashes = mut(register()[0], lambda r: (
        r["evidence"].append(ev("ev-a2", "byte_hash_check", "system", recorded_at="2026-01-02T00:00:00+00:00")),
        r["acquisition_state"].update(state="verified", evidence_ref="ev-a2")))
    ok(two_hashes)
    # the earlier hash check is dated later than the verifying one: the order is wrong
    bad(mut(two_hashes, lambda r: by_id(r, "ev-a2").update(recorded_at="2025-01-01T00:00:00+00:00")), CHAIN)


def test_an_unparseable_or_impossible_timestamp_is_an_error_not_a_crash():
    for stamp in ("9999-99-99T99:99:99Z", "2026-13-45T25:61:61Z"):
        with pytest.raises(ValidationError, match="not a real timestamp"):
            ok(mut(approved_record(), lambda r, s=stamp: by_id(r, "ev-b5").update(recorded_at=s)))


@pytest.mark.parametrize("stamp", [
    "2026-13-45T25:61:61Z", "2026-02-30T00:00:00Z", "2026-13-01T00:00:00Z", "2026-01-01T24:00:00Z",
    "2026-01-01T00:60:00Z", "2026-01-01T00:00:61Z", "2026-01-01T00:00:00+99:99", "2026-01-01T00:00:00-24:00",
    "9999-12-31T23:59:59Z", "0001-01-01T00:00:00Z", "\uff12\uff10\uff12\uff16-01-01T00:00:00Z"])
def test_recorded_at_must_be_a_real_calendar_timestamp_in_every_record_type(stamp):
    with pytest.raises(ValidationError, match="timestamp|String should match"):
        ok(mut(register()[1], lambda r: r["evidence"][0].update(recorded_at=stamp)))
    c = load("synthetic-conflict.json")
    c["evidence"].append(ev("ev-c9", "conflict_referral", "researcher", recorded_at=stamp))
    with pytest.raises(ValidationError, match="timestamp|String should match"):
        gov.SourceConflict.parse(c)
    f = load("synthetic-session-fact.json")
    f["evidence"].append(ev("ev-s9", "user_confirmation", "user", recorded_at=stamp))
    with pytest.raises(ValidationError, match="timestamp|String should match"):
        gov.SessionFact.parse(f)


def test_a_valid_timestamp_with_an_offset_is_accepted():
    ok(mut(register()[1], lambda r: r["evidence"][0].update(recorded_at="2026-01-01T07:59:59.123+08:00")))


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
    gov.check_register([ok(r) for r in regs])


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
    bad(mut(register()[1], build), message)


def test_a_reviewed_absence_of_supersession_stays_accepted():
    ok(mut(register()[1], lambda r: (
        r["evidence"].append(ev("ev-b7", "reviewer_absence_check", "reviewer")),
        r["supersession"].update(state="not_stated", evidence_ref="ev-b7"))))


def test_effective_to_before_effective_from_is_rejected():
    def dates(frm, to):
        def fn(r):
            r["evidence"].append(ev("ev-d", "printed_text_span", "researcher"))
            r["effective_from"].update(value=frm, state="observed", evidence_ref="ev-d", basis="printed_text")
            r["effective_to"].update(value=to, state="observed", evidence_ref="ev-d", basis="printed_text")
        return mut(register()[1], fn)
    ok(dates("2023-08-01", "2024-05-31"))
    ok(dates("2023-08-01", "2023-08-01"))
    ok(dates("2023", "2023-12"))            # partial dates overlap: not provably reversed
    ok(dates("not a date", "also not"))     # a format the owner has not fixed is not compared
    bad(dates("2024-05-31", "2023-08-01"), "effective_to is before effective_from")
    bad(dates("2024", "2023-12"), "effective_to is before effective_from")


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
    with pytest.raises(ValidationError):
        ok(rec)
    with pytest.raises(ValidationError):
        ok(mut(approved_record(), lambda r: r.__setitem__("approval_id", value)))


def test_an_authorization_dated_before_the_acquisition_or_the_scope_verification_is_rejected():
    bad(mut(approved_record(), lambda r: by_id(r, "ev-b6").update(recorded_at="2025-06-01T00:00:00+00:00")), "dated before")
    # the authorization may not precede the evidence that verified acquisition or scope either
    late_scope = mut(approved_record(), lambda r: by_id(r, "ev-b4").update(recorded_at="2026-01-05T00:00:00+00:00"))
    bad(late_scope, "dated before|earlier evidence")


# ---------------------------------------------------------------- M-d: paths and URLs
@pytest.mark.parametrize("name", ["file:///a.pdf", "~/a.pdf", "../a.pdf", "D:rel.pdf", "dir\\a.pdf", "C:\\x\\a.pdf",
                                  "/abs/a.pdf", "https://example.invalid/a.pdf", "a/b.pdf", "..", ".", "a\tb.pdf", "a\nb.pdf", "x:y.pdf"])
def test_filename_must_be_a_plain_name_not_a_path_or_url(name):
    bad(mut(register()[1], lambda r: r.update(filename=name)), "plain file name")


@pytest.mark.parametrize("good", ["synthetic-handbook.pdf", "Student Handbook (2023) v2.pdf", "a.b.c.pptx"])
def test_plain_filenames_are_accepted(good):
    ok(mut(register()[1], lambda r: r.update(filename=good)))


@pytest.mark.parametrize("loc", ["file:///a.pdf", "file://host/a.pdf", "C:\\Users\\x\\a.pdf", "C:/Users/x/a.pdf", "d:\\a", "\\\\host\\share",
                                 "/home/x/a.pdf", "/Users/x/a.pdf", "../a.pdf", "synthetic-locator-x/../y", "~/a.pdf",
                                 "a\\b", " leading", "x\ny", "/abs"])
def test_acquisition_locators_reject_local_paths(loc):
    bad(mut(register()[1], lambda r: r.update(acquisition_locators=["synthetic-locator-alpha/2", loc])), "locator")


@pytest.mark.parametrize("good", ["https://example.invalid/handbook.pdf", "synthetic-locator-alpha/2", "registrar-shelf-3/box-2"])
def test_logical_locators_and_https_urls_stay_accepted(good):
    ok(mut(register()[1], lambda r: r.update(acquisition_locators=[good])))


# ---------------------------------------------------------------- M-a: the namespace scan
PRIVATE_IN_INSTITUTIONAL = ["fact-synth-0001 ", "FACT-synth-0001", "fact-synth-0001\n", "\uff46act-synth-0001",
                            "fact\u2011synth-0001", "fact-synth-0001/x", "sess-synth-0001\t", " fact-synth-0001",
                            "see fact-synth-0001.", "(sess-synth-0001)", "x/FACT\u2010SYNTH-1", "fact-0001", "sess-7"]
INSTITUTIONAL_IN_SESSION = ["doc-synth-handbook\n", "ver-synth-0001 ", "DOC-synth-x", " edition-synth-1", "edition-synth-1/x",
                            "conflict-synth-0001\t", "\uff56er-synth-0001", "ver\u2011synth-0001", "doc-synth-handbook/x",
                            "ver-synth-0001#a", "ver-1"]
PROSE = ["Fact-checking Office of Records", "over-the-counter version-controlled copies", "edition-specific wording",
         "conflict-resolution procedure", "Doc-ument handling", "a fact", "xfact-synth-0001", "verification", "sess"]


@pytest.mark.parametrize("value", PRIVATE_IN_INSTITUTIONAL)
def test_private_id_variants_are_found_in_every_institutional_string(value):
    with pytest.raises(ValidationError, match="another namespace"):
        ok(mut(register()[1], lambda r: r["issuer"].update(value=value)))
    with pytest.raises(ValidationError, match="another namespace"):
        ok(mut(register()[1], lambda r: r.update(acquisition_locators=["synthetic-locator-alpha/2", "x/" + value.strip() + "/y"])))
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
    ok(mut(register()[1], lambda r: r["issuer"].update(value=value)))
    gov.SessionFact.parse(mut(load("synthetic-session-fact.json"), lambda r: r["fact"].update(value=value)))


def test_the_synthetic_examples_are_not_flagged():
    for rec in register():
        ok(rec)
    gov.SourceConflict.parse(load("synthetic-conflict.json"))
    gov.SessionFact.parse(load("synthetic-session-fact.json"))


def test_namespace_of_needs_more_than_a_bare_prefix_and_the_whole_id():
    for prefix in ("doc-", "ver-", "edition-", "conflict-", "sess-", "fact-"):
        assert base.namespace_of(prefix) is None, prefix
    assert base.namespace_of("doc-a") == "institutional" and base.namespace_of("fact-a") == "private_session"
    for padded in ("doc-a ", " doc-a", "doc-a\n", "DOC-a", "doc-a/b"):
        assert base.namespace_of(padded) is None, repr(padded)
