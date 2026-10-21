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
