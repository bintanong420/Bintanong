# Prospectus Phase B2: Year/Semester Verifier and Fixer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task, with superpowers:test-driven-development inside each task. Steps use checkbox (`- [ ]`) syntax. Tasks run through the project agents `extractor-implementer` and `extractor-reviewer`. Update `plans/plan_current_progress/extractor_split_progress.md` after every task commit (each task has a step for it).

**Status:** Written 4 October 2026 against `dev` after Phase B (the markup twin). Phase B2 sits between Phase B and Phase C of `plans/2026-10-03-prospectus-extractor-package-split.md`. Part of the parallel, review-only prospectus workstream: it advances nothing in `plans/INDEX.md` and approves no curriculum, RAG, or Prolog release. A human decision recorded here is "a person looked and decided", never issuing-office or curriculum-version approval.

**Goal:** After ingestion, triage every extracted curriculum by year and semester section, let a person confirm the clean sections in bulk and spend effort only on flagged ones, and record every human decision in an append-only ledger from which a corrected candidate JSON is rebuilt deterministically. The extraction itself is never edited.

**Architecture:** A verifier (`verify.py`) groups the candidate's courses into year x semester sections in printed order and computes flags and a health per section from the JSON and, when the original PDF is at hand, its text layer. A fixer (`fixes.py`) proposes a fix per flag only where the text already exists in the document. A review sheet (`sheet.py`, one Markdown file per prospectus) carries sections, flags, proposals and a decision column; `apply` validates the edited sheet against a freshly regenerated copy and appends ledger entries (`ledger.py`). `materialise` rebuilds a corrected candidate from the immutable extraction plus the applicable entries. The ledger line format is what the later browser GUI (draft Task 5) will read and append; no GUI is built here. The last task is the separate parser-level banner split, gated by the 44-input comparer.

**Tech Stack:** Python 3.13, stdlib only (`argparse`, `json`, `hashlib`, `subprocess` for `git`), pytest 9, `uv`. `pypdfium2` (already present through Docling) only to read a PDF text layer. No new dependency.

**Base:** `dev` after the Phase B close-out commits. **Branch to create:** `feat/prospectus-phase-b2-section-fixer`. Leave the dirty `.gitignore` and the untracked `plans/CODEX_HANDOFF_prospectus_extractor_phase2_2026-09-26.md` alone; never `git add -A` or `git add .`; stage by explicit path.

**Schema version:** unchanged (`palsu-prospectus-v3.0`) in every task. Tasks 1 to 12 add no key to the extractor's payload; the corrected candidate is a separate artifact with its own `review.schema` string (`prospectus-corrected-candidate-v1`). Task 13 changes extracted values and the contents of the existing `provenance.discarded_fragments` key, not the payload shape; it is reported field by field. Phase C bumps to `v3.1` as planned.

**Evidence base:** every number in "What the real data says" and every `Expected:` line quoted from a real-data command was measured on 4 October 2026 by a prototype of this plan's code run in a scratch copy of the repository (outside Git) against the cached runs in `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\compare_2026-10-03b\new` and the PDFs in the same dump. All 125 tests in this plan passed there. If a real-data number differs when you run it, the data or the code moved: investigate before trusting the rest of the task.

---

## Decisions needed before execution

The rest of the plan assumes the recommendation in each row. Steps that would change are marked **[D#]**.

| # | Question | Options | Recommendation and why |
| --- | --- | --- | --- |
| D1 | Review-sheet format. | (a) Markdown pipe tables, one per section. (b) YAML. (c) CSV, one file per section or one long file. | **(a).** It previews as real tables in VS Code (Ctrl+Shift+V), diffs line by line (one row per line), and the same file is readable by a person who never opens a terminal. `|` and `\` are escaped (`\|`, `\\`) and line breaks flattened, and a test round-trips both. (b) needs PyYAML, which the backend does not depend on, and a hand-edited YAML indent error is silent. (c) loses the one-table-per-section layout, and Excel rewrites `2/1` as a date and drops leading zeros, which would corrupt the very fields being reviewed. Encoding is UTF-8 with `\n` newlines on every OS. Changes Tasks 8 and 9. |
| D2 | Where sheets, ledgers and corrected candidates are stored. | (a) `<candidate folder>/review/<candidate name>/`, outside Git by construction, with a guard that refuses a tracked path inside the repository. (b) Under `docs/` or `plans/` in the repository. (c) One central folder keyed by PDF hash. | **(a).** They hold institutional text (titles, codes, a reviewer's name), master plan §16.1 and the draft's global constraints keep that out of Git by default, and keeping the ledger next to the run it describes means a run folder can be archived whole. (c) hides which run a decision belongs to. The guard (`assert_outside_git`) uses `git check-ignore`, so a path inside the repository is accepted only if `.gitignore` already covers it. Changes Task 10. |
| D3 | How a decision locates a course, and how finely it records one. | (a) The course's sorted source-cell ids plus a field name; a `row` field means "all fields as extracted". (b) The course code. (c) One entry per row only. | **(a).** Cell ids are what the GUI will have and what the draft and master §7.1 name; codes repeat (duplicates are a flag here) and change when corrected. Per-field entries give `accepted | corrected | unresolved` per critical field as §7.1 asks, and the `row` wildcard lets a section confirm be one line per course instead of three. A later entry for the same course and field wins; the earlier one stays as history. Changes Tasks 6 and 7. |
| D4 | Which fields a reviewer can correct in this phase. | (a) Code, title and term (year and semester). (b) Also units and prerequisites. | **(a).** Those are the three the fixer can propose for; units and prerequisites need re-derived fields (totals, resolution, eligibility) and would be edited more safely in the GUI against the PDF. A wrong printed total is recorded as `accepted` or `unresolved` with a reason. Changes Tasks 4, 7, 9. |
| D5 | What lets the state become `reviewed`. | (a) Every course decided (accepted or corrected) and every printed code the audit listed decided, nothing unresolved. Printed codes found only in the PDF text are recorded when decided but do not gate. (b) Also require those PDF-only codes. | **(a).** The state function must work from the candidate and the ledger alone (Phase C calls it without a PDF). The 6 PDF-only codes in BS Computer Science are elective-list codes in a footnote, not missed courses. `reviewed` means "a person decided everything", not "correct". Changes Task 6. |
| D6 | Health vocabulary. | (a) Section: `clean` (no flag above info), `review` (warn flags only), `broken` (any error flag). Prospectus: `clean`, `warnings_only`, `mixed`, `broken` (more than half the sections broken, or fewer than two term sections, or printed codes no course claimed numbering at least a quarter of the courses and at least three). (b) A numeric score. | **(a).** Plain words a reviewer can act on, derived from flags with fixed rules, tested on three fixtures. Error flags: banner text in a field, printed term total mismatch, a course in two terms or none, an unclaimed printed code or audit anomaly. Warn flags: prerequisite in the same or a later term, code or title not found in the PDF text. Changes Tasks 3 and 5. |
| D7 | Banner phrase test. | (a) Exact upper-case phrases only (`FIRST YEAR`, `SECOND SEMESTER`, `SUMMER`, `MID-YEAR`, an upper-case ordinal glued to a capitalised word such as `FIRST Ethics`). (b) Case-insensitive. | **(a).** The printed banners are upper case; case-insensitive matching would flag real titles such as "First Aid" and "Summer Internship". A test pins both. Changes Task 3. |
| D8 | What a reviewer can do about an unclaimed printed code or a withheld row. | (a) `ok` or `unresolved`, each with a reason; no "add course" action. (b) An add-course action. | **(a).** Adding a course means transcribing code, title, units and prerequisites from the PDF with per-field cell provenance, which is the GUI's job (draft Task 5) and the parser's (draft Task 2). Until then such rows are listed and decided, never fabricated. Changes Task 9. |
| D9 | Run the parser banner split (Task 13)? | (a) Yes, after the trial review (Task 12), and merge only on the user's go. (b) Skip it. | **(a), with eyes open.** The prototype measured on all 44 inputs: exactly 1 course title changes (`AS 1`, `EE FIRST SEMESTER Environmental Engineering` becomes `EE Environmental Engineering`), 54 courses gain a recorded banner fragment in `provenance`, and the verifier's `banner_leak` count falls from 3 to 2; every other flag count is unchanged. The data suggests the parser already removes most banner text, so the gain is small; the split matters for inputs the cached 44 do not show (a glued year plus semester banner currently corrupts the title: `SEMESTER Discrete Structures`). The trial review decides whether it is worth merging. |

## What the real data says (measured 4 October 2026)

These facts shaped the design and the expectations below.

1. **Banner words almost never survive into the extracted fields.** Over the 44 cached candidates (2,031 courses) the verifier's `banner_leak` check fires 3 times (`EE FIRST SEMESTER Environmental Engineering` and 2 others in 2 files). The banner text sits in the source cells (62 courses carry a banner in their own code or title cell: BSCS `t0-c9` is `FIRST SEMESTER Discrete Structures 1 1`) and the parser already strips it from the field (`title_raw` is the cleaned text). So check 1 is mostly an `info` flag at cell level, and the signal that matters is elsewhere: printed term totals disagree in 73 sections, 146 printed codes and 69 other anomalies are unclaimed (merged-cell rows withheld, missing year markers), and 114 titles are not found in the PDF text.
2. **Section banner cells ride in every course's provenance.** BSCS `t0-c8` (`FIRST YEAR`) and `t0-c9` are in the `source_cell_ids` of every course of the section, and Architecture `t0-c10` spans the code columns. Any check that reads "the course's cells" must separate a course's own single-column cells from section context cells (`own_role_cells`, Task 3), or every course looks contaminated.
3. **`title_from_pdf` is the working proposal.** Of 114 courses whose title is not in the PDF text, 62 get a proposal from the PDF row (Architecture: `Techniques 1 Purposive Communication` becomes `Purposive Communication`; `Graphics 2 Architectural Visual Communications 4-Visual` becomes `Architectural Visual Communications 4-Visual Techniques 2`). The rest are ambiguous (a title that repeats the units digit, such as `History of Architecture 3` with units 3) and stay flag-only. `strip_banner` and `move_term` have no hit on the 44 cached inputs; they exist for the glued banners the parser cannot yet split and are tested on synthetic cells.
4. **A printed term total with no courses is visible only in the audit's error text** (`Document declares a total for 1st Year 1st Semester but no courses were extracted there.`), because `term_unit_audit` lists only terms that have courses. The verifier reads that text (one regex) so an empty section appears.
5. **The legacy shim re-exports every public name of every package module, last module wins.** A new module that defines `main` or a second `DASHES` silently replaces the extractor's. The sheet CLI is therefore `fixer_main`, and `verify.py` imports the PDF dash set under a private alias. A test pins both.
6. **Triage over the 39 distinct PDFs** (Task 11 reproduces it, 3 seconds): 1 `clean` (BS Biology), 3 `warnings_only` (ABPhilStud, BSBA-HRM, IT), 17 `mixed`, 18 `broken` (BSE-Innovation-and-Tech: 76 unclaimed printed codes against 2 courses; Midwifery; Accountancy; Management Accounting; most Engineering and Education tracks).

## File structure

All new package code is under `backend/bintanong_tools/prospectus_extractor/`. Modules keep the package rule: a module imports only from modules above it in this list.

| File | Change | Responsibility |
| --- | --- | --- |
| `text.py` | Modify | `BANNER_PHRASE`, `has_banner_text`, `leading_banner`, `trailing_banner` (Task 3). |
| `course_checks.py` | Create (Task 2) | The audit script's pure checks (A to D, `PdfPage`, `load_pdf_pages`, manifest helpers), moved so the verifier reuses them. |
| `fixes.py` | Create (Task 4) | `Fix`, `strip_banner`, `title_from_pdf`, `propose_fixes`, term text helpers. |
| `placement.py` | Create (Task 5) | Unclaimed printed codes and anomalies, PDF box lookup, attaching an item to a section. |
| `verify.py` | Create (Tasks 3 to 5) | Sections, flags, health: `verify_candidate`. |
| `ledger.py` | Create (Tasks 6 and 7) | Entry format, append-only file, applicability, `content_review_state`, `materialise`. |
| `sheet.py` | Create (Tasks 8 and 9) | Render, parse and check the review sheet; turn decisions into entries. |
| `fixer_cli.py` | Create (Task 10) | `sheet`, `apply`, `materialise`, `status`, `triage`; reviewer identity; the outside-Git guard. |
| `sections.py` | Modify (Task 13 only) | The banner split in `_row_field_candidates` and the recorded fragment in `_candidate_to_raw_course`. |
| `backend/bintanong_tools/prospectus_fixer.py` | Create (Task 10) | Thin `python -m` entry point, like `prospectus_batch.py`. |
| `scripts/prospectus_course_audit.py` | Modify (Task 2) | Imports the moved checks; behavior and output unchanged. |
| `scripts/prospectus_course_compare.py` | Modify (Task 13) | `--allow-change`, `--report`, `--flags`. |
| `tests/fixer_fixtures.py`, `tests/sheet_helpers.py` | Create | Candidate fixtures from real Docling cell topology; helpers that edit a rendered sheet. |
| `tests/test_prospectus_course_checks.py`, `..._verify.py`, `..._fixes.py`, `..._verify_pdf.py`, `..._ledger.py`, `..._materialise.py`, `..._sheet.py`, `..._sheet_decisions.py`, `..._fixer_cli.py`, `..._fixer_e2e.py`, `..._banner_split.py` | Create | One focused file per task. |
| `tests/test_prospectus_course_compare.py` | Modify (Task 13) | Tests for the comparer's new options. |
| `docs/decisions/prospectus-section-fixer.md` | Create (Task 14) | Decision record with the evidence. |
| `plans/plan_current_progress/extractor_split_progress.md` | Modify | New "Phase B2" section, updated after each task. |
| `plans/2026-10-03-prospectus-phase-c-status-separation.md` | Modify (already done by the planner) | One-line note in the start check naming `content_review_state`. Task 14 only verifies it is still there. |

Unchanged on purpose: `common.py` (`SCHEMA_VERSION`), `pipeline.py`, `loader.py`, `markup.py`, `audit.py`, `selftest.py` (still 80/80), `batch.py`, `cli.py`. `prospectus_batch.py`'s `parser_sha256` is a hash of every package `.py`, so it changes when these modules land even though extraction is unchanged (like Phase A: not comparable with earlier manifests).

## Interface Phase C needs

Phase C replaces its constant `content_review: "pending"` with a derived value. The whole interface is one function in `ledger.py`:

```python
content_review_state(payload: Mapping, entries: Iterable[Mapping], pdf_sha256: str) -> dict
# {"state": "pending" | "partially_reviewed" | "reviewed", "courses": int, "decided": int,
#  "unresolved": int, "unclaimed_undecided": int, "inapplicable_entries": int}
```

`entries` come from `ledger.read_entries(path)`; entries recorded against another `pdf_sha256` are counted in `inapplicable_entries` and ignored. With no ledger, Phase C keeps `"pending"`. `reviewed` is not an approval (D5).

## Commands used throughout

PowerShell, repo root (Git Bash is broken on this machine).

```
# Full suite (baseline at the start of this phase: 93 passed, 13 subtests passed)
uv run --project backend --extra tools --extra dev --with fastapi==0.141.1 python -m pytest -q tests

# Self-test (baseline 80/80; it must not change)
uv run --project backend --extra tools --extra dev python -m backend.bintanong_tools.prospectus_extractor --self-test

# The fixer
uv run --project backend --extra tools --extra dev python -m backend.bintanong_tools.prospectus_fixer --help
```

Real-data paths (outside Git, as of 4 October 2026): `$GOLDEN` is `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\docling_jsonified_output\task2b_standing_isolated_2026-09-29` (44 `*_docling.json` and `isolated_manifest.json`); `$RUNS` is `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\compare_2026-10-03b\new` (44 numbered run folders with `candidate.json` and `source.txt`); `$PDFS` is `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\PalSU Undergraduate Prospectus Website Dump`; `$CHECK` is `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\markup_twin_visual_check_2026-10-03\all` (one folder per distinct PDF, each holding the PDF, the markup twin and the candidate JSON); `$MAP` is `$PDFS\Tiniguiban - Main\palsu_main_undergrad_program_college_meaning.md`.

Commit trailer for every commit in this plan: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

---

### Task 1: Start check

**Files:** read only, plus the progress file.

- [ ] **Step 1: Wait for Phase B to be on `dev`, then branch**

Another agent may still be committing Phase B's close-out. Do not start until it shows in the log.

```powershell
git log --oneline dev -8
git status --short
```

Expected: the log shows Phase B's close-out (the most recent Phase B commits at the time of writing are `4459591 docs: record Phase B review fixes and known limitations` and `42a5d2b fix: make the course comparer fail on missing outputs and cell mismatches`; a later Phase B decision-record commit is expected) and `git status --short` lists only ` M .gitignore` and `?? plans/CODEX_HANDOFF_prospectus_extractor_phase2_2026-09-26.md`. If Phase B is not on `dev` yet, stop and report.

```powershell
git switch dev
git pull --ff-only
git switch -c feat/prospectus-phase-b2-section-fixer
git rev-parse HEAD
```

(`git pull --ff-only` may report there is no remote; that is fine.) Record the printed hash as `$B2_BASE`.

- [ ] **Step 2: Baseline**

Run both commands from "Commands used throughout". Expected: `93 passed` with `13 subtests passed`, and `Self-test: 80/80 checks passed.` Any difference is a stop-and-report: record what you saw and do not continue.

- [ ] **Step 3: The Phase A gate is gone, and the files this phase builds on are as described**

```powershell
Test-Path tests/test_prospectus_split_equivalence.py
Select-String -Path scripts/prospectus_course_audit.py -Pattern '^# -{60,} (normalisation|IO: manifest, PDFs, runs)$', '^def run_all\(', '^DEFAULT_PDF_ROOT', '^DASHES = '
Select-String -Path backend/bintanong_tools/prospectus_extractor/text.py -Pattern '^def match_year_label\('
Select-String -Path backend/bintanong_tools/prospectus_extractor/common.py -Pattern '^SCHEMA_VERSION'
Select-String -Path scripts/prospectus_course_compare.py -Pattern '^def compare_runs\(', '^def compare_payloads\(', '^AUDIT_FIELDS'
```

Expected: `False` (Phase B deleted the gate; if `True`, delete it in this branch's first commit with `git rm tests/test_prospectus_split_equivalence.py` and `git commit -m "test: remove the Phase A equivalence gate" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`); the audit script shows both `# ---- normalisation` and `# ---- IO: manifest, PDFs, runs` markers, `def run_all(`, `DEFAULT_PDF_ROOT` and `DASHES = ` once each; `def match_year_label(` once in `text.py`; `SCHEMA_VERSION = "palsu-prospectus-v3.0"`; the comparer has `compare_runs`, `compare_payloads` and `AUDIT_FIELDS` once each. If a marker moved, adjust the marker text used in Task 2 and Task 13 scripts and note it in the progress file.

- [ ] **Step 4: Confirm the Phase C note is in place**

```powershell
Select-String -Path plans/2026-10-03-prospectus-phase-c-status-separation.md -Pattern 'Phase B2 note'
```

Expected: one match naming `ledger.content_review_state`. (The planner added it on 4 October; if it is missing, add the same one-line note under Task 1 "Files" of that plan and commit it with this task.)

- [ ] **Step 5: Start the progress section and commit**

Append to `plans/plan_current_progress/extractor_split_progress.md`:

```markdown
## Phase B2: year/semester verifier and fixer (branch feat/prospectus-phase-b2-section-fixer)

Plan: plans/2026-10-04-prospectus-phase-b2-section-fixer.md. Decisions D1-D9 in the plan assumed as recommended unless noted here. Base `$B2_BASE`: <hash>. Baseline: 93 passed + 13 subtests, self-test 80/80.

| Task | Status | Commit | Evidence |
| --- | --- | --- | --- |
```

```powershell
git add plans/plan_current_progress/extractor_split_progress.md
git commit -m "docs: start Phase B2 progress notes" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: Move the course-audit checks into the package (tests first)

**Why:** the verifier must reuse the audit's PDF checks rather than copy them, and `scripts/` is not importable from the package. The move is mechanical; the audit script keeps its behavior and its tests. Two small additions come with it: the PDF-miss check can run without a markup twin, and its rows name the occurrence.

**Files:**
- Create: `tests/test_prospectus_course_checks.py`
- Create: `backend/bintanong_tools/prospectus_extractor/course_checks.py` (by script)
- Modify: `scripts/prospectus_course_audit.py` (by the same script)

- [ ] **Step 1: Write the failing test**

`tests/test_prospectus_course_checks.py`:

```python
import importlib.util
from pathlib import Path

from backend.bintanong_tools.prospectus_extractor import course_checks as cc

_spec = importlib.util.spec_from_file_location(
    "prospectus_course_audit", Path(__file__).resolve().parents[1] / "scripts" / "prospectus_course_audit.py"
)
script = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(script)

SHARED = (
    "check_course_md", "check_course_pdf", "check_pdf_missed", "check_md_unclaimed", "parse_markup", "audit_file",
    "pdf_candidates", "text_in_box", "course_roles", "load_pdf_pages", "manifest_index", "resolve_pdf", "sha256",
    "normalise", "loose", "pdf_clean", "MdDoc", "PdfPage",
)


def test_the_audit_script_uses_the_package_checks_not_copies():
    for name in SHARED:
        assert getattr(script, name) is getattr(cc, name), name


def test_pdf_check_without_a_markup_twin_says_so_and_names_the_occurrence():
    course = {"course_code": "CS 101", "course_title": "Intro", "provenance": {"page": 1}}
    page = "CS 101 Intro 3 ZZ-999 Ghost Course 3 ZZ-999 Again"
    rows = cc.check_pdf_missed([course], {}, page, None, page_no=1)
    ghosts = [r for r in rows if r["json"] == "ZZ-999"]
    assert [(r["status"], r["md_location"], r["occurrence"]) for r in ghosts] == [("silent", "unknown", 1), ("silent", "unknown", 2)]
```

- [ ] **Step 2: Run it to see it fail**

```powershell
uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_course_checks.py
```

Expected: collection error, `ImportError: cannot import name 'course_checks' from 'backend.bintanong_tools.prospectus_extractor'`.

- [ ] **Step 3: Move the checks with a one-off script**

Save as `$env:TEMP\move_course_checks.py` and run it from the repo root. It cuts by marker text, stops if a marker is missing, writes the new module, and rewrites the script to import the moved names (so the audit script and its tests keep one import surface).

```python
"""Move the pure checks of scripts/prospectus_course_audit.py into the package, then thin the script.

Run from the repo root. Cuts by marker text, not line numbers, and stops if a marker is missing.
"""
from pathlib import Path

SCRIPT = Path("scripts/prospectus_course_audit.py")
MODULE = Path("backend/bintanong_tools/prospectus_extractor/course_checks.py")
text = SCRIPT.read_text(encoding="utf-8")
RULE = "# ---------------------------------------------------------------- "


def between(start: str, end: str) -> str:
    a = text.index(start)
    return text[a : text.index(end, a)]


MODULE_HEAD = '''"""Course-level checks of prospectus extractor output against its markup twin and the source PDF.

Pure functions; the only I/O is `load_pdf_pages`, `sha256`, `manifest_index` and `resolve_pdf`. The
audit script (scripts/prospectus_course_audit.py) and the year/semester verifier (verify.py) both
call them, so a check is written once.

Checks, per course unless noted (status values: match, loose, transformed, fail, empty,
not_checked; C and D use silent / flagged):
  A  JSON -> MD   A_prov A_code A_title A_lecture A_lab A_total A_prereq
  B  JSON -> PDF  B_code B_title B_units
  C  PDF -> JSON  (per printed candidate) code-like strings no course accounts for
  D  MD -> JSON   (per cell) code-like .md cells that no course claims

Normalisation (strict tier): Unicode NFC, whitespace runs to one space, trim. PDF text also maps
U+FFFE and U+00AD to "-" and "". Loose tier: whitespace and hyphen/dash characters removed.
Reuse for OCR output: pass pdf_pages = {page_no: PdfPage(text, chars, height)} from any source.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from .grid import is_probable_course_code

'''
dashes = between("DASHES = ", "DEFAULT_PDF_ROOT")
checks = between(RULE + "normalisation", RULE + "IO: manifest, PDFs, runs")
io = between("def sha256(", "def run_all(")
MODULE.write_text(MODULE_HEAD + dashes.rstrip() + "\n\n\n" + checks.rstrip() + "\n\n\n" + io.rstrip() + "\n", encoding="utf-8", newline="\n")

SCRIPT_IMPORTS = '''import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

# The checks live in the package so the year/semester verifier reuses them; the names below are
# re-exported so this script and its tests keep one import surface.
from backend.bintanong_tools.prospectus_extractor.course_checks import (  # noqa: E402,F401
    DASHES, MdDoc, PdfPage, audit_file, check_course_md, check_course_pdf, check_md_unclaimed,
    check_pdf_missed, course_roles, load_pdf_pages, loose, manifest_index, normalise, parse_markup,
    pdf_candidates, pdf_clean, resolve_pdf, sha256, text_in_box,
)

'''
default_root = between("DEFAULT_PDF_ROOT", RULE + "normalisation").rstrip()
head = text[: text.index("import argparse")]
SCRIPT.write_text(head + SCRIPT_IMPORTS + default_root + "\n\n\n" + text[text.index("def run_all(") :], encoding="utf-8", newline="\n")
print("moved:", MODULE, MODULE.stat().st_size, "bytes;", SCRIPT, SCRIPT.stat().st_size, "bytes")
```

```powershell
uv run --project backend --extra tools --extra dev python "$env:TEMP\move_course_checks.py"
uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_course_checks.py tests/test_prospectus_course_audit.py
```

Expected: the script prints the two sizes; pytest: `1 failed, 12 passed`. The failing test is `test_pdf_check_without_a_markup_twin_says_so_and_names_the_occurrence` (`AttributeError: 'NoneType' object has no attribute 'cells'`); the identity test and the 11 existing audit tests pass.

- [ ] **Step 4: Make the PDF-miss check work without a markup twin and report the occurrence**

In `backend/bintanong_tools/prospectus_extractor/course_checks.py` make two edits.

Replace

```python
def _md_location(key, md: MdDoc) -> str:
```

with

```python
def _md_location(key, md: MdDoc | None) -> str:
    if md is None:  # no markup twin available (the verifier works from the JSON alone)
        return "unknown"
```

and in `check_pdf_missed`, replace `| {"page": page_no, "md_location": where})` with `| {"page": page_no, "md_location": where, "occurrence": seen[key]})`.

- [ ] **Step 5: Run the tests and a real-data smoke**

```powershell
uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_course_checks.py tests/test_prospectus_course_audit.py
$d = 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump'
uv run --project backend --extra tools --extra dev python scripts/prospectus_course_audit.py --runs "$d\scratch\compare_2026-10-03b\new" --golden "$d\docling_jsonified_output\task2b_standing_isolated_2026-09-29" --out "$env:TEMP\b2-audit-smoke" --limit 2
```

Expected: `13 passed`. The audit prints (first two inputs, BSA and ABComm) `A_prov {'match': 127}`, `B_title {'match': 105, 'fail': 21, 'loose': 1}` and `C {}`: the same numbers as before the move.

- [ ] **Step 6: Full suite, progress note, commit**

Run the full suite (expected `95 passed`, 13 subtests passed). Add a row to the progress table: `2. Move course checks | done | <hash> | red: collection error; after move 1 failed 12 passed; green 13 passed; audit smoke identical; full suite 95`.

```powershell
git add tests/test_prospectus_course_checks.py backend/bintanong_tools/prospectus_extractor/course_checks.py scripts/prospectus_course_audit.py plans/plan_current_progress/extractor_split_progress.md
git commit -m "refactor: move the course-audit checks into the package so the verifier can reuse them" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: Banner text helpers, real-topology fixtures, and the verifier core (tests first)

**Why:** one function turns a candidate into year x semester sections in printed order with flags and a health per section. This task does the checks that need only the JSON: banner text in fields (check 1), printed term totals (2), a course in two terms or none (4), a prerequisite in the same or a later term (5), plus the section ids, row ids and health.

**Files:**
- Create: `tests/fixer_fixtures.py`, `tests/test_prospectus_verify.py`
- Modify: `backend/bintanong_tools/prospectus_extractor/text.py` (insert before `def match_year_label`)
- Create: `backend/bintanong_tools/prospectus_extractor/verify.py` (first version; Tasks 4 and 5 edit it)

