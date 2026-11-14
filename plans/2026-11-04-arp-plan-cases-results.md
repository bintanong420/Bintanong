# ARP-01..ARP-10 plan-check cases and timing split (Step 6) — 4 Nov 2026

Offline only: no model, backend, GUI or server was started. Cases are in `evaluation/planning/arp_cases.json`, the runner is
`python -m evaluation.planning.run_arp --ledgers <dir> --out <dir>`, and the tracked test is `tests/test_arp_cases.py`
(synthetic data plus a well-formedness check). The real-ledger run used the 39 reviewed curricula cached at
`audit-evidence/p12-memory-gates-20261104/ledgers` through `CurriculumRuntime.for_offline_research` (the research
authorization of `research_app.AUTHORIZATION`) and the reviewed `palsu-load-policy-v1` / `palsu-recovery-routes-v1`.
Raw output: `audit-evidence/arp-20261104/arp-results.json` (untracked; includes every rendered reply).
This is development evidence on reviewed research data, not school validation.

## Results (16 cases, 0 failures, 0 premise gaps in the case premises)

Expectations were written from the printed prerequisite structure of each ledger before the first run. Two were wrong and
were corrected after hand-checking the ledger, not the output: ARP-03's co-requisite Math 11/L, once passed, counts as met
(only Math 12/L blocks); and ARP-03/04 need `Math 12/L not_passed` stated, because a planned course with no stated result is
"completion unknown", not "unmet".

| Case | Curriculum | What was asked | Verdict per term (prerequisite and approval view) | Result |
| --- | --- | --- | --- | --- |
| ARP-01 | bscs-2018-2019 | CC 1/L, 2/L, 3/L, CS 1/L passed. Special CC 4/L (2nd yr 2nd sem), summer CS 4/L, special CC 5/L (3rd yr 1st sem) | all three terms "works, needs confirmation": CC 4/L, CS 4/L, CC 5/L each "requested, not confirmed" with the Handbook p. 37 / p. 35 clauses quoted | pass |
| ARP-01R | bscs-2018-2019 | Recovery after failing CC 4/L (2nd yr 1st sem) | dependency closure = CC 5/L, CS 4/L, CS 6, CS 7/L, CS 10/L, 11/L, 13/L, 14/L, 15/L, 16/L, 17/L, 18/L, CS 19 (hand-derived from the ledger, equal to Prolog's list); drafts A/B/C produced | pass |
| ARP-02A | bscs-proposed-2025-2026 | Passed CC 5/L; CS 6/L, CS 10/L not passed; CS 13/L in 3rd yr 2nd sem | blocked by CS 6/L and CS 10/L (own structure; the old CC 5/L rule is not borrowed) | pass |
| ARP-02B | bscs-2018-2019 | Same facts on the old curriculum | works (CS 13/L needs only CC 5/L) | pass |
| ARP-03 | bsce-2018-2019 | Math 11/L passed, Math 12/L not passed, Math 12/L + Phy 11/L in 1st yr 2nd sem | blocked by Math 12/L | pass |
| ARP-04 | bsme-2018-2019 | Identical facts and plan | works (Math 11/L is the prerequisite, Math 12/L a same-term co-requisite) | pass |
| ARP-05A | bsa-2018-2019 | VT-3/L passed; ACAD-1/L (3rd yr 2nd sem) then ACAD-2/L (4th yr 1st sem) | works, works | pass |
| ARP-05B | bsa-2018-2019 | AD-2/L passed (similar name), ACAD-1/L not passed; both ACAD courses in one term | blocked by ACAD-1/L; ACAD-1/L also "off-semester, requested, not confirmed" | pass |
| ARP-06A | bsn-2018-2019 | NCM15-101A, 101B, 102A passed; 102B not passed; NCM 15-103 | blocked by NCM15-102B only (all four parts preserved) | pass |
| ARP-06B | bsn-2018-2019 | Everything named for NCM 15-107A passed | unknown: the printed prerequisite "NCM 15-105B" is not a course in the reviewed curriculum | pass |
| ARP-06C | bsn-2018-2019 | Summer NCM 15-116 B, five printed prerequisites passed | works, needs confirmation (summer requested, not confirmed) | pass |
| ARP-07 | bsba-buseco-2018-2019 | GE-PC not taken; BE 2001 then BAC 5 | BE 2001 blocked by GE-PC; BAC 5 works (reviewed None) | pass |
| ARP-08 | bsed-math-2018-2019 | FS 2 and Ed 12 (broad "all ... Prof. Ed. and Specialization" cells) | unknown, unknown; never a positive verdict | pass |
| ARP-09A | bsmid-2019-2020 | Assess 2nd year 1st sem | `not_covered`, covered terms listed (3rd and 4th year only) | pass |
| ARP-09B | bsmid-2019-2020 | Earliest term for Mid Res 1 from 3rd yr 1st sem | unknown, no term invented | pass |
| ARP-10 | synthetic (QZV codes, fictional policy) | 3-term plan on unfamiliar codes | works (load within), blocked by QZV-B1/L, unknown for QZV-K10/L; unchanged checker and replies | pass |

## Premise gaps and findings

1. **Unit load cannot be checked on real data.** Only 3 of 39 ledgers carry any `units.total` (abpolsci, bsed-valed, bspsych-io,
   2 courses each); the rest print `units.printed` (for example "3/1") only. Every real-ledger term therefore has outcome
   `unknown` with load "units not printed for every course", and the `heads_up` (load above prescribed) and `within` verdicts
   are exercised only on the synthetic curriculum. ARP-01's "load reported" part is a premise gap. Totals were not derived
   from lecture/lab values (no unit/lab finding is made here); the owner would have to say how they are read.
2. **Reply wording defect (not fixed; outside this task).** A term with a missing unit total gets the "I can't fully check the
   prerequisites of X" line and the headline "Unknown", even when the prerequisite check was decided (ARP-04: all prerequisites
   met, reply headline Unknown; ARP-01 likewise). The cause is the `units_missing` reason being rendered with the
   `prereq_unknown` words in `backend/bintanong_generation/plan_check_reply.py`. The runner keeps this visible by reporting
   `term_outcome` and `units_missing` next to the prerequisite verdict. The same reply also prints one "can't fully check"
   line per reason, so a course with two reasons gets two lines.
