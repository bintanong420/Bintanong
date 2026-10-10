"""Pure source-bound review views. Preparation confers no execution authority."""
from __future__ import annotations

import copy
import hashlib
import json
import math
import re
from collections.abc import Mapping, Sequence
from typing import Any

from ...bintanong_contracts.base import VOCAB
from ...bintanong_contracts.governance import SourceDocumentVersion, check_register
from ...bintanong_contracts.source import SourceSpan, canonical_text, check_span_binding, is_privileged_key
from .audit import find_prerequisite_cycles
from .ledger import (course_locator, entry_problem, latest_by_field, locator_key, same_value,
                     split_applicable)
from .prerequisites import (CodeIndex, PREREQUISITE_AMBIGUITY_TYPES, PREREQUISITE_STATES,
                            classify_prerequisite_state, resolve_prerequisites)
from .prolog import pl_atom
from .text import norm_key

COMPILER_VERSION = "prospectus-rule-candidates-v1"
FIELDS = frozenset({"course_code", "course_title", "units.total", "units.lecture", "units.lab",
                    "year_level", "semester", "term_index", "prerequisites_raw", "category"})
COURSE_FIELDS = tuple(sorted(FIELDS - {"prerequisites_raw"}))


def _mapping(value: Any, name: str) -> Mapping:
    if not isinstance(value, Mapping) or any(not isinstance(k, str) for k in value):
        raise ValueError(f"{name} must be a mapping with text keys")
    return value


def _sequence(value: Any, name: str) -> Sequence:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ValueError(f"{name} must be a sequence")
    return value


def _text(value: Any, name: str, *, empty: bool = False) -> str:
    if not isinstance(value, str) or (not empty and not value.strip()):
        raise ValueError(f"{name} must be text")
    return value


def _number(value: Any, name: str, *, integer: bool = False) -> None:
    if value is None:
        return
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be a finite nonnegative number or null")
    if integer and (type(value) is not int or value < 1):
        raise ValueError(f"{name} must be a positive whole number or null")


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _claims(node: Any, source: SourceDocumentVersion, path: tuple[str, ...] = ()) -> None:
    """Allow known extractor diagnostics, never a supplied activation/promotion claim."""
    if isinstance(node, Mapping):
        for key, value in node.items():
            if not isinstance(key, str):
                raise ValueError("payload keys must be text")
            here = (*path, key)
            if here == ("prolog",):
                # Historical generated views include rule_complete; none are consumed here.
                continue
            if here == ("source_verification",):
                if value != source.verification_state.state:
                    raise ValueError("payload verification exceeds the source register")
            elif here == ("content_review",):
                if value != source.content_review_state.state:
                    raise ValueError("payload review differs from the source register")
            elif key in ("activation_allowed", "eligibility_executable", "executable", "rule_complete"):
                if value not in (False, None) or type(value) not in (bool, type(None)):
                    raise ValueError("payload claims executable rules")
            elif is_privileged_key(key) and here not in {
                ("audit", "status"), ("audit", "promotion_status"), ("quality_report", "status"),
            }:
                raise ValueError(f"untrusted privileged claim at {'/'.join(here)}")
            _claims(value, source, here)
    elif isinstance(node, (list, tuple)):
        for value in node:
            _claims(value, source, path)


def _field(course: Mapping, name: str) -> Any:
    return course["units"].get(name[6:]) if name.startswith("units.") else course.get(name)


def _supported(value: Any, spans: Sequence[dict]) -> bool:
    if value is None or not spans:
        return False
    printed = canonical_text(" ".join(s["text"] for s in spans))
    if type(value) in (int, float):
        # No numeric coercion/default: the complete field must print this number.
        return bool(re.fullmatch(r"\d+(?:\.\d+)?", printed)) and float(printed) == value
    return canonical_text(value) == printed


def _review_decisions(evidence: Mapping | None, source: SourceDocumentVersion) -> dict:
    if evidence is None:
        return {}
    evidence = _mapping(evidence, "review_evidence")
    if set(evidence) != {"version_id", "entries"}:
        raise ValueError("review_evidence needs version_id and existing ledger entries only")
    _text(evidence["version_id"], "review version")
    entries = _sequence(evidence["entries"], "review entries")
    valid = []
    for entry in entries:
        _mapping(entry, "review entry")
        if entry_problem(entry) is None:
            valid.append(copy.deepcopy(dict(entry)))
    if evidence["version_id"] != source.version_id:
        return {}
    applicable, _ = split_applicable(valid, source.byte_sha256)
    return latest_by_field(applicable)


