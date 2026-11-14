# Phase 09 exit reassessment

22 October 2026, at `998b1d5`. Read-only mapping of later evidence onto the
[21 October exit map](2026-10-21-phase09-remaining-work-and-exit-map.md); no model run.
Author assessment of developer cases, not independent or institutional gold.

## Written exit gate (master 14, Phase 09 plan)

| Requirement | Evidence | State |
| --- | --- | --- |
| Contradictory, fabricated-citation, wrong-version, unsupported-claim drafts rejected | Regression suite; full suite at `e53153b`: 6097 passed, 6 skipped, 0 failed (945 s) | Met (software) |
| Regeneration terminates after one repair | Same suite; per-part path keeps one repair | Met |
| Final output preserves symbolic status | Real Janus CC5 `ineligible` kept in en/fil/taglish (roster runs 3-6); fixture Hybrid h-en, b1, b2 | Met |
| Honest multilingual observations incl. residual failures | Per-part, broader b1-b6, roster runs 1-6 (63 accepted cases x en/fil/taglish) | Met, with limits below |

## The four quality holds from the reopening

| Hold (21 Oct map) | Later evidence | State |
| --- | --- | --- |
| Requested operation/identity (unrequested prerequisite op) | Task-first 4/4 interpretation; router reference errors now clarify (`c8a25f5`); roster run 3+: 0 system errors; all 18 no-context course questions clarify as expected | Resolved on observed cases |
| Complete question requirements (coalesced parts) | Per-part generation: 4/4 complete content (d-en fee fixed); pre-enrollment-first-step-tl answers all five requested details from Charter p.102 | Resolved on observed cases |
| Relevance beyond source support | b5/b6 unrelated questions withheld; per-student fee wrong answer (run 2) removed in run 5 (`d8d5220`): 0 wrong answers | Resolved, at a disclosed cost |
| Omissions the router never declares | No independent check exists; only declared parts are guaranteed. No observed silent omission in run 5's 10 answered document cases | Open: disclose as a limitation |

## Latest real-data result (run 5, `d8d5220`; run 6 style fixes on top)

63 cases: 13 answered, 26 clarification, 24 insufficient evidence; 0 wrong answers,
0 invented facts, 0 system errors. Of 18 document cases with reviewed fields, 10 answered
and 8 withheld (3 fee-example answers lost to the router's per-person reading; pre-enrollment
en/taglish withheld because the router added an unrequested deadline detail). Warm backend
timing: document answers median 32.2 s, Prolog answers 20.4 s, max 39.4 s.

## Limitations to carry if closed

1. Undeclared-part omissions are not independently detected.
2. All-or-nothing answers: one unavailable part withholds the verified parts (follow-up design).
3. Router over-reads: per-person amounts (3 fee-example answers withheld) and added details.
4. Style: some Taglish questions are labelled Filipino (model choice); floor stops English-only.
5. Latency: warm component only, 20-39 s; no student end-to-end, browser, Supabase or cold-start
   measurement; the 15-20 s target is unmet and unvalidated.
6. Retrieval uses the read-only PackageStorage stand-in, not hosted Supabase.
7. Inherited: candidate-only output, no institutional release/activation, university
   approval pending, F04 held, if/kung policy held, research-only real-data use.

## Recommendation

Close Phase 09 as an owner-approved offline research/software milestone with the
limitations above, as was done for Phases 05-08. Further accuracy gains now need router
changes (per-person and added-detail errors) or the partial-answer design, which fit
better as named follow-ups than as more Phase 09 loops within the one-week cap
(started 19 October). Latency levers stay optional follow-up work. Closing needs the
owner's explicit approval; this reassessment does not close the phase.