- [ ] **Step 1: Write the fixtures**

Cell texts, spans and boxes below are copied from the real Docling output in the cached run (BS Computer Science 2025-2026 `t0-c8`/`t0-c9`; BS Architecture `t0-c10` and the glued `Techniques 1` title; BS Entrepreneurship Innovation and Tech, where only the 4th-year rows were parsed). They are trimmed to a few courses. The PDF excerpt is a few printed lines of course titles. No PDF is stored.

`tests/fixer_fixtures.py`:

```python
"""Candidate-payload builders for the section verifier, fixer, ledger and review-sheet tests.

Cell texts, spans and boxes are copied from real Docling output in the cached task2b run
(BS Computer Science 2025-2026, BS Architecture, BS Entrepreneurship Innovation and Tech). They
are trimmed to a few courses each. No PDF is stored; PDF text below is a short excerpt.
"""

from __future__ import annotations

from backend.bintanong_tools.prospectus_extractor.text import term_index
from backend.bintanong_tools.prospectus_extractor.units import parse_units

T11 = ("1st Year", "1st Semester")
T12 = ("1st Year", "2nd Semester")


def cell(cid, text, r0, c0, c1, bbox=None, *, r1=None, page=1, table=0):
    return {
        "cell_id": cid, "table_index": table, "text": text, "raw_text": text,
        "row_start": r0, "row_end": r1 if r1 is not None else r0 + 1,
        "col_start": c0, "col_end": c1, "page": page, "bbox": bbox,
    }


def course(code, title, units, term, row, group, cells, *, title_raw=None, prereq="", prereq_list=(), page=1):
    year, semester = term
    units_dict = parse_units(units)
    boxes = [c["bbox"] for c in cells if c["bbox"]]
    union = (
        [min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes)]
        if boxes else None
    )
    return {
        "year_level": year, "semester": semester,
        "term_index": term_index(year or "", semester or ""),
        "course_code": code, "course_title": title,
        "title_raw": title if title_raw is None else title_raw, "footnote_marker": None,
        "units": units_dict, "total_units": units_dict["total"],
        "lecture_units": units_dict["lecture"], "lab_units": units_dict["lab"],
        "prerequisites_raw": prereq, "prerequisites": list(prereq_list),
        "prerequisites_unresolved": [], "confidence_flags": [],
        "provenance": {
            "page": page, "bbox": union, "valid": True, "highlightable": union is not None,
            "source_cell_ids": [c["cell_id"] for c in cells], "source_cells": cells,
        },
        "_source": {"table_index": 0, "row_index": row, "column_group": group},
        "code": code, "title": title,
    }


def payload(courses, *, layout, declared=None, evidence_cells=(), errors=(), unclaimed=(), name="Test Program"):
    """declared: {(year, semester): printed term total}. Computed totals come from the courses."""
    declared = declared or {}
    terms = sorted({(c["year_level"], c["semester"]) for c in courses if c["year_level"] and c["semester"]},
                   key=lambda t: term_index(*t))
    term_audit = [
        {"year_level": y, "semester": s, "declared_units": declared.get((y, s)),
         "computed_units": sum(c["total_units"] or 0 for c in courses if (c["year_level"], c["semester"]) == (y, s)),
         "course_count": sum(1 for c in courses if (c["year_level"], c["semester"]) == (y, s)),
         "matches": declared.get((y, s)) is None
         or declared[(y, s)] == sum(c["total_units"] or 0 for c in courses if (c["year_level"], c["semester"]) == (y, s))}
        for y, s in terms
    ]
    return {
        "program": name, "source_path": "x/x_docling.json",
        "courses": courses,
        "audit": {
            "status": "error" if errors else "ok", "errors": list(errors),
            "term_unit_audit": term_audit, "table_layout": layout,
            "curriculum_sections": [{"table_index": 0, "evidence_cells": list(evidence_cells)}],
            "unclaimed_course_candidates": list(unclaimed),
            "duplicate_course_codes": [],
        },
    }


# --- BS Computer Science 2025-2026: cell t0-c9 is a title cell that starts with the semester banner

BSCS_LAYOUT = [{"table_index": 0, "column_groups": [
    {"index": 0, "code_idx": 0, "title_idx": 1, "unit_idx": 2, "prereq_idx": 3},
    {"index": 1, "code_idx": 4, "title_idx": 5, "unit_idx": 6, "prereq_idx": 7},
]}]
BSCS_YEAR = cell("t0-c8", "FIRST YEAR", 1, 0, 8, [261.0, 173.6, 554.9, 183.5])
BSCS_TITLE_WITH_BANNER = cell("t0-c9", "FIRST SEMESTER Discrete Structures 1 1", 3, 1, 2, [103.4, 187.6, 210.2, 205.7])


def bscs():
    """Four first-year courses; printed term totals are set to the sums so the sections are clean."""
    cs1 = course("CS 1", "Discrete Structures 1", "3", T11, 3, 0, [
        cell("t0-c11", "CS 1", 3, 0, 1, [64.4, 195.6, 82.3, 205.5]), BSCS_TITLE_WITH_BANNER,
        cell("t0-c12", "3", 3, 2, 3, [246.7, 195.3, 259.7, 205.4]), BSCS_YEAR], title_raw="Discrete Structures 1 1")
    cc1 = course("CC 1/L", "Introduction to Computing", "2/1", T11, 4, 0, [
        cell("t0-c17", "CC 1/L", 4, 0, 1, [61.7, 205.2, 84.1, 215.3]),
        cell("t0-c18", "Introduction to Computing", 4, 1, 2, [99.8, 205.0, 181.7, 215.2]),
        cell("t0-c19", "2/1", 4, 2, 3, [246.7, 205.1, 260.1, 215.3]), BSCS_YEAR, BSCS_TITLE_WITH_BANNER])
    cs2 = course("CS 2", "Discrete Structures 2", "3", T12, 3, 1, [
        cell("t0-c13", "CS 2", 3, 4, 5, [322.2, 195.0, 340.1, 204.6]),
        cell("t0-c14", "Discrete Structures 2 2", 3, 5, 6, [364.7, 195.0, 433.6, 204.9]),
        cell("t0-c15", "3", 3, 6, 7, [494.2, 195.0, 507.2, 205.1]),
        cell("t0-c16", "CS 1", 3, 7, 8, [524.4, 194.1, 544.4, 203.9]), BSCS_YEAR, BSCS_TITLE_WITH_BANNER],
        title_raw="Discrete Structures 2 2", prereq="CS 1", prereq_list=["CS 1"])
    cc3 = course("CC 3/L", "Computer Programming 2", "2/1", T12, 4, 1, [
        cell("t0-c20", "CC 3/L", 4, 4, 5, [320.0, 205.2, 342.0, 215.3]),
        cell("t0-c21", "Computer Programming 2", 4, 5, 6, [364.0, 205.0, 440.0, 215.2]),
        cell("t0-c22", "2/1", 4, 6, 7, [494.0, 205.1, 508.0, 215.3]),
        cell("t0-c23", "CC 2/L", 4, 7, 8, [524.0, 205.1, 546.0, 215.3]), BSCS_YEAR, BSCS_TITLE_WITH_BANNER],
        prereq="CC 2/L")
    return payload([cs1, cc1, cs2, cc3], layout=BSCS_LAYOUT, evidence_cells=["t0-c8", "t0-c9"],
                   declared={T11: 6, T12: 6}, name="BS Computer Science")


# --- BS Architecture: wide banner cell t0-c10 spans the code columns; Docling glued a wrapped
# title line ("Techniques 1") to the start of the next row's title (GE-PC).

ARCH_LAYOUT = [{"table_index": 0, "column_groups": [
    {"index": 0, "code_idx": 1, "title_idx": 2, "unit_idx": 3, "prereq_idx": 4},
    {"index": 1, "code_idx": 6, "title_idx": 7, "unit_idx": 8, "prereq_idx": 9},
]}]
ARCH_BANNER = cell("t0-c10", "FIRST YEAR FIRST SEMESTER SECOND SEMESTER", 1, 1, 10, [69.6, 158.5, 553.8, 169.6])

ARCH_PAGE_TEXT = (
    "FIRST YEAR\r\nFIRST SEMESTER SECOND SEMESTER\r\n"
    "AD-1/L Architectural Design 1-Introduction to Design 1/1 AD-2/L Architectural Design 2-Creative Design and \r\n"
    "Fundamentals\r\n1/1 AD-1/L, \r\nTOA-1\r\n"
    "TOA-1/L Theory of Architecture1 2/1 GR-2/L Architectural Visual Communications 3-\r\nGraphics 2\r\n1/2 GR-1/L\r\n"
    "VT-1/L Architectural Visual Communications 2-Visual \r\nTechniques 1\r\n1/1 VT-2/L Architectural Visual "
    "Communications 4-Visual \r\nTechniques 2\r\n1/1 VT-1/L\r\n"
    "GE-PC Purposive Communication 3 TOA-2 Theory of Architecture 2 3 TOA-1\r\n"
)


def architecture():
    ad1 = course("AD-1/L", "Architectural Design 1-Introduction to Design", "1/1", T11, 2, 0, [
        cell("t0-c11", "AD-1/L", 2, 1, 2, [69.6, 170.0, 93.8, 180.3]),
        cell("t0-c12", "Architectural Design 1-Introduction to Design", 2, 2, 3, [110.1, 171.4, 243.1, 182.0]),
        cell("t0-c13", "1/1", 2, 3, 4, [251.7, 170.9, 268.0, 181.4]), ARCH_BANNER])
    toa1 = course("TOA-1/L", "1 Theory of Architecture1", "2/1", T11, 4, 0, [
        cell("t0-c26", "TOA-1/L", 4, 1, 2, [70.6, 198.9, 97.2, 209.0]),
        cell("t0-c22", "1 Theory of Architecture1", 4, 2, 3, [105.9, 198.9, 226.3, 209.4]),
        cell("t0-c27", "2/1", 4, 3, 4, [253.4, 199.0, 267.6, 209.6]), ARCH_BANNER])
    vt1 = course("VT-1/L", "Architectural Visual Communications 2-Visual", "1/1", T11, 5, 0, [
        cell("t0-c33", "VT-1/L", 5, 1, 2, [70.1, 214.0, 96.9, 224.1]),
        cell("t0-c34", "Architectural Visual Communications 2-Visual", 5, 2, 3, [109.1, 213.8, 241.8, 224.5]),
        cell("t0-c36", "1/1", 5, 3, 4, [254.0, 214.5, 267.1, 224.9]), ARCH_BANNER])
    gepc = course("GE-PC", "Techniques 1 Purposive Communication", "3", T11, 6, 0, [
        cell("t0-c41", "GE-PC", 6, 1, 2, [70.7, 228.3, 94.5, 238.4]),
        cell("t0-c35", "Techniques 1 Purposive Communication", 6, 2, 3, [107.4, 228.1, 208.1, 238.3]),
        cell("t0-c42", "3", 6, 3, 4, [254.4, 229.0, 266.8, 239.3]), ARCH_BANNER])
    ad2 = course("AD-2/L", "Architectural Design 2-Creative Design and", "1/1", T12, 2, 1, [
        cell("t0-c14", "AD-2/L", 2, 6, 7, [339.9, 170.6, 368.5, 180.7]),
        cell("t0-c15", "Architectural Design 2-Creative Design and", 2, 7, 8, [377.4, 171.9, 497.1, 182.4]),
        cell("t0-c17", "1/1", 2, 8, 9, [513.1, 170.3, 529.3, 181.0]),
        cell("t0-c18", "AD-1/L,", 2, 9, 10, [534.9, 170.1, 562.5, 180.2]), ARCH_BANNER],
        prereq="AD-1/L,", prereq_list=["AD-1/L"])
    vt2 = course("VT-2/L", "Graphics 2 Architectural Visual Communications 4-Visual", "1/1", T12, 5, 1, [
        cell("t0-c37", "VT-2/L", 5, 6, 7, [340.1, 214.3, 364.4, 224.1]),
        cell("t0-c30", "Graphics 2 Architectural Visual Communications 4-Visual", 5, 7, 8, [375.5, 213.1, 487.8, 223.7]),
        cell("t0-c39", "1/1", 5, 8, 9, [514.4, 214.4, 527.7, 225.0]),
        cell("t0-c40", "VT-1/L", 5, 9, 10, [537.1, 214.2, 558.5, 224.4]), ARCH_BANNER],
        prereq="VT-1/L", prereq_list=["VT-1/L"])
    toa2 = course("TOA-2", "Techniques 2 Theory of Architecture 2", "3", T12, 6, 1, [
        cell("t0-c43", "TOA-2", 6, 6, 7, [340.8, 228.7, 361.7, 238.6]),
        cell("t0-c38", "Techniques 2 Theory of Architecture 2", 6, 7, 8, [380.6, 228.9, 443.5, 239.3]),
        cell("t0-c44", "3", 6, 8, 9, [516.1, 228.7, 527.7, 239.3]),
        cell("t0-c45", "TOA-1", 6, 9, 10, [538.4, 227.6, 559.7, 237.8]), ARCH_BANNER], prereq="TOA-1")
    return payload([ad1, toa1, vt1, gepc, ad2, vt2, toa2], layout=ARCH_LAYOUT, evidence_cells=["t0-c10"],
                   declared={T11: 10, T12: 7}, name="BS Architecture")


# --- BS Entrepreneurship Innovation and Tech: only the 4th-year rows were parsed; fifteen printed
# codes above the "FOURTH YEAR" banner were left unclaimed (audit.unclaimed_course_candidates).

INNOV_LAYOUT = [{"table_index": 0, "column_groups": [
    {"index": 0, "code_idx": 1, "title_idx": 2, "unit_idx": 3, "prereq_idx": 4},
    {"index": 1, "code_idx": 5, "title_idx": 6, "unit_idx": 7, "prereq_idx": 8},
]}]
INNOV_YEAR = cell("t0-c62", "FOURTH YEAR", 9, 0, 9, [279.5, 782.3, 337.4, 789.5])
INNOV_SEM = cell("t0-c63", "FIRST SEMESTER SECOND SEMESTER", 10, 0, 9, [136.4, 792.3, 483.6, 799.5])
Y4 = ("4th Year", "1st Semester")
Y4B = ("4th Year", "2nd Semester")


def innovation():
    e14 = course("ENTRE 14", "Business Implementation 1", "5", Y4, 11, 0, [
        cell("t0-c64", "ENTRE 14", 11, 1, 2, [71.2, 802.6, 98.3, 818.9]),
        cell("t0-c65", "Business Implementation 1", 11, 2, 3, [107.2, 802.6, 203.1, 809.7]),
        cell("t0-c66", "5", 11, 3, 4, [247.5, 802.6, 251.9, 809.7]),
        cell("t0-c67", "ENTRE 10", 11, 4, 5, [272.1, 802.6, 299.2, 818.9]), INNOV_YEAR, INNOV_SEM],
        prereq="ENTRE 10")
    e15 = course("ENTRE 15", "Business Implementation 2", "5", Y4B, 11, 1, [
        cell("t0-c68", "ENTRE 15", 11, 5, 6, [345.5, 802.6, 372.6, 818.9]),
        cell("t0-c69", "Business Implementation 2", 11, 6, 7, [390.5, 802.6, 486.4, 809.7]),
        cell("t0-c70", "5", 11, 7, 8, [522.4, 802.6, 526.8, 809.7]),
        cell("t0-c71", "ENTRE 14", 11, 8, 9, [546.8, 802.6, 573.9, 818.9]), INNOV_YEAR, INNOV_SEM],
        prereq="ENTRE 14", prereq_list=["ENTRE 14"])

    def unclaimed(code, cid, bbox):
        return {"code": code, "normalized_code": code.replace(" ", ""), "cell_ids": [cid], "table_index": 0,
                "page": 1, "bbox": bbox, "confidence": "high"}

    items = [unclaimed("ENTRE 7", "t0-c0", [71.2, 579.5, 98.3, 595.9]),
             unclaimed("GE-IER", "t0-c4", [345.5, 584.1, 373.1, 591.3]),
             unclaimed("ENTRE 9", "t0-c54", [71.2, 749.0, 98.3, 765.0])]
    errors = ["Document declares a total for 1st Year 1st Semester but no courses were extracted there.",
              "3 high-confidence source course code(s) were not claimed by the parser."]
    return payload([e14, e15], layout=INNOV_LAYOUT, evidence_cells=["t0-c62", "t0-c63"], declared={Y4: 5, Y4B: 5},
                   errors=errors, unclaimed=items, name="BS Entrepreneurship Innovation and Tech")


# --- reading helpers for tests

def kinds(row):
    return [f.kind for f in row.flags]


def section(verification, sid):
    return next(s for s in verification.sections if s.sid == sid)


def by_code(payload, verification):
    return {payload["courses"][r.course]["course_code"]: r for s in verification.sections for r in s.rows if r.course is not None}
```

- [ ] **Step 2: Write the failing tests**

`tests/test_prospectus_verify.py`:

```python
import copy

import pytest

from backend.bintanong_tools.prospectus_extractor.text import has_banner_text, leading_banner, trailing_banner
from backend.bintanong_tools.prospectus_extractor.verify import verify_candidate

import fixer_fixtures as fx
from fixer_fixtures import by_code, kinds, section



# --- banner text helpers (also used by the parser split in the last task)

@pytest.mark.parametrize("text,banner,rest", [
    ("FIRST YEAR FIRST SEMESTER SECOND SEMESTER Discrete Structures", "FIRST YEAR FIRST SEMESTER SECOND SEMESTER", "Discrete Structures"),
    ("FIRST SEMESTER Discrete Structures 1 1", "FIRST SEMESTER", "Discrete Structures 1 1"),
    ("FIRST Ethics", "FIRST", "Ethics"),
    ("SECOND SEMESTER", "SECOND SEMESTER", ""),
    ("Discrete Structures", "", "Discrete Structures"),
    ("First Aid", "", "First Aid"),            # title case is a real title
    ("Summer Internship", "", "Summer Internship"),
])
def test_leading_banner(text, banner, rest):
    assert leading_banner(text) == (banner, rest)


def test_trailing_banner_and_has_banner_text():
    assert trailing_banner("Practicum FOURTH YEAR FIRST SEMESTER") == ("Practicum", "FOURTH YEAR FIRST SEMESTER")
    assert trailing_banner("Practicum") == ("Practicum", "")
    assert has_banner_text("EE FIRST SEMESTER Environmental Engineering")
    assert has_banner_text("FIRST Ethics")
    assert not has_banner_text("First Aid") and not has_banner_text("Summer Internship") and not has_banner_text("3RD YEAR".lower())


# --- sections, ids, order, totals

def test_a_clean_candidate_has_clean_sections_in_printed_order():
    payload = fx.bscs()
    v = verify_candidate(payload)
    assert [(s.sid, s.year, s.semester, s.health) for s in v.sections] == [
        ("S1", "1st Year", "1st Semester", "clean"), ("S2", "1st Year", "2nd Semester", "clean")]
    assert [r.rid for r in section(v, "S1").rows] == ["S1-01", "S1-02"]
    assert (section(v, "S1").declared, section(v, "S1").computed) == (6, 6)
    assert v.health == "clean" and v.pdf_checked is False and v.counts() == {}


def test_banner_text_in_the_courses_own_cell_is_info_and_banner_cells_of_other_courses_are_ignored():
    payload = fx.bscs()
    rows = by_code(payload, verify_candidate(payload))
    assert kinds(rows["CS 1"]) == ["banner_in_cell"] and rows["CS 1"].flags[0].severity == "info"
    for code in ("CC 1/L", "CS 2", "CC 3/L"):  # t0-c9 rides along in their provenance as section context
        assert kinds(rows[code]) == [], code


def test_banner_text_still_in_a_field_is_an_error_and_breaks_the_section():
    payload = fx.bscs()
    payload["courses"][1]["course_title"] = "EE FIRST SEMESTER Introduction to Computing"
    v = verify_candidate(payload)
    row = by_code(payload, v)["CC 1/L"]
    assert kinds(row) == ["banner_leak"] and row.flags[0].severity == "error"
    assert row.fixes == []  # banner in the middle of a title: flag only, no guess where the title starts
    assert section(v, "S1").health == "broken" and v.health == "mixed"


def test_a_standing_rule_in_the_prerequisite_is_not_banner_text():
    payload = fx.bscs()
    payload["courses"][2]["prerequisites_raw"] = "3RD YEAR STANDING"
    assert kinds(by_code(payload, verify_candidate(payload))["CS 2"]) == []


def test_unit_total_mismatch_is_a_section_error_with_the_difference():
    payload = fx.architecture()
    payload["audit"]["term_unit_audit"][0]["declared_units"] = 11
    v = verify_candidate(payload)
    s1 = section(v, "S1")
    assert [f.kind for f in s1.flags] == ["unit_total"] and "printed total 11, extracted 10 (-1)" in s1.flags[0].message
    assert s1.health == "broken" and section(v, "S2").health == "clean"
    assert v.counts() == {"unit_total": 1}


def test_a_printed_total_for_a_term_with_no_courses_gets_an_empty_section():
    payload = fx.innovation()
    v = verify_candidate(payload)
    assert [(s.sid, s.year, s.semester, len(s.rows)) for s in v.sections if s.sid != "SU"] == [
        ("S1", "1st Year", "1st Semester", 0), ("S2", "4th Year", "1st Semester", 1), ("S3", "4th Year", "2nd Semester", 1)]
    assert section(v, "S1").flags[0].kind == "unit_total" and section(v, "S1").health == "broken"


def test_course_in_two_terms_or_none():
    payload = fx.bscs()
    twin = copy.deepcopy(payload["courses"][0])
    twin["year_level"], twin["semester"], twin["term_index"] = "2nd Year", "1st Semester", 21
    twin["provenance"]["source_cell_ids"] = ["t9-c1"]
    lost = copy.deepcopy(payload["courses"][1])
    lost["year_level"] = lost["semester"] = None
    lost["course_code"] = "ZZ 9"
    lost["provenance"]["source_cell_ids"] = ["t9-c2"]
    payload["courses"] += [twin, lost]
    v = verify_candidate(payload)
    rows = {payload["courses"][r.course]["provenance"]["source_cell_ids"][0]: r for s in v.sections for r in s.rows if r.course is not None}
    assert "duplicate_course" in kinds(rows["t0-c11"]) and "duplicate_course" in kinds(rows["t9-c1"])
    assert kinds(rows["t9-c2"]) == ["no_term"]
    assert [s.sid for s in v.sections][-1] == "SN" and section(v, "SN").title == "No year or semester"


def test_prerequisite_in_the_same_or_a_later_term_is_a_warning():
    payload = fx.bscs()
    payload["courses"][0]["prerequisites"] = ["CS 2"]       # CS 2 is in the next semester
    payload["courses"][2]["prerequisites"] = ["CC 3/L"]     # same semester
    v = verify_candidate(payload)
    rows = by_code(payload, v)
    assert "prereq_order" in kinds(rows["CS 1"]) and "prereq_order" in kinds(rows["CS 2"])
    assert section(v, "S1").health == "review" and v.health == "warnings_only"


# --- unclaimed printed codes and where they sit


def test_health_overall_vocabulary_without_unclaimed_codes():
    assert verify_candidate(fx.bscs()).health == "clean"
    payload = fx.architecture()
    payload["audit"]["term_unit_audit"][0]["declared_units"] = 11
    assert verify_candidate(payload).health == "mixed"
    one_section = fx.bscs()
    one_section["courses"] = one_section["courses"][:2]          # a single term section: not enough to call it sound
    assert verify_candidate(one_section).health == "broken"
```

- [ ] **Step 3: Run them to see them fail**

```powershell
uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_verify.py
```

Expected: collection error, `ImportError: cannot import name 'has_banner_text' from 'backend.bintanong_tools.prospectus_extractor.text'`.

- [ ] **Step 4: Add the banner text helpers**

Insert this block in `backend/bintanong_tools/prospectus_extractor/text.py` immediately before `def match_year_label(text: str) -> str | None:` (two blank lines on each side). The same helpers serve the parser split in Task 13.

```python
_ORDINAL = r"(?:FIRST|SECOND|THIRD|FOURTH|FIFTH|1ST|2ND|3RD|4TH|5TH)"
_BANNER_UNIT = rf"(?:{_ORDINAL}\s+YEAR|{_ORDINAL}\s+SEM(?:ESTER)?|SEMESTER|SUMMER|MID[\s-]?YEAR)"


# Exact, upper-case printed banner phrases ("FIRST YEAR", "SECOND SEMESTER", "SUMMER", ...).
# Upper case only, so a real title such as "First Aid" or "Summer Internship" never matches.
BANNER_PHRASE = re.compile(rf"\b{_BANNER_UNIT}\b")


_LEADING_BANNER = re.compile(rf"^(?:(?:{_BANNER_UNIT}|{_ORDINAL})\b\s*)+")


_TRAILING_BANNER = re.compile(rf"\s+{_BANNER_UNIT}\s*$")


_LEADING_ORDINAL_WORD = re.compile(rf"^{_ORDINAL}\s+(?=[A-Z][a-z])")


def has_banner_text(text: str) -> bool:
    """True when `text` carries a printed banner phrase, or starts with an upper-case ordinal
    word glued to a capitalised word ("FIRST Ethics", the tail of a wrapped "FIRST SEMESTER")."""
    value = clean_str(text)
    return bool(BANNER_PHRASE.search(value) or _LEADING_ORDINAL_WORD.match(value))


def leading_banner(text: str) -> tuple[str, str]:
    """Split `text` into (banner, rest): the run of banner phrases at its start and what follows.
    ("", text) when it does not start with one. rest is "" when the whole text is banner."""
    value = clean_str(text)
    match = _LEADING_BANNER.match(value)
    if not match:
        return "", value
    return match.group().strip(), clean_str(value[match.end():])


def trailing_banner(text: str) -> tuple[str, str]:
    """Split `text` into (rest, banner): banner phrases at its end. (text, "") when none."""
    value = clean_str(text)
    banner = ""
    while True:
        match = _TRAILING_BANNER.search(value)
        if not match:
            return value, banner
        banner = clean_str(f"{match.group().strip()} {banner}")
        value = value[: match.start()]
```

- [ ] **Step 5: Create the verifier core**

`backend/bintanong_tools/prospectus_extractor/verify.py`:

