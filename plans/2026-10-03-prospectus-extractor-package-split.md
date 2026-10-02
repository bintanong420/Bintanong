# Prospectus Extractor Package Split Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task, with superpowers:test-driven-development inside each task. Steps use checkbox (`- [ ]`) syntax for tracking. Update `plans/plan_current_progress/extractor_split_progress.md` after every task commit.

**Status:** User-approved 3 October 2026 (answers to the grilling round are recorded under "Decisions"). Part of the parallel, review-only prospectus workstream. It does not advance `plans/INDEX.md`, and it does not approve any curriculum, RAG, or Prolog release.

**Goal:** Turn the 6,320-line `bintanong_prospectus_jsonifier.py` into the importable, cross-platform package `backend/bintanong_tools/prospectus_extractor/` with provably identical behavior (Phase A), then add the pending features as separate test-first phases (B–F).

**Architecture:** Phase A is a *scripted* move, not a hand rewrite. A one-off splitter slices the committed monolith by line range into 26 modules and generates their imports. Two independent proofs gate it: an AST test showing every top-level definition is unchanged, and a golden run showing identical outputs on the 44 cached Docling JSON files. The old file remains as a thin shim so every recorded command still works.

**Tech stack:** Python 3.13, stdlib `ast`/`pathlib`/`subprocess`, pytest 9, `uv`. No new dependency.

**Base commit:** `7591264` on `dev`. Monolith SHA-256 `8ea75006a4c588902738c3a31096d44aa453a2fdfdeffae8750bf681eae3164d` (the parser of the last 44-path run).

**Branch:** `refactor/prospectus-extractor-package` (already created from `dev`). Leave the dirty `.gitignore` and the untracked `plans/CODEX_HANDOFF_prospectus_extractor_phase2_2026-09-26.md` alone; never `git add -A`.

---

## Decisions (from the user, 3 October 2026)

| # | Decision |
| --- | --- |
| Q1 | Split first, **1:1**, then the pending plan features as separate TDD tasks. |
| Q2 | New package `backend/bintanong_tools/prospectus_extractor/`; old file stays as a shim. Must run on Windows, Linux, and later macOS. |
| Q3 | Flat modules following the monolith's own section headers; mirror the repo's existing conventions. |
| Q4 | Legacy and compatibility code moves to its own file for documentation; nothing is deleted. |
| Q5 | The 80-check self-test moves as-is to `selftest.py`; `--self-test` stays; one pytest asserts 80/80. |
| Q6 | The markup output must mirror how a PalSU prospectus looks on the page (Phase B). |
| Q7 | Isolated branch. |

Execution: implementer and reviewer subagents use the `sonnet` model (Sonnet 5; there is no "Sonnet 5.5" model ID). An independent Codex review (`codex exec`, CLI 0.157.0 is installed) runs at each gate marked **Codex gate**. If Codex is rate-limited or errors, record that in the progress file and continue; do not block.

## What "1:1" means here, and the two forced exceptions

Every top-level function, class, and constant of the monolith must appear in exactly one package module with an identical AST. Comments may be dropped only for the `# ====` section banners. Outputs on the 44 cached inputs must be identical outside fields that already differ between two runs of the old code.

Moving the file forces exactly two differences. Both are listed for review and nothing else is allowed:

1. **`ensure_docling_env()` re-launch command.** The monolith re-executes `Path(__file__)`, which after the move would be `docling_env.py`, not the CLI. New body re-runs the original command line: `subprocess.call([str(venv_py), *sys.orig_argv[1:]], env=env)`. Same intent, works for script, `-m`, and directory invocation on every OS.
2. **`find_default_output_root()` location.** Its text is unchanged, but `Path(__file__).parent` now resolves to `prospectus_extractor/docling_jsonified_output` instead of `bintanong_jsonifer_prolog/docling_jsonified_output`. It is only the fallback when `-o` is omitted. A `.gitignore` line is added for it in Task 6.

`DATA_ROOT` (`Path(__file__).resolve().parent.parent`) resolves to `backend/bintanong_tools` before and after, so the default source and semantic-map paths are unchanged.

## Alignment check against earlier plans

Checked: `master_implementation_plan_original_long.md` §§6, 7, 11, 20; `phase2_jsonifier_integration_plan.md`; `2026-09-26-prospectus-phase2-implementation-draft.md`; `prospectus_extractor_recovery_2026-09-29.md`; `plan_current_progress/current_progress.md`; `INDEX.md`.

| Finding | Where it comes from | What this plan does |
| --- | --- | --- |
| "Avoid a broad rewrite of the 6,230-line module." | Phase 2 integration plan, work order 5 | Phase A moves code without editing it and proves it. Not a rewrite. |
| "Export a small public API and wrap the existing 80-check suite in pytest." | Same | Tasks 5 and 6. |
| Master §20 assigns Docling parsing to `backend/app/ingestion/`; the approved workstream draft keeps the extractor under `backend/bintanong_tools/` with a thin adapter. | Master §20 vs draft "File ownership" | Follow the newer, user-approved draft. `app/ingestion/` can import the package later; noted as an open item, not changed here. |
| The module docstring says an ERROR audit emits "zero production Prolog or RAG", but the detailed JSON still embeds candidate Prolog and RAG objects when blocked. | Recovery report, remaining defect 4 | Not touched in Phase A (1:1). Fixed in Phase C. |
| `warn` audit becomes `promotion_status="VERIFIED"`; campus is hardcoded to `Tiniguiban - Main`. | Integration plan priorities 1–2; draft Task 3 | Phase C. |
| Cache fingerprint omits the PDF hash; `process_prospectus()` deletes old outputs before converting. | Integration plan priority 4; draft Task 4 | Phase D. |
| Course chunk IDs are `<code>::course`, so two editions collide; chunks lack page and cell IDs. | Integration plan priority 3; master §7.2; draft Task 6 | Phase E. |
| Default paths point at an in-repo dataset location that does not exist; docstring still names `palsu_prospectus_extractor.py` and says "not adjusted to this codebase yet". | Recovery report, remaining defect 5 | Docstring corrected in Task 5. Default paths untouched (1:1); replaced by explicit arguments in Phase F. |
| OCR is off; scanned prospectuses are unsupported. | Master §7.1 step 3, integration plan priority 5 | Unchanged. Stays documented as unsupported. |
| Task 2 parser repairs are partial (BSCS standing ownership, Social Work spill, Architecture titles). | Recovery report | Out of scope. The split must not change any of these candidate fields. |
| Human review GUI (draft Task 5) and the 39-PDF reference set (draft Task 8). | Draft | Unchanged and still owed. Phase B's markup twin is designed to be the GUI's "reconstructed table" view. |

