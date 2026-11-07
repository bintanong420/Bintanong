# PR20 compound and recovery follow-up

Owner authorized implementation after the [three-risk audit](2026-11-07-pr20-three-risk-check.md).
Worktree `p12-pr20`, feature branch `feature/p12-unified-answer-pipeline`; staging3218/API8023
only. Evaluation and p12-dev checkouts, source data, dependencies and model/context settings
remain unchanged. No numbered phase, merge or institutional activation.

## Changes

- Router v27 replaces the fictional one-check example with two distinct eligibility targets
  plus a documentary part, including an abbreviated second question. Exact quote/target and
  part guards remain. Redundant instructions were condensed to retain8192 context support.
- A Filipino live trace now supplies both operations but groups them into one quoted question.
  The compiler separates exactly two explicit eligibility targets sharing that span, using
  distinct literal target spans. It neither creates a missing operation nor broadens the
  executor; the existing compiler default remains OFF, staging override remains ON.
- Explicit fastest/earliest-return/as-soon-as-possible and selected Taglish equivalents reach
  the existing planner's `fastest_asked` option. Narrow negated preference phrases retain the
  default. This is request ordering only, not a new route or institutional rule. Generic
  curriculum-scoped planner reuse; default just-in-time DraftD remains owner-approved.
- Fastest headline says earliest **projected among generated drafts**, not a proven optimal
  or feasible schedule. Approvals, offerings, load warnings and unknown checks retain limits.
- Host recovery formatting now exposes sections shared by legacy full Markdown and V2.
  Primary draft, assumptions, affected subjects, standing/removal restrictions, term warnings
  and adviser notice stay visible. Other drafts, documented options and complete quotations
  use labelled native details/summary controls. No HTML source injection or Markdown directives.
- Python/SSE/Zod/React agree on bounded labelled details blocks. Warnings cannot acquire a
  collapse title. Missing printed labels or invalid/oversized presentation falls back to the
  full validated text. Copy/legacy text remains complete; planView stays disabled.

## Verification so far

- RED observed for missing fastest-intent forwarding, one-part/two-target compiler shape,
  absent recovery view, disclosure rendering and overconfident fastest wording; then GREEN.
-9 preference/chat scope cases pass, including two unrelated synthetic curricula.
-148 compiler/compound tests pass, including two synthetic shared-span regressions.
-22 compound pipeline/recovery presentation tests pass, including visible unknown/load
  limits, full text fallback, hidden alternatives/quotes and bounded disclosure validation.
- Frontend106 tests pass; after adding disclosure transport checks, focused16 pass.
  TypeScript and production Next16.4.3 Webpack build pass using existing Node24.21 dependencies.
  Known standalone tracing warnings arise from reused external node_modules; no packaging fix.
- Final router/API/compound gate1,120 passes after both compiler corrections. Broader
  recovery/plan-view gate90 passes in407.22s. These overlap other gates; do not sum them.
- Live router: Taglish now supplies two distinct correctly bound parts without repair. Filipino
  supplies both targets; compiler correction is covered offline, full staging check pending.
  Recovery token probe7325 input+768 output+8 guard=8101, under8192. Probe deliberately raises
  after counting; its synthetic diagnostic is not a model-execution failure.

Raw evidence stays under ignored `audit-evidence/pr20-local-staging-20261107` and named
external pytest basetemps. Docker Desktop/model were found stopped and existing instances
restarted under prior owner authorization. Full staging reload/live verification follows
verified commits; no availability assertion is inferred from historic PIDs or traces.

## Combined-candidate follow-up

Staging code651ce26d passed live English17.52s, Taglish15.64s, Filipino16.45s two-check
requests and English mixed Hybrid24.08s, with2/2/2/3 separately cited V2 parts. Filipino
and Taglish input replies were Taglish. These are spot checks, not whole-language acceptance.
The exact recovery question still failed17.05s: the model emitted redundant same-course
operations and invalid part grouping; its repair exceeded context. Existing recovery normalization
ran too late, after span compilation/normalization had already refused the structure.
Reuse that same normalization before compiler span construction for a recovery-only request
with no separately requested documentary topic or previous-course reference. No new operations,
grades or policy rules. Two synthetic RED regressions reproduce the malformed shape;185 related
checks pass after correction. Exact live router now validates with no repair at7326 input tokens. On staging API code
`a34c10c6`, the exact question answers through the frontend proxy in40.02s, English, with V2.
DraftC is named earliest projected among the generated drafts (3rd-year1st-semester), with
feasibility/approval qualification. Visible view458 words versus full copy/fallback1,642 words
(72.1% reduction), one primary draft and3 labelled disclosures. Unknown prerequisite checks
remain visible. PrimaryC has no load warning in this result; the alternativeD's load warning
remains in that expanded draft. Source IDs remain attached. No actual browser paint timing.

## Delivery and remaining acceptance

Code commits: `7002c43e` (router example/preference), `651ce26d` (progressive view/shared-span
compiler), `a34c10c6` (early existing recovery normalization). Staging API loads `a34c10c6`,
frontend production build includes651ce26d. Evaluation checkout and p12-dev remain untouched.
Automated model calls stop after the bounded checks; owner can test http://localhost:3218/chat.

Next: owner exploratory review of the primary draft and disclosures; retain full independent
acceptance, real browser390px/desktop keyboard/screen-reader checks and paired compiler OFF/ON
language evaluation before merge. No global optimality, all-curriculum live accuracy, latency
improvement or RTX3050/16GB fit claim. Context remains8192, compound default OFF, planView OFF.
The earlier bounded model-only keepalive does not establish indefinite server availability.
