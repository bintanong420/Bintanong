# Real-data roster run: protocol (fixed before running)

21 October 2026. Owner-authorized research mode (AGENTS.md). Code at the commit
that adds this file. One attempt per case, fixed order, no reruns or tuning.

## Stack

Research release per BSCS ledger (old 2018-2019 default; proposed 2025-2026 only for
cases whose context names it), Phase 05 reviewed package (19 chunks) via read-only
PackageStorage, real SEA-LION-E5 query encoder, real Gemma 4 E4B (CUDA container
18088, ctx 8192, out 768, temp 0, seed 0), real SWI-Prolog via Janus, `parts`
generation profile, separate routing. Encoder loaded once before timing.

## Cases (no new wording)

- 39 accepted document variants (Phase 05 `document-development-cases.json`),
  empty student context. Expected availability from Phase 05 labels
  (`reviewed_fields_available` vs insufficient); answer correctness by author reading.
- 18 accepted structured variants (accepted coverage matrix), empty context.
  Expected: CC5 -> clarification (no curriculum); practicum and the 12 non-BSCS
  program cases -> unavailable/clarification, never an invented decision.
- 6 context variants: the 3 CC5 wordings with curriculum `bscs-2018-2019`
  (expected ineligible: CC 4/L not completed, CC 3/L unknown) and with
  `bscs-proposed-2025-2026` (CC4 is not a reviewed proposed course: expected
  clarification/unknown, never ineligible-by-assumption).

## Recorded per case

Status, validation, decision, claims, citations, research_ref, per-stage event
durations, generation seconds and outer seconds. Excluded: API, browser, network,
Supabase (not used), queueing, cold start. Not an accuracy rate or student SLA.

## Run 1 result (code `eebbdb0`) and run 2 protocol

Run 1: 0 of 21 unavailable-fact document variants answered (no invention);
10 of 18 fact-available document variants answered, all 10 correct against the
printed source; CC5 with old curriculum 3/3 ineligible (CC 4/L not completed,
CC 3/L unknown); CC5 with proposed curriculum 3/3 clarification. Failures: 10
routing `truncated_output` (hidden thought channel used the 768-token budget),
1 generation `context_overflow` (citation geometry was ~80% of the input). One
Taglish question was answered in English. Median routing 30.1 s.
Fixes: `e945c80` compact model source cards; the thought-opener ban (this commit's
parent); `88ad891` printed course codes. Run 2 repeats the same 63 cases once each
with identical settings in `audit-evidence/p09-real-data-20261021/roster2/`.

## Run 3 protocol (after `c8a25f5`..this commit)

Changes since run 2: reference-error repair/clarify, mirrored deep word, checker hash
removal, line-break ban, compact topic schema display. Same 63 cases, settings and
order, once each, in `audit-evidence/p09-real-data-20261021/roster3full/`. Purpose:
confirm no quality regression and measure latency. Pass condition: no invented facts,
no previously correct answer lost, routing errors not increased.

## Run 4 protocol (#2 source-limit rule)

Code: the source-limits commit (parent of this protocol commit). Same 63 cases once each,
folder `roster4/`. Pass: `natural-u2-*` not answered with the printed total (withheld,
unavailable or clarification); `dev-special-class-printed-example-*` still answered with
20,000.00; no other previously correct answer lost; no invented facts; no new system errors.

## Run 4 result and run 5 protocol

Run 4 (clean rerun after a container restart; the first attempt is quarantined because the
server's host prompt cache grew to ~5.2/7.5 GiB and caused 120 s timeouts): no lost answers,
0 system errors, document median 31.9 s, but `natural-u2-en` still answered with the
printed total, so the prompt-only rule failed its target. Run 5 adds not-stated facts to
the topic menu (commit above). Same 63 cases, folder `roster5/`, same pass conditions as run 4.

## Run 7 (hosted Supabase retrieval), fixed 22 October 2026 before running

Code `b4616ab`. Same 63 accepted cases, one attempt each, same order and runner, with
`HOSTED=1`: document retrieval reads the active hosted research release
`p09-research-selected-20261022` through `HostedReleaseStorage` (anon key); Prolog and the
model are unchanged. Model container restarted first. Compare against run 5 (`d8d5220`,
PackageStorage): status per case, wrong answers, invented facts, system errors and timing.
The `retrieval` stage now includes the network round trip to Supabase and is reported
separately. Not a new accuracy rate; no wording or threshold changes.

## Run 9 (hosted 39-curriculum release, router v15), fixed 23 October 2026 before running

Code: the parent of the commit adding this section (program-name recognition, router v15).
Same 63 accepted cases, one attempt each, same order, with `HOSTED=1`, runner workspace
`audit-evidence/p09-real-data-20261021/roster9.py`, folder `roster9/`. Change from run 8: the
release is the single multi-curriculum research release built from all 39 curricula read
back from hosted Supabase (`load_release_curricula`) with the owner-approved program and
curriculum names; the two CC5 context variants name their curriculum in the request as before.
Model container restarted first; model settings unchanged.
Expectations: the 12 non-BSCS program variants may now reach Prolog (the program is named in
the question); any decision must match the reviewed ledger and printed page (author reading),
otherwise unavailable/clarification. "Computer Science" without an edition still clarifies (two
BSCS editions); practicum stays unavailable/clarification. Pass: no invented facts, no run-8
correct answer lost, system errors not increased. Not an accuracy rate or student SLA.
First run 9 attempt (`b3d8a15`) quarantined as `roster9-invalid-doc-path/` after 2 cases: every
document question failed `invalid_output` because all 39 prospectus versions were passed as
retrieval version ids (limit 32). Fixed in the commit before this note (retrieval gets document
versions only); an uncounted 2-case precheck answered. Run 9 restarts from case 1 at this commit.

## Run 10 (router host fixes), fixed 23 October 2026 before running

Code `0d69381` (owner "Host fixes" after run 9). Same 63 cases, runner `roster9.py roster10`,
`HOSTED=1`, model container restarted first, everything else as run 9. Pass: no invented facts,
no run 9 correct answer lost, the run 8 answers lost in run 9 (CC5 en old curriculum,
overload taglish) not lost again, system errors not increased. Not an accuracy rate or SLA.

## Run 11 (topic-menu not-stated fix), fixed 23 October 2026 before running

Code `bca2600`. Same 63 cases, runner `roster9.py roster11`, `HOSTED=1`, model container restarted
first, everything else as run 10. Pass: no invented facts, no run 10 correct answer lost, system
errors not increased; pre-enrollment-first-step en/tl expected answered (printed first-step fields);
missing-ending variants still withheld. Not an accuracy rate or SLA.

## Run 12 (per-person cue guard), fixed 23 October 2026 before running

Code: the commit adding the per-person cue guard (parent of this protocol commit). Same 63 cases,
runner `roster9.py roster12`, `HOSTED=1`, container restarted first, everything else as run 11.
Pass: 0 wrong or invented answers (natural-u2-* withheld or clarified), no run 11 correct answer
lost (pre-enrollment first step en/tl, fee example en/tl/taglish), system errors not increased.

## Run 13 (prompt reuse on), fixed 23 October 2026 before running

Code: the prompt-reuse profile commit (parent of this protocol commit). Same 63 cases, runner
workspace `roster13.py roster13` (= roster9 plus `PREFIX_CACHE=1` -> `prefix_cache=True`,
profile `p09-greedy-prefix-cache-v1`), `HOSTED=1`, container restarted first. Compare with run 12
(no reuse). Pass: same answered/withheld outcome per case or only explained safe changes, 0 wrong or
invented answers, system errors not increased. Timing reported against run 12 (warm backend only).
