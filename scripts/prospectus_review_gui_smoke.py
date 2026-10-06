#!/usr/bin/env python3
"""Drive the prospectus review GUI through TestClient on one real candidate and print what a reviewer would meet.

    python scripts/prospectus_review_gui_smoke.py --candidate X_prospectus.json --pdf X.pdf --review-dir SCRATCH/review
    python scripts/prospectus_review_gui_smoke.py --candidate ... --pdf ... --equivalence-dir SCRATCH/equiv

No UI and no browser: the same HTTP calls the page makes. The candidate and the PDF are only read; use COPIES and a
--review-dir outside the repository (the session refuses an unsafe folder). Every scripted answer carries a reason that
says it came from this script, so none of it can pass for a human review. Nothing here approves a curriculum.

Run needs the `review` extra (FastAPI, httpx): $env:TEMP\\gui-review-venv\\Scripts\\python.exe scripts\\...

The fixed answer script (run): bulk Yes on every section question; Yes on the first SAMPLE undecided course rows;
Other with the first proposal on OTHERS rows that have one (never an invented value); No with a reason on NOS rows;
on unclaimed codes: Other refused, Yes without a reason refused where that rule applies, then Yes and No with reasons;
on prerequisite questions (only candidates made after Phase C have any): Yes, Yes, No, Other. Then materialise.
--equivalence-dir: the same six decisions through the GUI and through an edited review sheet + `fixer_cli apply`
into two ledgers, compared field by field, then both materialised and compared.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "tests"))   # sheet_helpers (edit a rendered sheet the way a reviewer would)

from backend.bintanong_tools.prospectus_extractor import ledger as ledger_module  # noqa: E402
from backend.bintanong_tools.prospectus_extractor.fixer_cli import (  # noqa: E402
    fixer_main, load_candidate, resolve_identity,
)
from backend.bintanong_tools.prospectus_extractor.ledger import FIELD_PREREQ, entry_id_of, read_entries  # noqa: E402

PORT = 8765
REASON = "scripted answer from prospectus_review_gui_smoke.py, not a human review"
FROZEN = datetime(2026, 10, 7, 9, 0, 0, tzinfo=timezone.utc)


class Gui:
    """The loopback app on one session, called the way the page calls it."""

    def __init__(self, candidate, identity, reviewer, review_dir, docling_json=None):
        from fastapi.testclient import TestClient

        from backend.bintanong_tools.prospectus_review_gui.app import create_app, new_token
        from backend.bintanong_tools.prospectus_review_gui.session import open_session

        self.session = open_session(candidate, identity, reviewer, review_dir, pdf_path=identity.get("pdf_path"),
                                    docling_json=docling_json)
        self.token = new_token()
        self.client = TestClient(create_app(self.session, self.token, port=PORT), base_url=f"http://127.0.0.1:{PORT}")

    def close(self):
        self.session.close()

    def get(self, path):
        response = self.client.get(path)
        assert response.status_code == 200, (path, response.status_code, response.text[:200])
        return response.json()

    def post(self, path, body):
        return self.client.post(path, content=json.dumps(body), headers={
            "X-Review-Token": self.token, "Content-Type": "application/json"})

    def answer(self, qid, choice, **fields):
        """(ok, errors): the response of one answer; a refusal is data, not an exception."""
        response = self.post("/api/answer", {"qid": qid, "choice": choice, **fields})
        body = response.json()
        return response.status_code == 200, body.get("errors", [])

    def questions(self):
        return self.get("/api/queue")


def _summary(gui):
    sections = [(s.sid, s.health, s.title) for s in gui.session.verification.sections]
    queue = gui.questions()
    first = queue["queue"][0] if queue["queue"] else None
    by_kind = {}
    for q in queue["all"]:
        by_kind[q["kind"]] = by_kind.get(q["kind"], 0) + 1
    rows = [q for q in queue["queue"] if q["kind"] == "course"]
    title_rows = [q for q in rows if any(p["kind"] == "title_from_pdf" for p in q["proposals"])]
    return {
        "program": gui.session.payload.get("program"),
        "sections": {"total": len(sections), **{h: sum(1 for s in sections if s[1] == h) for h in ("clean", "review", "broken")}},
        "section_list": sections,
        "questions": by_kind,
        "bulk_questions": by_kind.get("section_confirm", 0),
        "bulk_for": [q["section"]["sid"] for q in queue["all"] if q["kind"] == "section_confirm"],
        "first_queue_qid": first["qid"] if first else None,
        "first_queue_kind": first["kind"] if first else None,
        "first_queue_section_health": first["section"]["health"] if first else None,
        "queue_kind_head20": [q["kind"] for q in queue["queue"][:20]],
        "title_from_pdf_rows": len(title_rows),
        "title_from_pdf_preselected": sum(1 for q in title_rows if q["decision"] is not None),   # must be 0
        "proposals_offered": sum(len(q["proposals"]) for q in queue["queue"]),
        "footnote_codes_in_SU": [q["reference"].get("code") for q in queue["queue"]
                                 if q["kind"] == "unclaimed" and q["section"]["sid"] == "SU"][:12],
        "prerequisite_state": gui.get("/api/state")["prerequisites"],
    }


def _answers(gui, samples, others, nos):
    done = {"bulk_yes": 0, "yes": 0, "other_proposal": 0, "no": 0, "unclaimed_yes": 0, "unclaimed_no": 0,
            "prereq_yes": 0, "prereq_no": 0, "prereq_other": 0, "refused": [], "checks": {}}

    def attempt(label, qid, choice, **fields):
        ok, errors = gui.answer(qid, choice, **fields)
        if ok:
            return True
        done["refused"].append({"what": label, "qid": qid, "errors": errors})
        return False

    for q in gui.questions()["all"]:
        if q["kind"] == "section_confirm" and not q["decided"]:
            done["bulk_yes"] += attempt("bulk yes", q["qid"], "yes")
    rows = [q for q in gui.questions()["queue"] if q["kind"] == "course"]
    with_fix = [q for q in rows if q["proposals"]]
    plain = [q for q in rows if not q["proposals"]]
    for q in with_fix[:others]:
        done["other_proposal"] += attempt("other with proposal", q["qid"], "other", proposals=[q["proposals"][0]["letter"]], reason=REASON)
    done["checks"]["rows_with_a_proposal_left_for_other"] = min(len(with_fix), others)
    for q in plain[:nos]:
        done["no"] += attempt("no with reason", q["qid"], "no", reason=f"{REASON}: left unresolved")
    rest = plain[nos:] + with_fix[others:]
    rest.sort(key=lambda q: q["position"])
    for q in rest[:samples]:
        done["yes"] += attempt("sample yes", q["qid"], "yes", reason=REASON)
    unclaimed = [q for q in gui.questions()["queue"] if q["kind"] == "unclaimed" and not q["decided"]]
    if unclaimed:
        done["checks"]["unclaimed_other_refused"] = not gui.answer(unclaimed[0]["qid"], "other", edits={"course_code": "ZZ 1"}, reason=REASON)[0]
        done["checks"]["unclaimed_yes_without_reason_refused"] = not gui.answer(unclaimed[0]["qid"], "yes")[0]
        done["unclaimed_yes"] += attempt("unclaimed yes", unclaimed[0]["qid"], "yes", reason=REASON)
    if len(unclaimed) > 1:
        done["unclaimed_no"] += attempt("unclaimed no", unclaimed[1]["qid"], "no", reason=f"{REASON}: left unresolved")
    prereq = [q for q in gui.questions()["queue"] if q["kind"] == "prerequisite" and not q["decided"]]
    for i, q in enumerate(prereq[:4]):
        if i < 2:
            done["prereq_yes"] += attempt("prereq yes", q["qid"], "yes")
        elif i == 2:
            done["prereq_no"] += attempt("prereq no", q["qid"], "no", reason=f"{REASON}: left unresolved")
        else:
            done["prereq_other"] += attempt("prereq other", q["qid"], "other", edits={FIELD_PREREQ: "SMOKE 101"}, reason=REASON)
    return done


def _all_unresolved(candidate, identity, reviewer, review_dir, docling_json):
    """Every individual question answered No with a reason in a throwaway ledger: none may be refused."""
    gui = Gui(candidate, identity, reviewer, review_dir, docling_json)
    try:
        asked = refused = 0
        for q in gui.questions()["all"]:
            if q["kind"] == "section_confirm":
                continue
            asked += 1
            refused += not gui.answer(q["qid"], "no", reason=f"{REASON}: left unresolved")[0]
        return {"asked": asked, "refused": refused, "content_review": gui.get("/api/state")["content_review"]}
    finally:
        gui.close()


def run(candidate, pdf, review_dir, reviewer, *, pdf_sha256=None, docling_json=None, samples=10, others=3, nos=2,
        all_unresolved=False):
    candidate = Path(candidate)
    identity = resolve_identity(load_candidate(candidate), pdf=pdf, pdf_sha256=pdf_sha256)
    started = time.perf_counter()
    gui = Gui(candidate, identity, reviewer, review_dir, docling_json)
    try:
        queue = gui.questions()
        if queue["queue"]:
            gui.get(f"/api/question/{queue['queue'][0]['qid']}")
        first_question_seconds = round(time.perf_counter() - started, 3)
        out = _summary(gui)
        out["first_question_seconds"] = first_question_seconds
        out["pdf"] = gui.get("/api/state")["pdf"]
        out["docling"] = gui.get("/api/state")["docling"]
        out["answers"] = _answers(gui, samples, others, nos)
        out["materialised"] = gui.post("/api/materialise", {}).json()
        out["state_after"] = gui.get("/api/state")["content_review"]
        out["ledger_entries"] = len(read_entries(gui.session.ledger_path))
    finally:
        gui.close()
    if all_unresolved:
        out["all_unresolved"] = _all_unresolved(candidate, identity, reviewer, Path(str(review_dir) + "_allno"), docling_json)
    out["total_seconds"] = round(time.perf_counter() - started, 3)
    return out


# --- equivalence of the two paths


class _Frozen(datetime):
    @classmethod
    def now(cls, tz=None):
        return FROZEN


def _comparable(corrected):
    """The Task 4 comparison: the corrected candidate without the entry ids (they differ with `via`)."""
    out = json.loads(json.dumps(corrected, sort_keys=True))
    out["review"].pop("applied_entry_ids")
    out["review"]["skipped"] = [{k: v for k, v in s.items() if k != "entry_id"} for s in out["review"]["skipped"]]
    return out


def equivalence(candidate, pdf, work_dir, reviewer="Equivalence Reviewer", docling_json=None):
    """Six course-field decisions entered through the GUI and through an edited sheet + `fixer_cli apply`."""
    from sheet_helpers import edit_row

    candidate, work_dir = Path(candidate), Path(work_dir)
    identity = resolve_identity(load_candidate(candidate), pdf=pdf)
    gui_dir, sheet_dir = work_dir / "gui", work_dir / "sheet"
    probe = Gui(candidate, identity, reviewer, work_dir / "probe", docling_json)
    try:
        rows = [q for q in probe.questions()["queue"] if q["kind"] == "course"]
    finally:
        probe.close()
    rows.sort(key=lambda q: q["position"])
    with_fix = [q for q in rows if q["proposals"]]
    plain = [q for q in rows if not q["proposals"]]
    assert len(plain) >= 5, "need five rows without a proposal"
    picks = [  # (row, sheet decision cells, GUI answer)
        (plain[0], {"decision": "ok"}, ("yes", {})),
        (plain[1], {"decision": f"ok: {REASON}"}, ("yes", {"reason": REASON})),
        (plain[2], {"decision": f"edit: {REASON}", "new_title": "Equivalence Test Title"},
         ("other", {"edits": {"course_title": "Equivalence Test Title"}, "reason": REASON})),
        (plain[3], {"decision": f"edit: {REASON}", "new_code": "ZZ 901"},
         ("other", {"edits": {"course_code": "ZZ 901"}, "reason": REASON})),
        (plain[4], {"decision": f"unresolved: {REASON}"}, ("no", {"reason": REASON})),
    ]
    if with_fix:
        picks.append((with_fix[0], {"decision": f"fix {with_fix[0]['proposals'][0]['letter']}: {REASON}"},
                      ("other", {"proposals": [with_fix[0]["proposals"][0]["letter"]], "reason": REASON})))
    else:
        assert len(plain) >= 6, "no proposal anywhere and fewer than six plain rows"
        picks.append((plain[5], {"decision": f"edit: {REASON}", "new_title": "Equivalence Test Title Two"},
                      ("other", {"edits": {"course_title": "Equivalence Test Title Two"}, "reason": REASON})))
    picks.sort(key=lambda p: p[0]["position"])
    result = {"decisions": [(p[0]["qid"], p[2][0]) for p in picks], "used_a_proposal": bool(with_fix)}

    with mock.patch.object(ledger_module, "datetime", _Frozen):   # recorded_at is the only clock in an entry
        gui = Gui(candidate, identity, reviewer, gui_dir, docling_json)
        try:
            for row, _sheet, (choice, fields) in picks:
                ok, errors = gui.answer(row["qid"], choice, **fields)
                assert ok, (row["qid"], errors)
            materialised_gui = gui.post("/api/materialise", {}).json()
            gui_ledger = gui.session.ledger_path
        finally:
            gui.close()
        sheet_args = ["--candidate", str(candidate), "--pdf", str(pdf), "--review-dir", str(sheet_dir)]
        assert fixer_main(["sheet", *sheet_args]) == 0
        sheet_path = sheet_dir / "review_sheet.md"
        text = sheet_path.read_text(encoding="utf-8")
        for row, cells, _gui in picks:
            text = edit_row(text, row["qid"], **cells)
        sheet_path.write_text(text, encoding="utf-8", newline="\n")
        assert fixer_main(["apply", *sheet_args, "--reviewer", reviewer]) == 0
        assert fixer_main(["materialise", *sheet_args, "--out", str(sheet_dir / "corrected_candidate.json")]) == 0
        sheet_ledger = sheet_dir / "decision_ledger.jsonl"

    gui_lines, sheet_lines = read_entries(gui_ledger), read_entries(sheet_ledger)
    result["entries"] = {"gui": len(gui_lines), "sheet": len(sheet_lines)}
    differing = set()
    for g, s in zip(gui_lines, sheet_lines):
        differing |= {k for k in {*g, *s} if g.get(k) != s.get(k)}
    result["keys_that_differ"] = sorted(differing)
    result["vias"] = {"gui": sorted({e["via"] for e in gui_lines}), "sheet": sorted({e["via"] for e in sheet_lines})}

    def normal(entry):
        entry = {**entry, "via": "x"}
        entry["entry_id"] = entry_id_of(entry)
        return entry

    result["equal_once_via_is_normalised_and_entry_id_recomputed"] = (
        len(gui_lines) == len(sheet_lines) and [normal(e) for e in gui_lines] == [normal(e) for e in sheet_lines])
    result["entry_id_includes_via"] = entry_id_of({**gui_lines[0], "via": "other"}) != gui_lines[0]["entry_id"]
    gui_bytes = (gui_dir / "corrected_candidate.json").read_bytes()
    sheet_bytes = (sheet_dir / "corrected_candidate.json").read_bytes()
    gui_json, sheet_json = json.loads(gui_bytes), json.loads(sheet_bytes)
    result["corrected_bytes_identical"] = gui_bytes == sheet_bytes
    result["corrected_equal_under_task4_comparison"] = _comparable(gui_json) == _comparable(sheet_json)
    result["corrected_top_level_keys_that_differ"] = sorted(k for k in {*gui_json, *sheet_json} if gui_json.get(k) != sheet_json.get(k))
    result["review_keys_that_differ"] = sorted(k for k in {*gui_json["review"], *sheet_json["review"]}
                                               if gui_json["review"].get(k) != sheet_json["review"].get(k))
    result["applied"] = {"gui": materialised_gui["applied"], "sheet": len(sheet_json["review"]["applied_entry_ids"])}
    result["note"] = "the sheet writes no prerequisite entries, so this covers the course fields only"
    return result


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    cli = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    cli.add_argument("--candidate", type=Path, required=True)
    cli.add_argument("--pdf", type=Path)
    cli.add_argument("--pdf-sha256")
    cli.add_argument("--docling-json", type=Path)
    cli.add_argument("--review-dir", type=Path, help="outside the repository; never the originals' review folder")
    cli.add_argument("--reviewer", default="smoke-script")
    cli.add_argument("--all-unresolved", action="store_true", help="also answer every question No in a throwaway ledger")
    cli.add_argument("--equivalence-dir", type=Path, help="run the GUI-vs-sheet equivalence into this folder instead")
    cli.add_argument("--json-out", type=Path)
    args = cli.parse_args(argv)
    if args.equivalence_dir:
        result = equivalence(args.candidate, args.pdf, args.equivalence_dir, docling_json=args.docling_json)
    else:
        if not args.review_dir:
            cli.error("--review-dir is required")
        result = run(args.candidate, args.pdf, args.review_dir, args.reviewer, pdf_sha256=args.pdf_sha256,
                     docling_json=args.docling_json, all_unresolved=args.all_unresolved)
    text = json.dumps(result, indent=2, ensure_ascii=True, default=str)
    if args.json_out:
        args.json_out.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
