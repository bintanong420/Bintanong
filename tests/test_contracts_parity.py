"""Phase 1 Task 3, fix pass 2: the package and the test-local governance checker must agree.

The test-local checker (tests/test_source_governance_manifests.py) is the independent cross-check of the
schemas and the vocabulary. This file feeds both implementations the SAME documents (the synthetic
examples and its whole mutation corpus) and asserts the same verdict, accept or reject. A document one
accepts and the other rejects is a bug in one of them.
"""

from __future__ import annotations

import copy

import pytest
from pydantic import ValidationError

from backend.bintanong_contracts import base, governance as gov, symbolic
import test_source_governance_manifests as tl

VOC = tl.vocabulary()


def package_rejects_register(rec) -> bool:
    try:
        gov.SourceDocumentVersion.parse(rec)
    except (ValidationError, base.ContractError):
        return True
    return False


def package_rejects_register_set(recs) -> bool:
    try:
        gov.check_register([gov.SourceDocumentVersion.parse(r) for r in recs])
    except (ValidationError, base.ContractError):
        return True
    return False


def package_rejects_conflict(rec, versions=None) -> bool:
    try:
        c = gov.SourceConflict.parse(rec)
        if versions is not None:
            gov.check_conflict_versions(c, versions)
    except (ValidationError, base.ContractError):
        return True
    return False


def package_rejects(model, rec) -> bool:
    try:
        model.parse(rec)
    except (ValidationError, base.ContractError):
        return True
    return False


# ---------------------------------------------------------------- corpora (built once, deterministic)
def _auth_blank(bad):
    return tl.mutated(tl.approved_record(), lambda r: (r.__setitem__("approval_id", bad), r["evidence"][5].update(authorization_ref=bad)))


def _supersession_wrapped(fn):
    def build(r):
        r["evidence"].append(tl.ev("ev-b7", "reviewer_absence_check", "reviewer"))
        fn(r)
    return tl.mutated(tl.register()[1], build)


def _chain_cases():
    reg = tl.register
    no_request = tl.mutated(tl.approved_record(), lambda r: r.__setitem__(
        "evidence", [e for e in r["evidence"] if e["evidence_id"] != "ev-b5"]))
    reorder = tl.mutated(tl.approved_record(), lambda r: r.__setitem__("evidence", [
        e for e in r["evidence"] if e["evidence_id"] not in ("ev-b5", "ev-b6")] + [
        next(e for e in r["evidence"] if e["evidence_id"] == "ev-b6"),
        next(e for e in r["evidence"] if e["evidence_id"] == "ev-b5")]))
    early_auth = tl.mutated(tl.approved_record(), lambda r: next(
        e for e in r["evidence"] if e["evidence_id"] == "ev-b6").update(recorded_at="2025-12-31T23:59:59+00:00"))
    late_auth = tl.mutated(tl.approved_record(), lambda r: next(
        e for e in r["evidence"] if e["evidence_id"] == "ev-b6").update(recorded_at="2026-01-02T00:00:00+00:00"))
    only_revocation = tl.mutated(reg()[1], lambda r: (
        r["evidence"].append(tl.ev("ev-x", "issuing_office_revocation", "issuing_office", authorization_ref="auth-synth-0001")),
        r["approval_state"].update(state="revoked", evidence_ref="ev-x"), r.__setitem__("approval_id", "auth-synth-0001")))
    only_revocation_pending = tl.mutated(reg()[0], lambda r: (
        r["evidence"].append(tl.ev("ev-x", "issuing_office_revocation", "issuing_office", authorization_ref="auth-synth-0001")),
        r["approval_state"].update(state="revoked", evidence_ref="ev-x"), r.__setitem__("approval_id", "auth-synth-0001")))
    rejected_no_request = tl.mutated(reg()[1], lambda r: (
        r["evidence"].append(tl.ev("ev-x", "issuing_office_rejection", "issuing_office")),
        r["approval_state"].update(state="rejected", evidence_ref="ev-x")))
    rejected_with_request = tl.mutated(reg()[1], lambda r: (
        r["evidence"].extend([tl.ev("ev-q", "approval_request", "researcher"), tl.ev("ev-x", "issuing_office_rejection", "issuing_office")]),
        r["approval_state"].update(state="rejected", evidence_ref="ev-x")))
    only_conf = tl.mutated(reg()[0], lambda r: (
        r["evidence"].append(tl.ev("ev-v", "issuing_office_confirmation", "issuing_office")),
        r["verification_state"].update(state="verified", evidence_ref="ev-v")))
    only_hash = tl.mutated(reg()[0], lambda r: (
        r.__setitem__("evidence", [tl.ev("ev-s", "byte_hash_check", "system")]),
        r["acquisition_state"].update(state="verified", evidence_ref="ev-s")))
    mismatch = tl.mutated(reg()[0], lambda r: (
        r.__setitem__("evidence", [tl.ev("ev-s", "byte_hash_check", "system")]),
        r["acquisition_state"].update(state="mismatch", evidence_ref="ev-s")))
    scope = tl.mutated(reg()[0], lambda r: (
        r["evidence"].append(tl.ev("ev-o", "issuing_office_confirmation", "issuing_office")),
        r["issuer"].update(value="X", state="verified", evidence_ref="ev-o", basis="issuing_office_statement")))
    return {"no_request": no_request, "request_after_auth": reorder, "auth_before_request": early_auth,
            "auth_after_request": late_auth, "revocation_only": only_revocation,
            "revocation_only_pending": only_revocation_pending, "revoked_ok": tl._revoked(),
            "revoked_other_ref": tl._revoked(ref="auth-synth-0099"), "rejected_no_request": rejected_no_request,
            "rejected_with_request": rejected_with_request, "confirmation_only": only_conf,
            "hash_only_verified": only_hash, "mismatch_from_nothing": mismatch, "scope_verified_no_observed": scope}