Nothing in this plan contradicts the developer's recorded intent. The one place the earlier documents disagree with each other is the package location (row 3).

## File structure after Phase A

All under `backend/bintanong_tools/prospectus_extractor/`. Line ranges refer to the monolith at `7591264`. Modules are listed in import order; a module imports only from modules above it.

| Module | Monolith lines | Responsibility |
| --- | --- | --- |
| `common.py` | 1–101 (non-import statements) | Schema versions; optional Rich console objects. |
| `docling_env.py` | 102–333 | Lazy Docling import, version guard, CUDA check, converter cache. |
| `text.py` | 334–446 | Text cleaning, code keys, year and semester label matching. |
| `footnotes.py` | 447–593 | Footnote marker detection and stripping. |
| `units.py` | 594–657 | Lecture/lab/total unit parsing. |
| `prerequisites.py` | 658–859 | Prerequisite tokenising, `CodeIndex`, resolution. |
| `grid.py` | 1304–1473, plus `MULTIPART_CODE`, `is_probable_course_code`, `_two_course_codes_in_cell` from 1612–1652 | Course-code recognition, total rows, `GridParseResult`, table year contexts. |
| `layout.py` | 860–1128 | Column-group and header detection. |
| `evidence.py` | 1129–1303 | `SourceBBox`, `NormalizedCell`, `NormalizedTable`, `ProspectusEvidence`. |
| `sections.py` | 1482–2818 (minus the three names moved to `grid.py`) | Structural tokenizer, curriculum sections, row assembly, provenance. The parser core; kept whole. |
| `repair.py` | 2819–3054 | Evidence-constrained semantic repair validation. |
| `parse.py` | 3055–3198 | `parse_curriculum_evidence`, `evidence_from_grids`, `parse_curriculum_grids`. |
| `legacy.py` | 1474–1481 | Deprecated `_parse_curriculum_grids_legacy`, kept for documentation (Q4). |
| `courses.py` | 3199–3363 | Course finalisation, classification, elective tracks. |
| `metadata.py` | 3364–3509 | Program, college, school-year metadata. |
| `audit.py` | 3510–3804 | Prerequisite cycles and `build_audit`. |
| `views.py` | 3805–3879 | Term tree, prerequisite edges, review CSV. |
| `prolog.py` | 3880–4058 | Candidate Prolog knowledge base. |
| `rag.py` | 4059–4216, plus `build_hierarchical_rag_chunks` from 4494–4532 | Semantic and layout RAG chunks. |
| `paths.py` | 4217–4237, plus `find_default_input_root`, `find_default_output_root` from 4949–4954 | Default locations. |
| `loader.py` | 4238–4676 (minus the chunker moved to `rag.py`) | Docling-to-evidence adapter, cache, `load_document`, `dump_grid`. |
| `pipeline.py` | 4677–4937 | `build_payload`, `build_essentials`, `process_prospectus`. |
| `batch.py` | 4938–5179 (minus the two functions moved to `paths.py`) | In-process batch engine and manifest. |
| `selftest.py` | 5493–6203 | Fixtures and the 80 checks, unchanged. |
| `tui.py` | 5180–5492 | Interactive terminal UI. |
| `cli.py` | 6204–6319 | `build_cli`, `main`. |
| `__init__.py` | new | Docstring and the small public API. |
| `__main__.py` | new | `python -m …prospectus_extractor` and run-by-path entry. |

Also touched: `backend/bintanong_tools/bintanong_jsonifer_prolog/bintanong_prospectus_jsonifier.py` (becomes the shim), `backend/bintanong_tools/prospectus_batch.py`, `tests/test_prospectus_batch.py`, `.gitignore` (one added line only), `docs/decisions/prospectus-extractor-package.md`.

Temporary, removed in Task 7: `scripts/split_prospectus_extractor.py`, `scripts/prospectus_golden_check.py`, `tests/test_prospectus_split_equivalence.py`.

## Commands used throughout

Run from the repo root in PowerShell or any POSIX shell.

```
# Full suite (baseline: 26 passed, 13 subtests passed)
uv run --project backend --extra tools --extra dev --with fastapi==0.141.1 python -m pytest -q tests

# Self-test through the old entry point (baseline: 80/80)
uv run --project backend --extra tools --extra dev python backend/bintanong_tools/bintanong_jsonifer_prolog/bintanong_prospectus_jsonifier.py --self-test
```

`$GOLDEN` below is `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\docling_jsonified_output\task2b_standing_isolated_2026-09-29` (44 `*_docling.json` files, outside Git). `$MAP` is `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\PalSU Undergraduate Prospectus Website Dump\Tiniguiban - Main\palsu_main_undergrad_program_college_meaning.md`.

---

# Phase A — the 1:1 split

### Task 1: Record the baseline and write the failing 1:1 test

**Files:**
- Create: `tests/test_prospectus_split_equivalence.py`
- Create: `plans/plan_current_progress/extractor_split_progress.md` (already seeded; append results)

- [ ] **Step 1: Confirm the baseline before touching anything**

Run both commands from "Commands used throughout". Expected: `26 passed` (13 subtests) and `80/80`. Confirm the monolith hash:

```
uv run --project backend --no-sync python -c "import hashlib,pathlib;print(hashlib.sha256(pathlib.Path('backend/bintanong_tools/bintanong_jsonifer_prolog/bintanong_prospectus_jsonifier.py').read_bytes()).hexdigest())"
```

Expected: `8ea75006a4c588902738c3a31096d44aa453a2fdfdeffae8750bf681eae3164d`. If any of the three differs, stop and report; do not continue.

- [ ] **Step 2: Write the failing test**