def build_rule_candidates(
    payload: Mapping[str, Any], source: SourceDocumentVersion,
    field_spans: Mapping[str, Mapping[str, Sequence[SourceSpan | Mapping[str, Any]]]], *,
    review_evidence: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate globally, then return deterministic inactive records and explicit blockers."""
    source = SourceDocumentVersion.parse(source.model_dump(mode="json")
                                          if isinstance(source, SourceDocumentVersion) else source)
    check_register([source])
    if source.acquisition_state.state == "mismatch":
        raise ValueError("source acquisition mismatch")
    payload = _mapping(payload, "payload")
    _claims(payload, source)
    identity = _mapping(payload.get("run_identity"), "run_identity")
    if identity.get("pdf_sha256") != source.byte_sha256:
        raise ValueError("payload digest differs from registered source")
    for name in ("document_id", "edition_id", "version_id", "namespace"):
        if name in payload and payload[name] != getattr(source, name):
            raise ValueError(f"payload {name} differs from registered source")
    courses = copy.deepcopy(list(_sequence(payload.get("courses"), "courses")))
    by_code = {}
    normalized = set()
    for course in courses:
        _mapping(course, "course")
        code = _text(course.get("course_code"), "course_code")
        if code != code.strip() or not norm_key(code) or norm_key(code) in normalized:
            raise ValueError("duplicate or malformed course code")
        normalized.add(norm_key(code))
        by_code[code] = course
        for name in ("course_title", "year_level", "semester", "category"):
            if course.get(name) is not None:
                _text(course[name], name, empty=True)
        _mapping(course.get("units"), "units")
        for name in ("total", "lecture", "lab"):
            _number(course["units"].get(name), f"units.{name}")
        _number(course.get("term_index"), "term_index", integer=True)
        _text(course.get("prerequisites_raw"), "prerequisites_raw", empty=True)
        for name in ("prerequisites", "prerequisites_unresolved", "standing_requirements"):
            values = _sequence(course.get(name), name)
            for value in values:
                _text(value, name)
            if len(set(values)) != len(values):
                raise ValueError(f"duplicate {name}")
        if course.get("prerequisite_state") not in PREREQUISITE_STATES:
            raise ValueError("missing or invalid prerequisite state")
        if any(norm_key(p) == norm_key(code) for p in course["prerequisites"]):
            raise ValueError("self prerequisite")
        _mapping(course.get("provenance", {}), "course provenance")
        _mapping(course.get("_source", {}), "course source")

    supports = {}
    for code, fields in _mapping(field_spans, "field_spans").items():
        if code not in by_code:
            raise ValueError("field evidence names an unknown course")
        supports[code] = {}
        for name, spans in _mapping(fields, "course field evidence").items():
            if name not in FIELDS:
                raise ValueError(f"unsupported evidence field {name}")
            parsed = []
            for item in _sequence(spans, "field spans"):
                support = SourceSpan.parse(item.model_dump(mode="json") if isinstance(item, SourceSpan) else item)
                if not support.is_complete or support.version_id != source.version_id:
                    raise ValueError("field span needs complete text/page and exact source version")
                check_span_binding(support, source)
                data = support.model_dump(mode="json")
                for ids in ("cell_ids", "item_ids"):
                    data["locator"][ids].sort()
                parsed.append(data)
            if len({_canonical(s) for s in parsed}) != len(parsed):
                raise ValueError("duplicate field span")
            supports[code][name] = parsed

    audit = _mapping(payload.get("audit", {}), "audit")
    anomalies = _sequence(audit.get("structural_anomalies", []), "structural anomalies")
    ambiguous = set()
    for anomaly in anomalies:
        _mapping(anomaly, "anomaly")
        if anomaly.get("type") in PREREQUISITE_AMBIGUITY_TYPES:
            ambiguous.update(_sequence(anomaly.get("source_cell_ids", []), "ambiguous cells"))
    decisions = _review_decisions(review_evidence, source)
    index = CodeIndex(sorted(by_code))
    for course in courses:
        resolution = resolve_prerequisites(course["prerequisites_raw"], index)
        if any(norm_key(p) == norm_key(course["course_code"]) for p in resolution.resolved):
            raise ValueError("printed self prerequisite")
        if (course["prerequisites"] != resolution.resolved
                or course["prerequisites_unresolved"] != resolution.unresolved
                or course["standing_requirements"] != resolution.standing_rules):
            raise ValueError("prerequisite references differ from recomputed source wording")
        recomputed = classify_prerequisite_state(course, frozenset(ambiguous))
        if course["prerequisite_state"] not in (recomputed, "reviewed_empty"):
            raise ValueError("prerequisite state differs from recomputed classification")
        if course["prerequisite_state"] == "reviewed_empty" and recomputed != "blank_unreviewed":
            raise ValueError("reviewed-empty claim on nonblank or ambiguous source")
        course["prerequisite_state"] = recomputed
    cycle_codes = {code for cycle in find_prerequisite_cycles(sorted(courses, key=lambda c: c["course_code"]))
                   for code in cycle}
    scope = {name: getattr(source, name).model_dump(mode="json") for name in VOCAB["scope_fields"]}
    source_identity = {name: getattr(source, name) for name in ("document_id", "edition_id", "version_id", "byte_sha256")}
    records = []

    def add(kind, code, value, raw, spans, state, blockers, refs=(), view=None):
        row = {"kind": kind, "course_code": code, "value": copy.deepcopy(value),
               "prerequisite_state": state, "raw_text": copy.deepcopy(raw), "spans": copy.deepcopy(spans),
               "scope": copy.deepcopy(scope), "review_evidence_refs": list(refs),
               "blockers": sorted(set(blockers)), "activation_allowed": False, "approval_id": None}
        row["id"] = _digest({"compiler_version": COMPILER_VERSION, "source": source_identity, **row})
        if view is not None and not blockers:
            row["review_view"] = view
        records.append(row)

    for course in sorted(courses, key=lambda c: c["course_code"]):
        code = course["course_code"]
        support = supports.get(code, {})
        blockers = [f"missing_or_unmatched_field_evidence:{f}" for f in COURSE_FIELDS
                    if not _supported(_field(course, f), support.get(f, []))]
        value = {name: copy.deepcopy(course.get(name)) for name in
                 ("course_code", "course_title", "units", "year_level", "semester", "term_index", "category")}
        course_view = None
        if not blockers:
            units = course["units"]
            clause = "course({}, {}, {}, {}, {}, {}, {}, {}).".format(
                pl_atom(code), pl_atom(course["course_title"]), units["total"], units["lecture"], units["lab"],
                pl_atom(course["year_level"]), pl_atom(course["semester"]), course["term_index"])
            course_view = {"clause": clause, "relation": value}
        add("course", code, value, {f: [s["text"] for s in support.get(f, [])] for f in COURSE_FIELDS},
            [s for f in COURSE_FIELDS for s in support.get(f, [])], course["prerequisite_state"], blockers,
            view=course_view)

        raw, state = course["prerequisites_raw"], course["prerequisite_state"]
        refs = []
        accepted = decisions.get((locator_key(course_locator(course)), "prerequisites_raw"))
        if (state == "blank_unreviewed" and accepted and accepted["disposition"] == "accepted"
                and same_value(accepted["old_value"], raw) and accepted["locator"] == course_locator(course)
                and sum(course_locator(c) == course_locator(course) for c in courses) == 1):
            state = "reviewed_empty"
            refs = [accepted["entry_id"]]
        blocked = [] if state in ("resolved", "stated_none", "reviewed_empty") else [state]
        if state != "reviewed_empty" and not _supported(raw, support.get("prerequisites_raw", [])):
            blocked.append("missing_or_unmatched_field_evidence:prerequisites_raw")
        for referenced in [code, *course["prerequisites"]]:
            if not _supported(referenced, supports.get(referenced, {}).get("course_code", [])):
                blocked.append("missing_course_identity_evidence")
        if code in cycle_codes:
            blocked.append("prerequisite_cycle")
        clauses = [f"prerequisite({pl_atom(code)}, {pl_atom(p)})." for p in course["prerequisites"]]
        add("prerequisites", code, {"all_of": course["prerequisites"],
            "unresolved": course["prerequisites_unresolved"], "standing": course["standing_requirements"]},
            raw, support.get("prerequisites_raw", []), state, blocked, refs,
            {"clauses": clauses, "relations": [{"course": code, "requires": p} for p in course["prerequisites"]]})

    metadata = _mapping(payload.get("metadata", {}), "metadata")
    program = {k: copy.deepcopy(v) for k, v in metadata.items()
               if k not in {"source_file", "generated_at", "extracted_at", "timestamp", "source_path"}}
    if program:
        add("program", None, program, program, [], None, ["unsupported_field_evidence"])
    for key, kind in (("elective_tracks", "elective_track"), ("term_units", "term_units")):
        for item in _sequence(payload.get(key, []), key):
            _mapping(item, kind)
            add(kind, None, item, item, [], None, ["unsupported_field_evidence"])
    records.sort(key=lambda r: (r["kind"], r["course_code"] or "", r["id"]))
    result = {"format_version": "bintanong-rule-candidates-v1", "compiler_version": COMPILER_VERSION,
              "source": {**source_identity, "namespace": source.namespace,
                         **{name: getattr(source, name).model_dump(mode="json") for name in
                            ("acquisition_state", "verification_state", "approval_state", "content_review_state")}},
              "records": records,
              "blockers": [{"record_id": r["id"], "reasons": r["blockers"]} for r in records if r["blockers"]]}
    result["content_digest"] = _digest(result)
    return result
