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

## Run 10 (router host fixes `0d69381`), 23 October 2026 - PASS

Same 63 cases once each on the hosted 39-curriculum release. 21 answered, 20 clarification, 22
insufficient; 0 system errors, 0 wrong or invented answers (author reading). Versus run 9 only three
cases changed: overload-conditions-taglish answered again (not more than 6 units, not over 28;
Handbook p.62); CC5 en with the old BSCS curriculum ineligible again (CC 4/L not completed, CC 3/L
unknown); CC5 en with the proposed curriculum now reaches Prolog and stays unknown (safe). Every run 9
answer kept. Still not answered: pre-enrollment-first-step-tl (insufficient, safe; disclosed).
Full suite before the run: 6188 passed, 6 skipped. Timing (warm backend): document answers median
34.1 s (max 45.5), Prolog 28.9 s, context 20.5 s; retrieval median 0.87 s. Excluded: browser, API,
queueing, cold start. Raw: workspace `audit-evidence/p09-real-data-20261021/roster10/`.

## Run 11 (topic-menu not-stated fix `bca2600`), 23 October 2026 - FAIL (2 wrong)

63 cases once each: 26 answered, 20 clarification, 17 insufficient; 0 system errors; no run 10 answer
lost. New correct answers: pre-enrollment-first-step en/tl (Enrolling Officer, fee None, 5 minutes,
College Enrollment Area; Charter step 1) and special-class example tl (20,000.00).
**Wrong:** `natural-u2-en` ("The amount printed for the student is 20,000.00 PHP") and
`natural-u2-taglish` ("Ang babayaran per student ay 20,000.00 PHP"): the printed class example is
presented as each student's share, which the source does not state (owner rule 22 Oct: withhold).
Cause: before the fix the menu offered "GCash permission" as answerable; the router copied it and the
policy withheld every special-class per-student question by accident. With GCash correctly offered as
not stated, the router requests only the printed example and the 4B model does not pick "official
individual student assessment". The earlier safe result was a side effect of the same menu bug.
Timing: document answers median 32.4 s, Prolog 27.6 s. Raw: `roster11/`.

## Run 12 (per-person cue guard `4fad98a`), 23 October 2026 - PASS

Full suite first: 6194 passed, 6 skipped. 63 cases once each: 24 answered, 20 clarification, 19
insufficient; 0 system errors, 0 wrong or invented answers. Versus run 11 only the two wrong answers
changed: natural-u2 en/taglish now insufficient evidence (natural-u2-tl already was). Every other run
11 answer kept, including pre-enrollment first step en/tl and the fee example en/tl/taglish (20,000.00).
Timing (warm backend): document answers median 34.3 s (max 43.3), Prolog 28.7 s, context 21.7 s;
retrieval median 0.92 s. Raw: workspace `audit-evidence/p09-real-data-20261021/roster12/`.

## Run 13 (prompt reuse on, profile p09-greedy-prefix-cache-v1, `c3d3790`), 23 October 2026 - PASS

63 cases once each: identical outcome per case to run 12 (24 answered, 20 clarification, 19
insufficient); 0 system errors, 0 wrong. 20 of 24 answers word-for-word identical; 4 reworded with the
same facts and citation (grade-excellent-taglish, cheating-first-offense tl/taglish,
pre-enrollment-first-step-tl; the last now also names the responsible person; cheating-tl drops the
word "discretion" but keeps automatic 0 or failing grade 5 by subject).
Timing, warm backend, run 12 -> run 13 medians: document answers 34.3 -> 27.7 s; Prolog 28.7 -> 23.4 s;
Prolog with curriculum context 21.7 -> 16.1 s; all 63 cases 28.4 -> 21.5 s; routing stage 18.5 -> 13.1 s.
Outlier: one hosted retrieval took 24.9 s (dev-vehicle-initial-application-payment-tl, 50.9 s total),
a Supabase/network spike unrelated to reuse. Excluded: browser, API, queueing, cold start; the first
request after a model restart gets no reuse. Raw: `roster13/`.

## Run 14 (router wire v4 / prompt v17, `59e294b`), 23 October 2026 - PASS

Full suite first: 6201 passed, 6 skipped. Binding head `d34cc43` (docs-only commits after `59e294b`),
prompt reuse on, hosted release. 63 cases once each: 25 answered, 19 clarification, 19 insufficient;
0 system errors, 0 wrong or invented answers. Versus run 13: 23 answers word-for-word identical;
overload-conditions-taglish reworded with the same facts and citation; one new answer,
completion-deadline-conflict-taglish (was clarification): it gives the printed one-year statement plus
the conflict notice ("magkasalungat ang sinasabi ng source ... Pakitanong sa tamang opisina"). Safe,
but weaker than the English answer, which shows both conflicting statements; the Taglish reader sees
only one side (disclosed limitation). No run 13 answer lost.
Timing, warm backend, run 13 -> run 14 medians: document answers 27.7 -> 26.3 s (max 50.9 -> 35.7);
Prolog 23.4 -> 20.3 s; Prolog with curriculum context 16.1 -> 14.8 s; all 63 cases 21.5 -> 20.3 s;
routing stage 13.1 -> 11.6 s. Excluded: browser, API, queueing, cold start. Raw: `roster14/`.