def register_corpus():
    reg, out = tl.register, {}
    for i, r in enumerate(reg()):
        out[f"example[{i}]"] = r
    out["approved_record"] = tl.approved_record()
    for table, base_rec in ((tl.MALFORMED_REGISTER, reg()[0]), (tl.PRIVILEGED, reg()[0]), (tl.FORGED, reg()[1]),
                            (tl.APPROVAL_ID, reg()[1])):
        for name, fn in table.items():
            out[name] = tl.mutated(base_rec, fn)
    for name, fn in tl.APPROVED_GUARDS.items():
        out[f"approved:{name}"] = tl.mutated(tl.approved_record(), fn)
    for name, fn in tl.SUPERSESSION_RECORD_BAD.items():
        out[f"supersession:{name}"] = _supersession_wrapped(fn[0])
    out["supersession:reviewed_absence"] = tl.mutated(reg()[1], lambda r: (
        r["evidence"].append(tl.ev("ev-b7", "reviewer_absence_check", "reviewer")),
        r["supersession"].update(state="not_stated", evidence_ref="ev-b7")))
    out.update({f"chain:{k}": v for k, v in _chain_cases().items()})
    for stamp in ("9999-99-99T99:99:99Z", "2026-02-30T00:00:00Z", "2026-13-01T00:00:00Z", "2026-01-01T24:00:00Z",
                  "2026-01-01T00:60:00Z", "2026-01-01T00:00:61Z", "2026-13-45T25:61:61Z", "2026-01-01T00:00:00+99:99",
                  "9999-12-31T23:59:59Z", "2026-01-01T00:00:00Z\n"):
        out[f"stamp:{stamp!r}"] = tl.mutated(reg()[1], lambda r, s=stamp: tl._forge_ts(r, s))
    for value in ("", " ", "auth x", " auth-synth-0001", "auth-synth-0001 ", "auth-synth-0001\n"):
        out[f"authref:{value!r}"] = _auth_blank(value)
    for value in tl.PRIVATE_IN_INSTITUTIONAL + tl.LEGITIMATE_PROSE:
        out[f"issuer:{value!r}"] = tl.mutated(reg()[1], lambda r, v=value: r["issuer"].update(value=v))
    for name in ("C:\\Users\\x\\a.pdf", "C:/Users/x/a.pdf", "dir\\a.pdf", "/abs/a.pdf", "file:///a.pdf", "\\\\host\\share\\a.pdf",
                 "a/b.pdf", "x:y.pdf", "..", ".", "a\tb.pdf", "a\nb.pdf", "", "D:rel.pdf", "https://x.invalid/a.pdf",
                 "synthetic-handbook.pdf", "Student Handbook (2023) v2.pdf", "a.b.c.pptx"):
        out[f"filename:{name!r}"] = tl.mutated(reg()[1], lambda r, n=name: r.update(filename=n))
    for loc in ("C:\\Users\\x\\a.pdf", "C:/Users/x/a.pdf", "d:\\a", "\\\\host\\share", "/home/x/a.pdf", "/Users/x/a.pdf",
                "file:///a.pdf", "../a.pdf", "synthetic-locator-x/../y", "~/a.pdf", "a\\b", " leading", "", "x\ny",
                "https://example.invalid/handbook.pdf", "synthetic-locator-alpha/2", "registrar-shelf-3/box-2"):
        out[f"locator:{loc!r}"] = tl.mutated(reg()[1], lambda r, v=loc: r.update(acquisition_locators=["synthetic-locator-base/1", v]))
    for field, good in tl.ID_FIELDS:
        for bad in (good, good + "\n", good.upper(), " " + good, good + " ", good[:-1] + "_", "x" + good, ""):
            out[f"id:{field}:{bad!r}"] = tl.mutated(reg()[1], lambda r, f=field, b=bad: r.update({f: b}))
    for name, fn in (("dates_ok", ("2023-08-01", "2024-05-31")), ("dates_reversed", ("2024-05-31", "2023-08-01")),
                     ("dates_partial_overlap", ("2023", "2023-12")), ("dates_partial_reversed", ("2024", "2023-12")),
                     ("dates_unparsed", ("soon", "later"))):
        out[name] = tl.mutated(reg()[1], lambda r, d=fn: (
            r["evidence"].append(tl.ev("ev-d", "printed_text_span", "researcher")),
            r["effective_from"].update(value=d[0], state="observed", evidence_ref="ev-d", basis="printed_text"),
            r["effective_to"].update(value=d[1], state="observed", evidence_ref="ev-d", basis="printed_text")))
    out["authorization_before_scope_verification"] = tl.mutated(
        tl.approved_record(), lambda r: next(e for e in r["evidence"] if e["evidence_id"] == "ev-b4").update(
            recorded_at="2026-01-05T00:00:00+00:00"))
    return out


