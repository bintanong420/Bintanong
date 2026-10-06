"""Append-only decision ledger (and, in the next task, the corrected candidate materialised from it).

The extraction is never edited. A human decision is one JSON line: who, when, why, which PDF
(`pdf_sha256`), which course (its source cell ids), which field, the old value and the new value
or a disposition (accepted, corrected, unresolved), and the fix proposal it came from. A corrected
candidate is rebuilt from the immutable extraction plus the applicable entries; entries recorded
against another PDF, another course or another old value are reported, never applied.

Conforms to master plan 7.1 step 7 and draft Task 5: reviewer, time, reason, PDF hash, course and
field locator, original value, correction or disposition, linked cells. A later GUI reads and
appends the same lines.

`entry_id` is a hash of the entry's own contents. It is tamper-evident only in the sense of catching an accidental
or careless edit of a line; it is not a signature and does not stop a deliberate forger, who can recompute it.
That is acceptable for a local, single-user ledger and must not be presented as more.
"""

from __future__ import annotations

import copy
import errno
import hashlib
import json
import os
import sys
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
MAX_UNITS = 99
UNIT_FIELDS = ("lecture_units", "lab_units", "total_units")   # the candidate's flat unit fields
FIELD_PREREQ = "prerequisites_raw"
CORRECTABLE_FIELDS = (*COURSE_FIELDS, *UNIT_FIELDS, FIELD_PREREQ)   # review state still asks only for COURSE_FIELDS
ENTRY_FIELDS = (*CORRECTABLE_FIELDS, FIELD_ROW, FIELD_UNCLAIMED)
STALE_SECTIONS = ["audit", "elective_tracks", "prolog", "quality_report", "rag"]  # not rebuilt from corrections


class LedgerError(ValueError):
    """The ledger file is not what an append-only ledger should be."""


class LedgerLine(dict):
    """An entry as read from the file, remembering which line it came from (equal to the plain dict)."""

    def __init__(self, entry: Mapping[str, Any], line: int):
        super().__init__(entry)
        self.line = line


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
        return None if ok else f"a corrected term must read as a year and one semester, not {_short(new_value)}"
    if field in UNIT_FIELDS:
        # parse_units reads at most two digits and the extractor derives every unit as a whole number (verify formats
        # the totals with `+d`); no real prospectus in the cache prints a fraction of a unit. 99 is that parser's ceiling.
        ok = type(new_value) is int and 0 <= new_value <= MAX_UNITS
        return None if ok else f"a corrected {field} must be a whole number from 0 to {MAX_UNITS}, not {_short(new_value)}"
    if field == FIELD_PREREQ:
        return None if isinstance(new_value, str) else f"a corrected {field} must be text (empty for none), not {_short(new_value)}"
    return f"only {', '.join(CORRECTABLE_FIELDS)} can be corrected, not {_short(field)}"


def _short(value: Any) -> str:
    """A value described for a message without formatting it whole: a ledger line can hold a huge int (str() of
    one raises ValueError past 4300 digits) or a megabyte string."""
    if isinstance(value, (bool, type(None))):
        return repr(value)
    if isinstance(value, int):
        return repr(value) if value.bit_length() <= 64 else f"an int of {value.bit_length()} bits"
    if isinstance(value, float):
        return f"float {value!r}"
    if isinstance(value, str):
        return repr(value) if len(value) <= 40 else repr(value[:37]) + f"... ({len(value)} characters)"
    return f"a {type(value).__name__}"