```python
"""Year/semester verifier: per-section flags, fix proposals and a health status for one candidate.

Reads a candidate payload (and, when given, the PDF text layer) and groups the courses into
year x semester sections in printed order. Nothing here changes a value. A section is:
  clean    no flag above `info`
  review   only `warn` flags (a prerequisite order, a title or code not found in the PDF text)
  broken   at least one `error` flag (banner text in a field, printed total mismatch, a course in
           two terms or none, a printed code no course claimed)
Flag kinds: banner_leak, unit_total, code_not_in_pdf, title_not_in_pdf, duplicate_course, no_term,
prereq_order, unclaimed_code, audit_anomaly (and `banner_in_cell`, info only).
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from .prerequisites import is_standing_rule
from .text import SEMESTER_ORDER, YEAR_ORDER, clean_str, has_banner_text, norm_key, term_index

ERROR, WARN, INFO = "error", "warn", "info"
NO_TERM, UNPLACED = "SN", "SU"
EMPTY_DECLARED = re.compile(
    r"Document declares a total for (\d\w\w Year) (.+?) but no courses were extracted there\."
)


@dataclass(frozen=True)
class Flag:
    kind: str
    severity: str
    message: str
    field: str | None = None


@dataclass
class Row:
    rid: str
    course: int | None = None   # index into payload["courses"]; None for an unclaimed printed code
    item: dict | None = None    # the unclaimed printed code: source, code, page, bbox, cell_ids, snippet
    flags: list[Flag] = field(default_factory=list)
    fixes: list[tuple[str, Any]] = field(default_factory=list)   # (letter, Fix)

    def worst(self) -> str | None:
        severities = {f.severity for f in self.flags}
        return ERROR if ERROR in severities else WARN if WARN in severities else None


@dataclass
class Section:
    sid: str
    year: str | None
    semester: str | None
    rows: list[Row] = field(default_factory=list)
    declared: int | None = None
    computed: int = 0
    flags: list[Flag] = field(default_factory=list)   # section-level: unit_total
    health: str = "clean"

    @property
    def title(self) -> str:
        if self.sid == UNPLACED:
            return "Unplaced printed codes"
        if self.sid == NO_TERM:
            return "No year or semester"
        return f"{self.year} - {self.semester}"


@dataclass
class Verification:
    sections: list[Section]
    pdf_checked: bool
    health: str

    def counts(self) -> dict[str, int]:
        """error and warn flags by kind, for comparing two runs of the extractor."""
        out: Counter = Counter()
        for section in self.sections:
            for flag in section.flags + [f for row in section.rows for f in row.flags]:
                if flag.severity != INFO:
                    out[flag.kind] += 1
        return dict(sorted(out.items()))


def own_role_cells(course: Mapping[str, Any], layout: Sequence[Mapping[str, Any]], evidence_ids: set[str]) -> dict[str, list]:
    """The course's own single-column cells by role. Section banner cells ride along in every
    course's provenance; they are left out unless they are also this course's own row cell
    (BS Computer Science t0-c9 is both the semester banner and the title of CS 1)."""
    src = course.get("_source") or {}
    table = next((t for t in layout if t.get("table_index") == src.get("table_index")), None)
    group = next((g for g in (table or {}).get("column_groups") or [] if g.get("index") == src.get("column_group")), None)
    roles: dict[str, list] = {"code": [], "title": [], "unit": [], "prereq": []}
    if not group:
        return roles
    by_col = {group.get(f"{r}_idx"): r for r in roles if group.get(f"{r}_idx") is not None}
    row = src.get("row_index")
    for cell in (course.get("provenance") or {}).get("source_cells") or []:
        if cell.get("col_end", 0) - cell.get("col_start", 0) != 1 or cell.get("col_start") not in by_col:
            continue
        on_row = row is not None and cell.get("row_start", -1) <= row < cell.get("row_end", -1)
        if cell.get("cell_id") in evidence_ids and not on_row:
            continue
        roles[by_col[cell["col_start"]]].append(cell)
    return roles


def _term_of(course: Mapping[str, Any]) -> int:
    return course.get("term_index") or term_index(course.get("year_level") or "", course.get("semester") or "")


def _course_flags(index, course, ctx) -> list[Flag]:
    flags: list[Flag] = []
    roles = own_role_cells(course, ctx["layout"], ctx["evidence_ids"])
    for name in ("course_code", "course_title", "prerequisites_raw"):
        value = clean_str(course.get(name))
        if not value or (name == "prerequisites_raw" and is_standing_rule(value)):
            continue
        if has_banner_text(value):
            flags.append(Flag("banner_leak", ERROR, f'{name} holds banner text: "{value}"', name))
    for role, name in (("code", "course_code"), ("title", "course_title")):
        for cell in roles[role]:
            if has_banner_text(cell.get("text") or "") and not has_banner_text(course.get(name) or ""):
                flags.append(Flag("banner_in_cell", INFO, f'cell {cell["cell_id"]} carried banner text; the parser removed it from the {role}', name))
    year, semester = course.get("year_level"), course.get("semester")
    if not year or not semester:
        flags.append(Flag("no_term", ERROR, "no verified year or semester"))
    key = norm_key(course.get("course_code") or "")
    if ctx["code_count"][key] > 1:
        others = sorted({f"{o.get('year_level')} {o.get('semester')}" for i, o in enumerate(ctx["courses"])
                         if i != index and norm_key(o.get("course_code") or "") == key})
        flags.append(Flag("duplicate_course", ERROR, f"code appears again in: {', '.join(others)}", "course_code"))
    elif year and semester:
        here = _term_of(course)
        for prereq in course.get("prerequisites") or []:
            there = ctx["positions"].get(prereq)
            if there is not None and there >= here:
                flags.append(Flag("prereq_order", WARN, f"prerequisite {prereq} is in the same or a later term", "prerequisites_raw"))
    return flags


def _health(section: Section) -> str:
    severities = {f.severity for f in section.flags} | {f.severity for r in section.rows for f in r.flags}
    return "broken" if ERROR in severities else "review" if WARN in severities else "clean"


def _overall(sections: Sequence[Section]) -> str:
    """clean | warnings_only | mixed | broken. Broken: most sections broken, or fewer than two term sections."""
    terms = [s for s in sections if s.sid not in (NO_TERM, UNPLACED)]
    broken = sum(s.health == "broken" for s in sections)
    if len(terms) < 2 or broken * 2 > len(sections):
        return "broken"
    if all(s.health == "clean" for s in sections):
        return "clean"
    return "mixed" if broken else "warnings_only"


def verify_candidate(payload: Mapping[str, Any]) -> Verification:
    courses = payload.get("courses") or []
    audit = payload.get("audit") or {}
    layout = audit.get("table_layout") or []
    evidence_ids = {i for s in audit.get("curriculum_sections") or [] for i in s.get("evidence_cells") or []}
    code_count = Counter(norm_key(c.get("course_code") or "") for c in courses)
    ctx = {
        "courses": courses, "layout": layout, "evidence_ids": evidence_ids,
        "code_count": code_count, "codes": [c.get("course_code") or "" for c in courses],
        "positions": {c.get("course_code"): _term_of(c) for c in courses
                      if code_count[norm_key(c.get("course_code") or "")] == 1 and c.get("year_level") and c.get("semester")},
    }
    declared = {(t["year_level"], t["semester"]): t.get("declared_units") for t in audit.get("term_unit_audit") or []}
    keys = {(c.get("year_level"), c.get("semester")) for c in courses if c.get("year_level") and c.get("semester")}
    empty = [(y, s) for e in audit.get("errors") or [] if (m := EMPTY_DECLARED.search(e)) for y, s in [m.groups()]]
    keys |= {t for t in empty if t[0] in YEAR_ORDER and t[1] in SEMESTER_ORDER}
    sections = [Section(f"S{n}", y, s, declared=declared.get((y, s)))
                for n, (y, s) in enumerate(sorted(keys, key=lambda t: term_index(*t)), 1)]
    by_term = {(s.year, s.semester): s for s in sections}
    loose_section = Section(NO_TERM, None, None)
    for index, course in enumerate(courses):
        section = by_term.get((course.get("year_level"), course.get("semester"))) or loose_section
        row = Row(f"{section.sid}-{len(section.rows) + 1:02d}", course=index)
        row.flags = _course_flags(index, course, ctx)
        section.rows.append(row)
        section.computed += course.get("total_units") or 0
    for section in sections:
        if (section.year, section.semester) in empty and not section.rows:
            section.flags.append(Flag("unit_total", ERROR, "a printed total exists for this term but no courses were extracted"))
        elif section.declared is not None and section.declared != section.computed:
            section.flags.append(Flag("unit_total", ERROR, f"printed total {section.declared}, extracted {section.computed} ({section.computed - section.declared:+d})"))
    sections += [s for s in (loose_section,) if s.rows]
    for section in sections:
        section.health = _health(section)
    return Verification(sections, False, _overall(sections))
```

- [ ] **Step 6: Run the tests, the self-test and the suite**

```powershell
uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_verify.py
uv run --project backend --extra tools --extra dev python -m backend.bintanong_tools.prospectus_extractor --self-test
uv run --project backend --extra tools --extra dev --with fastapi==0.141.1 python -m pytest -q tests
```

Expected: `17 passed`; `Self-test: 80/80 checks passed.`; full suite `112 passed`, 13 subtests passed.

- [ ] **Step 7: Progress note and commit**

Add a row: `3. Banner helpers, fixtures, verifier core | done | <hash> | red: ImportError has_banner_text; green 17 passed; full suite 112, self-test 80/80`.

```powershell
git add tests/fixer_fixtures.py tests/test_prospectus_verify.py backend/bintanong_tools/prospectus_extractor/text.py backend/bintanong_tools/prospectus_extractor/verify.py plans/plan_current_progress/extractor_split_progress.md
git commit -m "feat: verify year and semester sections of a candidate from its JSON" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: Fix proposals (tests first)

**Why:** H4. A proposal exists only where the text is already in the document: strip a leading or trailing banner from a code or title; move a course to the term its own cell's leading banner names; read a title from the PDF text when exactly one PDF row fits. Anything that would need invented text gets no proposal.

**Files:**
- Create: `tests/test_prospectus_fixes.py`
- Create: `backend/bintanong_tools/prospectus_extractor/fixes.py`
- Modify: `backend/bintanong_tools/prospectus_extractor/verify.py` (four small edits)

- [ ] **Step 1: Write the failing tests**

`tests/test_prospectus_fixes.py`:

```python
import pytest

from backend.bintanong_tools.prospectus_extractor.fixes import (
    format_term, parse_term, propose_fixes, strip_banner, title_from_pdf,
)
from backend.bintanong_tools.prospectus_extractor.verify import own_role_cells, verify_candidate

import fixer_fixtures as fx
from fixer_fixtures import by_code


@pytest.mark.parametrize("text,expected", [
    ("FIRST SEMESTER Discrete Structures 1", "Discrete Structures 1"),
    ("FIRST YEAR FIRST SEMESTER SECOND SEMESTER Discrete Structures", "Discrete Structures"),
    ("FIRST Ethics", "Ethics"),
    ("Practicum FOURTH YEAR", "Practicum"),
    ("EE FIRST SEMESTER Environmental Engineering", None),   # banner in the middle: no guess
    ("SECOND SEMESTER", None),                               # nothing left
    ("Discrete Structures", None),                           # nothing to strip
    ("First Aid", None),
])
def test_strip_banner(text, expected):
    assert strip_banner(text) == expected


def test_term_text_round_trip():
    assert format_term("2nd Year", "1st Semester") == "2nd Year / 1st Semester"
    assert parse_term("2nd Year / 1st Semester") == ("2nd Year", "1st Semester")
    assert parse_term("FIRST SEMESTER", default_year="3rd Year") == ("3rd Year", "1st Semester")
    assert parse_term("FIRST SEMESTER SECOND SEMESTER", default_year="3rd Year") is None
    assert parse_term("1st Semester") is None


def roles(course, payload):
    audit = payload["audit"]
    ids = {i for s in audit["curriculum_sections"] for i in s["evidence_cells"]}
    return own_role_cells(course, audit["table_layout"], ids)


def test_a_leading_banner_in_the_title_gets_a_strip_proposal_keyed_to_its_cell():
    payload = fx.bscs()
    course = payload["courses"][0]
    course["course_title"] = "FIRST SEMESTER Discrete Structures 1"
    fixes = propose_fixes(course, roles(course, payload))
    assert [(f.kind, f.field, f.old, f.new, f.fix_id) for f in fixes] == [
        ("strip_banner", "course_title", "FIRST SEMESTER Discrete Structures 1", "Discrete Structures 1",
         "strip_banner:course_title@t0-c9")]


def test_a_leading_banner_in_the_code_gets_a_strip_proposal():
    payload = fx.bscs()
    course = payload["courses"][0]
    course["course_code"] = "FIRST SEMESTER CS 1"
    fixes = propose_fixes(course, roles(course, payload))
    assert [(f.field, f.new) for f in fixes] == [("course_code", "CS 1")]


def test_a_banner_that_names_another_semester_proposes_a_move_but_one_that_names_both_does_not():
    payload = fx.bscs()
    course = payload["courses"][0]   # CS 1 sits in 1st Year / 1st Semester; its title cell is t0-c9
    cells = roles(course, payload)
    cells["title"][0] = {**cells["title"][0], "text": "SECOND SEMESTER Discrete Structures 1 1"}
    fixes = propose_fixes(course, cells)
    assert [(f.kind, f.field, f.old, f.new) for f in fixes] == [("move_term", "term", "1st Year / 1st Semester", "1st Year / 2nd Semester")]
    cells["title"][0] = {**cells["title"][0], "text": "FIRST SEMESTER SECOND SEMESTER Discrete Structures 1 1"}
    assert propose_fixes(course, cells) == []
    cells["title"][0] = {**cells["title"][0], "text": "FIRST YEAR SECOND SEMESTER Discrete Structures 1 1"}
    assert propose_fixes(course, cells)[0].new == "1st Year / 2nd Semester"


def test_the_real_bscs_banner_cell_agrees_with_the_course_so_no_move_is_proposed():
    payload = fx.bscs()
    assert all(propose_fixes(c, roles(c, payload)) == [] for c in payload["courses"])


def test_a_trailing_banner_names_the_next_section_and_never_moves_the_course():
    payload = fx.bscs()
    course = payload["courses"][0]
    cells = roles(course, payload)
    cells["title"][0] = {**cells["title"][0], "text": "Discrete Structures 1 SECOND SEMESTER"}
    assert propose_fixes(course, cells) == []


CODES = ["AD-1/L", "TOA-1/L", "VT-1/L", "VT-2/L", "GR-2/L", "GE-PC", "TOA-2", "AD-2/L"]


@pytest.mark.parametrize("code,units,current,expected", [
    ("TOA-1/L", "2/1", "1 Theory of Architecture1", "Theory of Architecture1"),
    ("GE-PC", "3", "Techniques 1 Purposive Communication", "Purposive Communication"),
    ("VT-1/L", "1/1", "Architectural Visual Communications 2-Visual", "Architectural Visual Communications 2-Visual Techniques 1"),
    ("AD-1/L", "1/1", "Architectural Design 1-Introduction to Design", None),   # already the printed title
])
def test_title_from_pdf_reads_the_one_matching_row(code, units, current, expected):
    assert title_from_pdf(code, units, current, fx.ARCH_PAGE_TEXT, CODES) == expected


def test_title_from_pdf_refuses_when_the_row_is_ambiguous_or_absent():
    page = "HOA-3 History of Architecture 3 3 HOA-2 BU-3/L Building Utilities 3 2/1"
    assert title_from_pdf("HOA-3", "3", "x", page, ["HOA-3", "BU-3/L"]) is None      # the units digit repeats in the title
    assert title_from_pdf("NOPE 1", "3", "x", page, ["HOA-3"]) is None               # code not printed
    twice = "CS 1 Alpha Beta 3 CS 2 Gamma 3 CS 1 Delta Epsilon 3"
    assert title_from_pdf("CS 1", "3", "x", twice, ["CS 1", "CS 2"]) is None         # two rows start with the code
    mention = "CS 2 Gamma 3 CS 1, CS 9 Other 3"
    assert title_from_pdf("CS 1", "3", "x", mention, ["CS 1", "CS 2", "CS 9"]) is None  # a prerequisite mention is not a row


def test_the_verifier_numbers_the_proposals_of_each_row():
    payload = fx.bscs()
    payload["courses"][0]["course_title"] = "FIRST SEMESTER Discrete Structures 1"
    payload["courses"][1]["course_code"] = "FIRST YEAR CC 1/L"
    v = verify_candidate(payload)
    rows = by_code(payload, v)
    assert [(l, f.kind, f.new) for l, f in rows["CS 1"].fixes] == [("a", "strip_banner", "Discrete Structures 1")]
    assert [(l, f.field, f.new) for l, f in rows["FIRST YEAR CC 1/L"].fixes] == [("a", "course_code", "CC 1/L")]
    assert rows["CS 2"].fixes == []
```

- [ ] **Step 2: Run them to see them fail**

```powershell
uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_fixes.py
```

Expected: collection error, `ModuleNotFoundError: No module named 'backend.bintanong_tools.prospectus_extractor.fixes'`.

- [ ] **Step 3: Implement the proposals**

`backend/bintanong_tools/prospectus_extractor/fixes.py`:

```python
"""Fix proposals for one flagged course. A proposal is only a proposal: a human accepts it.

Three kinds, each derived from text the document already holds, never from a guess:
  strip_banner    a banner phrase at the start or end of the code or title is removed
  move_term       the course's own code/title cell starts with a banner that names another term
  title_from_pdf  the title is read from the PDF text layer when exactly one PDF row matches
Anything that would need invented text (a title, a prerequisite) gets no proposal.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .course_checks import pdf_clean
from .text import BANNER_PHRASE, clean_str, leading_banner, match_semester_labels, match_year_label, trailing_banner

FIELD_CODE, FIELD_TITLE, FIELD_TERM = "course_code", "course_title", "term"


@dataclass(frozen=True)
class Fix:
    kind: str       # strip_banner | move_term | title_from_pdf
    field: str      # course_code | course_title | term
    old: str
    new: str
    note: str
    fix_id: str     # stable across sheet regenerations: "<kind>:<field>@<first source cell id>"


def format_term(year: str | None, semester: str | None) -> str:
    return f"{year or '?'} / {semester or '?'}"


def parse_term(text: str, default_year: str | None = None) -> tuple[str, str] | None:
    """'2nd Year / 1st Semester' (or just '1st Semester') to (year, semester), else None."""
    value = clean_str(text)
    year = match_year_label(value) or default_year
    labels = {label for _position, label in match_semester_labels(value)}
    if not year or len(labels) != 1:
        return None
    return year, labels.pop()


def strip_banner(text: str) -> str | None:
    """`text` without banner phrases at its start or end, or None when nothing sensible remains:
    nothing to strip, nothing left, or banner text still inside it (a banner in the middle of a
    title cannot be removed without guessing where the course text starts)."""
    value = clean_str(text)
    _banner, rest = leading_banner(value)
    rest, _tail = trailing_banner(rest)
    rest = clean_str(rest)
    if not rest or rest == value or BANNER_PHRASE.search(rest):
        return None
    return rest


def _fix_id(kind: str, field: str, cell_ids: Sequence[str]) -> str:
    return f"{kind}:{field}@{cell_ids[0] if cell_ids else 'none'}"


def _strip_fixes(course: Mapping[str, Any], role_cells: Mapping[str, Sequence[Mapping[str, Any]]]) -> list[Fix]:
    out = []
    for field, role, name in ((FIELD_CODE, "code", "code"), (FIELD_TITLE, "title", "title")):
        value = clean_str(course.get(field))
        cells = [c["cell_id"] for c in role_cells.get(role, [])]
        stripped = strip_banner(value) if BANNER_PHRASE.search(value) else None
        if stripped:
            out.append(Fix("strip_banner", field, value, stripped, f"banner text removed from the {name}",
                           _fix_id("strip_banner", field, cells)))
    return out


def _move_fix(course: Mapping[str, Any], role_cells: Mapping[str, Sequence[Mapping[str, Any]]]) -> list[Fix]:
    """A leading banner in the course's own code/title cell names the term the course sits in. Only
    a leading banner counts: a trailing one names the next section. Both semesters named, or an
    unreadable label, means flag-only."""
    year, semester = course.get("year_level"), course.get("semester")
    for role in ("code", "title"):
        for cell in role_cells.get(role, []):
            banner, rest = leading_banner(cell.get("text") or "")
            sems = {label for _p, label in match_semester_labels(banner)}
            if not banner or not rest or len(sems) != 1:
                continue
            target = (match_year_label(banner) or year, next(iter(sems)))
            if None in target or target == (year, semester):
                continue
            return [Fix("move_term", FIELD_TERM, format_term(year, semester), format_term(*target),
                        f'cell {cell["cell_id"]} starts with "{banner}"', _fix_id("move_term", FIELD_TERM, [cell["cell_id"]]))]
    return []


def title_from_pdf(code: str, units_raw: str, current: str, page_text: str, other_codes: Sequence[str]) -> str | None:
    """The title printed between `code` and the printed units, when the PDF text holds exactly one
    row that fits: `code`, words, then the units as a whole token, before the next known code.
    Several fits (a title that repeats the units digit) or none: None."""
    text = pdf_clean(page_text)
    units = clean_str(units_raw)
    if not code or not units:
        return None
    cuts = sorted({clean_str(c) for c in other_codes if clean_str(c) and clean_str(c) != code}, key=len, reverse=True)
    cut = re.compile(r"(?<!\S)(?:" + "|".join(re.escape(c) for c in cuts) + r")(?=\s|$)") if cuts else None
    found: list[str] = []
    for m in re.finditer(rf"(?<!\S){re.escape(code)}(?=\s)", text):
        window = text[m.end():].lstrip()
        stop = cut.search(window) if cut else None
        window = window[: stop.start()] if stop else window
        fits = [window[: u.start()].strip() for u in re.finditer(rf"(?<=\s){re.escape(units)}(?=\s|$)", window)]
        fits = [t for t in fits if len(re.findall(r"[A-Za-z]", t)) >= 2 and not BANNER_PHRASE.search(t)]
        if len(fits) > 1:
            return None
        found += fits
    if len(found) != 1 or found[0] == clean_str(current):
        return None
    return found[0]


def propose_fixes(
    course: Mapping[str, Any],
    role_cells: Mapping[str, Sequence[Mapping[str, Any]]],
    *,
    title_not_in_pdf: bool = False,
    page_text: str | None = None,
    known_codes: Sequence[str] = (),
) -> list[Fix]:
    fixes = _strip_fixes(course, role_cells) + _move_fix(course, role_cells)
    if title_not_in_pdf and page_text and not any(f.field == FIELD_TITLE for f in fixes):
        new = title_from_pdf(clean_str(course.get("course_code")), (course.get("units") or {}).get("raw") or "",
                             course.get("course_title") or "", page_text, known_codes)
        if new:
            cells = [c["cell_id"] for c in role_cells.get("title", [])]
            fixes.append(Fix("title_from_pdf", FIELD_TITLE, clean_str(course.get("course_title")), new,
                             "title read from the PDF text layer (one matching row)", _fix_id("title_from_pdf", FIELD_TITLE, cells)))
    return fixes
```

```powershell
uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_fixes.py
```

Expected: `1 failed, 19 passed`. The failure is `test_the_verifier_numbers_the_proposals_of_each_row` (the verifier does not call `propose_fixes` yet).

- [ ] **Step 4: Number the proposals in the verifier**

In `backend/bintanong_tools/prospectus_extractor/verify.py` apply these four replacements (each text occurs once).

**Edit 1.** Replace

```python
from .prerequisites import is_standing_rule
```

with

```python
from .fixes import propose_fixes
from .prerequisites import is_standing_rule
```

**Edit 2.** Replace

```python
def _course_flags(index, course, ctx) -> list[Flag]:
```

with

```python
def _course_flags(index, course, ctx) -> tuple[list[Flag], list]:
```

**Edit 3.** Replace

```python
    return flags


def _health(
```

with

```python
    fixes = propose_fixes(course, roles, known_codes=ctx["codes"])
    return flags, fixes


def _health(
```

**Edit 4.** Replace

```python
        row.flags = _course_flags(index, course, ctx)
```

with

```python
        row.flags, fixes = _course_flags(index, course, ctx)
        row.fixes = [(chr(ord("a") + i), fix) for i, fix in enumerate(fixes)]
```

- [ ] **Step 5: Run the tests and the suite**

```powershell
uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_fixes.py tests/test_prospectus_verify.py
uv run --project backend --extra tools --extra dev --with fastapi==0.141.1 python -m pytest -q tests
```

Expected: `37 passed`; full suite `132 passed`, 13 subtests passed.

- [ ] **Step 6: Progress note and commit**

Add a row: `4. Fix proposals | done | <hash> | red: ModuleNotFoundError fixes; 1 failed 19 passed before the verifier edit; green 20; full suite 132`.

```powershell
git add tests/test_prospectus_fixes.py backend/bintanong_tools/prospectus_extractor/fixes.py backend/bintanong_tools/prospectus_extractor/verify.py plans/plan_current_progress/extractor_split_progress.md
git commit -m "feat: propose banner strips, term moves and PDF-read titles for flagged courses" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: PDF text checks, unclaimed printed codes, and placing them in a section (tests first)

**Why:** check 3 (a code or title not found in the PDF text; "not checked" when only cached Docling JSON is at hand) and check 6 (printed codes no course claimed, attached to the section whose page region they sit in when that can be determined, else listed as unplaced). The audit's checks are reused, not rewritten.

**Files:**
- Create: `tests/test_prospectus_verify_pdf.py`
- Create: `backend/bintanong_tools/prospectus_extractor/placement.py`
- Modify: `backend/bintanong_tools/prospectus_extractor/verify.py` (edits below)

- [ ] **Step 1: Write the failing tests**

`tests/test_prospectus_verify_pdf.py`:

```python
import copy

import pytest

from backend.bintanong_tools.prospectus_extractor.course_checks import PdfPage
from backend.bintanong_tools.prospectus_extractor.placement import locate_in_page
from backend.bintanong_tools.prospectus_extractor.verify import verify_candidate

import fixer_fixtures as fx
from fixer_fixtures import by_code, kinds, section


def test_unclaimed_codes_above_the_first_banner_stay_unplaced():
    payload = fx.innovation()
    v = verify_candidate(payload)
    unplaced = section(v, "SU")
    assert [r.item["code"] for r in unplaced.rows] == ["ENTRE 7", "GE-IER", "ENTRE 9"]  # ENTRE 9 sits 17 pt above FOURTH YEAR
    assert [r.rid for r in unplaced.rows] == ["SU-U1", "SU-U2", "SU-U3"] and unplaced.health == "broken"
    assert v.health == "broken"


def test_an_unclaimed_code_below_a_sections_last_row_is_attached_to_that_section():
    payload = fx.innovation()
    box = {"code": "ENTRE 99", "cell_ids": ["t0-c90"], "table_index": 0, "page": 1, "bbox": [71.2, 822.0, 98.3, 832.0]}
    right = {"code": "ENTRE 98", "cell_ids": ["t0-c91"], "table_index": 0, "page": 1, "bbox": [345.5, 822.0, 372.6, 832.0]}
    far = {"code": "ENTRE 97", "cell_ids": ["t0-c92"], "table_index": 0, "page": 1, "bbox": [71.2, 900.0, 98.3, 910.0]}
    payload["audit"]["unclaimed_course_candidates"] = [box, right, far]
    v = verify_candidate(payload)
    assert [r.item["code"] for r in section(v, "S2").rows if r.item] == ["ENTRE 99"]
    assert [r.item["code"] for r in section(v, "S3").rows if r.item] == ["ENTRE 98"]
    assert [r.item["code"] for r in section(v, "SU").rows] == ["ENTRE 97"]


def test_other_audit_anomalies_become_rows_too_but_covered_ones_do_not():
    payload = fx.innovation()
    payload["audit"]["unclaimed_course_candidates"] = []
    payload["audit"]["structural_anomalies"] = [
        {"type": "multiple_course_codes_in_cell", "table_index": 0, "page": 1, "candidate_codes": ["GE-PH", "GE-STS"],
         "reason": "one source cell contains two codes", "source_cell_ids": ["t0-c70"],
         "source_cells": [{"cell_id": "t0-c70", "bbox": [71.2, 822.0, 98.3, 832.0]}]},
        {"type": "unclaimed_course_candidate", "source_cell_ids": ["t0-c0"]},
        {"type": "course_without_verified_semester", "source_cell_ids": ["t0-c1"]},
    ]
    v = verify_candidate(payload)
    rows = [r for s in v.sections for r in s.rows if r.item]
    assert [(r.item["code"], kinds(r)) for r in rows] == [("GE-PH, GE-STS", ["audit_anomaly"])]
    assert rows[0].rid.startswith("S2-U")


# --- PDF text layer (check 3) and silent printed codes

def test_title_and_code_not_in_the_pdf_text_are_warnings_and_only_with_the_pdf():
    payload = fx.architecture()
    assert not any(kinds(r) for s in verify_candidate(payload).sections for r in s.rows)
    v = verify_candidate(payload, {1: PdfPage(fx.ARCH_PAGE_TEXT)})
    rows = by_code(payload, v)
    assert v.pdf_checked is True
    assert kinds(rows["TOA-1/L"]) == ["title_not_in_pdf"] and kinds(rows["GE-PC"]) == ["title_not_in_pdf"]
    assert kinds(rows["AD-1/L"]) == [] and kinds(rows["VT-1/L"]) == []   # stored title is the start of the printed one
    assert kinds(rows["TOA-2"]) == ["title_not_in_pdf"] and kinds(rows["VT-2/L"]) == ["title_not_in_pdf"] and kinds(rows["AD-2/L"]) == []
    assert section(v, "S1").health == "review" and section(v, "S2").health == "review"


def test_a_printed_code_nobody_claims_is_found_in_the_pdf_and_placed_by_its_box():
    payload = fx.innovation()
    payload["audit"]["unclaimed_course_candidates"] = []
    payload["audit"]["errors"] = []
    text = "ENTRE 14 Business Implementation 1 5 ENTRE 10 ZZ-999 Ghost 3"
    chars = [(ch, 71.2 + 4 * i, 936.0 - 830.0, 75.2 + 4 * i, 936.0 - 822.0) for i, ch in enumerate("ZZ-999")]  # y up
    v = verify_candidate(payload, {1: PdfPage(text, chars, 936.0)})
    items = [r for s in v.sections for r in s.rows if r.item]
    assert [(r.item["source"], r.item["code"]) for r in items] == [("pdf", "ZZ-999")]
    assert items[0].item["bbox"] == pytest.approx([71.2, 822.0, 95.2, 830.0])
    assert items[0].rid.startswith("S1-U")  # no empty 1st-year section here: S1 is 4th Year 1st Semester


def test_locate_in_page_refuses_a_code_that_occurs_twice():
    boxes = lambda s, x0: [(ch, x0 + 5 * i, 10.0, x0 + 5 * i + 4, 20.0) for i, ch in enumerate(s)]
    page = PdfPage("CS 1 .. CS 10", boxes("CS1", 0) + boxes("CS10", 100), 100.0)
    assert locate_in_page(page, "CS 1") is None            # "cs1" is also inside "cs10"
    assert locate_in_page(page, "CS 10") == pytest.approx([100, 80, 119, 90])
    assert locate_in_page(PdfPage("x"), "CS 1") is None


def test_proposals_that_need_the_pdf_appear_only_with_it_and_only_on_flagged_rows():
    payload = fx.architecture()
    v = verify_candidate(payload, {1: PdfPage(fx.ARCH_PAGE_TEXT)})
    rows = by_code(payload, v)
    assert [(l, f.kind, f.new) for l, f in rows["GE-PC"].fixes] == [("a", "title_from_pdf", "Purposive Communication")]
    assert [(l, f.new) for l, f in rows["TOA-1/L"].fixes] == [("a", "Theory of Architecture1")]
    assert [f.new for _l, f in rows["VT-2/L"].fixes] == ["Architectural Visual Communications 4-Visual Techniques 2"]
    assert [f.new for _l, f in rows["TOA-2"].fixes] == ["Theory of Architecture 2"]
    assert rows["AD-1/L"].fixes == [] and rows["VT-1/L"].fixes == [] and rows["AD-2/L"].fixes == []
    assert not any(r.fixes for s in verify_candidate(payload).sections for r in s.rows)   # without the PDF: none


def test_health_is_broken_when_printed_codes_outnumber_a_quarter_of_the_courses():
    assert verify_candidate(fx.innovation()).health == "broken"      # 3 unclaimed codes, 2 courses
    payload = fx.bscs()
    payload["audit"]["unclaimed_course_candidates"] = [
        {"code": f"ZZ {n}", "cell_ids": [f"t0-c9{n}"], "table_index": 0, "page": 1, "bbox": None} for n in range(1, 4)]
    assert verify_candidate(payload).health == "broken"              # 3 of 4 courses
    payload["courses"] = [copy.deepcopy(c) for c in payload["courses"] for _ in range(4)]
    payload["audit"]["term_unit_audit"] = []                          # no printed totals to disagree with
    for index, course in enumerate(payload["courses"]):              # sixteen courses: three codes are under a quarter
        course["provenance"]["source_cell_ids"] = [f"t{index}-c1"]
        course["course_code"] = f"CS {index}"
    assert verify_candidate(payload).health == "mixed"
```

- [ ] **Step 2: Run them to see them fail**

```powershell
uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_verify_pdf.py
```

Expected: collection error, `ModuleNotFoundError: No module named 'backend.bintanong_tools.prospectus_extractor.placement'`.

- [ ] **Step 3: Create the placement module**

`backend/bintanong_tools/prospectus_extractor/placement.py`:

```python
"""Printed codes no course claimed, and which year/semester section they sit in.

