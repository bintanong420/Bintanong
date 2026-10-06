"""An answer (Yes, No, Other) to ledger entries.

This module builds no entry itself: every entry comes from `sheet.row_entries`, the function the review sheet
uses, so a GUI decision and a sheet decision are the same entries by construction. What it adds is the typed-value
parsing (text to a whole number, a year-and-semester text to the stored term) and the GUI's own rules about which
answer is allowed on which question. Any error means no entries (all or nothing, like the sheet).

Mapping (decision D4):
  course        Yes    -> ok          Other -> edit (or fix, for proposal letters and for a typed value equal to a proposal)
                No     -> unresolved when nothing is typed, else the same as Other
  printed code  Yes    -> ok          No    -> unresolved (a reason for both; Other is refused)
  section       Yes    -> one ok per course that has no decision yet, via gui_section_confirm (D11: never overrides
                          a decision); No writes nothing; Other is refused
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Iterable, Mapping, Sequence

from ..prospectus_extractor.fixes import FIELD_TERM, format_term, parse_term
from ..prospectus_extractor.ledger import UNIT_FIELDS, correction_problem
from ..prospectus_extractor.sheet import row_entries
from ..prospectus_extractor.verify import INFO, Verification
from .questions import SECTION_CONFIRM, UNCLAIMED, Question, confirmable, decision_index, has_decision

CHOICES = ("yes", "no", "other")
WHOLE_NUMBER = re.compile(r"[0-9]{1,6}")   # ASCII digits only: "+3", "3.5", "1e2", "-1" and other scripts' digits do not match
SECTION_CONFIRM_REASON = "section confirmed as extracted"
MAX_REASON = 2000   # characters, for a reason and a section note


@dataclass
class Answer:
    choice: str                                   # yes | no | other
    edits: Mapping[str, Any] = field(default_factory=dict)   # field name -> the text the reviewer typed
    proposals: Sequence[str] = ()                 # proposal letters the reviewer chose
    reason: str = ""
    note: str = ""                                # an optional note on a section question (becomes the reason)


def text_problem(text: Any, what: str) -> str | None:
    """Why typed text cannot be stored, or None: a lone surrogate cannot be written as UTF-8, and a control character
    (NUL, a newline, a tab) has no place in a code, a title or a reason (reasons are one line)."""
    if not isinstance(text, str):
        return None   # the type checks elsewhere name it
    try:
        text.encode("utf-8")
    except UnicodeEncodeError:
        return f"{what} contains a character that cannot be stored (a lone surrogate); retype it"
    if any(unicodedata.category(ch) == "Cc" for ch in text):
        return f"{what} contains a control character (a newline, tab or NUL); remove it"
    return None


def parse_typed_value(field_name: str, text: Any, default_year: str | None = None) -> tuple[Any, str | None]:
    """(value, None) or (None, message). The ledger owns the rules (`correction_problem`); this only turns text into
    the field's type and never reformats a value silently."""
    if not isinstance(text, str):
        return None, correction_problem(field_name, text) or f"a typed {field_name} must be text, not {type(text).__name__}"
    text = text.strip()
    if field_name == FIELD_TERM:
        parsed = parse_term(text, default_year)
        return (format_term(*parsed), None) if parsed else (None, correction_problem(field_name, text))
    value: Any = text
    if field_name in UNIT_FIELDS:
        if not WHOLE_NUMBER.fullmatch(text):
            return None, correction_problem(field_name, text)
        value = int(text)
    problem = correction_problem(field_name, value)
    return (None, problem) if problem else (value, None)


def _find(question: Question, verification: Verification):
    for section in verification.sections:
        if question.kind == SECTION_CONFIRM:
            if section.sid == question.section["sid"]:
                return section, None
            continue
        for row in section.rows:
            if row.rid == question.qid:
                return section, row
    return None, None


