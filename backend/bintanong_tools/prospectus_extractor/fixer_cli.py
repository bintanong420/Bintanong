"""Command line of the year/semester fixer.

    sheet        candidate.json -> review_sheet.md  (flags, proposals, health per section)
    apply        edited review_sheet.md -> decision ledger lines (nothing is written on any error)
    materialise  candidate.json + ledger -> corrected_candidate.json and the content-review state
    status       content-review state from the ledger
    triage       a runs folder -> TRIAGE.md, one line per distinct PDF, healthiest first

Typical review of one prospectus (write the sheet once, then edit it in any text editor):

    1. sheet        creates review_sheet.md next to the candidate. Open it beside the PDF.
    2. (you edit)   per section set `confirm: yes`, or fill the `decision` column of a row:
                    ok | fix | fix a | edit: reason | unresolved: reason
    3. apply        checks the whole sheet; if it is fine, records your decisions. Run it with
                    --dry-run first to only check. It can be run again safely.
    4. materialise  writes corrected_candidate.json. The original candidate is never changed.

Every command needs to know which PDF the candidate came from: pass --pdf FILE (best: it also
turns on the PDF text checks) or --pdf-sha256 HASH.

Sheets, ledgers and corrected candidates hold institutional data. They go in
`<candidate folder>/review/<candidate name>/` by default; the tool refuses to write inside this
repository unless the place is git-ignored. Nothing here approves a curriculum.

Exit codes: 0 done; 1 the sheet has problems (each listed with its line number, nothing was
written); 2 the command could not run (missing file, missing reviewer name, unsafe folder, wrong
options).
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
        return json.loads(Path(candidate).read_text(encoding="utf-8-sig"))
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
    try:
        parsed = parse_sheet(Path(sheet_path).read_text(encoding="utf-8-sig"))
    except OSError as exc:
        raise FixerError(f"cannot read the review sheet {sheet_path}: {exc}") from exc
    errors = check_against(parsed, parse_sheet(render_sheet(payload, verification, expected_identity)))
    entries: list = []
    if not errors:
        reviewer = resolve_reviewer(args.reviewer)
        entries, errors = build_entries(parsed, payload, verification, reviewer=reviewer, pdf_sha256=identity["pdf_sha256"])
    if errors:
        print(f"{len(errors)} problem(s); nothing was written:", file=sys.stderr)
        for message in errors:
            print(f"  {message}", file=sys.stderr)
        return 1
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
    write_corrected(out, corrected, raw_candidate=args.candidate)
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
        rows.append((folder.name, (payload, verify_candidate(payload, pages), Path(record["source"]).name if record else "-"), ""))
    shown = [r for r in rows if r[1] is not None]
    shown.sort(key=lambda r: (HEALTH_ORDER[r[1][1].health], r[0]))
    lines = ["# Review triage", "",
             f"{len(shown)} distinct PDFs, healthiest first. Confirm clean sections in bulk; spend review time on broken ones.", "",
             "| n | program | PDF | audit | health | PDF text | sections clean / review / broken | error and warn flags |", "|---|---|---|---|---|---|---|---|"]
    for name, (payload, v, pdf_name), _note in shown:
        tally = [sum(s.health == h for s in v.sections) for h in ("clean", "review", "broken")]
        flags = ", ".join(f"{k} {n}" for k, n in v.counts().items()) or "-"
        lines.append(f"| {name} | {(payload.get('program') or '').replace('|', '/')} | {pdf_name.replace('|', '/')} | {payload['audit']['status']} | {v.health} | "
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
    for stream in (sys.stdout, sys.stderr):  # titles are not ASCII; a Windows console may not be UTF-8
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    args = build_parser().parse_args(argv)
    try:
        return args.run(args)
    except (FixerError, LedgerError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2