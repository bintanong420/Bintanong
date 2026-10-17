"""Prepare separate reviewed readings; never create chunks or grant source approval.

Callers normalize recorded field decisions and check their scope against the owner
event. Hashes below bind the exact event/source bytes, not the truth or authority
of a review. The raw readers and governed canonical bundle loader stay separate.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any


EXCLUDED = frozenset({"medicine", "law", "graduate", "laboratory_school", "faculty", "staff"})
DECISIONS = ("accepted", "corrected", "unresolved", "pending")


def _text(value: Any, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"missing {label}")


def _sha(value: Any) -> None:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ValueError("invalid SHA256 digest")


def _locator(value: Any) -> None:
    if not isinstance(value, dict):
        raise ValueError("missing field locator")
    pages = value.get("physical_pages")
    if (not isinstance(pages, list) or not pages
            or any(type(p) is not int or p < 1 for p in pages)
            or len(set(pages)) != len(pages)):
        raise ValueError("invalid physical pages in locator")
    _text(value.get("field"), "locator field")


def _checked_bytes(artifacts: Mapping[str, bytes]) -> None:
    for sha, data in artifacts.items():
        _sha(sha)
        if not isinstance(data, bytes) or hashlib.sha256(data).hexdigest() != sha:
            raise ValueError("artifact digest mismatch")


def _event_sources(event: dict[str, Any]) -> set[str]:
    if "source_sha256" in event:
        _sha(event["source_sha256"])
        return {event["source_sha256"]}
    hashes = event.get("source_hashes")
    if not isinstance(hashes, dict) or not hashes:
        raise ValueError("review event source hashes absent")
    for sha in hashes.values():
        _sha(sha)
    return set(hashes.values())


def _event(data: bytes) -> dict[str, Any]:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate review event key")
            result[key] = value
        return result

    def nonfinite(value):
        raise ValueError("non-finite review event value")

    try:
        value = json.loads(data, object_pairs_hook=unique, parse_constant=nonfinite)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid review event JSON") from exc
    if not isinstance(value, dict):
        raise ValueError("review event must be an object")
    try:
        json.dumps(value, allow_nan=False)
    except ValueError as exc:
        raise ValueError("non-finite review event value") from exc
    _event_sources(value)
    if "owner_statement" in value:
        _text(value["owner_statement"], "review source/event owner statement")
    else:
        excerpts = value.get("owner_statement_excerpts")
        if not isinstance(excerpts, list) or not excerpts:
            raise ValueError("missing review source/event owner statement")
        for excerpt in excerpts:
            _text(excerpt, "owner statement excerpt")
    return value


def build_reviewed_policy_bundle(
    readings: Sequence[dict[str, Any]], *, sources: Mapping[str, bytes],
    review_events: Mapping[str, bytes],
) -> dict[str, Any]:
    """Validate explicit readings and partition preparation scope without promotion.

    No file writes, raw corrections, implicit field approval or audience guessing.
    Structured field values and original evidence are copied without flattening.
    Even explicitly selected undergraduate readings remain ineligible for release.
    """
    _checked_bytes(sources)
    _checked_bytes(review_events)
    events = {sha: _event(data) for sha, data in review_events.items()}
    selection = {"undergraduate": [], "unresolved": [], "excluded": []}
    counts: Counter[str] = Counter()
    seen: set[str] = set()
    rows = copy.deepcopy(list(readings))
    # Enforce a JSON artifact, including structured values and retained raw evidence.
    try:
        json.dumps(rows, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ValueError("readings must contain finite JSON values") from exc
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("reading must be an object")
        identity = row.get("reading_id")
        _text(identity, "reading identity")
        if identity in seen:
            raise ValueError("duplicate reading identity")
        seen.add(identity)
        sha = row.get("source_sha256")
        _sha(sha)
        if sha not in sources:
            raise ValueError("reading source bytes absent")
        _text(row.get("version_id"), "source version identity")
        audience, applicability = row.get("intended_audience"), row.get("applicability")
        if audience not in EXCLUDED | {"undergraduate", "unknown", "mixed"}:
            raise ValueError("invalid intended audience")
        if applicability not in {"unknown", "mixed", "undergraduate", "excluded"}:
            raise ValueError("invalid applicability")
        if applicability in {"undergraduate", "excluded"}:
            _text(row.get("applicability_evidence_ref"), "applicability evidence")
        group = ("excluded" if audience in EXCLUDED or applicability == "excluded" else
                 "undergraduate" if audience == "undergraduate" and applicability == "undergraduate"
                 else "unresolved")
        selection[group].append(identity)
        fields = row.get("fields")
        if not isinstance(fields, list) or not fields:
            raise ValueError("reading fields absent")
        names: set[str] = set()
        for field in fields:
            if not isinstance(field, dict):
                raise ValueError("field must be an object")
            name = field.get("name")
            _text(name, "field name")
            if name in names:
                raise ValueError("duplicate field name")
            names.add(name)
            if "original_value" not in field or "reviewed_value" not in field:
                raise ValueError("original and reviewed values required")
            _locator(field.get("locator"))
            blank = field.get("source_blank")
            if type(blank) is not bool or (blank and field["reviewed_value"] != ""):
                raise ValueError("literal source blank must stay an empty string")
            decision, event_ref = field.get("decision"), field.get("review_event_sha256")
            if decision not in DECISIONS:
                raise ValueError("invalid transcription decision")
            if decision != "pending" or event_ref is not None:
                if event_ref not in events or sha not in _event_sources(events[event_ref]):
                    raise ValueError("field review event missing or bound to another source")
            counts[decision] += 1
        gaps = row.get("gaps")
        if not isinstance(gaps, list):
            raise ValueError("gap list required")
        for gap in gaps:
            if not isinstance(gap, dict):
                raise ValueError("gap must be an object")
            _text(gap.get("gap_id"), "gap identity")
            _text(gap.get("issue"), "gap issue")
            affected = gap.get("field_names")
            claims = gap.get("affected_claims")
            if (not isinstance(affected, list) or not affected
                    or any(name not in names for name in affected)
                    or not isinstance(claims, list) or not claims
                    or any(not isinstance(c, str) or not c.strip() for c in claims)
                    or "visible_text" not in gap):
                raise ValueError("gap must bind existing fields, visible text and affected claims")
            _locator(gap.get("locator"))
        evidence = row.get("preserved_evidence")
        if not isinstance(evidence, list) or not evidence:
            raise ValueError("preserved raw/review evidence required")
        for item in evidence:
            if not isinstance(item, dict):
                raise ValueError("preserved evidence must be an object")
            _text(item.get("artifact"), "preserved artifact reference")
            _sha(item.get("sha256"))
    return {"schema_version": "bintanong-reviewed-policy-preparation-v1",
            "candidate_only": True, "activation_eligible": False,
            "source_governance_changed": False,
            "review_events": events, "readings": rows, "selection": selection,
            "coverage": {"reading_count": len(rows),
                "field_decisions": {d: counts[d] for d in DECISIONS},
                "selection_counts": {k: len(v) for k, v in selection.items()},
                "scope": "explicitly supplied readings only; not a whole-corpus audit"}}
