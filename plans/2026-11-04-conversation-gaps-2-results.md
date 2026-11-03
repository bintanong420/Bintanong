# Four conversation fixes (offline)

Worktree `p12cx`, branch `fix/conversation-gaps-2`, base `8a4a89b8`.
No active numbered phase; Phase 13 remains cancelled. No services called, started or stopped; no push.

## Context and scope

Read AGENTS, handoff skills, INDEX/current progress, latest Phase 12/common-query handoffs,
master sections 3 and 23, owner ledger 3–4 November and memory/eligibility plan.
Consulted thesis physical pp. 17–18 and 39–44 using installed system Python/PyMuPDF, and viewed
the runtime routing PNG. Venv lacks PDF readers; no packages installed. Undergraduate, advisory,
English/Taglish, scoped session facts and unknown/unmet boundaries remain applicable.

Evidence root (read only):
`audit-evidence/p12-common-queries-20261030/run-63c6e3a4-codex-evidence/`.
Tests contain synthetic courses/programs and fake transports only.

## Bug 2: bare program name

`cx-bare-bscs/call-2-result.json` and `cx-bare-cs/call-2-result.json` both declare zero parts
but include one unknown placeholder. Wire parsing rejected the count before `bare_program_name`.
Accept only that non-executable placeholder mismatch; keep actual action/topic count checks.
Regression recreates the recorded wire shape using Program A and checks one-attempt clarification.
RED: 1 failed/4 passed (`invalid_model_output`). GREEN: bare-name + wire suites, 40 passed.

## Bug 1: standalone results

`cx-statement/call-2-result.json`: RAG label, structured statement without an operation, and a course
quote including its final period. Validation only acknowledged control=clarify; exact aliases also failed
on the final period. `cx-statement-fil/call-2-result.json`: zero-count unknown placeholder (Bug 2), with
an omitted course mention (already repaired by the normalizer).
Accept a fully grounded, asserted, statement-only message before operation validation regardless of
the proposed route. Require complete claim coverage, no question mark or documentary part. Strip trailing
punctuation only to a reviewed alias, preserving a complete alias if it already exists. Existing
`accepted_facts`/ChatTurns persistence needs no new memory path. Acknowledgements use existing per-state
English/Taglish wording, one line per course/state. Friend reports and hypothetical results stay unacknowledged.
RED: both recorded shapes failed, plus the chat acknowledgement; multiline rendering and exact-punctuation
alias regressions each failed before their corrections. GREEN: related suites 145 passed; final focused 116 passed.
Separately quoted results joined with and/at/but/pero/saka/tapos are still a standalone statement: a further
regression failed on the unclaimed joining word, then passed after allowing only those joining words between
the grounded claims. Final affected routing/API/rendering gate: 143 passed (cx-final-targeted).
The chat regression verifies stored self-report provenance, next-turn context and an actual synthetic
Prolog eligibility verdict with no missing prerequisite fact.

## Bug 3: shifting with a reason

`cx-shift/call-2-result.json` targets BSIT as a course while listing it as a program. Existing topic-slip
repair removes that operation, but leaves the invalid failed-course claim. The next router request records
`invalid_course_quote_reference`; call 3 changes to an empty clarify. Drop only claims attached to the
noncourse target of the already-discarded topic operation. A program in a document-only shifting request
is its destination, not a conflicting selection of the student's curriculum. The shifting topics,
FAQ companion and printed-office referral remain unchanged. RED: invalid_reference; GREEN: routing,
wire, topic selection, validation and shifting generation suites 149 passed.

## Bug 4: eligibility track switch

`cx-trackswitch/integration.json` contains a release-stage hold and no model calls, so it cannot establish
a router refusal. Code inspection confirms `switch_program_follow_up` only accepted term operations.
Extend it to eligibility/missing-prerequisite checks using the previous course. `research_catalog` now supplies
an optional reviewed printed `course_code` separately from aliases (which include titles and initials).
Resolve that code in the destination curriculum, using its own course ID; never match a shared title or carry
facts from the old curriculum. No course returns the existing reviewed-course-not-found clarification;
duplicate course codes ask which course; multiple tracks retain program_choice. Term behavior stays covered.
RED: 4 failed/7 passed. GREEN: track/follow-up/contracts 43 passed; catalog/follow-up/private conversation 66 passed.
Runtime catalog tests also assert that the printed code survives construction.
Cross-layer review found the orchestrator still merged the original request's facts after the router switched
scope: constructing the new scoped RequestContext failed before symbolic dispatch. An additional regression
failed with zero symbolic calls, then passed after filtering the original facts by the resolved program/curriculum.
All orchestration suites plus track switch, runtime catalog, API chat and standalone results: 184 passed
(cx-track-orchestration-green). This belongs to the same Bug 4 commit.

## Verification commands

