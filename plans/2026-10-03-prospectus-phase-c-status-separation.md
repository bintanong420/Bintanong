# Phase C: Separate Audit, Review, and Source States Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task, with superpowers:test-driven-development inside each task. Steps use checkbox (`- [ ]`) syntax. Tasks run through the project agents `extractor-implementer` and `extractor-reviewer`. Append to `plans/plan_current_progress/extractor_split_progress.md` after every task commit.

**Goal:** A machine audit of `ok` or `warn` can no longer be read as approval. The payload carries three distinct states (`extraction_audit`, `content_review`, `source_verification`), metadata is reported as observations with evidence, every course carries a prerequisite state, and courses whose prerequisite rule is not fully understood never satisfy `eligible/2` or `next_eligible/2`.

**Architecture:** Additive only. Existing course fields, audit fields, and `promotion_status` keep their values. New fields are computed after `finalize_courses` from data the parser already produces. A new small module `authority.py` assembles the three states and a `blocked_by` list; `prolog.py` gains a `rule_complete/1` guard that `eligible/2` requires. A source record reaches the pipeline through keyword-only optional parameters, so existing callers are unaffected.

**Tech Stack:** Python 3.13, pytest 9, stdlib only, `uv`. SWI-Prolog (`swipl`) is used by one test and that test skips when it is absent.

**Branch:** `feat/prospectus-phase-c-status-separation`, created from `dev` after Phase B has merged. Never `git add -A`; never stage `.gitignore` or `plans/CODEX_HANDOFF_prospectus_extractor_phase2_2026-09-26.md`.

**Line references** are to `8d26f18` (the commit this plan was written against). Phase B edits `pipeline.py`; Task 1 re-reads and corrects them.

---

## Decisions needed before execution

