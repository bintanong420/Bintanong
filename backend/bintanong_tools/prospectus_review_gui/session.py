"""One review session: one candidate, one PDF identity, one reviewer, one ledger held locked until `close`.

The candidate is loaded once and never written. Decided-ness is recomputed from the ledger on every call; the
verification is computed once (the candidate is immutable). The only files written are the ledger (through
`ledger.append_entries`, under the session's `LedgerLock` and a `threading.Lock` for this process's threads), the
lock file beside it, and, on request, `corrected_candidate.json`. Page images and the twin live in memory.

Messages that can reach the browser name files, never their folders.
"""

from __future__ import annotations

import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping

from ..prospectus_extractor.course_checks import load_pdf_pages
from ..prospectus_extractor.fixer_cli import FixerError, assert_outside_git, load_candidate
from ..prospectus_extractor.ledger import (
    LedgerLock, append_entries, content_review_state, lock_path_for, materialise, read_entries, write_corrected,
)
from ..prospectus_extractor.sheet import candidate_sha256
from ..prospectus_extractor.verify import own_role_cells, verify_candidate
from .answers import Answer, answer_to_entries
from .geometry import boxes_for_question
from .questions import COURSE, PREREQ_SUFFIX, PREREQUISITE, SECTION_CONFIRM, UNCLAIMED, Question, build_questions, order_queue
from .render import PageError, PageRenderer, cells_fallback, course_json, evidence_mismatch, load_evidence, twin_fragment

LEDGER_NAME = "decision_ledger.jsonl"
CORRECTED_NAME = "corrected_candidate.json"
NOTE = "A decision here means a person looked and decided. It is not an approval of the curriculum."
APPROVAL_LINE = "A reviewed prospectus is not an approved curriculum"