```python
"""Phase A gate: the package is a 1:1 move of the monolith at BASE.

Every top-level definition of the old file must exist, AST-identical, in exactly
one package module, and the package must define nothing else. Delete this test
when Phase B starts changing behavior.
"""

from __future__ import annotations

import ast
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
BASE = "7591264"
MONOLITH = "backend/bintanong_tools/bintanong_jsonifer_prolog/bintanong_prospectus_jsonifier.py"
PACKAGE = REPO / "backend" / "bintanong_tools" / "prospectus_extractor"
HAND_WRITTEN = {"__init__.py", "__main__.py"}
# Definitions whose body was changed on purpose. Each one is explained in
# docs/decisions/prospectus-extractor-package.md.
DEVIATIONS = {"ensure_docling_env"}


def _definitions(source: str) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for node in ast.parse(source).body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            names = [node.name]
        elif isinstance(node, ast.Assign):
            names = [t.id for t in node.targets if isinstance(t, ast.Name)]
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names = [node.target.id]
        elif isinstance(node, ast.Try):
            names = ["<optional-rich-import>"]
        else:
            continue  # imports, docstring, `if` guards
        for name in names:
            found.setdefault(name, []).append(ast.dump(node))
    return found


def _monolith() -> dict[str, list[str]]:
    shown = subprocess.run(
        ["git", "show", f"{BASE}:{MONOLITH}"],
        cwd=REPO, capture_output=True, text=True, encoding="utf-8",
    )
    if shown.returncode != 0:
        pytest.skip(f"git cannot show {BASE}: {shown.stderr.strip()}")
    return _definitions(shown.stdout)


def _package() -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for path in sorted(PACKAGE.glob("*.py")):
        if path.name in HAND_WRITTEN:
            continue
        for name, dumps in _definitions(path.read_text(encoding="utf-8")).items():
            found.setdefault(name, []).extend(dumps)
    return found


def test_every_definition_moved_unchanged():
    old, new = _monolith(), _package()
    assert sorted(old) == sorted(new), {
        "missing": sorted(set(old) - set(new)),
        "extra": sorted(set(new) - set(old)),
    }
    changed = [
        name for name in old
        if name not in DEVIATIONS and sorted(old[name]) != sorted(new[name])
    ]
    assert changed == []


def test_deviations_are_real():
    old, new = _monolith(), _package()
    assert [name for name in DEVIATIONS if old[name] == new[name]] == []
```

- [ ] **Step 3: Run it and confirm it fails for the right reason**

Run: `uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_split_equivalence.py`
Expected: 2 failed. `test_every_definition_moved_unchanged` fails with every monolith name under `missing` and `extra` empty (the package directory does not exist yet). It must not be skipped; a skip means `git show 7591264:…` failed and needs fixing first.

- [ ] **Step 4: Commit**

```
git add tests/test_prospectus_split_equivalence.py plans/plan_current_progress/extractor_split_progress.md
git commit -m "test: add failing 1:1 gate for prospectus extractor split"
```

### Task 2: Write the golden-output check and capture the old behavior

**Files:**
- Create: `scripts/prospectus_golden_check.py`

- [ ] **Step 1: Write the script**

```python
#!/usr/bin/env python3
"""Phase A gate: old monolith and new package give the same outputs.

For every *_docling.json under GOLDEN the old code runs twice (A, B) and the new
package once (C). Anything that differs between A and B is run-to-run noise
(timestamps, output paths) and is ignored; everything else in C must equal A.

    python scripts/prospectus_golden_check.py GOLDEN WORK [--semantic-doc MAP] [--limit N]
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BASE = "7591264"
MONOLITH = "backend/bintanong_tools/bintanong_jsonifer_prolog/bintanong_prospectus_jsonifier.py"
# Same depth below backend/bintanong_tools as the original, so DATA_ROOT matches.
OLD_COPY = REPO / "backend" / "bintanong_tools" / "_golden_old" / "old_monolith.py"
NEW = ["-m", "backend.bintanong_tools.prospectus_extractor"]


def differing(a, b, path=()):
    """Paths at which two JSON-like values differ."""
    if type(a) is not type(b):
        return {path}
    if isinstance(a, dict):
        out = set()
        for key in set(a) | set(b):
            out |= differing(a.get(key), b.get(key), path + (key,)) if key in a and key in b else {path + (key,)}
        return out
    if isinstance(a, list):
        if len(a) != len(b):
            return {path}
        out = set()
        for index, (x, y) in enumerate(zip(a, b)):
            out |= differing(x, y, path + (index,))
        return out
    return set() if a == b else {path}


def load(path: Path):
    text = path.read_text(encoding="utf-8")
    return json.loads(text) if path.suffix == ".json" else text.splitlines()


def run(entry: list[str], source: Path, out_dir: Path, extra: list[str]) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, PYTHONHASHSEED="0", PYTHONIOENCODING="utf-8")
    command = [sys.executable, *entry, "-i", str(source), "-o", str(out_dir / "candidate.json"),
               "--export-all", "--device", "cpu", *extra]
    return subprocess.run(command, cwd=REPO, env=env, capture_output=True).returncode


def main() -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("golden", type=Path)
    cli.add_argument("work", type=Path)
    cli.add_argument("--semantic-doc", type=Path)
    cli.add_argument("--limit", type=int)
    args = cli.parse_args()

    OLD_COPY.parent.mkdir(parents=True, exist_ok=True)
    OLD_COPY.write_bytes(subprocess.run(["git", "show", f"{BASE}:{MONOLITH}"], cwd=REPO,
                                        check=True, capture_output=True).stdout)
    extra = ["--semantic-doc", str(args.semantic_doc)] if args.semantic_doc else ["--no-semantic-doc"]
    sources = sorted(args.golden.rglob("*_docling.json"))[: args.limit]
    if not sources:
        cli.error(f"no *_docling.json under {args.golden}")

    failures = 0
    for number, source in enumerate(sources, 1):
        dirs = {tag: args.work / f"{number:02d}" / tag for tag in "ABC"}
        codes = {
            "A": run([str(OLD_COPY)], source, dirs["A"], extra),
            "B": run([str(OLD_COPY)], source, dirs["B"], extra),
            "C": run(NEW, source, dirs["C"], extra),
        }
        problems = []
        if codes["A"] != codes["C"]:
            problems.append(f"exit old={codes['A']} new={codes['C']}")
        names = {tag: sorted(p.name for p in dirs[tag].iterdir()) for tag in "ABC"}
        if names["A"] != names["C"]:
            problems.append(f"files old={names['A']} new={names['C']}")
        noise_total = 0
        for name in names["A"]:
            if name not in names["C"] or name not in names["B"]:
                continue
            a, b, c = (load(dirs[tag] / name) for tag in "ABC")
            noise = differing(a, b)
            noise_total += len(noise)
            real = [p for p in differing(a, c) if not any(p[: len(n)] == n for n in noise)]
            if real:
                problems.append(f"{name}: {len(real)} differing paths, first {sorted(map(str, real))[:5]}")
        failures += bool(problems)
        print(f"{number}/{len(sources)} {'FAIL' if problems else 'ok'} exit={codes['A']} "
              f"noise={noise_total} {source.name}", flush=True)
        for problem in problems:
            print(f"    {problem}", flush=True)
    print(f"{len(sources) - failures}/{len(sources)} identical")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Prove the script can detect a difference (it has nothing to compare against yet)**

Run with one file: `uv run --project backend --extra tools --extra dev python scripts/prospectus_golden_check.py "$GOLDEN" "$TEMP/golden-smoke" --semantic-doc "$MAP" --limit 1`
Expected: `1/1 FAIL` with `exit old=<0 or 1> new=1` and a `files old=[...] new=[]` line, because the package does not exist. Open `$TEMP/golden-smoke/01/A` and confirm it contains `candidate.json` (and companions when the audit is not `error`). If directory A is empty, the old monolith failed to run from a `*_docling.json` input; read its stderr by re-running the printed command by hand and fix the script's arguments before continuing.

- [ ] **Step 3: Record run-to-run noise**

The `noise=` number is the count of JSON paths that differ between two old runs. Write the number and the first few noisy paths into the progress file. If noise is in the hundreds, set ordering is unstable and the check is too weak; stop and report.

- [ ] **Step 4: Commit**

```
git add scripts/prospectus_golden_check.py
git commit -m "test: add golden-output check for extractor split"
```

`backend/bintanong_tools/_golden_old/` is a temporary untracked folder; do not add it.

### Task 3: Write the splitter and generate the package

**Files:**
- Create: `scripts/split_prospectus_extractor.py`
- Create (generated): the 26 modules listed in "File structure"

- [ ] **Step 1: Write the splitter**

```python
#!/usr/bin/env python3
"""One-off: slice the monolith at BASE into bintanong_tools/prospectus_extractor/.

Code is copied byte-for-byte per top-level statement; only imports are generated.
Run from anywhere:  python scripts/split_prospectus_extractor.py
"""

