"""Run the fixed multi-turn conversation set against a running GUI (POST /api/chat). Standard library only.

    python evaluation/conversations/run_conversations.py [--base http://127.0.0.1:3216] [--out DIR] [ids...]

Each conversation gets a fresh session cookie (the server limits one person to 5 questions per 5 minutes), keeps it
across its turns, and backs off on HTTP 429 using Retry-After. Results are research evidence, not institutional approval.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
DEFAULT_OUT = Path(r"C:\Coding-projects\bintanong_workspace\audit-evidence\p12ct-conversations")


def program_id(curriculum_id: str) -> str:
    """abcomm-2018-2019 -> palsu-abcomm; bscs-proposed-2025-2026 -> palsu-bscs (matches the GUI picker's ids)."""
    return "palsu-" + re.sub(r"-proposed$", "", re.sub(r"-\d{4}-\d{4}$", "", curriculum_id))


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\u2019", "'")).casefold()


def check(expect: dict, defaults: dict, reply: str, meta: dict) -> list[str]:
    """Return the failed checks (empty list = pass)."""
    fails, body = [], norm(reply)
    if not body.strip():
        fails.append("empty reply")
    if expect.get("status") and meta.get("status") != expect["status"]:
        fails.append(f"status {meta.get('status')!r} != {expect['status']!r}")
    fails += [f"missing {s!r}" for s in expect.get("required", []) if norm(s) not in body]
    if expect.get("required_any") and not any(norm(s) in body for s in expect["required_any"]):
        fails.append(f"none of {expect['required_any']!r}")
    for s in defaults.get("forbidden", []) + expect.get("forbidden", []):
        if norm(s) in body:
            fails.append(f"forbidden {s!r}")
    return fails


def ask(base: str, text: str, curriculum: str | None, cookie: str | None, timeout: int):
    body = {"messages": [{"id": uuid.uuid4().hex, "role": "user", "parts": [{"type": "text", "text": text}]}]}
    if curriculum:
        body.update(programId=program_id(curriculum), curriculumId=curriculum)
    headers = {"Content-Type": "application/json", "Origin": base}
    if cookie:
        headers["Cookie"] = cookie
    response = urllib.request.urlopen(
        urllib.request.Request(base + "/api/chat", json.dumps(body).encode(), headers), timeout=timeout)
    cookie = (response.headers.get("Set-Cookie") or "").split(";", 1)[0] or cookie
    reply, meta = [], {}
    for line in response.read().decode("utf-8").splitlines():
        if line.startswith("data: ") and line[6:].strip() not in ("", "[DONE]"):
            try:
                part = json.loads(line[6:])
            except ValueError:
                continue
            if part.get("type") == "text-delta":
                reply.append(part.get("delta", ""))
            elif part.get("type") == "data-answer":
                meta = part.get("data", {})
    return "".join(reply), meta, cookie


def ask_with_backoff(base, text, curriculum, cookie, timeout, retries=6):
    for attempt in range(retries + 1):
        try:
            return ask(base, text, curriculum, cookie, timeout)
        except urllib.error.HTTPError as error:
            if error.code != 429 or attempt == retries:
                raise
            wait = int(error.headers.get("Retry-After") or 60) + 1
            print(f"  429, waiting {wait}s", flush=True)
            time.sleep(wait)


def run(case: dict, defaults: dict, args) -> dict:
    cookie, turns = None, []
    for n, turn in enumerate(case["turns"], 1):
        row = {"turn": n, "text": turn["text"], "expect": turn["expect"]}
        started = time.time()
        try:
            reply, meta, cookie = ask_with_backoff(args.base, turn["text"], case["curriculum_id"], cookie, args.timeout)
            row.update(reply=reply, status=meta.get("status"), missingFields=meta.get("missingFields"),
                       fails=check(turn["expect"], defaults, reply, meta))
        except Exception as error:  # a dead server or timeout fails the turn and ends the conversation
            row.update(reply="", status=None, missingFields=None, fails=[f"{type(error).__name__}: {error}"])
        row["seconds"] = round(time.time() - started, 1)
        row["ok"] = not row["fails"]
        turns.append(row)
        print(f"  turn {n} {'PASS' if row['ok'] else 'FAIL'} {row['seconds']}s {row['fails']}", flush=True)
        if row["reply"] == "" and not row["ok"] and row["fails"][0] != "empty reply":
            break
        time.sleep(args.pause)
    ok = len(turns) == len(case["turns"]) and all(t["ok"] for t in turns)
    return {**{k: case[k] for k in ("id", "category", "curriculum_id", "language", "note")},
            "pending": case.get("pending"), "ok": ok, "turns": turns}


def report(results: list[dict], args, stamp: str) -> str:
    live = [r for r in results if not r["pending"]]
    pend = [r for r in results if r["pending"]]
    count = lambda rs: f"{sum(r['ok'] for r in rs)}/{len(rs)}"
    lines = [f"# Conversation set results ({stamp})", "",
             f"Base `{args.base}`. Implemented cases passing: **{count(live)}**. Pending cases passing: {count(pend)} "
             "(reported separately; a failure there is expected until the named track lands).",
             "Research evidence only; not school validation or institutional approval.", ""]
    for title, group in (("Implemented behaviour", live), ("Pending (not yet implemented)", pend)):
        lines += [f"## {title}", ""]
        for r in group:
            tag = f" [pending: {r['pending']}]" if r["pending"] else ""
            lines += [f"### {'PASS' if r['ok'] else 'FAIL'} `{r['id']}`{tag}",
                      f"{r['category']} · {r['language']} · {r['curriculum_id'] or 'no program'} · {r['note']}", ""]
            for t in r["turns"]:
                lines += [f"- Turn {t['turn']} **{'PASS' if t['ok'] else 'FAIL'}** ({t['seconds']}s, status `{t['status']}`, "
                          f"missing `{t['missingFields']}`): {t['text']!r}"]
                if t["fails"]:
                    lines.append(f"  - failed: {'; '.join(t['fails'])}")
                lines += ["  > " + (line or " ") for line in (t["reply"] or "(no reply)").splitlines()[:25]]
            lines.append("")
    return "\n".join(lines)


def safe_out(out: Path) -> Path:
    out = out.resolve()
    if REPO in (out, *out.parents):
        ignored = subprocess.run(["git", "check-ignore", "-q", str(out / "x")], cwd=REPO).returncode == 0
        if not ignored:
            sys.exit(f"--out {out} is inside the repository and not ignored; use audit-evidence or another ignored folder")
    out.mkdir(parents=True, exist_ok=True)
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("ids", nargs="*", help="conversation ids (default: all)")
    p.add_argument("--base", default="http://127.0.0.1:3216")
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p.add_argument("--cases", type=Path, default=HERE / "cases.json")
    p.add_argument("--pause", type=float, default=3.0, help="seconds between turns")
    p.add_argument("--timeout", type=int, default=300, help="per-request seconds")
    args = p.parse_args()
    data = json.loads(args.cases.read_text(encoding="utf-8"))
    cases = [c for c in data["conversations"] if not args.ids or c["id"] in args.ids]
    out, stamp, results = safe_out(args.out), datetime.now().strftime("%Y%m%d-%H%M%S"), []
    for case in cases:
        print(f"{case['id']} ({case['category']}{', pending ' + case['pending'] if case.get('pending') else ''})", flush=True)
        results.append(run(case, data.get("defaults", {}), args))
        (out / f"conversations-{stamp}-partial.json").write_text(json.dumps(results, indent=1, ensure_ascii=False), encoding="utf-8")
    (out / f"conversations-{stamp}.json").write_text(json.dumps(results, indent=1, ensure_ascii=False), encoding="utf-8")
    (out / f"conversations-{stamp}.md").write_text(report(results, args, stamp), encoding="utf-8")
    live = [r for r in results if not r["pending"]]
    print(f"\n{sum(r['ok'] for r in live)}/{len(live)} implemented conversations pass; report in {out}")
    sys.exit(0 if all(r["ok"] for r in live) else 1)


if __name__ == "__main__":
    main()
