# Claude-to-Codex continuation log — 4 November 2026

Owner request: continue the interrupted Claude session and record changes for its return.
Recovered session: `b73f3662-df93-4755-8a11-22c52689e6e8` (p12); original compiler task and
approved wording/plan-check tasks read from its local JSONL/subagent records.
Starting p12 HEAD: `968ba2af`. Existing current-progress USG paragraph and `.playwright-mcp/` preserved.

## Authorized work recovered

1. Mixed routing: current model/prompt/wire, deterministic compiler, flag off by default, compare off/on live.
2. Approved conversational host wording and phrase regressions (`p12wd`).
3. Typed-plan/earliest-term backend helpers, then routing hook after compiler integration (`p12pc`).
4. Live gates and existing per-college prompts; push only after an owner instruction.

Wording and plan-check agents were interrupted before editing. Compiler agent committed `2f1153d2`,
with unfinished guard changes in `compile.py`. Those changes were preserved.

## Delivered so far

- `e2b243d6`: finished compiler guards; 15 new regressions. Twelve fail against committed pre-guard code;
  protocol guard separately RED 3 -> GREEN. Focused suite 58 passed.
- `c1b8d40d`: local compiler merge into p12.
- Default-path broad compiler suite before 15 new cases: 2150 passed / 2 xfailed (311 s).
- Source-backed offline memory gate: 15/15 passed. No source ledger/review digest edits.
- [Compiler log](2026-11-04-compiled-routing-continuation.md) records 11 flag-on expectation differences.
- Independent review found four more defects, each reproduced RED: malformed collections escape fallback;
  unknown titles inherit the previous course; repeated topics lose later requested claims; a result statement
  inside a second question part hides a missing operation. Fixed at `a96ea7db`; reviewer rechecked all four.
- `f723e21f`: malformed collection matrix and positive grounded-pronoun coverage; compiler suite 71 passed.
- `22ef3320` integrates approved conversational replies (`4b0277e7`); [wording report](2026-11-04-conversational-wording-results.md)
  records 1187 passed on that branch, including retained either/both/co-requisite semantics.
- `affc3aad` integrates backend typed-plan/earliest-term helpers (`77207f8d`);
  [helper report](2026-11-04-plan-check-replies-results.md) records exact entrypoints and tests. This completes the
  assigned backend half only: routing/generation hookup is still required before advertising either as chat behavior.
- Compiler-branch default broad after the initial 15 cases: 2165 passed / 2 xfailed (363.6 s).
- Live model memory scenarios on compiler branch `e2b243d6`, flag ON: 12/12 checks passed, 9 explanation drafts
  accepted, one rejected with the checked host answer retained. Runtime 7.9–45.2 s per turn; excludes HTTP/browser
  and retrieval. Final integrated branch still needs its live off/on comparison; this is not that final gate.
- Local API restarted on integrated code with compiler OFF; model, frontend and other services left running.
  New API parent PID `79920`; startup log `api-off.log` in the evidence root. Existing launcher PID file may be stale.

Raw outputs: `C:/Coding-projects/bintanong_workspace/audit-evidence/codex-claude-20261104/`.
Python 3.13 (`py -3.13 -B` or existing 3.13 venv), `pytest -p no:cacheprovider`, external basetemp.
No installs, lock/model/dependency edits, push, institutional activation or phase advancement.

## Context and boundaries

Read handoff skills, INDEX/current progress, Phase 12 handoff, relevant master routing/structured sections,
undergraduate scope policy, thesis physical pp. 17–18 and 39–44, and viewed runtime routing PNG.
No active numbered phase; superseded Phase 12 checkpoint stays historical. Preserve read-only undergraduate
advice, scoped self-reported facts, Prolog decision authority, source gaps, F04 hold and English/Taglish replies.

## Current next action

Finish integrated regression run and live flag-off/on conversations/per-college cases. Keep the compiler off until
the comparative evidence supports it. Plan-check/earliest-term chat wiring remains a separate coordinator task;
do not mistake helper delivery for a live feature. Do not re-ask settled wording approval.
