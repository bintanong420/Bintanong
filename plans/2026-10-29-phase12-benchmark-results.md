# Phase 12 benchmark — results, 29 October 2026

50 English/Taglish questions in the owner's four categories ([decision](owner-decisions-ledger.md), 29 Oct).
40 reuse owner-accepted gate cases that were **used during development** (results on them are optimistic);
10 new disciplinary cases from printed Handbook penalty rows. Evidence: ignored `audit-evidence/p12-benchmark-20261029`.
Condition C ran at `3448353` on the 560 FAQ-split package (local documents, hosted curricula, gate composition);
condition A is the same Gemma artifact and decoding with a one-line assistant prompt, no evidence or rules.
One attempt per case, author-written expectations (printed facts must appear; status/decision where set).

| Category | C full system | A strict | A content only |
| --- | ---: | ---: | ---: |
| Enrollment procedures | 11/14 | 1/14 | 1/14 |
| Prerequisite eligibility | 13/14 | 0/14 | 5/14 |
| Grade policies and academic standing | 9/12 | 2/12 | 2/12 |
| Disciplinary policies (new) | 2/10 | 0/10 | 0/10 |
| **All** | **35/50** | **3/50** | **8/50** |
| English / Taglish | 17/24 / 18/26 | 2/24 / 1/26 | 5/24 / 3/26 |
| Reused (development) / new | 33/40 / 2/10 | 3/40 / 0/10 | 8/40 / 0/10 |

A "strict" also requires the expected status/decision, which plain Gemma cannot produce (no clarify/abstain or rule
check); "content only" checks the printed facts alone. Warm inner seconds: C median 25.1, max 39.8; A median 6.9.
These exclude encoder startup, API/browser, network and queueing; they are not student-visible latency.

## C failures (15)

- Known from the gate (8): summer load en/Taglish, leave length Taglish, cc5-failed-cc4 en, second-year Taglish,
  graduation residence en/Taglish.
- New disciplinary (8 of 10 failed; only cheating passed): `academic_misconduct` holds all 38 printed penalty rows
  (uniform, smoking, bullying, ...) but its selector menu entry is the bare label "academic misconduct" (no printed
  opening: it is a legacy subject id). The selector picks `handbook_attendance_uniform` or `handbook_conduct`, which
  hold no penalties -> unavailable. Plagiarism selects the right topic but the router asks a not-stated claim
  ("missing item 22") -> clarification.

## Disciplinary fixes and final run (`7f8c02b`)

Owner chose "Fix now". Both changes test-first:
- `38ccb83`: the selector menu lists review-bound printed row names (penalty-table `Cause` fields, cut verbatim at a
  word; 34 of 37; defects withhold). RED 3 -> GREEN 12; related 869. Real selector prompt 5625 -> 6088 tokens
  (+768 output = 6856 of 8192). Run 2: 38/50, disciplinary 5/10, no regressions.
- `7f8c02b`: a printed penalty row is always quoted exactly (it was quoted only beside a recorded limitation; Gemma's
  paraphrase dropped the penalties). Blank printed offenses show as "unspecified". RED 1 -> GREEN 13; related 1051.

| Category | C first (`3448353`) | C final (`7f8c02b`) | A strict | A content |
| --- | ---: | ---: | ---: | ---: |
| Enrollment procedures | 11/14 | 11/14 | 1/14 | 1/14 |
| Prerequisite eligibility | 13/14 | 13/14 | 0/14 | 5/14 |
| Grade policies and academic standing | 9/12 | 9/12 | 2/12 | 2/12 |
| Disciplinary policies (new) | 2/10 | 7/10 | 0/10 | 0/10 |
| **All** | 35/50 | **40/50** | 3/50 | 8/50 |
| English / Taglish | 17/24 / 18/26 | 20/24 / 20/26 | | |

Final run: 41 answered, 6 clarifications, 3 insufficient evidence; warm inner median 26.4 s, max 44.1 s. No case that
passed in an earlier run failed in the final run. Still failing (10): the 7 known gate cases plus improper uniform
(Taglish; router claim), plagiarism en/Taglish (router picks the not-stated "missing item 22" claim although the
printed II.7b claim is listed; a host fix would need question keyword matching, which evidence selection avoids).

## Limitations

Single run, author-scored, no independent rater; 40/50 cases were development cases; the disciplinary set is small.
Condition B (RAG without rules) was not run (owner). No claim of institutional accuracy.
