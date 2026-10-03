"""Review sheet: one editable Markdown file per prospectus, and the step that turns it into ledger entries.

Layout: a header, then one block per section in printed order (health line, printed and extracted
units, `confirm`, `accept`, `reason`, and a table with one row per course). The reviewer edits only
the `decision`, `new code`, `new title` and `new term` columns and the `confirm`, `accept` and
`reason` lines. `apply` regenerates the expected sheet from the candidate and refuses a sheet whose
fixed text differs, so a stale or hand-edited sheet cannot write decisions.

decision cell:  ok | fix | fix a b | edit | unresolved   optionally followed by `: reason`
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Mapping, Sequence

from .fixes import FIELD_CODE, FIELD_TERM, FIELD_TITLE, Fix, format_term, parse_term
from .ledger import (ACCEPTED, CORRECTED, FIELD_ROW, FIELD_UNCLAIMED, UNRESOLVED, course_locator, course_snapshot,
                     make_entry, unclaimed_locator)
from .verify import Row, Section, Verification

SHEET_VERSION = "prospectus-review-sheet-v1"
COLUMNS = ["id", "code", "title", "units", "prereq", "flags", "proposal", "decision", "new code", "new title", "new term"]
FIXED = COLUMNS[:7]
FIX_KINDS = {"strip_banner", "move_term", "title_from_pdf"}
EDIT_FIELDS = {"new code": FIELD_CODE, "new title": FIELD_TITLE, "new term": FIELD_TERM}
VERBS = {"ok", "fix", "edit", "unresolved"}


def esc(text: Any) -> str:
    """One table cell: backslash and pipe escaped, line breaks flattened."""
    return " ".join(str(text if text is not None else "").split()).replace("\\", "\\\\").replace("|", "\\|")


def split_cells(line: str) -> list[str]:
    """Cells of one `| a | b |` line, honouring \\| and \\\\."""
    cells, cur, i, body = [], [], 0, line.strip()
    body = body[1:] if body.startswith("|") else body
    while i < len(body):
        ch = body[i]
        if ch == "\\" and i + 1 < len(body) and body[i + 1] in "\\|":
            cur.append(body[i + 1])
            i += 2
            continue
        if ch == "|":
            cells.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
        i += 1
    if "".join(cur).strip():
        cells.append("".join(cur).strip())
    return cells


def candidate_sha256(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def _flags_text(flags: Sequence[Any]) -> str:
    return "; ".join(f"{f.severity.upper()} {f.kind}: {f.message}" for f in flags)


def _proposal_text(fixes: Sequence[tuple[str, Fix]]) -> str:
    return "; ".join(f'{letter}) {fix.kind} {fix.field}: "{fix.old}" -> "{fix.new}"' for letter, fix in fixes)


def _row_cells(row: Row, payload: Mapping[str, Any]) -> list[str]:
    if row.course is None:
        item = row.item or {}
        return [row.rid, item.get("code", ""), "", "", "", _flags_text(row.flags), ""]
    course = payload["courses"][row.course]
    return [row.rid, course.get("course_code"), course.get("course_title"), (course.get("units") or {}).get("raw"),
            course.get("prerequisites_raw"), _flags_text(row.flags), _proposal_text(row.fixes)]


def _units_line(section: Section) -> str:
    return f"printed {section.declared if section.declared is not None else '-'}, extracted {section.computed}"


def render_sheet(payload: Mapping[str, Any], verification: Verification, identity: Mapping[str, Any]) -> str:
    counts = {h: sum(s.health == h for s in verification.sections) for h in ("clean", "review", "broken")}
    lines = [
        f"# Review sheet: {payload.get('program') or 'unnamed program'}", "",
        f"<!-- {SHEET_VERSION} -->",
        f"- pdf_sha256: {identity['pdf_sha256']}",
        f"- candidate_sha256: {identity['candidate_sha256']}",
        f"- pdf_text_checked: {'yes' if verification.pdf_checked else 'no'}",
        f"- prospectus health: {verification.health} ({counts['clean']} clean, {counts['review']} review, {counts['broken']} broken)",
        "",
        "Edit only the `decision`, `new code`, `new title` and `new term` columns and the `confirm`, `accept` and `reason` lines.",
        "decision: `ok` (as extracted) | `fix` (all proposals) | `fix a b` (named proposals) | `edit` (use the new columns) | `unresolved`;",
        "add `: reason` after it. `edit`, `unresolved` and `ok` on a printed code need a reason. `confirm: yes` accepts every unflagged row",
        "in the section; flagged rows still need their own decision. `accept: strip_banner, title_from_pdf, move_term, unclaimed` accepts",
        "that class of proposal for every undecided row of the section (give `reason:`). A blank decision writes nothing.",
        "A clean section here is clean on the checks that ran" + ("." if verification.pdf_checked else "; the PDF text was NOT checked."),
        "",
    ]
    for section in verification.sections:
        lines += [f"## {section.sid} - {section.title}", f"health: {section.health}", f"units: {_units_line(section)}",
                  f"flags: {_flags_text(section.flags)}".rstrip(), "confirm: no", "accept:", "reason:", "",
                  "| " + " | ".join(COLUMNS) + " |", "|" + "---|" * len(COLUMNS)]
        for row in section.rows:
            cells = [esc(c) for c in _row_cells(row, payload)] + [""] * (len(COLUMNS) - len(FIXED))
            lines.append("| " + " | ".join(cells) + " |")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


@dataclass
class ParsedSection:
    fixed: dict[str, str] = field(default_factory=dict)      # title, health, units, flags
    edits: dict[str, str] = field(default_factory=dict)      # confirm, accept, reason
    rows: dict[str, dict[str, str]] = field(default_factory=dict)
    lines: dict[str, int] = field(default_factory=dict)      # line number of each fixed/edit line and of the heading
    row_lines: dict[str, int] = field(default_factory=dict)  # line number of each row


@dataclass
class ParsedSheet:
    meta: dict[str, str] = field(default_factory=dict)
    meta_lines: dict[str, int] = field(default_factory=dict)
    sections: dict[str, ParsedSection] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


def at(number: int | None) -> str:
    """` (line 12)` for a message, empty when the line is unknown."""
    return f" (line {number})" if number else ""


def parse_sheet(text: str) -> ParsedSheet:
    """Parse a sheet as an editor may have saved it: any line ending, a UTF-8 BOM, spaces around lines and cells."""
    sheet, section, sid = ParsedSheet(), None, None
    text = text.lstrip("\ufeff")
    if f"<!-- {SHEET_VERSION} -->" not in text:
        sheet.errors.append(f"not a {SHEET_VERSION} file")
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if m := re.match(r"^## (S[0-9]+|SN|SU)\b", line):
            sid = m.group(1)
            if sid in sheet.sections:
                sheet.errors.append(f"line {number}: section {sid} appears twice (first on line {sheet.sections[sid].lines['title']})")
                section = ParsedSection()  # keep reading, but into a scratch section
                continue
            section = sheet.sections[sid] = ParsedSection()
            section.fixed["title"] = line
            section.lines["title"] = number
        elif section is None:
            if m := re.match(r"^- (pdf_sha256|candidate_sha256|pdf_text_checked|prospectus health):\s*(.*)$", line):
                sheet.meta[m.group(1)] = m.group(2).strip()
                sheet.meta_lines[m.group(1)] = number
            elif line.startswith("|"):
                sheet.errors.append(f"line {number}: a table row before the first section heading")
        elif m := re.match(r"^(health|units|flags):\s*(.*)$", line):
            section.fixed[m.group(1)] = m.group(2).strip()
            section.lines[m.group(1)] = number
        elif m := re.match(r"^(confirm|accept|reason):\s*(.*)$", line):
            section.edits[m.group(1)] = m.group(2).strip()
            section.lines[m.group(1)] = number
        elif line.startswith("|") and not re.match(r"^\|[\s\-|:]+$", line):
            cells = split_cells(line)
            if cells and cells[0] == "id":
                continue
            if len(cells) != len(COLUMNS):
                sheet.errors.append(f"line {number}: expected {len(COLUMNS)} columns, found {len(cells)}")
                continue
            if cells[0] in section.rows:
                sheet.errors.append(f"line {number}: row {cells[0]} appears twice (first on line {section.row_lines[cells[0]]})")
                continue
            section.rows[cells[0]] = dict(zip(COLUMNS, cells))
            section.row_lines[cells[0]] = number
    return sheet


def check_against(parsed: ParsedSheet, expected: ParsedSheet) -> list[str]:
    """Differences in everything the reviewer must not edit; every message names the line it found the problem on."""
    errors = list(parsed.errors)
    for key in ("pdf_sha256", "candidate_sha256", "pdf_text_checked", "prospectus health"):
        if parsed.meta.get(key) != expected.meta.get(key):
            errors.append(f"header {key} is {parsed.meta.get(key)!r}, expected {expected.meta.get(key)!r}{at(parsed.meta_lines.get(key))}; "
                          "this sheet was made from a different candidate or PDF: regenerate it")
    for sid in expected.sections.keys() - parsed.sections.keys():
        errors.append(f"section {sid} is missing from the sheet")
    for sid in parsed.sections.keys() - expected.sections.keys():
        errors.append(f"section {sid} is not in the candidate{at(parsed.sections[sid].lines.get('title'))}")
    owner = {rid: sid for sid, sec in expected.sections.items() for rid in sec.rows}
    present = {rid: sid for sid, sec in parsed.sections.items() for rid in sec.rows}
    for sid, want in expected.sections.items():
        have = parsed.sections.get(sid)
        if have is None:
            continue
        for key, value in want.fixed.items():
            if have.fixed.get(key) != value:
                errors.append(f"{sid}: {key} line was changed ({have.fixed.get(key)!r}, expected {value!r}){at(have.lines.get(key) or have.lines.get('title'))}")
        for rid in sorted(want.rows.keys() - have.rows.keys()):
            if present.get(rid) is None:
                errors.append(f"{rid}: row is missing")
        for rid in sorted(have.rows.keys() - want.rows.keys()):
            where = at(have.row_lines.get(rid))
            if rid in owner:
                errors.append(f"{rid}: row belongs in section {owner[rid]} but is in section {sid}{where}; "
                              "put it back, rows cannot move between sections")
            else:
                errors.append(f"{rid}: row is not in the candidate{where}")
        for rid, row in want.rows.items():
            for column in FIXED:
                if rid in have.rows and have.rows[rid][column] != row[column]:
                    errors.append(f"{rid}: column {column!r} was changed ({have.rows[rid][column]!r}, expected {row[column]!r}){at(have.row_lines.get(rid))}; "
                                  "use the new code / new title / new term columns to correct a value")
    return errors


def parse_decision(cell: str) -> tuple[str | None, list[str], str, str | None]:
    """(verb, proposal letters, reason, error) for one decision cell; verb None when blank."""
    text = cell.strip()
    if not text:
        return None, [], "", None
    head, _colon, reason = text.partition(":")
    tokens = [t for t in re.split(r"[\s,]+", head.strip().lower()) if t]
    verb, letters = tokens[0], tokens[1:]
    if verb not in VERBS:
        return None, [], "", f"unknown decision {tokens[0]!r}; use ok, fix, edit or unresolved"
    if letters and (verb != "fix" or any(not re.fullmatch(r"[a-z]", t) for t in letters)):
        return None, [], "", "only `fix` takes proposal letters, one letter each (fix a b)"
    return verb, letters, reason.strip(), None


def build_entries(
    parsed: ParsedSheet, payload: Mapping[str, Any], verification: Verification, *, reviewer: str, pdf_sha256: str,
    now: datetime | None = None,
) -> tuple[list[dict[str, Any]], list[str]]:
    """(entries, errors). Any error means no entries at all: a sheet is applied whole or not at all."""
    entries: list[dict[str, Any]] = []
    errors: list[str] = []
    for section in verification.sections:
        ps = parsed.sections[section.sid]
        confirm = ps.edits.get("confirm", "no").lower()
        classes = [c.strip() for c in ps.edits.get("accept", "").split(",") if c.strip()]
        section_reason = ps.edits.get("reason", "")
        if confirm not in ("yes", "no", ""):
            errors.append(f"{section.sid}: confirm must be yes or no, not {confirm!r}{at(ps.lines.get('confirm'))}")
        for name in classes:
            if name not in FIX_KINDS | {"unclaimed"}:
                errors.append(f"{section.sid}: accept lists unknown class {name!r}{at(ps.lines.get('accept'))}")
        if classes and not section_reason:
            errors.append(f"{section.sid}: accept needs a reason: line{at(ps.lines.get('reason') or ps.lines.get('accept'))}")
        for row in section.rows:
            cells = ps.rows[row.rid]
            where = at(ps.row_lines.get(row.rid))
            verb, letters, reason, problem = parse_decision(cells["decision"])
            edits = {name: cells[col] for col, name in EDIT_FIELDS.items() if cells[col]}
            if problem:
                errors.append(f"{row.rid}: {problem}{where}")
                continue
            via = "sheet"
            if verb is None:
                if edits:
                    errors.append(f"{row.rid}: a new value needs a decision (edit or fix){where}")
                    continue
                picked = [(l, f) for l, f in row.fixes if f.kind in classes]
                if picked:
                    verb, letters, reason, via = "fix", [l for l, _f in picked], section_reason, "section_accept"
                elif row.item is not None and "unclaimed" in classes:
                    verb, reason, via = "ok", section_reason, "section_accept"
                elif confirm == "yes" and row.worst() is None:
                    verb, reason, via = "ok", section_reason or "section confirmed as extracted", "section_confirm"
                elif confirm == "yes":
                    errors.append(f"{row.rid}: flagged but undecided in a confirmed section; decide it or leave confirm: no{where}")
                    continue
                else:
                    continue
            err = _row_entries(entries, row, section, payload, verb, letters, reason, edits, via, reviewer, pdf_sha256, now)
            errors += [f"{row.rid}: {e}{where}" for e in err]
    return ([] if errors else entries), errors


def _row_entries(entries, row, section, payload, verb, letters, reason, edits, via, reviewer, pdf_sha256, now) -> list[str]:
    def entry(locator, field_name, disposition, old, new, why, fix=None, rejected=()):
        return make_entry(reviewer=reviewer, reason=why, pdf_sha256=pdf_sha256, locator=locator, field=field_name,
                          disposition=disposition, old_value=old, new_value=new, section=section.title, fix_id=fix,
                          rejected_fixes=rejected, via=via, now=now)

    if row.course is None:  # an unclaimed printed code or an audit anomaly
        if verb not in ("ok", "unresolved"):
            return [f"a printed code can only be `ok` or `unresolved`, not {verb}"]
        if not reason:
            return [f"{verb} on a printed code needs a reason after the colon"]
        disposition = ACCEPTED if verb == "ok" else UNRESOLVED
        entries.append(entry(unclaimed_locator(row.item), FIELD_UNCLAIMED, disposition, row.item.get("code"), row.item.get("code"), reason))
        return []
    course = payload["courses"][row.course]
    locator, snapshot = course_locator(course), course_snapshot(course)
    if verb in ("ok", "unresolved") and edits:
        return [f"{verb} cannot carry new values"]
    if verb == "unresolved":
        if not reason:
            return ["unresolved needs a reason after the colon"]
        entries.append(entry(locator, FIELD_ROW, UNRESOLVED, snapshot, None, reason))
        return []
    if verb == "ok":
        entries.append(entry(locator, FIELD_ROW, ACCEPTED, snapshot, snapshot, reason or "accepted as extracted"))
        return []
    fixes = dict(row.fixes)
    chosen = [fixes[l] for l in letters if l in fixes] if letters else ([f for _l, f in row.fixes] if verb == "fix" else [])
    if letters and len(chosen) != len(letters):
        return [f"no proposal {', '.join(l for l in letters if l not in fixes)} on this row"]
    if verb == "fix" and not chosen:
        return ["fix: this row has no proposals"]
    if verb == "edit" and not edits:
        return ["edit: fill at least one of new code, new title, new term"]
    changes: dict[str, tuple[str, str, str | None]] = {f.field: (f.old, f.new, f.fix_id) for f in chosen}
    for name, value in edits.items():
        if name in changes:
            return [f"{name} is both proposed and edited"]
        if name == FIELD_TERM:
            parsed = parse_term(value, course.get("year_level"))
            if parsed is None:
                return [f"new term {value!r} is not a year and one semester, for example '2nd Year / 1st Semester'"]
            value = format_term(*parsed)
        if value == snapshot[name]:
            return [f"{name}: the new value equals the current one"]
        changes[name] = (snapshot[name], value, None)
    if edits and not reason:
        return ["edit needs a reason after the colon"]
    rejected = [f.fix_id for l, f in row.fixes if letters and l not in letters]
    entries.append(entry(locator, FIELD_ROW, ACCEPTED, snapshot, snapshot, "other fields accepted as extracted", rejected=rejected))
    for name in (FIELD_CODE, FIELD_TITLE, FIELD_TERM):
        if name in changes:
            old, new, fix_id = changes[name]
            entries.append(entry(locator, name, CORRECTED, old, new, reason or f"accepted proposal {fix_id.split(':')[0]}",
                                 fix=fix_id, rejected=rejected))
    return []