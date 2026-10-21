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