REGISTER = register_corpus()


@pytest.mark.parametrize("name", list(REGISTER))
def test_register_records_get_the_same_verdict(name):
    rec = REGISTER[name]
    assert bool(tl.register_errors(rec, VOC)) == package_rejects_register(rec), (
        name, tl.register_errors(rec, VOC))


def set_corpus():
    out = {"examples": tl.register()}
    out["empty"] = []
    out["pair"] = tl._pair()
    out["pair_inverse"] = tl._pair("superseded_by")
    regs = tl._pair()
    tl._sup(regs[0], "supersedes", regs[1]["version_id"])
    out["two_cycle"] = regs
    one_sided = tl._pair()
    one_sided[0]["supersession"] = copy.deepcopy(tl.register()[0]["supersession"])
    out["one_sided"] = one_sided
    chain = tl._chain3()
    twin = copy.deepcopy(chain[1])
    twin.update(version_id="ver-synth-handbook-3", edition_id="edition-synth-handbook-3", byte_sha256="b" * 64)
    chain.append(twin)
    h1, h2, h3 = chain[0], chain[1], chain[3]
    tl._sup(h3, "supersedes", h2["version_id"]); tl._sup(h2, "supersedes", h1["version_id"])
    h1["supersession"] = copy.deepcopy(tl.register()[0]["supersession"])
    chain[2]["supersession"] = copy.deepcopy(tl.register()[2]["supersession"])
    out["chain_of_three"] = copy.deepcopy(chain)
    tl._sup(h1, "supersedes", h3["version_id"])
    out["three_cycle"] = chain
    two_succ = tl._chain3()
    tw = copy.deepcopy(two_succ[1])
    tw.update(version_id="ver-synth-handbook-3", edition_id="edition-synth-handbook-3", byte_sha256="b" * 64)
    two_succ.append(tw)
    tl._sup(two_succ[1], "supersedes", two_succ[0]["version_id"]); tl._sup(two_succ[3], "supersedes", two_succ[0]["version_id"])
    tl._sup(two_succ[0], "superseded_by", two_succ[1]["version_id"])
    out["two_successors"] = two_succ
    for newer, older in ((1, 2), (2, 1)):
        cat = tl._chain3()
        tl._sup(cat[newer], "supersedes", cat[older]["version_id"]); tl._sup(cat[older], "superseded_by", cat[newer]["version_id"])
        out[f"category_{newer}_{older}"] = cat
    cross_doc = tl._pair()
    cross_doc[1]["document_id"] = "doc-synth-other"
    out["cross_document"] = cross_doc
    a, b = tl._twin_approved()
    out["same_authorization_ref"] = [a, b]
    out["distinct_authorization_refs"] = [a, tl.mutated(b, lambda r: (
        r.__setitem__("approval_id", "auth-synth-0002"),
        next(e for e in r["evidence"] if e["kind"] == "issuing_office_authorization").update(authorization_ref="auth-synth-0002")))]
    same_file = tl.register()
    same_file[1]["edition_id"] = same_file[0]["edition_id"]
    out["same_edition_other_bytes"] = same_file
    twin_bytes = tl.register()
    t2 = copy.deepcopy(twin_bytes[0])
    t2["version_id"], t2["edition_id"] = "ver-synth-twin", "edition-synth-twin"
    out["same_bytes"] = twin_bytes + [t2]
    out["duplicate_version"] = tl.register() + [copy.deepcopy(tl.register()[0])]
    missing = tl.register()
    missing[1]["supersession"].update(relation="supersedes", target_version_id="ver-synth-missing", state="observed",
                                      evidence_ref="ev-b3", basis="printed_text")
    out["target_missing"] = missing
    return out


