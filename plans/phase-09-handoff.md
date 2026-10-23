---
artifact: phase-handoff
phase: 9
status: complete
plan: plans/phase-09-generation-validation-plan.md
final_commit: 25f550f
next_phase: 10
completed_at: 2026-10-23T17:30:00+08:00
completion_scope: owner-directed offline research/software milestone on the hosted 39-curriculum research release
---

# Phase 09 final handoff (second closeout)

Owner direction, 23 October 2026: "do the work autonomously until you reach the end of phase 9 finally
transitioning to phase 10" (recorded in `owner-decisions-ledger.md`). Phase 09 was closed on 22 Oct
(`a31ac32`, history: `git show a31ac32:plans/phase-09-handoff.md`) and reopened the same day for hosted
Supabase. This closes the reopened work. It is not school approval, institutional release, activation,
student service or a latency SLA. No Phase 10 implementation has started.

Developer entry: [pipeline map](../docs/development/pipelines.md),
[generation](../backend/bintanong_generation/README.md), [routing](../backend/bintanong_routing/README.md).

## Written exit gate (master 14, Phase 09 plan)

| Exit | Evidence |
| --- | --- |
| Contradictory, fabricated-citation, wrong-version, unsupported drafts rejected | Synthetic regression suite; full suite at `59e294b`: 6201 passed, 6 skipped, 0 failed (1128 s) |
| Regeneration terminates | One repair after the draft; per-part path keeps it; fixed fallbacks |
| Canonical symbolic status preserved | Real Janus CC5 `ineligible` kept en/fil/taglish (runs 3-14); 39-curriculum Prolog checks per program review |
| Honest multilingual observations | [Roster results](2026-10-21-real-data-roster-results.md) runs 1-14, with residual failures disclosed |

Reopening goal (hosted Supabase) met: 15 migrations on hosted project `jyrudbiuajahsucsorco`, research
release with 5 sources/19 chunks and all 39 reviewed prospectus curricula, runtime reads via
`HostedReleaseStorage` (39/39 equivalence) ([plan](2026-10-22-hosted-supabase-integration-plan.md),
[ledgers load](2026-10-23-hosted-curriculum-ledgers-load.md)).

## What the reopened phase delivered

- Hosted Supabase retrieval and curricula; one research release serves all 39 curricula.
- Program prerequisite reviews for all 39 prospectus curricula (9 colleges), owner rulings in the ledger;
  co-requisite dependency fix (`781c9a2`), partial-rule decision (`e4bd8bd`).
- Router/host fixes: retrieval version ids (`b26de19`), host fixes (`0d69381`), topic-menu not-stated
  facts (`bca2600`), per-person cue guard (`4fad98a`).
- Latency: prompt reuse default (`25212ba`), router wire v4 / prompt v17 without `reason` (`59e294b`;
  the v16 attempt `76e0128` failed its precheck and was replaced).

## Latest real-data result (run 14, `59e294b`)

63 accepted cases: 25 answered, 19 clarification, 19 insufficient; 0 wrong, 0 invented, 0 system errors.
Warm backend medians: document answers 26.3 s (max 35.7), Prolog 20.3 s, Prolog with context 14.8 s,
all cases 20.3 s. Excluded: browser, API, network beyond Supabase calls, queueing, cold start. Author
assessment, not independent or institutional gold.

## Versions and digests

Python 3.13.7, Pydantic 2.13.5, HTTPX 0.28.1, pytest 9.1.1, SWI 10.1.15; no dependency/lock change.
llama.cpp container `bintanong-p09-cuda-latency`, image
`sha256:f66a5229a3e0586339d16155e9fe09c37834d7a7f4134bbdee7360b5a1f2546d`; ctx 8192, out 768, temp 0,
seed 0, `cache_prompt=true` (profile p09-greedy-prefix-cache-v1). Model
`C:/Coding-projects/bintanong_workspace/MODELS/GEMMA_4_E4B/gemma-4-E4B-it-UD-Q4_K_XL.gguf`, SHA256
`3cf61de12daa015ee0f7b68e7b7c541405bf220e1e942bad8b47cab827d7df80` (inherited; not re-hashed).
Router `bintanong-router-p09-v17` SHA256 `6a9c2e7ef5cd140f95e681ef97caa25f03b9585a5419c02d86c85efd3ad9c7fc`,
wire `bintanong-interpretation-wire-v4`. Part `8a5b89c7c992acb1ad3f45d461c88a1a15144169585e7d85e888d8890b950d41`,
confirm `00ae9170ba7f8066730881d64e75b60d5ba80b3ca46430b2a49e7c01acde4009`, style
`ac309f2a9125c8ec44bb91678adf35e400d3946fd2825bbc02df0f2ef56dea07`.
Raw evidence (ignored): workspace `audit-evidence/p09-real-data-20261021/` (roster12-14, latency14b/15b/16b),
`p09-router-short/` (suite logs), `p09-program-reviews/`, `p09-curricula-load-20261023/`.

## Exit verification (23 Oct)

Full suite at `59e294b` as above (`audit-evidence/p09-router-short/full-suite-3.log`); later commits are
docs only. Docs hygiene and phase-state tests rerun after this handoff; `phase_state.py validate` and
`can-advance` run after the index update. Context consulted: thesis physical 17-18 and the routing
PNG; no discrepancy.

## Disclosed limitations and risks

1. Undeclared-part omissions are not independently detected.
2. All-or-nothing answers: one unavailable part withholds verified parts.
3. Router over-reads remain possible; per-person amounts are now withheld by a host guard (safe, but
   the printed class example is not offered); pre-enrollment Taglish "...sa step 1?" still clarifies.
4. Some Taglish questions are labelled Filipino (model choice); style floor stops English-only replies.
5. Conflict answers can be one-sided: completion-deadline-conflict-taglish gives one statement plus
   the conflict notice, while English gives both.
6. Latency 15-36 s warm component; the 15-20 s target is unmet for documents and unvalidated; no
   student end-to-end, browser or cold-start timing. The first request after a model restart gets
   no prompt reuse; restart the container before long runs (prompt-cache memory growth).
7. Router outputs move with prompt wording on this 4B model; any router change needs a counted rerun.
8. Inherited: candidate-only output, no activation, university approval pending, F04 and if/kung
   policy held, real data for research development only, full-prospectus conversion stays draft.

## Next-phase prerequisites

Phase 10 (master 15 plus addendum 23: private PDFs/photos, session store, conversation context) starts
only when the owner says so. Read the [pre-phase research](2026-10-23-phase-10-pre-phase-research.md)
first; owner decisions D1-D3 there (OCR engine install, Gemma vision bake-off, session lifetime and
credential) gate only the photo-OCR step. Web/API wiring is Phase 11.
