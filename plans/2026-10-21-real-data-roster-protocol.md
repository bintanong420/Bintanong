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