from __future__ import annotations

import ast
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BASE = "7591264"
MONOLITH = "backend/bintanong_tools/bintanong_jsonifer_prolog/bintanong_prospectus_jsonifier.py"
PACKAGE = REPO / "backend" / "bintanong_tools" / "prospectus_extractor"

# (module, first line, last line, docstring) in import order: a module may only
# import from modules listed above it.
MODULES = [
    ("common", 1, 101, "Schema versions and optional Rich console objects."),
    ("docling_env", 102, 333, "Lazy Docling import, version guard, CUDA check and converter cache."),
    ("text", 334, 446, "Text cleaning, course-code keys, year and semester labels."),
    ("footnotes", 447, 593, "Footnote marker detection and stripping."),
    ("units", 594, 657, "Lecture, laboratory and total unit parsing."),
    ("prerequisites", 658, 859, "Prerequisite tokenising and resolution."),
    ("grid", 1304, 1473, "Course-code recognition, total rows and the parse result container."),
    ("layout", 860, 1128, "Column-group and header detection."),
    ("evidence", 1129, 1303, "Normalized Docling evidence: cells, tables, source boxes."),
    ("sections", 1482, 2818, "Structural tokenizer, curriculum sections and course row assembly."),
    ("repair", 2819, 3054, "Evidence-constrained semantic repair validation."),
    ("parse", 3055, 3198, "Evidence-to-curriculum entry points."),
    ("legacy", 1474, 1481, "Deprecated names kept for reference; nothing in the package calls them."),
    ("courses", 3199, 3363, "Course finalisation, classification and elective tracks."),
    ("metadata", 3364, 3509, "Program, college and school-year metadata."),
    ("audit", 3510, 3804, "Audit that fails loudly instead of emitting plausible garbage."),
    ("views", 3805, 3879, "Derived views: term tree, prerequisite edges, review CSV."),
    ("prolog", 3880, 4058, "Candidate Prolog knowledge base."),
    ("rag", 4059, 4216, "Semantic and layout RAG chunks."),
    ("paths", 4217, 4237, "Default input and output locations."),
    ("loader", 4238, 4676, "Docling-to-evidence adapter, conversion cache and document loading."),
    ("pipeline", 4677, 4937, "Payload assembly and single-document processing."),
    ("batch", 4938, 5179, "In-process batch engine and manifest."),
    ("selftest", 5493, 6203, "Built-in fixtures and the 80-check self-test."),
    ("tui", 5180, 5492, "Interactive terminal UI."),
    ("cli", 6204, 6319, "Command-line interface."),
]
# Definitions placed outside the module their line number falls in, to keep the
# import graph acyclic.
MOVES = {
    "MULTIPART_CODE": "grid",
    "is_probable_course_code": "grid",
    "_two_course_codes_in_cell": "grid",
    "build_hierarchical_rag_chunks": "rag",
    "find_default_input_root": "paths",
    "find_default_output_root": "paths",
}


def bound_names(node: ast.stmt) -> list[str]:
    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
        return [node.name]
    if isinstance(node, ast.Assign):
        return [t.id for t in node.targets if isinstance(t, ast.Name)]
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        return [node.target.id]
    if isinstance(node, ast.Try):
        names: list[str] = []
        for sub in ast.walk(node):
            if isinstance(sub, ast.Assign):
                names += [t.id for t in sub.targets if isinstance(t, ast.Name)]
            elif isinstance(sub, ast.ImportFrom):
                names += [a.asname or a.name for a in sub.names]
        return list(dict.fromkeys(names))
    return []


def strip_banner(text: str) -> str:
    rows = text.split("\n")
    while rows and not rows[0].strip():
        rows.pop(0)
    if rows and rows[0].startswith("# ====="):
        close = next(i for i in range(1, len(rows)) if rows[i].startswith("# ====="))
        rows = rows[close + 1:]
    return "\n".join(rows).strip("\n")


