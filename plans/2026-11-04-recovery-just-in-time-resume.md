# Recovery planner continuation, 4 November 2026

Recovered Claude session `b73f3662-df93-4755-8a11-22c52689e6e8`, worker
`ad0a9b711141b8a86`, from its preserved dirty files at `2696bb69`.
Owner decision: the preferred draft follows the demonstrated just-in-time shape,
without program/course constants; retain the earliest summer alternative.

The established identifiers stay honest: A regular offerings, B special classes,
C earliest placement with summer, D preferred just-in-time. The owner's earlier
“Draft B” named the example's shape, not the existing contract's special-only B.
The contract now accounts for exactly four drafted/dropped variants. D is first
by default; an explicit fastest request orders by actual regular-term rejoin.
Identical alternatives are suppressed with their identifier and reason preserved.

Inherited planner changes use reviewed dependency deadlines, keep courses in their
regular offering where possible, and skip summer when reporting rejoin. A course
without dependants needs a special class only if its next regular offering would
finish beyond the curriculum. No program/code constants were introduced.

Scope/routing evidence consulted: undergraduate policy; master structured/Prolog
routing sections; thesis physical pages 17–18 and 39–44; runtime routing PNG.
This remains advisory undergraduate planning over reviewed structured facts and
deterministic checks. Source, offering, approval and unknown-condition limits stay.
No scope/routing discrepancy was found in this slice. No live model/service,
dependency change, deployment, institutional activation or push was performed.

Verification (system Python 3.13, existing audit venv, no pytest cache, ignored
external basetemp under `audit-evidence/p12jit-resume`):

- Fresh inherited `-k no_dependant`: 2 passed, 16 deselected, 4.90s.
- New `-k 'first_draft or earliest_summer'` RED: four expected failures.
  The inherited C silently omitted the earliest-summer alternative.
- After adding D, a test incorrectly expected printed order in summer; actual
  H/J/G correctly preserves next-term dependency priority. Corrected the test.
- Same focused selection GREEN: 4 passed, 14 deselected, 73.21s. Exact preferred
  shape, preserved earliest summer and explicit fastest ordering pass under two
  synthetic course naming schemes. This is not coverage of all real curricula.
- A broader planner run produced no progress during resource pressure and was
  stopped by terminating only its own Python processes. It is not a passing gate.
- `git diff --check` passed. Broader planner/reply regressions remain to run.

Reply continuation: D is explicitly titled preferred / just in time in English
and Taglish. The leading answer uses D's actual regular rejoin term rather than
calling it the fewest-request draft or borrowing C's faster date. Sentence notes
use periods without `.;`; prerequisite-gap details are deduplicated below each
draft table while unknown term outcomes stay visible.

The inherited gap-note fixture discarded all other variants, violating the
existing exact-once validator. It now preserves them and inspects D's table.
After correcting test-only expectations, the three intended reply regressions
failed RED (10.13s). Full reply file GREEN: 11 passed, 23.37s.
The sole `RecoveryResult` constructor in this branch is the planner. Searches
found no other ABC-only variant type or three-draft consumer in backend/frontend.
The coordinator must check its newer plan-view fixtures during integration.

Coordinator integration: `9d260c8d` / `aeddd05c`. Expanded planner/search/reply/API
view gate completed **51 passed / 4 failed in 636.78s**; all four were stale
expectations (C was wrongly expected to disappear; API fixtures assumed A first
or only three variants). Corrected failing selections: **4 passed in 27.31s**;
complete API plan-view file: **10 passed in 9.75s**. Reply file in the integrated
selection: **11 passed** (also in the 20-pass portion of the narrow view/reply run).
The entire long gate was not repeated after those test-only corrections.

Independent integration review also found plan-view fastest selection recomputed
the last moved term instead of using `Draft.rejoin_term`. A new RED returned C
when the checked regular rejoin made D fastest. Ranking now consumes the canonical
regular rejoin; the API gate above verifies GREEN. Display `rejoinAfter` keeps its
existing meaning (the last delayed term), avoiding an API wording change.

No source-backed real-curriculum planner/gold-ledger acceptance run is claimed.
The coordinator owns the remaining conversation/compiler and live topic-switch gate.
