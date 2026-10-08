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
import unicodedata
from datetime import datetime
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


def _row_accepts(row, ev):
    return (ev["kind"] == row["evidence_kind"] and ev["recorded_by"] in row["recorded_by"]
            and bool(ev.get("authorization_ref")) == bool(row.get("needs_authorization_ref")))


def evidence_authorizes(voc, field, to_state, ev, frm=None):
    """True if `ev` can authorize entering `to_state` of `field` under some row of the table."""
    return any(_row_accepts(row, ev) for row in transition_rows(voc, field, to_state, frm))


TIMESTAMP_YEARS = (2000, 2100)  # default, owner-reviewable; the package uses the same bound


def _ts(ev):
    try:
        moment = datetime.fromisoformat(ev["recorded_at"])
    except ValueError:
        return None
    if moment.tzinfo is None or not TIMESTAMP_YEARS[0] <= moment.year <= TIMESTAMP_YEARS[1]:
        return None
    return moment


def _date_span(text):
    """Earliest and latest day a possibly partial ISO date can mean; None for any other format."""
    m = re.fullmatch(r"([0-9]{4})(?:-([0-9]{2})(?:-([0-9]{2}))?)?", text or "")
    if not m:
        return None
    import calendar
    from datetime import date
    year, month, day = int(m.group(1)), m.group(2), m.group(3)
    try:
        return (date(year, int(month or 1), int(day or 1)),
                date(year, int(month or 12), int(day) if day else calendar.monthrange(year, int(month or 12))[1]))
    except ValueError:
        return None


def entered_in_order(voc, field, state, evs, i):
    """The `from` column on a record: evs[i] enters `state` under a row whose `from` is the initial state
    or a state that EARLIER evidence of the same record (earlier in the list and not later in time) entered
    in turn. Evidence is not bound to a field, so this proves the order of the kinds, not who wrote what."""
    for row in transition_rows(voc, field, state):
        if not _row_accepts(row, evs[i]):
            continue
        if row["from"] == voc["initial_states"][field]:
            return True
        now = _ts(evs[i])
        for j in range(i):
            before = _ts(evs[j])
            if now and before and before <= now and entered_in_order(voc, field, row["from"], evs, j):
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


_DASHES = dict.fromkeys(map(ord, "\u2010\u2011\u2012\u2013\u2014\u2015\u2212\ufe58\ufe63\uff0d"), "-")


def folded(s):
    """NFKC, dash variants to '-', casefold: what a person would read as the same id. No strip is needed,
    because tokens are searched anywhere in the string, so surrounding whitespace never hides one."""
    return unicodedata.normalize("NFKC", s).translate(_DASHES).casefold()


def id_tokens(text, prefixes):
    """Id-like tokens starting with one of `prefixes` anywhere in `text`. A token is the prefix plus one or
    more hyphen-joined segments that either has a second segment or a digit, so ordinary prose such as
    'fact-checking' or 'edition-specific' is not an id. It must not continue a longer word ('xfact-1')."""
    pattern = r"(?<![a-z0-9])(" + "|".join(re.escape(p) for p in prefixes) + r")([a-z0-9]+(?:-[a-z0-9]+)*)"
    return [m.group(0) for m in re.finditer(pattern, folded(text)) if "-" in m.group(2) or re.search(r"\d", m.group(2))]


def namespace_errors(rec, voc):
    ns = rec.get("namespace")
    if ns not in voc["namespaces"]:
        return [f"unknown namespace {ns!r}"]
    foreign = [p for other, spec in voc["namespaces"].items() if other != ns for p in spec["id_prefixes"]]
    return [f"id {tok!r} in {s!r} belongs to another namespace than {ns}"
            for s in _strings(rec) for tok in id_tokens(s, foreign)]

# --------------------------------------------------------------------------------------------
# Register record and set
# --------------------------------------------------------------------------------------------
STATE_FIELDS = ("acquisition_state", "verification_state", "approval_state", "content_review_state")
OBSERVED = ("observed", "verified")


def evidence_errors(voc, evidence):
    """Per-record evidence rules: unique ids, real timestamps, authorization_ref only where a row needs one."""
    errs, seen = [], set()
    for ev_ in evidence:
        if ev_["evidence_id"] in seen:
            errs.append(f"duplicate evidence id {ev_['evidence_id']}")
        seen.add(ev_["evidence_id"])
        if _ts(ev_) is None:
            errs.append(f"evidence {ev_['evidence_id']}: {ev_['recorded_at']!r} is not a real timestamp")
        needs = any(t["evidence_kind"] == ev_["kind"] and t.get("needs_authorization_ref") for t in voc["transitions"])
        if needs != bool(ev_.get("authorization_ref")):
            errs.append(f"evidence {ev_['evidence_id']}: authorization_ref {'required' if needs else 'not allowed'}")
    return errs


def _check_state(errs, voc, evidence, label, vocab_field, state, ref):
    if state == voc["initial_states"][vocab_field]:
        if ref is not None:
            errs.append(f"{label}: initial state {state} must not cite evidence")
        return
    if ref is None:
        errs.append(f"{label}: {state} without an evidence reference")
        return
    position = next((i for i, e in enumerate(evidence) if e["evidence_id"] == ref), None)
    if position is None:
        errs.append(f"{label}: evidence {ref!r} not in the record")
        return
    ev_ = evidence[position]
    if not evidence_authorizes(voc, vocab_field, state, ev_):
        errs.append(f"{label}: evidence {ref!r} ({ev_['kind']} by {ev_['recorded_by']}) cannot authorize {state}")
    elif not entered_in_order(voc, vocab_field, state, evidence, position):
        errs.append(f"{label}: {state} has no earlier evidence that entered the state it comes from")


