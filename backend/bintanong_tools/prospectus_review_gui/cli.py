"""Command line of the prospectus review GUI.

    python -m backend.bintanong_tools.prospectus_review --candidate CANDIDATE.json --pdf ORIGINAL.pdf

Opens one candidate for review in your browser. The server listens on 127.0.0.1 only (there is no option to listen
anywhere else; use an SSH tunnel for remote use) and stops with Ctrl+C. Answers go into the same decision ledger
as the review sheet: `<candidate folder>/review/<candidate name>/decision_ledger.jsonl` by default, never inside
this repository unless the place is git-ignored. The candidate and the PDF are only read. Nothing here approves a
curriculum.

Exit codes: 0 stopped normally; 2 could not start (missing file, missing reviewer name, unsafe folder, wrong PDF,
port in use, ledger in use by another tool).
"""

from __future__ import annotations

import argparse
import socket
import sys
import webbrowser
from pathlib import Path
from typing import Sequence

from ..prospectus_extractor.fixer_cli import (
    FixerError, default_review_dir, load_candidate, resolve_identity, resolve_reviewer,
)
from ..prospectus_extractor.ledger import LedgerError

LOOPBACK = "127.0.0.1"
DEFAULT_PORT = 8765


def build_parser() -> argparse.ArgumentParser:
    cli = argparse.ArgumentParser(prog="prospectus_review", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    cli.add_argument("--candidate", type=Path, required=True, help="candidate.json (the *_prospectus.json output)")
    cli.add_argument("--pdf", type=Path, help="the original PDF: gives the hash, the page images and the PDF text checks")
    cli.add_argument("--pdf-sha256", help="hash of the original PDF when the file is not at hand (no page images then)")
    cli.add_argument("--golden", type=Path, help="run folder with isolated_manifest.json, to look the PDF up")
    cli.add_argument("--pdf-root", type=Path, help="folder searched for the PDF named in the manifest")
    cli.add_argument("--docling-json", type=Path, help="raw Docling JSON for the markup twin (default: the path the candidate recorded)")
    cli.add_argument("--review-dir", type=Path, help="default: <candidate folder>/review/<candidate name>")
    cli.add_argument("--reviewer", help="default: git config user.name")
    cli.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"port on {LOOPBACK} (default {DEFAULT_PORT}; 0 picks a free one)")
    cli.add_argument("--no-open", action="store_true", help="do not open the browser")
    return cli


def bind_loopback(port: int) -> socket.socket:
    """A listening socket on 127.0.0.1 only. OSError when the port is taken."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        if sys.platform != "win32":   # on Windows SO_REUSEADDR would let a second program take a port in use
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((LOOPBACK, port))
        sock.listen(64)
    except OSError:
        sock.close()
        raise
    return sock


def make_server(app):
    import uvicorn

    return uvicorn.Server(uvicorn.Config(app, log_level="warning", access_log=False))


def run_server(app, sock: socket.socket) -> None:
    """Serve on the bound socket until Ctrl+C (uvicorn stops on the signal and returns)."""
    make_server(app).run(sockets=[sock])


def review_main(argv: Sequence[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):  # titles are not ASCII; a Windows console may not be UTF-8
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    args = build_parser().parse_args(argv)
    if not 0 <= args.port <= 65535:
        print("error: --port must be from 0 to 65535", file=sys.stderr)
        return 2
    try:
        from .app import create_app, new_token
        from .session import open_session
    except ImportError as exc:
        print(f"error: the review GUI needs the `review` extra ({exc.name} is missing): uv sync --extra review --extra tools",
              file=sys.stderr)
        return 2
    try:
        payload = load_candidate(args.candidate)
        identity = resolve_identity(payload, pdf=args.pdf, pdf_sha256=args.pdf_sha256, golden=args.golden, pdf_root=args.pdf_root)
        reviewer = resolve_reviewer(args.reviewer)
        review_dir = args.review_dir or default_review_dir(args.candidate)
        session = open_session(args.candidate, identity, reviewer, review_dir, pdf_path=identity.get("pdf_path"),
                               docling_json=args.docling_json)
    except (FixerError, LedgerError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    try:
        try:
            sock = bind_loopback(args.port)
        except OSError:
            print(f"error: port {args.port} is in use on {LOOPBACK}; pass another --port, or 0 for any free port", file=sys.stderr)
            return 2
        try:
            port = sock.getsockname()[1]
            url = f"http://{LOOPBACK}:{port}/"
            state = session.state()
            print(f"Reviewing {state['program'] or args.candidate.name} as {reviewer}")
            print(f"  ledger: {session.ledger_path}")
            print(f"  twin:   {session.twin()['reason'] or 'markup twin ready'}")
            print(f"  open {url}   (Ctrl+C to stop)", flush=True)
            app = create_app(session, new_token(), port=port)
        except Exception as exc:   # a startup failure after the bind: release the port, no traceback
            sock.close()
            print(f"error: the review tool could not start ({type(exc).__name__}: {exc})", file=sys.stderr)
            return 2
        if not args.no_open:
            webbrowser.open(url)
        run_server(app, sock)
    finally:
        session.close()
    return 0
