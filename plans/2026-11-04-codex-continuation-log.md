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

## Account-switch resume (4 Nov, 08:47 onward)

Re-read handoff skills, index/progress, relevant master architecture, thesis physical pp. 17–18 and 39–44,
and routing PNG; phase inspector remains valid with no active numbered phase. Existing owner changes preserved.
Previous API/tests did not survive the account switch; prior partial `integrated-off.log` is incomplete evidence.
New API parent `69468`, compiler OFF, startup 178.7 s; `/health/ready` returned 200. Logs `resume-api-off.*`.

- Reproduced integrated suite failure: obsolete exact wording in `test_new_program_two_turn.py`, not a changed
  decision/memory/source result. `2a4e8247` updates both replies to the approved wording; focused GREEN 1 passed.
- Generation family fresh: 825 passed. Restarted broader suite as `integrated-fixed.log`.
- Full GUI-route conversation baseline OFF running (`conversations-off/`, log beside it).
- Confirmed pending helper defect: a passing plan result can be rendered against a different blocked plan with
  matching curriculum/term count. Original helper agent resumes a request/result digest binding fix in `p12pc`,
  following `69f43e35` checkpoint; not fixed in p12 yet. Earliest-term chain provenance also needs aggregation.
- Chat wiring proceeds separately in `p12-plan-chat` / `feat/plan-chat`, based on `2fa8ffad`, using LLM operations
  and existing adapters. No chat capability claimed until integrated and tested.
- `7b8e2047` integrates the request/policy binding correction (`1909112b`); added incoming historical checkpoint
  to resolve a documentation-only modify/delete cherry-pick conflict. No source-code conflict.
- `dae713c6` integrates earliest-term chain provenance (`c3ff35fb`), including rejection of mixed release scopes.
  The renderer must receive `result.checked_request` after the adapter injects owning-session facts.
- `d73fdbcf` repairs stale index wording: D1–D7 are settled in the owner plan; no new phase authorized.
- Duplicate coordinator planning focus runs (`binding-integrated`, `planning-fixed`) stopped before results
  to reduce concurrent load; not counted as verification. Reviewer owns the current focused recheck.
- Broad pre-chat-wiring regression (`integrated-fixed.log`): 2238 passed / 2 xfailed / 2 inherited dependency
  deprecation warnings, exit 0, 426.45 s. Planning fixes were integrated while this process was running;
  use their independent focused run for current-code evidence rather than treating this as a final frozen gate.
- Independent planning recheck: 70 passed / exit 0 in 221.44 s, covering `test_planning_chat.py`,
  `test_planning_earliest_provenance.py`, `test_planning_recovery.py`, `test_generation_recovery_reply.py`.
  Reviewer confirmed both fixes and existing recovery compatibility; v1 serialized plan results intentionally refused.
- GUI-route baseline OFF completed: 30/30 implemented conversations, 32/35 including pending-labelled cases.
  Failures: shifting transfer-units follow-up asks transfer direction; hotel-track follow-up omits Hotel;
  recovery Ask message becomes generic clarification, then summer follow-up unavailable. Bare program cases pass.
  Results and each turn retained under `conversations-off/`; do not erase pending failures behind 30/30 headline.
- API restarted for compilation ON comparison, parent PID `67244`, logs `compare-api-on.*`. Model/frontend unchanged;
  comparison uses the existing prompt (chat-plan prompt changes intentionally held out to isolate switch effect).
- First ON startup failed reading a hosted ledger (`StorageError: Storage transport request failed`), before
  inference. Retry parent PID `81880`, `compare-api-on-retry.*`, ready after 147.71 s. Initial health watcher
  timed out across the failed start; replacement watcher launched `conversations-on/` after retry readiness.
- Track-switch oracle limitation discovered by reading both cached reviewed BSHM ledgers: HMPE 5 requires THC-LA
  in Culinary AND Hotel. The fixture note incorrectly says Hotel has THC-RM and its second-turn assertion merely
  requires the word Hotel. Preserve original run and failure; missing Hotel is not proof of a wrong scope.
  A follow-up check must observe actual resolved scope/memory isolation, not invent a different prerequisite.
