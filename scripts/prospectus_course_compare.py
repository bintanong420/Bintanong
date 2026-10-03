#!/usr/bin/env python3
"""Field-level old-versus-new regression for the prospectus extractor.

    python scripts/prospectus_course_compare.py --golden GOLDEN --work WORK \
        [--base-ref 69ca855] [--semantic-doc MAP] [--limit N] [--jobs N] [--no-markup-check]

Runs the extractor from BASE_REF (a git worktree under WORK/../ or --worktree) and from the
current checkout over every *_docling.json under GOLDEN, in parallel, then compares only
course fields and audit counts (never timestamps). The NEW side must also have written a
*_prospectus.md in which every canonical cell appears exactly once (skip with --no-markup-check
for phases that predate the markup twin or that change it deliberately).

Layout: WORK/old/NN and WORK/new/NN each hold source.txt, exit.txt, log.txt, candidate.json
and companions. Later phases extend COURSE_FIELDS / AUDIT_FIELDS or add checks below.
Exit code 0 only when every input matches.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_BASE_REF = "69ca855"  # Phase B base: last commit before the markup twin
COURSE_FIELDS = (
    "course_code", "course_title", "year_level", "semester", "total_units", "lecture_units",
    "lab_units", "prerequisites", "prerequisites_raw", "prerequisites_unresolved",
    "standing_requirements", "category", "is_elective", "elective_group",
)
AUDIT_FIELDS = ("status", "errors", "total_courses", "computed_total_units", "years_detected")


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True).stdout.strip()


def ensure_worktree(ref: str, path: Path, repo: Path = REPO) -> Path:
    """Create (or reuse) a detached worktree of REF at PATH; a reused one must be at REF."""
    path = path.resolve()
    if not path.exists():
        subprocess.run(["git", "worktree", "add", "--detach", str(path), ref], cwd=repo, check=True)
        return path
    wanted, have = _git(repo, "rev-parse", f"{ref}^{{commit}}"), _git(path, "rev-parse", "HEAD")
    if wanted != have:
        sys.exit(f"worktree {path} is at {have[:12]}, not {ref} ({wanted[:12]}); remove it or pick another --worktree")
    return path


def run_one(tree: Path, source: Path, target: Path, semantic_doc: Path | None) -> int:
    tree, source, target = tree.resolve(), source.resolve(), target.resolve()  # the child runs in another cwd
    semantic_doc = semantic_doc.resolve() if semantic_doc else None
    target.mkdir(parents=True, exist_ok=True)
    (target / "source.txt").write_text(str(source), encoding="utf-8")
    extra = ["--semantic-doc", str(semantic_doc)] if semantic_doc else ["--no-semantic-doc"]
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONHASHSEED="0")
    done = subprocess.run(
        [sys.executable, "-m", "backend.bintanong_tools.prospectus_extractor",
         "-i", str(source), "-o", str(target / "candidate.json"), "--export-all", "--device", "cpu", *extra],
        cwd=tree, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    (target / "exit.txt").write_text(str(done.returncode), encoding="utf-8")
    (target / "log.txt").write_text(done.stdout + done.stderr, encoding="utf-8")
    return done.returncode


def run_side(label: str, tree: Path, sources: list[Path], out: Path, semantic_doc: Path | None, jobs: int) -> None:
    def work(item):
        number, source = item
        code = run_one(tree, source, out / f"{number:02d}", semantic_doc)
        print(f"[{label}] {number}/{len(sources)} exit={code} {source.name}", flush=True)

    with ThreadPoolExecutor(max_workers=jobs) as pool:
        list(pool.map(work, enumerate(sources, 1)))


def course_fields(payload: dict) -> dict:
    return {
        "courses": [{f: c.get(f) for f in COURSE_FIELDS} for c in payload["courses"]],
        "audit": {f: payload["audit"].get(f) for f in AUDIT_FIELDS},
    }


def compare_payloads(old: dict, new: dict) -> list[str]:
    """Differences between two payloads in course fields and audit counts."""
    a, b = course_fields(old), course_fields(new)
    issues = []
    if a["audit"] != b["audit"]:
        issues.append(f"audit differs: {a['audit']} != {b['audit']}")
    if len(a["courses"]) != len(b["courses"]):
        issues.append(f"course count differs: {len(a['courses'])} != {len(b['courses'])}")
    for index, (x, y) in enumerate(zip(a["courses"], b["courses"])):
        if x != y:
            issues.append(f"course {index} differs: {sorted(k for k in x if x[k] != y[k])}")
            break
    return issues


def evidence_cell_ids(source: Path) -> list[str]:
    """Cell ids the extractor (this checkout) derives from the cached Docling JSON."""
    sys.path.insert(0, str(REPO))
    from backend.bintanong_tools.prospectus_extractor.loader import evidence_adapter

    evidence = evidence_adapter(json.loads(source.read_text(encoding="utf-8")))
    return [cell.cell_id for table in evidence.tables for cell in table.cells]


def markup_problems(folder: Path, payload: dict, expected_ids: list[str] | None = None) -> list[str]:
    twin = folder / "candidate_prospectus.md"
    if not twin.exists() or twin.stat().st_size == 0:
        return ["missing or empty candidate_prospectus.md"]
    text = twin.read_text(encoding="utf-8")
    status = payload["audit"]["status"]
    problems = []
    if not text.splitlines()[0].startswith(f"<!-- extraction_audit: {status} |"):
        problems.append(f"line 1 does not announce audit status {status!r}")
    found = Counter(html.unescape(i) for i in re.findall(r'data-(?:unplaced-)?cell="([^"]*)"', text))
    expected = payload["evidence"]["canonical_cell_count"]
    if sum(found.values()) != expected:
        problems.append(f"markup has {sum(found.values())} cell elements, evidence has {expected}")
    if expected_ids is not None:
        want = Counter(expected_ids)
        missing, extra = sorted((want - found).elements()), sorted((found - want).elements())
        if missing or extra:
            problems.append(f"markup cell ids differ from evidence: missing {missing[:5]}, extra/duplicate {extra[:5]}")
    return problems


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def compare_runs(old_dir: Path, new_dir: Path, check_markup: bool) -> int:
    folders = sorted(p for p in old_dir.iterdir() if p.is_dir())
    if not folders:
        sys.exit(f"no run folders under {old_dir}")
    failures, gaps, unplaced, largest = 0, 0, 0, 0
    for old in folders:
        new = new_dir / old.name
        issues: list[str] = []
        if not new.is_dir():
            issues.append("missing in new run")
        else:
            if _read(old / "source.txt") != _read(new / "source.txt"):
                issues.append("different source file")
            if _read(old / "exit.txt") != _read(new / "exit.txt"):
                issues.append(f"exit code differs: {_read(old / 'exit.txt')} != {_read(new / 'exit.txt')}")
            before = old / "candidate.json"
            after = new / "candidate.json"
            if _read(old / "exit.txt").strip() not in ("", "0") and _read(new / "exit.txt").strip() not in ("", "0"):
                issues.append(f"both runs failed (exit {_read(old / 'exit.txt')}, {_read(new / 'exit.txt')})")
            if not before.exists() and not after.exists():
                issues.append("neither run wrote candidate.json")
            elif before.exists() != after.exists():
                issues.append("candidate.json exists in only one run")
            else:
                old_payload = json.loads(before.read_text(encoding="utf-8"))
                new_payload = json.loads(after.read_text(encoding="utf-8"))
                issues += compare_payloads(old_payload, new_payload)
                if check_markup:
                    ids = evidence_cell_ids(Path(_read(new / "source.txt")))
                    issues += markup_problems(new, new_payload, ids)
                    twin = new / "candidate_prospectus.md"
                    if twin.exists():
                        text = twin.read_text(encoding="utf-8")
                        gaps += "data-gap" in text
                        unplaced += "data-unplaced-cell" in text
                        largest = max(largest, twin.stat().st_size)
        failures += bool(issues)
        print(f"{old.name} {'FAIL' if issues else 'ok'} {Path(_read(old / 'source.txt')).name}")
        for issue in issues:
            print(f"    {issue}")
    print(f"{len(folders) - failures}/{len(folders)} identical")
    if check_markup:
        print(f"markup: {gaps} files with data-gap, {unplaced} with data-unplaced-cell, largest {largest} bytes")
    return 1 if failures else 0


def main(argv: list[str] | None = None) -> int:
    cli = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    cli.add_argument("--golden", type=Path, required=True, help="folder searched for *_docling.json")
    cli.add_argument("--work", type=Path, required=True, help="output folder (old/ and new/ inside)")
    cli.add_argument("--base-ref", default=DEFAULT_BASE_REF, help="git ref of the old side")
    cli.add_argument("--worktree", type=Path, help="where to put the old worktree (default: temp dir)")
    cli.add_argument("--semantic-doc", type=Path)
    cli.add_argument("--limit", type=int, help="first N inputs only")
    cli.add_argument("--jobs", type=int, default=2, help="parallel extractions per side")
    cli.add_argument("--no-markup-check", action="store_true")
    args = cli.parse_args(argv)

    args.golden, args.work = args.golden.resolve(), args.work.resolve()
    args.semantic_doc = args.semantic_doc.resolve() if args.semantic_doc else None
    sources = sorted(args.golden.rglob("*_docling.json"))[: args.limit]
    if not sources:
        sys.exit(f"no *_docling.json under {args.golden}")
    worktree = args.worktree or Path(tempfile.gettempdir()) / f"bintanong-compare-{args.base_ref}"
    old_tree = ensure_worktree(args.base_ref, worktree)
    print(f"old tree: {old_tree} ({args.base_ref}); new tree: {REPO}; {len(sources)} inputs", flush=True)
    with ThreadPoolExecutor(max_workers=2) as pool:
        sides = [
            pool.submit(run_side, "old", old_tree, sources, args.work / "old", args.semantic_doc, args.jobs),
            pool.submit(run_side, "new", REPO, sources, args.work / "new", args.semantic_doc, args.jobs),
        ]
        for side in sides:
            side.result()
    return compare_runs(args.work / "old", args.work / "new", not args.no_markup_check)


if __name__ == "__main__":
    raise SystemExit(main())
