# Current progress

Updated 24 October 2026. Phase 11 active (backend only, owner direction); resumed after the 24 Oct pause.
Worktree p11 / branch `feat/p11-backend-api` from `dev` `cbaa6a7`, nothing pushed.
[Plan](../phase-11-backend-api-plan.md) | [Checkpoint](../phase-11-checkpoint.md) |
[Pre-phase research](../2026-10-23-phase-11-pre-phase-research.md) | [Phase 10 handoff](../phase-10-handoff.md).
Last full snapshot before this replacement: `0e4e4f1:plans/plan_current_progress/current_progress.md`.

## Latest changes (24 Oct, Claude Code session)

- Security review done ([report](../2026-10-24-phase-11-security-review.md)); fixes S1, S2, S4-S8 committed; full
  suite at `72ec6d4` 6441 passed, 0 failed. Next.js advisories wait for UI integration (owner).
- Owner decisions: answer queue of 1 running + 4 waiting, then 503 `answers_busy` (`d1d416c`); PSU Google sign-in
  via Supabase Auth with a server-side `psu.palawan.edu.ph` check and one question per account, built with the
  UI integration; off-topic requests refused. Recorded as master section 25.
- Live abuse probe: off-topic, injection and secret-extraction questions refused, 0 leaks; one misleading
  "temporarily unavailable" refusal fixed (`5ee7b50`). Live capacity: one slot serves students in arrival order.
  Six at once: five answered by 76.8 s, the sixth got busy at once, no errors.
- Step 2 finding E1 fixed (`7c3786e`, owner choice): questions outside the 7 reviewed topics (leave of absence,
  transcript) now say the topic is not in the reviewed sources yet and refer to the university office.

- E3 fixed (`05f34d2`, owner chose office referral): a model "clarify" that names nothing now gets the E1 "not in
  reviewed sources, ask the office" reply; live 4/4 shifting questions. One covered Taglish pre-enrollment case also
  gets the referral (disclosed).
- 2a fixed (`9c09ac7`): overload questions the model checked as a course now answer from the overload topic
  (live: typo and one-word forms answered, matching Handbook table 6).
- 2b-2e (`467aa9d`, `9e3c5b0`, `8f15471`, `1f510dd`): prerequisite lists when no grade is stated (owner "List
  for both"), course-not-found reply, units -> referral, every chosen topic retrieved (full suite at `874f0c9`).
- [Security measures inventory](../2026-10-24-security-measures-inventory.md) for thesis Chapter IV (owner request).

- e2 done (owner decisions 24 Oct): special class fee host reply `c2ef61a` (printed rate + printed example +
  own charge not stated + referral, all languages, no model call); multi-part partial answers `0046b4d` (covered
  parts answered, a declared-unavailable part named with a referral; fee parts in mixed messages keep the host
  reply). Live: 3 fee questions and both overload + fee messages answered. Selection 1401 passed, 2 xfailed.

## Next action

Handoff point (owner asked for /clear). Course facts (step 2h) for all 39 curricula with hosted upload: owner
readings CF1-CF5 recorded; dry run done and verified (2132 courses; only source-error total mismatches).
Items 1-3 done (`6814775`; 39 ledgers with facts authored and regression-checked, untracked). Course facts live (R10/R6/title/year/fil/Taglish answered); hosted
upload verified; roster 18 regressions fixed (fee currency `ee3c61e`, route from parts `3094f14`, owner 25 Oct);
full suite at 01d8db2 0 failed. Reply wording approved (owner, 25 Oct). Owner 25 Oct: finish
non-UI step-2 items first; simple questions must not fail (simple-query battery to follow). f done (thanks, Cebuano,
referral); g decided (Handbook p.46); hosted insert APPROVED for the whole p.46 undergraduate table.
HANDOFF (owner /clear, 25 Oct): resume at checkpoint step 2 item g "NEXT ACTION" (build grading readings, embed,
rehearse, hosted insert, live check), then the remaining step-2 items and the simple-query battery. Owner CF6 + spot-check accepted (25 Oct); hosted upload after the wiring. Parked: Hybrid next-step part without a topic; full suite after `0046b4d`.

## Boundaries

Undergraduate scope, read-only advisory, source-gap, privacy, institutional release and one-week improvement
boundaries are unchanged. No grade or conversation persistence. No activation, push, training or DB change.
No dependency change without an owner decision. Context consulted 23 Oct: thesis physical 17-18 and 65-66, plus
the routing PNG; 25 Oct resume: physical 17-18 and the PNG again (referral/unavailable wording). No discrepancy.
