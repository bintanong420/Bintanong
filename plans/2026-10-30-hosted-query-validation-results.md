# Hosted query validation — 30 October 2026

Owner request: query common questions and course prerequisites from each program on the hosted release
(`p12-research-faqsplit-20261030`, backend on `hosted-research-api-config.json`, gate composition). Single runs.
Script, cases and replies (ignored): `audit-evidence/p12-hosted-560-activation-20261030/hosted_query_validation.py`,
`query-validation-cases.json`, `query-validation-results.jsonl`, retry `query-validation-retry-results.jsonl`.

Expected prerequisite answers come from the reviewed curriculum ledgers (printed prospectus), one case per
curriculum, rotating forms. These questions were chosen after the benchmark and are not part of it.

## Results

| Family | Cases | Correct | Notes |
| --- | ---: | ---: | --- |
| "Can I take X if I passed Y?" | 10 | 10 | "conditions satisfied" (scorer keyword bug first marked these failed; replies correct) |
| "Can I take X if I failed Y?" | 10 | 10 | documented condition unmet |
| "What are the prerequisites of X?" (9 English, 10 Taglish) | 19 | 19 | every printed code listed (up to six, e.g. BSEd English EL 15) |
| Printed prerequisite cell blank | 5 | 5 | never stated "no prerequisite" |
| Common document questions (7 English, 3 Taglish) | 10 | 6 | see below |

All 39 curricula (38 programs; BSCS old and proposed) answered their prerequisite case correctly: 44/44.
HTTP 200 for all 54; median 22.2 s, max 61.0 s outer request (single observations, backend warm).

Correct document answers: dropping, shifting (Taglish), absences (Taglish), good moral (Taglish), refund, cheating penalty.

## Findings (open)

1. **TOR request** ("How do I request a transcript of records?"): selects Charter 2.3 Request for TOR Copy, but the
   student text showed internal evidence IDs (`[ev-5c33…, ev-2a2a…]`) after multi-line host-rendered steps.
   **Fixed** in `3206ae1` (test-first; re-asked live: no IDs, 9 source cards). The `�` seen in the console was
   a display artifact: the reply holds the printed `’` (U+2019, 9×) and `–` (U+2013, 2×), no U+FFFD.
2. **Honors requirements** ("What are the requirements to graduate with honors?"): first run
   `temporarily_unavailable` (no backend error logged), retry also failed. The benchmark's narrower residence
   question passes.
3. **Academic probation** ("What happens if I am placed on academic probation?"): first run
   `insufficient_evidence`, retry answered: inconsistent between runs.
4. **INC removal** ("How do I remove an incomplete grade?"): "not in Bintanong's reviewed sources" twice,
   although the Charter has a removal service: topic selection miss.

The first run overlapped a full C: drive late in the run (cleared afterwards); the four document cases above
were retried after the earlier ones completed normally, and findings 1, 2 and 4 repeated.
