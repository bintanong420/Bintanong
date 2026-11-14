# Compiled routing continuation (Codex, 4 November 2026)

Resumed Claude's interrupted compiler agent in `p12mx` / `feat/compiled-routing`.
Base implementation: `2f1153d2`; inherited uncommitted `compile.py` guards preserved and completed.
Original task recovered from Claude session `b73f3662-df93-4755-8a11-22c52689e6e8`, compiler agent
`af7c76b94d6e7ccc7`. Owner approved the mixed compiler/current-wire approach and offline agent work.
No numbered phase started; Phase 13 stays cancelled.

## Scope and architecture

Consulted INDEX/current progress, final Phase 12 handoff, master routing/structured sections, undergraduate policy,
thesis physical pages 17–18 and 39–44, and runtime routing PNG. The compiler rebuilds validated dispatch structure;
LLM meaning, reviewed curriculum aliases, Prolog decisions, source gaps and session privacy retain their boundaries.
Current wire/prompt/model unchanged. `BINTANONG_ROUTER_COMPILE=1` opts in; default remains off.

## Changes after Claude paused

- Added synthetic regressions on both unfamiliar curricula for the inherited guards: an unbound second structured
  question cannot disappear; terminal controls stay on the existing parser path; a previous-course quote needs memory;
  offered topics/claims are checked before rebuilding; mentions follow message order with targets/claims remapped.
- Removed one duplicate check in the inherited unbound-part guard.
- Found and fixed acceptance of objects without the current wire protocol version. The compiler now falls back
  instead of manufacturing a clarification from malformed or retired packets.

## Verification so far

Evidence: `C:/Coding-projects/bintanong_workspace/audit-evidence/codex-claude-20261104/`.
System Python 3.13, `-B -m pytest`, `-p no:cacheprovider`, external `--basetemp`.

- Existing compiler suite: 43 passed before additions.
- New inherited-guard tests against committed `2f1153d2` code loaded in-process: 12 expected failures
  (`guard-red.log`); no working-tree files reverted.
- Protocol guard RED: 3 expected failures; GREEN compiler suite: 58 passed.
- Existing routing tests with compilation enabled: 719 passed / 11 failed (`routing-on-final.log`).
  These expectations exercise the old behavior: wrong route remains visible (1), repairing/rejecting guessed
  references (2), refusing authored occurrence slips (1), reference-refusal style paths and their fixed fake call
  budgets (6), and original mention target numbering (1). Expectations were not edited. The fake style transport's
  empty list is an altered call-path assertion, not a model-server observation. These differences are disclosed;
  they do not establish live safety or authorize enabling the switch by default.
- Broad flag-off and source-backed offline gate results pending at this checkpoint.

## Next action

Finish broad regression/source-backed checks, integrate into p12 with the independent approved reply tracks,
then compare live gates with the switch off/on. Keep the compiler off by default until the live evidence supports it.
No push, deployment, source edits or dependency changes authorized by this continuation.
