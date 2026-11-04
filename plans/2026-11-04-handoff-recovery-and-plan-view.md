# Handoff: recovery routes, greedy drafts and plan_view (4 November 2026)

Branch `p12-evaluation-harness`, merged (`75e00076`, `173dd27d`) and pushed to origin with `fe8ac24a`. Owner's uncommitted
USG paragraph in `plans/plan_current_progress/current_progress.md` and `.playwright-mcp/` stay untouched.
Git and fresh test runs outrank this note.

## Next action
Both `feat/recovery-routes-more` (`2696bb69` via `75e00076`) and `feat/plan-view` (`b62d021e` via `173dd27d`), plus the dependency completeness fix (`fe8ac24a`), are merged, verified, and pushed to `origin/p12-evaluation-harness`. Next: one backend restart (tell the owner first) and the owner's GUI test of the CC 4/L recovery question.

## Open worktrees (under `C:\Coding-projects\bintanong_workspace\worktrees\Bintanong\`)
| Worktree | Branch | State when written | Scope |
|---|---|---|---|
| `p12rr` | `feat/recovery-routes-more` | 5 commits (b9ab2922..c30027c4) + uncommitted `plan_check_reply.py`, `recovery_reply.py`, `render.py` | Track A clauses, removal/overload/waiver/D7, units a+b, greedy drafts, reply layout, unknown-load wording, Prolog memoization |
| `p12pv` | `feat/plan-view` | no commits; uncommitted `bintanong_api/presentation.py`, `stream.py`, `generation/contracts.py`, `generator.py`, `render.py`, new `tests/test_api_plan_view.py` | typed `plan_view` in the API answer (backend only; owner: frontend later) |

Where each worker stopped (owner usage limit): `p12rr` was updating `removal_lines`/`status_lines` to accept a
`cite`, and the matching call in the plan-check reply; `p12pv` was fixing its test fixtures (the fixture reply is
Taglish, so assert the Taglish note; repair the empty-drafts fixture).

Before relaunching anything: `git -C <wt> log --oneline b57db6a4..HEAD` and `git -C <wt> status --short`. Uncommitted
edits are unverified: run their tests first; never reset or delete them. Both touch `render.py`: expect a merge
conflict; resolve by keeping both changes.

## Remaining items for `p12rr` (owner-approved; ledger 4 Nov entries)
- Owner gold standard, BSCS 2018-2019, CC 4/L failed: 2nd yr 2nd sem = prescribed + special CC 4/L; summer = CS 4/L +
  CS 6 (6 of 9 units); 3rd yr 1st sem = prescribed + special CC 5/L only (major warning 24 vs 21); 3rd yr 2nd sem =
  regular. Must come out as one draft; generic for all curricula (no codes in code); "fastest"/"pinakamabilis"
  names that draft first, still "needs approval". Verify offline with cached ledger
  `C:\Coding-projects\bintanong_workspace\audit-evidence\p12-memory-gates-20261104\ledgers\bscs-2018-2019.json`.
- Units reading (owner decision, ledger): "a/b" = lecture/lab units, total a+b; plain number = total; else unknown.
- Reply layout: 1-2 line direct answer first, `###` sections, one table per draft (Term | Courses | Notes), each
  Handbook clause quoted once in a rules section, approval line once. Chat UI already renders Markdown (`3229e5af`).
- `units_missing` must not print the prerequisite-unknown wording (ARP-04 bsme).
- Speed: offline recovery 30.6 s, 77 Prolog calls at ~0.4 s. Memoize per (course, start-of-term passed set) within
  a run; identical drafts with/without memo (test); measure with `evaluation/planning/run_arp.py` (ARP-01R).
- Do not edit the owner decisions ledger; the router hook for stated status (graduating, last semester, delinquency)
  is reported by the agent, not yet wired.

## `p12pv` contract (backend only)
`plan_view`: `drafts[]` {label, summary {rejoin term, special requests, summer courses, major warnings},
terms[] {label, courses[] {code, mode, needs_confirmation}, load {status, units, ceiling}, notes[]}}, `fastest`;
absent without a recovery result. Built only from checked planner results, never model text.
Adapt the mapping to `p12rr`'s final draft fields after that merge.

## Tests (Python 3.13 venv above, `-p no:cacheprovider`, external `--basetemp` under audit-evidence)
`tests/test_planning*.py tests/test_generation_recovery_reply.py tests/test_plan_route_sources.py
tests/test_plan_chat_pipeline.py tests/test_earliest_chat_pipeline.py tests/test_orchestration_pipeline.py
tests/test_arp_cases.py tests/test_api*.py tests/test_routing_compile.py tests/test_reply_wording_guard.py`;
then the broad suite once after both merges. Last known: routing suite 797 passed; ARP 23 passed; compile 99 passed.

## Live (one model run at a time; RAM was ~1.7 GB free, the gate was killed for memory)
API restart: stop only the PID running `start_hosted_research_api`, then `scripts\start-bintanong.ps1` with
`BINTANONG_ROUTER_COMPILE=1`. Gates: `evaluation/conversations/run_conversations.py`, cases
`audit-evidence\p12-env-20261031\cases-per-college.json`, `cases-understanding.json`, then 116 samples.
Owner GUI prompts: `audit-evidence\p12-env-20261031\per-college-test-prompts.md`.

## Not authorized / pending the owner
No push without the owner's word. Frontend plan view (comparison table + timeline) waits for the owner. Owner still
reviewing 241 prerequisite cells (15 done). Commits: Conventional Commits, explicit staging, no attribution
trailers. Nothing here is institutional approval.