Items come from the audit's unclaimed list and anomalies (geometry in the candidate JSON) and, when
the PDF text layer is at hand, from printed code-like strings no course accounts for (geometry from
the PDF character boxes). Placement is conservative: an item is attached to a section only when its
box is inside that section's region (or just under its last row) and exactly one section fits;
anything else stays unplaced for the reviewer.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from .course_checks import DASHES as _PDF_DASHES  # not re-exported as DASHES: text.DASHES is a different set
from .course_checks import PdfPage, check_pdf_missed, loose
from .text import clean_str

BELOW_TOLERANCE = 30.0  # points under a section's last row where a missed course may still sit
# Anomalies already reported by another flag: the audit's own unclaimed list, and courses with no term.
COVERED_ANOMALIES = {"unclaimed_course_candidate", "course_without_verified_semester"}


def locate_in_page(page: PdfPage, code: str) -> list[float] | None:
    """[left, top, right, bottom] (top-left frame) of `code` in the PDF characters, only when the
    page holds exactly one such string; several (CS 1 inside CS 10) cannot be placed safely."""
    if not page.chars or not page.height:
        return None
    kept = [i for i, c in enumerate(page.chars) if c[0] and not c[0].isspace() and c[0] not in _PDF_DASHES]
    flat = "".join(page.chars[i][0].casefold() for i in kept)
    key = loose(code).casefold()
    if not key or flat.count(key) != 1:
        return None
    at = flat.index(key)
    boxes = [page.chars[kept[j]] for j in range(at, at + len(key))]
    return [min(b[1] for b in boxes), page.height - max(b[4] for b in boxes),
            max(b[3] for b in boxes), page.height - min(b[2] for b in boxes)]


def attach(item: Mapping[str, Any], regions: Mapping[str, Mapping[int, Sequence[float]]]) -> str | None:
    """The one section whose region holds the item, else None. Inside a region wins outright;
    otherwise a section whose last row ends within BELOW_TOLERANCE above the item; a tie is None.
    regions: section id -> page -> [left, top, right, bottom] in the table-cell (top-left) frame."""
    bbox, page = item.get("bbox"), item.get("page")
    if not bbox or page is None:
        return None
    left, top, right, bottom = bbox
    inside, below = [], []
    for sid, pages in regions.items():
        box = pages.get(page)
        if not box or min(right, box[2]) - max(left, box[0]) <= 0:
            continue
        middle = (top + bottom) / 2
        if box[1] <= middle <= box[3]:
            inside.append(sid)
        elif box[3] < middle <= box[3] + BELOW_TOLERANCE:
            below.append(sid)
    pool = inside or below
    return pool[0] if len(pool) == 1 else None


def unclaimed_items(audit: Mapping[str, Any], courses: Sequence[Mapping[str, Any]], pages: Mapping[int, PdfPage] | None) -> list[dict]:
    """Printed codes and anomalies no course accounts for: {source, code, page, bbox, cell_ids, table_index, snippet}."""
    items = [
        {"source": "audit", "code": u.get("code") or "", "page": u.get("page"), "bbox": u.get("bbox"),
         "cell_ids": list(u.get("cell_ids") or []), "table_index": u.get("table_index"), "snippet": ""}
        for u in audit.get("unclaimed_course_candidates") or []
    ]
    for anomaly in audit.get("structural_anomalies") or []:
        if anomaly.get("type") in COVERED_ANOMALIES:
            continue
        boxes = [c["bbox"] for c in anomaly.get("source_cells") or [] if c.get("bbox")]
        items.append({
            "source": "anomaly", "type": anomaly.get("type"), "page": anomaly.get("page"),
            "code": ", ".join(anomaly.get("candidate_codes") or []) or str(anomaly.get("type")),
            "bbox": [min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes)] if boxes else None,
            "cell_ids": list(anomaly.get("source_cell_ids") or []), "table_index": anomaly.get("table_index"),
            "snippet": clean_str(anomaly.get("reason")),
        })
    for page_no, page in sorted((pages or {}).items()):
        for row in check_pdf_missed(courses, audit, page.text, None, page_no):
            if row["status"] == "silent":  # the audit's own list is already above
                items.append({"source": "pdf", "code": row["json"], "page": page_no,
                              "bbox": locate_in_page(page, row["json"]), "cell_ids": [], "table_index": None,
                              "snippet": row["pdf"]})
    return items
```

```powershell
uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_verify_pdf.py
```

Expected: `7 failed, 1 passed`. The one pass is the placement test `test_locate_in_page_refuses_a_code_that_occurs_twice`; the other seven fail on the verifier (`TypeError: verify_candidate() takes 1 positional argument but 2 were given`, or no unclaimed rows).

- [ ] **Step 4: Wire PDF text and unclaimed codes into the verifier**

In `backend/bintanong_tools/prospectus_extractor/verify.py` apply these replacements in order (each text occurs once). After them the file is the final verifier.

**Edit 1.** Replace

```python
from .fixes import propose_fixes
```

with

```python
from .course_checks import PdfPage, check_course_pdf
from .fixes import propose_fixes
from .placement import attach, unclaimed_items
```

**Edit 2.** Replace

```python
def _course_flags(index, course, ctx)
```

with

```python
def _regions(sections: Sequence[Section], courses: Sequence[Mapping[str, Any]], layout, evidence_ids) -> dict:
    """sid -> page -> [left, top, right, bottom]. Horizontal extent from the course's own cells
    (so the two semesters of one year do not overlap); the top includes the section banner."""
    out: dict[str, dict[int, list[float]]] = {}
    for section in sections:
        for row in section.rows:
            if row.course is None:
                continue
            course = courses[row.course]
            own = [c for cells in own_role_cells(course, layout, evidence_ids).values() for c in cells if c.get("bbox")]
            allb = [c["bbox"] for c in (course.get("provenance") or {}).get("source_cells") or [] if c.get("bbox")]
            page = (course.get("provenance") or {}).get("page")
            if not own or page is None:
                continue
            left, right = min(c["bbox"][0] for c in own), max(c["bbox"][2] for c in own)
            top, bottom = min(b[1] for b in allb), max(b[3] for b in allb)
            box = out.setdefault(section.sid, {}).setdefault(page, [left, top, right, bottom])
            box[:] = [min(box[0], left), min(box[1], top), max(box[2], right), max(box[3], bottom)]
    return out


def _course_flags(index, course, ctx)
```

**Edit 3.** Replace

```python
    fixes = propose_fixes(course, roles, known_codes=ctx["codes"])
```

with

```python
    page = ctx["pages"].get((course.get("provenance") or {}).get("page")) if ctx["pages"] else None
    title_missing = False
    if page is not None:
        got = {r["check"]: r["status"] for r in check_course_pdf(course, page.text, page.chars, page.height, ctx["layout"])}
        if got.get("B_code") == "fail":
            flags.append(Flag("code_not_in_pdf", WARN, "code not found in the PDF text", "course_code"))
        if got.get("B_title") == "fail":
            title_missing = True
            flags.append(Flag("title_not_in_pdf", WARN, "title not found in the PDF text", "course_title"))
    fixes = propose_fixes(course, roles, title_not_in_pdf=title_missing, page_text=page.text if page else None,
                          known_codes=ctx["codes"])
```

**Edit 4.** Replace

```python
    """clean | warnings_only | mixed | broken. Broken: most sections broken, or fewer than two term sections."""
```

with

```python
    """clean | warnings_only | mixed | broken. Broken: most sections broken, fewer than two term
    sections, or printed codes no course claimed numbering a quarter of the courses (three at least)."""
```

**Edit 5.** Replace

```python
def _overall(sections: Sequence[Section]) -> str:
```

with

```python
def _overall(sections: Sequence[Section], course_count: int) -> str:
```

**Edit 6.** Replace

```python
    broken = sum(s.health == "broken" for s in sections)
```

with

```python
    broken = sum(s.health == "broken" for s in sections)
    unclaimed = sum(r.item is not None for s in sections for r in s.rows)
```

**Edit 7.** Replace

```python
    if len(terms) < 2 or broken * 2 > len(sections):
```

with

```python
    if len(terms) < 2 or broken * 2 > len(sections) or (unclaimed >= 3 and unclaimed * 4 >= course_count):
```

**Edit 8.** Replace

```python
def verify_candidate(payload: Mapping[str, Any]) -> Verification:
```

with

```python
def verify_candidate(payload: Mapping[str, Any], pdf_pages: Mapping[int, PdfPage] | None = None) -> Verification:
```

**Edit 9.** Replace

```python
"courses": courses, "layout": layout, "evidence_ids": evidence_ids,
```

with

```python
"courses": courses, "layout": layout, "evidence_ids": evidence_ids, "pages": pdf_pages or {},
```

**Edit 10.** Replace

```python
    sections += [s for s in (loose_section,) if s.rows]
```

with

```python
    regions = _regions(sections, courses, layout, evidence_ids)
    unplaced = Section(UNPLACED, None, None)
    by_sid = {s.sid: s for s in sections}
    for item in unclaimed_items(audit, courses, pdf_pages):
        section = by_sid.get(attach(item, regions)) or unplaced
        row = Row(f"{section.sid}-U{sum(r.item is not None for r in section.rows) + 1}", item=item)
        if item["source"] == "anomaly":
            row.flags.append(Flag("audit_anomaly", ERROR, f'{item["type"]}: {item["snippet"]} (page {item["page"]})'))
        else:
            row.flags.append(Flag("unclaimed_code", ERROR, f'printed code "{item["code"]}" was not claimed by any course ({item["source"]}, page {item["page"]})'))
        section.rows.append(row)
    sections += [s for s in (loose_section, unplaced) if s.rows]
```

**Edit 11.** Replace

```python
    return Verification(sections, False, _overall(sections))
```

with

```python
    return Verification(sections, bool(pdf_pages), _overall(sections, len(courses)))
```

- [ ] **Step 5: Run the tests and the suite**

```powershell
uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_verify_pdf.py tests/test_prospectus_verify.py tests/test_prospectus_fixes.py
uv run --project backend --extra tools --extra dev --with fastapi==0.141.1 python -m pytest -q tests
```

Expected: `45 passed`; full suite `140 passed`, 13 subtests passed.

- [ ] **Step 6: Real-data check against the course audit's numbers**

Save as `$env:TEMP\b2_smoke.py` and run from the repo root:

```python
"""Real-data smoke for the verifier: health and error/warn flag counts per run folder.

    python b2_smoke.py [--pdf] [NN ...]      from the repo root; --pdf also reads each PDF text layer
    python b2_smoke.py --proposals           fix proposals over the 39 distinct PDFs
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, ".")
from backend.bintanong_tools.prospectus_extractor.course_checks import load_pdf_pages, manifest_index, resolve_pdf  # noqa: E402
from backend.bintanong_tools.prospectus_extractor.verify import verify_candidate  # noqa: E402

D = Path(r"E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump")
RUNS = D / r"scratch\compare_2026-10-03b\new"
INDEX = manifest_index(D / r"docling_jsonified_output\task2b_standing_isolated_2026-09-29")
PDFS = D / "PalSU Undergraduate Prospectus Website Dump"
use_pdf = "--pdf" in sys.argv or "--proposals" in sys.argv
only = [a for a in sys.argv[1:] if a.isdigit()]
seen, kinds, flagged, with_fix = set(), Counter(), 0, 0
for n in sorted(p.name for p in RUNS.iterdir() if p.is_dir()):
    if only and n not in only:
        continue
    payload = json.loads((RUNS / n / "candidate.json").read_text(encoding="utf-8"))
    pages = None
    if use_pdf:
        record = INDEX[re.sub(r"[()]", "_", (RUNS / n / "source.txt").read_text(encoding="utf-8").strip())]
        if "--proposals" in sys.argv and record["pdf_sha256"] in seen:
            continue
        seen.add(record["pdf_sha256"])
        path, _ok = resolve_pdf(record, PDFS)
        pages = load_pdf_pages(path)
    v = verify_candidate(payload, pages)
    if "--proposals" in sys.argv:
        for s in v.sections:
            for r in s.rows:
                if r.course is None:
                    continue
                if any(f.kind == "title_not_in_pdf" for f in r.flags):
                    flagged += 1
                    with_fix += bool(r.fixes)
                for _letter, fix in r.fixes:
                    kinds[fix.kind] += 1
    else:
        print(n, v.health, v.counts())
if "--proposals" in sys.argv:
    print(dict(kinds), "title_not_in_pdf rows", flagged, "with a proposal", with_fix)
```

```powershell
uv run --project backend --extra tools --extra dev python "$env:TEMP\b2_smoke.py" 01 16 24 33 13
uv run --project backend --extra tools --extra dev python "$env:TEMP\b2_smoke.py" --pdf 01 16 24 33 13
uv run --project backend --extra tools --extra dev python "$env:TEMP\b2_smoke.py" --proposals
```

Expected (JSON only, then with the PDF text layer, then proposals over the 39 distinct PDFs):

```
01 mixed {'prereq_order': 1, 'unit_total': 1}
13 broken {'unclaimed_code': 15}
16 clean {}
24 broken {'audit_anomaly': 2, 'unclaimed_code': 1, 'unit_total': 1}
33 mixed {'audit_anomaly': 1}

01 mixed {'prereq_order': 1, 'title_not_in_pdf': 19, 'unit_total': 1}
13 broken {'unclaimed_code': 76}
16 warnings_only {'title_not_in_pdf': 1}
24 broken {'audit_anomaly': 2, 'code_not_in_pdf': 2, 'title_not_in_pdf': 4, 'unclaimed_code': 17, 'unit_total': 1}
33 mixed {'audit_anomaly': 1, 'unclaimed_code': 6}

{'title_from_pdf': 62} title_not_in_pdf rows 114 with a proposal 62
```

These agree with the course audit of 3 October (`course_audit_2026-10-03b`): Architecture 19 titles not in the PDF, BSBA-HRM 1, Midwifery 4 titles and 2 codes, BSE-Innovation 61 silent plus 15 listed printed codes. If a number differs, stop and find out which side moved.

- [ ] **Step 7: Progress note and commit**

Add a row: `5. PDF checks, unclaimed codes, placement | done | <hash> | red: ModuleNotFoundError placement; green 8 (45 verifier+fix tests); real data matches the 3 Oct course audit; 62 of 114 titles get a proposal; full suite 140`.

```powershell
git add tests/test_prospectus_verify_pdf.py backend/bintanong_tools/prospectus_extractor/placement.py backend/bintanong_tools/prospectus_extractor/verify.py plans/plan_current_progress/extractor_split_progress.md
git commit -m "feat: check titles and codes against the PDF text and place unclaimed printed codes in sections" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6: The decision ledger (tests first)

**Why:** H1. Human decisions go in an append-only file, never into the candidate. Each entry holds reviewer, time, reason, `pdf_sha256`, the course locator (its source cell ids), the field, the old value, the new value or a disposition, and the fix proposal it came from. Conforms to master plan §7.1 step 7 and approved draft Task 5. The state function Phase C reads lives here.

**Files:**
- Create: `tests/test_prospectus_ledger.py`
- Create: `backend/bintanong_tools/prospectus_extractor/ledger.py` (first version; Task 7 extends it)

- [ ] **Step 1: Write the failing tests**

`tests/test_prospectus_ledger.py`:

```python
import json
from datetime import datetime, timezone

import pytest

from backend.bintanong_tools.prospectus_extractor.ledger import (
    LedgerError, append_entries, content_review_state, course_locator, course_snapshot, latest_by_field,
    make_entry, read_entries, split_applicable, unclaimed_locator,
)

import fixer_fixtures as fx

HASH = "a" * 64
OTHER = "b" * 64
NOW = datetime(2026, 10, 4, 9, 30, tzinfo=timezone.utc)


def entry(course, field="row", disposition="accepted", old=None, new=None, pdf=HASH, reason="r", **extra):
    snapshot = course_snapshot(course)
    return make_entry(
        reviewer="Nestor", reason=reason, pdf_sha256=pdf, locator=course_locator(course), field=field,
        disposition=disposition, old_value=snapshot if old is None and field == "row" else old,
        new_value=snapshot if new is None and field == "row" else new, section="1st Year - 1st Semester",
        now=NOW, **extra)


def corrected_title(course, new, pdf=HASH):
    return entry(course, "course_title", "corrected", course["course_title"], new, pdf=pdf, fix_id="title_from_pdf:course_title@x")


def test_an_entry_carries_every_field_the_master_plan_names():
    course = fx.bscs()["courses"][0]
    e = corrected_title(course, "Discrete Structures 1")
    assert {"reviewer", "recorded_at", "reason", "pdf_sha256", "locator", "field", "old_value", "new_value",
            "disposition", "fix_id", "section", "entry_id", "ledger_version"} <= set(e)
    assert e["recorded_at"] == "2026-10-04T09:30:00Z"
    assert e["locator"] == {"kind": "course", "table_index": 0, "page": 1, "code_at_review": "CS 1",
                            "cell_ids": ["t0-c11", "t0-c12", "t0-c8", "t0-c9"]}
    assert e == corrected_title(course, "Discrete Structures 1")        # same content, same id
    assert e["entry_id"] != corrected_title(course, "Other")["entry_id"]


def test_an_entry_needs_a_reviewer_a_hash_and_a_known_disposition():
    course = fx.bscs()["courses"][0]
    bad = dict(reviewer="", reason="r", pdf_sha256=HASH, locator=course_locator(course), field="row", disposition="accepted",
               old_value=None, new_value=None, section="s")
    with pytest.raises(LedgerError):
        make_entry(**bad)
    with pytest.raises(LedgerError):
        make_entry(**{**bad, "reviewer": "N", "disposition": "approved"})
    with pytest.raises(LedgerError):
        make_entry(**{**bad, "reviewer": "N", "pdf_sha256": ""})


def test_the_ledger_is_append_only_and_applying_the_same_group_twice_writes_nothing(tmp_path):
    course = fx.bscs()["courses"][0]
    path = tmp_path / "review" / "decision_ledger.jsonl"
    group = [entry(course), corrected_title(course, "Discrete Structures 1")]
    assert append_entries(path, group) == (2, 0)
    before = path.read_bytes()
    assert append_entries(path, group) == (0, 2)
    assert path.read_bytes() == before
    assert b"\r\n" not in before and [json.loads(l)["field"] for l in before.decode().splitlines()] == ["row", "course_title"]
    later = [entry(course, "row", "unresolved", new=None, reason="cannot read the PDF")]
    assert append_entries(path, later) == (1, 0)
    assert path.read_bytes().startswith(before)                                  # old lines untouched
    assert len(read_entries(path)) == 3


def test_a_damaged_ledger_stops_the_append(tmp_path):
    path = tmp_path / "decision_ledger.jsonl"
    path.write_text('{"not": "an entry"}\n', encoding="utf-8")
    with pytest.raises(LedgerError, match="line 1"):
        append_entries(path, [entry(fx.bscs()["courses"][0])])
    path.write_text("{broken\n", encoding="utf-8")
    with pytest.raises(LedgerError, match="not JSON"):
        read_entries(path)


def test_entries_for_another_pdf_are_inapplicable():
    course = fx.bscs()["courses"][0]
    mine, theirs = corrected_title(course, "Mine"), corrected_title(course, "Theirs", pdf=OTHER)
    assert split_applicable([mine, theirs], HASH) == ([mine], [theirs])


def test_the_latest_decision_per_field_wins_and_a_row_entry_decides_all_fields():
    course = fx.bscs()["courses"][0]
    first, fix = entry(course), corrected_title(course, "New")
    revert = entry(course, reason="changed my mind")
    key = ("course", tuple(course_locator(course)["cell_ids"]))
    assert latest_by_field([first, fix])[(key, "course_title")] is fix
    assert latest_by_field([first, fix])[(key, "course_code")] is first
    assert latest_by_field([first, fix, revert])[(key, "course_title")] is revert


def decided_all(payload, disposition="accepted"):
    return [entry(c, "row", disposition, new=None if disposition == "unresolved" else None) for c in payload["courses"]]


def test_content_review_state_is_pending_partial_or_reviewed():
    payload = fx.bscs()
    assert content_review_state(payload, [], HASH) == {
        "state": "pending", "courses": 4, "decided": 0, "unresolved": 0, "unclaimed_undecided": 0, "inapplicable_entries": 0}
    some = decided_all(payload)[:3]
    assert content_review_state(payload, some, HASH)["state"] == "partially_reviewed"
    assert content_review_state(payload, some, HASH)["decided"] == 3
    assert content_review_state(payload, decided_all(payload), HASH)["state"] == "reviewed"
    unresolved = decided_all(payload)[:3] + [entry(payload["courses"][3], "row", "unresolved", new=None)]
    state = content_review_state(payload, unresolved, HASH)
    assert (state["state"], state["unresolved"]) == ("partially_reviewed", 1)
    assert content_review_state(payload, decided_all(payload), OTHER)["state"] == "pending"
    assert content_review_state(payload, decided_all(payload), OTHER)["inapplicable_entries"] == 4


def test_a_course_with_an_unresolved_field_is_not_decided_even_after_other_fields_were_accepted():
    payload = fx.bscs()
    course = payload["courses"][0]
    mixed = decided_all(payload) + [entry(course, "course_title", "unresolved", course["course_title"], None)]
    state = content_review_state(payload, mixed, HASH)
    assert (state["state"], state["decided"], state["unresolved"]) == ("partially_reviewed", 3, 1)


def test_listed_printed_codes_must_be_decided_before_the_review_counts_as_complete():
    payload = fx.innovation()
    rows = decided_all(payload)
    assert content_review_state(payload, rows, HASH)["unclaimed_undecided"] == 3
    assert content_review_state(payload, rows, HASH)["state"] == "partially_reviewed"
    for item in payload["audit"]["unclaimed_course_candidates"]:
        rows.append(make_entry(reviewer="N", reason="not a course", pdf_sha256=HASH, locator=unclaimed_locator(item),
                               field="unclaimed", disposition="accepted", old_value=item["code"], new_value=item["code"], section="s"))
    assert content_review_state(payload, rows, HASH)["state"] == "reviewed"
```

- [ ] **Step 2: Run them to see them fail**

```powershell
uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_ledger.py
```

Expected: collection error, `ModuleNotFoundError: No module named 'backend.bintanong_tools.prospectus_extractor.ledger'`.

- [ ] **Step 3: Implement the ledger**

`backend/bintanong_tools/prospectus_extractor/ledger.py`:

```python
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
```

- [ ] **Step 4: Run the tests and the suite**

```powershell
uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_ledger.py
uv run --project backend --extra tools --extra dev --with fastapi==0.141.1 python -m pytest -q tests
```

Expected: `9 passed`; full suite `149 passed`, 13 subtests passed.

- [ ] **Step 5: Progress note and commit**

Add a row: `6. Decision ledger | done | <hash> | red: ModuleNotFoundError ledger; green 9; full suite 149`.

```powershell
git add tests/test_prospectus_ledger.py backend/bintanong_tools/prospectus_extractor/ledger.py plans/plan_current_progress/extractor_split_progress.md
git commit -m "feat: append-only decision ledger with applicability by PDF hash and a content-review state" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 7: Materialise the corrected candidate (tests first)

**Why:** H1. The corrected candidate JSON is rebuilt deterministically from the immutable extraction plus the applicable entries. An entry for another PDF, another course, or against a value the extractor no longer produces is reported with a reason and never applied. Derived views are rebuilt with the extractor's own functions (`finalize_courses`, `build_curriculum_by_term`, ...); the audit, Prolog, RAG chunks and quality report are not re-derived and are listed as stale in `review.derived_sections_stale`. The verifier is re-run on the result so a bad move shows up as new flags.

**Files:**
- Create: `tests/test_prospectus_materialise.py`
- Modify: `backend/bintanong_tools/prospectus_extractor/ledger.py`

- [ ] **Step 1: Write the failing tests**

`tests/test_prospectus_materialise.py`:

```python
import copy
from datetime import datetime, timezone

from backend.bintanong_tools.prospectus_extractor.ledger import (
    CORRECTED, course_locator, course_snapshot, make_entry, materialise, write_corrected,
)

import fixer_fixtures as fx

HASH = "a" * 64
OTHER = "b" * 64
NOW = datetime(2026, 10, 4, 9, 30, tzinfo=timezone.utc)

def entry(course, field="row", disposition="accepted", old=None, new=None, pdf=HASH, reason="r", **extra):
    snapshot = course_snapshot(course)
    return make_entry(
        reviewer="Nestor", reason=reason, pdf_sha256=pdf, locator=course_locator(course), field=field,
        disposition=disposition, old_value=snapshot if old is None and field == "row" else old,
        new_value=snapshot if new is None and field == "row" else new, section="1st Year - 1st Semester",
        now=NOW, **extra)


def corrected_title(course, new, pdf=HASH):
    return entry(course, "course_title", "corrected", course["course_title"], new, pdf=pdf, fix_id="title_from_pdf:course_title@x")


def test_entries_for_another_pdf_are_reported_not_applied():
    payload = fx.bscs()
    course = payload["courses"][0]
    theirs = corrected_title(course, "Theirs", pdf=OTHER)
    corrected, report = materialise(payload, [theirs], HASH)
    assert corrected["courses"][0]["course_title"] == "Discrete Structures 1"
    assert report["skipped"] == [{"entry_id": theirs["entry_id"], "reason": "pdf_sha256_mismatch"}]
    assert corrected["review"]["content_review"]["inapplicable_entries"] == 1


def test_materialise_applies_corrections_rebuilds_views_and_leaves_the_input_alone():
    payload = fx.architecture()
    original = copy.deepcopy(payload)
    gepc, toa = payload["courses"][3], payload["courses"][1]
    move = payload["courses"][4]   # AD-2/L: 1st Year 2nd Semester
    entries = [
        entry(gepc), corrected_title(gepc, "Purposive Communication"),
        entry(toa), corrected_title(toa, "Theory of Architecture1"),
        entry(move), entry(move, "term", "corrected", "1st Year / 2nd Semester", "1st Year / 1st Semester"),
    ]
    corrected, report = materialise(payload, entries, HASH)
    assert payload == original                                          # never edited in place
    by_code = {c["course_code"]: c for c in corrected["courses"]}
    assert by_code["GE-PC"]["course_title"] == "Purposive Communication" and by_code["GE-PC"]["title"] == "Purposive Communication"
    assert by_code["AD-2/L"]["semester"] == "1st Semester" and by_code["AD-2/L"]["term_index"] == 11
    assert [c["course_code"] for c in corrected["curriculum_by_term"]["1st Year"]["1st Semester"]][-1] == "AD-2/L"
    assert corrected["review"]["applied_entry_ids"] == sorted(e["entry_id"] for e in entries if e["disposition"] == CORRECTED)
    assert report["applied"] == 3 and report["skipped"] == []
    assert set(corrected["review"]["derived_sections_stale"]) >= {"audit", "prolog", "rag"}
    assert corrected["review"]["verification_counts"] == {"prereq_order": 1, "unit_total": 2}  # the move is a bad one: the verifier says so
    assert corrected["review"]["content_review"]["state"] == "partially_reviewed"


def test_a_correction_is_skipped_when_the_value_it_was_made_against_has_changed_or_the_course_is_gone():
    payload = fx.architecture()
    toa = payload["courses"][1]
    stale = corrected_title(toa, "Theory of Architecture1")
    stale["old_value"] = "something the extractor no longer produces"
    gone = copy.deepcopy(toa)
    gone["provenance"]["source_cell_ids"] = ["t9-c1"]
    lost = corrected_title(gone, "Nowhere")
    corrected, report = materialise(payload, [entry(toa), stale, entry(gone), lost], HASH)
    assert {s["reason"] for s in report["skipped"]} == {"old_value_changed", "course_not_found"}
    assert corrected["courses"][1]["course_title"] == toa["course_title"]


def test_a_later_row_accept_reverts_an_earlier_correction():
    payload = fx.architecture()
    toa = payload["courses"][1]
    entries = [entry(toa), corrected_title(toa, "Theory of Architecture1"), entry(toa, reason="reverted")]
    corrected, report = materialise(payload, entries, HASH)
    assert report["applied"] == 0
    assert {c["course_code"]: c["course_title"] for c in corrected["courses"]}["TOA-1/L"] == toa["course_title"]


def test_the_corrected_candidate_is_byte_identical_for_the_same_inputs(tmp_path):
    payload = fx.architecture()
    toa = payload["courses"][1]
    entries = [entry(toa), corrected_title(toa, "Theory of Architecture1")]
    one, two = tmp_path / "one.json", tmp_path / "two.json"
    write_corrected(one, materialise(payload, entries, HASH)[0])
    write_corrected(two, materialise(copy.deepcopy(payload), list(entries), HASH)[0])
    assert one.read_bytes() == two.read_bytes() and b"\r\n" not in one.read_bytes()
```

- [ ] **Step 2: Run them to see them fail**

```powershell
uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_materialise.py
```

Expected: collection error, `ImportError: cannot import name 'materialise' from 'backend.bintanong_tools.prospectus_extractor.ledger'`.

- [ ] **Step 3: Extend the ledger**

In `ledger.py` apply these four replacements (each text occurs once), then append the block below to the end of the file (after `content_review_state`, two blank lines before it).

**Edit 1.** Replace

```python
import hashlib
```

with

```python
import copy
import hashlib
```

**Edit 2.** Replace

```python
from .fixes import FIELD_CODE, FIELD_TERM, FIELD_TITLE, format_term
```

with

```python
from .courses import finalize_courses
from .fixes import FIELD_CODE, FIELD_TERM, FIELD_TITLE, format_term, parse_term
from .text import term_index
from .verify import verify_candidate
from .views import build_curriculum_by_term, build_unlocks_map, make_prerequisite_edges
```

**Edit 3.** Replace

```python
LEDGER_VERSION = "prospectus-decision-ledger-v1"
```

with

```python
LEDGER_VERSION = "prospectus-decision-ledger-v1"
CORRECTED_VERSION = "prospectus-corrected-candidate-v1"
```

**Edit 4.** Replace

```python
COURSE_FIELDS = (FIELD_CODE, FIELD_TITLE, FIELD_TERM)
```

with

```python
COURSE_FIELDS = (FIELD_CODE, FIELD_TITLE, FIELD_TERM)
STALE_SECTIONS = ["audit", "elective_tracks", "prolog", "quality_report", "rag"]  # not rebuilt from corrections
```

Append to the end of `ledger.py`:

```python
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
    applicable, inapplicable = split_applicable(entries, pdf_sha256)
    skipped = [{"entry_id": e["entry_id"], "reason": "pdf_sha256_mismatch"} for e in inapplicable]
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
        "applied_entry_ids": sorted(applied), "skipped": sorted(skipped, key=lambda s: (s["reason"], s["entry_id"])),
        "duplicate_course_codes": [d["course_code"] for d in duplicates],
        "verification_counts": verify_candidate(corrected).counts(),
        "derived_sections_stale": STALE_SECTIONS,
        "note": "A corrected candidate is a review artifact. It is not an approved curriculum.",
    }
    return corrected, {"applied": len(applied), "skipped": skipped, "content_review": state}


def write_corrected(path: Path, corrected: Mapping[str, Any]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(corrected, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
```

- [ ] **Step 4: Run the tests and the suite**

```powershell
uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_materialise.py tests/test_prospectus_ledger.py
uv run --project backend --extra tools --extra dev --with fastapi==0.141.1 python -m pytest -q tests
```

Expected: `14 passed`; full suite `154 passed`, 13 subtests passed.

- [ ] **Step 5: Progress note and commit**

Add a row: `7. Materialise | done | <hash> | red: ImportError materialise; green 5 (14 with the ledger tests); full suite 154`.

```powershell
git add tests/test_prospectus_materialise.py backend/bintanong_tools/prospectus_extractor/ledger.py plans/plan_current_progress/extractor_split_progress.md
git commit -m "feat: materialise a corrected candidate from the immutable extraction and the applicable ledger entries" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 8: The review sheet: render, parse and check (tests first)

**Why:** H2. One Markdown file per prospectus: a header, then one block per year x semester section in printed order with a health line, printed and extracted units, a `confirm` field, an `accept` line, and a table with one row per course carrying its flags and numbered proposals. `apply` regenerates the expected sheet from the candidate and refuses a sheet whose fixed text differs, so a stale, cut-up or hand-edited sheet cannot write decisions.

**Files:**
- Create: `tests/sheet_helpers.py`, `tests/test_prospectus_sheet.py`
- Create: `backend/bintanong_tools/prospectus_extractor/sheet.py` (first version; Task 9 extends it)

- [ ] **Step 1: Write the helpers and the failing tests**

`tests/sheet_helpers.py` (edit a rendered sheet the way a reviewer would):

```python
"""Helpers that edit a rendered review sheet the way a reviewer would."""

from backend.bintanong_tools.prospectus_extractor.sheet import COLUMNS, esc, split_cells


def edit_row(text, rid, **cols):
    """Fill the editable columns of one row."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith(f"| {rid} |"):
            cells = split_cells(line)
            cells += [""] * (len(COLUMNS) - len(cells))
            for name, value in cols.items():
                cells[COLUMNS.index(name.replace("_", " "))] = value
            lines[i] = "| " + " | ".join(esc(c) for c in cells) + " |"
    return "\n".join(lines) + "\n"


