# Current progress

Updated 23 October 2026. Phase 09 complete (second closeout); no active phase; Phase 10 not started.
Branch p09 / `feat/p09-generation-validation`, nothing pushed.
[Final handoff](../phase-09-handoff.md) | [Phase 10 pre-phase research](../2026-10-23-phase-10-pre-phase-research.md).
Last full snapshot before this replacement: `e28eb5d:plans/plan_current_progress/current_progress.md`.

## Latest changes (23 Oct, Claude Code session)

- AGENTS.md: owner rule, intensive pre-phase research before each phase from Phase 10 on
  (`c334d4f`), recorded in `plans/YYYY-MM-DD-phase-NN-pre-phase-research.md`; research proposes only.
- Shorter router output (owner pick): wire v4 / prompt v17 drops the unused `reason` field
  (`59e294b`). Dropping `intent` as well (`76e0128`, v16) lost a failed-course claim after a
  container restart in an uncounted precheck, so intent stays. Router output -19..-43 tokens.
- Full suite at `59e294b`: 6201 passed, 6 skipped, 0 failed. Run 14 PASS: 25 answered, 19
  clarification, 19 insufficient; 0 wrong; medians document 26.3 s, Prolog 20.3 s, routing 11.6 s.
  One new Taglish conflict answer is safe but one-sided (disclosed).
- Phase 09 closed on the owner's direction ("do the work autonomously until you reach the end of
  phase 9 finally transitioning to phase 10"); decision in `owner-decisions-ledger.md`.
- Phase 10 pre-phase research written (`d34cc43`): reuse RequestContext facts, ocr_bench and Q8-Q16;
  born-digital PDFs via pypdfium2 need no OCR; Docling 2.142.0 exists (pin 2.133.0); Gemma 4 E4B
  reads images natively (needs an mmproj download); upload/injection/session findings.

## Next action

Wait for the owner's go to start Phase 10. On go: run `phase_state.py can-advance`, answer or defer
research decisions D1-D3 (OCR engine install, Gemma vision bake-off, session lifetime/credential),
create the Phase 10 worktree `p10` and plan, then build steps 1-4 (session store, upload validation,
born-digital PDF grade facts, conversation context) test-first.

## Boundaries

Undergraduate scope, read-only advisory, source-gap, privacy, institutional release and one-week
improvement boundaries unchanged. Accepted 75 variants and the held if/kung policy unchanged. No
activation, push, training, dependency or DB change this session. Context consulted 23 Oct resume:
thesis physical 17-18 (Scope and Limitations) and the routing PNG; no discrepancy.