def same_value(a: Any, b: Any) -> bool:
    """Equality that keeps types apart: a bool is never a number and an int is never a float."""
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a == b
    if isinstance(a, (int, float)) or isinstance(b, (int, float)):
        return type(a) is type(b) and a == b          # 0 and 0.0 are different stored values
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(same_value(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return len(a) == len(b) and all(same_value(x, y) for x, y in zip(a, b))
    return type(a) is type(b) and a == b


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
        return f"unknown field {_short(entry.get('field'))}"
    if problem := locator_problem(entry.get("locator")):
        return problem
    for name in ("entry_id", "reviewer", "recorded_at", "reason", "pdf_sha256"):
        if not _text(entry.get(name)):
            return f"missing {name}"
    if "old_value" not in entry:
        return "missing old_value"
    if entry.get("disposition") not in DISPOSITIONS:
        return f"unknown disposition {_short(entry.get('disposition'))}"
    if entry["disposition"] == CORRECTED and (problem := correction_problem(entry["field"], entry.get("new_value"))):
        return problem
    if entry["entry_id"] != entry_id_of(entry):
        return "entry_id does not match the entry's contents (edited after it was written?)"
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


def entry_id_of(entry: Mapping[str, Any]) -> str:
    """The id make_entry has always given: a hash of every other field of the entry."""
    body = {k: v for k, v in entry.items() if k != "entry_id"}
    try:
        return hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:16]
    except (TypeError, ValueError):
        return ""


def make_entry(
    *, reviewer: str, reason: str, pdf_sha256: str, locator: Mapping[str, Any], field: str, disposition: str,
    old_value: Any, new_value: Any, section: str, fix_id: str | None = None, rejected_fixes: Sequence[str] = (),
    via: str = "sheet", now: datetime | None = None,
) -> dict[str, Any]:
    if disposition not in DISPOSITIONS:
        raise LedgerError(f"unknown disposition {disposition!r}")
    if not reviewer.strip() or not pdf_sha256 or not reason.strip():
        raise LedgerError("an entry needs a reviewer, a reason and a pdf_sha256")
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
    entry["entry_id"] = entry_id_of(entry)
    return entry


def read_entries(path: Path) -> list[dict[str, Any]]:
    """Every line of the ledger, in order. A line that cannot be read comes back as a placeholder
    {"_unreadable": "line N ..."} that `entry_problem` reports: the ledger stays readable forever."""
    path = Path(path)
    if not path.exists():
        return []
    entries = []
    # Split on "\n" only: str.splitlines() also breaks at U+2028, U+2029 and U+0085, which json.dumps
    # (ensure_ascii=False) writes raw inside a value. Bytes are split first and decoded per line, so a
    # non-UTF-8 line is one reported line, not a fatal error; an editor's BOM is dropped.
    for number, raw in enumerate(path.read_bytes().removeprefix(b"\xef\xbb\xbf").split(b"\n"), 1):
        raw = raw.removesuffix(b"\r")
        if not raw.strip():
            continue
        try:
            entry = json.loads(raw.decode("utf-8"))
        except UnicodeDecodeError as exc:
            entries.append({"_unreadable": f"line {number} is not UTF-8: {exc}"})
            continue
        except json.JSONDecodeError as exc:
            entries.append({"_unreadable": f"line {number} is not JSON: {exc}"})
            continue
        if not isinstance(entry, dict) or entry.get("ledger_version") != LEDGER_VERSION:
            entries.append({"_unreadable": f"line {number} is not a {LEDGER_VERSION} entry"})
            continue
        entries.append(LedgerLine(entry, line=number))
    return entries


def _signature(entry: Mapping[str, Any]) -> tuple:
    """What makes a decision a repeat. The PDF is part of it (the same decision on another PDF is a new
    decision); reviewer, time and reason are not (an identical accept by a second reviewer is a repeat)."""
    return (entry["pdf_sha256"], entry["field"], entry["disposition"], json.dumps(entry["old_value"], sort_keys=True), json.dumps(entry["new_value"], sort_keys=True))


class LedgerBusy(LedgerError):
    """Another process holds the write lock on this ledger."""


# What a refused non-blocking lock raises: fcntl.flock gives EAGAIN/EWOULDBLOCK (EACCES on some systems), msvcrt.locking
# EACCES (EDEADLK after its retries), or ERROR_LOCK_VIOLATION. Anything else (ENOLCK on a share, EBADF...) is not "busy".
BUSY_ERRNOS = {errno.EACCES, errno.EAGAIN, errno.EWOULDBLOCK, errno.EDEADLK}
ERROR_LOCK_VIOLATION = 33


def lock_path_for(ledger_path: Path) -> Path:
    ledger_path = Path(ledger_path)
    return ledger_path.with_name(ledger_path.name + ".lock")


class LedgerLock:
    """Advisory write lock on `<ledger>.lock`, held by an open file handle until `release`.

    Byte 0 is the locked byte (msvcrt.locking on Windows, fcntl.flock elsewhere; the branch is chosen when the lock
    is taken). The holder's one-line description starts at byte 1, because on Windows a locked byte range cannot be
    read by another process. The OS drops the lock when its process dies, so there is no stale lock to detect.
    Advisory: it stops the tools of this repository, not an editor, and a network share may not honour it. The file
    holds no decision data and is left in place on release (deleting it would race a second writer).
    """

    def __init__(self, ledger_path: Path, who: str):
        self.ledger_path = Path(ledger_path)
        self.path = lock_path_for(self.ledger_path)
        self.who = who
        self._fd: int | None = None

    def _os_lock(self, fd: int, take: bool) -> None:
        os.lseek(fd, 0, os.SEEK_SET)
        if sys.platform == "win32":
            import msvcrt
            msvcrt.locking(fd, msvcrt.LK_NBLCK if take else msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(fd, (fcntl.LOCK_EX | fcntl.LOCK_NB) if take else fcntl.LOCK_UN)

    def _holder(self) -> str:
        try:
            with self.path.open("rb") as raw:
                raw.seek(1)
                text = raw.read(512).decode("utf-8", "replace").strip()
        except OSError:
            return "unknown holder"
        return text or "unknown holder"

    def __enter__(self) -> "LedgerLock":
        if self._fd is not None:
            raise LedgerError(f"this lock on {self.ledger_path.name} is already held")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(self.path, os.O_RDWR | os.O_CREAT | getattr(os, "O_BINARY", 0))
        try:
            self._os_lock(fd, True)
        except OSError as exc:
            os.close(fd)
            if exc.errno in BUSY_ERRNOS or getattr(exc, "winerror", None) == ERROR_LOCK_VIOLATION:
                raise LedgerBusy(f"the decision ledger {self.ledger_path.name} is in use by {self._holder()}; close that tool or wait") from None
            raise LedgerError(f"the lock file {self.path.name} cannot be locked (errno {exc.errno}: {exc.strerror or exc})") from exc
        try:
            started = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            holder = " ".join(f"{self.who}, pid {os.getpid()}, since {started}".split()).encode("utf-8")
            os.lseek(fd, 0, os.SEEK_SET)
            os.write(fd, b"\n" + holder + b"\n")
            os.ftruncate(fd, 2 + len(holder))
        except BaseException:
            try:
                self._os_lock(fd, False)
            except OSError:
                pass   # closing the handle below drops the lock as well
            os.close(fd)
            raise
        self._fd = fd
        return self

    def release(self) -> None:
        if self._fd is None:
            return
        fd, self._fd = self._fd, None
        try:
            self._os_lock(fd, False)
        finally:
            os.close(fd)

    def __exit__(self, *exc) -> None:
        self.release()


def append_entries(path: Path, entries: Sequence[Mapping[str, Any]], lock: LedgerLock | None = None) -> tuple[int, int]:
    """Append only; returns (written, skipped). A group of entries for one course or printed code
    that equals the tail of what the ledger already holds for it is skipped, so applying the same
    sheet twice writes nothing the second time. Existing lines are never rewritten.

    The ledger's write lock is held for the whole call: pass the `lock` a session already holds, or none to take
    one (LedgerBusy, with nothing written, when another process holds it)."""
    path = Path(path)
    if lock is None:
        with LedgerLock(path, "append_entries") as held:
            return append_entries(path, entries, held)
    if lock._fd is None:
        raise LedgerError(f"the lock on {lock.ledger_path.name} is not held; enter it (with LedgerLock(...) as lock) before passing it")
    if lock.path.resolve() != lock_path_for(path).resolve():
        raise LedgerError(f"the lock is for another ledger ({lock.ledger_path.name}), not {path.name}")
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


def split_stale(payload: Mapping[str, Any], entries: Iterable[Mapping[str, Any]]) -> tuple[list, list, list]:
    """(current, stale, orphan). An orphan names a course that is not in this candidate. A decision counts only while the value it was made on is still what the candidate
    holds: a `row` entry's old value is the course snapshot, a field entry's the field's value, an unclaimed
    code's the printed code. An unclaimed code that the audit does not list is not judged here."""
    by_key: dict[tuple, list[Mapping[str, Any]]] = defaultdict(list)
    for course in payload.get("courses") or []:
        by_key[locator_key(course_locator(course))].append(course)
    listed: dict[tuple, list[Any]] = defaultdict(list)
    for item in (payload.get("audit") or {}).get("unclaimed_course_candidates") or []:
        listed[locator_key(unclaimed_locator(item))].append(item.get("code"))
    current, stale, orphan = [], [], []
    for entry in entries:
        key = locator_key(entry["locator"])
        if key[0] == "unclaimed":
            held = listed.get(key, [])
        else:
            held = [course_snapshot(c) if entry["field"] == FIELD_ROW else _current(c, entry["field"]) for c in by_key.get(key, [])]
            if not held:
                orphan.append(entry)
                continue
        (stale if held and not any(same_value(entry["old_value"], h) for h in held) else current).append(entry)
    return current, stale, orphan


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
    applicable, stale, orphan = split_stale(payload, applicable)
    latest = latest_by_field(applicable)
    courses = payload.get("courses") or []
    decided = unresolved = 0
    for course in courses:
        key = locator_key(course_locator(course))
        chosen = [latest.get((key, name)) for name in COURSE_FIELDS]
        if all(chosen) and all(e["disposition"] != UNRESOLVED for e in chosen):
            decided += 1
        if any(e and e["disposition"] == UNRESOLVED for e in (latest.get((key, n)) for n in CORRECTABLE_FIELDS)):
            unresolved += 1
    audit = payload.get("audit") or {}
    listed = {locator_key(unclaimed_locator(u)) for u in audit.get("unclaimed_course_candidates") or []}
    undecided = sum(1 for key in listed if (key, FIELD_UNCLAIMED) not in latest)
    unresolved += sum(1 for (key, name), e in latest.items() if name == FIELD_UNCLAIMED and e["disposition"] == UNRESOLVED)
    if not applicable:
        state = "pending"
    elif courses and decided == len(courses) and undecided == 0 and unresolved == 0:
        state = "reviewed"
    else:
        state = "partially_reviewed"
    return {"state": state, "courses": len(courses), "decided": decided, "unresolved": unresolved,
            "unclaimed_undecided": undecided, "inapplicable_entries": len(inapplicable), "invalid_entries": len(invalid),
            "stale_entries": len(stale), "orphan_entries": len(orphan), "stale_lines": [e.line for e in stale if hasattr(e, "line")]}


def _current(course: Mapping[str, Any], field: str) -> Any:
    return course.get(field) if field in (*UNIT_FIELDS, FIELD_PREREQ) else course_snapshot(course)[field]


def _apply(course: dict[str, Any], field: str, value: str) -> bool:
    if field == FIELD_CODE:
        course["course_code"] = value
    elif field == FIELD_TITLE:
        course["course_title"] = value
    elif field in UNIT_FIELDS:   # finalize_courses rebuilds the flat unit fields from the units dict
        course["units"] = {**(course.get("units") or {}), field.removesuffix("_units"): value}
        course[field] = value
    elif field == FIELD_PREREQ:  # finalize_courses re-resolves prerequisites, unresolved and standing rules from it
        course[field] = value
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
    applicable, stale, orphan = split_stale(payload, applicable)
    skipped = [{"entry_id": e["entry_id"], "reason": "old_value_changed"} for e in stale]
    skipped += [{"entry_id": e["entry_id"], "reason": "course_not_found"} for e in orphan]
    skipped += [{"entry_id": e["entry_id"], "reason": "pdf_sha256_mismatch"} for e in inapplicable]
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
        if not same_value(_current(course, field), entry["old_value"]):
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