def main() -> None:
    source = subprocess.run(["git", "show", f"{BASE}:{MONOLITH}"], cwd=REPO, check=True,
                            capture_output=True).stdout.decode("utf-8")
    lines = source.splitlines()
    order = [name for name, *_ in MODULES]
    stdlib: dict[str, str] = {}
    chunks: dict[str, list[tuple[ast.stmt, str]]] = {name: [] for name in order}
    owner: dict[str, str] = {}
    optional: set[str] = set()

    previous_end = 0
    for index, node in enumerate(ast.parse(source).body):
        start, previous_end = previous_end, node.end_lineno
        if isinstance(node, ast.Import):
            for alias in node.names:
                stdlib[alias.asname or alias.name.split(".")[0]] = (
                    f"import {alias.name}" + (f" as {alias.asname}" if alias.asname else ""))
            continue
        if isinstance(node, ast.ImportFrom):
            for alias in node.names if node.module != "__future__" else []:
                stdlib[alias.asname or alias.name] = (
                    f"from {node.module} import {alias.name}" + (f" as {alias.asname}" if alias.asname else ""))
            continue
        if index == 0 or isinstance(node, ast.If):  # module docstring, __main__ guard
            continue
        names = bound_names(node)
        if not names:
            raise SystemExit(f"unhandled top-level statement at line {node.lineno}")
        module = MOVES.get(names[0]) or next(m for m, a, b, _ in MODULES if a <= node.lineno <= b)
        chunks[module].append((node, strip_banner("\n".join(lines[start:node.end_lineno]))))
        for name in names:
            if name in owner:
                raise SystemExit(f"{name} is defined twice (line {node.lineno})")
            owner[name] = module
        if isinstance(node, ast.Try):
            optional |= {a.asname or a.name for sub in ast.walk(node)
                         if isinstance(sub, ast.ImportFrom) for a in sub.names}

    PACKAGE.mkdir(parents=True, exist_ok=True)
    for module, _first, _last, doc in MODULES:
        used = {n.id for node, _ in chunks[module] for n in ast.walk(node) if isinstance(n, ast.Name)}
        own = {name for name, home in owner.items() if home == module}
        deps: dict[str, list[str]] = {}
        for name in sorted(used - own):
            if name in owner:
                deps.setdefault(owner[name], []).append(name)
        for dep, names in deps.items():
            if order.index(dep) >= order.index(module):
                raise SystemExit(f"{module} needs {names} from later module {dep}; add a MOVES entry")
        out = [f'"""{doc}"""', "", "from __future__ import annotations", ""]
        std = sorted({stdlib[name] for name in used - own if name in stdlib})
        out += std + [""] * bool(std)
        for dep in sorted(deps, key=order.index):
            hard = [n for n in deps[dep] if n not in optional]
            soft = [n for n in deps[dep] if n in optional]
            if soft and "RICH_AVAILABLE" not in hard:
                hard.append("RICH_AVAILABLE")
            out.append(f"from .{dep} import {', '.join(sorted(hard))}")
            if soft:  # these names only exist when Rich imported successfully
                out += ["", "if RICH_AVAILABLE:", f"    from .{dep} import {', '.join(soft)}"]
        out += [""] * bool(deps)
        for _node, text in chunks[module]:
            out += ["", text, ""]
        (PACKAGE / f"{module}.py").write_text("\n".join(out).rstrip("\n") + "\n", encoding="utf-8", newline="\n")
        print(f"{module:14} {len(chunks[module]):3} definitions")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run it**

Run: `uv run --project backend --no-sync python scripts/split_prospectus_extractor.py`
Expected: 26 lines, one per module, each with at least 1 definition, and no `SystemExit` message.

If it stops with `X needs [...] from later module Y; add a MOVES entry`: first check whether the listed name is a false hit, meaning a local variable or parameter in `X` that merely shares its name with a top-level definition in `Y`. If it is a real dependency, add one `MOVES` entry that places the *smaller* definition in the earlier module, and record the reason in the progress file. Do not edit generated modules to work around it. Do not reorder `MODULES` without re-checking every pair.

- [ ] **Step 3: Check the AST gate now mostly passes**

Run: `uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_split_equivalence.py`
Expected: `test_every_definition_moved_unchanged` PASSES (generated code is identical, including `ensure_docling_env`). `test_deviations_are_real` FAILS, because the one intended change has not been made yet. That failure is the red step for Task 4.

- [ ] **Step 4: Check every module imports**

Run:

```
uv run --project backend --extra tools --extra dev python -c "import importlib,pkgutil,backend.bintanong_tools.prospectus_extractor as p;[importlib.import_module(p.__name__+'.'+m.name) for m in pkgutil.iter_modules(p.__path__)];print('ok')"
```

Expected: `ok`. An `ImportError: cannot import name` means a circular import the order check missed; fix it with a `MOVES` entry and regenerate. A `NameError` at import time means a name used at module level was not detected as a dependency; report it rather than hand-patching.

- [ ] **Step 5: Commit**

```
git add scripts/split_prospectus_extractor.py backend/bintanong_tools/prospectus_extractor
git commit -m "refactor: generate prospectus_extractor package from the monolith"
```

### Task 4: Entry points, shim, and the one intended code change

**Files:**
- Create: `backend/bintanong_tools/prospectus_extractor/__init__.py`
- Create: `backend/bintanong_tools/prospectus_extractor/__main__.py`
- Modify: `backend/bintanong_tools/prospectus_extractor/docling_env.py` (`ensure_docling_env`, last line only)
- Replace: `backend/bintanong_tools/bintanong_jsonifer_prolog/bintanong_prospectus_jsonifier.py`
- Create: `tests/test_prospectus_entrypoints.py`

- [ ] **Step 1: Write the failing entry-point tests**

```python
"""The extractor must start the same way from every supported entry point."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOLS = REPO / "backend" / "bintanong_tools"
SHIM = TOOLS / "bintanong_jsonifer_prolog" / "bintanong_prospectus_jsonifier.py"

ENTRY_POINTS = {
    "module": ["-m", "backend.bintanong_tools.prospectus_extractor"],
    "package directory": [str(TOOLS / "prospectus_extractor")],
    "legacy shim": [str(SHIM)],
}


@pytest.mark.parametrize("entry", ENTRY_POINTS.values(), ids=ENTRY_POINTS.keys())
def test_self_test_passes_from_every_entry_point(entry):
    done = subprocess.run([sys.executable, *entry, "--self-test"], cwd=REPO,
                          capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert done.returncode == 0, done.stdout[-2000:] + done.stderr[-2000:]
    assert "80/80" in done.stdout


def test_shim_reexports_private_names_used_by_existing_tests():
    from backend.bintanong_tools import prospectus_extractor
    from backend.bintanong_tools.bintanong_jsonifer_prolog import bintanong_prospectus_jsonifier as shim

    for name in ("_row_field_candidates", "_two_course_codes_in_cell", "build_audit", "ColumnGroup",
                 "docling_to_normalized_table", "evidence_from_grids", "parse_curriculum_evidence",
                 "BatchConfig", "build_batch_items", "scan_inputs", "LoadedDocument", "main"):
        assert hasattr(shim, name), name
    assert shim.parse_curriculum_evidence is prospectus_extractor.parse_curriculum_evidence


def test_relaunch_reuses_the_original_command_line(monkeypatch):
    from backend.bintanong_tools.prospectus_extractor import docling_env

    calls = []
    monkeypatch.delenv("_PALSU_RELAUNCHED", raising=False)
    monkeypatch.setattr(docling_env, "_docling_importable", lambda: False)
    monkeypatch.setattr(docling_env, "_venv_python", lambda: Path("venv-python"))
    monkeypatch.setattr(docling_env.sys, "orig_argv", ["python", "-m", "pkg", "-i", "x.pdf"])
    monkeypatch.setattr(docling_env.subprocess, "call", lambda cmd, env: calls.append((cmd, env)) or 0)
    with pytest.raises(SystemExit):
        docling_env.ensure_docling_env()
    assert calls[0][0] == ["venv-python", "-m", "pkg", "-i", "x.pdf"]
    assert calls[0][1]["_PALSU_RELAUNCHED"] == "1"
```

