# Exact task brief from plans\2026-10-03-prospectus-phase-d-safe-cache.md

Read approved_execution.md and preflight-ledger.md first. They supersede obsolete base/merge/dev/version/path snippets in this preserved historical plan. Do not edit the original plan. Preserve original task requirements below unless an approved ruling supersedes them.

### Task 8: Prove the course fields are unchanged on the 44 cached inputs

**Files:**
- Create (not committed): `scripts/prospectus_course_compare.py`

The earlier golden script was deleted in `38af9fd`'s successor; it is recoverable with `git show 2dffe3d:scripts/prospectus_golden_check.py`. This phase needs a field-level comparer instead (old code vs new, course fields only), so the script below replaces it. Phase D must not change any extracted course value.

- [ ] **Step 1: Write the comparer**

```python
#!/usr/bin/env python3
"""Phase D regression: course fields are identical between the base commit and this branch.

    python scripts/prospectus_course_compare.py run --which old --repo OLD_TREE --golden DIR --work WORK --semantic-doc MAP
    python scripts/prospectus_course_compare.py run --which new --repo NEW_TREE --golden DIR --work WORK --semantic-doc MAP
    python scripts/prospectus_course_compare.py compare --work WORK

Each *_docling.json is run through `python -m backend.bintanong_tools.prospectus_extractor`
with cwd set to the tree under test, so that tree's package is the one imported.
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
    "standing_requirements", "category", "is_elective", "elective_group",
)
TOP_FIELDS = ("program", "degree", "college", "campus")
NEW_ONLY_FILES = {"candidate_publish.json"}


def run(args: argparse.Namespace) -> int:
    sources = sorted(args.golden.rglob("*_docling.json"))[: args.limit]
    if not sources:
        print(f"no *_docling.json under {args.golden}")
        return 2
    args.work.mkdir(parents=True, exist_ok=True)
    (args.work / "index.json").write_text(
        json.dumps({f"{n:02d}": s.name for n, s in enumerate(sources, 1)}, indent=2), encoding="utf-8")
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONHASHSEED="0")
    for number, source in enumerate(sources, 1):
        out = args.work / args.which / f"{number:02d}"
        out.mkdir(parents=True, exist_ok=True)
        command = [sys.executable, "-m", "backend.bintanong_tools.prospectus_extractor",
                   "-i", str(source), "-o", str(out / "candidate.json"), "--export-all",
                   "--device", "cpu", "--semantic-doc", str(args.semantic_doc)]
        with (out / "run.log").open("w", encoding="utf-8") as log:
            code = subprocess.run(command, cwd=args.repo, env=env, stdout=log,
                                  stderr=subprocess.STDOUT).returncode
        print(f"{args.which} {number}/{len(sources)} exit={code} {source.name}", flush=True)
    return 0


def project(payload: dict) -> dict:
    return {
        "top": {key: payload.get(key) for key in TOP_FIELDS},
        "effective_school_year": (payload.get("metadata") or {}).get("effective_school_year"),
        "audit_status": (payload.get("audit") or {}).get("status"),
        "courses": [{key: course.get(key) for key in COURSE_FIELDS} for course in payload.get("courses", [])],
    }


def compare(args: argparse.Namespace) -> int:
    index = json.loads((args.work / "index.json").read_text(encoding="utf-8"))
    failures = 0
    for number, name in index.items():
        old_dir, new_dir = args.work / "old" / number, args.work / "new" / number
        problems = []
        old_files = {p.name for p in old_dir.iterdir() if p.name not in {"run.log"}}
        new_files = {p.name for p in new_dir.iterdir() if p.name not in {"run.log"}} - NEW_ONLY_FILES
        if old_files != new_files:
            problems.append(f"file set differs: old={sorted(old_files)} new={sorted(new_files)}")
        try:
            old = project(json.loads((old_dir / "candidate.json").read_text(encoding="utf-8")))
            new = project(json.loads((new_dir / "candidate.json").read_text(encoding="utf-8")))
        except (OSError, ValueError) as exc:
            problems.append(f"cannot read candidate.json: {exc}")
        else:
            if old["top"] != new["top"] or old["effective_school_year"] != new["effective_school_year"]:
                problems.append("program/degree/college/campus/school year differ")
            if old["audit_status"] != new["audit_status"]:
                problems.append(f"audit status {old['audit_status']} -> {new['audit_status']}")
            if len(old["courses"]) != len(new["courses"]):
                problems.append(f"course count {len(old['courses'])} -> {len(new['courses'])}")
            else:
                for position, (a, b) in enumerate(zip(old["courses"], new["courses"])):
                    changed = [key for key in COURSE_FIELDS if a[key] != b[key]]
                    if changed:
                        problems.append(f"course #{position} {a['course_code']!r}: {changed}")
                        break
        failures += bool(problems)
        print(f"{number} {'FAIL' if problems else 'ok'} {name}")
        for problem in problems:
            print(f"    {problem}")
    total = len(index)
    print(f"{total - failures}/{total} identical")
    return 1 if failures else 0


def main() -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    sub = cli.add_subparsers(dest="command", required=True)
    runner = sub.add_parser("run")
    runner.add_argument("--which", choices=("old", "new"), required=True)
    runner.add_argument("--repo", type=Path, required=True)
    runner.add_argument("--golden", type=Path, required=True)
    runner.add_argument("--work", type=Path, required=True)
    runner.add_argument("--semantic-doc", type=Path, required=True)
    runner.add_argument("--limit", type=int)
    comparer = sub.add_parser("compare")
    comparer.add_argument("--work", type=Path, required=True)
    args = cli.parse_args()
    return run(args) if args.command == "run" else compare(args)


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Smoke test on one input (expect about 4 minutes)**

```
$REPO = "C:\Users\Hawksprey\source\repos\Bintanong"
$BASE_SHA = git -C $REPO merge-base dev HEAD
git -C $REPO worktree add --detach "$env:TEMP\phase-d-base" $BASE_SHA
$GOLDEN = "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\docling_jsonified_output\task2b_standing_isolated_2026-09-29"
$MAP = "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\PalSU Undergraduate Prospectus Website Dump\Tiniguiban - Main\palsu_main_undergrad_program_college_meaning.md"
$WORK = "$env:TEMP\phase-d-compare"
$PY = uv run --project backend --extra tools --extra dev python -c "import sys;print(sys.executable)"
& $PY scripts\prospectus_course_compare.py run --which old --repo "$env:TEMP\phase-d-base" --golden $GOLDEN --work $WORK --semantic-doc $MAP --limit 1
& $PY scripts\prospectus_course_compare.py run --which new --repo $REPO --golden $GOLDEN --work $WORK --semantic-doc $MAP --limit 1
& $PY scripts\prospectus_course_compare.py compare --work $WORK
```

Expected: `old 1/1 exit=0 ...`, `new 1/1 exit=0 ...`, then `01 ok ...` and `1/1 identical`. Open `$WORK\new\01` and confirm it also contains `candidate_publish.json` (new) and that `run.log` shows no traceback. If the old run fails to import, the worktree needs no environment of its own: the interpreter comes from the main checkout and only the working directory differs. If `candidate.json` is missing in either, read `run.log`.

- [ ] **Step 3: Full run, detached (about 90 minutes per side; old and new run in parallel)**

Background tool calls die after 10 minutes, so launch both detached and poll the logs:

```
Remove-Item $WORK -Recurse -Force
Start-Process pwsh -WindowStyle Hidden -ArgumentList '-NoProfile','-Command',"& '$PY' '$REPO\scripts\prospectus_course_compare.py' run --which old --repo '$env:TEMP\phase-d-base' --golden '$GOLDEN' --work '$WORK' --semantic-doc '$MAP' *> '$env:TEMP\phase-d-old.log'"
Start-Process pwsh -WindowStyle Hidden -ArgumentList '-NoProfile','-Command',"& '$PY' '$REPO\scripts\prospectus_course_compare.py' run --which new --repo '$REPO' --golden '$GOLDEN' --work '$WORK' --semantic-doc '$MAP' *> '$env:TEMP\phase-d-new.log'"
```

Poll every few minutes with `Get-Content "$env:TEMP\phase-d-old.log" -Tail 2; Get-Content "$env:TEMP\phase-d-new.log" -Tail 2` until both show `44/44`. Meanwhile proceed with Task 9 only if it does not use the same CPU heavily; otherwise wait.

- [ ] **Step 4: Compare**

```
& $PY scripts\prospectus_course_compare.py compare --work $WORK
```

Expected final line: `44/44 identical`, exit code 0. Any `FAIL` is a real difference: use superpowers:systematic-debugging, diff `old\NN\candidate.json` against `new\NN\candidate.json` on the named course, and trace the first differing field to a module. The only acceptable differences outside course fields are `run_identity`, `schema_version` (not compared) and the extra `candidate_publish.json`.

- [ ] **Step 5: Clean up and log**

```
git -C $REPO worktree remove --force "$env:TEMP\phase-d-base"
Remove-Item scripts\prospectus_course_compare.py
git status --short
```

Expected: only the two pre-existing untracked/modified items (`.gitignore`, the CODEX handoff). Append to the progress file: date, base SHA, `44/44 identical`, and a note that the comparer is recoverable from this plan (it is not committed).

---



### Task 9: One real end-to-end failure-injection run

**Files:** none (scratch folders under `$env:TEMP`).

This run uses a real PDF and a real Docling conversion, not the fakes. Docling can take several minutes per PDF, so launch the conversions detached.

- [ ] **Step 1: Pick the smallest source PDF and copy it into a scratch input folder**

```
$SRC = "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\PalSU Undergraduate Prospectus Website Dump\Tiniguiban - Main"
$pdf = Get-ChildItem $SRC -Recurse -Filter *.pdf | Sort-Object Length | Select-Object -First 1
$E2E = Join-Path $env:TEMP "phase-d-e2e"
Remove-Item $E2E -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory "$E2E\in","$E2E\out" | Out-Null
Copy-Item $pdf.FullName "$E2E\in\target.pdf"
$CMD = @("--project","backend","--extra","tools","--extra","dev","python","-m","backend.bintanong_tools.prospectus_extractor","-i","$E2E\in","--batch","-o","$E2E\out","--skip-existing","--export-all","--device","cpu","--semantic-doc",$MAP)
```

(`$MAP` as defined in Task 8.)

- [ ] **Step 2: Run A, a real first run (detached)**

```
Start-Process pwsh -WindowStyle Hidden -ArgumentList '-NoProfile','-Command',"uv run $($CMD -join ' ') *> '$E2E\runA.log'"
```

Poll `Get-Content "$E2E\runA.log" -Tail 5` until the line `[*] Batch: ...` appears. Expected: `1 extracted` (or `1 failed audit`; both publish) and a manifest line. Then record hashes of everything except the batch manifest:

```
$before = Get-ChildItem "$E2E\out" -File | Where-Object Name -ne "batch_manifest.json" | Get-FileHash | Select-Object Hash,@{n='N';e={Split-Path $_.Path -Leaf}}
$before | Format-Table
```

Expected files: `target_prospectus.json`, `target_docling.json`, `target_docling.meta.json`, `target_publish.json`, `target_essentials.json`, `target_review.csv` (and `.pl`/`_rag.jsonl` when the audit is not `error`).

- [ ] **Step 3: Run B, unchanged input**

Run the same command in the foreground (it should return in seconds): `uv run @CMD`. Expected: `[*] Batch: 0 extracted, 0 failed audit, 1 skipped, 0 errored.` when run A's audit was `ok`/`warn`. If run A's audit was `error`, expected is `1 failed audit` and no skip; that proves the failed-audit rule on real data, so note it and continue to Step 4 using a PDF that passes (pick the next-smallest) if you also want the identical-files check. Re-hash and compare with `$before`: expected no differences.

- [ ] **Step 4: Run C, failure injection at conversion**

Corrupt the PDF at the same path, then run (detached, as the converter may take time before failing):

```
[IO.File]::WriteAllBytes("$E2E\in\target.pdf", [Text.Encoding]::ASCII.GetBytes("%PDF-1.4 not really a pdf"))
Start-Process pwsh -WindowStyle Hidden -ArgumentList '-NoProfile','-Command',"uv run $($CMD -join ' ') *> '$E2E\runC.log'; `$LASTEXITCODE | Out-File '$E2E\runC.exit'"
```

When `runC.exit` exists: expected `[*] Batch: 0 extracted, 0 failed audit, 0 skipped, 1 errored.` and exit code `1`. Re-hash `$E2E\out` (excluding `batch_manifest.json`) and compare with `$before`: **expected no differences**. Check `Get-ChildItem "$E2E\out" -Force` shows no `.target.staging-*` directory, and that `$E2E\out\failed\target\failure.json` exists with an `error_type` and a traceback. If any earlier file changed, stop and report; that is a Phase D failure.

- [ ] **Step 5: Run D, restore and confirm the skip**

```
Copy-Item $pdf.FullName "$E2E\in\target.pdf" -Force
uv run @CMD
```

Expected: `1 skipped` (identical identity). `failed\target\` is still present: diagnostics are cleared by the next successful processing, not by a skip; note this in the decision record.

- [ ] **Step 6: Log**

Append to the progress file: the PDF file name, the three observed outcome lines, `no differences` for B and C, and the `failure.json` error type. Clean up: `Remove-Item $E2E -Recurse -Force`.

---



### Task 10: Documentation, Codex gate, hand-off

**Files:**
- Create: `docs/decisions/prospectus-cache-and-publication.md`
- Modify: `plans/plan_current_progress/extractor_split_progress.md`, `plans/plan_current_progress/current_progress.md`

- [ ] **Step 1: Write the decision record**

State, in plain sentences: the base commit; the two identities and what is in each; the cache meta format; the publish order, why the manifest is written last (a file-by-file publish is not atomic; hashes make a partial publish detectable), and that `Path.replace` over a file works on Windows while replacing a directory does not, so nothing replaces a directory; what "failure" means and what `failed/<base>/` holds; D1-D6 as implemented; the `run_identity` payload object and the schema bumps; that `--skip-existing` is batch-only; that outputs are now written with LF line endings; that `failed/` is cleared by a later successful publish, not by a skip; that a Docling JSON given as input is a review input and the output says so; and the Task 8 and Task 9 evidence (`44/44 identical`, the observed outcome lines).

- [ ] **Step 2: Full verification**

Run both commands from "Commands used throughout". Expected: full suite green, self-test 80/80. Record the counts.

- [ ] **Step 3: Codex gate (read-only, detached, about 15 minutes)**

```
$prompt = "Review branch feature/prospectus-phase-d-safe-cache against dev in this repo. Claim: the raw Docling JSON cache is reused only when PDF bytes and conversion settings match; process_prospectus stages into a sibling directory and publishes file by file with a hash manifest written last, so a failed run leaves earlier outputs byte-identical; --skip-existing never skips a failed audit, a changed PDF, a changed parser, or a half-published set. Try to break it: find any path where an earlier output is deleted or modified before conversion and audit finish, any Windows-specific failure of Path.replace or rmtree, any case where the manifest passes verification for an inconsistent set, any stale .pl or _rag.jsonl that can look current, any import of prospectus_batch from the package, and any course field that the change could alter. Do not modify files. Report findings with file and line."
Start-Process pwsh -WindowStyle Hidden -ArgumentList '-NoProfile','-Command',"codex exec --sandbox read-only -o '$env:TEMP\codex-phase-d.md' '$prompt'"
```

Poll for `$env:TEMP\codex-phase-d.md`. If Codex is rate-limited or errors, record that in the progress file and continue. Fix each confirmed finding with a failing test first; record unconfirmed ones as skipped with the reason.

- [ ] **Step 4: Log and commit**

Append a dated summary to `extractor_split_progress.md` and a "Phase D" paragraph to `current_progress.md` (branch, commits, counts, Task 8 and 9 results, Codex findings, "next: Phase E").

```
git add docs/decisions/prospectus-cache-and-publication.md plans/plan_current_progress/extractor_split_progress.md plans/plan_current_progress/current_progress.md
git commit -m "docs: record the safe cache and output publication design and its evidence" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

