"""Append-only decision ledger (and, in the next task, the corrected candidate materialised from it).

The extraction is never edited. A human decision is one JSON line: who, when, why, which PDF
(`pdf_sha256`), which course (its source cell ids), which field, the old value and the new value
or a disposition (accepted, corrected, unresolved), and the fix proposal it came from. A corrected
candidate is rebuilt from the immutable extraction plus the applicable entries; entries recorded
against another PDF, another course or another old value are reported, never applied.

Conforms to master plan 7.1 step 7 and draft Task 5: reviewer, time, reason, PDF hash, course and
field locator, original value, correction or disposition, linked cells. A later GUI reads and
appends the same lines.
"""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .fixes import FIELD_CODE, FIELD_TERM, FIELD_TITLE, format_term

LEDGER_VERSION = "prospectus-decision-ledger-v1"
ACCEPTED, CORRECTED, UNRESOLVED = "accepted", "corrected", "unresolved"
DISPOSITIONS = (ACCEPTED, CORRECTED, UNRESOLVED)
FIELD_ROW, FIELD_UNCLAIMED = "row", "unclaimed"
COURSE_FIELDS = (FIELD_CODE, FIELD_TITLE, FIELD_TERM)


class LedgerError(ValueError):
    """The ledger file is not what an append-only ledger should be."""


def course_snapshot(course: Mapping[str, Any]) -> dict[str, str]:
    return {
        FIELD_CODE: course.get("course_code") or "",
        FIELD_TITLE: course.get("course_title") or "",
        FIELD_TERM: format_term(course.get("year_level"), course.get("semester")),
    }


def course_locator(course: Mapping[str, Any]) -> dict[str, Any]:
    provenance = course.get("provenance") or {}
    return {
        "kind": "course",
        "table_index": (course.get("_source") or {}).get("table_index"),
        "cell_ids": sorted(provenance.get("source_cell_ids") or []),
        "page": provenance.get("page"),
        "code_at_review": course.get("course_code"),
    }


def unclaimed_locator(item: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "kind": "unclaimed", "table_index": item.get("table_index"), "cell_ids": sorted(item.get("cell_ids") or []),
        "page": item.get("page"), "code_at_review": item.get("code"),
    }


def locator_key(locator: Mapping[str, Any]) -> tuple:
    if locator.get("kind") == "unclaimed":
        return ("unclaimed", tuple(locator.get("cell_ids") or ()), locator.get("page"), locator.get("code_at_review"))
    return ("course", tuple(locator.get("cell_ids") or ()))


