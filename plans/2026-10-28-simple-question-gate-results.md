# Simple-question gate: first run results

28 October 2026, code `23e83aa` (detail-only answers included). 91 cases (owner accepted the coverage in principle the
same day): 32 Handbook/Charter in English and Taglish, 12 single-detail Charter, 6 course listings, 35 prerequisite
cases across 14 curricula plus BSCS, 2 controls. One attempt each, against the real inactive 559 package and hosted
curricula, read-only. Codex B's full suite ran at the same time, so the timings are not latency evidence.
Evidence (ignored): `workspace/audit-evidence/p11-simple-gate-20261028` (`build_cases.py`, `cases.json`, `run_gate.py`, `run-*/`).

**Automatic score 58/91. Three failures are my over-strict expectations, not system errors** (summer load
answered the "normal load" of 9 units as asked; Taglish leave says "isang (1) academic year"). **Adjusted: 61/91.**
The gate requires 91/91, so it has not passed.

Course listings (6/6), the English "can I take X if I failed Y" checks, prerequisite lists across all 14
curricula, the courses with no reviewed rule (never invented), and the greeting all pass.

## Failure causes (30 real)

| Cause | Cases | What happened |
| --- | ---: | --- |
| A. Wrong topic or claim chosen | 15 | Drop subject went to DAC policy, not the FAQ steps; probation went to discipline, not standing; certification fee went to TOR copy; transfer went to the Handbook, not the Charter table; diploma, DAC and overdue fine picked a not-stated/limit claim instead of the printed fields; honors residence picked the general residence clause; Law admission was answered as general admission (should be an undergraduate-scope notice); 2 temporarily unavailable |
| B. Right topic, no answer | 6 | Second-year classification, substitution deadline, refund requirements (en): insufficient or abstained although the printed text answers them |
| C. Taglish "hindi ko pa naipapasa" dropped | 7 | "Pwede ko bang kunin ang X kahit hindi ko pa naipapasa ang Y?" keeps the course check but drops the not-passed statement, so the result is unknown instead of ineligible (English "if I failed Y" passes in all 7 curricula) |
| D. Detail falls back to the whole table | 2 | Admission-test fee and TOR-copy time were labelled correctly, but the slice exceeds one claim, so the renderer fell back to the full service |

## Next, test-first

C and D first (deterministic, 9 cases), then A (selection, largest group), then B. Each fix gets a RED
regression on synthetic fixtures before the change, then the gate is rerun.

## Run 2 and follow-up fixes

Run 2 (`e193093`): **67/91, adjusted 70/91** (was 61). C fixed 7/7 (router v24: not yet passed / not taken is a
failed claim, meaning not completed); D fixed 2/2 (detail answers split within claim limits, phase headings kept).
No regressions. Diagnosis then moved honors residence, probation and refund requirements from B into A (wrong topic).

Follow-ups, each test-first, live-checked on the affected cases:
- `a6bc52a`: a single-detail part no longer needs whole-procedure record coverage (substitution deadline now passes
  in both languages).
- `2189faf`: owner-resolved source limits (owner 28 Oct 2026: year-level percentages shown as printed, no note).
- Latest commit: `specific` detail (one printed fact or rule) plus a no-clarify-for-missing-personal-details line.
  "When am I considered a second-year student?" now answers as printed. Its Taglish form still returns an empty
  router clarify, the same family as the earlier shifting clarify. Recorded, not retried further (stop rule).

Next: group A (topic or claim selection, about 18 cases), then a full gate rerun and full suite.