def _confirm(question, answer, section, ledger_entries, payload, reviewer, pdf_sha256, via, now):
    if answer.choice == "other":
        return [], ["a section question can only be answered Yes or No"]
    if answer.choice == "no":
        return [], []   # nothing is decided; the rows stay in the queue
    if not confirmable(section):
        kinds = sorted({f.kind for f in [*section.flags, *(f for r in section.rows for f in r.flags)] if f.severity != INFO})
        if not kinds:
            return [], ["this section has no courses to confirm"]
        return [], [f"a whole-section Yes cannot cover a section flagged {', '.join(kinds)}; answer its rows one by one"]
    if ledger_entries is None:
        return [], ["a section answer needs the ledger's current entries"]
    latest = decision_index(payload, ledger_entries, pdf_sha256)
    # D11: a section Yes never overrides a course that already has a decision (of any kind, even part of one)
    open_rows = [r for r in section.rows if r.course is not None and not has_decision(payload["courses"][r.course], latest)]
    if not open_rows:
        return [], ["every course in this section already has a decision; change a course by answering its own question"]
    via = "gui_section_confirm" if via == "gui" else via
    reason = answer.note.strip() or SECTION_CONFIRM_REASON
    entries: list[dict[str, Any]] = []
    errors: list[str] = []
    for row in open_rows:
        errors += row_entries(entries, row, section, payload, "ok", [], reason, {}, via, reviewer, pdf_sha256, now)
    return ([], errors) if errors else (entries, [])   # all or nothing: one course's error drops the whole section


def _printed_code(answer, row, section, payload, reviewer, pdf_sha256, via, now):
    if answer.choice == "other":
        return [], ["a printed code can only be answered Yes or No; no course is added or corrected here"]
    if answer.edits or answer.proposals:
        return [], ["a printed code takes no typed values or proposals"]
    reason = answer.reason.strip()
    if not reason:
        return [], ["a reason is needed for an answer about a printed code"]
    entries: list[dict[str, Any]] = []
    errors = row_entries(entries, row, section, payload, "ok" if answer.choice == "yes" else "unresolved", [], reason, {},
                         via, reviewer, pdf_sha256, now)
    return entries, errors


def _course(answer, row, section, payload, reviewer, pdf_sha256, via, now):
    course = payload["courses"][row.course]
    reason = answer.reason.strip()
    letters = set(answer.proposals)
    edits: dict[str, Any] = {}
    errors: list[str] = []
    for name, text in answer.edits.items():
        value, problem = parse_typed_value(name, text, course.get("year_level"))
        if problem:
            errors.append(problem)
            continue
        same = [letter for letter, fix in row.fixes if fix.field == name and fix.new == value]
        if same:   # a typed value equal to a proposal is that proposal accepted, recorded as the sheet records a fix
            letters.update(same)
        else:
            edits[name] = value
    if errors:
        return [], errors
    if answer.choice == "yes":
        if edits or letters:
            return [], ["Yes cannot carry new values or proposals; use Other"]
        verb = "ok"
    elif answer.choice == "no" and not edits and not letters:
        if not reason:
            return [], ["No needs a reason"]
        verb = "unresolved"
    else:
        if not edits and not letters:
            return [], ["Other needs a typed value or a proposal"]
        if edits and not reason:
            return [], ["a correction needs a reason"]
        verb = "fix" if letters else "edit"
    entries: list[dict[str, Any]] = []
    errors = row_entries(entries, row, section, payload, verb, sorted(letters), reason, edits, via, reviewer, pdf_sha256, now)
    return entries, errors


def answer_to_entries(
    question: Question, answer: Answer, *, payload: Mapping[str, Any], verification: Verification, reviewer: str,
    pdf_sha256: str, via: str = "gui", now: datetime | None = None, ledger_entries: Iterable[Mapping[str, Any]] | None = None,
) -> tuple[list[dict[str, Any]], list[str]]:
    """(entries, errors). Errors mean no entries. The question must be one of this verification's. A section answer
    needs `ledger_entries` (the ledger as it stands), so what is already decided is checked at answer time."""
    if answer.choice not in CHOICES:
        return [], [f"the answer must be yes, no or other, not {answer.choice!r}"]
    if not isinstance(reviewer, str) or not reviewer.strip():   # make_entry would raise on it
        return [], ["a reviewer name is needed"]
    for what, text in ("the reason", answer.reason), ("the note", answer.note):
        if isinstance(text, str) and len(text) > MAX_REASON:
            return [], [f"{what} is {len(text)} characters; the limit is {MAX_REASON}"]
        if problem := text_problem(text, what):
            return [], [problem]
    for name, text in answer.edits.items():
        if problem := text_problem(text, f"the typed {name}"):
            return [], [problem]
    section, row = _find(question, verification)
    if section is None or (row is None and question.kind != SECTION_CONFIRM):
        return [], [f"unknown question {question.qid}"]
    args = (payload, reviewer, pdf_sha256, via, now)
    if question.kind == SECTION_CONFIRM:
        return _confirm(question, answer, section, ledger_entries, *args)
    if question.kind == UNCLAIMED or row.course is None:
        return _printed_code(answer, row, section, *args)
    return _course(answer, row, section, *args)