def register_errors(rec, voc):
    errs = schema_errors(rec, schema("source-register-v1"))
    if errs:
        return errs
    errs += namespace_errors(rec, voc)
    evs = rec["evidence"]
    errs += evidence_errors(voc, evs)
    by_id = {e["evidence_id"]: e for e in evs}
    for name in STATE_FIELDS:
        _check_state(errs, voc, evs, name, name, rec[name]["state"], rec[name]["evidence_ref"])
    for name in voc["scope_fields"] + ["supersession"]:
        f = rec[name]
        _check_state(errs, voc, evs, name, "scope_field", f["state"], f["evidence_ref"])
        if name != "supersession":
            if f["state"] in ("pending", "not_stated") and (f["value"] is not None or f["basis"] is not None):
                errs.append(f"{name}: {f['state']} must carry no value and no basis (nothing is inferred)")
            if f["state"] in OBSERVED and (f["value"] is None or f["basis"] is None):
                errs.append(f"{name}: {f['state']} needs a value and an allowed basis")
            continue
        if f["state"] in ("pending", "not_stated") and f["basis"] is not None:
            errs.append(f"supersession: {f['state']} must carry no value and no basis (nothing is inferred)")
        if f["state"] in OBSERVED and f["basis"] is None:
            errs.append(f"supersession: {f['state']} needs a value and an allowed basis")
        if f["relation"] == "none":
            if f["target_version_id"] is not None:
                errs.append("supersession: relation none must not name a target")
            if f["state"] in OBSERVED:
                errs.append("supersession: relation none cannot be observed or verified")
        else:
            if f["target_version_id"] is None or f["state"] not in OBSERVED:
                errs.append("supersession: a relation needs a target and an observed or verified state")
            if f["target_version_id"] == rec["version_id"]:
                errs.append("supersession: a version cannot supersede itself")
    if rec["verification_state"]["state"] in ("observed", "verified") and \
            rec["acquisition_state"]["state"] not in ("observed", "verified"):
        errs.append("verification recorded against bytes that are not acquired and matching")
    frm_, to_ = rec["effective_from"], rec["effective_to"]
    if frm_["state"] in OBSERVED and to_["state"] in OBSERVED:
        a, b = _date_span(frm_["value"]), _date_span(to_["value"])
        if a and b and b[1] < a[0]:
            errs.append("effective_to is before effective_from")
    appr, aid = rec["approval_state"], rec["approval_id"]
    if appr["state"] in ("approved", "revoked"):
        ev_ = by_id.get(appr["evidence_ref"])
        if not aid or ev_ is None or ev_.get("authorization_ref") != aid:
            errs.append("approval_id must equal the authorization_ref of the cited authorized evidence")
    elif aid is not None:
        errs.append("approval_id supplied without authorized approval evidence")
    if appr["state"] == "revoked" and not any(
            e["kind"] == "issuing_office_authorization" and e.get("authorization_ref") == aid for e in evs):
        errs.append("revocation must cite the authorization_ref of the approval it revokes")
    if appr["state"] == "approved":
        if rec["acquisition_state"]["state"] != "verified" or rec["verification_state"]["state"] != "verified":
            errs.append("approval needs verified acquisition and verified scope")
        if rec["issuer"]["state"] != "verified" or any(
                rec[f]["state"] not in ("verified", "not_stated") for f in voc["scope_fields"]):
            errs.append("approval needs issuer and scope/effectivity fields verified or explicitly not stated")
        if rec["document_category"] in voc["proposal_categories"]:
            errs.append("a proposal candidate cannot be approved as a source")
        granted = _ts(by_id[appr["evidence_ref"]]) if appr["evidence_ref"] in by_id else None
        for name in ("acquisition_state", "verification_state"):
            basis = by_id.get(rec[name]["evidence_ref"])
            basis_at = _ts(basis) if basis else None
            if granted and basis_at and granted < basis_at:
                errs.append(f"approval: the authorization is dated before the {name} evidence it relies on")
    return errs


def _supersession_cycle(edges):
    graph = {}
    for newer, older in edges:
        graph.setdefault(newer, set()).add(older)
    done, active = set(), []

    def visit(node):
        if node in active:
            return active[active.index(node):] + [node]
        if node in done:
            return None
        active.append(node)
        for nxt in sorted(graph.get(node, ())):
            found = visit(nxt)
            if found:
                return found
        active.pop()
        done.add(node)
        return None
    for start in sorted(graph):
        found = visit(start)
        if found:
            return found
    return None


def register_set_errors(recs, voc):
    if not recs:
        return ["empty register: nothing was recorded, so nothing can be checked"]
    errs = []
    for r in recs:
        errs += [f"{r.get('version_id')}: {e}" for e in register_errors(r, voc)]
    ids = [r["version_id"] for r in recs]
    errs += [f"duplicate version_id {v}" for v in set(ids) if ids.count(v) > 1]
    by_hash, by_edition, by_ref = {}, {}, {}
    for r in recs:
        by_hash.setdefault(r["byte_sha256"], []).append(r["version_id"])
        by_edition.setdefault(r["edition_id"], set()).add(r["byte_sha256"])
        for e in r["evidence"]:
            if e.get("authorization_ref"):
                by_ref.setdefault(e["authorization_ref"], set()).add(r["version_id"])
    errs += [f"same bytes recorded as separate versions {v}; merge locators" for v in by_hash.values() if len(v) > 1]
    errs += [f"edition {e} spans different bytes (same filename is not same edition)"
             for e, h in by_edition.items() if len(h) > 1]
    errs += [f"authorization ref {ref} is shared by versions {sorted(v)}; one authorization names one version"
             for ref, v in by_ref.items() if len(v) > 1]
    by_version, edges = {r["version_id"]: r for r in recs}, set()
    for r in recs:
        s, tgt = r["supersession"], r["supersession"]["target_version_id"]
        if tgt is None:
            continue
        if tgt not in by_version:
            errs.append(f"{r['version_id']}: supersession target {tgt} is not in the register")
            continue
        other = by_version[tgt]
        if other["document_category"] != r["document_category"]:
            errs.append(f"{r['version_id']}: supersession category mismatch, {r['document_category']} and "
                        f"{other['document_category']}")
        if other["document_id"] != r["document_id"]:
            errs.append(f"{r['version_id']}: supersession crosses different documents")
        if other["supersession"]["relation"] == "none":
            errs.append(f"{r['version_id']}: supersession target {tgt} does not record the reciprocal relation")
        edges.add((r["version_id"], tgt) if s["relation"] == "supersedes" else (tgt, r["version_id"]))
    successors = {}
    for newer, older in edges:
        successors.setdefault(older, set()).add(newer)
    errs += [f"{older} has two successors {sorted(n)}" for older, n in successors.items() if len(n) > 1]
    cycle = _supersession_cycle(edges)
    if cycle:
        errs.append("supersession cycle: " + " -> ".join(cycle))
    return errs


