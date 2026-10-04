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

import copy
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .courses import finalize_courses
from .fixes import FIELD_CODE, FIELD_TERM, FIELD_TITLE, format_term, parse_term
from .text import term_index
from .verify import verify_candidate
from .views import build_curriculum_by_term, build_unlocks_map, make_prerequisite_edges

LEDGER_VERSION = "prospectus-decision-ledger-v1"
CORRECTED_VERSION = "prospectus-corrected-candidate-v1"
ACCEPTED, CORRECTED, UNRESOLVED = "accepted", "corrected", "unresolved"
DISPOSITIONS = (ACCEPTED, CORRECTED, UNRESOLVED)
FIELD_ROW, FIELD_UNCLAIMED = "row", "unclaimed"
COURSE_FIELDS = (FIELD_CODE, FIELD_TITLE, FIELD_TERM)
ENTRY_FIELDS = (*COURSE_FIELDS, FIELD_ROW, FIELD_UNCLAIMED)
STALE_SECTIONS = ["audit", "elective_tracks", "prolog", "quality_report", "rag"]  # not rebuilt from corrections


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


def correction_problem(field: Any, new_value: Any) -> str | None:
    """Why `new_value` cannot be applied to `field`, or None. Shared by writing and reading an entry."""
    if field in (FIELD_CODE, FIELD_TITLE):
        return None if isinstance(new_value, str) and new_value.strip() else f"a corrected {field} needs a non-empty text"
    if field == FIELD_TERM:
        ok = isinstance(new_value, str) and parse_term(new_value) is not None
        return None if ok else f"a corrected term must read as a year and one semester, not {new_value!r}"
    return f"only {', '.join(COURSE_FIELDS)} can be corrected, not {field!r}"


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def locator_problem(locator: Any) -> str | None:
    """Why `locator` is not the shape course_locator / unclaimed_locator write, or None."""
    if not isinstance(locator, dict) or locator.get("kind") not in ("course", "unclaimed"):
        return "missing or unreadable locator"
    cells = locator.get("cell_ids", [])
    if not isinstance(cells, list) or not all(isinstance(c, str) for c in cells):
        return "locator cell_ids must be a list of text"
    for name in ("table_index", "page"):
        if not isinstance(locator.get(name), (int, type(None))) or isinstance(locator.get(name), bool):
            return f"locator {name} must be a whole number or empty"
    if not isinstance(locator.get("code_at_review"), (str, type(None))):
        return "locator code_at_review must be text or empty"
    return None


def entry_problem(entry: Mapping[str, Any]) -> str | None:
    """Why a ledger line cannot be decided on, or None. Such a line stays in the file (append-only)
    and is reported, never applied, never a crash."""
    if "_unreadable" in entry:
        return str(entry["_unreadable"])
    if entry.get("field") not in ENTRY_FIELDS:
        return f"unknown field {entry.get('field')!r}"
    if problem := locator_problem(entry.get("locator")):
        return problem
    for name in ("reviewer", "recorded_at", "pdf_sha256"):
        if not _text(entry.get(name)):
            return f"missing {name}"
    if entry.get("disposition") not in DISPOSITIONS:
        return f"unknown disposition {entry.get('disposition')!r}"
    if entry["disposition"] == CORRECTED:
        return correction_problem(entry["field"], entry.get("new_value"))
    return None


def split_valid(entries: Iterable[Mapping[str, Any]]) -> tuple[list, list]:
    """(decidable entries, [(entry, problem)] for the rest)."""
    ok, bad = [], []
    for entry in entries:
        problem = entry_problem(entry)
        if problem:
            bad.append((entry, problem))
        else:
            ok.append(entry)
    return ok, bad


def make_entry(
    *, reviewer: str, reason: str, pdf_sha256: str, locator: Mapping[str, Any], field: str, disposition: str,
    old_value: Any, new_value: Any, section: str, fix_id: str | None = None, rejected_fixes: Sequence[str] = (),
    via: str = "sheet", now: datetime | None = None,
) -> dict[str, Any]:
    if disposition not in DISPOSITIONS:
        raise LedgerError(f"unknown disposition {disposition!r}")
    if not reviewer.strip() or not pdf_sha256:
        raise LedgerError("an entry needs a reviewer and a pdf_sha256")
    if field not in ENTRY_FIELDS:
        raise LedgerError(f"unknown field {field!r}; use one of {', '.join(ENTRY_FIELDS)}")
    if disposition == CORRECTED and (problem := correction_problem(field, new_value)):
        raise LedgerError(problem)
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
    """Every line of the ledger, in order. A line that cannot be read comes back as a placeholder
    {"_unreadable": "line N ..."} that `entry_problem` reports: the ledger stays readable forever."""
    path = Path(path)
    if not path.exists():
        return []
    entries = []
    # Split on "\n" only: str.splitlines() also breaks at U+2028, U+2029 and U+0085, which json.dumps
    # (ensure_ascii=False) writes raw inside a value. utf-8-sig tolerates an editor's BOM.
    for number, line in enumerate(path.read_bytes().decode("utf-8-sig").split("\n"), 1):
        line = line.removesuffix("\r")
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as exc:
            entries.append({"_unreadable": f"line {number} is not JSON: {exc}"})
            continue
        if not isinstance(entry, dict) or entry.get("ledger_version") != LEDGER_VERSION:
            entries.append({"_unreadable": f"line {number} is not a {LEDGER_VERSION} entry"})
            continue
        entries.append(entry)
    return entries