- [ ] **Step 2: Run and confirm the failures**

Run: `uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_entrypoints.py`
Expected: "module" and "package directory" fail (no `__main__.py`); "legacy shim" PASSES (still the monolith); the re-export test fails on the `is` assertion; the relaunch test fails because the command ends with the path of `docling_env.py`.

- [ ] **Step 3: Write `__init__.py`**

```python
"""PalSU prospectus extractor: original PDF (via Docling) to source-linked curriculum JSON.

Outputs are review candidates. An extractor audit of ``ok`` is not institutional
approval; see plans/2026-09-26-prospectus-phase2-implementation-draft.md.

Run it with any of::

    python -m bintanong_tools.prospectus_extractor --self-test
    python path/to/prospectus_extractor -i prospectus.pdf -o out.json --export-csv --strict
    python -m backend.bintanong_tools.prospectus_batch -i PDF_FOLDER -o NEW_RUN_FOLDER
"""

from .batch import BatchConfig, build_batch_items, run_batch, scan_inputs
from .cli import main
from .common import MANIFEST_SCHEMA_VERSION, SCHEMA_VERSION
from .evidence import LoadedDocument, NormalizedCell, NormalizedTable, ProspectusEvidence
from .loader import evidence_adapter, load_document
from .parse import parse_curriculum_evidence
from .pipeline import build_essentials, build_payload, process_prospectus
from .selftest import run_self_tests

__all__ = [
    "BatchConfig", "LoadedDocument", "MANIFEST_SCHEMA_VERSION", "NormalizedCell", "NormalizedTable",
    "ProspectusEvidence", "SCHEMA_VERSION", "build_batch_items", "build_essentials", "build_payload",
    "evidence_adapter", "load_document", "main", "parse_curriculum_evidence", "process_prospectus",
    "run_batch", "run_self_tests", "scan_inputs",
]
```

- [ ] **Step 4: Write `__main__.py`**

```python
"""Entry point for ``python -m …prospectus_extractor`` and ``python path/to/prospectus_extractor``."""

import sys
from pathlib import Path

if __package__:
    from .cli import main
else:  # started by path: make the package importable by its own name
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from prospectus_extractor.cli import main

sys.exit(main())
```

- [ ] **Step 5: Make the one intended change in `docling_env.py`**

Replace the last line of `ensure_docling_env`:

```python
    sys.exit(subprocess.call([str(venv_py), str(Path(__file__).resolve())] + sys.argv[1:], env=env))
```

with:

```python
    sys.exit(subprocess.call([str(venv_py), *sys.orig_argv[1:]], env=env))
```

Change nothing else in the function.

- [ ] **Step 6: Replace the monolith with the shim**

The whole new content of `bintanong_prospectus_jsonifier.py`:

```python
#!/usr/bin/env python3
"""Compatibility entry point for the PalSU prospectus extractor.

The code now lives in ``bintanong_tools/prospectus_extractor/``. This file keeps
older commands and imports working: it re-exports every name the single-file
version defined and runs the same CLI.

    python bintanong_prospectus_jsonifier.py --self-test
    python bintanong_prospectus_jsonifier.py -i prospectus.pdf --export-pl --export-csv
"""

import importlib
import pkgutil
import sys
from pathlib import Path

if __package__:
    _package = importlib.import_module("..prospectus_extractor", __package__)
else:  # started by path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    _package = importlib.import_module("prospectus_extractor")

for _info in pkgutil.iter_modules(_package.__path__):
    if _info.name != "__main__":
        _module = importlib.import_module(f"{_package.__name__}.{_info.name}")
        globals().update({k: v for k, v in vars(_module).items() if not k.startswith("__")})

if __name__ == "__main__":
    sys.exit(main())  # noqa: F821 - re-exported from prospectus_extractor.cli
```

- [ ] **Step 7: Run everything**

Run: `uv run --project backend --extra tools --extra dev --with fastapi==0.141.1 python -m pytest -q tests`
Expected: the previous 26 tests and 13 subtests pass, plus 5 new entry-point tests and both split-equivalence tests. No failures.

- [ ] **Step 8: Commit**

```
git add backend/bintanong_tools/prospectus_extractor backend/bintanong_tools/bintanong_jsonifer_prolog/bintanong_prospectus_jsonifier.py tests/test_prospectus_entrypoints.py
git commit -m "refactor: route the jsonifier entry points through prospectus_extractor"
```

### Task 5: Point the isolated batch runner at the package

**Files:**
- Modify: `backend/bintanong_tools/prospectus_batch.py`
- Modify: `tests/test_prospectus_batch.py`

Two things break silently otherwise: `parser_sha256` would hash only the shim, so a parser change would no longer change the recorded hash; and the child command would keep depending on the shim.

- [ ] **Step 1: Add the failing test** (append inside `IsolatedBatchTests` in `tests/test_prospectus_batch.py`)

```python
    def test_parser_hash_covers_every_package_module(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory)
            (package / "a.py").write_text("A = 1\n", encoding="utf-8")
            (package / "b.py").write_text("B = 1\n", encoding="utf-8")
            before = prospectus_batch.package_sha256(package)
            self.assertEqual(before, prospectus_batch.package_sha256(package))
            (package / "b.py").write_text("B = 2\n", encoding="utf-8")
            self.assertNotEqual(before, prospectus_batch.package_sha256(package))

    def test_child_runs_the_package_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "pdfs"
            source.mkdir()
            (source / "a.pdf").write_bytes(b"%PDF-test")
            commands = []

            def fake_child(command, **_kwargs):
                commands.append(command)
                return SimpleNamespace(returncode=1)

            with patch.object(prospectus_batch.subprocess, "run", side_effect=fake_child):
                prospectus_batch.run_isolated(source, Path(directory) / "out", None)
            self.assertEqual(Path(commands[0][1]).name, "prospectus_extractor")
            self.assertTrue((Path(commands[0][1]) / "__main__.py").is_file())
```

