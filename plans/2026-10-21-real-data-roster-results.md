# Real-data roster results (owner-authorized research mode)

21 October 2026. Protocol: [roster protocol](2026-10-21-real-data-roster-protocol.md).
Stack: reviewed Phase 05 package (19 chunks) via read-only PackageStorage, real
SEA-LION-E5 encoder, real Gemma 4 E4B (CUDA, ctx 8192, out 768, temp 0), real
SWI-Prolog/Janus with reviewed BSCS ledgers, `parts` generation. One attempt per
case per run. Author reading against the printed sources; not an accuracy rate,
independent test or student-visible latency. Raw: workspace
`audit-evidence/p09-real-data-20261021/roster{,2}/results.jsonl`.

## Run 2 (code `a5111f1`: compact source cards, thought-opener ban, printed codes)

| Group (n) | Correct behaviour | Wrong | System errors |
| --- | --- | --- | --- |
| Document, facts available (18) | 10 answered correctly; 3 withheld, 3 clarification | 0 | 1 routing, 1 repair-exhausted |
| Document, facts not available (21) | 19 withheld/clarification (no invention) | 1 (per-student fee) | 1 routing |
| CC5, old curriculum context (3) | 3 ineligible: CC 4/L not completed, CC 3/L unknown | 0 | 0 |
| CC5, proposed curriculum context (3) | 3 clarification (no reviewed CC4) | 0 | 0 |
| Course questions, no context (18) | 12 clarification | 0 | 6 routing |

Correct answers (author check against printed text): grade 1.0 = 98-100 Excellent
(Handbook p.46, en/fil/taglish); exam cheating first offense = automatic 0 or failing
grade 5 at the subject's discretion (en/fil/taglish); vehicle sticker application
P50.00; three-lecture-unit special-class example 20,000.00 (en/fil/taglish).

Wrong: `natural-u2-en` ("ten students ... how much does each student pay?") released
"The amount printed is 20,000.00 PHP." True printed fact, but not the requested
per-student amount, which the source does not state. Router mapped the question to the
nearest reviewed fact and the per-part reviewer accepted it (relevance weakness).

System errors: 8 routing `invalid_model_output`: the router invents a prerequisite
operation on a non-course phrase (e.g. "summer immersion after third year") or an
unreviewed program; the host refuses, the repair repeats it, and the student sees a
misleading "temporarily unavailable". Style: the Taglish cheating question is labelled
English by the router and answered in English (both runs).

Timing (warm, per case): answered document median 45.2 s (run 1: 54.8 s);
CC5 structured median 32.8 s; routing stage median 25.8 s (run 1: 30.1 s);
retrieval 0.31 s; Prolog 0.35 s. Excluded: API, browser, network, queueing, cold start.

## Run 1 (code `eebbdb0`) summary

Same correct answers and no invented facts; 11 system errors (10 routing truncations
from a hidden thought channel, 1 context overflow from citation geometry). Fixed by
`71734f2` and `e945c80` before run 2.

## Next candidates (not started)

1. Router: stop operations whose target is not a catalog course mention; on repeated
   invalid output answer with clarification/unavailable rather than "temporarily
   unavailable". 2. Relevance: a part asking for a per-person/derived amount must not
   map to a printed total. 3. Router style labelling for English-heavy Taglish.

## Follow-up fixes after run 2 (21 October 2026)