def _signature(entry: Mapping[str, Any]) -> tuple:
    """What makes a decision a repeat. The PDF is part of it (the same decision on another PDF is a new
    decision); reviewer, time and reason are not (an identical accept by a second reviewer is a repeat)."""
    return (entry["pdf_sha256"], entry["field"], entry["disposition"], json.dumps(entry["old_value"], sort_keys=True), json.dumps(entry["new_value"], sort_keys=True))


def append_entries(path: Path, entries: Sequence[Mapping[str, Any]]) -> tuple[int, int]:
    """Append only; returns (written, skipped). A group of entries for one course or printed code
    that equals the tail of what the ledger already holds for it is skipped, so applying the same
    sheet twice writes nothing the second time. Existing lines are never rewritten."""
    path = Path(path)
    existing, _undecidable = split_valid(read_entries(path))  # unreadable lines are skipped, never fatal
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
        with path.open("ab+") as probe:  # a hand-edited last line may lack its newline: never glue two entries together
            probe.seek(0, 2)
            if probe.tell() and (probe.seek(-1, 2), probe.read(1))[1] != b"\n":
                probe.write(b"\n")
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
    entries, invalid = split_valid(entries)
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
            "unclaimed_undecided": undecided, "inapplicable_entries": len(inapplicable), "invalid_entries": len(invalid)}


def _current(course: Mapping[str, Any], field: str) -> str:
    return course_snapshot(course)[field]


def _apply(course: dict[str, Any], field: str, value: str) -> bool:
    if field == FIELD_CODE:
        course["course_code"] = value
    elif field == FIELD_TITLE:
        course["course_title"] = value
    else:
        term = parse_term(value)
        if term is None:
            return False
        course["year_level"], course["semester"] = term
        course["term_index"] = term_index(*term)
    return True


def materialise(payload: Mapping[str, Any], entries: Iterable[Mapping[str, Any]], pdf_sha256: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """(corrected candidate, report). Deterministic: the same payload and ledger give the same bytes.

    Applies the latest `corrected` entry per course field when the PDF matches, exactly one course
    carries the locator's cell ids, and the course still holds the entry's old value. Everything
    else lands in report["skipped"] with a reason. Derived views are rebuilt; the sections named in
    review.derived_sections_stale are not re-derived and must not be read as the corrected state."""
    entries = list(entries)
    decidable, invalid = split_valid(entries)
    applicable, inapplicable = split_applicable(decidable, pdf_sha256)
    skipped = [{"entry_id": e["entry_id"], "reason": "pdf_sha256_mismatch"} for e in inapplicable]
    skipped += [{"entry_id": e.get("entry_id"), "reason": f"invalid_entry: {problem}"} for e, problem in invalid]
    courses = copy.deepcopy(list(payload.get("courses") or []))
    by_key: dict[tuple, list[int]] = defaultdict(list)
    for index, course in enumerate(courses):
        by_key[locator_key(course_locator(course))].append(index)
    applied: list[str] = []
    for (key, field), entry in sorted(latest_by_field(applicable).items(), key=lambda kv: (str(kv[0][0]), kv[0][1])):
        if key[0] != "course" or entry["disposition"] != CORRECTED or entry["field"] == FIELD_ROW:
            continue
        where = by_key.get(key, [])
        if len(where) != 1:
            skipped.append({"entry_id": entry["entry_id"], "reason": "course_not_found" if not where else "ambiguous_course"})
            continue
        course = courses[where[0]]
        if _current(course, field) != entry["old_value"]:
            skipped.append({"entry_id": entry["entry_id"], "reason": "old_value_changed"})
        elif not _apply(course, field, entry["new_value"]):
            skipped.append({"entry_id": entry["entry_id"], "reason": "unreadable_new_value"})
        else:
            applied.append(entry["entry_id"])
    for course in courses:
        course["code"], course["title"] = course.get("course_code"), course.get("course_title")
    final, _index, duplicates = finalize_courses(courses)
    corrected = {k: copy.deepcopy(v) for k, v in payload.items()}
    corrected.update({
        "courses": final,
        "curriculum_by_term": build_curriculum_by_term(final),
        "prerequisite_edges": make_prerequisite_edges(final),
        "unlocks": build_unlocks_map(final),
    })
    state = content_review_state(payload, entries, pdf_sha256)
    corrected["review"] = {
        "schema": CORRECTED_VERSION, "pdf_sha256": pdf_sha256, "content_review": state,
        "applied_entry_ids": sorted(applied), "skipped": sorted(skipped, key=lambda s: (s["reason"], str(s["entry_id"]))),
        "duplicate_course_codes": [d["course_code"] for d in duplicates],
        "verification_counts": verify_candidate(corrected).counts(),
        "derived_sections_stale": STALE_SECTIONS,
        "note": "A corrected candidate is a review artifact. It is not an approved curriculum.",
    }
    return corrected, {"applied": len(applied), "skipped": skipped, "content_review": state}


def write_corrected(path: Path, corrected: Mapping[str, Any], *, raw_candidate: Path | None = None) -> None:
    """Write the corrected candidate. Never onto `raw_candidate`: the extraction is immutable."""
    if raw_candidate is not None and Path(path).resolve() == Path(raw_candidate).resolve():
        raise LedgerError(f"{path} is the raw candidate; the extraction is never overwritten")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(corrected, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