class ReviewSession:
    def __init__(self, *, candidate: Path, payload: dict, identity: Mapping[str, Any], reviewer: str, review_dir: Path,
                 pdf_path: Path | None, docling_json: Path | None):
        self.candidate = Path(candidate)
        self.payload = payload
        self.pdf_sha256 = identity["pdf_sha256"]
        self.reviewer = reviewer
        self.review_dir = Path(review_dir)
        self.ledger_path = self.review_dir / LEDGER_NAME
        self.corrected_path = self.review_dir / CORRECTED_NAME
        self.pdf_path = Path(pdf_path) if pdf_path else None
        self.docling_json = Path(docling_json) if docling_json else None
        self.candidate_sha256 = candidate_sha256(payload)
        self._write_guard = threading.Lock()
        self._lock: LedgerLock | None = None
        self._renderer: PageRenderer | None = None
        self.pdf_problem: str | None = None
        self._twin: dict[str, Any] | None = None
        self.evidence = None
        self.evidence_problem: str | None = None
        audit = payload.get("audit") or {}
        self._layout = audit.get("table_layout") or []
        self._evidence_ids = {i for s in audit.get("curriculum_sections") or [] for i in s.get("evidence_cells") or []}
        self.verification = None

    # --- lifetime

    def _open(self) -> None:
        for target in (self.ledger_path, lock_path_for(self.ledger_path), self.corrected_path):
            assert_outside_git(target)
        pages = None
        if self.pdf_path is not None:
            try:
                self._renderer = PageRenderer(self.pdf_path)
                pages = load_pdf_pages(self.pdf_path)
            except PageError as exc:
                self.pdf_problem = str(exc)
        elif self.pdf_problem is None:
            self.pdf_problem = "no PDF was given for this session (pass --pdf to see the pages)"
        self.verification = verify_candidate(self.payload, pages)
        if self.docling_json is not None:
            self.evidence, self.evidence_problem = load_evidence(self.docling_json)
            if self.evidence is not None:
                self.evidence_problem = evidence_mismatch(self.evidence, self.payload, self.docling_json.name)
                if self.evidence_problem:   # wrong document: draw nothing rather than highlights on the wrong table
                    self.evidence = None
        else:
            self.evidence_problem = "no Docling JSON is known for this candidate"
        self._lock = LedgerLock(self.ledger_path, f"prospectus review GUI (reviewer {self.reviewer})").__enter__()

    def close(self) -> None:
        if self._lock is not None:
            self._lock.release()
            self._lock = None
        if self._renderer is not None:
            self._renderer.close()
            self._renderer = None

    def __enter__(self) -> "ReviewSession":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    # --- questions

    def _entries(self) -> list:
        return read_entries(self.ledger_path)

    def questions(self, entries: list | None = None) -> list[Question]:
        return build_questions(self.payload, self.verification, self._entries() if entries is None else entries, self.pdf_sha256)

    def queue(self, mode: str = "attention") -> list[Question]:
        return order_queue(self.questions(), mode)

    def question(self, qid: str, entries: list | None = None) -> Question:
        for q in self.questions(entries):
            if q.qid == qid:
                return q
        raise KeyError(qid)

    def _row(self, qid: str):
        for section in self.verification.sections:
            for row in section.rows:
                if row.rid == qid:
                    return row
        return None

    def question_view(self, qid: str) -> dict[str, Any]:
        """Everything one question's three panes need."""
        q = self.question(qid)
        row = self._row(qid.removesuffix(PREREQ_SUFFIX) if q.kind == PREREQUISITE else qid)
        course = self.payload["courses"][row.course] if q.kind in (COURSE, PREREQUISITE) and row is not None else None
        roles = own_role_cells(course, self._layout, self._evidence_ids) if course is not None else {}
        boxes: dict[str, Any] = {}
        if self._renderer is not None and q.kind in (COURSE, UNCLAIMED, PREREQUISITE, SECTION_CONFIRM):
            for page in q.pages:
                if 1 <= page <= self._renderer.page_count:
                    docling = (self.evidence.page_sizes.get(page) if self.evidence is not None else None)
                    boxes[str(page)] = boxes_for_question(
                        q, page=page, page_size=self._renderer.size(page), rotation=self._renderer.rotation(page),
                        docling_size=docling, course=course, role_cells=roles, item=row.item if row is not None else None)
                else:
                    boxes[str(page)] = {"boxes": [], "warning": f"page {page} is not in the PDF"}
        return {
            "question": q.to_dict(),
            "course": course_json(course, row, roles) if course is not None else None,
            "cells": cells_fallback(course, roles) if course is not None else [],
            "twin_cell_ids": list((course.get("provenance") or {}).get("source_cell_ids") or []) if course is not None else [],
            "boxes": boxes,
            "pdf": self.pdf_info(),
        }

    def pdf_info(self) -> dict[str, Any]:
        if self._renderer is None:
            return {"available": False, "reason": self.pdf_problem}
        return {"available": True, "name": self._renderer.name, "pages": self._renderer.page_count}

    def page_png(self, number: int, scale: float) -> bytes:
        if self._renderer is None:
            raise PageError(self.pdf_problem or "no PDF", "missing_pdf")
        return self._renderer.png(number, scale)

    def twin(self) -> dict[str, Any]:
        """The markup twin, computed once per session; without evidence, the reason and the cell fallback hint."""
        if self._twin is None:
            if self.evidence is None:
                self._twin = {"html": None, "reason": f"markup twin unavailable: {self.evidence_problem}"}
            else:
                self._twin = {"html": twin_fragment(self.evidence, self.payload, self.pdf_sha256), "reason": None}
        return self._twin

    # --- writing

    def answer(self, qid: str, answer: Answer, now: datetime | None = None) -> dict[str, Any]:
        """{"written", "skipped", "errors"}; KeyError for an unknown question. Nothing is written on any error."""
        if not isinstance(self.reviewer, str) or not self.reviewer.strip():
            return {"written": 0, "skipped": 0, "errors": ["a reviewer name is needed"]}
        with self._write_guard:
            if self._lock is None:
                return {"written": 0, "skipped": 0, "errors": ["the session is closed"]}
            entries_now = self._entries()
            question = self.question(qid, entries_now)
            entries, errors = answer_to_entries(
                question, answer, payload=self.payload, verification=self.verification, reviewer=self.reviewer,
                pdf_sha256=self.pdf_sha256, now=now, ledger_entries=entries_now)
            if errors:
                return {"written": 0, "skipped": 0, "errors": errors}
            written, skipped = append_entries(self.ledger_path, entries, self._lock)
        return {"written": written, "skipped": skipped, "errors": []}

    def materialise(self) -> dict[str, Any]:
        assert_outside_git(self.corrected_path)
        corrected, report = materialise(self.payload, self._entries(), self.pdf_sha256)
        write_corrected(self.corrected_path, corrected, raw_candidate=self.candidate)
        return {"file": self.corrected_path.name, "applied": report["applied"], "skipped": len(report["skipped"]),
                "content_review": report["content_review"]}

    def state(self) -> dict[str, Any]:
        entries = self._entries()
        questions = self.questions(entries)
        review = content_review_state(self.payload, entries, self.pdf_sha256)
        asked = [q for q in questions if q.kind == PREREQUISITE]
        audit = (self.payload.get("audit") or {}).get("status", "unknown")
        return {
            "program": self.payload.get("program") or "",
            "reviewer": self.reviewer,
            "extraction_audit": audit,
            "content_review": review,
            # The three states Phase C keeps apart, each with its own word. The content-review word is live from the
            # ledger; the payload's own `content_review` is what the extractor wrote and is never shown here. Source
            # verification is the source record's word (the GUI never sets it); the PDF-text check is shown beside it.
            "review_states": [
                {"name": "extraction audit", "word": audit, "meaning": "the extractor's check of its own work"},
                {"name": "content review", "word": review["state"], "meaning": "whether a person decided every course row"},
                {"name": "source verification", "word": str(self.payload.get("source_verification") or "pending"),
                 "meaning": "whether a person verified the source document"},
            ],
            "approval_line": APPROVAL_LINE,
            "prerequisites": {"questions": len(asked), "decided": sum(q.decided for q in asked),
                              "unclassified_courses": sum(1 for c in self.payload.get("courses") or [] if not c.get("prerequisite_state"))},
            "source_verification": {"health": self.verification.health, "pdf_checked": self.verification.pdf_checked},
            "progress": {"decided": sum(q.decided for q in questions if q.kind != PREREQUISITE),
                         "questions": sum(q.kind != PREREQUISITE for q in questions)},
            "pdf": self.pdf_info(),
            "docling": {"ok": self.evidence is not None, "warning": self.evidence_problem if self.docling_json is not None and self.evidence is None else None},
            "note": NOTE,
        }


def open_session(candidate: Path, identity: Mapping[str, Any], reviewer: str | None, review_dir: Path,
                 pdf_path: Path | None = None, docling_json: Path | None = None) -> ReviewSession:
    """Load, verify, guard and lock. FixerError for a missing reviewer or an unsafe folder, LedgerBusy when another
    tool holds the ledger. With no `docling_json`, the path the extractor recorded in the candidate is tried."""
    if not isinstance(reviewer, str) or not reviewer.strip():
        raise FixerError("no reviewer: pass --reviewer NAME or set git config user.name")
    payload = load_candidate(candidate)
    if docling_json is None:
        recorded = next((c.get("provenance", {}).get("raw_docling_json") for c in payload.get("courses") or []
                         if (c.get("provenance") or {}).get("raw_docling_json")), None)
        docling_json = Path(recorded) if recorded else None
    session = ReviewSession(candidate=candidate, payload=payload, identity=identity, reviewer=reviewer.strip(),
                            review_dir=review_dir, pdf_path=pdf_path or identity.get("pdf_path"), docling_json=docling_json)
    try:
        session._open()
    except BaseException:
        session.close()
        raise
    return session
