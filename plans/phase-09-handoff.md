---
artifact: phase-handoff
phase: 9
status: complete
plan: plans/phase-09-generation-validation-plan.md
final_commit: b28cd6c93fb98eb4e7fee3b101e85a7cfea09170
next_phase: 10
completed_at: 2026-10-22T14:00:00+08:00
completion_scope: owner-approved offline research/software milestone with real-data development evidence
---

# Phase 09 final handoff

Owner approved closeout on 22 October 2026 ("Approve closeout") after the
[exit reassessment](2026-10-22-phase09-exit-reassessment.md), with its seven
limitations disclosed. This is not institutional release, school approval, student
service or a latency SLA. Previous handoff (19 Oct offline milestone, reopened 20 Oct):
`git show 60a5fe3:plans/phase-09-handoff.md`. No Phase 10 work has started.

Developer entry: [pipeline map](../docs/development/pipelines.md),
[generation module](../backend/bintanong_generation/README.md),
[routing module](../backend/bintanong_routing/README.md).

## Written exit gate

| Exit | Evidence |
| --- | --- |
| Contradictory, fabricated-citation, wrong-version, unsupported drafts rejected | Synthetic regression suite; full suite at `e53153b`: 6097 passed, 6 skipped, 0 failed (945 s) |
| Regeneration terminates | One repair after the draft; per-part path keeps it; fixed fallbacks |
| Canonical symbolic status preserved | Real Janus CC5 `ineligible` kept in en/fil/taglish (roster runs 3-6); fixture Hybrid h-en, b1, b2 |
| Honest multilingual observations | [Per-part](2026-10-21-per-part-observation-results.md), [broader b1-b6](2026-10-21-broader-multilingual-check.md), [real-data roster runs 1-6](2026-10-21-real-data-roster-results.md) |

Reopening holds (21 Oct [exit map](2026-10-21-phase09-remaining-work-and-exit-map.md)):
requested operation/identity, complete requirements and relevance are resolved on the
observed cases; omissions the router never declares remain a disclosed limitation.

## What the reopened phase delivered

- Actual RAG/Symbolic/Hybrid composition ([results](2026-10-20-live-backend-composition-results.md)).
- Per-part generation, default profile `parts` ([decision](2026-10-21-per-part-generation-decision.md)).
- Owner reply-language rules: per-language prompt lines, deep-Tagalog repair, style floor
  (`e53153b`: English-only label with Filipino function words -> Taglish; failed-reference
  clarifications run the style call).
- Real-data development path (owner decision 21 Oct, AGENTS.md): read-only PackageStorage
  (`295a91c`), router topic menu (`f38b409`, not-stated facts `d8d5220`), research release
  builder (`12c5e65`), reference errors clarify (`c8a25f5`), latency cuts (`6d639f5`,
  `60647a4`, `b1fa765`; [budget](2026-10-21-latency-research-and-budget.md)).

## Latest real-data result

Run 5 (`d8d5220`), 63 accepted cases: 13 answered, 26 clarification, 24 insufficient;
0 wrong answers, 0 invented facts, 0 system errors. Document cases with reviewed fields:
10/18 answered, 8 withheld. Run 6 (`e53153b`, 9 cases) fixed the Taglish-to-English reply
and English clarification for a Filipino question. Warm backend component timing: document
median 32.2 s, Prolog 20.4 s, max 39.4 s. Excluded: browser, API, network, queueing,
Supabase, cold start. Author assessment, not independent or institutional gold.

## Versions and digests

Python 3.13.7, Pydantic 2.13.5, HTTPX 0.28.1, pytest 9.1.1, Janus 1.5.2, SWI 10.1.15;
no dependency/lock change. llama.cpp container `bintanong-p09-cuda-latency`, image
`sha256:f66a5229a3e0586339d16155e9fe09c37834d7a7f4134bbdee7360b5a1f2546d`; ctx 8192,
out 768, temp 0, seed 0. Model `C:/Coding-projects/bintanong_workspace/MODELS/GEMMA_4_E4B/
gemma-4-E4B-it-UD-Q4_K_XL.gguf`, SHA256 `3cf61de12daa015ee0f7b68e7b7c541405bf220e1e942bad8b47cab827d7df80`
(inherited; not re-hashed). Router `bintanong-router-p09-v14`. Prompt SHA256: part
`8a5b89c7c992acb1ad3f45d461c88a1a15144169585e7d85e888d8890b950d41`, confirm
`00ae9170ba7f8066730881d64e75b60d5ba80b3ca46430b2a49e7c01acde4009`, style
`ac309f2a9125c8ec44bb91678adf35e400d3946fd2825bbc02df0f2ef56dea07`.
Raw evidence (ignored): workspace `audit-evidence/p09-real-data-20261021/`,
`p09-style-floor-20261022/`, `p09-per-part-20261021/`, `p09-broader*-20261021/`.

## Exit verification (22 Oct)

Full suite at `e53153b` as above (log `audit-evidence/p09-style-floor-20261022/full-suite.log`);
later commits are docs only. Docs hygiene + phase-state tests: 30 passed, 14 subtests.
`phase_state.py validate` and `can-advance` run after this handoff. Context consulted:
thesis physical 17-18 and the routing PNG; no discrepancy.

## Disclosed limitations and risks

1. Undeclared-part omissions are not independently detected.
2. All-or-nothing answers: one unavailable part withholds verified parts.
3. Router over-reads per-person amounts (3 fee-example answers withheld) and adds details.
4. Some Taglish questions are labelled Filipino (model choice).
5. Latency 20-39 s warm component; 15-20 s target unmet/unvalidated; no end-to-end timing.
6. Retrieval uses the PackageStorage stand-in, not hosted Supabase.
7. Inherited: candidate-only output, no activation, university approval pending, F04 and
   if/kung policy held, real data for research development only.
Operational: restart the llama.cpp container before long runs (prompt-cache memory growth).

## Next-phase prerequisites

Phase 10 (master 15: private PDFs/photos and session context) may be planned after
`can-advance` succeeds and the owner says to start. Optional follow-ups, not Phase 10
prerequisites: partial answers naming the missing part, router per-person/added-detail
errors, latency levers (router prompt cache, unused router fields). Web/API is Phase 11.