def make_entry(
    *, reviewer: str, reason: str, pdf_sha256: str, locator: Mapping[str, Any], field: str, disposition: str,
    old_value: Any, new_value: Any, section: str, fix_id: str | None = None, rejected_fixes: Sequence[str] = (),
    via: str = "sheet", now: datetime | None = None,
) -> dict[str, Any]:
    if disposition not in DISPOSITIONS:
        raise LedgerError(f"unknown disposition {disposition!r}")
    if not reviewer.strip() or not pdf_sha256:
        raise LedgerError("an entry needs a reviewer and a pdf_sha256")
    entry = {
        "ledger_version": LEDGER_VERSION,
        "recorded_at": (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "reviewer": reviewer.strip(), "reason": reason.strip(), "pdf_sha256": pdf_sha256,
        "locator": dict(locator), "field": field, "disposition": disposition,
        "old_value": old_value, "new_value": new_value, "section": section,
        "fix_id": fix_id, "rejected_fixes": list(rejected_fixes), "via": via,
    }
    entry["entry_id"] = hashlib.sha256(json.dumps(entry, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:16]
    return entry


def read_entries(path: Path) -> list[dict[str, Any]]:
    path = Path(path)
    if not path.exists():
        return []
    entries = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as exc:
            raise LedgerError(f"{path} line {number} is not JSON: {exc}") from exc
        if entry.get("ledger_version") != LEDGER_VERSION or entry.get("disposition") not in DISPOSITIONS:
            raise LedgerError(f"{path} line {number} is not a {LEDGER_VERSION} entry")
        entries.append(entry)
    return entries


def _signature(entry: Mapping[str, Any]) -> tuple:
    return (entry["field"], entry["disposition"], json.dumps(entry["old_value"], sort_keys=True), json.dumps(entry["new_value"], sort_keys=True))


def append_entries(path: Path, entries: Sequence[Mapping[str, Any]]) -> tuple[int, int]:
    """Append only; returns (written, skipped). A group of entries for one course or printed code
    that equals the tail of what the ledger already holds for it is skipped, so applying the same
    sheet twice writes nothing the second time. Existing lines are never rewritten."""
    path = Path(path)
    existing = read_entries(path)  # raises on a damaged ledger before anything is appended
    held: dict[tuple, list] = defaultdict(list)
    for entry in existing:
        held[locator_key(entry["locator"])].append(_signature(entry))
    groups: dict[tuple, list] = defaultdict(list)
    for entry in entries:
        groups[locator_key(entry["locator"])].append(entry)
    fresh = []
    for key, group in groups.items():
        tail = held.get(key, [])[-len(group):]
        if tail != [_signature(e) for e in group]:
            fresh += group
    if fresh:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8", newline="\n") as handle:
            for entry in fresh:
                handle.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
            handle.flush()
    return len(fresh), len(entries) - len(fresh)


def split_applicable(entries: Iterable[Mapping[str, Any]], pdf_sha256: str) -> tuple[list, list]:
    """(applicable, inapplicable): entries recorded against another PDF are inapplicable."""
    ok, no = [], []
    for entry in entries:
        (ok if entry["pdf_sha256"] == pdf_sha256 else no).append(entry)
    return ok, no


def latest_by_field(entries: Iterable[Mapping[str, Any]]) -> dict[tuple, Mapping[str, Any]]:
    """(locator key, field) -> the last entry in file order that decides it. A `row` entry decides
    all three course fields; a later field entry overrides it for that field and the other way round."""
    latest: dict[tuple, Mapping[str, Any]] = {}
    for entry in entries:
        key = locator_key(entry["locator"])
        if entry["field"] == FIELD_ROW:
            for name in COURSE_FIELDS:
                latest[(key, name)] = entry
        else:
            latest[(key, entry["field"])] = entry
    return latest


def content_review_state(payload: Mapping[str, Any], entries: Iterable[Mapping[str, Any]], pdf_sha256: str) -> dict[str, Any]:
    """pending | partially_reviewed | reviewed, from the ledger alone. The interface Phase C reads.

    reviewed means a human decided every course (accepted or corrected) and every printed code or
    anomaly the audit listed, with nothing left unresolved. It does not mean the content is right
    and it is not an approval of the curriculum."""
    applicable, inapplicable = split_applicable(entries, pdf_sha256)
    latest = latest_by_field(applicable)
    courses = payload.get("courses") or []
    decided = unresolved = 0
    for course in courses:
        key = locator_key(course_locator(course))
        chosen = [latest.get((key, name)) for name in COURSE_FIELDS]
        if all(chosen) and all(e["disposition"] != UNRESOLVED for e in chosen):
            decided += 1
        if any(e and e["disposition"] == UNRESOLVED for e in chosen):
            unresolved += 1
    audit = payload.get("audit") or {}
    listed = {locator_key(unclaimed_locator(u)) for u in audit.get("unclaimed_course_candidates") or []}
    undecided = sum(1 for key in listed if (key, FIELD_UNCLAIMED) not in latest)
    unresolved += sum(1 for (key, name), e in latest.items() if name == FIELD_UNCLAIMED and e["disposition"] == UNRESOLVED)
    if not applicable:
        state = "pending"
    elif decided == len(courses) and undecided == 0 and unresolved == 0:
        state = "reviewed"
    else:
        state = "partially_reviewed"
    return {"state": state, "courses": len(courses), "decided": decided, "unresolved": unresolved,
            "unclaimed_undecided": undecided, "inapplicable_entries": len(inapplicable)}
