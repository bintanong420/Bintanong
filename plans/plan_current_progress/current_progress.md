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

## Not yet known

Mock tests prove structure, not model quality. Whether Gemma fills the fee slot
correctly needs one actual-model run on the four saved developer cases. Latency
should be similar (same call count) but is unmeasured.

## Next action

Plan and run one bounded actual-model observation of the `parts` profile on the
four saved developer cases (English, Filipino, Taglish, Hybrid relevance), using
the resident service and existing fixtures; record results honestly whatever
they show. Follow-up candidate (not started): answer verified parts while naming
an unavailable part, instead of withholding the whole answer.

## Boundaries

Undergraduate scope, read-only advisory, source-gap, privacy, institutional
release and one-week improvement boundaries unchanged. Accepted 75 variants and
the held if/kung policy are unchanged. No activation, push, training, dependency
or DB change. Phase 09 active; Phase 10 not started. Context consulted this
resume: thesis physical 17-18 (Scope and Limitations) and the routing PNG; no
discrepancy.
