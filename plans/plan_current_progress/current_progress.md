# Current progress

Updated 21 October 2026. Phase 09 active on p09 / `feat/p09-generation-validation`.
[Checkpoint](../phase-09-checkpoint.md) | [Per-part decision](../2026-10-21-per-part-generation-decision.md).
Last full snapshot before this replacement: `0a08d8d:plans/plan_current_progress/current_progress.md`.

## Latest change: per-part generation (owner-approved this session)

Agent handover: Claude Code took over from Codex on 21 October 2026.

Root cause of the English missing-fee failure: the selected `scoped` generator
had no per-part obligation (claims carried no part link; the prompt never said
"answer every part"), so all completeness checking fell on a post-hoc reviewer
that wrongly mapped the fee part to an office claim. The owner chose to fix the
generator instead of running the proposed native-thinking checker trial, which
is superseded and will not run.

Delivered (offline candidate, inactive):
- New default profile `parts` (`backend/bintanong_generation/part_answers.py`):
  one required answer slot per declared document part; `answered` with claims
  or `not_in_evidence` / `source_gap` with none. Host numbers claims and derives
  the mapping. An unavailable slot withholds the answer with no review call.
- Reviewer confirms each part against only its own claims plus per-claim support.
- Same two model calls as before; no budget/model/dependency/threshold change.
- Runtime settings, run record, CLI and evaluation hashes accept `parts`; older
  profiles remain explicit. READMEs and the pipeline doc were updated.
- TDD: 12 new tests (`tests/test_generation_part_slots.py`) RED then GREEN.
  Nine old tests that silently relied on the `scoped` default were pinned or
  updated. Focused generation/runtime/docs set: 406 passed.

## Actual-model result ([report](../2026-10-21-per-part-observation-results.md))

d-en now answers both parts (Office K, 7 tokens): the targeted failure is fixed.
d-fil and h-en pass. d-tl content is complete but its claims came out in plain
English, and the reviewer did not flag it: 3/4 full quality, strict gate FAIL.
Warm component 45.3-48.7 s per case (scoped was 43.7-49.8 s); four calls each.
A runner defect in a first attempt (zero generation calls) is disclosed there.

## Style guard (owner chose option a; `cd8e49b`)

Owner direction: natural Taglish = Filipino grammar words plus everyday English
terms (submit, fee, office); never deep Tagalog such as "isusumite". Added a
deterministic floor (English-only fil/taglish claim -> existing single repair)
and that prompt guidance. Second observation: d-en, h-en pass; d-fil complete but
casual Taglish for a formal-Filipino question; d-tl withheld because the repair
got only an opaque error code and repeated the English draft. Safe, still FAIL.

## Per-language style (`b0905cb`)

Owner plan: English -> English; Filipino -> mostly everyday Filipino; Taglish ->
Tagalog structure with English terms. Added per-language prompt lines, a
no-copying rule and a plain rewrite instruction on the style repair. Third
observation: 4/4 full quality on the first draft (author reading), 41-43 s.

## Next action

Owner confirmed the Filipino/Taglish wording reads naturally (21 Oct) and
approved plainer host-rendered Filipino lines (`39c46cb`, `d75f4d1`). Six-case
broader check: relevance works; fixes `838f6d4`; post-fix b1/b3/b4 pass. Owner
authorized real public sources/reviewed Prolog for development (AGENTS.md).
Real-data task 1 done: read-only PackageStorage (`295a91c`) reproduces Phase 05's
offered chunks 39/39; 3 overload results differ because Phase 05's double used
transitive neighbors the real SQL lacks. Next: router topic/fact selection. Against the exit map: interpretation
and completeness are now evidenced on the four fixtures; still open are the
relevance check on the per-part reviewer (old B cases never ran), omissions the
router never declares, broader multilingual cases (new wordings need owner
approval) and real-service timing, then formal closeout.
Separate follow-up: answer verified parts while naming an unavailable part.

## Boundaries

Undergraduate scope, read-only advisory, source-gap, privacy, institutional
release and one-week improvement boundaries unchanged. Accepted 75 variants and
the held if/kung policy are unchanged. No activation, push, training, dependency
or DB change. Phase 09 active; Phase 10 not started. Context consulted this
resume: thesis physical 17-18 (Scope and Limitations) and the routing PNG; no
discrepancy.