SETS = set_corpus()


@pytest.mark.parametrize("name", list(SETS))
def test_register_sets_get_the_same_verdict(name):
    recs = SETS[name]
    assert bool(tl.register_set_errors(recs, VOC)) == package_rejects_register_set(recs), (
        name, tl.register_set_errors(recs, VOC))


def conflict_corpus():
    ids = {r["version_id"] for r in tl.register()}
    out = {"example": (tl.conflict(), ids), "resolved": (tl.mutated(tl.conflict(), tl._resolved), ids)}
    for name, fn in tl.CONFLICT_BAD.items():
        out[name] = (tl.mutated(tl.conflict(), fn), ids)
    for cap in (" enrollment_procedure_answers", "enrollment_procedure_answers ", "enrollment_procedure_answers\n", " ", ""):
        out[f"cap:{cap!r}"] = (tl.mutated(tl.conflict(), lambda r, c=cap: r["affected_scope"].update(capability=c)), ids)
    for value in tl.PRIVATE_IN_INSTITUTIONAL + tl.LEGITIMATE_PROSE:
        out[f"claim:{value!r}"] = (tl.mutated(tl.conflict(), lambda r, v=value: r["claims"][0].update(claim_text=v)), ids)
        out[f"span:{value!r}"] = (tl.mutated(tl.conflict(), lambda r, v=value: r["claims"][0].update(span_ref=v)), ids)
    return out