def set_line(text, sid, key, value):
    lines, inside = text.splitlines(), False
    for i, line in enumerate(lines):
        if line.startswith("## "):
            inside = line.startswith(f"## {sid} ")
        elif inside and line.startswith(f"{key}:"):
            lines[i] = f"{key}: {value}"
    return "\n".join(lines) + "\n"
```

`tests/test_prospectus_sheet.py`:

```python
import re

import pytest

from backend.bintanong_tools.prospectus_extractor.course_checks import PdfPage
from backend.bintanong_tools.prospectus_extractor.sheet import (
    candidate_sha256, check_against, esc, parse_sheet, render_sheet, split_cells,
)
from backend.bintanong_tools.prospectus_extractor.verify import verify_candidate

import fixer_fixtures as fx
from sheet_helpers import edit_row, set_line

HASH = "a" * 64


def make(payload, pdf=False):
    v = verify_candidate(payload, {1: PdfPage(fx.ARCH_PAGE_TEXT)} if pdf else None)
    identity = {"pdf_sha256": HASH, "candidate_sha256": candidate_sha256(payload)}
    return v, render_sheet(payload, v, identity)


# --- escaping and layout

@pytest.mark.parametrize("value", ["plain", "a | b", "back\\slash", "ends with \\", "x\\|y", "two  spaces\nand a break"])
def test_a_cell_survives_escape_and_split(value):
    line = "| " + " | ".join([esc("id"), esc(value), esc("tail")]) + " |"
    assert split_cells(line) == ["id", " ".join(value.split()), "tail"]


def test_the_sheet_has_one_table_per_section_in_printed_order_and_a_health_line_each():
    payload = fx.architecture()
    v, text = make(payload, pdf=True)
    headings = re.findall(r"^## (S\w+) - (.*)$", text, re.M)
    assert headings[:2] == [("S1", "1st Year - 1st Semester"), ("S2", "1st Year - 2nd Semester")]
    assert re.findall(r"^health: (\w+)$", text, re.M)[:2] == ["review", "review"]
    assert text.count("| id | code | title | units | prereq | flags | proposal | decision | new code | new title | new term |") == len(v.sections)
    assert "units: printed 10, extracted 10" in text and "confirm: no" in text
    assert "- prospectus health:" in text and f"- pdf_sha256: {HASH}" in text and "- pdf_text_checked: yes" in text
    row = next(l for l in text.splitlines() if l.startswith("| S1-04 |"))
    assert "WARN title_not_in_pdf" in row and 'a) title_from_pdf course_title: "Techniques 1 Purposive Communication" -> "Purposive Communication"' in row


def test_a_sheet_made_without_the_pdf_says_the_text_was_not_checked():
    _v, text = make(fx.architecture())
    assert "- pdf_text_checked: no" in text and "the PDF text was NOT checked" in text


def test_a_pipe_in_a_title_does_not_break_the_row():
    payload = fx.bscs()
    payload["courses"][1]["course_title"] = "Intro | Computing \\ Basics"
    v, text = make(payload)
    parsed = parse_sheet(text)
    assert parsed.sections["S1"].rows["S1-02"]["title"] == "Intro | Computing \\ Basics"
    assert check_against(parsed, parse_sheet(text)) == []


# --- the editable parts and the fixed parts


def test_editing_the_decision_columns_is_allowed_and_editing_anything_else_is_refused():
    payload = fx.bscs()
    _v, text = make(payload)
    expected = parse_sheet(text)
    edited = edit_row(text, "S1-01", decision="ok")
    edited = set_line(edited, "S1", "confirm", "yes")
    assert check_against(parse_sheet(edited), expected) == []
    tampered = text.replace("Discrete Structures 1 |", "Discrete Structures 99 |", 1)
    problems = check_against(parse_sheet(tampered), expected)
    assert len(problems) == 1 and "S1-01: column 'title' was changed" in problems[0] and "new title" in problems[0]
    assert any("units line" in p or "units" in p for p in check_against(parse_sheet(text.replace("printed 6", "printed 7", 1)), expected))


def test_a_sheet_from_another_candidate_or_a_cut_up_sheet_is_refused():
    payload = fx.bscs()
    v, text = make(payload)
    other = fx.bscs()
    other["courses"][0]["course_title"] = "Changed"
    _v2, other_text = make(other)
    problems = check_against(parse_sheet(other_text), parse_sheet(text))
    assert any("candidate_sha256" in p and "regenerate" in p for p in problems)
    cut = "\n".join(l for l in text.splitlines() if not l.startswith("| S1-02 |"))
    assert "S1-02: row is missing" in check_against(parse_sheet(cut), parse_sheet(text))
    assert any("not a prospectus-review-sheet-v1" in e for e in parse_sheet("hello").errors)
```

- [ ] **Step 2: Run them to see them fail**

```powershell
uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_sheet.py
```

Expected: collection error, `ModuleNotFoundError: No module named 'backend.bintanong_tools.prospectus_extractor.sheet'`.

- [ ] **Step 3: Implement rendering, parsing and checking**

`backend/bintanong_tools/prospectus_extractor/sheet.py`:

```python
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
from typing import Any, Mapping, Sequence

from .fixes import Fix
from .verify import Row, Section, Verification

SHEET_VERSION = "prospectus-review-sheet-v1"
COLUMNS = ["id", "code", "title", "units", "prereq", "flags", "proposal", "decision", "new code", "new title", "new term"]
FIXED = COLUMNS[:7]


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
    fixed: dict[str, str] = field(default_factory=dict)      # health, units, flags
    edits: dict[str, str] = field(default_factory=dict)      # confirm, accept, reason
    rows: dict[str, dict[str, str]] = field(default_factory=dict)


@dataclass
class ParsedSheet:
    meta: dict[str, str] = field(default_factory=dict)
    sections: dict[str, ParsedSection] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


def parse_sheet(text: str) -> ParsedSheet:
    sheet, section = ParsedSheet(), None
    if f"<!-- {SHEET_VERSION} -->" not in text:
        sheet.errors.append(f"not a {SHEET_VERSION} file")
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if m := re.match(r"^## (S[0-9]+|SN|SU)\b", line):
            section = sheet.sections.setdefault(m.group(1), ParsedSection())
            if "title" not in section.fixed:
                section.fixed["title"] = line
        elif section is None:
            if m := re.match(r"^- (pdf_sha256|candidate_sha256|pdf_text_checked|prospectus health):\s*(.*)$", line):
                sheet.meta[m.group(1)] = m.group(2).strip()
        elif m := re.match(r"^(health|units|flags):\s*(.*)$", line):
            section.fixed[m.group(1)] = m.group(2).strip()
        elif m := re.match(r"^(confirm|accept|reason):\s*(.*)$", line):
            section.edits[m.group(1)] = m.group(2).strip()
        elif line.startswith("|") and not re.match(r"^\|[\s\-|:]+$", line):
            cells = split_cells(line)
            if cells and cells[0] == "id":
                continue
            if len(cells) < len(FIXED) or len(cells) > len(COLUMNS):
                sheet.errors.append(f"line {number}: expected {len(COLUMNS)} columns, found {len(cells)}")
                continue
            cells += [""] * (len(COLUMNS) - len(cells))
            section.rows[cells[0]] = dict(zip(COLUMNS, cells))
    return sheet


def check_against(parsed: ParsedSheet, expected: ParsedSheet) -> list[str]:
    """Differences in everything the reviewer must not edit."""
    errors = list(parsed.errors)
    for key in ("pdf_sha256", "candidate_sha256", "pdf_text_checked", "prospectus health"):
        if parsed.meta.get(key) != expected.meta.get(key):
            errors.append(f"header {key} is {parsed.meta.get(key)!r}, expected {expected.meta.get(key)!r}; "
                          "this sheet was made from a different candidate or PDF: regenerate it")
    for sid in expected.sections.keys() - parsed.sections.keys():
        errors.append(f"section {sid} is missing from the sheet")
    for sid in parsed.sections.keys() - expected.sections.keys():
        errors.append(f"section {sid} is not in the candidate")
    for sid, want in expected.sections.items():
        have = parsed.sections.get(sid)
        if have is None:
            continue
        for key, value in want.fixed.items():
            if have.fixed.get(key) != value:
                errors.append(f"{sid}: {key} line was changed ({have.fixed.get(key)!r}, expected {value!r})")
        for rid in want.rows.keys() - have.rows.keys():
            errors.append(f"{rid}: row is missing")
        for rid in have.rows.keys() - want.rows.keys():
            errors.append(f"{rid}: row is not in the candidate")
        for rid, row in want.rows.items():
            for column in FIXED:
                if rid in have.rows and have.rows[rid][column] != row[column]:
                    errors.append(f"{rid}: column {column!r} was changed ({have.rows[rid][column]!r}, expected {row[column]!r}); "
                                  "use the new code / new title / new term columns to correct a value")
    return errors
```

- [ ] **Step 4: Run the tests and the suite**

```powershell
uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_sheet.py
uv run --project backend --extra tools --extra dev --with fastapi==0.141.1 python -m pytest -q tests
```

Expected: `11 passed`; full suite `165 passed`, 13 subtests passed.

- [ ] **Step 5: Progress note and commit**

Add a row: `8. Review sheet render/parse/check | done | <hash> | red: ModuleNotFoundError sheet; green 11; full suite 165`.

```powershell
git add tests/sheet_helpers.py tests/test_prospectus_sheet.py backend/bintanong_tools/prospectus_extractor/sheet.py plans/plan_current_progress/extractor_split_progress.md
git commit -m "feat: render and parse the per-prospectus review sheet and refuse a sheet whose fixed text changed" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 9: From sheet decisions to ledger entries (tests first)

**Why:** H2 and H4. Nothing is written for a row left blank unless the section is confirmed; a whole class of proposal can be accepted in one line per section; every correction carries the proposal id it came from and a reason; a printed code can only be decided, never fabricated into a course (D8). The whole sheet is applied or none of it: any problem returns no entries.

**Files:**
- Create: `tests/test_prospectus_sheet_decisions.py`
- Modify: `backend/bintanong_tools/prospectus_extractor/sheet.py`

- [ ] **Step 1: Write the failing tests**

`tests/test_prospectus_sheet_decisions.py`:

```python
from datetime import datetime, timezone

import pytest

from backend.bintanong_tools.prospectus_extractor.course_checks import PdfPage
from backend.bintanong_tools.prospectus_extractor.sheet import (
    build_entries, candidate_sha256, parse_decision, parse_sheet, render_sheet,
)
from backend.bintanong_tools.prospectus_extractor.verify import verify_candidate

import fixer_fixtures as fx
from sheet_helpers import edit_row, set_line

HASH = "a" * 64
NOW = datetime(2026, 10, 4, 9, 30, tzinfo=timezone.utc)


def make(payload, pdf=False):
    v = verify_candidate(payload, {1: PdfPage(fx.ARCH_PAGE_TEXT)} if pdf else None)
    identity = {"pdf_sha256": HASH, "candidate_sha256": candidate_sha256(payload)}
    return v, render_sheet(payload, v, identity)


def entries_for(payload, text, v=None, pdf=False):
    v = v or verify_candidate(payload, {1: PdfPage(fx.ARCH_PAGE_TEXT)} if pdf else None)
    parsed = parse_sheet(text)
    assert parsed.errors == []
    return build_entries(parsed, payload, v, reviewer="Nestor", pdf_sha256=HASH, now=NOW)


# --- the decision cell

@pytest.mark.parametrize("cell,expected", [
    ("", (None, [], "", None)),
    ("ok", ("ok", [], "", None)),
    ("OK: looks right", ("ok", [], "looks right", None)),
    ("fix", ("fix", [], "", None)),
    ("fix a, c", ("fix", ["a", "c"], "", None)),
    ("fix a b: both fine", ("fix", ["a", "b"], "both fine", None)),
    ("edit: PDF shows X", ("edit", [], "PDF shows X", None)),
    ("unresolved: cannot read", ("unresolved", [], "cannot read", None)),
])
def test_parse_decision(cell, expected):
    assert parse_decision(cell) == expected


def test_parse_decision_rejects_nonsense():
    assert parse_decision("approve")[3] and parse_decision("ok a")[3] and parse_decision("fix ab")[3]


# --- decisions to ledger entries


def test_an_untouched_sheet_writes_nothing():
    payload = fx.architecture()
    _v, text = make(payload, pdf=True)
    assert entries_for(payload, text, pdf=True) == ([], [])


def test_ok_writes_one_row_entry_with_the_row_as_extracted():
    payload = fx.bscs()
    _v, text = make(payload)
    entries, errors = entries_for(payload, edit_row(text, "S1-02", decision="ok"))
    assert errors == [] and len(entries) == 1
    e = entries[0]
    assert (e["field"], e["disposition"], e["reviewer"], e["pdf_sha256"], e["via"]) == ("row", "accepted", "Nestor", HASH, "sheet")
    assert e["old_value"] == e["new_value"] == {"course_code": "CC 1/L", "course_title": "Introduction to Computing", "term": "1st Year / 1st Semester"}
    assert e["locator"]["cell_ids"] == ["t0-c17", "t0-c18", "t0-c19", "t0-c8", "t0-c9"]


def test_fix_accepts_all_proposals_and_fix_a_names_one():
    payload = fx.architecture()
    _v, text = make(payload, pdf=True)
    entries, errors = entries_for(payload, edit_row(text, "S1-04", decision="fix"), pdf=True)
    assert errors == []
    assert [(e["field"], e["disposition"]) for e in entries] == [("row", "accepted"), ("course_title", "corrected")]
    fix = entries[1]
    assert (fix["old_value"], fix["new_value"], fix["fix_id"]) == (
        "Techniques 1 Purposive Communication", "Purposive Communication", "title_from_pdf:course_title@t0-c35")
    assert fix["reason"] == "accepted proposal title_from_pdf"
    one, errors = entries_for(payload, edit_row(text, "S1-04", decision="fix a: checked against the PDF"), pdf=True)
    assert errors == [] and one[1]["reason"] == "checked against the PDF"
    _none, errors = entries_for(payload, edit_row(text, "S1-04", decision="fix b"), pdf=True)
    assert "no proposal b on this row" in errors[0]
    _none, errors = entries_for(payload, edit_row(text, "S1-01", decision="fix"), pdf=True)
    assert "this row has no proposals" in errors[0]


def test_rejecting_a_proposal_with_ok_is_recorded_as_accepted_as_extracted():
    payload = fx.architecture()
    _v, text = make(payload, pdf=True)
    entries, errors = entries_for(payload, edit_row(text, "S1-04", decision="ok: the printed title is wrapped"), pdf=True)
    assert errors == [] and [(e["field"], e["disposition"]) for e in entries] == [("row", "accepted")]


def test_edit_needs_a_value_and_a_reason_and_a_readable_term():
    payload = fx.bscs()
    _v, text = make(payload)
    entries, errors = entries_for(payload, edit_row(text, "S1-02", decision="edit: PDF page 1 shows this", new_title="Intro to Computing", new_term="2nd Year / 1st Semester"))
    assert errors == []
    assert [(e["field"], e["old_value"], e["new_value"], e["fix_id"]) for e in entries[1:]] == [
        ("course_title", "Introduction to Computing", "Intro to Computing", None),
        ("term", "1st Year / 1st Semester", "2nd Year / 1st Semester", None)]
    for cols, message in [
        (dict(decision="edit: why"), "fill at least one"),
        (dict(decision="edit", new_title="X"), "needs a reason"),
        (dict(decision="edit: why", new_term="never"), "is not a year and one semester"),
        (dict(decision="edit: why", new_title="Introduction to Computing"), "equals the current one"),
        (dict(new_title="X"), "needs a decision"),
        (dict(decision="ok", new_title="X"), "cannot carry new values"),
    ]:
        _e, errors = entries_for(payload, edit_row(text, "S1-02", **cols))
        assert message in errors[0], (cols, errors)


def test_unresolved_needs_a_reason_and_writes_no_correction():
    payload = fx.bscs()
    _v, text = make(payload)
    _e, errors = entries_for(payload, edit_row(text, "S1-02", decision="unresolved"))
    assert "needs a reason" in errors[0]
    entries, errors = entries_for(payload, edit_row(text, "S1-02", decision="unresolved: PDF unreadable here"))
    assert errors == [] and [(e["field"], e["disposition"], e["new_value"]) for e in entries] == [("row", "unresolved", None)]


def test_confirming_a_clean_section_accepts_every_row_but_not_other_sections():
    payload = fx.bscs()
    _v, text = make(payload)
    entries, errors = entries_for(payload, set_line(text, "S1", "confirm", "yes"))
    assert errors == []
    assert [(e["locator"]["code_at_review"], e["via"], e["reason"]) for e in entries] == [
        ("CS 1", "section_confirm", "section confirmed as extracted"), ("CC 1/L", "section_confirm", "section confirmed as extracted")]
    both = set_line(set_line(text, "S1", "confirm", "yes"), "S1", "reason", "checked against page 1")
    assert {e["reason"] for e in entries_for(payload, both)[0]} == {"checked against page 1"}


def test_confirming_a_section_with_an_undecided_flagged_row_is_refused_and_writes_nothing():
    payload = fx.architecture()
    _v, text = make(payload, pdf=True)
    entries, errors = entries_for(payload, set_line(text, "S1", "confirm", "yes"), pdf=True)
    assert entries == []
    assert sorted(e.split(":")[0] for e in errors) == ["S1-02", "S1-04"] and "flagged but undecided" in errors[0]


def test_info_flags_do_not_block_a_confirm():
    payload = fx.bscs()   # CS 1 carries an info flag (banner text in its own cell)
    _v, text = make(payload)
    assert "INFO banner_in_cell" in text
    assert entries_for(payload, set_line(text, "S1", "confirm", "yes"))[1] == []


def test_accepting_a_class_applies_that_proposal_to_every_undecided_row_of_the_section():
    payload = fx.architecture()
    _v, text = make(payload, pdf=True)
    text = set_line(set_line(text, "S1", "accept", "title_from_pdf"), "S1", "reason", "titles checked against PDF page 1")
    entries, errors = entries_for(payload, edit_row(text, "S1-04", decision="ok: keep as printed"), pdf=True)
    assert errors == []
    assert [(e["locator"]["code_at_review"], e["field"], e["via"]) for e in entries] == [
        ("TOA-1/L", "row", "section_accept"), ("TOA-1/L", "course_title", "section_accept"), ("GE-PC", "row", "sheet")]
    _e, errors = entries_for(payload, set_line(text, "S1", "reason", ""), pdf=True)
    assert "accept needs a reason" in errors[0]
    _e, errors = entries_for(payload, set_line(text, "S1", "accept", "everything"), pdf=True)
    assert "unknown class 'everything'" in errors[0]


def test_printed_codes_can_only_be_ok_or_unresolved_and_both_need_a_reason():
    payload = fx.innovation()
    _v, text = make(payload)
    assert "SU-U1" in text
    _e, errors = entries_for(payload, edit_row(text, "SU-U1", decision="ok"))
    assert "needs a reason" in errors[0]
    _e, errors = entries_for(payload, edit_row(text, "SU-U1", decision="fix"))
    assert "can only be `ok` or `unresolved`" in errors[0]
    entries, errors = entries_for(payload, edit_row(text, "SU-U1", decision="unresolved: row above the first banner is missing"))
    assert errors == [] and (entries[0]["field"], entries[0]["disposition"], entries[0]["locator"]["kind"]) == ("unclaimed", "unresolved", "unclaimed")
    all_ok = set_line(set_line(text, "SU", "accept", "unclaimed"), "SU", "reason", "these are listed prerequisites, not courses")
    entries, errors = entries_for(payload, all_ok)
    assert errors == [] and [e["disposition"] for e in entries] == ["accepted"] * 3
```

- [ ] **Step 2: Run them to see them fail**

```powershell
uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_sheet_decisions.py
```

Expected: collection error, `ImportError: cannot import name 'build_entries' from 'backend.bintanong_tools.prospectus_extractor.sheet'`.

- [ ] **Step 3: Extend the sheet module**

In `sheet.py` apply these three replacements (each text occurs once), then append the block below to the end of the file.

**Edit 1.** Replace

