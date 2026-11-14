# Exact task brief from plans\2026-10-03-prospectus-phase-f-tools-cli.md

Read approved_execution.md and preflight-ledger.md first. They supersede obsolete base/merge/dev/version/path snippets in this preserved historical plan. Do not edit the original plan. Preserve original task requirements below unless an approved ruling supersedes them.

### Task 10: Regression proof on the 44 cached inputs

**Files:**
- Create: `scripts/prospectus_course_compare.py` (temporary, deleted in Task 11)

Phase F changes no parser code, but it touches `pipeline.py`. The rule for every phase is a field-level proof on the 44 cached inputs. The earlier golden script is recoverable with `git show 2dffe3d:scripts/prospectus_golden_check.py`; this comparer is its field-level descendant (course fields only, base commit as a git worktree instead of a copied monolith).

- [ ] **Step 1: Write the comparer**

```python
#!/usr/bin/env python3
"""Phase F gate: course fields on the cached Docling JSON inputs are identical, base vs this branch.

    python scripts/prospectus_course_compare.py run --side old --code-root WORKTREE --golden DIR --work WORK --semantic-doc MAP
    python scripts/prospectus_course_compare.py run --side new --code-root REPO     --golden DIR --work WORK --semantic-doc MAP
    python scripts/prospectus_course_compare.py compare --work WORK

Each `run` takes ~2 minutes per input, so launch both sides detached and poll their logs.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

COURSE_FIELDS = (
    "course_code", "course_title", "year_level", "semester", "total_units", "lecture_units",
    "lab_units", "prerequisites", "prerequisites_raw", "prerequisites_unresolved",
    "standing_requirements",
)


def audit_status(payload: dict) -> str:
    audit = payload.get("extraction_audit", payload["audit"])
    return audit["status"] if isinstance(audit, dict) else str(audit)


def course_view(payload: dict) -> dict:
    return {
        "audit_status": audit_status(payload),
        "courses": [{field: course.get(field) for field in COURSE_FIELDS} for course in payload["courses"]],
    }


def run(args: argparse.Namespace) -> int:
    sources = sorted(args.golden.rglob("*_docling.json"))[: args.limit]
    if not sources:
        print(f"no *_docling.json under {args.golden}")
        return 2
    env = dict(os.environ, PYTHONHASHSEED="0", PYTHONIOENCODING="utf-8")
    for number, source in enumerate(sources, 1):
        out_dir = args.work / args.side / f"{number:02d}"
        out_dir.mkdir(parents=True, exist_ok=True)
        command = [
            sys.executable, "-m", "backend.bintanong_tools.prospectus_extractor",
            "-i", str(source), "-o", str(out_dir / "candidate.json"), "--device", "cpu",
            "--semantic-doc", str(args.semantic_doc),
        ]
        code = subprocess.run(command, cwd=args.code_root, env=env, capture_output=True).returncode
        (out_dir / "exit.txt").write_text(f"{code}\n{source.name}\n", encoding="utf-8")
        print(f"{args.side} {number}/{len(sources)} exit={code} {source.name}", flush=True)
    return 0


def compare(args: argparse.Namespace) -> int:
    old_dirs = sorted(p for p in (args.work / "old").iterdir() if p.is_dir())
    problems = 0
    for old in old_dirs:
        new = args.work / "new" / old.name
        notes = []
        if (old / "exit.txt").read_text(encoding="utf-8") != (new / "exit.txt").read_text(encoding="utf-8"):
            notes.append("exit code or input differs")
        old_json, new_json = old / "candidate.json", new / "candidate.json"
        if old_json.exists() != new_json.exists():
            notes.append("candidate.json present on one side only")
        elif old_json.exists():
            a = course_view(json.loads(old_json.read_text(encoding="utf-8")))
            b = course_view(json.loads(new_json.read_text(encoding="utf-8")))
            if a["audit_status"] != b["audit_status"]:
                notes.append(f"audit {a['audit_status']} -> {b['audit_status']}")
            if a["courses"] != b["courses"]:
                first = next((i for i, (x, y) in enumerate(zip(a["courses"], b["courses"])) if x != y), None)
                notes.append(f"courses differ (counts {len(a['courses'])}/{len(b['courses'])}, first index {first})")
        problems += bool(notes)
        print(f"{old.name} {'FAIL' if notes else 'ok'} {'; '.join(notes)}")
    print(f"{len(old_dirs) - problems}/{len(old_dirs)} identical")
    return 1 if problems else 0


def main() -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    sub = cli.add_subparsers(dest="mode", required=True)
    runner = sub.add_parser("run")
    runner.add_argument("--side", choices=("old", "new"), required=True)
    runner.add_argument("--code-root", type=Path, required=True)
    runner.add_argument("--golden", type=Path, required=True)
    runner.add_argument("--work", type=Path, required=True)
    runner.add_argument("--semantic-doc", type=Path, required=True)
    runner.add_argument("--limit", type=int)
    comparer = sub.add_parser("compare")
    comparer.add_argument("--work", type=Path, required=True)
    args = cli.parse_args()
    return run(args) if args.mode == "run" else compare(args)


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Prove the comparer can fail.** Use two inputs and a seeded difference:

```
$Work = "$env:TEMP\f-compare-smoke"
git worktree add "$env:TEMP\bintanong-base-old" dev
uv run --project backend --extra tools --extra dev python scripts/prospectus_course_compare.py run --side old --code-root "$env:TEMP\bintanong-base-old" --golden "$GOLDEN" --work $Work --semantic-doc "$MAP" --limit 1
uv run --project backend --extra tools --extra dev python scripts/prospectus_course_compare.py run --side new --code-root . --golden "$GOLDEN" --work $Work --semantic-doc "$MAP" --limit 1
uv run --project backend --extra tools --extra dev python scripts/prospectus_course_compare.py compare --work $Work
```

Expected: `01 ok` and `1/1 identical`. (`dev` is the base because this branch came from it and no Phase F code is on `dev`.) Then edit the `new` side's `$Work\new\01\candidate.json`, change one `course_code`, re-run `compare`, expected `01 FAIL courses differ` and exit 1; restore by re-running the `new` step.

- [ ] **Step 3: Launch the full 44-input run, both sides in parallel, detached.** Each side takes about 90 minutes.

```
$Work = "$env:TEMP\f-compare-full"
$py = "uv run --project '$Repo\backend' --extra tools --extra dev python '$Repo\scripts\prospectus_course_compare.py'"
Start-Process pwsh -ArgumentList '-NoProfile','-Command',"$py run --side old --code-root '$env:TEMP\bintanong-base-old' --golden '$GOLDEN' --work '$Work' --semantic-doc '$MAP' *> '$env:TEMP\f-old.log'" -WindowStyle Hidden
Start-Process pwsh -ArgumentList '-NoProfile','-Command',"cd '$Repo'; $py run --side new --code-root '$Repo' --golden '$GOLDEN' --work '$Work' --semantic-doc '$MAP' *> '$env:TEMP\f-new.log'" -WindowStyle Hidden
```

Poll `Get-Content $env:TEMP\f-old.log -Tail 2` and the `f-new.log` every few minutes; background tool calls die at 10 minutes, which is why the processes are started with `Start-Process`. Continue with Task 11 while waiting. When both logs show `44/44`, run the `compare` command against `$Work`.

Expected final line: `44/44 identical`. A `FAIL` means a course field differs between `dev` and this branch: Phase F should not be able to do that, so diff the two `candidate.json` files for that input, find the first differing course, and trace it (most likely a Phase B-E side effect on `dev` that moved since the base was recorded, which should be reported, not hidden).

- [ ] **Step 4: Record the result** (line, date, input count) in the progress file.

---



### Task 11: Documentation, Codex gate, finish

**Files:**
- Create: `docs/decisions/prospectus-tools-boundary.md`
- Delete: `scripts/prospectus_course_compare.py`
- Modify: `plans/plan_current_progress/extractor_split_progress.md`, `plans/plan_current_progress/current_progress.md`

- [ ] **Step 1: Write the decision and runbook** `docs/decisions/prospectus-tools-boundary.md` with exactly these sections and content (fill the Evidence section only with values observed in Tasks 9 and 10):

  1. **What this is.** The `prospectus` command and `prospectus.run_candidate()` turn an original PDF plus a provisional source record into a review-only candidate run. Nothing approves a source, curriculum, RAG, Prolog, or a Supabase release.
  2. **Decisions D1-D5** (the table above, with the chosen options), the smaller choices list, and the D2 consequence: `ingest parse <path>` replaces the old bare `ingest <path>` form.
  3. **Local reviewer flow.** Host command (from `backend/`): `uv run --extra tools python -m bintanong_tools.ingest prospectus <pdf-or-folder> --source-root <pdf root> --source-record <inventory.csv|record.json> --semantic-doc <map.md> --output-dir <new folder> [--strict]`. Container command: `docker compose --profile tools run --rm ingest python -m bintanong_tools.ingest prospectus "/sources/<path>" --source-root /sources --source-record /sources/<record file> --output-dir /candidate-output`, with `PROSPECTUS_PDF_DIR` and `PROSPECTUS_OUTPUT_DIR` set (the record file and semantic map must sit inside the PDF folder).
  4. **Record format.** CSV columns `pdf_sha256,source_locator,source_verification` (`pending` only) or JSON with the same keys (one object or a list). Locators are relative to `--source-root`, backslashes accepted.
  5. **Output layout and statuses.** `<output>/<locator without .pdf>/` with `candidate_run.json` and the artifacts it hashes; folder runs add `<output>/candidate_runs.json`. The three status fields, their meaning, and that `approved_source_version_id` is always `null` until a later step maps a Phase 1 source version. Exit codes `0/1/2`.
  6. **Refusals.** Hash mismatch (before and after conversion), no record for a PDF, record claiming anything but `pending`, path outside the source root, non-PDF input, missing Docling (with the `uv sync --extra tools` fix), existing run directory, missing semantic map. Folder mode checks every PDF before converting any.
  7. **Not supported.** Scanned or photographed prospectuses (OCR is off; a separate plan covers it, and `source_kind` stays in the evidence for it). Review decisions and the GUI (workstream draft Task 5). Release authoring.
  8. **Weight cache.** Named volume `docling-cache`; where the weights actually landed (from Task 9 Step 6); first run needs network, later runs set `HF_HUB_OFFLINE=1`; fallback (c).
  9. **Image hygiene.** The `.dockerignore` additions and why (Finding 1).
  10. **Host versus container.** Equivalence is on `candidate_facts_sha256`; artifact byte hashes differ by line endings (Finding 4).
  11. **Evidence** (observed values only): suite counts; `44/44 identical` line with date; either the Task 9 container results (engine versions, three exit codes, audit status, cache listing, offline result, equal lines) or the exact "Container gate: NOT RUN" sentence from Task 9 Step 1.

- [ ] **Step 2: Remove the scaffolding**

```
git worktree remove --force "$env:TEMP\bintanong-base-old"
git rm scripts/prospectus_course_compare.py
```

- [ ] **Step 3: Full suite and self-test**

Run both commands from "Commands used throughout". Expected: all pass (baseline plus the tests added in Tasks 2-8) and `80/80`.

- [ ] **Step 4: Codex gate.** Write the prompt to a file, launch detached, poll the output (about 15 minutes):

```
@'
Review branch feature/prospectus-tools-boundary against dev in this repo. Claims to test: (1) `prospectus` command and prospectus.run_candidate refuse on PDF hash mismatch before writing anything and re-verify after conversion; (2) a source record can never carry an approved state and the manifest source_verification always comes from ProvisionalSource; (3) folder mode checks every PDF and record before converting any; (4) the new command never reads paths.py defaults (DEFAULT_SEMANTIC_DOC, SOURCE_PDF_ROOT, DEFAULT_TARGET_PDF); (5) compose mounts PDFs read-only, outputs separately, publishes no port, and .dockerignore keeps dataset PDFs and host venvs out of the image; (6) the legacy extractor CLI and parse command behavior are unchanged except that `ingest parse <path>` is now a real subcommand. Try to find a way to produce a candidate from altered bytes, to write into the PDF mount, to smuggle an approval state, a path-traversal locator, or a Windows/Linux path bug. Do not modify files. Report findings with file and line.
'@ | Set-Content "$env:TEMP\codex-phase-f-prompt.txt" -Encoding utf8
Start-Process pwsh -ArgumentList '-NoProfile','-Command',"cd '$Repo'; codex exec --sandbox read-only -o '$env:TEMP\codex-phase-f.txt' (Get-Content -Raw '$env:TEMP\codex-phase-f-prompt.txt') *> '$env:TEMP\codex-phase-f.log'" -WindowStyle Hidden
```

Expected: `codex-phase-f.txt` appears with findings. Record them in the progress file. For each confirmed finding, write a failing test first, fix, and re-run the suite; note and skip unconfirmed ones. If Codex is rate-limited or errors, record that and continue.

- [ ] **Step 5: Progress files and commit**

Append to `plans/plan_current_progress/current_progress.md` a dated "Phase F: tools boundary" section: branch, commits, test counts, the `44/44 identical` line, container evidence or the skipped statement, the D2 command-form change, and "next: user decides on merge".

```
git add docs/decisions/prospectus-tools-boundary.md plans/plan_current_progress/extractor_split_progress.md plans/plan_current_progress/current_progress.md
git commit -m "docs: record the prospectus tools boundary, its runbook and evidence" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
git commit -m "chore: remove Phase F comparison scaffolding" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

