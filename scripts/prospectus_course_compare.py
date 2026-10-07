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
import statistics
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
# --- Phase C: opt-in status-field report (--status-report). Self-contained so later phases can merge cleanly. ---


def _key_diff(old, new, path=()):
    """Yield (kind, path) for every added, removed or changed key; equal-length lists are compared by item."""
    if isinstance(old, dict) and isinstance(new, dict):
        for key in sorted(old.keys() | new.keys()):
            if key not in new:
                yield "removed", path + (key,)
            elif key not in old:
                yield "added", path + (key,)
            else:
                yield from _key_diff(old[key], new[key], path + (key,))
    elif isinstance(old, list) and isinstance(new, list) and len(old) == len(new):
        for index, (a, b) in enumerate(zip(old, new)):
            yield from _key_diff(a, b, path + (index,))
    elif old != new:
        yield "changed", path


def _key_name(path) -> str:
    parts = ["[]" if isinstance(part, int) else str(part) for part in path]
    if parts[0] == "curriculum_by_term" and len(parts) >= 3:
        parts[1] = parts[2] = "*"
    if parts[0] == "unlocks" and len(parts) >= 2:
        parts[1] = "*"
    return ".".join(parts)


def _without_noise(payload: dict) -> dict:
    payload = {k: v for k, v in payload.items() if k != "generated_at"}
    clauses = (payload.get("prolog") or {}).get("clauses")
    if clauses:
        payload["prolog"] = {**payload["prolog"], "clauses": [c for c in clauses if not c.startswith("% Generated:")]}
    return payload


def payload_key_changes(old: dict, new: dict) -> Counter:
    """Counter of (kind, normalised key path) for one payload pair, ignoring run-to-run timestamps."""
    return Counter((kind, _key_name(path)) for kind, path in _key_diff(_without_noise(old), _without_noise(new)))


def status_report(old_dir: Path, new_dir: Path) -> dict:
    """Added, changed and removed payload keys over every pair of run folders, plus new-side prerequisite states."""
    changes: Counter = Counter()
    states: Counter = Counter()
    pairs = 0
    for old in sorted(p for p in old_dir.iterdir() if p.is_dir()):
        before, after = old / "candidate.json", new_dir / old.name / "candidate.json"
        if not (before.exists() and after.exists()):
            continue
        old_payload = json.loads(before.read_text(encoding="utf-8"))
        new_payload = json.loads(after.read_text(encoding="utf-8"))
        pairs += 1
        changes += payload_key_changes(old_payload, new_payload)
        states.update(c.get("prerequisite_state", "absent") for c in new_payload.get("courses", []))
    return {"pairs": pairs, "changes": changes, "states": dict(states)}


def print_status_report(report: dict) -> None:
    print(f"status report over {report['pairs']} payload pairs")
    for (kind, name), number in sorted(report["changes"].items()):
        print(f"  {kind:8} {number:>6}  {name}")
    print(f"  prerequisite states (new side): {report['states']}")


# --- Phase E: corpus gate report (--corpus-report). Read-only over a finished run folder. ---

TITLE_REASON = "title_not_in_source_text"
CAP_REVIEW_TOKENS = 480  # 512 less the 32-token reserve; estimate-v1 review metadata, not a tokenizer count
sys.path.insert(0, str(REPO))
from backend.bintanong_tools.prospectus_extractor.text import BANNER_WORDS as _EXTRACTOR_BANNER_WORDS  # noqa: E402

# The extractor's own year/semester banner vocabulary (lower-cased), not a second copy.
BANNER_WORDS = {w.lower() for w in _EXTRACTOR_BANNER_WORDS}
# Broader than the extractor on purpose: this report also names a rejected title's extra token when it is a
# total/units column word or an abbreviation that the section parser does not treat as a banner.
EXTRA_MARKER_WORDS = {"total", "totals", "subtotal", "grand", "yr", "units", "unit"}
ORDINAL = re.compile(r"\d+(st|nd|rd|th)")


def _is_marker_token(token: str) -> bool:
    """A banner word, a total/units word, an ordinal, or a token with no letters (a footnote or row digit)."""
    word = token.strip(".,:;()[]").lower()
    return (not any(ch.isalpha() for ch in word) or word in BANNER_WORDS or word in EXTRA_MARKER_WORDS
            or bool(ORDINAL.fullmatch(word)))


def classify_title(claimed: str, printed: str) -> tuple[str, str]:
    """(group, extra): how a rejected claimed title differs from the printed own-title cells."""
    if printed and claimed in printed:
        extra = " ".join((printed.replace(claimed, " ", 1)).split())
        if extra and all(_is_marker_token(t) for t in extra.split()):
            return "printed_equals_claim_plus_token", extra
        return "other", extra
    if printed and printed in claimed:
        return "claim_longer_than_cell", " ".join(claimed.replace(printed, " ", 1).split())
    return "other", ""