Do not merge into `dev` and do not push; ask the user (superpowers:finishing-a-development-branch).

**Phase D gate:** the cache tests, publish tests, publication tests and skip tests are green; `44/44 identical` on course fields; the real failure-injection run left the earlier files byte-identical and wrote diagnostics; the repeat run of an unchanged input skipped and produced identical files; the full suite and self-test are green; the decision record is written; Codex findings are resolved or recorded.

---

## Self-review

**Spec coverage.**
- Cache identity = PDF hash + conversion-affecting settings (OCR, table mode, cell matching env var, docling/docling-core/docling-parse versions) + parser package hash: Tasks 2 and 4 (conversion identity) and Task 2 and 7 (`run_key` adds the package hash). The device question is D2; the parser-hash split is D1.
- A mismatching cached JSON is ignored and reconverted when the PDF is available: Task 4 (five damage modes, settings change, OCR). Only-JSON input is a review input and the output says so: Task 6 (`review_input_only`, `review_note`, console warning).
- `--skip-existing` compares identity and audit status, never skips a failed audit: Task 7 `skip_check` and its tests.
- `process_prospectus` writes to a temporary sibling directory and publishes only after conversion and audit: Task 6. The old unlink-before-convert code (`pipeline.py:206-213`) is gone.
- Failure leaves earlier outputs byte-identical, diagnostics in `<output dir>/failed/<stem>/`: Tasks 5 and 6 tests; real run in Task 9.
- Windows: file-by-file publication, `replace_file` retry; partial publish handled by the manifest (justified above).
- Tests first, Docling faked at the `loader`/converter boundary and `pipeline.build_payload`: `tests/conftest.py`. One real failure-injection run: Task 9.
- Shared hash helper without an import cycle: `identity.py`, with an AST test.
- OCR room: `conversion_settings(do_ocr, ocr_languages)` is inside the cache identity and tested; `get_shared_converter`'s cache key is flagged for the OCR plan.
- 44-input regression, schema bump, progress file after each task, Codex gate, start check, Phase A gate conditional: Tasks 8, 6, every task, 10, 1.