- [ ] **Step 2: Run and confirm both fail**

Run: `uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_batch.py`
Expected: `AttributeError: … has no attribute 'package_sha256'`, and the second test fails because the child path is the shim file.

- [ ] **Step 3: Implement**

In `prospectus_batch.py`, change the import:

```python
from . import prospectus_extractor as extractor
```

Add below the imports:

```python
PACKAGE_DIR = Path(extractor.__file__).resolve().parent


def package_sha256(package: Path = PACKAGE_DIR) -> str:
    """One hash over every module, so any parser change changes the recorded hash."""
    digest = hashlib.sha256()
    for path in sorted(package.glob("*.py")):
        digest.update(path.name.encode())
        digest.update(path.read_bytes().replace(b"\r\n", b"\n"))
    return digest.hexdigest()
```

In `run_isolated`, replace `str(Path(extractor.__file__).resolve())` in `command` with `str(PACKAGE_DIR)`, and replace the `"parser_sha256"` value with `package_sha256()`.

Line endings are normalised so the same commit hashes equally on Windows and Linux checkouts.

- [ ] **Step 4: Run the suite**

Run: `uv run --project backend --extra tools --extra dev --with fastapi==0.141.1 python -m pytest -q tests`
Expected: all pass.

- [ ] **Step 5: Commit**

```
git add backend/bintanong_tools/prospectus_batch.py tests/test_prospectus_batch.py
git commit -m "fix: hash and launch the extractor package in the isolated batch"
```

### Task 6: Prove the outputs are identical, then document