CONFLICTS = conflict_corpus()


@pytest.mark.parametrize("name", list(CONFLICTS))
def test_conflicts_get_the_same_verdict(name):
    rec, ids = CONFLICTS[name]
    assert bool(tl.conflict_errors(rec, VOC, ids)) == package_rejects_conflict(rec, ids), (name, tl.conflict_errors(rec, VOC, ids))


def session_corpus():
    out = {"example": tl.session_fact(), "confirmed": tl.mutated(tl.session_fact(), lambda r: (
        r["evidence"].append(tl.ev("ev-s1", "user_confirmation", "user")),
        r.update(confirmation_state="user_confirmed", confirmation_evidence_ref="ev-s1")))}
    for name, fn in tl.SESSION_BAD.items():
        out[name] = tl.mutated(tl.session_fact(), fn)
    for value in tl.INSTITUTIONAL_IN_SESSION + tl.LEGITIMATE_PROSE:
        out[f"value:{value!r}"] = tl.mutated(tl.session_fact(), lambda r, v=value: r["fact"].update(value=v))
        out[f"key:{value!r}"] = tl.mutated(tl.session_fact(), lambda r, v=value: r["fact"].update(key=v))
    for stamp in ("2026-13-45T25:61:61Z", "2026-02-30T00:00:00Z", "9999-12-31T23:59:59Z"):
        out[f"stamp:{stamp}"] = tl.mutated(tl.session_fact(), lambda r, s=stamp: r["evidence"].append(
            tl.ev("ev-s9", "user_confirmation", "user", recorded_at=s)))
    return out


SESSIONS = session_corpus()


@pytest.mark.parametrize("name", list(SESSIONS))
def test_session_facts_get_the_same_verdict(name):
    rec = SESSIONS[name]
    assert bool(tl.session_fact_errors(rec, VOC)) == package_rejects(gov.SessionFact, rec), (name, tl.session_fact_errors(rec, VOC))


DECISIONS = {d["outcome"]: d for d in tl.decisions()}


def decision_corpus():
    out = {f"example:{k}": v for k, v in DECISIONS.items()}
    for name, (base_outcome, fn) in tl.DECISION_BAD.items():
        out[name] = tl.mutated(DECISIONS[base_outcome], fn)
    for ok in ("stated_none", "reviewed_empty", "resolved"):
        out[f"prereq:{ok}"] = tl.mutated(DECISIONS["eligible"], tl._set(("prerequisite_rule_state",), ok))
    for bad in ("blank_unreviewed", "unreadable", "unresolved_reference", "standing_condition", "alternative_or_exception"):
        out[f"prereq:{bad}"] = tl.mutated(DECISIONS["eligible"], tl._set(("prerequisite_rule_state",), bad))
    out["unknown_blank"] = tl.mutated(DECISIONS["unknown"], lambda r: (
        r.update(rule_coverage="verified", prerequisite_rule_state="blank_unreviewed"), r["missing_facts"].clear()))
    return out


DECISION_CASES = decision_corpus()


@pytest.mark.parametrize("name", list(DECISION_CASES))
def test_decisions_get_the_same_verdict(name):
    rec = DECISION_CASES[name]
    assert bool(tl.decision_errors(rec, VOC)) == package_rejects(symbolic.DecisionOutcome, rec), (name, tl.decision_errors(rec, VOC))


def test_the_corpus_has_both_verdicts_in_every_family():
    for family, rejects in ((REGISTER, package_rejects_register), (SETS, package_rejects_register_set),
                            (SESSIONS, lambda r: package_rejects(gov.SessionFact, r)),
                            (DECISION_CASES, lambda r: package_rejects(symbolic.DecisionOutcome, r))):
        verdicts = {rejects(rec) for rec in family.values()}
        assert verdicts == {True, False}
    assert len(REGISTER) > 150 and len(SETS) >= 18 and len(CONFLICTS) > 40 and len(SESSIONS) > 40