The rest of the plan assumes the recommendation in each row. Steps that would change are marked **[D#]**.

| # | Question | Options | Recommendation and why |
| --- | --- | --- | --- |
| D1 | What prerequisite-state vocabulary is honest? The outline proposes `reviewed_empty`, `unreadable`, `unresolved_reference`, `standing_condition`, `resolved`. | (a) Use exactly those five. (b) Emit only what the parser can tell apart, and reserve `reviewed_empty` for a human decision. (c) Change the parser to record blank-vs-missing cells. | **(b).** The parser cannot tell a printed-blank cell from a missing cell from an unreadable one: `_field_at` (`sections.py:179-183`) returns `None` for both "no cell" and "empty text", and `_candidate_to_raw_course` (`sections.py:1241`) turns `None` into `""`. So the extractor can never prove "reviewed empty". Emitted states: `resolved`, `stated_none` (the cell literally says none/-/n/a, i.e. printed evidence), `blank_unreviewed` (no text: printed blank, missing cell, or unread, indistinguishable), `standing_condition`, `unresolved_reference`, `alternative_or_exception` (OR/except/unless wording), `unreadable` (the audit flagged the cell as ambiguous, or text is present but nothing in it was recognised). `reviewed_empty` is in the vocabulary but is only ever written by the future review GUI. (c) is a parser change the outline does not ask for. **Consequence:** with extractor output alone, almost every first-year course (blank cell) is `blank_unreviewed`, so `eligible/2` offers almost nothing until a reviewer confirms the blanks. That is the point of "do not map unknown to zero". |
| D2 | Which states count as executable (a course in them may satisfy `eligible/2`)? | (a) `resolved` and `reviewed_empty` only (outline). (b) also `stated_none`. | **(b).** A printed "None" is source evidence of an empty rule, unlike a blank. `blank_unreviewed` stays excluded. If you prefer (a), delete `stated_none` from `EXECUTABLE_PREREQUISITE_STATES` in Task 2; nothing else changes. |
| D3 | The outline says a blocked audit must stop embedding candidate Prolog and RAG objects, as dropped or moved under `blocked_candidates`. | (a) Drop (current behavior, lock it with a test). (b) Move under `blocked_candidates`. | **(a), and nothing to build.** At `8d26f18`, `build_payload` already replaces Prolog with an empty `blocked` object and RAG with `[]` when `audit["status"] == "error"` (`pipeline.py:58-71`). The 44 cached outputs agree: 38 `error` payloads all have `prolog.status = blocked`, no clauses, no RAG chunks. The split plan's "still embeds" claim describes an older output. Phase C adds a regression test and adds the two new relation keys to the empty blocked object so its shape matches. Courses, `curriculum_by_term`, `prerequisite_edges`, and `unlocks` stay in blocked payloads: they are extraction candidates, not rule or RAG objects. |
| D4 | How does a source record reach the pipeline, and what happens on a hash mismatch? | (a) Keyword-only optional `source=` and `approved_scope=` on `build_payload` and `process_prospectus`, duck-typed; `process_prospectus` calls `source.verify_pdf()` and a mismatch raises `ValueError` before any output is touched. (b) Payload records the mismatch and carries on. (c) Import `ProvisionalSource` into the package. | **(a).** The package must keep running when started by path (`__main__.py` inserts `parents[1]` into `sys.path`), so it cannot import `backend.bintanong_tools.prospectus` with a relative import. Duck typing on `pdf_sha256`, `source_locator`, `source_verification`, `verify_pdf` avoids that. Raising matches draft Task 0 ("reject a declared hash that disagrees with the bytes") and Phase F's "refuses to run on a hash mismatch". The verify call sits before the stale-output unlink, so a mismatch also deletes nothing (Phase D later makes all publication safe). |
| D5 | `ProvisionalSource` has no scope, so "mismatched scope with an approved identity" needs an input for the approved identity. | (a) Optional `approved_scope: Mapping[str, str]` (keys such as `campus`, `college_code`, `program_name`) compared with observed metadata. (b) Wait for Phase 1 contracts. | **(a).** Tiny, optional, and Phase 1 can pass its approved identity through it later. No approved scope means identity is `pending`, which is a state, not an audit error. |
| D6 | Payload field shape. | (a) Three top-level strings plus one `authority` block holding source record, identity check, `eligibility_executable`, `blocked_by`, and a note. (b) One nested object. | **(a).** The outline says "three distinct payload fields"; strings are the easiest for GUI and manifest code to read. `promotion_status` is untouched and documented as non-approval, in code, in the payload note, and in a decision record. |
| D7 | Schema versions. | (a) `SCHEMA_VERSION` to `palsu-prospectus-v3.1`, essentials to `palsu-prospectus-essentials-v2`, manifest unchanged. (b) v4.0. | **(a).** All changes are additive; no field is removed or renamed. The batch manifest shape does not change. |
| D8 | Where do metadata observations live? | (a) `metadata["observations"]`, existing keys untouched. (b) New top-level key. | **(a).** `metadata` is already passed to every consumer of those values, and the compact essentials shape reads `payload["campus"]` and `payload["metadata"][...]`, which stay as they are. |

## What the outline got wrong or could not do against the real code

1. Blocked audits already drop candidate Prolog and RAG (D3). That scope item reduces to a regression test.
2. `reviewed_empty` and `unreadable` cannot be derived the way the outline implies (D1).
3. The outline says `source_verification` comes "from ProvisionalSource". `ProvisionalSource.source_verification` is fixed to `"pending"` and the record carries no scope, so identity comparison needs its own input (D5).
4. The 44 cached inputs are `*_docling.json`, not PDFs. They never exercise the hash check and never write `_essentials.json` (essentials are written only for `.pdf` input). The regression therefore proves course fields and payload shape; the hash check and essentials are covered by unit tests.
5. The existing `eligible/2` rule ignores standing requirements and unresolved prerequisite tokens entirely (it only checks `prerequisite/2` facts). Today `CC 4` with prerequisites `CS 9, CC 1` and `CS 9` unresolved is "eligible" once `CC 1` is passed. Phase C fixes this by the `rule_complete/1` guard.
6. `ambiguous_adjacent_prerequisite_fragment` is the only anomaly that names a prerequisite cell, and any anomaly makes the audit `error`. So the "audit flagged this cell" form of `unreadable` only appears in blocked payloads. In a payload the audit would have called `VERIFIED`, `unreadable` comes from "text present, nothing recognised" (for example a cell reading `Units`).
7. `parse_curriculum_evidence` already folds `or` into the unresolved-token list (the text `CC 1 or CS 2` yields prerequisites `CC 1, CS 2` plus unresolved `or`), which would execute as AND. The new `alternative_or_exception` state catches this by wording, independent of how tokens resolve.

## File structure

All new behavior sits next to the code it extends. Paths under `backend/bintanong_tools/prospectus_extractor/` unless noted.

| File | Change |
| --- | --- |
| `prerequisites.py` | Add the state vocabulary, `classify_prerequisite_state`, `annotate_prerequisite_states` (appended after `resolve_prerequisites`, line 215). |
| `prolog.py` | Emit `prerequisite_state/2` and `rule_complete/1`; `eligible/2` requires `rule_complete/1`; relations gain two keys; status comment. |
| `metadata.py` | `resolve_metadata` adds `metadata["observations"]` (lines 83-152). Values unchanged. |
| `authority.py` (new) | `check_identity`, `build_authority`. Pure functions, no I/O. |
| `pipeline.py` | `build_payload` and `process_prospectus` gain keyword-only parameters; annotate states; add authority fields; blocked relations shape; `build_essentials` additive fields; essentials schema string. |
| `audit.py` | Comment only, at `promotion_status` (line 274). |
| `common.py` | `SCHEMA_VERSION` bump (line 8). |
| `__init__.py` | Docstring note on status fields. |
| `tests/test_prospectus_authority.py` (new) | All Phase C tests. |
| `scripts/prospectus_status_compare.py` (new) | Two-sided field-level comparer for the 44-input regression. |
| `docs/decisions/prospectus-status-separation.md` (new) | Decision record. |
| `plans/plan_current_progress/extractor_split_progress.md` | Append a Phase C section. |

Not touched: `rag.py` (blocked audits already skip it; RAG source linking is Phase E), `loader.py`, `batch.py`, `cli.py`, `backend/bintanong_tools/prospectus.py` (read only; `ProvisionalSource` stays as is).

## Commands used throughout

PowerShell, repo root. (Git Bash is broken on this machine.)

```
# Full suite
uv run --project backend --extra tools --extra dev --with fastapi==0.141.1 python -m pytest -q tests

# Self-test (baseline 80/80)
uv run --project backend --extra tools --extra dev python -m backend.bintanong_tools.prospectus_extractor --self-test
```

`$GOLDEN` is `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\docling_jsonified_output\task2b_standing_isolated_2026-09-29` (44 `*_docling.json`). `$MAP` is `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\PalSU Undergraduate Prospectus Website Dump\Tiniguiban - Main\palsu_main_undergrad_program_college_meaning.md`.

Commit trailer for every commit in this plan: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

---

### Task 1: Start check

**Files:** read only, plus an append to the progress file.

- [ ] **Step 1: Branch and baseline**

```
git switch dev
git pull --ff-only
git log --oneline -5
git switch -c feat/prospectus-phase-c-status-separation
git rev-parse HEAD
```

Record the printed hash as `$BASE_REF`; Task 7 compares against it. Run both commands from "Commands used throughout". Record the passed count and `80/80` in the progress file. Any failure here is a stop-and-report.

- [ ] **Step 2: Remove the Phase A gate if it is still present**

```
Test-Path tests/test_prospectus_split_equivalence.py
```

Only Phase B should have hit this. If it prints `True`, delete it in this branch's first commit: `git rm tests/test_prospectus_split_equivalence.py` then `git commit -m "test: remove the Phase A equivalence gate"` (with the trailer). If `False`, do nothing.

- [ ] **Step 3: Re-read the touched code and correct line references**

Open these and confirm each anchor still exists. If Phase B moved one, note the new line in the progress file and use it for the rest of this plan.

| Anchor | Expected at `8d26f18` |
| --- | --- |
| `pipeline.py` `def build_payload(` | 25-31, parameters end with `repair_provider` |
| `pipeline.py` blocked Prolog object | 58-71 |
| `pipeline.py` `payload = {` ... `"audit": audit,` | 73-105 |
| `pipeline.py` `def build_essentials(` | 129-171 |
| `pipeline.py` `def process_prospectus(` and the `raise ValueError("Output must be a JSON file…")` | 174-203 |
| `prolog.py` `PROLOG_RULES` `eligible/2` | 33-36 |
| `prolog.py` `"relations": {` return | 181-189 |
| `metadata.py` `def resolve_metadata(` | 66-152 |
| `audit.py` `"promotion_status": ...` | 274 |
| `common.py` `SCHEMA_VERSION` | 8 |

Also check whether Phase B left a comparer script in `scripts/`; if one exists, Task 7 may reuse its `run` half but still needs the new `compare` rules.

- [ ] **Step 4: Prove the premise D3 is still true**

Run this probe (PowerShell). Expected output ends with `error blocked 0`.

```
$env:PYTHONPATH = (Get-Location).Path
@'
from pathlib import Path
from backend.bintanong_tools.prospectus_extractor.selftest import fixture_document, CS_HEADER, _cs_row, _merged, _cs_semester_row
from backend.bintanong_tools.prospectus_extractor.pipeline import build_payload
grid = [CS_HEADER, _merged("FIRST YEAR", 8), _cs_semester_row(),
        _cs_row(("CS 1", "A", "3", ""), ("CS 2", "B", "3", "CS 1")),
        _cs_row(("CS 1", "Dup", "3", ""))]
p = build_payload(fixture_document(grid, [("title", "BACHELOR OF SCIENCE IN TESTING")]), Path("x/x.pdf"), semantic_doc_path=None)
print(p["audit"]["status"], p["prolog"]["status"], len(p["rag"]["semantic_chunks"]))
'@ | Set-Content "$env:TEMP\c_probe.py" -Encoding utf8
uv run --project backend --extra tools --extra dev python "$env:TEMP\c_probe.py"
```

If a different result appears, stop: D3 changes and the plan needs a blocked-candidates task.

- [ ] **Step 5: Append the Phase C section to the progress file**

Add a heading `## Phase C: status separation` with the branch, `$BASE_REF`, baseline test counts, and any moved line references. Commit it:

```
git add plans/plan_current_progress/extractor_split_progress.md
git commit -m "docs: start Phase C progress notes"
```

---

### Task 2: Prerequisite state vocabulary and classifier (tests first)

**Files:**
- Create: `tests/test_prospectus_authority.py`
- Modify: `backend/bintanong_tools/prospectus_extractor/prerequisites.py` (append after line 215)

- [ ] **Step 1: Write the failing tests**

Create `tests/test_prospectus_authority.py`:

```python
"""Phase C: audit, content review, and source verification stay separate states.

A machine audit of ok or warn (legacy label VERIFIED) must never be enough to
produce executable eligibility.
"""

from __future__ import annotations

import pytest

from backend.bintanong_tools.prospectus_extractor.prerequisites import (
    EXECUTABLE_PREREQUISITE_STATES,
    PREREQUISITE_STATES,
    annotate_prerequisite_states,
    classify_prerequisite_state,
)


def course(raw, prereqs=(), unresolved=(), standing=(), cells=("t0-c1",)):
    return {
        "course_code": "X 1",
        "prerequisites_raw": raw,
        "prerequisites": list(prereqs),
        "prerequisites_unresolved": list(unresolved),
        "standing_requirements": list(standing),
        "provenance": {"source_cell_ids": list(cells)},
    }


STATE_CASES = [
    ("blank cell", course(""), "blank_unreviewed"),
    ("printed none", course("none"), "stated_none"),
    ("printed dash", course("-"), "stated_none"),
    ("one code", course("CS 1", ["CS 1"]), "resolved"),
    ("two codes", course("CS 1, CS 2", ["CS 1", "CS 2"]), "resolved"),
    ("standing only", course("Dean consent", standing=["Dean consent."]), "standing_condition"),
    ("code plus standing",
     course("CS 1, 70% of the units", ["CS 1"], standing=["70% of the units."]), "standing_condition"),
    ("unresolved token", course("CS 9", unresolved=["CS 9"]), "unresolved_reference"),
    ("or with leftover token", course("CS 1 or CS 2", ["CS 1", "CS 2"], unresolved=["or"]),
     "alternative_or_exception"),
    ("or that resolved fully", course("CS 1 or CS 2", ["CS 1", "CS 2"]), "alternative_or_exception"),
    ("exception wording",
     course("CS 1 except for transferees", ["CS 1"], unresolved=["except for transferees"]),
     "alternative_or_exception"),
    ("text present, nothing recognised", course("Units"), "unreadable"),
]


@pytest.mark.parametrize(("label", "record", "expected"), STATE_CASES, ids=[c[0] for c in STATE_CASES])
def test_prerequisite_state_of_one_course(label, record, expected):
    assert classify_prerequisite_state(record) == expected
    assert expected in PREREQUISITE_STATES


def test_audit_flagged_cell_is_unreadable_even_when_it_looks_resolved():
    record = course("CS 1", ["CS 1"], cells=("t0-c5", "t0-c6"))
    assert classify_prerequisite_state(record) == "resolved"
    assert classify_prerequisite_state(record, frozenset({"t0-c6"})) == "unreadable"


def test_only_complete_states_are_executable():
    assert EXECUTABLE_PREREQUISITE_STATES == {"resolved", "stated_none", "reviewed_empty"}
    # The extractor can not tell a blank from a missing cell, so it never emits reviewed_empty.
    emitted = {classify_prerequisite_state(record) for _label, record, _state in STATE_CASES}
    assert "reviewed_empty" not in emitted
    assert "blank_unreviewed" not in EXECUTABLE_PREREQUISITE_STATES


def test_annotate_marks_every_course_and_uses_only_prerequisite_anomalies():
    courses = [course("CS 1", ["CS 1"], cells=("t0-c5",)), course("", cells=("t0-c9",))]
    anomalies = [
        {"type": "ambiguous_adjacent_prerequisite_fragment", "source_cell_ids": ["t0-c5"]},
        {"type": "unclaimed_course_candidate", "source_cell_ids": ["t0-c9"]},
    ]
    annotate_prerequisite_states(courses, anomalies)
    assert [c["prerequisite_state"] for c in courses] == ["unreadable", "blank_unreviewed"]
```

- [ ] **Step 2: Run and confirm the failure**

Run: `uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_authority.py`
Expected: collection error `ImportError: cannot import name 'EXECUTABLE_PREREQUISITE_STATES'`. That is the right red.

- [ ] **Step 3: Implement**

Append to `prerequisites.py` after `resolve_prerequisites` (the file already imports `re`, `clean_str`, and defines `NULL_TOKENS`):

```python


# One state per course, describing how completely the extractor understood its
# prerequisite cell. The parser keeps no record of whether an empty cell was
# printed blank, missing, or unreadable (sections._field_at returns None for all
# three), so "reviewed_empty" is reserved for a human review decision and is
# never emitted here.
PREREQUISITE_STATES = (
    "resolved",
    "stated_none",
    "reviewed_empty",
    "blank_unreviewed",
    "standing_condition",
    "unresolved_reference",
    "alternative_or_exception",
    "unreadable",
)

# Only these may satisfy eligible/2. Everything else is excluded from executable rules.
EXECUTABLE_PREREQUISITE_STATES = frozenset({"resolved", "stated_none", "reviewed_empty"})

# Audit anomaly types that name a prerequisite cell the parser could not assign.
PREREQUISITE_AMBIGUITY_TYPES = frozenset({"ambiguous_adjacent_prerequisite_fragment"})

ALTERNATIVE_OR_EXCEPTION = re.compile(
    r"\b(?:or|either|except(?:ion|ing)?|unless|equivalent|provided|if)\b", re.IGNORECASE
)


def classify_prerequisite_state(course: dict, ambiguous_cell_ids: frozenset = frozenset()) -> str:
    """Worst-case state of one finalized course; the order below is the precedence."""
    raw = clean_str(course.get("prerequisites_raw"))
    cells = set((course.get("provenance") or {}).get("source_cell_ids") or ())
    if cells & ambiguous_cell_ids:
        return "unreadable"
    if ALTERNATIVE_OR_EXCEPTION.search(raw):
        return "alternative_or_exception"
    if course.get("prerequisites_unresolved"):
        return "unresolved_reference"
    if course.get("standing_requirements"):
        return "standing_condition"
    if not raw:
        return "blank_unreviewed"
    if raw.lower() in NULL_TOKENS:
        return "stated_none"
    if not course.get("prerequisites"):
        return "unreadable"  # text was printed but nothing in it was recognised
    return "resolved"


def annotate_prerequisite_states(courses, anomalies=()) -> None:
    """Set course['prerequisite_state'] on every course, in place."""
    ambiguous = frozenset(
        cell_id
        for anomaly in anomalies
        if anomaly.get("type") in PREREQUISITE_AMBIGUITY_TYPES
        for cell_id in anomaly.get("source_cell_ids", ())
    )
    for item in courses:
        item["prerequisite_state"] = classify_prerequisite_state(item, ambiguous)
```

- [ ] **Step 4: Run and confirm green**

Run: `uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_authority.py`
Expected: all pass (15 items: 12 parametrized states plus 3 functions).

- [ ] **Step 5: Mutation check (tests must be able to fail)**

Temporarily change `if raw.lower() in NULL_TOKENS:` to `if False:` and rerun. Expected: the two `stated_none` cases fail. Revert.

- [ ] **Step 6: Commit and record**

```
git add tests/test_prospectus_authority.py backend/bintanong_tools/prospectus_extractor/prerequisites.py
git commit -m "feat: classify each course's prerequisite state"
```

Append "Task 2 done, commit <hash>, N passed" to the progress file (stage it by explicit path, amend nothing; a separate `docs:` commit is fine).

---

### Task 3: Prolog excludes incomplete rules; states reach the payload (tests first)

**Files:**
- Modify: `tests/test_prospectus_authority.py` (append)
- Modify: `backend/bintanong_tools/prospectus_extractor/prolog.py` (lines 9, 33-36, 78-87, 139-153, 181-189)
- Modify: `backend/bintanong_tools/prospectus_extractor/pipeline.py` (import, annotate call, blocked relations)

This task covers draft cases 4 to 7 (unreadable cell, unresolved token, standing-only, `OR`/exception) and locks D3.

- [ ] **Step 1: Write the failing tests**

Add to the imports at the top of `tests/test_prospectus_authority.py`:

```python
import shutil
import subprocess
from pathlib import Path

from backend.bintanong_tools.prospectus_extractor.pipeline import build_payload
from backend.bintanong_tools.prospectus_extractor.prolog import generate_prolog_knowledge
from backend.bintanong_tools.prospectus_extractor.selftest import (
    CS_HEADER, _cs_row, _cs_semester_row, _merged, fixture_document,
)
```

Append:

```python
def payload_for(rows, **kwargs):
    grid = [CS_HEADER, _merged("FIRST YEAR", 8), _cs_semester_row(), *rows]
    document = fixture_document(grid, [("title", "BACHELOR OF SCIENCE IN COMPUTER SCIENCE PROGRAM")])
    return build_payload(document, Path("local/x.pdf"), semantic_doc_path=None, **kwargs)


# CS 1 has a blank cell; CS 2 requires exactly CS 1, so its rule is complete.
CONTROL = _cs_row(("CS 1", "Discrete Structures", "3", ""), ("CS 2", "Discrete Structures 2", "3", "CS 1"))


def one_case(cell):
    return _cs_row(("CC 1", "Intro to Computing", "3", cell))


@pytest.mark.parametrize(
    ("cell", "state"),
    [
        ("Units", "unreadable"),
        ("CS 9", "unresolved_reference"),
        ("Dean consent", "standing_condition"),
        ("CS 1 or CS 2", "alternative_or_exception"),
        ("CS 1 except transferees", "alternative_or_exception"),
    ],
)
def test_incomplete_prerequisite_rule_is_not_executable_even_when_audit_says_verified(cell, state):
    payload = payload_for([CONTROL, one_case(cell)])
    # Precondition: the legacy label says go. Without it this test proves nothing.
    assert payload["audit"]["status"] != "error"
    assert payload["audit"]["promotion_status"] == "VERIFIED"

    by_code = {c["course_code"]: c for c in payload["courses"]}
    assert by_code["CC 1"]["prerequisite_state"] == state
    clauses = payload["prolog"]["clauses"]
    assert "rule_complete('CC 1')." not in clauses
    assert "CC 1" not in payload["prolog"]["relations"]["rule_complete"]
    # Control: a fully understood rule still counts, so the exclusion is not blanket.
    assert by_code["CS 2"]["prerequisite_state"] == "resolved"
    assert "rule_complete('CS 2')." in clauses
    # A blank cell is unreviewed, not an empty rule.
    assert by_code["CS 1"]["prerequisite_state"] == "blank_unreviewed"
    assert "rule_complete('CS 1')." not in clauses
    assert payload["authority"]["eligibility_executable"] is False


def test_courses_without_a_state_are_never_complete():
    record = {
        "course_code": "X 1", "course_title": "T", "units": {"total": 3, "lecture": 3, "lab": 0},
        "year_level": "1st Year", "semester": "1st Semester", "category": "Core / Major",
        "prerequisites": [], "standing_requirements": [],
    }
    knowledge = generate_prolog_knowledge({}, [record], [], [])
    assert knowledge["relations"]["rule_complete"] == []
    assert knowledge["relations"]["prerequisite_states"] == [{"course": "X 1", "state": "unclassified"}]


@pytest.mark.skipif(shutil.which("swipl") is None, reason="SWI-Prolog is not installed")
def test_next_eligible_only_offers_courses_with_complete_rules(tmp_path):
    payload = payload_for([
        CONTROL,
        _cs_row(("CC 1", "Intro to Computing", "3", "CS 1 or CS 2"), ("CC 2", "Other", "3", "CS 1")),
        _cs_row(("CC 3", "Third", "3", "Dean consent")),
    ])
    kb = tmp_path / "kb.pl"
    kb.write_text("\n".join(payload["prolog"]["clauses"]) + "\n", encoding="utf-8", newline="\n")

    def next_eligible(passed):
        driver = tmp_path / "driver.pl"
        driver.write_text(
            f":- consult('{kb.as_posix()}').\n"
            f"main :- findall(C, next_eligible({passed}, C), L), format(\"~q~n\", [L]).\n"
            ":- initialization(main, main).\n",
            encoding="utf-8", newline="\n",
        )
        done = subprocess.run(["swipl", "-q", str(driver)], capture_output=True, text=True, encoding="utf-8")
        assert done.returncode == 0, done.stderr
        return done.stdout.strip()

    assert next_eligible("[]") == "[]"  # CS 1 is blank (unreviewed); CC 2 needs CS 1
    # CC 1 (OR) and CC 3 (standing) are never offered; CC 2 (resolved, CS 1 passed) is.
    assert next_eligible("['CS 1','CS 2']") == "['CC 2']"


def test_blocked_audit_drops_candidate_prolog_and_rag():
    payload = payload_for([CONTROL, _cs_row(("CS 1", "Duplicate code", "3", ""))])
    assert payload["audit"]["status"] == "error"
    assert payload["prolog"]["status"] == "blocked"
    assert payload["prolog"]["clauses"] == []
    assert payload["prolog"]["relations"] == {
        "courses": [], "prerequisites": [], "standing_requirements": [], "elective_tracks": [],
        "prerequisite_states": [], "rule_complete": [],
    }
    assert payload["rag"] == {"semantic_chunks": [], "hierarchical_chunks": []}
    assert "blocked_candidates" not in payload
```

- [ ] **Step 2: Run and confirm the failures**

Run: `uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_authority.py`
Expected: the five parametrized cases fail with `KeyError: 'prerequisite_state'`; `test_courses_without_a_state_are_never_complete` fails with `KeyError: 'rule_complete'`; the swipl test fails (`next_eligible([])` returns `['CS 1', ...]`, not `[]`); the blocked test fails on the relations dict (missing two keys). Task 2 tests stay green. If `eligibility_executable` raises `KeyError: 'authority'`, that is expected here; it passes in Task 5.

- [ ] **Step 3: Edit `prolog.py`**

(a) Replace line 9-13 imports so the executable set is available:

```python
from .common import RICH_AVAILABLE, SCHEMA_VERSION

if RICH_AVAILABLE:
    from .common import track
from .prerequisites import EXECUTABLE_PREREQUISITE_STATES
from .text import clean_str
```

(b) In `PROLOG_RULES`, replace the `eligible/2` block (lines 33-36) with:

```
% eligible(+Course, +PassedCodes): the prerequisite rule is complete and every
% prerequisite has been passed. A course without rule_complete/1 never qualifies.
eligible(Course, Passed) :-
    rule_complete(Course),
    course(Course, _, _, _, _, _, _, _),
    \\+ ( prerequisite(Course, Prereq), \\+ memberchk(Prereq, Passed) ).
```

(c) In the header, after `add("% Source: ...")` and before the closing `% ====` banner add:

```python
    add("% STATUS: review candidate. rule_complete/1 lists courses whose prerequisite cell the")
    add("% extractor fully understood; eligible/2 needs it. Nothing here is approved for active use.")
```

and after `add(":- discontiguous term_units/3.")` add:

```python
    add(":- discontiguous prerequisite_state/2.")
    add(":- dynamic rule_complete/1.")
```

(`dynamic` makes `rule_complete/1` defined even when no clause follows, so `eligible/2` fails instead of raising an existence error.)

(d) After the `standing_requirement` block (after the loop that ends at line 152) insert:

```python
    add("")
    add("% prerequisite_state(Course, State): how fully the extractor understood the prerequisite cell.")
    relational_states: list[dict[str, str]] = []
    complete: list[str] = []
    for course in courses:
        state = course.get("prerequisite_state", "unclassified")
        add(f"prerequisite_state({pl_atom(course['course_code'])}, {pl_atom(state)}).")
        relational_states.append({"course": course["course_code"], "state": state})
        if state in EXECUTABLE_PREREQUISITE_STATES:
            complete.append(course["course_code"])
    add("")
    add("% rule_complete(Course): the prerequisite rule is fully understood; eligible/2 requires it.")
    for code in complete:
        add(f"rule_complete({pl_atom(code)}).")
```

(e) In the returned `relations` dict add two keys after `"elective_tracks"`:

```python
            "prerequisite_states": relational_states,
            "rule_complete": complete,
```

- [ ] **Step 4: Edit `pipeline.py`**

Import: change the `courses` line neighbourhood to add

```python
from .prerequisites import annotate_prerequisite_states
```

Immediately after `tracks = link_elective_tracks(...)` (line 47) add:

```python
    annotate_prerequisite_states(courses, parse.anomalies)
```

In the blocked Prolog object (lines 59-69) extend `relations`:

```python
            "relations": {
                "courses": [],
                "prerequisites": [],
                "standing_requirements": [],
                "elective_tracks": [],
                "prerequisite_states": [],
                "rule_complete": [],
            },
```

Note `annotate_prerequisite_states` runs before `build_audit`; it only adds a key the audit never reads.

- [ ] **Step 5: Run and confirm the progress**

Run: `uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_authority.py`
Expected: everything passes except the `payload["authority"]["eligibility_executable"]` line inside the five parametrized cases (`KeyError: 'authority'`). That assertion belongs to Task 5: move it out of these cases into a separate test `test_authority_block_blocks_eligibility` that is written as Task 5's red step. Do not comment out assertions and do not commit a failing test; every commit in this phase must leave the full suite green. If `swipl` is present, the swipl test must pass here.

- [ ] **Step 6: Mutation check**

Remove `rule_complete(Course),` from the new `eligible/2` and rerun the swipl test. Expected: it fails (`CC 1` and `CC 3` appear). Restore.

- [ ] **Step 7: Self-test and commit**

Run the self-test command. Expected: `80/80`. Then:

```
git add tests/test_prospectus_authority.py backend/bintanong_tools/prospectus_extractor/prolog.py backend/bintanong_tools/prospectus_extractor/pipeline.py
git commit -m "feat: keep incomplete prerequisite rules out of eligible/2"
```

(If you left the `authority` assertion failing, commit after Task 5 instead and say so in the progress file.)

---

### Task 4: Metadata as observations with evidence (tests first)

**Files:**
- Modify: `tests/test_prospectus_authority.py` (append)
- Modify: `backend/bintanong_tools/prospectus_extractor/metadata.py` (`resolve_metadata`, lines 83-152)

Existing keys and values do not change, including the hardcoded campus.

- [ ] **Step 1: Write the failing tests**

Add to the test imports: `from backend.bintanong_tools.prospectus_extractor.metadata import resolve_metadata`.

Append:

```python
SEMANTIC_MAP = {
    "CS": {
        "name": "College of Sciences",
        "programs": [
            {"program_name": "Bachelor of Science in Computer Science", "degree": "BS Computer Science"}
        ],
    }
}


def test_metadata_keeps_its_values_and_adds_observations_with_evidence():
    metadata, _warnings = resolve_metadata(
        Path("Tiniguiban - Main/CS/bscs.pdf"),
        doc_text="BACHELOR OF SCIENCE IN COMPUTER SCIENCE Effective SY 2025-2026",
        semantic_map=SEMANTIC_MAP,
    )
    assert metadata["campus"] == "Tiniguiban - Main"          # unchanged value
    assert metadata["college_code"] == "CS"
    assert metadata["program_name"] == "Bachelor of Science in Computer Science"
    assert metadata["effective_school_year"] == "2025-2026"

    seen = metadata["observations"]
    assert seen["campus"] == {
        "value": "Tiniguiban - Main", "basis": "extractor_default", "evidence": None, "status": "candidate",
    }
    assert seen["college_code"] == {
        "value": "CS", "basis": "path_segment", "evidence": "CS", "status": "candidate",
    }
    assert seen["program_name"]["basis"] == "semantic_map_match"
    assert seen["program_name"]["evidence"] == "Bachelor of Science in Computer Science"
    assert seen["effective_school_year"]["basis"] == "path_or_document_head"
    assert seen["effective_school_year"]["evidence"] == "Effective SY 2025-2026"
    assert all(item["status"] == "candidate" for item in seen.values())


def test_unknown_metadata_has_no_basis_and_the_same_warnings_as_before():
    metadata, warnings = resolve_metadata(Path("unknown/x.pdf"), doc_text="", semantic_map={})
    assert len(warnings) == 3
    seen = metadata["observations"]
    for name in ("college_code", "program_name", "effective_school_year"):
        assert seen[name] == {"value": None, "basis": None, "evidence": None, "status": "candidate"}
    assert seen["campus"]["basis"] == "extractor_default"  # still an assumption, now labelled as one
```

- [ ] **Step 2: Run and confirm the failure**

Run: `uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_authority.py -k metadata`
Expected: both fail with `KeyError: 'observations'`.

- [ ] **Step 3: Implement in `metadata.py`**

In `resolve_metadata`, after `college_name = None` (line 84) add `college_basis = college_evidence = None`. In the two college branches record the basis:

```python
    for part in Path(source_path).parts:
        if part in semantic_map:
            college_code, college_name = part, semantic_map[part]["name"]
            college_basis, college_evidence = "path_segment", part
            break
    if not college_code:
        for code, info in semantic_map.items():
            if re.search(rf"(?<![A-Za-z]){re.escape(code)}(?![A-Za-z])", path_str):
                college_code, college_name = code, info["name"]
                college_basis, college_evidence = "path_pattern", code
                break
```

Before the program loop add `program_basis = program_evidence = None`. Replace the semantic-map match body with:

```python
            if name.lower() in haystack.lower() or (len(abbrev) > 4 and abbrev.lower() in haystack.lower()):
                program_name, degree = name, abbrev
                program_basis = "semantic_map_match"
                program_evidence = name if name.lower() in haystack.lower() else abbrev
                if not college_code:
                    college_basis, college_evidence = "semantic_map_program_match", name
                college_code = college_code or code
                college_name = college_name or info["name"]
                break
```

In the heading fallback, after `degree = derive_degree_code(program_name)` add:

```python
            program_basis, program_evidence = "document_heading", clean_str(match.group(1))
```

After the `sy_match` computation (line 128) add:

```python
    sy_evidence = clean_str(sy_match.group(0)) if sy_match else None
```

Before `metadata = {` define the helper, and add the last key to the dict (as its final entry, so existing key order is untouched):

```python
    def observed(value, basis, evidence):
        return {
            "value": value,
            "basis": basis if value else None,
            "evidence": evidence if value else None,
            "status": "candidate",
        }
```

```python
        "observations": {
            "campus": observed("Tiniguiban - Main", "extractor_default", None),
            "college_code": observed(college_code, college_basis, college_evidence),
            "program_name": observed(program_name, program_basis, program_evidence),
            "effective_school_year": observed(school_year, "path_or_document_head", sy_evidence),
        },
```

Do not change `"campus": "Tiniguiban - Main"` or any other existing key. (A later phase may add `source_kind: "ocr"` and per-cell confidence to these records; the dict leaves room.)

- [ ] **Step 4: Run, self-test, commit**

Run the two metadata tests (expect pass), the whole authority file, and the self-test (`80/80`).

```
git add tests/test_prospectus_authority.py backend/bintanong_tools/prospectus_extractor/metadata.py
git commit -m "feat: report metadata as candidate observations with evidence"
```

Append to the progress file.

---

### Task 5: Authority block, source plumbing, essentials, schema bump (tests first)

**Files:**
- Create: `backend/bintanong_tools/prospectus_extractor/authority.py`
- Modify: `backend/bintanong_tools/prospectus_extractor/pipeline.py`
- Modify: `backend/bintanong_tools/prospectus_extractor/common.py:8`
- Modify: `tests/test_prospectus_authority.py` (append)

Covers draft cases 1 to 3 (mismatched scope with an approved identity, pending identity, hash mismatch) and makes the Task 3 `authority` assertion pass.

- [ ] **Step 1: Write the failing tests**

Add to the test imports:

```python
import hashlib
import json

from backend.bintanong_tools.prospectus import ProvisionalSource
from backend.bintanong_tools.prospectus_extractor import pipeline
from backend.bintanong_tools.prospectus_extractor.common import SCHEMA_VERSION
```

Append:

```python
def test_mismatched_scope_with_an_approved_identity_blocks_eligibility():
    payload = payload_for([CONTROL], approved_scope={"campus": "Elsewhere Campus"})
    assert payload["audit"]["promotion_status"] == "VERIFIED"
    identity = payload["authority"]["identity_check"]
    assert identity["state"] == "mismatch"
    assert identity["mismatched_fields"] == ["campus"]
    assert "identity_mismatch" in payload["authority"]["blocked_by"]
    assert payload["authority"]["eligibility_executable"] is False
    # The parser's campus is still reported, but only as a labelled observation.
    assert payload["campus"] == "Tiniguiban - Main"
    assert payload["metadata"]["observations"]["campus"]["basis"] == "extractor_default"


def test_pending_identity_is_a_state_not_an_audit_error():
    with_scope = payload_for([CONTROL], approved_scope={"campus": "Tiniguiban - Main"})
    pending = payload_for([CONTROL])
    assert pending["authority"]["identity_check"] == {
        "state": "pending", "approved_scope": None, "mismatched_fields": [],
    }
    assert "identity_pending" in pending["authority"]["blocked_by"]
    assert pending["audit"]["errors"] == [] and pending["audit"]["errors"] == with_scope["audit"]["errors"]
    assert pending["audit"]["warnings"] == with_scope["audit"]["warnings"]
    assert pending["authority"]["eligibility_executable"] is False


def test_a_consistent_identity_alone_still_does_not_authorize():
    payload = payload_for([CONTROL], approved_scope={"campus": "Tiniguiban - Main"})
    assert payload["authority"]["identity_check"]["state"] == "consistent"
    assert "identity_pending" not in payload["authority"]["blocked_by"]
    assert "content_review_pending" in payload["authority"]["blocked_by"]
    assert payload["authority"]["eligibility_executable"] is False


def test_three_states_are_separate_fields_and_promotion_status_is_unchanged():
    payload = payload_for([CONTROL])
    assert payload["schema_version"] == SCHEMA_VERSION == "palsu-prospectus-v3.1"
    assert payload["extraction_audit"] == payload["audit"]["status"] == "warn"
    assert payload["content_review"] == "pending"
    assert payload["source_verification"] == "pending"
    assert payload["audit"]["promotion_status"] == "VERIFIED"           # kept for compatibility
    assert payload["quality_report"]["promotion_status"] == "VERIFIED"
    assert "not approval" in payload["authority"]["note"]
    assert payload["authority"]["source_record"] is None


def test_source_record_is_carried_but_not_trusted_without_a_hash_check():
    source = ProvisionalSource("0" * 64, "local/x.pdf")
    payload = payload_for([CONTROL], source=source)
    assert payload["source_verification"] == "pending"
    assert payload["authority"]["source_record"] == {
        "pdf_sha256": "0" * 64, "source_locator": "local/x.pdf", "pdf_hash_check": "not_checked",
    }
    assert "pdf_hash_not_checked" in payload["authority"]["blocked_by"]
    assert payload["authority"]["eligibility_executable"] is False


def test_hash_mismatch_raises_before_any_output_is_touched(tmp_path):
    pdf = tmp_path / "prospectus.pdf"
    pdf.write_bytes(b"%PDF-1.4\nchanged bytes")
    out = tmp_path / "x_prospectus.json"
    out.write_text("previous accepted output", encoding="utf-8")
    source = ProvisionalSource(hashlib.sha256(b"%PDF-1.4\noriginal").hexdigest(), "local/prospectus.pdf")
    with pytest.raises(ValueError, match="hash mismatch"):
        pipeline.process_prospectus(pdf, output_path=out, semantic_doc_path=None, quiet=True, source=source)
    assert out.read_text(encoding="utf-8") == "previous accepted output"
    assert not (tmp_path / "x_essentials.json").exists()


def test_matching_hash_is_recorded_and_still_does_not_authorize(tmp_path, monkeypatch):
    pdf = tmp_path / "prospectus.pdf"
    pdf.write_bytes(b"%PDF-1.4\noriginal")
    source = ProvisionalSource(hashlib.sha256(b"%PDF-1.4\noriginal").hexdigest(), "local/prospectus.pdf")
    grid = [CS_HEADER, _merged("FIRST YEAR", 8), _cs_semester_row(), CONTROL]
    document = fixture_document(grid, [("title", "BACHELOR OF SCIENCE IN COMPUTER SCIENCE PROGRAM")])
    monkeypatch.setattr(pipeline, "load_document", lambda *args, **kwargs: (document, None))
    out = tmp_path / "x_prospectus.json"

    payload = pipeline.process_prospectus(pdf, output_path=out, semantic_doc_path=None, quiet=True, source=source)

    assert payload["authority"]["source_record"]["pdf_hash_check"] == "matched"
    assert "pdf_hash_not_checked" not in payload["authority"]["blocked_by"]
    assert payload["authority"]["eligibility_executable"] is False
    essentials = json.loads((tmp_path / "x_essentials.json").read_text(encoding="utf-8"))
    assert essentials["schema_version"] == "palsu-prospectus-essentials-v2"
    assert essentials["extraction_status"] == "VERIFIED"                # legacy field still present
    assert essentials["extraction_audit"] == "warn"
    assert essentials["content_review"] == "pending"
    assert essentials["source_verification"] == "pending"
    assert essentials["eligibility_executable"] is False
    assert all("prerequisite_state" in item for item in essentials["courses"])
    assert essentials["campus"] == "Tiniguiban - Main"                  # compact shape unchanged
```

- [ ] **Step 2: Run and confirm the failures**

Run: `uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_authority.py`
Expected: the new tests fail with `TypeError: build_payload() got an unexpected keyword argument 'approved_scope'` (or `source`), and the Task 3 parametrized cases still fail on `KeyError: 'authority'`.

- [ ] **Step 3: Create `authority.py`**

```python
"""Keeps the extractor's audit, content review, and source verification as separate states.

Nothing here approves anything. The extractor can only ever report content review
as pending, so eligibility_executable is False for every payload it produces.
"""

from __future__ import annotations

from typing import Any
from typing import Mapping
from typing import Sequence

from .prerequisites import EXECUTABLE_PREREQUISITE_STATES
from .text import clean_str


def check_identity(
    metadata: Mapping[str, Any], approved_scope: Mapping[str, str] | None
) -> dict[str, Any]:
    """Compare observed metadata with an approved identity, when one was supplied."""
    if not approved_scope:
        return {"state": "pending", "approved_scope": None, "mismatched_fields": []}
    mismatched = [
        name
        for name, wanted in approved_scope.items()
        if clean_str(wanted).casefold() != clean_str(metadata.get(name)).casefold()
    ]
    return {
        "state": "mismatch" if mismatched else "consistent",
        "approved_scope": dict(approved_scope),
        "mismatched_fields": mismatched,
    }


def build_authority(
    *,
    audit_status: str,
    metadata: Mapping[str, Any],
    courses: Sequence[Mapping[str, Any]],
    source: Any = None,
    approved_scope: Mapping[str, str] | None = None,
    pdf_hash_check: str = "not_checked",
) -> dict[str, Any]:
    """The three status fields plus the `authority` block, ready to merge into a payload.

    `source` is duck-typed (pdf_sha256, source_locator, source_verification) so the
    package does not import the tools adapter that defines ProvisionalSource.
    """
    identity = check_identity(metadata, approved_scope)
    verification = getattr(source, "source_verification", "pending")
    record = None
    if source is not None:
        record = {
            "pdf_sha256": source.pdf_sha256,
            "source_locator": source.source_locator,
            "pdf_hash_check": pdf_hash_check,
        }

    blocked: list[str] = []
    if audit_status == "error":
        blocked.append("extraction_audit_error")
    blocked.append("content_review_pending")  # the extractor never reviews content
    if verification == "pending":
        blocked.append("source_verification_pending")
    if pdf_hash_check != "matched":
        blocked.append("pdf_hash_not_checked")
    if identity["state"] == "pending":
        blocked.append("identity_pending")
    elif identity["state"] == "mismatch":
        blocked.append("identity_mismatch")
    incomplete = [
        item for item in courses if item.get("prerequisite_state") not in EXECUTABLE_PREREQUISITE_STATES
    ]
    if incomplete:
        blocked.append("prerequisite_rules_incomplete")

    return {
        "extraction_audit": audit_status,
        "content_review": "pending",
        "source_verification": verification,
        "authority": {
            "source_record": record,
            "identity_check": identity,
            "eligibility_executable": not blocked,
            "blocked_by": blocked,
            "courses_with_incomplete_prerequisite_rule": len(incomplete),
            "note": (
                "audit.promotion_status is a legacy extractor label, not approval of the curriculum, "
                "the source, or any eligibility result. Read extraction_audit, content_review and "
                "source_verification."
            ),
        },
    }
```

- [ ] **Step 4: Edit `pipeline.py`**

Imports: add `from .authority import build_authority`.

`build_payload` signature: after `repair_provider: SemanticRepairProvider | None = None,` add

```python
    *,
    source: Any = None,
    approved_scope: Mapping[str, str] | None = None,
    pdf_hash_check: str = "not_checked",
```

(`Mapping` and `Any` are already imported.) Update the docstring's second line: `"""Evidence -> audited payload. Production artifacts require a passing audit; no state here is approval."""`.

After `audit = build_audit(...)` / `term_units = ...` add:

```python
    authority = build_authority(
        audit_status=audit["status"], metadata=metadata, courses=courses,
        source=source, approved_scope=approved_scope, pdf_hash_check=pdf_hash_check,
    )
```

In the `payload = {` literal add `**authority,` as the line directly after `"audit": audit,`.

`build_essentials`: after `"extraction_status": payload["audit"]["promotion_status"],` add

```python
        "extraction_audit": payload["extraction_audit"],
        "content_review": payload["content_review"],
        "source_verification": payload["source_verification"],
        "eligibility_executable": payload["authority"]["eligibility_executable"],
```

change `"schema_version": "palsu-prospectus-essentials-v1",` to `"palsu-prospectus-essentials-v2"`, and add `"prerequisite_state": course["prerequisite_state"],` after the `"standing_requirements"` entry in the per-course dict.

`process_prospectus` signature: after `quiet: bool = False,` add

```python
    *,
    source: Any = None,
    approved_scope: Mapping[str, str] | None = None,
```

Directly after the `raise ValueError("Output must be a JSON file distinct from the source")` block (line 203), before `base = ...`, add:

```python
    pdf_hash_check = "not_checked"
    if source is not None and input_path.suffix.lower() == ".pdf":
        source.verify_pdf(input_path)  # raises ValueError on a hash mismatch, before any output is touched
        pdf_hash_check = "matched"
```

and pass `source=source, approved_scope=approved_scope, pdf_hash_check=pdf_hash_check` in the `build_payload(...)` call there.

- [ ] **Step 5: Bump the schema version**

`common.py` line 8: `SCHEMA_VERSION = "palsu-prospectus-v3.1"`. Leave `MANIFEST_SCHEMA_VERSION` alone (**[D7]**).

- [ ] **Step 6: Run everything**

```
uv run --project backend --extra tools --extra dev --with fastapi==0.141.1 python -m pytest -q tests
uv run --project backend --extra tools --extra dev python -m backend.bintanong_tools.prospectus_extractor --self-test
```

Expected: all tests pass (including the Task 3 parametrized cases, now that `authority` exists), `80/80`. If `tests/test_prospectus_entrypoints.py` fails on the shim re-export check, read the message: the shim copies every public module name, and `authority.py` adds `build_authority` and `check_identity`, which is harmless.

- [ ] **Step 7: Mutation check**

In `build_authority`, change `if audit_status == "error":` to `if False:` and confirm no test fails (it is not asserted); then instead change `blocked.append("content_review_pending")` to `pass` and confirm `test_a_consistent_identity_alone_still_does_not_authorize` fails (`eligibility_executable` becomes true or the reason is missing). Revert both.

- [ ] **Step 8: Commit**

```
git add backend/bintanong_tools/prospectus_extractor/authority.py backend/bintanong_tools/prospectus_extractor/pipeline.py backend/bintanong_tools/prospectus_extractor/common.py tests/test_prospectus_authority.py
git commit -m "feat: separate extraction audit, content review and source verification"
```

If Task 3 was held back, add its two source files and the `prerequisites.py`/`prolog.py` edits to this commit or commit them first with their own message. Append to the progress file.

---

### Task 6: Document that `promotion_status` is not approval

**Files:**
- Modify: `backend/bintanong_tools/prospectus_extractor/audit.py:274`
- Modify: `backend/bintanong_tools/prospectus_extractor/__init__.py` (docstring)
- Create: `docs/decisions/prospectus-status-separation.md`

Documentation only. No test; the payload note is already asserted in Task 5.

- [ ] **Step 1: Comment in `audit.py`**

Replace line 274 with:

```python
        # Legacy label kept for existing readers. It means only that the extractor's own checks found
        # no error. It is NOT approval of the curriculum, the source, or any eligibility result.
        # Read extraction_audit, content_review and source_verification on the payload instead.
        "promotion_status": "REVIEW_REQUIRED" if errors else "VERIFIED",
```

- [ ] **Step 2: Docstring in `__init__.py`**

Append to the module docstring, before the closing quotes:

```
Status fields: ``extraction_audit`` (ok, warn or error) is the extractor's own check.
``content_review`` is always ``pending`` from the extractor. ``source_verification`` comes
from the source record and is ``pending`` unless a human verified the source. The legacy
``promotion_status`` is not approval; ``authority.eligibility_executable`` is false for
everything the extractor produces.
```

- [ ] **Step 3: Write the decision record**

Create `docs/decisions/prospectus-status-separation.md` stating, in plain sentences: the date and branch; the three states and what sets each; that `promotion_status` is kept only for compatibility; the prerequisite state vocabulary with, for each state, what the extractor can and cannot tell (copy the D1 reasoning, including that blank, missing, and unreadable cells are indistinguishable and that `reviewed_empty` is reserved for a human); which states are executable and why; that `eligible/2` previously ignored standing and unresolved tokens; that blocked audits already drop candidate Prolog and RAG (and are tested); the `ProvisionalSource` plumbing (keyword-only `source=`, `approved_scope=`, hash mismatch raises); that campus stays `Tiniguiban - Main` as a labelled `extractor_default` observation; the two schema version changes; and the regression result from Task 7 (fill it in after that task).

- [ ] **Step 4: Commit**

```
git add backend/bintanong_tools/prospectus_extractor/audit.py backend/bintanong_tools/prospectus_extractor/__init__.py docs/decisions/prospectus-status-separation.md
git commit -m "docs: record that promotion_status is not approval"
```

Run the full suite once more and note the count. Append to the progress file.

---

### Task 7: 44-input regression (course fields unchanged, changed fields listed)

**Files:**
- Create: `scripts/prospectus_status_compare.py`
- Modify: `docs/decisions/prospectus-status-separation.md` (result)

This gate takes roughly 90 minutes (each Docling-JSON run is about 2 minutes). Launch it detached: background tool calls die at 10 minutes. The old side and the new side run in parallel as two detached processes.

- [ ] **Step 1: Write the comparer**

The earlier golden script (`git show 2dffe3d:scripts/prospectus_golden_check.py`) ran the old code as a copied file. This one runs each side from its own checkout and compares fields, not bytes.

```python
#!/usr/bin/env python3
"""Phase C gate: course fields unchanged, every other change listed and expected.

    python scripts/prospectus_status_compare.py run TREE GOLDEN OUT [--semantic-doc MAP]
    python scripts/prospectus_status_compare.py compare OLD_OUT NEW_OUT

`run` processes every *_docling.json under GOLDEN with the code checked out at TREE.
`compare` fails on any removed or changed field outside ALLOWED_CHANGED, and on any
added field outside EXPECTED_ADDED. Later phases replace those two sets.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

# schema_version is bumped; prolog.clauses changes only for audits that are not `error`
# (the header comment, prerequisite_state/2, rule_complete/1 and the eligible/2 rule).
ALLOWED_CHANGED = {"schema_version", "prolog.clauses"}
EXPECTED_ADDED = {
    "extraction_audit",
    "content_review",
    "source_verification",
    "authority",
    "metadata.observations",
    "courses.[].prerequisite_state",
    "curriculum_by_term.*.*.[].prerequisite_state",
    "prolog.relations.prerequisite_states",
    "prolog.relations.rule_complete",
}


def run(tree: Path, golden: Path, out: Path, semantic: Path | None) -> int:
    env = dict(os.environ, PYTHONHASHSEED="0", PYTHONIOENCODING="utf-8")
    extra = ["--semantic-doc", str(semantic)] if semantic else ["--no-semantic-doc"]
    sources = sorted(golden.rglob("*_docling.json"))
    for number, source in enumerate(sources, 1):
        folder = out / f"{number:02d}"
        folder.mkdir(parents=True, exist_ok=True)
        done = subprocess.run(
            [sys.executable, "-m", "backend.bintanong_tools.prospectus_extractor",
             "-i", str(source), "-o", str(folder / "candidate.json"),
             "--export-all", "--device", "cpu", *extra],
            cwd=tree, env=env, capture_output=True,
        )
        (folder / "exit.txt").write_text(f"{done.returncode}\n{source}\n", encoding="utf-8")
        print(f"{number}/{len(sources)} exit={done.returncode} {source.name}", flush=True)
    print(f"done {len(sources)}")
    return 0


def diff(old, new, path=()):
    """Yield (kind, path) for every difference: changed, added or removed."""
    if isinstance(old, dict) and isinstance(new, dict):
        for key in sorted(old.keys() | new.keys()):
            if key not in new:
                yield "removed", path + (key,)
            elif key not in old:
                yield "added", path + (key,)
            else:
                yield from diff(old[key], new[key], path + (key,))
    elif isinstance(old, list) and isinstance(new, list) and len(old) == len(new):
        for index, (a, b) in enumerate(zip(old, new)):
            yield from diff(a, b, path + (index,))
    elif old != new:
        yield "changed", path


def normalise(path) -> str:
    parts = ["[]" if isinstance(part, int) else part for part in path]
    if parts[0] == "curriculum_by_term" and len(parts) >= 3:
        parts[1] = parts[2] = "*"
    if parts[0] == "unlocks" and len(parts) >= 2:
        parts[1] = "*"
    return ".".join(parts)


def load(folder: Path):
    target = folder / "candidate.json"
    if not target.exists():
        return None
    payload = json.loads(target.read_text(encoding="utf-8"))
    payload.pop("generated_at", None)  # run-to-run noise
    clauses = payload.get("prolog", {}).get("clauses")
    if clauses:
        payload["prolog"]["clauses"] = [line for line in clauses if not line.startswith("% Generated:")]
    return payload


def compare(old_out: Path, new_out: Path) -> int:
    counts: Counter = Counter()
    problems: list[str] = []
    folders = sorted(path for path in old_out.iterdir() if path.is_dir())
    for folder in folders:
        other = new_out / folder.name
        exits = [(side / "exit.txt").read_text(encoding="utf-8").splitlines()[0] for side in (folder, other)]
        if exits[0] != exits[1]:
            problems.append(f"{folder.name}: exit code old={exits[0]} new={exits[1]}")
        old, new = load(folder), load(other)
        if old is None or new is None:
            if (old is None) != (new is None):
                problems.append(f"{folder.name}: candidate.json exists on only one side")
            continue
        for kind, path in diff(old, new):
            name = normalise(path)
            counts[(kind, name)] += 1
            allowed = ALLOWED_CHANGED if kind == "changed" else EXPECTED_ADDED if kind == "added" else set()
            if name not in allowed:
                problems.append(f"{folder.name}: unexpected {kind} {name}")
    print(f"{'kind':8} {'inputs':>6}  field")
    for (kind, name), number in sorted(counts.items()):
        print(f"{kind:8} {number:>6}  {name}")
    for problem in problems[:40]:
        print("PROBLEM", problem)
    print(f"{len(folders)} inputs, {len(problems)} problem(s)")
    return 1 if problems else 0


def main() -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    sub = cli.add_subparsers(dest="command", required=True)
    runner = sub.add_parser("run")
    runner.add_argument("tree", type=Path)
    runner.add_argument("golden", type=Path)
    runner.add_argument("out", type=Path)
    runner.add_argument("--semantic-doc", type=Path)
    comparer = sub.add_parser("compare")
    comparer.add_argument("old_out", type=Path)
    comparer.add_argument("new_out", type=Path)
    args = cli.parse_args()
    if args.command == "run":
        return run(args.tree, args.golden, args.out, args.semantic_doc)
    return compare(args.old_out, args.new_out)


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Prove the comparer can fail (two inputs, about 8 minutes, foreground)**

Make a throwaway tree of the base and run two inputs on each side:

```
git worktree add "$env:TEMP\bintanong-phasec-base" $BASE_REF
$gold = 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\docling_jsonified_output\task2b_standing_isolated_2026-09-29'
$map  = 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\PalSU Undergraduate Prospectus Website Dump\Tiniguiban - Main\palsu_main_undergrad_program_college_meaning.md'
```

`run` has no `--limit`; for this smoke test copy two files into a scratch folder first:

```
New-Item -ItemType Directory -Force "$env:TEMP\phasec-smoke" | Out-Null
Get-ChildItem $gold -Recurse -Filter *_docling.json | Select-Object -First 2 | Copy-Item -Destination "$env:TEMP\phasec-smoke"
uv run --project backend --extra tools --extra dev python scripts/prospectus_status_compare.py run "$env:TEMP\bintanong-phasec-base" "$env:TEMP\phasec-smoke" "$env:TEMP\phasec-smoke-old" --semantic-doc $map
uv run --project backend --extra tools --extra dev python scripts/prospectus_status_compare.py run (Get-Location).Path "$env:TEMP\phasec-smoke" "$env:TEMP\phasec-smoke-new" --semantic-doc $map
uv run --project backend --extra tools --extra dev python scripts/prospectus_status_compare.py compare "$env:TEMP\phasec-smoke-old" "$env:TEMP\phasec-smoke-new"
```

Expected: `0 problem(s)` and a table whose `added` rows are exactly the `EXPECTED_ADDED` names and whose `changed` rows are `schema_version` (and `prolog.clauses` only if one of the two is a non-error audit). Then prove it can fail: edit one `courses[0].course_title` in `phasec-smoke-new\01\candidate.json` and rerun `compare`. Expected: `PROBLEM 01: unexpected changed courses.[].course_title` and exit code 1. Restore the file (rerun the new side for input 01 if needed).

- [ ] **Step 3: Launch the full runs detached, old and new in parallel**

```
$q = { param($s) '"' + $s + '"' }
$old = Join-Path $env:TEMP 'phasec-old'; $new = Join-Path $env:TEMP 'phasec-new'
$tree = Join-Path $env:TEMP 'bintanong-phasec-base'
$script = 'scripts/prospectus_status_compare.py'
foreach ($side in @(@($tree, $old), @((Get-Location).Path, $new))) {
  $procArgs = @('run','--project','backend','--extra','tools','--extra','dev','python',$script,'run',(& $q $side[0]),(& $q $gold),(& $q $side[1]),'--semantic-doc',(& $q $map))
  $log = "$($side[1]).log"
  Start-Process uv -ArgumentList $procArgs -WorkingDirectory (Get-Location).Path -RedirectStandardOutput $log -RedirectStandardError "$log.err" -WindowStyle Hidden
}
```

Poll with `Get-Content "$env:TEMP\phasec-old.log" -Tail 3` and the same for `phasec-new.log` every few minutes. Each ends with `done 44`. Expected: about 90 minutes.

- [ ] **Step 4: Compare**

```
uv run --project backend --extra tools --extra dev python scripts/prospectus_status_compare.py compare "$env:TEMP\phasec-old" "$env:TEMP\phasec-new"
```

**Pass condition:** `44 inputs, 0 problem(s)`, and the printed table equals this (counts for the `added` rows are all 44; `prolog.clauses` is 6, the number of non-error audits in the cached set: 1 `ok` plus 5 `warn`):

```
changed      6  prolog.clauses
changed     44  schema_version
added       44  authority
added       44  content_review
added       44  extraction_audit
added       44  metadata.observations
added       44  prolog.relations.prerequisite_states
added       44  prolog.relations.rule_complete
added       44  source_verification
added  <n>     courses.[].prerequisite_state
added  <n>     curriculum_by_term.*.*.[].prerequisite_state
```

The last two counts are the number of course entries across the 44 payloads (each course appears in both `courses` and `curriculum_by_term`, so the two numbers match). Nothing else may appear: in particular no `changed` or `removed` row under `courses`, `audit`, `metadata` values, `campus`, `quality_report`, `rag`, `evidence`, or `elective_tracks`.

If an unexpected row appears and it looks like noise (set order, a timestamp), run the old side twice on that single input and diff the two old outputs before blaming the change. If it is real, fix with a failing test first.

Also check by hand that the exit codes matched (the comparer reports mismatches as `PROBLEM`) and that 38 payloads still have `prolog.status = blocked`.

- [ ] **Step 5: Record the result and clean up**

Write the table, the date, `$BASE_REF`, and the commands into the "regression result" paragraph of `docs/decisions/prospectus-status-separation.md` and into the progress file. Remove the temporary tree: `git worktree remove "$env:TEMP\bintanong-phasec-base" --force`.

```
git add scripts/prospectus_status_compare.py docs/decisions/prospectus-status-separation.md
git commit -m "test: compare 44 cached inputs field by field for Phase C"
```

---

### Task 8: Codex gate and hand-off

**Files:** progress file only.

- [ ] **Step 1: Full verification**

Run the full suite and the self-test one last time. Record the counts. Expected: all pass, `80/80`.

- [ ] **Step 2: Reviewer pass**

Dispatch `extractor-reviewer` over the branch diff (`git diff dev...HEAD`) with this brief: confirm no existing course field, audit field, or `promotion_status` value changed; confirm every new field is additive; confirm each of the seven draft cases has a test that asserts `promotion_status == "VERIFIED"` as a precondition (the cases are: mismatched scope with an approved identity, pending identity, hash mismatch, unreadable cell, unresolved token, standing-only, OR/exception text; hash mismatch is the one that asserts a raise instead, because no payload is produced). Fix confirmed findings with a failing test first.

- [ ] **Step 3: Codex gate (read-only, detached, about 15 minutes)**

```
$prompt = "Review branch feat/prospectus-phase-c-status-separation against dev in this repo. Claim: the extractor payload now keeps extraction_audit, content_review and source_verification separate; no machine audit result (including the legacy promotion_status VERIFIED) can produce executable eligibility; courses whose prerequisite state is not resolved, stated_none or reviewed_empty never satisfy eligible/2 or next_eligible/2; and existing course fields are unchanged. Try to break each claim: find a prerequisite text that the parser resolves but the state classifier calls resolved when it is actually an alternative or exception, a path that reaches eligible/2 without rule_complete/1, a way a hash mismatch still deletes or overwrites old outputs, and any removed or renamed payload field. Do not modify files. Report findings with file and line."
Start-Process codex -ArgumentList @('exec','--sandbox','read-only','-o',"$env:TEMP\codex_phase_c.txt",('"' + $prompt + '"')) -WindowStyle Hidden -RedirectStandardOutput "$env:TEMP\codex_phase_c.log" -RedirectStandardError "$env:TEMP\codex_phase_c.err"
```

Poll `$env:TEMP\codex_phase_c.txt`. Record the findings in the progress file. If Codex is rate-limited or errors, record that and continue; do not block. Fix confirmed findings with a failing test first; note and skip unconfirmed ones.

- [ ] **Step 4: Hand-off**

Append to the progress file: final commit hash, test counts, the Task 7 table, Codex findings and dispositions, known limits (blank cells cannot be told from missing ones; `unreadable` in a non-blocked payload only comes from "nothing recognised"; the review CSV does not yet show `prerequisite_state`; the batch manifest does not yet carry the three states), and "next: Phase D". Commit:

```
git add plans/plan_current_progress/extractor_split_progress.md
git commit -m "docs: record Phase C results and gate findings"
```

Do not merge into `dev` and do not push; ask the user (superpowers:finishing-a-development-branch).

**Phase C gate:** the seven draft cases are green with `VERIFIED` as the precondition; blocked audits stay empty; `44 inputs, 0 problem(s)` with the expected table; self-test `80/80`; full suite green; `SCHEMA_VERSION` is `palsu-prospectus-v3.1`; decision record written; Codex findings resolved or recorded.

---

## Self-review

**Spec coverage (outline items):**
- Three distinct fields, `content_review` always pending, `source_verification` from the source record or `pending`: Task 5 (`build_authority`, tests `test_three_states_are_separate_fields...`, `test_source_record_is_carried...`).
- Source reaches the pipeline without breaking callers: keyword-only `source=` and `approved_scope=` (D4, Task 5); existing callers and the CLI are unchanged.
- `promotion_status` kept and documented as non-approval: Task 5 asserts it unchanged and adds `authority.note`; Task 6 documents it in code, docstring, and decision record.
- Metadata as observations with evidence, nothing deleted: Task 4; `build_essentials` and the compact shape untouched except additive keys (Task 5), checked by the 44-run (Task 7).
- Per-course prerequisite state, with the honest subset and the "can/cannot distinguish" analysis: D1, Task 2.
- Exclusion from `eligible/2` and `next_eligible/2`: Task 3 (with a swipl-executed test).
- Blocked audit drops Prolog and RAG: D3, already true, locked by a test in Task 3 with the relations shape aligned.
- Seven draft cases: scope mismatch, pending identity (Task 5); hash mismatch (Task 5, raise); unreadable, unresolved token, standing-only, OR/exception (Task 3). Each asserts the legacy label would say `VERIFIED` (hash mismatch asserts the raise and untouched outputs instead, because no payload exists).
- 44-input regression showing course fields unchanged and the exact changed fields: Task 7 with the expected table.
- Schema bump with what changed: D7, Task 5 step 5, listed in the decision record.
- Codex gate, progress-file updates, Phase A gate deletion conditional, commit trailer, explicit staging: Tasks 1 and 8, and each task.
- OCR room: the observation records carry `basis`, `evidence`, `status`, and a code comment notes a later `source_kind` or confidence field; no assumption that evidence is a born-digital text layer. Not otherwise planned.

**Placeholder scan:** no TBD or "similar to". Task 3 step 5 and the Task 3 commit have an explicit instruction for the one assertion that cannot pass until Task 5; it is the only forward dependency.

**Type and name consistency:** `PREREQUISITE_STATES`, `EXECUTABLE_PREREQUISITE_STATES`, `PREREQUISITE_AMBIGUITY_TYPES`, `classify_prerequisite_state`, `annotate_prerequisite_states` (Task 2) are used unchanged in Tasks 3 and 5. `build_authority` keyword names (`audit_status`, `metadata`, `courses`, `source`, `approved_scope`, `pdf_hash_check`) match the `build_payload` call. Payload keys `extraction_audit`, `content_review`, `source_verification`, `authority` (`source_record`, `identity_check`, `eligibility_executable`, `blocked_by`, `courses_with_incomplete_prerequisite_rule`, `note`) match tests, essentials, and the comparer's `EXPECTED_ADDED`. Prolog names `prerequisite_state/2`, `rule_complete/1`, relations keys `prerequisite_states` and `rule_complete` match in `prolog.py`, the blocked object, and the tests.

**Known risks to watch:** the `or` word-pattern is deliberately broad, so a course title fragment that leaks into a prerequisite cell and contains `or`, `if`, or `equivalent` would be classed `alternative_or_exception` and excluded; that is the safe side. The swipl test only runs where `swipl` is on `PATH`.
