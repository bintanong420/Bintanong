"""Phase 1 Task 2: governance vocabulary, transition table and synthetic examples.

The validators below are TEST-LOCAL. They exist so the schemas, the vocabulary and the transition
table in knowledge/manifests/ can be checked now; the shared Python contracts that replace them are
Phase 1 Task 3 (backend/bintanong_contracts/). Nothing here approves a source or an edition: every
example is synthetic and uses fictional locators.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import pytest

from backend.bintanong_tools.prospectus_extractor import prerequisites

ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "knowledge" / "manifests"
EXAMPLES = MAN / "examples"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def vocabulary():
    return _load(MAN / "governance-vocabulary.json")


def schema(name: str):
    return _load(MAN / "schemas" / f"{name}.schema.json")


def register():
    return _load(EXAMPLES / "synthetic-register.json")


def conflict():
    return _load(EXAMPLES / "synthetic-conflict.json")


def session_fact():
    return _load(EXAMPLES / "synthetic-session-fact.json")


def decisions():
    return _load(EXAMPLES / "synthetic-decisions.json")


# --------------------------------------------------------------------------------------------
# Test-local JSON Schema subset. An unsupported keyword raises, so a schema cannot silently use a
# rule this checker ignores.
# --------------------------------------------------------------------------------------------
_IGNORED = {"$schema", "$id", "title", "description", "$comment", "$defs"}
_TYPES = {"null": type(None), "string": str, "boolean": bool, "object": dict, "array": list}


def _is_type(value, name):
    if name == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    return isinstance(value, _TYPES[name]) and not (name == "string" and isinstance(value, bool))


def schema_errors(value, sch, root=None, path="$"):
    root = root or sch
    errs = []
    for key, rule in sch.items():
        if key in _IGNORED:
            continue
        if key == "$ref":
            target = root
            for part in rule[2:].split("/"):
                target = target[part]
            errs += schema_errors(value, target, root, path)
        elif key == "type":
            names = rule if isinstance(rule, list) else [rule]
            if not any(_is_type(value, n) for n in names):
                errs.append(f"{path}: expected type {names}")
        elif key == "enum":
            if value not in rule:
                errs.append(f"{path}: {value!r} not in enum")
        elif key == "const":
            if value != rule:
                errs.append(f"{path}: expected const {rule!r}")
        elif key == "pattern":
            if isinstance(value, str) and not re.search(rule, value):
                errs.append(f"{path}: does not match {rule}")
        elif key == "minLength":
            if isinstance(value, str) and len(value) < rule:
                errs.append(f"{path}: shorter than {rule}")
        elif key == "minItems":
            if isinstance(value, list) and len(value) < rule:
                errs.append(f"{path}: fewer than {rule} items")
        elif key == "required":
            if isinstance(value, dict):
                errs += [f"{path}: missing {k}" for k in rule if k not in value]
        elif key == "properties":
            if isinstance(value, dict):
                for k, sub in rule.items():
                    if k in value:
                        errs += schema_errors(value[k], sub, root, f"{path}.{k}")
        elif key == "additionalProperties":
            assert rule is False, "test-local checker supports only additionalProperties: false"
            if isinstance(value, dict):
                errs += [f"{path}: unknown key {k}" for k in value if k not in sch.get("properties", {})]
        elif key == "items":
            if isinstance(value, list):
                for i, item in enumerate(value):
                    errs += schema_errors(item, rule, root, f"{path}[{i}]")
        else:
            raise AssertionError(f"unsupported schema keyword {key!r}")
    return errs


# --------------------------------------------------------------------------------------------
# Transition table
# --------------------------------------------------------------------------------------------
def transition_rows(voc, field, to_state, frm=None):
    return [t for t in voc["transitions"]
            if t["field"] == field and t["to"] == to_state and (frm is None or t["from"] == frm)]


def evidence_authorizes(voc, field, to_state, ev, frm=None):
    """True if `ev` can authorize entering `to_state` of `field` under some row of the table."""
    for row in transition_rows(voc, field, to_state, frm):
        if ev["kind"] != row["evidence_kind"] or ev["recorded_by"] not in row["recorded_by"]:
            continue
        if bool(ev.get("authorization_ref")) != bool(row.get("needs_authorization_ref")):
            continue
        return True
    return False


def transition_allowed(voc, field, frm, to_state, ev):
    return evidence_authorizes(voc, field, to_state, ev, frm)


# --------------------------------------------------------------------------------------------
# Namespaces
# --------------------------------------------------------------------------------------------
def _strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for v in node.values():
            yield from _strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from _strings(v)


def namespace_errors(rec, voc):
    ns = rec.get("namespace")
    if ns not in voc["namespaces"]:
        return [f"unknown namespace {ns!r}"]
    foreign = [p for other, spec in voc["namespaces"].items() if other != ns for p in spec["id_prefixes"]]
    return [f"id {s!r} belongs to another namespace than {ns}" for s in _strings(rec)
            if any(re.fullmatch(re.escape(p) + r"[a-z0-9-]+", s) for p in foreign)]


# --------------------------------------------------------------------------------------------
# Register record and set
# --------------------------------------------------------------------------------------------
STATE_FIELDS = ("acquisition_state", "verification_state", "approval_state", "content_review_state")


def _check_state(errs, voc, evidence, label, vocab_field, state, ref):
    if state == voc["initial_states"][vocab_field]:
        if ref is not None:
            errs.append(f"{label}: initial state {state} must not cite evidence")
        return
    if ref is None:
        errs.append(f"{label}: {state} without an evidence reference")
        return
    ev = evidence.get(ref)
    if ev is None:
        errs.append(f"{label}: evidence {ref!r} not in the record")
    elif not evidence_authorizes(voc, vocab_field, state, ev):
        errs.append(f"{label}: evidence {ref!r} ({ev['kind']} by {ev['recorded_by']}) cannot authorize {state}")


def register_errors(rec, voc):
    errs = schema_errors(rec, schema("source-register-v1"))
    if errs:
        return errs
    errs += namespace_errors(rec, voc)
    evs = {}
    for ev in rec["evidence"]:
        if ev["evidence_id"] in evs:
            errs.append(f"duplicate evidence id {ev['evidence_id']}")
        evs[ev["evidence_id"]] = ev
        needs = any(t["evidence_kind"] == ev["kind"] and t.get("needs_authorization_ref") for t in voc["transitions"])
        if needs != bool(ev.get("authorization_ref")):
            errs.append(f"evidence {ev['evidence_id']}: authorization_ref {'required' if needs else 'not allowed'}")
    for name in STATE_FIELDS:
        _check_state(errs, voc, evs, name, name, rec[name]["state"], rec[name]["evidence_ref"])
    for name in voc["scope_fields"] + ["supersession"]:
        f = rec[name]
        _check_state(errs, voc, evs, name, "scope_field", f["state"], f["evidence_ref"])
        has_value = f["value"] is not None if name != "supersession" else rec[name]["relation"] != "none"
        if name != "supersession":
            if f["state"] in ("pending", "not_stated") and (f["value"] is not None or f["basis"] is not None):
                errs.append(f"{name}: {f['state']} must carry no value and no basis (nothing is inferred)")
            if f["state"] in ("observed", "verified") and (not has_value or f["basis"] is None):
                errs.append(f"{name}: {f['state']} needs a value and an allowed basis")
        else:
            if f["relation"] != "none":
                if f["target_version_id"] is None or f["state"] == "pending":
                    errs.append("supersession: a relation needs a target and an evidenced state")
                if f["target_version_id"] == rec["version_id"]:
                    errs.append("supersession: a version cannot supersede itself")
            elif f["target_version_id"] is not None:
                errs.append("supersession: relation none must not name a target")
    if rec["verification_state"]["state"] in ("observed", "verified") and \
            rec["acquisition_state"]["state"] not in ("observed", "verified"):
        errs.append("verification recorded against bytes that are not acquired and matching")
    appr, aid = rec["approval_state"], rec["approval_id"]
    if appr["state"] in ("approved", "revoked"):
        ev = evs.get(appr["evidence_ref"])
        if not aid or ev is None or ev.get("authorization_ref") != aid:
            errs.append("approval_id must equal the authorization_ref of the cited authorized evidence")
    elif aid is not None:
        errs.append("approval_id supplied without authorized approval evidence")
    if appr["state"] == "approved":
        if rec["acquisition_state"]["state"] != "verified" or rec["verification_state"]["state"] != "verified":
            errs.append("approval needs verified acquisition and verified scope")
        if rec["issuer"]["state"] != "verified" or any(
                rec[f]["state"] not in ("verified", "not_stated") for f in voc["scope_fields"]):
            errs.append("approval needs issuer and scope/effectivity fields verified or explicitly not stated")
        if rec["document_category"] in voc["proposal_categories"]:
            errs.append("a proposal candidate cannot be approved as a source")
    return errs


def register_set_errors(recs, voc):
    errs = []
    for r in recs:
        errs += [f"{r.get('version_id')}: {e}" for e in register_errors(r, voc)]
    ids = [r["version_id"] for r in recs]
    errs += [f"duplicate version_id {v}" for v in set(ids) if ids.count(v) > 1]
    by_hash, by_edition = {}, {}
    for r in recs:
        by_hash.setdefault(r["byte_sha256"], []).append(r["version_id"])
        by_edition.setdefault(r["edition_id"], set()).add(r["byte_sha256"])
    errs += [f"same bytes recorded as separate versions {v}; merge locators" for v in by_hash.values() if len(v) > 1]
    errs += [f"edition {e} spans different bytes (same filename is not same edition)"
             for e, h in by_edition.items() if len(h) > 1]
    for r in recs:
        tgt = r["supersession"]["target_version_id"]
        if tgt is not None and tgt not in ids:
            errs.append(f"{r['version_id']}: supersession target {tgt} is not in the register")
    return errs


# --------------------------------------------------------------------------------------------
# Conflict, session fact, decision
# --------------------------------------------------------------------------------------------
def conflict_errors(rec, voc, version_ids=None):
    errs = schema_errors(rec, schema("source-conflict-v1"))
    if errs:
        return errs
    errs += namespace_errors(rec, voc)
    evs = {e["evidence_id"]: e for e in rec["evidence"]}
    if len({(c["version_id"], c["span_ref"]) for c in rec["claims"]}) < 2:
        errs.append("a conflict needs two distinct claims")
    state, ref, basis = rec["resolution_state"], rec["resolution_evidence_ref"], rec["resolution_basis"]
    _check_state(errs, voc, evs, "resolution", "conflict_resolution_state", state, ref)
    if (state == "resolved") != (basis is not None):
        errs.append("a resolution basis is required exactly when the conflict is resolved")
    if version_ids is not None:
        errs += [f"claim cites unknown version {c['version_id']}" for c in rec["claims"] if c["version_id"] not in version_ids]
    return errs


def blocked_capabilities(conflicts):
    return {c["affected_scope"]["capability"] for c in conflicts if c["resolution_state"] != "resolved"}


def session_fact_errors(rec, voc):
    errs = schema_errors(rec, schema("session-fact-v1"))
    if errs:
        return errs
    errs += namespace_errors(rec, voc)
    evs = {e["evidence_id"]: e for e in rec["evidence"]}
    _check_state(errs, voc, evs, "confirmation", "session_confirmation_state",
                 rec["confirmation_state"], rec["confirmation_evidence_ref"])
    return errs


def decision_errors(rec, voc):
    errs = schema_errors(rec, schema("decision-v1"))
    if errs:
        return errs
    d = voc["decision"]
    rule = d["outcomes"][rec["outcome"]]
    if rule["predicate_supported"] != "any" and rec["predicate_supported"] != rule["predicate_supported"]:
        errs.append(f"{rec['outcome']}: predicate_supported must be {rule['predicate_supported']}")
    if rec["rule_coverage"] not in rule["rule_coverage"]:
        errs.append(f"{rec['outcome']}: rule_coverage {rec['rule_coverage']} not permitted")
    prs = rec["prerequisite_rule_state"]
    if rule["prerequisite_rule_state"] == "executable_or_null" and prs is not None \
            and prs not in d["executable_prerequisite_rule_states"]:
        errs.append(f"{rec['outcome']}: prerequisite rule state {prs} is not executable")
    errs += [f"{rec['outcome']}: {k} must not be empty" for k in rule["nonempty"] if not rec[k]]
    errs += [f"{rec['outcome']}: {k} must be empty" for k in rule["empty"] if rec[k]]
    if (rule["error_code"] == "null") != (rec["error_code"] is None):
        errs.append(f"{rec['outcome']}: error_code {'must be null' if rule['error_code'] == 'null' else 'is required'}")
    if rule["needs_unknown_reason"]:
        reason = (rec["missing_facts"] or rec["unknown_conditions"] or rec["unresolved_conflicts"]
                  or rec["rule_coverage"] != "verified"
                  or (prs is not None and prs not in d["executable_prerequisite_rule_states"]))
        if not reason:
            errs.append("unknown: names no missing fact, unknown condition, conflict or coverage gap")
    return errs


# --------------------------------------------------------------------------------------------
# Helpers to build mutated copies
# --------------------------------------------------------------------------------------------
def mutated(rec, fn):
    c = copy.deepcopy(rec)
    fn(c)
    return c


def ev(eid, kind, by, **extra):
    return {"evidence_id": eid, "kind": kind, "recorded_by": by, "recorded_at": "2026-01-01T00:00:00+00:00", **extra}


def approved_record():
    """A fully evidenced SYNTHETIC record: shows the guards pass when evidence is real."""
    r = copy.deepcopy(register()[1])
    r["evidence"] += [
        ev("ev-b4", "issuing_office_confirmation", "issuing_office"),
        ev("ev-b5", "approval_request", "researcher"),
        ev("ev-b6", "issuing_office_authorization", "issuing_office", authorization_ref="auth-synth-0001"),
        ev("ev-b7", "reviewer_absence_check", "reviewer"),
    ]
    for f in ("issuer", "printed_revision"):
        r[f]["state"], r[f]["evidence_ref"], r[f]["basis"] = "verified", "ev-b4", "issuing_office_statement"
    for f in ("campus", "college", "program", "cohort", "effective_from", "effective_to"):
        r[f]["state"], r[f]["evidence_ref"] = "not_stated", "ev-b7"
    r["verification_state"] = {"state": "verified", "evidence_ref": "ev-b4"}
    r["approval_state"] = {"state": "approved", "evidence_ref": "ev-b6"}
    r["approval_id"] = "auth-synth-0001"
    return r


# ============================================================================================
# Vocabulary and transition table
# ============================================================================================
def test_vocabulary_is_internally_consistent():
    voc = vocabulary()
    ids = [t["id"] for t in voc["transitions"]]
    assert len(ids) == len(set(ids))
    for t in voc["transitions"]:
        states = voc["states"][t["field"]]
        assert t["from"] in states and t["to"] in states and t["from"] != t["to"], t["id"]
        assert t["evidence_kind"] in voc["evidence_kinds"]["authorizing"], t["id"]
        assert set(t["recorded_by"]) <= set(voc["roles"]), t["id"]
    assert not set(voc["evidence_kinds"]["authorizing"]) & set(voc["evidence_kinds"]["non_authorizing"])
    for field, states in voc["states"].items():
        assert voc["initial_states"][field] in states
        reachable, frontier = {voc["initial_states"][field]}, True
        while frontier:
            frontier = {t["to"] for t in voc["transitions"] if t["field"] == field and t["from"] in reachable} - reachable
            reachable |= frontier
        assert reachable == set(states), f"{field}: states with no evidenced path: {set(states) - reachable}"


def test_no_state_is_reachable_without_its_own_evidence_kind():
    voc = vocabulary()
    # Skipping a step is not in the table: nothing goes straight to verified/approved/reviewed-by-approval.
    assert not transition_rows(voc, "verification_state", "verified", "pending")
    assert not transition_rows(voc, "acquisition_state", "verified", "pending")
    assert not transition_rows(voc, "approval_state", "approved", "not_requested")
    assert not transition_rows(voc, "scope_field", "verified", "pending")
    used = {t["evidence_kind"] for t in voc["transitions"]}
    assert not used & set(voc["evidence_kinds"]["non_authorizing"])
    approval_kinds = {t["evidence_kind"] for t in voc["transitions"] if t["field"] == "approval_state" and t["to"] == "approved"}
    review_kinds = {t["evidence_kind"] for t in voc["transitions"] if t["field"] == "content_review_state"}
    assert approval_kinds == {"issuing_office_authorization"} and not approval_kinds & review_kinds


def test_vocabulary_reuses_extractor_prerequisite_states():
    d = vocabulary()["decision"]
    assert tuple(d["prerequisite_rule_states"]) == prerequisites.PREREQUISITE_STATES
    assert frozenset(d["executable_prerequisite_rule_states"]) == prerequisites.EXECUTABLE_PREREQUISITE_STATES


def test_schema_enums_match_the_vocabulary():
    voc = vocabulary()
    reg = schema("source-register-v1")["$defs"]
    for name in STATE_FIELDS:
        assert reg[name]["properties"]["state"]["enum"] == voc["states"][name]
    assert reg["scope_field"]["properties"]["state"]["enum"] == voc["states"]["scope_field"]
    assert reg["supersession"]["properties"]["relation"]["enum"] == voc["supersession_relations"]
    assert reg["evidence"]["properties"]["kind"]["enum"] == voc["evidence_kinds"]["authorizing"] + voc["evidence_kinds"]["non_authorizing"]
    assert reg["evidence"]["properties"]["recorded_by"]["enum"] == voc["roles"]
    props = schema("source-register-v1")["properties"]
    assert props["document_category"]["enum"] == voc["document_categories"]
    assert set(voc["scope_fields"]) <= set(props)
    assert schema("source-conflict-v1")["properties"]["resolution_state"]["enum"] == voc["states"]["conflict_resolution_state"]
    assert schema("source-conflict-v1")["properties"]["resolution_basis"]["enum"] == voc["conflict_resolution_bases"] + [None]
    assert schema("session-fact-v1")["properties"]["confirmation_state"]["enum"] == voc["states"]["session_confirmation_state"]
    assert schema("decision-v1")["properties"]["outcome"]["enum"] == list(voc["decision"]["outcomes"])


def test_decision_outcomes_are_a_closed_set_of_five():
    assert set(vocabulary()["decision"]["outcomes"]) == {"eligible", "ineligible", "unknown", "unsupported", "error"}


def test_forbidden_inference_bases_cannot_support_any_field():
    voc = vocabulary()
    allowed, forbidden = set(voc["field_bases"]["allowed"]), set(voc["field_bases"]["forbidden_inference"])
    assert not allowed & forbidden
    assert {"filename_date", "college_vs_university_wording", "local_possession"} == forbidden
    for bad in forbidden:
        rec = mutated(register()[1], lambda r, b=bad: r["effective_from"].update(
            value="2023-08-01", state="observed", evidence_ref="ev-b3", basis=b))
        assert schema_errors(rec, schema("source-register-v1")), bad


@pytest.mark.parametrize("field,frm,to,kind,by,auth,ok", [
    ("approval_state", "requested", "approved", "issuing_office_authorization", "issuing_office", "auth-1", True),
    ("approval_state", "not_requested", "approved", "issuing_office_authorization", "issuing_office", "auth-1", False),
    ("approval_state", "requested", "approved", "issuing_office_authorization", "researcher", "auth-1", False),
    ("approval_state", "requested", "approved", "issuing_office_authorization", "issuing_office", None, False),
    ("approval_state", "requested", "approved", "extraction_audit", "system", None, False),
    ("approval_state", "requested", "approved", "content_review_record", "reviewer", None, False),
    ("verification_state", "pending", "verified", "issuing_office_confirmation", "issuing_office", None, False),
    ("verification_state", "observed", "verified", "extractor_status_label", "system", None, False),
    ("verification_state", "observed", "verified", "issuing_office_confirmation", "issuing_office", None, True),
    ("verification_state", "verified", "pending", "printed_text_span", "researcher", None, False),
    ("content_review_state", "partially_reviewed", "reviewed", "content_review_record", "reviewer", None, True),
    ("content_review_state", "partially_reviewed", "reviewed", "content_review_record", "researcher", None, False),
    ("acquisition_state", "observed", "verified", "byte_hash_check", "researcher", None, False),
    ("acquisition_state", "verified", "mismatch", "byte_hash_check", "system", None, True),
    ("session_confirmation_state", "unconfirmed", "user_confirmed", "user_confirmation", "user", None, True),
    ("session_confirmation_state", "unconfirmed", "user_confirmed", "user_confirmation", "issuing_office", None, False),
])
def test_transition_table_decides(field, frm, to, kind, by, auth, ok):
    e = ev("ev-x", kind, by, **({"authorization_ref": auth} if auth else {}))
    assert transition_allowed(vocabulary(), field, frm, to, e) is ok


# ============================================================================================
# Existing and new synthetic examples
# ============================================================================================
def test_every_manifest_json_is_synthetic_and_has_no_local_path():
    local = re.compile(r"[A-Za-z]:[\\/]|\\\\|/Users/|/home/|file://|\.\./")
    files = sorted(EXAMPLES.glob("*.json"))
    assert len(files) >= 4
    for f in files:
        assert not local.search(f.read_text(encoding="utf-8")), f.name
        data = _load(f)
        for rec in data if isinstance(data, list) else [data]:
            assert rec["synthetic"] is True, f.name
    for rec in register():
        for loc in rec["acquisition_locators"]:
            assert re.fullmatch(r"synthetic-locator-[a-z0-9-]+/\d+", loc), loc


def test_existing_and_new_examples_validate():
    voc = vocabulary()
    regs = register()
    assert register_set_errors(regs, voc) == []
    assert register_errors(approved_record(), voc) == []
    assert conflict_errors(conflict(), voc, {r["version_id"] for r in regs}) == []
    assert session_fact_errors(session_fact(), voc) == []
    outcomes = [d["outcome"] for d in decisions()]
    assert sorted(outcomes) == sorted(vocabulary()["decision"]["outcomes"])
    for d in decisions():
        assert decision_errors(d, voc) == [], d["outcome"]


def test_example_register_keeps_distinct_versions_and_the_proposal_candidate():
    regs = {r["version_id"]: r for r in register()}
    h1, h2 = regs["ver-synth-handbook-1"], regs["ver-synth-handbook-2"]
    assert h1["filename"] == h2["filename"] and h1["byte_sha256"] != h2["byte_sha256"]
    assert h1["edition_id"] != h2["edition_id"]
    assert len(h1["acquisition_locators"]) == 2  # duplicate locations preserved on one byte identity
    prop = regs["ver-synth-proposal-1"]
    assert prop["document_category"] == "curriculum_proposal_candidate" and prop["approval_id"] is None
    assert all(r["approval_id"] is None and r["approval_state"]["state"] == "not_requested" for r in regs.values())


def test_content_review_and_approval_are_separate_transitions():
    voc = vocabulary()
    reviewed_only = mutated(register()[1], lambda r: (
        r["evidence"].append(ev("ev-r1", "content_review_record", "reviewer")),
        r.__setitem__("content_review_state", {"state": "reviewed", "evidence_ref": "ev-r1"})))
    assert register_errors(reviewed_only, voc) == []
    assert reviewed_only["approval_state"]["state"] == "not_requested" and reviewed_only["approval_id"] is None
    # content review evidence cannot be cited for approval
    forged = mutated(approved_record(), lambda r: (
        r["evidence"].append(ev("ev-r1", "content_review_record", "reviewer")),
        r["approval_state"].update(evidence_ref="ev-r1")))
    assert register_errors(forged, voc)


# ============================================================================================
# Negative cases: each guard must fail
# ============================================================================================
def _set(path, value):
    def fn(rec):
        node = rec
        for p in path[:-1]:
            node = node[p]
        node[path[-1]] = value
    return fn


def _del(key):
    return lambda r: r.pop(key)


MALFORMED_REGISTER = {
    "missing_required_key": _del("byte_sha256"),
    "short_hash": _set(("byte_sha256",), "abc"),
    "wrong_schema_version": _set(("schema_version",), "bintanong-source-register-v2"),
    "wrong_namespace": _set(("namespace",), "private_session"),
    "locators_empty": _set(("acquisition_locators",), []),
    "unknown_category": _set(("document_category",), "official_curriculum"),
    "unknown_extra_key": _set(("approved",), True),
    "extractor_status_key": _set(("promotion_status",), "EXTRACTED"),
    "state_not_an_object": _set(("verification_state",), "verified"),
    "bad_timestamp": _set(("evidence", 0, "recorded_at"), "yesterday"),
}


@pytest.mark.parametrize("name", MALFORMED_REGISTER)
def test_malformed_register_record_is_rejected(name):
    assert register_errors(mutated(register()[0], MALFORMED_REGISTER[name]), vocabulary())


PRIVILEGED = {
    "approval_value_in_verification": _set(("verification_state", "state"), "approved"),
    "verified_value_in_approval": _set(("approval_state", "state"), "verified"),
    "extracted_as_state": _set(("verification_state", "state"), "EXTRACTED"),
    "official_as_state": _set(("acquisition_state", "state"), "official"),
    "approved_flag_key": _set(("is_approved",), True),
    "verified_key_in_state": lambda r: r["verification_state"].update(verified=True),
}


@pytest.mark.parametrize("name", PRIVILEGED)
def test_unknown_privileged_status_assertions_are_rejected(name):
    assert register_errors(mutated(register()[0], PRIVILEGED[name]), vocabulary())


FORGED = {
    "verified_without_evidence": lambda r: r["verification_state"].update(state="verified", evidence_ref=None),
    "verified_with_dangling_ref": lambda r: r["verification_state"].update(state="verified", evidence_ref="ev-nope"),
    "verified_citing_wrong_kind": lambda r: r["verification_state"].update(state="verified", evidence_ref="ev-b2"),
    "verified_by_extraction_audit": lambda r: (
        r["evidence"].append(ev("ev-x", "extraction_audit", "system")),
        r["verification_state"].update(state="verified", evidence_ref="ev-x")),
    "verified_by_extractor_label": lambda r: (
        r["evidence"].append(ev("ev-x", "extractor_status_label", "system")),
        r["verification_state"].update(state="verified", evidence_ref="ev-x")),
    "verified_by_researcher_claiming_office": lambda r: (
        r["evidence"].append(ev("ev-x", "issuing_office_confirmation", "researcher")),
        r["verification_state"].update(state="verified", evidence_ref="ev-x")),
    "acquisition_verified_by_researcher": lambda r: (
        r["evidence"].append(ev("ev-x", "byte_hash_check", "researcher")),
        r["acquisition_state"].update(state="verified", evidence_ref="ev-x")),
    "approved_without_evidence": lambda r: r["approval_state"].update(state="approved", evidence_ref=None),
    "approved_by_content_review": lambda r: (
        r["evidence"].append(ev("ev-x", "content_review_record", "reviewer")),
        r["approval_state"].update(state="approved", evidence_ref="ev-x")),
    "approved_by_extraction_audit": lambda r: (
        r["evidence"].append(ev("ev-x", "extraction_audit", "system")),
        r["approval_state"].update(state="approved", evidence_ref="ev-x")),
    "initial_state_citing_evidence": lambda r: r["approval_state"].update(evidence_ref="ev-b1"),
    "review_reviewed_by_researcher": lambda r: (
        r["evidence"].append(ev("ev-x", "content_review_record", "researcher")),
        r["content_review_state"].update(state="reviewed", evidence_ref="ev-x")),
    "observed_field_without_basis": lambda r: r["issuer"].update(value="X", state="observed", evidence_ref="ev-b3", basis=None),
    "pending_field_with_inferred_value": lambda r: r["effective_from"].update(value="2023"),
    "supersession_without_target": lambda r: r["supersession"].update(relation="supersedes", state="observed", evidence_ref="ev-b3", basis="printed_text"),
    "supersession_without_evidence": lambda r: r["supersession"].update(relation="supersedes", target_version_id="ver-synth-handbook-1"),
    "self_supersession": lambda r: r["supersession"].update(relation="supersedes", target_version_id="ver-synth-handbook-2", state="observed", evidence_ref="ev-b3", basis="printed_text"),
    "verification_on_unmatched_bytes": lambda r: r["acquisition_state"].update(state="mismatch"),
}


@pytest.mark.parametrize("name", FORGED)
def test_forged_state_without_authorized_evidence_is_rejected(name):
    assert register_errors(mutated(register()[1], FORGED[name]), vocabulary())


APPROVAL_ID = {
    "id_with_no_approval": lambda r: r.__setitem__("approval_id", "auth-synth-0001"),
    "id_with_requested_only": lambda r: (
        r["evidence"].append(ev("ev-x", "approval_request", "researcher")),
        r["approval_state"].update(state="requested", evidence_ref="ev-x"),
        r.__setitem__("approval_id", "auth-synth-0001")),
    "id_without_authorization_ref_on_evidence": lambda r: (
        r["evidence"].append(ev("ev-x", "issuing_office_authorization", "issuing_office")),
        r["approval_state"].update(state="approved", evidence_ref="ev-x"),
        r.__setitem__("approval_id", "auth-synth-0001")),
    "authorization_ref_on_unrelated_evidence": lambda r: r["evidence"][0].update(authorization_ref="auth-synth-0001"),
}


@pytest.mark.parametrize("name", APPROVAL_ID)
def test_approval_id_without_authorized_evidence_is_rejected(name):
    assert register_errors(mutated(register()[1], APPROVAL_ID[name]), vocabulary())


APPROVED_GUARDS = {
    "id_not_matching_authorization": _set(("approval_id",), "auth-other"),
    "id_missing": _set(("approval_id",), None),
    "acquisition_only_observed": lambda r: r["acquisition_state"].update(state="observed", evidence_ref="ev-b1"),
    "scope_only_observed": lambda r: r["verification_state"].update(state="observed", evidence_ref="ev-b3"),
    "issuer_not_verified": lambda r: r["issuer"].update(state="observed", evidence_ref="ev-b3", basis="printed_text"),
    "issuer_not_stated": lambda r: r["issuer"].update(value=None, state="not_stated", evidence_ref="ev-b7", basis=None),
    "effective_field_unresolved": lambda r: r["effective_from"].update(value=None, state="pending", evidence_ref=None, basis=None),
    "proposal_candidate": _set(("document_category",), "curriculum_proposal_candidate"),
}


def test_approved_record_passes_only_with_every_guard():
    assert register_errors(approved_record(), vocabulary()) == []
    for name, fn in APPROVED_GUARDS.items():
        assert register_errors(mutated(approved_record(), fn), vocabulary()), name


def test_register_set_rejects_same_filename_different_hash_as_one_edition():
    regs = register()
    regs[1]["edition_id"] = regs[0]["edition_id"]  # "same filename, so same edition"
    errs = register_set_errors(regs, vocabulary())
    assert any("same filename is not same edition" in e for e in errs)


def test_register_set_rejects_same_bytes_as_separate_versions_and_duplicate_ids():
    voc = vocabulary()
    regs = register()
    twin = copy.deepcopy(regs[0])
    twin["version_id"], twin["edition_id"] = "ver-synth-twin", "edition-synth-twin"
    assert any("same bytes" in e for e in register_set_errors(regs + [twin], voc))
    dup = copy.deepcopy(regs[0])
    assert any("duplicate version_id" in e for e in register_set_errors(regs + [dup], voc))


def test_register_set_rejects_supersession_target_outside_the_register():
    regs = register()
    regs[1]["supersession"].update(relation="supersedes", target_version_id="ver-synth-missing",
                                   state="observed", evidence_ref="ev-b3", basis="printed_text")
    assert any("not in the register" in e for e in register_set_errors(regs, vocabulary()))


# ---------------------------------- conflicts ------------------------------------------------
def _resolved(rec):
    rec["evidence"].append(ev("ev-c1", "issuing_office_resolution", "issuing_office"))
    rec.update(resolution_state="resolved", resolution_evidence_ref="ev-c1", resolution_basis="source_owner_ruling")


def test_resolved_conflict_with_authorized_evidence_passes():
    assert conflict_errors(mutated(conflict(), _resolved), vocabulary()) == []


CONFLICT_BAD = {
    "one_claim": lambda r: r["claims"].pop(),
    "duplicate_claim": lambda r: r["claims"].append(copy.deepcopy(r["claims"][0])) or r["claims"].pop(1),
    "resolved_without_evidence": lambda r: r.update(resolution_state="resolved", resolution_basis="source_owner_ruling"),
    "resolved_without_basis": lambda r: (_resolved(r), r.update(resolution_basis=None)),
    "resolved_by_researcher": lambda r: (_resolved(r), r["evidence"][0].update(recorded_by="researcher")),
    "newest_filename_basis": lambda r: (_resolved(r), r.update(resolution_basis="newest_filename")),
    "office_precedence_basis": lambda r: (_resolved(r), r.update(resolution_basis="office_precedence")),
    "unresolved_with_evidence": lambda r: r.update(resolution_evidence_ref="ev-c1"),
    "unresolved_with_basis": lambda r: r.update(resolution_basis="source_owner_ruling"),
    "resolved_by_extraction_audit": lambda r: (_resolved(r), r["evidence"][0].update(kind="extraction_audit")),
    "unknown_version": lambda r: r["claims"][0].update(version_id="ver-synth-nowhere"),
    "private_namespace": _set(("namespace",), "private_session"),
    "missing_scope_capability": lambda r: r["affected_scope"].pop("capability"),
    "private_fact_id_as_span": lambda r: r["claims"][0].update(span_ref="fact-synth-0001"),
    "session_id_as_span": lambda r: r["claims"][0].update(span_ref="sess-synth-0001"),
    "private_fact_id_as_version": lambda r: r["claims"][0].update(version_id="fact-synth-0001"),
}


@pytest.mark.parametrize("name", CONFLICT_BAD)
def test_bad_conflict_record_is_rejected(name):
    ids = {r["version_id"] for r in register()}
    assert conflict_errors(mutated(conflict(), CONFLICT_BAD[name]), vocabulary(), ids)


def test_unresolved_conflict_blocks_only_its_capability():
    c = conflict()
    assert blocked_capabilities([c]) == {"enrollment_procedure_answers"}
    other = mutated(c, lambda r: r["affected_scope"].update(capability="prerequisite_eligibility"))
    assert blocked_capabilities([c, other]) == {"enrollment_procedure_answers", "prerequisite_eligibility"}
    assert blocked_capabilities([mutated(c, _resolved), other]) == {"prerequisite_eligibility"}
    assert "grade_policy_answers" not in blocked_capabilities([c, other])


# ---------------------------------- session facts --------------------------------------------
SESSION_BAD = {
    "institutional_namespace": _set(("namespace",), "institutional"),
    "institutional_style_fact_id": _set(("fact_id",), "ver-synth-0001"),
    "institutional_style_session_id": _set(("session_id",), "doc-synth-0001"),
    "institutional_id_inside_fact": lambda r: r["fact"].update(value="doc-synth-handbook"),
    "persistent_lifecycle": _set(("lifecycle",), "persistent"),
    "register_lifecycle": _set(("lifecycle",), "register"),
    "unknown_origin": _set(("origin",), "official_record"),
    "verified_confirmation": _set(("confirmation_state",), "verified"),
    "confirmed_without_evidence": _set(("confirmation_state",), "user_confirmed"),
    "confirmed_by_office": lambda r: (
        r["evidence"].append(ev("ev-s1", "user_confirmation", "issuing_office")),
        r.update(confirmation_state="user_confirmed", confirmation_evidence_ref="ev-s1")),
    "confirmed_by_audit": lambda r: (
        r["evidence"].append(ev("ev-s1", "extraction_audit", "system")),
        r.update(confirmation_state="user_confirmed", confirmation_evidence_ref="ev-s1")),
    "approval_id_key": _set(("approval_id",), "auth-synth-0001"),
    "verified_key": _set(("verified",), True),
    "ledger_key": _set(("ledger_entry_id",), "entry-1"),
    "missing_session": _del("session_id"),
}


@pytest.mark.parametrize("name", SESSION_BAD)
def test_bad_session_fact_is_rejected(name):
    assert session_fact_errors(mutated(session_fact(), SESSION_BAD[name]), vocabulary())


def test_student_confirmation_stays_session_local():
    voc = vocabulary()
    fact = mutated(session_fact(), lambda r: (
        r["evidence"].append(ev("ev-s1", "user_confirmation", "user")),
        r.update(confirmation_state="user_confirmed", confirmation_evidence_ref="ev-s1")))
    assert session_fact_errors(fact, voc) == []
    assert fact["lifecycle"] == "session_only" and fact["namespace"] == "private_session"
    # no transition that a user-recorded evidence can authorize touches any institutional field
    for t in voc["transitions"]:
        if "user" in t["recorded_by"]:
            assert t["field"] == "session_confirmation_state"


def test_private_fact_id_in_an_institutional_register_record_is_rejected():
    voc = vocabulary()
    for fn in (_set(("document_id",), "fact-synth-0001"),
               lambda r: r["acquisition_locators"].append("fact-synth-0001"),
               lambda r: r["issuer"].update(value="sess-synth-0001", state="observed", evidence_ref="ev-b3", basis="printed_text")):
        assert register_errors(mutated(register()[1], fn), voc)


# ---------------------------------- decisions ------------------------------------------------
DECISION = {d["outcome"]: d for d in decisions()}
DECISION_BAD = {
    "unknown_outcome": ("eligible", _set(("outcome",), "approved")),
    "extra_approval_key": ("eligible", _set(("enrollment_approved",), True)),
    "eligible_with_missing_fact": ("eligible", lambda r: r["missing_facts"].append("x")),
    "eligible_with_unknown_condition": ("eligible", lambda r: r["unknown_conditions"].append("x")),
    "eligible_with_violation": ("eligible", lambda r: r["violated_conditions"].append("x")),
    "eligible_without_evidence": ("eligible", _set(("evidence_refs",), [])),
    "eligible_without_satisfied": ("eligible", _set(("satisfied_conditions",), [])),
    "eligible_blank_prerequisites": ("eligible", _set(("prerequisite_rule_state",), "blank_unreviewed")),
    "eligible_unreadable_prerequisites": ("eligible", _set(("prerequisite_rule_state",), "unreadable")),
    "eligible_partial_coverage": ("eligible", _set(("rule_coverage",), "partial")),
    "eligible_with_conflict": ("eligible", lambda r: r["unresolved_conflicts"].append("conflict-synth-0001")),
    "eligible_with_error_code": ("eligible", _set(("error_code",), "x")),
    "eligible_unsupported_predicate": ("eligible", _set(("predicate_supported",), False)),
    "ineligible_without_violation": ("ineligible", _set(("violated_conditions",), [])),
    "ineligible_without_evidence": ("ineligible", _set(("evidence_refs",), [])),
    "ineligible_with_conflict": ("ineligible", lambda r: r["unresolved_conflicts"].append("conflict-synth-0001")),
    "ineligible_absent_coverage": ("ineligible", _set(("rule_coverage",), "absent")),
    "unknown_with_nothing_missing": ("unknown", lambda r: (r.update(rule_coverage="verified"), r["missing_facts"].clear())),
    "unknown_with_violation": ("unknown", lambda r: r["violated_conditions"].append("x")),
    "unsupported_but_supported": ("unsupported", _set(("predicate_supported",), True)),
    "unsupported_with_evidence": ("unsupported", lambda r: r["evidence_refs"].append("x")),
    "unsupported_with_satisfied": ("unsupported", lambda r: r["satisfied_conditions"].append("x")),
    "error_without_code": ("error", _set(("error_code",), None)),
    "error_with_satisfied": ("error", lambda r: r["satisfied_conditions"].append("x")),
    "error_with_violation": ("error", lambda r: r["violated_conditions"].append("x")),
    "error_with_evidence": ("error", lambda r: r["evidence_refs"].append("x")),
    "unknown_with_error_code": ("unknown", _set(("error_code",), "x")),
}


@pytest.mark.parametrize("name", DECISION_BAD)
def test_bad_decision_is_rejected(name):
    base, fn = DECISION_BAD[name]
    assert decision_errors(mutated(DECISION[base], fn), vocabulary())


def test_verified_zero_prerequisites_differs_from_blank():
    voc = vocabulary()
    for ok in ("stated_none", "reviewed_empty", "resolved"):
        assert decision_errors(mutated(DECISION["eligible"], _set(("prerequisite_rule_state",), ok)), voc) == []
    for bad in ("blank_unreviewed", "unreadable", "unresolved_reference", "standing_condition", "alternative_or_exception"):
        assert decision_errors(mutated(DECISION["eligible"], _set(("prerequisite_rule_state",), bad)), voc), bad
    # a blank rule cannot ground "unknown" away either: it is itself a reason for unknown
    blank_unknown = mutated(DECISION["unknown"], lambda r: (r.update(rule_coverage="verified", prerequisite_rule_state="blank_unreviewed"), r["missing_facts"].clear()))
    assert decision_errors(blank_unknown, voc) == []