def _median_stats(values: list[int]) -> dict:
    values = sorted(values)
    return {"count": len(values), "min": values[0], "median": statistics.median(values), "max": values[-1]}


def corpus_gate(run_dir: Path) -> dict:
    """Source-gate statistics over RUN_DIR/NN/candidate.json. Nothing is written or changed."""
    sys.path.insert(0, str(REPO))
    from backend.bintanong_tools.prospectus_extractor.chunking import canonical_text
    from backend.bintanong_tools.prospectus_extractor.rag import printed_own_fields

    folders = sorted(p for p in run_dir.iterdir() if p.is_dir())
    blocked, failed, files, details = [], [], [], []
    totals, reasons, other_rejected = Counter(), Counter(), Counter()
    layout_reasons, groups, kinds, anchored = Counter(), Counter(), {}, Counter()
    table_files, with_chunks, over_cap = 0, 0, 0
    for folder in folders:
        name = Path(_read(folder / "source.txt")).name or folder.name
        candidate = folder / "candidate.json"
        if _read(folder / "exit.txt").strip() not in ("", "0") or not candidate.exists():
            failed.append({"input": name, "exit": _read(folder / "exit.txt").strip() or "missing"})
            continue
        payload = json.loads(candidate.read_text(encoding="utf-8"))
        audit, rag = payload["audit"], payload["rag"]
        if audit["status"] == "error":
            blocked.append({"input": name, "errors": len(audit.get("errors") or []),
                            "rejections": len(rag["rejected_chunks"]),
                            "chunks": len(rag["semantic_chunks"]) + len(rag["hierarchical_chunks"])})
            continue
        courses = payload["courses"]
        chunks = rag["semantic_chunks"] + rag["hierarchical_chunks"]
        with_chunks += bool(chunks)
        for chunk in chunks:
            kinds.setdefault(chunk["chunk_type"], []).append(chunk["token_count"])
            anchored[str(bool(chunk["source_anchored"])).lower()] += 1
            over_cap += chunk["chunk_type"] in ("course", "term_schedule") and chunk["token_count"] > CAP_REVIEW_TOKENS
        accepted = sum(c["chunk_type"] == "course" for c in rag["semantic_chunks"])
        by_reason, layout = Counter(), []
        evidence = [i for s in audit["curriculum_sections"] for i in s.get("evidence_cells") or []]
        for r in rag["rejected_chunks"]:
            if r["chunk_type"] == "course":
                by_reason[r["reason"]] += 1
                if r["reason"] == TITLE_REASON:
                    match = [c for c in courses if (c["course_code"], c["year_level"], c["semester"]) ==
                             (r["course_code"], r["year_level"], r["semester"])]
                    match = [c for c in match if (c["provenance"] or {}).get("source_cell_ids") == r["source_cell_ids"]] or match
                    claimed = canonical_text(match[0]["course_title"]) if match else ""
                    _, printed = printed_own_fields(match[0], audit["table_layout"], evidence) if match else (None, {})
                    printed = printed.get("title", "")
                    group, extra = classify_title(claimed, printed)
                    groups[group] += 1
                    details.append({"input": name, "course_code": r["course_code"], "claimed": claimed,
                                    "printed": printed, "group": group, "extra": extra})
            elif r["chunk_type"].startswith("hierarchical"):
                layout_reasons[r["reason"]] += 1
                layout.append({"label": r["label"], "reason": r["reason"], "refs": r["source_refs"],
                               "token_count": r.get("token_count")})
            else:
                other_rejected[f"{r['chunk_type']}:{r['reason']}"] += 1
        table_files += any(x["reason"] == "over_token_cap" and any(ref.startswith("#/tables/") for ref in x["refs"])
                           for x in layout)
        rejected = sum(by_reason.values())
        files.append({"input": name, "audit_status": audit["status"], "courses": len(courses),
                      "accepted": accepted, "rejected": rejected, "rejected_by_reason": dict(sorted(by_reason.items())),
                      "unaccounted": len(courses) - accepted - rejected, "layout_rejections": layout})
        totals.update(courses=len(courses), accepted=accepted, rejected=rejected,
                      unaccounted=len(courses) - accepted - rejected)
        reasons.update(by_reason)
    pct = f"{100 * totals['rejected'] / totals['courses']:.1f}" if totals["courses"] else "0.0"
    return {
        "inputs": len(folders), "blocked": blocked, "failed_runs": failed, "files": files,
        "totals": {"emitting_files": len(files), "courses": totals["courses"], "accepted": totals["accepted"],
                   "rejected": totals["rejected"], "rejected_pct": pct, "unaccounted": totals["unaccounted"],
                   "rejected_by_reason": dict(sorted(reasons.items()))},
        "title_groups": dict(sorted(groups.items())),
        "title_details": sorted(details, key=lambda d: (d["input"], d["course_code"], d["claimed"])),
        "layout": {"rejected_by_reason": dict(sorted(layout_reasons.items())), "emitting_files_with_table_over_cap": table_files},
        "other_rejected_by_type": dict(sorted(other_rejected.items())),
        "chunk_statistics": {"inputs_with_chunks": with_chunks, "anchored": {"false": anchored["false"], "true": anchored["true"]},
                             "by_type": {k: _median_stats(v) for k, v in sorted(kinds.items())},
                             "over_cap_course_or_term": over_cap},
    }