**Placeholder scan.** No "TBD"/"similar to Task N". The one literal that depends on Phase C (`palsu-prospectus-v3.2`) is declared in "SCHEMA_VERSION change" with the rule for adjusting it and appears in exactly Task 6 step 1 and step 4.

**Type and name consistency.** `file_sha256`, `package_sha256`, `PACKAGE_DIR`, `conversion_settings`, `conversion_identity`, `run_identity`, `IDENTITY_VERSION` (identity.py); `cache_reuse_check`, `_write_bytes_atomic`, `_cache_meta_path` (loader.py); `OutputNames`, `output_names`, `new_staging_dir`, `remove_stale_staging`, `replace_file`, `write_text_lf`, `publish_staged(stage, names, outputs, cache_files, run_identity, audit_status)`, `read_manifest`, `verify_published`, `write_failure`, `clear_failure`, `PUBLISH_SCHEMA` (publish.py); `skip_check(item, config, package_hash)` (batch.py). The tests call exactly these signatures. `load_document(..., stage_dir=)` and `get_pipeline_options(device, settings=)` are the only changed existing signatures; `process_prospectus`'s `force_reconvert` default changes from `True` to `False` (D4).

**Known risks.** The staged-write test stub (`pipeline_state`) bypasses the real parse; the Task 8 real-parse comparison and the Task 9 real conversion cover that gap. Publication is not atomic across files; the manifest makes the failure detectable, not impossible. Single writer per output stem is assumed (stale staging directories of the same stem are removed at the start of a run).