Python: `C:/Coding-projects/bintanong_workspace/audit-evidence/p12-env-20261031/venv/Scripts/python.exe`.
All pytest commands use `-p no:cacheprovider --basetemp C:/Coding-projects/bintanong_workspace/audit-evidence/p12cx-bt/<name> -q`.
Bug 2: `tests/test_routing_bare_program_name.py` (cx-bare-red2); then that file plus
`tests/test_routing_wire.py` (cx-bare-green). `git diff --check` passed.
Bug 1: standalone + API chat regression (cx-facts-red); multiline renderer (cx-facts-lines-red);
exact punctuation alias (cx-alias-red). Related GREEN cx-facts-green2, 145 passed.
Bug 3: `tests/test_routing_shifting_reason.py` (cx-shift-red2); plus wire, validation, topic selection,
shifting companion/referral suites (cx-shift-green), 149 passed.
Bug 4: `tests/test_routing_program_switch.py` (cx-track-red); plus follow-up/contracts (cx-track-green), 43 passed.
Final focused files: standalone, runtime research catalog, API chat turns, generation student facts,
program switch, shifting reason, bare program name, wire (cx-all-fixes): 116 passed.

Read-only replay of all five available recorded call-2 packets through wire parsing, normalization and
validation (using injected test aliases, no service/model/rule execution) produced:
both bare names -> bare_program_name; both statements -> facts_noted; shifting -> validated/RAG.

## Requested suites and environment limits

Requested files selected with PowerShell `Get-ChildItem tests/test_*.py` and name regex
`^test_(routing|private_context|api|orchestration|request|topic|generation|term|new_program|planning|conversation)`.
Initial baseline ran before product edits: 5 worker failures and 18 setup errors, then cleanup failed
with WinError 5 and suppressed the normal summary. The supplied baseline (2021 passed, 2 xfailed plus
31 planning) was not reproducible in this sandbox. The baseline collection totals 2024 for this exact selector;
the final collection totals 2039 (15 added cases). Planning contributes 31, not an additional run's distinct tests.
Baseline counts reconstructed from that collection and its progress output: 1999 passed, 2 xfailed,
5 failed, 18 errors; this is not an intact terminal summary.
First full post-fix run (cx-final): 2011 passed, 2 xfailed, 5 failed, 18 errors (2036 cases, before the last
exact-alias case was added). All five failures were `test_private_context_worker.py` denied Windows pipes;
18 tmpdir setup errors were API research composition (2), API research factory (15), generation evaluation (1).
Cleanup again failed with WinError 5. A temporary reporting hook printed counts before that cleanup; it is
removed before delivery and did not change test behavior. Final code's affected suites passed separately.
First restricted run excluded three whole files plus the one evaluation case: 2004 passed, 2 xfailed,
1 deselected (cx-final-unrestricted). That omitted 8 healthy cases along with the blocked cases, so it is
superseded by the exact-node run below. Do not present it as coverage of every unblocked test.
Exact-node run excluding only the 23 sandbox-blocked cases: 2013 passed, 2 xfailed, 23 deselected
(cx-final-exact), before the final joining-word correction. Final code with exactly those exclusions:
**2014 passed, 2 xfailed, 23 deselected**, exit 0 (cx-final-verified, 174.98 seconds).
Separate planning verification: 31 passed (cx-planning); these are included in the requested combined suite too.

## Commit/recovery boundary

No commits could be created: explicit `git add <paths>` failed creating
`C:/Users/Hawksprey/source/repos/Bintanong/.git/worktrees/p12cx/index.lock` with Permission denied.
Read-only ACL inspection shows explicit deny-write entries on the metadata directory. No ACLs changed,
no alternate Git metadata/repository used, no staged changes, no push. HEAD remains `8a4a89b8`.
Once the coordinator has normal Git access, split the shared wire/validation hunks into four bug commits:

- `fix(routing): clarify bare program wire placeholders`
- `fix(conversation): acknowledge and remember standalone results`
- `fix(routing): answer shifting questions with failure reasons`
- `fix(conversation): repeat eligibility checks across tracks`

## Next action

Coordinator splits the four bug commits and runs the 23 environment-blocked tests and live checks with
normal Git/process permissions. Do not repeat completed offline setup. Offline success does not establish
live accuracy or school approval. `phase_state.py validate` and final `git diff --check` passed.

## Coordinator audit (Claude, 4 Nov 2026)

- Committed as one commit (`e9efcfc5`), not four: the fixes share hunks in wire.py and validation.py and non-interactive
  hunk splitting was not available; the commit message names all four. Codex's current_progress.md edit was left out
  (the file carries an uncommitted owner paragraph on p12).
- Full requested suites with normal permissions, including the 23 sandbox-blocked cases: 2065 passed, 2 xfailed, 0 failed.
- Regression strength: the five changed/new test files run against the pre-fix code (`8a4a89b8`) give 18 failed /
  32 passed; on the fix all pass.
- Code review: the wire placeholder exception is narrow (zero declared parts, one empty unknown part, no operation,
  topic or claim); the dropped claim must target both a discarded operation and a program/curriculum mention; the
  punctuation trim applies only when the trimmed text is a reviewed alias and the untrimmed one is not; facts_noted
  requires every claim asserted, no "?", no document part and no unclaimed words besides joining words, so friend,
  hypothetical and question messages are not saved. The orchestrator change fixes a real cross-curriculum fact leak
  after a track switch (facts are filtered to the resolved scope).
- Notes, not defects: the shifting destination rule names the two shifting topic ids in validation.py (same pattern as
  existing topic companions); a course missing from the switched track renders the existing "not among the reviewed
  courses of your curriculum" text, which reads slightly off for another track.
- Live (`ca82cc22`): all 30 implemented conversations pass; bare program name and the eligibility track switch now
  work; open: the shifting follow-up "ilang units ang mate-transfer?" routes to transfer credentials, and the Filipino
  bare-name follow-up "yung subjects" fails.