def render_corpus_gate(report: dict) -> str:
    t, out = report["totals"], []
    out.append(f"CORPUS GATE: {report['inputs']} inputs; {len(report['blocked'])} blocked audit, "
               f"{t['emitting_files']} not blocked, {len(report['failed_runs'])} failed runs")
    out.append(f"\nBLOCKED AUDIT ({len(report['blocked'])}): no chunks, no rejections (reported apart)")
    out += [f"  {b['input']}  errors={b['errors']} chunks={b['chunks']} rejections={b['rejections']}" for b in report["blocked"]]
    out.append(f"\nFAILED RUNS ({len(report['failed_runs'])})")
    out += [f"  {f['input']}  exit={f['exit']}" for f in report["failed_runs"]]
    out.append("\nPER FILE (not blocked): accepted / rejected / courses")
    for f in report["files"]:
        why = ", ".join(f"{k}={v}" for k, v in f["rejected_by_reason"].items()) or "none"
        out.append(f"  {f['input']}  [{f['audit_status']}]  {f['accepted']} / {f['rejected']} / {f['courses']}"
                   f"  unaccounted={f['unaccounted']}  rejected by reason: {why}")
    out.append(f"\nTOTALS over {t['emitting_files']} not-blocked files: courses {t['courses']}, accepted {t['accepted']}, "
               f"rejected {t['rejected']} of {t['courses']} ({t['rejected_pct']}%), unaccounted {t['unaccounted']}")
    out += [f"  {k}: {v}" for k, v in t["rejected_by_reason"].items()]
    out.append(f"\nTITLE REJECTIONS BY GROUP: {report['title_groups']}")
    out += [f"  [{d['group']}] {d['input']} {d['course_code']}: claimed={d['claimed']!r} printed={d['printed']!r} extra={d['extra']!r}"
            for d in report["title_details"]]
    out.append(f"\nLAYOUT REJECTIONS: {report['layout']['rejected_by_reason']}; "
               f"not-blocked files that lost a table chunk as over_token_cap: {report['layout']['emitting_files_with_table_over_cap']} "
               f"of {t['emitting_files']}")
    for f in report["files"]:
        out += [f"  {f['input']}  {x['label']}  {x['reason']}  tokens={x['token_count']}  refs={x['refs']}"
                for x in f["layout_rejections"]]
    out.append(f"\nOTHER REJECTIONS (terms, overview, electives): {report['other_rejected_by_type']}")
    s = report["chunk_statistics"]
    out.append(f"\nCHUNKS: inputs with chunks {s['inputs_with_chunks']}; anchored {s['anchored']}; "
               f"course/term chunks over {CAP_REVIEW_TOKENS} estimated tokens: {s['over_cap_course_or_term']}")
    out += [f"  {k}: {v}" for k, v in s["by_type"].items()]
    return "\n".join(out) + "\n"


def write_corpus_report(run_dir: Path, out: Path) -> dict:
    """Write OUT (text) and OUT with a .json suffix, both LF and sorted, from RUN_DIR; returns the report."""
    report = corpus_gate(run_dir)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(render_corpus_gate(report).encode("utf-8"))
    out.with_suffix(".json").write_bytes((json.dumps(report, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    return report


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
    cli.add_argument("--status-report", action="store_true", help="also list added/changed/removed payload keys and prerequisite-state counts")
    cli.add_argument("--corpus-report", type=Path, help="also write the corpus gate report (text and .json) of the new side here")
    args = cli.parse_args(argv)

    if args.corpus_report:  # refuse before any run: the report is derived from institution data
        from backend.bintanong_tools.prospectus_extractor.fixer_cli import FixerError, assert_outside_git
        try:
            for target in (args.corpus_report, args.corpus_report.with_suffix(".json")):
                assert_outside_git(target)
        except FixerError as error:
            sys.exit(str(error))
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
    status = compare_runs(args.work / "old", args.work / "new", not args.no_markup_check)
    if args.status_report:
        print_status_report(status_report(args.work / "old", args.work / "new"))
    if args.corpus_report:
        write_corpus_report(args.work / "new", args.corpus_report)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