- `c8a25f5`: reference errors get a specific repair and, if persistent, a clarification.
  Rerun of the 9 error cases: 8 now clarification_needed; the 9th exposed a style-guard
  conflict (student wrote "isusumite"), fixed in `304a1f0` (mirror the student's word).
  Its blocked answer was correct: Enrolling Officer, fee printed "None", 5 minutes,
  College Enrollment Area.
- `6d639f5`: checker no longer copies identity hashes (12.4 s -> 4.6 s per answer).

## Run 3 (code `b1fa765`; protocol in the roster protocol file)

| Group (n) | Correct behaviour | Wrong | System errors |
| --- | --- | --- | --- |
| Document, facts available (18) | 12 answered correctly; 5 withheld, 1 clarification | 0 | 0 |
| Document, facts not available (21) | 20 withheld/clarification | 1 (per-student fee, as before) | 0 |
| CC5, old curriculum (3) | 3 ineligible (CC 4/L not completed, CC 3/L unknown) | 0 | 0 |
| CC5, proposed curriculum (3) | 3 clarification | 0 | 0 |
| Course questions, no context (18) | 18 clarification | 0 | 0 |

No previously correct answer was lost; new correct answers: vehicle sticker P50.00 in
Filipino and Taglish. **System errors 8 -> 0.** Timing (warm backend): answered
document median **34.7 s** (run 2: 45.2 s; run 1: 54.8 s); CC5 Prolog answers median
**21.6 s** (run 2: 32.8 s); routing stage median 20.9 s (run 2: 25.8 s).

## #2 (per-person amount) attempts

- Run 4 (`dd66c1a`, prompt-only source-limit rule; clean rerun after a container restart):
  no lost answers, 0 system errors, document median 31.9 s, but `natural-u2-en` still
  answered "The amount printed is 20,000.00 PHP." Prompt-only rule failed its target.
- Run 5 (`d8d5220`, not-stated facts offered in the topic menu): **0 wrong answers**
  (all three per-student wordings withheld), 0 system errors, one new correct answer
  (`pre-enrollment-first-step-tl`), but the router also picked "official individual
  student assessment" for the three "what does the fee example show" questions, so
  those correct answers (20,000.00) were lost. The 4B router does not reliably
  distinguish "what the printed example shows" from "one student's own charge".
- Operational finding: the llama.cpp host prompt cache grows across long runs; at
  ~5.2/7.5 GiB container memory the server slowed to 120 s timeouts. Restarting
  the container restored normal speed. A deployment needs a cache-RAM limit or restarts.
- Owner decision (22 October 2026): keep run 5's safe behaviour. An honest 'not enough
  evidence' is preferred over a misleading number; the withheld fee-example answers are a
  disclosed limitation of the 4B router.

## #3 (reply style) - run 6, 22 October 2026

Diagnosis from run 3's rendered headers: `cheating-first-offense-taglish` was labelled
English-only by the style call; `natural-u1/u2` clarifications fell back to English even
for pure Filipino because a failed-routing clarification never ran the style call; about
nine Taglish questions were labelled Filipino (formal header, Taglish-ish claims).
Owner approved (22 October 2026) both fixes in `e53153b`: an English-only label on a
question with an everyday Filipino function word becomes Taglish (offline check: 0/21
English roster questions affected), and an invalid-reference clarification gets one style
call. Fil-versus-Taglish stays the model's choice (Phase 07 prompt variants regressed).

Run 6 (9 cases: cheating and natural-u1/u2 in en/tl/taglish; container restarted first):
cheating-taglish now answers in Taglish with the same correct content; `natural-u1-tl`
clarifies in Filipino; English controls stay English; 0 system errors, 0 wrong answers.
`natural-u1-taglish` and `natural-u2-tl/taglish` now end as insufficient evidence instead of
clarification (safe; per-student amount is not stated). `natural-u1-taglish` is still
labelled Filipino (remaining fil/taglish limitation). Raw: workspace
`audit-evidence/p09-real-data-20261021/roster6/`.

## Run 7 (hosted Supabase retrieval) and run 8, 22 October 2026

Run 7 (`2817c5c`/`b4616ab`, `HOSTED=1`, 63 cases): 17 answered, 26 clarification, 20
insufficient; 0 system errors, 0 invented facts. Versus run 5 the only changes are four
newly answered cases: overload-conditions en/tl/taglish (correct; Handbook table 6 row 3,
"not more than 6 units but not to exceed 28 units") and completion-deadline-conflict-en.
They come from the real SQL returning required neighbours transitively (the stand-in did not).
The deadline answer quoted both printed rules correctly but did not say the handbook
conflicts on which applies (reviewed limit `conflicting_deadlines`): 1 misleading-by-omission
answer under the source-gap policy. Fixed in `f77b952` (host notice for cited unresolved
conflicts/defects). Run 8 (those 6 cases, hosted): the deadline answer now ends with the
conflict notice; overload answers unchanged with no notice; deadline tl/taglish still
withheld/clarify. After the fix: 17 answered, 0 wrong or misleading.
Timing (warm backend): document answers median 31.5 s, Prolog 20.1 s, max 38.6 s. The
retrieval stage (query embedding + hosted Supabase round trip) median 0.87 s, max 2.93 s
(run 5 stand-in: 0.35 s). Excluded: browser, API, queueing, cold start.

## Run 9 (hosted 39-curriculum release, router v15), 23 October 2026

Code `6dad1af` (retrieval version-id fix `b26de19`; an earlier attempt is quarantined, another was
stopped by the host for low memory after 2 cases). 63 cases once each: 19 answered (baseline run 7+8:
17), 22 clarification, 22 insufficient; 0 system errors, 0 wrong or invented answers (author reading).
New correct answers: Architecture AD-2/L en/tl/taglish ineligible (TOA-1/L not passed, BSA ledger)
and special-class fee example en/taglish (printed 20,000.00). Safe changes: CC5 under the proposed
curriculum and Criminology CDI 6/7 (tl) now unknown with the missing completion named; vehicle-sticker
replacement questions end as insufficient evidence instead of clarification.
**Pass condition failed: 3 run 8 correct answers lost.**
- `cs-cc5-failed-cc4-en@bscs-2018-2019` (was ineligible): under v15 the model quoted
  "I am a Computer Science student." as a program mention and omitted the CC5/CC4 course mentions its
  operation and claim refer to; both attempts identical -> `invalid_course_quote_reference` -> clarify.
- `overload-conditions-taglish`: v15 quoted "Graduating undergraduate sa last semester" as a
  curriculum mention; it resolves to nothing -> `unresolved_entity` clarify on a handbook-only question.
- `pre-enrollment-first-step-tl`: duplicated part asking also for an enrollment deadline not in the
  evidence -> insufficient (safe; model output variation).
Both routing losses reproduced deterministically in an uncounted probe. Timing (warm backend):
document answers median 32.2 s, Prolog 28.3 s (context 20.8 s); retrieval median 0.84 s.
Raw: workspace `audit-evidence/p09-real-data-20261021/roster9/`.