3. **ARP-06 clinical/RLE offering restrictions:** the ledgers hold prerequisite rules and printed units only; the checker can
   say only "requested, not confirmed". The "restrictions block certainty" premise is not in the reviewed data.
4. **ARP-09 coverage:** for Midwifery `list_term_courses` returns status `complete` with no courses for years 1 and 2, so
   `check_plan` and `earliest_term` have no explicit coverage-gap signal; only `assess_term` reports `not_covered`. The
   earliest-term result is safely `unknown`, but its reason is `prerequisite_chain_unresolved_within_five_years`, not a
   coverage gap, and it assumes the 8 listed earlier courses passed.
5. Architecture is `bsa-2018-2019` (program `palsu-bsa`). All other ARP curricula were present with the named course codes.

## Timing split (offline, warm, one run per case)

`time.perf_counter` around the existing calls, wrapping the runtime so each method's time is added up (no production code
changed). Stage definitions: **Prolog** = `runtime.check` and `runtime.list_affected_courses` (each starts a Prolog worker
process); **lookup** = `runtime.look_up` on the reviewed ledger (Python); **planner** = the rest of `check_plan` /
`earliest_term` / `plan_recovery` (control flow, memo, contract parsing); **render** = the host reply lines
(`plan_check_lines`, `earliest_term_lines`, `recovery_lines`). Runtime build (bundle preparation) is separate.

| Case | Stage | Total s | Prolog s (calls) | Lookup s (calls) | Planner s | Render s | Runtime build s |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ARP-01 | plan check, 3 terms | 1.42 | 1.37 (3) | 0.04 (8) | 0.004 | 0.002 | 1.00 |
| ARP-03 | plan check, 1 term, 2 courses | 0.87 | 0.83 (2) | 0.04 (7) | 0.002 | 0.0001 | 1.15 |
| ARP-06A | plan check, 1 term, 1 course | 0.63 | 0.52 (1) | 0.10 (6) | 0.005 | 0.0002 | 2.26 |
| ARP-02A | plan check, 1 term, 1 course | 0.47 | 0.44 (1) | 0.03 (6) | 0.002 | 0.0001 | 0.87 |
| ARP-10 | plan check, synthetic, 3 terms | 2.12 | 2.10 (5) | 0.01 (13) | 0.003 | 0.0002 | 0.45 |
| ARP-09B | earliest term, Midwifery | 8.85 | 8.81 (21) | 0.01 (5) | 0.031 | 0.0 | 0.35 |
| ARP-01R | recovery, 3 variants | 30.63 | 30.00 (77) | 0.39 (75) | 0.238 | 0.0002 | 1.00 |

All 16 rows are in `arp-results.json`. Reading: Prolog worker processes are about 0.4 to 0.5 s per check, so a plan check
costs roughly 0.45 s per planned course; planner and reply rendering are under 1 percent. The recovery draft set is the
expensive path: 77 Prolog checks, 30.6 s here (the memo already avoids repeats), which alone exceeds the 15–20 s warm
student-visible proposal in `Context/response-time-recommendation.md` before any Gemma time is added.

**Excluded, not measured here:** Gemma router and generation time (comes from the live runner's `integration.json` timings),
HTTP/stream, browser, network, Supabase, queueing, cold start, first-call model warm-up. Numbers are one run on this
machine, not a distribution, and not a student-visible latency.

### Warm backend turn times from the existing live conversation runs

Source: `audit-evidence/codex-claude-20261104/conversations-on*/` and `conversations-off/` (the JSON holds one
`seconds` per turn, the whole warm backend request through `ChatTurns.answer`, including router, Prolog, generation and
validation; no router/generation split is recorded, and browser/network/Supabase are excluded). Whole sets: conversations-on
67 turns, median 12.4 s, range 6.6 to 47.3 s; conversations-off 67 turns, median 13.4 s, range 7.1 to 28.7 s. The on/off
labels are the directory names; what the flag changes was not verified here.

| Turn (conversations-on) | Seconds | Status |
| --- | --- | --- |
| dsa-failed 1: "What subjects ang hindi ko matake if nabagsak ko DSA?" (dependency list) | 10.3 | answered |
| recovery-ask 1: failed DSA, "ano pwede ko itake para maging regular" (recovery drafts) | 47.3 | answered |
| recovery-ask 2: "paano kung summer?" | 13.3 | clarification_needed |
| live-scenarios term 1: "I failed CC 3/L and CC 4/L. What can I take next sem?" | 14.1 | clarification_needed |
| live-scenarios term 2: "second year, second sem" | 21.6 | answered |

No conversation in these files is an explicit "Check my plan" turn, so a warm Gemma+plan-check turn time is not available;
the recovery turn (47.3 s total) against the 30.6 s offline recovery computation suggests roughly 17 s for router,
generation and validation, but that subtraction compares different runs and is an inference, not a measurement.