**Files:**
- Create: `docs/decisions/prospectus-extractor-package.md`
- Create: `tests/test_prospectus_selftest.py`
- Modify: `.gitignore` (add one line; leave the user's existing uncommitted edits in place and stage only the new line with `git add -p`)

- [ ] **Step 1: Run the golden check on all 44 inputs**

Run: `uv run --project backend --extra tools --extra dev python scripts/prospectus_golden_check.py "$GOLDEN" "$TEMP/golden-full" --semantic-doc "$MAP"`
Expected final line: `44/44 identical`, exit code 0. Every line shows the same `exit=` the old code gave (1 for audit errors is normal: the last batch had 38).

Any `FAIL` line is a real behavior difference. Use superpowers:systematic-debugging: diff `A/candidate.json` against `C/candidate.json` for that input, find the first differing field, trace it to the module, and fix the *splitter or its manifest*, never the generated code by hand. Regenerate, re-apply Task 4 step 5, and rerun.

- [ ] **Step 2: Add the permanent self-test wrapper**

```python
"""The extractor's built-in 80-check suite, run under pytest."""

from backend.bintanong_tools.prospectus_extractor import run_self_tests


def test_builtin_self_tests_pass():
    assert run_self_tests(verbose=False) == 0
```

Run: `uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_selftest.py`
Expected: 1 passed. (`run_self_tests` returns the number of failed checks.)

- [ ] **Step 3: Write the decision record**

`docs/decisions/prospectus-extractor-package.md` must state, in plain sentences: the base commit and monolith hash; the module table from this plan; the two forced exceptions with their before and after lines; the `MOVES` entries and why each exists; the exact golden-check command, date, and `44/44 identical` result with the measured noise count; that the outputs remain review candidates; and how to run the extractor on Windows, Linux, and macOS (`python -m`, package directory, shim).

- [ ] **Step 4: Ignore the new default output folder**

Add this line under the existing `# local Bintanong PDF files` block of `.gitignore`:

```
/backend/bintanong_tools/prospectus_extractor/docling_jsonified_output/
```

- [ ] **Step 5: Codex gate**

Run: `codex exec "Review branch refactor/prospectus-extractor-package against commit 7591264 in this repo. The claim is that backend/bintanong_tools/prospectus_extractor is a behavior-identical split of the old bintanong_prospectus_jsonifier.py except for ensure_docling_env. Try to find any behavior difference, circular import, platform-specific path, or name the shim fails to re-export. Do not modify files. Report findings with file and line."`
Record the findings in the progress file. Fix confirmed findings with a failing test first; note and skip unconfirmed ones.

- [ ] **Step 6: Commit**

```
git add docs/decisions/prospectus-extractor-package.md tests/test_prospectus_selftest.py
git add -p .gitignore
git commit -m "docs: record the extractor package split and its equivalence evidence"
```

### Task 7: Remove the scaffolding and hand off

**Files:**
- Delete: `scripts/split_prospectus_extractor.py`, `scripts/prospectus_golden_check.py`, the untracked folder `backend/bintanong_tools/_golden_old/`
- Keep until Phase B starts: `tests/test_prospectus_split_equivalence.py`
- Modify: `plans/plan_current_progress/extractor_split_progress.md`, `plans/plan_current_progress/current_progress.md`

- [ ] **Step 1:** Delete the two scripts and the `_golden_old` folder. They stay available in Git history at the Task 6 commit; record that commit hash in the decision record.
- [ ] **Step 2:** Run the full suite once more. Expected: all pass.
- [ ] **Step 3:** Append a dated "Extractor package split" section to `current_progress.md`: branch, commits, test counts, golden result, the new `parser_sha256` meaning (package hash, not file hash, so it is not comparable with `8ea750…`), and "next: Phase B".
- [ ] **Step 4:** Commit with `git commit -m "chore: remove extractor split scaffolding"`. Do not merge into `dev` and do not push; ask the user (superpowers:finishing-a-development-branch).

**Phase A gate:** AST test green; `44/44 identical`; 80/80 from all three entry points; full suite green; decision record written; Codex findings resolved or recorded.

---

# Phases B–F — what comes next and how

Each phase gets its own detailed plan (same format as Phase A, written with superpowers:writing-plans) on its own branch from the merged Phase A, because each depends on details that only exist after the phase before it. What is fixed now is the order, the files, the tests that must fail first, and the gate.

When Phase B begins, delete `tests/test_prospectus_split_equivalence.py` in its first commit: from then on the package is allowed to differ from the monolith.

### Phase B — Markup twin that looks like the printed prospectus (Q6)

**Why first:** it only reads existing evidence, changes no extracted value, and the review GUI (draft Task 5) needs exactly this view.

**New file:** `prospectus_extractor/markup.py` with `render_prospectus_markup(evidence: ProspectusEvidence, payload: Mapping[str, Any]) -> str`. New CLI flag `--export-md` (included in `--export-all`), writing `<stem>_prospectus.md`.

**Shape:** the document follows the PDF top to bottom. Header text items (university, college, program, school year) come first in source order. Each Docling table is rendered as an HTML `<table>` inside the Markdown, because Markdown tables cannot express the merged year and semester banners. Every `NormalizedCell` becomes one `<td>` with its real `rowspan`/`colspan`, `data-cell="t0-c124"`, and `data-page`. So the two semesters sit side by side exactly as printed, banner rows span the full width, and `TOTAL` rows stay where they are. Footnotes and elective lists follow in source order. Cell text is the source text, never a paraphrase (master §7.1). The first line is a status comment: `<!-- extraction_audit: error | REVIEW REQUIRED | pdf_sha256: … -->`.

**Tests first (`tests/test_prospectus_markup.py`):** a merged banner cell yields one `<td colspan=…>` and not repeated text; every cell ID in the evidence appears exactly once; the BSCS self-test fixture renders both semesters of first year in one table row group; HTML-special characters in cell text are escaped; an `error` audit puts `REVIEW REQUIRED` in the first line; rendering is deterministic across two runs.

**Gate:** for BSCS and Architecture, a person comparing the rendered file with the PDF page finds the same rows, columns, and merged cells. Codex gate on the renderer.

### Phase C — Separate audit, review, and source states (draft Task 3)

**Files:** `audit.py`, `pipeline.py`, `metadata.py`, `prolog.py`, `backend/bintanong_tools/prospectus.py`; tests in `tests/test_prospectus_authority.py`.

**Changes:** the payload gains three distinct fields, `extraction_audit`, `content_review` (always `"pending"` from the extractor), and `source_verification` (from `ProvisionalSource`). `promotion_status` stays for compatibility but nothing may read it as approval. `resolve_metadata` reports campus, college, and program as observations with their evidence instead of asserting the hardcoded campus. Prerequisite state becomes one of `reviewed_empty`, `unreadable`, `unresolved_reference`, `standing_condition`, `resolved`. A course with anything other than `resolved` or `reviewed_empty` is excluded from `eligible/2` and `next_eligible/2` facts. A blocked audit stops embedding candidate Prolog and RAG objects in the detailed JSON.

**Tests first:** the seven cases named in the draft (mismatched scope, pending identity, hash mismatch, unreadable cell, unresolved token, standing-only, `OR`/exception text), each asserting no executable eligibility is produced even when the audit says `VERIFIED`.

**Gate:** rerun the 44-path isolated batch; course fields are unchanged from the Phase A baseline, only status fields and blocked companions differ. Bump `SCHEMA_VERSION`.

### Phase D — Safe cache and output publication (draft Task 4)

**Files:** `loader.py`, `pipeline.py`, `batch.py`; tests in `tests/test_prospectus_runs.py`.

**Changes:** the cache key includes the PDF SHA-256, Docling settings, and `package_sha256()`. `--skip-existing` compares that key and audit status instead of file existence. `process_prospectus` writes into a temporary directory next to the target and publishes with `Path.replace` only after conversion and audit finish; a failure leaves earlier outputs untouched and writes diagnostics to `<output>/failed/`.

**Tests first:** same path with changed bytes reconverts; cache without a matching hash is ignored; `--skip-existing` does not skip a failed audit; a conversion exception after a successful run leaves the earlier files byte-identical.

**Gate:** failure-injection run recorded; repeat run of unchanged input produces identical files.

### Phase E — Source-linked, edition-stable RAG chunks (draft Task 6, master §7.2)

**Files:** `rag.py`, `pipeline.py`; tests in `tests/test_prospectus_chunks.py`.

**Changes:** every course chunk carries `pdf_sha256`, page, table index, cell IDs, and the canonical source text, kept separate from the advising summary. Term and elective summaries list all contributing spans. Chunk ID is a hash of (PDF SHA-256, source locator, content hash, chunker version), replacing `<code>::course`. Token length is checked against the 512-token embedding limit named in master §7.2, with a 300–400 target. Chunks are built from reviewed or corrected candidates once the GUI exists; until then they are labelled `content_review: pending`.

**Tests first:** two editions of one course get different IDs; two runs of the same PDF get the same IDs; a multi-page summary lists every page; a prerequisite assertion without source cells is rejected.

**Gate:** every prerequisite or standing chunk of the two pilot PDFs resolves to the right page and cells. No embedding call.

### Phase F — Tools boundary (draft Task 7)

**Files:** `backend/bintanong_tools/ingest.py` (new `prospectus` command), `backend/bintanong_tools/prospectus.py` (adapter returning a candidate-run manifest), `compose.yaml` (read-only PDF mount, separate writable output mount), `tests/test_prospectus_cli.py`.

**Changes:** explicit `--source-root`, `--semantic-doc`, and provisional source record arguments replace the in-repo default paths in `paths.py`. The command refuses to run on a hash mismatch.

**Gate:** host and container produce equal candidate facts for one pilot PDF; `docker compose --profile tools run --rm ingest python -m bintanong_tools.ingest prospectus --help` works on Linux.

### Still owed by the existing draft, unchanged by this plan

Parser defect repairs (draft Task 2 remainder), the local review GUI (draft Task 5, after Phase B), and the 39-PDF reference review (draft Task 8). No accuracy claim and no active release follows from any phase here.

---

## Keeping track when usage runs low

`plans/plan_current_progress/extractor_split_progress.md` is the single resume point. After every task commit the controller writes: task number, commit hash, test counts actually observed, anything surprising, and the exact next step. If a subagent or Codex stops on a usage limit, write that down with what it had finished, inspect its partial work, and finish or redo the task locally. A fresh session resumes by reading that file, then `git log --oneline dev..HEAD`, then rerunning the full suite before trusting any recorded number.

## Self-review

- Spec coverage: split into functions and scripts (Tasks 3–5); 1:1 (Tasks 1, 2, 6); cross-platform entry points (Task 4, `sys.orig_argv`, `pathlib`, line-ending-neutral hash); legacy code kept in its own file (`legacy.py`); self-test kept (Tasks 4, 6); PalSU-like markup (Phase B); RAG readiness (Phases C–E); branch isolation; plan-alignment analysis; Codex gates; low-usage tracking.
- Names used consistently: `package_sha256`, `PACKAGE_DIR`, `run_self_tests`, `MOVES`, `MODULES`, `DEVIATIONS`.
- Known risk: the splitter's dependency detection is name-based, so a local variable that shares a name with a top-level definition yields a harmless extra import or a false "later module" stop. Task 3 step 2 says how to handle it.