(The second commit holds the `git rm` from Step 2; if it was staged earlier, commit it separately before the docs commit.) Do not merge into `dev` and do not push; ask the user (superpowers:finishing-a-development-branch).

**Phase F gate:** adapter and command tests green; `parse` contract tests green; Compose and `.dockerignore` tests green; `44/44 identical` on course fields; Codex findings resolved or recorded; and either the container evidence recorded (command shape, one pilot conversion, host/container `candidate_facts_sha256` equal, weight-cache result) or the container gate explicitly recorded as NOT RUN with the reason. Neither path activates RAG, Prolog, or a Supabase release.

---

## Self-review

- **Spec coverage.** Adapter with hash refusal, extractor call, manifest with provisional ID, null approved ID, hash, versions incl. package hash, artifacts with hashes, three statuses: Task 4. Typer command for a single PDF and a folder, provisional record input form decided (D1): Tasks 2, 5, 6. Explicit `--source-root` and `--semantic-doc` replacing in-repo defaults, legacy defaults kept: Tasks 3, 5 (the spy test), and "Not touched: paths.py, cli.py". Compose read-only PDF mount, separate writable mount, `:?` variables, no public service: Task 8. CLI/API equivalence: Task 7 and Task 9 Step 7. Docker verification command, real conversion, and skipped-evidence wording when no engine: Task 9. Model weights caching: D5, Tasks 8 and 9. Which Phase C/D outputs are consumed: the table plus `_status_fields`. Regression on the 44 inputs with detached launch: Task 10. Codex gate and progress updates: Task 11 and each task. `SCHEMA_VERSION` decision: stated (not bumped, why). OCR: no OCR planned; the manifest and notes keep `source_kind` out of the way.
- **Placeholder scan.** No TBD or "similar to". The only non-literal items are values the executor must observe (Evidence section, cache location, the Phase C key shape), each with the command that produces them and what to do for each outcome.
- **Name consistency.** `ProvisionalSource.provisional_source_id`, `SourceRecordError`, `load_provisional_sources`, `locator_for`, `source_for_pdf`, `normalize_locator`, `ExtractionSettings`, `run_candidate`, `run_candidates`, `run_dir_for`, `candidate_facts`, `_status_fields`, `_artifact_records`, `_child_command`, `_run_child`, `_run_folder`, `_summary`, `MANIFEST_NAME`, `INDEX_NAME`, `EXPECTED_FAILURES`, fixture `fake_conversion`, helpers `make_pdf` / `make_world` / `make_folder` / `invoke` / `prospectus_args`: defined in the task that first uses them and spelled identically afterwards. `run_candidates` calls `run_candidate` and `_run_child` by module-global name, which is what the tests patch.
- **Known risks.** Task 9 depends on a Docker engine that is not running today and on Docling's real cache location (an assumption verified, not claimed). Task 5's `__spec__.name` module derivation is checked by two tests. Phases B-E may rename payload keys or the `process_prospectus` signature; Task 1 Step 3 is the control.