```python
from dataclasses import dataclass, field
from typing
```

with

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing
```

**Edit 2.** Replace

```python
from .fixes import Fix
```

with

```python
from .fixes import FIELD_CODE, FIELD_TERM, FIELD_TITLE, Fix, format_term, parse_term
from .ledger import (ACCEPTED, CORRECTED, FIELD_ROW, FIELD_UNCLAIMED, UNRESOLVED, course_locator, course_snapshot,
                     make_entry, unclaimed_locator)
```

**Edit 3.** Replace

```python
FIXED = COLUMNS[:7]
```

with

```python
FIXED = COLUMNS[:7]
FIX_KINDS = {"strip_banner", "move_term", "title_from_pdf"}
EDIT_FIELDS = {"new code": FIELD_CODE, "new title": FIELD_TITLE, "new term": FIELD_TERM}
VERBS = {"ok", "fix", "edit", "unresolved"}
```

Append to the end of `sheet.py`:

```python
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
            errors.append(f"{section.sid}: confirm must be yes or no, not {confirm!r}")
        for name in classes:
            if name not in FIX_KINDS | {"unclaimed"}:
                errors.append(f"{section.sid}: accept lists unknown class {name!r}")
        if classes and not section_reason:
            errors.append(f"{section.sid}: accept needs a reason: line")
        for row in section.rows:
            cells = ps.rows[row.rid]
            verb, letters, reason, problem = parse_decision(cells["decision"])
            edits = {name: cells[col] for col, name in EDIT_FIELDS.items() if cells[col]}
            if problem:
                errors.append(f"{row.rid}: {problem}")
                continue
            via = "sheet"
            if verb is None:
                if edits:
                    errors.append(f"{row.rid}: a new value needs a decision (edit or fix)")
                    continue
                picked = [(l, f) for l, f in row.fixes if f.kind in classes]
                if picked:
                    verb, letters, reason, via = "fix", [l for l, _f in picked], section_reason, "section_accept"
                elif row.item is not None and "unclaimed" in classes:
                    verb, reason, via = "ok", section_reason, "section_accept"
                elif confirm == "yes" and row.worst() is None:
                    verb, reason, via = "ok", section_reason or "section confirmed as extracted", "section_confirm"
                elif confirm == "yes":
                    errors.append(f"{row.rid}: flagged but undecided in a confirmed section; decide it or leave confirm: no")
                    continue
                else:
                    continue
            err = _row_entries(entries, row, section, payload, verb, letters, reason, edits, via, reviewer, pdf_sha256, now)
            errors += [f"{row.rid}: {e}" for e in err]
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
```

- [ ] **Step 4: Run the tests and the suite**

```powershell
uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_sheet_decisions.py tests/test_prospectus_sheet.py
uv run --project backend --extra tools --extra dev --with fastapi==0.141.1 python -m pytest -q tests
```

Expected: `31 passed`; full suite `185 passed`, 13 subtests passed.

- [ ] **Step 5: Progress note and commit**

Add a row: `9. Decisions to entries | done | <hash> | red: ImportError build_entries; green 20 (31 with the sheet tests); full suite 185`.

```powershell
git add tests/test_prospectus_sheet_decisions.py backend/bintanong_tools/prospectus_extractor/sheet.py plans/plan_current_progress/extractor_split_progress.md
git commit -m "feat: turn review-sheet decisions into ledger entries, all or nothing" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 10: The command line, reviewer identity, and the outside-Git guard (tests first)

**Why:** `sheet`, `apply`, `materialise`, `status` and `triage` as one tool. Reviewer identity comes from `--reviewer` or `git config user.name` and is recorded in every entry (master §16.1: no hosted reviewer UI; this is a local file workflow). The PDF hash comes from the PDF file, a declared hash, a later phase's `run_identity`, or the run manifest; without one nothing is written. Output goes next to the candidate, never into a tracked place in the repository (D2).

**Files:**
- Create: `tests/test_prospectus_fixer_cli.py`
- Create: `backend/bintanong_tools/prospectus_extractor/fixer_cli.py`
- Create: `backend/bintanong_tools/prospectus_fixer.py`

- [ ] **Step 1: Write the failing tests**

`tests/test_prospectus_fixer_cli.py`:

```python
import json
from pathlib import Path

import pytest

from backend.bintanong_tools.prospectus_extractor import fixer_cli
from backend.bintanong_tools.prospectus_extractor.course_checks import PdfPage
from backend.bintanong_tools.prospectus_extractor.fixer_cli import (
    FixerError, REPO, assert_outside_git, default_review_dir, fixer_main as main, resolve_identity, resolve_reviewer,
)
from backend.bintanong_tools.prospectus_extractor.ledger import read_entries

import fixer_fixtures as fx
from sheet_helpers import edit_row, set_line

HASH = "c" * 64


def write_candidate(folder: Path, payload, name="x_prospectus.json") -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def sheet_path(candidate: Path) -> Path:
    return default_review_dir(candidate) / "review_sheet.md"


def run(*argv):
    return main([str(a) for a in argv])


def test_default_review_folder_sits_next_to_the_candidate_not_in_the_repository(tmp_path):
    candidate = write_candidate(tmp_path / "run" / "CAD", fx.bscs())
    folder = default_review_dir(candidate)
    assert folder == (tmp_path / "run" / "CAD" / "review" / "x_prospectus").resolve()
    assert_outside_git(folder)   # no error


def test_writing_into_a_tracked_place_in_the_repository_is_refused():
    with pytest.raises(FixerError, match="inside the repository and not git-ignored"):
        assert_outside_git(REPO / "docs" / "review-output")


def test_reviewer_comes_from_the_flag_or_git_config(monkeypatch):
    assert resolve_reviewer("  Nestor ") == "Nestor"

    class Done:
        stdout = "Git Name\n"

    monkeypatch.setattr(fixer_cli.subprocess, "run", lambda *a, **k: Done())
    assert resolve_reviewer(None) == "Git Name"
    Done.stdout = ""
    with pytest.raises(FixerError, match="no reviewer"):
        resolve_reviewer(None)


def test_pdf_identity_comes_from_the_file_then_the_hash_then_a_manifest(tmp_path):
    pdf = tmp_path / "a.pdf"
    pdf.write_bytes(b"%PDF fake")
    digest = fixer_cli.sha256(pdf)
    payload = {"source_path": str(tmp_path / "x_docling.json")}
    assert resolve_identity(payload, pdf=pdf) == {"pdf_sha256": digest, "pdf_path": pdf, "how": "pdf file"}
    with pytest.raises(FixerError, match="does not match"):
        resolve_identity(payload, pdf=pdf, pdf_sha256="0" * 64)
    assert resolve_identity(payload, pdf_sha256=HASH)["pdf_path"] is None
    assert resolve_identity({"run_identity": {"file_sha256": HASH}})["how"] == "run_identity"
    golden = tmp_path / "golden"
    golden.mkdir()
    (golden / "isolated_manifest.json").write_text(json.dumps({"records": [
        {"source": str(pdf), "pdf_sha256": digest, "json_path": str(tmp_path / "x_prospectus.json")}]}), encoding="utf-8")
    found = resolve_identity(payload, golden=golden, pdf_root=tmp_path)
    assert (found["pdf_sha256"], found["pdf_path"], found["how"]) == (digest, pdf, "manifest")
    (golden / "isolated_manifest.json").write_text(json.dumps({"records": [
        {"source": str(pdf), "pdf_sha256": "0" * 64, "json_path": str(tmp_path / "x_prospectus.json")}]}), encoding="utf-8")
    with pytest.raises(FixerError, match="does not match the manifest hash"):
        resolve_identity(payload, golden=golden, pdf_root=tmp_path)
    with pytest.raises(FixerError, match="pdf_sha256 unknown"):
        resolve_identity(payload)


def test_sheet_apply_status_materialise_round_trip(tmp_path, capsys):
    candidate = write_candidate(tmp_path, fx.bscs())
    assert run("sheet", "--candidate", candidate, "--pdf-sha256", HASH) == 0
    sheet = sheet_path(candidate)
    assert "health=clean" in capsys.readouterr().out and sheet.is_file()
    assert run("sheet", "--candidate", candidate, "--pdf-sha256", HASH) == 2          # would overwrite a sheet
    assert "exists" in capsys.readouterr().err
    assert run("sheet", "--candidate", candidate, "--pdf-sha256", HASH, "--force") == 0
    capsys.readouterr()

    assert run("status", "--candidate", candidate, "--pdf-sha256", HASH) == 0
    assert json.loads(capsys.readouterr().out)["state"] == "pending"

    text = set_line(set_line(sheet.read_text(encoding="utf-8"), "S1", "confirm", "yes"), "S2", "confirm", "yes")
    sheet.write_text(text, encoding="utf-8")
    assert run("apply", "--candidate", candidate, "--pdf-sha256", HASH, "--reviewer", "Nestor", "--dry-run") == 0
    assert not (sheet.parent / "decision_ledger.jsonl").exists()
    assert run("apply", "--candidate", candidate, "--pdf-sha256", HASH, "--reviewer", "Nestor") == 0
    assert "4 entries written, 0 already" in capsys.readouterr().out.splitlines()[-1]
    assert run("apply", "--candidate", candidate, "--pdf-sha256", HASH, "--reviewer", "Nestor") == 0
    assert "0 entries written, 4 already" in capsys.readouterr().out
    ledger = sheet.parent / "decision_ledger.jsonl"
    assert {e["reviewer"] for e in read_entries(ledger)} == {"Nestor"}

    assert run("status", "--candidate", candidate, "--pdf-sha256", HASH) == 0
    assert json.loads(capsys.readouterr().out)["state"] == "reviewed"
    assert run("status", "--candidate", candidate, "--pdf-sha256", "d" * 64) == 0     # another PDF: nothing applies
    other = json.loads(capsys.readouterr().out)
    assert (other["state"], other["inapplicable_entries"]) == ("pending", 4)

    assert run("materialise", "--candidate", candidate, "--pdf-sha256", HASH) == 0
    corrected = json.loads((sheet.parent / "corrected_candidate.json").read_text(encoding="utf-8"))
    assert corrected["review"]["content_review"]["state"] == "reviewed" and corrected["review"]["schema"] == "prospectus-corrected-candidate-v1"


def test_apply_refuses_a_sheet_that_no_longer_matches_the_candidate_and_writes_nothing(tmp_path, capsys):
    candidate = write_candidate(tmp_path, fx.bscs())
    assert run("sheet", "--candidate", candidate, "--pdf-sha256", HASH) == 0
    sheet = sheet_path(candidate)
    sheet.write_text(set_line(sheet.read_text(encoding="utf-8"), "S1", "confirm", "yes"), encoding="utf-8")
    changed = fx.bscs()
    changed["courses"][0]["course_title"] = "Another title"
    write_candidate(tmp_path, changed)
    capsys.readouterr()
    assert run("apply", "--candidate", candidate, "--pdf-sha256", HASH, "--reviewer", "N") == 2
    assert "regenerate it" in capsys.readouterr().err
    assert not (sheet.parent / "decision_ledger.jsonl").exists()


def test_apply_with_a_bad_decision_lists_every_problem_and_writes_nothing(tmp_path, capsys):
    candidate = write_candidate(tmp_path, fx.bscs())
    run("sheet", "--candidate", candidate, "--pdf-sha256", HASH)
    sheet = sheet_path(candidate)
    text = edit_row(sheet.read_text(encoding="utf-8"), "S1-01", decision="approve")
    sheet.write_text(edit_row(text, "S1-02", decision="edit"), encoding="utf-8")
    capsys.readouterr()
    assert run("apply", "--candidate", candidate, "--pdf-sha256", HASH, "--reviewer", "N") == 2
    err = capsys.readouterr().err
    assert "2 problem(s); nothing was written" in err and "S1-01: unknown decision" in err and "S1-02: edit: fill at least one" in err
    assert not (sheet.parent / "decision_ledger.jsonl").exists()


def test_the_pdf_text_checks_run_when_the_pdf_file_is_given(tmp_path, monkeypatch, capsys):
    pdf = tmp_path / "bsa.pdf"
    pdf.write_bytes(b"%PDF fake")
    monkeypatch.setattr(fixer_cli, "load_pdf_pages", lambda path: {1: PdfPage(fx.ARCH_PAGE_TEXT)})
    candidate = write_candidate(tmp_path, fx.architecture())
    assert run("sheet", "--candidate", candidate, "--pdf", pdf) == 0
    text = sheet_path(candidate).read_text(encoding="utf-8")
    assert "- pdf_text_checked: yes" in text and f"- pdf_sha256: {fixer_cli.sha256(pdf)}" in text and "title_from_pdf" in text
    capsys.readouterr()
    assert run("sheet", "--candidate", candidate, "--pdf", pdf, "--no-pdf-text", "--force") == 0
    assert "pdf_text_checked=no" in capsys.readouterr().out


def test_triage_lists_the_healthiest_first_and_collapses_a_repeated_pdf(tmp_path, capsys):
    runs, golden = tmp_path / "runs", tmp_path / "golden"
    golden.mkdir()
    records = []
    for number, (payload, digest) in enumerate([(fx.innovation(), "1" * 64), (fx.bscs(), "2" * 64), (fx.bscs(), "2" * 64)], 1):
        folder = runs / f"{number:02d}"
        write_candidate(folder, payload, "candidate.json")
        source = tmp_path / "docling" / f"p{number}_docling.json"
        (folder / "source.txt").write_text(str(source), encoding="utf-8")
        records.append({"source": str(tmp_path / f"p{number}.pdf"), "pdf_sha256": digest, "json_path": str(source).replace("_docling.json", "_prospectus.json")})
    (golden / "isolated_manifest.json").write_text(json.dumps({"records": records}), encoding="utf-8")
    out = tmp_path / "out" / "TRIAGE.md"
    assert run("triage", "--runs", runs, "--golden", golden, "--out", out) == 0
    lines = out.read_text(encoding="utf-8").splitlines()
    table = [l for l in lines if l.startswith("| 0")]
    assert [l.split("|")[1].strip() for l in table] == ["02", "01"]          # clean BS CS before the broken one
    assert "| clean |" in table[0] and "| broken |" in table[1] and "unclaimed_code 3" in table[1]
    assert "Skipped duplicates: 03 (same PDF as 02)" in lines[-1]


def test_the_module_entry_point_is_a_thin_wrapper():
    from backend.bintanong_tools import prospectus_fixer
    assert prospectus_fixer.main is fixer_cli.fixer_main


def test_a_damaged_ledger_is_reported_without_a_traceback(tmp_path, capsys):
    candidate = write_candidate(tmp_path, fx.bscs())
    run("sheet", "--candidate", candidate, "--pdf-sha256", HASH)
    ledger = default_review_dir(candidate) / "decision_ledger.jsonl"
    ledger.write_text("{broken\n", encoding="utf-8")
    capsys.readouterr()
    assert run("status", "--candidate", candidate, "--pdf-sha256", HASH) == 2
    assert "not JSON" in capsys.readouterr().err


def test_the_legacy_shim_still_exposes_the_extractors_own_main_and_text_constants():
    # The shim re-exports every public name of every module, last module wins: a new module that
    # defines `main` or its own DASHES would silently replace the extractor's.
    from backend.bintanong_tools.bintanong_jsonifer_prolog import bintanong_prospectus_jsonifier as shim
    from backend.bintanong_tools.prospectus_extractor import cli, text

    assert shim.main is cli.main and shim.DASHES is text.DASHES
```

- [ ] **Step 2: Run them to see them fail**

```powershell
uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_fixer_cli.py
```

Expected: collection error, `ImportError: cannot import name 'fixer_cli' from 'backend.bintanong_tools.prospectus_extractor'`.

- [ ] **Step 3: Implement the command line and the entry point**

`backend/bintanong_tools/prospectus_extractor/fixer_cli.py`:

```python
"""Command line of the year/semester fixer.

    sheet        candidate.json -> review_sheet.md  (flags, proposals, health per section)
    apply        edited review_sheet.md -> decision ledger lines (nothing is written on any error)
    materialise  candidate.json + ledger -> corrected_candidate.json and the content-review state
    status       content-review state from the ledger
    triage       a runs folder -> TRIAGE.md, one line per distinct PDF, healthiest first

Sheets, ledgers and corrected candidates hold institutional data. They go in
`<candidate folder>/review/<candidate name>/` by default, never inside this repository unless the
path is git-ignored. Nothing here approves a curriculum.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from .course_checks import load_pdf_pages, manifest_index, resolve_pdf, sha256
from .ledger import LedgerError, append_entries, content_review_state, materialise, read_entries, write_corrected
from .sheet import build_entries, candidate_sha256, check_against, parse_sheet, render_sheet
from .verify import verify_candidate

REPO = Path(__file__).resolve().parents[3]
HEALTH_ORDER = {"clean": 0, "warnings_only": 1, "mixed": 2, "broken": 3}


class FixerError(Exception):
    """A usage problem the reviewer can fix; printed without a traceback."""


def resolve_reviewer(flag: str | None) -> str:
    if flag and flag.strip():
        return flag.strip()
    try:
        name = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True, check=False).stdout.strip()
    except OSError:
        name = ""
    if not name:
        raise FixerError("no reviewer: pass --reviewer NAME or set git config user.name")
    return name


def assert_outside_git(path: Path) -> None:
    """Refuse to write institutional data into a tracked place in this repository."""
    path = Path(path).resolve()
    try:
        path.relative_to(REPO)
    except ValueError:
        return
    ignored = False
    try:
        ignored = subprocess.run(["git", "check-ignore", "-q", str(path)], cwd=REPO, check=False, stderr=subprocess.DEVNULL).returncode == 0
    except OSError:
        pass
    if not ignored:
        raise FixerError(f"{path} is inside the repository and not git-ignored; choose --review-dir outside it")


def default_review_dir(candidate: Path) -> Path:
    return candidate.resolve().parent / "review" / candidate.stem


def resolve_identity(
    payload: Mapping[str, Any], *, pdf: Path | None = None, pdf_sha256: str | None = None,
    golden: Path | None = None, pdf_root: Path | None = None,
) -> dict[str, Any]:
    """The PDF this candidate came from: {"pdf_sha256", "pdf_path" or None, "how"}. The sheet needs
    the hash; the PDF text layer (for the title and code checks) only when the file is at hand."""
    if pdf is not None:
        if not Path(pdf).is_file():
            raise FixerError(f"PDF not found: {pdf}")
        digest = sha256(Path(pdf))
        if pdf_sha256 and pdf_sha256 != digest:
            raise FixerError("--pdf-sha256 does not match the --pdf file")
        return {"pdf_sha256": digest, "pdf_path": Path(pdf), "how": "pdf file"}
    if pdf_sha256:
        return {"pdf_sha256": pdf_sha256, "pdf_path": None, "how": "declared hash"}
    recorded = ((payload.get("run_identity") or {}).get("file_sha256"))  # written by a later phase
    if recorded:
        return {"pdf_sha256": recorded, "pdf_path": None, "how": "run_identity"}
    source = Path(str(payload.get("source_path") or ""))
    if source.suffix.lower() == ".pdf" and source.is_file():
        return {"pdf_sha256": sha256(source), "pdf_path": source, "how": "source_path"}
    if golden is not None:
        record = manifest_index(Path(golden)).get(re.sub(r"[()]", "_", str(payload.get("source_path") or "")))
        if record:
            path, ok = resolve_pdf(record, Path(pdf_root) if pdf_root else Path("."))
            if path is not None and not ok:
                raise FixerError(f"{path} does not match the manifest hash {record['pdf_sha256']}")
            return {"pdf_sha256": record["pdf_sha256"], "pdf_path": path, "how": "manifest"}
    raise FixerError("pdf_sha256 unknown: pass --pdf FILE, --pdf-sha256 HASH, or --golden RUN_FOLDER (isolated_manifest.json)")


def _load(candidate: Path) -> dict[str, Any]:
    try:
        return json.loads(Path(candidate).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FixerError(f"cannot read candidate {candidate}: {exc}") from exc


def _prepare(args) -> tuple[dict, dict, Any]:
    payload = _load(args.candidate)
    identity = resolve_identity(payload, pdf=args.pdf, pdf_sha256=args.pdf_sha256, golden=args.golden, pdf_root=args.pdf_root)
    pages = load_pdf_pages(identity["pdf_path"]) if identity["pdf_path"] is not None and not args.no_pdf_text else None
    return payload, identity, pages


def cmd_sheet(args) -> int:
    payload, identity, pages = _prepare(args)
    folder = args.review_dir or default_review_dir(args.candidate)
    assert_outside_git(folder)
    target = folder / "review_sheet.md"
    if target.exists() and not args.force:
        raise FixerError(f"{target} exists; it may hold unapplied decisions. Move it or pass --force")
    verification = verify_candidate(payload, pages)
    identity = {**identity, "candidate_sha256": candidate_sha256(payload)}
    folder.mkdir(parents=True, exist_ok=True)
    target.write_text(render_sheet(payload, verification, identity), encoding="utf-8", newline="\n")
    print(f"{target}  health={verification.health}  pdf_text_checked={'yes' if verification.pdf_checked else 'no'}")
    for section in verification.sections:
        print(f"  {section.sid:<4}{section.health:<8}{section.title}")
    return 0


def cmd_apply(args) -> int:
    payload, identity, pages = _prepare(args)
    folder = args.review_dir or default_review_dir(args.candidate)
    sheet_path = args.sheet or folder / "review_sheet.md"
    ledger_path = args.ledger or folder / "decision_ledger.jsonl"
    assert_outside_git(ledger_path.parent)
    verification = verify_candidate(payload, pages)
    expected_identity = {**identity, "candidate_sha256": candidate_sha256(payload)}
    parsed = parse_sheet(Path(sheet_path).read_text(encoding="utf-8"))
    errors = check_against(parsed, parse_sheet(render_sheet(payload, verification, expected_identity)))
    entries: list = []
    if not errors:
        reviewer = resolve_reviewer(args.reviewer)
        entries, errors = build_entries(parsed, payload, verification, reviewer=reviewer, pdf_sha256=identity["pdf_sha256"])
    if errors:
        print(f"{len(errors)} problem(s); nothing was written:", file=sys.stderr)
        for message in errors:
            print(f"  {message}", file=sys.stderr)
        return 2
    if args.dry_run:
        print(f"dry run: {len(entries)} entries would be recorded in {ledger_path}")
        return 0
    written, skipped = append_entries(ledger_path, entries)
    print(f"{written} entries written, {skipped} already in {ledger_path}")
    return 0


def cmd_materialise(args) -> int:
    payload = _load(args.candidate)
    identity = resolve_identity(payload, pdf=args.pdf, pdf_sha256=args.pdf_sha256, golden=args.golden, pdf_root=args.pdf_root)
    folder = args.review_dir or default_review_dir(args.candidate)
    entries = read_entries(args.ledger or folder / "decision_ledger.jsonl")
    corrected, report = materialise(payload, entries, identity["pdf_sha256"])
    out = args.out or folder / "corrected_candidate.json"
    assert_outside_git(out.parent)
    write_corrected(out, corrected)
    state = report["content_review"]
    print(f"{out}: {report['applied']} corrections applied, {len(report['skipped'])} entries skipped; content_review={state['state']}")
    for skip in report["skipped"]:
        print(f"  skipped {skip['entry_id']}: {skip['reason']}")
    return 0


def cmd_status(args) -> int:
    payload = _load(args.candidate)
    identity = resolve_identity(payload, pdf=args.pdf, pdf_sha256=args.pdf_sha256, golden=args.golden, pdf_root=args.pdf_root)
    folder = args.review_dir or default_review_dir(args.candidate)
    state = content_review_state(payload, read_entries(args.ledger or folder / "decision_ledger.jsonl"), identity["pdf_sha256"])
    print(json.dumps(state, indent=2))
    return 0


def cmd_triage(args) -> int:
    index = manifest_index(args.golden)
    rows, seen = [], {}
    for folder in sorted(p for p in args.runs.iterdir() if p.is_dir() and (p / "candidate.json").exists()):
        payload = _load(folder / "candidate.json")
        source = (folder / "source.txt").read_text(encoding="utf-8").strip()
        record = index.get(re.sub(r"[()]", "_", source))
        digest = record["pdf_sha256"] if record else None
        if digest in seen:
            rows.append((folder.name, None, f"same PDF as {seen[digest]}"))
            continue
        seen[digest] = folder.name
        pages = None
        if record and args.pdf_root:
            path, ok = resolve_pdf(record, args.pdf_root)
            pages = load_pdf_pages(path) if path is not None and ok else None
        rows.append((folder.name, (payload, verify_candidate(payload, pages)), ""))
    shown = [r for r in rows if r[1] is not None]
    shown.sort(key=lambda r: (HEALTH_ORDER[r[1][1].health], r[0]))
    lines = ["# Review triage", "",
             f"{len(shown)} distinct PDFs, healthiest first. Confirm clean sections in bulk; spend review time on broken ones.", "",
             "| n | program | audit | health | PDF text | sections clean / review / broken | error and warn flags |", "|---|---|---|---|---|---|---|"]
    for name, (payload, v), _note in shown:
        tally = [sum(s.health == h for s in v.sections) for h in ("clean", "review", "broken")]
        flags = ", ".join(f"{k} {n}" for k, n in v.counts().items()) or "-"
        lines.append(f"| {name} | {(payload.get('program') or '').replace('|', '/')} | {payload['audit']['status']} | {v.health} | "
                     f"{'checked' if v.pdf_checked else 'not checked'} | {tally[0]} / {tally[1]} / {tally[2]} | {flags} |")
    dupes = [f"{n} ({note})" for n, pair, note in rows if pair is None]
    if dupes:
        lines += ["", "Skipped duplicates: " + ", ".join(dupes)]
    out = Path(args.out)
    assert_outside_git(out.parent)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"{out}: {len(shown)} prospectuses")
    return 0


def build_parser() -> argparse.ArgumentParser:
    cli = argparse.ArgumentParser(prog="prospectus_fixer", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = cli.add_subparsers(dest="command", required=True)

    def common(p, *, needs_candidate=True):
        if needs_candidate:
            p.add_argument("--candidate", type=Path, required=True, help="candidate.json (the *_prospectus.json output)")
        p.add_argument("--pdf", type=Path, help="the original PDF: gives the hash and the PDF text checks")
        p.add_argument("--pdf-sha256", help="hash of the original PDF when the file is not at hand (PDF text is then not checked)")
        p.add_argument("--golden", type=Path, help="run folder with isolated_manifest.json, to look the PDF up")
        p.add_argument("--pdf-root", type=Path, help="folder searched for the PDF named in the manifest")
        p.add_argument("--review-dir", type=Path, help="default: <candidate folder>/review/<candidate name>")
        p.add_argument("--no-pdf-text", action="store_true", help="skip the PDF text checks even when the PDF is found")

    p = sub.add_parser("sheet", help="write the review sheet")
    common(p)
    p.add_argument("--force", action="store_true")
    p.set_defaults(run=cmd_sheet)
    p = sub.add_parser("apply", help="validate the edited sheet and append ledger entries")
    common(p)
    p.add_argument("--sheet", type=Path)
    p.add_argument("--ledger", type=Path)
    p.add_argument("--reviewer", help="default: git config user.name")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(run=cmd_apply)
    p = sub.add_parser("materialise", help="write corrected_candidate.json from the ledger")
    common(p)
    p.add_argument("--ledger", type=Path)
    p.add_argument("--out", type=Path)
    p.set_defaults(run=cmd_materialise)
    p = sub.add_parser("status", help="content-review state from the ledger")
    common(p)
    p.add_argument("--ledger", type=Path)
    p.set_defaults(run=cmd_status)
    p = sub.add_parser("triage", help="TRIAGE.md for a runs folder")
    p.add_argument("--runs", type=Path, required=True, help="folder of NN/ run folders (candidate.json, source.txt)")
    p.add_argument("--golden", type=Path, required=True)
    p.add_argument("--pdf-root", type=Path)
    p.add_argument("--out", type=Path, required=True)
    p.set_defaults(run=cmd_triage)
    return cli


def fixer_main(argv: Sequence[str] | None = None) -> int:
    # Not `main`: the legacy shim re-exports every module's public names and `main` must stay cli.main.
    args = build_parser().parse_args(argv)
    try:
        return args.run(args)
    except (FixerError, LedgerError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
```

`backend/bintanong_tools/prospectus_fixer.py`:

