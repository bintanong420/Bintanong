"""What the review GUI asks, in which order, and what is already decided.

One question per course row, per printed code no course claimed, and per section that has no flag above `info`
(one bulk "are all N courses correct" question). Questions are data: nothing is pre-selected, and the
fixer's proposals are hints. Decided-ness comes from the ledger only, through the same filters the content-review
state uses (decidable line, this PDF, value still as reviewed), and a later line wins.

Nothing here writes or mutates the payload.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Iterable, Mapping, Sequence

from ..prospectus_extractor.ledger import (
    ACCEPTED, CORRECTABLE_FIELDS, CORRECTED, COURSE_FIELDS, FIELD_UNCLAIMED, UNRESOLVED, course_locator, latest_by_field,
    locator_key, split_applicable, split_stale, split_valid, unclaimed_locator,
)
from ..prospectus_extractor.verify import ERROR, INFO, WARN, Row, Section, Verification

COURSE, UNCLAIMED, SECTION_CONFIRM = "course", "unclaimed", "section_confirm"
HEALTH_RANK = {"broken": 0, "review": 1, "clean": 2}
SEVERITY_RANK = {ERROR: 0, WARN: 1}
MODES = ("attention", "print")


@dataclass
class Question:
    qid: str                       # the row id (S1-02, S1-U1) or "<sid>:confirm"
    kind: str                      # course | unclaimed | section_confirm
    section: dict[str, str]        # sid, title, health
    prompt: str
    reference: dict[str, Any]      # the values shown to the reviewer
    flags: list[dict[str, Any]]
    proposals: list[dict[str, Any]]
    editable_fields: list[str]
    other_allowed: bool
    locator: dict[str, Any] | None  # what the ledger keys the decision on (None for a section question)
    pages: list[int]
    decision: dict[str, Any] | None = None   # the current decision from the ledger, if any
    position: int = 0                        # printed order, section question first in its section
    members: list[str] = field(default_factory=list)   # section_confirm: the row ids it covers

    @property
    def decided(self) -> bool:
        """Accepted or corrected. An `unresolved` decision is shown but the question stays in the queue. A section
        question is decided once every course in it has a decision of any kind: it never overrides one (D11)."""
        if self.kind == SECTION_CONFIRM:
            return bool(self.decision)
        return bool(self.decision) and self.decision["disposition"] in (ACCEPTED, CORRECTED)

    def to_dict(self) -> dict[str, Any]:
        return {**asdict(self), "decided": self.decided}


def _flag(flag) -> dict[str, Any]:
    return {"severity": flag.severity, "kind": flag.kind, "message": flag.message, "field": flag.field}


def _proposal(letter: str, fix) -> dict[str, Any]:
    return {"letter": letter, "kind": fix.kind, "field": fix.field, "old": fix.old, "new": fix.new, "note": fix.note,
            "fix_id": fix.fix_id}


def _pages(course: Mapping[str, Any]) -> list[int]:
    provenance = course.get("provenance") or {}
    pages = {c.get("page") for c in provenance.get("source_cells") or []} | {provenance.get("page")}
    return sorted(p for p in pages if isinstance(p, int) and not isinstance(p, bool))


def _section_info(section: Section) -> dict[str, str]:
    return {"sid": section.sid, "title": section.title, "health": section.health}


def _course_question(row: Row, section: Section, course: Mapping[str, Any]) -> Question:
    title, code = course.get("course_title") or "", course.get("course_code") or ""
    term = f"{course.get('year_level') or '?'} / {course.get('semester') or '?'}"
    return Question(
        qid=row.rid, kind=COURSE, section=_section_info(section),
        prompt=f'Is the subject "{title}" with course code "{code}" correct?',
        reference={"code": code, "title": title, "term": term, "lecture_units": course.get("lecture_units"),
                   "lab_units": course.get("lab_units"), "total_units": course.get("total_units"),
                   "prerequisites_raw": course.get("prerequisites_raw") or ""},
        flags=[_flag(f) for f in row.flags], proposals=[_proposal(l, f) for l, f in row.fixes],
        editable_fields=list(CORRECTABLE_FIELDS), other_allowed=True, locator=course_locator(course), pages=_pages(course))


def _unclaimed_question(row: Row, section: Section) -> Question:
    item = row.item or {}
    page = item.get("page")
    if item.get("source") == "anomaly":
        prompt = f'The audit lists "{item.get("snippet")}" on page {page} as a problem no course explains. Is it right to leave it out?'
    else:
        prompt = f'The PDF prints "{item.get("code")}" on page {page} but no course uses it. Is it right to leave it out?'
    return Question(
        qid=row.rid, kind=UNCLAIMED, section=_section_info(section), prompt=prompt,
        reference={"code": item.get("code"), "page": page, "source": item.get("source"), "snippet": item.get("snippet")},
        flags=[_flag(f) for f in row.flags], proposals=[], editable_fields=[], other_allowed=False,
        locator=unclaimed_locator(item), pages=[page] if isinstance(page, int) else [])


def confirmable(section: Section) -> bool:
    """The sheet's rule (build_entries): no flag above `info` on the section or on any row (an unclaimed printed code
    always carries one), and at least one course."""
    flags = list(section.flags) + [f for row in section.rows for f in row.flags]
    return any(r.course is not None for r in section.rows) and all(f.severity == INFO for f in flags)


def _confirm_question(section: Section, courses: Sequence[Mapping[str, Any]]) -> Question:
    rows = [r for r in section.rows if r.course is not None]
    pages = sorted({p for r in rows for p in _pages(courses[r.course])})
    return Question(
        qid=f"{section.sid}:confirm", kind=SECTION_CONFIRM, section=_section_info(section),
        prompt=f"Are all {len(rows)} courses in {section.title} correct as extracted?",
        reference={"count": len(rows), "courses": [{"rid": r.rid, "code": courses[r.course].get("course_code") or "",
                                                    "title": courses[r.course].get("course_title") or ""} for r in rows]},
        flags=[], proposals=[], editable_fields=[], other_allowed=False, locator=None, pages=pages,
        members=[r.rid for r in rows])


def decision_index(payload: Mapping[str, Any], entries: Iterable[Mapping[str, Any]], pdf_sha256: str) -> dict[tuple, Mapping[str, Any]]:
    """(locator key, field) -> the entry that decides it now: decidable lines only, recorded against this PDF, whose
    old value is still what the candidate holds, the latest line winning."""
    valid, _invalid = split_valid(entries)
    applicable, _other_pdf = split_applicable(valid, pdf_sha256)
    current, _stale, _orphan = split_stale(payload, applicable)
    return latest_by_field(current)


def has_decision(course: Mapping[str, Any], latest: Mapping[tuple, Mapping[str, Any]]) -> bool:
    """Any current ledger line on any field of this course, whatever its disposition. A section Yes skips such a
    course (D11): it never overrides a decision, not even part of one."""
    key = locator_key(course_locator(course))
    return any((key, name) in latest for name in CORRECTABLE_FIELDS)


def current_decision(question: Question, latest: Mapping[tuple, Mapping[str, Any]]) -> dict[str, Any] | None:
    """The decision on a course or printed-code question, or None (undecided, or only part decided)."""
    if question.locator is None:
        return None
    key = locator_key(question.locator)
    if question.kind == UNCLAIMED:
        chosen = [e for e in [latest.get((key, FIELD_UNCLAIMED))] if e]
    else:
        chosen = [e for e in (latest.get((key, name)) for name in CORRECTABLE_FIELDS) if e]
        if not chosen:
            return None
        if not all(latest.get((key, name)) for name in COURSE_FIELDS) and not any(e["disposition"] == UNRESOLVED for e in chosen):
            return None
    if not chosen:
        return None
    pick = next((e for e in chosen if e["disposition"] == UNRESOLVED), None) \
        or next((e for e in chosen if e["disposition"] == CORRECTED), None) or chosen[0]
    return {"disposition": pick["disposition"], "reason": pick["reason"], "reviewer": pick["reviewer"],
            "recorded_at": pick["recorded_at"], "entry_id": pick["entry_id"], "via": pick.get("via")}


def build_questions(payload: Mapping[str, Any], verification: Verification, entries: Iterable[Mapping[str, Any]],
                    pdf_sha256: str) -> list[Question]:
    """Every question in printed order (a section's bulk question first), with its current decision."""
    courses = payload.get("courses") or []
    latest = decision_index(payload, entries, pdf_sha256)
    out: list[Question] = []
    for section in verification.sections:
        rows = []
        for row in section.rows:
            q = _unclaimed_question(row, section) if row.course is None else _course_question(row, section, courses[row.course])
            q.decision = current_decision(q, latest)
            rows.append(q)
        if confirmable(section):
            bulk = _confirm_question(section, courses)
            by_id = {q.qid: q for q in rows}
            if all(has_decision(courses[r.course], latest) for r in section.rows if r.course is not None):
                kinds = {(by_id[m].decision or {}).get("disposition") for m in bulk.members}
                bulk.decision = {"disposition": ACCEPTED if kinds == {ACCEPTED} else CORRECTED if kinds <= {ACCEPTED, CORRECTED}
                                 else UNRESOLVED, "count": len(bulk.members)}
            out.append(bulk)
        out += rows
    for position, q in enumerate(out):
        q.position = position
    return out


def _worst_rank(q: Question) -> int:
    return min((SEVERITY_RANK[f["severity"]] for f in q.flags if f["severity"] in SEVERITY_RANK), default=2)


def order_queue(questions: Iterable[Question], mode: str = "attention") -> list[Question]:
    """The questions still to answer. `attention`: broken sections first, then review, then clean; inside a section
    the section's bulk question, then flagged rows (errors before warnings), then clean rows; printed order breaks
    every tie. `print`: printed order. A decided question is not in the queue (it stays in `build_questions`)."""
    if mode not in MODES:
        raise ValueError(f"mode must be one of {', '.join(MODES)}, not {mode!r}")
    questions = list(questions)
    open_ = [q for q in questions if not q.decided]
    if mode == "print":
        return sorted(open_, key=lambda q: q.position)
    first: dict[str, int] = {}
    for q in questions:
        first.setdefault(q.section["sid"], q.position)
    return sorted(open_, key=lambda q: (HEALTH_RANK[q.section["health"]], first[q.section["sid"]], q.kind != SECTION_CONFIRM,
                                        _worst_rank(q), q.position))