# --------------------------------------------------------------------------------------------
# Conflict, session fact, decision
# --------------------------------------------------------------------------------------------
def conflict_errors(rec, voc, version_ids=None):
    errs = schema_errors(rec, schema("source-conflict-v1"))
    if errs:
        return errs
    errs += namespace_errors(rec, voc)
    errs += evidence_errors(voc, rec["evidence"])
    if len({(c["version_id"], c["span_ref"]) for c in rec["claims"]}) < 2:
        errs.append("a conflict needs two distinct claims")
    state, ref, basis = rec["resolution_state"], rec["resolution_evidence_ref"], rec["resolution_basis"]
    _check_state(errs, voc, rec["evidence"], "resolution", "conflict_resolution_state", state, ref)
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
    errs += evidence_errors(voc, rec["evidence"])
    _check_state(errs, voc, rec["evidence"], "confirmation", "session_confirmation_state",
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
# Synthetic examples (all new in this branch)
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


def test_examples_validate():
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


# ============================================================================================
# Fix pass 1 (review of ec0eac7..2b6c503). These tests were written red first.
# ============================================================================================
def _all_schemas():
    return {n: schema(n) for n in ("source-register-v1", "source-conflict-v1", "session-fact-v1", "decision-v1")}


def _walk(node, path="$"):
    """Yield (path, node) for every dict inside a schema document."""
    if isinstance(node, dict):
        yield path, node
        for k, v in node.items():
            yield from _walk(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _walk(v, f"{path}[{i}]")


def _forge_ts(rec, ts):
    rec["evidence"][0]["recorded_at"] = ts


# ---------------------------------- pinned transition table ---------------------------------
# (id, field, from, to, evidence kind, recorded_by, needs authorization_ref). Changing the table
# means changing this list on purpose.
PINNED_TRANSITIONS = [
    ("F1", "scope_field", "pending", "observed", "printed_text_span", ("researcher", "reviewer"), False),
    ("F2", "scope_field", "observed", "verified", "issuing_office_confirmation", ("issuing_office",), False),
    ("F3", "scope_field", "pending", "not_stated", "reviewer_absence_check", ("reviewer",), False),
    ("A1", "acquisition_state", "pending", "observed", "byte_hash_check", ("researcher", "reviewer", "system"), False),
    ("A2", "acquisition_state", "observed", "verified", "byte_hash_check", ("reviewer", "system"), False),
    ("A3", "acquisition_state", "observed", "mismatch", "byte_hash_check", ("reviewer", "system"), False),
    ("A4", "acquisition_state", "verified", "mismatch", "byte_hash_check", ("reviewer", "system"), False),
    ("V1", "verification_state", "pending", "observed", "printed_text_span", ("researcher", "reviewer"), False),
    ("V2", "verification_state", "observed", "verified", "issuing_office_confirmation", ("issuing_office",), False),
    ("V3", "verification_state", "observed", "rejected", "issuing_office_rejection", ("issuing_office",), False),
    ("V4", "verification_state", "verified", "rejected", "issuing_office_rejection", ("issuing_office",), False),
    ("P1", "approval_state", "not_requested", "requested", "approval_request", ("researcher", "reviewer"), False),
    ("P2", "approval_state", "requested", "approved", "issuing_office_authorization", ("issuing_office",), True),
    ("P3", "approval_state", "requested", "rejected", "issuing_office_rejection", ("issuing_office",), False),
    ("P4", "approval_state", "approved", "revoked", "issuing_office_revocation", ("issuing_office",), True),
    ("C1", "content_review_state", "pending", "partially_reviewed", "content_review_record", ("reviewer",), False),
    ("C2", "content_review_state", "partially_reviewed", "reviewed", "content_review_record", ("reviewer",), False),
    ("C3", "content_review_state", "pending", "reviewed", "content_review_record", ("reviewer",), False),
    ("R1", "conflict_resolution_state", "unresolved", "referred_to_source_owner", "conflict_referral", ("researcher", "reviewer"), False),
    ("R2", "conflict_resolution_state", "unresolved", "resolved", "issuing_office_resolution", ("issuing_office",), False),
    ("R3", "conflict_resolution_state", "referred_to_source_owner", "resolved", "issuing_office_resolution", ("issuing_office",), False),
    ("S1", "session_confirmation_state", "unconfirmed", "user_confirmed", "user_confirmation", ("user",), False),
    ("S2", "session_confirmation_state", "unconfirmed", "user_rejected", "user_confirmation", ("user",), False),
]
TERMINAL = {
    "scope_field": {"verified", "not_stated"},
    "acquisition_state": {"mismatch"},
    "verification_state": {"rejected"},
    "approval_state": {"rejected", "revoked"},
    "content_review_state": {"reviewed"},
    "conflict_resolution_state": {"resolved"},
    "session_confirmation_state": {"user_confirmed", "user_rejected"},
}


def test_the_transition_table_is_pinned_row_for_row():
    rows = [(t["id"], t["field"], t["from"], t["to"], t["evidence_kind"], tuple(t["recorded_by"]),
             bool(t.get("needs_authorization_ref"))) for t in vocabulary()["transitions"]]
    assert rows == PINNED_TRANSITIONS
    assert all(set(t) <= {"id", "field", "from", "to", "evidence_kind", "recorded_by",
                          "needs_authorization_ref", "guards"} for t in vocabulary()["transitions"])


@pytest.mark.parametrize("row", PINNED_TRANSITIONS, ids=lambda r: r[0])
def test_every_row_accepts_exactly_its_roles_and_its_reference_rule(row):
    rid, field, frm, to, kind, roles, needs_ref = row
    voc = vocabulary()
    for role in voc["roles"]:
        for ref in (None, "auth-x"):
            e = ev("ev-x", kind, role, **({"authorization_ref": ref} if ref else {}))
            expected = role in roles and bool(ref) == needs_ref
            assert transition_allowed(voc, field, frm, to, e) is expected, (rid, role, ref)


def test_terminal_states_have_no_outgoing_transition_rows():
    voc = vocabulary()
    for field, states in voc["states"].items():
        outgoing = {t["from"] for t in voc["transitions"] if t["field"] == field}
        assert set(states) - outgoing == TERMINAL[field], field


# ---------------------------------- checker and schema strictness ---------------------------
def test_checker_raises_on_an_unsupported_keyword_and_on_additional_properties_true():
    with pytest.raises(AssertionError, match="unsupported schema keyword"):
        schema_errors(1, {"minimum": 5})
    with pytest.raises(AssertionError, match="unsupported schema keyword"):
        schema_errors("x", {"format": "date"})
    with pytest.raises(AssertionError):
        schema_errors({}, {"additionalProperties": True})


def test_every_schema_object_forbids_extra_keys_and_requires_every_property():
    for name, sch in _all_schemas().items():
        for path, node in _walk(sch):
            if "properties" not in node or path.endswith(".properties"):
                continue
            assert node.get("additionalProperties") is False, (name, path)
            optional = {"authorization_ref"} if path.endswith(".evidence") or ".evidence" in path else set()
            assert set(node["required"]) == set(node["properties"]) - optional, (name, path)


@pytest.mark.parametrize("name,example", [
    ("source-register-v1", lambda: register()[1]), ("source-conflict-v1", conflict),
    ("session-fact-v1", session_fact), ("decision-v1", lambda: decisions()[0])])
def test_deleting_any_top_level_key_is_rejected(name, example):
    for key in example():
        assert schema_errors(mutated(example(), _del(key)), schema(name)), (name, key)


def test_every_schema_pattern_rejects_a_trailing_newline():
    checked = 0
    for name, sch in _all_schemas().items():
        for path, node in _walk(sch):
            if isinstance(node.get("pattern"), str):
                checked += 1
                assert node["pattern"].endswith("$(?!\\n)"), (name, path, node["pattern"])
    assert checked >= 15


ID_FIELDS = [("document_id", "doc-synth-handbook"), ("version_id", "ver-synth-x"), ("edition_id", "edition-synth-x"),
             ("byte_sha256", "a" * 64)]


@pytest.mark.parametrize("field,good", ID_FIELDS)
def test_register_ids_and_hash_reject_newline_case_and_wrong_prefix(field, good):
    assert register_errors(mutated(register()[1], _set((field,), good)), vocabulary()) == [] or field != "byte_sha256"
    for bad in (good + "\n", good.upper(), " " + good, good + " ", good[:-1] + "_", "x" + good, ""):
        assert schema_errors(mutated(register()[1], _set((field,), bad)), schema("source-register-v1")), (field, bad)
    assert schema_errors(mutated(register()[1], _set(("document_id",), "ver-synth-handbook")), schema("source-register-v1"))
    assert schema_errors(mutated(register()[1], _set(("document_id",), "doc-")), schema("source-register-v1"))


def test_conflict_session_and_timestamp_patterns_reject_a_trailing_newline():
    assert schema_errors(mutated(conflict(), _set(("conflict_id",), "conflict-synth-0001\n")), schema("source-conflict-v1"))
    assert schema_errors(mutated(conflict(), lambda r: r["claims"][0].update(version_id="ver-synth-x\n")), schema("source-conflict-v1"))
    assert schema_errors(mutated(session_fact(), _set(("fact_id",), "fact-synth-0001\n")), schema("session-fact-v1"))
    assert schema_errors(mutated(session_fact(), _set(("session_id",), "sess-synth-0001\n")), schema("session-fact-v1"))
    assert schema_errors(mutated(register()[1], _set(("evidence", 0, "recorded_at"), "2026-01-01T00:00:00Z\n")),
                         schema("source-register-v1"))


@pytest.mark.parametrize("bad", ["C:\\Users\\x\\a.pdf", "C:/Users/x/a.pdf", "dir\\a.pdf", "/abs/a.pdf", "file:///a.pdf",
                                 "\\\\host\\share\\a.pdf", "a/b.pdf", "x:y.pdf", "..", ".", "a\tb.pdf", "a\nb.pdf", ""])
def test_filename_rejects_paths_urls_and_control_characters(bad):
    assert schema_errors(mutated(register()[1], _set(("filename",), bad)), schema("source-register-v1")), bad


@pytest.mark.parametrize("good", ["synthetic-handbook.pdf", "Student Handbook (2023) v2.pdf", "a.b.c.pptx"])
def test_filename_accepts_plain_names(good):
    assert schema_errors(mutated(register()[1], _set(("filename",), good)), schema("source-register-v1")) == []


@pytest.mark.parametrize("bad", ["C:\\Users\\x\\a.pdf", "C:/Users/x/a.pdf", "d:\\a", "\\\\host\\share", "/home/x/a.pdf",
                                 "/Users/x/a.pdf", "file:///a.pdf", "../a.pdf", "synthetic-locator-x/../y", "~/a.pdf",
                                 "a\\b", " leading", "", "x\ny"])
def test_acquisition_locators_reject_local_paths(bad):
    rec = mutated(register()[1], _set(("acquisition_locators",), ["synthetic-locator-alpha/2", bad]))
    assert schema_errors(rec, schema("source-register-v1")), bad


@pytest.mark.parametrize("good", ["https://example.invalid/handbook.pdf", "synthetic-locator-alpha/2", "registrar-shelf-3/box-2"])
def test_acquisition_locators_accept_urls_and_shelf_references(good):
    rec = mutated(register()[1], _set(("acquisition_locators",), [good]))
    assert schema_errors(rec, schema("source-register-v1")) == []


@pytest.mark.parametrize("stamp", ["9999-99-99T99:99:99Z", "2026-02-30T00:00:00Z", "2026-13-01T00:00:00Z",
                                   "2026-01-01T24:00:00Z", "2026-01-01T00:60:00Z", "2026-01-01T00:00:61Z",
                                   "9999-12-31T23:59:59Z", "2026-01-01T00:00:00+99:99"])
def test_impossible_timestamps_are_rejected_in_every_record_type(stamp):
    voc = vocabulary()
    assert register_errors(mutated(register()[1], lambda r: _forge_ts(r, stamp)), voc)
    c = mutated(conflict(), lambda r: r["evidence"].append(ev("ev-c9", "conflict_referral", "researcher", recorded_at=stamp)))
    assert conflict_errors(c, voc)
    s = mutated(session_fact(), lambda r: r["evidence"].append(ev("ev-s9", "user_confirmation", "user", recorded_at=stamp)))
    assert session_fact_errors(s, voc)


def test_duplicate_evidence_ids_are_rejected_in_every_record_type():
    voc = vocabulary()
    assert any("duplicate evidence id" in e for e in register_errors(
        mutated(register()[1], lambda r: r["evidence"].append(copy.deepcopy(r["evidence"][0]))), voc))
    dup = lambda r: r["evidence"].extend([ev("ev-d", "conflict_referral", "researcher"), ev("ev-d", "conflict_referral", "reviewer")])
    assert any("duplicate evidence id" in e for e in conflict_errors(mutated(conflict(), dup), voc))
    dups = lambda r: r["evidence"].extend([ev("ev-d", "user_confirmation", "user"), ev("ev-d", "user_confirmation", "user")])
    assert any("duplicate evidence id" in e for e in session_fact_errors(mutated(session_fact(), dups), voc))


def test_supersession_relation_none_must_not_name_a_target():
    rec = mutated(register()[1], lambda r: r["supersession"].update(target_version_id="ver-synth-handbook-1"))
    assert any("relation none must not name a target" in e for e in register_errors(rec, vocabulary()))


def test_blank_or_padded_authorization_ids_are_rejected():
    voc = vocabulary()
    for bad in (" ", "", "auth x", " auth-synth-0001", "auth-synth-0001 ", "auth-synth-0001\n"):
        rec = mutated(approved_record(), lambda r, b=bad: (
            r.__setitem__("approval_id", b), r["evidence"][5].update(authorization_ref=b)))
        assert register_errors(rec, voc), repr(bad)


@pytest.mark.parametrize("cap", [" enrollment_procedure_answers", "enrollment_procedure_answers ",
                                 "enrollment_procedure_answers\n", " ", ""])
def test_capability_with_whitespace_or_blank_is_rejected(cap):
    rec = mutated(conflict(), lambda r: r["affected_scope"].update(capability=cap))
    assert conflict_errors(rec, vocabulary())


def test_an_empty_register_is_rejected():
    assert any("empty register" in e for e in register_set_errors([], vocabulary()))


# ---------------------------------- namespace scan ------------------------------------------
PRIVATE_IN_INSTITUTIONAL = ["fact-0001", "sess-7", "fact-synth-0001 ", " fact-synth-0001", "FACT-synth-0001", "fact-synth-0001\n",
                            "\uff46act-synth-0001", "fact\u2011synth-0001", "fact-synth-0001/x", "sess-synth-0001#a",
                            "see fact-synth-0001.", "(sess-synth-0001)", "x/FACT\u2010SYNTH-1"]
INSTITUTIONAL_IN_SESSION = ["ver-1", "doc-synth-handbook\n", "ver-synth-0001 ", "DOC-synth-x", " edition-synth-1", "conflict-synth-0001\t",
                            "ｖer-synth-0001", "ver\u2011synth-0001", "doc-synth-handbook/x", "ver-synth-0001#a"]
LEGITIMATE_PROSE = ["Fact-checking Office of Records", "over-the-counter version-controlled copies", "edition-specific wording",
                    "conflict-resolution procedure", "Doc-ument handling", "a fact", "xfact-synth-0001", "verification", "sess"]


@pytest.mark.parametrize("value", PRIVATE_IN_INSTITUTIONAL)
def test_private_id_variants_inside_institutional_records_are_found(value):
    voc = vocabulary()
    rec = mutated(register()[1], lambda r: r["issuer"].update(value=value))
    assert any("another namespace" in e for e in register_errors(rec, voc)), repr(value)
    con = mutated(conflict(), lambda r: r["claims"][0].update(claim_text=value))
    assert any("another namespace" in e for e in conflict_errors(con, voc)), repr(value)


@pytest.mark.parametrize("value", INSTITUTIONAL_IN_SESSION)
def test_institutional_id_variants_inside_session_facts_are_found(value):
    rec = mutated(session_fact(), lambda r: r["fact"].update(value=value))
    assert any("another namespace" in e for e in session_fact_errors(rec, vocabulary())), repr(value)
    rec = mutated(session_fact(), lambda r: r["fact"].update(key=value))
    assert any("another namespace" in e for e in session_fact_errors(rec, vocabulary())), repr(value)


@pytest.mark.parametrize("value", LEGITIMATE_PROSE)
def test_the_namespace_scan_does_not_flag_ordinary_prose(value):
    voc = vocabulary()
    assert not any("another namespace" in e for e in register_errors(
        mutated(register()[1], lambda r: r["issuer"].update(value=value)), voc)), value
    assert not any("another namespace" in e for e in session_fact_errors(
        mutated(session_fact(), lambda r: r["fact"].update(value=value)), voc)), value


def test_the_namespace_scan_does_not_flag_any_existing_example():
    voc = vocabulary()
    for rec in register() + [conflict(), session_fact(), approved_record()]:
        assert namespace_errors(rec, voc) == [], rec.get("version_id") or rec.get("conflict_id") or rec.get("fact_id")


# ---------------------------------- evidence chain (the `from` column) ----------------------
def _chain_errors(rec):
    return [e for e in register_errors(rec, vocabulary()) if "earlier evidence" in e]


def test_approved_without_an_earlier_request_is_rejected():
    rec = mutated(approved_record(), lambda r: r.__setitem__(
        "evidence", [e for e in r["evidence"] if e["evidence_id"] != "ev-b5"]))
    assert _chain_errors(rec)
    assert _chain_errors(approved_record()) == []


def test_request_recorded_after_the_authorization_is_rejected():
    def reorder(r):
        evs = {e["evidence_id"]: e for e in r["evidence"]}
        r["evidence"] = [e for e in r["evidence"] if e["evidence_id"] not in ("ev-b5", "ev-b6")] + [evs["ev-b6"], evs["ev-b5"]]
    assert _chain_errors(mutated(approved_record(), reorder))


def test_authorization_dated_before_its_request_is_rejected():
    rec = mutated(approved_record(), lambda r: next(
        e for e in r["evidence"] if e["evidence_id"] == "ev-b6").update(recorded_at="2025-12-31T23:59:59+00:00"))
    assert _chain_errors(rec)
    later = mutated(approved_record(), lambda r: next(
        e for e in r["evidence"] if e["evidence_id"] == "ev-b6").update(recorded_at="2026-01-02T00:00:00+00:00"))
    assert register_errors(later, vocabulary()) == []


def _revoked(**changes):
    def fn(r):
        r["evidence"].append(ev("ev-b8", "issuing_office_revocation", "issuing_office",
                                authorization_ref=changes.get("ref", "auth-synth-0001"), recorded_at="2026-01-03T00:00:00+00:00"))
        r["approval_state"] = {"state": "revoked", "evidence_ref": "ev-b8"}
        r["approval_id"] = changes.get("ref", "auth-synth-0001")
    return mutated(approved_record(), fn)


def test_revoked_needs_the_approval_chain_and_an_authorization_ref():
    voc = vocabulary()
    assert register_errors(_revoked(), voc) == []
    no_approval = mutated(_revoked(), lambda r: r.__setitem__(
        "evidence", [e for e in r["evidence"] if e["kind"] != "issuing_office_authorization"]))
    assert _chain_errors(no_approval)
    pending_to_revoked = mutated(register()[1], lambda r: (
        r["evidence"].append(ev("ev-x", "issuing_office_revocation", "issuing_office", authorization_ref="auth-synth-0001")),
        r["approval_state"].update(state="revoked", evidence_ref="ev-x"),
        r.__setitem__("approval_id", "auth-synth-0001")))
    assert _chain_errors(pending_to_revoked)
    no_ref = mutated(_revoked(), lambda r: r["evidence"][-1].pop("authorization_ref"))
    assert register_errors(no_ref, voc)


def test_rejected_needs_an_earlier_request():
    voc = vocabulary()
    without = mutated(register()[1], lambda r: (
        r["evidence"].append(ev("ev-x", "issuing_office_rejection", "issuing_office")),
        r["approval_state"].update(state="rejected", evidence_ref="ev-x")))
    assert _chain_errors(without)
    with_request = mutated(register()[1], lambda r: (
        r["evidence"].extend([ev("ev-q", "approval_request", "researcher"), ev("ev-x", "issuing_office_rejection", "issuing_office")]),
        r["approval_state"].update(state="rejected", evidence_ref="ev-x")))
    assert register_errors(with_request, voc) == []


def test_verified_states_need_the_earlier_observed_evidence():
    voc = vocabulary()
    only_confirmation = mutated(register()[0], lambda r: (
        r["evidence"].append(ev("ev-v", "issuing_office_confirmation", "issuing_office")),
        r["verification_state"].update(state="verified", evidence_ref="ev-v")))
    assert _chain_errors(only_confirmation)
    only_system_hash = mutated(register()[0], lambda r: (
        r.__setitem__("evidence", [ev("ev-s", "byte_hash_check", "system")]),
        r["acquisition_state"].update(state="verified", evidence_ref="ev-s")))
    assert _chain_errors(only_system_hash)
    mismatch_from_nothing = mutated(register()[0], lambda r: (
        r.__setitem__("evidence", [ev("ev-s", "byte_hash_check", "system")]),
        r["acquisition_state"].update(state="mismatch", evidence_ref="ev-s")))
    assert _chain_errors(mismatch_from_nothing)
    scope_verified = mutated(register()[0], lambda r: (
        r["evidence"].append(ev("ev-o", "issuing_office_confirmation", "issuing_office")),
        r["issuer"].update(value="X", state="verified", evidence_ref="ev-o", basis="issuing_office_statement")))
    assert _chain_errors(scope_verified)
    assert [e for e in register_errors(register()[1], voc)] == []


# ---------------------------------- supersession --------------------------------------------
def _pair(newer_relation="supersedes"):
    """regs[1] supersedes regs[0] and regs[0] records the inverse, each with printed evidence."""
    regs = register()
    for r in regs[:2]:
        r["evidence"].append(ev("ev-sup", "printed_text_span", "researcher"))
    inverse = {"supersedes": "superseded_by", "superseded_by": "supersedes"}
    a, b = regs[1], regs[0]
    a["supersession"] = {"relation": newer_relation, "target_version_id": b["version_id"], "state": "observed",
                         "evidence_ref": "ev-sup", "basis": "printed_text"}
    b["supersession"] = {"relation": inverse[newer_relation], "target_version_id": a["version_id"], "state": "observed",
                         "evidence_ref": "ev-sup", "basis": "printed_text"}
    return regs


def _sup(rec, relation, target, state="observed", basis="printed_text"):
    rec["supersession"] = {"relation": relation, "target_version_id": target, "state": state,
                           "evidence_ref": "ev-sup", "basis": basis}


def test_a_reciprocal_supersession_pair_is_accepted():
    voc = vocabulary()
    assert register_set_errors(_pair(), voc) == []
    assert register_set_errors(_pair("superseded_by"), voc) == []


def _chain3():
    regs = register()
    for r in regs:
        r["evidence"].append(ev("ev-sup", "printed_text_span", "researcher"))
    return regs  # [0]=ver-synth-handbook-1, [1]=ver-synth-handbook-2, [2]=ver-synth-proposal-1


def test_non_reciprocal_supersession_is_rejected():
    regs = _pair()
    regs[0]["supersession"] = copy.deepcopy(register()[0]["supersession"])
    assert any("reciprocal" in e for e in register_set_errors(regs, vocabulary()))


def test_a_two_cycle_is_rejected():
    regs = _pair()
    _sup(regs[0], "supersedes", regs[1]["version_id"])
    errs = register_set_errors(regs, vocabulary())
    assert any("cycle" in e for e in errs)


def test_a_longer_cycle_is_rejected_and_a_chain_is_not():
    voc = vocabulary()
    regs = _chain3()
    twin = copy.deepcopy(regs[1])
    twin.update(version_id="ver-synth-handbook-3", edition_id="edition-synth-handbook-3", byte_sha256="b" * 64)
    regs.append(twin)
    h1, h2, h3 = regs[0], regs[1], regs[3]
    _sup(h3, "supersedes", h2["version_id"]); _sup(h2, "supersedes", h1["version_id"])
    h1["supersession"] = copy.deepcopy(register()[0]["supersession"])
    regs[2]["supersession"] = copy.deepcopy(register()[2]["supersession"])
    assert [e for e in register_set_errors(regs, voc) if "cycle" in e] == []  # a chain: no cycle
    _sup(h1, "supersedes", h3["version_id"])
    assert any("cycle" in e for e in register_set_errors(regs, voc))


def test_two_different_successors_of_one_version_are_rejected():
    regs = _chain3()
    twin = copy.deepcopy(regs[1])
    twin.update(version_id="ver-synth-handbook-3", edition_id="edition-synth-handbook-3", byte_sha256="b" * 64)
    regs.append(twin)
    _sup(regs[1], "supersedes", regs[0]["version_id"]); _sup(regs[3], "supersedes", regs[0]["version_id"])
    _sup(regs[0], "superseded_by", regs[1]["version_id"])
    assert any("successor" in e for e in register_set_errors(regs, vocabulary()))


def test_source_document_and_proposal_candidate_cannot_supersede_each_other():
    voc = vocabulary()
    for newer, older in ((1, 2), (2, 1)):
        regs = _chain3()
        _sup(regs[newer], "supersedes", regs[older]["version_id"])
        _sup(regs[older], "superseded_by", regs[newer]["version_id"])
        assert any("category" in e for e in register_set_errors(regs, voc)), (newer, older)


SUPERSESSION_RECORD_BAD = {
    "supersedes_but_not_stated": (lambda r: r["supersession"].update(
        relation="supersedes", target_version_id="ver-synth-handbook-1", state="not_stated", evidence_ref="ev-b7", basis=None),
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
        "needs a value and an allowed basis"),
    "pending_with_basis": (lambda r: r["supersession"].update(basis="printed_text"),
                           "pending must carry no value and no basis"),
    "not_stated_with_target": (lambda r: r["supersession"].update(
        relation="none", target_version_id="ver-synth-handbook-1", state="not_stated", evidence_ref="ev-b7"),
        "relation none must not name a target"),
}


@pytest.mark.parametrize("name", SUPERSESSION_RECORD_BAD)
def test_weak_supersession_records_are_rejected(name):
    fn, message = SUPERSESSION_RECORD_BAD[name]

    def build(r):
        r["evidence"].append(ev("ev-b7", "reviewer_absence_check", "reviewer"))
        fn(r)
    assert any(message in e for e in register_errors(mutated(register()[1], build), vocabulary())), name

def test_relation_none_with_not_stated_is_a_legitimate_reviewed_absence():
    rec = mutated(register()[1], lambda r: (
        r["evidence"].append(ev("ev-b7", "reviewer_absence_check", "reviewer")),
        r["supersession"].update(state="not_stated", evidence_ref="ev-b7")))
    assert register_errors(rec, vocabulary()) == []


# ---------------------------------- authorization references --------------------------------
def _twin_approved():
    a = approved_record()
    b = copy.deepcopy(a)
    b.update(version_id="ver-synth-handbook-3", edition_id="edition-synth-handbook-3", byte_sha256="c" * 64)
    return a, b


def test_the_same_authorization_ref_on_two_versions_is_rejected():
    voc = vocabulary()
    a, b = _twin_approved()
    assert any("authorization ref" in e for e in register_set_errors([a, b], voc))
    other = mutated(b, lambda r: (r.__setitem__("approval_id", "auth-synth-0002"),
                                  next(e for e in r["evidence"] if e["kind"] == "issuing_office_authorization").update(
                                      authorization_ref="auth-synth-0002")))
    assert not any("authorization ref" in e for e in register_set_errors([a, other], voc))


def test_a_revocation_must_cite_the_approvals_authorization_ref():
    voc = vocabulary()
    other = _revoked(ref="auth-synth-0099")
    assert any("revocation" in e for e in register_errors(other, voc))
    assert register_errors(_revoked(), voc) == []

# ---------------------------------- second round: survivors of the first mutation run ---------
def test_authorizing_and_non_authorizing_evidence_kinds_are_pinned():
    kinds = vocabulary()["evidence_kinds"]
    assert set(kinds["non_authorizing"]) == {"extraction_audit", "extractor_status_label", "filename_observation",
                                             "local_possession_note"}
    assert set(kinds["authorizing"]) == {t[4] for t in PINNED_TRANSITIONS}


def test_the_approval_guards_are_pinned():
    voc = vocabulary()
    p2 = next(t for t in voc["transitions"] if t["id"] == "P2")
    assert p2["guards"] == ["acquisition_state=verified", "verification_state=verified", "issuer=verified",
                            "scope_fields=verified_or_not_stated", "category_not_proposal"]
    assert [t["id"] for t in voc["transitions"] if "guards" in t] == ["P2"]


CONSTS = [("source-register-v1", "namespace", "private_session"),
          ("source-register-v1", "schema_version", "bintanong-source-register-v2"),
          ("source-conflict-v1", "namespace", "private_session"), ("source-conflict-v1", "schema_version", "x"),
          ("session-fact-v1", "namespace", "institutional"), ("session-fact-v1", "schema_version", "x"),
          ("session-fact-v1", "lifecycle", "persistent"), ("decision-v1", "schema_version", "x")]
EXAMPLE_OF = {"source-register-v1": lambda: register()[1], "source-conflict-v1": conflict,
              "session-fact-v1": session_fact, "decision-v1": lambda: decisions()[0]}


@pytest.mark.parametrize("name,key,bad", CONSTS)
def test_schema_constants_reject_other_values_at_schema_level(name, key, bad):
    assert schema_errors(EXAMPLE_OF[name](), schema(name)) == []
    assert schema_errors(mutated(EXAMPLE_OF[name](), _set((key,), bad)), schema(name)), (name, key)


def test_a_conflict_with_one_claim_fails_the_schema_itself():
    assert schema_errors(mutated(conflict(), lambda r: r["claims"].pop()), schema("source-conflict-v1"))


def test_timestamps_and_authorization_refs_are_pattern_checked_in_every_schema():
    cases = {"source-register-v1": lambda: register()[1], "source-conflict-v1": conflict, "session-fact-v1": session_fact}
    for name, example in cases.items():
        for bad_ts in ("yesterday", "2026-01-01", "2026-01-01 00:00:00Z"):
            rec = mutated(example(), lambda r, b=bad_ts: r["evidence"].append(
                ev("ev-z", "byte_hash_check", "system", recorded_at=b)))
            assert schema_errors(rec, schema(name)), (name, bad_ts)
        for bad_ref in (" ", "", "auth x", "auth-1\n"):
            rec = mutated(example(), lambda r, b=bad_ref: r["evidence"].append(
                ev("ev-z", "byte_hash_check", "system", authorization_ref=b)))
            assert schema_errors(rec, schema(name)), (name, bad_ref)
    for bad_id in (" ", "", "auth x", "auth-1\n", " auth-1"):
        assert schema_errors(mutated(approved_record(), _set(("approval_id",), bad_id)),
                             schema("source-register-v1")), bad_id
    assert schema_errors(approved_record(), schema("source-register-v1")) == []


def test_checker_keywords_behave_on_small_schemas():
    assert schema_errors("abc", {"pattern": "b"}) == []  # search, not match
    assert schema_errors("xyz", {"pattern": "b"})
    assert schema_errors("", {"minLength": 1}) and schema_errors("a", {"minLength": 1}) == []
    assert schema_errors([], {"minItems": 1}) and schema_errors([1], {"minItems": 1}) == []
    assert schema_errors(1, {"type": "string"}) and schema_errors(True, {"type": "integer"})
    assert schema_errors("x", {"enum": ["a"]}) and schema_errors("x", {"const": "y"})
    assert schema_errors({}, {"required": ["a"]})
    assert schema_errors({"b": 1}, {"properties": {}, "additionalProperties": False})
    assert schema_errors(1, {"$ref": "#/$defs/s", "$defs": {"s": {"type": "string"}}})


@pytest.mark.parametrize("kind,by,ref,message", [
    ("extraction_audit", "system", "auth-x", "authorization_ref not allowed"),
    ("approval_request", "researcher", "auth-x", "authorization_ref not allowed"),
    ("issuing_office_authorization", "issuing_office", None, "authorization_ref required"),
    ("issuing_office_revocation", "issuing_office", None, "authorization_ref required"),
])
def test_authorization_ref_presence_is_checked_on_unreferenced_evidence_too(kind, by, ref, message):
    rec = mutated(register()[1], lambda r: r["evidence"].append(
        ev("ev-z", kind, by, **({"authorization_ref": ref} if ref else {}))))
    assert any(message in e for e in register_errors(rec, vocabulary()))


def test_an_impossible_timestamp_in_the_chain_is_an_error_not_a_crash():
    voc = vocabulary()
    for target in ("ev-b5", "ev-b6"):
        rec = mutated(approved_record(), lambda r, t=target: next(
            e for e in r["evidence"] if e["evidence_id"] == t).update(recorded_at="9999-99-99T99:99:99Z"))
        errs = register_errors(rec, voc)
        assert any("not a real timestamp" in e for e in errs) and any("earlier evidence" in e for e in errs), target


# ---------------------------------- fix pass 2: rules the package gained, mirrored here ----------
def test_effective_to_before_effective_from_is_rejected_for_iso_dates_only():
    def dates(frm, to):
        return mutated(register()[1], lambda r: (
            r["evidence"].append(ev("ev-d", "printed_text_span", "researcher")),
            r["effective_from"].update(value=frm, state="observed", evidence_ref="ev-d", basis="printed_text"),
            r["effective_to"].update(value=to, state="observed", evidence_ref="ev-d", basis="printed_text")))
    voc = vocabulary()
    for good in (("2023-08-01", "2024-05-31"), ("2023", "2023-12"), ("soon", "later")):
        assert register_errors(dates(*good), voc) == [], good
    for reversed_ in (("2024-05-31", "2023-08-01"), ("2024", "2023-12")):
        assert any("effective_to is before" in e for e in register_errors(dates(*reversed_), voc)), reversed_


def test_supersession_across_different_documents_is_rejected():
    regs = _pair()
    regs[1]["document_id"] = "doc-synth-other"
    assert any("different documents" in e for e in register_set_errors(regs, vocabulary()))


def test_an_authorization_dated_before_the_evidence_it_relies_on_is_rejected():
    rec = mutated(approved_record(), lambda r: next(
        e for e in r["evidence"] if e["evidence_id"] == "ev-b4").update(recorded_at="2026-01-05T00:00:00+00:00"))
    assert any("dated before" in e for e in register_errors(rec, vocabulary()))


def test_a_timestamp_outside_the_plausible_years_is_not_real():
    assert _ts({"recorded_at": "9999-12-31T23:59:59Z"}) is None
    assert _ts({"recorded_at": "2026-01-01T00:00:00Z"}) is not None