```python
"""Review sheets and a decision ledger for the year/semester sections of a prospectus candidate.

    python -m backend.bintanong_tools.prospectus_fixer sheet --candidate candidate.json --pdf original.pdf
"""

from __future__ import annotations

from .prospectus_extractor.fixer_cli import fixer_main as main

if __name__ == "__main__":
    raise SystemExit(main())
```

Why the entry function is `fixer_main` and not `main`: the legacy shim (`bintanong_prospectus_jsonifier.py`) copies every public name of every package module into its own namespace, last module wins. A second `main` would replace `cli.main` and break `--self-test` through the shim. The last test in the file pins this for `main` and `DASHES`.

- [ ] **Step 4: Run the tests, the entry points and the suite**

```powershell
uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_fixer_cli.py tests/test_prospectus_entrypoints.py
uv run --project backend --extra tools --extra dev python -m backend.bintanong_tools.prospectus_fixer --help
uv run --project backend --extra tools --extra dev --with fastapi==0.141.1 python -m pytest -q tests
```

Expected: `17 passed` (12 here plus the 5 entry-point tests, including the legacy shim self-test); `--help` lists `sheet, apply, materialise, status, triage`; full suite `197 passed`, 13 subtests passed.

- [ ] **Step 5: Progress note and commit**

Add a row: `10. CLI, reviewer, outside-Git guard | done | <hash> | red: ModuleNotFoundError fixer_cli; green 12; shim keeps cli.main and text.DASHES; full suite 197`.

```powershell
git add tests/test_prospectus_fixer_cli.py backend/bintanong_tools/prospectus_extractor/fixer_cli.py backend/bintanong_tools/prospectus_fixer.py plans/plan_current_progress/extractor_split_progress.md
git commit -m "feat: sheet, apply, materialise, status and triage commands with a local-only storage guard" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 11: End to end on three prospectuses of different health, and the sheets for the trial

**Why:** prove the pieces work together on small fixtures (automated), then on three real prospectuses of different health plus the broken one, and produce the sheets the user will try. BSBA-HRM is nearly clean, BS Computer Science is medium, BS Architecture has 19 glued titles, BSE-Innovation-and-Tech is badly broken (2 courses extracted, 76 printed codes unclaimed).

**Files:**
- Create: `tests/test_prospectus_fixer_e2e.py`

- [ ] **Step 1: Write the end-to-end test**

Three fixtures through `sheet`, `apply`, `status` and `materialise` with the real command line: a clean one confirmed in two lines, a medium one where one class-accept per section fixes the glued titles and `materialise` writes them while the original JSON stays untouched, and a broken one where the reviewer can only mark the unparsed printed codes unresolved.

`tests/test_prospectus_fixer_e2e.py`:

```python
"""Three candidates of different health through sheet, apply, status and materialise."""

import json

from backend.bintanong_tools.prospectus_extractor import fixer_cli
from backend.bintanong_tools.prospectus_extractor.course_checks import PdfPage
from backend.bintanong_tools.prospectus_extractor.fixer_cli import default_review_dir, fixer_main as main

import fixer_fixtures as fx
from sheet_helpers import edit_row, set_line


def step(capsys, *argv):
    code = main([str(a) for a in argv])
    return code, capsys.readouterr()


def state(capsys, candidate, *identity):
    code, out = step(capsys, "status", "--candidate", candidate, *identity)
    assert code == 0
    return json.loads(out.out)


def review(tmp_path, name, payload, pdf):
    candidate = tmp_path / name / "candidate.json"
    candidate.parent.mkdir()
    candidate.write_text(json.dumps(payload), encoding="utf-8")
    return candidate, default_review_dir(candidate)


def test_clean_medium_and_broken_candidates(tmp_path, monkeypatch, capsys):
    pdf = tmp_path / "x.pdf"
    pdf.write_bytes(b"%PDF fake")

    # clean: confirm both sections in two lines, the whole review is one apply
    candidate, folder = review(tmp_path, "bscs", fx.bscs(), pdf)
    declared = ("--pdf-sha256", "d" * 64)   # no PDF at hand: the text checks are skipped, the rest runs
    assert step(capsys, "sheet", "--candidate", candidate, *declared)[0] == 0
    sheet = folder / "review_sheet.md"
    text = sheet.read_text(encoding="utf-8")
    assert "- prospectus health: clean (2 clean, 0 review, 0 broken)" in text
    sheet.write_text(set_line(set_line(text, "S1", "confirm", "yes"), "S2", "confirm", "yes"), encoding="utf-8")
    assert step(capsys, "apply", "--candidate", candidate, *declared, "--reviewer", "Nestor")[0] == 0
    assert state(capsys, candidate, *declared)["state"] == "reviewed"

    # medium: glued titles get proposals; one class accept per section, then confirm
    monkeypatch.setattr(fixer_cli, "load_pdf_pages", lambda path: {1: PdfPage(fx.ARCH_PAGE_TEXT)})
    candidate, folder = review(tmp_path, "arch", fx.architecture(), pdf)
    assert step(capsys, "sheet", "--candidate", candidate, "--pdf", pdf)[0] == 0
    sheet = folder / "review_sheet.md"
    text = sheet.read_text(encoding="utf-8")
    assert "- prospectus health: mixed (0 clean, 2 review, 1 broken)" in text   # the broken one is SU: printed codes in the PDF no course claims
    for sid in ("S1", "S2"):
        text = set_line(set_line(set_line(text, sid, "accept", "title_from_pdf"), sid, "reason", "titles checked on PDF page 1"), sid, "confirm", "yes")
    sheet.write_text(text, encoding="utf-8")
    assert step(capsys, "apply", "--candidate", candidate, "--pdf", pdf, "--reviewer", "Nestor")[0] == 0
    assert state(capsys, candidate, "--pdf", pdf)["state"] == "reviewed"
    assert step(capsys, "materialise", "--candidate", candidate, "--pdf", pdf)[0] == 0
    corrected = json.loads((folder / "corrected_candidate.json").read_text(encoding="utf-8"))
    titles = {c["course_code"]: c["course_title"] for c in corrected["courses"]}
    assert titles["GE-PC"] == "Purposive Communication" and titles["TOA-2"] == "Theory of Architecture 2"
    assert titles["VT-2/L"] == "Architectural Visual Communications 4-Visual Techniques 2"
    assert corrected["review"]["applied_entry_ids"] and corrected["review"]["skipped"] == []
    original = json.loads(candidate.read_text(encoding="utf-8"))
    assert {c["course_code"]: c["course_title"] for c in original["courses"]}["GE-PC"] == "Techniques 1 Purposive Communication"

    # broken: the sheet lists what could not be read; the reviewer can only mark it unresolved
    candidate, folder = review(tmp_path, "innov", fx.innovation(), pdf)
    assert step(capsys, "sheet", "--candidate", candidate, "--pdf-sha256", "e" * 64)[0] == 0
    sheet = folder / "review_sheet.md"
    text = sheet.read_text(encoding="utf-8")
    assert "- prospectus health: broken" in text and "## SU - Unplaced printed codes" in text and "## S1 - 1st Year - 1st Semester" in text
    for rid in ("SU-U1", "SU-U2", "SU-U3"):
        text = edit_row(text, rid, decision="unresolved: printed on the PDF above the FOURTH YEAR banner, not parsed")
    sheet.write_text(set_line(set_line(text, "S2", "confirm", "yes"), "S3", "confirm", "yes"), encoding="utf-8")
    assert step(capsys, "apply", "--candidate", candidate, "--pdf-sha256", "e" * 64, "--reviewer", "Nestor")[0] == 0
    code, out = step(capsys, "status", "--candidate", candidate, "--pdf-sha256", "e" * 64)
    result = json.loads(out.out)
    assert (result["state"], result["decided"], result["unresolved"], result["unclaimed_undecided"]) == ("partially_reviewed", 2, 3, 0)
```

- [ ] **Step 2: Run it (expected to pass at once) and prove it can fail**

```powershell
uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_fixer_e2e.py
```

Expected: `1 passed`. This is an integration test over pieces that each went red then green in Tasks 3 to 10, so it passes on first run by design. Show that it can fail by breaking one rule temporarily, then restore it:

```powershell
(Get-Content backend/bintanong_tools/prospectus_extractor/ledger.py -Raw) -replace 'elif decided == len\(courses\) and undecided == 0 and unresolved == 0:', 'elif False:' | Set-Content backend/bintanong_tools/prospectus_extractor/ledger.py -NoNewline
uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_fixer_e2e.py
git checkout -- backend/bintanong_tools/prospectus_extractor/ledger.py
```

Expected: `1 failed` (`assert 'partially_reviewed' == 'reviewed'`), and after `git checkout` the file is back (`git status --short` does not list `ledger.py`).

- [ ] **Step 3: Produce the trial sheets for four real prospectuses**

Each folder under `$CHECK` holds the PDF, the markup twin and the candidate JSON, so the sheet goes next to them (default location `<folder>\review\<candidate name>\`, outside Git). Open the markup twin (`*_prospectus.md`, Ctrl+Shift+V) beside the sheet.

```powershell
$CHECK = 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\markup_twin_visual_check_2026-10-03\all'
$cases = @(
  @('CBA\BSBA - HUMAN RESOURCE', 'BSBA-HRM-for-student-new-version'),
  @('CS\Computer Science\New Curriculum (2025-2026)', '1_BS Computer Science_for BOR approval _rev02_v7_6 August 2025'),
  @('CAD', 'BSA-for-student-new-version'),
  @('CBA\BS ENTREP - INNOVATION TECH', 'BSE-Innovation-and-Tech-for-student-new-version')
)
foreach ($c in $cases) {
  $folder = Join-Path $CHECK $c[0]; $name = $c[1]
  uv run --project backend --extra tools --extra dev python -m backend.bintanong_tools.prospectus_fixer sheet --candidate "$folder\${name}_prospectus.json" --pdf "$folder\$name.pdf"
}
```

Expected (`sheet` needs no reviewer name; running it again for the same prospectus needs `--force` so a sheet with decisions is never overwritten by accident):

```
...\BSBA - HUMAN RESOURCE\review\BSBA-HRM-for-student-new-version_prospectus\review_sheet.md  health=warnings_only  pdf_text_checked=yes
  S1  clean   1st Year - 1st Semester
  S2  clean   1st Year - 2nd Semester
  S3  clean   2nd Year - 1st Semester
  S4  review  2nd Year - 2nd Semester
  S5  clean   3rd Year - 1st Semester
  S6  clean   3rd Year - 2nd Semester
  S7  clean   4th Year - 1st Semester
  S8  clean   4th Year - 2nd Semester
...\1_BS Computer Science_...\review_sheet.md  health=mixed  pdf_text_checked=yes
  S1  clean   1st Year - 1st Semester
  S2  clean   1st Year - 2nd Semester
  S3  clean   2nd Year - 1st Semester
  S4  clean   2nd Year - 2nd Semester
  S5  clean   3rd Year - 1st Semester
  S6  broken  3rd Year - 2nd Semester
  S7  clean   4th Year - 1st Semester
  S8  clean   4th Year - 2nd Semester
  SU  broken  Unplaced printed codes
...\CAD\review\BSA-for-student-new-version_prospectus\review_sheet.md  health=mixed  pdf_text_checked=yes
  S1  review  1st Year - 1st Semester
  S2  review  1st Year - 2nd Semester
  S3  review  2nd Year - 1st Semester
  S4  broken  2nd Year - 2nd Semester
  S5  review  3rd Year - 1st Semester
  S6  review  3rd Year - 2nd Semester
  S7  review  4th Year - 1st Semester
  S8  review  4th Year - 2nd Semester
  S9  clean   5th Year - 1st Semester
  S10 review  5th Year - 2nd Semester
...\BSE-Innovation-and-Tech-for-student-new-version_prospectus\review_sheet.md  health=broken  pdf_text_checked=yes
  S1  clean   4th Year - 1st Semester
  S2  clean   4th Year - 2nd Semester
  SU  broken  Unplaced printed codes
```

Open the Architecture sheet and check three things by eye: the `GE-PC` row shows `WARN title_not_in_pdf` and the proposal `a) title_from_pdf course_title: "Techniques 1 Purposive Communication" -> "Purposive Communication"`; section `S4` (2nd Year 2nd Semester) says `units: printed 23, extracted 22` and `flags: ERROR unit_total: printed total 23, extracted 22 (-1)`; the Innovation sheet's `SU` table lists `ENTRE 7`, `GE-IER`, `ST 3`, ... with `unclaimed_code` flags.

- [ ] **Step 4: Triage all 39 distinct prospectuses**

```powershell
$d = 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump'
uv run --project backend --extra tools --extra dev python -m backend.bintanong_tools.prospectus_fixer triage --runs "$d\scratch\compare_2026-10-03b\new" --golden "$d\docling_jsonified_output\task2b_standing_isolated_2026-09-29" --pdf-root "$d\PalSU Undergraduate Prospectus Website Dump" --out "$d\markup_twin_visual_check_2026-10-03\TRIAGE.md"
```

Expected: `...\TRIAGE.md: 39 prospectuses` in about 3 seconds. The file lists them healthiest first: 1 `clean` (BS Biology), 3 `warnings_only` (ABPhilStud, BSBA-HRM, IT), 17 `mixed`, 18 `broken`, and the line `Skipped duplicates: 03 (same PDF as 02), 06 (same PDF as 05), 21 (same PDF as 20), 25 (same PDF as 24), 41 (same PDF as 40)`. Count them:

```powershell
$t = Get-Content "$d\markup_twin_visual_check_2026-10-03\TRIAGE.md"
foreach ($h in 'clean','warnings_only','mixed','broken') { "$h " + ($t | Where-Object { $_ -match "^\| \d\d \|.*\| $h \| checked" }).Count }
```

Expected: `clean 1`, `warnings_only 3`, `mixed 17`, `broken 18`.

- [ ] **Step 5: Dry run on a copy: confirm every clean section of BSBA-HRM, apply, check status, materialise**

This uses a scratch review folder so the user's trial sheet stays untouched. Save as `$env:TEMP\confirm_clean.py`:

```python
import re, sys
from pathlib import Path
sheet = Path(sys.argv[1])
lines = sheet.read_text(encoding="utf-8").splitlines()
out, sid, clean = [], None, set()
for line in lines:
    m = re.match(r"^## (S\w+) ", line)
    if m: sid = m.group(1)
    if line.strip() == "health: clean" and sid: clean.add(sid)
    out.append(line)
for i, line in enumerate(out):
    m = re.match(r"^## (S\w+) ", line)
    if m: sid = m.group(1)
    if line.startswith("confirm:") and sid in clean:
        out[i] = "confirm: yes"
sheet.write_text("\n".join(out) + "\n", encoding="utf-8")
print("confirmed", sorted(clean))
```

```powershell
$folder = "$CHECK\CBA\BSBA - HUMAN RESOURCE"; $name = 'BSBA-HRM-for-student-new-version'; $rd = "$env:TEMP\b2trial\hrm"
$args2 = @('--candidate', "$folder\${name}_prospectus.json", '--pdf', "$folder\$name.pdf", '--review-dir', $rd)
uv run --project backend --extra tools --extra dev python -m backend.bintanong_tools.prospectus_fixer sheet @args2 --force
uv run --project backend --extra tools --extra dev python "$env:TEMP\confirm_clean.py" "$rd\review_sheet.md"
uv run --project backend --extra tools --extra dev python -m backend.bintanong_tools.prospectus_fixer apply @args2 --reviewer "trial run"
uv run --project backend --extra tools --extra dev python -m backend.bintanong_tools.prospectus_fixer status @args2
uv run --project backend --extra tools --extra dev python -m backend.bintanong_tools.prospectus_fixer materialise @args2
```

Expected: `confirmed ['S1', 'S2', 'S3', 'S5', 'S6', 'S7', 'S8']`; `42 entries written, 0 already in ...\decision_ledger.jsonl`; status `"state": "partially_reviewed"`, `"courses": 49`, `"decided": 42`, `"unresolved": 0`; materialise `0 corrections applied, 0 entries skipped; content_review=partially_reviewed`. Running `apply` a second time prints `0 entries written, 42 already in ...`.

- [ ] **Step 6: Full suite, progress note, commit**

Full suite expected `198 passed`, 13 subtests passed. Add a row: `11. End to end | done | <hash> | e2e test passes (fails with the reviewed rule broken); 4 trial sheets written; triage 1/3/17/18; HRM dry run 42 entries, partially_reviewed`.

```powershell
git add tests/test_prospectus_fixer_e2e.py plans/plan_current_progress/extractor_split_progress.md
git commit -m "test: end to end review of a clean, a medium and a broken prospectus through the fixer" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 12: Trial review by the user (human gate, no code)

**Why:** the sheet format, the proposal quality and the effort per prospectus are only judged by using them. The user tries the four sheets from Task 11 before the parser task, and decides about it.

- [ ] **Step 1: Hand over**

Stop here and tell the user, in your own words, with these facts:

- Where the four sheets are: `review\<candidate name>\review_sheet.md` inside each prospectus folder under `$CHECK` (BSBA-HRM, BS Computer Science new curriculum, BS Architecture, BSE-Innovation-and-Tech), plus `$CHECK\..\TRIAGE.md` with all 39 ordered by health.
- How to review: open the sheet and the markup twin side by side; in each section either set `confirm: yes` (accepts every unflagged row) or put a decision in the `decision` column of a row: `ok`, `fix` (accept every proposal on the row), `fix a`, `edit: reason` with `new title` / `new code` / `new term`, or `unresolved: reason`; `accept: title_from_pdf` plus a `reason:` line accepts that class of proposal for the whole section.
- How to apply (they run it themselves; it validates the whole sheet first and writes nothing if anything is wrong), per prospectus:

```powershell
uv run --project backend --extra tools --extra dev python -m backend.bintanong_tools.prospectus_fixer apply --candidate "<folder>\<name>_prospectus.json" --pdf "<folder>\<name>.pdf" --reviewer "<their name>"
uv run --project backend --extra tools --extra dev python -m backend.bintanong_tools.prospectus_fixer status --candidate "<folder>\<name>_prospectus.json" --pdf "<folder>\<name>.pdf"
uv run --project backend --extra tools --extra dev python -m backend.bintanong_tools.prospectus_fixer materialise --candidate "<folder>\<name>_prospectus.json" --pdf "<folder>\<name>.pdf"
```

- What to try: BSBA-HRM (confirm the clean sections in bulk, decide the one flagged row); BS Computer Science (the `SU` rows are elective-list codes in a footnote: `accept: unclaimed` with a reason); Architecture (`accept: title_from_pdf` for sections S1 and S2, then check `corrected_candidate.json`); Innovation (look only: it shows what a parser-level failure looks like, nothing in the sheet can fix it).
- What feedback is wanted: anything awkward in the sheet layout, a proposal that is wrong, a flag that is noise, how long a prospectus took.

- [ ] **Step 2: Record what comes back**

When the user returns, run `status` for each prospectus they touched and record in the progress file: states, entries written, time per prospectus, every complaint. Fix each defect they report with a failing test first, in its own commit; do not widen scope (D4, D8 are deliberate).

- [ ] **Step 3: Decide Task 13**

Record in the progress file the user's go or no-go for the parser banner split (D9). No go: skip Task 13 and go to Task 14, noting "Task 13 deferred" in the decision record. Add a row: `12. Trial review | done | n/a | <user's feedback, go/no-go for Task 13>`; commit the progress file only.

```powershell
git add plans/plan_current_progress/extractor_split_progress.md
git commit -m "docs: record the trial review of the section fixer" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 13: Parser-level banner split, gated by the 44-input comparer (tests first)

**Why:** H5. A code or title cell that starts with printed banner phrases is split into banner and course text, both keeping the original cell provenance. Today a glued year plus semester banner corrupts the value: `FIRST YEAR FIRST SEMESTER Discrete Structures 1` becomes the title `SEMESTER Discrete Structures`, and `SECOND SEMESTER Discrete Structures 2` becomes `Discrete Structures` (the series number is taken for a footnote marker). This task **changes extracted values**, so it is reported field by field, not hidden. Run it only after Task 12 gave a go (D9).

Prototype result on the 44 cached inputs, for comparison with your run: exactly one course field changes (file 28, `AS 1`, `course_title`: `EE FIRST SEMESTER Environmental Engineering` becomes `EE Environmental Engineering`), 54 courses gain a `provenance.discarded_fragments` entry (and `resolution_method` becomes `deterministic_repair`, the existing value for "text was set aside"), the verifier's `banner_leak` count falls from 3 to 2, and no other flag count changes. A first, unguarded version also changed two ABComm `GE-STS` titles for the worse (`Science, Technology, & Society 3`); the guard in `_split_banner_prefix` and the regression test for it exist because of that.

**Files:**
- Modify: `tests/test_prospectus_course_compare.py`, `scripts/prospectus_course_compare.py` (comparer options)
- Create: `tests/test_prospectus_banner_split.py`
- Modify: `backend/bintanong_tools/prospectus_extractor/sections.py`

- [ ] **Step 1: Comparer tests first**

Append to `tests/test_prospectus_course_compare.py` (after its last test):

```python
# --- intended changes: reported field by field, gated by an allow list and the verifier flag counts

def _course(code, title, row, **extra):
    base = {"course_code": code, "course_title": title, "year_level": "1st Year", "semester": "1st Semester",
            "total_units": 3, "_source": {"table_index": 0, "row_index": row, "column_group": 0},
            "provenance": {"resolution_method": "deterministic"}}
    base.update(extra)
    return base


def _payload(*courses, errors=()):
    return {"courses": list(courses), "audit": {"status": "ok", "total_courses": len(courses), "errors": list(errors)}}


def test_field_changes_lists_every_changed_field_matched_by_row_not_position():
    old = _payload(_course("CS 1", "SEMESTER Discrete Structures", 3), _course("CS 2", "Alpha", 4))
    new = _payload(_course("CS 0", "Zeta", 2), _course("CS 1", "Discrete Structures 1", 3,
                   provenance={"resolution_method": "deterministic_repair"}), _course("CS 2", "Alpha", 4))
    rows = compare.field_changes(old, new)
    assert [(r["code"], r["field"], r["old"], r["new"]) for r in rows] == [
        ("CS 0", "(course)", "absent", "present"),
        ("CS 1", "course_title", "SEMESTER Discrete Structures", "Discrete Structures 1"),
        ("CS 1", "provenance.resolution_method", "deterministic", "deterministic_repair"),
    ]


def test_allow_change_accepts_listed_fields_only():
    old = _payload(_course("CS 1", "Old", 3))
    new = _payload(_course("CS 1", "New", 3, total_units=4))
    assert compare.compare_payloads(old, new, frozenset({"course_title", "total_units"})) == []
    issues = compare.compare_payloads(old, new, frozenset({"course_title"}))
    assert issues == ["course 0 differs: ['total_units']"]
    assert compare.compare_payloads(old, new) == ["course 0 differs: ['course_title', 'total_units']"]


def test_a_verifier_flag_that_rises_is_reported_and_one_that_falls_is_not():
    import fixer_fixtures as fx

    dirty = fx.bscs()
    dirty["courses"][1]["course_title"] = "EE FIRST SEMESTER Introduction to Computing"
    clean = fx.bscs()
    assert compare.flag_rises(dirty, clean) == {}
    assert compare.flag_rises(clean, dirty) == {"banner_leak": (0, 1)}


def test_compare_runs_fails_on_a_rise_in_flags_and_writes_the_field_report(tmp_path):
    import fixer_fixtures as fx

    old, new = fx.bscs(), fx.bscs()
    new["courses"][1]["course_title"] = "EE FIRST SEMESTER Introduction to Computing"
    for name, data in (("old", old), ("new", new)):
        _run_folder(tmp_path, name, 0, data)
    report = tmp_path / "out" / "changes.csv"
    allow = frozenset({"course_title", "title"})
    assert compare.compare_runs(tmp_path / "old", tmp_path / "new", False, allow, flags=False, report=report) == 0
    assert compare.compare_runs(tmp_path / "old", tmp_path / "new", False, allow, flags=True) == 1
    lines = report.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "input,table,row,column_group,code,field,old,new"
    assert lines[1].startswith("01,0,4,0,CC 1/L,course_title,")
```

```powershell
uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_course_compare.py
```

Expected: `4 failed, 10 passed` (`AttributeError: module 'prospectus_course_compare' has no attribute 'field_changes'`, `compare_payloads() takes 2 positional arguments but 3 were given`, no `flag_rises`, `compare_runs()` too many arguments).

- [ ] **Step 2: Extend the comparer**

Save as `$env:TEMP\edit_compare.py` and run it from the repo root. Each edit replaces one exact text that must occur once; the script stops otherwise.

```python
"""Extend scripts/prospectus_course_compare.py for runs that change extracted values on purpose.
Run from the repo root. Each edit replaces one exact text that must occur exactly once.
"""
from pathlib import Path

PATH = Path("scripts/prospectus_course_compare.py")
text = PATH.read_text(encoding="utf-8")


def replace_once(old: str, new: str) -> None:
    global text
    if text.count(old) != 1:
        raise SystemExit(f"expected exactly one match, found {text.count(old)}: {old[:70]!r}")
    text = text.replace(old, new)


replace_once('''and companions. Later phases extend COURSE_FIELDS / AUDIT_FIELDS or add checks below.
Exit code 0 only when every input matches.
"""''', '''and companions. Later phases extend COURSE_FIELDS / AUDIT_FIELDS or add checks below.
Exit code 0 only when every input matches.

A phase that changes extracted values on purpose passes
    --allow-change course_title,computed_total_units   fields whose change is not a failure
    --report changes.csv                               one row per changed field of every course
    --flags                                            also run the section verifier on both sides
and the run then fails only on a change to a field not listed, and on a rise in any verifier flag
count. Every allowed change is still listed field by field; none is hidden.
"""''')

replace_once('''AUDIT_FIELDS = ("status", "errors", "total_courses", "computed_total_units", "years_detected")
''', '''AUDIT_FIELDS = ("status", "errors", "total_courses", "computed_total_units", "years_detected")
REPORT_ONLY_FIELDS = ("provenance.resolution_method", "provenance.discarded_fragments")  # listed in --report, never gating
''')

replace_once('''def course_fields(payload: dict) -> dict:
    return {
        "courses": [{f: c.get(f) for f in COURSE_FIELDS} for c in payload["courses"]],
        "audit": {f: payload["audit"].get(f) for f in AUDIT_FIELDS},
    }


def compare_payloads(old: dict, new: dict) -> list[str]:
    """Differences between two payloads in course fields and audit counts."""
    a, b = course_fields(old), course_fields(new)''', '''def course_fields(payload: dict, allow=frozenset()) -> dict:
    return {
        "courses": [{f: c.get(f) for f in COURSE_FIELDS if f not in allow} for c in payload["courses"]],
        "audit": {f: payload["audit"].get(f) for f in AUDIT_FIELDS if f not in allow},
    }


def compare_payloads(old: dict, new: dict, allow=frozenset()) -> list[str]:
    """Differences between two payloads in course fields and audit counts, except fields in `allow`."""
    a, b = course_fields(old, allow), course_fields(new, allow)''')

replace_once('''def evidence_cell_ids(source: Path) -> list[str]:''', '''def _course_key(course: dict) -> tuple:
    source = course.get("_source") or {}
    return (source.get("table_index"), source.get("row_index"), source.get("column_group"))


def _dig(course: dict, dotted: str):
    value = course
    for part in dotted.split("."):
        value = value.get(part) if isinstance(value, dict) else None
    return value


def field_changes(old: dict, new: dict) -> list[dict]:
    """Every changed field of every course, matched by table, row and column group (not by position,
    so a course the new parser finds or loses shows as added or removed, not as a shifted list)."""
    before = {_course_key(c): c for c in old["courses"]}
    after = {_course_key(c): c for c in new["courses"]}
    rows = []
    for key in sorted(before.keys() | after.keys(), key=str):
        code = (after.get(key) or before.get(key)).get("course_code")
        if key not in after or key not in before:
            rows.append({"key": key, "code": code, "field": "(course)",
                         "old": "present" if key in before else "absent", "new": "present" if key in after else "absent"})
            continue
        for name in (*COURSE_FIELDS, *REPORT_ONLY_FIELDS):
            x, y = _dig(before[key], name), _dig(after[key], name)
            if x != y:
                rows.append({"key": key, "code": code, "field": name, "old": x, "new": y})
    return rows


def write_report(path: Path, rows: list[dict]) -> None:
    """CSV of changes: input, table, row, column group, code, field, old, new (values as JSON)."""
    import csv

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["input", "table", "row", "column_group", "code", "field", "old", "new"])
        for r in rows:
            table, row, group = r["key"]
            writer.writerow([r["input"], table, row, group, r["code"], r["field"],
                             json.dumps(r["old"], ensure_ascii=False), json.dumps(r["new"], ensure_ascii=False)])


def flag_counts(payload: dict) -> dict:
    """Error and warn flags by kind from the section verifier (JSON only, no PDF)."""
    sys.path.insert(0, str(REPO))
    from backend.bintanong_tools.prospectus_extractor.verify import verify_candidate

    return verify_candidate(payload).counts()


def flag_rises(old: dict, new: dict) -> dict:
    """{kind: (before, after)} for every verifier flag kind that rose from the old to the new payload."""
    a, b = flag_counts(old), flag_counts(new)
    return {k: (a.get(k, 0), b.get(k, 0)) for k in sorted(a.keys() | b.keys()) if b.get(k, 0) > a.get(k, 0)}


def evidence_cell_ids(source: Path) -> list[str]:''')

replace_once('''def compare_runs(old_dir: Path, new_dir: Path, check_markup: bool) -> int:
    folders = sorted(p for p in old_dir.iterdir() if p.is_dir())
    if not folders:
        sys.exit(f"no run folders under {old_dir}")
    failures, gaps, unplaced, largest = 0, 0, 0, 0''', '''def compare_runs(old_dir: Path, new_dir: Path, check_markup: bool, allow=frozenset(), flags=False, report: Path | None = None) -> int:
    folders = sorted(p for p in old_dir.iterdir() if p.is_dir())
    if not folders:
        sys.exit(f"no run folders under {old_dir}")
    failures, gaps, unplaced, largest = 0, 0, 0, 0
    changed_rows: list[dict] = []
    totals_old: dict = {}
    totals_new: dict = {}''')

replace_once('''                issues += compare_payloads(old_payload, new_payload)
''', '''                issues += compare_payloads(old_payload, new_payload, allow)
                changes = field_changes(old_payload, new_payload)
                changed_rows += [{**c, "input": old.name} for c in changes]
                if changes:
                    print(f"{old.name}   {len(changes)} field change(s): " + ", ".join(f"{k} {n}" for k, n in sorted(Counter(c["field"] for c in changes).items())))
                if flags:
                    for target, payload in ((totals_old, old_payload), (totals_new, new_payload)):
                        for kind, n in flag_counts(payload).items():
                            target[kind] = target.get(kind, 0) + n
                    rises = flag_rises(old_payload, new_payload)
                    if rises:
                        issues.append("verifier flags rose: " + ", ".join(f"{k} {a}->{b}" for k, (a, b) in rises.items()))
''')

replace_once('''    print(f"{len(folders) - failures}/{len(folders)} identical")''', '''    print(f"{len(folders) - failures}/{len(folders)} identical" + (" (allowed changes: " + ", ".join(sorted(allow)) + ")" if allow else ""))
    if report is not None:
        write_report(report, changed_rows)
        print(f"{len(changed_rows)} changed fields written to {report}")
    if flags:
        print("verifier flags (error and warn), all inputs: old " + (", ".join(f"{k} {n}" for k, n in sorted(totals_old.items())) or "none"))
        print("verifier flags (error and warn), all inputs: new " + (", ".join(f"{k} {n}" for k, n in sorted(totals_new.items())) or "none"))''')

replace_once('''    cli.add_argument("--no-markup-check", action="store_true")''', '''    cli.add_argument("--no-markup-check", action="store_true")
    cli.add_argument("--allow-change", default="", help="comma-separated fields whose change is intended (course or audit fields)")
    cli.add_argument("--report", type=Path, help="CSV of every changed course field")
    cli.add_argument("--flags", action="store_true", help="also compare section-verifier flag counts; a rise fails")''')

replace_once('''    return compare_runs(args.work / "old", args.work / "new", not args.no_markup_check)''', '''    allow = frozenset(f for f in args.allow_change.split(",") if f)
    return compare_runs(args.work / "old", args.work / "new", not args.no_markup_check, allow, args.flags, args.report)''')
PATH.write_text(text, encoding="utf-8", newline="\n")
print("compare script edited")
```

```powershell
uv run --project backend --extra tools --extra dev python "$env:TEMP\edit_compare.py"
uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_course_compare.py
uv run --project backend --extra tools --extra dev --with fastapi==0.141.1 python -m pytest -q tests
```

Expected: `14 passed`; full suite `202 passed`, 13 subtests passed. The default behavior (no new option) is unchanged: strict on every course and audit field.

- [ ] **Step 3: Commit the comparer and record the parser base**

```powershell
git add tests/test_prospectus_course_compare.py scripts/prospectus_course_compare.py
git commit -m "test: let the course comparer list every changed field, allow named fields and compare verifier flags" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
git rev-parse HEAD
```

Record the printed hash as `$PARSER_BASE`: the old side of the 44-input run is the extractor at this commit.

- [ ] **Step 4: Write the failing parser tests**

`tests/test_prospectus_banner_split.py`:

```python
"""A code or title cell that starts with printed banner phrases is split into banner and course."""

import pytest

from backend.bintanong_tools.prospectus_extractor.parse import parse_curriculum_evidence
from backend.bintanong_tools.prospectus_extractor.selftest import cs_fixture_grid, fixture_document
from backend.bintanong_tools.prospectus_extractor.sections import _row_field_candidates
from backend.bintanong_tools.prospectus_extractor.evidence import normalized_table_from_grid
from backend.bintanong_tools.prospectus_extractor.layout import ColumnGroup

GROUP = ColumnGroup(0, 0, 1, 2, 3)


def fields(code, title):
    grid = [["Course Code", "Course Title", "Units", "Prerequisites"], [code, title, "3", ""]]
    out = _row_field_candidates(normalized_table_from_grid(grid), 1, GROUP, [GROUP])
    return out["code"].value, out["title"].value


@pytest.mark.parametrize("code,title,expected", [
    # split: more than one banner word at the start of the cell
    ("CS 1", "FIRST YEAR FIRST SEMESTER Discrete Structures 1", ("CS 1", "Discrete Structures 1")),
    ("CS 1", "FIRST SEMESTER SECOND SEMESTER Discrete Structures 1", ("CS 1", "Discrete Structures 1")),
    ("FIRST YEAR FIRST SEMESTER CS 1", "Discrete Structures 1", ("CS 1", "Discrete Structures 1")),
    ("FIRST SEMESTER SECOND SEMESTER CS 1", "Discrete Structures 1", ("CS 1", "Discrete Structures 1")),
    # unchanged by this step: handled before, or not a leading banner
    ("CS 1", "FIRST SEMESTER Discrete Structures 1 1", ("CS 1", "Discrete Structures 1 1")),
    ("FIRST SEMESTER CS 1", "Discrete Structures 1", ("CS 1", "Discrete Structures 1")),
    ("CS 1", "FIRST Ethics", ("CS 1", "FIRST Ethics")),                 # a lone ordinal: footnotes.clean_title
    ("CS 1", "Second Language Acquisition", ("CS 1", "Second Language Acquisition")),
    ("CS 1", "First Aid", ("CS 1", "First Aid")),
    ("CS 1", "EE FIRST SEMESTER Environmental Engineering", ("CS 1", "EE FIRST SEMESTER Environmental Engineering")),
    ("CS 1", "Discrete Structures SECOND YEAR", ("CS 1", "Discrete Structures SECOND YEAR")),
    ("CS 1", "FIRST YEAR", ("CS 1", "FIRST YEAR")),                     # nothing left after the banner: leave it
])
def test_row_fields_after_the_banner_split(code, title, expected):
    assert fields(code, title) == expected


def parse(title_one, title_two):
    grid = cs_fixture_grid()
    grid[3][1], grid[3][5] = title_one, title_two
    return {c["course_code"]: c for c in parse_curriculum_evidence(fixture_document(grid, [("title", "BACHELOR OF SCIENCE IN TESTING")])).courses}


def test_a_glued_year_and_semester_banner_no_longer_corrupts_the_title():
    courses = parse("FIRST YEAR FIRST SEMESTER Discrete Structures 1", "SECOND SEMESTER Discrete Structures 2")
    # before: "SEMESTER Discrete Structures" and "Discrete Structures" (a series number taken for a footnote marker)
    assert courses["CS 1"]["course_title"] == "Discrete Structures 1"
    assert courses["CS 2"]["course_title"] == "Discrete Structures 2"
    assert (courses["CS 1"]["year_level"], courses["CS 1"]["semester"]) == ("1st Year", "1st Semester")
    assert (courses["CS 2"]["year_level"], courses["CS 2"]["semester"]) == ("1st Year", "2nd Semester")


def test_the_banner_is_recorded_from_its_cell_and_the_cell_stays_in_the_provenance():
    course = parse("FIRST YEAR FIRST SEMESTER Discrete Structures 1", "Discrete Structures 2 2")["CS 1"]
    prov = course["provenance"]
    (fragment,) = prov["discarded_fragments"]
    assert fragment["text"] == "FIRST YEAR FIRST SEMESTER" and fragment["reason"].startswith("banner phrase")
    assert fragment["source_cell_ids"][0] in prov["source_cell_ids"]            # same cell: course text and banner
    assert prov["resolution_method"] == "deterministic_repair"
    assert prov["valid"] is True


def test_a_course_without_banner_text_keeps_its_deterministic_provenance():
    course = parse("Discrete Structures 1 1", "Discrete Structures 2 2")["CC 1/L"]
    assert course["provenance"]["resolution_method"] == "deterministic"
    assert "discarded_fragments" not in course["provenance"]


def test_one_cell_holding_banner_code_and_title_keeps_its_inline_handling():
    # ABComm t0-c62: banner, code and title share the code cell and the units sit in the title column.
    # Splitting the single banner first would send the rest down the fused-code branch and append
    # the units digit to the title ("Science, Technology, & Society 3").
    grid = [["Course Code", "Course Title", "Units", "Prerequisites"],
            ["FIRST SEMESTER GE-STS Science, Technology, & Society", "3", "", ""]]
    out = _row_field_candidates(normalized_table_from_grid(grid), 1, GROUP, [GROUP])
    assert (out["code"].value, out["title"].value, out["units"].value) == ("GE-STS", "Science, Technology, & Society", "3")
```

```powershell
uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_banner_split.py
```

Expected: `6 failed, 10 passed`. Failing: the four split cases (`('CS 1', 'FIRST YEAR FIRST SEMESTER Discrete Structures 1')` and the three like it), `test_a_glued_year_and_semester_banner_no_longer_corrupts_the_title` (`'SEMESTER Discrete Structures' != 'Discrete Structures 1'`) and `test_the_banner_is_recorded_from_its_cell_and_the_cell_stays_in_the_provenance` (`KeyError: 'discarded_fragments'`). The unchanged cases and the ABComm regression pass already: they pin behavior this task must not change.

- [ ] **Step 5: Implement the split**

Save as `$env:TEMP\edit_sections.py` and run it from the repo root:

```python
"""Apply the banner-split edits to prospectus_extractor/sections.py. Run from the repo root.

Each edit replaces one exact text that must occur exactly once; the script stops otherwise.
"""
from pathlib import Path

PATH = Path("backend/bintanong_tools/prospectus_extractor/sections.py")
text = PATH.read_text(encoding="utf-8")


def replace_once(old: str, new: str) -> None:
    global text
    if text.count(old) != 1:
        raise SystemExit(f"expected exactly one match, found {text.count(old)}: {old[:70]!r}")
    text = text.replace(old, new)


# 1. imports
replace_once(
    "from .text import INLINE_SEMESTER_PREFIX, YEAR_ORDER, clean_str, is_banner_text, match_semester_labels, match_year_label, norm_key, term_index",
    "from .text import INLINE_SEMESTER_PREFIX, YEAR_ORDER, clean_str, has_banner_text, is_banner_text, leading_banner, match_semester_labels, match_year_label, norm_key, term_index",
)

# 2. the split, before _row_field_candidates
replace_once(
    "def _row_field_candidates(\n",
    '''def _split_banner_prefix(field_value: FieldCandidate | None, is_code: bool = False) -> FieldCandidate | None:
    """A code or title cell that starts with printed banner phrases ("FIRST YEAR FIRST SEMESTER
    Discrete Structures 1") is banner plus course text. Keep the course text with the cell's
    evidence ids; the banner is recorded from the cell by _candidate_to_raw_course. Only
    multi-word banners are split: a lone ordinal or SEMESTER is handled below. A code cell that
    starts with one plain semester banner keeps the inline-heading branch below, which also decides
    how the rest divides into code and title (ABComm t0-c62: banner, code and title in one cell)."""
    if field_value is None:
        return None
    banner, rest = leading_banner(field_value.value)
    if len(banner.split()) < 2 or not rest:
        return field_value
    if is_code:
        inline = INLINE_SEMESTER_PREFIX.match(field_value.value)
        if inline and not has_banner_text(inline.group(1)):
            return field_value
    return FieldCandidate(rest, list(field_value.evidence_cell_ids), [*field_value.confidence_flags, "banner_split"])


def _row_field_candidates(
''',
)

# 3. call it right after the split-year handling
replace_once(
    '''    code = fields["code"]
    if code:
        code.value = re.sub(r"\\s*/\\s*", "/", code.value)
''',
    '''    fields["code"], fields["title"] = _split_banner_prefix(fields["code"], True), _split_banner_prefix(fields["title"])
    code = fields["code"]
    if code:
        code.value = re.sub(r"\\s*/\\s*", "/", code.value)
''',
)

# 4. record the banner when the raw course is built
replace_once(
    "def _candidate_to_raw_course(\n",
    '''BANNER_FRAGMENT_REASON = "banner phrase printed in the same cell as the course text"


def _banner_fragments(candidate: CourseCandidate, evidence: ProspectusEvidence) -> list[dict[str, Any]]:
    """Banner text that shares a code or title cell with the course. The cell stays in the course's
    provenance; this records what part of it is banner rather than dropping it silently."""
    cells = evidence.all_cells()
    found: list[dict[str, Any]] = []
    for named in (candidate.code, candidate.title):
        for cell_id in named.evidence_cell_ids if named else []:
            cell = cells.get(cell_id)
            if cell is None or any(cell_id in item["source_cell_ids"] for item in found):
                continue
            banner, rest = leading_banner(cell.text)
            if len(banner.split()) >= 2 and rest:
                found.append({"text": banner, "source_cell_ids": [cell_id], "reason": BANNER_FRAGMENT_REASON})
    return found


def _candidate_to_raw_course(
''',
)
replace_once(
    "    candidate.discarded_fragments.extend(discarded)\n    code = canonicalize_course_code(code_raw, title)",
    "    discarded = discarded + _banner_fragments(candidate, evidence)\n    candidate.discarded_fragments.extend(discarded)\n    code = canonicalize_course_code(code_raw, title)",
)
PATH.write_text(text, encoding="utf-8", newline="\n")
print("sections.py edited")
```

```powershell
uv run --project backend --extra tools --extra dev python "$env:TEMP\edit_sections.py"
uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_banner_split.py tests/test_prospectus_parser.py
uv run --project backend --extra tools --extra dev python -m backend.bintanong_tools.prospectus_extractor --self-test
uv run --project backend --extra tools --extra dev --with fastapi==0.141.1 python -m pytest -q tests
```

Expected: `20 passed, 13 subtests passed`; `80/80`; full suite `218 passed`, 13 subtests passed.

- [ ] **Step 6: Run the 44-input comparer detached and read it**

Each side runs the extractor on the 44 cached Docling JSON files. The prototype measured about 9 seconds per input, but background tool calls die at 10 minutes and a slower machine can take far longer, so launch detached and poll a log.

```powershell
$GOLDEN = 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\docling_jsonified_output\task2b_standing_isolated_2026-09-29'
$MAP = 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\PalSU Undergraduate Prospectus Website Dump\Tiniguiban - Main\palsu_main_undergrad_program_college_meaning.md'
$PARSER_BASE = '<hash recorded in step 3>'
$run = "$env:TEMP\b2-compare"; New-Item -ItemType Directory -Force $run | Out-Null
$cmd = "uv run --project backend --extra tools --extra dev python scripts/prospectus_course_compare.py --golden '$GOLDEN' --work '$run\work' --base-ref $PARSER_BASE --semantic-doc '$MAP' --jobs 2 --allow-change course_title --report '$run\changes.csv' --flags"
Start-Process pwsh -ArgumentList '-NoProfile','-Command',$cmd -WorkingDirectory (Get-Location).Path -RedirectStandardOutput "$run\compare.log" -RedirectStandardError "$run\compare.err" -WindowStyle Hidden
```

Poll `Get-Content "$run\compare.log" -Tail 5` until it ends with the verifier lines, then read the whole log and `$run\changes.csv`. Expected, as in the prototype:

```
28   5 field change(s): course_title 1, provenance.discarded_fragments 2, provenance.resolution_method 2
44/44 identical (allowed changes: course_title)
109 changed fields written to ...\changes.csv
verifier flags (error and warn), all inputs: old audit_anomaly 69, banner_leak 3, duplicate_course 33, no_term 85, prereq_order 22, unclaimed_code 146, unit_total 73
verifier flags (error and warn), all inputs: new audit_anomaly 69, banner_leak 2, duplicate_course 33, no_term 85, prereq_order 22, unclaimed_code 146, unit_total 73
```

(plus one `NN   N field change(s)` line for each of the other inputs whose courses gain a banner fragment, and the markup line). The CSV holds exactly one `course_title` row (input `28`, code `AS 1`) and 108 provenance rows (54 `resolution_method`, 54 `discarded_fragments`).

**Gate:** exit code 0; the only course field that changed is `course_title`, on the rows in the CSV; no verifier flag count rose; the markup cell-id check still passes for every input. If any other field changed or a flag count rose, stop, find out why, and do not commit the parser change. Clean up: `git worktree remove --force "$env:TEMP\bintanong-compare-$PARSER_BASE"` (the comparer names the old-side folder after the ref it was given).

- [ ] **Step 7: Record the field-by-field result and commit**

Copy the exact changed-field rows (the one `course_title` row and the counts of provenance rows) and the before/after flag totals into the progress file under a heading "Task 13 result". They are the report the user reads before deciding to merge.

```powershell
git add tests/test_prospectus_banner_split.py backend/bintanong_tools/prospectus_extractor/sections.py plans/plan_current_progress/extractor_split_progress.md
git commit -m "feat: split banner phrases from code and title cells and record them in the provenance" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 14: Decision record, final checks, Codex gate, hand off

**Files:**
- Create: `docs/decisions/prospectus-section-fixer.md`
- Modify: `plans/plan_current_progress/extractor_split_progress.md`

- [ ] **Step 1: Write the decision record**

`docs/decisions/prospectus-section-fixer.md` must state, in plain sentences: what the verifier, sheet, ledger and corrected candidate are and that a decision means a person looked, not that anyone approved a curriculum; the ledger line format (the fields listed in Task 6, `ledger_version` `prospectus-decision-ledger-v1`) as the contract the later GUI reads and appends; D1 to D9 as taken (note any that changed during execution, and whether Task 13 ran); the health vocabulary and thresholds; that nothing in the sheet fixes a parser-level failure such as BSE-Innovation-and-Tech (D8); where files live and why (D2) and that the guard needs `git`; the facts from "What the real data says" with their dates; the measured results of Tasks 5, 11, 12 and 13; that `parser_sha256` in the isolated-batch manifest changed because new modules joined the package (extraction itself did not, apart from Task 13); the interface for Phase C (`ledger.content_review_state`); and these known limitations:

- A wrapped title the parser cut short (BS Architecture `AD-2/L`: `Architectural Design 2-Creative Design and`, printed `... and Fundamentals`) is not flagged, because the stored text is found in the PDF as a prefix.
- A proposal can differ from the stored title only by apostrophe style (`'` in Docling, `’` in the PDF text).
- `title_from_pdf` needs the PDF text layer to read row by row; a PDF whose text is column-interleaved yields no unique row and no proposal. Cached Docling JSON alone gives no PDF checks at all (the sheet says so).
- Printed codes found only in the PDF text (elective lists in footnotes) are listed in `SU` and can be decided, but do not gate `reviewed` (D5).
- The corrected candidate is not re-audited; `audit`, `elective_tracks`, `prolog`, `rag` and `quality_report` in it are stale and named so.
- Section and row ids (`S3-04`) come from the candidate's content; after any parser change a sheet is stale (the candidate hash in its header will not match) and `apply` refuses it.
- OCR: the verifier reads whatever candidate and text pages it is given; `PdfPage` can come from an OCR engine as the audit script's docstring says. Nothing here assumes a born-digital text layer beyond the optional PDF checks.

- [ ] **Step 2: Run everything one last time**

Full suite (expected `218 passed`, 13 subtests passed; `198 passed` if Task 13 was deferred), self-test (`80/80`), and `git status --short` (only the files this phase lists, plus the two files you must leave alone). Confirm the Phase C note is still in `plans/2026-10-03-prospectus-phase-c-status-separation.md`.

- [ ] **Step 3: Codex gate (read-only, detached, about 15 minutes)**

```powershell
$run = "$env:TEMP\b2-codex"; New-Item -ItemType Directory -Force $run | Out-Null
@'
Review branch feat/prospectus-phase-b2-section-fixer against dev in this repo. Read backend/bintanong_tools/prospectus_extractor/verify.py, fixes.py, placement.py, ledger.py, sheet.py, fixer_cli.py, course_checks.py, the new helpers in text.py, the banner split in sections.py (_split_banner_prefix, _banner_fragments), scripts/prospectus_course_compare.py and the tests/test_prospectus_*.py files for these modules. Claims to attack: (1) the ledger is append-only: no code path rewrites or deletes an existing line, and a damaged ledger stops an append; (2) an entry recorded against a different pdf_sha256 never changes a corrected candidate and is reported; (3) apply writes nothing unless the whole sheet validates, and a sheet whose fixed text was edited or that came from another candidate is refused; (4) a fix proposal never contains text that is not already in the candidate cells or the PDF text layer, and title_from_pdf never proposes when two PDF rows fit; (5) the corrected candidate is byte-identical for the same inputs and the input payload is never mutated; (6) assert_outside_git cannot be bypassed by a relative path, a symlink or a case difference on Windows; (7) section health and the prospectus label follow the rules in the plan; (8) the banner split changes extracted values only where the plan says (read _split_banner_prefix against the ABComm t0-c62 case and footnotes.clean_title) and no other module's public name collides with the legacy shim's re-exports. Look for escaping bugs in the sheet table (pipes, backslashes, trailing backslash), off-by-one errors in the region and unplaced-code logic, wrong frames (table cells are top-left, PDF characters are y-up), and tests that cannot fail. Do not modify files. Report findings with file and line, and say which you could not confirm.
'@ | Set-Content "$run\prompt.txt" -Encoding utf8
Start-Process pwsh -ArgumentList '-NoProfile','-Command',"codex exec --sandbox read-only -o '$run\codex-report.md' (Get-Content '$run\prompt.txt' -Raw)" -WorkingDirectory (Get-Location).Path -RedirectStandardOutput "$run\codex.log" -RedirectStandardError "$run\codex.err" -WindowStyle Hidden
```

Poll `Get-Content "$run\codex.log" -Tail 5` until the process ends, then read `codex-report.md`. If Codex is rate-limited or errors, record that in the progress file and continue; do not block. Fix each confirmed finding with a failing test first; note and skip unconfirmed ones.

- [ ] **Step 4: Update the progress file and commit**

Set every Phase B2 row to done with the real evidence, add the Codex findings and the line: "Phase B2 complete on branch feat/prospectus-phase-b2-section-fixer; not merged, not pushed; next: user decides on merge, then Phase C (its `content_review` reads `ledger.content_review_state` when a ledger is passed)."

```powershell
git add docs/decisions/prospectus-section-fixer.md plans/plan_current_progress/extractor_split_progress.md
git commit -m "docs: record the year/semester verifier and fixer with its trial and regression evidence" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

Do not merge into `dev` and do not push; ask the user (superpowers:finishing-a-development-branch).

**Phase B2 gate:** tests of Tasks 2 to 11 green (suite 198) and, if Task 13 ran, 218 with the 44-input comparer exit 0 and exactly the reported field changes; self-test 80/80; the real-data numbers of Tasks 5 and 11 reproduced; the trial review done and recorded; ledger and sheets stay outside Git; Codex findings resolved or recorded; decision record written.

---

## Self-review

**Spec coverage (the user's decisions H1 to H6 and the brief):**
- H1, ledger never edits the candidate, append-only entries with reviewer, timestamp, reason, `pdf_sha256`, locator by source cell ids plus field, old and new value or disposition, fix id; corrected JSON rebuilt deterministically; other `pdf_sha256` inapplicable, reported, never applied; conform to master §7.1 and draft Task 5: Tasks 6 and 7 (tests for each property).
- H2, review sheet per prospectus, one table per year x semester in printed order, flags and proposal per row, section health line and confirm field, `verify`/`apply` reading the edited sheet, nothing written for unchanged rows unless confirmed, GUI-ready ledger, no GUI built, format recommended with reasons: D1, Tasks 8, 9, 10.
- H3, six checks: banner text (Task 3, `banner_leak`), totals (Task 3, `unit_total` plus the empty-section regex), code and title not in the PDF text with "not checked" when only cached JSON exists (Task 5, `pdf_checked`, the sheet header and the sheet's note), two terms or none (Task 3), prerequisite in the same or a later term (Task 3), unclaimed printed codes attached to a section when determinable (Task 5, `placement.py`).
- H4, proposals per flag, accept per row or per class per section, nothing reviewed without a human decision, nothing invented: Tasks 4 and 9.
- H5, parser banner split last, test first, gated by the 44-input comparer listing every changed field and the fixer's flag counts: Task 13.
- H6, Phase B2 before Phase C, minimal interface for `content_review`, one-line note in the Phase C start check: "Interface Phase C needs", Task 6, and the note already in the Phase C plan (verified in Tasks 1 and 14).
- Master §16.1 (no hosted reviewer UI, local file only), reviewer from flag or `git config user.name`, storage outside Git decided and justified (D2), `assert_outside_git`: Task 10.
- The audit script's checks are reused, moved into the package with tests: Task 2.
- End to end on three prospectuses of different health, sheets for the user, hand-off for a trial review before the parser task: Tasks 11 and 12.
- Brief rules: course fields unchanged except Task 13 (the 44-input comparer proves it there; Tasks 2 to 12 touch no extractor module except adding text helpers); `SCHEMA_VERSION` unchanged with the reason stated; start check first; Codex gate last; progress file after each task; cross-platform (pathlib, `newline="\n"`, UTF-8); tests first with a stated red outcome; no institution PDF in Git (fixtures hold cell texts and one short text excerpt); OCR not planned, room kept (the verifier takes any `PdfPage` source).

**Placeholder scan:** no step says "add validation" or "handle edge cases" without code; every code step shows the code or an exact replace-once script; the only angle-bracket placeholders are values the executor records (a commit hash, a reviewer name, a folder path in the hand-over text).

**Type and name consistency:** `Flag`, `Row`, `Section`, `Verification`, `verify_candidate(payload, pdf_pages=None)`, `own_role_cells`, `Fix(kind, field, old, new, note, fix_id)`, `propose_fixes(course, role_cells, *, title_not_in_pdf, page_text, known_codes)`, `placement.unclaimed_items/attach/locate_in_page`, `ledger.make_entry/append_entries/read_entries/latest_by_field/content_review_state/materialise/write_corrected`, `sheet.render_sheet/parse_sheet/check_against/parse_decision/build_entries`, `fixer_cli.fixer_main`, field names `course_code`, `course_title`, `term` (plus the wildcard `row` and `unclaimed`), dispositions `accepted | corrected | unresolved`, health words `clean | review | broken` (sections) and `clean | warnings_only | mixed | broken` (prospectus) are used identically in every task and test. The sheet's row ids (`S2-04`, `SU-U1`) and the ledger's cell-id locators are the two ways to name a course, and `apply` is the only code that maps one to the other.

**Riskiest task:** Task 5 (PDF-derived proposals and region placement depend on the text layer and on box frames, and the proposal quality is only proven on real PDFs), then Task 13 (the only task that changes extracted values; guarded by the comparer and by the ABComm regression test found in the prototype).
